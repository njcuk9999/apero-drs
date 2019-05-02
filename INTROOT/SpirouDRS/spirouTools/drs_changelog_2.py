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

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from datetime import datetime

# =============================================================================
# Define variables
# Name of program
__NAME__ = 'drs_changelog.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get constants
CONSTANTS = spirouConfig.Constants
# -----------------------------------------------------------------------------
rargs = [CONSTANTS.PACKAGE(), '../../']
PATH = spirouConfig.spirouConfigFile.get_relative_folder(*rargs)
FILENAME = os.path.join(PATH, 'changelog.md')
VERSIONFILE = os.path.join(PATH, 'VERSION.txt')
rargs = [CONSTANTS.PACKAGE(), './spirouConfig']
CONSTPATH = spirouConfig.spirouConfigFile.get_relative_folder(*rargs)
CONSTFILE = os.path.join(CONSTPATH, 'spirouConst.py')

VERSIONSTR = '__version__ = '
DATESTR = '__date__ = '

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
        if line.startswith(VERSIONSTR):
            version_it = it
        if line.startswith(DATESTR):
            date_it = it
    # update version
    lines[version_it] = '{0} \'{1}\'\n'.format(VERSIONSTR.strip(), version)
    # update date
    dt = datetime.now()
    dargs = [DATESTR.strip(), dt.year, dt.month, dt.day]
    lines[date_it] = '{0} \'{1:04d}-{2:02d}-{3:02d}\'\n'.format(*dargs)
    # write lines
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()
    # remove backup
    os.remove(filename + '.backup')


def main():
    # ----------------------------------------------------------------------
    # get values from config file
    p = spirouStartup.Begin(recipe=__NAME__, quiet=True)

    WLOG(p, '', 'Reading DRS version')
    # set new version
    version = ask_for_new_version()
    # add tag of version
    if version is not None:
        # tag head with version
        git_tag_head(version)
    else:
        version = str(__version__)

    # update DRS files
    update_version_file(VERSIONFILE, version)
    update_py_version(CONSTFILE, version)

    # create new changelog
    WLOG(p, '', 'Updating changelog')
    git_change_log(FILENAME)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)


# =============================================================================
# End of code
# =============================================================================
