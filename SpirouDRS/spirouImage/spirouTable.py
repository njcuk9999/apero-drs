#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-12-07 at 16:14

@author: cook



Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from astropy.table import Table
from astropy.io.registry import IORegistryError

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouTable.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# get the logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def make_table(columns, values, formats=None, units=None):

    # make empty table
    table = Table()
    # get variables
    emsg = ('Column names (length = {0}) must be equal length of {1} '
            ' (length = {2})')
    lcol = len(columns)
    lval = len(values)
    # make sure we have as many columns as we do values
    if lcol != lval:
        WLOG('error', '', emsg.format(lcol, 'values', lval))
    # make sure if we have formats we have as many as columns
    if formats is not None:
        if lcol != len(formats):
            WLOG('error', '', emsg.format(lcol, 'formats', len(formats)))
    # make sure if we have units we have as many as columns
    if units is not None:
        if lcol != len(units):
            WLOG('error', '', emsg.format(lcol, 'units', len(units)))
    # make sure that the values in values are the same length
    lval1 = len(values[0])
    for value in values:
        if len(value) != lval1:
            emsg = 'All values must have same number of rows '
            WLOG('error', '', emsg)
    # now construct the table
    for c_it, col in enumerate(columns):
        # get value for this iteration
        val = values[c_it]
        # set columns
        table[col] = val
        # if we have formats set format
        if formats is not None:
            table[col].format = formats[c_it]
        # if we have units set the unit
        if units is not None:
            table[col].unit = units[c_it]
    # finally return table
    return table


def write_table(table, filename, fmt='fits'):
    try:
        table.write(filename, format=fmt, overwrite=True)
    except IORegistryError:
        emsg = 'Table format {0} not understood, cannot write.'
        WLOG('error', '', emsg.format(fmt))




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
