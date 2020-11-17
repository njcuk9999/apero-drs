#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-24 at 16:33

@author: cook

import rules

only from
- apero.base.*
- apero.lang.*
"""
from typing import Any, Union

from apero import lang
from apero.base import base
from apero.base import drs_base


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.base.drs_exceptions.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get astropy time
Time = base.Time
# track used warnings
USED_TEXT_WARNINGS = []
USED_DRS_WARNINGS = []
USED_CONFIG_WARNINGS = []


# =============================================================================
# Define exception classes
# =============================================================================
class DrsException(Exception):
    """Raised when config file is incorrect"""
    pass


class Exit(SystemExit):
    # Raised when exit is called
    pass


class LogExit(Exit):
    # This should only be used when exiting from a log message
    def __init__(self, errormessage: str, *args, **kwargs):
        """
        A Log exit exception (stores error message)

        :param errormessage: str, the error message to store
        :param args: args passed to Exit-->SystemExit class
        :param kwargs: kwargs passed to Exit-->SystemExit class
        """
        self.errormessage = errormessage
        _ = args, kwargs

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


class DebugExit(Exit):
    # This exception should only be used when exiting the debugger (ipdb/pdb)
    def __init__(self, errormessage: str, *args, **kwargs):
        """
        A Debug exit exception (stores error message)

        :param errormessage: str, the error message to store
        :param args: args passed to Exit-->SystemExit class
        :param kwargs: kwargs passed to Exit-->SystemExit class
        """
        self.errormessage = errormessage
        Exit.__init__(*args, **kwargs)

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


class DrsCodedException(DrsException):
    """
    Exception to be passed to drs logger (up the chain)
    """

    def __init__(self, codeid: str, level: Union[str, None] = None,
                 targs: Union[None, list, str] = None,
                 func_name: Union[str, None] = None,
                 message: Union[str, None] = None):
        """
        A Drs Coded Exception (normally to be caught and piped into a
        WLOG/TextEntry so that codeid can be converted to readable error

        :param codeid: str, the code from the language database
        :param level: str, if set sets the level for logging
        :param targs: None/list/str: if set is the args to pass to TextEntry
        :param func_name:  str or None, if set is the function name where
                           exception occured
        """
        self.codeid = codeid
        self.level = level
        self.targs = targs
        self.func_name = func_name
        self.message = message

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

    def __str__(self):
        """
        The string representation of the error: used as message when raised
        :return:
        """
        if self.message is not None:
            message = str(self.message)
        else:
            message = str(lang.textentry(self.codeid, self.targs))
        # return the base printer version string represntation
        return drs_base.base_printer(self.codeid, message, self.level,
                                     self.targs, self.func_name,
                                     printstatement=False)

    def __repr__(self):
        """
        The string representation of the error class
        :return:
        """
        return self.__str__()

    def get(self, key: str, default: Any):
        """
        Quick get attribute (codeid/level/targs/func_name) and give a default
        key if not present or set to None

        :param key: str, the attribute to look for (and return)
        :param default: Any, the object to assign if attribute is missing or
                        set to None
        :return:
        """
        # check if we have this attribute
        if hasattr(self, key):
            # get the attribute
            value = getattr(self, key)
            # if attributes value is None return the default
            if value is None:
                return default
            # else return the attributes value
            else:
                return value
        # else return the default value
        else:
            return default


class DrsCodedWarning:
    """
    Warning to be passed to drs logger (up the chain)
    """
    global USED_DRS_WARNINGS

    def __init__(self, codeid: str, level: Union[str, None] = None,
                 targs: Union[None, list, str] = None,
                 func_name: Union[str, None] = None):
        """
        A Drs Coded Exception (normally to be caught and piped into a
        WLOG/TextEntry so that codeid can be converted to readable error

        :param codeid: str, the code from the language database
        :param level: str, if set sets the level for logging
        :param targs: None/list/str: if set is the args to pass to TextEntry
        :param func_name:  str or None, if set is the function name where
                           exception occured
        """
        self.codeid = codeid
        self.level = level
        self.targs = targs
        self.func_name = func_name
        # get message from string representation
        message = self.__str__()
        # only print if not in used warnings (avoids repetition)
        if message in USED_DRS_WARNINGS:
            return
        else:
            print(message)

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

    def __str__(self):
        """
        The string representation of the error: used as message when raised
        :return:
        """
        message = lang.textentry(self.codeid, self.targs)
        # return the base printer version string represntation
        return drs_base.base_printer(self.codeid, message, self.level,
                                     self.targs, self.func_name,
                                     printstatement=False)

    def __repr__(self):
        """
        The string representation of the error class
        :return:
        """
        return self.__str__()

    def get(self, key: str, default: Any):
        """
        Quick get attribute (codeid/level/targs/func_name) and give a default
        key if not present or set to None

        :param key: str, the attribute to look for (and return)
        :param default: Any, the object to assign if attribute is missing or
                        set to None
        :return:
        """
        # check if we have this attribute
        if hasattr(self, key):
            # get the attribute
            value = getattr(self, key)
            # if attributes value is None return the default
            if value is None:
                return default
            # else return the attributes value
            else:
                return value
        # else return the default value
        else:
            return default


# =============================================================================
# Define functions
# =============================================================================
# define a function to clear out warnings (for exit script)
def clear_warnings():
    """
    clear all globally set warnings
    :return:
    """
    global USED_TEXT_WARNINGS
    global USED_DRS_WARNINGS
    global USED_CONFIG_WARNINGS

    USED_TEXT_WARNINGS = []
    USED_DRS_WARNINGS = []
    USED_CONFIG_WARNINGS = []


# Define basic log function (for when we don't have full logger functionality)
#   i.e. within apero.lang or apero.constants
#   Note this can't be language specific=
def wlogbasic(_: Any, level: Union[str, None] = None,
              message: Union[str, None] = None, **kwargs):
    """
    Define a wlog basic (same inputs as the drs_log.wlog) but passed to the
    basic logger

    :param _: normally parameters but not needed (but needed in call to
              emulate call of drs_log.wlog
    :param level: str the level of the log (error/warning/info/ etc)
    :param message: str, the message for the log
    :param kwargs: passed to basiclogger
    :return:
    """
    # if level is debug don't log
    if level == 'debug':
        return None
    else:
        if isinstance(message, lang.Text):
            codeid = message.tkey
        else:
            codeid = ''
        # print message (and deal with errors)
        if level == 'error' and len(codeid) == 0:
            drs_base.base_error(codeid, message, level, **kwargs)
        elif level == 'error':
            raise DrsCodedException(codeid, 'error', message=message)
        else:
            drs_base.base_printer(codeid, message=message, level=level,
                                  **kwargs)


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
