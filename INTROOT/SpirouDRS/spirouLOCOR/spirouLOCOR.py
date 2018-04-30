#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou localization module

Created on 2017-10-25 at 11:31

@author: cook

"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage


# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouLOCOR.py'
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
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def fiber_params(pp, fiber, merge=False):
    """
    Takes the parameters defined in FIBER_PARAMS from parameter dictionary
    (i.e. from config files) and adds the correct parameter to a fiber
    parameter dictionary

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param fiber: string, the fiber type (and suffix used in confiruation file)
                  i.e. for fiber AB fiber="AB" and nbfib_AB should be present
                  in config if "nbfib" is in FIBER_PARAMS
    :param merge: bool, if True merges with pp and returns

    :return fparam: dictionary, the fiber parameter dictionary (if merge False)
    :treun pp: dictionary, paramter dictionary (if merge True)
    """
    # get dictionary parameters for suffix _fpall
    try:
        fparams = spirouConfig.ExtractDictParams(pp, '_fpall', fiber,
                                                 merge=merge)
    except ConfigError as e:
        WLOG(e.level, pp['log_opt'], e.msg)
        fparams = ParamDict()
    # return fiber dictionary
    return fparams


def get_loc_coefficients(p, hdr=None, loc=None):
    """
    Extracts loco coefficients from parameters keys (uses header="hdr" provided
    to get acquisition time or uses p['fitsfilename'] to get acquisition time if
    "hdr" is None

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                kw_LOCO_NBO: list, keyword store for the number of orders
                             located
                kw_LOCO_DEG_C: list, keyword store for the fit degree for
                               order centers
                kw_LOCO_DEG_W: list, keyword store for the fit degree for
                               order widths
                kw_LOCO_CTR_COEFF: list, keyword store for the Coeff center
                                   order
                kw_LOCO_FWHM_COEFF: list, keyword store for the Coeff width
                                    order
                LOC_FILE: string, the suffix for the location calibration
                          database key (usually the fiber type)
                             - read from "loc_file_fpall", if not defined
                               uses p["fiber"]
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                calibDB: dictionary, the calibration database dictionary
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['arg_night_name'])
                log_opt: string, log option, normally the program name

    :param hdr: dictionary, header file from FITS rec (opened by spirouFITS)
    :param loc: parameter dictionary, ParamDict containing data

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                number_orders: int, the number of orders in reference spectrum
                nbcoeff_ctr: int, number of coefficients for the center fit
                nbcoeff_wid: int, number of coefficients for the width fit
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
    """
    # get keywords
    loco_nbo = p['kw_LOCO_NBO'][0]
    loco_deg_c, loco_deg_w = p['kw_LOCO_DEG_C'][0], p['kw_LOCO_DEG_W'][0]
    loco_ctr_coeff = p['kw_LOCO_CTR_COEFF'][0]
    loco_fwhm_coeff = p['kw_LOCO_FWHM_COEFF'][0]

    # get loc file
    if 'LOC_FILE' in p:
        loc_file = 'LOC_' + p['LOC_FILE']
    else:
        loc_file = 'LOC_' + p['fiber']

    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = spirouCDB.GetAcqTime(p, hdr)
        # get calibDB
        c_database, p = spirouCDB.GetDatabase(p, acqtime)
    else:
        c_database = p['calibDB']
        acqtime = p['MAX_TIME_HUMAN']

    # get the reduced dir name
    reduced_dir = p['reduced_dir']

    # set up the loc param dict
    if loc is None:
        loc = ParamDict()

    # check for localization file for this fiber
    if not (loc_file in c_database):
        emsg1 = ('No order geometry defined in the calibDB for fiber: {0}'
                 '').format(p['fiber'])
        emsg2 = ('    requires key="{0}" in calibDB file (with time < {1}).'
                 '').format(loc_file, acqtime)
        emsg3 = '    Unable to complete the recipe, FATAL'
        WLOG('error', p['log_opt'], [emsg1, emsg2, emsg3])
    # else log that we are reading localization parameters
    wmsg = 'Reading localization parameters of Fiber {0}'
    WLOG('', p['log_opt'], wmsg.format(p['fiber']))
    # construct the localization file name
    loco_file = os.path.join(reduced_dir, c_database[loc_file][1])
    # get header for loco file
    hdict = spirouImage.ReadHeader(p, loco_file)
    # Get number of orders from header
    loc['number_orders'] = spirouImage.ReadKey(p, hdict, loco_nbo)
    # Get the number of fit coefficients from header
    loc['nbcoeff_ctr'] = spirouImage.ReadKey(p, hdict, loco_deg_c) + 1
    loc['nbcoeff_wid'] = spirouImage.ReadKey(p, hdict, loco_deg_w) + 1
    # Read the coefficients from header
    #     for center fits
    loc['acc'] = spirouImage.Read2Dkey(p, hdict, loco_ctr_coeff,
                                       loc['number_orders'], loc['nbcoeff_ctr'])
    #     for width fits
    loc['ass'] = spirouImage.Read2Dkey(p, hdict, loco_fwhm_coeff,
                                       loc['number_orders'], loc['nbcoeff_wid'])
    # add some other parameters to loc
    loc['loco_ctr_coeff'] = loco_ctr_coeff
    loc['loco_fwhm_coeff'] = loco_fwhm_coeff
    loc['loco_ctr_file'] = loco_file
    loc['loco_fwhm_file'] = loco_file
    # add source
    added = ['number_orders', 'nbcoeff_ctr', 'nbcoeff_wid', 'acc', 'ass',
             'loco_ctr_coeff', 'loco_fwhm_coeff', 'loco_ctr_file',
             'loco_fwhm_file']
    loc.set_sources(added, __NAME__ + '/get_loc_coefficients()')
    # return the loc param dict
    return loc


