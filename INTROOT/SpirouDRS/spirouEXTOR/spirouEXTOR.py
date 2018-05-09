#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou extraction functions

Created on 2017-11-07 at 13:46

@author: cook

"""
from __future__ import division
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
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# User functions
# =============================================================================
# noinspection PyPep8Naming
def extract_AB_order(pp, loc, image, rnum):
    """
    Perform the extraction on the AB fibers separately using the summation
    over constant range

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_CENT_COL: int, the column number (x-axis) of the central
                             column
                IC_FACDEC: float, the offset multiplicative factor for width
                IC_EXTOPT: int, the extraction option
                gain: float, the gain of the image
                IC_EXTNBSIG: float, distance away from center to extract
                             out to +/- (in rows or y-axis direction)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)


    :param image: numpy array (2D), the image
    :param rnum: int, the order number for this iteration

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                offset: numpy array (1D), the center values with the
                        offset in 'IC_CENT_COL' added
                cent1: numpy array (2D), the extraction for A, updated is
                       the order "rnum"
                nbcos: int, 0 (constant)
                cent2: numpy array (2D), the extraction for B, updated is
                       the order "rnum"
    """
    # get the width fit coefficients for this fit
    assi = loc['ASS'][rnum]
    # --------------------------------------------------------------------
    # Center the central pixel (using the width fit)
    # get the width of the central pixel of this order
    width_cent = np.polyval(assi[::-1], pp['IC_CENT_COL'])
    # work out the offset in width for the center pixel
    loc['OFFSET'] = width_cent * pp['IC_FACDEC']
    loc.set_source('OFFSET', __NAME__ + '/extract_AB_order()')
    # --------------------------------------------------------------------
    # deal with fiber A:

    # Get the center coeffs for this order
    acci = np.array(loc['ACC'][rnum])
    # move the intercept of the center fit by -offset
    acci[0] -= loc['OFFSET']
    # extract the data
    eargs = [image, acci, assi]
    ekwargs = dict(extopt=pp['IC_EXTOPT'], 
                   gain=pp['GAIN'],                 
                   range1=pp['IC_EXTNBSIG'],
                   range2=pp['IC_EXTNBSIG'])
    loc['CENT1'], cpt = extract_wrapper(*eargs, **ekwargs)
    loc.set_source('CENT1', __NAME__ + '/extract_AB_order()')
    loc['NBCOS'][rnum] = cpt
    # --------------------------------------------------------------------
    # deal with fiber B:

    # Get the center coeffs for this order
    acci = np.array(loc['ACC'][rnum])
    # move the intercept of the center fit by -offset
    acci[0] += loc['OFFSET']
    # extract the data
    eargs = [image, acci, assi]
    ekwargs = dict(extopt=pp['IC_EXTOPT'], 
                   gain=pp['GAIN'],                 
                   range1=pp['IC_EXTNBSIG'],
                   range2=pp['IC_EXTNBSIG'])
    loc['CENT2'], cpt = extract_wrapper(*eargs, **ekwargs)
    loc.set_source('CENT2', __NAME__ + '/extract_AB_order()')
    loc['NBCOS'][rnum] = cpt

    # return loc dictionary
    return loc


def extract_order(pp, loc, image, rnum, **kwargs):
    """
    Extract order without tilt or weight using spirouEXTOR.extract_wrapper()

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_EXTOPT: int, the extraction option
                IC_EXT_RANGE: float, the upper and lower edge of the order
                              in rows (y-axis) - half-zone width
                gain: float, the gain of the image

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)

    :param image: numpy array (2D), the image
    :param rnum: int, the order number for this iteration
    :param kwargs: additional keywords to pass to the extraction wrapper

            - allowed keywords are:

            range1  (defaults to "IC_EXT_RANGE")
            range2  (defaults to "IC_EXT_RANGE")
            gain    (defaults to "GAIN")

    :return cent: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return cpt: int, zero in this case
    """
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['ACC'][rnum], loc['ASS'][rnum]]
    ekwargs = dict(use_tilt=False, 
                   use_weight=False,
                   extopt=pp['IC_EXTOPT'],
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   gain=kwargs.get('gain', pp['GAIN']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_tilt_order(pp, loc, image, rnum, **kwargs):
    """
    Extract order with tilt but without weight using
    spirouEXTOR.extract_wrapper()

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_EXT_RANGE: float, the upper and lower edge of the order
                              in rows (y-axis) - half-zone width
                gain: float, the gain of the image

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)
                tilt: numpy array (1D), the tilt angle of each order

    :param image: numpy array (2D), the image
    :param rnum: int, the order number for this iteration
    :param kwargs: additional keywords to pass to the extraction wrapper

            - allowed keywords are:

            range1  (defaults to "IC_EXT_RANGE")
            range2  (defaults to "IC_EXT_RANGE")
            gain    (defaults to "GAIN")

    :return cent: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return cpt: int, zero in this case
    """
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['ACC'][rnum], loc['ASS'][rnum]]
    ekwargs = dict(use_tilt=True, 
                   use_weight=False,
                   tilt=loc['TILT'][rnum],
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   gain=kwargs.get('gain', pp['GAIN']),
                   tilt_bdr=kwargs.get('tilt_bdr', pp['IC_EXT_TILT_BORD']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_tilt_weight_order(pp, loc, image, orderp, rnum, **kwargs):
    """
    Extract order with tilt and weight using
    spirouEXTOR.extract_wrapper() with mode=1
    (extract_tilt_weight_order_old() is run)

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_EXT_RANGE: float, the upper and lower edge of the order
                              in rows (y-axis) - half-zone width
                gain: float, the gain of the image
                sigdet: float, the read noise of the image

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)
                tilt: numpy array (1D), the tilt angle of each order

    :param image: numpy array (2D), the image
    :param orderp: numpy array (2D), the order profile image
    :param rnum: int, the order number for this iteration
    :param kwargs: additional keywords to pass to the extraction wrapper

            - allowed keywords are:

            range1  (defaults to "IC_EXT_RANGE")
            range2  (defaults to "IC_EXT_RANGE")
            gain    (defaults to "GAIN")
            sigdet  (defaults to "SIGDET")

    :return cent: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return cpt: int, zero in this case
    """
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['ACC'][rnum], loc['ASS'][rnum]]
    ekwargs = dict(use_tilt=True, 
                   use_weight=True,
                   tilt=loc['TILT'][rnum], 
                   order_profile=orderp,
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   mode=1,
                   gain=kwargs.get('gain', pp['GAIN']),
                   sigdet=kwargs.get('sigdet', pp['SIGDET']),
                   tilt_bdr=kwargs.get('tilt_bdr', pp['IC_EXT_TILT_BORD']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_tilt_weight_order2(pp, loc, image, orderp, rnum, **kwargs):
    """
    Extract order with tilt and weight using
    spirouEXTOR.extract_wrapper() with mode=2
    (extract_tilt_weight_order() is run)

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_EXT_RANGE1: float, the upper edge of the order in rows
                               (y-axis) - half-zone width (lower)
                IC_EXT_RANGE2: float, the lower edge of the order in rows
                               (y-axis) - half-zone width (upper)
                gain: float, the gain of the image
                sigdet: float, the read noise of the image

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)
                tilt: numpy array (1D), the tilt angle of each order

    :param image: numpy array (2D), the image
    :param orderp: numpy array (2D), the order profile image
    :param rnum: int, the order number for this iteration
    :param kwargs: additional keywords to pass to the extraction wrapper

            - allowed keywords are:

            range1  (defaults to "IC_EXT_RANGE1")
            range2  (defaults to "IC_EXT_RANGE2")
            gain    (defaults to "GAIN")
            sigdet  (defaults to "SIGDET")

    :return cent: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return cpt: int, zero in this case
    """
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['ACC'][rnum], loc['ASS'][rnum]]
    ekwargs = dict(use_tilt=True,
                   use_weight=True,
                   tilt=loc['TILT'][rnum], 
                   order_profile=orderp,
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE1']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE2']),
                   mode=2,
                   gain=kwargs.get('gain', pp['GAIN']),
                   sigdet=kwargs.get('sigdet', pp['SIGDET']),
                   tilt_bdr=kwargs.get('tilt_bdr', pp['IC_EXT_TILT_BORD']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


def extract_weight_order(pp, loc, image, orderp, rnum, **kwargs):
    """
    Extract order with weight but without tilt using
    spirouEXTOR.extract_wrapper()

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_EXT_RANGE: float, the upper and lower edge of the order
                              in rows (y-axis) - half-zone width
                gain: float, the gain of the image
                sigdet: float, the read noise of the image

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)

    :param image: numpy array (2D), the image
    :param orderp: numpy array (2D), the order profile image
    :param rnum: int, the order number for this iteration
    :param kwargs: additional keywords to pass to the extraction wrapper

            - allowed keywords are:

            range1  (defaults to "IC_EXT_RANGE")
            range2  (defaults to "IC_EXT_RANGE")
            gain    (defaults to "GAIN")
            sigdet  (defaults to "SIGDET")

    :return cent: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return cpt: int, zero in this case
    """
    # construct the args and keyword args for extract wrapper
    eargs = [image, loc['ACC'][rnum], loc['ASS'][rnum]]
    ekwargs = dict(use_tilt=False,
                   use_weight=True,
                   tilt=None, 
                   order_profile=orderp,
                   range1=kwargs.get('range1', pp['IC_EXT_RANGE']),
                   range2=kwargs.get('range2', pp['IC_EXT_RANGE']),
                   gain=kwargs.get('gain', pp['GAIN']),
                   sigdet=kwargs.get('sigdet', pp['SIGDET']))
    # get the extraction for this order using the extract wrapper
    cent, cpt = extract_wrapper(*eargs, **ekwargs)
    # return 
    return cent, cpt


# =============================================================================
# Worker functions
# =============================================================================
def extract_wrapper(image, pos, sig, **kwargs):
    """
    Extraction wrapper - takes in image, pos, sig and kwargs and decides
    which extraction process to use.

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
                        defaults to p['NBSIG'] from constants_SPIROU.py

        gain:           float, gain of the image
                        defaults to p['GAIN'] from fitsfilename HEADER

        sigdet:         float, the sigdet of the image
                        defaults to p['SIGDET'] from fitsfilename HEADER

        range1:         float, Half-zone extraction width left side
                        (formally plage1)
                        defaults to p['IC_EXT_RANGE1'] from fiber parameters in
                        constatns_SPIROU.txt

        range2:         float, Half-zone extraction width left side
                        (formally plage2)
                        defaults to p['IC_EXT_RANGE2'] from fiber parameters in
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
    tilt_border = kwargs.get('tilt_bdr', None)
    # get parameters from keyword arguments but default to False
    use_tilt = kwargs.get('use_tilt', False)
    use_weight = kwargs.get('use_weight', False)
    # check len of pos and sig are the same
    if pos.shape != sig.shape:
        WLOG('error', '', ('"pos" and "sig" do not have the same shape '
                           '({0}.extract_wrapper())'.format(__NAME__)))
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
        check_for_none(tilt_border, 'tilt_border')
        # run extract and return
        ekwargs = dict(image=image, pos=pos, tilt=tilt, r1=range1, r2=range2,
                       orderp=order_profile, gain=gain, sigdet=sigdet,
                       tiltborder=tilt_border)
        if mode == 0:
            return extract_tilt_weight(**ekwargs)
            # return extract(**ekwargs)
        if mode == 1:
            return extract_tilt_weight(**ekwargs)
            # return extract(**ekwargs)
        if mode == 2:
