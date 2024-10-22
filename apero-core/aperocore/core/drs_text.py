#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO text and string manipulation functionality

Created on 2019-08-12 at 17:23

@author: cook

import rules

only from:
- apero.base.*
- apero.lang.*
- apero.core.core.drs_exceptions
"""
import os
import warnings
from pathlib import Path
from typing import Any, Union, List, Optional

import numpy as np

from aperocore import drs_lang
from aperocore.base import base
from aperocore.base import drs_base
from aperocore.core import drs_exceptions
from aperocore.core import drs_misc

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.core.drs_text.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# get text entry
textentry = drs_lang.textentry
# Get colours
COLOURS = drs_misc.Colors()


# =============================================================================
# Define functions
# =============================================================================
def load_text_file(filename: Union[str, Path], comments: str = '#',
                   delimiter: str = '=') -> np.ndarray:
    """
    Load a text file, first by trying np.genfromtxt else use a slow method

    :param filename: str or Path, the path to the text file to open
    :param comments: str, the character to use as comments when a line starts
                     with this character (default='#')
    :param delimiter: str, the character to use to split up columns of text
                      (default='=')
    :return: numpy array containing the rows and columns from filename
    """
    # catch and ignore warnings inside this code chunk
    with warnings.catch_warnings(record=True) as _:
        # try the faster method first (np.genfromtxt)
        # noinspection PyBroadException
        try:
            raw = np.genfromtxt(filename, comments=comments,
                                delimiter=delimiter, dtype=str).astype(str)
        # if genfromtxt fails use the slower method
        except Exception:
            raw = read_lines(filename, comments=comments, delimiter=delimiter)
    # return the raw lines as a np.array
    return raw


def read_lines(filename: Union[str, Path], comments: str = '#',
               delimiter: str = '=') -> np.ndarray:
    """
    Read the lines with the open command (slower than np.genfromtxt but more
    reliable when we have weird data)

    :param filename: str or Path, the path to the text file to open
    :param comments: str, the character to use as comments when a line starts
                     with this character (default='#')
    :param delimiter: str, the character to use to split up columns of text
                      (default='=')
    :return: numpy array containing the rows and columns from filename
    """
    func_name = __NAME__ + '.read_lines()'
    # manually open file (slow)
    try:
        # read the lines
        with open(filename, 'r') as f:
            lines = f.readlines()
    # if we can't open it break with an error message (hopefully caught higher
    #    up where we have access to drs_log.wlog)
    except Exception as e:
        eargs = [filename, type(e), e, func_name]
        ecode = '01-001-00024'
        emsg = textentry(ecode)
        raise drs_base.base_error(ecode, emsg, 'error', eargs)
    # valid lines
    raw = []
    # loop around lines
    for l_it, line in enumerate(lines):
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
                eargs = [filename, l_it + 1, line, delimiter, func_name]
                ecode = '01-001-00025'
                emsg = textentry(ecode)
                raise drs_base.base_error(ecode, emsg, 'error', eargs)
            # append to raw list
            raw.append([key, value])
    # check that raw has entries
    if len(raw) == 0:
        eargs = [filename]
        ecode = '01-001-00026'
        emsg = textentry(ecode)
        raise drs_base.base_error(ecode, emsg, 'error', eargs)

    # return raw
    return np.array(raw)


def save_text_file(filename: Union[str, None], array: np.ndarray,
                   func_name: Union[str, None] = None):
    """
    Save text to a file using np.savetxt and catch exceptions

    :param filename: str or Path, the path to the text file to save
    :param array: np.ndarray - the array to save to text file
    :param func_name: str the function where save_text_file was called

    :return: None
    """
    # if we don't have the function name set it here (for error message)
    if func_name is None:
        func_name = __NAME__ + '.save_text_file()'
    # try to save text file
    with warnings.catch_warnings(record=True) as _:
        try:
            # noinspection PyTypeChecker
            np.savetxt(filename, array)
        except Exception as e:
            eargs = [filename, type(e), e, func_name]
            raise DrsCodedException(codeid='00-008-00020', targs=eargs,
                                    level='error', func_name=func_name)


def common_text(stringlist: List[str],
                kind: str = 'prefix') -> Union[None, str]:
    """
    For a list of strings find common prefix or suffix, returns None
    if no common substring of kind is not 'prefix' or 'suffix'

    :param stringlist: a list of strings to test
    :param kind: string, either 'prefix' or 'suffix'
    :return:
    """
    # get the first sub string
    substring = stringlist[0]
    # if we are looking for a prefix
    if kind == 'prefix':
        # loop around strings in list (except first)
        for _str in stringlist[1:]:
            # while substring is not equal in first and Nth shorten
            while _str[:len(substring)] != substring and len(substring) != 0:
                substring = substring[:len(substring)-1]
            # test for blank string
            if len(substring) == 0:
                break
    # else if we are look for a suffix
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


def combine_uncommon_text(stringlist: List[str],
                          prefix: Union[str, None] = None,
                          suffix: Union[str, None] = None,
                          fmt: Union[str, None] = None) -> str:
    """
    Combine a set of strings with a common prefix and/or suffix

    must be "{0} {1} {2} {3}" where {0} is the prefix {1} is
                   the first entry {2} is the last entry and {3} is the suffix.
                   One can add any formatting inbetween  i.e. the default is
                   {0}F{1}T{2}{3}

    :param stringlist: list of strings to find uncommon text and combine
    :param prefix: str, predefined prefix to split by (should be common to all
                   strings in stringlist)
    :param suffix: str, predefined suffix to split by (should be common to all
                   strings in stringlist)

    :param fmt: str or None the format of the output text
                (defaults to {0}F{1}T{2}{3}) must include {0} {1} {2} {3} for
                piping strings to format text
    :return: returns a string that represents all input strings
    """
    if fmt is None:
        fmt = '{0}F{1}T{2}{3}'
    # deal with prefix/suffix being ''
    if prefix is not None:
        if len(prefix) == 0:
            prefix = None
    if suffix is not None:
        if len(suffix) == 0:
            suffix = None
    # remove prefix and suffix
    entries = []
    # loop around string list
    for entry in stringlist:
        # get the prefix if set
        if prefix is not None:
            entry = entry.split(prefix)[-1]
        # get the suffix if set
        if suffix is not None:
            entry = entry.split(suffix)[0]
        # append to entries
        entries.append(entry)
    # sort entries
    entries = np.sort(entries)
    # deal with no prefix (must be string)
    if prefix is None:
        prefix = ''
    # deal with no suffix (must be string)
    if suffix is None:
        suffix = ''
    # construct first-last analysis
    text = fmt.format(prefix, entries[0], entries[-1], suffix)
    # return text
    return text


def textwrap(input_string: str, length: int) -> List[str]:
    """
    Wraps the text `input_string` to the length of `length` new lines are
    indented with a tab

    Modified version of this: https://stackoverflow.com/a/16430754

    :param input_string: str, the input text to wrap
    :param length: int, the length of the wrap
    :type input_string: str
    :type length: int
    :return: list of strings, the new set of wrapped lines
    :rtype: list[str]
    """
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '.textwrap()'
    # set up a new empty list of strings
    new_string = []
    # loop around the input string split by new lines
    for substring in input_string.split("\n"):
        # if line is empty add an empty line to new_string
        if substring == "":
            new_string.append('')
        # set the current line length to zero initially
        wlen = 0
        # storage
        line = []
        # loop around words in string and split at words if length is too long
        #   words are definied by white spaces
        for dor in substring.split():
            # if the word + current length is shorter than the wrap length
            #   then append to current line
            if wlen + len(dor) + 1 <= length:
                line.append(dor)
                # update the current line length
                wlen += len(dor) + 1
            # else we have to wrap
            else:
                # add the current line to the output string
                new_string.append(" ".join(line))
                # start a new line with the word that broke the wrap
                line = [dor]
                # set the current line length to the length of the word
                wlen = len(dor)
        # if the length of the line is larger than zero append line
        if len(line) > 0:
            new_string.append(" ".join(line))
    # add a tab to all but first line
    new_string2 = [new_string[0]]
    # loop around lines in new strings (except the first line)
    for it in range(1, len(new_string)):
        new_string2.append('\t' + new_string[it])
    # return the new string with tabs for subsequent lines
    return new_string2


def null_text(variable: Any, nulls: Union[None, List[str]] = None) -> bool:
    """
    Deal with variables that are unset (i.e. None) but may be text nulls
    like "None" or ''  - nulls are set by "nulls" input

    :param variable: object, any variable to test for Null
    :param nulls: list of strings or None - if set extra strings that can be
                  a null value
    :return: True if value is a null value or False otherwise (or if variable
              is not str or None)
    """
    # set function name
    func_name = __NAME__ + '.null_text()'
    # try base function
    return drs_base.base_func(drs_base.base_null_text, func_name,
                              variable, nulls)


def true_text(variable: Any) -> bool:
    """
    Deal with variables that should be True or False  even when a string
    (defaults to False)

    i.e. returns True if variable = True, 1, "True", "T", "t", "true" etc

    :param variable: any variable to test whether it is True

    :returns: True if variable is considered True or False otherwise (or if
              variable is not bool, int, float or string)
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


