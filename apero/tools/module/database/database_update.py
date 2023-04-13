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

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.core import drs_text
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
def update_database(params: ParamDict, dbkind: str):
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

        # deal with removal of entries
        if dbkind == 'calib':
            remove = remove_db_entries(params, pconst, 'calibration')
            # we do not continue if we are removing entries
            if remove:
                return
        # otherwise we update full calibration database
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', textentry('40-006-00007', args=['calibration']),
             colour='magenta')
        WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
        calib_tellu_update(params, pconst, 'calibration')
    # update telluric database
    if dbkind in ['tellu', 'all']:
        # deal with removal of entries
        if dbkind == 'tellu':
            remove = remove_db_entries(params, pconst, 'telluric')
            # we do not continue if we are removing entries
            if remove:
                return
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
        index_update(params)

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
    # ----------------------------------------------------------------------
    # loop around all calib files and try to find the kinds
    for it in tqdm(range(len(db_files))):
        # ------------------------------------------------------------------
        # get db_file
        db_file = db_files[it]
        # ------------------------------------------------------------------
        # log progress
        wargs = [it + 1, len(db_files), os.path.basename(db_file)]
        WLOG(params, 'debug', textentry('40-505-00001', args=wargs))
        # ------------------------------------------------------------------
        if not hasattr(filemod.get(), file_set_name):
            eargs = [name, file_set_name, filemod.get(), func_name]
            WLOG(params, 'error', textentry('00-505-00001', args=eargs))
            file_set = None
        else:
            file_set = getattr(filemod.get(), file_set_name)
        # ------------------------------------------------------------------
        # skip default reference files
        if os.path.basename(db_file).startswith(REF_PREFIX):
            # log skipping
            wargs = [REF_PREFIX]
            WLOG(params, 'debug', textentry('40-505-00003', args=wargs))
            # skip
            continue
        # ------------------------------------------------------------------
        # make a new copy of out_file
        db_out_file = file_set.newcopy(params=params)
        # ------------------------------------------------------------------
        # try to find cdb_file
        found, kind = drs_file.id_drs_file(params, db_out_file,
                                           filename=db_file, nentries=1,
                                           required=False)
        # ------------------------------------------------------------------
        # append to cdb_data
        if found:
            # log that we found file
            WLOG(params, 'debug', textentry('40-505-00002', args=[kind]))
            # --------------------------------------------------------------
            # add the files back to the database
            if db_type == 'calibration':
                dbmanager.add_calib_file(kind, copy_files=False, verbose=False)
            elif db_type == 'telluric':
                dbmanager.add_tellu_file(kind, copy_files=False, verbose=False)
        # ------------------------------------------------------------------
        # delete file
        del kind, db_out_file


def index_update(params: ParamDict):
    # get all block kinds
    block_kinds = drs_file.DrsPath.get_block_names(params=params,
                                                   block_filter='indexing')
    # get index database
    findexdbm = drs_database.FileIndexDatabase(params)
    findexdbm.load_db()
    # loop around block kinds (with the indexing filter)
    for block_kind in block_kinds:
        # log block update
        WLOG(params, '', textentry('40-503-00044', args=[block_kind]))
        # update index database for block kind
        findexdbm = drs_utils.update_index_db(params, block_kind=block_kind,
                                              findexdbm=findexdbm)


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
        # storage for unique logcodes
        logentries, log_pids = dict(), []
        # ---------------------------------------------------------------------
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


def remove_db_entries(params: ParamDict, pconst: PseudoConstants,
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
        dbmanager = drs_database.CalibrationDatabase(params)
        path = params['DRS_CALIB_DB']
    elif db_type == 'telluric':
        dbmanager = drs_database.TelluricDatabase(params)
        path = params['DRS_TELLU_DB']
    else:
        # TODO: Add to language database
        emsg = 'Unknown database type: {0}'
        eargs = [db_type]
        WLOG(params, 'error', emsg.format(*eargs))
        return False
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
                    filename = table['FILENAME'][row]
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
# Define worker functions
# =============================================================================
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
    for logkey in logcols:
        # construct keys
        key = 'rlog.{0}'.format(logkey)
        # get value
        logvalue = logdict.get(key, 'NULL')
        # by definition these must have ended (even if the ptable says
        #     otherwise)
        if logkey == 'ENDED':
            logvalue = 1
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