def merge_coefficients(loc, coeffs, step):
    """
    Takes a list of coefficients "coeffs" and merges them based on "step"
    using the mean of "step" blocks

    i.e. shrinks a list of N coefficients to N/2 (if step = 2) where
         indices 0 and 1 are averaged, indices 2 and 3 are averaged etc

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                number_orders: int, the number of orders in reference spectrum

    :param coeffs: numpy array (2D), the list of coefficients
                   shape = (number of orders x number of fit parameters)

    :param step: int, the step between merges
                 i.e. total size before = "number_orders"
                      total size after = "number_orders"/step

    :return newcoeffs: numpy array (2D), the new list of coefficients
                shape = (number of orders/step x number of fit parmaeters)
    """
    # get number of orders
    nbo = loc['number_orders']
    # copy coeffs
    newcoeffs = coeffs.copy()
    # get sum of 0 to step pixels
    cosum = np.array(coeffs[0:nbo:step, :])
    for i_it in range(1, step):
        cosum = cosum + coeffs[i_it:nbo:step, :]
    # overwrite values into coeffs array
    newcoeffs[0:int(nbo/step), :] = (1/step)*cosum
    # return merged coeffients
    return newcoeffs


def find_order_centers(pp, image, loc, order_num):
    """
    Find the center pixels and widths of this order at specific points
    along this order="order_num"

    specific points are defined by steps (ic_locstepc) away from the
    central pixel (ic_cent_col)

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_LOCSTEPC: int, the column separation for fitting orders
                IC_CENT_COL: int, the column number (x-axis) of the central
                             column
                IC_EXT_WINDOW: int, extraction window size (half size)
                IC_IMAGE_GAP: int, the gap index in the selected area
                sigdet: float, the read noise of the image
                IC_LOCSEUIL: float, Normalised amplitude threshold to accept
                             pixels for background calculation
                IC_WIDTHMIN: int, minimum width of order to be accepted
                DRS_DEBUG: int, Whether to run in debug mode
                                0: no debug
                                1: basic debugging on errors
                                2: recipes specific (plots and some code runs)
                DRS_PLOT: bool, Whether to plot (True to plot)

    :param image: numpy array (2D), the image

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                ctro: numpy array (2D), storage for the center positions
                      shape = (number of orders x number of columns (x-axis)

    :param order_num: int, the current order to process

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ctro: numpy array (2D), storage for the center positions
                      shape = (number of orders x number of columns (x-axis)
                      updated the values for "order_num"
                sigo: numpy array (2D), storage for the width positions
                      shape = (number of orders x number of columns (x-axis)
                      updated the values for "order_num"
    """

    # get constants from parameter dictionary
    locstep, centralcol = pp['IC_LOCSTEPC'], pp['IC_CENT_COL']
    ext_window, image_gap = pp['IC_EXT_WINDOW'], pp['IC_IMAGE_GAP']
    sigdet, locthreshold = pp['sigdet'], pp['IC_LOCSEUIL']
    widthmin = pp['IC_WIDTHMIN']
    nm_threshold = pp['IC_NOISE_MULT_THRES']
    nx2 = image.shape[1]
    # get columns (start from the center and work outwards right side first
    # the left side) the order of these seems weird but we calculate row centers
    # from the central col (posc) to the RIGHT edge then calculate the center
    # pixel again from the "central col+locstep" pixel (first column calculated)
    # then we calculate row centers to the LEFT edge
    #   - hence the order of columns
    columns = list(range(centralcol + locstep, nx2 - locstep, locstep))
    columns += list(range(centralcol, locstep, -locstep))
    # loop around each column to get the order row center position from
    # previous central measurement.
    # For the first iteration this uses "posc" for all other iterations
    # uses the central position found at the nearest column to it
    # must also correct for conversion to int by adding 0.5
    center, width = 0, 0
    for col in columns:
        # for pixels>central pixel we need to get row center from last
        # iteration (or posc) this is to the LEFT
        if col > centralcol:
            rowcenter = int(loc['ctro'][order_num, col - locstep] + 0.5)
        # for pixels<=central pixel we need to get row center from last
        # iteration this ir to the RIGHT
        else:
            rowcenter = int(loc['ctro'][order_num, col + locstep] + 0.5)
        # need to define the extraction window edges
        rowtop, rowbottom = (rowcenter - ext_window), (rowcenter + ext_window)
        # now make sure our extraction isn't out of bounds
        if rowtop <= 0 or rowbottom >= nx2:
            break
        # make sure we are not in the image_gap
        # Question: Not sure what this is for
        if (rowtop < image_gap) and (rowbottom > image_gap):
            break
        # get the pixel values between row bottom and row top for
        # this column
        ovalues = image[rowtop:rowbottom, col]
        # only use if max - min above threshold = 100 * sigdet
        if np.max(ovalues) - np.min(ovalues) > (nm_threshold * sigdet):
            # as we are not normalised threshold needs multiplying by
            # the maximum value
            threshold = np.max(ovalues) * locthreshold
            # find the row center position and the width of the order
            # for this column
            lkwargs = dict(values=ovalues, threshold=threshold,
                           min_width=widthmin)
            center, width = locate_order_center(**lkwargs)
            # need to add on row top (as centers are relative positions)
            center = center + rowtop
            # if the width is zero set the position back to the original
            # position
            if width == 0:
                center = float(rowcenter)-1 # to force the order curvature
        # add these positions to storage
        loc['ctro'][order_num, col] = center
        loc['sigo'][order_num, col] = width
        # debug plot
        if pp['DRS_DEBUG'] == 2 and pp['DRS_PLOT']:
            dvars = [pp, order_num, col, rowcenter, rowtop, rowbottom,
                     center, width, ovalues]
            sPlt.debug_locplot_finding_orders(*dvars)
    # return the storage dictionary
    return loc


