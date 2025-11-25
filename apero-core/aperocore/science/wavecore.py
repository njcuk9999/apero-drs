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
