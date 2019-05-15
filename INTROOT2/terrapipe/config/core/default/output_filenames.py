#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 18:35

@author: cook
"""
import os

from terrapipe import constants
from terrapipe import config
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
# Get Logging function
WLOG = config.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry


# =============================================================================
# Define functions
# =============================================================================
def pp_file(params, **kwargs):
    func_name = __NAME__ + '.pp_file()'
    # get parameters from keyword arguments
    infile = kwargs.get('infile', None)
    outfile = kwargs.get('outfile', None)
    # deal with kwargs that are required
    if infile is None:
        WLOG(params, 'error', TextEntry('00-001-00017', args=[func_name]))
    if outfile is None:
        WLOG(params, 'error', TextEntry('00-001-00018', args=[func_name]))
    # construct out filename
    outfilename = infile.basename.replace(outfile.inext, outfile.ext)
    # get output path from params
    outpath = params['OUTPATH']
    # get output night name from params
    outdirectory = params['NIGHTNAME']
    # construct absolute path
    abspath = os.path.join(outpath, outdirectory, outfilename)
    # return absolute path
    return abspath


def debug_back(params, **kwargs):
    func_name = __NAME__ + '.debug_back()'
    # get parameters from keyword arguments
    infile = kwargs.get('infile', None)
    outfile = kwargs.get('outfile', None)
    fiber = kwargs.get('fiber', None)
    # deal with kwargs that are required
    if infile is None:
        WLOG(params, 'error', TextEntry('00-001-00017', args=[func_name]))
    if outfile is None:
        WLOG(params, 'error', TextEntry('00-001-00018', args=[func_name]))
    # construct out filename
    outext = outfile.ext.format(fiber)
    outfilename = infile.basename.replace(outfile.inext, outext)
    outfilename = 'DEBUG_' + outfilename
    # get output path from params
    outpath = params['OUTPATH']
    # get output night name from params
    outdirectory = params['NIGHTNAME']
    # construct absolute path
    abspath = os.path.join(outpath, outdirectory, outfilename)
    # return absolute path
    return abspath




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
