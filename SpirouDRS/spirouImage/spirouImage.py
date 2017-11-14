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
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from . import spirouFITS

# =============================================================================
# Define variables
# =============================================================================
# Get Logging function
WLOG = spirouCore.wlog
# Name of program
__NAME__ = 'spirouImage.py'
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
    :param gain: float, if p is None, used as the gain to multiple the image by
    :param exptime: float, if p is None, used as the exposure time the image
                    is multiplied by

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

def convert_to_adu(image, p=None, exptime=None):
    """
    Converts image from ADU/s into ADU

    :param image:
    :param p: dictionary or None, parameter dictionary, must contain 'exptime'
              and 'gain', if None gain and exptime must not be None
    :param exptime: float, if p is None, used as the exposure time the image
                    is multiplied by

    :return newimage: numpy array (2D), the image in e-
    """
    newimage = None
    if p is not None:
        try:
            newimage = image * p['exptime']
        except KeyError:
            emsg = ('If parameter dictionary is defined keys "exptime" '
                    'must be defined.')
            WLOG('error', '', emsg)
    elif exptime is not None:
        try:
            exptime = float(exptime)
            newimage = image * exptime
        except ValueError:
            emsg = ('"exptime" must be a float if parameter '
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
        masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
        emsg = 'No valid DARK in calibDB {0} ( with unix time <={1})'
        WLOG('error', p['log_opt'], emsg.format(masterfile, acqtime))
        corrected_image = image

    # finally return datac
    return corrected_image


def get_tilt(pp, lloc, image):
    """
    Get the tilt by correlating the extracted fibers

    :param pp: dictionary, parameter dictionary
    :param lloc: dictionary, parameter dictionary containing the data
    :param image: numpy array (2D), the image

    :return lloc: dictionary, parameter dictionary containing the data
    """
    nbo = lloc['number_orders']
    # storage for "nbcos"
    # Question: what is nbcos?
    lloc['nbcos'] = np.zeros(nbo, dtype=int)
    lloc.set_source('nbcos', __NAME__ + '/get_tilt()')
    # storage for tilt
    lloc['tilt'] = np.zeros(int(nbo/2), dtype=float)
    lloc.set_source('tilt', __NAME__ + '/get_tilt()')
    # loop around each order
    for order_num in range(0, nbo, 2):
        # extract this AB order
        lloc = spirouEXTOR.ExtractABorder(pp, lloc, image, order_num)
        # --------------------------------------------------------------------
        # Over sample the data and interpolate new extraction values
        pixels = np.arange(image.shape[1])
        os_pixels = np.arange(image.shape[1] * pp['COI']) / pp['COI']
        cent1i = np.interp(os_pixels, pixels, lloc['cent1'])
        cent2i = np.interp(os_pixels, pixels, lloc['cent2'])
        # --------------------------------------------------------------------
        # get the correlations between cent2i and cent1i
        cori = np.correlate(cent2i, cent1i, mode='same')
        # --------------------------------------------------------------------
        # get the tilt - the maximum correlation between the middle pixel
        #   and the middle pixel + 50 * p['COI']
        coi = int(pp['COI'])
        pos = int(image.shape[1] * coi / 2)
        delta = np.argmax(cori[pos:pos + 50 * coi]) / coi
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

    :param pp: dictionary, parameter dictionary
    :param lloc: dictionary, parameter dictionary containing the data
    :return lloc: dictionary, parameter dictionary containing the data
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



# =============================================================================
# Get basic image properties
# =============================================================================
def get_exptime(p, hdr, name=None):
    # return param
    return get_param(p, hdr, 'kw_exptime', name)


def get_gain(p, hdr, name=None):
    # return param
    return get_param(p, hdr, 'kw_gain', name)


def get_sigdet(p, hdr, name=None):
    # return param
    return get_param(p, hdr, 'kw_rdnoise', name)


def get_param(p, hdr, keyword, name=None):
    # get header keyword
    key = p[keyword][0]
    # deal with no name
    if name is None:
        name = key
    # get value
    p[name] = float(spirouFITS.keylookup(p, hdr, key, hdr['@@@hname']))
    # set source
    p.set_source(name, hdr['@@@hname'])
    # return p
    return p


# =============================================================================
# End of code
# =============================================================================
