#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-21 19:17

@author: cook

import rules

only from
- apero.base.*
- apero.lang.*
- apero.core.core.drs_break
- apero.core.core.drs_exceptions
"""
import numpy as np
import os
from pathlib import Path
import random
import string
import time
from typing import Any, Union, Tuple

from apero import lang
from apero.base import base
from apero.base import drs_base


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
textentry = lang.textentry


# =============================================================================
# Basic logging functions
# =============================================================================
class Colors:
    def __init__(self, theme: Union[str, None] = None):
        """
        Constructor of the colour class (colours based on theme)
        :param theme: str, if set sets the theme ('DARK' or 'LIGHT') defaults
                      to 'DARK'
        """
        # Basic definition of colours to use in log to screen
        self.BLACK1 = base.COLOURS['BLACK1']
        self.RED1 = base.COLOURS['RED1']
        self.GREEN1 = base.COLOURS['GREEN1']
        self.YELLOW1 = base.COLOURS['YELLOW1']
        self.BLUE1 = base.COLOURS['BLUE1']
        self.MAGENTA1 = base.COLOURS['MAGENTA1']
        self.CYAN1 = base.COLOURS['CYAN1']
        self.WHITE1 = base.COLOURS['WHITE1']
        self.BLACK2 = base.COLOURS['BLACK2']
        self.RED2 = base.COLOURS['RED2']
        self.GREEN2 = base.COLOURS['GREEN2']
        self.YELLOW2 = base.COLOURS['YELLOW2']
        self.BLUE2 = base.COLOURS['BLUE2']
        self.MAGENTA2 = base.COLOURS['MAGENTA2']
        self.CYAN2 = base.COLOURS['CYAN2']
        self.WHITE2 = base.COLOURS['WHITE2']
        self.ENDC = base.COLOURS['ENDC']
        self.BOLD = base.COLOURS['BOLD']
        self.UNDERLINE = base.COLOURS['UNDERLINE']
        # if we have no theme set - set the default
        if theme is None:
            self.theme = 'DARK'
        # if anything else set the theme to them
        else:
            self.theme = theme
        # get inital definitions of themed objects
        self.header = self.MAGENTA1
        self.okblue = self.BLUE1
        self.okgreen = self.GREEN1
        self.ok = self.MAGENTA2
        self.warning = self.YELLOW1
        self.fail = self.RED1
        self.debug = self.BLACK1
        # define the end of string code (block to reset)
        self.endc = self.ENDC
        # define the bold string code
        self.bold = self.BOLD
        # define the underline string code
        self.underline = self.UNDERLINE
        # update all others via theme
        self.update_theme()

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

    def __str__(self) -> str:
        """
        Return string represenation of Const class
        :return:
        """
        return 'Colors[{0}]'.format(self.theme)

    def update_theme(self, theme: Union[str, None] = None):
        """
        Update themed object names
            header/okblue/okgreen/ok/warning/fail/debug
        based on theme

        :param theme: str, if set sets the theme ('DARK' or 'LIGHT') defaults
                      to 'DARK'
        :return:
        """
        # if we have no theme set - set the default
        if theme is not None:
            self.theme = theme
        # set the dark colours
        if self.theme == 'DARK':
            self.header = self.MAGENTA1
            self.okblue = self.BLUE1
            self.okgreen = self.GREEN1
            self.ok = self.MAGENTA2
            self.warning = self.YELLOW1
            self.fail = self.RED1
            self.debug = self.BLACK1
        # set the light colours
        else:
            self.header = self.MAGENTA2
            self.okblue = self.MAGENTA2
            self.okgreen = self.BLACK2
            self.ok = self.MAGENTA2
            self.warning = self.BLUE2
            self.fail = self.RED2
            self.debug = self.GREEN2

    def print(self, message: str, colour: str) -> str:
        """
        A basic coloured print mesage
        If colour is incorrect does nothing

        :param message: str, the message to print
        :param colour: str, the colour to print, colour must be one of the
                       following: b, r, h, y, m, k

        :return: a coloured string ready to be printed to stdout
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
        # return colour mesage
        return start + message + self.endc


