#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spirou constant module

Constants used throughout DRS that are more complicated than simple objects
i.e. require a function and maybe input parameters

Created on 2017-11-13 at 14:22

@author: cook

Import rules: Only from spirouConfigFile
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
    version = '0.1.008'
    return version


def RELEASE():
    release = 'alpha pre-release'
    return release


def AUTHORS():
    # Module Authors (Used in all sub-packages)
    authors = 'N. Cook, F. Bouchy, E. Artigau, I. Boisse, M. Hobson, C. Moutou'
    return authors


def LATEST_EDIT():
    # Module last edit date (in form YYYY-MM-DD) used in all sub-packages
    date = '2018-01-30'
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
    debug = pp['DRS_DEBUG']
    return debug


# =============================================================================
# Define File functions
# =============================================================================
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

    program = p['program'] + '.info'
    manual_file = os.path.join(p['DRS_MAN'], program)
    return manual_file


def RAW_DIR(p):
    raw_dir = os.path.join(p['DRS_DATA_RAW'], p['arg_night_name'])
    return raw_dir


def REDUCED_DIR(p):
    # set the reduced directory from DRS_DATA_REDUC and 'arg_night_name'
    reduced_dir = os.path.join(p['DRS_DATA_REDUC'], p['arg_night_name'])
    # return reduced directory
    return reduced_dir


# =============================================================================
# Define Filename functions
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


def DARK_FILE(p):
    reducedfolder = p['reduced_dir']
    calibprefix = CALIB_PREFIX(p)
    darkfitsname = calibprefix + p['arg_file_names'][0]
    darkfits = os.path.join(reducedfolder, darkfitsname)
    return darkfits

def DARK_BADPIX_FILE(p):
    darkfile = DARK_FILE(p)
    badpixelfits = darkfile.replace('.fits', '_badpixel.fits')
    return badpixelfits


def BADPIX_FILE(p):
    reducedfolder = p['reduced_dir']
    calibprefix = CALIB_PREFIX(p)
    badpixelfn = p['flatfile'].replace('.fits', '_badpixel.fits')
    badpixelfitsname = calibprefix + badpixelfn
    badpixelfits = os.path.join(reducedfolder, badpixelfitsname)
    return badpixelfits


def LOC_ORDER_PROFILE_FILE(p):
    reducedfolder = p['reduced_dir']
    newext = '_order_profile_{0}.fits'.format(p['fiber'])
    calibprefix = CALIB_PREFIX(p)
    rawfn = p['arg_file_names'][0].replace('.fits', newext)
    rawfitsname = calibprefix + rawfn
    rawfits = os.path.join(reducedfolder, rawfitsname)
    return rawfits


def LOC_LOCO_FILE(p):
    reducedfolder = p['reduced_dir']
    locoext = '_loco_{0}.fits'.format(p['fiber'])
    calibprefix = CALIB_PREFIX(p)
    locofn = p['arg_file_names'][0].replace('.fits', locoext)
    locofitsname = calibprefix + locofn
    locofits = os.path.join(reducedfolder, locofitsname)
    return locofits


def LOC_LOCO_FILE2(p):
    reducedfolder = p['reduced_dir']
    locoext = '_fwhm-order_{0}.fits'.format(p['fiber'])
    calibprefix = CALIB_PREFIX(p)
    locofn2 = p['arg_file_names'][0].replace('.fits', locoext)
    locofits2name = calibprefix + locofn2
    locofits2 = os.path.join(reducedfolder, locofits2name)
    return locofits2


def LOC_LOCO_FILE3(p):
    reducedfolder = p['reduced_dir']
    locoext = '_with-order_{0}.fits'.format(p['fiber'])
    calibprefix = CALIB_PREFIX(p)
    locofn3  = p['arg_file_names'][0].replace('.fits', locoext)
    locofits3name = calibprefix + locofn3
    locofits3 = os.path.join(reducedfolder, locofits3name)
    return locofits3


def SLIT_TILT_FILE(p):
    reduced_dir = p['reduced_dir']
    calibprefix = CALIB_PREFIX(p)
    tiltfn = p['arg_file_names'][0].replace('.fits', '_tilt.fits')
    tiltfitsname = calibprefix + tiltfn
    tiltfits = os.path.join(reduced_dir, tiltfitsname)
    return tiltfits


def FF_BLAZE_FILE(p, fiber=None):

    if fiber is None:
        fiber = p['fiber']

    reduced_dir = p['reduced_dir']
    blazeext = '_blaze_{0}.fits'.format(fiber)
    calibprefix = CALIB_PREFIX(p)
    blazefn = p['arg_file_names'][0].replace('.fits', blazeext)
    blazefitsname = calibprefix + blazefn
    blazefits = os.path.join(reduced_dir, blazefitsname)
    return blazefits


def FF_FLAT_FILE(p, fiber=None):
    if fiber is None:
        fiber = p['fiber']
    reduced_dir = p['reduced_dir']
    flatext = '_flat_{0}.fits'.format(fiber)
    calibprefix = CALIB_PREFIX(p)
    flatfn = p['arg_file_names'][0].replace('.fits', flatext)
    flatfitsname = calibprefix + flatfn
    flatfits = os.path.join(reduced_dir, flatfitsname)
    return flatfits


