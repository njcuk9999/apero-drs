#!/usr/bin/env python
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
import time
from . import spirouConfigFile

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouConst.py'
# Get version and author
__version__ = '0.2.026'
__author__ = 'N. Cook, F. Bouchy, E. Artigau, I. Boisse, M. Hobson, C. Moutou'
__release__ = 'alpha pre-release'
__date__ = '2018-05-18'


# =============================================================================
# Define pre-functions
# =============================================================================
# noinspection PyPep8Naming
def CONFIGFILE():
    """
    Defines the primary config filename

    :return config_file: string, the primary config file filename
    """
    # Name of main config file (in CONFIGFOLDER() )
    config_file = 'config.py'
    return config_file


# noinspection PyPep8Naming
def PACKAGE():
    """
    Defines the package name (Used in code so MUST equal name of parent package)

    :return package: string, defines the package name
    """
    # Module package name (Used in code so MUST equal name of parent package)
    package = 'SpirouDRS'
    return package


# noinspection PyPep8Naming
def NAME():
    """
    Defines the name of the DRS

    :return drs_name: string, the name of the DRS
    """
    drs_name = 'SPIROU'
    return drs_name


# noinspection PyPep8Naming
def VERSION():
    """
    Defines the version of the DRS

    alpha and beta releases should be between 0 and 1
    full releases should be incremental (integers)
    with major sub-releases using the second decimal place
    and minor version changes using the third decimal place

    i.e.
    0.1.01
    0.1.02   - minor sub-release
    0.2      - major sub-release
    0.3      - major sub-release
    1.0      - first full release
    1.0.01   - minor sub-release after full release

    :return version: string, a numerical sequence in the form A.B.C where
                     A denotes full releases, B denotes major changes (but not
                     full release level), and C denotes minor changes
    """
    # Module Version (Used in all sub-packages)
    version = __version__
    return version


# noinspection PyPep8Naming
def RELEASE():
    """
    Defines the release state of the DRS
    i.e.
    alpha
    beta

    pre-release
    released

    :return release: string, the release state of the DRS
    """
    release = __release__
    return release


# noinspection PyPep8Naming
def AUTHORS():
    """
    Define the authors of the DRS

    :return authors: string, the list of authors, separated by commas
    """
    # Module Authors (Used in all sub-packages)
    authors = __author__
    return authors


# noinspection PyPep8Naming
def LATEST_EDIT():
    """
    Defines the latest edit date of the code (used in all recipes)

    :return date: string, the date (in format YYYY-MM-DD)
    """
    # Module last edit date (in form YYYY-MM-DD) used in all sub-packages
    date = __date__
    return date


# noinspection PyPep8Naming
def CONFIGFOLDER():
    """
    Defines the config folder folder name (relative to the
    spirouConfig.PACKAGE() level.

    :return config_folder: string, the config folder path relative to the
                           package level
    """
    # Name of main config folder (relative to PACKAGE() level)
    config_folder = '../config'
    return config_folder


# noinspection PyPep8Naming
def CDATA_REL_FOLDER():
    """
    Define the location and name of the constant data folder. Path is
    relative to the spirouConst.PACKAGE() path

    Use spirouConfig.GetAbsFolderPath(PACKAGE(), CDATA_REL_FOLDER()) to
    get absolute path

    :return const_data_folder: string, the location and name of the constant
                               data file
    """
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
# noinspection PyPep8Naming
def INTERACITVE_PLOTS_ENABLED():
    """
    Defines a master switch which decides whether interactive plots are used
    throughout the DRS (overrides user preference)

    :return interactive_plots: bool, if True uses interactive plots if False
                               uses plt.show() to show plots (pauses recipe)
    """
    # Whether to use plt.ion (if True) or to use plt.show (if False)
    interactive_plots = True
    return interactive_plots


# noinspection PyPep8Naming
def DEBUG():
    """
    Gets the debug mode from the primary constant file (using "DRS_DEBUG")

        0: no debug
        1: basic debugging on errors
        2: recipes specific (plots and some code runs)

    :return debug: int, the debug level of the DRS
    """
    debug = pp['DRS_DEBUG']
    return debug


