#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou Files

# For fits files

file_name = drs_finput("name", KW_KEY1="value1", KW_KEY2="value2",
                       ext=".fits", filename=)


Created on 2018-10-31 at 18:06

@author: cook
"""
from terrapipe.core import constants
from terrapipe.core.core import drs_file

from . import output_filenames as out

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.core.default.file_definitions.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']

# =============================================================================
# Define Files
# =============================================================================
drs_input = drs_file.DrsInputFile
drs_finput = drs_file.DrsFitsFile

# =============================================================================
# Raw Files
# =============================================================================
# generic raw file
raw_file = drs_finput('DRS_RAW', ext='.fits')

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', ext='pp.fits')

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
out_file = drs_finput('DRS_OUTPUT')


# =============================================================================
# Debug Files
# =============================================================================
debug_back = drs_finput('DEBUG_BACK', KW_OUTPUT='DEBUG_BACK',
                        ext='background.fits', outfunc=out.debug_file)


# =============================================================================
# End of code
# =============================================================================
