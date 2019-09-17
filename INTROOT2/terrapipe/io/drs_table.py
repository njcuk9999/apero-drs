#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-21 at 09:33

import rules:
    Cannot import whole of terrapipe.config (drs_setup uses drs_table)

@author: cook
"""
from __future__ import division
import numpy as np
import os
import shutil
from astropy.table import Table, vstack
from astropy.table import TableMergeError
from astropy.io.registry import get_formats
from astropy.io import fits
from collections import OrderedDict

from terrapipe.core import constants
from terrapipe.locale import drs_text
from terrapipe.core.core import drs_log

from . import drs_lock


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_table.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = drs_text.TextEntry

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

    :type p: ParamDict
    :type columns: list[str]
    :type values: list[list]
    :type formats: list[str]
    :type units: list[str]

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table instance, the astropy table containing
                   all columns and data
    :rtype: astropy.table.Table
    """

    func_name = __NAME__ + '.make_table()'
    # make empty table
    table = Table()
    # get variables
    lcol = len(columns)
    # make sure we have as many columns as we do values
    if lcol != len(values):
        eargs = [lcol, len(values), func_name]
        WLOG(p, 'error', TextEntry('01-002-00001', args=eargs))
    # make sure if we have formats we have as many as columns
    if formats is not None:
        if lcol != len(formats):
            eargs = [lcol, len(formats), func_name]
            WLOG(p, 'error', TextEntry('01-002-00002', args=eargs))
    else:
        formats = [None] * len(columns)
    # make sure if we have units we have as many as columns
    if units is not None:
        if lcol != len(units):
            eargs = [lcol, len(units), func_name]
            WLOG(p, 'error', TextEntry('01-002-00003', args=eargs))
    # make sure that the values in values are the same length
    lval1 = len(values[0])
    for value in values:
        if len(value) != lval1:
            WLOG(p, 'error', TextEntry('01-002-00004', args=[func_name]))
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
                WLOG(p, 'error', TextEntry('01-002-00005', args=eargs))
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

    :type p: ParamDict
    :type table: astropy.table.Table
    :type filename: str
    :type fmt: str
    :type header: dict

    :return: None

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
        WLOG(p, 'error', TextEntry('01-002-00006', args=eargs))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['write?'][pos]:
            eargs = [fmt, func_name]
            WLOG(p, 'error', TextEntry('01-002-00007', args=eargs))
    # get and check for file lock file
    lock, lock_file = drs_lock.check_lock_file(p, filename)
    # try to write table to file
    try:
        # write file
        table.write(filename, format=fmt, overwrite=True)
        # close lock file
        drs_lock.close_lock_file(p, lock, lock_file, filename)
    except Exception as e:
        # close lock file
        drs_lock.close_lock_file(p, lock, lock_file, filename)
        # log error
        eargs = [type(e), e, func_name]
        WLOG(p, 'error', TextEntry('01-002-00008', args=eargs))

    if (fmt == 'fits') and (header is not None):
        # reload fits data
        data, filehdr = fits.getdata(filename, header=True)
        # push keys into file header (value, comment tuple)
        for key in list(header.keys()):
            filehdr[key] = tuple(header[key])
        # get and check for file lock file
        lock, lock_file = drs_lock.check_lock_file(p, filename)
        # try to write table to file
        try:
            # save data
            fits.writeto(filename, data, filehdr, overwrite=True)
            # close lock file
            drs_lock.close_lock_file(p, lock, lock_file, filename)
        except Exception as e:
            # close lock file
            drs_lock.close_lock_file(p, lock, lock_file, filename)
            # log error
            eargs = [type(e), e, func_name]
            WLOG(p, 'error', TextEntry('01-002-00009', args=eargs))


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

    :type p: ParamDict
    :type table: astropy.table.Table
    :type filename: str
    :type fmt: str

    :exception SystemExit: on caught errors

    :returns: None

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
            WLOG(p, 'error', TextEntry('01-002-00010', args=eargs))
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

    :type p: ParamDict
    :type filename: str
    :type fmt: str
    :type colnames: list[str]

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table read from filename
    :rtype: astropy.table.Table

    astropy.table readable formats are as follows:

    """
    func_name = __NAME__ + '.read_table()'
    # get format table
    ftable = list_of_formats()

    # check that format in format_table
    if fmt not in ftable['Format']:
        eargs = [fmt, func_name]
        WLOG(p, 'error', TextEntry('01-002-00006', args=eargs))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            eargs = [fmt, func_name]
            WLOG(p, 'error', TextEntry('01-002-00008', args=eargs))

    # check that filename exists
    if not os.path.exists(filename):
        eargs = [filename, func_name]
        WLOG(p, 'error', TextEntry('01-002-00011', args=eargs))

    # remove data_start for fits files
    if (fmt in ['fits']) and ('data_start' in kwargs):
        del kwargs['data_start']

    # try to load file using astropy table
    try:
        table = Table.read(filename, format=fmt, **kwargs)
    except Exception as e:
        eargs = [type(e), e, filename, func_name]
        WLOG(p, 'error', TextEntry('01-002-00012', args=eargs))
        table = None

    # if we have colnames rename the columns
    if colnames is not None:
        if len(colnames) != len(table.colnames):
            eargs = [len(colnames), len(table.colnames), filename, func_name]
            WLOG(p, 'error', TextEntry('01-002-00013', args=eargs))
        # rename old names to new names
        oldcols = table.colnames
        for c_it, col in enumerate(colnames):
            table[oldcols[c_it]].name = col

    # return table
    return table


def print_full_table(p, table):
    """
    print and log table (all lines) in standard drs manner

    :param p: ParamDict, the constants parameter dictionary
    :param table: astropy.table.Table

    :type p: ParamDict
    :type table: astropy.table.Table

    :exception SystemExit: on caught errors

    :return: None
    """
    tablestrings = table.pformat(max_lines=len(table)*10,
                                 max_width=9999)
    WLOG(p, '', '=' * len(tablestrings[0]), wrap=False)
    WLOG(p, '', tablestrings, wrap=False)
    WLOG(p, '', '=' * len(tablestrings[0]), wrap=False)


# =============================================================================
# Define usable table functions
# =============================================================================
def make_fits_table(dictionary=None):
    """
    Make fits table from a dictionary

    :param dictionary: dict, the dictionary to make the astropy table from

    :type dictionary: dict

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table representation of the dictionary
    :rtype: astropy.table.Table
    """
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
    """
    Read a fits table and return an astropy.table or a dictionary (depending
    on value of "return_dict"

    :param p: ParamDict, the constants parameter dictionary
    :param filename: str, the filename to open
    :param return_dict: bool, whether to return a dictionary (True) or an
                        astropy.table.Table (False) default is False

    :type p: ParamDict
    :type filename: str
    :type return_dict: bool

    :exception SystemExit: on caught errors

    :returns: either an Astropy Table or OrderedDict
    :rtype: astropy.table.Table | dict
    """
    func_name = __NAME__ + '.read_fits_table()'
    # get and check for file lock file
    lock, lock_file = drs_lock.check_lock_file(p, filename)
    # check that filename exists
    if not os.path.exists(filename):
        eargs = [filename, func_name]
        WLOG(p, 'error', TextEntry('01-002-00014', args=eargs))
    # read data
    try:
        astropy_table = Table.read(filename)
    except OSError as e:
        # close lock file
        drs_lock.close_lock_file(p, lock, lock_file, filename)
        # try to deal with missing card issue
        astropy_table = deal_with_missing_end_card(p, filename, e, func_name)
    except Exception as e:
        # close lock file
        drs_lock.close_lock_file(p, lock, lock_file, filename)
        # display error
        eargs = [filename, type(e), e, func_name]
        WLOG(p, 'error', TextEntry('01-002-00015', args=eargs))
        astropy_table = None
    # close lock file
    drs_lock.close_lock_file(p, lock, lock_file, filename)
    # return dict if return_dict is True
    if return_dict:
        # set up dictionary for storage
        astropy_dict = OrderedDict()
        # copy the columns (numpy arrays) as the values to column name keys
        for col in astropy_table.colnames:
            astropy_dict[col] = np.array(astropy_table[col], dtype=str)
        # return dict
        return astropy_dict
    # return the astropy table
    return astropy_table


def write_fits_table(p, astropy_table, output_filename):
    """
    Write "astropy_table" fits table to "output_filename"

    :param p: ParamDict, the constants parameter dictionary
    :param astropy_table: astropy.table.Table, the input table to save
    :param output_filename: str, the output filename to save to

    :type p: ParamDict
    :type astropy_table: astropy.table.Table
    :type output_filename: str

    :exception SystemExit: on caught errors

    :returns: None
    """
    func_name = __NAME__ + '.write_fits_table()'
    # get directory name
    dir_name = os.path.dirname(output_filename)
    # check directory exists
    if not os.path.exists(dir_name):
        eargs = [dir_name, func_name]
        WLOG(p, 'error', TextEntry('01-002-00016', args=eargs))
    # get backup file name
    backup_file = output_filename.replace('.fits', '.fits.back')
    # get and check for file lock file
    lock, lock_file = drs_lock.check_lock_file(p, output_filename)
    # deal with file already existing
    if os.path.exists(output_filename):
        try:
            # backup file
            shutil.copy(output_filename, backup_file)
            # remove file
            os.remove(output_filename)
        except Exception as e:
            # close lock file
            drs_lock.close_lock_file(p, lock, lock_file, output_filename)
            # log error
            eargs = [output_filename, type(e), e, func_name]
            WLOG(p, 'error', TextEntry('01-002-00017', args=eargs))
    # write data
    try:
        # write file
        astropy_table.write(output_filename, format='fits', overwrite=True)
        # close lock file
        drs_lock.close_lock_file(p, lock, lock_file, output_filename)
        # remove backup file
        if os.path.exists(output_filename) and os.path.exists(backup_file):
            os.remove(backup_file)
    except Exception as e:
        # close lock file
        drs_lock.close_lock_file(p, lock, lock_file, output_filename)
        # remove backup file
        if os.path.exists(output_filename) and os.path.exists(backup_file):
            os.remove(backup_file)
        # log error
        eargs = [output_filename, type(e), e, func_name]
        WLOG(p, 'error', TextEntry('01-002-00017', args=eargs))


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

    :param p: ParamDict, the constant parameter dictionary
    :param filename: string, the full path and filename to open the file
    :param e: exception return, the error to print
    :param func_name: string, the function this was called for
                      (for error reporting)

    :type p: ParamDict
    :type filename: str
    :type e: Exception
    :type func_name: str

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table containing the fits file
    :rtype: astropy.table.Table
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
        WLOG(p, 'error', TextEntry('01-002-00018', args=eargs))
        data = None
    # test that we have columns and names
    if not hasattr(data, 'columns'):
        eargs = [filename, type(e), e, func_name]
        WLOG(p, 'error', TextEntry('01-002-00019', args=eargs))
        data = None
    if not hasattr(data.columns, 'names'):
        eargs = [filename, type(e), e, func_name]
        WLOG(p, 'error', TextEntry('01-002-00020', args=eargs))
        data = None
    # print warning
    wargs = [type(e), e, ext, filename, func_name]
    WLOG(p, 'warning', TextEntry('10-001-00006', args=wargs))
    # convert data to astropy table
    astropy_table = Table()
    for col in data.columns.names:
        astropy_table[col] = np.array(data[col])
    # save table for next time
    astropy_table.write(filename, format='fits', overwrite=True)
    # return table
    return astropy_table


def vstack_cols(params, tablelist):
    # deal with empty list
    if len(tablelist) == 0:
        # append a None
        return None
    elif len(tablelist) == 1:
        # append the single row
        return  tablelist[0]
    else:
        # get column names
        columns = tablelist[0].colnames
        # get value dictionary
        valuedict = dict()
        for col in columns:
            valuedict[col] = []
        # loop around elements in tablelist
        for it, table_it in enumerate(tablelist):
            # loop around columns and add to valudict
            for col in columns:
                valuedict[col] += list(table_it[col])
        # push into new table
        newtable = Table()
        for col in columns:
            newtable[col] = valuedict[col]
        # vstack all rows
        return newtable


# =============================================================================
# Define worker functions
# =============================================================================
def prep_merge(p, filename, table, preptable):
    """
    Prepare the merging of two files by checking that all columns and
    data types are correct

    :param p: ParamDict, the constants parameter dictionary
    :param filename: str, the filename of the table to merge
    :param table: astropy.table.Table, the parent table to merge to
    :param preptable: astropy.table.Table, the child table to merge into
                      "table" (parent)

    :type p: ParamDict
    :type filename: str
    :type table: astropy.table.Table
    :type preptable: astropy.table.Table

    :exception SystemExit: on caught errors

    :returns: the updated "preptable" ready for merging
    :rtype: astropy.table.Table
    """
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
            WLOG(p, 'error', TextEntry('01-002-00021', args=eargs))
        # check format
        if table[col].dtype != pformat:
            try:
                newtable[col] = np.array(table[col]).astype(pformat)
            except Exception as e:
                eargs = [col, filename, type(e), e, func_name]
                WLOG(p, 'error', TextEntry('01-002-00022', args=eargs))
        else:
            newtable[col] = table[col]
    # return prepped table
    return newtable


def test_format(fmt):
    """
    Test the format string with a floating point number

    :param fmt: string, the format string i.e. "7.4f"

    :type fmt: str

    :returns: bool, if valid returns True else returns False
    :rtype: bool
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

    :returns: astropy.table.Table instance containing the formats allow
              for reading and writing astropy tables
    :rtype: astropy.table.Table
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

    :type ftable: astropy.table.Table | None
    :type mask: np.ndarray

    :return: string containing a print version of ftable (with mask
             applied if mask is not None)
    :rtype: str
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
    merge_table.__doc__ += string_formats(ftable)
    # update doc for read_table
    readmask = ftable['read?']
    read_table.__doc__ += string_formats(ftable, mask=readmask)


# global call update the docs
update_docs()


# =============================================================================
# End of code
# =============================================================================
