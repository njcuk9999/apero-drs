#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DRIFT_RAW_spirou.py

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""

from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    pp = spirouStartup.RunInitialStartup()

    # TODO: add code

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', pp['log_opt'], ('Recipe {0} has been succesfully completed'
                                 '').format(pp['program']))

# =============================================================================
# End of code
# =============================================================================