def EXTRACT_E2DS_FILE(p, fiber=None):
    if fiber is None:
        fiber = p['fiber']
    reducedfolder = p['reduced_dir']
    e2ds_ext = '_e2ds_{0}.fits'.format(fiber)
    e2dsfitsname = p['arg_file_names'][0].replace('.fits', e2ds_ext)
    e2dsfits = os.path.join(reducedfolder,e2dsfitsname)
    return e2dsfits


def EXTRACT_LOCO_FILE(p):
    reducedfolder = p['reduced_dir']
    loco_filename = p['calibDB']['LOC_{0}'.format(p['LOC_FILE'])][1]
    loco_file = os.path.join(reducedfolder, loco_filename)
    return loco_file


def EXTRACT_E2DS_ALL_FILES(p, fiber=None):
    if fiber is None:
        fiber = p['fiber']
    reducedfolder = p['reduced_dir']
    ext_names = ['simple', 'tilt', 'tiltweight', 'tiltweight2',
                 'weight']
    extfitslist = []
    for ext_no in range(len(ext_names)):
        extname = ext_names[ext_no]
        ext_ext = '_e2ds_{0}_{1}.fits'.format(fiber, extname)
        extfitsname = p['arg_file_names'][0].replace('.fits', ext_ext)
        extfits = os.path.join(reducedfolder, extfitsname)
        extfitslist.append(extfits)
    return extfitslist


def DRIFT_RAW_FILE(p):
    reducedfolder = p['reduced_dir']
    drift_ext = '_drift_{0}.fits'.format(p['fiber'])
    driftfitsname = p['arg_file_names'][0].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    return driftfits


def DRIFT_E2DS_FITS_FILE(p):
    reducedfolder = p['reduced_dir']
    drift_ext = '_drift_{0}.fits'.format(p['fiber'])
    driftfitsname = p['reffilename'].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    return driftfits


def DRIFT_E2DS_TBL_FILE(p):
    reducedfolder = p['reduced_dir']
    drift_ext = '_drift_{0}.tbl'.format(p['fiber'])
    drifttblname = p['reffilename'].replace('.fits', drift_ext)
    drifttbl = os.path.join(reducedfolder, drifttblname)
    return drifttbl


def DRIFTPEAK_E2DS_FITS_FILE(p):
    reducedfolder = p['reduced_dir']
    drift_ext = '_driftnew_{0}.fits'.format(p['fiber'])
    driftfitsname = p['reffilename'].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    return driftfits


def DRIFTPEAK_E2DS_TBL_FILE(p):
    reducedfolder = p['reduced_dir']
    drift_ext = '_driftnew_{0}.tbl'.format(p['fiber'])
    drifttblname = p['reffilename'].replace('.fits', drift_ext)
    drifttbl = os.path.join(reducedfolder, drifttblname)
    return drifttbl


def CCF_FITS_FILE(p):
    reducedfolder = p['reduced_dir']
    # get new extension using ccf_mask without the extention
    newext = '_ccf_' + p['ccf_mask'].replace('.mas', '')
    # set the new filename as the reference file without the _e2ds
    corfilename = p['reffile'].replace('_e2ds', newext)

    corfile = os.path.join(reducedfolder, corfilename)
    # return the new ccf table file location and name
    return corfile


def CCF_TABLE_FILE(p):
    # start with the CCF fits file name
    corfile = CCF_FITS_FILE(p)
    # we want to save the file as a tbl file not a fits file
    ccf_table_file = corfile.replace('.fits', '.tbl')
    # return the new ccf table file location and name
    return ccf_table_file


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

def DATE_FMT_DEFAULT():
    date_fmt_default = '%Y-%m-%d-%H:%M:%S.%f'
    return date_fmt_default

def TIME_FORMAT_DEFAULT():
    time_format_default = '%H:%M:%S'
    return time_format_default


# =============================================================================
# Define logger functions
# =============================================================================
def LOG_TIMEZONE():
    # options are local or UTC
    log_timezone = 'UTC'
    log_timezone = 'local'
    return log_timezone


def LOG_TIME_FORMAT():
    log_time_format = '%H:%M:%S'
    return log_time_format


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
    clevels = dict(error=bcolors.FAIL,  # red
                   warning=bcolors.WARNING,  # yellow
                   info=bcolors.OKGREEN,  # green
                   graph=bcolors.OKBLUE,  # green
                   all=bcolors.OKGREEN)  # green
    return clevels

# defines the colours
class bcolors:
    HEADER = '\033[95;1m'
    OKBLUE = '\033[94;1m'
    OKGREEN = '\033[92;1m'
    WARNING = '\033[93;1m'
    FAIL = '\033[91;1m'
    ENDC = '\033[0;0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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

def DEFAULT_LOG_OPT():
    # get raw path from first item in sys.argv (normally the python
    #    script run file absolute path)
    rawpath = sys.argv[0]
    # get the file name (no path)
    path = os.path.split(rawpath)[-1]
    # clean .py from filename
    program = path.replace('.py', '')
    # return program
    return program


# =============================================================================
# Start of code
# =============================================================================
# Get version and author
__version__ = VERSION()
__author__ = AUTHORS()
__date__ = LATEST_EDIT()
__release__ = RELEASE()


# =============================================================================
# End of code
# =============================================================================
