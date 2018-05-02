#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-05-01 at 12:32

@author: cook
"""
from __future__ import division
import sys
import os
import time
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS.spirouUnitTests import spirouUnitRecipes
from SpirouDRS.spirouUnitTests import unit_test_comp_functions as utc


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
OLDPATH = '/scratch/Projects/SPIRou_Pipeline/data/reduced/20170710'
# plot path
RESULTSPATH = '/scratch/Projects/spirou_py3/unit_test_graphs/'
# -----------------------------------------------------------------------------
# list of valid recipes (first argument of each run)
VALID = spirouUnitRecipes.VALID_RECIPES
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def set_type(p, rparams):
    # check that "type" defined in run file
    if 'TYPE' not in rparams:
        emsg1 = '"type" not defined in run file = {0}'.format(p['rfile'])
        emsg2 = '    "type" must be set'
        emsg3 = '    "type" must be: "H2RG", "H4RG" or a valid path'
        WLOG('error', p['log_opt'], [emsg1, emsg2, emsg3])
    # set the type from parameter
    if rparams['TYPE'] == 'H2RG':
        os.environ[UCONFIG_VAR] = H2RG_USER_PATH
    elif rparams['TYPE'] == 'H4RG':
        os.environ[UCONFIG_VAR] = H4RG_USER_PATH
    # else we expect a valid path
    else:
        # check path exists
        if not os.path.exists(rparams['TYPE']):
            emsg1 = '"type" must be: "H2RG", "H4RG" or a valid path'
            emsg2 = '   "type" = {0}'.format(rparams['TYPE'])
            WLOG('error', p['log_opt'], [emsg1, emsg2])
        else:
            os.environ[UCONFIG_VAR] = rparams['TYPE']


def unset_type():
    """
    Unset type from environment before ending the code
    :return:
    """
    del os.environ[UCONFIG_VAR]


def set_comp(p, rparams):
    # check that "comparison" defined in run file
    if 'COMPARISON' not in rparams:
        emsg1 = '"comparison" not defined in run file {0}'.format(p['rfile'])
        emsg2 = '    "comparison" must be set'
        emsg3 = '    "comparison" must be either "True" or "False"'
        WLOG('error', p['log_opt'], [emsg1, emsg2, emsg3])
    # set the comparison from parameter
    try:
        comp = bool(rparams['COMPARISON'])
    except:
        emsg1 = '"comparison" must be either "True" or "False"'
        emsg2 = '    "comparison" = {0}'.format(rparams['COMPARISON'])
        WLOG('error', p['log_opt'], [emsg1, emsg2])
        comp = False
    # return comp
    return comp


def get_runs(p, rparams):
    # set up storage
    runs = OrderedDict()
    # loop around the rparams and add keys with "RUN_KEY"
    for key in list(rparams.keys()):
        if key.startswith(RUN_KEY):
            #  get this iteration parameter
            run_i = rparams[key]

            # check if run_i is a list
            if type(run_i) != list:
                emsg1 = '"{0}" is not a valid python list'.format(key)
                emsg2 = '   {0}={1}'.format(key, run_i)
                WLOG('error', p['log_opt'], [emsg1, emsg2])
            # check that first entry is a valid recipe
            if run_i[0] not in VALID:
                emsg1 = '"{0}" does not start with a valid DRS recipe'
                emsg2 = '   {0}[0]={1}'.format(key, run_i[0])
                WLOG('error', p['log_opt'], [emsg1, emsg2])
            # append to runs
            runs[key] = run_i
    # make sure we have some runs
    if len(runs) == 0:
        eargs = [RUN_KEY, p['rfile']]
        emsg = 'No runs ("{0}## = ") found in file {1}'
        WLOG('error', p['log_opt'], emsg.format(*eargs))
    # return runs
    return runs


def unit_log_title(p, title=' START OF UNIT TESTS'):
    WLOG('', p['log_opt'], '')
    WLOG('warning', p['log_opt'], spirouStartup.spirouStartup.HEADER)
    WLOG('warning', p['log_opt'], title)
    WLOG('warning', p['log_opt'], spirouStartup.spirouStartup.HEADER)
    WLOG('', p['log_opt'], '')


def log_timings(p, times):
    WLOG('', p['log_opt'], '')
    WLOG('', p['log_opt'], spirouStartup.spirouStartup.HEADER)
    WLOG('', p['log_opt'], ' TIMING STATS')
    WLOG('', p['log_opt'], spirouStartup.spirouStartup.HEADER)
    WLOG('', p['log_opt'], '')
    # Now print the stats for this test:
    for key in list(times.keys()):
        msg = '\t{0}\tTime taken = {1:.3f} s'.format(key, times[key])
        WLOG('', p['log_opt'], msg)
    WLOG('', p['log_opt'], '')


def manage_run(p, runname, run_i, timing, new_out, old_out,
               errors, compare=False):
    # get name of run (should be first element in run list
    name = run_i[0]
    runtitle = '{0}:{1}'.format(runname, name)
    # flush sys.argv
    sys.argv = [runtitle]
    # display run title
    unit_log_title(p, ' ' + runtitle)
    # deal with arguments and generate list of expected outputs
    args = spirouUnitRecipes.wrapper(p, runname, run_i)
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
    # get outputs
    ll['outputs'] = spirouUnitRecipes.wrapper(p, runname, run_i, ll)
    # comparison (if required)
    if compare:
        # set the file path for the comparison results (plots and table)
        filepath = utc.get_folder_name(RESULTSPATH)
        # run the comparison function
        cargs = [name, ll, new_out, old_out, errors, OLDPATH, filepath]
        new_out, old_out, errors = utc.compare(*cargs)
    # return the timing and the new and old outputs
    return timing, new_out, old_out


# =============================================================================
# End of code
# =============================================================================
