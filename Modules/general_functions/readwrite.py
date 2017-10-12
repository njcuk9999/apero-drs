#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readwrite.py

read and writing functions

Created on 2017-10-12 at 15:32

@author: cook



Version 0.0.0
"""
import numpy as np
from astropy.io import fits
import os
import sys

from startup import log


# =============================================================================
# Define variables
# =============================================================================
WLOG = log.logger
# -----------------------------------------------------------------------------

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

    :return data: numpy array (2D), the image
    :return header: dictionary, the header file of the image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]
    """
    # set up frequently used variables
    fitsfilename = p['fitsfilename']
    log_opt = p['log_opt']
    # log that we are reading the image
    WLOG('', log_opt, 'Reading Image ' + fitsfilename)
    # read data from fits file
    data, header, nx, ny = read_raw_data(fitsfilename)
    # log that we have loaded the image
    WLOG('', log_opt, 'Image {0} x {1} loaded'.format(nx, ny))
    # if we have more than one frame and add is True then add the rest of the
    #    frames
    data = math_controler(p, data, framemath)
    # convert header to python dictionary
    header = dict(zip(header.keys(), header.values()))
    # # add some keys to the header
    header['@@@hname'] = p['arg_file_names'][0] + ' Header File'
    header['@@@fname'] = fitsfilename

    # return data, header, data.shape[0], data.shape[1]
    return data, header, nx, ny


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
            sys.exit(1)

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


def math_controler(p, data, framemath='+'):
    """
    uses the framemath key to decide how 'arg_file_names' files are added to
    data (fitfilename)

    :param p: dictionary, parameter dictionary
    :param data: numpy array (2D), the image
    :param framemath: string, controls how files should be added

                currently supported are:
                'add' or '+'           - adds the frames
                'sub' or '-'           - subtracts the frames
                'average' or 'mean'    - averages the frames
                'multiply' or '*'      - multiplies the frames
                'divide' or '/'        - divides the frames
                'none'                 - does not add

    :return data: numpy array (2D), the image
    """
    # set up frequently used variables
    log_opt = p['log_opt']
    nbframes = len(p['arg_file_names'])
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
    if fm in ['Adding', '+']:
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
            sys.exit(1)
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
