#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bad pixel detection science functions

Pure numerical routines used to build a bad pixel map from a normalised
flat image and a dark image. These functions do not load APERO profiles or
depend on apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import List, Tuple

import numpy as np
from scipy.ndimage import filters

from aperocore.base import base
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.calib.badpix_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def normalise_median_flat(image: np.ndarray, wmed: float,
                          percentile: float, method: str = 'new'
                          ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Applies a median filter and normalises. Median filter is applied with
    width "wmed" and then normalised by the "percentile"-th percentile

    :param image: numpy array (2D), the image to median filter and
                  normalise
    :param wmed: float, the median filter width (see
                 scipy.ndimage.filters.median_filter "size" for more details)
    :param percentile: float, the percentile to normalise the image at
    :param method: string, "new" or "old" if "new" uses np.nanpercentile else
                   sorts the flattened image and takes the "percentile" (i.e.
                   90th) pixel value to normalise

    :returns: tuple, 1. norm_med_image: numpy array (2D), the median filtered
                        and normalised image
                     2. norm_image: numpy array (2D), the normalised image
    """
    # create storage for median-filtered flat image
    image_med = np.zeros_like(image)
    # must be forced to a native-ordered copy of the image for the median
    # filter to work properly
    image = np.array(image, dtype=np.float64)
    # loop around x axis
    for i_it in range(image.shape[1]):
        # x-spatial filtering and insert filtering into image_med array
        image_med[i_it, :] = filters.median_filter(image[i_it, :], wmed)

    if method == 'new':
        # get the Nth percentile of median image
        norm = mp.nanpercentile(image_med[np.isfinite(image_med)], percentile)
    else:
        v = image_med.reshape(np.prod(image.shape))
        v = np.sort(v)
        norm = v[int(np.prod(image.shape) * percentile / 100.0)]

    # apply to flat_med and flat_ref
    return image_med / norm, image / norm


def locate_bad_pixels(fimage: np.ndarray, fmed: np.ndarray,
                      dimage: np.ndarray, wmed: float, cut_ratio: float,
                      illum_cut: float, max_hotpix: float
                      ) -> Tuple[np.ndarray, List[float]]:
    """
    Locate the bad pixels in the flat image and the dark image

    :param fimage: numpy array (2D), the flat normalised image
    :param fmed: numpy array (2D), the flat median normalised image
    :param dimage: numpy array (2D), the dark image
    :param wmed: float, the median filter width used to remove residual
                scattered light/thermal background from the dark image
    :param cut_ratio: float, the maximum differential pixel cut ratio
    :param illum_cut: float, the illumination cut parameter, below this
                      value only the dark current is used to decide a pixel
                      is "bad"
    :param max_hotpix: float, the maximum flux in ADU/s to be considered too
                       hot to be used

    :returns: tuple, 1. bad_pix_mask: numpy array (2D), the bad pixel mask
                        image
                     2. badpix_stats: list of floats, the statistics array:
                            Fraction of hot pixels from dark [%]
                            Fraction of bad pixels from flat [%]
                            Fraction of NaN pixels in dark [%]
                            Fraction of NaN pixels in flat [%]
                            Fraction of bad pixels with all criteria [%]
    """
    if dimage.shape != fimage.shape:
        emsg = ('flat image and dark image do not have the same dimensions '
               '({0} vs {1})')
        raise ValueError(emsg.format(fimage.shape, dimage.shape))
    # -------------------------------------------------------------------------
    # create storage for ratio of flat_ref to flat_med
    fratio = np.zeros_like(fimage)
    # create storage for bad dark pixels
    badpix_dark = np.zeros_like(dimage, dtype=bool)
    # -------------------------------------------------------------------------
    # must be forced to a native-ordered copy of the image for the median
    # filter to work properly
    dimage = np.array(dimage, dtype=np.float64)
    # as there may be a small level of scattered light and thermal
    # background in the dark  we subtract the running median to look
    # only for isolate hot pixels
    for i_it in range(fimage.shape[1]):
        dimage[i_it, :] -= filters.median_filter(dimage[i_it, :], wmed)
    # work out how much do flat pixels deviate compared to expected value
    zmask = fmed != 0
    fratio[zmask] = fimage[zmask] / fmed[zmask]
    # catch the warnings
    with warnings.catch_warnings(record=True) as _:
        # if illumination is low, then consider pixel valid for this criterion
        fratio[fmed < illum_cut] = 1
    # catch the warnings
    with warnings.catch_warnings(record=True) as _:
        # where do pixels deviate too much
        badpix_flat = (np.abs(fratio - 1)) > cut_ratio
    # -------------------------------------------------------------------------
    # get finite flat pixels
    valid_flat = np.isfinite(fimage)
    # -------------------------------------------------------------------------
    # get finite dark pixels
    valid_dark = np.isfinite(dimage)
    # -------------------------------------------------------------------------
    # select pixels that are hot
    badpix_dark[valid_dark] = dimage[valid_dark] > max_hotpix
    # -------------------------------------------------------------------------
    # construct the bad pixel mask
    badpix_map = badpix_flat | badpix_dark | ~valid_flat | ~valid_dark
    # -------------------------------------------------------------------------
    # calculate stats
    badpix_stats = [(np.sum(badpix_dark) / np.array(badpix_dark).size) * 100,
                    (np.sum(badpix_flat) / np.array(badpix_flat).size) * 100,
                    (np.sum(~valid_dark) / np.array(valid_dark).size) * 100,
                    (np.sum(~valid_flat) / np.array(valid_flat).size) * 100,
                    (np.sum(badpix_map) / np.array(badpix_map).size) * 100]
    # -------------------------------------------------------------------------
    # return bad pixel map
    return badpix_map, badpix_stats


def full_flat_badpix_mask(mdata: np.ndarray, rotnum: int,
                          threshold: float) -> np.ndarray:
    """
    Compute the bad pixel mask from the full engineering flat reference
    image

    :param mdata: numpy array (2D), the full engineering flat reference data
    :param rotnum: int, the rotation to apply to the reference data (see
                   aperocore.math.rot8)
    :param threshold: float, the threshold on the engineering flat above
                      which the data is considered good

    :return: numpy array (2D) of bool, the bad pixel mask (True = bad pixel)
    """
    # apply threshold
    mask = np.abs(mp.rot8(mdata, rotnum) - 1) > threshold
    # return mask
    return mask
