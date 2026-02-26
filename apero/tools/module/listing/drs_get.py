#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-07

@author: cook
"""
import copy
import fnmatch
import os
import shutil
import tarfile
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from pandasql import sqldf
from astropy.io import fits
from astropy.time import Time

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.constants import path_definitions
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.core.utils import drs_utils

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_get.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
# Get the text types
textentry = lang.textentry
# ALLOWED NULL COLUMNS
NULL_COLS = ['KW_RUN_ID', 'KW_PI_NAME']
# get the tqdm module from base
tqdm = base.TQDM


# =============================================================================
# Define filter functions
# =============================================================================
def basic_filter(params: ParamDict, kw_objnames: List[str],
                 filters: Dict[str, List[str]], user_outdir: str,
                 do_copy: bool = True, do_symlink: bool = False,
                 tarfilename: Optional[str] = None,
                 since: Optional[Time] = None, latest: Optional[Time] = None,
                 timekey: str = 'observed', nosubdir: bool = False,
                 sizelimit: int = None
                 ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    The basic filter function - copies files into OBJNAME directories
    based on the

    :param params: ParamDict, the parameter dictionary of constants
    :param kw_objnames: list of strings, the object names to filter
    :param filters: dictionary of list of strings, each entry is a specific
                    filter from the index database
                    i.e.
                    filters['KW_DPRTYPE'] = ['OBJ_FP', 'OBJ_DARK']
    :param user_outdir: str, the output directory
    :param do_copy: bool, if True copies files (else just prints)
    :param do_symlink: bool, if True creates symlink instead of copying files
    :param tarfilename: str, if not None make a tar file instead of copying files/
                    creating symlinks

    :param since: str, if not None only copy files since this date
    :param latest: str, if not None only copy up to this date
    :param timekey: str, the time key to use (observed or processed)
    :param nosubdir: bool, if True does not create subdirectories for each
                     object name
    :param sizelimit: int, if not None only copy files up to this size limit
                      in GB

    :return: Tuple, 1. dict, for each objname a list of input file locations
                    2. dict, for each objname a list of output file locations
    """
    # -------------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # get whether to filter by passing qc
    filter_qc = not params['INPUTS']['failedqc']
    # get the yamls for permissions
    perm_yaml = params['INPUTS'].get('PERMISSION_YAML', None)
    group_yaml = params['INPUTS'].get('GROUP_YAML', None)
    group_server = params['INPUTS'].get('GROUP_SERVER', None)
    if perm_yaml in ['None', 'Null', '']:
        perm_yaml = None
    if group_yaml in ['None', 'Null', '']:
        group_yaml = None
    if group_server in ['None', 'Null', '']:
        group_server = None
    # -------------------------------------------------------------------------
    # load index database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    findexdb = drs_database.FileIndexDatabase(params)
    findexdb.load_db()
    # load object database
    WLOG(params, '', textentry('40-509-00001', args='astrometric'))
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # load log database
    WLOG(params, '', textentry('40-509-00001', args='log'))
    logdbm = drs_database.LogDatabase(params)
    logdbm.load_db()
    # -------------------------------------------------------------------------
    # deal with tar file name
    if tarfilename is not None:
        tarpath = os.path.join(user_outdir, tarfilename)
    else:
        tarpath = None
    # -------------------------------------------------------------------------
    # create reference condition
    master_condition = ''
    # loop around filters
    for _filter in filters:
        subconditions = []
        # get filter items
        filter_items = filters[_filter]
        # skip Nones
        if drs_text.null_text(filter_items, ['None', '', 'Null']):
            continue
        # deal with strs --> push into lists
        if isinstance(filter_items, str):
            filter_items = [filter_items]
        elif not isinstance(filter_items, list):
            emsg = 'Filter {0}={1} must be a string or list'
            eargs = [_filter, filter_items]
            WLOG(params, 'error', emsg.format(*eargs))
        # loop around object names
        for item in filter_items:
            # skip Nones
            if drs_text.null_text(item, ['None', '', 'Null']):
                continue
            # add to sub conditions
            subcondition = '({0}="{1}")'.format(_filter, item)
            subconditions.append(subcondition)
        # deal with no valid sub-conditions
        if len(subconditions) == 0:
            continue
        # deal with null columns
        if _filter in NULL_COLS:
            subconditions.append('({0} IS NULL)'.format(_filter))
        # add to condition
        if len(master_condition) == 0:
            master_condition += '({0})'.format(' OR '.join(subconditions))
        else:
            master_condition += ' AND ({0})'.format(' OR '.join(subconditions))
    # -------------------------------------------------------------------------
    # deal with time key and going from iso to mjd
    if timekey == 'processed':
        time_col = 'KW_DRS_DATE_NOW'
        if since is not None:
            since = f'\'{since.iso}\''
        if latest is not None:
            latest = f'\'{latest.iso}\''
    else:
        time_col = 'KW_MID_OBS_TIME'
        if since is not None:
            since = since.mjd
        if latest is not None:
            latest = latest.mjd
    # -------------------------------------------------------------------------
    if since is not None:
        subcondition = '({0} > {1})'.format(time_col, since)
        if len(master_condition) == 0:
            master_condition = subcondition
        else:
            master_condition += f' AND {subcondition}'
    # -------------------------------------------------------------------------
    if latest is not None:
        subcondition = '({0} <= {1})'.format(time_col, latest)
        if len(master_condition) == 0:
            master_condition = subcondition
        else:
            master_condition += f' AND {subcondition}'
    # -------------------------------------------------------------------------
    # separate list for each object name
    # -------------------------------------------------------------------------
    # storage of inpaths and run ids
    db_entries = dict(OBJNAME=dict(), RUN_ID=dict())
    # loop around input object names
    for kw_objname in kw_objnames:
        # clean object name (as best we can)
        clean_obj_name, _ = objdbm.find_objname(pconst, kw_objname)
        WLOG(params, '', textentry('40-509-00002', args=[clean_obj_name]))
        # write condition for this object
        if drs_text.null_text(kw_objname, ['None', '', 'Null']):
            obj_condition = None
        else:
            obj_condition = '(KW_OBJNAME="{0}")'.format(clean_obj_name)
        # deal with having an object condition
        condition = ''
        if obj_condition is not None:
            condition += str(obj_condition)
        # deal with having a reference condition
        if len(master_condition) > 0:
            # deal with not having an object condition (don't need the AND)
            if obj_condition is None:
                condition += str(master_condition)
            # deal with having an object condition (need an AND)
            else:
                condition += ' AND {0}'.format(master_condition)
        # deal with no condition still (set condition to None)
        if len(condition) == 0:
            condition = None
        # set columns to get
        icolumns = ['ABSPATH', 'KW_PID', 'KW_RUN_ID']
        # get inpaths
        if params['INPUTS'].get('NODB', False):
            itable = get_disk_entries(params, icolumns, condition=condition)
        else:
            itable = findexdb.get_entries(','.join(icolumns),
                                          condition=condition)
        inpaths = np.array(itable['ABSPATH'])
        ipids = np.array(itable['KW_PID'])
        run_ids = np.array(itable['KW_RUN_ID'])
        # ---------------------------------------------------------------------
        # need to filter by pid in log database
        #    (or read from header in disk case)
        # ---------------------------------------------------------------------
        if filter_qc and params['INPUTS'].get('NODB', False):
            # mask is easy in this case as we have QCC_ALL in the header
            mask = np.array(itable['KW_DRS_QC']).astype(bool)
        elif filter_qc:
            # get all pids where passed_all_qc is PASSED_ALL_QC is True
            ltable = logdbm.get_entries('PID, PASSED_ALL_QC')
            # find all pids that are not zero (nulls, nans and 1s)
            lmask = ~(ltable['PASSED_ALL_QC'] == 0)
            # get a unique list of pids that do not fail QC
            lpids = list(set(ltable[lmask]['PID']))
            # mask out any files that fail qc
            mask = np.isin(ipids, lpids)
        else:
            mask = np.ones(len(inpaths), dtype=bool)
        # ---------------------------------------------------------------------
        # load into file storage
        if len(inpaths[mask]) > 0:
            WLOG(params, '', textentry('40-509-00003', args=[len(inpaths)]))
            # keep files
            db_entries['OBJNAME'][clean_obj_name] = inpaths[mask]
            db_entries['RUN_ID'][clean_obj_name] = run_ids[mask]
        else:
            WLOG(params, '', textentry('40-509-00004'))
        # write that we excluded some files
        if filter_qc:
            WLOG(params, '', textentry('40-509-00005', args=[np.sum(~mask)]))
    # -------------------------------------------------------------------------
    # Now get outpaths (if infile exists)
    # -------------------------------------------------------------------------
    # storage of inpaths/outpaths
    if perm_yaml is not None and group_yaml is not None:
        gsout = get_perm_outpaths(params, nosubdir, db_entries,
                                  user_outdir, do_copy, perm_yaml, group_yaml,
                                  group_server)
    else:

        gsout = get_standard_outpaths(params, nosubdir, db_entries,
                                      user_outdir, do_copy)
    all_inpaths, all_outpaths, all_permissions = gsout
    # -------------------------------------------------------------------------
    # deal with file limit
    # -------------------------------------------------------------------------
    # first deal with checking total size of files
    if sizelimit is not None:
        check_size_limit(params, all_inpaths, sizelimit)
    # -------------------------------------------------------------------------
    # tar files
    # -------------------------------------------------------------------------
    # deal with tar
    if tarpath is not None and do_copy:
        # count files added
        nfiles = 0
        # add to tar file
        with tarfile.open(tarpath, 'w:gz') as tarfile_obj:
            # loop around objects
            for objname in all_inpaths:
                WLOG(params, '', '')
                WLOG(params, '', params['DRS_HEADER'])
                WLOG(params, '', textentry('40-509-00008', args=[objname]))
                WLOG(params, '', params['DRS_HEADER'])
                WLOG(params, '', '')
                # loop around files
                for row in range(len(all_inpaths[objname])):
                    # get in and out path
                    inpath = all_inpaths[objname][row]
                    outpath = all_outpaths[objname][row]
                    # ---------------------------------------------------------
                    # print string
                    copyargs = [row + 1, len(all_inpaths[objname]), outpath]
                    copystr = '[{0}/{1}] --> TAR[{2}]'.format(*copyargs)
                    # print copy string
                    WLOG(params, '', copystr, wrap=False)
                    tarfile_obj.add(inpath, arcname=os.path.basename(inpath))
                    # add to count
                    nfiles += 1
                    continue
        # remove tarpath if no files
        if nfiles == 0:
            if os.path.exists(tarpath):
                os.remove(tarpath)
        # return all in paths and out paths
        return all_inpaths, all_outpaths

    # -------------------------------------------------------------------------
    # Copy files
    # -------------------------------------------------------------------------
    copy_files(params, all_inpaths, all_outpaths, do_symlink, do_copy,
               all_permissions)
    # -------------------------------------------------------------------------
    # Return all in paths and out paths
    # -------------------------------------------------------------------------
    return all_inpaths, all_outpaths


