#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 11:36

@author: cook
"""
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy import version as av
import os
from pathlib import Path
import warnings
import traceback
from typing import Any, Dict, List, Tuple, Union

from apero.base import base
from apero.base import drs_exceptions
from apero.base import drs_text
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero import lang
from apero.io import drs_table
from apero.io import drs_lock
from apero.io import drs_path

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
# Drs File class
DrsInputFile = drs_file.DrsInputFile
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# Get function string
display_func = drs_log.display_func
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
# TODO: This should be changed for astropy -> 2.0.1
# bug that hdu.scale has bug before version 2.0.1
if av.major < 2 or (av.major == 2 and av.minor < 1):
    SCALEARGS = dict(bscale=(1.0 + 1.0e-8), bzero=1.0e-8)
else:
    SCALEARGS = dict(bscale=1, bzero=0)
# Define any simple type for typing
AnySimple = Union[int, float, str, bool]
# get header comment cards
HeaderCommentCards = fits.header._HeaderCommentaryCards


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
        _ = display_func(None, '__init__', __NAME__, self.classname)
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
        _ = display_func(None, '__setitem__', __NAME__, self.classname)
        # deal with key not being string
        if isinstance(key, tuple):
            # assume it is a tuple (key, id) - therefore we check key[0]
            if key[0].startswith('@@@'):
                tmpkey = self.__get_temp_key(key[0])
                self.__temp_items.__setitem__(tmpkey, item)
            else:
                # check for NaN values (and convert -- cannot put directly in)
                nan_filtered = self.__nan_check(item)
                # do the super __setitem__ on nan filtered item
                super().__setitem__(key, nan_filtered)
        # if key starts with @@@ add to temp items (without @@@)
        if key.startswith('@@@'):
            # use the __get_temp_key method to strip key
            self.__temp_items.__setitem__(self.__get_temp_key(key), item)
        # do not add empty keys
        elif key == '':
            pass
        # else add normal keys
        else:
            # check for NaN values (and convert -- cannot put directly in)
            nan_filtered = self.__nan_check(item)
            # do the super __setitem__ on nan filtered item
            super().__setitem__(key, nan_filtered)

    def __getitem__(self, key: str) -> Union[AnySimple, dict]:
        """
        Get an "item" with key
        same as using: item = header[key]

        :param key: str, the key in the header to get item for
        :return: the item in the header with key="key"
        """
        # set function
        _ = display_func(None, '__getitem__', __NAME__, self.classname)
        # deal with key not being string
        if isinstance(key, tuple):
            # assume it is a tuple (key, id) - therefore we check key[0]
            if key[0].startswith('@@@'):
                tmpkey = self.__get_temp_key(key[0])
                return self.__temp_items.__getitem__(tmpkey)
            else:
                return super().__getitem__(key)
        elif not isinstance(key, str):
            return super().__getitem__(key)
        # if key starts with @@@ get it from the temporary items storage
        if key.startswith('@@@'):
            return self.__temp_items.__getitem__(self.__get_temp_key(key))
        # else get it from the normal storage location (in super)
        else:
            return super().__getitem__(key)

    def __contains__(self, key: str) -> bool:
        """
        Whether key is in header
        same as using: key in header

        :param key: str, the key to search for in the header
        :return:
        """
        # set function
        _ = display_func(None, '__contains__', __NAME__, self.classname)
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

    def copy(self, strip: bool = False) -> 'Header':
        """
        Copy an entire header (including temp items)

        :param strip: If `True`, strip any headers that are specific to one
                      of the standard HDU types, so that this header can be
                      used in a different HDU.

        :return: copy of the header
        """
        # set function
        _ = display_func(None, 'copy', __NAME__, self.classname)
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
        _ = display_func(None, 'to_fits_header', __NAME__, self.classname)
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
        _ = display_func(None, 'from_fits_header', __NAME__)
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
        _ = display_func(None, 'from_fits_header', __NAME__)
        # look for temp key prefix
        if key.startswith(chars):
            return key[len(chars):]
        else:
            return key

    @staticmethod
    def __nan_check(value) -> Any:
        """
        Check for NaNs/Infs in value (cannot be used in astropy.io.header)

        :param value: Any, check for NaNs/INFs

        :return: if NaN or INF found replaces with string, else just returns
                 the original value
        """
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
def id_drs_file(params: ParamDict, recipe: Any,
                drs_file_sets: Union[List[DrsFitsFile], DrsFitsFile],
                filename: Union[List[str], str, None] = None,
                nentries: Union[int, None] = None,
                required: bool = True, use_input_file: bool = False
                ) -> Tuple[bool, Union[DrsFitsFile, List[DrsFitsFile]]]:
    """
    Identify the drs file (or set of drs files) each with DrsFitsFile.name
    and DrsFitsFile.filename (or 'filename') set (important must have filename
    to be able to read header) - uses the DrsFitsFile.fileset to search for a
    specific DrsFitsFile that this filename / header describes.
    If nentries = 1 returns the first DrsFitsFile that statisfies header,
    otherwise returns all DrsFitsFile(s) that statisfy the header.

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe to associate with this DrsFitsFile
    :param drs_file_sets: List[DrsFitsFile] or DrsFitsFile - the file instance
                          containing the filename, fileset (set of DrsinputFiles
                          for this group i.e. raw files) etc
                          if DrsFitsFile.filename is not set then 'filename'
                          must be set (raises error elsewise)
    :param filename: str or None, if DrsFitsFile (or instance in
                     List[DrsFitsFile]) does not have filename set it from here
                     this filename is the file that the header is read from
    :param nentries: int or None, if equal to 1 returns just the first
                     DrsFitsFile.fileset entry which matches the header - else
                     returns all DrsFitsFile(s) that match header
    :param required: bool, if True raises an error when filename/header combo
                     does not match a DrsFitsFile in any of the fileset(s)
    :param use_input_file: bool, if True set the data and header from the
                           inpit file (i.e. the DrsFitsFile with the fileset)
    :return: tuple, 1. bool, whether file was found,
                    2. the DrsFitsFile matching (if entries=1) else all the
                       DrsFitsFile(s) matching i.e. List[DrsFitsFile]
    """
    # set function
    func_name = display_func(params, 'id_drs_file', __NAME__)
    # ----------------------------------------------------------------------
    # deal with list vs no list for drs_file_sets
    if isinstance(drs_file_sets, list):
        pass
    else:
        drs_file_sets = [drs_file_sets]
    # ----------------------------------------------------------------------
    # storage
    found = False
    kinds = []
    names = []
    file_set = None
    # ----------------------------------------------------------------------
    # loop around file set
    for file_set in drs_file_sets:
        # get the names of the file_set
        names.append(file_set.name)
        # ------------------------------------------------------------------
        # check we have entries
        if len(file_set.fileset) == 0:
            continue
        # ------------------------------------------------------------------
        # check we have a params set for file_set
        file_set.params = params
        # ------------------------------------------------------------------
        # check we ahve a file set
        if file_set.filename is None:
            if filename is None:
                WLOG(params, 'error', 'filename is not set')
            else:
                file_set.set_filename(filename)
        # ------------------------------------------------------------------
        # get the associated files with this generic drs file
        fileset = list(file_set.fileset)
        # ------------------------------------------------------------------
        # loop around files
        for drsfile in fileset:
            # set params
            drsfile.params = params
            # --------------------------------------------------------------
            # debug
            dargs = [str(drsfile)]
            WLOG(params, 'debug', TextEntry('90-010-00001', args=dargs))
            # --------------------------------------------------------------
            # copy info from given_drsfile into drsfile
            file_in = drsfile.copyother(file_set, recipe=recipe)
            # --------------------------------------------------------------
            # load the header for this kind
            # noinspection PyBroadException
            try:
                # need to read the file header for this specific drs file
                file_in.read_header(log=False)
                # copy in hdict from file_set
                # - this is the only way to get keys added from file that is
                #   read above
                if file_set.hdict is not None:
                    for key in file_set.hdict:
                        file_in.header[key] = file_set.hdict[key]

            # if exception occurs continue to next file
            #    (this is not the correct file)
            except Exception as _:
                continue
            except SystemExit as _:
                continue
            # --------------------------------------------------------------
            # check this file is valid
            cond, _ = file_in.check_file()
            # --------------------------------------------------------------
            # if True we have found our file
            if cond:
                # ----------------------------------------------------------
                found = True
                # ----------------------------------------------------------
                # load the data for this kind
                cond1 = file_set.data is not None
                cond2 = file_set.header is not None
                # use the data if flagged and if possible (cond1 & cond2)
                if use_input_file and cond1 and cond2:
                    # shallow copy data
                    file_in.data = file_set.data
                    # copy over header
                    file_in.header = file_set.header
                else:
                    file_in.read_data()
                # ----------------------------------------------------------
                # append to list
                kinds.append(file_in)
                # ----------------------------------------------------------
                # if we only want one entry break here
                if nentries == 1:
                    break
    # ----------------------------------------------------------------------
    # deal with no files found
    if len(kinds) == 0 and required:
        # get header keys for info purposes
        keys = ['KW_CCAS', 'KW_CREF', 'KW_OBSTYPE', 'KW_TARGET_TYPE',
                'KW_OBJNAME']
        argstr = ''
        for key in keys:
            if file_set is not None and file_set.header is not None:
                value = file_set.get_hkey(key)
            else:
                value = None
            argstr += '\t{0}: {1}\n'.format(key, value)

        eargs = [' '.join(names), file_set.filename, argstr, func_name]
        WLOG(params, 'error', TextEntry('00-010-00001', args=eargs))
    # ----------------------------------------------------------------------
    # return found and the drsfile instance
    if len(kinds) == 0:
        return found, kinds
    elif nentries is None:
        return found, kinds
    elif nentries == 1:
        return found, kinds[0]
    else:
        return found, kinds[:nentries]


# =============================================================================
# Define read functions
# =============================================================================
# TODO: Got to here with the python typing

# define complex typing for readfits
DataHdrType = Tuple[np.ndarray, fits.Header]


def readfits(params: ParamDict, filename: Union[str, Path],
             getdata: bool = True, gethdr: bool = False,
             fmt: str = 'fits-image',
             ext: int = 0, func: Union[str, None] = None,
             log: bool = True, copy: bool = False
             ) -> Union[DataHdrType, np.ndarray, fits.Header, None]:
    """
    The drs fits file read function

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: string, the absolute path to the file
    :param getdata: bool, whether to return data from "ext"
    :param gethdr: bool, whether to return header from "ext"
    :param fmt: str, format of data (either 'fits-image' or 'fits-table'
    :param ext: int, the extension to open
    :param func: str, function name of calling function (input function)
    :param log: bool, if True logs that we read file
    :param copy: bool, if True copies the HDU[i].data and/or HDU[i].header so
                 HDU can be closed properly

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
    # set function
    func_name = display_func(params, 'readfits', __NAME__)
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
            WLOG(params, 'error', TextEntry('01-001-00013', args=eargs))
        else:
            eargs = [os.path.basename(filename), dirname, func_name]
            WLOG(params, 'error', TextEntry('01-001-00012', args=eargs))
    # -------------------------------------------------------------------------
    # deal with obtaining data
    if fmt == 'fits-image':
        data, header = _read_fitsimage(params, filename, getdata, gethdr, ext,
                                       log=log)
    elif fmt == 'fits-table':
        data, header = _read_fitstable(params, filename, getdata, gethdr, ext,
                                       log=log)
    elif fmt == 'fits-multi':
        data, header = _read_fitsmulti(params, filename, getdata, gethdr,
                                       log=log)
    else:
        cfmts = ', '.join(allowed_formats)
        eargs = [filename, fmt, cfmts, func_name]
        WLOG(params, 'error', TextEntry('00-008-00019', args=eargs))
        data, header = None, None
    # -------------------------------------------------------------------------
    # deal with copying
    if copy:
        data = np.array(data)
        header = fits.Header(header)
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


def read_header(params: ParamDict, filename: str, ext: int = 0,
                log: bool = True) -> fits.Header:
    """
    Read the header from a fits file located at 'filename' with extension
    'ext' (defaults to 0)

    :param params: ParamDict, parameter dictionary of constants
    :param filename: str, the filename to read the fits hdu from
    :param ext: int, the hdu extension to read the header from (defaults to 0)
    :param log: bool, if True logs on error, else raises astropy.io.fits
                exception that generated the error

    :return: astropy.io.fits.Header instance - the header read from 'filename'
    """
    # set function name
    func_name = display_func(params, 'read_header', __NAME__)
    # try to open header
    try:
        header = fits.getheader(filename, ext=ext)
    except Exception as e:
        if log:
            eargs = [os.path.basename(filename), ext, type(e), e, func_name]
            WLOG(params, 'error', TextEntry('01-001-00010', args=eargs))
            header = None
        else:
            raise e
    # return header
    return header


# define complex typing for _read_fitsmulti
DataHdrListType = Union[Tuple[List[np.ndarray], List[fits.Header]],
                        List[np.ndarray], List[fits.Header]]


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
    func_name = display_func(params, '_read_fitsmulti', __NAME__)
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
                if log:
                    eargs = [os.path.basename(filename), it, type(e), e,
                             func_name]
                    WLOG(params, 'error', TextEntry('01-001-00008', args=eargs))
                else:
                    raise e
            # append data
            try:
                if isinstance(hdulist[it].data, fits.BinTableHDU):
                    dataarr.append(Table.read(hdulist[it].data))
                else:
                    dataarr.append(hdulist[it].data)
            except Exception as e:
                if log:
                    eargs = [os.path.basename(filename), it, type(e), e,
                             func_name]
                    WLOG(params, 'error', TextEntry('01-001-00007', args=eargs))
                else:
                    raise e
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


# define complex typing for _read_fitsimage
ImageFitsType = Tuple[Union[np.ndarray, None], Union[fits.Header, None]]


def _read_fitsimage(params: ParamDict, filename: str, getdata: bool,
                    gethdr: bool, ext: int = 0,
                    log: bool = True) -> ImageFitsType:
    """
    Read a fits image in extension 'ext' for fits file 'filename'
    returns data if getdata is True, returns header if gethdr is True

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename to read the fits hdu from
    :param getdata: bool, if True read the data from extension 'ext'
    :param gethdr: bool, if True read the headers from extension 'ext'
    :param log: bool, if True logs on error, else raises astropy.io.fits
                exception that generated the error

    :return: data if getdata True and/or headers if gethdr True
    """
    # set function name
    _ = display_func(params, '_read_fitsimage', __NAME__)
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            data = fits.getdata(filename, ext=ext)
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = TextEntry('01-001-00014', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
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
                emsg = TextEntry('01-001-00015', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
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
                    gethdr: bool, ext: int = 0,
                    log: bool = True) -> TableFitsType:
    """
    Read a fits bin table in extension 'ext' for fits file 'filename'
    returns table if getdata is True, returns header if gethdr is True

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename to read the fits hdu from
    :param getdata: bool, if True read the table from extension 'ext'
    :param gethdr: bool, if True read the headers from extension 'ext'
    :param log: bool, if True logs on error, else raises astropy.io.fits
                exception that generated the error

    :return: table if getdata True and/or headers if gethdr True
    """
    # set function name
    _ = display_func(params, '_read_fitstable', __NAME__)
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            data = Table.read(filename, format='fits')
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = TextEntry('01-001-00016', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
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
                emsg = TextEntry('01-001-00017', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
                WLOG(params, 'error', emsg)
                header = None
            else:
                raise e
    else:
        header = None
    # -------------------------------------------------------------------------
    # return data and header
    return data, header


# =============================================================================
# Define write functions
# =============================================================================
# define complex typing for writing
ListImageTable = Union[List[Union[np.ndarray, Table]], np.ndarray, Table]
ListHeader = Union[List[Union[Header, fits.Header]], Header, fits.Header]


def writefits(params: ParamDict, filename: str,
              data: ListImageTable, header: ListHeader,
              datatype: Union[List[str], str] = 'image',
              dtype: Union[List[str], str, None] = None,
              func: Union[str, None] = None):
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
    _ = display_func(params, 'writefits', __NAME__)
    # ------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    lockfile = os.path.basename(filename)
    # start a lock
    lock = drs_lock.Lock(params, lockfile)

    # ------------------------------------------------------------------
    # make locked read function
    @drs_lock.synchronized(lock, params['PID'])
    def locked_write():
        return _write_fits(params, filename, data, header, datatype, dtype,
                           func)

    # ------------------------------------------------------------------
    # try to run locked read function
    try:
        locked_write()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


def _write_fits(params: ParamDict, filename: str,
                data: ListImageTable, header: ListHeader,
                datatype: Union[List[str], str] = 'image',
                dtype: Union[List[str], str, None] = None,
                func: Union[str, None] = None):
    """
    Internal write fits file function (should use writefits externally)
    write fits file with single extension (data/header/datatype/dtype)
    are not lists, or multiple extensions (data/header/datatype/dtype)
    are lists.

    if data/header/datatype/dtype are lists all others must be lists of the
    same legnth

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
    func_name = display_func(params, '_write_fits', __NAME__)
    # deal with function name coming from somewhere else
    if func is not None:
        func_name = '{0} (via {1})'.format(func, func_name)
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
        # convert Header instance to astropy.io.fits header
        if isinstance(header, Header):
            if hasattr(header, 'to_fits_header'):
                header = [header.to_fits_header()]
            else:
                header = [header.copy()]
        else:
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
    # try to create primary HDU first
    if isinstance(header[0], Header):
        if hasattr(header[0], 'to_fits_header'):
            header0 = header[0].to_fits_header()
        else:
            header0 = header[0].copy()
    else:
        header0 = header[0]
    # set up primary HDU (if data[0] == image then put this in the primary)
    #   else if table then primary HDU should be empty
    # TODO: need to fix this so hdu[0] is always empty
    # TODO:    --> start = 0 and no data[0] in PrimaryHDU
    if datatype[0] == 'image':
        hdu0 = fits.PrimaryHDU(data[0], header=header0)
        start = 1
    else:
        hdu0 = fits.PrimaryHDU(header=header0)
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
            if hasattr(header[it], 'to_fits_header'):
                header_it = header[it].to_fits_header()
            else:
                header_it = header[it].copy()
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
            hdulist.close()
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
def find_files(params: ParamDict, recipe: Any = None,
               kind: Union[str, None] = None,
               path=None, logic: str = 'and', fiber: Union[str, None] = None,
               return_table: bool = False, night: Union[str, None] = None,
               filters: Union[Dict[str, Any], None] = None,
               rawindexfile: Union[str, None] = None
               ) -> Union[Tuple[np.ndarray, Table], np.ndarray]:
    """
    Find files of type 'kind' that match a set of filters (if filters set) else
    return all files of that 'kind'

    If path is set will use this path to look for index files

    If kind is set to 'raw' uses DRS_DATA_RAW path, if kind is set to 'tmp'
    uses DRS_DATA_WORKING path, if kind is set to 'red' uses DRS_DATA_REDUC
    else uses params['INPATH']

    The logic defines how kwargs are added.
    kwargs must be in index file (column names) or in params as header keyword
    stores (i.e. KW_DPRTYPE = [HEADER key, HEADER value, HEADER comment]

    i.e.

    find_files(params, kind='tmp', filters=dict(KW_DPRTYPE='FP_FP'))
    --> will return all files in the working directory with DPRTYPE = 'FP_FP'

    find_files(params, kind='red',
               filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK'],
                            KW_OUTPUT='EXT_E2DS'))
    --> will return all files in reduced directory with:
          DPRTYPE = OBJ_FP or OBJ_DARK   and DRSOUTID

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, used when finding raw files (can be None elsewise)
    :param kind: str, the kind of file must be either 'raw', 'red' or 'tmp' or
                 None - if None 'path' or params['INPATH'] must be set
    :param path: str, the path to the index files
    :param logic: str, either 'and' or 'or' - how filters are combined
                  i.e. (FILTER1 AND FILTER2)  or (FILTER1 OR FILTER2)
                  note if values in filters are lists these are always combined
                  with OR statements

    :param fiber: str or None - if set means files must have an associated fiber
    :param return_table: bool, if True return masked index table with only those
                         files agreeing with filters
    :param night: str or None, if set filters the returns by the night name
                  directory
    :param filters: dict or None, if set contains key value pairs to filter the
                    returns by i.e.
                    filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK'],
                                 KW_OUTPUT='EXT_E2DS'))
                    will return all files in reduced directory with:
                        DPRTYPE = OBJ_FP or OBJ_DARK   and DRSOUTID
    :param rawindexfile: str, override the deafult raw index file name,
                         default set by params['REPROCESS_RAWINDEXFILE'],
                         only used it kind=='raw'

    :return: if return_table is true, returns a tuple of the filelist (np.array)
             and the index database filtered for all filters, if return_table is
             false, only returns the filters list of files (np.array)
    """
    # set function name
    func_name = display_func(params, 'find_files', __NAME__)
    # ----------------------------------------------------------------------
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get the index file col name
    filecol = params['DRS_INDEX_FILENAME']
    nightcol = params['REPROCESS_NIGHTCOL']
    timecol = 'KW_MID_OBS_TIME'
    # deal with no filters
    if filters is None:
        filters = dict()
    # ----------------------------------------------------------------------
    # deal with setting path
    if path is not None:
        path = str(path)
        columns = None
        index_files = None
        index_dir = None
    elif kind == 'raw':
        # get index table (generate if needed)
        indextable, index_dir = find_raw_files(params, recipe)
        # construct index file path for raw
        raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE',
                                func=func_name, override=rawindexfile)
        mpath = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
        # set the columns from table
        columns = indextable.colnames
        # set index files
        index_files = [mpath]
    elif kind == 'tmp':
        path = params['DRS_DATA_WORKING']
        columns = pconst.OUTPUT_FILE_HEADER_KEYS()
        index_files = None
        index_dir = None
    elif kind == 'red':
        path = params['DRS_DATA_REDUC']
        columns = pconst.OUTPUT_FILE_HEADER_KEYS()
        index_files = None
        index_dir = None
    else:
        path = params['INPATH']
        columns = None
        index_files = None
        index_dir = None
    # ----------------------------------------------------------------------
    # deal with making sure all kwargs are in columns (if columns defined)
    if columns is not None:
        for fkey in filters:
            # if dkey not in columns report error
            if fkey not in columns:
                # log and raise error
                eargs = [fkey, path, func_name]
                WLOG(params, 'error', TextEntry('00-004-00001', args=eargs))
    # ----------------------------------------------------------------------
    # get index files
    if index_files is None:
        index_files = get_index_files(params, path, night=night)
    # ----------------------------------------------------------------------
    # valid files storage
    valid_files = []
    table_list = []
    time_list = []
    # filters added string
    fstring = ''
    # ----------------------------------------------------------------------
    # loop through index files
    for index_file in index_files:
        # read index file
        index = drs_table.read_fits_table(params, index_file)
        # get directory
        if index_dir is None:
            dirname = os.path.dirname(index_file)
        else:
            dirname = index_dir
        # ------------------------------------------------------------------
        # overall masks
        mask = np.ones(len(index), dtype=bool)
        # filters added string
        fstring = ''
        # ------------------------------------------------------------------
        # filter via kwargs
        for fkey in filters:
            # --------------------------------------------------------------
            # if dkey is not found in index file then report error
            if fkey not in index.colnames:
                # report error
                eargs = [fkey, index_file, func_name]
                WLOG(params, 'error', TextEntry('00-004-00002', args=eargs))
            # --------------------------------------------------------------
            # deal with list of args
            if isinstance(filters[fkey], list):
                # get new mask
                mask0 = np.zeros_like(mask)
                # loop around kwargs[kwarg] values (has to be logic==or here)
                for value in filters[fkey]:
                    mask0 |= (index[fkey] == value.strip())
            else:
                mask0 = (index[fkey] == filters[fkey])
            # --------------------------------------------------------------
            # mask by filter
            if logic == 'or':
                mask |= mask0
            else:
                mask &= mask0
            # --------------------------------------------------------------
            # add to fstring
            fstring += '\n\t{0}=\'{1}\''.format(fkey, filters[fkey])
        # ------------------------------------------------------------------
        # get files for those that remain
        masked_files = index[filecol][mask]
        if index_dir is None:
            nightnames = np.array(mask).astype(int)
        else:
            nightnames = index[nightcol][mask]
        # ------------------------------------------------------------------
        masked_index = index[mask]
        # new mask for index files
        mask1 = np.zeros(len(masked_files), dtype=bool)
        # check that files exist
        # loop around masked files
        for row, filename in enumerate(masked_files):
            # deal with requiring night name
            if index_dir is None:
                nightname = ''
            else:
                nightname = nightnames[row]
            # --------------------------------------------------------------
            # deal with fiber
            if fiber is not None:
                # two conditions for not having fiber in name
                cond1 = '_{0}.'.format(fiber) not in filename
                cond2 = '_{0}_'.format(fiber) not in filename
                # if both conditions are True then skip
                if cond1 and cond2:
                    continue
            # get time value
            timeval = float(masked_index[timecol][row])
            # construct absolute path
            absfilename = os.path.join(dirname, nightname, filename)
            # check that file exists
            if not os.path.exists(absfilename):
                continue
            # deal with returning index
            mask1[row] = True
            # append to storage
            if absfilename not in valid_files:
                valid_files.append(absfilename)
                time_list.append(timeval)
        # ------------------------------------------------------------------
        # append to table list
        if return_table:
            table_list.append(masked_index[mask1])
    # ----------------------------------------------------------------------
    # log found
    wargs = [len(valid_files), fstring]
    WLOG(params, '', TextEntry('40-004-00004', args=wargs))
    # ----------------------------------------------------------------------
    # define sort mask (sort by time column)
    sortmask = np.argsort(time_list)
    # make sure valid_files is a numpy array
    valid_files = np.array(valid_files)
    # deal with table list
    if return_table:
        indextable = drs_table.vstack_cols(params, table_list)
        return valid_files[sortmask], indextable[sortmask]
    else:
        # return full list
        return valid_files[sortmask]


def get_index_files(params: ParamDict, path: Union[str, None] = None,
                    required: bool = True, night: Union[str, None] = None
                    ) -> np.ndarray:
    """
    Get index files in path (or sub-directory of path)
        if path is "None" params['INPATH'] is used

    :param params: ParamDict, the parameter dictionary of constants
    :param path: str, the path to check for filetypes (must have index files
                 in this path or sub directories of this path)
                 if path is "None" params['INPATH'] is used
    :param required: bool, if True generates an error when None found
    :param night: str or None, if set filters index files by night

    :type params: ParamDict
    :type path: str
    :type required: bool
    :type night: str

    :return: the absolute paths to all index files under path (array of strings)
    :rtype: np.array
    """
    # set function name
    func_name = display_func(params, 'get_index_files', __NAME__)
    # deal with no path set
    if path is None:
        path = params['INPATH']
    # storage of index files
    index_files = []
    # walk through path and find index files
    for root, dirs, files in os.walk(path, followlinks=True):
        # skip nights if required
        if night is not None:
            if not root.strip(os.sep).endswith(night):
                continue
        for filename in files:
            if filename == params['DRS_INDEX_FILE']:
                index_files.append(os.path.join(root, filename))
    # log number of index files found
    if len(index_files) > 0:
        WLOG(params, '', TextEntry('40-004-00003', args=[len(index_files)]))
    elif required:
        eargs = [path, func_name]
        WLOG(params, 'error', TextEntry('01-001-00021', args=eargs))
    # return the index files
    return np.sort(index_files)


def find_raw_files(params: ParamDict, recipe: Any,
                   nightcol: Union[str, None] = None,
                   absfilecol: Union[str, None] = None,
                   modifiedcol: Union[str, None] = None,
                   sort_col: Union[str, None] = None,
                   rawindexfile: Union[str, None] = None,
                   itablefilecol: Union[str, None] = None
                   ) -> Tuple[Table, str]:
    """
    Generate a list of all raw files (get raw files first from a pre-generated
    list of raw files and update by looking in the raw directory)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe associated with the call to this file
    :param nightcol: str or None, if set overrides params['REPROCESS_NIGHTCOL']
    :param absfilecol: str or None, if set overrides
                       params['REPROCESS_ABSFILECOL']
    :param modifiedcol: str or None, if set overrides
                        params['REPROCESS_MODIFIEDCOL']
    :param sort_col: str or None, if set overrides
                     params['REPROCESS_SORTCOL_HDRKEY']
    :param rawindexfile: str or None, if set overrides
                         params['REPROCESS_RAWINDEXFILE']
    :param itablefilecol: str or None, if set overrides
                          params['DRS_INDEX_FILENAME']

    :return: tuple, 1. the raw file table, 2. str, the raw file path
    """
    # set function name
    func_name = display_func(params, 'find_raw_files', __NAME__)
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', func=func_name,
                       override=nightcol)
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', func=func_name,
                         override=absfilecol)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', func=func_name,
                          override=modifiedcol)
    sortcol = pcheck(params, 'REPROCESS_SORTCOL_HDRKEY', func=func_name,
                     override=sort_col)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE', func=func_name,
                            override=rawindexfile)
    itable_filecol = pcheck(params, 'DRS_INDEX_FILENAME', func=func_name,
                            override=itablefilecol)
    # get path
    path, rpath = _get_path_and_check(params, 'DRS_DATA_RAW')
    # print progress
    WLOG(params, 'info', TextEntry('40-503-00010'))
    # get files
    gfout = _get_files(params, recipe, path, rpath)
    nightnames, filelist, basenames, mod_times, mkwargs = gfout
    # construct a table
    mastertable = Table()
    mastertable[night_col] = nightnames
    mastertable[itable_filecol] = basenames
    mastertable[absfile_col] = filelist
    mastertable[modified_col] = mod_times
    for kwarg in mkwargs:
        mastertable[kwarg] = mkwargs[kwarg]
    # sort by sortcol
    sortmask = np.argsort(mastertable[sortcol])
    mastertable = mastertable[sortmask]
    # save master table
    mpath = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    mastertable.write(mpath, overwrite=True)
    # return the file list
    return mastertable, rpath


def fix_header(params: ParamDict, recipe: Any,
               infile: Union[DrsFitsFile, None] = None,
               header: Union[Header, fits.Header, None] = None,
               raise_exception: bool = False
               ) -> Union[DrsFitsFile, Tuple[Header, Header]]:
    """
    Instrument specific header fixes are define in pseudo_const.py for an
    instrument and called here (function in pseudo_const.py is HEADER_FIXES)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe instance associated with calling this function
    :param infile: DrsFitsFile or None, the Drs file instance containing the
                   header to fix - if not set must have header set
    :param header: Header - if set fixes this header (if not set uses infile)
                   if both set 'header' takes precedence over infile.header
    :param raise_exception: bool, if True raise an exception instead of
                   logging an error

    :return: if infile is set return the infile with the updated infile.header,
             else return hdict and header (both fits.Header instances)
    """
    # set function name
    _ = display_func(params, 'fix_header', __NAME__)
    # deal with no header
    if header is None:
        header = infile.get_header()
        hdict = infile.hdict
        filename = infile.filename
        has_infile = True
    else:
        has_infile = False
        hdict = Header()
        filename = None

    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # use pseudo constant to apply any header fixes required (specific to
    #   a specific instrument) and update the header
    try:
        header, hdict = pconst.HEADER_FIXES(params=params, recipe=recipe,
                                            header=header, hdict=hdict,
                                            filename=filename)
    except drs_exceptions.DrsHeaderError as e:
        if raise_exception:
            raise e
        else:
            eargs = [e.key, e.filename]
            WLOG(params, 'error', TextEntry('01-001-00027', args=eargs))
    # if the input was an infile return the infile back
    if has_infile:
        # return the updated infile
        infile.header = header
        infile.hdict = hdict
        return infile
    # else return the header (assuming input was a header only)
    else:
        # else return the header
        return header, hdict


# =============================================================================
# Define other functions
# =============================================================================
def combine(params: ParamDict, recipe: Any,
            infiles: List[DrsFitsFile], math: str = 'average',
            same_type: bool = True) -> Union[DrsFitsFile, None]:
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
    :param recipe: DrsRecipe, the recipe associated with the call to this
                   function
    :param infiles: list of DrsFiles, list of DrsFitsFiles to combine
    :param math: str, the math allowed (see above)
    :param same_type: bool, if True all infiles must have the same DrsFitFile
                      dtype

    :type params: ParamDict
    :type infiles: list[DrsFitsFile]
    :type math: str
    :type same_type: bool

    :return: Returns the combined DrsFitFile (header same as infiles[0]) or
             if no infiles were given returns None
    :rtype: DrsFitsFile
    """
    # set function name
    func_name = display_func(params, 'combine', __NAME__)
    # if we have a string assume we have 1 file and skip combine
    if isinstance(infiles, DrsFitsFile):
        return infiles
    # make sure infiles is a list
    if not isinstance(infiles, list):
        WLOG(params, 'error', TextEntry('00-001-00020', args=[func_name]))
    # if we have only one file (or none) skip combine
    if len(infiles) == 1:
        return infiles[0]
    elif len(infiles) == 0:
        return None
    # check that all infiles are the same DrsFileType
    if same_type:
        for it, infile in enumerate(infiles):
            if infile.name != infiles[0].name:
                eargs = [infiles[0].name, it, infile.name, func_name]
                WLOG(params, 'error', TextEntry('00-001-00021', args=eargs))

    # get output path from params
    outpath = str(params['OUTPATH'])
    # check if outpath is set
    if outpath is None:
        WLOG(params, 'error', TextEntry('01-001-00023', args=[func_name]))
        return None
    # get the absolute path (for combined output)
    if params['NIGHTNAME'] is None:
        outdirectory = ''
    else:
        outdirectory = params['NIGHTNAME']
    # combine outpath and out directory
    abspath = os.path.join(outpath, outdirectory)
    # read all infiles (must be done before combine)
    for infile in infiles:
        infile.read_file()
    # make new infile using math
    outfile = infiles[0].combine(infiles[1:], math, same_type, path=abspath)
    # update the number of files
    outfile.numfiles = len(infiles)
    # write to disk
    WLOG(params, '', TextEntry('40-001-00025', args=[outfile.filename]))
    outfile.write_file()
    # add to output files (for indexing)
    recipe.add_output_file(outfile)
    # return combined infile
    return outfile


def get_mid_obs_time(params: ParamDict, header: Union[Header, fits.Header],
                     out_fmt: Union[str, None] = None
                     ) -> Tuple[Union[Time, str, float], str]:
    """
    Get the mid point observation time from header and push it into the
    required format

    :param params: Paramdict, parameter dictionary of constants
    :param header: Header or astropy.fits.Header - the header instance to
                   read the MIDMJD from
    :param out_fmt: str, the output format of the data (mjd, jd, iso, human,
                    unix, decimal year) - if set to None returns a astropy.Time
                    instance of the time
    :return: depending on out_fmt - returns a tuple, 1. the mid point of an
             observation (Time, str, float), 2. the method used to get the time
             [now always 'header' - calculated in preprocessing fix_header]
    """
    # set function name
    func_name = display_func(params, 'get_mid_obs_time', __NAME__)
    # get obs_time
    outkey = params['KW_MID_OBS_TIME'][0]
    # get format from params
    timefmt = params.instances['KW_MID_OBS_TIME'].datatype
    # get data type from params
    timetype = params.instances['KW_MID_OBS_TIME'].dataformat
    # get raw value from header
    rawtime = header[outkey]
    # get time object
    obstime = Time(timetype(rawtime), format=timefmt)
    # set the method for getting mid obs time
    method = 'header'
    dbname = 'header_time'
    # return time in requested format
    if out_fmt is None:
        return obstime, method
    elif out_fmt == 'mjd':
        return float(obstime.mjd), method
    elif out_fmt == 'jd':
        return float(obstime.jd), method
    elif out_fmt == 'iso' or out_fmt == 'human':
        return obstime.iso, method
    elif out_fmt == 'unix':
        return float(obstime.unix), method
    elif out_fmt == 'decimalyear':
        return float(obstime.decimalyear), method
    else:
        kinds = ['None', 'human', 'iso', 'unix', 'mjd', 'jd', 'decimalyear']
        eargs = [dbname, ' or '.join(kinds), out_fmt, func_name]
        WLOG(params, 'error', TextEntry('00-001-00030', args=eargs))


# =============================================================================
# Worker functions
# =============================================================================
# complex typing return for deal_with_bad_header
BadHdrType = Tuple[List[np.ndarray], List[fits.Header]]


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
    _ = display_func(params, 'deal_with_bad_header', __NAME__)
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
        WLOG(params, 'warning', TextEntry('10-001-00001', args=dargs))
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        WLOG(params, 'error', TextEntry('01-001-00001', args=[filename]))
    # return valid data
    return datastore, headerstore


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
    _ = display_func(None, 'check_dtype_for_header', __NAME__)
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


def _get_path_and_check(params: ParamDict, key: str) -> Tuple[str, str]:
    """
    Get path from params (using key) i.e. params[key]
    and add nightname (if in params) i.e. params['NIGHTNAME']
    and finally check whether path if valid

    :param params: ParamDict, parameter dictionary of constants
    :param key: str, the key in 'params' to get base path from

    :return: tuple, 1. the full path with nightname if used, 2. the base path
             (i.e. from params[key])
    """
    # set function name
    _ = display_func(params, '_get_path_and_check', __NAME__)
    # check key in params
    if key not in params:
        WLOG(params, 'error', '{0} not found in params'.format(key))
    # get top level path to search
    rpath = params[key]
    # deal with not having nightname
    if 'NIGHTNAME' not in params:
        path = str(rpath)
    elif params['NIGHTNAME'] not in ['', 'None', None]:
        path = os.path.join(rpath, params['NIGHTNAME'])
    else:
        path = str(rpath)
    # check if path exists
    if not os.path.exists(path):
        WLOG(params, 'error', 'Path {0} does not exist'.format(path))
    else:
        return path, rpath


# complex typing from _get_files
GetFilesType = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray,
                     Dict[str, np.ndarray]]


def _get_files(params: ParamDict, recipe: Any, path: str, rpath: str,
               absfilecol: Union[str, None] = None,
               modifiedcol: Union[str, None] = None,
               rawindexfile: Union[str, None] = None) -> GetFilesType:
    """
    Look for raw files - first in a table (rawindexfile) and then on disk
    at 'path'

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe associated with this call
    :param path: str, the path of the raw table file
    :param rpath: str, the bas epath of the raw table (without subdir)
    :param absfilecol: str or None, if set overrides
                       params['REPROCESS_ABSFILECOL']
    :param modifiedcol: str or None, if set overrides
                        params['REPROCESS_MODIFIEDCOL']
    :param rawindexfile: str or None, if set overrides
    params['REPROCESS_RAWINDEXFILE']

    :return: tuple, 1. np.array of night names (sub-directories), 2. np.array
             of raw filenames (absolute), 3. np.array of raw filenames
             (basenames) 4. np.array of last modified times 5. dictionary of
             header keys required for rawindexfile (each key has a value which
             is a np.array equal in length to the number of raw files
    """
    # set function name
    func_name = display_func(params, '_get_files', __NAME__)
    # get properties from params
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', func=func_name,
                         override=absfilecol)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', func=func_name,
                          override=modifiedcol)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE', func=func_name,
                            override=rawindexfile)
    # get the file filter (should be None unless we want specific files)
    filefilter = params.get('FILENAME', None)
    if filefilter is not None:
        filefilter = list(params['FILENAME'])
    # ----------------------------------------------------------------------
    # get the pseudo constant object
    pconst = constants.pload(params['INSTRUMENT'])
    # ----------------------------------------------------------------------
    # get header keys
    headerkeys = pconst.OUTPUT_FILE_HEADER_KEYS()
    # get raw valid files
    raw_valid = pconst.VALID_RAW_FILES()
    # ----------------------------------------------------------------------
    # storage list
    filelist, basenames, nightnames, mod_times = [], [], [], []
    blist = []
    # load raw index
    rawindexfile = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    if os.path.exists(rawindexfile):
        rawindex = drs_table.read_table(params, rawindexfile, fmt='fits')
    else:
        rawindex = None
    # ----------------------------------------------------------------------
    # populate the storage dictionary
    okwargs = dict()
    for key in headerkeys:
        okwargs[key] = []
    # ----------------------------------------------------------------------
    # deal with white/black list for nights
    wnightnames = None
    if 'WNIGHTNAMES' in params:
        if not drs_text.null_text(params['WNIGHTNAMES'], ['None', 'All', '']):
            wnightnames = params.listp('WNIGHTNAMES', dtype=str)
    bnightnames = None
    if 'BNIGHTNAMES' in params:
        if not drs_text.null_text(params['BNIGHTNAMES'], ['None', 'All', '']):
            bnightnames = params.listp('BNIGHTNAMES', dtype=str)
    # ----------------------------------------------------------------------
    # get files (walk through path)
    for root, dirs, files in os.walk(path, followlinks=True):
        # loop around files in this root directory
        for filename in files:
            # --------------------------------------------------------------
            if filefilter is not None:
                if os.path.basename(filename) not in filefilter:
                    continue
            # --------------------------------------------------------------
            # get night name
            ucpath = drs_path.get_uncommon_path(rpath, root)
            if ucpath is None:
                eargs = [path, rpath, func_name]
                WLOG(params, 'error', TextEntry('00-503-00003', args=eargs))
            # --------------------------------------------------------------
            # make sure file is valid
            isvalid = False
            for suffix in raw_valid:
                if filename.endswith(suffix):
                    isvalid = True
            # --------------------------------------------------------------
            # do not scan empty ucpath
            if len(ucpath) == 0:
                continue
            # --------------------------------------------------------------
            # deal with blacklist/whitelist
            if not drs_text.null_text(bnightnames, ['None', 'All', '']):
                if ucpath in bnightnames:
                    # only print path if not already in blist
                    if ucpath not in blist:
                        # log blacklisted
                        margs = [ucpath]
                        WLOG(params, '', TextEntry('40-503-00031', args=margs))
                        # add to blist for printouts
                        blist.append(ucpath)
                    # skip this night
                    continue
            if not drs_text.null_text(wnightnames, ['None', 'All', '']):
                if ucpath not in wnightnames:
                    # skip this night
                    continue
                # elif we haven't seen this night before log statement
                elif ucpath not in nightnames:
                    # log: whitelisted
                    margs = [ucpath]
                    WLOG(params, '', TextEntry('40-503-00030', args=margs))
            # --------------------------------------------------------------
            # log the night directory
            if (ucpath not in nightnames) and (ucpath != rpath):
                # log: scnannming directory
                margs = [ucpath]
                WLOG(params, '', TextEntry('40-503-00003', args=margs))
            # --------------------------------------------------------------
            # get absolute path
            abspath = os.path.join(root, filename)
            modified = os.path.getmtime(abspath)
            # --------------------------------------------------------------
            # if not valid skip
            if not isvalid:
                continue
            # --------------------------------------------------------------
            # else append to list
            else:
                nightnames.append(ucpath)
                filelist.append(abspath)
                basenames.append(filename)
                mod_times.append(modified)
            # --------------------------------------------------------------
            # see if file in raw index and has correct modified date
            if rawindex is not None:
                # find file
                rowmask = (rawindex[absfile_col] == abspath)
                # find match date
                rowmask &= modified == rawindex[modified_col]
                # only continue if both conditions found
                if np.sum(rowmask) > 0:
                    # locate file
                    row = np.where(rowmask)[0][0]
                    # if both conditions met load from raw fits file
                    for key in headerkeys:
                        okwargs[key].append(rawindex[key][row])
                    # file was found
                    rfound = True
                else:
                    rfound = False
            else:
                rfound = False
            # --------------------------------------------------------------
            # deal with header
            if filename.endswith('.fits') and not rfound:
                # read the header
                header = read_header(params, abspath)
                # fix the headers
                try:
                    header, _ = fix_header(params, recipe, header=header,
                                           raise_exception=True)
                except drs_exceptions.DrsHeaderError as e:
                    # log warning message
                    eargs = [e.key, abspath]
                    emsg = TextEntry('10-001-00008', args=eargs)
                    WLOG(params, 'warning', emsg)
                    # remove from lists
                    nightnames.pop()
                    filelist.pop()
                    basenames.pop()
                    mod_times.pop()
                    # continue to next file
                    continue

                # loop around header keys
                for key in headerkeys:
                    rkey = params[key][0]
                    # deal with no key set
                    if len(rkey) == 0:
                        okwargs[key].append('')
                    # deal with key in header
                    elif rkey in header:
                        okwargs[key].append(header[rkey])
                    # else be blank (like no key set)
                    else:
                        okwargs[key].append('')
    # ----------------------------------------------------------------------
    # sort by filename
    sortmask = np.argsort(filelist)
    filelist = np.array(filelist)[sortmask]
    nightnames = np.array(nightnames)[sortmask]
    basenames = np.array(basenames)[sortmask]
    mod_times = np.array(mod_times)[sortmask]
    # need to sort kwargs
    for key in okwargs:
        okwargs[key] = np.array(okwargs[key])[sortmask]
    # ----------------------------------------------------------------------
    # return filelist
    return nightnames, filelist, basenames, mod_times, okwargs


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
