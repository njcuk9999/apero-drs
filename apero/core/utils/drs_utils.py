#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO core utility and miscellaneous functionality

Created on 2020-10-2020-10-05 17:43

@author: cook

"""
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from apero.base import base
from apero.core import constants
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_database
from apero.core.core import drs_exceptions
from apero.core.core import drs_log
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_utils.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display func
display_func = drs_log.display_func
# get time object
Time = base.Time
# Get Logging function
WLOG = drs_log.wlog
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get parameter dictionary
ParamDict = constants.ParamDict
# get the binary dictionary
BinaryDict = base_class.BinaryDict
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# get databases
FileIndexDatabase = drs_database.FileIndexDatabase
LogDatabase = drs_database.LogDatabase
# get header classes from io.drs_fits
Header = drs_fits.Header
FitsHeader = drs_fits.fits.Header


# =============================================================================
# Define Classes
# =============================================================================
class RecipeLog:
    """
    Recipe log class - to store recipe log data
    """

    def __init__(self, name: str, sname: str, params: ParamDict, level: int = 0,
                 logger: Union[None, drs_log.Logger] = None,
                 database: Union[LogDatabase, None] = None,
                 flags: Optional[BinaryDict] = None):
        """
        Constructor for the recipe log

        :param name: str, the recipe name this recipe log belong to
        :param params: ParamDict, the constants parameter dictionary
        :param level: int, the level of this log 0 is root, higher numbers are
                      children of the root
        :param logger: if set the WLOG (Logger) instance to use
        """
        # set class name
        self.class_name = 'RecipeLog'
        # set function name
        _ = drs_misc.display_func('__init__', __NAME__, self.class_name)
        # get a database instance
        if isinstance(database, LogDatabase):
            self.logdbm = database
        else:
            self.logdbm = LogDatabase(params)
            self.logdbm.load_db()
        # get the recipe name
        self.name = str(name)
        self.sname = str(sname)
        # the block kind (raw/tmp/red etc)
        self.block_kind = 'None'
        # the default logging absolute path
        self.defaultpath = str(params['DRS_DATA_MSG_FULL'])
        # the log fits file name (log.fits)
        self.logfitsfile = str(params['DRS_LOG_FITS_NAME'])
        # the recipe input directory from recipe.inputdir
        self.inputdir = str(params['INPATH'])
        # the recipe output directory from recipe.outputdir
        self.outputdir = str(params['OUTPATH'])
        # the parameter dictionary of constants
        self.params = params
        # ---------------------------------------------------------------------
        self.no_log = False
        # deal with no save --> no log
        if 'INPUTS' in params:
            if 'NOSAVE' in params['INPUTS']:
                if params['INPUTS']['NOSAVE']:
                    self.no_log = True
        # ---------------------------------------------------------------------
        # the Logger instances (or None)
        self.wlog = logger
        # set the pid
        self.pid = str(params['PID'])
        # set the human time
        self.htime = str(params['DATE_NOW'])
        self.utime = Time(self.htime).unix
        self.start_time = str(params['DATE_NOW'])
        self.end_time = 'None'
        self.log_start = 'None'
        self.log_end = 'None'
        # set the group name
        self.group = str(params['DRS_GROUP'])
        # set the night name directory (and deal with no value)
        if 'OBS_DIR' not in params:
            self.obs_dir = 'other'
        elif params['OBS_DIR'] in [None, 'None', '']:
            self.obs_dir = 'other'
        else:
            self.obs_dir = str(params['OBS_DIR'])
        # set the log file name (just used to save log directory)
        #  for log table entry
        self.log_file = 'Not Set'
        # set the plot file name (just used to save the plot directory) for
        #   log table entry
        self.plot_dir = 'Not Set'
        # set the inputs
        self.args = ''
        self.kwargs = ''
        self.skwargs = ''
        self.runstring = ''
        self.recipe_type = str(params['DRS_RECIPE_TYPE'])
        self.recipe_kind = str(params['DRS_RECIPE_KIND'])
        self.program_name = str(params['DRS_USER_PROGRAM'])
        # set that recipe started
        self.started = True
        # set the iteration
        self.set = []
        # set the level (top level=0)
        self.level = level
        # set the level criteria
        self.level_criteria = ''
        self.level_iteration = 0
        # set qc
        self.passed_qc = False
        # set qc paarams
        self.qc_string = ''
        self.qc_name = ''
        self.qc_value = ''
        self.qc_pass = ''
        self.qc_logic = ''
        # keep the flags
        self.flags = flags
        self.flagnum = 0
        self.flagstr = ''
        # set flag: in parallel
        if 'INPUTS' in params:
            in_parallel = params['INPUTS'].get('PARALLEL', False)
            self.flags['IN_PARALLEL'] = in_parallel
        # set flag: running
        self.flags['RUNNING'] = True
        # set the errors
        self.errors = ''
        # get system stats at start
        stats = drs_misc.get_system_stats()
        # system stats
        self.ram_usage_start = stats['ram_used']
        self.ram_usage_end = -1
        self.ram_total = stats['raw_total']
        self.swap_usage_start = stats['swap_used']
        self.swap_usage_end = -1
        self.swap_total = stats['swap_total']
        self.cpu_usage_start = stats['cpu_percent']
        self.cpu_usage_end = -1
        self.cpu_num = stats['cpu_total']

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        String representation of this class
        :return:
        """
        # set function name
        _ = drs_misc.display_func('__str__', __NAME__, self.class_name)
        # return string representation of RecipeLOg
        return 'RecipeLog[{0}]'.format(self.name)

    def copy(self, rlog: 'RecipeLog'):
        """
        Copy another RecipeLog over this one

        :param rlog: Another RecipeLog instance
        :return:
        """
        # set function name
        _ = drs_misc.display_func('copy', __NAME__, self.class_name)
        # copy parameters
        self.name = str(rlog.name)
        self.sname = str(rlog.sname)
        self.block_kind = str(rlog.block_kind)
        self.recipe_type = str(rlog.recipe_type)
        self.recipe_kind = str(rlog.recipe_kind)
        self.pid = str(rlog.pid)
        self.htime = str(rlog.htime)
        self.utime = str(rlog.utime)
        self.group = str(rlog.group)
        self.obs_dir = str(rlog.obs_dir)
        self.defaultpath = str(rlog.defaultpath)
        self.inputdir = str(rlog.inputdir)
        self.outputdir = str(rlog.outputdir)
        self.log_file = str(rlog.log_file)
        self.plot_dir = str(rlog.plot_dir)
        self.runstring = str(rlog.runstring)
        self.args = str(rlog.args)
        self.kwargs = str(rlog.kwargs)
        self.skwargs = str(rlog.skwargs)
        self.start_time = str(rlog.start_time)
        self.end_time = str(rlog.end_time)
        self.level_criteria = str(rlog.level_criteria)
        self.passed_qc = bool(rlog.passed_qc)
        self.qc_string = str(rlog.qc_string)
        self.qc_name = str(rlog.qc_name)
        self.qc_value = str(rlog.qc_value)
        self.qc_pass = str(rlog.qc_pass)
        self.qc_logic = str(rlog.qc_logic)
        self.flags = rlog.flags.copy()
        self.flagnum = int(rlog.flagnum)
        self.flagstr = str(rlog.flagstr)
        self.errors = str(rlog.errors)
        self.ram_usage_start = float(rlog.ram_usage_start)
        self.ram_usage_end = float(rlog.ram_usage_end)
        self.ram_total = float(rlog.ram_total)
        self.swap_usage_start = float(rlog.swap_usage_start)
        self.swap_usage_end = float(rlog.swap_usage_end)
        self.swap_total = float(rlog.swap_total)
        self.cpu_usage_start = float(rlog.cpu_usage_start)
        self.cpu_usage_end = float(rlog.cpu_usage_end)
        self.cpu_num = int(rlog.cpu_num)

    def set_log_file(self, logfile: Union[str, Path]):
        """
        Set the log file

        :param logfile: str, the log file
        :return:
        """
        # set function name
        _ = drs_misc.display_func('set_log_file', __NAME__,
                                  self.class_name)
        # set the log file
        self.log_file = str(logfile)

    def set_plot_dir(self, params: ParamDict,
                     location: Union[str, Path, None] = None,
                     write: bool = True):
        """
        Set the plot directory for RecipeLog and all children

        :param params: ParamDict, the constants parameter dictionary
        :param location: str or Path, the path of the plot directory
        :param write: bool, if True update the log file
        :return:
        """
        # set function name
        _ = drs_misc.display_func('set_plot_dir', __NAME__,
                                  self.class_name)
        # deal with location being set
        if location is not None:
            self.plot_dir = str(location)
            # update children
            if len(self.set) != 0:
                for child in self.set:
                    child.set_plot_dir(params, location, write=False)
        else:
            self.plot_dir = 'None'
        # whether to write (update) recipe log file
        if write:
            self.write_logfile()

    def add_level(self, params: ParamDict, key: str, value: Any,
                  write: bool = True) -> 'RecipeLog':
        """
        Add a child level to the recipe log i.e. inside a for loop we may want
        one log entry for each iteration (level is incremented - root = 0)

        :param params: ParamDict, the constants parameter dictionary
        :param key: str, text describing this new level (i.e. fiber or
                    iteration) converted to key = value
                    e.g.  key: fiber
                              we have a level with the following:
                              fiber = A
                              fiber = B
                              fiber = C

        :param value: Any (must be convertable to string) the value of this
                      iterations key  i.e. key = value
        :param write: bool, if True writes to RecipeLog fits file
        :return: RecipeLog, the child instance of the parent RecipeLog
                 all children are stored inside a parent
        """
        # set function name
        # _ = drs_misc.display_func('add_level', __NAME__, self.class_name)

        # get new level
        level = self.level + 1
        # create new log
        newlog = RecipeLog(self.name, self.sname, params, level=level,
                           logger=self.wlog, database=self.logdbm,
                           flags=self.flags)
        # copy from parent
        newlog.copy(self)
        # set log start time
        newlog.log_start = str(Time.now().iso)
        # record level criteria
        newlog.level_criteria += '{0}={1} '.format(key, value)
        # update the level iteration
        newlog.level_iteration = len(self.set)
        # add newlog to set
        self.set.append(newlog)
        # ---------------------------------------------------------------------
        # whether to write (update) recipe log file
        if write:
            self.write_logfile()
        # return newlog (for use)
        return newlog

    def add_qc(self,
               qc_params: Tuple[List[str], List[Any], List[str], List[int]],
               passed: Union[int, bool, str], write: bool = True):
        """
        Add the quality control criteria (stored in qc_params) to the recipe
        log

        :param qc_params: the quality control storage, constists of
                          qc_names, qc_values, qc_logic, qc_pass where
                          qc_names is a list of variable names,
                          qc_values is a list of value for each variable
                          qc_logic is the pass/fail logic for variable
                          qc_pass is either 1 for passed qc or 0 for failure
        :param passed: int/bool/str if 1 or True or '1' all quality control was
                       passed (this is stored as a column in log database)
        :param write: bool, if True write parameters to log database
        :return:
        """
        # set function name
        _ = drs_misc.display_func('add_qc', __NAME__, self.class_name)
        # update passed
        if passed in [1, True, '1']:
            self.passed_qc = True
        else:
            self.passed_qc = False
        # update qc params
        qc_names, qc_values, qc_logic, qc_pass = qc_params
        for it in range(len(qc_names)):
            # deal with no qc set
            if qc_names[it] in ['None', None, '']:
                continue

            # set up qc pass string
            if qc_pass[it]:
                pass_str = 'PASSED'
            else:
                pass_str = 'FAILED'
            # deal with qc set
            qargs = [qc_names[it], qc_values[it], qc_logic[it], pass_str]
            self.qc_string += '{0}={1} [{2}] {3} ||'.format(*qargs)
            self.qc_name += '{0}||'.format(qc_names[it])
            self.qc_value += '{0}||'.format(qc_values[it])
            self.qc_logic += '{0}||'.format(qc_logic[it])
            self.qc_pass += '{0}||'.format(qc_pass[it])

        # whether to write (update) recipe log file
        if write:
            self.write_logfile()

    def no_qc(self, write: bool = True):
        """
        Writes that quality control passed (there were no quality control)

        :param write: bool, whether to write to log database
        :return:
        """
        # set function name
        _ = drs_misc.display_func('no_qc', __NAME__, self.class_name)
        # set passed_qc to True (no qc means automatic pass)
        self.passed_qc = True
        # all children must also not have qc
        instances = self.get_children()
        # loop around instances
        for inst in instances:
            inst.passed_qc = True
        # whether to write (update) recipe log file
        if write:
            self.write_logfile()

    def add_error(self, errortype: Union[Exception, str],
                  errormsg: str, write: bool = True):
        """
        Add an error (exception) to the database in the errors column
        errors are separate by two ||

            ErrorType: ErrorMessage ||

        :param errortype: Exception or string, the error exception or a string
                          representation of it
        :param errormsg: str, the error message to store
        :param write: bool, if True writes to the log database
        :return:
        """
        # set function name
        _ = drs_misc.display_func('add_error', __NAME__, self.class_name)
        # add errors in form ErrorType: ErrorMessage ||
        self.errors += '"{0}":"{1}"||'.format(errortype, errormsg)
        # whether to write (update) recipe log file
        if write:
            self.write_logfile()

    def get_children(self) -> List['RecipeLog']:
        """
        Get all child classes attached to this instance

        :return:
        """
        # if we have a set then we look for children
        if len(self.set) != 0:
            children = []
            # loop around children and check for children of children
            for child in self.set:
                children += child.get_children()
            # return this list of instances
            return children
        # if we don't have a set we just return ourself (weirdly we are one of
        #   our children in this definition)
        else:
            return [self]

    def end(self, write: bool = True, success: bool = True):
        """
        Add the row that says recipe finished correctly to database

        :param write: bool, whether to write to log database
        :param success: bool, if True adds an ended flag
        :return:
        """
        # set function name
        _ = drs_misc.display_func('end', __NAME__, self.class_name)
        # add the end time
        end_time = str(Time.now().iso)
        # both log end (for child) and full end time are updated
        self.log_end = end_time
        self.end_time = end_time
        # set the ended parameter to True
        if success:
            self.flags['ENDED'] = True
        # set the running parameter to False (we have finished whether
        #   successful or not)
        self.flags['RUNNING'] = False
        # get system stats at end
        stats = drs_misc.get_system_stats()
        self.ram_usage_end = stats['ram_used']
        self.swap_usage_end = stats['swap_used']
        self.cpu_usage_end = stats['cpu_percent']
        # whether to write (update) recipe log file
        if write:
            self.write_logfile()

    def write_logfile(self):
        """
        Write to the log database

        :return: None, unless return_values is True
        """
        # set function name
        _ = drs_misc.display_func('write_logfile', __NAME__,
                                  self.class_name)
        # do not write log if we have the no log flag
        if self.no_log:
            return
        # ---------------------------------------------------------------------
        # remove all entries with this pid
        self.logdbm.remove_pids(self.pid)
        # ---------------------------------------------------------------------
        # add instances (if we have a set use the set otherwise just add
        #    your self)
        instances = self.get_children()
        # loop around instances
        for inst in instances:
            # get utime
            utime = float(Time(inst.htime).unix)
            # convert flags before writing
            inst.convert_flags()
            # add entries
            self.logdbm.add_entries(recipe=inst.name, sname=inst.sname,
                                    block_kind=inst.block_kind,
                                    recipe_type=inst.recipe_type,
                                    recipe_kind=inst.recipe_kind,
                                    program_name=inst.program_name,
                                    pid=inst.pid, htime=inst.htime,
                                    unixtime=utime, group=inst.group,
                                    level=inst.level,
                                    sublevel=inst.level_iteration,
                                    levelcrit=inst.level_criteria,
                                    inpath=inst.inputdir,
                                    outpath=inst.outputdir,
                                    obs_dir=inst.obs_dir,
                                    logfile=inst.log_file,
                                    plotdir=inst.plot_dir,
                                    runstring=inst.runstring, args=inst.args,
                                    kwargs=inst.kwargs, skwargs=inst.skwargs,
                                    start_time=inst.start_time,
                                    # end time has to be taken from parent
                                    end_time=self.end_time,
                                    started=inst.started,
                                    passed_all_qc=inst.passed_qc,
                                    qc_string=inst.qc_string,
                                    qc_names=inst.qc_name,
                                    qc_values=inst.qc_value,
                                    qc_logic=inst.qc_logic,
                                    qc_pass=inst.qc_pass,
                                    errors=inst.errors,
                                    ended=int(inst.flags['ENDED']),
                                    flagnum=inst.flagnum,
                                    flagstr=inst.flagstr,
                                    used=1,
                                    ram_usage_start=inst.ram_usage_start,
                                    ram_usage_end=inst.ram_usage_end,
                                    ram_total=inst.ram_total,
                                    swap_usage_start=inst.swap_usage_start,
                                    swap_usage_end=inst.swap_usage_end,
                                    swap_total=inst.swap_total,
                                    cpu_usage_start=inst.cpu_usage_start,
                                    cpu_usage_end=inst.cpu_usage_end,
                                    cpu_num=inst.cpu_num,
                                    log_start=inst.log_start,
                                    log_end=inst.log_end)

    def _make_row(self) -> OrderedDict:
        """
        Make a row in the RecipeLog file

        :return: OrderedDict the row entry where each key is a column name
        """
        # set function name
        _ = drs_misc.display_func('_make_row', __NAME__, self.class_name)
        # convert flags
        self.convert_flags()
        # set rows
        row = OrderedDict()
        row['RECIPE'] = self.name
        row['BLOCK_KIND'] = self.block_kind
        row['RECIPE_TYPE'] = self.recipe_type
        row['RECIPE_KIND'] = self.recipe_kind
        row['PID'] = self.pid
        row['HTIME'] = self.htime
        row['GROUPNAME'] = self.group
        row['LEVEL'] = self.level
        row['SUBLEVEL'] = self.level_iteration
        row['LEVEL_CRIT'] = self.level_criteria
        row['INPATH'] = self.inputdir
        row['OUTPATH'] = self.outputdir
        row['OBS_DIR'] = self.obs_dir
        row['LOGFILE'] = self.log_file
        row['PLOTDIR'] = self.plot_dir
        row['RUNSTRING'] = self.runstring
        # add inputs
        row['ARGS'] = self.args
        row['KWARGS'] = self.kwargs
        row['SKWARGS'] = self.skwargs
        # add timings
        row['START_TIME'] = self.start_time
        row['END_TIME'] = self.end_time
        # add whether recipe started
        row['STARTED'] = self.started
        # add whether all qc passed
        row['PASSED_ALL_QC'] = self.passed_qc
        # qc columns
        row['QC_STRING'] = self.qc_string.strip().strip('||').strip()
        row['QC_NAMES'] = self.qc_name.strip().strip('||').strip()
        row['QC_VALUES'] = self.qc_value.strip().strip('||').strip()
        row['QC_LOGIC'] = self.qc_logic.strip().strip('||').strip()
        row['QC_PASS'] = self.qc_pass.strip().strip('||').strip()
        # add errors
        row['ERRORMSGS'] = self.errors
        # add flags
        row['FLAGNUM'] = self.flagnum
        row['FLAGSTR'] = self.flagstr
        # add system stats
        row['RAM_USAGE_START'] = self.ram_usage_start
        row['RAM_USAGE_END'] = self.ram_usage_end
        row['RAW_TOTAL'] = self.ram_total
        row['SWAP_USAGE_START'] = self.swap_usage_start
        row['SWAP_USAGE_END'] = self.swap_usage_end
        row['SWAP_TOTAL'] = self.swap_total
        row['CPU_USAGE_START'] = self.cpu_usage_start
        row['CPU_USAGE_END'] = self.cpu_usage_end
        row['CPU_NUM'] = self.cpu_num
        row['LOG_START'] = self.log_start
        row['LOG_END'] = self.log_end
        # return row
        return row

    def update_flags(self, **kwargs: bool):
        """
        Update the log flags

        :param kwargs: str, the keys to update
        :return:
        """
        # loop around flags and update the required ones
        for kwarg in kwargs:
            self.flags[kwarg] = bool(kwargs[kwarg])
        # convert flags for logging
        self.convert_flags()
        # whether to write (update) recipe log file
        self.write_logfile()

    def convert_flags(self):
        """
        Convert flags from a list to a string (keys separated by |)
        and decode the flag number from the individual flags

        :return: None, updates flagnum and flagstr
        """
        self.flagnum = self.flags.decode()
        self.flagstr = '|'.join(list(self.flags.keys()))

    def get_rows(self) -> List[OrderedDict]:
        """
        Get all rows for a entry (including all rows from the child Recipelog
        entries

        :return:
        """
        # set function name
        _ = drs_misc.display_func('_get_rows', __NAME__, self.class_name)
        # set rows storage
        rows = []
        # case where we have no sets
        if len(self.set) == 0:
            rows.append(self._make_row())
        else:
            # else we have children
            for child in self.set:
                rows += child.get_rows()
        # return rows
        return rows

    # complex param table return
    ParamTableReturn = Tuple[List[str], List[str], list, List[str], List[str],
                             List[int]]

    def get_param_table(self) -> ParamTableReturn:
        """
        Make lists of the names, kinds, values, sources, descriptions and counts
        for param table addition

        Note columns should be rlog.{LOG_DB_COLUMN}

        where LOG_DB_COLUMN is lowercase and is checked at the end

        :return: tuple of lists (name/kinds/values/sources/descriptions/counts)
        """
        # set function name
        func_name = display_func('get_param_table', __NAME__, self.class_name)
        # storage arrays
        names = []
        param_kinds = []
        values = []
        source = []
        description = []
        count = []
        # get log keys
        ldb_cols = constants.pload().LOG_DB_COLUMNS()
        log_keys = list(ldb_cols.altnames)
        log_comments = list(ldb_cols.comments)
        # convert the flags
        self.convert_flags()
        # ---------------------------------------------------------------------
        # define the values for each column (must be same length as
        #    LOG_DB_COLUMNS
        log_values = [self.name, self.sname, self.block_kind,
                      self.recipe_type, self.recipe_kind, self.program_name,
                      self.pid, self.htime, float(Time(self.htime).unix),
                      self.group, self.level, self.level_iteration,
                      self.level_criteria, self.inputdir, self.outputdir,
                      self.obs_dir, self.log_file, self.plot_dir,
                      self.runstring, self.args, self.kwargs, self.skwargs,
                      self.start_time, self.end_time, self.started,
                      self.passed_qc, self.qc_string,
                      self.qc_name, self.qc_value, self.qc_logic, self.qc_pass,
                      self.errors, int(self.flags['ENDED']),
                      self.flagnum, self.flagstr, 1, self.ram_usage_start,
                      self.ram_usage_end, self.ram_total, self.swap_usage_start,
                      self.swap_usage_end, self.swap_total,
                      self.cpu_usage_start, self.cpu_usage_end, self.cpu_num,
                      self.log_start, self.log_end]
        # ---------------------------------------------------------------------
        # loop around all rows and add to params
        for it in range(len(log_keys)):
            # ended will be zero as we are inside a recipe
            #   for the rlog table we assume the recipe finished
            #   (otherwise we would have to update the header at some point
            #   after the recipe finished)
            if log_keys[it].endswith('ENDED'):
                value = 1
            else:
                value = log_values[it]
            # set the name (from log key)
            names.append(log_keys[it])
            # set the parameter kind (rlog)
            param_kinds.append('rlog')
            # set the value
            values.append(value)
            # set the source of the value
            source.append(func_name)
            # set the description using the log comments
            description.append(log_comments[it])
            # set the count to 1 (always 1)
            count.append(1)
        # ---------------------------------------------------------------------
        # return lists
        return names, param_kinds, values, source, description, count


