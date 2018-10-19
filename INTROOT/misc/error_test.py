#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-19 at 11:55

@author: cook
"""

from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DARK_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt

# =============================================================================
# Define functions
# =============================================================================
def cause_error():

    emsgs = ['TEST ERROR']
    emsgs.append('Caused by: error_test.cause_error()')
    emsgs.append('Return to Exit')

    WLOG('error', 'TEST', emsgs)
    return 0


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    p = dict(LOG_OPT='ERROR_TEST')
    runn = 'TEST1'
    errors = dict()
    try:
        cause_error()
    except Exception as e:
        wmsgs = ['Run "{0}" had an unexpected error:'.format(runn)]
        for msg in str(e).split('\n'):
            wmsgs.append('\t' + msg)
        WLOG('warning', p['LOG_OPT'], wmsgs)
        errors[runn] = e
    except SystemExit as e:
        wmsgs = ['Run "{0}" had an expected error:'.format(runn)]
        for msg in str(e).split('\n'):
            wmsgs.append('\t' + msg)
        WLOG('warning', p['LOG_OPT'], wmsgs)
        errors[runn] = e


# =============================================================================
# End of code
# =============================================================================
