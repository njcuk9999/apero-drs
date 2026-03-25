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

from aperocore.base import base
from aperocore import drs_lang
from aperocore.core import drs_misc
from aperocore.core import drs_text
from aperocore.constants import load_functions
from aperocore.constants import param_functions
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.instruments.default import instrument as instrument_mod
from apero.utils import drs_recipe
from apero.utils import drs_utils
from apero.io import drs_table
from apero.tools.module.database import manage_databases
from apero.instruments import select
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'database_update.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# get parameter dictionary
ParamDict = param_functions.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
Instrument = instrument_mod.Instrument
# get display func
display_func = drs_misc.display_func
# Get the text types
textentry = drs_lang.textentry
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
    :param recipe: DrsRecipe, the recipe instance
    :param dbkind: str, the type of database (i.e. all, calib, tellu, log etc)
    :return:
    """
    # load pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)

    # update calibration database
    if dbkind in ['calib', 'all']:

        # deal with removal of entries
        if dbkind == 'calib':
            remove = remove_db_entries(params, recipe, 'calibration')
            # we do not continue if we are removing entries
            if remove:
                return
        # otherwise we update full calibration database
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['calibration']),
             colour='magenta')
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        calib_tellu_update(params, recipe, pconst, 'calibration')
    # update telluric database
    if dbkind in ['tellu', 'all']:
        # deal with removal of entries
        if dbkind == 'tellu':
            remove = remove_db_entries(params, recipe, 'telluric')
            # we do not continue if we are removing entries
            if remove:
                return
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['telluric']),
             colour='magenta')
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        calib_tellu_update(params, recipe, pconst, 'telluric')
    # update log and index database
    if dbkind in ['log', 'all']:
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['log']),
             colour='magenta')
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        log_update(params, recipe, pconst)
    # update index database
    if dbkind in ['findex', 'all']:
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['index']),
             colour='magenta')
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        index_update(params, recipe)

    if dbkind in ['astrom', 'all']:
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['object']),
             colour='magenta')
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        manage_databases.update_object_database(params)

    if dbkind in ['reject', 'all']:
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['reject']),
             colour='magenta')
        WLOG(params, 'info', params['LOG.HEADER'], colour='magenta')
        manage_databases.update_reject_database(params)


def reset_databases(params: ParamDict, dbkind):
    """
    Reset all database to installation point

    :param params: ParamDict, parameter dictionary of constants
    :param dbkind: str, the type of database (i.e. all, calib, tellu, log etc)
    :return:
    """
    manage_databases.install_databases(params, dbkind=dbkind, verbose=True)


def calib_tellu_update(params: ParamDict, recipe: DrsRecipe,
                       pconst: Instrument, db_type: str):
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
        db_path = params['PATH.CALIB']
        name = 'calibration database'
        file_set_name = 'calib_file'
        # load the calibration database
        dbmanager = drs_database.CalibrationDatabase(params, recipe.shortname)
        dbmanager.load_db()
    elif db_type == 'telluric':
        db_path = params['PATH.TELLU']
        name = 'telluric database'
        file_set_name = 'tellu_file'
        # load the telluric database
        dbmanager = drs_database.TelluricDatabase(params, recipe.shortname)
        dbmanager.load_db()
    else:
        raise AperoCodedException(params, '09-505-00001', targs=[db_type])
        dbmanager = None
        db_path = None
        name = None
        file_set_name = None
    # ----------------------------------------------------------------------
    # get a list of all database paths
    db_list = manage_databases.list_databases(params, recipe.shortname)
    # backup database
    dbmanager.database.backup()
    # reset database
    if db_type == 'calibration':
        # reset database
        manage_databases.create_calibration_database(params, pconst, db_list)
        # reload the calibration database
        dbmanager = drs_database.CalibrationDatabase(params, recipe.shortname)
        dbmanager.load_db()
    elif db_type == 'telluric':
        manage_databases.create_telluric_database(params, pconst, db_list)
        # reload the telluric database
        dbmanager = drs_database.TelluricDatabase(params, recipe.shortname)
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
    mp_key = params['TOOLS.REPROCESS.MP_CALIB'].lower()
    # log total file count and cores before processing (only if multiprocessing enabled)
    if cores > 1:
        total_files = len(db_files)
        WLOG(params, 'info', 'Running {0} update in multiprocess mode '
             'CORES={1} TOTAL_IT={2}'.format(db_type, cores, total_files))
    if mp_key == 'pathos' and cores > 1:
        _multi_process_calib_tellu_pathos(params, recipe.shortname,
                                          db_type, file_set_name,
                                          name, func_name, db_files, cores)
    elif mp_key == 'pool' and cores > 1:
        _multi_process_calib_tellu_pool(params, recipe.shortname,
                                        db_type, file_set_name,
                                        name, func_name, db_files, cores)
    elif mp_key == 'process' and cores > 1:
        _multi_process_calib_tellu_process(params, recipe.shortname,
                                           db_type, file_set_name,
                                           name, func_name, db_files, cores)
    else:
        # serial processing
        _calib_tellu_update_files(params, recipe.shortname,
                                  db_type, file_set_name,
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
    mp_key = params['TOOLS.REPROCESS.MP_FINDEX'].lower()
    if mp_key == 'pathos' and cores > 1:
        _multi_process_index_pathos(params, recipe.shortname, block_kinds,
                                    cores)
    elif mp_key == 'pool' and cores > 1:
        _multi_process_index_pool(params, recipe.shortname, block_kinds,
                                  cores)
    elif mp_key == 'process' and cores > 1:
        _multi_process_index_process(params, recipe.shortname, block_kinds,
                                     cores)
    else:
        # serial processing
        _index_update_blocks(params, recipe.shortname, block_kinds)


def log_update(params: ParamDict, recipe: DrsRecipe, pconst: Instrument):
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
    logdbm = drs_database.LogDatabase(params, recipe.shortname)
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
        # get multiprocessing method
        mp_logdb = params['TOOLS.REPROCESS.MP_LOGDB'].lower()
        # use parallel processing if enabled and we have multiple cores
        if mp_logdb == 'pathos' and cores > 1:
            logentries, log_pids = _multi_process_logdb_pathos(params, files,
                                                               cores)
        elif mp_logdb == 'pool' and cores > 1:
            logentries, log_pids = _multi_process_logdb_pool(params, files,
                                                             cores)
        elif mp_logdb == 'process' and cores > 1:
            logentries, log_pids = _multi_process_logdb_process(params, files,
                                                                cores)
        else:
            # serial processing
            logentries, log_pids = _log_update_files(params, files)
        # ---------------------------------------------------------------------
        # loop around unique pids and remove them from log database (we are
        #    updating them now)
        for pid in np.unique(log_pids):
            # remove pids
            logdbm.remove_pids(pid)
        # ---------------------------------------------------------------------
        # print progress
        # TODO: Add to lanagugage database
        msg = 'Merging entries into log database.'
        WLOG(params, 'info', msg)
        # add unique entries to log database
        for lcode in logentries:
            # add this entry
            logdbm.add_entries(*logentries[lcode])


# =============================================================================
# Define worker functions
# =============================================================================
def _calib_tellu_update_files(params: ParamDict, shortname: str,
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
    # load instrument config
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the file mod for this instrument
    filemod = pconst.FILEMOD()
    # load the database
    if db_type == 'calibration':
        dbmanager = drs_database.CalibrationDatabase(params, shortname)
    elif db_type == 'telluric':
        dbmanager = drs_database.TelluricDatabase(params, shortname)
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
        if not hasattr(filemod, file_set_name):
            eargs = [name, file_set_name, filemod, func_name]
            WLOG(params, 'error', textentry('00-505-00001', args=eargs))
            file_set = None
        else:
            file_set = getattr(filemod, file_set_name)
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


def _calib_tellu_update_files_batch(params: ParamDict, shortname: str,
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
    # load instrument config
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the file mod for this instrument
    filemod = pconst.FILEMOD()
    # load the database
    if db_type == 'calibration':
        dbmanager = drs_database.CalibrationDatabase(params, shortname)
    elif db_type == 'telluric':
        dbmanager = drs_database.TelluricDatabase(params, shortname)
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
        if not hasattr(filemod, file_set_name):
            eargs = [name, file_set_name, filemod, func_name]
            WLOG(params, 'error', textentry('00-505-00001', args=eargs))
            file_set = None
        else:
            file_set = getattr(filemod, file_set_name)
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


def _multi_process_calib_tellu_pathos(params: ParamDict, shortname: str,
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
    try:
        from pathos.multiprocessing import ProcessPool
        from functools import partial
        # split files into N=cores groups
        cores = min(cores, len(db_files))
        chunk_size = int(np.ceil(len(db_files) / cores))
        grouped_files = [db_files[i:i + chunk_size]
                         for i in range(0, len(db_files), chunk_size)]
        # create partial function with fixed common arguments
        total_batches = len(grouped_files)
        process_func = partial(_calib_tellu_update_files_batch,
                              params=params, shortname=shortname,
                              db_type=db_type, file_set_name=file_set_name,
                              name=name, func_name=func_name,
                              total_batches=total_batches)
        # prepare argument tuples with only variable parameters
        args_list = [[grouped_files[i], i + 1]
                     for i in range(len(grouped_files))]
        # start parallel jobs
        with ProcessPool(cores) as pool:
            pool.starmap(process_func, args_list)
    except ImportError:
        # fallback to pool mode if pathos not available
        return _multi_process_calib_tellu_pool(params, shortname, db_type,
                                              file_set_name, name, func_name,
                                              db_files, cores)


def _multi_process_calib_tellu_pool(params: ParamDict, shortname: str,
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
    from functools import partial
    # split files into N=cores groups
    cores = min(cores, len(db_files))
    chunk_size = int(np.ceil(len(db_files) / cores))
    grouped_files = [db_files[i:i + chunk_size]
                     for i in range(0, len(db_files), chunk_size)]
    # create partial function with fixed common arguments
    total_batches = len(grouped_files)
    process_func = partial(_calib_tellu_update_files_batch,
                          params=params, shortname=shortname,
                          db_type=db_type, file_set_name=file_set_name,
                          name=name, func_name=func_name,
                          total_batches=total_batches)
    # prepare argument tuples with only variable parameters
    args_list = [[grouped_files[i], i + 1]
                 for i in range(len(grouped_files))]
    # start parallel jobs
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        pool.starmap(process_func, args_list)


def _multi_process_calib_tellu_process(params: ParamDict, shortname: str,
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
        args = (params, shortname, db_type, file_set_name, name, func_name,
                grouped_file, f_it + 1, len(grouped_files))
        # create and start process
        process = Process(target=_calib_tellu_update_files_batch, args=args)
        process.start()
        jobs.append(process)
    # wait for all processes to complete
    for job in jobs:
        job.join()


def _index_update_blocks(params: ParamDict, shortname: str,
                         block_kinds: List) -> None:
    """
    Process a list of block kinds serially and update the index database

    :param params: ParamDict, parameter dictionary of constants
    :param block_kinds: List, list of block kind strings to process

    :return: None
    """
    # get index database
    findexdbm = drs_database.FileIndexDatabase(params, shortname)
    findexdbm.load_db()
    # get astrometric database
    astromdb = drs_database.AstrometricDatabase(params, shortname)
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


def _index_update_blocks_batch(params: ParamDict, shortname: str,
                               block_kinds: List, batch_idx: int = None,
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
    findexdbm = drs_database.FileIndexDatabase(params, shortname)
    findexdbm.load_db()
    # get astrometric database
    astromdb = drs_database.AstrometricDatabase(params, shortname)
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


def _multi_process_index_pathos(params: ParamDict, shortname: str,
                                block_kinds: List, cores: int) -> None:
    """
    Process block kinds via pathos.Pool.map, batching into Ncores groups

    :param params: ParamDict, parameter dictionary of constants
    :param block_kinds: List, list of block kind strings
    :param cores: int, the number of cores to use

    :return: None
    """
    try:
        from pathos.multiprocessing import ProcessPool
        from functools import partial
        # split block_kinds into N=cores groups
        cores = min(cores, len(block_kinds))
        chunk_size = int(np.ceil(len(block_kinds) / cores))
        grouped_kinds = [block_kinds[i:i + chunk_size]
                         for i in range(0, len(block_kinds), chunk_size)]
        # create partial function with fixed common arguments
        total_batches = len(grouped_kinds)
        process_func = partial(_index_update_blocks_batch,
                              params=params, shortname=shortname,
                              total_batches=total_batches)
        # prepare argument tuples with only variable parameters
        args_list = [[grouped_kinds[i], i + 1]
                     for i in range(len(grouped_kinds))]
        # start parallel jobs
        with ProcessPool(cores) as pool:
            pool.starmap(process_func, args_list)
    except ImportError:
        # fallback to pool mode if pathos not available
        return _multi_process_index_pool(params, shortname, block_kinds, cores)


def _multi_process_index_pool(params: ParamDict, shortname: str,
                              block_kinds: List, cores: int) -> None:
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
    from functools import partial
    # split block_kinds into N=cores groups
    cores = min(cores, len(block_kinds))
    chunk_size = int(np.ceil(len(block_kinds) / cores))
    grouped_kinds = [block_kinds[i:i + chunk_size]
                     for i in range(0, len(block_kinds), chunk_size)]
    # create partial function with fixed common arguments
    total_batches = len(grouped_kinds)
    process_func = partial(_index_update_blocks_batch,
                          params=params, shortname=shortname,
                          total_batches=total_batches)
    # prepare argument tuples with only variable parameters
    args_list = [[grouped_kinds[i], i + 1]
                 for i in range(len(grouped_kinds))]
    # start parallel jobs
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        pool.starmap(process_func, args_list)


def _multi_process_index_process(params: ParamDict, shortname: str,
                                 block_kinds: List, cores: int) -> None:
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
        args = (params, shortname, grouped_kind, k_it + 1, len(grouped_kinds))
        # create and start process
        process = Process(target=_index_update_blocks_batch, args=args)
        process.start()
        jobs.append(process)
    # wait for all processes to complete
    for job in jobs:
        job.join()


def _log_update_files(params: ParamDict, files: List) -> Tuple[dict, List]:
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
        # get hdu names
        with fits.open(filename) as hdus:
            hdu_names = list(map(lambda x: x.name, hdus))
        # deal with no param table - skip
        if 'PARAM_TABLE' not in hdu_names:
            continue
        # load param table
        ptable = drs_table.read_table(params, filename, fmt='fits',
                                      hdu='PARAM_TABLE')
        # get all log update entries (per file)
        logdict, lcode, lpid = _log_update(ptable)
        # merge duplicate lcodes (same PID/LEVEL/SUBLEVEL) rather than
        # silently overwriting – products from the same run can differ in
        # QC fields such as PASSED_ALL_QC
        if lcode in logentries:
            logentries[lcode] = _merge_log_entries(logentries[lcode],
                                                   logdict)
        else:
            logentries[lcode] = logdict
        # append to pids
        log_pids.append(lpid)
    # return results
    return logentries, log_pids


def _log_update_files_batch(params: ParamDict,
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
        # get hdu names
        with fits.open(filename) as hdus:
            hdu_names = list(map(lambda x: x.name, hdus))
        # deal with no param table - skip
        if 'PARAM_TABLE' not in hdu_names:
            continue
        # load param table
        ptable = drs_table.read_table(params, filename, fmt='fits',
                                      hdu='PARAM_TABLE')
        # get all log update entries (per file)
        logdict, lcode, lpid = _log_update(ptable)
        # merge duplicate lcodes (same PID/LEVEL/SUBLEVEL) rather than
        # silently overwriting – products from the same run can differ in
        # QC fields such as PASSED_ALL_QC
        if lcode in logentries:
            logentries[lcode] = _merge_log_entries(logentries[lcode],
                                                   logdict)
        else:
            logentries[lcode] = logdict
        # append to pids
        log_pids.append(lpid)
    # return results
    return logentries, log_pids


def _multi_process_logdb_pathos(params: ParamDict,
                                files: List, cores: int) -> Tuple[dict, List]:
    """
    Process files via pathos.Pool.map, batching files into Ncores groups

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PseudoConstants, pseudo constant object
    :param files: List, list of file paths to process
    :param cores: int, the number of cores to use

    :return: Tuple, 1. dict of logentries, 2. list of log_pids
    """
    try:
        from pathos.multiprocessing import ProcessPool
        from functools import partial
        # split files into N=cores groups
        cores = min(cores, len(files))
        chunk_size = int(np.ceil(len(files) / cores))
        grouped_files = [files[i:i + chunk_size]
                         for i in range(0, len(files), chunk_size)]
        # create partial function with fixed common arguments
        total_batches = len(grouped_files)
        process_func = partial(_log_update_files_batch,
                              params=params, total_batches=total_batches)
        # prepare argument tuples with only variable parameters
        args_list = [[grouped_files[i], i + 1]
                     for i in range(len(grouped_files))]
        # start parallel jobs
        with ProcessPool(cores) as pool:
            results = pool.starmap(process_func, args_list)
        # merge results from all batches – use _merge_log_entries so that
        # entries with the same PID/LEVEL/SUBLEVEL across batches are combined
        # correctly (e.g. PASSED_ALL_QC takes the logical AND) rather than
        # silently overwritten
        logentries, log_pids = dict(), []
        for batch_logentries, batch_log_pids in results:
            for lcode, entry in batch_logentries.items():
                if lcode in logentries:
                    logentries[lcode] = _merge_log_entries(logentries[lcode],
                                                           entry)
                else:
                    logentries[lcode] = entry
            log_pids.extend(batch_log_pids)
        # return merged results
        return logentries, log_pids
    except ImportError:
        # fallback to pool mode if pathos not available
        return _multi_process_logdb_pool(params, files, cores)


def _multi_process_logdb_pool(params: ParamDict,
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
    from functools import partial
    # split files into N=cores groups
    cores = min(cores, len(files))
    chunk_size = int(np.ceil(len(files) / cores))
    grouped_files = [files[i:i + chunk_size]
                     for i in range(0, len(files), chunk_size)]
    # create partial function with fixed common arguments
    total_batches = len(grouped_files)
    process_func = partial(_log_update_files_batch,
                          params=params, total_batches=total_batches)
    # prepare argument tuples with only variable parameters
    args_list = [[grouped_files[i], i + 1]
                 for i in range(len(grouped_files))]
    # start parallel jobs
    with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
        results = pool.starmap(process_func, args_list)
    # merge results from all batches – use _merge_log_entries so that
    # entries with the same PID/LEVEL/SUBLEVEL across batches are combined
    # correctly (e.g. PASSED_ALL_QC takes the logical AND) rather than
    # silently overwritten
    logentries, log_pids = dict(), []
    for batch_logentries, batch_log_pids in results:
        for lcode, entry in batch_logentries.items():
            if lcode in logentries:
                logentries[lcode] = _merge_log_entries(logentries[lcode],
                                                       entry)
            else:
                logentries[lcode] = entry
        log_pids.extend(batch_log_pids)
    # return merged results
    return logentries, log_pids


def _multi_process_logdb_process(params: ParamDict,
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
        args = (params, grouped_file, f_it + 1, len(grouped_files),
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
                logentries[lcode] = _merge_log_entries(logentries[lcode],
                                                       entry)
            else:
                logentries[lcode] = entry
        log_pids.extend(batch_log_pids)
    # return merged results
    return logentries, log_pids


def _log_update_files_batch_process(params: ParamDict,
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
    logentries, log_pids = _log_update_files_batch(params, files,
                                                   batch_idx, total_batches)
    # append results to shared list
    results_list.append((logentries, log_pids))


def _merge_log_entries(existing: List[Any],
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
    # get pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get log database column names
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



def _log_update(ptable: Table) -> Tuple[List[Any], str, str]:
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
    # load instrument config
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
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


def remove_db_entries(params: ParamDict, recipe: DrsRecipe,
                      db_type: str) -> bool:

    # first check if we have the --since and --keys arguments in INPUTS
    # if we do then we need to remove entries from the database
    if 'INPUTS' not in params:
        # we are not removing keys
        return False
    # get keys from inputs
    since = params['INPUTS']['SINCE']
    before = params['INPUTS']['BEFORE']
    keys = params['INPUTS']['KEYS']
    deletefiles = drs_text.true_text(params['INPUTS']['DELETEFILES'])
    test = drs_text.true_text(params['INPUTS']['TEST'])
    # check if either are valid
    have_since = not drs_text.null_text(since, ['None', '', 'Null'])
    have_keys = not drs_text.null_text(keys, ['None', '', 'Null'])
    have_before = not drs_text.null_text(before, ['None', '', 'Null'])
    # if we do not have either then we are not removing keys
    if not have_keys and not have_since and not have_before:
        # we are not removing keys
        return False
    # -------------------------------------------------------------------------
    # get database
    if db_type == 'calibration':
        dbmanager = drs_database.CalibrationDatabase(params, recipe.shortname)
        path = params['PATH.CALIB']
    elif db_type == 'telluric':
        dbmanager = drs_database.TelluricDatabase(params, recipe.shortname)
        path = params['PATH.TELLU']
    else:
        # TODO: Add to language database
        emsg = 'Unknown database type: {0}'
        eargs = [db_type]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)
    # load database
    dbmanager.load_db()
    # -------------------------------------------------------------------------
    # deal with condition for removal
    conditions = []
    # -------------------------------------------------------------------------
    # add the since condition
    if have_since:
        # convert since parameter from YYYY-MM-DD to unix time
        try:
            since_unix = base.Time(since, format='iso').unix
        except Exception as e:
            # TODO: Add to language database
            wmsg = ('Cannot convert --since parameter to unix time: {0}'
                    '\nError {1}: {2}')
            wargs = [since, type(e), str(e)]
            WLOG(params, 'warning', wmsg.format(*wargs))
            return True
        # add condition
        conditions.append('(UNIXTIME > {0})'.format(since_unix))
    # -------------------------------------------------------------------------
    # add the before condition
    if have_before:
        # convert before parameter from YYYY-MM-DD to unix time
        try:
            before_unix = base.Time(before, format='iso').unix
        except Exception as e:
            # TODO: Add to language database
            wmsg = ('Cannot convert --before parameter to unix time: {0}'
                    '\nError {1}: {2}')
            wargs = [since, type(e), str(e)]
            WLOG(params, 'warning', wmsg.format(*wargs))
            return True
        # add condition
        conditions.append('(UNIXTIME < {0})'.format(before_unix))
    # -------------------------------------------------------------------------
    # add the keyname condition
    if have_keys:
        # get keys
        keys = keys.split(',')
        # loop around keys and add to sub conditions
        sub_conditions = []
        for key in keys:
            sub_conditions.append('KEYNAME="{0}"'.format(key))
        # join with an OR and add to full condition
        conditions.append('({0})'.format(' OR '.join(sub_conditions)))
    # -------------------------------------------------------------------------
    # deal with no conditions (should not happen)
    if len(conditions) == 0:
        # TODO: Add to language database
        wmsg = ('No conditions to remove from database. Invalid --since '
                '--before and --keys arguments')
        WLOG(params, 'warning', wmsg, sublevel=1)
        return True
    # -------------------------------------------------------------------------
    # convert conditions to a string with the AND operator
    condition = ' AND '.join(conditions)
    # -------------------------------------------------------------------------
    # get a list of entries to remove
    table = dbmanager.database.get('*', condition=condition, return_table=True)
    # -------------------------------------------------------------------------
    # deal with no entries found
    if len(table) == 0:
        # TODO: Add to language database
        wmsg = 'Warning no entries found to remove from database'
        WLOG(params, 'warning', wmsg, sublevel=1)
        return True
    # -------------------------------------------------------------------------
    # ask user if they wish to remove these entries (or view entries before
    #     deletion)
    # get the number of entries
    nentries = len(table)
    # display message
    msg = 'Found {0} entries to remove from database'
    margs = [nentries]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # loop around until user decides something
    # ask user if they wish to continue
    while True:
        uinput = str(input('\n\nDo you wish to remove? [Y]es or [N]o ([V] to '
                           'view files):\t')).strip()
        # deal with viewing files
        if 'V' in uinput.upper():
            # print table
            for row in range(len(table)):
                print(table['KEYNAME'][row], '', '',
                      table['FILENAME'][row], '', '',
                      table['HUMANTIME'][row])
        elif 'Y' in uinput.upper():
            # log that we are remove entries
            msg = 'Removing {0} entries from database'
            margs = [nentries]
            WLOG(params, 'info', msg.format(*margs))
            # remove entries
            if not test:
                dbmanager.remove_entries(condition)
            # deal with removing files from disk
            if drs_text.true_text(deletefiles):
                # loop around files in table and remove them
                for row in range(len(table)):
                    # get filename
                    filename = str(table['FILENAME'][row])
                    # get full path
                    fullpath = os.path.join(path, filename)
                    # check if file exists
                    if os.path.exists(fullpath):
                        # log that we are removing file from disk
                        msg = 'Removing file from disk: {0}'
                        margs = [fullpath]
                        WLOG(params, '', msg.format(*margs))
                        # remove file
                        if not test:
                            os.remove(fullpath)
            break
        elif 'N' in uinput.upper():
            # return and do not continue
            return True
        else:
            print('Invalid input, please try again')
    # -------------------------------------------------------------------------
    # if we get to here we return with a True (as we do not continue)
    return True


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
