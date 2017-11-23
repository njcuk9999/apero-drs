#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-21 at 11:52

@author: cook

Version 0.0.1
"""
from __future__ import division
import numpy as np
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


# =============================================================================
# Define functions
# =============================================================================
def delta_v_rms_2d(spe, wave, sigdet, threshold, size):
    # flag (saturated) fluxes above threshold as "bad pixels"
    flag = spe < threshold
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]

    # get the wavelength normalised to the wavelength spacing
    nwave = wave[:, 1:-1] / (wave[:, 2:] - wave[:, :-2])
    # get the flux + noise array
    sxn = (spe[:, 1:-1] + sigdet ** 2)
    # get the flux difference normalised to the flux + noise
    nspe = (spe[:, 2:] - spe[:, :-2]) / sxn
    # get the mask value
    maskv = flag[:, 2:] * flag[:, 1:-1] * flag[:, :-2]
    # get the total
    tot = np.sum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    dvrms2 = (cc.c.value ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(np.sum(1.0 / dvrms2))
    # return dv rms and weighted mean
    return dvrms2, weightedmean


def renormalise_cosmic2d(speref, spe, threshold, size, cut):
    # flag (saturated) fluxes above threshold as "bad pixels"
    flag = (spe < threshold) & (speref < threshold)
    # get the dimensions of spe
    dim1, dim2 = spe.shape
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]
    # set bad pixels to zero (multiply by mask)
    spereff = speref * flag
    spef = spe * flag
    # create a normalised spectrum
    normspe = np.sum(spef, axis=1) / np.sum(spereff, axis=1)
    # get normed spectrum for each pixel for each order
    rnormspe = np.repeat(normspe, dim2).reshape((dim1, dim2))
    # get the sum of values for the combined speref and spe for each order
    stotal = np.sum(spereff + spef, axis=1) / dim2
    stotal = np.repeat(stotal, dim2).reshape((dim1, dim2))
    # get difference over the normalised spectrum
    ztop = spereff - spef / rnormspe
    zbottom = (spef / rnormspe) + spereff + stotal
    z = ztop / zbottom
    # get good values
    goodvalues = abs(z) > 0
    # set the bad values to NaN
    znan = np.copy(z)
    znan[~goodvalues] = np.nan
    # get the rms for each order
    rms = np.nanstd(znan, axis=1)
    # repeat the rms dim2 times
    rrms = np.repeat(rms, dim2).reshape((dim1, dim2))
    # for any values > cut*mean replace spef values with speref values
    spefc = np.where(abs(z) > cut * rrms, spereff * rnormspe, spef)
    # get the total z above cut*mean
    cpt = np.sum(abs(z) > cut * rrms)
    # create a normalise spectrum for the corrected spef
    cnormspe = np.sum(spefc, axis=1) / np.sum(spereff, axis=1)
    # get the normed spectrum for each pixel for each order
    rcnormspe = np.repeat(cnormspe, dim2).reshape((dim1, dim2))
    # get the normalised spectrum using the corrected normalised spectrum
    spen = spefc / rcnormspe
    # return parameters
    return spen, cnormspe, cpt


def calculate_rv_drifts_2d(speref, spe, wave, sigdet, threshold, size):
    # flag bad pixels (less than threshold + difference less than threshold/10)
    flag = (speref < threshold) & (spe < threshold)
    flag &= (speref - spe < threshold / 10.)
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]
    # get the wavelength normalised to the wavelength spacing
    nwave = wave[:, 1:-1] / (wave[:, 2:] - wave[:, :-2])
    # get the flux + noise array
    sxn = (speref[:, 1:-1] + sigdet ** 2)
    # get the flux difference normalised to the flux + noise
    nspe = (speref[:, 2:] - speref[:, :-2]) / sxn
    # get the mask value
    maskv = flag[:, 2:] * flag[:, 1:-1] * flag[:, :-2]
    # calculate the two sums
    sum1 = np.sum((nwave * nspe) * (spe[:, 1:-1] - speref[:, 1:-1]) * maskv, 1)
    sum2 = np.sum(sxn * ((nwave * nspe) ** 2) * maskv, 1)
    # calculate RV drift
    rvdrift = (cc.c.value) * (sum1 / sum2)
    # return RV drift
    return rvdrift


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