# =============================================================================
# Define disk functions
# =============================================================================
def get_disk_entries(params: ParamDict, icolumns: List[str],
                     condition: Optional[str] = None) -> pd.DataFrame:
    """
    Get entries from disk (instead of database)

    :param ParamDict params: the parameter dictionary of constants
    :param icolumns: list of strings, the columns to get (must be ABSPATH, KW_PID
                     and KW_RUN_ID)
    :param condition: str, the condition to apply (must be in the format of a
                      SQL condition but without the WHERE)
    :return: pandas dataframe, the entries that match the condition
    """
    # translate icolumns and conditions into required header keys
    hkeys = dict()
    # loop around columns and look for keys in params
    for key in icolumns:
        _key = key.strip()
        # skip any key that doesn't start with KW_
        if not _key.startswith('KW_'):
            continue
        # now look for keys in params and save the header key value
        if _key in params:
            hkeys[_key] = params[_key][0]
    # loop around conditions and look for keys in params
    for key in condition.split(' '):
        _key = key.strip('()')
        _key = _key.split('=')[0]
        # skip any key that doesn't start with KW_
        if not _key.startswith('KW_'):
            continue
        # now look for keys in params and save the header key value
        if _key in params:
            hkeys[_key] = params[_key][0]
    # Add the QCC_ALL key - will be needed for qc filtering later
    hkeys['KW_DRS_QC'] = params['KW_DRS_QC'][0]

    # deal with non-header keys required
    req_abspath =  'ABSPATH' in icolumns
    req_filename = 'FILENAME' in icolumns
    req_obsdir = 'OBS_DIR' in icolumns

    # we must have the block kind to know where to look for files on disk
    if params['INPUTS']['BLOCK_KIND'] in ['None', 'Null', None]:
        emsg = 'BLOCK_KIND must be given in INPUT to use disk entries (--nodb)'
        WLOG(params, 'error', emsg)
        return pd.DataFrame()
    # get the block
    block_kind = params['INPUTS']['BLOCK_KIND']
    # intial values for the block path and block names
    block_path, block_names = None, []
    # get the directory
    for block in path_definitions.BLOCKS:
        # construct this block
        _block = block(params)
        # append to block paths
        block_names.append(block.name)
        # update the path if found
        if block.name == block_kind:
            block_path = _block.path
    # deal with no path
    if block_path is None:
        emsg = 'Block kind {0} is invalid. Must be {1}'
        eargs = [block_kind, ','.join(block_names)]
        WLOG(params, 'error', emsg.format(*eargs))

    # get the suffix
    if params['INPUTS']['NODB_WILDCARD'] in ['None', 'Null', '', None]:
        file_wildcard = '*'
    else:
        file_wildcard = params['INPUTS']['NODB_WILDCARD']

    # -------------------------------------------------------------------------
    # Step 1: look for all files in the directory (or directories)
    # -------------------------------------------------------------------------
    files = _get_files_from_disk(block_path, file_wildcard)
    # -------------------------------------------------------------------------
    # Step 2: Read files from disk and read the header keys into
    # -------------------------------------------------------------------------
    records = _get_file_hkeys(params, files, hkeys, req_abspath, req_filename,
                              req_obsdir, block_kind, block_path)
    # -------------------------------------------------------------------------
    # Step 3: Convert records into pandas dataframe and apply condition filter
    # -------------------------------------------------------------------------
    itable = _convert_records_to_dataframe(records, condition=condition)

    # return this itable
    return itable


