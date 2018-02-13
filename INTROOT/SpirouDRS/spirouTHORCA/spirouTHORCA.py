#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou THORCA module

Created on 2017-12-19 at 16:20

@author: cook

"""
from __future__ import division
import numpy as np
from astropy import constants
from scipy.stats.stats import pearsonr
from scipy.optimize import curve_fit
import warnings
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouTHORCA.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
ConfigError = spirouConfig.ConfigError
# Get Logging function
WLOG = spirouCore.wlog


# =============================================================================
# Define functions
# =============================================================================
def get_e2ds_ll(p, hdr=None, filename=None, key=None):
    """
    Get the line list for the e2ds file from "filename" or from calibration
    database using hdr (aqctime) and key. Line list is constructed from
    fit coefficents stored in keywords:
        'kw_TH_ORD_N', 'kw_TH_LL_D', 'kw_TH_NAXIS1'

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                kw_TH_COEFF_PREFIX: list, the keyword store for the prefix to
                                    use to get the TH line list fit coefficients

    :param hdr: dictionary or None, the HEADER dictionary with the acquisition
                time in to use in the calibration database to get the filename
                with key=key (or if None key='WAVE_AB')
    :param filename: string or None, the file to get the line list from
                     (overrides getting the filename from calibration database)
    :param key: string or None, if defined the key in the calibration database
                to get the file from (using the HEADER dictionary to deal with
                calibration database time constraints for duplicated keys.

    :return ll: numpy array (1D), the line list values
    :return param_ll: numpy array (1d), the line list fit coefficients (used to
                      generate line list - read from file defined)
    """

    if key is None:
        # Question: Why WAVE_AB and not WAVE_{fiber} ??
        key = 'WAVE_AB'
    # get filename
    if filename is None:
        read_file = spirouCDB.GetFile(p, key, hdr)
    else:
        read_file = filename

    # read read_file
    rout = spirouImage.ReadImage(p, filename=read_file, log=False)
    wave, whdr, _, nx, ny = rout

    # extract required keyword arguments from the header
    keys = ['kw_TH_ORD_N', 'kw_TH_LL_D', 'kw_TH_NAXIS1']
    try:
        nbo, degll, xsize = spirouConfig.GetKwValues(p, whdr, keys, read_file)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, p['log_opt'], e.msg)
        nbo, degll, xsize = 0, 0, 0

    # get the coefficients from the header
    coeff_prefix = p['kw_TH_COEFF_PREFIX'][0]
    param_ll = []
    # loop around the orders
    for order_num in range(nbo):
        # loop around the fit degrees
        for deg_num in range(degll + 1):
            # get the row number
            num = (order_num * (degll + 1)) + deg_num
            # get the header key
            header_key = '{0}{1}'.format(coeff_prefix, num)
            # get the header value
            param_ll.append(whdr[header_key])

    # reshape param_ll to be size = (number of orders x degll+1
    param_ll = np.array(param_ll).reshape((nbo, degll +1))

    # get the line list
    ll = get_ll_from_coefficients(param_ll, xsize, nbo)

    # return ll and param_ll
    return ll, param_ll


def get_ll_from_coefficients(params, nx, nbo):
    """
    Use the coefficient matrix "params" to construct fit values for each order
    (dimension 0 of coefficient matrix) for values of x from 0 to nx
    (interger steps)

    :param params: numpy array (2D), the coefficient matrix
                   size = (number of orders x number of fit coefficients)

    :param nx: int, the number of values and the maximum value of x to use
               the coefficients for, where x is such that

                yfit = p[0]*x**(N-1) + p[1]*x**(N-2) + ... + p[N-2]*x + p[N-1]

                N = number of fit coefficients
                and p is the coefficients for one order
                (i.e. params = [ p_1, p_2, p_3, p_4, p_5, ... p_nbo]

    :param nbo: int, the number of orders to use

    :return ll: numpy array (2D): the yfit values for each order
                (i.e. ll = [yfit_1, yfit_2, yfit_3, ..., yfit_nbo] )
    """
    # create x values
    xfit = np.arange(nx)
    # create empty line list storage
    ll = np.zeros((nbo, nx))
    # loop around orders
    for order_num in range(nbo):
        # get the coefficients for this order and flip them
        # (numpy needs them backwards)
        coeffs = params[order_num][::-1]
        # get the y fit using the coefficients for this order and xfit
        # TODO: Check order of params[i]
        # Question: This could be wrong - if fit parameters are order
        # Question: differently
        yfit = np.polyval(coeffs, xfit)
        # add to line list storage
        ll[order_num, :] = yfit
    # return line list
    return ll


def get_dll_from_coefficients(params, nx, nbo):
    """
    Derivative of the coefficients, using the coefficient matrix "params"
    to construct the derivative of the fit values for each order
    (dimension 0 of coefficient matrix) for values of x from 0 to nx
    (interger steps)

    :param params: numpy array (2D), the coefficient matrix
                   size = (number of orders x number of fit coefficients)

    :param nx: int, the number of values and the maximum value of x to use
               the coefficients for, where x is such that

                yfit = p[0]*x**(N-1) + p[1]*x**(N-2) + ... + p[N-2]*x + p[N-1]

                dyfit = p[0]*(N-1)*x**(N-2) + p[1]*(N-2)*x**(N-3) + ... +
                        p[N-3]*x + p[N-2]

                N = number of fit coefficients
                and p is the coefficients for one order
                (i.e. params = [ p_1, p_2, p_3, p_4, p_5, ... p_nbo]

    :param nbo: int, the number of orders to use

    :return ll: numpy array (2D): the yfit values for each order
                (i.e. ll = [dyfit_1, dyfit_2, dyfit_3, ..., dyfit_nbo] )
    """

    # create x values
    xfit = np.arange(nx)
    # create empty line list storage
    ll = np.zeros((nbo, nx))
    # loop around orders
    for order_num in range(nbo):
        # get the coefficients for this order and flip them
        coeffs = params[order_num]
        # get the y fit using the coefficients for this order and xfit
        # TODO: Check order of params[i]
        # Question: This could be wrong - if fit parameters are order
        # Question: differently
        yfiti = []
        # derivative =  (j)*(a_j)*x^(j-1)   where j = it + 1
        for it in range(len(coeffs)-1):
            yfiti.append((it + 1) * coeffs[it + 1] * xfit**it)
        yfit = np.sum(yfiti, axis=0)
        # add to line list storage
        ll[order_num, :] = yfit
    # return line list
    return ll


# =============================================================================
# End of code
# =============================================================================
