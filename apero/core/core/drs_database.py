#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO database management functionality

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
import os
import shutil
import time
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np
import pandas as pd
import requests
from astropy.io.ascii.core import InconsistentTableError
from astropy.table import Table
from pandasql import sqldf

from apero.base import base
from apero.base import drs_db
from apero.base.drs_db import DatabaseManager
from apero.core import constants
from apero.core import lang
from apero.core.base import drs_exceptions
from apero.core.base import drs_text
from apero.core.base import drs_misc
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.io import drs_fits
from apero.io import drs_path

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
# get tqdm from base
tqdm = base.TQDM
# get ParamDict
ParamDict = constants.ParamDict
# get execption
DrsCodedException = drs_exceptions.DrsCodedException
# get display func
display_func = drs_log.display_func
# get WLOG
WLOG = drs_log.wlog
TLOG = drs_log.Printer
# get drs header
DrsHeader = drs_file.Header
FitsHeader = drs_file.FitsHeader
# get file types
DrsInputFile = drs_file.DrsInputFile
DrsFitsFile = drs_file.DrsFitsFile
# Get the text types
textentry = lang.textentry
# define drs files
DrsFileTypes = Union[drs_file.DrsInputFile, drs_file.DrsFitsFile,
                     drs_file.DrsNpyFile]
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get list of obj name cols
OBJNAMECOLS = ['KW_OBJNAME']
# complex return
DealFilenameReturn = Union[Tuple[str, str], Tuple[Path, str, str, str]]
# globals to save time on multiple reads
OBS_PATHS = dict()
FILEDBS = dict()
OBS_NAMES = dict()
# define reserved object names
RESERVED_OBJ_NAMES = ['CALIB', 'SKY', 'TEST']
# cache for google sheet
GOOGLE_TABLES = dict()
# define standard google base url
GOOGLE_BASE_URL = ('https://docs.google.com/spreadsheets/d/{}/gviz/'
                   'tq?tqx=out:csv&gid={}')


# =============================================================================
# Define classes
# =============================================================================


# =============================================================================
# Object database
# =============================================================================
class AstrometricDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, pconst: Any = None,
                 dparams: Optional[dict] = None):
        """
        Constructor of the Astrometric Database class

        :param params: ParamDict, parameter dictionary of constants
        :param dparams: dict, optional, the database yaml dictionary
                        (parse if preloaded, otherwise reloads)

        :return: None
        """
        # save class name
        self.classname = 'AstrometricDatabase'
        # deal with no pconst
        if pconst is None:
            pconst = constants.pload()
        # construct super class
        DatabaseManager.__init__(self, params, pconst)
        # set name
        self.name = 'astrom'
        self.kind = 'astrom'
        self.columns = self.pconst.ASTROMETRIC_DB_COLUMNS()
        self.colnames = self.columns.names
        # set path
        self.database_settings(kind=self.kind, dparams=dparams)

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
        # _ = display_func('get_entries', __NAME__, self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
        # ------------------------------------------------------------------
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
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
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
            # return pandas table
            return entries

    def add_entry(self, objname: str, objname_s: str,
                  ra: float, ra_s: str, dec: float, dec_s: str,
                  pmra: Union[float, None] = None, pmra_s: str = 'None',
                  pmde: Union[float, None] = None, pmde_s: str = 'None',
                  plx: Union[float, None] = None, plx_s: str = 'None',
                  rv: Union[float, None] = None, rv_s: str = 'None',
                  epoch: Union[float, None] = None,
                  teff: Union[float, None] = None, teff_s: str = 'None',
                  sp_type: Union[str, None] = None, sp_type_s: str = 'None',
                  aliases: Union[List[str], str, None] = None,
                  used: int = 1, notes: str = ''):
        """
        Add an object to the object database

        :param objname: str, the primary object name (SIMBAD name)
        :param objname_s: str, source of objname
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
        :param epoch: float, the Gaia epoch (2015.5)
        :param teff: float, the temperature in K
        :param teff_s: str, the source of Teff
        :param sp_type: str, the spectral type
        :param sp_type_s: str, the source of sp_type
        :param aliases: list of strings or string, any other names this
                        target can have
        :param used: int, whether to use entries or not (normally ste manually)
        :param notes: str, any notes/comments about this object

        :return: None - updates database
        """
        # deal with aliases
        if isinstance(aliases, str):
            daliases = aliases
        elif isinstance(aliases, list):
            daliases = '|'.join(aliases)
        else:
            daliases = 'None'
        # create insert dict
        insert_dict = dict()
        insert_dict['OBJNAME'] = drs_db.deal_with_null(objname)
        insert_dict['ORIGINAL_NAME'] = drs_db.deal_with_null(objname_s)
        insert_dict['ALIASES'] = daliases
        insert_dict['RA_DEG'] = ra
        insert_dict['RA_SOURCE'] = ra_s
        insert_dict['DEC_DEG'] = dec
        insert_dict['DEC_SOURCE'] = dec_s
        insert_dict['EPOCH'] = epoch
        insert_dict['PMRA'] = pmra
        insert_dict['PMRA_SOURCE'] = pmra_s
        insert_dict['PMDE'] = pmde
        insert_dict['PMDE_SOURCE'] = pmde_s
        insert_dict['PLX'] = plx
        insert_dict['PLX_SOURCE'] = plx_s
        insert_dict['RV'] = rv
        insert_dict['RV_SOURCE'] = rv_s
        insert_dict['TEFF'] = teff
        insert_dict['TEFF_SOURCE'] = teff_s
        insert_dict['SP_TYPE'] = drs_db.deal_with_null(sp_type)
        insert_dict['SP_TYPE_SOURCE'] = drs_db.deal_with_null(sp_type_s)
        insert_dict['NOTES'] = drs_db.deal_with_null(notes)
        insert_dict['USED'] = used
        insert_dict['DATE_ADDED'] = Time.now().iso
        # ------------------------------------------------------------------
        # check that we are adding the correct columns (i.e. all columns
        #   are in database)
        self.check_columns(insert_dict)
        # try to add a new row
        self.database.add_row(insert_dict=insert_dict)

    def count(self, condition: Union[str, None] = None) -> int:
        """
        Count the number of rows in the object database
        """
        return self.database.count(condition=condition)

    def find_objnames(self, pconst: constants.PseudoConstants,
                      objnames: Union[List[str], np.ndarray],
                      allow_empty: bool,
                      listname: Optional[str] = None,
                      ) -> Tuple[List[str], List[str]]:
        """
        Wrapper around find_objname

        :param pconst: psuedo constants - used to clean the object name
        :param objnames: list of str, a list of object names to clean and fimd
        :param allow_empty: bool, if True allows not objects to be found
                            if False will raise an error
        :param listname: str, the name of the objnames list (for error messages)
        :return:
        """
        func_name = display_func('find_objnames', __NAME__, self.classname)
        # deal with objnames not being a list or a
        if not isinstance(objnames, (list, np.ndarray)):
            objnames = [objnames]
        # loop around objects
        out_objnames = []
        missing_objnames = []
        for objname in objnames:
            out_objname, found = self.find_objname(pconst, objname)
            if found:
                out_objnames.append(out_objname)
            else:
                missing_objnames.append(objname)
        # ---------------------------------------------------------------------
        # deal with no entries and not expecting an empty list return
        if len(out_objnames) == 0 and not allow_empty:
            # deal with name of object list
            if listname is None:
                listname = func_name
            else:
                listname = f'"{listname}" ({func_name})'
            # log error: No objects found in astrometric database.
            emsg = 'No objects found in astrometric database.'
            emsg += '\n\tPlease add objects to the astrometric database.'
            emsg += '\n\tListname={0}'
            emsg += '\n\tObjnames: "{1}"'
            eargs = [listname, ', '.join(objnames)]
            # report the error
            WLOG(self.params, 'error', emsg.format(*eargs))
            return [], objnames
        # ---------------------------------------------------------------------
        # return the filled out list
        return out_objnames, missing_objnames

    def find_objname(self, pconst: constants.PseudoConstants,
                     objname: str, return_flag: bool = False
                     ) -> Tuple[str, Union[bool, int]]:
        """
        Find and clean the correct object name (as used by apero) this is
        either:
        1. from the OBJNAME column of the database directly
        2. from the ALIAS column of the database (if not found in OBJNAME)
        3. the cleaned input name (not found in the database)

        :param pconst: psuedo constants - used to clean the object name
        :param objname: str, the object name to clean and find
        :param return_flag: bool, if True returns a flag (0, 1 or 2) showing
                             where the object was found
                             else returns a True/False )found or not found)

        :return: Tuple, 1. str, the "correct" object name to use for the DRS,
                 2. a flag on where object was found 0=not found, 1=found in
                    OBJNAME, 2=found in ALIASES
        """
        # global to be updated so we don't do this more than once for the
        #   same objname
        global OBS_NAMES
        # ---------------------------------------------------------------------
        # check objname in global
        if objname in OBS_NAMES:
            return OBS_NAMES[objname]
        # ---------------------------------------------------------------------
        # deal with calib / sky / test
        if objname in RESERVED_OBJ_NAMES:
            return objname, True
        # ---------------------------------------------------------------------
        # assume we have not found our object name
        found = 0
        # clean the input objname
        cobjname = pconst.DRS_OBJ_NAME(objname)
        # deal with a null object (should not continue)
        if cobjname == 'Null':
            if return_flag:
                return '', 0
            else:
                return '', False
        # sql obj condition
        sql_obj_cond = 'OBJNAME="{0}" AND USED=1'.format(cobjname)
        # look for object name in database
        count = self.count(condition=sql_obj_cond)
        # if we have not found our object we must check aliases
        if count == 0:
            # condition - only use ones with USED
            condition = 'USED=1'
            # get the full database
            full_table = self.get_entries('OBJNAME, ALIASES',
                                          condition=condition)
            aliases = full_table['ALIASES']
            # set row to zero as a placeholder
            row = 0
            # loop around each row in the table
            for row in range(len(aliases)):
                # loop around aliases until we find the alias
                for alias in str(aliases[row]).split('|'):
                    if pconst.DRS_OBJ_NAME(alias) == cobjname:
                        found = 2
                        break
                # stop looping if we have found our object
                if found > 0:
                    break
            # get the cobjname for this target if found
            if found > 0:
                cobjname = full_table['OBJNAME'][row]
        # if there is an entry we found the object
        else:
            found = 1
        # store in global so we don't have to do this again
        OBS_NAMES[objname] = [cobjname, found]
        # return the correct object name
        if return_flag:
            return cobjname, found
        else:
            return cobjname, found > 0


