#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-21 at 11:52

@author: cook



Version 0.0.0
"""

from SpirouDRS import spirouConfig
from . import spirouRV

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouRV.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__all__ = ['DeltaVrms2D']

# =============================================================================
# Function aliases
# =============================================================================
# Compute the photon noise uncertainty for all order
DeltaVrms2D = spirouRV.delta_v_rms_2d


# =============================================================================
# End of code
# =============================================================================
