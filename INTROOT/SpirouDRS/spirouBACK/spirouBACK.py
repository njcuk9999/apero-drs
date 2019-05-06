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
from scipy.interpolate import griddata
from scipy import signal
from scipy.signal import convolve2d
from scipy.ndimage import map_coordinates as mapc

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage

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
# Get plotting functions
sPlt = spirouCore.sPlt


# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def make_background_map(p, image, badpixmask):

    # get constants
    width = p['IC_BKGR_BOXSIZE']
    percent = p['IC_BKGR_PERCENT']
    csize = p['IC_BKGR_MASK_CONVOLVE_SIZE']
    nbad = p['IC_BKGR_N_BAD_NEIGHBOURS']

    # set image bad pixels to NaN
    image0 = np.array(image)
    badmask = np.array(badpixmask, dtype=bool)
    image0[badmask] = np.nan

    # image that will contain the background estimate
    backest = np.zeros_like(image0)

    # we slice the image in ribbons of width "width".
    # The slicing is done in the cross-dispersion direction, so we
    # can simply take a median along the "fast" dispersion to find the
    # order profile. We pick width to be small enough for the orders not
    # to show a significant curvature within w pixels
    for x_it in range(0, image0.shape[1], width):
        # ribbon to find the order profile
        ribbon = np.nanmedian(image0[:, x_it:x_it + width], axis=1)

        for y_it in range(image0.shape[0]):
            # we perform a running Nth percentile filter along the
            # order profile. The box of the filter is w. Note that it could
            # differ in princile from w, its just the same for the sake of
            # simplicity.
            ystart = y_it - width // 2
            yend = y_it + width // 2
            if ystart < 0:
                ystart = 0
            if yend > image0.shape[0] - 1:
                yend = image0.shape[0] - 1
            # background estimate
            backest_pix = np.nanpercentile(ribbon[ystart:yend], percent)
            backest[y_it, x_it: x_it + width] = backest_pix
    # the mask is the area that is below then Nth percentile threshold
    backmask = np.array(image0 < backest, dtype=float)
    # we take advantage of the order geometry and for that the "dark"
    # region of the array be continuous in the "fast" dispersion axis
    nribbon = convolve2d(backmask, np.ones([1, csize]), mode='same')
    # we remove from the binary mask all isolated (within 1x7 ribbon)
    # dark pixels
    backmask[nribbon == 1] = 0
    # If a pixel has 3 or more "dark" neighbours, we consider it dark
    # regardless of its initial value
    backmask[nribbon >= nbad] = 1

    # return the background mask
    return backmask


def measure_background_from_map(p, image, header, comments):

    func_name = __NAME__ + '.measure_background_from_map()'

    # get constants
    width = p['IC_BKGR_BOXSIZE']

    # get badpixmask
    bmap, bhdr, badfile = spirouImage.GetBackgroundMap(p, header)
    # create mask from badpixmask
    mask = np.array(bmap, dtype=bool)
    # copy image
    image1 = np.array(image)
    # set to NAN all "illuminated" (non-background) pixels
    image1[~bmap] = np.nan

    # create the box centers
    # we construct a binned-down version of the full image with the estimate
    # of the background for each x+y "center". This image will be up-scaled to
    # the size of the full science image and subtracted

    # x and y centers for each background calculation
    xc = np.arange(width, image1.shape[0], width)
    yc = np.arange(width, image1.shape[1], width)
    # background map (binned-down for now)
    background_image = np.zeros((len(xc), len(yc)))
    # loop around all boxes with centers xc and yc
    # and find pixels within a given widths
    # around these centers in the full image
    for i_it in range(len(xc)):
        for j_it in range(len(yc)):
            xci, yci = xc[i_it], yc[j_it]
            # get the pixels for this box
            subframe = image1[xci - width:xci + width,
                       yci - width:yci + width]
            subframe = subframe.ravel()
            # get the (2*size)th minimum pixel
            with warnings.catch_warnings(record=True) as _:
                # do not use the nanpercentile, just a median
                # as we masked non-background pixels with NaNs
                value = np.nanmedian(subframe)

            if np.isfinite(value):
                background_image[i_it, j_it] = value
            else:
                background_image[i_it, j_it] = 0.0

    # define a mapping grid from size of background_image (image1[0]/width) by
    #    (image1[1]/width)
    # get shapes
    gridshape = background_image.shape
    imageshape = image1.shape
    # get fractional positions of the full image
    indices = np.indices(imageshape)
    fypix = indices[0]/imageshape[0]
    fxpix = indices[1]/imageshape[1]
    # scalge fraction positions to size of background image
    sypix = gridshape[0] * fypix
    sxpix = gridshape[1] * fxpix
    # coords for mapping
    coords = np.array([sypix, sxpix])
    # expand image onto the grid that matches the size of the input image
    background_image_full = mapc(background_image, coords,
                                 order=2, cval=np.nan, output=float,
                                 mode='constant')

    # ----------------------------------------------------------------------
    # Produce DEBUG plot
    # ----------------------------------------------------------------------
    data1 = image - background_image_full
    # construct debug background file name
    debug_background, tag = spirouConfig.Constants.BACKGROUND_CORRECT_FILE(p)
    # construct images
    dimages = [data1, image1, background_image_full, background_image]
    # construct hdicts
    hdict = spirouImage.CopyOriginalKeys(header, comments)
    drsname = ['DRSNAME', None, 'Extension description']
    hdict1 = spirouImage.AddKey(p, hdict, drsname, value='Corrected')
    hdict2 = spirouImage.AddKey(p, hdict, drsname, value='Original')
    hdict3 = spirouImage.AddKey(p, hdict, drsname, value='Background Full')
    hdict4 = spirouImage.AddKey(p, hdict, drsname, value='Background Binned')
    dheaders = [hdict1, hdict2, hdict3, hdict4]
    # write debug to file
    spirouImage.WriteImageMulti(p, debug_background, dimages, hdicts=dheaders)
    # ----------------------------------------------------------------------
    return


