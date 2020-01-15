#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou localization module

Created on 2017-10-30 at 17:09

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouLOCOR

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouLOCOR.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['BoxSmoothedImage', 'CalcLocoFits', 'FindPosCentCol',
           'FindOrderCtrs', 'GetCoeffs',
           'ImageLocSuperimp', 'InitialOrderFit',
           'LocCentralOrderPos', 'MergeCoefficients',
           'SigClipOrderFit']

# =============================================================================
# Function aliases
# =============================================================================
BoxSmoothedImage = spirouLOCOR.smoothed_boxmean_image

CalcLocoFits = spirouLOCOR.calculate_location_fits

FindPosCentCol = spirouLOCOR.find_position_of_cent_col

FindOrderCtrs = spirouLOCOR.find_order_centers

GetCoeffs = spirouLOCOR.get_loc_coefficients

GetFiberData = spirouLOCOR.get_fiber_data

ImageLocSuperimp = spirouLOCOR.image_localization_superposition

InitialOrderFit = spirouLOCOR.initial_order_fit

LocCentralOrderPos = spirouLOCOR.locate_order_center

MergeCoefficients = spirouLOCOR.merge_coefficients

SigClipOrderFit = spirouLOCOR.sigmaclip_order_fit

# =============================================================================
# End of code
# =============================================================================