def initial_order_fit(pp, loc, mask, onum, rnum, kind, fig=None, frame=None):
    """
    Performs a crude initial fit for this order, uses the ctro positions or
    sigo width values found in "FindOrderCtrs" or "find_order_centers" to do
    the fit

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                IC_LOCDFITC: int, order of polynomial to fit for positions
                IC_LOCDFITW: int, order of polynomial to fit for widths
                DRS_PLOT: bool, Whether to plot (True to plot)
                IC_CENT_COL: int, Definition of the central column

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                x: numpy array (1D), the order numbers
                ctro: numpy array (2D), storage for the center positions
                      shape = (number of orders x number of columns (x-axis)
                sigo: numpy array (2D), storage for the width positions
                      shape = (number of orders x number of columns (x-axis)

    :param mask: numpy array (1D) of booleans, True where we have non-zero
                 widths
    :param onum: int, order iteration number (running number over all
                 iterations)
    :param rnum: int, order number (running number of successful order
                 iterations only)
    :param kind: string, 'center' or 'fwhm', if 'center' then this fit is for
                 the central positions, if 'fwhm' this fit is for the width of
                 the orders
    :param fig: plt.figure, the figure to plot initial fit on
    :param frame: matplotlib axis i.e. plt.subplot(), the axis on which to plot
                  the initial fit on (carries the plt.imshow(image))
    :return fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['x'])
                where fity = Sum(a[i] * x^i)
            res = the residuals from y - fity
                 where y = ctro [kind='center'] or
                         = sigo [kind='fwhm'])
            abs_res = abs(res)
            rms = the standard deviation of the residuals
            max_ptp = maximum residual value max(res)
            max_ptp_frac = max_ptp / rms  [kind='center']
                         = max(abs_res/y) * 100   [kind='fwhm']
    """
    # deal with kind
    if kind not in ['center', 'fwhm']:
        emsg = 'Error: sigma_clip "kind" must be either "center" or "fwhm"'
        WLOG('error', pp['log_opt'], emsg)
    # get variables that are independent of kind
    x = loc['x']
    # get variables dependent on kind
    if kind == 'center':
        # constants
        f_order = pp['IC_LOCDFITC']
        # variables
        y = loc['ctro'][onum, :][mask]
    else:
        # constants
        f_order = pp['IC_LOCDFITW']
        # variables
        y = loc['sigo'][onum, :][mask]
    # -------------------------------------------------------------------------
    # calculate fit - coefficients, fit y params, residuals, absolute residuals,
    #                 rms and max_ptp
    # -------------------------------------------------------------------------
    acoeffs, fit, res, abs_res, rms, max_ptp = calculate_fit(x, y, f_order)
    # max_ptp_frac is different for different cases
    if kind == 'center':
        max_ptp_frac = max_ptp / rms
    else:
        max_ptp_frac = np.max(abs_res/y) * 100
    # -------------------------------------------------------------------------
    # plot order on image plot (if drs_plot is true)
    if pp['DRS_PLOT'] and kind == 'center':
        if fig is not None and frame is not None:
            sPlt.locplot_order(frame, x, y, rnum)
    # -------------------------------------------------------------------------
    # Work out the fit value at ic_cent_col (for logging)
    cfitval = np.polyval(acoeffs[::-1], pp['IC_CENT_COL'])
    # -------------------------------------------------------------------------
    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac, cfitval=cfitval)
    return fitdata


