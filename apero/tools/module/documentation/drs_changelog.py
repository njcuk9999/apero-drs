#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-01 at 17:02

@author: cook
"""

import os
import shutil
from datetime import datetime

from apero.base import base
from apero import core
from apero import lang


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_changelog.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# -----------------------------------------------------------------------------
# define line parameters
VERSIONSTR_PREFIX = '__version__ = '
DATESTR_PREFIX = '__date__ = '

VERSIONSTR = "__version__ = '{0}'"
DATESTR = "__date__ = '{0}'"


# =============================================================================
# Define functions
# =============================================================================
def ask_for_new_version(params):

    # get the text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # log current version
    print(textdict['40-501-00001'].format(__version__))
    # ask if we wish to change version
    uinput1 = str(input(textdict['40-501-00002'] + ' [Y]es or [N]o:\t'))
    # if yes change the version
    if 'Y' in uinput1.upper():
        cond = True
        uinput2a = ''
        while cond:
            # ask for new version
            uinput2a = str(input(textdict['40-501-00003']))
            # ask for new version again (must match)
            uinput2b = str(input(textdict['40-501-00004']))
            # if both versions don't match
            if uinput2a != uinput2b:
                # print that versions don't match
                print(textdict['40-501-00005'])
            else:
                # print the new version
                print(textdict['40-501-00006'].format(uinput2a))
                # ask if new version is correct
                qinput3 = textdict['40-501-00007'] + ' [Y]es or [N]o:\t'
                uinput3 = str(input(qinput3))
                if 'Y' in uinput3.upper():
                    cond = False
        # return new version
        return uinput2a
    else:
        # return None if we didn't want to change the version
        return None


def git_tag_head(version):

    os.system('git tag {0}'.format(version))


def git_remove_tag(version):
    os.system('git tag -d {0}'.format(version))


def git_change_log(filename):
    """
    requires pip install gitchangelog

    :param filename:
    :return:
    """

    os.system('gitchangelog > {0}'.format(filename))


def update_version_file(filename, version):
    # read the lines
    with open(filename, 'r') as f:
        lines = f.readlines()
    # make backup
    shutil.copy(filename, filename + '.backup')

    os.remove(filename)
    # edit first line
    lines[0] = 'DRS_VERSION = {0}\n'.format(version)
    # write the lines
    with open(filename, 'w') as f:
        f.writelines(lines)
    # remove backup
    os.remove(filename + '.backup')


def update_py_version(filename, version):
    # read the lines
    with open(filename, 'r') as f:
        lines = f.readlines()
    # make backup
    shutil.copy(filename, filename + '.backup')
    # find version and date to change
    version_it, date_it = None, None
    for it, line in enumerate(lines):
        if line.startswith(VERSIONSTR_PREFIX):
            version_it = it
        if line.startswith(DATESTR_PREFIX):
            date_it = it
    # update version
    version_string = VERSIONSTR.format(version)
    # update date
    dt = datetime.now()
    dargs = [DATESTR.strip(), dt.year, dt.month, dt.day]
    datestr = '{1:04d}-{2:02d}-{3:02d}'.format(*dargs)
    date_string = DATESTR.format(datestr)
    # get new lines
    new_lines = []
    # update lines
    for it, line in enumerate(lines):
        if it == version_it:
            new_lines += version_string + '\n'
        elif it == date_it:
            new_lines += date_string + '\n'
        else:
            new_lines.append(line)
    # write the lines
    with open(filename, 'w') as f:
        f.writelines(new_lines)
    # remove backup
    os.remove(filename + '.backup')


def preview_log(filename):
    os.system('more {0}'.format(filename))


def update_file(filename, prefix, suffix):
    # read the lines
    with open(filename, 'r') as f:
        lines = f.readlines()
    # storage of output lines
    outlines = []
    # find line
    for line in lines:
        # find prefix line
        if line.startswith(prefix):
            outline = prefix + suffix
        else:
            outline = line
        # add new line at end if not there
        if not line.endswith('\n'):
            outline += '\n'
        # append to output lines
        outlines.append(outline)
    # write to file
    with open(filename, 'w') as f:
        for outline in outlines:
            f.write(outline)


def format_rst(filename):
    # ----------------------------------------------------------------------
    # read the lines
    with open(filename, 'r') as f:
        lines = f.readlines()
    # ----------------------------------------------------------------------
    outlines = []
    # loop around in lines
    for line in lines:
        # ------------------------------------------------------------------
        # deal with special characters
        line = _special_chars(line)
        # ------------------------------------------------------------------
        # deal with line endings
        if not line.endswith('\n'):
            line += '\n'
        # append line to outlines
        outlines.append(line)
    # ----------------------------------------------------------------------
    # write outlines
    with open(filename, 'w') as f:
        for outline in outlines:
            f.write(outline)


def _special_chars(line):
    # replace tabs with spaces
    line = line.replace('\t', ' ' * 4)
    # need to remove all accent quotes
    line = line.replace('`', '')
    # special chars
    punctuation = ['\n', '.', ',', '!', '?', ':', ';', '"', '\'']
    chars = ['_', '*', '.py']
    prefix = [True, True, False]
    suffix = [True, True, True]
    contains = [True, True, False]
    # get words
    words = line.split(' ')
    # loop around all words
    for wit, word in enumerate(words):
        # copy word
        newword = str(word)
        # define empty out suffix (to be filled by punctuation)
        out_suffix = ''
        # need to deal with punctuation
        while (newword != '') and (newword[-1] in punctuation):
            newword = newword[:-1]
        if (len(newword) > 0) and (len(newword) != len(word)):
            out_suffix = word.split(newword)[-1]
        elif len(newword) == 0:
            continue
        # loop around special character sets
        for cit, char in enumerate(chars):
            # skip if we don't have characters
            if char not in word:
                continue
            # deal with prefix
            if prefix[cit]:
                cond1 = word.startswith(char)
            else:
                cond1 = False
            # deal with contains
            if contains[cit]:
                cond2 = char in word
            else:
                cond2 = False
            # deal with suffix
            if suffix[cit]:
                cond3 = word.endswith(char)
            else:
                cond3 = False
            # if any are true word is special
            if cond1 or cond2 or cond3:
                newword = '`{0}`'.format(newword)
                # add back puncutation
                newword += out_suffix
                # replace word with newword
                words[wit] = newword
                # word is special do not continue loop
                break
    # make new line
    newline = ' '.join(words)
    # return line
    return newline


# =============================================================================
# End of code
# =============================================================================
