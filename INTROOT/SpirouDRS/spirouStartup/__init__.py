#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialization code for Spirou startup module

Created on 2017-11-17 at 13:38

@author: cook

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

GetCustomFromRuntime = spirouStartup.get_custom_from_run_time_args

GetFile = spirouStartup.get_file

GetFiles = spirouStartup.get_files

GetFiberType = spirouStartup.get_fiber_type

LoadArguments = spirouStartup.load_arguments

InitialFileSetup = spirouStartup.initial_file_setup

LoadCalibDB = spirouStartup.load_calibdb

# =============================================================================
# End of code
# =============================================================================
