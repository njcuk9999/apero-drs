#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_SLIT_spirou

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""

from startup import RunInitialStartup, RunStartup
from startup import spirouLog

# =============================================================================
# Define variables
# =============================================================================
WLOG = spirouLog.logger
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
    pp = RunInitialStartup()

    # TODO: add code

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', pp['log_opt'], ('Recipe {0} has been succesfully completed'
                                 '').format(pp['program']))

# =============================================================================
# End of code
# =============================================================================
