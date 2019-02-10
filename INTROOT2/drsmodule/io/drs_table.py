#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-21 at 09:33

@author: cook
"""
from __future__ import division
import numpy as np
import os
from astropy.table import Table, vstack
from astropy.table import TableMergeError
from astropy.io.registry import get_formats
from astropy.io import fits
from collections import OrderedDict

from drsmodule import constants
from drsmodule.locale import drs_text
from drsmodule.config import drs_log
from . import drs_lock


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'table.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
ErrorEntry = drs_text.ErrorEntry

# -----------------------------------------------------------------------------


# =============================================================================
# Define usable table functions
# =============================================================================
def make_table(p, columns, values, formats=None, units=None):
    """
    Construct an astropy table from columns and values

    :param p: dictionary, parameter dictionary containing constants
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
    lcol = len(columns)
    # make sure we have as many columns as we do values
    if lcol != len(values):
        eargs = [lcol, len(values), func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00001', args=eargs))
    # make sure if we have formats we have as many as columns
    if formats is not None:
        if lcol != len(formats):
            eargs = [lcol, len(formats), func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00002', args=eargs))
    else:
        formats = [None] * len(columns)
    # make sure if we have units we have as many as columns
    if units is not None:
        if lcol != len(units):
            eargs = [lcol, len(units), func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00003', args=eargs))
    # make sure that the values in values are the same length
    lval1 = len(values[0])
    for value in values:
        if len(value) != lval1:
            WLOG(p, 'error', ErrorEntry('01-002-00004', args=[func_name]))
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
                eargs = [formats[c_it], col, func_name]
                WLOG(p, 'error', ErrorEntry('01-002-00005', args=eargs))
        # if we have units set the unit
        if units is not None:
            table[col].unit = units[c_it]
    # finally return table
    return table


def write_table(p, table, filename, fmt='fits', header=None):
    """
    Writes a table to file "filename" with format "fmt"

    :param p: dictionary, parameter dictionary containing constants
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
        eargs = [fmt, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00006', args=eargs))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['write?'][pos]:
            eargs = [fmt, func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00007', args=eargs))
    # get and check for file lock file
    lock, lock_file = drs_lock.check_fits_lock_file(p, filename)
    # try to write table to file
    try:
        # write file
        table.write(filename, format=fmt, overwrite=True)
        # close lock file
        drs_lock.close_fits_lock_file(p, lock, lock_file, filename)
    except Exception as e:
        # close lock file
        drs_lock.close_fits_lock_file(p, lock, lock_file, filename)
        # log error
        eargs = [type(e), e, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00008', args=eargs))

    if (fmt == 'fits') and (header is not None):
        # reload fits data
        data, filehdr = fits.getdata(filename, header=True)
        # push keys into file header (value, comment tuple)
        for key in list(header.keys()):
            filehdr[key] = tuple(header[key])
        # get and check for file lock file
        lock, lock_file = drs_lock.check_fits_lock_file(p, filename)
        # try to write table to file
        try:
            # save data
            fits.writeto(filename, data, filehdr, overwrite=True)
            # close lock file
            drs_lock.close_fits_lock_file(p, lock, lock_file, filename)
        except Exception as e:
            # close lock file
            drs_lock.close_fits_lock_file(p, lock, lock_file, filename)
            # log error
            eargs = [type(e), e, func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00009', args=eargs))


def merge_table(p, table, filename, fmt='fits'):
    """
    If a file already exists for "filename" try to merge this new table with
    the old one (requires all columns/formats to be the same).
    If filename does not exist writes "table" as if new table

    :param p: dictionary, parameter dictionary containing constants
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
            eargs = [filename, type(e), e, func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00010', args=eargs))
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

    :param p: dictionary, parameter dictionary containing constants
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
        eargs = [fmt, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00006', args=eargs))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            eargs = [fmt, func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00008', args=eargs))

    # check that filename exists
    if not os.path.exists(filename):
        emsg1 = 'File {0} does not exist'
        emsg2 = '    file = {0}'.format(filename)
        emsg3 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])

        eargs = [filename, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00011', args=eargs))

    # try to load file using astropy table
    try:
        table = Table.read(filename, format=fmt, **kwargs)
    except Exception as e:
        eargs = [type(e), e, filename, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00012', args=eargs))
        table = None

    # if we have colnames rename the columns
    if colnames is not None:
        if len(colnames) != len(table.colnames):
            eargs = [len(colnames), len(table.colnames), filename, func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00013', args=eargs))
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
        eargs = [filename, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00014', args=eargs))
    # read data
    try:
        astropy_table = Table.read(filename)
    except OSError as e:
        astropy_table = deal_with_missing_end_card(p, filename, e, func_name)
    except Exception as e:
        eargs = [filename, type(e), e, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00015', args=eargs))
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
        eargs = [dir_name, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00016', args=eargs))


    # get and check for file lock file
    lock, lock_file = drs_lock.check_fits_lock_file(p, output_filename)
    # write data
    try:
        # write file
        astropy_table.write(output_filename, format='fits', overwrite=True)
        # close lock file
        drs_lock.close_fits_lock_file(p, lock, lock_file, output_filename)
    except Exception as e:
        # close lock file
        drs_lock.close_fits_lock_file(p, lock, lock_file, output_filename)
        # log error
        eargs = [output_filename, type(e), e, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00017', args=eargs))


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
        eargs = [filename, type(e), e, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00018', args=eargs))
        data = None
    # test that we have columns and names
    if not hasattr(data, 'columns'):
        eargs = [filename, type(e), e, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00019', args=eargs))
        data = None
    if not hasattr(data.columns, 'names'):
        eargs = [filename, type(e), e, func_name]
        WLOG(p, 'error', ErrorEntry('01-002-00020', args=eargs))
        data = None
    # print warning
    wargs = [type(e), e, ext, filename, func_name]
    WLOG(p, 'warning', ErrorEntry('10-001-00006', args=wargs))
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
            eargs = [col, filename, func_name]
            WLOG(p, 'error', ErrorEntry('01-002-00021', args=eargs))
        # check format
        if table[col].dtype != pformat:
            try:
                newtable[col] = np.array(table[col]).astype(pformat)
            except Exception as e:
                eargs = [col, filename, type(e), e, func_name]
                WLOG(p, 'error', ErrorEntry('01-002-00022', args=eargs))
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
    # Cannot change language (as have no access to p)
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