def _get_files_from_disk(filepath: str, file_wildcard: str) -> List[str]:
    """
    Get all files from disk matching a wildcard

    :param filepath: str, the file path to search
    :param file_wildcard: str, the wildcard to use when searching for files

    :return: list of strings, the files found on disk
    """
    # storage of valid files
    valid_files = []
    # use os to walk the directory and find files
    for root, dirs, files in os.walk(filepath):
        # loop around files
        for filename in files:
            if fnmatch.fnmatch(filename, file_wildcard):
                valid_files.append(os.path.join(root, filename))
    # return valid files
    return valid_files



def _get_file_hkeys(params, files: List[str], hkeys: Dict[str, str],
                    req_abspath: bool, req_filename: bool,
                    req_obsdir: bool, block_kind: str,
                    block_path: str) -> List[Dict[str, Any]]:
    """
    Get header keys for a list of files, with optional parallelization

    :param params: ParamDict, the parameter dictionary of constants
    :param files: list of strings, the files to read header keys from
    :param hkeys: list of strings, the header keys to extract from each file
    :param req_abspath: bool, whether to include absolute path in the output
                        records
    :param req_filename: bool, whether to include filename in the output records
    :param req_obsdir: bool, whether to include observation directory in the
                       output records
    :param block_path: str, the base block path for calculating relative
                       observation directory
    :return:
    """
    # get the number of cores to use
    cores = drs_utils.get_cores(params)
    # get the multi-processing mode
    mp_mode = params['INPUTS']['MP_MODE']

    # print progress
    msg = 'Getting header keys for {0} files using {1} cores'
    margs = [len(files), cores]
    WLOG(params, 'info', msg.format(*margs))

    # use parallelization if requested and cores > 1
    if mp_mode.lower() == 'pathos' and cores > 1:
        records = _multi_process_get_hkeys_pathos(files, hkeys,
                                                  req_abspath, req_filename,
                                                  req_obsdir, block_kind,
                                                  block_path, cores)
    elif mp_mode.lower() == 'pool' and cores > 1:
        records = _multi_process_get_hkeys_pool(files, hkeys,
                                                req_abspath, req_filename,
                                                req_obsdir, block_kind,
                                                block_path, cores)
    elif mp_mode.lower() == 'process' and cores > 1:
        records = _multi_process_get_hkeys_process(files, hkeys,
                                                   req_abspath, req_filename,
                                                   req_obsdir, block_kind,
                                                   block_path, cores)
    else:
        records = _get_file_hkeys_serial(files, hkeys, req_abspath,
                                         req_filename, req_obsdir, block_kind,
                                         block_path)
    # return the records
    return records


