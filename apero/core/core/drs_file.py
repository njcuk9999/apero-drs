#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 12:03

@author: cook

Import rules:

    do not import from core.utils.drs_recipe
    do not import from core.core.drs_argument
"""
from astropy.table import Table
from astropy import version as av
from collections import OrderedDict
from copy import deepcopy
import numpy as np
import os
from pathlib import Path
from typing import Any, Dict, List, Union, Tuple, Type
import warnings

from apero.base import base
from apero.base import drs_exceptions
from apero.core.core import drs_log
from apero.core import constants
from apero.core import math as mp
from apero.core.instruments.default import output_filenames as outf
from apero.core.instruments.default import pseudo_const
from apero import lang
from apero.base import drs_text
from apero.io import drs_fits
from apero.io import drs_path
from apero.io import drs_table


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_file.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display func
display_func = drs_log.display_func
# get time object
Time = base.Time
# Get Logging function
WLOG = drs_log.wlog
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get parameter dictionary
ParamDict = constants.ParamDict
# get header classes from io.drs_fits
Header = drs_fits.Header
FitsHeader = drs_fits.fits.Header
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
HelpText = lang.core.drs_lang_text.HelpDict
# get exceptions
DrsHeaderError = drs_exceptions.DrsHeaderError
DrsCodedException = drs_exceptions.DrsCodedException
# TODO: This should be changed for astropy -> 2.0.1
# bug that hdu.scale has bug before version 2.0.1
if av.major < 2 or (av.major == 2 and av.minor < 1):
    SCALEARGS = dict(bscale=(1.0 + 1.0e-8), bzero=1.0e-8)
else:
    SCALEARGS = dict(bscale=1, bzero=0)
# get header comment card from drs_fits
HCC = drs_fits.HeaderCommentCards
# get default psuedo constants class
PseudoConstants = pseudo_const.PseudoConstants
# -----------------------------------------------------------------------------
# define complex typing
QCParamList = Tuple[List[str], List[Any], List[str], List[int]]


# =============================================================================
# Define File classes
# =============================================================================
class DrsInputFile:
    def __init__(self, name, filetype: str = '',
                 suffix: str = '',
                 remove_insuffix: bool = False,
                 prefix: str = '',
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 directory: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outfunc: Union[Any, None] = None,
                 inext: Union[str, None] = None,
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = None,
                 shape: Union[int, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = None,
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = None,
                 combined_list: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None):
        """
        Create a DRS Input File object

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants 
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys:  passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]


        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set class name
        self.class_name = 'DrsInputFile'
        # set function name
        _ = display_func(params, '__init__', __NAME__, self.class_name)
        # define a name
        self.name = name
        # define the extension
        self.filetype = filetype
        self.suffix = suffix
        self.remove_insuffix = remove_insuffix
        self.prefix = prefix
        self.filename = filename
        self.intype = intype
        # get fiber type (if set)
        self.fibers = fibers
        self.fiber = fiber
        # allow instance to be associated with a set of parameters
        self.params = params
        # set empty file attributes
        self.filename = filename
        self.path = path
        self.basename = basename
        self.inputdir = inputdir
        self.directory = directory
        self.data = data
        self.header = header
        if fileset is None:
            self.fileset = []
        else:
            self.fileset = fileset
        if filesetnames is None:
            self.filesetnames = []
        else:
            self.filesetnames = filesetnames
        self.outfunc = outfunc

        # following keys are not used in this class
        self.inext = inext
        self.dbname = dbname
        self.dbkey = dbkey
        if rkeys is None:
            self.required_header_keys = dict()
        else:
            self.required_header_keys = rkeys
        self.numfiles = numfiles
        self.shape = shape
        self.hdict = hdict
        # get the storage dictionary for output parameters
        if output_dict is None:
            self.output_dict = OrderedDict()
        else:
            self.output_dict = output_dict
        self.datatype = datatype
        self.dtype = dtype
        self.is_combined = is_combined
        self.combined_list = combined_list
        self.s1d = s1d
        # just set hkeys
        self.header_keys = hkeys
        # allow instance to be associated with a filename
        self.set_filename(filename)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        Defines the str(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        _ = display_func(self.params, '__str__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return '{0}[{1}]'.format(self.class_name, self.name)

    def __repr__(self) -> str:
        """
        Defines the print(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        _ = display_func(self.params, '__repr__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return 'DrsInputFile[{0}]'.format(self.name)

    def set_filename(self, filename: str):
        """
        Set the filename, basename and directory name from an absolute path

        :param filename: string, absolute path to the file

        :return None:
        """
        # set function name
        _ = display_func(self.params, 'set_filename', __NAME__, self.class_name)
        # skip if filename is None
        if filename is None:
            return
        # set filename, basename and directory name
        self.filename = str(os.path.abspath(filename))
        self.basename = os.path.basename(filename)
        self.path = os.path.dirname(filename)

    def check_filename(self):
        """
        Check filename - does nothing for DrsInputFile - but classes that
        inherit from this use this method - note for DrsInputFile we
        cannot check filename - other than that it is set

        :return:
        """
        # set function name
        _ = display_func(self.params, 'check_filename', __NAME__, self.class_name)
        # check that filename isn't None
        if self.filename is None:
            func = self.__repr__()
            eargs = [func, func + '.set_filename()']
            self.__error__(TextEntry('00-001-00002', args=eargs))

    def file_exists(self) -> bool:
        """
        Check if filename exists (normally after check_filename is set)

        :return: True if file exists
        """
        # set function name
        _ = display_func(self.params, 'set_filename', __NAME__, self.class_name)
        # assume file does not exist
        found = False
        # if filename is set check filename exists
        if self.filename is not None:
            # if filename is string check filename exists
            if isinstance(self.filename, str):
                # update found
                found = os.path.exists(self.filename)
        # return whether file was found
        return found

    def set_params(self, params: ParamDict):
        """
        Set the associated parameter dictionary for the file

        :param params: ParamDict, the parameter dictionary of constants
        :return: None
        """
        # set function name
        _ = display_func(self.params, 'set_params', __NAME__, self.class_name)
        # set the params
        self.params = params

    def newcopy(self, name: Union[str, None] = None,
                filetype: Union[str, None] = None,
                suffix: Union[str, None] = None,
                remove_insuffix: bool = False,
                prefix: Union[str, None] = None,
                fibers: Union[List[str], None] = None,
                fiber: Union[str, None] = None,
                params: Union[ParamDict, None] = None,
                filename: Union[str, None] = None,
                intype: Any = None,
                path: Union[str, None] = None,
                basename: Union[str, None] = None,
                inputdir: Union[str, None] = None,
                directory: Union[str, None] = None,
                data: Union[np.ndarray, None] = None,
                header: Union[drs_fits.Header, None] = None,
                fileset: Union[list, None] = None,
                filesetnames: Union[List[str], None] = None,
                outfunc: Union[Any, None] = None,
                inext: Union[str, None] = None,
                dbname: Union[str, None] = None,
                dbkey: Union[str, None] = None,
                rkeys: Union[dict, None] = None,
                numfiles: Union[int, None] = None,
                shape: Union[int, None] = None,
                hdict: Union[drs_fits.Header, None] = None,
                output_dict: Union[OrderedDict, None] = None,
                datatype: Union[str, None] = None,
                dtype: Union[type, None] = None,
                is_combined: Union[bool, None] = None,
                combined_list: Union[list, None] = None,
                s1d: Union[list, None] = None,
                hkeys: Union[Dict[str, str], None] = None):
        """
        Create a new copy of DRS Input File object - unset parameters come
        from current instance of Drs Input File

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set function name
        _ = display_func(self.params, 'newcopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsInputFile, self, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    def check_params(self, func):
        """
        Check that params is set - if not return an error
        :return:
        """
        # set function name
        if func is not None:
            func_name = func
        else:
            func_name = display_func(self.params, 'check_params', __NAME__,
                                     self.class_name)
        # ---------------------------------------------------------------------
        # check that params isn't None
        if self.params is None:
            func = self.__repr__()
            eargs = [func, self.filename, func_name]
            self.__error__(TextEntry('00-001-00003', args=eargs))

    def __error__(self, messages: Union[TextEntry, str]):
        """
        Raise an Logger message (level = error)
        :param messages: TextEntry or string of the messages to add
        :return: None
        """
        # set function name
        _ = display_func(self.params, '__error__', __NAME__, self.class_name)
        # run the log method: error mode
        self.__log__(messages, 'error')

    def __warning__(self, messages: Union[TextEntry, str]):
        """
        Log a Logger message (level = warning)
        :param messages: TextEntry or string of the messages to add
        :return: None
        """
        # set function name
        _ = display_func(self.params, '__warning__', __NAME__, self.class_name)
        # run the log method: warning mode
        self.__log__(messages, 'warning')

    def __message__(self, messages: Union[TextEntry, str]):
        """
        Log a Logger message (level = '')
        :param messages: TextEntry or string of the messages to add
        :return:
        """
        # set function name
        _ = display_func(self.params, '__message__', __NAME__, self.class_name)
        # print and log via wlogger
        WLOG(self.params, '', messages)

    def __log__(self, messages: Union[TextEntry, str], kind: str):
        """
        Generate a logger message for level = kind
        :param messages: TextEntry or string of the messages to add
        :param kind: str, level of the log message
        :return:
        """
        # set function name
        _ = display_func(self.params, '__log__', __NAME__, self.class_name)
        # format initial error message
        m0args = [kind.capitalize(), self.__repr__()]
        message0 = TextEntry('{0}: {1}'.format(*m0args))
        # append initial error message to messages
        messages = message0 + messages
        # print and log via wlogger
        WLOG(self.params, kind, messages)

    def addset(self, drsfile: Any):
        """
        For generic Input files only
        Add to a list of associated drs files (fileset) and the names to
        filesetnames

        :param drsfile: DrsInputFile, DrsFitsFile etc, file instance to add to
                        file set
        :return:
        """
        # set function name
        _ = display_func(self.params, 'addset', __NAME__, self.class_name)
        # append drs file to file set
        self.fileset.append(drsfile)
        # apeend drs file name to file set name list
        self.filesetnames.append(drsfile.name)

    def copyother(self, drsfile, name: Union[str, None] = None,
                  filetype: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  remove_insuffix: bool = False,
                  prefix: Union[str, None] = None,
                  fibers: Union[List[str], None] = None,
                  fiber: Union[str, None] = None,
                  params: Union[ParamDict, None] = None,
                  filename: Union[str, None] = None,
                  intype: Any = None,
                  path: Union[str, None] = None,
                  basename: Union[str, None] = None,
                  inputdir: Union[str, None] = None,
                  directory: Union[str, None] = None,
                  data: Union[np.ndarray, None] = None,
                  header: Union[drs_fits.Header, None] = None,
                  fileset: Union[list, None] = None,
                  filesetnames: Union[List[str], None] = None,
                  outfunc: Union[Any, None] = None,
                  inext: Union[str, None] = None,
                  dbname: Union[str, None] = None,
                  dbkey: Union[str, None] = None,
                  rkeys: Union[dict, None] = None,
                  numfiles: Union[int, None] = None,
                  shape: Union[int, None] = None,
                  hdict: Union[drs_fits.Header, None] = None,
                  output_dict: Union[OrderedDict, None] = None,
                  datatype: Union[str, None] = None,
                  dtype: Union[type, None] = None,
                  is_combined: Union[bool, None] = None,
                  combined_list: Union[list, None] = None,
                  s1d: Union[list, None] = None,
                  hkeys: Union[Dict[str, str], None] = None):
        """
        Copy most keys from drsfile (other arguments override attributes coming
        from drfile (or self)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        """
        # set function name
        _ = display_func(self.params, 'copyother', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsInputFile, self, drsfile, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    def completecopy(self, drsfile,
                     name: Union[str, None] = None,
                     filetype: Union[str, None] = None,
                     suffix: Union[str, None] = None,
                     remove_insuffix: bool = False,
                     prefix: Union[str, None] = None,
                     fibers: Union[List[str], None] = None,
                     fiber: Union[str, None] = None,
                     params: Union[ParamDict, None] = None,
                     filename: Union[str, None] = None,
                     intype: Any = None,
                     path: Union[str, None] = None,
                     basename: Union[str, None] = None,
                     inputdir: Union[str, None] = None,
                     directory: Union[str, None] = None,
                     data: Union[np.ndarray, None] = None,
                     header: Union[drs_fits.Header, None] = None,
                     fileset: Union[list, None] = None,
                     filesetnames: Union[List[str], None] = None,
                     outfunc: Union[Any, None] = None,
                     inext: Union[str, None] = None,
                     dbname: Union[str, None] = None,
                     dbkey: Union[str, None] = None,
                     rkeys: Union[dict, None] = None,
                     numfiles: Union[int, None] = None,
                     shape: Union[int, None] = None,
                     hdict: Union[drs_fits.Header, None] = None,
                     output_dict: Union[OrderedDict, None] = None,
                     datatype: Union[str, None] = None,
                     dtype: Union[type, None] = None,
                     is_combined: Union[bool, None] = None,
                     combined_list: Union[list, None] = None,
                     s1d: Union[list, None] = None,
                     hkeys: Union[Dict[str, str], None] = None):
        """
        Copy all keys from drsfile (unless other arguments set - these override
        copy from drsfile)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        """
        # set function name
        _ = display_func(self.params, 'completecopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsInputFile, drsfile, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    # -------------------------------------------------------------------------
    # file checking
    # -------------------------------------------------------------------------
    def check_another_file(self, input_file: Union['DrsInputFile']
                           ) -> Tuple[bool, Union[TextEntry, str, dict, None]]:
        """
        Checks that another file is consistent with this file type

        :param input_file: DrsInputFile
        :returns: True or False and the reason why (if False)
        """
        # set function name
        _ = display_func(self.params, 'check_another_file', __NAME__,
                         self.class_name)
        # 1. check extension
        cond1, msg1 = self.has_correct_extension(input_file.inext)
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist(None)
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys(None)
        if not cond2:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def check_file(self) -> Tuple[bool, Union[TextEntry, str, dict, None]]:
        """
        Checks that this file is correct

        :returns: True or False and the reason why (if False)
        """
        # set function name
        _ = display_func(self.params, 'check_file', __NAME__, self.class_name)
        # 1. check extension
        cond1, msg1 = self.has_correct_extension()
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist()
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys()
        if not cond3:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def has_correct_extension(self, filename: Union[str, None] = None,
                              filetype: Union[str, None] = None,
                              argname: Union[str, None] = None
                              ) -> Tuple[bool, Union[str, TextEntry, None]]:
        """
        Placeholder - cannot check header for DrsInputFile

        :param filename: None or filename the filename to check (if None sets
                         this from self.filename [Not used in DrsInputFile]
        :param filetype: None or file type (extension) - if None sets from
                         self.filetype [Not used in DrsInputFile]
        :param argname: str, the name of the argument we are checking the
                        extension of [Not used in DrsInputFile]

        :return: True and no reason (None)
        """
        # set function name
        _ = display_func(self.params, 'has_correct_extension', __NAME__,
                         self.class_name)
        # do nothing
        _ = filename
        _ = filetype
        _ = argname
        # always return True and None (abstract placeholder)
        return True, None

    def hkeys_exist(self, header: Union[drs_fits.Header, None] = None,
                    filename: Union[str, None] = None,
                    argname: Union[str, None] = None) -> Tuple[bool, None]:
        """
        Placeholder - cannot check header for DrsInputFile
        always returns True and no error message

        :param header: drs_fits.Header - the header file to check
                       [Not used in DrsInputFile]
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename [Not used in DrsInputFile]
        :param argname: str, the name of the argument we are checking the
                        extension of [Not used in DrsInputFile]

        :return: True and no reason (None)
        """
        # set function name
        _ = display_func(self.params, 'hkeys_exist', __NAME__, self.class_name)
        # do nothing
        _ = filename
        _ = header
        _ = argname
        # always return True and None (abstract placeholder)
        return True, None

    def has_correct_hkeys(self, header: Union[drs_fits.Header, None] = None,
                          argname: Union[str, None] = None,
                          log: bool = True, filename: Union[str, None] = None,
                          ) -> Tuple[bool, Union[dict, None]]:
        """
        Placeholder - cannot check header for DrsInputFile

        :param header: drs_fits.Header - the header file to check
                       [Not used in DrsInputFile]
        :param argname: str, the name of the argument we are checking the
                        extension of [Not used in DrsInputFile]
        :param log: bool, log checking [Not used in DrsInputFile]
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename [Not used in DrsInputFile]
                         
        :return: True and no reason (None)
        """
        # set function name
        _ = display_func(self.params, 'has_correct_hkeys', __NAME__, self.class_name)
        # do nothing
        _ = filename
        _ = header
        _ = argname
        _ = log
        # always return True and None (abstract placeholder)
        return True, None

    # -------------------------------------------------------------------------
    # read/write methods
    # -------------------------------------------------------------------------
    def read_file(self, ext: Union[int, None] = None, check: bool = False,
                  copy: bool = False):
        """
        Does nothing - abstract at this point - cannot read a generic file

        :param ext: int or None, the data extension to open
        :param check: bool, if True checks if data is already read and does
                      not read again, to overwrite/re-read set "check" to False
        :param copy: bool, if True make sure data is copied to HDU (i.e. can
                     close after even if numpy array is still used) numpy
                     array is stored in DrsFitsFile.data
        :return None:
        """
        # set function name
        _ = display_func(self.params, 'read_file', __NAME__, self.class_name)
        # do nothing else (no current read option for generic input files)
        _ = ext
        _ = check
        _ = copy

    def write_file(self, kind: str,
                   runstring: Union[str, None] = None):
        """
        Does nothing - abstract at this point - cannot write a generic file

        :return: None
        """
        # set function name
        _ = display_func(self.params, 'write_file', __NAME__, self.class_name)
        # do nothing else (no current write option for generic input files)
        _ = kind, runstring

    # -------------------------------------------------------------------------
    # user functions
    # -------------------------------------------------------------------------
    def construct_filename(self, infile: Union['DrsInputFile', None] = None,
                           outfile: Union['DrsInputFile', None] = None,
                           fiber: Union[str, None] = None,
                           path: Union[str, None] = None,
                           func: Union[str, None] = None,
                           remove_insuffix: Union[bool, None] = None,
                           prefix: Union[str, None] = None,
                           suffix: Union[str, None] = None,
                           check: bool = True,
                           filename: Union[str, None] = None):
        """
        Constructs the filename from the parameters defined at instance
        definition and using the infile (if required). If check is True, checks
        the infile type against "intype". Uses "outfunc" in instance definition
        to set the suffices/prefixes/fiber etc

        :param infile: Drsfile, the input DrsFile
        :param outfile: DrsFitsFile, output file - must be defined
        :param fiber: str, the fiber - must be set if infile.fibers is populated
        :param path: str, the path the file should have (if not set, set to
                     params['OUTPATH']  with params['NIGHTNAME'] if set)
        :param func: str, the function name if set (for errors)
        :param remove_insuffix: bool if set removes input suffix if not set
                                defaults to the outfile.remove_insuffix
        :param prefix: str, if set the prefix of the file (defaults to
                       outfile.prefix)
        :param suffix: str, if set the suffix of the file (defaults to
                       outfile.suffix)
        :param filename: str or None, only used for specific out fcuntions
                         (like set_file)

        :param check: bool, whether to check infile.name against self.intype

        :return: None, Sets self.filename and self.basename to the
                       correct values
        """
        # set function name
        func_name = display_func(self.params, 'construct_filename', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # deal with not outfile
        if outfile is None:
            outfile = self
        # if we have a function use it
        if self.outfunc is not None:
            try:
                abspath = self.outfunc(params, infile, outfile, fiber, path,
                                       func, remove_insuffix, prefix, suffix,
                                       filename)
            except DrsCodedException as e:
                level = e.get('level', 'error')
                eargs = e.get('targs', None)
                WLOG(params, level, TextEntry(e.codeid, args=eargs))
                abspath = None

            self.filename = abspath
            self.basename = os.path.basename(abspath)
        # else raise an error
        else:
            eargs = [self.__repr__(), func_name]
            WLOG(params, 'error', TextEntry('00-008-00004', args=eargs))
        # check that we are allowed to use infile (if set)
        if infile is not None and check:
            if self.intype is not None:
                # get required names
                reqfiles = self.generate_reqfiles()
                reqstr = ' or '.join(reqfiles)
                # see if infile is in reqfiles
                if infile.name not in reqfiles:
                    eargs = [infile.name, reqstr, self.filename, func_name]
                    WLOG(params, 'error', TextEntry('00-008-00017', args=eargs))

    def generate_reqfiles(self) -> List[str]:
        """
        Takes DrsInputFile.intype and works out all the combinations of
        file names that are valid for this "intype" (i.e. if we have a
        fileset in one of the "intypes" we should add all files from this set)

        :return: list of DrsInputFile names (drsfile.name) to know which names
                 are valid
        :rtype list:
        """
        # set function name
        _ = display_func(self.params, 'generate_reqfiles', __NAME__,
                         self.class_name)
        # deal with intype being unset
        if self.intype is None:
            return []
        # set out list storage
        required_names = []
        # deal with having a list of files
        if isinstance(self.intype, list):
            # loop around intypes
            for intype in self.intype:
                # deal with intype having fileset (set of files associated
                #   with this file)
                if len(intype.filesetnames) != 0:
                    required_names += list(intype.filesetnames)
                    required_names.append(intype.name)
                else:
                    required_names.append(intype.name)
        elif isinstance(self.intype, DrsInputFile):
            intype = self.intype
            # deal with intype having fileset (set of files associated
            #   with this file)
            if len(intype.filesetnames) != 0:
                required_names += list(intype.filesetnames)
                required_names.append(intype.name)
            else:
                required_names.append(intype.name)
        # clean up required name list by only keeping unique names
        required_names = list(np.unique(required_names))
        # return required names
        return required_names

    def reconstruct_filename(self, outext: Union[str, None] = None,
                             prefix: Union[str, None] = None,
                             suffix: Union[str, None] = None,
                             inext: Union[str, None] = None,
                             fiber: Union[str, None] = None):
        """
        Reconstructs the output filename based on the current filename (that is
        then striped back to the original input file name) and then added
        based on the input settings

        remove is based on the current DrsInputFile.filename,
        DrsInputFile.basename, DrsInputFile.prefix, DrsInputFile.suffix,
        DrsInputFile.fiber, DrsInputFile.filetype

        :param outext: str, the outfile extension (to add)
        :param prefix: str, if set the prefix of the file
        :param suffix: str, if set the suffix of the file
        :param inext: str, the infile extension (to remove)
        :param fiber: str, the fiber to add (if set)

        :return: None, updates DrsInputFile.filename,  DrsInputFile.basename,
                 DrsInputFile.prefix, DrsInputFile.suffix, DrsInputFile.fiber,
                 DrsInputFile.inext
        """
        # set function name
        func_name = display_func(self.params, 'reconstruct_filename', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # get current path and filename
        currentpath = os.path.dirname(self.filename)
        currentfile = self.basename
        # ----------------------------------------------------------------------
        # deal with non set value
        if prefix is None:
            prefix = self.prefix
        if suffix is None:
            suffix = self.suffix
        if inext is None:
            inext = self.filetype
        if fiber is None:
            fiber = self.fiber
        # ----------------------------------------------------------------------
        # create infilename
        # ----------------------------------------------------------------------
        # remove inext
        if self.inext is not None and currentfile.endswith(self.inext):
            currentfile = currentfile[:-len(self.inext)]
        # remove fiber
        if self.fiber is not None and currentfile.endswith('_' + self.fiber):
            currentfile = currentfile[:-len('_' + self.fiber)]
        # remove prefix
        if self.prefix is not None and currentfile.startswith(self.prefix):
            currentfile = currentfile[len(self.prefix):]
        # remove suffix
        if self.suffix is not None and currentfile.endswith(self.suffix):
            currentfile = currentfile[:-len(self.suffix)]
        # add back the inext
        if inext is not None and not currentfile.endswith(inext):
            currentfile = currentfile + inext
        # ----------------------------------------------------------------------
        # get re-constructed out file name
        outfilename = outf.get_outfilename(params, currentfile, prefix, suffix,
                                           inext, outext, fiber)
        # ----------------------------------------------------------------------
        # update self
        self.prefix = prefix
        self.suffix = suffix
        self.inext = inext
        self.fiber = fiber
        self.filename = os.path.join(currentpath, outfilename)
        self.basename = outfilename


class DrsFitsFile(DrsInputFile):
    def __init__(self, name, filetype: str = '.fits',
                 suffix: str = '',
                 remove_insuffix: bool = False,
                 prefix: str = '',
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 directory: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outfunc: Union[Any, None] = None,
                 inext: Union[str, None] = '.fits',
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = 0,
                 shape: Union[tuple, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = 'image',
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = False,
                 combined_list: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None):
        """
        Create a DRS Input File object

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric)
        :param dbkey: str, the database key
        :param rkeys: dict, the required header keys
        :param numfiles: int, the number of files represented by this file
                         instance
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on writing
        :param output_dict: dict, storage for data going to index database
        :param datatype: str, the fits image type 'image' or 'header'
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits images)
        :param is_combined: bool, if True this file represents a combined set
                            of files
        :param combined_list: list, the list of combined files that make this
                              file instance
        :param s1d: list, a list of s1d images attached to this file instance
                    (for use with extraction file instances)

        :param hkeys: passed to required header keys (i.e. must be a DRS
                      Header key reference -- "KW_HEADERKEY")

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set class name
        self.class_name = 'DrsFitsFile'
        # set function name
        _ = display_func(params, '__init__', __NAME__, self.class_name)
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, filetype, suffix, remove_insuffix,
                              prefix, fibers, fiber, params, filename, intype,
                              path, basename, inputdir, directory, data, header,
                              fileset, filesetnames, outfunc, inext, dbname,
                              dbkey, rkeys, numfiles, shape, hdict,
                              output_dict, datatype, dtype, is_combined,
                              combined_list, s1d, hkeys)
        # if ext in kwargs then we have a file extension to check
        self.filetype = filetype
        # set the input extension type
        self.inext = inext
        # get the input type (another DrsFitsFile that was or will be used
        #   to create this one i.e. for pp intype is a raw drs fits file,
        #   for out intype is most likely a pp drs fits file)
        self.intype = intype
        # get fiber types allowed for this drs fits file
        self.fibers = fibers
        # get the specific fiber linked to this drs fits file
        self.fiber = fiber
        # get the function used for writing output file
        self.outfunc = outfunc
        # get the database name (only set if intended to go into a database)
        self.dbname = dbname
        # get the raw database key name (only set if intended to go into a
        #    database) - this is the one set in constants
        self.raw_dbkey = dbkey
        # get the current database key -- this can change i.e. adding of a
        #   fiber to the end -- for the default set key see raw_dbkey
        self.dbkey = None
        if dbkey is not None:
            self.dbkey = str(dbkey)
        # add required header keys storage
        if rkeys is None:
            self.required_header_keys = dict()
        else:
            self.required_header_keys = rkeys
        # if we don't have any required keys pushed in we get these using
        #   the get_header_keys method (kwargs is passed to allow setting
        #   individual keys when drs fits instance is constructed)
        if len(self.required_header_keys) == 0:
            self.get_header_keys(hkeys)
        # get the fits data array (or set it to None)
        self.data = data
        # get the fits header (or set it to None)
        self.header = header
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)
        # get the number of files associated with this drs fits file
        self.numfiles = numfiles
        # get the shape of the fits data array (self.data)
        self.shape = shape
        # get the hdict (header dictionary storage) that will be passed to
        #   self.header - if not passed this is set as an empty header
        #   kept separate from self.header until all keys are added
        #   (to allow clean up + checking to occur only once)
        if hdict is None:
            self.hdict = drs_fits.Header()
        else:
            self.hdict = hdict
        # get the storage dictionary for output parameters
        if output_dict is None:
            self.output_dict = OrderedDict()
        else:
            self.output_dict = output_dict
        # get the data type for this drs fits file (either image or table)
        if datatype is None:
            self.datatype = 'image'
        else:
            self.datatype = datatype
        # get the dtype internally for fits image files (i.e. float or int)
        self.dtype = None
        # get the data array (for multi-extension fits)
        self.data_array = None
        # get the header array (fro multi-extnesion fits)
        self.header_array = None
        # flag whether file is a combined file
        self.is_combined = is_combined
        if combined_list is None:
            self.combined_list = []
        else:
            self.combined_list = combined_list
        # list s1d files linked to this file
        if s1d is None:
            self.s1d = []
        else:
            self.s1d = s1d

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        Defines the str(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(self.params, '__str__', __NAME__, self.class_name)
        # return the string output
        return self.string_output()

    def __repr__(self) -> str:
        """
        Defines the print(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(self.params, '__repr__', __NAME__, self.class_name)
        # return the string output
        return self.string_output()

    def get_header_keys(self, hkeys: Union[Dict[str, str], None]):
        """
        The rest of the kwargs from dictionary, search for keys starting with
        "KW_" and push them into required_header_keys (these are used to
        identify which keys in a header are required for a fits file to be this
        file instance kind

        :param kwargs: dict, a dictionary where the values are header key values
                       to id this file instance (compared to a fits header)

        :return: None
        """
        # set function name
        _ = display_func(self.params, 'get_header_keys', __NAME__,
                         self.class_name)
        # deal with no hkeys
        if hkeys is None:
            hkeys = dict()
        # add values to the header
        for hkey in hkeys:
            if 'KW_' in hkey.upper():
                self.required_header_keys[hkey] = hkeys[hkey]

    def newcopy(self, name: Union[str, None] = None,
                filetype: Union[str, None] = None,
                suffix: Union[str, None] = None,
                remove_insuffix: bool = False,
                prefix: Union[str, None] = None,
                fibers: Union[List[str], None] = None,
                fiber: Union[str, None] = None,
                params: Union[ParamDict, None] = None,
                filename: Union[str, None] = None,
                intype: Any = None,
                path: Union[str, None] = None,
                basename: Union[str, None] = None,
                inputdir: Union[str, None] = None,
                directory: Union[str, None] = None,
                data: Union[np.ndarray, None] = None,
                header: Union[drs_fits.Header, None] = None,
                fileset: Union[list, None] = None,
                filesetnames: Union[List[str], None] = None,
                outfunc: Union[Any, None] = None,
                inext: Union[str, None] = None,
                dbname: Union[str, None] = None,
                dbkey: Union[str, None] = None,
                rkeys: Union[dict, None] = None,
                numfiles: Union[int, None] = None,
                shape: Union[int, None] = None,
                hdict: Union[drs_fits.Header, None] = None,
                output_dict: Union[OrderedDict, None] = None,
                datatype: Union[str, None] = None,
                dtype: Union[type, None] = None,
                is_combined: Union[bool, None] = None,
                combined_list: Union[list, None] = None,
                s1d: Union[list, None] = None,
                hkeys: Union[Dict[str, str], None] = None):
        """
        Create a new copy of DRS Input File object - unset parameters come
        from current instance of Drs Input File

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set function name
        _ = display_func(self.params, 'newcopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsFitsFile, self, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    def string_output(self) -> str:
        """
        String output for DrsFitsFile. If fiber is not None this also
        contains the fiber type

        i.e. DrsFitsFile[{name}_{fiber}] or DrsFitsFile[{name}]
        :return string: str, the string to print
        """
        # set function name
        _ = display_func(self.params, 'string_output', __NAME__, self.class_name)
        # if we don't have the fiber print the drs fits file string
        if self.fiber is None:
            return '{0}[{1}]'.format(self.class_name, self.name)
        # if we have the fiber add it and print the drs fits file string
        else:
            return '{0}[{1}_{2}]'.format(self.class_name, self.name, self.fiber)

    def set_required_key(self, key: str, value: Any):
        """
        Set a required key

        :param key: str, the key to set
        :param value: value to put into required keys rkeys[key] = value
        :return:
        """
        # set function name
        _ = display_func(self.params, 'set_required_key', __NAME__,
                         self.class_name)
        # if we have a keyword (prefix 'KW_')
        if 'KW_' in key:
            # set required header keys
            self.required_header_keys[key] = value

    def copyother(self, drsfile, name: Union[str, None] = None,
                  filetype: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  remove_insuffix: bool = False,
                  prefix: Union[str, None] = None,
                  fibers: Union[List[str], None] = None,
                  fiber: Union[str, None] = None,
                  params: Union[ParamDict, None] = None,
                  filename: Union[str, None] = None,
                  intype: Any = None,
                  path: Union[str, None] = None,
                  basename: Union[str, None] = None,
                  inputdir: Union[str, None] = None,
                  directory: Union[str, None] = None,
                  data: Union[np.ndarray, None] = None,
                  header: Union[drs_fits.Header, None] = None,
                  fileset: Union[list, None] = None,
                  filesetnames: Union[List[str], None] = None,
                  outfunc: Union[Any, None] = None,
                  inext: Union[str, None] = None,
                  dbname: Union[str, None] = None,
                  dbkey: Union[str, None] = None,
                  rkeys: Union[dict, None] = None,
                  numfiles: Union[int, None] = None,
                  shape: Union[int, None] = None,
                  hdict: Union[drs_fits.Header, None] = None,
                  output_dict: Union[OrderedDict, None] = None,
                  datatype: Union[str, None] = None,
                  dtype: Union[type, None] = None,
                  is_combined: Union[bool, None] = None,
                  combined_list: Union[list, None] = None,
                  s1d: Union[list, None] = None,
                  hkeys: Union[Dict[str, str], None] = None):
        """
        Copy most keys from drsfile (other arguments override attributes coming
        from drfile (or self)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param kwargs: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        """
        # set function name
        func_name = display_func(self.params, 'copyother', __NAME__,
                                 self.class_name)
        # check params has been set
        self.check_params(func_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsFitsFile, self, drsfile, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    def completecopy(self, drsfile,
                     name: Union[str, None] = None,
                     filetype: Union[str, None] = None,
                     suffix: Union[str, None] = None,
                     remove_insuffix: bool = False,
                     prefix: Union[str, None] = None,
                     fibers: Union[List[str], None] = None,
                     fiber: Union[str, None] = None,
                     params: Union[ParamDict, None] = None,
                     filename: Union[str, None] = None,
                     intype: Any = None,
                     path: Union[str, None] = None,
                     basename: Union[str, None] = None,
                     inputdir: Union[str, None] = None,
                     directory: Union[str, None] = None,
                     data: Union[np.ndarray, None] = None,
                     header: Union[drs_fits.Header, None] = None,
                     fileset: Union[list, None] = None,
                     filesetnames: Union[List[str], None] = None,
                     outfunc: Union[Any, None] = None,
                     inext: Union[str, None] = None,
                     dbname: Union[str, None] = None,
                     dbkey: Union[str, None] = None,
                     rkeys: Union[dict, None] = None,
                     numfiles: Union[int, None] = None,
                     shape: Union[int, None] = None,
                     hdict: Union[drs_fits.Header, None] = None,
                     output_dict: Union[OrderedDict, None] = None,
                     datatype: Union[str, None] = None,
                     dtype: Union[type, None] = None,
                     is_combined: Union[bool, None] = None,
                     combined_list: Union[list, None] = None,
                     s1d: Union[list, None] = None,
                     hkeys: Union[Dict[str, str], None] = None):
        """
        Copy all keys from drsfile (unless other arguments set - these override
        copy from drsfile)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param directory: string, the aboslute path of the file without the
                          filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param kwargs: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        """
        # set function name
        _ = display_func(self.params, 'completecopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsFitsFile, drsfile, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    # -------------------------------------------------------------------------
    # file checking
    # -------------------------------------------------------------------------
    def check_file(self) -> Tuple[bool, Union[TextEntry, dict, str, None]]:
        """
        Checks that this file is correct

        :returns: True or False and the reason why (if False)
        """
        # set function name
        _ = display_func(self.params, 'check_file', __NAME__, self.class_name)
        # 1. check extension
        cond1, msg1 = self.has_correct_extension()
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist()
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys()
        if not cond3:
            return False, msg3
        # 4. check if we have a fiber defined
        self.has_fiber()
        # if 1, 2 and 3 pass return True
        return True, None

    def has_correct_extension(self, filename: Union[str, None] = None,
                              filetype: Union[str, None] = None,
                              argname: Union[str, None] = None
                              ) -> Tuple[bool, Union[str, TextEntry, None]]:
        """
        Check whether the filetype (file extension) is correct

        :param filename: None or filename the filename to check (if None sets
                         this from self.filename
        :param filetype: None or file type (extension) - if None sets from
                         self.filetype
        :param argname: str, the name of the argument we are checking the
                        extension of

        :return: True or False for correct extension and the reason why if False
        """
        # set function name
        func_name = display_func(self.params, 'has_correct_extension', __NAME__,
                                 self.class_name)
        # deal with no input extension
        if filetype is None:
            filetype = self.filetype
        # deal with no input filename
        if filename is None:
            filename = self.filename
            basename = self.basename
        else:
            basename = os.path.basename(filename)
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = TextEntry('40-001-00018')
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # get parameters
        params = self.params
        # -----------------------------------------------------------------
        # check extension
        if filetype is None:
            msg = TextEntry('09-000-00003', args=[basename])
            cond = True
        elif filename.endswith(filetype):
            msg = TextEntry('09-000-00004', args=[basename, filetype])
            cond = True
        else:
            msg = TextEntry('09-000-00005', args=[basename, filetype])
            cond = False
        # if valid return True and no error
        if cond:
            dargs = [argname, os.path.basename(filename)]
            WLOG(params, 'debug', TextEntry('90-001-00009', args=dargs),
                 wrap=False)
            return True, msg
        # if False generate error and return it
        else:
            emsg = TextEntry('09-001-00006', args=[argname, filetype])
            return False, emsg

    def hkeys_exist(self, header: Union[drs_fits.Header, None] = None,
                    filename: Union[str, None] = None,
                    argname: Union[str, None] = None
                    ) -> Tuple[bool, Union[str, TextEntry, None]]:
        """
        Check whether the header keys exist in the header

        :param header: drs_fits.Header - the header file to check
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename
        :param argname: str, the name of the argument we are checking the
                        extension of

        :return: True or False for correct header keys and the reason why
                 if False
        """
        # set function name
        func_name = display_func(self.params, 'hkeys_exist', __NAME__,
                                 self.class_name)
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True)
            # get header
            header = self.header
        # deal with no input filename
        if filename is None:
            basename = self.basename
        else:
            basename = os.path.basename(filename)
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # get parameters
        params = self.params
        pconst = constants.pload(self.params['INSTRUMENT'])
        # get the list of allowed required header keys
        allowed_keys = pconst.FILEDEF_HEADER_KEYS()
        # get the required header keys
        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = TextEntry('40-001-00018')
        # -----------------------------------------------------------------
        # Check that required keys are in header
        for drskey in rkeys:
            # check we are allowed to use this key (by instrument definition)
            if drskey not in allowed_keys:
                eargs = [self.name, drskey, 'FILEDEF_HEADER_KEYS()',
                         ','.join(allowed_keys), func_name]
                WLOG(params, 'error', TextEntry('00-006-00022', args=eargs))
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
                source = params.sources[drskey]
            else:
                key = drskey
                source = func_name
            # deal with empty key
            if (key is None) or key == '':
                eargs = [key, drskey, source]
                WLOG(params, 'error', TextEntry('00-006-00011', args=eargs))
            # check if key is in header
            if key not in header:
                eargs = [argname, key]
                emsg = TextEntry('09-001-00007', args=eargs)
                WLOG(params, 'debug', emsg)
                return False, emsg
            else:
                dargs = [argname, key, basename]
                WLOG(params, 'debug', TextEntry('90-001-00010', args=dargs),
                     wrap=False)
        # if we have got to this point return True (success) and no error
        #   messages
        return True, None

    def has_correct_hkeys(self, header: Union[drs_fits.Header, None] = None,
                          argname: Union[str, None] = None,
                          log: bool = True, filename: Union[str, None] = None,
                          ) -> Tuple[bool, Dict[str, tuple]]:
        """
        Check whether the header keys exist in the header

        :param header: drs_fits.Header - the header file to check
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename
        :param argname: str, the name of the argument we are checking the
                        extension of
        :param log: bool, if True logs that we have correct keys

        :return: True or False for correct header keys and the reason why
                 if False, and a dictionary of header keywords where each value
                 is in the form of a tuple: (found, argname, rvalue, value)
                 where
                 - found is True or False (whether header key was found)
                 - argname is a str, the argument name this belongs to
                 - rvalue is the required value (fails if incorrect)
                 - value is value in the header
        """
        # set function name
        func_name = display_func(self.params, 'has_correct_hkeys', __NAME__,
                                 self.class_name)
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # get parameters
        params = self.params
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True)
            # get header
            header = self.header
            # get file
            filename = self.filename
        # get short hand to required header keys
        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = TextEntry('40-001-00018')
        # -----------------------------------------------------------------
        # search for correct value for each header key
        found = True
        # storage
        errors = dict()
        # -----------------------------------------------------------------
        # loop around required keys
        for drskey in rkeys:
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
            else:
                key = drskey
            # check that key is in header
            if key not in header:
                ekwargs = dict(level='error', key=key, filename=filename)
                emsg = 'Key "{0}" not found'
                raise DrsHeaderError(emsg.format(key), **ekwargs)
            # get value and required value
            value = header[key].strip()
            rvalue = rkeys[drskey].strip()
            # check if key is valid
            if rvalue != value:
                dargs = [argname, key, rvalue]
                if log:
                    WLOG(params, 'debug', TextEntry('90-001-00011', args=dargs),
                         wrap=False)
                found = False
            else:
                dargs = [argname, key, rvalue]
                if log:
                    WLOG(params, 'debug', TextEntry('90-001-00012', args=dargs),
                         wrap=False)
            # store info
            errors[key] = (found, argname, rvalue, value)
        # return found (bool) and errors
        return found, errors

    def has_fiber(self, header: Union[drs_fits.Header, None] = None):
        """
        Checks for fiber key in header and sets self.fiber based on this key
        if fiber key not found in header self.fiber is None

        :param header: drs_fits.Header - the header file to check
        :return: None
        """
        # set function name
        func_name = display_func(self.params, 'has_fiber', __NAME__,
                                 self.class_name)
        # -----------------------------------------------------------------
        # check whether fiber already set (in which case ignore)
        if self.fiber is not None:
            return
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True)
            # get header
            header = self.header
        # get parameters
        params = self.params
        # -----------------------------------------------------------------
        kw_fiber = params['KW_FIBER'][0]
        # -----------------------------------------------------------------
        # deal with fiber
        if kw_fiber in self.header:
            fiber = header[kw_fiber]
        else:
            fiber = None
        # update fiber value
        if fiber is not None:
            self.fiber = fiber

    # -------------------------------------------------------------------------
    # table checking
    # -------------------------------------------------------------------------
    # TODO: this function needs to change when using checksum
    def get_infile_outfilename(self, recipename: str,
                               infilename: Union[str, Path],
                               allowfibers: Union[List[str], str, None] = None,
                               ext: Union[str, None] = '.fits'
                               ) -> Tuple['DrsFitsFile', bool, Union[str, None]]:
        """
        Get the DrsFitsFile.intype DrsFitsFile output instance based on the
        infilename (string) and whether it is valid infilename for the intype
        i.e. if intype = ppfile  then infilename should be a pp file

        :param recipename: string, the recipe name (for error handling)
        :param infilename: string, the input file to use to create the output
                           filename
        :param allowfibers: list of strings or string, the fiber or fibers
                            allowed for the output file created
        :param ext: string, the input file filetype (i.e. a fits file)
        :returns: a tuple of three things, 1. the output DrsFitsFile instance,
                  2. whether infilename was valid for the given input file
                  (if False output DrsFitsFile may be None) 3. the output
                  filename generated (also in output DrsFitsFile.filename)
        """
        # set function name
        func_name = display_func(self.params, 'get_infile_outfilename',
                                 __NAME__, self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # ------------------------------------------------------------------
        # 1. need to assign an input type for our raw file
        if self.intype is not None:
            # deal with in type being list
            if isinstance(self.intype, list):
                intype = self.intype[0]
            else:
                intype = self.intype
            # get new copy
            infile = intype.newcopy(params=params)
        else:
            infile = DrsFitsFile('DRS_RAW_TEMP')
        # ------------------------------------------------------------------
        # storage of files
        chain_files = []
        # need to go back through the file history and update filename
        cintype = self.completecopy(infile)
        # loop until we have no intype (raw file)
        while cintype is not None:
            # add to chain
            chain_files.append(self.completecopy(cintype))
            if hasattr(cintype, 'intype'):
                # deal with in type being list
                if isinstance(cintype.intype, list):
                    cintype = cintype.intype[0]
                else:
                    cintype = cintype.intype
            else:
                break
        # ------------------------------------------------------------------
        # set the file name to the infilename
        filename = str(infilename)
        bottomfile = chain_files[-1]
        # now we have chain we can project file (assuming last element in the
        #   chain is the raw file)
        for cintype in chain_files[::-1][1:]:
            bottomfile.filename = filename
            bottomfile.basename = os.path.basename(filename)
            # check whether we need fiber
            if bottomfile.fibers is not None:
                fiber = allowfibers
            else:
                fiber = None
            # make sure cintype has params
            cintype.params = params
            # get out file name
            out = cintype.check_table_filename(recipename, bottomfile,
                                               fullpath=True,
                                               allowedfibers=fiber)
            valid, outfilename = out
            # set the filename to the outfilename
            filename = outfilename
            bottomfile = cintype
        # ------------------------------------------------------------------
        # add values to infile
        infile.filename = filename
        infile.basename = os.path.basename(filename)
        infile.filetype = ext
        # ------------------------------------------------------------------
        # get outfilename (final)
        valid, outfilename = self.check_table_filename(recipename, infile,
                                                       allowfibers)
        # ------------------------------------------------------------------
        # return infile
        return infile, valid, outfilename

    def check_table_filename(self, recipename: str,
                             infile: 'DrsFitsFile',
                             allowedfibers: Union[List[str], str, None] = None,
                             fullpath: bool = False
                             ) -> Tuple[bool, Union[str, None]]:
        """
        Checks whether an "infile" (DrsFitsFile) is the same kind as this
        DrsFitsFile and returns the output filename (based on infile.filename)

        :param recipename: str, the recipe where this function was called
        :param infile: DrsFitsFile, the FitsFile instance to check
        :param allowedfibers: list of strings or string, the fiber or fibers
                            allowed for the output file created
        :param fullpath: bool, if True returns the absolute path, else returns
                         just the filename

        :return: tuple of length 2, 1. whether the infile is valid, 2.
                 the output path of the infile (if infile is valid else None)
        """
        # set function name
        func_name = display_func(self.params, 'check_table_filename', __NAME__,
                                 'DrsFitsFile')
        # get parameters
        self.check_params(func_name)
        params = self.params
        # ------------------------------------------------------------------
        # deal with fibers
        if allowedfibers is not None:
            if isinstance(allowedfibers, str):
                fibers = [allowedfibers]
            else:
                fibers = list(allowedfibers)
        elif self.fibers is None:
            fibers = [None]
        else:
            fibers = self.fibers
        # set initial value of out filename
        outfilename = infile.filename
        # loop around fibers
        for fiber in fibers:
            # 2. need to assign an output filename for out file
            if self.outfunc is not None:
                try:
                    outfilename = self.outfunc(params, infile=infile,
                                               outfile=self, fiber=fiber)
                except DrsCodedException as e:
                    level = e.get('level', 'error')
                    eargs = e.get('targs', None)
                    WLOG(params, level, TextEntry(e.codeid, args=eargs))
                    outfilename = None
            else:
                eargs = [self.name, recipename, func_name]
                WLOG(params, 'error', TextEntry('09-503-00009', args=eargs))
                outfilename = None
        # ------------------------------------------------------------------
        # assume file is valid
        valid = True
        # ------------------------------------------------------------------
        # check extension
        if outfilename.endswith(self.filetype):
            # remove extension to test suffix
            filename = outfilename[:-len(self.filetype)]
        else:
            filename = None
            valid = False
            # debug log that extension was incorrect
            dargs = [self.filetype, filename]
            WLOG(params, 'debug', TextEntry('90-008-00004', args=dargs))
        # ------------------------------------------------------------------
        # check suffix (after extension removed)
        if (self.suffix is not None) and valid:
            # if we have no fibers file should end with suffix
            if fibers == [None]:
                if not filename.endswith(self.suffix):
                    valid = False
                    # debug log that extension was incorrect
                    dargs = [self.suffix, filename]
                    WLOG(params, 'debug', TextEntry('90-008-00005', args=dargs))
            # ------------------------------------------------------------------
            # if we have fibers then file should end with one of them and
            # the suffix
            elif len(fibers) > 0:
                # have to set up a new valid that should be True if any
                #  fiber is present
                valid1 = False
                # loop around fibers
                for fiber in fibers:
                    if filename.endswith('{0}_{1}'.format(self.suffix, fiber)):
                        valid1 |= True
                # if valid1 is False debug log that fibers were not found
                if not valid1:
                    dargs = [', '.join(fibers), filename]
                    WLOG(params, 'debug', TextEntry('90-008-00006', args=dargs))
                # put valid1 back into valid
                valid &= valid1
        # ------------------------------------------------------------------
        # return valid (True if filename is valid False otherwise)
        if fullpath:
            return valid, outfilename
        else:
            return valid, os.path.basename(outfilename)

    def check_table_keys(self, filedict: dict,
                         rkeys: Union[dict, None] = None) -> bool:
        """
        Checks whether a dictionary contains the required key/value pairs
        to belong to this DrsFile

        :param filedict: dictionary, the dictionary of key/value pairs to
                         check against rkeys (or DrsFitsFile.rkeys if unset)
        :param rkeys: dictionary or None, if set use this as DrsFitsFile.rkeys

        :return: bool, True if dictionary of keys is valid for DrsFitsFile.rkeys
        """
        # set function name
        func_name = display_func(self.params, 'check_table_keys', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # ------------------------------------------------------------------
        # get required keys
        if rkeys is None:
            rkeys = self.required_header_keys
        # assume file is valid
        valid = True
        # loop around required keys
        for key in rkeys:
            # key needs to be in table
            if key in filedict:
                # get rvalue
                rvalues = rkeys[key]
                # check if rvalue is list
                if isinstance(rvalues, str):
                    rvalues = [rvalues]
                # set up aux valid
                valid1 = False
                # loop around
                for rvalue in rvalues:
                    # get this value
                    filedictvalue = filedict[key]
                    # deal with null values
                    if filedictvalue in [None, 'None', '']:
                        valid1 |= True
                        continue
                    # make sure there are no white spaces and all upper case
                    if isinstance(filedictvalue, str):
                        filedictvalue = filedictvalue.strip().upper()
                    # else make sure there are no end white spaces and all
                    #   upper case for the required value
                    rvalueclean = rvalue.strip().upper()
                    # if key is in file dictionary then we should check it
                    if filedictvalue == rvalueclean:
                        valid1 |= True
                # modify valid value
                valid &= valid1
                dargs = [key, valid, filedict['OUT'], rvalues]
                WLOG(params, 'debug', TextEntry('90-008-00003', args=dargs))
                # if we haven't found a key the we can stop here
                if not valid:
                    return False
            else:
                # Log that key was not found
                dargs = [key, filedict['OUT'], ', '.join(list(filedict.keys()))]
                WLOG(params, 'debug', TextEntry('90-008-00002', args=dargs))
        # return valid
        return valid

    # -------------------------------------------------------------------------
    # fits file methods
    # -------------------------------------------------------------------------
    def read_file(self, ext: Union[int, None] = None, check: bool = False,
                  copy: bool = False):
        """
        Read this fits file data and header

        :param ext: int or None, the data extension to open
        :param check: bool, if True checks if data is already read and does
                      not read again, to overwrite/re-read set "check" to False
        :param copy: bool, if True make sure data is copied to HDU (i.e. can
                     close after even if numpy array is still used) numpy
                     array is stored in DrsFitsFile.data (slower but safer)

        :return None:
        """
        # set function name
        _ = display_func(self.params, 'read_file', __NAME__, self.class_name)
        # check if we have data set
        if check:
            cond1 = self.data is not None
            cond2 = self.header is not None
            if cond1 and cond2:
                return True
        # deal with no extension
        if (ext is None) and (self.datatype == 'image'):
            ext = 0
        elif ext is None:
            ext = 1
        # get params
        params = self.params
        # check that filename is set
        self.check_filename()

        # get data format
        if self.datatype == 'image':
            fmt = 'fits-image'
        elif self.datatype == 'table':
            fmt = 'fits-table'
        # default to fits-image
        else:
            fmt = 'fits-image'
        # read the fits file
        out = drs_fits.readfits(params, self.filename, getdata=True,
                                gethdr=True, fmt=fmt, ext=ext)
        # deal with copying
        if copy:
            if self.datatype == 'table':
                self.data = Table(out[0])
            else:
                self.data = np.array(out[0])
        else:
            self.data = out[0]
        self.header = drs_fits.Header.from_fits_header(out[1])
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)
        # set number of data sets to 1
        self.numfiles = 1
        # set the shape
        if (self.data is not None) and (self.datatype == 'image'):
            self.shape = self.data.shape
        elif self.data is not None:
            self.shape = [len(self.data)]

    # TODO: when we change to default ext=1 this needs updating
    def read_data(self, ext: int = 0, log: bool = True,
                  copy: bool = False):
        """
        Read an image from DrsFitsFile.filename into DrsFitsFile.data

        :param ext: int, the extension to read
        :param log: bool, if True logs that file was read (via
                    drs_fits.readfits)
        :param copy: bool, if True copieds the data before setting it (allows
                     HDU to be closed when opening many files (slower but
                     safer)
        :return: None
        """
        # set function name
        _ = display_func(self.params, 'read_data', __NAME__, self.class_name)
        # check that filename is set
        self.check_filename()
        # get params
        params = self.params
        # get data
        data = drs_fits.readfits(params, self.filename, ext=ext, log=log)
        # set number of data sets to 1
        self.numfiles = 1
        # assign to object
        if copy:
            if self.datatype == 'table':
                return Table(self.data)
            else:
                return np.array(self.data)
        else:
            self.data = data
        # set shape
        if hasattr(self.data, 'shape'):
            self.shape = self.data.shape
        else:
            self.shape = None

    def read_header(self, ext: Union[int, None] = None, log: bool = True,
                    copy: bool = False):
        """
        Read a header from DrsFitsFile.filename into DrsFitsFile.header

        :param ext: int, the extension to read
        :param log: bool, if True logs that file was read (via
                    drs_fits.readfits)
        :param copy: bool, if True copieds the header before setting it (allows
                     HDU to be closed when opening many files (slower but
                     safer)
        :return: None
        """
        # set function name
        _ = display_func(self.params, 'read_header', __NAME__, self.class_name)
        # check that filename is set
        self.check_filename()
        # deal with no extension
        if (ext is None) and (self.datatype == 'image'):
            ext = 0
        elif ext is None:
            ext = 1
        # get params
        params = self.params
        # get header
        header = drs_fits.read_header(params, self.filename, ext=ext, log=log)
        # assign to object
        if copy:
            self.header = drs_fits.Header(header)
        else:
            self.header = header
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)

    def check_read(self, header_only: bool = False, data_only: bool = False,
                   load: bool = True):
        """
        Check whether data and header (from a fits file) have been read
        if load is True and they haven't been read them read them

        data is loaded into DrsFitsFile.data
        header is loaded into DrsFitsFile.header

        :param header_only: bool, if True only read/check header
        :param data_only: bool, if True only read/check data
        :param load: bool, if True load header and / or data

        :return: None
        """
        # set function name
        _ = display_func(self.params, 'check_read', __NAME__, self.class_name)
        # ---------------------------------------------------------------------
        # deal with header only
        # ---------------------------------------------------------------------
        # deal with only wanting to check if header is read
        if header_only:
            if self.header is None:
                if load:
                    return self.read_header()
                # raise exception
                func = self.__repr__()
                eargs = [func, func + '.read_file()']
                self.__error__(TextEntry('00-001-00004', args=eargs))
                return 0
            else:
                return 1
        # ---------------------------------------------------------------------
        # deal with data only
        # ---------------------------------------------------------------------
        if data_only:
            if self.data is None:
                if load:
                    return self.read_data()
                # raise exception
                func = self.__repr__()
                eargs = [func, func + '.read_file()']
                self.__error__(TextEntry('00-001-00004', args=eargs))
                return 0
            else:
                return 1
        # ---------------------------------------------------------------------
        # deal with both data and header
        # ---------------------------------------------------------------------
        if self.header is None and self.data is None:
            self.read_file()
            return 1
        if self.header is None:
            self.read_header()
            return 1
        if self.data is None:
            self.read_data()
            return 1
        # if we get here we are good - both data and read are loaded
        return 1

    def get_data(self, copy: bool = False) -> Union[np.ndarray, Table, None]:
        """
        return the data array

        :param copy: bool, if True deep copies the data
        :return: the data (numpy array)
        """
        # set function name
        _ = display_func(self.params, 'get_data', __NAME__, self.class_name)
        # check data exists
        if self.data is None:
            self.check_read(data_only=True)
        # deal with copying data
        if copy:
            if self.datatype == 'table':
                return Table(self.data)
            else:
                return np.array(self.data)
        else:
            return self.data

    def get_header(self, copy: bool = False) -> Union[drs_fits.Header, None]:
        """
        return the header

        :param copy: bool, if True deep copies the header
        :return: the header (drs_fits.Header)
        """
        # set function name
        _ = display_func(self.params, 'get_header', __NAME__, self.class_name)
        # check header exists
        if self.header is None:
            self.check_read(header_only=True)
        # deal with copying header
        if copy:
            return self.header.copy()
        else:
            return self.header

    def read_multi(self, ext: Union[int, None] = None,
                   check: bool = False) -> Union[bool, None]:
        """
        Read multiple extensions from a fits file
        sets the primary ext to DrsFitsFile.data and additional ones to
        DrsFitsFile.data_array
        and similarly primary header to DrsFitsFile.header and additional ones
        to DrsfitsFile.header_array

        :param ext: int or None, the primary extension
        :param check: if True this is just a check that DrsFitsFile.data and
                      DrsFitsFile.header exist
        :return: normally just sets DrsFitsFile attributes, but if check is True
                 returns bool, True if data/header are set, False otherwise
        """
        # set function name
        _ = display_func(self.params, 'read_multi', __NAME__, self.class_name)
        # check if we have data set
        if check:
            cond1 = self.data is not None
            cond2 = self.header is not None
            if cond1 and cond2:
                return True
            else:
                return False
        # get params
        params = self.params
        # check that filename is set
        self.check_filename()
        # get data format
        if ext is not None:
            out = drs_fits.readfits(params, self.filename, getdata=True,
                                    ext=ext, gethdr=True,
                                    fmt='fits-image')
        else:
            out = drs_fits.readfits(params, self.filename, getdata=True,
                                    gethdr=True, fmt='fits-multi')
        self.data = out[0][0]
        self.header = drs_fits.Header.from_fits_header(out[1][0])
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)

        self.data_array = out[0]
        # set number of data sets to 1
        self.numfiles = 1
        # append headers (as copy)
        self.header_array = []
        for header in out[1]:
            self.header_array.append(drs_fits.Header.from_fits_header(header))
        # set the shape
        if self.data is not None:
            self.shape = self.data.shape

    def update_header_with_hdict(self):
        """
        Updates header with hdict entries
        :return:
        """

        # set function name
        _ = display_func(self.params, 'update_header_with_hdict', __NAME__,
                         self.class_name)
        # deal with unset header
        if self.header is None:
            if isinstance(self.hdict, drs_fits.Header):
                self.header = self.hdict.copy()
                return
            self.header = drs_fits.Header()
        # add keys from hdict
        for key in self.hdict:
            # deal with COMMENT cards
            if isinstance(self.hdict[key], HCC):
                self.header[key] = (self.hdict[key][0],
                                    self.hdict.comments[key][0])
            # just set them to  header[key] = (VALUE, COMMENT)
            else:
                self.header[key] = (self.hdict[key], self.hdict.comments[key])

    def write_file(self, kind: str,
                   runstring: Union[str, None] = None):
        """
        Write a single Table/numpy array to disk useing DrsFitsFile.data,
        DrsFitsfile.header to write to DrsFitsFile.filename

        also used to update output_dictionary for index database

        :param kind: str, the kind of file (raw, tmp, red)
        :param runstring: str or None, if set sets the input run string that
                          can be used to re-run the recipe to get this output

        :return: None
        """
        # set function name
        func_name = display_func(self.params, 'write_file', __NAME__,
                                 self.class_name)
        # get params
        params = self.params
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # copy keys from hdict into header
        self.update_header_with_hdict()
        # write to file
        drs_fits.writefits(params, self.filename, self.data, self.header,
                           self.datatype, self.dtype, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary(kind, runstring)

    def write_multi(self, kind: str, data_list: List[Union[Table, np.ndarray]],
                    header_list: Union[List[drs_fits.Header], None] = None,
                    datatype_list: Union[List[str], None] = None,
                    dtype_list: Union[List[Union[Type, None]], None] = None,
                    runstring: Union[str, None] = None):
        """
        Write a set of Tables/numpy arrays to disk useing DrsFitsFile.data,
        DrsFitsfile.header to write to DrsFitsFile.filename
        also requires a list of addition numpy arrays/Tables (and optionally
        a list of headers) - must supply data_type list if a mix of numpy
        array and Tables (defaults to all being numpy arrays --> FitsImage)

        also used to update output_dictionary for index database

        :param kind: str, the kind of file (raw, tmp, red)
        :param data_list: list of numpy arrays or astropy Tables - MUST NOT
                          INCLUDE first entry (set by DrsFitsFile.data)
                          if all are numpy arrays do not need to set
                          datatype_list if mixed or Table then must set
        :param header_list: optional list of headers (not including primary
                            this is set by DrsFitsFile.header) if not set
                            these are the same as DrsFitsFile.header
        :param datatype_list: list of strings (or unset) these can either be
                              'image' or 'table' and must be set for each
                            numpy array / table in the list (must be same length
                            as data list)
        :param dtype_list: list of types - if set tries to force each extension
                           to this data type (only works for numpy arrays)
                           set individual elements to None if you don't want
                           to force data type for that entry
        :param runstring: str or None, if set sets the input run string that
                          can be used to re-run the recipe to get this output

        :return: None
        """
        # set function name
        func_name = display_func(self.params, 'write_multi', __NAME__,
                                 self.class_name)
        # get params
        params = self.params
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # copy keys from hdict into header
        self.update_header_with_hdict()
        # ---------------------------------------------------------------------
        # deal with header list being empty
        if header_list is None:
            header_list = []
            for it in range(len(data_list)):
                if self.header is not None:
                    header_list.append(self.header.to_fits_header())
                else:
                    header_list.append(None)
        # deal with datatype_list being empty
        if datatype_list is None:
            datatype_list = []
            for it in range(len(data_list)):
                if isinstance(data_list[it], Table):
                    datatype_list.append('table')
                else:
                    datatype_list.append('image')
        # deal with dtype being empty
        if dtype_list is None:
            dtype_list = [None] * len(data_list)
        # ---------------------------------------------------------------------
        # get data and header lists
        data_list = [self.data] + data_list
        header_list = [self.header] + header_list
        datatype_list = [self.datatype] + datatype_list
        dtype_list = [self.dtype] + dtype_list
        # writefits to file
        drs_fits.writefits(params, self.filename, data_list, header_list,
                           datatype_list, dtype_list, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary(kind, runstring)

    def get_fiber(self, header: Union[drs_fits.Header, None] = None
                  ) -> Union[str, None]:
        """
        Get the fiber from the header (if it exists) - if not forcing header
        header must be loaded before using this

        :param header: None (uses DrsFitsFile.header) or force a different
                       header
        :return: str or None - if found in header returns the fiber name else
                 returns None
        """
        # set function name
        _ = display_func(self.params, 'get_fiber', __NAME__, self.class_name)
        # get params
        params = self.params
        # must have fibers defined to be able to get a fiber
        if self.fibers is None:
            return None
        # get fiber header key
        key = params['KW_FIBER'][0]
        # deal with case where no header was given
        if header is None:
            if self.header is not None:
                if key in self.header:
                    return str(self.header[key])
        else:
            if key in header:
                return str(header[key])
        # if we still don't have fiber search in file name for fiber
        for fiber in self.fibers:
            if '_{0}'.format(fiber) in self.basename:
                return fiber
        # if we still don't have fiber then return None
        return None

    def output_dictionary(self, kind: str, runstring: Union[str, None] = None):
        """
        Generate the output dictionary (for use while writing)
        Uses OUTPUT_FILE_HEADER_KEYS and DrsFile.hdict to generate an
        output dictionary for this file (for use in indexing)

        Requires DrsFile.filename and DrsFile.params to be set

        :return None:
        """
        # set function name
        func_name = display_func(self.params, 'output_dictionary', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        params = self.params
        pconst = constants.pload(params['INSTRUMENT'])
        # get required keys for index database
        hkeys, htypes = pconst.INDEX_HEADER_KEYS()
        # deal with absolute path of file
        self.output_dict['PATH'] = str(self.filename)
        # deal with night name of file
        self.output_dict['DIRECTORY'] = str(self.params['NIGHTNAME'])
        # deal with basename of file
        self.output_dict['FILENAME'] = str(self.basename)
        # deal with kind
        self.output_dict['KIND'] = str(kind)
        # deal with last modified time for file
        self.output_dict['LAST_MODIFIED'] = Path(self.filename).lstat().st_mtime
        # deal with the run string (string that can be used to re-run the
        #     recipe to reproduce this file)
        if runstring is None:
            self.output_dict['RUNSTRING'] = 'None'
        else:
            self.output_dict['RUNSTRING'] = str(runstring)
        # add whether this row should be used be default (always 1)
        self.output_dict['USED'] = 1
        # add the raw fix (all files here should be raw fixed)
        self.output_dict['RAWFIX'] = 1

        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for it, key in enumerate(hkeys):
            # deal with header key stores
            if key in params:
                dkey = params[key][0]
            else:
                dkey = str(key)
            # get dtype
            dtype = htypes[it]
            # add key if in hdict (priority)
            if dkey in self.hdict:
                try:
                    self.output_dict[key] = dtype(self.hdict[dkey])
                except Exception as _:
                    self.output_dict[key] = 'None'
            elif dkey in self.header:
                try:
                    self.output_dict[key] = dtype(self.header[dkey])
                except Exception as _:
                    self.output_dict[key] = 'None'
            else:
                self.output_dict[key] = 'None'

    def combine(self, infiles: List['DrsFitsFile'], math: str = 'sum',
                same_type: bool = True,
                path: Union[str, None] = None) -> 'DrsFitsFile':
        """
        Combine a set of DrsFitsFiles into a single file using the "math"
        operation (i.e. sum, mean, median etc)

        :param infiles: a list of DrsFitsFile instances, to be combined
        :param math: str, the way to mathematically combine files
                     valid options are: sum, average, mean, median, med,
                     add, +, subtract, -, divide, /, multiple, times, *
        :param same_type: bool, if True input DrsFitsFile must be the same
                          type (DrsFitsFile.name identical) to combine otherwise
                          exception is raised
        :param path: None or str, update the path for the output combined
                     DrsFitsFile (added to new filename)

        :return: a new DrsFitsFile instance of the combined file
        """
        # set function name
        func_name = display_func(self.params, 'combine', __NAME__,
                                 self.class_name)
        # define usable math
        available_math = ['sum', 'average', 'mean', 'median', 'med',
                          'add', '+', 'subtract', '-', 'divide', '/',
                          'multiply', 'times', '*']
        # --------------------------------------------------------------------
        # check that params is set
        self.check_params(func_name)
        params = self.params
        # check that data is read
        self.check_read()
        # set new data to this files data
        data = np.array(self.data)
        # --------------------------------------------------------------------
        # cube
        datacube = [data]
        basenames = [self.basename]
        # combine data into cube
        for infile in infiles:
            # check data is read for infile
            infile.check_read()
            # check that infile matches in name to self
            if (self.name != infile.name) and same_type:
                eargs = [func_name]
                WLOG(params, 'error', TextEntry('00-001-00021', args=eargs))
            # add to cube
            datacube.append(infile.data)
            basenames.append(infile.basename)
        # make datacube an numpy array
        datacube = np.array(datacube)
        # --------------------------------------------------------------------
        # deal with math
        # --------------------------------------------------------------------
        # log what we are doing
        WLOG(params, '', TextEntry('40-999-00004', args=[math]))
        # if we want to sum the data
        if math in ['sum', 'add', '+']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nansum(datacube, axis=0)
        # else if we want to subtract the data
        elif math in ['subtract', '-']:
            for im in range(1, len(datacube)):
                data -= datacube[im]
        # else if we want to divide the data
        elif math in ['divide', '/']:
            for im in range(1, len(datacube)):
                data /= datacube[im]
        # else if we want to multiple the data
        elif math in ['multiple', 'times', '*']:
            for im in range(1, len(datacube)):
                data *= datacube[im]
        # elif if mean/average
        elif math in ['average', 'mean']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nanmean(datacube, axis=0)
        # elif if median
        elif math in ['median', 'med']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nanmedian(datacube, axis=0)
        # else we have an error in math
        else:
            eargs = [math, ', '.join(available_math), func_name]
            WLOG(params, 'error', TextEntry('00-001-00042', args=eargs))

        # --------------------------------------------------------------------
        # Need to setup a new filename
        # --------------------------------------------------------------------
        # get common prefix
        prefix = drs_text.common_text(basenames, 'prefix')
        suffix = drs_text.common_text(basenames, 'suffix')
        basename = drs_text.combine_uncommon_text(basenames, prefix, suffix)
        # update path and filename
        if path is None:
            path = self.path
        filename = os.path.join(path, basename)
        # --------------------------------------------------------------------
        # construct keys for new DrsFitsFile
        # --------------------------------------------------------------------
        return DrsFitsFile(self.name, self.filetype, self.suffix,
                           self.remove_insuffix, self.prefix, self.fibers,
                           self.fiber, self.params,
                           filename, self.intype, path, basename, self.inputdir,
                           self.directory, data, self.header, self.fileset, 
                           self.filesetnames, self.outfunc, self.inext, 
                           self.dbname, self.dbkey, self.required_header_keys, 
                           self.numfiles, data.shape, self.hdict, 
                           self.output_dict, self.datatype, self.dtype,
                           True, list(basenames), self.s1d)

    # -------------------------------------------------------------------------
    # fits file header methods
    # -------------------------------------------------------------------------
    def get_hkey(self, key, has_default=False, default=None,
                 required=True, dtype: Type = float,
                 listtype: Union[Type, None] = None) -> Any:
        """
        Looks for a key in DrsFitsFile.header, if has_default is
        True sets value of key to 'default' if not found else if "required"
        logs an error

        :param key: string, key in the dictionary to find first looks in
                            DrsFile.header directly then checks
        :param has_default: bool, if True uses "default" as the value if key
                            not found
        :param default: object, value of the key if not found and
                        has_default is True
        :param required: bool, if True key is required and causes error is
                         missing if False and key not found value is None
        :param dtype: type, the data type for output
        :param listtype: if type is a list this is the type of the list elements

        :return: the value from the header for key
        """
        # set function name
        func_name = display_func(self.params, 'read_header_key', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        # check that data is read
        self.check_read(header_only=True)
        # check key is valid
        drskey = self._check_key(key)
        # if we have a default key try to get key else use default value
        if has_default:
            value = self.header.get(drskey, default)
        # else we must look for the value manually and handle the exception
        else:
            try:
                value = self.header[drskey]
            except KeyError:
                # if we do not require this keyword don't generate an error
                #   just return None
                if not required:
                    return None
                # else generate an error
                else:
                    if key == drskey:
                        eargs = [drskey, self.filename, func_name]
                        emsg = TextEntry('09-000-00006', args=eargs)
                    else:
                        eargs = [drskey, self.filename, key, func_name]
                        emsg = TextEntry('09-000-00006', args=eargs)
                    self.__error__(emsg)
                    value = None
        # deal with booleans
        if isinstance(value, str):
            # if dtype is a bool try to push to a boolean
            if dtype == bool or dtype == 'bool':
                if value.upper() in ['1', 'TRUE', 'T']:
                    value = True
                else:
                    value = False
        # deal with input lists
        if isinstance(value, str):
            # if dtype is a list
            if dtype == list:
                # try to split the value as a list
                value = value.split(',')
                value = list(np.char.array(value).strip())
                # cast to required list type
                if listtype is not None and isinstance(listtype, type):
                    value = list(map(lambda x: listtype(x), value))
        # try to convert to dtype else just return as string
        try:
            value = dtype(value)
        except ValueError:
            value = str(value)
        except TypeError:
            value = str(value)
        # return value
        return value

    def get_hkeys(self, keys: List[str], has_default: bool = False,
                  defaults: Union[List[Any], None] = None) -> List[Any]:
        """
        Looks for a set of keys in DrsFile.header, if has_default is
        True sets value of key to 'default' if not found else if "required"
        logs an error

        :param keys: list of string, key in the dictionary to find
        :param has_default: bool, if True uses "default" as the value if key
                            not found
        :param defaults: object, value of the key if not found and
                        has_default is True

        :return value: object, value of DrsFile.header[key] or default (if
                       has_default=True)
        """
        # set function name
        func_name = display_func(self.params, 'read_header_keys', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        # check that data is read
        self.check_read(header_only=True)
        # make sure keys is a list
        try:
            keys = list(keys)
        except TypeError:
            self.__error__(TextEntry('00-001-00005', args=[func_name]))
        # if defaults is None --> list of Nones else make sure defaults
        #    is a list
        if defaults is None:
            defaults = list(np.repeat([None], len(keys)))
        else:
            try:
                defaults = list(defaults)
                if len(defaults) != len(keys):
                    self.__error__(TextEntry('00-001-00006', args=[func_name]))
            except TypeError:
                self.__error__(TextEntry('00-001-00007', args=[func_name]))
        # loop around keys and look up each key
        values = []
        for k_it, key in enumerate(keys):
            # get the value for key
            v = self.get_hkey(key, has_default, default=defaults[k_it])
            # append value to values list
            values.append(v)
        # return values
        return values

    def get_hkey_1d(self, key: str, dim1: Union[str, None] = None,
                    dtype: Type = float, start: int = 0,
                    excludes: Union[None, List[str], str] = None,
                    includes: Union[None, List[str], str] = None,
                    elogic: str = 'AND', ilogic: str = 'AND') -> np.ndarray:
        """
        Read a set of header keys that were created from a 1D list

        :param key: string, prefix of HEADER key to construct 1D list from
                     key[row number]
        :param dim1: int, the number of elements in dimension 1
                     (number of rows) if unset tries to guess number of rows
        :param dtype: type, the type to force the data to be (i.e. float, int)
        :param start: int, the start index for the 1d list (normally 0)
        :param excludes: List of strings or string, sub-strings to exclude
                         from matched header keys - requires using {} in the
                         key in place of missing text
        :param includes: List of strings or string, sub-strings to include
                         from matched header keys - requires using {} in the
                         key in place of missing text
        :param elogic: string, either 'AND' or 'OR' for combining multiple
                       excludes
        :param ilogic: string, either 'AND' or 'OR' for combining multiple
                       includes

        :return values: numpy array (1D), the values force to type = dtype
        """
        # set function name
        func_name = display_func(self.params, 'get_hkey_1d', __NAME__,
                                 self.class_name)
        # check that data is read
        self.check_read(header_only=True)
        # check key is valid
        drskey = self._check_key(key)
        # ------------------------------------------------------------------
        # deal with no dim1 key
        if dim1 is None:
            # use wild card to try to find keys
            wildkey = drskey.split('{')[0] + '*' + drskey.split('}')[-1]
            # use wild card in header
            rawwildvalues = list(self.header[wildkey].keys())
            # deal with includes/excludes
            ieargs = [rawwildvalues, includes, excludes, ilogic, elogic]
            wildvalues = drs_text.include_exclude(*ieargs)
            # deal with no wild card values found
            if wildvalues is None:
                eargs = [wildkey, dim1, self.basename, func_name]
                self.__error__(TextEntry('09-000-00008', args=eargs))
            # else get the length of dim1
            else:
                dim1 = len(wildvalues)
        # ------------------------------------------------------------------
        # create 1d list
        values = []
        # loop around the 2D array
        for it in range(start, dim1 + start):
            # construct the key name
            keyname = test_for_formatting(drskey, it)
            # try to get the values
            try:
                # set the value
                values.append(dtype(self.header[keyname]))
            except KeyError:
                eargs = [keyname, dim1, self.basename, func_name]
                self.__error__(TextEntry('09-000-00008', args=eargs))
                values = None
        # return values
        return np.array(values)

    def get_hkey_2d(self, key: str, dim1: Union[str, None],
                    dim2: Union[str, None], dtype: Type = float) -> np.ndarray:
        """
        Read a set of header keys that were created from a 2D list

        :param key: string, prefix of HEADER key to construct 2D list from
                     key[number]
               where number = (row number * number of columns) + column number
               where column number = dim2 and row number = range(0, dim1)
        :param dim1: int, the number of elements in dimension 1
                     (number of rows)
        :param dim2: int, the number of columns in dimension 2
                     (number of columns)
        :param dtype: type, the type to force the data to be (i.e. float, int)

        :return values: numpy array (2D), the values force to type = dtype
        """
        # set function name
        func_name = display_func(self.params, 'get_hkey_2d', __NAME__,
                                 self.class_name)
        # check that data is read
        self.check_read(header_only=True)
        # check key is valid
        drskey = self._check_key(key)
        # create 2d list
        values = np.zeros((dim1, dim2), dtype=dtype)
        # loop around the 2D array
        dim1, dim2 = values.shape
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = test_for_formatting(drskey, it * dim2 + jt)
                # try to get the values
                try:
                    # set the value
                    values[it][jt] = dtype(self.header[keyname])
                except KeyError:
                    eargs = [keyname, drskey, dim1, dim2, self.basename,
                             func_name]
                    self.__error__(TextEntry('09-000-00009', args=eargs))
        # return values
        return values

    def _check_key(self, key: str) -> str:
        """
        Checks whether a key comes from a keywordstore (stored inside parameter
        dictionary: DrsFitsFile.params)

        :param key: str, the key to check - if key is in paramdict then
                    key = params[key] - if output is a list (keyword store)
                    we assume key = key[0]

        :return: str, either the key, params[key], key[0], params[key][0]
        """
        # set function name
        _ = display_func(self.params, '_check_key', __NAME__, self.class_name)
        # get drs parameters
        drs_params = self.params
        # need to check drs_params for key (if key is not in header)
        if (key not in self.header) and (key in drs_params):
            store = drs_params[key]
            # see if we have key store
            if isinstance(store, list) and len(store) == 3:
                drskey = str(store[0])
                source = 'store[0]'
            # if we dont assume we have a string
            else:
                drskey = str(store)
                source = 'store'
        else:
            drskey = str(key)
            source = 'input'
        # debug log message
        dargs = [key, drskey, source]
        WLOG(drs_params, 'debug', TextEntry('90-008-00001', args=dargs))
        # return drskey
        return drskey

    def copy_original_keys(self, drs_file: 'DrsFitsFile' = None,
                           forbid_keys: bool = True,
                           root: Union[str, None] = None,
                           allkeys: bool = False,
                           group: Union[str, None] = None,
                           exclude_groups: Union[str, List[str], None] = None):
        """
        Copies keys from hdr dictionary to DrsFile.hdict,
        if forbid_keys is True some keys will not be copied
        (defined in spirouConfig.Constants.FORBIDDEN_COPY_KEYS())

        adds keys in form: hdict[key] = (value, comment)

        :param drs_file: DrsFile instance, the file to be used to copy the
                         header keys from (must have read this file to generate
                         the header)

        :param forbid_keys: bool, if True uses the forbidden copy keys
                            (defined in
                               spirouConfig.Constants.FORBIDDEN_COPY_KEYS()
                            to remove certain keys from those being copied,
                            if False copies all keys from input header

        :param root: string, if we have "root" then only copy keywords that
                     start with this string (prefix)

        :param allkeys: bool, if True return all keys from header

        :param group: string, if not None sets the group to use (will only
                      copy this groups header keys)

        :param exclude_groups: string or list or strings, if not None sets the
                              group or groups not to include in copy

        :return None:
        """
        # set function name
        _ = display_func(self.params, 'copy_original_keys', __NAME__,
                         self.class_name)
        # deal with exclude groups
        if exclude_groups is not None:
            if isinstance(exclude_groups, str):
                exclude_groups = [exclude_groups]
        # get drs_file header/comments
        if drs_file is None:
            self.check_read(header_only=True)
            fileheader = self.header
        else:
            # check that data/header is read
            drs_file.check_read(header_only=True)
            fileheader = drs_file.header
        # get cards to copy
        _cards = self.copy_cards(fileheader.cards, root, exclude_groups, group,
                                 forbid_keys, allkeys)
        # deal with appending to a hidct that isn't empty
        if self.hdict is None:
            self.hdict = drs_fits.Header(_cards)
        else:
            for _card in _cards:
                self.hdict.append(_card)

    def copy_cards(self, cards: drs_fits.Header.cards,
                   root: Union[str, None] = None,
                   exclude_groups: Union[str, List[str], None] = None,
                   group: Union[str, None] = None,
                   forbid_keys: bool = True, allkeys: bool = False
                   ) -> drs_fits.Header.cards:
        """
        Copy header cards in the correct way

        :param cards: astropy.io.fits.header.Cards instance
        :param root: str, if we have "root" then only copy keywords that
                     start with this string (prefix)
        :param exclude_groups: string or list or strings, if not None sets the
                              group or groups not to include in copy
        :param group: string, if not None sets the group to use (will only
                      copy this groups header keys)
        :param forbid_keys: bool, if True uses the forbidden copy keys
                            (defined in
                               spirouConfig.Constants.FORBIDDEN_COPY_KEYS()
                            to remove certain keys from those being copied,
                            if False copies all keys from input header
        :param allkeys: bool, if True return all keys from header

        :return: astropy.io.fits.header.Cards instance - updated
        """
        # set function name
        func_name = display_func(self.params, 'copy_cards', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # generate instances from params
        keyword_inst = constants.constant_functions.Keyword
        keyworddict = params.get_instanceof(keyword_inst, nameattr='key')
        # get pconstant
        pconstant = constants.pload(params['INSTRUMENT'])
        
        # filter function
        def __keep_card(card: drs_fits.fits.header.Card) -> bool:
            """
            Filter function to sort out whether to keep a card returns
            True if we should keep a card False if we shoudn't

            :param card: a astropy.io.fits.header.Card instance

            :return: True if we should keep a card False if we shoudn't
            """
            key = card[0]
            if root is not None:
                if not key.startswith(root):
                    return False
            # deal with exclude groups
            if exclude_groups is not None:
                # loop around keys
                for exgrp in exclude_groups:
                    # check if key is in keyword dict and return the
                    #    corresponding key (mkey) if found
                    cond, mkey = _check_keyworddict(key, keyworddict)
                    # if key is in keyword dict look if group matches
                    if cond:
                        keygroup = keyworddict[mkey].group
                        # if key group is None skip check
                        if keygroup is None:
                            continue
                        # if key group is equal to exclude group then return
                        #    False  i.e. don't keep
                        if keygroup.upper() == exgrp.upper():
                            return False
            # deal with group (have to get keyword instance from keyworddict
            #    then check if it has a group then see if group = keygroup)
            if group is not None:
                # check if key is in keyword dict and return the corresponding
                #    key (mkey) if found
                cond, mkey = _check_keyworddict(key, keyworddict)
                # if key is in keyword dict look if group matches
                if cond:
                    keygroup = keyworddict[mkey].group
                    # if key group is None skip it
                    if keygroup is None:
                        return False
                    # if key group does not match group skip it
                    if keygroup.upper() != group.upper():
                        return False
                # if we have a group but key is not in keyword dict we
                # return False --> we don't want this key
                else:
                    return False
            # skip if key is forbidden key
            if forbid_keys and (key in pconstant.FORBIDDEN_COPY_KEYS()):
                return False
            # skip if key is drs forbidden key (unless allkeys)
            elif (key in pconstant.FORBIDDEN_DRS_KEY()) and (not allkeys):
                return False
            # skip if key added temporarily in code (denoted by @@@)
            elif '@@@' in key:
                return False
            # skip QC keys (unless allkeys)
            elif is_forbidden_prefix(pconstant, key) and (not allkeys):
                return False
            else:
                return True

        # filter and create new header
        _copy_cards = filter(__keep_card, cards)
        # return cards for copy
        return _copy_cards

    def add_hkey(self, key: Union[str, None] = None,
                 keyword: Union[list, None] = None, value: Any = None,
                 comment: Union[str, None] = None,
                 fullpath: bool = False, mapf: Union[str, None] = None):
        """
        Add a new key to DrsFile.hdict from kwstore. If kwstore is None
        and key and comment are defined these are used instead.

            Each keywordstore is in form:
                [key, value, comment]    where key and comment are strings
            DrsFile.hdict is updated with hdict[key] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param keyword: if key not set use the keywordstore
                        keyword must be in the format:
                        keyword = [key, value, comment]
        :param value: object or None, if any python object (other than None)
                      will set the value of hdict[key] to (value, comment)
        :param comment: string or None, if kwstore not define this is the
                        comment to set in hdict[key] = (value, comment)
        :param fullpath: bool, if true header keys retain the full path
                         if False filenames are cut down to just the filename
                         (os.path.basename)
        :param mapf: string, sets how we interpret "value" - mapf can either be
                     "list" or "dict", if list then value should be a list of
                     values, if dict then value should be a dict

        :return: None (but updates DrsFitsFile.hdict)
        """
        # set function name
        func_name = display_func(self.params, 'add_hkey', __NAME__,
                                 self.class_name)
        # deal with mapf
        if mapf is not None:
            if mapf == 'list':
                value = ', '.join(np.array(value).astype(str))
            elif mapf == 'dict':
                value = value.__str__()

        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list) or isinstance(key, tuple):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(TextEntry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, value, comment]
        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            okey, dvalue, comment = self.get_keywordstore(tuple(kwstore), 
                                                          func_name)
        else:
            okey, dvalue, comment = key, None, comment

        # set the value to default value if value is None
        if value is None:
            value = dvalue

        # deal with paths (should only contain filename for header)
        if isinstance(value, str):
            if os.path.isfile(value) and (not fullpath):
                value = os.path.basename(value)

        # add to the hdict dictionary in form (value, comment)
        self.hdict[okey] = (value, comment)

    def add_hkeys(self, keys: Union[List[str], None] = None,
                  kwstores: Union[List[list], None] = None,
                  values: Union[List[Any], None] = None,
                  comments: Union[List[str], None] = None):
        """
        Add a set of new key to DrsFile.hdict from keywordstores. If kwstores
        is None and keys and comments are defined these are used instead.

        Each kwstores is in form:
                [key, value, comment]    where key and comment are strings


        :param keys: list of strings, if kwstores is None this is the list
                         of keys (must be same size as "comments")
        :param kwstores: list of lists, list of "keyword list" lists
                              each "keyword list" must be in form:
                              [string, value, string]
        :param values: list of objects or None, if any python object
                       (other than None) will replace the values in kwstores
                       (i.e. kwstore[1]) with value[i], if None uses the
                       value = kwstore[1] for each kwstores
        :param comments: list of string, if kwstores is None this is the list
                         of comments (must be same size as "keys")

        :return None:
        """
        # set function name
        func_name = display_func(self.params, 'add_hkeys', __NAME__,
                                 self.class_name)
        # deal with no keywordstore
        if (kwstores is None) and (keys is None or comments is None):
            self.__error__(TextEntry('00-001-00009', args=[func_name]))
        # deal with kwstores set
        if kwstores is not None:
            # make sure kwstores is a list of list
            if not isinstance(kwstores, list):
                self.__error__(TextEntry('00-001-00010', args=[func_name]))
            # loop around entries
            for k_it, kwstore in enumerate(kwstores):
                self.add_hkey(keyword=kwstore, value=values[k_it])
        # else we assume keys and comments
        else:
            if not isinstance(keys, list):
                self.__error__(TextEntry('00-001-00011', args=[func_name]))
            if not isinstance(comments, list):
                self.__error__(TextEntry('00-001-00012', args=[func_name]))
            if len(keys) != len(comments):
                self.__error__(TextEntry('00-001-00013', args=[func_name]))
            # loop around entries
            for k_it in range(len(keys)):
                self.add_hkey(key=keys[k_it], value=values[k_it],
                              comment=comments[k_it])

    def add_hkey_1d(self, key: Union[str, None] = None,
                    values: Union[List[Any], np.ndarray, None] = None,
                    keyword: Union[List[list], None] = None,
                    comment: Union[str, None] = None,
                    dim1name: Union[str, None] = None):
        """
        Add a new 1d list to key using the "kwstore"[0] or "key" as prefix
        in form:
            keyword = kwstore + row number
            keyword = key + row number
        and pushes it into DrsFile.hdict in form:
            hdict[keyword] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param values: numpy array or 1D list of keys or None
                       if numpy array or 1D list will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param keyword: string, if key is None uses key and comment in form
                   keyword = key + row number
        :param comment: string, the comment to go into the header
                        hdict[keyword] = (value, comment)
        :param dim1name: string, the name for dimension 1 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}

        :return None: updates DrsFitsFile.hdict
        """
        # set function name
        func_name = display_func(self.params, 'add_hkey_1d', __NAME__,
                                 self.class_name)
        # deal with no keywordstore
        if (key is None) and (keyword is None or comment is None):
            self.__error__(TextEntry('00-001-00014', args=[func_name]))
        # deal with no dim1name
        if dim1name is None:
            dim1name = 'dim1'
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(TextEntry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, None, comment]

        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            okey, dvalue, comment = self.get_keywordstore(tuple(kwstore), 
                                                          func_name)
        else:
            okey, dvalue, comment = keyword, None, comment
        # set the value to default value if value is None
        if values is None:
            values = [dvalue]
        # convert to a numpy array
        values = np.array(values)
        # get the length of dimension 1
        dim1 = len(values)
        # loop around the 1D array
        for it in range(dim1):
            # construct the key name
            keyname = test_for_formatting(okey, it)
            # get the value
            value = values[it]
            # deal with paths (should only contain filename for header)
            if isinstance(value, str):
                if os.path.isfile(value):
                    value = os.path.basename(value)
            # construct the comment name
            comm = '{0} {1}={2}'.format(comment, dim1name, it)
            # add to header dictionary
            self.hdict[keyname] = (value, comm)

    def add_hkey_2d(self, key: Union[str, None] = None,
                    keyword: Union[List[list], None] = None,
                    values: Union[np.ndarray, None] = None,
                    comment: Union[str, None] = None,
                    dim1name: Union[str, None] = None,
                    dim2name: Union[str, None] = None):
        """
        Add a new 2d list to key using the "kwstore"[0] or "key" as prefix
        in form:
            keyword = kwstore + row number
            keyword = key + row number

        where number = (row number * number of columns) + column number

        and pushes it into DrsFile.hdict in form:
            hdict[keyword] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param values: numpy array or None
                       if numpy array will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param keyword: string, if key is None uses key and comment in form
                   keyword = key + row number
        :param comment: string, the comment to go into the header
                        hdict[keyword] = (value, comment)
        :param dim1name: string, the name for dimension 1 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}
        :param dim2name: string, the name for dimension 2 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}

        :return None: updates DrsFitsFile.hdict
        """
        # set function name
        func_name = display_func(self.params, 'add_hkey_2d', __NAME__,
                                 self.class_name)
        # deal with no dim names
        if dim1name is None:
            dim1name = 'dim1'
        if dim2name is None:
            dim2name = 'dim2'
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(TextEntry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, None, comment]
        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            key, dvalue, comment = self.get_keywordstore(tuple(kwstore),
                                                         func_name)
        else:
            key, dvalue, comment = key, None, comment
        # set the value to default value if value is None
        if values is None:
            values = [dvalue]
        # convert to a numpy array
        values = np.array(values)
        # get the length of dimension 1
        dim1, dim2 = values.shape
        # loop around the 1D array
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = test_for_formatting(key, it * dim2 + jt)
                # get the value
                value = values[it, jt]
                # deal with paths (should only contain filename for header)
                if isinstance(value, str):
                    if os.path.isfile(value):
                        value = os.path.basename(value)
                # construct the comment name
                cargs = [comment, dim1name, it, dim2name, jt]
                comm = '{0} {1}={2} {3}={4}'.format(*cargs)
                # add to header dictionary
                self.hdict[keyname] = (value, comm)

    def add_qckeys(self, qcparams: Union[QCParamList, None] = None):
        """
        Add the quality control keys to the header, if None passed a single
        empty qc parameter is added with 'None' for all values

        :param qcparams: List of list containing:
                            [quality control names,
                             quality control values,
                             quality control logic,
                             quality control pass/fail]

        :return: None, updates DrsFitsFile.hdict
        """
        # set function name
        func_name = display_func(self.params, 'add_qckeys', __NAME__,
                                 self.class_name)
        # get parameters
        qc_kws = ['KW_DRS_QC_NAME', 'KW_DRS_QC_VAL', 'KW_DRS_QC_LOGIC',
                  'KW_DRS_QC_PASS']
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # deal with qcparams = None
        if qcparams is None:
            qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
            # add to qc header lists
            qc_pass.append(1)
            qc_values.append('None')
            qc_names.append('None')
            qc_logic.append('None')
            # store in qc_params
            qcparams = [qc_names, qc_values, qc_logic, qc_pass]
        # check lengths are the same
        lengths = []
        for qcparam in qcparams:
            lengths.append(len(qcparam))
        strlengths = map(lambda x: str(x), lengths)
        # loop around lengths and test that they are the same
        for length in lengths:
            if lengths[0] != length:
                eargs = [', '.join(strlengths), func_name]
                WLOG(params, 'error', TextEntry('00-001-00019', args=eargs))
        # loop around values and add to hdict
        for it in range(lengths[0]):
            # loop around qc parameters
            for jt, keystr in enumerate(qc_kws):
                keyws = params[keystr]
                # extract keyword, value and comment and put it into hdict
                key, dvalue, comment = self.get_keywordstore(keyws, func_name)
                value = qcparams[jt][it]
                # add to the hdict dictionary in form (value, comment)
                self.hdict[key.format(it + 1)] = (value, comment)
        # add a final criteria that says whether everything passed or not
        qc_all = params['KW_DRS_QC'][0]
        self.hdict[qc_all] = np.all(qcparams[3])

    def get_qckeys(self) -> QCParamList:
        """
        Get the quality control header keys from the header
        Note values will be pushed to strings (and may need to change data
        type after return)

        :return: List of list containing:
                            [quality control names,
                             quality control values,
                             quality control logic,
                             quality control pass/fail]
        """
        # set function name
        func_name = display_func(self.params, 'get_qckeys', __NAME__,
                                 self.class_name)
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # get qc all value
        qc_all = params['KW_DRS_QC'][0]
        # get qc_values
        qc_values = self.get_hkey_1d('KW_DRS_QC_VAL', dtype=str,
                                     start=1, excludes=qc_all)
        qc_names = self.get_hkey_1d('KW_DRS_QC_NAME', dtype=str,
                                    start=1, excludes=qc_all)
        qc_logic = self.get_hkey_1d('KW_DRS_QC_LOGIC', dtype=str,
                                    start=1, excludes=qc_all)
        qc_pass = self.get_hkey_1d('KW_DRS_QC_PASS', dtype=int,
                                   start=1, excludes=qc_all)
        # push into qc params
        qc_params = (list(qc_names), list(qc_values), list(qc_logic),
                     list(qc_pass))
        # return qc params
        return qc_params

    def get_keywordstore(self, kwstore: Tuple[str, Any, str],
                         func_name=None) -> Tuple[str, Any, str]:
        """
        Deal with extraction of key, value and comment from kwstore
        the kwstore should be a list in the following form:

        [name, value, comment]     with types [string, object, string]

        :param kwstore: list, keyword list must be in form:
                          [string, value, string]
        :param func_name: string or None, if not None defined where the
                          kwstore function is being called, if None
                          is set to here (spirouFITS.extract_key_word_store())

        :return key: string, the name/key of the HEADER (key/value/comment)
        :return value: object, any object to be put into the HEADER value
                       (under HEADER key="key")
        :return comment: string, the comment associated with the HEADER key
        """
        # deal with no func_name
        if func_name is None:
            # set function name
            func_name = display_func(self.params, 'get_keywordstore', __NAME__,
                                     self.class_name)
        # extract keyword, value and comment and put it into hdict
        # noinspection PyBroadException
        try:
            key, dvalue, comment = kwstore
        except Exception as _:
            eargs = [kwstore, func_name]
            self.__error__(TextEntry('00-001-00016', args=eargs))
            key, dvalue, comment = None, None, None
        # return values
        return key, dvalue, comment

    def copy_hdict(self, drsfile: 'DrsFitsFile'):
        """
        Copy a hdict entry from drsfile (a DrsFitsFile instance)

        :param drsfile: DrsFitsFile instance (containing drsfile.hdict)
        :return: None, updates DrsFitsFile.hdict
        """
        # set function name
        _ = display_func(self.params, 'copy_hdict', __NAME__, self.class_name)
        # set this instance to the hdict instance of another drs fits file
        self.hdict = drsfile.hdict.copy()

    def copy_header(self, drsfile: 'DrsFitsFile'):
        """
        Copy a header entry from drsfile (a DrsFitsFile instance)
        :param drsfile: DrsFitsFile instance (containing drsfile.hdict)
        :return: None, updates DrsFitsFile.header
        """
        # set function name
        _ = display_func(self.params, 'copy_header', __NAME__, self.class_name)
        # set this instance to the header instance of another drs fits file
        self.header = drsfile.header.copy()

    # -------------------------------------------------------------------------
    # database methods
    # -------------------------------------------------------------------------
    def get_dbkey(self) -> Union[str, None]:
        """
        Returns the database key for DrsFitsFile

        :return: str or None, if set returns the string name for the database
                 key
        """
        # set function name
        _ = display_func(self.params, 'get_dbkey', __NAME__, self.class_name)
        # deal with dbkey not set
        if self.raw_dbkey is None or self.dbkey is None:
            return None
        # set db key from raw dbkey
        self.dbkey = str(self.raw_dbkey)
        # make dbkey uppdercase
        if self.dbkey is not None:
            self.dbkey = self.dbkey.upper()
        # return dbkey
        return self.dbkey


class DrsNpyFile(DrsInputFile):
    def __init__(self, name, filetype: str = '.npy',
                 suffix: str = '',
                 remove_insuffix: bool = False,
                 prefix: str = '',
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 directory: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outfunc: Union[Any, None] = None,
                 inext: Union[str, None] = '.npy',
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = None,
                 shape: Union[int, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = None,
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = None,
                 combined_list: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None):
        """
        Create a DRS Npy File Input object

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: NOT USED FOR NPY FILE CLASS
        :param remove_insuffix: NOT USED FOR NPY FILE CLASS
        :param prefix: NOT USED FOR NPY FILE CLASS
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: NOT USED FOR NPY FILE CLASS
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: NOT USED FOR NPY FILE CLASS
        :param path: NOT USED FOR NPY FILE CLASS
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: NOT USED FOR NPY FILE CLASS
        :param directory: NOT USED FOR NPY FILE CLASS
        :param data: np.array - when loaded the data is stored here
        :param header: NOT USED FOR NPY FILE CLASS
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: NOT USED FOR NPY FILE CLASS
        :param numfiles: NOT USED FOR NPY FILE CLASS
        :param shape: NOT USED FOR NPY FILE CLASS
        :param hdict: NOT USED FOR NPY FILE CLASS
        :param output_dict: NOT USED FOR NPY FILE CLASS
        :param datatype: NOT USED FOR NPY FILE CLASS
        :param dtype: NOT USED FOR NPY FILE CLASS
        :param is_combined: NOT USED FOR NPY FILE CLASS
        :param combined_list: NOT USED FOR NPY FILE CLASS
        :param s1d: NOT USED FOR NPY FILE CLASS
        :param hkeys: NOT USED FOR NPY FILE CLASS
        """
        # set class name
        self.class_name = 'DrsNpyFile'
        # set function name
        _ = display_func(params, '__init__', __NAME__, self.class_name)
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, filetype, suffix, remove_insuffix,
                              prefix, fibers, fiber, params, filename, intype,
                              path, basename, inputdir, directory, data, header,
                              fileset, filesetnames, outfunc, inext, dbname,
                              dbkey, rkeys, numfiles, shape, hdict,
                              output_dict, datatype, dtype, is_combined,
                              combined_list, s1d, hkeys)
        # these keys are not set in DrsInputFile
        self.inext = inext
        # get tag
        self.dbname = dbname
        self.raw_dbkey = dbkey
        self.dbkey = None
        if dbkey is not None:
            self.dbkey = str(dbkey)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        Defines the str(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(self.params, '__str__', __NAME__, self.class_name)
        # return string output
        return self.string_output()

    def __repr__(self) -> str:
        """
        Defines the print(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(self.params, '__repr__', __NAME__, self.class_name)
        # return string output
        return self.string_output()

    def read_file(self, ext: Union[int, None] = None, check: bool = False,
                  copy: bool = False):
        """
        Read a npy file (using advance np.load via drs_path.numpy_load)

        :param ext: NOT USED FOR NPY FILE CLASS
        :param check: NOT USED FOR NPY FILE CLASS
        :param copy: NOT USED FOR NPY FILE CLASS
        :return None:
        """
        # not used
        _ = ext
        _ = check
        _ = copy
        # set function name
        func_name = display_func(self.params, 'read_file', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # if filename is set
        if self.filename is not None:
            try:
                # read file
                self.data = drs_path.numpy_load(self.filename)
            except Exception as e:
                eargs = [type(e), e, self.filename, func_name]
                WLOG(params, 'error', TextEntry('00-008-00018', args=eargs))
        # cause error if file name is not set
        else:
            WLOG(params, 'error', TextEntry('00-008-00013', args=[func_name]))

    def check_read(self, header_only: bool = False, data_only: bool = False,
                   load: bool = True):
        """
        Check whether data have been read
        if load is True and they haven't been read them read them

        data is loaded into DrsFitsFile.data

        :param header_only: not used for Npy File
        :param data_only: bool, if True only read/check data
        :param load: bool, if True load header and / or data

        :return: None
        """
        # set function name
        _ = display_func(self.params, 'check_read', __NAME__, self.class_name)
        # header only is not used
        _ = header_only
        # ---------------------------------------------------------------------
        # deal with data only
        # ---------------------------------------------------------------------
        if data_only:
            if self.data is None:
                if load:
                    return self.read_file()
                # raise exception
                func = self.__repr__()
                eargs = [func, func + '.read_file()']
                self.__error__(TextEntry('00-001-00004', args=eargs))
                return 0
            else:
                return 1
        # ---------------------------------------------------------------------
        # deal with both data and header
        # ---------------------------------------------------------------------
        if self.data is None:
            self.read_file()
            return 1
        # if we got here we are good - data has been read
        return 1

    def get_data(self, copy: bool = False) -> Union[np.ndarray, Table, None]:
        """
        return the data array

        :param copy: bool, if True deep copies the data
        :return: the data (numpy array)
        """
        # set function name
        _ = display_func(self.params, 'get_data', __NAME__, self.class_name)
        # check data exists
        if self.data is None:
            self.check_read(data_only=True)
        # deal with copying data
        if copy:
            return np.array(self.data)
        else:
            return self.data

    def write_file(self, kind: str, runstring: Union[str, None] = None):
        """
        Write a npy file (using np.save)

        also used to update output_dictionary for index database

        :return: None
        """
        # set function name
        func_name = display_func(self.params, 'write_file', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # if filename is not set raise error
        if self.filename is None:
            WLOG(params, 'error', TextEntry('00-008-00013', args=[func_name]))
        if self.data is not None:
            try:
                # save to file
                np.save(self.filename, self.data)
            except Exception as e:
                eargs = [type(e), e, self.filename, func_name]
                WLOG(params, 'error', TextEntry('00-008-00015', args=eargs))
        else:
            eargs = [self.filename, func_name]
            WLOG(params, 'error', TextEntry('00-008-00014', args=eargs))
        # write output dictionary
        self.output_dictionary(kind, runstring)


    def string_output(self) -> str:
        """
        String output for DrsFitsFile. If fiber is not None this also
        contains the fiber type

        i.e. DrsFitsFile[{name}_{fiber}] or DrsFitsFile[{name}]
        :return string: str, the string to print
        """
        # set function name
        _ = display_func(self.params, 'string_output', __NAME__,
                         self.class_name)
        # if we do not have a fiber print the string representation of drs npy
        if self.fiber is None:
            return 'DrsNpyFile[{0}]'.format(self.name)
        # if we do add fiber to the string representation
        else:
            return 'DrsNpyFile[{0}_{1}]'.format(self.name, self.fiber)

    def newcopy(self, name: Union[str, None] = None,
                filetype: Union[str, None] = None,
                suffix: Union[str, None] = None,
                remove_insuffix: bool = False,
                prefix: Union[str, None] = None,
                fibers: Union[List[str], None] = None,
                fiber: Union[str, None] = None,
                params: Union[ParamDict, None] = None,
                filename: Union[str, None] = None,
                intype: Any = None,
                path: Union[str, None] = None,
                basename: Union[str, None] = None,
                inputdir: Union[str, None] = None,
                directory: Union[str, None] = None,
                data: Union[np.ndarray, None] = None,
                header: Union[drs_fits.Header, None] = None,
                fileset: Union[list, None] = None,
                filesetnames: Union[List[str], None] = None,
                outfunc: Union[Any, None] = None,
                inext: Union[str, None] = None,
                dbname: Union[str, None] = None,
                dbkey: Union[str, None] = None,
                rkeys: Union[dict, None] = None,
                numfiles: Union[int, None] = None,
                shape: Union[int, None] = None,
                hdict: Union[drs_fits.Header, None] = None,
                output_dict: Union[OrderedDict, None] = None,
                datatype: Union[str, None] = None,
                dtype: Union[type, None] = None,
                is_combined: Union[bool, None] = None,
                combined_list: Union[list, None] = None,
                s1d: Union[list, None] = None,
                hkeys: Union[Dict[str, str], None] = None):
        """
        Create a new copy of DRS Npy File object - unset parameters come
        from current instance of Drs Input File

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: NOT USED FOR NPY FILE CLASS
        :param remove_insuffix: NOT USED FOR NPY FILE CLASS
        :param prefix: NOT USED FOR NPY FILE CLASS
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: set params
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: NOT USED FOR NPY FILE CLASS
        :param path: NOT USED FOR NPY FILE CLASS
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: NOT USED FOR NPY FILE CLASS
        :param directory: NOT USED FOR NPY FILE CLASS
        :param data: np.array - when loaded the data is stored here
        :param header: NOT USED FOR NPY FILE CLASS
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: NOT USED FOR NPY FILE CLASS
        :param numfiles: NOT USED FOR NPY FILE CLASS
        :param shape: NOT USED FOR NPY FILE CLASS
        :param hdict: NOT USED FOR NPY FILE CLASS
        :param output_dict: NOT USED FOR NPY FILE CLASS
        :param datatype: NOT USED FOR NPY FILE CLASS
        :param dtype: NOT USED FOR NPY FILE CLASS
        :param is_combined: NOT USED FOR NPY FILE CLASS
        :param combined_list: NOT USED FOR NPY FILE CLASS
        :param s1d: NOT USED FOR NPY FILE CLASS
        :param kwargs: NOT USED FOR NPY FILE CLASS
        """
        # set function name
        _ = display_func(self.params, 'newcopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsNpyFile, self, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    def completecopy(self, drsfile: 'DrsNpyFile',
                     name: Union[str, None] = None,
                     filetype: Union[str, None] = None,
                     suffix: Union[str, None] = None,
                     remove_insuffix: bool = False,
                     prefix: Union[str, None] = None,
                     fibers: Union[List[str], None] = None,
                     fiber: Union[str, None] = None,
                     params: Union[ParamDict, None] = None,
                     filename: Union[str, None] = None,
                     intype: Any = None,
                     path: Union[str, None] = None,
                     basename: Union[str, None] = None,
                     inputdir: Union[str, None] = None,
                     directory: Union[str, None] = None,
                     data: Union[np.ndarray, None] = None,
                     header: Union[drs_fits.Header, None] = None,
                     fileset: Union[list, None] = None,
                     filesetnames: Union[List[str], None] = None,
                     outfunc: Union[Any, None] = None,
                     inext: Union[str, None] = None,
                     dbname: Union[str, None] = None,
                     dbkey: Union[str, None] = None,
                     rkeys: Union[dict, None] = None,
                     numfiles: Union[int, None] = None,
                     shape: Union[int, None] = None,
                     hdict: Union[drs_fits.Header, None] = None,
                     output_dict: Union[OrderedDict, None] = None,
                     datatype: Union[str, None] = None,
                     dtype: Union[type, None] = None,
                     is_combined: Union[bool, None] = None,
                     combined_list: Union[list, None] = None,
                     s1d: Union[list, None] = None,
                     hkeys: Union[Dict[str, str], None] = None):
        """
        Copy all keys from drsfile (unless other arguments set - these override
        copy from drsfile)

        :param drsfile: DrsNpyFile instance, the instance to copy parameters
                        from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: NOT USED FOR NPY FILE CLASS
        :param remove_insuffix: NOT USED FOR NPY FILE CLASS
        :param prefix: NOT USED FOR NPY FILE CLASS
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: NOT USED FOR NPY FILE CLASS
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: NOT USED FOR NPY FILE CLASS
        :param path: NOT USED FOR NPY FILE CLASS
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: NOT USED FOR NPY FILE CLASS
        :param directory: NOT USED FOR NPY FILE CLASS
        :param data: np.array - when loaded the data is stored here
        :param header: NOT USED FOR NPY FILE CLASS
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outfunc: Function, the output function to generate the output
                        name (using in constructing filename)
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: NOT USED FOR NPY FILE CLASS
        :param numfiles: NOT USED FOR NPY FILE CLASS
        :param shape: NOT USED FOR NPY FILE CLASS
        :param hdict: NOT USED FOR NPY FILE CLASS
        :param output_dict: NOT USED FOR NPY FILE CLASS
        :param datatype: NOT USED FOR NPY FILE CLASS
        :param dtype: NOT USED FOR NPY FILE CLASS
        :param is_combined: NOT USED FOR NPY FILE CLASS
        :param combined_list: NOT USED FOR NPY FILE CLASS
        :param s1d: NOT USED FOR NPY FILE CLASS
        :param kwargs: NOT USED FOR NPY FILE CLASS
        """
        # set function name
        _ = display_func(self.params, 'completecopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsNpyFile, drsfile, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            directory, data, header, fileset, filesetnames,
                            outfunc, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys)

    def output_dictionary(self, kind: str, runstring: Union[str, None] = None):
        """
        Generate the output dictionary (for use while writing)
        Uses OUTPUT_FILE_HEADER_KEYS and DrsFile.hdict to generate an
        output dictionary for this file (for use in indexing)

        Requires DrsFile.filename and DrsFile.params to be set

        :return None:
        """
        # set function name
        func_name = display_func(self.params, 'output_dictionary', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        params = self.params
        pconst = constants.pload(params['INSTRUMENT'])
        # get required keys for index database
        hkeys, htypes = pconst.INDEX_HEADER_KEYS()
        # deal with absolute path of file
        self.output_dict['PATH'] = str(self.filename)
        # deal with night name of file
        self.output_dict['DIRECTORY'] = str(self.params['NIGHTNAME'])
        # deal with basename of file
        self.output_dict['FILENAME'] = str(self.basename)
        # deal with kind
        if kind in ['red', 'reduc', 'reduced']:
            self.output_dict['KIND'] = 'red'
        else:
            self.output_dict['KIND'] = str(kind)
        # deal with last modified time for file
        self.output_dict['LAST_MODIFIED'] = Path(self.filename).lstat().st_mtime
        # deal with the run string (string that can be used to re-run the
        #     recipe to reproduce this file)
        if runstring is None:
            self.output_dict['RUNSTRING'] = 'None'
        else:
            self.output_dict['RUNSTRING'] = str(runstring)
        # add whether this row should be used be default (always 1)
        self.output_dict['USED'] = 1
        # add the raw fix (all files here should be raw fixed)
        self.output_dict['RAWFIX'] = 1
        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for it, key in enumerate(hkeys):
            # no header for npy files
            self.output_dict[key] = 'None'

    # -------------------------------------------------------------------------
    # database methods
    # -------------------------------------------------------------------------
    def get_dbkey(self) -> Union[str, None]:
        """
        Returns the database key for DrsFitsFile

        :return: str or None, if set returns the string name for the database
                 key
        """
        # set function name
        _ = display_func(self.params, 'get_dbkey', __NAME__, self.class_name)
        # deal with dbkey not set
        if self.raw_dbkey is None or self.dbkey is None:
            return None
        # set db key from raw dbkey
        self.dbkey = str(self.raw_dbkey)
        # make dbkey uppdercase
        if self.dbkey is not None:
            self.dbkey = self.dbkey.upper()
        # return dbkey
        return self.dbkey


# =============================================================================
# Define search functions
# =============================================================================
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


# TODO: NOT USED?
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

# =============================================================================
# User DrsFile functions
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
    outfile.write_file(kind=recipe.outputdir, runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(outfile)
    # return combined infile
    return outfile


def fix_header(params: ParamDict, recipe: Any,
               infile: Union[DrsFitsFile, None] = None,
               header: Union[Header, FitsHeader, None] = None,
               raise_exception: bool = False
               ) -> Union[DrsFitsFile, Tuple[FitsHeader, Header]]:
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
            file_in = drsfile.copyother(file_set, params=params)
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


def get_mid_obs_time(params: ParamDict,
                     header: Union[Header, FitsHeader, None] = None,
                     infile: Union[DrsFitsFile, None] = None,
                     out_fmt: Union[str, None] = None
                     ) -> Tuple[Union[Time, str, float], str]:
    """
    Get the mid point observation time from header and push it into the
    required format

    :param params: Paramdict, parameter dictionary of constants
    :param header: Header or astropy.fits.Header - the header instance to
                   read the MIDMJD from
    :param infile: DrsFitsFile - if Header is not set get it from infile
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
    # if infile is set get header from infile
    if infile is not None and header is None:
        header = infile.get_header()
    # deal with header still being None
    if header is None:
        eargs = [func_name]
        WLOG(params, 'error', TextEntry('00-001-00051', args=eargs))
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


def get_dir(params: ParamDict, dir_string: str, kind: str = 'input') -> str:
    """
    Get the directory based on "dir_string" (either RAW, TMP, REDUCED)
    obtained via params

    Note if dir_string is full path we do not use path from params

    :param params: ParamDict, parameter dictionary of constants
    :param dir_string: str, either 'RAW', 'TMP' or 'REDUCED' (case insensitive)
    :param kind: str, type of dir for logging (either 'input' or 'output')

    :return: str, the directory path
    """
    # check if path has been set to an absolute path (that exists)
    if os.path.exists(os.path.abspath(dir_string)):
        return os.path.abspath(dir_string)
    # get the input directory from recipe.inputdir keyword
    if dir_string.upper() == 'RAW':
        dirpath = params['DRS_DATA_RAW']
    elif dir_string.upper() == 'TMP':
        dirpath = params['DRS_DATA_WORKING']
    elif dir_string.upper() == 'RED':
        dirpath = params['DRS_DATA_REDUC']
    # if not found produce error
    else:
        emsg = TextEntry('00-007-00002', args=[kind, dir_string])
        WLOG(params, 'error', emsg)
        dirpath = None
    return dirpath


def get_input_dir(params: ParamDict, directory: Union[str, None] = None,
                  force: bool = False,
                  forced_dir: Union[str, None] = str) -> Union[str, None]:
    """
    Get the input directory for this recipe based on what was set in
    initialisation (construction)

    :param params: the Parameter dictionary of constants
    :param directory: None or string - force the input dir (if it exists)
    :param force: bool if True allows force setting
    :param forced_dir: str, if set if the forced dir value to get (can be
                       a full path or 'RAW', 'TMP', 'REDUCED'

    if RAW uses DRS_DATA_RAW from drs_params
    if TMP uses DRS_DATA_WORKING from drs_params
    if REDUCED uses DRS_DATA_REDUC from drs_params

    :return input_dir: string, the input directory
    """
    # set function name
    func_name = display_func(params, 'get_input_dir', __NAME__)
    # deal with manual override of input dir
    if force and (directory is not None) and (os.path.exists(directory)):
        return directory
    # deal with no forced dir set
    if forced_dir is None:
        # raise error
        eargs = ['input', func_name]
        WLOG(params, 'error', TextEntry('00-006-00020', args=eargs))
    # deal with absolute path existing
    if force and os.path.exists(os.path.abspath(forced_dir)):
        return os.path.abspath(forced_dir)
    # check if "input_dir" is in namespace
    input_dir_pick = forced_dir.upper()
    # return input_dir
    return get_dir(params, input_dir_pick, kind='input')


def get_output_dir(params: ParamDict, directory: Union[str, None] = None,
                   force: bool = False,
                   forced_dir: Union[str, None] = str) -> Union[str, None]:
    """
    Get the input directory for this recipe based on what was set in
    initialisation (construction)

    :param params: the Parameter dictionary of constants
    :param directory: None or string - force the output dir (if it exists)
    :param force: bool if True allows force setting
    :param forced_dir: str, if set if the forced dir value to get (can be
                       a full path or 'RAW', 'TMP', 'REDUCED'

    if RAW uses DRS_DATA_RAW from drs_params
    if TMP uses DRS_DATA_WORKING from drs_params
    if REDUCED uses DRS_DATA_REDUC from drs_params

    :return input_dir: string, the input directory
    """
    # set function name
    func_name = display_func(params, 'get_output_dir', __NAME__)
    # deal with manual override of input dir
    if force and (directory is not None) and (os.path.exists(directory)):
        return directory
    # deal with no forced dir set
    if forced_dir is None:
        # raise error
        eargs = ['output', func_name]
        WLOG(params, 'error', TextEntry('00-006-00020', args=eargs))
    # deal with absolute path existing
    if force and os.path.exists(os.path.abspath(forced_dir)):
        return os.path.abspath(forced_dir)
    # check if "input_dir" is in namespace
    output_dir_pick = forced_dir.upper()
    # return input_dir
    return get_dir(params, output_dir_pick, kind='output')


# =============================================================================
# Worker functions
# =============================================================================
# complex typing from _get_files
GetFilesType = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray,
                     Dict[str, np.ndarray]]


# TODO: NOT USED?
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
                header = drs_fits.read_header(params, abspath)
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


def test_for_formatting(key: str, number: Union[int, float]) -> str:
    """
    Specific test of a string that may either be:

    key   or {key}{number}

    e.g. if key = XXX{0}  --> XXX{number}
    e.g. if key = XXX --> XXX

    Note if XXX{0:.3f} number must be a float

    :param key: str, the key to test (and return if no formatting present)
    :param number: int or float, depending on format of key (and key present)
    :return: str, the ouput either modified (if with formatting) or "key"
    """
    # set function name
    _ = display_func(None, 'test_for_formatting', __NAME__)
    # test the formatting by entering a number as format
    test_str = key.format(number)
    # if they are the same after test return key with the key and number in
    if test_str == key:
        return '{0}{1}'.format(key, number)
    # else we just return the test string
    else:
        return test_str


def is_forbidden_prefix(pconstant: PseudoConstants, key: str) -> bool:
    """
    Boolean check of the Pseudo Constants class for FORBIDDEN_HEADER_PREFIXES
    if key starts with forbidden header prefixes False is returned, otherwise
    True is return

    :param pconstant: PseudoConstants class instance
    :param key: str, the key to check

    :return: bool, True if key does not start with any forbidden header prefix,
             False if it does
    """
    # set function name
    _ = display_func(None, 'is_forbidden_prefix', __NAME__)
    # assume key is not forbidden
    cond = False
    # if prefix is forbidden and key starts with this prefix -->
    #   set cond to true (key is not forbidden)
    for prefix in pconstant.FORBIDDEN_HEADER_PREFIXES():
        if key.startswith(prefix):
            cond = True
    # return condition on whether key is forbidden
    return cond


def _check_keyworddict(key: str,
                       keyworddict: dict) -> Tuple[bool, Union[str, None]]:
    """
    Some keys have formatting i.e. LOCE{0:04d} and thus for these we need to
    check their prefix matches the key (else we just check whole key)

    This ONLY works under the assumption that all format keys look as following:

        AAAA{0:4d}

        BBB{0:2d}

    (i.e. a string followed by a single formatting)

    :param key: string, key in header to check
    :param keyworddict: dictionary, the keyword dictionary to check (from
                        keyword definitions)

    :type key: str
    :type keyworddict: dict

    :return:
    """
    # set function name
    _ = display_func(None, '_check_keyworddict', __NAME__)
    # loop around keys in keyword dict
    for mkey in keyworddict:
        # check if we have not formatting (assuming int/float)
        # noinspection PyBroadException
        try:
            if mkey.format(0) == mkey:
                # if key is found then we stop here
                if key == mkey:
                    return True, mkey
                # we can skip to next key
                else:
                    continue
        # if it breaks assume we have a none int/float format
        except Exception as _:
            pass
        # else remove the formatting (assume it start with a '{'
        prefix = mkey.split('{')[0]
        # if key is found we stop here
        if key.startswith(prefix):
            return True, mkey
        else:
            continue
    # if we have checked every key then key is not found
    return False, None


def _copydrsfile(drsfileclass, instance1: DrsInputFile,
                 instance2: Union[DrsInputFile, None],
                 name: Union[str, None] = None,
                 filetype: Union[str, None] = None,
                 suffix: Union[str, None] = None,
                 remove_insuffix: bool = False,
                 prefix: Union[str, None] = None,
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 directory: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outfunc: Union[Any, None] = None,
                 inext: Union[str, None] = None,
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = None,
                 shape: Union[int, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = None,
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = None,
                 combined_list: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None):
    """
    Master copier of file instance
    instance1 = self normally
    instance2 = another file instance (if required)

    :param drsfileclass: the class to use to create new instance
    :param instance1: the class we are copying basic details from
    :param instance2: None or the class we are copying fits file data from
                      (including filename etc)

    :param name: string, the name of the DRS input file
    :param filetype: string, the file type i.e. ".fits"
    :param suffix: string, the suffix to add when making an output filename
                   from an input filename
    :param remove_insuffix: bool, if True removes input file suffix before
                   adding output file suffix
    :param prefix: string, the prefix to add when maing an output fulename
                   from an input filename
    :param fibers: list of strings, the possible fibers this file can be
                   associated with, should be None if it is not associated
                   with a specific fiber
    :param fiber: string, the specific fiber that this file is associated
                  with
    :param params: ParamDict, the parameter dictionary of constants
    :param filename: string, the filename to give to this file (may override
                     other options)
    :param intype: DrsInputFile, an DrsFile instance associated with the
                   input file that generates this file (as an output)
                   i.e. if this is a pp file the intype would be a raw file
    :param path: string, the path to save the file to (when writing)
                 this may be left blank and defaults to the recipe default
                 (recommended in most cases) - ma be relative
    :param basename: string, the basename (i.e. filename without path) for
                     the file
    :param inputdir: string, the input directory (associated with an input
                     file, when this is an output file)
    :param directory: string, the aboslute path of the file without the
                      filename (based on the fully generated filename)
    :param data: np.array - when loaded the data is stored here
    :param header: drs_fits.Header - when loaded the header is stored here
    :param fileset: List of DrsFile instances - this file can be used as
                    a container for a set of DrsFiles
    :param filesetnames: List of strings, the names of each DrsFile same
                         as doing list(map(lambda x: x.name, fileset))
    :param outfunc: Function, the output function to generate the output
                    name (using in constructing filename)
    :param inext: str, the input file extension [not used in DrsInputFile]
    :param dbname: str, the database name this file can go in
                (i.e. cailbration or telluric) [not used in DrsInputFile]
    :param dbkey: str, the database key [not used in DrsInputFile]
    :param rkeys: dict, the required header keys [not used in DrsInputFile]
    :param numfiles: int, the number of files represented by this file
                     instance [not used in DrsInputFile]
    :param shape: tuple, the numpy array shape for data (if present)
    :param hdict: drs_fits.Header - the header dictionary - temporary
                  storage key value pairs to add to header on
                  writing [not used in DrsInputFile]
    :param output_dict: dict, storage for data going to index
                  database [not used in DrsInputFile]
    :param datatype: str, the fits image type 'image' or
                     'header'  [not used in DrsInputFile]
    :param dtype: type, float or int - the type of data in the fits file
                  (mostly required for fits
                  images) [not used in DrsInputFile]
    :param is_combined: bool, if True this file represents a combined set
                        of files [not used in DrsInputFile]
    :param combined_list: list, the list of combined files that make this
                          file instance [not used in DrsInputFile]
    :param s1d: list, a list of s1d images attached to this file instance
                      (for use with extraction file
                       instances) [not used in DrsInputFile]
    :param kwargs: passed to required header keys (i.e. must be a DRS
                   Header key reference -- "KW_HEADERKEY")
                   [not used in DrsInputFile]

    - Parent class for Drs Fits File object (DrsFitsFile)
    """
    # deal with no instance2
    if instance2 is None:
        instance2 = instance1
    # set function name
    _ = display_func(instance1.params, 'newcopy', __NAME__)
    # copy this instances values (if not overwritten)
    # set name if not set
    if name is None:
        name = deepcopy(instance1.name)
    # set filetype
    if filetype is None:
        filetype = deepcopy(instance1.filetype)
    # set suffix
    if suffix is None:
        suffix = deepcopy(instance1.suffix)
    # set remove insuffix
    if remove_insuffix is None:
        remove_insuffix = deepcopy(instance1.remove_insuffix)
    # set prefix
    if prefix is None:
        prefix = deepcopy(instance1.prefix)
    # set filename
    if filename is None:
        filename = deepcopy(instance2.filename)
    # set intype
    if intype is None:
        intype = instance2.intype
    # set fiber
    if fiber is None:
        fiber = deepcopy(instance1.fiber)
    # set fibers
    if fibers is None:
        fibers = deepcopy(instance1.fibers)
    # set params
    if params is None:
        params = instance1.params
    # set path
    if path is None:
        path = deepcopy(instance2.path)
    # set basename
    if basename is None:
        basename = deepcopy(instance2.basename)
    # set inputdir
    if inputdir is None:
        inputdir = deepcopy(instance2.basename)
    # set directory
    if directory is None:
        directory = deepcopy(instance2.directory)
    # set data
    if data is None:
        data = deepcopy(instance2.data)
    # set header
    if header is None:
        # deep copy drs_fits.Header
        if isinstance(instance2.header, drs_fits.Header):
            header = instance2.header.copy()
            # deep copy astropy.io.fits.Header
        elif isinstance(instance2.header, drs_fits.fits.Header):
            header = instance2.header.copy()
        else:
            header = None
    # set fileset
    if fileset is None:
        if instance1.fileset is None:
            fileset = None
        elif isinstance(instance1.fileset, list):
            # set up new file set storage
            fileset = []
            # loop around file sets
            for fileseti in instance1.fileset:
                fileset.append(fileseti.completecopy(fileseti))
        else:
            fileset = instance1.fileset
    # set filesetnames
    if filesetnames is None:
        filesetnames = deepcopy(instance1.filesetnames)
    # set outfunc
    if outfunc is None:
        outfunc = instance1.outfunc
    # set inext
    if inext is None:
        inext = deepcopy(instance2.inext)
    # set dbname
    if dbname is None:
        dbname = deepcopy(instance1.dbname)
    # set dbkey
    if dbkey is None:
        dbkey = deepcopy(instance1.dbkey)
    # set rkeys
    if rkeys is None:
        rkeys = deepcopy(instance1.required_header_keys)
    # set numfiles
    if numfiles is None:
        numfiles = deepcopy(instance2.numfiles)
    # set shape
    if shape is None:
        shape = deepcopy(instance2.shape)
    # set hdict
    if hdict is None:
        # deep copy drs_fits.Header
        if isinstance(instance2.hdict, drs_fits.Header):
            hdict = instance2.hdict.copy()
        # deep copy astropy.io.fits.Header
        elif isinstance(instance2.hdict, drs_fits.fits.Header):
            hdict = instance2.hdict.copy()
        else:
            hdict = None
    # set output dict
    if output_dict is None:
        output_dict = deepcopy(instance2.output_dict)
    # set data type
    if datatype is None:
        datatype = deepcopy(instance2.datatype)
    # set dtype
    if dtype is None:
        dtype = deepcopy(instance2.dtype)
    # set is_combined
    if is_combined is None:
        is_combined = deepcopy(instance2.is_combined)
    # set combined_list
    if combined_list is None:
        combined_list = instance2.combined_list
    # set s1d
    if s1d is None:
        s1d = instance2.s1d
    # copy file specific header keys (from required header keys)
    new_hkeys = dict()
    if hkeys is not None:
        for key in instance1.required_header_keys:
            if key not in hkeys:
                new_hkeys[key] = str(instance1.required_header_keys[key])
            else:
                new_hkeys[key] = str(hkeys[key])
    # return new instance
    return drsfileclass(name, filetype, suffix, remove_insuffix, prefix,
                        fibers, fiber, params, filename, intype, path,
                        basename, inputdir, directory, data, header,
                        fileset, filesetnames, outfunc, inext, dbname,
                        dbkey, rkeys, numfiles, shape, hdict,
                        output_dict, datatype, dtype, is_combined,
                        combined_list, s1d, new_hkeys)

# =============================================================================
# End of code
# =============================================================================
