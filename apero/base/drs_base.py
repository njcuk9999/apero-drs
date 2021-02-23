#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Only for functions that need to be used before or in the following codes:
- drs_db
- drs_exceptions
- drs_text

All functions using these function after this point should be overrided
elsewhere

Created on 2020-11-2020-11-13 16:06

@author: cook

Import rules:
- only from apero.base.base.py

"""
from hashlib import blake2b
import os
import pandas as pd
from pathlib import Path
import pkg_resources
from typing import Any, List, Union

from apero.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.base.drs_base.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# relative folder cache
REL_CACHE = dict()


# =============================================================================
# Define other functions - do not any apero functions in these
# =============================================================================
def lang_db_proxy() -> dict:
    """
    If all else fails (i.e. if the language database has yet to be
    installed - load the default reset file from reset csv files)

    :return: dictionary of key, value language pairs (default language)
    """
    # try to load the reset file manually
    # noinspection PyBroadException
    try:
        # get language path
        rellangpath = base.LANG_DEFAULT_PATH
        # get lang file
        rellangfile = base.LANG_DB_RESET
        # get default language
        if 'LANGUAGE' in base.IPARAMS:
            language = base.IPARAMS['LANGUAGE']
        else:
            language = base.DEFAULT_LANG
        # get relative path
        relpath = os.path.join(rellangpath, rellangfile)
        # get aboslute path
        langfile = _rel_folder(__PACKAGE__, relpath)
        # load language database
        df = pd.read_csv(langfile)
        # return dictionary
        return dict(zip(df['KEYNAME'], df[language]))
    # if we can't even do this then return an empty dictionary -
    #  all outputs will be the keyname
    except Exception as _:
        return dict()


def _rel_folder(package, folder):
    # change to this files location
    init = pkg_resources.resource_filename(package, '__init__.py')
    # Get the config_folder from relative path
    current = os.getcwd()
    # get directory name of folder
    dirname = os.path.dirname(init)
    # change to directory in init
    os.chdir(dirname)
    # get the absolute path of the folder
    absfolder = os.path.abspath(folder)
    # change back to current dir
    os.chdir(current)
    # return the absfolder
    return absfolder


def generate_hash(string_text: str, size: int = 10) -> str:
    # need to encode string
    encoded = string_text.encode('utf')
    # we want a hash of 10 characters
    digest = blake2b(encoded, digest_size=size)
    # create hash
    hash = digest.hexdigest()
    # return hash
    return str(hash)


# =============================================================================
# DrsBaseError text - only for where we do not have access to
#     apero.lang.coredrs_lang  this includes
#           - apero.base.drs_base
#           - apero.base.drs_db
#           - apero.lang.core.drs_lang
# =============================================================================
# Get the language database from the csv file in the default language
BETEXT = lang_db_proxy()


# =============================================================================
# Define base error
# =============================================================================
class DrsBaseException(Exception):
    """Raised when base function is incorrect"""
    pass


class DrsBaseError(DrsBaseException):
    def __init__(self, code, arguments=None):
        # define the class name
        self.classname = 'DrsBaseError'
        # define the language database code associated with this
        self.code = code
        # deal with bad code
        if self.code not in BETEXT:
            eargs = [self.code, __NAME__]
            raise DrsBaseError('KEYERROR', arguments=eargs)
        # define the message
        self.message = BETEXT[self.code]
        # define the args
        self.arguments = arguments

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

    def __repr__(self):
        """
        String representation used for raise Exception message printing
        :return:
        """
        if self.arguments is None:
            return self.message
        else:
            return self.message.format(*self.arguments)

    def __str__(self) -> str:
        """
        String representation used for raise Exception message printing
        :return:
        """
        return self.__repr__()


# =============================================================================
# Define core base functions
# =============================================================================
def base_func(func, _func, *args, **kwargs):
    """
    Wrapper to
    :param func:
    :param _func:
    :param args:
    :param kwargs:
    :return:
    """
    # try base function
    try:
        return func(*args, **kwargs)
    except DrsBaseError as drserror:
        base_error(drserror.code, drserror.message, 'error',
                   drserror.arguments)


def base_printer(codeid: str, message: str, level: str,
                 args: Union[str, list, None] = None,
                 exceptionname: Union[str, None] = None,
                 printstatement: bool = True) -> str:
    """
    Produce the base printout in form

    TIME - CHAR | PROGRAM | TYPE[CODE] Message

    where CHAR is *, !, ''
    where PROGRAM can be overwritten with exceptionname
    where TYPE is ERROR, WARNING, ''
    where CODE is codeid

    :param codeid: str, the code from the language database
    :param message: str, the message to print
    :param level: str, if set sets the level for logging
    :param args: None/list/str: if set is the args to pass to TextEntry
    :param exceptionname: str - if set overrides the program name
    :param printstatement: bool - if True prints the statement else just returns
                           it

    :return: str, the base printed message
    """
    red = base.COLOURS['RED1']
    yellow = base.COLOURS['YELLOW1']
    green = base.COLOURS['GREEN1']
    end = base.COLOURS['ENDC']
    # get time
    atime = base.Time.now()
    htime = atime.iso.split(' ')[-1]
    # define core format
    corefmt = '{0}-{1}|{2}|{3}'
    # start off with the exception name and code id
    # -------------------------------------------------------------------------
    if level == 'error':
        # set colour
        colour = red
        # set program
        if exceptionname is None:
            program = 'DrsBaseError'
        else:
            program = exceptionname
        # set level
        strlevel = 'E[{0}] '.format(codeid)
        charlevel = '*'
    # -------------------------------------------------------------------------
    elif level == 'warning':
        # set colour
        colour = yellow
        # set program
        if exceptionname is None:
            program = 'DrsBaseWarning'
        else:
            program = exceptionname
        # set level
        strlevel = 'W[{0}] '.format(codeid)
        charlevel = '!'
    # -------------------------------------------------------------------------
    else:
        # set colour
        colour = green
        # set program
        if exceptionname is None:
            program = ''
        else:
            program = exceptionname
        # set level
        strlevel = ''
        charlevel = ''
    # -------------------------------------------------------------------------
    # deal with args
    if args is not None:
        if isinstance(args, str):
            args = [args]
        message = message.format(*args)
    # -------------------------------------------------------------------------
    # construct string
    margs = [htime, charlevel, program, strlevel + message]
    msg = colour + corefmt.format(*margs) + end
    # -------------------------------------------------------------------------
    # print the message
    if printstatement:
        print(msg)
    # return the message
    return msg


def base_error(codeid: str, message: str, level: str,
               args: Union[str, list, None] = None,
               exceptionname: Union[str, None] = None,
               exception: Any = None) -> Any:
    # print error message
    base_printer(codeid, message, level, args, exceptionname)
    # raise exception
    if exception is not None:
        raise exception
    else:
        os._exit(0)


# =============================================================================
# Define base functions - should not be used except:
#        1. when define a function to override this
#        2. using somewhere override function cannot be used
# =============================================================================
def base_get_relative_folder(package: Union[None, str],
                             folder: Union[str, Path]) -> str:
    """
    BASE FUNCTION OVERRIDED IN apero.base.drs_break

    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    global REL_CACHE
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '.get_relative_folder()'
    if isinstance(folder, Path):
        folder = str(folder)
    # deal with no package
    if package is None:
        package = __PACKAGE__
    # ----------------------------------------------------------------------
    # check relative folder cache
    if package in REL_CACHE and folder in REL_CACHE[package]:
        return REL_CACHE[package][folder]
    # ----------------------------------------------------------------------
    # get the package.__init__ file path
    try:
        data_folder = _rel_folder(package, folder)
    except ImportError:
        eargs = [package, func_name]
        raise DrsBaseError('00-008-00001', arguments=eargs)
    # test that folder exists
    if not os.path.exists(data_folder):
        # raise exception
        eargs = [os.path.basename(data_folder), os.path.dirname(data_folder)]
        raise DrsBaseError('00-003-00005', arguments=eargs)
    # ----------------------------------------------------------------------
    # update REL_CACHE
    if package not in REL_CACHE:
        REL_CACHE[package] = dict()
    # update entry
    REL_CACHE[folder] = data_folder
    # ----------------------------------------------------------------------
    # return the absolute data_folder path
    return data_folder


def base_null_text(variable: Any, nulls: Union[None, List[str]] = None) -> bool:
    """
    BASE FUNCTION OVERRIDED IN apero.base.drs_text

    Deal with variables that are unset (i.e. None) but may be text nulls
    like "None" or ''  - nulls are set by "nulls" input

    :param variable: object, any variable to test for Null
    :param nulls: list of strings or None - if set extra strings that can be
                  a null value
    :return: True if value is a null value or False otherwise (or if variable
              is not str or None)
    """
    # if variable is None return True
    if variable is None:
        return True
    # if variable is in nulls (and nulls is set) return True
    if isinstance(variable, str):
        if nulls is not None:
            for null in nulls:
                if variable.upper() == null.upper():
                    return True
    # else in all other cases return False
    return False




# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