# =============================================================================
# Define File functions
# =============================================================================
# noinspection PyPep8Naming
def ARG_NIGHT_NAME(p):
    """
    Defines the folder name for raw or reduced files within the raw or reduced
    data folders, i.e. for /data/raw/20170710/  arg_night_name is "20170710"

    :param p: parameter dictionary, ParamDict containing constants
        If 'ARG_NIGHT_NAME' already defined in "p" this value is returned

    :return: string, the folder within data raw directory containing files
             (also reduced directory) i.e. /data/raw/20170710 would be
             "20170710"
    """
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


# noinspection PyPep8Naming
def NBFRAMES(p):
    """
    Defines the number of frames (files) as the length of "arg_file_names"
    i.e. the number of files defined at run time or in recipe input

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :return nbframes: int, the number of frames (files)
    """
    # Number of frames = length of arg_file_names
    nbframes = len(p['ARG_FILE_NAMES'])
    # return number of frames
    return nbframes


# noinspection PyPep8Naming
def FORBIDDEN_COPY_KEYS():
    """
    Defines the keys in a HEADER file not to copy when copying over all
    HEADER keys to a new fits file

    :return forbidden_keys: list of strings, the keys in a HEADER file not
                            to copy from and old fits file
    """
    forbidden_keys = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                      'EXTEND', 'COMMENT', 'CRVAL1', 'CRPIX1', 'CDELT1',
                      'CRVAL2', 'CRPIX2', 'CDELT2', 'BSCALE', 'BZERO',
                      'PHOT_IM', 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB']
    # return keys
    return forbidden_keys


# noinspection PyPep8Naming
def LOG_OPT(p):
    """
    Defines the program to use as the "option" in logging
    i.e. option in spirouConfig.WLOG(kind, option, message)

    if an error is raised spirouConst.DEFAULT_LOG_OPT() is used instead.

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]

    :return program: string, the program to use in log option
    """
    # deal with the log_opt "log option"
    #    either {program}   or {program}:{prefix}   or {program}:{prefix}+[...]

    try:
        arg_file_names = p['ARG_FILE_NAMES']
        program = p['PROGRAM']

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
    except Exception:
        log_opt = DEFAULT_LOG_OPT()

    return log_opt


# noinspection PyPep8Naming
def PROGRAM():
    """
    Defines the recipe/code/program currently running (from sys.argv[0])
    '.py' is removed

    :return program: string, the recipe/code/program name
    """
    # get run time parameters
    rparams = list(sys.argv)
    # get program name
    program = os.path.basename(rparams[0]).split('.py')[0]
    # return program
    return program


# noinspection PyPep8Naming
def MANUAL_FILE(p):
    """
    Defines the path and filename of the manual file for p['PROGRAM']

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                DRS_MAN: string, the file path to the manual files

    :return manual_file: the filename and location of the manual file for this
                         recipe/program
    """
    program = p['PROGRAM'] + '.info'
    manual_file = os.path.join(p['DRS_MAN'], program)
    return manual_file


# noinspection PyPep8Naming
def RAW_DIR(p):
    """
    Defines the raw data directory

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"

    :return raw_dir: string, the raw data directory
    """
    raw_dir = os.path.join(p['DRS_DATA_RAW'], p['ARG_NIGHT_NAME'])
    return raw_dir


# noinspection PyPep8Naming
def REDUCED_DIR(p):
    """
    Defines the reduced data directory

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"

    :return reduced_dir: string, the reduced data directory
    """
    # set the reduced directory from DRS_DATA_REDUC and 'arg_night_name'
    reduced_dir = os.path.join(p['DRS_DATA_REDUC'], p['ARG_NIGHT_NAME'])
    # return reduced directory
    return reduced_dir


