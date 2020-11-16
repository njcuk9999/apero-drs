#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-11-2020-11-13 10:41

@author: cook

# import rules

only from:
    - apero.base.base
    - apero.base.drs_base
    - apero.base.drs_db

"""
import numpy as np
import os
import pandas as pd
import shutil
from typing import Any, Dict, List, Union

from apero.base import base
from apero.base import drs_base
from apero.base import drs_db

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.lang.drs_lang.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get language from base
LANG = base.IPARAMS['LANGUAGE']
DEFAULT_LANG = base.DEFAULT_LANG
# get and load the language database once
langdbm = drs_db.LanguageDatabase()
langdbm.load_db()
langdict = langdbm.get_dict(language=LANG)
# define the database path relative to package
DATABASE_PATH = base.LANG_DEFAULT_PATH
# define the backup path relative to package
BACKUP_PATH = base.LANG_BACKUP_PATH
# define the database (xls file)
DATABASE_FILE = base.LANG_XLS_FILE


# =============================================================================
# Define classes
# =============================================================================
class Text(str):
    """
    Special text container (so we can store text entry key)
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.tkey = None
        self.tvalue = None
        self.targs = []
        self.tkwargs = dict()
        self.t_short = ''

    def set_text_props(self, key: str, value: str,
                       args: Union[List[Any], str, None] = None,
                       kwargs: Union[Dict[str, Any], None] = None):
        self.tkey = str(key)
        self.tvalue = str(value)
        if isinstance(args, str):
            self.targs = [args]
        else:
            self.targs = list(args)
        self.tkwargs = dict(kwargs)

    def get_text(self, report: bool = False,
                 reportlevel: Union[str, None] = None):
        # ---------------------------------------------------------------------
        # deal with report level character
        if isinstance(reportlevel, str):
            reportlevel = reportlevel[0].upper()
        else:
            reportlevel = self.t_short
        # ---------------------------------------------------------------------
        # deal with no args
        if self.targs is None and self.tkwargs is None:
            message = self.tvalue
        elif self.tkwargs is None:
            message = self.tvalue.format(*self.targs)
        elif self.targs is None:
            message = self.tvalue.format(**self.tkwargs)
        else:
            message = self.tvalue.format(*self.targs, **self.tkwargs)
        # ---------------------------------------------------------------------
        vargs = [reportlevel, self.tkey, message]
        # deal with report
        if report:
            valuestr = '{0}[{1}]: {2}'.format(*vargs)
        else:
            valuestr = '{2}'.format(*vargs)
        # ---------------------------------------------------------------------
        return valuestr


def textentry(key: str, args: Union[List[Any], str, None] = None,
              kwargs: Union[Dict[str, Any], None] = None):
    """
    Get text from a database

    This is the only function that can use langdict and expect it to be
    populated

    :param key:
    :param args:
    :param kwargs:
    :return:
    """
    # set function name
    _ = __NAME__ + '.textentry()'
    # deal with no entries
    if key not in langdict:
        message = key
    else:
        message = langdict[key]
    # deal with args
    if isinstance(args, str):
        args = [args]
    # create Text class for message
    msg_obj = Text(message)
    msg_obj.set_text_props(key, message, args, kwargs)
    # deal with no args
    if args is None and kwargs is None:
        return message
    elif kwargs is None:
        return message.format(*args)
    elif args is None:
        return message.format(**kwargs)
    else:
        return message.format(*args, **kwargs)


def read_xls(xls_file: str) -> pd.io.excel.ExcelFile:
    """
    Read a Excel file

    :param xls_file: str, the excel absolute path

    :return: a pandas representation of the excel file
    """
    # set function name
    _ = __NAME__ + '.read_xls()'
    # report progress: Loading database from file
    wcode = '40-001-00026'
    wmsg = drs_base.BETEXT[wcode]
    drs_base.base_printer(wcode, wmsg, '', args=[xls_file])
    try:
        xls = pd.ExcelFile(xls_file)
    except Exception as e:
        ecode = '00-002-00026'
        emsg = drs_base.BETEXT(ecode)
        eargs = [xls_file, str(e), e]
        return drs_base.base_error(ecode, emsg, 'error', args=eargs)
    return xls


