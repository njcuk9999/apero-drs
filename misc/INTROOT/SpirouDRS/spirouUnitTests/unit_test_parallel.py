#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-18 at 15:26

@author: cook
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict
from multiprocessing import Process

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTools

# TODO: This is a stupid fix for python 2 - should be done better
try:
    from . import spirouUnitTests
except ImportError:
    from SpirouDRS.spirouUnitTests import spirouUnitTests
except ValueError:
    import spirouUnitTests


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
# define the unit test run folder
UNIT_PATH = os.path.dirname(spirouUnitTests.__file__)
UNIT_TEST_PATH = os.path.join(UNIT_PATH, 'Runs')

# Max Processes
MAX_PROCESSES = 10


# =============================================================================
# Define functions
# =============================================================================
def unit_wrapper(p, runs):
    # storage for times
    times = OrderedDict()
    errors = OrderedDict()
    # log the start of the unit tests
    spirouUnitTests.unit_log_title(p)
    # loop around runs and process each
    for runn in list(runs.keys()):
        # try to run
        try:
            # do run
            rargs = [p, runn, runs[runn], times]
            times = spirouUnitTests.manage_run(*rargs)
        # Manage unexpected errors
        except Exception as e:
            wmsgs = ['Run "{0}" had an unexpected error:'.format(runn)]
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(p, 'warning', wmsgs)
            errors[runn] = str(e)
        # Manage expected errors
        except SystemExit as e:
            wmsgs = ['Run "{0}" had an expected error:'.format(runn)]
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(p, 'warning', wmsgs)
            errors[runn] = str(e)

    # make sure all plots are closed
    sPlt.closeall()
    # return times
    return times, errors


def group_runs(runs):
    # define storage for group runs
    groups = OrderedDict()
    # start group number at zero
    group_number = 0
    # start group program is None
    group_program = None
    # loop around runs
    for runn in runs:
        # get iteration program
        program = runs[runn][0]
        # get group program
        if group_program is None:
            group_program = str(program)
            group_number += 1
        elif program != group_program:
            group_program = str(program)
            group_number += 1
        else:
            group_program = str(group_program)
            group_number += 0

        # get key name
        group_name = 'Group{0:03d}'.format(group_number)
        # add run to group
        if group_name not in groups:
            groups[group_name] = [runs[runn]]
        else:
            groups[group_name].append(runs[runn])
    # return group runs
    return groups


def parallelize(groups, max_number):

    new_groups = OrderedDict()

    for group_name in groups:
        # get the length of groups
        group_length = len(groups[group_name])
        # get the max length of sub groups
        max_length = int(np.ceil(group_length / max_number))
        # set up the iteration
        sub_group = []
        # loop around elements in this group
        for element in groups[group_name]:
            if group_name not in new_groups:
                new_groups[group_name] = []
            # end group if longer than max_number
            if len(sub_group) >= max_length:
                new_groups[group_name].append(sub_group)
                sub_group = []
            # append to next group
            sub_group.append(element)
        # make sure to add last group!
        new_groups[group_name].append(sub_group)
    # return new groups with subgroups
    return new_groups


def make_subgroup_dict(sub_group, group_name):
    sruns = OrderedDict()
    for it, element in enumerate(sub_group):
        # construct name for run
        sname = '{0}-{1:03d}'.format(group_name, it)
        sruns[sname] = element
    return sruns


def main(runname=None, quiet=False):

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__, quiet=True)
    # now get custom arguments
    ckwargs = dict(positions=[0], types=[str], names=['RUNNAME'],
                   calls=[runname], require_night_name=False,
                   required=[False])
    customargs = spirouStartup.GetCustomFromRuntime(p, **ckwargs)
    # add custom args straight to p
    p = spirouStartup.LoadMinimum(p, customargs=customargs)

    # ----------------------------------------------------------------------
    # Read the run file and extract parameters
    # ----------------------------------------------------------------------
    # construct filename
    rfile = os.path.join(UNIT_TEST_PATH, p['RUNNAME'])

    # check if RUNNAME is None
    if p['RUNNAME'] == 'None':
        exists = False
        emsgs = ['No unit test run file defined.']
    # check that rfile exists
    elif not os.path.exists(rfile):
        emsgs = ['Unit test run file "{0}" does not exist'.format(rfile)]
        exists = False
    else:
        exists = True
        emsgs = []
    # deal with file wrong (or no file defined) --> print valid unit tests
    if not exists:
        emsgs.append('')
        emsgs.append('Available units tests are:')
        for rfile in os.listdir(UNIT_TEST_PATH):
            emsgs.append('\t{0}'.format(rfile))
        emsgs.append('')
        emsgs.append('Located at {0}'.format(UNIT_TEST_PATH))
        WLOG(p, 'error', emsgs)

    # get the parameters in the run file
    rparams = spirouConfig.GetConfigParams(p, filename=rfile)

    # reset the DRS
    if not quiet:
        spirouTools.DRS_Reset(log=False, called=True)

    # ----------------------------------------------------------------------
    # Get runs
    # ----------------------------------------------------------------------
    runs = spirouUnitTests.get_runs(p, rparams, rfile)

    # ----------------------------------------------------------------------
    # group runs (for parallelisation)
    # ----------------------------------------------------------------------
    # get groups that can be run in parallel
    groups = group_runs(runs)
    # split groups by max number of processes
    groups = parallelize(groups, MAX_PROCESSES)
    # loop around groups
    for group_name in groups:
        # process storage
        pp = []
        # loop around sub groups (to be run at the same time)
        for sub_group in groups[group_name]:
            # make sub_group a dict
            sruns = make_subgroup_dict(sub_group, group_name)
            # do parallel run
            process = Process(target=unit_wrapper, args=(p, sruns))
            process.start()
            pp.append(process)
        # do not continue until
        for process in pp:
            while process.is_alive():
                pass
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(p, 'info', wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