def _convert_records_to_dataframe(records: List[Dict[str, Any]],
                                  condition: Optional[str] = None) -> pd.DataFrame:
    """
    Convert a list of records (dictionaries) into a pandas DataFrame and
    apply a SQL condition filter using pandasql

    :param records: list of dictionaries, each dictionary contains header keys
                    and file information for a single file
    :param condition: str or None, SQL-like condition to filter the records
                      (e.g., 'KW_OBJNAME="GL699" AND KW_OUTPUT="EXT_E2DS"')

    :return: pandas DataFrame, the filtered table containing the header keys
             and file information
    """
    # convert list of dicts to pandas DataFrame
    if len(records) > 0:
        df = pd.DataFrame(records)

        # apply condition if provided using pandasql
        if condition is not None and condition.strip():
            try:
                # Use pandasql to apply the SQL WHERE condition
                query = f"SELECT * FROM df WHERE {condition}"
                df = sqldf(query, locals())
            except Exception as e:
                # raise APERO error if condition is invalid
                emsg = ('Invalid condition:\nWHERE "{0}". '
                        '\n\t Available columns = {1}'
                        '\n\tError: {1}')
                eargs = [condition, ','.join(df.columns), str(e)]
    else:
        df = pd.DataFrame()

    return df



# =============================================================================
# Define helper functions for parallel processing
# =============================================================================
def _get_single_file_hkeys(filename: str, hkeys: Dict[str, str],
                           req_abspath: bool, req_filename: bool,
                           req_obsdir: bool, block_kind: str,
                           block_path: str) -> Dict[str, Any]:
    """
    Process a single file and extract header keys and file information

    :param filename: str, path to the file
    :param hkeys: List[str], list of header keys to extract
    :param req_abspath: bool, whether to include absolute path
    :param req_filename: bool, whether to include filename
    :param req_obsdir: bool, whether to include observation directory
    :param block_path: str, base block path for relative path calculation

    :return: Dict[str, Any], record containing file info and header keys
    """
    record = dict()
    # try to read the header key from the file
    hdr = fits.getheader(filename)

    if req_abspath:
        record['ABSPATH'] = os.path.abspath(filename)
    if req_filename:
        record['FILENAME'] = os.path.basename(filename)
    if req_obsdir:
        record['OBS_DIR'] = os.path.relpath(os.path.dirname(filename),
                                            block_path)
    # always add block kind
    record['BLOCK_KIND'] = block_kind
    # get the header keys for this file
    for key in hkeys:
        # get the header key to look for in the file
        hkey = hkeys[key]
        # save as record (using original key name for the record)
        record[key] = copy.deepcopy(hdr.get(hkey, None))
    # return the record
    return record


def _get_file_hkeys_serial(files: List[str], hkeys: Dict[str, str],
                           req_abspath: bool, req_filename: bool,
                           req_obsdir: bool, block_kind: str,
                           block_path: str) -> List[Dict[str, Any]]:
    """
    Process files serially to extract header keys

    :param files: List[str], list of file paths
    :param hkeys: List[str], list of header keys to extract
    :param req_abspath: bool, whether to include absolute path
    :param req_filename: bool, whether to include filename
    :param req_obsdir: bool, whether to include observation directory
    :param block_path: str, base block path for relative path calculation

    :return: List[Dict[str, Any]], list of records
    """
    records = []
    for filename in tqdm(files):
        record = _get_single_file_hkeys(filename, hkeys, req_abspath,
                                        req_filename, req_obsdir, block_kind,
                                        block_path)
        records.append(record)
    return records


def _multi_process_get_hkeys_process(files: List[str], hkeys: Dict[str, str],
                                     req_abspath: bool, req_filename: bool,
                                     req_obsdir: bool, block_kind: str,
                                     block_path: str,
                                     cores: int) -> List[Dict[str, Any]]:
    """
    Process files using multiprocessing.Process

    :param files: List[str], list of file paths
    :param hkeys: List[str], list of header keys to extract
    :param req_abspath: bool, whether to include absolute path
    :param req_filename: bool, whether to include filename
    :param req_obsdir: bool, whether to include observation directory
    :param block_path: str, base block path for relative path calculation
    :param cores: int, number of cores to use

    :return: List[Dict[str, Any]], list of records
    """
    from multiprocessing import Process, Manager, Queue

    # split files into N=cores groups
    cores = min(cores, len(files))
    chunk_size = int(np.ceil(len(files) / cores))

    grouped_files = [files[i:i + chunk_size]
                     for i in range(0, len(files), chunk_size)]

    # use manager to share results across processes
    with Manager() as manager:
        records_list = manager.list()
        progress_queue = Queue()
        jobs = []

        # loop around each group
        for g_it, grouped_file in enumerate(grouped_files):
            args = [grouped_file, hkeys, req_abspath, req_filename,
                    req_obsdir, block_kind, block_path, records_list,
                    progress_queue]
            process = Process(target=_multi_get_hkeys_worker, args=args)
            process.start()
            jobs.append(process)

        # track progress
        pbar = tqdm(total=len(files), desc='Reading file headers')
        processed = 0
        while processed < len(files):
            try:
                progress_queue.get(timeout=0.1)
                processed += 1
                pbar.update(1)
            except:
                pass
            # check if all processes are done
            if all(not proc.is_alive() for proc in jobs):
                # get any remaining progress updates
                while not progress_queue.empty():
                    progress_queue.get()
                    processed += 1
                    pbar.update(1)
                break
        pbar.close()

        # wait for all processes to finish
        for proc in jobs:
            proc.join()

        # convert manager list to regular list
        records = list(records_list)

    return records


