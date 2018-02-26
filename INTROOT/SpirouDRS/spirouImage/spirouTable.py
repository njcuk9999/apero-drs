#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou Table (other than fits) module

Created on 2017-12-07 at 16:14

@author: cook

Import rules: Not spirouLOCOR
"""
from __future__ import division
import numpy as np
import os
from astropy.table import Table
from astropy.io.registry import get_formats

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
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# get the logging function
WLOG = spirouCore.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# -----------------------------------------------------------------------------


# =============================================================================
# Define usable functions
# =============================================================================
def make_table(columns, values, formats=None, units=None):
    """
    Construct an astropy table from columns and values

    :param columns: list of strings, the list of column names
    :param values: list of lists or numpy array (2D), the list of lists/array
                   of values, first dimension must have same length as number
                   of columns, there must be the same number of values in each
                   column
    :param formats: list of strings, the astropy formats for each column
                    i.e. 0.2f  for a float with two decimal places, must have
                    same length as number of columns
    :param units: list of strings, the units for each column, must have
                  same length as number of columns

    :return table: astropy.table.Table instance, the astropy table containing
                   all columns and data
    """

    func_name = __NAME__ + '.make_table()'
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

            emsg1 = emsg.format(lcol, 'formats', len(formats))
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
    # make sure if we have units we have as many as columns
    if units is not None:
        if lcol != len(units):
            emsg1 = emsg.format(lcol, 'units', len(formats))
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
    # make sure that the values in values are the same length
    lval1 = len(values[0])
    for value in values:
        if len(value) != lval1:
            emsg1 = 'All values must have same number of rows '
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
    # now construct the table
    for c_it, col in enumerate(columns):
        # get value for this iteration
        val = values[c_it]
        # set columns
        table[col] = val
        # if we have formats set format
        if formats is not None:
            if test_number_format(formats[c_it]):
                table[col].format = formats[c_it]
            else:
                eargs1 = [formats[c_it], col]
                emsg1 = 'Format "{0}" is invalid (Column = {1})'
                emsg2 = '    function = {0}'.format(func_name)
                WLOG('error', DPROG, [emsg1.format(eargs1), emsg2])
        # if we have units set the unit
        if units is not None:
            table[col].unit = units[c_it]
    # finally return table
    return table


def write_table(table, filename, fmt='fits'):
    """
    Writes a table to file "filename" with format "fmt"

    :param table: astropy table, the table to be writen to file
    :param filename: string, the filename and location of the table to read
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)

    :return None:

    astropy.table writeable formats are as follows:

    """
    func_name = __NAME__ + '.write_table()'
    # get format table
    ftable = list_of_formats()
    # check that format in format_table
    if fmt not in ftable['Format']:
        emsg1 = 'fmt={0} not valid for astropy.table reading'.format(fmt)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            emsg1 = 'fmt={0} cannot be read by astropy.table'.format(fmt)
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
    # try to write table to file
    try:
        table.write(filename, format=fmt, overwrite=True)
    except Exception as e:
        emsg1 = 'Cannot write table to file'
        emsg2 = '    Error {0}: {1}'.format(type(e), e)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2, emsg3])


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

    :return None:

    astropy.table readable formats are as follows:

    """
    func_name = __NAME__ + '.read_table()'
    # get format table
    ftable = list_of_formats()

    # check that format in format_table
    if fmt not in ftable['Format']:
        emsg1 = 'fmt={0} not valid for astropy.table reading'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            emsg1 = 'fmt={0} cannot be read by astropy.table'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])

    # check that filename exists
    if not os.path.exists(filename):
        emsg1 = 'File {0} does not exist'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])

    # try to load file using astropy table
    try:
        table = Table.read(filename, format='ascii')
    except Exception as e:
        emsg1 = ' Error {0}: {1}'.format(type(e), e)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])
        table = None

    # if we have colnames rename the columns
    if colnames is not None:
        if len(colnames) != len(table.colnames):
            emsg1 = 'Number of columns not equal to number of columns in table'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
        # rename old names to new names
        oldcols = table.colnames
        for c_it, col in enumerate(colnames):
            table[oldcols[c_it]].name = col

    # return table
    return table


# =============================================================================
# Define worker functions
# =============================================================================
def test_number_format(fmt):
    """
    Test the format string with a floating point number
    :param fmt: string, the format string i.e. "7.4f"

    :return passed: bool, if valid returns True else returns False
    """
    try:
        _ = ('{0:' + fmt + '}').format(123.456789)
        return True
    except ValueError:
        return False


def list_of_formats():
    """
    Get the list of astropy formats and return it

    :return ftable: astropy.table.Table instance containing the formats allow
                    for reading and writing astropy tables
    """
    ftable = get_formats(Table)

    ftable['read?'] = ftable['Read'] == 'Yes'
    ftable['write?'] = ftable['Write'] == 'Yes'

    # return format table
    return ftable


def string_formats(ftable=None, mask=None):
    """
    Creates a string list of formats from the ftable created by
    spirouTable.list_of_formats()

    :param ftable: astropy.table.Table instance containing the formats allow
                   for reading and writing astropy tables created by
                   spirouTable.list_of_formats()
    :param mask: None or numpy array (1D), if not None defines which rows of
                 ftable to add to string

    :return string: string containing a print version of ftable (with mask
                    applied if mask is not None)
    """
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
    """
    Updates the documentation of "write_table" and "read_table" with the
    string version of the formats currently available in astropy.
    This is only for internal use after the function definitions, to append
    the doc strings in "write_table" and "read_table

    :return None:
    """
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
# End of code
# =============================================================================
