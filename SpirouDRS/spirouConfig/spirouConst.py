#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spirouConst.py

Constants used throughout DRS that are more complicated than simple objects
i.e. require a function and maybe input parameters

Created on 2017-11-13 at 14:22

@author: cook

Import rules: Only from spirouConfigFile

Version 0.0.1
"""
from __future__ import division
import sys
import os
from . import spirouConfigFile

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouConst.py'
# Get version and author
__version__ = 'Unknown'
__author__ = 'Unknown'
__release__ = 'Unknown'
__date__ = 'Unknown'


# =============================================================================
# Define pre-functions
# =============================================================================
def CONFIGFILE():
    # Name of main config file (in CONFIGFOLDER() )
    config_file = 'config.py'
    return config_file


def PACKAGE():
    # Module package name (Used in code so MUST equal name of parent package)
    package = 'SpirouDRS'
    return package


def NAME():
    drs_name = 'SPIROU'
    return drs_name


def VERSION():
    # Module Version (Used in all sub-packages)
    version = '0.0.055'
    return version


def RELEASE():
    release = 'alpha'
    return release


def AUTHORS():
    # Module Authors (Used in all sub-packages)
    authors = 'N. Cook, F. Bouchy, E. Artigau, I. Boisse, M. Hobson, C. Moutou'
    return authors


def LATEST_EDIT():
    # Module last edit date (in form YYYY-MM-DD) used in all sub-packages
    date = '2018-01-10'
    return date


def CONFIGFOLDER():
    # Name of main config folder (relative to PACKAGE() level)
    config_folder = '../config'
    return config_folder


def CDATA_FOLDER():
    # Name of constant data folder (relative to PACKAGE() level)
    const_data_folder = './data'
    return const_data_folder


# =============================================================================
# Get constants from constant file
# =============================================================================
# get constants from file
ckwargs = dict(package=PACKAGE(), configfolder=CONFIGFOLDER(),
               configfile=CONFIGFILE(), return_raw=False)
pp = spirouConfigFile.read_config_file(**ckwargs)


# =============================================================================
# Define General functions
# =============================================================================
def INTERACITVE_PLOTS_ENABLED():
    # Whether to use plt.ion (if True) or to use plt.show (if False)
    interactive_plots = True
    return interactive_plots


def DEBUG():
    # TODO: for release this should be 0
    debug = pp['DRS_DEBUG']
    return debug


# =============================================================================
# Define File functions
# =============================================================================
def ARG_FILE_NAMES(p):
    # see if already defined
    if 'ARG_FILE_NAMES' in p:
        return p['ARG_FILE_NAMES']
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


def ARG_NIGHT_NAME(p):
    # see if already defined
    if 'ARG_NIGHT_NAME' in p:
        return p['ARG_NIGHT_NAME']
    # set up empty string
    arg_night_name = ''
    # get run time parameters
    rparams = list(sys.argv)
    # get night name
    if len(rparams) > 1:
        arg_night_name = str(rparams[1])
    # return arg_night_name
    return arg_night_name


def NBFRAMES(p):
    # Number of frames = length of arg_file_names
    nbframes = len(p['arg_file_names'])
    # return number of frames
    return nbframes


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
        fitsfilename = os.path.join(p['DRS_DATA_RAW'], arg_night_name,
                                    arg_file_names[0])
    else:
        fitsfilename = None
    # return fitsfilename
    return fitsfilename


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


def PROGRAM():
    # get run time parameters
    rparams = list(sys.argv)
    # get program name
    program = os.path.basename(rparams[0]).split('.py')[0]
    # return program
    return program


def MANUAL_FILE(p):
    manual_file = os.path.join(p['DRS_MAN'].replace(p['program'], '.info'))
    return manual_file


def RAW_DIR(p):
    raw_dir = os.path.join(p['DRS_DATA_RAW'], p['arg_night_name'])
    return raw_dir


def REDUCED_DIR(p):
    # set the reduced directory from DRS_DATA_REDUC and 'arg_night_name'
    reduced_dir = os.path.join(p['DRS_DATA_REDUC'], p['arg_night_name'])
    # return reduced directory
    return reduced_dir


def CCF_TABLE_FILE(p):
    # start with the CCF fits file name
    newfilename = CCF_FITS_FILE(p)
    # we want to save the file as a tbl file not a fits file
    newfilename = newfilename.replace('.fits', '.tbl')
    # join the new filename to the reduced directory
    ccf_table_file = os.path.join(p['REDUCED_DIR'], newfilename)
    # return the new ccf table file location and name
    return ccf_table_file


def CCF_FITS_FILE(p):
    # get new extension using ccf_mask without the extention
    newext = '_ccf_' + p['ccf_mask'].replace('.mas', '')
    # set the new filename as the reference file without the _e2ds
    newfilename = p['reffile'].replace('_e2ds', newext)
    # return the new ccf table file location and name
    return newfilename


# =============================================================================
# Define calibration database functions
# =============================================================================
def CALIBDB_MASTERFILE(p):
    masterfilepath = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
    return masterfilepath


def CALIBDB_LOCKFILE(p):
    lockfilepath = os.path.join(p['DRS_CALIB_DB'], 'lock_calibDB')
    return lockfilepath


def CALIB_PREFIX(p):
    argnightname = p['arg_night_name'].split('/')[-1]
    calib_prefix = argnightname + '_'
    return calib_prefix


# =============================================================================
# Define formatting functions
# =============================================================================
def CONFIG_KEY_ERROR(key, location=None):
    if location is None:
        cerrmsg = 'key "{0}" is not defined'
        return cerrmsg.format(key)
    else:
        cerrmsg = 'key "{0}" must be defined in file (located at {1})'
        return cerrmsg.format(key, location)


def DATE_FMT_HEADER():
    date_fmt_header = '%Y-%m-%d-%H:%M:%S.%f'
    return date_fmt_header


def DATE_FMT_CALIBDB():
    date_fmt_calibdb = '%Y-%m-%d-%H:%M:%S.%f'
    return date_fmt_calibdb


# =============================================================================
# Define logger functions
# =============================================================================
def LOG_TRIG_KEYS():
    # The trigger character to display for each
    trig_key = dict(all=' ', error='!', warning='@', info='*', graph='~')
    return trig_key


def WRITE_LEVEL():
    write_level = dict(error=3, warning=2, info=1, graph=0, all=0)
    return write_level


def LOG_EXIT_TYPE():
    # The exit style (on log exit)
    #  if 'sys' exits via sys.exit   - soft exit (ipython Exception)
    #  if 'os' exits via os._exit    - hard exit (complete exit)
    # Do nothing on exit call
    log_exit_type = None
    # Use os._exit
    log_exit_type = 'os'
    # Use sys.exit
    log_exit_type = 'sys'
    return log_exit_type


def LOG_CAUGHT_WARNINGS():
    # Define whether we warn
    warn = True
    return warn


def COLOUREDLEVELS():
    # reference:
    # http://ozzmaker.com/add-colour-to-text-in-python/
    clevels = dict(error=REDCOLOUR(),  # red
                   warning=YELLOWCOLOUR(),  # yellow
                   info=GREENCOLOUR(),  # green
                   graph=GREENCOLOUR(),  # green
                   all=GREENCOLOUR())  # green
    return clevels


def NORMALCOLOUR():
    norm = " \033[0;37;40m"
    return norm


def REDCOLOUR():
    red = '\033[0;31;48m'
    return red


def YELLOWCOLOUR():
    yellow = '\033[0;33;48m'
    return yellow


def GREENCOLOUR():
    green = '\033[0;32;48m'
    return green


def COLOURED_LOG():
    clog = pp['COLOURED_LOG']
    return clog


def EXIT():
    my_exit = LOG_EXIT_TYPE()
    if my_exit == 'sys':
        my_exit = sys.exit
    elif EXIT == 'os':
        my_exit = os._exit
    else:
        my_exit = lambda x: None
    return my_exit


def EXIT_LEVELS():
    exit_levels = ['error']
    return exit_levels


# =============================================================================
# Start of code
# =============================================================================
# Get version and author
__version__ = VERSION()
__author__ = AUTHORS()
__date__ = LATEST_EDIT()
__release__ = RELEASE()

# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