# =============================================================================
# Define Filename functions
# =============================================================================
# noinspection PyPep8Naming
def ARG_FILE_NAMES(p):
    """
    Defines the list of filenames (usually obtained from the run time argumnets
    (i.e. sys.argv). If 'arg_file_names' already in "p" then we use that to
    set the value.
    Files are obtained from run time/sys.argv is assumed
    to be in the following format:

    >> sys.argv = ['program.py', 'arg_night_name', 'file1', 'file2', 'file3']

    therefore arg_file_names has the value:

    >> arg_file_names = sys.argv[3:]

    :param p: parameter dictionary, ParamDict containing constants
        May contain:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

        If it does this value is used over sys.argv values

    :return arg_file_names: list of strings, the file names from run time, or
                            if p['ARG_FILE_NAMES'] exists value is taken from
                            there
    """
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


# noinspection PyPep8Naming
def FITSFILENAME(p):
    """
    Defines the full path of for the main raw fits file for a recipe
    i.e. /data/raw/20170710/filename.fits

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from

    :return fitsfilename: string, the main raw fits file location and filename
    """
    arg_file_dir = p['ARG_FILE_DIR']
    arg_file_names = p['ARG_FILE_NAMES']
    # construct fits file name (full path + first file in arguments)
    if len(arg_file_names) > 0:
        fitsfilename = os.path.join(arg_file_dir, arg_file_names[0])
    else:
        fitsfilename = None
    # return fitsfilename
    return fitsfilename


# noinspection PyPep8Naming
def DARK_FILE(p):
    """
    Defines the dark file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :return darkfits: string, the dark file location and filename
    """
    reducedfolder = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    darkfitsname = calibprefix + p['ARG_FILE_NAMES'][0]
    darkfits = os.path.join(reducedfolder, darkfitsname)
    return darkfits


# noinspection PyPep8Naming
def DARK_BADPIX_FILE(p):
    """
    Defines the bad pix file from cal_DARK

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :return badpixfits: string the dark bad pix file location and filename
    """
    darkfile = DARK_FILE(p)
    badpixelfits = darkfile.replace('.fits', '_badpixel.fits')
    return badpixelfits


# noinspection PyPep8Naming
def BADPIX_FILE(p):
    """
    Defines the bad pixel path and file name

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                flatfile: string, the flat file name (used to name the
                          badpix file, replacing .fits with _badpixel.fits
    :return string: the badpix path and filename
    """
    reducedfolder = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    badpixelfn = p['FLATFILE'].replace('.fits', '_badpixel.fits')
    badpixelfitsname = calibprefix + badpixelfn
    badpixelfits = os.path.join(reducedfolder, badpixelfitsname)
    return badpixelfits


# noinspection PyPep8Naming
def LOC_ORDER_PROFILE_FILE(p):
    """
    Defines the localisation file location and filename (the order profile
    image)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :return locofits: string, the localisation file location and filename (the
                      order profile image)
    """
    reducedfolder = p['REDUCED_DIR']
    newext = '_order_profile_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    rawfn = p['ARG_FILE_NAMES'][0].replace('.fits', newext)
    rawfitsname = calibprefix + rawfn
    orderpfile = os.path.join(reducedfolder, rawfitsname)
    return orderpfile


# noinspection PyPep8Naming
def LOC_LOCO_FILE(p):
    """
    Defines the localisation file location and filename

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :return locofits: string, the localisation file location and filename
    """
    reducedfolder = p['REDUCED_DIR']
    locoext = '_loco_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    locofn = p['ARG_FILE_NAMES'][0].replace('.fits', locoext)
    locofitsname = calibprefix + locofn
    locofits = os.path.join(reducedfolder, locofitsname)
    return locofits


# noinspection PyPep8Naming
def LOC_LOCO_FILE2(p):
    """
    Defines the localisation file location and filename (for fwhm)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :return locofits: string, the localisation file location and filename (for
                      fwhm)
    """
    reducedfolder = p['REDUCED_DIR']
    locoext = '_fwhm-order_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    locofn2 = p['ARG_FILE_NAMES'][0].replace('.fits', locoext)
    locofits2name = calibprefix + locofn2
    locofits2 = os.path.join(reducedfolder, locofits2name)
    return locofits2


