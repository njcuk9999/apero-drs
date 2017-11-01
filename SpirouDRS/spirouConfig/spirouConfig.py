#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-11 at 13:09

@author: cook



Version 0.0.0
"""

import numpy as np
import os
import pkg_resources

# =============================================================================
# Define variables
# =============================================================================
# Module package name
__PACKAGE__ = 'SpirouDRS'
# Program name
__NAME__ = 'spirouConfig.py'
# Name of main config folder (relative to package level)
__CONFIGFOLDER__ = '../config'
# Name of main config file
__CONFIG_FILE__ = 'config.txt'
# -----------------------------------------------------------------------------
# Whether to use plt.ion (if True) or to use plt.show (if False)
INTERACTIVE_PLOTS = True
# The trigger character to display for each
TRIG_KEY = dict(all=' ', error='!', warning='@', info='*', graph='~')
# The write level
WRITE_LEVEL = dict(error=3, warning=2, info=1, graph=0, all=0)
# The exit style (on log exit)
#  if 'sys' exits via sys.exit   - soft exit (ipython Exception)
#  if 'os' exits via os._exit    - hard exit (complete exit)
EXIT = 'sys'


# =============================================================================
# Define Custom classes
# =============================================================================
class ConfigException(Exception):
    """Raised when config file is incorrect"""
    pass


class ConfigError(ConfigException):
    """
    Custom Config Error for passing to the log
    """
    def __init__(self, message, key=None, config_file=None, level=None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: string, the message to print in the error (if key=None)
        :param key: string or None, the key that caused this error or None
        :param config_file: string or None, the source of the key it came from
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        """
        # set logging level
        if level is None:
            self.level = 'error'
        elif level in TRIG_KEY.keys():
            self.level = level
        else:
            self.level = 'error'
        # get config file path
        if config_file is None:
            config_file = get_default_config_file()
        if key is None and self.level == 'error':
            self.message = 'Config Error: ' + message
        elif key is None:
            self.message = message
        elif key is not None:
            emsg = 'key "{0}" must be defined in config file (located at {1})'
            self.message = emsg.format(key, config_file)
        else:
            emsg = 'There was a problem with the config file (located at {1})'
            self.message = emsg.format(config_file)


class ParamDict(dict):
    """
    Custom dictionary to retain source of a parameter (added via setSource,
    retreived via getSource)
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

    def get(self, key, default=None):
        if key in self.keys():
            return self.__getitem__(key)
        else:
            self.sources[key] = None
            return default

    def set_source(self, key, source):
        """
        Set a key to have sources[key] = source

        raises a ConfigError if key not found

        :param key: string, the main dictionary string
        :param source: string, the source to set
        :return:
        """
        # only add if key is in main dictionary
        if key in self.keys():
            self.sources[key] = source
        else:
            emsg = ('Source cannot be added for key {0} '
                    '[Not in parmeter dictionary]')
            raise ConfigError(emsg.format(key), level='error')

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
        :return:
        """
        # loop around each key in keys
        for k_it in range(len(keys)):
            # assign the key from k_it
            key = keys[k_it]
            # Get soure for this iteration
            if type(sources) == list:
                source = sources[k_it]
            elif type(sources) == dict:
                source = sources[key]
            else:
                source = str(sources)
            # only add if key is in main dictionary
            if key in self.keys():
                self.sources[key] = source
            else:
                emsg = ('Source cannot be added for key {0} '
                        '[Not in parmeter dictionary]')
                raise ConfigError(emsg.format(key), level='error')

    def set_all_sources(self, source):
        """
        Set all keys in dictionary to this source

        :param source: string, all keys will be set to this source
        :return:
        """
        # loop around each key in keys
        for key in self.keys():
            # set key
            self.sources[key] = source

    def get_source(self, key):
        """
        Get a source from the parameter dictionary (must be set)

        raises a ConfigError if key not found

        :param key: string, the key to find (must be set)

        :return source: string, the source of the parameter
        """
        if key in self.keys() and key in self.sources.keys():
            source = self.sources[key]
        else:
            emsg = ('No source set for key={0}')
            raise ConfigError(emsg.format(key), level='error')
        return source

    def source_values(self):
        """
        Get a list of sources for this parameter dictionary
        order the same as self.keys()

        :return sources: list, source values in self.keys() order
        """
        return list(self.sources.values())


