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
from apero.base import drs_exceptions
from apero.base import drs_misc
from apero import lang
from apero.core.constants import param_functions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.core.default.output_filenames.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get display func
display_func = drs_misc.display_func


# =============================================================================
# Define file output functions
# - Note should all have the same inputs and return
# =============================================================================
def general_file(params: ParamDict, infile: Any, outfile: Any,
                 fiber: Union[str, None] = None, path: Union[str, None] = None,
                 func: Union[str, None] = None,
                 remove_insuffix: Union[bool, None] = None,
                 prefix: Union[str, None] = None,
                 suffix: Union[str, None] = None,
                 filename: Union[str, None] = None) -> str:
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
    :param filename: not used for general file

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'general_file', __NAME__)
    # not used
    _ = filename
    # set function name from args
    if func is not None:
        func_name = '{0} [{1}]'.format(func, func_name)
    # deal with kwargs that are required
    if infile is None:
        raise DrsCodedException('00-001-00017', level='error',
                                targs=[func_name], func_name=func_name)
    if outfile is None:
        raise DrsCodedException('00-001-00018', level='error',
                                targs=[func_name], func_name=func_name)
    # try to get fiber from outfile
    if fiber is None:
        fiber = outfile.fiber
    # deal with fiber being required but still unset
    if outfile.fibers is not None and fiber is None:
        eargs = [outfile, func_name]
        raise DrsCodedException('00-001-00032', level='error',
                                targs=eargs, func_name=func_name)
    # set infile basename
    inbasename = infile.basename
    # get condition to remove input file prefix
    if remove_insuffix is None:
        remove_insuffix = outfile.remove_insuffix
    # if remove in suffix is True then remove it from inbasename
    if remove_insuffix and (infile.suffix is not None):
        # get the infile suffix
        insuffix = str(infile.suffix)
        # check for fibers
        if infile.fibers is not None:
            for infiber in infile.fibers:
                insuffix = str(infile.suffix)
                insuffix = '{0}_{1}'.format(insuffix, infiber.upper())
                # check that infile suffix is not None
                if insuffix in inbasename:
                    inbasename = inbasename.replace(insuffix, '')
        elif insuffix in inbasename:
            inbasename = inbasename.replace(insuffix, '')

    # get kwargs where default dependent on required arguments
    if prefix is None:
        prefix = outfile.prefix
    if suffix is None:
        suffix = outfile.suffix
    # construct out filename
    inext = infile.filetype
    outext = outfile.filetype
    outfilename = get_outfilename(params, inbasename, prefix=prefix,
                                  suffix=suffix, inext=inext, outext=outext,
                                  fiber=fiber)
    # deal with no given path (default)
    if path is None:
        # get output path from params
        outpath = params['OUTPATH']
        # check if outpath is set
        if outpath is None:
            raise DrsCodedException('00-001-00023', level='error',
                                    targs=[func_name], func_name=func_name)
        # get output night name from params
        if params['NIGHTNAME'] is None:
            outdirectory = ''
        else:
            outdirectory = params['NIGHTNAME']
        # make sure night name folder exists (create it if not)
        make_night_name(params, outdirectory, outpath)
        # construct absolute path
        abspath = os.path.join(outpath, outdirectory, outfilename)
    else:
        abspath = os.path.join(path, outfilename)
    # return absolute path
    return abspath


