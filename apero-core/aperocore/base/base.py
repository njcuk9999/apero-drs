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
import re
import os
import string
import sys
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq, CommentedSet
from ruamel.yaml.scalarfloat import ScalarFloat
from ruamel.yaml.scalarint import ScalarInt
from ruamel.yaml.scalarbool import ScalarBoolean
from ruamel.yaml.scalarstring import ScalarString

import numpy as np
import yaml
from astropy.time import Time, TimeDelta

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'aperocore'
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)

# =============================================================================
# Get variables from info.yaml
# =============================================================================
__version__ = __YAML__['VERSION']
__authors__ = __YAML__['AUTHORS']
__date__ = __YAML__['DATE']
__release__ = __YAML__['RELEASE']
# do this once per drs import
__now__ = Time.now()
AstropyTime = Time
AstropyTimeDelta = TimeDelta
# List of author names
AUTHORS = dict()
AUTHORS['NJC'] = 'Neil James Cook'
AUTHORS['EA'] = 'Etienne Artigau'
AUTHORS['EM'] = 'Eder Martioli'

# Define yaml files
INSTALL_YAML = 'install.yaml'
DATABASE_YAML = 'database.yaml'
USER_ENV = 'DRS_UCONFIG'
# switch for no db in args
NO_DB = False

# -----------------------------------------------------------------------------
# logging and warnings
# -----------------------------------------------------------------------------
# Make sure default directory exists
DEFAULT_LOG_PATH = str(os.path.expanduser('~/.apero/dlog/'))
# only use this to turn warnings to errors (we need to use this flag to stop
#   some exceptions creating long loops and freezing when all warnings go to
#   errors)
WARN_TO_ERROR = False
# this is how we turn warnings to errors
if WARN_TO_ERROR:
    warnings.filterwarnings('error')
# -----------------------------------------------------------------------------
# language settings
# -----------------------------------------------------------------------------
DEFAULT_LANG = __YAML__['DEFAULT_LANG']
# supported languages
LANGUAGES = __YAML__['LANGUAGES']
# define default language files
DEF_LANG_FILES = ['default_text.py', 'default_help.py']

# TODO: Is the rest of this being used?
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
SIMPLE_TYPES = [int, float, str, bool, list, dict]
SIMPLE_STYPES = ['int', 'float', 'str', 'bool', 'list', 'dict']
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
# Invert STRTYPE
TYPESTR = {v: k for k, v in STRTYPE.items()}
# define types that we can do min and max on
NUMBER_TYPES = [int, float]
# -----------------------------------------------------------------------------
# drs db settings
# -----------------------------------------------------------------------------
DEFAULT_DATABASE_PORT = 3306
DEFAULT_PATH_MAXC = 1024
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


# Default IPARAMS
D_IPARAMS = dict()
D_IPARAMS['DRS_LANG_MODULES'] = __YAML__['LANGUAGE_MODULES']['DEFAULT']
D_IPARAMS[USER_ENV] = None
D_IPARAMS['OBS.INSTRUMENT'] = 'None'
D_IPARAMS['GLOBAL.LANGUAGE'] = 'ENG'
D_IPARAMS['USE_TQDM'] = True


# =============================================================================
# Define functions
# =============================================================================
class BaseAperoError(Exception):
    """
    This error should only be used for errors that are expected and
    give a clear indiciation on what the user should do. No traceback will be
    given to keep it clear and consise.
    """
    def __init__(self, message):
        # remove traceback - we want a clear message to the user
        sys.tracebacklimit = 0
        super().__init__(message)


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
            emsg = '{0}={1} does not exist'
            raise BaseAperoError(emsg.format(USER_ENV, path))
    # else raise except (cannot come from database)
    emsg = ('{0} must be set (please run apero_profile.sh or '
            'apero_profile.bat or add {0} to your PATH)')
    raise BaseAperoError(emsg.format(USER_ENV))


def load_install_yaml(required: bool = True) -> Union[dict, None]:
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
            return load_yaml(path, default=D_IPARAMS)
        else:
            # raise an error
            emsg = '{0}={1} does not exist'
            raise BaseAperoError(emsg.format(USER_ENV, path))
    # try fall back option
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(path, 'data', 'default_install.yaml')
    if os.path.exists(path):
        return load_yaml(path, default=D_IPARAMS)
    elif required:
        # raise an error
        emsg = 'Default install.py={0} does not exist. Please run APERO setup.'
        raise BaseAperoError(emsg.format(path))

    if required:
        # else raise except (cannot come from database)
        emsg = ('{0} must be set (please run setup script or add {0} '
                'to your PATH)')
        raise BaseAperoError(emsg.format(USER_ENV))
    else:
        return D_IPARAMS


