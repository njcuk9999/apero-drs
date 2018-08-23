#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou Image processing module

Created on 2017-10-12 at 17:47

@author: cook

Import rules: Not spirouLOCOR
"""
from __future__ import division
import numpy as np
import os
import glob
import warnings
import scipy
from scipy.ndimage import filters, median_filter
from scipy.interpolate import InterpolatedUnivariateSpline as InterpUSpline
from scipy.interpolate import griddata

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from . import spirouFITS
from . import spirouTable

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouImage.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# -----------------------------------------------------------------------------


# =============================================================================
# Define Image modification function
# =============================================================================
def resize(image, x=None, y=None, xlow=0, xhigh=None, ylow=0, yhigh=None,
           getshape=True):
    """
    Resize an image based on a pixel values

    :param image: numpy array (2D), the image
    :param x: None or numpy array (1D), the list of x pixels
    :param y: None or numpy array (1D), the list of y pixels
    :param xlow: int, x pixel value (x, y) in the bottom left corner,
                 default = 0
    :param xhigh:  int, x pixel value (x, y) in the top right corner,
                 if None default is image.shape(1)
    :param ylow: int, y pixel value (x, y) in the bottom left corner,
                 default = 0
    :param yhigh: int, y pixel value (x, y) in the top right corner,
                 if None default is image.shape(0)
    :param getshape: bool, if True returns shape of newimage with newimage

    if getshape = True
    :return newimage: numpy array (2D), the new resized image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]

    if getshape = False
    :return newimage: numpy array (2D), the new resized image
    """
    func_name = __NAME__ + '.resize()'
    # Deal with no low/high values
    if xhigh is None:
        xhigh = image.shape(1)
    if yhigh is None:
        yhigh = image.shape(0)
    # if our x pixels and y pixels to keep are defined then use them to
    # construct the new image
    if x is not None and y is not None:
        pass
    # else define them from low/high values
    else:
        # deal with xlow > xhigh
        if xlow > xhigh:
            x = np.arange(xhigh + 1, xlow + 1)[::-1]
        elif xlow == xhigh:
            emsg1 = '"xlow" and "xhigh" cannot have the same values'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
        else:
            x = np.arange(xlow, xhigh)
        # deal with ylow > yhigh
        if ylow > yhigh:
            y = np.arange(yhigh + 1, ylow + 1)[::-1]
        elif ylow == yhigh:
            emsg1 = '"ylow" and "yhigh" cannot have the same values'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
        else:
            y = np.arange(ylow, yhigh)
    # construct the new image (if one can't raise error)
    try:
        newimage = np.take(np.take(image, x, axis=1), y, axis=0)
    except Exception as e:
        eargs1 = [xlow, xhigh, ylow, yhigh]
        emsg1 = 'Cannot resize "image" to ({0}-{1} by {2}-{3})'.format(*eargs1)
        emsg2 = '    Error {0}: {1}'.format(type(e), e)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2, emsg3])
        newimage = None

    # if getshape is True return newimage, newimage.shape[0], newimage.shape[1]
    if getshape:
        return newimage, newimage.shape[0], newimage.shape[1]
    else:
        # return new image
        return newimage


def rotate(image, rotation):
    """
    Rotates the image by rotation

    :param image: numpy array (2D), the image to rotate
    :param rotation: float, the rotational angle in degrees (counter-clockwise)
                     must be a multiple of +/- 90 degrees

    :return newimage:  numpy array (2D), the rotated image
    """
    rotation = int(rotation // 90)
    newimage = np.rot90(image, rotation)
    return newimage


def flip_image(image, fliprows=True, flipcols=True):
    """
    Flips the image in the x and/or the y direction

    :param image: numpy array (2D), the image
    :param fliprows: bool, if True reverses row order (axis = 0)
    :param flipcols: bool, if True reverses column order (axis = 1)

    :return newimage: numpy array (2D), the flipped image
    """
    func_name = __NAME__ + '.flip_image()'
    # raise error if image is not 2D
    if len(image.shape) < 2:
        emsg1 = 'Image must has at least two dimensions, shape = {0}'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1.format(image.shape), emsg2])
    # flip both dimensions
    if fliprows and flipcols:
        return image[::-1, ::-1]
    # flip first dimension
    elif fliprows:
        return image[::-1, :]
    # flip second dimension
    elif flipcols:
        return image[:, ::-1]
    # if both false just return image (no operation done)
    else:
        return image


def convert_to_e(image, p=None, gain=None, exptime=None):
    """
    Converts image from ADU/s into e-

    :param image: numpy array (2D), the image
    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least: (if exptime is None)
                exptime: float, the exposure time of the image
                gain: float, the gain of the image

    :param gain: float, if p is None, used as the gain to multiple the image by
    :param exptime: float, if p is None, used as the exposure time the image
                    is multiplied by

    :return newimage: numpy array (2D), the image in e-
    """
    func_name = __NAME__ + '.convert_to_e()'
    # test if we have p and exptime/gain are in p - if we do convert -
    #    else raise error
    if p is not None:
        try:
            newimage = image * p['EXPTIME'] * p['GAIN']
        except KeyError:
            emsg1 = ('If parameter dictionary is defined keys "exptime" '
                     'must be in parameter dictionary.')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', '', [emsg1, emsg2])
            newimage = None
    # test of we have exptime and gain defined - if we do convert - else
    #     raise error
    elif gain is not None and exptime is not None:
        try:
            gain, exptime = float(gain), float(exptime)
            newimage = image * gain * exptime
        except ValueError:
            emsg1 = ('"gain" and "exptime" must be floats if parameter '
                     'dictionary is None.')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', '', [emsg1, emsg2])
            newimage = None
    # if neither p['exptime'] and p['gain' or exptime and gain are defined
    #     raise error
    else:
        emsg1 = 'Either "p" or ("gain" and "exptime") must be defined'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', '', [emsg1, emsg2])
        newimage = None

    return newimage


def convert_to_adu(image, p=None, exptime=None):
    """
    Converts image from ADU/s into ADU

    :param image:

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least: (if exptime is None)
            exptime: float, the exposure time of the image

    :param exptime: float, if p is None, used as the exposure time the image
                    is multiplied by

    :return newimage: numpy array (2D), the image in e-
    """
    func_name = __NAME__ + '.convert_to_adu()'
    # test if we have p and exptime is in p - if we do convert - else raise
    #    error
    if p is not None:
        try:
            newimage = image * p['EXPTIME']
        except KeyError:
            emsg1 = ('If parameter dictionary is defined key "exptime" '
                     'must be in parameter dictionary.')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', '', [emsg1, emsg2])
            newimage = None
    # test of we have exptime defined - if we do convert - else raise error
    elif exptime is not None:
        try:
            exptime = float(exptime)
            newimage = image * exptime
        except ValueError:
            emsg1 = ('"exptime" must be a float if parameter '
                     'dictionary is None.')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', '', [emsg1, emsg2])
            newimage = None
    # if neither p['exptime'] or exptime are defined raise error
    else:
        emsg1 = 'Either "p" or "exptime" must be defined'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', '', [emsg1, emsg2])
        newimage = None

    return newimage


def get_all_similar_files(p, directory, prefix=None, suffix=None):
    """
    Get all similar files in a directory with matching prefix and suffix defined
    either by "prefix" and "suffix" or by p["ARG_FILE_NAMES"][0]

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                log_opt: string, log option, normally the program name

    :param directory: string, the directory to search for files
    :param prefix: string or None, if not None the prefix to search for, if
                   None defines the prefix from the first 5 characters of
                   p["ARG_FILE_NAMES"][0]
    :param suffix: string  or None, if not None the suffix to search for, if
                   None defines the prefix from the last 8 characters of
                   p["ARG_FILE_NAMES"][0]

    :return filelist: list of strings, the full paths of all files that are in
                      "directory" with the matching prefix and suffix defined
                      either by "prefix" and "suffix" or by
                      p["ARG_FILE_NAMES"][0]
    """
    func_name = __NAME__ + '.get_all_similar_files()'
    # deal with no "arg_file_names"
    if prefix is None or suffix is None:
        if 'arg_file_names' not in p:
            emsg1 = ('"prefix" and "suffix" not defined and "arg_file_names" '
                     'not found in "p"')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # get file prefix and suffix
    if prefix is None:
        prefix = p['ARG_FILE_NAMES'][0][0:5]
    if suffix is None:
        suffix = p['ARG_FILE_NAMES'][0][-8:]
    # constrcut file string
    filestring = '{0}*{1}'.format(prefix, suffix)
    locstring = os.path.join(directory, filestring)
    # get all files
    filelist = glob.glob(locstring)
    # sort list
    filelist = np.sort(filelist)
    # return file list
    return list(filelist)


def interp_bad_regions(p, image):
    """
    Interpolate over the bad regions to fill in holes on image (only to be used
    for image localization)

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                IC_IMAGE_TYPE: string, the type of detector (H2RG or H4RG)
                BAD_REGION_FIT: list of floats, the fit to the curvature
                BAD_REGION_MED_SIZE: int, the median filter box size
                BAD_REGION_THRESHOLD: float, the threshold below which the
                                      image (normalised) should be regarded as
                                      bad (and the pixels in the image that
                                      should be set to the norm value)
                BAD_REGION_KERNAL_SIZE: int, the box size used to do the
                                        convolution
                BAD_REGION_MED_SIZE2: int, the median filter box size used
                                      during the convolution
                BAD_REGION_GOOD_VALUE: float, the final good ratio value
                                       (ratio between the original image and
                                        the interpolated image) to accept
                                        pixels as good pixels

                BAD_REGION_BAD_VALUE: float, the final bad ratio value
                                       (ratio between the original image and
                                        the interpolated image) to reject
                                        pixels as bad pixels

    :param image: numpy array (2D), the image

    :return image3: numpy array (2D), the corrected image
    """
    # TODO: Eventually remove H2RG fix
    # do not interp for H2RG
    if p['IC_IMAGE_TYPE'] == 'H2RG':
        return image
    # get the image size
    dim1, dim2 = image.shape
    # get parameters from p
    curvefit = p['BAD_REGION_FIT']
    med_size = p['BAD_REGION_MED_SIZE']
    threshold = p['BAD_REGION_THRESHOLD']
    kernel_size = p['BAD_REGION_KERNEL_SIZE']
    med_size2  = p['BAD_REGION_MED_SIZE2']
    goodvalue = p['BAD_REGION_GOOD_VALUE']
    badvalue = p['BAD_REGION_BAD_VALUE']
    # set nan pixels to zero
    image2 = np.where(np.isfinite(image), image, np.zeros_like(image))
    # create fit (using bad_region_fit parameters) to order curvature
    xpixfit = np.arange(dim2)
    ypixfit = np.polyval(curvefit, xpixfit)
    # work out the delta pixel shift needed to "straighten" curvature
    pixshift = ypixfit - np.mean(ypixfit)
    # -------------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], '   - Straightening interpolation image')
    # loop around all x pixels and shift pixels by interpolating with a spline
    for xi in range(dim2):
        # produce the universal spline fit
        splinefit = InterpUSpline(xpixfit, image2[:, xi], k=1)
        # apply the spline fit with the shift and write to the image
        image2[:, xi] = splinefit(xpixfit + pixshift[xi])
    # -------------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], '   - Applying median filter to interpolation image')
    # loop around all y pixels and median filter
    for yi in range(dim1):
        # get this iterations row data
        row = np.array(image2[yi, :])
        # median filter this iterations row data
        row_med = median_filter(row, size=med_size, mode='reflect')
        # normalise the row by the median filter
        row = row/row_med
        # find all pixels where the normalised value is less than
        #    "bad_region_threshold"
        rowmask = row < threshold
        # set the masked row sto the row median filter values
        image2[yi, rowmask] = row_med[rowmask]
    # -------------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], '   - Applying convolution to interpolation image')
    # define a kernal (box size) for the convolution
    kernel = np.repeat(1.0/kernel_size, kernel_size)
    # loop around all y pixels and apply a convolution over a median
    #    filter to create the final straight image

    for yi in range(dim1):
        # get this iterations row data
        row = np.array(image2[yi, :])
        # median filter over the image
        row_med = median_filter(row, size=med_size2, mode='reflect')
        # convolve the row median filter and write to image
        image2[yi, :] = np.convolve(row_med, kernel, mode='same')
    # -------------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], '   - Un-straightening interpolation image')
    # make sure all NaNs are 0
    image2 = np.where(np.isfinite, image2, np.zeros_like(image2))
    image = np.where(np.isfinite, image, np.zeros_like(image))
    # add the curvature back in (again by interpolating with a spline)
    for xi in range(dim2):
        # produce the universal spline fit
        splinefit = InterpUSpline(xpixfit, image2[:, xi], k=1)
        # apply the spline fit with the shift and write to the image
        image2[:, xi] = splinefit(xpixfit - pixshift[xi])
    # -------------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], '   - Calculating good and bad pixels (from ratio)')
    # calculate the ratio between original image and interpolated image
    ratio = image/image2
    # set all ratios greater than 1 to the inverse (reflect around 1)
    with warnings.catch_warnings(record=True) as w:
        rmask = ratio > 1
        ratio[rmask] = 1.0/ratio[rmask]
    # create a weight image
    weights = np.zeros_like(image, dtype=float)
    # decide which pixels are good and which pixels are bad
    with warnings.catch_warnings(record=True) as w:
        goodmask = ratio > goodvalue
        badmask = ratio < badvalue
        betweenmask = (~badmask) & (~goodmask)
    # fill the weight image based on the ratio (percentage of good image used)
    weights[goodmask] = 1.0
    weights[badmask] = 0.0
    weights[betweenmask] = 1.0 - 4.0 * (goodvalue - ratio[betweenmask])
    # using the weight image to correct the original image
    image3 = (image2 * (1 - weights)) + (image * weights)
    # return corrected image
    return image3


def fix_non_preprocessed(p, image, filename=None):
    """
    If a raw file is not preprocessed, then fix it (i.e. rotate it) so
    it conforms to DRS standards

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
            PROCESSED_SUFFIX: string, the processed suffix
            PREPROCESSED: bool, flag whether file is detected as
                          pre-processed
            IC_IMAGE_TYPE: string, the detector type
            RAW_TO_PP_ROTATION: int, rotation angle in degrees (in degrees,
                                counter-clockwise direction) must be a multiple
                                of 90 degrees
    :param image: numpy array (2D), the image to manipulate
    :param filename: string, if p['PREPROCESSED'] is not defined the file
                     is checked (can be done if PREPROCESSED in p

    :return newimage: numpy array (2D), the new image that emulates a pre-
                      processed file
    """

    func_name = __NAME__ + '.fix_non_preprocessed()'
    # if preprocessed not found calculate it
    if 'PREPROCESSED' not in p:
        if filename is None:
            emsg1 = 'Need to identify whether file is preprocessed'
            emsg2 = '\tPlease add "filename" to call to {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        else:
            if p['PROCESSED_SUFFIX'] in filename:
                p['PREPROCESSED'] = True
            else:
                p['PREPROCESSED'] = False
    # get conditions for rotation
    # TODO: remove H4RG dependency
    cond1 = p['IC_IMAGE_TYPE'] == 'H4RG'
    cond2 = not p['PREPROCESSED']
    # if conditions met rotate
    if cond1 and cond2:
        # log warning
        wmsg = 'Warning: Using non-preprocessed file!'
        WLOG('warning', p['LOG_OPT'], wmsg)
        # get rotation
        rotation = p['RAW_TO_PP_ROTATION']
        # rotate and return image
        return rotate(image, rotation)
    # else return image
    else:
        return image


# =============================================================================
# Define Pre-processing correction functions
# =============================================================================
def ref_top_bottom(p, image):
    """
    Correction for the top and bottom reference pixels

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                TOTAL_AMP_NUM: int, the total number of amplifiers on the
                               detector
                NUMBER_REF_TOP: int, the number of reference pixels at the top
                                of the image (highest y pixel values)
                NUMBER_REF_BOTTOM: int, the number of reference pixels at the
                                   bottom of the image (lowest y pixel values)
    :param image: numpy array (2D), the image

    :return image: numpy array (2D), the corrected image
    """
    # get the image size
    dim1, dim2 = image.shape
    # get constants from p
    tamp = p['TOTAL_AMP_NUM']
    ntop = p['NUMBER_REF_TOP']
    nbottom = p['NUMBER_REF_BOTTOM']
    # get number of pixels in amplifier
    pix_in_amp = dim2 // tamp
    pix_in_amp_2 = pix_in_amp // 2
    # work out the weights for y pixels
    weight = np.arange(dim1)/(dim1-1)
    # pipe into array to cover odd pixels and even pixels
    weightarr = np.repeat(weight, dim2 // pix_in_amp_2)
    # reshape
    weightarr = weightarr.reshape(dim1, pix_in_amp_2)
    # loop around each amplifier
    for amp_num in range(tamp):
        # get the pixel mask for this amplifier
        pixmask = (amp_num * dim2 // tamp) + 2 * np.arange(pix_in_amp_2)
        # loop around the even and then the odd pixels
        for oddeven in range(2):
            # work out the median of the bottom pixels for this amplifier
            bottom = np.nanmedian(image[:nbottom, pixmask + oddeven])
            top = np.nanmedian(image[dim1 - ntop:, pixmask + oddeven])
            # work out contribution to subtract from top and bottom
            contrib = (top * weightarr) + (bottom * (1 - weightarr))
            # subtraction contribution from image for this amplifier
            image[:, pixmask+oddeven] -= contrib
    # return corrected image
    return image


def median_filter_dark_amp(p, image):
    """
    Use the dark amplifiers to produce a median pattern and apply this to the
    image

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                TOTAL_AMP_NUM: int, the total number of amplifiers on the
                               detector
                NUMBER_DARK_AMP: int, the number of unilluminated (dark)
                                 amplifiers on the detector
                DARK_MED_BINNUM: int, the number of bins to use in the median
                                 filter binning process (higher number = finer
                                 bins, lower number = bigger bins)
    :param image: numpy array (2D), the image

    :return image: numpy array (2D), the corrected image
    """
    # get the image size
    dim1, dim2 = image.shape
    # get constants from p
    namp = p['NUMBER_DARK_AMP']
    tamp = p['TOTAL_AMP_NUM']
    ybinnum = p['DARK_MED_BINNUM']
    # get number of pixels in amplifier
    pix_in_amp = dim2 // tamp
    # ----------------------------------------------------------------------
    # extract the dark amplifiers + one for the median filtering
    image2 = image[:, : 128 * (namp + 1)]
    # there are ribbons every two amplifiers covering two pixels
    xribbon = []
    for pix in range(pix_in_amp * 2, pix_in_amp * namp, pix_in_amp * 2):
        xribbon = np.append(xribbon, pix - 1)
        xribbon = np.append(xribbon, pix)
    # create a copy of the dark amplifiers and set the ribbons to NaN
    image2b = image2.copy()
    image2b[:, xribbon.astype(int)] = np.nan
    # ----------------------------------------------------------------------
    # produce the median-binned image
    binstep = dim1 // ybinnum
    xbinnum = (namp + 1) * pix_in_amp // binstep
    # create an array to hold binned image
    imagebin = np.zeros([ybinnum, xbinnum])
    # bin image using a median (loop around bins)
    for i in range(ybinnum):
        for j in range(xbinnum):
            # get iteration bin pposition
            x0, y0 = i * binstep, j * binstep
            x1, y1 = i * binstep + binstep, j * binstep + binstep
            # calculate value at this position
            imagebin[i, j] = np.nanmedian(image2b[x0:x1, y0:y1])
    # apply a cubic spline onto the binned image
    image3 = scipy.ndimage.zoom(imagebin, binstep, order=2)
    # ----------------------------------------------------------------------
    # subtract the low-frequency part of the image
    #    this leaves the common structures
    diffimage = image2 - image3
    # create a cube that contains the dark amplifiers
    darkamps = np.zeros([namp, dim1, pix_in_amp])
    # loop around each amplifier and add the diff image for this amplifier
    # into the common storage cube
    for amp in range(namp):
        # amplifiers are flipped for odd numbered amplifiers
        if (amp % 2) == 1:
            # work out pixel positions for this amplifier
            firstpixel = (amp * pix_in_amp) + (pix_in_amp - 1)
            lastpixel = (amp * pix_in_amp) - 1
            # add diff image (flipped as amp is odd)
            darkamps[amp, :, :] = diffimage[:, firstpixel:lastpixel:-1]
        else:
            # work out pixel positions
            firstpixel = (amp * pix_in_amp)
            lastpixel = firstpixel + pix_in_amp
            # add diff image
            darkamps[amp, :, :] = diffimage[:, firstpixel:lastpixel]
    # from the cube that contains all dark amplifiers construct the
    #    median dark amplifier
    refamp = np.nanmedian(darkamps, axis=0)
    # ----------------------------------------------------------------------
    # subtract the median dark amp from each amplifier in the image
    for amp in range(tamp):
        # if odd flip
        if (amp % 2) == 1:
            # work out pixel positions for this amplifier
            firstpixel = (amp * pix_in_amp) + (pix_in_amp - 1)
            lastpixel = (amp * pix_in_amp) - 1
            # subtract off refamp
            image[:, firstpixel:lastpixel:-1] -= refamp
        else:
            # work out pixel positions
            firstpixel = (amp * pix_in_amp)
            lastpixel = firstpixel + pix_in_amp
            # subtract off refamp
            image[:, firstpixel:lastpixel] -= refamp
    # ----------------------------------------------------------------------
    # finally return corrected image
    return image


def median_one_over_f_noise(p, image):
    """
    Use the top and bottom reference pixels to create a map of the 1/f noise
    and apply it to the image

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                NUMBER_REF_TOP: int, the number of reference pixels at the top
                                of the image (highest y pixel values)
                NUMBER_REF_BOTTOM: int, the number of reference pixels at the
                                   bottom of the image (lowest y pixel values)
                NUMBER_DARK_AMP: int, the number of unilluminated (dark)
                                 amplifiers on the detector
                DARK_MED_BINNUM: int, the number of bins to use in the median
                                 filter binning process (higher number = finer
                                 bins, lower number = bigger bins)
    :param image: numpy array (2D), the image

    :return image: numpy array (2D), the corrected image
    """
    # get the image size
    dim1, dim2 = image.shape
    # get constants from p
    ntop = p['NUMBER_REF_TOP']
    nbottom = p['NUMBER_REF_BOTTOM']
    ybinnum = p['DARK_MED_BINNUM']
    # get the bin step
    binstep = dim1 // ybinnum
    # generate the list of top and bottom reference pixels to use
    bottompixels = np.arange(nbottom)
    toppixels = dim2 - np.arange(1, ntop + 1)[::-1]
    usepixels = np.append(bottompixels, toppixels).astype(int)
    # median the reference pixels
    refimage = np.nanmedian(image[:, usepixels])
    # use the refimage to create a map of 1/f noise
    noise1f = scipy.ndimage.median_filter(refimage, size=binstep,
                                          mode='reflect')
    # subtract the 1/f noise from the image
    for pixel in range(dim2):
        image[:, pixel] -= noise1f
    # return the corrected image
    return image


def median_one_over_f_noise2(p, image):
    """
    Use the dark amplifiers to create a map of the 1/f (residual) noise and
    apply it to the image

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                TOTAL_AMP_NUM: int, the total number of amplifiers on the
                               detector
                NUMBER_DARK_AMP: int, the number of unilluminated (dark)
                                 amplifiers on the detector
    :param image: numpy array (2D), the image

    :return image: numpy array (2D), the corrected image
    """
    # get the image size
    dim1, dim2 = image.shape
    # get constants from p
    total_amps = p['TOTAL_AMP_NUM']
    n_dark_amp = p['NUMBER_DARK_AMP']
    # width of an amplifier
    amp_width = dim1 // total_amps
    # set up a residual low frequency array
    residual_low_f = np.zeros(dim1)
    # loop around the dark amplifiers
    for amp in range(n_dark_amp):
        # define the start and end points of this amplifier
        start = amp * amp_width
        end = amp * amp_width + amp_width
        # median this amplifier across the x axis
        residual_low_f_tmp = np.nanmedian(image[:, start:end], axis=1)
        # if this is the first amplifier just set it equal to the median
        if amp == 0:
            residual_low_f = np.array(residual_low_f_tmp)
        # else only set values if they are less than the previous amplifier(s)
        else:
            smaller = residual_low_f_tmp < residual_low_f
            residual_low_f[smaller] = residual_low_f_tmp[smaller]
    # subtract the 1/f noise from the image
    for pixel in range(dim2):
        image[:, pixel] -= residual_low_f
    # return the corrected image
    return image


# =============================================================================
# Define Image correction functions
# =============================================================================
def measure_dark(pp, image, image_name, short_name):
    """
    Measure the dark pixels in "image"

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                DARK_QMIN: int, The lower percentile (0 - 100)
                DARK_QMAX: int, The upper percentile (0 - 100)
                HISTO_BINS: int,  The number of bins in dark histogram
                HISTO_RANGE_LOW: float, the lower extent of the histogram
                                 in ADU/s
                HISTO_RANGE_HIGH: float, the upper extent of the histogram
                                  in ADU/s

    :param image: numpy array (2D), the image
    :param image_name: string, the name of the image (for logging)
    :param short_name: string, suffix (for parameter naming -
                        parmaeters added to pp with suffix i)

    :return pp: parameter dictionary, the updated parameter dictionary
            Adds the following: (based on "short_name")
                histo_full: numpy.histogram tuple (hist, bin_edges) for
                            the full image
                histo_blue: numpy.histogram tuple (hist, bin_edges) for
                            the blue part of the image
                histo_red: numpy.histogram tuple (hist, bin_edges) for
                            the red part of the image
                med_full: float, the median value of the non-Nan image values
                          for the full image
                med_blue: float, the median value of the non-Nan image values
                          for the blue part of the image
                med_red: float, the median value of the non-Nan image values
                         for the red part of the image
                dadead_full: float, the fraction of dead pixels as a percentage
                             for the full image
                dadead_blue: float, the fraction of dead pixels as a percentage
                             for the blue part of the image
                dadead_red: float, the fraction of dead pixels as a percentage
                            for the red part of the image

          where:
              hist : numpy array (1D) The values of the histogram.
              bin_edges : numpy array (1D) of floats, the bin edges
    """
    func_name = __NAME__ + '.measure_dark()'
    # make sure image is a numpy array
    try:
        image = np.array(image)
    except Exception as _:
        emsg1 = '"image" is not a valid numpy array'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', pp['LOG_OPT'], [emsg1, emsg2])
    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = np.median(fimage)
    # get the 5th and 95th percentile qmin
    try:
        qmin, qmax = np.percentile(fimage, [pp['DARK_QMIN'], pp['DARK_QMAX']])
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', pp['LOG_OPT'], [e.message, emsg])
        qmin, qmax = None, None
    # get the histogram for flattened data
    try:
        histo = np.histogram(fimage, bins=pp['HISTO_BINS'],
                             range=(pp['HISTO_RANGE_LOW'],
                                    pp['HISTO_RANGE_HIGH']),
                             density=True)
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', pp['LOG_OPT'], [e.message, emsg])
        histo = None
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    wargs = ['In {0}'.format(image_name), dadead, med, pp['DARK_QMIN'],
             pp['DARK_QMAX'], qmin, qmax]
    wmsg = ('{0:12s}: Frac dead pixels= {1:.4f} % - Median= {2:.3f} ADU/s - '
            'Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s')
    WLOG('info', pp['LOG_OPT'], wmsg.format(*wargs))
    # add required variables to pp
    source = '{0}/{1}'.format(__NAME__, 'measure_dark()')
    pp['histo_{0}'.format(short_name)] = histo
    pp.set_source('histo_{0}'.format(short_name), source)
    pp['med_{0}'.format(short_name)] = med
    pp.set_source('med_{0}'.format(short_name), source)
    pp['dadead_{0}'.format(short_name)] = dadead
    pp.set_source('dadead_{0}'.format(short_name), source)
    # return the parameter dictionary with new values
    return pp


def correct_for_dark(p, image, header, nfiles=None, return_dark=False):
    """
    Corrects "image" for "dark" using calibDB file (header must contain
    value of p['ACQTIME_KEY'] as a keyword)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                nbframes: int, the number of frames/files (usually the length
                          of "arg_file_names")
                calibDB: dictionary, the calibration database dictionary
                         (if not in "p" we construct it and need "max_time_unix"
                max_time_unix: float, the unix time to use as the time of
                                reference (used only if calibDB is not defined)
                log_opt: string, log option, normally the program name
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param image: numpy array (2D), the image
    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage
    :param nfiles: int or None, number of files that created image (need to
                   multiply by this to get the total dark) if None uses
                   p['NBFRAMES']
    :param return_dark: bool, if True returns corrected_image and dark
                        if False (default) returns corrected_image

    :return corrected_image: numpy array (2D), the dark corrected image
                             only returned if return_dark = True:
    :return darkimage: numpy array (2D), the dark
    """
    func_name = __NAME__ + '.correct_for_dark()'
    if nfiles is None:
        nfiles = p['NBFRAMES']

    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = spirouDB.GetAcqTime(p, header)
        # get calibDB
        cdb, p = spirouDB.GetCalibDatabase(p, acqtime)
    else:
        try:
            cdb = p['CALIBDB']
            acqtime = p['MAX_TIME_UNIX']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [e.message, emsg])
            cdb, acqtime = None, None

    # try to read 'DARK' from cdb
    if 'DARK' in cdb:
        darkfile = os.path.join(p['DRS_CALIB_DB'], cdb['DARK'][1])
        WLOG('', p['LOG_OPT'], 'Doing Dark Correction using ' + darkfile)
        darkimage, nx, ny = spirouFITS.read_raw_data(darkfile, False, True)
        corrected_image = image - (darkimage * nfiles)
    else:
        # get master config file name
        masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
        # deal with extra constrain on file from "closer/older"
        comptype = p.get('CALIB_DB_MATCH', None)
        if comptype == 'older':
            extstr = '(with unit time <={1})'
        else:
            extstr = ''
        # log error
        emsg1 = 'No valid DARK in calibDB {0} ' + extstr
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1.format(masterfile, acqtime), emsg2])
        corrected_image, darkimage = None, None

    # finally return datac
    if return_dark:
        return corrected_image, darkimage
    else:
        return corrected_image


def get_badpixel_map(p, header=None):
    """
    Get the bad pixel map from the calibDB

        Must contain at least:
                calibDB: dictionary, the calibration database dictionary
                         (if not in "p" we construct it and need "max_time_unix"
                max_time_unix: float, the unix time to use as the time of
                                reference (used only if calibDB is not defined)
                log_opt: string, log option, normally the program name
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage

    :return: badpixmask: numpy array (2D), the bad pixel mask
    """
    func_name = __NAME__ + '.get_badpixel_map()'
    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = spirouDB.GetAcqTime(p, header)
        # get calibDB
        cdb, p = spirouDB.GetCalibDatabase(p, acqtime)
    else:
        try:
            cdb = p['CALIBDB']
            acqtime = p['MAX_TIME_UNIX']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [e.message, emsg])
            cdb, acqtime = None, None

    # try to read 'BADPIX' from cdb
    if 'BADPIX' in cdb:
        badpixfile = os.path.join(p['DRS_CALIB_DB'], cdb['BADPIX'][1])
        WLOG('', p['LOG_OPT'], 'Doing Bad Pixel Correction using ' + badpixfile)
        badpixmask, nx, ny = spirouFITS.read_raw_data(badpixfile, False, True)
        return badpixmask
    else:
        # get master config file name
        masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
        # deal with extra constrain on file from "closer/older"
        comptype = p.get('CALIB_DB_MATCH', None)
        if comptype == 'older':
            extstr = '(with unit time <={1})'
        else:
            extstr = ''
        # log error
        emsg1 = 'No valid BADPIX in calibDB {0} ' + extstr
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1.format(masterfile, acqtime), emsg2])
        return 0


def correct_for_badpix(p, image, header):
    """
    Corrects "image" for "BADPIX" using calibDB file (header must contain
    value of p['ACQTIME_KEY'] as a keyword) - sets all bad pixels to zeros

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                calibDB: dictionary, the calibration database dictionary
                         (if not in "p" we construct it and need "max_time_unix"
                max_time_unix: float, the unix time to use as the time of
                                reference (used only if calibDB is not defined)
                log_opt: string, log option, normally the program name
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param image: numpy array (2D), the image
    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage

    :return corrected_image: numpy array (2D), the corrected image where all
                             bad pixels are set to zeros
    """
    func_name = __NAME__ + '.correct_for_baxpix()'
    # get badpixmask
    badpixmask = get_badpixel_map(p, header)
    # create mask from badpixmask
    mask = np.array(badpixmask, dtype=bool)
    # correct image (set bad pixels to zero)
    corrected_image = np.where(mask, np.zeros_like(image), image)
    # finally return corrected_image
    return corrected_image


def normalise_median_flat(p, image, method='new', wmed=None, percentile=None):
    """
    Applies a median filter and normalises. Median filter is applied with width
    "wmed" or p["BADPIX_FLAT_MED_WID"] if wmed is None) and then normalising by
    the 90th percentile

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                BADPIX_FLAT_MED_WID: float, the median image in the x
                                     dimension over a boxcar of this width
                BADPIX_NORM_PERCENTILE: float, the percentile to normalise
                                        to when normalising and median
                                        filtering image
                log_opt: string, log option, normally the program name

    :param image: numpy array (2D), the iamge to median filter and normalise
    :param method: string, "new" or "old" if "new" uses np.percentile else
                   sorts the flattened image and takes the "percentile" (i.e.
                   90th) pixel value to normalise
    :param wmed: float or None, if not None defines the median filter width
                 if None uses p["BADPIX_MED_WID", see
                 scipy.ndimage.filters.median_filter "size" for more details
    :param percentile: float or None, if not None degines the percentile to
                       normalise the image at, if None used from
                       p["BADPIX_NORM_PERCENTILE"]

    :return norm_med_image: numpy array (2D), the median filtered and normalised
                            image
    :return norm_image: numpy array (2D), the normalised image
    """
    func_name = __NAME__ + '.normalise_median_flat()'
    # log that we are normalising the flat
    WLOG('', p['LOG_OPT'], 'Normalising the flat')

    # get used percentile
    if percentile is None:
        try:
            percentile = p['BADPIX_NORM_PERCENTILE']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [e.message, emsg])

    # wmed: We construct a "simili" flat by taking the running median of the
    # flag in the x dimension over a boxcar width of wmed (suggested
    # value of ~7 pix). This assumes that the flux level varies only by
    # a small amount over wmed pixels and that the badpixels are
    # isolated enough that the median along that box will be representative
    # of the flux they should have if they were not bad
    if wmed is None:
        try:
            wmed = p['BADPIX_FLAT_MED_WID']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [e.message, emsg])

    # create storage for median-filtered flat image
    image_med = np.zeros_like(image)

    # loop around x axis
    for i_it in range(image.shape[1]):
        # x-spatial filtering and insert filtering into image_med array
        image_med[i_it, :] = filters.median_filter(image[i_it, :], wmed)

    if method == 'new':
        # get the 90th percentile of median image
        norm = np.percentile(image_med[np.isfinite(image_med)], percentile)

    else:
        v = image_med.reshape(np.product(image.shape))
        v = np.sort(v)
        norm = v[int(np.product(image.shape) * percentile/100.0)]

    # apply to flat_med and flat_ref
    return image_med/norm, image/norm


def locate_bad_pixels(p, fimage, fmed, dimage, wmed=None):
    """
    Locate the bad pixels in the flat image and the dark image

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                BADPIX_FLAT_MED_WID: float, the median image in the x
                                     dimension over a boxcar of this width
                BADPIX_FLAT_CUT_RATIO: float, the maximum differential pixel
                                       cut ratio
                BADPIX_ILLUM_CUT: float, the illumination cut parameter
                BADPIX_MAX_HOTPIX: float, the maximum flux in ADU/s to be
                                   considered too hot to be used

    :param fimage: numpy array (2D), the flat normalised image
    :param fmed: numpy array (2D), the flat median normalised image
    :param dimage: numpy array (2D), the dark image
    :param wmed: float or None, if not None defines the median filter width
                 if None uses p["BADPIX_MED_WID", see
                 scipy.ndimage.filters.median_filter "size" for more details

    :return bad_pix_mask: numpy array (2D), the bad pixel mask image
    :return badpix_stats: list of floats, the statistics array:
                            Fraction of hot pixels from dark [%]
                            Fraction of bad pixels from flat [%]
                            Fraction of NaN pixels in dark [%]
                            Fraction of NaN pixels in flat [%]
                            Fraction of bad pixels with all criteria [%]
    """
    func_name = __NAME__ + '.locate_bad_pixels()'
    # log that we are looking for bad pixels
    WLOG('', p['LOG_OPT'], 'Looking for bad pixels')
    # -------------------------------------------------------------------------
    # wmed: We construct a "simili" flat by taking the running median of the
    # flag in the x dimension over a boxcar width of wmed (suggested
    # value of ~7 pix). This assumes that the flux level varies only by
    # a small amount over wmed pixels and that the badpixels are
    # isolated enough that the median along that box will be representative
    # of the flux they should have if they were not bad
    if wmed is None:
        try:
            wmed = p['BADPIX_FLAT_MED_WID']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [e.message, emsg])

    # maxi differential pixel response relative to the expected value
    try:
        cut_ratio = p['BADPIX_FLAT_CUT_RATIO']
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [e.message, emsg])
        cut_ratio = None

    # illumination cut parameter. If we only cut the pixels that
    # fractionnally deviate by more than a certain amount, we are going
    # to have lots of bad pixels in unillumnated regions of the array.
    # We therefore need to set a threshold below which a pixels is
    # considered unilluminated. First of all, the flat field image is
    # normalized by its 90th percentile. This sets the brighter orders
    # to about 1. We then set an illumination threshold below which
    # only the dark current will be a relevant parameter to decide that
    #  a pixel is "bad"
    try:
        illum_cut = p['BADPIX_ILLUM_CUT']
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [e.message, emsg])
        illum_cut = None
    # hotpix. Max flux in ADU/s to be considered too hot to be used
    try:
        max_hotpix = p['BADPIX_MAX_HOTPIX']
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [e.message, emsg])
        max_hotpix = None
    # -------------------------------------------------------------------------
    # create storage for ratio of flat_ref to flat_med
    fratio = np.zeros_like(fimage)
    # create storage for bad dark pixels
    badpix_dark = np.zeros_like(dimage, dtype=bool)
    # -------------------------------------------------------------------------
    # complain if the flat image and dark image do not have the same dimensions
    if dimage.shape != fimage.shape:
        eargs = np.array([fimage.shape, dimage.shape]).flatten()
        emsg1 = ('Flat image ({0}x{1}) and Dark image ({2}x{3}) must have the '
                 'same shape.')
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1.format(*eargs), emsg2])
    # -------------------------------------------------------------------------
    # as there may be a small level of scattered light and thermal
    # background in the dark  we subtract the running median to look
    # only for isolate hot pixels
    for i_it in range(fimage.shape[1]):
        dimage[i_it, :] -= filters.median_filter(dimage[i_it, :], wmed)
    # work out how much do flat pixels deviate compared to expected value
    zmask = fmed != 0
    fratio[zmask] = fimage[zmask] / fmed[zmask]
    # catch the warnings
    with warnings.catch_warnings(record=True) as _:
        # if illumination is low, then consider pixel valid for this criterion
        fratio[fmed < illum_cut] = 1
    # catch the warnings
    with warnings.catch_warnings(record=True) as _:
        # where do pixels deviate too much
        badpix_flat = (np.abs(fratio - 1)) > cut_ratio
    # -------------------------------------------------------------------------
    # get finite flat pixels
    valid_flat = np.isfinite(fimage)
    # -------------------------------------------------------------------------
    # get finite dark pixels
    valid_dark = np.isfinite(dimage)
    # -------------------------------------------------------------------------
    # select pixels that are hot
    badpix_dark[valid_dark] = dimage[valid_dark] > max_hotpix
    # -------------------------------------------------------------------------
    # construct the bad pixel mask
    badpix_map = badpix_flat | badpix_dark | ~valid_flat | ~valid_dark
    # -------------------------------------------------------------------------
    # log results
    text = ['Fraction of hot pixels from dark: {0:.4f} %',
            'Fraction of bad pixels from flat: {0:.4f} %',
            'Fraction of non-finite pixels in dark: {0:.4f} %',
            'Fraction of non-finite pixels in flat: {0:.4f} %',
            'Fraction of bad pixels with all criteria: {0:.4f} %']
    badpix_stats = [(np.sum(badpix_dark) / badpix_dark.size) * 100,
                    (np.sum(badpix_flat) / badpix_flat.size) * 100,
                    (np.sum(~valid_dark) / valid_dark.size) * 100,
                    (np.sum(~valid_flat) / valid_flat.size) * 100,
                    (np.sum(badpix_map) / badpix_map.size) * 100]

    for it in range(len(text)):
        WLOG('', p['LOG_OPT'], text[it].format(badpix_stats[it]))
    # -------------------------------------------------------------------------
    # return bad pixel map
    return badpix_map, badpix_stats


def locate_bad_pixels_full(p, image):
    """
    Locate the bad pixels identified from the full engineering flat image
    (location defined from p['BADPIX_FULL_FLAT'])

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_IMAGE_TYPE: string, the detector type (this step is only for
                           H4RG)
            LOG_OPT: string, log option, normally the program name
            BADPIX_FULL_FLAT: string, the full engineering flat filename
            BADPIX_FULL_THRESHOLD: float, the threshold on the engineering
                                   above which the data is good
    :param image: numpy array (2D), the image to correct (for size only)

    :return newimage: numpy array (2D), the mask of the bad pixels
    :return stats: float, the fraction of un-illuminated pixels (percentage)
    """

    # TODO: remove H2RG dependencies
    # if we are using H2RG we don't need this map
    if p['IC_IMAGE_TYPE'] == 'H2RG':
        return np.ones_like(image, dtype=bool), 0
    # log that we are looking for bad pixels
    WLOG('', p['LOG_OPT'], 'Looking for bad pixels in full flat image')
    # get parameters from p
    filename = p['BADPIX_FULL_FLAT']
    threshold = p['BADPIX_FULL_THRESHOLD']
    # construct filepath
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.BADPIX_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    absfilename = os.path.join(datadir, filename)
    # check that filepath exists
    if not os.path.exists(absfilename):
        emsg = 'badpix full flat ({0}) not found in {1}. Please correct.'
        WLOG('error', p['LOG_OPT'], emsg.format(filename, datadir))
    # read image
    mdata, _, _, _, _ = spirouFITS.readimage(p, absfilename, kind='FULLFLAT')
    # apply threshold
    #mask = np.rot90(mdata, -1) < threshold
    mask = np.abs(np.rot90(mdata, -1)-1) > threshold

    # -------------------------------------------------------------------------
    # log results
    badpix_stats = (np.sum(mask) / mask.size) * 100
    text = 'Fraction of un-illuminated pixels in engineering flat {0:.4f} %'
    WLOG('', p['LOG_OPT'], text.format(badpix_stats))

    # return mask
    return mask, badpix_stats


def get_tilt(pp, lloc, image):
    """
    Get the tilt by correlating the extracted fibers

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                ic_tilt_coi: int, oversampling factor
                log_opt: string, log option, normally the program name

    :param lloc: parameter dictionary, ParamDict containing data
            Must contain at least:
                number_orders: int, the number of orders in reference spectrum
                cent1: numpy array (2D), the extraction for A, updated is
                       the order "rnum"
                cent2: numpy array (2D), the extraction for B, updated is
                       the order "rnum"
                offset: numpy array (1D), the center values with the
                        offset in 'IC_CENT_COL' added

    :param image: numpy array (2D), the image

    :return lloc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                nbcos: numpy array, zero array  (length of "number_orderes")
                tilt: numpy array (1D), the tilt angle of each order

    """
    nbo = lloc['NUMBER_ORDERS']
    # storage for "nbcos"
    # Question: what is nbcos? as it isn't used
    lloc['NBCOS'] = np.zeros(nbo, dtype=int)
    lloc.set_source('NBCOS', __NAME__ + '/get_tilt()')
    # storage for tilt
    lloc['TILT'] = np.zeros(int(nbo/2), dtype=float)
    lloc.set_source('TILT', __NAME__ + '/get_tilt()')
    # Over sample the data and interpolate new extraction values
    pixels = np.arange(image.shape[1])
    os_fac = pp['IC_TILT_COI']
    os_pixels = np.arange(image.shape[1] * os_fac) / os_fac
    # loop around each order
    for order_num in range(0, nbo, 2):
        # extract this AB order
        lloc = spirouEXTOR.ExtractABOrderOffset(pp, lloc, image, order_num)
        # --------------------------------------------------------------------
        # interpolate the pixels on to the extracted centers
        cent1i = np.interp(os_pixels, pixels, lloc['CENT1'])
        cent2i = np.interp(os_pixels, pixels, lloc['CENT2'])
        # --------------------------------------------------------------------
        # get the correlations between cent2i and cent1i
        cori = np.correlate(cent2i, cent1i, mode='same')
        # --------------------------------------------------------------------
        # get the tilt - the maximum correlation between the middle pixel
        #   and the middle pixel + 10 * p['COI']
        coi = int(os_fac)
        pos = int(image.shape[1] * coi / 2)
        delta = np.argmax(cori[pos:pos + 10 * coi]) / coi
        # get the angle of the tilt
        angle = np.rad2deg(-1 * np.arctan(delta / (2 * lloc['OFFSET'])))
        # log the tilt and angle
        wmsg = 'Order {0}: Tilt = {1:.2f} on pixel {2:.1f} = {3:.2f} deg'
        wargs = [order_num / 2, delta, 2 * lloc['OFFSET'], angle]
        WLOG('', pp['LOG_OPT'], wmsg.format(*wargs))
        # save tilt angle to lloc
        lloc['TILT'][int(order_num / 2)] = angle
    # return the lloc
    return lloc


def fit_tilt(pp, lloc):
    """
    Fit the tilt (lloc['TILT'] with a polynomial of size = p['IC_TILT_FILT']
    return the coefficients, fit and residual rms in lloc dictionary

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_TILT_FIT: int, Order of polynomial to fit for tilt

    :param lloc: parameter dictionary, ParamDict containing data
            Must contain at least:
                number_orders: int, the number of orders in reference spectrum
                tilt: numpy array (1D), the tilt angle of each order

    :return lloc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                xfit_tilt: numpy array (1D), the order numbers
                yfit_tilt: numpy array (1D), the fit for the tilt angle of each
                           order
                a_tilt: numpy array (1D), the fit coefficients (generated by
                        numpy.polyfit but IN REVERSE ORDER)
                rms_tilt: float, the RMS (np.std) of the residuals of the
                          tilt - tilt fit values
    """

    # get the x values for
    xfit = np.arange(lloc['NUMBER_ORDERS']/2)
    # get fit coefficients for the tilt polynomial fit
    atc = np.polyfit(xfit, lloc['TILT'], pp['IC_TILT_FIT'])[::-1]
    # get the yfit values for the fit
    yfit = np.polyval(atc[::-1], xfit)
    # get the rms for the residuls of the fit and the data
    rms = np.std(lloc['TILT'] - yfit)
    # store the fit data in lloc
    lloc['XFIT_TILT'] = xfit
    lloc.set_source('XFIT_TILT', __NAME__ + '/fit_tilt()')
    lloc['YFIT_TILT'] = yfit
    lloc.set_source('YFIT_TILT', __NAME__ + '/fit_tilt()')
    lloc['A_TILT'] = atc
    lloc.set_source('A_TILT', __NAME__ + '/fit_tilt()')
    lloc['RMS_TILT'] = rms
    lloc.set_source('RMS_TILT', __NAME__ + '/fit_tilt()')

    # return lloc
    return lloc


def read_line_list(p=None, filename=None):
    """
    Read the line list file (if filename is None construct file from
    p['IC_LL_LINE_FILE']

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            log_opt: string, log option, normally the program name

        May contain
            IC_LL_LINE_FILE: string, the file name of the line list to use
                             (required if filename is None)

    :param filename: string or None, if defined the filename

    :return ll: numpy array (1D), the wavelengths of the lines from line list
    :return amp: numpy array (1D), the amplitudes of the lines from line list
    """

    func_name = __NAME__ + '.read_line_list()'
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.WAVELENGTH_CATS_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # deal with p and filename being None
    if p is None and filename is None:
        emsg1 = 'p (ParamDict) or "filename" must be defined'
        emsg2 = '    function={0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # assign line file
    if filename is not None:
        # if filename is absolute path and file exists use this
        if os.path.exists(filename):
            linefile = filename
        # if filename is defined but doesn't exist try to see if it is in the
        # data folder
        else:
            linefile = os.path.join(datadir, filename)
    elif 'IC_LL_LINE_FILE' in p:
        # else use the predefined line list file from "p"
        if os.path.exists(p['IC_LL_LINE_FILE']):
            linefile = p['IC_LL_LINE_FILE']
        # if it isn't an absolute path try to see if it is in the data folder
        else:
            linefile = os.path.join(datadir, p['IC_LL_LINE_FILE'])
    else:
        emsg1 = ('p[\'IC_LL_LINE_FILE\'] (ParamDict) or "filename" '
                 'must be defined')
        emsg2 = '    function={0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        linefile = ''
    # check that line file exists
    if not os.path.exists(linefile):
        emsg1 = 'Line list file={0} does not exist.'.format(linefile)
        emsg2 = '    function={0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # read filename as a table (no header so need data_start=0)
    linetable = spirouTable.read_table(linefile,
                                       fmt='ascii.tab',
                                       colnames=['ll', 'amp', 'kind'],
                                       data_start=0)
    # push columns into numpy arrays and force to floats
    ll = np.array(linetable['ll'], dtype=float)
    amp = np.array(linetable['amp'], dtype=float)
    # log that we have opened line file
    wmsg = 'List of {0} HC lines read in file {1}'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(len(ll), linefile))
    # return line list and amps
    return ll, amp


# =============================================================================
# Get basic image properties
# =============================================================================
def get_exptime(p, hdr, name=None, return_value=False):
    """
    Get Exposure time from HEADER. Wrapper for spirouImage.get_param

    :param p: parameter dictionary, ParamDict of constants
    :param hdr: dictionary, header dictionary to extract
    :param name: string or None, if not None the name for the parameter
                 logged if there is an error in getting parameter, if name is
                 None the name is taken as "keyword"
    :param return_value: bool, if True returns parameter, if False adds
                         parameter to "p" parameter dictionary (and sets source)

    :return value: if return_value is True value of parameter is returned
    :return p: if return_value is False, updated parameter dictionary p with
               key = name is returned
    """
    # return param
    return get_param(p, hdr, 'kw_exptime', name, return_value)


def get_gain(p, hdr, name=None, return_value=False):
    """
    Get Gain from HEADER. Wrapper for spirouImage.get_param

    :param p: parameter dictionary, ParamDict of constants
    :param hdr: dictionary, header dictionary to extract
    :param name: string or None, if not None the name for the parameter
                 logged if there is an error in getting parameter, if name is
                 None the name is taken as "keyword"
    :param return_value: bool, if True returns parameter, if False adds
                         parameter to "p" parameter dictionary (and sets source)

    :return value: if return_value is True value of parameter is returned
    :return p: if return_value is False, updated parameter dictionary p with
               key = name is returned
    """
    # return param
    return get_param(p, hdr, 'kw_gain', name, return_value)


def get_sigdet(p, hdr, name=None, return_value=False):
    """
    Get sigdet from HEADER. Wrapper for spirouImage.get_param

    :param p: parameter dictionary, ParamDict of constants
    :param hdr: dictionary, header dictionary to extract
    :param name: string or None, if not None the name for the parameter
                 logged if there is an error in getting parameter, if name is
                 None the name is taken as "keyword"
    :param return_value: bool, if True returns parameter, if False adds
                         parameter to "p" parameter dictionary (and sets source)

    :return value: if return_value is True value of parameter is returned
    :return p: if return_value is False, updated parameter dictionary p with
               key = name is returned
    """
    # return param
    return get_param(p, hdr, 'kw_rdnoise', name, return_value)


def get_param(p, hdr, keyword, name=None, return_value=False, dtype=None):
    """
    Get parameter from header "hdr" using "keyword" (keyword store constant)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            "keyword" defined in call
            log_opt: string, log option, normally the program name
            "name" defined in call

    :param hdr: dictionary, HEADER dictionary containing key/value pairs
                extracted from a FITS rec header
    :param keyword: string, the keyword key (taken from "p") this allows
                    getting of the keyword store from the parameter dictionary
    :param name: string or None, if not None the name for the parameter
                 logged if there is an error in getting parameter, if name is
                 None the name is taken as "keyword"
    :param return_value: bool, if True returns parameter, if False adds
                         parameter to "p" parameter dictionary (and sets source)
    :param dtype: type or None, if not None then tries to convert raw
                  parameter to type=dtype

    :return value: if return_value is True value of parameter is returned
    :return p: if return_value is False, updated parameter dictionary p with
               key = name is returned
    """
    func_name = __NAME__ + '.get_param()'
    # get header keyword
    key = p[keyword][0]
    # deal with no name
    if name is None:
        name = key
    # get raw value
    rawvalue = spirouFITS.keylookup(p, hdr, key)
    # get type casted value
    try:
        if dtype is None:
            dtype = float
            value = float(rawvalue)
        elif type(dtype) == type:
            value = dtype(rawvalue)
        else:
            emsg1 = 'Dtype "{0}" is not a valid python type. Keyword={1}'
            emsg2 = '     function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1.format(dtype, keyword), emsg2])
            value = None
    except ValueError:
        emsg1 = ('Cannot convert keyword "{0}"="{1}" to type "{2}"'
                 '').format(keyword, rawvalue, dtype)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        value = None

    # deal with return value
    if return_value:
        return value
    else:
        # assign value to p[name]
        p[name] = value
        # set source
        if '@@@hname' in hdr:
            p.set_source(name, hdr['@@@hname'])
        else:
            p.set_source(name, func_name + ' (via file HEADER)')
        # return p
        return p


def get_acqtime(p, hdr, name=None, kind='human', return_value=False):
    """
    Get the acquision time from the header file, if there is not header file
    use the parameter dictionary "p" to open the header in 'arg_file_names[0]'

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            "name" defined in call
            parameter dictionary to give to value

    :param hdr: dictionary, the header dictionary created by
                spirouFITS.ReadImage
    :param name: string, the name in parameter dictionary to give to value
                 if return_value is False (i.e. p[name] = value)
    :param kind: string, 'human' for 'YYYY-mm-dd-HH-MM-SS.ss' or 'julian'
    :param return_value: bool, if False value is returned in p as p[name]
                         if True value is returned

    :return p or value: dictionary or string or float, if return_value is False
                        parameter dictionary is returned, if return_value is
                        True and kind=='human' returns a string, if return_value
                        is True and kind=='unix' returns a float
    """
    # deal with no name
    if name is None:
        name = 'acqtime'
    # get header keyword
    value = spirouDB.GetAcqTime(p, hdr, kind=kind)
    # deal with return value
    if return_value:
        return value
    else:
        # assign value to p[name]
        p[name] = value
        # set source
        p.set_source(name, hdr['@@@hname'])
        # return p
        return p


def get_wave_keys(p, loc, hdr):
    func_name = __NAME__ + '.get_wave_keys()'
    # check for header key
    if p['KW_WAVE_FILE'][0] in hdr:
        wkwargs = dict(p=p, hdr=hdr, return_value=True)
        loc['WAVEFILE'] = get_param(keyword='KW_WAVE_FILE', dtype=str,
                                    **wkwargs)
        loc['WAVETIME1'] = get_param(keyword='KW_WAVE_TIME1', dtype=str,
                                     **wkwargs)
        loc['WAVETIME2'] = get_param( keyword='KW_WAVE_TIME2', **wkwargs)
    # TODO: Remove section later
    else:
        # log warning
        wmsg = 'Warning key="{0}" not in HEADER file'
        WLOG('warning', p['LOG_OPT'], wmsg.format(p['KW_WAVE_FILE'][0]))
        # set wave file to fitsfilename
        loc['WAVEFILE'] = p['FITSFILENAME']
        loc['WAVETIME1'] = 'Unknown'
        loc['WAVETIME2'] = -9999

    # set sources
    loc.set_sources(['WAVEFILE', 'WAVETIME1', 'WAVETIME2'], func_name)
    # return loc
    return loc


def get_obj_name(p, hdr):
    # get parameter
    raw_obj_name = get_param(p, hdr, keyword='KW_OBJNAME', dtype=str,
                             return_value=True)
    # filter out bad characters
    obj_name = spirouFITS.get_good_object_name(p, rawname=raw_obj_name)
    # return object name
    return obj_name


def get_airmass(p, hdr):
    # get parameter
    raw_airmass = get_param(p, hdr, keyword='KW_AIRMASS', return_value=True)
    # return airmass
    return float(raw_airmass)


# TODO insert paremeter dictionnary
# TODO: FIX PROBLEMS: Write doc string
def e2dstos1d(wave,e2dsffb,bin):
    """
    Convert E2DS (2-dimension) spectra to 1-dimension spectra
    with merged spectral orders and regular sampling


    :param wave: wavelength solution
    :param e2dsffb : e2ds falt-fielded and blaze corrected
    :param bin : S1d sampling in nm
    """
    # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
    for o in range(len(e2dsffb)):

        x = wave[o] * 1.
        y = e2dsffb[o] * 1.

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Integral Calculation yy by summation
        dx = np.concatenate((np.array([x[1] - x[0]]), (x[2:] - x[0:-2]) / 2., np.array([x[-1] - x[-2]])))
        stepmax = np.max(dx)
        yy = np.concatenate((np.array([0.]), np.cumsum(y * dx)))
        xx = np.concatenate((x - dx / 2., np.array([x[-1] + dx[-1] / 2.])))

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Computation of the new coordinates
        #   if o == 0:
        xx = x[y > 0]
        l1 = 1. * (int(xx[0] * (1. / bin)) + 1) / (1. / bin) + bin
        l2 = 1. * (int(xx[-1] * (1. / bin))) / (1. / bin) - bin
        #   else:
        #       l1 = 1. * (int(x[0] * (1. / bin)) + 1) / (1. / bin) + bin
        #       l2 = 1. * (int(x[-1] * (1. / bin))) / (1. / bin) - bin

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Interpolation by cubic spline
        xxi = np.arange(l1, l2 + bin, bin) - bin / 2.
        yyi = griddata(xx, yy, xxi, method='cubic')

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Computation of the derivation
        xi = xxi[0:-1] + bin / 2.
        yi = (yyi[1:] - yyi[0:-1]) / bin

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Merging of orders
        if o == 0:
            xs1d = xi * 1.
            ys1d = yi * 1.

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        lim1 = xs1d[-1]
        lim2 = xi[0]
        if lim1 < lim2:
            zone0x = np.arange(lim1 + bin, lim2, bin)
            zone0y = np.zeros(len(zone0x), 'd')
            ys1d = np.concatenate((ys1d, zone0y, yi))
            xs1d = np.concatenate((xs1d, zone0x, xi))
        else:
            ind = int(round((lim1 - lim2) / bin))
            w = 1. - np.arange(ind * 1. + 1.) / ind
            zonec = ys1d[-ind - 1:] * w + yi[0:ind + 1] * (1. - w)
            ys1d = np.concatenate((ys1d[:-ind - 1], zonec, yi[ind + 1:]))
            xs1d = np.concatenate((xs1d[:-ind - 1], xi))

    return xs1d, ys1d


# =============================================================================
# End of code
# =============================================================================
