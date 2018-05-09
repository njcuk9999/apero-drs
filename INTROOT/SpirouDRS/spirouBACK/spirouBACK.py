#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The spirou background module

Created on 2017-11-10 at 14:33

@author: cook

"""
from __future__ import division
import numpy as np
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore


# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouBACK.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
WARNGLOG = spirouCore.warnlog
# Get plotting functions
sPlt = spirouCore.sPlt
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def measure_background_flatfield(p, image):
    """
    Measures the background of a flat field image - currently does not work
    as need an interpolation function (see code)

    :param p: parameter dictionary, ParamDict containing constants

            Must contain at least:
                IC_BKGR_WINDOW: int, Half-size of window for background
                                measurements
                GAIN: float, the gain of the image (from HEADER)
                SIGDET: float, the read noise of the image (from HEADER)
                log_opt: string, log option, normally the program name

    :param image: numpy array (2D), the image to measure the background of

    :return background: numpy array (2D), the background image (currently all
                        zeros) as background not implemented
    :return xc: numpy array (1D), the box centers (x positions) used to create
                the background image
    :return yc: numpy array (1D), the box centers (y positions) used to create
                the background image
    :return minlevel: numpy array (2D), the 2 * size -th minimum pixel value
                      of each box for each pixel in the image
    """
    func_name = __NAME__ + '.measure_background_flatfield()'

    # get constants
    size = p['IC_BKGR_WINDOW']
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
            subframe = image[xci-size:xci+size, yci-size:yci+size].ravel()
            # get the (2*size)th minimum pixel
            minlevel[i_it, j_it] = np.sort(subframe)[2 * size]

    # loop around columns
    # TODO: background spline interpolation - need to understand interpol.c
    # warning about not background code
    wmsg = 'No interpolation done in {0} (FUNCTION INCOMPLETE)'
    WLOG('warning', p['LOG_OPT'], wmsg.format(func_name))

    # return background, xc, yc and minlevel
    return background, xc, yc, minlevel


def measure_background_and_get_central_pixels(pp, loc, image):
    """
    Takes the image and measure the background

    :param pp: parameter dictionary, ParamDict containing constants
            Must contain at least:
                IC_OFFSET: int, row number of image to start processing at
                IC_CENT_COL: int, Definition of the central column
                IC_MIN_AMPLITUDE: int, Minimum amplitude to accept (in e-)
                IC_LOCSEUIL: float, Normalised amplitude threshold to accept
                             pixels for background calculation
                log_opt: string, log option, normally the program name
                DRS_DEBUG: int, Whether to run in debug mode
                                0: no debug
                                1: basic debugging on errors
                                2: recipes specific (plots and some code runs)
                DRS_PLOT: bool, Whether to plot (True to plot)

    :param loc: parameter dictionary, ParamDict containing data

    :param image: numpy array (2D), the image

    :return ycc: the normalised values the central pixels

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ycc: numpy array (1D), normalized central column of pixels
                mean_backgrd: float, 100 times the mean of the good background
                              pixels
                max_signal: float, the maximum value of the central column of
                            pixels
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
    WLOG('info', pp['LOG_OPT'], ('Maximum flux/pixel in the spectrum: '
                                 '{0:.1f} [e-]').format(max_signal))
    WLOG('info', pp['LOG_OPT'], ('Average background level: '
                                 '{0:.2f} [%]').format(mean_backgrd))
    # if in debug mode plot y, miny and maxy else just plot y
    if pp['DRS_DEBUG'] == 0 and pp['DRS_PLOT']:
        sPlt.locplot_y_miny_maxy(y, miny, maxy)
    if pp['DRS_PLOT']:
        sPlt.locplot_y_miny_maxy(y)

    # set function name (for source)
    func_name = __NAME__ + '.measure_background_and_get_central_pixels()'
    # Add to loc
    loc['YCC'] = ycc
    loc['MEAN_BACKGRD'] = mean_backgrd
    loc['MAX_SIGNAL'] = max_signal
    # set source
    loc.set_sources(['ycc', 'mean_backgrd', 'max_signal'], func_name)
    # return the localisation dictionary
    return loc


def measure_min_max(pp, y):
    """
    Measure the minimum, maximum peak to peak values in y, the third biggest
    pixel in y and the peak-to-peak difference between the minimum and
    maximum values in y

    :param pp: parameter dictionary, ParamDict containing constants
                Must contain at least:
                    IC_LOCNBPIX: int, Half spacing between orders

    :param y: numpy array (1D), the central column pixel values

    :return miny: numpy array (1D length = len(y)), the values
                  for minimum pixel defined by a box of pixel-size to
                  pixel+size for all columns
    :return maxy: numpy array (1D length = len(y)), the values
                  for maximum pixel defined by a box of pixel-size to
                  pixel+size for all columns
    :return max_signal: float, the pixel value of the third biggest value
                        in y
    :return diff_maxmin: float, the difference between maxy and miny
    """
    funcname = __NAME__ + '.measure_min_max()'
    # Get the box-smoothed min and max for the central column
    miny, maxy = measure_box_min_max(y, pp['IC_LOCNBPIX'])
    # record the maximum signal in the central column
    # QUESTION: Why the third biggest?
    max_signal = np.sort(y)[-3]
    # get the difference between max and min pixel values
    with warnings.catch_warnings(record=True) as w:
        diff_maxmin = maxy - miny
    # log any catch warnings
    WARNGLOG(w, funcname)
    # return values
    return miny, maxy, max_signal, diff_maxmin


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
        min_image[it] = np.min(y[it-size:it+size])
        max_image[it] = np.max(y[it-size:it+size])

    # deal with leading edge --> set to value at size
    min_image[0:size] = min_image[size]
    max_image[0:size] = max_image[size]
    # deal with trailing edge --> set to value at (image.shape[0]-size-1)
    min_image[ny-size:] = min_image[ny-size-1]
    max_image[ny-size:] = max_image[ny-size-1]
    # return arrays for minimum and maximum (box smoothed)
    return min_image, max_image


# =============================================================================
# End of code
# =============================================================================
