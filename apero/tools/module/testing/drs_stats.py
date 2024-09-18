#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs stats

Module to compute stats on the drs

Created on 2021-12-06

@author: cook
"""
import glob
import os
import re
import string
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from astropy.table import Table
from pandasql import sqldf

from apero.base import base
from apero.core.constants import param_functions
from apero.core import math as mp
from apero.core.base import drs_base_classes as base_class, drs_text, drs_misc
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_log_stats.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get astropy time
Time = base.Time
# get tqdm
tqdm = base.tqdm_module()
# Get Logging function
WLOG = drs_log.wlog
ParamDict = param_functions.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
# define index columns to get
FINDEX_COLS = ['FILENAME', 'OBS_DIR', 'BLOCK_KIND', 'KW_MID_OBS_TIME',
               'INFILES', 'KW_OUTPUT', 'KW_DPRTYPE']
# regex code for locating errors
REGEX_ERROR_CODE = r'E\[\d\d-\d\d\d-\d\d\d\d\d\]'
# apero processing code for printing error summary entry
REPORT_ERROR_CODE = 'W[40-503-00019]'
# apero code for unhandled error
UNHANDLED_ERROR_CODE = 'E[01-010-00001]'


# =============================================================================
# Define classes
# =============================================================================
class LogEntry:
    def __init__(self, pid: str, dataframe: pd.DataFrame):
        self.pid = str(pid)
        # fill out data
        self.dataframe = dataframe
        self.namespace = dict(data=dataframe)
        self.data = None
        self.index = None
        # define properties
        self.recipe_name = 'None'
        self.shortname = 'None'
        self.block_kind = 'None'
        self.recipe_type = 'None'
        self.recipe_kind = 'None'
        self.log_file = 'None'
        self.runstring = 'None'
        # get the mjd mid
        self.mjdmid = np.nan
        self.obs_dir = 'None'
        self.infiles = []
        self.outfiles = []
        self.outtypes = []
        self.dprtypes = []
        # timing variables
        self.start_time = np.nan
        self.end_time = np.nan
        self.duration = np.nan
        # flag for valid log entry
        self.has_index = False
        self.is_valid = False
        self.is_valid_for_timing = False
        self.is_valid_for_qc = False
        # set sub level criteria
        self.criteria = []
        # qc criteria (for each sub level)
        self.passed = dict()
        self.qc_names = dict()
        self.qc_values = dict()
        self.qc_passes = dict()
        self.qc_logics = dict()
        # running / ended / error criteria
        self.running = dict()
        self.ended = dict()
        self.errormsgs = dict()

    def __str__(self) -> str:
        return 'LogEntry[{0}|{1}]'.format(self.recipe_name, self.pid)

    def __repr__(self) -> str:
        return self.__str__()

    def get_attributes(self, params: ParamDict, mode: str,
                       idataframe: pd.DataFrame):
        """
        Get attributes from dataframe for this object
        :return:
        """
        # get data for this pid
        self.data = self.dataframe[self.dataframe['PID'] == self.pid]
        # deal with no data
        if len(self.data) == 0:
            return
        # get shared properties
        self.recipe_name = self.data.iloc[0]['RECIPE']
        self.shortname = self.data.iloc[0]['SHORTNAME']
        self.block_kind = self.data.iloc[0]['BLOCK_KIND']
        self.recipe_type = self.data.iloc[0]['RECIPE_TYPE']
        self.recipe_kind = self.data.iloc[0]['RECIPE_KIND']
        self.log_file = self.data.iloc[0]['LOGFILE']
        self.runstring = self.data.iloc[0]['RUNSTRING']

        if mode == 'index':
            # cross-match with index database
            self.index = _index_database_crossmatch(idataframe, self.pid)
            # add index linked parameters
            if len(self.index) > 0:
                # get the mjd mid
                self.mjdmid = self.index['KW_MID_OBS_TIME'].mean()
                # flag that we have index
                self.has_index = True
                # get the observation directories (assume all entries equal)
                self.obs_dir = self.index['OBS_DIR'].iloc[0]
                # get the in files (assume all entries equal)
                raw_infiles = self.index['INFILES'].iloc[0]
                if isinstance(raw_infiles, str):
                    self.infiles = self.index['INFILES'].iloc[0].split('|')
                # get out files
                self.outfiles = np.array(self.index['FILENAME'])
                # get the output file type
                self.outtypes = np.array(self.index['KW_OUTPUT'])
                # get the DPRTYPE
                self.dprtypes = np.array(self.index['KW_DPRTYPE'])
            else:
                self.has_index = False
        else:
            self.has_index = False

        # check if we are dealing with a recipe (ignore others)
        if self.recipe_type != 'recipe':
            return
        # get timing criteria
        if mode == 'timing':
            # get raw start and end time from data table
            rawstart = self.data.iloc[0]['START_TIME']
            rawend = self.data.iloc[0]['END_TIME']
            # try to get duration
            try:
                # convert start time to a time
                if not drs_text.null_text(rawstart, ['None', 'Null', '']):
                    self.start_time = Time(rawstart).unix
                else:
                    self.start_time = np.nan
                # convert end time to a time
                if not drs_text.null_text(rawend, ['None', 'Null', '']):
                    self.end_time = Time(rawend).unix
                else:
                    self.end_time = np.nan
                # work out duration
                self.duration = self.end_time - self.start_time
                # only keep values which are finite
                if np.isfinite(self.duration):
                    self.is_valid = True
                    self.is_valid_for_timing = True
            except Exception as e:
                emsg = ('TIMING ERROR PID {0}\n\tstart_time={1}'
                        '\n\tend_time={2}\n\t{3}: {4}')
                eargs = [self.pid, rawstart, rawend, type(e), str(e)[:84]]
                WLOG(params, 'warning', emsg.format(*eargs))
                # make sure this target is not valid
                self.is_valid = False
                self.is_valid_for_timing = False

        elif mode == 'qc':
            # if we don't have index can't do qc (need outputs for qc)
            # if not self.has_index:
            #     self.is_valid_for_qc = False
            #     return
            try:
                # get sub level criteria and remove static variables
                subcriteria = _sort_sublevel(self.data)
                self.criteria = list(subcriteria)
                # get qc/run/error criteria
                # must loop around rows
                for row in range(len(self.data)):
                    # get this rows datas
                    row_data = self.data.iloc[row]
                    # get sub level
                    sublevel = subcriteria[row]
                    # get passed criteria for all qc
                    passed = drs_text.true_text(row_data['PASSED_ALL_QC'])
                    # get qc_names
                    qc_names_raw = _get_list_param(row_data, 'QC_NAMES')
                    qc_values_raw = _get_list_param(row_data, 'QC_VALUES')
                    qc_logic_raw = _get_list_param(row_data, 'QC_LOGIC')
                    qc_pass_raw = _get_list_param(row_data, 'QC_PASS')
                    # evaluate qc_values
                    qc_names, qc_values, qc_logic, qc_pass = [], [], [], []
                    for qc_it in range(len(qc_names_raw)):
                        # remove any blank criteria
                        cond1 = len(qc_names_raw[qc_it]) == 0
                        cond2 = len(qc_values_raw[qc_it]) == 0
                        if cond1 or cond2:
                            continue
                        # evaluate values
                        # noinspection PyBroadException
                        try:
                            qc_values.append(eval(qc_values_raw[qc_it]))
                        except Exception as _:
                            qc_values.append(qc_values_raw[qc_it])
                        # add name as normal
                        qc_names.append(qc_names_raw[qc_it])
                        # add logic as normal
                        qc_logic.append(qc_logic_raw[qc_it])
                        # convert pass to boolean
                        qc_pass.append(drs_text.true_text(qc_pass_raw[qc_it]))
                    # get the flags
                    flags = base_class.BinaryDict()
                    flags.add_keys(row_data['FLAGSTR'].split('|'))
                    flags.encode(row_data['FLAGNUM'])
                    # get the running + ended flags
                    running = flags['RUNNING']
                    ended = flags['ENDED']
                    # get any errors
                    errors = _get_list_param(row_data, 'ERRORMSGS')
                    # -----------------------------------------------------------------
                    # push into storage
                    self.passed[sublevel] = passed
                    self.qc_names[sublevel] = qc_names
                    self.qc_values[sublevel] = dict(zip(qc_names, qc_values))
                    self.qc_logics[sublevel] = dict(zip(qc_names, qc_logic))
                    self.qc_passes[sublevel] = dict(zip(qc_names, qc_pass))
                    self.running[sublevel] = running
                    self.ended[sublevel] = ended
                    self.errormsgs[sublevel] = errors
                # set valid
                self.is_valid = True
                self.is_valid_for_qc = True
            except Exception as e:
                emsg = 'QC ERROR - PID {0}: {1}: {2}'
                eargs = [self.pid, type(e), str(e)]
                WLOG(params, 'warning', emsg.format(*eargs))
                self.is_valid_for_qc = False

    def query(self, command: str):
        return sqldf(command, self.namespace)


class StatProperty:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.value = None

    def add(self, pdict, value, func_name):
        self.value = value
        pdict[self.name] = self.value
        pdict.set_source(self.name, func_name)
        pdict.instances[self.name] = self

    def make(self) -> str:
        return f'{self.name} = {self.value}'


# =============================================================================
# Define class worker functions
# =============================================================================
def get_log_entries(params: ParamDict,
                    mode: str) -> List[LogEntry]:
    # load log database
    WLOG(params, '', 'Obtaining full log database. Please wait...')
    logdbm = drs_database.LogDatabase(params)
    logdbm.load_db()

    # get condition from arguments
    if drs_text.null_text(params['INPUTS']['SQL'], ['None', '', 'Null']):
        condition = None
    else:
        condition = params['INPUTS']['SQL']
    # get all entries from database
    dataframe = logdbm.get_entries('*', condition=condition)
    # get the index database
    if mode == 'index':
        WLOG(params, '', 'Obtaining full index database. Please wait...')
        findexdbm = drs_database.FileIndexDatabase(params)
        findexdbm.load_db()
        idataframe = findexdbm.get_entries('*')
    else:
        idataframe = pd.DataFrame()
    # -------------------------------------------------------------------------
    # get unique pids
    upids = np.unique(dataframe['PID'])
    # storage for log entries
    log_entries = []
    # print progress
    WLOG(params, '', 'Sorting {0} log entries'.format(len(upids)))
    # loop around pids
    for upid in tqdm(upids):
        # get a log entry
        log_entry = LogEntry(upid, dataframe)
        log_entry.get_attributes(params, mode=mode, idataframe=idataframe)
        # deal with valid data
        cond = log_entry.is_valid
        if mode == 'timing':
            cond &= log_entry.is_valid_for_timing
        elif mode == 'qc':
            cond &= log_entry.is_valid_for_qc
        # append to log entry storage list if conditions met
        if cond:
            log_entries.append(log_entry)
    # return list of log entries
    return log_entries


def _index_database_crossmatch(idataframe: pd.DataFrame,
                               pid: str) -> pd.DataFrame:
    """
    Get all index entries for a specific pid

    :param idataframe: pandas.DataFrame - the full index database
    :param pid: str, the unique pid from the log entry

    :return: pandas dataframe - all index entries that match this pid
    """
    # filter the index database by PID
    dataframe = idataframe[idataframe['KW_PID'] == pid]
    # return the
    return dataframe


# =============================================================================
# Define timing stats functions
# =============================================================================
def timing_stats(params: ParamDict, recipe: DrsRecipe) -> ParamDict:
    """
    Print and plot timing stats

    :param params:
    :param recipe:
    :return:
    """
    # set function name
    func_name = __NAME__ + '.timing_stats()'
    # print progress
    WLOG(params, 'info', 'Running timing code')
    # -------------------------------------------------------------------------
    # plot dt timing graph
    report_file = 'apero_stats_timing.fits'
    # construct report directory
    report_dir = os.path.join(params['DRS_DATA_MSG'], 'report')
    # deal with report directory not existing
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    # -------------------------------------------------------------------------
    # get log entries
    log_entries = get_log_entries(params, mode='timing')
    # -------------------------------------------------------------------------
    # get stats
    stat_dict = get_timing_stats(log_entries)
    # get log table
    log_dict = dict(recipe=[], shortname=[], pid=[], logfile=[], runstring=[],
                    start=[], end=[], duration=[])
    # loop around and add entries
    for log_entry in log_entries:
        log_dict['recipe'].append(log_entry.recipe_name)
        log_dict['shortname'].append(log_entry.shortname)
        log_dict['pid'].append(log_entry.pid)
        log_dict['logfile'].append(log_entry.log_file)
        log_dict['runstring'].append(log_entry.runstring)
        log_dict['start'].append(log_entry.start_time)
        log_dict['end'].append(log_entry.end_time)
        log_dict['duration'].append(log_entry.duration)
    # convert to table and write to disk
    log_table = Table(log_dict)
    # construct log file absolute path
    log_file = os.path.join(report_dir, report_file)
    # print progress
    WLOG(params, '', 'Writing log file: {0}'.format(log_file))
    # write to disk
    log_table.write(log_file, overwrite=True)
    # -------------------------------------------------------------------------
    # loop around recipe and print stats
    pdict = dict()

    for recipe_name in stat_dict:
        pdict[recipe_name] = print_timing_stats(params, recipe_name,
                                                stat_dict[recipe_name])
    # -------------------------------------------------------------------------
    # plot timing graph
    recipe.plot('STATS_TIMING_PLOT', logs=log_entries, pstats=pdict)
    # -------------------------------------------------------------------------
    # save outputs to return
    outputs = ParamDict()
    # loop around stat dictionary
    for recipe_name in stat_dict:
        # add outputs
        sprop = StatProperty(f'{recipe_name}_NRUNS', 'static')
        sprop.add(outputs, stat_dict[recipe_name]['NUMBER'], func_name)
    # return outputs
    return outputs


def get_timing_stats(logs: List[LogEntry]) -> Dict[str, Dict[str, Any]]:
    """
    Compile the timing stats for all log entries

    :param logs: list of LogEntry instances

    :return: dictionary of recipes, each dictionary contains a stats dictionary
    """
    durations = np.array(list(map(lambda x: x.duration, logs)))
    recipes = np.array(list(map(lambda x: x.shortname, logs)))
    start_times = np.array(list(map(lambda x: x.start_time, logs)))
    end_times = np.array(list(map(lambda x: x.end_time, logs)))
    # filter out NaNs
    nanmask = np.isfinite(durations)
    durations = durations[nanmask]
    recipes = recipes[nanmask]
    start_times = start_times[nanmask]
    end_times = end_times[nanmask]
    # sort by start_times
    sortmask = np.argsort(start_times)
    durations = durations[sortmask]
    recipes = recipes[sortmask]
    start_times = start_times[sortmask]
    end_times = end_times[sortmask]
    # storage for recipes
    recipe_dict = dict()
    # loop around recipes
    for recipe in recipes:
        # skip done recipes
        if recipe in recipe_dict:
            continue
        # mask the recipe
        rmask = (recipes == recipe)
        # storage for stats
        stats = dict()
        # stats
        stats['MEAN'] = mp.nanmean(durations[rmask])
        stats['MEDIAN'] = mp.nanmedian(durations[rmask])
        stats['SHORTEST'] = mp.nanmin(durations[rmask])
        stats['LONGEST'] = mp.nanmax(durations[rmask])
        stats['STD'] = mp.nanstd(durations[rmask])
        stats['NUMBER'] = len(durations[rmask])
        stats['CPU_TIME_SS'] = np.sum(durations[rmask])
        # total time
        last_entry = max(end_times[rmask])
        first_entry = min(start_times[rmask])
        stats['TOTALTIME_SS'] = (last_entry - first_entry)
        # speed up factor
        stats['SPEED_UP'] = stats['CPU_TIME_SS'] / stats['TOTALTIME_SS']
        # stats in hours
        stats['CPU_TIME_HR'] = stats['CPU_TIME_SS'] / 3600
        stats['TOTALTIME_HR'] = stats['TOTALTIME_SS'] / 3600
        # push to recipe dict storage
        recipe_dict[recipe] = stats
    # return the dictionary of recipes, each with a stats dictionary
    return recipe_dict


def print_timing_stats(params: ParamDict, recipe: str,
                       stats: Dict[str, Any]) -> str:
    WLOG(params, 'info', '=' * 50)
    WLOG(params, 'info', '\t{0}'.format(recipe))
    WLOG(params, 'info', '=' * 50)
    # print stats
    statstr = ('\n\tMean Time: {MEAN:.3f} s +/- {STD:.3f}'
               '\n\tMed Time: {MEDIAN:.3f} s +/- {STD:.3f}'
               '\n\tRange: {SHORTEST:.3f} s to {LONGEST:.3f}'
               '\n\tNruns: {NUMBER}'
               '\n\tTotal Time: {TOTALTIME_HR:.3f} hr'
               '\n\tTotal CPU Time: {CPU_TIME_HR:.3f} hr (x{SPEED_UP:.2f})'
               '\n')
    WLOG(params, '', statstr.format(**stats))

    return statstr.replace('\t', '\n').format(**stats)


# =============================================================================
# Define qc stats functions
# =============================================================================
def qc_stats(params: ParamDict, recipe: DrsRecipe) -> ParamDict:
    """
    Print and plot quality control / running / error stats

    :param params:
    :param recipe:
    :return:
    """
    # set function name
    func_name = __NAME__ + '.qc_stats()'
    # print progress
    WLOG(params, 'info', 'Running timing code')
    # get log entries
    log_entries = get_log_entries(params, mode='qc')
    # get stats
    stat_dict, stat_crit, stat_qc = get_qc_stats(log_entries)
    # loop around recipe and print stats
    for recipe_name in stat_dict:
        # print qc stats
        print_qc_stats(params, recipe_name, stat_dict[recipe_name],
                       stat_crit[recipe_name], stat_qc[recipe_name])
        # compile vectors for plotting
        cqcout = _compile_plot_qc_params(stats=stat_dict[recipe_name],
                                         criteria=stat_crit[recipe_name],
                                         qcdict=stat_qc[recipe_name])
        xvalues, yvalues, lvalues, llabels = cqcout
        # check we have more than one point
        cond = _check_have_stats(stat_dict[recipe_name])
        # plot if we have more than one point and we have a qc plot
        if cond and len(xvalues) > 1:
            recipe.plot('STAT_QC_RECIPE_PLOT', xvalues=xvalues,
                        yvalues=yvalues, lvalues=lvalues, llabels=llabels,
                        recipe_name=recipe_name)

    # -------------------------------------------------------------------------
    # save outputs to return
    outputs = ParamDict()
    # loop around stat dictionary
    for recipe_name in stat_dict:
        crits = stat_crit[recipe_name]
        # loop around log levels
        for crit in crits:
            # deal with log levels as stat_dict key
            if crit == 'None':
                cstring = ''
            else:
                cstring = f'::{crit.strip()}'
            # set number passed
            sprop = StatProperty(f'{recipe_name}_QC_NPASSED', 'static')
            sprop.add(outputs, stat_dict[recipe_name]['NUM_PASSED' + cstring],
                      func_name)
            # set number failed
            sprop = StatProperty(f'{recipe_name}_QC_NFAILED', 'static')
            sprop.add(outputs, stat_dict[recipe_name]['NUM_FAILED' + cstring],
                      func_name)
            # set number ended
            sprop = StatProperty(f'{recipe_name}_QC_NENDED', 'static')
            sprop.add(outputs, stat_dict[recipe_name]['NUM_ENDED' + cstring],
                      func_name)

    # return outputs
    return outputs


def _get_list_param(data, key: str, delimiter='||'):
    """
    Get the result of a parameter that is a list separated by some
    delimiter

    :param data:
    :param key:
    :param delimiter:
    :return:
    """
    if data[key] is None:
        return []
    else:
        return data[key].split(delimiter)


def _sort_sublevel(data: pd.DataFrame) -> List[str]:
    """
    Remove any static variables from the criteria

    :param data: pandas data, the sublevel criteria

    :return: list of strings, updated sublevel criteria
    """
    # deal with only one row --> no sub levels
    if len(data) == 1:
        return ['None']
    else:
        criteria = list(data['LEVELCRIT'])
    # Deal with no level criteria --> no sub levels
    if criteria[0] is None:
        return ['None']
    # separate first entry into categories
    categories = criteria[0].split()
    # get keys
    keys = []
    # loop around categories
    for cat in categories:
        keys.append(cat.split('=')[0])
    # storage for values
    all_values = dict()
    # now get all values for keys
    for crit in criteria:
        for key in keys:
            value = crit.split('{0}='.format(key))[-1].split()[0]
            if key in all_values:
                if value not in all_values[key]:
                    all_values[key].append(value)
            else:
                all_values[key] = [value]
    # remove any constants (non changing criteria)
    changing_values = dict()
    static_values = []
    # loop around all values to remove static variables
    for key in all_values:
        if len(all_values[key]) > 1:
            changing_values[key] = all_values[key]
        else:
            static_values += ['{0}={1} '.format(key, all_values[key][0])]
    # deal with no static values
    if len(static_values) == 0:
        return criteria
    # now make new criteria (without the static variables)
    new_criteria = []
    for crit in criteria:
        for static_value in static_values:
            new_criteria.append(crit.replace(static_value, ''))
    # return the new criteria for each level
    return new_criteria


QcStatReturn = Tuple[Dict[str, Dict[str, Any]],
                     Dict[str, List[str]],
                     Dict[str, Dict[str, List[str]]]]


def get_qc_stats(logs: List[LogEntry]) -> QcStatReturn:
    """
    Compile the timing stats for all log entries

    :param logs: list of LogEntry instances

    :return: dictionary of recipes, each dictionary contains a stats dictionary
    """
    # get list of all recipes
    recipes = np.array(list(map(lambda x: x.shortname, logs))).astype(str)
    # storage for recipes
    recipe_dict = dict()
    criteria_dict = dict()
    qc_dict = dict()
    # loop around recipes
    for recipe in recipes:
        # skip done recipes
        if recipe in recipe_dict:
            continue
        # get log list for this recipe
        rlogs = list(filter(lambda x: x.shortname == recipe, logs))
        # get criteria for this recipe
        rcrit = rlogs[0].criteria
        # push criteria into dictionary
        criteria_dict[recipe] = rcrit
        qc_dict[recipe] = dict()
        # create a stats dictionary
        stats = dict()
        # deal with not having to group
        for crit in rcrit:
            # deal with crit = None
            if drs_text.null_text(crit, ['None', '']):
                critstr = ''
            else:
                critstr = '::{0}'.format(crit.strip())
            # -----------------------------------------------------------------
            # get global qc values
            pfunc = lambda x: _mapqc(x, 'passed', crit, None, False)

            passed = np.array(list(map(pfunc, rlogs)))
            num_passed = np.sum(passed)
            num_failed = np.sum(~passed)
            # push into stats dict
            stats[f'PASSED{critstr}'] = passed
            stats[f'NUM_PASSED{critstr}'] = num_passed
            stats[f'NUM_FAILED{critstr}'] = num_failed
            # -----------------------------------------------------------------
            # get the names of the qc parameters
            qc_names = list(rlogs[0].qc_values[crit].keys())
            qc_dict[recipe][crit] = qc_names
            # get individual qc values
            for qcn in qc_names:
                # define mapping functions
                qcvfunc = lambda x: _mapqc(x, 'qc_values', crit, qcn, np.nan)
                qcpfunc = lambda x: _mapqc(x, 'qc_passes', crit, qcn, False)
                qclfunc = lambda x: _mapqc(x, 'qc_logics', crit, qcn, 'None')
                # get mapped values
                qcv = list(map(qcvfunc, rlogs))
                qcp = list(map(qcpfunc, rlogs))
                qcl = list(map(qclfunc, rlogs))
                # push into stats dict
                stats[f'QCV::{qcn}{critstr}'] = qcv
                stats[f'QCP::{qcn}{critstr}'] = qcp
                stats[f'QCL::{qcn}{critstr}'] = qcl
            # -----------------------------------------------------------------
            # get running / ended
            rfunc = lambda x: _mapqc(x, 'running', crit, None, False)
            efunc = lambda x: _mapqc(x, 'ended', crit, None, False)
            running = np.array(list(map(rfunc, rlogs)))
            ended = np.array(list(map(efunc, rlogs)))
            # push into stats dict
            stats[f'RUNNING{critstr}'] = running
            stats[f'ENDED{critstr}'] = ended
            stats[f'NUM_RUNNING{critstr}'] = np.sum(running)
            stats[f'NUM_ENDED{critstr}'] = np.sum(ended)
        # -----------------------------------------------------------------
        stats['MJDMID'] = np.array(list(map(lambda x: x.mjdmid, rlogs)))
        # push to recipe dict storage
        recipe_dict[recipe] = stats
    # return the dictionary of recipes, each with a stats dictionary
    return recipe_dict, criteria_dict, qc_dict


def print_qc_stats(params: ParamDict, recipe_name: str, stats: Dict[str, Any],
                   stat_crit: List[str], stat_qc: Dict[str, List[str]]):
    # print recipe
    WLOG(params, 'info', '=' * 50)
    WLOG(params, 'info', '\t{0}'.format(recipe_name))
    WLOG(params, 'info', '=' * 50)
    # loop around criteria
    for crit in stat_crit:
        # clean stat str
        statstr = ''
        # deal with crit = None
        if drs_text.null_text(crit, ['None', '']):
            critstr = ''
        else:
            critstr = '::{0}'.format(crit.strip())
            WLOG(params, '', '\t{0}'.format(crit))
        # add number run
        passed = stats[f'NUM_PASSED{critstr}']
        failed = stats[f'NUM_FAILED{critstr}']
        total = passed + failed
        # add to string
        statstr += '\t\tNumber passed: {0}/{1}\n'.format(passed, total)
        statstr += '\t\tNumber failed: {0}/{1}\n'.format(failed, total)
        # add QC
        for qc_name in stat_qc[crit]:
            values = stats[f'QCV::{qc_name}{critstr}']
            logic = stats[f'QCL::{qc_name}{critstr}']
            statstr = _statstr_print(statstr, f'{qc_name}{critstr}', values,
                                     logic)
        # add running / ended
        running = stats[f'NUM_RUNNING{critstr}']
        ended = stats[f'NUM_ENDED{critstr}']
        # add to string
        statstr += '\t\t' + '-' * 50 + '\n'
        statstr += '\t\tNumber running = {0}/{1}\n'.format(running, total)
        statstr += '\t\tNumber ended = {0}/{1}\n'.format(ended, total)
        # print stats
        WLOG(params, '', statstr)


def _statstr_print(statstr: str, key: str, values: List[Any],
                   logic: List[str]) -> str:
    """
    Produce qc stat string

    :param statstr:
    :param key:
    :param values:
    :return:
    """
    # deal with strings
    if not isinstance(values[0], (int, float)):
        return statstr
    elif isinstance(values[0], int):
        dtype = 'int'
    else:
        dtype = 'float'

    # deal with no value or single value
    if len(values) == 0:
        return statstr
    elif len(values) == 1:
        # deal with
        if dtype == 'int':
            statstr += '\t\t{0} = {1}\n'.format(key, values[0])
        elif np.log10(values[0]) > -4:
            statstr += '\t\t{0} = {1:.4f}\n'.format(key, values[0])
        else:
            statstr += '\t\t{0} = {1:.4e}\n'.format(key, values[0])
        return statstr

    valid_values = []
    for value in values:
        try:
            valid_values.append(float(value))
        except TypeError:
            continue

    # deal with significant figures
    with warnings.catch_warnings(record=True) as _:
        if dtype == 'int':
            fmtstr = '\t\t{0} {1} = {2}\n'
        elif np.log10(valid_values[0]) > -4:
            fmtstr = '\t\t{0} {1} = {2:.4f}\n'
        else:
            fmtstr = '\t\t{0} {1} = {2:.4e}\n'

    mean = mp.nanmean(valid_values)
    median = mp.nanmedian(valid_values)
    maximum = mp.nanmax(valid_values)
    minimum = mp.nanmin(valid_values)

    statstr += '\t\t' + '-' * 50 + '\n'
    if dtype == 'int':
        statstr += '\t\t{0} {1} = {2:.4f}\n'.format(key, 'Mean', mean)
        statstr += '\t\t{0} {1} = {2:.4f}\n'.format(key, 'Med ', median)
        statstr += fmtstr.format(key, 'Max ', int(maximum))
        statstr += fmtstr.format(key, 'Min ', int(minimum))
    else:
        statstr += fmtstr.format(key, 'Mean', mean)
        statstr += fmtstr.format(key, 'Med ', median)
        statstr += fmtstr.format(key, 'Max ', maximum)
        statstr += fmtstr.format(key, 'Min ', minimum)
    # add fail criteria
    statstr += '\t\tFail when {1}\n'.format(key, logic[0])
    # return stat string
    return statstr


def _mapqc(x, attribute: str, crit: str, name: Optional[str] = None,
           default: Optional[Any] = None):
    if hasattr(x, attribute):
        avalue = getattr(x, attribute)
        if crit in avalue:
            if name is None:
                return avalue[crit]
            if name in avalue[crit]:
                return avalue[crit][name]
    return default


def _compile_plot_qc_params(stats, criteria, qcdict):
    # -------------------------------------------------------------------------
    # plot parameters
    xvalues = dict()
    yvalues = dict()
    lvalues = dict()
    llabels = dict()
    # -------------------------------------------------------------------------
    # loop around criteria
    for crit in criteria:
        # deal with crit = None
        if drs_text.null_text(crit, ['None', '']):
            critstr = ''
        else:
            critstr = '::{0}'.format(crit.strip())
        # add passed / running / ended
        xvalues1, yvalues1, _ = _get_qcv(stats, 'MJDMID', f'PASSED{critstr}')
        xvalues2, yvalues2, _ = _get_qcv(stats, 'MJDMID', f'RUNNING{critstr}')
        xvalues3, yvalues3, _ = _get_qcv(stats, 'MJDMID', f'ENDED{critstr}')
        # check valid
        cond1 = np.sum(np.isfinite(xvalues1)) > 0
        cond2 = np.sum(np.isfinite(yvalues1)) > 0
        cond3 = len(xvalues1) > 0 and len(yvalues1) > 0
        # add to arrays
        if cond1 and cond2 and cond3:
            xvalues['Condition'] = [xvalues1, xvalues2, xvalues3]
            yvalues['Condition'] = [yvalues1, yvalues2, yvalues3]
            llabels['Condition'] = [f'{critstr} passed', f'{critstr} running',
                                    f'{critstr} ended']
            lvalues['Condition'] = [None, None, None]
        # ---------------------------------------------------------------------
        # loop around qc parameters
        for qc_name in qcdict[crit]:
            # get vectors
            name = f'{qc_name}{critstr}'
            qcvout = _get_qcv(stats, 'MJDMID', f'QCV::{qc_name}{critstr}')
            xvalues_i, yvalues_i, mask_i = qcvout
            # deal with non number qc (skip)
            if len(mask_i) == 0:
                continue
            # get logic and mask it
            logic = list(np.array(stats[f'QCL::{qc_name}{critstr}'])[mask_i])
            # try to get a limit from logic
            lvalues_i = _get_logic_values(qc_name, logic)
            # check valid
            cond1_i = np.sum(np.isfinite(xvalues_i)) > 0
            cond2_i = np.sum(np.isfinite(yvalues_i)) > 0
            cond3_i = len(xvalues_i) > 0 and len(yvalues_i) > 0
            # only add if all values aren't NaN
            if cond1_i and cond2_i and cond3_i:
                # add to arrays
                xvalues[name] = [xvalues_i]
                yvalues[name] = [yvalues_i]
                lvalues[name] = [lvalues_i]
                llabels[name] = [name]
    # return x, y, logic and labels vectors for plotting
    return xvalues, yvalues, lvalues, llabels


def _check_have_stats(stats: Dict[str, Any]) -> bool:
    """
    Check whether we have more than one stat

    :param stats:
    :return:
    """
    num_passed, num_failed = 0, 0
    # loop around stats
    for key in stats:
        if key.startswith('NUM_PASSED'):
            num_passed = stats[key]
        if key.startswith('NUM_FAILED'):
            num_failed = stats[key]
    # get total number
    total_number = num_passed + num_failed
    # return whether we have more than one stat
    return total_number > 1


def _get_logic_values(key: str, logic: List[str]) -> List[List[float]]:
    """
    Take the qc logic from all rows and try to construct a logic vector to
    plot (only if number)

    :param key: str, the variable name (should be contained within logic string)
    :param logic: list of strings, the logic for each row

    :return:
    """
    # punctuation
    chars = string.punctuation.replace('.', '')

    ldict = dict()
    # loop around logic
    for row in range(len(logic)):
        # remove key
        logicstr = logic[row].replace(key, '')
        # strip all punctuation
        for char in chars:
            logicstr = logicstr.replace(char, '')
        # strip whitespaces
        logicstr = logicstr.strip()
        # split on spaces (incase we have two numbers)
        logic_var = logicstr.split()
        # storage for number
        logic_nums = []
        # remove any non numeric "words"
        for subrow in range(len(logic_var)):
            # try to get a int or float out of parameter
            # noinspection PyBroadException
            try:
                logic_nums.append(float(eval(logic_var[subrow])))
            except Exception as _:
                continue
        # push numbers into dictionary
        for subrow in range(len(logic_nums)):
            if subrow in ldict:
                ldict[subrow].append(logic_nums[subrow])
            else:
                ldict[subrow] = [logic_nums[subrow]]
    # push into vectors
    lvalues = []
    for row in ldict:
        lvalues.append(ldict[row])
    # return lvalues
    return lvalues


def _get_qcv(stats: dict, xkey: str, ykey: str
             ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Filter out bad values for both x and y in the qc stat dictionary

    :param stats: dict, qc stat dictionary
    :param xkey: str, the key for x values in the stat dictionary
    :param ykey: str, the key for y values in the stat dictionary
    :return:
    """
    # get raw values
    xvalues = stats[xkey]
    yvalues = stats[ykey]
    mask = np.arange(len(xvalues))
    # storage for valid values
    valid_xvalues = []
    valid_yvalues = []
    valid_mask = []
    # loop around all values
    for row in range(len(yvalues)):
        # noinspection PyBroadException
        try:
            # cast to floats / bool
            vx = float(xvalues[row])
            vy = float(yvalues[row])
            vm = mask[row]
        except Exception as _:
            continue
        # append to array
        valid_xvalues.append(vx)
        valid_yvalues.append(vy)
        valid_mask.append(vm)
    # deal with no values
    if len(valid_mask) == 0:
        return np.array([]), np.array([]), np.array([])
    # make numpy arrays
    vxvalues, vyvalues = np.array(valid_xvalues), np.array(valid_yvalues)
    vmask = np.array(valid_mask)
    # sort by x values
    sortmask = np.argsort(vxvalues)
    # return sorted valid values in x and y
    return vxvalues[sortmask], vyvalues[sortmask], vmask[sortmask]


