#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-07 at 13:46

@author: cook



Version 0.0.0
"""

import numpy as np

from SpirouDRS import spirouCore
from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouEXTOR.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# User functions
# =============================================================================
def extract_AB_order(pp, loc, image, rnum):
    """
    Perform the extraction on the AB fibers separately using the summation
    over constant range

    :param image: numpy array (2D), the image
    :param pp: dictionary, parameter dictionary
    :param loc: dictionary, parameter dictionary containing the data
    :param image:
    :param rnum: int, the order number for this iteration

    :return loc: dictionary, parameter dictionary containing the data
    """
    # get the width fit coefficients for this fit
    assi = loc['ass'][rnum]
    # --------------------------------------------------------------------
    # Center the central pixel (using the width fit)
    # get the width of the central pixel of this order
    width_cent = np.polyval(assi[::-1], pp['IC_CENT_COL'])
    # work out the offset in width for the center pixel
    loc['offset'] = width_cent * pp['IC_FACDEC']
    loc.set_source('offset', __NAME__ + '/extract_AB_order()')
    # --------------------------------------------------------------------
    # deal with fiber A:

    # Get the center coeffs for this order
    acci = np.array(loc['acc'][rnum])
    # move the intercept of the center fit by -offset
    acci[0] -= loc['offset']
    # extract the data
    eargs = [image, acci, assi,]
    ekwargs = dict(extopt=pp['IC_EXTOPT'], 
                   gain=pp['gain'],                 
                   range1=pp['IC_EXTNBSIG'],
                   range2=pp['IC_EXTNBSIG'])
    loc['cent1'], cpt = extract_wrapper(*eargs, **ekwargs)
    loc.set_source('cent1', __NAME__ + '/extract_AB_order()')
    loc['nbcos'][rnum] = cpt
    # --------------------------------------------------------------------
    # deal with fiber B:

    # Get the center coeffs for this order
    acci = np.array(loc['acc'][rnum])
    # move the intercept of the center fit by -offset
    acci[0] += loc['offset']
    # extract the data
    eargs = [image, acci, assi,]
    ekwargs = dict(extopt=pp['IC_EXTOPT'], 
                   gain=pp['gain'],                 
                   range1=pp['IC_EXTNBSIG'],
                   range2=pp['IC_EXTNBSIG'])
    loc['cent2'], cpt = extract_wrapper(*eargs, **ekwargs)
    loc.set_source('cent2', __NAME__ + '/extract_AB_order()')
    loc['nbcos'][rnum] = cpt

    # return loc dictionary
    return loc


def extract_order(pp, loc, image, rnum, **kwargs):
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['acc'][rnum], loc['ass'][rnum]]
    ekwargs = dict(use_tilt=False, 
                   use_weight=False,
                   extopt=pp['IC_EXTOPT'],
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   gain=kwargs.get('gain', pp['gain']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_tilt_order(pp, loc, image, rnum, **kwargs):
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['acc'][rnum], loc['ass'][rnum]]
    ekwargs = dict(use_tilt=True, 
                   use_weight=False,
                   tilt=loc['tilt'][rnum],
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   gain=kwargs.get('gain', pp['gain']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_tilt_weight_order(pp, loc, image, orderp, rnum, **kwargs):
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['acc'][rnum], loc['ass'][rnum]]
    ekwargs = dict(use_tilt=True, 
                   use_weight=True,
                   tilt=loc['tilt'][rnum], 
                   order_profile=orderp,
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   mode=1,
                   gain=kwargs.get('gain', pp['gain']),
                   sigdet=kwargs.get('sigdet', pp['sigdet']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_tilt_weight_order2(pp, loc, image, orderp, rnum, **kwargs):
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['acc'][rnum], loc['ass'][rnum]]
    ekwargs = dict(use_tilt=True,
                   use_weight=True,
                   tilt=loc['tilt'][rnum], 
                   order_profile=orderp,
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE1']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE2']),
                   mode=2,
                   gain=kwargs.get('gain', pp['gain']),
                   sigdet=kwargs.get('sigdet', pp['sigdet']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_weight_order(pp, loc, image, orderp, rnum, **kwargs):
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['acc'][rnum], loc['ass'][rnum]]
    ekwargs = dict(use_tilt=False,
                   use_weight=True,
                   tilt=None, 
                   order_profile=orderp,
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   gain=kwargs.get('gain', pp['gain']),
                   sigdet=kwargs.get('sigdet', pp['sigdet']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


# =============================================================================
# Worker functions
# =============================================================================
def extract_wrapper(image, pos, sig, **kwargs):
    """

    :param p: dictionary, parameter dictionary, containing constants and
              variables (at least 'ic_extopt', 'ic_extnbsig' and 'gain')

              where 'ic_extopt' gives the extraction option
                    'ic_extnbsig' gives the distance away from center to
                       extract out to +/-
                    'gain' is the image gain (used to convert from ADU/s to e-)
    :param image: numpy array (2D), the image
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param sig: numpy array (1D), the width fit coefficients
                size = number of coefficients for fit
    :param kwargs: additional keyword arguments

    currently accepted keyword arguments are:

        extopt:         int, Extraction option in tilt file:
                         if 0 extraction by summation over constant range
                         if 1 extraction by summation over constant sigma
                            (not currently available)
                         if 2 Horne extraction without cosmic elimination
                            (not currently available)
                         if 3 Horne extraction with cosmic elimination
                            (not currently available)

        nbsig:          float,  distance away from center to extract out to +/-
                        defaults to p['nbsig'] from constants_SPIROU.txt

        gain:           float, gain of the image
                        defaults to p['gain'] from fitsfilename HEADER

        sigdet:         float, the sigdet of the image
                        defaults to p['sigdet'] from fitsfilename HEADER

        range1:         float, Half-zone extraction width left side
                        (formally plage1)
                        defaults to p['ic_ext_range1'] from fiber parameters in
                        constatns_SPIROU.txt

        range2:         float, Half-zone extraction width left side
                        (formally plage2)
                        defaults to p['ic_ext_range2'] from fiber parameters in
                        constatns_SPIROU.txt

        tilt:           numpy array (1D), the tilt for this order, if defined
                        uses tilt, if not defined does not

        use_weight:    bool, if True use weighted extraction, if False or not
                        defined does not use weighted extraction

        order_profile:  numpy array (2D), the image with fit superposed on top,
                        required for tilt and or weighted fit

        mode:           if use_weight and tilt is not None then
                        if mode = 'old'  will use old code (use this if
                        exception generated)
                        extract_tilt_weight_order_old() is run

                        else mode = 'new' and
                        extract_tilt_weight_order() is run

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    # get parameters from keywordargs but default to None
    extopt = kwargs.get('extopt', None)
    gain = kwargs.get('gain', None)
    sigdet = kwargs.get('sigdet', None)
    range1 = kwargs.get('range1', None)
    range2 = kwargs.get('range2', None)
    mode = kwargs.get('mode', None)
    tilt = kwargs.get('tilt', None)
    order_profile = kwargs.get('order_profile', None)
    # get parameters from keyword arguments but default to False
    use_tilt = kwargs.get('use_tilt', False)
    use_weight = kwargs.get('use_weight', False)
    # ----------------------------------------------------------------------
    # Extract  no tilt no weight extopt = 0
    # ----------------------------------------------------------------------
    # Option 0: Extraction by summation over constant range
    if extopt == 0:
        # check required values are not None
        check_for_none(range1, 'range1')
        check_for_none(gain, 'gain')
        # run extract and return
        return extract_const_range(image=image, pos=pos, nbsig=range1,
                                   gain=gain)
    # ----------------------------------------------------------------------
    # Extract tilt + weight
    # ----------------------------------------------------------------------
    # Extra: if tilt defined and order_profile defined and use_weight = True
    #        Extract using a weighted tilt
    elif use_tilt and use_weight and mode in [0, 1, 2, 3]:
        # check required values are not None
        check_for_none(range1, 'range1')
        check_for_none(range2, 'range2')
        check_for_none(tilt, 'tilt')
        check_for_none(order_profile, 'order_profile')
        check_for_none(gain, 'gain')
        check_for_none(sigdet, 'sig_det')
        # run extract and return
        ekwargs = dict(image=image, pos=pos, tilt=tilt, r1=range1, r2=range2,
                       orderp=order_profile, gain=gain, sigdet=sigdet)
        if mode == 0:
            return extract_tilt_weight(**ekwargs)
            # return extract(**ekwargs)
        if mode == 1:
            return extract_tilt_weight(**ekwargs)
            # return extract(**ekwargs)
        if mode == 2:
            return extract_tilt_weight2(**ekwargs)
        if mode == 3:
            return extract_tilt_weight_old2(**ekwargs)

    # ----------------------------------------------------------------------
    # Extract tilt  + no weight
    # ----------------------------------------------------------------------
    # Extra: if tilt defined but use_weight = False
    elif use_tilt and not use_weight:
        # check required values are not None
        check_for_none(range1, 'range1')
        check_for_none(range2, 'range2')
        check_for_none(tilt, 'tilt')
        check_for_none(gain, 'gain')
        # run extract and return
        ekwargs = dict(image=image, pos=pos, tilt=tilt, r1=range1, r2=range2,
                       gain=gain)
        return extract_tilt(**ekwargs)
        # return extract(**ekwargs)
    # ----------------------------------------------------------------------
    # Extract weight + no tilt
    # ----------------------------------------------------------------------
    elif not use_tilt and use_weight:
        # check required values are not None
        check_for_none(range1, 'range1')
        check_for_none(range2, 'range2')
        check_for_none(order_profile, 'order_profile')
        check_for_none(gain, 'gain')
        # run extract and return
        ekwargs = dict(image=image, pos=pos, r1=range1, r2=range2,
                       orderp=order_profile, gain=gain)
        return extract_weight(**ekwargs)
        # return extract(**ekwargs)
    # ----------------------------------------------------------------------
    # Extract no weight + no tilt
    # ----------------------------------------------------------------------
    elif not use_tilt and not use_weight:
        # check required values are not None
        check_for_none(range1, 'range1')
        check_for_none(range2, 'range2')
        check_for_none(order_profile, 'order_profile')
        check_for_none(gain, 'gain')
        check_for_none(sigdet, 'sig_det')
        # run extract and return
        WLOG('error', '', 'Extraction type invalid')
        # ekwargs = dict(image=image, pos=pos, r1=range1, r2=range2, gain=gain)
        # return extract(**ekwargs)
    # ----------------------------------------------------------------------
    # No Extract
    # ----------------------------------------------------------------------
    else:
        WLOG('error', '', 'Extraction type invalid')


