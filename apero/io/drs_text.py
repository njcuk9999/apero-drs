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

from apero.core import constants
from apero import lang
from apero.core.core import drs_log


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
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# alias pcheck
pcheck = drs_log.find_param


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


def common_text(stringlist, kind='prefix'):
    """
    For a list of strings find common prefix or suffix, returns None
    if no common substring of kind is not 'prefix' or 'suffix'

    :param stringlist: a list of strings to test
    :param kind: string, either 'prefix' or 'suffix'
    :return:
    """

    substring = stringlist[0]

    if kind == 'prefix':
        # loop around strings in list (except first)
        for _str in stringlist[1:]:
            # while substring is not equal in first and Nth shorten
            while _str[:len(substring)] != substring and len(substring) != 0:
                substring = substring[:len(substring)-1]
            # test for blank string
            if len(substring) == 0:
                break

    elif kind == 'suffix':
        # loop around strings in list (except first)
        for _str in stringlist[1:]:
            print('list: ', _str)
            # while substring is not equal in first and Nth shorten
            while _str[-len(substring):] != substring and len(substring) != 0:
                substring = substring[1:]
                print(substring)
            # test for blank string
            if len(substring) == 0:
                break
    # if prefix or suffix is the same as all in list return None - there
    # is no prefix
    if substring == stringlist[0]:
        return None
    # else return the substring
    else:
        return substring


def combine_uncommon_text(stringlist, prefix=None, suffix=None, fmt=None):
    """
    Combien a set of strings with a common prefix and/or suffix
    :param stringlist:
    :param prefix:
    :param suffix: must be "{0} {1} {2} {3}" where {0} is the prefix {1} is
                   the first entry {2} is the last entry and {3} is the suffix.
                   One can add any formatting inbetween  i.e. the default is
                   {0}F{1}T{2}{3}
    :return:
    """
    if fmt is None:
        fmt = '{0}F{1}T{2}{3}'
    # remove prefix and suffix
    entries = []
    # loop around string list
    for entry in stringlist:

        if prefix is not None:
            entry = entry.split(prefix)[-1]
        if suffix is not None:
            entry = entry.split(suffix)[0]
        entries.append(entry)
    # sort entries
    entries = np.sort(entries)
    # deal with no prefix
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = ''
    # construct first-last analysis
    text = fmt.format(prefix, entries[0], entries[-1], suffix)
    # return text
    return text


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