def measure_background_flatfield(p, image, header, comments):
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
    # func_name = __NAME__ + '.measure_background_flatfield()'

    image1 = np.array(image)
    image_med = signal.medfilt(image1, [3, 3])

    # get constants
    size = p['IC_BKGR_WINDOW']
    percent = p['IC_BKGR_PERCENT']
    # create the box centers
    xc = np.arange(size, image_med.shape[0], 2 * size)
    yc = np.arange(size, image_med.shape[1], 2 * size)
    # min level box
    minlevel = np.zeros((len(xc), len(yc)))
    # loop around all boxes with centers xc and yc
    for i_it in range(len(xc)):
        for j_it in range(len(yc)):
            xci, yci = xc[i_it], yc[j_it]
            # get the pixels for this box
            subframe = image_med[xci - size:xci + size,
                                 yci - size:yci + size].ravel()
            # get the (2*size)th minimum pixel
            with warnings.catch_warnings(record=True) as _:
                value = np.nanpercentile(subframe, percent)

            if np.isfinite(value):
                minlevel[i_it, j_it] = value
            else:
                minlevel[i_it, j_it] = 0.0

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    gridx1, gridy1 = np.mgrid[size:image_med.shape[0]:2 * size,
                              size:image_med.shape[1]:2 * size]
    gridx2, gridy2 = np.indices(image_med.shape)

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    minlevel2 = np.zeros((minlevel.shape[0] + 2, minlevel.shape[1] + 2),
                         dtype=float)
    minlevel2[1:-1, 1:-1] = minlevel
    minlevel2[0, 1:-1] = minlevel[0]
    minlevel2[-1, 1:-1] = minlevel[-1]
    minlevel2[1:-1, 0] = minlevel[:, 0]
    minlevel2[1:-1, -1] = minlevel[:, -1]
    minlevel2[0, 0] = minlevel[0, 0]
    minlevel2[-1, -1] = minlevel[-1, -1]
    minlevel2[0, -1] = minlevel[0, -1]
    minlevel2[-1, 0] = minlevel[-1, 0]

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    gridx1c = np.zeros((gridx1.shape[0] + 2, gridx1.shape[1] + 2), dtype=float)
    gridx1c[1:-1, 1:-1] = gridx1
    gridx1c[0, :] = 0
    gridx1c[-1, :] = np.shape(image_med)[0]
    gridx1c[:, 0] = gridx1c[:, 1]
    gridx1c[:, -1] = gridx1c[:, -2]

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    gridy1c = np.zeros((gridy1.shape[0] + 2, gridy1.shape[1] + 2), dtype=float)
    gridy1c[1:-1, 1:-1] = gridy1
    gridy1c[:, 0] = 0
    gridy1c[:, -1] = np.shape(image_med)[1]
    gridy1c[0, :] = gridy1c[1, :]
    gridy1c[-1, :] = gridy1c[-2, :]

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    points = np.array([gridx1c.ravel(), gridy1c.ravel()]).T
    background = griddata(points, minlevel2.ravel(), (gridx2, gridy2),
                          method='cubic')

    # ----------------------------------------------------------------------
    # Produce DEBUG plot
    # ----------------------------------------------------------------------
    data1 = image - background
    # construct debug background file name
    debug_background, tag = spirouConfig.Constants.BACKGROUND_CORRECT_FILE(p)
    # construct images
    dimages = [data1, background, image1, image_med]
    # construct hdicts
    hdict = spirouImage.CopyOriginalKeys(header, comments)
    drsname = ['DRSNAME', None, 'Extension description']
    hdict1 = spirouImage.AddKey(p, hdict, drsname, value='Corrected')
    hdict2 = spirouImage.AddKey(p, hdict, drsname, value='Background')
    hdict3 = spirouImage.AddKey(p, hdict, drsname, value='Original')
    hdict4 = spirouImage.AddKey(p, hdict, drsname, value='Median')
    dheaders = [hdict1, hdict2, hdict3, hdict4]
    # write debug to file
    spirouImage.WriteImageMulti(p, debug_background, dimages, hdicts=dheaders)
    # ----------------------------------------------------------------------


    # return background, xc, yc and minlevel
    return background, gridx1c, gridy1c, minlevel2


