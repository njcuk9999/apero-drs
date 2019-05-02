#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-01 at 17:02

@author: cook
"""

import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

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

    # create new changelog
    WLOG(p, '', 'Updating changelog')
    git_change_log(FILENAME)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
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
