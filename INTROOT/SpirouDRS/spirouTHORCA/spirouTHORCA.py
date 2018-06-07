#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou THORCA module

Created on 2017-12-19 at 16:20

@author: cook

"""
from __future__ import division
from astropy import constants as cc
from astropy import units as uu
import numpy as np
import warnings

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS.spirouCore import spirouMath

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
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt
# Speed of light
speed_of_light = cc.c.to(uu.km/uu.s).value
speed_of_light = 300000

# =============================================================================
# Define functions
# =============================================================================
def get_e2ds_ll(p, hdr=None, filename=None, key=None):
    """
    Get the line list for the e2ds file from "filename" or from calibration
    database using hdr (aqctime) and key. Line list is constructed from
    fit coefficents stored in keywords:
        'kw_TH_ORD_N', 'kw_TH_LL_D', 'kw_TH_NAXIS1'

    :param p: parameter dictionary, ParamDict containing constants
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
        gkv = spirouConfig.GetKeywordValues(p, whdr, keys, read_file)
        nbo, degll, xsize = gkv
    except spirouConfig.ConfigError as e:
        WLOG(e.level, p['LOG_OPT'], e.msg)
        nbo, degll, xsize = 0, 0, 0

    # get the coefficients from the header
    coeff_prefix = p['KW_TH_COEFF_PREFIX'][0]
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
    param_ll = np.array(param_ll).reshape((nbo, degll + 1))

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


def get_lamp_parameters(p, filename=None, kind=None):
    """
    Get lamp parameters from either a specified lamp type="kind" or a filename
    or from p['ARG_FILE_NAMES'][0] (if no filename or kind defined)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LAMPS: list of strings, the different allowed lamp types
            log_opt: string, log option, normally the program name
    :param filename: string or None, the filename to check for the lamp
                     substring in
    :param kind: string or None, the lamp type

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                LAMP_TYPE: string, the type of lamp (e.g. UNe or TH)
                IC_LL_LINE_FILE: string, the file name of the line list to use
                IC_CAT_TYPE: string, the line list catalogue type
    """

    func_name = __NAME__ + '.get_lamp_parameters()'
    # identify lamp
    if kind is not None:
        lamp = kind
    elif filename is not None:
        lamp = decide_on_lamp_type(p, filename=filename)
    else:
        lamp = decide_on_lamp_type(p, filename=p['ARG_FILE_NAMES'][0])

    # -------------------------------------------------------------------------
    # Now set parameters in p based on lamp type

    # the lamp type
    p['LAMP_TYPE'] = lamp
    p.set_source('LAMP_TYPE', func_name)
    # the lamp file
    p['IC_LL_LINE_FILE'] = p['IC_LL_LINE_FILE_ALL'][lamp]
    p.set_source('IC_LL_LINE_FILE', func_name)
    # the lamp cat type
    p['IC_CAT_TYPE'] = p['IC_CAT_TYPE_ALL'][lamp]
    p.set_source('IC_CAT_TYPE', func_name)
    # -------------------------------------------------------------------------
    # finally return p
    return p


def first_guess_at_wave_solution(p, loc, mode='new'):
    """
    First guess at wave solution, consistency check, using the wavelength
    solutions line list

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            CAL_HC_N_ORD_FINAL: int, defines first order solution is calculated
                                from
            CAL_HC_T_ORDER_START: int, defines the first order solution is
                                  calculated from
            log_opt: string, log option, normally the program name
            fiber: string, the fiber number

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:

    :param mode: string, if mode="new" uses python to work out gaussian fit
                         if mode="old" uses FORTRAN (testing only) requires
                         compiling of FORTRAN fitgaus into spirouTHORCA dir

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ECHELLE_ORDERS: numpy array, the echelle orders to fit
                LL_INIT: numpy array, the initial guess at the line list
                LL_LINE: numpy array, the line list wavelengths from file
                AMPL_LINE: numpy array, the line list amplitudes from file
                ALL_LINES: list of numpy arrays, length = number of orders
                            each numpy array contains gaussian parameters
                            for each found line in that order

    """
    func_name = __NAME__ + '.first_guess_at_wave_solution()'
    # get used constants from p
    n_order_final = p['CAL_HC_N_ORD_FINAL']
    # set up the orders to fit
    loc['ECHELLE_ORDERS'] = p['CAL_HC_T_ORDER_START'] - np.arange(n_order_final)
    loc.set_source('ECHELLE_ORDERS', func_name)

    # get wave solution filename
    wave_file = spirouImage.ReadWaveFile(p, loc['HDR'], return_filename=True)
    # log wave file name
    wmsg = 'Reading initial wavelength solution in {0}'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(wave_file))

    # get E2DS line list from wave_file
    ll_init, param_ll_init = get_e2ds_ll(p, loc['HDR'], filename=wave_file)
    # only perform fit on orders 0 to p['CAL_HC_N_ORD_FINAL']
    loc['LL_INIT'] = ll_init[:n_order_final]
    loc.set_source('LL_INIT', __NAME__ + func_name)

    # load line file (from p['IC_LL_LINE_FILE'])
    loc['LL_LINE'], loc['AMPL_LINE'] = spirouImage.ReadLineList(p)
    source = func_name + ' spirouImage.ReadLineList()'
    loc.set_sources(['ll_line', 'ampl_line'], source)

    # log that we are attempting to find ll on spectrum
    wmsg = 'On fiber {0} trying to identify lines using guess solution'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(p['FIBER']))

    # find the lines
    fargs = [p, loc['LL_INIT'], loc['LL_LINE'], loc['AMPL_LINE'],
             loc['DATA'][:p['CAL_HC_N_ORD_FINAL']], loc['ECHELLE_ORDERS']]
    all_lines = find_lines(*fargs, mode=mode)
    # add all lines to loc
    loc['ALL_LINES'] = all_lines
    loc.set_source('ALL_LINES', func_name)
    # return loc
    return loc


