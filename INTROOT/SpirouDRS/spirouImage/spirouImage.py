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
from astropy import constants as cc
from astropy import units as uu
import os
import glob
import warnings
import scipy
from scipy.ndimage import filters, median_filter
from scipy.ndimage import map_coordinates as mapc
from scipy.interpolate import griddata
from scipy.stats import stats
from scipy.signal import medfilt
from scipy.optimize import curve_fit

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from SpirouDRS.spirouCore import spirouMath
from SpirouDRS.spirouCore.spirouMath import IUVSpline
from SpirouDRS.spirouCore.spirouMath import nanpolyfit
import off_listing_REDUC_spirou

from . import spirouFITS
from . import spirouTable
from . import spirouFile

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
# Get plotting functions
sPlt = spirouCore.sPlt
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict
# get the config error
ConfigError = spirouConfig.ConfigError
# -----------------------------------------------------------------------------
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define Image modification function
# =============================================================================
def resize(p, image, x=None, y=None, xlow=0, xhigh=None, ylow=0, yhigh=None,
           getshape=True):
    """
    Resize an image based on a pixel values

    :param p: parameter dictionary of constants
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

    # deal with no xlow or ylow
    if xlow is None:
        xlow = p['IC_CCDX_LOW']
        xhigh = p['IC_CCDX_HIGH']
    if ylow is None:
        ylow = p['IC_CCDY_LOW']
        yhigh = p['IC_CCDY_HIGH']
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
            WLOG(p, 'error', [emsg1, emsg2])
        else:
            x = np.arange(xlow, xhigh)
        # deal with ylow > yhigh
        if ylow > yhigh:
            y = np.arange(yhigh + 1, ylow + 1)[::-1]
        elif ylow == yhigh:
            emsg1 = '"ylow" and "yhigh" cannot have the same values'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
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
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
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


def flip_image(p, image, fliprows=True, flipcols=True):
    """
    Flips the image in the x and/or the y direction

    :param p: ParamDict, the constants parameter dictionary
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
        WLOG(p, 'error', [emsg1.format(image.shape), emsg2])
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


def convert_to_e(image, p, gain=None, exptime=None):
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

    # test of we have exptime and gain defined - if we do convert - else
    #     raise error
    if gain is not None and exptime is not None:
        try:
            gain, exptime = float(gain), float(exptime)
            newimage = image * gain * exptime
        except ValueError:
            emsg1 = '"gain" and "exptime" must be floats'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
            newimage = None
    # test if we have p and exptime/gain are in p - if we do convert -
    #    else raise error
    else:
        try:
            newimage = image * p['EXPTIME'] * p['GAIN']
        except KeyError:
            emsg1 = ('If parameter dictionary is defined keys "exptime" '
                     'must be in parameter dictionary.')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
            newimage = None

    return newimage


def convert_to_adu(image, p, exptime=None):
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

    # test of we have exptime defined - if we do convert - else raise error
    if exptime is not None:
        try:
            exptime = float(exptime)
            newimage = image * exptime
        except ValueError:
            emsg1 = ('"exptime" must be a float if parameter '
                     'dictionary is None.')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
            newimage = None
    # test if we have p and exptime is in p - if we do convert - else raise
    #    error
    else:
        try:
            newimage = image * p['EXPTIME']
        except KeyError:
            emsg1 = ('If parameter dictionary is defined key "exptime" '
                     'must be in parameter dictionary.')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
            newimage = None

    return newimage


def get_all_similar_files_old(p, directory, prefix=None, suffix=None):
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
            WLOG(p, 'error', [emsg1, emsg2])
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


def get_all_similar_files(p, hdr):
    """
    Get all similar files in a directory with matching prefix and suffix defined
    either by "prefix" and "suffix" or by p["ARG_FILE_NAMES"][0]

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                log_opt: string, log option, normally the program name

    :param hdr: dict, header of the reference file

    :return filelist: list of strings, the full paths of all files that are in
                      "directory" with the matching prefix and suffix defined
                      either by "prefix" and "suffix" or by
                      p["ARG_FILE_NAMES"][0]
    """
    func_name = __NAME__ + '.get_all_similar_files()'

    # get the allowed file types
    allowed_file_types_all = p['DRIFT_PEAK_ALLOWED_OUTPUT']

    # get the keys for this file
    # if p['KW_OUTPUT'][0] in hdr:
    #     output = hdr[p['KW_OUTPUT'][0]]
    # else:
    #     emsg1 = 'Key "{0}" missing from header'.format(p['KW_OUTPUT'][0])
    #     emsg2 = '\tfunction = {0}'.format(func_name)
    #     WLOG(p, 'error', [emsg1, emsg2])
    #     output = None

    # get the output key for this file
    if p['KW_OUTPUT'][0] in hdr:
        output = hdr[p['KW_OUTPUT'][0]]
    else:
        emsg1 = 'Header key = "{0}" missing from file {1}'
        emsg2 = '\tfunction = {0}'.format(func_name)
        eargs = [p['KW_OUTPUT'][0], p['REFFILENAME']]
        WLOG(p, 'error', [emsg1.format(*eargs), emsg2])
        output = None

    # get lamp type and extraction type
    if p['KW_EXT_TYPE'][0] in hdr:
        ext_type = hdr[p['KW_EXT_TYPE'][0]]
        drift_types = p['DRIFT_PEAK_ALLOWED_TYPES'].keys()
        found, lamp = False, 'None'
        for kind in drift_types:
            if ext_type == kind:
                lamp = p['DRIFT_PEAK_ALLOWED_TYPES'][kind]
                found = True
        if not found:
            eargs1 = [p['KW_EXT_TYPE'][0], ' or '.join(drift_types)]
            emsg1 = ('Wrong type of image for Drift, header key "{0}" should be'
                     '{1}'.format(*eargs1))
            emsg2 = '\tPlease check DRIFT_PEAK_ALLOWED_TYPES'
            WLOG(p, 'error', [emsg1, emsg2])
            lamp = 'None'
            ext_type = None
    else:
        emsg1 = 'Header key = "{0}" missing from file {1}'
        emsg2 = '\tfunction = {0}'.format(func_name)
        eargs = [p['KW_EXT_TYPE'][0], p['REFFILENAME']]
        WLOG(p, 'error', [emsg1.format(*eargs), emsg2])
        lamp = 'None'
        ext_type = None
    # get file type allowed (using lamp type)
    if lamp in allowed_file_types_all:
        allowed_file_types = allowed_file_types_all[lamp]
    else:
        emsg1 = 'Reference file was identified as lamp={0}'
        emsg2 = '\tHowever DRIFT_PEAK_ALLOWED_OUTPUT missing this key.'
        emsg3 = '\tPlease check constants file'
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
        allowed_file_types = None

    # get expected index file name and location
    index_file = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    path = p['REDUCED_DIR']
    index_path = os.path.join(path, index_file)

    # if file does not exist try to index this folder
    ntries = 0
    while (not os.path.exists(index_path)) and (ntries < 5):
        wmsg = 'No index file. Running indexing (Attempt {0} of {1})'
        wargs = [ntries + 1, 5]
        WLOG(p, 'warning', wmsg.format(*wargs))
        off_listing_REDUC_spirou.main(night_name=p['ARG_NIGHT_NAME'],
                                      quiet=True)
        ntries += 1
    # if file exists then we have some indexed files
    if os.path.exists(index_path):
        itable = spirouTable.read_fits_table(p, index_path)
    else:
        emsg1 = 'No index file. Could not run indexing'
        emsg2 = '\t Please run off_listing_REDUC_spirou.py'
        WLOG(p, 'error', [emsg1, emsg2])
        itable = None

    # check that we have the correct output type (i.e. EXT_E2DS)
    mask1 = itable[p['KW_OUTPUT'][0]] == output
    # check that we have the correct extraction type (e.g. FP_FP or HCONE_HCONE)
    mask2 = np.in1d(np.array(itable[p['KW_EXT_TYPE'][0]], dtype=str),
                    np.array(allowed_file_types))
    # check that we are not including the original filename
    mask3 = itable['FILENAME'] != os.path.basename(p['FITSFILENAME'])
    # check that fiber type is correct for all
    mask4 = check_fiber_ext_type(p, itable, allowed_file_types)
    # combine masks
    mask = mask1 & mask2 & mask3 & mask4

    # check that we have some rows left
    if np.sum(mask) == 0:
        emsg = 'No other valid files found that match {0}="{1}" {2}="{3}"'
        eargs = [p['KW_OUTPUT'][0], allowed_file_types,
                 p['KW_EXT_TYPE'][0], ext_type]
        WLOG(p, 'error', emsg.format(*eargs))
    # if we do get date and sort by it
    else:
        # apply mask
        itable = itable[mask]
        # get the absolute filenames
        abs_filenames = []
        for row in range(len(itable)):
            # get filename (and make sure it is just a filename)
            filename = os.path.basename(itable['FILENAME'][row])
            # join to path
            abs_filename = os.path.join(p['ARG_FILE_DIR'], filename)
            # append to list
            abs_filenames.append(abs_filename)
        # add to itable
        itable['ABSFILENAMES'] = abs_filenames
        # get unix_time for each row
        unix_times = []
        for row in range(len(itable)):
            # get string date and time (part1 and part2)
            part1 = itable[p['kw_DATE_OBS'][0]][row].strip()
            part2 = itable[p['kw_UTC_OBS'][0]][row].strip()
            # merge into string
            stringtime = '{0}-{1}'.format(part1, part2)
            # convert to unix time
            # TODO: Do we want bad unix_times to just warn or to crash code
            try:
                unix_time = spirouMath.stringtime2unixtime(stringtime)
            except spirouMath.MathException as _:
                emsg1 = 'Time="{0}" not valid for file = {1}'
                emsg2 = '\tFrom header: {0}="{1}" {2}="{3}"'
                eargs1 = [stringtime, itable['FILENAME'][row]]
                eargs2 = [p['kw_DATE_OBS'][0], part1,
                          p['kw_UTC_OBS'][0], part2]
                emsgs = [emsg1.format(*eargs1), emsg2.format(*eargs2)]
                WLOG(p, 'warning', emsgs)
                unix_time = np.nan
            # append to list
            unix_times.append(unix_time)
        # sort by unix time
        sortmask = np.argsort(unix_times)
        # apply sort mask
        itable = itable[sortmask]
        # remove NaNs
        nanmask = np.isfinite(unix_times)
        itable = itable[nanmask]
        # raise error if we have no valid files left
        if np.sum(nanmask) == 0:
            emsg = 'No other valid files {0}/{1} (All files have invalid times)'
            eargs = [np.sum(nanmask), len(nanmask)]
            WLOG(p, 'error', emsg.format(*eargs))
        # get file list
        filelist = itable['ABSFILENAMES']
        # get file types that are left
        filetypes = np.unique(itable[p['KW_EXT_TYPE'][0]])
        # return file list
        return list(filelist), list(filetypes)


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
    # get the image size
    dim1, dim2 = image.shape
    # get parameters from p
    curvefit = p['BAD_REGION_FIT']
    med_size = p['BAD_REGION_MED_SIZE']
    threshold = p['BAD_REGION_THRESHOLD']
    kernel_size = p['BAD_REGION_KERNEL_SIZE']
    med_size2 = p['BAD_REGION_MED_SIZE2']
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
    WLOG(p, '', '   - Straightening interpolation image')
    # loop around all x pixels and shift pixels by interpolating with a spline
    for xi in range(dim2):
        # produce the universal spline fit
        splinefit = IUVSpline(xpixfit, image2[:, xi], k=1)
        # apply the spline fit with the shift and write to the image
        image2[:, xi] = splinefit(xpixfit + pixshift[xi])
    # -------------------------------------------------------------------------
    # log progress
    WLOG(p, '', '   - Applying median filter to interpolation image')
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
    WLOG(p, '', '   - Applying convolution to interpolation image')
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
    WLOG(p, '', '   - Un-straightening interpolation image')
    # make sure all NaNs are 0
    image2 = np.where(np.isfinite(image2), image2, np.zeros_like(image2))
    image = np.where(np.isfinite(image), image, np.zeros_like(image))
    # add the curvature back in (again by interpolating with a spline)
    for xi in range(dim2):
        # produce the universal spline fit
        splinefit = IUVSpline(xpixfit, image2[:, xi], k=1)
        # apply the spline fit with the shift and write to the image
        image2[:, xi] = splinefit(xpixfit - pixshift[xi])
    # -------------------------------------------------------------------------
    # log progress
    WLOG(p, '', '   - Calculating good and bad pixels (from ratio)')
    # calculate the ratio between original image and interpolated image
    ratio = image/image2
    # set all ratios greater than 1 to the inverse (reflect around 1)
    with warnings.catch_warnings(record=True) as _:
        rmask = ratio > 1
        ratio[rmask] = 1.0/ratio[rmask]
    # create a weight image
    weights = np.zeros_like(image, dtype=float)
    # decide which pixels are good and which pixels are bad
    with warnings.catch_warnings(record=True) as _:
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

    :param p: parameter dictionary, ParamDict containing constants
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
            WLOG(p, 'error', [emsg1, emsg2])
        else:
            if p['PROCESSED_SUFFIX'] in filename:
                p['PREPROCESSED'] = True
            else:
                p['PREPROCESSED'] = False
    # if not pre-processedrotate
    if not p['PREPROCESSED']:
        # log warning
        wmsg = 'Warning: Using non-preprocessed file!'
        WLOG(p, 'warning', wmsg)
        # get rotation
        rotation = p['RAW_TO_PP_ROTATION']
        # rotate and return image
        return rotate(image, rotation)
    # else return image
    else:
        return image


def check_fiber_ext_type(p, itable, allowed_file_types):
    # define mask4 as a set of Trues (i.e. we allow all by default)
    mask4 = np.ones(len(itable), dtype=bool)
    # loop around the different types
    for ext_type_ex in p['DRIFT_PEAK_OUTPUT_EXCEPT']:
        # check ext_type in allowed types
        if ext_type_ex not in allowed_file_types:
            continue
        # check fiber is correct if it isn't set all of this EXT_TYPE to False
        if p['FIBER'] != p['DRIFT_PEAK_OUTPUT_EXCEPT'][ext_type_ex]:
            tmp = itable[p['KW_EXT_TYPE'][0]] == ext_type_ex
            mask4[tmp] = False
    # return mask4
    return mask4


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


def get_full_flat(p):
    # get parameters from p
    filename = p['BADPIX_FULL_FLAT']
    # construct filepath
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.BADPIX_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    absfilename = os.path.join(datadir, filename)
    # check that filepath exists
    if not os.path.exists(absfilename):
        emsg = 'badpix full flat ({0}) not found in {1}. Please correct.'
        WLOG(p, 'error', emsg.format(filename, datadir))
    # read image
    mdata, _, _, _ = spirouFITS.readimage(p, absfilename, kind='FULLFLAT')
    # return image
    return mdata


def get_hot_pixels(p):
    # get full badpixel file
    full_badpix = get_full_flat(p)
    # get shape of full badpixel file
    dim1, dim2 = full_badpix.shape

    # get the med_size
    med_size = p['PP_CORRUPT_MED_SIZE']
    # get the hot pix threshold
    hot_thres = p['PP_CORRUPT_HOT_THRES']

    # get size of dark region
    pixels_per_amp = dim2 // p['TOTAL_AMP_NUM']
    dark_size = p['NUMBER_DARK_AMP'] * pixels_per_amp

    # mask the full_badpix (do not include dark area or edges)
    full_badpix[:, dark_size:] = np.nan
    full_badpix[:med_size, :] = np.nan
    full_badpix[:, :med_size] = np.nan
    full_badpix[-med_size:, :] = np.nan
    full_badpix[:, -med_size:] = np.nan

    # median out full band structures
    with warnings.catch_warnings(record=True) as _:
        for ix in range(med_size, dark_size):
            full_badpix[:, ix] -= np.nanmedian(full_badpix[:, ix])
        for iy in range(dim1):
            full_badpix[iy, :] -= np.nanmedian(full_badpix[iy, :])

    full_badpix[~np.isfinite(full_badpix)] = 0.0

    # locate hot pixels in the full bad pix
    yhot, xhot = np.where(full_badpix > hot_thres)

    # return the hot pixel indices
    return [yhot, xhot]


