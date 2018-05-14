#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_extract_RAW_spirou

Extracts order AB for specified files. Wrapper around cal_extract_RAW_spirou.py

Created on 2017-10-12 at 15:21

@author: cook

Last modified: 2017-12-11 at 15:24

Up-to-date with cal_extract_RAW_spirouAB AT-4 V47
"""
from __future__ import division

import cal_extract_RAW_spirou
from SpirouDRS import spirouStartup
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
# Define functions
# =============================================================================
def main(night_name=None, files=None, **kwargs):
    local = cal_extract_RAW_spirou.main(night_name, files,
                                        fiber_type='AB',
                                        ic_extract_type='2',
                                        ic_ext_sigdet=-1, **kwargs)
    return local


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run cal_extract_RAW_spirou main with fibertype set
    # (get other arguments from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================
