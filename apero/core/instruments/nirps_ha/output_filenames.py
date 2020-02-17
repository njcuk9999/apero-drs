#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 18:35

@author: cook
"""
import os

from apero.core import constants
from apero import core
from apero.core.instruments.default import output_filenames
from apero import locale


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.nirps_ha.output_filenames.py'
__INSTRUMENT__ = 'NIRPS_HA'
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
# Define functions
# =============================================================================
def general_file(params, **kwargs):
    func_name = __NAME__ + '.general_file()'
    func = kwargs.get('func', None)
    if func is None:
        func = func_name
    else:
        func = '{0} and {1}'.format(func, func_name)
    # update keywords func name
    kwargs['func'] = func
    return output_filenames.general_file(params, **kwargs)


def debug_file(params, **kwargs):
    func_name = __NAME__ + '.debug_file()'
    func = kwargs.get('func', None)
    if func is None:
        func = func_name
    else:
        func = '{0} and {1}'.format(func, func_name)
    # update keywords func name
    kwargs['func'] = func
    return output_filenames.debug_file(params, **kwargs)


def npy_file(params, **kwargs):
    func_name = __NAME__ + '.npy_file()'
    func = kwargs.get('func', None)
    if func is None:
        func = func_name
    else:
        func = '{0} and {1}'.format(func, func_name)
    # update keywords func name
    kwargs['func'] = func
    return output_filenames.npy_file(params, **kwargs)


def calib_file(params, **kwargs):
    func_name = __NAME__ + '.calib_file()'
    func = kwargs.get('func', None)
    if func is None:
        func = func_name
    else:
        func = '{0} and {1}'.format(func, func_name)
    # get output file
    outfile = kwargs.get('outfile', None)
    # get nightname
    nightname = kwargs.get('nightname', None)
    # get prefix
    if outfile is None:
        prefix = _calibration_prefix(params, nightname)
    else:
        prefix = _calibration_prefix(params, nightname) + outfile.prefix
    # update keywords func name
    kwargs['func'] = func
    # return general file with prefix updated
    return output_filenames.general_file(params, prefix=prefix, **kwargs)


def blank(params, **kwargs):
    return output_filenames.blank(params, **kwargs)


def set_file(params, **kwargs):
    return output_filenames.set_file(params, **kwargs)


# =============================================================================
# Define worker functions
# =============================================================================
def _calibration_prefix(params, nightname=None):
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