def _multi_process_get_hkeys_pool(files: List[str], hkeys: Dict[str, str],
                                  req_abspath: bool, req_filename: bool,
                                  req_obsdir: bool, block_kind: str,
                                  block_path: str,
                                  cores: int) -> List[Dict[str, Any]]:
    """
    Process files using multiprocessing.Pool

    :param files: List[str], list of file paths
    :param hkeys: List[str], list of header keys to extract
    :param req_abspath: bool, whether to include absolute path
    :param req_filename: bool, whether to include filename
    :param req_obsdir: bool, whether to include observation directory
    :param block_path: str, base block path for relative path calculation
    :param cores: int, number of cores to use

    :return: List[Dict[str, Any]], list of records
    """
    from multiprocessing import get_context
    from functools import partial

    # create partial function with fixed arguments
    process_func = partial(_get_single_file_hkeys, hkeys=hkeys,
                           req_abspath=req_abspath, req_filename=req_filename,
                           req_obsdir=req_obsdir, block_kind=block_kind,
                           block_path=block_path)

    # use pool to process files with progress bar
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        records = list(tqdm(pool.imap_unordered(process_func, files),
                           total=len(files), desc='Reading file headers'))

    return records


def _multi_process_get_hkeys_pathos(files: List[str], hkeys: Dict[str, str],
                                    req_abspath: bool, req_filename: bool,
                                    req_obsdir: bool, block_kind: str,
                                    block_path: str,
                                    cores: int) -> List[Dict[str, Any]]:
    """
    Process files using pathos multiprocessing

    :param files: List[str], list of file paths
    :param hkeys: List[str], list of header keys to extract
    :param req_abspath: bool, whether to include absolute path
    :param req_filename: bool, whether to include filename
    :param req_obsdir: bool, whether to include observation directory
    :param block_path: str, base block path for relative path calculation
    :param cores: int, number of cores to use

    :return: List[Dict[str, Any]], list of records
    """
    try:
        from pathos.multiprocessing import ProcessPool
        from functools import partial

        # create partial function with fixed arguments
        process_func = partial(_get_single_file_hkeys, hkeys=hkeys,
                               req_abspath=req_abspath,
                               req_filename=req_filename,
                               req_obsdir=req_obsdir,  block_kind= block_kind,
                               block_path=block_path)

        # use pathos pool to process files with progress bar
        with ProcessPool(cores) as pool:
            records = list(tqdm(pool.imap(process_func, files),
                               total=len(files), desc='Reading file headers'))

        return records
    except ImportError:
        # fallback to process mode if pathos not available
        return _multi_process_get_hkeys_process(files, hkeys,
                                                req_abspath, req_filename,
                                                req_obsdir, block_kind,
                                                block_path, cores)


def _multi_get_hkeys_worker(files: List[str], hkeys: Dict[str, str],
                            req_abspath: bool, req_filename: bool,
                            req_obsdir: bool, block_kind: str, block_path: str,
                            records_list, progress_queue=None) -> None:
    """
    Worker function for multiprocessing.Process to process a batch of files

    :param files: List[str], list of file paths to process
    :param hkeys: List[str], list of header keys to extract
    :param req_abspath: bool, whether to include absolute path
    :param req_filename: bool, whether to include filename
    :param req_obsdir: bool, whether to include observation directory
    :param block_path: str, base block path for relative path calculation
    :param records_list: multiprocessing.Manager.list, shared list for results
    :param progress_queue: multiprocessing.Queue, optional queue for progress updates

    :return: None
    """
    for filename in files:
        record = _get_single_file_hkeys(filename, hkeys, req_abspath,
                                        req_filename, req_obsdir, block_kind,
                                        block_path)
        records_list.append(record)
        # send progress update if queue is available
        if progress_queue is not None:
            progress_queue.put(1)


# =============================================================================
# Define helper functions
# =============================================================================
AllDict = Dict[str, List[str]]
PermDict = Dict[str, List[Union[None, Dict[str, str]]]]


def get_out_basename(params: ParamDict, infile: str) -> str:
    """
    Get the output base name for an input file based on prefix/suffix

    :param params: str, the parameter dictionary of constants
    :param infile: str, the input file name

    :return: str, the output base name with prefix/suffix applied if given
    """
    # get the prefix and suffix from inputs
    prefix = params['INPUTS'].get('OUT_PREFIX', None)
    suffix = params['INPUTS'].get('OUT_SUFFIX', None)
    # deal with null prefix/suffix
    if drs_text.null_text(prefix, ['None', '', 'Null']):
        prefix = None
    if drs_text.null_text(suffix, ['None', '', 'Null']):
        suffix = None
    # deal with no prefix or suffix --> just return base name
    if prefix is None and suffix is None:
        return os.path.basename(infile)
    # deal with only prefix (no suffix)
    if suffix is None:
        return prefix + os.path.basename(infile)
    # deal with only suffix (no prefix)
    elif prefix is None:
        base, ext = os.path.splitext(os.path.basename(infile))
        return base + suffix + ext
    # deal with both prefix and suffix
    else:
        base, ext = os.path.splitext(os.path.basename(infile))
        return prefix + base + suffix + ext


def get_standard_outpaths(params, nosubdir: bool, db_entries,
                          user_outdir, do_copy: bool = True
                          ) -> Tuple[AllDict, AllDict, PermDict]:
    # storage of inpaths/outpaths
    all_inpaths = dict()
    all_outpaths = dict()
    all_permissions = dict()
    # get just the in paths dictionary
    db_inpaths = db_entries['OBJNAME']
    # loop around objects with files
    for objname in db_inpaths:
        # output directory for objname
        if nosubdir:
            outdir = str(user_outdir)
        else:
            outdir = str(os.path.join(user_outdir, objname))
        # print progress: Adding outpaths for KW_OBJNAME={0}
        WLOG(params, '', textentry('40-509-00006', args=[objname]))
        # add object name to storage
        all_inpaths[objname] = []
        all_outpaths[objname] = []
        all_permissions[objname] = []
        # loop around all files for this object
        for filename in db_inpaths[objname]:
            # if object exists
            if os.path.exists(filename):
                # get paths
                inpath = filename
                basename = get_out_basename(params, filename)
                outpath = os.path.join(outdir, basename)
                # add to storage
                all_inpaths[objname].append(inpath)
                all_outpaths[objname].append(outpath)
                all_permissions[objname].append(None)
        # make a directory for this object (if it doesn't exist)
        if len(all_outpaths[objname]) != 0:
            # print progress: Added {0} outpaths'
            margs = [len(all_outpaths[objname])]
            WLOG(params, '', textentry('40-509-00007', args=margs))
            # create output directory if it doesn't exist
            if not os.path.exists(outdir) and do_copy:
                os.mkdir(outdir)

    return all_inpaths, all_outpaths, all_permissions