def npy_file(params: ParamDict, infile: Any, outfile: Any,
             fiber: Union[str, None] = None, path: Union[str, None] = None,
             func: Union[str, None] = None,
             remove_insuffix: Union[bool, None] = None,
             prefix: Union[str, None] = None,
             suffix: Union[str, None] = None,
             filename: Union[str, None] = None) -> str:
    """
    Construct a NPY filename from infile/outfile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param func: str, the function name if set (for errors)
    :param fiber: not used for npy_file
    :param path: not used for npy_file
    :param prefix: not used for npy_file
    :param suffix: not used for npy_file
    :param filename: not used for npy_file

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'npy_file', __NAME__)
    # deal with unused
    _ = fiber, path, remove_insuffix, prefix, suffix, filename
    # set function name from args
    if func is not None:
        func_name = '{0} [{1}]'.format(func, func_name)

    # get out file and report error if not set
    if outfile is None:
        raise DrsCodedException('00-001-00018', level='error',
                                targs=[func_name], func_name=func_name)
    # make sure filetype is .npy
    filetype = outfile.filetype
    if '.npy' not in filetype:
        raise DrsCodedException('00-001-00033', level='error',
                                targs=[filetype], func_name=func_name)
    # update keywords func name
    return general_file(params, infile, outfile, func=func_name)


def debug_file(params: ParamDict, infile: Any, outfile: Any,
               fiber: Union[str, None] = None, path: Union[str, None] = None,
               func: Union[str, None] = None,
               remove_insuffix: Union[bool, None] = None,
               prefix: Union[str, None] = None,
               suffix: Union[str, None] = None,
               filename: Union[str, None] = None) -> str:
    """
    Construct a NPY filename from infile/outfile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param func: str, the function name if set (for errors)
    :param prefix: str, if set the prefix of the file (defaults to
                   outfile.prefix)
    :param fiber: not used for debug_file
    :param path: not used for debug_file
    :param remove_insuffix: not used for debug_file
    :param suffix: not used for debug_file
    :param filename: not used for debug_file

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'npy_file', __NAME__)
    # deal with not used
    _ = fiber, path, remove_insuffix, suffix, filename
    # set function name from args
    if func is not None:
        func_name = '{0} [{1}]'.format(func, func_name)
    # deal with no prefix
    if prefix is None:
        prefix = outfile.prefix
    # get out file and report error if not set
    if outfile is not None:
        prefix = 'DEBUG_' + prefix
    else:
        prefix = 'DEBUG_'
    # return absolute path
    return general_file(params, infile, outfile, prefix=prefix, func=func_name)


def blank(params: ParamDict, infile: Any, outfile: Any,
               fiber: Union[str, None] = None, path: Union[str, None] = None,
               func: Union[str, None] = None,
               remove_insuffix: Union[bool, None] = None,
               prefix: Union[str, None] = None,
               suffix: Union[str, None] = None,
               filename: Union[str, None] = None) -> str:
    """
    Construct a blank filename from infile

    :param params: ParamDict, paremeter dictionary of constants
    :param infile: DrsFitsFile, input file - must be defined
    :param outfile: DrsFitsFile, output file - must be defined
    :param func: str, the function name if set (for errors)
    :param fiber: not used for blank output
    :param path: not used for blank output
    :param remove_insuffix: not used for blank output
    :param prefix: not used for blank output
    :param suffix: not used for blank output
    :param filename: not used for blank output

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'blank', __NAME__)
    # deal with not used
    _ = fiber, path, remove_insuffix, prefix, suffix, filename
    # set function name from args
    if func is None:
        func_name = '{0} [{1}]'.format(func, func_name)
    # deal with kwargs that are required
    if infile is None:
        _ = outfile
        raise DrsCodedException('00-001-00017', level='error',
                                targs=[func_name], func_name=func_name)
    # return absolute path
    return infile.filename


def set_file(params: ParamDict, infile: Any, outfile: Any,
               fiber: Union[str, None] = None, path: Union[str, None] = None,
               func: Union[str, None] = None,
               remove_insuffix: Union[bool, None] = None,
               prefix: Union[str, None] = None,
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
    :param fiber: not used for set_file
    :param remove_insuffix: not used for set_file
    :param prefix: not used for set file

    :return: the aboslute path to the file
    """
    # set function name
    func_name = display_func(params, 'set_file', __NAME__)
    # deal with not used
    _ = fiber, remove_insuffix, prefix
    # set function name from args
    if func is None:
        func_name = '{0} [{1}]'.format(func, func_name)
    # deal with no outfile set
    if outfile is None:
        _ = infile
        raise DrsCodedException('00-001-00018', level='error',
                                targs=[func_name], func_name=func_name)
    # get filename from outfile if None
    if filename is None:
        filename = outfile.basename
    # deal with no file name set and filename must be a basename (no path)
    if filename is None:
        raise DrsCodedException('00-001-00041', level='error',
                                targs=[func_name], func_name=func_name)
    else:
        filename = os.path.basename(filename)
    # get extension
    if suffix is None:
        outext = outfile.filetype
    else:
        outext = suffix + outfile.filetype
    # check for extension and set filename
    if filename.endswith(outext):
        outfilename = str(filename)
    else:
        outfilename = filename + outext
    # deal with no given path (default)
    if path is None:
        # get output path from params
        outpath = params['OUTPATH']
        # check if outpath is set
        if outpath is None:
            raise DrsCodedException('00-001-00023', level='error',
                                    targs=[func_name], func_name=func_name)
        # get output night name from params
        outdirectory = params['NIGHTNAME']
        # make sure night name folder exists (create it if not)
        make_night_name(params, outdirectory, outpath)
        # construct absolute path
        abspath = os.path.join(outpath, outdirectory, outfilename)
    else:
        abspath = os.path.join(path, outfilename)
    # return absolute path
    return abspath


