#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Order extraction science functions

Pure numerical routines for extracting 1D spectra from a straightened 2D
image using the order profile weighting method (with cosmic ray
rejection), plus small helper functions used to validate/parse extraction
setup values. These functions do not load APERO profiles or depend on
apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from aperocore.base import base
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.extract.extract_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def extraction(simage: np.ndarray, orderp: np.ndarray, pos: np.ndarray,
               r1: float, r2: float, cosmic_sigcut: float
               ) -> Tuple[np.ndarray, np.ndarray, int, np.ndarray]:
    """
    Extract order using tilt and weight (sigdet and badpix) and cosmic
    correction

    Same as extract_tilt_weight but slow (does NOT assume that rounded
    separation between extraction edges is constant along order)

    :param simage: numpy array (2D), the debananafied image (straightened
                   image)
    :param orderp: numpy array (2D), the image with fit superposed (zero
                   filled)
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param r1: float, the distance away from center to extract out to (top)
               across the orders direction
    :param r2: float, the distance away from center to extract out to
               (bottom) across the orders direction
    :param cosmic_sigcut: float, the sigma cut for cosmic rays

    :return: tuple, 1. numpy array (1D), the extracted pixel values, size =
             image.shape[1] (along the order direction), 2. numpy array
             (2D), the per-pixel weighted slice values, 3. int, the number
             of cosmic rays found, 4. numpy array (2D), the cosmic ray
             weights used for each pixel
    """
    dim1, dim2 = simage.shape
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    jcs = np.full(dim2, mp.val_cheby(pos, dim2 // 2, domain=[0, dim2]))
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - r1
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + r2
    # TODO: Note we still miss the top and bottom
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # create a slice image
    spelong = np.zeros((mp.nanmax(j2s - j1s) + 1, dim2), dtype=float)
    coslong = np.zeros((mp.nanmax(j2s - j1s) + 1, dim2), dtype=float)
    # define the number of cosmics found
    cpt = 0
    # loop around each pixel along the order
    with warnings.catch_warnings(record=True) as _:
        for ic in ics:
            if mask[ic]:
                # get the image slice
                sx = simage[j1s[ic]:j2s[ic] + 1, ic]
                # get hte order profile slice
                fx = orderp[j1s[ic]:j2s[ic] + 1, ic]
                # Renormalise the rotated order profile
                sumfx = mp.nansum(fx)
                if sumfx > 0:
                    fx = fx / sumfx
                else:
                    fx = np.ones(fx.shape, dtype=float)
                # get the amplitude (ratio between flux and flat)
                amp = mp.nanmedian(sx / fx)
                # residuals
                res = sx - fx * amp
                # work out number of sigma away from the median res
                ares = np.abs(res)
                nsig = ares / mp.nanmedian(ares)
                # work out weights (0 or 1 based on number of sigma)
                # TODO: Look at this later for the narrow NIRPS fiber
                if (r1 + r2) > 10:
                    weights = nsig < cosmic_sigcut
                else:
                    weights = np.isfinite(nsig)
                # add to the number of rejected cosmics
                cpt += np.sum(~weights)
                # weights to floats
                weights_float = np.array(weights).astype(float)
                # some matrix manipulation
                wsxfx = weights_float * sx * fx
                wfxfx = weights_float * fx ** 2
                sum_wfxfx = mp.nansum(wfxfx)
                # set the value of this pixel to the weighted sum
                spelong[:, ic] = wsxfx
                # nan the cosmic rays (to keep it consistent with spe)
                spelong[:, ic][~weights] = np.nan
                # collapse spectrum
                spe[ic] = mp.nansum(wsxfx)
                # normalise spe
                spe[ic] = spe[ic] / sum_wfxfx
                spelong[:, ic] = spelong[:, ic] / sum_wfxfx
                coslong[:, ic] = weights_float

    return spe, spelong, cpt, coslong


def calculate_snr(e2ds: np.ndarray, blaze_width: int, r1: float, r2: float,
                  eff_ron: float) -> Tuple[float, float]:
    """
    Calculate the signal to noise ratio for one extracted order

    :param e2ds: numpy array (1D), the extracted order
    :param blaze_width: int, the half-width of the window (around the
                        center of the order) used to measure the flux
    :param r1: float, the distance away from center extracted to (top)
    :param r2: float, the distance away from center extracted to (bottom)
    :param eff_ron: float, the effective readout noise

    :return: tuple, 1. float, the signal to noise ratio, 2. float, the
             average flux in the blaze window
    """
    # get the central pixel position
    cent_pos = int(len(e2ds) / 2)
    # get the blaze window size
    blaze_lower = cent_pos - blaze_width
    blaze_upper = cent_pos + blaze_width
    # get the average flux in the blaze window
    flux = mp.nansum(e2ds[blaze_lower:blaze_upper] / (2 * blaze_width))
    # calculate the noise
    noise = eff_ron * np.sqrt(r1 + r2)
    # calculate the snr ratio = flux / sqrt(flux + noise**2)
    snr = flux / np.sqrt(flux + noise ** 2)
    # return snr
    return snr, flux


def cosmic_correction(sx: np.ndarray, spe: np.ndarray, fx: np.ndarray,
                      ic: int, weights: np.ndarray, cpt: int,
                      cosmic_sigcut: float, cosmic_threshold: int
                      ) -> Tuple[np.ndarray, int]:
    """
    Calculate the cosmic correction

    :param sx: numpy array (1D), the raw extracted "ic"th order pixels
    :param spe: numpy array (1D), the output extracted order for the
                "ic"th pixels
    :param fx: numpy array (1D), the extracted order_profile for the
               "ic" the pixels
    :param ic: int, the iterator for this central x-pixel (for this order)
    :param weights: numpy array (1D), the weight array for the "ic"th
                    order pixels
    :param cpt: int, the number of cosmic rays found
    :param cosmic_sigcut: float, the sigma cut for cosmic rays
    :param cosmic_threshold: int, the number of allowed cosmic rays per
                             corr

    :return: tuple, 1. numpy array (1D), the extracted pixel values, size
             = image.shape[1] (along the order direction), 2. int, the
             number of cosmic rays found
    """
    # define the critical pixel values?
    crit = (sx - spe[ic] * fx)
    # re-cast the sigcut parameters
    sigcut = cosmic_sigcut  # 25% of the flux
    # start the loop counter
    nbloop = 0
    # loop around until either:
    #       critical pixel values > sigcut * extraction
    #    or
    #       the loop exceeds "cosmic_threshold"
    cond1 = mp.nanmax(crit) > mp.nanmax([sigcut * spe[ic], 1000.0])
    cond2 = nbloop < cosmic_threshold
    while cond1 and cond2:
        # define the cosmic ray mask (True where not cosmic ray)
        cosmask = ~(crit > mp.nanmax(crit) - 0.1)
        # set the pixels where there is a cosmic ray to zero
        part1 = weights * cosmask * sx * fx
        part2 = weights * cosmask * fx ** 2
        spe[ic] = mp.nansum(part1) / mp.nansum(part2)
        # recalculate the critical parameter
        crit = (sx * cosmask - spe[ic] * fx * cosmask)
        # increase the number of found cosmic rays by 1
        cpt += 1
        # increase the loop counter
        nbloop += 1
        # recalculate conditions
        cond1 = mp.nanmax(crit) > mp.nanmax([sigcut * spe[ic], 1000.0])
        cond2 = nbloop < cosmic_threshold

    # finally return spe and cpt
    return spe, cpt


def valid_orders(start_order: int, end_order: int,
                 skip_orders: Optional[List[int]] = None) -> List[int]:
    """
    Construct the list of valid (non-skipped) order numbers

    :param start_order: int, the first order number to use
    :param end_order: int, the last order number to use
    :param skip_orders: list of int or None, orders to skip

    :return: list of int, the valid order numbers

    :raises ValueError: if start_order/end_order cannot be cast to int, if
             start_order is negative, if start_order > end_order, or if
             skip_orders cannot be cast to a list of int
    """
    # push start and end to ints
    try:
        start_order = int(start_order)
    except Exception as e:
        emsg = 'start_order={0} must be an int: {1}: {2}'
        raise ValueError(emsg.format(start_order, type(e), e))
    try:
        end_order = int(end_order)
    except Exception as e:
        emsg = 'end_order={0} must be an int: {1}: {2}'
        raise ValueError(emsg.format(end_order, type(e), e))
    # start order must be zero or greater
    if start_order < 0:
        emsg = 'start_order={0} must be zero or greater'
        raise ValueError(emsg.format(start_order))
    # check that start order is less than end order
    if start_order > end_order:
        emsg = 'start_order={0} must be less than end_order={1}'
        raise ValueError(emsg.format(start_order, end_order))
    # deal with skip orders
    if not isinstance(skip_orders, list):
        skip_orders = []
    else:
        try:
            skip_orders = np.array(skip_orders).astype(float).astype(int)
        except Exception as e:
            emsg = 'skip_orders={0} must be a list of int: {1}: {2}'
            raise ValueError(emsg.format(skip_orders, type(e), e))
    # define storage
    v_orders = []
    # loop around orders
    for order_num in range(start_order, end_order + 1):
        if order_num in skip_orders:
            continue
        else:
            v_orders.append(order_num)
    # return valid orders
    return v_orders


def get_range(rangedict: Dict[str, Union[int, float, str]], fiber: str
             ) -> float:
    """
    Get the range value for a given fiber from a fiber-keyed range
    dictionary

    :param rangedict: dict, the range value for each fiber
    :param fiber: str, the fiber name

    :return: float, the range value for this fiber

    :raises ValueError: if rangedict is not a dict, if fiber is not in
             rangedict, or if the range value cannot be cast to a float
    """
    if not isinstance(rangedict, dict):
        emsg = 'rangedict must be a dict, got {0}'
        raise ValueError(emsg.format(type(rangedict)))
    # deal with fiber not being in range dictionary
    if fiber not in rangedict:
        emsg = 'fiber={0} not in rangedict={1}'
        raise ValueError(emsg.format(fiber, rangedict))
    else:
        try:
            # return range value
            return float(rangedict[fiber])
        except Exception as e:
            emsg = 'rangedict[{0}]={1} must be a float: {2}: {3}'
            raise ValueError(emsg.format(fiber, rangedict[fiber], type(e), e))


def measure_p2p_scat(wavemap: np.ndarray, e2ds: np.ndarray, blaze_width: int,
                     bands: Dict[str, Tuple[float, float]]
                     ) -> Dict[str, Union[np.ndarray, Dict[str, float]]]:
    """
    Calculate an estimate of the measured peak-to-peak scatter for a given
    e2ds per order and in some photometric bands

    this is measured from the point to point scatter inside the blaze
    window

    :param wavemap: numpy array (2D), the wavelength map for the e2ds
    :param e2ds: numpy array (2D), the extracted order
    :param blaze_width: int, the width of the blaze window
    :param bands: dict, maps a band name to a (wave_min, wave_max) tuple

    :return: dict, with 'MP2P' (numpy array, the per-order point to point
             scatter) and 'BP2P' (dict, the per-band point to point
             scatter)
    """
    # set up output properties
    sprops = dict()
    # return array
    snrs = np.full(e2ds.shape[0], fill_value=np.nan)
    # loop in order number
    for order_num in range(e2ds.shape[0]):
        # get the central pixel position
        cent_pos = int(len(e2ds[order_num]) / 2)
        # get the blaze window size
        blaze_lower = cent_pos - blaze_width
        blaze_upper = cent_pos + blaze_width
        # get the flux in the blaze window
        e2ds_bw = e2ds[order_num][blaze_lower:blaze_upper]
        # get the average flux in the blaze window
        with warnings.catch_warnings(record=True) as _:
            medflux = mp.nanpercentile(e2ds_bw, 90)
        # don't continue if we have no med flux (order center is empty)
        if not np.isfinite(medflux):
            continue
        # get the point to point flux for the noise estimate
        roll1 = (np.roll(e2ds_bw, 1) + np.roll(e2ds_bw, -1)) / 2
        # TODO: kw comment:   STD of spectrum + (mean of spectrum - 1)
        point2point = e2ds_bw - roll1
        # calculate the noise
        noise = mp.estimate_sigma(point2point) / np.sqrt(1.5)
        # calculate the snr ratio
        snr = medflux / noise
        # add to vector
        snrs[order_num] = snr
    # add to sprops
    sprops['MP2P'] = snrs
    # -------------------------------------------------------------------------
    # now work out per band SNRs
    # -------------------------------------------------------------------------
    # storage in sprops
    sprops['BP2P'] = dict()
    # get the mean wavelength per order
    waveord = np.nanmean(wavemap, axis=1)
    # loop around bands
    for iband in bands.keys():
        # get the band limits
        band = bands[iband]
        # make a mask of the orders for this band
        band_mask = (waveord > band[0]) & (waveord < band[1])
        # get the mean snr for this band
        band_snr = np.nanmean(snrs[band_mask])
        # push into sprops
        sprops['BP2P'][iband] = band_snr
    # return the snr
    return sprops
