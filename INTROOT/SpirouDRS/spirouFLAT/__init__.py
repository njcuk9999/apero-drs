#!/usr/bin/env python3
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
__all__ = ['MeasureBlazeForOrder']

# =============================================================================
# Function aliases
# =============================================================================
MeasureBlazeForOrder = spirouFLAT.measure_blaze_for_order
"""
Measure the blaze function (for good pixels this is a polynomial fit of
order = fitdegree, for bad pixels = 1.0).

bad pixels are defined as less than or equal to zero

:param y: numpy array (1D), the extracted pixels for this order
:param fitdegree: int, the polynomial degree

:return blaze: numpy array (1D), size = len(y), the blaze function: for
               good pixels this is the value of the fit, for bad pixels the
               value = 1.0
"""

# =============================================================================
# End of code
# =============================================================================