def test_for_corrupt_files(p, image, hotpix):
    # get the med_size
    med_size = p['PP_CORRUPT_MED_SIZE']
    # get hte percentile values
    rms_percentile = p['PP_RMS_PERCENTILE']
    percent_thres = p['PP_LOWEST_RMS_PERCENTILE']
    # get shape of full badpixel file
    dim1, dim2 = image.shape
    # get size of dark region
    pixels_per_amp = dim2 // p['TOTAL_AMP_NUM']
    dark_size = p['NUMBER_DARK_AMP'] * pixels_per_amp
    # get the x and y hot pixel values
    yhot, xhot = hotpix

    # get median hot pixel box
    med_hotpix = np.zeros([2 * med_size + 1, 2 * med_size + 1])

    # loop around x
    for dx in range(-med_size, med_size + 1):
        # loop around y
        for dy in range(-med_size, med_size + 1):
            # define position in median box
            posx = dx + med_size
            posy = dy + med_size
            # get the hot pixel values at position in median box
            data_hot = np.array(image[yhot + dx, xhot + dy])
            # median the data_hot for this box position
            med_hotpix[posx, posy] = np.nanmedian(data_hot)

    # get dark ribbon
    dark_ribbon = image[:, 0:dark_size]
    # you should not have an excess in odd/even RMS of pixels
    rms2 = np.nanmedian(np.abs(dark_ribbon[0:-1, :] - dark_ribbon[1:, :]))
    rms3 = np.nanmedian(np.abs(dark_ribbon[:, 0:-1] - dark_ribbon[:, 1:]))
    med0 = np.nanmedian(dark_ribbon, axis=0)
    med1 = np.nanmedian(dark_ribbon, axis=1)

    rms0 = np.nanmedian(np.abs(med0 - np.nanmedian(med0)))
    rms1 = np.nanmedian(np.abs(med1 - np.nanmedian(med1)))

    # get the 'rms_percentile' percentile value
    percentile_cut = np.nanpercentile(image, rms_percentile)
    # make sure the percentile does not fall below a lower level
    if percentile_cut < percent_thres:
        percentile_cut = percent_thres

    # normalise the rms by the percentile cut
    rms0 = rms0 / percentile_cut
    rms1 = rms1 / percentile_cut
    rms2 = rms2 / percentile_cut
    rms3 = rms3 / percentile_cut

    # normalise med_hotpix to it's own median
    res = med_hotpix - np.nanmedian(med_hotpix)
    # work out an rms
    rms = np.nanmedian(np.abs(res))
    # signal to noise = res / rms
    snr_hotpix = res[med_size, med_size] / rms

    # return test values
    return snr_hotpix, [rms0, rms1, rms2, rms3]


# =============================================================================
# Define Image correction functions
# =============================================================================
# noinspection PyTypeChecker
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
    # noinspection PyBroadException
    try:
        image = np.array(image)
    except Exception as _:
        emsg1 = '"image" is not a valid numpy array'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(pp, 'error', [emsg1, emsg2])
    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = np.nanmedian(fimage)
    # get the 5th and 95th percentile qmin
    try:
        # noinspection PyTypeChecker
        qmin, qmax = np.nanpercentile(fimage, [pp['DARK_QMIN'], pp['DARK_QMAX']])
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG(pp, 'error', [e.message, emsg])
        qmin, qmax = None, None
    # get the histogram for flattened data
    try:
        histo = np.histogram(fimage, bins=pp['HISTO_BINS'],
                             range=(pp['HISTO_RANGE_LOW'],
                                    pp['HISTO_RANGE_HIGH']),
                             density=True)
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG(pp, 'error', [e.message, emsg])
        histo = None
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    wargs = ['In {0}'.format(image_name), dadead, med, pp['DARK_QMIN'],
             pp['DARK_QMAX'], qmin, qmax]
    wmsg = ('{0:12s}: Frac dead pixels= {1:.4f} % - Median= {2:.3f} ADU/s - '
            'Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s')
    WLOG(pp, 'info', wmsg.format(*wargs))
    # add required variables to pp
    source = '{0}/{1}'.format(__NAME__, 'measure_dark()')

    pp['histo_{0}'.format(short_name)] = np.array(histo)
    pp.set_source('histo_{0}'.format(short_name), source)

    pp['med_{0}'.format(short_name)] = float(med)
    pp.set_source('med_{0}'.format(short_name), source)

    pp['dadead_{0}'.format(short_name)] = float(dadead)
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
    # get constants from p
    use_sky = p['USE_SKYDARK_CORRECTION']
    skydark_only = p['USE_SKYDARK_ONLY']
    # check number of frames
    if nfiles is None:
        nfiles = p['NBFRAMES']

    # -------------------------------------------------------------------------
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
            WLOG(p, 'error', [e.message, emsg])
            cdb, acqtime = None, None

    # -------------------------------------------------------------------------
    # try to read 'DARK' from cdb
    if 'DARKM' in cdb:
        darkfile = os.path.join(p['DRS_CALIB_DB'], cdb['DARKM'][1])
        darktime = float(cdb['DARKM'][-1])
    else:
        darkfile = None
        darktime = None
    # try to read 'SKYDARK' from cdb
    if 'SKYDARK' in cdb:
        skydarkfile = os.path.join(p['DRS_CALIB_DB'], cdb['SKYDARK'][1])
        skytime = float(cdb['SKYDARK'][-1])
    else:
        skydarkfile = None
        skytime = None

    # -------------------------------------------------------------------------
    # load the correct dark image
    # -------------------------------------------------------------------------
    # setup logic used in multiple
    cond1 = skydarkfile is not None
    cond2 = darkfile is not None
    # if we have both darkfile and skydarkfile use the closest
    if use_sky and cond1 and cond2 and (not skydark_only):
        # find closest to obs time
        pos = np.argmin(abs(np.array([skytime, darktime]) - acqtime))
        if pos == 0:
            use_file, use_type = str(skydarkfile), 'SKY'
        else:
            use_file, use_type = str(darkfile),  'DARK'
    # else if we only have sky
    elif use_sky and cond1:
        use_file, use_type = str(skydarkfile), 'SKY'
    # else if only have a dark
    elif cond2:
        use_file, use_type = str(darkfile), 'DARK'
    # else we don't have either --> error
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
        if use_sky and (not skydark_only):
            emsg1 = 'No valid DARK/SKYDARK in calibDB {0} ' + extstr
        elif use_sky and skydark_only:
            emsg1 = 'No valid SKYDARK in calibDB {0} ' + extstr
        else:
            emsg1 = 'No valid DARK in calibDB {0} ' + extstr
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1.format(masterfile, acqtime), emsg2])
        use_file, use_type = None, None
    # -------------------------------------------------------------------------
    # do dark using correct file
    darkimage, dhdr, _, _ = spirouFITS.read_raw_data(p, use_file, imageext=0)
    # Read dark file
    wmsg = [use_type, use_file]
    WLOG(p, '', 'Doing Dark Correction using {0}: {1}'.format(*wmsg))
    corrected_image = image - (darkimage * nfiles)
    # -------------------------------------------------------------------------
    # get the dark filename (from header)
    p['DARKFILE'] = os.path.basename(use_file)
    p.set_source('DARKFILE', func_name)

    # finally return datac
    if return_dark:
        return p, corrected_image, darkimage
    else:
        return p, corrected_image


def get_badpixel_map(p, header=None, quiet=False):
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

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, the program name for logging
        May contain:
            calibDB: dictionary, the calibration database

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
            WLOG(p, 'error', [e.message, emsg])
            cdb, acqtime = None, None

    # try to read 'BADPIX' from cdb
    if 'BADPIX' in cdb:
        badpixfile = os.path.join(p['DRS_CALIB_DB'], cdb['BADPIX'][1])
        if not quiet:
            WLOG(p, '', 'Doing Bad Pixel Correction using ' + badpixfile)
        badpixmask, bhdr, nx, ny = spirouFITS.read_raw_data(p, badpixfile)
        return badpixmask, bhdr, badpixfile
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
        WLOG(p, 'error', [emsg1.format(masterfile, acqtime), emsg2])


def get_background_map(p, header=None, quiet=False):
    """
    Get the background map from the calibDB

        Must contain at least:
                calibDB: dictionary, the calibration database dictionary
                         (if not in "p" we construct it and need "max_time_unix"
                max_time_unix: float, the unix time to use as the time of
                                reference (used only if calibDB is not defined)
                log_opt: string, log option, normally the program name
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, the program name for logging
        May contain:
            calibDB: dictionary, the calibration database

    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage

    :return: badpixmask: numpy array (2D), the bad pixel mask
    """
    func_name = __NAME__ + '.get_background_map()'
    key = 'BKGRDMAP'
    outfile = 'BKGRDFILE'
    if not quiet:
        WLOG(p, '', 'Doing Background Correction using ' + p[outfile])
    # load calibration file
    p, ofile, ohdr = load_calib_file(p, header, key, outfile, func_name)
    return p, ofile, ohdr