def sigmaclip_order_fit(pp, loc, fitdata, mask, onum, rnum, kind):
    """
    Performs a sigma clip fit for this order, uses the ctro positions or
    sigo width values found in "FindOrderCtrs" or "find_order_centers" to do
    the fit. Removes the largest residual from the initial fit (or subsequent
    sigmaclips) value in x and y and recalculates the fit.

    Does this until all the following conditions are NOT met:
           rms > 'ic_max_rms'   [kind='center' or kind='fwhm']
        or max_ptp > 'ic_max_ptp [kind='center']
        or max_ptp_frac > 'ic_ptporms_center'   [kind='center']
        or max_ptp_frac > 'ic_max_ptp_frac'     [kind='fwhm'

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                IC_MAX_RMS_CENTER: required when kind="center", float, Maximum
                                   rms for sigma-clip order fit (center
                                   positions)
                IC_MAX_RMS_FWHM: required when kind="fwhm", float, Maximum
                                 rms for sigma-clip order fit (width)
                IC_LOCDFITC: int, order of polynomial to fit for positions
                IC_MAX_PTP_CENTER: required when kind="center", float, Maximum
                                   peak-to-peak for sigma-clip order fit
                                   (center positions)
                IC_PTPORMS_CENTER: required when kind="center", float, Maximum
                                   frac ptp/rms for sigma-clip order fit
                                   (center positions)
                IC_LOCDFITW: int, order of polynomial to fit for widths
                IC_MAX_PTP_FRAC_FWHM: required when kind="fwhm", float, Maximum
                                      fractional peak-to-peak for sigma-clip
                                      order fit (width)
                DRS_DEBUG: int, Whether to run in debug mode
                                0: no debug
                                1: basic debugging on errors
                                2: recipes specific (plots and some code runs)
                DRS_PLOT: bool, Whether to plot (True to plot)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                ctro: numpy array (2D), storage for the center positions
                      shape = (number of orders x number of columns (x-axis)
                sigo: numpy array (2D), storage for the width positions
                      shape = (number of orders x number of columns (x-axis)
                max_rmpts_pos: int, maximum number of removed points in sigma
                               clipping process, for center fits
                max_rmpts_wid: int, maximum number of removed poitns in sigma
                               clipping process, for width fits

    :param fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['x'])
                where fity = Sum(a[i] * x^i)
            res = the residuals from y - fity
                 where y = ctro [kind='center'] or
                         = sigo [kind='fwhm'])
            abs_res = abs(res)
            rms = the standard deviation of the residuals
            max_ptp = maximum residual value max(res)
            max_ptp_frac = max_ptp / rms  [kind='center']
                         = max(abs_res/y) * 100   [kind='fwhm']

    :param mask: numpy array (1D) of booleans, True where we have non-zero
                 widths
    :param onum: int, order iteration number (running number over all
                 iterations)
    :param rnum: int, order number (running number of successful order
                 iterations only)
    :param kind: string, 'center' or 'fwhm', if 'center' then this fit is for
                 the central p

    :return fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['x'])
                where fity = Sum(a[i] * x^i)
            res = the residuals from y - fity
                 where y = ctro [kind='center'] or
                         = sigo [kind='fwhm'])
            abs_res = abs(res)
            rms = the standard deviation of the residuals
            max_ptp = maximum residual value max(res)
            max_ptp_frac = max_ptp / rms  [kind='center']
                         = max(abs_res/y) * 100   [kind='fwhm']
    """
    # deal with kind
    if kind not in ['center', 'fwhm']:
        WLOG('error', pp['log_opt'], ('Error: sigma_clip "kind" must be '
                                      'either "center" or "fwhm"'))
    # extract constants from fitdata
    acoeffs = fitdata['a']
    fit = fitdata['fit']
    res = fitdata['res']
    abs_res = fitdata['abs_res']
    rms = fitdata['rms']
    max_ptp = fitdata['max_ptp']
    max_ptp_frac = fitdata['max_ptp_frac']
    # get variables that are independent of kind
    x = loc['x']
    ic_max_rms = pp['IC_MAX_RMS_{0}'.format(kind.upper())]
    # get variables dependent on kind
    if kind == 'center':
        # constants
        f_order = pp['IC_LOCDFITC']
        ic_max_ptp = pp['IC_MAX_PTP_{0}'.format(kind.upper())]
        ic_max_ptp_frac = None
        ic_ptporms_center = pp['IC_PTPORMS_CENTER']
        # variables
        y = loc['ctro'][onum, :][mask]
        max_rmpts = loc['max_rmpts_pos'][rnum]
        kind2, ptpfrackind = 'center', 'sigrms'
    else:
        # constants
        f_order = pp['IC_LOCDFITW']
        ic_max_ptp = -np.inf
        ic_max_ptp_frac = pp['IC_MAX_PTP_FRAC{0}'.format(kind.upper())]
        ic_ptporms_center = None
        # variables
        y = loc['sigo'][onum, :][mask]
        max_rmpts = loc['max_rmpts_wid'][rnum]
        kind2, ptpfrackind = 'width ', 'ptp%'
    # -------------------------------------------------------------------------
    # Need to do sigma clip fit
    # -------------------------------------------------------------------------
    # define clipping mask
    wmask = np.ones(len(abs_res), dtype=bool)
    # get condition for doing sigma clip
    cond = rms > ic_max_rms
    if kind == 'center':
        cond |= max_ptp > ic_max_ptp
        cond |= (max_ptp_frac > ic_ptporms_center)
    else:
        cond |= (max_ptp_frac > ic_max_ptp_frac)
    # keep clipping until cond is met
    xo, yo = np.array(x), np.array(y)
    while cond:
        # Log that we are clipping the fit
        wargs = [kind, ptpfrackind, rms, max_ptp, max_ptp_frac]
        WLOG('', pp['log_opt'], ('      {0} fit converging with rms/ptp/{1}:'
                                 ' {2:.3f}/{3:.3f}/{4:.3f}').format(*wargs))
        # add residuals to loc
        loc['res'] = res
        loc.set_source('res', __NAME__ + '/sigmaclip_order_fit()')
        # debug plot
        if pp['DRS_PLOT'] and pp['DRS_DEBUG'] == 2:
            sPlt.debug_locplot_fit_residual(pp, loc, rnum, kind)
        # add one to the max rmpts
        max_rmpts += 1
        # remove the largest residual (set wmask = 0 at that position)
        wmask[np.argmax(abs_res)] = False
        # get the new x and y values (without largest residual)
        xo, yo = xo[wmask], yo[wmask]
        # fit the new x and y
        fdata = calculate_fit(xo, yo, f_order)
        acoeffs, fit, res, abs_res, rms, max_ptp = fdata
        # max_ptp_frac is different for different cases
        if kind == 'center':
            max_ptp_frac = max_ptp / rms
        else:
            max_ptp_frac = np.max(abs_res / yo) * 100
        # recalculate condition for doing sigma clip
        cond = rms > ic_max_rms
        if kind == 'center':
            cond |= (max_ptp > ic_max_ptp)
            cond |= (max_ptp_frac > ic_ptporms_center)
        else:
            cond |= (max_ptp_frac > ic_max_ptp_frac)
        # reform wmask
        wmask = wmask[wmask]
    else:
        wargs = [kind2, ptpfrackind, rms, max_ptp, max_ptp_frac, int(max_rmpts)]
        WLOG('', pp['log_opt'], (' - {0} fit rms/ptp/{1}: {2:.3f}/{3:.3f}/'
                                 '{4:.3f} with {5} rejected points'
                                 '').format(*wargs))
    # if max_rmpts > 50:
    #     stats = ('\n\tacoeffs={0}, \n\tfit={1}, \n\tres={2}, '
    #              '\t\tabs_res={3}, \n\trms={4}, \n\tmax_pt={5}'
    #              ''.format(acoeffs, fit, res, abs_res, rms, max_ptp))
    #     print('{0} fit did not converge stats: {1}'.format(kind, stats))
    #     sys.exit()
    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac,
                   max_rmpts=max_rmpts)
    return fitdata


