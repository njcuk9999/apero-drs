#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constants parameter functions

DRS Import Rules:

- only from apero.lang and apero.core.constants

Created on 2019-01-17 at 15:24

@author: cook
"""

from collections import OrderedDict
import copy
import numpy as np
import os
import pkg_resources
import shutil
import sys
from typing import Union, List, Type

from apero.core.constants import constant_functions
from apero.lang import drs_exceptions


# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'param_functions.py'
# Define package name
PACKAGE = 'apero'
# Define relative path to 'const' sub-package
CONST_PATH = './core/instruments/'
CORE_PATH = './core/instruments/default/'
# Define config/constant/keyword scripts to open
SCRIPTS = ['default_config.py', 'default_constants.py', 'default_keywords.py']
USCRIPTS = ['user_config.ini', 'user_constants.ini', 'user_keywords.ini']
PSEUDO_CONST_FILE = 'pseudo_const.py'
PSEUDO_CONST_CLASS = 'PseudoConstants'
# get the Drs Exceptions
ArgumentError = drs_exceptions.ArgumentError
ArgumentWarning = drs_exceptions.ArgumentWarning
DRSError = drs_exceptions.DrsError
DRSWarning = drs_exceptions.DrsWarning
TextError = drs_exceptions.TextError
TextWarning = drs_exceptions.TextWarning
ConfigError = drs_exceptions.ConfigError
ConfigWarning = drs_exceptions.ConfigWarning
# get the logger
BLOG = drs_exceptions.basiclogger
# relative folder cache
REL_CACHE = dict()
CONFIG_CACHE = dict()
PCONFIG_CACHE = dict()
# cache some settings
SETTINGS_CACHE_KEYS = ['DRS_DEBUG', 'ALLOW_BREAKPOINTS']
SETTINGS_CACHE = dict()


# =============================================================================
# Define Custom classes
# =============================================================================
# case insensitive dictionary
class CaseInsensitiveDict(dict):
    """
    Custom dictionary with string keys that are case insensitive
    """

    def __init__(self, *arg, **kw):
        """
        Construct the case insensitive dictionary class
        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        # set function name
        _ = display_func(None, '__init__', __NAME__, 'CaseInsensitiveDict')
        # super from dict
        super(CaseInsensitiveDict, self).__init__(*arg, **kw)
        # force keys to be capitals (internally)
        self.__capitalise_keys__()

    def __getitem__(self, key: str) -> object:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str

        :return value: object, the value stored at position "key"
        """
        # set function name
        _ = display_func(None, '__getitem__', __NAME__, 'CaseInsensitiveDict')
        # make key capitals
        key = _capitalise_key(key)
        # return from supers dictionary storage
        return super(CaseInsensitiveDict, self).__getitem__(key)

    def __setitem__(self, key: str, value: object, source: str = None):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter
        :param source: string, the source for the parameter

        :type key: str
        :type value: object
        :type source: str

        :return: None
        """
        # set function name
        _ = display_func(None, '__setitem__', __NAME__, 'CaseInsensitiveDict')
        # capitalise string keys
        key = _capitalise_key(key)
        # then do the normal dictionary setting
        super(CaseInsensitiveDict, self).__setitem__(key, value)

    def __contains__(self, key: str) -> bool:
        """
        Method to find whether CaseInsensitiveDict instance has key="key"
        used with the "in" operator
        if key exists in CaseInsensitiveDict True is returned else False
        is returned

        :param key: string, "key" to look for in CaseInsensitiveDict instance
        :type key: str

        :return bool: True if CaseInsensitiveDict instance has a key "key",
        else False
        :rtype: bool
        """
        # set function name
        _ = display_func(None, '__contains__', __NAME__, 'CaseInsensitiveDict')
        # capitalize key first
        key = _capitalise_key(key)
        # return True if key in keys else return False
        return super(CaseInsensitiveDict, self).__contains__(key)

    def __delitem__(self, key: str):
        """
        Deletes the "key" from CaseInsensitiveDict instance, case insensitive

        :param key: string, the key to delete from ParamDict instance,
                    case insensitive
        :type key: str

        :return None:
        """
        # set function name
        _ = display_func(None, '__delitem__', __NAME__, 'CaseInsensitiveDict')
        # capitalize key first
        key = _capitalise_key(key)
        # delete key from keys
        super(CaseInsensitiveDict, self).__delitem__(key)

    def get(self, key: str, default: Union[None, object] = None):
        """
        Overrides the dictionary get function
        If "key" is in CaseInsensitiveDict instance then returns this value,
        else returns "default" (if default returned source is set to None)
        key is case insensitive

        :param key: string, the key to search for in ParamDict instance
                    case insensitive
        :param default: object or None, if key not in ParamDict instance this
                        object is returned

        :type key: str
        :type default: Union[None, object]

        :return value: if key in ParamDict instance this value is returned else
                       the default value is returned (None if undefined)
        """
        # set function name
        _ = display_func(None, 'get', __NAME__, 'CaseInsensitiveDict')
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
        # set function name
        _ = display_func(None, '__capitalise_keys__', __NAME__,
                         'CaseInsensitiveDict')
        # make keys a list
        keys = list(self.keys())
        # loop around key in keys
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


class ListCaseInsensitiveDict(CaseInsensitiveDict):
    def __getitem__(self, key: str) -> list:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str

        :return value: list, the value stored at position "key"
        """
        # set function name
        _ = display_func(None, '__getitem__', __NAME__,
                         'ListCaseInsensitiveDict')
        # return from supers dictionary storage
        # noinspection PyTypeChecker
        return list(super(ListCaseInsensitiveDict, self).__getitem__(key))

    def __setitem__(self, key: str, value: list, source: str = None):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter
        :param source: string, the source for the parameter

        :type key: str
        :type value: list
        :type source: str

        :return: None
        """
        # set function name
        _ = display_func(None, '__setitem__', __NAME__,
                         'ListCaseInsensitiveDict')
        # then do the normal dictionary setting
        super(ListCaseInsensitiveDict, self).__setitem__(key, list(value))


