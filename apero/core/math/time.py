#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 15:54

@author: cook
"""
from apero.base import base
from apero.core.core import drs_misc

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.time.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Astropy Time and Time Delta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# get display func
display_func = drs_misc.display_func


# =============================================================================
# Define functions
# =============================================================================
def get_time_now() -> str:
    """
    Returns the time now (YYYY-mm-dd HH:MM:SS.SSS)

    :return time: string time YYYY-mm-dd HH:MM:SS.SSS
    """
    atime = Time.now()
    return atime.iso


def get_hhmmss_now() -> str:
    """
    Returns the time (HH:MM:SS.SSS)

    Assumes get_time_now() gives YYYY-mm-dd HH:MM:SS.SSS

    :return time: string time HH:MM:SS.SSS
    """
    full_time = get_time_now()
    return full_time.split(' ')[-1]


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