# =============================================================================
# Define error stats functions
# =============================================================================
class ErrorReportEntry:
    def __init__(self, loglines, start, end):

        self.error_lines = loglines[start:end]
        self.run_id = -1
        self.runstring = ''
        self.recipename = ''
        self.error_report = []
        self.error_str = ''
        self.error_codes = []

    def print_str(self):
        print(''.join(self.error_lines))

    def print_report(self):
        print(self.error_str)

    def write_entry(self, iteration, length) -> str:
        entrystr = ''
        entrystr += '\n#' + '=' * 80
        entrystr += '\n#' + ' {0} / {1}'.format(iteration + 1, length)
        entrystr += '\n#' + ' RUNSTRING = {0}'.format(self.runstring)
        entrystr += '\n#' + '=' * 80
        # entry str around lines in report and add to lines
        for reportline in self.error_report:
            entrystr += '\n' + reportline
        entrystr += '\n\n'
        return entrystr

    def process(self, params):
        # ---------------------------------------------------------------------
        # get run id - should be in line 0
        # noinspection PyBroadException
        try:
            run_id = self.error_lines[0].split('ID=\'')[-1]
            run_id = run_id.split('\'')[0]
            self.run_id = int(run_id)
        except Exception as _:
            self.run_id = -2
        # ---------------------------------------------------------------------
        # get run string
        runstring = self.error_lines[1].split('-@!|PROC|\t')[-1]
        self.runstring = runstring.split('\n')[0]
        # get recipe
        self.recipename = self.runstring.split()[0].replace('.py', '')
        # ---------------------------------------------------------------------
        # get error report
        report = []
        for line in self.error_lines[2:]:
            # remove \n
            line = line.replace('\n', '')
            # remove header
            line = line.replace(params['DRS_HEADER'], '')
            # remove timestamp
            line = line.split('-  |PROC|')[-1]
            # remove info lines
            line = line.split('-**|PROC|')[-1]
            # skip recipe complete message
            if 'I[40-003-00001]' in line:
                continue
            # remove empty lines
            if len(line.strip()) == 0:
                continue
            # if line is not empty add
            if len(line) != 0:
                report.append(line)
        # add to attributes
        self.error_report = report
        self.error_str = '\n'.join(report)
        # ---------------------------------------------------------------------
        # try to get any error codes
        error_codes = re.findall(REGEX_ERROR_CODE, ''.join(report))
        # make unique
        error_codes = np.unique(error_codes)
        # add to error codes
        if len(error_codes) == 0:
            self.error_codes = [UNHANDLED_ERROR_CODE]
        else:
            self.error_codes = error_codes