class ParamDict(CaseInsensitiveDict):
    """
    Custom dictionary to retain source of a parameter (added via setSource,
    retreived via getSource). String keys are case insensitive.
    """
    def __init__(self, *arg, **kw):
        """
        Constructor for parameter dictionary, calls dict.__init__
        i.e. the same as running dict(*arg, *kw)

        :param arg: arguments passed to CaseInsensitiveDict
        :param kw: keyword arguments passed to CaseInsensitiveDict
        """
        # set function name
        _ = display_func(None, '__init__', __NAME__, 'ParamDict')
        # storage for the sources
        self.sources = CaseInsensitiveDict()
        # storage for the source history
        self.source_history = ListCaseInsensitiveDict()
        # storage for the instances
        self.instances = CaseInsensitiveDict()
        # the print format
        self.pfmt = '\t{0:30s}{1:45s} # {2}'
        # the print format for list items
        self.pfmt_ns = '\t{1:45s}'
        # whether the parameter dictionary is locked for editing
        self.locked = False
        # get text entry from constants (manual database)
        self.textentry = constant_functions.DisplayText()
        # run the super class (CaseInsensitiveDict <-- dict)
        super(ParamDict, self).__init__(*arg, **kw)

    def __getitem__(self, key: str) -> object:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str
        :return value: object, the value stored at position "key"
        :raises ConfigError: if key not found
        """
        # set function name
        _ = display_func(None, '__getitem__', __NAME__, 'ParamDict')
        # try to get item from super
        try:
            return super(ParamDict, self).__getitem__(key)
        except KeyError:
            # log that parameter was not found in parameter dictionary
            emsg = self.textentry('00-003-00024', args=[key])
            raise ConfigError(emsg, level='error')

    def __setitem__(self, key: str, value: object,
                    source: Union[None, str] = None,
                    instance: Union[None, object] = None):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter
        :param source: string, the source for the parameter

        :type key: str
        :type source: Union[None, str]
        :type instance: Union[None, object]

        :return: None
        :raises ConfigError: if parameter dictionary is locked
        """
        global SETTINGS_CACHE
        # set function name
        _ = display_func(None, '__setitem__', __NAME__, 'ParamDict')
        # deal with parameter dictionary being locked
        if self.locked:
            # log that parameter dictionary is locked so we cannot set key
            raise ConfigError(self.textentry('00-003-00025', args=[key, value]))
        # if we dont have the key in sources set it regardless
        if key not in self.sources:
            self.sources[key] = source
            self.instances[key] = instance
        # if we do have the key only set it if source is not None
        elif source is not None:
            self.sources[key] = source
            self.instances[key] = instance
        # if setting in cached settings add
        if key in SETTINGS_CACHE_KEYS:
            SETTINGS_CACHE[key] = copy.deepcopy(value)
        # then do the normal dictionary setting
        super(ParamDict, self).__setitem__(key, value)

    def __contains__(self, key: str) -> bool:
        """
        Method to find whether ParamDict instance has key="key"
        used with the "in" operator
        if key exists in ParamDict True is returned else False is returned

        :param key: string, "key" to look for in ParamDict instance

        :return bool: True if ParamDict instance has a key "key", else False
        """
        # set function name
        _ = display_func(None, '__contains__', __NAME__, 'ParamDict')
        # run contains command from super
        return super(ParamDict, self).__contains__(key)

    def __delitem__(self, key: str):
        """
        Deletes the "key" from ParamDict instance, case insensitive

        :param key: string, the key to delete from ParamDict instance,
                    case insensitive

        :return None:
        """
        # set function name
        _ = display_func(None, '__delitem__', __NAME__, 'ParamDict')
        # delete item using super
        super(ParamDict, self).__delitem__(key)

    def __repr__(self):
        """
        Get the offical string representation for this instance
        :return: return the string representation

        :rtype: str
        """
        # set function name
        _ = display_func(None, '__repr__', __NAME__, 'ParamDict')
        # get string from string print
        return self._string_print()

    def __str__(self) -> str:
        """
        Get the informal string representation for this instance
        :return: return the string representation

        :rtype: str
        """
        # set function name
        _ = display_func(None, '__repr__', __NAME__, 'ParamDict')
        # get string from string print
        return self._string_print()

    def set(self, key: str, value: object,
            source: Union[None, str] = None,
            instance: Union[None, object] = None):
        """
        Set an item even if params is locked

        :param key: str, the key to set
        :param value: object, the value of the key to set
        :param source: str, the source of the value/key to set
        :param instance: object, the instance of the value/key to set

        :type key: str
        :type source: str
        :type instance: object

        :return: None
        """
        # set function name
        _ = display_func(None, 'set', __NAME__, 'ParamDict')
        # if we dont have the key in sources set it regardless
        if key not in self.sources:
            self.sources[key] = source
            self.instances[key] = instance
        # if we do have the key only set it if source is not None
        elif source is not None:
            self.sources[key] = source
            self.instances[key] = instance
        # then do the normal dictionary setting
        super(ParamDict, self).__setitem__(key, value)

    def lock(self):
        """
        Locks the parameter dictionary

        :return:
        """
        # set function name
        _ = display_func(None, 'lock', __NAME__, 'ParamDict')
        # set locked to True
        self.locked = True

    def unlock(self):
        """
        Unlocks the parameter dictionary

        :return:
        """
        # set function name
        _ = display_func(None, 'unlock', __NAME__, 'ParamDict')
        # set locked to False
        self.locked = False

    def get(self, key: str, default: Union[None, object] = None) -> object:
        """
        Overrides the dictionary get function
        If "key" is in ParamDict instance then returns this value, else
        returns "default" (if default returned source is set to None)
        key is case insensitive

        :param key: string, the key to search for in ParamDict instance
                    case insensitive
        :param default: object or None, if key not in ParamDict instance this
                        object is returned

        :type key: str

        :return value: if key in ParamDict instance this value is returned else
                       the default value is returned (None if undefined)
        """
        # set function name
        _ = display_func(None, 'get', __NAME__, 'ParamDict')
        # if we have the key return the value
        if key in self.keys():
            return self.__getitem__(key)
        # else return the default key (None if not defined)
        else:
            self.sources[key] = None
            return default

    def set_source(self, key: str, source: str):
        """
        Set a key to have sources[key] = source

        raises a ConfigError if key not found

        :param key: string, the main dictionary string
        :param source: string, the source to set

        :type key: str
        :type source: str

        :return None:
        :raises ConfigError: if key not found
        """
        # set function name
        _ = display_func(None, 'set_source', __NAME__, 'ParamDict')
        # capitalise
        key = _capitalise_key(key)
        # don't put full path for sources in package
        source = _check_mod_source(source)
        # only add if key is in main dictionary
        if key in self.keys():
            self.sources[key] = source
            # add to history
            if key in self.source_history:
                self.source_history[key].append(source)
            else:
                self.source_history[key] = [source]
        else:
            # log error: source cannot be added for key
            emsg = self.textentry('00-003-00026', args=[key])
            raise ConfigError(emsg, level='error')

    def set_instance(self, key: str, instance: object):
        """
        Set a key to have instance[key] = instance

        raise a Config Error if key not found
        :param key: str, the key to add
        :param instance: object, the instance to store (normally Const/Keyword)

        :type key: str

        :return None:
        :raises ConfigError: if key not found
        """
        # set function name
        _ = display_func(None, 'set_instance', __NAME__, 'ParamDict')
        # capitalise
        key = _capitalise_key(key)
        # only add if key is in main dictionary
        if key in self.keys():
            self.instances[key] = instance
        else:
            # log error: instance cannot be added for key
            emsg = self.textentry('00-003-00027', args=[key])
            raise ConfigError(emsg, level='error')

    def append_source(self, key: str, source: str):
        """
        Adds source to the source of key (appends if exists)
        i.e. sources[key] = oldsource + source

        :param key: string, the main dictionary string
        :param source: string, the source to set

        :type key: str
        :type source: str

        :return None:
        """
        # set function name
        _ = display_func(None, 'append_source', __NAME__, 'ParamDict')
        # capitalise
        key = _capitalise_key(key)
        # if key exists append source to it
        if key in self.keys() and key in list(self.sources.keys()):
            self.sources[key] += ' {0}'.format(source)
        else:
            self.set_source(key, source)

    def set_sources(self, keys: List[str],
                    sources: Union[str, List[str], dict]):
        """
        Set a list of keys sources

        raises a ConfigError if key not found

        :param keys: list of strings, the list of keys to add sources for
        :param sources: string or list of strings or dictionary of strings,
                        the source or sources to add,
                        if a dictionary source = sources[key] for key = keys[i]
                        if list source = sources[i]  for keys[i]
                        if string all sources with these keys will = source

        :type keys: list
        :type sources: Union[str, list, dict]

        :return None:
        """
        # set function name
        _ = display_func(None, 'set_sources', __NAME__, 'ParamDict')
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

    def set_instances(self, keys: List[str],
                      instances: Union[object, list, dict]):
        """
        Set a list of keys sources

        raises a ConfigError if key not found

        :param keys: list of strings, the list of keys to add sources for
        :param instances: object or list of objects or dictionary of objects,
                        the source or sources to add,
                        if a dictionary source = sources[key] for key = keys[i]
                        if list source = sources[i]  for keys[i]
                        if object all sources with these keys will = source

        :type keys: list
        :type instances: Union[object, list, dict]

        :return None:
        """
        # set function name
        _ = display_func(None, 'set_instances', __NAME__, 'ParamDict')
        # loop around each key in keys
        for k_it in range(len(keys)):
            # assign the key from k_it
            key = keys[k_it]
            # capitalise
            key = _capitalise_key(key)
            # Get source for this iteration
            if type(instances) == list:
                instance = instances[k_it]
            elif type(instances) == dict:
                instance = instances[key]
            else:
                instance = instances
            # set source
            self.set_instance(key, instance)

    def append_sources(self, keys: str, sources: Union[str, List[str], dict]):
        """
        Adds list of keys sources (appends if exists)

        raises a ConfigError if key not found

        :param keys: list of strings, the list of keys to add sources for
        :param sources: string or list of strings or dictionary of strings,
                        the source or sources to add,
                        if a dictionary source = sources[key] for key = keys[i]
                        if list source = sources[i]  for keys[i]
                        if string all sources with these keys will = source

        :type keys: list
        :type sources: Union[str, List[str], dict]

        :return None:
        """
        # set function name
        _ = display_func(None, 'append_sources', __NAME__, 'ParamDict')
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

    def set_all_sources(self, source: str):
        """
        Set all keys in dictionary to this source

        :param source: string, all keys will be set to this source

        :type source: str

        :return None:
        """
        # set function name
        _ = display_func(None, 'set_all_sources', __NAME__, 'ParamDict')
        # loop around each key in keys
        for key in self.keys():
            # capitalise
            key = _capitalise_key(key)
            # set key
            self.sources[key] = source

    def append_all_sources(self, source: str):
        """
        Sets all sources to this "source" value

        :param source: string, the source to set

        :type source: str

        :return None:
        """
        # set function name
        _ = display_func(None, 'append_all_sources', __NAME__, 'ParamDict')
        # loop around each key in keys
        for key in self.keys():
            # capitalise
            key = _capitalise_key(key)
            # set key
            self.sources[key] += ' {0}'.format(source)

    def get_source(self, key: str) -> str:
        """
        Get a source from the parameter dictionary (must be set)

        raises a ConfigError if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        # set function name
        _ = display_func(None, 'get_source', __NAME__, 'ParamDict')
        # capitalise
        key = _capitalise_key(key)
        # if key in keys and sources then return source
        if key in self.keys() and key in self.sources.keys():
            return str(self.sources[key])
        # else raise a Config Error
        else:
            # log error: no source set for key
            emsg = self.textentry('00-003-00028', args=[key])
            raise ConfigError(emsg, level='error')

    def get_instance(self, key: str) -> object:
        """
        Get a source from the parameter dictionary (must be set)

        raises a ConfigError if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        # set function name
        _ = display_func(None, 'get_instance', __NAME__, 'ParamDict')
        # capitalise
        key = _capitalise_key(key)
        # if key in keys and sources then return source
        if key in self.keys() and key in self.instances.keys():
            return self.instances[key]
        # else raise a Config Error
        else:
            emsg = self.textentry('00-003-00029', args=[key])
            raise ConfigError(emsg, level='error')

    def source_keys(self) -> List[str]:
        """
        Get a dict_keys for the sources for this parameter dictionary
        order the same as self.keys()

        :return sources: values of sources dictionary
        """
        # set function name
        _ = display_func(None, 'source_keys', __NAME__, 'ParamDict')
        # return all keys in source dictionary
        return list(self.sources.keys())

    def source_values(self) -> List[object]:
        """
        Get a dict_values for the sources for this parameter dictionary
        order the same as self.keys()

        :return sources: values of sources dictionary
        """
        # set function name
        _ = display_func(None, 'source_values', __NAME__, 'ParamDict')
        # return all values in source dictionary
        return list(self.sources.values())

    def startswith(self, substring: str) -> List[str]:
        """
        Return all keys that start with this substring

        :param substring: string, the prefix that the keys start with

        :type substring: str

        :return keys: list of strings, the keys with this substring at the start
        """
        # set function name
        _ = display_func(None, 'startswith', __NAME__, 'ParamDict')
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

    def contains(self, substring: str) -> List[str]:
        """
        Return all keys that contain this substring

        :param substring: string, the sub-string to look for in all keys

        :type substring: str

        :return keys: list of strings, the keys which contain this substring
        """
        # set function name
        _ = display_func(None, 'contains', __NAME__, 'ParamDict')
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

    def endswith(self, substring: str) -> List[str]:
        """
        Return all keys that end with this substring

        :param substring: string, the suffix that the keys ends with

        :type substring: str

        :return keys: list of strings, the keys with this substring at the end
        """
        # set function name
        _ = display_func(None, 'endswith', __NAME__, 'ParamDict')
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
        """
        Copy a parameter dictionary (deep copy parameters)

        :return: the copy of the parameter dictionary
        :rtype: ParamDict
        """
        # set function name
        _ = display_func(None, 'copy', __NAME__, 'ParamDict')
        # make new copy of param dict
        pp = ParamDict()
        keys = list(self.keys())
        values = list(self.values())
        # loop around keys and add to new copy
        for k_it, key in enumerate(keys):
            value = values[k_it]
            # try to deep copy parameter
            if isinstance(value, ParamDict):
                pp[key] = value.copy()
            else:
                # noinspection PyBroadException
                try:
                    pp[key] = copy.deepcopy(value)
                except Exception as _:
                    pp[key] = type(value)(value)
            # copy source
            if key in self.sources:
                pp.set_source(key, str(self.sources[key]))
            else:
                pp.set_source(key, 'Unknown')
            # copy source history
            if key in self.source_history:
                pp.source_history[key] = list(self.source_history[key])
            else:
                pp.source_history[key] = []
            # copy instance
            if key in self.instances:
                pp.set_instance(key, self.instances[key])
            else:
                pp.set_instance(key, None)
        # return new param dict filled
        return pp

    def merge(self, paramdict, overwrite: bool = True):
        """
        Merge another parameter dictionary with this one

        :param paramdict: ParamDict, another parameter dictionary to merge
                          with this one
        :param overwrite: bool, if True (default) allows overwriting of
                          parameters, else skips ones already present

        :type paramdict: ParamDict
        :type overwrite: bool

        :return: None
        """
        # set function name
        _ = display_func(None, 'merge', __NAME__, 'ParamDict')
        # add param dict to self
        for key in paramdict:
            # deal with no overwriting
            if not overwrite and key in self.keys:
                continue
            # copy source
            if key in paramdict.sources:
                ksource = paramdict.sources[key]
            else:
                ksource = None
            # copy instance
            if key in paramdict.instances:
                kinst = paramdict.instances[key]
            else:
                kinst = None
            # add to self
            self.set(key, paramdict[key], ksource, kinst)

    def _string_print(self) -> str:
        """
        Constructs a string representation of the instance

        :return: a string representation of the instance
        :rtype: str
        """
        # set function name
        _ = display_func(None, '_string_print', __NAME__, 'ParamDict')
        # get keys and values
        keys = list(self.keys())
        values = list(self.values())
        # string storage
        return_string = 'ParamDict:\n'
        strvalues = []
        # loop around each key in keys
        for k_it, key in enumerate(keys):
            # get this iterations values
            value = values[k_it]
            # deal with no source
            if key not in self.sources:
                self.sources[key] = 'None'
            # print value
            if type(value) in [list, np.ndarray]:
                sargs = [key, list(value), self.sources[key], self.pfmt]
                strvalues += _string_repr_list(*sargs)
            elif type(value) in [dict, OrderedDict, ParamDict]:
                strvalue = list(value.keys()).__repr__()[:40]
                sargs = [key + '[DICT]', strvalue, self.sources[key]]
                strvalues += [self.pfmt.format(*sargs)]
            else:
                strvalue = str(value)[:40]
                sargs = [key + ':', strvalue, self.sources[key]]
                strvalues += [self.pfmt.format(*sargs)]
        # combine list into single string
        for string_value in strvalues:
            return_string += '\n {0}'.format(string_value)
        # return string
        return return_string + '\n'

    def listp(self, key: str, separator: str = ',',
              dtype: Union[None, Type] = None) -> list:
        """
        Turn a string list parameter (separated with `separator`) into a list
        of objects (of data type `dtype`)

        i.e. ParamDict['MYPARAM'] = '1, 2, 3, 4'
        x = ParamDict.listp('my_parameter', dtype=int)
        gives:

        x = list([1, 2, 3, 4])

        :param key: str, the key that contains a string list
        :param separator: str, the character that separates
        :param dtype: type, the type to cast the list element to

        :return: the list of values extracted from the string for `key`
        :rtype: list
        """
        # set function name
        _ = display_func(None, 'listp', __NAME__, 'ParamDict')
        # if key is present attempt str-->list
        if key in self.keys():
            item = self.__getitem__(key)
        else:
            # log error: parameter not found in parameter dict (via listp)
            emsg = self.textentry('00-003-00030', args=[key])
            raise ConfigError(emsg, level='error')
        # convert string
        if key in self.keys() and isinstance(item, str):
            return _map_listparameter(str(item), separator=separator,
                                      dtype=dtype)
        elif isinstance(item, list):
            return item
        else:
            # log error: parameter not found in parameter dict (via listp)
            emsg = self.textentry('00-003-00032', args=[key])
            raise ConfigError(emsg, level='error')

    def dictp(self, key: str, dtype: Union[str, None] = None) -> dict:
        """
        Turn a string dictionary parameter into a python dictionary
        of objects (of data type `dtype`)

        i.e. ParamDict['MYPARAM'] = '{"varA":1, "varB":2}'
        x = ParamDict.listp('my_parameter', dtype=int)
        gives:

        x = dict(varA=1, varB=2)

        Note string dictionary must be in the {"key":value} format

        :param key: str, the key that contains a string list
        :param dtype: type, the type to cast the list element to

        :return: the list of values extracted from the string for `key`
        :rtype: dict
        """
        # set function name
        _ = display_func(None, 'dictp', __NAME__, 'ParamDict')
        # if key is present attempt str-->dict
        if key in self.keys():
            item = self.__getitem__(key)
        else:
            # log error message: parameter not found in param dict (via dictp)
            emsg = self.textentry('00-003-00031', args=[key])
            raise ConfigError(emsg.format(key), level='error')
        # convert string
        if isinstance(item, str):
            return _map_dictparameter(str(item), dtype=dtype)
        elif isinstance(item, dict):
            return item
        else:
            # log error message: parameter not found in param dict (via dictp)
            emsg = self.textentry('00-003-00033', args=[key])
            raise ConfigError(emsg.format(key), level='error')

    def get_instanceof(self, lookup: object, nameattr: str = 'name') -> dict:
        """
        Get all instances of object instance lookup

        i.e. perform isinstance(object, lookup)

        :param lookup: object, the instance to lookup
        :param nameattr: str, the attribute in instance that we will return
                         as the key

        :return: a dictionary of keys/value pairs where each value is an
                 instance that belongs to instance of `lookup`
        :rtype: dict
        """
        # set function name
        _ = display_func(None, 'get_instanceof', __NAME__, 'ParamDict')
        # output storage
        keydict = dict()
        # loop around all keys
        for key in list(self.instances.keys()):
            # get the instance for this key
            instance = self.instances[key]
            # skip None
            if instance is None:
                continue
            # else check instance type
            if isinstance(instance, type(lookup)):
                if hasattr(instance, nameattr):
                    name = getattr(instance, nameattr)
                    keydict[name] = instance
            else:
                continue
        # return keyworddict
        return keydict

    def info(self, key: str):
        """
        Display the information related to a specific key

        :param key: str, the key to display information about

        :type key: str

        :return: None
        """
        # set function name
        _ = display_func(None, 'info', __NAME__, 'ParamDict')
        # deal with key not existing
        if key not in self.keys():
            print(self.textentry('40-000-00001', args=[key]))
            return
        # print key title
        print(self.textentry('40-000-00002', args=[key]))
        # print value stats
        value = self.__getitem__(key)
        # print the data type
        print(self.textentry('40-000-00003', args=[type(value).__name__]))
        # deal with lists and numpy array
        if isinstance(value, (list, np.ndarray)):
            sargs = [key, list(value), None, self.pfmt_ns]
            wargs = [np.nanmin(value), np.nanmax(value),
                     np.sum(np.isnan(value)) > 0, _string_repr_list(*sargs)]
            print(self.textentry('40-000-00004', args=wargs))
        # deal with dictionaries
        elif isinstance(value, (dict, OrderedDict, ParamDict)):
            strvalue = list(value.keys()).__repr__()[:40]
            sargs = [key + '[DICT]', strvalue, None]
            wargs = [len(list(value.keys())), self.pfmt_ns.format(*sargs)]
            print(self.textentry('40-000-00005', args=wargs))
        # deal with everything else
        else:
            strvalue = str(value)[:40]
            sargs = [key + ':', strvalue, None]
            wargs = [self.pfmt_ns.format(*sargs)]
            print(self.textentry('40-000-00006', args=wargs))
        # add source info
        if key in self.sources:
            print(self.textentry('40-000-00007', args=[self.sources[key]]))
        # add instances info
        if key in self.instances:
            print(self.textentry('40-000-00008', args=[self.instances[key]]))

    def history(self, key: str):
        """
        Display the history of where key was defined (using source)

        :param key: str, the key to print history of

        :type key: str

        :return: None
        """
        # set function name
        _ = display_func(None, 'history', __NAME__, 'ParamDict')
        # if history found then print it
        if key in self.source_history:
            # print title: History for key
            print(self.textentry('40-000-00009', args=[key]))
            # loop around history and print row by row
            for it, entry in enumerate(self.source_history[key]):
                print('{0}: {1}'.format(it + 1, entry))
        # else display that there was not history found
        else:
            print(self.textentry('40-000-00010', args=[key]))


