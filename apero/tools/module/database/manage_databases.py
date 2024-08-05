#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Completely recreate database from scratch

Created on 2020-08-2020-08-18 17:13

@author: cook
"""
import os
from typing import Dict, List, Literal, Union

import numpy as np
import pandas as pd
from astropy.table import Table, vstack, MaskedColumn

from apero.base import base
from apero.base import drs_db
from apero.core import constants
from apero.core import lang
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_text

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.database.create_database.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get tqdm from base
tqdm = base.TQDM
# Get database definition
Database = drs_db.AperoDatabase
DatabaseM = drs_database.DatabaseManager
# Get ParamDict
ParamDict = constants.ParamDict
PseudoConst = constants.PseudoConstants
# Get Logging function
WLOG = drs_log.wlog
# get textentry
textentry = lang.textentry
# define reject column datatypes (force consistency)
REJECT_DATA_TYPES = dict()
REJECT_DATA_TYPES['IDENTIFIER'] = str
REJECT_DATA_TYPES['PP'] = int
REJECT_DATA_TYPES['TEL'] = int
REJECT_DATA_TYPES['RV'] = int
REJECT_DATA_TYPES['USED'] = int
REJECT_DATA_TYPES['COMMENT'] = str


# =============================================================================
# Define general functions
# =============================================================================
def kill(params: ParamDict, timeout: int = 60):
    """
    Kill all processes that are in the database yaml database from the specified
    user that are greater than timeout

    :param params: ParamDict, the parameter dictionary of constants
    :param timeout: time in seconds, the minimum time a sql process has been
                    running to kill it (if this is too low it will try to kill
                    itself which isn't recommended)
    :return:
    """
    # get database parameters from base
    dparams = base.DPARAMS
    # construct a generic database manager
    dbm = DatabaseM(params)
    dbm.kind = None
    dbm.dbtable = 'processlist'
    # set the database url
    dbm.load_db(dparams=dparams)
    # wrap in a try (this may not always work
    # noinspection PyBroadException
    try:
        # set update a database
        database = dbm.database
        # set up condition: only this users processes and only from the
        #   required database and that have been active for more than
        #   60 seconds
        cargs = [dbm.dbuser, dbm.dbname, timeout]
        condition = 'USER="{0}" AND DB="{1}" AND TIME > {2}'.format(*cargs)
        # log condition
        WLOG(params, '', 'Condition')
        WLOG(params, '', '\t' + condition)
        # get all processes that were started by user
        table = database.get('*', condition=condition, return_pandas=True)
        # get ids from table
        ids = table['ID'].to_list()
        # log how many ids found
        WLOG(params, '', 'Found {0} processes'.format(len(ids)))
        # try to kill processes
        for _id in ids:
            # set up command
            command = 'kill {0}'.format(_id)
            # execute command
            # noinspection PyBroadException
            try:
                with database.engine.connect() as connection:
                    connection.execute(command)
                # log killing
                WLOG(params, '', '\t' + command)
            except Exception as _:
                continue

    # just return if there is an exception
    except Exception as _:
        return


def export_database(params: ParamDict, database_name: str,
                    outfilename: str):
    """
    Exports a given database "database_name" to "outfilename" (csv file)

    :param params: ParamDict, parameter dictionary of constants
    :param database_name: str, the database name (calib, tellu, index, log,
                          object, lang)
    :param outfilename: str, the output filepath for the csv file

    :return: None, writes outfilename
    """
    # ----------------------------------------------------------------------
    # get database list
    databases = list_databases(params)
    # ----------------------------------------------------------------------
    # make sure database_name is lower case
    database_name = database_name.lower()
    # -------------------------------------------------------------------
    # deal with calibration database
    if database_name in base.DATABASE_NAMES:
        db = databases[database_name]
    # else log error
    else:
        # log error: Argument Error: EXPORTDB must be
        eargs = [' or '.join(base.DATABASE_NAMES)]
        WLOG(params, 'error', textentry('09-506-00001', args=eargs))
        db = None
    # -------------------------------------------------------------------
    # load database
    db.load_db()
    # -------------------------------------------------------------------
    # deal with no database
    if db.database is None:
        # log error: Database Error: Cannot load "{0}" database
        eargs = [database_name]
        WLOG(params, 'error', textentry('09-506-00002', args=eargs))
    # -------------------------------------------------------------------
    # get all rows as a pandas data frame
    df = db.database.get('*', return_pandas=True)
    # -------------------------------------------------------------------
    # print that we are saving csv file
    WLOG(params, '', textentry('40-507-00001', args=[outfilename]))
    # save to csv file
    df.to_csv(outfilename)


def import_database(params: ParamDict, database_name: str,
                    infilename: str,
                    joinmode: Literal["fail", "replace", "append"] = 'replace'):
    """
    Imports a given csv file "infilename" to database "database_name"

    :param params: ParamDict, parameter dictionary of constants
    :param database_name: str, the database name (calib, tellu, index, log,
                          object, lang)
    :param infilename: str, the input filepath for the csv file
    :param joinmode: str, the way to join current database and input fiile
                     - if 'replace' then current database is deleted first,
                     - if 'append' adds the infile to bottom of current database

    :return: None, writes to database
    """
    # ----------------------------------------------------------------------
    # get database list
    databases = list_databases(params)
    # ----------------------------------------------------------------------
    # make sure database_name is lower case
    database_name = database_name.lower()
    # -------------------------------------------------------------------
    # deal with joinmode
    if joinmode not in ['append', 'replace']:
        # log error: Join mode = "{0}" is invalid. Must be either "append"
        #            or "replace"
        WLOG(params, 'error', textentry('09-506-00004', args=[joinmode]))
    # -------------------------------------------------------------------
    # deal with calibration database
    if database_name in base.DATABASE_NAMES:
        db = databases[database_name]
    # else log error
    else:
        # log error Argument Error: EXPORTDB must be {0}
        eargs = [' or '.join(base.DATABASE_NAMES)]
        WLOG(params, 'error', textentry('09-506-00003', args=eargs))
        db = None
    # -------------------------------------------------------------------
    # load database
    # -------------------------------------------------------------------
    db.load_db()
    # deal with no database
    if db.database is None:
        # get a list of all other database
        other_databases = list(base.DATABASE_NAMES).remove(database_name)
        # install database
        install_databases(params, skip=other_databases)
        # load database
        db.load_db()
    # -------------------------------------------------------------------
    # load csv file
    # -------------------------------------------------------------------
    # print that we are saving csv file
    WLOG(params, '', textentry('40-507-00002', args=[infilename]))
    # load csv file into pandas table
    df = pd.read_csv(infilename)
    # -------------------------------------------------------------------
    # Push into database
    # -------------------------------------------------------------------
    # print log
    if joinmode == 'replace':
        wmsg = textentry('40-507-00003')
    else:
        wmsg = textentry('40-507-00004')
    # log
    WLOG(params, '', wmsg)
    # add pandas table to database
    db.database.add_from_pandas(df, if_exists=joinmode)


def list_databases(params: ParamDict) -> Dict[str, DatabaseM]:
    # set up storage
    databases = dict()
    pconst = constants.pload()
    # get databases from managers (later databases)
    calibdbm = drs_database.CalibrationDatabase(params, pconst)
    telludbm = drs_database.TelluricDatabase(params, pconst)
    findexdbm = drs_database.FileIndexDatabase(params, pconst)
    logdbm = drs_database.LogDatabase(params, pconst)
    objectdbm = drs_database.AstrometricDatabase(params, pconst)
    rejectdbm = drs_database.RejectDatabase(params, pconst)
    # add to storage
    databases['calib'] = calibdbm
    databases['tellu'] = telludbm
    databases['findex'] = findexdbm
    databases['log'] = logdbm
    databases['astrom'] = objectdbm
    databases['reject'] = rejectdbm
    # return the databases
    return databases


def install_databases(params: ParamDict, skip: Union[List[str], None] = None,
                      dbkind: Union[str, List[str]] = 'all',
                      verbose: bool = False):
    # deal with skip
    if skip is None:
        skip = []
    # deal with dbkind == 'all'
    if dbkind == 'all':
        runs = ['calib', 'tellu', 'findex', 'log', 'astrom', 'reject', 'lang']
    elif isinstance(dbkind, str):
        runs = [dbkind]
    else:
        runs = dbkind
    # get database paths
    databases = list_databases(params)
    # load pseudo constants
    pconst = constants.pload()
    # -------------------------------------------------------------------------
    # create calibration database
    if 'calib' not in skip and 'calib' in runs:
        _ = create_calibration_database(params, pconst, databases,
                                        verbose=verbose)
    # -------------------------------------------------------------------------
    # create telluric database
    if 'tellu' not in skip and 'tellu' in runs:
        _ = create_telluric_database(params, pconst, databases,
                                     verbose=verbose)
    # -------------------------------------------------------------------------
    # create index database
    if 'findex' not in skip and 'findex' in runs:
        _ = create_fileindex_database(params, pconst, databases,
                                      verbose=verbose)
    # -------------------------------------------------------------------------
    # create log database
    if 'log' not in skip and 'log' in runs:
        _ = create_log_database(params, pconst, databases, verbose=verbose)
    # -------------------------------------------------------------------------
    # create object database
    if 'astrom' not in skip and 'astrom' in runs:
        _ = create_object_database(params, pconst, databases, verbose=verbose)
    # -------------------------------------------------------------------------
    # create reject database
    if 'reject' not in skip and 'reject' in runs:
        _ = create_reject_database(params, pconst, databases, verbose=verbose)


# =============================================================================
# Define calibration database functions
# =============================================================================
def create_calibration_database(params: ParamDict, pconst: PseudoConst,
                                databases: Dict[str, DatabaseM],
                                verbose: bool = False) -> Database:
    """
    Setup for the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    reset_path = params['DATABASE_DIR']
    # get columns and ctypes from pconst
    cdb_cols = pconst.CALIBRATION_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    calibdbm = databases['calib']
    # -------------------------------------------------------------------------
    # make database
    calibdb = drs_db.AperoDatabase(calibdbm.dburl, tablename=calibdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if calibdb.tablename in calibdb.get_tables():
        calibdb.backup()
        calibdb.delete_table(calibdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted calibration database')
    # add main table
    calibdb.add_table(calibdb.tablename,
                      columns=cdb_cols.columns,
                      indexes=cdb_cols.indexes,
                      uniques=cdb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created calibration database')
    # ---------------------------------------------------------------------
    # construct reset file
    reset_abspath = str(os.path.join(asset_dir, reset_path, calibdbm.dbreset))
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    calibdb.add_from_pandas(reset_entries)
    # -------------------------------------------------------------------------
    return calibdb


# =============================================================================
# Define telluric database functions
# =============================================================================
def create_telluric_database(params: ParamDict, pconst: PseudoConst,
                             databases: Dict[str, DatabaseM],
                             verbose: bool = False) -> Database:
    """
    Setup for the telluric database

    :param params: ParamDict, parmaeter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    reset_path = params['DATABASE_DIR']
    # get columns and ctypes from pconst
    tdb_cols = pconst.TELLURIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    telludbm = databases['tellu']
    # -------------------------------------------------------------------------
    # make database
    telludb = drs_db.AperoDatabase(telludbm.dburl, tablename=telludbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if telludb.tablename in telludb.get_tables():
        telludb.backup()
        telludb.delete_table(telludb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted telluric database')
    # add main table
    telludb.add_table(telludb.tablename,
                      columns=tdb_cols.columns,
                      indexes=tdb_cols.indexes,
                      uniques=tdb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created telluric database')
    # ---------------------------------------------------------------------
    # construct reset file
    reset_abspath = str(os.path.join(asset_dir, reset_path, telludbm.dbreset))
    # the rest file may not exist - this is okay for the telluric database
    if os.path.exists(reset_abspath):
        # get rows from reset file
        reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
        # add rows from reset text file
        telludb.add_from_pandas(reset_entries)
    # ---------------------------------------------------------------------
    return telludb


# =============================================================================
# Define index database functions
# =============================================================================
def create_fileindex_database(params: ParamDict, pconst: PseudoConst,
                              databases: Dict[str, DatabaseM],
                              verbose: bool = False) -> Database:
    """
    Setup for the file index database

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    idb_cols = pconst.FILEINDEX_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    findexdbm = databases['findex']
    # -------------------------------------------------------------------------
    # make database
    indexdb = drs_db.AperoDatabase(findexdbm.dburl, tablename=findexdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if indexdb.tablename in indexdb.get_tables():
        indexdb.backup()
        indexdb.delete_table(indexdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted file index database')
    # add main table
    indexdb.add_table(indexdb.tablename,
                      columns=idb_cols.columns,
                      indexes=idb_cols.indexes,
                      uniques=idb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created file index database')
    # -------------------------------------------------------------------------
    return indexdb


# =============================================================================
# Define log database functions
# =============================================================================
def create_log_database(params: ParamDict, pconst: PseudoConst,
                        databases: Dict[str, DatabaseM],
                        verbose: bool = False) -> Database:
    """
    Setup for the index database

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    ldb_cols = pconst.LOG_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    logdbm = databases['log']
    # -------------------------------------------------------------------------
    # make database
    logdb = drs_db.AperoDatabase(logdbm.dburl, tablename=logdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if logdb.tablename in logdb.get_tables():
        logdb.backup()
        logdb.delete_table(logdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted recipe log database')
    # add main table
    logdb.add_table(logdb.tablename,
                    columns=ldb_cols.columns,
                    indexes=ldb_cols.indexes,
                    uniques=ldb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created recipe log database')
    # -------------------------------------------------------------------------
    return logdb


# =============================================================================
# Define object database functions
# =============================================================================
def create_object_database(params: ParamDict, pconst: PseudoConst,
                           databases: Dict[str, DatabaseM],
                           verbose: bool = False) -> Database:
    """
    Setup for the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    objdb_cols = pconst.ASTROMETRIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    objectdbm = databases['astrom']
    # -------------------------------------------------------------------------
    # make database
    objectdb = drs_db.AperoDatabase(objectdbm.dburl,
                                    tablename=objectdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if objectdb.tablename in objectdb.get_tables():
        objectdb.backup()
        objectdb.delete_table(objectdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted astrometric database')
    # add main table
    objectdb.add_table(objectdb.tablename,
                       columns=objdb_cols.columns,
                       indexes=objdb_cols.indexes,
                       uniques=objdb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created astrometric database')
    # ---------------------------------------------------------------------
    # update object database from google sheet(s)
    update_object_database(params)
    # -------------------------------------------------------------------------
    return objectdb


def object_db_populated(params: ParamDict) -> bool:
    """
    Check that object database is populated
    """
    # need to load database
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # count rows in database
    count = objdbm.database.count()
    # return a boolean for object database populated
    return count > 0


def get_object_database(params: ParamDict, log: bool = True) -> Table:
    """
    Get the object database from google sheet (or file)
    and combine with pending / user table if required and found

    :param params: ParamDict, parameter dictionary of constants
    :param log: whether to log table read

    :return: astropy table, the object database
    """
    # set function name
    func_name = __NAME__ + '.get_object_database()'
    # get parameters from params
    gsheet_url = params['OBJ_LIST_GOOGLE_SHEET_URL']
    main_id = params['OBJ_LIST_GSHEET_MAIN_LIST_ID']
    pending_id = params['OBJ_LIST_GSHEET_PEND_LIST_ID']
    user_url = params['OBJ_LIST_GSHEET_USER_URL']
    user_id = params['OBJ_LIST_GSHEET_USER_ID']
    # object col name in google sheet
    gl_objcol = params['GL_OBJ_COL_NAME']
    # -------------------------------------------------------------------------
    # load pseudo constants
    pconst = constants.pload()
    # get object database column data types
    obj_data_types = dict()
    astrom_cols = pconst.ASTROMETRIC_DB_COLUMNS()
    # loop around columns and get data type
    for col in astrom_cols.columns:
        obj_data_types[col.name] = astrom_cols.get_datatype(col.name)
    # -------------------------------------------------------------------------
    # print that we are updating object database
    if log:
        WLOG(params, 'info', textentry('40-503-00039'))
    # -------------------------------------------------------------------------
    # deal with gsheet_url being local csv file
    if os.path.exists(gsheet_url):
        mainpath = os.path.join(gsheet_url, main_id)
        pendpath = os.path.join(gsheet_url, pending_id)
        try:
            maintable = Table.read(mainpath, format='csv')
        except Exception as e:
            # error msg: if OBJ_LIST_GOOGLE_SHEET_URL is local directory
            #            main_id must be a valid csv file.
            eargs = [mainpath, type(e), str(e), func_name]
            WLOG(params, 'error', textentry('09-002-00005', args=eargs))
            maintable = Table()
        # noinspection PyBroadException
        try:
            pendtable = Table.read(pendpath, format='csv')
        except Exception as _:
            pendtable = Table()
    else:
        # get google sheets
        maintable = drs_database.get_google_sheet(params, gsheet_url, main_id)
        pendtable = drs_database.get_google_sheet(params, gsheet_url,
                                                  pending_id)
    # force types in main table and pend table (so we can join them)
    maintable = _force_column_dtypes(maintable, obj_data_types)
    pendtable = _force_column_dtypes(pendtable, obj_data_types)
    # -------------------------------------------------------------------------
    # get the user table if defined
    if not drs_text.null_text(user_url, ['None', 'Null', '']):
        if os.path.exists(user_url):
            userpath = os.path.join(user_url, user_id)
            # noinspection PyBroadException
            try:
                usertable = Table.read(userpath, format='csv')
            except Exception as _:
                usertable = Table()
        else:
            usertable = drs_database.get_google_sheet(params, user_url, user_id)
    else:
        usertable = Table()
    # force types in user table
    if len(usertable) > 0:
        usertable = _force_column_dtypes(usertable, obj_data_types)
    # -------------------------------------------------------------------------
    # update main table with other tables (if we have entries in the pending
    #   table) and if those object name column not already in main table
    for _table in [pendtable, usertable]:
        # only do this if this table has some entries
        if len(_table) != 0:
            # make sure we have the object name column
            if gl_objcol in _table.colnames:
                pmask = ~np.in1d(_table[gl_objcol], maintable[gl_objcol])
                # add new columns to main table
                maintable = vstack([maintable, _table[pmask]])
    # return the main table
    return maintable


def update_object_database(params: ParamDict, log: bool = True):
    """
    Update the local object database - note this overwrites all entries in the
    local database

    By default this uses a googlesheet URL (OBJ_LIST_GOOGLE_SHEET_URL)
    + workbook ids to populate the object database
    (OBJ_LIST_GSHEET_MAIN_LIST_ID + OBJ_LIST_GSHEET_PEND_LIST_ID)

    however if OBJ_LIST_GOOGLE_SHEET_URL is a local directory one can set the
    OBJ_LIST_GSHEET_MAIN_LIST_ID + OBJ_LIST_GSHEET_PEND_LIST_ID to csv
    files for a complete offline reduction

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs update

    :return: None, updates local object database
    """
    # get pconst
    pconst = constants.pload()
    # get list of databases
    databases = list_databases(params)
    # get the object database (combined with pending + user table)
    maintable = get_object_database(params, log=log)
    # -------------------------------------------------------------------------
    # convert main table to a pandas dataframe
    df = maintable.to_pandas()
    # add a date added column
    df['DATE_ADDED'] = np.full(len(df), base.__now__.iso)
    # -------------------------------------------------------------------------
    # get columns and ctypes from pconst
    objdb_cols = pconst.ASTROMETRIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    objectdbm = databases['astrom']
    # -------------------------------------------------------------------------
    # make database
    objectdb = drs_db.AperoDatabase(objectdbm.dburl,
                                    tablename=objectdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if objectdb.tablename in objectdb.get_tables():
        objectdb.backup()
        objectdb.delete_table(objectdb.tablename)
    # add main table
    objectdb.add_table(objectdb.tablename,
                       columns=objdb_cols.columns,
                       indexes=objdb_cols.indexes,
                       uniques=objdb_cols.uniques)
    # ---------------------------------------------------------------------
    # add rows from pandas dataframe
    objectdb.add_from_pandas(df, tablename=objectdb.tablename)


# =============================================================================
# Define reject database functions
# =============================================================================
def create_reject_database(params: ParamDict, pconst: PseudoConst,
                           databases: Dict[str, DatabaseM],
                           verbose: bool = False) -> Database:
    """
    Setup for the reject database

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    rejectdb_cols = pconst.REJECT_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    rejectdbm = databases['reject']
    # -------------------------------------------------------------------------
    # make database
    rejectdb = drs_db.AperoDatabase(rejectdbm.dburl,
                                    tablename=rejectdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if rejectdb.tablename in rejectdb.get_tables():
        rejectdb.backup()
        rejectdb.delete_table(rejectdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted reject database')
    # add main table
    rejectdb.add_table(rejectdb.tablename,
                       columns=rejectdb_cols.columns,
                       indexes=rejectdb_cols.indexes,
                       uniques=rejectdb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created reject database')
    # ---------------------------------------------------------------------
    # update object database from google sheet(s)
    update_reject_database(params)
    # -------------------------------------------------------------------------
    return rejectdb


def reject_db_populated(params: ParamDict) -> bool:
    """
    Check that reject database is populated
    """
    # need to load database
    rejectdbm = drs_database.RejectDatabase(params)
    rejectdbm.load_db()
    # count rows in database
    count = rejectdbm.database.count()
    # return a boolean for object database populated
    return count > 0


def update_reject_database(params: ParamDict, log: bool = True):
    """
    Update the local reject database - note this overwrites all entries in the
    local database

    By default this uses a googlesheet URL (REJECT_LIST_GOOGLE_SHEET_URL)

    however if REJECT_LIST_GOOGLE_SHEET_URL is a local directory one can set the
    REJECT_LIST_GSHEET_MAIN_LIST_ID to a csv file for a complete offline 
    reduction

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs update

    :return: None, updates local object database
    """
    # get pconst
    pconst = constants.pload()
    # get list of databases
    databases = list_databases(params)
    # get the object database (combined with pending + user table)
    maintable = get_reject_database(params, log=log)
    # -------------------------------------------------------------------------
    # convert main table to a pandas dataframe
    df = maintable.to_pandas()
    # -------------------------------------------------------------------------
    # get columns and ctypes from pconst
    rejectdb_cols = pconst.REJECT_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    rejectdbm = databases['reject']
    # -------------------------------------------------------------------------
    # make database
    rejectdb = drs_db.AperoDatabase(rejectdbm.dburl, tablename=rejectdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if rejectdb.tablename in rejectdb.get_tables():
        rejectdb.backup()
        rejectdb.delete_table(rejectdb.tablename)
    # add main table
    rejectdb.add_table(rejectdb.tablename,
                       columns=rejectdb_cols.columns,
                       indexes=rejectdb_cols.indexes,
                       uniques=rejectdb_cols.uniques)
    # ---------------------------------------------------------------------
    # add rows from pandas dataframe
    rejectdb.add_from_pandas(df)


def get_reject_database(params: ParamDict, log: bool = True) -> Table:
    """
    Get the reject database from google sheet (or file)
    and combine with pending / user table if required and found

    :param params: ParamDict, parameter dictionary of constants
    :param log: whether to log table read

    :return: astropy table, the object database
    """
    # set function name
    func_name = __NAME__ + '.get_reject_database()'
    # get parameters from params
    gsheet_url = params['REJECT_LIST_GOOGLE_SHEET_URL']
    main_id = params['REJECT_LIST_GSHEET_MAIN_LIST_ID']
    # print that we are updating object database
    if log:
        WLOG(params, 'info', textentry('40-503-00046'))
    # -------------------------------------------------------------------------
    # load pseudo constants
    pconst = constants.pload()
    # get reject database column data types
    reject_data_types = dict()
    reject_cols = pconst.REJECT_DB_COLUMNS()
    # loop around columns and get data type
    for col in reject_cols.columns:
        reject_data_types[col.name] = reject_cols.get_datatype(col.name)
    # -------------------------------------------------------------------------
    # deal with gsheet_url being local csv file
    if os.path.exists(gsheet_url):
        mainpath = os.path.join(gsheet_url, main_id)
        try:
            maintable = Table.read(mainpath, format='csv')
        except Exception as e:
            # error msg: if REJECT_LIST_GOOGLE_SHEET_URL is local directory
            #            main_id must be a valid csv file
            eargs = [mainpath, type(e), str(e), func_name]
            WLOG(params, 'error', textentry('09-002-00006', args=eargs))
            maintable = Table()
    else:
        # get google sheets
        maintable = drs_database.get_google_sheet(params, gsheet_url, main_id)
    # force types in main table and pend table (so we can join them)
    maintable = _force_column_dtypes(maintable, reject_data_types)
    # -------------------------------------------------------------------------
    # return the main table
    return maintable


# =============================================================================
# Define misc functions
# =============================================================================
def _force_column_dtypes(table: Table, coltype: Dict[str, type]) -> Table:
    """
    Force a table to have specific data types

    :param table: astropy.table.Table instance
    :param coltype: list of types to force columns to
    :return:
    """
    # loop around columns and force types
    for col in table.colnames:
        # if we do not define this column remove it
        if col not in coltype:
            del table[col]
            continue
        # strings are a pain have to do them manually
        if hasattr(table[col], 'mask'):
            mask = table[col].mask
            values = np.array(table[col]).astype(coltype[col])
            table[col] = MaskedColumn(values, mask=mask)

        else:
            table[col] = np.array(table[col]).astype(coltype[col])
    # return the new table
    return table


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # test with spirou
    _params = constants.load()
    # install database
    install_databases(_params)

# =============================================================================
# End of code
# =============================================================================
