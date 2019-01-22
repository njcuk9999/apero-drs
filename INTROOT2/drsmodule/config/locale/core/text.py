#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-22 at 09:53

@author: cook
"""
from astropy.table import Table
import os
from collections import OrderedDict

from drsmodule import constants
from drsmodule.config.math import time


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'text.py'
__INSTRUMENT__ = None
# Define package name
PACKAGE = 'drsmodule'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get the parameter dictionary
ParamDict = constants.ParamDict
# file locations
DEFAULT_PATH = './config/locale/databases/'
INSTRUMENT_PATH = './config/locale/databases/'
HELP_FILES = ['help.csv']
ERROR_FILES = ['error.csv']
FILE_FMT = 'csv'
DEFAULT_LANGUAGE = 'ENG'
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
class Text:
    def __init__(self, instrument, language):
        self.instrument = instrument
        self.language = language
        self.dict = ParamDict()

    def get(self, key):
        return self.dict[key]

    def getsouce(self, key):
        return self.dict.sources[key]

    def _load_dict(self, filelist):
        # get files to check
        dict_files = _get_dict_files(self.instrument, filelist)
        # read dict files
        values, sources = _read_dict_files(dict_files, self.language)
        # append to Parameter dictionary
        for key in list(values.keys()):
            self.dict[key] = values[key]
            self.dict.set_source(key, sources[key])

class ErrorText(Text):
    def __init__(self, instrument, language):
        Text.__init__(self, instrument, language)
        self._load_dict_error()

    def _load_dict_error(self):
        self._load_dict(ERROR_FILES)


class HelpText(Text):
    def __init__(self, instrument, language):
        Text.__init__(self, instrument, language)

    def _load_dict_help(self):
        self._load_dict(HELP_FILES)


# =============================================================================
# Define functions
# =============================================================================
def _get_dict_files(instrument, filelist):
    # setup storage for return file list
    return_files = []
    # get default file
    dfiles = constants.get_filenames(file_list=filelist,
                                     default_path=DEFAULT_PATH)
    # add the default files to return file list
    return_files += dfiles
    # loop around files in dmods
    for it in range(len(dfiles)):
        # get the default filename
        dfilename = str(os.path.basename(dfiles[it]))
        # get extension of default file
        if '.' in dfilename:
            ext = '.' + dfilename.split('.')[-1]
        else:
            ext = ''
        # check for instrument file
        if instrument is None:
            continue
        else:
            # remove extension add instrument name and readd extension
            iargs = [dfilename.split(ext), instrument.lower(), ext]
            ifilename = '{0}_{1}{2}'.format(*iargs)
            # construct full path for ifilename
            ifilepath = os.path.join(INSTRUMENT_PATH, ifilename)

            # check for ifilename existence
            if os.path.exists(ifilepath):
                return_files.append(ifilepath)
    # finally return files
    return return_files


def _read_dict_files(dict_files, language):

    # storage for outputs
    value_dict = OrderedDict()
    source_dict = OrderedDict()

    # loop around files
    for filename in dict_files:
        # get the data
        data = Table.read(filename, format=FILE_FMT)
        # deal with bad language
        if (language not in data.colnames):
            col = DEFAULT_LANGUAGE
        else:
            col = str(language)
        # append to dictionary and overwrite older values
        for row in range(len(data['KEY'])):
            key = str(data['KEY'][row])
            value = str(data[col][row])
            source = filename
            value_dict[key] = value
            source_dict[key] = source

    return value_dict, source_dict

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
