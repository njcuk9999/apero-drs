#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:08

@author: cook



Version 0.0.0
"""

from . import spirouCDB


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
