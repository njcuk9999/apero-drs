"""
Default parameters for instrument

Created on 2019-01-17

@author: cook
"""
from drsmodule.constants.default.default_config import *

# TODO: Note: If variables are not showing up MUST CHECK __all__ definition
# TODO:    in import * module


__NAME__ = 'drsmodule.config.instruments.spirou.default_config'

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



