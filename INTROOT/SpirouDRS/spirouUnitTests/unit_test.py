#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit test parser (runs unittest.run files)

Created on 2018-05-01 11:31:14

@author: cook
"""
from __future__ import division
import sys
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouUnitTests
from SpirouDRS import spirouTools

if sys.version_info.major == 2:
    # noinspection PyPep8Naming,PyShadowingBuiltins
    from collections import OrderedDict as dict


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


# =============================================================================
# Define main function
# =============================================================================
def main(runname=None, quiet=False):

    # reset the DRS
    if not quiet:
        spirouTools.DRS_Reset(log=False, called=True)

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(quiet=True)
    # now get custom arguments
    ckwargs = dict(positions=[0], types=[str], names=['RUNNAME'],
                   calls=[runname], require_night_name=False)
    customargs = spirouStartup.GetCustomFromRuntime(**ckwargs)
    # add custom args straight to p
    p = spirouStartup.LoadMinimum(p, customargs=customargs)

    # ----------------------------------------------------------------------
    # Read the run file and extract parameters
    # ----------------------------------------------------------------------
    # construct filename
    rfile = os.path.join(UNIT_TEST_PATH, p['RUNNAME'])
    # check that rfile exists
    if not os.path.exists(rfile):
        emsg = 'Unit test run file "{0}" does not exist'
        WLOG('error', p['log_opt'], emsg.format(rfile))
    # get the parameters in the run file
    rparams = spirouConfig.GetConfigParams(p, None, filename=rfile)

    # ----------------------------------------------------------------------
    # Set the type from run parameters
    # ----------------------------------------------------------------------
    # TODO: Remove H2RG compatibility
    spirouUnitTests.CheckType(p, rparams)

    # ----------------------------------------------------------------------
    # Check whether we need to compare files
    # ----------------------------------------------------------------------
    compare = spirouUnitTests.SetComp(p, rparams)

    # ----------------------------------------------------------------------
    # Get runs
    # ----------------------------------------------------------------------
    runs = spirouUnitTests.GetRuns(p, rparams)

    # ----------------------------------------------------------------------
    # Get runs
    # ----------------------------------------------------------------------
    # storage for times
    times = dict()
    # storage for outputs
    newoutputs, oldoutputs = dict(), dict()
    # storage for errors
    errors = []
    # log the start of the unit tests
    spirouUnitTests.UnitLogTitle(p)
    # loop around runs and process each
    for runn in list(runs.keys()):
        # do run
        rargs = [p, runn, runs[runn], times, newoutputs, oldoutputs,
                 errors, compare]
        times, newoutputs, oldoutputs = spirouUnitTests.ManageRun(*rargs)

    # ----------------------------------------------------------------------
    # Print timings
    # ----------------------------------------------------------------------
    spirouUnitTests.LogTimings(p, times)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))
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
