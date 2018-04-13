# This is the main config file


# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Whether to plot (True or 1 to plot)
DRS_PLOT = 1

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG = 0


# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------

#   Define the DATA directory
# TDATA = “/scratch/Projects/spirou_py3/data/”
TDATA = "/home/mhobson/SPIRou_CFHT_data/"

#   Define the root installation directory (INTROOT)
DRS_ROOT = '/home/mhobson/spirou_py3/branches/melissa/INTROOT/'

#   Define the folder with the raw data files in
DRS_DATA_RAW = '/home/mhobson/SPIRou_CFHT_data/raw'

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = '/home/mhobson/SPIRou_CFHT_data/reduced'

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = '/home/mhobson/SPIRou_CFHT_data/calibDB'

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = '/home/mhobson/SPIRou_CFHT_data/msg'

#   Define the working directory
DRS_DATA_WORKING = '/home/mhobson/SPIRou_CFHT_data/tmp'


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
# Special config file - doesn't exist and not used
SPECIAL_NAME = 'special_config_SPIROU.py'

#   Define the ICDP configuration file
#       (located at DRS_CONFIG or DRS_ROOT/config if DRS_CONFIG not defined)
ICDP_NAME = 'constants_SPIROU.py'


# -----------------------------------------------------------------------------
# Misc/ unneccessary / unsorted
# -----------------------------------------------------------------------------
# Set the log date?
#  value must be "YY-MM-DD" or "None"
# DRS_USED_DATE = None

# -----------------------------------------------------------------------------
#  End of configuration file
# -----------------------------------------------------------------------------
