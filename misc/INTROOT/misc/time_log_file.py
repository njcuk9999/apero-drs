#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-08 at 13:20

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as uu
from astropy.time import Time
from tqdm import tqdm
import warnings
from collections import OrderedDict


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def function1():
    return 0


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    # text = ''

    lines = text.split('\n')
    # print 'Hello World!'

    # storage
    storage = []
    # loop around lines
    for line in lines:
        if len(line) == 0:
            continue
        if line[0].isdigit():
            try:
                strtime = line.split('-')[0].strip()
                # assign random date
                strdate = '2019-01-01'
                # get rest of string
                rest = line[len(strtime):]
                # get time object
                t = Time('{0} {1}'.format(strdate, strtime))
                # add to storage
                storage.append([t, rest])
            except:
                continue

    time0 = storage[0][0]
    pfmt = '{0:06.3f} || {1:06.3f} - {2}'
    print(pfmt.format(0.0, 0.0, storage[0][1]))
    # loop around times takign the time delta
    for it in range(1, len(storage)):
        # get times from storage
        time1 = storage[it -1][0]
        time2 = storage[it][0]
        # get time delta in seconds
        timedelta0 = time2 - time0
        timedelta1 = time2 - time1
        timeseconds0 = np.round(timedelta0.to(uu.s), 3)
        timeseconds1 = np.round(timedelta1.to(uu.s), 3)
        pargs = [timeseconds0.value, timeseconds1.value, storage[it][1]]
        print(pfmt.format(*pargs))


# =============================================================================
# End of code
# =============================================================================
