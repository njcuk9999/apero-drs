#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-18 15:15

@author: cook
"""
import numpy as np
from pathlib import Path
from typing import Union
import shutil

from apero.base import base
from apero.base import drs_db
from apero.base import drs_exceptions
from apero.base import drs_text
from apero import lang
from apero.core import drs_log
from apero.core import constants
from apero.io import drs_fits


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.core.drs_database2.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get astropy Time from base
Time = base.Time
# get ParamDict
ParamDict = constants.ParamDict
# get execption
DrsCodedException = drs_exceptions.DrsCodedException
# get display func
display_func = drs_log.display_func
# get WLOG
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry


# =============================================================================
# Define classes
# =============================================================================
class DatabaseManager():
    """
    Apero Database Manager class (basically abstract)
    """
    def __init__(self, params: ParamDict, check: bool = False):
        """
        Construct the Database Manager

        :param params: ParamDict containing constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)
        """
        # save class name
        self.classname = 'DatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # save params for use throughout
        self.params = params
        # set name
        self.name = 'DatabaseManager'
        # set path
        self.path = None
        # set database
        self.database = None

    def set_path(self, dirname: Union[str, None] = None,
                 filename: Union[str, None] = None,
                 check: bool = True):
        """
        Set the path for the database

        :param dirname: str, either a valid Path or parameter in params
        :param filename: str, the filename or parameter in params
        :param check: bool, if True the filename has to exist
        :return:
        """
        # set function
        func_name = display_func(self.params, 'set_path', __NAME__,
                                 self.classname)
        # ---------------------------------------------------------------------
        # deal with directory
        # ---------------------------------------------------------------------
        # deal with no directory name
        if dirname is None:
            asset_dir = str(self.params['DRS_DATA_ASSETS'])
            database_dir = str(self.params['DATABASE_DIR'])
            dirname = Path(asset_dir).joinpath(database_dir)
        # deal with dir name being a parameter key (multiple depths allowed)
        while dirname in self.params:
            dirname = self.params[dirname]
        # deal with dirname still being a parameter
        try:
            dirname = Path(dirname)
        except Exception as e:
            # log error: Directory {0} invalid for database: {1}
            eargs = [dirname, self.name, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00016', args=eargs))
            return
        if not dirname.exists():
            # log error: Directory {0} does not exist (database = {1})
            eargs = [dirname, self.name, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00017', args=eargs))
            return
        # ---------------------------------------------------------------------
        # add filename
        # ---------------------------------------------------------------------
        # deal with no filename set
        if filename is None:
            filename = self.name + '.db'
        # deal with filename being a parameter key (multiple depths allowed)
        while filename in self.params:
            filename = self.params[filename]
        # add to dirname
        abspath = dirname.joinpath(filename)
        if not abspath.exists() and check:
            # log error: Directory {0} does not exist (database = {1})
            eargs = [abspath, self.name, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00018', args=eargs))
            return
        # set path
        self.path = abspath

    def load_db(self):
        """
        Load the database class and connect to SQL database
        :return:
        """
        # if we already have database do nothing
        if self.database is not None:
            return
        # load database only if path is set
        if self.path is not None:
            # log that we are loading database
            margs = [self.name, self.path]
            WLOG(self.params, '', TextEntry('40-006-00005', args=margs))
            # load database
            self.database = drs_db.Database(self.path)

    def __str__(self):
        return '{0}[{1}]'.format(self.classname, self.path)

    def __repr__(self):
        return self.__str__()


# =============================================================================
# Define specific file databases
# =============================================================================
class CalibrationDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        # save class name
        self.classname = 'CalibrationDatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # construct super class
        DatabaseManager.__init__(self, params)
        # set name
        self.name = 'calibration'
        # set path
        self.set_path('CALIB_DBFILE_PATH', 'CALIB_DB_NAME', check=check)
        # set database directory
        self.filedir = Path(str(self.params['DRS_CALIB_DB']))

    def add_calib_file(self, drsfile, verbose: bool = True,
                       copy_files=True):
        """
        Add DrsFile to the calibration database

        :param drsfile: DrsFile, the DrsFile to add
        :params verbose: bool, if True logs progress
        :param copy_files: bool, if True copies file to self.filedir
        :return:
        """
        # set function
        _ = display_func(self.params, 'add_calib_file', __NAME__,
                         self.classname)
        # deal with no database
        if self.database is None:
            self.load_db()
        # ------------------------------------------------------------------
        # get header and hdict
        hdict, header = _get_hdict(self.params, self.name, drsfile)
        # ------------------------------------------------------------------
        # get file key
        dbkey = _get_dbkey(self.params, drsfile, self.name)
        # check dbname
        _get_dbname(self.params, drsfile, self.name)
        # get fiber
        fiber = _get_hkey(self.params, 'KW_FIBER', hdict, header)
        # get super definition
        is_super = _get_is_super(self.params)
        # get time
        header_time = _get_time(self.params, self.name, header, hdict)
        # ------------------------------------------------------------------
        # deal with database input being set to False
        if 'DATABASE' in self.params['INPUTS']:
            if not self.params['INPUTS']['DATABASE']:
                # Log that we are not adding file due to user input
                wargs = [dbkey, drsfile.filename]
                WLOG(self.params, 'info', TextEntry('40-001-00024', args=wargs))
                # return here
                return
        # ------------------------------------------------------------------
        # copy file to database directory
        if copy_files:
            _copy_db_file(self.params, drsfile, self.filedir, self.name,
                          verbose=verbose)
        # ------------------------------------------------------------------
        # get entries in correct format
        key = str(dbkey).strip()
        is_super = is_super
        fiber = str(fiber)
        filename = str(drsfile.basename).strip()
        human_time = str(header_time.iso)
        unix_time = str(header_time.unix).strip()
        used = 1
        # ------------------------------------------------------------------
        # add entry to database
        values = [key, fiber, is_super, filename, human_time, unix_time, used]
        self.database.add_row(values, 'MAIN', commit=True)

    def get_calib_entry(self, columns: str , key: str, fiber: Union[str, None],
                        filetime: Union[Time, None], timemode: str ='older',
                        nentries: Union[int, str] = '*'):
        """

        :param columns: str, pushed to SQL (i.e. list columns or '*' for all)
        :param key: str, KEY=="key" condition
        :param fiber: str or None, if set FIBER=="fiber"
        :param filetime: astropy.Time,
        :param timemode:
        :param nentries:
        :return:
        """
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # condition for key
        sql['condition'] = 'KEY == "{0}"'.format(key)
        # condition for used
        sql['condition'] += ' AND USED == 1'
        # condition for fiber
        if fiber is not None:
            sql['condition'] += ' AND FIBER == "{0}"'.format(fiber)
        # sql for time mode
        if timemode == 'older' and filetime is not None:
            # condition:
            #       UNIXTIME - FILETIME < 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} < 0'.format(filetime.unix)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
        elif timemode == 'newer' and filetime is not None:
            # condition:
            #       UNIXTIME - FILETIME > 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} > 0'.format(filetime.unix)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
        elif filetime is not None:
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
        # add the number of entries to get
        if isinstance(nentries, int):
            sql['max_rows'] = nentries
        # if we have one entry just get the tuple back
        if nentries == 1:
            # do sql query
            entries = self.database.get(columns, 'MAIN', **sql)
            # return filename
            if len(entries) == 1:
                return entries[0][0]
        elif len(columns) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, 'MAIN', **sql)
            # return one list
            return entries[:, 0]
        else:
            # return as pandas table
            sql['return_pandas'] = True
            # do sql query
            entries = self.database.get(columns, 'MAIN', **sql)
            # return pandas table
            return entries


    def get_calib_file(self, key: str, drsfile=None, header=None, hdict=None,
                       filetime: Union[None, Time] = None,
                       timemode: Union[str, None] = None,
                       nentries: Union[str, int] = 1,
                       required: bool = True,
                       no_times: bool = False):
        """
        Handles getting a filename from calibration database (from filename,
        user input, or key in SQL database

        if filename is set or userinputkey in params['INPUTS'] sql database
        is not used

        for file time precedence is as follows:
            filetime >> hdict >> header >> drsfile

        :param key: str, the calibration key to look for in sql database
        :param drsfile: if set get time from drsfile header/hdict
                        (unless filetime set)
        :param header: if set get time from header (unless filetime set)
        :param hdict: if set get time from hdict (unless filetime set)
        :param userinputkey: str or None, if in params['INPUTS'] and exists
                             this is the file return
        :param filetime: Astropy Time or None - if set do not need
                         drsfile/header/hdict
        :param filename: str or None, if set and exists this is the file return
        :param timemode: None to use default or 'older' for only files older
                         that time in header/hdict/drsfile
        :param nentries: int/str if using the sql database sets max number of
                         entries to return
        :param required: bool, if True will cause an exception when no entries
                         found
        :return:
        """
        # set function
        func_name = display_func(self.params, 'get_calib_file', __NAME__,
                                 self.classname)
        # deal with no database
        if self.database is None:
            self.load_db()
        # ---------------------------------------------------------------------
        # else we get it from database
        # ---------------------------------------------------------------------
        if no_times:
            filetime = None
        elif (filetime is None):
            # need to get hdict/header
            hdict, header = _get_hdict(self.params, self.name, drsfile, hdict,
                                       header)
            # need to get filetime
            filetime = _get_time(self.params, self.name, hdict, header)
        # ---------------------------------------------------------------------
        # get fiber
        fiber = _get_hkey(self.params, 'KW_FIBER', header, hdict)
        # ---------------------------------------------------------------------
        # deal with default time mode
        if timemode is None:
            # get default mode from params
            timemode = self.params['CALIB_DB_MATCH']
            if timemode not in ['closest', 'older', 'newer']:
                # log error: Time mode invalid for Calibration database.
                eargs = [timemode, ' or '.join(['closest', 'older', 'newer'])]
                emsg = TextEntry('00-002-00021', args=eargs)
                WLOG(self.params, 'error', emsg)
        # ---------------------------------------------------------------------
        # do sql query
        # ---------------------------------------------------------------------
        filenames = self.get_calib_entry('FILENAME', key, fiber, filetime,
                                         timemode, nentries)
        # ---------------------------------------------------------------------
        # return absolute paths
        # ---------------------------------------------------------------------
        # deal with no filenames found and not required
        if len(filenames) == 0 and not required:
            return None
        # deal with no filenames found elsewise --> error
        if len(filenames) == 0:
            # get unique set of keys
            keys = np.unique(self.database.get('KEY', return_array=True))
            # get file description
            if drsfile is not None:
                if no_times:
                    infile = '{0} [NoTime]'.format(drsfile.filename)
                else:
                    infile = '{0} [Time={1}]'.format(drsfile.filename,
                                                     filetime.iso)
            else:
                if no_times:
                    infile = 'File[NoTime]'
                else:
                    infile = 'File[Time={0}]'.format(filetime.iso)
            # log error: No entries found in {0} database for key='{1}
            eargs = [self.name, key, ', '.join(keys), infile, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00015', args=eargs))
        # make all files absolute paths
        if isinstance(filenames, str):
            return Path(self.filedir).joinpath(filenames).absolute()
        # else loop around them (assume they are iterable)
        else:
            # set output storage
            outfilenames = []
            # loop around filenames
            for filename in filenames:
                outfilename = Path(self.filedir).joinpath(filename).absolute()
                # append to storage
                outfilenames.append(outfilename)
            # return outfilenames
            return outfilenames


class TelluricDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        # save class name
        self.classname = 'TelluricDatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # construct super class
        DatabaseManager.__init__(self, params)
        # set name
        self.name = 'telluric'
        # set path
        self.set_path('TELLU_DBFILE_PATH', 'TELLU_DB_NAME', check=check)
        # set database directory
        self.filedir = Path(str(self.params['DRS_TELLU_DB']))


    def add_tellu_file(self, drsfile, verbose: bool = True,
                       copy_files=True):
        """
        Add DrsFile to the calibration database

        :param drsfile: DrsFile, the DrsFile to add
        :params verbose: bool, if True logs progress
        :param copy_files: bool, if True copies file to self.filedir
        :return:
        """
        # set function
        _ = display_func(self.params, 'add_tellu_file', __NAME__,
                         self.classname)
        # deal with no database
        if self.database is None:
            self.load_db()
        # ------------------------------------------------------------------
        # get header and hdict
        hdict, header = _get_hdict(self.params, self.name, drsfile)
        # ------------------------------------------------------------------
        # get file key
        dbkey = _get_dbkey(self.params, drsfile, self.name)
        # check dbname
        _get_dbname(self.params, drsfile, self.name)
        # get fiber
        fiber = _get_hkey(self.params, 'KW_FIBER', hdict, header)
        # get super definition
        is_super = _get_is_super(self.params)
        # get time
        header_time = _get_time(self.params, self.name, header, hdict)
        # get object name
        objname = _get_hkey(self.params, 'KW_OBJNAME', hdict, header)
        # get airmass
        airmass = _get_hkey(self.params, 'KW_AIRMASS', hdict, header,
                            dtype=float)
        # get tau_water
        tau_water = _get_hkey(self.params, 'KW_TELLUP_EXPO_WATER', hdict,
                              header, dtype=float)
        # get tau_others
        tau_others = _get_hkey(self.params, 'KW_TELLUP_EXPO_OTHERS', hdict,
                              header, dtype=float)
        # ------------------------------------------------------------------
        # deal with database input being set to False
        if 'DATABASE' in self.params['INPUTS']:
            if not self.params['INPUTS']['DATABASE']:
                # Log that we are not adding file due to user input
                wargs = [dbkey, drsfile.filename]
                WLOG(self.params, 'info', TextEntry('40-001-00024', args=wargs))
                # return here
                return
        # ------------------------------------------------------------------
        # copy file to database directory
        if copy_files:
            _copy_db_file(self.params, drsfile, self.filedir, self.name,
                          verbose=verbose)
        # ------------------------------------------------------------------
        # get entries in correct format
        key = str(dbkey).strip()
        is_super = is_super
        fiber = str(fiber)
        filename = str(drsfile.basename).strip()
        human_time = str(header_time.iso)
        unix_time = str(header_time.unix).strip()
        used = 1
        # ------------------------------------------------------------------
        # add entry to database
        values = [key, fiber, is_super, filename, human_time, unix_time,
                  objname, airmass, tau_water, tau_others, used]
        self.database.add_row(values, 'MAIN', commit=True)


# =============================================================================
# Define specific file functions (for use in specific file databases above)
# =============================================================================
def _get_dbkey(params, drsfile, dbmname):
    """
    Get the dbkey attribute from a drsfile

    :param params:
    :param drsfile:
    :param dbmname:
    :return:
    """
    # set function
    func_name = display_func(params, '_get_dbkey', __NAME__)
    # get dbname from drsfile
    if hasattr(drsfile, 'dbkey') and hasattr(drsfile, 'get_dbkey'):
        return drsfile.get_dbkey()
    else:
        eargs = [drsfile.name, dbmname, func_name]
        WLOG(params, 'error', TextEntry('00-008-00012', args=eargs))
        return


def _get_dbname(params, drsfile, dbmname):
    """
    Get the dbname attribute from a drsfile
    :param params:
    :param drsfile:
    :param dbmname:
    :return:
    """
    # set function
    func_name = display_func(params, '_get_dbname', __NAME__)
    # get dbname from drsfile
    if hasattr(drsfile, 'dbname'):
        dbname = drsfile.dbname.upper()
        # test db name against this database
        if dbname != dbmname.upper():
            eargs = [drsfile.name, dbname, dbmname.upper(), drsfile.filename,
                     func_name]
            WLOG(params, 'error', TextEntry('00-002-00019', args=eargs))
    else:
        eargs = [drsfile.name, dbmname, func_name]
        WLOG(params, 'error', TextEntry('00-008-00012', args=eargs))
        return


def _get_hkey(params, pkey, header, hdict, dtype: type = str):
    """
    Get the drs key fiber value (if present)
    :param drsfile:
    :return:
    """
    # gey key from params
    key = params[pkey][0]
    # set fiber to None
    value = None
    # get fiber from hdict
    if hdict is not None:
        if key in hdict:
            value = hdict[key]
    # get fiber from header if not in hdict
    if header is not None and value is None:
        if key in header:
            value = header[key]
    # deal with dtype
    if value is not None:
        value = dtype(value)
    # return fiber
    return value


def _get_is_super(params):
    """
    Find out whether file entry is from a super set or not

    :param params:
    :return:
    """
    # get master setting from params
    is_super = params['IS_MASTER']
    # change bool to 1 or 0
    # get master key
    if is_super:
        is_super = 1
    else:
        is_super = 0
    return is_super


def _copy_db_file(params, drsfile, outpath, dbmname, verbose):
    # set function
    func_name = display_func(params, '_copy_db_file', __NAME__)
    # construct in path
    inpath = drsfile.filename
    # construct out path
    outpath = Path(outpath).joinpath(drsfile.basename)
    # skip if inpath and outpath are the same
    if inpath == outpath:
        return
    # copy
    try:
        # log if verbose
        if verbose:
            margs = [dbmname, outpath]
            WLOG(params, '', TextEntry('40-006-00004', args=margs))
        # copy file using shutil (should be thread safe)
        shutil.copyfile(inpath, outpath)
    except Exception as e:
        # log exception:
        eargs = [dbmname, inpath, outpath, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-002-00014', args=eargs))


def _get_hdict(params, dbname, drsfile, hdict=None, header=None):
    # set function name
    func_name = display_func(params, '_get_hdict', __NAME__)
    # deal with having hdict input
    if hdict is not None:
        return hdict, None
    # deal with having header input
    elif header is not None:
        return None, header
    # get hdict
    if hasattr(drsfile, 'hdict') and len(list(drsfile.hdict.keys())) != 0:
        hdict = drsfile.hdict
        header = None
    elif hasattr(drsfile, 'header') and len(list(drsfile.header.keys())) != 0:
        hdict = None
        header = drsfile.header
    else:
        eargs = [dbname, drsfile.name, func_name]
        WLOG(params, 'error', TextEntry('00-001-00027', args=eargs))
        hdict, header = None, None
    return hdict, header


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


# =============================================================================
# Define other databases
# =============================================================================
class IndexDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        # save class name
        self.classname = 'IndexDatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # construct super class
        DatabaseManager.__init__(self, params)
        # set name
        self.name = 'index'
        # set path
        self.set_path(None, 'TELLU_DB_NAME', check=check)


class LogDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        # save class name
        self.classname = 'LogDatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # construct super class
        DatabaseManager.__init__(self, params)
        # set name
        self.name = 'log'
        # set path
        self.set_path(None, 'LOG_DB_NAME', check=check)


class ObjectDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        # save class name
        self.classname = 'ObjectDatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # construct super class
        DatabaseManager.__init__(self, params)
        # set name
        self.name = 'object'
        # set path
        self.set_path(None, 'OBJECT_DB_NAME', check=check)



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
