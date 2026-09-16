#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Radial velocity / CCF science functions

Pure numerical routines for measuring FP peaks, photon noise, bisector
spans and other small radial-velocity helpers. These functions do not
load APERO profiles or depend on apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy.optimize import curve_fit

from aperocore.base import base
from aperocore.base import physics
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.velocity.velocity_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Speed of light
speed_of_light_ms = physics.speed_of_light_ms
speed_of_light = physics.speed_of_light_kms


# =============================================================================
# Define functions
# =============================================================================
def fwhm_fp_airy(popt: np.ndarray) -> float:
    """
    Calculate the FWHM of the FP peaks from the fit parameters

    :param popt: numpy array (1D), the best fit parameters from the FP peak
                 fitting

    :return: float, the FWHM of the FP peaks
    """
    # we find the fwhm of this function:
    #     # calculate ea_airy_function
    #     y = zp + amp * ((1 + np.cos(2 * np.pi * (x - x0) / w)) / 2.0) ** beta
    #   done in mp.ea_airy_function
    # get the parameters
    amp, x0, w, beta, zp = popt

    part1 = 2 * ((0.5 ** (1 / beta)) - 1)
    # deal with out of bounds
    if abs(part1) > 1:
        return np.nan
    # calculate the half width (inverse of beta)
    half_width = w * np.arccos(part1) / (2 * np.pi)
    # calculate the full width
    full_width = 2 * half_width
    # return the FWHM and error on the FWHM
    return full_width


def fit_fp_peaks(x: np.ndarray, y: np.ndarray, size: float,
                 return_model: bool = False
                 ) -> Union[Tuple[List[float], np.ndarray, Any,
                           Optional[str]],
                           Tuple[List[float], np.ndarray, Any,
                           Optional[str], np.ndarray]]:
    """
    Fit a FP peak with an Airy function

    :param x: numpy array (1D), the pixel positions around the peak
    :param y: numpy array (1D), the flux values around the peak
    :param size: float, the initial guess for the period of the peak
    :param return_model: bool, if True also return the fitted model

    :return: tuple, 1. the initial guess parameters, 2. the best fit
             parameters, 3. the fit covariance matrix (or None), 4. a
             warning string (or None) and, if return_model is True,
             5. the fitted model values
    """
    # storage of warnings
    warns = None
    # get gauss function
    ea_airy = mp.ea_airy_function
    # get the guess on the maximum peak position
    maxpos = mp.nanargmax(y)
    minpos = mp.nanargmin(y)
    ymax = y[maxpos]
    ymin = y[minpos]
    # set up initial guess
    # [amp, position, period, exponent, zero point]
    p0 = [ymax - ymin, mp.nanmedian(x), size, 1.5, np.max([0, ymin])]

    # deal with bad bounds
    if warns is not None:
        popt = [np.nan, np.nan, np.nan, np.nan, np.nan]
        pcov = None
        model = np.repeat([np.nan], len(x))
    else:
        # try to fit etiennes airy function
        try:
            with warnings.catch_warnings(record=True) as _:
                # popt, pcov = curve_fit(ea_airy, x, y, p0=p0, bounds=bounds)
                # noinspection PyTupleAssignmentBalance
                popt, pcov = curve_fit(ea_airy, x, y, p0=p0)
            model = ea_airy(x, *popt)
        except ValueError as e:
            # log that ydata or xdata contains NaNs
            popt = [np.nan, np.nan, np.nan, np.nan, np.nan]
            pcov = None
            warns = '{0}: {1}'.format(type(e), e)
            model = np.repeat([np.nan], len(x))
        except RuntimeError as e:
            popt = [np.nan, np.nan, np.nan, np.nan, np.nan]
            pcov = None
            warns = '{0}: {1}'.format(type(e), e)
            model = np.repeat([np.nan], len(x))
    # deal with returning model
    if return_model:
        return p0, popt, pcov, warns, model
    else:
        # return the guess and the best fit
        return p0, popt, pcov, warns


