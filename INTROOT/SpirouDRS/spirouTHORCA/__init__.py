#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialization code for Spirou THORCA module

Created on 2017-10-30 at 17:09

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouTHORCA

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouTHORCA.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['GetE2DSll', 'Getll', 'Getdll']

# =============================================================================
# Function aliases
# =============================================================================
GetE2DSll = spirouTHORCA.get_e2ds_ll
"""
Get the line list for the e2ds file from "filename" or from calibration
database using hdr (aqctime) and key. Line list is constructed from 
fit coefficents stored in keywords:
    'kw_TH_ORD_N', 'kw_TH_LL_D', 'kw_TH_NAXIS1'

:param p: parameter dictionary, ParamDict containing constnats
:param hdr: dictionary or None, the HEADER dictionary with the aqcuisition
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

Getll = spirouTHORCA.get_ll_from_coefficients
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

Getdll = spirouTHORCA.get_dll_from_coefficients
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