def detect_bad_lines(p, loc, key=None):

    # get constants from p
    max_error_onfit = p['IC_MAX_ERRW_ONFIT']
    max_error_sigll = p['IC_MAX_SIGLL_CAL_LINES']
    max_ampl_lines = p['IC_MAX_AMPL_LINE']

    # deal with key
    if key is None:
        key = 'ALL_LINES'
    elif key in loc:
        pass
    else:
        emsg = 'key = "{0}" not defined in "loc"'
        WLOG('error', p['LOG_OPT'], emsg.format(key))
        key = None

    # loop around each order
    for order_num in range(len(loc[key])):
        # get all lines 7
        lines = np.array(loc[key][order_num])
        # ---------------------------------------------------------------------
        # Criteria 1
        # ---------------------------------------------------------------------
        # create mask
        badfit = lines[:, 7] <= max_error_onfit
        # count number of bad lines
        num_badfit = np.sum(badfit)
        # put all bad fit lines to zero
        lines[:, 7][badfit] = 0.0
        # ---------------------------------------------------------------------
        # Criteria 2
        # ---------------------------------------------------------------------
        # calculate the sig-fit for the lines
        sigll = lines[:, 1]/lines[:, 0] * speed_of_light
        # create mask
        badsig = sigll >= max_error_sigll
        # count number of bad sig lines
        num_badsig = np.sum(badsig)
        # put all bad sig lines to zero
        lines[:, 7][badsig] = 0.0
        # ---------------------------------------------------------------------
        # Criteria 3
        # ---------------------------------------------------------------------
        # create mask
        badampl = lines[:, 2] >= max_ampl_lines
        # count number
        num_badampl = np.sum(badampl)
        # put all bad ampl to zero
        lines[:, 7][badsig] = 0.0
        # ---------------------------------------------------------------------
        # log criteria
        # ---------------------------------------------------------------------
        # combine masks
        badlines = badfit | badsig | badampl
        # count number
        num_bad, num_total = np.sum(badlines), badlines.size
        # log only if we have bad
        if np.sum(badlines) > 0:
            wargs = [order_num, num_bad, num_total, num_badsig, num_badampl,
                     num_badfit]
            wmsg = ('In Order {0} reject {1}/{2} ({3}/{4}/{5}) lines '
                    '[beyond (sig/ampl/err) limits]')
            WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(*wargs))
        # ---------------------------------------------------------------------
        # Remove infinities
        # ---------------------------------------------------------------------
        # create mask
        nanmask = ~np.isfinite(lines[:, 7])
        # put all NaN/infs to zero
        lines[:, 7][nanmask] = 0.0
        # ---------------------------------------------------------------------
        # add back to loc[key]
        # ---------------------------------------------------------------------
        loc[key][order_num] = lines

    # return loc
    return loc


def fit_1d_solution(p, loc):

    # get 1d solution
    loc = fit_1d_ll_solution(p, loc)
    # invert solution
    loc = invert_1ds_ll_solution(p, loc)
    # get the total number of orders to fit
    num_orders = len(loc['ALL_LINES'])
    # get the dimensions of the data
    ydim, xdim = loc['DATA'].shape
    # get new line list
    loc['LL_OUT'] = get_ll_from_coefficients(loc['INV_PARAM'], xdim, num_orders)
    # get the first derivative of the line list
    loc['DLL_OUT'] = get_dll_from_coefficients(loc['INV_PARAM'], xdim,
                                               num_orders)
    # find the central pixel value
    centpix = loc['LL_OUT'].shape[1]//2
    # get the mean pixel scale (in km/s/pixel) of the central pixel
    norm = loc['DLL_OUT'][:, centpix]/loc['LL_OUT'][:, centpix]
    meanpixscale = speed_of_light * np.sum(norm)/len(loc['LL_OUT'][:, centpix])
    # log message
    wmsg = 'On fiber {0} mean pixel scale at center: {1:.4f} [km/s/pixel]'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['FIBER'], meanpixscale))
    # return loc
    return loc


def calculate_littrow_sol(p, loc):

    func_name = __NAME__ + '.calculate_littrow_sol()'
    # get parameters from p
    remove_orders = p['IC_LITTROW_REMOVE_ORDERS']
    n_order_init = p['IC_LITTROW_ORDER_INIT']
    n_order_final = p['CAL_HC_N_ORD_FINAL']
    x_cut_step = p['IC_LITTROW_CUT_STEP']
    fit_degree = p['IC_LITTROW_FIT_DEG']
    # get parameters from loc
    torder = loc['ECHELLE_ORDERS']
    ll_out = loc['LL_OUT']
    # test if n_order_init is in remove_orders
    if n_order_init in remove_orders:
        wargs = ["IC_LITTROW_ORDER_INIT", p['IC_LITTROW_ORDER_INIT'],
                 "IC_LITTROW_REMOVE_ORDERS"]
        wmsg1 = 'Warning {0]={1} in {2}'.format(*wargs)
        # TODO: Remove H2RG dependency
        wmsg2 = ('    Please check constants_SPIROU_{0}.py file'
                 ''.format(p['IC_IMAGE_TYPE']))
        wmsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [wmsg1, wmsg2, wmsg3])
    # test if n_order_init is in remove_orders
    if n_order_final in remove_orders:
        wargs = ["CAL_HC_N_ORD_FINAL", p['CAL_HC_N_ORD_FINAL'],
                 "IC_LITTROW_REMOVE_ORDERS"]
        wmsg1 = 'Warning {0]={1} in {2}'.format(*wargs)
        # TODO: Remove H2RG dependency
        wmsg2 = ('    Please check constants_SPIROU_{0}.py file'
                 ''.format(p['IC_IMAGE_TYPE']))
        wmsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [wmsg1, wmsg2, wmsg3])
    # check that all remove orders exist
    for remove_order in remove_orders:
        if remove_order not in np.arange(n_order_final):
            wargs1 = [remove_order, 'IC_LITTROW_REMOVE_ORDERS', 0,
                       n_order_final]
            wmsg1 = (' Invalid order number={0} in {1} must be between'
                     '{2} and {3}'.format(*wargs1))
            wmsg2 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [wmsg1, wmsg2])

    # check to make sure we have some orders left
    if len(np.unique(remove_orders)) == n_order_final:
        wmsg = 'Cannot remove all orders. Check IC_LITTROW_REMOVE_ORDERS'
        WLOG('error', p['LOG_OPT'], wmsg)
    # get the total number of orders to fit
    num_orders = len(loc['ALL_LINES'])
    # get the dimensions of the data
    ydim, xdim = loc['DATA'].shape
    # deal with removing orders (via weighting stats)
    rmask = np.ones(num_orders, dtype=bool)
    if len(remove_orders) > 0:
        rmask[np.array(remove_orders)] = False
    # storage of results
    keys = ['LITTROW_MEAN_EXT', 'LITTROW_SIG_EXT', 'LITTROW_MINDEV_EXT',
            'LITTROW_MAXDEV_EXT', 'LITTROW_PARAM_EXT']
    for key in keys:
        loc[key] = []
        loc.set_source(key, func_name)
    # construct the Littrow cut points
    x_cut_points = np.arange(x_cut_step, xdim-x_cut_step, x_cut_step)
    # save to storage
    loc['X_CUT_POINTS'] = x_cut_points
    # get the echelle order values
    orderpos = torder[:n_order_final][rmask]
    # get the inverse order number
    inv_orderpos = 1.0 / orderpos
    # loop around cut points and get littrow parameters and stats
    for it in range(len(x_cut_points)):
        # this iterations x cut point
        x_cut_point = x_cut_points[it]
        # get the fractional wavelength contrib. at each x cut point
        ll_point = ll_out[:n_order_final, x_cut_point][rmask]
        ll_start_point = ll_out[n_order_init, x_cut_point]
        frac_ll_point = ll_point/ll_start_point
        # fit the inverse order numbers against the fractional
        #    wavelength contrib.
        coeffs = np.polyfit(inv_orderpos, frac_ll_point, fit_degree)[::-1]
        # calculate the fit values
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate the residuals
        res = cfit - frac_ll_point
        # find the largest residual
        largest = np.max(abs(res))
        sigmaclip = abs(res) != largest
        # remove the largest residual
        inv_orderpos_s = inv_orderpos[sigmaclip]
        frac_ll_point_s = frac_ll_point[sigmaclip]
        # refit the inverse order numbers against the fractional
        #    wavelength contrib. after sigma clip
        coeffs = np.polyfit(inv_orderpos_s, frac_ll_point_s, fit_degree)[::-1]
        # calculate the fit values (for all values - including sigma clipped)
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate residuals (in km/s) between fit and original values
        respix = speed_of_light * (cfit - frac_ll_point)/frac_ll_point
        # calculate stats
        mean = np.sum(respix) / len(respix)
        mean2 = np.sum(respix ** 2) / len(respix)
        rms = np.sqrt(mean2 - mean ** 2)
        mindev = np.min(respix)
        maxdev = np.max(respix)
        # add to storage
        loc['LITTROW_MEAN_EXT'].append(mean)
        loc['LITTROW_SIG_EXT'].append(rms)
        loc['LITTROW_MINDEV_EXT'].append(mindev)
        loc['LITTROW_MAXDEV_EXT'].append(maxdev)
        loc['LITTROW_PARAM_EXT'].append(coeffs)

    # return loc
    return loc


