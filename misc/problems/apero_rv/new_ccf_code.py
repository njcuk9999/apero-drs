#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-03-27 at 13:42

@author: cook
----------------------------------------------------------------------------
new_ccf_code.py
----------------------------------------------------------------------------


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
        IN_FILE: the e2dsff_C or e2dsff_tcorr _AB file
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
from astropy.io import fits
import numpy as np
import warnings
import sys
import os
from scipy.optimize import curve_fit
from scipy.stats import chisquare

import arv_util as arv

# =============================================================================
# Define variables
# =============================================================================
# constants
SPEED_OF_LIGHT = 299792.458  # [km/s]
IMAGE_PIXEL_SIZE = 2.28  # IMAGE_PIXEL_SIZE
MASK_COLS = ['ll_mask_s', 'll_mask_e', 'w_mask']
# get arguments
args = arv.Arguments(sys.argv)

# if all files copied to same directory set these to ''
# W1 = ''
# W2 = ''
# these files are on cook@nb19
W1 = '/scratch3/rali/spirou/mini_data/reduced/2019-04-20/'
W2 = '/scratch3/rali/drs/apero-drs/apero/data/spirou/ccf/'
# whether to plot (True or False)
args.PLOT = True
#---------------------------------------------------------------------------
# Pick you CCF convolution kernel. See explanantions below in the
# CCF function. Uncomment the kernel type you want and change the
# parameter.
# CCF is a set of Dirac functions
args.KERNEL = 'None'
# args.KERNEL_WIDTH = None
# args.KERNEL_EWIDTH = None
# args.KERNEL_BETA = None

# boxcar length expressed in km/s
# args.KERNEL = 'boxcar'
# args.KERNEL_WIDTH = 5

# gaussian with e-width in km/s
# args.KERNEL = 'gaussian'
# args.KERNEL_EWIDTH = 3.5

# supergaussian e-width + exponent
# args.KERNEL = 'supergaussian'
# args.KERNEL_EWIDTH = 3.5
# args.KERNEL_BETA = 4
#---------------------------------------------------------------------------

# deal with cases (quick switch between fiber=AB (OBJ) and fiber=C (FP)
#   quickly switch between:
#     case == 1:  standard AB OBJ fiber (edited in this file)
#     case == 2:  standard C FP fiber (edited in this file)
# set the case in the arguments
if args.CASE == 1:
    # build file paths
    args.IN_FILE = os.path.join(W1, '2400515o_pp_e2dsff_tcorr_AB.fits')
    args.BLAZE_FILE = os.path.join(W1, '2019-04-20_2400404f_pp_blaze_AB.fits')
    # if set to None uses IN_FILE header (where possible)
    # args.WAVE_FILE = None
    args.WAVE_FILE = os.path.join(W1, '2019-04-20_2400570c_pp_e2dsff_AB_wave_night_AB.fits')
    args.MASK_FILE = os.path.join(W2, 'masque_sept18_andres_trans50.mas')
    # variables
    # These values are taken from the constants file
    args.MASK_WIDTH = 1.7  # CCF_MASK_WIDTH
    args.MASK_MIN_WEIGHT = 0.0  # CCF_MASK_MIN_WEIGHT
    args.CCF_STEP = 0.5  # CCF_DEFAULT_STEP (or user input)
    args.CCF_WIDTH = 300  # CCF_DEFAULT_WIDTH (or user input)
    args.CCF_RV_NULL = 1000  # CCF_OBJRV_NULL_VAL (max allowed)
    args.IN_RV = None  # user input [km/s]
    args.CCF_N_ORD_MAX = 48  # CCF_N_ORD_MAX
    args.BLAZE_NORM_PERCENTILE = 90  # CCF_BLAZE_NORM_PERCENTILE
    args.BLAZE_THRESHOLD = 0.3  # WAVE_FP_BLAZE_THRES
    args.NOISE_SIGDET = 8.0  # CCF_NOISE_SIGDET
    args.NOISE_SIZE = 12  # CCF_NOISE_BOXSIZE
    args.NOISE_THRES = 1.0e9  # CCF_NOISE_THRES
elif args.CASE == 2:
    # build file paths
    args.IN_FILE = os.path.join(W1, '2400515o_pp_e2dsff_C.fits')
    args.BLAZE_FILE = os.path.join(W1, '2019-04-20_2400404f_pp_blaze_C.fits')
    # if set to None uses IN_FILE header (where possible)
    # WAVE_FILE = None
    args.WAVE_FILE = os.path.join(W1, '2019-04-20_2400570c_pp_e2dsff_C_wave_night_C.fits')
    args.MASK_FILE = os.path.join(W2, 'fp.mas')
    # variables
    # These values are taken from the constants file
    args.MASK_WIDTH = 1.7  # CCF_MASK_WIDTH
    args.MASK_MIN_WEIGHT = 0.0  # CCF_MASK_MIN_WEIGHT
    args.CCF_STEP = 0.5  # WAVE_CCF_STEP
    args.CCF_WIDTH = 7.5  # WAVE_CCF_WIDTH
    args.CCF_RV_NULL = 1000  # CCF_OBJRV_NULL_VAL (max allowed)
    args.IN_RV = None  # user input [km/s]
    args.CCF_N_ORD_MAX = 48  # WAVE_CCF_N_ORD_MAX
    args.BLAZE_NORM_PERCENTILE = 90  # CCF_BLAZE_NORM_PERCENTILE
    args.BLAZE_THRESHOLD = 0.3  # WAVE_FP_BLAZE_THRES
    args.NOISE_SIGDET = 8.0  # WAVE_CCF_NOISE_SIGDET
    args.NOISE_SIZE = 12  # WAVE_CCF_NOISE_BOXSIZE
    args.NOISE_THRES = 1.0e9  # WAVE_CCF_NOISE_THRES
