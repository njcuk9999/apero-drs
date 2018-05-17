#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou THORCA module

Created on 2017-10-30 at 17:09

@author: cook

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
__all__ = ['DetectBadLines', 'FirstGuessSolution',
           'GetE2DSll', 'Getll', 'Getdll', 'GetLampParams']

# =============================================================================
# Function aliases
# =============================================================================

DetectBadLines = spirouTHORCA.detect_bad_lines

FirstGuessSolution = spirouTHORCA.first_guess_at_wave_solution

GetE2DSll = spirouTHORCA.get_e2ds_ll

Getll = spirouTHORCA.get_ll_from_coefficients

Getdll = spirouTHORCA.get_dll_from_coefficients

GetLampParams = spirouTHORCA.get_lamp_parameters


# =============================================================================
# End of code
# =============================================================================
