"""
Default parameters for instrument

Created on 2019-01-17

@author: cook
"""
from ..core.default_config import *


# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Whether to plot (True or 1 to plot)
DRS_PLOT.value = False

# Whether to run in interactive mode - False or 0 to be in non-interactive mode
#    (If 0 DRS_PLOT will be forced to 0)
#    Will stop any user input at the end of recipes if set to 0
DRS_INTERACTIVE.value = False

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
DRS_DEBUG.value = False

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------
#   Define the root installation directory (INTROOT)
DRS_ROOT.value = '/drs/spirou/INTROOT/'

#   Define the folder with the raw data files in
DRS_DATA_RAW.value = '/drs/spirou/data/raw/'





