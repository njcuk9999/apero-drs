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
__all__ = ['DeBananafication', 'Extraction', 'ExtractABOrderOffset',
           'GetExtMethod', 'GetValidOrders']

# =============================================================================
# Function aliases
# =============================================================================
CleanHotpix = spirouEXTOR.clean_hotpix

CompareExtMethod = spirouEXTOR.compare_extraction_modes

DeBananafication = spirouEXTOR.debananafication

Extraction = spirouEXTOR.extraction_wrapper

ExtractABOrderOffset = spirouEXTOR.extract_AB_order

GetExtMethod = spirouEXTOR.get_extraction_method

GetValidOrders = spirouEXTOR.get_valid_orders
