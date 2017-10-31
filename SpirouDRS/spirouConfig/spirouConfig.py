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
# Name of main config folder (relative to package level)
__CONFIGFOLDER__ = '../config'
# Name of main config file
__CONFIG_FILE__ = 'config.txt'
# -----------------------------------------------------------------------------
# The trigger character to display for each
TRIG_KEY = dict(all=' ', error='!', warning='@', info='*', graph='~')
# The write level
WRITE_LEVEL = dict(error=3, warning=2, info=1, graph=0, all=0)
# The exit style (on log exit)
#  if 'sys' exits via sys.exit   - soft exit (ipython Exception)
#  if 'os' exits via os._exit    - hard exit (complete exit)
EXIT = 'sys'


# =============================================================================
# Define functions
# =============================================================================
class ConfigException(Exception):
    """Raised when config file is incorrect"""
    pass


class ConfigError(ConfigException):
    """
    Custom Config Error for passing to the log
    """
    def __init__(self, message, key=None, config_file=None, level=None):

        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level

        # get config file path
        if config_file is None:
            config_file = get_default_config_file()
        if key is None:
            self.message = 'Config Error: ' + message
        elif key is not None:
            emsg = 'key "{0}" must be defined in config file (located at {1})'
            self.message = emsg.format(key, config_file)
        else:
            emsg = 'There was a problem with the config file (located at {1})'
            self.message = emsg.format(config_file)


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
    params = dict(zip(keys, values))
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
        # log output
        if logthis:
            emsg = '{0} loaded from: {1}'.format(key, filename)
            raise ConfigError(emsg, config_file=filename, level='')
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

    # check whether we have drs_data_reduc key
    tmp = os.path.join(p['TDATA'], 'reduced', '')
    p['DRS_DATA_REDUC'] = p.get('DRS_DATA_REDUC', tmp)

    # check whether we have drs_data_msg key
    tmp = os.path.join(p['TDATA'], 'msg', '')
    p['DRS_DATA_MSG'] = p.get('DRS_DATA_MSG', tmp)

    # check whether we have drs_calib_db key
    tmp = os.path.join(p['TDATA'], 'calibDB', '')
    p['DRS_CALIB_DB'] = p.get('DRS_CALIB_DB', tmp)

    # check whether we have a drs_config key
    tmp = os.path.join(p['DRS_ROOT'], 'config', '')
    p['DRS_CONFIG'] = p.get('DRS_CONFIG', tmp)

    # check whether we have a drs_man key
    tmp = os.path.join(p['DRS_ROOT'], 'man', '')
    p['DRS_MAN'] = p.get('DRS_MAN', tmp)

    # check that drs_log exists else set to 1
    # cparams['DRS_LOG'] = cparams.get('DRS_LOG', 1)

    # check that drs_plot exists else set to 'NONE'
    p['DRS_PLOT'] = p.get('DRS_PLOT', 'undefined')

    # check whether we have a drs_config key
    p['DRS_DATA_WORKING'] = p.get('DRS_DATA_WORKING', None)

    # check that drs_used_date exists else set to 'undefined'
    p['DRS_USED_DATE'] = p.get('DRS_USED_DATE', 'undefined')

    # check that drs_debug exists else set to 0
    p['DRS_DEBUG'] = p.get('DRS_DEBUG', 0)

    # check that drs_interactive set else set to 0
    p['DRS_INTERACTIVE'] = p.get('DRS_INTERACTIVE', 0)

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p['PRINT_LEVEL'] = p.get('PRINT_LEVEL', 'all')
    if p['PRINT_LEVEL'] not in loglevels:
        p['PRINT_LEVEL'] = 'all'

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p['LOG_LEVEL'] = p.get('LOG_LEVEL', 'all')
    if p['LOG_LEVEL'] not in loglevels:
        p['LOG_LEVEL'] = 'all'
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
