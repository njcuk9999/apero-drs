#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

"""

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.tasks.apero_object_table"
ARI_DIR = Path.home() / ".ari"

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
USE_SUBPROCESS = False
# Whether this task can be run in multi-process mode
# (if False, will always run in main process)
MULTI_PROCESS = False
# Available APERO profile filters.
FILTERS = ["APERO_PROFILE_INCLUDE", "APERO_PROFILE_EXCLUDE"]


# =============================================================================
# Define classes
# =============================================================================
class AperoObjectTableTask(apero_async.AperoAsyncTask):
    """Class representing an asynchronous task in APERO RI."""

    def __init__(self, status="pending"):
        name = "APERO Object Table Task"
        description = (
            "Generate the object table for the "
            "APERO reduction interface for each apero profile."
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]):
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

        :param params: A dictionary of parameters needed to run the job.
        This should include database connection parameters and any other
        necessary information.
        """
        # empty the info
        self.info = ""
        # get apero profiles:
        all_profile_names = list(params["APERO_PROFILE_NAMES"])
        apero_profiles = params["APERO_PROFILES"]
        task_config = params.get("TASK_CONFIG", {})
        filters = apero_async.normalize_filter_map(
            task_config.get("filters", {})
        )
        apero_profile_names = apero_async.filter_profile_names(
            all_profile_names, filters
        )
        profile_note = apero_async.profile_filter_note(
            all_profile_names, apero_profile_names, filters
        )
        force_run = bool(task_config.get("force_run", False))
        task_logger = params.get("TASK_LOGGER")
        stop_event = params.get("STOP_EVENT")

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        tlog("APERO_OBJECT_TABLE start.")
        if profile_note:
            self.info += profile_note + "\n"
            tlog(profile_note)
        tlog(f"Configured APERO profiles: {len(apero_profile_names)}")

        # Check if there are any profiles configured
        if not apero_profile_names:
            self.info = "No APERO profiles configured."
            tlog("No APERO profiles configured. Nothing to do.")
            return

        for a_it, apero_profile in enumerate(apero_profile_names):
            if stop_event is not None and stop_event.is_set():
                tlog("Cancellation requested. Exiting before next profile.")
                return
            # update the progress
            self.progress = (a_it + 1) / len(apero_profile_names)
            tlog(
                f"Profile {a_it + 1}/{len(apero_profile_names)}: "
                f"{apero_profile}"
            )
            # -----------------------------------------------------------------
            # get parameters for this apero profile
            aparams = apero_profiles[apero_profile]
            instrument = str(
                params.get("INSTRUMENT")
                or aparams.get("general", {}).get("INSTRUMENT")
                or "unknown"
            )
            db_updates = {}
            try:
                should_skip, db_updates, skip_reason = (
                    apero_async.should_skip_profile_query(
                        aparams, force_run=force_run
                    )
                )
            except Exception as exc:
                should_skip = False
                skip_reason = f"Database update-time check unavailable: {exc}"
            if should_skip:
                tlog(f"Profile {apero_profile}: skipped. {skip_reason}")
                self.info += (
                    f"\n## Object Table for APERO Profile: {apero_profile}\n\n"
                    f"- Skipped query run. {skip_reason}\n"
                )
                continue

            # check that all required parameters are present
            rparams = check_required(aparams)
            # -----------------------------------------------------------------
            # specific sub-commands to add to rparams (shorthand)
            # -----------------------------------------------------------------
            rparams = sub_commands(rparams)
            # -----------------------------------------------------------------
            rquery = construct_query(rparams)
            # -----------------------------------------------------------------
            # run the query and get results
            db_params = apero_async.get_db_params(aparams)
            start = time.time()
            tlog(
                f"Profile {apero_profile}: running database query "
                "for object table..."
            )
            results = apero_async.database_query(db_params, rquery)
            tlog(
                f"Profile {apero_profile}: query complete with {
                    len(results)} rows " f"in {
                    time.time() -
                    start:.2f}s.")
            if stop_event is not None and stop_event.is_set():
                tlog(
                    f"Profile {apero_profile}: cancellation requested "
                    "after query. Exiting."
                )
                return
            # -----------------------------------------------------------------
            # time now
            time_now = datetime.now(timezone.utc).isoformat()
            metadata = dict()
            metadata["GENERATED_AT"] = time_now
            metadata["QUERY_TIME"] = time.time() - start
            metadata["APERO_PROFILE"] = apero_profile
            metadata["COLUMN_META"] = meta_columns()
            # construct filename
            instrument = aparams.get("general", {}).get("INSTRUMENT", "unknown")
            local_dir = (
                Path(params.get("LOCAL_DATA_DIR", str(ARI_DIR)))
                / "tasks"
                / instrument
                / apero_profile
            )
            basename = "object_table.json"
            filename = local_dir / basename
            # save results to JSON file for use in the UI
            apero_async.save_results(filename, results, metadata)
            tlog(f"Profile {apero_profile}: saved object table to {filename}.")
            if db_updates:
                try:
                    tlog(
                        f"Profile {apero_profile}: persisting DB "
                        "update fingerprint."
                    )
                    apero_async.save_profile_db_table_updates(
                        instrument, apero_profile, db_updates
                    )
                except Exception as exc:
                    tlog(
                        f"Profile {apero_profile}: warning, failed to persist "
                        f"database-update fingerprint: {exc}"
                    )
                    self.info += (
                        f"\n- Warning: failed to persist database-update "
                        f"fingerprint for {apero_profile}: {exc}\n"
                    )
            # -----------------------------------------------------------------
            # update the info markdown with meta data
            self.info += f"""
            ## Object Table for APERO Profile: {apero_profile}

            **Generated at**: {metadata['GENERATED_AT']}
            **Query time**: {metadata['QUERY_TIME']:.2f} seconds
            **APERO Profile**: {metadata['APERO_PROFILE']}
            """
            # -----------------------------------------------------------------
            # add to the output files for this task
            self.output_files.append(str(filename))
            # update the last run time
            self.last_run = time_now

        tlog("APERO_OBJECT_TABLE completed.")

    def test_query(self, params: Dict[str, Any]):
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
            # update the progress
            self.progress = (a_it + 1) / len(apero_profile_names)
            # -----------------------------------------------------------------
            # get parameters for this apero profile
            aparams = apero_profiles[apero_profile]

            # check that all required parameters are present
            rparams = check_required(aparams)
            # -----------------------------------------------------------------
            # specific sub-commands to add to rparams (shorthand)
            # -----------------------------------------------------------------
            rparams = sub_commands(rparams)
            # -----------------------------------------------------------------
            rquery = construct_query(rparams)
            # -----------------------------------------------------------------
            print(rquery.format(**rparams))


