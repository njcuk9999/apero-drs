#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-09-30 at 10:16

@author: cook

import rules:

only apero.base
"""
import logging
import os
import textwrap
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from apero.base import base
from apero.base import drs_lang
from apero.core.base import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.base.drs_log.py'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__author__
# no theme values
NO_THEME = [False, 'False', 'OFF', 'off', 'Off', 'None']
# General level
GENERAL = 15
# CACHE for all messages
CACHE = dict()
# Get astropy time from base module
Time = base.Time
# Get text entry
textentry = drs_lang.textentry
# Get exceptions
DrsLogException = drs_exceptions.DrsLogException
DrsCodedException = drs_exceptions.DrsCodedException
# Regular expression to match ANSI escape sequences
ANSI_ESCAPE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
# Define a default set of minimum params that are required for logging
DPARAMS = dict()
DPARAMS['DRS_DATA_MSG'] = base.get_default_log_dir()
DPARAMS['DRS_RECIPE_TYPE'] = 'default'
DPARAMS['DRS_LOG_CHAR_LEN'] = 80
DPARAMS['LOG_TRIG_KEYS'] = dict(all='  ', error='!!', warning='@@',
                               info='**', graph='~~', debug='++')
DPARAMS['WRITE_LEVELS'] = dict(error=3, warning=2, info=1,
                               graph=0, all=0, debug=0)
DPARAMS['REPORT_KEYS'] = dict(error=True, warning=True, info=False,
                              graph=False, all=False, debug=False)


# =============================================================================
# Define classes
# =============================================================================
class Log:
    """
    Log class to handle logging messages
    """
    def __init__(self, **kwargs):
        """
        Initialize the log class - overrides the logging module functionality
        """
        # get the logger
        self.logger = logging.getLogger(base.__package__)
        # set the default value to one below between INFO and DEBUG level
        self.baselevel = logging.DEBUG
        # define the levels
        self.INFO = logging.INFO
        self.WARNING = logging.WARNING
        # add a new level (GENERAL)
        self.GENERAL = GENERAL
        logging.addLevelName(self.GENERAL, 'GENERAL')
        # set logger to this as the lowest level
        self.logger.setLevel(self.baselevel)
        # set the log format
        self.theme = kwargs.get('theme', None)
        self.confmt = ConsoleFormat(theme=self.theme)
        self.filefmt = FileFormat(theme='OFF')
        self.console_handler = None
        self.file_handler = None
        # set program to None
        self.program = kwargs.get('program', None)
        self.code = kwargs.get('code', None)
        # save path
        self.filepath = None
        # add console
        self.console_verbosity = 2
        self._add_console(self.console_verbosity, level=self.GENERAL)
        # if we have a filename defined add a file logger
        if kwargs.get('filename', False):
            self.add_log_file(kwargs['filename'])

    def _add_console(self, verbose: int, level: int):
        # set console verbosity level
        self.console_verbosity = verbose
        # clean any handlers in logging currently
        for _ in range(len(self.logger.handlers)):
            self.logger.handlers.pop()
        # start the console log for debugging
        self.console_handler = logging.StreamHandler()
        # set the name (so we can access it later)
        self.console_handler.set_name('console')
        # set the format from console format
        self.console_handler.setFormatter(self.confmt)
        # set the default level (INFO)
        self.console_handler.setLevel(level)

    def _update_handles(self, verbose: int, level: int,
                        code: Union[str, None] = None,
                        program: Union[str, None] = None,
                        rmessage: Union[str, None] = None,
                        colour: Union[str, None] = None,
                        counter: int = 0,
                        to_console: bool = True,
                        to_file: bool = True):
        """
        Update the console

        :param verbose:
        :param level:
        :param program:
        :return:
        """
        # set console verbosity level
        self.console_verbosity = verbose
        self.program = program
        self.code = code
        # update console fmt
        self.confmt = ConsoleFormat(theme=self.theme, code=code,
                                    program=program, colour=colour,
                                    counter=counter)
        self.filefmt = FileFormat(theme='OFF', code=code, program=program,
                                  rmessage=rmessage)
        # clean any handlers in logging currently
        self.logger.handlers = []
        # deal with console
        if to_console:
            lhandler = self.console_handler
            if isinstance(lhandler, logging.StreamHandler):
                lhandler.setLevel(level)
            lhandler.setFormatter(self.confmt)
            self.logger.addHandler(lhandler)
        if to_file:
            lhandler = self.file_handler
            if isinstance(lhandler, logging.StreamHandler):
                lhandler.setLevel(level)
            lhandler.setFormatter(self.filefmt)
            self.logger.addHandler(lhandler)

    def add_log_file(self, filepath: str, level: Union[str, int, None] = None):
        """
        Updates the file_handler with the new file path and level

        :param filepath: str, the path to the log file
        :param level: str, int, None, the level to log at (default None)
        """
        # set file path
        self.filepath = filepath
        # get the File Handler
        self.file_handler = logging.FileHandler(str(filepath))
        # set the name (so we can access it later)
        self.file_handler.set_name('file')
        # set the log file format
        self.file_handler.setFormatter(self.filefmt)
        # if we have an integer just use it
        if isinstance(level, int):
            self.file_handler.setLevel(level)
        # set the level from level argument (using logging.{LEVEL}
        elif isinstance(level, str) and hasattr(logging, level):
            record = getattr(logging, level)
            self.file_handler.setLevel(record)
        # if it doesn't exist use the lowest level
        else:
            self.file_handler.setLevel(self.baselevel)

    def set_level(self, name: str = 'console',
                  level: Union[int, str, None] = 'DEBUG'):
        """
        Set the level of either "console" (for standard output) or "file"
        (for log file) - will print all messages at this level and above

        :param name: str, either "console" or "file" other names will do nothing
        :param level: str, int or None, the level to add if string must be
                      'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' if unset
                      does nothing
        :return:
        """
        # loop around all handlers
        for handler in self.logger.handlers:
            # get the name of this handler
            hname = handler.get_name()
            # if name matches with required name then update level
            if name.upper() == hname.upper():
                # if we have an integer level just use it
                if isinstance(level, int):
                    # update handler level
                    handler.setLevel(level)
                # if we have a level and it is valid update level
                elif level is not None and hasattr(logging, level):
                    # get level from logging
                    record = getattr(logging, level)
                    # update handler level
                    handler.setLevel(record)

    def general(self, message: str, *args,
                code: Union[str, None] = None,
                program: Union[str, None] = None,
                rmessage: Union[str, None] = None,
                colour: Union[str, None] = None,
                key: Union[str, None] = None,
                to_console: bool = True, to_file: bool = True,
                counter: int = 0, **kwargs):
        """
        Log a message at the GENERAL level

        :param message: str, the message to log
        :param args: list, the arguments passed to logger._log
        :param code: str, the code for the message
        :param program: str, the program for the message
        :param rmessage: str, the raw text code for the message (always with
                         text code)
        :param colour: str, overwrite the colour to print the message in
                       (None uses default for this level)
        :param key: str, the key level to store the message under in the cache
        :param to_console: bool, if True log to console
        :param to_file: bool, if True log to file
        :param kwargs: dict, the keyword arguments passed to logger._log

        :return: None
        """
        # update the handles with the properties from this call
        self.update_handles(self.console_verbosity, code, program,
                            rmessage, colour, to_console, to_file,
                            counter)
        # update cached log
        cache_logger(self.filepath, rmessage, code=self.code,
                     program=self.program, key=key)
        # noinspection PyProtectedMember
        self.logger._log(self.GENERAL, message, args, **kwargs)

    def debug(self, message: str, *args,
              code: Union[str, None] = None,
              program: Union[str, None] = None,
              rmessage: Union[str, None] = None,
              colour: Union[str, None] = None,
              key: Union[str, None] = None,
              to_console: bool = True, to_file: bool = True,
              counter: int = 0, **kwargs):
        """
        Log a message at the GENERAL level

        :param message: str, the message to log
        :param args: list, the arguments passed to logger._log
        :param code: str, the code for the message
        :param program: str, the program for the message
        :param rmessage: str, the raw text code for the message (always with
                         text code)
        :param colour: str, overwrite the colour to print the message in
                       (None uses default for this level)
        :param key: str, the key level to store the message under in the cache
        :param to_console: bool, if True log to console
        :param to_file: bool, if True log to file
        :param kwargs: dict, the keyword arguments passed to logger._log

        :return: None
        """
        # update the handles with the properties from this call
        self.update_handles(self.console_verbosity, code, program,
                            rmessage, colour, to_console, to_file,
                            counter)
        # update cached log
        cache_logger(self.filepath, rmessage, code=self.code,
                     program=self.program, key=key)
        # run logger
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args,
             code: Union[str, None] = None,
             program: Union[str, None] = None,
             rmessage: Union[str, None] = None,
             colour: Union[str, None] = None,
             key: Union[str, None] = None,
             to_console: bool = True, to_file: bool = True,
             counter: int = 0, **kwargs):
        """
        Log a message at the GENERAL level

        :param message: str, the message to log
        :param args: list, the arguments passed to logger._log
        :param code: str, the code for the message
        :param program: str, the program for the message
        :param rmessage: str, the raw text code for the message (always with
                         text code)
        :param colour: str, overwrite the colour to print the message in
                       (None uses default for this level)
        :param key: str, the key level to store the message under in the cache
        :param to_console: bool, if True log to console
        :param to_file: bool, if True log to file
        :param kwargs: dict, the keyword arguments passed to logger._log

        :return: None
        """
        # update the handles with the properties from this call
        self.update_handles(self.console_verbosity, code, program,
                            rmessage, colour, to_console, to_file,
                            counter)
        # update cached log
        cache_logger(self.filepath, rmessage, code=self.code,
                     program=self.program, key=key)
        # run logger
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args,
                code: Union[str, None] = None,
                program: Union[str, None] = None,
                rmessage: Union[str, None] = None,
                colour: Union[str, None] = None,
                key: Union[str, None] = None,
                to_console: bool = True, to_file: bool = True,
                counter: int = 0, **kwargs):
        """
        Log a message at the GENERAL level

        :param message: str, the message to log
        :param args: list, the arguments passed to logger._log
        :param code: str, the code for the message
        :param program: str, the program for the message
        :param rmessage: str, the raw text code for the message (always with
                         text code)
        :param colour: str, overwrite the colour to print the message in
                       (None uses default for this level)
        :param key: str, the key level to store the message under in the cache
        :param to_console: bool, if True log to console
        :param to_file: bool, if True log to file
        :param kwargs: dict, the keyword arguments passed to logger._log

        :return: None
        """
        # update the handles with the properties from this call
        self.update_handles(self.console_verbosity, code, program,
                            rmessage, colour, to_console, to_file,
                            counter)
        # update cached log
        cache_logger(self.filepath, rmessage, code=self.code,
                     program=self.program, key=key)
        # run logger
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args,
              code: Union[str, None] = None,
              program: Union[str, None] = None,
              rmessage: Union[str, None] = None,
              colour: Union[str, None] = None,
              key: Union[str, None] = None,
              to_console: bool = True, to_file: bool = True,
              counter: int = 0, **kwargs):
        """
        Log a message at the GENERAL level

        :param message: str, the message to log
        :param args: list, the arguments passed to logger._log
        :param code: str, the code for the message
        :param program: str, the program for the message
        :param rmessage: str, the raw text code for the message (always with
                         text code)
        :param colour: str, overwrite the colour to print the message in
                       (None uses default for this level)
        :param key: str, the key level to store the message under in the cache
        :param to_console: bool, if True log to console
        :param to_file: bool, if True log to file
        :param kwargs: dict, the keyword arguments passed to logger._log

        :return: None
        """
        # update the handles with the properties from this call
        self.update_handles(self.console_verbosity, code, program,
                            rmessage, colour, to_console, to_file,
                            counter)
        # update cached log
        cache_logger(self.filepath, rmessage, code=self.code,
                     program=self.program, key=key)
        # run logger
        self.logger.error(message, *args, **kwargs)

    def update_handles(self, verbose: int = 2,
                       code: Union[str, None] = None,
                       program: Union[str, None] = None,
                       rmessage: Union[str, None] = None,
                       colour: Union[str, None] = None,
                       to_console: bool = True,
                       to_file: bool = True, counter: int = 0):
        """
        Update the text printed to console
            0=only warnings/errors
            1=info/warnings/errors,'
            2=general/info/warning/errors

        :param verbose: int, either 0, 1, 2 see above for definition
        :param code: str, if set changes the code message (default None)
        :param program: str, if set changes the program message (default None)
        :param rmessage: str, if set changes the raw message (default None)
        :param colour: str, if set changes the colour of the message
        (default None)
        :param to_console: bool, if True log to console
        :param to_file: bool, if True log to file

        :return: None, updates consolehandler
        """
        if verbose == 2:
            # set the default console level to GENERAL
            self._update_handles(verbose, self.GENERAL, code, program,
                                 rmessage, colour, counter,
                                 to_console=to_console, to_file=to_file)
        elif verbose == 1:
            # set the default console level to INFO
            self._update_handles(verbose, self.INFO, code, program,
                                 rmessage, colour, counter,
                                 to_console=to_console, to_file=to_file)
        elif verbose == 0:
            # set the default console level to WARNING
            self._update_handles(verbose, self.WARNING, code, program,
                                 rmessage, colour, counter,
                                 to_console=to_console, to_file=to_file)
        else:
            # set the default console level to GENERAL
            self._update_handles(verbose, self.GENERAL, code, program,
                                 rmessage, colour, counter,
                                 to_console=to_console, to_file=to_file)

    @staticmethod
    def get_cache() -> List[str]:
        """
        Get the cached log messages

        :return: list of str, the cached log messages
        """
        # copy cache to local variable
        cache = []
        for record in CACHE:
            cache.append(str(record))
        # return cache
        return cache


# Custom formatter
class ConsoleFormat(logging.Formatter):
    """
    Custom formatter for console output
    """
    def __init__(self, fmt: str = "%(levelno)s: %(msg)s", theme=None,
                 code: Union[str, None] = None,
                 program: Union[str, None] = None,
                 colour: Union[str, None] = None,
                 counter: int = 0):
        """
        Initialize the formatter

        :param fmt: str, the format string
        :param theme: str, the theme to use
        :param code: str, the code to use
        :param program: str, the program to use
        :param colour: str, the colour to use
        """
        # get colours
        self.cprint = Colors(theme=theme, override=colour)
        # define default format
        if program is None:
            program = ''
        if code is None:
            code = ' '
        # coounter changes how we display to the console
        if counter == 0:
            self.fmt = '%(asctime)s.%(msecs)03d|'
            self.fmt += f'{code}|{program}| %(message)s'
        else:
            self.fmt = '  L %(message)s'
        # set this as the default logging format
        self.default = logging.Formatter(self.fmt, datefmt='%Y-%m-%d %H:%M:%S')
        # define empty format
        self.empty_fmt = '%(message)s'
        # define debug format
        self.debug_fmt = self.cprint.debug + self.fmt + self.cprint.endc
        # add a new level (GENERAL)
        self.GENERAL = 15
        self.general_fmt = self.cprint.okgreen + self.fmt + self.cprint.endc
        # define info format
        self.info_fmt = self.cprint.okblue + self.fmt + self.cprint.endc
        # define warning format
        self.warning_fmt = self.cprint.warning + self.fmt + self.cprint.endc
        # define error format
        self.error_fmt = self.cprint.fail + self.fmt + self.cprint.endc
        # define critical format
        self.critial_fmt = self.cprint.fail + self.fmt + self.cprint.endc
        # initialize parent
        logging.Formatter.__init__(self, fmt, datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record):
        """
        Format the record (using the level to determine the format)

        :param record: the record to format

        :return: the formatted record
        """
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        # noinspection PyProtectedMember
        format_orig = self._style._fmt
        # Replace the original format with one customized by logging level
        if record.levelno < logging.INFO:
            self._style._fmt = self.debug_fmt
        if record.levelno == self.GENERAL:
            self._style._fmt = self.general_fmt
        elif record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt
        elif record.levelno == logging.WARNING:
            self._style._fmt = self.warning_fmt
        elif record.levelno >= logging.ERROR and record.levelno != 999:
            self._style._fmt = self.error_fmt
        elif record.levelno == 999:
            self._style._fmt = self.empty_fmt
        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
        logging.Formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result


class FileFormat(logging.Formatter):
    """
    Custom formatter for file output
    """
    def __init__(self, fmt: str = "%(levelno)s: %(msg)s", theme=None,
                 code: Union[str, None] = None,
                 program: Union[str, None] = None,
                 rmessage: Union[str, None] = None):
        """
        Initialize the formatter for log file output

        :param fmt: str, the format string
        :param theme: str, the theme to use
        :param code: str, the code to use
        :param program: str, the program to use
        :param rmessage: str, the raw message to use

        :return: None
        """
        # we don't use the theme for file format
        _ = theme
        # define default format
        if program is None:
            program = ''
        if code is None:
            code = ' '
        self.fmt = '%(asctime)s.%(msecs)03d|'
        # push code/program/re
        if rmessage is not None and len(rmessage) > 0:
            self.fmt += f'{code}|{program}| {rmessage}'
        else:
            self.fmt += f'{code}|{program}| %(message)s'
        # set this as the default logging format
        self.default = logging.Formatter(self.fmt, datefmt='%Y-%m-%d %H:%M:%S')
        # define empty format
        self.empty_fmt = '%(message)s'
        # define debug format
        self.debug_fmt = self.fmt
        # add a new level (GENERAL)
        self.GENERAL = 15
        self.general_fmt = self.fmt
        # define info format
        self.info_fmt = self.fmt
        # define warning format
        self.warning_fmt = self.fmt
        # define error format
        self.error_fmt = self.fmt
        # define critical format
        self.critial_fmt = self.fmt
        # initialize parent
        logging.Formatter.__init__(self, fmt, datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record):
        """
        Format the record (using the level to determine the format)
        """
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        # noinspection PyProtectedMember
        format_orig = self._style._fmt
        # Replace the original format with one customized by logging level
        if record.levelno < logging.INFO:
            self._style._fmt = self.debug_fmt
        if record.levelno == self.GENERAL:
            self._style._fmt = self.general_fmt
        elif record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt
        elif record.levelno == logging.WARNING:
            self._style._fmt = self.warning_fmt
        elif record.levelno >= logging.ERROR and record.levelno != 999:
            self._style._fmt = self.error_fmt
        elif record.levelno == 999:
            self._style._fmt = self.empty_fmt
        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
        logging.Formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result


# Color class
class Colors:
    """
    Class to handle color printing
    """
    BLACK1 = '\033[90;1m'
    RED1 = '\033[1;91;1m'
    GREEN1 = '\033[92;1m'
    YELLOW1 = '\033[1;93;1m'
    BLUE1 = '\033[94;1m'
    MAGENTA1 = '\033[1;95;1m'
    CYAN1 = '\033[1;96;1m'
    WHITE1 = '\033[97;1m'
    BLACK2 = '\033[1;30m'
    RED2 = '\033[1;31m'
    GREEN2 = '\033[1;32m'
    YELLOW2 = '\033[1;33m'
    BLUE2 = '\033[1;34m'
    MAGENTA2 = '\033[1;35m'
    CYAN2 = '\033[1;36m'
    WHITE2 = '\033[1;37m'
    ENDC = '\033[0;0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    endc: str = ENDC
    bold: str = None
    underline: str = None
    header: str = None
    okblue: str = None
    okgreen: str = None
    ok: str = None
    warning: str = None
    fail: str = None
    debug: str = None

    def __init__(self, theme: Union[str, None] = None,
                 override: Union[str, None] = None):
        """
        Initialize the color class
        """
        # set theme if not given
        if theme is None:
            self.theme = 'DARK'
        else:
            self.theme = theme
        # update the attributes based on theme choice
        self.update_theme(override=override)

    def update_theme(self, theme: Union[str, None] = None,
                     override: Union[str, None] = None):
        """
        Update the attributes based on theme choice
        """
        # deal with setting the colour from override
        if override is not None:
            override = self.get_colour(override)
            self.header = override
            self.okblue = override
            self.okgreen = override
            self.ok = override
            self.warning = override
            self.fail = override
            self.debug = override
            return
        # deal with no theme from call
        if theme is not None:
            self.theme = theme
        # if theme is dark set all to dark
        if self.theme == 'DARK':
            self.header = self.MAGENTA1
            self.okblue = self.BLUE1
            self.okgreen = self.GREEN1
            self.ok = self.MAGENTA2
            self.warning = self.YELLOW1
            self.fail = self.RED1
            self.debug = self.BLACK1
            return
        # if there is no theme given set all to override
        elif self.theme in NO_THEME:
            self.header = ''
            self.okblue = ''
            self.okgreen = ''
            self.ok = ''
            self.warning = ''
            self.fail = ''
            self.debug = ''
            return
        # if we get here we use the default theme
        self.header = self.MAGENTA2
        self.okblue = self.MAGENTA2
        self.okgreen = self.BLACK2
        self.ok = self.MAGENTA2
        self.warning = self.BLUE2
        self.fail = self.RED2
        self.debug = self.GREEN2

    def get_colour(self, colour: Union[str, None] = None) -> str:
        """
        Get the colour code for a given colour string

        :param colour: str, the colour to get the code for

        :return: str, the colour code
        """
        if colour in ['b', 'blue']:
            start = self.BLUE1
        elif colour in ['r', 'red']:
            start = self.RED1
        elif colour in ['g', 'green']:
            start = self.GREEN1
        elif colour in ['y', 'yellow']:
            start = self.YELLOW1
        elif colour in ['m', 'magenta']:
            start = self.MAGENTA1
        elif colour in ['k', 'black', 'grey']:
            start = self.BLACK1
        else:
            start = self.endc
        return start

    def print(self, message: str, colour: Union[str, None] = None):
        """
        Get a string representaion of a message in a given colour

        :param message: str, the message to print
        :param colour: str, the colour to print the message in

        :return: str, the message in the given colour
        """
        # get start colour
        start = self.get_colour(colour)
        # return colour mesage
        return start + message + self.endc


class Wlog:
    """
    Wlog class to handle logging messages from the code - and storing the
    log classes so we don't create them multiple times
    """
    log_classes = dict()

    def __call__(self, params: Any = None, key: str = '',
                 message: Union[drs_lang.Text, str, None] = None,
                 printonly: bool = False, logonly: bool = False,
                 wrap: bool = True, option: str = None, colour: str = None,
                 raise_exception: bool = True, sublevel: Optional[int] = None):
        """
        Main function to log messages from the code
        """
        # get the logger instance
        log = self.get_log(params)
        # ---------------------------------------------------------------------
        # deal with sub level
        if sublevel is not None:
            if sublevel <= 0:
                sublevel = 0
            elif sublevel > 10:
                sublevel = 9
        # ---------------------------------------------------------------------
        # get messages
        fmsg = format_message(params, key, message, option, sublevel, wrap)
        messages1, code, option, messages2 = fmsg
        # ---------------------------------------------------------------------
        # deal with print and log only
        if printonly:
            to_console, to_file = True, False
        elif logonly:
            to_console, to_file = False, True
        else:
            to_console, to_file = True, True
        # ---------------------------------------------------------------------
        # keep counter on messages
        counter = 0
        # loop around message and log them
        for message1, message2 in zip(messages1, messages2):
            log_kwargs = dict(message=message1, code=code, program=option,
                              to_console=to_console, to_file=to_file,
                              rmessage=message2, colour=colour, key=key,
                              counter=counter)
            # log at the correct level
            if key == 'info':
                log.info(**log_kwargs)
            elif key == 'warning':
                log.warning(**log_kwargs)
            elif key == 'error':
                log.error(**log_kwargs)
                # only raise exception if raise_exception is True
                if raise_exception:
                    raise DrsCodedException(message2)
            elif key == 'general':
                log.general(**log_kwargs)
            elif key == 'debug':
                log.debug(**log_kwargs)
            else:
                log.general(**log_kwargs)
            # increment counter
            counter += 1

    def get_log(self, params: Any) -> Log:
        """
        Get the log class for a given set of parameters

        :param params: Any, the parameters to get the log class for
        """
        # ---------------------------------------------------------------------
        # deal with params not being set
        if params is None:
            params = DPARAMS
        # ---------------------------------------------------------------------
        # get logfilepath
        logfilepath = get_logfilepath(params)
        # ---------------------------------------------------------------------
        # if we have a log class for this logfilepath use it
        if logfilepath in self.log_classes:
            log = self.log_classes[logfilepath]
        else:
            # create new log
            log = Log(filename=logfilepath)
            self.log_classes[logfilepath] = log
        # return the log
        return log

    def output_param_dict(self, params: Any) -> Dict[str, List[str]]:
        """
        Push the LOG_STORAGE_KEYS into a parameter dictionary (either new
        if new = True or self.pout otherwise and return it

        :param params: ParamDict, the current constants parameter dictionary

        :return: A dictionary of log files, taken from the cache
        """
        # get the log
        log = self.get_log(params)
        # storage
        storage = dict()
        # loop around all keys
        for key in params['LOG_STORAGE_KEYS']:
            # get the storage value
            storekey = params['LOG_STORAGE_KEYS'][key]
            # get entries
            if key not in CACHE[log.filepath]:
                entries = []
            else:
                entries = CACHE[log.filepath][key]
            # push into params
            storage[storekey] = list(entries)
        # return all these log files
        return storage

    def logger_storage(self, params: Any, key: str, ttime: str,
                       message: str, program: str):
        # get the log
        log = self.get_log(params)
        # push to cache
        cache_logger(log.filepath, message, code=key, timestr=ttime,
                     key=key, program=program)

    def clean_log(self, params: Any = None):
        # get the log
        log = self.get_log(params)
        # clear this cache
        CACHE[log.filepath] = dict()


class AperoCodedException(DrsCodedException):
    """
    AperoCodedException: Exception class for APERO
    """
    wlog = Wlog()

    def __init__(self, params: Any = None,
                 code: Union[str, None] = None,
                 message: Union[str, None] = None,
                 targs: Union[list, None] = None):
        """
        Initialize the exception

        :param params: Any, the parameters to get the log class for
        :param code: str, the code for the message
        :param message: str, the message to log
        :param targs: list, the arguments to pass to the message

        :return: None
        """
        # set the default path
        self.default_path = base.DEFAULT_LOG_PATH
        # set code
        self.code = code
        # set targs
        self.targs = targs
        # if we have a code
        if self.code is not None and self.message is None:
            # set code
            self.code = code
            # set the message from the code
            self.message = drs_lang.textentry(self.code, targs)
        elif self.code is not None:
            # set code
            self.code = code
            # otherwise use the message
            self.message = drs_lang.textentry(self.message, targs)
        else:
            # otherwise use the message
            self.message = message
        # deal with no params
        if params is None:
            self.params = DPARAMS
        else:
            self.params = params

    def __str__(self):
        """
        The string representation of the error: used as message when raised
        :return:
        """
        # log the error to the log file
        self.wlog(self.params, 'error', self.message, logonly=True,
                  raise_exception=False)
        # return the message as the string (for the raise)
        if self.message is None:
            message = drs_lang.textentry(self.code, self.targs)
        else:
            message = self.message
        # return the base printer version string represntation
        return str(message)


class AperoCodedWarning():
    """
    AperoCodedException: Exception class for APERO
    """
    wlog = Wlog()

    def __init__(self, params: Any = None,
                 code: Union[str, None] = None,
                 message: Union[str, None] = None,
                 targs: Union[list, None] = None,
                 sublevel: Optional[int] = None):
        """
        Initialize the exception

        :param params: Any, the parameters to get the log class for
        :param code: str, the code for the message
        :param message: str, the message to log
        :param targs: list, the arguments to pass to the message

        :return: None
        """
        # set the default path
        self.default_path = base.DEFAULT_LOG_PATH
        # set code
        self.code = code
        self.targs = targs
        # set the sublevel
        self.sublevel = sublevel
        # if we have a code
        if self.code is not None:
            # set code
            self.code = code
            # set the message from the code
            self.message = drs_lang.textentry(self.code, targs)
        else:
            # otherwise use the message
            self.message = message
        # deal with no params
        if params is None:
            self.params = DPARAMS
        else:
            self.params = params
        # log the error to the log file
        self.wlog(self.params, 'warning', self.message,
                  sublevel=self.sublevel)


# =============================================================================
# Define functions
# =============================================================================
def cache_logger(filepath: str, message: str, code: Union[str, None] = None,
                 program: Union[str, None] = None,
                 key: Union[str, None] = None,
                 timestr: Union[str, None] = None):
    """
    Store message formated properly to cache (for return to lbl code)

    :param filepath: str, the path to the log file
    :param message: str, the log message to store
    :param code: str or None, if set the code id
    :param program: str or None, if set the program id

    :return: None, updates CACHE
    """
    # need to global edit cache
    global CACHE
    # get time now
    if timestr is None:
        timestr = Time.now().iso
    # -------------------------------------------------------------------------
    if program is not None:
        record = f'{timestr}|{code}|{program}| {message}'
    else:
        record = f'{timestr}|{code}|{program}| {message}'
    # -------------------------------------------------------------------------
    # push to cache
    if filepath not in CACHE:
        # deal with no file path
        CACHE[filepath] = dict()
    # -------------------------------------------------------------------------
    # deal with a new key (not previously in cache)
    if key not in CACHE[filepath]:
        CACHE[filepath][key] = [record]
    # add to existing key
    else:
        CACHE[filepath][key].append(record)


def get_logfilepath(params: Any, use_group: bool = True) -> str:
    """
    Construct the log file path and filename (normally from "DRS_DATA_MSG"
    generates an DrsCodedException exception.

    "DRS_DATA_MSG" is defined in "config.py"

    :param params: Parameter dictionary of constants
    :param use_group: bool if True use group name in log file path

    :return lpath: string, the path and filename for the log file to be used
    :return warning: bool, if True print warnings about log file path
    """
    # -------------------------------------------------------------------------
    # deal with group
    if not use_group:
        group = None
        reset = True
    elif 'DRS_GROUP_PATH' in params:
        group = params['DRS_GROUP_PATH']
        reset = False
    else:
        group = None
        reset = False
    # -------------------------------------------------------------------------
    # get dir_data_msg key
    dir_data_msg = get_drs_data_msg(params, group, reset=reset)
    # -------------------------------------------------------------------------
    # add log file to path
    lpath = get_drs_filename(params, dir_data_msg)
    # return the logpath and the warning
    return lpath


def get_drs_filename(params: Any, dir_data_msg: Union[str, None] = None
                     ) -> str:
    """
    Get the drs message filename (from params)

    :param params: ParamDict, the parameter dictionary of constants
    :param dir_data_msg: str, the directory to store the log file in

    :return: str, the log file path
    """
    if dir_data_msg is None:
        dir_data_msg = str(params['DRS_DATA_MSG'])
    # deal with no PID
    if 'PID' not in params:
        pid = 'UNKNOWN-PID'
    else:
        pid = str(params['PID'])
    # deal with no recipe
    if 'RECIPE' not in params:
        recipe = 'UNKNOWN-RECIPE'
    else:
        recipe = str(params['RECIPE'].replace('.py', ''))
    # construct the logfile path
    largs = [pid, recipe]
    lpath = os.path.join(dir_data_msg, 'APEROL-{0}_{1}.log'.format(*largs))
    # return the log path
    return str(lpath)


def get_drs_data_msg(params: Any, group: Union[str, None] = None,
                     reset: bool = False) -> str:
    """
    Get the drs message full path (either from existing one, or create one
    using group name)

    :param params: ParamDict, the parameter dictionary of constants
    :param group: str, the group name (if set)
    :param reset: bool, if True recalculates drs message full path

    :return: str, the drs message full path
    """
    # if we have a full path in params we use this
    if 'DRS_DATA_MSG_FULL' in params and not reset:
        # check that path exists - if it does skip next steps
        if params['DRS_DATA_MSG_FULL'] is None:
            pass
        elif os.path.exists(params['DRS_DATA_MSG_FULL']):
            return params['DRS_DATA_MSG_FULL']
    # ----------------------------------------------------------------------
    # get from params
    dir_data_msg = params.get('DRS_DATA_MSG', None)
    # ----------------------------------------------------------------------
    # only sort by recipe kind if group is None
    if (params['DRS_RECIPE_TYPE'] is not None) and (group is None):
        kind = params['DRS_RECIPE_TYPE'].lower()
        dir_data_msg = os.path.join(dir_data_msg, kind)
    # if we have a group (and we are dealing with a recipe called within
    #    another then put it in processing folder
    elif group is not None and params['DRS_RECIPE_TYPE'] == 'sub-recipe':
        dir_data_msg = os.path.join(dir_data_msg, 'sub-recipe')
    # if we have a group (and we are not dealing with a recipe called within
    #    another then put it in processing folder
    elif group is not None:
        dir_data_msg = os.path.join(dir_data_msg, 'processing')
    # otherwise shove into an "other" directory
    else:
        dir_data_msg = os.path.join(dir_data_msg, 'other')
    # ----------------------------------------------------------------------
    # deal with a group directory (groups must be in sub-directory)
    if (group is not None) and (dir_data_msg is not None):
        # join to group name
        dir_data_msg = os.path.join(str(dir_data_msg), group)
    # ----------------------------------------------------------------------
    # add night name dir (if available) - put into sub-directory
    if ('OBS_SUBDIR' in params) and (dir_data_msg is not None):
        obs_subdir = params['OBS_SUBDIR']
        # only add sub-directory if not None
        if str(obs_subdir).upper() not in ['NONE', 'NULL', '']:
            # only add sub-directory if sub-directory not in the log path
            #   already
            if obs_subdir not in dir_data_msg:
                dir_data_msg = os.path.join(dir_data_msg, obs_subdir)
    # ----------------------------------------------------------------------
    # try to create directory
    if not os.path.exists(dir_data_msg):
        # noinspection PyBroadException
        try:
            os.makedirs(dir_data_msg)
        except Exception as _:
            pass
    # ----------------------------------------------------------------------
    # if None use we have to create it
    if dir_data_msg is None:
        # create default path
        create = True
    # if it doesn't exist we also have to create it
    elif not os.path.exists(dir_data_msg):
        # create default path
        create = True
    else:
        return dir_data_msg
    # ----------------------------------------------------------------------
    # if we have reached here then we need to create a default drs_data_msg
    if create:
        # get the users home directory
        homedir = os.path.expanduser('~')
        # make the default message directory
        default_msg = os.path.join(homedir, '.apero/msg/')
        # check that deafult message directory exists
        if not os.path.exists(default_msg):
            # noinspection PyBroadException
            try:
                os.makedirs(default_msg)
                return default_msg
            except Exception as _:
                return './'
        else:
            return default_msg


def format_message(params: Any, key: str,
                   message: Union[drs_lang.Text, str, None],
                   option: Union[str, None],
                   sublevel: Union[int, None],
                   wrap: bool = True
                   ) -> Tuple[List[str], str, str, List[str]]:
    """
    Format the message for the log file

    :param params: ParamDict, the parameter dictionary of constants
    :param key: str, the key (level) for the message
    :param message: Union[drs_lang.Text, str, None], the message to log (can be
                    a string or a drs_lang.Text object)
    :param option: Union[str, None], the option for the message
    :param sublevel: Union[str, None], the sublevel of the message
    :param wrap: bool, if True wrap the message to the log width

    :return: tuple, 1. list of str messages formatted for log file,
                    2. the code for the message,
                    3. the option for the
                    4. the list of str messages with text code
    """
    # -------------------------------------------------------------------------
    # deal with message format (convert to drs_lang.Text)
    if message is None:
        msg_obj = textentry('Unknown')
    elif isinstance(message, drs_lang.Text):
        msg_obj = message
    elif isinstance(message, str):
        msg_obj = textentry(message)
    elif isinstance(message, list):
        msg_obj = textentry(message[0])
        for msg in message[1:]:
            msg_obj += textentry(msg)
    else:
        raise DrsLogException(textentry('00-005-00001', args=[message]))
    # -------------------------------------------------------------------------
    # deal with text wrapping
    if wrap:
        msg_string = msg_obj.tvalue.split('\n')
        # loop around these lines
        for it, msg in enumerate(msg_string):
            msg_string[it] = textwrap.fill(msg,
                                           width=params['DRS_LOG_CHAR_LEN'],
                                           break_long_words=False,
                                           break_on_hyphens=False)
        msg_obj.tvalue = '\n'.join(msg_string)
    # -------------------------------------------------------------------------
    # strip white spaces
    msg_obj.tvalue = msg_obj.tvalue.strip()
    # -------------------------------------------------------------------------
    # if key is '' then set it to all
    if len(key) == 0:
        key = 'all'
    # check for key in various levels (give error if not)
    if key not in params['LOG_TRIG_KEYS']:
        eargs = [key, 'LOG_TRIG_KEYS']
        raise DrsLogException(textentry('00-005-00002', args=eargs))
    if key not in params['WRITE_LEVELS']:
        eargs = [key, 'WRITE_LEVELS']
        raise DrsLogException(textentry('00-005-00003', args=eargs))
    if key not in params['REPORT_KEYS']:
        eargs = [key, 'REPORT_KEYS']
        raise DrsLogException(textentry('00-005-00005', args=eargs))
    # ---------------------------------------------------------------------
    # deal with option
    if option is not None:
        option = option
    elif 'RECIPE_SHORT' in params:
        option = str(params.get('RECIPE_SHORT', ''))
    elif 'RECIPE' in params:
        option = str(params.get('RECIPE', ''))
    else:
        option = ''
    # overwrite these with DRS_USER_PROGRAM (if not None)
    userprogram = str(params.get('DRS_USER_PROGRAM', None))
    if userprogram != 'None':
        option = userprogram
    # -------------------------------------------------------------------------
    # deal with report level
    report = params['REPORT_KEYS'][key]
    # -------------------------------------------------------------------------
    # deal with code level
    code = params['LOG_TRIG_KEYS'][key]
    # deal with code-sublevel
    if sublevel is None:
        pass
    elif sublevel <= params['DRS_LOG_SUBLEVEL_DIV']:
        code = code + params['DRS_LOG_SUBLEVEL_DIV_CHAR']['LOW']
    else:
        code = code + params['DRS_LOG_SUBLEVEL_DIV_CHAR']['HIGH']
    # -------------------------------------------------------------------------
    # get messages
    if isinstance(msg_obj, drs_lang.Text):
        raw_messages1 = msg_obj.get_text(report=report, reportlevel=key)
        raw_messages2 = msg_obj.get_text(report=True, reportlevel=key)
        # raw messages 2 are just for the log - no colour
        raw_messages2 = _clean_message(raw_messages2)
    else:
        raw_messages1 = str(msg_obj)
        raw_messages2 = str(msg_obj)
    # -------------------------------------------------------------------------
    # logger can't have % - replace with unicode
    raw_messages1 = raw_messages1.replace('%', '\u066A')
    raw_messages2 = raw_messages2.replace('%', '\u066A')
    # -------------------------------------------------------------------------
    # split by '\n' to create list of messages
    raw_messages1 = raw_messages1.split('\n')
    raw_messages2 = raw_messages2.split('\n')
    # -------------------------------------------------------------------------
    # if we have mutiple messages add a blank one first
    if len(raw_messages1) > 1:
        raw_messages1.insert(0, '')
        raw_messages2.insert(0, '')
    # -------------------------------------------------------------------------
    # return the raw messages and the code
    return raw_messages1, code, option, raw_messages2


def _clean_message(message: str) -> str:
    """
    Remove colours from a message

    :param message: str, message to clean

    :return: str, cleaned message
    """
    # Strip ANSI escape sequences from the message
    message = ANSI_ESCAPE.sub('', message)
    # return message
    return message


# =============================================================================
# Activate Wlog (only need one)
# =============================================================================
wlog = Wlog()


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
