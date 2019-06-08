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
from . import spirouConfigFile


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouConst.py'
# Define version
__version__ = '0.5.001'
# Define Authors
# noinspection PyPep8
__author__ = ('N. Cook, F. Bouchy, E. Artigau, , M. Hobson, C. Moutou, '
              'I. Boisse, E. Martioli')
# Define release type
__release__ = 'beta pre-release'
# Define date of last edit
__date__ = '2019-05-27'


# =============================================================================
# Define pre-functions
# =============================================================================
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
def LANGUAGE():
    language = 'ENG'
    return language


# =============================================================================
# Define Constants
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
def RECIPE_CONTROL_FILE():
    """
    Defines the recipe control filename

    :return recipe_control_file: string, the recipe control filename
    """
    recipe_control_file = 'recipe_control.txt'
    recipe_control_format = 'csv'
    return recipe_control_file, recipe_control_format


# noinspection PyPep8Naming
def TELLU_DATABASE_BLACKLIST_FILE():
    """
    Defines the telluric database blacklist filename

    :return blacklistfile: string, the telluric blacklist file
    """
    blacklistfile = 'tellu_blacklist.txt'
    return blacklistfile


# noinspection PyPep8Naming
def TELLU_DATABASE_WHITELIST_FILE():
    """
    Defines the telluric database blacklist filename

    :return blacklistfile: string, the telluric blacklist file
    """
    whitelistfile = 'tellu_whitelist.txt'
    return whitelistfile


# =============================================================================
# Define Directories
# =============================================================================
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


# noinspection PyPep8Naming
def CCF_MASK_DIR():
    """
    Define the ccf mask dir relative path

    :return reldir: str, the relative path
    """

    ccf_mask_dir = './data/ccf_masks'
    return ccf_mask_dir


# noinspection PyPep8Naming
def LSD_MASK_DIR():
    """
    Define the LSD mask dir relative path
        
    :return reldir: str, the relative path
    """
    lsd_mask_dir = './data/lsd_masks'
    return lsd_mask_dir


# noinspection PyPep8Naming
def BADPIX_DIR():
    """
    Define the badpix dir relative path

    :return reldir: str, the relative path
    """
    badpix_dir = './data/badpix'
    return badpix_dir


# noinspection PyPep8Naming
def BARYCORRPY_DIR():
    """
    Define barycorrpy dir relative path

    :return reldir: str, the relative path
    """

    barycorrpy_dir = './data/barycorrpy'
    return barycorrpy_dir


# noinspection PyPep8Naming
def ASTROPY_IERS_DIR():
    astropy_iers_dir = './data/barycorrpy/'
    # File must be downloaded from:
    #     http://maia.usno.navy.mil/ser7/finals2000A.all
    return astropy_iers_dir


# noinspection PyPep8Naming
def RESET_CALIBDB_DIR():
    """
    Define the reset dir relative path
    :return:
    """
    reset_calibdb_dir = './data/reset_calibDB'
    return reset_calibdb_dir


# noinspection PyPep8Naming
def RESET_TELLUDB_DIR():
    """
    Define the reset dir relative path
    :return:
    """
    reset_telludb_dir = './data/reset_telluDB'
    return reset_telludb_dir


# noinspection PyPep8Naming
def WAVELENGTH_CATS_DIR():
    """
    Define the wavelength catalogues dir relative path
    :return:
    """
    wavelength_cats_dir = './data/wavelength_cats'
    return wavelength_cats_dir


# noinspection PyPep8Naming
def CAVITY_LENGTH_FILE():
    """
    Define the cavity length file (located in the WAVELENGTH_CATS_DIR()

    :return:
    """
    cavity_length_file = 'cavity_length.dat'
    return cavity_length_file


# noinspection PyPep8Naming
def DATA_CONSTANT_DIR():
    """
    Define the data constants dir relative path
    :return:
    """
    data_constant_dir = './data/constants/'
    return data_constant_dir


# noinspection PyPep8Naming
def TAGFOLDER():
    tag_folder = './data/constants'
    return tag_folder


# noinspection PyPep8Naming
def TAGFILE():
    tag_file = 'output_keys.py'
    return tag_file


# =============================================================================
# Get constants from constant file
# =============================================================================
# get constants from file
ckwargs = dict(package=PACKAGE(), configfolder=CONFIGFOLDER(),
               configfile=CONFIGFILE(), return_raw=False)
pp = spirouConfigFile.read_config_file(**ckwargs)
if 'USER_CONFIG' in pp:
    pp, _ = spirouConfigFile.get_user_config(pp, package=PACKAGE(),
                                             configfolder=CONFIGFOLDER(),
                                             configfile=CONFIGFILE())

# =============================================================================
# Get tags from tag file
# =============================================================================
ckwargs = dict(package=PACKAGE(), relfolder=TAGFOLDER(),
               filename=TAGFILE())
tags = spirouConfigFile.get_tags(**ckwargs)


# =============================================================================
# Define General functions
# =============================================================================
# noinspection PyPep8Naming
def UPDATE_PP(params):
    # get pp as a global
    global pp
    # set global pp value to local value
    for key in params:
        pp[key] = params[key]


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
def FORBIDDEN_COPY_DRS_KEYS():
    # DRS OUTPUT KEYS
    forbidden_keys = ['WAVELOC', 'REFRFILE', 'DRSPID', 'VERSION',
                      'DRSOUTID']
    # return keys
    return forbidden_keys


# noinspection PyPep8Naming
def FORBIDDEN_HEADER_PREFIXES():
    """
    Define the QC keys prefixes that should not be copied (i.e. they are
    just for the input file not the output file)

    :return keys:
    """
    prefixes = ['QCC', 'INF1', 'INF2', 'INF3', 'INP1']
    # return keys
    return prefixes


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

    # noinspection PyBroadException
    try:
        program = p['PROGRAM']
        log_opt = program
    except Exception:
        log_opt = DEFAULT_LOG_OPT()

    return log_opt


# noinspection PyPep8Naming
def PROGRAM(p=None):
    """
    Defines the recipe/code/program currently running (from sys.argv[0])
    '.py' is removed

    :return program: string, the recipe/code/program name
    """
    # get run time parameters
    rparams = list(sys.argv)
    # get program name
    if p is not None:
        if 'RECIPE' in p:
            program = p['RECIPE'].split('.py')[0]
        else:
            program = os.path.basename(rparams[0]).split('.py')[0]
    else:
        program = os.path.basename(rparams[0]).split('.py')[0]
    # return program
    return program


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
def TMP_DIR(p):
    """
    Defines the temp data directory (for storage of the pre-processing files)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"

    :return raw_dir: string, the raw data directory
    """
    tmp_dir = os.path.join(p['DRS_DATA_WORKING'], p['ARG_NIGHT_NAME'])
    return tmp_dir


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
# Define Input Filename functions
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


