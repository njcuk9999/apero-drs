#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-11-25 at 09:40

@author: cook
"""
import copy
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.ndimage import median_filter, zoom, binary_dilation
from scipy.optimize import curve_fit
from scipy.special import erf, erfinv

from aperocore.base import base
from aperocore import math as mp
from aperocore.core import drs_log
from aperocore.base import physics

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.calib.wave_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get apero exception
AperoCodedException = drs_log.AperoCodedException
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = physics.speed_of_light_ms
# noinspection PyUnresolvedReferences
speed_of_light_kms = physics.speed_of_light_kms


# =============================================================================
# Define functions
# =============================================================================
def wave_to_wave(spectrum, wave1, wave2, reshape=False, splinek=5):
    """
    Shifts a "spectrum" at a given wavelength solution (map), "wave1", to
    another wavelength solution (map) "wave2"

    :param spectrum: numpy array (2D),  flux in the reference frame of the
                     file wave1
    :param wave1: numpy array (2D), initial wavelength grid
    :param wave2: numpy array (2D), destination wavelength grid
    :param reshape: bool, if True try to reshape spectrum to the shape of
                    the output wave solution
    :param splinek: int, the splinke k value

    :return output_spectrum: numpy array (2D), spectrum resampled to "wave2"
    """
    func_name = __NAME__ + '._wave_to_wave()'
    # deal with reshape
    if reshape or (spectrum.shape != wave2.shape):
        try:
            spectrum = spectrum.reshape(wave2.shape)
        except ValueError:
            # log that we cannot reshape spectrum
            emsg = ('Spectrum (shape = {0}) cannot be reshaped to match wave '
                    'solution (shape = {1}) \n\t Function = {2}')
            eargs = [spectrum.shape, wave2.shape, func_name]
            raise AperoCodedException(None, None, message=emsg.format(*eargs))
    # if they are the same
    # noinspection PyTypeChecker
    if mp.nansum(wave1 != wave2) == 0:
        return spectrum
    # size of array, assumes wave1, wave2 and spectrum have same shape
    sz = np.shape(spectrum)
    # create storage for the output spectrum
    output_spectrum = np.zeros(sz) + np.nan
    # looping through the orders to shift them from one grid to the other
    for iord in range(sz[0]):
        # only interpolate valid pixels
        g = np.isfinite(spectrum[iord, :])
        # if not enough valid pixel, then skip order (need k+1 points)
        if mp.nansum(g) > 6:
            # spline the spectrum
            spline = mp.iuv_spline(wave1[iord, g], spectrum[iord, g],
                                   k=splinek, ext=3)
            # keep track of pixels affected by NaNs
            splinemask = mp.iuv_spline(wave1[iord, :], g, k=1, ext=1)
            # spline the input onto the output
            output_spectrum[iord, :] = spline(wave2[iord, :])
            # find which pixels are not NaNs
            mask = splinemask(wave2[iord, :])
            # set to NaN pixels outside of domain
            bad = (output_spectrum[iord, :] == 0)
            output_spectrum[iord, bad] = np.nan
            # affected by a NaN value
            # normally we would use only pixels ==1, but we get values
            #    that are not exactly one due to the interpolation scheme.
            #    We just set that >50% of the
            # flux comes from valid pixels
            bad = (mask <= 0.9)
            # mask pixels affected by nan
            output_spectrum[iord, bad] = np.nan
    # return the filled output spectrum
    return output_spectrum


def update_wave_with_npeak(wave: np.ndarray, npeak: np.ndarray,
                           cavity_length_poly: np.ndarray,
                           cavity_pedestal: float,
                           fp_inv_itr: int ,
                           inst_wavestart: float,
                           inst_waveend: float) -> np.ndarray:
    """
    Update the wavelength solution using the nth peak and the cavity length
    polynomial

    :param wave: numpy array (2D), wavelength solution to update
    :param npeak: numpy array (2D), nth peak for each pixel
    :param cavity_length_poly: numpy array (1D), polynomial coefficients for
                               the cavity length as a function of order
    :param cavity_pedestal: float, pedestal value for the cavity length
    :param fp_inv_itr: int, define the number of iterations required to do the
                       FP polynomial inversion
    :param inst_wavestart: float, starting wavelength of the instrument
    :param inst_waveend: float, ending wavelength of the instrument

    :return: numpy array (2D), updated wavelength solution
    """
    # need a few iterations to invert polynomial relations
    for _ in range(fp_inv_itr):
        # invert the cavity vs wave
        tmp_cavity = mp.val_cheby(cavity_length_poly, wave,
                                  domain=[inst_wavestart, inst_waveend])
        tmp_cavity = tmp_cavity + cavity_pedestal
        # recalculate the initial guess at wavelength using the cavity
        #   width polynomial guess
        wave = tmp_cavity / npeak
    # return the updated wavelength solution
    return wave


def slinky_ewidth(wavegrid: np.ndarray, velocity_shifts: np.ndarray
                  ) -> Tuple[float, np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Compute the e-width of the covariance of velocity shifts as a function of
    wavelength distance

    This tells us how correlated the velocity shifts are at different
    wavelength separations

    :param wavegrid: The wavelength grid in microns
    :param velocity_shifts: The velocity shifts at each wavelength point in
                            m/s

    :return: tuple, 1. The e-width in km/s, the fit parameters and the
             covariance vs distance data
             2. popt: The fit parameters of the Gaussian
             3. cov_dv: The covariance vs distance data (gridx, gridy)
    """
    func_name = f'{__NAME__}.slinky_ewidth()'
    # define a grid for the covariance vs distance
    space_cov_dv = np.linspace(0, 2, 100) ** 2
    # mask out values that are too small (less than the smallest
    # wavelength step)
    too_small = mp.nanmedian(np.diff(wavegrid)) > space_cov_dv
    space_cov_dv = space_cov_dv[~too_small]
    # compute covariance vs distance
    cov_dv = mp.covariance_vs_distance(wavegrid, velocity_shifts, space_cov_dv)

    # in pcov, we force the zero point to zero and center to zero, we only
    # fit amplitude and sigma
    # Fit Gaussian to measured covariance with constraint that sigma
    # must be positive
    try:
        # noinspection PyTupleAssignmentBalance
        popt, pcov = curve_fit(mp.gauss_floor,
                               xdata=cov_dv[0], ydata=cov_dv[1],
                               p0=[mp.nanmax(cov_dv[1]), 1.0],
                               bounds=([0, 0], [np.inf, np.inf]))
    except RuntimeError:
        emsg = ('Could not fit Gaussian to covariance data '
                '\n\tFunction = {0}')
        eargs = [func_name]
        raise AperoCodedException(None, None, message=emsg.format(*eargs),
                                  targs=eargs)

    # Convert sigma to e-width (characteristic width of correlation)
    ew_cov = popt[1] / np.sqrt(2)

    # return e-width
    return ew_cov, popt, cov_dv