# =============================================================================
# Define functions
# =============================================================================
def update_paramdicts(*args, **kwargs):
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'update_paramdicts', __NAME__)
    # get key from kwargs
    key = kwargs.get('key', None)
    # get value from kwargs
    value = kwargs.get('value', None)
    # get source from kwargs
    source = kwargs.get('source', None)
    # get instance from kwargs
    instance = kwargs.get('instance', None)
    # loop through param dicts
    for arg in args:
        if isinstance(arg, ParamDict):
            arg.set(key, value=value, source=source, instance=instance)


def load_config(instrument=None, from_file=True, cache=True):
    global CONFIG_CACHE
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'load_config', __NAME__)
    # check config cache
    if instrument in CONFIG_CACHE and cache:
        return CONFIG_CACHE[instrument].copy()
    # deal with instrument set to 'None'
    if isinstance(instrument, str):
        if instrument.upper() == 'NONE':
            instrument = None
    # get instrument sub-package constants files
    modules = get_module_names(instrument)
    # get constants from modules
    try:
        keys, values, sources, instances = _load_from_module(modules, True)
    except ConfigError:
        sys.exit(1)

    params = ParamDict(zip(keys, values))
    # Set the source
    params.set_sources(keys=keys, sources=sources)
    # add to params
    for it in range(len(keys)):
        # set instance (Const/Keyword instance)
        params.set_instance(keys[it], instances[it])
    # get constants from user config files
    if from_file:
        # get instrument user config files
        files = _get_file_names(params, instrument)
        try:
            keys, values, sources, instances = _load_from_file(files, modules)
        except ConfigError:
            sys.exit(1)
        # add to params
        for it in range(len(keys)):
            # set value
            params[keys[it]] = values[it]
            # set instance (Const/Keyword instance)
            params.set_instance(keys[it], instances[it])
        params.set_sources(keys=keys, sources=sources)
    # save sources to params
    params = _save_config_params(params)
    # cache these params
    if cache:
        CONFIG_CACHE[instrument] = params.copy()
    # return the parameter dictionary
    return params


