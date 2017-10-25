#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spirouFITS.py

read and writing functions

Created on 2017-10-12 at 15:32

@author: cook



Version 0.0.0
"""
import numpy as np
from astropy.io import fits
import os
import sys
import warnings
from collections import OrderedDict

from startup import log


# =============================================================================
# Define variables
# =============================================================================
WLOG = log.logger
# -----------------------------------------------------------------------------
FORBIDDEN_COPY_KEY = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                      'EXTEND', 'COMMENT', 'CRVAL1', 'CRPIX1', 'CDELT1',
                      'CRVAL2', 'CRPIX2', 'CDELT2', 'BSCALE', 'BZERO',
                      'PHOT_IM', 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB']


# =============================================================================
# Define user functions
# =============================================================================
def readimage(p, framemath='+'):
    """
    Reads the image 'fitsfilename' defined in p and adds files defined in
    'arg_file_names' if add is True

    :param p: dictionary, parameter dictionary
    :param framemath: string, controls how files should be added

                currently supported are:
                'add' or '+'           - adds the frames
                'sub' or '-'           - subtracts the frames
                'average' or 'mean'    - averages the frames
                'multiply' or '*'      - multiplies the frames
                'divide' or '/'        - divides the frames
                'none'                 - does not add

    :return image: numpy array (2D), the image
    :return header: dictionary, the header file of the image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]
    """
    # set up frequently used variables
    fitsfilename = p['fitsfilename']
    log_opt = p['log_opt']
    # log that we are reading the image
    WLOG('', log_opt, 'Reading Image ' + fitsfilename)
    # read image from fits file
    image, imageheader, nx, ny = read_raw_data(fitsfilename)
    # log that we have loaded the image
    WLOG('', log_opt, 'Image {0} x {1} loaded'.format(nx, ny))
    # if we have more than one frame and add is True then add the rest of the
    #    frames
    image = math_controller(p, image, framemath)
    # convert header to python dictionary
    header = dict(zip(imageheader.keys(), imageheader.values()))
    comments = dict(zip(imageheader.keys(), imageheader.comments))
    # # add some keys to the header-
    header['@@@hname'] = p['arg_file_names'][0] + ' Header File'
    header['@@@fname'] = fitsfilename

    # return data, header, data.shape[0], data.shape[1]
    return image, header, comments, nx, ny


def keylookup(p, d=None, key=None, name=None, has_default=False, default=None):
    """
    Looks for a key in dictionary p, named 'name'
    if has_default sets value of key to 'default' if not found
    else logs an error

    :param p: dictionary, any dictionary
    :param d: dictionary, any dictionary, if None uses parameter dictionary
    :param key: string, key in the dictionary to find
    :param name: string, the name of the dictionary (for log)
    :param has_default: bool, if True uses "default" as the value if key
                        not found
    :param default: object, value of the key if not found and
                    has_default is True

    :return value: object, value of p[key] or default (if has_default=True)
    """
    # deal with d = None
    if d is None:
        d = p
    # deal with no name
    if name is None and d is None:
        name = 'Parameter Dictionary'
    elif name is None:
        name = 'Unknown Dictionary'
    # deal with no key
    if key is None:
        WLOG('error', p['log_opt'], 'Must define key')
        raise ValueError('Must define key')
    # if we have default value use get else try standard call or log if error
    if has_default:
        value = d.get(key, default)
    else:
        try:
            value = d[key]
        except KeyError:
            emsg = 'Key "{0}" not found in "{1}"'.format(key, name)
            WLOG('error', p['log_opt'], emsg)

    return value


def keyslookup(p, d=None, keys=None, name=None, has_default=False,
               defaults=None):
    """
    Looks for keys in dictionary p, named 'name'
    if has_default sets value of key to 'default' if not found
    else logs an error

    :param p: dictionary, any dictionary
    :param d: dictionary, any dictionary, if None uses parameter dictionary
    :param keys: list of strings, keys in the dictionary to find
    :param name: string, the name of the dictionary (for log)
    :param has_default: bool, if True uses "default" as the value if key
                        not found
    :param default: list of objects or None, values of the keys if not
                    found and has_default is True

    :return values: list of objects, values of p[key] for key in keys
                    or default value for each key (if has_default=True)
    """

    # make sure keys is a list
    try:
        keys = list(keys)
    except TypeError:
        raise ValueError('"keys" must be a list')
    # if defaults is None --> list of Nones else make sure defaults is a list
    if defaults is None:
        defaults = list(np.repeat([None], len(keys)))
    else:
        try:
            defaults = list(defaults)
            if len(defaults) != len(keys):
                raise ValueError('"defaults" must be same length as "keys"')
        except TypeError:
            raise ValueError('"defaults" must be a list')

    # loop around keys and look up each key
    values = []
    for k_it, key in enumerate(keys):
        # get the value for key
        v = keylookup(p, d, key, name, has_default, default=defaults[k_it])
        # append value to values list
        values.append(v)
    # return values
    return values


def writeimage(filename, image, hdict):
    """
    Writes an image and its header to file

    :param filename: string, filename to save the fits file to
    :param image: numpy array (2D), the image
    :param hdict: dictionary, header dictionary to write to fits file

                Must be in form:

                        hdict[key] = (value, comment)
                or
                        hdict[key] = value     (comment will be equal to
                                                "UNKNOWN"
    :return:
    """

    # check if file exists and remove it if it does
    if os.path.exists(filename):
        os.remove(filename)
    # create the primary hdu
    hdu = fits.PrimaryHDU(image)
    # add header keys to the hdu header
    for key in list(hdict.keys()):
        hdu.header[key] = hdict[key]
    # write to file
    with warnings.catch_warnings(record=True) as w:
        hdu.writeto(filename)
    log.warninglogger(w)


def copy_original_keys(header, comments, hdict=None, forbid_keys=True):
    """
    Copies keys from hdr dictionary to hdict, if forbid_keys is True some
    keys will not be copies (defined in python code)

    :param header: header dictionary from readimage (ReadImage) function

    :param comments: comment dictionary from readimage (ReadImage) function

    :param hdict: dictionary or None, header dictionary to write to fits file
                  if None hdict is created

                Must be in form:

                        hdict[key] = (value, comment)
                or
                        hdict[key] = value     (comment will be equal to
                                                "UNKNOWN"

    :return:
    """
    if hdict is None:
        hdict = OrderedDict()

    for key in list(header.keys()):
        # skip if key is forbidden keys
        if forbid_keys and (key in FORBIDDEN_COPY_KEY):
            continue
        # skip if key added temporarily in code (denoted by @@@)
        elif '@@@' in key:
            continue
        # else add key to hdict
        else:
            # if key in "comments" add it as a tuple else comment_ is blank
            if key in comments:
                hdict[key] = (header[key], comments[key])
            else:
                hdict[key] = (header[key], '')
    # return the hdict ready to write to fits file
    return hdict


# =============================================================================
# Define pyfits functions
# =============================================================================
def read_raw_data(filename, getheader=True, getshape=True):
    """
    Reads the raw data and possibly header using astropy.io.fits

    :param filename: string, the filename to open with astropy.io.fits
    :param getheader: bool, if True loads the filename header
    :param getshape: bool, if True returns the shape

    if getheader = getshape = True
    :return data: numpy array (2D), the image
    :return header: dictionary, the header file of the image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]

    if getheader = False, getshape = True
    :return data: numpy array (2D), the image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]

    if getheader = False, getshape = False
    :return data: numpy array (2D), the image
    :return header: dictionary, the header file of the image

    if getheader = getshape = False
     :return data: numpy array (2D), the image
    """
    # get the data
    data = fits.getdata(filename)
    # get the header if "getheader" and "getshape" are True
    if getheader:
        header = fits.getheader(filename)
    else:
        header = dict()
    # return based on whether header and shape
    if getheader and getshape:
        return data, header, data.shape[0], data.shape[1]
    elif getheader:
        return data, header
    elif getshape:
        return data, data.shape[0], data.shape[1]
    else:
        return data


def math_controller(p, data, framemath=None):
    """
    uses the framemath key to decide how 'arg_file_names' files are added to
    data (fitfilename)

    :param p: dictionary, parameter dictionary
    :param data: numpy array (2D), the image
    :param framemath: string, or None controls how files should be added

                currently supported are:
                'add' or '+'           - adds the frames
                'sub' or '-'           - subtracts the frames
                'average' or 'mean'    - averages the frames
                'multiply' or '*'      - multiplies the frames
                'divide' or '/'        - divides the frames
                'none' or None         - does not do any math

    :return data: numpy array (2D), the image
    """
    if framemath is None:
        return data

    # set up frequently used variables
    log_opt = p['log_opt']
    nbframes = p['nbframes']
    acceptable_math = ['ADD', '+', 'SUB', '-', 'AVERAGE', 'MEAN',
                       'MULTIPLY', '*', 'DIVIDE', '/', 'NONE']

    # convert add to upper case
    fm = framemath.upper()
    # check that frame math is acceptable

    if fm not in acceptable_math:
        eargs = [fm, '", "'.join(acceptable_math)]
        raise ValueError('framemath="{0}" has to be one of the following:\n\t\t'
                         '"{1}"'.format(*eargs))
    # if we have no math don't continue
    if fm == 'NONE':
        return data
    # if we have only one frame don't continue
    if nbframes < 2:
        return data
    # select text for logging
    if fm in ['ADD', '+']:
        kind = 'Adding'
    elif fm in ['MEAN', 'AVERAGE']:
        kind = 'Averaging'
    elif fm in ['SUB', '-']:
        kind = 'Subtracting'
    elif fm in ['MULTIPLY', '*']:
        kind = 'Multiplying'
    elif fm in ['DIVIDE', '/']:
        kind = 'Dividing'
    else:
        kind = 'no'
    # log that we are adding frames
    WLOG('info', log_opt, '{0} frames'.format(kind))
    # loop around each frame
    for f_it in range(1, nbframes):
        # construct frame file name
        framefilename = os.path.join(p['DRS_DATA_RAW'],
                                     p['arg_night_name'],
                                     p['arg_file_names'][f_it])
        # check whether frame file name exists, log and exit if not
        if not os.path.exists(framefilename):
            WLOG('error', log_opt, ('File: {0} does not exist'
                                    ''.format(framefilename)))
        else:
            # load that we are reading this file
            WLOG('', log_opt, 'Reading File: ' + framefilename)
            # finally add/subtract/multiple/divide data
            if fm in ['ADD', '+', 'MEAN', 'AVERAGE']:
                data += read_raw_data(framefilename, False, False)
            elif fm in ['SUB', '-']:
                data -= read_raw_data(framefilename, False, False)
            elif fm in ['MULTIPLY', '*']:
                data *= read_raw_data(framefilename, False, False)
            elif fm in ['DIVIDE', '/']:
                data /= read_raw_data(framefilename, False, False)
            else:
                continue
    # if we need to average data then divide by nbframes
    if fm in ['MEAN', 'AVERAGE']:
        data /= nbframes
    # return data
    return data


# =============================================================================
# End of code
# =============================================================================