def error_stats(params: ParamDict):
    """
    Get the error stats files and sorts logs into files.
    Files are saved to {DRS_DATA_MSG}/reports/LOG_NAME/

    :param params: ParamDict, parameter dictionary of constants

    :return: None, writes log files to {DRS_DATA_MSG}/reports/LOG_NAME/
    """
    # set function name
    func_name = __NAME__ + '.error_stats()'
    # deal with plog from arguments
    plog_files = []
    if 'INPUTS' in params:
        if 'PLOG' in params['INPUTS']:
            null_text = ['None', 'Null', '']
            if drs_text.null_text(params['INPUTS']['PLOG'], null_text):
                plog_files = []
            else:
                plog_files = params['INPUTS'].listp('PLOG', dtype=str)
    # -------------------------------------------------------------------------
    if len(plog_files) == 0:
        # get log directory
        plog_dir = os.path.join(params['DRS_DATA_MSG'], 'tool')
        # -------------------------------------------------------------------------
        # locate all processing logs
        plog_files = []
        for _root, _dirs, _files in os.walk(plog_dir):
            for filename in _files:
                if filename.endswith('apero_processing.log'):
                    plog_files.append(os.path.join(_root, filename))
    # -------------------------------------------------------------------------
    # storage for output
    recipe_count_all = dict()
    # loop around log files
    for p_it, plog_file in enumerate(plog_files):
        # print progress
        msg = 'Analysing log file {0} of {1}'
        WLOG(params, 'info', msg.format(p_it + 1, len(plog_files)))
        msg = '\tLogfile: {0}'
        WLOG(params, 'info', msg.format(plog_file), wrap=False)
        # read the log file
        with open(plog_file, 'r') as plogfile:
            lines = plogfile.readlines()
        # storage for this processing log
        recipe_count_all[plog_file] = dict()
        # ---------------------------------------------------------------------
        # get the reports in a directory
        report_subdir = os.path.basename(plog_file).replace('.log', '')
        # construct report directory
        report_dir = os.path.join(params['DRS_DATA_MSG'], 'report',
                                  report_subdir)
        # deal with report directory not existing
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        # log that we are removing all files from report directory
        WLOG(params, '', 'Removing all files from : {0}'.format(report_dir))
        # make sure directory is empty
        for filename in glob.glob(report_dir + '/*'):
            msg = '\t - Removing {0}'
            WLOG(params, '', msg.format(os.path.basename(filename)))
            os.remove(filename)
        # ---------------------------------------------------------------------
        # counter for number of runs
        num_runs = 0
        # scan through and find how many runs we had
        for it, line in enumerate(lines):
            if '|PROC|Validating run ' in line:
                num_runs += 1
        # print how many runs there were
        WLOG(params, 'info', 'In total there were {0} runs'.format(num_runs))
        # ---------------------------------------------------------------------
        # scan through and find all error reporting lines - note down the line
        # numbers
        reported_error_lines = []
        # loop around lines and find all lines containing the report error code
        for it, line in enumerate(lines):
            if REPORT_ERROR_CODE in line:
                reported_error_lines.append(it)
        # ---------------------------------------------------------------------
        # storage of error entries
        error_rentries = []
        # print progress
        msg = 'Creating error entries for {0} errors'
        WLOG(params, 'info', msg.format(len(reported_error_lines)))
        # for each reported error line we can generate an error report entry
        for row in tqdm(range(len(reported_error_lines))):
            # get start and end line numbers
            if row != len(reported_error_lines) - 1:
                start = reported_error_lines[row]
                end = reported_error_lines[row + 1]
            # deal with last report
            else:
                start = reported_error_lines[row]
                end = len(lines)
            # create error report entry instance
            error_rentry = ErrorReportEntry(lines, start, end)
            error_rentry.process(params)
            # append to error entries
            error_rentries.append(error_rentry)
        # ---------------------------------------------------------------------
        # print progress
        WLOG(params, 'info', 'Counting number of errors per recipe')
        # count number of errors for each recipe
        recipe_count = dict()
        # loop around error entries
        for entry in error_rentries:
            if entry.recipename in recipe_count:
                recipe_count[entry.recipename] += 1
            else:
                recipe_count[entry.recipename] = 1
        # print stats
        for recipename in recipe_count:
            msg = '\t- There were {0} errors for recipe {1}'
            WLOG(params, '', msg.format(recipe_count[recipename], recipename))

        # save all plog recipe counts
        recipe_count_all[plog_file]['TCOUNT'] = len(error_rentries)
        recipe_count_all[plog_file]['RCOUNT'] = recipe_count
        # ---------------------------------------------------------------------
        # print progress
        WLOG(params, 'info', 'Counting number of unique errors')
        # count all error code occurrences
        all_error_codes = dict()
        all_error_codes_runstrings = dict()
        all_error_codes_instance = dict()
        all_error_codes_example = dict()
        all_error_codes_recipe_names = dict()
        known_errors = dict()
        # loop around error entries
        for entry in error_rentries:
            for code in entry.error_codes:
                if code not in all_error_codes:
                    all_error_codes[code] = 1
                    all_error_codes_runstrings[code] = [entry.runstring]
                    all_error_codes_instance[code] = [entry]
                    all_error_codes_example[code] = entry.error_str
                    all_error_codes_recipe_names[code] = [entry.recipename]
                    known_errors[code] = dict()
                else:
                    all_error_codes[code] += 1
                    all_error_codes_runstrings[code] += [entry.runstring]
                    all_error_codes_instance[code] += [entry]
                    all_error_codes_recipe_names[code] += [entry.recipename]
        # update full plog
        recipe_count_all[plog_file]['EXPECTED_COUNT'] = all_error_codes
        # ---------------------------------------------------------------------
        # print out error codes into groups
        for code in all_error_codes:
            # skip unhandled errors
            if code == UNHANDLED_ERROR_CODE:
                continue
            # print progress
            WLOG(params, '', 'Writing error file for code {0}'.format(code),
                 colour='magenta')
            # get a new set of lines
            lines = ''
            # clean code
            codestr = str(code)
            for char in ['[', ']', '-']:
                codestr = codestr.replace(char, '_')
            codestr = codestr.strip('_')
            # get the list of instances
            instances = all_error_codes_instance[code]
            # get unique recipe names
            urecipe_names = np.unique(all_error_codes_recipe_names[code])
            # log how many instances found
            msg = '\t Found {0} recipes with this error'
            WLOG(params, '', msg.format(len(instances)))
            # print unique recipe names
            WLOG(params, '', '\t({0})'.format(','.join(urecipe_names)))
            # loop around instances
            for it, instance in enumerate(instances):
                lines += instance.write_entry(it, len(instances))
            # save to file
            with open(os.path.join(report_dir, codestr + '.log'), 'w') as rfile:
                rfile.write(lines)
        # ---------------------------------------------------------------------
        # deal with out unhandled errors
        # ---------------------------------------------------------------------
        # print progress
        WLOG(params, '', 'Dealing with unhandled errors')
        # deal with no unhandled errors found
        if UNHANDLED_ERROR_CODE not in all_error_codes_instance:
            WLOG(params, 'info', '\tNo unhandled errors found')
            # update full plog
            recipe_count_all[plog_file]['UNEXPECTED_COUNT'] = dict()
            continue
        # get unhandled instances
        uinstances = all_error_codes_instance[UNHANDLED_ERROR_CODE]
        uerror_reports = list(map(lambda x: x.error_report, uinstances))
        # group by last line
        groups = np.unique(list(map(lambda x: x[-1].strip(), uerror_reports)))
        groupids = list(range(len(groups)))
        # storage
        group_instances = dict()
        # loop around unhandled instances
        for uinstance in uinstances:
            # get group name for this instance
            group = uinstance.error_report[-1].strip()
            # get group id
            pos = list(groups).index(group)
            groupid = groupids[pos]
            # add to storage
            if groupid in group_instances:
                group_instances[groupid].append(uinstance)
            else:
                group_instances[groupid] = [uinstance]
        # ---------------------------------------------------------------------
        # write unhandled groups to log files
        # print progress
        WLOG(params, 'info', 'Writing unhandled errors to group log files')
        # store unhandled
        unhandled_store = dict()
        # loop around groups and save
        for key in group_instances:
            # define the code string
            codestr = 'E_UNHANDLE_{0:05d}'.format(key)
            # print progress
            msg = '\t - Writing error file for group {0}'
            WLOG(params, '', msg.format(codestr), colour='magenta')
            WLOG(params, '', '\t\t{0}'.format(groups[key]))
            # get the instances for this group
            instance_group = group_instances[key]
            # get all recipes for this group
            allrecipes = list(map(lambda x: x.recipename, instance_group))
            # get unique recipe names
            urecipe_names = np.unique(allrecipes)
            # log how many instances found
            msg = '\t\t Found {0} recipes with this error'
            WLOG(params, '', msg.format(len(instance_group)))
            # store number
            unhandled_store[key] = len(instance_group)
            # print unique recipe names
            WLOG(params, '', '\t\t({0})'.format(','.join(urecipe_names)))
            # reset lines
            lines = ''
            # loop around instances
            for it, instance in enumerate(instance_group):
                lines += instance.write_entry(it, len(instance_group))
            # save to file
            with open(os.path.join(report_dir, codestr + '.log'), 'w') as rfile:
                rfile.write(lines)
        # update full plog
        recipe_count_all[plog_file]['UNEXPECTED_COUNT'] = unhandled_store
    # -------------------------------------------------------------------------
    # save outputs to return
    outputs = ParamDict()
    # loop around stat dictionary
    for plog_file in recipe_count_all:
        # each plog file creates one entry
        sprop = StatProperty(plog_file, 'varying')
        sprop.add(outputs, recipe_count_all[plog_file], func_name)
    # return outputs
    return outputs


