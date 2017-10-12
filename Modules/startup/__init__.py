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

__all__ = ['ReadConfigFile', 'RunInitialStartup', 'RunStartup', 'wlog']
__author__ = 'Neil Cook'
__version__ = '0.0.1'

# =============================================================================
# Define functions
# =============================================================================
# Reads the config file and loads all variables into dictionary
ReadConfigFile = configsetup.read_config_file
# Runs the initial start up script (checking of parameters and title)
RunInitialStartup = startupfunctions.run_inital_startup
# Runs the start up script
RunStartup = startupfunctions.run_startup
# The stdout/log file controller
wlog = log.logger
