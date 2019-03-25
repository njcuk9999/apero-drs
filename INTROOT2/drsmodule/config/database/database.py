#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-25 at 16:49

@author: cook
"""
from __future__ import division
import traceback
import numpy as np
import os
import shutil

from drsmodule import constants
from drsmodule import config
from drsmodule import locale
from drsmodule.science import preprocessing
from drsmodule.io import drs_image
from drsmodule.config.instruments.spirou import file_definitions
from . import calibdb
from . import telludb

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'database.database.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = config.wlog
# Get the text types
ErrorEntry = locale.drs_text.ErrorEntry


# =============================================================================
# Define functions
# =============================================================================
def add_file(params, outfile):
    func_name = __NAME__ + '.add_file()'
    # ------------------------------------------------------------------
    # get properties from outfile
    inpath = outfile.filename
    infile = outfile.basename
    # ------------------------------------------------------------------
    # get database name (if it exists)
    dbname = _get_dbname(params, outfile)
    # ------------------------------------------------------------------
    # get database key (if it exists)
    dbkey = _get_dbkey(params, outfile)
    # ------------------------------------------------------------------
    # test database name
    if dbname.lower() == 'telluric':
        outpath = params['DRS_TELLU_DB']
    elif dbname.lower() == 'calibration':
        outpath = params['DRS_CALIB_DB']
    else:
        eargs = [outfile.name, outfile.dbname, 'calibration, telluric',
                 func_name]
        WLOG(params, 'error', ErrorEntry('00-008-00006', args=eargs))
        outpath = ''
    # ------------------------------------------------------------------
    # construct outpath
    abs_outpath = os.path.join(outpath, infile)
    # ------------------------------------------------------------------
    # first copy file to database folder
    _copy_db_file(params, dbname, inpath, abs_outpath)

    # update database with key
    if dbname.lower() == 'telluric':
        # TODO: Add update_db function to calibdb
        calibdb.update_db(dbname, dbkey, outfile)
    elif dbname.lower() == 'calibration':
        # TODO: Add update_db function to telludb
        telludb.update_db(dbname, dbkey, outfile)


# =============================================================================
# Define worker functions
# =============================================================================
def _get_dbkey(params, outfile):
    func_name = __NAME__ + '._get_dbkey()'
    # get database key (if it exists)
    if hasattr(outfile, 'dbkey'):
        dbkey = outfile.key.upper()
    else:
        eargs = [outfile.name, func_name]
        WLOG(params, 'error', ErrorEntry('00-008-00007', args=eargs))
        dbkey = ''
    return dbkey


def _get_dbname(params, outfile):
    func_name = __NAME__ + '._get_dbname()'
    if hasattr(outfile, 'dbname'):
        dbname = outfile.dbname.capitalize()
    else:
        eargs = [outfile.name, func_name]
        WLOG(params, 'error', ErrorEntry('00-008-00005', args=eargs))
        dbname = None
    return dbname


def _copy_db_file(params, dbname, inpath, outpath):
    func_name = __NAME__ + '._copy_file()'
    # noinspection PyExceptClausesOrder
    try:
        shutil.copyfile(inpath, outpath)
        os.chmod(outpath, 0o0644)
    except IOError as e:
        emsg1 = 'I/O problem on {0}'.format(outpath)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(params, 'error', [emsg1, emsg2])

        eargs = [dbname, inpath, outpath, type(e), e, func_name]
        WLOG(params, 'error', ErrorEntry('', args=eargs))
    except OSError as e:
        wargs = [dbname, outpath, type(e), e, func_name]
        WLOG(params, 'warning', ErrorEntry('10-001-00007', args=wargs))





# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
