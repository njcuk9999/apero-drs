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
DEFAULT_LANG = base.DEFAULT_LANG
LANG = base.IPARAMS.get('LANGUAGE', DEFAULT_LANG)
# get and load the language database once
try:
    langdbm = drs_db.LanguageDatabase()
    # if we can't access straight away go to proxy
    langdbm.database.tries = 1
    # load database
    langdbm.load_db()
    # Can be the case that we have the database but we are yet to
    # create the language table - in this case we need to use the proxy
    # dictionary instead - else we get the dictionary from the langauage
    # database table
    if langdbm.database.tname in langdbm.database.tables:
        langdict = langdbm.get_dict(language=LANG)
    else:
        langdict = drs_base.lang_db_proxy()
# if we can't then we have no language database
except Exception as _:
    langdict = drs_base.lang_db_proxy()
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
        str.__init__(*args, **kwargs)
        self.tkey = None
        self.tvalue = str(args[0])
        self.targs = None
        self.tkwargs = None
        self.t_short = ''
        self.formatted = False

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state (for pickle)
        return state

    def __setstate__(self, state):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __add__(self, other: Union['Text', str]):
        """
        string-like addition (returning a Text instance)

        Equivalent to x + y

        :param other: Text or str, add 'other' (y) to end of self (x)

        :return: combined string (x + y)   (self + other)
        """
        # must merge changes from other if Text instance
        if isinstance(other, Text):
            othertext = other.get_text()
        else:
            othertext = str(other)
        # make new object
        msg = Text(self.get_text() + othertext)
        # set text properties
        msg.set_text_props(self.tkey)
        return msg

    def __radd__(self, other: Union['Text', str]):
        """
        string-like addition (returning a Text instance)

        Equivalent to y + x

        :param other: Text or str, add 'other' (y) to start of self (x)

        :return: combined string (y + x)   (other + self)
        """
        # must merge changes from other if Text instance
        if isinstance(other, Text):
            othertext = other.get_text()
        else:
            othertext = str(other)
        # make new object
        msg = Text(othertext + self.get_text())
        # set text properties
        msg.set_text_props(self.tkey)
        return msg

    def __mul__(self, other):
        NotImplemented('Multiply in {0}.Text not implemented'.format(__NAME__))

    def set_text_props(self, key: str,
                       args: Union[List[Any], str, None] = None,
                       kwargs: Union[Dict[str, Any], None] = None):
        """
        Add the text properties to the Text (done so init is like str)

        :param key: str, the key (code id) for the language database
        :param value: str, the text (unformatted)
        :param args: if set a list of arguments to pass to the formatter
                     i.e. value.format(*args)
        :param kwargs: if set a dictionary of keyword arguments to pass to the
                       formatter (i.e. value.format(**kwargs)
        :return: None - updates tkey, tvalue, targs, tkwargs
        """
        self.tkey = str(key)
        # deal with arguments
        if args is not None:
            if isinstance(args, list):
                self.targs = list(args)
            else:
                self.targs = [str(args)]
        # deal with kwargs
        if kwargs is not None:
            self.tkwargs = dict(kwargs)

    def get_text(self, report: bool = False,
                 reportlevel: Union[str, None] = None) -> str:
        """
        Return the full text (with reporting if requested) for this Text
        instance - this is returned as a string instance

        if report = True:
            "X[##-###-#####]: msg.format(*self.targs, **self.tkwargs)"
        else:
            "msg.format(*self.targs, **self.tkwargs)"

        :param report: bool, - if true reports the code id of this text entry
                       in format X[##-###-#####] where X is the first
                       character in reportlevel
        :param reportlevel: str, single character describing the reporting
                            i.e. E for Error, W for Warning etc

        :return: string representation of the Text instance
        """
        # ---------------------------------------------------------------------
        # deal with report level character
        if isinstance(reportlevel, str):
            reportlevel = reportlevel[0].upper()
        else:
            reportlevel = self.t_short
        # ---------------------------------------------------------------------
        # make sure tvalue is up-to-date
        self.get_formatting()
        # ---------------------------------------------------------------------
        vargs = [reportlevel, self.tkey, self.tvalue]
        # deal with report
        if report and (self.tkey != self.tvalue):
            valuestr = '{0}[{1}]: {2}'.format(*vargs)
        else:
            valuestr = '{2}'.format(*vargs)
        # ---------------------------------------------------------------------
        return valuestr

    def get_formatting(self, force=False):
        # don't bother if already formatted
        if not force and self.formatted:
            return
        # set that we have formatted (so we don't do it again)
        self.formatted = True
        # ---------------------------------------------------------------------
        # deal with no value
        if self.tvalue is None:
            value = str(self)
        else:
            value = self.tvalue
        # ---------------------------------------------------------------------
        # deal with no args
        if self.targs is None and self.tkwargs is None:
            self.tvalue = value
        elif self.tkwargs is None and self.targs is not None:
            self.tvalue = value.format(*self.targs)
        elif self.targs is None and self.tkwargs is not None:
            self.tvalue = value.format(**self.tkwargs)
        else:
            self.tvalue = value.format(*self.targs, **self.tkwargs)

    def __repr__(self) -> str:
        if not self.formatted:
            self.get_formatting()
        return str(self.tvalue)

    def __str__(self) -> str:
        if not self.formatted:
            self.get_formatting()
        return str(self.tvalue)


def textentry(key: str, args: Union[List[Any], str, None] = None,
              kwargs: Union[Dict[str, Any], None] = None) -> Text:
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
    msg_obj.set_text_props(key, args, kwargs)
    # return msg_obj
    return msg_obj


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
        dataframes[instruments[it]] = pd.concat(dflist, sort=True)

    # push dataframes into csv files for reset
    for instrument in dataframes:
        # get dataframe
        df = dataframes[instrument]
        # get reset path
        rpath = os.path.join(out_dir, reset_paths[instrument])
        # write path to log: Saving reset file
        wcode = '40-001-00028'
        wmsg = drs_base.BETEXT[wcode]
        drs_base.base_printer(wcode, wmsg, '', args=[rpath])
        # remove non utf-8 characters
        for column in df.columns:
            # change encoding
            values = df[column].str.encode('ascii', 'ignore')
            values = values.str.decode('ascii')
            # add back to columns
            df[column] = values
        # save to csv
        df.to_csv(rpath, sep=',', quoting=2, index=False, encoding='utf-8')


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
            wmsg = drs_base.BETEXT[wcode]
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
