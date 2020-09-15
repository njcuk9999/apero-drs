#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-21 19:17

@author: cook
"""
import os
from typing import Any, Union

from apero.base import base
from apero.base import drs_break
from apero.base import drs_exceptions


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


def display_func(params: Any = None, name: Union[str, None] = None,
                 program: Union[str, None] = None,
                 class_name: Union[str, None] = None,
                 wlog: Any = None, textentry: Any = None) -> str:
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

    :param params: None or ParamDict (containing "INPUTS" for breakfunc/
                   breakpoint)
    :param name: str or None - if set is the name of the function
                 (i.e. def myfunction   name = "myfunction")
                 if unset, set to "Unknown"
    :param program: str or None, the program or recipe the function is defined
                    in, if unset not added to the output string
    :param class_name: str or None, the class name, if unset not added
                       (i.e. class myclass   class_name = "myclass"
    :param wlog: None or drs_log.wlog logger - prints log messages to wlog or
                 if not set uses drs_exceptions.wlogbasic to print log message
    :param textentry: None or TextEntry class - used to turn code ids into
                      human-readable text messages - if not set uses
                      drs_exceptions.base_printer to print the error message
                      (as a raw text id)
    :returns: a properly constructed string representation of where the
              function is.
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '.display_func()'
    # deal with no wlog defined
    if wlog is None:
        wlog = drs_exceptions.wlogbasic
    # start the string function
    strfunc = ''
    # deal with no file name
    if name is None:
        name = 'Unknown'
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
    # deal with adding a break point
    if params is not None:
        if 'INPUTS' in params and 'BREAKFUNC' in params['INPUTS']:
            # get break function
            breakfunc = params['INPUTS']['BREAKFUNC']
            # only deal with break function if it is set
            if breakfunc not in [None, 'None', '']:
                # get function name (without ending)
                funcname = strfunc.replace('()', '')
                # if function name endwith break function then we break here
                if funcname.endswith(breakfunc):
                    # log we are breaking due to break function
                    wargs = [breakfunc]
                    if textentry is None:
                        bargs = ['10-005-00004', 'warning', wargs, func_name]
                        msg = drs_exceptions.base_printer(*bargs)
                    else:
                        msg = textentry('10-005-00004', args=wargs)
                    wlog(params, 'warning', msg)
                    drs_break.break_point(params, allow=True, level=3)
    # ----------------------------------------------------------------------
    # deal with no params (do not log)
    if params is None:
        return strfunc
    # deal with no debug mode
    if 'DRS_DEBUG' not in params or 'DEBUG_MODE_FUNC_PRINT' not in params:
        return strfunc
    # deal with debug level too low (just return here)
    if params['DRS_DEBUG'] < params['DEBUG_MODE_FUNC_PRINT']:
        return strfunc
    # ----------------------------------------------------------------------
    # below here just for debug mode func print
    # ----------------------------------------------------------------------
    # add the string function to param dict
    if 'DEBUG_FUNC_LIST' not in params:
        params.set('DEBUG_FUNC_LIST', value=[None], source=func_name)
    if 'DEBUG_FUNC_DICT' not in params:
        params.set('DEBUG_FUNC_DICT', value=dict(), source=func_name)
    # append to list
    params['DEBUG_FUNC_LIST'].append(strfunc)
    # update debug dictionary
    if strfunc in params['DEBUG_FUNC_DICT']:
        params['DEBUG_FUNC_DICT'][strfunc] += 1
    else:
        params['DEBUG_FUNC_DICT'][strfunc] = 1
    # get count
    count = params['DEBUG_FUNC_DICT'][strfunc]
    # find previous entry
    previous = params['DEBUG_FUNC_LIST'][-2]
    # find out whether we have the same entry
    same_entry = previous == strfunc
    # add count
    strfunc += ' (N={0})'.format(count)
    # if we don't have a list then just print
    if params['DEBUG_FUNC_LIST'][-2] is None:
        # deal with textentry
        if textentry is None:
            bargs = ['90-000-00004', 'debug', [strfunc], func_name]
            msg = drs_exceptions.base_printer(*bargs)
        else:
            msg = textentry('90-000-00004', args=[strfunc])
        # log in func
        wlog(params, 'debug', msg, wrap=False)
    elif not same_entry:
        # get previous set of counts
        previous_count = _get_prev_count(params, previous)
        # only log if count is greater than 1
        if previous_count > 1:
            # log how many of previous there were
            if textentry is None:
                bargs = ['90-000-00005', 'debug', [previous_count], func_name]
                msg = drs_exceptions.base_printer(*bargs)
            else:
                msg = textentry('90-000-00005', args=[previous_count])
            wlog(params, 'debug', msg)
        # log a debug
        if textentry is None:
            bargs = ['90-000-00004', 'debug', [strfunc], func_name]
            msg = drs_exceptions.base_printer(*bargs)
        else:
            msg = textentry('90-000-00004', args=[strfunc])
        # log in func
        wlog(params, 'debug', msg, wrap=False)
    # return func_name
    return strfunc


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
    _ = display_func(None, '._get_prev_count()', __NAME__)
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


def get_uncommon_path(path1: str, path2: str) -> str:
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
    _ = display_func(None, 'get_uncommon_path', __NAME__)
    # may need to switch paths if len(path2) > len(path1)
    if len(path2) > len(path1):
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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
