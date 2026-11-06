#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

"""

import hashlib
import json
import multiprocessing as mp
import os
import shutil
import tempfile
import time
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from apero_ri.base.base import BLOCK_KIND
from apero_ri.core import secret_store
from apero_ri.tasks import apero_async
from astropy.io import fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.tasks.apero_object_query"

# list of parameters needed for this task (for checking in run_job)
PARAM_LIST = []
PARAM_LIST.append("LOCAL_DATA_DIR")
PARAM_LIST.append("INSTRUMENT")
PARAM_LIST.append("APERO_PROFILES")
PARAM_LIST.append("APERO_PROFILE_NAMES")
# Profile params are hydrated dynamically from APERO profiles + instrument
# preset.
APERO_PROFILE_PARAM_LIST = []
# Set the default frequency for this task (in hours)
DEFAULT_FREQUENCY = 6.0
# Set whether this task is enabled by default in the admin portal
DEFAULT_ENABLED = True
# Set the type of task (INSTRUMENT, GLOBAL)
TASK_TYPE = "INSTRUMENT"
# Whether this task has a sub-process (for sub-processing loading bar in UI)
USE_SUBPROCESS = True
# Whether this task can be run in multi-process mode
# (if False, will always run in main process)
MULTI_PROCESS = True
# Whether this task supports local pre-built output sync/copy workflows.
LOCAL_TASK = True
# Available filters for quick test runs.
# - APERO_PROFILE_INCLUDE: run only listed APERO profiles
# - APERO_PROFILE_EXCLUDE: skip listed APERO profiles
# - OBJNAME_INCLUDE: run only listed names
# - OBJNAME_EXCLUDE: remove listed names from the run set
FILTERS = [
    "APERO_PROFILE_INCLUDE",
    "APERO_PROFILE_EXCLUDE",
    "OBJNAME_INCLUDE",
    "OBJNAME_EXCLUDE",
]


# =============================================================================
# Define classes
# =============================================================================
class AperoObjectQueryTask(apero_async.AperoAsyncTask):
    """Class representing an asynchronous task in APERO RI."""

    def __init__(self, status: str = "pending") -> None:
        """Initialize the task with its starting status."""
        name = "APERO Object Query Task"
        description = (
            "Generate the object query for the "
            "APERO reduction interface for each apero profile."
        )
        super().__init__(name, description, status)

    # -----------------------------------------------------------------
    # Main entry point
    # -----------------------------------------------------------------
    def run_job(self, params: Dict[str, Any]) -> None:
        """Run per-object DB+header queries for every configured profile.

        Required keys in *params*:

        - ``APERO_PROFILE_NAMES``: list of profile name strings
        - ``APERO_PROFILES``: dict mapping each name → profile config
        - ``LOCAL_DATA_DIR`` (str): output root directory
        - ``INSTRUMENT`` (str)

        Optional keys:

        - ``TASK_CONFIG``: dict with ``force_run``, ``ncores``,
          ``mp_backend``, ``mp_start_method``
        - ``TASK_LOGGER``: callable for progress messages
        - ``STOP_EVENT``: threading/multiprocessing Event for
          cooperative cancellation
        """
        self.info = ""
        ctx = self._init_run_context(params)
        profile_note = str(ctx.get("profile_filter_note", "") or "").strip()
        if profile_note:
            self.info += profile_note + "\n"
            ctx["tlog"](profile_note)

        if not ctx["profile_names"]:
            self.info = "No APERO profiles configured."
            ctx["tlog"]("No APERO profiles configured. Nothing to do.")
            return

        profile_errors = []
        for a_it, profile_name in enumerate(ctx["profile_names"]):
            if ctx.get("stop_event") is not None and ctx["stop_event"].is_set():
                ctx["tlog"](
                    "Cancellation requested. Exiting before next profile.")
                break
            self.progress = (a_it + 1) / len(ctx["profile_names"])
            self.subprogress = 0.0
            try:
                self._run_profile(ctx, a_it, profile_name)
            except Exception as exc:
                err_msg = (
                    f"Profile {profile_name}: failed — {exc}"
                )
                ctx["tlog"](f"ERROR: {err_msg}")
                try:
                    _save_profile_query_state(
                        ctx["profiles"][profile_name],
                        profile_name,
                        status="failed",
                        error=str(exc),
                    )
                except OSError as state_exc:
                    ctx["tlog"](
                        f"Profile {profile_name}: unable to record refresh "
                        f"failure status: {state_exc}"
                    )
                self.info += (
                    f"\n## Object Query for APERO Profile: {profile_name}\n\n"
                    f"- **ERROR**: {err_msg}\n"
                )
                profile_errors.append(err_msg)

        if profile_errors:
            ctx["tlog"](
                "APERO_OBJECT_QUERY completed with errors in "
                f"{len(profile_errors)} profile(s): "
                + "; ".join(profile_errors)
            )
        else:
            ctx["tlog"]("APERO_OBJECT_QUERY completed.")

    # -----------------------------------------------------------------
    # Per-profile processing
    # -----------------------------------------------------------------
    def _run_profile(
        self, ctx: Dict[str, Any], a_it: int, profile_name: str,
    ) -> None:
        """Process one APERO profile: skip check, query objects, run jobs."""
        tlog = ctx["tlog"]
        stop_event = ctx["stop_event"]
        aparams = ctx["profiles"][profile_name]
        instrument = str(
            ctx["params"].get("INSTRUMENT")
            or aparams.get("general", {}).get("INSTRUMENT")
            or "unknown"
        )

        tlog(f'Profile {a_it + 1}/{len(ctx["profile_names"])}: {profile_name}')
        _save_profile_query_state(
            aparams, profile_name, status="running"
        )

        # Guard: check that all configured paths are accessible.
        # If an sshfs/remote drive is down, path.is_dir() returns
        # False. We skip the profile entirely to avoid overwriting
        # previously-good output files with null data.
        missing_paths = apero_async.check_profile_paths_accessible(aparams)
        if missing_paths:
            detail = "; ".join(
                f"{k}={p}" for k, p in missing_paths
            )
            msg = (
                f"Profile {profile_name}: skipping - one or more "
                "required data paths are not accessible (sshfs / "
                f"remote drive down?): {detail}"
            )
            tlog(msg)
            self.info += (
                f"\n## Object Query for APERO Profile: {profile_name}\n\n"
                f"- **Skipped** (path check failed): {msg}\n"
            )
            raise RuntimeError(msg)

        # query distinct object names
        object_names, obj_query_time = self._query_object_names(
            aparams, profile_name, tlog, ctx.get("filters", {})
        )

        # Ensure output directory exists. Workers publish staged tables only
        # after all database and header reads for an object succeed.
        local_objdir = _resolve_objects_dir(aparams, profile_name)
        local_objdir.mkdir(parents=True, exist_ok=True)

        # run the object loop (parallel or serial)
        timing_per_obj, output_files, header_rows_total = self._run_object_loop(
            ctx, aparams, profile_name, object_names
        )
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError(
                f"Profile {profile_name}: refresh cancelled before "
                "all objects were processed"
            )

        # report and persist
        self._report_profile_results(
            profile_name,
            obj_query_time,
            timing_per_obj,
            header_rows_total,
            tlog,
        )
        self.output_files += output_files
        self._invalidate_profile_plot_cache(
            aparams, instrument, profile_name, tlog
        )
        object_filters = ctx.get("filters", {})
        is_partial = any(
            str(object_filters.get(key, "")).strip()
            for key in ("OBJNAME_INCLUDE", "OBJNAME_EXCLUDE")
        )
        _save_profile_query_state(
            aparams,
            profile_name,
            status="partial" if is_partial else "success",
        )
        self.last_run = datetime.now(timezone.utc).isoformat()

    # -----------------------------------------------------------------
    # Helpers: init, skip check, object loop, reporting, persistence
    # -----------------------------------------------------------------
    @staticmethod
    def _init_run_context(
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract commonly used values from *params* into a context dict."""
        task_config = params.get("TASK_CONFIG", {})
        filters = _normalize_filters(task_config.get("filters", {}))
        all_profiles = list(params.get("APERO_PROFILE_NAMES", []))
        profile_names = apero_async.filter_profile_names(all_profiles, filters)
        profile_filter_note = apero_async.profile_filter_note(
            all_profiles, profile_names, filters
        )
        mp_cfg = _normalize_mp_config(task_config)
        task_logger = params.get("TASK_LOGGER")

        def tlog(message: str) -> None:
            """Send a progress message when a task logger is available."""
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        tlog("APERO_OBJECT_QUERY start.")
        return {
            "params": params,
            "profile_names": profile_names,
            "profiles": params.get("APERO_PROFILES", {}),
            "force_run": bool(task_config.get("force_run", False)),
            "filters": filters,
            "profile_filter_note": profile_filter_note,
            "mp_cfg": mp_cfg,
            "tlog": tlog,
            "stop_event": params.get("STOP_EVENT"),
        }

    def _query_object_names(
        self,
        aparams: Dict[str, Any],
        profile_name: str,
        tlog: Any,
        task_filters: Optional[Dict[str, str]] = None,
    ) -> tuple[list[str], float]:
        """Query distinct object names from the file index table."""
        obj_query = _construct_obj_query(aparams)
        db_params = apero_async.get_db_params(aparams)
        tlog(f"Profile {profile_name}: querying distinct object names...")
        start = time.time()
        objlist = apero_async.database_query(db_params, obj_query)
        elapsed = time.time() - start

        self.info += (
            f"Found {len(objlist)} unique objects in the database "
            f"for APERO profile: {profile_name}\n"
            f"Object query time: {elapsed:.2f} seconds\n"
        )
        tlog(
            f"Profile {profile_name}: found {len(objlist)} objects "
            f"in {elapsed:.2f}s."
        )

        names = []
        tfilt = task_filters if isinstance(task_filters, dict) else {}
        # INCLUDE keeps only listed names; empty include means "all names".
        include_objnames = _parse_objname_list(tfilt.get("OBJNAME_INCLUDE", ""))
        # EXCLUDE removes names after include-filtering.
        excluded_objnames = _parse_objname_list(
            tfilt.get("OBJNAME_EXCLUDE", "")
        )
        for entry in objlist:
            if isinstance(entry, dict):
                raw_name = entry.get("KW_OBJNAME", "")
            else:
                raw_name = entry or ""
            name = str(raw_name)
            lname = name.lower()
            if not name:
                continue
            if include_objnames and lname not in include_objnames:
                continue
            if lname in excluded_objnames:
                continue
            names.append(name)
        return names, elapsed

    def _run_object_loop(
        self,
        ctx: Dict[str, Any],
        aparams: Dict[str, Any],
        profile_name: str,
        object_names: list[str],
    ) -> tuple[list[float], list[str], int]:
        """Execute per-object jobs, returning timing, files, header count."""
        tlog = ctx["tlog"]
        stop_event = ctx["stop_event"]
        mp_cfg = ctx["mp_cfg"]
        force_run = bool(ctx.get("force_run", False))
        total = len(object_names)
        timing = []
        output_files = []
        header_rows_total = 0

        if not object_names:
            tlog(f"Profile {profile_name}: no valid object names to process.")
            return timing, output_files, header_rows_total

        use_parallel = MULTI_PROCESS and mp_cfg["ncores"] > 1 and total > 1
        if use_parallel:
            timing, output_files, header_rows_total = self._run_parallel(
                aparams,
                profile_name,
                object_names,
                mp_cfg,
                tlog,
                stop_event,
                total,
                force_run,
            )
        else:
            timing, output_files, header_rows_total = self._run_serial(
                aparams,
                profile_name,
                object_names,
                tlog,
                stop_event,
                total,
                force_run,
            )
        return timing, output_files, header_rows_total

    def _run_parallel(
        self,
        aparams: Dict[str, Any],
        profile_name: str,
        object_names: list[str],
        mp_cfg: Dict[str, Any],
        tlog: Any,
        stop_event: Any,
        total: int,
        force_run: bool,
    ) -> tuple[list[float], list[str], int]:
        """Run object jobs in parallel using a configured executor."""
        tlog(
            f"Profile {profile_name}: parallel object loop "
            f'backend={mp_cfg["backend"]}, workers={mp_cfg["ncores"]}.'
        )
        timing = []
        output_files = []
        header_rows_total = 0
        done = 0
        worker_pids = set()
        batch_size = max(1, int(mp_cfg["ncores"]))
        executor, pool_mode = _make_executor(
            mp_cfg["backend"],
            mp_cfg["ncores"],
            mp_cfg["start_method"],
            tlog,
        )
        tlog(
            f"Profile {profile_name}: mode={pool_mode} "
            f'workers={mp_cfg["ncores"]}.'
        )
        with executor as pool:
            num_batches = (total + batch_size - 1) // batch_size
            for batch_idx in range(num_batches):
                batch_start = batch_idx * batch_size
                batch_end = min(total, batch_start + batch_size)
                batch_objects = object_names[batch_start:batch_end]
                tlog(
                    f"Profile {profile_name}: submitting batch "
                    f"{batch_idx + 1}/{num_batches} "
                    f"({batch_start + 1}-{batch_end}/{total})."
                )

                for global_idx, name in enumerate(
                    batch_objects, start=batch_start + 1
                ):
                    tlog(
                        f"Profile {profile_name}: {name} START "
                        f"({global_idx}/{total}, "
                        f"batch={batch_idx + 1}/{num_batches})."
                    )

                futures = {
                    pool.submit(
                        _run_single_object_job,
                        aparams,
                        name,
                        profile_name,
                        force_run,
                    ): (name, global_idx)
                    for global_idx, name in enumerate(
                        batch_objects, start=batch_start + 1
                    )
                }

                for fut in as_completed(futures):
                    if stop_event is not None and stop_event.is_set():
                        for _f in futures:
                            _f.cancel()
                        tlog(f"Profile {profile_name}: cancelled.")
                        return timing, output_files, header_rows_total

                    objname, global_idx = futures[fut]
                    try:
                        result = fut.result()
                    except Exception as exc:
                        tlog(
                            f"Profile {profile_name}: {objname} failed: "
                            f"{exc}"
                        )
                        raise RuntimeError(
                            f"Object {objname} refresh failed"
                        ) from exc
                    done += 1
                    self.subprogress = done / max(1, total)
                    timing.append(result["object_total"])
                    header_rows_total += int(result["header_rows"])
                    output_files.extend(result.get("output_files", []))
                    worker_pid = int(result.get("worker_pid", 0) or 0)
                    if worker_pid > 0:
                        worker_pids.add(worker_pid)
                    is_skipped = bool(result.get("skipped", False))
                    skip_tag = " SKIPPED" if is_skipped else ""
                    tlog(
                        f"Profile {profile_name}: {objname}{skip_tag} DONE "
                        f"({global_idx}/{total}, "
                        f'{result["object_total"]:.2f}s, '
                        f"batch={batch_idx + 1}/{num_batches}, "
                        f'worker_pid={worker_pid or "n/a"}, '
                        f"unique_workers={len(worker_pids)}/"
                        f'{mp_cfg["ncores"]}).'
                    )
        if worker_pids:
            pids = ", ".join(str(pid) for pid in sorted(worker_pids))
            tlog(
                f"Profile {profile_name}: parallel verification summary: "
                f"unique worker processes used={len(worker_pids)}/"
                f'{mp_cfg["ncores"]}; '
                f"pids=[{pids}]."
            )
        return timing, output_files, header_rows_total

    def _run_serial(
        self,
        aparams: Dict[str, Any],
        profile_name: str,
        object_names: list[str],
        tlog: Any,
        stop_event: Any,
        total: int,
        force_run: bool,
    ) -> tuple[list[float], list[str], int]:
        """Run object jobs serially."""
        tlog(f"Profile {profile_name}: serial mode.")
        timing = []
        output_files = []
        header_rows_total = 0
        for o_it, objname in enumerate(object_names):
            if stop_event is not None and stop_event.is_set():
                tlog(f"Profile {profile_name}: cancelled.")
                return timing, output_files, header_rows_total
            self.subprogress = (o_it + 1) / max(1, total)
            tlog(
                f"Profile {profile_name}: {objname} START "
                f"({o_it + 1}/{total})."
            )
            try:
                result = _run_single_object_job(
                    aparams, objname, profile_name, force_run
                )
            except Exception as exc:
                tlog(
                    f"Profile {profile_name}: {objname} failed: {exc}"
                )
                raise RuntimeError(
                    f"Object {objname} refresh failed"
                ) from exc
            timing.append(result["object_total"])
            header_rows_total += int(result["header_rows"])
            output_files.extend(result.get("output_files", []))
            skip_tag = " SKIPPED" if result.get("skipped", False) else ""
            tlog(
                f"Profile {profile_name}: {objname}{skip_tag} DONE "
                f'({o_it + 1}/{total}, {result["object_total"]:.2f}s).'
            )
        return timing, output_files, header_rows_total

    def _report_profile_results(
        self,
        profile_name: str,
        obj_query_time: float,
        timing_per_obj: list[float],
        header_rows_total: int,
        tlog: Any,
    ) -> None:
        """Append summary markdown and log final profile stats."""
        ave = (
            sum(timing_per_obj) / len(timing_per_obj) if timing_per_obj else 0.0
        )
        total_time = sum(timing_per_obj)
        self.info += (
            f"\n## Object Query for APERO Profile: {profile_name}\n\n"
            f"- Queried {len(timing_per_obj)} objects\n"
            f"- Average query time per object: {ave:.2f} seconds\n"
            f"- Total query time: {total_time:.2f} seconds\n"
            f"- Read {header_rows_total} headers\n"
        )
        tlog(
            f"Profile {profile_name}: done. objects={len(timing_per_obj)}, "
            f"avg={ave:.2f}s, total={total_time:.2f}s."
        )

    def _invalidate_profile_plot_cache(
        self,
        aparams: Dict[str, Any],
        instrument: str,
        profile_name: str,
        tlog: Any,
    ) -> None:
        """Invalidate stale plot cache after object data has been refreshed."""
        try:
            from apero_ri.core.plot_cache import (
                invalidate_profile,
                load_cache_config,
                resolve_cache_root,
            )

            local_data = aparams.get("LOCAL_DATA_DIR",
                                     str(secret_store.get_ari_dir()))
            cache_cfg = load_cache_config(Path(local_data))
            if cache_cfg.get("enabled"):
                cache_root = resolve_cache_root(Path(local_data), cache_cfg)
                removed = invalidate_profile(
                    cache_root, instrument, profile_name
                )
                if removed:
                    self.info += (
                        f"\n- Invalidated {removed} cached plot "
                        f"files for {profile_name}\n"
                    )
                    tlog(
                        f"Profile {profile_name}: invalidated "
                        f"{removed} cached plot(s)."
                    )
        except Exception:
            pass

    def test_query(self, params: Dict[str, Any], objnames: str) -> None:
        """
        Create a file that can be used to populate the object table in the
        APERO reduction interface.

        parameters needed in params for this task:
        - LOCAL_DATA_DIR: str, the local directory where data files are stored
        - APERO_PROFILES: dict of dicts, where each key is an APERO profile
                          name and each value is a dictionary of parameters for
                          that profile
        - APERO_PROFILE_NAMES: list of strings

        parameters needed in params['APERO_PROFILES'] for each profile::

        - DATABASE_MODE: str, mysql+pymysql
        - DATABASE_HOST: str, the database host, e.g. localhost
        - DATABASE_USER: str, the database user, e.g. root
        - DATABASE_PASSWORD: str, the database password, e.g. password
        - DATABASE_NAME: str, the database name to connect to
        - ASTROM_TABLENAME: str, the name of the table containing astrometric
          data
        - CALIB_TABLENAME: str, the name of the table containing calibration
          data
        - FINDEX_TABLENAME: str, the name of the table containing file index
          data
        - LOG_TABLENAME: str, the name of the table containing log data
        - TELLU_TABLENAME: str, the name of the table containing telluric data
        - REJECT_TABLENAME: str, the name of the table containing rejected data
        - SCIENCE_FIBER: str, the name of the science fiber, e.g. 'A' or 'B'
        - SCIENCE_TYPES: list of str, the list of DPRTYPEs to include in
                            the object table, e.g. 'POLAR_FP', 'OBJ_SKY' etc
        - INSTRUEMNT: str, the name of the instrument, e.g. 'SPIROU'

        :param params: A dictionary of parameters needed to run the job.
        This should include database connection parameters and any other
        necessary information.
        """

        # get apero profiles:
        apero_profile_names = params["APERO_PROFILE_NAMES"]
        apero_profiles = params["APERO_PROFILES"]

        # Check if there are any profiles configured
        if not apero_profile_names:
            self.info = "No APERO profiles configured."
            return

        for a_it, apero_profile in enumerate(apero_profile_names):
            # -----------------------------------------------------------------
            # get parameters for this apero profile
            aparams = apero_profiles[apero_profile]
            # ----------------------------------------------------------------
            # Map DATABASE_USERNAME -> DATABASE_USER for database_query
            db_params = dict(aparams)
            if (
                "DATABASE_USERNAME" in db_params
                and "DATABASE_USER" not in db_params
            ):
                db_params["DATABASE_USER"] = db_params["DATABASE_USERNAME"]
            # -----------------------------------------------------------------
            # define the object name query
            obj_query = _construct_obj_query(aparams)
            print(f"Object name query for APERO profile: {apero_profile}\n")
            print(obj_query)
            print("\n\n")
            # ----------------------------------------------------------------
            # storage of timings per object
            timing_per_obj = []
            # storage of output file names
            output_files = []

            objlist = objnames.split(",")
            # -----------------------------------------------------------------
            for o_it, objname in enumerate(objlist):
                # start time
                start = time.time()
                # update the progress (combination of apero_profile + object)
                part1 = (o_it + 1) / len(objlist)
                part2 = (a_it + 1) / len(apero_profile_names)
                self.progress = part1 * part2

                # -------------------------------------------------------------
                # Step 1: Query the databases for the object and get all
                #         information
                # -------------------------------------------------------------
                # returns an object table (on row per parameter)
                # return a file table (one row per observation)
                outputs = object_query_db(
                    aparams,
                    objname,
                    apero_profile_names[a_it],
                    return_query=True,
                )


