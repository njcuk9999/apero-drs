#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2021-01-2021-01-13 15:56

@author: cook
"""
import os
from pathlib import Path
import shutil
from typing import Tuple

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.constants import constant_functions as cf
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.core import drs_break
from apero.tools.module.setup import drs_installation as install


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_constants.py'
__INSTRUMENT__ = base.IPARAMS['INSTRUMENT']
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get constants
Constants = constants.load(__INSTRUMENT__)
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# get display func
display_func = drs_log.display_func


# =============================================================================
# Define functions
# =============================================================================
def deal_with_generate(params: ParamDict):
    """
    Re-generate user_config and user_constant files using installation files
    useful when needing more constants

    :param params: ParamDict, the current set of parameter constants

    :return: None - writes + backs up user_config.ini and user_constants.ini
    """
    # get user config directory
    userconfig = Path(os.environ[base.USER_ENV])
    # constuct config and const file paths
    uconfigpath = userconfig.joinpath(install.UCONFIG)
    uconstpath = userconfig.joinpath(install.UCONST)
    # construct backup paths
    backup_config = str(uconfigpath) + '.backup'
    backup_const = str(uconstpath) + '.backup'
    # backup files if they exist
    if uconfigpath.exists():
        WLOG(params, '', 'Backing up config file: {0}'.format(backup_config))
        shutil.copy(uconfigpath, backup_config)
    if uconstpath.exists():
        WLOG(params, '', 'Backing up const file: {0}'.format(backup_const))
        shutil.copy(uconstpath, backup_const)
    # get the user input
    generate = params['INPUTS']['GENERATE']
    # deal with generate not filled
    if drs_text.null_text(generate, ['None']):
        return False
    # only access standard or full or choose
    if generate not in ['standard', 'full', 'choose']:
        return False
    # deal with user options
    if generate == 'full':
        kwargs = dict(devmode=True, ask_user=False)
    elif generate == 'choose':
        kwargs = dict(devmode=True, ask_user=True)
    else:
        kwargs = dict(devmode=False, ask_user=False)
    # create files
    config_lines, const_lines = install.create_ufiles(params, **kwargs)
    # write / update config and const
    uconfig = install.ufile_write(params, config_lines, userconfig,
                                  install.UCONFIG, 'config')
    uconst = install.ufile_write(params, const_lines, userconfig,
                                 install.UCONST, 'constant')
    # log writing of files
    WLOG(params, '', 'Writing: {0}'.format(uconfig))
    WLOG(params, '', 'Writing: {0}'.format(uconst))
    # return success
    return True


def deal_with_clean(params) -> bool:
    """
    Function to clean constants (use with causion)

    1. add descriptions from comments

    2. flags constants that are not used [NOT IMPLEMENTED YET]

    :param params: ParamDict, the parameter dictionary of constants

    :return: bool, success - whether we cleaned constants (True/False)
    """
    # set function name
    func_name = display_func(params, 'deal_with_clean', __NAME__)
    # warn user this could screw things up
    WLOG(params, 'warning', 'Cleaning constants changes core python files')
    uinput = input('Do you wish to continue? [Y]es or [N]o:\t')
    # do not continue
    if 'Y' not in uinput.upper():
        return False
    # -------------------------------------------------------------------------
    # Adding descriptions from comments
    # -------------------------------------------------------------------------
    # get a list of base config / constants scripts
    const_dir = drs_break.get_relative_folder(__PACKAGE__, base.CORE_PATH)

    # loop around all types
    for filename in base.SCRIPTS:
        # log progress
        WLOG(params, 'info', 'Processing file: {0}'.format(filename))
        # get full path to script
        const_path = os.path.join(const_dir, filename)
        # load script as module
        instances = cf.import_module(func_name, const_path).get()
        # ---------------------------------------------------------------------
        # store instances without descriptions
        no_desc, kinds = [], []
        # loop around instances
        for key in instances.__dict__:
            # get instance
            instance = instances.__dict__[key]
            # check that instance is a Constant or Keyword
            if isinstance(instance, (cf.Const, cf.Keyword)):
                # if instance has no description flag it now
                if instance.description is None:
                    no_desc.append(instance.name)
                if isinstance(instance, cf.Const):
                    kinds.append('Const')
                else:
                    kinds.append('Keyword')
        # ---------------------------------------------------------------------
        # now we need to find and add the descriptions from the commands of
        #   the line(s) before
        # ---------------------------------------------------------------------
        # get string representation of file
        with open(const_path, 'r') as const_file:
            all_lines = const_file.readlines()
        # merge into one string
        const_string = ''
        for line in all_lines:
            const_string += line

        # loop around keys
        for row, key in enumerate(no_desc):
            # print progress
            WLOG(params, '', '\tProcessing key: {0}'.format(key))
            # get constant entry
            const_entry, start, end = get_const(key, const_string, kinds[row])
            # deal with key not found
            if start == -1:
                WLOG(params, 'error', 'Key: "{0}" not found'.format(key))
            # get description
            description = get_comment(start, const_string)
            # add the description to the end of the const_etnry
            nargs = [const_entry[:-1], description]
            new_entry = '{0}, description=(\'{1}\'))'.format(*nargs)
            # format line
            new_entry = format_lines(new_entry)
            # now find the const_entry and replace all instances with
            #   new_entry
            const_string = const_string.replace(const_entry, new_entry)
        # ---------------------------------------------------------------------
        # write to file
        with open(const_path, 'w') as const_file:
            const_file.write(const_string)
    # ---------------------------------------------------------------------
    # if we have got to here return a success
    return True


def get_const(key: str, string: str,
              itype: str = 'Const') -> Tuple[str, int, int]:
    """
    Get the substring KEY = itype(*)

    i.e.

    DRS_VERSION = Const(*)

    :param key: str, the varaible name
    :param string: str, the full constant text file as one string
    :param itype: str, either Const or Keyword
    :return:
    """
    # get pattern to start sequence
    pattern = '{0} = {1}('.format(key, itype)
    # find the starting position in sequence
    start = string.find(pattern)
    # deal with no pattern found
    if start == -1:
        pass

    # now find the closing bracket for this statement
    find, end = 1, start
    # loop around characters in string
    for row, char in enumerate(string[start + len(pattern):]):
        # if find is 0 break
        if find == 0:
            end = start + len(pattern) + int(row)
            break
        # if we open new bracket we need to find extra closing ones
        if char == '(':
            find += 1
        # if we find a closing one find goes down
        if char == ')':
            find -= 1

    return string[start: end], start, end


def get_comment(start: int, string: str) -> str:
    """
    Get the previous lines that are comment lines and push into a description

    :param start:
    :param string:
    :return:
    """
    # split string into lines
    lines = string[:start-1].split('\n')

    comment_lines = []
    # find all comment lines
    for line in lines:
        # if line is starts with a hash we say this line is a comment line
        if line.startswith('#'):
            comment_lines.append(True)
        # all other lines are not comments
        else:
            comment_lines.append(False)
    # find the last set of comment lines
    description = ''
    row = len(comment_lines) - 1
    while row > 0:
        # must break for headers
        if lines[row].endswith('='):
            break
        # add the comment to the description (in reverse order)
        if comment_lines[row]:
            description = lines[row][1:] + description
        # break if we don't have a comment line
        else:
            break
        # must remove one from the row number (as we are looking in reverse
        #     order)
        row -= 1

    # need to clean up description
    # 1. strip whitespaces at start/end
    description = description.strip()
    # 2. remove ' characters
    description = description.replace('\'', '')
    # 3. remove # characters
    description = description.replace('#', '')
    # 4. remove \n and \t
    description = description.replace('\n', '').replace('\t', '')
    # 5. remove all whitespaces large than 1
    while '  ' in description:
        description = description.replace('  ', ' ')

    # return the description as a single string
    return description


def format_lines(entry, length=78):
    """
    Deal with description making the lines too long

    :param entry: str, the entry to add
    :param length: int, the length of the line
    :return:
    """
    # need to deal with last line too long
    lines = entry.split('\n')
    # get last line
    line = lines[-1]
    # get any indentation
    tmpline = str(line)
    whitespace = 0
    while tmpline.startswith(' '):
        tmpline = tmpline[1:]
        whitespace += 1
    # deal with long line
    if len(line) > length:
        # new line chars
        new_chars = '\n' + ' ' * whitespace
        # move description to a new line
        line = line.replace('description=(', new_chars + 'description=(')
    # return string
    return '\n'.join(lines[:-1] + [line])


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