def calculate_fit(x, y, f):
    """
    Calculate the polynomial fit between x and y, for "f" fit parameters,
    also calculate the residuals, absolute residuals, RMS and max peak-to-peak
    values

    :param x: numpy array (1D), the x values to use for the fit
    :param y: numpy array (1D), the y values to fit
    :param f: int, the number of fit parameters (i.e. for quadratic fit f=2)

    :return a: numpy array (1D), the fit coefficients
                        shape = f
    :return fit: numpy array (1D), the fit values for positions in x
                        shape = len(y) and len(x)
    :return res: numpy array (1D), the residuals between y and fit
                        shape = len(y) and len(x)
    :return abs_res: numpy array (1D), the absolute values of "res"  abs(res)
                        shape = len(y) and len(x)
    :return rms: float, the RMS (root-mean square) of the residuals (std)
    :return max_ptp: float, the max peak to peak value of the absolute
                     residuals i.e. max(abs_res)
    """
    # Do initial fit (revere due to fortran compatibility)
    a = np.polyfit(x, y, deg=f)[::-1]
    # Get the intial fit data
    fit = np.polyval(a[::-1], x)
    # work out residuals
    res = y - fit
    # Work out absolute residuals
    abs_res = abs(res)
    # work out rms
    rms = np.std(res)
    # work out max point to point of residuals
    max_ptp = np.max(abs_res)
    # return all
    return a, fit, res, abs_res, rms, max_ptp


