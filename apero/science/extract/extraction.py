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
import warnings

from apero import core
from apero.core import constants
from apero.core import math as mp
from apero import locale
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.science.calib import flat_blaze

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.extraction.py'
__INSTRUMENT__ = 'None'
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
def extraction_twod(params, simage, orderp, pos, nframes, props, kind=None,
                    inflat=None, inblaze=None, fiber=None, **kwargs):
    func_name = __NAME__ + '.extraction_twod()'
    # ----------------------------------------------------------------------
    # get number of orders from params/kwargs
    start_order = pcheck(params, 'EXT_START_ORDER', 'start', kwargs, func_name)
    end_order = pcheck(params, 'EXT_END_ORDER', 'end', kwargs, func_name)
    range1 = pcheck(params, 'EXT_RANGE1', 'range1', kwargs, func_name,
                    mapf='dict', dtype=float)
    range2 = pcheck(params, 'EXT_RANGE2', 'range2', kwargs, func_name,
                    mapf='dict', dtype=float)
    skip_orders = pcheck(params, 'EXT_SKIP_ORDERS', 'skip', kwargs, func_name,
                         mapf='list', dtype=int)
    sigdet = pcheck(props, 'SIGDET', 'sigdet', kwargs, func_name)
    gain = pcheck(props, 'GAIN', 'gain', kwargs, func_name)
    cosmic = pcheck(params, 'EXT_COSMIC_CORRETION', 'cosmic', kwargs, func_name)
    cosmic_sigcut = pcheck(params, 'EXT_COSMIC_SIGCUT', 'cosmic_sigcuit',
                           kwargs, func_name)
    cosmic_thres = pcheck(params, 'EXT_COSMIC_THRESHOLD', 'cosmic_thres',
                          kwargs, func_name)
    # TODO: is blaze_size needed with sinc function?
    blaze_size = pcheck(params, 'FF_BLAZE_HALF_WINDOW', 'blaze_size',
                        kwargs, func_name)
    # TODO: is blaze_cut needed with sinc function?
    blaze_cut = pcheck(params, 'FF_BLAZE_THRESHOLD', 'blaze_cut', kwargs,
                       func_name)
    # TODO: is blaze_deg needed with sinc function?
    blaze_deg = pcheck(params, 'FF_BLAZE_DEGREE', 'blaze_deg', kwargs,
                       func_name)
    blaze_scut = pcheck(params, 'FF_BLAZE_SCUT', 'blaze_scut', kwargs,
                        func_name)
    blaze_sigfit = pcheck(params, 'FF_BLAZE_SIGFIT', 'blaze_sigfit', kwargs,
                          func_name)
    blaze_bpercentile = pcheck(params, 'FF_BLAZE_BPERCENTILE',
                               'blaze_bpercentile', kwargs, func_name)
    blaze_niter = pcheck(params, 'FF_BLAZE_NITER', 'blaze_niter', kwargs,
                         func_name)

    qc_ext_flux_max = pcheck(params, 'QC_EXT_FLUX_MAX', 'qc_ext_flux_max',
                             kwargs, func_name)
    # ----------------------------------------------------------------------
    # deal with ranges
    range1 = _get_range(params, range1, fiber, keys=['EXT_RANGE1', 'range1'])
    range2 = _get_range(params, range2, fiber, keys=['EXT_RANGE2', 'range2'])
    # ----------------------------------------------------------------------
    # calculate saturation level
    sat_level = qc_ext_flux_max * nframes
    # ----------------------------------------------------------------------
    # if we are dealing with a flat extraction we don't want to correct for
    #    cosmics
    if kind == 'flat':
        cosmic = False
    # ----------------------------------------------------------------------
    # get shame of image and number of orders
    dim1, dim2 = simage.shape
    nbo = pos.shape[0]
    # check that orderp is same dimensions as image
    if simage.shape != orderp.shape:
        eargs = [simage.shape, orderp.shape]
        WLOG(params, 'error', TextEntry('00-016-00006', args=eargs))
    # ----------------------------------------------------------------------
    # deal with start order being None
    if start_order is None:
        start_order = 0
    if end_order is None:
        end_order = nbo - 1
    # construct valid order (only skip if flat)
    valid_orders = _valid_orders(params, start_order, end_order, skip_orders)
    # ----------------------------------------------------------------------
    # storage for all orders
    e2ds = np.zeros([nbo, dim2]) * np.nan
    e2dsll = []
    cpt = np.repeat([np.nan], nbo)
    snr = np.repeat([np.nan], nbo)
    flat = np.zeros([nbo, dim2]) * np.nan
    blaze = np.zeros([nbo, dim2]) * np.nan
    rms = np.repeat([np.nan], nbo)
    fluxval = np.repeat([np.nan], nbo)

    # loop around orders
    for order_num in range(nbo):
        # ------------------------------------------------------------------
        # skip this order fill in with NaNs
        if order_num not in valid_orders:
            # set all values to NaN
            e2dsi = np.repeat([np.nan], dim2)
            e2dslli = np.zeros((int(range1+range2), dim2)) * np.nan
            cpti = np.nan
            snri = np.nan
            fluxi = np.repeat([np.nan], dim2)
            flati = np.repeat([np.nan], dim2)
            blazei = np.repeat([np.nan], dim2)
            rmsi = np.nan
            # --------------------------------------------------------------
            # log that we skipped this order
            wargs = [order_num]
            WLOG(params, 'warning', TextEntry('10-016-00001', args=wargs))
        # ------------------------------------------------------------------
        # else extract order by order
        else:
            # get the coefficients for this order
            opos = pos[order_num]
            # extract 1D for this order
            e2dsi, e2dslli, cpti = extraction(simage, orderp, opos, range1,
                                              range2, sigdet, gain, cosmic,
                                              cosmic_sigcut, cosmic_thres)
            # --------------------------------------------------------------
            # calculate the signal to noise ratio
            snri, fluxi = calculate_snr(e2dsi, blaze_size, range1, range2,
                                        sigdet)
            # --------------------------------------------------------------
            # if kind is flat remove low blaze edges, calculate blaze and flat
            if kind == 'flat':
                # fargs = [e2dsi, fluxi, blaze_cut, blaze_deg]
                # fout = flat_blaze.calculate_blaze_flat(*fargs)
                fargs = [e2dsi, blaze_scut, blaze_sigfit, blaze_bpercentile,
                         order_num, fiber, blaze_niter]
                fout = flat_blaze.calculate_blaze_flat_sinc(params, *fargs)
                e2dsi, flati, blazei, rmsi = fout
                # log process (for fiber # and order # S/N = , FF rms = )
                wargs = [fiber, order_num, snri, rmsi]
                WLOG(params, '', TextEntry('40-015-00001', args=wargs))
            # --------------------------------------------------------------
            # else just set to NaNs and log SNR/cosmics
            else:
                # get flat/blaze/rms to NaN
                flati = np.repeat([np.nan], dim2)
                blazei = np.repeat([np.nan], dim2)
                rmsi = np.nan
                # log process (for fiber # and order # S/N = , cosmics = )
                if cosmic:
                    wargs = [fiber, order_num, snri, cpti]
                    WLOG(params, '', TextEntry('40-016-00001', args=wargs))
                else:
                    wargs = [fiber, order_num, snri]
                    WLOG(params, '', TextEntry('40-016-00002', args=wargs))
        # ------------------------------------------------------------------
        # Check saturation limit
        # ------------------------------------------------------------------
        # get flux level
        fluxval_i = (fluxi / gain) / (range1 + range2)
        # if larger than limit warn the user
        if fluxval_i > sat_level:
            # log message (SATURATION LEVEL REACHED)
            wargs = [fiber, order_num, fluxval_i, sat_level]
            WLOG(params, 'warning', TextEntry('10-016-00002', args=wargs))
        # ------------------------------------------------------------------
        # append to arrays
        e2ds[order_num] = e2dsi
        e2dsll.append(e2dslli)
        cpt[order_num] = cpti
        snr[order_num] = snri
        flat[order_num] = flati
        blaze[order_num] = blazei
        rms[order_num] = rmsi
        fluxval[order_num] = fluxval_i
    # ----------------------------------------------------------------------
    # store extraction properties in parameter dictionary
    props = ParamDict()
    props['E2DS'] = e2ds
    props['E2DSLL'] = np.vstack(e2dsll)
    props['SNR'] = snr
    props['N_COSMIC'] = cpt
    props['RMS'] = rms
    props['FLUX_VAL'] = fluxval
    # deal with adding the flat and making e2dsff
    if inflat is None:
        props['FLAT'] = flat
        props['E2DSFF'] = np.zeros([nbo, dim2]) * np.nan
    else:
        props['FLAT'] = inflat
        props['E2DSFF'] = e2ds / inflat
    # deal with adding the blaze
    if inblaze is None:
        props['BLAZE'] = blaze
    else:
        props['BLAZE'] = inblaze
    # add setup properties
    props['FIBER'] = fiber
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
    props['BLAZE_SIZE'] = blaze_size
    props['BLAZE_CUT'] = blaze_cut
    props['BLAZE_DEG'] = blaze_deg
    props['SAT_QC'] = qc_ext_flux_max
    props['SAT_LEVEL'] = sat_level
    props['BLAZE_SCUT'] = blaze_scut
    props['BLAZE_SIGFIT'] = blaze_sigfit
    props['BLAZE_BPERCENTILE'] = blaze_bpercentile
    props['BLAZE_NITER'] = blaze_niter

    # add source
    keys = ['E2DS', 'E2DSFF', 'E2DSLL', 'SNR', 'N_COSMIC', 'RMS',
            'FLAT', 'BLAZE', 'FLUX_VAL', 'FIBER',
            'START_ORDER', 'END_ORDER', 'RANGE1', 'RANGE2', 'SKIP_ORDERS',
            'GAIN', 'SIGDET', 'COSMIC', 'COSMIC_SIGCUT', 'COSMIC_THRESHOLD',
            'BLAZE_SIZE', 'BLAZE_CUT', 'BLAZE_DEG', 'SAT_QC', 'SAT_LEVEL',
            'BLAZE_SCUT', 'BLAZE_SIGFIT', 'BLAZE_BPERCENTILE', 'BLAZE_NITER']
    props.set_sources(keys, func_name)
    # return property parameter dictionary
    return props


