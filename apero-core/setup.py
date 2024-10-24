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
# dev mode
DEV_MODE = False


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
        with open('aperocore/info.yaml', 'r') as vfile:
            vtext = vfile.readlines()
    except Exception as e:
        print('Error: Could not read version file')
        print('Error: {0}'.format(e))
        sys.exit(1)
    # return version
    return vtext[1].split(':')[-1].strip()


def load_requirements() -> list:
    """
    Load requirements from file
    :return:
    """
    requirements = 'requirements.txt'
    # storage for list of modules
    modules = []
    # open requirements file
    with open(requirements, 'r') as rfile:
        lines = rfile.readlines()
    # get modules from lines in requirements file
    for line in lines:
        if len(line) == '':
            continue
        if line.startswith('#'):
            continue
        else:
            modules.append(line)
    # return modules
    return modules


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    setup(name='aperocore',
          packages=['aperocore', 'aperocore.base',
                    'aperocore.constants', 'aperocore.core',
                    'aperocore.drs_lang', 'aperocore.drs_lang.tables',
                    'aperocore.math'],
          version=get_version(),
          url='http://apero.exoplanets.ca',
          license='MIT',
          author='Neil Cook',
          author_email='neil.james.cook@gmail.com',
          description=('Core functionality of APERO projects'),
          install_requires=load_requirements(),
          include_package_data=True)


# =============================================================================
# End of code
# =============================================================================