def to_plain_data(obj):
    """Recursively convert ruamel.yaml data structures to plain Python types."""
    # --- container types ---
    if isinstance(obj, CommentedMap):
        # stays as dict (or OrderedDict)
        return {k: to_plain_data(v) for k, v in obj.items()}

    elif isinstance(obj, CommentedSeq):
        # stays as list
        return [to_plain_data(v) for v in obj]

    elif isinstance(obj, CommentedSet):
        # YAML set syntax
        return set(to_plain_data(k) for k in obj)
    # --- scalar wrapper types ---
    elif isinstance(obj, (ScalarString,)):
        return str(obj)
    elif isinstance(obj, (ScalarFloat,)):
        return float(obj)
    elif isinstance(obj, (ScalarInt,)):
        return int(obj)
    elif isinstance(obj, (ScalarBoolean,)):
        return bool(obj)
    # --- already a native Python type ---
    else:
        return obj


def load_yaml(filename: str, default: Optional[Dict[str, Any]] = None) -> dict:
    """
    Load a yaml file as a dictionary

    :param filename: str, the filename (absolute path) of the yaml file

    :returns: dictionary dict, the dictionary loaded from yaml file
    """
    # initialize YAML object
    yaml_inst = YAML(typ='rt')
    enable_scientific_floats(yaml_inst)
    #open filename
    with open(filename, 'r') as yfile:
        dictionary = yaml_inst.load(yfile)
    # fill in any missing with default (in case of missing keys)
    if default is not None:
        for key in default:
            if key not in dictionary:
                dictionary[key] = default[key]
    # return the dictionary
    return to_plain_data(dictionary)


def enable_scientific_floats(yaml: YAML) -> None:
    """
    Enable parsing of scientific notation floats (e.g. 1.23e6)
    for a ruamel.yaml YAML(typ='rt') instance.
    """
    float_re = re.compile(
        r'''^(?:[-+]?(?:[0-9][0-9_]*)?\.[0-9_]*   # 1.23
             (?:[eE][-+]?[0-9]+)?                 # 1.23e10
           | [-+]?[0-9][0-9_]*(?:[eE][-+]?[0-9]+) # 1e6
           | \.inf | \.Inf | \.INF
           | \.nan | \.NaN | \.NAN)$''', re.X
    )

    yaml.Resolver.add_implicit_resolver(
        'tag:yaml.org,2002:float',
        float_re,
        list('-+0123456789.')
    )


def write_yaml(dictionary: dict, filename: str,
               width: float = None):
    """
    Write a yaml file from a dictionary

    :param dictionary: dict, the dictionary to write
    :param filename: str, the filename (absolute path) of the yaml file

    :return: None - writes yaml file 'filename'
    """
    # save file
    with open(filename, 'w') as yfile:
        yaml.dump(dictionary, yfile, width=width)


def tqdm_module(use: bool = True):
    """
    Get the tqdm module in on or off mode

    :return: function, the tqdm method (or class with a call)
    """
    # this will replace tqdm with the return of the first arg
    def _tqdm(*args, **kwargs):
        _ = kwargs
        return args[0]
    # if we want to use tqdm then use it
    if 'USE_TQDM' in IPARAMS and use:
        if IPARAMS['USE_TQDM']:
            from tqdm import tqdm as _tqdm
    elif 'USE_TQDM' in __YAML__:
        if __YAML__['USE_TQDM']:
            from tqdm import tqdm as _tqdm

    return _tqdm


def get_default_log_dir() -> str:
    """
    Get the log directory when no parameters are given
    """
    default_path = DEFAULT_LOG_PATH
    # make sure the default log path exists
    if not os.path.exists(default_path):
        os.makedirs(default_path)
    # get date now
    datestr = Time.now().fits.split('T')[0]
    # return the log file
    return str(os.path.join(default_path, datestr))


# =============================================================================
# Define functions
# =============================================================================
# populate DPARAMS or IPARAMS
# noinspection PyBroadException
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
