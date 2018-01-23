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
__all__ = ['Begin', 'GetCustomFromRuntime', 'GetFile', 'GetFiberType',
           'LoadArguments', 'InitialFileSetup']

# =============================================================================
# Function aliases
# =============================================================================

Begin = spirouStartup.run_begin

# Get custom args from run time args (sys.argv)
GetCustomFromRuntime = spirouStartup.get_custom_from_run_time_args

# get a file from a dir name and file name + prefixes
GetFile = spirouStartup.get_file

# get the fiber type from a filename
GetFiberType = spirouStartup.get_fiber_type

# Runs the initial start up script (checking of parameters and title)
LoadArguments = spirouStartup.load_arguments

# Runs the start up script
InitialFileSetup = spirouStartup.initial_file_setup

# =============================================================================
# End of code
# =============================================================================
