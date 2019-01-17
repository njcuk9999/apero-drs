# This is the main config file
from .._package import package


# -----------------------------------------------------------------------------
# Define variables
# -----------------------------------------------------------------------------
# all definition
__all__ = ['DRS_PLOT', 'DRS_INTERACTIVE', 'DRS_DEBUG', 'DRS_ROOT',
           'DRS_DATA_RAW', 'DRS_DATA_REDUC', 'DRS_CALIB_DB', 'DRS_TELLU_DB',
           'DRS_DATA_MSG', 'DRS_DATA_WORKING', 'PRINT_LEVEL', 'LOG_LEVEL',
           'COLOURED_LOG', 'THEME']
# Constants definition
Const = package.Const


# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Whether to plot (True or 1 to plot)
DRS_PLOT = Const('DRS_PLOT', value=True, dtype=bool)

# Whether to run in interactive mode - False or 0 to be in non-interactive mode
#    (If 0 DRS_PLOT will be forced to 0)
#    Will stop any user input at the end of recipes if set to 0
DRS_INTERACTIVE = Const('DRS_INTERACTIVE', value=True, dtype=bool)

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = Const('DRS_DEBUG', value=0, dtype=int)

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------
#   Define the root installation directory (INTROOT)
DRS_ROOT = Const('DRS_ROOT', dtype=str)

#   Define the folder with the raw data files in
DRS_DATA_RAW = Const('DRS_DATA_RAW', dtype=str)

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = Const('DRS_DATA_REDUC', dtype=str)

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = Const('DRS_CALIB_DB', dtype=str)

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = Const('DRS_TELLU_DB', dtype=str)

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = Const('DRS_DATA_MSG', dtype=str)

#   Define the working directory
DRS_DATA_WORKING = Const('DRS_DATA_WORKING', dtype=str)

# -----------------------------------------------------------------------------
# Logging settings
# -----------------------------------------------------------------------------

#   Level at which to print, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
PRINT_LEVEL = Const('PRINT_LEVEL', value='all', dtype=str,
                    options=['all', 'info', 'warning', 'error'])

#   Level at which to log in log file, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
LOG_LEVEL = Const('LOG_LEVEL', value='all', dtype=str,
                  options=['all', 'info', 'warning', 'error'])

#   Coloured logging to standard output (console)
COLOURED_LOG = Const('COLOURED_LOG', value=True, dtype=bool)

#   Theme (DARK or LIGHT)
THEME = Const('THEME', value='DARK', dtype=str, options=['DARK', 'LIGHT'])

# -----------------------------------------------------------------------------
#  End of configuration file
# -----------------------------------------------------------------------------
