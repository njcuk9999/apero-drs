# This is the main config file
from terrapipe.core.constants import constant_functions

# =============================================================================
# Define variables
# =============================================================================
# all definition
__all__ = [# global settings
           'DRS_PLOT', 'DRS_INTERACTIVE', 'DRS_DEBUG',
           # path settings
           'DRS_ROOT', 'DRS_DATA_RAW', 'DRS_DATA_REDUC', 'DRS_CALIB_DB',
           'DRS_TELLU_DB', 'DRS_DATA_MSG', 'DRS_DATA_WORKING', 'DRS_DATA_RUN',
           # General properites
           'DRS_VERSION', 'AUTHORS', 'DRS_RELEASE', 'DRS_DATE', 'LANGUAGE',
           # Instrument/Observatory Constants
           'INSTRUMENT', 'OBS_LONG', 'OBS_LAT', 'OBS_ALT',
           # DRS SETTINGS
           'DRS_PACKAGE', 'DRS_USERENV',
           # DRS INTERNAL PATHS
           'DRS_USER_DEFAULT', 'DRS_MOD_DATA_PATH', 'DRS_MOD_INSTRUMENT_CONFIG',
           'DRS_MOD_CORE_CONFIG', 'DRS_WAVE_DATA',
           'DRS_INSTRUMENT_RECIPE_PATH', 'DRS_DEFAULT_RECIPE_PATH',
           'DRS_BADPIX_DATA', 'DRS_CALIB_DATA', 'DRS_RESET_CALIBDB_PATH',
           'DRS_RESET_TELLUDB_PATH', 'DRS_USER_PROGRAM', 'DRS_INDEX_FILE',
           'DRS_PDB_RC_FILE', 'IPYTHON_RETURN',
           # DRS INDEXING SETTINGS
           'DRS_INDEX_FILE', 'DRS_INDEX_FILENAME',
           # DATABASE SETTINGS
           'DB_MAX_WAIT', 'LOCKOPEN_MAX_WAIT', 'TELLU_DB_NAME', 'CALIB_DB_NAME',
           'CALIB_DB_MATCH',
           # DISPLAY/LOGGING SETTINGS
           'DRS_PRINT_LEVEL', 'DRS_LOG_LEVEL', 'DRS_COLOURED_LOG', 'DRS_THEME',
           'DRS_MAX_IO_DISPLAY_LIMIT', 'DRS_HEADER', 'DRS_LOG_CAUGHT_WARNINGS',
           'DRS_LOG_EXIT_TYPE', 'DRS_LOG_FORMAT',
           # PLOT SETTINGS
           'DRS_PLOT_FONT_FAMILY', 'DRS_PLOT_FONT_WEIGHT',
           'DRS_PLOT_FONT_SIZE', 'DRS_PLOT_STYLE', 'DRS_DATA_PLOT',
            # debug settings
            'DEBUG_MODE_LOG_PRINT', 'DEBUG_MODE_TEXTNAME_PRINT',
            'DEBUG_MODE_FUNC_PRINT',
            ]

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

#   Define the run directory
DRS_DATA_RUN = Const('DRS_DATA_RUN', dtype='path', source=__NAME__)


# =============================================================================
# =============================================================================
# Internal configuration (These should probably not change per instrument)
# =============================================================================
# =============================================================================