def include_exclude(inlist: List[str],
                    includes: Union[None, List[str], str] = None,
                    excludes: Union[None, List[str], str] = None,
                    ilogic: str = 'AND', elogic: str = 'AND') -> List[str]:
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


# capitalisation function (for case insensitive keys)
def capitalise_key(key: str) -> str:
    """
    Capitalizes "key" (used to make ParamDict case insensitive), only if
    key is a string

    :param key: string or object, if string then key is capitalized else
                nothing is done

    :return key: capitalized string (or unchanged object)
    """
    # capitalise string keys
    if isinstance(key, str):
        if key.isupper():
            return key
        else:
            return key.upper()
    else:
        return key


def test_format(fmt: str) -> bool:
    """
    Test the format string with a floating point number

    :param fmt: string, the format string i.e. "7.4f"

    :type fmt: str

    :returns: bool, if valid returns True else returns False
    :rtype: bool
    """
    # set function
    _ = __NAME__ + '.test_format()'
    # test format of a string
    try:
        if fmt.startswith('{') and fmt.endswith('}'):
            return True
        elif 's' in fmt:
            return True
        elif 'd' in fmt:
            _ = ('{0:' + fmt + '}').format(123)
        else:
            _ = ('{0:' + fmt + '}').format(123.456789)
        return True
    except ValueError:
        return False


