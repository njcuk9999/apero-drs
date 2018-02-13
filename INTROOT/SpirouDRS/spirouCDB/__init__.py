#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou calibration database module

Created on 2017-10-30 at 17:08

@author: cook

"""

from SpirouDRS import spirouConfig
from . import spirouCDB

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouCDB.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['CopyCDBfiles', 'GetAcqTime', 'GetDatabase', 'GetFile',
           'PutFile', 'UpdateMaster']

# =============================================================================
# Function aliases
# =============================================================================
CopyCDBfiles = spirouCDB.copy_files

GetAcqTime = spirouCDB.get_acquisition_time

GetDatabase = spirouCDB.get_database

GetFile = spirouCDB.get_file_name

PutFile = spirouCDB.put_file

UpdateMaster = spirouCDB.update_datebase

# =============================================================================
# End of code
# =============================================================================