# =============================================================================
# General properites
# =============================================================================
# Version
DRS_VERSION = Const('DRS_VERSION', value='0.5.079', dtype=str,
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
DRS_DATE = Const('DATE', value='2019-09-26', dtype=str, source=__NAME__)

# Language
LANGUAGE = Const('LANGUAGE', value='ENG', dtype=str, options=['ENG', 'FR'],
                 source=__NAME__)

# =============================================================================
# Instrument/Observatory Constants
# =============================================================================
# Instrument Name
INSTRUMENT = Const('INSTRUMENT', value=None, dtype=str,
                   options=['None', 'SPIROU', 'NIRPS'], source=__NAME__)

# Defines the longitude West is negative
OBS_LONG = Const('OBS_LONG', value=None, dtype=float, source=__NAME__)
#  Defines the latitude North (deg)
OBS_LAT = Const('OBS_LAT', value=None, dtype=float, source=__NAME__)
#  Defines the CFHT altitude (m)
OBS_ALT = Const('OBS_LAT', value=None, dtype=float, source=__NAME__)

# =============================================================================
# DRS SETTINGS
# =============================================================================

#   The top-level package name (i.e. import PACKAGE)
DRS_PACKAGE = Const('DRS_PACKAGE', value='terrapipe', dtype=str,
                    source=__NAME__)

#   User-config environmental variable
DRS_USERENV = Const('DRS_USERENV', value='DRS_UCONFIG', dtype=str,
                    source=__NAME__)

#   User-defined program name (overwrite logging program)
DRS_USER_PROGRAM = Const('DRS_USER_PROGRAM', value=None, dtype=str,
                         source=__NAME__)


# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
#   User-config default location (if environmental variable not set)
#   this is relative to the package level
DRS_USER_DEFAULT = Const('DRS_USER_DEFAULT', value='../config/', dtype=str,
                         source=__NAME__)

#   where to store internal data
DRS_MOD_DATA_PATH = Const('DRS_MOD_DATA_PATH', value='./data/', dtype=str,
                          source=__NAME__)

#   where instrument configuration files are stored
DRS_MOD_INSTRUMENT_CONFIG = Const('DRS_MOD_INSTRUMENT_CONFIG', dtype=str,
                                  value='./core/instruments/',
                                  source=__NAME__)

#   where the core configuration files are stored
DRS_MOD_CORE_CONFIG = Const('DRS_MOD_CORE_CONFIG', dtype=str,
                            value='./core/instruments/default',
                            source=__NAME__)

# where the instrument recipes are stored
DRS_INSTRUMENT_RECIPE_PATH = Const('DRS_INSTRUMENT_RECIPE_PATH', dtype=str,
                                   value=None, source=__NAME__)

# where the default recipes are stored
DRS_DEFAULT_RECIPE_PATH = Const('DRS_DEFAULT_RECIPE_PATH', dtype=str,
                                value='./recipes/', source=__NAME__)

#  where the bad pixel data are stored
DRS_BADPIX_DATA = Const('DRS_BADPIX_DATA', dtype=str, source=__NAME__)

# where the calibration data are stored
DRS_CALIB_DATA = Const('DRS_CALIB_DATA', dtype=str, source=__NAME__)

# where the wave data are stored
DRS_WAVE_DATA = Const('DRS_WAVE_DATA', dtype=str, source=__NAME__)

# where the reset data are stored
DRS_RESET_CALIBDB_PATH = Const('DRS_RESET_CALIBDB_PATH', dtype=str,
                               source=__NAME__)
DRS_RESET_TELLUDB_PATH = Const('DRS_RESET_TELLUDB_PATH', dtype=str,
                               source=__NAME__)

# where the pdb rc file is
DRS_PDB_RC_FILE = Const('DRS_PDB_RC_FILE', value='./data/core/.pdbrc',
                        dtype=str, source=__NAME__)
# whether to be in ipython return mode (always exits to ipdb via pdbrc)
IPYTHON_RETURN = Const('IPYTHON_RETURN', value=False, dtype=bool,
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
LOCKOPEN_MAX_WAIT = Const('LOCKOPEN_MAX_WAIT', dtype=int, value=600, minimum=1,
                          source=__NAME__)

# the telluric database name
TELLU_DB_NAME = Const('TELLU_DB_NAME', dtype=str, source=__NAME__,
                      value='master_tellu.txt')

# the calibration database name
CALIB_DB_NAME = Const('TELLU_DB_NAME', dtype=str, source=__NAME__,
                      value='master_calib.txt')

#   Define the match type for calibDB files
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
CALIB_DB_MATCH = Const('CALIB_DB_MATCH', dtype=str, source=__NAME__,
                       value='closest')

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
# DEBUG MODES
# =============================================================================
# The debug number to print debug log messages
DEBUG_MODE_LOG_PRINT = Const('DEBUG_MODE_LOG_PRINT', value=1, dtype=int,
                             source=__NAME__)

# The debug number to print text entry names on all messages
DEBUG_MODE_TEXTNAME_PRINT = Const('DEBUG_MODE_TEXTNAME_PRINT', value=100,
                                  dtype=int, source=__NAME__)

# The debug number to print function definitions
DEBUG_MODE_FUNC_PRINT = Const('DEBUG_MODE_FUNC_PRINT', value=200, dtype=int,
                              source=__NAME__)


# =============================================================================
#  End of configuration file
# =============================================================================
