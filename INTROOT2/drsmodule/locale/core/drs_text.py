#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Text functions

NOTE: CANNOT IMPORT ANY DRS MODULES

Created on 2019-01-22 at 09:53

@author: cook
"""
import numpy as np
import os
from astropy.table import Table
from collections import OrderedDict
import pkg_resources

from . import drs_exceptions

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
# must be csv files
HELP_FILES = ['help.csv']
ERROR_FILES = ['error.csv']
DEFAULT_LANGUAGE = 'ENG'
# define escape characters
ESCAPE_CHARS = {'\n': '\\n', '\t': '\\t'}
# get the Drs Exceptions
DrsError = drs_exceptions.DrsError
DrsWarning = drs_exceptions.DrsWarning
TextError = drs_exceptions.TextError
TextWarning = drs_exceptions.TextWarning
ConfigError = drs_exceptions.ConfigError
ConfigWarning = drs_exceptions.ConfigWarning


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
            emsg = 'Cannot load Abstract class "{0}"'
            TextError(message=emsg.format(self.name), level='error')
        # deal with no dict loaded
        if len(self.dict) == 0:
            emsg = '"{0}" dictionary not loaded. Please load using {0}.{1}'
            eargs = [self.name, self.load_func]
            TextError(message=emsg.format(*eargs), level='error')
        if key not in self.dict:
            emsg = 'Key "{0}" not found in {1} translation matrix.'
            eargs = [key, self.name]
            TextError(message=emsg.format(*eargs), level='error')
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
                args = [[]]*len(key)
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
        """
        Use a Text, ErrorText or HelpText instance (the translation matrix
        object) to turn Entry into a valid python string

        :param tobj: Text, ErrorText or HelpText instance, the translation
                     matrix object
        :param report: bool, if True adds a "name" for the Entry and the
                       key-code used to identify it (i.e. Error[00-000-00000])
        :param reportlevel: string or None, the "name" for the report i.e.
                            if report is True:
                                 "Reportlevel[00-000-00000]" is printed infront
                                 of level
        :return:
        """
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
                args = self._convert_args(it, tobj)
                kwargs = self._convert_kwargs(tobj)
                msg_value = key.format(*args, **kwargs)
                valuestr += '{1}'.format(reportlevel, msg_value)
            elif tobj is not None:
                args = self._convert_args(it, tobj)
                kwargs = self._convert_kwargs(tobj)
                msg_value = tobj[key].format(*args, **kwargs)
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

    def _convert_args(self, it, tobj):
        """
        Convert args that are Entry, ErrorEntry and HelpEntry to strings
        based on tobj

        :param it: int, the iteration of args to convert
        :param tobj: Text, ErrorText or HelpText instance, the translation
                     matrix object

        :return args: list, the list of args (where Entry, ErrorEntry and
                      HelpEntry values are now strings)
        """
        # get raw arguments for this iteration
        raw_args = self.args[it]
        # storage for args
        args = []
        # loop around raw_args and look for entries - we need to translate them
        # now
        for raw_arg in raw_args:
            if type(raw_arg) in [Entry, ErrorEntry, HelpEntry]:
                args.append(raw_arg.get(tobj, report=False))
            else:
                args.append(raw_arg)
        # return args
        return args

    def _convert_kwargs(self, tobj):
        """
        Convert kwargs that are Entry, ErrorEntry and HelpEntry to strings
        based on tobj

        :param tobj: Text, ErrorText or HelpText instance, the translation
                     matrix object
        :return kwargs: dictionary, the dictionary of kwargs (where Entry,
                        ErrorEntry and HelpEntry values are now strings)
        """
        # loop around kwargs
        kwargs = dict()
        for kwarg in self.kwargs:
            if type(self.kwargs[kwarg]) in [Entry, ErrorEntry, HelpEntry]:
                kwargs[kwarg] = self.kwargs[kwarg].get(tobj, report=False)
            else:
                kwargs[kwarg] = self.kwargs[kwarg]
        # return kwargs
        return kwargs


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

        # add args
        args = self.args + self2.args
        kwargs = self.kwargs
        for kwarg2 in self2.kwargs:
            kwargs[kwarg2] = self2.kwargs[kwarg2]
        return HelpEntry(keys, args, kwargs)


# =============================================================================
# Define private functions
# =============================================================================
def _get_dict_files(instrument, filelist):
    # setup storage for return file list
    return_files = []
    # get instrument path
    ifolder = _get_relative_folder(PACKAGE, INSTRUMENT_PATH)
    # get default file
    dfolder = _get_relative_folder(PACKAGE, DEFAULT_PATH)
    dfiles = []
    for file_d in filelist:
        abspath_d = os.path.join(dfolder, file_d)
        if os.path.exists(abspath_d):
            dfiles.append(abspath_d)
        else:
            wmsg = 'DRS Warning: Language file "{0}" not found.'
            TextWarning(wmsg.format(file_d), level='warning')
    if len(dfiles) == 0:
        emsg = 'DRS Error: No language files found.'
        TextError(emsg, level='error')
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
            iargs = [dfilename.split(ext)[0], instrument.lower(), ext]
            ifilename = '{0}_{1}{2}'.format(*iargs)
            # construct full path for ifilename
            ifilepath = os.path.join(ifolder, ifilename)
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
        cachedfile = filename.replace('.csv', newext)
        if os.path.exists(cachedfile):
            # get the data
            data = np.load(cachedfile)
            columns = data.dtype.names
        else:
            # try to get the data
            try:
                data = Table.read(filename, format='ascii.csv',
                                  fast_reader=False)
            except Exception as e:
                emsg1 = 'Error opening file "{0}"'.format(filename)
                emsg2 = '\n\t Error {0}: {1}'.format(type(e), e)
                raise TextError(emsg1 + emsg2)

            # get the columns names
            columns = data.colnames
            # fill values to "N/A"
            data = data.filled()
            # save to file
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
            if str(data[col][row]) in ['--', 'N/A', 'inf', '999999']:
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