def slinky_fit(xvector: np.ndarray, yvector: np.ndarray, yerr: np.ndarray,
               wslinky: float = 1e-1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Project data points onto a regular grid using a Gaussian weight.

    :param x: The x values for which we have data and errors
    :param y: The y values for which we have data and errors
    :param yerr: The error on y
    :param wslinky: The e-width of the Gaussian kernel
    :param xmin: The starting point of the grid
    :param xmax: The end point of the grid
    :param npts: The number of points in the grid
    :return: The x and y values of the grid at which we have projected the data
    """
    # make sure we have no infinite values, nans and y uncertainties are
    # all positive
    valid = np.isfinite(xvector) & np.isfinite(yvector)
    valid &= np.isfinite(yerr) & (yerr > 0)
    # apply the valid mask
    xvector = np.array(xvector)[valid]
    yvector = np.array(yvector)[valid]
    yerr = np.array(yerr)[valid]
    # get the min and max of the x vector
    xmin = np.min(xvector)
    xmax = np.max(xvector)
    # the caracterisic length is the FWHM/2.355, we want >3 points per FWHM
    # so by using 2*wslinky, we have ~3.5 points per FWHM
    npts = int( 2*(xmax - xmin) / wslinky )
    # Create a grid of x values
    grid_x = np.linspace(xmin, xmax, npts)
    # Initialize weights and y values for the grid
    weights = np.full(npts, 1e-12)
    grid_y = np.zeros(npts)
    # pre-compute ratios of the x grid and original x vector to e-width
    xvbis = grid_x / wslinky
    xbis = xvector / wslinky
    # Loop over each data point
    for it in range(len(xvector)):
        # Calculate the distance between the grid points and the data point
        dd = xvbis - xbis[it]
        # only keep those within 10 e-widths
        good = np.abs(dd) < 10
        # mask the original distance
        dd2 = dd[good]
        # Calculate the weight of the data point
        weight2 = np.exp(-0.5 * dd2 ** 2) / yerr[it] ** 2
        # Add the weight to the grid weights
        weights[good] += weight2
        # Add the weighted y value to the grid y values
        grid_y[good] += weight2 * yvector[it]
    # Normalize the y values by the weights
    grid_y /= weights
    # return the grid x and y values
    return grid_x, grid_y


def table_adjust_fp_peak_number(
        order_num: np.ndarray,
        pixel_meas: np.ndarray,
        peak_number: np.ndarray,
        nsigcut: float = 3.0,
        fit_degree: int = 11,
        max_tries: int = 100) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Correct FP peak numbers that are offset by an integer order-to-order.

    The FP peak number at a fixed reference pixel varies smoothly with order.
    This function measures that trend, identifies the order with the largest
    residual to a robust polynomial fit, and applies an integer shift if that
    shift reduces the residual dispersion. The process repeats until no
    improvement is found or the iteration limit is reached.

    :param order_num: np.ndarray, the order number for each FP line
    :param pixel_meas: np.ndarray, the measured pixel position for each FP line
    :param peak_number: np.ndarray, the FP peak number for each FP line
    :param nsigcut: float, sigma threshold for the robust polynomial fit
    :param fit_degree: int, polynomial degree used in the robust fit
    :param max_tries: int, maximum number of correction attempts

    :return: tuple, 1. adjusted peak-number vector, 2. residual history dict
    """
    # Copy all inputs so we never mutate caller-owned arrays in place.
    orders = np.array(order_num, dtype=int)
    pixels = np.array(pixel_meas, dtype=float)
    peaks = np.array(peak_number, dtype=float)
    # Keep track of the original dtype for the returned peak numbers.
    peak_dtype = np.array(peak_number).dtype
    # Work out the reference pixel near the middle of the detector.
    pixref = 0.5 * (mp.nanmax(pixels) + mp.nanmin(pixels))
    # Define the per-order storage size from the maximum valid order.
    max_order = int(mp.nanmax(orders))
    # Store the interpolated peak number at the reference pixel for each order.
    midcount = np.full(max_order + 1, np.nan)
    # Store the integer correction eventually applied to each order.
    corrections = np.zeros(max_order + 1, dtype=int)
    # Set up plotting/debug information for every attempted iteration.
    res_dict = dict()
    res_dict['pixref'] = float(pixref)
    res_dict['order_num'] = np.arange(max_order + 1)
    res_dict['midcount_start'] = np.array(midcount)
    res_dict['midcount_end'] = np.array(midcount)
    res_dict['residuals'] = []
    res_dict['trial_residuals'] = []
    res_dict['fit_coeffs'] = []
    res_dict['worst_order'] = []
    res_dict['worst_shift'] = []
    res_dict['accepted'] = []
    res_dict['dispersion'] = []
    res_dict['trial_dispersion'] = []
    res_dict['order_corrections'] = np.array(corrections)
    res_dict['n_iterations'] = 0
    res_dict['stop_reason'] = 'not_run'
    # Loop around each order and estimate the peak number at pixref.
    for current_order in np.unique(orders):
        # Isolate the lines that belong to this order.
        omask = orders == current_order
        opixels = np.array(pixels[omask], dtype=float)
        opeaks = np.array(peaks[omask], dtype=float)
        # Keep only finite measurements.
        valid = np.isfinite(opixels) & np.isfinite(opeaks)
        opixels = opixels[valid]
        opeaks = opeaks[valid]
        # We need at least five points for the local line fit.
        if len(opixels) < 5:
            continue
        # Sort by pixel so the nearest-point selection is deterministic.
        sortmask = np.argsort(opixels)
        opixels = opixels[sortmask]
        opeaks = opeaks[sortmask]
        # Fit only the five lines closest to the reference pixel.
        near = np.argsort(np.abs(opixels - pixref))[:5]
        near = np.sort(near)
        # Fit a straight line between peak number and pixel position.
        fit = np.polyfit(opixels[near], opeaks[near], deg=1)
        # Evaluate the fitted line at the reference pixel.
        midcount[current_order] = np.polyval(fit, pixref)
    # Save the measured starting state for plotting.
    res_dict['midcount_start'] = np.array(midcount)
    # Stop early if there are not enough orders to fit a trend.
    finite_midcount = np.isfinite(midcount)
    if mp.nansum(finite_midcount) < 2:
        res_dict['midcount_end'] = np.array(midcount)
        res_dict['stop_reason'] = 'too_few_orders'
        if peak_dtype.kind in ['i', 'u']:
            peaks = peaks.astype(peak_dtype)
        return peaks, res_dict
    # Try iterative order-by-order integer corrections.
    for it in range(max_tries):
        # Use only finite orders when constructing the robust fit.
        valid_orders = np.where(np.isfinite(midcount))[0]
        # Downgrade the fit degree if too few orders are available.
        use_degree = min(int(fit_degree), len(valid_orders) - 1)
        # Stop if we cannot form a meaningful trend.
        if use_degree < 1:
            res_dict['stop_reason'] = 'fit_degree_too_small'
            break
        # Fit a smooth trend of the peak number at the reference pixel.
        fit, _ = mp.robust_polyfit(valid_orders, midcount[valid_orders],
                                   degree=use_degree,
                                   nsigcut=nsigcut)
        # Evaluate the fitted trend for all orders.
        model = np.polyval(fit, np.arange(len(midcount)))
        # Work out the residuals in units of FP peaks.
        res = midcount - model
        # Identify the order with the largest absolute residual.
        worst = int(mp.nanargmax(np.abs(res)))
        # The candidate correction is the nearest integer peak offset.
        shift = int(np.round(res[worst]))
        # Keep a trial version so we can compare dispersions.
        midcount_trial = np.array(midcount)
        midcount_trial[worst] -= shift
        # Keep the residuals to the same fit for the trial correction.
        trial_res = midcount_trial - model
        # Compare the residual dispersions before and after the shift.
        disp_before = float(mp.nanstd(res))
        disp_after = float(mp.nanstd(trial_res))
        # Save this attempted iteration for plotting.
        res_dict['residuals'].append(np.array(res))
        res_dict['trial_residuals'].append(np.array(trial_res))
        res_dict['fit_coeffs'].append(np.array(fit))
        res_dict['worst_order'].append(worst)
        res_dict['worst_shift'].append(shift)
        res_dict['dispersion'].append(disp_before)
        res_dict['trial_dispersion'].append(disp_after)
        # If the residual is not close to an integer, we are done.
        if shift == 0:
            res_dict['accepted'].append(False)
            res_dict['stop_reason'] = 'zero_shift on loop {0}'.format(it)
            break
        # Keep the correction only if it reduces the residual dispersion.
        if disp_after < disp_before:
            midcount = np.array(midcount_trial)
            corrections[worst] -= shift
            res_dict['accepted'].append(True)
            res_dict['n_iterations'] += 1
            res_dict['order_corrections'] = np.array(corrections)
            continue
        # Otherwise nothing useful is left to correct.
        res_dict['accepted'].append(False)
        res_dict['stop_reason'] = 'no_improvement'
        break
    else:
        res_dict['stop_reason'] = 'max_tries'
    # Apply the final per-order integer corrections to the peak numbers.
    adjusted_peaks = np.array(peaks)
    for current_order in np.unique(orders):
        if corrections[current_order] == 0:
            continue
        omask = orders == current_order
        adjusted_peaks[omask] = (adjusted_peaks[omask]
                                 + corrections[current_order])
    # Store the final state for plotting/inspection.
    res_dict['midcount_end'] = np.array(midcount)
    # Cast back to the original dtype when that is safe.
    if peak_dtype.kind in ['i', 'u']:
        adjusted_peaks = adjusted_peaks.astype(peak_dtype)
    # Return the corrected peak numbers and plotting history.
    return adjusted_peaks, res_dict


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