#            return extract_tilt_weight2(**ekwargs)
            return extract_tilt_weight2cosm(**ekwargs)
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
        check_for_none(tilt_border, 'tilt_border')
        # run extract and return
        ekwargs = dict(image=image, pos=pos, tilt=tilt, r1=range1, r2=range2,
                       gain=gain, tiltborder=tilt_border)
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


def extract_tilt(image, pos, tilt, r1, r2, gain, tiltborder=2):
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
    :param tiltborder: int, the number of pixels to set as the border (needed
                       to allow for tilt to not go off edge of image)

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
    i1s = ics - tiltborder
    i2s = ics + tiltborder
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # get the weight contribution matrix (look up table)
    wwa = work_out_ww(ww0, ww1, tiltshift, r1)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics[tiltborder:-tiltborder]:
        if mask[ic]:
            # get ww0i and ww1i for this iteration
            ww0i, ww1i = ww0[ic], ww1[ic]
            ww = wwa[(ww0i, ww1i)]
            # multiple the image by the rotation matrix
            sx = image[j1s[ic]+1:j2s[ic], i1s[ic]:i2s[ic] + 1] * ww[1:-1]
            spe[ic] = np.sum(sx)
            # add the main order pixels
            # add the bits missing due to rounding
            sxl = image[j1s[ic], i1s[ic]:i2s[ic] + 1] * ww[0]
            spe[ic] += lower[ic] * np.sum(sxl)
            sxu = image[j2s[ic], i1s[ic]:i2s[ic] + 1] * ww[-1]
            spe[ic] += upper[ic] * np.sum(sxu)
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
            sx = image[j1s[ic] + 1: j2s[ic], ic]
            sx1 = image[j1s[ic]: j2s[ic] + 1, ic]
            # Get the extraction of the order_profile
            fx = orderp[j1s[ic]:j2s[ic] + 1, ic]
            # Renormalise the order_profile
            fx = fx / np.sum(fx)
            # get the weights
            # weight values less than 0 to 0.000001
            raw_weights = np.where(sx1 > 0, 1, 0.000001)
            weights = fx * raw_weights
            # get the normalisation (equal to the sum of the weights squared)
            norm = np.sum(weights**2)
            # add the main extraction to array
            spe[ic] = np.sum(sx * weights[1:-1])
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


