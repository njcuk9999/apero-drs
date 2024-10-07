#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO base functionality

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
import os
from hashlib import blake2b
from pathlib import Path
from typing import Any, List, Union

import pkg_resources

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
# cache for language proxy dict
BETEXT = dict()

# =============================================================================
# Define other functions - do not any apero functions in these
# =============================================================================
def _escape_map(value: Any) -> Any:
    """
    Corrects \\n and \\t --> \n and \t  but breaks \\ if required before
    n and t

    :param value: Any, the value to check

    :return: Any, the checked and/or updated value
    """
    if not isinstance(value, str):
        return value
    else:
        if '\\n' in value or '\\t' in value:
            return value.replace('\\n', '\n').replace('\\t', '\t')
        else:
            return value


def lang_db_proxy(language=None):
    """
    If all else fails (i.e. if the language database has yet to be
    installed - load the default reset file from reset csv files)

    :return: dictionary of key, value language pairs (default language)
    """
    global BETEXT

    # get the apero path
    drs_root_guess = os.path.dirname(os.path.dirname(__file__))
    lang_path = os.path.join(drs_root_guess, 'base', 'drs_lang', 'tables')
    # deal with no language
    if language is None:
        language = base.DEFAULT_LANG
    # loop around lanuage table files
    for lang_basename in base.DEF_LANG_FILES:
        # construct language file
        lang_file = os.path.join(lang_path, lang_basename)
        # read file
        with open(lang_file, 'r') as lfile:
            lines = lfile.readlines()
        # make text pairs
        in_file = True
        while in_file:
            # if no lines left break
            if len(lines) == 0:
                break
            # get the first line
            line = lines.pop(0)
            # if we have a start of a text block
            if 'langlist.create' in line:
                # get the text key
                key = line.split('langlist.create(\'')[-1].split('\'')[0]
                # get the language values
                next_lines = lines[:len(base.LANGUAGES)]
                for nline in next_lines:
                    if f'item.value[\'{language}\']' in nline:
                        value = nline.split('] = ')[-1]
                        value = value.strip('\n')
                        value = value.strip('\'').strip('"')
                        value = value.replace('\\n', '\n')
                        value = value.replace('\\t', '\t')
                        BETEXT[key] = value
                        break


def _rel_folder(package: str, folder: str) -> str:
    """
    Return the absolute path from a relative 'folder' (relative to 'package')

    :param package: str, the package name
    :param folder: str, the relative directory

    :return: str, the absolute path of the relative 'folder'
    """
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
    """
    Generate a hash code based on the 'string_text' of length 'size'

    :param string_text: str, the string to generate hash code from
    :param size: int, the size of the hash to create

    :return: str, the generated hash code
    """
    # need to encode string
    encoded = string_text.encode('utf')
    # we want a hash of 10 characters
    digest = blake2b(encoded, digest_size=size)
    # create hash
    hashstr = digest.hexdigest()
    # return hash
    return str(hashstr)


# =============================================================================
# DrsBaseError text - only for where we do not have access to
#     apero.lang.coredrs_lang  this includes
#           - apero.base.drs_base
#           - apero.base.drs_db
#           - apero.lang.core.drs_lang
# =============================================================================
# Get the language database from the csv file in the default language
lang_db_proxy()


# =============================================================================
# Define base error
# =============================================================================
class DrsBaseException(Exception):
    """Raised when base function is incorrect"""
    pass


class DrsBaseError(DrsBaseException):
    def __init__(self, code: str, arguments: Union[List, None] = None):
        """
        Construct drs base error

        :param code: str, the language code for error string

        :param arguments: list, list of arguments for error string (or None if
                          no arguments
        """
        # define the class name
        self.classname = 'DrsBaseError'
        # define the language database code associated with this
        self.code = code
        # deal with bad code
        if self.code not in BETEXT:
            eargs = [self.code, __NAME__]
            raise DrsBaseError('KEYERROR', arguments=eargs)
        # define the message
        if arguments is None:
            self.message = 'E[{0}]: '.format(self.code) + BETEXT[self.code]
        else:
            self.message = ('E[{0}]: '.format(self.code) +
                            BETEXT[self.code].format(*arguments))
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
def base_func(func, _func: str, *args, **kwargs):
    """
    Wrapper to wrap around base functions

    :param func: any function
    :param _func: str, function name [not used?]
    :param args: arguments passed to 'func'
    :param kwargs: keyword arguments passed to 'func'

    :return: call to 'func'
    """
    # try base function
    try:
        return func(*args, **kwargs)
    except DrsBaseError as drserror:
        raise base_error(drserror.code, drserror.message, 'error',
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
        charlevel = '**'
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
        charlevel = '!!'
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


def base_error(codeid: str, message: str, level: str = 'error',
               args: Union[str, list, None] = None,
               exceptionname: Union[str, None] = None,
               exception: Any = None,
               exit_flag: bool = False) -> Any:
    """
    Base error prints the error using base_printer and DrsBaseError

    :param codeid: str, the language code for error string
    :param message: str, a message to add to the error string
    :param level: str, level of the message (normally 'error')
    :param args: list, list of arguments passed to error string
    :param exceptionname: str, name of the exception
    :param exception: valid python Exception
    :param exit_flag: bool, if True forces an exit after error

    :return: DrsBaseError or exception or exit
    """
    # print error message
    msg = base_printer(codeid, message, level, args, exceptionname,
                       printstatement=exit_flag)
    # raise exception
    if not exit_flag:
        # exit criteria
        if exception is None:
            return DrsBaseError(codeid, args)
        else:
            return exception(msg)
    else:
        # noinspection PyUnresolvedReferences,PyProtectedMember
        os._exit(0)


# =============================================================================
# Define base functions - should not be used except:
#        1. when define a function to override this
#        2. using somewhere override function cannot be used
# =============================================================================
def base_get_relative_folder(package: Union[None, str],
                             folder: Union[str, Path],
                             required: bool = True) -> str:
    """
    BASE FUNCTION OVERRIDED IN apero.base.drs_break

    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the config folder
    :param required: bool, if True raises an exception if absolute path does
                     not exist

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
        # deal with folder not being required
        if not required:
            return ''
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
