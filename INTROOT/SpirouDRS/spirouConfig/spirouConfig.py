#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spirou configuration module

Created on 2017-10-11 at 13:09

@author: cook

Import rules: Only from spirouConfig
"""
from __future__ import division
import os
from . import spirouConst as Constants
from . import spirouConfigFile

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouConfig.py'
# Get version and author
__version__ = Constants.VERSION()
__author__ = Constants.AUTHORS()
__date__ = Constants.LATEST_EDIT()
__release__ = Constants.RELEASE()
# -----------------------------------------------------------------------------
# Get constant parameters
PACKAGE = Constants.PACKAGE()
CONFIG_FILE = Constants.CONFIGFILE()
CONFIGFOLDER = Constants.CONFIGFOLDER()
TRIG_KEY = Constants.LOG_TRIG_KEYS()
ConfigException = spirouConfigFile.ConfigException

# =============================================================================
# Define Custom classes
# =============================================================================
class ConfigError(ConfigException):
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
            self.message = 'Config Error'
        elif type(message) == str:
            self.message = 'Config Error: ' + message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        elif level in TRIG_KEY.keys():
            self.level = level
        else:
            self.level = 'error'
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
        return self.args[0]

    # overwrite print message with args[0]
    def __str__(self):
        return self.args[0]


class ParamDict(dict):
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
        self.sources = dict()
        super(ParamDict, self).__init__(*arg, **kw)
        self.__capitalise_keys__()

    def __getitem__(self, key):
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :return value: object, the value stored at position "key"
        """
        oldkey = key
        key = self.__capitalise_key__(key)
        try:
            return super(ParamDict, self).__getitem__(key)
        except KeyError:
            emsg = 'Parameter "{0}" not found in parameter dictionary'
            raise ConfigError(emsg.format(oldkey), level='error')

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
        key = self.__capitalise_key__(key)
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
        key = self.__capitalise_key__(key)
        return super(ParamDict, self).__contains__(key)

    def __delitem__(self, key):
        """
        Deletes the "key" from ParamDict instance, case insensitive

        :param key: string, the key to delete from ParamDict instance,
                    case insensitive

        :return None:
        """

        key = self.__capitalise_key__(key)
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
        # capitalise string keys
        key = self.__capitalise_key__(key)
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
        # capitalise string keys
        key = self.__capitalise_key__(key)
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
        # capitalise string keys
        key = self.__capitalise_key__(key)
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
            # capitalise string keys
            key = self.__capitalise_key__(key)
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
            # capitalise string keys
            key = self.__capitalise_key__(key)
            # set key
            self.sources[key] += ' {0}'.format(source)

    def get_source(self, key):
        """
        Get a source from the parameter dictionary (must be set)

        raises a ConfigError if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        # capitalise string keys
        key = self.__capitalise_key__(key)
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
                value = super(ParamDict, self).__getitem__(key)
                # delete old key
                super(ParamDict, self).__delitem__(key)
                # if it is a string set it to upper case
                key = key.upper()
                # set the new key
                super(ParamDict, self).__setitem__(key, value)

    def __capitalise_key__(self, key):
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
#   Read/Write/Get Functions
# =============================================================================
def read_config_file(config_file=None):
    """
    Read config file wrapper (push into ParamDict)

    :param config_file: string or None, the config_file name, if none uses
                        PACKAGE/CONFIGFOLDER and CONFIG_FILE to get config
                        file name
    :return params: parameter dictionary with key value pairs fron config file
    """
    # TODO: store user config in /home/$USER/.spirou_config
    # TODO: This will avoid having to rewrite config for every update
    # TODO: Read default parameters and then add "user parameters" to them
    ckwargs = dict(package=PACKAGE, configfolder=CONFIGFOLDER,
                   configfile=CONFIG_FILE, config_file=config_file)
    keys, values = spirouConfigFile.read_config_file(**ckwargs)
    # convert key value pairs into dictionary
    # TODO: use default parameters to check format/range etc for config
    # TODO: return error if user defined config file is wrong
    params = ParamDict(zip(keys, values))
    # Set the source
    params.set_sources(keys=keys, sources=config_file)
    # return dictionary
    return params


def load_config_from_file(p, key, required=False, logthis=False):
    """
    Load a secondary level confiruation file filename = "key", this requires
    the primary config file to already be loaded into "p"
    (i.e. p['DRS_CONFIG'] and p[key] to be set)

    :param p: parameter dictionary, contains constants (at least 'DRS_CONFIG'
              and "key" to be set)
    :param key: string, the key to access the config file name for (in "p")
    :param required: bool, if required is True then the secondary config file
                     is required for the DRS to run and a ConfigError is raised
                     (program exit)
    :param logthis: bool, if True loading of this config file is logged to
                    screen/log file

    :return p: parameter, dictionary, the updated parameter dictionary with
               the secondary configuration files loaded into it as key/value
               pairs
    """
    func_name = __NAME__ + '.load_config_from_file()'
    # Check that DRS_CONFIG and "key" is in p
    check_config(p, ['DRS_CONFIG', key])
    # construct icdp file name
    filename = os.path.join(p['DRS_CONFIG'], p[key])
    # try to open file
    if os.path.exists(filename):
        # read config file into new dictionary
        newparams = read_config_file(filename)
        # merge with param file
        for newkey in list(newparams.keys()):
            # Warn the user than key is being overwritten
            if newkey in list(p.keys()):
                wmsg = 'Warning key {0} overwritten by config: {1}'
                raise ConfigError(wmsg.format(newkey, filename),
                                  level='warning')
            # Write key
            p[newkey] = newparams[newkey]
            # set the source of new parameter
            p.set_source(newkey, source=filename)
        # log output
        if logthis:
            emsg = '{0} loaded from: {1}'.format(key, filename)
            raise ConfigError(emsg, level='all')
    else:
        if required:
            # log error
            emsg1 = 'Config file "{0}" not found'.format(filename)
            emsg2 = '   function = {0}'.format(func_name)
            raise ConfigError([emsg1, emsg2], level='error')
    # return p
    return p


def extract_dict_params(pp, suffix, fiber, merge=False):
    """
    Extract parameters from parameter dictionary "pp" with a certain suffix
    "suffix" (whose value must be a dictionary containing fibers) add them
    to a new parameter dictionary (if merge=False) if merge is True then
    add them back to the "pp" parameter dictionary

    :param pp: parameter dictionary, containing constants
    :param suffix: string, the suffix string to look for in "pp", all keys
                   must have values that are dictionaries containing (at least)
                   the key "fiber"

                   i.e. in the constants file:
                   param1_suffix = {'AB'=1, 'B'=2, 'C'=3}
                   param2_suffix = {'AB'='yes', 'B'='no', 'C'='no'}
                   param3_suffix = {'AB'=True, 'B'=False, 'C'=True}

    :param fiber: string, the key within the value dictionary to look for
                  (i.e. in the above example 'AB' or 'B' or 'C' are valid
    :param merge: bool, if True merges new keys with "pp" else provides
                  a new parameter dictionary with all parameters that had the
                  suffix in (with the suffix removed)

    :return ParamDict: if merge is True "pp" is returned with the new constants
                       added, else a new parameter dictionary is returned

        i.e. for the above example return is the following:

            "fiber" = "AB"

            ParamDict(param1=1, param2='yes', param3=True)

    """
    func_name = __NAME__ + '.extract_dict_params()'
    # make suffix uppercase
    suffix = suffix.upper()
    # set up the fiber parameter directory
    fparam = ParamDict()
    # get keys list
    keys = list(pp.keys())
    # loop around keys in FIBER_PARAMS
    for key in keys:
        # skip if suffix not in key
        if suffix not in key:
            continue
        # skip if suffix not at the end of key
        if key[-len(suffix):] != suffix:
            continue
        # try to evaluate key:
        #    raise error if key does not evaluate to a dictionary
        #    raise error if 'fiber' not in dictionary
        try:
            if type(pp[key]) == dict:
                params = pp[key]
            elif type(pp[key]) == str:
                params = eval(pp[key])
                if type(params) != dict:
                    raise NameError('')
                if fiber not in params:
                    raise ConfigError('')
            else:
                raise TypeError('')
        except NameError:
            emsg1 = ('Parameter={0} has suffix="{1}" and must be a valid python'
                     ' dictionary in form {\'key\':value}').format(key, suffix)
            emsg2 = '    function={0}'.format(func_name)
            raise ConfigError([emsg1, emsg2], level='error')
        except ConfigError:
            emsg1 = 'Parameter={0} has suffix="{1}"'
            emsg2 = ('   it must be a dictionary containing (at least) the '
                     'key {2}').format(key, suffix, fiber)
            emsg3 = '    function={0}'.format(func_name)
            raise ConfigError([emsg1, emsg2, emsg3], level='error')
        except TypeError:
            emsg1 = 'Parameter={0} must be a dictionary'.format(key)
            emsg2 = ('    dictionary must be in form {\'key\':value}'
                     '').format(key, suffix)
            emsg3 = '    function={0}'.format(func_name)
            raise ConfigError([emsg1, emsg2, emsg3], level='error')
        # we have dictionary with our fiber key so can now get value
        value = params[fiber]
        # get new key without the suffix
        newkey = key[:-len(suffix)]
        # get the old source
        source = pp.get_source(key)
        # construct new source
        newsource = '{0}+{1}/fiber_params()'.format(source, __NAME__)
        # add to pp (if merge) else add to new parameter dictionary
        if merge:
            pp[newkey] = value
            pp.set_source(newkey, newsource)
        else:
            fparam[newkey] = value
            fparam.set_source(newkey, newsource)

    # add fiber to the parameters
    if merge:
        pp['fiber'] = fiber
        pp.set_source('fiber', __NAME__ + '/fiber_params()')
    else:
        fparam['fiber'] = fiber
        fparam.set_source('fiber', __NAME__ + '/fiber_params()')

    # return pp if merge or fparam if not merge
    if merge:
        return pp
    else:
        return fparam


# =============================================================================
#    Checking functions
# =============================================================================
def check_config(params, keys):
    """
    Check whether we have certain keys in dictionary
    raises a Config Error if keys are not in params

    :param params: parameter dictionary
    :param keys: string or list of strings containing the keys to look for

    :return None:
    """
    func_name = __NAME__ + '.check_config()'
    # get config file path
    # config_file = get_default_config_file()
    # make sure we have a list
    if type(keys) == str:
        keys = [keys]
    elif hasattr(keys, '__len__'):
        keys = list(keys)
    else:
        emsg1 = 'Key(s) must be string or list of strings'
        emsg2 = '    function = {0}'.format(func_name)
        raise ConfigError([emsg1, emsg2], level='error')
    # loop around each key and check if it exists
    for key in keys:
        if key not in params:
            # if there is an error return error message
            emsg = 'key "{0}" not found, it must be defined in a config file'
            # return error message
            raise ConfigError(emsg.format(key), level='error')


def check_params(p):
    """
    Check the parameter dictionary has certain required values, p must contain
    at the very least keys 'DRS_ROOT' and 'TDATA'

    :param p: dictionary, parameter dictionary
               (must have at least keys 'DRS_ROOT' and 'TDATA')

    :return p: dictionary, the updated parameter dictionary
    """
    func_name = __NAME__ + '.check_params()'
    # get log levels
    loglevels = list(TRIG_KEY.keys())
    # check that the drs_root and tdata variables are named
    check_config(p, ['DRS_ROOT', 'TDATA'])
    # check whether we have drs_data_raw key
    tmp = os.path.join(p['TDATA'], 'raw', '')
    p = check_set_default_val(p, 'DRS_DATA_RAW', tmp, func_name)

    # check whether we have drs_data_reduc key
    tmp = os.path.join(p['TDATA'], 'reduced', '')
    p = check_set_default_val(p, 'DRS_DATA_REDUC', tmp, func_name)

    # check whether we have drs_data_msg key
    tmp = os.path.join(p['TDATA'], 'msg', '')
    p = check_set_default_val(p, 'DRS_DATA_MSG', tmp, func_name)

    # check whether we have drs_calib_db key
    tmp = os.path.join(p['TDATA'], 'calibDB', '')
    p = check_set_default_val(p, 'DRS_CALIB_DB', tmp, func_name)

    # check whether we have a drs_config key
    tmp = os.path.join(p['DRS_ROOT'], 'config', '')
    p = check_set_default_val(p, 'DRS_CONFIG', tmp, func_name)

    # check whether we have a drs_man key
    tmp = os.path.join(p['DRS_ROOT'], 'man', '')
    p = check_set_default_val(p, 'DRS_MAN', tmp, func_name)

    # check that drs_log exists else set to 1
    # cparams['DRS_LOG'] = cparams.get('DRS_LOG', 1)

    # check that drs_plot exists else set to 'NONE'
    p = check_set_default_val(p, 'DRS_PLOT', 'undefined', func_name)

    # check whether we have a drs_config key
    p = check_set_default_val(p, 'DRS_DATA_WORKING', None, func_name)

    # check that drs_used_date exists else set to 'undefined'
    p = check_set_default_val(p, 'DRS_USED_DATE', 'undefined', func_name)

    # check that drs_debug exists else set to 0
    p = check_set_default_val(p, 'DRS_DEBUG', 0, func_name)

    # check that drs_interactive set else set to 0
    p = check_set_default_val(p, 'DRS_INTERACTIVE', 0, func_name)

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p = check_set_default_val(p, 'PRINT_LEVEL', 'all', func_name)
    if p['PRINT_LEVEL'] not in loglevels:
        p['PRINT_LEVEL'] = 'all'
        p = check_set_default_val(p, 'PRINT_LEVEL', 'all', func_name)

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p = check_set_default_val(p, 'LOG_LEVEL', 'all', func_name)
    if p['LOG_LEVEL'] not in loglevels:
        p['LOG_LEVEL'] = 'all'
        p = check_set_default_val(p, 'LOG_LEVEL', 'all', func_name)
    # return parameters
    return p


# =============================================================================
#    Worker functions
# =============================================================================
def get_default_config_file():
    """
    Get default config file defined in CONFIG_FILE at relative path
    CONFIGFOLDER from PACKAGE

    :return config_file: string, the path and filename of the default config
                         file
    """
    func_name = __NAME__ + '.get_default_config_file()'
    # Get the config file path
    cargs = [PACKAGE, CONFIGFOLDER, CONFIG_FILE]
    config_file = spirouConfigFile.get_default_config_file(*cargs)
    # make sure config file exists
    if not os.path.exists(config_file):
        emsg1 = "Config file doesn't exists at {0}".format(config_file)
        emsg2 = '   function = {0}'.format(func_name)
        raise ConfigError([emsg1, emsg2], level='error')
    # return the config file path
    return config_file


def check_set_default_val(p, key, dvalue, source=None):
    """
    Function to set the source of "key" if the value in "key" is equal
    to the dvalue (only for use, multiple times, in spirouConfig.check_params())

    :param p: parameter dictionary, parameter dictionary containing constants
    :param key: string, the key to check
    :param dvalue: object, the default value of the key to check
    :param source: string, the source location of the parameter if defaulted

    :return p: parameter dictionary, the updated parameter dictionary
    """
    if key not in p:
        p[key] = dvalue
        p.set_source(key, source)
    return p


# =============================================================================
# End of code
# =============================================================================
