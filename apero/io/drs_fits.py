#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 11:36

@author: cook

Import rules:
    only from core.core.drs_log, core.io, core.math, core.constants,
    apero.lang, apero.base

    do not import from core.core.drs_file
    do not import from core.core.drs_argument
    do not import from core.io.drs_image
    do not import from core.core.drs_database
"""
import numpy as np
from astropy.io import fits
from astropy.io.fits.verify import VerifyWarning
from astropy.table import Table
from copy import deepcopy
import os
from pathlib import Path
import warnings
import time
import traceback
from typing import Any, List, Tuple, Union

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero import lang

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_fits.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Astropy Time and Time Delta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# set scale args for astropy >3.0
SCALEARGS = dict(bscale=1, bzero=0)
# Define any simple type for typing
AnySimple = Union[int, float, str, bool]
# get header comment cards
HeaderCommentCards = fits.header._HeaderCommentaryCards
# filter verify warnings
warnings.filterwarnings('ignore', category=VerifyWarning)


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
        """
        Construct the Apero Fits Header

        :param args: passed to super astropy.io.fits.Header
        :param kwargs: passed to super astropy.io.fits.Header
        """
        # save class name
        self.classname = 'Header'
        # set function
        _ = display_func('__init__', __NAME__, self.classname)
        # construct astropy.io.fits.Header class
        super().__init__(*args, **kwargs)
        # set storage for temporary items
        self.__temp_items = {}

    def __setitem__(self, key: str,
                    item: Union[AnySimple, Tuple[AnySimple, str]]):
        """
        Set a key with "item"
        same as using: header[key] = item

        :param key: str, the key to add to the header
        :param item: object, the object to
        :return: None
        """
        # set function
        _ = display_func('__setitem__', __NAME__, self.classname)
        # deal with key not being string
        if isinstance(key, tuple):
            # assume it is a tuple (key, id) - therefore we check key[0]
            if key[0].startswith('@@@'):
                tmpkey = self.__get_temp_key(key[0])
                self.__temp_items.__setitem__(tmpkey, item)
            else:
                # check for NaN values (and convert -- cannot put directly in)
                nan_filtered = self.__nan_check(item)
                # deal with long keys
                if len(key[0]) > 8 and not key[0].startswith('HIERARCH'):
                    dkey = 'HIERARCH ' + key[0]
                else:
                    dkey = str(key[0])
                # do the super __setitem__ on nan filtered item
                super().__setitem__(dkey, nan_filtered)
        # if key starts with @@@ add to temp items (without @@@)
        elif key.startswith('@@@') or key.startswith('HIERARCH @@@'):
            # use the __get_temp_key method to strip key
            self.__temp_items.__setitem__(self.__get_temp_key(key), item)
        # do not add empty keys
        elif key == '':
            pass
        # else add normal keys
        else:
            # deal with long keys
            if len(key) > 8 and not key.startswith('HIERARCH'):
                dkey = 'HIERARCH ' + key
            else:
                dkey = str(key)
            # check for NaN values (and convert -- cannot put directly in)
            nan_filtered = self.__nan_check(item)
            # do the super __setitem__ on nan filtered item
            super().__setitem__(dkey, nan_filtered)

    def __getitem__(self, key: str) -> Union[AnySimple, dict]:
        """
        Get an "item" with key
        same as using: item = header[key]

        :param key: str, the key in the header to get item for
        :return: the item in the header with key="key"
        """
        # set function
        _ = display_func('__getitem__', __NAME__, self.classname)
        # deal with key not being string
        if isinstance(key, tuple):
            # assume it is a tuple (key, id) - therefore we check key[0]
            if key[0].startswith('@@@'):
                tmpkey = self.__get_temp_key(key[0])
                value = self.__temp_items.__getitem__(tmpkey)
                return self.__nan_check(value, dtype=float)
            else:
                value = super().__getitem__(key)
                return self.__nan_check(value, dtype=float)
        elif not isinstance(key, str):
            value = super().__getitem__(key)
            return self.__nan_check(value, dtype=float)
        # if key starts with @@@ get it from the temporary items storage
        if key.startswith('@@@'):
            value = self.__temp_items.__getitem__(self.__get_temp_key(key))
            return self.__nan_check(value, dtype=float)
        # else get it from the normal storage location (in super)
        else:
            value = super().__getitem__(key)
            return self.__nan_check(value, dtype=float)

    def get(self, key, default=None):
        value = super().get(key, default)
        return self.__nan_check(value, dtype=float)

    def get_key(self, params: ParamDict, key: str, default=None) -> Any:
        # deal with key in params
        if key in params:
            drs_key, _, drs_comment = params[key]
        else:
            drs_key = str(key)
        return self.get(drs_key, default=default)

    def __contains__(self, key: str) -> bool:
        """
        Whether key is in header
        same as using: key in header

        :param key: str, the key to search for in the header
        :return:
        """
        # set function
        _ = display_func('__contains__', __NAME__, self.classname)
        # deal with key not being str
        if isinstance(key, tuple):
            if key[0].startswith('@@@'):
                tmpkey = self.__get_temp_key(key[0])
                return self.__temp_items.__contains__(tmpkey)
            else:
                return super().__contains__(key)
        elif not isinstance(key, str):
            return super().__contains__(key)
        # if key starts with @@@ then get it from the temp_items
        if key.startswith('@@@'):
            return self.__temp_items.__contains__(self.__get_temp_key(key))
        # else just do the super contains
        else:
            return super().__contains__(key)

    def set_key(self, params: ParamDict, key: str, value: Any):
        """
        Set a key (maybe from params with a keywordstore)

        :param params: ParamDict, parameter dictionary of constants
        :param key: str, either key or key in params for keywordsotre
        :param value: Any, the value to put into the header

        :return: None - sets the key or params[key][0]
        """
        # deal with key in params
        if key in params:
            drs_key, _, drs_comment = params[key]
            drs_value = (value, drs_comment)
        else:
            drs_key = str(key)
            drs_value = value
        # set item as normal
        self.__setitem__(drs_key, drs_value)

    def copy(self, strip: bool = False) -> 'Header':
        """
        Copy an entire header (including temp items)

        :param strip: If `True`, strip any headers that are specific to one
                      of the standard HDU types, so that this header can be
                      used in a different HDU.

        :return: copy of the header
        """
        # set function
        _ = display_func('copy', __NAME__, self.classname)
        # copy header via super
        header = Header(super().copy(strip), copy=False)
        # copy temp items
        header.__temp_items = self.__temp_items.copy()
        return header

    def to_fits_header(self, strip: bool = True,
                       nan_to_string: bool = True) -> fits.Header:
        """
        Cast Header in to astropy.io.fits.Header (including the NaN to
        string and no temp items)

        :param strip: If `True`, strip any headers that are specific to one
                      of the standard HDU types, so that this header can be
                      used in a different HDU.

        :param nan_to_string: bool, whether to convert NaNs to strings (for
                              saving to HDU)
        :return: copy of the header
        """
        # set function
        _ = display_func('to_fits_header', __NAME__, self.classname)
        # copy header via super
        header = super().copy(strip=strip)
        # if nan to string is True set all header keys (note the __setitem__
        #   converts NaNs to strings)
        if nan_to_string:
            for key in list(header.keys()):
                # need to deal with comment keys
                #    Cannot do header['COMMENT'] = header['COMMENT']
                if isinstance(header[key], HeaderCommentCards):
                    header[key] = header[key][0]
                else:
                    header[key] = header[key]
        # return fits header
        return header

    @staticmethod
    def from_fits_header(fits_header: fits.Header) -> 'Header':
        """
        Get the Header instance from a fits.Header instance (copy all keys)

        :param fits_header: astropy.io.fits Header
        :return:
        """
        # set function
        _ = display_func('from_fits_header', __NAME__)
        # construct new Header instance
        return Header(fits_header, copy=True)

    @staticmethod
    def __get_temp_key(key: str, chars: str = '@@@') -> Any:
        """
        Remove first three characters ('chars') from a key if they are there
        else return the key unchanged

        :param key: the key to change
        :param chars: the characters to remove
        :return:
        """
        # set function
        _ = display_func('from_fits_header', __NAME__)
        # look for temp key prefix
        if key.startswith(chars):
            return key[len(chars):]
        else:
            return key

    @staticmethod
    def __nan_check(value, dtype=None) -> Any:
        """
        Check for NaNs/Infs in value (cannot be used in astropy.io.header)

        :param value: Any, check for NaNs/INFs

        :return: if NaN or INF found replaces with string, else just returns
                 the original value
        """
        if isinstance(value, str):
            if value.upper() == 'NAN' and dtype == float:
                return np.nan
            if value.upper() == 'INF' and dtype == float:
                return np.inf
            if value.upper() == '-INF' and dtype == float:
                return -np.inf
        # if we expect a float don't continue (used for get not set)
        if dtype == float:
            return value
        # check for NaNs
        if isinstance(value, float) and np.isnan(value):
            return 'NaN'
        # check for positive infinity
        elif isinstance(value, float) and np.isposinf(value):
            return 'INF'
        # check for negative infinity
        elif isinstance(value, float) and np.isneginf(value):
            return '-INF'
        # check and deal with tuple
        elif type(value) == tuple:
            return (Header.__nan_check(value[0]),) + value[1:]
        # else return original value
        else:
            return value


# =============================================================================
# Define read functions
# =============================================================================
# define complex typing for readfits
DataHdrType = Union[Tuple[np.ndarray, fits.Header], np.ndarray, None,
                    Tuple[np.ndarray, fits.Header, str], Tuple[np.ndarray, str],
                    Tuple[List[Union[np.ndarray, Table]], List[fits.Header]],
                    Tuple[List[Union[np.ndarray, Table]], List[fits.Header],
                          List[str]]]


def readfits(params: ParamDict, filename: Union[str, Path],
             getdata: bool = True, gethdr: bool = False,
             fmt: str = 'fits-image',
             ext: Union[int, None] = None,
             extname: Union[str, None] = None,
             func: Union[str, None] = None,
             log: bool = True, copy: bool = False,
             return_names: bool = False
             ) -> Union[DataHdrType, np.ndarray, fits.Header, None]:
    """
    The drs fits file read function

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: string, the absolute path to the file
    :param getdata: bool, whether to return data from "ext"
    :param gethdr: bool, whether to return header from "ext"
    :param fmt: str, format of data (either 'fits-image' or 'fits-table'
    :param ext: int or None, if set tries to read this extension (via position)
    :param extname: str or None, if set tires to read this extension (via name)
    :param func: str, function name of calling function (input function)
    :param log: bool, if True logs that we read file
    :param copy: bool, if True copies the HDU[i].data and/or HDU[i].header so
                 HDU can be closed properly
    :param return_names: bool, if True returns extension names

    :returns: if getdata and gethdr: returns data, header, if getdata return
              data, if gethdr returns header.
              if fmt 'fits-time' returns np.array for data and dictionary for
              header, if fmt 'fits-table' returns astropy.table for data and
              dictionary for header
    """
    # set function
    func_name = display_func('readfits', __NAME__)
    if func is not None:
        func_name = '{0} and {1}'.format(func, func_name)
    # define allowed values of 'fmt'
    allowed_formats = ['fits-image', 'fits-table', 'fits-multi']
    # -------------------------------------------------------------------------
    # deal with filename not existing
    if not os.path.exists(filename):
        # check directory exists
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            eargs = [dirname, os.path.basename(filename), func_name]
            WLOG(params, 'error', textentry('01-001-00013', args=eargs))
        else:
            eargs = [os.path.basename(filename), dirname, func_name]
            WLOG(params, 'error', textentry('01-001-00012', args=eargs))
    # -------------------------------------------------------------------------
    # deal with obtaining data
    if fmt == 'fits-image':
        data, header = _read_fitsimage(params, filename, getdata, gethdr, ext,
                                       extname, log=log)
        name = None
        # deal with copying
        if copy:
            if getdata:
                data = np.array(data)
            if gethdr:
                header = fits.Header(header)
    elif fmt == 'fits-table':
        data, header = _read_fitstable(params, filename, getdata, gethdr, ext,
                                       extname, log=log)
        name = None
        # deal with copying
        if copy:
            if getdata:
                data = Table(data)
            if gethdr:
                header = fits.Header(header)
    elif fmt == 'fits-multi':
        mout = _read_fitsmulti(params, filename, getdata, gethdr, log=log)
        if getdata and gethdr:
            data, header, name = mout
        elif getdata:
            data, name = mout
            header = None
        else:
            data = None
            header, name = mout
        # deal with copying
        if copy:
            data = deepcopy(data)
            header = deepcopy(header)
    else:
        cfmts = ', '.join(allowed_formats)
        eargs = [filename, fmt, cfmts, func_name]
        WLOG(params, 'error', textentry('00-008-00019', args=eargs))
        return None
    # -------------------------------------------------------------------------
    # deal with return
    if return_names:
        if getdata and gethdr:
            return data, header, name
        elif getdata:
            return data, name
        elif gethdr:
            return header, name
        else:
            return None
    else:
        if getdata and gethdr:
            return data, header
        elif getdata:
            return data
        elif gethdr:
            return header
        else:
            return None


def read_header(params: ParamDict, filename: str, ext: Union[int, None] = None,
                log: bool = True) -> fits.Header:
    """
    Read the header from a fits file located at 'filename' with extension
    'ext' (defaults to 0)

    :param params: ParamDict, parameter dictionary of constants
    :param filename: str, the filename to read the fits hdu from
    :param ext: int, the hdu extension to read the header from (defaults to
                first extension)
    :param log: bool, if True logs on error, else raises astropy.io.fits
                exception that generated the error

    :return: astropy.io.fits.Header instance - the header read from 'filename'
    """
    # set function name
    func_name = display_func('read_header', __NAME__)
    # try to open header
    try:
        header = fits.getheader(filename, ext=ext)
    except Exception as e:
        if log:
            eargs = [os.path.basename(filename), ext, type(e), e, func_name]
            WLOG(params, 'error', textentry('01-001-00010', args=eargs))
            header = None
        else:
            raise e
    # return header
    return header


# define complex typing for _read_fitsmulti
DataHdrListType = Union[Tuple[List[np.ndarray], List[fits.Header], List[str]],
                        Tuple[List[np.ndarray], List[str]],
                        Tuple[List[fits.Header], List[str]]]


def _read_fitsmulti(params: ParamDict, filename: str, getdata: bool,
                    gethdr: bool, log: bool = True) -> DataHdrListType:
    """
    Read all extensions from a multi-extension fits file 'filename'
    returns data if getdata is True, returns header if gethdr is True

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename to read the fits hdu from
    :param getdata: bool, if True read the data from all extensions
    :param gethdr: bool, if True read the headers from all extensions
    :param log: bool, if True logs on error, else raises astropy.io.fits
                exception that generated the error

    :return: list of data if getdata True and/or list of headers if gethdr True
    """
    # set function name
    func_name = display_func('_read_fitsmulti', __NAME__)
    # attempt to open hdu of fits file
    try:
        hdulist = fits.open(filename)
    except Exception as e:
        eargs = [filename, type(e), e, func_name]
        WLOG(params, 'error', textentry('01-001-00006', args=eargs))
        hdulist = None
    # -------------------------------------------------------------------------
    # get the number of fits files in filename
    try:
        n_ext = len(hdulist)
    except Exception as e:
        WLOG(params, 'warning', textentry('10-001-00005', args=[type(e), e]),
             sublevel=2)
        n_ext = None
    # deal with unknown number of extensions
    if n_ext is None:
        bout = deal_with_bad_header(params, hdulist, filename)
        dataarr, headerarr, names = bout
    # -------------------------------------------------------------------------
    # else get the data and header based on how many extnesions there are
    else:
        dataarr, headerarr, names = [], [], []
        for it in range(n_ext):
            # get name
            if hdulist[it].name is not None:
                names.append(str(hdulist[it].name))
            else:
                names.append('Unknown')
            # get xtension type
            if hdulist[it].header is not None:
                xtension = hdulist[it].header.get('XTENSION', None)
            else:
                xtension = None
            # append header
            try:
                headerarr.append(hdulist[it].header)
            except Exception as e:
                if log:
                    eargs = [os.path.basename(filename), it, type(e), e,
                             func_name]
                    WLOG(params, 'error', textentry('01-001-00008', args=eargs))
                else:
                    raise e
            # append data
            try:
                if isinstance(hdulist[it].data, fits.BinTableHDU):
                    dataarr.append(Table(hdulist[it].data))
                elif xtension is not None and xtension == 'BINTABLE':
                    dataarr.append(Table(hdulist[it].data))
                else:
                    dataarr.append(hdulist[it].data)
            except Exception as e:
                if log:
                    eargs = [os.path.basename(filename), it, type(e), e,
                             func_name]
                    WLOG(params, 'error', textentry('01-001-00007', args=eargs))
                else:
                    raise e
    # -------------------------------------------------------------------------
    # return data and/or header
    if getdata and gethdr:
        return dataarr, headerarr, names
    elif getdata:
        return dataarr, names
    else:
        return headerarr, names


# define complex typing for _read_fitsimage
ImageFitsType = Tuple[Union[np.ndarray, None], Union[fits.Header, None]]


def _read_fitsimage(params: ParamDict, filename: str, getdata: bool,
                    gethdr: bool, ext: Union[int, None] = None,
                    extname: Union[str, None] = None,
                    log: bool = True) -> ImageFitsType:
    """
    Read a fits image in extension 'ext' for fits file 'filename'
    returns data if getdata is True, returns header if gethdr is True

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename to read the fits hdu from
    :param getdata: bool, if True read the data from extension 'ext'
    :param gethdr: bool, if True read the headers from extension 'ext'
    :param ext: int or None, if set tries to read this extension (via position)
    :param extname: str or None, if set tires to read this extension (via name)
    :param log: bool, if True logs on error, else raises astropy.io.fits
                exception that generated the error

    :return: data if getdata True and/or headers if gethdr True
    """
    # set function name
    _ = display_func('_read_fitsimage', __NAME__)
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            # deal with ext being set
            if ext is not None:
                # open fits file
                with fits.open(filename) as hdulist:
                    if len(hdulist)-1 < ext:
                        # TODO: move to language database
                        emsg = ('File {0} does not have extension {1} '
                                '\n\t File may be corrupted or wrong type')
                        eargs = [filename, ext]
                        WLOG(params, 'error', emsg.format(*eargs))
                    data = np.array(hdulist[ext].data)
            # deal with extname being set
            elif extname is not None:
                # open fits file
                with fits.open(filename) as hdulist:
                    if extname not in hdulist:
                        # TODO: move to language database
                        emsg = ('File {0} does not have extension name {1} '
                                '\n\t File may be corrupted or wrong type')
                        eargs = [filename, extname]
                        WLOG(params, 'error', emsg.format(*eargs))
                    data = np.array(hdulist[extname].data)
            # just load first valid extension
            else:
                data = fits.getdata(filename)
        except Exception as _:
            try:
                # try to deal with corrupted data extensions
                data = deal_with_bad_file_single(filename, ext=ext,
                                                 extname=extname,
                                                 flavour='data')
            except Exception as e:
                if log:
                    if ext is not None:
                        extstr = 'ext = {0}'.format(ext)
                    elif extname is not None:
                        extstr = 'extname = {0}'.format(extname)
                    else:
                        extstr = ''
                    # if we get to this point we cannot open the required
                    #   extension
                    string_trackback = traceback.format_exc()
                    eargs = [filename, extstr, type(e)]
                    emsg = textentry('01-001-00014', args=eargs)
                    emsg += '\n\n' + textentry(string_trackback)
                    WLOG(params, 'error', emsg)
                    data = None
                else:
                    raise e
    else:
        data = None
    # -------------------------------------------------------------------------
    # deal with getting header
    if gethdr:
        try:
            # deal with ext being set
            if ext is not None:
                # open fits file
                with fits.open(filename) as hdulist:
                    if len(hdulist) - 1 < ext:
                        # TODO: move to language database
                        emsg = ('File {0} does not have extension {1} '
                                '\n\t File may be corrupted or wrong type')
                        eargs = [filename, ext]
                        WLOG(params, 'error', emsg.format(*eargs))
                    header = Header(hdulist[ext].header)
            # deal with extname being set
            elif extname is not None:
                # open fits file
                with fits.open(filename) as hdulist:
                    if extname not in hdulist:
                        # TODO: move to language database
                        emsg = ('File {0} does not have extension name {1} '
                                '\n\t File may be corrupted or wrong type')
                        eargs = [filename, extname]
                        WLOG(params, 'error', emsg.format(*eargs))
                    header = Header(hdulist[extname].header)
            # just load first valid extension
            else:
                header = fits.getdata(filename)
        except Exception as _:
            try:
                # try to deal with corrupted data extensions
                header = deal_with_bad_file_single(filename, ext=ext,
                                                   extname=extname,
                                                   flavour='header')
            except Exception as e:
                if log:
                    if ext is not None:
                        extstr = 'ext = {0}'.format(ext)
                    elif extname is not None:
                        extstr = 'extname = {0}'.format(extname)
                    else:
                        extstr = ''
                    string_trackback = traceback.format_exc()
                    eargs = [filename, extstr, type(e)]
                    emsg = textentry('01-001-00015', args=eargs)
                    emsg += '\n\n' + textentry(string_trackback)
                    WLOG(params, 'error', emsg)
                    header = None
                else:
                    raise e
    else:
        header = None
    # -------------------------------------------------------------------------
    # return data and header
    return data, header


# define complex typing for _read_fitsimage
TableFitsType = Tuple[Union[Table, None], Union[fits.Header, None]]


def _read_fitstable(params: ParamDict, filename: str, getdata: bool,
                    gethdr: bool, ext: Union[int, None] = None,
                    extname: Union[str, None] = None,
                    log: bool = True) -> TableFitsType:
    """
    Read a fits bin table in extension 'ext' for fits file 'filename'
    returns table if getdata is True, returns header if gethdr is True

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename to read the fits hdu from
    :param getdata: bool, if True read the table from extension 'ext'
    :param gethdr: bool, if True read the headers from extension 'ext'
    :param ext: int or None, if set tries to read this extension (via position)
    :param extname: str or None, if set tires to read this extension (via name)
    :param log: bool, if True logs on error, else raises astropy.io.fits
                exception that generated the error

    :return: table if getdata True and/or headers if gethdr True
    """
    # set function name
    _ = display_func('_read_fitstable', __NAME__)
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            with warnings.catch_warnings(record=True) as _:
                if ext is not None:
                    data = Table.read(filename, format='fits', hdu=ext)
                elif extname is not None:
                    data = Table.read(filename, format='fits', hdu=extname)
                else:
                    data = Table.read(filename, format='fits')
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = textentry('01-001-00016', args=[filename, ext, type(e)])
                emsg += '\n\n' + textentry(string_trackback)
                WLOG(params, 'error', emsg)
                data = None
            else:
                raise e
    else:
        data = None
    # -------------------------------------------------------------------------
    # deal with getting header
    if gethdr:
        try:
            header = fits.getheader(filename, ext=ext)
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = textentry('01-001-00017', args=[filename, ext, type(e)])
                emsg += '\n\n' + textentry(string_trackback)
                WLOG(params, 'error', emsg)
                header = None
            else:
                raise e
    else:
        header = None
    # -------------------------------------------------------------------------
    # return data and header
    return data, header


def find_named_extensions(filename: str, name: Union[str, None] = None,
                          startswith: Union[str, None] = None) -> List[int]:
    """
    Find named extensions (either matching "name" or starting with "startswith")
    returns a list of matched extensions (integers)

    :param filename: str, the filename to try and open
    :param name: str or None, if set EXTNAME much match this for extension to
                 be returned
    :param startswith: str or None, if set and name not set EXTNAME must start
                       with this for extension to be returned

    :return: a list of matched extensions (integers)
    """
    # valid extensions
    valid_ext = []
    # open file
    with fits.open(filename) as hdulist:
        # loop around extensions
        for it in range(len(hdulist)):
            # deal with None and non string names
            if not isinstance(hdulist[it].name, str):
                continue
            # deal with full name being set
            if name is not None:
                if hdulist[it].name == name:
                    valid_ext.append(it)
            # deal with starts with being set
            elif startswith is not None:
                if hdulist[it].name.startswith(startswith):
                    valid_ext.append(it)
    # return valid extensions
    return valid_ext


# =============================================================================
# Define write functions
# =============================================================================
# define complex typing for writing
ListImageTable = List[Union[np.ndarray, Table, None]]
ListHeader = List[Union[Header, fits.Header, None]]


def writefits(params: ParamDict, filename: str, data: ListImageTable,
              header: ListHeader, names: List[Union[str, None]],
              datatype: List[str],
              dtype: List[Union[str, None]], func: Union[str, None] = None):
    """
    Write a fits file (wrapper around locked function _write_fits) either
    with single extension (data/header/datatype/dtype) are not lists,
    or multiple extensions (data/header/datatype/dtype) are lists.

    if data/header/datatype/dtype are lists all others must be lists of the
    same legnth

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename and location to save fits file to
    :param data: list of np.array/Table or just a np.array/Table - this is the
                 data to be written the the fits HDU (HDU[i].data)
    :param header: list of Header/fits.Header instances or just a
                   Header/fits.Header instance - this is the header to be
                   written to the fits HDU (HDU[i].header)
    :param names: str or list of strings, the names of each extension

    :param datatype: str or list of strings, the data type for each extension
                     - must be either 'image' (for a ImageHDU) or 'table'
                     (for a BinTableHDU)
    :param dtype: str or list of strings, the destination data type, use a
                  string representing a numpy dtype name, (e.g. ``'uint8'``,
                  ``'int16'``, ``'float32'`` etc.).
    :param func: str or None, the function calling the writefits function (for
                 logging purposes)

    :return: None - writes Fits HDU to 'filename'
    """
    # set function name
    _ = display_func('writefits', __NAME__)
    # ------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    # lockfile = os.path.basename(filename)
    # # start a lock
    # lock = drs_lock.Lock(params, lockfile)

    # ------------------------------------------------------------------
    # make locked read function
    # @drs_lock.synchronized(lock, params['PID'])
    # def locked_write():
    #     return _write_fits(params, filename, data, header, datatype, dtype,
    #                        func)
    return _write_fits(params, filename, data, header, names, datatype, dtype,
                       func)
    # ------------------------------------------------------------------
    # try to run locked read function
    # try:
    #     locked_write()
    # except KeyboardInterrupt as e:
    #     lock.reset()
    #     raise e
    # except Exception as e:
    #     # reset lock
    #     lock.reset()
    #     raise e


def _write_fits(params: ParamDict, filename: str, data: ListImageTable,
                header: ListHeader, names: List[Union[str, None]],
                datatype: List[Union[str, None]], dtype: List[Union[str, None]],
                func: Union[str, None] = None):
    """
    Internal write fits file function (should use writefits externally)
    write fits file with single extension (data/header/datatype/dtype)
    are not lists, or multiple extensions (data/header/datatype/dtype)
    are lists.

    if data/header/datatype/dtype are lists all others must be lists of the
    same length

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename and location to save fits file to
    :param data: list of np.array/Table or just a np.array/Table - this is the
                 data to be written the the fits HDU (HDU[i].data)
    :param header: list of Header/fits.Header instances or just a
                   Header/fits.Header instance - this is the header to be
                   written to the fits HDU (HDU[i].header)
    :param datatype: str or list of strings, the data type for each extension
                     - must be either 'image' (for a ImageHDU) or 'table'
                     (for a BinTableHDU)
    :param dtype: str or list of strings, the destination data type, use a
                  string representing a numpy dtype name, (e.g. ``'uint8'``,
                  ``'int16'``, ``'float32'`` etc.).
    :param func: str or None, the function calling the writefits function (for
                 logging purposes)

    :return: None - writes Fits HDU to 'filename'
    """
    # set function name
    func_name = display_func('_write_fits', __NAME__)
    # deal with function name coming from somewhere else
    if func is not None:
        func_name = '{0} (via {1})'.format(func, func_name)
    # ----------------------------------------------------------------------
    # check if file exists and remove it if it does
    # done in a while loop
    tries, success, store_error = 0, False, None
    while tries <= 5:
        # test if file exists
        if os.path.exists(filename):
            # if it does try to remove it
            try:
                # remove file
                os.remove(filename)
                # success is True we don't need to report an error
                success = True
                # break out of while loop
                break
            # removing file may fail if removed by another process (very rare)
            # so sleep for 0.1 s and then try to see if the file exists again
            except Exception as e:
                # add to tries (we don't want to try too many times)
                tries += 1
                # sleep zzz
                time.sleep(0.1)
                # store the error for eventual reporting (if fails more than
                #   5 times)
                store_error = (type(e), str(e))
        # if file does not exist we can break out of loop
        else:
            # success is True we don't need to report an error
            success = True
            # break out of while loop
            break
    # deal with not being able to remove file
    if not success:
        eargs = [os.path.basename(filename), store_error[0], store_error[1],
                 func_name]
        WLOG(params, 'error', textentry('01-001-00003', args=eargs))
    # ----------------------------------------------------------------------
    # header must be same length as data
    if len(data) != len(header):
        eargs = [filename, len(data), len(header), func_name]
        WLOG(params, 'error', textentry('00-013-00004', args=eargs))
    # datatype must be same length as data
    if len(data) != len(datatype):
        eargs = [filename, len(data), len(datatype), func_name]
        WLOG(params, 'error', textentry('00-013-00005', args=eargs))
    # names must be same length as data
    if len(names) != len(data):
        eargs = [filename, len(data), len(names), func_name]
        WLOG(params, 'error', textentry('00-013-00009', args=eargs))
    # if dtype is not None must be same length as data
    if dtype is not None:
        if len(data) != len(dtype):
            eargs = [filename, len(data), len(dtype), func_name]
            WLOG(params, 'error', textentry('00-013-00006', args=eargs))
    # ----------------------------------------------------------------------
    # create the multi HDU list
    # try to create primary HDU first
    if isinstance(header[0], Header):
        if hasattr(header[0], 'to_fits_header'):
            header0 = header[0].to_fits_header()
        else:
            header0 = header[0].copy()
    else:
        header0 = header[0]

    # data should not be in primary - we should have None as the first data
    # entry - if no
    if data[0] is None:
        # set up primary HDU (header only)
        hdu0 = fits.PrimaryHDU(header=header0)
    else:
        # set up primary HDU (header only)
        hdu0 = fits.PrimaryHDU(data[0], header=header0)
    # remove first entry from data / header
    data = data[1:]
    header = header[1:]
    names = names[1:]
    datatype = datatype[1:]
    dtype = dtype[1:]
    # add primary to hdus
    hdus = [hdu0]
    # add all others afterwards
    for it in range(len(data)):
        # ---------------------------------------------------------------------
        # sanity check on data type (force Tables to 'table')
        if isinstance(data[it], Table):
            datatype[it] = 'table'
        elif not isinstance(data[it], np.ndarray):
            pass
        elif 'void' in data[it].dtype.name:
            datatype[it] = 'table'
        # ---------------------------------------------------------------------
        if datatype[it] == 'image':
            fitstype = fits.ImageHDU
        elif datatype[it] == 'table':
            fitstype = fits.BinTableHDU
        else:
            # warn user that extension is being skipped
            wargs = [it + 1, names[it], datatype[it]]
            WLOG(params, 'warning', textentry('10-001-00010', args=wargs),
                 sublevel=4)
            continue
        # ---------------------------------------------------------------------
        # only add if header is a fits header
        if isinstance(header[it], (Header, fits.Header)):
            # deal with our custom headers
            if hasattr(header[it], 'to_fits_header'):
                header_it = header[it].to_fits_header()
            else:
                header_it = header[it].copy()
        # otherwise we shouldn't really set header
        else:
            header_it = fits.Header()
        # must add the EXTNAME for all extensions
        header_it['EXTNAME'] = (names[it], 'name of the extension')
        # ---------------------------------------------------------------------
        # set HDU_i
        hdu_i = fitstype(data[it], header=header_it)
        # deal with dtype being set
        if dtype is not None and datatype[it] == 'image':
            if dtype[it] is not None:
                hdu_i.scale(type=dtype[it], **SCALEARGS)
        hdus.append(hdu_i)
    # convert to  HDU list
    hdulist = fits.HDUList(hdus)
    # except Exception as e:
    #     eargs = [type(e), e, func_name]
    #     WLOG(params, 'error', textentry('01-001-00004', args=eargs))
    #     hdulist = None
    # ---------------------------------------------------------------------
    # write to file
    with warnings.catch_warnings(record=True) as w:
        try:
            hdulist.writeto(filename, overwrite=True)
            hdulist.close()
        except Exception as e:
            eargs = [os.path.basename(filename), type(e), e, func_name]
            WLOG(params, 'error', textentry('01-001-00005', args=eargs))
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


def update_extension(params: ParamDict, filename: str, extension: int,
                     data: Union[np.ndarray, Table, None] = None,
                     header: Union[Header, None] = None, fmt: str = 'image'):
    """
    Update the extension of an existing file

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename to save to
    :param extension: int, the extension to update
    :param data: numpy array or astropy Table, the data to update
    :param header: Header, if set updates the header
    :param fmt: str, the data format (image or table)

    :return: None, updates filename hdu extension="extension"
    """
    # set function name
    func_name = display_func('_update_extension', __NAME__)
    # deal with fits type
    if fmt in ['image', 'fits-image']:
        fitstype = fits.ImageHDU
    elif fmt in ['table', 'fits-table']:
        fitstype = fits.BinTableHDU
    else:
        # log error fmt must be image or table
        WLOG(params, 'error', textentry('00-004-00013', args=[fmt]))
        return
    # open hdulist
    with fits.open(filename) as hdulist:
        # only update if we have enough extensions
        if len(hdulist) >= extension:
            # set up new hdu
            new_hdu_list = []
            # loop around all extensions
            for ext in range(len(hdulist)):
                # if we are not changing the extension add it here
                if ext != extension:
                    new_hdu_list.append(hdulist[ext].copy())
                # else update data / header
                else:
                    # update header if not None (and Header instance)
                    if header is not None:
                        if isinstance(header, Header):
                            header = header.to_fits_header()
                        else:
                            header = header.copy()
                    if data is None and header is None:
                        new_hdu_list.append(hdulist[ext].copy())
                    elif data is None:
                        new_hdu = hdulist[ext].copy()
                        new_hdu.header = header
                        new_hdu_list.append(new_hdu)
                    elif header is None:
                        new_hdu_list.append(fitstype(data))
                    else:
                        new_hdu_list.append(fitstype(data, header=header))
        # else raise error
        else:
            # log error: Extension {0} not in {1}
            eargs = [extension, filename, func_name]
            # log error
            WLOG(params, 'error', textentry('00-004-00014', args=eargs))
            return
        # write to file
        with warnings.catch_warnings(record=True) as _:
            try:
                nhdulist = fits.HDUList(new_hdu_list)
                nhdulist.writeto(filename, overwrite=True)
                nhdulist.close()
            except Exception as e:
                eargs = [os.path.basename(filename), type(e), e, func_name]
                WLOG(params, 'error', textentry('01-001-00005', args=eargs))


# =============================================================================
# Worker functions
# =============================================================================
# complex typing return for deal_with_bad_header
BadHdrType = Tuple[List[np.ndarray], List[fits.Header], List[str]]


def deal_with_bad_header(params: ParamDict, hdu: fits.HDUList,
                         filename: str) -> BadHdrType:
    """
    Deal with bad headers by iterating through good hdu's until we hit a
    problem

    :param params: ParamDict, the constants file
    :param hdu: astropy.io.fits HDU
    :param filename: string - the filename for logging

    :returns: a typle 1. the list of data (images), 2. the list of headers
              up to the point where it cannot get them
    """
    # set function name
    _ = display_func('deal_with_bad_header', __NAME__)
    # define condition to pass
    cond = True
    # define iterator
    it = 0
    # define storage
    datastore = []
    headerstore = []
    names = []
    # loop through HDU's until we cannot open them
    while cond:
        # noinspection PyBroadException
        try:
            datastore.append(hdu[it].data)
            headerstore.append(hdu[it].header)
            names.append(hdu[it].name)
        except Exception as _:
            cond = False
        # iterate
        it += 1
    # print message
    if len(datastore) > 0:
        dargs = [it - 1, filename]
        WLOG(params, 'warning', textentry('10-001-00001', args=dargs),
             sublevel=4)
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        WLOG(params, 'error', textentry('01-001-00001', args=[filename]))
    # return valid data
    return datastore, headerstore, names


def check_dtype_for_header(value: Any) -> Any:
    """
    Header datatype value assignment
    if string:  check for file (os.path.isfile) --> remove path
                check for directory (os.path.isdir) --> remove path
    if bool: change True --> 1, False --> 0
    if float: np.nan --> NaN  np.inf --> INF  -np.inf --> -INF
    if int: just copy to new int
    else: copy to new string

    :param value: Any value to be pushed into header

    :return: the value updates with rules above
    """
    # set function name
    _ = display_func('check_dtype_for_header', __NAME__)
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
        elif np.isposinf(value):
            newvalue = 'INF'
        elif np.isneginf(value):
            newvalue = '-INF'
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


def deal_with_bad_file_single(filename, ext=None, extname=None,
                              flavour: str = 'data'):
    """
    One last attempt to read data or header but not both, for a single
    ext or extname

    :param filename:
    :param ext:
    :param extname:
    :return:
    """
    # open HDU
    hdulist = fits.open(filename)
    # deal with having an extension number
    if ext is not None:
        if flavour == 'data':
            return hdulist[ext].data
        else:
            return hdulist[ext].header
    # deal with having a extension name
    if extname is not None:
        if flavour == 'data':
            return hdulist[extname].data
        else:
            return hdulist[extname].header
    # else loop around until we find the data we are after
    else:
        for ext in range(len(hdulist)):
            if flavour == 'data' and hdulist[ext].data is not None:
                return hdulist[ext].data
            elif flavour == 'header' and hdulist[ext].header is not None:
                return hdulist[ext].header


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
