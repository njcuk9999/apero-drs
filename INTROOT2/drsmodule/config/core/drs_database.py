#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-25 at 16:49

@author: cook
"""
from __future__ import division
from astropy.time import Time
import os
import shutil

from drsmodule import constants
from drsmodule import locale
from drsmodule.io import drs_lock
from . import drs_log

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
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry


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
    outpath = _get_outpath(params, dbname, outfile)
    # ------------------------------------------------------------------
    # construct outpath
    abs_outpath = os.path.join(outpath, infile)
    # ------------------------------------------------------------------
    # first copy file to database folder
    _copy_db_file(params, dbname, inpath, abs_outpath)

    # update database with key
    if dbname.lower() == 'telluric':
        update_calibdb(params, dbname, dbkey, outfile)
    elif dbname.lower() == 'calibration':
        update_telludb(params, dbname, dbkey, outfile)


# =============================================================================
# Define calibration database functions
# =============================================================================
def update_calibdb(params, dbname, dbkey, outfile):
    func_name = __NAME__ + '.update_calibdb()'
    # ----------------------------------------------------------------------
    # get the hdict
    hdict = _get_hdict(params, dbname, outfile)
    # ----------------------------------------------------------------------
    # get time from header
    header_time = _get_time(params, dbname, hdict)
    # ----------------------------------------------------------------------
    # get properties for database
    key = str(dbkey)
    nightname = str(params['NIGHTNAME'])
    filename = outfile.basename
    human_time = str(header_time.iso)
    unix_time = str(header_time.unix)
    # ----------------------------------------------------------------------
    # push into list
    largs = [key, nightname, filename, human_time, unix_time]
    # construct the line
    line = '\n{0} {1} {2} {3} {4}'.format(*largs)
    # ----------------------------------------------------------------------
    # write to file
    _write_line_to_database(params, key, dbname, outfile, line)


# =============================================================================
# Define telluric database functions
# =============================================================================
def update_telludb(params, dbname, dbkey, outfile):
    func_name = __NAME__ + '.update_calibdb()'
    # ----------------------------------------------------------------------
    # get the hdict
    hdict = _get_hdict(params, dbname, outfile)
    # ----------------------------------------------------------------------
    # get time from header
    header_time = _get_time(params, dbname, hdict)
    # ----------------------------------------------------------------------
    # get properties for database
    key = str(dbkey)
    nightname = str(params['NIGHTNAME'])
    filename = outfile.basename
    human_time = str(header_time.iso)
    unix_time = str(header_time.unix)
    # ----------------------------------------------------------------------
    # push into list
    largs = [key, nightname, filename, human_time, unix_time]
    # construct the line
    line = '\n{0} {1} {2} {3} {4}'.format(*largs)
    # ----------------------------------------------------------------------
    # write to file
    _write_line_to_database(params, key, dbname, outfile, line)


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
        WLOG(params, 'error', TextEntry('00-008-00007', args=eargs))
        dbkey = ''
    return dbkey


def _get_dbname(params, outfile):
    func_name = __NAME__ + '._get_dbname()'
    if hasattr(outfile, 'dbname'):
        dbname = outfile.dbname.capitalize()
    else:
        eargs = [outfile.name, func_name]
        WLOG(params, 'error', TextEntry('00-008-00005', args=eargs))
        dbname = None
    return dbname


def _get_hdict(params, dbname, outfile):
    func_name = __NAME__ + '._get_hdict()'
    # get hdict
    if hasattr(outfile, 'hdict'):
        hdict = outfile.hdict
    elif hasattr(outfile, 'header'):
        hdict = outfile.header
    else:
        eargs = [dbname, outfile.name, func_name]
        WLOG(params, 'error', TextEntry('00-001-00027', args=eargs))
        hdict = None
    return hdict


def _get_outpath(params, dbname, outfile):
    func_name = __NAME__ + '._get_outpath()'
    # test database name
    if dbname.lower() == 'telluric':
        outpath = params['DRS_TELLU_DB']
    elif dbname.lower() == 'calibration':
        outpath = params['DRS_CALIB_DB']
    else:
        eargs = [outfile.name, outfile.dbname, 'calibration, telluric',
                 func_name]
        WLOG(params, 'error', TextEntry('00-008-00006', args=eargs))
        outpath = ''
    return outpath


def _get_database_file(params, dbname, outfile):
    func_name = __NAME__ + '._get_database_file()'
    # test database name
    if dbname.lower() == 'telluric':
        outpath = params['DRS_TELLU_DB']
    elif dbname.lower() == 'calibration':
        outpath = params['DRS_CALIB_DB']
    else:
        eargs = [outfile.name, outfile.dbname, 'calibration, telluric',
                 func_name]
        WLOG(params, 'error', TextEntry('00-008-00006', args=eargs))
        outpath = ''
    return outpath


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
        WLOG(params, 'error', TextEntry('', args=eargs))
    except OSError as e:
        wargs = [dbname, outpath, type(e), e, func_name]
        WLOG(params, 'warning', TextEntry('10-001-00007', args=wargs))


def _get_time(params, dbname, hdict, kind=None):
    func_name = __NAME__ + '._get_time()'
    # ----------------------------------------------------------------------
    # get keywords from params
    timekey = drs_log.find_param(params, 'KW_ACQTIME', func_name)[0]
    timefmt = drs_log.find_param(params, 'KW_ACQTIME_FMT', func_name)
    timetype = drs_log.find_param(params, 'KW_ACQTIME_DTYPE', func_name)
    # ----------------------------------------------------------------------
    # get raw time
    if timekey in hdict:
        # get the raw time from the header
        raw_time = hdict[timekey]
    else:
        eargs = [dbname, timekey, func_name]
        WLOG(params, 'error', TextEntry('00-001-00028', args=eargs))
        raw_time = None
    # ----------------------------------------------------------------------
    # convert raw time to astropy time
    try:
        a_time = Time(timetype(raw_time), format=timefmt)
    except Exception as e:
        eargs = [dbname, raw_time, timefmt, timetype, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-001-00029', args=eargs))
        a_time = None
    # ----------------------------------------------------------------------
    # if kind is None return the astropy object
    if kind is None:
        return a_time
    elif kind == 'human':
        return str(a_time.iso)
    elif kind == 'unix':
        return float(a_time.unix)
    elif kind == 'mjd':
        return float(a_time.mjd)
    else:
        kinds = ['None', 'human', 'unix', 'mjd']
        eargs = [dbname, ', '.join(kinds), kind, func_name]
        WLOG(params, 'error', TextEntry('00-001-00030', args=eargs))


def _write_line_to_database(params, key, dbname, outfile, line):
    func_name = __NAME__ + '._write_line_to_database()'
    # get outpath
    outpath = _get_outpath(params, dbname, outfile)
    # get file name
    db_file = _get_database_file(params, dbname, outfile)
    # construct absolute path
    abspath = os.path.join(outpath, db_file)
    # lock the master file
    lock, lock_file = drs_lock.check_fits_lock_file(params, abspath)
    # try to open the master file
    try:
        f = open(abspath, 'a')
        f.writelines([line])
        f.close()
        # print progress
        wargs = [dbname, key]
        WLOG(params, 'info', TextEntry('40-006-00001', args=wargs))
    except Exception as e:
        # must close lock file
        drs_lock.close_fits_lock_file(params, lock, lock_file, abspath)
        # error message
        eargs = [dbname, key, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('01-001-00018', args=eargs))
    # must close lock file
    drs_lock.close_fits_lock_file(params, lock, lock_file, abspath)


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
