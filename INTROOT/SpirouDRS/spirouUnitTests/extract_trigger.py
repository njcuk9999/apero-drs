#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-17 at 10:56

@author: cook
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'off_listing_RAW_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get param dictionary
ParamDict = spirouConfig.ParamDict
# skip found files
SKIP_DONE = False
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
#def main(night_name=None):
if True:
    night_name = None
    night_name = 'TEST1/20180805'

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, require_night_name=False)

    # ----------------------------------------------------------------------
    # Define paths
    # ----------------------------------------------------------------------
    if p['ARG_NIGHT_NAME'] == '':
        print('All files in {0}'.format(p['ARG_FILE_DIR']))
    else:
        print('Night name files in {0}'.format(p['ARG_FILE_DIR']))



def main(night_name=None):
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    # spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

