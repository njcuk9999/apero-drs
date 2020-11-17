#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-21 at 09:33

@author: cook

Import rules:
    only from core.core.drs_log, core.io, core.math, core.constants,
    apero.lang, apero.base

    do not import from core.core.drs_file
    do not import from core.core.drs_argument
    do not import from core.core.drs_database
"""
from astropy.table import Column, Table, vstack
from astropy.table import TableMergeError
from astropy.io.registry import get_formats
from astropy.io import fits
from collections import OrderedDict
import numpy as np
import os
import shutil
from typing import List, Tuple, Type, Union

from apero.base import base
from apero.core.core import drs_text
from apero.core import constants
from apero import lang
from apero.core.core import drs_log
from apero.io import drs_lock


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_table.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry

# -----------------------------------------------------------------------------
# define list of integers
INTEGERS = (np.int, np.int32, np.int64, int)
STRINGS = (str, np.str)
FLOATS = (np.float, np.float32, np.float64, float)


# =============================================================================
# Define usable table functions
# =============================================================================
def make_table(params: ParamDict, columns: List[str],
               values: Union[list, np.ndarray],
               formats: List[str] = None,
               units: List[str] = None) -> Table:
    """
    Construct an astropy table from columns and values

    :param params: dictionary, parameter dictionary containing constants
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

    :type params: ParamDict
    :type columns: list[str]
    :type values: list[list]
    :type formats: list[str]
    :type units: list[str]

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table instance, the astropy table containing
                   all columns and data
    :rtype: astropy.table.Table
    """
    # set function
    func_name = display_func(params, 'make_table', __NAME__)
    # make empty table
    table = Table()
    # get variables
    lcol = len(columns)
    # make sure we have as many columns as we do values
    if lcol != len(values):
        eargs = [lcol, len(values), func_name]
        WLOG(params, 'error', textentry('01-002-00001', args=eargs))
    # make sure if we have formats we have as many as columns
    if formats is not None:
        if lcol != len(formats):
            eargs = [lcol, len(formats), func_name]
            WLOG(params, 'error', textentry('01-002-00002', args=eargs))
    else:
        formats = [None] * len(columns)
    # make sure if we have units we have as many as columns
    if units is not None:
        if lcol != len(units):
            eargs = [lcol, len(units), func_name]
            WLOG(params, 'error', textentry('01-002-00003', args=eargs))
    # make sure that the values in values are the same length
    lval1 = len(values[0])
    for value in values:
        if len(value) != lval1:
            WLOG(params, 'error', textentry('01-002-00004', args=[func_name]))
    # now construct the table
    for c_it, col in enumerate(columns):
        # get value for this iteration
        val = values[c_it]
        # set columns
        table[col] = val
        # if we have formats set format
        if formats[c_it] is not None:
            if drs_text.test_format(formats[c_it]):
                table[col].format = formats[c_it]
            else:
                eargs = [formats[c_it], col, func_name]
                WLOG(params, 'error', textentry('01-002-00005', args=eargs))
        # if we have units set the unit
        if units is not None:
            table[col].unit = units[c_it]
    # finally return table
    return table


def write_table(params: ParamDict, table: Table, filename: str,
                fmt: str = 'fits', header: Union[dict, None] = None):
    """
    Writes a table to file "filename" with format "fmt"

    :param params: dictionary, parameter dictionary containing constants
    :param table: astropy table, the table to be writen to file
    :param filename: string, the filename and location of the table
                     to written to
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)

    :param header: None or dict, if fmt='fits' this can be a header dictionary
                   of key, value, comment groups
                       i.e. header[key] = [value, comment]
                   which will be put into the header

    :type params: ParamDict
    :type table: astropy.table.Table
    :type filename: str
    :type fmt: str
    :type header: dict

    :return: None - writes the table to 'filename'

    Note to open fits tables in IDL see here:
        https://idlastro.gsfc.nasa.gov/ftp/pro/fits_table/aaareadme.txt

        lookup:
            ftab_print, 'file.fits'
        read:
            tab = readfits('file.fits', hdr, /EXTEN)
            col1 = tbget(hdr, tab, 'COLUMN1')


    astropy.table writeable formats are as follows:

    """
    # set function
    func_name = display_func(params, 'write_table', __NAME__)
    # get format table
    ftable = list_of_formats()
    # check that format in format_table
    if fmt not in ftable['Format']:
        eargs = [fmt, func_name]
        WLOG(params, 'error', textentry('01-002-00006', args=eargs))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['write?'][pos]:
            eargs = [fmt, func_name]
            WLOG(params, 'error', textentry('01-002-00007', args=eargs))
    # ----------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    lockfile = os.path.basename(filename)
    # start a lock
    lock = drs_lock.Lock(params, lockfile)

    # make locked write function
    @drs_lock.synchronized(lock, params['PID'])
    def locked_write():
        # try to write table to file
        try:
            # write file
            table.write(filename, format=fmt, overwrite=True)
        except Exception as exception:
            # log error
            _eargs = [type(exception), exception, func_name]
            WLOG(params, 'error', textentry('01-002-00008', args=_eargs))

        if (fmt == 'fits') and (header is not None):
            # reload fits data
            data, filehdr = fits.getdata(filename, header=True)
            # push keys into file header (value, comment tuple)
            for key in list(header.keys()):
                filehdr[key] = tuple(header[key])
            # try to write table to file
            try:
                # save data
                fits.writeto(filename, data, filehdr, overwrite=True)
            except Exception as exception:
                # log error
                _eargs = [type(exception), exception, func_name]
                WLOG(params, 'error', textentry('01-002-00009', args=_eargs))
    # -------------------------------------------------------------------------
    # try to run locked makedirs
    try:
        locked_write()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


def merge_table(params: ParamDict, table: Table, filename: str,
                fmt: str = 'fits'):
    """
    If a file already exists for "filename" try to merge this new table with
    the old one (requires all columns/formats to be the same).
    If filename does not exist writes "table" as if new table

    :param params: dictionary, parameter dictionary containing constants
    :param table:  astropy table, the new table to be merged to existing file
    :param filename: string, the filename and location of the table
                     to written to
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)

    :type params: ParamDict
    :type table: astropy.table.Table
    :type filename: str
    :type fmt: str

    :exception SystemExit: on caught errors

    :returns: None - writes table to 'filename'

    astropy.table writeable formats are as follows:
    """
    # set function
    func_name = display_func(params, 'merge_table', __NAME__)
    # first try to open table
    if os.path.exists(filename):
        # read old table
        old_table = read_table(params, filename, fmt)
        # check against new table (colnames and formats)
        old_table = prep_merge(params, filename, old_table, table)
        # generate a new table
        try:
            new_table = vstack([old_table, table])
        except TableMergeError as e:
            eargs = [filename, type(e), e, func_name]
            WLOG(params, 'error', textentry('01-002-00010', args=eargs))
            new_table = None
        # write new table
        write_table(params, new_table, filename, fmt)
    # else just write the table
    else:
        write_table(params, table, filename, fmt)


def read_table(params: ParamDict, filename: str, fmt: str,
               colnames: Union[List[str], None] = None, **kwargs) -> Table:
    """
    Reads a table from file "filename" in format "fmt", if colnames are defined
    renames the columns to these name

    :param params: dictionary, parameter dictionary containing constants
    :param filename: string, the filename and location of the table to read
    :param fmt: string, the format of the table to read from (must be valid
                for astropy.table to read - see below)
    :param colnames: list of strings or None, if not None renames all columns
                     to these strings, must be the same length as columns
                     in file that is read
    :param kwargs: keys to pass to the reader
                   (Table.read(filename, format=fmt**kwargs))

    :type params: ParamDict
    :type filename: str
    :type fmt: str
    :type colnames: list[str]

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table read from filename
    :rtype: astropy.table.Table

    astropy.table readable formats are as follows:

    """
    # set function
    func_name = display_func(params, 'read_table', __NAME__)
    # get format table
    ftable = list_of_formats()
    # don't let format be None
    if fmt is None:
        fmt = 'fits'
    # check that format in format_table
    if fmt not in ftable['Format']:
        eargs = [fmt, func_name]
        WLOG(params, 'error', textentry('01-002-00006', args=eargs))
    # else check that we can read file
    else:
        pos = np.where(ftable['Format'] == fmt)[0][0]
        if not ftable['read?'][pos]:
            eargs = [fmt, func_name]
            WLOG(params, 'error', textentry('01-002-00008', args=eargs))

    # check that filename exists
    if not os.path.exists(filename):
        eargs = [filename, func_name]
        WLOG(params, 'error', textentry('01-002-00011', args=eargs))

    # remove data_start for fits files
    if (fmt in ['fits']) and ('data_start' in kwargs):
        del kwargs['data_start']

    # try to load file using astropy table
    try:
        table = Table.read(filename, format=fmt, **kwargs)
    except Exception as e:
        eargs = [type(e), e, filename, func_name]
        WLOG(params, 'error', textentry('01-002-00012', args=eargs))
        table = None

    # if we have colnames rename the columns
    if colnames is not None:
        if len(colnames) != len(table.colnames):
            eargs = [len(colnames), len(table.colnames), filename, func_name]
            WLOG(params, 'error', textentry('01-002-00013', args=eargs))
        # rename old names to new names
        oldcols = table.colnames
        for c_it, col in enumerate(colnames):
            table[oldcols[c_it]].name = col

    # return table
    return table


def print_full_table(params: ParamDict, table: Table):
    """
    print and log table (all lines) in standard drs manner

    :param params: ParamDict, the constants parameter dictionary
    :param table: astropy.table.Table

    :type params: ParamDict
    :type table: astropy.table.Table

    :exception SystemExit: on caught errors

    :return: None - prints the table (up to 9999)
    """
    # set function
    _ = display_func(params, 'print_full_table', __NAME__)
    # print table
    tablestrings = table.pformat(max_lines=len(table)*10,
                                 max_width=9999)
    WLOG(params, '', '=' * len(tablestrings[0]), wrap=False)
    WLOG(params, '', tablestrings, wrap=False)
    WLOG(params, '', '=' * len(tablestrings[0]), wrap=False)


# =============================================================================
# Define usable table functions
# =============================================================================
def make_fits_table(dictionary: Union[dict, None] = None) -> Table:
    """
    Make fits table from a dictionary

    :param dictionary: dict, the dictionary to make the astropy table from

    :type dictionary: dict

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table representation of the dictionary
    :rtype: astropy.table.Table
    """
    # set function
    _ = display_func(None, 'make_fits_table', __NAME__)
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


def read_fits_table(params: ParamDict, filename: str,
                    return_dict: bool = False) -> Union[Table, dict]:
    """
    Read a fits table and return an astropy.table or a dictionary (depending
    on value of "return_dict"

    :param params: ParamDict, the constants parameter dictionary
    :param filename: str, the filename to open
    :param return_dict: bool, whether to return a dictionary (True) or an
                        astropy.table.Table (False) default is False

    :type params: ParamDict
    :type filename: str
    :type return_dict: bool

    :exception SystemExit: on caught errors

    :returns: either an Astropy Table or OrderedDict
    :rtype: astropy.table.Table | dict
    """
    # set function
    func_name = display_func(params, 'read_fits_table', __NAME__)
    # check that filename exists
    if not os.path.exists(filename):
        eargs = [filename, func_name]
        WLOG(params, 'error', textentry('01-002-00014', args=eargs))
    # read data
    try:
        astropy_table = Table.read(filename)
    except OSError as e:
        # try to deal with missing card issue
        astropy_table = deal_with_missing_end_card(params, filename, e,
                                                   func_name)
    except Exception as e:
        # display error
        eargs = [filename, type(e), e, func_name]
        WLOG(params, 'error', textentry('01-002-00015', args=eargs))
        astropy_table = None
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


def write_fits_table(params: ParamDict, astropy_table: Table,
                     output_filename: str):
    """
    Write "astropy_table" fits table to "output_filename"

    :param params: ParamDict, the constants parameter dictionary
    :param astropy_table: astropy.table.Table, the input table to save
    :param output_filename: str, the output filename to save to

    :type params: ParamDict
    :type astropy_table: astropy.table.Table
    :type output_filename: str

    :exception SystemExit: on caught errors

    :returns: None -> writes 'astropy_table' to 'output_filename'
    """
    # set function
    func_name = display_func(params, 'write_fits_table', __NAME__)
    # get directory name
    dir_name = os.path.dirname(output_filename)
    # check directory exists
    if not os.path.exists(dir_name):
        eargs = [dir_name, func_name]
        WLOG(params, 'error', textentry('01-002-00016', args=eargs))
    # get backup file name
    backup_file = output_filename.replace('.fits', '.fits.back')
    # deal with file already existing
    if os.path.exists(output_filename):
        try:
            # backup file
            shutil.copy(output_filename, backup_file)
            # remove file
            os.remove(output_filename)
        except Exception as e:
            # log error
            eargs = [output_filename, type(e), e, func_name]
            WLOG(params, 'error', textentry('01-002-00023', args=eargs))
    # write data
    try:
        # write file
        astropy_table.write(output_filename, format='fits', overwrite=True)
        # remove backup file
        if os.path.exists(output_filename) and os.path.exists(backup_file):
            os.remove(backup_file)
    except Exception as e:
        # cond 1 output file exists
        cond1 = os.path.exists(output_filename)
        # remove backup file
        if cond1 and os.path.exists(backup_file):
            os.remove(backup_file)
        # if index file does not exist take it from the backup file
        elif not cond1 and os.path.exists(backup_file):
            shutil.copy(backup_file, output_filename)
        # log error
        eargs = [output_filename, type(e), e, func_name]
        WLOG(params, 'error', textentry('01-002-00017', args=eargs))


def deal_with_missing_end_card(params: ParamDict, filename: str,
                               exception: Exception, func: str) -> Table:
    """
    This is specifically to fix a unidentfied error that causes fits table
    to be saved without END card.

    Generated with call to fits file:
        data = Table.read(fits_file)

    Error generated without this:
        OSError: Header missing END card.

    Solution is to read with fits (astropy.io.fits)
    --> also saves over old index file so this problem doesn't persist

    :param params: ParamDict, the constant parameter dictionary
    :param filename: string, the full path and filename to open the file
    :param exception: exception return, the error to print
    :param func: string, the function this was called for (for error reporting)

    :type params: ParamDict
    :type filename: str
    :type exception: Exception
    :type func: str

    :exception SystemExit: on caught errors

    :returns: astropy.table.Table containing the fits file
    :rtype: astropy.table.Table
    """
    # set function
    func_name = display_func(params, 'deal_with_missing_end_card', __NAME__)
    if func is not None:
        func_name += '(via {0})'.format(func)
    # open fits file
    hdu = fits.open(filename, ignore_missing_end=True)
    ext = None
    if hdu[0].data is not None:
        data = hdu[0].data
        ext = 0
    elif hdu[1].data is not None:
        data = hdu[1].data
        ext = 1
    else:
        eargs = [filename, type(exception), exception, func_name]
        WLOG(params, 'error', textentry('01-002-00018', args=eargs))
        data = None
    # test that we have columns and names
    if not hasattr(data, 'columns'):
        eargs = [filename, type(exception), exception, func_name]
        WLOG(params, 'error', textentry('01-002-00019', args=eargs))
        data = None
    if not hasattr(data.columns, 'names'):
        eargs = [filename, type(exception), exception, func_name]
        WLOG(params, 'error', textentry('01-002-00020', args=eargs))
        data = None
    # print warning
    wargs = [type(exception), exception, ext, filename, func_name]
    WLOG(params, 'warning', textentry('10-001-00006', args=wargs))
    # convert data to astropy table
    astropy_table = Table()
    for col in data.columns.names:
        astropy_table[col] = np.array(data[col])
    # save table for next time
    astropy_table.write(filename, format='fits', overwrite=True)
    # return table
    return astropy_table


def vstack_cols(params: ParamDict,
                tablelist: List[Table]) -> Union[Table, None]:
    """
    Take a list of Astropy Tables and stack into single Astropy Table
    Note same as core.core.drs_recipe.vstack_cols

    :param params: ParamDict, parameter dictionary of constants
    :param tablelist: list of tables, the tables to stack
    :return:
    """
    # set function
    _ = display_func(params, 'vstack_cols', __NAME__)
    # deal with empty list
    if len(tablelist) == 0:
        # append a None
        return None
    elif len(tablelist) == 1:
        # append the single row
        return tablelist[0]
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
                # must catch instances of astropy.table.row.Row as
                #   they are not a list
                if isinstance(table_it, Table.Row):
                    valuedict[col] += [table_it[col]]
                # else we assume they are astropy.table.Table
                else:
                    valuedict[col] += list(table_it[col])
        # push into new table
        newtable = Table()
        for col in columns:
            newtable[col] = valuedict[col]
        # vstack all rows
        return newtable


def force_dtype_col(column: Union[np.ndarray, list, Column],
                    dtype: Union[Type, None] = str,
                    lower: bool = False, upper: bool = False,
                    strip: bool = False
                    ) -> Tuple[Union[np.ndarray, None], Union[Type, None]]:
    """
    Force a 'column' to a specific datatype 'dtype'

    :param column: np.array, list or astropy.table.Column - the column to try
                   to force all entries to the same dtype
    :param dtype: None or Type, the type to force (if None uses the first entry
                  to force all elements to that dtype
    :param lower: bool, if True and dtype is str force all to lower case
    :param upper: bool, if True and dtype is str force all to upper case
    :param strip: bool, if True and dtype is str force string.strip()

    :return: tuple, 1. if force typing was successful return a np.array of the
                    column (or if dtype not recognised)
                    2. the dtype forced to (None if not recognised/not forced)
    """
    # set function
    _ = display_func(None, 'force_dtype_col', __NAME__)
    # if we have no columns don't do anything
    if len(column) == 0:
        return column, None
    # if dtype not set try to work it out
    if dtype is None:
        if isinstance(column[0], INTEGERS):
            dtype = int
        elif isinstance(column[0], STRINGS):
            dtype = str
        elif isinstance(column[0], FLOATS):
            dtype = float
        else:
            dtype = None
    # deal with string columns
    if dtype in STRINGS:
        # noinspection PyBroadException
        try:
            # cast to string (may be byte)
            col = np.array(column).astype(str)
            # create character array
            col = np.char.array(col)
            if lower:
                col = col.lower()
            if upper:
                col = col.upper()
            if strip:
                col = col.strip()
            # return the column
            return col, str
        except Exception as _:
            return None, None
    # deal with integer columns
    if dtype in INTEGERS:
        # noinspection PyBroadException
        try:
            col = np.array(column).astype(int)
            return col, int
        except Exception as _:
            return None, None
    # deal with float columns
    if dtype in FLOATS:
        # noinspection PyBroadException
        try:
            col = np.array(column).astype(float)
            return col, float
        except Exception as _:
            return None, None
    # else just return the column as is
    return np.array(column), None


# =============================================================================
# Define worker functions
# =============================================================================
def prep_merge(params: ParamDict, filename: str, table: Table,
               preptable: Table) -> Table:
    """
    Prepare the merging of two files by checking that all columns and
    data types are correct

    :param params: ParamDict, the constants parameter dictionary
    :param filename: str, the filename of the table to merge
    :param table: astropy.table.Table, the parent table to merge to
    :param preptable: astropy.table.Table, the child table to merge into
                      "table" (parent)

    :type params: ParamDict
    :type filename: str
    :type table: astropy.table.Table
    :type preptable: astropy.table.Table

    :exception SystemExit: on caught errors

    :returns: the updated "preptable" ready for merging
    :rtype: astropy.table.Table
    """
    # set function
    func_name = display_func(params, 'prep_merge', __NAME__)
    # set up new table to store prepped data
    newtable = Table()
    # loop around all columns
    for col in preptable.colnames:
        # get required format
        pformat = preptable[col].dtype
        # check for column name
        if col not in table.colnames:
            eargs = [col, filename, func_name]
            WLOG(params, 'error', textentry('01-002-00021', args=eargs))
        # check format
        if table[col].dtype != pformat:
            try:
                newtable[col] = np.array(table[col]).astype(pformat)
            except Exception as e:
                eargs = [col, filename, type(e), e, func_name]
                WLOG(params, 'error', textentry('01-002-00022', args=eargs))
        else:
            newtable[col] = table[col]
    # return prepped table
    return newtable


def list_of_formats() -> Table:
    """
    Get the list of astropy formats and return it

    :returns: astropy.table.Table instance containing the formats allow
              for reading and writing astropy tables
    :rtype: astropy.table.Table
    """
    # set function
    _ = display_func(None, 'list_of_formats', __NAME__)
    # get table formats
    ftable = get_formats(Table)
    # push read and write into this table
    ftable['read?'] = ftable['Read'] == 'Yes'
    ftable['write?'] = ftable['Write'] == 'Yes'
    # return format table
    return ftable


def string_formats(ftable: Union[Table, None] = None,
                   mask: np.ndarray = None) -> str:
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

    :return: None - just update the docstrings
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
