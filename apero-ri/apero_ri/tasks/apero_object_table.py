#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

"""
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List

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
DEFAULT_FREQUENCY = 6.0
# Set whether this task is enabled by default in the admin portal
DEFAULT_ENABLED = True
# Set the type of task (INSTRUMENT, GLOBAL)
TASK_TYPE = 'INSTRUMENT'


# =============================================================================
# Define global classes
# =============================================================================
class AperoObjectTableTask(apero_async.AperoAsyncTask):
    """Class representing an asynchronous task in APERO RI."""
    def __init__(self, status='pending'):
        name = 'APERO Object Table Task'
        description = ('Generate the object table for the '
                       'APERO reduction interface for each apero profile.')
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
            basename = 'object_table.json'
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
               
            
def check_required(aparams) -> Dict[str, Any]:
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
    latest_obs = 'FROM_UNIXTIME((MAX(fdb.KW_MID_OBS_TIME) - 40587) * 86400)'
    latest_mod = 'FROM_UNIXTIME(MAX(fdb.LAST_MODIFIED))'
    
    # Build science type list for WHERE clause
    scitype_list = ', '.join([f"'{t}'" for t in rparams['SCIENCE_TYPES']])
    
    # Push into rparams
    rparams['ALL_DPRTYPES'] = all_dprtypes
    rparams['ALL_RUN_IDS'] = all_run_ids
    rparams['ALL_PI_NAMES'] = all_pi_names
    rparams['LATEST_OBS'] = latest_obs
    rparams['LAST_MODIFIED'] = latest_mod
    rparams['SCIENCE_TYPE_LIST'] = scitype_list
    
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
    # --------------------------------------------------------------------------
    # Object name
    cols['OBJNAME'] = dict(sortable=True,
                           filterable=True,
                           removable=False,
                           default=True,
                           coltype='string',
                           hidden=False)
    # --------------------------------------------------------------------------    
    # astrometric default cols
    colnames = ['RA [Deg]', 'Dec [Deg]', 'Teff [K]', 'SpT']
    coltypes = ['number', 'number', 'number', 'string', 'string']
    for colname, coltype in zip(colnames, coltypes):
        cols[colname] = dict(sortable=False, 
                             filterable=True, 
                             removable=True, 
                             default=True, 
                             coltype=coltype, 
                             hidden=False)
    # --------------------------------------------------------------------------
    # other astromeric (not default)
    astrom_cols = ['RA source', 'Dec source', 'Teff source', 'SpT source',
                   'PMRA [mas/yr]', 'PMRA source', 'PMDE [mas/yr]', 
                   'PMDE source', 'Plx [mas]', 'Plx source', 'RV [km/s]', 
                   'RV source']
    astrom_types = ['string', 'string', 'string', 'string',
                    'number', 'string', 'number', 'string', 'number', 
                    'string', 'number', 'string']
    for colname, coltype in zip(astrom_cols, astrom_types):
        cols[colname] = dict(sortable=False, 
                             filterable=True, 
                             removable=True, 
                             default=False, 
                             coltype=coltype, 
                             hidden=True)
    # -------------------------------------------------------------------------- 
    # dprtype
    cols['DPRTYPE'] = dict(sortable=True,
                           filterable=True,
                           removable=True,
                           default=True,
                           coltype='string',
                           hidden=False)
    # --------------------------------------------------------------------------
    # date cols
    date_colnames = ['latest obs', 'last modified']
    for colname in date_colnames:
        cols[colname] = dict(sortable=True,
                             filterable=True,
                             removable=True,
                             default=True,
                             coltype='date',
                             hidden=False)
    # --------------------------------------------------------------------------
    # hidden cols
    hidden_cols = ['ALIASES', 'RA source', 'Dec source', 
                   'Teff source', 'SpT source',
                   'PMRA source', 'PMDE source', 'Plx source', 'RV source',
                   'ALL_DPRTYPES', 'ALL_RUN_IDS']
    hcoltypes = ['string', 'string', 'string', 'string', 'string', 'string', 
                 'string', 'string', 'string', 'string', 'string']
    for colname, coltype in zip(hidden_cols, hcoltypes):
        cols[colname] = dict(sortable=False,
                             filterable=False,
                             removable=False,
                             default=False,
                             coltype=coltype,
                             hidden=True)
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
# =============================================================================
# End of main code
# =============================================================================