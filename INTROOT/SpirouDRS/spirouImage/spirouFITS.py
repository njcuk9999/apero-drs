#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou FITS rec module

read and writing functions

Created on 2017-10-12 at 15:32

@author: cook

Import rules: Not spirouLOCOR Not from any spirouImage modules
"""
from __future__ import division
import numpy as np
from astropy import version as av
from astropy.io import fits
import string
import os
import warnings
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB

# TODO: This should be changed for astropy -> 2.0.1
# bug that hdu.scale has bug before version 2.0.1
if av.major < 2 or (av.major == 2 and av.minor < 1):
    SCALEARGS = dict(bscale=(1.0 + 1.0e-8), bzero=1.0e-8)
else:
    SCALEARGS = dict(bscale=1, bzero=0)

# =============================================================================
# Define variables
# =============================================================================
# get the logging function
WLOG = spirouCore.wlog
# set the name
__NAME__ = 'spirouFITS.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# get the parameter dictionary object
ParamDict = spirouConfig.ParamDict
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# -----------------------------------------------------------------------------
FORBIDDEN_COPY_KEY = spirouConfig.Constants.FORBIDDEN_COPY_KEYS()
# object name bad characters
BADCHARS = [' '] + list(string.punctuation)


# =============================================================================
# Define Read/Write User
# =============================================================================
def readimage(p, filename=None, log=True, kind=None):
    """
    Reads the image 'fitsfilename' defined in p and adds files defined in
    'arg_file_names' if add is True

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                      file for a recipe
                      i.e. /data/raw/20170710/filename.fits
                log_opt: string, log option, normally the program name
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :param filename: string or None, filename of the image to read, if None
                     then p['FITSFILENAME'] is used
    :param log: bool, if True logs opening and size
    :param kind: string or None, if defined names the image else just image,
                 used in logging (if log = True)

    :return image: numpy array (2D), the image
    :return header: dictionary, the header file of the image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]
    """
    func_name = __NAME__ + '.readimage()'
    # sort out no kind
    if kind is None:
        kind = 'Image'
    else:
        kind += ' Image'
    # set up frequently used variables
    log_opt = p['LOG_OPT']
    # get file name
    if filename is None:
        try:
            fitsfilename = p['FITSFILENAME']
        except KeyError:
            emsg1 = '"fitsfilename" is not defined in parameter dictionary'
            emsg2 = '   function = {0}'.format(func_name)
            WLOG('error', log_opt, [emsg1, emsg2])
            fitsfilename = ''
    else:
        fitsfilename = filename
    # log that we are reading the image
    if log:
        WLOG('', log_opt, 'Reading {0} '.format(kind) + fitsfilename)
    # read image from fits file
    image, imageheader, nx, ny = read_raw_data(fitsfilename)
    # log that we have loaded the image
    if log:
        WLOG('', log_opt, '{0} {1} x {2} loaded'.format(kind, nx, ny))
    # convert header to python dictionary
    header = OrderedDict(zip(imageheader.keys(), imageheader.values()))
    comments = OrderedDict(zip(imageheader.keys(), imageheader.comments))
    # # add some keys to the header-
    if filename is None:
        header['@@@hname'] = p['ARG_FILE_NAMES'][0] + ' Header File'
        header['@@@fname'] = p['FITSFILENAME']
    else:
        header['@@@hname'] = filename + ' Header File'
        header['@@@fname'] = filename
    # return data, header, data.shape[0], data.shape[1]
    return image, header, comments, nx, ny


def readdata(p, filename, log=True, return_header=True, return_shape=True):
    """
    Reads the image 'fitsfilename' defined in p and adds files defined in
    'arg_file_names' if add is True

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param filename: string, filename of the image to read
    :param log: bool, if True logs opening and size
    :param return_header: bool, if True returns header
    :param return_shape: bool, if True returns shape

    :return image: numpy array (2D), the image

    if return_header also returns:
        :return header: dictionary, the header file of the image
        :return comments: dictionary, the header comment file

    if return_shape also returns:
        if len(data.shape)==2
            :return nx: int, the shape in the first dimension,
                        i.e. data.shape[0]
            :return ny: int, the shape in the second dimension,
                        i.e. data.shape[1]
        if len(data.shape)!=2
            :return shape: tuple, data.shape
            :return empty: None, blank entry
    """
    # set up frequently used variables
    log_opt = p['LOG_OPT']
    # log that we are reading the image
    if log:
        WLOG('', log_opt, 'Reading File: {0} '.format(filename))
    # read image from fits file
    rdata = read_raw_data(filename, getheader=return_header,
                          getshape=return_shape)
    # if we are returnning header then add some keys
    if return_header:
        image, imageheader, nx, ny = rdata
        # convert header to python dictionary
        header = OrderedDict(zip(imageheader.keys(), imageheader.values()))
        comments = OrderedDict(zip(imageheader.keys(), imageheader.comments))
        # # add some keys to the header-
        header['@@@hname'] = filename + ' Header File'
        header['@@@fname'] = filename
        if return_shape:
            return image, header, comments, nx, ny
        else:
            return image, header
    else:
        return rdata


def readimage_and_combine(p, framemath='+', filename=None, filenames=None,
                          log=True):
    """
    Reads the image 'fitsfilename' defined in p and adds files defined in
    'arg_file_names' if add is True

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

                optional:
                fitsfilename: string, the full path of for the main raw fits
                      file for a recipe i.e. /data/raw/20170710/filename.fits
                      (if filename is None this is required)

                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                      (if filenames is None this is required)

    :param framemath: string, controls how files should be added

                currently supported are:
                'add' or '+'           - adds the frames
                'sub' or '-'           - subtracts the frames
                'average' or 'mean'    - averages the frames
                'multiply' or '*'      - multiplies the frames
                'divide' or '/'        - divides the frames
                'none'                 - does not add

    :param filename: string or None, filename of the image to read, if None
                     then p['FITSFILENAME'] is used

    :param filenames: list of strings or None, filenames to combine with
                      "filename", if None then p['ARG_FILE_NAMES'] is used

    :param log: bool, if True logs opening and size

    :return image: numpy array (2D), the image
    :return header: dictionary, the header file of the image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]
    """
    func_name = __NAME__ + '.readimage_and_combine()'
    # set up frequently used variables
    log_opt = p['LOG_OPT']
    # -------------------------------------------------------------------------
    # get file name
    if filename is None:
        try:
            filename = p['FITSFILENAME']
        except KeyError:
            emsg1 = ('"filename" is not defined and "fitsfilename" is not '
                     'defined in parameter dictionary')
            emsg2 = '    function={0}'.format(func_name)
            WLOG('error', log_opt, [emsg1, emsg2])
    else:
        p['FITSFILENAME'] = filename
        p.append_source('FITSFILENAME', func_name)
        filename = str(filename)
    # -------------------------------------------------------------------------
    # get additional files
    if filenames is None:
        try:
            filenames = p['ARG_FILE_NAMES'][1:]
        except KeyError:
            emsg1 = ('"filenames" is not defined and "arg_file_names" is not in'
                     ' parameter dictionary')
            emsg2 = '    function={0}'.format(func_name)
            WLOG('error', log_opt, [emsg1, emsg2])
    else:
        p['NBFRAMES'] = len(filenames) + 1
        p.set_source('NBFRAMES', func_name)
        filenames = list(filenames)
    # -------------------------------------------------------------------------
    # log that we are reading the image
    if log:
        WLOG('', log_opt, 'Reading Image ' + filename)
    # read image from fits file
    image, imageheader, nx, ny = read_raw_data(filename)
    # log that we have loaded the image
    if log:
        WLOG('', log_opt, 'Image {0} x {1} loaded'.format(nx, ny))
    # if we have more than one frame and add is True then add the rest of the
    #    frames, currently we overwrite p['fitsfilename'] and header with
    #    last entry
    if framemath is not None or framemath is not 'none':
        p, image, imageheader = math_controller(p, image, imageheader,
                                                filenames, framemath)
    # set fits file name to the first file
    p['FITSFILENAME'] = filename
    p.append_source('FITSFILENAME', __NAME__)

    # convert header to python dictionary
    header = OrderedDict(zip(imageheader.keys(), imageheader.values()))
    comments = OrderedDict(zip(imageheader.keys(), imageheader.comments))
    # # add some keys to the header-
    header['@@@hname'] = filename + ' Header File'
    header['@@@fname'] = p['FITSFILENAME']

    # return data, header, data.shape[0], data.shape[1]
    return p, image, header, comments

def writeimage(p, filename, image, hdict=None, dtype=None):
    """
    Writes an image and its header to file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                output: dict, the output filename as key and the
                        output file headers as the values
    :param filename: string, filename to save the fits file to
    :param image: numpy array (2D), the image
    :param hdict: dictionary or None, header dictionary to write to fits file

                Must be in form:

                        hdict[key] = (value, comment)
                or
                        hdict[key] = value     (comment will be equal to
                                                "UNKNOWN"
                if None does not write header to fits file

    :param dtype: None or hdu format type, forces the image to be in the
                  format type specified (if not None)

                  valid formats are for example: 'int32', 'float64'

    :return None:
    """
    func_name = __NAME__ + '.writeimage()'

    # check if file exists and remove it if it does
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception as e:
            emsg1 = ' File {0} already exists and cannot be overwritten.'
            emsg2 = '    Error {0}: {1}'.format(type(e), e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1.format(filename), emsg2, emsg3])
    # create the primary hdu
    try:
        hdu = fits.PrimaryHDU(image)
    except Exception as e:
        emsg1 = 'Cannot open image with astropy.io.fits'
        emsg2 = '    Error {0}: {1}'.format(type(e), e)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2, emsg3])
        hdu = None
    # force type
    if dtype is not None:
        hdu.scale(type=dtype, **SCALEARGS)
    # add header keys to the hdu header
    if hdict is not None:
        for key in list(hdict.keys()):
            hdu.header[key] = hdict[key]
    # write to file
    with warnings.catch_warnings(record=True) as w:
        try:
            hdu.writeto(filename, overwrite=True)
        except Exception as e:
            emsg1 = 'Cannot write image to fits file {0}'.format(filename)
            emsg2 = '    Error {0}: {1}'.format(type(e), e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2, emsg3])

    # ignore truncated comment warning since spirou images have some poorly 
    #   formatted header cards
    # TODO: This should not be suppressed but dealt with properly!
    w1 = []
    for warning in w:
        wmsg = 'Card is too long, comment will be truncated.'
        if wmsg != str(warning.message):
            w1.append(warning)
    # add warnings to the warning logger and log if we have them
    spirouCore.spirouLog.warninglogger(w1)
    # deal with output dictionary (of required keys)
    p = write_output_dict(p, filename, hdict)
    # return p
    return p



def write_image_multi(p, filename, image_list, hdict=None, dtype=None,
                      hdicts=None, dtypes=None):
    """
    Writes a set of images (image_list") and its header to file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                output: dict, the output filename as key and the
                        output file headers as the values
    :param filename: string, filename to save the fits file to
    :param image_list: list of "numy arrys", the list of images to save each
                       image must be a numpy array (2D)
    :param hdict: dictionary or None, header dictionary to write to fits file.
                  Written to the primary only! (see hdicts for adding to all)

                Must be in form:

                        hdict[key] = (value, comment)
                or
                        hdict[key] = value     (comment will be equal to
                                                "UNKNOWN"
                if None does not write header to fits file

    :param dtype: None or hdu format type, forces the image to be in the
                  format type specified (if not None). Written to the
                  primary only! (see dtypes for adding to all)

                  valid formats are for example: 'int32', 'float64'

    :param hdicts: list form of hdict (to allow header for each image) to not
                   set a dictionary use element value as None
                   i.e. [hdict1, hdict2, None, hdict3]

    :param dtypes: list form of dtype (to allow dtype to be added to each image)
                   to not force set a dtype use element value as None
                   i.e. [dtype1, None, dtype2]

    :return None:
    """
    func_name = __NAME__ + '.write_image_multi()'
    # check if file exists and remove it if it does
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception as e:
            emsg1 = ' File {0} already exists and cannot be overwritten.'
            emsg2 = '    Error {0}: {1}'.format(type(e), e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1.format(filename), emsg2, emsg3])
    # ------------------------------------------------------------------------
    # check if image_list is a list
    if type(image_list) not in [np.ndarray, list]:
        emsg1 = '"image_list" must be a list of images (currently type={0})'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1.format(type(image_list)), emsg2])
    # else we need to check hdict and dtype are lists
    else:
        # handle multiple dtypes
        if dtypes is not None:
            if len(dtypes) != len(image_list):
                emsg1 = ('dtypes must be the same length as image_list')
                emsg2 = '    function = {0}'.format(func_name)
                WLOG('error', DPROG, [emsg1, emsg2])
        elif type(dtype) not in [np.ndarray, list]:
            dtypes = [dtype] + [None] * (len(image_list) - 1)
        elif len(dtype) != len(image_list):
            emsg1 = ('If "dtype" is a list it must be the same length as '
                     'image_list')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
        else:
            dtypes = dtype
        # handle multiple hdicts
        if hdicts is not None:
            if len(hdicts) != len(image_list):
                emsg1 = ('dtypes must be the same length as image_list')
                emsg2 = '    function = {0}'.format(func_name)
                WLOG('error', DPROG, [emsg1, emsg2])

        elif type(hdict) not in [np.ndarray, list]:
            hdicts = [hdict] + [None] * (len(image_list) - 1)
        elif len(hdict) != len(image_list):
            emsg1 = ('If "hdict" is a list it must be the same length as '
                     'image_list')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
        else:
            hdicts = hdict
    # ------------------------------------------------------------------------
    # create the multi HDU list
    try:
        # add the first image to the primary hdu
        hdu1 = fits.PrimaryHDU(image_list[0])
        # add all others afterwards
        hdus = [hdu1]
        for image in image_list[1: ]:
            hdus.append(fits.ImageHDU(image))
        # add to HDU list
        hdu = fits.HDUList(hdus)
    except Exception as e:
        emsg1 = 'Cannot open image with astropy.io.fits'
        emsg2 = '    Error {0}: {1}'.format(type(e), e)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2, emsg3])
        hdu = None
    # force type
    if dtypes is not None:
        for it in range(len(hdu)):
            if dtypes[it] is not None:
                hdu[it].scale(type=dtypes[it], **SCALEARGS)
    # add header keys to the hdu header
    if hdicts is not None:
        for it in range(len(hdu)):
            if hdicts[it] is not None:
                for key in list(hdicts[it].keys()):
                    hdu[it].header[key] = hdicts[it][key]

    # close hdu we are finished
    if hdu is not None:
        hdu.close()
    # write to file
    with warnings.catch_warnings(record=True) as w:
        try:
            hdu.writeto(filename, overwrite=True)
        except Exception as e:
            emsg1 = 'Cannot write image to fits file {0}'.format(filename)
            emsg2 = '    Error {0}: {1}'.format(type(e), e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2, emsg3])

    # deal with output dictionary (of required keys)
    p = write_output_dict(p, filename, hdicts[0])
    # return p
    return p


def write_output_dict(p, filename, hdict):
    # deal with output dictionary (of required keys)
    bfilename = os.path.basename(filename)
    output_file_header_keys = spirouConfig.Constants.OUTPUT_FILE_HEADER_KEYS(p)
    p['OUTPUTS'][bfilename] = OrderedDict()
    # loop around the keys and find them in hdict (or add null character if
    #     not found)
    for key in output_file_header_keys:
        if key in hdict:
            p['OUTPUTS'][bfilename][key] = str(hdict[key][0])
        else:
            p['OUTPUTS'][bfilename][key] = '--'
    # add DRS_TYPE
    p['OUTPUTS'][bfilename]['DRS_TYPE'] = p['DRS_TYPE']
    # return p
    return p

def read_tilt_file(p, hdr=None, filename=None, key=None, return_filename=False,
                   required=True):
    """
    Reads the tilt file (from calib database or filename) and using the
    'kw_TILT' keyword-store extracts the tilts for each order

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                kw_TILT: list, the keyword list for kw_TILT (defined in
                         spirouKeywords.py)
                IC_TILT_NBO: int, Number of orders in tilt file

    :param hdr: dictionary or None, the header dictionary to look for the
                     acquisition time in, if None loads the header from
                     p['FITSFILENAME']
    :param filename: string or None, the filename and path of the tilt file,
                     if None gets the TILT file from the calib database
                     keyword "TILT"
    :param key: string or None, if None key='TILT' else uses string as key
                from calibDB (first entry) to get tilt file
    :param return_filename: bool, if true return the filename only
    :param required: bool, if True code generates log exit else raises a
                     ConfigError (to be caught)

    if return_filename is False
        :return tilt: numpy array (1D), the tilts for each order
    else
        :return read_file: string, name of tilt file
    """
    if key is None:
        key = 'TILT'
    # get filename
    if filename is None:
        read_file = spirouDB.GetCalibFile(p, key, hdr, required=required)
    else:
        read_file = filename
    # deal with returning filename
    if return_filename:
        return read_file
    # log tilt file used
    wmsg = 'Using {0} file: "{1}"'.format(key, read_file)
    WLOG('', p['LOG_OPT'], wmsg)
    # read read_file
    rout = readimage(p, filename=read_file, log=False)
    image, hdict, _, nx, ny = rout
    # get the tilt keys
    tilt = read_key_2d_list(p, hdict, p['KW_TILT'][0], p['IC_TILT_NBO'], 1)
    # return the first set of keys
    return tilt[:, 0]


def read_wave_file(p, hdr=None, filename=None, key=None, return_header=False,
                   return_filename=False, required=True):
    """
    Reads the wave file (from calib database or filename)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param hdr: dictionary or None, the header dictionary to look for the
                     acquisition time in, if None loads the header from
                     p['FITSFILENAME']
    :param filename: string or None, the filename and path of the tilt file,
                     if None gets the WAVE file from the calib database
                     keyword "WAVE_{fiber}"
    :param key: string or None, if None key='WAVE' else uses string as key
                from calibDB (first entry) to get wave file
    :param return_header: bool, if True returns header file else just returns
                          wave file
    :param return_filename: bool, if true return the filename only
    :param required: bool, if True code generates log exit else raises a
                     ConfigError (to be caught)

    if return_filename is False and return header is False

        :return wave: numpy array (2D), the wavelengths for each pixel
                      (x-direction) for each order
    elif return_filename is False:
        :return wave: numpy array (2D), the wavelengths for each pixel
                      (x-direction) for each order
        :return hdict: dictionary, the header file of the wavelength solution
    else:
        :return read_file: string, the file name associated with the wavelength
                           solution
    """
    if key is None:
        key = 'WAVE_' + p['FIBER']
    # get filename
    if filename is None:
        read_file = spirouDB.GetCalibFile(p, key, hdr, required=required)
    else:
        read_file = filename
    # deal with returning filename only
    if return_filename:
        return read_file
    # log wave file used
    wmsg = 'Using {0} file: "{1}"'.format(key, read_file)
    WLOG('', p['LOG_OPT'], wmsg)
    # read read_file
    rout = readimage(p, filename=read_file, log=False)
    wave, hdict, _, nx, ny = rout

    if return_header:
        return wave, hdict
    else:
        # return the wave file
        return wave


def read_wave_params(p, hdr):
    func_name = __NAME__ + '.read_wave_params()'
    # get constants from p
    key = p['KW_WAVE_PARAM'][0]
    dim1key = p['KW_WAVE_ORD_N'][0]
    dim2key = p['KW_WAVE_LL_DEG'][0]
    # get dim1 value
    if dim1key in hdr:
        dim1 = hdr[dim1key]
    else:
        emsg1 = 'key = "{0}" not found in WAVE HEADER (for dim1)'
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1.format(dim1key), emsg2])
        dim1 = None
    # get dim2 value
    if dim2key in hdr:
        dim2 = hdr[dim2key] + 1
    else:
        emsg1 = 'key = "{0}" not found in WAVE HEADER (for dim2)'
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1.format(dim2key), emsg2])
        dim2 = None
    # get wave params from header
    wave_params = read_key_2d_list(p, hdr, key, dim1, dim2)
    # return 2d list
    return wave_params


def get_wave_solution(p, image=None, hdr=None):
    func_name = __NAME__ + '.get_wave_solution()'
    # get constants from p
    dim1key = p['KW_WAVE_ORD_N'][0]
    dim2key = p['KW_WAVE_LL_DEG'][0]
    # conditions to use header instead of calibDB
    cond1 = (dim1key in hdr) and (dim2key in hdr)
    cond2 = image is not None
    cond3 = not p['CALIB_DB_FORCE_WAVESOL']

    # if we have header use header to get wave solution
    if cond1 and cond2 and cond3:
        # get the wave parmaeters from the header
        wave_params = read_wave_params(p, hdr)
        # get the dimensions
        dim1 = hdr[dim1key]
        # check that dim1 is the correct number of orders
        if dim1 != image.shape[0]:
            emsg1 = ('Number of orders in HEADER ({0}={1}) not compatible with '
                    'number of orders in image ({2}')
            eargs = [dim1key, dim1, image.shape[0]]
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1.format(*eargs), emsg2])
        # define empty wave solution
        wave = np.zeros_like(image)
        xpixels = np.arange(image.shape[1])
        # load the wave solution for each order
        for order_num in range(dim1):
            wave[order_num] = np.polyval(wave_params[order_num][::-1], xpixels)
    # else we use the calibDB (using the header) to get the wave solution
    else:
        wave = read_wave_file(p, hdr)
    # return wave solution
    return wave


def get_good_object_name(p, hdr=None, rawname=None):
    # get raw name
    if (rawname is None) or (hdr is not None):
        rawname = hdr[p['kw_OBJNAME'][0]]
    else:
        rawname = str(rawname)
    # remove spaces from start and end
    name = rawname.strip()
    # replace bad characters in between with '_'
    for badchar in BADCHARS:
        name = name.replace(badchar, '_')
    # return cleaned up name
    return name



def read_hcref_file(p, hdr=None, filename=None, key=None, return_header=False,
                    return_filename=False, required=True):
    """
    Reads the hcref file (from calib database or filename)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param hdr: dictionary or None, the header dictionary to look for the
                     acquisition time in, if None loads the header from
                     p['FITSFILENAME']
    :param filename: string or None, the filename and path of the tilt file,
                     if None gets the WAVE file from the calib database
                     keyword "HCREF_{fiber}"
    :param key: string or None, if None key='HCREF' else uses string as key
                from calibDB (first entry) to get wave file
    :param return_header: bool, if True returns header file else just returns
                          wave file
    :param return_filename: bool, if true return the filename only
    :param required: bool, if True code generates log exit else raises a
                     ConfigError (to be caught)

    if return_filename is False and return header is False

        :return hcref: numpy array (2D), the hc reference data (e2ds file)
    elif return_filename is False:
        :return wave: numpy array (2D), the wavelengths for each pixel
                      (x-direction) for each order
        :return hdict: dictionary, the header file of the wavelength solution
    else:
        :return read_file: string, the file name associated with the wavelength
                           solution
    """
    if key is None:
        key = 'HCREF_' + p['FIBER']
    # get filename
    if filename is None:
        read_file = spirouDB.GetCalibFile(p, key, hdr, required=required)
    else:
        read_file = filename
    # deal with returning filename only
    if return_filename:
        return read_file
    # read read_file
    rout = readimage(p, filename=read_file, log=False)
    hcref, hdict, _, nx, ny = rout

    if return_header:
        return hcref, hdict
    else:
        # return the wave file
        return hcref


def read_flat_file(p, hdr=None, filename=None, key=None, required=True):
    """
    Reads the flat file (from calib database or filename)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                log_opt: string, log option, normally the program name

    :param hdr: dictionary or None, the header dictionary to look for the
                     acquisition time in, if None loads the header from
                     p['FITSFILENAME']
    :param filename: string or None, the filename and path of the tilt file,
                     if None gets the FLAT file from the calib database
                     keyword "FLAT_{fiber}"
    :param key: string or None, if None key='FLAT_{fiber}' else uses string
                as key from calibDB (first entry) to get wave file
    :param required: bool, if True code generates log exit else raises a
                     ConfigError (to be caught)

    :return wave: numpy array (2D), the flat image
    """
    func_name = __NAME__ + '.read_flat_file()'
    if key is None:
        try:
            key = 'FLAT_{0}'.format(p['FIBER'])
        except spirouConfig.ConfigError as _:
            emsg1 = 'Parameter "fiber" not found in parameter dictionary'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # get filename
    if filename is None:
        read_file = spirouDB.GetCalibFile(p, key, hdr, required=required)
    else:
        read_file = filename
    # log flat file used
    wmsg = 'Using {0} file: "{1}"'.format(key, read_file)
    WLOG('', p['LOG_OPT'], wmsg)
    # read read_file
    rout = readdata(p, filename=read_file, log=False)
    flat, hdict, _, nx, ny = rout
    # return the wave file
    return flat


def read_blaze_file(p, hdr=None, filename=None, key=None, required=True):
    """
    Reads the blaze file (from calib database or filename)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param hdr: dictionary or None, the header dictionary to look for the
                     acquisition time in, if None loads the header from
                     p['FITSFILENAME']
    :param filename: string or None, the filename and path of the tilt file,
                     if None gets the WAVE file from the calib database
                     keyword "BLAZE_{fiber}"
    :param key: string or None, if None key='BLAZE_{fiber}' else uses string
                as key from calibDB (first entry) to get wave file
    :param required: bool, if True code generates log exit else raises a
                     ConfigError (to be caught)

    :return blaze: numpy array (2D), the blaze function (along x-direction)
                  for each order
    """
    func_name = __NAME__ + '.read_blaze_file()'
    if key is None:
        try:
            key = 'BLAZE_{0}'.format(p['FIBER'])
        except spirouConfig.ConfigError as _:
            emsg1 = 'Parameter "fiber" not found in parameter dictionary'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # get filename
    if filename is None:
        read_file = spirouDB.GetCalibFile(p, key, hdr, required=required)
    else:
        read_file = filename
    # log blaze file used
    wmsg = 'Using {0} file: "{1}"'.format(key, read_file)
    WLOG('', p['LOG_OPT'], wmsg)
    # read read_file
    rout = readdata(p, filename=read_file, log=False)
    blaze, hdict, _, nx, ny = rout
    # return the wave file
    return blaze


def read_order_profile_superposition(p, hdr=None, filename=None,
                                     required=True):
    """
    Read the order profile superposition image from either "filename" (if not
    None) or get filename from the calibration database using "p"

    "ORDER_PROFILE_{X}" must be in calibration database if filename is None
    where X is either p["ORDERP_FILE"] or p["FIBER"] (presedence in that order)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                ORDERP_FILE: string, the suffix for the order profile
                             calibration database key (usually the fiber type)
                             - read from "orderp_file_fpall"
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                log_opt: string, log option, normally the program name

    :param hdr: dictionary or None, header dictionary (used to get the
                acquisition time if trying to get "ORDER_PROFILE_{X}" from
                the calibration database, if None uses the header from the
                first file in "ARG_FILE_NAMES" i.e. "FITSFILENAME"
    :param filename: string or None, if defined no need for "hdr" or keys from
                     "p" the order profile is read straight from "filename"
    :param required: bool, if True code generates log exit else raises a
                     ConfigError (to be caught)

    :return orderp: numpy array (2D), the order profile image read from file
    """

    func_name = __NAME__ + '.read_order_profile_superposition()'
    # Log that we are reading the order profile
    wmsg = 'Reading order profile of Fiber {0}'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(p['FIBER']))
    # construct key
    # get loc file
    if filename is not None:
        key = None
    elif 'ORDERP_FILE' in p:
        key = 'ORDER_PROFILE_{0}'.format(p['ORDERP_FILE'])
    elif 'FIBER' in p:
        key = 'ORDER_PROFILE_{0}'.format(p['FIBER'])
    else:
        emsg1 = ('Cannot open the order profile: Parameter dictionary '
                 'does not contain key "ORDERP_FILE" or "FIBER"')
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        key = None
    # construct read filename from calibDB or from "filename"
    if filename is None:
        read_file = spirouDB.GetCalibFile(p, key, hdr, required=required)
    else:
        read_file = filename
    # log order profile file used
    wmsg = 'Using {0} file: "{1}"'.format(key, read_file)
    WLOG('', p['LOG_OPT'], wmsg)
    # read read_file
    rout = readimage(p, filename=read_file, log=False)
    # return order profile (via readimage = image, hdict, commments, nx, ny
    return rout


# =============================================================================
# Define header User functions
# =============================================================================
def keylookup(p, d=None, key=None, has_default=False, default=None,
              required=True):
    """
    Looks for a key in dictionary "p" or "d", if has_default is True sets
    value of key to 'default' if not found else logs an error

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                "key": if d is None must contain key="key" or error is raised
    :param d: dictionary, any dictionary, if None uses parameter dictionary
              if "d" is not None then must contain key="key" or error is raised
    :param key: string, key in the dictionary to find
    :param has_default: bool, if True uses "default" as the value if key
                        not found
    :param default: object, value of the key if not found and
                    has_default is True
    :param required: bool, if True key is required and causes error is missing
                     if False and key not found value is None

    :return value: object, value of p[key] or default (if has_default=True)
    """
    func_name = __NAME__ + '.keylookup()'
    # deal with d = None
    if d is None:
        name = 'p'
        d = p
    else:
        name = 'd'
    # deal with no key
    if key is None:
        WLOG('error', p['LOG_OPT'], 'Must define key')
    # if we have default value use get else try standard call or log if error
    value = None
    if has_default:
        value = d.get(key, default)
    else:
        try:
            value = d[key]
        except KeyError:
            if not required:
                return None
            else:
                emsg1 = 'Key "{0}" not found in "{1}"'.format(key, name)
                emsg2 = '    function = {0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])

    return value


def keyslookup(p, d=None, keys=None, has_default=False, defaults=None):
    """
    Looks for keys in dictionary "p" or "d", if has_default is True sets
    value of key to 'default' if not found else logs an error

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                "key": if d is None must contain key="key" or error is raised
    :param d: dictionary, any dictionary, if None uses parameter dictionary
              if "d" is not None then must contain key="key" or error is raised
    :param keys: list of strings, keys in the dictionary to find
    :param has_default: bool, if True uses "default" as the value if key
                        not found
    :param defaults: list of objects or None, values of the keys if not
                     found and has_default is True

    :return values: list of objects, values of p[key] for key in keys
                    or default value for each key (if has_default=True)
    """
    func_name = __NAME__ + '.keyslookup()'
    # make sure keys is a list
    try:
        keys = list(keys)
    except TypeError:
        emsg1 = '"keys" must be a valid python list'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])

    # if defaults is None --> list of Nones else make sure defaults is a list
    if defaults is None:
        defaults = list(np.repeat([None], len(keys)))
    else:
        try:
            defaults = list(defaults)
            if len(defaults) != len(keys):
                emsg1 = '"defaults" must be same length as "keys"'
                emsg2 = '    function = {0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        except TypeError:
            emsg1 = '"defaults" must be a valid python list'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])

    # loop around keys and look up each key
    values = []
    for k_it, key in enumerate(keys):
        # get the value for key
        v = keylookup(p, d, key, has_default, default=defaults[k_it])
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
    :param forbid_keys: bool, if True uses the forbidden copy keys (defined in
                        spirouConfig.Constants.FORBIDDEN_COPY_KEYS() to remove
                        certain keys from those being copied, if False copies
                        all keys from input header

    :return hdict: dictionary, (updated or new) header dictionary containing
                   key/value pairs from the header (that are NOT in
                   spirouConfig.spirouConst.FORBIDDEN_COPY_KEY)
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


def copy_root_keys(hdict=None, filename=None, root=None, ext=0):
    """
    Copy keys from a filename to hdict

    :param hdict: dictionary or None, header dictionary to write to fits file
                  if None hdict is created
    :param filename: string, location and filename of the FITS rec to open

    :param root: string, if we have "root" then only copy keywords that start
                 with this string (prefix)

    :param ext: int, the extension of the FITS rec to open header from
                (defaults to 0)

    :return hdict: dictionary containing all keys to write to file each
                   key has a value = [header value, comment]
    """
    func_name = __NAME__ + '.copy_root_keys()'
    # deal with no hdict and no filename
    if hdict is None:
        hdict = OrderedDict()
    if filename is None:
        emsg1 = 'No filename defined (Filename is required)'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])
    # read header file
    hdr, cmts = read_raw_header(filename=filename, headerext=ext)
    # loop around header keys
    for key in list(hdr.keys()):
        # if we have a root only copy those keys that start with root
        if root is not None:
            if key.startswith(root):
                hdict[key] = (hdr[key], cmts[key])
        else:
            hdict[key] = (hdr[key], cmts[key])
    # return header
    return hdict


def add_new_key(hdict=None, keywordstore=None, value=None):
    """
    Add a new key to hdict from keywordstore, if value is not None then the
    keywordstore value is updated. Each keywordstore is in form:
            [key, value, comment]    where key and comment are strings
    if hdict is None creates a new dictionary

    :param hdict: dictionary or None, storage for adding to FITS rec
    :param keywordstore: list, keyword list (defined in spirouKeywords.py)
                         must be in form [string, value, string]
    :param value: object or None, if any python object (other than None) will
                  replace the value in keywordstore (i.e. keywordstore[1]) with
                  value, if None uses the value = keywordstore[1]

    :return hdict: dictionary, storage for adding to FITS rec
    """
    func_name = __NAME__ + '.add_ney_key()'
    # deal with no hdict
    if hdict is None:
        hdict = OrderedDict()
    # deal with no keywordstore
    if keywordstore is None:
        emsg1 = '"keywordstore" must be defined.'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])

    # extract keyword, value and comment and put it into hdict
    key, dvalue, comment = extract_key_word_store(keywordstore, func_name)

    # set the value to default value if value is None
    if value is None:
        value = dvalue
    # add to the hdict dictionary in form (value, comment)
    hdict[key] = (value, comment)
    # return hdict
    return hdict


def add_new_keys(hdict=None, keywordstores=None, values=None):
    """
    Add a set of new key to hdict from keywordstores, if values is not None,
    then all values are set to None, keywordstores is a list of keywordstore
    objects. Each keywordstore is in form:
            [key, value, comment]    where key and comment are strings

    :param hdict: dictionary or None, storage for adding to FITS rec if None
                  creates a new dictionary to store keys in
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
    func_name = __NAME__ + '.add_new_keys()'
    # deal with no hdict
    if hdict is None:
        hdict = OrderedDict()

    if keywordstores is None:
        emsg1 = '"keywordstores" must be defined as a list of keyword stores'
        emsg2 = ('   keywordstore must be [name, value, comment] = '
                 '[string, object, string]')
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2, emsg3])

    # deal with no values
    if values is None:
        values = np.repeat([None], len(keywordstores))
    # loop around keywordstores and pipe to add_new_key for each iteration
    for k_it, keywordstore in enumerate(keywordstores):
        hdict = add_new_key(hdict, keywordstore, values[k_it])
    # return hdict
    return hdict


def add_key_1d_list(hdict, keywordstore, values=None, dim1name='order'):
    """
    Add a new 1d list to key using the keywordstorage[0] as prefix in form
    keyword = kewordstoreage + row number

    :param hdict: dictionary, storage for adding to FITS rec
    :param keywordstore: list, keyword list (defined in spirouKeywords.py)
                         must be in form [string, value, string]
    :param values: numpy array or 1D list of keys or None

                  if numpy array or 1D list will create a set of keys in form
                  keyword = kewordstoreage + row number
                  where row number is the position in values
                  with value = values[row number][column number]

                  if None uses the value = keywordstore[1]
    :param dim1name: string, the name for dimension 1 (rows), used in FITS rec
                     HEADER comments in form:
          COMMENT = keywordstore[2] dim1name={row number}

    :return hdict: dictionary, storage for adding to FITS rec
    """
    func_name = __NAME__ + '.add_key_1d_list()'
    # extract keyword, value and comment and put it into hdict
    key, dvalue, comment = extract_key_word_store(keywordstore, func_name)
    # set the value to default value if value is None
    if values is None:
        values = [dvalue]
    # convert to a numpy array
    values = np.array(values)
    # loop around the 2D array
    dim1 = len(values)
    for i_it in range(dim1):
            # construct the key name
            keyname = '{0}{1}'.format(key, i_it)
            # get the value
            value = values[i_it]
            # construct the comment name
            comm = '{0} {1}={2}'.format(comment, dim1name, i_it)
            # add to header dictionary
            hdict[keyname] = (value, comm)
    # return the header dictionary
    return hdict


def add_key_2d_list(hdict, keywordstore, values=None, dim1name='order',
                    dim2name='coeff'):
    """
    Add a new 2d list to key using the keywordstorage[0] as prefix in form
    keyword = kewordstoreage + number

    where number = (row number * number of columns) + column number

    :param hdict: dictionary, storage for adding to FITS rec
    :param keywordstore: list, keyword list (defined in spirouKeywords.py)
                         must be in form [string, value, string]
    :param values: numpy array or 2D list of keys or None

                  if numpy array or 2D list will create a set of keys in form
                  keyword = kewordstoreage + number
                  where number = (row number*number of columns)+column number
                  with value = values[row number][column number]

                  if None uses the value = keywordstore[1]
    :param dim1name: string, the name for dimension 1 (rows), used in FITS rec
                     HEADER comments in form:
          COMMENT = keywordstore[2] dim1name={row number} dim2name={col number}
    :param dim2name: string, the name for dimension 2 (cols), used in FITS rec
                     HEADER comments in form:
          COMMENT = keywordstore[2] dim1name={row number} dim2name={col number}

    :return hdict: dictionary, storage for adding to FITS rec
    """
    func_name = __NAME__ + '.add_key_2d_list()'
    # extract keyword, value and comment and put it into hdict
    key, dvalue, comment = extract_key_word_store(keywordstore, func_name)
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
            cargs = [comment, dim1name, i_it, dim2name, j_it]
            comm = '{0} {1}={2} {3}={4}'.format(*cargs)
            # add to header dictionary
            hdict[keyname] = (value, comm)
    # return the header dictionary
    return hdict


def extract_key_word_store(keywordstore=None, func_name=None):
    """
    Deal with extraction of key, value and comment from keywordstore
    the keywordstore should be a list in the following form:

    [name, value, comment]     with types [string, object, string]

    :param keywordstore: list, keyword list (defined in spirouKeywords.py)
                         must be in form [string, value, string]
    :param func_name: string or None, if not None defined where the
                      keywordstore function is being called, if None is set to
                      here (spirouFITS.extract_key_word_store())

    :return key: string, the name/key of the HEADER (key/value/comment)
    :return value: object, any object to be put into the HEADER value
                   (under HEADER key="key")
    :return comment: string, the comment associated with the HEADER key
    """
    # deal with no func_name
    if func_name is None:
        func_name = __NAME__ + '.extract_key_word_store()'
    # extract keyword, value and comment and put it into hdict
    try:
        key, dvalue, comment = keywordstore
    except Exception as _:
        emsg1 = 'There was a problem with the "keywordstore"'
        emsg2 = '   It must be a list/tuple with of the following format:'
        emsg3 = '       [string, object, string]'
        emsg4 = '     where the first is the HEADER name of the keyword'
        emsg5 = '     where the second is the default value for the keyword'
        emsg6 = '     where the third is the HEADER comment'
        emsg7 = '   keywordstore currently is "{0}"'.format(keywordstore)
        emsg8 = '   function = {0}'.format(func_name)
        emsgs = [emsg1, emsg2, emsg3, emsg4, emsg5, emsg6, emsg7, emsg8]
        WLOG('error', DPROG, emsgs)
        key, dvalue, comment = None, None, None
    # return values
    return key, dvalue, comment


def get_type_from_header(p, keywordstore, hdict=None, filename=None):
    """
    Special FITS HEADER keyword - get the type of file from a FITS file HEADER
    using "keywordstore"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits

    :param keywordstore: list, a keyword store in the form
                         [name, value, comment] where the format is
                         [string, object, string]
    :param hdict: dictionary or None, the HEADER dictionary containing
                  key/value pairs from a FITS HEADER, if None uses the
                  header from "FITSFILENAME" in "p", unless filename is not None
                  This hdict is used to get the type of file
    :param filename: string or None, if not None and hdict is None, this is the
                     file which is used to extract the HEADER from to get
                     the type of file

    :return ftype: string, the type of file (extracted from a HEADER dictionary/
                   file) if undefined set to 'UNKNOWN'
    """
    func_name = __NAME__ + '.get_type_from_header()'
    # set up frequently used variables
    log_opt = p['LOG_OPT']
    # if we don't have the hdict then we need to load the header from file
    if hdict is None:
        # get file name
        if filename is None:
            try:
                fitsfilename = p['FITSFILENAME']
            except KeyError:
                emsg1 = '"fitsfilename" is not defined in parameter dictionary'
                emsg2 = '    function = {0}'.format(func_name)
                WLOG('error', log_opt, [emsg1, emsg2])
                fitsfilename = ''
        else:
            fitsfilename = filename
        # get the hdict
        hdict, _ = read_raw_header(fitsfilename, headerext=0)
    else:
        if type(hdict) not in [dict, OrderedDict, ParamDict]:
            emsg1 = ('"hdict" must be None or a valid python dictionary or '
                     'Parameter Dictionary')
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', log_opt, [emsg1, emsg2])
    # get the key from header dictionary
    if keywordstore[0] in hdict:
        return hdict[keywordstore[0]]
    else:
        return 'UNKNOWN'


def read_header(p=None, filepath=None, ext=0, return_comments=False):
    """
    Read the header from a file at "filepath" with extention "ext" (default=0)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param filepath: string, filename and path of FITS file to open
    :param ext: int, extension in FITS rec to open (default = 0)
    :param return_comments: bool, if True returns a dictionary of the comments

    :return hdict: dictionary, the dictionary with key value pairs
    """
    func_name = __NAME__ + '.read_header()'
    # if p is None
    if p is None:
        log_opt = ''
    else:
        log_opt = p['LOG_OPT']
    # if filepath is None raise error
    if filepath is None:
        emsg1 = 'Error "filepath" is required'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', log_opt, [emsg1, emsg2])
    # try to get header from filepath
    try:
        header = fits.getheader(filepath, ext=ext)
    except IOError:
        emsg1 = 'Cannot open header of file {0}'.format(filepath)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', log_opt, [emsg1, emsg2])
        header = None
    # load in to dictionary
    hdict = OrderedDict(zip(header.keys(), header.values()))
    cdict = OrderedDict(zip(header.keys(), header.comments))
    # return hdict
    if return_comments:
        return hdict, cdict
    else:
        return hdict


def read_key(p, hdict=None, key=None):
    """
    Read a key from hdict (or p if hdict is not defined) and return it's
    value.

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param hdict: dictionary or None, the dictionary to add the key to once
                  found, if None creates a new dictionary
    :param key: string, key in the dictionary to find

    :return value: object, the value of the key from hdict
                   (or p if hdict is None)
    """
    func_name = __NAME__ + '.read_key()'
    # deal with no key
    if key is None:
        emsg1 = 'Error "key" must be defined'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # return the value of the key
    return keylookup(p, hdict, key=key)


def read_key_2d_list(p, hdict, key, dim1, dim2):
    """
    Read a set of header keys that were created from a 2D list

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param hdict: dictionary, HEADER dictionary to extract key/value pairs from
    :param key: string, prefix of HEADER key to construct 2D list from
                 key[number]

                 where number = (row number * number of columns) + column number
                 where column number = dim2 and row number = range(0, dim1)
    :param dim1: int, the number of elements in dimension 1 (number of rows)
    :param dim2: int, the number of columns in dimension 2 (number of columns)

    if return_file is false:
        :return value: numpy array (2D), the reconstructed 2D list of variables
                       from the HEADER dictionary keys
    else:
        :return
    """
    func_name = __NAME__ + '.read_key_2d_list()'
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
                emsg1 = ('Cannot find key with dim1={1} dim2={2} in "hdict"'
                         '').format(keyname, dim1, dim2)
                emsg2 = '    function = {0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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

        if len(data.shape)==2
            :return nx: int, the shape in the first dimension,
                        i.e. data.shape[0]
            :return ny: int, the shape in the second dimension,
                        i.e. data.shape[1]
        if len(data.shape)!=2
            :return shape: tuple, data.shape
            :return empty: None, blank entry

    if getheader = False, getshape = False
    :return data: numpy array (2D), the image
    :return header: dictionary, the header file of the image

    if getheader = getshape = False
     :return data: numpy array (2D), the image
    """
    func_name = __NAME__ + '.read_raw_data()'
    # get the data
    try:
        hdu = fits.open(filename)
    except Exception as e:
        emsg1 = 'File "{0}" cannot be opened by astropy.io.fits'
        emsg2 = '   Error {0}: {1}'.format(type(e), e)
        emsg3 = '   function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1.format(filename), emsg2, emsg3])
        hdu = None
    # get the number of fits files in filename
    try:
        ext = len(hdu)
    except Exception as e:
        wmsg1 = 'Problem with one of the extensions'
        wmsg2 = '    Error reads: {0}'.format(e)
        WLOG('warning', DPROG, [wmsg1, wmsg2])
        ext = None

    # deal with unknown ext
    if ext is None:
        hdu = fits.open(filename)
        data, header = deal_with_bad_header(hdu)

    # Get the data and header based on how many extensions there are
    else:
        if ext == 1:
            openext = 0
        else:
            openext = 1
        # try to open the data and close the hdu
        try:
            data = hdu[openext].data
        except Exception as e:
            emsg1 = 'Could not open data for file "{0}" extension={1}'
            emsg2 = '    Error {0}: {1}'.format(type(e), e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1.format(filename, openext), emsg2,
                                  emsg3])
            data = None
        # get the header (if header extension is available else default to zero)
        if headerext <= ext:
            try:
                header = hdu[headerext].header
            except Exception as e:
                emsg1 = 'Could not open header for file "{0}" extension={1}'
                emsg2 = '    Error {0}: {1}'.format(type(e), e)
                emsg3 = '    function = {0}'.format(func_name)
                WLOG('error', DPROG, [emsg1.format(filename, openext), emsg2,
                                      emsg3])
                header = None
        else:
            header = hdu[0]

    # close the HDU we are finished with it
    if hdu is not None:
        hdu.close()

    # return based on whether header and shape are required
    if getheader and getshape:
        if len(data.shape) == 2:
            return data, header, data.shape[0], data.shape[1]
        else:
            return data, header, data.shape, None
    elif getheader:
        return data, header
    elif getshape:
        if len(data.shape) == 2:
            return data, data.shape[0], data.shape[1]
        else:
            return data, data.shape, None
    else:
        return data


def deal_with_bad_header(hdu):
    """
    Deal with bad headers by iterating through good hdu's until we hit a
    problem

    :param hdu: astropy.io.fits HDU

    :return data:
    :return header:
    """
    # define condition to pass
    cond = True
    # define iterator
    it = 0
    # define storage
    datastore = []
    headerstore = []
    # loop through HDU's until we cannot open them
    while cond:
        try:
            datastore.append(hdu[it].data)
            headerstore.append(hdu[it].header)
        except:
            cond = False
        # iterate
        it += 1
    # print message
    if len(datastore) > 0:
        WLOG('warning', DPROG, '    Partially recovered fits file')
        WLOG('warning', DPROG, '    Problem with ext={0}'.format(it-1))
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        emsg = 'Recovery failed: Fatal I/O Error cannot load file.'
        WLOG('error', DPROG, emsg)
        data, header = None, None
    else:
        data = datastore[valid[0]]
        header = hdu[0].header
    # return data and header
    return data, header


def read_raw_header(filename, headerext=0):
    """
    Reads the header of a fits file using astropy.io.fits

    :param filename: string, the filename to open with astropy.io.fits
    :param headerext: int, the extension to read the header from

    :return hdr: dictionary, the HEADER dictionary of key/value pairs,
                 where the values are the values in the HEADER
    :return cmt: dictionary,  the COMMENT dictionary from the HEADER fits file
                 of key/value pairs, where the values are the comments
                 from the HEADER file (for use in copying/writing keys to
                 new file)
    """
    func_name = __NAME__ + '.read_raw_header()'
    # get the data
    try:
        hdu = fits.open(filename)
    except Exception as e:
        emsg1 = 'File "{0}" cannot be opened by astropy.io.fits'
        emsg2 = '   Error {0}: {1}'.format(type(e), e)
        emsg3 = '   function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1.format(filename), emsg2, emsg3])
        hdu = None
    # get the number of fits files in filename
    ext = len(hdu)
    # Get the data and header based on how many extensions there are
    if ext == 1:
        openext = 0
    else:
        openext = 1
    # get the header (if header extension is available else default to zero)
    if headerext <= ext:
        try:
            header = hdu[headerext].header
        except Exception as e:
            emsg1 = 'Could not open header for file "{0}" extension={1}'
            emsg2 = '    Error {0}: {1}'.format(type(e), e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1.format(filename, openext), emsg2,
                                  emsg3])
            header = None
    else:
        header = hdu[0]
    # convert header to python dictionary
    hdr = OrderedDict(zip(header.keys(), header.values()))
    cmt = OrderedDict(zip(header.keys(), header.comments))

    # return header dictionaries
    return hdr, cmt


def math_controller(p, data, header, filenames, framemath=None, directory=None):
    """
    uses the framemath key to decide how 'arg_file_names' files are added to
    data (fitfilename)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param data: numpy array (2D), the image
    :param header: header dictionary from readimage (ReadImage) function
    :param filenames: list of strings, the filenames to read and combine with
                      "data"
    :param framemath: string, or None controls how files should be added

                currently supported are:
                'add' or '+'           - adds the frames
                'sub' or '-'           - subtracts the frames
                'average' or 'mean'    - averages the frames
                'multiply' or '*'      - multiplies the frames
                'divide' or '/'        - divides the frames
                'none' or None         - does not do any math

    :param directory: string or None, if not None defines the directory to use
                      if the filenames have an absolute path this is ignored,
                      if directory is None p['ARG_FILE_DIR'] is used.

    :return p: dictionary, parameter dictionary
    :return data: numpy array (2D), the image
    :return header: header dictionary from readimage (ReadImage) function
    """
    func_name = __NAME__ + '.math_controler()'
    # deal with no framemath
    if framemath is None:
        return p, data, header
    # set up frequently used variables
    log_opt = p['LOG_OPT']
    # get math type
    kind, op = math_type(p, framemath)
    # if we have no math don't continue
    if kind == 'no':
        return p, data, header
    # if we have only one frame don't continue
    if len(filenames) < 1:
        return p, data, header
    # log that we are adding frames
    WLOG('info', log_opt, '{0} {1} frame(s)'.format(kind, len(filenames)))
    # chosen dir (if filenames is not an absolute path)
    if directory is None:
        directory = p['ARG_FILE_DIR']
    # loop around each frame
    for f_it in range(len(filenames)):
        # construct frame file name
        if os.path.exists(filenames[f_it]):
            framefilename = filenames[f_it]
        else:
            framefilename = os.path.join(directory, filenames[f_it])
        # check whether frame file name exists, log and exit if not
        if not os.path.exists(framefilename):
            emsg1 = 'File "{0}" does not exist'.format(framefilename)
            emsg2 = '    function {0}'.format(func_name)
            WLOG('error', log_opt, [emsg1, emsg2])
        else:
            # load that we are reading this file
            WLOG('', log_opt, 'Reading File: ' + framefilename)
            # get tmp data and tmp header
            dtmp, htmp = read_raw_data(framefilename, True, False)
            # finally add/subtract/multiple/divide data
            if op in ['+', 'mean']:
                data += dtmp
            elif op == '-':
                data -= dtmp
            elif op == '*':
                data *= dtmp
            elif op == '/':
                data /= dtmp
            else:
                continue
    # if we need to average data then divide by nbframes
    if op == 'mean':
        data /= (len(filenames) + 1)
    # return data
    return p, data, header


def math_type(p, framemath):
    """
    Take the string "framemath" and choose which math operator to use to combine
    files currently supported combining math operators are:
        'ADD', '+', 'SUB', '-', 'AVERAGE', 'MEAN', 'MULTIPLY', '*',
        'DIVIDE', '/', 'NONE'

    :param p: parameter dictionary
    :param framemath: string, the way to combine files currently supported
                      strings are:
                'ADD', '+', 'SUB', '-', 'AVERAGE', 'MEAN', 'MULTIPLY', '*',
                'DIVIDE', '/', 'NONE'

    :return kind: string, description of math operator
    :return op: string, operator string (used to do operation)
    """

    func_name = __NAME__ + 'math_type'
    # define acceptable MATH
    acceptable_math = ['ADD', '+', 'SUB', '-', 'AVERAGE', 'MEAN',
                       'MULTIPLY', '*', 'DIVIDE', '/', 'NONE']
    # convert add to upper case
    fm = framemath.upper()
    # check that frame math is acceptable if not report to log
    if fm not in acceptable_math:
        emsgs = ['framemath="{0}" not a valid operation'.format(fm),
                 '    must be one of the following:']
        for a_it in range(0, int(len(acceptable_math)/3)*3, 3):
            a_math = acceptable_math[a_it: a_it+3]
            emsgs.append('\t "{0}", "{1}", "{2}"'.format(*a_math))
        emsgs.append('    Error raised in function = {0}'.format(func_name))
        WLOG('error', p['LOG_OPT'], emsgs)
    # select text for logging
    if fm in ['ADD', '+']:
        kind, op = 'Adding', '+'
    elif fm in ['MEAN', 'AVERAGE']:
        kind, op = 'Averaging', 'mean'
    elif fm in ['SUB', '-']:
        kind, op = 'Subtracting', '-'
    elif fm in ['MULTIPLY', '*']:
        kind, op = 'Multiplying', '*'
    elif fm in ['DIVIDE', '/']:
        kind, op = 'Dividing', '/'
    else:
        kind, op = 'no', None
    return kind, op


# =============================================================================
# End of code
# =============================================================================
