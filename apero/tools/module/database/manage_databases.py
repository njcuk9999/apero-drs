#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Completely recreate database from scratch

Created on 2020-08-2020-08-18 17:13

@author: cook
"""
from astropy.table import Table, vstack, MaskedColumn
import numpy as np
import os
import pandas as pd
from typing import Dict, List, Union

from apero.base import base
from apero.base import drs_db
from apero.core import constants
from apero.core.instruments.default import pseudo_const
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_data
from apero import lang
from apero.science.preprocessing import gen_pp

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
Database = drs_db.Database
DatabaseM = drs_database.DatabaseManager
BaseDatabaseM = drs_db.BaseDatabaseManager
# Get ParamDict
ParamDict = constants.ParamDict
PseudoConst = pseudo_const.PseudoConstants
# Get Logging function
WLOG = drs_log.wlog
# get textentry
textentry = lang.textentry
# define object column datatypes (force consistency)
OBJ_DATA_TYPES = dict()
OBJ_DATA_TYPES['OBJNAME'] = str
OBJ_DATA_TYPES['ORIGINAL_NAME'] = str
OBJ_DATA_TYPES['ALIASES'] = str
OBJ_DATA_TYPES['RA_DEG'] = float
OBJ_DATA_TYPES['RA_SOURCE'] = str
OBJ_DATA_TYPES['DEC_DEG'] = float
OBJ_DATA_TYPES['DEC_SOURCE'] = str
OBJ_DATA_TYPES['EPOCH'] = float
OBJ_DATA_TYPES['PMRA'] = float
OBJ_DATA_TYPES['PMRA_SOURCE'] = str
OBJ_DATA_TYPES['PMDE'] = float
OBJ_DATA_TYPES['PMDE_SOURCE'] = str
OBJ_DATA_TYPES['PLX'] = float
OBJ_DATA_TYPES['PLX_SOURCE'] = str
OBJ_DATA_TYPES['RV'] = float
OBJ_DATA_TYPES['RV_SOURCE'] = str
OBJ_DATA_TYPES['SP_TYPE'] = str
OBJ_DATA_TYPES['SP_SOURCE'] = str
OBJ_DATA_TYPES['TEFF'] = float
OBJ_DATA_TYPES['TEFF_SOURCE'] = str
OBJ_DATA_TYPES['NOTES'] = str
OBJ_DATA_TYPES['USED'] = int

# =============================================================================
# Define functions
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
    # deal with mysql
    if dparams['USE_MYSQL']:
        # get path
        path = ''
        # get hostname / user / password
        host = dparams['MYSQL']['HOST']
        user = dparams['MYSQL']['USER']
        userdb = dparams['MYSQL']['DATABASE']
        passwd = dparams['MYSQL']['PASSWD']
        databasename = 'information_schema'
        tablename = 'processlist'
        # wrap in a try (this may not always work
        try:
            # get database connection
            infodb = drs_db.MySQLDatabase(path=path, host=host, user=user,
                                          passwd=passwd,
                                          database=databasename,
                                          tablename=tablename,
                                          absolute_table_name=True)
            # set up condition: only this users processes and only from the
            #   required database and that have been active for more than
            #   60 seconds
            cargs = [user, userdb, timeout]
            condition = 'USER="{0}" AND DB="{1}" AND TIME > {2}'.format(*cargs)
            # log condition
            WLOG(params, '', 'Condition')
            WLOG(params, '', '\t' + condition)
            # get all processes that were started by user
            table = infodb.get('*', condition=condition, return_pandas=True)
            # get ids from table
            ids = list(table['ID'].values)
            # log how many ids found
            WLOG(params, '', 'Found {0} processes'.format(len(ids)))
            # try to kill processes
            for _id in ids:
                # set up command
                command = 'kill {0}'.format(_id)
                # execute command
                try:
                    infodb.execute(command, False)
                    # log killing
                    WLOG(params, '', '\t' + command)
                except Exception:
                    continue
            # close the connection
            infodb._conn_.close()
        # just return if there is an exception
        except Exception:
            return


def list_databases(params: ParamDict) -> Dict[str, DatabaseM]:
    # set up storage
    databases = dict()
    # get databases from managers (later databases)
    calibdbm = drs_database.CalibrationDatabase(params, check=False)
    telludbm = drs_database.TelluricDatabase(params, check=False)
    indexdbm = drs_database.IndexDatabase(params, check=False)
    logdbm = drs_database.LogDatabase(params, check=False)
    objectdbm = drs_database.ObjectDatabase(params, check=False)
    landdbm = drs_db.LanguageDatabase(check=False)
    # add to storage
    databases['calib'] = calibdbm
    databases['tellu'] = telludbm
    databases['index'] = indexdbm
    databases['log'] = logdbm
    databases['object'] = objectdbm
    databases['lang'] = landdbm
    # return the databases
    return databases


def install_databases(params: ParamDict, skip: Union[List[str], None] = None):
    # deal with skip
    if skip is None:
        skip = []
    # get database paths
    databases = list_databases(params)
    # load pseudo constants
    pconst = constants.pload()
    # -------------------------------------------------------------------------
    # create calibration database
    if 'calib' not in skip:
        _ = create_calibration_database(params, pconst, databases)
    # -------------------------------------------------------------------------
    # create telluric database
    if 'tellu' not in skip:
        _ = create_telluric_database(pconst, databases)
    # -------------------------------------------------------------------------
    # create index database
    if 'index' not in skip:
        _ = create_index_database(pconst, databases)
    # -------------------------------------------------------------------------
    # create log database
    if 'log' not in skip:
        _ = create_log_database(pconst, databases)
    # -------------------------------------------------------------------------
    # create object database
    if 'object' not in skip:
        _ = create_object_database(params, pconst, databases)
    # -------------------------------------------------------------------------
    # # create params database
    # if 'params' not in skip:
    #     paramsdb = create_params_database(pconst, databases)
    # -------------------------------------------------------------------------
    # create language database
    if 'lang' not in skip:
        _ = create_lang_database(databases)


def create_calibration_database(params: ParamDict, pconst: PseudoConst,
                                databases: Dict[str, DatabaseM],
                                tries: int = 20) -> Database:
    """
    Setup for the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers

    :returns: database - the telluric database
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    reset_path = params['DATABASE_DIR']
    # get columns and ctypes from pconst
    cdb_cols = pconst.CALIBRATION_DB_COLUMNS()
    columns = list(cdb_cols.names)
    ctypes = list(cdb_cols.datatypes)
    cicols = list(cdb_cols.index_cols)
    # -------------------------------------------------------------------------
    # construct directory
    calibdbm = databases['calib']
    # -------------------------------------------------------------------------
    # make database
    calibdb = drs_db.database_wrapper(calibdbm.kind, calibdbm.path, tries=tries)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if calibdb.tname in calibdb.tables:
        calibdb.backup()
        calibdb.delete_table(calibdb.tname)
    # add main table
    calibdb.add_table(calibdb.tname, columns, ctypes, index_cols=cicols)
    # ---------------------------------------------------------------------
    # construct reset file
    reset_abspath = os.path.join(asset_dir, reset_path, calibdbm.dbreset)
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    calibdb.add_from_pandas(reset_entries)
    # -------------------------------------------------------------------------
    return calibdb


