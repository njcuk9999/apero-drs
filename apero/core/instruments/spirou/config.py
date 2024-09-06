"""
Default parameters for SPIROU

Created on 2019-01-17

@author: cook
"""
from apero.base import base
from apero.core.instruments.default import config

# Note: If variables are not showing up MUST CHECK __all__ definition
#       in import * module
__NAME__ = 'config.instruments.spirou.config.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# copy the storage
CDict = config.CDict.copy()

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Instrument Name
CDict.set('INSTRUMENT', value='SPIROU', source=__NAME__, author='NJC')

# Defines the longitude West is negative
CDict.set('OBS_LONG', value=-155.468876, source=__NAME__, author='EA')

#  Defines the latitude North (deg)
CDict.set('OBS_LAT', value=19.825252, source=__NAME__, author='EA')

#  Defines the CFHT altitude (m)
CDict.set('OBS_ALT', value=4204, source=__NAME__, author='EA')

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# PLotting mode (0-3)
DRS_PLOT = CDict.DRS_PLOT.copy(__NAME__)
DRS_PLOT.value = 0

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = CDict.DRS_DEBUG.copy(__NAME__)
DRS_DEBUG.value = 0

# Add snapshot parameter table to reduced outputs
PARAMETER_SNAPSHOT = CDict.PARAMETER_SNAPSHOT.copy(__NAME__)
PARAMETER_SNAPSHOT.value = True

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------
#   Define the root installation directory
DRS_ROOT = CDict.DRS_ROOT.copy(__NAME__)
DRS_ROOT.value = '/drs/spirou/drs/'

#   Define the folder with the raw data files in
DRS_DATA_RAW = CDict.DRS_DATA_RAW.copy(__NAME__)
DRS_DATA_RAW.value = '/drs/spirou/data/raw/'

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = CDict.DRS_DATA_REDUC.copy(__NAME__)
DRS_DATA_REDUC.value = '/drs/spirou/data/reduced'

#   Define the directory that the post processed data should be saved to
DRS_DATA_OUT = CDict.DRS_DATA_OUT.copy(__NAME__)
DRS_DATA_OUT.value = '/drs/spirou/data/out'

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = CDict.DRS_CALIB_DB.copy(__NAME__)
DRS_CALIB_DB.value = '/drs/spirou/data/calibDB'

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = CDict.DRS_TELLU_DB.copy(__NAME__)
DRS_TELLU_DB.value = '/drs/spirou/data/telluDB'

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = CDict.DRS_DATA_MSG.copy(__NAME__)
DRS_DATA_MSG.value = '/drs/spirou/data/msg'

#   Define the working directory
DRS_DATA_WORKING = CDict.DRS_DATA_WORKING.copy(__NAME__)
DRS_DATA_WORKING.value = '/drs/spirou/data/tmp'

#   Define the plotting directory
DRS_DATA_PLOT = CDict.DRS_DATA_PLOT.copy(__NAME__)
DRS_DATA_PLOT.value = '/drs/spirou/data/plot'

#   Define the run directory
DRS_DATA_RUN = CDict.DRS_DATA_RUN.copy(__NAME__)
DRS_DATA_RUN.value = '/drs/spirou/data/run'

#   Define the assets directory
DRS_DATA_ASSETS = CDict.DRS_DATA_ASSETS.copy(__NAME__)
DRS_DATA_ASSETS.value = '/drs/spirou/data/assets'

#   Define the other directory
DRS_DATA_OTHER = CDict.DRS_DATA_OTHER.copy(__NAME__)
DRS_DATA_OTHER.value = '/drs/spirou/data/other'

# Define the lbl directory
LBL_PATH = CDict.LBL_PATH.copy(__NAME__)
LBL_PATH.value = '/drs/spirou/data/lbl'

# =============================================================================
# DATABASE SETTINGS
# =============================================================================
# Define database directory (relative to assets directory)
DATABASE_DIR = CDict.DATABASE_DIR.copy(__NAME__)
DATABASE_DIR.value = 'databases/'

#   Define the match type for calibDB files
#         match = 'older'  only select calibration files that are older in
#                          time than input file (and then base it on which is
#                          closest in time)
#         match = 'newer'  only select calibration files that are newer in
#                          time than input file (and then base it on which is
#                          closest in time)
#         match = 'closest'  calibration file selection based on which is
#                            closest in time to the input file
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
CALIB_DB_MATCH = CDict.CALIB_DB_MATCH.copy(__NAME__)
CALIB_DB_MATCH.value = 'closest'

#   Define the match type for calibDB files
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
TELLU_DB_MATCH = CDict.TELLU_DB_MATCH.copy(__NAME__)
TELLU_DB_MATCH.value = 'closest'

# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
# where the instrument recipes are stored
DRS_INSTRUMENT_RECIPE_PATH = CDict.DRS_INSTRUMENT_RECIPE_PATH.copy(__NAME__)
DRS_INSTRUMENT_RECIPE_PATH.value = './recipes/'

#  where the bad pixel data are stored (within assets directory)
DRS_BADPIX_DATA = CDict.DRS_BADPIX_DATA.copy(__NAME__)
DRS_BADPIX_DATA.value = 'engineering/'

# where the calibration data are stored (within assets directory)
DRS_CALIB_DATA = CDict.DRS_CALIB_DATA.copy(__NAME__)
DRS_CALIB_DATA.value = 'calib/'

# where the wave data are stored (within assets directory)
DRS_WAVE_DATA = CDict.DRS_WAVE_DATA.copy(__NAME__)
DRS_WAVE_DATA.value = 'calib/'

# where the assets directory is (relative to apero module)
# TODO: remove and replace with online link / user link
DRS_RESET_ASSETS_PATH = CDict.DRS_RESET_ASSETS_PATH.copy(__NAME__)
DRS_RESET_ASSETS_PATH.value = './apero-assets/'

# where the checksum and critica data (git managed) are stored
DRS_CRITICAL_DATA_PATH = CDict.DRS_CRITICAL_DATA_PATH.copy(__NAME__)
DRS_CRITICAL_DATA_PATH.value = './data/'

# where the reset data are stored (within assets directory)
# for calibDB (within assets directory)
DRS_RESET_CALIBDB_PATH = CDict.DRS_RESET_CALIBDB_PATH.copy(__NAME__)
DRS_RESET_CALIBDB_PATH.value = 'reset/calibdb/'
# for telluDB (within assets directory)
DRS_RESET_TELLUDB_PATH = CDict.DRS_RESET_TELLUDB_PATH.copy(__NAME__)
DRS_RESET_TELLUDB_PATH.value = 'reset/telludb/'
# for run files (within assets directory)
DRS_RESET_RUN_PATH = CDict.DRS_RESET_RUN_PATH.copy(__NAME__)
DRS_RESET_RUN_PATH.value = 'reset/runs/'


# =============================================================================
#  End of configuration file
# =============================================================================