def correct_for_badpix(p, image, header, return_map=False, quiet=True):
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
    :param return_map: bool, if True returns bad pixel map else returns
                       corrected image

    :returns: numpy array (2D), the corrected image where all bad pixels are
              set to zeros or the bad pixel map (if return_map = True)
    """
    func_name = __NAME__ + '.correct_for_baxpix()'
    # get badpixmask
    badpixmask, bhdr, badfile = get_badpixel_map(p, header, quiet=quiet)
    # create mask from badpixmask
    mask = np.array(badpixmask, dtype=bool)
    # get bad pixel file
    p['BADPFILE'] = os.path.basename(badfile)
    p.set_source('BADPFILE', func_name)
    # return
    if return_map:
        return p, mask
    else:
        # log doing bad pixel correction
        WLOG(p, '', 'Doing Bad Pixel Correction {0}'.format(badfile))
        # correct image (set bad pixels to zero)
        corrected_image = np.array(image)
        corrected_image[mask] = np.nan
        # finally return corrected_image
        return p, corrected_image


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
    :param method: string, "new" or "old" if "new" uses np.nanpercentile else
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
    WLOG(p, '', 'Normalising the flat')

    # get used percentile
    if percentile is None:
        try:
            percentile = p['BADPIX_NORM_PERCENTILE']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [e.message, emsg])

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
            WLOG(p, 'error', [e.message, emsg])

    # create storage for median-filtered flat image
    image_med = np.zeros_like(image)

    # loop around x axis
    for i_it in range(image.shape[1]):
        # x-spatial filtering and insert filtering into image_med array
        image_med[i_it, :] = filters.median_filter(image[i_it, :], wmed)

    if method == 'new':
        # get the 90th percentile of median image
        norm = np.nanpercentile(image_med[np.isfinite(image_med)], percentile)

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
    WLOG(p, '', 'Looking for bad pixels')
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
            WLOG(p, 'error', [e.message, emsg])

    # maxi differential pixel response relative to the expected value
    try:
        cut_ratio = p['BADPIX_FLAT_CUT_RATIO']
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [e.message, emsg])
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
        WLOG(p, 'error', [e.message, emsg])
        illum_cut = None
    # hotpix. Max flux in ADU/s to be considered too hot to be used
    try:
        max_hotpix = p['BADPIX_MAX_HOTPIX']
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [e.message, emsg])
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
        WLOG(p, 'error', [emsg1.format(*eargs), emsg2])
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
    badpix_stats = [(np.sum(badpix_dark) / np.array(badpix_dark).size) * 100,
                    (np.sum(badpix_flat) / np.array(badpix_flat).size) * 100,
                    (np.sum(~valid_dark) / np.array(valid_dark).size) * 100,
                    (np.sum(~valid_flat) / np.array(valid_flat).size) * 100,
                    (np.sum(badpix_map) / np.array(badpix_map).size) * 100]

    for it in range(len(text)):
        WLOG(p, '', text[it].format(badpix_stats[it]))
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
    # log that we are looking for bad pixels
    WLOG(p, '', 'Looking for bad pixels in full flat image')
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
        WLOG(p, 'error', emsg.format(filename, datadir))
    # read image
    mdata, _, _, _ = spirouFITS.readimage(p, absfilename, kind='FULLFLAT')

    if image.shape != mdata.shape:
        wmsg = 'Full flat shape = {0}, image shape = {1}'
        WLOG(p, 'warning', wmsg.format(mdata.shape, image.shape))
    # apply threshold
    # mask = np.rot90(mdata, -1) < threshold
    mask = np.abs(np.rot90(mdata, -1)-1) > threshold

    # -------------------------------------------------------------------------
    # log results
    badpix_stats = (np.sum(mask) / np.array(mask).size) * 100
    text = 'Fraction of un-illuminated pixels in engineering flat {0:.4f} %'
    WLOG(p, '', text.format(badpix_stats))

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
    # storage for "nbcos" (number of cosmic rays detected)
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
        nanmask = np.isfinite(lloc['CENT1']) & np.isfinite(lloc['CENT2'])
        # interpolate the pixels on to the extracted centers
        cent1i = np.interp(os_pixels, pixels[nanmask], lloc['CENT1'][nanmask])
        cent2i = np.interp(os_pixels, pixels[nanmask], lloc['CENT2'][nanmask])
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
        WLOG(pp, '', wmsg.format(*wargs))
        # save tilt angle to lloc
        lloc['TILT'][int(order_num / 2)] = angle
    # return the lloc
    return lloc


def load_shape_x(p, hdr):
    func_name = __NAME__ + '.load_shape_x()'
    key = 'SHAPEX'
    outfile = 'SHAPEXFILE'
    p, ofile, ohdr = load_calib_file(p, hdr, key, outfile, func_name)
    return p, ofile


def load_shape_y(p, hdr):
    func_name = __NAME__ + '.load_shape_y()'
    key = 'SHAPEY'
    outfile = 'SHAPEYFILE'
    p, ofile, ohdr = load_calib_file(p, hdr, key, outfile, func_name)
    return p, ofile


def load_shape_local(p, hdr):
    func_name = __NAME__ + '.load_shape_local()'
    key = 'SHAPE'
    outfile = 'SHAPEFILE'
    p, ofile, ohdr = load_calib_file(p, hdr, key, outfile, func_name)
    # vector in this case is 1D (dx, dy, A, B, C, D) so return only a
    #   1D vector (as well as p)
    return p, ofile[0]


def load_master_fp(p, hdr):
    func_name = __NAME__ + '.load_master_fp()'
    key = 'FPMASTER'
    outfile = 'FPMASTERFILE'
    p, ofile, ohdr = load_calib_file(p, hdr, key, outfile, func_name)
    return p, ofile


def load_tapas(p, hdr):
    func_name = __NAME__ + '.load_tapas()'
    key = 'TELL_MOLE'
    outfile = 'TAPASFILE'
    p, ofile, ohdr = load_calib_table(p, hdr, key, outfile, func_name)
    return p, ofile


def load_thermal(p, hdr, fiber):
    func_name = __NAME__ + '.load_thermal()'
    key = 'THERMAL_{0}'.format(fiber)
    outfile = 'THERMALFILE_{0}'.format(fiber)
    p, ofile, ohdr = load_calib_file(p, hdr, key, outfile, func_name)
    return p, ofile


def load_calib_file(p, header, key, outfile, func_name=None, ext=0):
    if func_name is None:
        func_name = __NAME__ + '.load_calib_file()'
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
            WLOG(p, 'error', [e.message, emsg])
            cdb, acqtime = None, None
    # try to read 'BADPIX' from cdb
    if key in cdb:
        calibfile = os.path.join(p['DRS_CALIB_DB'], cdb[key][1])
        calibdata, calibhdr, _, _ = spirouFITS.read_raw_data(p, calibfile,
                                                             imageext=ext)
        p[outfile] = calibfile
        p.set_source(outfile, func_name)
        # return parameter dictionary and shape file
        return p, calibdata, calibhdr
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
        emsg1 = 'No valid {2} in calibDB {0} ' + extstr
        emsg2 = '    function = {0}'.format(func_name)
        eargs = [masterfile, acqtime, key]
        WLOG(p, 'error', [emsg1.format(*eargs), emsg2])


def load_calib_table(p, header, key, outfile, func_name=None, ext=0):
    if func_name is None:
        func_name = __NAME__ + '.load_calib_file()'
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
            WLOG(p, 'error', [e.message, emsg])
            cdb, acqtime = None, None
    # try to read 'BADPIX' from cdb
    if key in cdb:
        calibfile = os.path.join(p['DRS_CALIB_DB'], cdb[key][1])
        calibdata = spirouTable.read_table(p, calibfile, fmt='fits')
        p[outfile] = calibfile
        p.set_source(outfile, func_name)
        # return parameter dictionary and shape file
        return p, calibdata, None
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
        emsg1 = 'No valid {2} in calibDB {0} ' + extstr
        emsg2 = '    function = {0}'.format(func_name)
        eargs = [masterfile, acqtime, key]
        WLOG(p, 'error', [emsg1.format(*eargs), emsg2])


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
    atc = nanpolyfit(xfit, lloc['TILT'], pp['IC_TILT_FIT'])[::-1]
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
        WLOG(p, 'error', [emsg1, emsg2])
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
        WLOG(p, 'error', [emsg1, emsg2])
        linefile = ''
    # check that line file exists
    if not os.path.exists(linefile):
        emsg1 = 'Line list file={0} does not exist.'.format(linefile)
        emsg2 = '    function={0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # read filename as a table (no header so need data_start=0)
    linetable = spirouTable.read_table(p, linefile,
                                       fmt='ascii.tab',
                                       colnames=['ll', 'amp', 'kind'],
                                       data_start=0)
    # push columns into numpy arrays and force to floats
    ll = np.array(linetable['ll'], dtype=float)
    amp = np.array(linetable['amp'], dtype=float)
    # log that we have opened line file
    wmsg = 'List of {0} HC lines read in file {1}'
    WLOG(p, '', wmsg.format(len(ll), linefile))
    # return line list and amps
    return ll, amp


def read_cavity_length(p, filename=None):

    func_name = __NAME__ + '.read_cavity_length()'
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.WAVELENGTH_CATS_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # assign line file
    if filename is not None:
        # if filename is absolute path and file exists use this
        if os.path.exists(filename):
            cavityfile = filename
        # if filename is defined but doesn't exist try to see if it is in the
        # data folder
        else:
            cavityfile = os.path.join(datadir, filename)
        cavityfilename = os.path.basename(filename)
    else:
        cavityfilename = spirouConfig.Constants.CAVITY_LENGTH_FILE()
        cavityfile = os.path.join(datadir, cavityfilename)
    # check that line file exists
    if not os.path.exists(cavityfile):
        emsg1 = 'Cavity file={0} does not exist.'.format(cavityfile)
        emsg2 = '    function={0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # read filename as a table (no header so need data_start=0)
    colnames = ['NTH_ORDER', 'WAVELENGTH_COEFF']
    table = spirouTable.read_table(p, cavityfile, fmt='ascii',
                                   colnames=colnames, data_start=0)
    # push columns into numpy arrays and force to floats
    coeff_nums = np.array(table['NTH_ORDER'], dtype=float)
    coeff_values = np.array(table['WAVELENGTH_COEFF'], dtype=float)
    ncoeff = len(coeff_nums)
    # log that we have opened line file
    wmsg = 'List of {0} cavity length coefficients read in file {1}'
    wargs = [ncoeff, cavityfilename]
    WLOG(p, '', wmsg.format(*wargs))

    # reformat into well behaved array
    poly_cavity = np.zeros(ncoeff)
    for it in range(ncoeff):
        poly_cavity[it] = coeff_values[it]
    # flip to match
    poly_cavity = poly_cavity[::-1]

    # return line list and amps
    return poly_cavity


# =============================================================================
# Shape functions
# =============================================================================
# TODO: Remove old shape map
def get_shape_map_old(p, loc):
    func_name = __NAME__ + '.get_shape_map()'
    # get constants from p
    nbanana = p['SHAPE_NUM_ITERATIONS']
    width = p['SHAPE_ABC_WIDTH']
    nsections = p['SHAPE_NSECTIONS']
    large_angle_range = p['SHAPE_LARGE_ANGLE_RANGE']
    small_angle_range = p['SHAPE_SMALL_ANGLE_RANGE']
    sigclipmax = p['SHAPE_SIGMACLIP_MAX']
    med_filter_size = p['SHAPE_MEDIAN_FILTER_SIZE']
    min_good_corr = p['SHAPE_MIN_GOOD_CORRELATION']
    # get data from loc
    data1 = np.array(loc['DATA'])
    nbo = loc['NUMBER_ORDERS'] // 2
    acc = loc['ACC']
    # get the dimensions
    dim0, dim1 = loc['DATA'].shape
    master_dxmap = np.zeros_like(data1)
    # define storage for plotting
    slope_deg_arr, slope_arr, skeep_arr = [], [], []
    xsec_arr, ccor_arr = [], []
    ddx_arr, dx_arr = [], []
    dypix_arr, cckeep_arr = [], []

    # -------------------------------------------------------------------------
    # iterating the correction, from coarser to finer
    for banana_num in range(nbanana):
        # ---------------------------------------------------------------------
        # we use the code that will be used by the extraction to ensure
        # that slice images are as straight as can be
        # ---------------------------------------------------------------------
        # if the map is not zeros, we use it as a starting point
        if np.sum(master_dxmap != 0) != 0:
            data2 = spirouEXTOR.DeBananafication(p, data1, dx=master_dxmap)
            # if this is not the first iteration, then we must be really close
            # to a slope of 0
            range_slopes_deg = small_angle_range
        else:
            data2 = np.array(data1)
            # starting point for slope exploration
            range_slopes_deg = large_angle_range
        # expressed in pixels, not degrees
        range_slopes = np.tan(np.deg2rad(np.array(range_slopes_deg)))
        # set up iteration storage
        slope_deg_arr_i, slope_arr_i, skeep_arr_i = [], [], []
        xsec_arr_i, ccor_arr_i = [], []
        ddx_arr_i, dx_arr_i = [], []
        dypix_arr_i,  cckeep_arr_i = [], []
        # ---------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):
            # -----------------------------------------------------------------
            # Log progress
            wmsg = 'Banana iteration: {0}: Order {1}/{2} '
            wargs = [banana_num + 1, order_num + 1, nbo]
            WLOG(p, '', wmsg.format(*wargs))
            # -----------------------------------------------------------------
            # create the x pixel vector (used with polynomials to find
            #    order center)
            xpix = np.arange(dim1)
            # y order center positions (every other one)
            ypix = np.polyval(acc[order_num * 2][::-1], xpix)
            # defining a ribbon that will contain the straightened order
            ribbon = np.zeros([width, dim1])
            # get the widths
            widths = np.arange(width) - width / 2.0
            # get all bottoms and tops
            bottoms = ypix - width/2 - 2
            tops = ypix + width/2 + 2
            # splitting the original image onto the ribbon
            for ix in range(dim1):
                # define bottom and top that encompasses all 3 fibers
                bottom = int(bottoms[ix])
                top = int(tops[ix])
                sx = np.arange(bottom, top)
                # calculate spline interpolation and ribbon values
                if bottom > 0:
                    spline = IUVSpline(sx, data2[bottom:top, ix], ext=1, k=1)
                    ribbon[:, ix] = spline(ypix[ix] + widths)
            # normalizing ribbon stripes to their median abs dev
            for iw in range(width):
                norm = np.nanmedian(np.abs(ribbon[iw, :]))
                ribbon[iw, :] = ribbon[iw, :] / norm
            # range explored in slopes
            # TODO: question Where does the /8.0 come from?
            sfactor = (range_slopes[1] - range_slopes[0]) / 8.0
            slopes = (np.arange(9) * sfactor) + range_slopes[0]
            # log the range slope exploration
            wmsg = '\tRange slope exploration: {0:.3f} -> {1:.3f} deg'
            wargs = [range_slopes_deg[0], range_slopes_deg[1]]
            WLOG(p, '', wmsg.format(*wargs))
            # -------------------------------------------------------------
            # the domain is sliced into a number of sections, then we
            # find the tilt that maximizes the RV content
            xsection = dim1 * (np.arange(nsections) + 0.5) / nsections
            dxsection = np.repeat([np.nan], len(xsection))
            keep = np.zeros(len(dxsection), dtype=bool)
            ribbon2 = np.array(ribbon)
            # RV content per slice and per slope
            rvcontent = np.zeros([len(slopes), nsections])
            # loop around the slopes
            for islope, slope in enumerate(slopes):
                # copy the ribbon
                ribbon2 = np.array(ribbon)
                # interpolate new slope-ed ribbon
                for iw in range(width):
                    # get the ddx value
                    ddx = (iw - width/2.0) * slope
                    # get the spline
                    spline = IUVSpline(xpix, ribbon[iw, :], ext=1)
                    # calculate the new ribbon values
                    ribbon2[iw, :] = spline(xpix + ddx)
                # record the profile of the ribbon
                profile = np.nanmedian(ribbon2, axis=0)
                # loop around the sections to record rv content
                for nsection in range(nsections):
                    # sum of integral of derivatives == RV content.
                    # This should be maximal when the angle is right
                    start = nsection * dim1//nsections
                    end = (nsection + 1) * dim1//nsections
                    grad = np.gradient(profile[start:end])
                    rvcontent[islope, nsection] = np.nansum(grad ** 2)
            # -------------------------------------------------------------
            # we find the peak of RV content and fit a parabola to that peak
            for nsection in range(nsections):
                # we must have some RV content (i.e., !=0)
                if np.nanmax(rvcontent[:, nsection]) != 0:
                    vec = np.ones_like(slopes)
                    vec[0], vec[-1] = 0, 0
                    # get the max pixel
                    maxpix = np.nanargmax(rvcontent[:, nsection] * vec)
                    # max RV and fit on the neighbouring pixels
                    xff = slopes[maxpix - 1: maxpix + 2]
                    yff = rvcontent[maxpix - 1: maxpix + 2, nsection]
                    coeffs = nanpolyfit(xff, yff, 2)
                    # if peak within range, then its fine
                    dcoeffs = -0.5 * coeffs[1] / coeffs[0]
                    if np.abs(dcoeffs) < 1:
                        dxsection[nsection] = dcoeffs
                # we sigma-clip the dx[x] values relative to a linear fit
                keep = np.isfinite(dxsection)
            # -------------------------------------------------------------
            # sigma clip
            sigmax = np.inf
            while sigmax > sigclipmax:
                # recalculate the fit
                coeffs = nanpolyfit(xsection[keep], dxsection[keep], 2)
                # get the residuals
                res = dxsection - np.polyval(coeffs, xsection)
                # normalise residuals
                res = res - np.nanmedian(res[keep])
                res = res / np.nanmedian(np.abs(res[keep]))
                # calculate the sigma
                sigmax = np.nanmax(np.abs(res[keep]))
                # do not keep bad residuals
                with warnings.catch_warnings(record=True) as _:
                    keep &= np.abs(res) < sigclipmax
            # -------------------------------------------------------------
            # fit a 2nd order polynomial to the slope vx position
            #    along order
            coeffs = nanpolyfit(xsection[keep], dxsection[keep], 2)
            # log slope at center
            s_xpix = dim1//2
            s_ypix = np.rad2deg(np.arctan(np.polyval(coeffs, s_xpix)))
            wmsg = '\tSlope at pixel {0}: {1:.5f} deg'
            wargs = [s_xpix, s_ypix]
            WLOG(p, '', wmsg.format(*wargs))
            # get slope for full range
            slope = np.polyval(coeffs, np.arange(dim1))
            # -------------------------------------------------------------
            # append to storage (for plotting)
            xsec_arr_i.append(np.array(xsection))
            slope_deg_arr_i.append(np.rad2deg(np.arctan(dxsection)))
            slope_arr_i.append(np.rad2deg(np.arctan(slope)))
            skeep_arr_i.append(np.array(keep))
            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the
            yfit = np.polyval(coeffs, xpix)
            #    slicer profile
            for iw in range(width):
                # get the x shift
                ddx = (iw - width/2.0) * yfit
                # calculate the spline at this width
                spline = IUVSpline(xpix, ribbon[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon2[iw, :] = spline(xpix + ddx)

            # median FP peak profile. We will cross-correlate each
            # row of the ribbon with this
            profile = np.nanmedian(ribbon2, axis=0)
            medianprofile = filters.median_filter(profile, med_filter_size)
            profile = profile - medianprofile

            # -------------------------------------------------------------
            # cross-correlation peaks of median profile VS position
            #    along ribbon
            # reset dx and ddx
            dx = np.repeat([np.nan], width)
            # TODO: Question: Why -3 to 4 where does this come from?
            ddx = np.arange(-3, 4)
            # set up cross-correlation storage
            ccor = np.zeros([width, len(ddx)], dtype=float)
            # loop around widths
            for iw in range(width):
                for jw in range(len(ddx)):
                    # calculate the peasron r coefficient
                    xff = ribbon2[iw, :]
                    yff = np.roll(profile, ddx[jw])
                    pearsonr_value = stats.pearsonr(xff, yff)[0]
                    # push into cross-correlation storage
                    ccor[iw, jw] = pearsonr_value
                # fit a gaussian to the cross-correlation peak
                xvec = ddx
                yvec = ccor[iw, :]
                with warnings.catch_warnings(record=True) as _:
                    gcoeffs, _ = spirouMath.gauss_fit_nn(xvec, yvec, 4)
                # check that max value is good
                if np.nanmax(ccor[iw, :]) > min_good_corr:
                    dx[iw] = gcoeffs[1]
            # -------------------------------------------------------------
            # remove any offset in dx, this would only shift the spectra
            dx = dx - np.nanmedian(dx)
            dypix = np.arange(len(dx))
            with warnings.catch_warnings(record=True):
                keep = np.abs(dx) < 1
            keep &= np.isfinite(dx)
            # -------------------------------------------------------------
            # if the first pixel is nan and the second is OK,
            #    then for continuity, pad
            if (not keep[0]) and keep[1]:
                keep[0] = True
                dx[0] = dx[1]
            # same at the other end
            if (not keep[-1]) and keep[-2]:
                keep[-1] = True
                dx[-1] = dx[-2]
            # -------------------------------------------------------------
            # append to storage for plotting
            ccor_arr_i.append(np.array(ccor))
            ddx_arr_i.append(np.array(ddx))
            dx_arr_i.append(np.array(dx))
            dypix_arr_i.append(np.array(dypix))
            cckeep_arr_i.append(np.array(keep))
            # -------------------------------------------------------------
            # spline everything onto the master DX map
            spline = IUVSpline(dypix[keep], dx[keep], ext=0)
            # for all field positions along the order, we determine the
            #    dx+rotation values and update the master DX map
            fracs = ypix - np.fix(ypix)
            widths = np.arange(width)

            for ix in range(dim1):
                # get the fraction missed
                # frac = ypix[ix] - np.fix(ypix[ix])
                # get dx0 with slope factor added
                dx0 = (widths - width // 2 + (1 - fracs[ix])) * slope[ix]
                # get the ypix at this value
                ypix2 = int(ypix[ix]) + np.arange(-width//2, width//2)
                # get the ddx
                ddx = spline(widths - fracs[ix])
                # set the zero shifts to NaNs
                ddx[ddx == 0] = np.nan
                # only set positive ypixels
                pos_y_mask = ypix2 >= 0
                # if we have some values add to master DX map
                if np.sum(pos_y_mask) != 0:
                    # get positions in y
                    positions = ypix2[pos_y_mask]
                    # get shifts combination od ddx and dx0 correction
                    shifts = (ddx + dx0)[pos_y_mask]
                    # apply shifts to master dx map at correct positions
                    master_dxmap[positions, ix] += shifts
        # ---------------------------------------------------------------------
        # append to storage
        slope_deg_arr.append(slope_deg_arr_i), slope_arr.append(slope_arr_i)
        skeep_arr.append(skeep_arr_i), xsec_arr.append(xsec_arr_i)
        ccor_arr.append(ccor_arr_i), ddx_arr.append(ddx_arr_i)
        dx_arr.append(dx_arr_i), dypix_arr.append(dypix_arr_i)
        cckeep_arr.append(cckeep_arr_i)

    # push storage into loc
    loc['SLOPE_DEG'], loc['SLOPE'] = slope_deg_arr, slope_arr
    loc['S_KEEP'], loc['XSECTION'] = skeep_arr, xsec_arr
    loc['CCOR'], loc['DDX'] = ccor_arr, ddx_arr
    loc['DX'], loc['DYPIX'] = dx_arr, dypix_arr
    loc['C_KEEP'] = cckeep_arr
    # add DXMAP to loc
    loc['DXMAP'] = master_dxmap
    # set source
    keys = ['SLOPE_DEG', 'SLOPE', 'S_KEEP', 'XSECTION', 'CCOR', 'DDX',
            'DX', 'DYPIX', 'C_KEEP', 'DXMAP']
    loc.set_sources(keys, func_name)
    # return loc
    return loc


def get_x_shape_map(p, loc):
    func_name = __NAME__ + '.get_x_shape_map()'
    # get constants from p
    nbanana = p['SHAPE_NUM_ITERATIONS']
    width = p['SHAPE_ABC_WIDTH']
    nsections = p['SHAPE_NSECTIONS']
    large_angle_range = p['SHAPE_LARGE_ANGLE_RANGE']
    small_angle_range = p['SHAPE_SMALL_ANGLE_RANGE']
    sigclipmax = p['SHAPE_SIGMACLIP_MAX']
    med_filter_size = p['SHAPE_MEDIAN_FILTER_SIZE']
    min_good_corr = p['SHAPE_MIN_GOOD_CORRELATION']
    short_medfilt_width = p['SHAPE_SHORT_DX_MEDFILT_WID']
    long_medfilt_width = p['SHAPE_LONG_DX_MEDFILT_WID']

    plot_on = p.get(p['PLOT_PER_ORDER'], False)
    # get data from loc
    hcdata1 = np.array(loc['HCDATA1'])
    fpdata1 = np.array(loc['FPDATA1'])
    nbo = loc['NUMBER_ORDERS'] // 2
    acc = loc['ACC']

    # get the dimensions
    dim1, dim2 = loc['HCDATA1'].shape
    master_dxmap = np.zeros_like(hcdata1)
    # storage for mapping orders
    map_orders = np.zeros_like(hcdata1) - 1
    order_overlap = np.zeros_like(hcdata1)
    slope_all_ord = np.zeros((nbo, dim2))
    corr_dx_from_fp = np.zeros((nbo, dim2))

    # define storage for plotting
    slope_deg_arr, slope_arr, skeep_arr = [], [], []
    xsec_arr, ccor_arr = [], []
    ddx_arr, dx_arr = [], []
    dypix_arr, cckeep_arr = [], []

    # define storage in loc
    loc['CORR_DX_FROM_FP'] = np.zeros((nbo, dim2))
    loc['XPEAK2'] = [[]] * nbo
    loc['PEAKVAL2'] = [[]] * nbo
    loc['EWVAL2'] = [[]] * nbo
    loc['ERR_PIX'] = [[]] * nbo
    loc['GOOD_MASK'] = [[]] * nbo
    # set source
    sources = ['CORR_DX_FROM_FP', 'XPEAK2', 'PEAKVAL2', 'EWVAL2', 'ERR_PIX',
               'GOOD_MASK']
    loc.set_sources(sources, func_name)

    # -------------------------------------------------------------------------
    # create the x pixel vector (used with polynomials to find
    #    order center)
    xpix = np.array(range(dim2))
    # y order center positions (every other one)
    ypix = np.zeros((nbo, dim2))
    # loop around order number
    for order_num in range(nbo):
        # x pixel vecctor that is used with polynomials to
        # find the order center y order center
        ypix[order_num] = np.polyval(acc[order_num * 2][::-1], xpix)

    # -------------------------------------------------------------------------
    # iterating the correction, from coarser to finer
    for banana_num in range(nbanana):
        # ---------------------------------------------------------------------
        # we use the code that will be used by the extraction to ensure
        # that slice images are as straight as can be
        # ---------------------------------------------------------------------
        # if the map is not zeros, we use it as a starting point
        if np.sum(master_dxmap != 0) != 0:
            hcdata2 = ea_transform(hcdata1, dxmap=master_dxmap)
            fpdata2 = ea_transform(fpdata1, dxmap=master_dxmap)
            # if this is not the first iteration, then we must be really close
            # to a slope of 0
            range_slopes_deg = small_angle_range
        else:
            hcdata2 = np.array(hcdata1)
            fpdata2 = np.array(fpdata1)
            # starting point for slope exploration
            range_slopes_deg = large_angle_range
        # expressed in pixels, not degrees
        range_slopes = np.tan(np.deg2rad(np.array(range_slopes_deg)))
        # set up iteration storage
        slope_deg_arr_i, slope_arr_i, skeep_arr_i = [], [], []
        xsec_arr_i, ccor_arr_i = [], []
        ddx_arr_i, dx_arr_i = [], []
        dypix_arr_i,  cckeep_arr_i = [], []

        # storage for loc2
        loc2s = []
        # get dx array (NaN)
        dx = np.zeros((nbo, width)) + np.nan
        # ---------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):
            # -----------------------------------------------------------------
            # Log progress
            wmsg = 'Banana iteration: {0}/{1}: Order {2}/{3} '
            wargs = [banana_num + 1, nbanana, order_num + 1, nbo]
            WLOG(p, '', wmsg.format(*wargs))
            # -----------------------------------------------------------------
            # defining a ribbon that will contain the straightened order
            ribbon_hc = np.zeros([width, dim2])
            ribbon_fp = np.zeros([width, dim2])
            # get the widths
            widths = np.arange(width) - width / 2.0
            # get all bottoms and tops
            bottoms = ypix[order_num] - width/ 2 - 2
            tops = ypix[order_num] + width/ 2 + 2
            # splitting the original image onto the ribbon
            for ix in range(dim2):
                # define bottom and top that encompasses all 3 fibers
                bottom = int(bottoms[ix])
                top = int(tops[ix])
                sx = np.arange(bottom, top)
                # calculate spline interpolation and ribbon values
                if bottom > 0:
                    # for the hc data
                    spline_hc = IUVSpline(sx, hcdata2[bottom:top, ix],
                                          ext=1, k=3)
                    ribbon_hc[:, ix] = spline_hc(ypix[order_num, ix] + widths)
                    # for the fp data
                    spline_fp = IUVSpline(sx, fpdata2[bottom:top, ix],
                                          ext=1, k=3)
                    ribbon_fp[:, ix] = spline_fp(ypix[order_num, ix] + widths)

            # normalizing ribbon stripes to their median abs dev
            for iw in range(width):
                # for the hc data
                norm_fp = np.nanmedian(np.abs(ribbon_fp[iw, :]))
                ribbon_hc[iw, :] = ribbon_hc[iw, :] / norm_fp
                # for the fp data
                ribbon_fp[iw, :] = ribbon_fp[iw, :] / norm_fp
            # range explored in slopes
            # TODO: question Where does the /8.0 come from?
            sfactor = (range_slopes[1] - range_slopes[0]) / 8.0
            slopes = (np.arange(9) * sfactor) + range_slopes[0]
            # log the range slope exploration
            wmsg = '\tRange slope exploration: {0:.3f} -> {1:.3f} deg'
            wargs = [range_slopes_deg[0], range_slopes_deg[1]]
            WLOG(p, '', wmsg.format(*wargs))
            # -------------------------------------------------------------
            # the domain is sliced into a number of sections, then we
            # find the tilt that maximizes the RV content
            xsection = dim2 * (np.arange(nsections) + 0.5) / nsections
            dxsection = np.repeat([np.nan], len(xsection))
            keep = np.zeros(len(dxsection), dtype=bool)
            ribbon_fp2 = np.array(ribbon_fp)
            # RV content per slice and per slope
            rvcontent = np.zeros([len(slopes), nsections])
            # loop around the slopes
            for islope, slope in enumerate(slopes):
                # copy the ribbon
                ribbon_fp2 = np.array(ribbon_fp)
                # interpolate new slope-ed ribbon
                for iw in range(width):
                    # get the ddx value
                    ddx = (iw - width/2.0) * slope
                    # get the spline
                    spline = IUVSpline(xpix, ribbon_fp[iw, :], ext=1)
                    # calculate the new ribbon values
                    ribbon_fp2[iw, :] = spline(xpix + ddx)
                # record the profile of the ribbon
                profile = np.nanmedian(ribbon_fp2, axis=0)
                # loop around the sections to record rv content
                for nsection in range(nsections):
                    # sum of integral of derivatives == RV content.
                    # This should be maximal when the angle is right
                    start = nsection * dim2//nsections
                    end = (nsection + 1) * dim2//nsections
                    grad = np.gradient(profile[start:end])
                    rvcontent[islope, nsection] = np.nansum(grad ** 2)
            # -------------------------------------------------------------
            # we find the peak of RV content and fit a parabola to that peak
            for nsection in range(nsections):
                # we must have some RV content (i.e., !=0)
                if np.nanmax(rvcontent[:, nsection]) != 0:
                    vec = np.ones_like(slopes)
                    vec[0], vec[-1] = 0, 0
                    # get the max pixel
                    maxpix = np.nanargmax(rvcontent[:, nsection] * vec)
                    # max RV and fit on the neighbouring pixels
                    xff = slopes[maxpix - 1: maxpix + 2]
                    yff = rvcontent[maxpix - 1: maxpix + 2, nsection]
                    coeffs = nanpolyfit(xff, yff, 2)
                    # if peak within range, then its fine
                    dcoeffs = -0.5 * coeffs[1] / coeffs[0]
                    if np.abs(dcoeffs) < 1:
                        dxsection[nsection] = dcoeffs
                # we sigma-clip the dx[x] values relative to a linear fit
                keep = np.isfinite(dxsection)
            # -------------------------------------------------------------
            # work out the median slope
            dxdiff = dxsection[1:] - dxsection[:-1]
            xdiff = xsection[1:] - xsection[:-1]
            medslope = np.nanmedian(dxdiff/xdiff)
            # work out the residual of dxsection (based on median slope)
            residual = dxsection - (medslope * xsection)
            residual = residual - np.nanmedian(residual)
            res_residual = residual - np.nanmedian(residual)
            residual = residual / np.nanmedian(np.abs(res_residual))
            # work out the maximum sigma and update keep vector
            sigmax = np.nanmax(np.abs(residual[keep]))
            with warnings.catch_warnings(record=True) as _:
                keep &= np.abs(residual) < sigclipmax
            # -------------------------------------------------------------
            # sigma clip
            while sigmax > sigclipmax:
                # recalculate the fit
                coeffs = nanpolyfit(xsection[keep], dxsection[keep], 2)
                # get the residuals
                res = dxsection - np.polyval(coeffs, xsection)
                # normalise residuals
                res = res - np.nanmedian(res[keep])
                res = res / np.nanmedian(np.abs(res[keep]))
                # calculate the sigma
                sigmax = np.nanmax(np.abs(res[keep]))
                # do not keep bad residuals
                with warnings.catch_warnings(record=True) as _:
                    keep &= np.abs(res) < sigclipmax
            # -------------------------------------------------------------
            # fit a 2nd order polynomial to the slope vx position
            #    along order
            coeffs = nanpolyfit(xsection[keep], dxsection[keep], 2)
            # log slope at center
            s_xpix = dim2//2
            s_ypix = np.rad2deg(np.arctan(np.polyval(coeffs, s_xpix)))
            wmsg = '\tSlope at pixel {0}: {1:.5f} deg'
            wargs = [s_xpix, s_ypix]
            WLOG(p, '', wmsg.format(*wargs))
            # get slope for full range
            slope_all_ord[order_num] = np.polyval(coeffs, np.arange(dim2))
            # -------------------------------------------------------------
            # append to storage (for plotting)
            xsec_arr_i.append(np.array(xsection))
            slope_deg_arr_i.append(np.rad2deg(np.arctan(dxsection)))
            slope_arr_i.append(np.rad2deg(np.arctan(slope_all_ord[order_num])))
            skeep_arr_i.append(np.array(keep))

            # -----------------------------------------------------------------
            # append to new loc
            loc2 = ParamDict()
            if p['DRS_PLOT'] and p['DRS_DEBUG'] >= 2:
                # add temp keys for debug plot
                loc2['NUMBER_ORDERS'] = loc['NUMBER_ORDERS']
                loc2['HCDATA'] = loc['HCDATA']
                loc2['SLOPE_DEG'] = np.rad2deg(np.arctan(dxsection))
                loc2['SLOPE'] = np.rad2deg(np.arctan(slope_all_ord[order_num]))
                loc2['S_KEEP'] = np.array(keep)

            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the
            #    slicer profile in the fp
            yfit = np.polyval(coeffs, xpix)
            for iw in range(width):
                # get the x shift
                ddx = (iw - width/2.0) * yfit
                # calculate the spline at this width
                spline_fp = IUVSpline(xpix, ribbon_fp[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon_fp2[iw, :] = spline_fp(xpix + ddx)
            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the slicer profile
            #    in the hc
            ribbon_hc2 = np.array(ribbon_hc)
            for iw in range(width):
                # get the x shift
                ddx = (iw - width/2.0) * yfit
                # calculate the spline at this width
                spline_hc = IUVSpline(xpix, ribbon_hc[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon_hc2[iw, :] = spline_hc(xpix + ddx)

            # -------------------------------------------------------------
            # get the median values of the fp and hc
            sp_fp = np.nanmedian(ribbon_fp2, axis=0)
            sp_hc = np.nanmedian(ribbon_hc2, axis=0)

            loc = get_offset_sp(p, loc, sp_fp, sp_hc, order_num)
            corr_dx_from_fp[order_num] = loc['CORR_DX_FROM_FP'][order_num]

            # -------------------------------------------------------------
            # median FP peak profile. We will cross-correlate each
            # row of the ribbon with this
            profile = np.nanmedian(ribbon_fp2, axis=0)
            medianprofile = filters.median_filter(profile, med_filter_size)
            profile = profile - medianprofile

            # -------------------------------------------------------------
            # cross-correlation peaks of median profile VS position
            #    along ribbon
            # TODO: Question: Why -3 to 4 where does this come from?
            ddx = np.arange(-3, 4)
            # set up cross-correlation storage
            ccor = np.zeros([width, len(ddx)], dtype=float)
            # loop around widths
            for iw in range(width):
                for jw in range(len(ddx)):
                    # calculate the peasron r coefficient
                    xff = ribbon_fp2[iw, :]
                    yff = np.roll(profile, ddx[jw])
                    pearsonr_value = stats.pearsonr(xff, yff)[0]
                    # push into cross-correlation storage
                    ccor[iw, jw] = pearsonr_value
                # fit a gaussian to the cross-correlation peak
                xvec = ddx
                yvec = ccor[iw, :]
                with warnings.catch_warnings(record=True) as _:
                    gcoeffs, _ = spirouMath.gauss_fit_nn(xvec, yvec, 4)
                # check that max value is good
                if np.nanmax(ccor[iw, :]) > min_good_corr:
                    dx[order_num, iw] = gcoeffs[1]
            # -------------------------------------------------------------
            # remove any offset in dx, this would only shift the spectra
            dypix = np.arange(len(dx[order_num]))
            with warnings.catch_warnings(record=True):
                keep = np.abs(dx[order_num] - np.nanmedian(dx[order_num])) < 1
            keep &= np.isfinite(dx[order_num])
            # -------------------------------------------------------------
            # if the first pixel is nan and the second is OK,
            #    then for continuity, pad
            # if (not keep[0]) and keep[1]:
            #     keep[0] = True
            #     dx[0] = dx[1]
            # # same at the other end
            # if (not keep[-1]) and keep[-2]:
            #     keep[-1] = True
            #     dx[-1] = dx[-2]

            # -------------------------------------------------------------
            # append to storage for plotting
            ccor_arr_i.append(np.array(ccor))
            ddx_arr_i.append(np.array(ddx))
            dx_arr_i.append(np.array(dx[order_num]))
            dypix_arr_i.append(np.array(dypix))
            cckeep_arr_i.append(np.array(keep))
            # -----------------------------------------------------------------
            if p['DRS_PLOT'] and p['DRS_DEBUG'] >= 2:
                # add temp keys for debug plot
                loc2['XSECTION'] = np.array(xsection)
                loc2['CCOR'], loc2['DDX'] = ccor, ddx
                loc2['DX'], loc2['DYPIX'] = dx[order_num], dypix
                loc2['C_KEEP'] = keep
            # append loc2 to storage
            loc2s.append(loc2)
            # -----------------------------------------------------------------
            # set those values that should not be kept to NaN
            dx[order_num][~keep] = np.nan

        # -----------------------------------------------------------------
        # get the median filter of dx (short median filter)
        dx2_short = np.array(dx)
        for iw in range(width):
            dx2_short[:, iw] = median_filter_ea(dx[:, iw], short_medfilt_width)
        # get the median filter of short dx with longer median
        #     filter/second pass
        dx2_long = np.array(dx)
        for iw in range(width):
            dx2_long[:, iw] = median_filter_ea(dx2_short[:, iw],
                                               long_medfilt_width)
        # apply short dx filter to dx2
        dx2 = np.array(dx2_short)
        # apply long dx filter to NaN positions of short dx filter
        nanmask = ~np.isfinite(dx2)
        dx2[nanmask] = dx2_long[nanmask]

        # ---------------------------------------------------------------------
        # dx plot
        if p['DRS_PLOT'] > 0:
            # plots setup: start interactive plot
            sPlt.start_interactive_session(p)
            # plot
            sPlt.slit_shape_dx_plot(p, dx, dx2, banana_num)
            # end interactive section
            sPlt.end_interactive_session(p)

        # ---------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):

            # -------------------------------------------------------------
            # log process
            wmsg = ('Update of the big dx map after filtering of pre-order '
                    'dx: {0}/{1}')
            wargs = [order_num + 1, nbo]
            WLOG(p, '', wmsg.format(*wargs))

            # -------------------------------------------------------------
            # spline everything onto the master DX map
            #    ext=3 forces that out-of-range values are set to boundary
            #    value this simply uses the last reliable dx measurement for
            #    the neighbouring slit position

            # redefine keep array from dx2
            keep = np.isfinite(dx2[order_num])
            # redefine dypix
            dypix = np.arange(len(keep))
            # get locations of keep
            pos_keep = np.where(keep)[0]
            # set the start point
            start_good_ccor = np.min(pos_keep) - 2
            # deal with start being out-of-bounds
            if start_good_ccor == -1:
                start_good_ccor = 0
            # set the end point
            end_good_ccor = np.max(pos_keep) + 2
            # deal with end being out-of-bounds
            if end_good_ccor == width:
                end_good_ccor = width - 1
            # work out spline
            spline = IUVSpline(dypix[keep], dx2[order_num][keep], ext=3)
            # define a mask for the good ccor
            good_ccor_mask = np.zeros(len(keep), dtype=bool)
            good_ccor_mask[start_good_ccor:end_good_ccor] = True

            # log start and end points
            wmsg = '\tData along slice. Start={0} End={1}'
            wargs = [start_good_ccor, end_good_ccor]
            WLOG(p, '', wmsg.format(*wargs))

            # -------------------------------------------------------------
            # for all field positions along the order, we determine the
            #    dx+rotation values and update the master DX map
            fracs = ypix[order_num] - np.fix(ypix[order_num])
            widths = np.arange(width)

            for ix in range(dim2):
                # get slope
                slope = slope_all_ord[order_num, ix]
                # get dx0 with slope factor added
                dx0 = (widths - width // 2 + (1 - fracs[ix])) * slope
                # get the ypix at this value
                widthrange = np.arange(-width//2, width//2)
                ypix2 = int(ypix[order_num, ix]) + widthrange
                # get the ddx
                ddx = spline(widths - fracs[ix])
                # set the zero shifts to NaNs
                ddx[ddx == 0] = np.nan
                # only set positive ypixels
                pos_y_mask = (ypix2 >= 0) & good_ccor_mask
                # do not want overlap between orders and a gap of 1 pixel
                ypix0 = ypix[order_num, ix]
                # identify the upper bound of order
                if order_num != (nbo-1):
                    ypixa = ypix[order_num + 1, ix]
                    upper_ylimit_overlap = ypix0 + 0.5 * (ypixa - ypix0) - 1
                else:
                    upper_ylimit_overlap = dim1 - 1
                # identify the lower bound of order
                if order_num !=0:
                    ypixb = ypix[order_num - 1, ix]
                    lower_ylimit_overlap = ypix0 - 0.5 * (ypix0 - ypixb) + 1
                else:
                    lower_ylimit_overlap = 0
                # add these constraints to the position mask
                pos_y_mask &= (ypix2 > lower_ylimit_overlap)
                pos_y_mask &= (ypix2 < upper_ylimit_overlap)
                # if we have some values add to master DX map
                if np.sum(pos_y_mask) != 0:
                    # get positions in y
                    positions = ypix2[pos_y_mask]

                    # for first iteration
                    if banana_num == 0:
                        # get good positions
                        good_pos = map_orders[positions, ix] != -1
                        # get order overlap from last order
                        order_overlap[positions, ix] += good_pos
                        # update map_orders
                        map_orders[positions, ix] = order_num

                    # get shifts combination of ddx and dx0 correction
                    ddx_f = ddx + dx0
                    shifts = ddx_f[pos_y_mask] - corr_dx_from_fp[order_num][ix]
                    # apply shifts to master dx map at correct positions
                    master_dxmap[positions, ix] += shifts

            # -----------------------------------------------------------------
            if p['DRS_PLOT'] and (p['DRS_DEBUG'] >= 2) and plot_on:
                # plot angle and offset plot for each order
                sPlt.plt.ioff()
                sPlt.slit_shape_angle_plot(p, loc2s[order_num], bnum=banana_num,
                                           order=order_num)
                sPlt.slit_shape_offset_plot(p, loc, bnum=banana_num,
                                            order=order_num)
                sPlt.plt.show()
                sPlt.plt.close()
                sPlt.plt.ion()
        # ---------------------------------------------------------------------
        # append to storage
        slope_deg_arr.append(slope_deg_arr_i), slope_arr.append(slope_arr_i)
        skeep_arr.append(skeep_arr_i), xsec_arr.append(xsec_arr_i)
        ccor_arr.append(ccor_arr_i), ddx_arr.append(ddx_arr_i)
        dx_arr.append(dx_arr_i), dypix_arr.append(dypix_arr_i)
        cckeep_arr.append(cckeep_arr_i)

    # setting to 0 pixels that are NaNs
    nanmask = ~np.isfinite(master_dxmap)
    master_dxmap[nanmask] = 0.0

    # distortions where there is some overlap between orders will be wrong
    master_dxmap[order_overlap != 0] = 0.0

    # push storage into loc
    loc['SLOPE_DEG'], loc['SLOPE'] = slope_deg_arr, slope_arr
    loc['S_KEEP'], loc['XSECTION'] = skeep_arr, xsec_arr
    loc['CCOR'], loc['DDX'] = ccor_arr, ddx_arr
    loc['DX'], loc['DYPIX'] = dx_arr, dypix_arr
    loc['C_KEEP'] = cckeep_arr
    # add DXMAP to loc
    loc['DXMAP'] = master_dxmap
    # add new hcdata/fpdata and order overlap for sanity checks
    loc['ORDER_OVERLAP'] = order_overlap
    # set source
    keys = ['SLOPE_DEG', 'SLOPE', 'S_KEEP', 'XSECTION', 'CCOR', 'DDX',
            'DX', 'DYPIX', 'C_KEEP', 'DXMAP', 'ORDER_OVERLAP']
    loc.set_sources(keys, func_name)
    # return loc
    return loc


def get_y_shape_map(p, loc, hdr):
    func_name = __NAME__ + '.get_y_shape_map()'
    # get data from loc
    nbo = loc['NUMBER_ORDERS'] // 2
    dim1, dim2 = loc['FPDATA1'].shape

    # x indices in the initial image
    xpix = np.arange(dim2)

    # TODO: This is very messy --> clean up
    loc_fibers = dict()
    # loop around fiber types
    for fiber in ['AB', 'A', 'B', 'C']:
        p_tmp, loc_tmp = p.copy(), ParamDict()
        # set fiber
        p_tmp['FIBER'] = fiber
        p_tmp.set_source('FIBER', __NAME__ + '/main()()')
        # --------------------------------------------------------------
        # Get localisation coefficients
        # --------------------------------------------------------------
        # get this fibers parameters
        p_tmp = spirouFile.fiber_params(p_tmp, p_tmp['FIBER'], merge=True)
        # get localisation fit coefficients
        p_tmp, loc_tmp = get_loc_coefficients(p_tmp, hdr)
        loc_tmp['LOCOFILE'] = p_tmp['LOCOFILE']
        loc_tmp.set_source('LOCOFILE', p_tmp.sources['LOCOFILE'])
        # --------------------------------------------------------------
        # Average AB into one fiber for AB, A and B
        # --------------------------------------------------------------
        # if we have an AB fiber merge fit coefficients by taking the
        # average
        # of the coefficients
        # (i.e. average of the 1st and 2nd, average of 3rd and 4th, ...)
        # if fiber is AB take the average of the orders
        if fiber == 'AB':
            # merge
            loc_tmp['ACC'] = merge_coefficients(loc_tmp, loc_tmp['ACC'], step=2)
            loc_tmp['ASS'] = merge_coefficients(loc_tmp, loc_tmp['ASS'], step=2)
            # set the number of order to half of the original
            loc_tmp['NUMBER_ORDERS'] = int(loc_tmp['NUMBER_ORDERS'] / 2.0)
        # if fiber is B take the even orders
        elif fiber == 'B':
            loc_tmp['ACC'] = loc_tmp['ACC'][:-1:2]
            loc_tmp['ASS'] = loc_tmp['ASS'][:-1:2]
            loc_tmp['NUMBER_ORDERS'] = int(loc_tmp['NUMBER_ORDERS'] / 2.0)
        # if fiber is A take the even orders
        elif fiber == 'A':
            loc_tmp['ACC'] = loc_tmp['ACC'][1::2]
            loc_tmp['ASS'] = loc_tmp['ASS'][1::2]
            loc_tmp['NUMBER_ORDERS'] = int(loc_tmp['NUMBER_ORDERS'] / 2.0)
        # ------------------------------------------------------------------
        # append to storage dictionary
        # ------------------------------------------------------------------
        loc_fibers[fiber] = loc_tmp.copy()

    # set pos_a, pos_b, pos_c
    pos_a = loc_fibers['A']['ACC']
    pos_b = loc_fibers['B']['ACC']
    pos_c = loc_fibers['C']['ACC']

    # looping through x pixels
    # We take each column and determine where abc fibers fall relative
    # to the central pixel in x (normally, that's 4088/2) along the y axis.
    # This difference in position gives a dy that need to be applied to
    # straighten the orders

    # Once we have determined this for all abc fibers and all orders, we
    # fit a Nth order polynomial to the dy versus y relation along the
    # column, and apply a spline to straighten the order.
    y0 = np.zeros((nbo * 3, dim2))

    # log progress
    WLOG(p, '', 'Creating DY map from localisation')

    # set a master dy map
    master_dymap = np.zeros_like(loc['FPDATA1'])
    # loop around orders and get polynomial values for fibers A, B and C
    for order_num in range(nbo):
        iord = order_num * 3
        y0[iord, :] = np.polyval(pos_a[order_num, :][::-1], xpix)
        y0[iord + 1, :] = np.polyval(pos_b[order_num, :][::-1], xpix)
        y0[iord + 2, :] = np.polyval(pos_c[order_num, :][::-1], xpix)
    # loop around each x pixel (columns)
    for ix in range(dim2):
        # dy for all orders and all fibers
        dy = y0[:, ix] - y0[:, dim2 // 2]
        # fitting the dy to the position of the order
        yfit = nanpolyfit(y0[:, ix], dy, 3)
        ypix = np.arange(dim1)
        # add to the master dy map
        master_dymap[:, ix] = np.polyval(yfit, ypix)
    # add DXMAP to loc
    loc['DYMAP'] = master_dymap
    loc.set_source('DYMAP', func_name)
    # return loc
    return loc


def get_loc_coefficients(p, hdr=None, loc=None):
    """
    Extracts loco coefficients from parameters keys (uses header="hdr" provided
    to get acquisition time or uses p['FITSFILENAME'] to get acquisition time if
    "hdr" is None

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                kw_LOCO_NBO: list, keyword store for the number of orders
                             located
                kw_LOCO_DEG_C: list, keyword store for the fit degree for
                               order centers
                kw_LOCO_DEG_W: list, keyword store for the fit degree for
                               order widths
                kw_LOCO_CTR_COEFF: list, keyword store for the Coeff center
                                   order
                kw_LOCO_FWHM_COEFF: list, keyword store for the Coeff width
                                    order
                LOC_FILE: string, the suffix for the location calibration
                          database key (usually the fiber type)
                             - read from "loc_file_fpall", if not defined
                               uses p['FIBER']
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                calibDB: dictionary, the calibration database dictionary
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                log_opt: string, log option, normally the program name

    :param hdr: dictionary, header file from FITS rec (opened by spirouFITS)
    :param loc: parameter dictionary, ParamDict containing data

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                number_orders: int, the number of orders in reference spectrum
                nbcoeff_ctr: int, number of coefficients for the center fit
                nbcoeff_wid: int, number of coefficients for the width fit
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
    """
    func_name = __NAME__ + '.get_loc_coefficients()'
    # get keywords
    loco_nbo = p['KW_LOCO_NBO'][0]
    loco_deg_c, loco_deg_w = p['KW_LOCO_DEG_C'][0], p['KW_LOCO_DEG_W'][0]
    loco_ctr_coeff = p['KW_LOCO_CTR_COEFF'][0]
    loco_fwhm_coeff = p['KW_LOCO_FWHM_COEFF'][0]

    # get loc file
    if 'LOC_FILE' in p:
        loc_file = 'LOC_' + p['LOC_FILE']
    else:
        loc_file = 'LOC_' + p['FIBER']

    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = spirouDB.GetAcqTime(p, hdr)
        # get calibDB
        c_database, p = spirouDB.GetCalibDatabase(p, acqtime)
    else:
        c_database = p['CALIBDB']
        acqtime = p['MAX_TIME_HUMAN']

    # get the reduced dir name
    reduced_dir = p['REDUCED_DIR']

    # set up the loc param dict
    if loc is None:
        loc = ParamDict()

    # check for localization file for this fiber
    if not (loc_file in c_database):
        emsg1 = ('No order geometry defined in the calibDB for fiber: {0}'
                 '').format(p['FIBER'])
        emsg2 = ('    requires key="{0}" in calibDB file (with time < {1}).'
                 '').format(loc_file, acqtime)
        emsg3 = '    Unable to complete the recipe, FATAL'
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
    # construct the localization file name
    loco_file = os.path.join(reduced_dir, c_database[loc_file][1])
    # log that we are reading localization parameters
    wmsg = 'Reading localization parameters of Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(p['FIBER'], c_database[loc_file][1]))
    # get header for loco file
    hdict = spirouFITS.read_header(p, loco_file)
    # Get number of orders from header
    loc['NUMBER_ORDERS'] = int(spirouFITS.read_key(p, hdict, loco_nbo))
    # Get the number of fit coefficients from header
    loc['NBCOEFF_CTR'] = int(spirouFITS.read_key(p, hdict, loco_deg_c)) + 1
    loc['NBCOEFF_WID'] = int(spirouFITS.read_key(p, hdict, loco_deg_w)) + 1
    # Read the coefficients from header
    #     for center fits
    loc['ACC'] = spirouFITS.read_key_2d_list(p, hdict, loco_ctr_coeff,
                                             loc['NUMBER_ORDERS'],
                                             loc['NBCOEFF_CTR'])
    #     for width fits
    loc['ASS'] = spirouFITS.read_key_2d_list(p, hdict, loco_fwhm_coeff,
                                             loc['NUMBER_ORDERS'],
                                             loc['NBCOEFF_WID'])
    # add some other parameters to loc
    loc['LOCO_CTR_COEFF'] = loco_ctr_coeff
    loc['LOCO_FWHM_COEFF'] = loco_fwhm_coeff
    loc['LOCO_CTR_FILE'] = loco_file
    loc['LOCO_FWHM_FILE'] = loco_file
    # add source
    added = ['number_orders', 'nbcoeff_ctr', 'nbcoeff_wid', 'acc', 'ass',
             'loco_ctr_coeff', 'loco_fwhm_coeff', 'loco_ctr_file',
             'loco_fwhm_file']
    loc.set_sources(added, func_name)

    # get filename
    p['LOCOFILE'] = os.path.basename(loco_file)
    p.set_source('LOCOFILE', func_name)

    # return the loc param dict
    return p, loc


def merge_coefficients(loc, coeffs, step):
    """
    Takes a list of coefficients "coeffs" and merges them based on "step"
    using the mean of "step" blocks

    i.e. shrinks a list of N coefficients to N/2 (if step = 2) where
         indices 0 and 1 are averaged, indices 2 and 3 are averaged etc

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                number_orders: int, the number of orders in reference spectrum

    :param coeffs: numpy array (2D), the list of coefficients
                   shape = (number of orders x number of fit parameters)

    :param step: int, the step between merges
                 i.e. total size before = "number_orders"
                      total size after = "number_orders"/step

    :return newcoeffs: numpy array (2D), the new list of coefficients
                shape = (number of orders/step x number of fit parmaeters)
    """
    # get number of orders
    nbo = loc['NUMBER_ORDERS']
    # copy coeffs
    newcoeffs = coeffs.copy()
    # get sum of 0 to step pixels
    cosum = np.array(coeffs[0:nbo:step, :])
    for i_it in range(1, step):
        cosum = cosum + coeffs[i_it:nbo:step, :]
    # overwrite values into coeffs array
    newcoeffs[0:int(nbo/step), :] = (1/step)*cosum
    # return merged coeffients
    return newcoeffs


def median_filter_ea(vector, width):
    """
    Median filter array "vector" by a box of width "width"
    Note: uses nanmedian to median the boxes

    :param vector: numpy array (1D): the vector to median filter
    :param width: int, the size of the median box to apply

    :return vector2: numpy array (1D): same size as "vector" except the pixel
                     value is that of the median of box +/- width//2 of each
                     pixel
    """
    # construct an output vector filled with NaNs
    vector2 = np.zeros_like(vector) + np.nan
    # loop around pixel in vector
    for ix in range(len(vector)):
        # define a start and end of our median box
        start = ix - width // 2
        end = ix + width // 2
        # deal with boundaries
        if start < 0:
            start = 0
        if end > len(vector) - 1:
            end = len(vector) - 1
        # set the value of the new pixel equal to the median of the box of
        #   the original vector (and deal with NaNs)
        with warnings.catch_warnings(record=True) as _:
            vector2[ix] = np.nanmedian(vector[start:end])
    # return new vector
    return vector2


def get_offset_sp(p, loc, sp_fp, sp_hc, order_num):
    # get constants from p
    xoffset = p['SHAPEOFFSET_XOFFSET']
    bottom_fp_percentile = p['SHAPEOFFSET_BOTTOM_PERCENTILE']
    top_fp_percentile = p['SHAPEOFFSET_TOP_PERCENTILE']
    top_floor_frac = p['SHAPEOFFSET_TOP_FLOOR_FRAC']
    med_filter_wid = p['SHAPEOFFSET_MED_FILTER_WIDTH']
    fpindexmax = p['SHAPEOFFSET_FPINDEX_MAX']
    valid_fp_length = p['SHAPEOFFSET_VALID_FP_LENGTH']
    drift_margin = p['SHAPEOFFSET_DRIFT_MARGIN']
    inv_iterations = p['SHAPEOFFSET_WAVEFP_INV_ITERATION']
    mask_border = p['SHAPEOFFSET_MASK_BORDER']
    minimum_maxpeak_frac = p['SHAPEOFFSET_MINIMUM_MAXPEAK_FRAC']
    mask_pixwidth = p['SHAPEOFFSET_MASK_PIXWIDTH']
    mask_extwidth = p['SHAPEOFFSET_MASK_EXTWIDTH']
    deviant_percentiles = p['SHAPEOFFSET_DEVIANT_PERCENTILES']
    fp_max_num_error = p['SHAPEOFFSET_FPMAX_NUM_ERROR']
    fit_hc_sigma = p['SHAPEOFFSET_FIT_HC_SIGMA']
    maxdev_threshold = p['SHAPEOFFSET_MAXDEV_THRESHOLD']
    absdev_threshold = p['SHAPEOFFSET_ABSDEV_THRESHOLD']
    # -------------------------------------------------------------------------
    # get data from loc
    dim1, dim2 = np.shape(loc['HCDATA1'])
    poly_wave_ref = loc['MASTERWAVEP']
    une_lines = loc['LL_LINE']
    poly_cavity = loc['CAVITY_LEN_COEFFS']
    # -------------------------------------------------------------------------
    # define storage for the bottom and top values of the FPs
    bottom = np.zeros_like(sp_fp)
    top = np.zeros_like(sp_fp)
    # -------------------------------------------------------------------------
    # loop around pixels
    for xpix in range(dim2):
        # put the start a certain number of pixels behind
        start = xpix - xoffset
        end = xpix + xoffset
        # deal with boundaries
        if start < 0:
            start = 0
        if end > (dim2 - 1):
            end = dim2 - 1
        # define a segment between start and end
        segment = sp_fp[start:end]
        # push values into bottom and top
        bottom[xpix] = np.nanpercentile(segment, bottom_fp_percentile)
        top[xpix] = np.nanpercentile(segment, top_fp_percentile)
    # -------------------------------------------------------------------------
    # put a floor in the top values
    top_floor_value = top_floor_frac * np.max(top)
    top_mask = top <= top_floor_value
    top[top_mask] = top_floor_value
    # -------------------------------------------------------------------------
    # subtract off the bottom from the FP's of this order
    sp_fp = sp_fp - bottom
    # normalise by the difference between top and bottom
    sp_fp = sp_fp / (top - bottom)
    # set NaN's to zero
    sp_fp[~np.isfinite(sp_fp)] = 0.0
    # -------------------------------------------------------------------------
    # The HC spectrum is high-passed. We are just interested to know if
    # a given expected line from the catalog falls at the position of a
    # >3-sigma peak relative to the continuum
    sp_hc = sp_hc - medfilt(sp_hc, med_filter_wid)
    # normalise HC to its absolute deviation
    norm = np.nanmedian(np.abs(sp_hc[sp_hc != 0]))
    sp_hc = sp_hc / norm
    # -------------------------------------------------------------------------
    # fpindex is a variable that contains the index of the FP peak interference
    # this is expected to range from ~10000 to ~25000
    fpindex = np.arange(fpindexmax) + 1
    # -------------------------------------------------------------------------
    # We find the exact wavelength of each FP peak in fpindex
    # considering the cavity length

    # The cavity length is very slightly wavelength dependent (hence the
    # polynomial read earlier). First we find the length in the middle of the
    # expected wavelength domain from the reference file

    # just to cut the number of peaks so that they are
    # all contained within the relevant domain
    xdomain = np.linspace(0, dim2, 3).astype(int)
    wave_start_med_end = np.polyval(poly_wave_ref[order_num][::-1], xdomain)
    # get the wavelengths for the fp
    wave_fp = np.polyval(poly_cavity, wave_start_med_end[1]) * 2/fpindex
    # -------------------------------------------------------------------------
    # we give a 20 nm marging on either side... who knows, maybe SPIRou
    #    has drifted
    good = (wave_fp > wave_start_med_end[0] - drift_margin)
    good &= (wave_fp < wave_start_med_end[2] + drift_margin)
    # keep only the relevant FPs in this good region
    fpindex = fpindex[good]
    wave_fp = wave_fp[good]
    # -------------------------------------------------------------------------
    # a numerical trick so that we don't have to invert the poly_cavity
    #    polynomial wave_fp depends on the cavity length, which in turns
    #    depends (very slightly) on wave_fp again. This iteration
    #    fixes the problem
    for iteration in range(inv_iterations):
        wave_fp = np.polyval(poly_cavity, wave_fp) * 2 / fpindex
    # -------------------------------------------------------------------------
    # get the pixel position along the spectrum
    xpixs = np.arange(len(sp_fp))
    # storage to be appended to
    # x position of the FP peak, peak value. Could be used for quality check,
    #    e-width of the line. Could be used for quality check
    xpeak, peakval, ewval = [], [], []
    # peak value of the FP spectrum
    maxfp = np.max(sp_fp)
    # current maximum value after masking
    max_it = float(maxfp)
    # mask
    mask = np.ones_like(sp_fp).astype(int)
    # deal with borders
    mask[:mask_border] = 0
    mask[-mask_border:] = 0

    # looping while FP peaks are at least "minimum_maxpeak_frac" * 100% of
    #     the max peak value
    while max_it > (maxfp * minimum_maxpeak_frac):
        # get the position of the maximum peak
        pos = np.argmax(sp_fp * mask)
        # get the current maximum value
        max_it = sp_fp[pos]
        # set this peak to False in the mask
        fpstart, fpend = pos - mask_pixwidth, pos + mask_pixwidth + 1
        mask[fpstart:fpend] = 0
        # set the width
        extstart, extend = pos - mask_extwidth, pos + mask_extwidth + 1
        # extract a window in the spectrum
        yy = sp_fp[extstart:extend]
        xx = xpixs[extstart:extend]
        # find the domain between the minima before and the minima after the
        #   peak value
        mask1 = np.ones_like(yy).astype(int)
        mask1[:mask_extwidth] = 0
        mask2 = np.ones_like(yy).astype(int)
        mask2[mask_extwidth:] = 0
        # find the minima of the fp's in this mask
        y0 = np.argmin(yy/np.max(yy) + mask1)
        y1 = np.argmin(yy/np.max(yy) + mask2)
        # re-set xx and yy
        xx = np.array(xx[y0:y1 + 1]).astype(float)
        yy = np.array(yy[y0:y1 + 1]).astype(float)

        # the FP must be at least 5 pixels long to be valid
        if len(xx) > valid_fp_length:
            # set up the guess: amp, x0, w, zp
            guess = [np.max(yy) - np.min(yy),  xx[np.argmax(yy)],
                     1, np.min(yy), 0]
            # try to fit a gaussian
            try:
                coeffs, _ = curve_fit(spirouMath.gauss_fit_s, xx, yy, p0=guess)
                goodfit = True
            except Exception as _:
                goodfit, coeffs = False, None
            # if we had a fit then update some values
            if goodfit:
                xpeak.append(coeffs[1])
                peakval.append(coeffs[0])
                ewval.append(coeffs[2])

    # -------------------------------------------------------------------------
    # sort FP peaks by their x pixel position
    indices = np.argsort(xpeak)
    # apply sort to vectors
    xpeak2 = np.array(xpeak)[indices]
    peakval2 = np.array(peakval)[indices]
    ewval2 = np.array(ewval)[indices]
    # we  "count" the FP peaks and determine their number in the
    #   FP interference
    # determine distance between consecutive peaks
    xpeak2_mean = (xpeak2[1:] + xpeak2[:-1]) / 2
    dxpeak = xpeak2[1:] - xpeak2[:-1]
    # we clip the most deviant peaks
    lowermask = dxpeak > np.nanpercentile(dxpeak, deviant_percentiles[0])
    uppermask = dxpeak < np.nanpercentile(dxpeak, deviant_percentiles[1])
    good = lowermask & uppermask
    # apply good mask and fit the peak separation
    fit_peak_separation = nanpolyfit(xpeak2_mean[good], dxpeak[good], 2)
    # Looping through peaks and counting the number of meddx between peaks
    #    we know that peaks will be at integer multiple or medds (in the
    #    overwhelming majority, they will be at 1 x meddx)
    ipeak = np.zeros(len(xpeak2), dtype=int)
    # loop around the xpeaks
    for it in range(1, len(xpeak2)):
        # get the distance between peaks
        dx = xpeak2[it] - xpeak2[it - 1]
        # get the estimate from the fit peak separation
        dx_est = np.polyval(fit_peak_separation, xpeak2[it])
        # find the integer number of the peak
        ipeak[it] = ipeak[it - 1] + np.round(dx / dx_est)
        # if we have a unexpected deviation log it
        if np.round(dx/dx_est) != 1:
            wmsg = '\t\tdx = {0:.5f} dx/dx_est = {1:.5f} estimate = {2:.5f}'
            wargs = [dx, dx/dx_est, dx_est]
            WLOG(p, '', wmsg.format(*wargs))
    # -------------------------------------------------------------------------
    # Trusting the wavelength solution this is the wavelength of FP peaks
    wave_from_hdr = np.polyval(poly_wave_ref[order_num][::-1], xpeak2)
    # We estimate the FP order of the first FP peak. This integer value
    # should be good to within a few units
    fit0 = np.polyval(poly_cavity, wave_from_hdr[0])
    fp_peak0_est = int(fit0 * 2 / wave_from_hdr[0])
    # we scan "zp", which is the FP order of the first FP peak that we've
    #    found we assume that the error in FP order assignment could range
    #    from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
    #    tested to date
    best_zp = int(fp_peak0_est)
    max_good = 0
    # loop around estimates
    fpstart = fp_peak0_est - fpindex[0] - fp_max_num_error
    fpend = fp_peak0_est - fpindex[0] + fp_max_num_error
    # loop from fpstart to fpend
    for zp in range(fpstart, fpend):
        # we take a trial solution between wave (from the theoretical FP
        #    solution) and the x position of measured peaks
        fitzp = nanpolyfit(wave_fp[zp - ipeak], xpeak2, 3)
        # we predict an x position for the known U Ne lines
        xpos_predict = np.polyval(fitzp, une_lines)
        # deal with borders
        good = (xpos_predict > 0) & (xpos_predict < dim2)
        xpos_predict = xpos_predict[good]
        # we check how many of these lines indeed fall on > "fit_hc_sigma"
        #    sigma excursion of the HC spectrum
        xpos_predict_int = np.zeros(len(xpos_predict), dtype=int)
        for it in range(len(xpos_predict_int)):
            xpos_predict_int[it] = xpos_predict[it]
        # the FP order number that produces the most HC matches
        #   is taken to be the right wavelength solution
        frac_good = np.mean(sp_hc[xpos_predict_int] > fit_hc_sigma)
        # update the best values if better than last iteration
        if frac_good > max_good:
            max_good, best_zp = frac_good, zp
    # -------------------------------------------------------------------------
    # log the predicted vs measured FP peak
    wmsg = '\tPredicted FP peak #: {0}   Measured FP peak #: {1}'
    wargs = [fp_peak0_est, fpindex[best_zp]]
    WLOG(p, '', wmsg.format(*wargs))
    # -------------------------------------------------------------------------
    # we find teh actual wavelength of our IDed peaks
    wave_xpeak2 = wave_fp[best_zp - ipeak]
    # get the derivative of the polynomial
    poly = poly_wave_ref[order_num]
    deriv_poly = np.polyder(poly[::-1], 1)[::-1]
    # we find the corresponding offset
    err_wave = wave_xpeak2 - np.polyval(poly[::-1], xpeak2)
    err_pix = err_wave / np.polyval(deriv_poly[::-1], xpeak2)
    # -------------------------------------------------------------------------
    # first we perform a thresholding with a 1st order polynomial
    maxabsdev = np.inf
    good = np.isfinite(err_pix)
    # loop around until we are better than threshold
    while maxabsdev > maxdev_threshold:
        # get the error fit (1st order polynomial)
        fit_err_xpix = nanpolyfit(xpeak2[good], err_pix[good], 1)
        # get the deviation from error fit
        dev = err_pix - np.polyval(fit_err_xpix, xpeak2)
        # get the median absolute deviation
        absdev = np.nanmedian(np.abs(dev))
        # very low thresholding values tend to clip valid points
        if absdev < absdev_threshold:
            absdev = absdev_threshold
        # get the max median asbolute deviation
        maxabsdev = np.nanmax(np.abs(dev[good]/absdev))
        # iterate the good mask
        good &= np.abs(dev / absdev) < maxdev_threshold
    # -------------------------------------------------------------------------
    # then we perform a thresholding with a 5th order polynomial
    maxabsdev = np.inf
    # loop around until we are better than threshold
    while maxabsdev > maxdev_threshold:
        # get the error fit (1st order polynomial)
        fit_err_xpix = nanpolyfit(xpeak2[good], err_pix[good], 5)
        # get the deviation from error fit
        dev = err_pix - np.polyval(fit_err_xpix, xpeak2)
        # get the median absolute deviation
        absdev = np.nanmedian(np.abs(dev))
        # very low thresholding values tend to clip valid points
        if absdev < absdev_threshold:
            absdev = absdev_threshold
        # get the max median asbolute deviation
        maxabsdev = np.nanmax(np.abs(dev[good]/absdev))
        # iterate the good mask
        good &= np.abs(dev/absdev)  < maxdev_threshold
    # -------------------------------------------------------------------------
    # this relation is the (sigma-clipped) fit between the xpix error
    #    and xpix along the order. The corresponding correction vector will
    #    be sent back to the dx grid
    corr_err_xpix = np.polyval(fit_err_xpix, np.arange(dim2))
    # -------------------------------------------------------------------------
    # get the statistics
    std_dev = np.std(dev)
    errpix_med = np.nanmedian(err_pix)
    std_corr = np.std(corr_err_xpix[xpos_predict_int])
    corr_med = np.nanmedian(corr_err_xpix[xpos_predict_int])
    cent_fit = nanpolyfit(xpeak2[good], fpindex[zp - ipeak[good]], 5)
    num_fp_cent = np.polyval(cent_fit, dim2//2)
    # log the statistics
    wargs = [std_dev, absdev, errpix_med, std_corr, corr_med, num_fp_cent]
    wmsg1 = '\t\tstddev pixel error relative to fit: {0:.5f} pix'.format(*wargs)
    wmsg2 = '\t\tabsdev pixel error relative to fit: {1:.5f} pix'.format(*wargs)
    wmsg3 = ('\t\tmedian pixel error relative to zero: {2:.5f} '
             'pix'.format(*wargs))
    wmsg4 = '\t\tstddev applied correction: {3:.5f} pix'.format(*wargs)
    wmsg5 = '\t\tmed applied correction: {4:.5f} pix'.format(*wargs)
    wmsg6 = '\t\tNth FP peak at center of order: {5:.5f}'.format(*wargs)
    WLOG(p, '', [wmsg1, wmsg2, wmsg3, wmsg4, wmsg5, wmsg6])
    # -------------------------------------------------------------------------
    # save to loc
    loc['CORR_DX_FROM_FP'][order_num] = corr_err_xpix
    loc['XPEAK2'][order_num] = xpeak2
    loc['PEAKVAL2'][order_num] = peakval2
    loc['EWVAL2'][order_num] = ewval2
    loc['ERR_PIX'][order_num] = err_pix
    loc['GOOD_MASK'][order_num] = good
    # -------------------------------------------------------------------------
    # return loc
    return loc


def construct_master_fp(p, refimage, filenames, matched_id):

    # get values from p
    percent_thres = p['FP_MASTER_PERCENT_THRES']
    qc_res = p['SHAPE_QC_LINEAR_TRANS_RES_THRES']

    # ----------------------------------------------------------------------
    # Read individual files and sum groups
    # ----------------------------------------------------------------------
    # log process
    WLOG(p, '', 'Reading FP files and combining groups')
    # Find all unique groups
    u_groups = np.unique(matched_id)
    # storage of dark cube
    fp_cube, transforms_list = [], []
    # loop through groups
    for g_it, group_num in enumerate(u_groups):
        # log progress
        wmsg = 'Combining FP Group {0} of {1}'
        WLOG(p, 'info', wmsg.format(g_it + 1, len(u_groups)))
        # find all files for this group
        fp_ids = filenames[matched_id == group_num]
        # only combine if 3 or more images were taken
        if len(fp_ids) >= 3:
            # load this groups files into a cube
            cube = []
            for f_it, filename in enumerate(fp_ids):
                # log reading of data
                basename = os.path.basename(filename)
                wmsg = 'Reading file {0} ({1} / {2})'
                WLOG(p, 'info', wmsg.format(basename, f_it + 1, len(fp_ids)))
                # read data
                data_it, hdr_it, _, _ = spirouFITS.readimage(p, filename)
                # set the number of frames
                p['NBFRAMES'] = 1
                p.set_source('NBFRAMES', __NAME__ + '.main()')
                # Correction of DARK
                p, datac_it = correct_for_dark(p, data_it, hdr_it)
                # Resize fp data
                # rotate the image and convert from ADU/s to e-
                data_it = flip_image(p, datac_it)
                data_it = convert_to_e(data_it, p=p)
                # convert NaN to zeros
                # TODO: Do we need to set zeros?
                data0_it = np.where(~np.isfinite(data_it),
                                   np.zeros_like(data_it), data_it)
                # resize image
                bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                               ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                               getshape=False)
                data1_it = resize(p, data0_it, **bkwargs)
                # log change in data size
                wmsg = 'FP Image {0} format changed to {1}x{2}'
                WLOG(p, '', wmsg.format(f_it + 1, *data1_it.shape))
                # Correct for the BADPIX mask (set all bad pixels to zero)
                bargs = [p, data1_it, hdr_it]
                p, data1_it = correct_for_badpix(*bargs)
                p, badpixmask = correct_for_badpix(*bargs, return_map=True)
                # get the number of bad pixels
                with warnings.catch_warnings(record=True) as _:
                    n_bad_pix = np.nansum(data1_it <= 0)
                n_bad_pix_frac = n_bad_pix * 100 / np.product(data1_it.shape)
                # Log number
                wmsg = 'Nb FP dead pixels = {0} / {1:.2f} %'
                WLOG(p, '', wmsg.format(int(n_bad_pix), n_bad_pix_frac))
                # normalise to the FP_MASTER_PERCENT_THRES percentile
                data1_it = data1_it / np.nanpercentile(data1_it, percent_thres)
                # log progress
                WLOG(p, '', 'Cleaning FP hot pixels')
                # correct hot pixels
                data1_it = spirouEXTOR.CleanHotpix(data1_it, badpixmask)
                #add to cube
                cube.append(data1_it)
            # log progress
            wmsg = 'Calculating median of {0} images'
            WLOG(p, '', wmsg.format(len(fp_ids)))
            # median fp cube
            with warnings.catch_warnings(record=True) as _:
                groupfp = np.nanmedian(cube, axis=0)
            # shift group to master
            gout = get_linear_transform_params(p, refimage, groupfp)
            transforms, xres, yres = gout
            # quality control on group
            if transforms is None:
                wmsg1 = 'Quality control failed for group {0}'.format(g_it + 1)
                wmsg2 = '\tImage quality too poor (sigma clip failed)'
                WLOG(p, 'warning', [wmsg1, wmsg2])
                # skip adding to group
                continue
            if (xres > qc_res) or (yres > qc_res):
                # log QC failure
                wmsg1 = 'Quality control failed for group {0}'.format(g_it + 1)
                wmsg2 = '\tXRES = {0} YRES = {1} (limit = {2})'
                wargs = [xres, yres, qc_res]
                WLOG(p, 'warning', [wmsg1, wmsg2.format(*wargs)])
                # skip adding to group
                continue

            groupfp = ea_transform(groupfp, lin_transform_vect=transforms)
            # append to cube
            fp_cube.append(groupfp)
            for filename in fp_ids:
                transforms_list.append(transforms)
    # convert fp cube to array
    fp_cube = np.array(fp_cube)
    # return fp_cube
    return fp_cube, np.array(transforms_list)


def xy_acc_peak(xpeak, ypeak, im):
    # black magic arithmetic for replace a 2nd order polynomial by
    # some arithmetic directly on pixel values to find
    # the maxima in x and y for each peak

    # vectors to contain peak pixels and its neighbours in x or y for
    # im1 and im2
    vvy = np.zeros([3, len(ypeak)])
    vvx = np.zeros([3, len(ypeak)])

    # pad values of neighbours in vv[xy][12]
    for i in range(-1, 2):
        vvy[i + 1, :] = im[ypeak + i, xpeak]
        vvx[i + 1, :] = im[ypeak, xpeak + i]

    # subtract peak pixel value
    vvx[0, :] -= vvx[1, :]
    vvx[2, :] -= vvx[1, :]

    # find the slope of the linear fix
    mx = (vvx[2, :] - vvx[0, :]) / 2

    # find the 2nd order of the polynomial
    ax = vvx[2, :] - mx

    # all the same in y direction for im
    vvy[0, :] -= vvy[1, :]
    vvy[2, :] -= vvy[1, :]

    my = (vvy[2, :] - vvy[0, :]) / 2
    ay = vvy[2, :] - my

    # peaks position is point of zero derivative. We add the integer
    # pixel value of [xy]peak[12]
    x1 = -0.5 * mx / ax + xpeak
    y1 = -0.5 * my / ay + ypeak

    return x1,y1


def twod_peak_fit(xx, yy, zz, size):
    # get peak position (in y and x)
    imax = np.argmax(zz)
    dy0, dx0 = imax // len(xx), imax % len(xx)
    # 2nd order fit to the cross-correlation peak (in y)
    if np.abs(yy[dy0]) <= (size - 2):
        # get the y start and end points
        d_start, d_end = dy0 - 1, dy0 + 2
        # calculate the center in y using polynomial fit (quadratic)
        coeffs = np.polyfit(yy[d_start:d_end], zz[d_start:d_end, dx0], 2)
        # add center 2nd order shift to the shift (differential of coeffs)
        yshift = -0.5 * coeffs[1] / coeffs[0]
    # else just add the max shift
    else:
        yshift = yy[dy0]

    # 2nd order fit to the cross-correlation peak (in x)
    if np.abs(xx[dx0] <= (size - 2)):
        # get the x start and end points
        d_start, d_end = dx0 - 1, dx0 + 2
        # calculate the center in x using polynomial fit (quadratic)
        coeffs = np.polyfit(xx[d_start:d_end], zz[dy0, d_start:d_end], 2)
        # add center 2nd order shift to the shift (differential of coeffs)
        xshift = -0.5 * coeffs[1] / coeffs[0]
    # else just add the max shift
    else:
        xshift = xx[dx0]
    # return the x and y shifts
    return yshift, xshift


def get_linear_transform_params(p, image1, image2):

    # get parameters from p
    maxn_percent = p['SHAPE_MASTER_VALIDFP_PERCENTILE']
    maxn_thres = p['SHAPE_MASTER_VALIDFP_THRESHOLD']
    niterations = p['SHAPE_MASTER_LINTRANS_NITER']
    ini_boxsize = p['SHAPE_MASTER_FP_INI_BOXSIZE']
    small_boxsize = p['SHAPE_MASTER_FP_SMALL_BOXSIZE']
    # get the shape of the image
    dim1, dim2 = image1.shape
    # check that image is correct shape
    if image2.shape != image1.shape:
        emsg = 'Image 1 (shape={0}) not the same as image 2 (shape={1})'
        WLOG(p, 'error', emsg.format(image1.shape, image2.shape))
    # linear transform vector
    # with dx0,dy0,A,B,C,D
    # we start assuming that there is no shift in x or y
    # and that the image is not sheared or rotated
    lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    # find the fp peaks (via max neighbours) in image1
    mask1 = max_neighbour_mask(image1, maxn_percent, maxn_thres)
    # copy image2
    image3 = np.array(image2)
    # print out initial conditions of linear transform vector
    WLOG(p, 'info', 'Linear transformation start point:')
    ltv = np.array(lin_transform_vect)
    wmsg1 = '\tdx={0:.6f} dy={1:.6f}'.format(*ltv)
    wargs2 = [dim2, (ltv[2] - 1) * dim2, ltv[3] * dim2]
    wmsg2 = '\t{0}(A-1)={1:.6f}\t{0}B={2:.6f}'.format(*wargs2)
    wargs3 = [dim2, ltv[3] * dim2, (ltv[5] - 1) * dim2]
    wmsg3 = '\t{0}C={1:.6f}\t{0}(D-1)={2:.6f}'.format(*wargs3)
    WLOG(p, '', [wmsg1, wmsg2, wmsg3])
    # loop around iterations
    for n_it in range(niterations):
        # log progress
        wmsg = 'Iteration {0}/{1}'
        WLOG(p, '', wmsg.format(n_it + 1, niterations))
        # transform image2 if we have some transforms (initial we don't)
        if n_it > 0:
            image3 = ea_transform(image2, lin_transform_vect)
        # find the fp peaks (via max neighbours) in image2
        mask2 = max_neighbour_mask(image3, maxn_percent, maxn_thres)
        # we search in +- wdd to find the maximum number of matching
        # bright peaks. We first explore a big +-11 pixel range, but
        # afterward we can scan a much smaller region
        if n_it == 0:
            wdd = ini_boxsize
        else:
            wdd = small_boxsize
        # define the scanning range in dx and dy
        dd = np.arange(-wdd, wdd + 1)
        map_dxdy = np.zeros([len(dd), len(dd)])
        # peaks cannot be at the edges of the image
        mask1[:wdd + 1, :] = False
        mask1[:, :wdd + 1] = False
        mask1[-wdd -1:, :] = False
        mask1[:, -wdd -1:] = False
        # get the positions of the x and y peaks (based on mask1)
        ypeak1, xpeak1 = np.where(mask1)
        # fill map_dxdy with the mean of the wdd box
        for y_it in range(len(dd)):
            for x_it in range(len(dd)):
                # get the boolean values for mask 2 for this dd
                boxvalues = mask2[ypeak1 + dd[y_it], xpeak1 + dd[x_it]]
                # push these values into the map
                map_dxdy[y_it, x_it] = np.mean(boxvalues)
        # get the shifts for these mapped values
        pos = np.argmax(map_dxdy)
        dy0, dx0 = -dd[pos // len(dd)], -dd[pos % len(dd)]
        # shift by integer if dx0 or dy0 is not 0
        # this is used later to ensures that the pixels found as
        # peaks in one image are also peaks in the other.
        mask2b = np.roll(np.roll(mask2, dy0, axis=0), dx0, axis=1)
        # position of peaks in 2nd image
        xpeak2 = np.array(xpeak1 - dx0, dtype=int)
        ypeak2 = np.array(ypeak1 - dy0, dtype=int)
        # peaks in image1 must be peaks in image2 when accounting for the
        # integer offset
        keep = mask2b[ypeak1, xpeak1]
        xpeak1 = xpeak1[keep]
        ypeak1 = ypeak1[keep]
        xpeak2 = xpeak2[keep]
        ypeak2 = ypeak2[keep]
        # do a fit to these positions in both images to get the peak centers
        x1, y1 = xy_acc_peak(xpeak1, ypeak1, image1)
        x2, y2 = xy_acc_peak(xpeak2, ypeak2, image3)
        # we loop on the linear model converting x1 y1 to x2 y2
        nbad, ampsx, ampsy = 1, np.zeros(3), np.zeros(3)

        n_terms = len(x1)
        while nbad != 0:
            # define vectory
            vvv = np.zeros([3, len(x1)])
            vvv[0, :], vvv[1, :], vvv[2, :] = np.ones_like(x1), x1, y1
            # linear minimisation of difference w.r.t. v
            ampsx, xrecon = spirouMath.linear_minimization(x1 - x2, vvv)
            ampsy, yrecon = spirouMath.linear_minimization(y1 - y2, vvv)
            # express distance of all residual error in x1-y1 and y1-y2
            # in absolute deviation
            xnanmed = np.nanmedian(np.abs((x1 - x2) - xrecon))
            ynanmed = np.nanmedian(np.abs((y1 - y2) - yrecon))
            xrms = ((x1 - x2) - xrecon) ** 2 / xnanmed
            yrms = ((y1 - y2) - yrecon) ** 2 / ynanmed
            # How many 'sigma' for the core of distribution
            nsig = np.sqrt(xrms ** 2 + yrms ** 2)
            with warnings.catch_warnings(record=True) as _:
                bad = nsig > 1.5
            # remove outliers and start again if there was one
            nbad = np.sum(bad)

            x1, x2 = x1[~bad], x2[~bad]
            y1, y2 = y1[~bad], y2[~bad]

            if len(x1) < (0.5 * n_terms):
                return None, None, None

        xres = np.std((x1 - x2) - xrecon)
        yres = np.std((y1 - y2) - yrecon)

        # we have our linear transform terms!
        dx0, dy0 = ampsx[0], ampsy[0]
        d_transform = [dx0, dy0, ampsx[1], ampsx[2], ampsy[1], ampsy[2]]
        # propagate to linear transform vector
        lin_transform_vect -= d_transform
        ltv = np.array(lin_transform_vect)
        # print out per iteration
        wmsg1 = '\tdx={0:.6f} dy={1:.6f}'.format(*ltv)
        wargs2 = [dim2, (ltv[2]-1) * dim2, ltv[3] * dim2]
        wmsg2 = '\t{0}(A-1)={1:.6f}\t{0}B={2:.6f}'.format(*wargs2)
        wargs3 = [dim2, ltv[3] * dim2, (ltv[5] - 1) * dim2]
        wmsg3 = '\t{0}C={1:.6f}\t{0}(D-1)={2:.6f}'.format(*wargs3)
        WLOG(p, '', [wmsg1, wmsg2, wmsg3])
    # plot if in debug mode
    if p['DRS_DEBUG'] > 0 and p['DRS_PLOT'] > 0:
        sPlt.shape_linear_trans_param_plot(p, image1, x1, x2, y1, y2)
    # return linear transform vector
    return lin_transform_vect, xres, yres


def max_neighbour_mask(image, percent, thres):
    # construct a cube with 8 slices that contain the 8 neighbours
    #   of any pixel. This is used to find pixels brighter that their
    #   neighbours
    box = np.zeros([9, image.shape[0], image.shape[1]], dtype=float)
    xpos, ypos = np.indices([3, 3]) - 1
    # loop around
    for it in range(len(xpos.flatten())):
        dx, dy = xpos.flatten()[it], ypos.flatten()[it]
        if (dx == 0) and (dy == 0):
            box[it] = np.nan
        else:
            box[it] = np.roll(np.roll(image, dx, axis=0), dy, axis=1)
    # maximum value of neighbouring pixels
    with warnings.catch_warnings(record=True) as _:
        max_neighbours = np.nanmax(box, axis=0)

    # find pixels brighter than neighbours and brighter than 80th percentile
    # of image. These are the peaks of FP lines
    # we also impose that the pixel be within 1.5x of its neighbours
    # to filter-out noise excursions
    with warnings.catch_warnings(record=True) as _:
        mask = (image > max_neighbours)
        mask &= (image > np.nanpercentile(image, percent))
        mask &= (image / max_neighbours < thres)
    # return mask of where peaks are
    return mask


def ea_transform(image, lin_transform_vect=None, dxmap=None, dymap=None):
    """
    Shifts / transforms image by three different transformations:

    a) a linear transform (defined by "lin_transform_vect")

        this is a list of components for the shift:
            dx, dy, A, B, C, D
        where dx and dy are shifts in x and y and A, B, C, D form the
        transform matrix:

                    [ A   B
                      C   D ]

    b) a shift in x position (dxmap) where a shift is defined for each pixel

    c) a shift in y position (dymap) where a shift is defined for each pixel

    :param image: numpy array (2D), the image to transform
    :param lin_transform_vect: np.ndarray [size=6], the linear transform
                               parameters (dx, dy, A, B, C, D)
    :param dxmap: numpy array (2D), the x shift map (same size as image)
    :param dymap: numpy array (2D), the y shift map (same size as image)

    :type image: np.ndarray
    :type lin_transform_vect: np.ndarray
    :type dxmap: np.ndarray
    :type dymap: np.ndarray

    :returns: The transformed image
    :rtype: np.ndarray
    """
    func_name = __NAME__ + '.ea_transform()'
    # check size of dx and dy map
    if dxmap is not None:
        if dxmap.shape != image.shape:
            emsg = ('Incorrect shape for dx map (shape={0}) must be {1}'
                    '\n\t function = {2}')
            eargs = [dxmap.shape, image.shape, func_name]
            raise ValueError(emsg.format(*eargs))
    if dymap is not None:
        if dymap.shape != image.shape:
            emsg = ('Incorrect shape for dy map (shape={0}) must be {1}'
                    '\n\t function = {2}')
            eargs = [dxmap.shape, image.shape, func_name]
            raise ValueError(emsg.format(*eargs))
    # deal with no linear transform required (just a dxmap or dymap shift)
    if lin_transform_vect is None:
        lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    # copy the image
    image = np.array(image)
    # transforming an image with the 6 linear transform terms
    # Be careful with NaN values, there should be none
    dx, dy, A, B, C, D = lin_transform_vect
    # get the pixel locations for the image
    yy, xx = np.indices(image.shape, dtype=float)
    # get the shifted x pixel locations
    xx2 = dx + xx * A + yy * B
    if dxmap is not None:
        xx2 += dxmap
    # get the shifted y pixel locations
    yy2 = dy + xx * C + yy * D
    if dymap is not None:
        yy2 += dymap
    # get the valid (non Nan) pixels
    valid_mask = np.isfinite(image)
    # set the weight equal to the valid pixels (1 for valid, 0 for not valid)
    weight = valid_mask.astype(float)
    # set all NaNs to zero (for transform)
    image[~valid_mask] = 0
    # we need to properly propagate NaN in the interpolation.
    out_image = mapc(image, [yy2, xx2], order=2, cval=np.nan, output=float,
                     mode='constant')
    out_weight = mapc(weight, [yy2, xx2], order=2, cval=0, output=float,
                      mode='constant')
    # divide by the weight (NaN pixels)
    with warnings.catch_warnings(record=True) as _:
        out_image = out_image / out_weight
        out_image[out_weight < 0.5] = np.nan
    # return transformed image
    return out_image


# =============================================================================
# Get basic image properties
# =============================================================================
def get_files(p, filetype=None, allowedtypes=None):

    # get parameters from p
    path = p['ARG_FILE_DIR']
    if filetype is None:
        WLOG(p, 'error', 'Filetype not set')
    if allowedtypes is None:
        WLOG(p, 'error', 'Allowed types not set')
    # -------------------------------------------------------------------------
    # check file type is allowed
    if filetype not in allowedtypes:
        emsgs = ['Invalid file type = {0}'.format(filetype),
                 '\t Must be one of the following']
        for allowedtype in allowedtypes:
            emsgs.append('\t\t - "{0}"'.format(allowedtype))
        WLOG(p, 'error', emsgs)
    # -------------------------------------------------------------------------
    # get index files
    index_files = []
    # walk through path and find index files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == spirouConfig.Constants.INDEX_OUTPUT_FILENAME():
                index_files.append(os.path.join(root, filename))
    # log number of index files found
    if len(index_files) > 0:
        wmsg = 'Found {0} index files'
        WLOG(p, '', wmsg.format(len(index_files)))
    else:
        emsg = ('No index files found. Please run a off_listing script to '
                'continue')
        WLOG(p, 'error', emsg)
    # -------------------------------------------------------------------------
    # valid files dictionary (key = telluric object name)
    valid_files = []
    # ---------------------------------------------------------------------
    # loop through index files
    for index_file in index_files:
        # read index file
        index = spirouTable.read_fits_table(p, index_file)
        # get directory
        dirname = os.path.dirname(index_file)
        # -----------------------------------------------------------------
        # get filename and object name
        index_filenames = index['FILENAME']
        index_output = index[p['KW_DPRTYPE'][0]]
        # -----------------------------------------------------------------
        # mask by KW_OUTPUT
        mask = index_output == filetype
        # -----------------------------------------------------------------
        # append found files to this list
        if np.nansum(mask) > 0:
            for filename in index_filenames[mask]:
                # construct absolute path
                absfilename = os.path.join(dirname, filename)
                # check that file exists
                if not os.path.exists(absfilename):
                    continue
                # append to storage
                if absfilename not in valid_files:
                    valid_files.append(absfilename)
    # ---------------------------------------------------------------------
    # log found
    wmsg = '\tFound {0} {1} files'.format(len(valid_files), filetype)
    WLOG(p, '', wmsg)
    # return full list
    return valid_files


def group_files_by_time(p, times, time_thres, time_unit='hours'):
    func_name = __NAME__ + '.group_files_by_time()'
    # make sure time units are correct
    if time_unit == 'hours':
        time_thres = time_thres / 24
    elif time_unit == 'days':
        pass
    else:
        emsg1 = 'Time unit not supported must be "hours" or "days"'
        emsg2 = 'function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # ID of matched multiplets of files
    matched_id = np.zeros_like(times, dtype=int)
    # loop until all files are matched with all other files taken within
    #    DARK_MASTER_MATCH_TIME
    group_num, it = 1, 0
    while np.min(matched_id) == 0 and it < len(times):
        # find all non-matched dark times
        non_matched = matched_id == 0
        # find the first non-matched dark time
        first = np.min(np.where(non_matched)[0])
        # find all non-matched that are lower than threshold (in days)
        group_mask = np.abs(times[first] - times) < time_thres
        # add this group to matched_id
        matched_id[group_mask] = group_num
        # change the group number (add 1)
        group_num += 1
        # increase iterator
        it += 1
    # return the group match id
    return matched_id


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


def get_param(p, hdr, keyword, name=None, return_value=False, dtype=None,
              required=True):
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
    :param required: bool, if True raises error if keyword not found, if False
                     returns a value of None if keyword not found

    :return value: if return_value is True value of parameter is returned
    :return p: if return_value is False, updated parameter dictionary p with
               key = name is returned
    """
    func_name = __NAME__ + '.get_param()'

    # get header keyword
    try:
        key = p[keyword][0]
    except Exception as e:
        key = keyword

    # deal with no name
    if name is None:
        name = key
    # get raw value
    rawvalue = spirouFITS.keylookup(p, hdr, key, required=required)
    # get type casted value
    try:
        if rawvalue is None:
            value = None
        elif dtype is None:
            dtype = float
            value = float(rawvalue)
        elif type(dtype) == type:
            value = dtype(rawvalue)
        else:
            emsg1 = 'Dtype "{0}" is not a valid python type. Keyword={1}'
            emsg2 = '     function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1.format(dtype, keyword), emsg2])
            value = None
    except ValueError:
        if not required:
            value = None
        else:
            emsg1 = ('Cannot convert keyword "{0}"="{1}" to type "{2}"'
                     '').format(keyword, rawvalue, dtype)
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
            value = None
    except TypeError:
        if not required:
            value = None
        else:
            emsg = 'Cannot convert "{0}" to type "{1}"'.format(rawvalue, dtype)
            WLOG(p, 'error', emsg)


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
    if p['KW_CDBWAVE'][0] in hdr:
        wkwargs = dict(p=p, hdr=hdr, return_value=True)
        loc['WAVETIME1'] = get_param(keyword='KW_WAVE_TIME1', dtype=str,
                                     **wkwargs)
        loc['WAVETIME2'] = get_param(keyword='KW_WAVE_TIME2', **wkwargs)
    # else we have got the wave info from the calibDB
    else:
        # log warning
        wmsg = 'Warning key="{0}" not in HEADER file (Using CalibDB)'
        WLOG(p, 'warning', wmsg.format(p['KW_CDBWAVE'][0]))
        # get parameters from the calibDB
        calib_time_human = spirouDB.GetAcqTime(p, hdr)
        fmt = spirouConfig.Constants.DATE_FMT_HEADER()
        calib_time_unix = spirouMath.stringtime2unixtime(calib_time_human, fmt)
        # set the parameters in wave
        loc['WAVETIME1'] = calib_time_human
        loc['WAVETIME2'] = calib_time_unix
    # set sources
    loc.set_sources(['WAVETIME1', 'WAVETIME2'], func_name)
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
def e2dstos1d_old(wave, e2dsffb, sbin):
    """
    Convert E2DS (2-dimension) spectra to 1-dimension spectra
    with merged spectral orders and regular sampling


    :param wave: wavelength solution
    :param e2dsffb : e2ds falt-fielded and blaze corrected
    :param sbin : S1d sampling in nm
    """
    # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
    for o in range(len(e2dsffb)):

        x = wave[o] * 1.
        y = e2dsffb[o] * 1.

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Integral Calculation yy by summation
        parts = [np.array([x[1] - x[0]]),
                 (x[2:] - x[0:-2]) / 2.,
                 np.array([x[-1] - x[-2]])]
        dx = np.concatenate(parts)
        # stepmax = np.max(dx)
        yy = np.concatenate((np.array([0.]), np.cumsum(y * dx)))
        # xx = np.concatenate((x - dx / 2., np.array([x[-1] + dx[-1] / 2.])))

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Computation of the new coordinates
        #   if o == 0:
        xx = x[y > 0]
        l1 = 1. * (int(xx[0] * (1. / sbin)) + 1) / (1. / sbin) + sbin
        l2 = 1. * (int(xx[-1] * (1. / sbin))) / (1. / sbin) - sbin
        #   else:
        #       l1 = 1. * (int(x[0] * (1. / bin)) + 1) / (1. / bin) + bin
        #       l2 = 1. * (int(x[-1] * (1. / bin))) / (1. / bin) - bin

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Interpolation by cubic spline
        xxi = np.arange(l1, l2 + sbin, sbin) - sbin / 2.
        yyi = griddata(xx, yy, xxi, method='cubic')

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Computation of the derivation
        xi = xxi[0:-1] + sbin / 2.
        yi = (yyi[1:] - yyi[0:-1]) / sbin

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # Merging of orders
        if o == 0:
            xs1d = xi * 1.
            ys1d = yi * 1.

        # TODO: FIX PROBLEMS: ADD COMMENTS TO SECTION + Fix PEP8
        # noinspection PyUnboundLocalVariable
        lim1 = xs1d[-1]
        lim2 = xi[0]
        if lim1 < lim2:
            zone0x = np.arange(lim1 + sbin, lim2, sbin)
            zone0y = np.zeros(len(zone0x), 'd')
            # noinspection PyUnboundLocalVariable
            ys1d = np.concatenate((ys1d, zone0y, yi))
            xs1d = np.concatenate((xs1d, zone0x, xi))
        else:
            ind = int(round((lim1 - lim2) / sbin))
            w = 1. - np.arange(ind * 1. + 1.) / ind
            # noinspection PyUnboundLocalVariable
            zonec = ys1d[-ind - 1:] * w + yi[0:ind + 1] * (1. - w)
            ys1d = np.concatenate((ys1d[:-ind - 1], zonec, yi[ind + 1:]))
            xs1d = np.concatenate((xs1d[:-ind - 1], xi))

    # noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
    return xs1d, ys1d



