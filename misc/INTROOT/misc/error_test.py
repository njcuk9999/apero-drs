#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-19 at 11:55

@author: cook
"""

from __future__ import division

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore


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
def cause_error(p):

    emsgs = ['TEST ERROR', 'Caused by: error_test.cause_error()',
             'Return to Exit']

    WLOG(p, 'error', emsgs)
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
        cause_error(p)
    except Exception as e:
        wmsgs = ['Run "{0}" had an unexpected error:'.format(runn)]
        for msg in str(e).split('\n'):
            wmsgs.append('\t' + msg)
        WLOG(p, 'warning', wmsgs)
        errors[runn] = str(e)
    except SystemExit as e:
        wmsgs = ['Run "{0}" had an expected error:'.format(runn)]
        for msg in str(e).split('\n'):
            wmsgs.append('\t' + msg)
        WLOG(p, 'warning', wmsgs)
        errors[runn] = str(e)


# =============================================================================
# End of code
# =============================================================================
