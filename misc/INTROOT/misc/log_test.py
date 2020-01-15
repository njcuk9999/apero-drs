#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-12-18 at 14:30

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_CCF_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


def test_log(p, levels):

    # display title
    spirouStartup.spirouStartup.display_drs_title(p)
    # display initial parameterisation
    spirouStartup.spirouStartup.display_initial_parameterisation(p)
    # display system info (log only)
    spirouStartup.spirouStartup.display_system_info(p)

    input_debug = int(p['DRS_DEBUG'])

    for it in range(25):
        i = np.random.randint(0, len(levels))
        if levels[i] == 'error':
            p['DRS_DEBUG'] = 0
        try:
            wmsg = ('This is a test message, designed to test the logger '
                    'level="{0}"')
            debug = int(p['DRS_DEBUG'])
            WLOG(p, levels[i], wmsg.format(levels[i]))
        except:
            pass
        if levels[i] == 'error':
            p['DRS_DEBUG'] = int(input_debug)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":

    levels = ['all', 'debug', 'graph', 'info', 'warning', 'error'] + ['']*5

    p = spirouStartup.Begin(recipe=__NAME__, quiet=True)
    # ----------------------------------------------------------------------
    # reset p parameters
    p['DRS_DEBUG'] = 42
    p['COLOURED_LOG'] = True
    p['THEME'] = 'DARK'
    # test coloured log (dark theme)
    print('\n\nDEBUG: DARK Coloured log')
    test_log(p, levels)
    # test coloured log (light theme)
    print('\n\nDEBUG: LIGHT Coloured log')
    p['THEME'] = 'light'
    test_log(p, levels)
    # test uncoloured log
    print('\n\nDEBUG: Uncoloured log')
    p['COLOURED_LOG'] = False
    test_log(p, levels)
    # ----------------------------------------------------------------------
    # reset p parameters
    p['DRS_DEBUG'] = 0
    p['COLOURED_LOG'] = True
    p['THEME'] = 'DARK'
    # test coloured log (dark theme)
    print('\n\nDARK Coloured log')
    test_log(p, levels)
    # test coloured log (light theme)
    print('\n\nLIGHT Coloured log')
    p['THEME'] = 'light'
    test_log(p, levels)
    # test uncoloured log
    print('\n\nUncoloured log')
    p['COLOURED_LOG'] = False
    test_log(p, levels)

# =============================================================================
# End of code
# =============================================================================
