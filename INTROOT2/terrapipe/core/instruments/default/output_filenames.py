#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 18:35

@author: cook
"""
import os

from terrapipe.core import constants
from terrapipe import core
from terrapipe import locale


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.core.default.output_filenames.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry


# =============================================================================
# Define file functions
# =============================================================================
def general_file(params, **kwargs):
    func = __NAME__ + '.general_file()'
    if 'func' in kwargs:
        func_name = '{0} [{1}]'.format(kwargs.get('func', ''), func)
    else:
        func_name = func
    # get parameters from keyword arguments
    infile = kwargs.get('infile', None)
    outfile = kwargs.get('outfile', None)
    fiber = kwargs.get('fiber', None)
    path = kwargs.get('path', None)
    # deal with kwargs that are required
    if infile is None:
        WLOG(params, 'error', TextEntry('00-001-00017', args=[func_name]))
    if outfile is None:
        WLOG(params, 'error', TextEntry('00-001-00018', args=[func_name]))
    # try to get fiber from outfile
    if fiber is None:
        fiber = outfile.fiber
    # deal with fiber being required but still unset
    if outfile.fibers is not None and fiber is None:
        eargs = [outfile, func_name]
        WLOG(params, 'error', TextEntry('00-001-00032', args=eargs))

    # set infile basename
    inbasename = infile.basename
    # get condition to remove input file prefix
    remove_insuffix = kwargs.get('remove_insuffix', outfile.remove_insuffix)
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
    prefix = kwargs.get('prefix', outfile.prefix)
    suffix = kwargs.get('suffix', outfile.suffix)
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
            WLOG(params, 'error', TextEntry('01-001-00023', args=[func_name]))
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


def npy_file(params, **kwargs):
    func = __NAME__ + '.npy_file()'
    if 'func' in kwargs:
        func_name = '{0} [{1}]'.format(kwargs.get('func', ''), func)
    else:
        func_name = func
    # get out file and report error if not set
    outfile = kwargs.get('outfile', None)
    if outfile is None:
        WLOG(params, 'error', TextEntry('00-001-00018', args=[func_name]))
    # make sure filetype is .npy
    filetype = outfile.filetype
    if '.npy' not in filetype:
        WLOG(params, 'error', TextEntry('00-001-00033', args=[filetype]))
    # update keywords func name
    kwargs['func'] = func
    return general_file(params, **kwargs)


def debug_file(params, **kwargs):
    func = __NAME__ + '.debug_back()'
    if 'func' in kwargs:
        func_name = '{0} [{1}]'.format(kwargs.get('func', ''), func)
    else:
        func_name = func
    # update keywords func name
    kwargs['func'] = func_name
    # get parameters from keyword arguments
    outfile = kwargs.get('outfile', None)
    if outfile is not None:
        prefix = 'DEBUG_' + kwargs.get('prefix', outfile.prefix)
    else:
        prefix = 'DEBUG_'
    # return absolute path
    return general_file(params, prefix=prefix, **kwargs)


def blank(params, **kwargs):
    func = __NAME__ + '.blank()'
    if 'func' in kwargs:
        func_name = '{0} [{1}]'.format(kwargs.get('func', ''), func)
    else:
        func_name = func
    # get parameters from keyword arguments
    infile = kwargs.get('infile', None)
    # deal with kwargs that are required
    if infile is None:
        WLOG(params, 'error', TextEntry('00-001-00017', args=[func_name]))
    # return absolute path
    return infile.filename


def set_file(params, **kwargs):
    func = __NAME__ + '.set_file()'
    if 'func' in kwargs:
        func_name = '{0} [{1}]'.format(kwargs.get('func', ''), func)
    else:
        func_name = func
    # get set filename from kwargs
    filename = kwargs.get('filename', None)
    # get output file
    outfile = kwargs.get('outfile', None)
    # deal with no outfile set
    if outfile is None:
        WLOG(params, 'error', TextEntry('00-001-00018', args=[func_name]))
    # get filename from outfile if None
    if filename is None:
        filename = outfile.filename
    # deal with no file name set
    if filename is None:
        WLOG(params, 'error', TextEntry('00-001-00041', args=[func_name]))
    # get suffix
    suffix = kwargs.get('suffix', None)
    # get path
    path = kwargs.get('path', None)
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
            WLOG(params, 'error', TextEntry('01-001-00023', args=[func_name]))
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
def get_outfilename(params, infilename, prefix=None, suffix=None,
                    inext=None, outext=None, fiber=None):
    func_name = __NAME__ + '.get_outfilename()'
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
        WLOG(params, 'error', TextEntry('00-001-00031', args=eargs))
        outfilename = ''
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


def make_night_name(params, nightname, path):
    func_name = __NAME__ + '.make_night_name()'
    # make full path
    full_path = os.path.join(path, nightname)

    rel_path = os.path.join(os.path.curdir, nightname)

    # if full path exists then just return
    if os.path.exists(full_path):
        return
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
            WLOG(params, 'error', TextEntry('09-002-00002', args=eargs))
    # try to see if path exists one last time
    if os.path.exists(full_path):
        return
    else:
        eargs = [rel_path, path, func_name]
        WLOG(params, 'error', TextEntry('09-002-00003', args=eargs))


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
