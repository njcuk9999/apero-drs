#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flat and blaze calibration science functions

Pure numerical routines used to fit the blaze/flat sinc model and to
characterise the flux at the edges of the order trace. These functions do
not load APERO profiles or depend on apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import List, Tuple

import numpy as np
from scipy.optimize import curve_fit

from aperocore.base import base
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.calib.flat_blaze_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

blaze_flat_return = Tuple[np.ndarray, np.ndarray, np.ndarray, float]


# =============================================================================
# Define functions
# =============================================================================
def calculate_blaze_flat_sinc(e2ds_ini: np.ndarray, peak_cut: float,
                              badpercentile: float, med_size: int
                              ) -> blaze_flat_return:
    """
    Calculate the blaze function using a sinc function

    :param e2ds_ini: numpy (1D) array: the extracted flux for this order
    :param peak_cut: float, the threshold expressed as the fraction of the
                     maximum peak, below this threshold the blaze is set to
                     NaN
    :param badpercentile: float, the hot pixel percentile level
    :param med_size: int, the sinc fit median filter width

    :return: tuple, 1. the updated extracted flux for this order
             2. the flat profile for this order
             3. the blaze fit for this order
             4. the rms for this order

    :raises RuntimeError: if the sinc fit fails after all fallback attempts
    """
    # ----------------------------------------------------------------------
    # defnie the x positions
    xpix = np.arange(len(e2ds_ini))
    # ------------------------------------------------------------------
    # Need to median filter the e2ds here as we want to fit the shape not
    #   individual line shapes for the blaze
    e2ds = mp.medfilt_1d(e2ds_ini, med_size)
    # region over which we will fit
    keep = np.isfinite(e2ds)
    # keep only regions that make sense compared to the 95th percentile
    #   max would be affected by outliers
    with warnings.catch_warnings(record=True) as _:
        keep &= e2ds > 0.05 * mp.nanpercentile(e2ds, 95)
        keep &= e2ds < 2 * mp.nanpercentile(e2ds, 95)
    # ------------------------------------------------------------------
    # guess of peak value, we do not take the max as there may be a
    #     hot/bad pix in the order
    thres = mp.nanpercentile(e2ds, badpercentile)
    # ------------------------------------------------------------------
    # how many points above 50% of peak value?
    # The period should be a factor of about 2.0 more than the domain
    # that is above the 5th percentile
    nthres = mp.nansum(e2ds[keep] > thres / 2.0)
    # median position of points above threshold
    with warnings.catch_warnings(record=True) as _:
        pospeak = mp.nanmedian(xpix[e2ds > thres])
    # ------------------------------------------------------------------
    # starting point for the fit to the blaze sinc model
    # we start with :
    #
    # peak value is == threshold percentile
    # period of sinc is == 2x the width of pixels above 50% of the peak
    # the peak position is == the median x value of pixels above
    #                         95th percent.
    # no quadratic term
    # no SED slope
    fit_guess = [thres, nthres * 2.0, pospeak, 0, 0, 0]
    # ------------------------------------------------------------------
    # we set reasonable bounds
    # pass without DC and SLOPE
    bounds = [(0, 0.0, 0.0, -np.inf, -np.inf, -1e-20),
              (thres * 1.5, np.inf, np.max(xpix), np.inf, np.inf, 1e-20)]
    # set a counter
    n_it = -1
    # -------------------------------------------------------------------------
    # try a few times (this can fix it not working)
    tries = 0
    popt, pcov = [], []
    while tries <= 5:
        # try to fit and if there is a failure catch it
        try:
            # we optimize over pixels that are not NaN
            # noinspection PyTupleAssignmentBalance
            popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                   p0=fit_guess, bounds=bounds)
            # we then re-fit to avoid local minima (this has happened - fitting
            #   a second time seemed to fix this - when the guess is off)
            # noinspection PyTupleAssignmentBalance
            popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=popt,
                                   bounds=bounds)
            # worked --> break while loop
            break
        except RuntimeError as _:
            # if it failed with bounds try without bounds
            try:
                # we optimize over pixels that are not NaN (this time with
                # no bounds)
                # noinspection PyTupleAssignmentBalance
                popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                       p0=fit_guess)
                # we then re-fit to avoid local minima (this has happened
                #    - fitting a second time seemed to fix this
                #    - when the guess is off)
                # noinspection PyTupleAssignmentBalance
                popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=popt)
                # worked --> break while loop
                break
            except RuntimeError as _:
                # finally try without the cubic term
                try:
                    fit_guess1 = fit_guess[:5]
                    # we optimize over pixels that are not NaN (this time with
                    #    no bounds)
                    # noinspection PyTupleAssignmentBalance
                    popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                           p0=fit_guess1)
                    # worked --> break while loop
                    break
                except RuntimeError as e:
                    # try again (this can fix it not working)
                    if tries < 5:
                        tries += 1
                    # on the 5th attempt give up
                    if tries == 5:
                        strlist = ('amp={0} period={1} lin={2} slope={3} '
                                   'quad={4} (cube={5})')
                        strguess = strlist.format(*fit_guess)
                        strlower = strlist.format(*bounds[0])
                        strupper = strlist.format(*bounds[1])
                        raise RuntimeError(strguess, strlower, strupper,
                                          type(e).__name__, str(e))
    # ------------------------------------------------------------------
    # calculate the blaze from the curve_fit coefficients
    blaze = mp.sinc(xpix, *popt, peak_cut=peak_cut)
    # ----------------------------------------------------------------------
    # remove nan in the blaze also in the e2ds
    # ----------------------------------------------------------------------
    blazemask = np.isnan(blaze)
    e2ds_ini[blazemask] = np.nan
    # calculate the flat
    with warnings.catch_warnings(record=True) as _:
        flat = e2ds_ini / blaze
    # ----------------------------------------------------------------------
    # calculate the rms
    # ----------------------------------------------------------------------
    rms = mp.robust_nanstd(flat[keep])
    # remove any very large outliers (set to NaN)
    with warnings.catch_warnings(record=True) as _:
        bad_mask1 = np.abs(flat - 1) > 10 * rms
        # apply mask
        flat[bad_mask1] = np.nan
        blaze[bad_mask1] = np.nan
        e2ds_ini[bad_mask1] = np.nan
    # ----------------------------------------------------------------------
    # remove outliers within flat field to avoid division by small numbers
    #   or suspiciously large flat response
    with warnings.catch_warnings(record=True) as _:
        bad_mask2 = np.abs(1 - flat) > 0.2
        # apply mask
        flat[bad_mask2] = np.nan
        blaze[bad_mask2] = np.nan
        e2ds_ini[bad_mask1] = np.nan
    # ----------------------------------------------------------------------
    # If the blaze is below 0.25 we consider that the blaze and flat correction
    # are not reliable
    with warnings.catch_warnings(record=True) as _:
        bad_mask3 = blaze < 0.25 * np.nanmax(blaze)
        flat[bad_mask3] = np.nan
        blaze[bad_mask3] = np.nan
        e2ds_ini[bad_mask3] = np.nan
    # ----------------------------------------------------------------------
    # recalculate calculate the rms
    # ----------------------------------------------------------------------
    rms = mp.robust_nanstd(flat[keep])
    # ----------------------------------------------------------------------
    # return values
    return e2ds_ini, flat, blaze, rms


