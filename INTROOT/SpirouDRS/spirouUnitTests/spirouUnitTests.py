#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-05-01 at 12:32

@author: cook
"""
from __future__ import division
import numpy as np
import sys
import time
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup


# TODO: This is a stupid fix for python 2 - should be done better
try:
    from . import spirouUnitRecipes
except ImportError:
    from SpirouDRS.spirouUnitTests import spirouUnitRecipes
except ValueError:
    import spirouUnitRecipes


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'unit_test.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Define the environmental variable that controls user custom config path
UCONFIG_VAR = 'DRS_UCONFIG'
# define the key in the run files to define keys
RUN_KEY = 'RUN'
# set the user paths
H2RG_USER_PATH = '~/spirou_config_H2RG/'
H4RG_USER_PATH = '~/spirou_config_H4RG/'
# define old version reduced path
OLDPATH = '/scratch/Projects/SPIRou_Pipeline/data/reduced/'
# plot and save path
RESULTSPATH = '/scratch/Projects/spirou_py3/unit_test_graphs/'
# threshold for difference pass (comparison)
THRESHOLD = -8
# -----------------------------------------------------------------------------
# list of valid recipes (first argument of each run)
VALID = spirouUnitRecipes.VALID_RECIPES
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def get_runs(p, rparams, rfile):
    # set up storage
    runs = OrderedDict()
    # loop around the rparams and add keys with "RUN_KEY"
    for key in list(rparams.keys()):
        if key.upper().startswith(RUN_KEY.upper()):
            #  get this iteration parameter
            run_i = rparams[key]

            # check if run_i is a list
            if type(run_i) != list:
                emsg1 = '"{0}" is not a valid python list'.format(key)
                emsg2 = '   {0}={1}'.format(key, run_i)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
            # check that first entry is a valid recipe
            if run_i[0] not in VALID:
                emsg1 = ('"{0}" does not start with a valid DRS recipe'
                         '').format(key)
                emsg2 = '   {0}[0]={1}'.format(key, run_i[0])
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
            # append to runs
            runs[key] = run_i
    # make sure we have some runs
    if len(runs) == 0:
        eargs = [RUN_KEY, rfile]
        emsg = 'No runs ("{0}## = ") found in file {1}'
        WLOG('error', p['LOG_OPT'], emsg.format(*eargs))
    # sort into order
    unsorted = np.array(list(runs.keys()))
    sorted = np.sort(unsorted)
    # add an OrderedDict
    sorted_runs = OrderedDict()
    # add runs to new dictionary in the correct order
    for run_i in sorted:
        sorted_runs[run_i] = runs[run_i]
    # return runs
    return sorted_runs


def unit_log_title(p, title=' START OF UNIT TESTS'):
    WLOG('', p['LOG_OPT'], '')
    WLOG('warning', p['LOG_OPT'], spirouStartup.spirouStartup.HEADER)
    WLOG('warning', p['LOG_OPT'], title)
    WLOG('warning', p['LOG_OPT'], spirouStartup.spirouStartup.HEADER)
    WLOG('', p['LOG_OPT'], '')


def log_timings(p, times):

    # add times together
    times['Total'] = np.sum(list(times.values()))
    # log the times
    WLOG('', p['LOG_OPT'], '')
    WLOG('', p['LOG_OPT'], spirouStartup.spirouStartup.HEADER)
    title = ' TIMING STATS: {RUNNAME} (V{DRS_VERSION})'.format(**p)
    WLOG('', p['LOG_OPT'], title)
    WLOG('', p['LOG_OPT'], spirouStartup.spirouStartup.HEADER)
    WLOG('', p['LOG_OPT'], '')
    # Now print the stats for this test:
    for key in list(times.keys()):
        msg = '  {0:35s} Time taken = {1:.3f} s'.format(key, times[key])
        WLOG('', p['LOG_OPT'], msg)
    WLOG('', p['LOG_OPT'], '')


def log_errors(p, errors):
    # log the times
    WLOG('', p['LOG_OPT'], '')
    WLOG('', p['LOG_OPT'], spirouStartup.spirouStartup.HEADER)
    title = ' ERRORS: {RUNNAME} (V{DRS_VERSION})'.format(**p)
    WLOG('', p['LOG_OPT'], title)
    WLOG('', p['LOG_OPT'], spirouStartup.spirouStartup.HEADER)
    WLOG('', p['LOG_OPT'], '')

    for error in errors:
        msg = 'Run {0} error = {1}'
        WLOG('warning', p['LOG_OPT'], msg.format(error, errors[error]))


def manage_run(p, runname, run_i, timing):
    # get name of run (should be first element in run list
    name = run_i[0]
    runtitle = '{0}:{1}'.format(runname, name)
    # flush sys.argv
    sys.argv = [runtitle]
    # display run title
    unit_log_title(p, ' ' + runtitle)
    # deal with arguments and generate list of expected outputs
    args, name = spirouUnitRecipes.wrapper(p, runname, run_i)
    # start timer
    starttime = time.time()
    # run program
    ll = spirouUnitRecipes.run_main(p, name, args)
    # end timer
    endtime = time.time()
    # deal with closing plots
    sPlt.closeall()
    # add to timer
    timing['{0}:{1}'.format(runname, name)] = endtime - starttime
    # return the timing
    return timing


# =============================================================================
# End of code
# =============================================================================
