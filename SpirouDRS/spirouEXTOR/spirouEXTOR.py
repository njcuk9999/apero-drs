#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-07 at 13:46

@author: cook



Version 0.0.0
"""

import numpy as np
from numexpr import evaluate as ne
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings

from SpirouDRS.spirouCore import spirouMath as sm

# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def extract_wrapper(p, image, pos, sig, tilt=False, weighted=False):
    # get parameters from parameter dictionary
    extopt = p['IC_EXTOPT']
    nbsig = p['IC_EXTNBSIG']
    ccdgain = p['gain']

    # Option 0: Extraction by summation over constant range
    if extopt == 0 and not tilt and not weighted:
        return extract_const_range(image, pos, sig, nbsig, ccdgain)


def extract_const_range(image, pos, sig, nbsig, ccdgain):
    nbcos = 0
    # create storage for extration
    spe = np.zeros(image.shape[0], dtype=float)
    # create array of pixel values
    ics = np.arange(image.shape[0])
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - nbsig
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + nbsig
    # get the integer pixel position of the lower bounds
    ind1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    ind2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (ind1s > 0) & (ind2s < image.shape[1])
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = ind1s + 0.5 - lim1s, lim2s - ind2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # add the main order pixels


            spe[ic] = np.sum(image[ic, ind1s[ic] + 1: ind2s[ic]])
            # add the bits missing due to rounding
            spe[ic] += lower[ic] * image[ic, ind1s[ic]]
            spe[ic] += upper[ic] * image[ic, ind2s[ic]]
    # convert to e-
    spe *= ccdgain

    return spe[::-1], nbcos


def extract_const_range1(image, pos, sig, nbsig, ccdgain):
    """
    python = 11.5 ms  fortran = 13 ms

    But different results

    :param image:
    :param pos:
    :param sig:
    :param nbsig:
    :param ccdgain:
    :return:
    """
    nbcos = 0
    # create storage for extration
    spe = np.zeros(image.shape[0], dtype=float)
    # create array of pixel values
    ics = np.arange(image.shape[0])
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - nbsig
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + nbsig
    # get the integer pixel position of the lower bounds
    ind1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    ind2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (ind1s > 0) & (ind2s < image.shape[1])
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = ind1s + 0.5 - lim1s, lim2s - ind2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # add the main order pixels
            spe[ic] = np.sum(image[ic, ind1s[ic] + 1: ind2s[ic]])
            # add the bits missing due to rounding
            spe[ic] += lower[ic] * image[ic, ind1s[ic]]
            spe[ic] += upper[ic] * image[ic, ind2s[ic]]
    # convert to e-
    spe *= ccdgain

    return spe[::-1], nbcos


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