def extrapolate_littrow_sol(p, loc):

    func_name = __NAME__ + '.extrapolate_littrow_sol()'
    # get parameters from p
    fit_degree = p['IC_LITTROW_ORDER_FIT_DEG']
    t_order_start = p['CAL_HC_T_ORDER_START']
    n_order_init = p['IC_LITTROW_ORDER_INIT']

    # get parameters from loc
    litt_param = loc['LITTROW_PARAM_EXT']

    # get the dimensions of the data
    ydim, xdim = loc['DATA'].shape
    # get the pixel positions
    x_points = np.arange(xdim)
    # construct the Littrow cut points (in pixels)
    x_cut_points = loc['X_CUT_POINTS']
    # construct the Littrow cut points (in wavelength)
    ll_cut_points = loc['LL_OUT'][n_order_init][x_cut_points]

    # set up storage
    loc['LITTROW_EXTRAP'] = np.zeros((ydim, len(x_cut_points)), dtype=float)
    loc['LITTROW_EXTRAP_SOL'] = np.zeros_like(loc['DATA'])
    loc['LITTROW_EXTRAP_PARAM'] = np.zeros((ydim, fit_degree + 1),dtype=float)

    # calculate the echelle order position for this order
    echelle_order_nums = t_order_start - np.arange(ydim)
    # calculate the inverse echelle order nums
    inv_echelle_order_nums = 1.0 / echelle_order_nums

    # loop around the x cut points
    for it in range(len(x_cut_points)):
        # evaluate the fit for this order
        cfit = np.polyval(litt_param[it][::-1], inv_echelle_order_nums)
        # evaluate littrow fit for x_cut_points on each order (in wavelength)
        litt_extrap_o = cfit * ll_cut_points[it]
        # add to storage
        loc['LITTROW_EXTRAP'][:, it] = litt_extrap_o

    for order_num in range(ydim):
        # fit the littrow extrapolation
        param = np.polyfit(x_cut_points, loc['LITTROW_EXTRAP'][order_num],
                           fit_degree)[::-1]
        # add to storage
        loc['LITTROW_EXTRAP_PARAM'][order_num] = param
        # evaluate the polynomial for all pixels in data
        loc['LITTROW_EXTRAP_SOL'][order_num] = np.polyval(param[::-1], x_points)

    return loc


def second_guess_at_wave_solution(p, loc, mode='new'):

    func_name = __NAME__ + '.second_guess_at_wave_solution()'
    # Update the free span wavelength value
    p['IC_LL_FREE_SPAN'] = p['IC_LL_FREE_SPAN_2']
    # New final order value
    n_ord_final = p['CAL_HC_N_ORD_FINAL']
    n_ord_final_2 = p['CAL_HC_N_ORD_FINAL_2']
    # recalculate echelle order number
    echelle_order = p['CAL_HC_T_ORDER_START'] - np.arange(n_ord_final_2)

    # set the starting point as the outputs from the first guess solution
    # loop around original order num
    ll_line_2, ampl_line_2 = [], []
    for order_num in range(n_ord_final):
        # get this orders details
        details = loc['FINAL_DETAILS'][order_num]
        # append to lists
        ll_line_2 = np.append(ll_line_2, details[0])
        ampl_line_2 = np.append(ampl_line_2, details[3])

    # Now add in any lines which are outside the range of the first guess
    #    solution
    lmask = loc['LL_LINE'] > np.max(ll_line_2)
    ll_line_2 = np.append(ll_line_2, loc['LL_LINE'][lmask])
    ampl_line_2 = np.append(ampl_line_2, loc['AMPL_LINE'][lmask])

    # log second pass
    wmsg = ('On fiber {0} trying to identify lines using guess solution '
            '(second pass)'.format(p['FIBER']))
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg)

    # find the lines
    ll = loc['LITTROW_EXTRAP_SOL'][:n_ord_final_2]
    datax = loc['DATA'][:n_ord_final_2]

    fargs = [p, ll, ll_line_2, ampl_line_2, datax, echelle_order]
    all_lines = find_lines(*fargs, mode=mode)

    # add all lines to loc
    loc['ALL_LINES_2'] = all_lines
    loc.set_source('ALL_LINES_2', func_name)
    # return loc
    return loc