def get_perm_outpaths(params, nosubdir: bool, db_entries,
                      user_outdir, do_copy: bool = True,
                      perm_yaml: str = None, group_yaml: str = None,
                      group_server: str = None
                      ) -> Tuple[AllDict, AllDict, PermDict]:

    # storage of inpaths/outpaths
    all_inpaths = dict()
    all_outpaths = dict()
    all_permissions = dict()
    # get in paths dictionary and run ids dictionary
    db_inpaths = db_entries['OBJNAME']
    db_runids = db_entries['RUN_ID']
    # -------------------------------------------------------------------------
    # load permission yaml
    if not os.path.exists(perm_yaml):
        eargs = [perm_yaml]
        emsg = 'Permission YAML file {0} does not exist'
        WLOG(params, 'error', emsg.format(*eargs))
    perm_dict = base.load_yaml(perm_yaml)
    # -------------------------------------------------------------------------
    # load group yaml
    if not os.path.exists(group_yaml):
        eargs = [group_yaml]
        emsg = 'Group YAML file {0} does not exist'
        WLOG(params, 'error', emsg.format(*eargs))
    group_dict = base.load_yaml(group_yaml)
    # -------------------------------------------------------------------------
    # user outdir needs to have an objects and a runid directory
    obj_dir = os.path.join(user_outdir, 'objects')
    runid_dir = os.path.join(user_outdir, 'runids')
    # make the object sub-directory if it doesn't exist
    if not os.path.exists(obj_dir) and do_copy:
        os.mkdir(obj_dir)
    # make the runid sub-directory if it doesn't exist
    if not os.path.exists(runid_dir) and do_copy:
        os.mkdir(runid_dir)
    # -------------------------------------------------------------------------
    # loop around objects with files
    for objname in db_inpaths:

        # output directory for objname
        if nosubdir:
            obj_outdir = str(obj_dir)
        else:
            obj_outdir = str(os.path.join(obj_dir, objname))

        # print progress: Adding outpaths for KW_OBJNAME={0}
        WLOG(params, '', textentry('40-509-00006', args=[objname]))
        # add object name to storage
        all_inpaths[objname] = []
        all_outpaths[objname] = []
        all_permissions[objname] = []
        # loop around all files for this object
        for f_it, filename in enumerate(db_inpaths[objname]):
            # if object exists
            if os.path.exists(filename):
                # get file base name
                basename = get_out_basename(params, filename)
                # get paths
                run_id_inpath = filename
                # -------------------------------------------------------------
                # manage run id files
                # -------------------------------------------------------------
                # get run id for this file
                run_id = db_runids[objname][f_it]
                # skip files we don't have permission to copy
                if run_id not in perm_dict:
                    continue
                # out run id path is runid_dir/{RUNID}/basename
                run_id_outdir = os.path.join(runid_dir, str(run_id))
                # make run id directory if it doesn't exist
                if not os.path.exists(run_id_outdir) and do_copy:
                    os.mkdir(run_id_outdir)
                # run directory permission commands (if given)
                _ = permission_commands(params, run_id, perm_dict,
                                        group_dict, group_server,
                                        ptype='dir',
                                        run=True, path=run_id_outdir)

                run_id_outpath = os.path.join(run_id_outdir, basename)
                # add obj path to storage
                all_inpaths[objname].append(run_id_inpath)
                all_outpaths[objname].append(run_id_outpath)

                # TODO: Test whether we need to add permissions per file
                #       of if per directory is enough
                # run directory permission commands (if given)
                # cmds = permission_commands(params, run_id, perm_dict,
                #                         group_dict, group_server,
                #                         ptype='file',
                #                         run=True, path=run_id_outdir)
                cmds = []
                all_permissions[objname].append(dict(CTYPE='CP', COMMANDS=cmds))
                # -------------------------------------------------------------
                # manage object files
                # -------------------------------------------------------------
                # make run id directory if it doesn't exist
                if not os.path.exists(obj_outdir) and do_copy:
                    os.mkdir(obj_outdir)
                # get the outpath for the object file
                obj_outpath = os.path.join(obj_outdir, basename)
                # add obj path to storage
                all_inpaths[objname].append(run_id_outpath)
                all_outpaths[objname].append(obj_outpath)
                all_permissions[objname].append(dict(CTYPE='SYM', COMMANDS=[]))

    # return in paths out paths and permissions
    return all_inpaths, all_outpaths, all_permissions


def copy_files(params, all_inpaths: AllDict,  all_outpaths: AllDict,
               do_symlink: bool, do_copy: bool,
               all_permissions: PermDict):
    # get the number of cores to use
    cores = drs_utils.get_cores(params)
    # get the multi-processing mode
    mp_mode = params['INPUTS']['MP_MODE']

    for objname in all_inpaths:
        WLOG(params, '', '')
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', textentry('40-509-00008', args=[objname]))
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', '')

        # prepare data for parallel processing
        copy_tasks = []
        for row in range(len(all_inpaths[objname])):
            inpath = all_inpaths[objname][row]
            outpath = all_outpaths[objname][row]
            permission = all_permissions[objname][row]
            total_files = len(all_inpaths[objname])
            copy_tasks.append((row, inpath, outpath, permission, total_files,
                             do_symlink, do_copy))

        # use parallelization if requested and cores > 1
        if mp_mode.lower() == 'pathos' and cores > 1:
            _multi_process_copy_files_pathos(params, copy_tasks, cores)
        elif mp_mode.lower() == 'pool' and cores > 1:
            _multi_process_copy_files_pool(params, copy_tasks, cores)
        elif mp_mode.lower() == 'process' and cores > 1:
            _multi_process_copy_files_process(params, copy_tasks, cores)
        else:
            _copy_files_serial(params, copy_tasks)

    return all_inpaths, all_outpaths