# =============================================================================
# Define user functions
# =============================================================================
def get_outfilename(params: ParamDict, infilename: str,
                    prefix: Union[str, None] = None,
                    suffix: Union[str, None] = None,
                    inext: Union[str, None] = None,
                    outext: Union[str, None] = None,
                    fiber: Union[str, None] = None) -> str:
    """
    Get the output filename from a input filename (with inext) and add a
    prefix/suffix fiber etc

    :param params: ParamDict, paremeter dictionary of constants
    :param infilename: str, the infile name
    :param prefix: str, if set the prefix of the file
    :param suffix: str, if set the suffix of the file
    :param inext: str, the infile extension (to remove)
    :param outext: str, the outfile extension (to add)
    :param fiber: str, the fiber to add (if set)

    :return: str, the filename correct for prefix/suffix/fiber etc
    """
    # set function name
    func_name = display_func(params, 'get_outfilename', __NAME__)
    # make surte infilename is a basename not a path
    infilename = os.path.basename(infilename)
    # deal with fiber
    if fiber is not None:
        suffix = '{0}_{1}'.format(suffix, fiber.upper())
    # remove extension
    if inext is None:
        inext = infilename.split('.')[-1]
    # strip filename of extenstion
    if infilename.endswith(inext):
        outfilename = str(infilename[:-len(inext)])
    else:
        eargs = [infilename, inext, func_name]
        raise DrsCodedException('00-001-00031', level='error',
                                targs=eargs, func_name=func_name)
    # add prefix and suffix
    if prefix is not None:
        outfilename = '{0}{1}'.format(prefix, outfilename)
    if suffix is not None:
        outfilename = '{0}{1}'.format(outfilename, suffix)
    # add back extention or add new one
    if outext is None:
        if not suffix.endswith(inext):
            outfilename = '{0}{1}'.format(outfilename, inext)
    elif not suffix.endswith(outext):
        outfilename = '{0}{1}'.format(outfilename, outext)
    # return filename
    return outfilename


def make_night_name(params: ParamDict, nightname: Union[str, None],
                    path: str) -> str:
    """
    Make a directory with a night directory given - and also add the directory
    if needed

    :param params: ParamDict, parameter dictionary constants dictionary
    :param nightname: str or None, if set add this to the directory path
    :param path: str, the absolute path (above nightname level)

    :return: str, the path with the night name added (if set)
    """
    # set function name
    func_name = display_func(params, 'get_outfilename', __NAME__)
    # deal with no night name set
    if nightname is None:
        return path
    # make full path
    full_path = os.path.join(path, nightname)

    rel_path = os.path.join(os.path.curdir, nightname)

    # if full path exists then just return
    if os.path.exists(full_path):
        return full_path
    # else try to create it
    else:
        try:
            # save current path
            cwd = os.getcwd()
            # change to path
            os.chdir(path)
            # attempt to make folders
            os.makedirs(rel_path)
            # change back to current path
            os.chdir(cwd)
        except Exception as e:
            eargs = [rel_path, path, type(e), e, func_name]
            raise DrsCodedException('09-002-00002', level='error',
                                    targs=eargs, func_name=func_name)
    # try to see if path exists one last time
    if os.path.exists(full_path):
        return full_path
    else:
        eargs = [rel_path, path, func_name]
        raise DrsCodedException('09-002-00003', level='error',
                                targs=eargs, func_name=func_name)


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