def load_pconfig(instrument=None):
    global PCONFIG_CACHE
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(None, 'load_pconfig', __NAME__)
    # check cache
    if instrument in PCONFIG_CACHE:
        return PCONFIG_CACHE[instrument]
    # deal with instrument set to 'None'
    if isinstance(instrument, str):
        if instrument.upper() == 'NONE':
            instrument = None
    # get instrument sub-package constants files
    modules = get_module_names(instrument, mod_list=[PSEUDO_CONST_FILE])
    # import module
    mod = constant_functions.import_module(func_name, modules[0])
    # check that we have class and import it
    if hasattr(mod, PSEUDO_CONST_CLASS):
        psconst = getattr(mod, PSEUDO_CONST_CLASS)
    # else raise error
    else:
        emsg = 'Module "{0}" is required to have class "{1}"'
        ConfigError(emsg.format(modules[0], PSEUDO_CONST_CLASS))
        sys.exit(1)
    # get instance of PseudoClass
    pconfig = psconst(instrument=instrument)
    # update cache
    PCONFIG_CACHE[instrument] = pconfig
    return pconfig


def get_config_all():
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'get_config_all', __NAME__)
    # get module names
    modules = get_module_names(None)
    # loop around modules and print our __all__ statement
    for module in modules:
        # generate a list of all functions in a module
        rawlist = constant_functions.generate_consts(module)[0]
        # print to std-out
        print('=' * 50)
        print('MODULE: {0}'.format(module))
        print('=' * 50)
        print('')
        print('__all__ = [\'{0}\']'.format('\', \''.join(rawlist)))
        print('')


