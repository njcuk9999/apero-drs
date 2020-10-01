#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-18 15:15

@author: cook
"""
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
from typing import Any, List, Tuple, Type, Union

from apero.base import base
from apero.base import drs_db
from apero.base import drs_exceptions
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log

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
# get drs header
DrsHeader = drs_file.Header
FitsHeader = drs_file.FitsHeader
# get file types
DrsInputFile = drs_file.DrsInputFile
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
# define drs files
DrsFileTypes = Union[drs_file.DrsInputFile, drs_file.DrsFitsFile,
                     drs_file.DrsNpyFile]


# =============================================================================
# Define classes
# =============================================================================
class DatabaseManager:
    """
    Apero Database Manager class (basically abstract)
    """

    def __init__(self, params: ParamDict, check: bool = False):
        """
        Construct the Database Manager

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is) - base class does nothing
        """
        # save class name
        self.classname = 'DatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # save params for use throughout
        self.params = params
        # set name
        self.name = 'DatabaseManager'
        # check does nothing
        _ = check
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
        # noinspection PyBroadException
        try:
            dirname = Path(dirname)
        except Exception as _:
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

    def load_db(self, check: bool = False):
        """
        Load the database class and connect to SQL database

        :param check: if True will reload the database even if already defined
                      else if we Database.database is set this function does
                      nothing

        :return:
        """
        # set function
        _ = display_func(self.params, 'load_db', __NAME__, self.classname)
        # if we already have database do nothing
        if (self.database is not None) and (not check):
            return
        # load database only if path is set
        if self.path is not None:
            # log that we are loading database
            margs = [self.name, self.path]
            WLOG(self.params, 'info', TextEntry('40-006-00005', args=margs))
            # load database
            self.database = drs_db.Database(self.path)

    def __str__(self):
        """
        Return the string representation of the class
        :return:
        """
        # set function
        _ = display_func(self.params, '__str__', __NAME__, self.classname)
        # return string representation
        return '{0}[{1}]'.format(self.classname, self.path)

    def __repr__(self):
        """
        Return the string representation of the class
        :return:
        """
        # set function
        _ = display_func(self.params, '__repr__', __NAME__, self.classname)
        # return string representation
        return self.__str__()


# =============================================================================
# Define specific file databases
# =============================================================================
class CalibrationDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        """
        Constructor of the Calibration Database class

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
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
        :param verbose: bool, if True logs progress
        :param copy_files: bool, if True copies file to self.filedir

        :return: None
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

    def get_calib_entry(self, columns: str, key: str,
                        fiber: Union[str, None] = None,
                        filetime: Union[Time, None] = None,
                        timemode: str = 'older',
                        nentries: Union[int, str] = '*'
                        ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the calibration database

        :param columns: str, pushed to SQL (i.e. list columns or '*' for all)
        :param key: str, KEY=="key" condition
        :param fiber: str or None, if set FIBER=="fiber"
        :param filetime: astropy.Time, if Not None the point in time to order
                         the files by
        :param timemode: str, the way in which to select which calibration to
                         use (either 'older' 'closest' or 'newer'
        :param nentries: int or str, the number of entries to return
                         only valid string is '*' for all entries

        :return: the entries of columns, if nentries = 1 returns either that
                 entry (as a tuple) or None, if len(columns) = 1, returns
                 a np.ndarray, else returns a pandas table
        """
        # set function
        _ = display_func(self.params, 'get_calib_entry', __NAME__,
                         self.classname)
        # set up kwargs from database query
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
            sql['sort_descending'] = False
        elif timemode == 'newer' and filetime is not None:
            # condition:
            #       UNIXTIME - FILETIME > 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} > 0'.format(filetime.unix)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
            sql['sort_descending'] = False
        elif filetime is not None:
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
            sql['sort_descending'] = False
        else:
            # sort by: UNIXTIME
            sql['sort_by'] = 'UNIXTIME'
            sql['sort_descending'] = True

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
            else:
                return None

        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, 'MAIN', **sql)
            # return one list
            if len(entries) == 0:
                return []
            else:
                return entries[:, 0]
        # else return a pandas table
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
                       no_times: bool = False,
                       fiber: Union[str, None] = None
                       ) -> Union[None, Path, List[Path]]:
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
        :param filetime: Astropy Time or None - if set do not need
                         drsfile/header/hdict
        :param timemode: None to use default or 'older' for only files older
                         that time in header/hdict/drsfile
        :param nentries: int/str if using the sql database sets max number of
                         entries to return
        :param required: bool, if True will cause an exception when no entries
                         found
        :param no_times: bool, if True does not use times to choose correct
                         files
        :param fiber: str or None, if set sets the fiber to use - if no fiber
                      required do not set
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
        if no_times or header is None:
            filetime = None
        elif filetime is None:
            # need to get hdict/header
            hdict, header = _get_hdict(self.params, self.name, drsfile, hdict,
                                       header)
            # need to get filetime
            filetime = _get_time(self.params, self.name, hdict, header)
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
        # get calibration database entries --> FILENAME
        #   if nentries = 1 : str or None
        #   if nentries > 1 : 1d numpy array
        filenames = self.get_calib_entry('FILENAME', key, fiber, filetime,
                                         timemode, nentries)
        # ---------------------------------------------------------------------
        # return absolute paths
        # ---------------------------------------------------------------------
        # deal with no filenames found and not required
        if (filenames is None or len(filenames) == 0) and not required:
            return None
        # deal with no filenames found elsewise --> error
        if filenames is None or len(filenames) == 0:
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
        """
        Constructor of the Telluric Database class

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
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

    def add_tellu_file(self, drsfile: DrsInputFile, verbose: bool = True,
                       copy_files: bool = True,
                       objname: Union[str, None] = None,
                       airmass: Union[float, str, None] = None,
                       tau_water: Union[float, str, None] = None,
                       tau_others: Union[float, str, None] = None):
        """
        Add DrsFile to the calibration database

        :param drsfile: DrsFile, the DrsFile to add
        :param verbose: bool, if True logs progress
        :param copy_files: bool, if True copies file to self.filedir
        :param objname: str or None, the object name if None uses object name
                        from drsfile.header
        :param airmass: float or str or None, if flaot is the airmass value
                        if str then should be 'None' to show no value wanted
                        if None then uses airmass from drsfile.header
        :param tau_water:  float or str or None, if flaot is the tau_water value
                           if str then should be 'None' to show no value wanted
                           if None then uses tau_water from drsfile.header
        :param tau_others: float or str or None, if flaot is the tau_others
                           value if str then should be 'None' to show no value
                           wanted if None then uses tau_others from
                           drsfile.header

        :return: None - adds row to the database (and copies file if
                        copy_files=True)
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
        if objname is None:
            objname = _get_hkey(self.params, 'KW_OBJNAME', hdict, header)
        # get airmass
        if airmass is None:
            airmass = _get_hkey(self.params, 'KW_AIRMASS', hdict, header,
                                dtype=float)
        # get tau_water
        if tau_water is None:
            tau_water = _get_hkey(self.params, 'KW_TELLUP_EXPO_WATER', hdict,
                                  header, dtype=float)
        # get tau_others
        if tau_others is None:
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
        # deal with no tau_water/tau_other being None (should be float)
        # if tau_water is None:
        #     tau_water = 'None'
        # if tau_others is None:
        #     tau_others = 'None'
        # ------------------------------------------------------------------
        # add entry to database
        values = [key, fiber, is_super, filename, human_time, unix_time,
                  objname, airmass, tau_water, tau_others, used]
        self.database.add_row(values, 'MAIN', commit=True)

    def get_tellu_entry(self, columns: str, key: str,
                        fiber: Union[str, None] = None,
                        filetime: Union[Time, None] = None,
                        timemode: str = 'older',
                        nentries: Union[int, str] = '*',
                        objname: Union[str, None] = None,
                        tau_water: Union[Tuple[float, float], None] = None,
                        tau_others: Union[Tuple[float, float], None] = None,
                        ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the calibration database

        :param columns: str, pushed to SQL (i.e. list columns or '*' for all)
        :param key: str, KEY=="key" condition
        :param fiber: str or None, if set FIBER=="fiber"
        :param filetime: astropy.Time, if Not None the point in time to order
                         the files by
        :param timemode: str, the way in which to select which telluric to
                         use (either 'older' 'closest' or 'newer')
                         based on filetime as the "zero point" time
        :param nentries: int or str, the number of entries to return
                         only valid string is '*' for all entries
        :param objname: str or None, if set OBJECT=="fiber"
        :param tau_water: tuple or None, if set sets the lower and upper
                          bounds for tau water i.e.
                          TAU_WATER > tau_water[0]
                          TAU_WATER < tau_water[1]
        :param tau_others: tuple or None, if set sets the lower and upper bounds
                           for tau others  i.e.
                           TAU_OTHERS > tau_others[0]
                           TAU_OTHERS < tau_others[1]
        :return: the entries of columns, if nentries = 1 returns either that
                 entry (as a tuple) or None, if len(columns) = 1, returns
                 a np.ndarray, else returns a pandas table
        """
        # set function
        _ = display_func(self.params, 'get_tellu_entry', __NAME__,
                         self.classname)
        # set up kwargs from database query
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
        # condition for objname
        if objname is not None:
            sql['condition'] += ' AND OBJECT == "{0}"'.format(objname)

        # condition for tau_water
        if tau_water is not None and len(tau_water) == 2:
            sql['condition'] += 'AND TAU_WATER > {0}'.format(tau_water[0])
            sql['condition'] += 'AND TAU_WATER < {0}'.format(tau_water[1])

        # condition for tau_other
        if tau_others is not None and len(tau_others) == 2:
            sql['condition'] += 'AND TAU_OTHERS > {0}'.format(tau_others[0])
            sql['condition'] += 'AND TAU_OTHERS < {0}'.format(tau_others[1])

        # sql for time mode
        if timemode == 'older' and filetime is not None:
            # condition:
            #       UNIXTIME - FILETIME < 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} < 0'.format(filetime.unix)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
            sql['sort_descending'] = False
        elif timemode == 'newer' and filetime is not None:
            # condition:
            #       UNIXTIME - FILETIME > 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} > 0'.format(filetime.unix)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
            sql['sort_descending'] = False
        elif filetime is not None:
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['sort_by'] = 'abs(UNIXTIME - {0})'.format(filetime.unix)
            sql['sort_descending'] = False
        else:
            # sort by: UNIXTIME
            sql['sort_by'] = 'UNIXTIME'
            sql['sort_descending'] = True
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
            else:
                return None
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, 'MAIN', **sql)
            # return one list
            if len(entries) == 0:
                return []
            else:
                return entries[:, 0]
        # else return a pandas table
        else:
            # return as pandas table
            sql['return_pandas'] = True
            # do sql query
            entries = self.database.get(columns, 'MAIN', **sql)
            # return pandas table
            return entries

    def get_tellu_file(self, key: str, drsfile=None, header=None, hdict=None,
                       filetime: Union[None, Time] = None,
                       timemode: Union[str, None] = None,
                       nentries: Union[str, int] = 1,
                       required: bool = True,
                       no_times: bool = False,
                       objname: Union[str, None] = None,
                       tau_water: Union[Tuple[float, float], None] = None,
                       tau_others: Union[Tuple[float, float], None] = None,
                       fiber: Union[str, None] = None
                       ) -> Union[None, Path, List[Path]]:
        """
        Handles getting a filename from telluric database (from filename,
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
        :param filetime: Astropy Time or None - if set do not need
                         drsfile/header/hdict
        :param timemode: None to use default or 'older' for only files older
                         that time in header/hdict/drsfile
        :param nentries: int/str if using the sql database sets max number of
                         entries to return
        :param required: bool, if True will cause an exception when no entries
                         found
        :param no_times: bool, if True does not use times to choose correct
                         files
        :param objname: str or None, if set filters by object name

        :param tau_water: tuple or None, filters the lower and upper
                          bounds for tau water i.e.
                          TAU_WATER > tau_water[0]
                          TAU_WATER < tau_water[1]
        :param tau_others: tuple or None, filters the lower and upper bounds
                           for tau others  i.e.
                           TAU_OTHERS > tau_others[0]
                           TAU_OTHERS < tau_others[1]

        :param fiber: str or None, if set sets the fiber to use - if no fiber
                      required do not set
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
        if no_times or header is None:
            filetime = None
        elif filetime is None:
            # need to get hdict/header
            hdict, header = _get_hdict(self.params, self.name, drsfile, hdict,
                                       header)
            # need to get filetime
            filetime = _get_time(self.params, self.name, hdict, header)
        # ---------------------------------------------------------------------
        # deal with default time mode
        if timemode is None:
            # get default mode from params
            timemode = self.params['TELLU_DB_MATCH']
            if timemode not in ['closest', 'older', 'newer']:
                # log error: Time mode invalid for Calibration database.
                eargs = [timemode, ' or '.join(['closest', 'older', 'newer'])]
                emsg = TextEntry('00-002-00021', args=eargs)
                WLOG(self.params, 'error', emsg)
        # ---------------------------------------------------------------------
        # do sql query
        # ---------------------------------------------------------------------
        # get calibration database entries --> FILENAME
        #   if nentries = 1 : str or None
        #   if nentries > 1 : 1d numpy array
        filenames = self.get_tellu_entry('FILENAME', key, fiber, filetime,
                                         timemode, nentries, objname,
                                         tau_water, tau_others)
        # deal with filename being pandas dataframe (i.e.

        # ---------------------------------------------------------------------
        # return absolute paths
        # ---------------------------------------------------------------------
        # deal with no filenames found and not required
        if (filenames is None or len(filenames) == 0) and not required:
            return None
        # deal with no filenames found elsewise --> error
        if filenames is None or len(filenames) == 0:
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


# =============================================================================
# Define specific file functions (for use in specific file databases above)
# =============================================================================
def _get_dbkey(params: ParamDict, drsfile: DrsFileTypes, dbmname: str) -> str:
    """
    Get the dbkey attribute from a drsfile

    :param params: ParamDict, parameter dictionary of constants
    :param drsfile: DrsFile instance used to get the dbkey
    :param dbmname: str, the name of the database

    :return: str, the dbkey
    """
    # set function
    func_name = display_func(params, '_get_dbkey', __NAME__)
    # get dbname from drsfile
    if hasattr(drsfile, 'dbkey') and hasattr(drsfile, 'get_dbkey'):
        return drsfile.get_dbkey()
    else:
        eargs = [drsfile.name, dbmname, func_name]
        WLOG(params, 'error', TextEntry('00-008-00012', args=eargs))
        return 'None'


def _get_dbname(params: ParamDict, drsfile: DrsFileTypes, dbmname: str) -> bool:
    """
    Check the dbname attribute from a drsfile matches the database type

    :param params: ParamDict, the parameter dictionary of constants
    :param drsfile: DrsInputFile (fits or npy) instance to get dbname from
    :param dbmname: str, the name of the database

    :return: bool, True if passed (raises exception otherwise)
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
            return False
    else:
        eargs = [drsfile.name, dbmname, func_name]
        WLOG(params, 'error', TextEntry('00-008-00012', args=eargs))
        return False
    # if we are here return True --> success
    return True


def _get_hkey(params: ParamDict, pkey: str,
              header: Union[FitsHeader, DrsHeader, None],
              hdict: Union[DrsHeader, None], dtype: Type = str) -> Any:
    """
    Get the value for a header key "pkey (if present in hdict, then in header)
    else if not present return None

    :param params: ParamDict, the parameter dictionary of constants
    :param pkey: str, the key in the headers to check
    :param header: astropy.io.fits header or drs_fits.Header to check for pkey
    :param hdict: drs_fits.Header to check for pkey (takes precendence over
                  header
    :param dtype: type the type to force return value to

    :return: Any, the value for pkey (None if not found)
    """
    # set function
    func_name = display_func(params, '_get_hkey', __NAME__)
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
        try:
            value = dtype(value)
        except Exception as e:
            eargs = [type(e), str(e), func_name]
            WLOG(params, 'error', TextEntry('00-000-00002', args=eargs))
    # return fiber
    return value


def _get_is_super(params: ParamDict) -> int:
    """
    Find out whether file entry is from a super set or not

    :param params: ParamDict, the parameter dictionary of constants

    :return: 1 if code is super else returns 0
    """
    # get master setting from params
    is_super = params['IS_MASTER']
    # change bool to 1 or 0
    # get master key
    if is_super:
        is_super = 1
    else:
        is_super = 0
    # return is super value
    return is_super


def _copy_db_file(params: ParamDict, drsfile: DrsFileTypes,
                  outpath: Union[str, Path], dbmname: str,
                  verbose: bool = True):
    """
    Copy a database file from drsfile.filename to outpath

    :param params: ParamDict, parameter dictionary of constants
    :param drsfile: DrsInputFile (fits or npy) instance to get .filename from
    :param outpath: str or Path, the output directory to copy the file to
    :param dbmname: str, the database name
    :param verbose: bool, if True log that we are copying files

    :return: None
    """
    # set function
    func_name = display_func(params, '_copy_db_file', __NAME__)
    # construct in path
    inpath = drsfile.filename
    # construct out path
    outpath = Path(outpath).joinpath(drsfile.basename)
    # skip if inpath and outpath are the same
    if str(inpath) == str(outpath):
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


HeaderType = Union[DrsHeader, FitsHeader, None]


def _get_hdict(params: ParamDict, dbname: str, drsfile: DrsFileTypes = None,
               hdict: HeaderType = None,
               header: HeaderType = None) -> Tuple[HeaderType, HeaderType]:
    """
    Get the hdict and header (either from inputs or drsfile)

    :param params: ParamDict, parameter dictionary of constants
    :param dbname: str, the database name
    :param drsfile: DrsInputFile (fits or npy) instance to get the hdict/header
                    from (if hdict and header are both None)
    :param header: astropy.io.fits header or drs_fits.Header to check for pkey
    :param hdict: drs_fits.Header to check for pkey (takes precendence over
                  header

    :return: hdict (None if not found) and header (None if not found)
    """
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
    elif (hasattr(drsfile, 'header') and
          len(list(drsfile.get_header().keys())) != 0):
        hdict = None
        header = drsfile.get_header()
    else:
        eargs = [dbname, drsfile.name, func_name]
        WLOG(params, 'error', TextEntry('00-001-00027', args=eargs))
        hdict, header = None, None
    return hdict, header


def _get_time(params: ParamDict, dbname: str,
              hdict: HeaderType = None, header: HeaderType = None,
              kind: Union[str, None] = None) -> Union[Time, str, float]:
    """
    Get the time from the header/hdict and return in format "kind"

    :param params: ParamDict, parameter dictionary of constants
    :param dbname: str, the database name
    :param header: astropy.io.fits header or drs_fits.Header to check for pkey
    :param hdict: drs_fits.Header to check for pkey (takes precendence over
                  header
    :param kind: str
    :return:
    """
    # set function name
    func_name = display_func(params, '_get_time', __NAME__)
    # ----------------------------------------------------------------------
    # get raw time from hdict / header
    if hdict is not None:
        t, m = drs_file.get_mid_obs_time(params, hdict, out_fmt=kind)
        return t
    elif header is not None:
        t, m = drs_file.get_mid_obs_time(params, header, out_fmt=kind)
        return t
    else:
        eargs = [dbname, func_name]
        WLOG(params, 'error', TextEntry('00-001-00039', args=eargs))


# =============================================================================
# Define other databases
# =============================================================================
class IndexDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        """
        Constructor of the Index Database class

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
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
        """
        Constructor of the Log Database class

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
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
        """
        Constructor of the Object Database class

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
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
