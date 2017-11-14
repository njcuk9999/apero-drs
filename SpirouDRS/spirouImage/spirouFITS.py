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

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouCDB

# =============================================================================
# Define variables
# =============================================================================
WLOG = spirouCore.wlog
__NAME__ = 'spirouFITS.py'
# -----------------------------------------------------------------------------
FORBIDDEN_COPY_KEY = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                      'EXTEND', 'COMMENT', 'CRVAL1', 'CRPIX1', 'CDELT1',
                      'CRVAL2', 'CRPIX2', 'CDELT2', 'BSCALE', 'BZERO',
                      'PHOT_IM', 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB']


# =============================================================================
# Define Read/Write User
# =============================================================================
def readimage(p, framemath='+', filename=None, log=True):
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
    :param filename: string or None, filename of the image to read, if None
                     then p['fitsfilename'] is used
    :param log: bool, if True logs opening and size

    :return image: numpy array (2D), the image
    :return header: dictionary, the header file of the image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]
    """
    # set up frequently used variables
    log_opt = p['log_opt']
    # get file name
    if filename is None:
        try:
            fitsfilename = p['fitsfilename']
        except KeyError:
            emsg = '"fitsfilename" is not defined in parameter dictionary'
            WLOG('error', log_opt, emsg)
            fitsfilename = ''
    else:
        fitsfilename = filename
    # log that we are reading the image
    if log:
        WLOG('', log_opt, 'Reading Image ' + fitsfilename)
    # read image from fits file
    image, imageheader, nx, ny = read_raw_data(fitsfilename)
    # log that we have loaded the image
    if log:
        WLOG('', log_opt, 'Image {0} x {1} loaded'.format(nx, ny))
    # if we have more than one frame and add is True then add the rest of the
    #    frames, currently we overwrite p['fitsfilename'] and header with
    #    last entry
    # TODO: Do we want to overwrite header/fitsfilename with last entry?
    if framemath is not None or framemath is not 'none':
        p, image, imageheader = math_controller(p, image, imageheader,
                                                framemath)
    # convert header to python dictionary
    header = dict(zip(imageheader.keys(), imageheader.values()))
    comments = dict(zip(imageheader.keys(), imageheader.comments))
    # # add some keys to the header-
    if filename is None:
        header['@@@hname'] = p['arg_file_names'][0] + ' Header File'
        header['@@@fname'] = p['fitsfilename']

    # return data, header, data.shape[0], data.shape[1]
    return image, header, comments, nx, ny


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
    spirouCore.spirouLog.warninglogger(w)


def read_tilt_file(p, hdr=None, filename=None):
    """
    Reads the tilt file (from calib database or filename) and using the
    'kw_TILT' keyword-store extracts the tilts for each order

    :param p: dictionary, parameter dictionary

    :param hdr: dictionary or None, the header dictionary to look for the
                     acquisition time in, if None loads the header from
                     p['fitsfilename']

    :param filename: string or None, the filename and path of the tilt file,
                     if None gets the TILT file from the calib database
                     keyword "TILT"

    :return tilt: list of the tilt for each order
    """
    # get filename
    read_file = spirouCDB.GetFile(p, 'TILT', hdr)
    # read read_file
    rout = readimage(p, framemath='none', filename=read_file, log=False)
    image, hdict, _, nx, ny = rout
    # get the tilt keys
    tilt = read_key_2d_list(p, hdict, p['kw_TILT'][0], p['IC_TILT_NBO'], 1)
    # return the first set of keys
    return tilt[:, 0]


def read_order_profile_superposition(p, hdr=None, filename=None):
    # Log that we are reading the order profile
    wmsg = 'Reading order profile of Fiber {0}'
    WLOG('', p['log_opt'] + p['fiber'], wmsg.format(p['fiber']))
    # construct key
    key = 'ORDER_PROFILE_{0}'.format(p['fiber'])
    # construct filename
    read_file = spirouCDB.GetFile(p, key, hdr)
    # read read_file
    rout = readimage(p, framemath='none', filename=read_file, log=False)
    # return order profile (via readimage = image, hdict, commments, nx, ny
    return rout


# =============================================================================
# Define header User functions
# =============================================================================
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


def add_new_key(hdict, keywordstore, value=None):
    """
    Add a new key to hdict from keywordstore, if value is not None then the
    keywordstore value is updated. Each keywordstore is in form:
            [key, value, comment]    where key and comment are strings

    :param hdict: dictionary, storage for adding to FITS rec
    :param keywordstore: list, keyword list (defined in spirouKeywords.py)
                         must be in form [string, value, string]
    :param value: object or None, if any python object (other than None) will
                  replace the value in keywordstore (i.e. keywordstore[1]) with
                  value, if None uses the value = keywordstore[1]

    :return hdict: dictionary, storage for adding to FITS rec
    """
    # extract keyword, value and comment and put it into hdict
    key, dvalue, comment = keywordstore
    # set the value to default value if value is None
    if value is None:
        value = dvalue
    # add to the hdict dictionary in form (value, comment)
    hdict[key] = (value, comment)
    # return hdict
    return hdict


def add_new_keys(hdict, keywordstores, values=None):
    """
    Add a set of new key to hdict from keywordstores, if values is not None,
    then all values are set to None, keywordstores is a list of keywordstore
    objects. Each keywordstore is in form:
            [key, value, comment]    where key and comment are strings

    :param hdict: dictionary, storage for adding to FITS rec
    :param keywordstores: list of lists, list of "keyword list" lists
                          (defined in spirouKeywords.py)
                          each "keyword list" must be in form:
                          [string, value, string]
    :param values: list of objects or None, if any python object
                   (other than None) will replace the values in keywordstores
                   (i.e. keywordstore[1]) with value[i], if None uses the
                   value = keywordstore[1] for each keywordstores

    :return hdict: dictionary, storage for adding to FITS rec
    """
    # deal with no values
    if values is None:
        values = np.repeat([None], len(keywordstores))
    # loop around keywordstores and pipe to add_new_key for each iteration
    for k_it, keywordstore in enumerate(keywordstores):
        hdict = add_new_key(hdict, keywordstore, values[k_it])
    # return hdict
    return hdict


def add_key_2d_list(hdict, keywordstore, values=None):
    """
    Add a new 2d list to key using the keywordstorage[0] as prefix in form
    keyword = kewordstoreage + number

    where number = (row number * number of columns) + column number

    :param hdict: dictionary, storage for adding to FITS rec
    :param keywordstore: list, keyword list (defined in spirouKeywords.py)
                         must be in form [string, value, string]
    :param value: numpy array or 2D list of keys or None

                  if numpy array or 2D list will create a set of keys in form
                  keyword = kewordstoreage + number
                  where number = (row number * number of columns) + column number
                  with value = values[row number][column number]

                  if None uses the value = keywordstore[1]

    :return hdict: dictionary, storage for adding to FITS rec
    """
    # extract keyword, value and comment and put it into hdict
    key, dvalue, comment = keywordstore
    # set the value to default value if value is None
    if values is None:
        values = [[dvalue]]
    # convert to a numpy array
    values = np.array(values)
    # loop around the 2D array
    dim1, dim2 = values.shape
    for i_it in range(dim1):
        for j_it in range(dim2):
            # construct the key name
            keyname = '{0}{1}'.format(key, i_it * dim2 + j_it)
            # get the value
            value = values[i_it, j_it]
            # construct the comment name
            comm = '{0} order={1} coeff={2}'.format(comment, i_it, j_it)
            # add to header dictionary
            hdict[keyname] = (value, comm)
    # return the header dictionary
    return hdict


def read_header(p, filepath, ext=0):
    """
    Read the header from a file at "filepath" with extention "ext" (default=0)

    :param p: dictionary, parameter dictionary
    :param filepath: string, filename and path of FITS file to open
    :param ext: int, extension in FITS rec to open (default = 0)
    :return hdict: dictionary, the dictionary with key value pairs
    """
    # if we don't have header get it (using 'fitsfilename')
    header = dict()
    try:
        header = fits.getheader(filepath)
    except IOError:
        emsg = 'Cannot open header of file {0}'
        WLOG('error', p['log_opt'], emsg.format(filepath))
    # load in to dictionary
    hdict = dict(zip(header.keys(), header.values()))
    # return hdict
    return hdict


def read_key(p, hdict, key):
    return keylookup(p, hdict, key=key)


def read_key_2d_list(p, hdict, key, dim1, dim2):
    # create 2d list
    values = np.zeros((dim1, dim2), dtype=float)
    # loop around the 2D array
    dim1, dim2 = values.shape
    for i_it in range(dim1):
        for j_it in range(dim2):
            # construct the key name
            keyname = '{0}{1}'.format(key, i_it * dim2 + j_it)
            # try to get the values
            try:
                # set the value
                values[i_it][j_it] = float(hdict[keyname])
            except KeyError:
                emsg = 'Cannot find key: {0} nbo={1} nbc={2} in hdict'
                WLOG('error', p['log_opt'], emsg.format(keyname, dim1, dim2))
    # return values
    return values


# =============================================================================
# Define pyfits worker functions
# =============================================================================
def read_raw_data(filename, getheader=True, getshape=True, headerext=0):
    """
    Reads the raw data and possibly header using astropy.io.fits

        If there is one extension it is used
        If there are two extensions the second is used

    :param filename: string, the filename to open with astropy.io.fits
    :param getheader: bool, if True loads the filename header
    :param getshape: bool, if True returns the shape
    :param headerext: int, the extension to read the header from

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
    hdu = fits.open(filename)
    ext = len(hdu)
    # Get the data and header based on how many extensions there are
    if ext == 1:
        data = hdu[0].data
    else:
        data = hdu[1].data

    hdu.close()
    # get the header (if header extension is available else default to zero)
    if headerext <= ext:
        header = hdu[headerext].header
    else:
        header = hdu[0]
    # return based on whether header and shape are required
    if getheader and getshape:
        return data, header, data.shape[0], data.shape[1]
    elif getheader:
        return data, header
    elif getshape:
        return data, data.shape[0], data.shape[1]
    else:
        return data


