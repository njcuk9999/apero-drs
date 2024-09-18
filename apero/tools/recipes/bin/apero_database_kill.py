#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-05-18

@author: cook
"""
from apero.base import base
from apero.core.constants import load_functions
from apero.tools.module.database import manage_databases


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_database_kill.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # load params
    params = load_functions.load_config()
    # kill all user processes in the database that have been running for
    manage_databases.kill(params, timeout=60)


# =============================================================================
# End of code
# =============================================================================
