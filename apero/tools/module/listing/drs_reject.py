#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DRS Rejection functions

Created on 2024-03-11 at 11:15

@author: cook
"""
from typing import Tuple

import numpy as np
import pandas as pd
import gspread_pandas as gspd

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_misc
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
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def add_file_reject(params: ParamDict, identifier: str):
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
    # ----------------------------------------------------------------------
    # if we have the identifier report and return
    if identifier in identifier_column:
        # make a mask for the identifier
        mask = identifier_column == identifier
        # get the comment for the identifier
        comment = np.array(dataframe['COMMENT'])[mask][0]

        msg = 'Identifier already in reject list with comment: {0}'
        margs = [comment]
        WLOG(params, '', msg.format(*margs), colour='magenta')
        return
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
        pp, tel, rv, comment = ask_user_for_reject_info(identifier)
    # ----------------------------------------------------------------------
    # now we can add to dataframe
    new_row = dict(IDENTIFIER=[identifier], PP=[pp], TEL=[tel], RV=[rv],
                   COMMENT=[comment])
    # add to dataframe
    dataframe = pd.concat([dataframe, pd.DataFrame(new_row)], ignore_index=True)
    # print progress
    msg = 'Pushing identifier={0} to reject list google-sheet'
    WLOG(params, '', msg.format(identifier))
    # push dataframe back to server
    if not test:
        google_sheet.df_to_sheet(dataframe, index=False, replace=True,
                                 sheet=sheet_name)
    # print progress
    msg = 'identifier={0} added to reject list google-sheet'
    WLOG(params, '', msg.format(identifier))


def ask_user_for_reject_info(identifer: str) -> Tuple[int, int, int, str]:
    """
    Ask the user for the rejection information

    :param identifer: str, the identifer to reject

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
        msg = 'Reject identifier={0} at the {1} stage?'
        margs = [identifer, test]
        value = drs_installation.ask(msg.format(*margs), dtype='YN')
        # append to logic values
        logic_values.append(int(value))
    # get the values
    pp, tel, rv = logic_values
    # get the comment
    question = 'Enter a comment to reject identifier={0}'
    comment = drs_installation.ask(question.format(identifer),
                                   dtype=str)
    # return the values
    return pp, tel, rv, comment


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