def create_telluric_database(pconst: PseudoConst,
                             databases: Dict[str, DatabaseM],
                             tries: int = 20) -> Database:
    """
    Setup for the telluric database

    :param pconst: Pseudo constants
    :param databases: dictionary of database managers

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    tdb_cols = pconst.TELLURIC_DB_COLUMNS()
    columns = list(tdb_cols.names)
    ctypes = list(tdb_cols.datatypes)
    cicols = list(tdb_cols.index_cols)
    # -------------------------------------------------------------------------
    # construct directory
    telludbm = databases['tellu']
    # -------------------------------------------------------------------------
    # make database
    telludb = drs_db.database_wrapper(telludbm.kind, telludbm.path, tries=tries)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if telludb.tname in telludb.tables:
        telludb.backup()
        telludb.delete_table(telludb.tname)
    # add main table
    telludb.add_table(telludb.tname, columns, ctypes, index_cols=cicols)
    # -------------------------------------------------------------------------
    return telludb


def create_index_database(pconst: PseudoConst,
                          databases: Dict[str, DatabaseM],
                          tries: int = 20) -> Database:
    """
    Setup for the index database

    :param pconst: Pseudo constants
    :param databases: dictionary of database managers

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    idb_cols = pconst.INDEX_DB_COLUMNS()
    columns = list(idb_cols.names)
    ctypes = list(idb_cols.datatypes)
    cuniques = list(idb_cols.unique_cols)
    cicols = list(idb_cols.index_cols)
    cigroups = idb_cols.get_index_groups()
    # -------------------------------------------------------------------------
    # construct directory
    indexdbm = databases['index']
    # -------------------------------------------------------------------------
    # make database
    indexdb = drs_db.database_wrapper(indexdbm.kind, indexdbm.path, tries=tries)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if indexdb.tname in indexdb.tables:
        indexdb.backup()
        indexdb.delete_table(indexdb.tname)
    # add main table
    indexdb.add_table(indexdb.tname, columns, ctypes, unique_cols=cuniques,
                      index_cols=cicols, index_groups=cigroups)
    # -------------------------------------------------------------------------
    return indexdb