def measure_background_flatfield_old(p, image, header, comments, badpixmask):

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
    # func_name = __NAME__ + '.measure_background_flatfield()'

    # get constants
    size = p['IC_BKGR_WINDOW']
    percent = p['IC_BKGR_PERCENT']
    # create the box centers
    xc = np.arange(size, image.shape[0], 2 * size)
    yc = np.arange(size, image.shape[1], 2 * size)
    # min level box
    minlevel = np.zeros((len(xc), len(yc)))
    # loop around all boxes with centers xc and yc
    for i_it in range(len(xc)):
        for j_it in range(len(yc)):
            xci, yci = xc[i_it], yc[j_it]
            # get the pixels for this box
            subframe = image[xci - size:xci + size,
                             yci - size:yci + size].ravel()
            # get the (2*size)th minimum pixel
            mask = subframe > 0
            maskedsubframe = subframe[mask]
            if len(maskedsubframe) > 0:
                minlevel[i_it, j_it] = np.max(
                    [np.nanpercentile(maskedsubframe, percent), 0])
            else:
                minlevel[i_it, j_it] = 0

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    gridx1, gridy1 = np.mgrid[size:image.shape[0]:2 * size,
                              size:image.shape[1]:2 * size]
    gridx2, gridy2 = np.indices(image.shape)

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    minlevel2 = np.zeros((minlevel.shape[0] + 2, minlevel.shape[1] + 2),
                         dtype=float)
    minlevel2[1:-1, 1:-1] = minlevel
    minlevel2[0, 1:-1] = minlevel[0]
    minlevel2[-1, 1:-1] = minlevel[-1]
    minlevel2[1:-1, 0] = minlevel[:, 0]
    minlevel2[1:-1, -1] = minlevel[:, -1]
    minlevel2[0, 0] = minlevel[0, 0]
    minlevel2[-1, -1] = minlevel[-1, -1]
    minlevel2[0, -1] = minlevel[0, -1]
    minlevel2[-1, 0] = minlevel[-1, 0]

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    gridx1c = np.zeros((gridx1.shape[0] + 2, gridx1.shape[1] + 2), dtype=float)
    gridx1c[1:-1, 1:-1] = gridx1
    gridx1c[0, :] = 0
    gridx1c[-1, :] = np.shape(image)[0]
    gridx1c[:, 0] = gridx1c[:, 1]
    gridx1c[:, -1] = gridx1c[:, -2]

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    gridy1c = np.zeros((gridy1.shape[0] + 2, gridy1.shape[1] + 2), dtype=float)
    gridy1c[1:-1, 1:-1] = gridy1
    gridy1c[:, 0] = 0
    gridy1c[:, -1] = np.shape(image)[1]
    gridy1c[0, :] = gridy1c[1, :]
    gridy1c[-1, :] = gridy1c[-2, :]

    # TODO: FIX PROBLEMS: SECTION NEEDS COMMENTING!!!
    points = np.array([gridx1c.ravel(), gridy1c.ravel()]).T
    background = griddata(points, minlevel2.ravel(), (gridx2, gridy2),
                          method='linear')

    # return background, xc, yc and minlevel
    return background, gridx1c, gridy1c, minlevel2


def measure_background_and_get_central_pixels(p, loc, image):
    """
    Takes the image and measure the background

    :param p: parameter dictionary, ParamDict containing constants
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
    y = image[p['IC_OFFSET']:, p['IC_CENT_COL']]
    # measure min max of box smoothed central col
    miny, maxy, max_signal, diff_maxmin = measure_min_max(p, y)
    # normalised the central pixel values above the minimum amplitude
    #   zero by miny and normalise by (maxy - miny)
    #   Set all values below ic_min_amplitude to zero
    max_amp = p['IC_MIN_AMPLITUDE']
    ycc = np.where(diff_maxmin > max_amp, (y - miny) / diff_maxmin, 0)
    # get the normalised minimum values for those rows above threshold
    #   i.e. good background measurements
    normed_miny = miny / diff_maxmin
    goodback = np.compress(ycc > p['IC_LOCSEUIL'], normed_miny)
    # measure the mean good background as a percentage
    # (goodback and ycc are between 0 and 1)
    mean_backgrd = np.mean(goodback) * 100
    # Log the maximum signal and the mean background
    wmsg = 'Maximum flux/pixel in the spectrum: {0:.1f} [e-]'
    WLOG(p, 'info', wmsg.format(max_signal))
    wmsg = 'Average background level: {0:.2f} [%]'
    WLOG(p, 'info', wmsg.format(mean_backgrd))
    # plot y, miny and maxy
    if p['DRS_PLOT'] > 0:
        sPlt.locplot_y_miny_maxy(p, y, miny, maxy)

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
    max_signal = np.nanpercentile(y, 95)
    # get the difference between max and min pixel values
    diff_maxmin = maxy - miny
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

# =============================================================================
# End of code
# =============================================================================
