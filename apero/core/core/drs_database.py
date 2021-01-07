#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-18 15:15

@author: cook

import rules

only from
- apero.base.*
- apero.lang.*
- apero.core.core.drs_misc
- apero.core.core.drs_text
- apero.core.core.drs_exceptions
- apero.core.math.*
- apero.io.drs_fits
"""
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
from typing import Any, Dict, List, Tuple, Type, Union
from tqdm import tqdm

from apero import lang
from apero.base import base
from apero.base import drs_db
from apero.core import constants
from apero.core.core import drs_misc
from apero.core.core import drs_exceptions
from apero.core.core import drs_text
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
textentry = lang.textentry
# define drs files
DrsFileTypes = Union[drs_file.DrsInputFile, drs_file.DrsFitsFile,
                     drs_file.DrsNpyFile]
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get list of obj name cols
OBJNAMECOLS = ['KW_OBJNAME']
# gaia col name
GAIA_COL_NAME = 'GAIADR2ID'


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
        self.instrument = base.IPARAMS['INSTRUMENT']
        # get pconst (for use throughout)
        self.pconst = constants.pload(self.instrument)
        # set name
        self.name = 'DatabaseManager'
        self.kind = 'None'
        self.dbtype = None
        # set parameters
        self.dbhost = None
        self.dbuser = None
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

        :param kind: str, the kind of datatable
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
        # deal with path for SQLITE3
        # ---------------------------------------------------------------------
        if self.dbtype == 'SQLITE3':
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
                emsg = textentry('00-002-00016', args=eargs)
                WLOG(self.params, 'error', emsg)
                return
            # check for directory
            if not dirname.exists() and check:
                # log error: Directory {0} does not exist (database = {1})
                eargs = [dirname, self.name, func_name]
                emsg = textentry('00-002-00017', args=eargs)
                WLOG(self.params, 'error', emsg)
                return
            # -----------------------------------------------------------------
            # add filename
            # -----------------------------------------------------------------
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
                emsg = textentry('00-002-00018', args=eargs)
                WLOG(self.params, 'error', emsg)
                return
            # set path
            self.path = abspath
        # ---------------------------------------------------------------------
        # deal with path for MySQL (only for printing)
        # ---------------------------------------------------------------------
        elif self.dbtype == 'MYSQL':
            self.path = '{0}@{1}'.format(self.dbuser, self.dbhost)
        else:
            emsg = 'Database type "{0}" invalid'
            WLOG(self.params, 'error', emsg.format(self.dbtype))

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
        # log that we are loading database
        margs = [self.name, self.path]
        WLOG(self.params, 'info', textentry('40-006-00005', args=margs))
        # load database
        self.database = drs_db.database_wrapper(self.kind, self.path)

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
        # get correct sub-dictionary
        if ddict['USE_MYSQL']:
            sdict = ddict['MYSQL']
            self.dbtype = 'MYSQL'
            self.dbhost = sdict['HOST']
            self.dbuser = sdict['USER']
        else:
            sdict = ddict['SQLITE3']
            self.dbtype = 'SQLITE3'
        # kind must be one of the following
        if kind not in ['CALIB', 'TELLU', 'INDEX', 'LOG', 'OBJECT', 'LANG']:
            raise ValueError('kind=={0} invalid'.format(kind))
        # set name/path/reset based on ddict
        self.dbname = sdict[kind]['NAME']
        self.dbpath = sdict[kind]['PATH']
        if drs_text.null_text(sdict[kind]['RESET'], ['None']):
            self.dbreset = None
        else:
            self.dbreset = sdict[kind]['RESET']


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
        self.kind = 'CALIB'
        # set path
        self.set_path(kind=self.kind, check=check)
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
                WLOG(self.params, 'info', textentry('40-001-00024', args=wargs))
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
        self.database.add_row(values, table=self.database.tname, commit=True)

    def get_calib_entry(self, columns: str, key: str,
                        fiber: Union[str, None] = None,
                        filetime: Union[Time, None] = None,
                        timemode: str = 'older',
                        nentries: Union[int, str] = '*'
                        ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the calibration database

        :param columns: str, pushed to SQL (i.e. list columns or '*' for all)
        :param key: str, KEY="key" condition
        :param fiber: str or None, if set FIBER="fiber"
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
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # condition for key
        sql['condition'] = 'KEYNAME = "{0}"'.format(key)
        # condition for used
        sql['condition'] += ' AND USED = 1'
        # condition for fiber
        if fiber is not None:
            sql['condition'] += ' AND FIBER = "{0}"'.format(fiber)
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
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
            # return filename
            if len(entries) == 1:
                if len(colnames) == 1:
                    return entries[0][0]
                else:
                    return entries[0]
            else:
                return None
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
                emsg = textentry('00-002-00021', args=eargs)
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
            keys = self.database.unique('KEYNAME', table=self.database.tname)
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
            WLOG(self.params, 'error', textentry('00-002-00015', args=eargs))
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

    def remove_entries(self, condition):
        # set function
        _ = display_func(self.params, 'remove_entries', __NAME__,
                         self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(table=self.database.tname,
                                  condition=condition)


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
        self.kind = 'TELLU'
        # set path
        self.set_path(kind=self.kind, check=check)
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
                WLOG(self.params, 'info', textentry('40-001-00024', args=wargs))
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
        self.database.add_row(values, table=self.database.tname, commit=True)

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
        :param key: str, KEY="key" condition
        :param fiber: str or None, if set FIBER="fiber"
        :param filetime: astropy.Time, if Not None the point in time to order
                         the files by
        :param timemode: str, the way in which to select which telluric to
                         use (either 'older' 'closest' or 'newer')
                         based on filetime as the "zero point" time
        :param nentries: int or str, the number of entries to return
                         only valid string is '*' for all entries
        :param objname: str or None, if set OBJECT="fiber"
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
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # condition for key
        sql['condition'] = 'KEYNAME = "{0}"'.format(key)
        # condition for used
        sql['condition'] += ' AND USED = 1'
        # condition for fiber
        if fiber is not None:
            sql['condition'] += ' AND FIBER = "{0}"'.format(fiber)
        # condition for objname
        if objname is not None:
            sql['condition'] += ' AND OBJECT = "{0}"'.format(objname)

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
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
            # return filename
            if len(entries) == 1:
                if len(colnames) == 1:
                    return entries[0][0]
                else:
                    return entries[0]
            else:
                return None

        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
                emsg = textentry('00-002-00021', args=eargs)
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
            keys = self.database.unique('KEYNAME', table=self.database.tname)
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
            WLOG(self.params, 'error', textentry('00-002-00015', args=eargs))
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

    def remove_entries(self, condition):
        # set function
        _ = display_func(self.params, 'remove_entries', __NAME__,
                         self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(table=self.database.tname,
                                  condition=condition)


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
        WLOG(params, 'error', textentry('00-008-00012', args=eargs))
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
            WLOG(params, 'error', textentry('00-002-00019', args=eargs))
            return False
    else:
        eargs = [drsfile.name, dbmname, func_name]
        WLOG(params, 'error', textentry('00-008-00012', args=eargs))
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
            WLOG(params, 'error', textentry('00-000-00002', args=eargs))
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
            WLOG(params, '', textentry('40-006-00004', args=margs))
        # copy file using shutil (should be thread safe)
        shutil.copyfile(inpath, outpath)
    except Exception as e:
        # log exception:
        eargs = [dbmname, inpath, outpath, type(e), e, func_name]
        WLOG(params, 'error', textentry('00-002-00014', args=eargs))


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
        WLOG(params, 'error', textentry('00-001-00027', args=eargs))
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
        WLOG(params, 'error', textentry('00-001-00039', args=eargs))


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
        self.kind = 'INDEX'
        # set path
        self.set_path(kind=self.kind, check=check)
        # store whether an update has been done
        self.update_entries_params = []

    def add_entry(self, directory: str, filename: Union[Path, str], kind: str,
                  runstring: Union[str, None] = None,
                  hkeys: Union[Dict[str, str], None] = None,
                  fullpath: Union[Path, str, None] = None,
                  used: Union[int, None] = None,
                  rawfix: Union[int, None] = None,
                  force_dir: Union[str, None] = None, commit: bool = True):
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
        :param runstring: str, the command line arg representation of this
                          indexs recipe run
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
        :param commit: bool, if True commitrs

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
        if rawfix is None:
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
                # noinspection PyBroadException
                try:
                    # get data type
                    dtype = rtypes[h_it]
                    # try to case and append
                    hvalues.append(dtype(hkeys[hkey]))
                except Exception as _:
                    wargs = [self.name, hkey, hkeys[hkey],
                             rtypes[h_it], func_name]
                    wmsg = textentry('10-002-00003', args=wargs)
                    WLOG(self.params, 'warning', wmsg)
                    hvalues.append('NULL')
            else:
                hvalues.append('NULL')
        # ------------------------------------------------------------------
        # make absolute path
        path = Path(path).joinpath(directory, filename)
        # ------------------------------------------------------------------
        # get current list of paths for
        currentpath = self.get_entries('ABSPATH', directory=directory,
                                       filename=basename, nentries=1)
        # ------------------------------------------------------------------
        # deal with updating entry
        if currentpath is not None and str(currentpath) == str(path):
            # add new entry to database
            values = [str(path), str(directory), str(basename), str(kind),
                      float(last_modified), str(runstring)]
            values += hvalues + [used, rawfix]
            # set up condition
            condition = 'FILENAME = "{0}"'.format(filename)
            condition += ' AND DIRNAME = "{0}"'.format(directory)
            condition += ' AND ABSPATH = "{0}"'.format(path)
            # update row in database
            self.database.set('*', values=values, condition=condition,
                              table=self.database.tname,
                              commit=commit)
        else:
            # add new entry to database
            values = [str(path), str(directory), str(basename), str(kind),
                      float(last_modified), str(runstring)]
            values += hvalues + [used, rawfix]
            self.database.add_row(values, table=self.database.tname,
                                  commit=commit)

    def remove_entries(self, condition):
        # set function
        _ = display_func(self.params, 'remove_entries', __NAME__,
                         self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(table=self.database.tname,
                                  condition=condition)

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
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # ------------------------------------------------------------------
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # sort by last modified
        sql['sort_by'] = 'LAST_MODIFIED'
        # condition for used
        sql['condition'] = 'USED = 1'
        # ------------------------------------------------------------------
        if condition is not None:
            sql['condition'] += ' AND {0}'.format(condition)
        # ------------------------------------------------------------------
        # deal with kind set
        if kind is not None:
            sql['condition'] += ' AND KIND = "{0}"'.format(kind)
        # ------------------------------------------------------------------
        # deal with directory set
        if directory is not None:
            sql['condition'] += ' AND DIRNAME = "{0}"'.format(directory)
        # ------------------------------------------------------------------
        # deal with filename set
        if filename is not None:
            sql['condition'] += ' AND FILENAME = "{0}"'.format(filename)
        # ------------------------------------------------------------------
        # get allowed header keys
        rkeys, rtypes = self.pconst.INDEX_HEADER_KEYS()
        # deal with filter by header keys
        if hkeys is not None and isinstance(hkeys, dict):

            for h_it, hkey in enumerate(rkeys):
                if hkey in hkeys:
                    # noinspection PyBroadException
                    try:
                        # get data type
                        dtype = rtypes[h_it]
                        # try to case and add to condition
                        condition = _hkey_condition(hkey, dtype, hkeys[hkey])
                        sql['condition'] += condition
                    except Exception as _:
                        wargs = [self.name, hkey, hkeys[hkey],
                                 rtypes[h_it], func_name]
                        wmsg = textentry('10-002-00003', args=wargs)
                        WLOG(self.params, 'warning', wmsg)
        # ------------------------------------------------------------------
        # add the number of entries to get
        if isinstance(nentries, int):
            sql['max_rows'] = nentries
        # if we have one entry just get the tuple back
        if nentries == 1:
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
            # return filename
            if len(entries) == 1:
                if len(colnames) == 1:
                    return entries[0][0]
                else:
                    return entries[0]
            else:
                return None
        # ------------------------------------------------------------------
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
        :param force_update: bool, if True forces the update even if database
                             thinks it is up-to-date

        :return: None - updates the index database
        """
        # set function
        _ = display_func(self.params, 'update_entries', __NAME__,
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
        exclude_files = self.get_entries('ABSPATH', kind=kind)
        # ---------------------------------------------------------------------
        # locate all files within path
        reqfiles = _get_files(path, kind, include_directories,
                              exclude_directories, include_files,
                              exclude_files, suffix)
        # ---------------------------------------------------------------------
        # get a list of keys
        rkeys, rtypes = self.pconst.INDEX_HEADER_KEYS()
        ikeys, itypes = self.pconst.INDEX_DB_COLUMNS()
        # ---------------------------------------------------------------------
        # deal with database having wrong columns (if we have added / remove a
        #  column and are updating because of this)
        columns = self.database.colnames('*', self.database.tname)
        # check if columns and rkeys agree
        if len(columns) != len(ikeys):
            # prompt user and warn
            wmsg = 'Index database has wrong number of columns'
            WLOG(self.params, 'warning', wmsg)
            userinput = input('Reset database [Y]es or [N]o?\t')
            # if yes delete table and recreate
            if 'Y' in userinput.upper():
                # remove table
                self.database.delete_table(self.database.tname)
                # add new empty table
                self.database.add_table(self.database.tname, ikeys, itypes)
                # reload database
                self.load_db()
                # update all entries for raw index entries
                WLOG(self.params, 'info', 'Rebuilding raw index entries')
                self.update_entries('raw', force_update=True)
                # update all entries for tmp index entries
                WLOG(self.params, 'info', 'Rebuilding tmp index entries')
                self.update_entries('tmp', force_update=True)
                # update all entries for reduced index entries
                WLOG(self.params, 'info', 'Rebuilding reduced index entries')
                self.update_entries('red', force_update=True)
                return
        # ---------------------------------------------------------------------
        # deal with no files
        if len(reqfiles) == 0:
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
            self.add_entry(directory, basename, kind, hkeys=hkeys, commit=False)
        # finally commit all entries
        self.database.commit()

    def update_header_fix(self, recipe):
        # set function name
        _ = display_func(self.params, 'update_objname', __NAME__,
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
        columns = ['ABSPATH', 'RAWFIX'] + rkeys
        # get data for columns
        table = self.get_entries(', '.join(columns), kind='raw')
        # if all rows have rawfix == 1 then just return now
        if np.sum(table['RAWFIX']) == len(table):
            return
        # need to loop around each row
        for row in tqdm(range(len(table))):
            # do not re-fix is rawfix is 1
            if table['RAWFIX'].iloc[row] == 1:
               continue
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
            condition = 'ABSPATH="{0}"'.format(table['ABSPATH'].iloc[row])
            # get values
            values = [table['ABSPATH'].iloc[row], 1]
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
            self.database.set(columns, values=values, condition=condition,
                              table=self.database.tname)

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
            emsg = textentry('00-002-00023', args=eargs)
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


def _hkey_condition(name, datatype, hkey):
    """
    Deal with generating a condition from a hkey (list or str)
    """
    # must deal with hkeys as lists
    if isinstance(hkey, list):
        # store sub-conditions
        subconditions = []
        # loop around elements in hkey
        for sub_hkey in hkey:
            # cast value into data type
            value = datatype(sub_hkey)
            # add to sub condition
            subconditions.append('{0}="{1}"'.format(name, value))
        # make full condition based on sub conditions
        condition = 'AND ({0})'.format(' OR '.join(subconditions))
        # return condition
        return condition
    else:
        # cast value into data type
        value = datatype(hkey)
        # return condition
        return ' AND {0}="{1}"'.format(name, value)


# =============================================================================
# Define Log database
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
        self.kind = 'LOG'
        # set path
        self.set_path(kind=self.kind, check=check)

    def remove_pids(self, pid: str):
        """
        Remove rows with this pid
        :param pid:
        :return:
        """
        # set up condition
        condition = 'PID="{0}"'.format(pid)
        # delete rows that match this criteria
        self.database.delete_rows(table=self.database.tname,
                                  condition=condition)

    def add_entries(self, recipe: Union[str, None] = None,
                    sname: Union[str, None] = None,
                    rkind: Union[str, None] = None,
                    rtype: Union[str, None] = None,
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
                    started: Union[bool, int, None] = None,
                    passed_all_qc: Union[bool, int, None] = None,
                    qc_string: Union[str, None] = None,
                    qc_names: Union[str, None] = None,
                    qc_values: Union[str, None] = None,
                    qc_logic: Union[str, None] = None,
                    qc_pass: Union[str, None] = None,
                    errors: Union[str, None] = None,
                    ended: Union[bool, int, None] = None,
                    used: Union[int, None] = None,
                    commit: bool = True):
        """
        Add a log entry to database

        :param recipe: str, the recipe name
        :param rkind: str, the recipe kind ('recipe', 'tool', 'processing')
        :param pid: str, the unique process identifier for this run
        :param htime: str, the human time (related to pid creation)
        :param unixtime: float, the unix time (related to pid creation)
        :param group: str, the group name (used for processing)
        :param level: int, which level this entry is related to
        :param sublevel: int, which element in the level this entry relates to
        :param levelcrit: str, the criteria describing this entries (i.e.
                          level and sublevel)
        :param inpath: str, the input directory used for this recipe run
        :param outpath: str, the output directory used for this recipe run
        :param directory: str, the directory that set for this recipe run
        :param logfile: str, where the log file is saved for this recipe run
        :param plotdir: str, where the plot files are saved for this recipe run
        :param runstring: str, the command that can be used to re-run this
                          recipe run
        :param args: str, the positional arguments (named) used for this
                     recipe run - divided by ||
        :param kwargs: str, the optional arguments (named) used for this
                       recipe run - divided by ||
        :param skwargs: str, the special arguments (named) used for this
                        recipe run - divided by ||
        :param started: bool or int, whether a recipe run was started (should
                        always be 1 or True)
        :param passed_all_qc: bool or int, whether all qc passed on this run
        :param qc_string: str, qc parameter string (in full) for each qc
                          - divided by ||
        :param qc_names: str, the qc names for each qc - divided by ||
        :param qc_values: str, the qc value (calculated) for each qc
                          - divided by ||
        :param qc_logic: str, the qc logic (i.e.  {name} < {limit}) for each
                         qc - divided by ||
        :param qc_pass: str, whether each qc passed or failed, 1 for pass 0 for
                        fail - divided by ||
        :param errors: str, errors found and passed to this entry - divided by
                       ||
        :param ended: bool or int, whether a recipe run ended - 1 for ended
                      0 if did not end (default)
        :param used: int, if entry should be used - always 1 for use internally
        :param commit: bool, if True commit, if False need to commit later
                       (i.e. commit a batch of executions)

        :return: None - updates database
        """

        # need to clean error to put into database
        clean_error = _clean_error(errors)
        # get correct order
        keys = [recipe, sname, rkind, rtype, pid, htime, unixtime, group,
                level, sublevel, levelcrit, inpath, outpath, directory,
                logfile, plotdir, runstring, args, kwargs, skwargs, started,
                passed_all_qc, qc_string, qc_names, qc_values, qc_logic,
                qc_pass, clean_error, ended, used]
        # get column names and column datatypes
        colnames, coltypes = self.pconst.LOG_DB_COLUMNS()
        # storage of values
        values = []
        # loop around values
        for it in range(len(keys)):
            # deal with unset key
            if drs_text.null_text(keys[it], ['None', '']):
                values.append('None')
            else:
                # noinspection PyBroadException
                try:
                    # get data type
                    dtype = coltypes[it]
                    # append forcing data type
                    values.append(dtype(keys[it]))
                except Exception as _:
                    values.append('None')
        # add row to database
        self.database.add_row(values, table=self.database.tname, commit=commit)

    def get_entries(self, columns: str = '*',
                    wdirs: Union[List[str], None] = None,
                    bdirs: Union[List[str], None] = None,
                    nentries: Union[int, None] = None,
                    condition: Union[str, None] = None,
                    ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the index database (can set columns to return, or
        filter by specific columns)

        :param columns: str, the columns to return ('*' for all)
        :param wdirs: list of strings - if set a list of allowed directories
        :param bdirs: list of strings - if set a list of disallowed directories
        :param nentries: int or None, if set limits the number of entries to get
                         back - sorted newest to oldest
        :param condition: str or None, if set the SQL query to add

        :return: the entries of columns, if nentries = 1 returns either that
                 entry (as a tuple) or None, if len(columns) = 1, returns
                 a np.ndarray, else returns a pandas table
        """
        # set function
        _ = display_func(self.params, 'get_entries', __NAME__, self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # ------------------------------------------------------------------
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # sort by last modified
        sql['sort_by'] = 'UNIXTIME'
        # condition for used
        sql['condition'] = 'USED = 1'
        # ------------------------------------------------------------------
        if condition is not None:
            sql['condition'] += ' AND {0}'.format(condition)
        # ------------------------------------------------------------------
        # deal with whitelist directory set
        if wdirs is not None:
            # define a subcondition
            subconditions = []
            # loop around white listed nights and only keep these
            for directory in wdirs:
                # add subcondition
                subcondition = 'DIRNAME="{0}"'.format(directory)
                subconditions.append(subcondition)
            # add to conditions
            condition += ' AND ({0})'.format(' OR '.join(subconditions))
        # ------------------------------------------------------------------
        # deal with blacklist directory set
        if bdirs is not None:
            for directory in bdirs:
                # add to condition
                condition += ' AND (DIRNAME!="{0}")'.format(directory)
        # ------------------------------------------------------------------
        # add the number of entries to get
        if isinstance(nentries, int):
            sql['max_rows'] = nentries
        # if we have one entry just get the tuple back
        if nentries == 1:
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
            # return filename
            if len(entries) == 1:
                if len(colnames) == 1:
                    return entries[0][0]
                else:
                    return entries[0]
            else:
                return None
        # ------------------------------------------------------------------
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
            # return pandas table
            return entries

    def remove_entries(self, condition):
        # set function
        _ = display_func(self.params, 'remove_entries', __NAME__,
                         self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(table=self.database.tname,
                                  condition=condition)


def _clean_error(errors: Union[str, None]) -> Union[str, None]:
    """
    Clean the error string so it can go in the database

    :param errors: str, the error string to clean

    :return: str, cleaned error string
    """
    if errors is None:
        return errors
    # else we push everything else to a string
    if not isinstance(errors, str):
        errors = str(errors)
    # define some bad characters
    bad_chars = ['\n', '\t', r'\\', r'>', r'<', '"', "'"]
    # loop around bad characters and remove them
    for bad_char in bad_chars:
        errors = errors.replace(bad_char, ' ')
    # remove double spaces
    while '  ' in errors:
        errors = errors.replace('  ', ' ')
    # return the clean string
    return errors


# =============================================================================
# Define other databases
# =============================================================================
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
        self.kind = 'OBJECT'
        # set path
        self.set_path(kind=self.kind, check=check)

    def get_entries(self, columns: str = '*',
                    nentries: Union[int, None] = None,
                    condition: Union[str, None] = None,
                    ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the object database (can set columns to return, or
        filter by specific columns)

        :param columns: str, the columns to return ('*' for all)
        :param nentries: int or None, if set limits the number of entries to get
                         back - sorted newest to oldest
        :param condition: str or None, if set the SQL query to add

        :return: the entries of columns, if nentries = 1 returns either that
                 entry (as a tuple) or None, if len(columns) = 1, returns
                 a np.ndarray, else returns a pandas table
        """
        # set function
        _ = display_func(self.params, 'get_entries', __NAME__, self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # ------------------------------------------------------------------
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # sort by last modified
        sql['sort_by'] = GAIA_COL_NAME
        # condition for used
        sql['condition'] = 'USED = 1'
        # ------------------------------------------------------------------
        if condition is not None:
            sql['condition'] += ' AND {0}'.format(condition)
        # ------------------------------------------------------------------
        # add the number of entries to get
        if isinstance(nentries, int):
            sql['max_rows'] = nentries
        # if we have one entry just get the tuple back
        if nentries == 1:
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
            # return filename
            if len(entries) == 1:
                if len(colnames) == 1:
                    return entries[0][0]
                else:
                    return entries[0]
            else:
                return None
        # ------------------------------------------------------------------
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
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
            entries = self.database.get(columns, table=self.database.tname,
                                        **sql)
            # return pandas table
            return entries

    def add_entry(self, objname: str, objname_s: str,
                  gaia_id: str, gaia_id_s: str,
                  ra: float, ra_s: str, dec: float, dec_s: str,
                  pmra: Union[float, None] = None, pmra_s: str = 'None',
                  pmde: Union[float, None] = None, pmde_s: str = 'None',
                  plx: Union[float, None] = None, plx_s: str = 'None',
                  rv: Union[float, None] = None, rv_s: str = 'None',
                  gmag: Union[float, None] = None, gmag_s: str = 'None',
                  bpmag: Union[float, None] = None, bpmag_s: str = 'None',
                  rpmag: Union[float, None] = None, rpmag_s: str = 'None',
                  epoch: Union[float, None] = None, epoch_s: str = 'None',
                  teff: Union[float, None] = None, teff_s: str = 'None',
                  aliases: Union[List[str], str, None] = None,
                  aliases_s: str = 'None', used: int = 1, commit: bool = True):
        """
        Add an object to the object database

        :param objname: str, the primary object name (SIMBAD name)
        :param objname_s: str, source of objname
        :param gaia_id: str, the Gaia ID (from Gaia DR2)
        :param gaia_id_s: str, source of Gaia ID
        :param ra: float, the Gaia right ascension of an object (in degrees)
        :param ra_s: str, source of ra
        :param dec: float, the Gaia declination of an object (in degrees)
        :param dec_s: str, source of dec
        :param pmra: float, the Gaia proper motion in RA (in mas/yr)
        :param pmra_s: str, source of pmra
        :param pmde: float, the Gaia proper motion in Dec (in mas/yr)
        :param pmde_s: str, source of pmde
        :param plx: float, the Gaia parallax in mas
        :param plx_s: str, source of plx
        :param rv: float, the RV in km/s
        :param rv_s: str, source of rv
        :param gmag: float, the Gaia G magnitude
        :param gmag_s: str, source of gmag
        :param bpmag: float, the Gaia BP magnitude
        :param bpmag_s: str, the source of bpmag
        :param rpmag: float, the Gaia RP magniutde
        :param rpmag_s: str, the source of rpmag
        :param epoch: float, the Gaia epoch (2015.5)
        :param epoch_s: str, the source of epoch
        :param teff: float, the temperature in K
        :param teff_s: str, the source of Teff
        :param aliases: list of strings or string, any other names this
                        target can have
        :param aliases_s: str, the source of aliases
        :param used: int, whether to use entries or not (normally ste manually)
        :param commit: bool, if True commit, if False need to commit later
                       (i.e. commit a batch of executions)

        :return: None - updates database
        """
        # deal with values
        values = [objname, objname_s, gaia_id, gaia_id_s, ra, ra_s, dec, dec_s,
                  pmra, pmra_s, pmde, pmde_s, plx, plx_s, rv, rv_s, gmag,
                  gmag_s, bpmag, bpmag_s, rpmag, rpmag_s, epoch, epoch_s,
                  teff, teff_s]
        # deal with null values
        for it, value in enumerate(values):
            if value is None:
                values[it] = 'None'
        # deal with aliases
        if isinstance(aliases, str):
            values.append(aliases)
            values.append(aliases_s)
        elif isinstance(aliases, list):
            values.append('|'.join(aliases))
            values.append(aliases_s)
        else:
            values.append('None')
            values.append(aliases_s)
        # add used
        values.append(used)
        # add row
        self.set_row(gaia_id, objname, '*', values, commit)

    def set_row(self, gaia_id: str, objname: str,
                columns: Union[str, List[str]], values: list,
                commit: bool = True):
        # need to see if we already have gaia id
        condition1 = '{0}="{1}"'.format(GAIA_COL_NAME, gaia_id)
        gaiaids = self.database.unique(GAIA_COL_NAME, condition=condition1,
                                       table=self.database.tname)
        condition2 = '{0}="{1}"'.format('OBJNAME', objname)
        objnames = self.database.unique('OBJNAME', condition=condition2,
                                        table=self.database.tname)
        # ------------------------------------------------------------------
        # deal with updating entry
        if (gaiaids is not None) and (len(gaiaids) > 0):
            # update row in database
            self.database.set(columns, values=values, condition=condition1,
                              table=self.database.tname, commit=commit)
        # else we update based on object name
        elif (objnames is not None) and (len(objnames) > 0):
            # update row in database
            self.database.set(columns, values=values, condition=condition2,
                              table=self.database.tname, commit=commit)
        # else add row to database (as new row)
        else:
            self.database.add_row(values, table=self.database.tname,
                                  columns=columns, commit=commit)

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