# noinspection PyPep8Naming
def LOC_LOCO_FILE3(p):
    """
    Defines the localisation file location and filename (for order
    superposition)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :return locofits: string, the localisation file location and filename (for
                      order superposition)
    """
    reducedfolder = p['REDUCED_DIR']
    locoext = '_with-order_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    locofn3 = p['ARG_FILE_NAMES'][0].replace('.fits', locoext)
    locofits3name = calibprefix + locofn3
    locofits3 = os.path.join(reducedfolder, locofits3name)
    return locofits3


# noinspection PyPep8Naming
def SLIT_TILT_FILE(p):
    """
    Defines the slit tilt file location and filename

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :return tiltfits: string, slit tilt file location and filename
    """
    reduced_dir = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    tiltfn = p['ARG_FILE_NAMES'][0].replace('.fits', '_tilt.fits')
    tiltfitsname = calibprefix + tiltfn
    tiltfits = os.path.join(reduced_dir, tiltfitsname)
    return tiltfits


# noinspection PyPep8Naming
def FF_BLAZE_FILE(p, fiber=None):
    """
    Define the flat fielding blaze filename and location

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :param fiber: string, the fiber name, if None tries to get the fiber name
                  from "p" (i.e. p['FIBER'])
    :return blazefits: string, the flat fielding blaze filename and location
    """

    if fiber is None:
        fiber = p['FIBER']

    reduced_dir = p['REDUCED_DIR']
    blazeext = '_blaze_{0}.fits'.format(fiber)
    calibprefix = CALIB_PREFIX(p)
    blazefn = p['ARG_FILE_NAMES'][0].replace('.fits', blazeext)
    blazefitsname = calibprefix + blazefn
    blazefits = os.path.join(reduced_dir, blazefitsname)
    return blazefits


# noinspection PyPep8Naming
def FF_FLAT_FILE(p, fiber=None):
    """
    Defines the flat field file name and location to save flat field file to

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :param fiber: string, the fiber name, if None tries to get the fiber name
                  from "p" (i.e. p['FIBER'])

    :return flatfits: string, the flat field filename and location
    """
    if fiber is None:
        fiber = p['FIBER']
    reduced_dir = p['REDUCED_DIR']
    flatext = '_flat_{0}.fits'.format(fiber)
    calibprefix = CALIB_PREFIX(p)
    flatfn = p['ARG_FILE_NAMES'][0].replace('.fits', flatext)
    flatfitsname = calibprefix + flatfn
    flatfits = os.path.join(reduced_dir, flatfitsname)
    return flatfits


# noinspection PyPep8Naming
def EXTRACT_E2DS_FILE(p, fiber=None):
    """
    Defines the extraction E2DS file name and location

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
    :param fiber: string, the fiber name, if None tries to get the fiber name
                  from "p" (i.e. p['FIBER'])
    :return e2dsfits: string, the filename and location of the extraction
                      E2DS file
    """
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    e2ds_ext = '_e2ds_{0}.fits'.format(fiber)
    e2dsfitsname = p['ARG_FILE_NAMES'][0].replace('.fits', e2ds_ext)
    e2dsfits = os.path.join(reducedfolder, e2dsfitsname)
    return e2dsfits


# noinspection PyPep8Naming
def EXTRACT_LOCO_FILE(p):
    """
    Defines the file name and location of the extraction localisation filename
    using the calibration database file name and the loc_file suffix

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                calibDB: dictionary, the calibration database dictionary
                LOC_FILE: string, the suffix to use in the filename, defined
                          in primary config file (LOC_FILE_FPALL)


    :return loco_file: string, the localisation filename and location built from
                       the calibration database file:

                       LOC_{X}   where X is the suffix provided by "LOC_FILE"
                                 selected from a specific fiber by
                                 "LOC_FILE_FPALL"
    """
    reducedfolder = p['REDUCED_DIR']
    loco_filename = p['CALIBDB']['LOC_{0}'.format(p['LOC_FILE'])][1]
    loco_file = os.path.join(reducedfolder, loco_filename)
    return loco_file