def flux_edge_trace(e2ds: np.ndarray, e2dsll: np.ndarray, mid_size: int,
                    ignore_orders: List[int], flux_edge_limit: float
                    ) -> Tuple[np.ndarray, np.ndarray, float, List[int]]:
    """
    Calculate the flux at the edges of the trace

    :param e2ds: numpy (2D) array, the extracted 2D spectrum (used only for
                the number of orders)
    :param e2dsll: numpy (2D) array, the per-pixel (unbinned) extracted flux
    :param mid_size: int, the half-width of the region (in pixels) around
                     the center of the array used to compute the median
                     trace profile
    :param ignore_orders: list of int, orders to ignore (set to NaN) when
                          computing the edge flux
    :param flux_edge_limit: float, the edge flux value above which an order
                            is considered to have failed

    :return: tuple, 1. numpy array, the per-order normalized median trace
                profile
             2. numpy array, the total edge flux for each order
             3. float, the maximum edge flux across all orders
             4. list of int, the orders whose edge flux is above
                flux_edge_limit
    """
    # get the number of orders
    norders = e2ds.shape[0]
    # find the middle of the array
    mid = e2dsll.shape[1] // 2
    # -------------------------------------------------------------------------
    # median trace profile of the center of the image
    med = np.nanmedian(e2dsll[:, mid - mid_size:mid + mid_size], axis=1)
    # reshape the median profile to have the number of orders
    med = med.reshape(norders, med.shape[0] // norders)
    # -------------------------------------------------------------------------
    # normalize each order to a mean of 1
    for order_num in range(norders):
        segment = med[order_num]
        med[order_num] /= np.nansum(segment)
    # -------------------------------------------------------------------------
    # we find the flux at the edges of the trace for each order. The total
    # edge flux should be small and account for <1% of the total flux.
    flux_left = med[:, 0]
    flux_right = med[:, -1]
    # set ignore orders to nans
    cut_mask = np.isin(np.arange(norders), ignore_orders)
    # set these orders to NaN
    flux_left[cut_mask] = np.nan
    flux_right[cut_mask] = np.nan
    # get the total edge flux
    flux_edge = flux_left + flux_right
    # -------------------------------------------------------------------------
    # store the orders with flux greater than limit
    failed = (flux_edge > flux_edge_limit) & np.isfinite(flux_edge)
    failed_orders = list(np.where(failed)[0])
    # get the maximum edge flux across all orders
    max_edge_flux = np.nanmax(flux_edge)
    # -------------------------------------------------------------------------
    # return normalized trace, max edge flux and list of failed orders
    return med, flux_edge, float(max_edge_flux), failed_orders
