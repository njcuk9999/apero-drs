#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 11:36

@author: cook
"""
from __future__ import division
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy import version as av
import os
import warnings
import traceback

from terrapipe import constants
from terrapipe.config.core import drs_log
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
# TODO: This should be changed for astropy -> 2.0.1
# bug that hdu.scale has bug before version 2.0.1
if av.major < 2 or (av.major == 2 and av.minor < 1):
    SCALEARGS = dict(bscale=(1.0 + 1.0e-8), bzero=1.0e-8)
else:
    SCALEARGS = dict(bscale=1, bzero=0)


# =============================================================================
# Define classes
# =============================================================================
class Header(fits.Header):
    """
    Wrapper class for fits headers that allows us to add functionality.
    - Stores temporary items with keys starting with '@@@'
       - Only shows up through "[]" and "in" operations
    - Can automatically convert NaN values to strings
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__temp_items = {}

    def __setitem__(self, key, item):
        if key.startswith('@@@'):
            self.__temp_items.__setitem__(self.__get_temp_key(key), item)
        else:
            super().__setitem__(key, item)

    def __getitem__(self, key):
        if key.startswith('@@@'):
            return self.__temp_items.__getitem__(self.__get_temp_key(key))
        else:
            return super().__getitem__(key)

    def __contains__(self, key):
        if key.startswith('@@@'):
            return self.__temp_items.__contains__(self.__get_temp_key(key))
        else:
            return super().__contains__(key)

    def copy(self, strip=False):
        header = Header(self, copy=True)
        if strip:
            header._strip()
        header.__temp_items = self.__temp_items.copy()
        return header

    def to_fits_header(self, strip=True, nan_to_string=True):
        header = super().copy(strip=strip)
        if nan_to_string:
            for key in list(header.keys()):
                value = header[key]
                if type(value) == float and np.isnan(value):
                    header[key] = 'NaN'
        return header

    @staticmethod
    def from_fits_header(fits_header):
        return Header(fits_header, copy=True)

    @staticmethod
    def __get_temp_key(key):
        return key[3:]


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
    allowed_formats = ['fits-image', 'fits-table', 'fits-multi']
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
    elif fmt == 'fits-multi':
        data, header = _read_fitsmulti(params, filename, getdata, gethdr)
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


def read_header(params, filename, ext=0):
    func_name = __NAME__ + '.read_header()'
    # try to open header
    try:
        header = fits.getheader(filename, ext=ext)
    except Exception as e:
        eargs = [os.path.basename(filename), ext, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('01-001-00010', args=eargs))
        header = None
    # return header
    return header


def _read_fitsmulti(params, filename, getdata, gethdr):

    func_name = __NAME__ + '._read_fitsmulti()'
    # attempt to open hdu of fits file
    try:
        hdulist = fits.open(filename)
    except Exception as e:
        eargs = [filename, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('01-001-00006', args=eargs))
        hdulist = None
    # -------------------------------------------------------------------------
    # get the number of fits files in filename
    try:
        n_ext = len(hdulist)
    except Exception as e:
        WLOG(params, 'warning', TextEntry('10-001-00005', args=[type(e), e]))
        n_ext = None
    # deal with unknown number of extensions
    if n_ext is None:
        data, header = deal_with_bad_header(params, hdulist, filename)
    # -------------------------------------------------------------------------
    # else get the data and header based on how many extnesions there are
    else:
        data, header = [], []
        for it in range(n_ext):
            # append header
            try:
                header.append(hdulist[it].header)
            except Exception as e:
                eargs = [os.path.basename(filename), it, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('01-001-00008', args=eargs))
            # append data
            try:
                if isinstance(hdulist[it].data, fits.BinTableHDU):
                    data.append(Table.read(hdulist[it].data))
                else:
                    data.append(hdulist[it].data)
            except Exception as e:
                eargs = [os.path.basename(filename), it, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('01-001-00007', args=eargs))
    # -------------------------------------------------------------------------
    # return data and/or header
    if getdata and gethdr:
        return data, header
    elif getdata:
        return data
    else:
        return header


def _read_fitsimage(params, filename, getdata, gethdr, ext=0):
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