else:
    raise ValueError('INPUT ERROR: Case must be 1 or 2')


# =============================================================================
# Define functions
# =============================================================================
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
        pfit, pcov = curve_fit(arv.gauss_function, x, y, p0=guess, sigma=weights,
                               absolute_sigma=True)
    if return_fit and return_uncertainties:
        # calculate the fit parameters
        yfit = arv.gauss_function(x, *pfit)
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
        yfit = arv.gauss_function(x, *pfit)
        # return pfit and yfit
        return pfit, yfit
    # if return uncertainties
    elif return_uncertainties:
        # calculate the fit parameters
        yfit = arv.gauss_function(x, *pfit)
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


def ccf_calculation(wave, image, blaze, targetrv, mask_centers, mask_weights,
                    berv, fit_type, ccf_width, ccf_step, blaze_norm_percentile,
                    blaze_threshold, kernel=None):
    # get rvmin and rvmax
    rvmin = targetrv - ccf_width
    rvmax = targetrv + ccf_width + ccf_step
    # get the dimensions
    nbo, nbpix = image.shape
    # create a rv ccf range
    rv_ccf = np.arange(rvmin, rvmax, ccf_step)
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
            ker = np.ones(int(np.round(kernel[1] / ccf_step)))
        elif kernel[0] == 'gaussian':
            # width of the gaussian expressed in
            # steps of CCF
            ew = kernel[1] / ccf_step
            index = np.arange(-4 * np.ceil(ew), 4 * np.ceil(ew) + 1)
            ker = np.exp(-0.5 * (index / ew) ** 2)
        elif kernel[0] == 'supergaussian':
            # width of the gaussian expressed in
            # steps of CCF. Exponents should be
            # between 0.1 and 10.. Values above
            # 10 are (nearly) the same as a boxcar.
            if (kernel[1] < 0.1) or (kernel[1] > 10):
                raise ValueError('CCF ERROR: kernel[1] is out of range.')

            ew = kernel[1] / ccf_step

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

        # COMMENT EA, normalizatoin moved before the masking
        #
        # normalize per-ord blaze to its peak value
        # this gets rid of the calibration lamp SED
        bl_ord /= np.nanpercentile(bl_ord, blaze_norm_percentile)
        # COMMENT EA, changing NaNs to 0 in the blaze
        bl_ord[np.isfinite(bl_ord) == 0] = 0
        # mask on the blaze
        with warnings.catch_warnings(record=True) as _:
            blazemask = bl_ord > blaze_threshold
        # get order mask centers and mask weights
        min_ord_wav = np.nanmin(wa_ord[blazemask])
        max_ord_wav = np.nanmax(wa_ord[blazemask])
        # COMMENT EA there's a problem with the sign in the min/max
        min_ord_wav = min_ord_wav * (1 - rvmin / SPEED_OF_LIGHT)
        max_ord_wav = max_ord_wav * (1 - rvmax / SPEED_OF_LIGHT)
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
        spline_sp = arv.iuv_spline(wa_ord[good], sp_ord[good], k=5, ext=1)
        spline_bl = arv.iuv_spline(wa_ord[good], bl_ord[good], k=5, ext=1)
        # ------------------------------------------------------------------
        # set up the ccf for this order
        ccf_ord = np.zeros_like(rv_ccf)
        # ------------------------------------------------------------------
        # get the wavelength shift (dv) in relativistic way
        wave_shifts = arv.relativistic_waveshift(rv_ccf - berv)
        # ------------------------------------------------------------------
        # set number of valid lines used to zero
        numlines = 0
        # loop around the rvs and calculate the CCF at this point
        part3 = spline_bl(omask_centers)
        for rv_element in range(len(rv_ccf)):
            wave_tmp = omask_centers * wave_shifts[rv_element]
            part1 = spline_sp(wave_tmp)
            part2 = spline_bl(wave_tmp)
            numlines = np.sum(spline_bl(wave_tmp) != 0)
            # CCF is the division of the sums
            with warnings.catch_warnings(record=True) as _:
                ccf_element = ((part1 * part3) / part2) * omask_weights
                ccf_ord[rv_element] = np.nansum(ccf_element)
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