def extract_const_range(image, pos, nbsig, gain):
    """
    Extracts this order using position only

    python = 12 ms  fortran = 13 ms

    :param image: numpy array (2D), the image
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param nbsig: float, the distance away from center to extract out to +/-
    :param gain: float, the gain of the image (for conversion from ADU/s to e-)

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    # print('extract_const_range')
    dim1, dim2 = image.shape
    nbcos = 0
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - nbsig
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + nbsig
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # add the main order pixels
            spe[ic] = np.sum(image[j1s[ic] + 1: j2s[ic], ic])
            # add the bits missing due to rounding
            spe[ic] += lower[ic] * image[j1s[ic], ic]
            spe[ic] += upper[ic] * image[j2s[ic], ic]
    # convert to e-
    spe *= gain

    return spe[::-1], nbcos


def extract_tilt(image, pos, tilt, r1, r2, gain):
    """
    Extract order using tilt

    :param image: numpy array (2D), the image
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param tilt: float, the tilt for this order
    :param r1: float, the distance away from center to extract out to (top)
               across the orders direction
    :param r2: float, the distance away from center to extract out to (bottom)
               across the orders direction
    :param gain: float, the gain of the image (for conversion from ADU/s to e-)

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    # print('extract_tilt')
    dim1, dim2 = image.shape
    nbcos = 0
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - r1
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + r2
    # get the pixels around the order
    i1s = ics - 2
    i2s = ics + 2
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # check that ww0 and ww1 are constant (They should be)
    if len(np.unique(ww0)) != 1:
        raise ValueError('Neil error: Assumption that ww0 is constant is wrong'
                         '(spirouEXTOR.py/extract_tilt_weight)')
    # ww0 and ww1 are constant
    ww0, ww1 = ww0[0], ww1[0]
    # create a box of the correct size
    ww = np.zeros((ww0, ww1))
    # calculate the tilt shift for each pixel in the box
    ff = tiltshift * (np.arange(ww0) - r1)
    # normalise tilt shift between -0.5 and 0.5
    rr = np.round(ff) - ff
    # Set the masks for tilt values of ff
    mask1 = (ff >= -2.0) & (ff < -1.5)
    mask2 = (ff >= -1.5) & (ff < -1.0)
    mask3 = (ff >= -1.0) & (ff < -0.5)
    mask4 = (ff >= -0.5) & (ff < 0.0)
    mask5 = (ff >= 0.0) & (ff < 0.5)
    mask6 = (ff >= 0.5) & (ff < 1.0)
    mask7 = (ff >= 1.0) & (ff < 1.5)
    mask8 = (ff >= 1.5) & (ff < 2.0)
    # get rra, rrb and rrc
    rra, rrb, rrc = -rr, 1 - rr, 1 + rr
    # modify the shift values in the box dependent on the mask
    ww[:, 0] = np.where(mask1, rrc, 0) + np.where(mask2, rr, 0)
    ww[:, 1] = np.where(mask1, rra, 0) + np.where(mask2, rrb, 0)
    ww[:, 1] += np.where(mask3, rrc, 0) + np.where(mask4, rr, 0)
    ww[:, 2] = np.where(mask3, rra, 0) + np.where(mask4, rrb, 0)
    ww[:, 2] += np.where(mask5, rrc, 0) + np.where(mask6, rr, 0)
    ww[:, 3] = np.where(mask5, rra, 0) + np.where(mask6, rrb, 0)
    ww[:, 3] += np.where(mask7, rrc, 0) + np.where(mask8, rr, 0)
    ww[:, 4] = np.where(mask7, rra, 0) + np.where(mask8, rrb, 0)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics[2:-2]:
        # multiple the image by the rotation matrix
        Sx = image[j1s[ic]+1:j2s[ic], i1s[ic]:i2s[ic] + 1] * ww[1:-1]
        spe[ic] = np.sum(Sx)
        # add the main order pixels
        # add the bits missing due to rounding
        Sxl = image[j1s[ic], i1s[ic]:i2s[ic] + 1] * ww[0]
        spe[ic] += lower[ic] * np.sum(Sxl)
        Sxu = image[j2s[ic], i1s[ic]:i2s[ic] + 1] * ww[-1]
        spe[ic] += upper[ic] * np.sum(Sxu)
    # convert to e-
    spe *= gain
    # return spe and nbcos
    return spe, nbcos


