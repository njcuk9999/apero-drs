#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 12:24

@author: cook
"""
import numpy as np
import warnings


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------


# =============================================================================
# Define General functions
# =============================================================================
def measure_box_min_max(y, size):
    """
    Measure the minimum and maximum pixel value for each pixel using a box which
    surrounds that pixel by:  pixel-size to pixel+size.

    Edge pixels (0-->size and (len(y)-size)-->len(y) are
    set to the values for pixel=size and pixel=(len(y)-size)

    :param y: numpy array (1D), the image
    :param size: int, the half size of the box to use (half height)
                 so box is defined from  pixel-size to pixel+size

    :return min_image: numpy array (1D length = len(y)), the values
                       for minimum pixel defined by a box of pixel-size to
                       pixel+size for all columns
    :return max_image: numpy array (1D length = len(y)), the values
                       for maximum pixel defined by a box of pixel-size to
                       pixel+size for all columns
    """
    # get length of rows
    ny = y.shape[0]
    # Set up min and max arrays (length = number of rows)
    min_image = np.zeros(ny, dtype=float)
    max_image = np.zeros(ny, dtype=float)
    # loop around each pixel from "size" to length - "size" (non-edge pixels)
    # and get the minimum and maximum of each box
    for it in range(size, ny - size):
        min_image[it] = np.nanmin(y[it - size:it + size])
        max_image[it] = np.nanmax(y[it - size:it + size])

    # deal with leading edge --> set to value at size
    min_image[0:size] = min_image[size]
    max_image[0:size] = max_image[size]
    # deal with trailing edge --> set to value at (image.shape[0]-size-1)
    min_image[ny - size:] = min_image[ny - size - 1]
    max_image[ny - size:] = max_image[ny - size - 1]
    # return arrays for minimum and maximum (box smoothed)
    return min_image, max_image


def calculate_polyvals(coeffs, dim):
    """
    Calculates all fits in coeffs array across pixels of size=dim

    :param coeffs: coefficient array,
                   size = (number of orders x number of coefficients in fit)
                   output array will be size = (number of orders x dim)
    :param dim: int, number of pixels to calculate fit for
                fit will be done over x = 0 to dim in steps of 1
    :return yfits: array,
                   size = (number of orders x dim)
                   the fit for each order at each pixel values from 0 to dim
    """
    # create storage array
    yfits = np.zeros((len(coeffs), dim))
    # get pixel range for dimension
    xfit = np.arange(0, dim, 1)
    # loop around each fit and fit
    for j_it in range(len(coeffs)):
        yfits[j_it] = np.polyval(coeffs[j_it][::-1], xfit)
    # return fits
    return yfits



# =============================================================================
# Define NaN functions
# =============================================================================
def nanpad(oimage):
    """
    Pads NaN values with the median (non NaN values from the 9 pixels around
    it) does this iteratively until no NaNs are left - if all 9 pixels are
    NaN - median is NaN

    :param oimage: numpy array (2D), the input image with NaNs
    :type oimage: np.ndarray

    :return: Nan-removed copy of original image
    :rtype: np.ndarray
    """
    image = np.array(oimage)
    # replace the NaNs on the edge with zeros
    image[:, 0] = killnan(image[:, 0], 0)
    image[0, :] = killnan(image[0, :], 0)
    image[:, -1] = killnan(image[:, -1], 0)
    image[-1, :] = killnan(image[-1, :], 0)
    # find x/y positions of NaNs
    gy, gx = np.where(~np.isfinite(image))
    # for each NaN, find the 8 neighbouring pixels and pad them
    # into an array that is 9xN.
    while len(gy) != 0:
        # array that contains neighbours to a given pixel along
        # the axis 1
        tmp = np.zeros([len(gy), 9])
        # pad the neighbour array
        for it in range(9):
            ypix = gy + (it // 3) - 1
            xpix = gx + (it % 3) - 1
            tmp[:, it] = image[ypix, xpix]
        # median the neghbours and pad back into the input image
        with warnings.catch_warnings(record=True) as _:
            image[gy, gx] = np.nanmedian(tmp, axis=1)
        # find NaNs again and pad again if needed
        gy, gx = np.where(~np.isfinite(image))
    # return padded image
    return image


def nanpolyfit(x, y, deg, **kwargs):
    # find the NaNs
    nanmask = np.isfinite(y) & np.isfinite(x)
    # return polyfit without the nans
    return np.polyfit(x[nanmask], y[nanmask], deg, **kwargs)


def killnan(vect, val=0):
    mask = ~np.isfinite(vect)
    vect[mask] = val
    return vect



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
