#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-21 19:17

@author: cook
"""
import os

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

    def __init__(self, theme=None):
        if theme is None:
            self.theme = 'DARK'
        else:
            self.theme = theme
        self.endc = self.ENDC
        self.bold = self.BOLD
        self.underline = self.UNDERLINE
        self.update_theme()

    def update_theme(self, theme=None):
        if theme is not None:
            self.theme = theme
        if self.theme == 'DARK':
            self.header = self.MAGENTA1
            self.okblue = self.BLUE1
            self.okgreen = self.GREEN1
            self.ok = self.MAGENTA2
            self.warning = self.YELLOW1
            self.fail = self.RED1
            self.debug = self.BLACK1
        else:
            self.header = self.MAGENTA2
            self.okblue = self.MAGENTA2
            self.okgreen = self.BLACK2
            self.ok = self.MAGENTA2
            self.warning = self.BLUE2
            self.fail = self.RED2
            self.debug = self.GREEN2

    def print(self, message, colour):
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


def display_func(params=None, name=None, program=None, class_name=None,
                 wlog=None, textentry=None):
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


def _get_prev_count(params, previous):
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '._get_prev_count()'
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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
