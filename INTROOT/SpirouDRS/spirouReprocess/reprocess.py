#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-10 at 10:49

@author: cook
"""
from __future__ import division
import sys

from SpirouDRS import spirouReprocess
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'reprocess.py'
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
def main(runfile=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, require_night_name=False)
    # deal with run file
    p, runtable = spirouReprocess.RunFile(p, runfile)
    # reset sys.argv so it doesn't mess with recipes
    sys.argv = [__NAME__]
    # send email if configured
    spirouReprocess.SendEmail(p, kind='start')

    # ----------------------------------------------------------------------
    # Deal with reset options
    # ----------------------------------------------------------------------
    spirouReprocess.ResetFiles(p)

    # ----------------------------------------------------------------------
    # find all files
    # ----------------------------------------------------------------------
    WLOG(p, 'info', 'Finding all raw files')
    rawtable, rawpath = spirouReprocess.FindRawFiles(p)
    # WLOG(p, 'info', 'Finding all pp files')
    # tmptable, tmppath = spirouReprocess.FindTmpFiles(p)
    # WLOG(p, 'info', 'Finding all reduced files')
    # redtable, redpath = spirouReprocess.FindRedFiles(p)
    # store in lists
    tables = [rawtable]   # , tmptable, redtable]
    paths = [rawpath]  # , tmppath, redpath]

    # ----------------------------------------------------------------------
    # Generate run list
    # ----------------------------------------------------------------------
    runlist = spirouReprocess.GenerateRunList(p, tables, paths, runtable)

    # ----------------------------------------------------------------------
    # Process run list
    # ----------------------------------------------------------------------
    outlist = spirouReprocess.ProcessRunList(p, runlist)

    # ----------------------------------------------------------------------
    # Print timing
    # ----------------------------------------------------------------------
    # get header
    header = spirouConfig.Constants.HEADER()
    WLOG(p, '', '')
    WLOG(p, '', header)
    WLOG(p, '', 'Timings:')
    WLOG(p, '', header)
    WLOG(p, '', '')
    # loop around timings (non-errors only)
    for key in outlist:
        cond1 = len(outlist[key]['ERROR']) == 0
        cond2 = outlist[key]['TIMING'] is not None
        if cond1 and cond2:
            wmsg = 'ID={0:05d}  Time = {1}'
            WLOG(p, '', wmsg.format(key, outlist[key]['TIMING']))
            WLOG(p, 'warning', '\t{0}'.format(outlist[key]['RUNSTRING']),
                 wrap=False)

    # ----------------------------------------------------------------------
    # Print out any errors
    # ----------------------------------------------------------------------
    # get header
    header = spirouConfig.Constants.HEADER()
    WLOG(p, '', '')
    WLOG(p, '', header)
    WLOG(p, '', 'Errors:')
    WLOG(p, '', header)
    WLOG(p, '', '')
    # loop around each entry of outlist and print any errors
    for key in outlist:
        if len(outlist[key]['ERROR']) > 0:
            WLOG(p, '', '', colour='red')
            WLOG(p, '', header, colour='red')
            WLOG(p, 'warning', 'Error found for ID={0:05d}'.format(key),
                 colour='red', wrap=False)
            WLOG(p, 'warning', '\t{0}'.format(outlist[key]['RUNSTRING']),
                 colour='red', wrap=False)
            WLOG(p, '', header, colour='red')
            WLOG(p, '', '', colour='red')
            WLOG(p, 'warning', outlist[key]['ERROR'], colour='red', wrap=False)
            WLOG(p, '', '', colour='red')
            WLOG.printmessage(p, outlist[key]['TRACEBACK'], colour='red')
            WLOG(p, '', '', colour='red')
            WLOG(p, '', header, colour='red')

    # send email if configured
    spirouReprocess.SendEmail(p, kind='end')

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)

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
