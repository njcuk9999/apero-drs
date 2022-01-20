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
from apero.base import base
from apero.core.core import drs_file
from apero.core.instruments.default import output_filenames as out

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.core.default.file_definitions.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__

# =============================================================================
# Define Files
# =============================================================================
drs_input = drs_file.DrsInputFile
drs_finput = drs_file.DrsFitsFile
drs_oinput = drs_file.DrsOutFile

# =============================================================================
# Raw Files
# =============================================================================
# generic raw file
raw_file = drs_finput('DRS_RAW', filetype='.fits', suffix='',
                      outfunc=out.blank)

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', filetype='.fits', suffix='_pp',
                     outfunc=out.general_file, intype=raw_file)

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
red_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                      intype=pp_file)
# calib out file
calib_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file)
# telluric out file
tellu_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file)

# =============================================================================
# Post processed Files
# =============================================================================
# generic post processed file
post_file = drs_oinput('DRS_POST', filetype='.fits', suffix='',
                       outfunc=out.post_file)

# =============================================================================
# End of code
# =============================================================================
