#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs stats

Module to compute stats on the drs

Created on 2021-12-06

@author: cook
"""
import numpy as np
from pandasql import sqldf
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
import warnings

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_recipe


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
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
# define index columns to get
INDEX_COLS = ['FILENAME', 'OBS_DIR', 'BLOCK_KIND', 'KW_MID_OBS_TIME',
              'INFILES', 'KW_OUTPUT', 'KW_DPRTYPE']


# =============================================================================
# General functions
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
        self.is_valid = False
        self.is_valid_for_timing = False
        self.is_valid_for_qc = False
        # set sublevel criteria
        self.criteria = []
        # qc criteria (for each sublevel)
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

    def get_attributes(self, params: ParamDict, mode: str):
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
        # cross-match with index database
        self.index = _index_database_crossmatch(params, self.pid,
                                                ','.join(INDEX_COLS))
        # add index linked parameters
        if len(self.index) > 0:
            # get the mjd mid
            self.mjdmid = self.index['KW_MID_OBS_TIME'].mean()
            # get the observation directories (assume all entries equal)
            self.obs_dir = self.index['OBS_DIR'][0]
            # get the infiles (assume all entries equal)
            raw_infiles = self.index['INFILES'][0]
            if isinstance(raw_infiles, str):
                self.infiles = self.index['INFILES'][0].split('|')
            # get outfiles
            self.outfiles = np.array(self.index['FILENAME'])
            # get the output file type
            self.outtypes = np.array(self.index['KW_OUTPUT'])
            # get the DPRTYPE
            self.dprtypes = np.array(self.index['KW_DPRTYPE'])

        # check if we are dealing with a recipe (ignore others)
        if self.recipe_type != 'recipe':
            return
        # get timing criteria
        if mode == 'timing':
            try:
                self.start_time = Time(self.data.iloc[0]['START_TIME']).unix
                self.end_time = Time(self.data.iloc[0]['END_TIME']).unix
                self.duration = self.end_time - self.start_time
                if np.isfinite(self.duration):
                    self.is_valid = True
                    self.is_valid_for_timing = True
            except Exception as e:
                emsg = 'TIMING ERROR - PID {0}: {1}: {2}'
                eargs = [self.pid, type(e), str(e)]
                WLOG(params, 'warning', emsg.format(*eargs))
        elif mode == 'qc':
            try:
                # get sub level criteria and remove static variables
                subcriteria = _sort_sublevel(self.data)
                self.criteria = list(subcriteria)
                # get qc/run/error criteria
                # must loop around rows
                for row in range(len(self.data)):
                    # get this rows datas
                    row_data = self.data.iloc[row]
                    # get sublevel
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
                    # get running critera
                    running = drs_text.true_text(row_data['RUNNING'])
                    # get ended critera
                    ended = drs_text.true_text(row_data['ENDED'])
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



def get_log_entries(params: ParamDict,
                    mode: str) -> List[LogEntry]:

    # load log database
    logdbm = drs_database.LogDatabase(params)
    logdbm.load_db()
    # get all entries from database
    dataframe = logdbm.get_entries('*')
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
        log_entry.get_attributes(params, mode=mode)
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


def _index_database_crossmatch(params: ParamDict, pid: str,
                               columns: str = '*') -> pd.DataFrame:
    """
    Get all index entries for a specific pid

    :param params: ParamDict, parameter dictionary of constants
    :param pid: str, the unique pid from the log entry
    :param columns: str, comma separated list of columns to get

    :return: pandas dataframe - all index entries that match this pid
    """
    # load index database
    indexdbm = drs_database.IndexDatabase(params)
    indexdbm.load_db()
    # set up condition
    condition = 'KW_PID="{0}"'.format(pid)
    # get data frames
    dataframe = indexdbm.get_entries(columns, condition=condition)
    # return the
    return dataframe


# =============================================================================
# Define timing stats functions
# =============================================================================
def timing_stats(params: ParamDict, recipe: DrsRecipe):
    """
    Print and plot timing stats

    :param params:
    :param recipe:
    :return:
    """
    # print progress
    WLOG(params, 'info', 'Running timing code')
    # get log entries
    log_entries = get_log_entries(params, mode='timing')
    # -------------------------------------------------------------------------
    # get stats
    stat_dict = get_timing_stats(log_entries)
    # loop around recipe and print stats
    for recipe_name in stat_dict:
        print_timing_stats(params, recipe_name, stat_dict[recipe_name])
    # -------------------------------------------------------------------------
    # plot timing graph
    recipe.plot('STATS_TIMING_PLOT', logs=log_entries)


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
        stats['MEAN'] = np.nanmean(durations[rmask])
        stats['MEDIAN'] = np.nanmedian(durations[rmask])
        stats['SHORTEST'] = np.nanmin(durations[rmask])
        stats['LONGEST'] = np.nanmax(durations[rmask])
        stats['STD'] = np.nanstd(durations[rmask])
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


def print_timing_stats(params: ParamDict, recipe: str, stats: Dict[str, Any]):
    WLOG(params, 'info', '='*50)
    WLOG(params, 'info', '\t{0}'.format(recipe))
    WLOG(params, 'info', '='*50)
    # print stats
    statstr = ('\n\tMean Time: {MEAN:.3f} s +/- {STD:.3f}'
               '\n\tMed Time: {MEDIAN:.3f} s +/- {STD:.3f}'
               '\n\tRange: {SHORTEST:.3f} s to {LONGEST:.3f}'
               '\n\tNruns: {NUMBER}'
               '\n\tTotal Time: {TOTALTIME_HR:.3f} hr'
               '\n\tTotal CPU Time: {CPU_TIME_HR:.3f} hr (x{SPEED_UP:.2f})'
               '\n')
    WLOG(params, '', statstr.format(**stats))


# =============================================================================
# Define timing stats functions
# =============================================================================
def qc_stats(params: ParamDict, recipe: DrsRecipe):
    """
    Print and plot quality control / running / error stats

    :param params:
    :param recipe:
    :return:
    """
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
        # produce the plots
        # TODO: finish this
        recipe.plot('STAT_QC_RECIPE_PLOT', stats=stat_dict[recipe_name],
                    crit=stat_crit[recipe_name], qc=stat_qc[recipe_name])





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


def _sort_sublevel(data) -> List[str]:
    """
    Remove any static variables from the criteria

    :param criteria: pandas data, the sublevel criteria

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
                qcv = list(map(qcvfunc,  rlogs))
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
    WLOG(params, 'info', '='*50)
    WLOG(params, 'info', '\t{0}'.format(recipe_name))
    WLOG(params, 'info', '='*50)
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

    mean = np.nanmean(valid_values)
    median = np.nanmedian(valid_values)
    maximum = np.nanmax(valid_values)
    minimum = np.nanmin(valid_values)

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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
