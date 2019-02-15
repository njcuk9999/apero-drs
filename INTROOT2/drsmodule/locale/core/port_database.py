#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Just used to port database and clear up old files

Requires pandas to be installed

Created on 2019-01-24 at 13:49

@author: cook
"""
from astropy.table import Table
import importlib
import os
import shutil
from drsmodule.locale import drs_text
from drsmodule.locale import drs_exceptions


# =============================================================================
# Define variables
# =============================================================================
# define the package name
PACKAGE = 'drsmodule'
# define the database path relative to package
DATABASE_PATH = './locale/databases/'
# define the backup path relative to package
BACKUP_PATH = './locale/backup/'
# define the database (xls file)
DATABASE_FILE = 'language.xls'
# define the database names (sheet names in the xls file)
DATABASE_NAMES = ['HELP', 'ERROR', 'HELP_SPIROU', 'ERROR_SPIROU', 'HELP_NIRPS',
                  'ERROR_NIRPS']
# define the csv output filenames
OUTPUT_NAMES = ['help.csv', 'error.csv', 'help_spirou.csv', 'error_spirou.csv',
                'help_nirps.csv', 'error_nirps.csv']
# BADCODES

# define the pandas module
PANDAS_MODULE = 'pandas'
# get the Drs Exceptions
DRSError = drs_exceptions.DrsError
DRSWarning = drs_exceptions.DrsWarning
TextError = drs_exceptions.TextError
TextWarning = drs_exceptions.TextWarning
ConfigError = drs_exceptions.ConfigError
ConfigWarning = drs_exceptions.ConfigWarning
# get the logger
BLOG = drs_exceptions.basiclogger


# =============================================================================
# Define functions
# =============================================================================
def read_database(xls_file):

    # import pandas here
    try:
        pd = importlib.import_module(PANDAS_MODULE)
    except Exception as e:
        emsg1 = 'Requires pandas to be installed'
        emsg2 = '\tError was {0}: {1}'.format(type(e), e)
        BLOG([emsg1, emsg2], level='error', name='Database')
        return 1
    try:
        xls = pd.ExcelFile(xls_file)
    except Exception as e:
        emsg1 = 'Cannot open file="{0}"'.format(xls_file)
        emsg2 = '\tError was {0}: {1}'.format(type(e), e)
        BLOG([emsg1, emsg2], level='error', name='Database')
        return 1
    return xls


def convert_csv(xls, sheet_names, out_names, out_dir):
    outpaths = []
    # get sheets
    for it, sheet in enumerate(sheet_names):
        #
        BLOG('Writing sheet "{0}"'.format(sheet), level='', name='Database')
        # skip other sheets
        if sheet not in xls.sheet_names:
            emsg1 = 'Cannot find sheet {0} in database'
            BLOG(emsg1.format(sheet), level='error', name='Database')
        # get xls sheet
        pdsheet = xls.parse(sheet)
        # construct outpath
        outpath = os.path.join(out_dir, out_names[it])
        # save to csv
        pdsheet.to_csv(outpath, sep=',', quoting=2, index=False)
        # append to outpaths
        outpaths.append(outpath)
    # return outpaths
    return outpaths



def validate_csv(files):


    for filename in files:

        # try to get the data
        try:
            data = Table.read(filename, format='ascii.csv', fast_reader=False)
            del data
            continue
        except Exception as e:
            wmsg = 'Error occured when trying to validate: {0}'
            wmsg += '\n\t Error {0}: {1}'.format(type(e), e)
            BLOG(wmsg.format(filename), level='warning', name='CSV')

        # remove all bad characters




# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get abspath from relative path
    database_path = drs_text.get_relative_folder(PACKAGE, DATABASE_PATH)
    backup_path = drs_text.get_relative_folder(PACKAGE, BACKUP_PATH)
    # ----------------------------------------------------------------------
    # get database abspath
    dabspath = os.path.join(database_path, DATABASE_FILE)
    babspath = os.path.join(backup_path, DATABASE_FILE)
    # ----------------------------------------------------------------------
    # check that we have database file in files
    if not os.path.exists(dabspath):
        emsg = 'Cannot find database file {0} in directory {1}'
        eargs = [DATABASE_FILE, database_path]
        BLOG(emsg.format(*eargs), level='error', name='Database')
    # ----------------------------------------------------------------------
    # create a backup of the database
    shutil.copy(dabspath, babspath)
    # ----------------------------------------------------------------------
    #  first get contents of database directory
    files = os.listdir(database_path)
    # ----------------------------------------------------------------------
    # clear files from database (other than database)
    for filename in files:
        abspath = os.path.join(database_path, filename)
        if os.path.isdir(abspath):
            continue
        if filename != DATABASE_FILE:
            os.remove(abspath)
    # ----------------------------------------------------------------------
    # read the database file
    database = read_database(dabspath)
    # convert to csv and save
    opaths = convert_csv(database, DATABASE_NAMES, OUTPUT_NAMES, database_path)
    # validate csv files
    validate_csv(opaths)


# =============================================================================
# End of code
# =============================================================================
