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
from astropy.table import Table, vstack
from astropy.table import TableMergeError
from astropy.io.registry import get_formats
from astropy.io import fits
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from . import spirouFITS

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
# -----------------------------------------------------------------------------


# =============================================================================
# Define usable table functions
# =============================================================================
def make_table(p, columns, values, formats=None, units=None):
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
        WLOG(p, 'error', emsg.format(lcol, 'values', lval))
    # make sure if we have formats we have as many as columns
    if formats is not None:
        if lcol != len(formats):
            emsg1 = emsg.format(lcol, 'formats', len(formats))
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
    else:
        formats = [None] * len(columns)
    # make sure if we have units we have as many as columns
    if units is not None:
        if lcol != len(units):
            emsg1 = emsg.format(lcol, 'units', len(formats))
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
    # make sure that the values in values are the same length
    lval1 = len(values[0])
    for value in values:
        if len(value) != lval1:
            emsg1 = 'All values must have same number of rows '
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
    # now construct the table
    for c_it, col in enumerate(columns):
        # get value for this iteration
        val = values[c_it]
        # set columns
        table[col] = val
        # if we have formats set format
        if formats[c_it] is not None:
            if test_format(formats[c_it]):
                table[col].format = formats[c_it]
            else:
                eargs1 = [formats[c_it], col]
                emsg1 = 'Format "{0}" is invalid (Column = {1})'
                emsg2 = '    function = {0}'.format(func_name)
                WLOG(p, 'error', [emsg1.format(*eargs1), emsg2])
        # if we have units set the unit
        if units is not None:
            table[col].unit = units[c_it]
    # finally return table
    return table


def write_table(p, table, filename, fmt='fits', header=None):
    """
    Writes a table to file "filename" with format "fmt"

    :param table: astropy table, the table to be writen to file
    :param filename: string, the filename and location of the table
                     to written to
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)

    :param header: None or dict, if fmt='fits' this can be a header dictionary
                   of key, value, comment groups
                       i.e. header[key] = [value, comment]
                   which will be put into the header

    :return None:

    Note to open fits tables in IDL see here:
        https://idlastro.gsfc.nasa.gov/ftp/pro/fits_table/aaareadme.txt

        lookup:
            ftab_print, 'file.fits'
        read:
            tab = readfits('file.fits', hdr, /EXTEN)
            col1 = tbget(hdr, tab, 'COLUMN1')


    astropy.table writeable formats are as follows:

    """
    func_name = __NAME__ + '.write_table()'
    # get format table
    ftable = list_of_formats()
    # check that format in format_table
    if fmt not in ftable['Format']:
        emsg1 = 'fmt={0} not valid for astropy.table reading'.format(fmt)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            emsg1 = 'fmt={0} cannot be read by astropy.table'.format(fmt)
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
    # get and check for file lock file
    lock, lock_file = spirouFITS.check_fits_lock_file(p, filename)
    # try to write table to file
    try:
        # write file
        table.write(filename, format=fmt, overwrite=True)
        # close lock file
        spirouFITS.close_fits_lock_file(p, lock, lock_file, filename)
    except Exception as e:
        # close lock file
        spirouFITS.close_fits_lock_file(p, lock, lock_file, filename)
        # log error
        emsg1 = 'Cannot write table to file'
        emsg2 = '    Error {0}: {1}'.format(type(e), e)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])

    if (fmt == 'fits') and (header is not None):
        # reload fits data
        data, filehdr = fits.getdata(filename, header=True)
        # push keys into file header (value, comment tuple)
        combined_hdr = spirouFITS.Header(filehdr)
        combined_hdr.extend(header.cards, update=True)
        filehdr = combined_hdr.to_fits_header(strip=False)

        # get and check for file lock file
        lock, lock_file = spirouFITS.check_fits_lock_file(p, filename)
        # try to write table to file
        try:
            # save data
            fits.writeto(filename, data, filehdr, overwrite=True)
            # close lock file
            spirouFITS.close_fits_lock_file(p, lock, lock_file, filename)
        except Exception as e:
            # close lock file
            spirouFITS.close_fits_lock_file(p, lock, lock_file, filename)
            # log error
            emsg1 = 'Cannot write header to file'
            emsg2 = '    Error {0}: {1}'.format(type(e), e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])


