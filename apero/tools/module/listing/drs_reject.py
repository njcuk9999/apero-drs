#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DRS Rejection functions

Created on 2024-03-11 at 11:15

@author: cook
"""
import os
import glob
from typing import Tuple

import numpy as np
import pandas as pd
import gspread_pandas as gspd
from astropy.table import Table

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.utils import drs_recipe
from apero.core.core import drs_log
from apero.core.core import drs_misc
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.tools.module.setup import drs_installation

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_reject.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get time instance
Time = base.Time
# get text entry instance
textentry = lang.textentry
# get the parmeter dictionary instance
ParamDict = constants.ParamDict
# get the DrsRecipe instance
DrsRecipe = drs_recipe.DrsRecipe
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# get tqdm instance
TQDM = base.tqdm_module()
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def add_file_reject(params: ParamDict, recipe: DrsRecipe, raw_identifier: str):
    """
    Add an identifier to the file reject list

    :param params: ParamDict, the parameter dictionary of constants
    :param identifier: str, the identifier to reject

    :return: None, updates the file reject list
    """
    # add gspread directory and afiles
    drs_misc.gsp_setup()
    # get whether we are in a test
    test = params['INPUTS']['test']
    # check whether we have an auto fill
    autofill = params['INPUTS']['autofill']
    # define the sheet id and sheet name
    sheet_id = params['REJECT_LIST_GOOGLE_SHEET_URL']
    # get the google sheet name
    sheet_name = params['REJECT_LIST_GSHEET_SHEET_NAME']
    # load google sheet instance
    google_sheet = gspd.spread.Spread(sheet_id)
    # convert google sheet to pandas dataframe
    dataframe = google_sheet.sheet_to_df(index=0, sheet=sheet_name)
    # get the identifer column
    identifier_column = np.array(dataframe['IDENTIFIER']).astype(str)
    # get the raw directory
    rawdir = params['DRS_DATA_RAW']
    # get astrometric database
    objdbm = drs_database.AstrometricDatabase(params)
    # load astrometric database
    objdbm.load_db()
    # ----------------------------------------------------------------------
    # generate a list of raw files
    # ----------------------------------------------------------------------
    # print progress
    msg = 'Generating list of raw files'
    WLOG(params, 'info', msg)
    # storage of all raw files
    all_files = dict()
    # walk around all raw files
    for root, dirs, files in os.walk(rawdir, followlinks=True):
        # loop around files in this directories
        for filename in files:
            # append to raw_files
            filename_it = os.path.join(root, filename)
            # get the identifier
            identifier_it = os.path.basename(filename).split('.fits')[0]
            # push into dictionary
            all_files[identifier_it] = filename_it
    # ----------------------------------------------------------------------
    # deal with multiple identifiers (split by comma)
    if ',' in raw_identifier:
        identifiers = raw_identifier.split(',')
    else:
        identifiers = [raw_identifier]
    # ----------------------------------------------------------------------
    # simple cleaning to avoid some user errors
    for it, identifier in enumerate(identifiers):
        # remove any path given
        clean_identifier = os.path.basename(identifier)
        # remove .fits from the identifiers (user may have given the filename)
        if clean_identifier.endswith('.fits'):
            clean_identifier = clean_identifier[:-len('.fits')]
        # update identifiers
        identifiers[it] = clean_identifier
    # ----------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # ----------------------------------------------------------------------
    # loop around identifiers
    # ----------------------------------------------------------------------
    # storage for file indo
    file_info = dict()
    file_info['ROW'] = []
    file_info['IDENTIFIER'] = []
    file_info['OBSDIR'] = []
    file_info['DPRTYPE'] = []
    file_info['OBJNAME'] = []
    # counter for row
    row = 0
    # loop around identifiers and get file info (or skip)
    for identifier in identifiers:
        # print progresss
        msg = '\tAnalysing files for identifier: {0}'
        margs = [identifier]
        WLOG(params, '', msg.format(*margs))
        # if we have the identifier report and return
        if identifier in identifier_column:
            # make a mask for the identifier
            mask = identifier_column == identifier
            # get the comment for the identifier
            comment = np.array(dataframe['COMMENT'])[mask][0]

            msg = '\tIdentifier {0} already in reject list with comment: {1}'
            margs = [identifier, comment]
            WLOG(params, '', msg.format(*margs), colour='magenta')
            continue

        else:
            # locate identifier in all_files
            if identifier in all_files:
                # get filename
                filename = str(all_files[identifier])
                # get obsdir (remove rawdir and identifier)
                obsdir = filename.split(rawdir)[-1].split(identifier)[0]
                # remove leading and trailing os.sep
                obsdir = obsdir.strip(os.sep)
                # get header
                header = drs_fits.read_header(params, filename)
                # fix the header (as we do in apero)
                header, _ = pconst.HEADER_FIXES(params, recipe, header, dict(),
                                                filename, True, objdbm)
                # get dprtype
                dprtype = header[params['KW_DPRTYPE'][0]]
                # get apero objname
                objname = header[params['KW_OBJNAME'][0]]
            # otherwise say we do not have this file
            else:
                dprtype = '--'
                objname = '--'
                obsdir = 'NOT-ON-DISK'
            # push into storage
            file_info['ROW'].append(row)
            file_info['IDENTIFIER'].append(identifier)
            file_info['OBSDIR'].append(obsdir)
            file_info['DPRTYPE'].append(dprtype)
            file_info['OBJNAME'].append(objname)
            # increment row
            row += 1

    # ------------------------------------------------------------------------
    # print a summary table
    # ------------------------------------------------------------------------
    # convert to astropy table (for printing)
    file_table = Table(file_info)
    # print table will all columns and rows
    file_table.pprint(max_lines=-1, max_width=-1)

    # ------------------------------------------------------------------------
    # Ask if all rows are correct (and to remove any with the row number)
    question = 'Are all rows correct, please check carefully?'
    correct = drs_installation.ask(question, dtype='YN', default='Y')
    # storage of the rows to remove
    remove_row_ints = []
    # if all rows are not correct ask the user for the rows to remove
    while not correct:
        # ask for rows to remove
        question = ('Enter the row numbers to remove (comma separated),'
                    ' leave blank for no rows to add')
        remove_rows = drs_installation.ask(question, dtype=str)
        # split by comma
        remove_rows = remove_rows.split(',')
        # deal with no rows to add
        if len(remove_rows) == 0:
            correct = True
            continue
        # storage of the rows to remove
        remove_row_ints = []
        # flag warnings
        has_warnings = False
        # loop around all rows specified
        for _row in remove_rows:
            # try to convert to int and make sure it is in the table
            try:
                # convert to int
                remove_row_ints.append(int(_row))
                # deal with
                if int(_row) not in file_table['ROW']:
                    wmsg = 'Row number={0} not in table'
                    wargs = [_row]
                    WLOG(params, 'warning', wmsg.format(*wargs))
                    has_warnings = True

            except ValueError:
                wmsg = 'Row number={0} must be an integer'
                wargs = [_row]
                WLOG(params, 'warning', wmsg.format(*wargs))
                has_warnings= True
        # deal with having warnings --> restart while loop
        if has_warnings:
            continue
        else:
            correct = True
    # convert to numpy array (and double check we have only ints
    remove_rows = np.array(remove_row_ints).astype(int)
    # remove rows
    file_table.remove_rows(remove_rows)

    # ----------------------------------------------------------------------
    # if we have autofill use it
    if autofill not in [None, 'None']:
        # split the auto fill into PP,TEL,RV,COMMENT
        autofill_list = autofill.split(',')
        # check we have 4 values
        if len(autofill_list) != 4:
            WLOG(params, 'error', 'Autofill must be in form PP,TEL,RV,COMMENT')
            return
        # get the values
        pp_str, tel_str, rv_str, comment = autofill_list

        # pp, tel and rv should be 1 or 0 (True or False)
        logic_value_str = [pp_str, tel_str, rv_str]
        logic_values = []
        for value in logic_value_str:
            if str(value).upper() in ['1', 'TRUE', 'T']:
                logic_values.append(1)
            elif str(value).upper() in ['0', 'FALSE', 'F']:
                logic_values.append(0)
            else:
                emsg = '{0} must be True/T/1 or False/F/0'
                eargs = [value]
                WLOG(params, 'error', emsg.format(*eargs))
                return
        # get the values
        pp, tel, rv = logic_values
    # otherwise we ask the user for some information
    else:
        pp, tel, rv, comment = ask_user_for_reject_info()
    # ----------------------------------------------------------------------
    # loop around identifiers and add to reject list
    for identifier in file_table['IDENTIFIER']:
        # get the time now in iso format
        time_now = base.Time.now().iso
        # ----------------------------------------------------------------------
        # now we can add to dataframe
        new_row = dict(IDENTIFIER=[identifier], DATE_ADDED=[time_now],
                       PP=[pp], TEL=[tel], RV=[rv], USED=[1],
                       COMMENT=[comment])
        # add to dataframe
        dataframe = pd.concat([dataframe, pd.DataFrame(new_row)],
                              ignore_index=True)
        # print progress
        msg = 'Pushing identifier={0} to reject list google-sheet'
        WLOG(params, '', msg.format(identifier))
    # push dataframe back to server
    if not test:
        google_sheet.df_to_sheet(dataframe, index=False, replace=True,
                                 sheet=sheet_name)
    # print progress
    for identifier in file_table['IDENTIFIER']:
        msg = 'identifier={0} added to reject list google-sheet'
        WLOG(params, '', msg.format(identifier))


def ask_user_for_reject_info() -> Tuple[int, int, int, str]:
    """
    Ask the user for the rejection information

    :return: Tuple, 1. int, 1 if rejected at PP stage, 0 otherwise
                    2. int, 1 if rejected at TEL stage, 0 otherwise
                    3. int, 1 if rejected at RV stage, 0 otherwise
                    4. str, the comment for the rejection
    """
    # ask the user for the rejection information
    tests = ['PP', 'TEL', 'RV']
    logic_values = []
    for test in tests:
        # ask the user for the rejection information
        msg = 'Reject identifier(s) at the {0} stage?'
        margs = [test]
        value = drs_installation.ask(msg.format(*margs), dtype='YN')
        # append to logic values
        logic_values.append(int(value))
    # get the values
    pp, tel, rv = logic_values
    # get the comment
    question = 'Enter a comment to reject identifier(s)'
    comment = drs_installation.ask(question, dtype=str)
    # return the values
    return pp, tel, rv, comment


def update_from_obsdir(params: ParamDict, recipe: DrsRecipe, obsdir: str) -> str:
    """
    Update the identifier from the obsdir (add all observations that are not
    science observations to the reject list

    :param params: ParamDict, the parameter dictionary of constants
    :param obsdir: str, the obsdir to update from

    :return: str, comma separated list of identifiers from the obsdir
    """
    # deal with bad obsdir
    if obsdir in [None, 'None', '', 'Null']:
        return 'None'
    # get the raw directory from params
    rawdir = params['DRS_DATA_RAW']
    # deal with bad obsdir
    if obsdir not in os.listdir(rawdir):
        WLOG(params, 'error', '--obsdir={0} not found in raw directory')
        return 'None'
    # construct path to obsdir
    rawpath = os.path.join(rawdir, obsdir)
    # get the object database
    objdbm = drs_database.AstrometricDatabase(params)
    # load object database
    objdbm.load_db()
    # ----------------------------------------------------------------------
    # get the pseudo constants
    pconst = constants.pload()
    # ----------------------------------------------------------------------
    # get the files in the raw obs dir
    files = glob.glob(os.path.join(rawpath, '*.fits'))
    # deal with no files found
    if len(files) == 0:
        emsg = 'No files found in raw directory: {0}'
        eargs = [rawpath]
        WLOG(params, 'error', emsg.format(*eargs))
    # ----------------------------------------------------------------------
    # non-valid dptypes
    sci_dprtype = params['PP_OBJ_DPRTYPES']
    # state progress
    msg = 'Analysing files in raw directory: {0}'
    margs = [rawpath]
    WLOG(params, '', msg.format(*margs))
    # store valid files
    valid_files = []
    # we need to construct the dprtypes
    for filename in TQDM(files):
        # get header
        header = drs_fits.read_header(params, filename)
        # fix the header (as we do in apero)
        header, _ = pconst.HEADER_FIXES(params, recipe, header, dict(),
                                        filename, True, objdbm)
        # get dprtype
        dprtype = header[params['KW_DPRTYPE'][0]]
        # only add filename
        if dprtype not in sci_dprtype:
            valid_files.append(filename)
    # ----------------------------------------------------------------------
    # get the identifiers for the files (this should be the full filename
    # without the extension)
    identifiers = []
    for filename in valid_files:
        # get the identifier
        identifier = os.path.basename(filename).split('.fits')[0]
        # append to list
        identifiers.append(identifier)
    # ---------------------------------------------------------------------
    # State that we are adding this number of files
    msg = 'Adding {0} identifiers from obsdir={1}'
    margs = [len(identifiers), obsdir]
    WLOG(params, '', msg.format(*margs))
    # ----------------------------------------------------------------------
    # join into a comma separated string list
    return ','.join(identifiers)


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