def display_func(name: Union[str, None] = None,
                 program: Union[str, None] = None,
                 class_name: Union[str, None] = None) -> str:
    """
    Start of function setup. Returns a properly constructed string
    representation of where the function is.

    string is formatted as follows:
        program.class_name.name    (if class_name and program set)
        program.name               (if class_name not set and program set)
        name                       (if class_name and program not set)

    If params is a ParamDict checks the inputs for a breakfunc and if the
    "name" matched the breakfunc - will add a break point at the start of
    function where display_func was used

    :param name: str or None - if set is the name of the function
                 (i.e. def myfunction   name = "myfunction")
                 if unset, set to "Unknown"
    :param program: str or None, the program or recipe the function is defined
                    in, if unset not added to the output string
    :param class_name: str or None, the class name, if unset not added
                       (i.e. class myclass   class_name = "myclass"

    :returns: a properly constructed string representation of where the
              function is.
    """
    # start the string function
    strfunc = ''
    # deal with no file name
    if name is None:
        name = 'Unknown'
    elif not isinstance(name, str):
        emsg = 'display func "name" not string. \n\tValue = {0}\n\tType = {1}'
        raise ValueError(emsg.format(name, type(name)))
    # ----------------------------------------------------------------------
    # add the program
    if program is not None:
        strfunc = str(program)
    if class_name is not None:
        strfunc += '.{0}'.format(class_name)
    # add the name
    strfunc += '.{0}'.format(name)
    # add brackets to show function
    if not strfunc.endswith('()'):
        strfunc += '()'
    # ----------------------------------------------------------------------
    # return formatted function name
    return strfunc


# =============================================================================
# Basic other functions
# =============================================================================
def _get_prev_count(params: Any, previous: str) -> int:
    """
    Get the previous number of times a function was found in
    params['DEBUG_FUNC_LIST']

    :param params: None or ParamDict containing at least DEBUG_FUNC_LIST (a list
                   of debug functions)
    :param previous: str, the last debug function used

    :return: number of times function occurs in DEBUG_FUNC_LIST
    """
    # set function name (cannot break here --> no access to inputs)
    _ = display_func('._get_prev_count()', __NAME__)
    # deal with no params
    if params is None:
        return 0
    # get the debug list
    debug_list = params['DEBUG_FUNC_LIST'][:-1]
    # get the number of iterations
    n_elements = 0
    # loop around until we get to
    for row in range(len(debug_list))[::-1]:
        if debug_list[row] != previous:
            break
        else:
            n_elements += 1
    # return number of element founds
    return n_elements


def get_uncommon_path(path1: Union[Path, str], path2: Union[Path, str]) -> str:
    """
    Get the uncommon path of "path1" compared to "path2"

    i.e. if path1 = /home/user/dir1/dir2/dir3/
         and path2 = /home/user/dir1/

         the output should be /dir2/dir3/

    :param path1: string, the longer root path to return (without the common
                  path)
    :param path2: string, the shorter root path to compare to

    :return uncommon_path: string, the uncommon path between path1 and path2
    """
    # set function name (cannot break here --> no access to params)
    _ = display_func('get_uncommon_path', __NAME__)
    # may need to switch paths if len(path2) > len(path1)
    if len(str(path2)) > len(str(path1)):
        _path1 = str(path2)
        _path2 = str(path1)
    else:
        _path1 = str(path1)
        _path2 = str(path2)
    # paths must be absolute
    _path1 = os.path.abspath(_path1)
    _path2 = os.path.abspath(_path2)
    # get common path
    common = os.path.commonpath([_path2, _path1]) + os.sep
    # return the non-common part of the path
    return _path1.split(common)[-1]


def unix_char_code() -> Tuple[float, str, str]:
    """
    Get the time now (using astropy.Time) and return the unix time
    human time and a random code of 4 characters

    :return: tuple, 1. the unix time now, 2. the human time now, 3. a random
             set of 4 characters
    """
    # set function name
    _ = display_func('unix_char_code', __NAME__)
    # we need a random seed
    np.random.seed(random.randint(1, 2 ** 30))
    # generate a random number (in case time is too similar)
    #  -- happens a lot in multiprocessing
    rint = np.random.randint(1000, 9999, 1)[0] / 1e7
    # wait a fraction of time (between 1us and 1ms)
    time.sleep(float(rint))
    # get the time now from astropy
    timenow = Time.now()
    # get unix and human time from astropy time now
    unixtime = timenow.unix * 1e7
    humantime = timenow.iso
    # generate random four characters to make sure pid is unique
    rval = ''.join(np.random.choice(list(CHARS), size=4))
    return unixtime, humantime, rval


def get_relative_folder(package: Union[None, str],
                        folder: Union[str, Path]) -> str:
    """
    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    # set function name
    func_name = str(__NAME__) + '.get_relative_folder()'
    # try base function
    return drs_base.base_func(drs_base.base_get_relative_folder, func_name,
                              package, folder)

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
