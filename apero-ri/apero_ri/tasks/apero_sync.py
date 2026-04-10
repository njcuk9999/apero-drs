#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Standalone local task runner.

Run any registered APERO RI task locally on a machine that has apero_ri
installed, without needing a server, scheduler, or web UI.

Usage example (from a Python script or REPL on the data-hosting machine)::

    from apero_ri.tasks import apero_sync

    # Minimal params – only what the task actually needs.
    params = {
        'LOCAL_DATA_DIR': '/data/spirou/ari_local',
        'INSTRUMENT': 'SPIROU',
        'APERO_PROFILES': {
            'my_profile': {
                'database': {
                    'DATABASE_MODE': 'mysql+pymysql',
                    'DATABASE_HOST': 'localhost:3306',
                    'DATABASE_USER': 'root',
                    'DATABASE_PASSWORD': 'secret',
                    'DATABASE_NAME': 'spirou_db',
                    'FINDEX_TABLENAME': 'FILE_INDEX',
                    'ASTROM_TABLENAME': 'ASTROMETRY',
                    'CALIB_TABLENAME': 'CALIBRATION',
                    'LOG_TABLENAME': 'LOG_TABLE',
                    'TELLU_TABLENAME': 'TELLURIC',
                    'REJECT_TABLENAME': 'REJECT_TABLE',
                },
                'general': {
                    'INSTRUMENT': 'SPIROU',
                    'SCIENCE_FIBER': 'A',
                    'SCIENCE_TYPES': ['OBJ_SKY', 'POLAR_FP'],
                },
                'paths': {
                    'raw': '/data/spirou/raw',
                    'tmp': '/data/spirou/tmp',
                    'red': '/data/spirou/red',
                    'out': '/data/spirou/out',
                    'lbl': '/data/spirou/lbl',
                    'calib': '/data/spirou/calib',
                },
                'sci-headers': { ... },
            },
        },
        'APERO_PROFILE_NAMES': ['my_profile'],
        'TASK_CONFIG': {
            'force_run': True,
            'ncores': 4,
        },
    }
    apero_sync.run('APERO_OBJECT_QUERY', params)

The output JSON files are written under ``LOCAL_DATA_DIR/tasks/<instrument>/…``
just as they would be on the ARI server.  The server task can then be
configured with ``sync_source`` to copy those files instead of re-running the
heavy DB+FITS queries over SSHFS.
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
# Module-level name used for logging / identification in tracebacks
__NAME__ = "apero_ri.tasks.apero_sync"


