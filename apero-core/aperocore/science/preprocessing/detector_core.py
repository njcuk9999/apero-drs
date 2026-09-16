#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Preprocessing detector science functions

Pure numerical routines for detector-level corrections (cosmic ray
rejection using the slope/intercept ramp fit, and top/bottom reference
pixel correction). These functions do not load APERO profiles or depend
on apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import Tuple

import numpy as np

from aperocore.base import base
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.preprocessing.detector_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def correct_cosmics(image: np.ndarray, intercept: np.ndarray,
                    errslope: np.ndarray, inttime: np.ndarray, tamp: int,
                    ntop: int, nbottom: int, readout_noise: float,
                    variance_cut1: float, variance_cut2: float,
                    intercept_cut1: float, intercept_cut2: float,
                    intboxsize: int
                    ) -> Tuple[np.ndarray, int, int, int]:
    """
    Locate and correct cosmic rays using the errorslope and the intercept

    :param image: numpy array (2D), the image to correct
    :param intercept: numpy array (2D), the intercept image
    :param errslope: numpy array (2D), the error slope image
    :param inttime: numpy array (2D), the integration time [s] image
    :param tamp: int, the total number of amplifiers
    :param ntop: int, the number of reference pixels at the top
    :param nbottom: int, the number of reference pixels at the bottom
    :param readout_noise: float, the estimated readout noise
    :param variance_cut1: float, the lower slope-variance cut (in sigma^2)
    :param variance_cut2: float, the upper slope-variance cut (in sigma^2)
    :param intercept_cut1: float, the lower intercept cut (in sigma^2)
    :param intercept_cut2: float, the upper intercept cut (in sigma^2)
    :param intboxsize: int, the box size (pixels) used for the per-region
                       intercept median removal

    :return: tuple, 1. numpy array (2D), the corrected image (bad pixels
             set to NaN), 2. int, the number of bad intercept pixels,
             3. int, the number of bad slope pixels, 4. int, the number of
             pixels bad in both
    """
    # get the 1 sigma fraction (~68)
    norm_frac = mp.normal_fraction(1) * 100
    # get shape of image
    nby, nbx = image.shape
    # get the size of each amplifier
    ampsize = int(nbx / tamp)
    # express image and slope in ADU not ADU/s
    image2 = np.array(image) * inttime
    with warnings.catch_warnings(record=True) as _:
        errslope = np.array(errslope) * inttime
    # -------------------------------------------------------------------------
    # using the error on the slope
    # -------------------------------------------------------------------------
    # express excursions as variance so we can subtract things
    variance = errslope ** 2
    # get a list of reference pixels
    ref_pix = list(range(nbottom)) + list(range(nby - ntop, nby))
    ref_pix = np.array(ref_pix)
    # loop around amplifiers and subtract median per-amplifier variance
    for it in range(tamp):
        # get start and end points of this amplifier
        start, end = it * ampsize, it * ampsize + ampsize
        # get the box of reference pixels for this amplifier
        box = variance[ref_pix, start:end]
        # get median of box
        with warnings.catch_warnings(record=True) as _:
            boxmed = mp.nanmedian(box)
        # subtract median per-amplifier variance
        variance[:, start:end] = variance[:, start:end] - boxmed
    # set all negative pixels to 0 (just for the flagging)
    image2[image2 < 0] = 0
    # get the expected image value (with noise estimate added)
    expected = image2 + readout_noise ** 2
    # get the fractional number of sigmas away from expected value
    with warnings.catch_warnings(record=True) as _:
        nsig2 = variance / expected
    # number of simga away from bulk of expected-to-observed variance
    with warnings.catch_warnings(record=True) as _:
        nsig2 = nsig2 / mp.nanpercentile(np.abs(nsig2), norm_frac)
    # mask the nsigma by the variance cuts
    mask1 = np.array(nsig2 > variance_cut1)
    mask2 = np.array(nsig2 > variance_cut2)
    # mask of where variance is bad
    mask_slope_variance = mp.xpand_mask(mask1, mask2)
    # set bad pixels to NaN
    image[mask_slope_variance] = np.nan
    # -------------------------------------------------------------------------
    # using the intercept
    # -------------------------------------------------------------------------
    # remove median per-column intercept
    for it in range(nbx):
        # get intercept median
        with warnings.catch_warnings(record=True) as _:
            intmed = mp.nanmedian(intercept[:, it])
            # subtract off the median
        intercept[:, it] = intercept[:, it] - intmed
    # remove per-region intercept - loop around the box sizes
    for it in range(intboxsize):
        for jt in range(intboxsize):
            # work out ypix start and end
            starty, endy = it * intboxsize, it * intboxsize + intboxsize
            # work out xpix start and end
            startx, endx = jt * intboxsize, jt * intboxsize + intboxsize
            # work out median of intbox
            with warnings.catch_warnings(record=True) as _:
                intmed = mp.nanmedian(intercept[starty:endy, startx:endx])
            # subtract off the intbox median
            intercept[starty:endy, startx:endx] -= intmed
    # normalize to 1-sigma
    with warnings.catch_warnings(record=True) as _:
        intercept = intercept / mp.nanpercentile(np.abs(intercept), norm_frac)
    # express as varuabce
    nsig2 = intercept ** 2
    # mask the nsigma by the variance cuts
    mask1 = np.array(nsig2 > intercept_cut1)
    mask2 = np.array(nsig2 > intercept_cut2)
    # mask of where variance is bad
    mask_intercept_deviation = mp.xpand_mask(mask1, mask2)
    # do not mask the reference pixels (intercept is different from rest of
    #  the detector)
    mask_intercept_deviation[ref_pix] = False
    mask_intercept_deviation[:, ref_pix] = False
    # set bad pixels to NaN
    image[mask_intercept_deviation] = np.nan
    # calculate some stats
    num_bad_intercept = int(mp.nansum(mask_intercept_deviation))
    num_bad_slope = int(mp.nansum(mask_slope_variance))
    # get those with both
    mask_both = mask_intercept_deviation & mask_slope_variance
    num_bad_both = int(mp.nansum(mask_both))
    # return the image and the bad-pixel stats
    return image, num_bad_intercept, num_bad_slope, num_bad_both