def extraction(simage, orderp, pos, r1, r2, sigdet, gain, cosmic=True,
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

    :param cosmic: bool, if True do cosmic correct else do not
    :param cosmic_sigcut: float, the sigma cut for cosmic rays
    :param cosmic_thres: int, the number of allowed cosmic rays per corr

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
    spelong = np.zeros((mp.nanmax(j2s - j1s) + 1, dim2), dtype=float)
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
                if mp.nansum(fx) > 0:
                    fx = fx / mp.nansum(fx)
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
                    raw_weights = mp.nanmax([noises, sigdets], axis=0)
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
                spe[ic] = mp.nansum(weights * sx * fx)
                # normalise spe
                spe[ic] = spe[ic] / mp.nansum(weights * fx ** 2)
                spelong[:, ic] = spelong[:, ic] / mp.nansum(weights * fx ** 2)

                # Cosmic rays correction
                if cosmic:
                    spe, cpt = cosmic_correction(sx, spe, fx, ic, weights, cpt,
                                                 cosmic_sigcut, cosmic_thres)
    # multiple spe by gain to convert to e-
    spe *= gain
    spelong *= gain

    return spe, spelong, cpt


def calculate_snr(e2ds, blaze_width, r1, r2, sigdet):
    # get the central pixel position
    cent_pos = int(len(e2ds) / 2)
    # get the blaze window size
    blaze_lower = cent_pos - blaze_width
    blaze_upper = cent_pos + blaze_width
    # get the average flux in the blaze window
    flux = mp.nansum(e2ds[blaze_lower:blaze_upper] / (2 * blaze_width))
    # calculate the noise
    noise = sigdet * np.sqrt(r1 + r2)
    # calculate the snr ratio = flux / sqrt(flux + noise**2)
    snr = flux / np.sqrt(flux + noise ** 2)
    # return snr
    return snr, flux


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
    cond1 = mp.nanmax(crit) > mp.nanmax((sigcut * spe[ic], 1000.))
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
        cond1 = mp.nanmax(crit) > mp.nanmax((sigcut * spe[ic], 1000.))
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
    if not isinstance(skip_orders, list):
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
        if (order_num in skip_orders):
            continue
        else:
            valid_orders.append(order_num)
    # return valid orders
    return valid_orders


def _get_range(params, rangedict, fiber, keys):
    func_name = __NAME__ + '._get_range()'

    if not isinstance(rangedict, dict):
        eargs = [keys[0], keys[1], func_name]
        WLOG(params, 'error', TextEntry('00-016-00007', arg=eargs))
    # deal with fiber not being in range dictionary
    if fiber not in rangedict:
        # log that range1 had invalid fiber type
        eargs = [fiber, rangedict, keys[0], keys[1], func_name]
        WLOG(params, 'error', TextEntry('00-016-00008', args=eargs))
    else:
        try:
            # return range value
            return float(rangedict[fiber])
        except ValueError as _:
            eargs = [fiber, rangedict, keys[0], keys[1], func_name]
            WLOG(params, 'error', TextEntry('00-016-00009', args=eargs))
        except Exception as e:
            eargs = [fiber, rangedict, type(e), e, keys[0], keys[1], func_name]
            WLOG(params, 'error', TextEntry('00-016-00010', args=eargs))


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