# noinspection PyPep8Naming
def DRIFT_RAW_FILE(p):
    """
    Defines the drift_raw fits file name and location using
    "arg_file_names"[0] and replacing ".fits" with "_drift_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :return driftfits: string, the drift_raw fits file name and location
    """
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_drift_{0}.fits'.format(p['FIBER'])
    driftfitsname = p['ARG_FILE_NAMES'][0].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    return driftfits


# noinspection PyPep8Naming
def DRIFT_E2DS_FITS_FILE(p):
    """
    Defines the drift_e2ds fits file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name

    :return driftfits: string, the drift_e2ds peak drift fits file location
                       and filename
    """
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_drift_{0}.fits'.format(p['FIBER'])
    driftfitsname = p['REFFILENAME'].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    return driftfits


# noinspection PyPep8Naming
def DRIFT_E2DS_TBL_FILE(p):
    """
    Defines the drift_e2ds table file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name

    :return driftfits: string, the drift_e2ds peak drift table file location
                       and filename
    """
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_drift_{0}.tbl'.format(p['FIBER'])
    drifttblname = p['REFFILENAME'].replace('.fits', drift_ext)
    drifttbl = os.path.join(reducedfolder, drifttblname)
    return drifttbl


# noinspection PyPep8Naming
def DRIFTPEAK_E2DS_FITS_FILE(p):
    """
    Defines the drift peak fits drift file name and location using "reffilename"
    and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name

    :return driftfits: string, the drift peak drift fits file location and
                       filename
    """
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_driftnew_{0}.fits'.format(p['FIBER'])
    driftfitsname = p['REFFILENAME'].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    return driftfits


# noinspection PyPep8Naming
def DRIFTPEAK_E2DS_TBL_FILE(p):
    """
    Defines the drift peak drift table file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name

    :return driftfits: string, the drift peak drift table file location and
                       filename
    """
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_driftnew_{0}.tbl'.format(p['FIBER'])
    drifttblname = p['REFFILENAME'].replace('.fits', drift_ext)
    drifttbl = os.path.join(reducedfolder, drifttblname)
    return drifttbl


# noinspection PyPep8Naming
def CCF_FITS_FILE(p):
    """
    Defines the CCF fits file location and name

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                ccf_mask: string, the CCF mask file
                reffile: string, the CCF reference file
    :return corfile: string, the CCF table file location and name
    """
    reducedfolder = p['REDUCED_DIR']
    # get new extension using ccf_mask without the extention
    newext = '_ccf_' + p['CCF_MASK'].replace('.mas', '')
    # set the new filename as the reference file without the _e2ds
    corfilename = p['E2DSFILE'].replace('_e2ds', newext)

    corfile = os.path.join(reducedfolder, corfilename)
    # return the new ccf file location and name
    return corfile


# noinspection PyPep8Naming
def CCF_TABLE_FILE(p):
    """
    Defines the CCF table file location and name

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                ccf_mask: string, the CCF mask file
                reffile: string, the CCF reference file
    :return ccf_table_file:
    """
    # start with the CCF fits file name
    corfile = CCF_FITS_FILE(p)
    # we want to save the file as a tbl file not a fits file
    ccf_table_file = corfile.replace('.fits', '.tbl')
    # return the new ccf table file location and name
    return ccf_table_file


