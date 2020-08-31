#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 18:35

@author: cook
"""
import os
from typing import Any, Union

from apero.base import base
from apero.base import drs_misc
from apero.core.instruments.default import output_filenames
from apero import lang
from apero.core.constants import param_functions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.spirou.output_filenames.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get display func
display_func = drs_misc.display_func


# =============================================================================
# Define functions
# =============================================================================
def general_file(params: ParamDict, infile: Any, outfile: Any,
                 fiber: Union[str, None] = None, path: Union[str, None] = None,
                 func: Union[str, None] = None,
                 remove_insuffix: Union[bool, None] = None,
                 prefix: Union[str, None] = None,
                 suffix: Union[str, None] = None) -> str:
    """
    Construct a general absolute filename from infile/outfile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
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

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'general_file', __NAME__)
    # set function name from args
    if func is not None:
        func_name = '{0} [{1}]'.format(func, func_name)
    return output_filenames.general_file(params, infile, outfile, fiber,
                                         path, func_name, remove_insuffix,
                                         prefix, suffix)


def npy_file(params: ParamDict, infile: Any, outfile: Any,
             func: Union[str, None] = None) -> str:
    """
    Construct a NPY filename from infile/outfile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param func: str, the function name if set (for errors)

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'npy_file', __NAME__)
    # set function name from args
    if func is not None:
        func_name = '{0} [{1}]'.format(func, func_name)

    return output_filenames.npy_file(params, infile, outfile, func=func_name)


def debug_file(params: ParamDict, infile: Any, outfile: Any,
               func: Union[str, None] = None,
               prefix: Union[str, None] = None) -> str:
    """
    Construct a NPY filename from infile/outfile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param func: str, the function name if set (for errors)
    :param prefix: str, if set the prefix of the file (defaults to
                   outfile.prefix)

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'npy_file', __NAME__)
    # set function name from args
    if func is not None:
        func_name = '{0} [{1}]'.format(func, func_name)
    return output_filenames.debug_file(params, infile, outfile,
                                       func_name, prefix)


def calib_file(params: ParamDict, infile: Any, outfile: Any,
               fiber: Union[str, None] = None, path: Union[str, None] = None,
               func: Union[str, None] = None,
               remove_insuffix: Union[bool, None] = None,
               suffix: Union[str, None] = None) -> str:
    """
    Construct a general absolute filename from infile/outfile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param fiber: str, the fiber - must be set if infile.fibers is populated
    :param path: str, the path the file should have (if not set, set to
                 params['OUTPATH']  with params['NIGHTNAME'] if set)
    :param func: str, the function name if set (for errors)
    :param remove_insuffix: bool if set removes input suffix if not set
                            defaults to the outfile.remove_insuffix
    :param suffix: str, if set the suffix of the file (defaults to
                   outfile.suffix)

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'general_file', __NAME__)
    # set function name from args
    if func is not None:
        func_name = '{0} [{1}]'.format(func, func_name)
    # get nightname
    # nightname = kwargs.get('nightname', None)
    # get prefix
    if outfile is None:
        # prefix = _calibration_prefix(params, nightname)
        prefix = ''
    else:
        # prefix = _calibration_prefix(params, nightname) + outfile.prefix
        prefix = outfile.prefix
    # return general file with prefix updated
    return output_filenames.general_file(params, infile, outfile, fiber, path,
                                         func_name, remove_insuffix, prefix,
                                         suffix)


def blank(params: ParamDict, infile: Any, outfile: Any,
          func: Union[str, None] = None) -> str:
    """
    Construct a blank filename from infile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param func: str, the function name if set (for errors)

    :return: the aboslute path to the file
    """
    return output_filenames.blank(params, infile, outfile, func)


def set_file(params: ParamDict, infile: Any, outfile: Any,
             path: Union[str, None] = None,
             func: Union[str, None] = None,
             suffix: Union[str, None] = None,
             filename: Union[str, None] = None) -> str:
    """
    Construct a absolute filename based on the filename, can replace
    suffix

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param path: str, the path the file should have (if not set, set to
                 params['OUTPATH']  with params['NIGHTNAME'] if set)
    :param func: str, the function name if set (for errors)
    :param suffix: str, if set the suffix of the file (defaults to
                   outfile.suffix)
    :param filename: str, the filename to give the file

    :return: the aboslute path to the file
    """
    return output_filenames.set_file(params, infile, outfile, path, func,
                                     suffix, filename)


# =============================================================================
# Define worker functions
# =============================================================================
def _calibration_prefix(params: ParamDict,
                        nightname: Union[str, None] = None) -> str:
    """
    Define the calibration database file prefix (using arg_night_name)

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
                NIGHTNAME: string, the folder within data raw directory
                           containing files (also reduced directory) i.e.
                           /data/raw/20170710 would be "20170710"
    :param nightname: str, sets the night name (if None set from
                      params['NIGHTNAME']

    :return calib_prefix: string the calibration database prefix to add to all
                          calibration database files
    """
    if nightname is None:
        nightname = params['NIGHTNAME']
    # remove separators
    calib_prefix = nightname.replace(os.sep, '_')
    # return calib_prefix
    return calib_prefix + '_'


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
