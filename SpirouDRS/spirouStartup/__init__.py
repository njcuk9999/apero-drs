#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-17 at 13:38

@author: cook



Version 0.0.0
"""
from SpirouDRS import spirouConfig
from . import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouCore.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['RunInitialStartup', 'RunStartup']

# =============================================================================
# Function aliases
# =============================================================================

# Get custom args from run time args (sys.argv)
GetCustomFromRuntime = spirouStartup.get_custom_from_run_time_args

# get a file from a dir name and file name + prefixes
GetFile = spirouStartup.get_file

# get the fiber type from a filename
GetFiberType = spirouStartup.get_fiber_type

# Runs the initial start up script (checking of parameters and title)
RunInitialStartup = spirouStartup.run_initial_startup

# Runs the start up script
RunStartup = spirouStartup.run_startup

# =============================================================================
# End of code
# =============================================================================
