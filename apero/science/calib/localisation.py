#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 13:48

@author: cook
"""
from collections import OrderedDict
import numpy as np
from skimage import measure
from scipy.ndimage import percentile_filter, binary_dilation
from typing import Dict, Tuple, Union
import warnings

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_log, drs_file
from apero.core.core import drs_database
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
def calculate_order_profile(params, image, **kwargs):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param kwargs: keyword arguments

    :keyword size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge

    :return newimage: numpy array (2D), the smoothed image
    """
    func_name = __NAME__ + '.calculate_order_profile()'
    # get constants from params
    size = pcheck(params, 'LOC_ORDERP_BOX_SIZE', 'size', kwargs, func_name)
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
                      fiber: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find and fit the orders for this order based on the "image" (order profile)

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DreRecipe instance, the recipe that called this function
    :param image: np.array (2D), the image to fit the orders on
    :param fiber: str, the fiber name (i.e. 'A', 'B' or 'C')

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
    binsize = pcheck(params, 'LOC_BINSIZE', func=func_name)
    # the percentile of a box that is always an illuminated pixel
    box_perc_low = pcheck(params, 'LOC_BOX_PERCENTILE_LOW', func=func_name)
    box_perc_high = pcheck(params, 'LOC_BOX_PERCENTILE_HIGH', func=func_name)
    # the size of the pecentile filter - should be a bit bigger than the
    # inter-order gap
    perc_filter_size = pcheck(params, 'LOC_PERCENTILE_FILTER_SIZE',
                              func=func_name)
    # the fiber dilation number of iterations this should only be used when
    #     we want a combined localisation solution i.e. AB from A and B
    fiber_dilate_iterations = pcheck(params, 'LOC_FIBER_DILATE_ITERATIONS',
                                     func=func_name)
    # the minimum area (number of pixels) that defines an order
    min_area = pcheck(params, 'LOC_MIN_ORDER_AREA', func=func_name)
    # Order of polynomial to fit for positions
    order_fit = pcheck(params, 'LOC_CENT_POLY_DEG', func=func_name)
    # range width size (used to fit the width of the orders at certain points)
    range_width_sum = pcheck(params, 'LOC_RANGE_WID_SUM', func=func_name)
    # define the minimum and maximum detector position where the centers of
    #   the orders should fall
    ydet_min = pcheck(params, 'LOC_YDET_MIN', func=func_name)
    ydet_max = pcheck(params, 'LOC_YDET_MAX', func=func_name)

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
    # print progress
    # TODO: move to language database
    msg = 'Finding and fitting orders for fiber = {0}'
    margs = [fiber]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # get the shape of the image
    nbypix, nbxpix  = image.shape
    # set NaN pixels to zero to avoid warnings later on
    image[~np.isfinite(image)] = 0
    # -------------------------------------------------------------------------
    # print progress
    # TODO: move to language database
    WLOG(params, '', '\tMasking orders')
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
        tmp = tmp  / 2.0 + zp
        # pad the threshold map
        maptmp = np.repeat(tmp, binsize).reshape([nbypix, binsize])
        threshold[:, bin_it:bin_it + binsize] = maptmp
    # -------------------------------------------------------------------------
    # create a binary mask that will indicate if a pixel is in or out of orders
    mask_orders = image > threshold
    # mask the edges to avoid problems
    mask_orders[0:binsize] = 0
    mask_orders[:, 0:binsize] = 0
    mask_orders[:, -binsize:] = 0
    mask_orders[-binsize:, :] = 0
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
    # find the regions that define the orders
    # the map contains integer values that are common to all pixels that form
    # a region in the binary mask
    all_labels = measure.label(mask_orders, connectivity=2)
    label_props = measure.regionprops(all_labels)
    # find the area of all regions, we know that orders cover many pixels
    area = []
    for label_prop in label_props:
        area.append(label_prop.area)
    # these areas are considered orders. This is just a first guess we will
    #   confirm these later - we have to add 1 as measure.label defines "0" as
    #   the "background" - this is not an order
    is_order = np.where(np.array(area) > min_area)[0] + 1
    # log how many blobs were found
    # TODO: move to language database
    msg = '\tFound {0} order blobs'
    margs = [len(is_order)]
    WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # storage for fit the x vs y position per region
    all_fits = np.zeros([len(is_order), order_fit + 1])
    # storage for position of fit at center of images
    order_centers = np.zeros(len(is_order))
    # storage for the width of orcer
    order_widths = np.zeros([len(is_order), 3])

    # loop through orders
    for order_num in range(len(is_order)):
        # ---------------------------------------------------------------------
        # find x y position of the region considered to be an order
        xy = label_props[is_order[order_num] - 1].coords
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
        for ibin in range(3):
            # get the pixels within this part of the detector
            pos = np.abs(xpos - (ibin + 1) * nbxpix / 4)
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
        cent_fit = np.polyfit(xpos - nbxpix / 2, ypos, order_fit)
        # save fit to all fits
        all_fits[order_num] = cent_fit
        # position of the order at the center of the image
        order_centers[order_num] = np.polyval(cent_fit, 0)
    # -------------------------------------------------------------------------
    # keep only orders that have a center within the allowed y range
    keep = (order_centers > ydet_min) & (order_centers < ydet_max)
    # log how many orders we are keeping
    # TODO: move to language database
    msg = '\tKeeping {0} order'
    margs = [np.sum(keep)]
    WLOG(params, '', msg.format(*margs))

    # apply keep mask to centers and widths
    order_centers = order_centers[keep]
    order_widths = order_widths[keep]
    all_fits = all_fits[keep]
    # -------------------------------------------------------------------------
    # sort all regions in increasing y value
    sortmask = np.argsort(order_centers)
    order_centers = order_centers[sortmask]
    order_widths = order_widths[sortmask]
    all_fits = all_fits[sortmask]
    # -------------------------------------------------------------------------
    # plot the width of the regions as a function of y position
    recipe.plot('LOC_WIDTH_REGIONS', centers=order_centers, widths=order_widths,
                image=image)
    # -------------------------------------------------------------------------
    # if orders come in doublets the gap between orders will therefore be nearly
    #    constant if we step from A to B and vary if we step from B to next
    #    orders A. We use that to identify which orders match and remove the
    #    other orders
    if fiber_doublets:
        index = np.arange(len(order_centers))
        cent_fit = np.polyfit(index, order_centers, order_fit)
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
        other_widths = order_widths[keep]
        all_fits = all_fits[keep]
    # -------------------------------------------------------------------------
    # find the gap between consecutive orders and use this to confirm the
    #    numbering
    orderdiff = order_centers[1:] - order_centers[:-1]
    fit_gap, gapmask = mp.robust_polyfit(order_centers[1:], orderdiff, 3, 5)
    # -------------------------------------------------------------------------
    recipe.plot('LOC_GAP_ORDERS', centers=order_centers, mask=gapmask,
                fit=fit_gap)
    # -------------------------------------------------------------------------
    # use the robust polyfit mask to determine which order is valid
    valid_order_centers = order_centers[1:][gapmask]
    valid_gap = (order_centers[1:] - order_centers[:-1])[gapmask]
    valid_fits = all_fits[1:][gapmask]
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
    nth_ord = np.ones(order_fit + 1, dtype=float)
    # for the intercept, we use a high-order-fit
    nth_ord[-1] = 11
    # for the slope, we use a high-order fit
    nth_ord[-2] = 5
    # for the curvature, we use a high-order-fit
    nth_ord[-3] = 3
    # -------------------------------------------------------------------------
    # force continuity between the localisation parameters
    for it in range(valid_fits.shape[1]):
        # robustly fit in the order direction
        cfit, cmask = mp.robust_polyfit(index2, valid_fits[:, it],
                                        nth_ord[it], 5)
        # update the full fits
        fits_full[:, it] = np.polyval(cfit, index_full)
    # get the central pixel position (note x=0 at the center here)
    for it in range(fits_full.shape[0]):
        center_full[it] = np.polyval(fits_full[it], 0)
    # -------------------------------------------------------------------------
    # keep only orders that have a center within the allowed y range
    keep = (center_full > ydet_min) & (center_full < ydet_max)
    # copy to the final center fits
    final_cent_fit = fits_full[keep]
    # -------------------------------------------------------------------------
    # log final number of orders
    msg = 'Final number of Orders: {0}'
    margs = [final_cent_fit.shape[0]]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # plot first and final fit over image
    recipe.plot('LOC_IMAGE_FIT', image=image, coeffs_old=all_fits,
                coeffs=final_cent_fit, kind=fiber, reverse=False,
                offset=-nbxpix//2, xlines=[nbxpix//2],
                ylines=[ydet_min, ydet_max])
    # -------------------------------------------------------------------------
    # convert back to start at x = 0
    xpix = np.arange(nbxpix)
    for order_num in range(len(final_cent_fit)):
        # get the current y values (centers at x half detector width)
        ypix = np.polyval(final_cent_fit[order_num], xpix - nbxpix // 2)
        # push into the final center fit
        final_cent_fit[order_num] = np.polyfit(xpix, ypix, order_fit)
    # -------------------------------------------------------------------------
    # need a final_wid_fit
    # TODO: add this
    final_width_fit = np.zeros_like(final_cent_fit)

    return final_cent_fit, final_width_fit


def merge_coeffs(params: ParamDict,
                 ldict: Dict[str, tuple]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Deal with merging A and B solutions (for SPIRou) - this is just because
    :param params:
    :param ldict:
    :return:
    """
    # get the fibers we have in ldict
    _fibers = list(ldict.keys())
    # merge lidct into a single array
    if len(_fibers) == 1:
        # get coefficients - need to be flipped
        cent_coeffs = ldict[_fibers[0]][0][:, ::-1]
        wid_coeffs = ldict[_fibers[0]][1][:, ::-1]
        # return arrays
        return np.array(cent_coeffs), np.array(wid_coeffs)
    else:
        # get the first fibers values (to get the number of orders)
        fiber0 = _fibers[0]
        cent_coeffs0 = ldict[fiber0][0]
        # get the number of orders
        nbo = cent_coeffs0.shape[0]
        # storage for output
        cent_coeffs, wid_coeffs = [], []
        # loop around orders
        for order_num in range(nbo):
            for _fiber in list(_fibers):

                fiber_nbo = len(ldict[_fiber][0])
                # must check we have the same number of orders
                if fiber_nbo != nbo:
                    # TODO: move to language database
                    emsg = ('Inconsistent number of orders between {0} (={1})'
                            ' and {2} (={3})')
                    eargs = [fiber0, nbo, _fiber, fiber_nbo]
                    WLOG(params, 'error', emsg.format(*eargs))
                # add to merged coeffs - need to be flipped
                cent_coeffs.append(ldict[_fiber][0][order_num][::-1])
                wid_coeffs.append(ldict[_fiber][1][order_num][::-1])
        # convert to numpy arrays
        cent_coeffs = np.array(cent_coeffs)
        wid_coeffs = np.array(wid_coeffs)
        # return arrays
        return cent_coeffs, wid_coeffs


# TODO: not used any more?
def check_coeffs(params, recipe, image, coeffs, fiber, kind=None):
    """
    Check and correct the coefficients by rejecting misbehaving coefficients
    and smoothing with a robust fit

    :param coeffs:

    :return:
    """
    # get the sigma clipping cut off value
    nsigclip = params['LOC_COEFF_SIGCLIP']
    coeffdeg = params['LOC_COEFFSIG_DEG']
    # ----------------------------------------------------------------------
    # get fiber params
    pconst = constants.pload()
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)
    max_num_orders = fiberparams['FIBER_MAX_NUM_ORDERS']
    set_num_fibers = fiberparams['FIBER_SET_NUM_FIBERS']
    num_fibers = max_num_orders / set_num_fibers
    # ----------------------------------------------------------------------
    # make sure coeffs is a numpy array
    coeffs = np.array(coeffs)
    # get the shape of coefficients
    nbo, nbcoeff = coeffs.shape
    # get the image shape
    dim1, dim2 = image.shape
    # ----------------------------------------------------------------------
    # define an x array and we'll determine the position along each order as a
    # matrix of y values. These will be sanitized and used to compute new coeffs
    xpix = np.linspace(0, dim2, nbcoeff * 10, dtype=float)
    # y matrix full of zeros
    ypix = np.zeros([nbo, len(xpix)])
    # fill in ypix
    for order_num in range(nbo):
        ypix[order_num] = np.polyval(coeffs[order_num][::-1], xpix)
    # sanity check
    ypix_ini = np.array(ypix)
    # ----------------------------------------------------------------------
    # storage of output values
    new_coeffs = np.zeros_like(coeffs)
    # we loop through fiber A and B and sanitize y position independently
    for mod in range(int(nbo // num_fibers)):
        # log progress
        WLOG(params, '', textentry('40-013-00026', args=[mod]))
        # index of Nth diffraction order
        index = np.arange(nbo)
        # keep either fiber A or B using modulo
        index = index[(index % (nbo // num_fibers)) == mod]
        # loop through xpix values and sanitize ypix values. y pix is fitted
        # with a sigma-clipped 6 or 7th order polynomial
        for it in range(len(xpix)):
            # only use in the fit values falling on the science array. Otherwise
            # the values are unconstrainted by flat field frames
            good = (ypix[index, it] > 0) & (ypix[index, it] < dim2)
            # robust polynomial fit
            fit, keep = mp.robust_polyfit(index[good], ypix[index, it][good],
                                          coeffdeg, nsigclip)
            # put values back in the ypix matri
            ypix[index, it] = np.polyval(fit, index)
    # ----------------------------------------------------------------------
    # storage for plotting
    good_arr = []
    ypix2 = []
    # ----------------------------------------------------------------------
    # re-fit the coefficients
    for order_num in range(nbo):
        # fit the order position using the sanitized ypix values
        good = (ypix[order_num] > 0) & (ypix[order_num] < dim2)
        # use the same order of coefficient
        new_coeff_ord = np.polyfit(xpix[good], ypix[order_num, good], nbcoeff - 1)
        # push into new array
        new_coeffs[order_num] = new_coeff_ord[::-1]
        # add update y values (for plotting)
        ypix2.append(np.polyval(new_coeff_ord, xpix))
        # storage for plotting
        good_arr.append(good)
    # make ypix2 an array
    ypix2 = np.array(ypix2)
    # ----------------------------------------------------------------------
    # plot of the coeffs
    recipe.plot('LOC_CHECK_COEFFS', ypix=ypix2, ypix0=ypix_ini,
                xpix=xpix, good=good_arr, kind=kind, image=image)
    # ----------------------------------------------------------------------
    return new_coeffs


# TODO: not used any more?
def check_coeffs_nirps(params: ParamDict, recipe: DrsRecipe, image: np.ndarray,
                       cent_coeffs: np.ndarray, wid_coeffs: np.ndarray,
                       fiber: str, max_nord: Union[int, None] = None
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Function to check whether we have missed any orders and add them back
    if we have (based on other orders and the step between orders)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance that called this function
    :param image: np.ndarray, an image on the detector (used for shape)
    :param cent_coeffs: np.ndarray, the coefficients of the center positions
    :param wid_coeffs: np.ndarray, the coefficients of the widths
    :param fiber: str, the fiber we are checking
    :param max_nord: int or None, if sets overrides FIBER_MAX_NUM_ORDERS from
                     pseudo constants pconst.FIBER_SETTINGS dictionary

    :return: tuple, 1. the updated cent_coeffs, 2. the updated wid_coeffs
    """
    # set function name
    func_name = display_func('check_coeffs_nirps', __NAME__)
    # get fiber params
    pconst = constants.pload()
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)
    # get the sigma clipping cut off value
    nsigclip = params['LOC_COEFF_SIGCLIP']
    coeffdeg = params['LOC_COEFFSIG_DEG']
    ycut = params['LOC_MAX_YPIX_VALUE']
    max_num_orders = pcheck(params, 'FIBER_MAX_NUM_ORDERS',
                            override=max_nord, func=func_name,
                            paramdict=fiberparams)
    # get the shapes
    nbypix, nbxpix = image.shape
    nbo, nccoeffs = cent_coeffs.shape
    _, nwcoeffs = wid_coeffs.shape
    # define the x pixel positions
    xpix = np.arange(nbxpix)
    ypix = np.arange(nbypix)
    # -------------------------------------------------------------------------
    # identify centers of all orders (based on current coefficients)
    centers = []
    for ordernum in range(nbo):
        centers.append(np.polyval(cent_coeffs[ordernum][::-1], nbxpix // 2))
    # -------------------------------------------------------------------------
    # find the indices of each order by extrapolating the neighbour's positions
    indices = np.arange(nbo)
    for ordernum in range(1, nbo - 1):
        # get the previous step
        diff_before = centers[ordernum] - centers[ordernum - 1]
        step_prev = diff_before / (indices[ordernum] - indices[ordernum - 1])
        # get the integer steps
        diff_after = centers[ordernum + 1] - centers[ordernum]
        nstep = np.round(diff_after / step_prev).astype(int)
        # add the next index
        indices[ordernum + 1] = indices[ordernum] + nstep
    # -------------------------------------------------------------------------
    # new shape of the coefficient matrix
    new_cen_coeffs = np.zeros([np.max(indices) + 1, nccoeffs]) + np.nan
    new_wid_coeffs = np.zeros([np.max(indices) + 1, nwcoeffs]) + np.nan
    new_nbo = new_cen_coeffs.shape[0]
    # fill known orders
    new_cen_coeffs[indices, :] = cent_coeffs
    new_wid_coeffs[indices, :] = wid_coeffs
    # find position of each order from coefficients
    ordermap = np.zeros([nbypix, np.max(indices) + 1]) + np.nan
    widthmap = np.zeros([nbypix, np.max(indices) + 1]) + np.nan
    # construct an order map that will be fitted
    # loop around orders
    for ordernum in range(new_nbo):
        # calculate y positions (centers)
        cypix = np.polyval(new_cen_coeffs[ordernum, ::-1], ypix)
        # push into order map
        ordermap[:, ordernum] = cypix
        # calcaulte y positions (width)
        wypix = np.polyval(new_wid_coeffs[ordernum, ::-1], ypix)
        # push into width map
        widthmap[:, ordernum] = wypix
    # -------------------------------------------------------------------------
    # remove bad values (out of bounds)
    with warnings.catch_warnings(record=True) as _:
        # remove pixels that are off the bottom of the image
        ordermap[ordermap < 0] = np.nan
        # remove pixels that are off the top of the image
        ordermap[ordermap > nbypix] = np.nan
        # remove parts of the polyfit which curve the wrong way
        ordermap[np.gradient(np.gradient(ordermap, axis=0), axis=0) > 0] = np.nan
    # fixing continuity of orders - remove discontinuities that arise from the
    #   polynomial going out of bounds and back into bounds
    for ordernum in range(new_nbo):
        # find the NaN positions in the order map (left side of detector)
        ppos1 = np.where(~np.isfinite(ordermap[:nbxpix // 2, ordernum]))[0]
        if len(ppos1) > 0:
            # remove all pixels where the polyfit is not valid (from left
            #   side of detector)
            cut1 = np.max(ppos1)
            ordermap[:cut1, ordernum] = np.nan
        # find the NaN positions in the order map (right side of detector)
        ppos2 = np.where(~np.isfinite(ordermap[nbxpix // 2:, ordernum]))[0]
        if len(ppos2) > 0:
            # remove all pixels where the polyfit is not valid (from right
            #   side of detector)
            cut2 = np.min(ppos2)
            ordermap[cut2 + nbxpix // 2:, ordernum] = np.nan
    # -------------------------------------------------------------------------
    # clean-up the order map
    for y_it in range(nbypix):
        orders = np.arange(new_nbo)
        # polyfit across the orders (in y direction for centers)
        cfit, mask = mp.robust_polyfit(orders, ordermap[y_it, :], coeffdeg,
                                       nsigclip)
        # re-fit the coefficients and push into ordermap
        ordermap[y_it, :] = np.polyval(cfit, orders)
        # polyfit across the orders (in y direction for widths)
        wfit, mask = mp.robust_polyfit(orders, widthmap[y_it, :], coeffdeg,
                                       nsigclip)
        # re-fit the coefficients and push into ordermap
        widthmap[y_it, :] = np.polyval(wfit, orders)

    # -------------------------------------------------------------------------
    # only keep those orders below our y-threshold cut
    order_mask = np.where(np.max(ordermap, axis=0) < ycut)[0][-max_num_orders:]
    # re-shape ordermap and widthmap
    ordermap = ordermap[:, order_mask]
    widthmap = widthmap[:, order_mask]
    # reset new_cen_coeffs and new_wid_coeffs
    new_cen_coeffs = np.zeros([max_num_orders, nccoeffs])
    new_wid_coeffs = np.zeros([max_num_orders, nwcoeffs])
    # reset nbo
    nbo = int(max_num_orders)
    # -------------------------------------------------------------------------
    # re-fit the localisation polynomials
    for ordernum in range(nbo):
        # work out the new polynomials for this order (for centers)
        ocen_coeffs = np.polyfit(ypix, ordermap[:, ordernum], nccoeffs - 1)
        # must flip these backwards
        new_cen_coeffs[ordernum, :] = ocen_coeffs[::-1]
        # work out the new polynomials for this order (for widths)
        owid_coeffs = np.polyfit(ypix, widthmap[:, ordernum], nwcoeffs - 1)
        # must flip these backwards
        new_wid_coeffs[ordernum, :] = owid_coeffs[::-1]
    # -------------------------------------------------------------------------
    # make arrays for plotting
    cypix2, cypix1 = np.zeros([nbo, nbxpix]), np.zeros([nbo, nbxpix])
    good_arr = np.ones([nbo, nbxpix]).astype(bool)
    wypix2, wypix1 = np.zeros([nbo, nbxpix]), np.zeros([nbo, nbxpix])
    # loop around orders and fill in values
    for ordernum in range(nbo):
        cypix2[ordernum] = np.polyval(new_cen_coeffs[ordernum][::-1], xpix)
        cypix1[ordernum] = np.polyval(cent_coeffs[ordernum][::-1], xpix)
        wypix2[ordernum] = np.polyval(new_wid_coeffs[ordernum][::-1], xpix)
        wypix1[ordernum] = np.polyval(wid_coeffs[ordernum][::-1], xpix)
    # plot of the coeffs
    recipe.plot('LOC_CHECK_COEFFS', ypix=cypix2, ypix0=cypix1,
                xpix=xpix, good=good_arr, kind='center', image=image)
    recipe.plot('LOC_CHECK_COEFFS', ypix=wypix2, ypix0=wypix1,
                xpix=xpix, good=good_arr, kind='width', image=image)
    # -------------------------------------------------------------------------
    # return new centers and widths
    return new_cen_coeffs, new_wid_coeffs


# TODO: not used any more?
def find_and_fit_localisation(params, recipe, image, sigdet, fiber, **kwargs):
    func_name = __NAME__ + '.find_and_fit_localisation()'

    # get fiber params
    pconst = constants.pload()
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)

    # ----------------------------------------------------------------------
    # get constants from p
    # ----------------------------------------------------------------------
    row_offset = pcheck(params, 'LOC_START_ROW_OFFSET', 'row_offset', kwargs,
                        func=func_name)
    central_col = pcheck(params, 'LOC_CENTRAL_COLUMN', 'central_col', kwargs,
                         func=func_name)
    horder_size = pcheck(params, 'LOC_HALF_ORDER_SPACING', 'horder_size',
                         kwargs, func=func_name)
    minpeak_amp = pcheck(params, 'LOC_MINPEAK_AMPLITUDE', 'minpeak_amp',
                         kwargs, func=func_name)
    back_thres = pcheck(params, 'LOC_BKGRD_THRESHOLD', 'back_thres', kwargs,
                        func=func_name)
    first_order = pcheck(params, 'FIBER_FIRST_ORDER_JUMP', 'first_order',
                         kwargs, func=func_name, paramdict=fiberparams)
    max_num_orders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', 'max_num_orders',
                            kwargs, func=func_name, paramdict=fiberparams)
    num_fibers = pcheck(params, 'FIBER_SET_NUM_FIBERS', 'num_fibers', kwargs,
                        func=func_name, paramdict=fiberparams)
    wid_poly_deg = pcheck(params, 'LOC_WIDTH_POLY_DEG', 'wid_poly_deg', kwargs,
                          func=func_name)
    cent_poly_deg = pcheck(params, 'LOC_CENT_POLY_DEG', 'cent_poly_deg',
                           kwargs, func=func_name)
    locstep = pcheck(params, 'LOC_COLUMN_SEP_FITTING', 'locstep', kwargs,
                     func=func_name)
    ext_window = pcheck(params, 'LOC_EXT_WINDOW_SIZE', 'ext_window', kwargs,
                        func=func_name)
    image_gap = pcheck(params, 'LOC_IMAGE_GAP', 'image_gap', kwargs,
                       func=func_name)
    widthmin = pcheck(params, 'LOC_ORDER_WIDTH_MIN', 'widthmin', kwargs,
                      func=func_name)
    nm_thres = pcheck(params, 'LOC_NOISE_MULTIPLIER_THRES', 'nm_thres', kwargs,
                      func=func_name)
    max_rms_cent = pcheck(params, 'LOC_MAX_RMS_CENT', 'max_rms_cent', kwargs,
                          func=func_name)
    max_ptp_cent = pcheck(params, 'LOC_MAX_PTP_CENT', 'max_ptp_cent', kwargs,
                          func=func_name)
    ptporms_cent = pcheck(params, 'LOC_PTPORMS_CENT', 'ptporms_cent', kwargs,
                          func=func_name)
    max_rms_wid = pcheck(params, 'LOC_MAX_RMS_WID', 'max_rms_wid', kwargs,
                         func=func_name)
    max_ptp_wid = pcheck(params, 'LOC_MAX_PTP_WID', 'max_ptp_wid', kwargs,
                         func=func_name)
    center_drop = pcheck(params, 'LOC_ORDER_CURVE_DROP', 'curve_drop', kwargs,
                         func=func_name)
    # ----------------------------------------------------------------------
    # Step 1: Measure and correct background on the central column
    # ----------------------------------------------------------------------
    # clip the data - start with the ic_offset row and only
    # deal with the central column column=ic_cent_col
    y = np.nanmedian(image[row_offset:, central_col - 10:central_col + 10], axis=1)
    # measure min max of box smoothed central col
    miny, maxy = mp.measure_box_min_max(y, horder_size)
    max_signal = np.nanpercentile(y, 95)
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
    # plot y, miny and maxy
    recipe.plot('LOC_MINMAX_CENTS', y=y, mask=goodmask, miny=miny, maxy=maxy)

    # ----------------------------------------------------------------------
    # Step 2: Search for order center on the central column - quick
    #         estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', textentry('40-013-00005'))
    # plot the minimum of ycc and back_thres
    recipe.plot('LOC_MIN_CENTS_THRES', centers=ycc, threshold=back_thres)
    # find the central positions of the orders in the central
    posc_all = find_position_of_cent_col(ycc, back_thres)
    # depending on the fiber type we may need to skip some pixels and also
    # we need to add back on the ic_offset applied
    posc = posc_all[first_order:] + row_offset
    # work out the number of orders to use (minimum of ic_locnbmaxo and number
    #    of orders found in 'LocateCentralOrderPositions')
    num_orders = mp.nanmin([max_num_orders, len(posc)])
    norm_num_orders = int(num_orders / num_fibers)
    # log the number of orders than have been detected
    wargs = [fiber, norm_num_orders, num_fibers]
    WLOG(params, 'info', textentry('40-013-00006', args=wargs))
    # ----------------------------------------------------------------------
    # Step 3: Search for order center and profile on specific columns
    # ----------------------------------------------------------------------
    cent_0 = np.zeros((num_orders, image.shape[1]), dtype=float)
    wid_0 = np.zeros((num_orders, image.shape[1]), dtype=float)
    # Create arrays to store coefficients for position and width
    cent_coeffs = np.zeros((num_orders, cent_poly_deg + 1))
    wid_coeffs = np.zeros((num_orders, wid_poly_deg + 1))
    # Create arrays to store rms values for position and width
    cent_rms = np.zeros(num_orders)
    wid_rms = np.zeros(num_orders)
    # Create arrays to store point to point max value for position and width
    cent_max_ptp = np.zeros(num_orders)
    cent_frac_ptp = np.zeros(num_orders)
    wid_max_ptp = np.zeros(num_orders)
    wid_frac_ptp = np.zeros(num_orders)
    # Create arrays to store rejected points
    cent_max_rmpts = np.zeros(num_orders)
    wid_max_rmpts = np.zeros(num_orders)
    # storage for plotting
    xplot, yplot = [], []
    # ----------------------------------------------------------------------
    # set the central col centers in the cpos_orders array
    cent_0[:, central_col] = posc[0:num_orders]
    # ----------------------------------------------------------------------
    # storage for plotting
    dvars = OrderedDict()
    plimits = OrderedDict()
    # loop around each order
    rorder_num = 0
    # loop around orders
    for order_num in range(num_orders):
        # get the shape of the image
        nx2 = image.shape[1]
        # ------------------------------------------------------------------
        # get columns (start from the center and work outwards right side
        # first the left side) the order of these seems weird but we
        # calculate row centers from the central col (posc) to the RIGHT
        # edge then calculate the center pixel again from the
        # "central col+locstep" pixel (first column calculated) then we
        # calculate row centers to the LEFT edge - hence the order of columns
        columns = list(range(central_col + locstep, nx2 - locstep, locstep))
        columns += list(range(central_col - locstep, locstep, -locstep))
        # ------------------------------------------------------------------
        # storage for plotting
        col_vals, maxycc, minxcc, maxxcc = [], -np.inf, np.inf, -np.inf
        # loop around each column to get the order row center position from
        # previous central measurement.
        # For the first iteration this uses "posc" for all other iterations
        # uses the central position found at the nearest column to it
        # must also correct for conversion to int by adding 0.5
        # center, width = 0, 0
        columns = np.array(columns)

        columns = columns[np.argsort(np.abs(columns - central_col))]

        for col in columns:
            # for pixels>central pixel we need to get row center from last
            # iteration (or posc) this is to the LEFT
            if col > central_col:
                rowcenter = int(cent_0[order_num, col - locstep] + 0.5)
            # for pixels<=central pixel we need to get row center from last
            # iteration this ir to the RIGHT
            else:
                rowcenter = int(cent_0[order_num, col + locstep] + 0.5)
            # need to define the extraction window edges
            rowtop, rowbottom = (rowcenter - ext_window), (
                    rowcenter + ext_window)
            # now make sure our extraction isn't out of bounds
            if rowtop <= 0 or rowbottom >= nx2:
                break
            # get the pixel values between row bottom and row top for
            # this column
            # median over whole box of pixels to avoid outliers
            imagebox = image[rowtop:rowbottom, col:col + locstep]
            # get the values
            ovalues = mp.nanmedian(imagebox, axis=1)
            # as we are not normalised threshold needs multiplying by
            # the maximum value
            threshold = mp.nanmax(ovalues) * back_thres
            # find the row center position and the width of the order
            # for this column
            lkwargs = dict(values=ovalues, threshold=threshold,
                           min_width=widthmin)
            center, width = locate_order_center(**lkwargs)
            # need to add on row top (as centers are relative positions)
            center = center + rowtop
            # if the width is zero set the position back to the original
            # position
            if width == 0:
                # to force the order curvature
                center = float(rowcenter) - center_drop
            # add these positions to storage
            cent_0[order_num, col] = center
            wid_0[order_num, col] = width
            # debug plot parameters
            if np.nanmax(ovalues) > maxycc:
                maxycc = np.nanmax(ovalues)
            if (rowtop - center) < minxcc:
                minxcc = rowtop - center
            if (rowbottom - center) > maxxcc:
                maxxcc = rowbottom - center
            col_val = [rowcenter, rowtop, rowbottom, center, width, ovalues]
            col_vals.append(col_val)
        # append col vals to order storage
        dvars[order_num] = col_vals
        plimits[order_num] = [minxcc, maxxcc, 0, maxycc]
        # ------------------------------------------------------------------
        # only keep the orders with non-zero width
        mask = wid_0[order_num, :] != 0
        # get the x pixels where we have non-zero width
        xpix = np.arange(image.shape[1])[mask]
        # check that we have enough data points to fit data
        if len(xpix) > (mp.nanmax([wid_poly_deg, cent_poly_deg]) + 1):
            # --------------------------------------------------------------
            # initial fit for center positions for this order
            cent_y = cent_0[rorder_num, :][mask]
            iofargs = [params, xpix, cent_y, cent_poly_deg, central_col]
            cf_data = initial_order_fit(*iofargs, kind='center')
            # append centers for plot
            xplot.append(xpix), yplot.append(cent_y)
            # --------------------------------------------------------------
            # initial fit for widths for this order
            wid_y = wid_0[rorder_num, :][mask]
            iofargs = [params, xpix, wid_y, wid_poly_deg, central_col]
            wf_data = initial_order_fit(*iofargs, kind='fwhm')
            # --------------------------------------------------------------
            # Log order number and fit at central pixel and width and rms
            wargs = [rorder_num, cf_data['cfitval'], wf_data['cfitval'],
                     cf_data['rms']]
            WLOG(params, '', textentry('40-013-00007', args=wargs))
            # --------------------------------------------------------------
            # sigma fit params for center
            sigfargs = [params, recipe, xpix, cent_y, cf_data, cent_poly_deg,
                        cent_max_rmpts[rorder_num], rorder_num]
            sigfkwargs = dict(ic_max_ptp=max_ptp_cent, ic_max_ptp_frac=None,
                              ic_ptporms=ptporms_cent, ic_max_rms=max_rms_cent,
                              kind='center')
            # sigma clip fit for center positions for this order
            cf_data = sigmaclip_order_fit(*sigfargs, **sigfkwargs)
            # load results into storage arrays for this order
            cent_coeffs[rorder_num] = cf_data['a']
            cent_rms[rorder_num] = cf_data['rms']
            cent_max_ptp[rorder_num] = cf_data['max_ptp']
            cent_frac_ptp[rorder_num] = cf_data['max_ptp_frac']
            cent_max_rmpts[rorder_num] = cf_data['max_rmpts']
            # --------------------------------------------------------------
            # sigma fit params for width
            sigfargs = [params, recipe, xpix, wid_y, wf_data, wid_poly_deg,
                        wid_max_rmpts[rorder_num], rorder_num]
            sigfkwargs = dict(ic_max_ptp=-np.inf, ic_max_ptp_frac=max_ptp_wid,
                              ic_ptporms=None, ic_max_rms=max_rms_wid,
                              kind='fwhm')
            # sigma clip fit for width positions for this order
            wf_data = sigmaclip_order_fit(*sigfargs, **sigfkwargs)
            # load results into storage arrays for this order
            wid_coeffs[rorder_num] = wf_data['a']
            wid_rms[rorder_num] = wf_data['rms']
            wid_max_ptp[rorder_num] = wf_data['max_ptp']
            wid_frac_ptp[rorder_num] = wf_data['max_ptp_frac']
            wid_max_rmpts[rorder_num] = wf_data['max_rmpts']
            # --------------------------------------------------------------
            # increase the roder_num iterator
            rorder_num += 1
        # else log that the order is unusable
        else:
            WLOG(params, '', textentry('40-013-00010'))
    # plot finding orders plot
    recipe.plot('LOC_FINDING_ORDERS', plotdict=dvars, plimits=plimits)
    # ----------------------------------------------------------------------
    # Log that the order geometry has been measured
    wargs = [fiber, rorder_num]
    WLOG(params, 'info', textentry('40-013-00011', args=wargs))
    # get the mean rms values
    mean_rms_cent = mp.nansum(cent_rms[:rorder_num]) * 1000 / rorder_num
    mean_rms_wid = mp.nansum(wid_rms[:rorder_num]) * 1000 / rorder_num
    # Log mean rms values
    WLOG(params, 'info', textentry('40-013-00012', args=[mean_rms_cent]))
    WLOG(params, 'info', textentry('40-013-00013', args=[mean_rms_wid]))
    # ----------------------------------------------------------------------
    # return
    outputs = [cent_0, cent_coeffs, cent_rms, cent_max_ptp, cent_frac_ptp,
               cent_max_rmpts, wid_0, wid_coeffs, wid_rms, wid_max_ptp,
               wid_frac_ptp, wid_max_rmpts, xplot, yplot, rorder_num,
               mean_rms_cent, mean_rms_wid, max_signal, mean_backgrd]
    return outputs


def image_superimp(image, coeffs):
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
        fity = np.polyval(coeffs[order_num][::-1], xdata) + 0.5
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


def get_coefficients(params, recipe, header, fiber, database=None, **kwargs):
    func_name = __NAME__ + '.get_coefficients()'
    # get pseudo constants
    pconst = constants.pload()
    # get parameters from params/kwargs
    merge = kwargs.get('merge', False)
    filename = kwargs.get('filename', None)
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
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # load loco file
    locofilepath = gen_calib.load_calib_file(params, key, header,
                                             filename=filename,
                                             userinputkey='LOCOFILE',
                                             database=calibdbm, fiber=usefiber,
                                             return_filename=True)
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
def loc_quality_control(params, fiber, cent_max_rmpts, wid_max_rmpts,
                        mean_rms_cent, mean_rms_wid, rorder_num, cent_fits):
    # set function name
    func_name = display_func('localisation_quality_control', __NAME__)
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # get qc parameters
    max_removed_cent = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_CTR',
                              func=func_name)
    max_removed_wid = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_WID',
                             func=func_name)
    rmsmax_cent = pcheck(params, 'QC_LOC_RMSMAX_CTR', func=func_name)
    rmsmax_wid = pcheck(params, 'QC_LOC_RMSMAX_WID', func=func_name)
    # this one comes from pseudo constants
    pconst = constants.pload()
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)

    required_norders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', func=func_name,
                              paramdict=fiberparams)
    # ----------------------------------------------------------------------
    # check that max number of points rejected in center fit is below
    #    threshold
    sum_cent_max_rmpts = mp.nansum(cent_max_rmpts)
    if sum_cent_max_rmpts > max_removed_cent:
        # add failed message to fail message list
        fargs = [sum_cent_max_rmpts, max_removed_cent]
        fail_msg.append(textentry('40-013-00014', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(sum_cent_max_rmpts)
    qc_names.append('sum(MAX_RMPTS_POS)')
    qc_logic.append('sum(MAX_RMPTS_POS) < {0:.2f}'
                    ''.format(sum_cent_max_rmpts))
    # ----------------------------------------------------------------------
    # check that  max number of points rejected in width fit is below
    #   threshold
    sum_wid_max_rmpts = mp.nansum(wid_max_rmpts)
    if sum_wid_max_rmpts > max_removed_wid:
        # add failed message to fail message list
        fargs = [sum_wid_max_rmpts, max_removed_wid]
        fail_msg.append(textentry('40-013-00015', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(sum_wid_max_rmpts)
    qc_names.append('sum(MAX_RMPTS_WID)')
    qc_logic.append('sum(MAX_RMPTS_WID) < {0:.2f}'
                    ''.format(sum_wid_max_rmpts))
    # ------------------------------------------------------------------
    if mean_rms_cent > rmsmax_cent:
        # add failed message to fail message list
        fargs = [mean_rms_cent, rmsmax_cent]
        fail_msg.append(textentry('40-013-00016', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mean_rms_cent)
    qc_names.append('mean_rms_center')
    qc_logic.append('mean_rms_center < {0:.2f}'.format(rmsmax_cent))
    # ------------------------------------------------------------------
    if mean_rms_wid > rmsmax_wid:
        # add failed message to fail message list
        fargs = [mean_rms_wid, rmsmax_wid]
        fail_msg.append(textentry('40-013-00017', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mean_rms_wid)
    qc_names.append('mean_rms_wid')
    qc_logic.append('mean_rms_wid < {0:.2f}'.format(rmsmax_wid))
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
    diff = np.diff(cent_fits, axis=0)
    negative_diff = np.min(diff) < 0
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
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params, passed


def write_localisation_files(params, recipe, infile, image, rawfiles, combine,
                             fiber, props, order_profile, mean_backgrd,
                             rorder_num, max_signal, cent_coeffs, wid_coeffs,
                             center_fits, width_fits, qc_params):
    # set function name
    func_name = display_func('write_localisation_files', __NAME__)
    # get qc parameters
    max_removed_cent = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_CTR',
                              func=func_name)
    max_removed_wid = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_WID',
                             func=func_name)
    rmsmax_cent = pcheck(params, 'QC_LOC_RMSMAX_CTR', func=func_name)
    rmsmax_wid = pcheck(params, 'QC_LOC_RMSMAX_WID', func=func_name)
    # this one comes from pseudo constants
    pconst = constants.pload()
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
    # add the calibration files use
    loco1file = gen_calib.add_calibs_to_header(loco1file, props)
    # add localisation parameters
    loco1file.add_hkey('KW_LOC_BCKGRD', value=mean_backgrd)
    loco1file.add_hkey('KW_LOC_NBO', value=rorder_num)
    loco1file.add_hkey('KW_LOC_DEG_C', value=params['LOC_CENT_POLY_DEG'])
    loco1file.add_hkey('KW_LOC_DEG_W', value=params['LOC_WIDTH_POLY_DEG'])
    loco1file.add_hkey('KW_LOC_MAXFLX', value=max_signal)
    loco1file.add_hkey('KW_LOC_SMAXPTS_CTR', value=max_removed_cent)
    loco1file.add_hkey('KW_LOC_SMAXPTS_WID', value=max_removed_wid)
    loco1file.add_hkey('KW_LOC_RMS_CTR', value=rmsmax_cent)
    loco1file.add_hkey('KW_LOC_RMS_WID', value=rmsmax_wid)
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


def loc_summary(recipe, it, params, qc_params, props, mean_backgrd, rorder_num,
                max_signal):
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_DPRTYPE', value=props['DPRTYPE'])
    recipe.plot.add_stat('KW_LOC_BCKGRD', value=mean_backgrd)
    recipe.plot.add_stat('KW_LOC_NBO', value=rorder_num)
    recipe.plot.add_stat('KW_LOC_DEG_C', value=params['LOC_CENT_POLY_DEG'])
    recipe.plot.add_stat('KW_LOC_DEG_W', value=params['LOC_WIDTH_POLY_DEG'])
    recipe.plot.add_stat('KW_LOC_MAXFLX', value=max_signal)
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
# Worker functions
# =============================================================================
def find_position_of_cent_col(values, threshold):
    """
    Finds the central positions based on the central column values

    :param values: numpy array (1D) size = number of rows,
                    the central column values
    :param threshold: float, the threshold above which to find pixels as being
                      part of an order

    :return position: numpy array (1D), size= number of rows,
                      the pixel positions in cvalues where the centers of each
                      order should be

    For 1000 loops, best of 3: 771 µs per loop
    """
    # store the positions of the orders
    positions = []
    # get the len of cvalues
    length = len(values)
    # initialise the row number to zero
    row, order_end = 0, 0
    # move the row number to the first row below threshold
    # (avoids first order on the edge)
    while values[row] > threshold:
        row += 1
        if row == length:
            break
    # continue to move through rows
    while row < length:
        # if row is above threshold then we have found a start point
        if values[row] > threshold:
            # save the start point
            order_start = row
            # continue to move through rows to find end (end of order defined
            # as the point at which it slips below the threshold)
            while values[row] >= threshold:
                row += 1
                # if we have reached the end of cvalues stop (it is an end of
                # an order by definition
                if row == length:
                    break
            # as we have reached the end we should not add to positions
            if row == length:
                break
            else:
                # else record the end position
                order_end = row
                # determine the center of gravity of the order
                # lx is the pixels in this order
                lx = np.arange(order_start, order_end, 1)
                # ly is the cvalues values in this order (use lx to get them)
                ly = values[lx]
                # position = sum of (lx * ly) / sum of sum(ly)
                position = mp.nansum(lx * ly * 1.0) / mp.nansum(ly)
                # append position and width to storage
                positions.append(position)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return np.array(positions)


def locate_order_center(values, threshold, min_width=None):
    """
    Takes the values across the oder and finds the order center by looking for
    the start and end of the order (and thus the center) above threshold

    :param values: numpy array (1D) size = number of rows, the pixels in an
                    order

    :param threshold: float, the threshold above which to find pixels as being
                      part of an order

    :param min_width: float, the minimum width for an order to be accepted

    :return positions: numpy array (1D), size= number of rows,
                       the pixel positions in cvalues where the centers of each
                       order should be

    :return widths:    numpy array (1D), size= number of rows,
                       the pixel positions in cvalues where the centers of each
                       order should be

    For 1000 loops, best of 3: 771 µs per loop
    """
    # deal with no min_width
    if min_width is None:
        min_width = 0
    # get the len of cvalues
    length = len(values)
    # initialise the row number to zero
    row, order_end = 0, 0
    position, width = 0, 0
    # move the row number to the first row below threshold
    # (avoids first order on the edge)
    while values[row] > threshold:
        row += 1
        if row == length:
            break
    # continue to move through rows
    while row < length and (order_end == 0):
        # if row is above threshold then we have found a start point
        if values[row] > threshold:
            # save the start point
            order_start = row
            # continue to move through rows to find end (end of order defined
            # as the point at which it slips below the threshold)
            while values[row] >= threshold:
                row += 1
                # if we have reached the end of cvalues stop (it is an end of
                # an order by definition
                if row == length:
                    break
            # as we have reached the end we should not add to positions
            if row == length:
                break
            elif (row - order_start) > min_width:
                # else record the end position
                order_end = row
                # determine the center of gravity of the order
                # lx is the pixels in this order
                lx = np.arange(order_start, order_end, 1)
                # ly is the cvalues values in this order (use lx to get them)
                ly = values[lx]
                # position = sum of (lx * ly) / sum of sum(ly)
                position = mp.nansum(lx * ly * 1.0) / mp.nansum(ly)
                # width is just the distance from start to end
                width = abs(order_end - order_start)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return position, width


def initial_order_fit(params, x, y, f_order, ccol, kind):
    """
    Performs a crude initial fit for this order, uses the ctro positions or
    sigo width values found in "FindOrderCtrs" or "find_order_centers" to do
    the fit

    :return fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['X'])
                where fity = Sum(a[i] * x^i)
            res = the residuals from y - fity
                 where y = ctro [kind='center'] or
                         = sigo [kind='fwhm'])
            abs_res = abs(res)
            rms = the standard deviation of the residuals
            max_ptp = maximum residual value max(res)
            max_ptp_frac = max_ptp / rms  [kind='center']
                         = max(abs_res/y) * 100   [kind='fwhm']
    """
    func_name = __NAME__ + '.initial_order_fit()'
    # deal with kind
    if kind not in ['center', 'fwhm']:
        WLOG(params, 'error', textentry('00-013-00002', args=[kind, func_name]))
    # -------------------------------------------------------------------------
    # calculate fit - coefficients, fit y params, residuals, absolute residuals,
    #                 rms and max_ptp
    # -------------------------------------------------------------------------
    acoeffs, fit, res, abs_res, rms, max_ptp = calculate_fit(x, y, f_order)
    # max_ptp_frac is different for different cases
    if kind == 'center':
        max_ptp_frac = max_ptp / rms
    else:
        max_ptp_frac = mp.nanmax(abs_res / y) * 100
    # -------------------------------------------------------------------------
    # Work out the fit value at ic_cent_col (for logging)
    cfitval = np.polyval(acoeffs[::-1], ccol)
    # -------------------------------------------------------------------------
    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac, cfitval=cfitval)
    return fitdata


def sigmaclip_order_fit(params, recipe, x, y, fitdata, f_order, max_rmpts,
                        rnum, ic_max_ptp, ic_max_ptp_frac, ic_ptporms,
                        ic_max_rms, kind):
    """
    Performs a sigma clip fit for this order, uses the ctro positions or
    sigo width values found in "FindOrderCtrs" or "find_order_centers" to do
    the fit. Removes the largest residual from the initial fit (or subsequent
    sigmaclips) value in x and y and recalculates the fit.

    Does this until all the following conditions are NOT met:
           rms > 'ic_max_rms'   [kind='center' or kind='fwhm']
        or max_ptp > 'ic_max_ptp [kind='center']
        or max_ptp_frac > 'ic_ptporms_center'   [kind='center']
        or max_ptp_frac > 'ic_max_ptp_frac'     [kind='fwhm'

    :param params:
    :param x:
    :param y:

    :param fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['X'])
                where fity = Sum(a[i] * x^i)
            res = the residuals from y - fity
                 where y = ctro [kind='center'] or
                         = sigo [kind='fwhm'])
            abs_res = abs(res)
            rms = the standard deviation of the residuals
            max_ptp = maximum residual value max(res)
            max_ptp_frac = max_ptp / rms  [kind='center']
                         = max(abs_res/y) * 100   [kind='fwhm']

    :param f_order:

    :param rnum: int, order number (running number of successful order
                 iterations only)
    :param kind: string, 'center' or 'fwhm', if 'center' then this fit is for
                 the central p

    :return fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['X'])
                where fity = Sum(a[i] * x^i)
            res = the residuals from y - fity
                 where y = ctro [kind='center'] or
                         = sigo [kind='fwhm'])
            abs_res = abs(res)
            rms = the standard deviation of the residuals
            max_ptp = maximum residual value max(res)
            max_ptp_frac = max_ptp / rms  [kind='center']
                         = max(abs_res/y) * 100   [kind='fwhm']
    """
    func_name = __NAME__ + '.sigmaclip_order_fit()'
    # deal with kind
    if kind not in ['center', 'fwhm']:
        WLOG(params, 'error', textentry('00-013-00003', args=[kind, func_name]))
    # extract constants from fitdata
    acoeffs = fitdata['a']
    fit = fitdata['fit']
    res = fitdata['res']
    abs_res = fitdata['abs_res']
    rms = fitdata['rms']
    max_ptp = fitdata['max_ptp']
    max_ptp_frac = fitdata['max_ptp_frac']

    # get variables dependent on kind
    if kind == 'center':
        # variables
        kind2, ptpfrackind = 'center', 'sigrms'
    else:
        # variables
        kind2, ptpfrackind = 'width ', 'ptp%'
    # -------------------------------------------------------------------------
    # Need to do sigma clip fit
    # -------------------------------------------------------------------------
    # define clipping mask
    wmask = np.ones(len(abs_res), dtype=bool)
    # get condition for doing sigma clip
    cond = rms > ic_max_rms
    if kind == 'center':
        cond |= max_ptp > ic_max_ptp
        cond |= (max_ptp_frac > ic_ptporms)
    else:
        cond |= (max_ptp_frac > ic_max_ptp_frac)
    # keep clipping until cond is met
    xo, yo = np.array(x), np.array(y)
    while cond:
        # Log that we are clipping the fit
        wargs = [kind, ptpfrackind, rms, max_ptp, max_ptp_frac]
        WLOG(params, '', textentry('40-013-00008', args=wargs))
        # add residuals to loc
        recipe.plot('LOC_FIT_RESIDUALS', x=x, y=res, xo=xo, rnum=rnum,
                    kind=kind)
        # add one to the max rmpts
        max_rmpts += 1
        # remove the largest residual (set wmask = 0 at that position)
        wmask[np.argmax(abs_res)] = False
        # get the new x and y values (without largest residual)
        xo, yo = xo[wmask], yo[wmask]
        # fit the new x and y
        fdata = calculate_fit(xo, yo, f_order)
        acoeffs, fit, res, abs_res, rms, max_ptp = fdata
        # max_ptp_frac is different for different cases
        if kind == 'center':
            max_ptp_frac = max_ptp / rms
        else:
            max_ptp_frac = mp.nanmax(abs_res / yo) * 100
        # recalculate condition for doing sigma clip
        cond = rms > ic_max_rms
        if kind == 'center':
            cond |= (max_ptp > ic_max_ptp)
            cond |= (max_ptp_frac > ic_ptporms)
        else:
            cond |= (max_ptp_frac > ic_max_ptp_frac)
        # reform wmask
        wmask = wmask[wmask]
    else:
        wargs = [kind2, ptpfrackind, rms, max_ptp, max_ptp_frac, int(max_rmpts)]
        WLOG(params, '', textentry('40-013-00009', args=wargs))

    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac,
                   max_rmpts=max_rmpts)
    return fitdata


def calculate_fit(x, y, f):
    """
    Calculate the polynomial fit between x and y, for "f" fit parameters,
    also calculate the residuals, absolute residuals, RMS and max peak-to-peak
    values

    :param x: numpy array (1D), the x values to use for the fit
    :param y: numpy array (1D), the y values to fit
    :param f: int, the number of fit parameters (i.e. for quadratic fit f=2)

    :return a: numpy array (1D), the fit coefficients
                        shape = f
    :return fit: numpy array (1D), the fit values for positions in x
                        shape = len(y) and len(x)
    :return res: numpy array (1D), the residuals between y and fit
                        shape = len(y) and len(x)
    :return abs_res: numpy array (1D), the absolute values of "res"  abs(res)
                        shape = len(y) and len(x)
    :return rms: float, the RMS (root-mean square) of the residuals (std)
    :return max_ptp: float, the max peak to peak value of the absolute
                     residuals i.e. max(abs_res)
    """
    # Do initial fit (revere due to fortran compatibility)
    a = mp.nanpolyfit(x, y, deg=f)[::-1]
    # Get the intial fit data
    fit = np.polyval(a[::-1], x)
    # work out residuals
    res = y - fit
    # Work out absolute residuals
    abs_res = abs(res)
    # work out rms
    rms = mp.nanstd(res)
    # work out max point to point of residuals
    max_ptp = mp.nanmax(abs_res)
    # return all
    return a, fit, res, abs_res, rms, max_ptp


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
