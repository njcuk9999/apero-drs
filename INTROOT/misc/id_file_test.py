#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-06-12 at 11:56

@author: cook
"""

from __future__ import division

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_preprocess_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------

WS1 = '/scratch/Projects/spirou_py3/data_h4rg/raw/AT5/20180529/'
WS2 = '/scratch/Projects/spirou_py3/data/raw/20170710/'
WS3 = '/scratch/Projects/spirou_py3/data_h4rg/raw/AT5/20180409/'
WS4 = '/scratch/Projects/spirou_py3/data_h4rg/raw/AT5/20180424/'

TEST_FILES = [WS1 + 'dark_dark_001d.fits', WS1 + 'flat_flat_001f.fits',
              WS2 + 'dark_dark02d.fits', WS2 + 'fp_fp02a.fits',
              WS2 + 'flat_flat03f10.fits', WS2 + 'flat_dark02f.fits',
              WS2 + 'dark_flat02f.fits', WS2 + 'hcone_hcone04c61.fits',
              WS3 + 'hcone_dark_001.fits', WS3 + 'flat_dark_001.fits',
              WS3 + 'hctwo_hctwo_001.fits', WS4 + 'Gl410_fp01o.fits',
              WS4 + 'Gl699_fp42o.fits']

P = dict(LOG_OPT='test', DRS_DEBUG=1,
         KW_DPRTYPE=['DPRTYPE', '', ''],
         KW_OBSTYPE=['OBSTYPE', '', ''],
         KW_CCAS=['SBCCAS_P', '', ''],
         KW_CREF=['SBCREF_P', '', ''])

# =============================================================================
# Define functions
# =============================================================================
def identify_raw_file(p, filename, hdr=None, cdr=None):
    return spirouImage.IdentifyUnProFile(p, filename, hdr, cdr)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # test
    for it, test_file in enumerate(TEST_FILES):
        print('\n\n\n {0}: file = {1}'.format(it+1, test_file))
        filename, header, comments = identify_raw_file(P, test_file)

# =============================================================================
# End of code
# =============================================================================
