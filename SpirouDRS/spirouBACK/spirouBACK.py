#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-10 at 14:33

@author: cook



Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS.spirouCore import spirouPlot as sPlt

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouBACK.py'
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# get the logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def measure_background_flatfield(p, image):

    # get constants
    size = p['IC_BKGR_WINDOW']
    gain = p['GAIN']
    sigdet = p['SIGDET']
    # set the background image to zeros
    background = np.zeros_like(image)
    # create the box centers
    xc = np.arange(size, image.shape[0], 2*size)
    yc = np.arange(size, image.shape[1], 2*size)
    # min level box
    minlevel = np.zeros((len(xc), len(yc)))
    # loop around all boxes with centers xc and yc
    for i_it in range(len(xc)):
        for j_it in range(len(yc)):
            xci, yci = xc[i_it], yc[i_it]
            # get the pixels for this box
            subframe = image[xci-size:xci+size,yci-size:yci+size].ravel()
            # get the (2*size)th minimum pixel
            minlevel[i_it, j_it] = np.sort(subframe)[2 * size]

    # loop around columns
    # TODO: background spline interpolation - need to understand interpol.c

    return background, xc, yc, minlevel


def measure_background_and_get_central_pixels(pp, loc, image):
    """
    Takes the image and measure the background

    :param pp: dictionary, parameter dictionary
    :param loc: dictionary, localisation parameter dictionary
    :param image: numpy array (2D), the image

    :return ycc: the normalised values the central pixels
    """
    # clip the data - start with the ic_offset row and only
    # deal with the central column column=ic_cent_col
    y = image[pp['IC_OFFSET']:, pp['IC_CENT_COL']]
    # measure min max of box smoothed central col
    miny, maxy, max_signal, diff_maxmin = measure_min_max(pp, y)
    # normalised the central pixel values above the minimum amplitude
    #   zero by miny and normalise by (maxy - miny)
    #   Set all values below ic_min_amplitude to zero
    max_amp = pp['IC_MIN_AMPLITUDE']
    ycc = np.where(diff_maxmin > max_amp, (y - miny)/diff_maxmin, 0)
    # get the normalised minimum values for those rows above threshold
    #   i.e. good background measurements
    normed_miny = miny/diff_maxmin
    goodback = np.compress(ycc > pp['IC_LOCSEUIL'], normed_miny)
    # measure the mean good background as a percentage
    # (goodback and ycc are between 0 and 1)
    mean_backgrd = np.mean(goodback) * 100
    # Log the maximum signal and the mean background
    WLOG('info', pp['log_opt'], ('Maximum flux/pixel in the spectrum: '
                                 '{0:.1f} [e-]').format(max_signal))
    WLOG('info', pp['log_opt'], ('Average background level: '
                                 '{0:.2f} [%]').format(mean_backgrd))
    # if in debug mode plot y, miny and maxy else just plot y
    if pp['IC_DEBUG'] and pp['DRS_PLOT']:
        sPlt.locplot_y_miny_maxy(y, miny, maxy)
    if pp['DRS_PLOT']:
        sPlt.locplot_y_miny_maxy(y)

    # set function name (for source)
    __funcname__ = '/measure_background_and_get_central_pixels()'
    # Add to loc
    loc['ycc'] = ycc
    loc.set_source('ycc', __NAME__ + __funcname__)
    loc['mean_backgrd'] = mean_backgrd
    loc.set_source('mean_backgrd', __NAME__ + __funcname__)
    loc['max_signal'] = max_signal
    loc.set_source('max_signal', __NAME__ + __funcname__)
    # return the localisation dictionary
    return loc


def measure_min_max(pp, y):
    # Get the box-smoothed min and max for the central column
    miny, maxy = measure_box_min_max(y, pp['IC_LOCNBPIX'])
    # record the maximum signal in the central column
    # QUESTION: Why the third biggest?
    max_signal = np.sort(y)[-3]
    # get the difference between max and min pixel values
    diff_maxmin = maxy - miny
    # return values
    return miny, maxy, max_signal, diff_maxmin



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