# =============================================================================
# Public API
# =============================================================================
def run(
    task_key: str,
    params: Dict[str, Any],
    *,
    verbose: bool = True,
    log_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a registered APERO RI task locally with the supplied params.

    Parameters
    ----------
    task_key : str
        Registry key from ``apero_ri.tasks.TASK_LIST``, e.g.
        ``'APERO_OBJECT_QUERY'``.
    params : dict
        The ``run_job`` parameter dict.  At minimum must contain
        ``LOCAL_DATA_DIR`` and whatever the target task requires (see
        each task module's ``PARAM_LIST``).
    verbose : bool
        If True (default), progress messages are printed to stdout.
    log_file : str, optional
        Path to a file where progress messages are also appended.

    Returns
    -------
    dict
        Summary with keys ``status``, ``duration_s``, ``info``,
        ``output_files``.
    """
    # Late import: avoids circular imports and lets this module be
    # imported without triggering full task registration overhead.
    from apero_ri import tasks as task_module

    # ---- validate task key -------------------------------------------------
    # TASK_LIST is the central registry mapping string keys (e.g.
    # 'APERO_OBJECT_QUERY') to their AperoAsyncTask sub-classes.
    if task_key not in task_module.TASK_LIST:
        available = sorted(task_module.TASK_LIST.keys())
        raise ValueError(
            f"Unknown task key {task_key!r}.  "
            f'Available: {", ".join(available)}'
        )

    # apero_sync is intentionally restricted to tasks that explicitly
    # support local pre-built workflows (LOCAL_TASK=True).
    local_allowed = bool(task_module.LOCAL_TASK.get(task_key, False))
    if not local_allowed:
        allowed = ", ".join(sorted(local_task_keys()))
        raise ValueError(
            f"Task {task_key!r} is not LOCAL_TASK-enabled. "
            f"Allowed tasks: {allowed}"
        )

    # Some tasks may fail to import (e.g. missing optional dependency).
    # IMPORT_ERRORS stores the traceback string, if any, keyed by task key.
    import_error = (task_module.IMPORT_ERRORS or {}).get(task_key, "")
    if import_error:
        raise RuntimeError(
            f"Task {task_key!r} failed to import:\n{import_error}"
        )

    # ---- build logger ------------------------------------------------------
    # Create a timestamped logging function that prints to stdout and/or
    # a log file.  Tasks expect a callable under params['TASK_LOGGER'].
    logger = _build_logger(verbose, log_file)
    # Shallow-copy params so we can inject keys without mutating the
    # caller's dict.
    params = dict(params)
    # Inject the logger so the task's run_job can call
    # params['TASK_LOGGER'](msg) without needing the web-server logging
    # infrastructure.
    params["TASK_LOGGER"] = logger

    # ---- ensure LOCAL_DATA_DIR exists --------------------------------------
    # LOCAL_DATA_DIR is the root directory where all task output JSON/CSV
    # files are written (under tasks/<instrument>/<profile>/…).
    local_data_dir = params.get("LOCAL_DATA_DIR")
    if local_data_dir:
        # Create the directory tree if it doesn't exist yet.
        Path(local_data_dir).mkdir(parents=True, exist_ok=True)

    # ---- inject INSTRUMENT into each profile's general dict ----------------
    # Tasks expect each profile config to carry INSTRUMENT both at the
    # top-level and inside the 'general' sub-dict.  When running locally
    # users often only set it at the top level, so we propagate it down.
    instrument = params.get("INSTRUMENT", "")
    profiles = params.get("APERO_PROFILES", {})
    for _pname, pcfg in profiles.items():
        if not isinstance(pcfg, dict):
            continue
        # Ensure the 'general' sub-dict exists and carries INSTRUMENT.
        general = pcfg.setdefault("general", {})
        if isinstance(general, dict):
            general.setdefault("INSTRUMENT", instrument)
        # Also set INSTRUMENT and LOCAL_DATA_DIR at the profile top-level
        # because some helper functions read them from there directly.
        pcfg.setdefault("INSTRUMENT", instrument)
        pcfg.setdefault(
            "LOCAL_DATA_DIR", local_data_dir or str(Path.home() / ".ari")
        )

    # If the caller didn't explicitly list profile names, derive them
    # from the keys of the APERO_PROFILES dict (order preserved in 3.7+).
    if "APERO_PROFILE_NAMES" not in params:
        params["APERO_PROFILE_NAMES"] = list(profiles.keys())

    # TASK_CONFIG carries per-task overrides like force_run, ncores, etc.
    # Default to an empty dict so tasks can safely call .get() on it.
    if "TASK_CONFIG" not in params:
        params["TASK_CONFIG"] = {}

    # ---- instantiate and run -----------------------------------------------
    # Look up the task class from the registry and create a fresh instance.
    # Each instance has its own .info, .progress, .output_files attributes
    # that run_job populates during execution.
    task_cls = task_module.TASK_LIST[task_key]
    instance = task_cls()
    logger(f"apero_sync: running {task_key}")

    # Record a high-resolution start time for duration measurement.
    t0 = time.perf_counter()
    status = "completed"
    error = ""
    try:
        # run_job is the main entry point defined by each AperoAsyncTask
        # sub-class.  It reads from params and writes results to disk.
        instance.run_job(params)
    except Exception as exc:
        # If run_job raises, capture the error but do not re-raise so we
        # can still return a summary dict to the caller.
        status = "failed"
        error = str(exc)
        import traceback

        logger(f"apero_sync: {task_key} FAILED: {exc}")
        traceback.print_exc()
    finally:
        # Always compute duration, even on failure.
        duration = time.perf_counter() - t0

    # Build a summary dict that mirrors what the scheduler would store.
    result = {
        "status": status,  # 'completed' or 'failed'
        "duration_s": round(duration, 2),  # wall-clock seconds
        "info": getattr(instance, "info", ""),  # markdown summary from the task
        "output_files": getattr(
            instance, "output_files", []
        ),  # list of files written
        "error": error,  # empty string on success
    }
    logger(
        f"apero_sync: {task_key} finished in {duration:.1f}s "
        f"with status={status}."
    )
    return result


def list_tasks() -> Dict[str, Dict[str, Any]]:
    """Return metadata for all registered tasks.

    Returns
    -------
    dict
        Mapping of task_key → {type, param_list, frequency, enabled,
        multi_process, import_error}.
    """
    from apero_ri import tasks as tm

    out: Dict[str, Dict[str, Any]] = {}
    # Walk every registered task and collect its metadata from the
    # parallel registry dicts (TYPE, P_LIST, FREQ, etc.).
    for key in tm.TASK_LIST:
        out[key] = {
            # 'INSTRUMENT' or 'GENERAL' – whether the task runs per-
            # instrument or once globally.
            "type": tm.TYPE.get(key, "INSTRUMENT"),
            # List of param keys the task expects in its run_job dict.
            "param_list": tm.P_LIST.get(key, []),
            # Default run frequency in hours (used by the scheduler).
            "frequency": tm.FREQ.get(key, 24.0),
            # Whether the scheduler would run this task automatically.
            "enabled": tm.ENABLED.get(key, False),
            # Whether the task supports multiprocessing internally.
            "multi_process": tm.MULTI_PROCESS.get(key, False),
            # Whether this task is allowed for local sync/copy workflows.
            "local_task": tm.LOCAL_TASK.get(key, False),
            # Non-empty string if the task module failed to import.
            "import_error": (tm.IMPORT_ERRORS or {}).get(key, ""),
        }
    return out


def local_task_keys() -> List[str]:
    """Return task keys that are LOCAL_TASK-enabled."""
    from apero_ri import tasks as tm

    return sorted(
        [
            key
            for key in tm.TASK_LIST.keys()
            if bool(tm.LOCAL_TASK.get(key, False))
        ]
    )


def run_for_profile(
    task_key: str,
    profile_yaml: str,
    *,
    local_data_dir: str = "",
    instrument: str = "",
    task_config: Optional[Dict[str, Any]] = None,
    verbose: bool = True,
    log_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience wrapper that loads a single APERO profile YAML file.

    Parameters
    ----------
    task_key : str
        Task registry key.
    profile_yaml : str
        Path to a YAML file containing one profile's config (the same
        structure stored in ``apero_profiles.yaml`` under an instrument →
        profile-name key).
    local_data_dir : str
        Where output files are written.  Defaults to ``~/.ari``.
    instrument : str
        Instrument name.  Falls back to ``general.INSTRUMENT`` in the
        profile YAML.
    task_config : dict, optional
        Extra task config (force_run, ncores, etc.).
    verbose : bool
        Print progress to stdout.
    log_file : str, optional
        Also log to this file.

    Returns
    -------
    dict
        Same as ``run()``.
    """
    import yaml

    # Resolve the profile YAML to an absolute path (handles ~ and symlinks).
    profile_path = Path(profile_yaml).expanduser().resolve()
    # Load the YAML file – expected to be a single dict with database,
    # general, paths, sci-headers sub-keys (same structure as one entry
    # inside apero_profiles.yaml).
    with profile_path.open("r", encoding="utf-8") as fh:
        profile_data = yaml.safe_load(fh) or {}
    if not isinstance(profile_data, dict):
        raise ValueError(
            f"Profile YAML must be a dict, got {type(profile_data).__name__}"
        )

    # Use the filename stem (e.g. 'my_profile' from 'my_profile.yaml')
    # as the profile name.  This matches how the server identifies profiles.
    profile_name = profile_path.stem
    # Fall back to the instrument name inside the profile if not supplied
    # by the caller.
    if not instrument:
        instrument = (
            profile_data.get("general", {}).get("INSTRUMENT", "")
            or profile_data.get("INSTRUMENT", "")
            or "unknown"
        )
    # Default output directory is ~/.ari, matching the server convention.
    if not local_data_dir:
        local_data_dir = str(Path.home() / ".ari")

    # Build the full params dict that run() expects, wrapping the single
    # profile in the same structure the server builds from
    # apero_profiles.yaml.
    params = {
        "LOCAL_DATA_DIR": local_data_dir,
        "INSTRUMENT": instrument,
        "APERO_PROFILES": {profile_name: profile_data},
        "APERO_PROFILE_NAMES": [profile_name],
        "TASK_CONFIG": dict(task_config or {}),
    }
    # Delegate to the main run() function with the assembled params.
    return run(task_key, params, verbose=verbose, log_file=log_file)


# =============================================================================
# Private helpers
# =============================================================================
def _build_logger(verbose: bool, log_file: Optional[str] = None):
    """Return a logging callable for TASK_LOGGER injection.

    The returned function accepts a single string message and prints it
    with a UTC timestamp.  This replaces the server's web-based logging
    (tlog / TASK_LOGGER) so that tasks produce identical output whether
    run by the scheduler or locally via apero_sync.
    """
    # Convert the log file string to a Path (or None) once up front,
    # avoiding repeated Path construction on every log call.
    log_path = Path(log_file) if log_file else None
    if log_path:
        # Ensure the parent directory exists so the first .open('a') works.
        log_path.parent.mkdir(parents=True, exist_ok=True)

    def _log(message: str) -> None:
        # UTC timestamp prefix for reproducible, timezone-independent logs.
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        line = f"{stamp} | {message}"
        # Print to stdout if verbose mode is on.
        if verbose:
            print(line, flush=True)
        # Append to the log file if one was requested.  Silently ignore
        # write failures (e.g. disk full) to avoid crashing the task.
        if log_path:
            try:
                with log_path.open("a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            except Exception:
                pass

    return _log


# =============================================================================
# CLI entry point
# =============================================================================
def _cli_main(argv: Optional[List[str]] = None) -> None:
    """
    Minimal CLI:

    ``python -m apero_ri.tasks.apero_sync TASK_KEY params.yaml``.

    """
    import argparse

    import yaml

    # Build a minimal argument parser.  Only two positional args are
    # required: the task key and a YAML file containing the run params.
    parser = argparse.ArgumentParser(
        description="Run a LOCAL_TASK APERO RI task locally.",
    )
    parser.add_argument(
        "--list-local-tasks",
        action="store_true",
        help="List task keys that support LOCAL_TASK local execution and exit.",
    )
    # Positional: which task to run (e.g. 'APERO_OBJECT_QUERY').
    parser.add_argument("task_key", nargs="?", help="Task key from TASK_LIST.")
    # Positional: path to a YAML file whose top-level dict is the params
    # dict passed to run_job (LOCAL_DATA_DIR, APERO_PROFILES, etc.).
    parser.add_argument(
        "params_yaml",
        nargs="?",
        help="Path to a YAML file containing the run params dict.",
    )
    # Optional: write timestamped log lines to this file as well.
    parser.add_argument(
        "--log",
        default=None,
        help="Optional log file path.",
    )
    # Optional: suppress stdout output (log file still written if given).
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout progress messages.",
    )
    args = parser.parse_args(argv)

    if args.list_local_tasks:
        keys = local_task_keys()
        if not keys:
            print("No LOCAL_TASK-enabled tasks found.")
        else:
            print("LOCAL_TASK-enabled tasks:")
            for key in keys:
                print(f"- {key}")
        return

    if not args.task_key or not args.params_yaml:
        parser.error(
            "task_key and params_yaml are required unless "
            "--list-local-tasks is used"
        )

    # Load the params YAML file.  Must be a top-level dict.
    with open(args.params_yaml, "r", encoding="utf-8") as fh:
        params = yaml.safe_load(fh) or {}
    if not isinstance(params, dict):
        print(f"ERROR: params YAML must be a dict.", file=sys.stderr)
        sys.exit(1)

    # Delegate to run() with the parsed arguments.
    result = run(
        args.task_key, params, verbose=not args.quiet, log_file=args.log
    )

    # Exit with a non-zero code on failure so callers (e.g. cron, CI)
    # can detect errors.
    if result["status"] != "completed":
        print(f'\nTask failed: {result.get("error", "")}', file=sys.stderr)
        sys.exit(1)
    # On success, print a short summary of how many files were generated.
    print(f'\nDone. Output files: {len(result["output_files"])}')


if __name__ == "__main__":
    _cli_main()
