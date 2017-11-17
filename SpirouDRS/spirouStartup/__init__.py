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
__all__ = ['RunInitialStartup', 'RunStartup']

# =============================================================================
# Function aliases
# =============================================================================
# Runs the initial start up script (checking of parameters and title)
RunInitialStartup = spirouStartup.run_inital_startup

# Runs the start up script
RunStartup = spirouStartup.run_startup

# =============================================================================
# End of code
# =============================================================================
