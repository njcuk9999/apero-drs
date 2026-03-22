#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

"""
import time
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from astropy.io import fits

from apero_ri.base.base import BLOCK_KIND
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
APERO_PROFILE_PARAM_LIST.append('database')
APERO_PROFILE_PARAM_LIST.append('paths')
APERO_PROFILE_PARAM_LIST.append('headers')
APERO_PROFILE_PARAM_LIST.append('plots')
APERO_PROFILE_PARAM_LIST.append('general')
# Set the default frequency for this task (in hours)
DEFAULT_FREQUENCY = 6.0
# Set whether this task is enabled by default in the admin portal
DEFAULT_ENABLED = True
# Set the type of task (INSTRUMENT, GLOBAL)
TASK_TYPE = 'INSTRUMENT'
# BLOCK_KIND is imported from apero_ri.base.base (shared with basket_funcs)


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
            instrument = str(params.get('INSTRUMENT')
                             or aparams.get('general', {}).get('INSTRUMENT')
                             or 'unknown')
            db_updates = {}
            try:
                should_skip, db_updates, skip_reason = (
                    apero_async.should_skip_profile_query(aparams)
                )
            except Exception as exc:
                should_skip = False
                skip_reason = f'Database update-time check unavailable: {exc}'
            if should_skip:
                self.info += (
                    f'\n## Object Query for APERO Profile: {apero_profile}\n\n'
                    f'- Skipped query run. {skip_reason}\n'
                )
                continue
            # -----------------------------------------------------------------
            # define the object name query
            obj_query = _construct_obj_query(aparams)
            # first lets get a list of objects from the astrometric database
            db_params = apero_async.get_db_params(aparams)
            start = time.time()
            objlist = apero_async.database_query(db_params, obj_query)
            # get the number of objects
            self.info += f'Found {len(objlist)} unique objects in the database '
            self.info += f'for APERO profile: {apero_profile}\n'
            self.info += f'Object query time: {time.time() - start:.2f} seconds\n'
            # ----------------------------------------------------------------
            # clear out and lock the object directory
            local_objdir = (Path(aparams.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                            / 'tasks'  / aparams.get('general', {}).get('INSTRUMENT', 'unknown')
                            / apero_profile_names[a_it] / 'objects')
            with _acquire_directory_lock(local_objdir):
                _clear_directory_contents(local_objdir)
            # ----------------------------------------------------------------
            # storage of timings per object
            timing_per_obj = []
            # storage of output file names
            output_files = []
            # -----------------------------------------------------------------
            for o_it, obj_entry in enumerate(objlist):
                # get object name from entries
                objname = obj_entry['KW_OBJNAME']
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
                outputs = object_query_db(aparams, objname,
                                          apero_profile_names[a_it])
                
                # -------------------------------------------------------------
                # Step 2: Get header keys for all files for this object
                # -------------------------------------------------------------
                # returns a header table (one row per observation)
                object_query_headers(aparams, objname,
                                     apero_profile_names[a_it], outputs)
                
                # -------------------------------------------------------------
                # combine the timings from all queries for this object
                timing_per_obj.append(sum(outputs['timings'].values()))


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
            if db_updates:
                try:
                    apero_async.save_profile_db_table_updates(
                        instrument, apero_profile, db_updates
                    )
                except Exception as exc:
                    self.info += (
                        f'\n- Warning: failed to persist database-update '
                        f'fingerprint for {apero_profile}: {exc}\n'
                    )
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
        - INSTRUEMNT: str, the name of the instrument, e.g. 'SPIROU'
        
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
            obj_query = _construct_obj_query(aparams)
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
                # Step 1: Query the databases for the object and get all 
                #         information
                # -------------------------------------------------------------
                # returns an object table (on row per parameter)
                # return a file table (one row per observation)
                outputs = object_query_db(aparams, objname,
                                          apero_profile_names[a_it], 
                                          return_query=True)
                


# =============================================================================
# Define main functions (used in run_job)
# =============================================================================               
def object_query_db(aparams, objname, apero_profile_name, 
                    return_query: bool = False) -> dict[str, Any]:
    if not objname:
        raise ValueError('Object name is empty or invalid.')
    
    # check that all required parameters are present
    rparams = _check_required(aparams)
    
    # get parameters only needed for sub-commands
    fiber = rparams['SCIENCE_FIBER']
    scitypes = rparams['SCIENCE_TYPES']
    # storage of queries
    queries = dict()
    # all files
    all_results = _file_col_query(rparams, objname)
    queries['all'] = all_results
    # raw file table
    raw_results = _file_col_query(rparams, objname,
                                 block_kind='raw', scitype=scitypes)
    queries['raw'] = raw_results
    # pp file table
    pp_results = _file_col_query(rparams, objname, block_kind='tmp',
                                scitype=scitypes)
    queries['pp'] = pp_results
    # red file table
    ext_results = _file_col_query(rparams, objname, block_kind='red',
                                 scitype=scitypes, output='EXT_E2DS_FF',
                                 fiber=fiber)
    queries['ext'] = ext_results
    # tcorr file table
    tcorr_results = _file_col_query(rparams, objname, block_kind='red',
                                   scitype=scitypes, output='TELLU_OBJ',
                                   fiber=fiber)
    queries['tcorr'] = tcorr_results
    # ccf file table
    ccf_results = _file_col_query(rparams, objname, block_kind='red',
                                 scitype=scitypes, output='CCF_RV',
                                 fiber=fiber)
    queries['ccf'] = ccf_results
    # e.fits file table
    efits_results = _file_col_query(rparams, objname, block_kind='out',
                                   output='DRS_POST_E')
    queries['efits'] = efits_results
    # t.fits file table
    tfits_results = _file_col_query(rparams, objname, block_kind='out',
                                   output='DRS_POST_T')
    queries['tfits'] = tfits_results

    # lbl fits file table
    lbl_results = _file_col_query(rparams, objname, block_kind='lbl',
                                 scitype=scitypes, output='LBL_FITS')
    queries['lbl'] = lbl_results

    # lbl rdb file table (one row per science+comparison pair)
    lbl_rdb_results = _file_col_query(rparams, objname, block_kind='lbl',
                                     scitype=None, output='LBL_RDB')
    queries['lbl_rdb'] = lbl_rdb_results

    # storage for timing for database queries
    outputs = dict()
    outputs['queries'] = queries
    outputs['timings'] = dict()
    outputs['results'] = dict()
    # deal with returning just the queries (we print them)
    if return_query:
        for key, query in queries.items():
            print(f'Query for {key}:\n\n{query}\n\n\n\n')
    # deal with running the queries and saving the results
    else:
        # loop around queries and execute them, storing the results in files 
        # for the UI to use
        for key, query in queries.items():
            try:
                outputs = _file_col_cmd(aparams, query, 
                                        apero_profile_name,
                                        objname=objname, fkind=key, 
                                        outputs=outputs)
            except Exception as e:
                # inject a print out of the query for debugging
                emg = f'{key} query: \n{query}\n\nError: {str(e)}'
                raise RuntimeError(emg)
            
    return outputs


def object_query_headers(aparams, objname, apero_profile_name,
                         outputs):

    # get results
    results = outputs['results']
    # output table
    header_dict = dict()
    # start time
    start = time.time()
    # loop around file kinds
    for fkind in results:
        # get entries for this fkind
        entries = results[fkind]
        # get the hkeys for this fkind
        hkeys = aparams['headers'].get(fkind, None)
        # deal with no header keys
        if hkeys is None or len(hkeys) == 0:
            continue
        # loop around each entry
        for entry in entries:
            # get identifier
            identifier = entry['IDENTIFIER']
            # get block kind
            block_kind = BLOCK_KIND.get(entry['BLOCK_KIND'], None)
            # deal with no block kind defined
            if block_kind is None:
                continue
            # deal with first time we see this object
            if identifier not in header_dict:
                header_dict[identifier] = dict(IDENTIFIER=identifier)
            # -----------------------------------------------------------------
            # convert block kind to a path
            block_kind = aparams['paths'][block_kind]
            # construct filename from keys
            abspath = Path(block_kind) / entry['OBS_DIR'] / entry['FILENAME']
            # -----------------------------------------------------------------
            # check if path exists - if it doesn't fill with None
            if not abspath.exists():
                header_dict[identifier] = _fill_dict_null(hkeys)
                continue
            # -----------------------------------------------------------------
            # check if file is fits file
            if abspath.suffix != '.fits':
                header_dict[identifier] = _fill_dict_null(hkeys)
                continue
            # otherwise we open the file
            hdr = fits.getheader(abspath)
            # loop around header key and load into header list
            for hkey in hkeys:
                _hvalue = _get_hdr_key(hdr, hkey, hkeys[hkey])
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
    metadata['GENERATED_AT'] = time_now
    metadata['QUERY_TIME'] = end - start
    metadata['APERO_PROFILE'] = apero_profile_name
    # ---------------------------------------------------------------------
    # construct filename
    instrument = aparams.get('INSTRUMENT', 'unknown')
    local_dir = (Path(aparams.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                 / 'tasks' / instrument / apero_profile_name / 'objects')
    basename = f'htable_{objname}.json'
    filename = local_dir / basename
    # save results to JSON file for use in the UI
    apero_async.save_results(filename, header_list, metadata)

                
# =============================================================================
# Define helper functions
# ============================================================================= 
def _construct_obj_query(aparams):
    general = aparams.get('general', {})
    if not isinstance(general, dict):
        general = {}
    database = aparams.get('database', {})
    if not isinstance(database, dict):
        database = {}
    science_types = general.get('SCIENCE_TYPES', aparams.get('SCIENCE_TYPES', []))
    if not isinstance(science_types, list):
        science_types = [science_types]
    scitypes = ','.join([f'"{t}"' for t in science_types])
    findex_table = database.get('FINDEX_TABLENAME', aparams.get('FINDEX_TABLENAME', ''))
    if not findex_table:
        raise ValueError('Missing required parameter: database.FINDEX_TABLENAME')
    oparams = dict(FINDEX_TABLENAME=findex_table,
                   SCIENCE_TYPES=scitypes)
    
    obj_query = ('SELECT DISTINCT KW_OBJNAME FROM {FINDEX_TABLENAME} '
                 ' WHERE BLOCK_KIND="raw" AND '
                 'KW_DPRTYPE IN ({SCIENCE_TYPES})')
    obj_query = obj_query.format(**oparams)
    return obj_query


def _get_hdr_key(hdr: fits.Header, keyname: str,
                 hkey: Dict[str, Any]):
    header_key = hkey.get('key', 'Unknown')
    dtype = hkey.get('dtype', 'str')
    # try to open and type cast header key
    try:
        # deal with header key existing
        if header_key in hdr:
            raw_value = hdr[header_key]
            # deal with types
            if dtype == 'float':
                value = float(raw_value)
            elif dtype == 'int':
                value = int(raw_value)
            elif dtype == 'bool':
                value = bool(raw_value)
            else:
                value = str(raw_value)
        else:
            value = None
    except Exception as e:
        emsg = (f'Missing required parameter {keyname}: {header_key}'
                f'\n\tError {type(e)}: {e}')
        raise ValueError(emsg)
    # return values
    return value


def _file_col_query(rparams, objname, block_kind: Optional[str] = None,
                   fiber: Optional[str] = None, scitype: Optional[str] = None, 
                   output: Optional[str] = None) -> str:
    objname_safe = objname.replace("'", "''")
    # deal with optional conditions
    condition = []
    if block_kind is not None:
        condition.append(f"fdb.BLOCK_KIND = '{block_kind}'")
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
        fdb.KW_IDENTIFIER AS IDENTIFIER,
        fdb.KW_DPRTYPE AS KW_DPRTYPE,
        fdb.KW_OUTPUT AS KW_OUTPUT,
        fdb.KW_FIBER AS KW_FIBER,
        fdb.KW_RUN_ID AS KW_RUN_ID,
        fdb.KW_PI_NAME AS KW_PI_NAME,
        FROM_UNIXTIME((fdb.KW_MID_OBS_TIME - 40587) * 86400) AS MID_OBS_TIME,
        FROM_UNIXTIME(fdb.LAST_MODIFIED) AS LAST_MODIFIED,
        fdb.KW_PID AS PID,
        ldb.PASSED_ALL_QC AS PASSED_ALL_QC
    FROM {FINDEX_TABLENAME} fdb
    LEFT JOIN (
        SELECT PID, MAX(PASSED_ALL_QC) AS PASSED_ALL_QC
        FROM {LOG_TABLENAME}
        GROUP BY PID
    ) ldb
            ON fdb.KW_PID = ldb.PID
    WHERE fdb.KW_OBJNAME = '{OBJNAME}' {CONDITION}
    """
    # construct the formatted query
    if len(condition) > 0:
        condition = ' AND ' + ' AND '.join(condition)
    else:
        condition = ''
    rquery =  query.format(OBJNAME=objname_safe, CONDITION=condition,
                           **rparams)
    # deal with just returning the query for testing
    return rquery

 