def calculate_location_fits(coeffs, dim):
    """
    Calculates all fits in coeffs array across pixels of size=dim

    :param coeffs: coefficient array,
                   size = (number of orders x number of coefficients in fit)
                   output array will be size = (number of orders x dim)
    :param dim: int, number of pixels to calculate fit for
                fit will be done over x = 0 to dim in steps of 1
    :return yfits: array,
                   size = (number of orders x dim)
                   the fit for each order at each pixel values from 0 to dim
    """
    # create storage array
    yfits = np.zeros((len(coeffs), dim))
    # get pixel range for dimension
    xfit = np.arange(0, dim, 1)
    # loop around each fit and fit
    for j_it in range(len(coeffs)):
        yfits[j_it] = np.polyval(coeffs[j_it][::-1], xfit)
    # return fits
    return yfits


# TODO: after H2RG tests over can remove method (keep "new" method)
def smoothed_boxmean_image(image, size, weighted=True, mode='convolve',
                           method='new'):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels.

        if mode='convolve' (default) then this is done
        by convolving a top-hat function with the image (FAST)
        - note produces small inconsistencies due to FT of top-hat function

        if mode='manual' then this is done by working out the mean in each
        box manually (SLOW)

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param weighted: bool, if True pixel values less than zero are weighted to
                     a value of 1e-6 and values above 0 are weighted to a value
                     of 1
    :param mode: string, if 'convolve' convoles with a top-hat function of the
                         size "box" for each column (FAST) - note produces small
                         inconsistencies due to FT of top-hat function

                         if 'manual' calculates every box individually (SLOW)
    :param method: string, if 'new' uses a median, if 'old' uses average

    :return newimage: numpy array (2D), the smoothed image
    """
    if mode == 'convolve':
        return smoothed_boxmean_image2(image, size, weighted=weighted)
    if mode == 'manual':
        return smoothed_boxmean_image1(image, size, weighted=weighted,
                                       method=method)
    else:
        emsg = 'mode keyword={0} not valid. Must be "convolve" or "manual"'
        raise KeyError(emsg.format(mode))


# TODO: after H2RG tests over can remove method (keep "new" method)
def smoothed_boxmean_image1(image, size, weighted=True, method='new'):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param weighted: bool, if True pixel values less than zero are weighted to
                     a value of 1e-6 and values above 0 are weighted to a value
                     of 1
    :param method: string, if 'new' uses a median, if 'old' uses average

    :return newimage: numpy array (2D), the smoothed image

    For 1 loop, best of 3: 628 ms per loop
    """
    newimage = np.zeros_like(image)

    # loop around each pixel column
    for it in range(0, image.shape[1], 1):
        # deal with leading edge --> i.e. box expands until it is full size
        if it < size:
            # get the subimage defined by the box for all rows
            part = image[:, 0:it + size + 1]
        # deal with main part (where box is of size="size"
        elif size <= it <= image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size: it + size + 1]
        # deal with the trailing edge --> i.e. box shrinks from full size
        elif it > image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size: it + size + 1]
        # get the weights (pixels below 0 are set to 1e-6, pixels above to 1)
        if weighted:
            weights = np.where(part > 0, 1, 1.e-6)
        else:
            weights = np.ones(len(part))
        # apply the weighted mean for this column
        if method == 'old':
            newimage[:, it] = np.average(part, axis=1, weights=weights)
        else:
            newimage[:, it] = np.median(part, axis=1)
    # return the new smoothed image
    return newimage


