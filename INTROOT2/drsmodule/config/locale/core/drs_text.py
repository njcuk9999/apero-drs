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


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_text.py'
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

ESCAPE_CHARS = {'\n':'\\n', '\t':'\\t'}


# -----------------------------------------------------------------------------
class TextException(Exception):
    """Raised when config file is incorrect"""
    pass


class TextError(TextException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message=None, level=None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        """
        # deal with message
        if message is None:
            self.message = 'Text Error'
        elif type(message) == str:
            self.message = message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level
        # deal with a list message (for printing)
        if type(self.message) == list:
            amessage = ''
            for mess in message:
                amessage += '\n\t\t{0}'.format(mess)
            message = amessage
        # set args to message (for printing)
        argmessage = 'level={0}: {1}'
        self.args = (argmessage.format(self.level, message),)

    # overwrite string repr message with args[0]
    def __repr__(self):
        """
        String representation of ConfigError

        :return message: string, the message assigned in constructor
        """
        return self.args[0]

    # overwrite print message with args[0]
    def __str__(self):
        """
        String printing of ConfigError

        :return message: string, the message assigned in constructor
        """
        return self.args[0]


# =============================================================================
# Define functions
# =============================================================================
class Text:
    def __init__(self, instrument, language):
        self.name = 'Text'
        self.load_func = '_load_dict()'
        self.instrument = instrument
        self.language = language
        self.dict = ParamDict()
        self.sources = []
        self.kind = dict()
        self.comment = dict()

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __delitem__(self, key):
        self.dict.__delitem__(key)

    def get(self, key):
        if self.name == 'Text':
            emsg = 'Dev Error: Cannot load Abstract class "{0}"'
            raise TextError(message=emsg.format(self.name), level='error')
        # deal with no dict loaded
        if len(self.dict) == 0:
            emsg = '"{0}" dictionary not loaded. Please load using {0}.{1}'
            eargs = [self.name, self.load_func]
            raise TextError(message=emsg.format(*eargs), level='error')
        if key not in self.dict:
            emsg = 'Key "{0}" not found in {1} translation matrix.'
            eargs = [key, self.name]
            raise TextError(message=emsg.format(*eargs), level='error')
        return self.dict[key]

    def getsouce(self, key):
        return self.dict.sources[key]

    def _load_dict(self, filelist):
        # get files to check
        dict_files = _get_dict_files(self.instrument, filelist)
        # read dict files
        out = _read_dict_files(dict_files, self.language)
        values, sources, kinds, comments = out
        # append to Parameter dictionary
        for key in list(values.keys()):
            # clean values (escape characters)
            value = values[key]
            for char in ESCAPE_CHARS:
                value = value.replace(ESCAPE_CHARS[char], char)
            # add to dict
            self.dict[key] = value
            self.dict.set_source(key, sources[key])
            # other values
            self.kind[key] = kinds[key]
            self.comment = comments[key]


class ErrorText(Text):
    def __init__(self, instrument, language):
        Text.__init__(self, instrument, language)
        self.name = 'ErrorText'
        self.load_func = '_load_dict_error()'
        self._load_dict_error()

    def _load_dict_error(self):
        self._load_dict(ERROR_FILES)


class HelpText(Text):
    def __init__(self, instrument, language):
        Text.__init__(self, instrument, language)
        self.name = 'HelpText'
        self.load_func = '_load_dict_help()'
        self._load_dict_help()

    def _load_dict_help(self):
        self._load_dict(HELP_FILES)


class Entry:
    def __init__(self, key):
        self.name = 'Entry'
        self.short = ''
        self.key = key

    def __str__(self):
        return('{0}[{1}]'.format(self.name, self.key))

    def __repr__(self):
        return('{0}[{1}]'.format(self.name, self.key))

    def print(self):
        return('{0}{1}: '.format(self.short, self.key))


class ErrorEntry(Entry):
    def __init__(self, key):
        self.key = key
        Entry.__init__(self, key)
        self.name = 'ErrorEntry'
        self.short = 'Error '

class HelpEntry(Entry):
    def __init__(self, key):
        self.key = key
        Entry.__init__(self, key)
        self.name = 'HelpEntry'
        self.short = ''


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
    kind_dict = OrderedDict()
    comment_dict = OrderedDict()

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
            # check if masked (and use default language)
            if str(data[col][row]) == '--':
                col = DEFAULT_LANGUAGE
            # get this row/columns values
            value = str(data[col][row])
            kind = str(data['KIND'])
            comment = str(data['COMMENT']) + 'Args: ' + str(data['ARGUMENTS'])
            source = filename
            # append to dictionaries
            value_dict[key] = value
            source_dict[key] = source
            kind_dict[key] = kind
            comment_dict[key] = comment
    # return dictionaries
    return value_dict, source_dict, kind_dict, comment_dict


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