# =============================================================================
#   Read/Write Functions
# =============================================================================
def read_config_file(config_file=None):
    # TODO: store user config in /home/$USER/.spirou_config
    # TODO: This will avoid having to rewrite config for every update
    # TODO: Read default parameters and then add "user parameters" to them
    if config_file is None:
        # get config file path
        config_file = get_default_config_file()
    # get keys and values from config file
    keys, values = gettxt(config_file)
    # convert key value pairs into dictionary
    # TODO: use default parameters to check format/range etc for config
    # TODO: return error if user defined config file is wrong
    params = ParamDict(zip(keys, values))
    # Set the source
    params.set_sources(keys=keys, sources=config_file)
    # return dictionary
    return params


def load_config_from_file(p, key, required=False, logthis=False):
    # Check that key  exists in config file
    check_config(p, key)
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
                                  config_file=filename, level='warning')
            # Write key
            p[newkey] = newparams[newkey]
            # set the source of new parameter
            p.set_source(newkey, source=filename)
        # log output
        if logthis:
            emsg = '{0} loaded from: {1}'.format(key, filename)
            raise ConfigError(emsg, config_file=filename, level='all')
    else:
        if required:
            # log error
            emsg = 'Config file: {0} not found'.format(filename)
            raise ConfigError(emsg, config_file=filename, level='error')
    # return p
    return p


def gettxt(filename):
    """
    read config file and convert to key, value pairs
        comments have a '#' at the start
        format of variables:   key = value

    :param filename:
    :return keys: list of strings, upper case strings for each variable
    :return values: list of strings, value of each key
    """
    # read raw config file as strings
    raw = np.genfromtxt(filename, comments="#", delimiter='=',
                        dtype=str).astype(str)
    # check that we have open config file correctly
    try:
        lraw = len(raw)
    except TypeError:
        return [], []
    # loop around each variable (key and value pairs)
    keys, values = [], []
    for row in range(lraw):
        # remove whitespaces and quotation marks from start/end
        key = raw[row, 0].strip().strip("'").strip('"')
        value = raw[row, 1].strip().strip("'").strip('"')
        # add key.upper() to keys
        keys.append(key.upper())
        # add value to values
        values.append(evaluate_value(value))
    # return keys and values
    return keys, values


# =============================================================================
#    Checking functions
# =============================================================================

def check_config(params, keys):
    """
    Check whether we have certain keys in dictionary

    :param params: dictionary
    :param keys: string or list of strings
    :return:
    """
    # get config file path
    # config_file = get_default_config_file()
    # make sure we have a list
    if type(keys) == str:
        keys = [keys]
    elif hasattr(keys, '__len__'):
        pass
    else:
        raise ConfigError("Key(s) must be string or list of strings",
                          level='error')
    # loop around each key and check if it exists
    for key in keys:
        if key not in params:
            # if there is an error return error message
            emsg = 'key "{0}" must be defined in a config file'
            # return error message
            raise ConfigError(emsg.format(key), level='error')


