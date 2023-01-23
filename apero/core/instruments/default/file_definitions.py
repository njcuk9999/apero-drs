#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO DrsFile definitions for NO INSTRUMENT

# For fits files

file_name = drs_finput(name, filetype, suffix=, outclass, instrument,
                       description)

Created on 2018-10-31 at 18:06

@author: cook
"""
from apero.base import base
from apero.core.core import drs_file
from apero.core.core import drs_out_file as out

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
# define out file classes
blank_ofile = out.BlankOutFile()
general_ofile = out.GeneralOutFile()
debug_ofile = out.DebugOutFile()
set_ofile = out.SetOutFile()
post_ofile = out.PostOutFile()
calib_ofile = out.CalibOutFile()
mcalib_ofile = out.RefCalibOutFile()
tellu_ofile = out.TelluOutFile()
mtellu_ofile = out.RefTelluOutFile()

# =============================================================================
# Raw Files
# =============================================================================
# generic raw file
raw_file = drs_finput('DRS_RAW', filetype='.fits', suffix='',
                      outclass=blank_ofile,
                      description='Generic raw file')

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', filetype='.fits', suffix='_pp',
                     outclass=general_ofile, intype=raw_file,
                     description='Generic pre-processed file')

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
red_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                      intype=pp_file, outclass=blank_ofile,
                      description='Generic reduced file')
# calib out file
calib_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file, outclass=blank_ofile,
                        description='Generic calibration file')
# telluric out file
tellu_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file, outclass=blank_ofile,
                        description='Generic telluric file')

# =============================================================================
# Post processed Files
# =============================================================================
# generic post processed file
post_file = drs_oinput('DRS_POST', filetype='.fits', suffix='',
                       outclass=post_ofile,
                       description='Generic post process file')

# =============================================================================
# End of code
# =============================================================================
