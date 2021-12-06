#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs stats

Module to compute stats on the drs

Created on 2021-12-06

@author: cook
"""
from astropy import units as uu
import numpy as np
from pandasql import sqldf
import pandas as pd
from typing import Any, Dict, List

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
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


# =============================================================================
# Define timing stats functions
# =============================================================================
class LogEntry:
    def __init__(self, pid: str, dataframe: pd.DataFrame):
        self.pid = str(pid)
        # fill out data
        self.dataframe = dataframe
        self.namespace = dict(data=dataframe)
        self.data = None
        # define properties
        self.recipe_name = 'None'
        self.shortname = 'None'
        self.block_kind = 'None'
        self.recipe_type = 'None'
        self.recipe_kind = 'None'
        self.start_time = np.nan
        self.end_time = np.nan
        self.duration = np.nan
        # flag for valid log entry
        self.is_valid = False

    def get_attributes(self):
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

        if self.recipe_type != 'recipe':
            self.is_valid = False
            return

        try:
            self.start_time = Time(self.data.iloc[0]['START_TIME']).unix
            self.end_time = Time(self.data.iloc[0]['END_TIME']).unix
            self.duration = self.end_time - self.start_time
            if np.isfinite(self.duration):
                self.is_valid = True
        except ValueError:
            self.is_valid = False

    def query(self, command: str):
        return sqldf(command, self.namespace)



def timing_stats(params: ParamDict, recipe: DrsRecipe):
    """
    Print and plot timing stats

    :param params:
    :param recipe:
    :return:
    """
    # load log database
    logdbm = drs_database.LogDatabase(params)
    logdbm.load_db()
    # print progress
    WLOG(params, 'info', 'Running timing code')
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
        log_entry.get_attributes()
        # append to log entry storage list
        if log_entry.is_valid:
            log_entries.append(log_entry)
    # -------------------------------------------------------------------------
    # get stats
    stat_dict = get_stats(log_entries)
    # loop around recipe and print stats
    for recipe_name in stat_dict:
        print_stats(params, recipe_name, stat_dict[recipe_name])
    # -------------------------------------------------------------------------
    # plot timing graph
    recipe.plot('STATS_TIMING_PLOT', logs=log_entries)


def get_stats(logs: List[LogEntry]) -> Dict[str, Dict[str, Any]]:
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

    return recipe_dict


def print_stats(params: ParamDict, recipe: str, stats: Dict[str, Any]):
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
def qc_stats(params: ParamDict):
    pass


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
