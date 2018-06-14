#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou flat fielding module

Created on 2017-11-14 at 15:37

@author: cook

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
__all__ = ['GetFlat', 'GetValidOrders', 'MeasureBlazeForOrder']

# =============================================================================
# Function aliases
# =============================================================================
GetFlat = spirouFLAT.get_flat

MeasureBlazeForOrder = spirouFLAT.measure_blaze_for_order

GetValidOrders = spirouFLAT.get_valid_orders

# =============================================================================
# End of code
# =============================================================================
