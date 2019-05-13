#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 11:36

@author: cook
"""
from __future__ import division
import traceback
import os
from astropy.io import fits
from astropy.table import Table
import numpy as np

from terrapipe import constants
from terrapipe.config import drs_log
from terrapipe import locale
from terrapipe.config import drs_file

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
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry


# =============================================================================
# Define read functions
# =============================================================================
def read(params, filename, getdata=True, gethdr=False, fmt='fits-image', ext=0):
    """
    The drs fits file read function

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: string, the absolute path to the file
    :param getdata: bool, whether to return data from "ext"
    :param gethdr: bool, whether to return header from "ext"
    :param fmt: str, format of data (either 'fits-image' or 'fits-table'
    :param ext: int, the extension to open

    :type params: ParamDict
    :type filename: str
    :type getdata: bool
    :type gethdr: bool
    :type fmt: str
    :type ext: int

    :returns: if getdata and gethdr: returns data, header, if getdata return
              data, if gethdr returns header.
              if fmt 'fits-time' returns np.array for data and dictionary for
              header, if fmt 'fits-table' returns astropy.table for data and
              dictionary for header
    """
    func_name = __NAME__ + '.read()'
    # define allowed values of 'fmt'
    allowed_formats = ['fits-image', 'fits-table']
    # -------------------------------------------------------------------------
    # deal with filename not existing
    if not os.path.exists(filename):
        # check directory exists
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            eargs = [dirname, os.path.basename(filename), func_name]
            WLOG(params, 'error', TextEntry('01-001-00013', args=eargs))
        else:
            eargs = [os.path.basename(filename), dirname, func_name]
            WLOG(params, 'error', TextEntry('01-001-00012', args=eargs))
    # -------------------------------------------------------------------------
    # deal with obtaining data
    if fmt == 'fits-image':
        data, header = _read_fitsimage(params, filename, getdata, gethdr, ext)
    elif fmt == 'fits-table':
        data, header = _read_fitstable(params, filename, getdata, gethdr, ext)
    else:
        cfmts = ', '.join(allowed_formats)
        eargs = [filename, fmt, cfmts, func_name]
        WLOG(params, 'error', TextEntry('', args=eargs))
        data, header = None, None
    # -------------------------------------------------------------------------
    # deal with return
    if getdata and gethdr:
        return data, header
    elif getdata:
        return data
    elif gethdr:
        return header
    else:
        return None


def _read_fitsimage(params, filename, getdata, gethdr, ext):
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            data = fits.getdata(filename, ext=ext)
        except Exception as e:
            string_trackback = traceback.format_exc()
            emsg = TextEntry('01-001-00014', args=[filename, ext, type(e)])
            emsg += '\n\n' + TextEntry(string_trackback)
            WLOG(params, 'error', emsg)
            data = None
    else:
        data = None
    # -------------------------------------------------------------------------
    # deal with getting header
    if gethdr:
        try:
            header = fits.getheader(filename, ext=ext)
        except Exception as e:
            string_trackback = traceback.format_exc()
            emsg = TextEntry('01-001-00015', args=[filename, ext, type(e)])
            emsg += '\n\n' + TextEntry(string_trackback)
            WLOG(params, 'error', emsg)
            header = None
    else:
        header = None
    # -------------------------------------------------------------------------
    # return data and header
    return data, header


def _read_fitstable(params, filename, getdata, gethdr, ext):
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            data = Table.read(filename, fornat='fits')
        except Exception as e:
            string_trackback = traceback.format_exc()
            emsg = TextEntry('01-001-00016', args=[filename, ext, type(e)])
            emsg += '\n\n' + TextEntry(string_trackback)
            WLOG(params, 'error', emsg)
            data = None
    else:
        data = None
    # -------------------------------------------------------------------------
    # deal with getting header
    if gethdr:
        try:
            header = fits.getheader(filename, ext=ext)
        except Exception as e:
            string_trackback = traceback.format_exc()
            emsg = TextEntry('01-001-00017', args=[filename, ext, type(e)])
            emsg += '\n\n' + TextEntry(string_trackback)
            WLOG(params, 'error', emsg)
            header = None
    else:
        header = None
    # -------------------------------------------------------------------------
    # return data and header
    return data, header


# =============================================================================
# Define write functions
# =============================================================================
# TODO: write function (if needed)
def write(params, filename, header=None, comments=None):
    return 0


# =============================================================================
# Define other functions
# =============================================================================
def combine(params, infiles, math='average', same_type=True):
    """
    Takes a list of infiles and combines them (infiles must be DrsFitsFiles)
    combines using the math given.

    Allowed math:
        'sum', 'add', '+'
        'average', 'mean'
        'subtract', '-'
        'divide', '/'
        'multiply', 'times', '*'

    Note 'infiles' must be all the same DrsFitsFile type to combine by default,
    use 'same_type=False' to override this option

    Note the header is copied from infiles[0]

    :param params: ParamDict, parameter dictionary of constants
    :param infiles: list of DrsFiles, list of DrsFitsFiles to combine
    :param math: str, the math allowed (see above)
    :param same_type: bool, if True all infiles must have the same DrsFitFile
                      dtype

    :type params: ParamDict
    :type infiles: list[DrsFitsFile]
    :type math: str
    :type same_type: bool

    :return: Returns the combined DrsFitFile (header same as infiles[0])
    :rtype: DrsFitsFile
    """
    func_name = __NAME__ + '.combine()'
    # if we have a string assume we have 1 file and skip combine
    if type(infiles) is str:
        return infiles
    # make sure infiles is a list
    if type(infiles) is not list:
        WLOG(params, 'error', TextEntry('00-001-00020', args=[func_name]))
    # if we have only one file (or none) skip combine
    if len(infiles) == 1:
        return infiles[0]
    elif len(infiles) == 0:
        return infiles
    # check that all infiles are the same DrsFileType
    if same_type:
        for it, infile in enumerate(infiles):
            if infile.name != infiles[0].name:
                eargs = [infiles[0].name, it, infile.name, func_name]
                WLOG(params, 'error', TextEntry('00-001-00021', args=eargs))
    # make new infile using math
    outfile = infiles[0].combine(infiles[1:], math, same_type)
    # return combined infile
    return outfile


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