def check_params(p):
    """
    Check the parameter dictionary has certain required values

    :param p: dictionary, parameter dictionary
    :return p: dictionary, the updated parameter dictionary
    """
    # get log levels
    loglevels = list(TRIG_KEY.keys())
    # check that the drs_root and tdata variables are named
    check_config(p, ['DRS_ROOT', 'TDATA'])
    # check whether we have drs_data_raw key
    tmp = os.path.join(p['TDATA'], 'raw', '')
    p['DRS_DATA_RAW'] = p.get('DRS_DATA_RAW', tmp)
    p = set_source_for_defaulting_statements(p, 'DRS_DATA_RAW', tmp)

    # check whether we have drs_data_reduc key
    tmp = os.path.join(p['TDATA'], 'reduced', '')
    p['DRS_DATA_REDUC'] = p.get('DRS_DATA_REDUC', tmp)
    p = set_source_for_defaulting_statements(p, 'DRS_DATA_REDUC', tmp)

    # check whether we have drs_data_msg key
    tmp = os.path.join(p['TDATA'], 'msg', '')
    p['DRS_DATA_MSG'] = p.get('DRS_DATA_MSG', tmp)
    p = set_source_for_defaulting_statements(p, 'DRS_DATA_MSG', tmp)

    # check whether we have drs_calib_db key
    tmp = os.path.join(p['TDATA'], 'calibDB', '')
    p['DRS_CALIB_DB'] = p.get('DRS_CALIB_DB', tmp)
    p = set_source_for_defaulting_statements(p, 'DRS_CALIB_DB', tmp)

    # check whether we have a drs_config key
    tmp = os.path.join(p['DRS_ROOT'], 'config', '')
    p['DRS_CONFIG'] = p.get('DRS_CONFIG', tmp)
    p = set_source_for_defaulting_statements(p, 'DRS_CONFIG', tmp)

    # check whether we have a drs_man key
    tmp = os.path.join(p['DRS_ROOT'], 'man', '')
    p['DRS_MAN'] = p.get('DRS_MAN', tmp)
    p = set_source_for_defaulting_statements(p, 'DRS_MAN', tmp)

    # check that drs_log exists else set to 1
    # cparams['DRS_LOG'] = cparams.get('DRS_LOG', 1)

    # check that drs_plot exists else set to 'NONE'
    p['DRS_PLOT'] = p.get('DRS_PLOT', 'undefined')
    p = set_source_for_defaulting_statements(p, 'DRS_PLOT', 'undefined')

    # check whether we have a drs_config key
    p['DRS_DATA_WORKING'] = p.get('DRS_DATA_WORKING', None)
    p = set_source_for_defaulting_statements(p, 'DRS_DATA_WORKING', None)

    # check that drs_used_date exists else set to 'undefined'
    p['DRS_USED_DATE'] = p.get('DRS_USED_DATE', 'undefined')
    p = set_source_for_defaulting_statements(p, 'DRS_USED_DATE', 'undefined')

    # check that drs_debug exists else set to 0
    p['DRS_DEBUG'] = p.get('DRS_DEBUG', 0)
    p = set_source_for_defaulting_statements(p, 'DRS_DEBUG', 0)

    # check that drs_interactive set else set to 0
    p['DRS_INTERACTIVE'] = p.get('DRS_INTERACTIVE', 0)
    p = set_source_for_defaulting_statements(p, 'DRS_INTERACTIVE', 0)

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p['PRINT_LEVEL'] = p.get('PRINT_LEVEL', 'all')
    p = set_source_for_defaulting_statements(p, 'PRINT_LEVEL', 'all')
    if p['PRINT_LEVEL'] not in loglevels:
        p['PRINT_LEVEL'] = 'all'
        p = set_source_for_defaulting_statements(p, 'PRINT_LEVEL', 'all')

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p['LOG_LEVEL'] = p.get('LOG_LEVEL', 'all')
    p = set_source_for_defaulting_statements(p, 'LOG_LEVEL', 'all')
    if p['LOG_LEVEL'] not in loglevels:
        p['LOG_LEVEL'] = 'all'
        p = set_source_for_defaulting_statements(p, 'LOG_LEVEL', 'all')
    # return parameters
    return p


# =============================================================================
#    Worker functions
# =============================================================================
def evaluate_value(value):
    """
    Takes a value and tries to interpret it as an INT/FLOAT/BOOL etc
    any strings will throw a NameError and thus be returned as a string

    :param value: string, any string value to be interpreted by python

    :return: object, if eval(value) works returns properly formated object
             else returns the value as a string
    """
    try:
        newvalue = eval(value)
        if type(newvalue) not in [int, float, bool, complex]:
            return value
        else:
            return newvalue
    except Exception:
        return value


def get_default_config_file():
    """
    Get default config file defined in __CONFIG_FILE__ at relative path
    __CONFIGFOLDER__ from __PACKAGE__

    :return config_file: string, the path and filename of the default config
                         file
    """
    init = pkg_resources.resource_filename(__PACKAGE__, '__init__.py')
    # Get the config_folder from relative path
    current = os.getcwd()
    os.chdir(os.path.dirname(init))
    config_folder = os.path.abspath(__CONFIGFOLDER__)
    os.chdir(current)
    # Get the config file path
    config_file = os.path.join(config_folder, __CONFIG_FILE__)
    # make sure config file exists
    if not os.path.exists(config_file):
        emsg = "Config file doesn't exists at {0}".format(config_file)
        raise ConfigError(emsg, config_file=config_file, level='error')
    # return the config file path
    return config_file


def set_source_for_defaulting_statements(p, key, dvalue):
    if p[key] == dvalue:
        p.set_source(key, __NAME__ + '/check_params()')
    return p

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
