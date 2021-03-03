#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup.py function - test stage - DO NOT USE

Created on 2019-01-17 at 15:24

@author: cook
"""
from setuptools import setup
import sys

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
def load_requirements() -> list:
    """
    Load requirements from file
    :return:
    """
    if '--dev' in sys.argv:
        requirements = '../requirements_current.txt'
        # remove dev from arguments
        pos = sys.argv.index('--dev')
        sys.argv.pop(pos)

    else:
        requirements = '../requirements_current.txt'
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
    setup(name='apero',
          version='0.7.035dev',
          packages=['apero', 'apero.base', 'apero.core', 'apero.core.core',
                    'apero.core.math', 'apero.core.utils', 'apero.core.constants',
                    'apero.core.instruments', 'apero.core.instruments.spirou',
                    'apero.core.instruments.default',
                    'apero.core.instruments.nirps_ha',
                    'apero.lang', 'apero.lang.core', 'apero.tools',
                    'apero.tools.module', 'apero.tools.module.gui',
                    'apero.tools.module.error', 'apero.tools.module.setup',
                    'apero.tools.module.utils', 'apero.tools.module.listing',
                    'apero.tools.module.testing', 'apero.tools.module.database',
                    'apero.tools.module.processing',
                    'apero.tools.module.visulisation',
                    'apero.tools.module.documentation', 'apero.science',
                    'apero.science.calib', 'apero.science.polar',
                    'apero.science.extract', 'apero.science.telluric',
                    'apero.science.velocity', 'apero.science.preprocessing',
                    'apero.plotting'],
          package_dir={'': 'apero'},
          url='http://venus.astro.umontreal.ca/~cook/apero-drs',
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

