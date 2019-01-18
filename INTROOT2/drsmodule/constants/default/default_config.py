# This is the main config file
from drsmodule.constants.core import constant_functions


# =============================================================================
# Define variables
# =============================================================================
# all definition
__all__ = ['DRS_PLOT', 'DRS_INTERACTIVE', 'DRS_DEBUG', 'DRS_ROOT',
           'DRS_DATA_RAW', 'DRS_DATA_REDUC', 'DRS_CALIB_DB', 'DRS_TELLU_DB',
           'DRS_DATA_MSG', 'DRS_DATA_WORKING', 'VERSION', 'AUTHORS', 'RELEASE',
           'DATE', 'LANGUAGE', 'INSTRUMENT', 'DRS_PACKAGE', 'DRS_USERENV',
           'DRS_USER_DEFAULT', 'DRS_PRINT_LEVEL', 'DRS_LOG_LEVEL',
           'DRS_COLOURED_LOG', 'DRS_THEME', 'DRS_MAX_IO_DISPLAY_LIMIT',
           'DRS_HEADER', 'DRS_PLOT_FONT_FAMILY', 'DRS_PLOT_FONT_WEIGHT',
           'DRS_PLOT_FONT_SIZE', 'DRS_PLOT_STYLE']

# Constants definition
Const = constant_functions.Const

# =============================================================================
# global settings
# =============================================================================
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

# =============================================================================
# path settings
# =============================================================================
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


# =============================================================================
# =============================================================================
# Internal configuration (These should probably not change per instrument)
# =============================================================================
# =============================================================================

# =============================================================================
# General properites
# =============================================================================
# Version
VERSION = Const('VERSION', value='0.4.016', dtype=str)

# Authors
AUTHORS = Const('AUTHOR',
                value=['N. Cook', 'F. Bouchy', 'E. Artigau', 'M. Hobson',
                       'C. Moutou', 'I. Boisse', 'E. Martioli'],
                dtype=list, dtypei=str)

# Release version
RELEASE = Const('RELEASE', value='alpha pre-release', dtype=str)

# Date
DATE = Const('DATE', value='2019-01-18', dtype=str)

# Language
LANGUAGE = Const('LANGUAGE', value='ENG', dtype=str, options=['ENG'])


# =============================================================================
# Instrument Constants
# =============================================================================
# Instrument Name
INSTRUMENT = Const('INSTRUMENT', value='None', dtype=str,
                   options=['None', 'SPIROU', 'NIRPS'])

# =============================================================================
# DRS SETTINGS
# =============================================================================

#   The top-level package name (i.e. import PACKAGE)
DRS_PACKAGE = Const('DRS_PACKAGE', value='drsmodule', dtype=str)

#   User-config environmental variable
DRS_USERENV = Const('DRS_USERENV', value='DRS_UCONFIG', dtype=str)

#   User-config default location (if environmental variable not set)
#   this is relative to the package level
DRS_USER_DEFAULT = Const('DRS_USER_DEFAULT', value='../config/', dtype=str)


# =============================================================================
# DISPLAY/LOGGING SETTINGS
# =============================================================================
#   Level at which to print, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
DRS_PRINT_LEVEL = Const('DRS_PRINT_LEVEL', value='all', dtype=str,
                    options=['all', 'info', 'warning', 'error'])

#   Level at which to log in log file, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
DRS_LOG_LEVEL = Const('DRS_LOG_LEVEL', value='all', dtype=str,
                  options=['all', 'info', 'warning', 'error'])

#   Coloured logging to standard output (console)
DRS_COLOURED_LOG = Const('DRS_COLOURED_LOG', value=True, dtype=bool)

#   Theme (DARK or LIGHT)
DRS_THEME = Const('DRS_THEME', value='DARK', dtype=str,
                  options=['DARK', 'LIGHT'])

# Maximum display limit for files/directory when argument error raise
DRS_MAX_IO_DISPLAY_LIMIT = Const('DRS_MAX_IO_DISPLAY_LIMIT', value=15,
                                 dtype=int)

# DRS Header string
DRS_HEADER = Const('DRS_HEADER', value=(' ' + '*'*65), dtype=str)

# Defines a master switch, whether to report warnings that are caught in
DRS_LOG_CAUGHT_WARNINGS = Const('DRS_LOG_CAUGHT_WARNINGS',
                                value=True, dtype=bool)

# Defines how python exits, when an exit is required after logging, string
#     input fed into spirouConst.EXIT()
#     if 'sys' exits via sys.exit   - soft exit (ipython Exception)
#     if 'os' exits via os._exit    - hard exit (complete exit)
DRS_LOG_EXIT_TYPE = Const('DRS_LOG_EXIT_TYPE', value='sys', dtype=str,
                          options=['os', 'sys'])

# =============================================================================
# PLOT SETTINGS
# =============================================================================
# Set the default font family for all graphs
#     (i.e. monospace) "None" for not set
DRS_PLOT_FONT_FAMILY = Const('DRS_PLOT_FONT_FAMILY', value='None', dtype=str)

# Set the default font weight for all graphs
#     (i.e. bold/normal) "None" for not set
DRS_PLOT_FONT_WEIGHT = Const('DRS_PLOT_FONT_WEIGHT', value='None', dtype=str)

# Set the default font size for all graphs (-1 for not set)
DRS_PLOT_FONT_SIZE = Const('DRS_PLOT_FONT_SIZE', value=-1, dtype=int)

# Set the default plot style
#     (i.e. seaborn or dark_background) "None" for not set
DRS_PLOT_STYLE = Const('DRS_PLOT_STYLE', value='None', dtype=str)



# =============================================================================
#  End of configuration file
# =============================================================================
