#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

"""
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.apero_observation_table'
ARI_DIR = Path.home() / '.ari'

# list of parameters needed for this task (for checking in run_job)
PARAM_LIST = []
PARAM_LIST.append('LOCAL_DATA_DIR')
PARAM_LIST.append('INSTRUMENT')
PARAM_LIST.append('APERO_PROFILES')
PARAM_LIST.append('APERO_PROFILE_NAMES')
# Profile params are hydrated dynamically from APERO profiles + instrument
# preset.
APERO_PROFILE_PARAM_LIST = []
# Set the default frequency for this task (in hours)
DEFAULT_FREQUENCY = 6.0
# Set whether this task is enabled by default in the admin portal
DEFAULT_ENABLED = True
# Set the type of task (INSTRUMENT, GLOBAL)
TASK_TYPE = 'INSTRUMENT'
# Whether this task has a sub-process (for sub-processing loading bar in UI)
USE_SUBPROCESS = False
# Whether this task can be run in multi-process mode 
# (if False, will always run in main process)
MULTI_PROCESS = False


# =============================================================================
# Define classes
# =============================================================================
class AperoObservationTableTask(apero_async.AperoAsyncTask):
    """Class representing an asynchronous task in APERO RI."""
    def __init__(self, status='pending'):
        name = 'APERO Observation Table Task'
        description = ('Generate the observation table for the '
                       'APERO reduction interface for each apero profile.')
        super().__init__(name, description, status)
        

    def run_job(self, params: Dict[str, Any]):
        """
        Create a file that can be used to populate the observation table in the 
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
        self.info = ''
        # get apero profiles:
        apero_profile_names = params['APERO_PROFILE_NAMES']
        apero_profiles = params['APERO_PROFILES']
        task_config = params.get('TASK_CONFIG', {})
        force_run = bool(task_config.get('force_run', False))
        task_logger = params.get('TASK_LOGGER')
        stop_event = params.get('STOP_EVENT')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        tlog('APERO_OBSERVATION_TABLE start.')
        tlog(f'Configured APERO profiles: {len(apero_profile_names)}')
        
        # Check if there are any profiles configured
        if not apero_profile_names:
            self.info = 'No APERO profiles configured.'
            tlog('No APERO profiles configured. Nothing to do.')
            return
        
        for a_it, apero_profile in enumerate(apero_profile_names):
            if stop_event is not None and stop_event.is_set():
                tlog('Cancellation requested. Exiting before next profile.')
                return
            # update the progress
            self.progress = (a_it + 1) / len(apero_profile_names)
            tlog(f'Profile {a_it + 1}/{len(apero_profile_names)}: {apero_profile}')
            # -----------------------------------------------------------------
            # get parameters for this apero profile
            aparams = apero_profiles[apero_profile]
            instrument = str(params.get('INSTRUMENT')
                             or aparams.get('general', {}).get('INSTRUMENT')
                             or 'unknown')
            db_updates = {}
            try:
                should_skip, db_updates, skip_reason = (
                    apero_async.should_skip_profile_query(
                        aparams, force_run=force_run
                    )
                )
            except Exception as exc:
                should_skip = False
                skip_reason = f'Database update-time check unavailable: {exc}'
            if should_skip:
                tlog(f'Profile {apero_profile}: skipped. {skip_reason}')
                self.info += (
                    f'\n## Observation Table for APERO Profile: {apero_profile}\n\n'
                    f'- Skipped query run. {skip_reason}\n'
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
            tlog(f'Profile {apero_profile}: running database query for observation table...')
            results = apero_async.database_query(db_params, rquery)
            tlog(
                f'Profile {apero_profile}: query complete with {len(results)} rows '
                f'in {time.time() - start:.2f}s.'
            )
            if stop_event is not None and stop_event.is_set():
                tlog(f'Profile {apero_profile}: cancellation requested after query. Exiting.')
                return
            # -----------------------------------------------------------------
            # time now
            time_now = datetime.now(timezone.utc).isoformat()
            metadata = dict()
            metadata['GENERATED_AT'] = time_now
            metadata['QUERY_TIME'] = time.time() - start
            metadata['APERO_PROFILE'] = apero_profile
            metadata['COLUMN_META'] = meta_columns()
            # construct filename
            instrument = (
                aparams.get('general', {}).get('INSTRUMENT', 'unknown')
            )
            local_dir = (Path(params.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                         / 'tasks' / instrument / apero_profile)
            basename = 'obs_table.json'
            filename =  local_dir / basename
            # save results to JSON file for use in the UI
            apero_async.save_results(filename, results, metadata)
            tlog(f'Profile {apero_profile}: saved observation table to {filename}.')
            if db_updates:
                try:
                    tlog(f'Profile {apero_profile}: persisting DB update fingerprint.')
                    apero_async.save_profile_db_table_updates(
                        instrument, apero_profile, db_updates
                    )
                except Exception as exc:
                    tlog(
                        f'Profile {apero_profile}: warning, failed to persist '
                        f'database-update fingerprint: {exc}'
                    )
                    self.info += (
                        f'\n- Warning: failed to persist database-update '
                        f'fingerprint for {apero_profile}: {exc}\n'
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

        tlog('APERO_OBSERVATION_TABLE completed.')
    
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
        apero_profile_names = params['APERO_PROFILE_NAMES']
        apero_profiles = params['APERO_PROFILES']
        
        # Check if there are any profiles configured
        if not apero_profile_names:
            self.info = 'No APERO profiles configured.'
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
def check_required(aparams: Dict[str, Any]) -> Dict[str, Any]:
    required_params = [
        'ASTROM_TABLENAME',
        'CALIB_TABLENAME',
        'FINDEX_TABLENAME',
        'LOG_TABLENAME',
        'TELLU_TABLENAME',
        'REJECT_TABLENAME',
    ]
    # Check and cut down parameters needed for query
    rparams = dict()
    # Prefer nested database config and flatten required keys for SQL
    # templates.
    db_cfg = aparams.get('database', {})
    if not isinstance(db_cfg, dict):
        db_cfg = {}
    # loop around parameters
    for param in required_params:
        value = db_cfg.get(param, aparams.get(param))
        if value in (None, ''):
            raise ValueError(f'Missing required parameter: database.{param}')
        rparams[param] = value
    # extract science params from the 'general' sub-dict and flatten into
    # rparams
    general = aparams.get('general', {})
    for key in ('SCIENCE_FIBER', 'SCIENCE_TYPES'):
        if key not in general:
            raise ValueError(f'Missing required parameter: general.{key}')
        rparams[key] = general[key]
    return rparams


def sub_commands(rparams):
    # ---------------------------------------------------------------------
    # get parameters only needed for sub-commands
    fiber = f'\"{rparams["SCIENCE_FIBER"]}\"'
    scitypes = ','.join([f'"{t}"' for t in rparams['SCIENCE_TYPES']])
    # ---------------------------------------------------------------------
    # specific sub-commands to add to rparams (shorthand)
    # ---------------------------------------------------------------------
    # get all unique run_ids for the object (for filtering in the UI)
    all_run_ids = ('GROUP_CONCAT(DISTINCT KW_RUN_ID SEPARATOR ", ")'
                f' AS ALL_RUN_IDS')
    # sum all files in raw
    raw_files = ('SUM(BLOCK_KIND = "raw"'
                f' AND KW_DPRTYPE IN ({scitypes}))'
                f' AS raw_files')
    # sum all files in red with output EXT_E2DS_FF (science fiber)
    red_files = ('SUM(BLOCK_KIND = "red"'
                f' AND KW_OUTPUT = "EXT_E2DS_FF"'
                f' AND KW_FIBER = {fiber}'
                f' AND KW_DPRTYPE IN ({scitypes}))'
                f' AS red_files')
    # sum all files in red with output TELLU_OBJ
    tcorr_files = ('SUM(BLOCK_KIND = "red"'
                f' AND KW_OUTPUT = "TELLU_OBJ"'
                f' AND KW_FIBER = {fiber}'
                f' AND KW_DPRTYPE IN ({scitypes}))'
                f' AS tcorr_files')
    # push sub-commands into rparams
    rparams['ALL_RUN_IDS'] = all_run_ids
    rparams['RAW_FILES'] = raw_files
    rparams['RED_FILES'] = red_files
    rparams['TCORR_FILES'] = tcorr_files
    # return the updated rparams
    return rparams


def construct_query(rparams):
    # construct the SQL query
    query = """
    SELECT
        findex.OBS_DIR AS NIGHT,
        findex.KW_OBJNAME AS OBJNAME,
        findex.ALL_RUN_IDS AS RUN_ID,
        findex.raw_files AS `raw files`,
        findex.red_files AS `ext files`,
        findex.tcorr_files AS `tcorr files`
    FROM (
        SELECT
            OBS_DIR,
            KW_OBJNAME,
            {ALL_RUN_IDS},
            {RAW_FILES},
            {RED_FILES},
            {TCORR_FILES}
        FROM {FINDEX_TABLENAME}

        GROUP BY OBS_DIR, KW_OBJNAME
        HAVING raw_files > 0
    ) AS findex
    JOIN {ASTROM_TABLENAME} astrom
        ON findex.KW_OBJNAME = astrom.OBJNAME
    ORDER BY findex.OBS_DIR DESC;
    """
    # ---------------------------------------------------------------------
    # format the query with rparams
    rquery = query.format(**rparams)
    return rquery


def meta_columns():
    cols = dict()
    # Night
    cols['NIGHT'] = dict()
    cols['NIGHT']['sortable'] = True
    cols['NIGHT']['filterable'] = True
    cols['NIGHT']['removable'] = False
    cols['NIGHT']['default'] = True
    cols['NIGHT']['type'] = 'night'
    # Object name
    cols['OBJNAME'] = dict()
    cols['OBJNAME']['sortable'] = True
    cols['OBJNAME']['filterable'] = True
    cols['OBJNAME']['removable'] = False
    cols['OBJNAME']['default'] = True
    cols['OBJNAME']['type'] = 'string'
    # RUN_ID
    cols['RUN_ID'] = dict()
    cols['RUN_ID']['sortable'] = False
    cols['RUN_ID']['filterable'] = False
    cols['RUN_ID']['removable'] = False
    cols['RUN_ID']['default'] = False
    cols['RUN_ID']['type'] = 'string'
    # raw files
    cols['raw files'] = dict()
    cols['raw files']['sortable'] = False
    cols['raw files']['filterable'] = True
    cols['raw files']['removable'] = True
    cols['raw files']['default'] = True
    cols['raw files']['type'] = 'number'
    # ext files
    cols['ext files'] = dict()
    cols['ext files']['sortable'] = False
    cols['ext files']['filterable'] = True
    cols['ext files']['removable'] = True
    cols['ext files']['default'] = True
    cols['ext files']['type'] = 'number'
    # tcorr files
    cols['tcorr files'] = dict()
    cols['tcorr files']['sortable'] = False
    cols['tcorr files']['filterable'] = True
    cols['tcorr files']['removable'] = True
    cols['tcorr files']['default'] = True
    cols['tcorr files']['type'] = 'number'
    # -------------------------------------------------------------------------
    # return the column meta data
    return cols


# =============================================================================
# Start of main code
# =============================================================================
if __name__ == '__main__':
    from apero_ri.core.auth import load_apero_profiles
    # -- Configure which profile to test with --
    _TEST_INSTRUMENT = 'SPIROU'
    _TEST_PROFILE = 'spirou_xxs_08_cook_home'

    # Load profiles from ~/.ari/admin/apero_profiles.yaml
    _all_profiles = load_apero_profiles()
    _inst_profiles = _all_profiles.get(_TEST_INSTRUMENT, {})
    if _TEST_PROFILE not in _inst_profiles:
        raise RuntimeError(
            f'Profile "{_TEST_PROFILE}" not found under instrument '
            f'"{_TEST_INSTRUMENT}" in apero_profiles.yaml'
        )
    _profile = _inst_profiles[_TEST_PROFILE]

    task = AperoObservationTableTask()
    run_params = {
        'LOCAL_DATA_DIR': str(ARI_DIR),
        'INSTRUMENT': _TEST_INSTRUMENT.lower(),
        'APERO_PROFILE_NAMES': [_TEST_PROFILE],
        'APERO_PROFILES': {_TEST_PROFILE: _profile},
    }
    task.test_query(run_params)

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