def cull_leading_trailing(text: str, chars: Union[List[str], str]) -> str:
    """
    Remove leading and trailing charaters from text i.e.

    text = '''This is some text'''
    chars = ["'"]

    returns: This is some text

    :param text: str, the text to clean
    :param chars: list of strings or string, the characters to remove from
                  start/end
    :return: str, the cleaned string
    """
    # make sure chars is a list of strings
    if isinstance(chars, str):
        chars = [chars]
    # loop around each character and remove from start and end
    for char in chars:
        while text.startswith(char):
            text = text[1:]
        while text.endswith(char):
            text = text[:-1]
    # return cleaned string
    return text


def clean_strings(strings: Union[List[str], str]) -> Union[List[str], str]:
    """
    Take a string or list of strings and removes all trailing and preceeding
    whitespaces and puts all characters as upper case

    :param strings: list of strings or string, the string or strings to
                    strip of whitespaces + upper case
    :return:
    """
    if isinstance(strings, str):
        return strings.strip().upper()
    else:
        outstrings = []
        for string in strings:
            outstrings.append(string.strip().upper())
        return outstrings


def cprint(message: Union[drs_lang.Text, str], colour: str = 'g'):
    """
    print coloured message

    :param message: str, message to print
    :param colour: str, colour to print
    :return:
    """
    print(COLOURS.print(str(message), colour))


