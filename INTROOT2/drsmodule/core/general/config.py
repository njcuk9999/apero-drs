#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 15:24

@author: cook
"""
import os
import importlib
import pkg_resources

from drsmodule.const._package import package
from drsmodule.const.core.default_config import *
from drsmodule.const.core.default_constants import *
from drsmodule.const.core.default_keywords import *


# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'config.py'
# Define package name
PACKAGE = 'drsmodule'
# Define relative path to 'const' sub-package
CONST_PATH = './const/'
# Define config/constant/keyword scripts to open
SCRIPTS = ['default_config.py', 'default_constants.py', 'default_keywords.py']
# Define the Config Exception
ConfigError = package.ConfigError


# -----------------------------------------------------------------------------


# =============================================================================
# Define Custom classes
# =============================================================================
# case insensitive dictionary
class CaseInsensitiveDict(dict):
    """
    Custom dictionary with string keys that are case insensitive
    """

    def __init__(self, *arg, **kw):
        super(CaseInsensitiveDict, self).__init__(*arg, **kw)
        self.__capitalise_keys__()

    def __getitem__(self, key):
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :return value: object, the value stored at position "key"
        """
        key = _capitalise_key(key)
        return super(CaseInsensitiveDict, self).__getitem__(key)

    def __setitem__(self, key, value, source=None):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter
        :param source: string, the source for the parameter
        :return:
        """
        # capitalise string keys
        key = _capitalise_key(key)
        # then do the normal dictionary setting
        super(CaseInsensitiveDict, self).__setitem__(key, value)

    def __contains__(self, key):
        """
        Method to find whether CaseInsensitiveDict instance has key="key"
        used with the "in" operator
        if key exists in CaseInsensitiveDict True is returned else False
        is returned

        :param key: string, "key" to look for in CaseInsensitiveDict instance

        :return bool: True if CaseInsensitiveDict instance has a key "key",
        else False
        """
        key = _capitalise_key(key)
        return super(CaseInsensitiveDict, self).__contains__(key)

    def __delitem__(self, key):
        """
        Deletes the "key" from CaseInsensitiveDict instance, case insensitive

        :param key: string, the key to delete from ParamDict instance,
                    case insensitive

        :return None:
        """
        key = _capitalise_key(key)
        super(CaseInsensitiveDict, self).__delitem__(key)

    def get(self, key, default=None):
        """
        Overrides the dictionary get function
        If "key" is in CaseInsensitiveDict instance then returns this value,
        else returns "default" (if default returned source is set to None)
        key is case insensitive

        :param key: string, the key to search for in ParamDict instance
                    case insensitive
        :param default: object or None, if key not in ParamDict instance this
                        object is returned

        :return value: if key in ParamDict instance this value is returned else
                       the default value is returned (None if undefined)
        """
        # capitalise string keys
        key = _capitalise_key(key)
        # if we have the key return the value
        if key in self.keys():
            return self.__getitem__(key)
        # else return the default key (None if not defined)
        else:
            return default

    def __capitalise_keys__(self):
        """
        Capitalizes all keys in ParamDict (used to make ParamDict case
        insensitive), only if keys entered are strings

        :return None:
        """
        keys = list(self.keys())
        for key in keys:
            # check if key is a string
            if type(key) == str:
                # get value
                value = super(CaseInsensitiveDict, self).__getitem__(key)
                # delete old key
                super(CaseInsensitiveDict, self).__delitem__(key)
                # if it is a string set it to upper case
                key = key.upper()
                # set the new key
                super(CaseInsensitiveDict, self).__setitem__(key, value)


class ParamDict(CaseInsensitiveDict):
    """
    Custom dictionary to retain source of a parameter (added via setSource,
    retreived via getSource). String keys are case insensitive.
    """

    def __init__(self, *arg, **kw):
        """
        Constructor for parameter dictionary, calls dict.__init__
        i.e. the same as running dict(*arg, *kw)

        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        self.sources = CaseInsensitiveDict()
        super(ParamDict, self).__init__(*arg, **kw)

    def __getitem__(self, key):
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :return value: object, the value stored at position "key"
        """
        try:
            return super(ParamDict, self).__getitem__(key)
        except KeyError:
            emsg = ('Config Error: Parameter "{0}" not found in parameter '
                    'dictionary')
            raise ConfigError(emsg.format(key), level='error')

    def __setitem__(self, key, value, source=None):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter
        :param source: string, the source for the parameter
        :return:
        """
        # if we dont have the key in sources set it regardless
        if key not in self.sources:
            self.sources[key] = source
        # if we do have the key only set it if source is not None
        elif source is not None:
            self.sources[key] = source
        # then do the normal dictionary setting
        super(ParamDict, self).__setitem__(key, value)

    def __contains__(self, key):
        """
        Method to find whether ParamDict instance has key="key"
        used with the "in" operator
        if key exists in ParamDict True is returned else False is returned

        :param key: string, "key" to look for in ParamDict instance

        :return bool: True if ParamDict instance has a key "key", else False
        """
        return super(ParamDict, self).__contains__(key)

    def __delitem__(self, key):
        """
        Deletes the "key" from ParamDict instance, case insensitive

        :param key: string, the key to delete from ParamDict instance,
                    case insensitive

        :return None:
        """
        super(ParamDict, self).__delitem__(key)

    def get(self, key, default=None):
        """
        Overrides the dictionary get function
        If "key" is in ParamDict instance then returns this value, else
        returns "default" (if default returned source is set to None)
        key is case insensitive

        :param key: string, the key to search for in ParamDict instance
                    case insensitive
        :param default: object or None, if key not in ParamDict instance this
                        object is returned

        :return value: if key in ParamDict instance this value is returned else
                       the default value is returned (None if undefined)
        """
        # if we have the key return the value
        if key in self.keys():
            return self.__getitem__(key)
        # else return the default key (None if not defined)
        else:
            self.sources[key] = None
            return default

    def set_source(self, key, source):
        """
        Set a key to have sources[key] = source

        raises a ConfigError if key not found

        :param key: string, the main dictionary string
        :param source: string, the source to set

        :return None:
        """
        # capitalise
        key = _capitalise_key(key)
        # only add if key is in main dictionary
        if key in self.keys():
            self.sources[key] = source
        else:
            emsg1 = 'Source cannot be added for key "{0}" '.format(key)
            emsg2 = '     "{0}" is not in Parameter Dictionary'.format(key)
            raise ConfigError([emsg1, emsg2], level='error')

    def append_source(self, key, source):
        """
        Adds source to the source of key (appends if exists)
        i.e. sources[key] = oldsource + source

        :param key: string, the main dictionary string
        :param source: string, the source to set

        :return None:
        """
        # capitalise
        key = _capitalise_key(key)
        # if key exists append source to it
        if key in self.keys() and key in list(self.sources.keys()):
            self.sources[key] += ' {0}'.format(source)
        else:
            self.set_source(key, source)

    def set_sources(self, keys, sources):
        """
        Set a list of keys sources

        raises a ConfigError if key not found

        :param keys: list of strings, the list of keys to add sources for
        :param sources: string or list of strings or dictionary of strings,
                        the source or sources to add,
                        if a dictionary source = sources[key] for key = keys[i]
                        if list source = sources[i]  for keys[i]
                        if string all sources with these keys will = source

        :return None:
        """
        # loop around each key in keys
        for k_it in range(len(keys)):
            # assign the key from k_it
            key = keys[k_it]
            # capitalise
            key = _capitalise_key(key)
            # Get source for this iteration
            if type(sources) == list:
                source = sources[k_it]
            elif type(sources) == dict:
                source = sources[key]
            else:
                source = str(sources)
            # set source
            self.set_source(key, source)

    def append_sources(self, keys, sources):
        """
        Adds list of keys sources (appends if exists)

        raises a ConfigError if key not found

        :param keys: list of strings, the list of keys to add sources for
        :param sources: string or list of strings or dictionary of strings,
                        the source or sources to add,
                        if a dictionary source = sources[key] for key = keys[i]
                        if list source = sources[i]  for keys[i]
                        if string all sources with these keys will = source

        :return None:
        """
        # loop around each key in keys
        for k_it in range(len(keys)):
            # assign the key from k_it
            key = keys[k_it]
            # capitalise
            key = _capitalise_key(key)
            # Get source for this iteration
            if type(sources) == list:
                source = sources[k_it]
            elif type(sources) == dict:
                source = sources[key]
            else:
                source = str(sources)
            # append key
            self.append_source(key, source)

    def set_all_sources(self, source):
        """
        Set all keys in dictionary to this source

        :param source: string, all keys will be set to this source

        :return None:
        """
        # loop around each key in keys
        for key in self.keys():
            # capitalise
            key = _capitalise_key(key)
            # set key
            self.sources[key] = source

    def append_all_sources(self, source):
        """
        Sets all sources to this "source" value

        :param source: string, the source to set

        :return None:
        """

        # loop around each key in keys
        for key in self.keys():
            # capitalise
            key = _capitalise_key(key)
            # set key
            self.sources[key] += ' {0}'.format(source)

    def get_source(self, key):
        """
        Get a source from the parameter dictionary (must be set)

        raises a ConfigError if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        # capitalise
        key = _capitalise_key(key)
        # if key in keys and sources then return source
        if key in self.keys() and key in self.sources.keys():
            return self.sources[key]
        # else raise a Config Error
        else:
            emsg = 'No source set for key={0} in ParamDict'
            raise ConfigError(emsg.format(key), level='error')

    def source_keys(self):
        """
        Get a dict_keys for the sources for this parameter dictionary
        order the same as self.keys()

        :return sources: values of sources dictionary
        """
        return self.sources.keys

    def source_values(self):
        """
        Get a dict_values for the sources for this parameter dictionary
        order the same as self.keys()

        :return sources: values of sources dictionary
        """
        return self.sources.values

    def startswith(self, substring):
        """
        Return all keys that start with this substring

        :param substring: string, the prefix that the keys start with

        :return keys: list of strings, the keys with this substring at the start
        """
        # define return list
        return_keys = []
        # loop around keys
        for key in self.keys():
            # make sure key is string
            if type(key) != str:
                continue
            # if first
            if str(key).startswith(substring.upper()):
                return_keys.append(key)
        # return keys
        return return_keys

    def contains(self, substring):
        """
        Return all keys that contain this substring

        :param substring: string, the sub-string to look for in all keys

        :return keys: list of strings, the keys which contain this substring
        """
        # define return
        # define return list
        return_keys = []
        # loop around keys
        for key in self.keys():
            # make sure key is string
            if type(key) != str:
                continue
            # if first
            if substring.upper() in key:
                return_keys.append(key)
        # return keys
        return return_keys

    def endswith(self, substring):
        """
        Return all keys that end with this substring

        :param substring: string, the suffix that the keys ends with

        :return keys: list of strings, the keys with this substring at the end
        """
        # define return list
        return_keys = []
        # loop around keys
        for key in self.keys():
            # make sure key is string
            if type(key) != str:
                continue
            # if first
            if str(key).endswith(substring.upper()):
                return_keys.append(key)
        # return keys
        return return_keys

    def copy(self):
        # make new copy of param dict
        pp = ParamDict()
        keys = list(self.keys())
        values = list(self.values())
        # loop around keys and add to new copy
        for k_it, key in enumerate(keys):
            value = values[k_it]
            pp[key] = type(value)(value)
            pp.set_source(key, self.sources[key])
        # return new param dict filled
        return pp


# =============================================================================
# Define functions
# =============================================================================
def load_config(instrument=None):

    # get instrument sub-package constants files
    modules = _get_module_names(instrument)

    # get constants from modules
    keys, values, sources = _load_from_module(modules)

    params = ParamDict(zip(keys, values))
    # Set the source
    params.set_sources(keys=keys, sources=sources)

    # TODO: Got to here
    # TODO: Need to get file now (from params?)
    # TODO: Then need to load from file (using module for options/type etc)
    # get instrument user config files
    files = _get_file_names(params, instrument)

    # get constants from user config files
    keys, values, sources = _load_from_file(files, modules)

    # add to params
    for it in range(len(keys)):
        params[keys[it]] = values[it]
    params.set_sources(keys=keys, sources=sources)

    # return the parameter dictionary
    return params


# =============================================================================
# Config loading private functions
# =============================================================================
def _get_file_names(params, instrument=None):

    files = []
    return files


def _get_module_names(instrument=None):
    func_name = __NAME__ + '._get_module_names()'
    # deal with no instrument
    if instrument is None:
        emsg1 = 'Instrument "{0}" is not a valid instrument'.format(instrument)
        emsg2 = '\tBased on "Const" sub-package directories'
        ConfigError([emsg1, emsg2], level='error')
    # get constants package path
    const_path = _get_relative_folder(PACKAGE, CONST_PATH)
    # get the directories within const_path
    filelist = os.listdir(const_path)
    directories = []
    for filename in filelist:
        if os.path.isdir(filename):
            directories.append(filename)
    # construct sub-module name
    relpath = CONST_PATH.replace('.', '').replace(os.sep, '.')
    relpath = relpath.strip('.')

    # construct module import name
    modpath = '{0}.{1}.{2}'.format(PACKAGE, relpath, instrument.lower())
    filepath = os.path.join(const_path, instrument.lower())

    # get module names
    mods, paths = [], []
    for script in SCRIPTS:
        # make sure script doesn't end with .py
        script = script.strip('.py')
        # get mod path
        mod = '{0}.{1}'.format(modpath, script)
        # get file path
        fpath = os.path.join(filepath, script)
        # append if path exists
        if not os.path.exists(fpath):
            emsgs = ['DevError: Const mod path "{0}" does not exist.'
                     ''.format(mod), '\tfunction = {0}'.format(func_name)]
            ConfigError(emsgs, level='error')
        if not os.path.isdir(fpath):
            emsgs = ['DevError: Const mod path "{0}" is not a directory.'
                     ''.format(mod), '\tfunction = {0}'.format(func_name)]
            ConfigError(emsgs, level='error')
        # append mods
        mods.append(mod)
    # make sure we found something
    if len(mods) == 0:
        emsgs = ['DevError: No config dirs found',
                 '\tfunction = {0}'.format(func_name)]
        ConfigError(emsgs, level='error')
    if len(mods) != len(SCRIPTS):
        emsgs = ['DevError: Const mod scrips missing found=[{0}]'
                 ''.format(','.join(mods)),
                 '\tfunction = {0}'.format(func_name)]
        ConfigError(emsgs, level='error')
    # return modules
    return mods


def _get_relative_folder(package, folder):
    """
    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the configuration folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    func_name = __NAME__ + '.get_relative_folder()'
    # get the package.__init__ file path
    try:
        init = pkg_resources.resource_filename(package, '__init__.py')
    except ImportError:
        emsg = 'Package name = "{0}" is invalid (function = {1})'
        raise ConfigError(emsg.format(package, func_name), level='error')
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
        emsg = 'Folder "{0}" does not exist in {1}'
        eargs = [os.path.basename(data_folder), os.path.dirname(data_folder)]
        raise ConfigError(emsg.format(*eargs), level='error')
    # return the absolute data_folder path
    return data_folder