def mean_ccf(props, targetrv, fit_type, ccf_n_ord_max, ccf_step, ccf_width,
             mask_file, noise_sigdet, noise_size, noise_thres, mask_min_weight,
             mask_width):
    # get the average ccf
    mean_ccf = np.nanmean(props['CCF'][: ccf_n_ord_max], axis=0)
    # get the fit for the normalized average ccf
    mean_ccf_coeffs, mean_ccf_fit = fit_ccf(props['RV_CCF'],
                                            mean_ccf, fit_type=fit_type)
    # get the RV value from the normalised average ccf fit center location
    ccf_rv = float(mean_ccf_coeffs[1])
    # get the contrast (ccf fit amplitude)
    ccf_contrast = np.abs(100 * mean_ccf_coeffs[0])
    # get the FWHM value
    ccf_fwhm = mean_ccf_coeffs[2] * arv.fwhm()
    # --------------------------------------------------------------------------
    #  CCF_NOISE uncertainty
    ccf_noise_tot = np.sqrt(np.nanmean(props['CCF_NOISE'] ** 2, axis=0))
    # Calculate the slope of the CCF
    average_ccf_diff = (mean_ccf[2:] - mean_ccf[:-2])
    rv_ccf_diff = (props['RV_CCF'][2:] - props['RV_CCF'][:-2])
    ccf_slope = average_ccf_diff / rv_ccf_diff
    # Calculate the CCF oversampling
    ccf_oversamp = IMAGE_PIXEL_SIZE / ccf_step
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
    # add constants to props
    props['CCF_MASK'] = os.path.basename(mask_file)
    props['CCF_STEP'] = ccf_step
    props['CCF_WIDTH'] = ccf_width
    props['TARGET_RV'] = targetrv
    props['CCF_SIGDET'] = noise_sigdet
    props['CCF_BOXSIZE'] = noise_size
    props['CCF_MAXFLUX'] = noise_thres
    props['CCF_NMAX'] = ccf_n_ord_max
    props['MASK_MIN'] = mask_min_weight
    props['MASK_WIDTH'] = mask_width
    props['MASK_UNITS'] = 'nm'
    # --------------------------------------------------------------------------
    return props


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    # need to get arguments from command line
    args.args_from_cmd()
    args.kernel_args()
    # get input telluric corrected file and header
    image, header = fits.getdata(args.IN_FILE, header=True)
    blaze = fits.getdata(args.BLAZE_FILE)
    masktable = arv.read_mask(args.MASK_FILE, MASK_COLS)
    wave, wheader, wavefile = arv.read_wave(image, header, args.WAVE_FILE)
    # get the dimensions
    nbo, nbpix = image.shape
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
        if np.isnan(targetrv) or np.abs(targetrv) > args.CCF_RV_NULL:
            targetrv = 0.0
    else:
        targetrv = 0.0
    if args.IN_RV is not None:
        targetrv = float(args.IN_RV)
    # --------------------------------------------------------------------------
    # get mask centers, and weights
    _, mask_centers, mask_weights = arv.get_mask(masktable, args.MASK_WIDTH,
                                                 args.MASK_MIN_WEIGHT)
    # --------------------------------------------------------------------------
    # Photon noise uncertainty
    # --------------------------------------------------------------------------
    dkwargs = dict(spe=image, wave=wave, sigdet=args.NOISE_SIGDET,
                   size=args.NOISE_SIZE, threshold=args.NOISE_THRES)
    # run DeltaVrms2D
    dvrmsref, wmeanref = delta_v_rms_2d(**dkwargs)
    wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f}'
    print(wmsg.format(fiber, wmeanref))

    # --------------------------------------------------------------------------
    # Calculate the CCF
    # --------------------------------------------------------------------------
    print('\nRunning CCF calculation')
    props = ccf_calculation(wave, image, blaze, targetrv, mask_centers,
                            mask_weights, berv, fit_type, args.CCF_WIDTH,
                            args.CCF_STEP, args.BLAZE_NORM_PERCENTILE,
                            args.BLAZE_THRESHOLD, kernel=args.kernelparams)
    # --------------------------------------------------------------------------
    # Calculate the mean CCF
    # --------------------------------------------------------------------------
    print('\nRunning Mean CCF')
    props = mean_ccf(props, targetrv, fit_type, args.CCF_N_ORD_MAX,
                     args.CCF_STEP, args.CCF_WIDTH, args.MASK_FILE,
                     args.NOISE_SIGDET, args.NOISE_SIZE, args.NOISE_THRES,
                     args.MASK_MIN_WEIGHT, args.MASK_WIDTH)

    # --------------------------------------------------------------------------
    # Plots
    # --------------------------------------------------------------------------
    if args.PLOT:
        # plot individual CCFs
        print('\n Plotting individual CCFs')
        arv.plot_individual_ccf(props, nbo)
        # plot mean ccf and fit
        print('\n Plotting Mean CCF')
        arv.plot_mean_ccf(props)

    # --------------------------------------------------------------------------
    # Save file
    # --------------------------------------------------------------------------
    # write the two tables to file CCFTABLE_{filename}_{mask}.fits
    arv.write_file(props, args.IN_FILE, args.MASK_FILE, header, wheader,
                   wavefile, args.OUTDIR)

# ==============================================================================
# End of code
# ==============================================================================
