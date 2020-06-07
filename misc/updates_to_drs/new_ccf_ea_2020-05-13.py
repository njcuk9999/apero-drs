#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE
# CODE DESCRIPTION HERE
Created on 2020-03-27 at 13:42
@author: cook
"""
from astropy.io import fits
from astropy.table import Table
from astropy import units as uu
import numpy as np
import warnings
import sys
import os
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.optimize import curve_fit
from scipy.stats import chisquare
import matplotlib.pyplot as plt
from scipy.signal import convolve
import glob
from fits2wave import *

MASK_COLS = ['ll_mask_s', 'll_mask_e', 'w_mask']

# variables
# These values are taken from the constants file
MASK_WIDTH = 1.7  # CCF_MASK_WIDTH
# MASK_MIN_WEIGHT = 0.0  # CCF_MASK_MIN_WEIGHT

# should be smaller than ~0.25
CCF_STEP = 0.1  # CCF_DEFAULT_STEP (or user input)
CCF_WIDTH = 50  # CCF_DEFAULT_WIDTH (or user input)
CCF_RV_NULL = 1000  # CCF_OBJRV_NULL_VAL (max allowed)
IN_RV = -110  # user input [km/s]
CCF_N_ORD_MAX = 48  # CCF_N_ORD_MAX
BLAZE_NORM_PERCENTILE = 95  # CCF_BLAZE_NORM_PERCENTILE
BLAZE_THRESHOLD = 0.3  # WAVE_FP_BLAZE_THRES
IMAGE_PIXEL_SIZE = 2.28  # IMAGE_PIXEL_SIZE
NOISE_SIGDET = 8.0  # CCF_NOISE_SIGDET
NOISE_SIZE = 12  # CCF_NOISE_BOXSIZE
NOISE_THRES = 1.0e9  # CCF_NOISE_THRES
SPEED_OF_LIGHT = 299792.458  # [km/s]


# =============================================================================
# Define functions
# =============================================================================
def read_mask(MASK_FILE, MASK_COLS):
    table = Table.read(MASK_FILE, format='ascii')
    # get column names
    oldcols = list(table.colnames)
    # rename columns
    for c_it, col in enumerate(MASK_COLS):
        table[oldcols[c_it]].name = col
    # return table
    return table


def get_mask(table, mask_width, mask_units='nm'):
    ll_mask_e = np.array(table['ll_mask_e']).astype(float)
    ll_mask_s = np.array(table['ll_mask_s']).astype(float)
    ll_mask_d = ll_mask_e - ll_mask_s
    ll_mask_ctr = ll_mask_s + ll_mask_d * 0.5
    # if mask_width > 0 ll_mask_d is multiplied by mask_width/c

    # if mask_width > 0:
    #    ll_mask_d = mask_width * ll_mask_s / SPEED_OF_LIGHT
    # make w_mask an array
    w_mask = np.array(table['w_mask']).astype(float)
    # use w_min to select on w_mask or keep all if w_mask_min >= 1
    # if mask_min < 1.0:
    #    mask = w_mask > mask_min
    #    ll_mask_d = ll_mask_d[mask]
    #    ll_mask_ctr = ll_mask_ctr[mask]
    #    w_mask = w_mask[mask]
    # else set all w_mask to one (and use all lines in file)
    # else:
    #    w_mask = np.ones(len(ll_mask_d))
    # ----------------------------------------------------------------------
    # deal with the units of ll_mask_d and ll_mask_ctr
    # must be returned in nanometers
    # ----------------------------------------------------------------------
    # get unit object from mask units string
    unit = getattr(uu, mask_units)
    # add units
    ll_mask_d = ll_mask_d * unit
    ll_mask_ctr = ll_mask_ctr * unit
    # convert to nanometers
    ll_mask_d = ll_mask_d.to(uu.nm).value
    ll_mask_ctr = ll_mask_ctr.to(uu.nm).value
    # ----------------------------------------------------------------------
    # return the size of each pixel, the central point of each pixel
    #    and the weight mask
    return ll_mask_d, ll_mask_ctr, w_mask


def relativistic_waveshift(dv, units='km/s'):
    """
    Relativistic offset in wavelength
    default is dv in km/s
    :param dv: float or numpy array, the dv values
    :param units: string or astropy units, the units of dv
    :return:
    """
    # get c in correct units
    # noinspection PyUnresolvedReferences
    if units == 'km/s' or units == uu.km / uu.s:
        c = SPEED_OF_LIGHT
    # noinspection PyUnresolvedReferences
    elif units == 'm/s' or units == uu.m / uu.s:
        c = SPEED_OF_LIGHT * 1000
    else:
        raise ValueError("Wrong units for dv ({0})".format(units))
    # work out correction
    corrv = np.sqrt((1 + dv / c) / (1 - dv / c))
    # return correction
    return corrv


def iuv_spline(x, y, **kwargs):
    # check whether weights are set
    w = kwargs.get('w', None)
    # copy x and y
    x, y = np.array(x), np.array(y)
    # find all NaN values
    nanmask = ~np.isfinite(y)

    if np.sum(~nanmask) < 2:
        y = np.zeros_like(x)
    elif np.sum(nanmask) == 0:
        pass
    else:
        # replace all NaN's with linear interpolation
        badspline = InterpolatedUnivariateSpline(x[~nanmask], y[~nanmask],
                                                 k=1, ext=1)
        y[nanmask] = badspline(x[nanmask])
    # return spline
    return InterpolatedUnivariateSpline(x, y, **kwargs)


def fit_ccf(rv, ccf, fit_type):
    """
    Fit the CCF to a guassian function
    :param rv: numpy array (1D), the radial velocities for the line
    :param ccf: numpy array (1D), the CCF values for the line
    :param fit_type: int, if "0" then we have an absorption line
                          if "1" then we have an emission line
    :return result: numpy array (1D), the fit parameters in the
                    following order:
                [amplitude, center, fwhm, offset from 0 (in y-direction)]
    :return ccf_fit: numpy array (1D), the fit values, i.e. the gaussian values
                     for the fit parameters in "result"
    """
    # deal with inconsistent lengths
    if len(rv) != len(ccf):
        print('\tERROR: RV AND CCF SHAPE DO NOT MATCH')
        sys.exit()

    # deal with all nans
    if np.sum(np.isnan(ccf)) == len(ccf):
        # log warning about all NaN ccf
        print('\tWARNING: NANS in CCF')
        # return NaNs
        result = np.zeros(4) * np.nan
        ccf_fit = np.zeros_like(ccf) * np.nan
        return result, ccf_fit

    # get constants
    max_ccf, min_ccf = np.nanmax(ccf), np.nanmin(ccf)
    argmin, argmax = np.nanargmin(ccf), np.nanargmax(ccf)
    diff = max_ccf - min_ccf
    rvdiff = rv[1] - rv[0]
    # set up guess for gaussian fit
    # if fit_type == 0 then we have absorption lines
    if fit_type == 0:
        if np.nanmax(ccf) != 0:
            a = np.array([-diff / max_ccf, rv[argmin], 4 * rvdiff, 0])
        else:
            a = np.zeros(4)
    # else (fit_type == 1) then we have emission lines
    else:
        a = np.array([diff / max_ccf, rv[argmax], 4 * rvdiff, 1])
    # normalise y
    y = ccf / max_ccf - 1 + fit_type
    # x is just the RVs
    x = rv
    # uniform weights
    w = np.ones(len(ccf))
    # get gaussian fit
    nanmask = np.isfinite(y)
    y[~nanmask] = 0.0
    # fit the gaussian
    try:
        with warnings.catch_warnings(record=True) as _:
            result, fit = fitgaussian(x, y, weights=w, guess=a)
    except RuntimeError:
        result = np.repeat(np.nan, 4)
        fit = np.repeat(np.nan, len(x))

    # scale the ccf
    ccf_fit = (fit + 1 - fit_type) * max_ccf

    # return the best guess and the gaussian fit
    return result, ccf_fit


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


def fitgaussian(x, y, weights=None, guess=None, return_fit=True,
                return_uncertainties=False):
    """
    Fit a single gaussian to the data "y" at positions "x", points can be
    weighted by "weights" and an initial guess for the gaussian parameters
    :param x: numpy array (1D), the x values for the gaussian
    :param y: numpy array (1D), the y values for the gaussian
    :param weights: numpy array (1D), the weights for each y value
    :param guess: list of floats, the initial guess for the guassian fit
                  parameters in the following order:
                  [amplitude, center, fwhm, offset from 0 (in y-direction)]
    :param return_fit: bool, if True also calculates the fit values for x
                       i.e. yfit = gauss_function(x, *pfit)
    :param return_uncertainties: bool, if True also calculates the uncertainties
                                 based on the covariance matrix (pcov)
                                 uncertainties = np.sqrt(np.diag(pcov))
    :return pfit: numpy array (1D), the fit parameters in the
                  following order:
                [amplitude, center, fwhm, offset from 0 (in y-direction)]
    :return yfit: numpy array (1D), the fit y values, i.e. the gaussian values
                  for the fit parameters, only returned if return_fit = True
    """

    # if we don't have weights set them to be all equally weighted
    if weights is None:
        weights = np.ones(len(x))
    weights = 1.0 / weights
    # if we aren't provided a guess, make one
    if guess is None:
        guess = [np.nanmax(y), np.nanmean(y), np.nanstd(y), 0]
    # calculate the fit using curve_fit to the function "gauss_function"
    with warnings.catch_warnings(record=True) as _:
        pfit, pcov = curve_fit(gauss_function, x, y, p0=guess, sigma=weights,
                               absolute_sigma=True)
    if return_fit and return_uncertainties:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # work out the normalisation constant
        chis, _ = chisquare(y, f_exp=yfit)
        norm = chis / (len(y) - len(guess))
        # calculate the fit uncertainties based on pcov
        efit = np.sqrt(np.diag(pcov)) * np.sqrt(norm)
        # return pfit, yfit and efit
        return pfit, yfit, efit
    # if just return fit
    elif return_fit:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # return pfit and yfit
        return pfit, yfit
    # if return uncertainties
    elif return_uncertainties:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # work out the normalisation constant
        chis, _ = chisquare(y, f_exp=yfit)
        norm = chis / (len(y) - len(guess))
        # calculate the fit uncertainties based on pcov
        efit = np.sqrt(np.diag(pcov)) * np.sqrt(norm)
        # return pfit and efit
        return pfit, efit
    # else just return the pfit
    else:
        # return pfit
        return pfit


def delta_v_rms_2d(spe, wave, sigdet, threshold, size):
    """
    Compute the photon noise uncertainty for all orders (for the 2D image)
    :param spe: numpy array (2D), the extracted spectrum
                size = (number of orders by number of columns (x-axis))
    :param wave: numpy array (2D), the wave solution for each pixel
    :param sigdet: float, the read noise (sigdet) for calculating the
                   noise array
    :param threshold: float, upper limit for pixel values, above this limit
                      pixels are regarded as saturated
    :param size: int, size (in pixels) around saturated pixels to also regard
                 as bad pixels
    :return dvrms2: numpy array (1D), the photon noise for each pixel (squared)
    :return weightedmean: float, weighted mean photon noise across all orders
    """
    # flag (saturated) fluxes above threshold as "bad pixels"
    with warnings.catch_warnings(record=True) as _:
        flag = spe < threshold
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]
    # get the wavelength normalised to the wavelength spacing
    nwave = wave[:, 1:-1] / (wave[:, 2:] - wave[:, :-2])
    # get the flux + noise array
    sxn = (spe[:, 1:-1] + sigdet ** 2)
    # get the flux difference normalised to the flux + noise
    nspe = (spe[:, 2:] - spe[:, :-2]) / sxn
    # get the mask value
    maskv = flag[:, 2:] * flag[:, 1:-1] * flag[:, :-2]
    # get the total
    tot = np.nansum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    with warnings.catch_warnings(record=True) as _:
        dvrms2 = ((SPEED_OF_LIGHT * 1000) ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(np.nansum(1.0 / dvrms2))
    # return dv rms and weighted mean
    return dvrms2, weightedmean


def fwhm(sigma=1.0):
    """
    Get the Full-width-half-maximum value from the sigma value (~2.3548)
    :param sigma: float, the sigma, default value is 1.0 (normalised gaussian)
    :return: 2 * sqrt(2 * log(2)) * sigma = 2.3548200450309493 * sigma
    """
    return 2 * np.sqrt(2 * np.log(2)) * sigma


def ccf_calculation(wave, image, blaze, targetrv, mask_centers, mask_weights,
                    berv, fit_type, kernel=None):
    # get rvmin and rvmax
    rvmin = targetrv - CCF_WIDTH
    rvmax = targetrv + CCF_WIDTH + CCF_STEP
    # get the dimensions
    nbo, nbpix = image.shape
    # create a rv ccf range
    rv_ccf = np.arange(rvmin, rvmax, CCF_STEP)
    # storage of the ccf
    ccf_all = []
    ccf_noise_all = []
    ccf_all_fit = []
    ccf_all_results = []
    ccf_lines = []
    ccf_all_snr = []
    ccf_norm_all = []

    # if we have defined 'kernel', it must be a list
    # with the first element being the type of convolution
    # and subsequent arguments being parameters. For now,
    # we have :
    #
    #  --> boxcar convolution
    # ['boxcar', width]
    #
    # kernel = [1, 1, ...., 1, 1]
    #
    # --> gaussian convolution
    #
    # ['gaussian', e-width]
    # kernel = exp( -0.5*(x/ew)**2 )
    #
    # --> super gaussian
    #
    # ['supergaussian', e-width, beta]
    #
    # kernel = exp( -0.5*(x/ew)**beta )
    #
    # Other functions could be added below
    #
    if isinstance(kernel, list):
        if kernel[0] == 'boxcar':
            # ones with a length of kernel[1]
            ker = np.ones(int(np.round(kernel[1] / CCF_STEP)))
        elif kernel[0] == 'gaussian':
            # width of the gaussian expressed in
            # steps of CCF
            ew = kernel[1] / CCF_STEP
            index = np.arange(-4 * np.ceil(ew), 4 * np.ceil(ew) + 1)
            ker = np.exp(-0.5 * (index / ew) ** 2)
        elif kernel[0] == 'supergaussian':
            # width of the gaussian expressed in
            # steps of CCF. Exponents should be
            # between 0.1 and 10.. Values above
            # 10 are (nearly) the same as a boxcar.
            if (kernel[1] < 0.1) or (kernel[1] > 10):
                raise ValueError('CCF ERROR: kernel[1] is out of range.')

            ew = kernel[1] / CCF_STEP

            index = np.arange(-4 * np.ceil(ew), 4 * np.ceil(ew) + 1)
            ker = np.exp(-0.5 * np.abs(index / ew) ** kernel[2])

        else:
            # kernel name is not known - generate error
            raise ValueError('CCF ERROR: name of kernel not accepted!')

        ker = ker / np.sum(ker)

        if len(ker) > (len(rv_ccf) - 1):
            # TODO : give a proper error
            err_msg = """
            The size of your convolution kernel is too big for your
            CCF size. Please either increase the CCF_WIDTH value or
            decrease the width of your convolution kernel. In boxcar, 
            this implies a length bigger than CCF_WIDTH/CCF_STEP, in 
            gaussian and supergaussian, this means that 
            CCF_WIDTH/CCF_STEP is >8*ew. The kernel has to run from
            -4 sigma to +4 sigma.
            """
            raise ValueError('CCF ERROR: {0}'.format(err_msg))

    # ----------------------------------------------------------------------
    # loop around the orders
    for order_num in range(nbo):
        # log the process
        print('Order {0}'.format(order_num))
        # ------------------------------------------------------------------
        # get this orders values
        wa_ord = np.array(wave[order_num])
        sp_ord = np.array(image[order_num])
        bl_ord = np.array(blaze[order_num])

        # COMMENT EA, normalization moved before the masking
        #
        # normalize per-ord blaze to its peak value
        # this gets rid of the calibration lamp SED
        bl_ord /= np.nanpercentile(bl_ord, BLAZE_NORM_PERCENTILE)
        # COMMENT EA, changing NaNs to 0 in the blaze
        bl_ord[np.isfinite(bl_ord) == 0] = 0
        # mask on the blaze
        with warnings.catch_warnings(record=True) as _:
            blazemask = bl_ord > BLAZE_THRESHOLD
        # get order mask centers and mask weights
        min_ord_wav = np.nanmin(wa_ord[blazemask])
        max_ord_wav = np.nanmax(wa_ord[blazemask])
        # COMMENT EA there's a problem with the sign in the min/max

        # print(order_num, min_ord_wav, max_ord_wav, min_ord_wav * (1 - rvmin / SPEED_OF_LIGHT), max_ord_wav * (1 - rvmax / SPEED_OF_LIGHT), rvmin, rvmax)
        # min_ord_wav = min_ord_wav * (1 - rvmin / SPEED_OF_LIGHT)
        # max_ord_wav = max_ord_wav * (1 - rvmax / SPEED_OF_LIGHT)

        # mask the ccf mask by the order length
        mask_wave_mask = (mask_centers > min_ord_wav)
        mask_wave_mask &= (mask_centers < max_ord_wav)
        omask_centers = mask_centers[mask_wave_mask]
        omask_weights = mask_weights[mask_wave_mask]

        # ------------------------------------------------------------------
        # find any places in spectrum or blaze where pixel is NaN
        nanmask = np.isnan(sp_ord) | np.isnan(bl_ord)
        # ------------------------------------------------------------------
        # deal with no valid lines
        if np.sum(mask_wave_mask) == 0:
            print('\tWARNING: MASK INVALID FOR WAVELENGTH RANGE --> NAN')
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # deal with all nan
        if np.sum(nanmask) == nbpix:
            print('\tWARNING: ALL SP OR BLZ NAN --> NAN')
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # set the spectrum or blaze NaN pixels to zero (dealt with by divide)
        sp_ord[nanmask] = 0
        bl_ord[nanmask] = 0
        # now every value that is zero is masked (we don't want to spline these)
        good = (sp_ord != 0) & (bl_ord != 0)
        # ------------------------------------------------------------------
        # spline the spectrum and the blaze
        spline_sp = iuv_spline(wa_ord[good], sp_ord[good], k=5, ext=1)
        spline_bl = iuv_spline(wa_ord[good], bl_ord[good], k=5, ext=1)

        # ------------------------------------------------------------------
        # set up the ccf for this order
        ccf_ord = np.zeros_like(rv_ccf)
        # ------------------------------------------------------------------
        # get the wavelength shift (dv) in relativistic way
        wave_shifts = relativistic_waveshift(rv_ccf - berv)
        # ------------------------------------------------------------------

        # if order_num == 35:
        #    print()
        #    stop

        wave_tmp_start = omask_centers * wave_shifts[0]
        wave_tmp_end = omask_centers * wave_shifts[-1]
        valid_lines_start = spline_bl(wave_tmp_start) != 0
        valid_lines_end = spline_bl(wave_tmp_end) != 0

        keep = valid_lines_start * valid_lines_end
        omask_centers = omask_centers[keep]
        omask_weights = omask_weights[keep]

        # set number of valid lines used to zero
        numlines = 0
        # loop around the rvs and calculate the CCF at this point
        part3 = spline_bl(omask_centers)

        # if order_num == 42:
        #    print(order_num, min_ord_wav, max_ord_wav)
        #
        #    plt.plot(wa_ord, sp_ord/np.nanmedian(sp_ord))
        #    plt.plot(wa_ord, bl_ord/np.nanmedian(bl_ord))
        #    plt.plot(omask_centers, part3/np.nanmedian(part3),'go')
        #    plt.show()

        # we added the mask weights
        omask_weights /= np.nanmean(omask_weights)
        for rv_element in range(len(rv_ccf)):
            wave_tmp = omask_centers * wave_shifts[rv_element]
            part1 = spline_sp(wave_tmp)
            part2 = spline_bl(wave_tmp)

            valid_lines = spline_bl(wave_tmp) != 0
            numlines = np.sum(valid_lines)
            # if order_num ==42:
            #    print(numlines,len(valid_lines), rv_element)
            # CCF is the division of the sums
            with warnings.catch_warnings(record=True) as _:
                ccf_element = ((part1 * part3) / part2)
                ccf_ord[rv_element] = np.nansum(ccf_element[valid_lines] * omask_weights[
                    valid_lines])  # /np.nansum(omask_weights[valid_lines]*part3[valid_lines])
        # ------------------------------------------------------------------
        # deal with NaNs in ccf
        if np.sum(np.isnan(ccf_ord)) > 0:
            # log all NaN
            print('WARNING: CCF is NAN')
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # Convolve by the appropriate CCF kernel, if any
        if type(kernel) == list:
            weight = np.convolve(np.ones(len(ccf_ord)), ker, mode='same')
            ccf_ord = np.convolve(ccf_ord, ker, mode='same') / weight
        # ------------------------------------------------------------------
        # normalise each orders CCF to median
        ccf_norm = np.nanmedian(ccf_ord)
        # ccf_ord = ccf_ord / ccf_norm
        # ------------------------------------------------------------------
        # fit the CCF with a gaussian
        fargs = [rv_ccf, ccf_ord, fit_type]
        ccf_coeffs_ord, ccf_fit_ord = fit_ccf(*fargs)
        # ------------------------------------------------------------------
        # calculate the residuals of the ccf fit
        res = ccf_ord - ccf_fit_ord
        # calculate the CCF noise per order
        ccf_noise = np.array(res)
        # calculate the snr for this order
        ccf_snr = np.abs(ccf_coeffs_ord[0] / np.nanmedian(np.abs(ccf_noise)))
        # ------------------------------------------------------------------
        # append ccf to storage
        ccf_all.append(ccf_ord)
        ccf_all_fit.append(ccf_fit_ord)
        ccf_all_results.append(ccf_coeffs_ord)
        ccf_noise_all.append(ccf_noise)
        ccf_lines.append(numlines)
        ccf_all_snr.append(ccf_snr)
        ccf_norm_all.append(ccf_norm)
    # store outputs in param dict
    props = dict()
    props['RV_CCF'] = rv_ccf
    props['CCF'] = np.array(ccf_all)
    props['CCF_LINES'] = np.array(ccf_lines)
    props['TOT_LINE'] = np.sum(ccf_lines)
    props['CCF_NOISE'] = np.array(ccf_noise_all)
    props['CCF_SNR'] = np.array(ccf_all_snr)
    props['CCF_FIT'] = np.array(ccf_all_fit)
    props['CCF_FIT_COEFFS'] = np.array(ccf_all_results)
    props['CCF_NORM'] = np.array(ccf_norm_all)

    # Return properties
    return props


def mean_ccf(props, targetrv, fit_type, ):
    # get the average ccf
    mean_ccf = np.nanmean(props['CCF'][: CCF_N_ORD_MAX], axis=0)
    # get the fit for the normalized average ccf
    mean_ccf_coeffs, mean_ccf_fit = fit_ccf(props['RV_CCF'],
                                            mean_ccf, fit_type=fit_type)
    # get the RV value from the normalised average ccf fit center location
    ccf_rv = float(mean_ccf_coeffs[1])
    # get the contrast (ccf fit amplitude)
    ccf_contrast = np.abs(100 * mean_ccf_coeffs[0])
    # get the FWHM value
    ccf_fwhm = mean_ccf_coeffs[2] * fwhm()
    # --------------------------------------------------------------------------
    #  CCF_NOISE uncertainty
    ccf_noise_tot = np.sqrt(np.nanmean(props['CCF_NOISE'] ** 2, axis=0))
    # Calculate the slope of the CCF
    average_ccf_diff = (mean_ccf[2:] - mean_ccf[:-2])
    rv_ccf_diff = (props['RV_CCF'][2:] - props['RV_CCF'][:-2])
    ccf_slope = average_ccf_diff / rv_ccf_diff
    # Calculate the CCF oversampling
    ccf_oversamp = IMAGE_PIXEL_SIZE / CCF_STEP
    # create a list of indices based on the oversample grid size
    flist = np.arange(np.round(len(ccf_slope) / ccf_oversamp))
    indexlist = np.array(flist * ccf_oversamp, dtype=int)
    # we only want the unique pixels (not oversampled)
    indexlist = np.unique(indexlist)
    # get the rv noise from the sum of pixels for those points that are
    #     not oversampled
    keep_ccf_slope = ccf_slope[indexlist]
    keep_ccf_noise = ccf_noise_tot[1:-1][indexlist]
    rv_noise = np.nansum(keep_ccf_slope ** 2 / keep_ccf_noise ** 2) ** (-0.5)
    # --------------------------------------------------------------------------
    # log the stats
    wargs = [ccf_contrast, float(mean_ccf_coeffs[1]), rv_noise, ccf_fwhm]
    print('MEAN CCF:')
    print('\tCorrelation: C={0:1f}[%] RV={1:.5f}[km/s] RV_NOISE={2:.5f}[km/s] '
          'FWHM={3:.4f}[km/s]'.format(*wargs))
    # --------------------------------------------------------------------------
    # add to output array
    props['MEAN_CCF'] = mean_ccf
    props['MEAN_RV'] = ccf_rv
    props['MEAN_CONTRAST'] = ccf_contrast
    props['MEAN_FWHM'] = ccf_fwhm
    props['MEAN_CCF_RES'] = mean_ccf_coeffs
    props['MEAN_CCF_FIT'] = mean_ccf_fit
    props['MEAN_RV_NOISE'] = rv_noise
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    return props


def plot_individual_ccf(props, nbo):
    # get the plot loop generator
    generator = plotloop(range(nbo))
    # loop around orders
    for order_num in generator:
        plt.close()
        fig, frame = plt.subplots(ncols=1, nrows=1)
        frame.plot(props['RV_CCF'], props['CCF'][order_num], color='b',
                   marker='+', ls='None', label='data')
        frame.plot(props['RV_CCF'], props['CCF_FIT'][order_num], color='r', )
        rvorder = props['CCF_FIT_COEFFS'][order_num][1]
        frame.set(title='Order {0}  RV = {1} km/s'.format(order_num, rvorder),
                  xlabel='RV [km/s]', ylabel='CCF')
        plt.show()
        plt.close()


def plot_mean_ccf(props):
    plt.close()
    fig, frame = plt.subplots(ncols=1, nrows=1)
    frame.plot(props['RV_CCF'], props['MEAN_CCF'], color='b', marker='+',
               ls='None')
    frame.plot(props['RV_CCF'], props['MEAN_CCF_FIT'], color='r')
    frame.set(title='Mean CCF   RV = {0} km/s'.format(props['MEAN_RV']),
              xlabel='RV [km/s]', ylabel='CCF')
    plt.show()
    plt.close()


def plotloop(looplist):
    # check that looplist is a valid list
    if not isinstance(looplist, list):
        # noinspection PyBroadException
        try:
            looplist = list(looplist)
        except Exception as _:
            print('PLOT ERROR: looplist must be a list')
    # define message to give to user
    message = ('Plot loop navigation: Go to \n\t [P]revious plot '
               '\n\t [N]ext plot \n\t [E]nd plotting '
               '\n\t Number from [0 to {0}]: \t')
    message = message.format(len(looplist) - 1)
    # start the iterator at zero
    it = 0
    first = True
    # loop around until we hit the length of the loop list
    while it < len(looplist):
        # deal with end of looplist
        if it == len(looplist):
            # break out of while
            break
        # if this is the first iteration do not print message
        if first:
            # yield the first iteration value
            yield looplist[it]
            # increase the iterator value
            it += 1
            first = False
        # else we need to ask to go to previous, next or end
        else:
            # get user input
            userinput = input(message)
            # try to cast into a integer
            # noinspection PyBroadException
            try:
                userinput = int(userinput)
            except Exception as _:
                userinput = str(userinput)
            # if 'p' in user input we assume they want to go to previous
            if 'P' in str(userinput).upper():
                yield looplist[it - 1]
                it -= 1
            # if 'n' in user input we assume they want to go to next
            elif 'N' in str(userinput).upper():
                yield looplist[it + 1]
                it += 1
            elif isinstance(userinput, int):
                it = userinput
                # deal with it too low
                if it < 0:
                    it = 0
                # deal with it too large
                elif it >= len(looplist):
                    it = len(looplist) - 1
                # yield the value of it
                yield looplist[it]
            # else we assume the loop is over and we want to exit
            else:
                # break out of while
                break


def write_file(props, infile, maskname, header, wheader, only_outname=False):
    # ----------------------------------------------------------------------
    # construct out file name
    inbasename = os.path.basename(infile).split('.')[0]
    maskbasename = os.path.basename(maskname).split('.')[0]
    inpath = os.path.dirname(infile)
    outfile = 'CCFTABLE_{0}_{1}.fits'.format(inbasename, maskbasename)
    outpath = os.path.join(inpath, outfile)

    if only_outname:
        return outpath

    # ----------------------------------------------------------------------
    # produce CCF table
    table1 = Table()
    table1['RV'] = props['RV_CCF']
    for order_num in range(len(props['CCF'])):
        table1['ORDER{0:02d}'.format(order_num)] = props['CCF'][order_num]
    table1['COMBINED'] = props['MEAN_CCF']
    # ----------------------------------------------------------------------
    # produce stats table
    table2 = Table()
    table2['ORDERS'] = np.arange(len(props['CCF'])).astype(int)
    table2['NLINES'] = props['CCF_LINES']
    # get the coefficients
    coeffs = props['CCF_FIT_COEFFS']
    table2['CONTRAST'] = np.abs(100 * coeffs[:, 0])
    table2['RV'] = coeffs[:, 1]
    table2['FWHM'] = coeffs[:, 2]
    table2['DC'] = coeffs[:, 3]
    table2['SNR'] = props['CCF_SNR']
    table2['NORM'] = props['CCF_NORM']

    # ----------------------------------------------------------------------
    # add to the header
    # ----------------------------------------------------------------------
    # add results from the CCF
    header['CCFMNRV'] = (props['MEAN_RV'],
                         'Mean RV calc. from the mean CCF [km/s]')
    header['CCFMCONT'] = (props['MEAN_CONTRAST'],
                          'Mean contrast (depth of fit) from mean CCF')
    header['CCFMFWHM'] = (props['MEAN_FWHM'],
                          'Mean FWHM from mean CCF')
    header['CCFMRVNS'] = (props['MEAN_RV_NOISE'],
                          'Mean RV Noise from mean CCF')
    header['CCFTLINE'] = (props['TOT_LINE'],
                          'Total no. of mask lines used in CCF')
    # ----------------------------------------------------------------------
    # add constants used to process
    header['CCFMASK'] = (props['CCF_MASK'], 'CCF mask file used')
    header['CCFSTEP'] = (props['CCF_STEP'], 'CCF step used [km/s]')
    header['CCFWIDTH'] = (props['CCF_WIDTH'], 'CCF width used [km/s]')
    header['CCFTRGRV'] = (props['TARGET_RV'],
                          'CCF central RV used in CCF [km/s]')
    header['CCFSIGDT'] = (props['CCF_SIGDET'],
                          'Read noise used in photon noise calc. in CCF')
    header['CCFBOXSZ'] = (props['CCF_BOXSIZE'],
                          'Size of bad px used in photon noise calc. in CCF')
    header['CCFMAXFX'] = (props['CCF_MAXFLUX'],
                          'Flux thres for bad px in photon noise calc. in CCF')
    header['CCFORDMX'] = (props['CCF_NMAX'],
                          'Last order used in mean for mean CCF')
    # header['CCFMSKMN'] = (props['MASK_MIN'],
    #                      'Minimum weight of lines used in the CCF mask')
    header['CCFMSKWD'] = (props['MASK_WIDTH'],
                          'Width of lines used in the CCF mask')
    header['CCFMUNIT'] = (props['MASK_UNITS'], 'Units used in CCF Mask')
    # ----------------------------------------------------------------------
    # header['RV_WAVFN'] = (os.path.basename(WAVE_FILE),
    #                      'RV wave file used')
    header['RV_WAVTM'] = (wheader['MJDMID'],
                          'RV wave file time [mjd]')
    header['RV_WAVTD'] = (header['MJDMID'] - wheader['MJDMID'],
                          'RV timediff [days] btwn file and wave solution')
    header['RV_WAVFP'] = ('None', 'RV measured from wave sol FP CCF [km/s]')
    header['RV_SIMFP'] = ('None', 'RV measured from simultaneous FP CCF [km/s]')
    header['RV_DRIFT'] = ('None',
                          'RV drift between wave sol and sim. FP CCF [km/s]')
    header['RV_OBJ'] = (props['MEAN_RV'],
                        'RV calc in the object CCF (non corr.) [km/s]')
    header['RV_CORR'] = ('None', 'RV corrected for FP CCF drift [km/s]')
    # ----------------------------------------------------------------------
    # log where we are writing the file to
    print('Writing file to {0}'.format(outpath))
    # construct hdus
    hdu = fits.PrimaryHDU()
    t1 = fits.BinTableHDU(table1, header=header)
    t2 = fits.BinTableHDU(table2, header=header)
    # construct hdu list
    hdulist = fits.HDUList([hdu, t1, t2])
    # write hdulist
    hdulist.writeto(outpath, overwrite=True)

    return outpath


def get_ccf(IN_FILES, MASK_FILE='Gl699_neg.mas',
            BLAZE_FILE='workplace1/2019-04-20_2400404f_pp_blaze_AB.fits', KERNEL=None
            ):
    helpstr = """
    ----------------------------------------------------------------------------
    new_ccf_code.py 
    ----------------------------------------------------------------------------
    This code takes no arguments - you must edit the "variables section"  of the
    code
    1. Finding the correct calibrations
        a) For your observation find the date
        b) Go to your /calibDB/ directory
        c) find the correct file (closest in time?):
            BLAZE:  *blaze_{fiber}.fits
            WAVE:   *wave_night_{fiber}.fits
    2. Finding masks
        a) go to your apero-drs installation directory
        b) go to data/spirou/ccf sub-directory
        c) use one of these masks
    3. Two options for where you put files
        a) copy all data to a directory of your choice ({path})
            i) copy this code there and set W1='' and W2=''
            ii) or set W1={path} and W2={path}
        b) set the paths for your data (W1) and your mask directory (W2)
        Then update the filenames:
            IN_FILES: the e2dsff_C or e2dsff_tcorr _AB file. Can include
                      wildcards to process multiple files at once. These files
                      must share the same BLAZE_FILE, WAVE_FIlE and all options.

            BLAZE_FILE: the blaze file from calibDB - get the fiber correct!
            WAVE_FILE: the wave file from calibDB - get the fiber correct!
            MASK_FILE: the mask file
        Note there are two cases (set CASE=1 or CASE=2)
        For case=1 we assume your IN_FILE is a OBJ
        For case=2 we assume your IN_FILe is a FP
    Adding a convolution kernel. You can pass a kernel argument that 
    describes the convolution of the LSF. 'None' produces a Dirac comb
    while 3 others are described below.
        --> boxcar convolution
        ['boxcar', width]
        kernel = [1, 1, ...., 1, 1]
        --> gaussian convolution
        ['gaussian', e-width]
        kernel = exp( -0.5*(x/ew)**2 )
        --> super gaussian
        ['supergaussian', e-width, beta]
        kernel = exp( -0.5*(x/ew)**beta )
        Other functions could be added 
    ----------------------------------------------------------------------------
    """

    # =============================================================================
    # Define variables
    # =============================================================================
    # constants
    # if all files copied to same directory set these to ''
    # W1 = ''
    # W2 = ''
    # these files are on cook@nb19
    # W1 = 'workplace1'
    # W2 = 'workplace2'
    # whether to plot (True or False)
    PLOT = False
    # which case 1: science (OBJ) 2: reference (FP)
    CASE = 1

    # Pick you CCF convolution kernel. See explanantions below in the
    # CCF function. Uncomment the kernel type you want and change the
    # parameter.

    # CCF is a set of Dirac functions
    # KERNEL = None
    # boxcar length expressed in km/s
    # KERNEL = ['boxcar', 5]
    # gaussian with e-width in km/s
    # KERNEL = ['gaussian', 3.5]
    # supergaussian e-width + exponent
    # KERNEL = ['supergaussian', 3.5, 4]

    # build file paths
    # IN_FILES = glob.glob('Gl699/2*o_pp_e2dsff_*tcorr_AB.fits')
    # BLAZE_FILE = 'workplace1/2019-04-20_2400404f_pp_blaze_AB.fits'
    # MASK_FILE = 'Gl699_neg.mas'
    # MASK_FILE = 'workplace2/masque_sept18_andres_trans50.mas'

    for IN_FILE in IN_FILES:
        # get input telluric corrected file and header
        image, header = fits.getdata(IN_FILE, header=True)
        blaze = fits.getdata(BLAZE_FILE)
        masktable = read_mask(MASK_FILE, MASK_COLS)
        wheader = header
        wave = fits2wave(wheader)
        # wave, wheader = fits.getdata(WAVE_FILE, header=True)
        # get the dimensions
        nbo, nbpix = image.shape

        outname = write_file(dict(), IN_FILE, MASK_FILE, header, wheader, only_outname=True)
        if os.path.isfile(outname):
            print('File {0} exists, we skip'.format(outname))
            continue

        # --------------------------------------------------------------------------
        # get fiber typoe
        if 'FIBER' in header:
            fiber = header['FIBER']
        else:
            raise ValueError('HEADER ERROR: FIBER MISSING')
        # --------------------------------------------------------------------------
        # get dprtype
        if 'DPRTYPE' in header:
            if fiber == 'AB':
                dprtype = header['DPRTYPE'].split('_')[0]
            else:
                dprtype = header['DPRTYPE'].split('_')[1]
        else:
            raise ValueError('HEADER ERROR: DPRTYPE MISSING')
        # make sure dprtype is correct for fiber
        if dprtype not in ['OBJ', 'FP']:
            raise ValueError('HEADER ERROR: DPRTPYE must be OBJ or FP')
        # --------------------------------------------------------------------------
        # get berv from header
        if fiber == 'AB' and dprtype == 'OBJ':
            berv = header['BERV']
            # absorption features
            fit_type = 0
        else:
            berv = 0.0
            # emission features
            fit_type = 1
        # --------------------------------------------------------------------------
        # get rv from header (or set to zero)
        if ('OBJRV' in header) and dprtype == 'OBJ':
            targetrv = header['OBJRV']
            if np.isnan(targetrv) or np.abs(targetrv) > CCF_RV_NULL:
                targetrv = 0.0
        else:
            targetrv = 0.0
        if IN_RV is not None:
            targetrv = float(IN_RV)
        # --------------------------------------------------------------------------
        # get mask centers, and weights
        _, mask_centers, mask_weights = get_mask(masktable, MASK_WIDTH)
        # --------------------------------------------------------------------------
        # Photon noise uncertainty
        # --------------------------------------------------------------------------
        dkwargs = dict(spe=image, wave=wave, sigdet=NOISE_SIGDET,
                       size=NOISE_SIZE, threshold=NOISE_THRES)
        # run DeltaVrms2D
        dvrmsref, wmeanref = delta_v_rms_2d(**dkwargs)
        wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f}'
        print(wmsg.format(fiber, wmeanref))

        # --------------------------------------------------------------------------
        # Calculate the CCF
        # --------------------------------------------------------------------------
        print('\nRunning CCF calculation')
        props = ccf_calculation(wave, image, blaze, targetrv, mask_centers,
                                mask_weights, berv, fit_type, kernel=KERNEL)
        # --------------------------------------------------------------------------
        # Calculate the mean CCF
        # --------------------------------------------------------------------------
        print('\nRunning Mean CCF')

        # add constants to props
        props['CCF_MASK'] = os.path.basename(MASK_FILE)
        props['CCF_STEP'] = CCF_STEP
        props['CCF_WIDTH'] = CCF_WIDTH
        props['TARGET_RV'] = targetrv
        props['CCF_SIGDET'] = NOISE_SIGDET
        props['CCF_BOXSIZE'] = NOISE_SIZE
        props['CCF_MAXFLUX'] = NOISE_THRES
        props['CCF_NMAX'] = CCF_N_ORD_MAX
        # props['MASK_MIN'] = MASK_MIN_WEIGHT
        props['MASK_WIDTH'] = MASK_WIDTH
        props['MASK_UNITS'] = 'nm'

        props = mean_ccf(props, targetrv, fit_type)

        # --------------------------------------------------------------------------
        # Plots
        # --------------------------------------------------------------------------
        if PLOT:
            # plot individual CCFs
            print('\n Plotting individual CCFs')
            plot_individual_ccf(props, nbo)
            # plot mean ccf and fit
            print('\n Plotting Mean CCF')
            plot_mean_ccf(props)

        # --------------------------------------------------------------------------
        # Save file
        # --------------------------------------------------------------------------
        # write the two tables to file CCFTABLE_{filename}_{mask}.fits
        write_file(props, IN_FILE, MASK_FILE, header, wheader)

    return IN_FILE


def wrap_ccf():
    # file_strings = ['Gl699/2*o_pp_e2dsff_*tcorr_AB.fits','Gl699/2*o_pp_e2dsff_*sanit_AB.fits']
    # mask_names = ['M4_all.mas','Gl699_full.mas','Gl699_neg.mas','Gl699_pos.mas','workplace2/masque_sept18_andres_trans50.mas']

    file_strings = ['Gl699/2*o_pp_e2dsff_*sanit_AB.fits', 'Gl699/2*o_pp_e2dsff_*tcorr_AB.fits']
    mask_names = ['Gl699_neg.mas', 'Gl699_full.mas']

    for file_string in file_strings:
        for mask_name in mask_names:
            get_ccf(glob.glob(file_string), MASK_FILE=mask_name)