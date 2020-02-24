"""
Default parameters for instrument

Created on 2019-01-17

@author: cook
"""
from apero.core.instruments.default.default_config import *

# Note: If variables are not showing up MUST CHECK __all__ definition
#       in import * module
__NAME__ = 'config.instruments.nirps_ha.default_config.py'

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Instrument Name
INSTRUMENT = INSTRUMENT.copy(__NAME__)
INSTRUMENT.value = 'NIRPS_HA'

# Defines the longitude West is negative
OBS_LONG = OBS_LONG.copy(__NAME__)
OBS_LONG.value = -29.261165622

#  Defines the latitude North (deg)
OBS_LAT = OBS_LAT.copy(__NAME__)
OBS_LAT.value = -70.731330408

#  Defines the CFHT altitude (m)
OBS_ALT = OBS_ALT.copy(__NAME__)
OBS_ALT.value = 2400

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Whether to plotting (True or 1 to plotting)
DRS_PLOT = DRS_PLOT.copy(__NAME__)
DRS_PLOT.value = 0

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = DRS_DEBUG.copy(__NAME__)
DRS_DEBUG.value = 0

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------
#   Define the root installation directory
DRS_ROOT = DRS_ROOT.copy(__NAME__)
DRS_ROOT.value = '/drs/nirps_ha/drs/'

#   Define the folder with the raw data files in
DRS_DATA_RAW = DRS_DATA_RAW.copy(__NAME__)
DRS_DATA_RAW.value = '/drs/nirps_ha/data/raw/'

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = DRS_DATA_REDUC.copy(__NAME__)
DRS_DATA_REDUC.value = '/drs/nirps_ha/data/reduced'

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = DRS_CALIB_DB.copy(__NAME__)
DRS_CALIB_DB.value = '/drs/nirps_ha/data/calibDB'

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = DRS_TELLU_DB.copy(__NAME__)
DRS_TELLU_DB.value = '/drs/nirps_ha/data/telluDB'

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = DRS_DATA_MSG.copy(__NAME__)
DRS_DATA_MSG.value = '/drs/nirps_ha/data/msg'

#   Define the working directory
DRS_DATA_WORKING = DRS_DATA_WORKING.copy(__NAME__)
DRS_DATA_WORKING.value = '/drs/nirps_ha/data/tmp'

#   Define the plotting directory
DRS_DATA_PLOT = DRS_DATA_PLOT.copy(__NAME__)
DRS_DATA_PLOT.value = '/drs/nirps_ha/data/plot'

#   Define the run directory
DRS_DATA_RUN = DRS_DATA_RUN.copy(__NAME__)
DRS_DATA_RUN.value = '/drs/nirps_ha/data/run'

#   Define ds9 path (optional)
DRS_DS9_PATH = DRS_DS9_PATH.copy(__NAME__)
DRS_DS9_PATH.value = '/usr/bin/ds9'

#   Define latex path (optional)
DRS_PDFLATEX_PATH = DRS_PDFLATEX_PATH.copy(__NAME__)
DRS_PDFLATEX_PATH.value = '/usr/bin/pdflatex'


# =============================================================================
# DATABASE SETTINGS
# =============================================================================
#   the maximum wait time for calibration database file to be in use (locked)
#       after which an error is raised (in seconds)
DB_MAX_WAIT = DB_MAX_WAIT.copy(__NAME__)
DB_MAX_WAIT.value = 600

# file max wait
LOCKOPEN_MAX_WAIT = LOCKOPEN_MAX_WAIT.copy(__NAME__)
LOCKOPEN_MAX_WAIT.value = 600

# the telluric database name
TELLU_DB_NAME = TELLU_DB_NAME.copy(__NAME__)
TELLU_DB_NAME.value = 'master_tellu_NIRPS_HA.txt'

# the calibration database name
CALIB_DB_NAME = CALIB_DB_NAME.copy(__NAME__)
CALIB_DB_NAME.value = 'master_calib_NIRPS_HA.txt'

#   Define the match type for calibDB files
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
CALIB_DB_MATCH = CALIB_DB_MATCH.copy(__NAME__)
CALIB_DB_MATCH.value = 'closest'

# define the calibration database columns
CALIB_DB_COLS = CALIB_DB_COLS.copy(__NAME__)
CALIB_DB_COLS.value = 'key, nightname, filename, humantime, unixtime'
# define the calibration database key column
CALIB_DB_KEY_COL = CALIB_DB_KEY_COL.copy(__NAME__)
CALIB_DB_KEY_COL.value = 'key'
# define the calibration database time column
CALIB_DB_TIME_COL = CALIB_DB_TIME_COL.copy(__NAME__)
CALIB_DB_TIME_COL.value = 'unixtime'
# define the calibration database filename column
CALIB_DB_FILE_COL = CALIB_DB_FILE_COL.copy(__NAME__)
CALIB_DB_FILE_COL.value = 'filename'

# define the telluric database columns (must contain "key")
TELLU_DB_COLS = TELLU_DB_COLS.copy(__NAME__)
TELLU_DB_COLS.value = 'key, nightname, filename, humantime, unixtime, objname'
# define the telluric database key column
TELLU_DB_KEY_COL = TELLU_DB_KEY_COL.copy(__NAME__)
TELLU_DB_KEY_COL.value = 'key'
# define the telluric database time column
TELLU_DB_TIME_COL = TELLU_DB_TIME_COL.copy(__NAME__)
TELLU_DB_TIME_COL.value = 'unixtime'
# define the telluric database filename column
TELLU_DB_FILE_COL = TELLU_DB_FILE_COL.copy(__NAME__)
TELLU_DB_FILE_COL.value = 'filename'


# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
# where the instrument recipes are stored
DRS_INSTRUMENT_RECIPE_PATH = DRS_INSTRUMENT_RECIPE_PATH.copy(__NAME__)
DRS_INSTRUMENT_RECIPE_PATH.value = './recipes/'

#  where the bad pixel data are stored
DRS_BADPIX_DATA = DRS_BADPIX_DATA.copy(__NAME__)
DRS_BADPIX_DATA.value = './data/nirps_ha/engineering/'

# where the calibration data are stored
DRS_CALIB_DATA = DRS_CALIB_DATA.copy(__NAME__)
DRS_CALIB_DATA.value = './data/nirps_ha/calib/'

# where the wave data are stored
DRS_WAVE_DATA = DRS_WAVE_DATA.copy(__NAME__)
DRS_WAVE_DATA.value = './data/nirps_ha/calib/'

# where the reset data are stored
# for calibDB
DRS_RESET_CALIBDB_PATH = DRS_RESET_CALIBDB_PATH.copy(__NAME__)
DRS_RESET_CALIBDB_PATH.value = './data/nirps_ha/reset/calibdb/'
# for telluDB
DRS_RESET_TELLUDB_PATH = DRS_RESET_TELLUDB_PATH.copy(__NAME__)
DRS_RESET_TELLUDB_PATH.value = './data/nirps_ha/reset/telludb/'
# for run files
DRS_RESET_RUN_PATH = DRS_RESET_RUN_PATH.copy(__NAME__)
DRS_RESET_RUN_PATH.value = './data/nirps_ha/reset/runs/'


# =============================================================================
#  End of configuration file
# =============================================================================