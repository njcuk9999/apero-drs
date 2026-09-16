#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Telluric science functions

Pure numerical routines used by the telluric-correction recipes: blaze
normalisation, the iterative sigma-clipped transmission model fit, and
sky-emission-line region identification. These functions do not load
APERO profiles or depend on apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import Tuple

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion

from aperocore.base import base
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.telluric.telluric_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def normalise_by_pblaze(image: np.ndarray, blaze: np.ndarray,
                        blaze_p: float, cut_blaze_norm: float
                        ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Normalise an e2ds image by its blaze, itself normalised by the blaze
    percentile per order

    :param image: numpy array (2D), the e2ds image to normalise
    :param blaze: numpy array (2D), the blaze image
    :param blaze_p: float, the percentile of the blaze used to normalise
                    each order
    :param cut_blaze_norm: float, the normalised-blaze level below which
                           pixels are considered bad (set to NaN)

    :return: tuple, 1. numpy array (2D), the blaze-normalised image,
             2. numpy array (2D), the normalised blaze (bad pixels are NaN)
    """
    # copy the image
    image1 = np.array(image)
    # copy blaze
    blaze_norm = np.array(blaze)
    # loop through blaze orders, normalize blaze by its peak amplitude
    for order_num in range(image1.shape[0]):
        # normalize the spectrum
        spo, bzo = image1[order_num], blaze[order_num]
        # normalise image
        image1[order_num] = spo / mp.nanpercentile(spo, blaze_p)
        # normalize the blaze
        blaze_norm[order_num] = bzo / mp.nanpercentile(bzo, blaze_p)
    # ----------------------------------------------------------------------
    # find where the blaze is bad
    with warnings.catch_warnings(record=True) as _:
        badblaze = blaze_norm < cut_blaze_norm
    # ----------------------------------------------------------------------
    # set bad blaze to NaN
    blaze_norm[badblaze] = np.nan
    # set to NaN values where spectrum is zero
    zeromask = image1 == 0
    image1[zeromask] = np.nan
    # divide spectrum by blaze
    with warnings.catch_warnings(record=True) as _:
        image1 = image1 / blaze_norm
    # return the normalised image and normalised blaze
    return image1, blaze_norm


def make_trans_model(transcube: np.ndarray, expo_water: np.ndarray,
                     expo_others: np.ndarray, sigma_cut: float,
                     min_trans_files: int
                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fit a per-pixel linear model (bias + water absorption + other
    absorption) to a cube of log-transmission maps, iteratively rejecting
    the worst outlier observation until none exceeds sigma_cut

    :param transcube: numpy array (3D), the log-transmission maps, shape
                      (norders, npix, ntransfiles)
    :param expo_water: numpy array (1D), the water absorption exponent for
                       each transmission file
    :param expo_others: numpy array (1D), the other-species absorption
                        exponent for each transmission file
    :param sigma_cut: float, the sigma-clip threshold for outlier rejection
    :param min_trans_files: int, the minimum number of transmission files
                            required to fit a given pixel

    :return: tuple, 1. numpy array (2D), the fitted bias (zero-point)
             residual per pixel, 2. numpy array (2D), the fitted water
             absorption residual per pixel, 3. numpy array (2D), the
             fitted other-species absorption residual per pixel
    """
    # get a reference trans file from cube (first trans file)
    ref_trans = transcube[:, :, 0]
    # -------------------------------------------------------------------------
    # sample vectors for the reconstruction
    sample = np.zeros([3, len(expo_water)])
    # bias level of the residual
    sample[0] = 1
    # water abso
    sample[1] = expo_water
    # dry abso
    sample[2] = expo_others
    # -------------------------------------------------------------------------
    # create the reference vectors
    zero_residual = np.full_like(ref_trans, np.nan)
    expo_water_residual = np.full_like(ref_trans, np.nan)
    expo_others_residual = np.full_like(ref_trans, np.nan)
    # loop around all orders
    for order_num in range(ref_trans.shape[0]):
        # loop around all pixels in order
        for ix in range(ref_trans.shape[1]):
            # get one pixel of the trans_cube for all observations
            trans_slice = transcube[order_num, ix, :]
            # deal with not having enough pixels (skip)
            if np.sum(np.isfinite(trans_slice)) < min_trans_files:
                continue
            # if we can all zero values skip
            if mp.nansum(trans_slice) == 0:
                continue
            # construct a linear model with offset and water+dry components
            worst_offender = np.inf
            # loop until no point is an outlier beyond "sigma cut" sigma
            while worst_offender > sigma_cut:
                # get the linear minimization between trans files and our
                # sample
                # noinspection PyBroadException
                try:
                    amp, recon = mp.linear_minimization(trans_slice, sample)
                except Exception as _:
                    break
                # work out the sigma between trans slice and recon
                res = trans_slice - recon
                est_sig = mp.estimate_sigma(res)
                sigma = res / est_sig
                # re-calculate worst offender
                worst_pos = mp.nanargmax(sigma)
                worst_offender = sigma[worst_pos]
                # deal with worst offender - remove worst
                if worst_offender > sigma_cut:
                    trans_slice[worst_pos] = np.nan
                # else we are good - push values into output vectors
                else:
                    zero_residual[order_num, ix] = amp[0]
                    expo_water_residual[order_num, ix] = amp[1]
                    expo_others_residual[order_num, ix] = amp[2]
                # recalculate the size of trans_slice
                num = np.sum(np.isfinite(trans_slice))
                # if we have less than the minimum number of points left
                #   stop here
                if num < min_trans_files:
                    break
    # -------------------------------------------------------------------------
    return zero_residual, expo_water_residual, expo_others_residual


def identify_sky_line_regions(wave1d: np.ndarray, sky_med: np.ndarray,
                              line_sigma: float, erode_size: int,
                              dilate_size: int, wavestart: float,
                              waveend: float, binvelo: float) -> np.ndarray:
    """
    Identify contiguous sky-emission-line regions in a median sky
    spectrum, and label them (order-overlap aware, via a common
    velocity/"magic" grid)

    :param wave1d: numpy array (1D), the (raveled) e2ds wavelength map
    :param sky_med: numpy array (1D), the median sky spectrum (raveled,
                    same shape as wave1d)
    :param line_sigma: float, the number of sigma above the noise a pixel
                       must be to be considered part of a line
    :param erode_size: int, the binary erosion structure size used to
                       remove features that are too narrow
    :param dilate_size: int, the binary dilation structure size used to
                        recover the wings of a line
    :param wavestart: float, the start wavelength of the magic grid
    :param waveend: float, the end wavelength of the magic grid
    :param binvelo: float, the magic grid bin width, in km/s

    :return: numpy array (1D) of int, same shape as wave1d, the region ID
             for each pixel (0 = not part of any region)
    """
    # set all NaN values to zero
    sky_med = np.array(sky_med)
    sky_med[~np.isfinite(sky_med)] = 0.0
    # find positive excursions in sky signal
    nsig = sky_med / mp.estimate_sigma(sky_med)
    # identify lines that are n sigma positive excursions
    line = np.array(nsig > line_sigma, dtype=int)
    # erode features that are too narrow
    line = binary_erosion(line, structure=np.ones(erode_size))
    # dilate to get wings of lines
    line = binary_dilation(line, structure=np.ones(dilate_size))
    # build the region mask
    regions = np.cumsum(line != np.roll(line, 1))
    # set all the even regions to zero
    regions[(regions % 2) == 0] = 0
    # re-number all non-zero regions to produce labels from 1--> N
    #   (original were all the odd numbers)
    non_zero = regions != 0
    regions[non_zero] = (regions[non_zero] + 1) // 2
    # velocity grid in round numbers of m / s
    magic_grid = mp.get_magic_grid(wavestart, waveend, binvelo * 1000)
    # put the line mask onto the magic grid to avoid errors at order overlaps
    magic_mask = np.zeros_like(magic_grid, dtype=bool)
    # find unique valid regions
    valid_regions = set(regions)
    valid_regions.remove(0)
    # loop around regions and fill magic mask
    for region in valid_regions:
        # find pixels that are in this region
        good = regions == region
        # find mask of minimum and maximum wavelength for this region
        minmask = magic_grid > np.min(wave1d[good])
        maxmask = magic_grid < np.max(wave1d[good])
        magic_mask[minmask & maxmask] = True
    # now in the space of magic grid work out the regions
    # build the region mask
    regions_magic = np.cumsum(magic_mask != np.roll(magic_mask, 1))
    # set all the even regions to zero
    regions_magic[(regions_magic % 2) == 0] = 0
    # re-number all non-zero regions to produce labels from 1--> N
    #   (original were all the odd numbers)
    non_zero_magic = regions_magic != 0
    regions_magic[non_zero_magic] = (regions_magic[non_zero_magic] + 1) // 2
    # fill the original map with unique values and common ID for overlapping
    #   orders
    regions = np.zeros_like(regions, dtype=int)
    # find unique valid regions
    valid_regions = set(regions_magic)
    valid_regions.remove(0)
    # loop around regions and fill
    for region in valid_regions:
        wave_min = np.min(magic_grid[regions_magic == region])
        wave_max = np.max(magic_grid[regions_magic == region])
        # find valid pixels in wavelength
        good = (wave1d > wave_min) & (wave1d < wave_max)
        # update the region id for these good pixels
        regions[good] = region
    # return updated region id map
    return regions