# =============================================================================
# Define functions
# =============================================================================
# complex typing for update_index_db
FileType = Union[List[Path], Path, List[str], str, None]


def update_index_db(params: ParamDict, block_kind: str,
                    includelist: Union[List[str], None] = None,
                    excludelist: Union[List[str], None] = None,
                    filename: FileType = None,
                    suffix: str = '',
                    findexdbm: Union[FileIndexDatabase, None] = None
                    ) -> FileIndexDatabase:
    """
    Block function to update index database

    (if params['INPUTS']['PARALLEL'] is True does not update database).

    :param params: ParamDict, the parameter dictionary of constants
    :param block_kind: str, the block kind (raw/tmp/red)
    :param includelist: list of strings or None, if set the observation
                        directories to include in update
    :param excludelist: list of strings or None, if set the observation
                        directories to exclude in update
    :param filename: list of paths, path, list or strings or string or None,
                     if set the filename or filenames to update
    :param suffix: str, the suffix (i.e. extension of filenames) - filters
                   to only set these files
    :param findexdbm: IndexDatabase instance or None, if set will not reload
                     index database if None will load index database

    :return: updated or loaded index database unless
             params['INPUTS']['PARALLEL'] is True
    """
    # -------------------------------------------------------------------------
    # load the index database
    if findexdbm is None:
        findexdbm = FileIndexDatabase(params)
    findexdbm.load_db()
    # -------------------------------------------------------------------------
    # check whether we are updating the index
    update_index = True
    if 'INPUTS' in params:
        if params['INPUTS'].get('PARALLEL', False):
            update_index = False
    if not update_index:
        return findexdbm
    # -------------------------------------------------------------------------
    # deal with white list and black list
    # no include dirs
    if drs_text.null_text(includelist, ['None', 'All', '']):
        include_dirs = None
    elif includelist in [['All'], ['None'], ['']]:
        include_dirs = None
    # else use include list dirs
    else:
        include_dirs = list(includelist)
    # no exclude dirs
    if drs_text.null_text(excludelist, ['None', 'All', '']):
        exclude_dirs = None
    elif excludelist in [['All'], ['None'], ['']]:
        exclude_dirs = None
    # else exclude dirs
    else:
        exclude_dirs = list(excludelist)
    # -------------------------------------------------------------------------
    # update index database with raw files
    findexdbm.update_entries(block_kind=block_kind,
                             exclude_directories=exclude_dirs,
                             include_directories=include_dirs,
                             filename=filename, suffix=suffix)
    # -------------------------------------------------------------------------
    # we need to reset some globally stored variables - these should be
    #   recalculated when used
    store = drs_database.PandasDBStorage()
    store.reset(subkey=block_kind)
    # return the database
    return findexdbm