def merge_table(p, table, filename, fmt='fits'):
    """
    If a file already exists for "filename" try to merge this new table with
    the old one (requires all columns/formats to be the same).
    If filename does not exist writes "table" as if new table

    :param table:  astropy table, the new table to be merged to existing file
    :param filename: string, the filename and location of the table
                     to written to
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)

    :return None:

    astropy.table writeable formats are as follows:
    """
    func_name = __NAME__ + '.merge_table()'
    # first try to open table
    if os.path.exists(filename):
        # read old table
        old_table = read_table(p, filename, fmt)
        # check against new table (colnames and formats)
        old_table = prep_merge(p, filename, old_table, table)
        # generate a new table
        try:
            new_table = vstack([old_table, table])
        except TableMergeError as e:
            emsg1 = 'Cannot merge file={0}'.format(filename)
            emsg2 = '    Error reads: {0}'.format(e)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
            new_table = None
        # write new table
        write_table(p, new_table, filename, fmt)
    # else just write the table
    else:
        write_table(p, table, filename, fmt)


def read_table(p, filename, fmt, colnames=None, **kwargs):
    """
    Reads a table from file "filename" in format "fmt", if colnames are defined
    renames the columns to these name

    :param filename: string, the filename and location of the table to read
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)
    :param colnames: list of strings or None, if not None renames all columns
                     to these strings, must be the same length as columns
                     in file that is read
    :param kwargs: keys to pass to the reader
                   (Table.read(filename, format=fmt**kwargs))

    :return None:

    astropy.table readable formats are as follows:

    """
    func_name = __NAME__ + '.read_table()'
    # get format table
    ftable = list_of_formats()

    # check that format in format_table
    if fmt not in ftable['Format']:
        emsg1 = 'fmt={0} not valid for astropy.table reading'
        emsg2 = '    file = {0}'.format(filename)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            emsg1 = 'fmt={0} cannot be read by astropy.table'
            emsg2 = '    file = {0}'.format(filename)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])

    # check that filename exists
    if not os.path.exists(filename):
        emsg1 = 'File {0} does not exist'
        emsg2 = '    file = {0}'.format(filename)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])

    # try to load file using astropy table
    try:
        table = Table.read(filename, format=fmt, **kwargs)
    except Exception as e:
        emsg1 = ' Error {0}: {1}'.format(type(e), e)
        emsg2 = '    file = {0}'.format(filename)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
        table = None

    # if we have colnames rename the columns
    if colnames is not None:
        if len(colnames) != len(table.colnames):
            emsg1 = ('Number of columns ({0}) not equal to number of '
                     'columns in table ({1})'
                     ''.format(len(colnames), len(table.colnames)))
            emsg2 = '    file = {0}'.format(filename)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
        # rename old names to new names
        oldcols = table.colnames
        for c_it, col in enumerate(colnames):
            table[oldcols[c_it]].name = col

    # return table
    return table


def print_full_table(p, table):
    tablestrings = table.pformat(max_lines=len(table)*10,
                                 max_width=9999)
    WLOG(p, '', '=' * len(tablestrings[0]), wrap=False)
    WLOG(p, '', tablestrings, wrap=False)
    WLOG(p, '', '=' * len(tablestrings[0]), wrap=False)


# =============================================================================
# Define usable table functions
# =============================================================================
def make_fits_table(dictionary=None):
    # if dictionary is None return empty astropy table
    if dictionary is None:
        return Table()
    # else construct from dictionary
    else:
        # construct astropy table
        astropy_table = Table()
        # loop through dictionary and add keys as columns
        for key in dictionary:
            astropy_table[key] = dictionary[key]
        # return filled astropy table
        return astropy_table


def read_fits_table(p, filename, return_dict=False):
    func_name = __NAME__ + '.read_fits_table()'
    # check that filename exists
    if not os.path.exists(filename):
        emsg1 = 'File {0} does not exist'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # read data
    try:
        astropy_table = Table.read(filename)
    except OSError as e:
        astropy_table = deal_with_missing_end_card(p, filename, e, func_name)
    except Exception as e:
        emsg1 = 'Error cannot open {0} as a fits table'.format(filename)
        emsg2 = '\tError was: {0}'.format(e)
        emsg3 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
        astropy_table = None
    # return dict if return_dict is True
    if return_dict:
        # set up dictionary for storage
        astropy_dict = OrderedDict()
        # copy the columns (numpy arrays) as the values to column name keys
        for col in astropy_table.colnames:
            astropy_dict[col] = np.array(astropy_table[col])
        # return dict
        return astropy_dict
    # return the astropy table
    return astropy_table