# =============================================================================
# Define memory stats functions
# =============================================================================
def memory_stats(params: ParamDict, recipe: DrsRecipe):
    """
    Create the memory stats plot

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this module (used for
                   plotting)

    :return: None, plots graph
    """
    # set function name
    func_name = __NAME__ + '.memory_stats()'
    # ---------------------------------------------------------------------
    # construct report directory
    report_dir = os.path.join(params['DRS_DATA_MSG'], 'report')
    # deal with report directory not existing
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    # ---------------------------------------------------------------------
    # get log database
    WLOG(params, '', 'Loading log database')
    logdbm = drs_database.LogDatabase(params)
    # set up condition
    condition = 'RECIPE_TYPE LIKE "%recipe%" AND ENDED=1'
    columns = ('SHORTNAME, UNIXTIME, RAM_USAGE_START, RAM_USAGE_END, '
               'START_TIME, END_TIME, RECIPE, RECIPE_TYPE, ENDED')
    # -------------------------------------------------------------------------
    # use sql to turn off certain recipes
    if not drs_text.null_text(params['INPUTS']['SQL'], ['None', '', 'Null']):
        condition += 'AND' + params['INPUTS']['SQL']
    # -------------------------------------------------------------------------
    # get limit
    if params['INPUTS']['LIMIT'] != 0:
        limit = params['INPUTS']['LIMIT']
    else:
        limit = None
    # -------------------------------------------------------------------------
    # get columns from log dbm
    ltable = logdbm.get_entries(columns, condition=condition,
                                groupby='PID')
    # find start and end points for each recipe
    shortnames = logdbm.database.unique('SHORTNAME', condition=condition)
    # -------------------------------------------------------------------------
    # deal with limit
    if limit is not None:
        # store valid shortnames
        new_shortnames = []
        # loop around all shortnames
        for shortname in shortnames:
            # get a mask for this shortname
            mask = ltable['SHORTNAME'] == shortname
            # remove any able limit
            if np.sum(mask) > limit:
                ltable = ltable[~mask]
            else:
                new_shortnames.append(shortname)
        # overwrite original list
        shortnames = np.array(new_shortnames)
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Sorting time axis')
    # change time into time since start
    time000 = np.min(ltable['UNIXTIME'])
    time0 = ltable['UNIXTIME'] - time000
    # change time to hours
    time0 = time0 / 3600
    # change start time and end time into time since start
    starttime = pd.to_datetime(ltable["START_TIME"]).view("int64") / 10 ** 9
    starttime = (starttime - time000) / 3600
    endtime = pd.to_datetime(ltable["END_TIME"]).view("int64") / 10 ** 9
    endtime = (endtime - time000) / 3600
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Getting recipe start and finish limits')
    # get first occurrence of each short name
    unix_short = []
    for shortname in shortnames:
        mask = ltable['SHORTNAME'] == shortname
        unix_short.append(np.min(starttime[mask]))
    # resort shortnames by occurrence
    shortnames = shortnames[np.argsort(unix_short)]
    # storage box values
    shortname_values = dict()
    # find the first and last entry for each shortname
    for shortname in shortnames:
        mask = ltable['SHORTNAME'] == shortname
        # have to deal with one entry
        if np.sum(mask) == 1:
            s_start = np.array([starttime[mask].iloc[0]])
            s_end = np.array([endtime[mask].iloc[0]])
            smed = time0[mask].iloc[0]
            r_start = np.array([ltable['RAM_USAGE_START'][mask].iloc[0]])
            r_end = np.array([ltable['RAM_USAGE_END'][mask].iloc[0]])
        else:
            s_start = np.array(starttime[mask])
            s_end = np.array(endtime[mask])
            smed = np.median(time0[mask])
            r_start = np.array(ltable['RAM_USAGE_START'][mask])
            r_end = np.array(ltable['RAM_USAGE_END'][mask])
        smin = smed - np.min(s_start)
        smax = np.max(s_end) - smed
        shortname_values[shortname] = [smin, smed, smax, s_start, s_end,
                                       r_start, r_end]
    # -------------------------------------------------------------------------
    # length
    # window = len(ltable) // 1000
    window = 1
    # print progress
    WLOG(params, '', f'Calculating rolling mean of timings (window={window}')
    # mean results
    unixtime = time0.rolling(window=window).mean()
    ram_start = ltable['RAM_USAGE_START'].rolling(window=window).mean()
    ram_end = ltable['RAM_USAGE_END'].rolling(window=window).mean()
    rmax_start = ltable['RAM_USAGE_START'].rolling(window=window).max()
    rmin_start = ltable['RAM_USAGE_START'].rolling(window=window).min()
    rmax_end = ltable['RAM_USAGE_END'].rolling(window=window).max()
    rmin_end = ltable['RAM_USAGE_END'].rolling(window=window).min()
    # -------------------------------------------------------------------------
    # remove nans
    nanmask = np.isfinite(unixtime) & np.isfinite(ram_start)
    nanmask &= np.isfinite(ram_end)
    time0 = time0[nanmask]
    ram_start = ram_start[nanmask]
    ram_end = ram_end[nanmask]
    rmax_start = rmax_start[nanmask]
    rmin_start = rmin_start[nanmask]
    rmax_end = rmax_end[nanmask]
    rmin_end = rmin_end[nanmask]
    # -------------------------------------------------------------------------
    # print stats to screen
    for shortname in shortname_values:
        _, _, _, _, _, r_start, r_end = shortname_values[shortname]
        WLOG(params, 'info', 'Recipe = {0}'.format(shortname))
        WLOG(params, '', '\tMin RAM start: {0:.3f} GB'.format(np.min(r_start)))
        WLOG(params, '', '\tMax RAM start: {0:.3f} GB'.format(np.max(r_start)))
        WLOG(params, '', '\tMin RAM end: {0:.3f} GB'.format(np.min(r_end)))
        WLOG(params, '', '\tMax RAM end: {0:.3f} GB'.format(np.max(r_end)))

    # -------------------------------------------------------------------------
    # plot (more to recipe plots)
    recipe.plot('STAT_RAM_PLOT', time0=time0, ram_start=ram_start,
                ram_end=ram_end, rmax_start=rmax_start, rmax_end=rmax_end,
                rmin_start=rmin_start, rmin_end=rmin_end,
                shortnames=shortnames, shortname_values=shortname_values)
    # -------------------------------------------------------------------------
    # make table 1 output
    table1 = Table()
    table1['TIME_SINCE_START'] = time0
    table1['RAM_MIN_START'] = rmin_start
    table1['RAM_MIN_END'] = rmin_end
    table1['RAM_MAX_START'] = rmax_start
    table1['RAM_MAX_END'] = rmax_end
    table1['RAM_MIN_MIN'] = np.min([rmin_start, rmin_end], axis=0)
    table1['RAM_MAX_MAX'] = np.max([rmax_start, rmax_end], axis=0)
    table1['RAM_MEAN'] = np.mean([ram_start, ram_end], axis=0)
    # -------------------------------------------------------------------------
    # get data for table 2
    tabledict2 = dict(SHORTNAME=[], START_UNIX=[],
                      MED_UNIX=[], END_UNIX=[])
    for shortname in shortname_values:
        smin, smed, smax, _, _, _, _ = shortname_values[shortname]
        tabledict2['SHORTNAME'].append(shortname)
        tabledict2['START_UNIX'].append(smin)
        tabledict2['MED_UNIX'].append(smed)
        tabledict2['END_UNIX'].append(smax)
    # push table 2 data into table
    table2 = Table(tabledict2)
    # -------------------------------------------------------------------------
    # construct filename
    filename = os.path.join(report_dir, 'apero_stats_memory.fits')
    # write memory data
    drs_fits.writefits(params, filename, data=[None, table1, table2],
                       header=[None, None, None], names=[None, 'ram', 'recipe'],
                       datatype=[None, 'table', 'table'],
                       dtype=[None, None, None])
    # -------------------------------------------------------------------------
    # save outputs to return
    outputs = ParamDict()
    # loop around stat dictionary
    for shortname in shortnames:
        # add outputs
        sout = shortname_values[shortname]
        smin, smed, smax, s_start, s_end, r_start, r_end = sout
        # set time start
        sprop = StatProperty(f'{shortname}_TIMESTART', 'varying')
        sprop.add(outputs, smed - smin, func_name)
        # set time median
        sprop = StatProperty(f'{shortname}_TIMEMED', 'varying')
        sprop.add(outputs, smed, func_name)
        # set time end
        sprop = StatProperty(f'{shortname}_TIMEEND', 'varying')
        sprop.add(outputs, smed + smax, func_name)
        # set ram start min
        sprop = StatProperty(f'{shortname}_RAMSTART_MIN', 'varying')
        sprop.add(outputs, np.nanmin(r_start), func_name)
        # set ram start max
        sprop = StatProperty(f'{shortname}_RAMSTART_MAX', 'varying')
        sprop.add(outputs, np.nanmax(r_start), func_name)
        # set ram end min
        sprop = StatProperty(f'{shortname}_RAMEND_MIN', 'varying')
        sprop.add(outputs, np.nanmin(r_end), func_name)
        # set ram end max
        sprop = StatProperty(f'{shortname}_RAMEND_MAX', 'varying')
        sprop.add(outputs, np.nanmax(r_end), func_name)

    # return outputs
    return outputs


