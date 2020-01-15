# This is the main config file


# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Plotting mode: 0 = off, 1 = on screen, 2 = save to plotting directory
DRS_PLOT = 1

# Whether to run in interactive mode - False or 0 to be in non-interactive mode
#    (If DRS_INTERACTIVE = 0 and DRS_PLOT = 1, DRS_PLOT forced to 0)
#    Will stop any user input at the end of recipes if set to 0
DRS_INTERACTIVE = 1

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = 0

# Whether to use user config (True or 1 to use)
#      if False (or 0) only uses default configuration files
USER_CONFIG = 1

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------

# DO NOT change in here! Please add DRS_UCONFIG to your environmental settings
# then copy this section to a new config.py at that path

#   Define the DATA directory
TDATA = "/drs/spirou/data/"

#   Define the root installation directory (INTROOT)
DRS_ROOT = '/drs/spirou/drs/misc/INTROOT/'

#   Define the folder with the raw data files in
DRS_DATA_RAW = '/drs/spirou/data/raw'

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = '/drs/spirou/data/reduced'

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = '/drs/spirou/data/calibDB'

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = '/drs/spirou/data/telluDB'

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = '/drs/spirou/data/msg'

#   Define the working directory
DRS_DATA_WORKING = '/drs/spirou/data/tmp'

#   Define the plotting directory
DRS_DATA_PLOT = '/drs/spirou/data/plot'

#   Define the run directory
DRS_DATA_RUN = '/drs/spirou/data/runs'

#   Define the user directory
#        (overwritten by DRS_UCONFIG environmental variable)
#      If only using default config file (i.e this file) comment this line out
# DRS_UCONFIG = '~/spirou_config_H4RG/'

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

#   Theme (DARK or LIGHT)
THEME = 'DARK'

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
