#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou THORCA module

Created on 2017-12-19 at 16:20

@author: cook

import rules: cannot import spirouWAVE
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
# get default program
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt
# Speed of light
speed_of_light = cc.c.to(uu.km/uu.s).value


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
    keys = ['KW_WAVE_ORD_N', 'KW_WAVE_LL_DEG', 'KW_TH_NAXIS1']
    try:
        gkv = spirouConfig.GetKeywordValues(p, whdr, keys, read_file)
        nbo, degll, xsize = gkv
    except spirouConfig.ConfigError as e:
        WLOG(e.level, p['LOG_OPT'], e.msg)
        nbo, degll, xsize = 0, 0, 0

    # get the coefficients from the header
    coeff_prefix = p['KW_WAVE_PARAM'][0]
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
    ll = spirouMath.get_ll_from_coefficients(param_ll, xsize, nbo)

    # return ll and param_ll
    return ll, param_ll


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


def first_guess_at_wave_solution(p, loc, mode=0):
    """
    First guess at wave solution, consistency check, using the wavelength
    solutions line list

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_HC_N_ORD_START: int, defines first order solution is calculated
            IC_HC_N_ORD_FINAL: int, defines last order solution is calculated
                                from
            IC_HC_T_ORDER_START: int, defines the echelle order of
                                the first e2ds order
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
    n_order_final = p['IC_HC_N_ORD_FINAL']
    n_order_start = p['IC_HC_N_ORD_START']
    freespan = p['IC_LL_FREE_SPAN']
    # set up the orders to fit
    orderrange = np.arange(n_order_start, n_order_final)
    loc['ECHELLE_ORDERS'] = p['IC_HC_T_ORDER_START'] - orderrange
    loc.set_source('ECHELLE_ORDERS', func_name)

    # get wave solution filename
    wave_file = spirouImage.ReadWaveFile(p, loc['HCHDR'], return_filename=True)
    # log wave file name
    wmsg = 'Reading initial wavelength solution in {0}'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(wave_file))

    # get E2DS line list from wave_file
    ll_init, param_ll_init = get_e2ds_ll(p, loc['HCHDR'], filename=wave_file)
    # only perform fit on orders 0 to p['IC_HC_N_ORD_FINAL']
    loc['LL_INIT'] = ll_init[n_order_start:n_order_final]
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
             loc['HCDATA'][p['IC_HC_N_ORD_START']:p['IC_HC_N_ORD_FINAL']], loc['ECHELLE_ORDERS'],
             freespan]
    all_lines = find_lines(*fargs, mode=mode)
    # add all lines to loc
    loc['ALL_LINES_1'] = all_lines
    loc.set_source('ALL_LINES_1', func_name)
    # return loc
    return loc


def detect_bad_lines(p, loc, key=None, iteration=0):

    # get constants from p
    max_error_onfit = p['IC_MAX_ERRW_ONFIT']
    max_error_sigll = p['IC_MAX_SIGLL_CAL_LINES']
    max_ampl_lines = p['IC_MAX_AMPL_LINE']
    t_ord_start = p['IC_HC_T_ORDER_START']
    torder = loc['ECHELLE_ORDERS']


    # deal with key
    if key is None:
        key = 'ALL_LINES_{0}'.format(iteration)
    elif key in loc:
        pass
    else:
        emsg = 'key = "{0}" not defined in "loc"'
        WLOG('error', p['LOG_OPT'], emsg.format(key))
        key = None

    #good lines count
    good_lines_total = 0
    # loop around each order
    for order_num in range(len(loc[key])):
        # get all lines 7
        lines = np.array(loc[key][order_num])
        # keep only vqlid lines
        testmask = lines[:,2]>0
        lines = lines[testmask]
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
        #TODO remove lines with sigll < 1 pixel ?
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
        good_lines_total += num_total - num_bad
        # log only if we have bad
        if np.sum(badlines) > 0:
#            wargs = [order_num, num_bad, num_total, num_badsig, num_badampl,
#                     num_badfit]
#            wmsg = ('In Order {0} reject {1}/{2} ({3}/{4}/{5}) lines '
#                    '[beyond (sig/ampl/err) limits]')
            wargs = [torder[order_num], t_ord_start - torder[order_num],
                     num_total - num_bad, num_badsig, num_badampl,
                     num_badfit]
            wmsg = ('In Order {0:3} ({1:2}) keep {2} lines / ({3}/{4}/{5}) lines '
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
    # print total of good lines
    wargs = [good_lines_total]
    wmsg = ('Total good lines: {0}')
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(*wargs))

    # return loc
    return loc


def fit_1d_solution(p, loc, ll, iteration=0):

    func_name = __NAME__ + '.fit_1d_solution()'
    # get 1d solution
    loc = fit_1d_ll_solution(p, loc, ll, iteration)
    # invert solution
    loc = invert_1ds_ll_solution(p, loc, ll, iteration)
    # get the total number of orders to fit
    num_orders = len(loc['ALL_LINES_{0}'.format(iteration)])
    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # get inv_params
    inv_params = loc['LL_PARAM_{0}'.format(iteration)]
    # get new line list
    ll_out = spirouMath.get_ll_from_coefficients(inv_params, xdim, num_orders)
    # get the first derivative of the line list
    dll_out = spirouMath.get_dll_from_coefficients(inv_params, xdim, num_orders)
    # find the central pixel value
    centpix = ll_out.shape[1]//2
    # get the mean pixel scale (in km/s/pixel) of the central pixel
    norm = dll_out[:, centpix]/ll_out[:, centpix]
    meanpixscale = speed_of_light * np.sum(norm)/len(ll_out[:, centpix])
    # add to loc
    loc['LL_OUT_{0}'.format(iteration)] = ll_out
    loc.set_source('LL_OUT_{0}'.format(iteration), func_name)
    loc['DLL_OUT_{0}'.format(iteration)] = dll_out
    loc.set_source('DLL_OUT_{0}'.format(iteration), func_name)
    # log message
    wmsg = 'On fiber {0} mean pixel scale at center: {1:.4f} [km/s/pixel]'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['FIBER'], meanpixscale))
    # return loc
    return loc


def calculate_littrow_sol(p, loc, ll, iteration=0, log=False):

    func_name = __NAME__ + '.calculate_littrow_sol()'
    # get parameters from p
    remove_orders = p['IC_LITTROW_REMOVE_ORDERS']
    n_order_init = p['IC_LITTROW_ORDER_INIT']
    n_order_final = p['IC_HC_N_ORD_FINAL']
    n_order_start = p['IC_HC_N_ORD_START']
    x_cut_step = p['IC_LITTROW_CUT_STEP_{0}'.format(iteration)]
    fit_degree = p['IC_LITTROW_FIT_DEG_{0}'.format(iteration)]
    # get parameters from loc
    torder = loc['ECHELLE_ORDERS']
    ll_out = ll
    # test if n_order_init is in remove_orders
    if n_order_init in remove_orders:
        wargs = ["IC_LITTROW_ORDER_INIT", p['IC_LITTROW_ORDER_INIT'],
                 "IC_LITTROW_REMOVE_ORDERS"]
        wmsg1 = 'Warning {0}={1} in {2}'.format(*wargs)
        # TODO: Remove H2RG dependency
        wmsg2 = ('    Please check constants_SPIROU_{0}.py file'
                 ''.format(p['IC_IMAGE_TYPE']))
        wmsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [wmsg1, wmsg2, wmsg3])
    # test if n_order_init is in remove_orders
    if n_order_final in remove_orders:
        wargs = ["IC_HC_N_ORD_FINAL", p['IC_HC_N_ORD_FINAL'],
                 "IC_LITTROW_REMOVE_ORDERS"]
        wmsg1 = 'Warning {0}={1} in {2}'.format(*wargs)
        # TODO: Remove H2RG dependency
        wmsg2 = ('    Please check constants_SPIROU_{0}.py file'
                 ''.format(p['IC_IMAGE_TYPE']))
        wmsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [wmsg1, wmsg2, wmsg3])
    # check that all remove orders exist
    for remove_order in remove_orders:
        if remove_order not in np.arange(n_order_final):
            wargs1 = [remove_order, 'IC_LITTROW_REMOVE_ORDERS', n_order_init,
                       n_order_final]
            wmsg1 = (' Invalid order number={0} in {1} must be between'
                     '{2} and {3}'.format(*wargs1))
            wmsg2 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [wmsg1, wmsg2])

    # check to make sure we have some orders left
    if len(np.unique(remove_orders)) == n_order_final - n_order_start:
        wmsg = 'Cannot remove all orders. Check IC_LITTROW_REMOVE_ORDERS'
        WLOG('error', p['LOG_OPT'], wmsg)
    # get the total number of orders to fit
    num_orders = len(loc['ALL_LINES_{0}'.format(iteration)])
    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # deal with removing orders (via weighting stats)
    rmask = np.ones(num_orders, dtype=bool)
    if len(remove_orders) > 0:
        rmask[np.array(remove_orders)] = False
    # storage of results
    keys = ['LITTROW_MEAN', 'LITTROW_SIG', 'LITTROW_MINDEV',
            'LITTROW_MAXDEV', 'LITTROW_PARAM', 'LITTROW_XX', 'LITTROW_YY']
    for key in keys:
        nkey = key + '_{0}'.format(iteration)
        loc[nkey] = []
        loc.set_source(nkey, func_name)
    # construct the Littrow cut points
    x_cut_points = np.arange(x_cut_step, xdim-x_cut_step, x_cut_step)
    # save to storage
    loc['X_CUT_POINTS_{0}'.format(iteration)] = x_cut_points
    # get the echelle order values
    #TODO check if mask needs resizing
    orderpos = torder[rmask]
    # get the inverse order number
    inv_orderpos = 1.0 / orderpos
    # loop around cut points and get littrow parameters and stats
    for it in range(len(x_cut_points)):
        # this iterations x cut point
        x_cut_point = x_cut_points[it]
        # get the fractional wavelength contrib. at each x cut point
        ll_point = ll_out[:, x_cut_point][rmask]
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
        loc['LITTROW_MEAN_{0}'.format(iteration)].append(mean)
        loc['LITTROW_SIG_{0}'.format(iteration)].append(rms)
        loc['LITTROW_MINDEV_{0}'.format(iteration)].append(mindev)
        loc['LITTROW_MAXDEV_{0}'.format(iteration)].append(maxdev)
        loc['LITTROW_PARAM_{0}'.format(iteration)].append(coeffs)
        loc['LITTROW_XX_{0}'.format(iteration)].append(orderpos)
        loc['LITTROW_YY_{0}'.format(iteration)].append(respix)
        # if log then log output
        if log:
            emsg1 = 'Littrow check at X={0}'.format(x_cut_point)
            eargs = [mean * 1000, rms * 1000, mindev * 1000, maxdev * 1000,
                     mindev/rms, maxdev/rms]
            emsg2 = ('    mean:{0:.3f}[m/s] rms:{1:.2f}[m/s] min/max:{2:.2f}/'
                     '{3:.2f}[m/s] (frac:{4:.1f}/{5:.1f})'.format(*eargs))
            WLOG('info', p['LOG_OPT'] + p['FIBER'], [emsg1, emsg2])

    # return loc
    return loc


def extrapolate_littrow_sol(p, loc, ll, iteration=0):

    func_name = __NAME__ + '.extrapolate_littrow_sol()'
    # get parameters from p
    fit_degree = p['IC_LITTROW_ORDER_FIT_DEG']
    t_order_start = p['IC_HC_T_ORDER_START']
    n_order_init = p['IC_LITTROW_ORDER_INIT']

    # get parameters from loc
    litt_param = loc['LITTROW_PARAM_{0}'.format(iteration)]

    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # get the pixel positions
    x_points = np.arange(xdim)
    # construct the Littrow cut points (in pixels)
    x_cut_points = loc['X_CUT_POINTS_{0}'.format(iteration)]
    # construct the Littrow cut points (in wavelength)
    ll_cut_points = ll[n_order_init][x_cut_points]

    # set up storage
    littrow_extrap = np.zeros((ydim, len(x_cut_points)), dtype=float)
    littrow_extrap_sol = np.zeros_like(loc['HCDATA'])
    littrow_extrap_param = np.zeros((ydim, fit_degree + 1),dtype=float)

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
        littrow_extrap[:, it] = litt_extrap_o

    for order_num in range(ydim):
        # fit the littrow extrapolation
        param = np.polyfit(x_cut_points, littrow_extrap[order_num],
                           fit_degree)[::-1]
        # add to storage
        littrow_extrap_param[order_num] = param
        # evaluate the polynomial for all pixels in data
        littrow_extrap_sol[order_num] = np.polyval(param[::-1], x_points)

    # add to storage
    loc['LITTROW_EXTRAP_{0}'.format(iteration)] = littrow_extrap
    loc['LITTROW_EXTRAP_SOL_{0}'.format(iteration)] = littrow_extrap_sol
    loc['LITTROW_EXTRAP_PARAM_{0}'.format(iteration)] = littrow_extrap_param

    sources = ['LITTROW_EXTRAP_{0}'.format(iteration),
               'LITTROW_EXTRAP_SOL_{0}'.format(iteration),
               'LITTROW_EXTRAP_PARAM_{0}'.format(iteration)]
    loc.set_sources(sources, func_name)
    # return loc
    return loc


def second_guess_at_wave_solution(p, loc, mode=0):

    func_name = __NAME__ + '.second_guess_at_wave_solution()'
    # Update the free span wavelength value
    freespan = p['IC_LL_FREE_SPAN_2']
    # New final order value
    n_ord_final = p['IC_HC_N_ORD_FINAL']
    n_ord_start = p['IC_HC_N_ORD_START']
    n_ord_start_2 = p['IC_HC_N_ORD_START_2']
    n_ord_final_2 = p['IC_HC_N_ORD_FINAL_2']
    # recalculate echelle order number
    echelle_order = p['IC_HC_T_ORDER_START'] - np.arange(n_ord_start_2, n_ord_final_2)
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', func_name)


    # set the starting point as the outputs from the first guess solution
    # loop around original order num
#    ll_line_2, ampl_line_2 = [], []
#    for order_num in range(n_ord_final - n_ord_start):
        # get this orders details
#        details = loc['X_DETAILS_1'][order_num]
        # append to lists
#        ll_line_2 = np.append(ll_line_2, details[0])
#        ampl_line_2 = np.append(ampl_line_2, details[3])

    # Now add in any lines which are outside the range of the first guess
    #    solution
#    lmask = loc['LL_LINE'] > np.max(ll_line_2)
#    lmask |= loc['LL_LINE'] < np.min(ll_line_2)
#    ll_line_2 = np.append(ll_line_2, loc['LL_LINE'][lmask])
#    ampl_line_2 = np.append(ampl_line_2, loc['AMPL_LINE'][lmask])
#    ll_line_2_sortmask = ll_line_2.argsort()
#    ll_line_2 = ll_line_2[ll_line_2_sortmask]
#    ampl_line_2 = ampl_line_2[ll_line_2_sortmask]

    #use whole catalogue
    ll_line_2 = loc['LL_LINE']
    ampl_line_2 = loc['AMPL_LINE']

    # log second pass
    wmsg = ('On fiber {0} trying to identify lines using guess solution '
            '(second pass)'.format(p['FIBER']))
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg)

    # find the lines
    ll = loc['LITTROW_EXTRAP_SOL_1'][n_ord_start_2:n_ord_final_2]
    datax = loc['HCDATA'][n_ord_start_2:n_ord_final_2]

    fargs = [p, ll, ll_line_2, ampl_line_2, datax, echelle_order, freespan]
    all_lines = find_lines(*fargs, mode=mode)

    # add all lines to loc
    loc['ALL_LINES_2'] = all_lines
    loc.set_source('ALL_LINES_2', func_name)
    # return loc
    return loc


def join_orders(p, loc):

    func_name = __NAME__ + '.join_orders()'
    # get parameters from p
    n_ord_start_2 = p['IC_HC_N_ORD_START_2']
    n_ord_final_2 = p['IC_HC_N_ORD_FINAL_2']

    # get data from loc
    # the second iteration outputs
    ll_out_2 = loc['LL_OUT_2']
    param_out_2 = loc['LL_PARAM_2']

    # the littrow extrapolation (for orders < n_ord_start_2)
    littrow_extrap_sol_blue = loc['LITTROW_EXTRAP_SOL_2'][:n_ord_start_2]
    littrow_extrap_sol_param_blue = loc['LITTROW_EXTRAP_PARAM_2'][:n_ord_start_2]

    # the littrow extrapolation (for orders > n_ord_final_2)
    littrow_extrap_sol_red = loc['LITTROW_EXTRAP_SOL_2'][n_ord_final_2:]
    littrow_extrap_sol_param_red = loc['LITTROW_EXTRAP_PARAM_2'][n_ord_final_2:]

    # create stack
    ll_stack, param_stack = [], []
    # add extrapolation from littrow to orders < n_ord_start_2
    if len(littrow_extrap_sol_blue) > 0:
        ll_stack.append(littrow_extrap_sol_blue)
        param_stack.append(littrow_extrap_sol_param_blue)
    # add second iteration outputs
    if len(ll_out_2) > 0:
        ll_stack.append(ll_out_2)
        param_stack.append(param_out_2)
    # add extrapolation from littrow to orders > n_ord_final_2
    if len(littrow_extrap_sol_red) > 0:
        ll_stack.append(littrow_extrap_sol_red)
        param_stack.append(littrow_extrap_sol_param_red)

    # convert stacks to arrays and add to storage
    loc['LL_FINAL'] = np.vstack(ll_stack)
    loc['LL_PARAM_FINAL'] = np.vstack(param_stack)
    loc.set_sources(['LL_FINAL', 'LL_PARAM_FINAL'], func_name)

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


def find_lines(p, ll, ll_line, ampl_line, datax, torder, freespan, mode='new'):
    """
    Find the lines on the E2DS spectrum

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LL_SP_MIN   minimum wavelength of the catalog
            IC_LL_SP_MAX   maximum wavelength of the catalog
            IC_RESOL       Resolution of spectrograph
            IC_LL_FREE_SPAN   window size in sigma unit
            IC_HC_NOISE

    :param ll:
    :param ll_line:
    :param ampl_line:
    :param datax:
    :param torder:
    :param freespan:

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
    t_ord_start = p['IC_HC_T_ORDER_START']
    resol = p['IC_RESOL']
    ll_free_span = freespan
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
            for span in ll_free_span:
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
                # make sure we have more than 4 data points to fit a gaussian
                if len(sxpos) < 4:
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
#        min_ll, max_ll = ll_line_s[0], ll_line_s[-1]
        min_ll, max_ll = np.min(ll_line_s), np.max(ll_line_s)
        nlines_valid = np.sum(gauss_fit[:, 2] > 0)
        nlines_total = len(gauss_fit[:, 2])
        percentage_vlines = 100 * (nlines_valid/nlines_total)
        # log the stats for this order
        wmsg = 'Order {0:3} ({1:2}): [{2:6.1f} - {3:6.1f}]'
        wmsg += ' ({4:3}/{5:3})={6:3.1f}% lines identified'
        wargs = [torder[order_num], t_ord_start - torder[order_num], min_ll, max_ll,
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
        try:
            # choose between fit gaussian types
            ag, siga, cfit = fitgaus_wrapper(slln, sdata, invsig, gcoeffs,
                                             mode=mode)
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
        # TODO: This should be here and work!!!
        # if np.sum(~np.isfinite(params)) != 0:
        #     params[1] = 1
        #     params[2] = 0
        #     params[3] = 0
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


def fitgaus_wrapper(x, y, invsig, guess, mode=0):
    """
    Fits a guassian to "y" (at positions "x") with weights "invsig" based on an
    initial "guess" - fit process method depends on "mode" selected

    :param x: numpy array (1D), the input x-axis
    :param y: numpy array (1D), the input y-axis (to fit) - same shape as x
    :param invsig: numpy array (1D), the weights - same shape as x
    :param guess: numpy array (1D), the initial guess for the fit
                    (Amplitude, Center, Sigma, DC)
    :param mode: define the mode to use. Current allowed modes are:
         0: Fortran "fitgaus" routine (requires SpirouDRS.fortran.figgaus.f
            to be compiled using f2py:
                f2py -c -m fitgaus --noopt --quiet fitgaus.f
         1: Python fit using scipy.optimize.curve_fit
         2: Python fit using lmfit.models (Model, GaussianModel) - requires
             lmfit python module to be installed (pip install lmfit)
         3: Python (conversion of Fortran "fitgaus") - direct fortran gaussj
         4: Python (conversion of Fortran "fitgaus") - gaussj Melissa
         5: Python (conversion of Fortran "fitgaus") - gaussj Neil

    :return ag: numpy array (1D), the fit parameters
                    (Amplitude, Center, Sigma, DC)
    :return siga: numpy array (1D), the errors of the fit parameters
                    (Amplitude, Center, Sigma, DC)
    :return cfig: numpy array (1D), the fit points for this gaussian
                    (shape = same as x and y)
    """

    func_name = __NAME__ + '.fitgaus_wrapper()'
    # TODO: Test of fitgaus.fitfaus FORTRAN ROUTINE
    # TODO:     (requires fitgaus.so to be compiled and put in
    # TODO:      SpirouDRS.spirouTHORA folder)
    if mode == 0:
        try:
            from SpirouDRS.fortran import fitgaus
        except:
            emsg1 = 'Fortran module "fitgaus" required.'
            emsg2 = '   Please install in .../SpirouDRS/fortran/'
            emsg3 = '   i.e. use: '
            emsg4 = '      f2py -c -m fitgaus --noopt --quiet fitgaus.f'
            WLOG('error', DPROG, [emsg1, emsg2, emsg3, emsg4])
        cfit = np.zeros_like(y)
        siga = np.zeros_like(guess)
        ag = np.array(guess)
        fitgaus.fitgaus(x, y, invsig, ag, siga, cfit)
    elif mode == 1:
        fkwargs = dict(weights=invsig, guess=guess, return_fit=True,
                       return_uncertainties=True)
        ag, siga, cfit = spirouMath.fitgaussian(x, y, **fkwargs)
    elif mode == 2:
        fkwargs = dict(weights=invsig, return_fit=True,
                       return_uncertainties=True)
        ag, siga, cfit = spirouMath.fitgaussian_lmfit(x, y, **fkwargs)
    elif mode == 3:
        try:
            from SpirouDRS.fortran import gfit
        except Exception as e:
            emsg1 = 'Python file "gfit" error'
            emsg2 = '    located in .../SpirouDRS/fortran/'
            emsg3 = '    error reads:'
            emsg4 = '        {0}'.format(e)
            WLOG('error', DPROG, [emsg1, emsg2, emsg3, emsg4])
        ag, siga, cfit = gfit.fitgaus(x, y, invsig, guess, mode=0)
    elif mode == 4:
        try:
            from SpirouDRS.fortran import gfit
        except Exception as e:
            emsg1 = 'Python file "gfit" error'
            emsg2 = '    located in .../SpirouDRS/fortran/'
            emsg3 = '    error reads:'
            emsg4 = '        {0}'.format(e)
            WLOG('error', DPROG, [emsg1, emsg2, emsg3, emsg4])
        ag, siga, cfit = gfit.fitgaus(x, y, invsig, guess, mode=1)
    elif mode == 5:
        try:
            from SpirouDRS.fortran import gfit
        except Exception as e:
            emsg1 = 'Python file "gfit" error'
            emsg2 = '    located in .../SpirouDRS/fortran/'
            emsg3 = '    error reads:'
            emsg4 = '        {0}'.format(e)
            WLOG('error', DPROG, [emsg1, emsg2, emsg3, emsg4])
        ag, siga, cfit = gfit.fitgaus(x, y, invsig, guess, mode=2)
    else:
        emsg1 = 'Mode not understood. Must be 0, 1, 2, 3, 4 or 5'
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])
        ag, siga, cfit = None, None, None

    # return outputs
    return ag, siga, cfit


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