# =============================================================================
# Define worker functions
# =============================================================================
def decide_on_lamp_type(p, filename):
    """
    From a filename and p['IC_LAMPS'] decide on a lamp type for the file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LAMPS: list of strings, the different allowed lamp types
            log_opt: string, log option, normally the program name
    :param filename: string, the filename to check for the lamp substring in

    :return lamp_type: string, the lamp type for this file (one of the values
                       in p['IC_LAMPS']
    """
    func_name = __NAME__ + '.decide_on_lamp_type()'
    # storage for lamp type
    lamp_type = None
    # loop around each lamp in defined lamp types
    for lamp in p['IC_LAMPS']:
        # check for lamp in filename
        if p['IC_LAMPS'][lamp] in filename:
            # check if we have already found a lamp type
            if lamp_type is not None:
                emsg1 = ('Multiple lamp types found in file={0}, lamp type is '
                         'ambiguous'.format(filename))
                emsg2 = '    function={0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
            else:
                lamp_type = lamp
    # check that lamp is defined
    if lamp_type is None:
        emsg1 = 'Lamp type for file={0} cannot be identified.'.format(filename)
        emsg2 = ('    Must be one of the following: {0}'
                 ''.format(', '.join(p['IC_LAMPS'])))
        emsg3 = '    function={0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
    # finally return lamp type
    return lamp_type


def find_lines(p, ll, ll_line, ampl_line, datax, torder, mode='new'):
    """
    Find the lines on the E2DS spectrum

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LL_SP_MIN
            IC_LL_SP_MAX
            IC_RESOL
            IC_LL_FREE_SPAN
            IC_HC_NOISE

    :param ll:
    :param ll_line:
    :param ampl_line:
    :param datax:
    :param torder:

    :param mode: string, if mode="new" uses python to work out gaussian fit
                         if mode="old" uses FORTRAN (testing only) requires
                         compiling of FORTRAN fitgaus into spirouTHORCA dir

    :return all_lines: list, all lines in format:

                    [order1lines, order2lines, order3lines, ..., orderNlines]

                    where order1lines = [gparams1, gparams2, ..., gparamsN]

                    where:
                        gparams[0] = output wavelengths
                        gparams[1] = output sigma (gauss fit width)
                        gparams[2] = output amplitude (gauss fit)
                        gparams[3] = difference in input/output wavelength
                        gparams[4] = input amplitudes
                        gparams[5] = output pixel positions
                        gparams[6] = output pixel sigma width
                                          (gauss fit width in pixels)
                        gparams[7] = output weights for the pixel position
                    (See fit_emi_line)

    """
    func_name = __NAME__ + '.find_lines()'
    # get parameters from p
    ll_sp_min = p['IC_LL_SP_MIN']
    ll_sp_max = p['IC_LL_SP_MAX']
    resol = p['IC_RESOL']
    ll_free_span = p['IC_LL_FREE_SPAN']
    image_ron = p['IC_HC_NOISE']

    # set update a pixel array
    xpos = np.arange(datax.shape[1])
    # set up storage
    all_cal_line_fit = []
    # loop around the orders
    for order_num in np.arange(datax.shape[0]):
        # order extend (in wavelengths)
        order_min, order_max = ll[order_num, 0], ll[order_num, -1]
        # select lines based on boundaries
        wave_mask = (ll_line >= order_min)
        wave_mask &= (ll_line <= order_max)
        wave_mask &= (ll_line >= ll_sp_min)
        wave_mask &= (ll_line <= ll_sp_max)
        # apply mask to ll_line and ampl_line
        ll_line_s = ll_line[wave_mask]
        ampl_line_s = ampl_line[wave_mask]
        # check to make sure we have lines
        if not len(ll_line_s) > 0:
            # if we have no lines print detailed error report and exit
            emsg1 = 'Order {0}: NO LINES IDENTIFIED!!'.format(order_num)
            emsg2args = [order_min, order_max]
            emsg2 = '   Order limit: [{0:6.1f}-{1:6.1f}]'.format(*emsg2args)
            emsg3args = [ll_sp_min, ll_sp_max]
            emsg3 = '   Hard limit: [{0:6.1f}-{1:6.1f}]'.format(*emsg3args)
            emsg4args = [ll_line[0], ll_line[-1]]
            emsg4 = '   Line interval: [{0:6.1f}-{1:6.1f}]'.format(*emsg4args)
            emsg5 = '       function={0}'.format(func_name)
            emsg6 = ' Unable to reduce, check guess solution'
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3, emsg4,
                                         emsg5, emsg6])
        gauss_fit = []
        # loop around the lines in kept line list
        for ll_i in np.arange(len(ll_line_s)):
            # get this iterations line
            line = float(ll_line_s[ll_i])
            # loop around these two span values
            for span in [4.25, ll_free_span]:
                # calculate line limits
                ll_span_min = line - span * (line/(resol * 2.355))
                ll_span_max = line + span * (line/(resol * 2.355))
                # calculate line mask for each span
                line_mask = ll[order_num] >= ll_span_min
                line_mask &= ll[order_num] <= ll_span_max
                # apply line mask to ll, xpos and data
                sll = ll[order_num, :][line_mask]
                sxpos = xpos[line_mask]
                sdata = datax[order_num, :][line_mask]
                # normalise sdata by the minimum sdata
                sdata = sdata - np.min(sdata)
                # make sure we have more than 3 data points
                if len(sxpos) < 3:
                    wmsg = 'Resolution or ll_span are too small'
                    WLOG('', p['LOG_OPT'], wmsg)
                # work out a pixel weighting
                line_weight = 1.0/(sdata + image_ron**2)
                # check that the sum of the weighted flux is not zero
                if np.sum(sdata * line_weight) != 0:
                    # if it isn't zero set the line value to the
                    #   weighted mean value
                    line = np.sum(sll * sdata * line_weight)
                    line = line / np.sum(sdata * line_weight)
                else:
                    # if it is zero then just use the line
                    line = float(ll_line_s[ll_i])
            # perform the gaussian fit on the line
            with warnings.catch_warnings(record=True) as w:
                # TODO: PROBLEM WITH FIT_EMI_LINE
                # TODO:  1 scipy.optimize.curve_fit does not give
                # TODO:    same result as foutran fitgaus.fitgaus routine
                # TODO:  2 fitgaus.fitgaus routine (in py3) does not give
                # TODO:    same result as AT4-V48 version (py2 old)
                # TODO:  3 scipy.optimize.curve_fit is slower
                gau_param = fit_emi_line(sll, sxpos, sdata, line_weight,
                                         mode=mode)
            # check if gau_param[7] is positive
            if gau_param[7] > 0:
                # Set the difference in input/output wavelength
                gau_param[3] = ll_line_s[ll_i] - gau_param[0]
                # Set the input amplitudes
                gau_param[4] = ampl_line_s[ll_i]
            # finally append parameters to storage
            gauss_fit.append(gau_param)
        # finally reshape all the gauss_fit parameters
        gauss_fit = np.array(gauss_fit).reshape(len(ll_line_s), 8)
        # calculate stats for logging
        min_ll, max_ll = ll_line_s[0], ll_line_s[-1]
        nlines_valid = np.sum(gauss_fit[:, 7] > 0)
        nlines_total = len(gauss_fit[:, 7])
        percentage_vlines = 100 * (nlines_valid/nlines_total)
        # log the stats for this order
        wmsg = 'Order {0:3} ({1:2}): [{2:6.1f} - {3:6.1f}]'
        wmsg += ' ({4:3}/{5:3})={6:3.1f}% lines identified'
        wargs = [torder[order_num], order_num, min_ll, max_ll,
                 nlines_valid, nlines_total, percentage_vlines]
        WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
        all_cal_line_fit.append(gauss_fit)
    # return all lines found (36 x number of lines found for order)
    return all_cal_line_fit



