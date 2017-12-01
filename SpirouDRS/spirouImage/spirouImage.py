#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 17:47

@author: cook

Import rules: Not spirouLOCOR

Version 0.0.0
"""
from __future__ import division
import numpy as np
import os
import glob

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
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
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


def get_all_similar_files(p):

    # get path
    rawdir = spirouConfig.Constants.RAW_DIR(p)
    # get file prefix and suffix
    prefix = p['arg_file_names'][0][0:5]
    suffix = p['arg_file_names'][0][-8:]
    # constrcut file string
    filestring = '{0}*{1}'.format(prefix, suffix)
    locstring = os.path.join(rawdir, filestring)
    # get all files
    filelist = glob.glob(locstring)
    # remove fitsfilename (reference file)
    filelist.remove(p['fitsfilename'])
    # sort list
    filelist = np.sort(filelist)
    # return file list
    return filelist


# =============================================================================
# Define Image correction functions
# =============================================================================
def measure_dark(pp, image, image_name, short_name):
    """
    Measure the dark pixels in "image"

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param image_name: string, the name of the image (for logging)
    :param short_name: string, suffix (for parameter naming -
                        parmaeters added to pp with suffix i)
    :return pp: dictionary, parameter dictionary
    """

    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = np.median(fimage)
    # get the 5th and 95h percentile qmin
    qmin, qmax = np.percentile(fimage, [pp['DARK_QMIN'], pp['DARK_QMAX']])
    # get the histogram for flattened data
    histo = np.histogram(fimage, bins=pp['HISTO_BINS'],
                         range=(pp['HISTO_RANGE_LOW'], pp['HISTO_RANGE_HIGH']))
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    largs = ['In {0}'.format(image_name), dadead, med, pp['DARK_QMIN'],
             pp['DARK_QMAX'], qmin, qmax]
    WLOG('info', pp['log_opt'], ('{0:12s}: Frac dead pixels= {1:.1f} % - '
                                 'Median= {2:.2f} ADU/s - '
                                 'Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s'
                                 '').format(*largs))
    # add required variables to pp
    source = '{0}/{1}'.format(__NAME__, 'measure_dark()')
    pp['histo_{0}'.format(short_name)] = histo
    pp.set_source('histo_{0}'.format(short_name), source)
    pp['med_{0}'.format(short_name)] = med
    pp.set_source('med_{0}'.format(short_name), source)
    pp['dadead_{0}'.format(short_name)] = dadead
    pp.set_source('dadead_{0}'.format(short_name), source)

    return pp


def correct_for_dark(p, image, header, nfiles=None, return_dark=False):
    """
    Corrects "data" for "dark" using calibDB file (header must contain
        value of p['ACQTIME_KEY'] as a keyword

    :param p: dictionary, parameter dictionary
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

    :return dark: numpy array (2D), the dark
    """
    if nfiles is None:
        nfiles = p['nbframes']

    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = spirouCDB.GetAcqTime(p, header)
        # get calibDB
        cdb, p = spirouCDB.GetDatabase(p, acqtime)
    else:
        cdb = p['calibDB']
        acqtime = p['max_time_unix']

    # try to read 'DARK' from cdb
    if 'DARK' in cdb:
        darkfile = os.path.join(p['DRS_CALIB_DB'], cdb['DARK'][1])
        WLOG('', p['log_opt'], 'Doing Dark Correction using ' + darkfile)
        darkimage, nx, ny = spirouFITS.read_raw_data(darkfile, False, True)
        corrected_image = image - (darkimage * nfiles)
    else:
        masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
        emsg = 'No valid DARK in calibDB {0} ( with unix time <={1})'
        WLOG('error', p['log_opt'], emsg.format(masterfile, acqtime))
        corrected_image, darkimage = None, None

    # finally return datac
    if return_dark:
        return corrected_image, darkimage
    else:
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
        lloc = spirouEXTOR.ExtractABOrderOffset(pp, lloc, image, order_num)
        # --------------------------------------------------------------------
        # Over sample the data and interpolate new extraction values
        pixels = np.arange(image.shape[1])
        os_fac = pp['ic_tilt_coi']
        os_pixels = np.arange(image.shape[1] * os_fac) / os_fac
        cent1i = np.interp(os_pixels, pixels, lloc['cent1'])
        cent2i = np.interp(os_pixels, pixels, lloc['cent2'])
        # --------------------------------------------------------------------
        # get the correlations between cent2i and cent1i
        cori = np.correlate(cent2i, cent1i, mode='same')
        # --------------------------------------------------------------------
        # get the tilt - the maximum correlation between the middle pixel
        #   and the middle pixel + 50 * p['COI']
        coi = int(os_fac)
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
def get_exptime(p, hdr, name=None, return_value=False):
    # return param
    return get_param(p, hdr, 'kw_exptime', name, return_value)


def get_gain(p, hdr, name=None, return_value=False):
    # return param
    return get_param(p, hdr, 'kw_gain', name, return_value)


def get_sigdet(p, hdr, name=None, return_value=False):
    # return param
    return get_param(p, hdr, 'kw_rdnoise', name, return_value)


def get_param(p, hdr, keyword, name=None, return_value=False):
    # get header keyword
    key = p[keyword][0]
    # deal with no name
    if name is None:
        name = key
    # get value
    value = float(spirouFITS.keylookup(p, hdr, key, hdr['@@@hname']))
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

    :param p: dictionary, parameter dictionary
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
