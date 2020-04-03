#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:23

@author: cook
"""
import numpy as np
import warnings

from apero import core
from apero.core import constants
from apero import locale
from apero.core.core import drs_log
from apero.core.core import drs_file


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_text.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def load_text_file(params, filename, comments='#', delimiter='='):
    with warnings.catch_warnings(record=True) as _:
        # noinspection PyBroadException
        try:
            raw = np.genfromtxt(filename, comments=comments,
                                delimiter=delimiter, dtype=str).astype(str)
        except Exception:
            raw = read_lines(params, filename, comments=comments,
                             delimiter=delimiter)
    # return the raw lines
    return raw


def read_lines(params, filename, comments='#', delimiter=' '):
    """

    :param filename:
    :param comments:
    :param delimiter:
    :return:
    """
    func_name = __NAME__ + '.read_lines()'
    # manually open file (slow)
    try:
        # read the lines
        with open(filename, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        eargs = [filename, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('01-001-00024', args=eargs))
        lines = None
    # valid lines
    raw = []
    # loop around lines
    for l, line in enumerate(lines):
        # remove line endings and blanks at start and end
        line = line.replace('\n', '').strip()
        # do not include blank lines
        if len(line) == 0:
            continue
        # do not include commented lines
        elif line[0] == comments:
            continue
        else:
            # append to raw
            try:
                key, value = line.split(delimiter)
            except ValueError as _:
                eargs = [filename, l + 1, line, delimiter, func_name]
                WLOG(params, 'error', TextEntry('01-001-00025', args=eargs))
                key, value = None, None
            # append to raw list
            raw.append([key, value])
    # check that raw has entries
    if len(raw) == 0:
        WLOG(params, 'error', TextEntry('01-001-00026', args=[filename]))
    # return raw
    return np.array(raw)


def save_text_file(params, filename, array, func_name=None):
    if func_name is None:
        func_name = __NAME__ + '.save_text_file()'
    # try to save text file
    with warnings.catch_warnings(record=True) as _:
        try:
            np.savetxt(filename, array)
        except Exception as e:
            eargs = [filename, type(e), e, func_name]
            WLOG(params, 'error', TextEntry('00-008-00020', args=eargs))


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