# =============================================================================
# Define main functions (used in run_job)
# =============================================================================
def _resolve_objects_dir(
    aparams: Dict[str, Any], profile_name: str,
) -> Path:
    """Return the per-profile objects output directory."""
    instrument = aparams.get("general", {}).get(
        "INSTRUMENT", aparams.get("INSTRUMENT", "unknown")
    )
    return (
        Path(aparams.get("LOCAL_DATA_DIR", str(secret_store.get_ari_dir())))
        / "tasks"
        / instrument
        / profile_name
        / "objects"
    )


def _profile_query_state_path(
    aparams: Dict[str, Any], profile_name: str,
) -> Path:
    """Return the persisted refresh status file for an APERO profile."""
    return _resolve_objects_dir(aparams, profile_name).parent / (
        ".object_query_state.json"
    )


def _save_profile_query_state(
    aparams: Dict[str, Any],
    profile_name: str,
    status: str,
    error: str = "",
) -> None:
    """Atomically save profile refresh status without losing last success."""
    state_path = _profile_query_state_path(aparams, profile_name)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        state = {}
    except json.JSONDecodeError:
        state = {}
    if not isinstance(state, dict):
        state = {}

    now = datetime.now(timezone.utc).isoformat()
    state["status"] = status
    state["last_attempt_at"] = now
    state["error"] = str(error or "")
    if status == "success":
        state["last_success_at"] = now

    tmp_path = state_path.with_name(state_path.name + ".tmp")
    tmp_path.write_text(
        json.dumps(state, sort_keys=True, indent=2), encoding="utf-8"
    )
    os.replace(tmp_path, state_path)


