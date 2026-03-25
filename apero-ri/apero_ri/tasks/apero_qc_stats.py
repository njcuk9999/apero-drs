#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

"""
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from astropy.io import fits

from apero_ri.tasks import apero_async
from apero_ri.base.base import BLOCK_KIND

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.apero_qc_stats'
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


# =============================================================================
# Define classes
# =============================================================================
class AperoQCStats(apero_async.AperoAsyncTask):
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
                self.info += (
                    f'\n## APERO query stats for APERO Profile: {apero_profile}\n\n'
                    f'- Skipped query run. {skip_reason}\n'
                )
                continue
            # -----------------------------------------------------------------
            # step 1: get calibration files from database
            cfiles, qtime, qnum = get_calib_file(aparams)

            # step 2: read headers and get variables required
            cresults, htime, hnum = read_calib_headers(aparams, cfiles)
            # -----------------------------------------------------------------
            # time now
            time_now = datetime.now(timezone.utc).isoformat()
            metadata = dict()
            metadata['GENERATED_AT'] = time_now
            metadata['QUERY_TIME'] = qtime
            metadata['N_QUERIES'] = qnum
            metadata['HEADER_READ_TIME'] = htime
            metadata['N_HEADERS'] = hnum
            metadata['APERO_PROFILE'] = apero_profile
            # construct filename
            for output in cresults:
                instrument = (
                    aparams.get('general', {}).get('INSTRUMENT', 'unknown')
                )
                local_dir = (Path(params.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                             / 'tasks' / instrument / apero_profile)
                basename = f'qc_stats_{output}.json'
                filename =  local_dir / basename
                # get result
                result = cresults[output]
                # save results to JSON file for use in the UI
                apero_async.save_results(filename, result, metadata)
                # -------------------------------------------------------------
                # add to the output files for this task
                self.output_files.append(str(filename))
            # -----------------------------------------------------------------
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
            # -----------------------------------------------------------------
            # update the info markdown with meta data
            self.info += f"""
            ## Object Table for APERO Profile: {apero_profile}
            
            **Generated at**: {metadata['GENERATED_AT']}  
            **Query time**: {metadata['QUERY_TIME']:.2f} seconds
            **Number of queries**: {metadata['N_QUERIES']}
            
            **Header read time**: {metadata['HEADER_READ_TIME']:.2f} seconds
            **Number of read headers**: {metadata['N_HEADERS']} 
            
            **APERO Profile**: {metadata['APERO_PROFILE']}
            """

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
            # step 1: get calibration files from database
            cquery, _, _ = get_calib_file(aparams, return_query=True)
            # print the query
            print('='*50)
            print(apero_profile_names[a_it])
            print('='*50)
            for output in cquery:
                print(f'Query for KW_OUTPUT={output}')
                print(cquery[output])


# -------------------------------------------------------------------------
# Define helper functions
# -------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def get_calib_file(aparams: Dict[str, Any], return_query=False
                   ) -> Tuple[Dict[str, List[Path]], float, int]:
    # get the hkeys for this fkind
    hcfg = aparams.get('calib-headers', {})
    # Construct queries
    query = """
    SELECT
        BLOCK_KIND,
        OBS_DIR,
        FILENAME,
        KW_OUTPUT
    FROM {FINDEX_TABLENAME}
    WHERE KW_OUTPUT = '{OUTPUT}'
    """
    # get the database parameters
    db_params = apero_async.get_db_params(aparams)
    # storage dictionary to return
    storage = dict()
    # storage for the query times
    times = []
    # get the findex database
    findex = aparams['database']['FINDEX_TABLENAME']
    # loop around
    for output in hcfg:
        # generate the query
        rquery = query.format(OUTPUT=output, FINDEX_TABLENAME=findex)
        # if we only want the query stop here
        if return_query:
            storage[output] = rquery
            continue
        # otherwise query the database
        start = time.time()
        results = apero_async.database_query(db_params, rquery)
        # add to the timings
        times.append(time.time() - start)
        # storage list for this outputs absolute paths
        storage[output] = []
        # we want the filenames
        for entry in results:
            # get block kind
            block_kind = BLOCK_KIND.get(entry['BLOCK_KIND'], None)
            # deal with no block kind defined
            if block_kind is None:
                continue
            # convert block kind to a path
            block_kind = aparams['paths'][block_kind]
            # construct filename from keys
            abspath = Path(block_kind) / entry['OBS_DIR'] / entry['FILENAME']
            # push into storage
            storage[output].append(abspath)

    # work out the total query time
    total_query_time = sum(times)
    total_queries = len(times)
    # return the storage and total query time
    return storage, total_query_time, total_queries



def read_calib_headers(aparams: Dict[str, Any],
                       cfiles: Dict[str, List[Path]]
                       ) -> Tuple[Dict[str, List[dict]], float, int]:

    # get the hkeys for this fkind
    hcfg = aparams.get('calib-headers', {})

    # output table
    header_dict = dict()
    times = []
    # now we read the cfiles
    for output in cfiles:
        # get files
        files = cfiles[output]
        # deal with no files
        if len(files) == 0:
            continue
        # get the required header keys
        hkeys = hcfg.get(output, {})
        # storage for this output
        header_dict[output] = []
        # start a timer
        start = time.time()
        # loop around files
        for abspath in files:
            # check if path exists - if it doesn't fill with None
            if not abspath.exists():
                header_dict[output].append(apero_async.fill_dict_null(hkeys))
                continue
            # check if file is fits file
            if abspath.suffix != '.fits':
                header_dict[output].append(apero_async.fill_dict_null(hkeys))
                continue
            #
            fdict = dict()
            # otherwise we open the file
            hdr = fits.getheader(abspath)
            # loop around header key and load into header list
            for hkey in hkeys:
                fdict[hkey] = apero_async.get_hdr_key(hdr, hkey, hkeys[hkey])
            # push into header_dict
            header_dict[output].append(fdict)
        # append read timer
        times.append(time.time() - start)
    # work out the total query time
    total_read_time = sum(times)
    total_reads = len(times)

    return header_dict, total_read_time, total_reads

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

    task = AperoQCStats()
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