def _file_col_cmd(aparams, rquery, apero_profile_name, 
                 objname, fkind, outputs):
    db_params = apero_async.get_db_params(aparams)
    start = time.time()
    results = apero_async.database_query(db_params, rquery)
    end = time.time()
    # ---------------------------------------------------------------------
    # time now
    time_now = datetime.now(timezone.utc).isoformat()
    metadata = dict()
    metadata['GENERATED_AT'] = time_now
    metadata['QUERY_TIME'] = end - start
    metadata['APERO_PROFILE'] = apero_profile_name
    
    # only save if there are results
    if isinstance(results, list) and len(results) > 0:        
        # construct filename
        instrument = aparams.get('INSTRUMENT', 'unknown')
        local_dir = (Path(aparams.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                    / 'tasks'  / instrument / apero_profile_name / 'objects')
        basename = f'ftable_{fkind}_{objname}.json'
        filename = local_dir / basename
        # save results to JSON file for use in the UI
        apero_async.save_results(filename, results, metadata)
    # store timing for this object
    outputs['timings'][fkind] = metadata['QUERY_TIME']
    outputs['results'][fkind] = results

    return outputs


def _check_required(aparams) -> Dict[str, Any]:
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
    # Prefer nested database config and flatten required keys for SQL templates.
    db_cfg = aparams.get('database', {})
    if not isinstance(db_cfg, dict):
        db_cfg = {}
    # loop around parameters
    for param in required_params:
        value = db_cfg.get(param, aparams.get(param))
        if value in (None, ''):
            raise ValueError(f'Missing required parameter: database.{param}')
        rparams[param] = value
    # extract science params from the 'general' sub-dict and flatten into rparams
    general = aparams.get('general', {})
    for key in ('SCIENCE_FIBER', 'SCIENCE_TYPES'):
        if key not in general:
            raise ValueError(f'Missing required parameter: general.{key}')
        rparams[key] = general[key]
    # return the required parameters
    return rparams


def _acquire_directory_lock(directory: Path):
    """Acquire an exclusive lock for a directory using a sidecar lock file."""
    import fcntl

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / '.objects.lock'
    lock_handle = lock_path.open('a+')
    # Blocking lock: waits until another process releases the lock.
    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)

    class _DirectoryLock:
        def __enter__(self):
            return lock_handle

        def __exit__(self, exc_type, exc, tb):
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            finally:
                lock_handle.close()

    return _DirectoryLock()


def _clear_directory_contents(directory: Path) -> None:
    """Delete all children in a directory while preserving the directory itself."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for entry in directory.iterdir():
        if entry.name == '.objects.lock':
            continue
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=False)
        else:
            entry.unlink()


def _fill_dict_null(mykeys, mydict: Optional[dict] = None):
    # deal with no input dictionary
    if mydict is None:
        mydict = dict()
    # loop around keys and fill with nulls
    for key in mykeys:
        mydict[key] = None
    return mydict

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

    task = AperoObjectQueryTask()
    run_params = {
        'LOCAL_DATA_DIR': str(ARI_DIR),
        'INSTRUMENT': _TEST_INSTRUMENT.lower(),
        'APERO_PROFILE_NAMES': [_TEST_PROFILE],
        'APERO_PROFILES': {_TEST_PROFILE: _profile},
    }
    # task.test_query(run_params, objnames='GL699')
    task.run_job(run_params)
# =============================================================================
# End of main code
# =============================================================================