#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO order localisation (order centers and order widths) functionality

Created on 2019-05-15 at 13:48

@author: cook
"""
import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.ndimage import percentile_filter, binary_dilation
from scipy.ndimage.filters import median_filter
from skimage import measure

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_database
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_recipe
from apero.io import drs_table
from apero.science.calib import gen_calib

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.localisation.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
# get the calibration database
CalibrationDatabase = drs_database.CalibrationDatabase
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
def calculate_order_profile(params: ParamDict, image: np.ndarray,
                            box_size: Optional[int] = None) -> np.ndarray:
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param params: ParamDict, the parameter dictionary of constants
    :param image: numpy array (2D), the image
    :param box_size: int, the number of pixels to mask before and after pixel
                     (for every row), if set overrides "LOC_ORDERP_BOX_SIZE"
                     from params

    :return newimage: numpy array (2D), the smoothed image
    """
    func_name = __NAME__ + '.calculate_order_profile()'
    # get constants from params
    size = pcheck(params, 'LOC_ORDERP_BOX_SIZE', func=func_name,
                  override=box_size)
    # -------------------------------------------------------------------------
    # log that we are creating order profile
    WLOG(params, '', textentry('40-013-00001'))
    # -------------------------------------------------------------------------
    # copy the original image
    newimage = np.zeros_like(image)
    # loop around each pixel column
    for it in range(0, image.shape[1], 1):
        # ------------------------------------------------------------------
        # deal with leading edge --> i.e. box expands until it is full size
        if it < size:
            # get the subimage defined by the box for all rows
            part = image[:, 0:it + size + 1]
        # deal with main part (where box is of size="size"
        elif size <= it <= image.shape[1] - size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size: it + size + 1]
        # deal with the trailing edge --> i.e. box shrinks from full size
        elif it > image.shape[1] - size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size:]
        # else we have zeros (shouldn't happen)
        else:
            part = np.zeros_like(image)
        # ------------------------------------------------------------------
        # apply the weighted mean for this column
        with warnings.catch_warnings(record=True) as _:
            newimage[:, it] = mp.nanmedian(part, axis=1)
    # return the new smoothed image
    return newimage