def find_lines2(p, ll, ll_line, ampl_line, datax, torder, mode='new'):
    """
    Find the lines on the E2DS spectrum

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LL_SP_MIN
            IC_LL_SP_MAX
            IC_RESOL
            IC_LL_FREE_SPAN
            IC_HC_NOISE

    :param ll:
    :param ll_line:
    :param ampl_line:
    :param datax:
    :param torder:

    :param mode: string, if mode="new" uses python to work out gaussian fit
                         if mode="old" uses FORTRAN (testing only) requires
                         compiling of FORTRAN fitgaus into spirouTHORCA dir

    :return all_lines: list, all lines in format:

                    [order1lines, order2lines, order3lines, ..., orderNlines]

                    where order1lines = [gparams1, gparams2, ..., gparamsN]

                    where:
                        gparams[0] = output wavelengths
                        gparams[1] = output sigma (gauss fit width)
                        gparams[2] = output amplitude (gauss fit)
                        gparams[3] = difference in input/output wavelength
                        gparams[4] = input amplitudes
                        gparams[5] = output pixel positions
                        gparams[6] = output pixel sigma width
                                          (gauss fit width in pixels)
                        gparams[7] = output weights for the pixel position
                    (See fit_emi_line)

    """
    func_name = __NAME__ + '.find_lines()'
    # get parameters from p
    ll_sp_min = p['IC_LL_SP_MIN']
    ll_sp_max = p['IC_LL_SP_MAX']
    resol = p['IC_RESOL']
    ll_free_span = p['IC_LL_FREE_SPAN']
    image_ron = p['IC_HC_NOISE']

    # set update a pixel array
    xpos = np.arange(datax.shape[1])
    # set up storage
    all_cal_line_fit = []
    # loop around the orders
    for order_num in np.arange(datax.shape[0]):
        # order extend (in wavelengths)
        order_min, order_max = ll[order_num, 0], ll[order_num, -1]
        # select lines based on boundaries
        wave_mask = (ll_line >= order_min)
        wave_mask &= (ll_line <= order_max)
        wave_mask &= (ll_line >= ll_sp_min)
        wave_mask &= (ll_line <= ll_sp_max)
        # apply mask to ll_line and ampl_line
        ll_line_s = ll_line[wave_mask]
        ampl_line_s = ampl_line[wave_mask]
        # check to make sure we have lines
        if not len(ll_line_s) > 0:
            # if we have no lines print detailed error report and exit
            emsg1 = 'Order {0}: NO LINES IDENTIFIED!!'.format(order_num)
            emsg2args = [order_min, order_max]
            emsg2 = '   Order limit: [{0:6.1f}-{1:6.1f}]'.format(*emsg2args)
            emsg3args = [ll_sp_min, ll_sp_max]
            emsg3 = '   Hard limit: [{0:6.1f}-{1:6.1f}]'.format(*emsg3args)
            emsg4args = [ll_line[0], ll_line[-1]]
            emsg4 = '   Line interval: [{0:6.1f}-{1:6.1f}]'.format(*emsg4args)
            emsg5 = '       function={0}'.format(func_name)
            emsg6 = ' Unable to reduce, check guess solution'
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3, emsg4,
                                         emsg5, emsg6])
        gauss_fit = []

        # loop around the lines in kept line list
        for ll_i in np.arange(len(ll_line_s)):
            # get this iterations line
            line = float(ll_line_s[ll_i])
            # calculate line limits
            ll_span_min = line - ll_free_span * (line / (resol * 2.355))
            ll_span_max = line + ll_free_span * (line / (resol * 2.355))
            # calculate line mask for each span
            line_mask = ll[order_num] >= ll_span_min
            line_mask &= ll[order_num] <= ll_span_max
            # apply line mask to ll, xpos and data
            sll = ll[order_num, :][line_mask]
            sxpos = xpos[line_mask]
            sdata = datax[order_num, :][line_mask]
            # normalise sdata by the minimum sdata
            sdata = sdata - np.min(sdata)
            # work out a pixel weighting
            line_weight = np.sqrt(1.0 / (sdata + image_ron ** 2))

            # -----------------------------------------------------------------
            # fit the gaussians to each line
            try:
                fkwargs = dict(weights=line_weight,
                               return_fit=True,
                               return_uncertainties=True)
                results = spirouMath.fitgaussian_lmfit(sll, sdata, **fkwargs)
                params, siga, fit = results
            except Exception:
                params = [0.0, 0.0, 0.0, 0.0]
                siga = [0.0, 0.0, 0.0, 0.0]
                fit = np.zeros_like(sll)

            # check for infinites
            if np.sum(~np.isfinite(params) | ~np.isfinite(siga)) != 0:
                params = [0.0, 0.0, 0.0, 0.0]
                siga = [0.0, 0.0, 0.0, 0.0]
                fit = np.zeros_like(sll)

            # -----------------------------------------------------------------
            # get the wavelength and pixel difference
            slldiff = sll[-1] - sll[0]
            sxposdiff = sxpos[-1] - sxpos[0]
            # set up the gparams storage
            gparams = np.zeros(8, dtype='float')
            # Set the centre of the gaussian fit (in wavelengths)
            gparams[0] = params[1]
            # Set width of gaussian fit (in wavelengths)
            gparams[1] = params[2]
            # Set the difference in the input and output central wavelength fits
            gparams[2] = params[0]
            # Set the x pixel position (center)
            gparams[5] = (params[1] * sxposdiff) + sxpos[0]
            # Set the pixel width
            gparams[6] = params[2] * sxposdiff
            # Set the pixel weighting (depending on params[3]
            if params[3] * sxposdiff != 0:
                gparams[7] = 1.00/(siga[1] * sxposdiff)**2
            else:
                gparams[7] = 0.0
            # set the
            if gparams[7] > 0:
                # Set the difference in the input and output central wavelength fits
                gparams[3] = ll_line_s[ll_i] - params[1]
                # Set the input amplitude
                gparams[4] = ampl_line_s[ll_i]
            else:
                gparams[3], gparams[4] = 0.0, 0.0
            # finally append parameters to storage
            gauss_fit.append(gparams)
        # finally reshape all the gauss_fit parameters
        gauss_fit = np.array(gauss_fit).reshape(len(ll_line_s), 8)
        # calculate stats for logging
        min_ll, max_ll = ll_line_s[0], ll_line_s[-1]
        nlines_valid = np.sum(gauss_fit[:, 7] > 0)
        nlines_total = len(gauss_fit[:, 7])
        percentage_vlines = 100 * (nlines_valid/nlines_total)
        # log the stats for this order
        wmsg = 'Order {0:3} ({1:2}): [{2:6.1f} - {3:6.1f}]'
        wmsg += ' ({4:3}/{5:3})={6:3.1f}% lines identified'
        wargs = [torder[order_num], order_num, min_ll, max_ll,
                 nlines_valid, nlines_total, percentage_vlines]
        WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
        all_cal_line_fit.append(gauss_fit)

    # return all lines found (36 x number of lines found for order)
    return all_cal_line_fit