def create_log_database(pconst: PseudoConst,
                        databases: Dict[str, DatabaseM],
                        tries: int = 20) -> Database:
    """
    Setup for the index database

    :param pconst: Pseudo constants
    :param databases: dictionary of database managers

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    ldb_cols = pconst.LOG_DB_COLUMNS()
    columns = list(ldb_cols.names)
    ctypes = list(ldb_cols.datatypes)
    cicols = list(ldb_cols.index_cols)
    # -------------------------------------------------------------------------
    # construct directory
    logdbm = databases['log']
    # -------------------------------------------------------------------------
    # make database
    logdb = drs_db.database_wrapper(logdbm.kind, logdbm.path, tries=tries)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if logdb.tname in logdb.tables:
        logdb.backup()
        logdb.delete_table(logdb.tname)
    # add main table
    logdb.add_table(logdb.tname, columns, ctypes, index_cols=cicols)
    # -------------------------------------------------------------------------
    return logdb


def create_object_database(params: ParamDict, pconst: PseudoConst,
                           databases: Dict[str, DatabaseM],
                           tries: int = 20) -> Database:
    """
    Setup for the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    objdb_cols = pconst.OBJECT_DB_COLUMNS()
    columns = list(objdb_cols.names)
    ctypes = list(objdb_cols.datatypes)
    cuniques = list(objdb_cols.unique_cols)
    cindexs = list(objdb_cols.index_cols)
    # -------------------------------------------------------------------------
    # construct directory
    objectdbm = databases['object']
    # -------------------------------------------------------------------------
    # make database
    objectdb = drs_db.database_wrapper(objectdbm.kind, objectdbm.path,
                                       tries=tries)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if objectdb.tname in objectdb.tables:
        objectdb.backup()
        objectdb.delete_table(objectdb.tname)
    # add main table
    objectdb.add_table(objectdb.tname, columns, ctypes, unique_cols=cuniques,
                       index_cols=cindexs)
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
    objdbm = drs_database.ObjectDatabase(params)
    objdbm.load_db()
    # count rows in database
    count = objdbm.database.count()
    # return a boolean for object database populated
    return count > 0


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

    :return: None, updates local object database
    """
    # get parameters from params
    gsheet_url = params['OBJ_LIST_GOOGLE_SHEET_URL']
    main_id = params['OBJ_LIST_GSHEET_MAIN_LIST_ID']
    pending_id = params['OBJ_LIST_GSHEET_PEND_LIST_ID']
    user_url = params['OBJ_LIST_GSHEET_USER_URL']
    user_id = params['OBJ_LIST_GSHEET_USER_ID']
    # get pconst
    pconst = constants.pload()
    # get list of databases
    databases = list_databases(params)
    # object col name in google sheet
    gl_objcol = params['GL_OBJ_COL_NAME']
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
            # TODO: move to language database
            emsg = ('Error: if OBJ_LIST_GOOGLE_SHEET_URL is local directory'
                    ' main_id must be a valid csv file. \nError {0}: {1}')
            eargs = [type(e), str(e)]
            WLOG(params, 'error', emsg.format(*eargs))
            maintable = Table()
        try:
            pendtable = Table.read(pendpath, format='csv')
        except Exception as _:
            pendtable = Table()
    else:
        # get google sheets
        maintable = gen_pp.get_google_sheet(params, gsheet_url, main_id)
        pendtable = gen_pp.get_google_sheet(params, gsheet_url, pending_id)
    # force types in main table and pend table (so we can join them)
    maintable = _force_column_dtypes(maintable, OBJ_DATA_TYPES)
    pendtable = _force_column_dtypes(pendtable, OBJ_DATA_TYPES)
    # -------------------------------------------------------------------------
    # get the user table if defined
    if not drs_text.null_text(user_url, ['None', 'Null', '']):
        if os.path.exists(user_url):
            userpath = os.path.join(user_url, user_id)
            try:
                usertable = Table.read(userpath, format='csv')
            except Exception as _:
                usertable = Table()
        else:
            usertable = gen_pp.get_google_sheet(params, user_url, user_id)
    else:
        usertable = Table()
    # force types in user table
    if len(usertable) > 0:
        usertable = _force_column_dtypes(usertable, OBJ_DATA_TYPES)
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
    # -------------------------------------------------------------------------
    # convert main table to a pandas dataframe
    df = maintable.to_pandas()
    # add a date added column
    df['DATE_ADDED'] = np.full(len(df), base.__now__.iso)
    # -------------------------------------------------------------------------
    # get columns and ctypes from pconst
    objdb_cols = pconst.OBJECT_DB_COLUMNS()
    columns = list(objdb_cols.names)
    ctypes = list(objdb_cols.datatypes)
    cuniques = list(objdb_cols.unique_cols)
    cindexs = list(objdb_cols.index_cols)
    # -------------------------------------------------------------------------
    # construct directory
    objectdbm = databases['object']
    # -------------------------------------------------------------------------
    # make database
    objectdb = drs_db.database_wrapper(objectdbm.kind, objectdbm.path)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if objectdb.tname in objectdb.tables:
        objectdb.backup()
        objectdb.delete_table(objectdb.tname)
    # add main table
    objectdb.add_table(objectdb.tname, columns, ctypes, unique_cols=cuniques,
                       index_cols=cindexs)
    # ---------------------------------------------------------------------
    # add rows from pandas dataframe
    objectdb.add_from_pandas(df, unique_cols=cuniques)


def _force_column_dtypes(table: Table, coltype: Dict[str, type]) -> Table:
    """
    Force a table to have specific data types

    :param table: astropy.table.Table instance
    :param coltype: list of types to force columns to
    :return:
    """
    # loop around columns and force types
    for col in table.colnames:
        # strings are a pain have to do them manually
        if hasattr(table[col], 'mask'):
            mask = table[col].mask
            values = np.array(table[col]).astype(coltype[col])
            table[col] = MaskedColumn(values, mask=mask)

        else:
            table[col] = np.array(table[col]).astype(coltype[col])
    # return the new table
    return table



# def update_object_database_old(params: ParamDict):
#     """
#     Update the local object database - note this overwrites all entries in the
#     local database - i.e. we assume the google sheet is more correct
#     however it does leave entries that are not in the google sheet in the
#     local object database
#
#     :param params: ParamDict, the parameter dictionary of constants
#
#     :return: None, updates local object database
#     """
#     # get psuedo constants
#     pconst = constants.pload()
#     # print that we are updating object database
#     WLOG(params, 'info', textentry('40-503-00039'))
#     # gaia col name in google sheet
#     gl_gaia_colname = params['GL_GAIA_COL_NAME']
#     # object col name in google sheet
#     gl_obj_colname = params['GL_OBJ_COL_NAME']
#     # need to load database
#     objdbm = drs_database.ObjectDatabase(params)
#     objdbm.load_db()
#     # get google sheets
#     gtable = gen_pp.get_google_sheet(params,
#                                      params['OBJ_LIST_GOOGLE_SHEET_URL'],
#                                      params['OBJ_LIST_GOOGLE_SHEET_WNUM'])
#     # update rows in gtable
#     for row in tqdm(range(len(gtable))):
#         # get object name and gaia id
#         objname = gtable[gl_obj_colname][row]
#         gaiaid = gtable[gl_gaia_colname][row]
#         # TODO: Need column in database / reset / google sheet or some way
#         #       to switch between
#         gaiadr = 'Gaia DR2'
#         # clean up object name
#         cobjname = pconst.DRS_OBJ_NAME(objname)
#         # log progress ( as debug )
#         WLOG(params, 'debug', textentry('40-503-00040', args=[objname, gaiaid]))
#         # get astro object (current settings)
#         astro_obj = gen_pp.AstroObject(params, pconst, gaiaid, gaiadr, np.nan,
#                                        np.nan, objdbm, cobjname, np.nan, np.nan,
#                                        np.nan, np.nan, np.nan)
#         # resolve target (with current properties)
#         astro_obj.update_target(gtable)
#         # write to database
#         if astro_obj.gaia_id is not None:
#             astro_obj.write_obj(objdbm)