def calc_localisation(params: ParamDict, recipe: DrsRecipe, image: np.ndarray,
                      fiber: str, binsize: Optional[int] = None,
                      boxp_low: Optional[float] = None,
                      boxp_high: Optional[float] = None,
                      percentile_fsize: Optional[float] = None,
                      fdilate_itr: Optional[int] = None,
                      min_order_area: Optional[int] = None,
                      cent_poly_deg: Optional[int] = None,
                      wid_poly_deg: Optional[int] = None,
                      range_wid_sum: Optional[int] = None,
                      loc_ydet_min: Optional[int] = None,
                      loc_ydet_max: Optional[int] = None,
                      num_wsamples: Optional[int] = None,
                      ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find and fit the orders for this order based on the "image" (order profile)

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DreRecipe instance, the recipe that called this function
    :param image: np.array (2D), the image to fit the orders on
    :param fiber: str, the fiber name (i.e. 'A', 'B' or 'C')
    :param binsize: int or None, median-binning size in the dispersion
                    direction, if set overrides "LOC_BINSIZE" from params
    :param boxp_low: float or None, the percentile of a box that is always an
                     illuminated pixel, if set overrides
                     "LOC_BOX_PERCENTILE_LOW" from  params
    :param boxp_high: float or None, the percentile of a box that is always an
                      illuminated pixel, if set overrides
                      "LOC_BOX_PERCENTILE_HIGH" from params
    :param percentile_fsize: float or None, the size of the percentile filter,
                             if set overrides "LOC_PERCENTILE_FILTER_SIZE"
                             from params
    :param fdilate_itr: int or None, the fiber dilation number of iterations,
                        if set overrides "LOC_FIBER_DILATE_ITERATIONS" from
                        params
    :param min_order_area: int or None, the minimum area (number of pixels)
                           that defines an order, if set overrides
                           "LOC_MIN_ORDER_AREA" from params
    :param cent_poly_deg: int or None, degree of polynomial to fit for
                          positions, if set overrides "LOC_CENT_POLY_DEG"
                          from params
    :param wid_poly_deg: int or None, degree of polynomial to fit the widths,
                         if set overrides "LOC_WIDTH_POLY_DEG" from params
    :param range_wid_sum: int or None, range width size (used to fit the width
                          of the orders at certain points), if set overrides
                          "LOC_RANGE_WID_SUM" from params
    :param loc_ydet_min: int or None, the minimum detector position where the
                         centers of the bottom most order should fall, if set
                         overrides "LOC_YDET_MIN" from params
    :param loc_ydet_max: int or None, the maximum detector position where the
                         centers of the top most order should fall, if set
                         overrides "LOC_YDET_MAX" from params
    :param num_wsamples: int or None, the number of width samples to use, if
                         set overrides "LOC_NUM_WID_SAMPLES" from params

    :return: tuple, 1. the central position coefficients for each order, 2. the
             width coefficients for each order
    """
    # set function name
    func_name = display_func('calc_localisation', __NAME__, )
    # -------------------------------------------------------------------------
    # Get properties from params
    # -------------------------------------------------------------------------
    # median-binning size in the dispersion direction. This is just used to
    #     get an order-of-magnitude of the order profile along a given column
    binsize = pcheck(params, 'LOC_BINSIZE', func=func_name,
                     override=binsize)
    # the percentile of a box that is always an illuminated pixel
    box_perc_low = pcheck(params, 'LOC_BOX_PERCENTILE_LOW', func=func_name,
                          override=boxp_low)
    box_perc_high = pcheck(params, 'LOC_BOX_PERCENTILE_HIGH', func=func_name,
                           override=boxp_high)
    # the size of the percentile filter - should be a bit bigger than the
    # inter-order gap
    perc_filter_size = pcheck(params, 'LOC_PERCENTILE_FILTER_SIZE',
                              func=func_name, override=percentile_fsize)
    # the fiber dilation number of iterations this should only be used when
    #     we want a combined localisation solution i.e. AB from A and B
    fiber_dilate_iterations = pcheck(params, 'LOC_FIBER_DILATE_ITERATIONS',
                                     func=func_name, override=fdilate_itr)
    # the minimum area (number of pixels) that defines an order
    min_area = pcheck(params, 'LOC_MIN_ORDER_AREA', func=func_name,
                      override=min_order_area)
    # degree of polynomial to fit for positions
    cent_order_fit = pcheck(params, 'LOC_CENT_POLY_DEG', func=func_name,
                            override=cent_poly_deg)
    # degree of polynomial to fit the widths
    wid_order_fit = pcheck(params, 'LOC_WIDTH_POLY_DEG', func=func_name,
                           override=wid_poly_deg)
    # range width size (used to fit the width of the orders at certain points)
    range_width_sum = pcheck(params, 'LOC_RANGE_WID_SUM', func=func_name,
                             override=range_wid_sum)
    # define the minimum and maximum detector position where the centers of
    #   the orders should fall
    ydet_min = pcheck(params, 'LOC_YDET_MIN', func=func_name,
                      override=loc_ydet_min)
    ydet_max = pcheck(params, 'LOC_YDET_MAX', func=func_name,
                      override=loc_ydet_max)
    # number of width samples to use
    num_wid_samples = pcheck(params, 'LOC_NUM_WID_SAMPLES', func=func_name,
                             override=num_wsamples)
    # -------------------------------------------------------------------------
    # Fiber properties
    # -------------------------------------------------------------------------
    # get pseudo constants
    pconst = constants.pload()
    # whether we are dilate the imagine due to fiber configuration this should
    #     only be used when we want a combined localisation solution
    #     i.e. AB from A and B
    fiber_dilate = pconst.FIBER_DILATE(fiber)
    # whether we have orders coming in doublets (i.e. SPIROUs AB --> A + B)
    fiber_doublets = pconst.FIBER_DOUBLETS(fiber)
    # the parity of the fiber i.e. A = -1, B = +1
    fiber_doublet_parity = pconst.FIBER_DOUBLET_PARITY(fiber)
    # -------------------------------------------------------------------------
    # print progress: Finding and fitting orders for fiber = {0}'
    WLOG(params, 'info', textentry('40-013-00028', args=[fiber]))
    # -------------------------------------------------------------------------
    # get the shape of the image
    nbypix, nbxpix = image.shape
    # set NaN pixels to zero to avoid warnings later on
    image[~np.isfinite(image)] = 0
    # set up an array of pixel values along order direction (x)
    xpix = np.arange(nbxpix)
    # -------------------------------------------------------------------------
    # print progress: Masking orders
    WLOG(params, '', textentry('40-013-00029'))
    # empty array to hold the value above which a pixel is considered
    #     illuminated for the purpose of order localisation
    threshold = np.zeros_like(image)
    # bin up the data - loop around binsize
    for bin_it in range(binsize, nbxpix - binsize, binsize):
        # profile for the spectral column
        tmp = mp.nanmedian(image[:, bin_it:bin_it + binsize], axis=1)
        # we assume that the 95th percentile of a box is always an
        #     illuminated pixel. We set the threshold at half that value.
        #     This is location-dependent, so we need to have a running
        #     95th percentile filter with a certain size. We use 100 pixels
        #     for the filter, this number should be a bit bigger than the
        #     inter-order gap.
        zp = percentile_filter(tmp, box_perc_low, size=perc_filter_size)
        tmp = percentile_filter(tmp, box_perc_high, size=perc_filter_size)
        # adding the foot after the division by 2
        tmp = tmp / 2.0 + zp
        # pad the threshold map
        maptmp = np.repeat(tmp, binsize).reshape([nbypix, binsize])
        threshold[:, bin_it:bin_it + binsize] = maptmp
    # -------------------------------------------------------------------------
    # create a binary mask that will indicate if a pixel is in or out of orders
    mask_orders = image > threshold
    # mask the edges to avoid problems
    mask_orders[:, 0:binsize] = 0
    mask_orders[:, -binsize:] = 0
    # -------------------------------------------------------------------------
    # copy mask orders (for plotting
    mask_orders0 = np.array(mask_orders)
    # -------------------------------------------------------------------------
    # find the regions that define the orders
    # the map contains integer values that are common to all pixels that form
    # a region in the binary mask
    all_labels1 = measure.label(mask_orders, connectivity=2)
    label_props1 = measure.regionprops(all_labels1)
    # find the area of all regions, we know that orders cover many pixels
    area1 = []
    for label_prop in label_props1:
        area1.append(label_prop.area)
    # these areas are considered orders. This is just a first guess we will
    #   confirm these later - we have to add 1 as measure.label defines "0" as
    #   the "background" - this is not an order
    is_order1 = np.where(np.array(area1) > min_area)[0] + 1
    # -------------------------------------------------------------------------
    # loop around orders
    for order_num in is_order1:
        # get this orders pixels
        mask_region = (all_labels1 == order_num)
        # get the flux values of the pixels for this order
        value = image[mask_region]
        # get the low flux bound (more than 5% of peak flux)
        low_flux = value < mp.nanpercentile(value, 95) * 0.05
        # get the positions so we can mask them with the low_flux mask
        ypix1, xpix1 = np.where(mask_region)
        # mask mask_orders with low_flux for this order region
        mask_orders[ypix1[low_flux], xpix1[low_flux]] = 0
    # -------------------------------------------------------------------------
    # clean up edges of orders
    for row in range(mask_orders.shape[0]):
        mask_orders[row] = median_filter(mask_orders[row], 11)
    # -------------------------------------------------------------------------
    # apply a binary dilation, mostly to avoid mis-interpreting slices as
    #    individual orders
    if fiber_dilate:
        # we dilate "fiber_dilate_iterations" times to merge orders together
        #    this should only be used when we want a combined localisation
        #    solution i.e. AB from A and B
        for _ in range(fiber_dilate_iterations):
            mask_orders = binary_dilation(mask_orders)
    # else we just do the binary dilation once
    else:
        mask_orders = binary_dilation(mask_orders)
    # -------------------------------------------------------------------------
    # add image plot of mask orders
    recipe.plot('LOC_IM_REGIONS', mask0=mask_orders0, mask1=mask_orders)
    # -------------------------------------------------------------------------
    # find the regions that define the orders (again now we have
    # the map contains integer values that are common to all pixels that form
    # a region in the binary mask
    all_labels2 = measure.label(mask_orders, connectivity=2)
    label_props2 = measure.regionprops(all_labels2)
    # find the area of all regions, we know that orders cover many pixels
    area2 = []
    for label_prop in label_props2:
        area2.append(label_prop.area)
    # these areas are considered orders. This is just a first guess we will
    #   confirm these later - we have to add 1 as measure.label defines "0" as
    #   the "background" - this is not an order
    is_order2 = np.where(np.array(area2) > min_area)[0] + 1
    # log how many blobs were found: Found {0} order blobs'
    margs = [len(is_order2)]
    WLOG(params, '', textentry('40-013-00030', args=margs))
    # -------------------------------------------------------------------------
    # storage for fit the x vs y position per region
    all_fits = np.zeros([len(is_order2), cent_order_fit + 1])
    # storage for position of fit at center of images
    order_centers = np.zeros(len(is_order2))
    # storage for the width of orcer
    order_widths = np.zeros([len(is_order2), num_wid_samples])
    # storage for valid labels
    valid_labels = np.array(is_order2)
    # loop through orders
    for order_num in range(len(is_order2)):
        # ---------------------------------------------------------------------
        # find x y position of the region considered to be an order
        xy = label_props2[is_order2[order_num] - 1].coords
        # extract the positions
        ypos, xpos = xy[:, 0], xy[:, 1]
        # determine if order overlaps with image center, if not it is not good
        is_valid = np.min(xpos) < nbxpix / 2
        is_valid &= np.max(xpos) > nbxpix / 2
        # if not valid do not continue
        if not is_valid:
            continue
        # ---------------------------------------------------------------------
        # We get how many illuminated pixels are within +/- "range_width_sum"
        #   pixels of the center of the image. This determines the width of
        #   the order. Orders can be banana-shaped within the region, that's
        #   fine
        for ibin in range(num_wid_samples):
            # get the pixels within this part of the detector
            pos = np.abs(xpos - (ibin + 1) * nbxpix / (num_wid_samples + 1))
            posmask = pos < range_width_sum
            # get the width at 3 points
            binwidth = (np.sum(posmask) / (range_width_sum * 2 + 1)) + 2
            order_widths[order_num, ibin] = binwidth
        # polynomial fit of x vs y of illuminated pixels
        # IMPORTANT NOTE
        # To avoid covariance problems between intercept and slope later on,
        #     we define the x position in the fit as relative to the center
        #     of the array. The DRS uses a fit with x=0 at the edge of the
        #     array. We'll return the proper fit at the end, but for all
        #     intermediate steps, the fit assumes that x = 0 is the *center*
        #     of the image, not it's border.
        # cent_fit = np.polyfit(xpos - nbxpix / 2, ypos, cent_order_fit)
        cent_fit = mp.fit_cheby(xpos, ypos, cent_order_fit,
                                domain=[0, image.shape[1]])

        # save fit to all fits
        all_fits[order_num] = cent_fit
        # position of the order at the center of the image
        # order_centers[order_num] = np.polyval(cent_fit, 0)
        # term 0 of a Cheby polynomial is midpoint
        order_centers[order_num] = mp.val_cheby(cent_fit, image.shape[1] // 2,
                                                domain=[0, image.shape[1]])

    measured_order_centers = np.array(order_centers)
    # -------------------------------------------------------------------------
    # keep only orders that have a center within the allowed y range
    keep = (order_centers > ydet_min) & (order_centers < ydet_max)
    # log how many orders we are keeping: Keeping {0} orders
    margs = [np.sum(keep)]
    WLOG(params, '', textentry('40-013-00031', args=margs))
    # apply keep mask to centers and widths
    order_centers = order_centers[keep]
    # order_widths = order_widths[keep]
    all_fits = all_fits[keep]
    valid_labels = valid_labels[keep]
    # -------------------------------------------------------------------------
    # sort all regions in increasing y value
    sortmask = np.argsort(order_centers)
    order_centers = order_centers[sortmask]
    # order_widths = order_widths[sortmask]
    all_fits = all_fits[sortmask]
    # -------------------------------------------------------------------------
    # if orders come in doublets the gap between orders will therefore be nearly
    #    constant if we step from A to B and vary if we step from B to next
    #    orders A. We use that to identify which orders match and remove the
    #    other orders
    if fiber_doublets:
        index = np.arange(len(order_centers))
        # ok as a polyfit, it's just the position of order centers along the
        # y axis of the array. This is used to ID orders that have problematic
        # gaps.
        cent_fit = np.polyfit(index, order_centers, 5)
        residuals = order_centers - np.polyval(cent_fit, index)
        # doublet fibers have a parity
        if fiber_doublet_parity < 0:
            keep = residuals < 0
        else:
            keep = residuals > 0
        # plot the fiber doublet parity plot
        recipe.plot('LOC_FIBER_DOUBLET_PARITY', index=index,
                    centers=order_centers, residuals=residuals, fit=cent_fit)
        # remove the other fibers orders
        order_centers = order_centers[keep]
        # other_widths = order_widths[keep]
        all_fits = all_fits[keep]
        valid_labels = valid_labels[keep]
    # -------------------------------------------------------------------------
    # find the gap between consecutive orders and use this to confirm the
    #    numbering
    orderdiff = order_centers[1:] - order_centers[:-1]
    # same as above, the polyfit is used to identify orders that do not
    # follo the right stepping expected from cross-dispersion.
    fit_gap, gapmask = mp.robust_polyfit(order_centers[1:], orderdiff, 3, 5)
    # -------------------------------------------------------------------------
    recipe.plot('LOC_GAP_ORDERS', centers=order_centers, mask=gapmask,
                fit=fit_gap)
    # -------------------------------------------------------------------------
    # use the robust polyfit mask to determine which order is valid
    valid_order_centers = order_centers[1:][gapmask]
    valid_gap = (order_centers[1:] - order_centers[:-1])[gapmask]
    valid_fits = all_fits[1:][gapmask]
    valid_labels = valid_labels[1:][gapmask]
    # -------------------------------------------------------------------------
    # loop around valid orders and count the orders using known gap
    index2 = np.zeros_like(valid_order_centers, dtype=int)
    for it in range(1, len(valid_order_centers)):
        # get the difference
        pixdiff = (valid_order_centers[it] - valid_order_centers[it - 1])
        pixdiff = pixdiff / valid_gap[it]
        # count the orders using the known gap to know if we missed any
        index2[it] = index2[it - 1] + int(np.round(pixdiff))
    # -------------------------------------------------------------------------
    # have a big matrix to be filled with interpolated orders. We make it 5
    #   orders bigger in both directions just in case we missed red/blue orders
    #   These will be checked against y limits later
    index_full = np.arange(np.min(index2) - 5, np.max(index2) + 5)
    fits_full = np.zeros([len(index_full), valid_fits.shape[1]])
    center_full = np.zeros(len(index_full))
    # -------------------------------------------------------------------------
    # order of polynomial fits used for the consistency of fitting values
    nth_ord = np.ones(cent_order_fit + 1, dtype=int)
    # for the intercept, we use a high-order-fit
    nth_ord[0] = 13
    # for the slope, we use a high-order fit
    nth_ord[1] = 7
    # for the curvature, we use a high-order-fit
    nth_ord[2] = 3
    # -------------------------------------------------------------------------
    # domain across the orders
    domain = [np.min(index_full), np.max(index_full)]
    # force continuity between the localisation parameters
    for it in range(valid_fits.shape[1]):
        # robustly fit in the order direction
        cfit, cmask = mp.robust_chebyfit(index2, valid_fits[:, it], nth_ord[it],
                                         5, domain=domain)
        # update the full fits
        fits_full[:, it] = mp.val_cheby(cfit, index_full, domain=domain)
    # get the central pixel position (note x=0 at the center here)
    for it in range(fits_full.shape[0]):
        center_full[it] = mp.val_cheby(fits_full[it], image.shape[1] // 2,
                                       domain=[0, image.shape[1]])
    # -------------------------------------------------------------------------
    # keep only orders that have a center within the allowed y range
    keep = (center_full > ydet_min) & (center_full < ydet_max)
    # copy to the final center fits
    final_cent_fit = fits_full[keep]
    center_full = center_full[keep]
    # -------------------------------------------------------------------------
    # Remove cross term between coefficients in the fit by using the original
    #   measured centers of the labels (orders)
    # -------------------------------------------------------------------------
    # get the max offset to allow correction using order separation
    max_measured_offset = np.median(abs(np.diff(center_full))) / 4
    # loop around each order
    for order_num in range(len(center_full)):
        # get the difference in final position and measure position
        diff = center_full[order_num] - measured_order_centers
        # get the minimum offset between the order in the original labelled fits
        #   (measured position)
        pos = np.argmin(abs(diff))
        # if the difference is small then we take this as a correction to the
        #   order center and fit
        if abs(diff[pos]) < max_measured_offset:
            final_cent_fit[order_num, 0] -= diff[pos]
            center_full[order_num] -= diff[pos]
    # -------------------------------------------------------------------------
    # log final number of orders
    msg = 'Final number of Orders: {0}'
    margs = [final_cent_fit.shape[0]]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # Calculate width polynomial fits
    # -------------------------------------------------------------------------
    # storage for the width fit
    width_fit = np.zeros([len(valid_labels), wid_order_fit + 1])
    width_pos = np.zeros([len(valid_labels)])
    # loop around each order
    for wit, valid_label in enumerate(valid_labels):
        # we get back the map of all pixels in this order (from the labelling)
        ordpixmap = all_labels2 == valid_label
        # we sum all the pixels in the y direction (this is the width in pixels
        #  we have per x pixel
        sumpixmap_x = np.sum(ordpixmap, axis=0)
        sumpixmap_y = np.sum(ordpixmap, axis=1)
        # get valid pixels within this order
        validsumpixmap = np.where(sumpixmap_x > 0.5 * np.max(sumpixmap_x))[0]
        imin = np.min(validsumpixmap) + 15
        imax = np.max(validsumpixmap) - 15
        # we convolve this with a box to smooth it out
        csumpixmap = np.convolve(sumpixmap_x, np.ones(15) / 15, mode='same')
        # we then fit this robustly with a polyfit
        wfit, wmask = mp.robust_chebyfit(xpix[imin:imax], csumpixmap[imin:imax],
                                         wid_order_fit, 5, domain=[0, nbxpix])
        # add this to the fit
        width_fit[wit] = wfit
        # get the mean position of region in y
        wpos = np.sum(sumpixmap_y * np.arange(len(sumpixmap_y)))
        width_pos[wit] = wpos / np.sum(sumpixmap_y)
    # -------------------------------------------------------------------------
    # need a final width fit array
    final_width_fit = np.zeros([final_cent_fit.shape[0], wid_order_fit + 1])
    # force continuity between the localisation parameters
    for it in range(width_fit.shape[1]):
        # robustly fit in the order direction
        wfit, wmask = mp.robust_polyfit(width_pos, width_fit[:, it],
                                        wid_order_fit, 5)
        # update the full fits
        final_width_fit[:, it] = np.polyval(wfit, center_full)
    # -------------------------------------------------------------------------
    # plot the width coefficients
    recipe.plot('LOC_WIDTH_REGIONS', coeffs1=width_fit, coeffs2=final_width_fit)
    # -------------------------------------------------------------------------
    # plot first and final fit over image
    recipe.plot('LOC_IMAGE_FIT', image=image, coeffs_old=all_fits,
                coeffs=final_cent_fit, kind=fiber, reverse=False,
                offset=0.0, xlines=[nbxpix // 2],
                ylines=[ydet_min, ydet_max], width_coeffs=final_width_fit)
    # -------------------------------------------------------------------------
    # Convert centers fit to "start" at x = 0  (previous x = image.shape[1]//2)
    # -------------------------------------------------------------------------
    # convert back to start at x = 0
    # for order_num in range(len(final_cent_fit)):
    #     # get the current y values (centers at x half detector width)
    #     #ypix = np.polyval(final_cent_fit[order_num], xpix - nbxpix // 2)
    #     # push into the final center fit
    #     #final_cent_fit[order_num] = np.polyfit(xpix, ypix, cent_order_fit)
    #     final_cent_fit[order_num] = mp.val_cheby(cent_order_fit,
    #                                              nbxpix//2,
    #                                              domain=[0, nbxpix])

    # -------------------------------------------------------------------------
    # return the final centers fit and widths fit
    return final_cent_fit, final_width_fit


def merge_coeffs(params: ParamDict,
                 ldict: Dict[str, tuple], nbxpix: int
                 ) -> Tuple[np.ndarray, np.ndarray, str]:
    """
    Deal with merging A and B solutions (for SPIRou) - this is just because
    originally they were merged

    i.e. we go from "cent coeffs fiber 1" and "cent coeffs fiber 2" to:
        order1 fiber1
        order1 fiber2
        order2 fiber1
        order2 fiber2
        ...
        orderN fiber1
        orderN fiber2

    :param params:ParamDict, the parameter dictionary of constants
    :param ldict: dictionary of fibers:
                  ldict[fiber1] = [cent coeffs fiber1, wid coeffs fiber1]
                  ldict[fiber2] = [cent coeffs fiber2, wid coeffs fiber2]
    :param nbxpix: int, the number of pixels in the x-direction

    :return: tuple, 1. the combined cent coeffs, 2. the combined width coeffs
             3. the name of the fibers i.e. "1 + 2"
    """
    # set the function name
    func_name = display_func('merge_coeffs', __NAME__)
    # get the fibers we have in ldict
    _fibers = np.array(list(ldict.keys()))
    # merge ldict into a single array
    if len(_fibers) == 1:
        # get coefficients - need to be flipped
        cent_coeffs = ldict[_fibers[0]][0]
        wid_coeffs = ldict[_fibers[0]][1]
        fiber_name = _fibers[0]
        # return arrays
        return np.array(cent_coeffs), np.array(wid_coeffs), fiber_name
    else:
        # get the first fibers values (to get the number of orders)
        fiber0 = _fibers[0]
        cent_coeffs0 = ldict[fiber0][0]
        # get the number of orders
        nbo = cent_coeffs0.shape[0]
        # storage for output
        cent_coeffs, wid_coeffs = [], []

        # need to get the order of the fibers
        fiber_min = []
        for _fiber in _fibers:
            # get the center value of the first order
            #    (by definition the closest to the bottom of the detector))
            cent = mp.val_cheby(ldict[_fiber][0][0], nbxpix // 2,
                                domain=[0, nbxpix])
            fiber_min.append(cent)
        # get the fibers in the correct order
        _fibers = _fibers[np.argsort(fiber_min)]
        # loop around orders
        for order_num in range(nbo):
            # loop around the fibers in correct order
            for _fiber in _fibers:
                # get this fiber numbers of orders
                fiber_nbo = len(ldict[_fiber][0])
                # must check we have the same number of orders
                if fiber_nbo != nbo:
                    # log error: Inconsistent number of orders between fibers
                    eargs = [fiber0, nbo, _fiber, fiber_nbo, func_name]
                    WLOG(params, 'error', textentry('00-013-00008', args=eargs))
                # add to merged coeffs - need to be flipped
                cent_coeffs.append(ldict[_fiber][0][order_num])
                wid_coeffs.append(ldict[_fiber][1][order_num])
        # convert to numpy arrays
        cent_coeffs = np.array(cent_coeffs)
        wid_coeffs = np.array(wid_coeffs)
        # get fiber name
        fiber_name = ' + '.join(list(_fibers))
        # return arrays
        return cent_coeffs, wid_coeffs, fiber_name


def image_superimp(image: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    """
    Take an image and superimpose zeros over the positions in the image where
    the central fits where found to be

    :param image: numpy array (2D), the image
    :param coeffs: coefficient array,
                   size = (number of orders x number of coefficients in fit)
                   output array will be size = (number of orders x dim)

    :return newimage: numpy array (2D), the image with super-imposed zero filled
                      fits
    """
    # copy the old image
    newimage = image.copy()
    # get the number of orders
    n_orders = len(coeffs)
    # get the pixel positions along the order
    xdata = np.arange(image.shape[1])
    # loop around each order
    fitxarray, fityarray = [], []
    for order_num in range(n_orders):
        # get the pixel positions across the order (from fit coeffs in position)
        # add 0.5 to account for later conversion to int
        fity = mp.val_cheby(coeffs[order_num], xdata, [0, image.shape[1]]) + 0.5
        # elements must be > 0 and less than image.shape[0]
        mask = (fity > 0) & (fity < image.shape[0])
        # Add good values to storage array
        fityarray = np.append(fityarray, fity[mask])
        fitxarray = np.append(fitxarray, xdata[mask])

    # convert fitxarray and fityarra to integers
    fitxarray = np.array(fitxarray, dtype=int)
    fityarray = np.array(fityarray, dtype=int)
    # use fitxarray and fityarray as positions to set 0 in newimage
    newimage[fityarray, fitxarray] = 0
    # return newimage
    return newimage


def get_coefficients(params: ParamDict, header: drs_file.Header,
                     fiber: str, database: Optional[CalibrationDatabase] = None,
                     merge: bool = False,
                     filename: Optional[str] = None) -> ParamDict:
    """
    Get the localisation coefficients for a specific header

    :param params: ParamDict, parameter dictionary of constants
    :param header: fits Header, the header to match date/time of coefficients
                   caliration file to
    :param fiber: str, the fiber to get coefficients for
    :param database: CalibrationDatabase instance or None, if not set will
                     reload the calibration database
    :param merge: bool, if True merges the orders based on pseudo consts
                  "FIBER_LOC_COEFF_EXT" method.
    :param filename: str or None, if set overrides the file used to get the
                     coefficients (does not use database)

    :return: ParamDict, the localisation parameter dictionary
    """
    # set function name
    func_name = __NAME__ + '.get_coefficients()'
    # get pseudo constants
    pconst = constants.pload()
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_LOC_TYPES(fiber)
    # -------------------------------------------------------------------------
    # get loco file instance
    locofile = drs_file.get_file_definition(params, 'LOC_LOCO',
                                            block_kind='red')
    # get calibration key
    key = locofile.get_dbkey()
    # load database
    if database is None:
        calibdbm = CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # load loco file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, key, header, filename=filename,
                          userinputkey='LOCOFILE', database=calibdbm,
                          fiber=usefiber, return_filename=True)
    # get properties from calibration file
    locofilepath, locotime = cfile.filename, cfile.mjdmid
    # ------------------------------------------------------------------------
    # construct new infile instance and read data/header
    locofile = locofile.newcopy(filename=locofilepath, params=params,
                                fiber=usefiber)
    locofile.read_file()
    # -------------------------------------------------------------------------
    # extract keys from header
    nbo = locofile.get_hkey('KW_LOC_NBO', dtype=int)
    deg_c = locofile.get_hkey('KW_LOC_DEG_C', dtype=int)
    deg_w = locofile.get_hkey('KW_LOC_DEG_W', dtype=int)
    nset = params['FIBER_SET_NUM_FIBERS_{0}'.format(fiber)]
    # extract coefficients from header
    cent_coeffs = locofile.get_hkey_2d('KW_LOC_CTR_COEFF',
                                       dim1=nbo, dim2=deg_c + 1)
    wid_coeffs = locofile.get_hkey_2d('KW_LOC_WID_COEFF',
                                      dim1=nbo, dim2=deg_w + 1)
    # merge or extract individual coeffs
    if merge:
        cent_coeffs, nbo = pconst.FIBER_LOC_COEFF_EXT(cent_coeffs, fiber)
        wid_coeffs, nbo = pconst.FIBER_LOC_COEFF_EXT(wid_coeffs, fiber)
        nset = 1
    # -------------------------------------------------------------------------
    # store localisation properties in parameter dictionary
    props = ParamDict()
    props['LOCOFILE'] = locofilepath
    props['LOCOTIME'] = locotime
    props['LOCOOBJECT'] = locofile
    props['NBO'] = int(nbo // nset)
    props['DEG_C'] = int(deg_c)
    props['DEG_W'] = int(deg_w)
    props['CENT_COEFFS'] = cent_coeffs
    props['WID_COEFFS'] = wid_coeffs
    props['MERGED'] = merge
    props['NSET'] = nset
    # set sources
    keys = ['CENT_COEFFS', 'WID_COEFFS', 'LOCOFILE', 'LOCOOBJECT', 'NBO',
            'DEG_C', 'DEG_W', 'MERGED', 'NSET']
    props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # return the coefficients and properties
    return props


# =============================================================================
# write files and qc functions
# =============================================================================
def loc_stats(params: ParamDict, fiber: str, cent_coeffs: np.ndarray,
              wid_coeffs: np.ndarray, image: np.ndarray,
              central_col: Optional[int] = None,
              horder_size: Optional[int] = None,
              minpeak_amp: Optional[float] = None,
              back_thres: Optional[float] = None,
              loc_ydet_min: Optional[int] = None,
              loc_ydet_max: Optional[int] = None) -> ParamDict:
    """
    Calculate the localisation statistics

    :param params: ParamDict, parameter dictionary of constants
    :param fiber: str, the fiber name
    :param cent_coeffs: numpy 2D array of position coefficients
    :param wid_coeffs: numpy 2D array of width coefficients
    :param image: numpy 2D array, the original input image
    :param central_col: int or None, the central column for use in localisation,
                        if set overrides "LOC_CENTRAL_COLUMN" from params
    :param horder_size: int or None, Half spacing between orders, if set
                        overrides "LOC_HALF_ORDER_SPACING" from params
    :param minpeak_amp: float or None, Minimum amplitude to accept (in e-),
                        if set overrides "LOC_MINPEAK_AMPLITUDE" from params
    :param back_thres: float or None, Normalised amplitude threshold to accept
                       pixels for background calculation, if set overrides
                       "LOC_BKGRD_THRESHOLD" from params
    :param loc_ydet_min: int or None, the minimum detector position where the
                         centers of the bottom most order should fall, if set
                         overrides "LOC_YDET_MIN" from params
    :param loc_ydet_max: int or None, the maximum detector position where the
                         centers of the top most order should fall, if set
                         overrides "LOC_YDET_MAX" from params

    :return: ParamDict, the localisation parameter dictionary
    """

    # set function name
    func_name = display_func('loc_stats', __NAME__)

    # get constants from params
    central_col = pcheck(params, 'LOC_CENTRAL_COLUMN', func=func_name,
                         override=central_col)
    horder_size = pcheck(params, 'LOC_HALF_ORDER_SPACING', func=func_name,
                         override=horder_size)
    minpeak_amp = pcheck(params, 'LOC_MINPEAK_AMPLITUDE', func=func_name,
                         override=minpeak_amp)
    back_thres = pcheck(params, 'LOC_BKGRD_THRESHOLD', func=func_name,
                        override=back_thres)
    # define the minimum and maximum detector position where the centers of
    #   the orders should fall
    ydet_min = pcheck(params, 'LOC_YDET_MIN', func=func_name,
                      override=loc_ydet_min)
    ydet_max = pcheck(params, 'LOC_YDET_MAX', func=func_name,
                      override=loc_ydet_max)
    # -------------------------------------------------------------------------
    # get shape of the original image
    nbypix, nbxpix = image.shape
    xpix = np.arange(nbxpix)
    # shape of coeffiecients
    nbo, nbcoeffs = cent_coeffs.shape
    # -------------------------------------------------------------------------
    # get the center fits (as an image)
    center_fits = np.zeros([nbo, nbxpix])
    # loop around orders
    for order_num in range(nbo):
        # get this orders coefficients (flipped for numpy)
        ord_coeffs = cent_coeffs[order_num]
        # load these values into the center fits arrays
        center_fits[order_num] = mp.val_cheby(ord_coeffs, xpix,
                                              domain=[0, nbxpix])
    # -------------------------------------------------------------------------
    # get the width fits (as an image)
    width_fits = np.zeros([nbo, nbxpix])
    # loop around orders
    for order_num in range(nbo):
        # get this orders coefficients (flipped for numpy)
        ord_coeffs = wid_coeffs[order_num]
        # load these values into the center fits arrays
        width_fits[order_num] = mp.val_cheby(ord_coeffs, xpix,
                                             domain=[0, nbxpix])
    # -------------------------------------------------------------------------
    # difference between centers
    cent_diff = np.diff(center_fits, axis=0)
    # -------------------------------------------------------------------------
    # Get max signal and mean background (just for stats)
    # -------------------------------------------------------------------------
    # deal with the central column column=ic_cent_col
    y = mp.nanmedian(image[ydet_min:ydet_max,
                     central_col - 10:central_col + 10],
                     axis=1)
    # measure min max of box smoothed central col
    miny, maxy = mp.measure_box_min_max(y, horder_size)
    max_signal = mp.nanpercentile(y, 95)
    diff_maxmin = maxy - miny
    # normalised the central pixel values above the minimum amplitude
    #   zero by miny and normalise by (maxy - miny)
    #   Set all values below ic_min_amplitude to zero
    ycc = np.where(diff_maxmin > minpeak_amp, (y - miny) / diff_maxmin, 0)
    # get the normalised minimum values for those rows above threshold
    #   i.e. good background measurements
    normed_miny = miny / diff_maxmin
    # find all y positions above the background threshold
    goodmask = ycc > back_thres
    # measure the mean good background as a percentage
    mean_backgrd = np.mean(normed_miny[goodmask]) * 100
    # Log the maximum signal and the mean background
    WLOG(params, 'info', textentry('40-013-00003', args=[max_signal]))
    WLOG(params, 'info', textentry('40-013-00004', args=[mean_backgrd]))
    # -------------------------------------------------------------------------
    # load stats into parameter dictionary
    lprops = ParamDict()
    lprops['CENT_COEFFS'] = cent_coeffs
    lprops['WID_COEFFS'] = wid_coeffs
    lprops['CENTER_FITS'] = center_fits
    lprops['WIDTH_FITS'] = width_fits
    lprops['FIBER'] = fiber
    lprops['CENTER_DIFF'] = cent_diff
    lprops['NORDERS'] = nbo
    lprops['NCOEFFS'] = nbcoeffs
    lprops['MAX_SIGNAL'] = max_signal
    lprops['MEAN_BACKGRD'] = mean_backgrd
    lprops['NBXPIX'] = nbxpix
    # add source
    keys = ['CENT_COEFFS', 'WID_COEFFS', 'CENTER_FITS', 'WIDTH_FITS', 'FIBER',
            'CENTER_DIFF', 'NORDERS', 'NCOEFFS', 'MAX_SIGNAL', 'MEAN_BACKGRD',
            'NBXPIX']
    lprops.set_sources(keys, func_name)
    # return stats parameter dictionary
    return lprops


def loc_quality_control(params: ParamDict, lprops: ParamDict
                        ) -> Tuple[List[list], int]:
    """
    Calculate the localisation quality control criteria

    :param params: ParamDict, parameter dictionary of constants
    :param lprops: ParamDict, the localisation parameter dictionary

    :return: tuple, 1. the quality control lists, 2. bool whether all tests
             passed
    """
    # set function name
    func_name = display_func('localisation_quality_control', __NAME__)
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # get qc parameters
    # max_removed_cent = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_CTR',
    #                           func=func_name)
    # max_removed_wid = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_WID',
    #                          func=func_name)
    # rmsmax_cent = pcheck(params, 'QC_LOC_RMSMAX_CTR', func=func_name)
    # rmsmax_wid = pcheck(params, 'QC_LOC_RMSMAX_WID', func=func_name)
    # get constants from stats
    fiber = lprops['FIBER']
    rorder_num = lprops['NORDERS']
    cent_diff = lprops['CENTER_DIFF']
    # this one comes from pseudo constants
    pconst = constants.pload()
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)

    required_norders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', func=func_name,
                              paramdict=fiberparams)
    # ----------------------------------------------------------------------
    # # check that max number of points rejected in center fit is below
    # #    threshold
    # sum_cent_max_rmpts = mp.nansum(cent_max_rmpts)
    # if sum_cent_max_rmpts > max_removed_cent:
    #     # add failed message to fail message list
    #     fargs = [sum_cent_max_rmpts, max_removed_cent]
    #     fail_msg.append(textentry('40-013-00014', args=fargs))
    #     qc_pass.append(0)
    # else:
    #     qc_pass.append(1)
    # # add to qc header lists
    # qc_values.append(sum_cent_max_rmpts)
    # qc_names.append('sum(MAX_RMPTS_POS)')
    # qc_logic.append('sum(MAX_RMPTS_POS) < {0:.2f}'
    #                 ''.format(sum_cent_max_rmpts))
    # # ----------------------------------------------------------------------
    # # check that  max number of points rejected in width fit is below
    # #   threshold
    # sum_wid_max_rmpts = mp.nansum(wid_max_rmpts)
    # if sum_wid_max_rmpts > max_removed_wid:
    #     # add failed message to fail message list
    #     fargs = [sum_wid_max_rmpts, max_removed_wid]
    #     fail_msg.append(textentry('40-013-00015', args=fargs))
    #     qc_pass.append(0)
    # else:
    #     qc_pass.append(1)
    # # add to qc header lists
    # qc_values.append(sum_wid_max_rmpts)
    # qc_names.append('sum(MAX_RMPTS_WID)')
    # qc_logic.append('sum(MAX_RMPTS_WID) < {0:.2f}'
    #                 ''.format(sum_wid_max_rmpts))
    # ------------------------------------------------------------------
    # if mean_rms_cent > rmsmax_cent:
    #     # add failed message to fail message list
    #     fargs = [mean_rms_cent, rmsmax_cent]
    #     fail_msg.append(textentry('40-013-00016', args=fargs))
    #     qc_pass.append(0)
    # else:
    #     qc_pass.append(1)
    # # add to qc header lists
    # qc_values.append(mean_rms_cent)
    # qc_names.append('mean_rms_center')
    # qc_logic.append('mean_rms_center < {0:.2f}'.format(rmsmax_cent))
    # # ------------------------------------------------------------------
    # if mean_rms_wid > rmsmax_wid:
    #     # add failed message to fail message list
    #     fargs = [mean_rms_wid, rmsmax_wid]
    #     fail_msg.append(textentry('40-013-00017', args=fargs))
    #     qc_pass.append(0)
    # else:
    #     qc_pass.append(1)
    # # add to qc header lists
    # qc_values.append(mean_rms_wid)
    # qc_names.append('mean_rms_wid')
    # qc_logic.append('mean_rms_wid < {0:.2f}'.format(rmsmax_wid))
    # ------------------------------------------------------------------
    # check for abnormal number of identified orders
    if rorder_num != required_norders:
        # add failed message to fail message list
        fargs = [rorder_num, required_norders]
        fail_msg.append(textentry('40-013-00018', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(rorder_num)
    qc_names.append('rorder_num')
    qc_logic.append('rorder_num != {0}'.format(required_norders))
    # ------------------------------------------------------------------
    # all positions in any pixel column should be positive
    #   (i.e. one order should not cross another)
    # find the difference between every order for every column
    negative_diff = np.min(cent_diff) < 0
    # if any value is negative QC fails
    if negative_diff:
        # add failed message to fail message list
        fargs = [' ']
        fail_msg.append(textentry('40-013-00027', *fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(negative_diff)
    qc_names.append('YCENT')
    qc_logic.append('min(diff(YCENT)) < 0')
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #    quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params, passed


def write_localisation_files(params: ParamDict, recipe: DrsRecipe,
                             infile: DrsFitsFile, image: np.ndarray,
                             rawfiles: List[str], combine: bool,
                             fiber: str, props: ParamDict,
                             order_profile: np.ndarray, lprops: ParamDict,
                             qc_params: List[list]
                             ) -> Tuple[DrsFitsFile, DrsFitsFile]:
    """
    Write the localisation order profile and coefficients files to disk

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance that called this function
    :param infile: DrsFitsFile, the input drs fits file instance
    :param image: numpy 2D array, the original input image (to superimpose
                  orders onto for debug file) may have been combined
    :param rawfiles: list of strings, the filenames of the input files
    :param combine: bool, if True, input files have be combined
    :param fiber: str, the fiber we are writing loc files for
    :param props: ParamDict, the calibration of pp file parameter dictionary
    :param order_profile: numpy 2D array the order profile
    :param lprops: ParamDict, the localisation parameter dictionary
    :param qc_params: list of lists, the quality control lists

    :return: tuple, 1. the order profile drs file instance, 2. the localisation
             drs file instance
    """
    # this one comes from pseudo constants
    pconst = constants.pload()
    # get properties from lprops
    cent_coeffs = lprops['CENT_COEFFS']
    wid_coeffs = lprops['WID_COEFFS']
    center_fits = lprops['CENTER_FITS']
    width_fits = lprops['WIDTH_FITS']
    mean_backgrd = lprops['MEAN_BACKGRD']
    rorder_num = lprops['NORDERS']
    max_signal = lprops['MAX_SIGNAL']
    # ------------------------------------------------------------------
    # Make cent coefficient table
    # ------------------------------------------------------------------
    # get number of orders
    nbo = cent_coeffs.shape[0]
    fiberlist = pconst.FIBER_LOC(fiber=fiber)
    # add order column
    cent_cols = ['ORDER']
    cent_vals = [np.repeat(np.arange(nbo // len(fiberlist)), len(fiberlist))]
    # add fiber column
    cent_cols += ['FIBER']
    cent_vals.append(np.tile([fiberlist], nbo // len(fiberlist))[0])
    # add coefficients columns
    for c_it in range(cent_coeffs.shape[1]):
        cent_cols.append('COEFFS_{0}'.format(c_it))
        cent_vals.append(cent_coeffs[:, c_it])
    cent_table = drs_table.make_table(params, columns=cent_cols,
                                      values=cent_vals)
    # ------------------------------------------------------------------
    # Make width coefficient table
    # ------------------------------------------------------------------
    # add order column
    wid_cols = ['ORDER']
    wid_vals = [np.repeat(np.arange(nbo // len(fiberlist)), len(fiberlist))]
    # add fiber column
    wid_cols += ['FIBER']
    wid_vals.append(np.tile([fiberlist], nbo // len(fiberlist))[0])
    # add coefficients columns
    for c_it in range(wid_coeffs.shape[1]):
        wid_cols.append('COEFFS_{0}'.format(c_it))
        wid_vals.append(wid_coeffs[:, c_it])
    wid_table = drs_table.make_table(params, columns=wid_cols,
                                     values=wid_vals)
    # ------------------------------------------------------------------
    # Write image order_profile to file
    # ------------------------------------------------------------------
    # get a new copy to the order profile
    orderpfile = recipe.outputs['ORDERP_FILE'].newcopy(params=params,
                                                       fiber=fiber)
    # construct the filename from file instance
    orderpfile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file
    orderpfile.copy_original_keys(infile)
    # add version
    orderpfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    orderpfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    orderpfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    orderpfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    orderpfile.add_hkey('KW_OUTPUT', value=orderpfile.name)
    orderpfile.add_hkey('KW_FIBER', value=fiber)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    orderpfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add infiles
    orderpfile.infiles = hfiles
    # add the calibration files use
    orderpfile = gen_calib.add_calibs_to_header(orderpfile, props)
    # add qc parameters
    orderpfile.add_qckeys(qc_params)
    # copy data
    orderpfile.data = order_profile
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-013-00002', args=[orderpfile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=orderpfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    orderpfile.write_multi(data_list=data_list, name_list=name_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(orderpfile)
    # ------------------------------------------------------------------
    # Save and record of image of localization with order center
    #     and keywords
    # ------------------------------------------------------------------
    loco1file = recipe.outputs['LOCO_FILE'].newcopy(params=params,
                                                    fiber=fiber)
    # construct the filename from file instance
    loco1file.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    loco1file.copy_original_keys(infile)
    # add version
    loco1file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    loco1file.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    loco1file.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    loco1file.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    loco1file.add_hkey('KW_OUTPUT', value=loco1file.name)
    loco1file.add_hkey('KW_FIBER', value=fiber)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    loco1file.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add infiles
    loco1file.infiles = list(hfiles)
    # add the calibration files use
    loco1file = gen_calib.add_calibs_to_header(loco1file, props)
    # add localisation parameters
    loco1file.add_hkey('KW_LOC_BCKGRD', value=mean_backgrd)
    loco1file.add_hkey('KW_LOC_NBO', value=rorder_num)
    loco1file.add_hkey('KW_LOC_DEG_C', value=params['LOC_CENT_POLY_DEG'])
    loco1file.add_hkey('KW_LOC_DEG_W', value=params['LOC_WIDTH_POLY_DEG'])
    loco1file.add_hkey('KW_LOC_MAXFLX', value=max_signal)
    # write 2D list of position fit coefficients
    loco1file.add_hkey_2d('KW_LOC_CTR_COEFF', values=cent_coeffs,
                          dim1name='order', dim2name='coeff')
    # write 2D list of width fit coefficients
    loco1file.add_hkey_2d('KW_LOC_WID_COEFF', values=wid_coeffs,
                          dim1name='order', dim2name='coeff')
    # add qc parameters
    loco1file.add_qckeys(qc_params)
    # copy data
    loco1file.data = center_fits
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-013-00019', args=[loco1file.filename]))
    # define multi lists
    data_list = [cent_table, wid_table]
    name_list = ['CENT_TABLE', 'WIDTH_TABLE']
    datatype_list = ['table', 'table']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=loco1file)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    loco1file.write_multi(data_list=data_list, name_list=name_list,
                          datatype_list=datatype_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(loco1file)
    # ------------------------------------------------------------------
    # Save and record of image of sigma
    # ------------------------------------------------------------------
    loco2file = recipe.outputs['FWHM_FILE'].newcopy(params=params,
                                                    fiber=fiber)
    # construct the filename from file instance
    loco2file.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from loco1file
    loco2file.copy_hdict(loco1file)
    # add infiles
    loco2file.infiles = list(hfiles)
    # set output key
    loco2file.add_hkey('KW_OUTPUT', value=loco2file.name)
    # copy data
    loco2file.data = width_fits
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-013-00020', args=[loco2file.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=loco2file)]
        name_list += ['PARAM_TABLE']
    # write image to file
    loco2file.write_multi(data_list=data_list, name_list=name_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(loco2file)
    # ------------------------------------------------------------------
    # Save and Record of image of localization
    # ------------------------------------------------------------------
    if params['LOC_SAVE_SUPERIMP_FILE']:
        # --------------------------------------------------------------
        # super impose zeros over the fit in the image
        image5 = image_superimp(image, cent_coeffs)
        # --------------------------------------------------------------
        loco3file = recipe.outputs['SUP_FILE'].newcopy(params=params,
                                                       fiber=fiber)
        # construct the filename from file instance
        loco3file.construct_filename(infile=infile)
        # --------------------------------------------------------------
        # define header keys for output file
        # copy keys from loco1file
        loco3file.copy_hdict(loco1file)
        # set output key
        loco3file.add_hkey('KW_OUTPUT', value=loco3file.name)
        # add infiles
        loco3file.infiles = list(hfiles)
        # copy data
        loco3file.data = image5
        # --------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [loco3file.filename]
        WLOG(params, '', textentry('40-013-00021', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=loco3file)]
            name_list += ['PARAM_TABLE']
        # write image to file
        loco3file.write_multi(data_list=data_list, name_list=name_list,
                              block_kind=recipe.out_block_str,
                              runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(loco3file)
    # ------------------------------------------------------------------
    # return out files
    return orderpfile, loco1file


def loc_summary(recipe: DrsRecipe, it: int, params: ParamDict,
                qc_params: List[list], props: ParamDict, lprops: ParamDict):
    """
    Produce the localisation summary document

    :param recipe: DrsRecipe, the recipe instance that called this function
    :param it: int, the iteration number for localisation
    :param params: ParamDict, parameter dictionary of constants
    :param qc_params: list of lists, the quality control lists
    :param props: ParamDict, the calibration of pp file parameter dictionary
    :param lprops: ParamDict, the localisation parameter dictionary

    :return: None, saves summary document(s) to disk
    """
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_DPRTYPE', value=props['DPRTYPE'])
    recipe.plot.add_stat('KW_LOC_BCKGRD', value=lprops['MEAN_BACKGRD'])
    recipe.plot.add_stat('KW_LOC_NBO', value=lprops['NORDERS'])
    recipe.plot.add_stat('KW_LOC_DEG_C', value=params['LOC_CENT_POLY_DEG'])
    recipe.plot.add_stat('KW_LOC_DEG_W', value=params['LOC_WIDTH_POLY_DEG'])
    recipe.plot.add_stat('KW_LOC_MAXFLX', value=lprops['MAX_SIGNAL'])
    recipe.plot.add_stat('KW_LOC_SMAXPTS_CTR',
                         value=params['QC_LOC_MAXFIT_REMOVED_CTR'])
    recipe.plot.add_stat('KW_LOC_SMAXPTS_WID',
                         value=params['QC_LOC_MAXFIT_REMOVED_WID'])
    recipe.plot.add_stat('KW_LOC_RMS_CTR',
                         value=params['QC_LOC_RMSMAX_CTR'])
    recipe.plot.add_stat('KW_LOC_RMS_WID',
                         value=params['QC_LOC_RMSMAX_WID'])
    # construct summary
    recipe.plot.summary_document(it, qc_params)


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