def get_file_names(instrument=None, file_list=None, instrument_path=None,
                   default_path=None):
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(None, 'get_file_names', __NAME__)
    # get core path
    core_path = get_relative_folder(PACKAGE, default_path)
    # get constants package path
    if instrument is not None:
        const_path = get_relative_folder(PACKAGE, instrument_path)
        # get the directories within const_path
        filelist = os.listdir(const_path)
        directories = []
        for filename in filelist:
            if os.path.isdir(filename):
                directories.append(filename)
    else:
        const_path = None
        # get the directories within const_path
        filelist = os.listdir(core_path)
        directories = []
        for filename in filelist:
            if os.path.isdir(filename):
                directories.append(filename)

    # construct module import name
    if instrument is None:
        filepath = os.path.join(core_path, '')
    else:
        filepath = os.path.join(const_path, instrument.lower())

    # get module names
    paths = []
    for filename in file_list:
        # get file path
        fpath = os.path.join(filepath, filename)
        # append if path exists
        if not os.path.exists(fpath):
            emsgs = ['DevError: Filepath "{0}" does not exist.'
                     ''.format(fpath),
                     '\tfunction = {0}'.format(func_name)]
            raise ConfigError(emsgs, level='error')
        # append mods
        paths.append(fpath)
    # make sure we found something
    if len(paths) == 0:
        emsgs = ['DevError: No files found',
                 '\tfunction = {0}'.format(func_name)]
        raise ConfigError(emsgs, level='error')
    # return modules
    return paths


def get_module_names(instrument=None, mod_list=None, instrument_path=None,
                     default_path=None, path=True):
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(None, '_get_module_names', __NAME__)
    # deal with no module list
    if mod_list is None:
        mod_list = SCRIPTS
    # deal with no path
    if instrument_path is None:
        instrument_path = CONST_PATH
    if default_path is None:
        default_path = CORE_PATH

    # get constants package path
    const_path = get_relative_folder(PACKAGE, instrument_path)
    core_path = get_relative_folder(PACKAGE, default_path)
    # get the directories within const_path
    filelist = os.listdir(const_path)
    directories = []
    for filename in filelist:
        if os.path.isdir(filename):
            directories.append(filename)
    # construct sub-module name
    relpath = instrument_path.replace('.', '').replace(os.sep, '.')
    relpath = relpath.strip('.')
    corepath = default_path.replace('.', '').replace(os.sep, '.')
    corepath = corepath.strip('.')

    # construct module import name
    if instrument is None:
        modpath = '{0}.{1}'.format(PACKAGE, corepath)
        filepath = os.path.join(core_path, '')
    else:
        modpath = '{0}.{1}.{2}'.format(PACKAGE, relpath, instrument.lower())
        filepath = os.path.join(const_path, instrument.lower())

    # get module names
    mods, paths = [], []
    for script in mod_list:
        # make sure script doesn't end with .py
        mscript = script.split('.')[0]
        # get mod path
        mod = '{0}.{1}'.format(modpath, mscript)
        # get file path
        fpath = os.path.join(filepath, script)
        # append if path exists
        found = True
        if not os.path.exists(fpath):
            if not fpath.endswith('.py'):
                fpath += '.py'
                if not os.path.exists(fpath):
                    found = False
            else:
                found = False
        # deal with no file found
        if not found:
            emsgs = ['DevError: Const mod path "{0}" does not exist.'
                     ''.format(mod),
                     '\tpath = {0}'.format(fpath),
                     '\tfunction = {0}'.format(func_name)]
            raise ConfigError(emsgs, level='error')
        # append mods
        mods.append(mod)
        paths.append(fpath)
    # make sure we found something
    if len(mods) == 0:
        emsgs = ['DevError: No config dirs found',
                 '\tfunction = {0}'.format(func_name)]
        raise ConfigError(emsgs, level='error')
    if len(mods) != len(mod_list):
        emsgs = ['DevError: Const mod scrips missing found=[{0}]'
                 ''.format(','.join(mods)),
                 '\tfunction = {0}'.format(func_name)]
        raise ConfigError(emsgs, level='error')

    # return modules
    if path:
        return paths
    else:
        return mods


