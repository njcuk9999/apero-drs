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
WLOG = config.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
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
    params = config.end_main(params, success, outputs=None)
    # return a copy of locally defined variables in the memory
    return config.get_locals(dict(locals()), llmain)


def __main__(recipe, params):

    # get the text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # ----------------------------------------------------------------------
    # if in preview mode tell user
    if params['INPUTS']['PREVIEW']:
        WLOG(params, 'info', TextEntry('40-501-0008'))
    # ----------------------------------------------------------------------
    # read and ask for new version
    WLOG(params, '', TextEntry('40-501-0009'))
    # set new version
    version = ask_for_new_version(params)
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
    if not params['INPUTS']['PREVIEW']:
        update_version_file(VERSIONFILE, version)
        update_py_version(CONSTFILE, version)
    # ----------------------------------------------------------------------
    # create new changelog
    # log that we are updating the change log
    WLOG(params, '', TextEntry('40-501-0010'))
    # if not in preview mode modify the changelog directly
    if not params['INPUTS']['PREVIEW']:
        git_change_log(FILENAME)
    # else save to a tmp file
    else:
        git_change_log('tmp.txt')
        preview_log('tmp.txt')
        # if the version is new make sure this version is not a git tag
        #    already (won't fail if we don't have the tag)
        if new:
            git_remove_tag(version)
    # ----------------------------------------------------------------------
    # if we are in preview mode should we keep these changes and update version
    if params['INPUTS']['PREVIEW']:
        # ask whether to keep changes
        uinput = input(textdict['40-501-0011'] + ' [Y]es [N]o:\t')
        # if we want to keep the changes apply changes from above
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
