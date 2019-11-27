#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 18:35

@author: cook
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'recipe_definitions.py'
__INSTRUMENT__ = 'SPIROU'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get param dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# TODO: replace with apero
# Define proxy classes (from input_redo)
# =============================================================================
class Entry:
    """
    Proxy class to avoid changes below
    """
    def __init__(self):
        pass
    def __call__(self, errortype, args):
        return errortype

# =============================================================================
# TODO: replace with apero
# Define proxy variables
# =============================================================================
TextEntry = Entry()


# =============================================================================
# Define functions
# =============================================================================
def general_file(params, **kwargs):
    func_name = __NAME__ + '.general_file()'
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


def calib_file(params, **kwargs):
    func_name = __NAME__ + '.general_file()'
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


def debug_file(params, **kwargs):
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