def print_error(error):
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'print_error', __NAME__)
    # print the configuration file
    print('\n')
    print('=' * 70)
    print(' Configuration file {0}:'.format(error.level))
    print('=' * 70, '\n')
    # get the error string
    estring = error.message
    # if error string is not a list assume it is a string and push it into
    #   a single element list
    if type(estring) is not list:
        estring = [estring]
    # loop around error strings (now must be a list of strings)
    for emsg in estring:
        # replace new line with new line + tab
        emsg = emsg.replace('\n', '\n\t')
        # print to std-out
        print('\t' + emsg)
    # print a gap between this and next lines
    print('=' * 70, '\n')


def break_point(params=None, allow=None, level=2):
    # set function name (cannot break inside break function)
    _ = str(__NAME__) + '.break_point()'
    # if we don't have parameters load them from config file
    if params is None:
        params = load_config()
        # force to True
        params['ALLOW_BREAKPOINTS'] = True
    # if allow is not set
    if allow is None:
        allow = params['ALLOW_BREAKPOINTS']
    # if still not allowed the return
    if not allow:
        return
    # copy pdbrc
    _copy_pdb_rc(params, level=level)
    # catch bdb quit
    # noinspection PyPep8
    try:
        _execute_ipdb()
    except Exception:
        emsg = 'USER[00-000-00000]: Debugger breakpoint exit.'
        raise drs_exceptions.DebugExit(emsg)
    finally:
        # delete pdbrc
        _remove_pdb_rc(params)


# noinspection PyUnusedLocal
def catch_sigint(signal_received, frame):
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'catch_sigint', __NAME__)
    # raise Keyboard Interrupt
    raise KeyboardInterrupt('\nSIGINT or CTRL-C detected. Exiting\n')


def window_size(drows=80, dcols=80):
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'window_size', __NAME__)
    # only works on unix operating systems
    if os.name == 'posix':
        # see if we have stty commnad
        if shutil.which('stty') is None:
            return drows, dcols
        # try to open via open and split output back to rows and columns
        # noinspection PyPep8,PyBroadException
        try:
            rows, columns = os.popen('stty size', 'r').read().split()
            return int(rows), int(columns)
        # if not just pass over this
        except Exception:
            pass
    # if we are on windows we have to get window size differently
    elif os.name == 'nt':
        # taken from: https://gist.github.com/jtriley/1108174
        # noinspection PyPep8,PyBroadException
        try:
            import struct
            from ctypes import windll, create_string_buffer
            # stdin handle is -10
            # stdout handle is -11
            # stderr handle is -12
            h = windll.kernel32.GetStdHandle(-12)
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
            if res:
                out = struct.unpack("hhhhHhhhhhh", csbi.raw)
                left, top, right, bottom = out[5:9]
                sizex = right - left + 1
                sizey = bottom - top + 1
                return int(sizey), int(sizex)
        # if not just pass over this
        except Exception:
            pass
    # if we have reached this point return the default number of rows
    #   and columns
    return drows, dcols


def display_func(params=None, name=None, program=None, class_name=None,
                 wlog=None, textentry=None):
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '.display_func()'
    # deal with no wlog defined
    if wlog is None:
        wlog = drs_exceptions.wlogbasic
    # deal with not text entry defined
    if textentry is None:
        textentry = constant_functions.DisplayText()
    # start the string function
    strfunc = ''
    # deal with no file name
    if name is None:
        name = 'Unknown'
    # ----------------------------------------------------------------------
    # add the program
    if program is not None:
        strfunc = str(program)
    if class_name is not None:
        strfunc += '.{0}'.format(class_name)
    # add the name
    strfunc += '.{0}'.format(name)
    # add brackets to show function
    if not strfunc.endswith('()'):
        strfunc += '()'
    # ----------------------------------------------------------------------
    # deal with adding a break point
    if params is not None:
        if 'INPUTS' in params and 'BREAKFUNC' in params['INPUTS']:
            # get break function
            breakfunc = params['INPUTS']['BREAKFUNC']
            # only deal with break function if it is set
            if breakfunc not in [None, 'None', '']:
                # get function name (without ending)
                funcname = strfunc.replace('()', '')
                # if function name endwith break function then we break here
                if funcname.endswith(breakfunc):
                    # log we are breaking due to break function
                    wargs = [breakfunc]
                    msg = textentry('10-005-00004', args=wargs)
                    wlog(params, 'warning', msg)
                    break_point(params, allow=True, level=3)
    # ----------------------------------------------------------------------
    # deal with no params (do not log)
    if params is None:
        return strfunc
    # deal with debug level too low (just return here)
    if params['DRS_DEBUG'] < params['DEBUG_MODE_FUNC_PRINT']:
        return strfunc
    # ----------------------------------------------------------------------
    # below here just for debug mode func print
    # ----------------------------------------------------------------------
    # add the string function to param dict
    if 'DEBUG_FUNC_LIST' not in params:
        params.set('DEBUG_FUNC_LIST', value=[None], source=func_name)
    if 'DEBUG_FUNC_DICT' not in params:
        params.set('DEBUG_FUNC_DICT', value=dict(), source=func_name)
    # append to list
    params['DEBUG_FUNC_LIST'].append(strfunc)
    # update debug dictionary
    if strfunc in params['DEBUG_FUNC_DICT']:
        params['DEBUG_FUNC_DICT'][strfunc] += 1
    else:
        params['DEBUG_FUNC_DICT'][strfunc] = 1
    # get count
    count = params['DEBUG_FUNC_DICT'][strfunc]
    # find previous entry
    previous = params['DEBUG_FUNC_LIST'][-2]
    # find out whether we have the same entry
    same_entry = previous == strfunc
    # add count
    strfunc += ' (N={0})'.format(count)
    # if we don't have a list then just print
    if params['DEBUG_FUNC_LIST'][-2] is None:
        # log in func
        wlog(params, 'debug', textentry('90-000-00004', args=[strfunc]),
             wrap=False)
    elif not same_entry:
        # get previous set of counts
        previous_count = _get_prev_count(params, previous)
        # only log if count is greater than 1
        if previous_count > 1:
            # log how many of previous there were
            dargs = [previous_count]
            wlog(params, 'debug', textentry('90-000-00005', args=dargs))
        # log in func
        wlog(params, 'debug', textentry('90-000-00004', args=[strfunc]),
             wrap=False)
    # return func_name
    return strfunc