def extract_weight(image, pos, r1, r2, orderp, gain):
    """
    Extract order using weight (badpix)

    :param image: numpy array (2D), the image
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

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    # print('extract_weight')
    dim1, dim2 = image.shape
    nbcos = 0
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - r1
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + r2
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # Get the extraction of the main profile
            Sx = image[j1s[ic] + 1: j2s[ic], ic]
            Sx1 = image[j1s[ic]: j2s[ic] + 1, ic]
            # Get the extraction of the order_profile
            Fx = orderp[j1s[ic]:j2s[ic] + 1, ic]
            # Renormalise the order_profile
            Fx = Fx / np.sum(Fx)
            # get the weights
            # weight values less than 0 to 0.000001
            raw_weights = np.where(Sx1 > 0, 1, 0.000001)
            weights = Fx * raw_weights
            # get the normalisation (equal to the sum of the weights squared)
            norm = np.sum(weights**2)
            # add the main extraction to array
            spe[ic] =  np.sum(Sx * weights[1:-1])
            # add the bits missing due to rounding
            # Question: this differs from tilt+weight
            # Question:    this one adds only 1 contribution on to value of spe
            spe[ic] += lower[ic] * image[j1s[ic], ic] * weights[0]
            spe[ic] += upper[ic] * image[j2s[ic], ic] * weights[-1]
            # divide by the normalisation
            spe[ic] /= norm
    # convert to e-
    spe *= gain
    # return spe and nbcos
    return spe, nbcos


def extract_tilt_weight2(image, pos, tilt, r1, r2, orderp, gain, sigdet):
    """
    Extract order using tilt and weight (sigdet and badpix)

    Same as extract_tilt_weight but slow (does NOT assume that rounded
    separation between extraction edges is constant along order)


    :param image: numpy array (2D), the image
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param tilt: float, the tilt for this order

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

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    dim1, dim2 = image.shape
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - r1
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + r2
    # get the pixels around the order
    i1s = ics - 2
    i2s = ics + 2
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # check that ww0 and ww1 are constant (They should be)
    if len(np.unique(ww0)) != 1:
        raise ValueError('Neil error: Assumption that ww0 is constant is wrong'
                         '(spirouEXTOR.py/extract_tilt_weight)')
    # ww0 and ww1 are constant
    ww0, ww1 = ww0[0], ww1[0]
    # create a box of the correct size
    ww = np.zeros((ww0, ww1))
    # calculate the tilt shift for each pixel in the box
    ff = tiltshift * (np.arange(ww0) - r1)
    # normalise tilt shift between -0.5 and 0.5
    rr = np.round(ff) - ff
    # Set the masks for tilt values of ff
    mask1 = (ff >= -2.0) & (ff < -1.5)
    mask2 = (ff >= -1.5) & (ff < -1.0)
    mask3 = (ff >= -1.0) & (ff < -0.5)
    mask4 = (ff >= -0.5) & (ff < 0.0)
    mask5 = (ff >= 0.0) & (ff < 0.5)
    mask6 = (ff >= 0.5) & (ff < 1.0)
    mask7 = (ff >= 1.0) & (ff < 1.5)
    mask8 = (ff >= 1.5) & (ff < 2.0)
    # get rra, rrb and rrc
    rra, rrb, rrc = -rr, 1 - rr, 1 + rr
    # modify the shift values in the box dependent on the mask
    ww[:, 0] = np.where(mask1, rrc, 0) + np.where(mask2, rr, 0)
    ww[:, 1] = np.where(mask1, rra, 0) + np.where(mask2, rrb, 0)
    ww[:, 1] += np.where(mask3, rrc, 0) + np.where(mask4, rr, 0)
    ww[:, 2] = np.where(mask3, rra, 0) + np.where(mask4, rrb, 0)
    ww[:, 2] += np.where(mask5, rrc, 0) + np.where(mask6, rr, 0)
    ww[:, 3] = np.where(mask5, rra, 0) + np.where(mask6, rrb, 0)
    ww[:, 3] += np.where(mask7, rrc, 0) + np.where(mask8, rr, 0)
    ww[:, 4] = np.where(mask7, rra, 0) + np.where(mask8, rrb, 0)

    # loop around each pixel along the order
    for ic in ics[2:-2]:
        # multiple the image by the rotation matrix
        Sx = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
        # multiple the order_profile by the rotation matrix
        Fx = orderp[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
        # Renormalise the rotated order profile
        Fx = Fx / np.sum(Fx)
        # weight values less than 0 to 1e-9
        raw_weights = np.where(Sx > 0, 1, 1e-9)
        # weights are then modified by the gain and sigdet added in quadrature
        weights = raw_weights / ((Sx * gain) + sigdet**2)
        # set the value of this pixel to the weighted sum
        spe[ic] = np.sum(weights * Sx * Fx)/np.sum(weights * Fx**2)
    # multiple spe by gain to convert to e-
    spe *= gain

    return spe, 0


def extract_tilt_weight_old2(image, pos, tilt, r1, r2, orderp,
                             gain, sigdet):
    """
    Extract order using tilt and weight (sigdet and badpix)

    Same as extract_tilt_weight but slow (does NOT assume that rounded
    separation between extraction edges is constant along order)


    :param image: numpy array (2D), the image
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param tilt: float, the tilt for this order

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

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """

    dim1, dim2 = image.shape
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - r1
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + r2
    # get the pixels around the order
    i1s = ics - 2
    i2s = ics + 2
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # loop around each pixel along the order
    for ic in ics[2:-2]:
        # create a box of the correct size
        ww = np.zeros((ww0[ic], ww1[ic]))
        # calculate the tilt shift for each pixel in the box
        ff = tiltshift * (np.arange(ww0[ic]) - r1)
        # normalise tilt shift between -0.5 and 0.5
        rr = np.round(ff) - ff
        # Set the masks for tilt values of ff
        mask1 = (ff >= -2.0) & (ff < -1.5)
        mask2 = (ff >= -1.5) & (ff < -1.0)
        mask3 = (ff >= -1.0) & (ff < -0.5)
        mask4 = (ff >= -0.5) & (ff < 0.0)
        mask5 = (ff >= 0.0) & (ff < 0.5)
        mask6 = (ff >= 0.5) & (ff < 1.0)
        mask7 = (ff >= 1.0) & (ff < 1.5)
        mask8 = (ff >= 1.5) & (ff < 2.0)
        # get rra, rrb and rrc
        rra, rrb, rrc = -rr, 1 - rr, 1 + rr
        # modify the shift values in the box dependent on the mask
        ww[:, 0] = np.where(mask1, rrc, 0) + np.where(mask2, rr, 0)
        ww[:, 1] = np.where(mask1, rra, 0) + np.where(mask2, rrb, 0)
        ww[:, 1] += np.where(mask3, rrc, 0) + np.where(mask4, rr, 0)
        ww[:, 2] = np.where(mask3, rra, 0) + np.where(mask4, rrb, 0)
        ww[:, 2] += np.where(mask5, rrc, 0) + np.where(mask6, rr, 0)
        ww[:, 3] = np.where(mask5, rra, 0) + np.where(mask6, rrb, 0)
        ww[:, 3] += np.where(mask7, rrc, 0) + np.where(mask8, rr, 0)
        ww[:, 4] = np.where(mask7, rra, 0) + np.where(mask8, rrb, 0)
        # multiple the image by the rotation matrix
        Sx = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
        # multiple the order_profile by the rotation matrix
        Fx = orderp[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
        # Renormalise the rotated order profile
        Fx = Fx / np.sum(Fx)
        # weight values less than 0 to 1e-9
        raw_weights = np.where(Sx > 0, 1, 1e-9)
        # weights are then modified by the gain and sigdet added in quadrature
        weights = raw_weights / ((Sx * gain) + sigdet**2)
        # set the value of this pixel to the weighted sum
        spe[ic] = np.sum(weights * Sx * Fx)/np.sum(weights * Fx**2)
    # multiple spe by gain to convert to e-
    spe *= gain

    return spe, 0


def extract_tilt_weight(image, pos, tilt, r1, r2, orderp, gain, sigdet):
    """
    Extract order using tilt and weight (sigdet and badpix)

    Same as extract_tilt_weight but slow (does NOT assume that rounded
    separation between extraction edges is constant along order)


    :param image: numpy array (2D), the image
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param tilt: float, the tilt for this order

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

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    # print('extract_tilt_weight')
    dim1, dim2 = image.shape
    nbcos = 0
    # create storage for extration
    spe = np.zeros(dim2, dtype=float)
    # create array of pixel values
    ics = np.arange(dim2)
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - r1
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + r2
    # get the pixels around the order
    i1s = ics - 2
    i2s = ics + 2
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # check that ww0 and ww1 are constant (They should be)
    if len(np.unique(ww0)) != 1:
        raise ValueError('Neil error: Assumption that ww0 is constant is wrong'
                         '(spirouEXTOR.py/extract_tilt_weight)')
    # ww0 and ww1 are constant
    ww0, ww1 = ww0[0], ww1[0]
    # create a box of the correct size
    ww = np.zeros((ww0, ww1))
    # calculate the tilt shift for each pixel in the box
    ff = tiltshift * (np.arange(ww0) - r1)
    # normalise tilt shift between -0.5 and 0.5
    rr = np.round(ff) - ff
    # Set the masks for tilt values of ff
    mask1 = (ff >= -2.0) & (ff < -1.5)
    mask2 = (ff >= -1.5) & (ff < -1.0)
    mask3 = (ff >= -1.0) & (ff < -0.5)
    mask4 = (ff >= -0.5) & (ff < 0.0)
    mask5 = (ff >= 0.0) & (ff < 0.5)
    mask6 = (ff >= 0.5) & (ff < 1.0)
    mask7 = (ff >= 1.0) & (ff < 1.5)
    mask8 = (ff >= 1.5) & (ff < 2.0)
    # get rra, rrb and rrc
    rra, rrb, rrc = -rr, 1 - rr, 1 + rr
    # modify the shift values in the box dependent on the mask
    ww[:, 0] = np.where(mask1, rrc, 0) + np.where(mask2, rr, 0)
    ww[:, 1] = np.where(mask1, rra, 0) + np.where(mask2, rrb, 0)
    ww[:, 1] += np.where(mask3, rrc, 0) + np.where(mask4, rr, 0)
    ww[:, 2] = np.where(mask3, rra, 0) + np.where(mask4, rrb, 0)
    ww[:, 2] += np.where(mask5, rrc, 0) + np.where(mask6, rr, 0)
    ww[:, 3] = np.where(mask5, rra, 0) + np.where(mask6, rrb, 0)
    ww[:, 3] += np.where(mask7, rrc, 0) + np.where(mask8, rr, 0)
    ww[:, 4] = np.where(mask7, rra, 0) + np.where(mask8, rrb, 0)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics[2:-2]:
        # Get the extraction of the main profile
        Sx = image[j1s[ic] + 1: j2s[ic], i1s[ic]: i2s[ic]+1] * ww[1:-1]
        Sx1 = image[j1s[ic]: j2s[ic] + 1, i1s[ic]: i2s[ic]+1]
        # Get the extraction of the order_profile
        Fx = orderp[j1s[ic]: j2s[ic] + 1, i1s[ic]: i2s[ic]+1]
        # Renormalise the order_profile
        Fx = Fx/np.sum(Fx)
        # get the weights
        # weight values less than 0 to 0.000001
        raw_weights = np.where(Sx1 > 0, 1, 0.000001)
        weights = Fx * raw_weights
        # get the normalisation (equal to the sum of the weights squared)
        norm = np.sum(weights**2)
        # add the main extraction to array
        mainvalues = np.sum(Sx * weights[1:-1], 1)
        # add the bits missing due to rounding
        Sxl = image[j1s[ic], i1s[ic]:i2s[ic] + 1] * ww[0] * weights[0]
        lowervalue = lower[ic] * np.sum(Sxl)
        Sxu = image[j2s[ic], i1s[ic]:i2s[ic] + 1] * ww[-1] * weights[-1]
        uppervalue = upper[ic] * np.sum(Sxu)
        # add lower and upper constants to array and sum over all
        # Question: Is this correct or a typo?
        # Question: Is the intention to add contribution due to lower and upper
        # Question:    end to each of the main pixels, or just to the total?
        spe[ic] = np.sum(mainvalues + lowervalue + uppervalue)
        # divide by the normalisation
        spe[ic] /= norm
    # convert to e-
    spe *= gain
    # return spe and nbcos
    return spe, nbcos


# def extract(image, pos, tilt=None, r1=None, r2=None, orderp=None,
#             gain=None, sigdet=None):
#     """
#     Extract order using tilt and weight (sigdet and badpix)
#
#     Same as extract_tilt_weight but slow (does NOT assume that rounded
#     separation between extraction edges is constant along order)
#
#
#     :param image: numpy array (2D), the image
#     :param pos: numpy array (1D), the position fit coefficients
#                 size = number of coefficients for fit
#     :param tilt: float, the tilt for this order
#
#     :param r1: float, the distance away from center to extract out to (top)
#                across the orders direction
#     :param r2: float, the distance away from center to extract out to (bottom)
#                across the orders direction
#     :param orderp: numpy array (2D), the image with fit superposed
#                    (zero filled)
#     :param gain: float, the gain of the image (for conversion from
#                  ADU/s to e-)
#     :param sigdet: float, the sigdet to use in the weighting
#                    weights = 1/(signal*gain + sigdet^2) with bad pixels
#                    multiplied by a weight of 1e-9 and good pixels
#                    multiplied by 1
#
#     :return spe: numpy array (1D), the extracted pixel values,
#                  size = image.shape[1] (along the order direction)
#     :return nbcos: int, zero in this case
#     """
#     dim1, dim2 = image.shape
#     nbcos = 0
#     # create storage for extration
#     spe = np.zeros(dim2, dtype=float)
#     # create array of pixel values
#     ics = np.arange(dim2)
#     # get positions across the orders for each pixel value along the order
#     jcs = np.polyval(pos[::-1], ics)
#     # get the lower bound of the order for each pixel value along the order
#     lim1s = jcs - r1
#     # get the upper bound of the order for each pixel value along the order
#     lim2s = jcs + r2
#     # get the pixels around the order
#     i1s = ics - 2
#     i2s = ics + 2
#     # get the integer pixel position of the lower bounds
#     j1s = np.array(np.round(lim1s), dtype=int)
#     # get the integer pixel position of the upper bounds
#     j2s = np.array(np.round(lim2s), dtype=int)
#     # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
#     ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
#
#     # check that ww0 and ww1 are constant (They should be)
#     if len(np.unique(ww0)) != 1:
#         raise ValueError('Neil error: Assumption that ww0 is constant is
#                          'wrong (spirouEXTOR.py/extract_tilt_weight)')
#     # get tilt matrix (if we have tilt)
#     ww = get_tilt_matrix(ww0, ww1, r1, r2, tilt)
#     # account for the missing fractional pixels (due to integer rounding)
#     lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
#     # loop around each pixel along the order and, if it is within the image,
#     #   sum the values contained within the order (including the bits missing
#     #   due to rounding)
#     for ic in ics:
#         # Get the extraction of the main profile
#         Sx = image[j1s[ic] + 1: j2s[ic], ic]
#         # Get the extraction of the order_profile
#         # (if no weights then set to 1)
#         if orderp is None:
#             Fx = np.ones_like(Sx)
#         else:
#             Fx = orderp[j1s[ic]:j2s[ic] + 1, ic]
#             # Renormalise the order_profile
#             Fx = Fx / np.sum(Fx)
#         # add the main order pixels
#         spe[ic] = np.sum(Sx)
#         # get the weights
#         # weight values less than 0 to 0.000001
#         raw_weights = np.where(Sx > 0, 1, 0.000001)
#         weights = Fx * raw_weights
#         # get the normalisation (equal to the sum of the weights squared)
#         norm = np.sum(weights**2)
#         # add the main extraction to array
#         SSx = np.sum(Sx)
#         spe[ic] = SSx * weights[1:-1] * ww[1:-1]
#         # add the bits missing due to rounding
#         Sxl = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1]
#         Sxl *= ww[0] * weights[1:-1]
#         spe[ic] += lower[ic] * np.sum(Sxl)
#         Sxu = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1]
#         Sxu *= ww[-1] * weights[1:-1]
#         spe[ic] += upper[ic] * np.sum(Sxu)
#         # divide by the normalisation
#         spe[ic] /= norm
#     # convert to e-
#     spe *= gain
#     # return spe and nbcos
#     return spe, nbcos
#


# =============================================================================
# Other functions
# =============================================================================


def check_for_none(value, name):
    # func name
    fname = __NAME__ + '/extract_wrapper()'
    if value is None:
        emsg = 'Keyword "{0}" is not defined for {1}'
        WLOG('error', '', emsg.format(name, fname))


# def get_tilt_matrix(ww0, ww1, r1, r2, tilt=None):
#     # get tilt (or set to zero)
#     if tilt is None:
#         tiltshift = 0.0
#     else:
#         # calculate the tilt shift
#         tiltshift = np.tan(np.deg2rad(tilt))
#     # ww0 and ww1 are constant
#     ww0, ww1 = ww0[0], ww1[0]
#     # create a box of the correct size
#     ww = np.zeros((ww0, ww1))
#     # calculate the tilt shift for each pixel in the box
#     ff = tiltshift * (np.arange(ww0) - r1)
#     # normalise tilt shift between -0.5 and 0.5
#     rr = np.round(ff) - ff
#     # Set the masks for tilt values of ff
#     mask1 = (ff >= -2.0) & (ff < -1.5)
#     mask2 = (ff >= -1.5) & (ff < -1.0)
#     mask3 = (ff >= -1.0) & (ff < -0.5)
#     mask4 = (ff >= -0.5) & (ff < 0.0)
#     mask5 = (ff >= 0.0) & (ff < 0.5)
#     mask6 = (ff >= 0.5) & (ff < 1.0)
#     mask7 = (ff >= 1.0) & (ff < 1.5)
#     mask8 = (ff >= 1.5) & (ff < 2.0)
#     # get rra, rrb and rrc
#     rra, rrb, rrc = -rr, 1 - rr, 1 + rr
#     # modify the shift values in the box dependent on the mask
#     ww[:, 0] = np.where(mask1, rrc, 0) + np.where(mask2, rr, 0)
#     ww[:, 1] = np.where(mask1, rra, 0) + np.where(mask2, rrb, 0)
#     ww[:, 1] += np.where(mask3, rrc, 0) + np.where(mask4, rr, 0)
#     ww[:, 2] = np.where(mask3, rra, 0) + np.where(mask4, rrb, 0)
#     ww[:, 2] += np.where(mask5, rrc, 0) + np.where(mask6, rr, 0)
#     ww[:, 3] = np.where(mask5, rra, 0) + np.where(mask6, rrb, 0)
#     ww[:, 3] += np.where(mask7, rrc, 0) + np.where(mask8, rr, 0)
#     ww[:, 4] = np.where(mask7, rra, 0) + np.where(mask8, rrb, 0)
#     # return tilt matrix
#     return ww

# =============================================================================
# Test functions
# =============================================================================
def extract_const_range_fortran(flatimage, pos, sig, dim, nbsig, gain):
    """
    Raw copy of the fortran code "extract2.py" - no optimisation

    :param flatimage: 1D numpy array, the flattened image,
                        use image.ravel(order='F')
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param sig: numpy array (1D), the width fit coefficients
                size = number of coefficients for fit
    :param dim: int, size of array along the order, image.shape[1]
    :param nbsig: float, the distance away from center to extract out to +/-
    :param gain: float, the gain of the image (for conversion from ADU/s to e-)

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return cpt: int, zero in this case
    """
    m = len(flatimage)
    ncpos = len(pos)

    ny = int(m/dim)
    nx = int(m/ny)

    cpt = 0

    spe = np.zeros(ny, dtype=float)

    for ic in range(1, ny+1):
        jc = 0
        for j in range(1, ncpos+1):
            jc += pos[j-1] * (ic-1)**(j-1)
        lim1 = jc - nbsig
        lim2 = jc + nbsig
        # fortran int rounds the same as python int
        j1 = int(np.round(lim1) + 0.5)
        j2 = int(np.round(lim2) + 0.5)
        if (j1 > 0) and (j2 < nx):
            # for j in range(j1+1, j2):
            #     spe[ic-1] += flatimage[j+nx*(ic-1)]
            spe[ic-1] = np.sum(flatimage[j1+1+nx*(ic-1):j2+nx*(ic-1)])
            spe[ic-1] += (j1+0.5-lim1)*flatimage[j1+nx*(ic-1)]
            spe[ic-1] += (lim2-j2+0.5)*flatimage[j2+nx*(ic-1)]

            lilbit = (j1+0.5-lim1)*flatimage[j1+nx*(ic-1)]
            lilbit += (lim2-j2+0.5)*flatimage[j2+nx*(ic-1)]
            print('', ic, jc, spe[ic-1], lilbit)

            spe[ic - 1] *= gain

    sper = spe[::-1]

    return sper, cpt


def extract_const_range_wrong(image, pos, nbsig, gain):
    """
    Optimised copy of hadmrEXTOR/extract.py

    python = 12 ms  fortran = 13 ms

    axis is wrong in this case - returns spe of shape = image.shape[0]
    should return shape = image.shape[1] fixed in "extract_const_range"

    :param image: numpy array (2D), the image
    :param pos: numpy array (1D), the position fit coefficients
                size = number of coefficients for fit
    :param nbsig: float, the distance away from center to extract out to +/-
    :param gain: float, the gain of the image (for conversion from ADU/s to e-)

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    dim1, dim2 = image.shape
    nbcos = 0
    # create storage for extration
    spe = np.zeros(dim1, dtype=float)
    # create array of pixel values
    ics = np.arange(dim1)
    # get positions across the orders for each pixel value along the order
    jcs = np.polyval(pos[::-1], ics)
    # get the lower bound of the order for each pixel value along the order
    lim1s = jcs - nbsig
    # get the upper bound of the order for each pixel value along the order
    lim2s = jcs + nbsig
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim2)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # add the main order pixels
            spe[ic] = np.sum(image[ic, j1s[ic] + 1: j2s[ic]])
            # add the bits missing due to rounding
            spe[ic] += lower[ic] * image[ic, j1s[ic]]
            spe[ic] += upper[ic] * image[ic, j2s[ic]]
    # convert to e-
    spe *= gain

    return spe[::-1], nbcos


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