def _load_from_module(modules):
    func_name = __NAME__ + '._load_from_module()'
    # storage for returned values
    keys, values, sources = [], [], []
    # loop around modules
    for module in modules:
        # get a list of keys values
        mkeys, mvalues = package.generate_all_consts(module)
        # loop around each value and test type
        for it in range(len(mkeys)):
            # get iteration values
            mvalue = mvalues[it]
            # get the parameter name
            key = mkeys[it]
            # deal with duplicate keys
            if key in keys:
                emsgs = ['Duplicate Const parameter "{0}" for instrument "{1}"'
                         ''.format(key, module),
                         '\tModule list: {0}'.format(','.join(modules)),
                         '\tfunction = {0}'.format(func_name)]
                ConfigError(emsgs, level='error')
            # valid parameter
            cond = mvalue.validate()
            # if validated append to keys/values/sources
            if cond:
                keys.append(key)
                values.append(mvalue.true_value)
                sources.append(module)
    # return keys
    return keys, values, sources


def _load_from_file(files, modules):
    keys, values, sources = [], [], []
    return keys, values, sources


# =============================================================================
# Other private functions
# =============================================================================
# capitalisation function (for case insensitive keys)
def _capitalise_key(key):
    """
    Capitalizes "key" (used to make ParamDict case insensitive), only if
    key is a string

    :param key: string or object, if string then key is capitalized else
                nothing is done

    :return key: capitalized string (or unchanged object)
    """
    # capitalise string keys
    if type(key) == str:
        key = key.upper()
    return key


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
