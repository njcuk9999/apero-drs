#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-12-06 at 14:26

@author: cook



Version 0.0.0
"""

from SpirouDRS import spirouConfig
from . import unit_test_functions as utf

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouUnitTests.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = []
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
UNIT_TEST_CAL_BADPIX = utf.UNIT_TEST_CAL_BADPIX

UNIT_TEST_CAL_DARK = utf.UNIT_TEST_CAL_DARK

UNIT_TEST_CAL_LOC_RAW = utf.UNIT_TEST_CAL_LOC_RAW

UNIT_TEST_CAL_SLIT = utf.UNIT_TEST_CAL_SLIT

UNIT_TEST_CAL_FF_RAW = utf.UNIT_TEST_CAL_FF_RAW

UNIT_TEST_CAL_EXTRACT = utf.UNIT_TEST_CAL_EXTRACT

UNIT_TEST_CAL_DRIFT_RAW = utf.UNIT_TEST_CAL_DRIFT_RAW

UNIT_TEST_CAL_DRIFT_E2DS = utf.UNIT_TEST_CAL_DRIFT_E2DS

UNIT_TEST_CAL_DRIFTPEAK_E2DS = utf.UNIT_TEST_CAL_DRIFTPEAK_E2DS

UNIT_TEST_CAL_CCF_E2DS = utf.UNIT_TEST_CAL_CCF_E2DS


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
