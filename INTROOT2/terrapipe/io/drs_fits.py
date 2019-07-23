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
from astropy.time import Time
from astropy import version as av
import os
import warnings
import traceback

from terrapipe.core import constants
from terrapipe.core.core import drs_log
from terrapipe import locale
from . import drs_table

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
# noinspection PyCompatibility
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
            nan_filtered = self.__nan_check(item)
            super().__setitem__(key, nan_filtered)

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
        header = Header(super().copy(strip), copy=False)
        header.__temp_items = self.__temp_items.copy()
        return header

    def to_fits_header(self, strip=True, nan_to_string=True):
        header = super().copy(strip=strip)
        if nan_to_string:
            for key in list(header.keys()):
                header[key] = header[key]
        return header

    @staticmethod
    def from_fits_header(fits_header):
        return Header(fits_header, copy=True)

    @staticmethod
    def __get_temp_key(key):
        return key[3:]

    @staticmethod
    def __nan_check(value):
        if isinstance(value, float) and np.isnan(value):
            return 'NaN'
        elif type(value) == tuple:
            return (Header.__nan_check(value[0]),) + value[1:]
        else:
            return value


# =============================================================================
# Define read functions
# =============================================================================
def read(params, filename, getdata=True, gethdr=False, fmt='fits-image', ext=0,
         func=None):
    """
    The drs fits file read function

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: string, the absolute path to the file
    :param getdata: bool, whether to return data from "ext"
    :param gethdr: bool, whether to return header from "ext"
    :param fmt: str, format of data (either 'fits-image' or 'fits-table'
    :param ext: int, the extension to open
    :param func: str, function name of calling function (input function)

    :type params: ParamDict
    :type filename: str
    :type getdata: bool
    :type gethdr: bool
    :type fmt: str
    :type ext: int
    :type func: str

    :returns: if getdata and gethdr: returns data, header, if getdata return
              data, if gethdr returns header.
              if fmt 'fits-time' returns np.array for data and dictionary for
              header, if fmt 'fits-table' returns astropy.table for data and
              dictionary for header
    """
    if func is None:
        func_name = __NAME__ + '.read()'
    else:
        func_name = '{0} and {1}'.format(func, __NAME__ + '.read()')
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
        dataarr, headerarr = [], []
        for it in range(n_ext):
            # append header
            try:
                headerarr.append(hdulist[it].header)
            except Exception as e:
                eargs = [os.path.basename(filename), it, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('01-001-00008', args=eargs))
            # append data
            try:
                if isinstance(hdulist[it].data, fits.BinTableHDU):
                    dataarr.append(Table.read(hdulist[it].data))
                else:
                    dataarr.append(hdulist[it].data)
            except Exception as e:
                eargs = [os.path.basename(filename), it, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('01-001-00007', args=eargs))
        data = list(dataarr)
        header = list(headerarr)
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
        header = [header.to_fits_header()]
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
    # try to create primary HDU first
    if isinstance(header[0], Header):
        header0 = header[0].to_fits_header()
    else:
        header0 = header[0]
    # set up primary HDU (if data[0] == image then put this in the primary)
    #   else if table then primary HDU should be empty
    if datatype[0] == 'image':
        hdu0 = fits.PrimaryHDU(data[0], header=header0)
        start = 1
    else:
        hdu0 = fits.PrimaryHDU()
        start = 0

    if dtype is not None:
        hdu0.scale(type=dtype[0], **SCALEARGS)
    # add all others afterwards
    hdus = [hdu0]
    for it in range(start, len(data)):
        if datatype[it] == 'image':
            fitstype = fits.ImageHDU
        elif datatype[it] == 'table':
            fitstype = fits.BinTableHDU
        else:
            continue
        # add to hdu list
        if isinstance(header[it], Header):
            header_it = header[it].to_fits_header()
        else:
            header_it = header[it]
        hdu_i = fitstype(data[it], header=header_it)
        if dtype is not None and datatype[it] == 'image':
            if dtype[it] is not None:
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
# Define search functions
# =============================================================================
def find_filetypes(params, filetype, allowedtypes=None, path=None):
    """
    Find all files in "path" with DPRTYPE = "filetype"

    must be in "allowedtypes" if None
    if path is "None" params['INPATH'] is used

    :param params: ParamDict, the parameter dictionary of constants
    :param filetype: str, the value of DPRTYPE files must have
    :param allowedtypes: list of strings, the allowed "filetypes" (filetypes
                         can be a user input so must be checked for valid
                         filetype) by default is undefined (thus all "filetypes"
                         will be valid)
    :param path: str, the path to check for filetypes (must have index files
                 in this path or sub directories of this path)
                 if path is "None" params['INPATH'] is used

    :type params: ParamDict
    :type filetype: str
    :type allowedtypes: list[str]
    :type path: str

    :return:
    """
    func_name = __NAME__ + '.find_filetypes()'
    # deal with no path set
    if path is None:
        path = params['INPATH']
    # deal with no allowed types
    if allowedtypes is None:
        allowedtypes = [filetype]
    elif isinstance(allowedtypes, str):
        # split at commas
        allowedtypes = allowedtypes.split(',')
        # strip spaces
        allowedtypes = list(map(lambda x: x.strip(), allowedtypes))
    else:
        allowedtypes = list(allowedtypes)
    # ----------------------------------------------------------------------
    # check file type is allowed
    if filetype not in allowedtypes:
        emsg = TextEntry('01-001-00020', args=[filetype, func_name])
        for allowedtype in allowedtypes:
            emsg += '\n\t - "{0}"'.format(allowedtype)
        WLOG(params, 'error', emsg)
    # ----------------------------------------------------------------------
    # get index files
    index_files = get_index_files(params, path)
    # ----------------------------------------------------------------------
    # valid files dictionary (key = telluric object name)
    valid_files = []
    # ----------------------------------------------------------------------
    # ---------------------------------------------------------------------
    # loop through index files
    for index_file in index_files:
        # read index file
        index = drs_table.read_fits_table(params, index_file)
        # get directory
        dirname = os.path.dirname(index_file)
        # -----------------------------------------------------------------
        # get filename and object name
        index_filenames = index['FILENAME']
        index_output = index[params['KW_DPRTYPE'][0]]
        # -----------------------------------------------------------------
        # mask by KW_OUTPUT
        mask = index_output == filetype
        # -----------------------------------------------------------------
        # append found files to this list
        if np.nansum(mask) > 0:
            for filename in index_filenames[mask]:
                # construct absolute path
                absfilename = os.path.join(dirname, filename)
                # check that file exists
                if not os.path.exists(absfilename):
                    continue
                # append to storage
                if absfilename not in valid_files:
                    valid_files.append(absfilename)
    # ---------------------------------------------------------------------
    # log found
    wargs = [len(valid_files), filetype]
    WLOG(params, '', TextEntry('40-004-00004', args=wargs))
    # return full list
    return valid_files


