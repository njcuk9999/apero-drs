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

from drsmodule import constants
from drsmodule.config import drs_log
from drsmodule import locale


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
ErrorEntry = locale.drs_text.ErrorEntry


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
            WLOG(params, 'error', ErrorEntry('01-001-00013', args=eargs))
        else:
            eargs = [os.path.basename(filename), dirname, func_name]
            WLOG(params, 'error', ErrorEntry('01-001-00012', args=eargs))
    # -------------------------------------------------------------------------
    # deal with obtaining data
    if fmt == 'fits-image':
        data, header = _read_fitsimage(params, filename, getdata, gethdr, ext)
    elif fmt == 'fits-table':
        data, header = _read_fitstable(params, filename, getdata, gethdr, ext)
    else:
        cfmts = ', '.join(allowed_formats)
        eargs = [filename, fmt, cfmts, func_name]
        WLOG(params, 'error', ErrorEntry('', args=eargs))
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
            emsg = ErrorEntry('01-001-00014', args=[filename, ext, type(e)])
            emsg += '\n\n' + ErrorEntry(string_trackback)
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
            emsg = ErrorEntry('01-001-00015', args=[filename, ext, type(e)])
            emsg += '\n\n' + ErrorEntry(string_trackback)
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
            emsg = ErrorEntry('01-001-00016', args=[filename, ext, type(e)])
            emsg += '\n\n' + ErrorEntry(string_trackback)
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
            emsg = ErrorEntry('01-001-00017', args=[filename, ext, type(e)])
            emsg += '\n\n' + ErrorEntry(string_trackback)
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
# TODO: write function
def combine(params, infiles, math='average'):

    # make sure infiles is a list
    if type(infiles) is not list:
        WLOG(params, 'error', ErrorEntry(''))

    # check that all infiles are the same DrsFileType

    # make new infile using math
    # question: how do we deal with multiple headers?

    # return combined infile (as a single entry list)
    return infiles


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
