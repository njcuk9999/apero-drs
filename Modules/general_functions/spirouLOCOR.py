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
def smoothed_boxmean_image(image, size, weighted=True, mode='convolve'):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels.

        if mode='convolve' (default) then this is done
        by convolving a tophat function with the image (FAST)

        if mode='manual' then this is done by working out the mean in each
        box manually (SLOW)

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
    if mode=='convolve':
        return smoothed_boxmean_image2(image, size, weighted=weighted)
    if mode=='manual':
        return smoothed_boxmean_image1(image, size, weighted=weighted)
    else:
        emsg = 'mode keyword={0} not valid. Must be "convolve" or "manual"'
        raise KeyError(emsg.format(mode))


def smoothed_boxmean_image1(image, size, weighted=True):
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

    For 1 loop, best of 3: 628 ms per loop
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


def smoothed_boxmean_image2(image, size, weighted=True):
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

    For 10 loops, best of 3: 94.7 ms per loop
    """
    # define a box to smooth by
    box = np.ones(size)
    # defined the weights for each pixel
    if weighted:
        weights = np.where(image > 0, 1.0, 1.e-6)
    else:
        weights = np.ones_like(image)
    # new weighted image
    weightedimage = image * weights

    # need to work on each row separately
    newimage = np.zeros_like(image)
    for row in range(image.shape[0]):
        # work out the weighted image
        s_weighted_image = np.convolve(weightedimage[row], box, mode='same')
        s_weights = np.convolve(weights[row], box, mode='same')
        # apply the weighted mean for this column
        newimage[row] = s_weighted_image/s_weights
    # return new image
    return newimage


def __test_smoothed_boxmean_image(image, size, row=1000, column=1000):
    """
    This is a test code for comparison between smoothed_boxmean_image1 "manual"
    and smoothed_boxmean_image2 "convovle"

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param column: int, the column number to plot for
    :return None:
    """
    # get the new images
    image1 = smoothed_boxmean_image(image, size)
    image2 = smoothed_boxmean_image2(image, size)
    # set up the plot
    fsize = (4, 6)
    fig = plt.figure()
    frames = [plt.subplot2grid(fsize, (0, 0), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (0, 2), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (0, 4), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (2, 0), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (2, 3), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (3, 0), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (3, 3), colspan=3, rowspan=1)]
    # plot the images and image diff
    frames[0].imshow(image1)
    frames[0].set_title('Image Old method')
    frames[1].imshow(image2)
    frames[1].set_title('Image New method')
    frames[2].imshow(image1 - image2)
    frames[2].set_title('Image1 - Image2')
    # plot the column plot
    frames[3].plot(image[:, column], label='Original')
    frames[3].plot(image1[:, column], label='Old method')
    frames[3].plot(image2[:, column], label='New method')
    frames[3].legend()
    frames[3].set_title('Column {0}'.format(column))
    frames[4].plot(image1[:, column] - image2[:, column])
    frames[4].set_title('Column {0}  Image1 - Image2'.format(column))
    # plot the row plot
    frames[5].plot(image[row, :], label='Original')
    frames[5].plot(image1[row, :], label='Old method')
    frames[5].plot(image2[row, :], label='New method')
    frames[5].legend()
    frames[5].set_title('Row {0}'.format(row))
    frames[6].plot(image1[row, :] - image2[row, :])
    frames[6].set_title('Row {0}  Image1 - Image2'.format(row))
    plt.subplots_adjust(hspace=0.5)

    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    and end of orders above threshold

    :param cvalues: numpy array (1D) size = number of rows,
                    the central pixel values
    :param threshold: float, the threshold above which to find pixels as being
                      part of an order

    :return positions: numpy array (1D), size= number of rows,
                       the pixel positions in cvalues where the centers of each
                       order should be

    For 1000 loops, best of 3: 771 µs per loop
    """

    # store the positions of the orders
    positions, ends, starts = [], [], []
    # get the len of cvalues
    length = len(cvalues)
    # initialise the row number to zero
    row = 0
    # move the row number to the first row below threshold
    # (avoids first order on the edge)
    while cvalues[row] > threshold:
        row += 1
    # continue to move through rows
    while row < length:
        # if row is above threshold then we have found a start point
        if cvalues[row] > threshold:
            # save the start point
            order_start = row
            # continue to move through rows to find end (end of order defined
            # as the point at which it slips below the threshold)
            while cvalues[row] >= threshold:
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
                ly = cvalues[lx]
                # position = sum of (lx * ly) / sum of sum(ly)
                position = np.sum(lx * ly * 1.0) / np.sum(ly)
                positions.append(position)
                ends.append(order_end)
                starts.append(order_start)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return positions


def locate_order_positions2(cvalues, threshold):
    """
    Test version

    Takes the central pixel values and finds orders by looking for the start
    and end of orders above threshold

    :param cvalues: numpy array (1D) size = number of rows,
                    the central pixel values
    :param threshold: float, the threshold above which to find pixels as being
                      part of an order

    :return positions: numpy array (1D), size= number of rows,
                       the pixel positions in cvalues where the centers of each
                       order should be

    For 1000 loops, best of 3: 401 µs per loop
    """

    # define a mask of cvalues < threshold
    mask = cvalues > threshold
    # if there is an order on the leading edge set ignore it (set to False)
    row = 0
    while mask[row]:
        mask[row] = False
        row +=1
    # define a box (of width 3) to smooth the mask
    box = np.ones(3)
    # convole box with mask
    smoothmask = np.convolve(mask, box, mode='same')
    # now where the array was [True, True, True] gives a value of 3 at the
    #     center
    # now where the array was [True, True, False] or [False, True, True] or
    #     [True, False, True] gives a value of 2 at the center
    # now where the array was [False, False, True] or [True, True, False] or
    #     [False, True, False] gives a value of 1
    # now where the array was [False, False, False] gives a value of 0
    # --> we want the positions where the value==2
    raw_positions = np.where(smoothmask == 2)[0]
    # starts are the even positions
    ostarts = raw_positions[::2]
    # ends are the odd positions
    oends = raw_positions[1::2]
    # then loop around to calculate true positions
    positions = []
    for start, end in zip(ostarts, oends):
        # get x values and y values for order
        lx = np.arange(start, end+1)
        ly = cvalues[lx]
        positions.append(np.sum(lx * ly) / np.sum(ly))
    # return positions
    return positions


# =============================================================================
# End of code
# =============================================================================