def convert_csv(xls: pd.io.excel.ExcelFile, out_dir: str):
    """
    Use the pandas excel file to write the reset files (one default one and
    one for each instrument)

    :param xls: a pandas representation of the excel file
    :param out_dir: str, the output directory for the reset files

    :return: None - writes the reset files
    """
    # set function name
    func_name = __NAME__ + '.convert_csv()'
    # create sheet names
    sheet_names = ['HELP', 'TEXT']
    instruments = ['NONE', 'NONE']
    dataframes = dict(NONE=pd.DataFrame())
    reset_paths = dict(NONE=base.LANG_DB_RESET)
    # loop around instruments
    for instrument in base.INSTRUMENTS:
        # ignore None
        cond1 = drs_base.base_func(drs_base.base_null_text, func_name,
                                   instrument, ['None', '', 'NULL'])
        if cond1:
            continue
        # add help sheet
        sheet_names.append('HELP_{0}'.format(instrument.upper()))
        instruments.append(instrument)
        # add text sheet
        sheet_names.append('TEXT_{0}'.format(instrument.upper()))
        instruments.append(instrument)
        # add to dataframes
        dataframes[instrument] = pd.DataFrame()
        # add to reset paths
        reset_paths[instrument] = base.LANG_DB_RESET_INST.format(instrument)

    # get sheets
    for it, sheet in enumerate(sheet_names):
        # print progress: Analyzing sheet
        wcode = '40-001-00027'
        wmsg = drs_base.BETEXT[wcode]
        drs_base.base_printer(wcode, wmsg, '', args=[sheet])
        # skip other sheets
        if sheet not in xls.sheet_names:
            continue
        # get xls sheet
        pdsheet = xls.parse(sheet)
        # add to correct dataframe
        dflist = [dataframes[instruments[it]], pdsheet]
        dataframes[instruments[it]] = pd.concat(dflist)

    # push dataframes into csv files for reset
    for instrument in dataframes:
        # get dataframe
        df = dataframes[instrument]
        # get reset path
        rpath = os.path.join(out_dir, reset_paths[instrument])
        # write path to log: Saving reset file
        wcode = '40-001-00028'
        wmsg = drs_base.BETEXT
        drs_base.base_printer(wcode, wmsg, '', args=[rpath])
        # save to csv
        df.to_csv(rpath, sep=',', quoting=2, index=False)


def make_reset_csvs():
    # ----------------------------------------------------------------------
    # get abspath from relative path
    database_path = drs_base.base_get_relative_folder(__PACKAGE__,
                                                      DATABASE_PATH)
    backup_path = drs_base.base_get_relative_folder(__PACKAGE__, BACKUP_PATH)
    # ----------------------------------------------------------------------
    # get database abspath
    dabspath = os.path.join(database_path, DATABASE_FILE)
    babspath = os.path.join(backup_path, DATABASE_FILE)
    # ----------------------------------------------------------------------
    # check that we have database file in files
    if not os.path.exists(dabspath):
        ecode = '00-002-00027'
        emsg = drs_base.BETEXT[ecode]
        eargs = [DATABASE_FILE, database_path]
        return drs_base.base_error(ecode, emsg, 'error', args=eargs)
    # ----------------------------------------------------------------------
    # create a backup of the database: Backing up database
    wcode = '40-001-00029'
    wmsg = drs_base.BETEXT[wcode]
    drs_base.base_printer(wcode, wmsg, '', args=[babspath])
    shutil.copy(dabspath, babspath)
    # ----------------------------------------------------------------------
    #  first get contents of database directory
    files = np.sort(os.listdir(database_path))
    # ----------------------------------------------------------------------
    # clear files from database (other than database)
    for filename in files:
        abspath = os.path.join(database_path, filename)
        if os.path.isdir(abspath):
            continue
        if filename != DATABASE_FILE:
            # log message: Removing file
            wcode = '40-001-00030'
            wmsg = drs_base.BETEXT
            drs_base.base_printer(wcode, wmsg, '', args=[filename])
            os.remove(abspath)
    # ----------------------------------------------------------------------
    # read the database file
    xls_instance = read_xls(dabspath)
    # convert to csv and save
    convert_csv(xls_instance, database_path)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
