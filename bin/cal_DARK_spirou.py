#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DARK_spirou.py [night_directory] [fitsfilename]

Prepares the dark files for SPIRou

Created on 2017-10-11 at 10:45

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""

from startup import RunInitialStartup, RunStartup
from startup import log

# =============================================================================
# Define variables
# =============================================================================
WLOG = log.logger
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
    # run specific start up
    pp = RunStartup(pp, kind='dark', prefixes=['dark_dark'])
    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Dark Measurement
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Identification of bad pixels
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Save dark to calibDB
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', pp['log_opt'], ('Recipe {0} has been succesfully completed'
                                 '').format(pp['program']))

# =============================================================================
# End of code
# =============================================================================
