#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:09

@author: cook



Version 0.0.0
"""
from SpirouDRS import spirouConfig
from . import spirouTHORCA

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouTHORCA.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = []

# =============================================================================
# Function aliases
# =============================================================================

# get the e2ds line list
GetE2DSll = spirouTHORCA.get_e2ds_ll

# get the line list from fits
Getll = spirouTHORCA.get_ll_from_coefficients

# get the derivative of the line list from fits
Getdll = spirouTHORCA.get_dll_from_coefficients