def create_lang_database(databases: Dict[str, Union[DatabaseM, BaseDatabaseM]],
                         tries: int = 20) -> Database:
    """
    Setup for the index database

    :param pconst: Pseudo constants
    :param databases: dictionary of database managers

    :returns: database - the telluric database
    """
    # -------------------------------------------------------------------------
    # construct directory
    langdbm = databases['lang']
    assert isinstance(langdbm, drs_db.LanguageDatabase)
    # -------------------------------------------------------------------------
    # make database
    langdb = drs_db.database_wrapper(langdbm.kind, langdbm.path, tries=tries)
    lang_cols = langdbm.columns
    columns = list(lang_cols.names)
    ctypes = list(lang_cols.datatypes)
    cicols = list(lang_cols.index_cols)
    # -------------------------------------------------------------------------
    if langdb.tname in langdb.tables:
        langdb.backup()
        langdb.delete_table(langdb.tname)
    # add main table
    langdb.add_table(langdb.tname, columns, ctypes, index_cols=cicols)
    # ---------------------------------------------------------------------
    # add rows from reset text file for default file
    # ---------------------------------------------------------------------
    # get rows from reset file
    reset_entries0 = pd.read_csv(langdbm.resetfile, skipinitialspace=True)
    # remove entries with KEYNAME == nan
    mask0 = np.array(reset_entries0['KEYNAME']).astype(str) == 'nan'
    # add rows from reset text file
    langdb.add_from_pandas(reset_entries0[~mask0])
    # ---------------------------------------------------------------------
    # add rows from reset text file for instrument file
    # ---------------------------------------------------------------------
    # get rows from instrument file
    reset_entries1 = pd.read_csv(langdbm.instruement_resetfile,
                                 skipinitialspace=True)
    # remove entries with KEYNAME == nan
    mask1 = np.array(reset_entries1['KEYNAME']).astype(str) == 'nan'
    reset_entries1 = reset_entries1[~mask1]
    # reload database into landgm
    langdbm.load_db(check=False)
    # need to loop around rows and add them one by one for instrument
    for row in range(len(reset_entries1)):
        # get row data
        rowdata = reset_entries1.iloc[row]
        # fill values
        entry = dict()
        entry['key'] = rowdata['KEYNAME']
        entry['kind'] = rowdata['KIND']
        entry['comment'] = rowdata['KEYDESC']
        entry['arguments'] = rowdata['ARGUMENTS']
        entry['textdict'] = dict()
        for language in base.LANGUAGES:
            entry['textdict'][language] = rowdata[language]
        # add entry
        langdbm.add_entry(**entry)
    # -------------------------------------------------------------------------
    return langdb


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
                    infilename: str, joinmode: str = 'replace'):
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
    # get pconst
    pconst = constants.pload()
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
    # get unique columns
    if 'INDEX' in db.database.tname:
        idb_cols = pconst.INDEX_DB_COLUMNS()
        ucols = list(idb_cols.unique_cols)
    elif 'OBJECT' in db.database.tname:
        odb_cols = pconst.OBJECT_DB_COLUMNS()
        ucols = list(odb_cols.unique_cols)
    else:
        ucols = None
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
    db.database.add_from_pandas(df, if_exists=joinmode, unique_cols=ucols)


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
