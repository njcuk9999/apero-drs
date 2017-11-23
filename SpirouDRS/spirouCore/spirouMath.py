#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-07 at 17:28

@author: cook

Import rules: Only from spirouConfig and spirouCore

Version 0.0.0
"""
from __future__ import division
import numpy as np
import datetime
import time

from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouMath.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Date format
DATE_FMT = "%Y-%m-%d-%H:%M:%S.%f"
# =============================================================================
# Define functions
# =============================================================================
def polyval(p, x):
    """
    Faster version of numpy.polyval
    From here: https://stackoverflow.com/a/32527284
    :param p:
    :param x:
    :return:
    """
    y = np.zeros(x.shape, dtype=float)
    for i, v in enumerate(p):
        y *= x
        y += v
    return y


# =============================================================================
# Time functions
# =============================================================================
def stringtime2unixtime(string, fmt=DATE_FMT):
    dt = datetime.datetime.strptime(string, fmt)
    t_tuple = dt.timetuple()
    return int(time.mktime(t_tuple))


def unixtime2stringtime(ts, fmt=DATE_FMT):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime(fmt)


# =============================================================================
# End of code
# =============================================================================
