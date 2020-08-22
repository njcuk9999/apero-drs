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

from apero.base import base
from apero.base import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'apero.lang.core.drs_lang_text.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# file locations
DEFAULT_PATH = base.LANG_DEFAULT_PATH
INSTRUMENT_PATH = base.LANG_INSTRUMNET_PATH
# must be csv files
HELP_FILES = ['help.csv']
ERROR_FILES = ['error.csv']
DEFAULT_LANGUAGE = base.DEFAULT_LANG
# define escape characters
ESCAPE_CHARS = {'\n': '\\n', '\t': '\\t'}
# get the Drs Exceptions
DrsError = drs_exceptions.DrsError
DrsWarning = drs_exceptions.DrsWarning
TextError = drs_exceptions.TextError
TextWarning = drs_exceptions.TextWarning
ConfigError = drs_exceptions.ConfigError
ConfigWarning = drs_exceptions.ConfigWarning

# Cached data
CACHE_DATA = dict()


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
        global CACHE_DATA
        # check for type in cached data
        cond1 = self.name in CACHE_DATA
        cond2 = False
        cond3 = False
        # check for instrument in cached data type
        if cond1:
            cond2 = self.instrument in CACHE_DATA[self.name]
        # test for language dictionary in cached instrument type
        if cond2:
            cond3 = self.language in CACHE_DATA[self.name][self.instrument]
        # if we have all three conditions True
        if cond1 and cond2 and cond3:
            # get data from cached data
            out = CACHE_DATA[self.name][self.instrument][self.language]
            values, sources, args, kinds, comments = out
        else:
            # get files to check
            dict_files = _get_dict_files(self.instrument, filelist)
            # read dict files
            out = _read_dict_files(dict_files, self.language)
            values, sources, args, kinds, comments = out
            # save data to cached data
            if self.name not in CACHE_DATA:
                CACHE_DATA[self.name] = dict()
            if self.instrument not in CACHE_DATA[self.name]:
                CACHE_DATA[self.name][self.instrument] = dict()
            CACHE_DATA[self.name][self.instrument][self.language] = out
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
            self.comment[key] = comments[key]

    def __str__(self):
        return 'Text[{0},{1}]'.format(self.instrument, self.language)

    def __repr__(self):
        return 'Text[{0},{1}]'.format(self.instrument, self.language)


class TextDict(Text):
    def __init__(self, instrument, language):
        """
        Accessing the language database via loaded dictionary

        :param instrument:
        :param language:

        :type instrument: str
        :type language: str
        """
        self.instrument = str(instrument)
        self.language = str(language)
        Text.__init__(self, instrument, language)
        self.name = 'TextDict'
        self.load_func = '_load_dict_error()'
        self._load_dict_error()

    def _load_dict_error(self):
        self._load_dict(ERROR_FILES)

    def __str__(self):
        return 'TextDict[{0},{1}]'.format(self.instrument, self.language)

    def __repr__(self):
        return 'TextDict[{0},{1}]'.format(self.instrument, self.language)


class HelpDict(Text):
    def __init__(self, instrument, language):
        Text.__init__(self, instrument, language)
        self.name = 'HelpDict'
        self.load_func = '_load_dict_help()'
        self._load_dict_help()

    def _load_dict_help(self):
        self._load_dict(HELP_FILES)

    def __str__(self):
        return 'HelpDict[{0},{1}]'.format(self.instrument, self.language)

    def __repr__(self):
        return 'HelpDict[{0},{1}]'.format(self.instrument, self.language)


