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
from scipy.ndimage import filters

from SpirouDRS import spirouCDB
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

    :param image:
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
            newimage = image * p['exptime'] * p['gain']
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
            newimage = image * p['exptime']
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
            WLOG('error', p['log_opt'], [emsg1, emsg2])
    # get file prefix and suffix
    if prefix is None:
        prefix = p['arg_file_names'][0][0:5]
    if suffix is None:
        suffix = p['arg_file_names'][0][-8:]
    # constrcut file string
    filestring = '{0}*{1}'.format(prefix, suffix)
    locstring = os.path.join(directory, filestring)
    # get all files
    filelist = glob.glob(locstring)
    # sort list
    filelist = np.sort(filelist)
    # return file list
    return list(filelist)


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
        WLOG('error', pp['log_opt'], [emsg1, emsg2])
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
        WLOG('error', pp['log_opt'], [e.message, emsg])
        qmin, qmax = None, None
    # get the histogram for flattened data
    try:
        histo = np.histogram(fimage, bins=pp['HISTO_BINS'],
                             range=(pp['HISTO_RANGE_LOW'],
                                    pp['HISTO_RANGE_HIGH']))
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', pp['log_opt'], [e.message, emsg])
        histo = None
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    wargs = ['In {0}'.format(image_name), dadead, med, pp['DARK_QMIN'],
             pp['DARK_QMAX'], qmin, qmax]
    wmsg = ('{0:12s}: Frac dead pixels= {1:.1f} % - Median= {2:.2f} ADU/s - '
            'Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s')
    WLOG('info', pp['log_opt'], wmsg.format(*wargs))
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
                   p['nbframes']
    :param return_dark: bool, if True returns corrected_image and dark
                        if False (default) returns corrected_image

    :return corrected_image: numpy array (2D), the dark corrected image
                             only returned if return_dark = True:
    :return darkimage: numpy array (2D), the dark
    """
    func_name = __NAME__ + '.correct_for_dark()'
    if nfiles is None:
        nfiles = p['nbframes']

    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = spirouCDB.GetAcqTime(p, header)
        # get calibDB
        cdb, p = spirouCDB.GetDatabase(p, acqtime)
    else:
        try:
            cdb = p['calibDB']
            acqtime = p['max_time_unix']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG('error', p['log_opt'], [e.message, emsg])
            cdb, acqtime = None, None

    # try to read 'DARK' from cdb
    if 'DARK' in cdb:
        darkfile = os.path.join(p['DRS_CALIB_DB'], cdb['DARK'][1])
        WLOG('', p['log_opt'], 'Doing Dark Correction using ' + darkfile)
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
        WLOG('error', p['log_opt'], [emsg1.format(masterfile, acqtime), emsg2])
        corrected_image, darkimage = None, None

    # finally return datac
    if return_dark:
        return corrected_image, darkimage
    else:
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
    WLOG('', p['log_opt'], 'Normalising the flat')

    # get used percentile
    if percentile is None:
        try:
            percentile = p['BADPIX_NORM_PERCENTILE']
        except spirouConfig.ConfigError as e:
            emsg = '    function = {0}'.format(func_name)
            WLOG('error', p['log_opt'], [e.message, emsg])

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
            WLOG('error', p['log_opt'], [e.message, emsg])

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
    WLOG('', p['log_opt'], 'Looking for bad pixels')
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
            WLOG('error', p['log_opt'], [e.message, emsg])

    # maxi differential pixel response relative to the expected value
    try:
        cut_ratio = p['BADPIX_FLAT_CUT_RATIO']
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', p['log_opt'], [e.message, emsg])
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
        WLOG('error', p['log_opt'], [e.message, emsg])
        illum_cut = None
    # hotpix. Max flux in ADU/s to be considered too hot to be used
    try:
        max_hotpix = p['BADPIX_MAX_HOTPIX']
    except spirouConfig.ConfigError as e:
        emsg = '    function = {0}'.format(func_name)
        WLOG('error', p['log_opt'], [e.message, emsg])
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
        WLOG('error', p['log_opt'], [emsg1.format(*eargs), emsg2])
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
    text = ['Fraction of hot pixels from dark: {0:.2f} %',
            'Fraction of bad pixels from flat: {0:.2f} %',
            'Fraction of non-finite pixels in dark: {0:.2f} %',
            'Fraction of non-finite pixels in flat: {0:.2f} %',
            'Fraction of bad pixels with all criteria: {0:.2f} %']
    badpix_stats = [np.mean(badpix_dark) * 100, np.mean(badpix_flat) * 100,
                    np.mean(~valid_dark) * 100, np.mean(~valid_flat) * 100,
                    np.mean(badpix_map) * 100]

    for it in range(len(text)):
        WLOG('', p['log_opt'], text[it].format(badpix_stats[it]))
    # -------------------------------------------------------------------------
    # return bad pixel map
    return badpix_map, badpix_stats


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
    nbo = lloc['number_orders']
    # storage for "nbcos"
    # Question: what is nbcos? as it isn't used
    lloc['nbcos'] = np.zeros(nbo, dtype=int)
    lloc.set_source('nbcos', __NAME__ + '/get_tilt()')
    # storage for tilt
    lloc['tilt'] = np.zeros(int(nbo/2), dtype=float)
    lloc.set_source('tilt', __NAME__ + '/get_tilt()')
    # Over sample the data and interpolate new extraction values
    pixels = np.arange(image.shape[1])
    os_fac = pp['ic_tilt_coi']
    os_pixels = np.arange(image.shape[1] * os_fac) / os_fac
    # loop around each order
    for order_num in range(0, nbo, 2):
        # extract this AB order
        lloc = spirouEXTOR.ExtractABOrderOffset(pp, lloc, image, order_num)
        # --------------------------------------------------------------------
        # interpolate the pixels on to the extracted centers
        cent1i = np.interp(os_pixels, pixels, lloc['cent1'])
        cent2i = np.interp(os_pixels, pixels, lloc['cent2'])
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
        angle = np.rad2deg(-1 * np.arctan(delta / (2 * lloc['offset'])))
        # log the tilt and angle
        wmsg = 'Order {0}: Tilt = {1:.2f} on pixel {2:.1f} = {3:.2f} deg'
        wargs = [order_num / 2, delta, 2 * lloc['offset'], angle]
        WLOG('', pp['log_opt'], wmsg.format(*wargs))
        # save tilt angle to lloc
        lloc['tilt'][int(order_num / 2)] = angle
    # return the lloc
    return lloc


def fit_tilt(pp, lloc):
    """
    Fit the tilt (lloc['tilt'] with a polynomial of size = p['ic_tilt_filt']
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
    xfit = np.arange(lloc['number_orders']/2)
    # get fit coefficients for the tilt polynomial fit
    atc = np.polyfit(xfit, lloc['tilt'], pp['IC_TILT_FIT'])[::-1]
    # get the yfit values for the fit
    yfit = np.polyval(atc[::-1], xfit)
    # get the rms for the residuls of the fit and the data
    rms = np.std(lloc['tilt'] - yfit)
    # store the fit data in lloc
    lloc['xfit_tilt'] = xfit
    lloc.set_source('xfit_tilt', __NAME__ + '/fit_tilt()')
    lloc['yfit_tilt'] = yfit
    lloc.set_source('yfit_tilt', __NAME__ + '/fit_tilt()')
    lloc['a_tilt'] = atc
    lloc.set_source('a_tilt', __NAME__ + '/fit_tilt()')
    lloc['rms_tilt'] = rms
    lloc.set_source('rms_tilt', __NAME__ + '/fit_tilt()')

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

    # TODO: what are ll and amp
    :return ll:
    :return amp:
    """

    func_name = __NAME__ + '.read_line_list()'
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.CDATA_REL_FOLDER()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # deal with p and filename being None
    if p is None and filename is None:
        emsg1 = 'p (ParamDict) or "filename" must be defined'
        emsg2 = '    function={0}'.format(func_name)
        WLOG('error', p['log_opt'], [emsg1, emsg2])
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
        WLOG('error', p['log_opt'], [emsg1, emsg2])
        linefile = ''
    # check that line file exists
    if not os.path.exists(linefile):
        emsg1 = 'Line list file={0} does not exist.'.format(linefile)
        emsg2 = '    function={0}'.format(func_name)
        WLOG('error', p['log_opt'], [emsg1, emsg2])
    # read filename as a table
    linetable = spirouTable.read_table(linefile, fmt='ascii',
                                       colnames=['ll', 'amp'])
    # push columns into numpy arrays and force to floats
    ll = np.array(linetable['ll'], dtype=float)
    amp = np.array(linetable['amp'], dtype=float)
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
    rawvalue = spirouFITS.keylookup(p, hdr, key, hdr['@@@hname'])
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
            WLOG('error', p['log_opt'], [emsg1.format(dtype, keyword), emsg2])
            value = None
    except ValueError:
        emsg1 = ('Cannot convert keyword "{0}" to type "{1}"'
                 '').format(keyword, dtype)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['log_opt'], [emsg1, emsg2])
        value = None

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
    :param kind: string, 'human' for 'YYYY-mm-dd-HH-MM-SS.ss' or 'unix'
                 for time since 1970-01-01
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
    value = spirouCDB.GetAcqTime(p, hdr, kind=kind)
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


# =============================================================================
# End of code
# =============================================================================
