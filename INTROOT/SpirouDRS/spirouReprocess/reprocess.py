#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-10 at 10:49

@author: cook
"""
from __future__ import division

from SpirouDRS import spirouReprocess
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'extract_trigger.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get param dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================
# def main(runfile=None):
if True:
    runfile = 'run_test002.ini'

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, require_night_name=False)
    # deal with run file
    p, runtable = spirouReprocess.RunFile(p, runfile)

    # ----------------------------------------------------------------------
    # find all files
    # ----------------------------------------------------------------------
    WLOG(p, 'info', 'Finding all raw files')
    rawtable, rawpath = spirouReprocess.FindRawFiles(p)
    WLOG(p, 'info', 'Finding all pp files')
    tmptable, tmppath = spirouReprocess.FindTmpFiles(p)
    WLOG(p, 'info', 'Finding all reduced files')
    redtable, redpath = spirouReprocess.FindRedFiles(p)
    # store in lists
    tables = [rawtable, tmptable, redtable]
    paths = [rawpath, tmppath, redpath]

    # ----------------------------------------------------------------------
    # Generate run list
    # ----------------------------------------------------------------------
    runlist = spirouReprocess.GenerateRunList(p, tables, paths, runtable)


    # ----------------------------------------------------------------------
    # Process run list
    # ----------------------------------------------------------------------



# =============================================================================
# Start of code
# =============================================================================
# if __name__ == "__main__":
#     # run main with no arguments (get from command line - sys.argv)
#     ll = main()
#     # exit message if in debug mode
#     spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
