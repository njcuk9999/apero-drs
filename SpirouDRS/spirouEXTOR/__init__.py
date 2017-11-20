#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-07 13:45

@author: cook



Version 0.0.0
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
__all__ = ['Extraction', 'ExtractABOrderOffset', 'ExtractOrder',
           'ExtractOrder0', 'ExtractTiltOrder', 'ExtractTiltWeightOrder',
            'ExtractTiltWeightOrder2', 'ExtractWeightOrder']

# =============================================================================
# Function aliases
# =============================================================================
Extraction = spirouEXTOR.extract_wrapper
"""

:param p: dictionary, parameter dictionary, containing constants and
          variables (at least 'ic_extopt', 'ic_extnbsig' and 'gain')

          where 'ic_extopt' gives the extraction option
                'ic_extnbsig' gives the distance away from center to
                   extract out to +/-
                'gain' is the image gain (used to convert from ADU/s to e-)

:param image: numpy array (2D), the image
:param pos: numpy array (1D), the position fit coefficients
            size = number of coefficients for fit
:param sig: numpy array (1D), the width fit coefficients
            size = number of coefficients for fit
:param tilt: bool, whether to extract using a tilt (not used yet)
:param weighted: bool, whether to extract using weights (not used yet)

:return spe: numpy array (1D), the extracted pixel values,
             size = image.shape[1] (along the order direction)
:return nbcos: int, zero in this case
"""


ExtractABOrderOffset = spirouEXTOR.extract_AB_order
"""
Perform the extraction on the AB fibers separately using the summation
over constant range

:param pp: dictionary, parameter dictionary
:param lloc: dictionary, parameter dictionary containing the data
:param order_num: int, the order number for this iteration
:return lloc: dictionary, parameter dictionary containing the data
"""

ExtractOrder = spirouEXTOR.extract_order

ExtractTiltOrder = spirouEXTOR.extract_tilt_order

ExtractTiltWeightOrder = spirouEXTOR.extract_tilt_weight_order

ExtractTiltWeightOrder2 = spirouEXTOR.extract_tilt_weight_order2

ExtractWeightOrder = spirouEXTOR.extract_weight_order