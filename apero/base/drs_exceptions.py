#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-24 at 16:33

@author: cook

Rules only import base.py from apero.base no other apero modules
"""
import sys
from pathlib import Path
from typing import Any, List, Union

from apero.base import base

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
class TextException(Exception):
    """Raised when config file is incorrect"""
    pass


class TextError(TextException):
    """
    Custom Text Warning for passing to the log
    """

    def __init__(self, message: Union[str, None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True)
            message = message.split('\n')
            level = 'error'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level
        # send to basic logger
        basiclogger(message=self.message, level=self.level,  name='Text',
                    force_exit=False, wlog=wlog, **kwargs)

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
        String representation used for raise Exception message printing
        :return:
        """
        return _flatmessage(self.message)


class TextWarning:
    global USED_TEXT_WARNINGS

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for TextWarning sets message to self.message and level to
        self.level

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True,
                                      reportlevel='TextWarning')
            message = message.split('\n')
            level = 'warning'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = [message]
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'warning'
        else:
            self.level = level
        # deal with a list message (for printing)
        amessage = ''
        for it, mess in enumerate(self.message):
            if it > 0:
                amessage += '\n\t\t{0}'.format(mess)
            else:
                amessage += mess
        if amessage in USED_TEXT_WARNINGS:
            pass
        else:
            USED_TEXT_WARNINGS.append(amessage)
            # send to basic logger
            basiclogger(message=self.message, level=self.level, name='Text',
                        force_exit=False, wlog=wlog, **kwargs)

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


class DrsException(Exception):
    """Raised when config file is incorrect"""
    pass


class DrsError(DrsException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for DRSError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True)
            message = message.split('\n')
            level = 'error'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level
        # send to basic logger
        basiclogger(message=self.message, level=self.level,  name='DRS',
                    force_exit=False, wlog=wlog, **kwargs)

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
        return _flatmessage(self.message)


class DrsHeaderError(DrsException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None, key: Union[None, str] = None,
                 filename: Union[None, str, Path] = None):

        """
        Constructor for DRSError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        :param key: str/path if key is the key that caused the header exception
        :param filename: str the file that the header belong to that caused
                         exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True)
            message = message.split('\n')
            level = 'error'
        # get key and filename
        self.key = key
        self.filename = filename
        # set wlog
        self.wlog = wlog
        # deal with kwargs being None
        if kwargs is None:
            self.kwargs = dict()
        else:
            self.kwargs = kwargs
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level

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
        return _flatmessage(self.message)


class DrsWarning:
    global USED_DRS_WARNINGS

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for DrsWarning sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True,
                                      reportlevel='DrsWarning')
            message = message.split('\n')
            level = 'warning'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = [message]
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'warning'
        else:
            self.level = level
        # deal with a list message (for printing)
        amessage = ''
        for it, mess in enumerate(self.message):
            if it > 0:
                amessage += '\n\t\t{0}'.format(mess)
            else:
                amessage += mess
        if amessage in USED_DRS_WARNINGS:
            pass
        else:
            USED_DRS_WARNINGS.append(amessage)
            # send to basic logger
            basiclogger(message=self.message, level=self.level, name='DRS',
                        force_exit=False, wlog=wlog, **kwargs)

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


class ConfigException(Exception):
    """Raised when config file is incorrect"""
    pass


class ConfigError(ConfigException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True)
            message = message.split('\n')
            level = 'error'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level
        # send to basic logger
        basiclogger(message=self.message, level=self.level, name='Config',
                    force_exit=False, wlog=wlog, **kwargs)

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
        Standard string representation - used for raise Exception message
        :return:
        """
        return _flatmessage(self.message)


class ConfigWarning:
    global USED_CONFIG_WARNINGS

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for ConfigWarning sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True)
            message = message.split('\n')
            level = 'warning'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = [message]
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'warning'
        else:
            self.level = level

        # deal with a list message (for printing)
        amessage = ''
        for it, mess in enumerate(self.message):
            if it > 0:
                amessage += '\n\t\t{0}'.format(mess)
            else:
                amessage += mess
        if amessage in USED_CONFIG_WARNINGS:
            pass
        else:
            USED_CONFIG_WARNINGS.append(amessage)
            # send to basic logger
            basiclogger(message=self.message, level=self.level,
                        name='Config', force_exit=False, wlog=wlog, **kwargs)

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


class ArgumentException(Exception):
    """Raised when config file is incorrect"""
    pass