def delta_v_rms_2d(spe: np.ndarray, wave: np.ndarray, sigdet: float,
                   threshold: float, size: int
                   ) -> Tuple[np.ndarray, float, np.ndarray]:
    """
    Compute the photon noise uncertainty for all orders (for the 2D image)

    :param spe: numpy array (2D), the extracted spectrum
                size = (number of orders by number of columns (x-axis))
    :param wave: numpy array (2D), the wave solution for each pixel
    :param sigdet: float, the read noise (sigdet) for calculating the
                   noise array
    :param threshold: float, upper limit for pixel values, above this limit
                      pixels are regarded as saturated
    :param size: int, size (in pixels) around saturated pixels to also
                 regard as bad pixels

    :return: tuple, 1. numpy array (1D), the photon noise for each order
             (squared), 2. float, weighted mean photon noise across all
             orders, 3. numpy array (1D), the per-order photon noise
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
    # get the total per order
    tot = mp.nansum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    with warnings.catch_warnings(record=True) as _:
        dvrms2 = (speed_of_light_ms ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(mp.nansum(1.0 / dvrms2))
    # per order value
    weightedmeanorder = np.sqrt(dvrms2)
    # return dv rms and weighted mean
    return dvrms2, weightedmean, weightedmeanorder


def estimate_photon_noise(wavemap: np.ndarray, rv_ccf: np.ndarray,
                          ccf_fit_ord: np.ndarray,
                          ccf_coeffs_ord: np.ndarray, sig_ord: np.ndarray,
                          fit_type: int, norm: float = 1
                          ) -> Tuple[float, float]:
    """
    Estimate the photon noise using the gradients of wave, dv and ccf

    :param wavemap: np.ndarray, the wavelength map for this order
    :param rv_ccf: np.ndarray, the rv vector
    :param ccf_fit_ord: np.ndarray, the fitted gaussian slope vector
    :param ccf_coeffs_ord: np.ndarray, the gaussian slope coefficients
    :param sig_ord: np.ndarray, the ccf pixel noise vector
    :param fit_type: int, the type of fit (0=absorption, 1=emission)
    :param norm: scale factor for the fit compared to the ccf

    :return: tuple, 1. the CCF photon noise, 2. The CCF SNR
    """
    # some gradients
    gradwave = np.nanmedian(wavemap / np.gradient(wavemap))
    grad_dv = np.gradient(rv_ccf)
    med_grad_dv = mp.nanmedian(grad_dv)
    # estimate oversampling factor
    oversampling_ratio_ord = (speed_of_light / gradwave) / med_grad_dv
    # error on the RV from the photon noise
    ccf_grad = np.gradient(ccf_fit_ord * norm) / grad_dv
    # bouchy 2001 formula
    sum_ratio2 = np.sqrt(np.sum((ccf_grad / sig_ord) ** 2))
    ccf_phot_noise = (1 / sum_ratio2) * np.sqrt(oversampling_ratio_ord)
    # get the ccf snr (1/mean snr)*depth
    if fit_type == 0:
        ccf_snr = ccf_coeffs_ord[1] * mp.fwhm() / ccf_phot_noise
    else:
        ccf_snr = ccf_coeffs_ord[2] * mp.fwhm() / ccf_phot_noise
    # return the photon noise and SNR
    return ccf_phot_noise, ccf_snr


def bisector_cut(xx: np.ndarray, yy: np.ndarray, cut: float) -> float:
    """
    Calculate the bisector span of the CCF at a given cut

    :param xx: np.ndarray, the x values (radial velocities)
    :param yy: np.ndarray, the y values (CCF values)
    :param cut: float, the cut value to calculate the bisector span at

    :return: float, the bisector span at this cut value
    """
    # find the two points where the CCF is above cut and interpolate with a
    #    linear fit
    lims1 = np.where(yy > cut)[0][[0, -1]]
    # find the value at the left side
    x1_start = max([lims1[0] - 2, 0])
    x1_end = min([lims1[0] + 1, len(yy)])
    v1_fit = np.polyfit(yy[x1_start:x1_end], xx[x1_start:x1_end], 1)
    v1_val = np.polyval(v1_fit, cut)
    # find the value at the right side
    x2_start = lims1[1]
    x2_end = min([lims1[1] + 2, len(yy)])
    v2_fit = np.polyfit(yy[x2_start:x2_end], xx[x2_start:x2_end], 1)
    v2_val = np.polyval(v2_fit, cut)
    # return the bisector span for this cut
    return (v1_val + v2_val) / 2


def bisector(rv: np.ndarray, ccf: np.ndarray, ccf_coeffs: np.ndarray,
            fit_type: int, bs_cut_top: float, bs_cut_bottom: float) -> float:
    """
    Calculate the bisector span of the CCF

    :param rv: np.ndarray, the radial velocities for the ccf
    :param ccf: np.ndarray, the CCF values
    :param ccf_coeffs: np.ndarray, the gaussian fit coefficients for the CCF
    :param fit_type: int, the type of fit (0=absorption, 1=emission)
    :param bs_cut_top: float, the fraction of the depth for the top cut
    :param bs_cut_bottom: float, the fraction of the depth for the bottom
                          cut

    :return: float, the bisector span
    """
    # take the gaussian fit without a depth
    ccf_coeffs2 = np.array(ccf_coeffs)
    # set the depth to 0 (i.e. no depth)
    ccf_coeffs2[2] = 0
    # normalize CCF without the gaussian. Sets the continuum flat to 1
    if fit_type == 0:
        ccf2 = (1 - ccf / mp.gaussian_slope(rv, *ccf_coeffs2)) / ccf_coeffs[2]
    else:
        ccf2 = (ccf - mp.gauss_fit_s(rv, *ccf_coeffs2)) / ccf_coeffs[0]
    # ----------------------------------------------------------------------
    # Bisector at cut1
    span_top = bisector_cut(rv, ccf2, bs_cut_top)
    # Bisector at cut2
    span_bottom = bisector_cut(rv, ccf2, bs_cut_bottom)
    # difference between the two bisector cuts
    return span_top - span_bottom


def get_coeff_dict(coeffs: np.ndarray, names: List[str]
                   ) -> Dict[str, Union[np.ndarray, float]]:
    """
    Turn a coefficients vector (2D - per order or 1D) into a dictionary
    of terms which can be called with fit names

    :param coeffs: np.ndarray - 2D - per order or 1D list of coefficients.
                   If 2D should be Nxlen(names) in shape
    :param names: list of strings, the name of the coefficients

    :return: dict, dictionary of coefficients key = name
    """
    # storage for coefficients
    cdict = dict()
    # loop around fit names
    for f_it, name in enumerate(names):
        if len(coeffs.shape) == 2:
            cdict[name] = coeffs[:, f_it]
        else:
            cdict[name] = coeffs[f_it]
    # return coefficients
    return cdict
