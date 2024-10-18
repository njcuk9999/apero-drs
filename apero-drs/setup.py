#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup.py function - test stage - DO NOT USE

Created on 2019-01-17 at 15:24

@author: cook
"""
import sys
import os
from pathlib import Path

from setuptools import setup, find_packages

# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'setup.py'
# Get the package directory from this file name
PACKAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

SCRIPT_PATHS = [os.path.join('apero', 'tools', 'recipes', 'bin'),
                os.path.join('apero', 'tools', 'recipes', 'dev'),
                os.path.join('apero', 'tools', 'recipes', 'utils')]

# =============================================================================
# Define functions
# =============================================================================
def get_version() -> str:
    """
    Get the version from the version file
    :return:
    """
    # copy version.txt file to apero-core
    if os.path.exists('version.txt'):
        os.remove('version.txt')
    shutil.copy('../version.txt', 'version.txt')
    # try to open version file
    try:
        with open('version.txt', 'r') as vfile:
            vtext = vfile.readlines()
    except Exception as e:
        print('Error: Could not read version file')
        print('Error: {0}'.format(e))
        sys.exit(1)
    # return version
    return vtext[0]


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



def load_scripts() -> list:
    """
    Load scripts from file
    :return:
    """
    scripts = []
    # loop around script paths
    for strpath in SCRIPT_PATHS:
        path = PACKAGE_DIR.joinpath(strpath)
        # loop around files in path
        for filepath in path.iterdir():
            if filepath.name == '__init__.py':
                continue
            if filepath.is_file() and os.access(filepath, os.X_OK):
                scripts.append(os.path.relpath(str(filepath)))
    # return modules
    return scripts


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    setup(name='apero',
          packages=find_packages(),
          version=get_version(),
          scripts=load_scripts(),
          url='http://apero.exoplanets.ca',
          license='MIT',
          author='Neil Cook',
          author_email='neil.james.cook@gmail.com',
          description=('APERO is a pipeline designed to reduce astrophysical '
                       'observations (specifically from echelle spectrographs). '
                       'It is the offical pipeline for SPIRou and is also '
                       'used for NIRPS.'),
          install_requires=load_requirements(),
          include_package_data=True)


# =============================================================================
# End of code
# =============================================================================

