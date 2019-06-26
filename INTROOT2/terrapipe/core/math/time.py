#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 15:54

@author: cook
"""

from astropy.time import Time


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def get_time_now():
    """
    Returns the time now (YYYY-mm-dd HH:MM:SS.SSS)

    :return time: string time YYYY-mm-dd HH:MM:SS.SSS
    """
    atime = Time.now()
    return atime.iso


def get_hhmmss_now():
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
