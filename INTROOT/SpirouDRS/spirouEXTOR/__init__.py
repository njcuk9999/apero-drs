#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou Extraction module

Created on 2017-11-07 13:45

@author: cook

"""
from SpirouDRS.spirouConfig import Constants
from . import spirouEXTOR

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouEXTOR.__init__()'
# Get version and author
__version__ = Constants.VERSION()
__author__ = Constants.AUTHORS()
__date__ = Constants.LATEST_EDIT()
__release__ = Constants.RELEASE()
# define imports using asterisk
__all__ = ['EarthVelocityCorrection', 'Extraction', 'ExtractABOrderOffset',
           'GetEarthVelocityCorrection', 'GetExtMethod', 'GetValidOrders']

# =============================================================================
# Function aliases
# =============================================================================
EarthVelocityCorrection = spirouEXTOR.earth_velocity_correction

Extraction = spirouEXTOR.extraction_wrapper

# Extraction = spirouEXTOR.extract_wrapper

ExtractABOrderOffset = spirouEXTOR.extract_AB_order

# ExtractOrder = spirouEXTOR.extract_order
#
# ExtractTiltOrder = spirouEXTOR.extract_tilt_order
#
# ExtractTiltWeightOrder = spirouEXTOR.extract_tilt_weight_order
#
# ExtractTiltWeightOrder2 = spirouEXTOR.extract_tilt_weight_order2
#
# ExtractWeightOrder = spirouEXTOR.extract_weight_order

GetEarthVelocityCorrection = spirouEXTOR.get_earth_velocity_correction

GetExtMethod = spirouEXTOR.get_extraction_method

GetValidOrders = spirouEXTOR.get_valid_orders