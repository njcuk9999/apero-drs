#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Library for polarimetry calculation

Created on 2018-06-12 at 9:29

@author: E. Martioli

"""

from SpirouDRS import spirouConfig
from . import spirouPOLAR
from . import spirouLSD

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouPOLAR.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['LoadPolarData', 'SortPolarFiles', 'CalculatePolarimetry',
           'CalculateContinuum', 'CalculateStokesI', 'LSDAnalysis',
           'OutputLSDimage', 'PolarHeader']

# =============================================================================
# Function aliases
# =============================================================================
SortPolarFiles = spirouPOLAR.sort_polar_files

LoadPolarData = spirouPOLAR.load_data

CalculatePolarimetry = spirouPOLAR.calculate_polarimetry_wrapper

CalculateContinuum = spirouPOLAR.calculate_continuum

CalculateStokesI = spirouPOLAR.calculate_stokes_i

LSDAnalysis = spirouLSD.lsd_analysis_wrapper

OutputLSDimage = spirouLSD.output_lsd_image

PolarHeader = spirouPOLAR.polar_products_header

# =============================================================================
# End of code
# =============================================================================
