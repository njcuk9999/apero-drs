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

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    setup(name='apero-drs',
          packages=find_packages(),
          # version=get_version(),
          # scripts=load_scripts(),
          include_package_data=True)


# =============================================================================
# End of code
# =============================================================================

