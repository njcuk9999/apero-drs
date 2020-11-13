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
from apero.core.utils import drs_data
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
# Get database definition
Database = drs_db.Database
DatabaseM = drs_database.DatabaseManager
BaseDatabaseM = drs_db.BaseDatabaseManager
# Get ParamDict
ParamDict = constants.ParamDict
PseudoConst = pseudo_const.PseudoConstants


# =============================================================================
# Define functions
# =============================================================================
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
    pconst = constants.pload(params['INSTRUMENT'])
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
    columns, ctypes = pconst.CALIBRATION_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    calibdbm = databases['calib']
    # -------------------------------------------------------------------------
    # make database
    calibdb = drs_db.database_wrapper(calibdbm.kind, calibdbm.path)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in calibdb.tables:
        calibdb.delete_table('MAIN')
    # add main table
    calibdb.add_table('MAIN', columns, ctypes)
    # ---------------------------------------------------------------------
    # construct reset file
    reset_abspath = os.path.join(asset_dir, reset_path, calibdbm.dbreset)
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    calibdb.add_from_pandas(reset_entries, table='MAIN')
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
    columns, ctypes = pconst.TELLURIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    telludbm = databases['tellu']
    # -------------------------------------------------------------------------
    # make database
    telludb = drs_db.database_wrapper(telludbm.kind, telludbm.path)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in telludb.tables:
        telludb.delete_table('MAIN')
    # add main table
    telludb.add_table('MAIN', columns, ctypes)
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
    columns, ctypes = pconst.INDEX_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    indexdbm = databases['index']
    # -------------------------------------------------------------------------
    # make database
    indexdb = drs_db.database_wrapper(indexdbm.kind, indexdbm.path)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in indexdb.tables:
        indexdb.delete_table('MAIN')
    # add main table
    indexdb.add_table('MAIN', columns, ctypes)
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
    columns, ctypes = pconst.LOG_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    logdbm = databases['log']
    # -------------------------------------------------------------------------
    # make database
    logdb = drs_db.database_wrapper(logdbm.kind, logdbm.path)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in logdb.tables:
        logdb.delete_table('MAIN')
    # add main table
    logdb.add_table('MAIN', columns, ctypes)
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
    columns, ctypes = pconst.OBJECT_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    objectdbm = databases['object']
    # -------------------------------------------------------------------------
    # make database
    objectdb = drs_db.database_wrapper(objectdbm.kind, objectdbm.path)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in objectdb.tables:
        objectdb.delete_table('MAIN')
    # add main table
    objectdb.add_table('MAIN', columns, ctypes)
    # ---------------------------------------------------------------------
    # construct reset file
    reset_abspath = os.path.join(asset_dir, reset_path, objectdbm.dbreset)
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    objectdb.add_from_pandas(reset_entries, table='MAIN')
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
    pconst = constants.pload(params['INSTRUMENT'])
    # need to load database
    objdbm = drs_database.ObjectDatabase(params)
    objdbm.load_db()
    # remove table if it already exists
    if 'MAIN' in objdbm.database.tables:
        objdbm.database.delete_table('MAIN')
    # get columns and ctypes from pconst
    columns, ctypes = pconst.OBJECT_DB_COLUMNS()
    # add main table
    objdbm.database.add_table('MAIN', columns, ctypes)
    # get google sheets
    gtable = gen_pp.get_google_sheet(params['OBJ_LIST_GOOGLE_SHEET_URL'],
                                     params['OBJ_LIST_GOOGLE_SHEET_WNUM'])
    objnames = list(np.unique(gtable['OBJNAME']))
    # resolve targets
    gen_pp.resolve_targets(params, objnames, database=objdbm)
    # get table
    table = objdbm.get_entries('*')
    # write to csv file
    table.to_csv(os.path.join(asset_dir, reset_path, objdbm.dbreset),
                 index=False)


# def create_params_database(pconst, databases) -> Database:
#     """
#     Setup for the index database
#     :param params:
#     :param pconst:
#     :return:
#     """
#     # get columns and ctypes from pconst
#     columns, ctypes = pconst.PARAMS_DB_COLUMNS()
#     # -------------------------------------------------------------------------
#     # construct directory
#     params_abspath = databases['params']
#     # -------------------------------------------------------------------------
#     # make database
#     paramsdb = Database(params_abspath)
#     # -------------------------------------------------------------------------
#     if 'MAIN' in paramsdb.tables:
#         paramsdb.delete_table('MAIN')
#     # add main table
#     paramsdb.add_table('MAIN', columns, ctypes)
#     # -------------------------------------------------------------------------
#     return paramsdb


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
    columns = langdbm.columns
    ctypes = langdbm.ctypes
    # -------------------------------------------------------------------------
    if 'MAIN' in langdb.tables:
        langdb.delete_table('MAIN')
    # add main table
    langdb.add_table('MAIN', columns, ctypes)
    # ---------------------------------------------------------------------
    # add rows from reset text file for default file
    # ---------------------------------------------------------------------
    # get rows from reset file
    reset_entries0 = pd.read_csv(langdbm.resetfile, skipinitialspace=True)
    # remove entries with KEYNAME == nan
    mask0 = np.array(reset_entries0['KEYNAME']).astype(str) == 'nan'
    # add rows from reset text file
    langdb.add_from_pandas(reset_entries0[~mask0], table='MAIN')
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
        langdbm.add_entry(commit=False, **entry)
    # commit
    langdbm.database.commit()
    # -------------------------------------------------------------------------
    return langdb


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # test with spirou
    _params = constants.load('SPIROU')

    # We need to make the object reset
    make_object_reset(_params)

    # install database
    install_databases(_params)

# =============================================================================
# End of code
# =============================================================================
