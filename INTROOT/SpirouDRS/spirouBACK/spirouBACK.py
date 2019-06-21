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
import os
from scipy.interpolate import griddata
from scipy import signal
from scipy.signal import convolve2d, medfilt
from scipy.ndimage import map_coordinates as mapc

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouDB
from SpirouDRS.spirouCore.spirouMath import IUVSpline


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
    with warnings.catch_warnings(record=True) as _:
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


def make_local_background_map(p, image):
    """
    determine the proper amplitude for the  scaling of the
    scattered-light image

    :param p:
    :param image:
    :return:
    """
    func_name = __NAME__ + '.make_local_background_map()'
    # get constants from parameter dictionary
    xsize = p['IC_BKGR_LOCAL_XSIZE']
    ysize = p['IC_BKGR_LOCAL_YSIZE']
    bthres = p['IC_BKGR_LOCAL_THRES']
    wx_ker = p['IC_BKGR_KER_WX']
    wy_ker = p['IC_BKGR_KER_WY']
    # measure local background
    scat_light = measure_local_background(p, image)

    # define the start and end of the center
    startx = (image.shape[1] // 2) - xsize
    endx = (image.shape[1] // 2) + xsize
    starty = (image.shape[0] // 2) - ysize
    endy = (image.shape[0] // 2) + ysize

    # log process
    WLOG(p, '', 'Optimizing amplitude for scattered light scaling')
    WLOG(p, '', '')

    # we extract a median order profile for the center of the image
    profile = np.nanmedian(image[:, startx:endx], axis=1)
    profile2 = np.nanmedian(scat_light[:, startx:endx], axis=1)

    # we look at the central part of the array and at the pixels
    # that are smaller than (bthres * 100)% of the peak of the orders
    keep = profile < (bthres * np.max(profile))
    # only look at those pixels in the center (y-direction)
    keep[:starty] = False
    keep[endy:] = False

    # we determine the scattered light profile for both the model and the
    # observed scatter
    observed_scatter = profile - np.mean(profile[keep])
    model_scatter = profile2 - np.mean(profile2[keep])

    # we perform a dot-product between the obsered and modelled scattered
    # light to find the amplitude of our model
    part1 = observed_scatter[keep] * model_scatter[keep]
    part2 = observed_scatter[keep] ** 2
    amp = np.sum(part1)/np.sum(part2)

    # divide the scattered light by the amp
    profile2 = profile2 / amp

    # print out some stats
    wmsg1 = 'Amplitude to be used for scattered light scaling: {0}'
    wmsg2 = 'wx = {0}, wy = {1}'
    wmsg3 = 'fractional rms = {0}'
    WLOG(p, 'info', wmsg1.format(amp))
    WLOG(p, 'info', wmsg2.format(wx_ker, wy_ker))
    WLOG(p, 'info', wmsg3.format(np.std(profile2[keep] - profile[keep])))

    if p['DRS_PLOT'] > 0:
        sPlt.local_scattered_light_plot(p, image, keep, profile, profile2, amp)


def measure_local_background(p, image):
    func_name = __NAME__ + '.measure_local_background()'
    # get constants from parameter dictionary
    wx_ker = p['IC_BKGR_KER_WX']
    wy_ker = p['IC_BKGR_KER_WY']
    sig_ker = p['IC_BKGR_KER_SIG']
    # log process
    WLOG(p, '', 'Measuring local background using 2D Gaussian Kernel')
    # construct a convolution kernel. We go from -"sig_ker" to +"sig_ker" sigma
    #   in each direction. Its important no to make the kernel too big
    #   as this slows-down the 2D convolution. Do NOT make it a -10 to
    #   +10 sigma gaussian!
    ker_sigx = int((wx_ker * sig_ker * 2) + 1)
    ker_sigy = int((wy_ker * sig_ker * 2) + 1)
    kery, kerx = np.indices([ker_sigy, ker_sigx], dtype=float)
    # this normalises kernal x and y between +1 and -1
    kery = kery - np.mean(kery)
    kerx = kerx - np.mean(kerx)
    # calculate 2D gaussian kernel
    ker = np.exp(-0.5 * ((kerx / wx_ker)**2 + (kery / wy_ker)**2))
    # we normalize the integral of the kernel to 1 so that the AMP factor
    #    corresponds to the fraction of scattered light and therefore has a
    #    physical meaning.
    ker = ker / np.sum(ker)

    # we need to remove NaNs from image
    WLOG(p, '', '\tPadding NaNs')
    image1 = spirouCore.spirouMath.nanpad(image)

    # we determine the scattered light image by convolving our image by
    #    the kernel
    WLOG(p, '', '\tCalculating 2D convolution')
    scattered_light = convolve2d(image1, ker, mode='same')
    # returned the scattered light
    return scattered_light


def measure_background_from_map(p, image, header):
    func_name = __NAME__ + '.measure_background_from_map()'
    # get constants from parameter dictionary
    width = p['IC_BKGR_BOXSIZE']
    amp_ker = p['IC_BKGR_KER_AMP']
    # ------------------------------------------------------------------------
    # measure local background
    scattered_light = measure_local_background(p, image)
    # we extract a median order profile for the center of the image
    local_background_correction = scattered_light / amp_ker
    # correct the image for local background
    image1 = image - local_background_correction

    # -------------------------------------------------------------------------
    # get badpixmask
    p, bmap, bhdr = spirouImage.GetBackgroundMap(p, header)
    # create mask from badpixmask
    bmap = np.array(bmap, dtype=bool)
    # copy image
    image2 = np.array(image1)
    # set to NAN all "illuminated" (non-background) pixels
    image2[~bmap] = np.nan
    # -------------------------------------------------------------------------
    # create the box centers
    # we construct a binned-down version of the full image with the estimate
    # of the background for each x+y "center". This image will be up-scaled to
    # the size of the full science image and subtracted

    # x and y centers for each background calculation
    xc = np.arange(width, image2.shape[0], width)
    yc = np.arange(width, image2.shape[1], width)
    # background map (binned-down for now)
    background_image = np.zeros((len(xc), len(yc)))
    # loop around all boxes with centers xc and yc
    # and find pixels within a given widths
    # around these centers in the full image
    for i_it in range(len(xc)):
        for j_it in range(len(yc)):
            xci, yci = xc[i_it], yc[j_it]
            # get the pixels for this box
            subframe = image2[xci - width:xci + width, yci - width:yci + width]
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
    imageshape = image2.shape
    # get fractional positions of the full image
    indices = np.indices(imageshape)
    fypix = indices[0]/imageshape[0]
    fxpix = indices[1]/imageshape[1]
    # scalge fraction positions to size of background image
    sypix = (gridshape[0]-1) * fypix
    sxpix = (gridshape[1]-1) * fxpix
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
    dimages = [data1, image, image1, image2, local_background_correction,
               background_image_full, background_image]
    # construct hdicts
    hdict = spirouImage.CopyOriginalKeys(header)
    drsname = ['EXTDESC', None, 'Extension description']
    hdict1 = spirouImage.AddKey(p, hdict, drsname, value='Corrected')
    hdict2 = spirouImage.AddKey(p, hdict, drsname, value='Original')
    hdict3 = spirouImage.AddKey(p, hdict, drsname, value='Locally corrected')
    hdict4 = spirouImage.AddKey(p, hdict, drsname, value='LC NaN filled')
    hdict5 = spirouImage.AddKey(p, hdict, drsname, value='Local Background')
    hdict6 = spirouImage.AddKey(p, hdict, drsname, value='Global Background')
    hdict7 = spirouImage.AddKey(p, hdict, drsname,
                                value='Global Background Binned')
    dheaders = [hdict1, hdict2, hdict3, hdict4, hdict5, hdict6, hdict7]
    # write debug to file
    _ = spirouImage.WriteImageMulti(p, debug_background, dimages,
                                    hdicts=dheaders)
    # ----------------------------------------------------------------------
    return p, background_image_full


def measure_background_flatfield(p, image, header):
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
    hdict = spirouImage.CopyOriginalKeys(header)
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


def measure_background_flatfield_old(p, image, header, badpixmask):

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


def correction_thermal(p, image, hdr, mode, fiber, flat=None):
    func_name = __NAME__ + '.correction_thermal()'
    # log progress
    wmsg = 'Correcting for Thermal Background (mode = {0})'
    WLOG(p, '', wmsg.format(mode))
    # decide on how to correct
    if mode == 1:
        return correction_thermal1(p, image, hdr, fiber, flat)
    elif mode == 2:
        return correction_thermal2(p, image, hdr, fiber, flat)
    else:
        wmsg = 'Mode = {0} not supported. Correction skipped.'
        WLOG(p, 'warning', wmsg.format(mode))

        # set tapas file used
        outfile = 'THERMALFILE_{0}'.format(fiber)
        p[outfile] = 'None'
        p.set_source(outfile, func_name)
        # return p and image
        return p, image


def correction_thermal1(p, image, hdr, fiber, flat=None):
    # get constants from p
    threshold_tapas_bgnd = p['THERMAL_THRES_TAPAS_BGND']
    bgnd_filter_width = p['THERMAL_BGND_FILTER_WID']
    th_red_limit = p['THERMAL_RED_LIMIT']
    torder = p['THERMAL_ORDER']

    # ----------------------------------------------------------------------
    # Get master wavelength grid
    masterwave = spirouDB.GetDatabaseMasterWave(p)
    # Force A and B to AB solution
    if fiber in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = fiber
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=masterwave, fiber=wave_fiber,
                                       return_wavemap=True, quiet=True)
    _, wave, _ = mout
    # ----------------------------------------------------------------------
    # get the thermal extraction for this fiber
    p, thermal = spirouImage.GetThermal(p, hdr, fiber=fiber)
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if np.nansum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return p, image
    # ----------------------------------------------------------------------
    # load tapas
    p, tapas = spirouImage.GetTapas(p, hdr)
    wtapas, ttapas = tapas['wavelength'], tapas['trans_combined']
    # ----------------------------------------------------------------------
    # splining tapas onto the order 49 wavelength grid
    sptapas = IUVSpline(wtapas, ttapas)

    # binary mask to be saved; this corresponds to the domain for which
    #    transmission is basically zero and we can safely use the domain
    #    to scale the thermal background. We only do this for wavelength smaller
    #    than "THERMAL_TAPAS_RED_LIMIT" nm as this is the red end of the
    #    TAPAS domain
    # set torder mask all to False initially
    torder_mask = np.zeros_like(wave[torder, :], dtype=bool)
    # get the wave mask
    wavemask = wave[torder] < th_red_limit
    # get the tapas data for these wavelengths
    torder_tapas = sptapas(wave[torder, wavemask])
    # find those pixels lower than threshold in tapas
    torder_mask[wavemask] =  torder_tapas < threshold_tapas_bgnd

    # median filter the thermal (loop around orders)
    for order_num in range(thermal.shape[0]):
        thermal[order_num] = medfilt(thermal[order_num], bgnd_filter_width)

    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, torder_mask]
    image_torder = image[torder, torder_mask]
    ratio = np.nanmedian(thermal_torder / image_torder)
    # scale thermal by ratio
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot debug plot
    if p['DRS_DEBUG'] > 0 and p['DRS_PLOT'] > 0:
        data = [wave, image, thermal, torder, torder_mask]
        sPlt.thermal_background_debug_plot(p, *data, fiber=fiber)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # return p and corrected image
    return p, corrected_image


def correction_thermal2(p, image, hdr, fiber, flat=None):
    func_name = __NAME__ + '.correction_thermal2()'
    # get parameters from p
    bgnd_filter_width = p['THERMAL_BGND_FILTER_WID']
    envelope_percent = p['THERMAL_ENVELOPE_PERCENTILE']
    torder = p['THERMAL_ORDER']
    th_red_limit = p['THERMAL_RED_LIMIT']
    th_blue_limit = p['THERMAL_RED_LIMIT']
    # get the shape
    dim1, dim2 = image.shape
    # ----------------------------------------------------------------------
    # Get master wavelength grid
    masterwave = spirouDB.GetDatabaseMasterWave(p)
    # Force A and B to AB solution
    if fiber in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = fiber
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=masterwave, fiber=wave_fiber,
                                       return_wavemap=True, quiet=True)
    _, wave, _ = mout
    # ----------------------------------------------------------------------
    # get the thermal extraction for this fiber
    p, thermal = spirouImage.GetThermal(p, hdr, fiber=fiber)
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if np.sum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return p, image
    # ----------------------------------------------------------------------
    # set up an envelope to measure thermal background in image
    envelope = np.zeros(dim2)
    # loop around all pixels
    for x_it in range(dim2):
        # define start and end points
        start = x_it - bgnd_filter_width // 2
        end = x_it + bgnd_filter_width // 2
        # deal with out of bounds
        if start < 0:
            start = 0
        if end > dim2 -1:
            end = dim2 - 1
        # get the box for this pixel
        imagebox = image[torder, start:end]
        # get the envelope
        envelope[x_it] = np.nanpercentile(imagebox, envelope_percent)
    # ----------------------------------------------------------------------
    # median filter the thermal (loop around orders)
    for order_num in range(dim1):
        thermal[order_num] = medfilt(thermal[order_num], bgnd_filter_width)
    # ----------------------------------------------------------------------
    # only keep wavelength in range of thermal limits
    wavemask = (wave[torder] > th_blue_limit) & (wave[torder] < th_red_limit)
    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, wavemask]
    envelope_torder = envelope[wavemask]
    ratio = np.nanmedian(thermal_torder / envelope_torder)
    # scale thermal by ratio
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot debug plot
    if p['DRS_DEBUG'] > 0 and p['DRS_PLOT'] > 0:
        data = [wave, image, thermal, torder, wavemask]
        sPlt.thermal_background_debug_plot(p, *data, fiber=fiber)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # return p and corrected image
    return p, corrected_image


# =============================================================================
# End of code
# =============================================================================
