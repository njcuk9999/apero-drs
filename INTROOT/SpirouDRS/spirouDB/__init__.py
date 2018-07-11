#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou calibration database module

Created on 2017-10-30 at 17:08

@author: cook

"""

from SpirouDRS import spirouConfig
from . import spirouCDB
from . import spirouTDB

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouDB.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['CopyCDBfiles', 'GetAcqTime', 'GetCalibDatabase', 'GetCalibFile',
           'PutCalibFile', 'UpdateCalibMaster', 'CopyTDBfiles',
           'GetTelluDatabase', 'GetTelluFile', 'PutTelluFile',
           'UpdateTelluMaster']

# =============================================================================
# Function aliases
# =============================================================================
CopyCDBfiles = spirouCDB.copy_files

GetAcqTime = spirouCDB.get_acquisition_time

GetCalibDatabase = spirouCDB.get_database

GetCalibFile = spirouCDB.get_file_name

PutCalibFile = spirouCDB.put_file

UpdateCalibMaster = spirouCDB.update_datebase

CopyTDBfiles = spirouTDB.copy_files

GetTelluDatabase = spirouTDB.get_database

GetTelluFile = spirouTDB.get_file_name

PutTelluFile = spirouTDB.put_file

UpdateTelluMaster = spirouTDB.update_datebase

# =============================================================================
# End of code
# =============================================================================
