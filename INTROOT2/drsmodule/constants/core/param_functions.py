#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 15:24

@author: cook
"""
import numpy as np
import os
import pkg_resources
import importlib
from collections import OrderedDict

from . import constant_functions


# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'config.py'
# Define package name
PACKAGE = 'drsmodule'
# Define relative path to 'const' sub-package
CONST_PATH = './configuration/instruments/'
CORE_PATH = './constants/default/'
# Define config/constant/keyword scripts to open
SCRIPTS = ['default_config.py', 'default_constants.py', 'default_keywords.py']
USCRIPTS = ['user_config.ini', 'user_constants.ini', 'user_keywords.ini']
PSEUDO_CONST_FILE = 'pseudo_const.py'
PSEUDO_CONST_CLASS = 'PseudoConstants'
# Define the Config Exception
ConfigError = constant_functions.ConfigError
ConfigWarning = constant_functions.ConfigWarning



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

    def __repr__(self):
        return self._string_print()

    def __str__(self):
        return self._string_print()

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

    def _string_print(self):
        pfmt = '\t{0:30s}{1:45s}// {2}'

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
            # print value
            if type(value) in [list, np.ndarray]:
                sargs = [key, list(value), self.sources[key], pfmt]
                strvalues  += _string_repr_list(*sargs)
            elif type(value) in [dict, OrderedDict, ParamDict]:
                strvalue = list(value.keys()).__repr__()[:40]
                sargs = [key + '[DICT]', strvalue, self.sources[key]]
                strvalues += [pfmt.format(*sargs)]
            else:
                strvalue = value.__repr__()[:40]
                sargs = [key + ':', strvalue, self.sources[key]]
                strvalues += [pfmt.format(*sargs)]
        # combine list into single string
        for string_value in strvalues:
            return_string += '\n {0}'.format(string_value)
        # return string
        return return_string + '\n'


# =============================================================================
# Define functions
# =============================================================================
def load_config(instrument=None):
    # get instrument sub-package constants files
    modules = get_module_names(instrument)
    # deal with no instrument
    if instrument is None:
        quiet = True
    else:
        quiet = False
    # get constants from modules
    keys, values, sources = _load_from_module(modules, True)
    params = ParamDict(zip(keys, values))
    # Set the source
    params.set_sources(keys=keys, sources=sources)
    # save sources to params
    params = _save_config_params(params, sources)
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


def load_pconfig(instrument=None):
    # get instrument sub-package constants files
    modules = get_module_names(instrument, mod_list=[PSEUDO_CONST_FILE])
    # get PseudoConstants class from modules

    mod = importlib.import_module(modules[0])

    # check that we have class and import it
    if hasattr(mod, PSEUDO_CONST_CLASS):
        PsConst = getattr(mod, PSEUDO_CONST_CLASS)
    # else raise error
    else:
        emsg = 'DevError: Module "{0}" is required to have class "{1}"'
        raise ConfigError(emsg.format(modules[0], PSEUDO_CONST_CLASS))

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


def get_module_names(instrument=None, mod_list=None, instrument_path=None,
                     default_path=None):
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
    const_path = _get_relative_folder(PACKAGE, instrument_path)
    core_path = _get_relative_folder(PACKAGE, default_path)
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
        if not os.path.exists(fpath):
            emsgs = ['DevError: Const mod path "{0}" does not exist.'
                     ''.format(mod),
                     '\tpath = {0}'.format(fpath),
                     '\tfunction = {0}'.format(func_name)]
            raise ConfigError(emsgs, level='error')
        # append mods
        mods.append(mod)
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
    return mods


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
    user_dpath = _get_relative_folder(drs_package, user_dpath)
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
                 'has not configurations files')
        wmsg2 = '\tValid configuration files: {0}'.format(','.join(USCRIPTS))
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
        wmsg = ('User config defined in {0} but instrument '
                '"{1}" directory not found')
        ConfigWarning(wmsg.format(source, instrument))
    # return the subdir
    return subdir


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


def _load_from_module(modules, quiet=False):
    func_name = __NAME__ + '._load_from_module()'
    # storage for returned values
    keys, values, sources = [], [], []
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
                sources.append(module)
    # return keys
    return keys, values, sources


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
                ConfigWarning([wmsg1.format(*wargs1), wmsg2])
            # append to list
            fkeys.append(fkeyi)
            fvalues.append(fvaluei)
            fsources.append(filename)
    # -------------------------------------------------------------------------
    # Now need to test the values are correct
    # -------------------------------------------------------------------------
    # storage for returned values
    keys, values, sources = [], [], []
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
                value = mvalue.validate(fvalues[jt])
                # now append to output lists
                keys.append(fkeys[jt])
                values.append(value)
                sources.append(fsources[jt])
    # return keys values and sources
    return keys, values, sources


def _save_config_params(params, sources):
    func_name = __NAME__ + '._save_config_params()'
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