# =============================================================================
# Define file index stats functions
# =============================================================================
class FileStat:
    def __init__(self, name: str, path: str, condition: Optional[str] = None,
                 per_obs_dir: bool = False, suffix: str = ''):
        """
        Construct the file stat class

        :param name: str, the name for the variable
        :param path: path, the path to the directory to check
        :param condition: str, the sql WHERE condition to identify this
                          type of file
        :param per_obs_dir: bool, if True do this per directory
        :param suffix: str, the suffix to look for (defaults to '' for None)
        """
        self.name = name
        self.path = path
        self.suffix = suffix
        self.condition = condition
        # can't have a suffix and check database
        if self.condition is not None and len(self.suffix) > 0:
            self.condition += f' AND FILENAME LIKE "%{suffix}"'
        self.per_obs_dir = per_obs_dir
        self.disk_name = f'DISK_{name.upper()}'
        self.db_name = f'DB_{name.upper()}'
        # stuff filled by class
        self.paths = []
        self.names = []
        self.conditions = []
        self.disk_counts = dict()
        self.db_counts = dict()
        # must deal with per obs dirs
        self.deal_with_per_obs_dir()

    def deal_with_per_obs_dir(self):
        """
        Deal with requiring obs_dir sub-directories

        :return:
        """
        if not self.per_obs_dir:
            self.paths = [self.path]
            self.names = [self.name]
            self.conditions = [self.condition]
        else:
            paths = glob.glob(self.path + '/*')
            for path in paths:
                obs_dir = drs_misc.get_uncommon_path(path, self.path)
                # do not include non-directories (obs_dir must be a directory)
                if not os.path.isdir(path):
                    continue
                name = f'{self.name}[{obs_dir}]'
                condition = f'{self.condition} AND OBS_DIR="{obs_dir}"'
                # update class attributes
                self.paths.append(path)
                self.names.append(name)
                self.conditions.append(condition)

    def count_on_disk(self):
        """
        Count files on disk

        :return: None, updates self.disk_counts
        """
        # loop through paths
        for it, path in enumerate(self.paths):
            count = 0
            # loop through files in path
            for root, dirs, files in os.walk(path):
                # loop through files in each directory
                for filename in files:
                    # deal with suffix
                    if filename.endswith(self.suffix):
                        # add to count
                        count += 1
            # save to storage
            self.disk_counts['disk_' + self.names[it]] = count

    def count_in_db(self, database: drs_database.drs_db.Database):
        """
        Count files in database

        :param database: the raw database class (drs_db.Database)

        :return: None, updates self.db_counts
        """
        # loop through conditions
        for it, condition in enumerate(self.conditions):
            # if we have a condition query database
            if condition is not None:
                count = database.count(database.tname, condition)
            else:
                count = np.nan
            # save to storage
            self.db_counts['db_' + self.names[it]] = count


