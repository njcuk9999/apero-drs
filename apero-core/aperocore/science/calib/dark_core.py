#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dark calibration science functions

Pure numerical routines used to characterise and correct for dark current.
These functions do not load APERO profiles or depend on apero-drs.

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
__NAME__ = 'aperocore.science.calib.dark_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def measure_dark(image: np.ndarray, dark_qmin: int, dark_qmax: int,
                 histo_bins: int, histo_low: float, histo_high: float
                 ) -> Tuple[Tuple[np.ndarray, np.ndarray], float, float,
                           float, float]:
    """
    Measure the dark pixels in "image"

    :param image: numpy array (2D), the image
    :param dark_qmin: int, the lower percentile (0 - 100) used for the
                      logged statistics
    :param dark_qmax: int, the upper percentile (0 - 100) used for the
                      logged statistics
    :param histo_bins: int, the number of bins in dark histogram
    :param histo_low: float, the lower extent of the histogram in ADU/s
    :param histo_high: float, the upper extent of the histogram in ADU/s

    :returns: tuple, 1. hist numpy.histogram tuple (hist, bin_edges) - the
             two arrays have different lengths so this is a tuple, not a
             numpy array,
             2. med: float, the median value of the non-Nan image values,
             3. dadead: float, the fraction of dead pixels as a percentage
             4. qmin: float, the dark_qmin-th percentile of the image
             5. qmax: float, the dark_qmax-th percentile of the image

          where:
              hist : numpy array (1D) The values of the histogram.
              bin_edges : numpy array (1D) of floats, the bin edges
    """
    # make sure image is a numpy array
    image = np.array(image)
    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = mp.nanmedian(fimage)
    # get the qmin-th and qmax-th percentile
    qmin, qmax = np.percentile(fimage, [dark_qmin, dark_qmax])
    # get the histogram for flattened data
    histo = np.histogram(fimage, bins=histo_bins,
                         range=(histo_low, histo_high), density=True)
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.prod(image.shape)
    # return the statistics (histo is a (hist, bin_edges) tuple of arrays
    # with different lengths, so it is not converted to a numpy array)
    outs = histo, float(med), float(dadead), float(qmin), float(qmax)
    return outs


def measure_dark_badpix(image: np.ndarray, nanmask: np.ndarray,
                        darkcutlimit: float) -> Tuple[float, float]:
    """
    Measure the bad pixels (non-dark pixels and NaN pixels)

    :param image: numpy array (2D), the image
    :param nanmask: numpy array (2D), the mask of non-finite values
    :param darkcutlimit: float, the bad pixel cut limit in ADU/s

    :return: tuple, 1. the percentage of bad dark pixels
             2. the percentage of bad dark pixels above cut limit or NaN
    """
    # get number of bad dark pixels (as a fraction of total pixels)
    with warnings.catch_warnings(record=True) as _:
        baddark = 100.0 * np.sum(image > darkcutlimit)
        baddark /= np.prod(image.shape)
    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as _:
        datacutmask = ~((image > darkcutlimit) | nanmask)
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.prod(image.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    dadeadall = n_bad_pix * 100 / np.prod(image.shape)
    # return baddark and dadeadall
    return baddark, dadeadall


def correct_dark(image: np.ndarray, darkimage: np.ndarray, nfiles: int
                 ) -> np.ndarray:
    """
    Correct "image" for "dark" by subtracting the dark scaled by the number
    of files that were combined to create "image"

    :param image: numpy array (2D), the image
    :param darkimage: numpy array (2D), the dark image
    :param nfiles: int, number of files that created image (need to
                   multiply by this to get the total dark)

    :return: numpy array (2D), the dark corrected image
    """
    return image - (darkimage * nfiles)
