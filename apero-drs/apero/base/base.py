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
import warnings
from pathlib import Path
import yaml

from aperocore.base import base

from importlib.metadata import version

try:
    from apero._version import __date__
except ImportError:
    __date__ = ''

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'apero'
__version__ = version(__PACKAGE__)
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)

# =============================================================================
# Get variables from info.yaml
# =============================================================================
__authors__ = __YAML__['DRS.AUTHORS']
__release__ = __YAML__['DRS.RELEASE']
# do this once per drs import
__now__ = base.Time.now()
AstropyTime = base.Time
AstropyTimeDelta = base.TimeDelta
# List of author names
AUTHORS = base.AUTHORS

# Define yaml files
INSTALL_YAML = 'install.yaml'
DATABASE_YAML = 'database.yaml'
USER_ENV = base.USER_ENV
# switch for no db in args
NO_DB = False
# Define instruments (last one should be 'None')
INSTRUMENTS = __YAML__['DRS.INSTRUMENTS']
# -----------------------------------------------------------------------------
# constants/parameter settings
# -----------------------------------------------------------------------------
CONST_PATH = './core/instruments/'
CORE_PATH = './core/instruments/default/'
PDB_RC_FILE = './data/core/pdbrc_full'
PDB_RC_FILENAME = '.pdbrc'
SCRIPTS = ['default_config.py', 'default_constants.py', 'default_keywords.py']
# USCRIPTS = ['user_config.ini', 'user_constants.ini', 'user_keywords.ini']
PSEUDO_CONST_FILE = 'pseudo_const.py'
PSEUDO_CONST_CLASS = 'PseudoConstants'
DEFAULT_PSEUDO_CONST_CLASS = 'DefaultPseudoConstants'
# absolute paths (from relative paths to here)
REQUIREMENTS = __PATH__.parent.joinpath('requirements.txt')
# data checksum filename
CHECKSUM_FILE = 'checksums.yaml'
# yaml groups
YAML_GROUPS = ['DRS', 'PREPROCESSING', 'CALIBRATION', 'OBJECT', 'DEBUG',
               'TOOLS']
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
# databases
DATABASE_NAMES = ['calib', 'tellu', 'findex', 'log', 'astrom', 'reject']
DATABASE_FULLNAMES = ['calibration', 'telluric', 'file index', 'recipe log',
                      'astrometric', 'rejection']
DATABASE_COL_CLASS = ['CALIBRATION_DB_COLUMNS', 'TELLURIC_DB_COLUMNS',
                      'FILEINDEX_DB_COLUMNS', 'LOG_DB_COLUMNS',
                      'ASTROMETRIC_DB_COLUMNS', 'REJECT_DB_COLUMNS']
# Support database types
SUPPORTED_DATABASES = __YAML__['DB_MODES']
# -----------------------------------------------------------------------------
# language settings
# -----------------------------------------------------------------------------
DEFAULT_LANG = base.DEFAULT_LANG
# supported languages
LANGUAGES = base.LANGUAGES
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
# -----------------------------------------------------------------------------
# Hard coded constants that should not be changed ever
# -----------------------------------------------------------------------------
# Sun's elevation at civil twilight (degrees)
CIVIL_TWILIGHT = __YAML__['CIVIL_TWILIGHT']
# Sun's elevation at nautical twilight (degrees)
NAUTICAL_TWILIGHT = __YAML__['NAUTICAL_TWILIGHT']
# Sun's elevation at astronomical twilight (degrees)
ASTRONOMIAL_TWILIGHT = __YAML__['ASTRONOMIAL_TWILIGHT']
# -----------------------------------------------------------------------------
# Some astrophysical constants
# -----------------------------------------------------------------------------
PHOT_BANDS = dict()
PHOT_BANDS['U'] = [305.511, 403.064]
PHOT_BANDS['G'] = [379.764, 555.304]
PHOT_BANDS['R'] = [541.823, 699.442]
PHOT_BANDS['I'] = [669.241, 840.032]
PHOT_BANDS['Z'] = [796.47, 1087.33]
PHOT_BANDS['Y'] = [938.6, 1113.4]
PHOT_BANDS['J'] = [1153.6, 1354.4]
PHOT_BANDS['H'] = [1462.9, 1808.5]
PHOT_BANDS['K'] = [1957.8, 2343.1]

# =============================================================================
# Define functions
# =============================================================================
# populate DPARAMS or IPARAMS
# noinspection PyBroadException
base.DPARAMS = base.load_database_yaml()
base.IPARAMS = base.load_install_yaml()
# need tqdm
TQDM = base.tqdm_module()

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