# noinspection PyPep8Naming
def EM_SPE_FILE(p):
    """
    Defines the cal_exposure_meter telluric spectrum map

        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                em_output_type: string, the type of output generated

    :return fitsfile: string, absolute path for the output
    """
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = 'em_tell_spec_{0}.fits'.format(kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # return absolute path
    return fitsfile


def EM_WAVE_FILE(p):
    """
    Defines the cal_exposure_meter wavelength

        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                em_output_type: string, the type of output generated

    :return fitsfile: string, absolute path for the output
    """
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = 'em_wavemap_{0}.fits'.format(kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # return absolute path
    return fitsfile


def EM_MASK_FILE(p):
    """
    Defines the cal_exposure_meter telluric spectrum map

        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                em_output_type: string, the type of output generated

    :return fitsfile: string, absolute path for the output
    """
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = 'em_mask_map_{0}.fits'.format(kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # return absolute path
    return fitsfile


# =============================================================================
# Define calibration database functions
# =============================================================================
# noinspection PyPep8Naming
def CALIBDB_MASTERFILE(p):
    """
    Define the name and location of the calibration database file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from
                IC_CALIBDB_FILENAME: string, the name of the calibration
                                     database file
    :return string: the path and location of the calibration database file
    """
    masterfilepath = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
    return masterfilepath


# noinspection PyPep8Naming
def CALIBDB_LOCKFILE(p):
    """
    Define the location and filename of the lock file for the calibration
    database

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                CALIB_DB_MATCH: string, either "closest" or "older"
                                whether to use the "closest" time
                                ("closest") or the closest time that is
                                older ("older") than "max_time_unix"
    :return lockfilepath: string, the location and filename of the lock file
                          for the calibration database
    """
    lockfilepath = os.path.join(p['DRS_CALIB_DB'], 'lock_calibDB')
    return lockfilepath


# noinspection PyPep8Naming
def CALIB_PREFIX(p):
    """
    Define the calibration database file prefix (using arg_night_name)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
    :return calib_prefix: string the calibration database prefix to add to all
                          calibration database files
    """
    argnightname = p['ARG_NIGHT_NAME'].split('/')[-1]
    calib_prefix = argnightname + '_'
    return calib_prefix


# =============================================================================
# Define formatting functions
# =============================================================================
# noinspection PyPep8Naming
def CONFIG_KEY_ERROR(key, location=None):
    """
    Defines the error message displayed when a SpirouConfig.ConfigError is
    raised

    :param key: string, the key that generated the config error
    :param location: string, the location of the code that generated the error

    :return cerrmsg: string, the message to display when ConfigError is raised.
    """
    if location is None:
        cerrmsg = 'key "{0}" is not defined'
        return cerrmsg.format(key)
    else:
        cerrmsg = 'key "{0}" must be defined in file (located at {1})'
        return cerrmsg.format(key, location)


# noinspection PyPep8Naming
def DATE_FMT_HEADER(p):
    """
    The date format for string timestamp for reading times from FITS
    file HEADERS

    Commonly used format codes:
        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.

    :return date_fmt_calibdb: string, the string timestamp format for use in
                              reading FITS file HEADERS
    """
    # TODO: This switch will be obsolete after H2RG testing is over
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        date_fmt_header = '%Y-%m-%dT%H:%M:%S'
    else:
        date_fmt_header = '%Y-%m-%d-%H:%M:%S.%f'
    return date_fmt_header


# noinspection PyPep8Naming
def DATE_FMT_CALIBDB():
    """
    The date format for string timestamp in the calibration database

    Commonly used format codes:
        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.

    :return date_fmt_calibdb: string, the string timestamp format for the
                              calibration database
    """
    date_fmt_calibdb = '%Y-%m-%d-%H:%M:%S.%f'
    return date_fmt_calibdb


# noinspection PyPep8Naming
def DATE_FMT_DEFAULT():
    """
    The date format for string timestamp used by default (if not defined or
    used)

    Commonly used format codes:
        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.

    :return date_fmt_calibdb: string, the string timestamp format used by
                              default
    """
    date_fmt_default = '%Y-%m-%d-%H:%M:%S.%f'
    return date_fmt_default


# noinspection PyPep8Naming
def TIME_FORMAT_DEFAULT():
    """
    The time format for string timestamp used by default (if not defined or
    used)

    Commonly used format codes:
        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.

    :return time_format_default: string, the string timestamp format used by
                                 default
    """
    time_format_default = '%H:%M:%S'
    return time_format_default


# =============================================================================
# Define logger functions
# =============================================================================
# noinspection PyPep8Naming
def LOG_FILE_NAME(p, dir_data_msg=None, utime=None):
    """
    Define the log filename and full path.

    The filename is defined as:
        DRS-YYYY-MM-DD  (GMT date)
    The directory is defined as dir_data_msg (or p['DRS_DATA_MSG'] if not
        defined)

    if p['DRS_USED_DATE'] is set this date is used instead
    if no utime is defined uses the time now (in gmt time)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_DATA_MSG: string, the directory that the log messages
                              should be saved to (if "dir_data_msg" not defined)
                DRS_USED_DATE: string, the used date (if not defined or set to
                               "None" then "utime" is used or if "utime" not
                               defined uses the time now
    :param dir_data_msg: string or None, if defined the p
    :param utime: float or None, the unix time to use to set the date, if
                  undefined uses time.time() (time now) - in GMT

    :return lpath: string, the full path and file name for the log file
    """
    # deal with no dir_data_msg
    if dir_data_msg is None:
        dir_data_msg = p.get('DRS_DATA_MSG', None)
    # deal with no utime (set it to the time now)
    if utime is None:
        utime = time.time()
    # Get the used date if it is not None
    p['DRS_USED_DATE'] = p.get('DRS_USED_DATE', 'None').upper()
    udate = p['DRS_USED_DATE']
    # if we don't have a udate use the date
    if udate == 'undefined' or udate == 'NONE':
        date = time.strftime('%Y-%m-%d', time.gmtime(utime))
    else:
        date = p['DRS_USED_DATE']
    # Get the HOST name (if it does not exist host = 'HOST')
    host = os.environ.get('HOST', 'HOST')
    # construct the logfile path
    lpath = os.path.join(dir_data_msg, 'DRS-{0}.{1}'.format(host, date))
    # return lpath
    return lpath


# noinspection PyPep8Naming
def LOG_TIMEZONE():
    """
    The time zone to use in timestamps for logging (i.e. UTC)

    options are:
            'UTC' for universal time / GMT
            'local' for local time (computer time)

    :return log_timezone: string, the timezone to use (either "UTC" or "local")
    """
    # options are local or UTC
    # log_timezone = 'UTC'
    log_timezone = 'local'
    return log_timezone


# noinspection PyPep8Naming
def LOG_TIME_FORMAT():
    """
    The time format to use in the log time stamp

    Commonly used format codes:

        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.

    :return log_time_format: string, the log timestamp format
    """
    log_time_format = '%H:%M:%S'
    return log_time_format


# noinspection PyPep8Naming
def LOG_TRIG_KEYS():
    """
    The log trigger key characters to use in log. Keys must be the same as
    spirouConst.WRITE_LEVELS()

    i.e.

    if the following is defined:
    >> trig_key[error] = '!'
    and the following log is used:
    >> WLOG('error', 'program', 'message')
    the output is:
    >> print("TIMESTAMP - ! |program|message")

    :return trig_key: dictionary, contains all the trigger keys and the
                      characters/strings to use in logging. Keys must be the
                      same as spirouConst.WRITE_LEVELS()
    """
    # The trigger character to display for each
    trig_key = dict(all=' ', error='!', warning='@', info='*', graph='~')
    return trig_key


# noinspection PyPep8Naming
def WRITE_LEVEL():
    """
    The write levels. Keys must be the same as spirouConst.LOG_TRIG_KEYS()

    The write levels define which levels are logged and printed (based on
    constants "PRINT_LEVEL" and "LOG_LEVEL" in the primary config file

    i.e. if
    >> PRINT_LEVEL = 'warning'
    then no level with a numerical value less than
    >> write_level['warning']
    will be printed to the screen

    similarly if
    >> LOG_LEVEL = 'error'
    then no level with a numerical value less than
    >> write_level['error']
    will be printed to the log file

    :return write_level: dictionary, contains the keys and numerical levels
                         of each trigger level. Keys must be the same as
                         spirouConst.LOG_TRIG_KEYS()
    """
    write_level = dict(error=3, warning=2, info=1, graph=0, all=0)
    return write_level


# noinspection PyPep8Naming
def LOG_CAUGHT_WARNINGS():
    """
    Defines a master switch, whether to report warnings that are caught in

    >> with warnings.catch_warnings(record=True) as w:
    >>     code_that_may_gen_warnings

    :return warn: bool, if True reports warnings, if False does not
    """
    # Define whether we warn
    warn = True
    return warn


# noinspection PyPep8Naming
def COLOUREDLEVELS():
    """
    Defines the colours if using coloured log.
    Allowed colour strings are found here:
            see here:
            http://ozzmaker.com/add-colour-to-text-in-python/
            or in spirouConst.bcolors (colour class):
                HEADER, OKBLUE, OKGREEN, WARNING, FAIL,
                BOLD, UNDERLINE

    :return clevels: dictionary, containing all the keys identical to
                     LOG_TRIG_KEYS or WRITE_LEVEL, values must be strings
                     that prodive colour information to python print statement
                     see here:
                         http://ozzmaker.com/add-colour-to-text-in-python/
    """
    # reference:
    # http://ozzmaker.com/add-colour-to-text-in-python/
    clevels = dict(error=BColors.FAIL,  # red
                   warning=BColors.WARNING,  # yellow
                   info=BColors.OKGREEN,  # green
                   graph=BColors.OKBLUE,  # green
                   all=BColors.OKGREEN)  # green
    return clevels


# defines the colours
class BColors:
    HEADER = '\033[95;1m'
    OKBLUE = '\033[94;1m'
    OKGREEN = '\033[92;1m'
    WARNING = '\033[93;1m'
    FAIL = '\033[91;1m'
    ENDC = '\033[0;0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# noinspection PyPep8Naming
def COLOURED_LOG(p=None):
    """
    Defines whether we use a coloured log to print to the screen/
    standard output

    :param p: parameter dictionary, ParamDict containing constants
        Must may contain:
            COLOURED_LOG: bool, if True uses coloured log, else non-coloured

    :return clog: bool, decides whether we use a coloured log or not
    """
    if p is None:
        clog = pp['COLOURED_LOG']
    elif 'COLOURED_LOG' not in p:
        clog = pp['COLOURED_LOG']
    else:
        clog = True
    return clog


# noinspection PyPep8Naming
def LOG_EXIT_TYPE():
    """
    Defines how python exits, when an exit is required after logging, string
    input fed into spirouConst.EXIT()

    The exit style (on log exit)

    if 'sys' exits via sys.exit   - soft exit (ipython Exception)
    if 'os' exits via os._exit    - hard exit (complete exit)

    if None - does not exit (this is NOT recommended as it will break all
                             exception handling)

    :return log_exit_type: string or None, the exit type (fed into
                           spirouConst.EXIT())
    """

    # Do nothing on exit call
    # log_exit_type = None
    # Use os._exit
    # log_exit_type = 'os'
    # Use sys.exit
    log_exit_type = 'sys'
    return log_exit_type


# noinspection PyPep8Naming
def EXIT():
    """
    Defines how to exit based on the string defined in
    spirouConst.LOG_EXIT_TYPE()

    :return my_exit: function
    """
    my_exit = LOG_EXIT_TYPE()
    if my_exit == 'sys':
        my_exit = sys.exit
    elif EXIT == 'os':
        # noinspection PyProtectedMember
        my_exit = os._exit
    else:
        def my_exit(_):
            return None
    return my_exit


# noinspection PyPep8Naming
def EXIT_LEVELS():
    """
    Defines which levels (in spirouConst.LOG_TRIG_KEYS and
    spirouConst.WRITE_LEVELS) trigger an exit of the DRS after they are logged
    (must be a list of strings)

    :return exit_levels: list of strings, the keys in spirouConst.LOG_TRIG_KEYS
                         and spirouConst.WRITE_LEVELS which trigger an exit
                         after they are logged
    """
    exit_levels = ['error']
    return exit_levels


# noinspection PyPep8Naming
def DEFAULT_LOG_OPT():
    """
    Defines the default program to use as the "option" in logging
    i.e. option in spirouConfig.WLOG(kind, option, message)

    :return program: string, the default program to use in log option
    """
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
# End of code
# =============================================================================
