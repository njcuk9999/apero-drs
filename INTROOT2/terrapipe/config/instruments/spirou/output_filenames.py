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
__NAME__ = 'config.instruments.spirou.output_filenames.py'
__INSTRUMENT__ = 'SPIROU'
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


def dark_file(params, **kwargs):
    func_name = __NAME__ + '.dark_file()'
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
    # add calibration prefix
    outfilename = _calibration_prefix(params) + outfilename
    # get output path from params
    outpath = params['OUTPATH']
    # get output night name from params
    outdirectory = params['NIGHTNAME']
    # construct absolute path
    abspath = os.path.join(outpath, outdirectory, outfilename)
    # return absolute path
    return abspath


def sky_file(params, **kwargs):
    func_name = __NAME__ + '.dark_file()'
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
    # add calibration prefix
    outfilename = _calibration_prefix(params) + outfilename
    # get output path from params
    outpath = params['OUTPATH']
    # get output night name from params
    outdirectory = params['NIGHTNAME']
    # construct absolute path
    abspath = os.path.join(outpath, outdirectory, outfilename)
    # return absolute path
    return abspath


def badpix_file(params, **kwargs):
    func_name = __NAME__ + '.dark_file()'
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
    # add calibration prefix
    outfilename = _calibration_prefix(params) + outfilename
    # get output path from params
    outpath = params['OUTPATH']
    # get output night name from params
    outdirectory = params['NIGHTNAME']
    # construct absolute path
    abspath = os.path.join(outpath, outdirectory, outfilename)
    # return absolute path
    return abspath


def backmap_file(params, **kwargs):
    func_name = __NAME__ + '.dark_file()'
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
    # add calibration prefix
    outfilename = _calibration_prefix(params) + outfilename
    # get output path from params
    outpath = params['OUTPATH']
    # get output night name from params
    outdirectory = params['NIGHTNAME']
    # construct absolute path
    abspath = os.path.join(outpath, outdirectory, outfilename)
    # return absolute path
    return abspath


# =============================================================================
# Define worker functions
# =============================================================================
def _calibration_prefix(params):
    """
    Define the calibration database file prefix (using arg_night_name)

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
                NIGHTNAME: string, the folder within data raw directory
                           containing files (also reduced directory) i.e.
                           /data/raw/20170710 would be "20170710"
    :return calib_prefix: string the calibration database prefix to add to all
                          calibration database files
    """
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