# =============================================================================
# Define Output Filename functions
# =============================================================================
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
    func_name = 'DARK_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    darkfitsname = calibprefix + p['ARG_FILE_NAMES'][0]
    darkfits = os.path.join(reducedfolder, darkfitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return darkfits, tag


# noinspection PyPep8Naming
def DARK_FILE_MASTER(p, filename):
    func_name = 'DARK_MASTER_FILE'
    # define input dir
    outdir = p['REDUCED_DIR']
    basefile = os.path.basename(filename)
    # define filename
    basefile = basefile.replace('.fits', '_dark_master.fits')
    # construt absolute filename
    darkmasterfits = os.path.join(outdir, basefile)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return darkmasterfits, tag


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
    func_name = 'DARK_BADPIX_FILE'
    # define filename
    darkfile = DARK_FILE(p)[0]
    badpixelfits = darkfile.replace('.fits', '_badpixel.fits')
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return badpixelfits, tag


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
    func_name = 'BADPIX_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    badpixelfn = p['FLATFILE'].replace('.fits', '_badpixel.fits')
    badpixelfitsname = calibprefix + badpixelfn
    badpixelfits = os.path.join(reducedfolder, badpixelfitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return badpixelfits, tag



# noinspection PyPep8Naming
def BKGD_MAP_FILE(p):
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
    func_name = 'BKGD_MAP_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    badpixelfn = p['FLATFILE'].replace('.fits', '_bmap.fits')
    badpixelfitsname = calibprefix + badpixelfn
    badpixelfits = os.path.join(reducedfolder, badpixelfitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return badpixelfits, tag


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
    func_name = 'LOC_ORDER_PROFILE_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    newext = '_order_profile_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    rawfn = p['ARG_FILE_NAMES'][0].replace('.fits', newext)
    rawfitsname = calibprefix + rawfn
    orderpfile = os.path.join(reducedfolder, rawfitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return orderpfile, tag


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
    func_name = 'LOC_LOCO_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    locoext = '_loco_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    locofn = p['ARG_FILE_NAMES'][0].replace('.fits', locoext)
    locofitsname = calibprefix + locofn
    locofits = os.path.join(reducedfolder, locofitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return locofits, tag


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
    func_name = 'LOC_LOCO_FILE2'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    locoext = '_fwhm-order_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    locofn2 = p['ARG_FILE_NAMES'][0].replace('.fits', locoext)
    locofits2name = calibprefix + locofn2
    locofits2 = os.path.join(reducedfolder, locofits2name)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return locofits2, tag


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
    func_name = 'LOC_LOCO_FILE3'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    locoext = '_with-order_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    locofn3 = p['ARG_FILE_NAMES'][0].replace('.fits', locoext)
    locofits3name = calibprefix + locofn3
    locofits3 = os.path.join(reducedfolder, locofits3name)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return locofits3, tag


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
    func_name = 'SLIT_TILT_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    tiltfn = p['ARG_FILE_NAMES'][0].replace('.fits', '_tilt.fits')
    tiltfitsname = calibprefix + tiltfn
    tiltfits = os.path.join(reduced_dir, tiltfitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return tiltfits, tag



# noinspection PyPep8Naming
def SLIT_SHAPE_LOCAL_FILE(p):
    """
    Defines the shape file location and filename

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :return tiltfits: string, slit tilt file location and filename
    """
    func_name = 'SLIT_SHAPE_LOCAL_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    shapefn = p['ARG_FILE_NAMES'][0].replace('.fits', '_shape.fits')
    shapefitsname = calibprefix + shapefn
    shapefits = os.path.join(reduced_dir, shapefitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return shapefits, tag


# noinspection PyPep8Naming
def SLIT_XSHAPE_FILE(p):
    """
    Defines the shape file location and filename

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :return tiltfits: string, slit tilt file location and filename
    """
    func_name = 'SLIT_XSHAPE_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    shapefn = p['FPFILE'].replace('.fits', '_shapex.fits')
    shapefitsname = calibprefix + shapefn
    shapefits = os.path.join(reduced_dir, shapefitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return shapefits, tag


# noinspection PyPep8Naming
def SLIT_YSHAPE_FILE(p):
    """
    Defines the shape file location and filename

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :return tiltfits: string, slit tilt file location and filename
    """
    func_name = 'SLIT_YSHAPE_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    shapefn = p['FPFILE'].replace('.fits', '_shapey.fits')
    shapefitsname = calibprefix + shapefn
    shapefits = os.path.join(reduced_dir, shapefitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return shapefits, tag


def SLIT_MASTER_FP_FILE(p):
    func_name = 'SLIT_MASTER_FP_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    calibprefix = CALIB_PREFIX(p)
    shapefn = p['FPFILE'].replace('.fits', '_fpmaster.fits')
    shapefitsname = calibprefix + shapefn
    shapefits = os.path.join(reduced_dir, shapefitsname)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return shapefits, tag


# noinspection PyPep8Naming
def SLIT_SHAPE_IN_FP_FILE(p):
    func_name = 'SLIT_SHAPE_IN_FP_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    # get filename
    oldfilename = p['FPFILE']
    # construct prefix
    prefix = 'SHAPE-DEBUG-StartingFp_'
    # construct new filename and full path
    newfilename = prefix + oldfilename
    abspath = os.path.join(reduced_dir, newfilename)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return abspath, tag


# noinspection PyPep8Naming
def SLIT_SHAPE_OUT_FP_FILE(p):
    func_name = 'SLIT_SHAPE_OUT_FP_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    # get filename
    oldfilename = p['FPFILE']
    # construct prefix
    prefix = 'SHAPE-DEBUG-CorrectedFp_'
    # construct new filename and full path
    newfilename = prefix + oldfilename
    abspath = os.path.join(reduced_dir, newfilename)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return abspath, tag


# noinspection PyPep8Naming
def SLIT_SHAPE_IN_HC_FILE(p):
    func_name = 'SLIT_SHAPE_IN_HC_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    # get filename
    oldfilename = p['HCFILE']
    # construct prefix
    prefix = 'SHAPE-DEBUG-StartingHC_'
    # construct new filename and full path
    newfilename = prefix + oldfilename
    abspath = os.path.join(reduced_dir, newfilename)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return abspath, tag


# noinspection PyPep8Naming
def SLIT_SHAPE_OUT_HC_FILE(p):
    func_name = 'SLIT_SHAPE_OUT_HC_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    # get filename
    oldfilename = p['HCFILE']
    # construct prefix
    prefix = 'SHAPE-DEBUG-CorrectedHC_'
    # construct new filename and full path
    newfilename = prefix + oldfilename
    abspath = os.path.join(reduced_dir, newfilename)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return abspath, tag


# noinspection PyPep8Naming
def SLIT_SHAPE_OVERLAP_FILE(p):
    func_name = 'SLIT_SHAPE_OVERLAP_FILE'
    # define filename
    reduced_dir = p['REDUCED_DIR']
    # get filename
    oldfilename = p['FPFILE']
    # construct prefix
    prefix = 'SHAPE-DEBUG-Order_Overlap_'
    # construct new filename and full path
    newfilename = prefix + oldfilename
    abspath = os.path.join(reduced_dir, newfilename)
    # get tag
    tag = tags[func_name]
    # return filename and tag
    return abspath, tag


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
    func_name = 'FF_BLAZE_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']

    reduced_dir = p['REDUCED_DIR']
    blazeext = '_blaze_{0}.fits'.format(fiber)
    calibprefix = CALIB_PREFIX(p)
    blazefn = p['ARG_FILE_NAMES'][0].replace('.fits', blazeext)
    blazefitsname = calibprefix + blazefn
    blazefits = os.path.join(reduced_dir, blazefitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return blazefits, tag


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
    func_name = 'FF_FLAT_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reduced_dir = p['REDUCED_DIR']
    flatext = '_flat_{0}.fits'.format(fiber)
    calibprefix = CALIB_PREFIX(p)
    flatfn = p['ARG_FILE_NAMES'][0].replace('.fits', flatext)
    flatfitsname = calibprefix + flatfn
    flatfits = os.path.join(reduced_dir, flatfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return flatfits, tag


# noinspection PyPep8Naming
def BACKGROUND_CORRECT_FILE(p, fiber=None):
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
    func_name = 'EXTRACT_E2DS_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    e2ds_ext = '_background_{0}.fits'.format(fiber)
    e2dsfitsname = p['ARG_FILE_NAMES'][0].replace('.fits', e2ds_ext)
    e2dsfits = os.path.join(reducedfolder, 'DEBUG_' + e2dsfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return e2dsfits, tag


# noinspection PyPep8Naming
def EXTRACT_E2DS_FILE(p, fiber=None, filename=None):
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
    func_name = 'EXTRACT_E2DS_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    if filename is None:
        filename = p['ARG_FILE_NAMES'][0]

    reducedfolder = p['REDUCED_DIR']
    e2ds_ext = '_e2ds_{0}.fits'.format(fiber)

    e2dsfitsname = filename.replace('.fits', e2ds_ext)
    e2dsfits = os.path.join(reducedfolder, e2dsfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return e2dsfits, tag


# noinspection PyPep8Naming
def EXTRACT_E2DSFF_FILE(p, fiber=None):
    """
    Defines the extraction E2DSFF file name and location

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
    func_name = 'EXTRACT_E2DSFF_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    e2ds_ext = '_e2dsff_{0}.fits'.format(fiber)
    e2dsfitsname = p['ARG_FILE_NAMES'][0].replace('.fits', e2ds_ext)
    e2dsfits = os.path.join(reducedfolder, e2dsfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return e2dsfits, tag


# noinspection PyPep8Naming
def EXTRACT_E2DSLL_FILE(p, fiber=None):
    """
    Defines the extraction E2DSLL file name and location

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
    func_name = 'EXTRACT_E2DSLL_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    e2ds_ext = '_e2dsll_{0}.fits'.format(fiber)
    e2dsfitsname = p['ARG_FILE_NAMES'][0].replace('.fits', e2ds_ext)
    e2dsfits = os.path.join(reducedfolder, e2dsfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return e2dsfits, tag


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
    func_name = 'EXTRACT_LOCO_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    loco_filename = p['CALIBDB']['LOC_{0}'.format(p['LOC_FILE'])][1]
    loco_file = os.path.join(reducedfolder, loco_filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['LOC_FILE'])
    # return filename and tag
    return loco_file, tag


# noinspection PyPep8Naming
def EXTRACT_S1D_FILE1(p, fiber=None):
    """
    Defines the 1D extraction file name and location

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
    func_name = 'EXTRACT_S1D_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    newext = '_s1d_w_{0}.fits'.format(fiber)
    oldext = '.fits'
    filename = p['ARG_FILE_NAMES'][0].replace(oldext, newext)
    absfilepath = os.path.join(reducedfolder, filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return absfilepath, tag


# noinspection PyPep8Naming
def EXTRACT_S1D_FILE2(p, fiber=None):
    """
    Defines the 1D extraction file name and location

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
    func_name = 'EXTRACT_S1D_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    newext = '_s1d_v_{0}.fits'.format(fiber)
    oldext = '.fits'
    filename = p['ARG_FILE_NAMES'][0].replace(oldext, newext)
    absfilepath = os.path.join(reducedfolder, filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return absfilepath, tag


# noinspection PyPep8Naming
def DRIFT_RAW_FILE(p, fiber=None):
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

    :param fiber: string or None, if None uses "FIBER" from p, else is the
                  fiber to use (i.e. AB or A or B or C)

    :return driftfits: string, the drift_raw fits file name and location
    """
    func_name = 'DRIFT_RAW_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_drift_{0}.fits'.format(fiber)
    driftfitsname = p['ARG_FILE_NAMES'][0].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return driftfits, tag


# noinspection PyPep8Naming
def DRIFT_E2DS_FITS_FILE(p, fiber=None):
    """
    Defines the drift_e2ds fits file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name
    :param fiber: string or None, if None uses "FIBER" from p, else is the
                  fiber to use (i.e. AB or A or B or C)

    :return driftfits: string, the drift_e2ds peak drift fits file location
                       and filename
    """
    func_name = 'DRIFT_E2DS_FITS_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_drift_{0}.fits'.format(fiber)
    driftfitsname = p['REFFILENAME'].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return driftfits, tag


# noinspection PyPep8Naming
def DRIFT_E2DS_TBL_FILE(p, fiber=None):
    """
    Defines the drift_e2ds table file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name
    :param fiber: string or None, if None uses "FIBER" from p, else is the
                  fiber to use (i.e. AB or A or B or C)

    :return driftfits: string, the drift_e2ds peak drift table file location
                       and filename
    """
    # func_name = 'DRIFT_E2DS_FITS_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_drift_{0}.tbl'.format(fiber)
    drifttblname = p['REFFILENAME'].replace('.fits', drift_ext)
    drifttbl = os.path.join(reducedfolder, drifttblname)
    # return filename
    return drifttbl


# noinspection PyPep8Naming
def DRIFTCCF_E2DS_FITS_FILE(p, fiber=None):
    """
    Defines the drift_e2ds fits file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name
    :param fiber: string or None, if None uses "FIBER" from p, else is the
                  fiber to use (i.e. AB or A or B or C)

    :return driftfits: string, the drift_e2ds peak drift fits file location
                       and filename
    """
    func_name = 'DRIFTCCF_E2DS_FITS_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_driftccf_{0}.fits'.format(fiber)
    driftfitsname = p['REFFILENAME'].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return driftfits, tag


# noinspection PyPep8Naming
def DRIFTCCF_E2DS_TBL_FILE(p, fiber=None):
    """
    Defines the drift_e2ds table file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name
    :param fiber: string or None, if None uses "FIBER" from p, else is the
                  fiber to use (i.e. AB or A or B or C)

    :return driftfits: string, the drift_e2ds peak drift table file location
                       and filename
    """
    # func_name = 'DRIFTCCF_E2DS_FITS_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_driftccf_{0}.tbl'.format(fiber)
    drifttblname = p['REFFILENAME'].replace('.fits', drift_ext)
    drifttbl = os.path.join(reducedfolder, drifttblname)
    # return filename
    return drifttbl


# noinspection PyPep8Naming
def DRIFTPEAK_E2DS_FITS_FILE(p, fiber=None):
    """
    Defines the drift peak fits drift file name and location using "reffilename"
    and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name
    :param fiber: string or None, if None uses "FIBER" from p, else is the
                  fiber to use (i.e. AB or A or B or C)

    :return driftfits: string, the drift peak drift fits file location and
                       filename
    """
    func_name = 'DRIFTPEAK_E2DS_FITS_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_driftnew_{0}.fits'.format(fiber)
    driftfitsname = p['REFFILENAME'].replace('.fits', drift_ext)
    driftfits = os.path.join(reducedfolder, driftfitsname)
    # get tag
    tag = tags[func_name] + '_{0}'.format(fiber)
    # return filename and tag
    return driftfits, tag


# noinspection PyPep8Naming
def DRIFTPEAK_E2DS_TBL_FILE(p, fiber=None):
    """
    Defines the drift peak drift table file name and location using
    "reffilename" and replacing ".fits" with "_driftnew_{fiber}.fits"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                fiber: string, the fiber type
                reffilename: string, the name of the reference file name
    :param fiber: string or None, if None uses "FIBER" from p, else is the
                  fiber to use (i.e. AB or A or B or C)

    :return driftfits: string, the drift peak drift table file location and
                       filename
    """
    # func_name = 'DRIFTPEAK_E2DS_TBL_FILE'
    # define filename
    if fiber is None:
        fiber = p['FIBER']
    reducedfolder = p['REDUCED_DIR']
    drift_ext = '_driftnew_{0}.tbl'.format(fiber)
    drifttblname = p['REFFILENAME'].replace('.fits', drift_ext)
    drifttbl = os.path.join(reducedfolder, drifttblname)
    # return filename
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
    func_name = 'CCF_FITS_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    # get new extension using ccf_mask without the extention
    newext = '_ccf_' + p['CCF_MASK'].replace('.mas', '')
    # set the new filename as the reference file without the _e2ds
    if '_e2dsff' in p['E2DSFILE']:
        corfilename = p['E2DSFILE'].replace('_e2dsff', newext)
        key = func_name + '_FF'
        tag = tags[key]
    else:
        tag = tags[func_name]
        corfilename = p['E2DSFILE'].replace('_e2ds', newext)

    corfile = os.path.join(reducedfolder, corfilename)
    # return the new ccf file location and name
    return corfile, tag


# noinspection PyPep8Naming
def CCF_FP_FITS_FILE1(p):
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
    func_name = 'CCF_FP_FITS_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    # get new extension using ccf_mask without the extention
    newext = '_ccf_fp_' + p['CCF_MASK'].replace('.mas', '')
    # set the new filename as the reference file without the _e2ds
    if '_e2dsff' in p['E2DSFILE']:
        corfilename = p['E2DSFILE'].replace('_e2dsff', newext)
        key = func_name + '_FF'
        tag = tags[key]
    else:
        tag = tags[func_name]
        corfilename = p['E2DSFILE'].replace('_e2ds', newext)

    corfile = os.path.join(reducedfolder, corfilename)
    # return the new ccf file location and name
    return corfile, tag


# noinspection PyPep8Naming
def CCF_FP_FITS_FILE2(p):
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
    func_name = 'CCF_FP_FITS_FILE'
    # define filename
    reducedfolder = p['REDUCED_DIR']
    # get new extension using ccf_mask without the extention
    newext = '_ccf_fp_' + p['CCF_MASK'].replace('.mas', '')
    # set the new filename as the reference file without the _e2ds
    if '_e2dsff' in p['E2DSFILE']:
        corfilename = p['E2DSFILE'].replace('_e2dsff', newext)
        key = func_name + '_FF'
        tag = tags[key]
    else:
        tag = tags[func_name]
        corfilename = p['E2DSFILE'].replace('_e2ds', newext)

    corfilename = corfilename.replace('AB', 'C')

    corfile = os.path.join(reducedfolder, corfilename)
    # return the new ccf file location and name
    return corfile, tag


# noinspection PyPep8Naming
def CCF_FP_TABLE_FILE1(p):
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
    # func_name = 'CCF_FP_TABLE_FILE'
    # start with the CCF fits file name
    corfile = CCF_FP_FITS_FILE1(p)[0]
    # we want to save the file as a tbl file not a fits file
    ccf_table_file = corfile.replace('.fits', '.tbl')
    # return the new ccf table file location and name
    return ccf_table_file


# noinspection PyPep8Naming
def CCF_FP_TABLE_FILE2(p):
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
    # func_name = 'CCF_FP_TABLE_FILE'
    # start with the CCF fits file name
    corfile = CCF_FP_FITS_FILE2(p)[0]
    # we want to save the file as a tbl file not a fits file
    ccf_table_file = corfile.replace('.fits', '.tbl')
    # return the new ccf table file location and name
    return ccf_table_file


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
    # func_name = 'CCF_TABLE_FILE'
    # start with the CCF fits file name
    corfile = CCF_FITS_FILE(p)[0]
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
    func_name = 'EM_SPE_FILE'
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = 'em_tell_spec_{0}.fits'.format(kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(kind)
    # return absolute path and tag
    return fitsfile, tag


# noinspection PyPep8Naming
def EM_WAVE_FILE(p):
    """
    Defines the cal_exposure_meter wavelength

        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                em_output_type: string, the type of output generated

    :return fitsfile: string, absolute path for the output
    """
    func_name = 'EM_WAVE_FILE'
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = 'em_wavemap_{0}.fits'.format(kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(kind)
    # return absolute path and tag
    return fitsfile, tag


# noinspection PyPep8Naming
def EM_MASK_FILE(p):
    """
    Defines the cal_exposure_meter telluric spectrum map

        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                em_output_type: string, the type of output generated

    :return fitsfile: string, absolute path for the output
    """
    func_name = 'EM_MASK_FILE'
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = 'em_mask_map_{0}.fits'.format(kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(kind)
    # return absolute path and tag
    return fitsfile, tag


# noinspection PyPep8Naming
def EM_ORDERPROFILE_TMP_FILE(p):
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get localisation name
    locofile = p['LOCOFILE'].replace('.fits', '')
    # construct file name
    filename = 'em_orderp_map_{0}.npy'.format(locofile)
    # construct absolute path
    abspath = os.path.join(redfolder, filename)
    # return absolute path
    return abspath


# noinspection PyPep8Naming
def WAVE_MAP_SPE_FILE(p):
    """
    Defines the cal_exposure_meter wavelength

        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                em_output_type: string, the type of output generated

    :return fitsfile: string, absolute path for the output
    """
    func_name = 'WAVE_MAP_SPE_FILE'
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get prefix
    prefix = p['E2DSPREFIX']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = '{0}_{1}_{2}.fits'.format(prefix, 'SPE', kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(kind)
    # return absolute path and tag
    return fitsfile, tag


# noinspection PyPep8Naming
def WAVE_MAP_SPE0_FILE(p):
    """
    Defines the cal_exposure_meter wavelength

        Must contain at least:
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                em_output_type: string, the type of output generated

    :return fitsfile: string, absolute path for the output
    """
    func_name = 'WAVE_MAP_SPE0_FILE'
    # get folder path
    redfolder = p['REDUCED_DIR']
    # get prefix
    prefix = p['E2DSPREFIX']
    # get output type (distinguish)
    kind = p['EM_OUTPUT_TYPE']
    # construct file name
    filename = '{0}_{1}_{2}.fits'.format(prefix, 'SPE0', kind)
    # construct absolute path
    fitsfile = os.path.join(redfolder, filename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(kind)
    # return absolute path and tag
    return fitsfile, tag


# noinspection PyPep8Naming
def WAVE_FILE(p):
    func_name = 'WAVE_FILE'
    # set reduced folder name
    reducedfolder = p['REDUCED_DIR']
    # get filename
    filename = p['ARG_FILE_NAMES'][0]
    # deal with E2DS files and E2DSFF files
    if 'e2dsff' in filename:
        old_ext = '_e2dsff_{0}.fits'.format(p['FIBER'])
    else:
        old_ext = '_e2ds_{0}.fits'.format(p['FIBER'])
    waveext = '_wave_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    wavefn = filename.replace(old_ext, waveext)
    wavefilename = calibprefix + wavefn
    wavefile = os.path.join(reducedfolder, wavefilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return wavefile, tag


# noinspection PyPep8Naming
def WAVE_FILE_EA(p):
    func_name = 'WAVE_FILE_EA'
    # set reduced folder name
    reducedfolder = p['REDUCED_DIR']
    # get filename
    filename = p['ARG_FILE_NAMES'][0]
    # deal with E2DS files and E2DSFF files
    if 'e2dsff' in filename:
        old_ext = '_e2dsff_{0}.fits'.format(p['FIBER'])
    else:
        old_ext = '_e2ds_{0}.fits'.format(p['FIBER'])
    waveext = '_wave_ea_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    wavefn = filename.replace(old_ext, waveext)
    wavefilename = calibprefix + wavefn
    wavefile = os.path.join(reducedfolder, wavefilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return wavefile, tag


# add fp filename if it exists
# noinspection PyPep8Naming
def WAVE_FILE_EA_2(p):
    func_name = 'WAVE_FILE_EA'
    # set reduced folder name
    reducedfolder = p['REDUCED_DIR']
    # get filename
    filename = p['ARG_FILE_NAMES'][0]
    # deal with E2DS files and E2DSFF files
    if 'e2dsff' in filename:
        old_ext = '_e2dsff_{0}.fits'.format(p['FIBER'])
    else:
        old_ext = '_e2ds_{0}.fits'.format(p['FIBER'])
    waveext = '_wave_ea_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    wavefn = filename.replace(old_ext, waveext)
    # check if FP
    if 'FPFILE' in p:
        # get filename
        raw_infile2 = os.path.basename(p['FPFILE'])
        # we shouldn't mix ed2s w e2dsff so can use same extension
        wavefn2 = raw_infile2.replace(old_ext, '_'
                                               '')
        wavefilename = calibprefix + wavefn2 + wavefn
    else:
        wavefilename = calibprefix + wavefn
    wavefile = os.path.join(reducedfolder, wavefilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return wavefile, tag


# add fp filename if it exists
# noinspection PyPep8Naming
def WAVE_FILE_NEW(p):
    func_name = 'WAVE_FILE_EA'
    # set reduced folder name
    reducedfolder = p['REDUCED_DIR']
    # get filename
    filename = p['ARG_FILE_NAMES'][0]
    # deal with E2DS files and E2DSFF files
    if 'e2dsff' in filename:
        old_ext = '_e2dsff_{0}.fits'.format(p['FIBER'])
    else:
        old_ext = '_e2ds_{0}.fits'.format(p['FIBER'])
    waveext = '_wave_new_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    wavefn = filename.replace(old_ext, waveext)
    # check if FP
    if 'FPFILE' in p:
        # get filename
        raw_infile2 = os.path.basename(p['FPFILE'])
        # we shouldn't mix ed2s w e2dsff so can use same extension
        wavefn2 = raw_infile2.replace(old_ext, '_'
                                               '')
        wavefilename = calibprefix + wavefn2 + wavefn
    else:
        wavefilename = calibprefix + wavefn
    wavefile = os.path.join(reducedfolder, wavefilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return wavefile, tag


# noinspection PyPep8Naming
def WAVE_TBL_FILE(p):
    reducedfolder = p['REDUCED_DIR']
    wavetblfb = 'cal_HC_result.tbl'
    wavetblfile = os.path.join(reducedfolder, wavetblfb)
    return wavetblfile


# noinspection PyPep8Naming
def WAVE_FILE_FP(p):
    func_name = 'WAVE_FILE_FP'
    # set reduced folder name
    reducedfolder = p['REDUCED_DIR']
    # get filename
    filename = p['ARG_FILE_NAMES'][0]
    # deal with E2DS files and E2DSFF files
    if 'e2dsff' in filename:
        old_ext = '_e2dsff_{0}.fits'.format(p['FIBER'])
    else:
        old_ext = '_e2ds_{0}.fits'.format(p['FIBER'])
    waveext = '_wave_fp_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    wavefn = filename.replace(old_ext, waveext)
    wavefilename = calibprefix + wavefn
    wavefile = os.path.join(reducedfolder, wavefilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return wavefile, tag


# noinspection PyPep8Naming
def WAVE_TBL_FILE_FP(p):
    reducedfolder = p['REDUCED_DIR']
    wavetblfb = 'cal_WAVE_result.tbl'
    wavetblfile = os.path.join(reducedfolder, wavetblfb)
    return wavetblfile


# noinspection PyPep8Naming
def WAVE_LINE_FILE(p):
    # define filename
    reducedfolder = p['REDUCED_DIR']
    wavellext = '_hc_lines_{0}.tbl'.format(p['FIBER'])
    wavellfn = p['ARG_FILE_NAMES'][0].replace('.fits', wavellext)
    wavellfile = os.path.join(reducedfolder, wavellfn)
    # return filename
    return wavellfile


# noinspection PyPep8Naming
def WAVE_TBL_FILE_EA(p):
    reducedfolder = p['REDUCED_DIR']
    wavetblfb = 'cal_WAVE_EA_result.tbl'
    wavetblfile = os.path.join(reducedfolder, wavetblfb)
    return wavetblfile


# noinspection PyPep8Naming
def WAVE_TBL_FILE_NEW(p):
    reducedfolder = p['REDUCED_DIR']
    wavetblfb = 'cal_WAVE_NEW_result.tbl'
    wavetblfile = os.path.join(reducedfolder, wavetblfb)
    return wavetblfile


# noinspection PyPep8Naming
def WAVE_LINE_FILE_EA(p):
    reducedfolder = p['REDUCED_DIR']
    wavellext = '_hc_lines_ea_{0}.tbl'.format(p['FIBER'])
    wavellfn = p['ARG_FILE_NAMES'][0].replace('.fits', wavellext)
    wavellfile = os.path.join(reducedfolder, wavellfn)
    return wavellfile


# noinspection PyPep8Naming
def WAVE_LINE_FILE_NEW(p):
    reducedfolder = p['REDUCED_DIR']
    wavellext = '_hc_lines_new_{0}.tbl'.format(p['FIBER'])
    wavellfn = p['ARG_FILE_NAMES'][0].replace('.fits', wavellext)
    wavellfile = os.path.join(reducedfolder, wavellfn)
    return wavellfile


# noinspection PyPep8Naming
def WAVE_RES_FILE_EA(p):
    func_name = 'WAVE_RES_FILE_EA'
    # set reduced folder name
    reducedfolder = p['REDUCED_DIR']
    # get filename
    filename = p['ARG_FILE_NAMES'][0]
    # deal with E2DS files and E2DSFF files
    if 'e2dsff' in filename:
        old_ext = '_e2dsff_{0}.fits'.format(p['FIBER'])
    else:
        old_ext = '_e2ds_{0}.fits'.format(p['FIBER'])
    waveext = '_waveres_ea_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    wavefn = filename.replace(old_ext, waveext)
    wavefilename = calibprefix + wavefn
    wavefile = os.path.join(reducedfolder, wavefilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return wavefile, tag


# noinspection PyPep8Naming
def WAVE_RES_FILE_NEW(p):
    func_name = 'WAVE_RES_FILE_EA'
    # set reduced folder name
    reducedfolder = p['REDUCED_DIR']
    # get filename
    filename = p['ARG_FILE_NAMES'][0]
    # deal with E2DS files and E2DSFF files
    if 'e2dsff' in filename:
        old_ext = '_e2dsff_{0}.fits'.format(p['FIBER'])
    else:
        old_ext = '_e2ds_{0}.fits'.format(p['FIBER'])
    waveext = '_waveres_new_{0}.fits'.format(p['FIBER'])
    calibprefix = CALIB_PREFIX(p)
    wavefn = filename.replace(old_ext, waveext)
    wavefilename = calibprefix + wavefn
    wavefile = os.path.join(reducedfolder, wavefilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return wavefile, tag


# noinspection PyPep8Naming
def WAVE_E2DS_COPY(p):
    func_name = 'WAVE_E2DS_COPY'
    # get base filename
    basefilename = os.path.basename(p['FITSFILENAME'])
    # get path
    path = os.path.dirname(p['FITSFILENAME'])
    # get prefix
    calibprefix = CALIB_PREFIX(p)
    # construct filename
    filename = '{0}{1}'.format(calibprefix, basefilename)
    # construct absolute path
    e2dscopy = os.path.join(path, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return e2dscopy, tag


# noinspection PyPep8Naming
def HC_INIT_LINELIST(p):
    # get the directory
    reduced_dir = p['ARG_FILE_DIR']
    # get the first input filename
    old_filename = p['ARG_FILE_NAMES'][0]
    # get the new ext
    new_ext = '_linelist.dat'
    # get the old ext
    old_ext = '.fits'
    # construct new filename
    new_filename = old_filename.replace(old_ext, new_ext)
    # construct absolute path
    abspath = os.path.join(reduced_dir, new_filename)
    # return absolute path and tag
    return abspath


# noinspection PyPep8Naming
def TELLU_TRANS_MAP_FILE(p, filename):
    func_name = 'TELLU_TRANS_MAP_FILE'
    # get path
    path = p['ARG_FILE_DIR']
    # get extension
    newext = '_trans.fits'
    oldext = '.fits'
    # construct filename
    filename = filename.replace(oldext, newext)
    # construct absolute path
    outfile = os.path.join(path, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return outfile, tag


# noinspection PyPep8Naming
def TELLU_ABSO_MAP_FILE(p):
    func_name = 'TELLU_ABSO_MAP_FILE'
    # get path
    path = p['ARG_FILE_DIR']
    # get extension
    filename = 'abso_map.fits'
    # construct absolute path
    outfile = os.path.join(path, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return outfile, tag


# noinspection PyPep8Naming
def TELLU_ABSO_MEDIAN_FILE(p):
    func_name = 'TELLU_ABSO_MEDIAN_FILE'
    # get path
    path = p['ARG_FILE_DIR']
    # get extension
    filename = 'abso_median.fits'
    # construct absolute path
    outfile = os.path.join(path, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path
    return outfile, tag


# noinspection PyPep8Naming
def TELLU_ABSO_NORM_MAP_FILE(p):
    func_name = 'TELLU_ABSO_NORM_MAP_FILE'
    # get path
    path = p['ARG_FILE_DIR']
    # get extension
    filename = 'abso_map_norm.fits'
    # construct absolute path
    outfile = os.path.join(path, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path
    return outfile, tag


# noinspection PyPep8Naming
def TELLU_ABSO_SAVE(p, file_time):
    # get telluDB path
    path = p['DRS_TELLU_DB']
    # construct filename
    prefix = 'tellu_save'
    filename = '{0}_{1}.npy'.format(prefix, file_time)
    # construct absolute path
    outfile = os.path.join(path, filename)
    # return absolute path
    return outfile, prefix


# noinspection PyPep8Naming
def TELLU_FIT_OUT_FILE(p, filename):
    func_name = 'TELLU_FIT_OUT_FILE'
    # define filename
    oldext = '.fits'
    newext = '_tellu_corrected.fits'
    outfilename1 = os.path.basename(filename).replace(oldext, newext)
    outfile1 = os.path.join(p['ARG_FILE_DIR'], outfilename1)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return absolute path
    return outfile1, tag



# noinspection PyPep8Naming
def TELLU_FIT_S1D_FILE1(p, filename):
    """
    Defines the 1D extraction file name and location

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
    func_name = 'TELLU_S1D_FILE1'
    # define filename
    absfilepath, _ = TELLU_FIT_OUT_FILE(p, filename)
    if 'e2dsff' in absfilepath:
        absfilepath = absfilepath.replace('e2dsff', 's1d_w')
    else:
        absfilepath = absfilepath.replace('e2ds', 's1d_w')
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return absfilepath, tag + 'tellu'


# noinspection PyPep8Naming
def TELLU_FIT_S1D_FILE2(p, filename):
    """
    Defines the 1D extraction file name and location

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
    func_name = 'TELLU_S1D_FILE2'
    # define filename
    absfilepath, _ = TELLU_FIT_OUT_FILE(p, filename)
    if 'e2dsff' in absfilepath:
        absfilepath = absfilepath.replace('e2dsff', 's1d_v')
    else:
        absfilepath = absfilepath.replace('e2ds', 's1d_v')
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return filename and tag
    return absfilepath, tag + 'tellu'


# noinspection PyPep8Naming
def TELLU_FIT_RECON_FILE(p, filename):
    func_name = 'TELLU_FIT_RECON_FILE'
    # define filename
    oldext = '.fits'
    newext = '_tellu_recon.fits'
    outfilename2 = os.path.basename(filename).replace(oldext, newext)
    outfile2 = os.path.join(p['ARG_FILE_DIR'], outfilename2)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return absolute path
    return outfile2, tag


# noinspection PyPep8Naming
def OBJTELLU_TEMPLATE_FILE(p, loc):
    func_name = 'OBJTELLU_TEMPLATE_FILE'
    # define filename
    reduced_dir = p['ARG_FILE_DIR']
    outfilename = 'Template_{0}.fits'.format(loc['OBJNAME'])
    outfile = os.path.join(reduced_dir, outfilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return absolute path
    return outfile, tag


# noinspection PyPep8Naming
def OBJTELLU_TEMPLATE_CUBE_FILE1(p, loc):
    func_name = 'OBJTELLU_TEMPLATE_CUBE_FILE1'
    # define filename
    reduced_dir = p['ARG_FILE_DIR']
    outfilename = 'BigCube_{0}.fits'.format(loc['OBJNAME'])
    outfile = os.path.join(reduced_dir, outfilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return absolute path
    return outfile, tag


# noinspection PyPep8Naming
def OBJTELLU_TEMPLATE_CUBE_FILE2(p, loc):
    func_name = 'OBJTELLU_TEMPLATE_CUBE_FILE2'
    # define filename
    reduced_dir = p['ARG_FILE_DIR']
    outfilename = 'BigCube0_{0}.fits'.format(loc['OBJNAME'])
    outfile = os.path.join(reduced_dir, outfilename)
    # get tag
    tag = tags[func_name] + '_{0}'.format(p['FIBER'])
    # return absolute path
    return outfile, tag


# noinspection PyPep8Naming
def DEG_POL_FILE(p, loc):
    func_name = 'DEG_POL_FILE'
    # get reduced dir
    reducedfolder = p['REDUCED_DIR']
    # get base filename
    basefilename = loc['BASENAME']
    # get new extention
    new_ext = '_pol.fits'
    # get new filename
    filename = basefilename.replace('_A.fits', new_ext)
    # construct absolute path
    deg_pol_filename = os.path.join(reducedfolder, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return deg_pol_filename, tag


# noinspection PyPep8Naming
def STOKESI_POL_FILE(p, loc):
    func_name = 'STOKESI_POL_FILE'
    # get reduced dir
    reducedfolder = p['REDUCED_DIR']
    # get base filename
    basefilename = loc['BASENAME']
    # get new extention
    new_ext = '_AB_StokesI.fits'
    # get new filename
    filename = basefilename.replace('_A.fits', new_ext)
    # construct absolute path
    stokesI_filename = os.path.join(reducedfolder, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return stokesI_filename, tag


# noinspection PyPep8Naming
def NULL_POL1_FILE(p, loc):
    func_name = 'NULL_POL1_FILE'
    # get reduced dir
    reducedfolder = p['REDUCED_DIR']
    # get base filename
    basefilename = loc['BASENAME']
    # get new extention
    new_ext = '_null1_pol.fits'
    # get new filename
    filename = basefilename.replace('_A.fits', new_ext)
    # construct absolute path
    null_pol1_filename = os.path.join(reducedfolder, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return null_pol1_filename, tag


# noinspection PyPep8Naming
def NULL_POL2_FILE(p, loc):
    func_name = 'NULL_POL2_FILE'
    # get reduced dir
    reducedfolder = p['REDUCED_DIR']
    # get base filename
    basefilename = loc['BASENAME']
    # get new extention
    new_ext = '_null2_pol.fits'
    # get new filename
    filename = basefilename.replace('_A.fits', new_ext)
    # construct absolute path
    null_pol2_filename = os.path.join(reducedfolder, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return null_pol2_filename, tag


# noinspection PyPep8Naming
def LSD_POL_FILE(p, loc):
    func_name = 'LSD_POL_FILE'
    # get reduced dir
    reducedfolder = p['REDUCED_DIR']
    # get base filename
    basefilename = loc['BASENAME']
    # get new extention
    new_ext = '_lsd_pol.fits'
    # get new filename
    filename = basefilename.replace('_A.fits', new_ext)
    # construct absolute path
    lsd_pol_filename = os.path.join(reducedfolder, filename)
    # get tag
    tag = tags[func_name]
    # return absolute path and tag
    return lsd_pol_filename, tag


# noinspection PyPep8Naming
def OFF_LISTING_RAW_FILE(p):
    # get constants from p
    msg_dir = p['DRS_DATA_MSG']
    night_name = p['ARG_NIGHT_NAME']
    # get base filename
    basefilename = 'listing_raw_{0}.txt'.format(os.path.split(night_name)[-1])
    # get absolute path
    abspath = os.path.join(msg_dir, basefilename)
    # return absolute path and tag
    return abspath


# noinspection PyPep8Naming
def OFF_LISTING_REDUC_FILE(p):
    # get constants from p
    msg_dir = p['DRS_DATA_MSG']
    night_name = p['ARG_NIGHT_NAME']
    # get base filename
    basefilename = 'listing_reduc_{0}.txt'.format(os.path.split(night_name)[-1])
    # get absolute path
    abspath = os.path.join(msg_dir, basefilename)
    # return absolute path and tag
    return abspath


# =============================================================================
# Define output file function
# =============================================================================
# noinspection PyPep8Naming
def INDEX_OUTPUT_FILENAME():
    filename = 'index.fits'
    return filename


# noinspection PyPep8Naming
def INDEX_LOCK_FILENAME(p):
    # get the message directory
    if 'DRS_DATA_MSG' not in p:
        p['DRS_DATA_MSG'] = './'
    if not os.path.exists(p['DRS_DATA_MSG']):
        p['DRS_DATA_MSG'] = './'
    # get the night name directory
    if 'ARG_NIGHT_NAME' not in p:
        night_name = 'UNKNOWN'
    else:
        night_name = p['ARG_NIGHT_NAME'].replace(os.sep, '_')
        night_name = night_name.replace(' ', '_')
    # get the index file
    index_file = INDEX_OUTPUT_FILENAME()
    # construct the index lock file name
    oargs = [night_name, index_file]
    opath = os.path.join(p['DRS_DATA_MSG'], '{0}_{1}'.format(*oargs))
    # return the index lock file name
    return opath


# noinspection PyPep8Naming
def OUTPUT_FILE_HEADER_KEYS(p):
    """
    Output file header keys.

    This list is the master list and RAW_OUTPUT_COLUMNS, REDUC_OUTPUT_COLUMNS
    etc must be in this list
    :param p:
    :return:
    """
    # Get required header keys from spirouKeywords.py (via p)
    output_keys = [p['KW_DATE_OBS'][0],
                   p['KW_UTC_OBS'][0],
                   p['KW_ACQTIME'][0],
                   p['KW_OBJNAME'][0],
                   p['KW_OBSTYPE'][0],
                   p['KW_EXPTIME'][0],
                   p['KW_CCAS'][0],
                   p['KW_CREF'][0],
                   p['KW_CDEN'][0],
                   p['KW_DPRTYPE'][0],
                   p['KW_OUTPUT'][0],
                   p['KW_EXT_TYPE'][0],
                   p['KW_CMPLTEXP'][0],
                   p['KW_NEXP'][0],
                   p['KW_VERSION'][0],
                   p['KW_PPVERSION'][0]]
    # return output_keys
    return output_keys


# noinspection PyPep8Naming
def RAW_OUTPUT_COLUMNS(p):
    func_name = __NAME__ + '.RAW_OUTPUT_COLUMNS()'
    # define selected keys
    output_keys = [p['KW_DATE_OBS'][0],
                   p['KW_UTC_OBS'][0],
                   p['KW_ACQTIME'][0],
                   p['KW_OBJNAME'][0],
                   p['KW_OBSTYPE'][0],
                   p['KW_EXPTIME'][0],
                   p['KW_DPRTYPE'][0],
                   p['KW_CCAS'][0],
                   p['KW_CREF'][0],
                   p['KW_CDEN'][0],
                   p['KW_CMPLTEXP'][0],
                   p['KW_NEXP'][0],
                   p['KW_PPVERSION'][0]]
    # check in master list
    masterlist = __NAME__ + '.OUTPUT_FILE_HEADER_KEYS()'
    for key in output_keys:
        if key not in OUTPUT_FILE_HEADER_KEYS(p):
            emsg1 = 'Key {0} must be in {1}'.format(key, masterlist)
            emsg2 = '\tfunction = {0}'.format(func_name)
            raise ValueError(emsg1 + '\n' + emsg2)
    # return keys
    return output_keys


# noinspection PyPep8Naming
def REDUC_OUTPUT_COLUMNS(p):
    func_name = __NAME__ + '.REDUC_OUTPUT_COLUMNS()'

    output_keys = [p['KW_DATE_OBS'][0],
                   p['KW_UTC_OBS'][0],
                   p['KW_ACQTIME'][0],
                   p['KW_OBJNAME'][0],
                   p['KW_OUTPUT'][0],
                   p['KW_EXT_TYPE'][0],
                   p['KW_VERSION'][0]]
    # check in master list
    masterlist = __NAME__ + '.OUTPUT_FILE_HEADER_KEYS()'
    for key in output_keys:
        if key not in OUTPUT_FILE_HEADER_KEYS(p):
            emsg1 = 'Key {0} must be in {1}'.format(key, masterlist)
            emsg2 = '\tfunction = {0}'.format(func_name)
            raise ValueError(emsg1 + '\n' + emsg2)
    # return keys
    return output_keys


# noinspection PyPep8Naming
def GEN_OUTPUT_COLUMNS(p):
    output_keys = [p['KW_DATE_OBS'][0],
                   p['KW_UTC_OBS'][0],
                   p['KW_ACQTIME'][0],
                   p['KW_OBJNAME'][0],
                   p['KW_OBSTYPE'][0],
                   p['KW_EXPTIME'][0],
                   p['KW_OUTPUT'][0],
                   p['KW_EXT_TYPE'][0],
                   p['KW_VERSION'][0]]
    return output_keys


# =============================================================================
# Define database functions
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


# noinspection PyPep8Naming
def TELLUDB_MASTERFILE(p):
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
    masterfilepath = os.path.join(p['DRS_TELLU_DB'], p['IC_TELLUDB_FILENAME'])
    return masterfilepath


# noinspection PyPep8Naming
def TELLUDB_LOCKFILE(p):
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
    lockfilepath = os.path.join(p['DRS_TELLU_DB'], 'lock_telluDB')
    return lockfilepath


# noinspection PyPep8Naming
def TELLU_PREFIX(p):
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
def DATE_FMT_HEADER():
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
    date_fmt_header = '%Y-%m-%dT%H:%M:%S'

    return date_fmt_header


# noinspection PyPep8Naming
def ASTROPY_DATE_FMT_CALIBDB():
    date_fmt = 'iso'
    return date_fmt


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
def DATE_FMT_TELLUDB():
    """
    The date format for string timestamp in the telluric database

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

    :return date_fmt_telludb: string, the string timestamp format for the
                              calibration database
    """
    date_fmt_telludb = '%Y-%m-%d-%H:%M:%S.%f'
    return date_fmt_telludb


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
def LOG_FILE_NAME(p, dir_data_msg=None):
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

    :return lpath: string, the full path and file name for the log file
    """
    # deal with no dir_data_msg
    if dir_data_msg is None:
        dir_data_msg = p.get('DRS_DATA_MSG', './')

    # deal with no PID
    if 'PID' not in p:
        pid = 'UNKNOWN-PID'
    else:
        pid = p['PID']

    # deal with no recipe
    if 'RECIPE' not in p:
        recipe = 'UNKNOWN-RECIPE'
    else:
        recipe = p['RECIPE'].replace('.py', '')

    # Get the HOST name (if it does not exist host = 'HOST')
    host = os.environ.get('HOST', 'HOST')
    # construct the logfile path
    largs = [host, pid, recipe]
    lpath = os.path.join(dir_data_msg, 'DRS-{0}_{1}_{2}'.format(*largs))
    # return lpath
    return lpath


# noinspection PyPep8Naming
def CHARACTER_LOG_LENGTH():
    length = 80
    return length


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
    >> WLOG(p, 'error', 'message')
    the output is:
    >> print("TIMESTAMP - ! |program|message")

    :return trig_key: dictionary, contains all the trigger keys and the
                      characters/strings to use in logging. Keys must be the
                      same as spirouConst.WRITE_LEVELS()
    """
    # The trigger character to display for each
    trig_key = dict(all=' ', error='!', warning='@', info='*', graph='~',
                    debug='+')
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
    write_level = dict(error=3, warning=2, info=1, graph=0, all=0,
                       debug=0)
    return write_level


# noinspection PyPep8Naming
def LOG_STORAGE_KEYS():
    # The storage key to use for each key
    storekey = dict(all='LOGGER_ALL', error='LOGGER_ERROR',
                    warning='LOGGER_WARNING', info='LOGGER_INFO',
                    graph='LOGGER_ALL', debug='LOGGER_DEBUG')
    return storekey


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
def COLOUREDLEVELS(p=None):
    """
    Defines the colours if using coloured log.
    Allowed colour strings are found here:
            see here:
            http://ozzmaker.com/add-colour-to-text-in-python/
            or in spirouConst.colors (colour class):
                HEADER, OKBLUE, OKGREEN, WARNING, FAIL,
                BOLD, UNDERLINE

    :return clevels: dictionary, containing all the keys identical to
                     LOG_TRIG_KEYS or WRITE_LEVEL, values must be strings
                     that prodive colour information to python print statement
                     see here:
                         http://ozzmaker.com/add-colour-to-text-in-python/
    """
    # reference:
    colors = Colors()
    if p is not None:
        if 'THEME' in p:
            colors.update_theme(p['THEME'])
    # http://ozzmaker.com/add-colour-to-text-in-python/
    clevels = dict(error=colors.fail,       # red
                   warning=colors.warning,  # yellow
                   info=colors.okblue,      # blue
                   graph=colors.ok,         # magenta
                   all=colors.okgreen,      # green
                   debug=colors.debug)      # green
    return clevels


# defines the colours
# noinspection PyPep8Naming
class Colors:
    BLACK1 = '\033[90;1m'
    RED1 = '\033[1;91;1m'
    GREEN1 = '\033[92;1m'
    YELLOW1 = '\033[1;93;1m'
    BLUE1 = '\033[94;1m'
    MAGENTA1 = '\033[1;95;1m'
    CYAN1 = '\033[1;96;1m'
    WHITE1 = '\033[97;1m'
    BLACK2 = '\033[1;30m'
    RED2 = '\033[1;31m'
    GREEN2 = '\033[1;32m'
    YELLOW2 = '\033[1;33m'
    BLUE2 = '\033[1;34m'
    MAGENTA2 = '\033[1;35m'
    CYAN2 = '\033[1;36m'
    WHITE2 = '\033[1;37m'
    ENDC = '\033[0;0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self):
        if 'THEME' not in pp:
            self.theme = 'DARK'
        else:
            self.theme = pp['THEME']
        self.endc = self.ENDC
        self.bold = self.BOLD
        self.underline = self.UNDERLINE

        self.header = self.MAGENTA1
        self.okblue = self.BLUE1
        self.okgreen = self.GREEN1
        self.ok = self.MAGENTA2
        self.warning = self.YELLOW1
        self.fail = self.RED1
        self.debug = self.BLACK1

        self.update_theme()

    def update_theme(self, theme=None):
        if theme is not None:
            self.theme = theme
        if self.theme == 'DARK':
            self.header = self.MAGENTA1
            self.okblue = self.BLUE1
            self.okgreen = self.GREEN1
            self.ok = self.MAGENTA2
            self.warning = self.YELLOW1
            self.fail = self.RED1
            self.debug = self.BLACK1
        else:
            self.header = self.MAGENTA2
            self.okblue = self.MAGENTA2
            self.okgreen = self.BLACK2
            self.ok = self.MAGENTA2
            self.warning = self.BLUE2
            self.fail = self.RED2
            self.debug = self.GREEN2


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
        clog = p['COLOURED_LOG']
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
    elif my_exit == 'os':
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


# noinspection PyPep8Naming
def MAX_DISPLAY_LIMIT():
    """
    Maximum display limit for files/directory when argument error raise
    :return:
    """
    max_display_limit = 15
    return max_display_limit


# noinspection PyPep8Naming
def HEADER():
    header = ' ' + '*' * 65
    return header


# =============================================================================
# Plot functions
# =============================================================================
# noinspection PyPep8Naming
def PLOT_FONT_SIZE():
    """
    Set the default font size for all graphs

    Note: A good size for viewing on the screen is around 12

    setting value to None will use system defaults

    :return fontsize: int or string or None: fontsize accepted by matplotlib
    """
    # fontsize = 20
    fontsize = 'None'
    return fontsize


# noinspection PyPep8Naming
def PLOT_FONT_WEIGHT():
    """
    Set the default font weight for all graphs

    setting value to None will use system defaults

    :return weight: string or None: font weight accepted by matplotlib
    """
    # weight = 'bold'
    # weight = 'normal'
    weight = 'None'
    return weight


# noinspection PyPep8Naming
def PLOT_FONT_FAMILY():
    """
    Set the default font family for all graphs (i.e. monospace)

    setting value to None will use system defaults

    :return family: string or None: font family (style name) accepted by
                    matplotlib
    """
    # family = 'monospace'
    family = 'None'
    return family


# noinspection PyPep8Naming
def PLOT_STYLE():

    # style = 'seaborn'
    # style = 'dark_background'
    style = 'None'
    return style


# noinspection PyPep8Naming
def FONT_DICT():
    """
    Font manager for matplotlib fonts - added to matplotlib.rcParams as a
    dictionary
    :return font: rcParams dictionary (must be accepted by maplotlbi.rcParams)

    see:
      https://matplotlib.org/api/matplotlib_configuration_api.html#matplotlib.rc
    """
    font = dict()
    if PLOT_FONT_FAMILY() != 'None':
        font['family'] = PLOT_FONT_FAMILY()
    if PLOT_FONT_WEIGHT() != 'None':
        font['weight'] = PLOT_FONT_WEIGHT()
    if PLOT_FONT_SIZE() != 'None':
        font['size'] = PLOT_FONT_SIZE()
    return font


# noinspection PyPep8Naming
def PLOT_EXTENSIONS():
    """
    Extensions for plotting

    Supported formats: eps, pdf, pgf, png, ps, raw, rgba, svg, svgz

    :return:
    """
    extensions = ['png', 'pdf']
    return extensions


# noinspection PyPep8Naming
def PLOT_FIGSIZE():
    """
    The fig size (in inches) for all saved figures
    :return:
    """
    figsize = (10, 8)
    return figsize


# =============================================================================
# End of code
# =============================================================================
