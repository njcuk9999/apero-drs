#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit test parser (runs unittest.run files)

Created on 2018-05-01 11:31:14

@author: cook
"""
from __future__ import division
import os
from collections import OrderedDict

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


# =============================================================================
# Define main function
# =============================================================================
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
    p = spirouStartup.LoadMinimum(p, customargs=customargs, quiet=True)

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
        spirouTools.DRS_Reset(log=True, called=True)

    # ----------------------------------------------------------------------
    # Get runs
    # ----------------------------------------------------------------------
    runs = spirouUnitTests.get_runs(p, rparams, rfile)

    # ----------------------------------------------------------------------
    # Run runs
    # ----------------------------------------------------------------------
    # storage for times
    times = OrderedDict()
    errors = OrderedDict()
    # log the start of the unit tests
    spirouUnitTests.unit_log_title(p)
    # loop around runs and process each
    for runn in list(runs.keys()):
        if p['DRS_DEBUG'] > 0:
            # do run
            rargs = [p, runn, runs[runn], times]
            times = spirouUnitTests.manage_run(*rargs)
        else:
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

    # ----------------------------------------------------------------------
    # Make sure all plots are close
    # ----------------------------------------------------------------------
    sPlt.closeall()

    # ----------------------------------------------------------------------
    # Print timings
    # ----------------------------------------------------------------------
    spirouUnitTests.log_timings(p, times)

    # ----------------------------------------------------------------------
    # Print errors
    # ----------------------------------------------------------------------
    spirouUnitTests.log_errors(p, errors)

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
