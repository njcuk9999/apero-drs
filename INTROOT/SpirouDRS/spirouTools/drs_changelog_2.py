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


# =============================================================================
# Define variables
# =============================================================================
__version__ = spirouConfig.Constants.VERSION()
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def ask_for_new_version():
    print('Current version is {0}'.format(__version__))
    uinput1 = str(input('\n\t New version required? [Y]es or [N]o:\t'))

    if 'Y' in uinput1.upper():
        cond = True
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



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # set new version
    version = ask_for_new_version()
    # add tag of version
    if version is not None:
        # tag head with version
        git_tag_head(version)

        # create new changelog



# =============================================================================
# End of code
# =============================================================================