def smoothed_boxmean_image2(image, size, weighted=True):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param weighted: bool, if True pixel values less than zero are weighted to
                     a value of 1e-6 and values above 0 are weighted to a value
                     of 1

    :return newimage: numpy array (2D), the smoothed image

    For 10 loops, best of 3: 94.7 ms per loop
    """
    # define a box to smooth by
    box = np.ones(size)
    # defined the weights for each pixel
    if weighted:
        weights = np.where(image > 0, 1.0, 1.e-6)
    else:
        weights = np.ones_like(image)
    # new weighted image
    weightedimage = image * weights

    # need to work on each row separately
    newimage = np.zeros_like(image)
    for row in range(image.shape[0]):
        # work out the weighted image
        s_weighted_image = np.convolve(weightedimage[row], box, mode='same')
        s_weights = np.convolve(weights[row], box, mode='same')
        # apply the weighted mean for this column
        newimage[row] = s_weighted_image/s_weights
    # return new image
    return newimage


# TODO: remove later
def __test_smoothed_boxmean_image(image, size, row=1000, column=1000):
    # get the new images
    image1 = smoothed_boxmean_image1(image, size)
    image2 = smoothed_boxmean_image2(image, size)

    # plot graph in sPlt
    sPlt.__test_smoothed_boxmean_image(image, image1, image2, size,
                                       row=row, column=column)


def image_localization_superposition(image, coeffs):
    """
    Take an image and superimpose zeros over the positions in the image where
    the central fits where found to be

    :param image: numpy array (2D), the image
    :param coeffs: coefficient array,
                   size = (number of orders x number of coefficients in fit)
                   output array will be size = (number of orders x dim)
    :return newimage: numpy array (2D), the image with super-imposed zero filled
                      fits
    """
    # copy the old image
    newimage = image.copy()
    # get the number of orders
    n_orders = len(coeffs)
    # get the pixel positions along the order
    xdata = np.arange(image.shape[1])
    # loop around each order
    fitxarray, fityarray = [], []
    for order_num in range(n_orders):
        # get the pixel positions across the order (from fit coeffs in position)
        # add 0.5 to account for later conversion to int
        fity = np.polyval(coeffs[order_num][::-1], xdata) + 0.5
        # elements must be > 0 and less than image.shape[0]
        mask = (fity > 0) & (fity < image.shape[0])
        # Add good values to storage array
        fityarray = np.append(fityarray, fity[mask])
        fitxarray = np.append(fitxarray, xdata[mask])

    # convert fitxarray and fityarra to integers
    fitxarray = np.array(fitxarray, dtype=int)
    fityarray = np.array(fityarray, dtype=int)
    # use fitxarray and fityarray as positions to set 0 in newimage
    newimage[fityarray, fitxarray] = 0
    # return newimage
    return newimage


# def locate_center_order_positions(cvalues, threshold, mode='convolve',
#                                   min_width=None):
#     """
#     Takes the central pixel values and finds orders by looking for the start
#     and end of orders above threshold
#
#         if mode='convolve' (default) then this is done
#         by convolving a top-hat function with a mask of
#         cvalues>threshold (FAST)
#
#         if mode='manual' then this is done by working out the star and end
#         positions manually (SLOW)
#
#     :param cvalues: numpy array (1D) size = number of rows,
#                     the central pixel values
#     :param threshold: float, the threshold above which to find pixels as being
#                       part of an order
#     :param mode: string, if 'convolve' convolves a top-hat function with
#                          a mask of cvalues>threshold (FAST)
#
#                          if 'manual' manually counts every start
#                          and end (SLOW)
#
#     :param min_width: int or None, if not None sets a minimum width
#                       requirement for the size of the order
#
#     :return positions: numpy array (1D), size=len(cvalues),
#                        the pixel positions in cvalues where the centers of
#                        each order should be
#
#     :return widths: numpy array (1D), size=len(cvalues), the widths of each
#                     order
#     """
#     if mode == 'convolve':
#         return locate_order_positions2(cvalues, threshold, min_width)
#     if mode == 'manual':
#         return locate_order_positions1(cvalues, threshold, min_width)
#     else:
#         emsg = 'mode keyword={0} not valid. Must be "convolve" or "manual"'
#         raise KeyError(emsg.format(mode))


def find_position_of_cent_col(values, threshold):
    """
    Finds the central positions based on the central column values

    :param values: numpy array (1D) size = number of rows,
                    the central column values
    :param threshold: float, the threshold above which to find pixels as being
                      part of an order

    :return position: numpy array (1D), size= number of rows,
                      the pixel positions in cvalues where the centers of each
                      order should be

    For 1000 loops, best of 3: 771 µs per loop
    """
    # store the positions of the orders
    positions = []
    # get the len of cvalues
    length = len(values)
    # initialise the row number to zero
    row, order_end = 0, 0
    # move the row number to the first row below threshold
    # (avoids first order on the edge)
    while values[row] > threshold:
        row += 1
        if row == length:
            break
    # continue to move through rows
    while row < length:
        # if row is above threshold then we have found a start point
        if values[row] > threshold:
            # save the start point
            order_start = row
            # continue to move through rows to find end (end of order defined
            # as the point at which it slips below the threshold)
            while values[row] >= threshold:
                row += 1
                # if we have reached the end of cvalues stop (it is an end of
                # an order by definition
                if row == length:
                    break
            # as we have reached the end we should not add to positions
            if row == length:
                break
            else:
                # else record the end position
                order_end = row
                # determine the center of gravity of the order
                # lx is the pixels in this order
                lx = np.arange(order_start, order_end, 1)
                # ly is the cvalues values in this order (use lx to get them)
                ly = values[lx]
                # position = sum of (lx * ly) / sum of sum(ly)
                position = np.sum(lx * ly * 1.0) / np.sum(ly)
                # append position and width to storage
                positions.append(position)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return np.array(positions)