def file_index_stats(params: ParamDict) -> ParamDict:
    """
    Get statistics on the file index

    :param params: ParamDict, the parameter dictionary of constants

    :return: ParamDicts, the param dictionary for outputs
    """
    # set function name
    func_name = __NAME__ + 'file_index_stats()'
    # load index database
    findexdb = drs_database.FileIndexDatabase(params)
    findexdb.load_db()
    # define data to count
    # noinspection PyListCreation
    file_stats: list[FileStat] = []
    # raw / tmp / red
    file_stats.append(FileStat('raw', path=params['DRS_DATA_RAW'],
                               condition='BLOCK_KIND="raw"'))
    file_stats.append(FileStat('raw[fits]', path=params['DRS_DATA_RAW'],
                               condition='BLOCK_KIND="raw"',
                               suffix='.fits'))
    file_stats.append(FileStat('tmp', path=params['DRS_DATA_WORKING'],
                               condition='BLOCK_KIND="tmp"'))
    file_stats.append(FileStat('tmp[fits]', path=params['DRS_DATA_WORKING'],
                               condition='BLOCK_KIND="tmp"',
                               suffix='.fits'))
    file_stats.append(FileStat('red', path=params['DRS_DATA_REDUC'],
                               condition='BLOCK_KIND="red"'))
    file_stats.append(FileStat('red[fits]', path=params['DRS_DATA_REDUC'],
                               condition='BLOCK_KIND="red"',
                               suffix='.fits'))
    # calib + tellu
    file_stats.append(FileStat('calib', path=params['DRS_CALIB_DB']))
    file_stats.append(FileStat('calib[fits]', path=params['DRS_CALIB_DB'],
                               suffix='.fits'))
    file_stats.append(FileStat('tellu', path=params['DRS_TELLU_DB']))
    file_stats.append(FileStat('tellu[fits]', path=params['DRS_TELLU_DB'],
                               suffix='.fits'))
    # per night
    file_stats.append(FileStat('raw[fits]', path=params['DRS_DATA_RAW'],
                               condition='BLOCK_KIND="raw"', per_obs_dir=True,
                               suffix='.fits'))
    file_stats.append(FileStat('tmp[fits]', path=params['DRS_DATA_WORKING'],
                               condition='BLOCK_KIND="tmp"', per_obs_dir=True,
                               suffix='.fits'))
    file_stats.append(FileStat('red[fits]', path=params['DRS_DATA_REDUC'],
                               condition='BLOCK_KIND="red"', per_obs_dir=True,
                               suffix='.fits'))
    # -------------------------------------------------------------------------
    # store file outputs
    file_outputs = dict()
    # loop around all counts
    for it in range(len(file_stats)):
        # get this iterations values
        file_stat = file_stats[it]
        # ---------------------------------------------------------------------
        # log progress
        WLOG(params, 'info', f'Counting disk files for {file_stat.name}')
        # count files on disk
        file_stat.count_on_disk()
        # print counts
        for name in file_stat.disk_counts:
            # get count for disk name
            disk_count = file_stat.disk_counts[name]
            # log output
            WLOG(params, '', f'\t{name}={disk_count}')
            # add to outputs
            file_outputs[name] = disk_count
        # ---------------------------------------------------------------------
        # log progress
        WLOG(params, 'info', f'Counting db files for {file_stat.name}')
        # count files in database
        file_stat.count_in_db(findexdb.database)
        # print counts
        for name in file_stat.db_counts:
            # get count for disk name
            db_count = file_stat.db_counts[name]
            # log output
            WLOG(params, '', f'\t{name}={db_count}')
            # add to outputs
            file_outputs[name] = db_count
    # -------------------------------------------------------------------------
    # save outputs to return
    outputs = ParamDict()
    for param_name in file_outputs:
        # set ram end max
        sprop = StatProperty(param_name, 'static')
        sprop.add(outputs, file_outputs[param_name], func_name)
    # return outputs
    return outputs


