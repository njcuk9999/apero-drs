#!/usr/bin/env python
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
__all__ = ['Begin', 'DisplayTitle', 'DisplaySysInfo', 'Exit',
           'GetCustomFromRuntime', 'GetFile', 'GetFiles',
           'InitialFileSetup', 'LoadArguments', 'LoadMinimum',
           'LoadOtherConfig', 'LoadCalibDB', 'MultiFileSetup',
           'SingleFileSetup']

# =============================================================================
# Function aliases
# =============================================================================

Begin = spirouStartup.run_begin

DisplayTitle = spirouStartup.display_title

DisplaySysInfo = spirouStartup.display_system_info

Exit = spirouStartup.exit_script

GetCustomFromRuntime = spirouStartup.get_custom_from_run_time_args

GetFile = spirouStartup.get_file

GetFiles = spirouStartup.get_files

InitialFileSetup = spirouStartup.initial_file_setup

LoadArguments = spirouStartup.load_arguments

LoadMinimum = spirouStartup.load_minimum

LoadOtherConfig = spirouStartup.load_other_config_file

LoadCalibDB = spirouStartup.load_calibdb

MultiFileSetup = spirouStartup.multi_file_setup

SingleFileSetup = spirouStartup.single_file_setup



# =============================================================================
# End of code
# =============================================================================