# =============================================================================
# Define helper functions for parallel file copying
# =============================================================================

def _copy_single_file(params: ParamDict, task: tuple) -> None:
    """
    Copy or symlink a single file with optional permissions

    :param params: ParamDict, parameter dictionary
    :param task: tuple containing (row, inpath, outpath, permission,
                 total_files, do_symlink, do_copy)

    :return: None
    """
    row, inpath, outpath, permission, total_files, do_symlink, do_copy = task

    # -----------------------------------------------------------------
    # copy via all permissions dictionary
    # -----------------------------------------------------------------
    if permission is not None:
        # get copy type and commands
        ctype = permission['CTYPE']
        commands = permission['COMMANDS']
        # print string
        copyargs = [row + 1, total_files, ctype, outpath]
        copystr = '[{0}/{1}] --> {2}[{3}]'.format(*copyargs)
        # print copy string
        WLOG(params, '', copystr, wrap=False)
        # remove previous
        remove_previous(outpath)
        # run copy commands on files
        # (usually a copy or symlink followed by some permission change)
        try:
            if ctype == 'SYM':
                os.symlink(inpath, outpath)
            else:
                shutil.copy(inpath, outpath)
            # then run permission commands
            for command in commands:
                os.system(command)
        except Exception as _:
            eargs = [ctype, inpath, outpath]
            emsg = 'Failed to run {0} commands on {1} to {2}'
            emsg += ' with commands: \n{2}'
            emsg = emsg.format(*eargs, '\n'.join(commands))
            WLOG(params, 'error', emsg.format(*eargs))
    # -----------------------------------------------------------------
    # copy via symbolic link
    # -----------------------------------------------------------------
    elif do_symlink and do_copy:
        # print string
        copyargs = [row + 1, total_files, outpath]
        copystr = '[{0}/{1}] --> SYM[{2}]'.format(*copyargs)
        # print copy string
        WLOG(params, '', copystr, wrap=False)
        # remove and symlink
        remove_previous(outpath)
        os.symlink(inpath, outpath)
    # -----------------------------------------------------------------
    # copy via shutil copy (full copy)
    # -----------------------------------------------------------------
    elif do_copy:
        # print string
        copyargs = [row + 1, total_files, outpath]
        copystr = '[{0}/{1}] --> CP[{2}]'.format(*copyargs)
        # print copy string
        WLOG(params, '', copystr, wrap=False)
        # remove and copy
        remove_previous(outpath)
        shutil.copy(inpath, outpath)


def _copy_files_serial(params: ParamDict, tasks: List[tuple]) -> None:
    """
    Copy files serially with progress bar

    :param params: ParamDict, parameter dictionary
    :param tasks: List of tuples, each containing copy task info

    :return: None
    """
    for task in tqdm(tasks, desc='Copying files'):
        _copy_single_file(params, task)


def _multi_process_copy_files_process(params: ParamDict, tasks: List[tuple],
                                      cores: int) -> None:
    """
    Copy files using multiprocessing.Process

    :param params: ParamDict, parameter dictionary
    :param tasks: List of tuples, each containing copy task info
    :param cores: int, number of cores to use

    :return: None
    """
    from multiprocessing import Process, Queue

    # split tasks into N=cores groups
    cores = min(cores, len(tasks))
    chunk_size = int(np.ceil(len(tasks) / cores))

    grouped_tasks = [tasks[i:i + chunk_size]
                     for i in range(0, len(tasks), chunk_size)]

    # create progress queue
    progress_queue = Queue()
    jobs = []

    # loop around each group
    for g_it, grouped_task in enumerate(grouped_tasks):
        args = [params, grouped_task, progress_queue]
        process = Process(target=_multi_copy_worker, args=args)
        process.start()
        jobs.append(process)

    # track progress
    pbar = tqdm(total=len(tasks), desc='Copying files')
    processed = 0
    while processed < len(tasks):
        try:
            progress_queue.get(timeout=0.1)
            processed += 1
            pbar.update(1)
        except:
            pass
        # check if all processes are done
        if all(not proc.is_alive() for proc in jobs):
            # get any remaining progress updates
            while not progress_queue.empty():
                progress_queue.get()
                processed += 1
                pbar.update(1)
            break
    pbar.close()

    # wait for all processes to finish
    for proc in jobs:
        proc.join()


def _multi_process_copy_files_pool(params: ParamDict, tasks: List[tuple],
                                   cores: int) -> None:
    """
    Copy files using multiprocessing.Pool

    :param params: ParamDict, parameter dictionary
    :param tasks: List of tuples, each containing copy task info
    :param cores: int, number of cores to use

    :return: None
    """
    from multiprocessing import get_context
    from functools import partial

    # create partial function with fixed params argument
    copy_func = partial(_copy_single_file, params)

    # use pool to process files with progress bar
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        list(tqdm(pool.imap_unordered(copy_func, tasks),
                 total=len(tasks), desc='Copying files'))


def _multi_process_copy_files_pathos(params: ParamDict, tasks: List[tuple],
                                     cores: int) -> None:
    """
    Copy files using pathos multiprocessing

    :param params: ParamDict, parameter dictionary
    :param tasks: List of tuples, each containing copy task info
    :param cores: int, number of cores to use

    :return: None
    """
    try:
        from pathos.multiprocessing import ProcessPool
        from functools import partial

        # create partial function with fixed params argument
        copy_func = partial(_copy_single_file, params)

        # use pathos pool to process files with progress bar
        with ProcessPool(cores) as pool:
            list(tqdm(pool.imap(copy_func, tasks),
                     total=len(tasks), desc='Copying files'))
    except ImportError:
        # fallback to process mode if pathos not available
        _multi_process_copy_files_process(params, tasks, cores)


