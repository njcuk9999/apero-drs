#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Text functions

NOTE: CANNOT IMPORT ANY DRS MODULES

Created on 2019-01-22 at 09:53

@author: cook
"""
import numpy as np
from astropy.time import Time
import os
import sys
from astropy.table import Table
from collections import OrderedDict
import pkg_resources
import warnings


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_text.py'
__INSTRUMENT__ = None
# Define package name
PACKAGE = 'drsmodule'
# file locations
DEFAULT_PATH = './locale/databases/'
INSTRUMENT_PATH = './locale/databases/'
HELP_FILES = ['help.csv']
ERROR_FILES = ['error.csv']
FILE_FMT = 'csv'
DEFAULT_LANGUAGE = 'ENG'
# define escape characters
ESCAPE_CHARS = {'\n': '\\n', '\t': '\\t'}


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
        self.dict = OrderedDict()
        self.sources = OrderedDict()
        self.kind = OrderedDict()
        self.comment = OrderedDict()

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
        return self.sources[key]

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
            self.sources[key] = sources[key]
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
    def __init__(self, key, args=None, kwargs=None):
        self.name = 'Entry'
        self.short = ''
        # make keys a list
        if type(key) is list:
            self.keys = key
            if args is None:
                args = [[]*len(key)]
            self.args = args
        else:
            self.keys = [key]
            if args is None:
                args = []
            self.args = [args]
        # add keyword args
        if kwargs is None:
            self.kwargs = dict()
        else:
            self.kwargs = kwargs

    def __str__(self):
        value = self.get()
        return value

    def __repr__(self):
        return self.__str__()

    def __add__(self, self2):
        keys = self.keys + self2.keys
        args = self.args + self2.args
        kwargs = self.kwargs
        for kwarg2 in self2.kwargs:
            kwargs[kwarg2] = self2.kwargs[kwarg2]
        return Entry(keys, args, kwargs)

    def get(self, tobj=None, report=False, reportlevel=None):

        # deal with no reportlevel
        if reportlevel is None:
            reportlevel = self.short
        elif type(reportlevel) is str:
            reportlevel = reportlevel.capitalize()
        else:
            reportlevel = self.short

        valuestr = ''
        for it, key in enumerate(self.keys):
            # get msg_value with args/kwargs
            if (tobj is not None) and (key not in tobj.dict):
                msg_value = key.format(*self.args[it], **self.kwargs)
                valuestr += '{1}'.format(reportlevel, msg_value)
            elif tobj is not None:
                msg_value = tobj[key].format(*self.args[it], **self.kwargs)
                vargs = [reportlevel, key, msg_value]
                if report:
                    valuestr += '{0}[{1}]: {2}'.format(*vargs)
                else:
                    valuestr += '{2}'.format(*vargs)
            else:
                valuestr += '{0}[{1}]'.format(reportlevel, key)
            # add separator between list entries
            if (len(self.keys) != 1) and (it != len(self.keys) - 1):
                valuestr += '\n'
        # return string
        return valuestr

    def convert(self, obj):
        return obj(self.keys, self.args, self.kwargs)


class ErrorEntry(Entry):
    def __init__(self, key, args=None, kwargs=None):
        Entry.__init__(self, key, args, kwargs)
        self.name = 'ErrorEntry'
        self.short = 'Error'

    def __add__(self, self2):
        keys = self.keys + self2.keys
        args = self.args + self2.args
        kwargs = self.kwargs
        for kwarg2 in self2.kwargs:
            kwargs[kwarg2] = self2.kwargs[kwarg2]
        return ErrorEntry(keys, args, kwargs)


class HelpEntry(Entry):
    def __init__(self, key, args=None, kwargs=None):
        Entry.__init__(self, key, args, kwargs)
        self.name = 'HelpEntry'
        self.short = ''

    def __add__(self, self2):
        keys = self.keys + self2.keys
        args = self.args + self2.args
        kwargs = self.kwargs
        for kwarg2 in self2.kwargs:
            kwargs[kwarg2] = self2.kwargs[kwarg2]
        return HelpEntry(keys, args, kwargs)


# =============================================================================
# Define basic log function (for when we don't have full logger functionality)
#   i.e. within drsmodule.locale or drmodule.constants
#   Note this can't be language specific
# =============================================================================
def basiclogger(message=None, level=None):
    # deal with no level
    if level is None:
        level = 'error'
    # deal with message format (convert to ErrorEntry)
    if message is None:
        message = ['Unknown']
    elif type(message) is str:
        message = [message]
    elif type(message) is not list:
        basiclogger('Basic logger error. Cannot read message="{0}"'
                    ''.format(message), level='error')
    # deal with levels
    if level == 'error':
        exit = True
        key = '{0} | {1} Error | {2} '
    elif level == 'warning':
        exit = False
        key = '{0} | {1} Warning | {2}'
    else:
        exit = False
        key = '{0} | {1} Log | {2}'
    # deal with printing log messages
    for mess in message:
        # get time
        atime = Time.now()
        htime = atime.iso.split(' ')[-1]
        # print log message
        print(key.format(htime, PACKAGE.upper(), mess))
    # deal with exiting
    if exit:
        sys.exit()


# =============================================================================
# Define private functions
# =============================================================================
def _get_dict_files(instrument, filelist):
    # setup storage for return file list
    return_files = []
    # get default file
    dfolder = _get_relative_folder(PACKAGE, DEFAULT_PATH)
    dfiles = []
    for file_d in filelist:
        abspath_d = os.path.join(dfolder, file_d)
        if os.path.exists(abspath_d):
            dfiles.append(abspath_d)
        else:
            warnings.warn('DRS Warning: Language file "{0}" not found.')
    if len(dfiles) == 0:
        raise ValueError('DRS Error: No language files found.')
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


def _get_relative_folder(package, folder):
    """
    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    func_name = __NAME__ + '.get_relative_folder()'
    # get the package.__init__ file path
    try:
        init = pkg_resources.resource_filename(package, '__init__.py')
    except ImportError:
        emsg = 'DRS Error: Package name = "{0}" is invalid (function = {1})'
        raise ValueError(emsg.format(package, func_name))
    # Get the config_folder from relative path
    current = os.getcwd()
    # get directory name of folder
    dirname = os.path.dirname(init)
    # change to directory in init
    os.chdir(dirname)
    # get the absolute path of the folder
    data_folder = os.path.abspath(folder)
    # change back to working dir
    os.chdir(current)
    # test that folder exists
    if not os.path.exists(data_folder):
        emsg = 'DRS Error: Folder "{0}" does not exist in {1}'
        eargs = [os.path.basename(data_folder), os.path.dirname(data_folder)]
        raise ValueError(emsg.format(*eargs))
    # return the absolute data_folder path
    return data_folder