def user_input(question: str, dtype: Union[str, type, None] = None,
               options: Union[List[Any], None] = None,
               default: Any = None,
               required: bool = True, color='g',
               stringlimit: Optional[int] = None,
               restricted_chars: List[str] = None,
               optiondescs: List[str] = None) -> Any:
    """
    Ask user for an input

    :param question: str, the question to ask
    :param dtype: str, the data type (int/float/bool/str/path/YN)
    :param options: list, list of valid options
    :param optiondesc: list, list of option descriptions
    :param default: object, if set the default value, if unset a value
                    if required
    :param required: bool, if False and dtype=path does not create a path
                     else does not change anything
    :param color: str, the color of the text printed out
    :param stringlimit: int, the maximum length of a string
    :param restricted_chars: list of str, the restricted characters
    :param optiondescs: list of str, the descriptions of the options
                        (if None uses options itself)

    :return: the response from the user or the default
    """
    # set up check criteria as True at first
    check = True
    # set up user input as unset
    uinput = None
    # -------------------------------------------------------------------------
    # deal with dtype
    if isinstance(dtype, str):
        dtype = dtype.upper()
    elif isinstance(dtype, Path):
        dtype = 'PATH'
    # deal with paths (expand)
    if dtype == 'PATH':
        if default not in [None, 'None', '']:
            default = Path(default)
            default.expanduser()
        else:
            default = None
    # -------------------------------------------------------------------------
    # deal options + option descriptions
    if optiondescs is not None and options is not None:
        optiondesc = []
        option_dict = dict()
        for option, desc in zip(options, optiondescs):
            optiondesc.append(f'{option}: {desc}')
            option_dict[option] = option
    # deal with options + no option descriptions
    elif options is not None:
        if dtype in [int, float, 'INT', 'FLOAT']:
            optiondesc = [str(i) for i in options]
            option_dict = None
        else:
            optiondesc = []
            option_dict = dict()
            for it, option in enumerate(options):
                optiondesc.append(f'{it+1}: {option}')
                option_dict[str(it+1)] = option
            dtype = 'OPTION'
    # deal with no options
    else:
        optiondesc = None
        option_dict = None
    # -------------------------------------------------------------------------
    # deal with yes/no dtype
    if dtype == 'YN':
        options = [drs_lang.YES, drs_lang.NO]
        optiondesc = [drs_lang.YES_OR_NO]
        option_dict = None
    # -------------------------------------------------------------------------
    # loop around until check is passed
    while check:
        # ask question
        cprint(question, color)
        # print options
        if options is not None:
            cprint(drs_lang.OPTIONS_ARE + ':', 'b')
            print('   ' + '\n   '.join(list(np.array(optiondesc, dtype=str))))
        if default is not None:
            cprint('   {0}: {1}'.format(drs_lang.DEFAULT_IS, default), 'b')
        # record response
        uinput = input(' >>   ')
        # ---------------------------------------------------------------------
        # deal with restricted characters
        if restricted_chars is not None:
            bad_char = False
            for char in restricted_chars:
                if char in uinput:
                    wmsg = ('Restricted character "{0}" found in input. '
                            'Please correct.')
                    cprint(wmsg.format(char), 'y')
                    # check again flag
                    check = True
                    # bad character flag
                    bad_char = True
                    continue
            # ask the question again
            if bad_char:
                continue
        # ---------------------------------------------------------------------
        # deal with string ints, floats, logic
        if dtype in ['INT', 'FLOAT', 'BOOL', 'STR']:
            # noinspection PyBroadException
            try:
                basetype = eval(dtype.lower())
                uinput = basetype(uinput)
                check = False
            except Exception as _:
                if uinput == '' and default is not None:
                    check = False
                else:
                    cargs = [dtype.lower()]
                    cprint(textentry('40-001-00034', args=cargs), 'y')
                    check = True
                    continue
        # ---------------------------------------------------------------------
        # deal with int/float/logic
        if dtype in [int, float, bool, str]:
            # noinspection PyBroadException
            try:
                uinput = dtype(uinput)
                check = False
            except Exception as _:
                cargs = [dtype.__name__]
                cprint(textentry('40-001-00034', args=cargs), 'y')
                check = True
                continue
        # deal with paths
        elif dtype == 'PATH':
            # --------------------------------------------------------------
            # check whether default wanted and user types 'None' or blank ('')
            if uinput in ['None', ''] and default is not None:
                uinput = default
                # deal with a null default
                if default in ['None', '']:
                    return default
            # deal with case where path is 'None' or blank and path is not
            # required (even if not required must be set to None or blank)
            elif not required and uinput in ['None', '']:
                return None
            # otherwise 'None and '' are not valid
            elif uinput in ['None', '']:
                cprint(textentry('40-001-00035'), 'y')
                check = True
                continue
            # --------------------------------------------------------------
            # try to create path
            # noinspection PyBroadException
            try:
                upath = Path(uinput)
            except Exception as _:
                if not required:
                    cprint(textentry('40-001-00036'), 'y')
                    check = True
                    continue
                else:
                    cprint(textentry('40-001-00037'), 'y')
                    check = True
                    continue
            # get rid of expansions
            upath.expanduser()
            # --------------------------------------------------------------
            # check whether path exists
            if upath.exists():
                return upath
            # if path does not exist ask to make it (if create)
            else:
                # check whether to create path
                pathquestion = textentry('40-001-00038', args=[uinput])
                create = user_input(pathquestion, dtype='YN')
                if create:
                    if not upath.exists():
                        # noinspection PyBroadException
                        try:
                            os.makedirs(upath)
                        except Exception as _:
                            cprint(textentry('40-001-00037'), 'y')
                            check = True
                            continue
                    return upath
                else:
                    cprint(textentry('40-001-00037'), 'y')
                    check = True
                    continue
        # deal with Yes/No questions
        elif dtype == 'YN':
            if drs_lang.YES in uinput.upper():
                return True
            elif drs_lang.NO in uinput.upper():
                return False
            else:
                cprint(textentry('40-001-00039', args=[drs_lang.YES_OR_NO]), 'y')
                check = True
                continue
        # deal with options
        if options is not None:
            if option_dict is not None:
                if uinput in option_dict:
                    return option_dict[uinput]
            # convert options to string
            options = np.char.array(np.array(options, dtype=str))
            if str(uinput).upper() in options.upper():
                check = False
                continue
            elif uinput == '' and default is not None:
                check = False
                continue
            else:
                ortxt = ' {0} '.format(drs_lang.OR)
                optionstr = ortxt.join(np.array(options, dtype=str))
                cprint(textentry('40-001-00039', args=[optionstr]), 'y')
                check = True
        # deal with string and string limit
        if dtype == str and stringlimit is not None:
            if len(uinput) > stringlimit:
                msg = 'String length must be less than {0} characters'
                margs = [stringlimit]
                cprint(msg.format(*margs), 'y')
                check = True
                continue
    # deal with returning default
    if uinput == '' and default is not None:
        return default
    else:
        # return uinput
        return uinput



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
