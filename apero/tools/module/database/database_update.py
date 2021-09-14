#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-05-10

@author: cook
"""
from astropy.table import Table, vstack
from astropy.io import fits
import numpy as np
import os
import glob
from pathlib import Path
import shutil
from typing import Any, List, Tuple

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.core.utils import drs_utils
from apero.io import drs_fits
from apero.io import drs_table
from apero.tools.module.database import manage_databases
from apero.core.instruments.default import pseudo_const
from apero.science import preprocessing as prep


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
# Define the gaia drs column in database
GAIA_COL = 'GAIADR2ID'


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
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    WLOG(params, 'info', textentry('40-006-00007', args=['calibration']),
         colour='magenta')
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    calib_tellu_update(params, recipe, pconst, 'calibration')
    # update telluric database
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    WLOG(params, 'info', textentry('40-006-00007', args=['telluric']),
         colour='magenta')
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    calib_tellu_update(params, recipe, pconst, 'telluric')
    # update log and index database
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    WLOG(params, 'info', textentry('40-006-00007', args=['log']),
         colour='magenta')
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    log_update(params, pconst)
    # update index database
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    WLOG(params, 'info', textentry('40-006-00007', args=['index']),
         colour='magenta')
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    index_update(params)


def update_obj_reset(params: ParamDict):
    """
    Update the reset.object.csv file from either a manual dfits query piped
    to a text file (or set of text files) or from the currently defined
    raw directory

    :param params: ParamDict, the parameter dictionary of constants

    :return:
    """
    # get objdb arg from user
    objdb_arg = str(params['INPUTS']['OBJDB'])
    # deal with objdb argument being null
    if drs_text.null_text(objdb_arg, ['None', '', 'Null']):
        return
    # -------------------------------------------------------------------------
    # load psuedo constants
    pconst = constants.pload()
    # get database parameters
    dparams = base.DPARAMS
    # get the obj cols
    rawobjcol = params['KW_OBJECTNAME'][0]
    objcol = params['KW_OBJNAME'][0]
    # get reset path
    asset_dir = params['DRS_DATA_ASSETS']
    reset_path = params['DATABASE_DIR']
    obj_reset_path = os.path.join(asset_dir, reset_path)
    # get obj reset filename
    if dparams['USE_MYSQL']:
        obj_reset_basename = dparams['MYSQL']['OBJECT']['RESET']
    else:
        obj_reset_basename = dparams['SQLITE3']['OBJECT']['RESET']
    # get full path to reset file
    obj_reset_file = os.path.join(obj_reset_path, obj_reset_basename)
    # -------------------------------------------------------------------------
    # backup and remove old reset file
    shutil.copy(obj_reset_file, obj_reset_file + '.backup')
    # clear obj reset file
    _clear_obj_reset_file(obj_reset_file)
    # -------------------------------------------------------------------------
    # load the master file
    if objdb_arg.upper() in ['TRUE', '1']:
        master_table = _master_obj_table_from_raw(params)
    else:
        # get files using glob
        files = glob.glob(objdb_arg)
        # get master table from these files
        master_table = _master_obj_table_from_dfits(files)
    # print how many objects files found
    margs = [len(master_table)]
    WLOG(params, '', textentry('40-006-00008', args=margs))
    # -------------------------------------------------------------------------
    # get unique objects
    utable = _unique_obj_table(params, master_table)
    # print how many unique objects found
    margs = [len(utable)]
    WLOG(params, '', textentry('40-006-00009', args=margs))
    # -------------------------------------------------------------------------
    # Load temporary new database
    # -------------------------------------------------------------------------
    # modify path to reset files (this is what we are going to create)
    params.set('DRS_DATA_ASSETS', os.path.dirname(obj_reset_file))
    params.set('DATABASE_DIR', '')
    # update dparams (to be pushed into object database definition)
    dparams = dict(base.DPARAMS)
    if dparams['USE_MYSQL']:
        dparams['MYSQL']['OBJECT']['PROFILE'] = 'RESET_TEST'
        dparams['MYSQL']['OBJECT']['RESET'] = os.path.basename(obj_reset_file)
    else:
        dparams['SQLITE3']['OBJECT']['PROFILE'] = 'RESET_TEST'
        dparams['SQLITE3']['OBJECT']['NAME'] = 'object_reset_test.db'
        dparams['SQLITE3']['OBJECT']['RESET'] = os.path.basename(obj_reset_file)
    # list database
    iobjdb = drs_database.ObjectDatabase(params, check=False, dparams=dparams)
    databases = dict(object=iobjdb)
    # set up a proxy database (do not change current databases)
    manage_databases.create_object_database(params, pconst, databases)
    # load object database
    objdbm = drs_database.ObjectDatabase(params, dparams=dparams)
    objdbm.load_db()
    # -------------------------------------------------------------------------
    # Resolve targets in Gaia
    # -------------------------------------------------------------------------
    # loop around objects
    for row in range(len(utable)):
        # get objname for this row
        rawobjname = utable[rawobjcol][row]
        # ---------------------------------------------------------------------
        # print progress: Analysing {0}={1}   ({2}/{3})
        margs = [rawobjcol, rawobjname, row+1, len(utable)]
        WLOG(params, '', textentry('40-006-00010', args=margs))
        # ---------------------------------------------------------------------
        # make a fake header
        header = drs_fits.Header()
        for col in utable.colnames:
            header[col] = utable[col][row]
        # need to add columns
        header[objcol] = pconst.DRS_OBJ_NAME(rawobjname)
        # ---------------------------------------------------------------------
        # resolve target
        _ = prep.resolve_target(params, pconst, header=header, database=objdbm)

    # -------------------------------------------------------------------------
    # deal with saving database to csv
    # -------------------------------------------------------------------------
    # only want to keep rows with Gaia ID
    condition = '{0} !="NULL"'.format(GAIA_COL)
    # get dataframe
    df = objdbm.database.get('*', objdbm.database.tname, condition=condition,
                             return_pandas=True)
    # print update: Found {0} objects with Gaia entries
    margs = [len(df)]
    WLOG(params, '', textentry('40-006-00011', args=margs))
    # sort by objname
    df = df.sort_values('OBJNAME')
    # print saving of file: Saving reset file to: {0}
    margs = [obj_reset_file]
    WLOG(params, '', textentry('40-006-00012', args=margs))
    # save to csv file
    df.to_csv(obj_reset_file, index=False)


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
        # skip default master files
        if os.path.basename(db_file).startswith(MASTER_PREFIX):
            # log skipping
            wargs = [MASTER_PREFIX]
            WLOG(params, 'debug', textentry('40-505-00003', args=wargs))
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
        # append value to values
        logvalues.append(logvalue)
    # generate unique log code
    largs = [logdict['rlog.PID'], logdict['rlog.LEVEL'],
             logdict['rlog.SUBLEVEL']]
    logcode = '{0} {1} {2}'.format(*largs)
    # return the log values and the log code
    return logvalues, logcode, logdict['rlog.PID']


def _clear_obj_reset_file(filename: str):
    """
    Clear the object reset file

    :param filename: str, the object reset file to clear

    :return: None, clear the file
    """
    # open the file
    with open(filename, 'r') as reset_file:
        lines = reset_file.readlines()
    # remove obj reset file
    os.remove(filename)
    # write only the first line (the header columns)
    with open(filename, 'w') as reset_file:
        reset_file.write(lines[0])


def _master_obj_table_from_raw(params: ParamDict) -> Table:
    """
    Create the master object table from the current files in the current raw
    directory

    :param params: ParamDict, the parameter dictionary of constants

    :return: Table, the master table combined output of dfits files
    """
    # get the current raw directory
    rawdir = params['DRS_DATA_RAW']
    # Define FLOAT columns (for object database from dfits)
    rcols = [params['KW_OBJECTNAME'][0], params['KW_OBJRA'][0],
             params['KW_OBJDEC'][0], params['KW_ACQTIME'][0],
             params['KW_INPUTRV'][0], params['KW_OBJ_TEMP'][0]]
    # get all o.fits files
    obj_files = glob.glob(os.path.join(rawdir, '*', '*o.fits'))
    # store header values
    dict_table = dict()
    # add empty columns to fill
    for rcol in rcols:
        dict_table[rcol] = []
    # print progress: Reading {0} object headers...
    margs = [len(obj_files)]
    WLOG(params, 'info', textentry('40-006-00013', args=margs))
    # loop around fits files and get header keys
    for filename in tqdm(obj_files):
        # load header
        try:
            header = fits.getheader(filename)
        except Exception as _:
            continue
        # add header
        for rcol in rcols:
            if rcol in header:
                dict_table[rcol].append(header[rcol])
            else:
                dict_table[rcol].append('Null')
    # finally convert dict_table to astropy table
    master_table = Table()
    for rcol in rcols:
        master_table[rcol] = np.array(dict_table[rcol])
    # return master table
    return master_table


def _master_obj_table_from_dfits(files: List[str]) -> Table:
    """
    Get the master object table list from a set of dfits file

    i.e. dfits *.fits | fitsort OBJNAME RA_DEG DEC_DEG MJDEND OBJRV
                                                    OBJTEMP > spirou_targets.txt

    :param files: list of strings, the absolute paths to the dfits files

    :return: Table, the master table combined output of dfits files
    """
    # get a list of all files
    master_table = Table()
    # open and combine lines
    for filename in files:
        table = Table.read(filename, format='ascii.tab')
        # clean column names
        tmp_table = Table()
        # clean column names
        for col in table.colnames:
            newcol = col.strip()
            tmp_table[newcol] = table[col]
        # add to master table
        master_table = vstack([master_table, tmp_table])
    # return master table
    return master_table


def _unique_obj_table(params: ParamDict, master_table: Table) -> Table:
    """
    Convert a mater_table into a table of unique OBJNAMES
    must contain columns of the header keys equivalent to:

    KW_OBJECT, KW_OBJRA, KW_OBJDEC, KW_ACQTIME, KW_INPUTRV, KW_OBJ_TEMP

    The order and any extra columns do not matter

    :param params: ParamDict, the parameter dictionary of constants
    :param master_table: astropy.table.Table, the master table containing all
                         rows (either from dfits or search of all headers on
                         disk)
    :return: astropy.table.Table, the unique objects table - this will take the
             first row of each unique object name (defined by header key
             KW_OBJECT)
    """
    # get object column
    objcol = params['KW_OBJECTNAME'][0]
    # Define FLOAT columns (for object database from dfits)
    float_cols = [params['KW_OBJRA'][0], params['KW_OBJDEC'][0],
                  params['KW_ACQTIME'][0], params['KW_INPUTRV'][0],
                  params['KW_OBJ_TEMP'][0]]
    # keep only one of each object types
    unique_objects = []
    # store mask of unique objects
    mask = np.zeros(len(master_table)).astype(bool)
    # loop around all rows
    for row in range(len(master_table)):
        # get a slighly cleaner objname
        objname = master_table[objcol][row].strip()
        # deal with objnames already found (skip)
        if objname in unique_objects:
            continue
        # else this is the first example --> add to mask and unique objects
        else:
            mask[row] = True
            unique_objects.append(objname)
    # mask the master table
    master_table = master_table[mask]
    # fix columns
    master_table[objcol] = unique_objects
    # remove bad columns
    for colname in master_table.colnames:
        # remove columns starting with "col" - artifact of dfits
        if colname.startswith('col'):
            del master_table[colname]
    # fix float columns
    for float_col in float_cols:
        float_data = np.zeros(len(master_table))
        # loop around each entry (have to deal with non-float values)
        for row in range(len(master_table)):
            # try to make a float
            try:
                row_value = float(master_table[float_col][row])
            # set everything else to NaN
            except Exception as _:
                row_value = np.nan
            # add to new float data values for this row
            float_data[row] = row_value
        # load float data into table (replace column)
        master_table[float_col] = float_data
    # return this table
    return master_table



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
