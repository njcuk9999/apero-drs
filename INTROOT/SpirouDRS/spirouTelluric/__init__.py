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
# define all
__all__ = ['CheckBlackList', 'ConstructConvKernel1', 'ConstructConvKernel2',
           'GetMolecularTellLines', 'GetNormalizedBlaze', 'GetBERV',
           'CalculateAbsorptionPCA', 'CalcReconAbso', 'CalcMolecularAbsorption',
           'LinMini', 'Wave2Wave']


# =============================================================================
# Define functions
# =============================================================================

ApplyTemplate = spirouTelluric.apply_template

CalcTelluAbsorption = spirouTelluric.calculate_telluric_absorption

CheckBlackList = spirouTelluric.check_blacklist

ConstructConvKernel1 = spirouTelluric.construct_convolution_kernal1

ConstructConvKernel2 = spirouTelluric.construct_convolution_kernal2

GetMolecularTellLines = spirouTelluric.get_molecular_tell_lines

GetNormalizedBlaze = spirouTelluric.get_normalized_blaze

GetBERV = spirouTelluric.get_berv_value

CalculateAbsorptionPCA = spirouTelluric.calculate_absorption_pca

CalcReconAbso = spirouTelluric.calc_recon_abso

CalcMolecularAbsorption = spirouTelluric.calc_molecular_absorption

BervCorrectTemplate = spirouTelluric.berv_correct_template

LinMini = spirouTelluric.lin_mini

Wave2Wave = spirouTelluric.wave2wave

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
