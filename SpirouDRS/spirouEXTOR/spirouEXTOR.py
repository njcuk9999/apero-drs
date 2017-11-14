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

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'spirouEXTOR.py'
# -----------------------------------------------------------------------------


# =============================================================================
# User functions
# =============================================================================
def extract_AB_order(pp, lloc, image, order_num):
    """
    Perform the extraction on the AB fibers separately using the summation
    over constant range

    :param image: numpy array (2D), the image
    :param pp: dictionary, parameter dictionary
    :param lloc: dictionary, parameter dictionary containing the data
    :param image:
    :param order_num: int, the order number for this iteration

    :return lloc: dictionary, parameter dictionary containing the data
    """
    # get the width fit coefficients for this fit
    assi = lloc['ass'][order_num]
    # --------------------------------------------------------------------
    # Center the central pixel (using the width fit)
    # get the width of the central pixel of this order
    width_cent = np.polyval(assi[::-1], pp['IC_CENT_COL'])
    # work out the offset in width for the center pixel
    lloc['offset'] = width_cent * pp['IC_FACDEC']
    lloc.set_source('offset', __NAME__ + '/extract_AB_order()')
    # --------------------------------------------------------------------
    # deal with fiber A:

    # Get the center coeffs for this order
    acci = np.array(lloc['acc'][order_num])
    # move the intercept of the center fit by -offset
    acci[0] -= lloc['offset']
    # extract the data
    lloc['cent1'], cpt = extract_wrapper(pp, image, acci, assi)
    lloc.set_source('cent1', __NAME__ + '/extract_AB_order()')
    lloc['nbcos'][order_num] = cpt
    # --------------------------------------------------------------------
    # deal with fiber B:

    # Get the center coeffs for this order
    acci = np.array(lloc['acc'][order_num])
    # move the intercept of the center fit by -offset
    acci[0] += lloc['offset']
    # extract the data
    lloc['cent2'], cpt = extract_wrapper(pp, image, acci, assi)
    lloc.set_source('cent2', __NAME__ + '/extract_AB_order()')
    lloc['nbcos'][order_num] = cpt

    # return loc dictionary
    return lloc


def extract_tilt_weight_order(pp, loc, image, orderp, rnum):
    # construct the args and keyword args for extract wrapper
    extargs = [pp, image, loc['acc'][rnum], loc['ass'][rnum]]
    extkwargs = dict(tilt=loc['tilt'][rnum], order_profile=orderp,
                     use_weights=True)
    # get the extraction for this order using the extract wrapper
    return extract_wrapper(*extargs, **extkwargs)


# =============================================================================
# Worker functions
# =============================================================================
def extract_wrapper(p, image, pos, sig, **kwargs):
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

        tilt:           numpy array (1D), the tilt for this order, if defined
                        uses tilt, if not defined does not

        use_weights:    bool, if True use weighted extraction, if False or not
                        defined does not use weighted extraction

        order_profile:  numpy array (2D), the image with fit superposed on top,
                        required for tilt and or weighted fit

        mode:           if use_weights and tilt is not None then
                        if mode = 'old'  will use old code (use this if
                        exception generated)
                        extract_tilt_weight_order_old() is run

                        else mode = 'new' and
                        extract_tilt_weight_order() is run

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    # get parameters from parameter dictionary
    extopt = p['IC_EXTOPT']
    nbsig = p['IC_EXTNBSIG']
    image_gain = p['gain']
    image_sigdet = p['sigdet']
    range1 = p['IC_EXT_RANGE1']
    range2 = p['IC_EXT_RANGE2']
    mode = kwargs.get('mode', 'new')
    # get parameters from keyword arguments
    tilt = kwargs.get('tilt', None)
    use_weights = kwargs.get('use_weights', False)
    order_profile = kwargs.get('order_profile', None)

    # Option 0: Extraction by summation over constant range
    if extopt == 0 and (tilt is None) and not use_weights:
        return extract_const_range(image, pos, nbsig, image_gain)

    # Extra: if tilt defined and order_profile defined and use_weights = True
    #        Extract using a weighted tilt
    elif tilt is not None and order_profile is not None and use_weights:
        args = [image, pos, tilt, range1, range2,
                order_profile, image_gain, image_sigdet]
        if mode == 'old':
            return extract_tilt_weight_old(*args)
        else:
            return extract_tilt_weight(*args)



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
    ind1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    ind2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (ind1s > 0) & (ind2s < dim1)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = ind1s + 0.5 - lim1s, lim2s - ind2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # add the main order pixels
            spe[ic] = np.sum(image[ind1s[ic] + 1: ind2s[ic], ic])
            # add the bits missing due to rounding
            spe[ic] += lower[ic] * image[ind1s[ic], ic]
            spe[ic] += upper[ic] * image[ind2s[ic], ic]
    # convert to e-
    spe *= gain

    return spe[::-1], nbcos


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
        Fx /= np.sum(Fx)
        # weight values less than 0 to 1e-9
        raw_weights = np.where(Sx > 0, 1, 1e-9)
        # weights are then modified by the gain and sigdet added in quadrature
        weights = raw_weights / ((Sx * gain) + sigdet**2)
        # set the value of this pixel to the weighted sum
        spe[ic] = np.sum(weights * Sx * Fx)/np.sum(weights * Fx**2)
    # multiple spe by gain to convert to e-
    spe *= gain

    return spe, 0


