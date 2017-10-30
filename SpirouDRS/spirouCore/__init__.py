#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:10

@author: cook



Version 0.0.0
"""

from . import spirouConfig
from . import spirouLog
from . import spirouStartup


# Reads the config file and loads all variables into dictionary
ReadConfigFile = spirouConfig.read_config_file

# Runs the initial start up script (checking of parameters and title)
RunInitialStartup = spirouStartup.run_inital_startup

# Runs the start up script
RunStartup = spirouStartup.run_startup

# The stdout/log file controller
wlog = spirouLog.logger
