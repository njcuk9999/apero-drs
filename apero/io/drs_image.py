#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions for dealing with APERO images

Created on 2019-03-21 at 14:28

@author: cook

Import rules:
    only from core.core.drs_log, core.io, core.math, core.constants,
    apero.lang, apero.base

    do not import from core.core.drs_file
    do not import from core.core.drs_argument
    do not import from core.core.drs_database
"""
import os
import warnings
from typing import Any, Dict, List, Optional, Union, Tuple

import numpy as np
from scipy.ndimage.morphology import binary_erosion, binary_dilation

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_log
from apero.core.core import drs_misc
from apero.io import drs_fits
from apero.io import drs_path

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_path.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# Get function string
display_func = drs_log.display_func


# =============================================================================
# Define functions
# =============================================================================
def rotate_image(image: np.ndarray, rotnum: int) -> np.ndarray:
    """
    Rotates the image by a given rotation (rotnum)

    rotnum = 0 -> same as input
    rotnum = 1 -> 90deg counter-clock-wise
    rotnum = 2 -> 180deg
    rotnum = 3 -> 90deg clock-wise
    rotnum = 4 -> flip top-bottom
    rotnum = 5 -> flip top-bottom and rotate 90 deg counter-clock-wise
    rotnum = 6 -> flip top-bottom and rotate 180 deg
    rotnum = 7 -> flip top-bottom and rotate 90 deg clock-wise
    rotnum >=8 -> performs a modulo 8 anyway

    :param image: numpy array (2D), the image to rotate
    :param rotnum: integer between 0 and 7

    :type image: np.ndarray
    :type rotnum: int

    :return newimage:  numpy array (2D), the rotated image
    """
    # set function name
    # _ = display_func('rotate_image', __NAME__)
    # return math functino to rotate
    return mp.rot8(image, rotnum)


def resize(params: ParamDict, image: np.ndarray,
           x: Union[np.ndarray, None] = None, y: Union[np.ndarray, None] = None,
           xlow: int = 0, xhigh: Union[int, None] = None, ylow: int = 0,
           yhigh: Union[int, None] = None) -> Union[np.ndarray, None]:
    """
    Resize an image based on a pixel values

    :param params: ParamDict, parameter dictionary of constants
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
                 if None default is image.shape[0]

    if getshape = True
    :return newimage: numpy array (2D), the new resized image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]

    if getshape = False
    :return newimage: numpy array (2D), the new resized image
    """
    # set function name
    func_name = display_func('resize', __NAME__)
    # Deal with no low/high values
    if xhigh is None:
        xhigh = image.shape[1]
    if yhigh is None:
        yhigh = image.shape[0]
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
            eargs = ['xlow', 'xhigh', xlow, func_name]
            WLOG(params, 'error', textentry('00-001-00023', args=eargs))
        else:
            x = np.arange(xlow, xhigh)
        # deal with ylow > yhigh
        if ylow > yhigh:
            y = np.arange(yhigh + 1, ylow + 1)[::-1]
        elif ylow == yhigh:
            eargs = ['ylow', 'yhigh', xlow, func_name]
            WLOG(params, 'error', textentry('00-001-00023', args=eargs))
        else:
            y = np.arange(ylow, yhigh)
    # construct the new image (if one can't raise error)
    try:
        newimage = np.take(np.take(image, x, axis=1), y, axis=0)
    except Exception as e:
        eargs = [xlow, xhigh, ylow, yhigh, type(e), e, func_name]
        WLOG(params, 'error', textentry('00-001-00024', args=eargs))
        newimage = None
    # return error if we removed all pixels
    if newimage.shape[0] == 0 or newimage.shape[1] == 0:
        eargs = [xlow, xhigh, ylow, yhigh, func_name]
        WLOG(params, 'error', textentry('00-001-00025', args=eargs))
        newimage = None

    # return new image
    return newimage


def flip_image(params: ParamDict, image: np.ndarray, fliprows: bool = True,
               flipcols: bool = True) -> np.ndarray:
    """
    Flips the image in the x and/or the y direction

    :param params: ParamDict, the constants parameter dictionary
    :param image: numpy array (2D), the image
    :param fliprows: bool, if True reverses row order (axis = 0)
    :param flipcols: bool, if True reverses column order (axis = 1)

    :return newimage: numpy array (2D), the flipped image
    """
    # set function name
    func_name = display_func('flip_image', __NAME__)
    # raise error if image is not 2D
    if len(image.shape) < 2:
        eargs = [image.shape, func_name]
        WLOG(params, 'error', textentry('09-002-00001', args=eargs))
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


def convert_to_e(params: ParamDict, image: np.ndarray,
                 gain: Union[float, None] = None,
                 exptime: Union[float, None] = None) -> np.ndarray:
    """
    Converts image from ADU/s into e-

    :param params: parameter dictionary, ParamDict containing constants
            Must contain at least: (if exptime is None)
                exptime: float, the exposure time of the image
                gain: float, the gain of the image
    :param image: numpy array (2D), the image

    :param gain: float, if set overrides params['GAIN'], used as the gain
                   to multiple the image by
    :param exptime: float, if set overrides params['EXPTIME'], used as the
                      exposure time the image is multiplied by

    :return newimage: numpy array (2D), the image in e-
    """
    # set function name
    func_name = display_func('convert_to_e', __NAME__)
    # get constants from params / kwargs
    _gain = pcheck(params, 'GAIN', func=func_name, override=gain)
    _exptime = pcheck(params, 'EXPTIME', func=func_name, override=exptime)
    # correct image
    newimage = image * _gain * _exptime
    # return corrected image
    return newimage


def convert_to_adu(params: ParamDict, image: np.ndarray,
                   exptime=Union[float, None]) -> np.ndarray:
    """
    Converts image from ADU/s into ADU

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least: (if exptime is None)
            exptime: float, the exposure time of the image
    :param image: np.narray the image to convert to ADUs
    :param exptime: float, if set overrides params['EXPTIME'], used as the
                    exposure time the image is multiplied by

    :return newimage: numpy array (2D), the image in e-
    """
    # set function name
    func_name = display_func('convert_to_adu', __NAME__)
    # get constants from params / kwargs
    _exptime = pcheck(params, 'EXPTIME', func=func_name, override=exptime)
    # correct image
    newimage = image * _exptime
    # return corrected image
    return newimage


def clean_hotpix(image: np.ndarray, badpix: np.ndarray) -> np.ndarray:
    """
    Cleans an image by finding pixels that are high-sigma (positive or negative)
    outliers compared to their immediate neighbours. Bad pixels are
    interpolated with a 2D surface fit by using valid pixels within the
    3x3 pixel box centered on the bad pix.

    Pixels in big clusters of bad pix (more than 3 bad neighbours)
    are left as is

    First we construct a 'flattened' image
    We perform a low-pass filter along the x axis
    filtering the image so that only pixel-to-pixel structures
    remain. This is use to find big outliers in RMS.
    First we apply a median filtering, which removes big outliers
    and then we smooth the image to avoid big regions filled with zeros.
    Regions filled with zeros in the low-pass image happen when the local
    median is equal to the pixel value in the input image.

    We apply a 5-pix median boxcar in X and a 5-pix boxcar smoothing
    in x. This blurs along the dispersion over a scale of ~7 pixels.

    perform a [1,5] median filtering by rolling axis of a 2D image
    and constructing a 5*N*M cube, then taking a big median along axis=0
    analoguous to, but faster than :
        low_pass = signal.medfilt(image_rms_measurement, [1, 5])

    :param image: np.ndarray (2D) the image to fix the hot pixels for
    :param badpix: np.ndarray (2D) the bad pixel map to help fix bad pixel

    :return: np.array the image corrected for hot pixels
    """
    # set function name
    # _ = display_func('clean_hotpix', __NAME__)
    # copy the image
    image_rms_measurement = np.array(image)
    # make shifted cubes from +/- 2 pixels
    tmp = []
    for d in range(-2, 3):
        tmp.append(np.roll(image, d))
    tmp = np.array(tmp)
    # median along the shifted axis
    tmp = mp.nanmedian(tmp, axis=0)
    # same trick but for convolution with a [1,5] boxcar
    low_pass = np.zeros_like(tmp)
    # make a low pass shifted cube from +2/-2 pixels
    for d in range(-2, 3):
        low_pass += np.roll(tmp, d)
    # divide by the number of shifts
    low_pass /= 5
    # residual image showing pixel-to-pixel noise
    # the image is now centered on zero, so we can
    # determine the RMS around a given pixel
    image_rms_measurement -= low_pass

    abs_image_rms_measurement = np.abs(image_rms_measurement)
    # same as a [3,3] median filtering with signal.medfilt but faster
    tmp = []
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            tmp.append(np.roll(abs_image_rms_measurement, [dx, dy],
                               axis=[0, 1]))
    tmp = np.array(tmp)
    # median the cube
    rms = mp.nanmedian(tmp, axis=0)
    # the RMS cannot be arbitrarily small, so  we set
    # a lower limit to the local RMS at 0.5x the median
    # rms
    with warnings.catch_warnings(record=True) as _:
        rms[rms < (0.5 * mp.nanmedian(rms))] = 0.5 * mp.nanmedian(rms)
        # determining a proxy of N sigma
        nsig = image_rms_measurement / rms
        # TODO: remove hard-coded 10 value
        bad = np.array((np.abs(nsig) > 10), dtype=bool)
    # known bad pixels are also considered bad even if they are
    # within the +-N sigma rejection
    badpix = badpix | bad | ~np.isfinite(image)
    # we remove bad pixels at the periphery of the image
    # badpix[0, :] = False
    # badpix[-1, :] = False
    # badpix[:, 0] = False
    # badpix[:, -1] = False
    # find the pixel locations where we have bad pixels
    x, y = np.where(badpix)
    # set up the boxes
    box3d = np.zeros([len(x), 3, 3])
    keep3d = np.zeros([len(x), 3, 3], dtype=bool)
    # centering on zero
    # yy, xx = np.indices([3, 3]) - 1

    sz = image.shape
    # loop around the pixels in x and y
    for ix in range(-1, 2):
        for iy in range(-1, 2):
            # fill in the values for box and keep
            # box3d[:, ix + 1, iy + 1] = image[x + ix, y + iy]
            # keep3d[:, ix + 1, iy + 1] = ~badpix[x + ix, y + iy]
            box3d[:, ix + 1, iy + 1] = image[(x + ix) % sz[0], (y + iy) % sz[1]]
            keep3d[:, ix + 1, iy + 1] = ~badpix[(x + ix) % sz[0], (y + iy) % sz[1]]

    # find valid neighbours
    nvalid = np.sum(np.sum(keep3d, axis=1), axis=1)
    # keep only points with >5 valid neighbours
    box3d = box3d[nvalid > 5]
    keep3d = keep3d[nvalid > 5]
    x = x[nvalid > 5]
    y = y[nvalid > 5]
    nvalid = nvalid[nvalid > 5]
    # copy the original image
    image1 = np.array(image)
    # correcting bad pixels with a 2D fit to valid neighbours
    # pre-computing some values that are needed below
    # xx2 = xx ** 2
    # yy2 = yy ** 2
    # xy = xx * yy
    # ones = np.ones_like(xx)
    # loop around the x axis
    for it in range(len(x)):
        # get the keep and box values for this iteration
        keep = keep3d[it]
        box = box3d[it]
        if nvalid[it] == 8:
            # we fall in a special case where there is only a central pixel
            # that is bad surrounded by valid pixel. The central value is
            # straightforward to compute by using the means of 4 immediate
            # neighbours and the 4 corner neighbours.
            m1 = np.mean(box[[0, 1, 1, 2], [1, 0, 2, 1]])
            m2 = np.mean(box[[0, 0, 2, 2], [2, 0, 2, 0]])
            image1[x[it], y[it]] = 2 * m1 - m2
        else:

            image1[x[it], y[it]] = np.nanmean(box[keep])

        # else:
        #     # fitting a 2D 2nd order polynomial surface. As the xx=0, yy=0
        #     # corresponds to the bad pixel, then the first coefficient
        #     # of the fit (its zero point) corresponds to the value that
        #     # must be given to the pixel
        #     a = np.array([ones[keep], xx[keep], yy[keep], xx2[keep], yy2[keep],
        #                   xy[keep]])
        #     b = box[keep]
        #     # perform a least squares fit on a and b
        #     coeff, _ = mp.linear_minimization(b, a, no_recon=True)
        #     # this is equivalent to the slower command :
        #     # coeff = fit2dpoly(xx[keep], yy[keep], box[keep])
        #     image1[x[it], y[it]] = coeff[0]
    # return the cleaned image
    return image1


def get_fiber_types(params: ParamDict,
                    fibertypes: Union[List[str], None] = None,
                    fiber: Union[str, None] = None) -> List[str]:
    """
    Get the correct fiber types based on params['FIBER_TYPES'] - if fibertypes
    is set this is just returned, if fiber is 'ALL' return all fiber types,
    else if fiber is in fibers just return fiber in a list form.

    :param params: ParamDict, parameter dictionary of constants
    :param fibertypes: None or list of strings, if set this is the list of
                       fibers returned
    :param fiber: str or None, if set returns this fiber (in a list)

    :return: list of strings, the fibers allowed
    """
    # set function name
    func_name = display_func('get_fiber_types', __NAME__)
    # get parameter list from params/kwargs
    validfibertypes = params.listp('FIBER_TYPES', dtype=str)
    # if fiber types is defined then return it (assuming user knows best)
    if fibertypes is not None:
        return fibertypes

    # deal with no "FIBER" in "INPUTS"
    if "FIBER" not in params['INPUTS'] and fiber is None:
        return validfibertypes

    # get fiber from inputs (now that we know it is there)
    if fiber is None:
        if 'FIBER' in params['INPUTS']:
            fiber = str(params['INPUTS']['FIBER'])

    # deal with input from command line (via params['INPUTS'])
    if fiber.upper() == 'ALL':
        return validfibertypes
    elif fiber in validfibertypes:
        return [fiber]
    else:
        eargs = [fiber, ', '.join(validfibertypes), func_name]
        WLOG(params, 'error', textentry('09-001-00030', args=eargs))


def npy_filelist(params: ParamDict, name: str, index: int,
                 array: np.ndarray, filenames: Union[List[str], None],
                 subdir: Union[str, None] = None,
                 outdir: Union[str, None] = None) -> Tuple[List[str], str]:
    """
    Save a numpy array to a npy file and append to 'filenames' (or start a new
    list of 'filenames')

    file is named as follows:
        /LIM-{unixtime}-{random value}/{name}_{index}.npy

    :param params: ParamDict, parameter dictionary of constants
    :param name: str, the name to add to the npy filename (as a prefix)
    :param index: int, the iteration of this file
    :param array: np.array - the numay array to save in the npy file
    :param filenames: either None or a list of previous filenames
    :param subdir: str or None, if set replaces this default sub-directory
                   with user defined sub-directory (default is
                   LIM-{unixtime}-{random value})
    :param outdir: str  or None, the output dir for the subdirectory and npy
                   files to be save - if not set defaults to current directory

    :return: tuple, 1. the list of npy filenames, 2. the sub-directory name used
             to store npy filename
    """
    # set function name
    # _ = display_func('npy_filelist', __NAME__)
    # deal with no filenames
    if filenames is None:
        filenames = []
    # deal with not outdir
    if outdir is None:
        outdir = ''
    # deal with having no subdir
    if subdir is None:
        # get unix char code
        unixtime, humantime, rval = drs_misc.unix_char_code()
        # create subdir
        subdir = 'LIM-{0:020d}-{1}'.format(int(unixtime), rval)
    # construct file name
    filename = '{0}_{1:06d}.npy'.format(name, index)
    filepath = os.path.join(outdir, subdir)
    # create subdir
    if not os.path.exists(filepath):
        WLOG(params, '', 'Creating directory: {0}'.format(filepath))
        os.mkdir(filepath)
    # construct absolute path to file
    abspath = os.path.join(filepath, filename)
    # save to disk
    np.save(abspath, array)
    # add to list
    filenames.append(abspath)
    # return appended filenames list
    return filenames, subdir


def npy_fileclean(params: ParamDict, filenames: Union[List[str], None],
                  subdir: Union[str, None] = None,
                  outdir: Union[str, None] = None):
    """
    Remove all numpy files (after no longer needed) and the sub-directory they
    were saved to (a clean up)

    :param params: ParamDict, the parameter dictionary of constants
    :param filenames: None or list of npy files
    :param subdir: str or None, if set replaces this default sub-directory
                   with user defined sub-directory (default is
                   LIM-{unixtime}-{random value})
    :param outdir: str  or None, the output dir for the subdirectory and npy
                   files to be save - if not set defaults to current directory

    :return: None - removes npy files and subdir
    """
    # set function name
    # _ = display_func('npy_fileclean', __NAME__)
    # deal with not outdir
    if outdir is None:
        outdir = ''
    # remove files
    for filename in filenames:
        WLOG(params, '', 'Removing file: {0}'.format(filename))
        os.remove(filename)
    # construct file dir
    filepath = os.path.join(outdir, subdir)
    # ----------------------------------------------------------------------
    # delete the sub directory
    while os.path.exists(filepath):
        WLOG(params, '', 'Removing directory: {0}'.format(filepath))
        os.removedirs(filepath)


def large_image_combine(params: ParamDict, files: Union[List[str], np.ndarray],
                        math: str = 'median', fmt='fits', nmax: int = 2e7,
                        subdir: Union[str, None] = None,
                        outdir: Union[str, None] = None,
                        func: Optional[Any] = None,
                        fkwargs: Optional[Dict[str, Any]] = None
                        ) -> Union[np.ndarray, Tuple[np.ndarray, List[str]]]:
    """
    Pass a large list of images and combine in a memory efficient
    way. (math = 'median', 'mean', 'sum')

    Set the nmax parameter to the maximum number of pixels to load into memory
    Memory requirements = 64 bits * nmax

    i.e. nmax = 2e7 ~ 1.28 Gb

    :param params: the constant parameter dictionary
    :param files: list of strings, the files to open
    :param math: the mathematical operation to combine (median, mean, sum)
    :param fmt: the format of the file to large image combine (fits or npy)
    :param nmax: int, the maximum number of pixels to open at any given time
                 note assuming 64 bits per pixel this gives a direct memory
                 constraint - 2e7 pixels ~ 1.28 Gb
    :param subdir: None or string, the sub-directory to store temporary
                   products in - should be unique
    :param outdir: the output directory for intermediate products (if unset
                   uses the current directory)
    :param func: A function only taking the image and keyword arguments from
                 fkwargs as arguments as well as an additional "hdr"
                 keyword argument (containing the header of the image file)
                 Note hdr can be None
                 This function is applied to the image, it must return
                 the same shape image as a np.ndarray only

                 e.g.  def lowpass(image, hdr=None, width=101):
                            return image - lowpassfilter(image, width)

                       fkwargs = dict(width=101)

    :param fkwargs: Optional dictionary, if func is defined pass arguments to
                    pass to "func" (must be the same for all images)

    :type params: ParamDict
    :type files: List[str]
    :type nmax: int
    :type subdir: Union[str, None]
    :type outdir: Union[str, None]

    :return: numpy 2D array: the nan-median image of all files
    :rtype: np.ndarray
    """
    # set function name
    func_name = display_func('large_image_combine', __NAME__)
    # deal with math mode
    if math == 'median':
        cfunc = mp.nanmedian
    elif math == 'mean':
        cfunc = mp.nanmean
    elif math == 'sum':
        cfunc = mp.nansum
    else:
        emsg = 'Math error: {0} is invalid must be: {1}'
        eargs = [math, '"median" or "mean" or "sum"']
        WLOG(params, 'error', emsg.format(*eargs))
        cfunc = None
    # deal with not outdir
    if outdir is None:
        outdir = ''
    # deal with having no subdir
    if subdir is None:
        # get unix char code
        unixtime, humantime, rval = drs_misc.unix_char_code()
        # create subdir
        subdir = 'LIM-{0:020d}-{1}'.format(int(unixtime), rval)
    # construct file dir
    subfilepath = os.path.join(outdir, subdir)
    # create subdir
    if not os.path.exists(subfilepath):
        os.mkdir(subfilepath)
    # get the number of files
    numfiles = len(files)
    # ----------------------------------------------------------------------
    # load first image
    if fmt == 'fits':
        image0, hdr0 = drs_fits.readfits(params, files[0], gethdr=True)
    elif fmt == 'npy':
        image0 = drs_path.numpy_load(files[0])
        hdr0 = None
    else:
        # fmt="{0}" is incorrect
        eargs = [fmt, 'fits, npy', func_name]
        WLOG(params, 'error', textentry('00-001-00044', args=eargs))
        image0, hdr0 = None, None
    # ----------------------------------------------------------------------
    # deal with only having 1 file
    if numfiles == 1:
        # delete the sub directory
        if os.path.exists(subfilepath):
            os.removedirs(subfilepath)
        # ------------------------------------------------------------------
        # deal with no fkwargs
        if fkwargs is None:
            fkwargs = dict(hdr=hdr0)
        else:
            fkwargs['hdr'] = hdr0
        # apply a function to the image (if func is not None)
        if func is not None:
            image0 = func(image0, hdr=hdr0, **fkwargs)
        # return the only image
        return image0
    # ----------------------------------------------------------------------
    # get the shape of the image
    mdim1, mdim2 = np.array(image0.shape).astype(int)
    del image0
    # number of ribbons considering dimensions
    nribbons = int(np.ceil((mdim1 * mdim2 * numfiles / nmax)))
    # find pixels in each ribbon
    bins = np.array(np.arange(0, nribbons) / (nribbons - 1)).astype(int)
    bins = bins * mdim1
    # ----------------------------------------------------------------------
    # loop around files and save ribbons as numpy arrays
    for f_it, filename in enumerate(files):
        # log message so we know how far through we are
        # Processing file {0} / {1}
        wargs = [f_it + 1, numfiles]
        WLOG(params, '', textentry('40-000-00012', args=wargs))
        # ------------------------------------------------------------------
        # load file
        if fmt == 'fits':
            image, hdr = drs_fits.readfits(params, filename, gethdr=True)
        elif fmt == 'npy':
            image = drs_path.numpy_load(filename)
            hdr = None
        else:
            # fmt="{0}" is incorrect
            eargs = [fmt, 'fits, npy', func_name]
            WLOG(params, 'error', textentry('00-001-00044', args=eargs))
            image, hdr = None, None
        # get the shape of the image
        dim1, dim2 = np.array(image.shape).astype(int)
        # construct clean version of filename
        clean_filename = filename.replace('.', '_')
        # ------------------------------------------------------------------
        # check that dimensions are the same as first file
        if dim1 != mdim1 or dim2 != mdim2:
            # log error
            # Files are not the same shape
            eargs = [mdim1, mdim2, f_it, dim1, dim2, files[0], files[1],
                     func_name]
            WLOG(params, 'error', textentry('00-001-00045', args=eargs))
        # ------------------------------------------------------------------
        # deal with no fkwargs
        if fkwargs is None:
            fkwargs = dict(hdr=hdr)
        else:
            fkwargs['hdr'] = hdr
        # apply a function to the image (if func is not None)
        if func is not None:
            image = func(image, hdr=hdr, **fkwargs)
        # ------------------------------------------------------------------
        # extract and save ribbons
        for b_it in range(len(bins) - 1):
            # get ribbon from file
            ribbon = np.array(image[bins[b_it]: bins[b_it + 1]])
            # construct ribbon nmae
            ribbon_name = '{0}_ribbon{1:06d}.npy'.format(clean_filename, b_it)
            ribbon_path = os.path.join(subfilepath, ribbon_name)
            # save ribbon to file
            # log: Saving file: {0}
            WLOG(params, '', textentry('40-000-00013', args=[ribbon_path]))
            np.save(ribbon_path, ribbon)
            # delete ribbon
            del ribbon
        # delete image from memory
        del image
    # ----------------------------------------------------------------------
    # storage for output image
    out_image = np.zeros((mdim1, mdim2))
    # loop through the files of the same ribbon
    for b_it in range(len(bins) - 1):
        # log message so we know how far through we are
        # Combining ribbon {0} / {1}
        wargs = [b_it + 1, len(bins)]
        WLOG(params, '', textentry('40-000-00014', args=wargs))
        # store box
        box = []
        # ------------------------------------------------------------------
        # loop around each ribbon and add to the box
        for f_it, filename in enumerate(files):
            # construct ribbon nmae
            clean_filename = filename.replace('.', '_')
            ribbon_name = '{0}_ribbon{1:06d}.npy'.format(clean_filename, b_it)
            ribbon_path = os.path.join(subfilepath, ribbon_name)
            # load ribbon
            # log: Loading file: {0}
            WLOG(params, '', textentry('40-000-00015', args=[ribbon_path]))
            ribbon = np.load(ribbon_path)
            # delete this ribbon from disk
            # log: Removing file: {0}
            WLOG(params, '', textentry('40-000-00016', args=[ribbon_path]))
            os.remove(ribbon_path)
            # append to box
            box.append(np.array(ribbon))
            # delete ribbon
            del ribbon
        # ------------------------------------------------------------------
        # convert box to a numpy array
        box = np.array(box)
        # fill the full image
        out_image[bins[b_it]: bins[b_it + 1]] = cfunc(box, axis=0)
        # delete the box
        del box
    # ----------------------------------------------------------------------
    # delete the sub directory
    if os.path.exists(subfilepath):
        os.removedirs(subfilepath)
    # ----------------------------------------------------------------------
    # return the out image
    return out_image


def expand_badpixelmap(params: ParamDict, bad_pixel_map1: np.ndarray
                       ) -> np.ndarray:
    """
    Expand large bad pixel areas to make sure the edges are counted as
    bad pixels

    Erode size (BAD_PIX_ERODE_SIZE) defines areas that are large/small
    Dilate size (BAD_PIX_DILATE_SIZE) determines how much larger to make them

    :param params: ParamDict
    :param bad_pixel_map1: np.ndarray, input bad pixel map (1=bad, 0=good)

    :return: np.ndarray, updated bad pixel map (1=bad, 0=good)
    """
    # get erode and dilate size
    erode_size = pcheck(params, 'BADPIX_ERODE_SIZE', dtype=float)
    dilate_size = pcheck(params, 'BADPIX_DILATE_SIZE', dtype=float)
    # define circular masks for the erosion and dilation of the bad pixels
    erode_mask = mp.get_circular_mask(erode_size)
    dilate_mask = mp.get_circular_mask(dilate_size)
    # remove small bad pixels (i.e. pixels with one of the dimensions of
    #    size = 1)
    bad_pixel_map2 = binary_erosion(bad_pixel_map1, structure=erode_mask)
    # expand large bad pixel regions
    bad_pixel_map2 = binary_dilation(bad_pixel_map2, structure=dilate_mask)
    # bad pixels are a combination of original map and the expanded region
    bad_pixel_map3 = bad_pixel_map1 | bad_pixel_map2
    # return
    return bad_pixel_map3


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
