#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-21 at 11:52

@author: cook



Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from astropy import constants as cc

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore


# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouRV.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
ConfigError = spirouConfig.ConfigError
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def delta_v_rms_2d(spe, wave, sigdet, threshold, size):
    # flag (saturated) fluxes above threshold as "bad pixels"
    mask = spe < threshold
    # copy mask
    mask1 = np.copy(mask)
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2*size, 1):
        mask1[:, size:-size] *= mask1[:, i_it: i_it-2*size]

    # get the wavelength normalised to the wavelength spacing
    nwave = wave[:, 1:-1] / (wave[:, 2:] - wave[:,:-2])
    # get the flux + noise array
    Sxn = (spe[:, 1:-1] + sigdet**2)
    # get the flux difference normalised to the flux + noise
    nspe = (spe[:, 2:] - spe[:, :-2]) / Sxn
    # get the mask value
    maskv = mask1[:, 2:] * mask1[:, 1:-1] * mask1[:, :-2]
    # get the total
    tot = np.sum(Sxn * ((nwave*nspe)**2) * maskv, axis=1)
    # convert to dvrms2
    dvrms2 = cc.c.value**2/abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1./np.sqrt(np.sum(1.0/dvrms2))
    # return dv rms and weighted mean
    return dvrms2, weightedmean


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
