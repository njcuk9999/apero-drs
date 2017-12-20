#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-12-07 at 16:14

@author: cook



Version 0.0.0
"""
from __future__ import division
import numpy as np
import os
from astropy.table import Table
from astropy.io.registry import IORegistryError, get_formats

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore


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
# Define usable functions
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
    """
    Writes a table to file "filename" with format "fmt"

    :param filename: string, the filename and location of the table to read
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)
    :param colnames:
    :return:

    astropy.table writeable formats are as follows:

    """
    # get format table
    ftable = list_of_formats()

    # check that format in format_table
    if fmt not in ftable['Format']:
        wmsg = 'fmt={0} not valid for astropy.table reading (in {1})'
        WLOG('error', '', wmsg.format(fmt, __NAME__ + '/write_table()'))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            wmsg = 'fmt={0} cannot be read by astropy.table (in {1})'
            WLOG('error', '', wmsg.format(fmt, __NAME__ + '/write_table()'))

    try:
        table.write(filename, format=fmt, overwrite=True)
    except IORegistryError:
        emsg = 'Cannot write to file IO error in {0}'
        WLOG('error', '', emsg.format(__NAME__ + '/write_table'))


def read_table(filename, fmt, colnames=None):
    """
    Reads a table from file "filename" in format "fmt", if colnames are defined
    renames the columns to these name

    :param filename: string, the filename and location of the table to read
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)
    :param colnames: list of strings or None, if not None renames all columns
                     to these strings, must be the same length as columns
                     in file that is read
    :return:

    astropy.table readable formats are as follows:

    """
    # get format table
    ftable = list_of_formats()


    # check that format in format_table
    if fmt not in ftable['Format']:
        wmsg = 'fmt={0} not valid for astropy.table reading (in {1})'
        WLOG('error', '', wmsg.format(fmt, __NAME__ + '/read_table()'))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            wmsg = 'fmt={0} cannot be read by astropy.table (in {1})'
            WLOG('error', '', wmsg.format(fmt, __NAME__ + '/read_table()'))

    # check that filename exists
    if not os.path.exists(filename):
        raise IOError('File {0} does not exist'.format(filename))

    # load file using astropy table
    table = Table.read(filename, format='ascii')

    # if we have colnames rename the columns
    if colnames is not None:
        if len(colnames) != len(table.colnames):
            wmsg = ''
            WLOG('error', '', wmsg.format())
        # rename old names to new names
        oldcols = table.colnames
        for c_it, col in enumerate(colnames):
            table[oldcols[c_it]].name = col

    # return table
    return table

# =============================================================================
# Define worker functions
# =============================================================================
def list_of_formats():
    ftable = get_formats(Table)

    ftable['read?'] = ftable['Read'] == 'Yes'
    ftable['write?'] = ftable['Write'] == 'Yes'

    # return format table
    return ftable


def string_formats(ftable=None, mask=None):
    # deal with no format table
    if ftable is None:
        ftable = list_of_formats()
    # deal with no mask
    if mask is None:
        mask = np.ones(len(ftable), dtype=bool)
    # construct the top
    string = '\n\t Format \n\t ----------------------'
    # loop around the rows in Formats
    for row, fmt in enumerate(ftable['Format']):
        # only append if mask is True for this row
        if mask[row]:
            string += '\n\t {0}'.format(fmt)
    # return the string
    return string

def update_docs():
    # get ftable
    ftable = list_of_formats()
    # update doc for write_table
    writemask = ftable['write?']
    write_table.__doc__ += string_formats(ftable, mask=writemask)
    # update doc for read_table
    readmask = ftable['read?']
    read_table.__doc__ += string_formats(ftable, mask=readmask)


# global call update the docs
update_docs()

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