def find_files(params: ParamDict, block_kind: str, filters: Dict[str, str],
               columns='ABSPATH',
               findexdbm: Union[FileIndexDatabase, None] = None
               ) -> Union[np.ndarray, pd.DataFrame]:
    """
    Find a type of files from the file index database using a set of filters

    :param params: ParamDict, the parameter dictionary of constants
    :param block_kind: str, the block kind (raw/tmp/red etc)
    :param filters: dict, the column names within the file index database
                    with which to filter by, the values of the dictionary
                    filter the database. filters are used with "AND" logic
    :param columns: str, the columns to return from the database (can use
                    '*' for all, if a single column is given a numpy array
                    if returned otherwise a pandas dataframe is returned
    :param findexdbm: FileIndexDatabase class or None, pass a current
                      file index database class (otherwise reloaded)

    :return: if one column a numpy 1D array is returned, otherwise a pandas
             dataframe is returned with all the requested columns
    """
    # update database
    update_index = True
    if 'PARALLEL' in params:
        if params['INPUTS']['PARALLEL']:
            update_index = False
    # update index database if required
    if update_index:
        findexdbm = update_index_db(params, block_kind=block_kind,
                                    findexdbm=findexdbm)
    # get columns
    colnames = findexdbm.database.colnames('*')
    # get file list using filters
    condition = 'BLOCK_KIND="{0}"'.format(block_kind)
    # loop around filters
    for fkey in filters:
        if fkey in colnames:
            _filters = filters[fkey]
            # make sure filter is a list
            if isinstance(_filters, str):
                _filters = [_filters]
            # loop around filter elements and combine with "OR"
            subconditions = []
            for _filter in _filters:
                # make sure filter is stripped
                _filter = _filter.strip()
                # add to subconditions
                subconditions.append('{0}="{1}"'.format(fkey, _filter))
            # add subconditions to condition
            condition += ' AND ({0})'.format(' OR '.join(subconditions))
    # get columns for this condition
    return findexdbm.get_entries(columns, block_kind=block_kind,
                                 condition=condition)