def extract_tilt_weight2(image, pos, tilt, r1, r2, orderp, gain, sigdet,
                         tiltborder=2):
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
    :param tiltborder: int, the number of pixels to set as the border (needed
                       to allow for tilt to not go off edge of image)

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
    i1s = ics - tiltborder
    i2s = ics + tiltborder
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # get the weight contribution matrix (look up table)
    wwa = work_out_ww(ww0, ww1, tiltshift, r1)
    # loop around each pixel along the order
    for ic in ics[tiltborder:-tiltborder]:
        if mask[ic]:
            # get ww0i and ww1i for this iteration
            ww0i, ww1i = ww0[ic], ww1[ic]
            ww = wwa[(ww0i, ww1i)]
            # multiple the image by the rotation matrix
            sx = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
            # multiple the order_profile by the rotation matrix
            fx = orderp[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
            # Renormalise the rotated order profile
            fx = fx / np.sum(fx)
            # weight values less than 0 to 1e-9
            raw_weights = np.where(sx > 0, 1, 1e-9)
            # weights are then modified by the gain and sigdet added in quadrature
            weights = raw_weights / ((sx * gain) + sigdet**2)
            # set the value of this pixel to the weighted sum
            spe[ic] = np.sum(weights * sx * fx)/np.sum(weights * fx**2)
    # multiple spe by gain to convert to e-
    spe *= gain

    return spe, 0

def extract_tilt_weight2cosm(image, pos, tilt, r1, r2, orderp, gain, sigdet,
                         tiltborder=2):
    """
    Extract order using tilt and weight (sigdet and badpix) and cosmic correction

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
    :param tiltborder: int, the number of pixels to set as the border (needed
                       to allow for tilt to not go off edge of image)

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
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # get the weight contribution matrix (look up table)
    wwa = work_out_ww(ww0, ww1, tiltshift, r1)
    # count of the detected cosmic rays
    cpt = 0
    # loop around each pixel along the order
    for ic in ics[tiltborder:-tiltborder]:
        if mask[ic]:
            # get ww0i and ww1i for this iteration
            ww0i, ww1i = ww0[ic], ww1[ic]
            ww = wwa[(ww0i, ww1i)]
            # multiple the image by the rotation matrix
            sx = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
            # multiple the order_profile by the rotation matrix
            fx = orderp[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
            # Renormalise the rotated order profile
            fx = fx / np.sum(fx)
            # weight values less than 0 to 1e-9
            raw_weights = np.where(sx > 0, 1, 1e-9)
            # weights are then modified by the gain and sigdet added in quadrature
            weights = raw_weights / ((sx * gain) + sigdet**2)
            # set the value of this pixel to the weighted sum
            spe[ic] = np.sum(weights * sx * fx)/np.sum(weights * fx**2)
            # Cosmic rays correction
            crit = (sx  - spe[ic] * fx)
            sigcut = 0.25 # 25% of the flux
            cosmask = np.ones(np.shape(crit),'d')
            nbloop=0
            while np.max(crit) > sigcut * spe[ic] and nbloop<5:
#                print('cosmic detected in line %i with amp %.2f' %(ic,np.max(crit)/spe[ic]))
                cosmask = np.where(crit>np.max(crit)-0.1,0.,cosmask)
                spe[ic] = np.sum(weights * cosmask * sx * fx) / np.sum(weights * cosmask * fx ** 2)
                crit = (sx * cosmask - spe[ic] * fx * cosmask)
                cpt += 1
                nbloop += 1
#        crit = (data[ic, ind1:ind2 + 1] * ccdgain - spe[ic] * profil) ** 2 / var
#        seuil = seuilcosmic * spe[ic]
#        while max(crit) > max(seuil, 25):
            #	    print 'COSMICS DETECTED',max(crit),' Line',ic
#            cpt = cpt + 1
#            masque = masque - greater(crit, max(crit) - 0.1)
#            masque = clip(masque, 0., 1.)
#            norm = sum(profil * profil * masque / var)
#            spe[ic] = (sum(data[ic, ind1 + 1:ind2, ] * ccdgain * profil[1:-1] * masque[1:-1] / var[1:-1]) + \
#                       c1 * data[ic, ind1] * ccdgain * profil[0] * masque[0] / var[0] + \
#                       c2 * data[ic, ind2] * ccdgain * profil[-1] * masque[-1] / var[-1]) / norm
#            var = profil * spe[ic] + sigdet ** 2
#            seuil = seuilcosmic * spe[ic]
#            crit = (data[ic, ind1:ind2 + 1] * ccdgain * masque - spe[ic] * masque * profil) ** 2 / var
#    print    'Nb cosmics detected : ', cpt

    # multiple spe by gain to convert to e-
#    print('Nb cosmic detected  %i' %(cpt))
    spe *= gain

    return spe, cpt


def work_out_ww(ww0, ww1, tiltshift, r1):
    """
    Calculate the tilting contribution matrix

    We only need to calculate the tilt contribution matrix for each unique
    value in ww0 and ww1 (only changes by +/- 1 due to rounding)

    :param ww0: numpy array (1D), the end positions for lower bounds
    :param ww1: numpy array (1D), the end postitions for upper bounds
    :param tiltshift: float, tangent of the tilt in radians
    :param r1: float, the distance between center and lower bound

    :return wwall: dictionary with tuple keys giving unique lower bound
                   and upper bound combinations values are the tilt matrix
                   at each unique set of bounds
    """
    # find unique values of ww0 and ww1
    uww0 = np.unique(ww0)
    uww1 = np.unique(ww1)
    # add dictionary for unique values in ww0 and ww1
    wwall = dict()
    # loop around unique values in ww0
    for ww0i in uww0:
        # loop around unique values in ww1
        for ww1i in uww1:
            # create a box of the correct size
            ww = np.zeros((ww0i, ww1i))
            # calculate the tilt shift for each pixel in the box
            ff = tiltshift * (np.arange(ww0i) - r1)
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
            # add to dictionary
            wwall[(ww0i, ww1i)] = ww

    # finally return the ww for all unique combinations
    return wwall


def extract_tilt_weight_old2(image, pos, tilt, r1, r2, orderp,
                             gain, sigdet, tiltborder=2):
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
    :param tiltborder: int, the number of pixels to set as the border (needed
                       to allow for tilt to not go off edge of image)

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
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # loop around each pixel along the order
    for ic in ics[tiltborder:-tiltborder]:
        if mask[ic]:
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
            sx = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
            # multiple the order_profile by the rotation matrix
            fx = orderp[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
            # Renormalise the rotated order profile
            fx = fx / np.sum(fx)
            # weight values less than 0 to 1e-9
            raw_weights = np.where(sx > 0, 1, 1e-9)
            # weights are then modified by the gain and sigdet added
            #     in quadrature
            weights = raw_weights / ((sx * gain) + sigdet**2)
            # set the value of this pixel to the weighted sum
            spe[ic] = np.sum(weights * sx * fx)/np.sum(weights * fx**2)
    # multiple spe by gain to convert to e-
    spe *= gain

    return spe, 0


def extract_tilt_weight(image, pos, tilt, r1, r2, orderp, gain, sigdet,
                        tiltborder):
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
    :param tiltborder: int, the number of pixels to set as the border (needed
                       to allow for tilt to not go off edge of image)

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
    i1s = ics - tiltborder
    i2s = ics + tiltborder
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1
    # calculate the tilt shift
    tiltshift = np.tan(np.deg2rad(tilt))
    # get the weight contribution matrix (look up table)
    wwa = work_out_ww(ww0, ww1, tiltshift, r1)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics[tiltborder:-tiltborder]:
        if mask[ic]:
            # get ww0i and ww1i for this iteration
            ww0i, ww1i = ww0[ic], ww1[ic]
            ww = wwa[(ww0i, ww1i)]
            # Get the extraction of the main profile
            sx = image[j1s[ic] + 1: j2s[ic], i1s[ic]: i2s[ic]+1] * ww[1:-1]
            sx1 = image[j1s[ic]: j2s[ic] + 1, i1s[ic]: i2s[ic]+1]
            # Get the extraction of the order_profile
            fx = orderp[j1s[ic]: j2s[ic] + 1, i1s[ic]: i2s[ic]+1]
            # Renormalise the order_profile
            fx = fx/np.sum(fx)
            # get the weights
            # weight values less than 0 to 0.000001
            raw_weights = np.where(sx1 > 0, 1, 0.000001)
            weights = fx * raw_weights
            # get the normalisation (equal to the sum of the weights squared)
            norm = np.sum(weights**2)
            # add the main extraction to array
            mainvalues = np.sum(sx * weights[1:-1], 1)
            # add the bits missing due to rounding
            sxl = image[j1s[ic], i1s[ic]:i2s[ic] + 1] * ww[0] * weights[0]
            lowervalue = lower[ic] * np.sum(sxl)
            sxu = image[j2s[ic], i1s[ic]:i2s[ic] + 1] * ww[-1] * weights[-1]
            uppervalue = upper[ic] * np.sum(sxu)
            # add lower and upper constants to array and sum over all
            # Question: Is this correct or a typo?
            # Question: Is the intention to add contribution due to lower
            # Question:    and upper end to each of the main pixels, or
            # Question:    just to the total?
            spe[ic] = np.sum(mainvalues + lowervalue + uppervalue)
            # divide by the normalisation
            spe[ic] /= norm
    # convert to e-
    spe *= gain
    # return spe and nbcos
    return spe, nbcos


def extract_tilt_weight_old(image, pos, tilt=None, r1=None, r2=None,
                            orderp=None, gain=None, sigdet=None, tiltborder=2):
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
    :param orderp: numpy array (2D), the image with fit superposed
                   (zero filled)
    :param gain: float, the gain of the image (for conversion from
                 ADU/s to e-)
    :param sigdet: float, the sigdet to use in the weighting
                   weights = 1/(signal*gain + sigdet^2) with bad pixels
                   multiplied by a weight of 1e-9 and good pixels
                   multiplied by 1
    :param tiltborder: int, the number of pixels to set as the border (needed
                       to allow for tilt to not go off edge of image)

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
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
    i1s = ics - tiltborder
    i2s = ics + tiltborder
    # get the integer pixel position of the lower bounds
    j1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    j2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (j1s > 0) & (j2s < dim1)
    # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
    ww0, ww1 = j2s - j1s + 1, i2s - i1s + 1

    # check that ww0 and ww1 are constant (They should be)
    if len(np.unique(ww0)) != 1:
        raise ValueError('Neil error: Assumption that ww0 is constant is'
                         'wrong (spirouEXTOR.py/extract_tilt_weight)')
    # get tilt matrix (if we have tilt)
    ww = get_tilt_matrix(ww0, ww1, r1, r2, tilt)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = j1s + 0.5 - lim1s, lim2s - j2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # Get the extraction of the main profile
            sx = image[j1s[ic] + 1: j2s[ic], ic]
            # Get the extraction of the order_profile
            # (if no weights then set to 1)
            if orderp is None:
                fx = np.ones_like(sx)
            else:
                fx = orderp[j1s[ic]:j2s[ic] + 1, ic]
                # Renormalise the order_profile
                fx = fx / np.sum(fx)
            # add the main order pixels
            spe[ic] = np.sum(sx)
            # get the weights
            # weight values less than 0 to 0.000001
            raw_weights = np.where(sx > 0, 1, 0.000001)
            weights = fx * raw_weights
            # get the normalisation (equal to the sum of the weights squared)
            norm = np.sum(weights**2)
            # add the main extraction to array
            s_sx = np.sum(sx)
            spe[ic] = s_sx * weights[1:-1] * ww[1:-1]
            # add the bits missing due to rounding
            sxl = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1]
            sxl *= ww[0] * weights[1:-1]
            spe[ic] += lower[ic] * np.sum(sxl)
            sxu = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1]
            sxu *= ww[-1] * weights[1:-1]
            spe[ic] += upper[ic] * np.sum(sxu)
            # divide by the normalisation
            spe[ic] /= norm
    # convert to e-
    spe *= gain
    # return spe and nbcos
    return spe, nbcos


# =============================================================================
# Other functions
# =============================================================================
def get_valid_orders(p, loc):
    """
    Get valid order range (from min to max) from constants

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            EXT_START_ORDER: int or None, the order number to start with, if
                             None this is set to zero
            EXT_END_ORDER: int or None, the order number to end with, if None
                           this is set to the last order number
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            number_orders: int, the number of orders in reference spectrum
    :return valid_ordesr: list, all integer values between the start order and
                          end order
    """
    func_name = __NAME__ + '.get_valid_orders()'
    # get from p or set or get from loc
    if str(p['EXT_START_ORDER']) == 'None':
        order_range_lower = 0
    else:
        order_range_lower = p['EXT_START_ORDER']
    if str(p['EXT_END_ORDER']) == 'None':
        order_range_upper = loc['NUMBER_ORDERS']
    else:
        order_range_upper = p['EXT_END_ORDER']

    # check that order_range_lower is valid
    try:
        orl = int(order_range_lower)
        if orl < 0:
            raise ValueError
    except ValueError:
        emsg1 = 'EXT_START_ORDER = {0}'.format(order_range_lower)
        emsg2 = '    must be "None" or a valid positive integer'
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
        orl = 0
    # check that order_range_upper is valid
    try:
        oru = int(order_range_upper)
        if oru < 0:
            raise ValueError
    except ValueError:
        emsg1 = 'EXT_END_ORDER = {0}'.format(order_range_upper)
        emsg2 = '    must be "None" or a valid positive integer'
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
        oru = 0
    # return the range of the orders
    return list(range(orl, oru))


def check_for_none(value, name, fname=None):
    """
    Checks is value is None, if it is an error is generated
    For specific use in spirouEXTOR.extract_wrapper() but can be used elsewhere
    by defining the fname parameter

    Generates WLOG error exit if value is None

    :param value: object, the object to test whether it is None
    :param name: string, the (printable) name for value
    :param fname: string or None, if not None the function name check_for_none
                  is called from, if None defaults to
                  spirouEXTOR.extract_wrapper()

    :return None:
    """
    # func name
    if fname is None:
        fname = __NAME__ + '/extract_wrapper()'
    if value is None:
        emsg = 'Keyword "{0}" is not defined for {1}'
        WLOG('error', '', emsg.format(name, fname))


def get_tilt_matrix(ww0, ww1, r1, r2, tilt=None):
    """
    Work out tilt matrix

    :param ww0: numpy array (1D), the end positions for lower bounds
    :param ww1: numpy array (1D), the end postitions for upper bounds
    :param r1: float, the distance between center and lower bound
    :param r2: float, the distance between center and upper bound
    :param tilt: float, the tilt in degrees

    :return ww: the tilt matrix
    """
    # get tilt (or set to zero)
    if tilt is None:
        tiltshift = 0.0
    else:
        # calculate the tilt shift
        tiltshift = np.tan(np.deg2rad(tilt))
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
    # return tilt matrix
    return ww


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
# End of code
# =============================================================================
