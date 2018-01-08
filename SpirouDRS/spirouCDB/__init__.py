#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:08

@author: cook



Version 0.0.0
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
__all__ = ['CopyCDBfiles',
           'GetAcqTime',
           'GetDatabase',
           'GetFile',
           'PutFile',
           'UpdateMaster']

# =============================================================================
# Function aliases
# =============================================================================
# copy calib database files to folder
CopyCDBfiles = spirouCDB.copy_files

# Gets the acquisition time for use in getting the database entries
GetAcqTime = spirouCDB.get_acquision_time

# Gets all entries from calibDB where unix time <= max_time
GetDatabase = spirouCDB.get_database

# Gets a filename from the calibDB
GetFile = spirouCDB.get_file_name

# Copies the "inputfile" to the calibDB folder
PutFile = spirouCDB.put_file

# Updates (or creates) the calibDB with an entry or entries in the form:
#    {key} {arg_night_name} {filename} {human_time} {unix_time}
UpdateMaster = spirouCDB.update_datebase

# =============================================================================
# End of code
# =============================================================================