# =============================================================================
# Define specific file databases
# =============================================================================
class CalibrationDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, pconst: Any = None):
        """
        Constructor of the Calibration Database class

        :param params: ParamDict, parameter dictionary of constants

        :return: None
        """
        # save class name
        self.classname = 'CalibrationDatabaseManager'
        # deal with no pconst
        if pconst is None:
            pconst = constants.pload()
        # construct super class
        DatabaseManager.__init__(self, params, pconst)
        # set name
        self.name = 'calibration'
        self.kind = 'calib'
        self.columns = self.pconst.CALIBRATION_DB_COLUMNS()
        self.colnames = self.columns.names
        # set path
        self.database_settings(kind=self.kind)
        # set database directory
        self.filedir = Path(str(self.params['DRS_CALIB_DB']))

    def add_calib_file(self, drsfile: DrsInputFile, verbose: bool = True,
                       copy_files=True):
        """
        Add DrsFile to the calibration database

        :param drsfile: DrsFile, the DrsFile to add
        :param verbose: bool, if True logs progress
        :param copy_files: bool, if True copies file to self.filedir

        :return: None
        """
        # set function
        # _ = display_func('add_calib_file', __NAME__,
        #                  self.classname)
        # deal with nosave
        if drsfile.nosave:
            return
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
        _get_dbtable(self.params, drsfile, self.name)
        # get fiber
        fiber = _get_hkey(self.params, 'KW_FIBER', hdict, header)
        # get super definition
        is_super = _get_is_super(drsfile)
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
        insert_dict = dict()
        insert_dict['KEYNAME'] = str(dbkey).strip()
        insert_dict['FIBER'] = str(fiber)
        insert_dict['REFCAL'] = int(is_super)
        insert_dict['FILENAME'] = str(drsfile.basename).strip()
        insert_dict['HUMANTIME'] = str(header_time.iso)
        insert_dict['UNIXTIME'] = float(header_time.unix)
        insert_dict['PID'] = str(self.params['PID'])
        insert_dict['PDATE'] = str(self.params['DATE_NOW'])
        insert_dict['USED'] = 1
        # ------------------------------------------------------------------
        # check that we are adding the correct columns (i.e. all columns
        #   are in database)
        self.check_columns(insert_dict)
        # ------------------------------------------------------------------
        # try to add a new row
        self.database.add_row(insert_dict=insert_dict)
        # update parameter table (if fits file)
        if isinstance(drsfile, DrsFitsFile):
            drsfile.update_param_table('CALIB_DB_ENTRY',
                                       param_kind='calib',
                                       values=list(insert_dict.values()))

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
        # _ = display_func('get_calib_entry', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # set up kwargs from database query
        sql = dict()
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # condition for key
        sql['condition'] = 'KEYNAME = "{0}"'.format(key)
        # condition for used
        sql['condition'] += ' AND USED = 1'
        # get unix time
        if hasattr(filetime, 'unix'):
            utime = filetime.unix
        else:
            utime = None
        # condition for fiber
        if fiber is not None:
            sql['condition'] += ' AND FIBER = "{0}"'.format(fiber)
        # sql for time mode
        if timemode == 'older' and utime is not None:
            # condition:
            #       UNIXTIME - FILETIME < 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} < 0'.format(utime)
            sql['sort_by'] = drs_db.SA_TEXT('abs(UNIXTIME - {0})'.format(utime))
            sql['sort_descending'] = False
        elif timemode == 'newer' and utime is not None:
            # condition:
            #       UNIXTIME - FILETIME > 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} > 0'.format(utime)
            sql['sort_by'] = drs_db.SA_TEXT('abs(UNIXTIME - {0})'.format(utime))
            sql['sort_descending'] = False
        elif utime is not None:
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['sort_by'] = drs_db.SA_TEXT('abs(UNIXTIME - {0})'.format(utime))
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
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
            # return pandas table
            return entries

    CALIB_FILE_RTN = Union[Tuple[None, float, bool],
                           Tuple[Path, float, bool],
                           Tuple[List[Path], List[float], List[bool]],
                           None]

    def get_calib_file(self, key: str, drsfile=None, header=None, hdict=None,
                       filetime: Union[None, Time] = None,
                       timemode: Union[str, None] = None,
                       nentries: Union[str, int] = 1,
                       required: bool = True,
                       no_times: bool = False,
                       fiber: Union[str, None] = None,
                       bintimes: bool = False) -> CALIB_FILE_RTN:
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
        :param bintimes: bool, if True will bin files by midnight/midday

        :return:
        """
        # set function
        func_name = display_func('get_calib_file', __NAME__,
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
            filetime = np.nan
        elif filetime is None:
            # need to get hdict/header
            hdict, header = _get_hdict(self.params, self.name, drsfile, hdict,
                                       header)
            # need to get filetime
            filetime = _get_time(self.params, self.name, hdict, header)
            # bin files by midnight/midday
            if bintimes:
                # get the the fraction of the day to bin to (0 = midnight
                # before observation, 0.5 = noon, and 1.0 = midnight after
                day_frac = self.params['CALIB_DB_DAYFRAC']
                # modify the filetime to be the binned time
                filetime = drs_misc.bin_by_time(self.params, filetime, day_frac)
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
        ctable = self.get_calib_entry('FILENAME, REFCAL, UNIXTIME', key,
                                      fiber, filetime, timemode, nentries)
        # deal with return of two columns (tulpe or pandas table)
        if ctable is None:
            filenames = None
            filetimes = np.nan
            reference = False
        elif isinstance(ctable, (tuple, list)):
            # get filename
            filenames = str(ctable[0])
            # get file time (unix)
            utimes = float(ctable[2])
            # get whether calibration is a reference
            reference = drs_text.true_text(ctable[1])
            # get file times in MJD
            filetimes = float(Time(utimes, format='unix').mjd)
        else:
            # get filenames
            filenames = np.array(ctable['FILENAME'])
            # get file times (unix)
            utimes = np.array(ctable['UNIXTIME'])
            # get whether calibrations are references
            reference = np.array(ctable['REFCAL']).astype(bool)
            # get file times in MJD
            filetimes = np.array(Time(utimes, format='unix').mjd).astype(float)
        # ---------------------------------------------------------------------
        # return absolute paths
        # ---------------------------------------------------------------------
        # deal with no filenames found and not required
        if (filenames is None or len(filenames) == 0) and not required:
            return None, np.nan, False
        # deal with no filenames found elsewise --> error
        if filenames is None or len(filenames) == 0:
            # get unique set of keys
            keys = self.database.unique('KEYNAME')
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
            # set output
            outfilename = Path(self.filedir).joinpath(filenames).absolute()
            # return outfilenames
            return outfilename, float(filetimes), bool(reference)
        # else loop around them (assume they are iterable)
        else:
            # set output storage
            outfilenames = []
            # loop around filenames
            for it, filename in enumerate(filenames):
                outfilename = Path(self.filedir).joinpath(filename).absolute()
                # append to storage
                outfilenames.append(outfilename)
            # return outfilenames
            return outfilenames, list(filetimes), list(reference)

    def remove_entries(self, condition: str):
        """
        Remove row(s) from a database

        :param condition: str, the sql WHERE condition for removing row(s) from
                          the database

        :return: None, operation on database
        """
        # set function
        # _ = display_func('remove_entries', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(condition=condition)


class TelluricDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, pconst: Any = None):
        """
        Constructor of the Telluric Database class

        :param params: ParamDict, parameter dictionary of constants

        :return: None
        """
        # save class name
        self.classname = 'TelluricDatabaseManager'
        # deal with no pconst
        if pconst is None:
            pconst = constants.pload()
        # construct super class
        DatabaseManager.__init__(self, params, pconst)
        # set name
        self.name = 'telluric'
        self.kind = 'tellu'
        self.columns = self.pconst.TELLURIC_DB_COLUMNS()
        self.colnames = self.columns.names
        # set path
        self.database_settings(kind=self.kind)
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
        # _ = display_func('add_tellu_file', __NAME__,
        #                  self.classname)
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
        _get_dbtable(self.params, drsfile, self.name)
        # get fiber
        fiber = _get_hkey(self.params, 'KW_FIBER', hdict, header)
        # get super definition
        is_super = _get_is_super(drsfile)
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
        insert_dict = dict()
        insert_dict['KEYNAME'] = str(dbkey).strip()
        insert_dict['FIBER'] = str(fiber).strip()
        insert_dict['REFCAL'] = int(is_super)
        insert_dict['FILENAME'] = str(drsfile.basename).strip()
        insert_dict['HUMANTIME'] = str(header_time.iso)
        insert_dict['UNIXTIME'] = float(header_time.unix)
        insert_dict['OBJECT'] = objname
        insert_dict['AIRMASS'] = airmass
        insert_dict['TAU_WATER'] = tau_water
        insert_dict['TAU_OTHERS'] = tau_others
        insert_dict['PID'] = str(self.params['PID'])
        insert_dict['PDATE'] = str(self.params['DATE_NOW'])
        insert_dict['USED'] = 1
        # ------------------------------------------------------------------
        # check that we are adding the correct columns (i.e. all columns
        #   are in database)
        self.check_columns(insert_dict)
        # ------------------------------------------------------------------
        # try to add a new row
        self.database.add_row(insert_dict=insert_dict)
        # update parameter table (if fits file)
        if isinstance(drsfile, DrsFitsFile):
            drsfile.update_param_table('TELLU_DB_ENTRY',
                                       param_kind='tellu',
                                       values=list(insert_dict.values()))

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
        # _ = display_func('get_tellu_entry', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
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
            sql['sort_by'] = drs_db.SA_TEXT('abs(UNIXTIME - {0})'
                                            ''.format(filetime.unix))
            sql['sort_descending'] = False
        elif timemode == 'newer' and filetime is not None:
            # condition:
            #       UNIXTIME - FILETIME > 0
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['condition'] += ' AND UNIXTIME - {0} > 0'.format(filetime.unix)
            sql['sort_by'] = drs_db.SA_TEXT('abs(UNIXTIME - {0})'
                                            ''.format(filetime.unix))
            sql['sort_descending'] = False
        elif filetime is not None:
            # sort by:
            #       ABS(UNIXTIME - FILETIME)
            sql['sort_by'] = drs_db.SA_TEXT('abs(UNIXTIME - {0})'
                                            ''.format(filetime.unix))
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
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
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
        func_name = display_func('get_calib_file', __NAME__,
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
            keys = self.database.unique('KEYNAME')
            # get file description
            if drsfile is not None:
                if no_times:
                    infile = '{0} [NoTime]'.format(drsfile.filename)
                elif filetime is not None:
                    infile = '{0} [Time={1}]'.format(drsfile.filename,
                                                     filetime.iso)
                else:
                    infile = 'None'
            else:
                if no_times:
                    infile = 'File[NoTime]'
                elif filetime is not None:
                    infile = 'File[Time={0}]'.format(filetime.iso)
                else:
                    infile = 'None'
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

    def remove_entries(self, condition: str):
        """
        Remove row(s) from a database

        :param condition: str, the sql WHERE condition for removing row(s) from
                          the database

        :return: None, operation on database
        """
        # set function
        # _ = display_func('remove_entries', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(condition=condition)


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
    func_name = display_func('_get_dbkey', __NAME__)
    # get dbname from drsfile
    if hasattr(drsfile, 'dbkey') and hasattr(drsfile, 'get_dbkey'):
        return drsfile.get_dbkey()
    else:
        eargs = [drsfile.name, dbmname, func_name]
        WLOG(params, 'error', textentry('00-008-00012', args=eargs))
        return 'None'


def _get_dbtable(params: ParamDict, drsfile: DrsFileTypes, dbmname: str) -> bool:
    """
    Check the dbname attribute from a drsfile matches the database type

    :param params: ParamDict, the parameter dictionary of constants
    :param drsfile: DrsInputFile (fits or npy) instance to get dbname from
    :param dbmname: str, the name of the database

    :return: bool, True if passed (raises exception otherwise)
    """
    # set function
    func_name = display_func('_get_dbname', __NAME__)
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
        emsg = ('Drsfile {0} cannot use database "{1}". Check file_definitions'
                '\n\tFunction = {2}')
        WLOG(params, 'error', emsg.format(*eargs))
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
    func_name = display_func('_get_hkey', __NAME__)
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


def _get_is_super(drsfile: DrsInputFile) -> int:
    """
    Find out whether file entry is from a super set or not

    :param drsfile: DrsFitsFile - the file to check whether it is a super

    :return: 1 if code is super else returns 0
    """
    # no outclass - not super
    if drsfile.outclass is None:
        return 0
    # get reference setting from params
    is_super = drsfile.outclass.reference
    # change bool to 1 or 0
    # get reference key
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
    func_name = display_func('_copy_db_file', __NAME__)
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
    func_name = display_func('_get_hdict', __NAME__)
    # get pseudo constants
    pconst = constants.pload()
    # deal with having hdict input
    if hdict is not None:
        return hdict, None
    # deal with having header input
    elif header is not None:
        return None, header
    # get hdict / header
    cond1 = hasattr(drsfile, 'hdict') and len(list(drsfile.hdict.keys())) != 0
    cond2 = hasattr(drsfile, 'header')
    # if fits file then we check the size of header
    if isinstance(drsfile, DrsFitsFile):
        cond2 &= len(list(drsfile.get_header().keys())) != 0
    # if npy file we check for header
    elif isinstance(drsfile, drs_file.DrsNpyFile):
        # if we have header check length of header
        if cond2:
            cond2 &= len(list(drsfile.header.keys())) != 0
        # else set cond2 to False
        else:
            cond2 = False
    # if we don't have header skip
    else:
        cond2 = False
    # deal with having both hdict and heaader
    if cond1 and cond2:
        # combine
        hdict = _force_apero_header(drsfile.hdict)
        header = _force_apero_header(drsfile.header)
        # add keys from hdict to header
        for key in hdict:
            # do not look at forbidden keys
            if key in params['FORBIDDEN_OUT_KEYS']:
                continue
            # else set key from hdict with the comment
            header[key] = (hdict[key], hdict.comments[key])
        # now set hdict to None
        hdict = None
    # deal with only having hdict
    elif cond1:
        hdict = _force_apero_header(drsfile.hdict)
        header = None
    # deal with only having header
    elif cond2:
        hdict = None
        header = _force_apero_header(drsfile.get_header())
    else:
        eargs = [dbname, drsfile.name, func_name]
        WLOG(params, 'error', textentry('00-001-00027', args=eargs))
        hdict, header = None, None
    return hdict, header


def _force_apero_header(header: Union[drs_fits.fits.Header, drs_fits.Header]
                        ) -> drs_fits.Header:
    """
    Force a header to be an apero fits header

    :param header: either an apero fits Header or an astropy fits Header

    :return: the apero fits Header equivalent
    """
    if isinstance(header, drs_fits.Header):
        return header
    else:
        return drs_fits.Header(header)


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
    func_name = display_func('_get_time', __NAME__)
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
class FileIndexDatabase(DatabaseManager):

    def __init__(self, params: ParamDict, pconst: Any = None):
        """
        Constructor of the Index Database class

        :param params: ParamDict, parameter dictionary of constants

        :return: None
        """
        # save class name
        self.classname = 'FileIndexDatabaseManager'
        # deal with no pconst
        if pconst is None:
            pconst = constants.pload()
        # construct super class
        DatabaseManager.__init__(self, params, pconst)
        # set name
        self.name = 'findex'
        self.kind = 'findex'
        self.columns = self.pconst.FILEINDEX_DB_COLUMNS()
        self.colnames = self.columns.names
        self.hcolumns = self.pconst.FILEINDEX_HEADER_COLS()
        self.hcolnames = self.hcolumns.names
        # set path
        self.database_settings(kind=self.kind)
        # store whether an update has been done
        self.update_entries_params = []

    def add_entry(self, basefile: drs_file.DrsPath,
                  block_kind: str, recipe: Union[str, None] = None,
                  runstring: Union[str, None] = None,
                  infiles: Union[str, None] = None,
                  hkeys: Union[Dict[str, str], None] = None,
                  used: Union[int, None] = None,
                  rawfix: Union[int, None] = None):
        """
        Add an entry to the index database

        :param basefile: str, the sub-directory name (under the raw/reduced/
                         tmp directory)
        :param block_kind: str, either 'raw', 'red', 'tmp', 'calib', 'tellu',
                           'asset' this determines the path of the file i.e.
                            path/directory/filename (unless filename is an
                            absolute path) - note in this case directory should
                            still be filled correctly (for database)
        :param recipe: str, the recipe name
        :param runstring: str, the command line arg representation of this
                          indexs recipe run
        :param infiles: str, the string list of infiles for this index entry
                        (blank if not a drs output)
        :param hkeys: dictionary of strings, for each instrument a set
                            of header keys is index - add any that are set to
                            here (see pseudo_constants.INDEX_HEADER_KEYS)
                            any that are not set here are set to 'None'

        :param used: int or None, if set overrides the default "used" parameter
        :param rawfix: int or None, if set overrides the default "rawfix"
                       parameter

        :return: None - adds entry to index database
        """
        # set function
        func_name = display_func('add_entry', __NAME__,
                                 self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # set used to 1
        if used is None:
            used = 1
        # this is a flag to test whether raw data has been fixed (so we don't
        #   do it again when not required)
        if rawfix is None:
            if block_kind.lower() == 'raw':
                rawfix = 0
            else:
                rawfix = 1
        # ------------------------------------------------------------------
        # get last modified time for file (need absolute path)
        last_modified = float(basefile.to_path().stat().st_mtime)
        # get recipe
        if drs_text.null_text(recipe, ['None', 'Null']):
            recipe = 'Unknown'
        # get run string
        if drs_text.null_text(runstring, ['None', 'Null']):
            runstring = 'NULL'
        # get infiles
        if drs_text.null_text(infiles, ['None', 'Null', '']):
            infiles = 'NULL'
        # ------------------------------------------------------------------
        # get allowed header keys
        iheader_cols = self.pconst.FILEINDEX_HEADER_COLS()
        rkeys = list(iheader_cols.names)
        # store values in correct order for database.add_row
        hvalues = dict()
        # deal with no hkeys
        if hkeys is None:
            hkeys = dict()
        # loop around allowed header keys and check for them in headers
        #  keys - if not there set to 'None'
        for h_it, hkey in enumerate(rkeys):
            if hkey in hkeys:
                # get data type
                dtype = self.columns.get_datatype(hkey)
                if dtype is None:
                    continue
                # noinspection PyBroadException
                try:
                    # get value
                    value = hkeys[hkey]
                    # deal with a null value
                    if drs_text.null_text(value, ['None', 'Null']):
                        hvalues[hkey] = 'NULL'
                    else:
                        # try to case and append
                        hvalues[hkey] = dtype(value)
                except Exception as _:
                    wargs = [self.name, hkey, hkeys[hkey],
                             dtype, func_name]
                    wmsg = textentry('10-002-00003', args=wargs)
                    WLOG(self.params, 'warning', wmsg, sublevel=2)
                    hvalues[hkey] = 'NULL'
            else:
                hvalues[hkey] = 'NULL'
        # ------------------------------------------------------------------
        # create insert dictionary
        insert_dict = dict()
        insert_dict['ABSPATH'] = str(basefile.abspath)
        insert_dict['OBS_DIR'] = str(basefile.obs_dir)
        insert_dict['FILENAME'] = str(basefile.basename)
        insert_dict['BLOCK_KIND'] = block_kind
        insert_dict['LAST_MODIFIED'] = float(last_modified)
        insert_dict['RECIPE'] = str(recipe)
        insert_dict['RUNSTRING'] = str(runstring)
        insert_dict['INFILES'] = str(infiles)
        # push header values into insert dictionary
        for hkey in self.hcolnames:
            insert_dict[hkey] = hvalues[hkey]
        insert_dict['USED'] = used
        insert_dict['RAWFIX'] = rawfix
        # ------------------------------------------------------------------
        # check for entry already in database
        condition = '(OBS_DIR="{0}")'.format(insert_dict['OBS_DIR'])
        condition += ' AND (BLOCK_KIND="{0}")'.format(block_kind)
        condition += ' AND (FILENAME="{0}")'.format(insert_dict['FILENAME'])
        # ------------------------------------------------------------------
        # check that we are adding the correct columns (i.e. all columns
        #   are in database)
        self.check_columns(insert_dict)
        # ------------------------------------------------------------------
        # count number of entries for this
        num_rows = self.database.count(condition=condition)
        # if we don't have an entry we add a row
        if num_rows == 0:
            self.database.add_row(insert_dict=insert_dict)
        else:
            # condition comes from uhash - so set to None here (to remember)
            condition = None
            # update row in database
            self.database.set(update_dict=insert_dict, condition=condition)

    def remove_entries(self, condition: str):
        """
        Remove row(s) from a database

        :param condition: str, the sql WHERE condition for removing row(s) from
                          the database

        :return: None, operation on database
        """
        # set function
        # _ = display_func('remove_entries', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(condition=condition)

    def get_entries(self, columns: str = '*',
                    obs_dir: Union[str, None] = None,
                    filename: Union[Path, str, None] = None,
                    block_kind: Union[str, None] = None,
                    hkeys: Union[Dict[str, str], None] = None,
                    nentries: Union[int, None] = None,
                    condition: Union[str, None] = None,
                    ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the index database (can set columns to return, or
        filter by specific columns)

        :param columns: str, the columns to return ('*' for all)
        :param obs_dir: str or None, if set filters results by directory name
        :param filename: str or None, if set filters results by filename
        :param block_kind: str or None, if set filters results by kind
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
        func_name = display_func('get_entries', __NAME__,
                                 self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
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
        if block_kind is not None:
            sql['condition'] += ' AND BLOCK_KIND = "{0}"'.format(block_kind)
        # ------------------------------------------------------------------
        # deal with directory set
        if obs_dir is not None:
            sql['condition'] += ' AND OBS_DIR = "{0}"'.format(obs_dir)
        # ------------------------------------------------------------------
        # deal with filename set
        if filename is not None:
            sql['condition'] += ' AND FILENAME = "{0}"'.format(filename)
        # ------------------------------------------------------------------
        # get allowed header keys
        iheader_cols = self.pconst.FILEINDEX_HEADER_COLS()
        rkeys = list(iheader_cols.names)
        # deal with filter by header keys
        if hkeys is not None and isinstance(hkeys, dict):
            # loop around each valid header key in index database
            for h_it, hkey in enumerate(rkeys):
                # if we have the key in our header keys
                if hkey in hkeys:
                    # get data type
                    dtype = self.columns.get_datatype(hkey)
                    if dtype is None:
                        continue
                    # noinspection PyBroadException
                    try:
                        # try to case and add to condition
                        hargs = [hkey, dtype, hkeys[hkey]]
                        condition = drs_file.index_hkey_condition(*hargs)
                        sql['condition'] += condition
                    except Exception as _:
                        wargs = [self.name, hkey, hkeys[hkey],
                                 dtype, func_name]
                        wmsg = textentry('10-002-00003', args=wargs)
                        WLOG(self.params, 'warning', wmsg)
        # ------------------------------------------------------------------
        # add the number of entries to get
        if isinstance(nentries, int):
            sql['max_rows'] = nentries
        # if we have one entry just get the tuple back
        if nentries == 1:
            # do sql query
            entries = self.database.get(columns, **sql)
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
        colnames = self.database.colnames(columns)
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
            # return pandas table
            return entries

    # complex typing for filename(s) in update_entries
    FileTypes = Union[List[Union[Path, str]], Path, str, None]

    def update_entries(self, block_kind: str,
                       include_directories: Union[List[str], None] = None,
                       exclude_directories: Union[List[str], None] = None,
                       filename: FileTypes = None, suffix: str = '',
                       force_update: bool = False):
        """
        Update the index database for files of 'kind', deal with including
        and excluding directories for files with 'suffix'

        :param block_kind: str, either 'raw', 'red', 'tmp', 'calib', 'tellu',
                           'asset' this determines the path of the file i.e.
                            path/directory/filename (unless filename is
                            an absolute path) - note in this case directory
                            should still be filled correctly (for database)
        :param include_directories: list of strings or None, if set only
                                    include these observation directories to
                                    update index database
        :param exclude_directories: list of strings or None, if set exclude
                                    these observation directories from being
                                    updated in the index database
        :param filename: str, Path, list of strs/Paths or None, if set we only
                         include this filename or these filenames
        :param suffix: str, the suffix (i.e. extension of filenames) - filters
                       to only set these files
        :param force_update: bool, if True forces the update even if database
                             thinks it is up-to-date

        :return: None - updates the index database
        """
        # set function
        # _ = display_func('update_entries', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # ---------------------------------------------------------------------
        # deal with database already being up-to-date
        # store whether an update has been done
        if not force_update:
            # if the exact same inputs have been used we can skip update
            #   (Again unless "force_update" was used)
            cond = self._update_params(block_kind=block_kind,
                                       include_directories=include_directories,
                                       exclude_directories=exclude_directories,
                                       filename=filename)
            # if we are not updating return here
            if not cond:
                # print skipping: Skipping search (already run)
                WLOG(self.params, 'debug', textentry('40-001-00031'))
                return None
        # ---------------------------------------------------------------------
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # get the block instance
        block_inst = drs_file.DrsPath(self.params, block_kind=block_kind)
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
        etable = self.get_entries('ABSPATH, OBS_DIR, LAST_MODIFIED',
                                  block_kind=block_kind)
        raw_exclude_files = list(etable['ABSPATH'])
        raw_exclude_obs_dirs = list(etable['OBS_DIR'])
        # ---------------------------------------------------------------------
        # only check last modified for raw files (we assume that any other
        #   file has been correctly updated by the drs)
        if block_kind.lower() == 'raw':
            raw_last_mod = list(etable['LAST_MODIFIED'])
        else:
            raw_last_mod = None
        # ---------------------------------------------------------------------
        # must check exclude files are on disk unless we are in parellel mode
        parallel = False
        if 'PARALLEL' in self.params['INPUTS']:
            if self.params['INPUTS']['PARALLEL']:
                parallel = True
        # only check for deletions on disk if not in a parellel loop
        if not parallel:
            exclude_files, remove_files, remove_obs_dirs = [], [], []
            # deal with updating last modified date
            if raw_last_mod is not None:
                elast_mod = []
            else:
                elast_mod = None
            # loop around files to exclude
            for r_it, raw_exclude_file in enumerate(raw_exclude_files):
                if os.path.exists(raw_exclude_file):
                    exclude_files.append(raw_exclude_file)
                    if elast_mod is not None:
                        elast_mod.append(raw_last_mod[r_it])
                else:
                    remove_files.append(raw_exclude_file)
                    remove_obs_dirs.append(raw_exclude_obs_dirs[r_it])
            # remove entries from database where file does not exist
            rm_condition_all = 'BLOCK_KIND="{0}" AND '.format(block_kind)
            rm_conditions = []
            # loop around files to remove
            for r_it, remove_file in enumerate(remove_files):
                # add remove file condition with obs_dir + filename
                rm_cond = '(OBS_DIR="{0}" AND FILENAME="{1}")'
                rm_args = [remove_obs_dirs[r_it], os.path.basename(remove_file)]
                rm_conditions.append(rm_cond.format(*rm_args))
                # print removing file: File no longer on disk - removing from
                #                file index database: {0}
                wmsg = textentry('10-002-00008', args=[remove_file])
                WLOG(self.params, 'warning', wmsg)

            # remove entries which no longer exist on disk
            if len(rm_conditions) > 0:
                # add all remove conditions with the OR criteria
                rm_condition_all += ' OR '.join(rm_conditions)
                # use database to remove entries
                self.remove_entries(condition=rm_condition_all)
        # else we just use the raw list
        else:
            exclude_files = list(raw_exclude_files)
            elast_mod = raw_last_mod

        # ---------------------------------------------------------------------
        # locate all files within path
        reqfiles = _get_files(self.params, block_inst.abspath, block_kind,
                              include_directories, exclude_directories,
                              include_files, exclude_files, suffix, elast_mod)
        # ---------------------------------------------------------------------
        # get allowed header keys
        iheader_cols = self.pconst.FILEINDEX_HEADER_COLS()
        rkeys = list(iheader_cols.names)
        # get unique columns
        idb_cols = self.pconst.FILEINDEX_DB_COLUMNS()
        ikeys = list(idb_cols.names)
        ucols = list(idb_cols.uniques)
        # need to add hash key if required
        if len(ucols) > 0:
            ikeys += [drs_db.UHASH_COL]
        # ---------------------------------------------------------------------
        # deal with database having wrong columns (if we have added / remove a
        #  column and are updating because of this)
        columns = self.database.colnames('*')
        # check if columns and rkeys agree
        if len(columns) != len(ikeys):
            # prompt user and warn
            wargs = [len(columns), len(ikeys)]
            # log warning: Index database has wrong number of columns
            WLOG(self.params, 'warning', textentry('10-002-00005', args=wargs))
            # reset database
            userinput = input(str(textentry('10-002-00006')))
            # if yes delete table and recreate
            if 'Y' in userinput.upper():
                # remove table
                self.database.delete_table(self.database.tablename)
                # add new empty table
                self.database.add_table(self.database.tablename,
                                        self.columns.columns,
                                        self.columns.indexes,
                                        self.columns.uniques)
                # reload database
                self.load_db()
                # update all entries for raw index entries
                iargs = ['raw']
                WLOG(self.params, 'info', textentry('40-006-00006', args=iargs))
                self.update_entries('raw', force_update=True)
                # update all entries for tmp index entries
                iargs = ['tmp']
                WLOG(self.params, 'info', textentry('40-006-00006', args=iargs))
                self.update_entries('tmp', force_update=True)
                # update all entries for reduced index entries
                iargs = ['red']
                WLOG(self.params, 'info', textentry('40-006-00006', args=iargs))
                self.update_entries('red', force_update=True)
                return
        # ---------------------------------------------------------------------
        # deal with no files
        if len(reqfiles) == 0:
            # return
            return
        # ---------------------------------------------------------------------
        # log: Reading headers of {0} files (to be updated)
        margs = [len(reqfiles)]
        WLOG(self.params, '', textentry('40-001-00032', args=margs))
        # add required files to the database
        for reqfile in tqdm(reqfiles):
            # get a drs path for required file
            req_inst = drs_file.DrsPath(self.params, abspath=reqfile)
            # get header keys
            hkeys = dict()
            # load missing files
            if str(reqfile).endswith('.fits'):
                # load header
                try:
                    header = drs_fits.read_header(self.params, str(reqfile),
                                                  log=False)
                except Exception as e:
                    # print error message as warning:
                    #       Skipping file {0}\n\tError {1}: {2}'
                    wargs = [str(reqfile), type(e), str(e)]
                    wmsg = textentry('10-002-00009', args=wargs)
                    WLOG(self.params, 'warning', wmsg, sublevel=6)
                    continue
                # loop around required keys
                for rkey in rkeys:
                    # get drs key
                    drs_key = self.params[rkey][0]
                    # if key is in header then add to hkeys
                    if drs_key in header:
                        hkeys[rkey] = header[drs_key]
            # add to database
            self.add_entry(req_inst, block_kind, hkeys=hkeys)

    def update_header_fix(self, recipe: Any, objdbm: AstrometricDatabase):
        """
        Update the index database with the header fixes for block_kind = raw

        The object database is required as we need to check against object
        name aliases (raw data will have the wrong object name otherwise)

        :param recipe: DrsRecipe, the recipe that called this function
        :param objdbm: ObjectDatabase, the object database class

        :return: None - updates the IndexDatabase
        """
        # set function name
        # _ = display_func('update_objname', __NAME__, self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # get allowed header keys
        iheader_cols = self.pconst.FILEINDEX_HEADER_COLS()
        rkeys = list(iheader_cols.names)
        # get columns
        columns = ['BLOCK_KIND', 'ABSPATH', 'OBS_DIR', 'FILENAME', 'RAWFIX']
        columns += rkeys
        # get data for columns
        table = self.get_entries(', '.join(columns), block_kind='raw')
        # if all rows have rawfix == 1 then just return now
        if np.sum(table['RAWFIX']) == len(table):
            return
        # need to loop around each row
        for row in tqdm(range(len(table))):
            # do not re-fix is rawfix is 1
            if table['RAWFIX'].iloc[row] == 1:
                continue
            # do not fix headers of non-fits files
            if not table['FILENAME'].iloc[row].endswith('.fits'):
                continue
            # get new header to push keys into
            header = drs_fits.Header()
            # add keys to header
            for rkey in rkeys:
                # get drs key
                drs_key = self.params[rkey][0]
                # get data type
                dtype = iheader_cols.get_datatype(rkey)
                # get value from table for rkey
                value = table[rkey].iloc[row]
                # populate header
                if value is None:
                    header[drs_key] = 'Null'
                else:
                    header[drs_key] = dtype(value)
            # fix header (with new keys in)
            header, _ = drs_file.fix_header(self.params, recipe, header=header,
                                            check_aliases=True, objdbm=objdbm)
            # condition is that full path is the same
            ctxt = 'BLOCK_KIND="{0}" AND OBS_DIR="{2}" AND FILENAME="{3}"'
            # cargs must match "columns" above
            cargs = [table['BLOCK_KIND'].iloc[row], table['ABSPATH'].iloc[row],
                     table['OBS_DIR'].iloc[row], table['FILENAME'].iloc[row]]
            condition = ctxt.format(*cargs)
            # get values
            values = cargs + ['1']
            # add header keys in rkeys
            for rkey in rkeys:
                # get drs key
                drs_key = self.params[rkey][0]
                # get value from table for rkey
                if drs_key in header:
                    values.append(header[drs_key])
                else:
                    values.append('Null')
            # update this row (should only be one row based on condition)
            self.database.set(columns, values=values, condition=condition)

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

    def get_unique(self, column: str,
                   condition: Optional[str] = None) -> np.ndarray:
        """
        Get unique entries in a column

        :param column: str, the column name
        :param condition: optional str, if present a condition to limit the
                          search to

        :return: list of unique entries from "column"
        """
        # use database functionality
        return self.database.unique(column, condition=condition)


def _get_files(params: ParamDict, path: Union[Path, str], block_kind: str,
               incdirs: Union[List[Union[str, Path]], None] = None,
               excdirs: Union[List[Union[str, Path]], None] = None,
               incfiles: Union[List[Union[str, Path]], None] = None,
               excfiles: Union[List[Union[str, Path]], None] = None,
               suffix: str = '',
               last_modified: Union[List[float], None] = None) -> List[Path]:
    """
    Get files in 'path'. If kind in ['raw' 'tmp' 'red'] then look through
    subdirectories including 'incdirs' directories and excluding 'excdirs'
    directories

    :param path: Path or str, the path to the directory to find files for
    :param block_kind: str, the kind of files to kind (raw/tmp/red/calib/tellu etc)
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
    :param last_modified: list of floats - the last modified times for the
                          excfiles (if given, checks the last modified date
                          and doesn't exclude files if last modified date is
                          different from this list) - must be same length as
                          excfiles

    :return: list of paths, the file list (absolute file list) as Path instances
    """
    # fix path as string
    if isinstance(path, str):
        path = Path(path)
    # get path instance
    path_inst = drs_file.DrsPath(params, _update=False)
    # get blocks with obs_dirs
    block_names = path_inst.blocks_with_obs_dirs()
    # -------------------------------------------------------------------------
    # print progress: Searching all directories'
    WLOG(params, '', textentry('40-001-00033'))
    # get conditions (so we don't repeat them)
    incdircond = incdirs is not None
    excdircond = excdirs is not None
    # -------------------------------------------------------------------------
    # get absolute path for all included dirs
    incdirs1 = []
    if incdircond:
        for incdir in incdirs:
            ipath = drs_file.DrsPath(params, block_kind=block_kind,
                                     obs_dir=incdir)
            incdirs1.append(ipath.abspath)
    # -------------------------------------------------------------------------
    # get absolute path for all excluded dirs
    excdirs1 = []
    if excdircond:
        for excdir in excdirs:
            epath = drs_file.DrsPath(params, block_kind=block_kind,
                                     obs_dir=excdir)
            excdirs1.append(epath.abspath)
    # -------------------------------------------------------------------------
    # only use sub-directories for the following kinds
    if block_kind.lower() in block_names:
        # ---------------------------------------------------------------------
        # processing sub-directories
        TLOG(params, '', 'Listing dir {0}...'.format(path))
        # get all sub directory path
        all_dirs = drs_path.listdirs(str(path))
        # loop around directories
        subdirs = []
        for item in all_dirs:
            # processing sub-directories
            TLOG(params, '', 'Listing dir {0}...'.format(item))
            # skip directories not in included directories
            if incdircond:
                if item not in incdirs1:
                    continue
            # skip directories in excluded directories
            if excdircond:
                if item in excdirs1:
                    continue
            # if we have reached here then append subdirs
            subdirs.append(item)
            # clear loading message
        TLOG(params, '', '')
    # else we do not use subdirs
    else:
        subdirs = None
    # -------------------------------------------------------------------------
    # deal with no subdirs
    if subdirs is None:
        # get all files in path
        # allfiles = list(path.rglob('*{0}'.format(suffix)))
        allfiles = drs_path.recursive_path_glob(params, path, suffix=suffix)
    # else we have subdirs
    else:
        allfiles = []
        # loop around subdirs
        for subdir in subdirs:
            # processing sub-directories
            TLOG(params, '', 'Analysing {0}...'.format(subdir))
            # append to filenames
            # allfiles += list(Path(subdir).glob('*{0}'.format(suffix)))
            allfiles += drs_path.recursive_path_glob(params, subdir,
                                                     suffix=suffix)
    # clear loading message
    TLOG(params, '', '')
    # -------------------------------------------------------------------------
    # store valid files
    valid_files = []
    # include files condition
    incond = incfiles is not None and len(incfiles) > 0
    # exclude files condition
    outcond = excfiles is not None
    # last mod condition
    lmodcond = last_modified is not None
    # -------------------------------------------------------------------------
    # convert last modified
    if last_modified is not None:
        lmod = dict(zip(excfiles, last_modified))
    else:
        lmod = dict()
    # -------------------------------------------------------------------------
    # make incfiles and exfiles sets (quicker than lists)
    if incond:
        incfiles = set(incfiles)
    if outcond:
        excfiles = set(excfiles)
    # -------------------------------------------------------------------------
    # filter files
    for filename in allfiles:
        # processing sub-directories
        TLOG(params, '', 'Check filter {0}...'.format(filename))
        # str filename
        strfilename = str(filename)
        # do not include directories
        if not filename.is_file():
            continue
        # include files (if include files defined) and filename in incfiles
        if incond and strfilename not in incfiles:
            continue
        # exclude files (if exclude files defined) and filename in excfiles
        if outcond and strfilename in excfiles:
            # only do this condition if last modified was defined
            if lmodcond:
                # get last modified time
                ftime = float(filename.stat().st_mtime)
                # only continue if ftime is equal to the one given
                #  we only need precision at 1e-2 seconds
                if np.round(ftime, 2) == np.round(lmod[strfilename], 2):
                    continue
            # else if we do not have a last modified vector just skip
            #    this file
            else:
                continue
        # add file to valid file list
        valid_files.append(filename.absolute())
    # clear loading message
    TLOG(params, '', '')
    # return valid files
    return valid_files


# =============================================================================
# Define Log database
# =============================================================================
class LogDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, pconst: Any = None):
        """
        Constructor of the Log Database class

        :param params: ParamDict, parameter dictionary of constants

        :return: None
        """
        # save class name
        self.classname = 'LogDatabaseManager'
        # deal with no pconst
        if pconst is None:
            pconst = constants.pload()
        # construct super class
        DatabaseManager.__init__(self, params, pconst)
        # set name
        self.name = 'log'
        self.kind = 'log'
        # set path
        self.database_settings(kind=self.kind)

    def remove_pids(self, pid: str):
        """
        Remove rows with this pid
        :param pid:
        :return:
        """
        # set up condition
        condition = 'PID="{0}"'.format(pid)
        # delete rows that match this criteria
        self.database.delete_rows(condition=condition)

    def add_entries(self, recipe: Union[str, None] = None,
                    sname: Union[str, None] = None,
                    block_kind: Union[str, None] = None,
                    recipe_type: Union[str, None] = None,
                    recipe_kind: Union[str, None] = None,
                    program_name: Union[str, None] = None,
                    pid: Union[str, None] = None,
                    htime: Union[str, None] = None,
                    unixtime: Union[float, None] = None,
                    group: Union[str, None] = None,
                    level: Union[int, None] = None,
                    sublevel: Union[int, None] = None,
                    levelcrit: Union[str, None] = None,
                    inpath: Union[str, None] = None,
                    outpath: Union[str, None] = None,
                    obs_dir: Union[str, None] = None,
                    logfile: Union[str, None] = None,
                    plotdir: Union[str, None] = None,
                    runstring: Union[str, None] = None,
                    args: Union[str, None] = None,
                    kwargs: Union[str, None] = None,
                    skwargs: Union[str, None] = None,
                    start_time: Union[str, None] = None,
                    end_time: Union[str, None] = None,
                    started: Union[bool, int, None] = None,
                    passed_all_qc: Union[bool, int, None] = None,
                    qc_string: Union[str, None] = None,
                    qc_names: Union[str, None] = None,
                    qc_values: Union[str, None] = None,
                    qc_logic: Union[str, None] = None,
                    qc_pass: Union[str, None] = None,
                    errors: Union[str, None] = None,
                    ended: Union[int, None] = None,
                    flagnum: Union[int, None] = None,
                    flagstr: Union[str, None] = None,
                    used: Union[int, None] = None,
                    ram_usage_start: Union[float, None] = None,
                    ram_usage_end: Union[float, None] = None,
                    ram_total: Union[float, None] = None,
                    swap_usage_start: Union[float, None] = None,
                    swap_usage_end: Union[float, None] = None,
                    swap_total: Union[float, None] = None,
                    cpu_usage_start: Union[float, None] = None,
                    cpu_usage_end: Union[float, None] = None,
                    cpu_num: Union[int, None] = None,
                    log_start: Union[str, None] = None,
                    log_end: Union[str, None] = None):
        """
        Add a log entry to database

        :param recipe: str, the recipe name
        :param sname: str, the short name
        :param block_kind: str, the block kind (raw/tmp/reduced etc)
        :param recipe_type: str, the type of recipe ('recipe', 'tool',
                            'processing' etc)
        :param recipe_kind: str, the kind of recipe ('calib', 'extract',
               'tellu' etc)
        :param program_name: str, the program name for this run
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
        :param obs_dir: str, the directory that set for this recipe run
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
        :param start_time: str, the human time recipe started
        :param end_time: str, the human time recipe ended
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
        :param ended: int, 1 if ended, 0 if still running
        :param flagnum: int, the integer version of the binary flag number
        :param flagstr: str, the flag strings for each bit of the binary number
        :param used: int, if entry should be used - always 1 for use internally
        :param ram_usage_start: float, RAM usage GB at start of recipe
        :param ram_usage_end: float, RAM usage GB at end of recipe
        :param ram_total: float, RAM total at start of recipe
        :param swap_usage_start: float, SWAP usage GB at start of recipe
        :param swap_usage_end: float, SWAP usage GB at end of recipe
        :param swap_total: float, SWAP total at start of recipe
        :param cpu_usage_start: float, CPU usage (percentage) at start of recipe
        :param cpu_usage_end: float, CPU usage (percentrage) at end of recipe
        :param cpu_num: int, number of CPUs at start
        :param log_start: str, the human time log sub-level started
        :param log_end: str, the human time log sub-level ended

        :return: None - updates database
        """
        # need to clean error to put into database
        clean_error = _clean_error(errors)
        # get insert dictionary
        insert_dict = dict()
        insert_dict['RECIPE'] = drs_db.deal_with_null(recipe)
        insert_dict['SHORTNAME'] = drs_db.deal_with_null(sname)
        insert_dict['BLOCK_KIND'] = drs_db.deal_with_null(block_kind)
        insert_dict['RECIPE_TYPE'] = drs_db.deal_with_null(recipe_type)
        insert_dict['RECIPE_KIND'] = drs_db.deal_with_null(recipe_kind)
        insert_dict['PROGRAM_NAME'] = drs_db.deal_with_null(program_name)
        insert_dict['PID'] = drs_db.deal_with_null(pid)
        insert_dict['HUMANTIME'] = drs_db.deal_with_null(htime)
        insert_dict['UNIXTIME'] = drs_db.deal_with_null(unixtime)
        insert_dict['GROUPNAME'] = drs_db.deal_with_null(group)
        insert_dict['LEVEL'] = drs_db.deal_with_null(level)
        insert_dict['SUBLEVEL'] = drs_db.deal_with_null(sublevel)
        insert_dict['LEVELCRIT'] = drs_db.deal_with_null(levelcrit)
        insert_dict['INPATH'] = drs_db.deal_with_null(inpath)
        insert_dict['OUTPATH'] = drs_db.deal_with_null(outpath)
        insert_dict['OBS_DIR'] = drs_db.deal_with_null(obs_dir)
        insert_dict['LOGFILE'] = drs_db.deal_with_null(logfile)
        insert_dict['PLOTDIR'] = drs_db.deal_with_null(plotdir)
        insert_dict['RUNSTRING'] = drs_db.deal_with_null(runstring)
        insert_dict['ARGS'] = drs_db.deal_with_null(args)
        insert_dict['KWARGS'] = drs_db.deal_with_null(kwargs)
        insert_dict['SKWARGS'] = drs_db.deal_with_null(skwargs)
        insert_dict['START_TIME'] = drs_db.deal_with_null(start_time)
        insert_dict['END_TIME'] = drs_db.deal_with_null(end_time)
        insert_dict['STARTED'] = drs_db.deal_with_null(started)
        insert_dict['PASSED_ALL_QC'] = drs_db.deal_with_null(passed_all_qc)
        insert_dict['QC_STRING'] = drs_db.deal_with_null(qc_string)
        insert_dict['QC_NAMES'] = drs_db.deal_with_null(qc_names)
        insert_dict['QC_VALUES'] = drs_db.deal_with_null(qc_values)
        insert_dict['QC_LOGIC'] = drs_db.deal_with_null(qc_logic)
        insert_dict['QC_PASS'] = drs_db.deal_with_null(qc_pass)
        insert_dict['ERRORMSGS'] = drs_db.deal_with_null(clean_error)
        insert_dict['ENDED'] = drs_db.deal_with_null(ended)
        insert_dict['FLAGNUM'] = drs_db.deal_with_null(flagnum)
        insert_dict['FLAGSTR'] = drs_db.deal_with_null(flagstr)
        insert_dict['USED'] = drs_db.deal_with_null(used)
        insert_dict['RAM_USAGE_START'] = drs_db.deal_with_null(ram_usage_start)
        insert_dict['RAM_USAGE_END'] = drs_db.deal_with_null(ram_usage_end)
        insert_dict['RAM_TOTAL'] = drs_db.deal_with_null(ram_total)
        insert_dict['SWAP_USAGE_START'] = drs_db.deal_with_null(swap_usage_start)
        insert_dict['SWAP_USAGE_END'] = drs_db.deal_with_null(swap_usage_end)
        insert_dict['SWAP_TOTAL'] = drs_db.deal_with_null(swap_total)
        insert_dict['CPU_USAGE_START'] = drs_db.deal_with_null(cpu_usage_start)
        insert_dict['CPU_USAGE_END'] = drs_db.deal_with_null(cpu_usage_end)
        insert_dict['CPU_NUM'] = drs_db.deal_with_null(cpu_num)
        insert_dict['LOG_START'] = drs_db.deal_with_null(log_start)
        insert_dict['LOG_END'] = drs_db.deal_with_null(log_end)
        # ------------------------------------------------------------------
        # check that we are adding the correct columns (i.e. all columns
        #   are in database)
        self.check_columns(insert_dict)
        # add row to database
        self.database.add_row(insert_dict=insert_dict)

    def get_entries(self, columns: str = '*',
                    include_obs_dirs: Union[List[str], None] = None,
                    exclude_obs_dirs: Union[List[str], None] = None,
                    nentries: Union[int, None] = None,
                    condition: Union[str, None] = None,
                    groupby: Union[str, None] = None,
                    ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the index database (can set columns to return, or
        filter by specific columns)

        :param columns: str, the columns to return ('*' for all)
        :param include_obs_dirs: list of strings - if set a list of allowed
                                 directories
        :param exclude_obs_dirs: list of strings - if set a list of disallowed
                                 directories
        :param nentries: int or None, if set limits the number of entries to get
                         back - sorted newest to oldest
        :param condition: str or None, if set the SQL query to add
        :param groupby: str or None, if set the SQL group by column

        :return: the entries of columns, if nentries = 1 returns either that
                 entry (as a tuple) or None, if len(columns) = 1, returns
                 a np.ndarray, else returns a pandas table
        """
        # set function
        # _ = display_func('get_entries', __NAME__, self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
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
        if include_obs_dirs is not None:
            # define a subcondition
            subconditions = []
            # loop around white listed nights and only keep these
            for obs_dir in include_obs_dirs:
                # add subcondition
                subcondition = 'OBS_DIR="{0}"'.format(obs_dir)
                subconditions.append(subcondition)
            # must include "other" for OBS_DIR
            subconditions.append('OBS_DIR="other"')
            # add to conditions
            sql['condition'] += ' AND ({0})'.format(' OR '.join(subconditions))
        # ------------------------------------------------------------------
        # deal with blacklist directory set
        if exclude_obs_dirs is not None:
            for obs_dir in exclude_obs_dirs:
                # add to condition
                sql['condition'] += ' AND (OBS_DIR!="{0}")'.format(obs_dir)
        # ------------------------------------------------------------------
        # add a group by argument
        if groupby is not None:
            sql['groupby'] = groupby
        # ------------------------------------------------------------------
        # add the number of entries to get
        if isinstance(nentries, int):
            sql['max_rows'] = nentries
        # if we have one entry just get the tuple back
        if nentries == 1:
            # do sql query
            entries = self.database.get(columns, **sql)
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
        colnames = self.database.colnames(columns)
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
            # return pandas table
            return entries

    def remove_entries(self, condition: str):
        """
        Remove row(s) from a database

        :param condition: str, the sql WHERE condition for removing row(s) from
                          the database

        :return: None, operation on database
        """
        # set function
        # _ = display_func('remove_entries', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(condition=condition)


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
# Define reject database
# =============================================================================
class RejectDatabase(DatabaseManager):
    def __init__(self, params: ParamDict, pconst: Any = None):
        """
        Constructor of the Reject Database class

        :param params: ParamDict, parameter dictionary of constants

        :return: None
        """
        # save class name
        self.classname = 'RejectDatabaseManager'
        # deal with no pconst
        if pconst is None:
            pconst = constants.pload()
        # construct super class
        DatabaseManager.__init__(self, params, pconst)
        # set name
        self.name = 'reject'
        self.kind = 'reject'
        # set path
        self.database_settings(kind=self.kind)

    def add_entries(self, identifier: Optional[str] = None,
                    pp_flag: Optional[bool] = None,
                    tel_flag: Optional[bool] = None,
                    rv_flag: Optional[bool] = None,
                    used: Union[int, None] = None,
                    comment: Union[str, None] = None):
        """
        Add a reject entry to database

        :param identifier: str, the identifying unique string for this
                           observation
        :param pp_flag: bool, if True reject at the preprocessing level
        :param tel_flag: bool, if True reject at the telluric processing level
        :param rv_flag: bool, if True reject at the RV processing level
        :param used: int, if entry should be used - always 1 for use internally
        :param comment:

        :return: None - updates database
        """
        # fill insert dict
        insert_dict = dict()
        insert_dict['IDENTIFIER'] = drs_db.deal_with_null(identifier)
        insert_dict['PP_FLAG'] = drs_db.deal_with_null(pp_flag)
        insert_dict['TEL'] = drs_db.deal_with_null(tel_flag)
        insert_dict['RV'] = drs_db.deal_with_null(rv_flag)
        insert_dict['USED'] = drs_db.deal_with_null(used)
        insert_dict['DATE_ADDED'] = Time.now().iso
        insert_dict['COMMENT'] = drs_db.deal_with_null(comment)
        # ------------------------------------------------------------------
        # check that we are adding the correct columns (i.e. all columns
        #   are in database)
        self.check_columns(insert_dict)
        # add row to database
        self.database.add_row(insert_dict=insert_dict)

    def get_entries(self, columns: str = '*',
                    nentries: Union[int, None] = None,
                    condition: Union[str, None] = None,
                    ) -> Union[None, list, tuple, np.ndarray, pd.DataFrame]:
        """
        Get an entry from the reject database (can set columns to return, or
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
        # _ = display_func('get_entries', __NAME__, self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns)
        # ------------------------------------------------------------------
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
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
            entries = self.database.get(columns, **sql)
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
        colnames = self.database.colnames(columns)
        # if we have one column return a list
        if len(colnames) == 1:
            # return array for ease
            sql['return_array'] = True
            # do sql query
            entries = self.database.get(columns, **sql)
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
            entries = self.database.get(columns, **sql)
            # return pandas table
            return entries

    def remove_entries(self, condition: str):
        """
        Remove row(s) from a database

        :param condition: str, the sql WHERE condition for removing row(s) from
                          the database

        :return: None, operation on database
        """
        # set function
        # _ = display_func('remove_entries', __NAME__,
        #                  self.classname)
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with no database loaded
        if self.database is None:
            self.load_db()
        # remove entries
        self.database.delete_rows(condition=condition)


# =============================================================================
# Define class for astropy table as database
# =============================================================================
class PandasDBStorage:
    classname: str = 'PandasDBStorage'

    def __init__(self):
        """
        Constructs the Pandas database storage class
        """
        self.obs_paths = dict(OBS_PATHS)
        self.filedbs = dict(FILEDBS)

    @staticmethod
    def set(key: str, value: Any):
        """
        Setter function to store value of "key" globally

        :param key: str, the key to store
        :param value: Any, the value to store for key

        :return: None, updates global variable "key" with value (if found)
        """
        # set globals
        global OBS_PATHS
        global FILEDBS

        if key == 'obs_path':
            OBS_PATHS = value
        elif key == 'filedbs':
            FILEDBS = value

    def get(self, key: str) -> Any:
        """
        Getter function to get value of "key" from global store

        :param key: str, the key to get

        :return: Any, the value stored globally for "key"
        """
        if key == 'obs_paths':
            return OBS_PATHS
        elif key == 'filedbs':
            return FILEDBS
        else:
            emsg = 'Key "{0}" not found in {1}'
            raise KeyError(emsg.format(key, self.classname))

    @staticmethod
    def reset(key: Optional[str] = None, subkey: Optional[str] = None):
        """
        Resets "key" globally to default value / remove subkey

        :param key: str or None, the key to reset back to default value
        :param subkey: str or None, if set and subkey in one of our global
                       dictionaries remove this key instead of resetting
                       everything

        :return: None, resets the storage global variables
        """
        # set globals
        global OBS_PATHS
        global FILEDBS

        if key == 'obs_path':
            # if we have a sub key just delete this
            if subkey is not None and subkey in OBS_PATHS:
                del OBS_PATHS[subkey]
            # else reset entire thing
            else:
                OBS_PATHS = dict()
        elif key == 'filedbs':
            # if we have a sub key just delete this
            if subkey is not None and subkey in FILEDBS:
                del FILEDBS[subkey]
            # else reset entire thing
            else:
                FILEDBS = dict()
        # no key --> reset all
        if key is None:
            # if we have a sub key just delete this
            if subkey is not None:
                if subkey in OBS_PATHS:
                    del OBS_PATHS[subkey]
                if subkey in FILEDBS:
                    del FILEDBS[subkey]
            # else reset entire thing
            else:
                OBS_PATHS = dict()
                FILEDBS = dict()


class PandasLikeDatabase:
    def __init__(self, data: pd.DataFrame):
        """
        Construct a database just using a pandas dataframe stored in the memory

        can be used instead of a database (when we have a static database
        loading from a dataframe is more efficient and avoids extra reads of
        the database)

        :param data: pandas.DataFrame, the pandas dataframe - usually taken
                     from a call to a database
        """
        self.namespace = dict(data=data)
        self.tablename = 'data'

    def execute(self, command: str) -> pd.DataFrame:
        """
        How we run an sql query on a pandas database

        Note the table has to be in self.namespace

        i.e. "SELECT * FROM data" requires self.namespace['data'] = self.data

        :param command: str, the sql command to run
        :return:
        """
        return sqldf(command, self.namespace)

    def count(self, condition: str = None) -> int:
        """
        Proxy for the drs_database.database count method

        :param condition: Filter results using a SQL conditions string
                       -- see examples, and possibly this
                       useful tutorial:
                           https://www.sqlitetutorial.net/sqlite-where/.
                       If None, no results will be filtered out.

        :return: int, the count
        """
        # construct basic command SELECT COUNT(*) FROM {TABLE}
        command = "SELECT COUNT(*) FROM {}".format(self.tablename)
        # deal with condition
        if condition is not None:
            command += " WHERE {} ".format(condition)
        # run command
        df = self.execute(command)
        # return result
        return int(df.iloc[0])

    def get_index_entries(self, columns: str, condition: Optional[str] = None):
        """
        Proxy for index database get_entries method

        Currently only supports a columns and condition argument

        :param columns: str, the columns to return ('*' for all)
        :param condition: str or None, if set the SQL query to add
        :return:
        """
        # construct basic command SELECT {COLUMNS} FROM {TABLE}
        command = 'SELECT {0} FROM {1}'.format(columns, self.tablename)
        # deal with condition
        if condition is not None:
            command += " WHERE {} ".format(condition)
        # run command
        df = self.execute(command)
        # return the data frame
        return df

    def colnames(self, columns: str = '*') -> List[str]:
        """
        Return the list of column names

        Proxy for database.colnames

        :return: List of strings (the column names)
        """
        cnames = list(self.namespace['data'].columns)
        # if user requested all columns, return all columns
        if columns == '*':
            return cnames
        # deal with specifying columns (return just columns in database
        #   that match "columns"
        else:
            requested_columns = columns.split(',')
            # loop around requested columns and search for them in all columns
            outcolumns = []
            for rcol in requested_columns:
                if rcol.strip() in cnames:
                    outcolumns.append(rcol.strip())
            # return the output columns
            return outcolumns


# =============================================================================
# Define other database functionality
# =============================================================================
def get_google_sheet(params: ParamDict, sheet_id: str, worksheet: int = 0,
                     cached: bool = True) -> Table:
    """
    Load a google sheet from url using a sheet id (if cached = True and
    previous loaded - just loads from memory)

    :param params: ParamDict, parameter dictionary of constants
    :param sheet_id: str, the google sheet id
    :param worksheet: int, the worksheet id (defaults to 0)
    :param cached: bool, if True and previous loaded, loads from memory

    :return: Table, astropy table representation of google sheet
    """
    # set google cache table as global
    global GOOGLE_TABLES
    # set function name
    func_name = display_func('get_google_sheet', __NAME__)
    # construct url for worksheet
    url = GOOGLE_BASE_URL.format(sheet_id, worksheet)
    # deal with table existing
    if url in GOOGLE_TABLES and cached:
        return GOOGLE_TABLES[url]
    # get data using a request
    try:
        rawdata = requests.get(url)
    except Exception as e:
        # log error: Could not load table from url
        eargs = [url, type(e), str(e), func_name]
        WLOG(params, 'error', textentry('00-010-00009', args=eargs))
        return Table()
    # deal with no rows in table
    if '\n' not in rawdata.text:
        return Table()
    # convert rawdata input table
    with warnings.catch_warnings(record=True) as _:
        tries = 0
        while tries < 10:
            # try to open table
            try:
                table = Table.read(rawdata.text, format='ascii')
                break
            # if this fails try again (but with a limit
            except InconsistentTableError as _:
                tries += 1
                # lets wait a little bit to try again
                time.sleep(2)
            # deal with no rows in table - assume this always gives a
            #   FileNotFoundErorr
            except FileNotFoundError:
                table = Table()
                break
    # need to deal with too many tries
    if tries >= 10:
        # log error: Could not load table from url: (Tried 10 times)
        eargs = [url, func_name]
        WLOG(params, 'error', textentry('00-010-00010', args=eargs))
    # add to cached storage
    GOOGLE_TABLES[url] = table
    # return table
    return table


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
