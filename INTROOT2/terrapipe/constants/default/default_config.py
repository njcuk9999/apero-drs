# This is the main config file
from terrapipe.constants.core import constant_functions


# =============================================================================
# Define variables
# =============================================================================
# all definition
__all__ = ['DRS_PLOT', 'DRS_INTERACTIVE', 'DRS_DEBUG', 'DRS_ROOT',
           'DRS_DATA_RAW', 'DRS_DATA_REDUC', 'DRS_CALIB_DB', 'DRS_TELLU_DB',
           'DRS_DATA_MSG', 'DRS_DATA_WORKING', 'DRS_VERSION', 'AUTHORS',
           'DRS_RELEASE', 'DRS_DATE', 'LANGUAGE', 'INSTRUMENT', 'DRS_PACKAGE',
           'DRS_USERENV', 'DRS_USER_DEFAULT', 'DRS_PRINT_LEVEL',
           'DRS_LOG_LEVEL', 'DRS_COLOURED_LOG', 'DRS_THEME',
           'DRS_MAX_IO_DISPLAY_LIMIT', 'DRS_HEADER', 'DRS_LOG_CAUGHT_WARNINGS',
           'DRS_LOG_EXIT_TYPE', 'DRS_PLOT_FONT_FAMILY', 'DRS_PLOT_FONT_WEIGHT',
           'DRS_PLOT_FONT_SIZE', 'DRS_PLOT_STYLE', 'DRS_DATA_PLOT',
           'DB_MAX_WAIT', 'FITSOPEN_MAX_WAIT', 'TELLU_DB_NAME', 'CALIB_DB_NAME']

# set name
__NAME__ = 'terrapipe.constants.default.default_config'

# Constants definition
Const = constant_functions.Const

# =============================================================================
# global settings
# =============================================================================
# Whether to plotting (True or 1 to plotting)
DRS_PLOT = Const('DRS_PLOT', value=0, dtype=int, source=__NAME__)

# Whether to run in interactive mode - False or 0 to be in non-interactive mode
#    (If 0 DRS_PLOT will be forced to 0)
#    Will stop any user input at the end of recipes if set to 0
DRS_INTERACTIVE = Const('DRS_INTERACTIVE', value=False, dtype=bool,
                        source=__NAME__)

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = Const('DRS_DEBUG', value=0, dtype=int, source=__NAME__)

# =============================================================================
# path settings
# =============================================================================
#   Define the root installation directory (INTROOT)
DRS_ROOT = Const('DRS_ROOT', dtype='path', source=__NAME__)

#   Define the folder with the raw data files in
DRS_DATA_RAW = Const('DRS_DATA_RAW', dtype='path', source=__NAME__)

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = Const('DRS_DATA_REDUC', dtype='path', source=__NAME__)

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = Const('DRS_CALIB_DB', dtype='path', source=__NAME__)

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = Const('DRS_TELLU_DB', dtype='path', source=__NAME__)

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = Const('DRS_DATA_MSG', dtype='path', source=__NAME__)

#   Define the working directory
DRS_DATA_WORKING = Const('DRS_DATA_WORKING', dtype='path', source=__NAME__)

#   Define the plotting directory
DRS_DATA_PLOT = Const('DRS_DATA_PLOT', dtype='path', source=__NAME__)


# =============================================================================
# =============================================================================
# Internal configuration (These should probably not change per instrument)
# =============================================================================
# =============================================================================

# =============================================================================
# General properites
# =============================================================================
# Version
DRS_VERSION = Const('DRS_VERSION', value='0.4.016', dtype=str,
                    source=__NAME__)

# Authors
AUTHORS = Const('AUTHOR',
                value=['N. Cook', 'F. Bouchy', 'E. Artigau', 'M. Hobson',
                       'C. Moutou', 'I. Boisse', 'E. Martioli'],
                dtype=list, dtypei=str, source=__NAME__)

# Release version
DRS_RELEASE = Const('RELEASE', value='alpha pre-release', dtype=str,
                    source=__NAME__)

# Date
DRS_DATE = Const('DATE', value='2019-01-18', dtype=str, source=__NAME__)

# Language
LANGUAGE = Const('LANGUAGE', value='ENG', dtype=str, options=['ENG', 'FR'],
                 source=__NAME__)

# =============================================================================
# Instrument Constants
# =============================================================================
# Instrument Name
INSTRUMENT = Const('INSTRUMENT', value=None, dtype=str,
                   options=['None', 'SPIROU', 'NIRPS'], source=__NAME__)

# =============================================================================
# DRS SETTINGS
# =============================================================================

#   The top-level package name (i.e. import PACKAGE)
DRS_PACKAGE = Const('DRS_PACKAGE', value='terrapipe', dtype=str,
                    source=__NAME__)

#   User-config environmental variable
DRS_USERENV = Const('DRS_USERENV', value='DRS_UCONFIG', dtype=str,
                    source=__NAME__)

# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
#   User-config default location (if environmental variable not set)
#   this is relative to the package level
DRS_USER_DEFAULT = Const('DRS_USER_DEFAULT', value='../config/', dtype=str,
                         source=__NAME__)