# =============================================================================
# Define functions
# =============================================================================
def object_query_db(
    aparams: Dict[str, Any],
    objname: str,
    apero_profile_name: str,
    return_query: bool = False,
) -> dict[str, Any]:
    """Query APERO tables and optionally save per-object file tables.

    Args:
        aparams: Hydrated APERO profile parameters.
        objname: Object name to query; an empty name returns empty results.
        apero_profile_name: Profile name used for output files and metadata.
        return_query: Print query strings instead of executing them.

    Returns:
        Mapping with ``queries``, ``timings``, and ``results`` entries.
    """
    if not objname:
        outputs = dict()
        outputs["queries"] = dict()
        outputs["timings"] = dict()
        outputs["results"] = dict()
        return outputs

    # check that all required parameters are present
    rparams = _check_required(aparams)

    # get parameters only needed for sub-commands
    fiber = rparams["SCIENCE_FIBER"]
    scitypes = rparams["SCIENCE_TYPES"]
    # storage of queries
    queries = dict()
    # raw file table
    raw_results = _file_col_query(
        rparams, objname, block_kind="raw", scitype=scitypes
    )
    queries["raw"] = raw_results
    # pp file table
    pp_results = _file_col_query(
        rparams, objname, block_kind="tmp", scitype=scitypes
    )
    queries["pp"] = pp_results
    # red file table
    ext_results = _file_col_query(
        rparams,
        objname,
        block_kind="red",
        scitype=scitypes,
        output="EXT_E2DS_FF",
        fiber=fiber,
    )
    queries["ext"] = ext_results
    # tcorr file table
    tcorr_results = _file_col_query(
        rparams,
        objname,
        block_kind="red",
        scitype=scitypes,
        output="TELLU_OBJ",
        fiber=fiber,
    )
    queries["tcorr"] = tcorr_results
    # ccf file table
    ccf_results = _file_col_query(
        rparams,
        objname,
        block_kind="red",
        scitype=scitypes,
        output="CCF_RV",
        fiber=fiber,
    )
    queries["ccf"] = ccf_results
    # e.fits file table
    efits_results = _file_col_query(
        rparams, objname, block_kind="out", output="DRS_POST_E"
    )
    queries["efits"] = efits_results
    # t.fits file table
    tfits_results = _file_col_query(
        rparams, objname, block_kind="out", output="DRS_POST_T"
    )
    queries["tfits"] = tfits_results

    # all files (must run before lbl/lbl_rdb so IDENTIFIER-matched
    # backfilling can use ftable_all rows as source metadata)
    all_results = _file_col_query(rparams, objname)
    queries["all"] = all_results

    # lbl fits file table
    lbl_results = _file_col_query(
        rparams, objname, block_kind="lbl", scitype=scitypes, output="LBL_FITS"
    )
    queries["lbl"] = lbl_results

    # lbl rdb file table (one row per science+comparison pair)
    lbl_rdb_results = _file_col_query(
        rparams, objname, block_kind="lbl", scitype=None, output="LBL_RDB"
    )
    queries["lbl_rdb"] = lbl_rdb_results
    # storage for timing for database queries
    outputs = dict()
    outputs["queries"] = queries
    outputs["timings"] = dict()
    outputs["results"] = dict()
    # deal with returning just the queries (we print them)
    if return_query:
        for key, query in queries.items():
            print(f"Query for {key}:\n\n{query}\n\n\n\n")
    # deal with running the queries and saving the results
    else:
        # loop around queries and execute them, storing the results in files
        # for the UI to use
        for key, query in queries.items():
            try:
                outputs = _file_col_cmd(
                    aparams,
                    query,
                    apero_profile_name,
                    objname=objname,
                    fkind=key,
                    outputs=outputs,
                )
            except Exception as e:
                # inject a print out of the query for debugging
                emg = f"{key} query: \n{query}\n\nError: {str(e)}"
                raise RuntimeError(emg)

    return outputs


