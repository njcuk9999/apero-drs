"""
Default parameters for instrument

Created on 2019-01-17

@author: cook
"""
from terrapipe.constants.default.default_config import *

# TODO: Note: If variables are not showing up MUST CHECK __all__ definition
# TODO:    in import * module


__NAME__ = 'config.instruments.spirou.default_config.py'

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Instrument Name
INSTRUMENT = INSTRUMENT.copy(__NAME__)
INSTRUMENT.value = 'SPIROU'

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Whether to plotting (True or 1 to plotting)
DRS_PLOT = DRS_PLOT.copy(__NAME__)
DRS_PLOT.value = 0

# Whether to run in interactive mode - False or 0 to be in non-interactive mode
#    (If 0 DRS_PLOT will be forced to 0)
#    Will stop any user input at the end of recipes if set to 0
DRS_INTERACTIVE = DRS_INTERACTIVE.copy(__NAME__)
DRS_INTERACTIVE.value = False

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = DRS_DEBUG.copy(__NAME__)
DRS_DEBUG.value = 0

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------
#   Define the root installation directory (INTROOT)
DRS_ROOT = DRS_ROOT.copy(__NAME__)
DRS_ROOT.value = '/drs/spirou/INTROOT/'

#   Define the folder with the raw data files in
DRS_DATA_RAW = DRS_DATA_RAW.copy(__NAME__)
DRS_DATA_RAW.value = '/drs/spirou/data/raw/'

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = DRS_DATA_REDUC.copy(__NAME__)
DRS_DATA_REDUC.value = '/drs/spirou/data/reduced'

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = DRS_CALIB_DB.copy(__NAME__)
DRS_CALIB_DB.value = '/drs/spirou/data/calibDB'

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = DRS_TELLU_DB.copy(__NAME__)
DRS_TELLU_DB.value = '/drs/spirou/data/telluDB'

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = DRS_DATA_MSG.copy(__NAME__)
DRS_DATA_MSG.value = '/drs/spirou/data/msg'

#   Define the working directory
DRS_DATA_WORKING = DRS_DATA_WORKING.copy(__NAME__)
DRS_DATA_WORKING.value = '/drs/spirou/data/tmp'

#   Define the plotting directory
DRS_DATA_PLOT = DRS_DATA_PLOT.copy(__NAME__)
DRS_DATA_PLOT.value = '/drs/spirou/data/plot'


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
TELLU_DB_NAME.value = 'master_tellu_SPIROU.txt'

# the calibration database name
CALIB_DB_NAME = CALIB_DB_NAME.copy(__NAME__)
CALIB_DB_NAME.value = 'master_calib_SPIROU.txt'

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

# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
#  where the bad pixel data are stored
DRS_BADPIX_DATA = DRS_BADPIX_DATA.copy(__NAME__)
DRS_BADPIX_DATA.value = './data/spirou/engineering/'