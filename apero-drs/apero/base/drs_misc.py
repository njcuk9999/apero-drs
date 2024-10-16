#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO core miscellaneous functionality

Created on 2020-08-2020-08-21 19:17

@author: cook

import rules

only from
- apero.base.*
- apero.lang.*
- apero.core.core.drs_break
- apero.core.core.drs_exceptions
"""
import os
import string
import time
from typing import Any
import pandas as pd

from aperocore.base import base
from aperocore import drs_lang
from aperocore.core import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.base.drs_misc.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get time
Time = base.Time
# get all chars
CHARS = string.ascii_uppercase + string.digits
# get textentry
textentry = drs_lang.textentry
# define relative path to google token files
PARAM1 = ('241559402076-vbo2eu8sl64ehur7'
          'n1qhqb0q9pfb5hei.apps.googleusercontent.com')
PARAM2 = ('apero-data-manag-', '1602517149890')
PARAM3 = ''.join(base.GSPARAM)
PARAM4 = ('1//0dBWyhNqcGHgdCgYIARAAGA0SNwF-L9IrhXoPCjWJtD4f0EDxA',
          'gFX75Q-f5TOfO1VQNFgSFQ_89IW7trN3B4I0UYvvbVfrGRXZZg')
PATH1 = 'gspread_pandas/google_secret.json'
PATH2 = 'gspread_pandas/creds/default'
TEXT1 = ('{{"installed":{{"client_id":"{0}","project_id":"{1}","auth_uri":'
         '"https://accounts.google.com/o/oauth2/auth","token_uri":'
         '"https://oauth2.googleapis.com/token","auth_provider_x509_cert'
         '_url":"https://www.googleapis.com/oauth2/v1/certs","client_'
         'secret":"{2}","redirect_uris":["urn:ietf:wg:oauth:2.0:oob",'
         '"http://localhost"]}}}}')
TEXT2 = ('{{"refresh_token": "{0}", "token_uri": "https://oauth2.googleap'
         'is.com/token", "client_id": "{1}", "client_secret": "{2}", '
         '"scopes": ["openid", "https://www.googleapis.com/auth/drive", '
         '"https://www.googleapis.com/auth/userinfo.email", '
         '"https://www.googleapis.com/auth/spreadsheets"]}}')
# get coded error
DrsCodedException= drs_exceptions.DrsCodedException


# =============================================================================
# Basic other functions
# =============================================================================
def gsp_setup():
    # make sure token is in correct directory
    outpath = os.path.join(os.path.expanduser('~'), '.config/')
    # make sure .config exists
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    # construct paths
    path1 = os.path.join(outpath, PATH1)
    path2 = os.path.join(outpath, PATH2)
    # make sure paths exist
    if not os.path.exists(os.path.dirname(path1)):
        os.makedirs(os.path.dirname(path1))
    if not os.path.exists(os.path.dirname(path2)):
        os.makedirs(os.path.dirname(path2))
    # make file
    with open(path1, 'w') as file1:
        file1.write(TEXT1.format(PARAM1, ''.join(PARAM2), PARAM3))
    with open(path2, 'w') as file2:
        file2.write(TEXT2.format(''.join(PARAM4), PARAM1, PARAM3))


def check_local_googlesheet(params: Any, dataframe,
                            sheet_name: str, sheet_id: str, logger=None,
                            check_len: bool = True):
    """
    Check a local backup of a google sheet against the version we want to
    upload - if for any reason it is shorter than the online version we will
    raise an error

    :param params: ParamDict, the parameter dictionary of constants
    :param google_sheet: gspread instance
    :param dataframe: pandas dataframe to add
    :param sheet_name: str, the name of the sheet
    :param sheet_id: str, the id of the sheet
    :param logger: logger instance (None means use print)
    :param check_len: bool, if True checks the length of the online version
                      and raises error if the new version is shorter
    :param kwargs: passed to push_to_googlesheet

    :raises DrsCodedException: if the online version is shorter than the local
    :return: Nothing, saves a local backup of dataframe (for future comparison)
    """
    # deal with local directory not existing
    if not os.path.exists(os.path.join(params['DRS_DATA_OTHER'], 'local')):
        os.makedirs(os.path.join(params['DRS_DATA_OTHER'], 'local'))
    # construct local path
    filename = os.path.join(params['DRS_DATA_OTHER'], 'local',
                            f'{sheet_id}_{sheet_name}.csv')
    # check if the local file exists
    if check_len and os.path.exists(filename):
        last_dataframe = pd.read_csv(filename)
        # check that the new dataframe isn't shorter than the old one
        if len(dataframe) < len(last_dataframe):
            emsg = (f'Sheet {sheet_name} ({sheet_id}) has got shorter - '
                    f'something went wrong. Please delete {last_dataframe} and '
                    f'try again - note we are resetting the online version to '
                    f'this last version.')
            raise DrsCodedException('None', level='error', message=emsg)
   # if local file still exists remove it
    if os.path.exists(filename):
        os.remove(filename)
    # print progress
    msg = 'Saving local backup ({0})'.format(filename)
    if logger is None:
        print(msg)
    else:
        logger(params, '', msg)
    # save table to local directory
    dataframe.to_csv(filename, index=False)


def pull_from_googlesheet(params: Any, google_sheet: Any, logger=None,
                          **kwargs):
    """
    Pull from googlesheets using the gspread class
    Has a while loop to try multiple times before raising an error

    :param params: ParamDict, the parameter dictionary of constants
    :param google_sheet: gspread instance
    :param dataframe: pandas dataframe to add
    :param logger: logger instance (None means use print)
    :param kwargs: passed to google_sheets.df_to_sheet

    :return:
    """
    # push dataframe back to server
    fail_count, error = 0, ''
    while fail_count < 10:
        try:
            return google_sheet.sheet_to_df(**kwargs)
        except Exception as e:
            msg = ('Attempt {0}: Could not pull from googlesheets. '
                   'Trying again in 45 s')
            margs = [fail_count + 1]
            # log the message
            if logger is None:
                print(msg.format(*margs))
            else:
                logger(params, 'warning', msg.format(*margs))
            fail_count += 1
            error = e
            time.sleep(45)
    # if we still have not succeeded raise exception here
    emsg = ('Could not pull from google sheets. Tried 10 times. '
            'Error {0}: {1}')
    raise DrsCodedException('None', level='error',
                            message=emsg.format(type(error), str(error)))


def push_to_googlesheet(params: Any, google_sheet: Any, dataframe: pd.DataFrame,
                        logger=None, **kwargs):
    """
    Push to googlesheets using the gspread class
    Has a while loop to try multiple times before raising an error

    :param params: ParamDict, the parameter dictionary of constants
    :param google_sheet: gspread instance
    :param dataframe: pandas dataframe to add
    :param logger: logger instance (None means use print)
    :param kwargs: passed to google_sheets.df_to_sheet

    :return:
    """
    # push dataframe back to server
    fail_count, error = 0, ''
    while fail_count < 10:
        try:
            google_sheet.df_to_sheet(dataframe, **kwargs)
            return
        except Exception as e:
            msg = ('Attempt {0}: Could not upload to googlesheets. '
                   'Trying again in 45 s')
            margs = [fail_count + 1]
            # log the message
            if logger is None:
                print(msg.format(*margs))
            else:
                logger(params, 'warning', msg.format(*margs))
            fail_count += 1
            error = e
            time.sleep(45)
    # if we still have not succeeded raise exception here
    emsg = ('Could not upload to google sheets. Tried 10 times. '
            'Error {0}: {1}')
    raise DrsCodedException('None', level='error',
                            message=emsg.format(type(error), str(error)))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
