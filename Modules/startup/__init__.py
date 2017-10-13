#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__init__.py

startup module controller

Created on 2017-10-11 at 10:43

@author: cook

Version 0.0.1
"""
from . import configsetup
from . import startupfunctions
from . import log
from . import spirouCDB

__all__ = ['PutFile', 'ReadConfigFile', 'RunInitialStartup', 'RunStartup',
           'UpdateMaster', 'wlog']
__author__ = 'Neil Cook'
__version__ = '0.0.1'

# =============================================================================
# Define functions
# =============================================================================
# Copies the "inputfile" to the calibDB folder
PutFile = spirouCDB.put_file

# Reads the config file and loads all variables into dictionary
ReadConfigFile = configsetup.read_config_file

# Runs the initial start up script (checking of parameters and title)
RunInitialStartup = startupfunctions.run_inital_startup

# Runs the start up script
RunStartup = startupfunctions.run_startup

# Updates (or creates) the calibDB with an entry or entries in the form:
#    {key} {arg_night_name} {filename} {human_time} {unix_time}
UpdateMaster = spirouCDB.update_datebase

# The stdout/log file controller
wlog = log.logger