def e2dstos1d(p, wave, e2ds, blaze, wgrid='wave'):
    """
    Go from E2DS with a wave solution and blaze solution to a 1D spectrum

    :param p:
    :param wave:
    :param e2ds:
    :param blaze:
    :return:
    """

    # get parameters from p
    wavestart = p['EXTRACT_S1D_WAVESTART']
    waveend = p['EXTRACT_S1D_WAVEEND']
    binwave = p['IC_BIN_S1D_UWAVE']
    binvelo = p['IC_BIN_S1D_UVELO']
    smooth_size = p['IC_S1D_EDGE_SMOOTH_SIZE']
    blazethres = p['TELLU_CUT_BLAZE_NORM']

    # get size from e2ds
    nord, npix = e2ds.shape

    # -------------------------------------------------------------------------
    # Decide on output wavelength grid
    # -------------------------------------------------------------------------
    if wgrid == 'wave':
        wavegrid = np.arange(wavestart, waveend + binwave/2.0, binwave)
    else:
        # work out number of wavelength points
        flambda = np.log(waveend/wavestart)
        nlambda = np.round((speed_of_light / binvelo) * flambda)
        # updating end wavelength slightly to have exactly 'step' km/s
        waveend = np.exp(nlambda * (binvelo / speed_of_light)) * wavestart
        # get the wavegrid
        index = np.arange(nlambda) / nlambda
        wavegrid = wavestart * np.exp(index * np.log(waveend / wavestart))

    # -------------------------------------------------------------------------
    # define a smooth transition mask at the edges of the image
    # this ensures that the s1d has no discontinuity when going from one order
    # to the next. We define a scale for this mask
    # smoothing scale
    # -------------------------------------------------------------------------
    # define a kernal that goes from -3 to +3 smooth_sizes of the mask
    xker = np.arange(-smooth_size * 3, smooth_size * 3, 1)
    ker = np.exp(-0.5*(xker / smooth_size)**2)
    # set up the edge vector
    edges = np.ones(npix, dtype=bool)
    # set edges of the image to 0 so that  we get a sloping weight
    edges[:int(3 * smooth_size)] = False
    edges[-int(3 * smooth_size):] = False
    # define the weighting for the edges (slopevector)
    slopevector = np.zeros_like(blaze)
    # for each order find the sloping weight vector
    for order_num in range(nord):
        # get the blaze for this order
        oblaze = blaze[order_num]
        # find the valid pixels
        cond1 = np.isfinite(oblaze) & np.isfinite(e2ds[order_num])
        with warnings.catch_warnings(record=True) as _:
            cond2 = oblaze > (blazethres * np.nanmax(oblaze))
        valid = cond1 & cond2 & edges
        # convolve with the edge kernel
        oweight = np.convolve(valid, ker, mode='same')
        # normalise to the maximum
        oweight = oweight - np.nanmin(oweight)
        oweight = oweight / np.nanmax(oweight)
        # append to sloping vector storage
        slopevector[order_num] = oweight

    # multiple the spectrum and blaze by the sloping vector
    blaze = blaze * slopevector
    e2ds = e2ds * slopevector

    # -------------------------------------------------------------------------
    # Perform a weighted mean of overlapping orders
    # by performing a spline of both the blaze and the spectrum
    # -------------------------------------------------------------------------
    out_spec = np.zeros_like(wavegrid)
    weight = np.zeros_like(wavegrid)
    # loop around all orders
    for order_num in range(nord):
        # identify the valid pixels
        valid = np.isfinite(e2ds[order_num]) & np.isfinite(blaze[order_num])
        # if we have no valid points we need to skip
        if np.sum(valid) == 0:
            continue
        # get this orders vectors
        owave = wave[order_num, valid]
        oe2ds = e2ds[order_num, valid]
        oblaze = blaze[order_num, valid]
        # create the splines for this order
        spline_sp = IUVSpline(owave, oe2ds, k=5, ext=1)
        spline_bl = IUVSpline(owave, oblaze, k=5, ext=1)
        # can only spline in domain of the wave
        useful_range = (wavegrid > np.nanmin(owave))
        useful_range &= (wavegrid < np.nanmax(owave))
        # get splines and add to outputs
        weight[useful_range] += spline_bl(wavegrid[useful_range])
        out_spec[useful_range] += spline_sp(wavegrid[useful_range])

    # need to deal with zero weight --> set them to NaNs
    zeroweights = weight == 0
    weight[zeroweights] = np.nan

    # debug plot
    if p['DRS_PLOT'] > 0 and p['DRS_DEBUG'] > 0:
        sPlt.ext_1d_spectrum_debug_plot(p, wavegrid, out_spec, weight, wgrid)

    # work out the weighted spectrum
    with warnings.catch_warnings(record=True) as _:
        w_out_spec = out_spec / weight

    # divide by weights
    return wavegrid, w_out_spec


# =============================================================================
# End of code
# =============================================================================
