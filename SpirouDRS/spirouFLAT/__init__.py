#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-14 at 15:37

@author: cook



Version 0.0.0
"""

from SpirouDRS import spirouConfig
from . import spirouFLAT

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouFLAT.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['MeasureBlazeForOrder']

# =============================================================================
# Function aliases
# =============================================================================
MeasureBlazeForOrder = spirouFLAT.measure_blaze_for_order

# =============================================================================
# End of code
# =============================================================================
