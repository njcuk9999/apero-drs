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
from SpirouDRS import spirouTools

# TODO: This is a stupid fix for python 2 - should be done better
try:
    from . import spirouUnitTests
except ImportError:
    from SpirouDRS.spirouUnitTests import spirouUnitTests
except ValueError:
    import spirouUnitTests

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
                   calls=[runname], require_night_name=False,
                   required=[False])
    customargs = spirouStartup.GetCustomFromRuntime(**ckwargs)
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
        WLOG('error', p['LOG_OPT'], emsgs)

    # get the parameters in the run file
    rparams = spirouConfig.GetConfigParams(p, None, filename=rfile)

    # ----------------------------------------------------------------------
    # Set the type from run parameters
    # ----------------------------------------------------------------------
    # TODO: Remove H2RG compatibility
    spirouUnitTests.check_type(p, rparams)

    # ----------------------------------------------------------------------
    # Check whether we need to compare files
    # ----------------------------------------------------------------------
    compare = spirouUnitTests.set_comp(p, rparams)

    # ----------------------------------------------------------------------
    # Get runs
    # ----------------------------------------------------------------------
    runs = spirouUnitTests.get_runs(p, rparams, rfile)

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
    spirouUnitTests.unit_log_title(p)
    # loop around runs and process each
    for runn in list(runs.keys()):
        # do run
        rargs = [p, runn, runs[runn], times, newoutputs, oldoutputs,
                 errors, compare]
        times, newoutputs, oldoutputs = spirouUnitTests.manage_run(*rargs)

    # ----------------------------------------------------------------------
    # Print timings
    # ----------------------------------------------------------------------
    spirouUnitTests.log_timings(p, times)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
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
