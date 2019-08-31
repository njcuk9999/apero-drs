#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constants parameter functions

DRS Import Rules:

- only from terrapipe.locale

Created on 2019-01-17 at 15:24

@author: cook
"""
import numpy as np
import sys
import os
import pkg_resources
import copy

from collections import OrderedDict

from terrapipe.locale import drs_exceptions
from . import constant_functions

# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'param_functions.py'
# Define package name
PACKAGE = 'terrapipe'
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
        self.instances = CaseInsensitiveDict()
        self.locked = False
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

    def __setitem__(self, key, value, source=None, instance=None):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter
        :param source: string, the source for the parameter
        :return:
        """
        if self.locked:
            emsg = 'ParamDict locked. \n\t Cannot add \'{0}\'=\'{1}\''
            raise ConfigError(emsg.format(key, value))

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

    def __repr__(self):
        return self._string_print()

    def __str__(self):
        return self._string_print()

    def set(self, key, value, source=None, instance=None):
        """
        Set an item even if params is locked

        :param key:
        :param value:
        :param source:
        :param instance:
        :return:
        """
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
        self.locked = True

    def unlock(self):
        self.locked = False

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

        # don't put full path for sources in package
        source = _check_mod_source(source)

        # only add if key is in main dictionary
        if key in self.keys():
            self.sources[key] = source
        else:
            emsg1 = 'Source cannot be added for key "{0}" '.format(key)
            emsg2 = '     "{0}" is not in Parameter Dictionary'.format(key)
            raise ConfigError([emsg1, emsg2], level='error')

    def set_instance(self, key, instance):
        # capitalise
        key = _capitalise_key(key)
        # only add if key is in main dictionary
        if key in self.keys():
            self.instances[key] = instance
        else:
            emsg1 = 'Instance cannot be added for key "{0}" '.format(key)
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

    def set_instances(self, keys, instances):
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
            if type(instances) == list:
                instance = instances[k_it]
            elif type(instances) == dict:
                instance = instances[key]
            else:
                instance = instances
            # set source
            self.set_instance(key, instance)

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

    def get_instance(self, key):
        """
        Get a source from the parameter dictionary (must be set)

        raises a ConfigError if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        # capitalise
        key = _capitalise_key(key)
        # if key in keys and sources then return source
        if key in self.keys() and key in self.instances.keys():
            return self.instances[key]
        # else raise a Config Error
        else:
            emsg = 'No instance set for key={0} in ParamDict'
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
            # try to deep copy parameter
            try:
                pp[key] = copy.deepcopy(value)
            except Exception as _:
                pp[key] = type(value)(value)
            # copy source
            if key in self.sources:
                pp.set_source(key, self.sources[key])
            else:
                pp.set_source(key, None)
            # copy instance
            if key in self.instances:
                pp.set_instance(key, self.instances[key])
            else:
                pp.set_instance(key, None)
        # return new param dict filled
        return pp

    def _string_print(self):
        pfmt = '\t{0:30s}{1:45s} # {2}'

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
                sargs = [key, list(value), self.sources[key], pfmt]
                strvalues  += _string_repr_list(*sargs)
            elif type(value) in [dict, OrderedDict, ParamDict]:
                strvalue = list(value.keys()).__repr__()[:40]
                sargs = [key + '[DICT]', strvalue, self.sources[key]]
                strvalues += [pfmt.format(*sargs)]
            else:
                strvalue = str(value)[:40]
                sargs = [key + ':', strvalue, self.sources[key]]
                strvalues += [pfmt.format(*sargs)]
        # combine list into single string
        for string_value in strvalues:
            return_string += '\n {0}'.format(string_value)
        # return string
        return return_string + '\n'

    def listp(self, key, separator=',', dtype=None):
        if key in self.keys():
            return _map_listparameter(self.__getitem__(key),
                                      separator=separator, dtype=dtype)
        else:
            emsg = ('Config Error: Parameter "{0}" not found in parameter '
                    'dictionary (via listp)')
            raise ConfigError(emsg.format(key), level='error')

    def dictp(self, key, dtype=None):
        if key in self.keys():
            return _map_dictparameter(self.__getitem__(key), dtype=dtype)
        else:
            emsg = ('Config Error: Parameter "{0}" not found in parameter '
                    'dictionary (via dictp)')
            raise ConfigError(emsg.format(key), level='error')

    def get_keyword_instances(self):
        keyworddict = dict()
        # loop around all keys
        for key in list(self.instances.keys()):
            # get the instance for this key
            instance = self.instances[key]
            # skip None
            if instance is None:
                continue
            # else check instance type
            if isinstance(instance, constant_functions.Keyword):
                keyworddict[instance.key] = instance
            else:
                continue
        # return keyworddict
        return keyworddict


# =============================================================================
# Define functions
# =============================================================================
def update_paramdicts(*args, **kwargs):
    key = kwargs.get('key', None)
    value = kwargs.get('value', None)
    source = kwargs.get('source', None)
    instance = kwargs.get('instance', None)
    # loop through param dicts
    for arg in args:
        if isinstance(arg, ParamDict):
            arg.set(key, value=value, source=source, instance=instance)


def load_config(instrument=None):
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
    # get instrument user config files
    files = _get_file_names(params, instrument)
    # get constants from user config files
    try:
        keys, values, sources, instances  = _load_from_file(files, modules)
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
    # return the parameter dictionary
    return params


def load_pconfig(instrument=None):
    func_name = __NAME__ + '.load_pconfig()'
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
        PsConst = getattr(mod, PSEUDO_CONST_CLASS)
    # else raise error
    else:
        emsg = 'Module "{0}" is required to have class "{1}"'
        ConfigError(emsg.format(modules[0], PSEUDO_CONST_CLASS))
        sys.exit(1)
    # return instance of PseudoClass
    return PsConst(instrument=instrument)


def get_config_all():
    modules = get_module_names(None)

    for module in modules:
        rawlist = constant_functions.generate_consts(module)[0]

        print('='*50)
        print('MODULE: {0}'.format(module))
        print('='*50)
        print('')
        print('__all__ = [\'{0}\']'.format('\', \''.join(rawlist)))
        print('')


def get_file_names(instrument=None, file_list=None, instrument_path=None,
                     default_path=None):
    func_name = __NAME__ + '.get_file_names()'

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
    func_name = __NAME__ + '._get_module_names()'

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
    print('\n')
    print('='*70)
    print(' Configuration file {0}:'.format(error.level))
    print('=' * 70, '\n')
    estring = error.message
    if type(estring) is not list:
        estring = [estring]
    for emsg in estring:
        emsg = emsg.replace('\n', '\n\t')
        print('\t' + emsg)

    print('='*70, '\n')


# =============================================================================
# Config loading private functions
# =============================================================================
def _get_file_names(params, instrument=None):

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
    subdir = None
    for filename in os.listdir(directory):
        cond1 = os.path.isdir(os.path.join(directory, filename))
        cond2 = filename.lower() == instrument.lower()
        if cond1 and cond2:
            subdir = filename
    # deal with instrument sub-folder not found
    if subdir is None:
        wmsg1 = ('User config defined in {0} but instrument '
                '"{1}" directory not found')
        wmsg2 = '\tDirectory = "{1}"'.format(source, os.path.join(directory))
        wmsg3 = '\tUsing default configuration files.'
        ConfigWarning([wmsg1.format(source, instrument.lower()), wmsg2, wmsg3])
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


def _load_from_module(modules, quiet=False):
    func_name = __NAME__ + '._load_from_module()'
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
                emsgs = ['Duplicate Const parameter "{0}" for instrument "{1}"'
                         ''.format(key, module),
                         '\tModule list: {0}'.format(','.join(modules)),
                         '\tfunction = {0}'.format(func_name)]
                raise ConfigError(emsgs, level='error')
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
                wmsg1 = 'Key {0} duplicated in "{1}"'
                wargs1 = [fkeyi, filename]
                wmsg2 = '\tOther configs: {0}'.format(','.join(set(fsources)))
                wmsg3 = '\tConfig File = "{0}"'.format(filename)
                ConfigWarning([wmsg1.format(*wargs1), wmsg2, wmsg3])
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


def _save_config_params(params,):
    func_name = __NAME__ + '._save_config_params()'
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


def _check_mod_source(source):
    # deal with source being None
    if source is None:
        return None
    # get package path
    package_path = get_relative_folder(PACKAGE, '')
    # if package path not in source then skip
    if package_path not in source:
        return source
    # if source doesn't exist also skip
    if not os.path.exists(source):
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


def _string_repr_list(key, values, source, fmt):
    str_value = list(values).__repr__()
    if len(str_value) > 40:
        str_value = str_value[:40] + '...'
    return [fmt.format(key, str_value, source)]


def _map_listparameter(value, separator=',', dtype=None):

    func_name = __NAME__ + '._map_listparameter()'
    # try evaulating as a list
    try:
        rawvalue = eval(value)
        if isinstance(rawvalue, list):
            return list(rawvalue)
    except Exception as e:
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
        error = ('Parameter \'{0}\' can not be converted to a list.' 
                 '\n\t Error {1}: {2}. \n\t function = {3}')
        BLOG(message=error.format(eargs), level='error')


def _map_dictparameter(value, dtype=None):
    func_name = __NAME__ + '._map_dictparameter()'
    # deal with an empty value i.e. ''
    if value == '':
        return []
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
        error = ('Parameter \'{0}\' can not be converted to a dictionary.' 
                 '\n\t Error {1}: {2}. \n\t function = {3}')
        BLOG(message=error.format(eargs), level='error')


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