# =============================================================================
# Define functions
# =============================================================================
def check_required(aparams) -> Dict[str, Any]:
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


def group_concat(col_in: str, col_out: str):
    # group concat for a column (e.g. to get all unique dprtypes or run_ids)
    return f'GROUP_CONCAT(DISTINCT {col_in} SEPARATOR ", ") AS {col_out}'


def sub_commands(rparams):
    # Build simple aggregation queries for the core columns
    all_dprtypes = 'GROUP_CONCAT(DISTINCT fdb.KW_DPRTYPE SEPARATOR ", ")'
    all_run_ids = 'GROUP_CONCAT(DISTINCT fdb.KW_RUN_ID SEPARATOR ", ")'
    all_pi_names = 'GROUP_CONCAT(DISTINCT fdb.KW_PI_NAME SEPARATOR ", ")'

    # Get last observation and modification times
    latest_obs = "FROM_UNIXTIME((MAX(fdb.KW_MID_OBS_TIME) - 40587) * 86400)"
    latest_mod = "FROM_UNIXTIME(MAX(fdb.LAST_MODIFIED))"

    # Build science type list for WHERE clause
    scitype_list = ", ".join([f"'{t}'" for t in rparams["SCIENCE_TYPES"]])

    # Push into rparams
    rparams["ALL_DPRTYPES"] = all_dprtypes
    rparams["ALL_RUN_IDS"] = all_run_ids
    rparams["ALL_PI_NAMES"] = all_pi_names
    rparams["LATEST_OBS"] = latest_obs
    rparams["LAST_MODIFIED"] = latest_mod
    rparams["SCIENCE_TYPE_LIST"] = scitype_list

    return rparams


def construct_query(rparams):
    # Simple, lean query for object table
    query = """
    SELECT
        findex.KW_OBJNAME AS OBJNAME,
        astrom.ALIASES AS ALIASES,
        astrom.RA_DEG AS `RA [Deg]`,
        astrom.RA_SOURCE AS `RA source`,
        astrom.DEC_DEG AS `Dec [Deg]`,
        astrom.DEC_SOURCE AS `Dec source`,
        astrom.TEFF AS `Teff [K]`,
        astrom.TEFF_SOURCE AS `Teff source`,
        astrom.SP_TYPE AS SpT,
        astrom.SP_SOURCE AS `SpT source`,
        astrom.PMRA AS `PMRA [mas/yr]`,
        astrom.PMRA_SOURCE AS `PMRA source`,
        astrom.PMDE AS `PMDE [mas/yr]`,
        astrom.PMDE_SOURCE AS `PMDE source`,
        astrom.PLX AS `Plx [mas]`,
        astrom.PLX_SOURCE AS `Plx source`,
        astrom.RV AS `RV [km/s]`,
        astrom.RV_SOURCE AS `RV source`,
        astrom.EPOCH AS `EPOCH [JD]`,
        findex.DPRTYPE AS DPRTYPE,
        findex.RUN_ID AS RUN_ID,
        findex.PI_NAMES AS PI_NAMES,
        findex.`last obs` AS `last obs`,
        findex.`last modified` AS `last modified`
    FROM (
        SELECT
            fdb.KW_OBJNAME,
            {ALL_DPRTYPES} AS DPRTYPE,
            {ALL_RUN_IDS} AS RUN_ID,
            {ALL_PI_NAMES} AS PI_NAMES,
            {LATEST_OBS} AS `last obs`,
            {LAST_MODIFIED} AS `last modified`
        FROM {FINDEX_TABLENAME} fdb
        WHERE fdb.BLOCK_KIND IN ('raw', 'tmp', 'red', 'out', 'lbl')
        GROUP BY fdb.KW_OBJNAME
    ) AS findex
    JOIN {ASTROM_TABLENAME} astrom
        ON findex.KW_OBJNAME = astrom.OBJNAME;
    """
    return query.format(**rparams)


