#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 14:28

@author: cook
"""

from __future__ import division
import numpy as np
from scipy import signal
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe.core import math
from terrapipe.core.core import drs_log
from terrapipe import locale


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_path.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def rotate_image(image, rotation):
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


def resize(params, image, x=None, y=None, xlow=0, xhigh=None,
           ylow=0, yhigh=None):
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
            eargs = ['xlow', 'xhigh', xlow, func_name]
            WLOG(params, 'error', TextEntry('00-001-00023', args=eargs))
        else:
            x = np.arange(xlow, xhigh)
        # deal with ylow > yhigh
        if ylow > yhigh:
            y = np.arange(yhigh + 1, ylow + 1)[::-1]
        elif ylow == yhigh:
            eargs = ['ylow', 'yhigh', xlow, func_name]
            WLOG(params, 'error', TextEntry('00-001-00023', args=eargs))
        else:
            y = np.arange(ylow, yhigh)
    # construct the new image (if one can't raise error)
    try:
        newimage = np.take(np.take(image, x, axis=1), y, axis=0)
    except Exception as e:
        eargs = [xlow, xhigh, ylow, yhigh, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-001-00024', args=eargs))
        newimage = None
    # return error if we removed all pixels
    if newimage.shape[0] == 0 or newimage.shape[1] == 0:
        eargs = [xlow, xhigh, ylow, yhigh, func_name]
        WLOG(params, 'error', TextEntry('00-001-00025', args=eargs))
        newimage = None

    # return new image
    return newimage


def flip_image(params, image, fliprows=True, flipcols=True):
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
        eargs = [image.shape, func_name]
        WLOG(params, 'error', TextEntry('09-002-00001', args=eargs))
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



def convert_to_e(params, image, **kwargs):
    """
    Converts image from ADU/s into e-

    :param image: numpy array (2D), the image
    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least: (if exptime is None)
                exptime: float, the exposure time of the image
                gain: float, the gain of the image

    :keyword gain: float, if p is None, used as the gain to multiple the
                   image by
    :keyword exptime: float, if p is None, used as the exposure time the image
                    is multiplied by

    :return newimage: numpy array (2D), the image in e-
    """
    func_name = __NAME__ + '.convert_to_e()'
    # get constants from params / kwargs
    gain = pcheck(params, 'GAIN', 'gain', kwargs, func=func_name)
    exptime = pcheck(params, 'EXPTIME', 'exptime', kwargs, func=func_name)
    # correct image
    newimage = image * gain * exptime
    # return corrected image
    return newimage


def convert_to_adu(params, image, **kwargs):
    """
    Converts image from ADU/s into ADU

    :param image:

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least: (if exptime is None)
            exptime: float, the exposure time of the image

    :keyword exptime: float, if p is None, used as the exposure time the image
                    is multiplied by

    :return newimage: numpy array (2D), the image in e-
    """
    func_name = __NAME__ + '.convert_to_adu()'
    # get constants from params / kwargs
    exptime = pcheck(params, 'EXPTIME', 'exptime', kwargs, func=func_name)
    # correct image
    newimage = image * exptime
    # return corrected image
    return newimage


def clean_hotpix(image, badpix):
    # Cleans an image by finding pixels that are high-sigma (positive or negative)
    # outliers compared to their immediate neighbours. Bad pixels are
    # interpolated with a 2D surface fit by using valid pixels within the
    # 3x3 pixel box centered on the bad pix.
    #
    # Pixels in big clusters of bad pix (more than 3 bad neighbours)
    # are left as is
    image_rms_measurement = np.array(image)
    # First we construct a 'flattened' image
    # We perform a low-pass filter along the x axis
    # filtering the image so that only pixel-to-pixel structures
    # remain. This is use to find big outliers in RMS.
    # First we apply a median filtering, which removes big outliers
    # and then we smooth the image to avoid big regions filled with zeros.
    # Regions filled with zeros in the low-pass image happen when the local
    # median is equal to the pixel value in the input image.
    #
    # We apply a 5-pix median boxcar in X and a 5-pix boxcar smoothing
    # in x. This blurs along the dispersion over a scale of ~7 pixels.
    box = np.ones([1, 5])
    box /= np.nansum(box)
    low_pass = signal.medfilt(image_rms_measurement, [1, 5])
    low_pass = signal.convolve2d(low_pass, box, mode='same')
    # residual image showing pixel-to-pixel noise
    # the image is now centered on zero, so we can
    # determine the RMS around a given pixel
    image_rms_measurement -= low_pass
    # smooth the abs(image) with a 3x3 kernel
    rms = signal.medfilt(np.abs(image_rms_measurement), [3, 3])
    # the RMS cannot be arbitrarily small, so  we set
    # a lower limit to the local RMS at 0.5x the median
    # rms
    with warnings.catch_warnings(record=True) as _:
        rms[rms < (0.5 * np.nanmedian(rms))] = 0.5 * np.nanmedian(rms)
        # determining a proxy of N sigma
        nsig = image_rms_measurement / rms
        bad = np.array((np.abs(nsig) > 10), dtype=bool)
    # known bad pixels are also considered bad even if they are
    # within the +-N sigma rejection
    badpix = badpix | bad | ~np.isfinite(image)
    # find the pixel locations where we have bad pixels
    x, y = np.where(badpix)
    # centering on zero
    yy, xx = np.indices([3, 3]) - 1
    # copy the original iamge
    image1 = np.array(image)
    # correcting bad pixels with a 2D fit to valid neighbours
    for i in range(len(x)):
        keep = ~badpix[x[i] - 1:x[i] + 2, y[i] - 1:y[i] + 2]
        if np.nansum(keep) < 6:
            continue
        box = image[x[i] - 1:x[i] + 2, y[i] - 1:y[i] + 2]
        # fitting a 2D 2nd order polynomial surface. As the xx=0, yy=0
        # corresponds to the bad pixel, then the first coefficient
        # of the fit (its zero point) corresponds to the value that
        # must be given to the pixel
        coeff = math.fit2dpoly(xx[keep], yy[keep], box[keep])
        image1[x[i], y[i]] = coeff[0]
    # return the cleaned image
    return image1




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
