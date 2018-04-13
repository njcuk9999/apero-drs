#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou THORCA module

Created on 2017-12-19 at 16:20

@author: cook

"""
from __future__ import division
import numpy as np

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


def first_guess_at_wave_solution(p, loc):
    """
    First guess at wave solution, consistency check, using the wavelength
    solutions line list

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            CAL_HC_N_ORD_FINAL
            CAL_HC_T_ORDER_START
            log_opt
            fiber

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                FIT_ORDERS
                LL_INIT
                LL_LINE
                AMPL_LINE

    """
    func_name = __NAME__ + '.first_guess_at_wave_solution()'
    # get used constants from p
    n_order_final = p['CAL_HC_N_ORD_FINAL']
    # set up the orders to fit
    loc['fit_orders'] = p['CAL_HC_T_ORDER_START'] - np.arange(n_order_final)
    loc.set_source('fit_orders', func_name)
    # get wave solution filename
    wave_file = spirouImage.ReadWaveFile(p, loc['hdr'], return_filename=True)
    # log wave file name
    wmsg = 'Reading initial wavelength solution in {0}'
    WLOG('', p['log_opt'] + p['fiber'], wmsg.format(wave_file))
    # get E2DS line list from wave_file
    ll_init, param_ll_init = get_e2ds_ll(p, loc['hdr'], filename=wave_file)
    # only perform fit on orders 0 to p['CAL_HC_N_ORD_FINAL']
    loc['ll_init'] = ll_init[:n_order_final]
    loc.set_source('ll_init', __NAME__ + func_name)
    # load line file (from p['IC_LL_LINE_FILE'])
    loc['ll_line'], loc['ampl_line'] = spirouImage.ReadLineList(p)
    source = func_name + ' spirouImage.ReadLineList()'
    loc.set_sources(['ll_line', 'ampl_line'], source)
    # log that we are attempting to find ll on spectrum
    wmsg = 'On fiber {0} trying to identify lines using guess solution'
    WLOG('', p['log_opt'] + p['fiber'], wmsg.format(p['fiber']))
    # find the lines
    loc = find_lines(p, loc)



    return loc


def find_lines(p, loc):
    """
    Find the lines on the E2DS spectrum

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LL_SP_MIN
            IC_LL_SP_MAX
            IC_RESOL
            IC_LL_FREE_SPAN
            IC_HC_NOISE

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            LL_INIT
            LL_LINE
            AMPL_LINE
            DATA
            FIT_ORDERS

    :return:
    """
    func_name = __NAME__ + '.find_lines()'
    # get parameters from p
    ll_sp_min = p['IC_LL_SP_MIN']
    ll_sp_max = p['IC_LL_SP_MAX']
    resol = p['IC_RESOL']
    ll_free_span = p['IC_LL_FREE_SPAN']
    image_ron = p['IC_HC_NOISE']
    # get parameters from loc
    ll = loc['LL_INIT']
    ll_line = loc['LL_LINE']
    ampl_line = loc['AMPL_LINE']
    data = loc['DATA']
    torder = loc['FIT_ORDERS']
    # set update a pixel array
    xpos = np.arange(data.shape[1])
    # set up storage
    all_cal_line_fit = []
    # loop around the orders
    for order_num in np.arange(data.shape[0]):
        # order extend (in wavelengths)
        order_min, order_max = np.min(ll[order_num]), np.max(ll[order_num])
        # select lines based on boundaries
        wave_mask = (ll_line >= order_min)
        wave_mask &= (ll_line <= order_max)
        wave_mask &= (ll_line >= ll_sp_min)
        wave_mask &= (ll_line <= ll_sp_max)
        # apply mask to ll_line and ampl_line
        ll_line_s = ll_line[wave_mask]
        ampl_line_s = ampl_line[wave_mask]
        # check to make sure we have lines
        if len(ll_line_s) > 0:
            gauss_fit = []
        else:
            # if we have no lines print detailed error report and exit
            emsg1 = 'Order {0}: NO LINES IDENTIFIED!!'.format(order_num)
            emsg2args = [order_min, order_max]
            emsg2 = '   Order limit: [{0:6.1f}-{1:6.1f}]'.format(*emsg2args)
            emsg3args = [ll_sp_min, ll_sp_max]
            emsg3 = '   Hard limit: [{0:6.1f}-{1:6.1f}]'.format(*emsg3args)
            emsg4args = [np.min(ll_line), np.max(ll_line)]
            emsg4 = '   Line interval: [{0:6.1f}-{1:6.1f}]'.format(*emsg4args)
            emsg5 = '       function={0}'.format(func_name)
            emsg6 = ' Unable to reduce, check guess solution'
            WLOG('error', p['log_opt'], [emsg1, emsg2, emsg3, emsg4,
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
                sll = ll[order_num][line_mask]
                sxpos = xpos[line_mask]
                sdata = data[order_num][line_mask]
                # normalise sdata by the minimum sdata
                sdata -= np.min(sdata)
                # make sure we have more than 3 data points
                if len(sxpos) < 3:
                    wmsg = 'Resolution or ll_span are too small'
                    WLOG('', p['log_opt'], wmsg)
                # work out a pixel weighting
                line_weight = 1.0/(sdata + image_ron**2)
                # check that the sum of the weighted flux is not zero
                if np.sum(sdata * line_weight) != 0:
                    # if it isn't zero set the line value to the
                    #   weighted mean value
                    line = np.sum(sll * sdata * line_weight)
                    line /= np.sum(sdata * line_weight)
                else:
                    # if it is zero then just use the line
                    line = float(ll_line_s[ll_i])
                # perform the gaussian fit on the line
                gau_param = fit_emi_line(sll, sxpos, sdata, line_weight)
                # check if gau_param[7] is positive
                if gau_param[7] > 0:
                    gau_param[3] = ll_line_s[ll_i] - gau_param[0]
                    gau_param[4] = ampl_line_s[ll_i]
                # finally append parameters to storage
                gauss_fit.append(gau_param)
            # finally reshape all the gauss_fit parameters
            gauss_fit = gauss_fit.reshape(len(ll_line_s, 8))
            # calculate stats for logging
            min_ll, max_ll = np.min(ll_line_s), np.max(ll_line_s)
            nlines_valid = np.sum(gauss_fit[:, 2] > 0)
            nlines_total = len(gauss_fit[:, 2])
            percentage_vlines = 100 * (nlines_valid/nlines_total)
            # log the stats for this order
            wmsg = 'Order {0:3} ({1:2}): [{2:6.1f} - {3:6.1f}]'
            wmsg += ' ({4:3}/{5:3})={6:3}% lines identified'
            wargs = [torder[order_num], order_num, min_ll, max_ll,
                     nlines_valid, nlines_total, percentage_vlines]
            WLOG('', p['log_opt'], wmsg.format(*wargs))
            all_cal_line_fit.append(gauss_fit)
    # return all lines found (36 x number of lines found for order)
    return all_cal_line_fit


def fit_emi_line(sll, sxpos, sdata, weight):

    # get fit degree
    fitdegree = 3

    # set data less than or equal to 1 to 1
    smask = sdata > 1
    sdata1 = np.where(smask, sdata, np.ones_like(sdata))
    lsdata = np.log(sdata1)

    # set coeff array
    coeffs = np.zeros(fitdegree)

    # perform a weighted fit
    slln = (sll - sll[0])/(sll[-1]-sll[0])
    # test for NaNs
    if np.sum(~np.isfinite[slln]) != 0:
        coeffs[2] = 0
        slln = 0
    else:
        if not np.max(lsdata) == 0:
            weights = np.sqrt(weight*sdata**2)
            coeffs = np.polyfit(slln, lsdata, fitdegree, w=weights)[::-1]

    # perform a gaussian fit
    gparams = np.zeros(9, dtype='float')
    params = np.zeros(4, dtype='float')

    # only perform gaussian fit if coeffs[2] is negative
    if coeffs[2] < 0:
        # populate the guess for center
        params[0] = -1 * coeffs[1]/ (2 * coeffs[2])
        # populate the guess for FWHM
        params[1] = np.sqrt(-1/(2 * coeffs[2]))
        # populate the guess for the amplitude
        params[2] = np.exp(params[0]**2/(2 * params[1]**2) + coeffs[0])
        # set up the guess (from params)
        coeffs = np.array([params[2], params[0], params[1], 0])
        # set up the weights for each pixel
        invsig = np.sqrt(weight)
        # fit a gaussian
        fkwargs = dict(weights=invsig, guess=coeffs, return_fit=False,
                       return_uncertainties=True)
        coeffs, siga = spirouMath.fitgaussian(slln, sdata, **fkwargs)
        # copy the gaussian fit coefficients into params
        params[0] = coeffs[1]
        params[1] = coeffs[2]
        params[2] = coeffs[0]
        params[3] = siga[1]

        # test for NaNs
        if np.sum(~np.isfinite(params)) != 0:
            params[1] = 1
            params[2] = 0
            params[3] = 0
    # if coefficient is positive
    else:
        params[0] = 0
        params[1] = 1
        params[2] = 0
        params[3] = 0

    # TODO: -------------------------------------------------
    # QUESTION: GOT TO THIS POINT
    # TODO: -------------------------------------------------

    return gparams

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
                WLOG('error', p['log_opt'], [emsg1, emsg2])
            else:
                lamp_type = lamp
    # check that lamp is defined
    if lamp_type is None:
        emsg1 = 'Lamp type for file={0} cannot be identified.'.format(filename)
        emsg2 = ('    Must be one of the following: {0}'
                 ''.format(', '.join(p['IC_LAMPS'])))
        emsg3 = '    function={0}'.format(func_name)
        WLOG('error', p['log_opt'], [emsg1, emsg2, emsg3])
    # finally return lamp type
    return lamp_type


# =============================================================================
# End of code
# =============================================================================