def _multi_copy_worker(params: ParamDict, tasks: List[tuple],
                      progress_queue) -> None:
    """
    Worker function for multiprocessing.Process to copy a batch of files

    :param params: ParamDict, parameter dictionary
    :param tasks: List of tuples, each containing copy task info
    :param progress_queue: multiprocessing.Queue, queue for progress updates

    :return: None
    """
    for task in tasks:
        _copy_single_file(params, task)
        # send progress update
        progress_queue.put(1)


def permission_commands(params, run_id: str, perm_dict: dict,
                        group_dict: dict, group_server: str,
                        ptype: str = 'file',
                        run: bool = False, path: str = '') -> List[str]:
    """
    Run permission commands on a file

    :param params: ParamDict, the parameter dictionary of constants
    :param commands: list of strings, the commands to run

    :return:
    """
    # find run id in permission dictionary
    if run_id not in perm_dict:
        return []
    # get the permissions for this run id
    run_id_dict = perm_dict[run_id]
    # -------------------------------------------------------------------------
    # storage of users and their permissions
    users = dict()
    # deal with groups
    for group in run_id_dict.get('GROUPS', []):
        # make sure the group exists in our group dictionary
        if group in group_dict:
            _group_dict = group_dict[group]
            # get group parameters
            _group_users = _group_dict.get('USERS', [])
            _group_server = _group_dict.get('SERVER', None)
            _group_dir_perms = _group_dict.get('DIRECTORY_PERMISSIONS', None)
            _group_file_perms = _group_dict.get('FILE_PERMISSIONS', None)
            # if the group server is not the same as the current server skip
            #  this group
            if group_server != _group_server:
                continue
            # loop around users in this group
            for _user in _group_users:
                # make sure we don't add a user twice
                if _user not in users:
                    # deal with directory
                    if ptype == 'dir':
                        users[_user] = _group_dir_perms
                    else:
                        users[_user] = _group_file_perms
    # -------------------------------------------------------------------------
    # store commands to run
    commands = []
    # loop around users and run commands
    for _user in users:
        # get args
        _kwargs = dict(user=_user, path=path)
        # loop around commands
        for user_cmd in users[_user]:
            # skip if no command given
            if user_cmd is None:
                continue
            # push arguments into command
            command = user_cmd.format(**_kwargs)
            # add to commands (if not already there)
            if command not in commands:
                commands.append(command)
    # -------------------------------------------------------------------------
    # try to run command
    if run:
        for command in commands:
            try:
                os.system(command)
            except Exception as _:
                eargs = [command]
                emsg = 'Failed to run permission command: {0}'
                WLOG(params, 'error', emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # return commands
    return commands


def remove_previous(outpath: str):
    """
    Deal with removing previous file (whether it is a hard link or symlink)
    :param outpath: str, file to check
    :return:
    """
    if os.path.islink(outpath):
        os.unlink(outpath)
    elif not os.path.exists(outpath):
        return
    else:
        os.remove(outpath)


def all_objects(params):
    # load index database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    findexdb = drs_database.FileIndexDatabase(params)
    findexdb.load_db()
    # return all object names
    objs =  findexdb.get_unique(column='KW_OBJNAME',
                                condition='BLOCK_KIND="raw"')
    # print number of objects found
    msg = 'Found {0} raw objects in file index database'
    margs = [len(objs)]
    WLOG(params, 'info', msg.format(*margs))
    # return objects
    return objs


def fiber_by_output(kw_fibers: Union[List[str], None],
                    kw_outputs: Union[List[str], None]
                    ) -> Union[List[str], None]:
    # if we have no outputs just return the fibers
    if kw_outputs is None:
        return kw_fibers
    # if fibers is already None just return it
    if kw_fibers is None:
        return None
    # load psuedo constants
    pconst = constants.pload()
    filemod = pconst.FILEMOD().get()
    # get filesets
    filedefs = [filemod.raw_file, filemod.pp_file, filemod.red_file,
                filemod.post_file]
    # get all drs output ids that do not have fiber set
    no_fiber_drsoutids = []
    # loop around
    for filedef in filedefs:
        for drs_file in filedef.fileset:
            if drs_file.fibers is None:
                no_fiber_drsoutids.append(drs_file.name)
    # now deal with outputs that our in our list
    # if we have one output in out list return kw_fibers = None
    for kw_output in kw_outputs:
        if kw_output in no_fiber_drsoutids:
            return None
    # if we get to here we return kw_fibers
    return kw_fibers


def check_size_limit(params: ParamDict, inpaths: Dict[str, List[str]],
                     sizelimit: int):
    """
    Check that the total size of files does not exceed the size limit

    :param params: ParamDict, the parameter dictionary of constants
    :param inpaths: dictionary, for each objname a list of input file locations
    :param sizelimit: int, a file limit in GBs

    :raises: WLOG error if total size of files exceeds limit
    :return:
    """
    # deal with bad size limit
    if sizelimit in ['None', None, '', 'Null']:
        return
    # deal with bad size limit
    if sizelimit <= 0:
        return
    # store total size in bytes
    total_size = 0
    # loop around all objects and all files and add to the total size
    for key in inpaths:
        for path in inpaths[key]:
            total_size += os.path.getsize(path)
    # convert to GB
    total_size = total_size / (1024 ** 3)
    # deal with total size being too large
    if total_size > sizelimit:
        # print warning
        eargs = [total_size, sizelimit]
        emsg = ('Total size of files ({0:.3f} GB) exceeds limit ({1:.3f} GB)')
        WLOG(params, 'error', emsg.format(*eargs))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