def locate_order_center(values, threshold, min_width=None):
    """
    Takes the values across the oder and finds the order center by looking for
    the start and end of the order (and thus the center) above threshold

    :param values: numpy array (1D) size = number of rows, the pixels in an
                    order

    :param threshold: float, the threshold above which to find pixels as being
                      part of an order

    :param min_width: float, the minimum width for an order to be accepted

    :return positions: numpy array (1D), size= number of rows,
                       the pixel positions in cvalues where the centers of each
                       order should be

    :return widths:    numpy array (1D), size= number of rows,
                       the pixel positions in cvalues where the centers of each
                       order should be

    For 1000 loops, best of 3: 771 µs per loop
    """
    # deal with no min_width
    if min_width is None:
        min_width = 0
    # get the len of cvalues
    length = len(values)
    # initialise the row number to zero
    row, order_end = 0, 0
    position, width = 0, 0
    # move the row number to the first row below threshold
    # (avoids first order on the edge)
    while values[row] > threshold:
        row += 1
        if row == length:
            break
    # continue to move through rows
    while row < length and (order_end == 0):
        # if row is above threshold then we have found a start point
        if values[row] > threshold:
            # save the start point
            order_start = row
            # continue to move through rows to find end (end of order defined
            # as the point at which it slips below the threshold)
            while values[row] >= threshold:
                row += 1
                # if we have reached the end of cvalues stop (it is an end of
                # an order by definition
                if row == length:
                    break
            # as we have reached the end we should not add to positions
            if row == length:
                break
            elif (row - order_start) > min_width:
                # else record the end position
                order_end = row
                # determine the center of gravity of the order
                # lx is the pixels in this order
                lx = np.arange(order_start, order_end, 1)
                # ly is the cvalues values in this order (use lx to get them)
                ly = values[lx]
                # position = sum of (lx * ly) / sum of sum(ly)
                position = np.sum(lx * ly * 1.0) / np.sum(ly)
                # width is just the distance from start to end
                width = abs(order_end - order_start)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return position, width


# def locate_order_positions2(cvalues, threshold, min_width=None):
#     """
#     Test version
#
#     Takes the central pixel values and finds orders by looking for the start
#     and end of orders above threshold
#
#     :param cvalues: numpy array (1D) size = number of rows,
#                     the central pixel values
#     :param threshold: float, the threshold above which to find pixels as being
#                       part of an order
#     :param min_width: int or None, if not None sets a minimum width
#                       requirement for the size of the order
#
#     :return positions: numpy array (1D), size=len(cvalues),
#                        the pixel positions in cvalues where the centers of
#                        each  order should be
#
#     :return widths: numpy array (1D), size=len(cvalues), the widths of each
#                     order
#
#     For 1000 loops, best of 3: 401 µs per loop
#     """
#     # deal with no min_width
#     if min_width is None:
#         min_width = 0
#     # define a mask of cvalues < threshold
#     mask = np.array(cvalues) > threshold
#     # if there is an order on the leading edge set ignore it (set to False)
#     row = 0
#     while mask[row]:
#         mask[row] = False
#         row += 1
#     # define a box (of width 3) to smooth the mask
#     box = np.ones(3)
#     # convole box with mask
#     smoothmask = np.convolve(mask, box, mode='same')
#     # now where the array was [True, True, True] gives a value of 3 at the
#     #     center
#     # now where the array was [True, True, False] or [False, True, True] or
#     #     [True, False, True] gives a value of 2 at the center
#     # now where the array was [False, False, True] or [True, True, False] or
#     #     [False, True, False] gives a value of 1
#     # now where the array was [False, False, False] gives a value of 0
#     # --> we want the positions where the value==2
#     raw_positions = np.where(smoothmask == 2)[0]
#     # starts are the even positions
#     ostarts = raw_positions[::2]
#     # ends are the odd positions
#     oends = raw_positions[1::2]
#     # then loop around to calculate true positions
#     positions, widths = [], []
#     for start, end in zip(ostarts, oends):
#         if (end - start) > min_width:
#             # get x values and y values for order
#             # add one to end to get full pixel range
#             lx = np.arange(start, end + 1)
#             ly = cvalues[lx]
#             # position = sum of (lx * ly) / sum of sum(ly)
#             positions.append(np.sum(lx * ly) / np.sum(ly))
#             # width = end - start, add one to end to get full pixel range
#             widths.append(abs((end + 1 ) - start))
#     # return positions
#     return np.array(positions), np.array(widths)

# =============================================================================
# End of code
# =============================================================================