# =============================================================================
# Config loading private functions
# =============================================================================
def _get_file_names(params, instrument=None):
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(params, '_get_file_names', __NAME__)
    # deal with no instrument
    if instrument is None:
        return []
    # get user environmental path
    user_env = params['DRS_USERENV']
    # get user default path (if environmental path unset)
    user_dpath = params['DRS_USER_DEFAULT']
    # get the package name
    drs_package = params['DRS_PACKAGE']
    # change user_dpath to a absolute path
    user_dpath = get_relative_folder(drs_package, user_dpath)
    # deal with no user environment and no default path
    if user_env is None and user_dpath is None:
        return []
    # set empty directory
    directory = None
    # -------------------------------------------------------------------------
    # User environmental path
    # -------------------------------------------------------------------------
    # check environmental path exists
    if user_env in os.environ:
        # get value
        path = os.environ[user_env]
        # check that directory linked exists
        if os.path.exists(path):
            # set directory
            directory = path

    # -------------------------------------------------------------------------
    # if directory is not empty then we need to get instrument specific files
    # -------------------------------------------------------------------------
    if directory is not None:
        # look for sub-directories (and if not found directory set to None so
        #   that we check the user default path)
        source = 'environmental variables ({0})'.format(user_env)
        subdir = _get_subdir(directory, instrument, source=source)
        if subdir is None:
            directory = None

    # -------------------------------------------------------------------------
    # User default path
    # -------------------------------------------------------------------------
    # check default path exists
    if directory is None:
        # check the directory linked exists
        if os.path.exists(user_dpath):
            # set directory
            directory = user_dpath
    # if directory is still empty return empty list
    if directory is None:
        return []
    # -------------------------------------------------------------------------
    # if directory is not empty then we need to get instrument specific files
    # -------------------------------------------------------------------------
    # look for sub-directories (This time if not found we have none and should
    #    return an empty set of files
    source = 'default user config file ({0})'.format(user_dpath)
    subdir = _get_subdir(directory, instrument, source=source)
    if subdir is None:
        return []

    # -------------------------------------------------------------------------
    # look for user configurations within instrument sub-folder
    # -------------------------------------------------------------------------
    files = []
    for script in USCRIPTS:
        # construct path
        path = os.path.join(directory, subdir, script)
        # check that it exists
        if os.path.exists(path):
            files.append(path)

    # deal with no files found
    if len(files) == 0:
        wmsg1 = ('User config defined but instrument "{0}" directory '
                 'has no configurations files')
        wmsg2 = '\tValid config files: {0}'.format(','.join(USCRIPTS))
        ConfigWarning([wmsg1.format(instrument), wmsg2])

    # return files
    return files


def _get_subdir(directory, instrument, source):
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'catch_sigint', __NAME__)
    # get display text
    textentry = constant_functions.DisplayText()
    # set the sub directory to None initially
    subdir = None
    # loop around items in the directory
    for filename in os.listdir(directory):
        # check that the absolute path is a directory
        cond1 = os.path.isdir(os.path.join(directory, filename))
        # check that item (directory) is named the same as the instrument
        cond2 = filename.lower() == instrument.lower()
        # if both conditions true set the sub directory as this item
        if cond1 and cond2:
            subdir = filename
    # deal with instrument sub-folder not found
    if subdir is None:
        # raise a config warning that directory not found
        wargs = [source, instrument.lower(), directory]
        ConfigWarning(textentry('10-002-00001', args=wargs))
    # return the subdir
    return subdir


def get_relative_folder(package, folder):
    """
    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    global REL_CACHE
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(None, 'get_relative_folder', __NAME__)
    # get text entry
    textentry = constant_functions.DisplayText()
    # ----------------------------------------------------------------------
    # check relative folder cache
    if package in REL_CACHE and folder in REL_CACHE[package]:
        return REL_CACHE[package][folder]
    # ----------------------------------------------------------------------
    # get the package.__init__ file path
    try:
        init = pkg_resources.resource_filename(package, '__init__.py')
    except ImportError:
        eargs = [package, func_name]
        raise ConfigError(textentry('00-008-00001', args=eargs), level='error')
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
        # raise exception
        eargs = [os.path.basename(data_folder), os.path.dirname(data_folder)]
        raise ConfigError(textentry('00-003-00005', args=eargs), level='error')

    # ----------------------------------------------------------------------
    # update REL_CACHE
    if package not in REL_CACHE:
        REL_CACHE[package] = dict()
    # update entry
    REL_CACHE[folder] = data_folder
    # ----------------------------------------------------------------------
    # return the absolute data_folder path
    return data_folder


def _load_from_module(modules, quiet=False):
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(None, '_load_from_module', __NAME__)
    # get text entry
    textentry = constant_functions.DisplayText()
    # storage for returned values
    keys, values, sources, instances = [], [], [], []
    # loop around modules
    for module in modules:
        # get a list of keys values
        mkeys, mvalues = constant_functions.generate_consts(module)
        # loop around each value and test type
        for it in range(len(mkeys)):
            # get iteration values
            mvalue = mvalues[it]
            # get the parameter name
            key = mkeys[it]
            # deal with duplicate keys
            if key in keys:
                # raise exception
                eargs = [key, module, ','.join(modules), func_name]
                raise ConfigError(textentry('00-003-00006', args=eargs),
                                  level='error')
            # valid parameter
            cond = mvalue.validate(quiet=quiet)
            # if validated append to keys/values/sources
            if cond:
                keys.append(key)
                values.append(mvalue.true_value)
                sources.append(mvalue.source)
                instances.append(mvalue)
    # return keys
    return keys, values, sources, instances


def _load_from_file(files, modules):
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, '_load_from_file', __NAME__)
    # get text entry
    textentry = constant_functions.DisplayText()
    # -------------------------------------------------------------------------
    # load constants from file
    # -------------------------------------------------------------------------
    fkeys, fvalues, fsources = [], [], []
    for filename in files:
        # get keys/values from script
        fkey, fvalue = constant_functions.get_constants_from_file(filename)
        # add to fkeys and fvalues (loop around fkeys)
        for it in range(len(fkey)):
            # get this iterations values
            fkeyi, fvaluei = fkey[it], fvalue[it]
            # if this is not a new constant print warning
            if fkeyi in fkeys:
                # log warning message
                wargs = [fkeyi, filename, ','.join(set(fsources)), filename]
                ConfigWarning(textentry('10-002-00002', args=wargs),
                              level='warning')
            # append to list
            fkeys.append(fkeyi)
            fvalues.append(fvaluei)
            fsources.append(filename)
    # -------------------------------------------------------------------------
    # Now need to test the values are correct
    # -------------------------------------------------------------------------
    # storage for returned values
    keys, values, sources, instances = [], [], [], []
    # loop around modules
    for module in modules:
        # get a list of keys values
        mkeys, mvalues = constant_functions.generate_consts(module)
        # loop around each value and test type
        for it in range(len(mkeys)):
            # get iteration values
            mvalue = mvalues[it]
            # loop around the file values
            for jt in range(len(fkeys)):
                # if we are not dealing with the same key skip
                if fkeys[jt] != mkeys[it]:
                    continue
                # if we are then we need to validate
                value = mvalue.validate(fvalues[jt], source=fsources[jt])
                # now append to output lists
                keys.append(fkeys[jt])
                values.append(value)
                sources.append(fsources[jt])
                instances.append(mvalue)
    # return keys values and sources
    return keys, values, sources, instances


def _save_config_params(params):
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(params, '_save_config_params', __NAME__)
    # get sources from paramater dictionary
    sources = params.sources.values()
    # get unique sources
    usources = set(sources)
    # set up storage
    params['DRS_CONFIG'] = []
    params.set_source('DRS_CONFIG', func_name)
    # loop around and add to param
    for source in usources:
        params['DRS_CONFIG'].append(source)
    # return the parameters
    return params


def _check_mod_source(source: str) -> str:
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, '_check_mod_source', __NAME__)
    # deal with source is None
    if source is None:
        return source
    # if source doesn't exist also skip
    if not os.path.exists(source):
        return source
    # get package path
    package_path = get_relative_folder(PACKAGE, '')
    # if package path not in source then skip
    if package_path not in source:
        return source
    # remove package path and replace with PACKAGE
    source = source.replace(package_path, PACKAGE.lower())
    # replace separators with .
    source = source.replace(os.sep, '.')
    # remove double dots
    while '..' in source:
        source = source.replace('..', '.')
    # return edited source
    return source


def _execute_ipdb():
    # set function name (cannot break here --> within break function)
    _ = str(__NAME__) + '._execute_ipdb()'
    # start ipdb
    # noinspection PyBroadException
    try:
        # import ipython debugger
        # noinspection PyUnresolvedReferences
        import ipdb
        # set the ipython trace
        ipdb.set_trace()
    except Exception as _:
        # import python debugger (standard python module)
        import pdb
        # set the python trace
        pdb.set_trace()


# =============================================================================
# Other private functions
# =============================================================================
# capitalisation function (for case insensitive keys)
def _capitalise_key(key: str) -> str:
    """
    Capitalizes "key" (used to make ParamDict case insensitive), only if
    key is a string

    :param key: string or object, if string then key is capitalized else
                nothing is done

    :return key: capitalized string (or unchanged object)
    """
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, '_capitalise_key', __NAME__)
    # capitalise string keys
    if type(key) == str:
        key = key.upper()
    return key


def _string_repr_list(key: str, values: Union[list, np.ndarray], source: str,
                      fmt: str) -> List[str]:
    """
    Represent a list (or array) as a string list but only the first
    40 charactersay

    :param key: str, the key the list (values) came from
    :param values: vector, the list or numpy array to print as a string
    :param source: str, the source where the values were defined
    :param fmt: str, the format for the printed list
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, '_load_from_file', __NAME__)
    # get the list as a string
    str_value = list(values).__repr__()
    # if the string is longer than 40 characters cut down and add ...
    if len(str_value) > 40:
        str_value = str_value[:40] + '...'
    # return the string as a list entry
    return [fmt.format(key, str_value, source)]


