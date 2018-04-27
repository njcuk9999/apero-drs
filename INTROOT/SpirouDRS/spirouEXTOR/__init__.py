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
__all__ = ['Extraction', 'ExtractABOrderOffset', 'ExtractOrder',
           'ExtractTiltOrder', 'ExtractTiltWeightOrder',
           'ExtractTiltWeightOrder2', 'ExtractWeightOrder',
           'GetValidOrders']

# =============================================================================
# Function aliases
# =============================================================================
Extraction = spirouEXTOR.extract_wrapper

ExtractABOrderOffset = spirouEXTOR.extract_AB_order

ExtractOrder = spirouEXTOR.extract_order

ExtractTiltOrder = spirouEXTOR.extract_tilt_order

ExtractTiltWeightOrder = spirouEXTOR.extract_tilt_weight_order

ExtractTiltWeightOrder2 = spirouEXTOR.extract_tilt_weight_order2

ExtractWeightOrder = spirouEXTOR.extract_weight_order

GetValidOrders = spirouEXTOR.get_valid_orders