def extract_tilt_weight_old(image, pos, tilt, r1, r2, orderp,
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
        Fx /= np.sum(Fx)
        # weight values less than 0 to 1e-9
        raw_weights = np.where(Sx > 0, 1, 1e-9)
        # weights are then modified by the gain and sigdet added in quadrature
        weights = raw_weights / ((Sx * gain) + sigdet**2)
        # set the value of this pixel to the weighted sum
        spe[ic] = np.sum(weights * Sx * Fx)/np.sum(weights * Fx**2)
    # multiple spe by gain to convert to e-
    spe *= gain

    return spe, 0


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
    ncsig = len(sig)

    ny = int(m/dim)
    nx = int(m/ny)

    cpt = 0

    spe = np.zeros(ny, dtype=float)
    sper = np.zeros(ny, dtype=float)

    for ic in range(1, ny+1):
        jc = 0
        for j in range(1, ncpos+1):
            jc += pos[j-1] * (ic-1)**(j-1)
        lim1 = jc - nbsig
        lim2 = jc + nbsig
        # fortran int rounds the same as python int
        ind1 = int(np.round(lim1) + 0.5)
        ind2 = int(np.round(lim2) + 0.5)
        if (ind1 > 0) and (ind2 < nx):
            # for j in range(ind1+1, ind2):
            #     spe[ic-1] += flatimage[j+nx*(ic-1)]
            spe[ic-1] = np.sum(flatimage[ind1+1+nx*(ic-1):ind2+nx*(ic-1)])
            spe[ic-1] += (ind1+0.5-lim1)*flatimage[ind1+nx*(ic-1)]
            spe[ic-1] += (lim2-ind2+0.5)*flatimage[ind2+nx*(ic-1)]

            lilbit = (ind1+0.5-lim1)*flatimage[ind1+nx*(ic-1)]
            lilbit += (lim2-ind2+0.5)*flatimage[ind2+nx*(ic-1)]
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
    ind1s = np.array(np.round(lim1s), dtype=int)
    # get the integer pixel position of the upper bounds
    ind2s = np.array(np.round(lim2s), dtype=int)
    # make sure the pixel positions are within the image
    mask = (ind1s > 0) & (ind2s < dim2)
    # account for the missing fractional pixels (due to integer rounding)
    lower, upper = ind1s + 0.5 - lim1s, lim2s - ind2s + 0.5
    # loop around each pixel along the order and, if it is within the image,
    #   sum the values contained within the order (including the bits missing
    #   due to rounding)
    for ic in ics:
        if mask[ic]:
            # add the main order pixels
            spe[ic] = np.sum(image[ic, ind1s[ic] + 1: ind2s[ic]])
            # add the bits missing due to rounding
            spe[ic] += lower[ic] * image[ic, ind1s[ic]]
            spe[ic] += upper[ic] * image[ic, ind2s[ic]]
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
