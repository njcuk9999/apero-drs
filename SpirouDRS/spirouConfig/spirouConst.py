#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spirouConst.py

Constants used throughout DRS that are more complicated than simple objects
i.e. require a function and maybe input parameters

Created on 2017-11-13 at 14:22

@author: cook

Version 0.0.1
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouConst.py'
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def ARG_FILE_NAMES():
    # empty file names
    arg_file_names = []
    # get run time parameters
    rparams = list(sys.argv)
    # get night name and filenames
    if len(rparams) > 1:
        for r_it in range(2, len(rparams)):
            arg_file_names.append(str(rparams[r_it]))
    # return arg_file_names
    return arg_file_names


def ARG_NIGHT_NAME():
    # st
    arg_night_name = ''
    # get run time parameters
    rparams = list(sys.argv)
    # get night name
    if len(rparams) > 1:
        arg_night_name = str(rparams[1])
    # return arg_night_name
    return arg_night_name


def CALIBDB_MASTERFILE(p):
    masterfile = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
    return masterfile


def CALIBDB_LOCKFILE(p):
    lockfilename = os.path.join(p['DRS_CALIB_DB'], 'lock_calibDB')
    return lockfilename


def FORBIDDEN_COPY_KEYS():
    forbidden_keys = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                      'EXTEND', 'COMMENT', 'CRVAL1', 'CRPIX1', 'CDELT1',
                      'CRVAL2', 'CRPIX2', 'CDELT2', 'BSCALE', 'BZERO',
                      'PHOT_IM', 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB']
    # return keys
    return forbidden_keys


def FITSFILENAME(p):

    arg_file_names = p['arg_file_names']
    arg_night_name = p['arg_night_name']
    # construct fits file name (full path + first file in arguments)
    if len(arg_file_names) > 0:
        fits_fn = os.path.join(p['DRS_DATA_RAW'], arg_night_name,
                               arg_file_names[0])
    else:
        fits_fn = None
    # return fitsfilename
    return fits_fn


def LOG_OPT(p):

    # deal with the log_opt "log option"
    #    either {program}   or {program}:{prefix}   or {program}:{prefix}+[...]

    arg_file_names = p['arg_file_names']
    program = p['program']

    if len(arg_file_names) == 0:
        log_opt = program
    elif len(arg_file_names) == 1:
        index = arg_file_names[0].find('.')
        lo_arg = [program, arg_file_names[0][index - 5: index]]
        log_opt = '{0}:{1}'.format(*lo_arg)
    else:
        index = arg_file_names[0].find('.')
        lo_arg = [program, arg_file_names[0][index - 5: index]]
        log_opt = '{0}:{1}+[...]'.format(*lo_arg)

    return log_opt


def MANUAL_FILE(p):
    manual_file = os.path.join(p['DRS_MAN'].replace(p['program'], '.info'))
    return manual_file


def NBFRAMES(p):
    # Number of frames = length of arg_file_names
    nbframes = len(p['arg_file_names'])
    # return number of frames
    return nbframes


def PROGRAM():
    # get run time parameters
    rparams = list(sys.argv)
    # get program name
    program = os.path.basename(rparams[0]).split('.py')[0]
    # return program
    return program


def RAW_DIR(p):
    raw_dir = os.path.join(p['DRS_DATA_RAW'], p['arg_night_name'])
    return raw_dir


def REDUCED_DIR(p):

    # set the reduced directory from DRS_DATA_REDUC and 'arg_night_name'
    reduced_dir = os.path.join(p['DRS_DATA_REDUC'], p['arg_night_name'])
    # return reduced directory
    return reduced_dir




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
