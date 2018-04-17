#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou flat fielding module

Created on 2017-11-14 at 15:37

@author: cook

"""
from __future__ import division
import numpy as np

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouFLAT.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# -----------------------------------------------------------------------------
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get Config error
ConfigError = spirouConfig.ConfigError
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()


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


def correct_flat(p=None, loc=None, hdr=None, filename=None):
    """
    Attempts to read the flat
    :param p:
    :param loc:
    :param hdr:
    :param filename:

    :return loc:
    """
    func_name = __NAME__ + '.correct_flat()'

    # deal with no p and no filename
    if p is None and filename is None:
        emsg1 = ('Error either "p" (ParamDict) or "filename" (string) must '
                 'be defined')
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])

    # get flat from file
    try:
        # read the flat
        flat = spirouImage.ReadFlatFile(p, hdr, required=False)
        # where the flat is zeros set it to ones
        flat = np.where(flat == 0.0, np.ones_like(loc['data']), flat)
    # if there is no flat defined in calibDB use a ones array
    except ConfigError as e:
        # log warning
        wmsg = [e.message, '    Using constant flat instead.']
        WLOG('warning', p['log_opt'], wmsg)
        # flat set to ones
        flat = np.ones_like(loc['data'])

    # add flat to loc
    loc['flat'] = flat
    loc.set_source('flat', func_name)

    # correct the data with the flat
    # TODO: Should this be used?
    #loc['data'] = loc['data']/flat

    # return loc
    return loc




# =============================================================================
# End of code
# =============================================================================
