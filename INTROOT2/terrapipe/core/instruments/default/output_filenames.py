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
    func_name = kwargs.get('func', __NAME__ + '.general_file()')
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
    # get kwargs where default dependent on required arguments
    prefix = kwargs.get('prefix', outfile.prefix)
    suffix = kwargs.get('suffix', outfile.suffix)
    # construct out filename
    inext = infile.filetype
    outext = outfile.filetype
    outfilename = get_outfilename(params, infile.basename, prefix=prefix,
                                  suffix=suffix, inext=inext, outext=outext,
                                  fiber=fiber)
    # deal with no given path (default)
    if path is None:
        # get output path from params
        outpath = params['OUTPATH']
        # get output night name from params
        outdirectory = params['NIGHTNAME']
        # construct absolute path
        abspath = os.path.join(outpath, outdirectory, outfilename)
    else:
        abspath = os.path.join(path, outfilename)
    # return absolute path
    return abspath


def npy_file(params, **kwargs):
    func_name = __NAME__ + '.npy_file()'
    func = kwargs.get('func', None)
    if func is None:
        func = func_name
    else:
        func = '{0} and {1}'.format(func, func_name)
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
    func_name = __NAME__ + '.debug_back()'
    func = kwargs.get('func', None)
    if func is None:
        func = func_name
    else:
        func = '{0} and {1}'.format(func, func_name)
    # update keywords func name
    kwargs['func'] = func
    # get parameters from keyword arguments
    outfile = kwargs.get('outfile', None)
    if outfile is not None:
        prefix = 'DEBUG_' + kwargs.get('prefix', outfile.prefix)
    else:
        prefix = 'DEBUG_'
    # return absolute path
    return general_file(params, prefix=prefix, **kwargs)





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
        outfilename = '{0}{1}'.format(outfilename, inext)
    else:
        outfilename = '{0}{1}'.format(outfilename, outext)
    # return filename
    return outfilename


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