def fit_1d_ll_solution(p, loc, ll, iteration):
    func_name = __NAME__ + '.fit_1d_ll_solution()'
    # get constants from p
    #   max_weight is the weight corresponding to IC_ERRX_MIN
    max_weight = 1.0 / p['IC_ERRX_MIN'] ** 2
    fit_degree = p['IC_LL_DEGR_FIT']
    max_ll_fit_rms = p['IC_MAX_LLFIT_RMS']
    t_ord_start = p['IC_HC_T_ORDER_START']
    threshold = 1e-30
    # get data from loc
    torder = loc['ECHELLE_ORDERS']
    all_lines = loc['ALL_LINES_{0}'.format(iteration)]
    # Get the number of orders
    num_orders = ll.shape[0]
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
        wargs1 = [torder[order_num], t_ord_start - torder[order_num], ll[order_num][0],
                  ll[order_num][-1]]
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
    loc['X_MEAN_{0}'.format(iteration)] = final_mean
    loc['X_VAR_{0}'.format(iteration)] = final_var
    loc['X_ITER_{0}'.format(iteration)] = final_iter
    loc['X_PARAM_{0}'.format(iteration)] = final_param
    loc['X_DETAILS_{0}'.format(iteration)] = final_details
    loc['SCALE_{0}'.format(iteration)] = scale
    sources = ['X_MEAN_{0}'.format(iteration),
               'X_VAR_{0}'.format(iteration),
               'X_ITER_{0}'.format(iteration),
               'X_PARAM_{0}'.format(iteration),
               'X_DETAILS_{0}'.format(iteration),
               'SCALE_{0}'.format(iteration)]
    loc.set_sources(sources, func_name)
    # return loc
    return loc


def invert_1ds_ll_solution(p, loc, ll, iteration=0):
    func_name = __NAME__ + '.invert_1ds_ll_solution()'
    # get constants from p
    fit_degree = p['IC_LL_DEGR_FIT']
    # get data from loc
    details = loc['X_DETAILS_{0}'.format(iteration)]
    iter = loc['X_ITER_{0}'.format(iteration)]
    # Get the number of orders
    num_orders = ll.shape[0]
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
    loc['LL_MEAN_{0}'.format(iteration)] = final_mean
    loc['LL_VAR_{0}'.format(iteration)] = final_var
    loc['LL_PARAM_{0}'.format(iteration)] = np.array(inv_params)
    loc['LL_DETAILS_{0}'.format(iteration)] = inv_details
    sources = ['LL_MEAN_{0}'.format(iteration),
               'LL_VAR_{0}'.format(iteration),
               'LL_PARAM_{0}'.format(iteration),
               'LL_DETAILS_{0}'.format(iteration)]
    loc.set_sources(sources, func_name)
    # return loc
    return loc


# =============================================================================
# End of code
# =============================================================================
