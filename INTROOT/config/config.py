# This is the main config file


# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Whether to plot (True or 1 to plot)
DRS_PLOT = 1

# Whether to run in interactive mode - False or 0 to be in non-interactive mode
#    (If 0 DRS_PLOT will be forced to 0)
#    Will stop any user input at the end of recipes if set to 0
DRS_INTERACTIVE = 1

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = 0

# Whether to use user config (True or 1 to use)
#      if False (or 0) only uses default configuration files
USER_CONFIG = 0

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------

#   Define the DATA directory
TDATA = "/Users/edermartioli/SPIROU-pipeline/data/"

#   Define the root installation directory (INTROOT)
DRS_ROOT = '/Users/edermartioli/SpirouDRS/'

#   Define the folder with the raw data files in
DRS_DATA_RAW = '/Users/edermartioli/SPIROU-pipeline/data/raw'

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = '/Users/edermartioli/SPIROU-pipeline/data/reduced'

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = '/Users/edermartioli/SPIROU-pipeline/data/calibDB'

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = '/Users/edermartioli/SPIROU-pipeline/data/msg'

#   Define the working directory
DRS_DATA_WORKING = '/Users/edermartioli/SPIROU-pipeline/data/tmp'

#   Define the user directory
#        (overwritten by DRS_UCONFIG environmental variable)
#      If only using default config file (i.e this file) comment this line out
# DRS_UCONFIG = '~/spirou_config_H2RG/'
DRS_UCONFIG = '~/spirou_config_H4RG/'

# -----------------------------------------------------------------------------
# Logging settings
# -----------------------------------------------------------------------------

#   Level at which to print, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
PRINT_LEVEL = 'all'

#   Level at which to log in log file, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
LOG_LEVEL = 'all'

#   Coloured logging to standard output (console)
COLOURED_LOG = True


# -----------------------------------------------------------------------------
# config file locations
# -----------------------------------------------------------------------------
#       location (in order of priority):
#           DRS_UCONFIG
#           DRS_CONFIG (or DRS_ROOT/config if DRS_CONFIG not defined)

# Special config file - doesn't exist and not used
SPECIAL_NAME = 'special_config_SPIROU.py'

#   Define the ICDP configuration file
ICDP_NAME = 'constants_SPIROU_H4RG.py'


# -----------------------------------------------------------------------------
#  End of configuration file
# -----------------------------------------------------------------------------