def fit_emi_line(sll, sxpos, sdata, weight, mode='new'):
    """
    Fit emission line

    :param sll:
    :param sxpos:
    :param sdata:
    :param weight:
    :param mode:

    :return gparams: list of length = 8:
                gparams[0] = output wavelengths
                gparams[1] = output sigma (gauss fit width)
                gparams[2] = output amplitude (gauss fit)
                gparams[3] = difference in input/output wavelength
                gparams[4] = input amplitudes
                gparams[5] = output pixel positions
                gparams[6] = output pixel sigma width
                                  (gauss fit width in pixels)
                gparams[7] = output weights for the pixel position
    """


    # get fit degree
    fitdegree = 2

    # set data less than or equal to 1 to 1
    smask = sdata > 1
    sdata1 = np.where(smask, sdata, np.ones_like(sdata))
    lsdata = np.log(sdata1)

    # set coeff array
    coeffs = np.zeros(fitdegree + 1)

    # normalise the wavelength data
    slln = (sll - sll[0])/(sll[-1]-sll[0])
    # test for NaNs
    if np.sum(~np.isfinite(slln)) != 0:
        coeffs[2] = 0
        slln = 0
    # if no NaNs work out weights and fit
    else:
        if not np.max(lsdata) == 0:
            # weights = sqrt(weight * sdata^2)
            weights = np.sqrt(weight*sdata**2)
            # fit the lsdata with a weighted polyfit
            coeffs = np.polyfit(slln, lsdata, fitdegree, w=weights)[::-1]

    # perform a gaussian fit
    gparams = np.zeros(8, dtype='float')
    params = np.zeros(4, dtype='float')

    # only perform gaussian fit if coeffs[2] (intercept) is negative
    if coeffs[2] < 0:
        # populate the guess for center (quadratic fit minimum)
        params[0] = -1 * coeffs[1] / (2 * coeffs[2])
        # populate the guess for FWHM
        params[1] = np.sqrt(-1/(2 * coeffs[2]))
        # populate the guess for the amplitude
        params[2] = np.exp(params[0]**2/(2 * params[1]**2) + coeffs[0])
        # set up the guess (from params)
        # f(x) = a1 * exp( -(x-a2)**2 / (2*a3**2) ) + a4
        gcoeffs = np.array([params[2], params[0], params[1], 0.0])
        # set up the weights for each pixel
        invsig = np.sqrt(weight)
        # fit a gaussian
        fkwargs = dict(weights=invsig, guess=gcoeffs, return_fit=False,
                       return_uncertainties=True)
        try:
            if mode == 'new':
                ag, siga = spirouMath.fitgaussian(slln, sdata, **fkwargs)

            # TODO: Test of fitgaus.fitfaus FORTRAN ROUTINE
            # TODO:     (requires fitgaus.so to be compiled and put in
            # TODO:      SpirouDRS.spirouTHORA folder)
            else:
                from SpirouDRS.fortran import fitgaus
                f = np.zeros_like(sdata)
                siga = np.zeros_like(gcoeffs)
                ag = gcoeffs.copy()
                fitgaus.fitgaus(slln,sdata,invsig,ag,siga,f)
            # copy the gaussian fit coefficients into params
            params[0] = ag[1]
            params[1] = ag[2]
            params[2] = ag[0]
            params[3] = siga[1]
        # if it breaks set parameters to bad parameters
        except RuntimeError:
            params[1] = 1
            params[2] = 0
            params[3] = 0
        # test for NaNs - if NaNs set to bad parameters
        if np.sum(~np.isfinite(params)) != 0:
            params[1] = 1
            params[2] = 0
            params[3] = 0
    # if coeff[2] (intercept) is positive set to bad parameters
    else:
        params[0] = 0
        params[1] = 1
        params[2] = 0
        params[3] = 0

    # get the wavelength different and position diff
    slldiff = sll[-1] - sll[0]
    sxposdiff = sxpos[-1] - sxpos[0]

    # set the gaussian parameters
    # Set the centre of the gaussian fit (in wavelengths)
    gparams[0] = (params[0] * slldiff) + sll[0]
    # Set width of gaussian fit (in wavelengths)
    gparams[1] = params[1] * slldiff
    # Set the amplitude of gaussian fit
    gparams[2] = params[2]
    # Set the difference in the input and output central wavelength fits
    gparams[3] = 0.0
    # Set the input amplitude
    gparams[4] = 0.0
    # Set the x pixel position (center)
    gparams[5] = (params[0] * sxposdiff) + sxpos[0]
    # Set the pixel width
    gparams[6] = params[1] * sxposdiff
    # Set the pixel weighting (depending on params[3]
    if params[3] * sxposdiff != 0:
        gparams[7] = 1.0/(params[3] * sxposdiff)**2
    else:
        gparams[7] = 0.0
    # return gparams
    return gparams


