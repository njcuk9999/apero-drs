#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-25 at 16:49

@author: cook
"""
from __future__ import division
import numpy as np
from astropy.time import Time
from astropy.table import Table, vstack
import os
import shutil
from collections import OrderedDict

from apero.core import constants
from apero import locale
from apero.io import drs_lock
from apero.io import drs_fits
from apero.io import drs_table
from apero.core.core import drs_log


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.core.drs_database.py'
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
# Get function string
display_func = drs_log.display_func
# Get the text types
TextEntry = locale.drs_text.TextEntry
# alias pcheck
pcheck = drs_log.find_param


# =============================================================================
# Define database class
# =============================================================================
class Database():
    def __init__(self, params, dbname):
        # set constant values
        # TODO: move to params?
        # TODO:   must contain "key"
        self.calib_cols = ['key', 'nightname', 'filename', 'humantime',
                           'unixtime']
        self.tellu_cols = ['key', 'nightname', 'filename', 'humantime',
                           'unixtime', 'objname']
        self.key_col = 'key'
        self.time_col = 'unixtime'
        self.file_col = 'filename'
        # set value from construction
        self.params = params
        self.dbname = dbname
        # empty to fill later
        self.key_pos = None
        self.time_pos = None
        self.file_pos = None
        self.unique_keys = None
        self.rdata = None
        self.data = None
        # get values based on dbname
        self.dbfile = _get_database_file(self.params, self.dbname)
        self.dbshort = _get_dbshort(self.params, self.dbname)
        self.outpath = _get_outpath(self.params, self.dbname)
        self.abspath = os.path.join(self.outpath, self.dbfile)
        self.colnames = self.get_colnames()

    def get_colnames(self):
        """
        Get the column names using the database name (set in construction)
        :return:
        """
        func_name = __NAME__ + '.Database.get_colnames()'
        # set colnames based on databasename
        if self.dbname == 'calibration':
            colnames = self.calib_cols
        elif self.dbname == 'telluric':
            colnames = self.tellu_cols
        else:
            eargs = [self.dbname, 'calibration or telluric', func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00001', args=eargs))
            colnames = []
        # check required columns are present
        if self.key_col not in colnames:
            eargs = [self.key_col, self.dbname, colnames, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00002', args=eargs))
        if self.time_col not in colnames:
            eargs = [self.key_col, self.dbname, colnames, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00003', args=eargs))
        if self.file_col not in colnames:
            eargs = [self.key_col, self.dbname, colnames, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00004', args=eargs))
        # find positions of required columns
        self.key_pos = np.where(self.key_col == np.array(colnames))[0][0]
        self.time_pos = np.where(self.time_col == np.array(colnames))[0][0]
        self.file_pos = np.where(self.file_col == np.array(colnames))[0][0]
        # set colnames
        return colnames

    def check_read(self):
        if self.rdata is None:
            self.read()

    def read(self):
        """
        Read the database from file and store in astropy.table format
        :return:
        """
        func_name = __NAME__ + '.Database.read()'
        # lock the master file
        lock, lock_file = drs_lock.check_lock_file(self.params, self.abspath)
        # ---------------------------------------------------------------------
        # try to open the master file
        try:
            f = open(self.abspath, 'r')
            lines = list(f.readlines())
            f.close()
        except Exception as e:
            # must close lock file
            drs_lock.close_lock_file(self.params, lock, lock_file, self.abspath)
            # error message
            eargs = [self.dbname, type(e), e, self.abspath, func_name]
            WLOG(self.params, 'error', TextEntry('01-001-00019', args=eargs))
            lines = []
        # ---------------------------------------------------------------------
        # make dict storage to append to
        rstorage, storage = OrderedDict(), OrderedDict()
        for col in ['rkey', 'rtime', 'rfile']:
            rstorage[col] = []
        for col in self.colnames:
            storage[col] = []
        # ---------------------------------------------------------------------
        # clean up database and add to storage
        for l_it, line in enumerate(lines):
            # ignore blank lines or lines starting with '#'
            if len(line) == 0:
                continue
            if line == '\n':
                continue
            if line.strip()[0] == '#':
                continue
            # split line to reveal values
            values = line.split()
            # make sure values has correct length and cause error if not
            if len(values) != len(self.colnames):
                eargs = [self.dbname, l_it, line,
                         ', '.join(self.colnames), self.abspath, func_name]
                emsg = TextEntry('00-002-00005', args=eargs)
                WLOG(self.params, 'error', emsg)
            # append rkey and rfile to rstorage
            rstorage['rkey'].append(values[self.key_pos])
            rstorage['rfile'].append(values[self.time_pos])
            # convert time to astropy time and append to rstorage
            try:
                rtime = Time(float(values[self.time_pos]), format='unix')
            except Exception as e:
                # must close lock file
                drs_lock.close_lock_file(self.params, lock, lock_file,
                                         self.abspath)
                # log error
                eargs = [self.dbname, l_it, line, type(e), str(e),
                         self.abspath, func_name]
                emsg = TextEntry('00-002-00007', args=eargs)
                WLOG(self.params, 'error', emsg)
                rtime = None
            rstorage['rtime'].append(rtime)
            # append all values to storage
            for col_it, col in enumerate(self.colnames):
                storage[col].append(values[col_it])
        # make full tables
        self.rdata, self.data = Table(), Table()
        # read dict into tables
        for col in storage.keys():
            self.data[col] = np.array(storage[col])
        # create required table in good format
        for col in rstorage.keys():
            self.rdata[col] = np.array(rstorage[col])
        # finally get a list of unique keys
        self.unique_keys = np.unique(self.rdata['rkey'])
        # must close lock file
        drs_lock.close_lock_file(self.params, lock, lock_file, self.abspath)

    def write(self):
        pass

    def get_entry(self, entryname, mode=None, usetime=None, n_entries=1,
                  time_fmt='iso', required=True):
        """
        Get a database entry for key='entryname'

        if mode = 'older' then only uses database entries older than 'usetime'

        selects n_entries that are closest in time to 'usetime'

        time format must be valid astropy.time.Time format i.e.
        'jd', 'mjd', 'decimalyear', 'unix', 'cxcsec', 'gps', 'plot_date',
        'datetime', 'iso', 'isot', 'yday', 'datetime64', 'fits', 'byear',
        'jyear', 'byear_str', 'jyear_str'
        default is 'iso'

        :param entryname:
        :param mode:
        :param usetime:
        :param n_entries:
        :param time_fmt:
        :param required:
        :return:
        """
        func_name = __NAME__ + '.Database.get_entry()'
        # check that we have data
        self.check_read()
        # convert usetime to astropy.time
        if isinstance(usetime, Time):
            pass
        elif usetime is not None:
            usetime = Time(usetime, format=time_fmt)
        # get unique keys in database
        ukeys = np.unique(self.rdata['rkey'])
        # mask by key
        mask1 = self.rdata['rkey'] == entryname
        # if we have no rows we must report it
        if (np.sum(mask1) == 0) and not required:
            return Table()
        elif np.sum(mask1) == 0:
            eargs = [self.dbname, entryname, ', '.join(ukeys), self.abspath,
                     func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00006', args=eargs))
            entries, r_entries = None, None
        else:
            entries = self.data[mask1]
            r_entries = self.rdata[mask1]
        # if mode is None then we just want all data from this entry
        if mode is None:
            # sort by time
            timesort = np.argsort(r_entries['rtime'])
            # return the first n_entries (after timesorting)
            if isinstance(n_entries, str):
                return entries[timesort]
            elif isinstance(n_entries, int):
                return entries[timesort][:n_entries]
        # if mode is not None and time_used is None we have a problem
        elif (mode is not None) and (usetime is None):
            eargs = [mode, self.dbname, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00008', args=eargs))
            mask2 = None
        # if mode is not None we need to deal with finding the correct entry
        elif mode == 'older':
            # only keep those older than usetime
            mask2 = np.array(r_entries['rtime']) < usetime
            # if we have no rows we must report it
            if (np.sum(mask2) == 0) and not required:
                return Table()
            if np.sum(mask2) == 0:
                eargs = [self.dbname, entryname, usetime.iso, self.abspath,
                         func_name]
                WLOG(self.params, 'error',
                     TextEntry('00-002-00006', args=eargs))
                entries, r_entries = None, None
            else:
                entries = self.data[mask1]
                r_entries = self.rdata[mask1]
        else:
            mask2 = np.ones_like(r_entries['rtime'], dtype=bool)
        # if we have reached here we have a mask and must find the closest
        #    'n_entries'
        entries = entries[mask2]
        r_entries = r_entries[mask2]
        # sort remaining by time
        timesort = np.argsort(abs(Time(r_entries['rtime']) - usetime))
        # return the first n_entries (after timesorting)
        if isinstance(n_entries, str):
            return entries[timesort]
        elif isinstance(n_entries, int):
            return entries[timesort][:n_entries]
        else:
            eargs = [n_entries, type(n_entries), func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00013', args=eargs))


# =============================================================================
# Define functions
# =============================================================================
def add_file(params, outfile, night=None, copy_files=True, log=True):
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
    dbkey = get_dbkey(params, outfile)
    # ------------------------------------------------------------------
    # deal with database input being set to False
    if 'DATABASE' in params['INPUTS']:
        if not params['INPUTS']['DATABASE']:
            # Log that we are not adding file due to user input
            wargs = [dbkey, outfile.filename]
            WLOG(params, 'info', TextEntry('40-001-00024', args=wargs))
            # return here
            return
    # ------------------------------------------------------------------
    # test database name
    outpath = _get_outpath(params, dbname, outfile)
    # ------------------------------------------------------------------
    # construct outpath
    abs_outpath = os.path.join(outpath, infile)
    # ------------------------------------------------------------------
    # first copy file to database folder
    if copy_files:
        _copy_db_file(params, dbname, inpath, abs_outpath)
    # ------------------------------------------------------------------
    # update database with key
    if dbname.lower() == 'telluric':
        # get object name
        if hasattr(outfile, 'get_key'):
            objname = outfile.get_key('KW_OBJNAME', dtype=str)
        else:
            objname = 'None'
        # update telluric database
        update_telludb(params, dbname, dbkey, outfile, night, objname, log)
    elif dbname.lower() == 'calibration':
        # update calibration database
        update_calibdb(params, dbname, dbkey, outfile, night, log)


def copy_calibrations(params, header, **kwargs):
    func_name = __NAME__ + '.copy_calibrations()'
    # get parameters from params/kwargs
    mode = pcheck(params, 'CALIB_DB_MATCH', 'mode', kwargs, func_name)
    # set the dbname
    dbname = 'calibration'
    # get the output filename directory
    outpath = os.path.join(params['OUTPATH'], params['NIGHTNAME'])
    # ----------------------------------------------------------------------
    # get calibration database
    cdb = get_full_database(params, dbname)
    # get shortname
    dbshort = cdb.dbshort
    # ----------------------------------------------------------------------
    # get each unique key get the entry
    entry_tables = []
    # loop around unique keys and add to list
    gkwargs = dict(database=cdb, header=header, n_ent=1, required=False,
                   mode=mode)
    for key in cdb.unique_keys:
        # get closest key
        entry_table = get_key_from_db(params, key, **gkwargs)
        # append to list of tables if we have rows
        if len(entry_table) > 0:
            entry_tables.append(entry_table)
    # ----------------------------------------------------------------------
    # stack the tables vertically
    ctable = vstack(entry_tables)
    # get the filenames
    filecol = cdb.file_col
    infilenames = ctable[filecol]
    # ----------------------------------------------------------------------
    # loop around file names and copy
    for infilename in infilenames:
        # get absolute paths
        inpath = _get_outpath(params, dbname)
        inabspath = os.path.join(inpath, infilename)
        outabspath = os.path.join(outpath, infilename)
        # debug message
        dargs = [dbname, inabspath, outabspath]
        WLOG(params, 'debug',TextEntry('90-002-00001', args=dargs))
        # if file exists do not copy it
        if os.path.exists(outabspath):
            # log copying skipped
            wargs = [dbshort, infilename]
            WLOG(params, '', TextEntry('40-006-00002', args=wargs))
        # else copy it
        else:
            # log copying
            wargs = [dbshort, infilename, outpath]
            WLOG(params, '', TextEntry('40-006-00003', args=wargs))
            # copy the database file
            _copy_db_file(params, dbname, inabspath, outabspath)


def get_header_time(params, database, header):
    # set function name
    func_name = display_func(params, 'get_header_time', __NAME__)
    # get time from header
    return _get_time(params, database.dbname, header=header)


# =============================================================================
# Define database get functions
# =============================================================================
def get_key_from_db(params, key, database, header, n_ent=1, required=True,
                    mode=None, **kwargs):
    func_name = __NAME__ + '.get_key_from_db()'
    # ----------------------------------------------------------------------
    # deal with no mode set (assume from calibDB)
    if mode is None:
        mode = pcheck(params, 'CALIB_DB_MATCH', 'mode', kwargs, func_name)
    # debug print mode using
    dargs = [mode, func_name]
    WLOG(params, 'debug', TextEntry('90-002-00002', args=dargs))
    # ----------------------------------------------------------------------
    # get time from header
    header_time = _get_time(params, database.dbname, header=header)
    # get the correct entry from database
    gkwargs = dict(mode=mode, usetime=header_time, n_entries=n_ent,
                   required=required)
    # return the database entries (in astropy.table format)
    return database.get_entry(key, **gkwargs)


def get_full_database(params, dbname):
    func_name = __NAME__ + '.get_full_database()'

    dbshort = _get_dbshort(params, dbname)
    # check for calibDB in params
    if dbshort in params:
        return params[dbshort]
    # get all lines from calibration database
    else:
        database = Database(params, dbname)
        database.read()
        return database


def get_db_abspath(params, filename=None, where='guess'):
    func_name = __NAME__ + '.get_db_abspath()'
    # ------------------------------------------------------------------
    # get the calibration path and telluric path
    cal_path = os.path.join(params['DRS_CALIB_DB'], filename)
    tel_path = os.path.join(params['DRS_TELLU_DB'], filename)
    # ------------------------------------------------------------------
    # deal with where file is located
    if where == 'calibration':
        abspath = cal_path
    elif where == 'telluric':
        abspath = tel_path
    elif where == 'guess':
        # check full path
        if os.path.exists(filename):
            abspath = str(filename)
        # check cal path
        elif os.path.exists(cal_path):
            abspath = cal_path
        # check tellu path
        elif os.path.exists(tel_path):
            abspath = tel_path
        else:
            # raise error that defined filename does not exist
            eargs = ['\n\t\t'.join([filename, cal_path, tel_path]), func_name]
            WLOG(params, 'error', TextEntry('00-001-00036', args=eargs))
            abspath = None
    else:
        # raise error that 'where' was not valid
        eargs = [' or '.join(['calibration', 'telluric', 'guess']), func_name]
        WLOG(params, 'error', TextEntry('00-001-00037', args=eargs))
        abspath = None
    # return the absolute path
    return abspath


def get_db_file(params, abspath, ext=0, fmt='fits', kind='image',
                get_image=True, get_header=False):
    func_name = __NAME__ + '.get_db_file'
    # ------------------------------------------------------------------
    # deal with npy files
    if abspath.endswith('.npy'):
        image = np.load(abspath)
        return image, None
    # ------------------------------------------------------------------
    # get db fits file
    if (not get_image) or (not abspath.endswith('.fits')):
        image = None
    elif kind == 'image':
        image = drs_fits.read(params, abspath, ext=ext)
    elif kind == 'table':
        image = drs_table.read_table(params, abspath, fmt=fmt)
    else:
        # raise error is kind is incorrect
        eargs = [' or '.join(['image', 'table']), func_name]
        WLOG(params, 'error', TextEntry('00-001-00038', args=eargs))
        image = None
    # ------------------------------------------------------------------
    # get header if required (and a fits file)
    if get_header and abspath.endswith('.fits'):
        header = drs_fits.read_header(params, abspath, ext=ext)
    else:
        header = None
    # return the image and header
    return image, header


# =============================================================================
# Define calibration database functions
# =============================================================================
# TODO: Redo to use Database class
def update_calibdb(params, dbname, dbkey, outfile, night=None, log=True):
    func_name = __NAME__ + '.update_calibdb()'
    func_name = display_func
    # deal with no night name
    if night is None:
        night = drs_log.find_param(params, 'NIGHTNAME', func=func_name)
    if night == '' or night is None:
        night = 'None'
    # ----------------------------------------------------------------------
    # get the hdict
    hdict, header = _get_hdict(params, dbname, outfile)
    # ----------------------------------------------------------------------
    # get time from header
    header_time = _get_time(params, dbname, header=header, hdict=hdict)
    # ----------------------------------------------------------------------
    # get properties for database
    key = str(dbkey).strip()
    nightname = str(night).strip()
    filename = str(outfile.basename).strip()
    human_time = str(header_time.iso).replace(' ', '_').strip()
    unix_time = str(header_time.unix).strip()
    # ----------------------------------------------------------------------
    # push into list
    largs = [key, nightname, filename, human_time, unix_time]
    # construct the line
    line = '\n{0} {1} {2} {3} {4}'.format(*largs)
    # ----------------------------------------------------------------------
    # write to file
    _write_line_to_database(params, key, dbname, outfile, line, log)


# =============================================================================
# Define telluric database functions
# =============================================================================
def update_telludb(params, dbname, dbkey, outfile, night=None, objname=None,
                   log=True):
    func_name = __NAME__ + '.update_calibdb()'
    # deal with no night name
    if night is None:
        night = drs_log.find_param(params, 'NIGHTNAME', func=func_name)
    if night == '' or night is None:
        night = 'None'
    # deal with no object name
    if objname is None:
        objname = 'Unknown'
    # ----------------------------------------------------------------------
    # get the hdict
    hdict, header = _get_hdict(params, dbname, outfile)
    # ----------------------------------------------------------------------
    # get time from header
    header_time = _get_time(params, dbname, header=header, hdict=hdict)
    # ----------------------------------------------------------------------
    # get properties for database
    key = str(dbkey).strip()
    nightname = str(night).strip()
    filename = str(outfile.basename).strip()
    human_time = str(header_time.iso).replace(' ', '_').strip()
    unix_time = str(header_time.unix).strip()
    # ----------------------------------------------------------------------
    # push into list
    largs = [key, nightname, filename, human_time, unix_time, objname]
    # construct the line
    line = '\n{0} {1} {2} {3} {4} {5}'.format(*largs)
    # ----------------------------------------------------------------------
    # write to file
    _write_line_to_database(params, key, dbname, outfile, line, log)


# =============================================================================
# Define worker functions
# =============================================================================
def get_dbkey(params, outfile):
    # set function name
    func_name = display_func(params, 'get_dbkey', __NAME__)
    # get database key (if it exists)
    if hasattr(outfile, 'dbkey'):
        dbkey = outfile.get_dbkey()
    else:
        eargs = [outfile.name, func_name]
        WLOG(params, 'error', TextEntry('00-008-00012', args=eargs))
        dbkey = ''
    # return dbkey
    return dbkey


def _get_dbname(params, outfile):
    # set function name
    func_name = display_func(params, '_get_dbname', __NAME__)
    # get database names
    dbnames = ['telluric', 'calibration']
    # deal with each database name
    if hasattr(outfile, 'dbname'):
        dbname = outfile.dbname.capitalize()
    else:
        eargs = [outfile.name, ', '.join(dbnames), func_name]
        WLOG(params, 'error', TextEntry('00-002-00012', args=eargs))
        dbname = None
    return dbname


def _get_dbshort(params, dbname):
    # set function name
    func_name = display_func(params, '_get_dbshort', __NAME__)
    # get database names
    dbnames = ['telluric', 'calibration']
    # deal with each database name
    if dbname == 'calibration':
        dbshort = 'calibdb'
    elif dbname == 'telluric':
        dbshort = 'telludb'
    else:
        eargs = [' or '.join(dbnames), func_name]
        WLOG(params, 'error', TextEntry('00-002-00001', args=eargs))
        dbshort = None
    return dbshort


def _get_hdict(params, dbname, outfile):
    # set function name
    func_name = display_func(params, '_get_hdict', __NAME__)
    # get hdict
    if hasattr(outfile, 'hdict') and len(list(outfile.hdict.keys())) != 0:
        hdict = outfile.hdict
        header = None
    elif hasattr(outfile, 'header') and len(list(outfile.header.keys())) != 0:
        hdict = None
        header = outfile.header
    else:
        eargs = [dbname, outfile.name, func_name]
        WLOG(params, 'error', TextEntry('00-001-00027', args=eargs))
        hdict, header = None, None
    return hdict, header


def _get_outpath(params, dbname, outfile=None):
    # set function name
    func_name = display_func(params, '_get_outpath', __NAME__)
    # test database name
    if dbname.lower() == 'telluric':
        outpath = params['DRS_TELLU_DB']
    elif dbname.lower() == 'calibration':
        outpath = params['DRS_CALIB_DB']
    elif outfile is None:
        eargs = ['calibration, telluric', func_name]
        WLOG(params, 'error', TextEntry('00-002-00001', args=eargs))
        outpath = ''
    else:
        eargs = [outfile.name, outfile.dbname, 'calibration, telluric',
                 func_name]
        WLOG(params, 'error', TextEntry('00-002-00011', args=eargs))
        outpath = ''
    return outpath


def _get_database_file(params, dbname, outfile=None):
    # set function name
    func_name = display_func(params, '_get_database_file', __NAME__)
    # test database name
    if dbname.lower() == 'telluric':
        outpath = params['TELLU_DB_NAME']
    elif dbname.lower() == 'calibration':
        outpath = params['CALIB_DB_NAME']
    elif outfile is None:
        eargs = ['calibration, telluric', func_name]
        WLOG(params, 'error', TextEntry('00-002-00001', args=eargs))
        outpath = ''
    else:
        eargs = [outfile.name, outfile.dbname, 'calibration, telluric',
                 func_name]
        WLOG(params, 'error', TextEntry('00-002-00011', args=eargs))
        outpath = ''
    return outpath


def _copy_db_file(params, dbname, inpath, outpath):
    # set function name
    func_name = display_func(params, '_copy_file', __NAME__)
    # remove file if already present
    if inpath == outpath:
        return 0
    # lock the input and output files
    lock1, lock_file1 = drs_lock.check_lock_file(params, inpath)
    lock2, lock_file2 = drs_lock.check_lock_file(params, outpath)
    # noinspection PyExceptClausesOrder
    try:
        shutil.copyfile(inpath, outpath)
        os.chmod(outpath, 0o0644)
    except IOError as e:
        # close input and output lock files
        drs_lock.close_lock_file(params, lock1, lock_file1, inpath)
        drs_lock.close_lock_file(params, lock2, lock_file2, outpath)
        # log and raise error
        eargs = [dbname, inpath, outpath, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-002-00014', args=eargs))
    except OSError as e:
        wargs = [dbname, outpath, type(e), e, func_name]
        WLOG(params, 'warning', TextEntry('10-001-00007', args=wargs))
    # close input and output lock files
    drs_lock.close_lock_file(params, lock1, lock_file1, inpath)
    drs_lock.close_lock_file(params, lock2, lock_file2, outpath)


def _get_time(params, dbname, header=None, hdict=None, kind=None):
    # set function name
    func_name = display_func(params, '_get_time', __NAME__)
    # ----------------------------------------------------------------------
    # get raw time from hdict / header
    if hdict is not None:
        t, m = drs_fits.get_mid_obs_time(params, hdict, out_fmt=kind)
        return t
    elif header is not None:
        t, m = drs_fits.get_mid_obs_time(params, header, out_fmt=kind)
        return t
    else:
        eargs = [dbname, func_name]
        WLOG(params, 'error', TextEntry('00-001-00039', args=eargs))


def _read_lines_from_database(params, dbname):
    # set function name
    func_name = display_func(params, '_read_lines_from_database', __NAME__)
    # get outpath
    outpath = _get_outpath(params, dbname)
    # get file name
    db_file = _get_database_file(params, dbname)
    # construct absolute path
    abspath = os.path.join(outpath, db_file)
    # lock the master file
    lock, lock_file = drs_lock.check_lock_file(params, abspath)
    # ----------------------------------------------------------------------
    # try to open the master file
    try:
        f = open(abspath, 'a')
        lines = list(f.readlines())
        f.close()
    except Exception as e:
        # must close lock file
        drs_lock.close_lock_file(params, lock, lock_file, abspath)
        # error message
        eargs = [dbname, type(e), e, abspath, func_name]
        WLOG(params, 'error', TextEntry('01-001-00019', args=eargs))
        lines = []
    # ----------------------------------------------------------------------
    # database storage
    database = OrderedDict()
    # clean up database
    for l_it, line in enumerate(lines):
        # ignore blank lines or lines starting with '#'
        if len(line) == 0:
            continue
        if line == '\n':
            continue
        if line.strip()[0] == '#':
            continue
        # get elements from database
        try:
            # need to get key. Must be first entry in line (separated by spaces)
            key = line.split()[0]
            # check if key already in database
            if key in database:
                # noinspection PyTypeChecker
                database[key].append([l_it] + line.split()[1:])
            else:
                # noinspection PyTypeChecker
                database[key] = [[l_it] + line.split()[1:]]
        except ValueError:
            # must close lock file
            drs_lock.close_lock_file(params, lock, lock_file, abspath)
            # error message
            eargs = [dbname, abspath, func_name]
            WLOG(params, 'error', TextEntry('09-002-00002', args=eargs))
    # ----------------------------------------------------------------------
    # Need to check if lists are empty after loop
    if len(database) == 0:
        # must close lock file
        drs_lock.close_lock_file(params, lock, lock_file, abspath)
        # error message
        eargs = [dbname, abspath, func_name]
        WLOG(params, 'error', TextEntry('09-002-00003', args=eargs))
        # ----------------------------------------------------------------------
    # must close lock file
    drs_lock.close_lock_file(params, lock, lock_file, abspath)
    # return database
    return database


def _write_line_to_database(params, key, dbname, outfile, line, log=True):
    # set function name
    func_name = display_func(params, '_write_line_to_database', __NAME__)
    # get outpath
    outpath = _get_outpath(params, dbname, outfile)
    # get file name
    db_file = _get_database_file(params, dbname, outfile)
    # construct absolute path
    abspath = os.path.join(outpath, db_file)
    # lock the master file
    lock, lock_file = drs_lock.check_lock_file(params, abspath)
    # ----------------------------------------------------------------------
    # try to open the master file
    try:
        f = open(abspath, 'a')
        f.writelines([line])
        f.close()
        # print progress
        wargs = [dbname, key]
        if log:
            WLOG(params, 'info', TextEntry('40-006-00001', args=wargs))
    except Exception as e:
        # must close lock file
        drs_lock.close_lock_file(params, lock, lock_file, abspath)
        # error message
        eargs = [dbname, key, type(e), e, abspath, func_name]
        WLOG(params, 'error', TextEntry('01-001-00018', args=eargs))
    # ----------------------------------------------------------------------
    # must close lock file
    drs_lock.close_lock_file(params, lock, lock_file, abspath)


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
