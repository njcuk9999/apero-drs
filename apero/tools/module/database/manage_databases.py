#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Completely recreate database from scratch

Created on 2020-08-2020-08-18 17:13

@author: cook
"""
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
            table = infodb.get('*', table=tablename, condition=condition,
                               return_pandas=True)
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
                                databases: Dict[str, DatabaseM]) -> Database:
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
    calibdb = drs_db.database_wrapper(calibdbm.kind, calibdbm.path)
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
    calibdb.add_from_pandas(reset_entries, table=calibdb.tname)
    # -------------------------------------------------------------------------
    return calibdb


def create_telluric_database(pconst: PseudoConst,
                             databases: Dict[str, DatabaseM]) -> Database:
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
    telludb = drs_db.database_wrapper(telludbm.kind, telludbm.path)
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
                          databases: Dict[str, DatabaseM]) -> Database:
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
    # -------------------------------------------------------------------------
    # construct directory
    indexdbm = databases['index']
    # -------------------------------------------------------------------------
    # make database
    indexdb = drs_db.database_wrapper(indexdbm.kind, indexdbm.path)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if indexdb.tname in indexdb.tables:
        indexdb.backup()
        indexdb.delete_table(indexdb.tname)
    # add main table
    indexdb.add_table(indexdb.tname, columns, ctypes, unique_cols=cuniques,
                      index_cols=cicols)
    # -------------------------------------------------------------------------
    return indexdb


def create_log_database(pconst: PseudoConst,
                        databases: Dict[str, DatabaseM]) -> Database:
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
    logdb = drs_db.database_wrapper(logdbm.kind, logdbm.path)
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
                           databases: Dict[str, DatabaseM]) -> Database:
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
    # construct reset file
    reset_abspath = os.path.join(asset_dir, reset_path, objectdbm.dbreset)
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    objectdb.add_from_pandas(reset_entries, table=objectdb.tname,
                             unique_cols=cuniques)
    # -------------------------------------------------------------------------
    return objectdb


def make_object_reset(params: ParamDict):
    """
    This makes the reset file starting with the googlesheet
    (must clean the current database)

    :param params: ParamDict, parameter dictionary of constants

    :return: None - makes reset.obj.csv
    """
    # get parameters from params
    rel_path = os.path.join(params['DRS_RESET_ASSETS_PATH'],
                            params['INSTRUMENT'].lower())
    asset_dir = drs_data.construct_path(params, '', rel_path)
    reset_path = params['DATABASE_DIR']
    # get pconst
    pconst = constants.pload()
    # need to load database
    objdbm = drs_database.ObjectDatabase(params)
    objdbm.load_db()
    # remove table if it already exists
    if objdbm.database.tname in objdbm.database.tables:
        objdbm.database.backup()
        objdbm.database.delete_table(objdbm.database.tname)
    # get columns and ctypes from pconst
    objdb_cols = pconst.OBJECT_DB_COLUMNS()
    columns = list(objdb_cols.names)
    ctypes = list(objdb_cols.datatypes)
    cuniques = list(objdb_cols.unique_cols)
    cicols = list(objdb_cols.index_cols)
    # add main table
    objdbm.database.add_table(objdbm.database.tname, columns, ctypes,
                              unique_cols=cuniques, index_cols=cicols)
    # get google sheets
    gtable = gen_pp.get_google_sheet(params,
                                     params['OBJ_LIST_GOOGLE_SHEET_URL'],
                                     params['OBJ_LIST_GOOGLE_SHEET_WNUM'])
    objnames = list(np.unique(gtable['OBJECT']))
    # resolve targets
    gen_pp.resolve_targets(params, objnames, database=objdbm)
    # get table
    table = objdbm.get_entries('*')
    # write to csv file
    table.to_csv(os.path.join(asset_dir, reset_path, objdbm.dbreset),
                 index=False)


def update_object_database(params: ParamDict):
    """
    Update the local object database - note this overwrites all entries in the
    local database - i.e. we assume the google sheet is more correct
    however it does leave entries that are not in the google sheet in the
    local object database

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, updates local object database
    """
    # get psuedo constants
    pconst = constants.pload()
    # print that we are updating object database
    WLOG(params, 'info', textentry('40-503-00039'))
    # gaia col name in google sheet
    gl_gaia_colname = params['GL_GAIA_COL_NAME']
    # object col name in google sheet
    gl_obj_colname = params['GL_OBJ_COL_NAME']
    # need to load database
    objdbm = drs_database.ObjectDatabase(params)
    objdbm.load_db()
    # get google sheets
    gtable = gen_pp.get_google_sheet(params,
                                     params['OBJ_LIST_GOOGLE_SHEET_URL'],
                                     params['OBJ_LIST_GOOGLE_SHEET_WNUM'])
    # update rows in gtable
    for row in tqdm(range(len(gtable))):
        # get object name and gaia id
        objname = gtable[gl_obj_colname][row]
        gaiaid = gtable[gl_gaia_colname][row]
        # TODO: Need column in database / reset / google sheet or some way
        #       to switch between
        gaiadr = 'Gaia DR2'
        # clean up object name
        cobjname = pconst.DRS_OBJ_NAME(objname)
        # log progress ( as debug )
        WLOG(params, 'debug', textentry('40-503-00040', args=[objname, gaiaid]))
        # get astro object (current settings)
        astro_obj = gen_pp.AstroObject(params, pconst, gaiaid, gaiadr, np.nan,
                                       np.nan, objdbm, cobjname, np.nan, np.nan,
                                       np.nan, np.nan, np.nan)
        # resolve target (with current properties)
        astro_obj.update_target(gtable)
        # write to database
        if astro_obj.gaia_id is not None:
            astro_obj.write_obj(objdbm)


def create_lang_database(databases: Dict[str, Union[DatabaseM, BaseDatabaseM]]
                         ) -> Database:
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
    langdb = drs_db.database_wrapper(langdbm.kind, langdbm.path)
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
    langdb.add_from_pandas(reset_entries0[~mask0], table=langdb.tname)
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
    df = db.database.get('*', table=db.database.tname, return_pandas=True)
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
    db.database.add_from_pandas(df, db.database.tname, if_exists=joinmode,
                                unique_cols=ucols)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # test with spirou
    _params = constants.load()

    # We need to make the object reset
    make_object_reset(_params)

    # install database
    install_databases(_params)

# =============================================================================
# End of code
# =============================================================================
