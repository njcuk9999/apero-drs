#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO base definitions

Some things must be defined once and used throughout the drs
Most functions do not go in here

Created on 2020-08-2020-08-21 19:43

@author: cook

import rules:

- no imports from apero

"""
import os
import string
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from astropy.time import Time, TimeDelta

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'apero'
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = 'None'
__version__ = '0.7.283'
__author__ = ['N. Cook', 'E. Artigau', 'F. Bouchy', 'M. Hobson', 'C. Moutou',
              'I. Boisse', 'E. Martioli']
__date__ = '2023-05-23'
__release__ = 'alpha pre-release'
# do this once per drs import
__now__ = Time.now()
AstropyTime = Time
AstropyTimeDelta = TimeDelta
# List of author names
AUTHORS = dict()
AUTHORS['NJC'] = 'Neil James Cook'
AUTHORS['EA'] = 'Etienne Artigau'
AUTHORS['EM'] = 'Eder Martioli'
AUTHORS['MH'] = 'Melissa Hobson'

# Define yaml files
INSTALL_YAML = 'install.yaml'
DATABASE_YAML = 'database.yaml'
USER_ENV = 'DRS_UCONFIG'
# switch for no db in args
NO_DB = False
# Define instruments (last one should be 'None')
INSTRUMENTS = ['SPIROU', 'NIRPS_HA', 'NIRPS_HE', 'None']
# -----------------------------------------------------------------------------
# constants/parameter settings
# -----------------------------------------------------------------------------
CONST_PATH = './core/instruments/'
CORE_PATH = './core/instruments/default/'
PDB_RC_FILE = './data/core/pdbrc_full'
PDB_RC_FILENAME = '.pdbrc'
SCRIPTS = ['default_config.py', 'default_constants.py', 'default_keywords.py']
USCRIPTS = ['user_config.ini', 'user_constants.ini', 'user_keywords.ini']
PSEUDO_CONST_FILE = 'pseudo_const.py'
PSEUDO_CONST_CLASS = 'PseudoConstants'
DEFAULT_PSEUDO_CONST_CLASS = 'DefaultPseudoConstants'
# absolute paths (from relative paths to here)
RECOMM_USER = __PATH__.parent.joinpath('requirements_current.txt')
RECOMM_DEV = __PATH__.parent.joinpath('requirements_developer.txt')
# -----------------------------------------------------------------------------
# warnings
# -----------------------------------------------------------------------------
# only use this to turn warnings to errors (we need to use this flag to stop
#   some exceptions creating long loops and freezing when all warnings go to
#   errors)
WARN_TO_ERROR = False
# this is how we turn warnings to errors
if WARN_TO_ERROR:
    warnings.filterwarnings('error')

# -----------------------------------------------------------------------------
# databases
DATABASE_NAMES = ['calib', 'tellu', 'findex', 'log', 'astrom', 'lang', 'reject']
DATABASE_FULLNAMES = ['calibration', 'telluric', 'file index', 'recipe log',
                      'astrometric', 'language', 'rejection']
DATABASE_COL_CLASS = ['CALIBRATION_DB_COLUMNS', 'TELLURIC_DB_COLUMNS',
                      'FILEINDEX_DB_COLUMNS', 'LOG_DB_COLUMNS',
                      'ASTROMETRIC_DB_COLUMNS', None, 'REJECT_DB_COLUMNS']
# -----------------------------------------------------------------------------
# language settings
# -----------------------------------------------------------------------------
DEFAULT_LANG = 'ENG'
LANGUAGES = ['ENG', 'FR']
LANG_DEFAULT_PATH = './lang/databases/'
LANG_INSTRUMNET_PATH = './lang/databases/'
LANG_BACKUP_PATH = './lang/backup/'
LANG_XLS_FILE = 'language.xls'
LANG_DB_FILE = 'lang.db'
LANG_DB_RESET = 'reset.lang.csv'
LANG_DB_RESET_INST = 'reset.lang.{0}.csv'
GSPARAM = ('OE4_WF0Btk29', 'Gmb8SrbTJ3UF')
# -----------------------------------------------------------------------------
# types definitions
# -----------------------------------------------------------------------------
# Define simple types allowed for constants
SIMPLE_TYPES = [int, float, str, bool, list]
SIMPLE_STYPES = ['int', 'float', 'str', 'bool', 'list']
# define valid characters
VALID_CHARS = list(string.ascii_letters) + list(string.digits)
VALID_CHARS += list(string.punctuation) + list(string.whitespace)
# define display strings for types
STRTYPE = OrderedDict()
STRTYPE[int] = 'int'
STRTYPE[float] = 'float'
STRTYPE[str] = 'str'
STRTYPE[complex] = 'complex'
STRTYPE[list] = 'list'
STRTYPE[bool] = 'bool'
STRTYPE[np.ndarray] = 'np.ndarray'
# define types that we can do min and max on
NUMBER_TYPES = [int, float]
# -----------------------------------------------------------------------------
# display settings
# -----------------------------------------------------------------------------
# define colours (should not be used if we have access to drs_misc)
COLOURS = dict()
COLOURS['BLACK1'] = '\033[90;1m'
COLOURS['RED1'] = '\033[1;91;1m'
COLOURS['GREEN1'] = '\033[92;1m'
COLOURS['YELLOW1'] = '\033[1;93;1m'
COLOURS['BLUE1'] = '\033[94;1m'
COLOURS['MAGENTA1'] = '\033[1;95;1m'
COLOURS['CYAN1'] = '\033[1;96;1m'
COLOURS['WHITE1'] = '\033[97;1m'
COLOURS['BLACK2'] = '\033[1;30m'
COLOURS['RED2'] = '\033[1;31m'
COLOURS['GREEN2'] = '\033[1;32m'
COLOURS['YELLOW2'] = '\033[1;33m'
COLOURS['BLUE2'] = '\033[1;34m'
COLOURS['MAGENTA2'] = '\033[1;35m'
COLOURS['CYAN2'] = '\033[1;36m'
COLOURS['WHITE2'] = '\033[1;37m'
COLOURS['ENDC'] = '\033[0;0m'
COLOURS['BOLD'] = '\033[1m'
COLOURS['UNDERLINE'] = '\033[4m'
# -----------------------------------------------------------------------------
# allowed log flags
# -----------------------------------------------------------------------------
# define default flags for all recipes
DEFAULT_FLAGS = dict(IN_PARALLEL=False, RUNNING=False, ENDED=False,
                     FORCE_REFWAVE=False, USER_FIBERS=False)
# define allowed log flags
LOG_FLAGS = dict()
# LOG_FLAG[key] = description
LOG_FLAGS['IN_PARALLEL'] = 'Recipe was run in parallel'
LOG_FLAGS['RUNNING'] = 'Recipe is still running and has not ended'
LOG_FLAGS['ENDED'] = 'Recipe has ended'
LOG_FLAGS['FORCE_REFWAVE'] = 'Wave solution was forced to reference wave sol'
LOG_FLAGS['OBJ'] = 'Is an OBJECT file'
LOG_FLAGS['QCPASSED'] = 'Preprocessing passed QC'
LOG_FLAGS['SCIFIBER'] = 'Localisation recipe used the science fiber'
LOG_FLAGS['REFFIBER'] = 'Localisation recipe used the reference fiber'
LOG_FLAGS['INT_EXT'] = 'An internal extraction is done in this recipe'
LOG_FLAGS['EXT_FOUND'] = 'Extracted files for internal extraction were found.'
LOG_FLAGS['USER_FIBERS'] = 'User changed the expected fibers'
LOG_FLAGS['QUICKLOOK'] = 'Extraction is running in quick look mode'
LOG_FLAGS['EXP_FPLINE'] = 'Extraction has an FP ref fiber and addition outputs'
LOG_FLAGS['INPUTQC'] = 'Polar inputs passed QC (or were forced to)'
LOG_FLAGS['ONLYPRECLEAN'] = 'Only do preclean part of telluric correction'


# =============================================================================
# Define functions
# =============================================================================
def load_database_yaml() -> dict:
    """
    Load database yaml file

    :return: dict, the loaded yaml file
    """
    # check for environmental variable
    if USER_ENV in os.environ:
        # get path
        path = os.environ[USER_ENV]
        # add filename
        path = os.path.join(path, DATABASE_YAML)
        # check that path exists
        if os.path.exists(path):
            # load yaml file
            return load_yaml(path)
        else:
            # raise an error
            emsg = 'Core Error: {0}={1} does not exist'
            raise EnvironmentError(emsg.format(USER_ENV, path))
    # else raise except (cannot come from database)
    emsg = 'Core Error: {0} must be set (please run setup script)'
    raise EnvironmentError(emsg.format(USER_ENV))


def load_install_yaml() -> dict:
    """
    Load installation yaml file

    :return: dict, the loaded installation yaml
    """
    # check for environmental variable
    if USER_ENV in os.environ:
        # get path
        path = os.environ[USER_ENV]
        # add filename
        path = os.path.join(path, INSTALL_YAML)
        # check that path exists
        if os.path.exists(path):
            # load yaml file
            return load_yaml(path)
        else:
            # raise an error
            emsg = 'Core Error: {0}={1} does not exist'
            raise EnvironmentError(emsg.format(USER_ENV, path))
    # else raise except (cannot come from database)
    emsg = 'Core Error: {0} must be set (please run setup script)'
    raise EnvironmentError(emsg.format(USER_ENV))


def load_yaml(filename: str) -> dict:
    """
    Load a yaml file as a dictionary

    :param filename: str, the filename (absolute path) of the yaml file

    :returns: dictionary dict, the dictionary loaded from yaml file
    """
    with open(filename, 'r') as yfile:
        dictionary = yaml.load(yfile, Loader=yaml.FullLoader)
    return dictionary


def write_yaml(dictionary: dict, filename: str):
    """
    Write a yaml file from a dictionary

    :param dictionary: dict, the dictionary to write
    :param filename: str, the filename (absolute path) of the yaml file

    :return: None - writes yaml file 'filename'
    """
    # save file
    with open(filename, 'w') as yfile:
        yaml.dump(dictionary, yfile)


def create_yamls(allparams: Any):
    """
    Create the yaml files from allparams

    :param allparams: ParamDict, the parameter dictionary of installation

    :return: None - writes install.yaml and database.yaml
    """
    # get config directory
    userconfig = Path(allparams['USERCONFIG'])
    # -------------------------------------------------------------------------
    # create install yaml
    # -------------------------------------------------------------------------
    # get save path
    install_path = userconfig.joinpath(INSTALL_YAML)
    # populate dictionary
    install_dict = dict()
    install_dict['DRS_UCONFIG'] = str(userconfig)
    install_dict['INSTRUMENT'] = allparams['INSTRUMENT']
    install_dict['LANGUAGE'] = allparams['LANGUAGE']
    install_dict['USE_TQDM'] = True
    # write database
    write_yaml(install_dict, str(install_path))
    # -------------------------------------------------------------------------
    # create database yaml
    # -------------------------------------------------------------------------
    # get save path
    database_path = userconfig.joinpath(DATABASE_YAML)
    # populate dictionary
    database_dict = dict()
    # -------------------------------------------------------------------------
    #  SQLITE SETTINGS
    # -------------------------------------------------------------------------
    # sql lite settings
    database_dict['USE_SQLITE3'] = allparams['SQLITE'].get('USE_SQLITE3', True)
    sqlite3 = dict()
    sdict = allparams['SQLITE']
    # add database settings
    sqlite3['HOST'] = sdict.get('HOST', 'NULL')
    sqlite3['USER'] = sdict.get('USER', 'NULL')
    sqlite3['PASSWD'] = sdict.get('PASSWD', 'NULL')
    sqlite3['DATABASE'] = sdict.get('DATABASE', 'NULL')
    # add calib database
    calibdb = dict()
    calibdb['PATH'] = sdict.get('CALIB_PATH', 'DRS_CALIB_DB')
    calibdb['NAME'] = sdict.get('CALIB_NAME', 'calib.db')
    calibdb['RESET'] = sdict.get('CALIB_RESET', 'reset.calib.csv')
    calibdb['PROFILE'] = sdict.get('CALIB_PROFILE', 'NULL')
    sqlite3['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['PATH'] = sdict.get('TELLU_PATH', 'DRS_TELLU_DB')
    telludb['NAME'] = sdict.get('TELLU_NAME', 'tellu.db')
    telludb['RESET'] = sdict.get('TELLU_RESET', 'reset.tellu.csv')
    telludb['PROFILE'] = sdict.get('TELLU_PROFILE', 'NULL')
    sqlite3['TELLU'] = telludb
    # add index database
    findexdb = dict()
    findexdb['PATH'] = sdict.get('FINDEX_PATH', 'DRS_DATA_ASSETS')
    findexdb['NAME'] = sdict.get('FINDEX_NAME', 'index.db')
    findexdb['RESET'] = sdict.get('FINDEX_RESET', 'NULL')
    findexdb['PROFILE'] = sdict.get('FINDEX_PROFILE', 'NULL')
    sqlite3['FINDEX'] = findexdb
    # add log database
    logdb = dict()
    logdb['PATH'] = sdict.get('LOG_PATH', 'DRS_DATA_ASSETS')
    logdb['NAME'] = sdict.get('LOG_NAME', 'log.db')
    logdb['RESET'] = sdict.get('LOG_RESET', 'NULL')
    logdb['PROFILE'] = sdict.get('LOG_PROFILE', 'NULL')
    sqlite3['LOG'] = logdb
    # add object database
    astromdb = dict()
    astromdb['PATH'] = sdict.get('ASTROM_PATH', 'DRS_DATA_ASSETS')
    astromdb['NAME'] = sdict.get('ASTROM_NAME', 'object.db')
    astromdb['RESET'] = sdict.get('ASTROM_RESET', 'reset.astrom.csv')
    astromdb['PROFILE'] = sdict.get('ASTROM_PROFILE', 'NULL')
    sqlite3['ASTROM'] = astromdb
    # add reject database
    rejectdb = dict()
    rejectdb['PATH'] = sdict.get('REJECT_PATH', 'DRS_DATA_ASSETS')
    rejectdb['NAME'] = sdict.get('REJECT_NAME', 'reject.db')
    rejectdb['RESET'] = sdict.get('REJECT_RESET', 'NULL')
    rejectdb['PROFILE'] = sdict.get('REJECT_PROFILE', 'NULL')
    sqlite3['REJECT'] = rejectdb
    # add language database
    langdb = dict()
    langdb['PATH'] = sdict.get('LANG_PATH', 'DRS_DATA_ASSETS')
    langdb['NAME'] = sdict.get('LANG_PATH', 'lang.db')
    langdb['RESET'] = sdict.get('LANG_PATH', 'NULL')
    langdb['PROFILE'] = sdict.get('LANG_PROFILE', 'NULL')
    sqlite3['LANG'] = langdb
    # add sqlite database to database_dict
    database_dict['SQLITE3'] = sqlite3
    # -------------------------------------------------------------------------
    #  MYSQL SETTINGS
    # -------------------------------------------------------------------------
    # mysql settings
    database_dict['USE_MYSQL'] = allparams['MYSQL'].get('USE_MYSQL', False)
    mysql = dict()
    mdict = allparams['MYSQL']
    # add database settings
    mysql['HOST'] = mdict.get('HOST', 'localhost')
    mysql['USER'] = mdict.get('USER', 'None')
    mysql['PASSWD'] = mdict.get('PASSWD', 'None')
    mysql['DATABASE'] = mdict.get('DATABASE', 'None')
    # add calib database
    calibdb = dict()
    calibdb['PATH'] = mdict.get('CALIB_PATH', 'NULL')
    calibdb['NAME'] = mdict.get('CALIB_NAME', 'NULL')
    calibdb['RESET'] = mdict.get('CALIB_RESET', 'reset.calib.csv')
    calibdb['PROFILE'] = mdict.get('CALIB_PROFILE', 'MAIN')
    mysql['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['PATH'] = mdict.get('TELLU_PATH', 'NULL')
    telludb['NAME'] = mdict.get('TELLU_NAME', 'NULL')
    telludb['RESET'] = mdict.get('TELLU_RESET', 'reset.tellu.csv')
    telludb['PROFILE'] = mdict.get('TELLU_PROFILE', 'MAIN')
    mysql['TELLU'] = telludb
    # add index database
    findexdb = dict()
    findexdb['PATH'] = mdict.get('FINDEX_PATH', 'NULL')
    findexdb['NAME'] = mdict.get('FINDEX_NAME', 'NULL')
    findexdb['RESET'] = mdict.get('FINDEX_RESET', 'NULL')
    findexdb['PROFILE'] = mdict.get('FINDEX_PROFILE', 'MAIN')
    mysql['FINDEX'] = findexdb
    # add log database
    logdb = dict()
    logdb['PATH'] = mdict.get('LOG_PATH', 'NULL')
    logdb['NAME'] = mdict.get('LOG_NAME', 'NULL')
    logdb['RESET'] = mdict.get('LOG_RESET', 'NULL')
    logdb['PROFILE'] = mdict.get('LOG_PROFILE', 'MAIN')
    mysql['LOG'] = logdb
    # add object database
    astromdb = dict()
    astromdb['PATH'] = mdict.get('ASTROM_PATH', 'NULL')
    astromdb['NAME'] = mdict.get('ASTROM_NAME', 'NULL')
    astromdb['RESET'] = mdict.get('ASTROM_RESET', 'reset.astrom.csv')
    astromdb['PROFILE'] = mdict.get('ASTROM_PROFILE', 'MAIN')
    mysql['ASTROM'] = astromdb
    # add reject database
    rejectdb = dict()
    rejectdb['PATH'] = mdict.get('REJECT_PATH', 'NULL')
    rejectdb['NAME'] = mdict.get('REJECT_NAME', 'NULL')
    rejectdb['RESET'] = mdict.get('REJECT_RESET', 'NULL')
    rejectdb['PROFILE'] = mdict.get('REJECT_PROFILE', 'MAIN')
    mysql['REJECT'] = rejectdb
    # add language database
    langdb = dict()
    langdb['PATH'] = mdict.get('LANG_PATH', 'DRS_DATA_ASSETS')
    langdb['NAME'] = mdict.get('LANG_PATH', 'lang.db')
    langdb['RESET'] = mdict.get('LANG_PATH', 'NULL')
    langdb['PROFILE'] = mdict.get('LANG_PROFILE', 'MAIN')
    mysql['LANG'] = langdb
    # mysql['PARAMS_PATH'] = 'DRS_DATA_ASSETS'
    database_dict['MYSQL'] = mysql
    # write database
    write_yaml(database_dict, str(database_path))


def tqdm_module():
    """
    Get the tqdm module in on or off mode

    :return: function, the tqdm method (or class with a call)
    """
    # this will replace tqdm with the return of the first arg
    def _tqdm(*args, **kwargs):
        _ = kwargs
        return args[0]
    # if we want to use tqdm then use it
    if 'USE_TQDM' in IPARAMS:
        if IPARAMS['USE_TQDM']:
            from tqdm import tqdm as _tqdm

    return _tqdm


# =============================================================================
# Define functions
# =============================================================================
# populate DPARAMS or IPARAMS
# noinspection PyBroadException
try:
    DPARAMS = load_database_yaml()
    IPARAMS = load_install_yaml()
except Exception as _:
    DPARAMS = dict()
    IPARAMS = dict()
# need tqdm
TQDM = tqdm_module()

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
