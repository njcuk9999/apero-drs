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

from terrapipe import config
from terrapipe import constants
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
WLOG = config.wlog
# -----------------------------------------------------------------------------
rargs = [Constants, Constants['DRS_PACKAGE'], '../../']
PATH = drs_path.get_relative_folder(*rargs)
FILENAME = os.path.join(PATH, 'changelog.md')
VERSIONFILE = os.path.join(PATH, 'VERSION.txt')
rargs = [Constants, Constants['DRS_PACKAGE'], './constants/default']
CONSTPATH = drs_path.get_relative_folder(*rargs)
CONSTFILE = os.path.join(CONSTPATH, 'default_config.py')
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
def ask_for_new_version():
    print('Current version is {0}'.format(__version__))
    uinput1 = str(input('\n\t New version required? [Y]es or [N]o:\t'))

    if 'Y' in uinput1.upper():
        cond = True
        uinput2a = ''
        while cond:
            uinput2a = str(input('\n\t Please Enter new version:\t'))
            uinput2b = str(input('\n\t Please Re-Enter new version:\t'))
            if uinput2a != uinput2b:
                print('Versions do not match')
            else:
                print('\n\t New version is "{0}"'.format(uinput2a))
                uinput3 = str(input('\t\tIs this correct? [Y]es or [N]o:\t'))
                if 'Y' in uinput3.upper():
                    cond = False
        return uinput2a
    else:
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
# Define main functions
# =============================================================================
def main(preview=1, **kwargs):
    """
    Main function for drs_changelog.py

    :param preview: bool, if True does not save before previewing if False
                    saves without previewing
    :param kwargs: any additional keywords

    :type preview: bool

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(preview=preview, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = config.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = config.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    params = config.end_main(params, success)
    # return a copy of locally defined variables in the memory
    return config.get_locals(dict(locals()), llmain)


def __main__(recipe, params):
    # ----------------------------------------------------------------------
    # if in preview mode tell user
    if params['PREVIEW']:
        WLOG(params, 'info', 'Running in preview mode.')
    # ----------------------------------------------------------------------
    # read and ask for new version
    WLOG(params, '', 'Reading DRS version')
    # set new version
    version = ask_for_new_version()
    # add tag of version
    if version is not None:
        # tag head with version
        git_remove_tag(version)
        git_tag_head(version)
        new = True
    else:
        version = str(__version__)
        new = False
    # ----------------------------------------------------------------------
    # update DRS files
    if not params['PREVIEW']:
        update_version_file(VERSIONFILE, version)
        update_py_version(CONSTFILE, version)
    # ----------------------------------------------------------------------
    # create new changelog
    WLOG(params, '', 'Updating changelog')
    if not params['PREVIEW']:
        git_change_log(FILENAME)
    else:
        git_change_log('tmp.txt')
        preview_log('tmp.txt')
        if new:
            git_remove_tag(version)
    # ----------------------------------------------------------------------
    # if we are in preview mode should we keep these changes and update version
    if params['PREVIEW']:
        uinput = input('Keep changes? [Y]es [N]o:\t')
        if 'Y' in uinput.upper():
            # redo tagging
            git_remove_tag(version)
            git_tag_head(version)
            # update version file and python version file
            update_version_file(VERSIONFILE, version)
            update_py_version(CONSTFILE, version)
            # move the tmp.txt to change log
            shutil.move('tmp.txt', FILENAME)
        else:
            os.remove('tmp.txt')
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    config.end(ll, has_plots=False)


# =============================================================================
# End of code
# =============================================================================
