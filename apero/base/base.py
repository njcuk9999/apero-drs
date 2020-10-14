#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Some things must be defined once and used throughout the drs
No functions in here please

Created on 2020-08-2020-08-21 19:43

@author: cook
"""
from astropy.time import Time, TimeDelta
from collections import OrderedDict
import numpy as np
import os
from pathlib import Path
import string
from typing import Any
import yaml


# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'apero'
__INSTRUMENT__ = 'None'
__version__ = '0.7.000'
__author__ = ['N. Cook', 'E. Artigau', 'F. Bouchy', 'M. Hobson', 'C. Moutou',
              'I. Boisse', 'E. Martioli']
__date__ = '2020-08-21'
__release__ = 'alpha pre-release'
# do this once per drs import
# TODO: first time Time.now is done it takes a very long time
__now__ = Time.now()
AstropyTime = Time
AstropyTimeDelta = TimeDelta
# Define simple types allowed for constants
SIMPLE_TYPES = [int, float, str, bool, list]
SIMPLE_STYPES = ['int', 'float', 'str', 'bool', 'list']
# define valid characters
VALID_CHARS = list(string.ascii_letters) + list(string.digits)
VALID_CHARS += list(string.punctuation) + list(string.whitespace)
# Define yaml files
INSTALL_YAML = 'install.yaml'
DATABASE_YAML = 'database.yaml'
USER_ENV = 'DRS_UCONFIG'
# Define relative path to 'const' sub-package
CONST_PATH = './core/instruments/'
CORE_PATH = './core/instruments/default/'
PDB_RC_FILE = './data/core/pdbrc_full'
PDB_RC_FILENAME = '.pdbrc'
LANG_DEFAULT_PATH = './lang/databases/'
LANG_INSTRUMNET_PATH = './lang/databases/'
LANG_BACKUP_PATH = './lang/backup/'
# Define config/constant/keyword scripts to open
SCRIPTS = ['default_config.py', 'default_constants.py', 'default_keywords.py']
USCRIPTS = ['user_config.ini', 'user_constants.ini', 'user_keywords.ini']
PSEUDO_CONST_FILE = 'pseudo_const.py'
PSEUDO_CONST_CLASS = 'PseudoConstants'
# define display strings for types
STRTYPE = OrderedDict()
STRTYPE[int] = 'int'
STRTYPE[float] = 'float'
STRTYPE[str] = 'str'
STRTYPE[complex] = 'complex'
STRTYPE[list] = 'list'
STRTYPE[np.ndarray] = 'np.ndarray'
# define types that we can do min and max on
NUMBER_TYPES = [int, float]
# default language
DEFAULT_LANG = 'ENG'
LANGUAGES = ['ENG', 'FR']
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
    # write database
    write_yaml(install_dict, install_path)
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
    database_dict['USE_SQLITE3'] = True
    sqlite3 = dict()
    # add calib database
    calibdb = dict()
    calibdb['PATH'] = 'DRS_CALIB_DB'
    calibdb['NAME'] = 'calib.db'
    calibdb['RESET'] = 'reset.calib.csv'
    sqlite3['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['PATH'] = 'DRS_TELLU_DB'
    telludb['NAME'] = 'tellu.db'
    telludb['RESET'] = 'None'
    sqlite3['TELLU'] = telludb
    # add index database
    indexdb = dict()
    indexdb['PATH'] = 'DRS_DATA_ASSETS'
    indexdb['NAME'] = 'index.db'
    indexdb['RESET'] = 'None'
    sqlite3['INDEX'] = indexdb
    # add log database
    logdb = dict()
    logdb['PATH'] = 'DRS_DATA_ASSETS'
    logdb['NAME'] = 'log.db'
    logdb['RESET'] = 'None'
    sqlite3['LOG'] = logdb
    # add object database
    objectdb = dict()
    objectdb['PATH'] = 'DRS_DATA_ASSETS'
    objectdb['NAME'] = 'object.db'
    objectdb['RESET'] = 'reset.object.csv'
    sqlite3['OBJECT'] = objectdb
    # add language database
    langdb = dict()
    langdb['PATH'] = 'DRS_DATA_ASSETS'
    langdb['NAME'] = 'lang.db'
    langdb['RESET'] = 'None'
    sqlite3['LANG'] = langdb
    # add sqlite database to database_dict
    database_dict['SQLITE3'] = sqlite3
    # -------------------------------------------------------------------------
    #  MYSQL SETTINGS
    # -------------------------------------------------------------------------
    # mysql settings
    database_dict['USE_MYSQL'] = False
    mysql = dict()
    # add calib database
    calibdb = dict()
    calibdb['PATH'] = 'DRS_CALIB_DB'
    calibdb['NAME'] = 'calib.db'
    calibdb['RESET'] = 'reset.calib.csv'
    mysql['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['PATH'] = 'DRS_TELLU_DB'
    telludb['NAME'] = 'tellu.db'
    telludb['RESET'] = 'None'
    mysql['TELLU'] = telludb
    # add index database
    indexdb = dict()
    indexdb['PATH'] = 'DRS_DATA_ASSETS'
    indexdb['NAME'] = 'index.db'
    indexdb['RESET'] = 'None'
    mysql['INDEX'] = indexdb
    # add log database
    logdb = dict()
    logdb['PATH'] = 'DRS_DATA_ASSETS'
    logdb['NAME'] = 'log.db'
    logdb['RESET'] = 'None'
    mysql['LOG'] = logdb
    # add object database
    objectdb = dict()
    objectdb['PATH'] = 'DRS_DATA_ASSETS'
    objectdb['NAME'] = 'object.db'
    objectdb['RESET'] = 'reset.object.csv'
    mysql['OBJECT'] = objectdb
    # add language database
    langdb = dict()
    langdb['PATH'] = 'DRS_DATA_ASSETS'
    langdb['NAME'] = 'lang.db'
    langdb['RESET'] = 'None'
    mysql['LANG'] = langdb
    # mysql['PARAMS_PATH'] = 'DRS_DATA_ASSETS'
    database_dict['MYSQL'] = mysql
    # write database
    write_yaml(database_dict, database_path)


# =============================================================================
# Define functions
# =============================================================================
DPARAMS = load_database_yaml()
IPARAMS = load_install_yaml()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
