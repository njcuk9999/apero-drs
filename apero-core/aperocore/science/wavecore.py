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
from typing import Any, List, Optional, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.ndimage import median_filter, zoom
from scipy.ndimage.morphology import binary_dilation
from scipy.optimize import curve_fit
from scipy.special import erf, erfinv
import statsmodels.api as statsmodels

from aperocore.base import base
from aperocore import math as mp
from aperocore.core import drs_log
from aperocore.base import physics

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.wavecore'
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
    too_small = np.nanmedian(np.diff(wavegrid)) > space_cov_dv
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
                               p0=[np.nanmax(cov_dv[1]), 1.0],
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
