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

# Gets all entries from calibDB where unix time <= max_time
GetDatabase = spirouCDB.get_database

# Copies the "inputfile" to the calibDB folder
PutFile = spirouCDB.put_file

# Updates (or creates) the calibDB with an entry or entries in the form:
#    {key} {arg_night_name} {filename} {human_time} {unix_time}
UpdateMaster = spirouCDB.update_datebase