def meta_columns():
    cols = dict()
    # -------------------------------------------------------------------------
    # Object name
    cols["OBJNAME"] = dict(
        sortable=True,
        filterable=True,
        removable=False,
        default=True,
        coltype="string",
        hidden=False,
        advanced_search=False,
    )
    # -------------------------------------------------------------------------
    # astrometric default cols
    colnames = ["RA [Deg]", "Dec [Deg]", "Teff [K]", "SpT"]
    coltypes = ["number", "number", "number", "string", "string"]
    asearch = [False, False, True, True]
    for colname, coltype, adv_search in zip(colnames, coltypes, asearch):
        cols[colname] = dict(
            sortable=False,
            filterable=True,
            removable=True,
            default=True,
            coltype=coltype,
            hidden=False,
            advanced_search=adv_search,
        )
    # -------------------------------------------------------------------------
    # other astromeric (not default)
    astrom_cols = [
        "RA source",
        "Dec source",
        "Teff source",
        "SpT source",
        "PMRA [mas/yr]",
        "PMRA source",
        "PMDE [mas/yr]",
        "PMDE source",
        "Plx [mas]",
        "Plx source",
        "RV [km/s]",
        "RV source",
    ]
    astrom_types = [
        "string",
        "string",
        "string",
        "string",
        "number",
        "string",
        "number",
        "string",
        "number",
        "string",
        "number",
        "string",
    ]
    for colname, coltype in zip(astrom_cols, astrom_types):
        cols[colname] = dict(
            sortable=False,
            filterable=True,
            removable=True,
            default=False,
            coltype=coltype,
            hidden=True,
            advanced_search=False,
        )
    # -------------------------------------------------------------------------
    # Run ID (comma-separated list of run IDs per object)
    cols['Run ID'] = dict(
        sortable=True,
        filterable=True,
        removable=True,
        default=False,
        coltype='string',
        hidden=False,
        advanced_search=True,
    )
    # -------------------------------------------------------------------------
    # dprtype
    cols["DPRTYPE"] = dict(
        sortable=True,
        filterable=True,
        removable=True,
        default=True,
        coltype="string",
        hidden=False,
        advanced_search=True,
    )
    # -------------------------------------------------------------------------
    # date cols
    date_colnames = ["latest obs", "last modified"]
    for colname in date_colnames:
        cols[colname] = dict(
            sortable=True,
            filterable=True,
            removable=True,
            default=True,
            coltype="date",
            hidden=False,
            advanced_search=False,
        )
    # -------------------------------------------------------------------------
    # hidden cols
    hidden_cols = [
        "ALIASES",
        "RA source",
        "Dec source",
        "Teff source",
        "SpT source",
        "PMRA source",
        "PMDE source",
        "Plx source",
        "RV source",
        "EPOCH [JD]",
        "ALL_DPRTYPES",
        "PI_NAMES",
    ]
    hcoltypes = [
        "string",
        "string",
        "string",
        "string",
        "string",
        "string",
        "string",
        "string",
        "string",
        "number",
        "string",
        "string",
    ]
    for colname, coltype in zip(hidden_cols, hcoltypes):
        cols[colname] = dict(
            sortable=False,
            filterable=False,
            removable=False,
            default=False,
            coltype=coltype,
            hidden=True,
            advanced_search=False,
        )
    # -------------------------------------------------------------------------
    # return the column meta data
    return cols


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

    task = AperoObjectTableTask()
    run_params = {
        "LOCAL_DATA_DIR": str(ARI_DIR),
        "INSTRUMENT": _TEST_INSTRUMENT.lower(),
        "APERO_PROFILE_NAMES": [_TEST_PROFILE],
        "APERO_PROFILES": {_TEST_PROFILE: _profile},
    }
    task.test_query(run_params)
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
