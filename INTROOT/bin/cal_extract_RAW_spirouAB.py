#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_extract_RAW_spirou

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook

Last modified: 2017-12-11 at 15:24

Up-to-date with cal_extract_RAW_spirouAB AT-4 V47
"""
from __future__ import division

import cal_extract_RAW_spirou
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_extract_RAW_spirouAB.py'
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

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run cal_extract_RAW_spirou main with fibertype set
    # (get other arguments from command line - sys.argv)
    ll = cal_extract_RAW_spirou.main(fiber_type='AB',
                                     ic_extract_type='all',
                                     ic_ext_sigdet=-1)

# =============================================================================
# End of code
# =============================================================================
