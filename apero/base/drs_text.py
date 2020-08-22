#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Text and string manipulation functions here

Created on 2019-08-12 at 17:23

@author: cook
"""
import numpy as np
import warnings

from apero.base import base
from apero.base import drs_exceptions


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_text.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException


# =============================================================================
# Define functions
# =============================================================================
def load_text_file(filename, comments='#', delimiter='='):
    with warnings.catch_warnings(record=True) as _:
        # noinspection PyBroadException
        try:
            raw = np.genfromtxt(filename, comments=comments,
                                delimiter=delimiter, dtype=str).astype(str)
        except Exception:
            raw = read_lines(filename, comments=comments, delimiter=delimiter)
    # return the raw lines
    return raw


def read_lines(filename, comments='#', delimiter=' '):
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
        raise DrsCodedException(codeid='01-001-00024', targs=eargs,
                                level='error', func_name=func_name)
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
                raise DrsCodedException(codeid='01-001-00025', targs=eargs,
                                        level='error', func_name=func_name)
            # append to raw list
            raw.append([key, value])
    # check that raw has entries
    if len(raw) == 0:
        eargs = [filename]
        raise DrsCodedException(codeid='01-001-00026', targs=eargs,
                                level='error', func_name=func_name)
    # return raw
    return np.array(raw)


def save_text_file(filename, array, func_name=None):
    if func_name is None:
        func_name = __NAME__ + '.save_text_file()'
    # try to save text file
    with warnings.catch_warnings(record=True) as _:
        try:
            np.savetxt(filename, array)
        except Exception as e:
            eargs = [filename, type(e), e, func_name]
            raise DrsCodedException(codeid='00-008-00020', targs=eargs,
                                    level='error', func_name=func_name)


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
            # while substring is not equal in first and Nth shorten
            while _str[-len(substring):] != substring and len(substring) != 0:
                substring = substring[1:]
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
    # deal with prefix/suffix being ''
    if len(prefix) == 0:
        prefix = None
    if len(suffix) == 0:
        suffix = None
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


def null_text(variable, nulls=None):
    """
    Deal with variables that are unset (i.e. None) but may be text nulls
    like "None" or ''  - nulls are set by "nulls" input

    :param variable: object, any variable to test for Null
    :param nulls: list of strings or None - if set extra strings that can be
                  a null value
    :return:
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


def true_text(variable):
    """
    Deal with variables that should be True or False  even when a string
    (defaults to False)

    i.e. returns True if variable = True, 1, "True", "T", "t", "true" etc

    :param variable:
    :return:
    """
    # if variable is a True or 1 return True
    if variable in [True, 1]:
        return True
    # if variable is string test string Trues
    if isinstance(variable, str):
        if variable.upper() in ['TRUE', 'T', '1']:
            return True
    # else in all other cases return False
    return False


def include_exclude(inlist, includes=None, excludes=None, ilogic='AND',
                    elogic='AND'):
    """
    Filter a list by a list of include and exclude strings
    (can use AND or OR) in both includes and excludes

    includes: if ilogic=='AND'  all must be in list entry
              if ilogic=='OR'   one must be in list entry

    excludes: if elogic=='AND'   all must not be in list entry
              if elogic=='OR'    one must not be in list entry

    :param inlist: list, the input list of strings to check
    :param includes: list or string, the include string(s)
    :param excludes: list or string, the exclude string(s)
    :param ilogic: string, 'AND' or 'OR' logic to use when combining includes
    :param elogic: string, 'AND' or 'OR' logic to use when combining excludes

    :type inlist: list
    :type includes: Union[None, list, str]
    :type excludes: Union[None, list, str]
    :type ilogic: str
    :type elogic: str

    :return: the filtered list of strings
    :rtype: list
    """
    # ----------------------------------------------------------------------
    if includes is None and excludes is None:
        return list(inlist)
    # ----------------------------------------------------------------------
    mask = np.ones(len(inlist)).astype(bool)
    # ----------------------------------------------------------------------
    if includes is not None:
        if isinstance(includes, str):
            includes = [includes]
        elif not isinstance(includes, list):
            raise ValueError('includes list must be a list or string')
        # loop around values
        for row, value in enumerate(inlist):
            # start off assuming we need to keep value
            if ilogic == 'AND':
                keep = True
            else:
                keep = False
            # loop around include strings
            for include in includes:
                if ilogic == 'AND':
                    if include in value:
                        keep &= True
                    else:
                        keep &= False
                else:
                    if include in value:
                        keep |= True
                    else:
                        keep |= False
            # change mask
            mask[row] = keep
    # ----------------------------------------------------------------------
    if excludes is not None:
        if isinstance(excludes, str):
            excludes = [excludes]
        elif not isinstance(excludes, list):
            raise ValueError('excludes list must be a list or string')
        # loop around values
        for row, value in enumerate(inlist):
            # start off assuming we need to keep value
            if ilogic == 'AND':
                keep = True
            else:
                keep = False
            # loop around include strings
            for exclude in excludes:
                if elogic == 'AND':
                    if exclude not in value:
                        keep &= True
                    else:
                        keep &= False
                else:
                    if exclude not in value:
                        keep |= True
                    else:
                        keep |= False
            # update mask
            mask[row] &= keep
    # ----------------------------------------------------------------------
    # return outlist
    return list(np.array(inlist)[mask])


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
