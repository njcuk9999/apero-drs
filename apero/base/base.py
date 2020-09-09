#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Some things must be defined once and used throughout the drs
No functions in here please

Created on 2020-08-2020-08-21 19:43

@author: cook
"""
from astropy.time import Time, TimeDelta
import numpy as np
import string
from collections import OrderedDict

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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