def uniform_time_list(times: Union[List[float], np.ndarray], number: int
                      ) -> np.ndarray:
    """
    Create a very uniformly distributed list of times (distributed uniformly in
    time goes. Takes the full times vector and cuts it down list of positions
    (length "number") that are uniform in time

    :param times: list or numpy 1D array, a 1D vector of times matching the
    :param number: int, the number elements to have after cut

    :return: np.ndarray, mask, True where time should be used
    """
    # if we have less than the required number of files return a mask of all
    #    files
    if len(times) <= number:
        return np.ones_like(times).astype(bool)
    # convert times to numpy array
    times = np.array(times)
    # copy the times to new vector
    times2 = times[np.argsort(times)]
    # loop around until we have N files in times2
    while len(times2) > number:
        # work out the difference in times between previous and next times
        dt1 = np.abs(times2 - np.roll(times2, 1))
        dt2 = np.abs(times2 - np.roll(times2, -1))
        # find all times larger before than after
        dmask = dt2 < dt1
        # push values from before to after if smaller
        dt1[dmask] = dt2[dmask]
        # remove smallest delta time
        times2 = np.delete(times2, np.argmin(dt1))
    # create a mask of positions of times in times2
    mask = np.array(np.in1d(times, times2))
    # return the mask
    return mask


