#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 17:47

@author: cook



Version 0.0.0
"""

import numpy as np
import sys
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouCore
from . import spirouFITS

# =============================================================================
# Define variables
# =============================================================================
WLOG = spirouCore.wlog
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
            emsg = '"xlow" and "xhigh" cannot have the same values'
            WLOG('error', '', emsg)
        else:
            x = np.arange(xlow, xhigh)
        # deal with ylow > yhigh
        if ylow > yhigh:
            y = np.arange(yhigh + 1, ylow + 1)[::-1]
        elif ylow == yhigh:
            emsg = '"ylow" and "yhigh" cannot have the same values'
            WLOG('error', '', emsg)
        else:
            y = np.arange(ylow, yhigh)
    # construct the new image
    newimage = np.take(np.take(image, x, axis=1), y, axis=0)
    # if getshape is True return newimage, newimage.shape[0], newimage.shape[1]
    if getshape:
        return newimage, newimage.shape[0], newimage.shape[1]
    else:
        # return new image
        return newimage


def flip_image(image, flipx=True, flipy=True):
    """
    Flips the image in the x and/or the y direction

    :param image: numpy array (2D), the image
    :param flipx: bool, if True flips in x direction (axis = 0)
    :param flipy: bool, if True flips in y direction (axis = 1)

    :return newimage: numpy array (2D), the flipped image
    """
    if flipx and flipy:
        return image[::-1, ::-1]
    elif flipx:
        return image[::-1, :]
    elif flipy:
        return image[:, ::-1]
    else:
        return image




def convert_to_e(image, p=None, gain=None, exptime=None):
    """
    Converts image from ADU/s into e-

    :param image:
    :param p: dictionary or None, parameter dictionary, must contain 'exptime'
              and 'gain', if None gain and exptime must not be None

    :return newimage: numpy array (2D), the image in e-
    """
    newimage = None
    if p is not None:
        try:
            newimage = image * p['exptime'] * p['gain']
        except KeyError:
            emsg = ('If parameter dictionary is defined keys "exptime" '
                    'and "gain" must be defined.')
            WLOG('error', '', emsg)
    elif gain is not None and exptime is not None:
        try:
            gain, exptime = float(gain), float(exptime)
            newimage = image * gain * exptime
        except ValueError:
            emsg = ('"gain" and "exptime" must be floats if parameter '
                    'dictionary is None.')
            WLOG('error', '', emsg)

    return newimage


# =============================================================================
# Define Image correction functions
# =============================================================================
def correct_for_dark(p, image, header):
    """
    Corrects "data" for "dark" using calibDB file (header must contain
        value of p['ACQTIME_KEY'] as a keyword

    :param p: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage

    :return corrected_image: numpy array (2D), the dark corrected image
    """

    # get acquisition time
    acqtime = spirouCDB.GetAcqTime(p, header)

    # get calibDB
    cdb = spirouCDB.GetDatabase(p, acqtime)

    # try to read 'DARK' from cdb
    if 'DARK' in cdb:
        darkfile = os.path.join(p['DRS_CALIB_DB'], cdb['DARK'][1])
        WLOG('', p['log_opt'], 'Doing Dark Correction using ' + darkfile)
        darkimage, nx, ny = spirouFITS.read_raw_data(darkfile, False, True)
        corrected_image = image - (darkimage * p['nbframes'])
    else:
        masterfile = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
        emsg = 'No valid DARK in calibDB {0} ( with unix time <={1})'
        WLOG('error', p['log_opt'], emsg.format(masterfile, acqtime))

    # finally return datac
    return corrected_image






# =============================================================================
# End of code
# =============================================================================
