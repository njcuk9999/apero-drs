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
CALIBDB_TEXTFILE = None
TELLUDB_TEXTFILE = None
INDEX_TEXTFILE = None
LOG_TEXTFILE = None
OBJECT_TEXTFILE = None
PARAMS_TEXTFILE = None

# =============================================================================
# Define functions
# =============================================================================
def create_databases(params, skip=None):

    # deal with skip
    if skip is None:
        skip = []

    # TODO: remove - for tests only
    params.set('CALIB_DB_NAME', value='calib.db')
    params.set('TELLU_DB_NAME', value='tellu.db')

    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # -------------------------------------------------------------------------
    # create calibration database
    if 'calib' not in skip:
        calibdb = create_calibration_database(params, pconst)
    # -------------------------------------------------------------------------
    # create telluric database
    if 'tellu' not in skip:
        telludb = create_telluric_database(params, pconst)
    # -------------------------------------------------------------------------
    # create index database
    if 'index' not in skip:
        indexdb = create_index_database(params, pconst)
    # -------------------------------------------------------------------------
    # create log database
    if 'log' not in skip:
        logdb = create_log_database(params, pconst)
    # -------------------------------------------------------------------------
    # create object database
    if 'object' not in skip:
        objectdb = create_object_database(params, pconst)
    # -------------------------------------------------------------------------
    # create params database
    if 'params' not in skip:
        paramsdb = create_params_database(params, pconst)
    # -------------------------------------------------------------------------


def create_calibration_database(params, pconst) -> drs_database.Database:
    """
    Setup for the calibration database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params
    calib_dir = params['DRS_CALIB_DB']
    calib_file = params['CALIB_DB_NAME']
    asset_dir = params['DRS_DATA_ASSETS']
    reset_path = params['DATABASE_DIR']
    reset_file = params['CALIB_DB_RESET']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.CALIBRATION_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    calib_abspath = os.path.join(calib_dir, calib_file)
    # -------------------------------------------------------------------------
    # make database
    calibdb = drs_database.Database(calib_abspath)
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


def create_telluric_database(params, pconst) -> drs_database.Database:
    """
    Setup for the telluric database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params
    tellu_dir = params['DRS_TELLU_DB']
    tellu_file = params['TELLU_DB_NAME']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.TELLURIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    tellu_abspath = os.path.join(tellu_dir, tellu_file)
    # -------------------------------------------------------------------------
    # make database
    telludb = drs_database.Database(tellu_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in telludb.tables:
        telludb.delete_table('MAIN')
    # add main table
    telludb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    return telludb


def create_index_database(params, pconst) -> drs_database.Database:
    """
    Setup for the index database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    index_dir = params['DATABASE_DIR']
    index_file = params['INDEX_DB_NAME']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.INDEX_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    index_abspath = os.path.join(asset_dir, index_dir, index_file)
    # -------------------------------------------------------------------------
    # make database
    indexdb = drs_database.Database(index_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in indexdb.tables:
        indexdb.delete_table('MAIN')
    # add main table
    indexdb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    return indexdb


def create_log_database(params, pconst) -> drs_database.Database:
    """
    Setup for the index database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    log_dir = params['DATABASE_DIR']
    log_file = params['LOG_DB_NAME']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.TELLURIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    log_abspath = os.path.join(asset_dir, log_dir, log_file)
    # -------------------------------------------------------------------------
    # make database
    logdb = drs_database.Database(log_abspath)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if 'MAIN' in logdb.tables:
        logdb.delete_table('MAIN')
    # add main table
    logdb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    return logdb


def create_object_database(params, pconst) -> drs_database.Database:
    """
    Setup for the calibration database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    object_dir = params['DATABASE_DIR']
    object_file = params['OBJECT_DB_NAME']
    reset_path = params['DATABASE_DIR']
    reset_file = params['OBJECT_DB_RESET']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.OBJECT_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    object_abspath = os.path.join(asset_dir, object_dir, object_file)
    # -------------------------------------------------------------------------
    # make database
    objectdb = drs_database.Database(object_abspath)
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


def create_params_database(params, pconst) -> drs_database.Database:
    """
    Setup for the index database
    :param params:
    :param pconst:
    :return:
    """
    # get parameters from params
    asset_dir = params['DRS_DATA_ASSETS']
    params_dir = params['DATABASE_DIR']
    params_file = params['LOG_DB_NAME']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.PARAMS_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    params_abspath = os.path.join(asset_dir, params_dir, params_file)
    # -------------------------------------------------------------------------
    # make database
    paramsdb = drs_database.Database(params_abspath)
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
