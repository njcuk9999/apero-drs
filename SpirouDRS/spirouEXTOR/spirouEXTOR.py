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
# Worker functions
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


# =============================================================================
# Worker functions
# =============================================================================
def extract_wrapper(p, image, pos, sig, tilt=False, weighted=False):
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
    :param tilt: bool, whether to extract using a tilt (not used yet)
    :param weighted: bool, whether to extract using weights (not used yet)

    :return spe: numpy array (1D), the extracted pixel values,
                 size = image.shape[1] (along the order direction)
    :return nbcos: int, zero in this case
    """
    # get parameters from parameter dictionary
    extopt = p['IC_EXTOPT']
    nbsig = p['IC_EXTNBSIG']
    image_gain = p['gain']

    # Option 0: Extraction by summation over constant range
    if extopt == 0 and not tilt and not weighted:
        return extract_const_range(image, pos, nbsig, image_gain)


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
