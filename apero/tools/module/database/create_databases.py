#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Completely recreate database from scratch

Created on 2020-08-2020-08-18 17:13

@author: cook
"""
import os
import pandas as pd

from apero.core import constants
from apero.core.core import drs_database2 as drs_database

# =============================================================================
# Define variables
# =============================================================================
Database = drs_database.Database


# =============================================================================
# Define functions
# =============================================================================
def list_databases(params):
    # set up storage
    databases = dict()
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    calib_dir = params['DRS_CALIB_DB']
    calib_file = params['CALIB_DB_NAME']
    tellu_dir = params['DRS_TELLU_DB']
    tellu_file = params['TELLU_DB_NAME']
    index_dir = params['DATABASE_DIR']
    index_file = params['INDEX_DB_NAME']
    log_dir = params['DATABASE_DIR']
    log_file = params['LOG_DB_NAME']
    object_dir = params['DATABASE_DIR']
    object_file = params['OBJECT_DB_NAME']
    params_dir = params['DATABASE_DIR']
    params_file = params['LOG_DB_NAME']
    # construct paths
    calib_abspath = os.path.join(calib_dir, calib_file)
    tellu_abspath = os.path.join(tellu_dir, tellu_file)
    index_abspath = os.path.join(asset_dir, index_dir, index_file)
    log_abspath = os.path.join(asset_dir, log_dir, log_file)
    object_abspath = os.path.join(asset_dir, object_dir, object_file)
    params_abspath = os.path.join(asset_dir, params_dir, params_file)
    # add to storage
    databases['calib'] = calib_abspath
    databases['tellu'] = tellu_abspath
    databases['index'] = index_abspath
    databases['log'] = log_abspath
    databases['object'] = object_abspath
    databases['params'] = params_abspath
    # return the databases
    return databases



def create_databases(params, skip=None):

    # deal with skip
    if skip is None:
        skip = []

    # TODO: remove - for tests only
    params.set('CALIB_DB_NAME', value='calib.db')
    params.set('TELLU_DB_NAME', value='tellu.db')

    # get database paths
    databases = list_databases(params)

    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # -------------------------------------------------------------------------
    # create calibration database
    if 'calib' not in skip:
        calibdb = create_calibration_database(params, pconst, databases)
    # -------------------------------------------------------------------------
    # create telluric database
    if 'tellu' not in skip:
        telludb = create_telluric_database(pconst, databases)
    # -------------------------------------------------------------------------
    # create index database
    if 'index' not in skip:
        indexdb = create_index_database(pconst, databases)
    # -------------------------------------------------------------------------
    # create log database
    if 'log' not in skip:
        logdb = create_log_database(pconst, databases)
    # -------------------------------------------------------------------------
    # create object database
    if 'object' not in skip:
        objectdb = create_object_database(params, pconst, databases)
    # -------------------------------------------------------------------------
    # create params database
    if 'params' not in skip:
        paramsdb = create_params_database(pconst, databases)
    # -------------------------------------------------------------------------


def create_calibration_database(params, pconst, databases) -> Database:
    """
    Setup for the calibration database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params

    asset_dir = params['DRS_DATA_ASSETS']
    reset_path = params['DATABASE_DIR']
    reset_file = params['CALIB_DB_RESET']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.CALIBRATION_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    calib_abspath = databases['calib']
    # -------------------------------------------------------------------------
    # make database
    calibdb = Database(calib_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in calibdb.tables:
        calibdb.delete_table('MAIN')
    # add main table
    calibdb.add_table('MAIN', columns, ctypes)
    # ---------------------------------------------------------------------
    # construct reset file
    reset_abspath = os.path.join(asset_dir, reset_path, reset_file)
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    calibdb.add_from_pandas(reset_entries, 'MAIN')
    # -------------------------------------------------------------------------
    return calibdb


def create_telluric_database(pconst, databases) -> Database:
    """
    Setup for the telluric database
    :param params:
    :param pconst:
    :return:
    """
    # get columns and ctypes from pconst
    columns, ctypes = pconst.TELLURIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    tellu_abspath = databases['tellu']
    # -------------------------------------------------------------------------
    # make database
    telludb = Database(tellu_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in telludb.tables:
        telludb.delete_table('MAIN')
    # add main table
    telludb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    return telludb


def create_index_database(pconst, databases) -> Database:
    """
    Setup for the index database
    :param params:
    :param pconst:
    :return:
    """
    # get columns and ctypes from pconst
    columns, ctypes = pconst.INDEX_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    index_abspath = databases['index']
    # -------------------------------------------------------------------------
    # make database
    indexdb = Database(index_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in indexdb.tables:
        indexdb.delete_table('MAIN')
    # add main table
    indexdb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    return indexdb


def create_log_database(pconst, databases) -> Database:
    """
    Setup for the index database
    :param params:
    :param pconst:
    :return:
    """
    # get columns and ctypes from pconst
    columns, ctypes = pconst.TELLURIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    log_abspath = databases['log']
    # -------------------------------------------------------------------------
    # make database
    logdb = Database(log_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in logdb.tables:
        logdb.delete_table('MAIN')
    # add main table
    logdb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    return logdb


def create_object_database(params, pconst, databases) -> Database:
    """
    Setup for the calibration database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    reset_path = params['DATABASE_DIR']
    reset_file = params['OBJECT_DB_RESET']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.OBJECT_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    object_abspath = databases['object']
    # -------------------------------------------------------------------------
    # make database
    objectdb = Database(object_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in objectdb.tables:
        objectdb.delete_table('MAIN')
    # add main table
    objectdb.add_table('MAIN', columns, ctypes)
    # ---------------------------------------------------------------------
    # construct reset file
    reset_abspath = os.path.join(asset_dir, reset_path, reset_file)
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    objectdb.add_from_pandas(reset_entries, 'MAIN')
    # -------------------------------------------------------------------------
    return objectdb


def create_params_database(pconst, databases) -> Database:
    """
    Setup for the index database
    :param params:
    :param pconst:
    :return:
    """
    # get columns and ctypes from pconst
    columns, ctypes = pconst.PARAMS_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    params_abspath = databases['params']
    # -------------------------------------------------------------------------
    # make database
    paramsdb = Database(params_abspath)
    # -------------------------------------------------------------------------
    if 'MAIN' in paramsdb.tables:
        paramsdb.delete_table('MAIN')
    # add main table
    paramsdb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    return paramsdb


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
