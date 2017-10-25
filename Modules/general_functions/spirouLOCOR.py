#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-25 at 11:31

@author: cook



Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def smoothed_boxmean_image(image, size, weighted=True):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param weighted: bool, if True pixel values less than zero are weighted to
                     a value of 1e-6 and values above 0 are weighted to a value
                     of 1

    :return newimage: numpy array (2D), the smoothed image
    """
    newimage = np.zeros_like(image)

    # loop around each pixel column
    for it in range(0, image.shape[1], 1):
        # deal with leading edge --> i.e. box expands until it is full size
        if it < size:
            # get the subimage defined by the box for all rows
            part = image[:, 0:it + size + 1]
        # deal with main part (where box is of size="size"
        elif size <= it <= image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size: it + size + 1]
        # deal with the trailing edge --> i.e. box shrinks from full size
        elif it > image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size: it + size + 1]
        # get the weights (pixels below 0 are set to 1e-6, pixels above to 1)
        if weighted:
            weights = np.where(part > 0, 1, 1.e-6)
        else:
            weights = np.ones(len(part))
        # apply the weighted mean for this column
        newimage[:, it] = np.average(part, axis=1, weights=weights)
    # return the new smoothed image
    return newimage


def measure_box_min_max(image, size):
    """
    Measure the minimum and maximum pixel value for each row using a box which
    contains all pixels for rows:  row-size to row+size and all columns.

    Edge pixels (0-->size and (image.shape[0]-size)-->image.shape[0] are
    set to the values for row=size and row=(image.shape[0]-size)

    :param image: numpy array (2D), the image
    :param size: int, the half size of the box to use (half height)
                 so box is defined from  row-size to row+size

    :return min_image: numpy array (1D length = image.shape[0]), the row values
                       for minimum pixel defined by a box of row-size to
                       row+size for all columns
    :retrun max_image: numpy array (1D length = image.shape[0]), the row values
                       for maximum pixel defined by a box of row-size to
                       row+size for all columns
    """
    # get length of rows
    ny = image.shape[0]
    # Set up min and max arrays (length = number of rows)
    min_image = np.zeros(ny, dtype=float)
    max_image = np.zeros(ny, dtype=float)
    # loop around each pixel from "size" to length - "size" (non-edge pixels)
    # and get the minimum and maximum of each box
    for it in range(size, ny - size):
        min_image[it] = np.min(image[it-size:it+size])
        max_image[it] = np.max(image[it-size:it+size])

    # deal with leading edge --> set to value at size
    min_image[0:size] = min_image[size]
    max_image[0:size] = max_image[size]
    # deal with trailing edge --> set to value at (image.shape[0]-size-1)
    min_image[ny-size:] = min_image[ny-size-1]
    max_image[ny-size:] = max_image[ny-size-1]
    # return arrays for minimum and maximum (box smoothed)
    return min_image, max_image


def locate_order_positions(cvalues, threshold):
    """
    Takes the central pixel values and finds orders by looking for the start
    and end above threshold

    :param cvalues: numpy array (1D) size = number of rows,
                    the central pixel values
    :param threshold: float, the threshold above which to find pixels as being
                      part of an order

    :return positions: numpy array (1D), size= number of rows,
                       the pixel positions in cvalues where the centers of each
                       order should be
    """

# =============================================================================
# End of code
# =============================================================================
