#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-08 at 16:32

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core import math
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.extraction.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define extraction functions
# =============================================================================
def extraction_twod(params, image, orderp, pos, **kwargs):

    func_name = __NAME__ + '.extraction_twod()'

    # get number of orders from params/kwargs
    start_order = pcheck(params, 'START_ORDER', 'start', kwargs, func_name)
    end_order = pcheck(params, 'END_ORDER', 'end', kwargs, func_name)
    range1 = pcheck(params, 'EXT_RANGE1', 'range1', kwargs, func_name)
    range2 = pcheck(params, 'EXT_RANGE2', 'range2', kwargs, func_name)
    skip_orders = pcheck(params, 'SKIP_ORDERS', 'skip', kwargs, func_name,
                         mapf='list')
    sigdet = pcheck(params, 'SIGDET', 'sigdet', kwargs, func_name)
    gain = pcheck(params, 'GAIN', 'gain', kwargs, func_name)
    cosmic = pcheck(params, 'EXT_COSMIC_CORRETION', 'cosmic', kwargs, func_name)
    cosmic_sigcut = pcheck(params, 'EXT_COSMIC_SIGCUT', 'cosmic_sigcuit',
                           kwargs, func_name)
    cosmic_thres = pcheck(params, 'EXT_COSMIC_THRESHOLD', 'cosmic_thres',
                           kwargs, func_name)

    blaze_size = pcheck(params, 'EXT_BLAZE_HALF_WINDOW')

    # get shame of image and number of orders
    dim1, dim2 = image.shape
    nbo = pos.shape[0]

    # check that orderp is same dimensions as image
    if image.shape != orderp.shape:
        eargs = [image.shape, orderp.shape]
        WLOG(params, 'error', TextEntry('00-016-00006', args=eargs))

    # construct order
    valid_orders = _valid_orders(params, start_order, end_order, skip_orders)

    # storage for all orders
    e2ds = np.zeros([nbo])
    e2dsll = []
    cpt = np.repeat([np.nan], nbo)

    # loop around orders
    for order_num in range(len(nbo)):
        # skip this order fill in with NaNs
        if order_num not in valid_orders:
            e2dsi = np.repeat([np.nan], dim2)
            e2dslli = np.zeros((range1+range2, dim2)) * np.nan
            cpti = np.nan
        # else extract
        else:
            # get the coefficients for this order
            opos = pos[order_num]
            # extract
            e2dsi, e2dslli, cpti = extraction(image, orderp, opos, range1,
                                              range2, sigdet, gain, cosmic,
                                              cosmic_sigcut, cosmic_thres)

            # TODO: continue here
            snr = calculate_snr()

        # append to array
        e2ds[order_num] = e2dsi
        e2dsll.append(e2dslli)
        cpt[order_num] = cpti

    # store extraction properties in parameter dictionary
    props = ParamDict()

    props['E2DS'] = e2ds
    props['E2DSLL'] = e2dsll
    props['N_COSMIC'] = cpt
    props['START_ORDER'] = start_order
    props['END_ORDER'] = end_order
    props['RANGE1'] = range1
    props['RANGE2'] = range2
    props['SKIP_ORDERS'] = skip_orders
    props['GAIN'] = gain
    props['SIGDET'] = sigdet
    props['COSMIC'] = cosmic
    props['COSMIC_SIGCUT'] = cosmic_sigcut
    props['COSMIC_THRESHOLD'] = cosmic_thres


    return props


