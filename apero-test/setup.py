#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup.py function - test stage - DO NOT USE

Created on 2019-01-17 at 15:24

@author: cook
"""
import sys

from setuptools import setup

# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'setup.py'


# =============================================================================
# Define functions
# =============================================================================
def get_version() -> str:
    """
    Get the version from the version file
    :return:
    """
    # try to open version file
    try:
        with open('aperotest/info.yaml', 'r') as vfile:
            vtext = vfile.readlines()
    except Exception as e:
        print('Error: Could not read version file')
        print('Error: {0}'.format(e))
        sys.exit(1)
    # return version
    return vtext[1].split(':')[-1].strip()

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    setup(version=get_version())

# =============================================================================
# End of code
# =============================================================================

