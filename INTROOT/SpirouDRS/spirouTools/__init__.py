#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-04-05 at 14:36

@author: cook
"""

from SpirouDRS import spirouConfig
from . import drs_tools
from . import drs_reset
from . import drs_dependencies

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
__all__ = ['DisplayCalibDB', 'DRS_Dependencies', 'DRS_Reset',
           'ListRawFiles', 'ListReducedFiles', 'ListCalibFiles']


# =============================================================================
# Define functions
# =============================================================================

DisplayCalibDB = drs_tools.display_calibdb

DRS_Dependencies = drs_dependencies.main

DRS_Reset = drs_reset.main

ListRawFiles = drs_tools.list_raw_files

ListReducedFiles = drs_tools.list_reduced_files

ListCalibFiles = drs_tools.list_calib_files

# =============================================================================
# End of code
# =============================================================================