def get_index_files(params, path=None):
    """
    Get index files in path (or sub-directory of path)
        if path is "None" params['INPATH'] is used

    :param params: ParamDict, the parameter dictionary of constants
    :param path: str, the path to check for filetypes (must have index files
                 in this path or sub directories of this path)
                 if path is "None" params['INPATH'] is used

    :type params: ParamDict
    :type path: str

    :return: the absolute paths to all index files under path
    :rtype: list[str]
    """
    func_name = __NAME__ + '.get_index_files()'
    # deal with no path set
    if path is None:
        path = params['INPATH']
    # storage of index files
    index_files = []
    # walk through path and find index files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == params['DRS_INDEX_FILE']:
                index_files.append(os.path.join(root, filename))
    # log number of index files found
    if len(index_files) > 0:
        WLOG(params, '', TextEntry('40-004-00003', args=[len(index_files)]))
    else:
        eargs = [path, func_name]
        WLOG(params, 'error', TextEntry('01-001-00021', args=eargs))
    # return the index files
    return index_files


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
    # update the number of files
    outfile.numfiles = len(infiles)
    # return combined infile
    return outfile


def header_start_time(params, hdr, out_fmt='mjd', func=None, name=None):
    """
    Get acquisition time from header

    :param params:
    :param hdr:
    :param out_fmt:
    :param func: str, input function name
    :param name:

    :type params: ParamDict
    :type hdr: Header
    :type out_fmt: str

    :return:
    """
    if func is None:
        func_name = __NAME__ + '.header_time()'
    else:
        func_name = func
    # deal with no name
    if name is None:
        dbname = 'header_time'
    else:
        dbname = name
        # ----------------------------------------------------------------------
    # get acqtime
    time_key = drs_log.find_param(params, 'KW_ACQTIME', func=func_name)[0]
    timefmt = drs_log.find_param(params, 'KW_ACQTIME_FMT', func=func_name)
    timetype = drs_log.find_param(params, 'KW_ACQTIME_DTYPE', func=func_name)
    # ----------------------------------------------------------------------
    # get values from header
    if time_key in hdr:
        rawtime = hdr[time_key]
    else:
        eargs = [dbname, 'hdict', time_key, func_name]
        WLOG(params, 'error', TextEntry('00-001-00028', args=eargs))
        rawtime = None
    # ----------------------------------------------------------------------
    # get astropy time
    try:
        acqtime = Time(timetype(rawtime), format=timefmt)
    except Exception as e:
        eargs = [dbname, rawtime, timefmt, timetype, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-001-00029', args=eargs))
        acqtime = None
    # ----------------------------------------------------------------------
    # return time in requested format
    if out_fmt is None:
        return acqtime
    elif out_fmt == 'mjd':
        return float(acqtime.mjd)
    elif out_fmt == 'jd':
        return float(acqtime.jd)
    elif out_fmt == 'iso' or out_fmt == 'human':
        return acqtime.iso
    elif out_fmt == 'unix':
        return float(acqtime.unix)
    elif out_fmt == 'decimalyear':
        return float(acqtime.decimalyear)
    else:
        kinds = ['None', 'human', 'iso', 'unix', 'mjd', 'jd', 'decimalyear']
        eargs = [dbname, ' or '.join(kinds), out_fmt, func_name]
        WLOG(params, 'error', TextEntry('00-001-00030', args=eargs))


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
        except Exception as _:
            cond = False
        # iterate
        it += 1
    # print message
    if len(datastore) > 0:
        dargs = [it - 1, filename]
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


def check_dtype_for_header(value):
    # if value is a string check if it is a path if it is remove path
    #   and leave base file
    if isinstance(value, str):
        if os.path.isfile(value):
            newvalue = os.path.basename(value)
        elif os.path.isdir(value):
            newvalue = os.path.dirname(value)
        else:
            newvalue = str(value)
    # if value is a bool then we need to true it to a int (1 or 0)
    elif isinstance(value, bool):
        if value:
            newvalue = 1
        else:
            newvalue = 0
    # if value is a float need to check for NaN
    elif isinstance(value, float):
        if np.isnan(value):
            newvalue = 'NaN'
        else:
            newvalue = float(value)
    # if value is a int do nothing
    elif isinstance(value, int):
        newvalue = int(value)
    # else convert to string to be safe
    else:
        newvalue = str(value)
    # return new value
    return newvalue


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
