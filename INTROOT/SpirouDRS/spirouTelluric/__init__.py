#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-12 08:18
@author: ncook
Version 0.0.1
"""
from SpirouDRS import spirouConfig
from . import spirouTelluric

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouUnitTests.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()


# =============================================================================
# Define functions
# =============================================================================

ConstructConvolutionKernel1 = spirouTelluric.construct_convolution_kernal1

ConstructConvolutionKernel2 = spirouTelluric.construct_convolution_kernal2

GetMolecularTellLines = spirouTelluric.get_molecular_tell_lines

GetNormalizedBlaze = spirouTelluric.get_normalized_blaze

GetBERV = spirouTelluric.get_berv_value

CalculateAbsorptionPCA = spirouTelluric.calculate_absorption_pca


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================