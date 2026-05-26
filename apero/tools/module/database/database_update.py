#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-05-10

@author: cook
"""
import glob
import os
from pathlib import Path
from typing import Any, List, Tuple

import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.time import Time

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_utils
from apero.io import drs_table
from apero.tools.module.database import manage_databases

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'database_update.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get parameter dictionary
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
PseudoConstants = constants.PseudoConstants
# get display func
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# get tqdm (if required)
tqdm = base.tqdm_module()
# Define reference prefix
REF_PREFIX = 'REF_'
# Define the gaia drs column in database
GAIA_COL = 'GAIADR2ID'


# =============================================================================
# Define functions
# =============================================================================
def update_database(params: ParamDict, recipe: DrsRecipe, dbkind: str):
    """
    Update the calib/tellu/log and index databases from files on disk

    :param params: Paramdict, the parameter dictionary of constants
    :param dbkind: str, the type of database (i.e. all, calib, tellu, log etc)
    :return:
    """
    # load pconst
    pconst = constants.pload()

    # update calibration database
    if dbkind in ['calib', 'all']:
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['calibration']),
             colour='magenta')
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        calib_tellu_update(params, pconst, 'calibration')
    # update telluric database
    if dbkind in ['tellu', 'all']:
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['telluric']),
             colour='magenta')
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        calib_tellu_update(params, pconst, 'telluric')
    # update log and index database
    if dbkind in ['log', 'all']:
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['log']),
             colour='magenta')
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        log_update(params, pconst)
    # update index database
    if dbkind in ['findex', 'all']:
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['index']),
             colour='magenta')
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        index_update(params, recipe)

    if dbkind in ['astrom', 'all']:
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['object']),
             colour='magenta')
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        manage_databases.update_object_database(params)

    if dbkind in ['reject', 'all']:
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['reject']),
             colour='magenta')
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        manage_databases.update_reject_database(params)


def reset_databases(params: ParamDict, dbkind):
    """
    Reset all database to installation point

    :param params: ParamDict, parameter dictionary of constants
    :param dbkind: str, the type of database (i.e. all, calib, tellu, log etc)
    :return:
    """
    manage_databases.install_databases(params, dbkind=dbkind, verbose=True)


def calib_tellu_update(params: ParamDict, pconst: PseudoConstants,
                       db_type: str):
    """
    Update either the calibration or telluric database with files on disk

    :param params: Paramdict, the parameter dictionary of constants
    :param pconst: PseudoConst, pseudo constant object
    :param db_type: str, either 'calibration' or 'telluric'

    :return: None updates either calibration or telluric database
    """
    # set function name
    func_name = display_func('calib_tellu_update', __NAME__)
    # ----------------------------------------------------------------------
    # get the settings for each type of database
    if db_type == 'calibration':
        db_path = params['DRS_CALIB_DB']
        name = 'calibration database'
        file_set_name = 'calib_file'
        # load the calibration database
        dbmanager = drs_database.CalibrationDatabase(params)
        dbmanager.load_db()
    elif db_type == 'telluric':
        db_path = params['DRS_TELLU_DB']
        name = 'telluric database'
        file_set_name = 'tellu_file'
        # load the telluric database
        dbmanager = drs_database.TelluricDatabase(params)
        dbmanager.load_db()
    else:
        WLOG(params, 'error', textentry('09-505-00001', args=[db_type]))
        dbmanager = None
        db_path = None
        name = None
        file_set_name = None
    # ----------------------------------------------------------------------
    # get a list of all database paths
    db_list = manage_databases.list_databases(params)
    # backup database
    dbmanager.database.backup()
    # reset database
    if db_type == 'calibration':
        # reset database
        manage_databases.create_calibration_database(params, pconst, db_list)
        # reload the calibration database
        dbmanager = drs_database.CalibrationDatabase(params)
        dbmanager.load_db()
    elif db_type == 'telluric':
        manage_databases.create_telluric_database(params, pconst, db_list)
        # reload the telluric database
        dbmanager = drs_database.TelluricDatabase(params)
        dbmanager.load_db()
    # ----------------------------------------------------------------------
    # get all fits files in the cdb path
    db_files = np.sort(glob.glob(db_path + os.sep + '*.fits'))
    # ----------------------------------------------------------------------
    # get the file mod for this instrument
    filemod = pconst.FILEMOD()
    # ----------------------------------------------------------------------
    # define storage of found files
    db_times = []
    # ----------------------------------------------------------------------
    # loop around all calib files and get the modified times
    for it, db_file in enumerate(db_files):
        # get the modified time of the file
        modtime = os.path.getmtime(db_file)
        # append to db_times
        db_times.append(modtime)
    # ----------------------------------------------------------------------
    # sort by time
    sortmask = np.argsort(db_times)
    db_files = np.array(db_files)[sortmask]
    # convert to list
    db_files = list(db_files)
    # get number of cores
    cores = drs_utils.get_cores(params)
    # use parallel processing if enabled and we have multiple cores
    mp_key = 'REPROCESS_MP_CALIB'
    # log total file count and cores before processing (only if multiprocessing enabled)
    if cores > 1:
        total_files = len(db_files)
        WLOG(params, 'info', 'Running {0} update in multiprocess mode '
             'CORES={1} TOTAL_IT={2}'.format(db_type, cores, total_files))
    if params[mp_key].lower() == 'pathos' and cores > 1:
        _multi_process_calib_tellu_pathos(params, pconst, db_type, file_set_name,
                                          name, func_name, db_files, cores)
    elif params[mp_key].lower() == 'pool' and cores > 1:
        _multi_process_calib_tellu_pool(params, pconst, db_type, file_set_name,
                                        name, func_name, db_files, cores)
    elif params[mp_key].lower() == 'process' and cores > 1:
        _multi_process_calib_tellu_process(params, pconst, db_type, file_set_name,
                                           name, func_name, db_files, cores)
    else:
        # serial processing
        _calib_tellu_update_files(params, pconst, db_type, file_set_name,
                                  name, func_name, db_files)


def index_update(params: ParamDict, recipe: DrsRecipe):
    """
    Update the file index database using multiprocessing if enabled

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance

    :return: None updates index database
    """
    # get all block kinds
    block_kinds = drs_file.DrsPath.get_block_names(params=params,
                                                   block_filter='indexing')
    # get number of cores
    cores = drs_utils.get_cores(params)
    # log total blocks and cores before processing (only if multiprocessing enabled)
    if cores > 1:
        total_blocks = len(block_kinds)
        WLOG(params, 'info', 'Running index update in multiprocess mode '
             'CORES={0} TOTAL_IT={1}'.format(cores, total_blocks))
    # use parallel processing if enabled and we have multiple cores
    mp_key = 'REPROCESS_MP_FINDEX'
    if params[mp_key].lower() == 'pathos' and cores > 1:
        _multi_process_index_pathos(params, block_kinds, cores)
    elif params[mp_key].lower() == 'pool' and cores > 1:
        _multi_process_index_pool(params, block_kinds, cores)
    elif params[mp_key].lower() == 'process' and cores > 1:
        _multi_process_index_process(params, block_kinds, cores)
    else:
        # serial processing
        _index_update_blocks(params, block_kinds)


def log_update(params: ParamDict, pconst: PseudoConstants):
    """
    Update log database using files on disk in block directories flagged as
    "logging" block kinds

    :param params: Paramdict, the parameter dictionary of constants
    :param pconst: PseudoConst, pseudo constant object

    :return: None updates log database
    """
    # get all blocks
    blocks = drs_file.DrsPath.get_blocks(params)
    # get index database
    logdbm = drs_database.LogDatabase(params)
    logdbm.load_db()
    # -------------------------------------------------------------------------
    # loop around blocks
    for block in blocks:
        # skip non logging blocks
        if not block.logging:
            continue
        # ---------------------------------------------------------------------
        # print progress
        msg = 'Updating {0} for log database'
        WLOG(params, '', msg.format(block.name))
        # ---------------------------------------------------------------------
        # get all files
        files = list(Path(block.path).rglob('*.fits'))
        # get number of cores
        cores = drs_utils.get_cores(params)
        # log total file count and cores before processing (only if multiprocessing enabled)
        if cores > 1:
            total_files = len(files)
            WLOG(params, 'info', 'Running log update in multiprocess mode '
                 'CORES={0} TOTAL_IT={1}'.format(cores, total_files))
        # use parallel processing if enabled and we have multiple cores
        if params['REPROCESS_MP_LOGDB'].lower() == 'pathos' and cores > 1:
            logentries, log_pids = _multi_process_logdb_pathos(params, pconst,
                                                                files, cores)
        elif params['REPROCESS_MP_LOGDB'].lower() == 'pool' and cores > 1:
            logentries, log_pids = _multi_process_logdb_pool(params, pconst,
                                                              files, cores)
        elif params['REPROCESS_MP_LOGDB'].lower() == 'process' and cores > 1:
            logentries, log_pids = _multi_process_logdb_process(params, pconst,
                                                                 files, cores)
        else:
            # serial processing
            logentries, log_pids = _log_update_files(params, pconst, files)
        # ---------------------------------------------------------------------
        # loop around unique pids and remove them from log database (we are
        #    updating them now)
        for pid in np.unique(log_pids):
            # remove pids
            logdbm.remove_pids(pid)
        # ---------------------------------------------------------------------
        # add unique entries to log database
        for lcode in logentries:
            # add this entry
            logdbm.add_entries(*logentries[lcode])


# =============================================================================
# Define worker functions
# =============================================================================
def _calib_tellu_update_files(params: ParamDict, pconst: PseudoConstants,
                              db_type: str, file_set_name: str,
                              name: str, func_name: str,
                              db_files: List) -> None:
    """
    Process a list of database files serially and update the database

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param db_type: str, either 'calibration' or 'telluric'
    :param file_set_name: str, the file set name ('calib_file' or 'tellu_file')
    :param name: str, display name ('calibration database' or 'telluric database')
    :param func_name: str, function name for logging
    :param db_files: List, list of database file paths to process

    :return: None
    """
    # get the file mod for this instrument
    filemod = pconst.FILEMOD()
    # load the database
    if db_type == 'calibration':
        dbmanager = drs_database.CalibrationDatabase(params)
    elif db_type == 'telluric':
        dbmanager = drs_database.TelluricDatabase(params)
    else:
        return
    dbmanager.load_db()
    # loop around all database files and try to find the kinds
    for it in tqdm(range(len(db_files))):
        # get db_file
        db_file = db_files[it]
        # log progress
        wargs = [it + 1, len(db_files), os.path.basename(db_file)]
        WLOG(params, 'debug', textentry('40-505-00001', args=wargs))
        # get file set
        if not hasattr(filemod.get(), file_set_name):
            eargs = [name, file_set_name, filemod.get(), func_name]
            WLOG(params, 'error', textentry('00-505-00001', args=eargs))
            file_set = None
        else:
            file_set = getattr(filemod.get(), file_set_name)
        # skip default reference files
        if os.path.basename(db_file).startswith(REF_PREFIX):
            # log skipping
            wargs = [REF_PREFIX]
            WLOG(params, 'debug', textentry('40-505-00003', args=wargs))
            # skip
            continue
        # make a new copy of out_file
        db_out_file = file_set.newcopy(params=params)
        # try to find db_file
        found, kind = drs_file.id_drs_file(params, db_out_file,
                                           filename=db_file, nentries=1,
                                           required=False)
        # append to cdb_data
        if found:
            # log that we found file
            WLOG(params, 'debug', textentry('40-505-00002', args=[kind]))
            # add the files back to the database
            if db_type == 'calibration':
                dbmanager.add_calib_file(kind, copy_files=False, verbose=False)
            elif db_type == 'telluric':
                dbmanager.add_tellu_file(kind, copy_files=False, verbose=False)
        # delete file
        del kind, db_out_file


def _calib_tellu_update_files_batch(params: ParamDict, pconst: PseudoConstants,
                                    db_type: str, file_set_name: str,
                                    name: str, func_name: str,
                                    db_files: List, batch_idx: int = None,
                                    total_batches: int = None) -> None:
    """
    Process a batch of database files and update the database

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param db_type: str, either 'calibration' or 'telluric'
    :param file_set_name: str, the file set name ('calib_file' or 'tellu_file')
    :param name: str, display name ('calibration database' or 'telluric database')
    :param func_name: str, function name for logging
    :param db_files: List, list of database file paths to process
    :param batch_idx: int, the batch index (for logging)
    :param total_batches: int, the total number of batches (for logging)

    :return: None
    """
    # get the file mod for this instrument
    filemod = pconst.FILEMOD()
    # load the database
    if db_type == 'calibration':
        dbmanager = drs_database.CalibrationDatabase(params)
    elif db_type == 'telluric':
        dbmanager = drs_database.TelluricDatabase(params)
    else:
        return
    dbmanager.load_db()
    # start a message if batch_idx and total_batches given
    if (batch_idx is not None) and (total_batches is not None):
        batch_msg = ' [{0}/{1}] '.format(batch_idx, total_batches)
    else:
        batch_msg = ''
    # loop around all database files and try to find the kinds
    for it in tqdm(range(len(db_files)), desc='Calib DB batch' + batch_msg):
        # get db_file
        db_file = db_files[it]
        # log progress
        wargs = [it + 1, len(db_files), os.path.basename(db_file)]
        WLOG(params, 'debug', textentry('40-505-00001', args=wargs))
        # get file set
        if not hasattr(filemod.get(), file_set_name):
            eargs = [name, file_set_name, filemod.get(), func_name]
            WLOG(params, 'error', textentry('00-505-00001', args=eargs))
            file_set = None
        else:
            file_set = getattr(filemod.get(), file_set_name)
        # skip default reference files
        if os.path.basename(db_file).startswith(REF_PREFIX):
            # log skipping
            wargs = [REF_PREFIX]
            WLOG(params, 'debug', textentry('40-505-00003', args=wargs))
            # skip
            continue
        # make a new copy of out_file
        db_out_file = file_set.newcopy(params=params)
        # try to find db_file
        found, kind = drs_file.id_drs_file(params, db_out_file,
                                           filename=db_file, nentries=1,
                                           required=False)
        # append to cdb_data
        if found:
            # log that we found file
            WLOG(params, 'debug', textentry('40-505-00002', args=[kind]))
            # add the files back to the database
            if db_type == 'calibration':
                dbmanager.add_calib_file(kind, copy_files=False, verbose=False)
            elif db_type == 'telluric':
                dbmanager.add_tellu_file(kind, copy_files=False, verbose=False)
        # delete file
        del kind, db_out_file


def _multi_process_calib_tellu_pathos(params: ParamDict, pconst: PseudoConstants,
                                      db_type: str, file_set_name: str,
                                      name: str, func_name: str,
                                      db_files: List, cores: int) -> None:
    """
    Process database files via pathos.Pool.map, batching into Ncores groups

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param db_type: str, either 'calibration' or 'telluric'
    :param file_set_name: str, the file set name
    :param name: str, display name
    :param func_name: str, function name for logging
    :param db_files: List, list of database file paths
    :param cores: int, the number of cores to use

    :return: None
    """
    # deal with Pool specific imports
    from pathos.pools import ParallelPool as Pool
    # set up the pool
    pool = Pool(ncpus=cores, maxtasksperchild=1)
    # split files into N=cores groups
    cores = min(cores, len(db_files))
    chunk_size = int(np.ceil(len(db_files) / cores))
    grouped_files = [db_files[i:i + chunk_size]
                     for i in range(0, len(db_files), chunk_size)]
    # list of params for each entry
    params_per_process = []
    # populate params for each sub group
    for f_it, grouped_file in enumerate(grouped_files):
        args = [params, pconst, db_type, file_set_name, name, func_name,
                grouped_file, f_it + 1, len(grouped_files)]
        params_per_process.append(args)
    # transpose the params axis
    params_per_process2 = list(zip(*params_per_process))
    # start parallel jobs
    pool.map(_calib_tellu_update_files_batch, *params_per_process2)
    # close the pool
    pool.close()
    pool.join()


def _multi_process_calib_tellu_pool(params: ParamDict, pconst: PseudoConstants,
                                    db_type: str, file_set_name: str,
                                    name: str, func_name: str,
                                    db_files: List, cores: int) -> None:
    """
    Process database files via multiprocessing.Pool.starmap, batching into
    Ncores groups

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param db_type: str, either 'calibration' or 'telluric'
    :param file_set_name: str, the file set name
    :param name: str, display name
    :param func_name: str, function name for logging
    :param db_files: List, list of database file paths
    :param cores: int, the number of cores to use

    :return: None
    """
    # deal with Pool specific imports
    from multiprocessing import get_context
    # split files into N=cores groups
    cores = min(cores, len(db_files))
    chunk_size = int(np.ceil(len(db_files) / cores))
    grouped_files = [db_files[i:i + chunk_size]
                     for i in range(0, len(db_files), chunk_size)]
    # list of params for each entry
    params_per_process = []
    # populate params for each sub group
    for f_it, grouped_file in enumerate(grouped_files):
        args = [params, pconst, db_type, file_set_name, name, func_name,
                grouped_file, f_it + 1, len(grouped_files)]
        params_per_process.append(args)
    # start parallel jobs
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        pool.starmap(_calib_tellu_update_files_batch, params_per_process)


def _multi_process_calib_tellu_process(params: ParamDict, pconst: PseudoConstants,
                                       db_type: str, file_set_name: str,
                                       name: str, func_name: str,
                                       db_files: List, cores: int) -> None:
    """
    Process database files via multiprocessing.Process, batching into Ncores
    groups

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param db_type: str, either 'calibration' or 'telluric'
    :param file_set_name: str, the file set name
    :param name: str, display name
    :param func_name: str, function name for logging
    :param db_files: List, list of database file paths
    :param cores: int, the number of cores to use

    :return: None
    """
    # import multiprocessing
    from multiprocessing import Process
    # split files into N=cores groups
    cores = min(cores, len(db_files))
    chunk_size = int(np.ceil(len(db_files) / cores))
    grouped_files = [db_files[i:i + chunk_size]
                     for i in range(0, len(db_files), chunk_size)]
    # process storage
    jobs = []
    # loop around each batch
    for f_it, grouped_file in enumerate(grouped_files):
        # get the arguments for this group
        args = (params, pconst, db_type, file_set_name, name, func_name,
                grouped_file, f_it + 1, len(grouped_files))
        # create and start process
        process = Process(target=_calib_tellu_update_files_batch, args=args)
        process.start()
        jobs.append(process)
    # wait for all processes to complete
    for job in jobs:
        job.join()


def _index_update_blocks(params: ParamDict, block_kinds: List) -> None:
    """
    Process a list of block kinds serially and update the index database

    :param params: ParamDict, parameter dictionary of constants
    :param block_kinds: List, list of block kind strings to process

    :return: None
    """
    # get index database
    findexdbm = drs_database.FileIndexDatabase(params)
    findexdbm.load_db()
    # get astrometric database
    astromdb = drs_database.AstrometricDatabase(params)
    astromdb.load_db()
    # loop around block kinds (with the indexing filter)
    for block_kind in block_kinds:
        # log block update
        WLOG(params, '', textentry('40-503-00044', args=[block_kind]))
        # update index database for block kind
        findexdbm = drs_utils.update_index_db(params, block_kind=block_kind,
                                              findexdbm=findexdbm)
        # update headers of raw files
        if block_kind == 'raw':
            # fix the headers
            findexdbm.update_header_fix(objdbm=astromdb)


def _index_update_blocks_batch(params: ParamDict, block_kinds: List,
                               batch_idx: int = None,
                               total_batches: int = None) -> None:
    """
    Process a batch of block kinds and update the index database

    :param params: ParamDict, parameter dictionary of constants
    :param block_kinds: List, list of block kind strings to process
    :param batch_idx: int, the batch index (for logging)
    :param total_batches: int, the total number of batches (for logging)

    :return: None
    """
    # get index database
    findexdbm = drs_database.FileIndexDatabase(params)
    findexdbm.load_db()
    # get astrometric database
    astromdb = drs_database.AstrometricDatabase(params)
    astromdb.load_db()
    # start a message if batch_idx and total_batches given
    if (batch_idx is not None) and (total_batches is not None):
        batch_msg = ' [{0}/{1}] '.format(batch_idx, total_batches)
    else:
        batch_msg = ''
    # loop around block kinds (with the indexing filter)
    for block_kind in tqdm(block_kinds, desc='Index DB batch' + batch_msg):
        # log block update
        WLOG(params, '', textentry('40-503-00044', args=[block_kind]))
        # update index database for block kind
        findexdbm = drs_utils.update_index_db(params, block_kind=block_kind,
                                              findexdbm=findexdbm)
        # update headers of raw files
        if block_kind == 'raw':
            # fix the headers
            findexdbm.update_header_fix(objdbm=astromdb)


def _multi_process_index_pathos(params: ParamDict, block_kinds: List,
                                cores: int) -> None:
    """
    Process block kinds via pathos.Pool.map, batching into Ncores groups

    :param params: ParamDict, parameter dictionary of constants
    :param block_kinds: List, list of block kind strings
    :param cores: int, the number of cores to use

    :return: None
    """
    # deal with Pool specific imports
    from pathos.pools import ParallelPool as Pool
    # set up the pool
    pool = Pool(ncpus=cores, maxtasksperchild=1)
    # split block_kinds into N=cores groups
    cores = min(cores, len(block_kinds))
    chunk_size = int(np.ceil(len(block_kinds) / cores))
    grouped_kinds = [block_kinds[i:i + chunk_size]
                     for i in range(0, len(block_kinds), chunk_size)]
    # list of params for each entry
    params_per_process = []
    # populate params for each sub group
    for k_it, grouped_kind in enumerate(grouped_kinds):
        args = [params, grouped_kind, k_it + 1, len(grouped_kinds)]
        params_per_process.append(args)
    # transpose the params axis
    params_per_process2 = list(zip(*params_per_process))
    # start parallel jobs
    pool.map(_index_update_blocks_batch, *params_per_process2)
    # close the pool
    pool.close()
    pool.join()


def _multi_process_index_pool(params: ParamDict, block_kinds: List,
                              cores: int) -> None:
    """
    Process block kinds via multiprocessing.Pool.starmap, batching into
    Ncores groups

    :param params: ParamDict, parameter dictionary of constants
    :param block_kinds: List, list of block kind strings
    :param cores: int, the number of cores to use

    :return: None
    """
    # deal with Pool specific imports
    from multiprocessing import get_context
    # split block_kinds into N=cores groups
    cores = min(cores, len(block_kinds))
    chunk_size = int(np.ceil(len(block_kinds) / cores))
    grouped_kinds = [block_kinds[i:i + chunk_size]
                     for i in range(0, len(block_kinds), chunk_size)]
    # list of params for each entry
    params_per_process = []
    # populate params for each sub group
    for k_it, grouped_kind in enumerate(grouped_kinds):
        args = [params, grouped_kind, k_it + 1, len(grouped_kinds)]
        params_per_process.append(args)
    # start parallel jobs
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        pool.starmap(_index_update_blocks_batch, params_per_process)


def _multi_process_index_process(params: ParamDict, block_kinds: List,
                                 cores: int) -> None:
    """
    Process block kinds via multiprocessing.Process, batching into Ncores
    groups

    :param params: ParamDict, parameter dictionary of constants
    :param block_kinds: List, list of block kind strings
    :param cores: int, the number of cores to use

    :return: None
    """
    # import multiprocessing
    from multiprocessing import Process
    # split block_kinds into N=cores groups
    cores = min(cores, len(block_kinds))
    chunk_size = int(np.ceil(len(block_kinds) / cores))
    grouped_kinds = [block_kinds[i:i + chunk_size]
                     for i in range(0, len(block_kinds), chunk_size)]
    # process storage
    jobs = []
    # loop around each batch
    for k_it, grouped_kind in enumerate(grouped_kinds):
        # get the arguments for this group
        args = (params, grouped_kind, k_it + 1, len(grouped_kinds))
        # create and start process
        process = Process(target=_index_update_blocks_batch, args=args)
        process.start()
        jobs.append(process)
    # wait for all processes to complete
    for job in jobs:
        job.join()


def _log_update_files(params: ParamDict, pconst: PseudoConstants,
                      files: List) -> Tuple[dict, List]:
    """
    Process a list of files serially and extract log update entries

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param files: List, list of file paths to process

    :return: Tuple, 1. dict of logentries, 2. list of log_pids
    """
    # storage for unique logcodes
    logentries, log_pids = dict(), []
    # loop around files
    for filepath in tqdm(files):
        # get string version
        filename = str(filepath)
        # get all log update entries (per file)
        log_result = _get_log_update_entry(params, pconst, filename)
        if log_result is None:
            continue
        logdict, lcode, lpid = log_result
        # merge duplicate lcodes (same PID/LEVEL/SUBLEVEL) rather than
        # silently overwriting – products from the same run can differ in
        # QC fields such as PASSED_ALL_QC
        if lcode in logentries:
            logentries[lcode] = _combine_log_entries(pconst,
                                                     logentries[lcode],
                                                     logdict)
        else:
            logentries[lcode] = logdict
        # append to pids
        log_pids.append(lpid)
    # return results
    return logentries, log_pids


def _log_update_files_batch(params: ParamDict, pconst: PseudoConstants,
                            files: List, batch_idx: int = None,
                            total_batches: int = None) -> Tuple[dict, List]:
    """
    Process a batch of files and extract log update entries

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param files: List, list of file paths to process
    :param batch_idx: int, the batch index (for logging)
    :param total_batches: int, the total number of batches (for logging)

    :return: Tuple, 1. dict of logentries, 2. list of log_pids
    """
    # storage for unique logcodes
    logentries, log_pids = dict(), []
    # start a message if batch_idx and total_batches given
    if (batch_idx is not None) and (total_batches is not None):
        batch_msg = ' [{0}/{1}] '.format(batch_idx, total_batches)
    else:
        batch_msg = ''
    # loop around files
    for filepath in tqdm(files, desc='Log DB batch' + batch_msg):
        # get string version
        filename = str(filepath)
        # get all log update entries (per file)
        log_result = _get_log_update_entry(params, pconst, filename)
        if log_result is None:
            continue
        logdict, lcode, lpid = log_result
        # merge duplicate lcodes (same PID/LEVEL/SUBLEVEL) rather than
        # silently overwriting – products from the same run can differ in
        # QC fields such as PASSED_ALL_QC
        if lcode in logentries:
            logentries[lcode] = _combine_log_entries(pconst,
                                                     logentries[lcode],
                                                     logdict)
        else:
            logentries[lcode] = logdict
        # append to pids
        log_pids.append(lpid)
    # return results
    return logentries, log_pids


def _multi_process_logdb_pathos(params: ParamDict, pconst: PseudoConstants,
                                files: List, cores: int) -> Tuple[dict, List]:
    """
    Process files via pathos.Pool.map, batching files into Ncores groups

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param files: List, list of file paths to process
    :param cores: int, the number of cores to use

    :return: Tuple, 1. dict of logentries, 2. list of log_pids
    """
    # deal with Pool specific imports
    from pathos.pools import ParallelPool as Pool
    # set up the pool
    pool = Pool(ncpus=cores, maxtasksperchild=1)
    # split files into N=cores groups
    cores = min(cores, len(files))
    chunk_size = int(np.ceil(len(files) / cores))
    grouped_files = [files[i:i + chunk_size]
                     for i in range(0, len(files), chunk_size)]
    # list of params for each entry
    params_per_process = []
    # populate params for each sub group
    for f_it, grouped_file in enumerate(grouped_files):
        args = [params, pconst, grouped_file, f_it + 1, len(grouped_files)]
        params_per_process.append(args)
    # transpose the params axis
    params_per_process2 = list(zip(*params_per_process))
    # start parallel jobs
    results = pool.map(_log_update_files_batch, *params_per_process2)
    # close the pool
    pool.close()
    pool.join()
    # merge results from all batches – use _merge_log_entries so that
    # entries with the same PID/LEVEL/SUBLEVEL across batches are combined
    # correctly (e.g. PASSED_ALL_QC takes the logical AND) rather than
    # silently overwritten
    logentries, log_pids = dict(), []
    for batch_logentries, batch_log_pids in results:
        for lcode, entry in batch_logentries.items():
            if lcode in logentries:
                logentries[lcode] = _combine_log_entries(pconst,
                                                         logentries[lcode],
                                                         entry)
            else:
                logentries[lcode] = entry
        log_pids.extend(batch_log_pids)
    # return merged results
    return logentries, log_pids


def _multi_process_logdb_pool(params: ParamDict, pconst: PseudoConstants,
                              files: List, cores: int) -> Tuple[dict, List]:
    """
    Process files via multiprocessing.Pool.starmap, batching files into Ncores
    groups

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param files: List, list of file paths to process
    :param cores: int, the number of cores to use

    :return: Tuple, 1. dict of logentries, 2. list of log_pids
    """
    # deal with Pool specific imports
    from multiprocessing import get_context
    # split files into N=cores groups
    cores = min(cores, len(files))
    chunk_size = int(np.ceil(len(files) / cores))
    grouped_files = [files[i:i + chunk_size]
                     for i in range(0, len(files), chunk_size)]
    # list of params for each entry
    params_per_process = []
    # populate params for each sub group
    for f_it, grouped_file in enumerate(grouped_files):
        args = [params, pconst, grouped_file, f_it + 1, len(grouped_files)]
        params_per_process.append(args)
    # start parallel jobs
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        results = pool.starmap(_log_update_files_batch, params_per_process)
    # merge results from all batches – use _merge_log_entries so that
    # entries with the same PID/LEVEL/SUBLEVEL across batches are combined
    # correctly (e.g. PASSED_ALL_QC takes the logical AND) rather than
    # silently overwritten
    logentries, log_pids = dict(), []
    for batch_logentries, batch_log_pids in results:
        for lcode, entry in batch_logentries.items():
            if lcode in logentries:
                logentries[lcode] = _combine_log_entries(pconst,
                                                         logentries[lcode],
                                                         entry)
            else:
                logentries[lcode] = entry
        log_pids.extend(batch_log_pids)
    # return merged results
    return logentries, log_pids


def _multi_process_logdb_process(params: ParamDict, pconst: PseudoConstants,
                                 files: List, cores: int) -> Tuple[dict, List]:
    """
    Process files via multiprocessing.Process, batching files into Ncores
    groups

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param files: List, list of file paths to process
    :param cores: int, the number of cores to use

    :return: Tuple, 1. dict of logentries, 2. list of log_pids
    """
    # import multiprocessing
    from multiprocessing import Process, Manager
    # split files into N=cores groups
    cores = min(cores, len(files))
    chunk_size = int(np.ceil(len(files) / cores))
    grouped_files = [files[i:i + chunk_size]
                     for i in range(0, len(files), chunk_size)]
    # create a manager for shared data
    manager = Manager()
    results_list = manager.list()
    # process storage
    jobs = []
    # loop around each batch
    for f_it, grouped_file in enumerate(grouped_files):
        # get the arguments for this group
        args = (params, pconst, grouped_file, f_it + 1, len(grouped_files),
                results_list)
        # create and start process
        process = Process(target=_log_update_files_batch_process,
                          args=args)
        process.start()
        jobs.append(process)
    # wait for all processes to complete
    for job in jobs:
        job.join()
    # merge results from all batches – use _merge_log_entries so that
    # entries with the same PID/LEVEL/SUBLEVEL across batches are combined
    # correctly (e.g. PASSED_ALL_QC takes the logical AND) rather than
    # silently overwritten
    logentries, log_pids = dict(), []
    for batch_logentries, batch_log_pids in results_list:
        for lcode, entry in batch_logentries.items():
            if lcode in logentries:
                logentries[lcode] = _combine_log_entries(pconst,
                                                         logentries[lcode],
                                                         entry)
            else:
                logentries[lcode] = entry
        log_pids.extend(batch_log_pids)
    # return merged results
    return logentries, log_pids


def _log_update_files_batch_process(params: ParamDict, pconst: PseudoConstants,
                                    files: List, batch_idx: int,
                                    total_batches: int,
                                    results_list: List) -> None:
    """
    Process a batch of files for multiprocessing.Process and append results
    to shared list

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param files: List, list of file paths to process
    :param batch_idx: int, the batch index
    :param total_batches: int, the total number of batches
    :param results_list: List, shared list to append results to

    :return: None (appends to results_list)
    """
    # process the batch
    logentries, log_pids = _log_update_files_batch(params, pconst, files,
                                                   batch_idx, total_batches)
    # append results to shared list
    results_list.append((logentries, log_pids))


def _get_log_update_entry(params: ParamDict, pconst: PseudoConstants,
                          filename: str):
    """
    Get the log database payload for a file.

    Normal APERO products use the PARAM_TABLE. For older/special FITS files
    without that extension we synthesize a minimal log entry from the header so
    that the file still has a usable PID/PASSED_ALL_QC record in the log
    database.

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param filename: str, absolute path to a FITS file

    :return: tuple or None, (logvalues, logcode, pid) when a payload can be
             created, otherwise None
    """
    with fits.open(filename) as hdus:
        hdu_names = list(map(lambda x: x.name, hdus))
        if 'PARAM_TABLE' in hdu_names:
            ptable = drs_table.read_table(params, filename, fmt='fits',
                                          hdu='PARAM_TABLE')
            return _log_update(pconst, ptable)
        return _log_update_from_header(params, pconst, filename,
                                       hdus[0].header)


def _log_update_from_header(params: ParamDict, pconst: PseudoConstants,
                            filename: str,
                            header: fits.Header) -> Tuple[List[Any], str, str]:
    """
    Synthesize a minimal log database entry from FITS header keywords when a
    file has no PARAM_TABLE extension.

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param filename: str, absolute path to a FITS file
    :param header: fits.Header, the primary FITS header

    :return: tuple, 1. list of log entry values, 2. str unique log code,
             3. str pid
    """
    # get the log database columns
    ldb_cols = pconst.LOG_DB_COLUMNS()
    logcols = list(ldb_cols.names)
    # get the block kind from the filename
    block_kind = _get_log_block_kind(params, filename)
    # define keys for the header
    pid_key = params.instances['KW_PID'].key
    date_key = params.instances['KW_DRS_DATE_NOW'].key
    # get the pid from the header (if it exists)
    pid = header.get(pid_key, None)
    # get the human time from the header (if it exists)
    humantime = header.get(date_key, None)
    # get the basename of the file
    basename = os.path.basename(filename)
    # deal with no PID
    if pid in [None, '', 'NULL']:
        pid = 'MISSINGPID::{0}'.format(basename)
    # format the human time and get unix time
    humantime, unixtime = _get_log_header_times(filename, humantime)
    # push default values into the log database
    defaults = dict(RECIPE='apero_database', SHORTNAME='DBUPDATE',
                    BLOCK_KIND=block_kind, RECIPE_TYPE='unknown',
                    RECIPE_KIND='unknown', PROGRAM_NAME='unknown', PID=pid,
                    HUMANTIME=humantime, UNIXTIME=unixtime,
                    GROUPNAME='unknown', LEVEL=0, SUBLEVEL=0,
                    LEVELCRIT='unknown', INPATH='unknown',
                    OUTPATH=basename, OBS_DIR='unknown',
                    LOGFILE='unknown', PLOTDIR='unknown',
                    RUNSTRING='apero_database.py --update --dbkind=log',
                    ARGS='unknown', KWARGS=f'--filename={filename}',
                    SKWARGS='unknown',
                    START_TIME=humantime, END_TIME=humantime, STARTED=1,
                    PASSED_ALL_QC=1, QC_STRING='', QC_NAMES='', QC_VALUES='',
                    QC_LOGIC='', QC_PASS='', ERRORMSGS='', ENDED=1,
                    FLAGNUM=0, FLAGSTR='', USED=1, RAM_USAGE_START=0.0,
                    RAM_USAGE_END=0.0, RAW_TOTAL=0.0, SWAP_USAGE_START=0.0,
                    SWAP_USAGE_END=0.0, SWAP_TOTAL=0.0,
                    CPU_USAGE_START=0.0, CPU_USAGE_END=0.0, CPU_NUM=0,
                    LOG_START=humantime, LOG_END=humantime)
    # loop around default values and add them as a list
    logvalues = []
    for logkey in logcols:
        logvalues.append(defaults.get(logkey, 'NULL'))
    # default log code
    logcode = '{0} 0 0'.format(pid)
    # return same outputs as _log_update
    return logvalues, logcode, pid


def _get_log_header_times(filename: str, humantime: Any) -> Tuple[str, float]:
    """
    Derive a stable HUMANTIME/UNIXTIME pair for header-synthesized log rows.

    :param filename: str, file path used for file-system fallback times
    :param humantime: Any, candidate human-readable time from FITS header

    :return: tuple, 1. HUMANTIME string, 2. UNIXTIME float
    """
    parsed_time = None
    if humantime not in [None, '', 'NULL']:
        humantime = str(humantime)
        for timefmt in ['iso', 'isot', 'fits']:
            try:
                parsed_time = Time(humantime, format=timefmt)
                break
            except Exception:
                continue
        if parsed_time is None:
            try:
                parsed_time = Time(humantime)
            except Exception:
                parsed_time = None

    if parsed_time is None:
        parsed_time = Time(os.path.getmtime(filename), format='unix')

    return parsed_time.iso, float(parsed_time.unix)


def _get_log_block_kind(params: ParamDict, filename: str) -> str:
    """
    Resolve the block kind for a file from its absolute path.

    :param params: ParamDict, parameter dictionary of constants
    :param filename: str, absolute file path

    :return: str, the block name or 'unknown' if no block matches
    """
    abspath = os.path.abspath(filename)
    matched_block, matched_length = 'unknown', -1

    for block in drs_file.DrsPath.get_blocks(params, check=False):
        blockpath = os.path.abspath(block.path)
        try:
            commonpath = os.path.commonpath([abspath, blockpath])
        except ValueError:
            continue
        if commonpath == blockpath and len(blockpath) > matched_length:
            matched_block = block.name
            matched_length = len(blockpath)

    return matched_block


def _combine_log_entries(pconst: PseudoConstants,
                         existing: List[Any],
                         new: List[Any]) -> List[Any]:
    """
    Combine two log entries with special handling for synthesized fallback
    rows created from headers when PARAM_TABLE is missing.

    For synthesized rows we keep only the newest UNIXTIME for a given
    PID/LEVEL/SUBLEVEL. For normal PARAM_TABLE rows we preserve the existing QC
    merge rules.

    :param pconst: PseudoConst, pseudo constant object
    :param existing: List, log entry values already stored for this logcode
    :param new: List, log entry values from the current file

    :return: List, combined log entry values
    """
    existing_fallback = _is_header_log_entry(pconst, existing)
    new_fallback = _is_header_log_entry(pconst, new)

    if existing_fallback and new_fallback:
        return _select_newer_log_entry(pconst, existing, new)
    if existing_fallback and not new_fallback:
        return list(new)
    if new_fallback and not existing_fallback:
        return list(existing)
    return _merge_log_entries(pconst, existing, new)


def _is_header_log_entry(pconst: PseudoConstants, entry: List[Any]) -> bool:
    """
    Identify synthesized log rows created by `_log_update_from_header`.

    :param pconst: PseudoConst, pseudo constant object
    :param entry: List, log entry values

    :return: bool, True when the entry is a synthesized fallback row
    """
    ldb_cols = pconst.LOG_DB_COLUMNS()
    logcols = list(ldb_cols.names)

    def _value(key: str, default: Any = None) -> Any:
        if key not in logcols:
            return default
        return entry[logcols.index(key)]

    return (_value('RECIPE') == 'apero_database'
            and _value('SHORTNAME') == 'DBUPDATE'
            and _value('RUNSTRING') == 'apero_database.py --update --dbkind=log'
            and str(_value('LEVEL', '0')) == '0'
            and str(_value('SUBLEVEL', '0')) == '0')


def _select_newer_log_entry(pconst: PseudoConstants,
                            existing: List[Any],
                            new: List[Any]) -> List[Any]:
    """
    Select the entry with the newest UNIXTIME.

    :param pconst: PseudoConst, pseudo constant object
    :param existing: List, existing log entry values
    :param new: List, new log entry values

    :return: List, whichever entry is newest
    """
    ldb_cols = pconst.LOG_DB_COLUMNS()
    logcols = list(ldb_cols.names)

    if 'UNIXTIME' not in logcols:
        return list(new)

    idx = logcols.index('UNIXTIME')

    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return float('-inf')

    if _to_float(new[idx]) >= _to_float(existing[idx]):
        return list(new)
    return list(existing)


def _merge_log_entries(pconst: PseudoConstants,
                       existing: List[Any],
                       new: List[Any]) -> List[Any]:
    """
    Merge two log entry value-lists that share the same PID/LEVEL/SUBLEVEL
    (i.e. the same logcode) but may differ in QC-related fields.

    Multiple output files produced by a single recipe run carry identical
    PARAM_TABLEs except that fields such as PASSED_ALL_QC / QC_* can vary
    per-product.  Silently overwriting the first entry with the last one
    (the previous behaviour) is wrong — the merge rules below preserve the
    most conservative / most informative state:

      * PASSED_ALL_QC  – logical AND (min): one failure marks the whole run
      * QC_STRING / QC_NAMES / QC_VALUES / QC_LOGIC / QC_PASS
                       – if the new entry failed while the existing one passed,
                         adopt the new entry's strings so the failure is
                         visible; if both failed, concatenate with ' | '
      * ERRORMSGS      – concatenate distinct messages with ' | '
      * all other cols – keep the value from the first (existing) entry

    :param pconst: PseudoConst, pseudo constant object
    :param existing: List, log entry values already stored for this logcode
    :param new: List, log entry values from the current file

    :return: List, merged log entry values
    """
    ldb_cols = pconst.LOG_DB_COLUMNS()
    logcols = list(ldb_cols.names)

    # start with the existing entry as the base
    merged = list(existing)

    # columns whose strings should be combined when QC differs
    qc_str_fields = {'QC_STRING', 'QC_NAMES', 'QC_VALUES', 'QC_LOGIC',
                     'QC_PASS'}

    # ------------------------------------------------------------------
    # locate PASSED_ALL_QC index — if absent we cannot merge meaningfully
    # ------------------------------------------------------------------
    if 'PASSED_ALL_QC' not in logcols:
        return merged
    qc_idx = logcols.index('PASSED_ALL_QC')

    def _to_int(val: Any, default: int = 0) -> int:
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    existing_passed = _to_int(existing[qc_idx], default=1)
    new_passed = _to_int(new[qc_idx], default=1)

    # logical AND: one failure is enough to mark the whole run as failed
    merged[qc_idx] = min(existing_passed, new_passed)

    # ------------------------------------------------------------------
    # QC string fields
    # ------------------------------------------------------------------
    for field in qc_str_fields:
        if field not in logcols:
            continue
        idx = logcols.index(field)
        ev = str(existing[idx]) if existing[idx] not in ('NULL', None, '') else ''
        nv = str(new[idx]) if new[idx] not in ('NULL', None, '') else ''

        if new_passed == 0 and existing_passed == 1:
            # new entry failed, existing passed → use new strings so the
            # failure reason is recorded
            merged[idx] = new[idx]
        elif new_passed == 0 and existing_passed == 0:
            # both failed → concatenate distinct strings
            if ev and nv and ev != nv:
                merged[idx] = ev + ' | ' + nv
            elif nv:
                merged[idx] = new[idx]
        # else new_passed == 1: existing info is already correct or failing,
        # keep merged (= existing) value unchanged

    # ------------------------------------------------------------------
    # ERRORMSGS – always concatenate distinct messages
    # ------------------------------------------------------------------
    if 'ERRORMSGS' in logcols:
        err_idx = logcols.index('ERRORMSGS')
        ev = str(existing[err_idx]) if existing[err_idx] not in ('NULL', None, '') else ''
        nv = str(new[err_idx]) if new[err_idx] not in ('NULL', None, '') else ''
        if nv and nv not in ev:
            merged[err_idx] = (ev + ' | ' + nv).strip(' | ') if ev else nv

    return merged


def _log_update(pconst: PseudoConstants,
                ptable: Table) -> Tuple[List[Any], str, str]:
    """
    Get a log entry for individual file - may not be unique so must be filtered
    for uniqueness using the lcode string (returned)

    :param pconst: PseudoConst, pseudo constant object
    :param ptable: Table,  the parameter snapshot table (usually last extension)

    :return: Tuple, 1. list of log entry values, 2. str, the unique log code
             to test for unique log entries (files may share same log entry),
             3. str, the pid, unique pids should be remove before adding new
             entries
    """
    # log entry mask
    logmask = ptable['KIND'] == 'rlog'
    # push into a dictionary (for easy access)
    logdict = dict()
    # loop around keys in ptable and convert to dictionary
    for row, key in enumerate(ptable[logmask]['NAME']):
        logdict[key] = ptable[logmask]['VALUE'][row]
    # get log keys and types
    ldb_cols = pconst.LOG_DB_COLUMNS()
    logcols = list(ldb_cols.names)
    # loop around log keys and add them to values
    logvalues = []
    for l_it, logkey in enumerate(logcols):
        # construct keys
        key = 'rlog.{0}'.format(logkey)
        # get value
        logvalue = logdict.get(key, 'NULL')
        # by definition these must have ended (even if the ptable says
        #     otherwise)
        if logkey == 'ENDED':
            logvalue = 1
        # Need to convert boolean strings to int for database storage
        if logvalue in ['True', 'False'] and ldb_cols.dtypes[l_it] is int:
            logvalue = int(logvalue == 'True')
        # append value to values
        logvalues.append(logvalue)
    # generate unique log code
    largs = [logdict['rlog.PID'], logdict['rlog.LEVEL'],
             logdict['rlog.SUBLEVEL']]
    logcode = '{0} {1} {2}'.format(*largs)
    # return the log values and the log code
    return logvalues, logcode, logdict['rlog.PID']


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
