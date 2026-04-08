#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

"""
import time
import os
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
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
# Whether this task has a sub-process (for sub-processing loading bar in UI)
USE_SUBPROCESS = True
# Whether this task can be run in multi-process mode 
# (if False, will always run in main process)
MULTI_PROCESS = True
# Whether this task supports local pre-built output sync/copy workflows.
LOCAL_TASK = True


# =============================================================================
# Define classes
# =============================================================================
class AperoQCStats(apero_async.AperoAsyncTask):
    """Class representing an asynchronous task in APERO RI."""
    def __init__(self, status='pending'):
        name = 'APERO Quality Control Task'
        description = ('Generate the quality control statistics for the '
                       'APERO reduction interface for each apero profile.')
        super().__init__(name, description, status)
        self.subprogress = 0.0
        self.USE_SUBPROCESS = True

    def run_job(self, params: Dict[str, Any]):
        """
        Create a file that can be used to populate the quality control 
        statistics in the APERO reduction interface.
        
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
        mp_cfg = _normalize_mp_config(task_config)
        task_logger = params.get('TASK_LOGGER')
        stop_event = params.get('STOP_EVENT')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        tlog('APERO_QC_STATS start.')
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
                    f'\n## APERO query stats for APERO Profile: {apero_profile}\n\n'
                    f'- Skipped query run. {skip_reason}\n'
                )
                continue
            # -----------------------------------------------------------------
            # step 1: get calibration files from database
            # -----------------------------------------------------------------
            # log message
            tlog(f'Profile {apero_profile}: querying calibration file '
                 'inventory...')
            # get the calib files
            cfiles, qtime, qnum = get_calib_file(
                aparams, task_logger=tlog, stop_event=stop_event
            )
            if stop_event is not None and stop_event.is_set():
                tlog(f'Profile {apero_profile}: cancellation requested '
                     'after DB query step. Exiting.')
                return
            # -----------------------------------------------------------------
            # step 2: read headers and get variables required
            # -----------------------------------------------------------------
            # log message
            tlog(f'Profile {apero_profile}: reading calibration headers...')
            self.subprogress = 0.0

            def _update_subprogress(done_items: int,
                                    total_items: int,
                                    _item_name: str) -> None:
                total = max(int(total_items or 0), 1)
                self.subprogress = min(1.0, float(done_items) / float(total))

            # read the headers
            cresults, htime, hnum = read_calib_headers(aparams, cfiles, 
                                                       task_logger=tlog, 
                                                       stop_event=stop_event,
                                                       ncores=mp_cfg['ncores'],
                                                       mp_backend=mp_cfg['backend'],
                                                       mp_start_method=mp_cfg['start_method'],
                                                       progress_callback=_update_subprogress)
            self.subprogress = 1.0
            # deal with stop event
            if stop_event is not None and stop_event.is_set():
                tlog(f'Profile {apero_profile}: cancellation requested during '
                     'header read. Exiting.')
                return
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
            tlog(f'Profile {apero_profile}: step timings query={qtime:.2f}s '
                 f'({qnum} queries), headers={htime:.2f}s ({hnum} '
                 'header groups).')
            # construct filename
            for output in cresults:
                instrument = (aparams.get('general', {}).get('INSTRUMENT', 
                                                             'unknown'))
                local_dir = (Path(params.get('LOCAL_DATA_DIR', str(ARI_DIR)))
                             / 'tasks' / instrument / apero_profile)
                basename = f'qc_stats_{output}.json'
                filename =  local_dir / basename
                # get result
                result = cresults[output]
                # save results to JSON file for use in the UI
                apero_async.save_results(filename, result, metadata)
                tlog(
                    f'Profile {apero_profile}: saved qc stats for output={output} '
                    f'to {filename}.'
                )
                # -------------------------------------------------------------
                # add to the output files for this task
                self.output_files.append(str(filename))
            # -----------------------------------------------------------------
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
            **Number of queries**: {metadata['N_QUERIES']}
            
            **Header read time**: {metadata['HEADER_READ_TIME']:.2f} seconds
            **Number of read headers**: {metadata['N_HEADERS']} 
            
            **APERO Profile**: {metadata['APERO_PROFILE']}
            """

            # update the last run time
            self.last_run = time_now

        tlog('APERO_QC_STATS completed.')
    
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
def get_calib_file(aparams: Dict[str, Any], return_query=False,
                   task_logger=None, stop_event=None
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
        if stop_event is not None and stop_event.is_set():
            if callable(task_logger):
                task_logger('QC stats DB query cancelled by stop request.')
            break
        # generate the query
        rquery = query.format(OUTPUT=output, FINDEX_TABLENAME=findex)
        # if we only want the query stop here
        if return_query:
            storage[output] = rquery
            continue
        # otherwise query the database
        start = time.time()
        results = apero_async.database_query(db_params, rquery)
        if callable(task_logger):
            task_logger(
                f'QC stats DB query output={output}: '
                f'{len(results)} rows in {time.time() - start:.2f}s.'
            )
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
                       cfiles: Dict[str, List[Path]],
                       task_logger=None, stop_event=None,
                       ncores: int = 1,
                       mp_backend: str = 'threads',
                       mp_start_method: str = 'default',
                       progress_callback=None
                       ) -> Tuple[Dict[str, List[dict]], float, int]:

    # get the hkeys for this fkind
    hcfg = aparams.get('calib-headers', {})

    # output table
    header_dict = dict()
    times = []
    # now we read the cfiles
    use_parallel = MULTI_PROCESS and int(ncores or 1) > 1
    executor = None
    if use_parallel:
        executor = _make_executor(mp_backend, int(ncores),
                                  mp_start_method, task_logger)
    total_files = sum(len(files or []) for files in cfiles.values())
    done_files = 0
    if callable(progress_callback):
        try:
            progress_callback(done_files, total_files, '')
        except Exception:
            pass
    for output in cfiles:
        if stop_event is not None and stop_event.is_set():
            if callable(task_logger):
                task_logger('QC stats header read cancelled by stop request.')
            break
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
        if executor is not None and len(files) > 1:
            futures = {
                executor.submit(_read_one_calib_header, str(abspath), hkeys): abspath
                for abspath in files
            }
            for fut in as_completed(futures):
                if stop_event is not None and stop_event.is_set():
                    for _f in futures:
                        _f.cancel()
                    if callable(task_logger):
                        task_logger(
                            f'QC stats header read output={output}: cancelled mid-stream.'
                        )
                    break
                header_dict[output].append(fut.result())
                done_files += 1
                if callable(progress_callback):
                    try:
                        progress_callback(done_files, total_files,
                                          str(futures.get(fut, '')))
                    except Exception:
                        pass
        else:
            # loop around files
            for abspath in files:
                if stop_event is not None and stop_event.is_set():
                    if callable(task_logger):
                        task_logger(
                            f'QC stats header read output={output}: cancelled mid-stream.'
                        )
                    break
                header_dict[output].append(_read_one_calib_header(str(abspath), hkeys))
                done_files += 1
                if callable(progress_callback):
                    try:
                        progress_callback(done_files, total_files, str(abspath))
                    except Exception:
                        pass
        if callable(task_logger):
            task_logger(
                f'QC stats header read output={output}: '
                f'{len(header_dict.get(output, []))} rows processed.'
            )
        # append read timer
        times.append(time.time() - start)
    if executor is not None:
        executor.shutdown(wait=True, cancel_futures=True)
    # work out the total query time
    total_read_time = sum(times)
    total_reads = len(times)

    return header_dict, total_read_time, total_reads


def _read_one_calib_header(abspath: str, hkeys: Dict[str, Any]) -> Dict[str, Any]:
    """Read selected FITS header keys for one file with null fallback."""
    path = Path(abspath)
    if not path.exists():
        return apero_async.fill_dict_null(hkeys)
    if path.suffix != '.fits':
        return apero_async.fill_dict_null(hkeys)
    hdr = fits.getheader(path)
    fdict = dict()
    for hkey in hkeys:
        fdict[hkey] = apero_async.get_hdr_key(hdr, hkey, hkeys[hkey])
    return fdict


def _normalize_mp_config(task_config: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize multiprocessing config from TASK_CONFIG."""
    cfg = task_config or {}
    try:
        ncores = int(cfg.get('ncores', cfg.get('NCORES', 1)) or 1)
    except (TypeError, ValueError):
        ncores = 1
    ncores = max(1, ncores)

    backend = str(cfg.get('mp_backend', 'threads') or 'threads').strip().lower()
    if backend not in ('threads', 'processes'):
        backend = 'threads'

    start_method = str(
        cfg.get('mp_start_method', 'default') or 'default'
    ).strip().lower()
    if start_method not in ('default', 'spawn', 'fork', 'forkserver'):
        start_method = 'default'

    max_cores = max(int(os.cpu_count() or 1), 1)
    ncores = min(max_cores, ncores)
    return {
        'ncores': ncores,
        'backend': backend,
        'start_method': start_method,
    }


def _make_executor(mp_backend: str, ncores: int,
                   mp_start_method: str, task_logger=None):
    """Build thread/process executor with fallback to threads."""
    if mp_backend == 'processes':
        try:
            ctx = None
            if mp_start_method != 'default':
                ctx = mp.get_context(mp_start_method)
            return ProcessPoolExecutor(max_workers=max(1, ncores),
                                       mp_context=ctx)
        except Exception as exc:
            if callable(task_logger):
                task_logger(
                    f'QC stats process pool init failed ({exc}); falling back to threads.'
                )
    return ThreadPoolExecutor(max_workers=max(1, ncores))

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
