#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-18 15:15

@author: cook

## import rules

only from core.core, core.math, core.constants, apero.lang, apero.base
"""
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
from typing import Any, Dict, List, Tuple, Type, Union
from tqdm import tqdm

from apero.base import base
from apero.base import drs_misc
from apero.base import drs_db
from apero.base import drs_exceptions
from apero.base import drs_text
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.core.drs_database.py'
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
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get list of obj name cols
OBJNAMECOLS = ['KW_OBJNAME']


# =============================================================================
# Define classes
# =============================================================================
class DatabaseManager:
    """
    Apero Database Manager class (basically abstract)
    """
    # define attribute types
    path: Union[Path, str, None]
    database: Union[drs_db.Database, None]

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
        self.instrument = params['INSTRUMENT']
        # get pconst (for use throughout)
        self.pconst = constants.pload(self.instrument)
        # set name
        self.name = 'DatabaseManager'
        # set parameters
        self.dbpath = None
        self.dbname = None
        self.dbreset = None
        # check does nothing
        _ = check
        # set path
        self.path = None
        # set unloaded database
        self.database = None

    def set_path(self, kind: str, check: bool = True):
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

        # deal with no instrument (i.e. no database)
        if self.instrument == 'None':
            return
        # load database settings
        self.database_settings(kind=kind)
        # ---------------------------------------------------------------------
        # deal with directory
        # ---------------------------------------------------------------------
        # get directory name
        dirname = str(self.dbpath)
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
        # check for directory
        if not dirname.exists() and check:
            # log error: Directory {0} does not exist (database = {1})
            eargs = [dirname, self.name, func_name]
            WLOG(self.params, 'error', TextEntry('00-002-00017', args=eargs))
            return
        # ---------------------------------------------------------------------
        # add filename
        # ---------------------------------------------------------------------
        # get directory name
        filename = str(self.dbname)
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
        # deal with no instrument
        if self.instrument == 'None':
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

    def database_settings(self, kind: str):
        # load database yaml file
        ddict = base.DPARAMS
        # ----------------------------------------------------------------------
        # SQLITE3 settings
        # ----------------------------------------------------------------------
        if ddict['USE_SQLITE3']:
            # force kind to upper
            kind = kind.upper()
            # kind must be one of the following
            if kind not in ['CALIB', 'TELLU', 'INDEX', 'LOG', 'OBJECT', 'LANG']:
                raise ValueError('kind=={0} invalid'.format(kind))
            # set name/path/reset based on ddict
            self.dbname = ddict['SQLITE3'][kind]['NAME']
            self.dbpath = ddict['SQLITE3'][kind]['PATH']
            if drs_text.null_text(ddict['SQLITE3'][kind]['RESET'], ['None']):
                self.dbreset = None
            else:
                self.dbreset = ddict['SQLITE3'][kind]['RESET']
        else:
            NotImplemented('MySQL not implemented yet')


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
        self.set_path(kind='CALIB', check=check)
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
        # deal with no instrument
        if self.instrument == 'None':
            return
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
        # deal with no instrument set
        if self.instrument == 'None':
            return None
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
        # deal with no instrument set
        if self.instrument == 'None':
            return None
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
        self.set_path(kind='TELLU', check=check)
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
        # deal with no instrument set
        if self.instrument == 'None':
            return
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
        # deal with no instrument set
        if self.instrument == 'None':
            return None
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
        # deal with no instrument set
        if self.instrument == 'None':
            return None
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
# Define index databases
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
        self.set_path(kind='INDEX', check=check)
        # store whether an update has been done
        self.update_entries_params = []

    def add_entry(self, directory: str, filename: Union[Path, str], kind: str,
                  runstring: Union[str, None] = None,
                  hkeys: Union[Dict[str, str], None] = None,
                  fullpath: Union[Path, str, None] = None,
                  used: Union[int, None] = None,
                  rawfix: Union[int, None] = None,
                  force_dir: Union[str, None] = None):
        """
        Add an entry to the index database

        :param directory: str, the sub-directory name (under the raw/reduced/
                          tmp directory)
        :param filename: str or Path, the filename to add (can be absolute file
                         or basename, but must exist on disk)
        :param kind: str, either 'raw', 'red', 'tmp', 'calib', 'tellu', 'asset'
                     this determines the path of the file i.e.
                     path/directory/filename (unless filename is an absolute
                     path) - note in this case directory should still be
                     filled correctly (for database)

        :param hkeys: dictionary of strings, for each instrument a set
                            of header keys is index - add any that are set to
                            here (see pseudo_constants.INDEX_HEADER_KEYS)
                            any that are not set here are set to 'None'

        :param fullpath: str or None, if set means there is already a 'path'
                         parameter
        :param used: int or None, if set overrides the default "used" parameter
        :param rawfix: int or None, if set overrides the default "rawfix"
                       parameter
        :param force_dir: str or None, if set overrides our "kind" path

        :return: None - adds entry to index database
        """
        # set function
        func_name = display_func(self.params, 'add_entry', __NAME__,
                                 self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # deal with filename/basename/path
        out = self.deal_with_filename(kind, directory, filename,
                                      fullpath=fullpath, func=func_name,
                                      force_dir=force_dir)
        filename, basename, path = out

        # set used to 1
        if used is None:
            used = 1
        # this is a flag to test whether raw data has been fixed (so we don't
        #   do it again when not required)
        if rawfix is not None:
            if kind == 'raw':
                rawfix = 0
            else:
                rawfix = 1
        # ------------------------------------------------------------------
        # get last modified time for file (need absolute path)
        last_modified = filename.stat().st_mtime
        # get run string
        if runstring is None:
            runstring = 'None'
        # ------------------------------------------------------------------
        # get allowed header keys
        rkeys, rtypes = self.pconst.INDEX_HEADER_KEYS()
        # store values in correct order for database.add_row
        hvalues = []
        # deal with no hkeys
        if hkeys is None:
            hkeys = dict()
        # loop around allowed header keys and check for them in headers
        #  keys - if not there set to 'None'
        for h_it, hkey in enumerate(rkeys):
            if hkey in hkeys:
                try:
                    # get data type
                    dtype = rtypes[h_it]
                    # try to case and append
                    hvalues.append(dtype(hkeys[hkey]))
                except Exception as _:
                    wargs = [self.name, hkey, hkeys[hkey],
                             rtypes[h_it], func_name]
                    wmsg = TextEntry('10-002-00003', args=wargs)
                    WLOG(self.params, 'warning', wmsg)
                    hvalues.append('None')
            else:
                hvalues.append('None')
        # ------------------------------------------------------------------
        # make absolute path
        path = Path(path).joinpath(directory, filename)
        # ------------------------------------------------------------------
        # get current list of paths for
        currentpath = self.get_entries('PATH', directory=directory,
                                       filename=basename, nentries=1)
        # ------------------------------------------------------------------
        # deal with updating entry
        if currentpath is not None and str(currentpath) == str(path):
            # add new entry to database
            values = [str(path), str(directory), str(basename), str(kind),
                      float(last_modified), str(runstring)]
            values += hvalues + [used, rawfix]
            # set up condition
            condition = 'FILENAME == "{0}"'.format(filename)
            condition += ' AND DIRECTORY == "{0}"'.format(directory)
            condition += ' AND PATH == "{0}"'.format(path)
            # update row in database
            self.database.set('*', values, condition=condition, table='MAIN',
                              commit=True)
        else:
            # add new entry to database
            values = [str(path), str(directory), str(basename), str(kind),
                      float(last_modified), str(runstring)]
            values += hvalues + [used, rawfix]
            self.database.add_row(values, 'MAIN', commit=True)

    def get_entries(self, columns: str = '*',
                    directory: Union[str, None] = None,
                    filename: Union[Path, str, None] = None,
                    kind: Union[str, None] = None,
                    hkeys: Union[Dict[str, str], None] = None,
                    nentries: Union[int, None] = None,
                    condition: Union[str, None] = None,
                    ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the index database (can set columns to return, or
        filter by specific columns)

        :param columns: str, the columns to return ('*' for all)
        :param directory: str or None, if set filters results by directory name
        :param filename: str or None, if set filters results by filename
        :param kind: str or None, if set filters results by kind
        :param hkeys: dict or None, if set is a dictionary of strings
                            where each string is one of the index database
                            header keys (see pseudo_constants.INDEX_HEADER_KEYS)
        :param nentries: int or None, if set limits the number of entries to get
                         back - sorted newest to oldest
        :param condition: str or None, if set the SQL query to add

        :return: the entries of columns, if nentries = 1 returns either that
                 entry (as a tuple) or None, if len(columns) = 1, returns
                 a np.ndarray, else returns a pandas table
        """
        # set function
        func_name = display_func(self.params, 'get_entries', __NAME__,
                                 self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # ------------------------------------------------------------------
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # sort by last modified
        sql['sort_by'] = 'LAST_MODIFIED'
        # condition for used
        sql['condition'] = 'USED == 1'
        # ------------------------------------------------------------------
        if condition is not None:
            sql['condition'] += ' AND {0}'.format(condition)
        # ------------------------------------------------------------------
        # deal with kind set
        if kind is not None:
            sql['condition'] += ' AND KIND == "{0}"'.format(kind)
        # ------------------------------------------------------------------
        # deal with directory set
        if directory is not None:
            sql['condition'] += ' AND DIRECTORY == "{0}"'.format(directory)
        # ------------------------------------------------------------------
        # deal with filename set
        if filename is not None:
            sql['condition'] += ' AND FILENAME == "{0}"'.format(filename)
        # ------------------------------------------------------------------
        # get allowed header keys
        rkeys, rtypes = self.pconst.INDEX_HEADER_KEYS()
        # deal with filter by header keys
        if hkeys is not None and isinstance(hkeys, dict):

            for h_it, hkey in enumerate(rkeys):
                if hkey in hkeys:
                    try:
                        # get data type
                        dtype = rtypes[h_it]
                        # try to case and add to condition
                        hargs = [hkey, dtype(hkeys[hkey])]
                        sql['condition'] += ' AND {0} == "{1}"'.format(*hargs)
                    except Exception as e:
                        wargs = [self.name, hkey, hkeys[hkey],
                                 rtypes[h_it], func_name]
                        wmsg = TextEntry('10-002-00003', args=wargs)
                        WLOG(self.params, 'warning', wmsg)
        # ------------------------------------------------------------------
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
        # ------------------------------------------------------------------
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

    # complex typing for filename(s) in update_entries
    FileTypes = Union[List[Union[Path, str]], Path, str, None]

    def update_entries(self, kind,
                       include_directories: Union[List[str], None] = None,
                       exclude_directories: Union[List[str], None] = None,
                       filename: FileTypes = None, suffix: str = '',
                       force_dir: Union[str, None] = None,
                       force_update: bool = False):
        """
        Update the index database for files of 'kind', deal with including
        and excluding directories for files with 'suffix'

        :param kind: str, either 'raw', 'red', 'tmp', 'calib', 'tellu', 'asset'
                     this determines the path of the file i.e.
                     path/directory/filename (unless filename is an absolute
                     path) - note in this case directory should still be
                     filled correctly (for database)
        :param include_directories: list of strings or None, if set only
                                    include these directories to update
                                    index database
        :param exclude_directories: list of strings or None, if set exclude
                                    these directories from being updated
                                    in the index database
        :param filename: str, Path, list of strs/Paths or None, if set we only
                         include this filename or these filenames
        :param suffix: str, the suffix (i.e. extension of filenames) - filters
                       to only set these files
        :param force_dir: str or None, if set overrides our "kind" path

        :return: None - updates the index database
        """
        # set function
        func_name = display_func(self.params, 'update_entries', __NAME__,
                                 self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # ---------------------------------------------------------------------
        # deal with database already being up-to-date
        # store whether an update has been done
        if not force_update:
            # if the exact same inputs have been used we can skip update
            #   (Again unless "force_update" was used)
            cond = self._update_params(kind=kind,
                                       include_directories=include_directories,
                                       exclude_directories=exclude_directories,
                                       filename=filename, force_dir=force_dir)
            # if we are not updating return here
            if not cond:
                return None
        # ---------------------------------------------------------------------
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # get the path for kind
        path = self.deal_with_filename(kind, None, None, force_dir=force_dir)
        # ---------------------------------------------------------------------
        # deal with a predefined file list (or single file)
        if filename is not None:
            if isinstance(filename, (str, Path)):
                include_files = [filename]
            else:
                include_files = filename
        else:
            include_files = []
        # ---------------------------------------------------------------------
        # deal with files we don't need (already have)
        exclude_files = self.get_entries('PATH', kind=kind)
        # ---------------------------------------------------------------------
        # locate all files within path
        reqfiles = _get_files(path, kind, include_directories,
                              exclude_directories, include_files,
                              exclude_files, suffix)
        # ---------------------------------------------------------------------
        # get a list of keys
        rkeys, rtypes = self.pconst.INDEX_HEADER_KEYS()
        # ---------------------------------------------------------------------
        # deal with no files
        if len(reqfiles) == 0:
            # set condition that we have updated
            self.has_update_entries = True
            # return
            return
        # add required files to the database
        for reqfile in tqdm(reqfiles):
            # set directory
            uncommonpath = drs_misc.get_uncommon_path(path, reqfile)
            # get the directory name
            directory = Path(uncommonpath).parent
            # get the basename
            basename = Path(uncommonpath).name
            # get header keys
            hkeys = dict()
            # load missing files
            if str(reqfile).endswith('.fits'):
                # load header
                header = drs_fits.read_header(self.params, str(reqfile))
                # loop around required keys
                for rkey in rkeys:
                    # get drs key
                    drs_key = self.params[rkey][0]

                    if drs_key in header:
                        hkeys[rkey] = header[drs_key]
            # add to database
            self.add_entry(directory, basename, kind, hkeys=hkeys)


    def update_header_fix(self, recipe):
        # set function name
        func_name = display_func(self.params, 'update_objname', __NAME__,
                                 self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # get allowed header keys
        rkeys, rtypes = self.pconst.INDEX_HEADER_KEYS()
        # get columns
        columns = ['PATH', 'RAWFIX'] + rkeys
        # get data for columns
        table = self.get_entries(', '.join(columns), kind='raw')
        # need to loop around each row
        for row in tqdm(range(len(table))):
            # do not re-fix is rawfix is 1
            # if table['RAWFIX'].iloc[row] == 1:
            #    continue
            # get new header to push keys into
            header = drs_fits.Header()
            # add keys to header
            for rkey in rkeys:
                # get drs key
                drs_key = self.params[rkey][0]
                # get value from table for rkey
                value = table[rkey].iloc[row]
                # populate header
                header[drs_key] = value
            # fix header (with new keys in)
            header, _ = drs_file.fix_header(self.params, recipe, header=header)
            # condition is that full path is the same
            condition = 'PATH=="{0}"'.format(table['PATH'].iloc[row])
            # get values
            values = [table['PATH'].iloc[row], 1]
            # add header keys in rkeys
            for rkey in rkeys:
                # get drs key
                drs_key = self.params[rkey][0]
                # get value from table for rkey
                if drs_key in header:
                    values.append(header[drs_key])
                else:
                    values.append('None')
            # update this row (should only be one row based on condition)
            self.database.set(columns, values, condition=condition)


    def deal_with_filename(self, kind: str, directory: Union[str, None] = None,
                           filename: Union[str, None] = None,
                           fullpath: Union[str, None] = None,
                           force_dir: Union[str, None] = None,
                           func: Union[str, None] = None
                           ) -> Union[str, Tuple[Path, str, str]]:
        """
        Wrapper around _deal_with_filename

        Takes a filename (either str or Path) and a kind and directory and
        checks that file exists and returns basename/filename/path in correct
        format for database

        :param params: ParamDict, the parameter dictionary of constants
        :param name: str, the name of the database used in
        :param kind: str, either 'raw', 'red', 'tmp', 'calib', 'tellu', 'asset'
                 this determines the path of the file i.e.
                 path/directory/filename (unless filename is an absolute
                 path) - note in this case directory should still be
                 filled correctly (for database)
        :param directory: str, the sub-directory name (under the raw/reduced/
                          tmp directory)
        :param filename: str or Path, the filename to add (can be absolute file
                         or basename, but must exist on disk)
        :param fullpath: str or None, if set overrides all other path getting
                         and is used for return
        :param force_dir: str or None, if set overrides our "kind" path
        :param func: str, the function name where this func was called
                     (for error logging)
        :return: if directory and filename are None returns just the path
                 (based on kind, else returns a tuple, 1. the filename (Path),
                 2. the basename and the path
        """
        return _deal_with_filename(self.params, self.name, kind, directory,
                                   filename, fullpath, force_dir, func)

    def _update_params(self, **kwargs) -> bool:
        """
        Update the parameters for update_entries (so we don't update twice)

        :param kwargs: list of arguments for update_entries

        :return: bool, True if we should update, False otherwise
        """
        # assume we want to update
        update = True
        # loop around entries
        for entry in self.update_entries_params:
            # if we don't want to update break
            if not update:
                break
            # set condition whether this entry matches kwargs
            match_entry = True
            # loop around entry
            for key in entry:
                # only update if key is in kwargs
                if key in kwargs:
                    # only update if key matches entry
                    if kwargs[key] == entry[key]:
                        match_entry &= True
                    else:
                        match_entry &= False
            # if we have found a match we do not want to update
            if match_entry:
                update = False
        # now add this setup for next time
        if update:
            self.update_entries_params.append(kwargs)
        # return whether to update or not
        return update


def _deal_with_filename(params: ParamDict, name: str, kind: str,
                        directory: Union[str, None] = None,
                        filename: Union[str, None] = None,
                        fullpath: Union[str, None] = None,
                        force_dir: Union[str, None] = None,
                        func: Union[str, None] = None
                        ) -> Union[str, Tuple[Path, str, str]]:
    """
    Takes a filename (either str or Path) and a kind and directory and
    checks that file exists and returns basename/filename/path in correct
    format for database

    :param params: ParamDict, the parameter dictionary of constants
    :param name: str, the name of the database used in
    :param kind: str, either 'raw', 'red', 'tmp', 'calib', 'tellu', 'asset'
             this determines the path of the file i.e.
             path/directory/filename (unless filename is an absolute
             path) - note in this case directory should still be
             filled correctly (for database)
    :param directory: str, the sub-directory name (under the raw/reduced/
                      tmp directory)
    :param filename: str or Path, the filename to add (can be absolute file
                     or basename, but must exist on disk)
    :param fullpath: str or None, if set overrides all other path getting and
                     is used for return
    :param force_dir: str or None, if set overrides our "kind" path
    :param func: str, the function name where this func was called (for error
                 logging)
    :return: if directory and filename are None returns just the path (based on
             kind, else returns a tuple, 1. the filename (Path),
             2. the basename and the path
    """
    # ------------------------------------------------------------------
    # deal with function name
    if func is None:
        func_name = display_func(params, '_deal_with_filename', __NAME__)
    else:
        func_name = str(func)
    # ------------------------------------------------------------------
    # deal with kind
    if force_dir is not None:
        path = drs_file.get_dir(params, kind, force_dir,
                                kind='database (forced)')
    else:
        path = drs_file.get_dir(params, kind, None, kind='database')
    # deal with having full path
    if fullpath is not None:
        if isinstance(fullpath, str):
            fullpath = Path(fullpath)
        # return forced paths (from path input)
        return fullpath, fullpath.name, path

    # deal with no directory and/or no filename (just want the path)
    if directory is None or filename is None:
        return path
    # ------------------------------------------------------------------
    # make filename a Path
    if isinstance(filename, str):
        filename = Path(filename)

    # get absolute path for file if not given
    if isinstance(filename, Path):
        if filename.exists():
            filename = filename.absolute()
        elif Path(path).joinpath(directory, filename).exists():
            filename = Path(path).joinpath(directory, filename)
            filename = filename.absolute()
        else:
            eargs = [name, filename, func_name]
            emsg = TextEntry('00-002-00023', args=eargs)
            WLOG(params, 'error', emsg)
            raise DrsCodedException('00-002-00023', targs=eargs,
                                    func_name=func_name)
    # get basename
    basename = str(filename.name)

    # return the filename as Path object (absolute), basename and path
    return filename, basename, path


def _get_files(path: Union[Path, str], kind: str,
               incdirs: Union[List[Union[str, Path]], None] = None,
               excdirs: Union[List[Union[str, Path]], None] = None,
               incfiles: Union[List[Union[str, Path]], None] = None,
               excfiles: Union[List[Union[str, Path]], None] = None,
               suffix: str = '') -> List[Path]:
    """
    Get files in 'path'. If kind in ['raw' 'tmp' 'red'] then look through
    subdirectories including 'incdirs' directories and excluding 'excdirs'
    directories

    :param path: Path or str, the path to the directory to find files for
    :param kind: str, the kind of files to kind (raw/tmp/red/calib/tellu etc)
    :param incdirs: list of strings or None, if set list the only directories
                    to include in the file list
    :param excdirs: list of strings or None, if set list any directories the
                    file list should exclude
    :param incfiles: list of files to include - if set only these files should
                     be included in the returned file list
    :param excfiles: list of files to exclude - if set none of these files
                     should be included in the returned file list
    :param suffix: str, the suffix which all files returns must have
                   (i.e. the extension)

    :return: list of paths, the file list (absolute file list) as Path instances
    """
    # fix path as string
    if isinstance(path, str):
        path = Path(path)
    # only use sub-directories for the following kinds
    if kind in ['raw', 'tmp', 'red']:
        # ---------------------------------------------------------------------
        # get directory path
        raw_subdirs = path.glob('*')
        # loop around directories
        subdirs = []
        for subdir in raw_subdirs:
            # skip non-directories
            if not subdir.is_dir():
                continue
            # skip directories not in included directories
            if incdirs is not None:
                if subdir not in incdirs:
                    continue
            # skip directories in excluded directories
            if excdirs is not None:
                if subdir in excdirs:
                    continue
            # if we have reached here then append subdirs
            subdirs.append(subdir)
    # else we do not use subdirs
    else:
        subdirs = None
    # -------------------------------------------------------------------------
    # deal with no subdirs
    if subdirs is None:
        # get all files in path
        allfiles = list(path.glob('*{0}'.format(suffix)))
    # -------------------------------------------------------------------------
    # else we have subdirs
    else:
        allfiles = []
        # loop around subdirs
        for subdir in subdirs:
            # append to filenames
            allfiles += list(subdir.glob('*{0}'.format(suffix)))
    # -------------------------------------------------------------------------
    # store valid files
    valid_files = []
    # filter files
    for filename in allfiles:
        # do not include directories
        if not filename.is_file():
            continue
        # include files
        if incfiles is not None and len(incfiles) > 0:
            if str(filename) not in incfiles:
                continue
        # exclude files
        if excfiles is not None:
            if str(filename) in excfiles:
                continue
        # add file to valid file list
        valid_files.append(filename.absolute())
    # return valid files
    return valid_files


# =============================================================================
# Define other databases
# =============================================================================
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
        self.set_path(kind='LOG', check=check)

    # TODO: finish this
    def add_entries(self, recipe: Union[str, None] = None,
                    rkind: Union[str, None] = None,
                    pid: Union[str, None] = None,
                    htime: Union[str, None] = None,
                    unixtime: Union[float, None] = None,
                    group: Union[str, None] = None,
                    level: Union[int, None] = None,
                    sublevel: Union[int, None] = None,
                    levelcrit: Union[str, None] = None,
                    inpath: Union[str, None] = None,
                    outpath: Union[str, None] = None,
                    directory: Union[str, None] = None,
                    logfile: Union[str, None] = None,
                    plotdir: Union[str, None] = None,
                    runstring: Union[str, None] = None,
                    args: Union[str, None] = None,
                    kwargs: Union[str, None] = None,
                    skwargs: Union[str, None] = None,
                    started: Union[bool, None] = None,
                    passed_all_qc: Union[bool, None] = None,
                    qc_string: Union[str, None] = None,
                    qc_names: Union[str, None] = None,
                    qc_values: Union[str, None] = None,
                    qc_logic: Union[str, None] = None,
                    qc_pass: Union[bool, None] = None,
                    errors: Union[bool, None] = None,
                    ended: Union[bool, None] = None,
                    used: Union[int, None] = None):
        pass


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
        self.set_path(kind='OBJECT', check=check)


class LanguageDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, check: bool = True):
        """
        Constructor of the Object Database class

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
        # save class name
        self.classname = 'LanguageDatabaseManager'
        # set function
        _ = display_func(params, '__init__', __NAME__, self.classname)
        # construct super class
        DatabaseManager.__init__(self, params)
        # set name
        self.name = 'language'
        # set path
        self.set_path(kind='LANG', check=check)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
