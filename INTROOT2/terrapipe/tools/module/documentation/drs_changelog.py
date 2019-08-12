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

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.io import drs_path

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_changelog.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# -----------------------------------------------------------------------------
# define line parameters
VERSIONSTR_PREFIX = 'DRS_VERSION = Const('
DATESTR_PREFIX = 'DRS_DATE = Const('

VERSIONSTR = """
DRS_VERSION = Const('DRS_VERSION', value='{0}', dtype=str, 
                    source=__NAME__)
"""
DATESTR = """
DRS_DATE = Const('DATE', value='{0}', dtype=str, 
                 source=__NAME__)
"""


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
    # read file and delete
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    # make backup
    shutil.copy(filename, filename + '.backup')

    os.remove(filename)
    # edit first line
    lines[0] = 'DRS_VERSION = {0}\n'.format(version)
    # write file and save
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()
    # remove backup
    os.remove(filename + '.backup')


def update_py_version(filename, version):
    # read const file
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
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
    lines[version_it] = VERSIONSTR.format(version)
    # update date
    dt = datetime.now()
    dargs = [DATESTR.strip(), dt.year, dt.month, dt.day]
    datestr = '{0} \'{1:04d}-{2:02d}-{3:02d}\'\n'.format(*dargs)
    lines[date_it] = DATESTR.format(datestr)
    # write lines
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()
    # remove backup
    os.remove(filename + '.backup')


def preview_log(filename):
    os.system('more {0}'.format(filename))


# =============================================================================
# End of code
# =============================================================================
