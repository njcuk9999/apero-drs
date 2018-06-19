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
def measure_blaze_for_order(p, y):
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

    # get parameters from p
    fitdegree = p['IC_BLAZE_FITN']

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


def get_flat(p=None, loc=None, hdr=None, filename=None):
    """
    Attempts to read the flat and if it fails uses a constant flat

    :param p or None: parameter dictionary, ParamDict containing constants
        If defined must contain at least:
            fitsfilename: string, the full path of for the main raw fits
                          file for a recipe
                          i.e. /data/raw/20170710/filename.fits
            fiber: string, the fiber used for this recipe (eg. AB or A or C)
            log_opt: string, log option, normally the program name
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            data: numpy array (2D), the image (used for shape)
    :param hdr or None: dictionary or None, if defined is the header file used
                        to choose the date used in teh calibDB (else uses
                        FITSFILENAME to get date for calibDB)
    :param filename or None: string, the flat file name to read, if None
                             uses FLAT_{FIBER} and gets the flat filename from
                             calibDB

    :return lloc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                FLAT: numpy array (2D), the flat image should be the same
                      shape as data
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
        flat = np.where(flat == 0.0, np.ones_like(loc['HCDATA']), flat)
    # if there is no flat defined in calibDB use a ones array
    except ConfigError as e:
        # log warning
        wmsg = [e.message, '    Using constant flat instead.']
        WLOG('warning', p['LOG_OPT'], wmsg)
        # flat set to ones
        flat = np.ones_like(loc['HCDATA'])

    # add flat to loc
    loc['FLAT'] = flat
    loc.set_source('FLAT', func_name)

    # return loc
    return loc


def get_valid_orders(p, loc):
    """
    Get valid order range (from min to max) from constants

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            FF_START_ORDER: int or None, the order number to start with, if
                             None this is set to zero
            FF_END_ORDER: int or None, the order number to end with, if None
                           this is set to the last order number
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            number_orders: int, the number of orders in reference spectrum
    :return valid_ordesr: list, all integer values between the start order and
                          end order
    """
    func_name = __NAME__ + '.get_valid_orders()'
    # get from p or set or get from loc
    if str(p['FF_START_ORDER']) == 'None':
        order_range_lower = 0
    else:
        order_range_lower = p['FF_START_ORDER']
    if str(p['FF_END_ORDER']) == 'None':
        order_range_upper = loc['NUMBER_ORDERS']
    else:
        order_range_upper = p['FF_END_ORDER']

    # check that order_range_lower is valid
    try:
        orl = int(order_range_lower)
        if orl < 0:
            raise ValueError
    except ValueError:
        emsg1 = 'FF_START_ORDER = {0}'.format(order_range_lower)
        emsg2 = '    must be "None" or a valid positive integer'
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
        orl = 0
    # check that order_range_upper is valid
    try:
        oru = int(order_range_upper)
        if oru < 0:
            raise ValueError
    except ValueError:
        emsg1 = 'FF_END_ORDER = {0}'.format(order_range_upper)
        emsg2 = '    must be "None" or a valid positive integer'
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
        oru = 0
    # return the range of the orders
    return range(orl, oru)


# =============================================================================
# End of code
# =============================================================================