def _read_fitstable(params, filename, getdata, gethdr, ext=0):
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
def write(params, filename, data, header, datatype, dtype=None, func=None):
    # deal with function name coming from somewhere else
    if func is None:
        func_name = __NAME__ + '.write()'
    else:
        func_name = '{0} (via {1})'.format(func, __NAME__ + '.write()')
    # ----------------------------------------------------------------------
    # check if file exists and remove it if it does
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception as e:
            eargs = [os.path.basename(filename), type(e), e, func_name]
            WLOG(params, 'error', TextEntry('01-001-00003', args=eargs))
    # ----------------------------------------------------------------------
    # make sure we are dealing with lists of data and headers
    if not isinstance(data, list):
        data = [data]
    if not isinstance(header, list):
        header = [header]
    if not isinstance(datatype, list):
        datatype = [datatype]
    if dtype is not None and not isinstance(dtype, list):
        dtype = [dtype]
    # ----------------------------------------------------------------------
    # header must be same length as data
    if len(data) != len(header):
        eargs = [filename, len(data), len(header), func_name]
        WLOG(params, 'error', TextEntry('00-013-00004', args=eargs))
    # datatype must be same length as data
    if len(data) != len(datatype):
        eargs = [filename, len(data), len(datatype), func_name]
        WLOG(params, 'error', TextEntry('00-013-00005', args=eargs))
    # if dtype is not None must be same length as data
    if dtype is not None:
        if len(data) != len(dtype):
            eargs = [filename, len(data), len(dtype), func_name]
            WLOG(params, 'error', TextEntry('00-013-00006', args=eargs))
    # ----------------------------------------------------------------------
    # create the multi HDU list
    #try:
    # try to create primary HDU first
    hdu0 = fits.PrimaryHDU(data[0], header=header[0])
    if dtype is not None:
        hdu0.scale(type=dtype[0], **SCALEARGS)
    # add all others afterwards
    hdus = [hdu0]
    for it in range(1, len(data)):
        if datatype[it] == 'image':
            fitstype = fits.ImageHDU
        elif datatype[it] == 'table':
            fitstype = fits.BinTableHDU
        else:
            continue
        # add to hdu list
        hdu_i = fitstype(data[it], header=header[it])
        if dtype is not None:
            hdu_i.scale(type=dtype[it])
        hdus.append(hdu_i)
    # convert to  HDU list
    hdulist = fits.HDUList(hdus)
    # except Exception as e:
    #     eargs = [type(e), e, func_name]
    #     WLOG(params, 'error', TextEntry('01-001-00004', args=eargs))
    #     hdulist = None
    # ---------------------------------------------------------------------
    # write to file
    with warnings.catch_warnings(record=True) as w:
        try:
            hdulist.writeto(filename, overwrite=True)
        except Exception as e:
            eargs = [os.path.basename(filename), type(e), e, func_name]
            WLOG(params, 'error', TextEntry('01-001-00005', args=eargs))
    # ---------------------------------------------------------------------
    # ignore truncated comment warning since spirou images have some poorly
    #   formatted header cards
    w1 = []
    for warning in w:
        # Note: cannot change language as we are looking for python error
        #       this is in english and shouldn't be changed
        wmsg = 'Card is too long, comment will be truncated.'
        if wmsg != str(warning.message):
            w1.append(warning)
    # add warnings to the warning logger and log if we have them
    drs_log.warninglogger(params, w1)


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


# =============================================================================
# Worker functions
# =============================================================================
def deal_with_bad_header(p, hdu, filename):
    """
    Deal with bad headers by iterating through good hdu's until we hit a
    problem

    :param p: ParamDict, the constants file
    :param hdu: astropy.io.fits HDU
    :param filename: string - the filename for logging

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
        # noinspection PyBroadException
        try:
            datastore.append(hdu[it].data)
            headerstore.append(hdu[it].header)
        except:
            cond = False
        # iterate
        it += 1
    # print message
    if len(datastore) > 0:
        dargs = [it-1, filename]
        WLOG(p, 'warning', TextEntry('10-001-00001', args=dargs))
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        WLOG(p, 'error', TextEntry('01-001-00001', args=[filename]))
    # return valid data
    return datastore, headerstore


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