def extraction(simage, orderp, pos, r1, r2, sigdet, gain, cosmic,
               cosmic_sigcut=0.25, cosmic_thres=5):
    """
    Extract order using tilt and weight (sigdet and badpix) and cosmic
    correction

    Same as extract_tilt_weight but slow (does NOT assume that rounded
    separation between extraction edges is constant along order)

    :param simage: numpy array (2D), the debananafied image (straightened image)
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit

    :param r1: float, the distance away from center to extract out to (top)
               across the orders direction
    :param r2: float, the distance away from center to extract out to (bottom)
               across the orders direction
    :param orderp: numpy array (2D), the image with fit superposed (zero filled)
    :param gain: float, the gain of the image (for conversion from ADU/s to e-)
    :param sigdet: float, the sigdet to use in the weighting
                   weights = 1/(signal*gain + sigdet^2) with bad pixels
                   multiplied by a weight of 1e-9 and good pixels
                   multiplied by 1

    :param cosmic_sigcut: float, the sigma cut for cosmic rays
    :param cosmic_threshold: int, the number of allowed cosmic rays per corr

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, the number of cosmic rays found
    """
    dim1, dim2 = simage.shape
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    # jcs = np.polyval(pos[::-1], ics)
    jcs = np.repeat(np.polyval(pos[::-1], dim2 // 2), dim2)
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
    spelong = np.zeros((np.nanmax(j2s - j1s) + 1, dim2), dtype=float)
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
                if np.nansum(fx) > 0:
                    fx = fx / np.nansum(fx)
                else:
                    fx = np.ones(fx.shape, dtype=float)

                # weights are then modified by the gain and sigdet added
                #    in quadrature
                # TODO: URGENT: Must figure out what is going on here
                # TODO:         case 0, 1 and 2 lead to "bands" of
                # TODO:         flux (check the e2dsll files)
                case = 3
                if case == 0:
                    raw_weights = np.where(sx > 0, 1, 1e-9)
                    weights = raw_weights / ((sx * gain) + sigdet ** 2)
                elif case == 1:
                    # the weights should never be smaller than sigdet^2
                    sigdets = np.repeat([sigdet ** 2], len(sx))
                    noises = (sx * gain) + sigdet ** 2
                    # find the weight for each pixel in sx
                    raw_weights = np.max([noises, sigdets], axis=0)
                    # weights is the inverse
                    weights = 1.0 / raw_weights
                elif case == 2:
                    raw_weights = np.ones_like(sx)
                    weights = raw_weights / ((sx * gain) + sigdet ** 2)
                else:
                    weights = np.ones_like(sx)
                    weights[~np.isfinite(sx)] = np.nan

                # set the value of this pixel to the weighted sum
                spelong[:, ic] = (weights * sx * fx)
                spe[ic] = np.nansum(weights * sx * fx)
                # normalise spe
                spe[ic] = spe[ic] / np.nansum(weights * fx ** 2)
                spelong[:, ic] = spelong[:, ic] / np.nansum(weights * fx ** 2)

                # Cosmic rays correction
                if cosmic:
                    spe, cpt = cosmic_correction(sx, spe, fx, ic, weights, cpt,
                                                 cosmic_sigcut, cosmic_thres)
    # multiple spe by gain to convert to e-
    spe *= gain
    spelong *= gain

    return spe, spelong, cpt


def calculate_snr()


def cosmic_correction(sx, spe, fx, ic, weights, cpt, cosmic_sigcut,
                      cosmic_threshold):
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
    :param cosmic_threshold: int, the number of allowed cosmic rays per corr

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return cpt: int, the number of cosmic rays found
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
    cond1 = np.nanmax(crit) > np.nanmax((sigcut * spe[ic], 1000.))
    cond2 = nbloop < cosmic_threshold
    while cond1 and cond2:
        # define the cosmic ray mask (True where not cosmic ray)
        cosmask = ~(crit > np.nanmax(crit) - 0.1)
        # set the pixels where there is a cosmic ray to zero
        part1 = weights * cosmask * sx * fx
        part2 = weights * cosmask * fx ** 2
        spe[ic] = np.nansum(part1) / np.nansum(part2)
        # recalculate the critical parameter
        crit = (sx * cosmask - spe[ic] * fx * cosmask)
        # increase the number of found cosmic rays by 1
        cpt += 1
        # increase the loop counter
        nbloop += 1
        # recalculate conditions
        cond1 = np.nanmax(crit) > np.nanmax((sigcut * spe[ic], 1000.))
        cond2 = nbloop < cosmic_threshold

    # finally return spe and cpt
    return spe, cpt


# =============================================================================
# Define worker functions
# =============================================================================
def _valid_orders(params, start_order, end_order, skip_orders=None):
    func_name = __NAME__ + '._valid_orders()'
    # push start and end to ints
    try:
        start_order = int(start_order)
    except Exception as e:
        eargs = [start_order, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-016-00001', args=eargs))
    try:
        end_order = int(end_order)
    except Exception as e:
        eargs = [end_order, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-016-00002', args=eargs))
    # start order must be zero or greater
    if start_order < 0:
        eargs = [start_order, func_name]
        WLOG(params, 'error', TextEntry('00-016-00003', args=eargs))
    # check that start order is less than end order
    if start_order > end_order:
        eargs = [start_order, end_order, func_name]
        WLOG(params, 'error', TextEntry('00-016-00004', args=eargs))
    # deal with skip orders
    if skip_orders is None or skip_orders.upper() == 'NONE':
       skip_orders = []
    else:
        try:
            skip_orders = np.array(skip_orders).astype(float).astype(int)
        except Exception as e:
            eargs = [skip_orders, type(e), e, func_name]
            WLOG(params, 'error', TextEntry('00-016-00005', args=eargs))
    # define storage
    valid_orders = []
    # loop around orders
    for order_num in range(start_order, end_order + 1):
        if order_num in skip_orders:
            continue
        else:
            valid_orders.append(order_num)
    # return valid orders
    return valid_orders


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