#   where to store internal data
DRS_MOD_DATA_PATH = Const('DRS_MOD_DATA_PATH', value='./data/', dtype=str)

#   where instrument configuration files are stored
DRS_MOD_INSTRUMENT_CONFIG = Const('DRS_MOD_INSTRUMENT_CONFIG', dtype=str,
                                  value='./config/instruments/',
                                  source=__NAME__)

#   where the core configuration files are stored
DRS_MOD_CORE_CONFIG = Const('DRS_MOD_CORE_CONFIG', dtype=str,
                            value='./config/core/default',
                            source=__NAME__)

# =============================================================================
# DRS INDEXING SETTINGS
# =============================================================================
# Define the name of the index file (in each working/reduced directory)
DRS_INDEX_FILE = Const('DRS_INDEX_FILE', dtype=str, value='index.fits',
                       source=__NAME__)

# Define the filename column of the index file
DRS_INDEX_FILENAME = Const('DRS_INDEX_FILENAME', dtype=str, value='FILENAME',
                           source=__NAME__)


# =============================================================================
# DATABASE SETTINGS
# =============================================================================
#   the maximum wait time for calibration database file to be in use (locked)
#       after which an error is raised (in seconds)
DB_MAX_WAIT = Const('DB_MAX_WAIT', dtype=int, value=600, minimum=1,
                    source=__NAME__)

# file max wait
FITSOPEN_MAX_WAIT = Const('FITSOPEN_MAX_WAIT', dtype=int, value=600, minimum=1,
                          source=__NAME__)

# the telluric database name
TELLU_DB_NAME = Const('TELLU_DB_NAME', dtype=str, source=__NAME__,
                      value='master_tellu.txt')

# the calibration database name
CALIB_DB_NAME = Const('TELLU_DB_NAME', dtype=str, source=__NAME__,
                      value='master_calib.txt')

# =============================================================================
# DISPLAY/LOGGING SETTINGS
# =============================================================================
#   Level at which to print, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
DRS_PRINT_LEVEL = Const('DRS_PRINT_LEVEL', value='all', dtype=str,
                        options=['all', 'info', 'warning', 'error'],
                        source=__NAME__)

#   Level at which to log in log file, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
DRS_LOG_LEVEL = Const('DRS_LOG_LEVEL', value='all', dtype=str,
                      options=['all', 'info', 'warning', 'error'],
                      source=__NAME__)

#   Coloured logging to standard output (console)
DRS_COLOURED_LOG = Const('DRS_COLOURED_LOG', value=True, dtype=bool,
                         source=__NAME__)

#   Theme (DARK or LIGHT)
DRS_THEME = Const('DRS_THEME', value='DARK', dtype=str,
                  options=['DARK', 'LIGHT'], source=__NAME__)

# Maximum display limit for files/directory when argument error raise
DRS_MAX_IO_DISPLAY_LIMIT = Const('DRS_MAX_IO_DISPLAY_LIMIT', value=15,
                                 dtype=int, source=__NAME__)

# DRS Header string
DRS_HEADER = Const('DRS_HEADER', value=(' ' + '*'*75), dtype=str,
                   source=__NAME__)

# Defines a master switch, whether to report warnings that are caught in
DRS_LOG_CAUGHT_WARNINGS = Const('DRS_LOG_CAUGHT_WARNINGS',
                                value=True, dtype=bool, source=__NAME__)

# Defines how python exits, when an exit is required after logging, string
#     input fed into spirouConst.EXIT()
#     if 'sys' exits via sys.exit   - soft exit (ipython Exception)
#     if 'os' exits via os._exit    - hard exit (complete exit)
DRS_LOG_EXIT_TYPE = Const('DRS_LOG_EXIT_TYPE', value='sys', dtype=str,
                          options=['os', 'sys'], source=__NAME__)

# Defines the DRS log format
DRS_LOG_FORMAT = Const('DRS_LOG_FORMAT', value='{0} - {1} |{2}|{3}',
                       dtype=str, source=__NAME__)

# =============================================================================
# PLOT SETTINGS
# =============================================================================
# Set the default font family for all graphs
#     (i.e. monospace) "None" for not set
DRS_PLOT_FONT_FAMILY = Const('DRS_PLOT_FONT_FAMILY', value='None', dtype=str,
                             source=__NAME__)

# Set the default font weight for all graphs
#     (i.e. bold/normal) "None" for not set
DRS_PLOT_FONT_WEIGHT = Const('DRS_PLOT_FONT_WEIGHT', value='None', dtype=str,
                             source=__NAME__)

# Set the default font size for all graphs (-1 for not set)
DRS_PLOT_FONT_SIZE = Const('DRS_PLOT_FONT_SIZE', value=-1, dtype=int,
                           source=__NAME__)

# Set the default plotting style
#     (i.e. seaborn or dark_background) "None" for not set
DRS_PLOT_STYLE = Const('DRS_PLOT_STYLE', value='None', dtype=str,
                       source=__NAME__)

# =============================================================================
#  End of configuration file
# =============================================================================
