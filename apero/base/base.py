#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Some things must be defined once and used throughout the drs
No functions in here please

Created on 2020-08-2020-08-21 19:43

@author: cook

import rules:

- no imports from apero

"""
from astropy.time import Time, TimeDelta
from collections import OrderedDict
import numpy as np
import os
from pathlib import Path
import string
from typing import Any
import warnings
import yaml


# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'apero'
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = 'None'
__version__ = '0.7.142'
__author__ = ['N. Cook', 'E. Artigau', 'F. Bouchy', 'M. Hobson', 'C. Moutou',
              'I. Boisse', 'E. Martioli']
__date__ = '2021-07-05'
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

# Define instruments
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
DATABASE_NAMES = ['calib', 'tellu', 'index', 'log', 'object', 'lang']
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


# =============================================================================
# Define functions
# =============================================================================
def load_database_yaml() -> dict:
    # check for environmental variable
    if USER_ENV in os.environ:
        # get path
        path = os.environ[USER_ENV]
        # add filename
        path = os.path.join(path, DATABASE_YAML)
        # load yaml file
        return load_yaml(path)
    # else raise except (cannot come from database)
    else:
        emsg = 'Core Error: {0} must be set (please run setup script)'
        raise EnvironmentError(emsg.format(USER_ENV))


def load_install_yaml():
    # check for environmental variable
    if USER_ENV in os.environ:
        # get path
        path = os.environ[USER_ENV]
        # add filename
        path = os.path.join(path, INSTALL_YAML)
        # load yaml file
        return load_yaml(path)
    # else raise except (cannot come from database)
    else:
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
    # add database settings
    sqlite3['HOST'] = allparams['SQLITE'].get('HOST', 'NULL')
    sqlite3['USER'] = allparams['SQLITE'].get('USER', 'NULL')
    sqlite3['PASSWD'] = allparams['SQLITE'].get('PASSWD', 'NULL')
    sqlite3['DATABASE'] = allparams['SQLITE'].get('DATABASE', 'NULL')
    # add calib database
    calibdb = dict()
    calibdb['PATH'] = allparams['SQLITE'].get('CALIB_PATH', 'DRS_CALIB_DB')
    calibdb['NAME'] = allparams['SQLITE'].get('CALIB_NAME', 'calib.db')
    calibdb['RESET'] = allparams['SQLITE'].get('CALIB_RESET', 'reset.calib.csv')
    calibdb['PROFILE'] = allparams['SQLITE'].get('CALIB_PROFILE', 'NULL')
    sqlite3['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['PATH'] = allparams['SQLITE'].get('TELLU_PATH', 'DRS_TELLU_DB')
    telludb['NAME'] = allparams['SQLITE'].get('TELLU_NAME', 'tellu.db')
    telludb['RESET'] = allparams['SQLITE'].get('TELLU_RESET', 'NULL')
    telludb['PROFILE'] = allparams['SQLITE'].get('TELLU_PROFILE', 'NULL')
    sqlite3['TELLU'] = telludb
    # add index database
    indexdb = dict()
    indexdb['PATH'] = allparams['SQLITE'].get('IDX_PATH', 'DRS_DATA_ASSETS')
    indexdb['NAME'] = allparams['SQLITE'].get('IDX_NAME', 'index.db')
    indexdb['RESET'] = allparams['SQLITE'].get('IDX_RESET', 'NULL')
    indexdb['PROFILE'] = allparams['SQLITE'].get('IDX_PROFILE', 'NULL')
    sqlite3['INDEX'] = indexdb
    # add log database
    logdb = dict()
    logdb['PATH'] = allparams['SQLITE'].get('LOG_PATH', 'DRS_DATA_ASSETS')
    logdb['NAME'] = allparams['SQLITE'].get('LOG_NAME', 'log.db')
    logdb['RESET'] = allparams['SQLITE'].get('LOG_RESET', 'NULL')
    logdb['PROFILE'] = allparams['SQLITE'].get('LOG_PROFILE', 'NULL')
    sqlite3['LOG'] = logdb
    # add object database
    objectdb = dict()
    objectdb['PATH'] = allparams['SQLITE'].get('OBJ_PATH', 'DRS_DATA_ASSETS')
    objectdb['NAME'] = allparams['SQLITE'].get('OBJ_NAME', 'object.db')
    objectdb['RESET'] = allparams['SQLITE'].get('OBJ_RESET', 'reset.object.csv')
    objectdb['PROFILE'] = allparams['SQLITE'].get('OBJ_PROFILE', 'NULL')
    sqlite3['OBJECT'] = objectdb
    # add language database
    langdb = dict()
    langdb['PATH'] = allparams['SQLITE'].get('LANG_PATH', 'DRS_DATA_ASSETS')
    langdb['NAME'] = allparams['SQLITE'].get('LANG_PATH', 'lang.db')
    langdb['RESET'] = allparams['SQLITE'].get('LANG_PATH', 'NULL')
    langdb['PROFILE'] = allparams['SQLITE'].get('LANG_PROFILE', 'NULL')
    sqlite3['LANG'] = langdb
    # add sqlite database to database_dict
    database_dict['SQLITE3'] = sqlite3
    # -------------------------------------------------------------------------
    #  MYSQL SETTINGS
    # -------------------------------------------------------------------------
    # mysql settings
    database_dict['USE_MYSQL'] = allparams['MYSQL'].get('USE_MYSQL', False)
    mysql = dict()
    # add database settings
    mysql['HOST'] = allparams['MYSQL'].get('HOST', 'localhost')
    mysql['USER'] = allparams['MYSQL'].get('USER', 'None')
    mysql['PASSWD'] = allparams['MYSQL'].get('PASSWD', 'None')
    mysql['DATABASE'] = allparams['MYSQL'].get('DATABASE', 'None')
    # add calib database
    calibdb = dict()
    calibdb['PATH'] = allparams['MYSQL'].get('CALIB_PATH', 'NULL')
    calibdb['NAME'] = allparams['MYSQL'].get('CALIB_NAME', 'NULL')
    calibdb['RESET'] = allparams['MYSQL'].get('CALIB_RESET', 'reset.calib.csv')
    calibdb['PROFILE'] = allparams['MYSQL'].get('CALIB_PROFILE', 'MAIN')
    mysql['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['PATH'] = allparams['MYSQL'].get('TELLU_PATH', 'NULL')
    telludb['NAME'] = allparams['MYSQL'].get('TELLU_NAME', 'NULL')
    telludb['RESET'] = allparams['MYSQL'].get('TELLU_RESET', 'NULL')
    telludb['PROFILE'] = allparams['MYSQL'].get('TELLU_PROFILE', 'MAIN')
    mysql['TELLU'] = telludb
    # add index database
    indexdb = dict()
    indexdb['PATH'] = allparams['MYSQL'].get('IDX_PATH', 'NULL')
    indexdb['NAME'] = allparams['MYSQL'].get('IDX_NAME', 'NULL')
    indexdb['RESET'] = allparams['MYSQL'].get('IDX_RESET', 'NULL')
    indexdb['PROFILE'] = allparams['MYSQL'].get('IDX_PROFILE', 'MAIN')
    mysql['INDEX'] = indexdb
    # add log database
    logdb = dict()
    logdb['PATH'] = allparams['MYSQL'].get('LOG_PATH', 'NULL')
    logdb['NAME'] = allparams['MYSQL'].get('LOG_NAME', 'NULL')
    logdb['RESET'] = allparams['MYSQL'].get('LOG_RESET', 'NULL')
    logdb['PROFILE'] = allparams['MYSQL'].get('LOG_PROFILE', 'MAIN')
    mysql['LOG'] = logdb
    # add object database
    objectdb = dict()
    objectdb['PATH'] = allparams['MYSQL'].get('OBJ_PATH', 'NULL')
    objectdb['NAME'] = allparams['MYSQL'].get('OBJ_NAME', 'NULL')
    objectdb['RESET'] = allparams['MYSQL'].get('OBJ_RESET', 'reset.object.csv')
    objectdb['PROFILE'] = allparams['MYSQL'].get('OBJ_PROFILE', 'MAIN')
    mysql['OBJECT'] = objectdb
    # add language database
    langdb = dict()
    langdb['PATH'] = allparams['MYSQL'].get('LANG_PATH', 'DRS_DATA_ASSETS')
    langdb['NAME'] = allparams['MYSQL'].get('LANG_PATH', 'lang.db')
    langdb['RESET'] = allparams['MYSQL'].get('LANG_PATH', 'NULL')
    langdb['PROFILE'] = allparams['MYSQL'].get('LANG_PROFILE', 'MAIN')
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
