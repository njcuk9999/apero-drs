#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-05-10

@author: cook
"""
from astropy.table import Table
import numpy as np
import os
import glob
from pathlib import Path
from typing import Any, List, Tuple

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.utils import drs_recipe
from apero.core.utils import drs_utils
from apero.io import drs_fits
from apero.io import drs_table
from apero.tools.module.database import manage_databases
from apero.core.instruments.default import pseudo_const


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
PseudoConstants = pseudo_const.PseudoConstants
# get display func
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# get tqdm (if required)
tqdm = base.tqdm_module()
# Define master prefix
MASTER_PREFIX = 'MASTER_'


# =============================================================================
# Define functions
# =============================================================================
def update_database(params: ParamDict, recipe: DrsRecipe):
    """
    Update the calib/tellu/log and index databases from files on disk

    :param params: Paramdict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :return:
    """
    # load pconst
    pconst = constants.pload()
    # update calibration database
    calib_tellu_update(params, recipe, pconst, 'calibration')
    # update telluric database
    calib_tellu_update(params, recipe, pconst, 'telluric')
    # update log and index database
    log_update(params, pconst)
    # update index database
    index_update(params)


def calib_tellu_update(params: ParamDict, recipe: DrsRecipe,
                       pconst: PseudoConstants, db_type: str):
    """
    Update either the calibration or telluric database with files on disk

    :param params: Paramdict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
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
        manage_databases.create_telluric_database(pconst, db_list)
        # reload the telluric database
        dbmanager = drs_database.CalibrationDatabase(params)
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
    # ----------------------------------------------------------------------
    # loop around all calib files and try to find the kinds
    for it, db_file in enumerate(db_files):
        # log progress
        wargs = [it + 1, len(db_files), os.path.basename(db_file)]
        WLOG(params, 'info', textentry('40-505-00001', args=wargs))
        # ------------------------------------------------------------------
        if not hasattr(filemod.get(), file_set_name):
            eargs = [name, file_set_name, filemod.get(), func_name]
            WLOG(params, 'error', textentry('00-505-00001', args=eargs))
            file_set = None
        else:
            file_set = getattr(filemod.get(), file_set_name)
        # ------------------------------------------------------------------
        # skip default master files
        if os.path.basename(db_file).startswith(MASTER_PREFIX):
            # log skipping
            wargs = [MASTER_PREFIX]
            WLOG(params, 'info', textentry('40-505-00003', args=wargs))
            # skip
            continue
        # ------------------------------------------------------------------
        # make a new copy of out_file
        db_out_file = file_set.newcopy(params=params)
        # ------------------------------------------------------------------
        # try to find cdb_file
        found, kind = drs_file.id_drs_file(params, recipe, db_out_file,
                                           filename=db_file, nentries=1,
                                           required=False)
        # ------------------------------------------------------------------
        # append to cdb_data
        if found:
            # log that we found i
            WLOG(params, '', textentry('40-505-00002', args=[kind]))
            # --------------------------------------------------------------
            # add the files back to the database
            if db_type == 'calibration':
                dbmanager.add_calib_file(kind, copy_files=False, verbose=False)
            elif db_type == 'telluric':
                dbmanager.add_tellu_file(kind, copy_files=False, verbose=False)
        # ------------------------------------------------------------------
        # delete file
        del kind, db_out_file
    # print note about masters
    WLOG(params, 'info', textentry('40-505-00004'))
    _ = input('\t')


def index_update(params: ParamDict,):
    # get all block kinds
    block_kinds = drs_file.DrsPath.get_block_names(params=params,
                                                   block_filter='indexing')
    # get index database
    indexdbm = drs_database.IndexDatabase(params)
    indexdbm.load_db()
    # loop around block kinds (with the indexing filter)
    for block_kind in block_kinds:
        # log block update
        WLOG(params, '', textentry('40-503-00044', args=[block_kind]))
        # update index database for block kind
        indexdbm = drs_utils.update_index_db(params, block_kind=block_kind,
                                             indexdbm=indexdbm)


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
        files = Path(block.path).rglob('*.fits')
        # storage for unique logcodes
        logentries, log_pids = dict(), []
        # ---------------------------------------------------------------------
        # loop around files
        for filepath in tqdm(files):
            # get string version
            filename = str(filepath)
            # load param table
            # TODO: need to check for PARAM_TABLE in filename
            ptable = drs_table.read_table(params, filename, fmt='fits',
                                          hdu='PARAM_TABLE')
            # get all log update entries (per file)
            logdict, lcode, lpid = _log_update(pconst, ptable)
            # add log dict as a log code (unique ones only)
            logentries[lcode] = logdict
            # append to pids
            log_pids.append(lpid)
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
    logcols, _ = pconst.LOG_DB_COLUMNS()
    # loop around log keys and add them to values
    logvalues = []
    for logkey in logcols:
        # construct keys
        key = 'rlog.{0}'.format(logkey.lower())
        # get value
        logvalue = logdict.get(key, 'NULL')
        # append value to values
        logvalues.append(logvalue)
    # generate unique log code
    largs = [logdict['rlog.pid'], logdict['rlog.level'],
             logdict['rlog.sublevel']]
    logcode = '{0} {1} {2}'.format(*largs)
    # return the log values and the log code
    return logvalues, logcode, logdict['rlog.pid']


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