def fit_emi_line2(sll, sxpos, sdata, weight, mode='new'):
    """
    Fit emission line

    :param sll:
    :param sxpos:
    :param sdata:
    :param weight:
    :param mode:

    :return gparams: list of length = 8:
                gparams[0] = output wavelengths
                gparams[1] = output sigma (gauss fit width)
                gparams[2] = output amplitude (gauss fit)
                gparams[3] = difference in input/output wavelength
                gparams[4] = input amplitudes
                gparams[5] = output pixel positions
                gparams[6] = output pixel sigma width
                                  (gauss fit width in pixels)
                gparams[7] = output weights for the pixel position
    """
    # normalise the wavelength data
    slln = (sll - sll[0])/(sll[-1]-sll[0])
    # run the gaussian fit (using lmfit)
    invsig = np.sqrt(weight)
    fkwargs = dict(weights=invsig, return_fit=False,
                   return_uncertainties=True)
    ag, siga = spirouMath.fitgaussian_lmfit(slln, sdata, **fkwargs)
    # push the params into the correct order
    params = np.array([ag[1], ag[2], ag[0], siga[1]])
    # get the wavelength different and position diff
    slldiff = sll[-1] - sll[0]
    sxposdiff = sxpos[-1] - sxpos[0]
    # set the gaussian parameters
    gparams = np.zeros(8, dtype='float')
    # Set the centre of the gaussian fit (in wavelengths)
    gparams[0] = (params[0] * slldiff) + sll[0]
    # Set width of gaussian fit (in wavelengths)
    gparams[1] = params[1] * slldiff
    # Set the amplitude of gaussian fit
    gparams[2] = params[2]
    # Set the difference in the input and output central wavelength fits
    gparams[3] = 0.0
    # Set the input amplitude
    gparams[4] = 0.0
    # Set the x pixel position (center)
    gparams[5] = (params[0] * sxposdiff) + sxpos[0]
    # Set the pixel width
    gparams[6] = params[1] * sxposdiff
    # Set the pixel weighting (depending on params[3]
    if params[3] * sxposdiff != 0:
        gparams[7] = 1.0/(params[3] * sxposdiff)**2
    else:
        gparams[7] = 0.0
    # return gparams
    return gparams