class Entry:
    def __init__(self, key, args=None, kwargs=None):
        self.name = 'Entry'
        self.short = ''
        self.current = 0
        # make args a list if it is a string
        if type(args) is str:
            args = [args]
        elif type(args) in [int, float, bool]:
            args = [str(args)]
        # make keys a list
        if isinstance(key, list):
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

    def __add__(self, other):

        if type(other) == str:
            message2 = TextEntry(other)
            return self + message2
        else:
            keys = self.keys + other.keys
            args = self.args + other.args
            kwargs = self.kwargs
            for kwarg2 in other.kwargs:
                kwargs[kwarg2] = other.kwargs[kwarg2]
            return Entry(keys, args, kwargs)

    def __radd__(self, other):
        if type(other) == str:
            message2 = Entry(other)
            return message2 + self
        else:
            keys = other.keys + self.keys
            args = other.args + self.args
            kwargs = other.kwargs
            for kwarg2 in self.kwargs:
                kwargs[kwarg2] = self.kwargs[kwarg2]
            return Entry(keys, args, kwargs)

    def __len__(self):

        allnone = True
        for key in self.keys:
            if key is not None:
                allnone &= False
        if allnone:
            return 0
        else:
            return len(self.keys)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > (len(self.keys) - 1):
            self.current = 0
            raise StopIteration
        else:
            self.current += 1
            key = self.keys[self.current - 1]
            args = self.args[self.current - 1]
            return Entry(key, args, self.kwargs)

    def __eq__(self, other):
        # if we aren't dealing with Entries then they are not equal
        if not isinstance(other, type(self)):
            return False
        # if we are we have a few extra criteria
        equal = True
        # check keys, args and kwargs
        equal &= self.keys == other.keys
        equal &= self.args == other.args
        equal &= self.kwargs == other.kwargs
        # return whether equal
        return equal

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, item):
        # start thinking item is contained
        contains = True
        # copy keys, args, kwargs
        keys = list(self.keys)
        args = list(self.args)
        kwargs = dict(self.kwargs)
        # check keys, args, kwargs
        # must remove entries to make sure we don't check same entry twice
        for it, key in enumerate(item.keys):
            contains &= (key in keys)
            if key in keys:
                keys.pop(it)
        for it, arg in enumerate(item.args):
            contains &= (arg in args)
            if arg in args:
                args.pop(it)
        for kwarg in item.kwargs:
            contains &= (kwarg in kwargs)
            if kwarg in kwargs:
                del kwargs[kwarg]
        # return critera
        return contains

    def get(self, tobj=None, report=False, reportlevel=None):
        """
        Use a Text, TextDict or HelpDict instance (the translation matrix
        object) to turn Entry into a valid python string

        :param tobj: Text, TextDict or HelpDict instance, the translation
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
            reportlevel = reportlevel[0].upper()
        else:
            reportlevel = self.short

        valuestr = ''
        for it, key in enumerate(self.keys):
            # get msg_value with args/kwargs
            if (tobj is not None) and (key not in tobj.dict):
                args = self._convert_args(it, tobj)
                kwargs = self._convert_kwargs(tobj)
                # deal with msg_value being None
                if key is None:
                    msg_value = ''
                else:
                    # deal with args and kwargs not being defined
                    try:
                        msg_value = key.format(*args, **kwargs)
                    except IndexError:
                        msg_value = key
                    except KeyError:
                        msg_value = key
                valuestr += '{1}'.format(reportlevel, msg_value)
                # add separator between list entries
                if key is None:
                    pass
                elif (len(self.keys) != 1) and (it != len(self.keys) - 1):
                    valuestr += ' '

            elif tobj is not None:
                args = self._convert_args(it, tobj)
                kwargs = self._convert_kwargs(tobj)
                # deal with msg_value being None
                if tobj[key] is None:
                    msg_value = ''
                else:
                    # deal with args and kwargs not being defined
                    try:
                        msg_value = tobj[key].format(*args, **kwargs)
                    except IndexError:
                        msg_value = tobj[key]
                    except KeyError:
                        msg_value = tobj[key]
                vargs = [reportlevel, key, msg_value]
                if report:
                    valuestr += '{0}[{1}]: {2}'.format(*vargs)
                else:
                    valuestr += '{2}'.format(*vargs)
                # add separator between list entries
                if tobj[key] is None:
                    pass
                elif (len(self.keys) != 1) and (it != len(self.keys) - 1):
                    valuestr += ' '
            else:
                valuestr += '{0}[{1}]'.format(reportlevel, repr(key))
                # add separator between list entries
                if (len(self.keys) != 1) and (it != len(self.keys) - 1):
                    valuestr += ' '
        # return string
        return valuestr

    def convert(self, obj):
        return obj(self.keys, self.args, self.kwargs)

    def _convert_args(self, it, tobj):
        """
        Convert args that are Entry, TextEntry and HelpEntry to strings
        based on tobj

        :param it: int, the iteration of args to convert
        :param tobj: Text, TextDict or HelpDict instance, the translation
                     matrix object

        :return args: list, the list of args (where Entry, TextEntry and
                      HelpEntry values are now strings)
        """
        # get raw arguments for this iteration
        raw_args = self.args[it]
        # storage for args
        args = []
        # loop around raw_args and look for entries - we need to translate them
        # now
        for raw_arg in raw_args:
            if type(raw_arg) in [Entry, TextEntry, HelpEntry]:
                args.append(raw_arg.get(tobj, report=False))
            else:
                args.append(raw_arg)
        # return args
        return args

    def _convert_kwargs(self, tobj):
        """
        Convert kwargs that are Entry, TextEntry and HelpEntry to strings
        based on tobj

        :param tobj: Text, TextDict or HelpDict instance, the translation
                     matrix object
        :return kwargs: dictionary, the dictionary of kwargs (where Entry,
                        TextEntry and HelpEntry values are now strings)
        """
        # loop around kwargs
        kwargs = dict()
        for kwarg in self.kwargs:
            if type(self.kwargs[kwarg]) in [Entry, TextEntry, HelpEntry]:
                kwargs[kwarg] = self.kwargs[kwarg].get(tobj, report=False)
            else:
                kwargs[kwarg] = self.kwargs[kwarg]
        # return kwargs
        return kwargs


class TextEntry(Entry):
    def __init__(self, key, args=None, kwargs=None):
        Entry.__init__(self, key, args, kwargs)
        self.name = 'TextEntry'
        self.short = 'E'

    def __add__(self, other):
        if type(other) == str:
            message2 = TextEntry(other)
            return self + message2
        else:
            keys = self.keys + other.keys
            args = self.args + other.args
            kwargs = self.kwargs
            for kwarg2 in other.kwargs:
                kwargs[kwarg2] = other.kwargs[kwarg2]
            return TextEntry(keys, args, kwargs)

    def __radd__(self, other):
        if type(other) == str:
            message2 = TextEntry(other)
            return message2 + self
        else:
            keys = other.keys + self.keys
            args = other.args + self.args
            kwargs = other.kwargs
            for kwarg2 in self.kwargs:
                kwargs[kwarg2] = self.kwargs[kwarg2]
            return TextEntry(keys, args, kwargs)


class HelpEntry(Entry):
    def __init__(self, key, args=None, kwargs=None):
        Entry.__init__(self, key, args, kwargs)
        self.name = 'H'
        self.short = ''

    def __add__(self, other):
        if type(other) == str:
            message2 = HelpEntry(other)
            return self + message2
        else:
            keys = self.keys + other.keys

            # add args
            args = self.args + other.args
            kwargs = self.kwargs
            for kwarg2 in other.kwargs:
                kwargs[kwarg2] = other.kwargs[kwarg2]
            return HelpEntry(keys, args, kwargs)

    def __radd__(self, other):
        if type(other) == str:
            message2 = HelpEntry(other)
            return message2 + self
        else:
            keys = other.keys + self.keys
            args = other.args + self.args
            kwargs = other.kwargs
            for kwarg2 in self.kwargs:
                kwargs[kwarg2] = self.kwargs[kwarg2]
            return HelpEntry(keys, args, kwargs)


# =============================================================================
# Define private functions
# =============================================================================
def _get_dict_files(instrument, filelist):
    # setup storage for return file list
    return_files = []
    # get instrument path
    ifolder = get_relative_folder(__PACKAGE__, INSTRUMENT_PATH)
    # get default file
    dfolder = get_relative_folder(__PACKAGE__, DEFAULT_PATH)
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


def get_relative_folder(package, folder):
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
    arg_dict = OrderedDict()
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
            data = np.load(cachedfile, allow_pickle=True)
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
            arg_dict[key] = args
            source_dict[key] = source
            kind_dict[key] = kind
            comment_dict[key] = comment
    # return dictionaries
    return value_dict, source_dict, arg_dict, kind_dict, comment_dict


# =============================================================================
# End of code
# =============================================================================
