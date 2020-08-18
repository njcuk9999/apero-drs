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
def create_databases(params):
    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # -------------------------------------------------------------------------
    # create calibration database
    create_calibration_database(params, pconst)


def create_calibration_database(params, pconst):

    # get parameters from params
    calib_dir = params['DRS_CALIB_DB']
    calib_file = params['CALIB_DB_NAME']
    reset_path = params['DATABASE_DIR']
    reset_file = params['RESET_PATH']
    # get columns and ctypes from pconst
    columns, ctypes = pconst.CALIBRATION_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    calib_abspath = os.path.join(calib_dir, calib_file)
    # -------------------------------------------------------------------------
    # make database
    calibdb = drs_database.Database(calib_abspath)
    # -------------------------------------------------------------------------
    # add main table
    if 'MAIN' not in calibdb.tables:
        calibdb.add_table('MAIN', columns, ctypes)
    # -------------------------------------------------------------------------
    # construct reset file
    reset_abspath = os.path.join(reset_path, reset_file)
    # get rows from reset file
    reset_entries = pd.read_csv(reset_abspath, skipinitialspace=True)
    # add rows from reset text file
    calibdb.add_from_pandas(reset_entries, 'MAIN')




# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
