#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-13 at 15:30

@author: cook
"""
from __future__ import division
from astropy.table import Table
import numpy as np
import os
import glob
from collections import OrderedDict

from apero.core import constants
from apero.locale import drs_text
from apero.core.core import drs_log


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_log_stats.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = drs_text.TextEntry
TextDict = drs_text.TextDict
HelpText = drs_text.HelpDict
# define columns from log files
RECIPECOL = 'RECIPE'
STARTCOL = 'STARTED'
PASSEDCOL = 'PASSED_QC'
ENDCOL = 'ENDED'

# =============================================================================
# Define functions
# =============================================================================
def get_log_files(params, recipe, path, nightname=None):
    # ----------------------------------------------------------------------
    # load night names
    files = glob.glob(os.path.join(path, '*'))
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, 'info', 'Finding night directories for {0}'.format(path))
    # find directories
    nights = []
    # loop around files
    for filepath in files:
        # get basename
        basename = os.path.basename(filepath)
        # deal with having a night name set
        if nightname not in [None, 'None', '']:
            if basename == nightname:
                nights.append(filepath)
        elif os.path.isdir(filepath):
            nights.append(filepath)
    # log how many nights found
    if len(nights) > 0:
        WLOG(params, '', 'Found {0} night directories'.format(len(nights)))
    else:
        WLOG(params, 'error', 'No night directories found.')
    # ----------------------------------------------------------------------
    # locate log files
    logfitsfile = recipe.log.logfitsfile
    # log files
    logfiles, nightnames = [], []
    # loop around nights
    for night in nights:
        # get absolute path
        abspath = os.path.join(night, logfitsfile)
        # see if file exists
        if os.path.exists(abspath):
            logfiles.append(abspath)
            nightnames.append(os.path.basename(night))
    # log how many log files found
    if len(logfiles) > 0:
        WLOG(params, '', 'Found {0} night directories'.format(len(logfiles)))
    else:
        WLOG(params, 'error', 'No night directories found.')
    # return the log files and night names
    return logfiles, nightnames



def make_log_table(params, logfiles, nightnames):
    # log progress
    WLOG(params, '', 'Loading log files')
    # define dict storage
    masterdict = OrderedDict()
    # loop around log files and open them into storage
    for l_it, logfile in enumerate(logfiles):
        # print progress
        WLOG(params, '', '\t - Loading {0}'.format(logfile))
        # open file
        table = Table.read(logfile, format='fits')
        # add a night column to masterdict
        if 'NIGHT' not in masterdict:
            masterdict['NIGHT'] = [nightnames[l_it]] * len(table)
        else:
            masterdict['NIGHT'] += [nightnames[l_it]] * len(table)
        # now add columsn from table
        for col in table.colnames:
            if col not in masterdict:
                masterdict[col] = list(table[col])
            else:
                masterdict[col] += list(table[col])
    # once we have the master dict convert to table
    mastertable = Table()
    for col in masterdict:
        mastertable[col] = masterdict[col]
    # return master table
    return mastertable


def calculate_stats(params, recipe, mastertable):

    # get unique recipes
    urecipes = np.unique(mastertable[RECIPECOL])

    # store stats
    started_stats = OrderedDict()
    passed_stats = OrderedDict()
    ended_stats = OrderedDict()

    started_arr, passed_arr, ended_arr = [], [] ,[]

    # count how many started, passed qc and ended
    for urecipe in urecipes:
        # mask the table
        mask = mastertable[RECIPECOL] == urecipe
        # started
        started = np.sum(mask & mastertable[STARTCOL])
        # passed qc
        passed = np.sum(mask & mastertable[PASSEDCOL])
        # ended
        ended = np.sum(mask & mastertable[ENDCOL])
        # append stats to dict
        started_stats[urecipe] = started
        passed_stats [urecipe] = passed
        ended_stats[urecipe] = ended

        started_arr.append(started)
        passed_arr.append(passed)
        ended_arr.append(ended)

    # make arrays
    x = np.arange(0, len(urecipes))
    started_arr = np.array(started_arr)
    passed_arr = np.array(passed_arr)
    ended_arr = np.array(ended_arr)
    # print stats
    for urecipe in urecipes:
        started = started_stats[urecipe]
        passed = passed_stats [urecipe]
        ended = ended_stats[urecipe]

        WLOG(params, 'info', 'Recipe = {0}'.format(urecipe))
        WLOG(params, '', '\t Started: {0}'.format(started))

        uargs = [passed, started - passed, 100 * (started - passed) / started]
        msg = '\t passed qc: {0} failed qc: {1} ({2:.2f} %)'
        WLOG(params, '', msg.format(*uargs))

        uargs = [ended, started - ended, 100 * (started - ended) / started]
        msg = '\t finished: {0} unfinished: {1} ({2:.2f} %)'
        WLOG(params, '', msg.format(*uargs))

    # --------------------------------------------------------------
    # plot bar plot
    pkwargs = dict(started=started_arr, passed=passed_arr, ended=ended_arr,
                   urecipes=urecipes)
    recipe.plot('LOGSTATS_BAR', **pkwargs)


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
