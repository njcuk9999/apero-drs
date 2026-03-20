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
ARI_DIR = Path.home() / '.ari'

# list of parameters needed for this task (for checking in run_job)
PARAM_LIST = []
PARAM_LIST.append('LOCAL_DATA_DIR')
PARAM_LIST.append('INSTRUMENT')
PARAM_LIST.append('APERO_PROFILES')
PARAM_LIST.append('APERO_PROFILE_NAMES')
# list of apero profile parameters needed for this task (for checking in run_job)
APERO_PROFILE_PARAM_LIST = []
APERO_PROFILE_PARAM_LIST.append('DATABASE_MODE')
APERO_PROFILE_PARAM_LIST.append('DATABASE_HOST')
APERO_PROFILE_PARAM_LIST.append('DATABASE_USER')
APERO_PROFILE_PARAM_LIST.append('DATABASE_PASSWORD')
APERO_PROFILE_PARAM_LIST.append('DATABASE_NAME')
APERO_PROFILE_PARAM_LIST.append('ASTROM_TABLENAME')
APERO_PROFILE_PARAM_LIST.append('CALIB_TABLENAME')
APERO_PROFILE_PARAM_LIST.append('FINDEX_TABLENAME')
APERO_PROFILE_PARAM_LIST.append('LOG_TABLENAME')
APERO_PROFILE_PARAM_LIST.append('TELLU_TABLENAME')
APERO_PROFILE_PARAM_LIST.append('REJECT_TABLENAME')
APERO_PROFILE_PARAM_LIST.append('SCIENCE_FIBER')
APERO_PROFILE_PARAM_LIST.append('SCIENCE_TYPES')
# Set the default frequency for this task (in hours)
DEFAULT_FREQUENCY = 1.0
# Set whether this task is enabled by default in the admin portal
DEFAULT_ENABLED = True
# Set the type of task (INSTRUMENT, GLOBAL)
TASK_TYPE = 'INSTRUMENT'


# =============================================================================
# Define global classes
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
        - ASTROM_TABLENAME: str, the name of the table containing astrometric data
        - CALIB_TABLENAME: str, the name of the table containing calibration data
        - FINDEX_TABLENAME: str, the name of the table containing file index data
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
            # ---------------------------------------------------------------------
            # specific sub-commands to add to rparams (shorthand)
            # ---------------------------------------------------------------------
            rparams = sub_commands(rparams)
            # ----------------------------------------------------------------------
            rquery = construct_query(rparams)
            # ---------------------------------------------------------------------
            # run the query and get results
            # Map DATABASE_USERNAME -> DATABASE_USER for database_query
            db_params = dict(aparams)
            if 'DATABASE_USERNAME' in db_params and 'DATABASE_USER' not in db_params:
                db_params['DATABASE_USER'] = db_params['DATABASE_USERNAME']
            start = time.time()
            results = apero_async.database_query(db_params, rquery)
            # ---------------------------------------------------------------------
            # time now
            time_now = datetime.now(timezone.utc).isoformat()
            metadata = dict()
            metadata['GENERATED_AT'] = time_now
            metadata['QUERY_TIME'] = time.time() - start
            metadata['APERO_PROFILE'] = apero_profile
            metadata['COLUMN_META'] = meta_columns()
            # construct filename
            instrument = params.get('INSTRUMENT', 'unknown')
            local_dir = (Path(params.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                         / 'tasks' / instrument / apero_profile)
            basename = 'obs_table.json'
            filename =  local_dir / basename
            # save results to JSON file for use in the UI
            apero_async.save_results(filename, results, metadata)
            # ---------------------------------------------------------------------
            # update the info markdown with meta data
            self.info += f"""
            ## Object Table for APERO Profile: {apero_profile}
            
            **Generated at**: {metadata['GENERATED_AT']}  
            **Query time**: {metadata['QUERY_TIME']:.2f} seconds
            **APERO Profile**: {metadata['APERO_PROFILE']}
            """
            # ---------------------------------------------------------------------
            # add to the output files for this task
            self.output_files.append(str(filename))
            # update the last run time
            self.last_run = time_now
    
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
        - ASTROM_TABLENAME: str, the name of the table containing astrometric data
        - CALIB_TABLENAME: str, the name of the table containing calibration data
        - FINDEX_TABLENAME: str, the name of the table containing file index data
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
            # ---------------------------------------------------------------------
            # specific sub-commands to add to rparams (shorthand)
            # ---------------------------------------------------------------------
            rparams = sub_commands(rparams)
            # ----------------------------------------------------------------------
            rquery = construct_query(rparams)  
            # ----------------------------------------------------------------------
            print(rquery.format(**rparams)) 
            

def check_required(aparams: Dict[str, Any]) -> Dict[str, Any]:
    required_params = [
        'ASTROM_TABLENAME',
        'CALIB_TABLENAME',
        'FINDEX_TABLENAME',
        'LOG_TABLENAME',
        'TELLU_TABLENAME',
        'REJECT_TABLENAME',
        'SCIENCE_FIBER',
        'SCIENCE_TYPES',
    ]
    # Check and cut down parameters needed for query
    rparams = dict()
    # loop around parmaeters
    for param in required_params:
        if param not in aparams:
            raise ValueError(f'Missing required parameter: {param}')
        else:
            rparams[param] = aparams[param]
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
    # prompt for database password
    import getpass
    db_password = getpass.getpass('Enter database password: ')
    # create an instance of the task and run it with test parameters
    task = AperoObjectTableTask()
    test_params = {
        'LOCAL_DATA_DIR': str(ARI_DIR),
        'INSTRUMENT': 'spirou',
        'APERO_PROFILE_NAMES': ['default'],
        'APERO_PROFILES': {
            'default': {
                'DATABASE_MODE': 'mysql+pymysql',
                'DATABASE_HOST': 'cosmos.astro.umontreal.ca',
                'DATABASE_USER': 'spirou',
                'DATABASE_PASSWORD': f'{db_password}!',
                'DATABASE_NAME': 'spirou',
                'ASTROM_TABLENAME': 'astrom_spirou_offline_db',
                'CALIB_TABLENAME': 'calib_spirou_offline_db',
                'FINDEX_TABLENAME': 'findex_spirou_offline_db',
                'LOG_TABLENAME': 'log_spirou_offline_db',
                'TELLU_TABLENAME': 'tellu_spirou_offline_db',
                'REJECT_TABLENAME': 'reject_spirou_offline_db',
                'SCIENCE_FIBER': 'AB',
                'SCIENCE_TYPES': ['POLAR_FP', 'POLAR_DARK', 'OBJ_DARK', 'OBJ_FP']
            }
        }
    }
    task.test_query(test_params)