def _read_dict_files(dict_files, language):

    # storage for outputs
    value_dict = OrderedDict()
    source_dict = OrderedDict()
    kind_dict = OrderedDict()
    comment_dict = OrderedDict()

    # loop around files
    for filename in dict_files:
        # check for cached file
        utime = os.path.getmtime(filename)
        newext = '_{0}.npy'.format(utime)
        cachedfile = filename.replace('.' + FILE_FMT, newext)
        if os.path.exists(cachedfile):
            # get the data
            data = np.load(cachedfile)
            columns = data.dtype.names
        else:
            # get the data
            data = Table.read(filename, format=FILE_FMT)
            columns = data.colnames
            np.save(cachedfile, data)
        # append to dictionary and overwrite older values
        for row in range(len(data['KEY'])):
            key = str(data['KEY'][row])
            # deal with bad language
            if language not in columns:
                col = DEFAULT_LANGUAGE
            else:
                col = str(language)
            # check if masked (and use default language)
            if str(data[col][row]) == '--':
                col = DEFAULT_LANGUAGE
            # get this row/columns values
            value = str(data[col][row])
            kind = str(data['KIND'][row])
            args = str(data['ARGUMENTS'][row])
            comment = str(data['COMMENT'][row]) + args
            source = filename + '[{0}]'.format(col)
            # append to dictionaries
            value_dict[key] = value
            source_dict[key] = source
            kind_dict[key] = kind
            comment_dict[key] = comment
    # return dictionaries
    return value_dict, source_dict, kind_dict, comment_dict


# =============================================================================
# End of code
# =============================================================================