def display_flag(params: ParamDict):
    """
    Print out the binary flags used throughout the logging process

    :param params: ParamDict, parameter dictionary of constants

    :return: None, prints out flags using logger
    """
    # get inputs
    inputs = params['INPUTS']
    null_text = ['None', '', 'Null']
    # flag mode
    cond1 = drs_text.null_text(inputs.get('RECIPE', None), null_text)
    cond2 = drs_text.null_text(inputs.get('FLAGNUM', None), null_text)
    # deal with recipe or flagnum being None
    if cond1 or cond2:
        return
    # get the recipe name (or short name)
    recipe = str(params['INPUTS']['recipe'].replace('.py', ''))
    # get the flag number
    flagnum = params['INPUTS']['flagnum']
    # print progress
    WLOG(params, '', 'Flag mode: {0}[{1}]'.format(recipe, flagnum))
    # load pseudo constants
    pconst = constants.pload()
    # get the recipe module
    rmod = pconst.RECIPEMOD().get()
    # get binary flags for recipe
    srecipes = rmod.recipes
    srecipe = None
    found = False
    # find recipe in recipes
    for srecipe in srecipes:
        # remove py from recipe name
        rname = srecipe.name.replace('.py', '')
        rname = rname.replace(__INSTRUMENT__.lower(), '')
        rname = rname.strip('_')
        # test recipe and short name
        cond3 = recipe.upper() == rname.upper()
        cond4 = recipe.upper() == srecipe.shortname.upper()
        # if cond 3 or cond 4 we have found our recipe
        if cond3 or cond4:
            found = True
            break
    # deal with recipe not being found
    if not found:
        WLOG(params, 'warning', 'Invalid "recipe" argument.')
        return
    # get binary flags
    flags = srecipe.flags
    # deal with non-integer
    if not isinstance(flagnum, int):
        WLOG(params, 'warning', 'Invalid flag number (must be int).')
    # encode the given number
    flags.encode(flagnum)
    # print the recipe name
    WLOG(params, '', 'recipe = {0}'.format(srecipe.name))
    # print the flags
    for flag in flags:
        WLOG(params, '', '\t{0:20s}: {1}'.format(flag, flags[flag]))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