# =============================================================================
# Define combine stats functions
# =============================================================================
def combine_stats(params: ParamDict, outputs: List[Union[ParamDict, None]]):
    """
    Combine the various outputs into a text file

    :param params: ParamDict, the parameter dictionary of constants
    :param outputs: list of ParamDicts, the output parameter dictionary from
                    each statistic (or None if statistic was skipped)

    :return: None, writes files apero_stats_static and apero_stats_varying
    """
    # -------------------------------------------------------------------------
    # construct report directory
    report_dir = os.path.join(params['DRS_DATA_MSG'], 'report')
    # deal with report directory not existing
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    # -------------------------------------------------------------------------
    # construct file names
    static_file = os.path.join(report_dir, 'apero_stats_static.txt')
    varying_file = os.path.join(report_dir, 'apero_stats_varying.txt')
    # -------------------------------------------------------------------------
    static_list = []
    varying_list = []
    # get all static files and add to file
    for output in outputs:
        # skip None
        if output is None:
            continue
        # loop around parameters in each output
        for param_name in output:
            # get instance associated with parameter
            instance = output.instances[param_name]
            # deal with static vs varying
            if instance.kind == 'static':
                static_list.append(instance.make())
            else:
                varying_list.append(instance.make())
    # -------------------------------------------------------------------------
    # log progress
    WLOG(params, 'info', f'Saving file {static_file}')
    # create static file list
    with open(static_file, 'w') as sfile:
        for line in static_list:
            sfile.write(line + '\n')
    # -------------------------------------------------------------------------
    # log progress
    WLOG(params, 'info', f'Saving file {varying_file}')
    # create varying file list
    with open(varying_file, 'w') as vfile:
        for line in varying_list:
            vfile.write(line + '\n')
    # -------------------------------------------------------------------------


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