def _normalize_mp_config(task_config: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize multiprocessing config from TASK_CONFIG."""
    cfg = task_config or {}
    try:
        ncores = int(cfg.get("ncores", cfg.get("NCORES", 1)) or 1)
    except (TypeError, ValueError):
        ncores = 1
    ncores = max(1, ncores)

    backend = str(cfg.get("mp_backend", "threads") or "threads").strip().lower()
    if backend not in ("threads", "processes"):
        backend = "threads"

    start_method = (
        str(cfg.get("mp_start_method", "default") or "default").strip().lower()
    )
    if start_method not in ("default", "spawn", "fork", "forkserver"):
        start_method = "default"

    max_cores = max(int(os.cpu_count() or 1), 1)
    ncores = min(max_cores, ncores)
    return {
        "ncores": ncores,
        "backend": backend,
        "start_method": start_method,
    }


def _normalize_filters(raw_filters: Any) -> Dict[str, str]:
    """Normalize task filters into uppercase {KEY: value} strings."""
    out = apero_async.normalize_filter_map(raw_filters)
    # Backward compatibility: accept legacy OBJNAME key as exclude.
    has_legacy = "OBJNAME" in out
    has_new = "OBJNAME_EXCLUDE" in out
    if has_legacy and not has_new:
        out["OBJNAME_EXCLUDE"] = out.get("OBJNAME", "")
    if has_legacy:
        out.pop("OBJNAME", None)
    return out


def _parse_objname_list(raw_value: Any) -> set[str]:
    """Parse object-name list from comma/semicolon/newline string."""
    text = str(raw_value or "").strip()
    if not text:
        return set()
    norm = text.replace(";", ",").replace("\n", ",")
    values = {
        chunk.strip().lower()
        for chunk in norm.split(",")
        if chunk and chunk.strip()
    }
    return values


def _make_executor(
    backend: str, ncores: int, start_method: str, tlog: Any,
) -> tuple[Any, str]:
    """Build executor and return (executor, mode) with fallback to threads."""
    if backend == "processes":
        try:
            ctx = None
            if start_method != "default":
                ctx = mp.get_context(start_method)
            mode = (
                "ProcessPoolExecutor"
                if start_method == "default"
                else f"ProcessPoolExecutor[{start_method}]"
            )
            return ProcessPoolExecutor(max_workers=ncores, mp_context=ctx), mode
        except Exception as exc:
            tlog(f"Process pool init failed ({exc}); falling back to threads.")
    return ThreadPoolExecutor(max_workers=ncores), "ThreadPoolExecutor"


def _run_single_object_job(
    aparams: Dict[str, Any],
    objname: str,
    apero_profile_name: str,
    force_run: bool = False,
) -> Dict[str, Any]:
    """Run one object query+header workflow and return summary metrics."""
    worker_pid = os.getpid()
    start_total = time.time()
    local_dir = _resolve_objects_dir(aparams, apero_profile_name)
    local_dir.mkdir(parents=True, exist_ok=True)
    current_product_fp = _product_change_fingerprint(aparams, objname)
    prev_product_fp = _load_object_product_fingerprint(local_dir, objname)

    # If existing LBL files still contain null security fields, force a
    # rebuild so IDENTIFIER-based backfilling can repair them.
    needs_lbl_security_fix = _needs_lbl_security_rebuild(local_dir, objname)

    is_changed = (
        force_run
        or (prev_product_fp is None)
        or (current_product_fp != prev_product_fp)
        or needs_lbl_security_fix
    )
    if not is_changed:
        output_files = [
            str(path) for path in _object_output_paths(local_dir, objname)
        ]
        return {
            "object_total": float(time.time() - start_total),
            "header_time": 0.0,
            "header_rows": 0,
            "worker_pid": int(worker_pid),
            "output_files": output_files,
            "skipped": True,
        }

    stage_root = tempfile.TemporaryDirectory(
        prefix=".object-query-", dir=local_dir.parent
    )
    try:
        stage_params = dict(aparams)
        stage_params["LOCAL_DATA_DIR"] = stage_root.name
        stage_params["INSTRUMENT"] = (
            aparams.get("INSTRUMENT")
            or aparams.get("general", {}).get("INSTRUMENT")
            or "unknown"
        )
        stage_dir = _resolve_objects_dir(stage_params, apero_profile_name)
        outputs = object_query_db(
            stage_params, objname, apero_profile_name
        )
        htime = object_query_headers(
            stage_params, objname, apero_profile_name, outputs
        )
        staged_paths = _object_output_paths(stage_dir, objname)
        if not any(path.name == f"htable_{objname}.json"
                   for path in staged_paths):
            raise RuntimeError(
                f"Object query did not create an htable for {objname}"
            )

        updated_product_fp = _product_change_fingerprint(aparams, objname)
        if updated_product_fp != current_product_fp:
            raise RuntimeError(
                f"Indexed products changed during refresh for {objname}; "
                "retrying on the next task run"
            )

        _publish_object_outputs(stage_dir, local_dir, objname)
        _save_object_product_fingerprint(
            local_dir, objname, updated_product_fp
        )
        output_files = [
            str(path) for path in _object_output_paths(local_dir, objname)
        ]
    finally:
        stage_root.cleanup()

    result_rows = outputs.get("results", {})
    header_rows = sum(
        len(rows)
        for rows in result_rows.values()
        if isinstance(rows, list)
    ) if isinstance(result_rows, dict) else 0

    return {
        "object_total": float(time.time() - start_total),
        "header_time": float(htime),
        "header_rows": int(header_rows),
        "worker_pid": int(worker_pid),
        "output_files": output_files,
        "skipped": False,
    }


def _product_change_query(
    rparams: Dict[str, Any], objname: str,
) -> str:
    """Construct a per-object query covering every indexed product."""
    objname_safe = objname.replace("'", "''")
    query = """
    SELECT
        fdb.BLOCK_KIND AS BLOCK_KIND,
        fdb.KW_OUTPUT AS KW_OUTPUT,
        fdb.KW_FIBER AS KW_FIBER,
        fdb.KW_DPRTYPE AS KW_DPRTYPE,
        fdb.KW_RUN_ID AS KW_RUN_ID,
        fdb.KW_PI_NAME AS KW_PI_NAME,
        fdb.IDENTIFIER AS IDENTIFIER,
        fdb.OBS_DIR AS OBS_DIR,
        fdb.FILENAME AS FILENAME,
        fdb.LAST_MODIFIED AS LAST_MODIFIED
    FROM {FINDEX_TABLENAME} fdb
    WHERE fdb.KW_OBJNAME = '{OBJNAME}'
    ORDER BY fdb.BLOCK_KIND, fdb.KW_OUTPUT, fdb.KW_FIBER,
             fdb.KW_DPRTYPE, fdb.IDENTIFIER, fdb.OBS_DIR,
             fdb.FILENAME, fdb.LAST_MODIFIED
    """
    return query.format(
        OBJNAME=objname_safe,
        **rparams,
    )


def _product_change_fingerprint(
    aparams: Dict[str, Any], objname: str,
) -> str:
    """Return a stable fingerprint of all indexed products for an object."""
    rparams = _check_required(aparams)
    query = _product_change_query(rparams, objname)
    db_params = apero_async.get_db_params(aparams)
    results = apero_async.database_query(db_params, query)
    if not isinstance(results, list):
        raise RuntimeError(
            f"Product fingerprint query returned invalid data for {objname}"
        )
    encoded = json.dumps(
        results, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _object_state_file(local_dir: Path, objname: str) -> Path:
    """Return per-object state filename used for product fingerprints."""
    return Path(local_dir) / f".state_{objname}.json"


def _load_object_product_fingerprint(
    local_dir: Path, objname: str
) -> Optional[str]:
    """Load the current product fingerprint for one object."""
    state_file = _object_state_file(local_dir, objname)
    if not state_file.exists():
        return None
    try:
        payload = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("schema_version") != 2:
        return None
    value = payload.get("product_fingerprint", None)
    return None if value in (None, "") else str(value)


def _save_object_product_fingerprint(
    local_dir: Path, objname: str, fingerprint: str
) -> None:
    """Atomically persist the successfully published product fingerprint."""
    state_file = _object_state_file(local_dir, objname)
    payload = {
        "schema_version": 2,
        "product_fingerprint": str(fingerprint or ""),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    tmp_path = state_file.with_name(state_file.name + ".tmp")
    tmp_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8"
    )
    os.replace(tmp_path, state_file)


def _object_output_paths(local_dir: Path, objname: str) -> list[Path]:
    """Return the generated table files for one object."""
    local_dir = Path(local_dir)
    if not local_dir.exists():
        return []
    fsuffix = f"_{objname}.json"
    return [
        path for path in local_dir.iterdir()
        if path.is_file()
        and (
            path.name == f"htable_{objname}.json"
            or (
                path.name.startswith("ftable_")
                and path.name.endswith(fsuffix)
            )
        )
    ]


def _publish_object_outputs(
    stage_dir: Path, local_dir: Path, objname: str,
) -> None:
    """Publish staged tables and roll back if replacing a file fails."""
    staged_paths = _object_output_paths(stage_dir, objname)
    staged_names = {path.name for path in staged_paths}
    if f"htable_{objname}.json" not in staged_names:
        raise RuntimeError(f"Staged object tables lack an htable for {objname}")

    local_dir.mkdir(parents=True, exist_ok=True)
    old_paths = _object_output_paths(local_dir, objname)
    old_names = {path.name for path in old_paths}
    backup_root = tempfile.TemporaryDirectory(
        prefix=".object-query-backup-", dir=local_dir.parent
    )
    backup_dir = Path(backup_root.name)
    try:
        for old_path in old_paths:
            shutil.copy2(old_path, backup_dir / old_path.name)
        try:
            for staged_path in staged_paths:
                os.replace(staged_path, local_dir / staged_path.name)

            for old_path in old_paths:
                if old_path.name not in staged_names:
                    old_path.unlink()
        except OSError as publish_error:
            rollback_errors = []
            for path in _object_output_paths(local_dir, objname):
                if path.name not in old_names:
                    try:
                        path.unlink()
                    except OSError as rollback_error:
                        rollback_errors.append(str(rollback_error))
            for name in old_names:
                try:
                    os.replace(backup_dir / name, local_dir / name)
                except OSError as rollback_error:
                    rollback_errors.append(str(rollback_error))
            if rollback_errors:
                detail = "; ".join(rollback_errors)
                raise RuntimeError(
                    f"Publishing tables failed and rollback was incomplete: "
                    f"{detail}"
                ) from publish_error
            raise
    finally:
        backup_root.cleanup()


def _needs_lbl_security_rebuild(local_dir: Path, objname: str) -> bool:
    """Return True when existing LBL rows still miss KW_RUN_ID/KW_PI_NAME."""
    local_dir = Path(local_dir)
    targets = [
        local_dir / f"ftable_lbl_{objname}.json",
        local_dir / f"ftable_lbl_rdb_{objname}.json",
    ]
    for path in targets:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            # Corrupt/invalid output should be regenerated.
            return True
        rows = payload.get("rows", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            return True
        for row in rows:
            if not isinstance(row, dict):
                continue
            run_id = str(row.get("KW_RUN_ID", "") or "").strip()
            pi_name = str(row.get("KW_PI_NAME", "") or "").strip()
            if not run_id or not pi_name:
                return True
    return False


def object_query_headers(
    aparams: Dict[str, Any],
    objname: str,
    apero_profile_name: str,
    outputs: Dict[str, Any],
) -> float:
    """Read configured FITS cards and save one object's header table.

    Args:
        aparams: Hydrated APERO profile parameters.
        objname: Object name whose file headers are collected.
        apero_profile_name: Profile name used for output files and metadata.
        outputs: Query results grouped by file kind.

    Returns:
        Time spent reading headers, in seconds.
    """
    # get results
    results = outputs["results"]
    # output table
    header_dict = dict()
    # start time
    start = time.time()
    # loop around file kinds
    for fkind in results:
        # get entries for this fkind
        entries = results[fkind]
        # get the hkeys for this fkind
        hcfg = aparams.get("sci-headers", aparams.get("headers", {}))
        if not isinstance(hcfg, dict):
            hcfg = {}
        hkeys = hcfg.get(fkind, None)
        # deal with no header keys
        if hkeys is None or len(hkeys) == 0:
            continue
        # loop around each entry
        for entry in entries:
            # get identifier
            identifier = entry["IDENTIFIER"]
            # get block kind
            block_kind = BLOCK_KIND.get(entry["BLOCK_KIND"], None)
            # deal with no block kind defined
            if block_kind is None:
                continue
            # deal with first time we see this object
            if identifier not in header_dict:
                header_dict[identifier] = dict(IDENTIFIER=identifier)
            # -----------------------------------------------------------------
            # convert block kind to a path
            block_kind = aparams["paths"][block_kind]
            # construct filename from keys
            abspath = Path(block_kind) / entry["OBS_DIR"] / entry["FILENAME"]
            # -----------------------------------------------------------------
            # check if path exists - on SSHFS this can raise OSError
            try:
                path_exists = abspath.exists()
            except OSError as exc:
                raise OSError(
                    f"Cannot access indexed file {abspath}"
                ) from exc
            if not path_exists:
                raise FileNotFoundError(
                    f"Indexed file is missing: {abspath}"
                )
            # -----------------------------------------------------------------
            # check if file is fits file
            if abspath.suffix != ".fits":
                header_dict[identifier] = apero_async.fill_dict_null(hkeys)
                continue
            # otherwise we open the file
            try:
                hdr = fits.getheader(abspath)
            except OSError as exc:
                raise OSError(
                    f"Cannot read FITS header from {abspath}"
                ) from exc
            # loop around header key and load into header list
            for hkey in hkeys:
                _hvalue = apero_async.get_hdr_key(hdr, hkey, hkeys[hkey])
                header_dict[identifier][hkey] = _hvalue
    # end time
    end = time.time()
    # ---------------------------------------------------------------------
    # convert header dict to a list of dictionaries (one list entry for
    # each identifier)
    header_list = []
    for key in header_dict:
        header_list.append(header_dict[key])
    # ---------------------------------------------------------------------
    # time now
    time_now = datetime.now(timezone.utc).isoformat()
    metadata = dict()
    metadata["GENERATED_AT"] = time_now
    metadata["QUERY_TIME"] = end - start
    metadata["APERO_PROFILE"] = apero_profile_name
    # ---------------------------------------------------------------------
    # construct filename
    instrument = aparams.get("INSTRUMENT", "unknown")
    local_dir = (
        Path(aparams.get("LOCAL_DATA_DIR", str(secret_store.get_ari_dir())))
        / "tasks"
        / instrument
        / apero_profile_name
        / "objects"
    )
    basename = f"htable_{objname}.json"
    filename = local_dir / basename
    # save results to JSON file for use in the UI
    apero_async.save_results(filename, header_list, metadata)

    return metadata["QUERY_TIME"]


# -------------------------------------------------------------------------
# Define helper functions
# -------------------------------------------------------------------------
def _construct_obj_query(aparams: Dict[str, Any]) -> str:
    """Build the distinct raw-object query for a profile.

    Args:
        aparams: Profile settings containing science types and file-index
            table name.

    Returns:
        SQL selecting distinct raw object names.

    Raises:
        ValueError: If the file-index table name is missing.
    """
    general = aparams.get("general", {})
    if not isinstance(general, dict):
        general = {}
    database = aparams.get("database", {})
    if not isinstance(database, dict):
        database = {}
    science_types = general.get(
        "SCIENCE_TYPES", aparams.get("SCIENCE_TYPES", [])
    )
    if not isinstance(science_types, list):
        science_types = [science_types]
    scitypes = ",".join([f'"{t}"' for t in science_types])
    findex_table = database.get(
        "FINDEX_TABLENAME", aparams.get("FINDEX_TABLENAME", "")
    )
    if not findex_table:
        raise ValueError(
            "Missing required parameter: database.FINDEX_TABLENAME"
        )
    oparams = dict(FINDEX_TABLENAME=findex_table, SCIENCE_TYPES=scitypes)

    obj_query = (
        "SELECT DISTINCT KW_OBJNAME FROM {FINDEX_TABLENAME} "
        ' WHERE BLOCK_KIND="raw" AND '
        "KW_DPRTYPE IN ({SCIENCE_TYPES})"
    )
    obj_query = obj_query.format(**oparams)
    return obj_query


def _file_col_query(
    rparams: Dict[str, Any],
    objname: str,
    block_kind: Optional[str] = None,
    fiber: Optional[str] = None,
    scitype: Any = None,
    output: Optional[str] = None,
) -> str:
    """Build a file-index query for one object and optional filters.

    Args:
        rparams: Required table names and science settings.
        objname: Object name to select.
        block_kind: Optional file block kind filter.
        fiber: Optional fiber filter.
        scitype: Whether to apply the profile's science-type filter.
        output: Optional output-type filter.

    Returns:
        SQL query string for the selected file rows.
    """
    objname_safe = objname.replace("'", "''")
    # deal with optional conditions
    condition = []
    if block_kind is not None:
        condition.append(f"fdb.BLOCK_KIND = '{block_kind}'")
    if fiber is not None:
        condition.append(f"fdb.KW_FIBER = '{fiber}'")
    if scitype is not None:
        scitype_list = ", ".join([f"'{t}'" for t in rparams["SCIENCE_TYPES"]])
        condition.append(f"fdb.KW_DPRTYPE IN ({scitype_list})")
    if output is not None:
        condition.append(f"fdb.KW_OUTPUT = '{output}'")
    # construct the query
    query = """
    SELECT
        fdb.BLOCK_KIND AS BLOCK_KIND,
        fdb.OBS_DIR AS OBS_DIR,
        fdb.FILENAME AS FILENAME,
        fdb.KW_IDENTIFIER AS IDENTIFIER,
        fdb.KW_DPRTYPE AS KW_DPRTYPE,
        fdb.KW_OUTPUT AS KW_OUTPUT,
        fdb.KW_FIBER AS KW_FIBER,
        fdb.KW_RUN_ID AS KW_RUN_ID,
        fdb.KW_PI_NAME AS KW_PI_NAME,
        FROM_UNIXTIME((fdb.KW_MID_OBS_TIME - 40587) * 86400) AS MID_OBS_TIME,
        FROM_UNIXTIME(fdb.LAST_MODIFIED) AS LAST_MODIFIED,
        fdb.KW_PID AS PID,
        fdb.KW_DRS_QC AS PASSED_ALL_QC
    FROM {FINDEX_TABLENAME} fdb
    WHERE fdb.KW_OBJNAME = '{OBJNAME}' {CONDITION}
    """
    # construct the formatted query
    if len(condition) > 0:
        condition = " AND " + " AND ".join(condition)
    else:
        condition = ""
    rquery = query.format(OBJNAME=objname_safe, CONDITION=condition, **rparams)
    # deal with just returning the query for testing
    return rquery


def _file_col_cmd(
    aparams: Dict[str, Any],
    rquery: str,
    apero_profile_name: str,
    objname: str,
    fkind: str,
    outputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute a file query, backfill security fields, and store its rows.

    Args:
        aparams: Hydrated APERO profile parameters.
        rquery: SQL statement for the file table.
        apero_profile_name: Profile name used in saved metadata.
        objname: Object name used to name the output file.
        fkind: File-table kind used to label results and output.
        outputs: Accumulated query, timing, and result mappings.

    Returns:
        Updated output mappings containing this query's rows and timing.
    """
    db_params = apero_async.get_db_params(aparams)
    start = time.time()
    results = apero_async.database_query(db_params, rquery)

    # For LBL products, some rows can miss KW_RUN_ID / KW_PI_NAME because
    # those header keys are absent in LBL files. Backfill from matching
    # IDENTIFIER rows in ftable_all first, then fallback to t.fits.
    if fkind in ("lbl", "lbl_rdb"):
        all_rows = outputs.get("results", {}).get("all", [])
        tfits_rows = outputs.get("results", {}).get("tfits", [])
        results = _backfill_lbl_security_fields(results, all_rows, tfits_rows)

    # The combined "all" ftable also contains LBL rows that may be
    # missing KW_RUN_ID / KW_PI_NAME for the same reason. Backfill those
    # in-place from the non-LBL rows in the same result set so downstream
    # consumers (e.g. file browser access filtering) don't strip them.
    # Note: this runs before lbl/lbl_rdb queries (see queries dict order),
    # so we only have the in-set non-LBL rows as donors here, which is
    # enough for any LBL file whose source identifier appears in "all".
    if fkind == "all" and isinstance(results, list) and results:
        from apero_ri.core.basket_funcs import backfill_lbl_run_ids

        results = backfill_lbl_run_ids(results)

    end = time.time()
    # ---------------------------------------------------------------------
    # time now
    time_now = datetime.now(timezone.utc).isoformat()
    metadata = dict()
    metadata["GENERATED_AT"] = time_now
    metadata["QUERY_TIME"] = end - start
    metadata["APERO_PROFILE"] = apero_profile_name

    # only save if there are results
    if isinstance(results, list) and len(results) > 0:
        # construct filename
        instrument = aparams.get("INSTRUMENT", "unknown")
        local_dir = (
            Path(aparams.get("LOCAL_DATA_DIR", str(secret_store.get_ari_dir())))
            / "tasks"
            / instrument
            / apero_profile_name
            / "objects"
        )
        basename = f"ftable_{fkind}_{objname}.json"
        filename = local_dir / basename
        # save results to JSON file for use in the UI
        apero_async.save_results(filename, results, metadata)
    # store timing for this object
    outputs["timings"][fkind] = metadata["QUERY_TIME"]
    outputs["results"][fkind] = results

    return outputs


def _backfill_lbl_security_fields(
    lbl_rows: Any, all_rows: Any, tfits_rows: Any,
) -> Any:
    """Fill missing LBL run and PI fields from matching source rows.

    Args:
        lbl_rows: LBL result rows to patch.
        all_rows: Combined file-table rows used as the primary source.
        tfits_rows: T.fits rows used as the fallback source.

    Returns:
        The original LBL input when it is not a non-empty list; otherwise
        rows with missing security fields filled where a match is found.
    """
    if not isinstance(lbl_rows, list) or not lbl_rows:
        return lbl_rows

    by_identifier = dict()
    by_obs_dir = dict()

    def _ingest_source_rows(source_rows: Any) -> None:
        """Index source security fields by identifier and observation dir."""
        if not isinstance(source_rows, list):
            return
        for row in source_rows:
            if not isinstance(row, dict):
                continue
            ident = str(row.get("IDENTIFIER", "") or "").strip()
            obs_dir = str(row.get("OBS_DIR", "") or "").strip()
            run_id = str(row.get("KW_RUN_ID", "") or "").strip()
            pi_name = str(row.get("KW_PI_NAME", "") or "").strip()
            if not (run_id or pi_name):
                continue
            payload = {"KW_RUN_ID": run_id, "KW_PI_NAME": pi_name}
            if ident and ident not in by_identifier:
                by_identifier[ident] = payload
            if obs_dir and obs_dir not in by_obs_dir:
                by_obs_dir[obs_dir] = payload

    # Primary source: ftable_all (explicit user-requested upstream source)
    _ingest_source_rows(all_rows)
    # Fallback source: t.fits
    _ingest_source_rows(tfits_rows)

    if not by_identifier and not by_obs_dir:
        return lbl_rows

    patched = []
    for row in lbl_rows:
        if not isinstance(row, dict):
            patched.append(row)
            continue

        run_id = str(row.get("KW_RUN_ID", "") or "").strip()
        pi_name = str(row.get("KW_PI_NAME", "") or "").strip()
        if run_id and pi_name:
            patched.append(row)
            continue

        ident = str(row.get("IDENTIFIER", "") or "").strip()
        obs_dir = str(row.get("OBS_DIR", "") or "").strip()
        src = by_identifier.get(ident) or by_obs_dir.get(obs_dir)
        if not src:
            patched.append(row)
            continue

        new_row = dict(row)
        if not run_id and src.get("KW_RUN_ID"):
            new_row["KW_RUN_ID"] = src["KW_RUN_ID"]
        if not pi_name and src.get("KW_PI_NAME"):
            new_row["KW_PI_NAME"] = src["KW_PI_NAME"]
        patched.append(new_row)

    return patched


def _check_required(aparams: Dict[str, Any]) -> Dict[str, Any]:
    """Extract required database and science settings from a profile.

    Args:
        aparams: Hydrated APERO profile parameters.

    Returns:
        Flat mapping of table names, science fiber, and science types.

    Raises:
        ValueError: If a required profile parameter is absent.
    """
    required_params = [
        "ASTROM_TABLENAME",
        "CALIB_TABLENAME",
        "FINDEX_TABLENAME",
        "LOG_TABLENAME",
        "TELLU_TABLENAME",
        "REJECT_TABLENAME",
    ]
    # Check and cut down parameters needed for query
    rparams = dict()
    # Prefer nested database config and flatten required keys for SQL
    # templates.
    db_cfg = aparams.get("database", {})
    if not isinstance(db_cfg, dict):
        db_cfg = {}
    # loop around parameters
    for param in required_params:
        value = db_cfg.get(param, aparams.get(param))
        if value in (None, ""):
            raise ValueError(f"Missing required parameter: database.{param}")
        rparams[param] = value
    # extract science params from the 'general' sub-dict and flatten into
    # rparams
    general = aparams.get("general", {})
    for key in ("SCIENCE_FIBER", "SCIENCE_TYPES"):
        if key not in general:
            raise ValueError(f"Missing required parameter: general.{key}")
        rparams[key] = general[key]
    # return the required parameters
    return rparams


def _acquire_directory_lock(directory: Path) -> Any:
    """Acquire an exclusive lock for a directory using a sidecar lock file."""
    import fcntl

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / ".objects.lock"
    lock_handle = lock_path.open("a+")
    # Blocking lock: waits until another process releases the lock.
    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)

    class _DirectoryLock:
        def __enter__(self) -> Any:
            """Return the open sidecar lock file while holding its lock."""
            return lock_handle

        def __exit__(
            self, exc_type: Any, exc: Any, tb: Any,
        ) -> None:
            """Release the lock and close its sidecar file."""
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            finally:
                lock_handle.close()

    return _DirectoryLock()