def _map_listparameter(value, separator=',', dtype=None):
    """
    Map a string list into a python list

    :param value: str or list, if list returns if string tries to evaluate
    :param separator: str, where to split the str at to make a list
    :param dtype: type, if set forces elements of list to this data type
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(None, '_map_listparameter', __NAME__)
    # get text entry
    textentry = constant_functions.DisplayText()
    # return list if already a list
    if isinstance(value, (list, np.ndarray)):
        return list(value)
    # try evaluating is a list
    # noinspection PyBroadException
    try:
        # evulate value
        rawvalue = eval(value)
        # if it is a list return as a list
        if isinstance(rawvalue, list):
            return list(rawvalue)
    # if it is not pass
    except Exception as _:
        pass
    # deal with an empty value i.e. ''
    if value == '':
        return []
    # try to return dtyped data
    try:
        # first split by separator
        listparameter = value.split(separator)

        # return the stripped down values
        if dtype is not None and isinstance(dtype, type):
            return list(map(lambda x: dtype(x.strip()), listparameter))
        else:
            return list(map(lambda x: x.strip(), listparameter))
    except Exception as e:
        eargs = [value, type(e), e, func_name]
        BLOG(message=textentry('00-003-00002', args=eargs), level='error')


def _map_dictparameter(value: str, dtype: Union[None, Type] = None) -> dict:
    """
    Map a string dictionary into a python dictionary

    :param value: str, tries to evaluate string into a dictionary
                  i.e. "dict(a=1, b=2)"  or {'a':1, 'b': 2}

    :param dtype: type, if set forces elements of list to this data type
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func(None, '_map_dictparameter', __NAME__)
    # get text entry
    textentry = constant_functions.DisplayText()
    # deal with an empty value i.e. ''
    if value == '':
        return dict()
    # try evaulating as a dict
    try:
        rawvalue = eval(value)
        if isinstance(rawvalue, dict):
            returndict = dict()
            for key in rawvalue.keys():
                if dtype is not None and isinstance(dtype, type):
                    returndict[key] = dtype(rawvalue[key])
                else:
                    returndict[key] = rawvalue[key]
            return returndict
    except Exception as e:
        eargs = [value, type(e), e, func_name]
        BLOG(message=textentry('00-003-00003', args=eargs), level='error')


def _copy_pdb_rc(params, level=0):
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '_copy_pdb_rc()'
    # set global CURRENT_PATH
    global CURRENT_PATH
    # get package
    package = params['DRS_PACKAGE']
    # get path
    path = params['DRS_PDB_RC_FILE']
    # get file name
    filename = os.path.basename(path)
    # get current path
    CURRENT_PATH = os.getcwd()
    # get absolute path
    oldsrc = get_relative_folder(package, path)
    tmppath = oldsrc + '_tmp'
    # get newsrc
    newsrc = os.path.join(CURRENT_PATH, filename)
    # read the lines
    with open(oldsrc, 'r') as f:
        lines = f.readlines()
    # deal with levels
    if level == 0:
        upkey = ''
    else:
        upkey = 'up\n' * level
    # loop around lines and replace
    newlines = []
    for line in lines:
        newlines.append(line.format(up=upkey))
    # write the lines
    with open(tmppath, 'w') as f:
        f.writelines(newlines)
    # copy
    shutil.copy(tmppath, newsrc)
    # remove tmp file
    os.remove(tmppath)


def _remove_pdb_rc(params):
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '_remove_pdb_rc()'
    # get path
    path = params['DRS_PDB_RC_FILE']
    # get file name
    filename = os.path.basename(path)
    # get newsrc
    newsrc = os.path.join(CURRENT_PATH, filename)
    # remove
    if os.path.exists(newsrc):
        os.remove(newsrc)


def _get_prev_count(params, previous):
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '._get_prev_count()'
    # get the debug list
    debug_list = params['DEBUG_FUNC_LIST'][:-1]
    # get the number of iterations
    n_elements = 0
    # loop around until we get to
    for row in range(len(debug_list))[::-1]:
        if debug_list[row] != previous:
            break
        else:
            n_elements += 1
    # return number of element founds
    return n_elements


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
