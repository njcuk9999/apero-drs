#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-24 at 16:33

@author: cook
"""
from astropy.time import Time
import sys


# =============================================================================
# Define variables
# =============================================================================
# Define package name
PACKAGE = 'apero'
# track used warnings
USED_TEXT_WARNINGS = []
USED_DRS_WARNINGS = []
USED_CONFIG_WARNINGS = []
# -----------------------------------------------------------------------------

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

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
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

    def __str__(self):
        return _flatmessage(self.message)


class TextWarning:
    global USED_TEXT_WARNINGS

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):
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


class DrsException(Exception):
    """Raised when config file is incorrect"""
    pass


class DrsError(DrsException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):
        """
        Constructor for DRSError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
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

    def __str__(self):
        return _flatmessage(self.message)


class DrsHeaderError(DrsException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None, key=None, filename=None):
        """
        Constructor for DRSError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        """
        # deal with errorobj
        if errorobj is not None:
            message = errorobj[0].get(errorobj[1], report=True)
            message = message.split('\n')
            level = 'error'
        # get key and filename
        self.key = key
        self.filename = filename
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

    def __str__(self):
        return _flatmessage(self.message)



class DrsWarning:
    global USED_DRS_WARNINGS

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):

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


class ConfigException(Exception):
    """Raised when config file is incorrect"""
    pass


class ConfigError(ConfigException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
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

    def __str__(self):
        return _flatmessage(self.message)


class ConfigWarning:
    global USED_CONFIG_WARNINGS

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):

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


class ArgumentException(Exception):
    """Raised when config file is incorrect"""
    pass


class ArgumentError(ArgumentException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
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

    def __str__(self):
        return  _flatmessage(self.message)


class ArgumentWarning:
    global USED_CONFIG_WARNINGS

    def __init__(self, message=None, level=None, wlog=None, kwargs=None,
                 errorobj=None):

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


class Exit(SystemExit):
    """Raised when exit is called"""
    pass


class LogExit(Exit):
    """
    This should only be used when exiting from a log message
    """
    def __init__(self, errormessage, *args, **kwargs):
        self.errormessage = errormessage
        super().__init__(*args, **kwargs)


class DebugExit(Exit):
    """
    This exception should only be used when exiting the debugger (ipdb/pdb)
    """
    def __init__(self, errormessage, *args, **kwargs):
        self.errormessage = errormessage
        super().__init__(*args, **kwargs)


# =============================================================================
# Define functions
# =============================================================================
# define a function to clear out warnings (for exit script)
def clear_warnings():
    global USED_TEXT_WARNINGS
    global USED_DRS_WARNINGS
    global USED_CONFIG_WARNINGS

    USED_TEXT_WARNINGS = []
    USED_DRS_WARNINGS = []
    USED_CONFIG_WARNINGS = []


# Define basic log function (for when we don't have full logger functionality)
#   i.e. within apero.lang or apero.constants
#   Note this can't be language specific=
def wlogbasic(_, level, message, **kwargs):
    if level == 'debug':
        return None
    else:
        return basiclogger(message=message, level=level, **kwargs)


def basiclogger(message=None, level=None, name=None, force_exit=True,
                wlog=None, **kwargs):

    # check for wlog and use if available
    if wlog is not None:
        wlog(key=level, message=message, **kwargs)
        print_statement = False
    else:
        print_statement = True

    # deal with no name
    if name is None:
        name = PACKAGE.upper()
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
        exit = True
        key = '{0} - * |{1} Error| {2} '
    elif level == 'warning':
        exit = False
        key = '{0} - ! |{1} Warning| {2}'
    else:
        exit = False
        key = '{0} -   |{1} Log| {2}'
    # deal with printing log messages
    if print_statement:
        # get time
        # TODO: first time Time.now is done it takes a very long time
        atime = Time.now()
        htime = atime.iso.split(' ')[-1]
        # loop around message
        for mess in message:
            # print log message
            print(key.format(htime, name, mess))
    # deal with exiting
    if exit and force_exit:
        sys.exit()


def _flatmessage(message):

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