def write_fits_table(p, astropy_table, output_filename):
    func_name = __NAME__ + '.write_fits_table()'
    # get directory name
    dir_name = os.path.dirname(output_filename)
    # check directory exists
    if not os.path.exists(dir_name):
        emsg1 = 'Errors directory {0} does not exist'.format(dir_name)
        emsg2 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # get and check for file lock file
    lock, lock_file = spirouFITS.check_fits_lock_file(p, output_filename)
    # write data
    try:
        # remove file first
        os.remove(output_filename)
        # write file
        astropy_table.write(output_filename, format='fits', overwrite=True)
        # close lock file
        spirouFITS.close_fits_lock_file(p, lock, lock_file, output_filename)
    except Exception as e:
        # close lock file
        spirouFITS.close_fits_lock_file(p, lock, lock_file, output_filename)
        # log error
        emsg1 = 'Error cannot write {0} as a fits table'.format(output_filename)
        emsg2 = '\tError was: {0}'.format(e)
        emsg3 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])


# TODO: Find cause of this problem and fix properly
def deal_with_missing_end_card(p, filename, e, func_name):
    """
    This is specifically to fix a unidentfied error that causes fits table
    to be saved without END card.

    Generated with call to fits file:
        data = Table.read(fits_file)

    Error generated without this:
        OSError: Header missing END card.

    Solution is to read with fits (astropy.io.fits)
    --> also saves over old index file so this problem doesn't persist

    :param p: parameter dictionary
    :param filename: string, the full path and filename to open the file
    :param e: exception return, the error to print
    :param func_name: string, the function this was called for
                      (for error reporting)
    :return astropy_table: astropy.table.Table containing the fits file
    """
    hdu = fits.open(filename, ignore_missing_end=True)
    ext = None
    if hdu.data[0] is not None:
        data = hdu[0].data
        ext = 0
    elif hdu.data[1] is not None:
        data = hdu[1].data
        ext = 1
    else:
        emsg1 = 'Error cannot open {0} as a fits table'.format(filename)
        emsg2 = '\tError was: {0}'.format(e)
        emsg3 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
        data = None
    # test that we have columns and names
    if not hasattr(data, 'columns'):
        emsg1 = 'Error cannot open {0} as a fits table'.format(filename)
        emsg2 = '\tError was: data cannot read "columns"'
        emsg3 = '\tError was: {0}'.format(e)
        emsg4 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3, emsg4])
        data = None
    if not hasattr(data.columns, 'names'):
        emsg1 = 'Error cannot open {0} as a fits table'.format(filename)
        emsg2 = '\tError was: data cannot read "columns.names"'
        emsg3 = '\tError was: {0}'.format(e)
        emsg4 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3, emsg4])
        data = None
    # print warning
    wmsg1 = 'Error found = {0}'.format(e)
    wmsg2 = '\tCorrected by manually reading extension {0} as table'.format(ext)
    wmsg3 = '\tSaving over file "{0}"'.format(filename)
    wmsg4 = '\tfunction = {0}'.format(func_name)
    WLOG(p, 'warning', [wmsg1, wmsg2, wmsg3, wmsg4])
    # convert data to astropy table
    astropy_table = Table()
    for col in data.columns.names:
        astropy_table[col] = np.array(data[col])
    # save table for next time
    astropy_table.write(filename, format='fits', overwrite=True)
    # return table
    return astropy_table


# =============================================================================
# Define worker functions
# =============================================================================
def prep_merge(p, filename, table, preptable):
    func_name = __NAME__ + '.prep_merge()'
    # set up new table to store prepped data
    newtable = Table()
    # loop around all columns
    for col in preptable.colnames:
        # get required format
        pformat = preptable[col].dtype
        # check for column name
        if col not in table.colnames:
            emsg1 = 'Column {0} not in file {1}'.format(col, filename)
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # check format
        if table[col].dtype != pformat:
            try:
                newtable[col] = np.array(table[col]).astype(pformat)
            except Exception as e:
                emsg1 = 'Incompatible data types for column={0} for file {1}'
                emsg2 = '    error reads: {0}'.format(e)
                WLOG(p, 'error', [emsg1.format(col, filename), emsg2])
        else:
            newtable[col] = table[col]
    # return prepped table
    return newtable


def test_format(fmt):
    """
    Test the format string with a floating point number
    :param fmt: string, the format string i.e. "7.4f"

    :return passed: bool, if valid returns True else returns False
    """
    try:
        if fmt.startswith('{') and fmt.endswith('}'):
            return True
        elif 's' in fmt:
            return True
        elif 'd' in fmt:
            _ = ('{0:' + fmt + '}').format(123)
        else:
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
    # update doc for merge_table
    merge_table.__doc__ += string_formats(ftable, mask=None)
    # update doc for read_table
    readmask = ftable['read?']
    read_table.__doc__ += string_formats(ftable, mask=readmask)


# global call update the docs
update_docs()


# =============================================================================
# End of code
# =============================================================================
