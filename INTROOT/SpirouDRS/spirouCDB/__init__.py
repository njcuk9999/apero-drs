#!/usr/bin/env python3
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
__all__ = ['CopyCDBfiles',
           'GetAcqTime',
           'GetDatabase',
           'GetFile',
           'PutFile',
           'UpdateMaster']

# =============================================================================
# Function aliases
# =============================================================================
CopyCDBfiles = spirouCDB.copy_files
"""
Copy the files from calibDB to the reduced folder
   p['DRS_DATA_REDUC']/p['arg_night_name']
based on the latest calibDB files from header, if there is not header file
use the parameter dictionary "p" to open the header in 'arg_file_names[0]'

:param p: dictionary, parameter dictionary
:param header: dictionary, the header dictionary created by
               spirouFITS.ReadImage

:return None:
"""

GetAcqTime = spirouCDB.get_acquisition_time
"""
Get the acquision time from the header file, if there is not header file
use the parameter dictionary "p" to open the header in 'arg_file_names[0]'

:param p: dictionary, parameter dictionary
:param header: dictionary, the header dictionary created by
               spirouFITS.ReadImage
:param kind: string, 'human' for 'YYYY-mm-dd-HH-MM-SS.ss' or 'unix'
             for time since 1970-01-01
:param filename: string or None, location of the file if header is None

:return acqtime: string, the human or unix time from header file
"""

GetDatabase = spirouCDB.get_database
"""
Gets all entries from calibDB where unix time <= max_time. If update is
False then will first search for and use 'calibDB' in p (if it exists)

:param p: dictionary, parameter dictionary
:param max_time: str, maximum time allowed for all calibDB entries
                 format = (YYYY-MM-DD HH:MM:SS.MS)
:param update: bool, if False looks for "calibDB' in p, and if found does
               not load new database

:return c_database: dictionary, the calibDB database in form:

                c_database[key] = [dirname, filename]

    lines in calibDB must be in form:

        {key} {dirname} {filename} {human_time} {unix_time}

:return p: dictionary, parameter dictionary
"""

GetFile = spirouCDB.get_file_name
"""
Get the filename for "key" in the calibration database (for use when
the calibration database is not needed for more than one use and does
not exist already (i.e. called via spirouCDB.GetDatabase() )

:param p: parameter dictionary, the parameter dictionary containing
          constants
:param key: string, the key to look for in the calibration database
:param hdr: dict or None, the header dictionary to use to get the
            acquisition time, if hdr is None code tries to get
            header from p['arg_file_names'][0]
:param filename: string or None, if defined this is the filename returned
                 (means calibration database is not used)

:return read_file: string, the filename in calibration database for
                   "key" (selected via unix_time in calibDB)
"""

PutFile = spirouCDB.put_file
"""
Copies the "inputfile" to the calibration database folder

:param p: dictionary, parameter dictionary
:param inputfile: string, the input file path and file name

:return None:
"""

UpdateMaster = spirouCDB.update_datebase
"""
Updates (or creates) the calibDB with an entry or entries in the form:

    {key} {arg_night_name} {filename} {human_time} {unix_time}

where arg_night_name comes from p["arg_night_name']
where "human_time" and "unix_time" come from the filename headers (hdrs)
    using HEADER_KEY = timekey (or "ACQTIME1" if timekey=None)


:param p: dictionary, parameter dictionary

:param keys: string or list of strings, keys to add to the calibDB

:param filenames: string or list of strings, filenames to add to the
                  calibDB, if keys is a list must be a list of same length
                  as "keys"

:param hdrs: dictionary or list of dictionaries, header dictionary/
             dictionaries to find 'timekey' in - the acquisition time,
             if keys is a list must be a list of same length  as "keys"

:param timekey: string, key to find acquisition time in header "hdr" if
                None defaults to the program default ('ACQTIME1')

:return None:
"""

# =============================================================================
# End of code
# =============================================================================