def gauss_function(x, a, x0, sigma, dc):
    """
    A standard 1D gaussian function (for fitting against)]=

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2) + dc


def fit_1d_ll_solution(p, loc):

    func_name = __NAME__ + '.fit_1d_ll_solution()'
    # get constants from p
    #   max_weight is the weight corresponding to IC_ERRX_MIN
    max_weight = 1.0 / p['IC_ERRX_MIN'] ** 2
    fit_degree = p['IC_LL_DEGR_FIT']
    max_ll_fit_rms = p['IC_MAX_LLFIT_RMS']
    threshold = 1e-30
    # get data from loc
    all_lines = loc['ALL_LINES']
    torder = loc['ECHELLE_ORDERS']
    # Get the number of orders
    num_orders = loc['LL_INIT'].shape[0]
    # -------------------------------------------------------------------------
    # set up all storage
    final_iter = []       # will fill [wmean, var, length]
    final_param = []      # will fill the fit coefficients
    final_details = []    # will fill [lines, x_fit, cfit, weight]
    final_dxdl = []       # will fill the derivative of the fit coefficients
    scale = []            # conversion factor to km/s
    # set up global stats
    sweight = 0.0
    wsumres = 0.0
    wsumres2 = 0.0
    # loop around orders
    for order_num in np.arange(num_orders):
        # ---------------------------------------------------------------------
        # get this orders parameters
        weights = all_lines[order_num][:, 7]
        diff_in_out = all_lines[order_num][:, 3]
        centers = all_lines[order_num][:, 0]
        pixelcenters = all_lines[order_num][:, 5]
        # ---------------------------------------------------------------------
        # only keep the lines that have postive weight
        goodlinemask = weights > threshold
        lines = centers[goodlinemask] + diff_in_out[goodlinemask]
        x_fit = pixelcenters[goodlinemask]
        # get the weights and modify by max_weight
        weight = (weights[goodlinemask] * max_weight)
        weight = weight / (weights[goodlinemask] + max_weight)
        # ---------------------------------------------------------------------
        # iteratively try to improve the fit
        improve = 1
        iter, details = [], []
        wmean, var = 0, 0
        # sigma clip the largest rms until RMS < MAX_RMS
        while improve:
            # fit wavelength to pixel solution (with polynomial)
            ww = np.sqrt(weight)
            coeffs = np.polyfit(lines, x_fit, fit_degree, w=ww)[::-1]
            # calculate the fit
            cfit = np.polyval(coeffs[::-1], lines)
            # calculate the variance
            res = cfit - x_fit
            wsig = np.sum(res**2 * weight) / np.sum(weight)
            wmean = (np.sum(res * weight) / np.sum(weight))
            var = wsig - (wmean ** 2)
            # append stats
            iter.append([np.array(wmean), np.array(var),
                         np.array(coeffs)])
            details.append([np.array(lines),  np.array(x_fit),
                            np.array(cfit), np.array(weight)])
            # check improve condition (RMS > MAX_RMS)
            ll_fit_rms = abs(res) * np.sqrt(weight)
            badrms = ll_fit_rms > max_ll_fit_rms
            improve = np.sum(badrms)
            # set largest weighted residual to zero
            largest = np.max(ll_fit_rms)
            badpoints = ll_fit_rms == largest
            weight[badpoints] = 0.0
            # only keep the lines that have postive weight
            goodmask = weight > 0.0
            # check that we have points
            if np.sum(goodmask) == 0:
                emsg1 = ('Order {0}: Sigma clipping in 1D fit solution '
                         'failed'.format(order_num))
                emsg2 = ('\tRMS > MAX_RMS={0}'
                         ''.format(max_ll_fit_rms))
                emsg3 = '\tfunction = {0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
            else:
                lines = lines[goodmask]
                x_fit = x_fit[goodmask]
                weight = weight[goodmask]
        # ---------------------------------------------------------------------
        # log the fitted wave solution
        wmsg1 = 'Fit wave. sol. order: {0:3d} ({1:2d}) [{2:.1f}- {3:.1f}]'
        wargs1 = [torder[order_num], order_num, loc['LL_INIT'][order_num][0],
                  loc['LL_INIT'][order_num][-1]]
        wmsg2 = ('\tmean: {0:.4f}[mpix] rms={1:.5f} [mpix] ({2:2d} it.) '
                 '[{3} --> {4} lines] ')
        wargs2 = [wmean * 1000, np.sqrt(var) * 1000, len(iter),
                  len(details[0][1]), len(details[-1][1])]
        wmsgs = [wmsg1.format(*wargs1), wmsg2.format(*wargs2)]
        WLOG('', p['LOG_OPT'] + p['FIBER'], wmsgs)
        # ---------------------------------------------------------------------
        # append to all storage
        # ---------------------------------------------------------------------
        # append the last wmean, var and number of lines
        num_lines = len(details[-1][1])
        final_iter.append([iter[-1][0], iter[-1][1], num_lines])
        # append the last coefficients
        final_param.append(iter[-1][2])
        # append the last details [lines, x_fit, cfit, weight]
        final_details.append(np.array(details[-1]))
        # append the derivative of the coefficients
        poly = np.poly1d(iter[-1][2][::-1])
        dxdl = np.polyder(poly)(details[-1][0])
        final_dxdl.append(dxdl)
        # ---------------------------------------------------------------------
        # global statistics
        # ---------------------------------------------------------------------
        # work out conversion factor
        # TODO: speed of light proper!
        convert = speed_of_light / (dxdl * details[-1][0])
        # get res1
        res1 = details[-1][1] - details[-1][2]
        # sum the weights (recursively)
        sweight += np.sum(details[-1][3])
        # sum the weighted residuals in km/s
        wsumres += np.sum(res1 * convert * details[-1][3])
        # sum the weighted squared residuals in km/s
        wsumres2 += np.sum(details[-1][3] * (res1 * convert) ** 2 )
        # store the conversion to km/s
        scale.append(convert)
    # convert to arrays
    final_iter = np.array(final_iter)
    final_param = np.array(final_param)
    # calculate the final var and mean
    final_mean = (wsumres / sweight)
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # log the global stats
    total_lines = np.sum(final_iter[:, 2])
    wmsg1 = 'On fiber {0} fit line statistic:'.format(p['FIBER'])
    wargs2 = [final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
              total_lines, 1000.0 * np.sqrt(final_var / total_lines)]
    wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} lines (error on mean '
             'value:{3:.2f}[m/s])'.format(*wargs2))
    WLOG('info', p['LOG_OPT'] + p['FIBER'], [wmsg1, wmsg2])
    # save outputs to loc
    loc['FINAL_MEAN'] = final_mean
    loc['FINAL_VAR'] = final_var
    loc['FINAL_ITER'] = final_iter
    loc['FINAL_PARAM'] = final_param
    loc['FINAL_DETAILS'] = final_details
    loc['SCALE'] = scale
    sources = ['FINAL_MEAN',  'FINAL_VAR', 'FINAL_ITER', 'FINAL_PARAM',
               'FINAL_DETAILS', 'SCALE']
    loc.set_sources(sources, func_name)
    # return loc
    return loc


def invert_1ds_ll_solution(p, loc):
    func_name = __NAME__ + '.invert_1ds_ll_solution()'
    # get constants from p
    fit_degree = p['IC_LL_DEGR_FIT']
    # get data from loc
    details = loc['FINAL_DETAILS']
    iter = loc['FINAL_ITER']
    # Get the number of orders
    num_orders = loc['LL_INIT'].shape[0]
    # loop around orders
    inv_details = []
    inv_params = []
    sweight = 0.0
    wsumres = 0.0
    wsumres2 = 0.0
    for order_num in np.arange(num_orders):
        # get the lines and wavelength fit for this order
        lines = details[order_num][0]
        cfit = details[order_num][2]
        wei = details[order_num][3]
        # get the number of lines
        num_lines = len(lines)
        # set weights
        weight = np.ones(num_lines, dtype=float)
        # get fit coefficients
        coeffs = np.polyfit(cfit, lines, fit_degree, w=weight)[::-1]
        # get the y values for the coefficients
        icfit = np.polyval(coeffs[::-1], cfit)
        # work out the residuals
        res = icfit - lines
        # work out the normalised res in km/s
        nres = speed_of_light * (res / lines)
        # append values to storage
        inv_details.append([nres, wei])
        inv_params.append(coeffs)
        # ---------------------------------------------------------------------
        # invert parameters
        # ---------------------------------------------------------------------
        # sum the weights (recursively)
        sweight += np.sum(wei)
        # sum the weighted residuals in km/s
        wsumres += np.sum(nres * wei)
        # sum the weighted squared residuals in km/s
        wsumres2 += np.sum(wei * nres **2)
    # calculate the final var and mean
    final_mean = (wsumres / sweight)
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # log the invertion process
    total_lines = np.sum(iter[:, 2])
    wargs = [final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
             1000.0 * np.sqrt(final_var / total_lines)]
    wmsg = ('Inversion noise ==> mean={0:.3f}[m/s] rms={1:.1f}'
            '(error on mean value:{2:.2f}[m/s])'.format(*wargs))
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg)
    # save outputs to loc
    loc['LL_MEAN'] = final_mean
    loc['LL_VAR'] = final_var
    loc['INV_PARAM'] = np.array(inv_params)
    loc['INV_DETAILS'] = inv_details
    sources = ['LL_MEAN',  'LL_VAR', 'INV_PARAM', 'INV_DETAILS']
    loc.set_sources(sources, func_name)
    # return loc
    return loc


# =============================================================================
# End of code
# =============================================================================
