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
DRS_DEBUG = 42

# Whether to use user config (True or 1 to use)
#      if False (or 0) only uses default configuration files
USER_CONFIG = 1

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------

# DO NOT change in here! Please add DRS_UCONFIG to your environmental settings
# then copy this section to a new config.py at that path

#   Define the DATA directory
TDATA = "/home/data/CFHT/"

#   Define the root installation directory (INTROOT)
DRS_ROOT = '/home/mhobson/spirou_py3/INTROOT/'

#   Define the folder with the raw data files in
DRS_DATA_RAW = '/home/data/CFHT/raw'

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = '/home/data/CFHT/reduced'

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = '/home/data/CFHT/calibDB'

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = '/drs/spirou/data/telluDB'

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = '/home/data/CFHT/msg'

#   Define the working directory
DRS_DATA_WORKING = '/home/data/CFHT/tmp'

#   Define the user directory
#        (overwritten by DRS_UCONFIG environmental variable)
#      If only using default config file (i.e this file) comment this line out
# DRS_UCONFIG = '/home/mhobson/spirou_py3/INTROOT/config'
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
