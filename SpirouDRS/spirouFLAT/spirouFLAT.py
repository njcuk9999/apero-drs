#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-14 at 15:37

@author: cook



Version 0.0.0
"""
from __future__ import division
import numpy as np

from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouFLAT.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__all__ = ['measure_blaze_for_order']
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def measure_blaze_for_order(y, fitdegree):
    """
    Measure the blaze function (for good pixels this is a polynomial fit of
    order = fitdegree, for bad pixels = 1.0).

    bad pixels are defined as less than or equal to zero

    :param y: numpy array (1D), the extracted pixels for this order
    :param fitdegree: int, the polynomial degree

    :return blaze: numpy array (1D), size = len(y), the blaze function: for
                   good pixels this is the value of the fit, for bad pixels the
                   value = 1.0
    """

    # set up x range
    x = np.arange(len(y))
    # remove bad pixels
    mask = y > 0
    yc = y[mask]
    xc = x[mask]
    # do poly fit
    coeffs = np.polyfit(xc, yc, deg=fitdegree)
    # get the fit values for these coefficients
    fity = np.polyval(coeffs, x)
    # calculate the blaze as the fit values for all good pixels and 1 elsewise
    blaze = np.where(mask, fity, 1.0)
    # return blaze
    return blaze

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