def math_controller(p, data, header, framemath=None):
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
        return p, data, header
    # if we have only one frame don't continue
    if nbframes < 2:
        return p, data, header
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
        rawdir = spirouConfig.Constants.RAW_DIR(p)
        framefilename = os.path.join(rawdir, p['arg_file_names'][f_it])
        # check whether frame file name exists, log and exit if not
        if not os.path.exists(framefilename):
            WLOG('error', log_opt, ('File: {0} does not exist'
                                    ''.format(framefilename)))
        else:
            # load that we are reading this file
            WLOG('', log_opt, 'Reading File: ' + framefilename)
            # get data and override header
            dtmp, htmp = read_raw_data(framefilename, True, False)
            header = htmp
            # currently we overwrite fitsfilename with last framefilename
            p['fitsfilename'] = framefilename
            p.set_source('fitsfilename', __NAME__)
            # finally add/subtract/multiple/divide data
            if fm in ['ADD', '+', 'MEAN', 'AVERAGE']:
                data += dtmp
            elif fm in ['SUB', '-']:
                data -= dtmp
            elif fm in ['MULTIPLY', '*']:
                data *= dtmp
            elif fm in ['DIVIDE', '/']:
                data /= dtmp
            else:
                continue
    # if we need to average data then divide by nbframes
    if fm in ['MEAN', 'AVERAGE']:
        data /= nbframes

    # return data
    return p, data, header


# =============================================================================
# End of code
# =============================================================================
