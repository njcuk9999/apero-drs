#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
unit_test_comp_functions.py

Comparison functions for the unit tests

Created on 2017-12-06 at 14:26

@author: cook
"""

from SpirouDRS import spirouConfig
from . import spirouUnitTests
from . import unit_test
from . import spirouUnitRecipes

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
__all__ = ['GetRuns', 'LogTimings', 'ManageRun', 'UnitLogTitle', 'UnitTest']
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
# unit tests

GetRuns = spirouUnitTests.get_runs

LogTimings = spirouUnitTests.log_timings

ManageRun = spirouUnitTests.manage_run

UnitLogTitle = spirouUnitTests.unit_log_title

UnitTest = unit_test

# =============================================================================
# End of code
# =============================================================================
