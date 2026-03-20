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
class AperoObjectQueryTask(apero_async.AperoAsyncTask):
    """Class representing an asynchronous task in APERO RI."""
    def __init__(self, status='pending'):
        name = 'APERO Object Query Task'
        description = ('Generate the object query for the '
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
        
        # loop around apero profiles
        for a_it, apero_profile in enumerate(apero_profile_names):
            
            # -----------------------------------------------------------------
            # get parameters for this apero profile
            aparams = apero_profiles[apero_profile]
             # -----------------------------------------------------------------
            # Map DATABASE_USERNAME -> DATABASE_USER for database_query
            db_params = dict(aparams)
            if 'DATABASE_USERNAME' in db_params and 'DATABASE_USER' not in db_params:
                db_params['DATABASE_USER'] = db_params['DATABASE_USERNAME']
            # -----------------------------------------------------------------
            # define the object name query
            obj_query = "SELECT DISTINCT KW_OBJNAME FROM {FINDEX_TABLENAME}"
            obj_query = obj_query.format(FINDEX_TABLENAME=aparams['FINDEX_TABLENAME'])
            # first lets get a list of objects from the astrometric database
            start = time.time()
            objlist = apero_async.database_query(db_params, obj_query)
            # get the number of objects
            self.info += f'Found {len(objlist)} unique objects in the database '
            self.info += f'for APERO profile: {apero_profile}\n'
            self.info += f'Object query time: {time.time() - start:.2f} seconds\n'
            # ----------------------------------------------------------------
            # storage of timings per object
            timing_per_obj = []
            # storage of output file names
            output_files = []
            # -----------------------------------------------------------------
            for o_it, objname in enumerate(objlist):
                # start time
                start = time.time()
                # update the progress (combination of apero_profile + object)
                part1 = (o_it + 1) / len(objlist)
                part2 = (a_it + 1) / len(apero_profile_names)
                self.progress = part1 * part2

                # -------------------------------------------------------------
                # Step 2: Query the databases for the object and get all 
                #         information
                # -------------------------------------------------------------
                # returns an object table (on row per parameter)
                # return a file table (one row per observation)
                obj_ftables = object_query_db(aparams, objname)
                
                # -------------------------------------------------------------
                # Step 2: Get header keys for all files for this object
                # -------------------------------------------------------------
                # returns a header table (one row per observation)
                # obj_htable = object_query_headers(obj_ftable)


            # -----------------------------------------------------------------
            # get average query time
            ave_query_time = sum(timing_per_obj) / len(timing_per_obj)
            # update the info markdown with meta data
            self.info += f"""
            ## Object Query for APERO Profile: {apero_profile}
            
            - Queried {len(timing_per_obj)} objects
            - Average query time per object: {ave_query_time:.2f} seconds 
            - Total query time: {sum(timing_per_obj):.2f} seconds
            """
            # -----------------------------------------------------------------
            # add to the output files for this task
            self.output_files += output_files
            # update the last run time
            self.last_run = datetime.now(timezone.utc).isoformat()
    
    def test_query(self, params: Dict[str, Any], objnames: str):
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
            # -----------------------------------------------------------------
            # get parameters for this apero profile
            aparams = apero_profiles[apero_profile]
             # -----------------------------------------------------------------
            # Map DATABASE_USERNAME -> DATABASE_USER for database_query
            db_params = dict(aparams)
            if 'DATABASE_USERNAME' in db_params and 'DATABASE_USER' not in db_params:
                db_params['DATABASE_USER'] = db_params['DATABASE_USERNAME']
            # -----------------------------------------------------------------
            # define the object name query
            obj_query = "SELECT DISTINCT KW_OBJNAME FROM {FINDEX_TABLENAME}"
            obj_query = obj_query.format(FINDEX_TABLENAME=aparams['FINDEX_TABLENAME'])
            
            print(f'Object name query for APERO profile: {apero_profile}\n')
            print(obj_query)
            print('\n\n')
            # ----------------------------------------------------------------
            # storage of timings per object
            timing_per_obj = []
            # storage of output file names
            output_files = []
            
            objlist = objnames.split(',')
            # -----------------------------------------------------------------
            for o_it, objname in enumerate(objlist):
                # start time
                start = time.time()
                # update the progress (combination of apero_profile + object)
                part1 = (o_it + 1) / len(objlist)
                part2 = (a_it + 1) / len(apero_profile_names)
                self.progress = part1 * part2

                # -------------------------------------------------------------
                # Step 2: Query the databases for the object and get all 
                #         information
                # -------------------------------------------------------------
                # returns an object table (on row per parameter)
                # return a file table (one row per observation)
                obj_ftables = object_query_db(aparams, objname, 
                                              return_query=True)
                

def file_col_query(aparams, rparams, objname, fkind, block_kind: str,
                   fiber: str = None, scitype: str = None, 
                   output:  str = None, return_query: bool = False):
    # deal with optional conditions
    condition = [f"fdb.BLOCK_KIND = '{block_kind}'"]
    if fiber is not None:
        condition.append(f"fdb.KW_FIBER = '{fiber}'")
    if scitype is not None:
        scitype_list = ', '.join([f"'{t}'" for t in rparams['SCIENCE_TYPES']])
        condition.append(f"fdb.KW_DPRTYPE IN ({scitype_list})")
    if output is not None:
        condition.append(f"fdb.KW_OUTPUT = '{output}'")
    # construct the query
    query = """
    SELECT
        fdb.BLOCK_KIND AS BLOCK_KIND,
        fdb.OBS_DIR AS OBS_DIR,
        fdb.FILENAME AS FILENAME,
        fdb.KW_RUN_ID AS KW_RUN_ID,
        fdb.KW_PI_NAME AS KW_PI_NAME,
        FROM_UNIXTIME((fdb.KW_MID_OBS_TIME - 40587) * 86400) AS MID_OBS_TIME,
        FROM_UNIXTIME(fdb.LAST_MODIFIED) AS LAST_MODIFIED,
        fdb.KW_PID AS PID,
        ldb.PASSED_ALL_QC AS PASSED_ALL_QC
    FROM {FINDEX_TABLENAME} fdb
    LEFT JOIN {LOG_TABLENAME} ldb
            ON fdb.KW_PID = ldb.PID
    WHERE fdb.KW_OBJNAME = '{OBJNAME}' AND {CONDITION}
    """
    # construct the formatted query
    rquery =  query.format(OBJNAME=objname, CONDITION=' AND '.join(condition),
                           **rparams)
    # deal with just returning the query for testing
    if return_query:
        return rquery
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
    # construct filename
    instrument = params.get('INSTRUMENT', 'unknown')
    local_dir = (Path(params.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                / 'tasks'  / instrument / apero_profile_name / 'objects')
    basename = f'ftable_{fkind}_{objname}.json'
    filename =  local_dir / basename
    # save results to JSON file for use in the UI
    apero_async.save_results(filename, results, metadata)
    # store timing for this object
    timing_per_obj.append(metadata['QUERY_TIME'])
    # -------------------------------------------------------------------------
    # return the json results
    return results
 

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

def sub_commands(rparams):

    # get parameters only needed for sub-commands
    fiber = f'"{rparams["SCIENCE_FIBER"]}"'
    scitypes = ','.join([f'"{t}"' for t in rparams['SCIENCE_TYPES']])
    return rparams
    

def object_query_db(aparams, objname, return_query: bool = False):
    
    # check that all required parameters are present
    rparams = check_required(aparams)
    # specific sub-commands to add to rparams (shorthand)
    rparams = sub_commands(rparams)
    
    
    # get parameters only needed for sub-commands
    fiber = f'"{rparams["SCIENCE_FIBER"]}"'
    scitypes = ','.join([f'"{t}"' for t in rparams['SCIENCE_TYPES']])
    # storage of queries
    queries = dict()
    # raw file table
    raw_results = file_col_query(aparams, rparams, objname,
                                 fkind='raw', block_kind='raw',
                                 scitype=scitypes, return_query=return_query)
    queries['raw'] = raw_results
    # pp file table
    pp_results = file_col_query(aparams, rparams, objname,
                                fkind='pp', block_kind='tmp',
                                scitype=scitypes, return_query=return_query)
    queries['pp'] = pp_results
    # red file table
    red_results = file_col_query(aparams, rparams, objname,
                                 fkind='red', block_kind='red',
                                 scitype=scitypes, output='EXT_E2DS_FF',
                                 fiber=fiber, return_query=return_query)
    queries['red'] = red_results
    # tcorr file table
    tcorr_results = file_col_query(aparams, rparams, objname,
                                   fkind='tcorr', block_kind='red',
                                   scitype=scitypes, output='TELLU_OBJ',
                                   fiber=fiber, return_query=return_query)
    queries['tcorr'] = tcorr_results
    # ccf file table
    ccf_results = file_col_query(aparams, rparams, objname,
                                 fkind='ccf', block_kind='red',
                                 scitype=scitypes, output='CCF_RV',
                                 fiber=fiber, return_query=return_query)
    queries['ccf'] = ccf_results
    # e.fits file table
    efits_results = file_col_query(aparams, rparams, objname,
                                   fkind='efits', block_kind='out',
                                   scitype=scitypes, output='DRS_POST_E',
                                   fiber=fiber, return_query=return_query)
    queries['efits'] = efits_results
    # t.fits file table
    tfits_results = file_col_query(aparams, rparams, objname,
                                   fkind='tfits', block_kind='out',
                                   scitype=scitypes, output='DRS_POST_T',
                                   fiber=fiber, return_query=return_query)
    queries['tfits'] = tfits_results

    # lbl fits file table
    lbl_results = file_col_query(aparams, rparams, objname,
                                 fkind='lbl', block_kind='lbl',
                                 output='LBL_FITS',
                                 return_query=return_query)
    queries['lbl'] = lbl_results


    if return_query:
        for key, query in queries.items():
            print(f'Query for {key}:\n\n{query}\n\n\n\n')


def object_query_headers(obj_ftable):
    pass



if __name__ == '__main__':
    # prompt for database password
    import getpass
    db_password = getpass.getpass('Enter database password: ')
    # create an instance of the task and run it with test parameters
    task = AperoObjectQueryTask()
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
    task.test_query(test_params, objnames='GL699')