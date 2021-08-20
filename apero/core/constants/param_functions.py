#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constants parameter functions

DRS Import Rules:

- only from apero.lang and apero.core.constants

Created on 2019-01-17 at 15:24

@author: cook
"""
from astropy.io import fits
from astropy.table import Table
from collections import OrderedDict
import copy
import numpy as np
import os
import shutil
from typing import Any, List, Tuple, Type, Union
from pathlib import Path

from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_exceptions
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero import lang
from apero.core.constants import constant_functions
from apero.core.instruments.default import pseudo_const

# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'param_functions.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get the Drs Exceptions
DrsCodedException = drs_exceptions.DrsCodedException
DrsCodedWarning = drs_exceptions.DrsCodedWarning
# relative folder cache
REL_CACHE = dict()
CONFIG_CACHE = dict()
PCONFIG_CACHE = dict()
# cache some settings
SETTINGS_CACHE_KEYS = ['DRS_DEBUG', 'ALLOW_BREAKPOINTS']
SETTINGS_CACHE = dict()
# get parameters from base
CONST_PATH = base.CONST_PATH
CORE_PATH = base.CORE_PATH
# Define config/constant/keyword scripts to open
SCRIPTS = base.SCRIPTS
USCRIPTS = base.USCRIPTS
PSEUDO_CONST_FILE = base.PSEUDO_CONST_FILE
PSEUDO_CONST_CLASS = base.PSEUDO_CONST_CLASS
# Get base classes
CaseInDict = base_class.CaseInsensitiveDict
# Get the text types
textentry = lang.textentry
# get display func
display_func = drs_misc.display_func

# =============================================================================
# Define complex type returns
# =============================================================================
Const, Keyword = constant_functions.Const, constant_functions.Keyword

Exceptions = Union[DrsCodedException]

ModLoads = Tuple[List[str], List[Any], List[str], List[Union[Const, Keyword]]]


# =============================================================================
# Define Custom classes
# =============================================================================
class ParamDict(CaseInDict):
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
        # set class name
        self.class_name = 'ParamDict'
        # set function name
        _ = display_func('__init__', __NAME__, self.class_name)
        # storage for the sources
        self.sources = CaseInDict()
        # storage for the source history
        self.source_history = base_class.ListCaseINSDict()
        # storage for the Const/Keyword instances
        self.instances = constant_functions.CKCaseINSDict()
        # storage for used constants (get or set)
        self.used = CaseInDict()
        # the print format
        self.pfmt = '\t{0:30s}{1:45s} # {2}'
        # the print format for list items
        self.pfmt_ns = '\t{1:45s}'
        # whether the parameter dictionary is locked for editing
        self.locked = False
        # run the super class (CaseInsensitiveDict <-- dict)
        super(ParamDict, self).__init__(*arg, **kw)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state (for pickle)
        return state

    def __setstate__(self, state):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __getitem__(self, key: str) -> Any:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str
        :return value: object, the value stored at position "key"
        :raises DrsCodedException: if key not found
        """
        # set function name
        func_name = display_func('__getitem__', __NAME__, self.class_name)
        # store:
        if key in self.data.keys():
            if key not in self.used:
                self.used[key] = 0
            else:
                self.used[key] += 1
        # try to get item from super
        try:
            return super(ParamDict, self).__getitem__(key)
        except KeyError:
            # log that parameter was not found in parameter dictionary
            raise DrsCodedException('00-003-00024', targs=[key], level='error',
                                    func_name=func_name)

    def __setitem__(self, key: str, value: object,
                    source: Union[None, str] = None,
                    instance: Union[None, Const, Keyword] = None):
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
        :raises DrsCodedException: if parameter dictionary is locked
        """
        global SETTINGS_CACHE
        # set function name
        func_name = display_func('__setitem__', __NAME__, self.class_name)
        # deal with parameter dictionary being locked
        if self.locked:
            # log that parameter dictionary is locked so we cannot set key
            raise DrsCodedException('00-003-00025', targs=[key, value],
                                    level='error', func_name=func_name)
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
        _ = display_func('__contains__', __NAME__, self.class_name)
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
        _ = display_func('__delitem__', __NAME__, self.class_name)
        # delete item using super
        super(ParamDict, self).__delitem__(key)

    def __repr__(self) -> str:
        """
        Get the offical string representation for this instance
        :return: return the string representation

        :rtype: str
        """
        # set function name
        _ = display_func('__repr__', __NAME__, self.class_name)
        # get string from string print
        return self._string_print()

    def __str__(self) -> str:
        """
        Get the informal string representation for this instance
        :return: return the string representation

        :rtype: str
        """
        # set function name
        _ = display_func('__repr__', __NAME__, self.class_name)
        # get string from string print
        return self._string_print()

    def set(self, key: str, value: Any,
            source: Union[None, str] = None,
            instance: Union[None, Const, Keyword] = None,
            record_use: bool = True):
        """
        Set an item even if params is locked

        :param key: str, the key to set
        :param value: object, the value of the key to set
        :param source: str, the source of the value/key to set
        :param instance: object, the instance of the value/key to set
        :param record_use: bool, if True record use (in self.used)

        :type key: str
        :type source: str
        :type instance: object

        :return: None
        """
        # set function name
        _ = display_func('set', __NAME__, self.class_name)
        # update used
        if key in self.data.keys() and record_use:
            if key not in self.used:
                self.used[key] = 0
            else:
                self.used[key] += 1
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
        _ = display_func('lock', __NAME__, self.class_name)
        # set locked to True
        self.locked = True

    def unlock(self):
        """
        Unlocks the parameter dictionary

        :return:
        """
        # set function name
        _ = display_func('unlock', __NAME__, self.class_name)
        # set locked to False
        self.locked = False

    def get(self, key: str, default: Union[None, Any] = None) -> Any:
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
        _ = display_func('get', __NAME__, self.class_name)
        # if we have the key return the value
        if key in self.data.keys():
            return self.__getitem__(key)
        # else return the default key (None if not defined)
        else:
            self.sources[key] = None
            return default

    def set_source(self, key: str, source: str):
        """
        Set a key to have sources[key] = source

        raises a DrsCodedException if key not found

        :param key: string, the main dictionary string
        :param source: string, the source to set

        :type key: str
        :type source: str

        :return None:
        :raises DrsCodedException: if key not found
        """
        # set function name
        func_name = display_func('set_source', __NAME__, self.class_name)
        # capitalise
        key = drs_text.capitalise_key(key)
        # don't put full path for sources in package
        source = _check_mod_source(source)
        # only add if key is in main dictionary
        if key in self.data.keys():
            self.sources[key] = source
            # add to history
            if key in self.source_history:
                self.source_history[key].append(source)
            else:
                self.source_history[key] = [source]
        else:
            # log error: source cannot be added for key
            raise DrsCodedException('00-003-00026', targs=[key], level='error',
                                    func_name=func_name)

    def set_instance(self, key: str, instance: Union[None, Const, Keyword]):
        """
        Set a key to have instance[key] = instance

        raise a Config Error if key not found
        :param key: str, the key to add
        :param instance: Any object, the instance to store
                         (normally Const/Keyword)
                         Note objects must be pickle-able

        :type key: str

        :return None:
        :raises DrsCodedException: if key not found
        """
        # set function name
        func_name = display_func('set_instance', __NAME__,
                                 self.class_name)
        # capitalise
        key = drs_text.capitalise_key(key)
        # only add if key is in main dictionary
        if key in self.data.keys():
            self.instances[key] = instance
        else:
            # log error: instance cannot be added for key
            raise DrsCodedException('00-003-00027', targs=[key], level='error',
                                    func_name=func_name)

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
        _ = display_func('append_source', __NAME__, self.class_name)
        # capitalise
        key = drs_text.capitalise_key(key)
        # if key exists append source to it
        if key in self.data.keys() and key in list(self.sources.keys()):
            self.sources[key] += ' {0}'.format(source)
        else:
            self.set_source(key, source)

    def set_sources(self, keys: List[str],
                    sources: Union[str, List[str], dict]):
        """
        Set a list of keys sources

        raises a DrsCodedException if key not found

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
        _ = display_func('set_sources', __NAME__, self.class_name)
        # loop around each key in keys
        for k_it in range(len(keys)):
            # assign the key from k_it
            key = keys[k_it]
            # capitalise
            key = drs_text.capitalise_key(key)
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

        raises a DrsCodedException if key not found

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
        _ = display_func('set_instances', __NAME__, self.class_name)
        # loop around each key in keys
        for k_it in range(len(keys)):
            # assign the key from k_it
            key = keys[k_it]
            # capitalise
            key = drs_text.capitalise_key(key)
            # Get source for this iteration
            if type(instances) == list:
                instance = instances[k_it]
            elif type(instances) == dict:
                instance = instances[key]
            else:
                instance = instances
            # set source
            self.set_instance(key, instance)

    def append_sources(self, keys: List[str],
                       sources: Union[str, List[str], dict]):
        """
        Adds list of keys sources (appends if exists)

        raises a DrsCodedException if key not found

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
        _ = display_func('append_sources', __NAME__, self.class_name)
        # loop around each key in keys
        for k_it in range(len(keys)):
            # assign the key from k_it
            key = keys[k_it]
            # capitalise
            key = drs_text.capitalise_key(key)
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
        _ = display_func('set_all_sources', __NAME__, self.class_name)
        # loop around each key in keys
        for key in self.data.keys():
            # capitalise
            key = drs_text.capitalise_key(key)
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
        _ = display_func('append_all_sources', __NAME__, self.class_name)
        # loop around each key in keys
        for key in self.data.keys():
            # capitalise
            key = drs_text.capitalise_key(key)
            # set key
            self.sources[key] += ' {0}'.format(source)

    def get_source(self, key: str) -> str:
        """
        Get a source from the parameter dictionary (must be set)

        raises a DrsCodedException if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        # set function name
        func_name = display_func('get_source', __NAME__, self.class_name)
        # capitalise
        key = drs_text.capitalise_key(key)
        # if key in keys and sources then return source
        if key in self.data.keys() and key in self.sources.keys():
            return str(self.sources[key])
        # else raise a Config Error
        else:
            # log error: no source set for key
            raise DrsCodedException('00-003-00028', targs=[key], level='error',
                                    func_name=func_name)

    def get_instance(self, key: str) -> Union[None, Const, Keyword]:
        """
        Get a source from the parameter dictionary (must be set)

        raises a DrsCodedException if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        # set function name
        func_name = display_func('get_instance', __NAME__,
                                 self.class_name)
        # capitalise
        key = drs_text.capitalise_key(key)
        # if key in keys and sources then return source
        if key in self.data.keys() and key in self.instances.keys():
            return self.instances[key]
        # else raise a Config Error
        else:
            raise DrsCodedException('00-003-00029', targs=[key], level='error',
                                    func_name=func_name)

    def source_keys(self) -> List[str]:
        """
        Get a dict_keys for the sources for this parameter dictionary
        order the same as self.keys()

        :return sources: values of sources dictionary
        """
        # set function name
        _ = display_func('source_keys', __NAME__, self.class_name)
        # return all keys in source dictionary
        return list(self.sources.keys())

    def source_values(self) -> List[object]:
        """
        Get a dict_values for the sources for this parameter dictionary
        order the same as self.keys()

        :return sources: values of sources dictionary
        """
        # set function name
        _ = display_func('source_values', __NAME__, self.class_name)
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
        _ = display_func('startswith', __NAME__, self.class_name)
        # define return list
        return_keys = []
        # loop around keys
        for key in self.data.keys():
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
        _ = display_func('contains', __NAME__, self.class_name)
        # define return list
        return_keys = []
        # loop around keys
        for key in self.data.keys():
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
        _ = display_func('endswith', __NAME__, self.class_name)
        # define return list
        return_keys = []
        # loop around keys
        for key in self.data.keys():
            # make sure key is string
            if type(key) != str:
                continue
            # if first
            if str(key).endswith(substring.upper()):
                return_keys.append(key)
        # return keys
        return return_keys

    def copy(self) -> 'ParamDict':
        """
        Copy a parameter dictionary (deep copy parameters)

        :return: the copy of the parameter dictionary
        :rtype: ParamDict
        """
        # set function name
        _ = display_func('copy', __NAME__, self.class_name)
        # make new copy of param dict
        pp = ParamDict()
        keys = list(self.data.keys())
        values = list(self.data.values())
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
            # copy used
            if key in self.used:
                pp.used[key] = self.used[key]
        # return new param dict filled
        return pp

    def merge(self, paramdict: 'ParamDict', overwrite: bool = True):
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
        _ = display_func('merge', __NAME__, self.class_name)
        # add param dict to self
        for key in paramdict:
            # deal with no overwriting
            if not overwrite and key in self.data.keys:
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
            # add to self (but don't record this as a use)
            self.set(key, paramdict[key], ksource, kinst,
                     record_use=False)

    def _string_print(self) -> str:
        """
        Constructs a string representation of the instance

        :return: a string representation of the instance
        :rtype: str
        """
        # set function name
        _ = display_func('_string_print', __NAME__, self.class_name)
        # get keys and values
        keys = list(self.data.keys())
        values = list(self.data.values())
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
              dtype: Union[None, Type, str] = None,
              required: bool = True) -> Union[list, None]:
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

        :raises DrsCodedException: when item is not correct type
        """
        # set function name
        func_name = display_func('listp', __NAME__, self.class_name)
        # if key is present attempt str-->list
        if key in self.data.keys():
            item = self.__getitem__(key)
        elif not required:
            return None
        else:
            # log error: parameter not found in parameter dict (via listp)
            raise DrsCodedException('00-003-00030', targs=[key], level='error',
                                    func_name=func_name)
        if item is None:
            return []
        # convert string
        if key in self.data.keys() and isinstance(item, str):
            return _map_listparameter(str(item), separator=separator,
                                      dtype=dtype)
        elif isinstance(item, list):
            return item
        elif not required:
            return None
        else:
            # log error: parameter not found in parameter dict (via listp)
            raise DrsCodedException('00-003-00032', targs=[key], level='error',
                                    func_name=func_name)

    def dictp(self, key: str, dtype: Union[str, Type, None] = None,
              required: bool = True) -> Union[dict, None]:
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

        :raises DrsCodedException: when key is missing or item is incorrect
        """
        # set function name
        func_name = display_func('dictp', __NAME__, self.class_name)
        # if key is present attempt str-->dict
        if key in self.data.keys():
            item = self.__getitem__(key)
        elif not required:
            return None
        else:
            # log error message: parameter not found in param dict (via dictp)
            raise DrsCodedException('00-003-00031', targs=[key], level='error',
                                    func_name=func_name)
        if item is None:
            return dict()
        # convert string
        if isinstance(item, str):
            return _map_dictparameter(str(item), dtype=dtype)
        elif isinstance(item, dict):
            return item
        elif not required:
            return None
        else:
            # log error message: parameter not found in param dict (via dictp)
            raise DrsCodedException('00-003-00033', targs=[key], level='error',
                                    func_name=func_name)

    def get_instanceof(self, lookup: Union[Const, Keyword, Type],
                       nameattr: str = 'name') -> dict:
        """
        Get all instances of object instance lookup

        i.e. perform isinstance(object, lookup)

        :param lookup: Const or Keyword instance, the instance to lookup
        :param nameattr: str, the attribute in instance that we will return
                         as the key

        :return: a dictionary of keys/value pairs where each value is an
                 instance that belongs to instance of `lookup`
        :rtype: dict
        """
        # set function name
        _ = display_func('get_instanceof', __NAME__, self.class_name)
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
        _ = display_func('info', __NAME__, self.class_name)
        # deal with key not existing
        if key not in self.data.keys():
            print(textentry('40-000-00001', args=[key]))
            return
        # print key title
        print(textentry('40-000-00002', args=[key]))
        # print value stats
        value = self.__getitem__(key)
        # print the data type
        print(textentry('40-000-00003', args=[type(value).__name__]))
        # deal with lists and numpy array
        if isinstance(value, (list, np.ndarray)):
            sargs = [key, list(value), None, self.pfmt_ns]
            wargs = [np.nanmin(value), np.nanmax(value),
                     np.sum(np.isnan(value)) > 0, _string_repr_list(*sargs)]
            print(textentry('40-000-00004', args=wargs))
        # deal with dictionaries
        elif isinstance(value, (dict, OrderedDict, ParamDict)):
            strvalue = list(value.keys()).__repr__()[:40]
            sargs = [key + '[DICT]', strvalue, None]
            wargs = [len(list(value.keys())), self.pfmt_ns.format(*sargs)]
            print(textentry('40-000-00005', args=wargs))
        # deal with everything else
        else:
            strvalue = str(value)[:40]
            sargs = [key + ':', strvalue, None]
            wargs = [self.pfmt_ns.format(*sargs)]
            print(textentry('40-000-00006', args=wargs))
        # add source info
        if key in self.sources:
            print(textentry('40-000-00007', args=[self.sources[key]]))
        # add instances info
        if key in self.instances:
            print(textentry('40-000-00008', args=[self.instances[key]]))

    def history(self, key: str):
        """
        Display the history of where key was defined (using source)

        :param key: str, the key to print history of

        :type key: str

        :return: None
        """
        # set function name
        _ = display_func('history', __NAME__, self.class_name)
        # if history found then print it
        if key in self.source_history:
            # print title: History for key
            print(textentry('40-000-00009', args=[key]))
            # loop around history and print row by row
            for it, entry in enumerate(self.source_history[key]):
                print('{0}: {1}'.format(it + 1, entry))
        # else display that there was not history found
        else:
            print(textentry('40-000-00010', args=[key]))

    def keys(self):
        return list(self.data.keys())

    def values(self):
        return list(self.data.values())

    def snapshot_table(self, recipe: Union[Any, None] = None,
                       names: Union[list, None] = None,
                       kinds: Union[list, None] = None,
                       values: Union[list, None] = None,
                       sources: Union[list, None] = None,
                       descs: Union[list, None] = None,
                       drsfitsfile: Any = None) -> Table:
        """
        Takes a snapshot of the current configuration (for reproducibility)

        :param recipe: DrsRecipe class, the recipe instance that called this
                       function
        :param names: list of strings, the name of each constant (can be
                      none to not add extra keys)
        :param kinds: list of kinds, the kind of each constant (can be
                      none to not add extra keys) must be same length as names
        :param values: list of values, the value of each constant (can be
                       none to not add extra keys) must be same length as names
        :param sources: list of source, the source of each constant (can be
                       none to not add extra keys) must be same length as names
        :param descs: list of desc, the description of each constant (can be
                     none to not add extra keys) must be same length as names
        :param drsfitsfile: if set is the drsfile that we assume will add to
                            names/kinds/values/sources/descs (header keys
                            added to constants)

        :return:
        """
        # set function name
        func_name = display_func('snapshot_table', __NAME__)
        # tabledict
        tabledict = dict()
        # ---------------------------------------------------------------------
        # make sure names/kinds/values/sources/descs conform to each other
        # if names is None we assume kinds/values/sources/descs is None
        if names is None:
            kinds, values, sources, descs = None, None, None, None
        # if names is set kinds/values/sources/desc must be a list and must be
        #    the same length as names
        else:
            length = len(names)
            inputs = [kinds, values, sources, descs]
            inames = ['kinds', 'values', 'sources', 'descs']
            # loop around inputs to check
            for it in range(len(inputs)):
                # deal with input not being a list
                if not isinstance(kinds, list):
                    eargs = [inames[it], func_name]
                    DrsCodedException('00-001-00056', 'error', targs=eargs,
                                      func_name=func_name)
                # deal with length of input
                if len(inputs[it]) != length:
                    eargs = [inames[it], len(inputs[it]), length, func_name]
                    DrsCodedException('00-001-00055', 'error', targs=eargs,
                                      func_name=func_name)
        # ---------------------------------------------------------------------
        # extract out hdict values
        names, kinds, values, sources, descs = _add_hdict(drsfitsfile, names,
                                                          kinds, values,
                                                          sources, descs)
        # ---------------------------------------------------------------------
        # set columns for table
        columns = ['NAME', 'KIND', 'VALUE', 'SOURCE', 'DESCRIPTION', 'COUNT']
        # ---------------------------------------------------------------------
        # make columns empty lists
        for key in columns:
            tabledict[key] = []
        # ---------------------------------------------------------------------
        # add install params
        # ---------------------------------------------------------------------
        # get yaml keys and values
        ikeys, ivalues = _yaml_walk(base.IPARAMS)
        # loop around input parameters
        for it, ikey in enumerate(ikeys):
            # add install key name
            tabledict['NAME'].append(ikey)
            # add install kind
            tabledict['KIND'].append('install')
            # add install value
            tabledict['VALUE'].append(str(ivalues[it]))
            # add install source (the install yaml)
            tabledict['SOURCE'].append(os.path.join(base.IPARAMS['DRS_UCONFIG'],
                                                    base.INSTALL_YAML))
            # add install description (default)
            tabledict['DESCRIPTION'].append('Install parameter')
            # add install key count (always 1)
            tabledict['COUNT'].append(1)
        # ---------------------------------------------------------------------
        # add database parameters
        # ---------------------------------------------------------------------
        # get yaml keys and values
        dkeys, dvalues = _yaml_walk(base.DPARAMS)
        # loop around database parameters
        for it, dkey in enumerate(dkeys):
            # skip password keys
            if 'pass' in dkey.lower():
                continue
            # add database key name
            tabledict['NAME'].append(dkey)
            # add database key kind
            tabledict['KIND'].append('database')
            # add database key value
            tabledict['VALUE'].append(str(dvalues[it]))
            # add database key source (database yaml file)
            tabledict['SOURCE'].append(os.path.join(base.IPARAMS['DRS_UCONFIG'],
                                                    base.DATABASE_YAML))
            # add database description (default)
            tabledict['DESCRIPTION'].append('Database parameter')
            # add database count (always 1)
            tabledict['COUNT'].append(1)
        # ---------------------------------------------------------------------
        # get recipe parameters (from recipe)
        # ---------------------------------------------------------------------
        if recipe is not None:
            # add recipe parameters
            tabledict = _add_recipe_params_to_table_dict(tabledict, recipe)

        # ---------------------------------------------------------------------
        # get parameters from param dict
        # ---------------------------------------------------------------------
        # loop around parameter keys
        for key in self.data.keys():
            # do not continue if we have not used this key (not in dict)
            if key not in self.used:
                continue
            # do not continue if we have not used this key (set to zero)
            if int(self.used[key]) < 1:
                continue
            # add param_dict entry (or entries)
            tabledict = _add_param_dict_to_tabledict(tabledict, self.data,
                                                     key, self.instances,
                                                     self.sources, self.used,
                                                     None)
        # ---------------------------------------------------------------------
        # deal with
        # ---------------------------------------------------------------------
        # loop around arguments
        if names is not None:
            for it, name in enumerate(names):
                tabledict['NAME'].append(name)
                # add kind
                if kinds[it] is not None:
                    tabledict['KIND'].append(kinds[it])
                else:
                    tabledict['KIND'].append('custom')
                # add value
                if values[it] is not None:
                    tabledict['VALUE'].append(str(values[it]))
                else:
                    tabledict['VALUE'].append('None')
                # add source
                if sources[it] is not None:
                    tabledict['SOURCE'].append(sources[it])
                else:
                    tabledict['SOURCE'].append('None')
                # add description
                if descs[it] is not None:
                    tabledict['DESCRIPTION'].append(descs[it])
                else:
                    tabledict['DESCRIPTION'].append('custom')
                # add count
                tabledict['COUNT'].append(1)
        # ---------------------------------------------------------------------
        # convert dictionary to table
        table = Table()
        for col in columns:
            table[col] = np.array(tabledict[col], dtype=str)
        # return table
        return table


class PCheck:
    def __init__(self, wlog: Any = None):
        """
        Constructor for checking a parameter dictionary

        :param wlog: Either None or the wlog (for printing) if wlog is not
                     defined may have to catch a DrsCodedException
                     (can put in here or in the call)
        """
        # set class name
        self.class_name = 'PCheck'
        # set function name
        _ = display_func('__init__', __NAME__, self.class_name)
        # set wlog from inputs
        self.wlog = wlog

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state (for pickle)
        return state

    def __setstate__(self, state):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __str__(self):
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        # set function name
        _ = display_func('__str__', __NAME__, self.class_name)
        # return string representation
        return '{0}[CaseInsensitiveDict]'.format(self.class_name)

    def __repr__(self) -> str:
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        # set function name
        _ = display_func('__repr__', __NAME__, self.class_name)
        # return string representation
        return self.__str__()

    def __call__(self, params: Union[ParamDict, None] = None,
                 key: Union[str, None] = None,
                 name: Union[str, None] = None,
                 kwargs: Union[dict, None] = None,
                 func: Union[str, None] = None,
                 mapf: Union[str, None] = None,
                 dtype: Union[Type, None] = None,
                 paramdict: Union[ParamDict, None] = None,
                 required: bool = True,
                 default: Any = None, wlog: Union[Any, None] = None,
                 override: Any = None) -> Any:
        """
         Find a parameter "key" first in params or paramdict (if defined)
         or in kwargs (with "name") - note if "name" in kwargs overrides
         params/paramdict

         :param params: ParamDict, the constants Parameter dictionary
         :param key: string, the key to search for in "params"
                     (or paramdict if defined)
         :param name: string, the name in kwargs of the constant - overrides use
                      of param
         :param kwargs: dict, the keyword arg dictionary (or any dictionary
                        containing "key"
         :param func: string, the function name "find_param" was used
                      in (for logging)
         :param mapf: string, 'list' or 'dict' - the way to map a string parameter
                      i.e. 'a,b,c' mapf='list' -->  ['a', 'b', 'c']
                      i.e. '{a:1, b:2}  mapf='dict' --> dict(a=1, b=2)
         :param dtype: type, the data type for output of mapf (list or dict) for
                       key
         :param paramdict: ParamDict, if defined overrides the use of params for
                           searching for "key"
         :param required: bool, if True and "key" not found
                          (and "constant" not found)
         :param default: object, the default value of key if not found (if None
                         does not set and raises error if required=True)
         :param wlog: Either None or the wlog (for printing) if wlog is not defined
                      may have to catch a DrsCodedException
                      (can put in here or before in the __init__)
        :param override: Any, an override value if set takes precendence over
                         other values

         :type params: ParamDict
         :type key: str
         :type name: str
         :type kwargs: dict
         :type func: str
         :type mapf: str
         :type dtype: type
         :type paramdict: ParamDict
         :type required: bool
         :type default: object

         :return: returns the object or list/dict (if mapf='list'/'dict')
         """
        # set function name
        func_name = display_func('find_param', __NAME__,
                                 self.class_name)
        # deal with override value
        if override is not None:
            return copy.deepcopy(override)
        # deal with wlog
        if wlog is None:
            wlog = self.wlog
        # deal with params being None
        if params is None:
            params = ParamDict()
        # deal with dictionary being None
        if paramdict is None:
            paramdict = params
        else:
            paramdict = ParamDict(paramdict)
        # deal with key being None
        if key is None and name is None:
            if wlog is not None:
                wlog(params, 'error', textentry('00-003-00004'))
            else:
                raise DrsCodedException('00-003-00004', level='error',
                                        func_name=func_name)
        elif key is None:
            key = 'Not set'
        # deal with no kwargs
        if kwargs is None:
            rkwargs = dict()
        else:
            rkwargs = dict()
            # force all kwargs to be upper case
            for kwarg in kwargs:
                rkwargs[kwarg.upper()] = kwargs[kwarg]
        # deal with no function
        if func is None:
            func = 'UNKNOWN'
        # deal with no name
        if name is None:
            name = key.upper()
        else:
            name = name.upper()

        # deal with None in rkwargs (take it as being unset)
        if name in rkwargs:
            if rkwargs[name] is None:
                del rkwargs[name]
        # deal with key not found in params
        not_in_paramdict = name not in rkwargs
        not_in_rkwargs = key not in paramdict
        return_default = (not required) or (default is not None)

        # now return a deep copied version of the value

        # if we don't require value
        if return_default and not_in_paramdict and not_in_rkwargs:
            return copy.deepcopy(default)
        elif not_in_paramdict and not_in_rkwargs:
            eargs = [key, func]
            if wlog is not None:
                wlog(params, 'error', textentry('00-003-00001', args=eargs))
            else:
                raise DrsCodedException('00-003-00001', level='error',
                                        targs=eargs, func_name=func_name)
            return copy.deepcopy(default)
        elif name in rkwargs:
            return copy.deepcopy(rkwargs[name])
        elif mapf == 'list':
            return copy.deepcopy(paramdict.listp(key, dtype=dtype))
        elif mapf == 'dict':
            return copy.deepcopy(paramdict.dictp(key, dtype=dtype))
        else:
            return copy.deepcopy(paramdict[key])


# =============================================================================
# Define functions
# =============================================================================
def update_paramdicts(*args: List[ParamDict], key: str,
                      value: Any = None,
                      source: str = None,
                      instance: Union[None, Const, Keyword] = None):
    """
    Update a set of parameter dictionarys with a key/value/source/instance

    [Updates parameter dictionaries in memory - they are not returned]

    :param args: list of parameter dictionaries
    :param key: str, the parameter dictionary key to update
    :param value: Any, the value of the key to set
    :param source: str (optional) the source of the key/value
    :param instance: Const/Keyword (optional) the Const/Keyword instance to go
                     with the key/value pair
    :return:
    """
    # set function name
    _ = display_func('update_paramdicts', __NAME__)
    # loop through param dicts
    for arg in args:
        if isinstance(arg, ParamDict):
            arg.set(key, value=value, source=source, instance=instance)


def load_config(instrument: Union[str, None] = None,
                from_file: bool = True,
                cache: bool = True) -> ParamDict:
    """
    Load an instruments configuration into a Parameter Dictionary (ParamDict)

    :param instrument: str, the instrumnet config to load (can be None)
    :param from_file: bool, if True loads from user files (else loads from
                      module only
    :param cache: bool, use the cached parameters - no need to reload from
                  module - if True and cache present supersedes from_file
    :return: ParamDict containing the constants
    """
    global CONFIG_CACHE
    # set function name (cannot break here --> no access to inputs)
    _ = display_func('load_config', __NAME__)
    # deal with no instrument
    if instrument is None:
        if 'INSTRUMENT' in base.IPARAMS:
            instrument = base.IPARAMS['INSTRUMENT']
        else:
            instrument = 'None'
    # check config cache
    if instrument in CONFIG_CACHE and cache:
        return CONFIG_CACHE[instrument].copy()
    # get instrument sub-package constants files
    modules = get_module_names(instrument)
    # get constants from modules
    keys, values, sources, instances = _load_from_module(modules, True)

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

        keys, values, sources, instances = _load_from_file(files, modules)

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
    if cache and from_file:
        CONFIG_CACHE[instrument] = params.copy()
    # return the parameter dictionary
    return params


def load_pconfig(instrument: Union[str, None] = None
                 ) -> pseudo_const.PseudoConstants:
    """
    Load an instrument pseudo constants

    :param instrument: str, the instrument to load pseudo constants for

    :return: the PesudoConstant class
    """
    global PCONFIG_CACHE
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('load_pconfig', __NAME__)
    # deal with no instrument
    if instrument is None:
        instrument = base.IPARAMS['INSTRUMENT']
    # check cache
    if instrument in PCONFIG_CACHE:
        return PCONFIG_CACHE[instrument]
    # get instrument sub-package constants files
    modules = get_module_names(instrument, mod_list=[PSEUDO_CONST_FILE])
    # import module
    module = constant_functions.import_module(func_name, modules[0])
    # get the correct module for this class
    mod = module.get()
    # check that we have class and import it
    if hasattr(mod, PSEUDO_CONST_CLASS):
        psconst = getattr(mod, PSEUDO_CONST_CLASS)
    # else raise error
    else:
        eargs = [modules[0], PSEUDO_CONST_CLASS, func_name]
        raise DrsCodedException('00-001-00046', targs=eargs, level='error',
                                func_name=func_name)

    # get instance of PseudoClass
    pconfig = psconst(instrument=instrument)
    # update cache
    PCONFIG_CACHE[instrument] = pconfig
    return pconfig


def get_config_all():
    """
    List all attributes in modules (from get_module_names)
    :return:
    """
    # set function name
    _ = display_func('get_config_all', __NAME__)
    # get module names
    modules = get_module_names('None')
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


def get_module_names(instrument: str = 'None',
                     mod_list: Union[None, List[str]] = None,
                     instrument_path: Union[str, Path, None] = None,
                     default_path: Union[str, Path, None] = None,
                     return_paths: bool = True) -> List[str]:
    """
    Get a list of module paths / names

    :param instrument: str, the instrument name
    :param mod_list: list of strings, the list of modules (in instrument path)
    :param instrument_path: str or Path, the path wher the mod files are
    :param default_path: str or Path, the default instrument path (where const
                         files for instrument = None are stored) - top level
    :param return_paths: bool, if True returns paths
                         i.e. path1/path2/filename.py
                         if False returns python like paths
                         i.e. path1.path2.filename

    :return: returns module paths or module chains (list of strings)
                 return_paths = True -> path1/path2/filename.py
                 return_paths = False -> path1.path2.filename

    :raises DrsCodedException: on exceptions
    """
    # set function name
    func_name = display_func('_get_module_names', __NAME__)
    # deal with no module list
    if mod_list is None:
        mod_list = SCRIPTS
    # deal with no path
    if drs_text.null_text(instrument_path, ['None', '']):
        instrument_path = CONST_PATH
    if default_path is None:
        default_path = CORE_PATH
    # get constants package path
    const_path = drs_misc.get_relative_folder(__PACKAGE__, instrument_path)
    core_path = drs_misc.get_relative_folder(__PACKAGE__, default_path)
    # get the directories within const_path
    filelist = np.sort(os.listdir(const_path))
    directories = []
    for filename in filelist:
        if os.path.isdir(filename):
            directories.append(filename)
    # construct sub-module name
    relpath = os.path.normpath(instrument_path).replace('.', '')
    relpath = relpath.replace(os.sep, '.').strip('.')
    corepath = os.path.normpath(default_path).replace('.', '')
    corepath = corepath.replace(os.sep, '.').strip('.')

    # construct module import name
    if instrument == 'None':
        modpath = '{0}.{1}'.format(__PACKAGE__, corepath)
        filepath = os.path.join(core_path, '')
    else:
        modpath = '{0}.{1}.{2}'.format(__PACKAGE__, relpath, instrument.lower())
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
            # log error: dev error module {0} is required to have class {1}
            eargs = [mod, fpath, func_name]
            raise DrsCodedException('00-001-00047', targs=eargs, level='error',
                                    func_name=func_name)
        # append mods
        mods.append(mod)
        paths.append(fpath)
    # make sure we found something
    if len(mods) == 0:
        # log error: DevError: no config directories found
        raise DrsCodedException('00-001-00048', targs=[func_name], level='error',
                                func_name=func_name)
    if len(mods) != len(mod_list):
        # log error: DevError: Const mod scripts missing
        eargs = [','.join(mods), ','.join(mod_list), func_name]
        raise DrsCodedException('00-001-000479', targs=eargs, level='error',
                                func_name=func_name)
    # return modules
    if return_paths:
        return paths
    else:
        return mods


def print_error(error: DrsCodedException):
    """
    Print an exceptions message/level etc

    :param error: one of the drs_exceptions classes
    :return:
    """
    # set function name
    _ = display_func('print_error', __NAME__)
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


# noinspection PyUnusedLocal
def catch_sigint(signal: Any, frame: Any):
    """
    The signal handler -
    :param signal: expected from call to signal.signal (not used)
    :param frame:  expected from call to signal.signal (not used)
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    _ = display_func('catch_sigint', __NAME__)
    # raise Keyboard Interrupt
    raise KeyboardInterrupt('\nSIGINT or CTRL-C detected. Exiting\n')


def window_size(drows: int = 80, dcols: int = 80) -> Tuple[int, int]:
    """
    Tries to work out the window size, if it cannot returns drows, dcols

    :param drows: int, default number of rows
    :param dcols: int, default number of columns
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    _ = display_func('window_size', __NAME__)
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


# =============================================================================
# Config loading private functions
# =============================================================================
def _get_file_names(params: ParamDict,
                    instrument: Union[str, None] = None) -> List[str]:
    """
    Lists the users config / constants files for the specific instrument
    if None are found returns the default files

    :param params: Paramdict - parameter dictionary
    :param instrument: str, the instrument to list files for
    :return: list of strings - the config /constant files found
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_get_file_names', __NAME__)
    # deal with no instrument
    if drs_text.null_text(instrument, ['None', '']):
        return []
    # get user environmental path
    user_env = params['DRS_USERENV']
    # deal with no user environment and no default path
    if user_env is None:
        return []
    # set empty directory
    config_dir = None
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
            config_dir = path
    # -------------------------------------------------------------------------
    # if directory is still empty return empty list
    if config_dir is None:
        return []
    # -------------------------------------------------------------------------
    # look for user configurations within instrument sub-folder
    # -------------------------------------------------------------------------
    config_files = []
    for script in USCRIPTS:
        # construct path
        config_path = os.path.join(config_dir, script)
        # check that it exists
        if os.path.exists(config_path):
            config_files.append(config_path)
    # deal with no files found
    if len(config_files) == 0:
        wargs = [config_dir, ','.join(USCRIPTS)]
        DrsCodedWarning('00-003-00036', 'warning', targs=wargs,
                        func_name=func_name)
    # return files
    return config_files


def _load_from_module(modules: List[str], quiet: bool = False) -> ModLoads:
    """
    Load constants/keywords from modules and validates them

    :param modules: list of strings, the module paths
    :param quiet: bool, if True prints when validating
    :return: list of keys (str), list of values (Any), list of sources (str),
             list of instances (either Const or Keyword instances)
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_load_from_module', __NAME__)
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
                raise DrsCodedException('00-003-00006', targs=eargs,
                                        level='error', func_name=func_name)
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


def _load_from_file(files: List[str], modules: List[str]) -> ModLoads:
    """
    Load constants/keywords from a list of config/const files and validates them

    :param files: list of strings, the file paths to the config/const files
    :param modules: list of strings, the module paths

    :return: list of keys (str), list of values (Any), list of sources (str),
             list of instances (either Const or Keyword instances)
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_load_from_file', __NAME__)
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
                DrsCodedWarning('10-002-00002', 'warning', targs=wargs,
                                func_name=func_name)
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


def _save_config_params(params: ParamDict) -> ParamDict:
    """
    Adds 'DRS_CONFIG' list of config files to parameter dictionary

    :param params: ParamDict - the parameter dictionary of constants

    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_save_config_params', __NAME__)
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


def _check_mod_source(source: str) -> Union[None, str]:
    """
    Check that the source (a module file) is a python mod path
    i.e. path1.path2.filename  and not a file path
    i.e. path1/path2/filename.py

    :param source: str, the moudle source to check
    :return: str, the cleaned source i.e. path1.path2.filename
    """
    # set function name (cannot break here --> no access to inputs)
    _ = display_func('_check_mod_source', __NAME__)
    # deal with source is None
    if source is None:
        return source
    # if source doesn't exist also skip
    if not os.path.exists(source):
        return source
    # get package path
    package_path = drs_misc.get_relative_folder(__PACKAGE__, '')
    # if package path not in source then skip
    if package_path not in source:
        return source
    # remove package path and replace with PACKAGE
    source = source.replace(package_path, __PACKAGE__.lower())
    # replace separators with .
    source = source.replace(os.sep, '.')
    # remove double dots
    while '..' in source:
        source = source.replace('..', '.')
    # return edited source
    return source


# =============================================================================
# Other private functions
# =============================================================================
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
    _ = display_func('_load_from_file', __NAME__)
    # get the list as a string
    str_value = list(values).__repr__()
    # if the string is longer than 40 characters cut down and add ...
    if len(str_value) > 40:
        str_value = str_value[:40] + '...'
    # return the string as a list entry
    return [fmt.format(key, str_value, source)]


def _map_listparameter(value: Union[str, list], separator: str = ',',
                       dtype: Union[None, Type] = None) -> list:
    """
    Map a string list into a python list

    :param value: str or list, if list returns if string tries to evaluate
    :param separator: str, where to split the str at to make a list
    :param dtype: type, if set forces elements of list to this data type
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_map_listparameter', __NAME__)
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
        raise DrsCodedException('00-003-00002', targs=eargs, level='error',
                                func_name=func_name)


def _map_dictparameter(value: str, dtype: Union[None, Type] = None) -> dict:
    """
    Map a string dictionary into a python dictionary

    :param value: str, tries to evaluate string into a dictionary
                  i.e. "dict(a=1, b=2)"  or {'a':1, 'b': 2}

    :param dtype: type, if set forces elements of list to this data type
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_map_dictparameter', __NAME__)
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
        raise DrsCodedException('00-003-00003', targs=eargs, level='error',
                                func_name=func_name)


def _yaml_walk(yaml_dict) -> Tuple[list, list]:
    """
    Turn a yaml dictionary into a list of keys and a list of values

    :param yaml_dict: dict, the yaml nested dictionary

    :return: tuple 1. list of keys, 2. list of values
    """
    chains, values = [], []
    for key in yaml_dict:
        if isinstance(yaml_dict[key], dict):
            links, link_values = _yaml_walk(yaml_dict[key])
            for it, link in enumerate(links):
                chain = '{0}.{1}'.format(key, link)
                chains.append(chain)
                values.append(link_values[it])
        else:
            chains.append(key)
            values.append(yaml_dict[key])
    return chains, values


def _add_recipe_params_to_table_dict(tabledict: dict, recipe: Any) -> dict:
    """
    Add parameters from the recipe (and recipe log) if present

    :param tabledict: dict, the table dict with each column as a list
    :param recipe: DrsRecipe instance that called this function

    :return: dict, the updated table dictionary
    """
    # deal with no recipe
    if recipe is None:
        return tabledict
    # deal with no log
    if recipe.log is None:
        return tabledict
    if len(recipe.log.set) == 0:
        instances = [recipe.log]
    else:
        instances = recipe.log.set
    # loop
    inst = instances[-1]
    # get the param table
    out = inst.get_param_table()
    # extract list from get_param_table return
    names, param_kinds, values, sources, descriptions, counts = out
    # loop around and add to table dict
    for row in range(len(names)):
        # add database key name
        tabledict['NAME'].append(names[row])
        # add database key kind
        tabledict['KIND'].append(param_kinds[row])
        # add database key value
        tabledict['VALUE'].append(values[row])
        # add database key source (database yaml file)
        tabledict['SOURCE'].append(sources[row])
        # add database description (default)
        tabledict['DESCRIPTION'].append(descriptions[row])
        # add database count (always 1)
        tabledict['COUNT'].append(counts[row])
    # return updated table dict
    return tabledict


def _add_param_dict_to_tabledict(tabledict: dict,
                                 data: Union[ParamDict, dict, list],
                                 key: Union[str, int],
                                 instances: Union[CaseInDict, None] = None,
                                 sources: Union[CaseInDict, None] = None,
                                 used: Union[CaseInDict, None] = None,
                                 it: Union[int, None] = None,
                                 pkey: Union[str, None] = None) -> dict:
    """
    Add a parameter dictionary, dictionary or list to the tabledict

    :param tabledict: dict, the table dict with each column as a list
    :param data: paramdict, dict or list to add to the tabledict
    :param key: str, the name to give in the tabledict
    :param instances: dict of instances (Const or Keyword), this is accessed
                      by pkey and sets the description i.e. instances must have
                      the "description" method
    :param sources: dict of strings, the source of each parameter (accessed by
                    pkey)
    :param used: dict of ints, the number of times a parameter was used
                 (accessed by pkey)
    :param it: int, an iterator either added to the key (for the name) or used
               when data is a list
    :param pkey: key, the key to find variables in input dictionaries

    :return: dict, the table dictionary
    """
    # -------------------------------------------------------------------------
    # deal with pkay not set
    if pkey is None:
        pkey = str(key)
    # -------------------------------------------------------------------------
    # get the instance
    if instances is None:
        instance = None
    else:
        instance = instances[pkey]
        # if we have a constant check that we want to output it
        if isinstance(instance, (Const, Keyword)):
            # attribute output = False means we don't add
            if not instance.output:
                return tabledict
    # -------------------------------------------------------------------------
    # get the source
    if sources is None:
        source = None
    else:
        source = sources[pkey]
    # -------------------------------------------------------------------------
    # deal with data being list
    if isinstance(data, list):
        value = data[it]
    else:
        # add value (if list)
        value = data[pkey]
    # -------------------------------------------------------------------------
    # deal with value being a parameter dictionary itself
    if isinstance(value, ParamDict):
        # loop around keys in parameter dictionary
        for jt, skey in enumerate(value.keys()):
            # key to go into function
            rkey = '{0}[{1}]'.format(key, skey)
            # try to add sub-level to table dict
            tabledict = _add_param_dict_to_tabledict(tabledict, value.data,
                                                     rkey, value.instances,
                                                     value.sources, value.used,
                                                     None, pkey=skey)
        # stop here
        return tabledict
    # -------------------------------------------------------------------------
    # deal with a value being a dictionary
    elif isinstance(value, dict):
        # loop around keys in dictionary
        for jt, skey in enumerate(value.keys()):
            # key to go into function
            rkey = '{0}[{1}]'.format(key, skey)
            # try to add sub-level to table dict
            tabledict = _add_param_dict_to_tabledict(tabledict, value,
                                                     rkey, instances, sources,
                                                     used, None, pkey=skey)
        # stop here
        return tabledict
    # -------------------------------------------------------------------------
    # deal with a value being a list (but not keyword stores)
    elif isinstance(value, list) and not key.startswith('KW_'):
        # loop around elements in list
        for jt in range(len(value)):
            # try to add sub-level to table dict
            tabledict = _add_param_dict_to_tabledict(tabledict, value, key,
                                                     instances, sources,
                                                     used, jt, pkey=pkey)
        # stop here
        return tabledict
    # -------------------------------------------------------------------------
    # deal with keyword stores
    elif isinstance(value, list) and key.startswith('KW_'):
        # keywords will be added manually
        return tabledict
    # -------------------------------------------------------------------------
    # deal with other simple types
    elif isinstance(value, (str, int, float, bool)):
        # add skip if not used
        if pkey not in used:
            return tabledict
        # add to count
        tabledict['COUNT'].append(used[pkey])
        # fill in value
        tabledict['VALUE'].append(str(value))
        # fill in row
        if it is not None:
            tabledict['NAME'].append('{0}[{1}]'.format(key, it))
        else:
            tabledict['NAME'].append(key)
        tabledict['KIND'].append('parameter')
        # add description
        if instance is not None and hasattr(instance, 'description'):
            tabledict['DESCRIPTION'].append(instance.description)
        else:
            tabledict['DESCRIPTION'].append('Parameter in parameter '
                                            'dictionary')
        # add source
        if source is not None:
            tabledict['SOURCE'].append(source)
        else:
            tabledict['SOURCE'].append('None')
    # return table dictionary
    return tabledict


AddHdictReturn = Tuple[List[str], List[str], List[Any], List[str], List[str]]


def _add_hdict(drsfitsfile: Any, names: Union[List[str], None] = None,
               kinds: Union[List[str], None] = None,
               values: Union[List[Any], None] = None,
               sources: Union[List[str], None] = None,
               descs: Union[List[str], None] = None) -> AddHdictReturn:
    """
    Extract out of drs fits file the hdict and push it into
    names, values, sources, desc (for insertion into tabledict)

    :param drsfitsfile: DrsFitsFile
    :param names: list of strings or None - the names currently set to add to
                 tabledict
    :param kinds: list of strings or None - the kinds currently set to add to
                  tabledict
    :param values: list of strings or None - the values currently set to
                   add to tabledict
    :param sources: list of strings or None - the sources currently set to add
                    to tabledict
    :param descs: list of strings or None - the descriptions currently set to
                  add to tabledict

    :return: tuple containing the names/values/sources/descriptions
    """
    # deal with drsfitsfile not being correct (just skip this step)
    if not hasattr(drsfitsfile, 'hdict'):
        return names, kinds, values, sources, descs
    else:
        # get hdict
        hdict = drsfitsfile.hdict
        # set filename (for source)
        filename = drsfitsfile.filename
        # make sure hdict is correct
        if not isinstance(hdict, fits.Header):
            return names, kinds, values, sources, descs
    # if any are None just set them all to empty lists
    if names is None:
        names, kinds, values, sources, descs = [], [], [], [], []
    # loop around keys
    for key in hdict.keys():
        # add header key as name
        names.append(key)
        # add kind set to header
        kinds.append('header')
        # set the value to the header value
        values.append(hdict[key])
        # set the source to the header of a filename
        sources.append('HEADER: {0}'.format(filename))
        # set the description from the header comment
        descs.append(hdict.comments[key])
    # return the lists for insertion into table dict
    return names, kinds, values, sources, descs


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
