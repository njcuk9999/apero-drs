#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_extract_RAW_spirou

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""
from __future__ import division

import cal_extract_RAW_spirou
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_extract_RAW_spirouC.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
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
    cal_extract_RAW_spirou.main(fiber_type='C')

# =============================================================================
# End of code
# =============================================================================