def _clear_directory_contents(directory: Path) -> None:
    """
    Delete all children in a directory while preserving the directory itself.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for entry in directory.iterdir():
        if entry.name == ".objects.lock":
            continue
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=False)
        else:
            entry.unlink()


# =============================================================================
# Start of main code
# =============================================================================
if __name__ == "__main__":
    from apero_ri.core.auth import load_apero_profiles

    # -- Configure which profile to test with --
    _TEST_INSTRUMENT = "SPIROU"
    _TEST_PROFILE = "spirou_xxs_08_cook_home"

    # Load profiles from ~/.ari/admin/apero_profiles.yaml
    _all_profiles = load_apero_profiles()
    _inst_profiles = _all_profiles.get(_TEST_INSTRUMENT, {})
    if _TEST_PROFILE not in _inst_profiles:
        raise RuntimeError(
            f'Profile "{_TEST_PROFILE}" not found under instrument '
            f'"{_TEST_INSTRUMENT}" in apero_profiles.yaml'
        )
    _profile = _inst_profiles[_TEST_PROFILE]

    task = AperoObjectQueryTask()
    run_params = {
        "LOCAL_DATA_DIR": str(secret_store.get_ari_dir()),
        "INSTRUMENT": _TEST_INSTRUMENT.lower(),
        "APERO_PROFILE_NAMES": [_TEST_PROFILE],
        "APERO_PROFILES": {_TEST_PROFILE: _profile},
    }
    # task.test_query(run_params, objnames='GL699')
    task.run_job(run_params)
# =============================================================================
# End of main code
# =============================================================================

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
