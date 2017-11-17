#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:10

@author: cook



Version 0.0.0
"""
from SpirouDRS import spirouConfig
from . import spirouLog
from . import spirouPlot
from . import spirouMath

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouCore.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__all__ = ['wlog',
           'sPlt']

# =============================================================================
# Function aliases
# =============================================================================
# The stdout/log file controller
wlog = spirouLog.logger

# Plotting functions alias
sPlt = spirouPlot

# =============================================================================
# End of code
# =============================================================================
