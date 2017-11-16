#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_extract_RAW_spirou

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""


from SpirouDRS import spirouCore
from SpirouDRS import spirouImage

# =============================================================================
# Define variables
# =============================================================================
WLOG = spirouCore.wlog

__NAME__ = 'cal_extract_RAW_spirou.py'
# -----------------------------------------------------------------------------
# Remove this for final (only for testing)
import sys
if len(sys.argv) == 1:
    sys.argv = ['test: ' + __NAME__, '20170710', 'hcone_dark02c61.fits',
                'hcone_dark03c61.fits', 'hcone_dark04c61.fits',
                'hcone_dark05c61.fits', 'hcone_dark06c61.fits']

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
    p = spirouCore.RunInitialStartup()
    # run specific start up
    p = spirouCore.RunStartup(p, kind='Flat-field', calibdb=True)
    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/__main__')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    fib_typ = ['AB', 'A', 'B', 'C']
    p['fib_type'] = ['AB']
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                '').format(p['program']))

# =============================================================================
# End of code
# =============================================================================