def ref_top_bottom(image: np.ndarray, tamp: int, ntop: int,
                   nbottom: int) -> np.ndarray:
    """
    Correction for the top and bottom reference pixels

    :param image: numpy array (2D), the image
    :param tamp: int, the total number of amplifiers
    :param ntop: int, the number of reference pixels at the top
    :param nbottom: int, the number of reference pixels at the bottom

    :return: numpy array (2D), the corrected image
    """
    # get the image size
    dim1, dim2 = image.shape
    # get number of pixels in amplifier
    pix_in_amp = dim2 // tamp
    pix_in_amp_2 = pix_in_amp // 2
    # work out the weights for y pixels
    weight = np.arange(dim1) / (dim1 - 1)
    # pipe into array to cover odd pixels and even pixels
    weightarr = np.repeat(weight, dim2 // pix_in_amp_2)
    # reshape
    weightarr = weightarr.reshape(dim1, pix_in_amp_2)
    # loop around each amplifier
    for amp_num in range(tamp):
        # get the pixel mask for this amplifier
        pixmask = (amp_num * dim2 // tamp) + 2 * np.arange(pix_in_amp_2)
        # loop around the even and then the odd pixels
        for oddeven in range(2):
            # work out the median of the bottom pixels for this amplifier
            bottom = mp.nanmedian(image[:nbottom, pixmask + oddeven])
            top = mp.nanmedian(image[dim1 - ntop:, pixmask + oddeven])
            # work out contribution to subtract from top and bottom
            contrib = (top * weightarr) + (bottom * (1 - weightarr))
            # subtraction contribution from image for this amplifier
            image[:, pixmask + oddeven] -= contrib
    # return corrected image
    return image