class ArgumentError(ArgumentException):
    # Custom Config Error for passing to the log

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for ArgumentError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True)
            message = message.split('\n')
            level = 'error'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level
        # send to basic logger
        basiclogger(message=self.message, level=self.level, name='Config',
                    force_exit=False, wlog=wlog, **kwargs)

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
        Standard string representation - used for raise Exception message
        :return:
        """
        return _flatmessage(self.message)


class ArgumentWarning:
    global USED_CONFIG_WARNINGS

    def __init__(self, message: Union[str, List[str], None] = None,
                 level: Union[str, None] = None,
                 wlog: Any = None, kwargs: Union[None, dict] = None,
                 errorobj: Any = None):
        """
        Constructor for ArgumentWarning sets message to self.message and level
        to self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        :param wlog: None or pass a drs_log.wlog instance (to use logger)
        :param kwargs: None or dict passed to basic logger
        :param errorobj: instance of raised exception
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True,
                                      reportlevel='ArgumentWarning')
            message = message.split('\n')
            level = 'warning'
        # deal with kwargs being None
        if kwargs is None:
            kwargs = dict()
        # deal with message
        if message is None:
            self.message = 'Unknown'
        elif type(message) == str:
            self.message = [message]
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'warning'
        else:
            self.level = level
        # deal with a list message (for printing)
        amessage = ''
        for it, mess in enumerate(self.message):
            if it > 0:
                amessage += '\n\t\t{0}'.format(mess)
            else:
                amessage += mess
        if amessage in USED_CONFIG_WARNINGS:
            pass
        else:
            USED_CONFIG_WARNINGS.append(amessage)
            # send to basic logger
            basiclogger(message=self.message, level=self.level,
                        name='Config', force_exit=False, wlog=wlog, **kwargs)

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


class DrsMathException(Exception):
    """Raised when config file is incorrect"""
    pass


class DrsCodedException(DrsException):
    """
    Exception to be passed to drs logger (up the chain)
    """
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
        # return the base printer version string represntation
        return base_printer(self.codeid, self.level, self.targs, self.func_name)

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


def base_printer(codeid: str, level: Union[str, None] = None,
                 args: Union[str, list, None] = None,
                 func_name: Union[str, None] = None) -> str:
    """
    Produce the string representation of a codeid error

    :param codeid: str, the code from the language database
    :param level: str, if set sets the level for logging
    :param args: None/list/str: if set is the args to pass to TextEntry
    :param func_name:  str or None, if set is the function name where
                       exception occured
    :return:
    """
    # start off with the excedption name and code id
    emsg = 'DrsCodedException[{0}]'.format(codeid)
    # if we have a level add it as a new line to the message
    if level is not None:
        emsg += '\n\tLevel: {0}'.format(level)
    # if we have args add them one by one as new lines to the message
    if args is not None:
        # if it is a list of args add them one by one
        if isinstance(args, list):
            for it, arg in enumerate(args):
                emsg += '\n\t Arg[{0}] = {1}'.format(it, arg)
        # else assume we have a string
        else:
            emsg += '\n\tArgs: {0}'.format(args)
    # add function name where error occurred too (if set)
    if func_name is not None:
        emsg += '\n\tFunction: {0}'.format(func_name)
    # return the error message
    return emsg


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
        return basiclogger(message=message, level=level, **kwargs)


def basiclogger(message: Union[str, None] = None,
                level: Union[str, None] = None,
                name: Union[str, None] = None, force_exit: bool = True,
                wlog: Any = None, **kwargs):
    """
    The basic logger (to emulate wlog)

    :param message: str, the message for the log
    :param level: str the level of the log (error/warning/info/ etc)
    :param name: str program/recipe name
    :param force_exit: bool, if True exit after logger (sys.exit)
    :param wlog: a drs_log.wlog instance (use this if present instead of the
                 basic logger)
    :param kwargs: passed to drs_log.wlog if present
    :return:
    """

    # check for wlog and use if available
    if wlog is not None:
        wlog(key=level, message=message, **kwargs)
        print_statement = False
    else:
        print_statement = True

    # deal with no name
    if name is None:
        name = __PACKAGE__.upper()
    # capitalize name
    name = name.capitalize()
    # deal with no level
    if level is None:
        level = 'error'
    # deal with message format (convert to TextEntry)
    if message is None:
        message = ['Unknown']
    elif type(message) is str:
        message = [message]
    elif type(message) is not list:
        basiclogger('Basic logger error. Cannot read message="{0}"'
                    ''.format(message), level='error')
    # deal with levels
    if level == 'error':
        do_exit = True
        key = '{0} - * |{1} Error| {2} '
    elif level == 'warning':
        do_exit = False
        key = '{0} - ! |{1} Warning| {2}'
    else:
        do_exit = False
        key = '{0} -   |{1} Log| {2}'
    # deal with printing log messages
    if print_statement:
        # get time
        atime = Time.now()
        htime = atime.iso.split(' ')[-1]
        # loop around message
        for mess in message:
            # print log message
            print(key.format(htime, name, mess))
    # deal with exiting
    if do_exit and force_exit:
        sys.exit()


def _flatmessage(message: Union[str, list, None]) -> str:
    """
    A flat version of the message (i.e. no tabs or new lines)

    :param message: str, the message to make flat
    :return:
    """
    # deal with message format (convert to TextEntry)
    if message is None:
        message = ['']
    elif type(message) is str:
        message = [message]
    elif type(message) is not list:
        message = ['']
    outstring = ''
    for mess in message:
        mess = mess.replace('\t', ' ')
        mess = mess.replace('\n', ' ')
        while '  ' in mess:
            mess = mess.replace('  ', ' ')
        outstring += mess
    return outstring


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
