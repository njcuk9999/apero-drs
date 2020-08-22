#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-18 15:15

@author: cook
"""
from apero.base import base
from apero.base import drs_db

from apero.core import constants
from apero.tools.module.database import create_databases

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.core.drs_database2.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__


ParamDict = constants.ParamDict


# =============================================================================
# Define classes
# =============================================================================
class DrsFileDatabase(drs_db.Database):
    def __init__(self, params: ParamDict, name):

        self.name = name
        self.path = create_databases.list_databases(params)



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
