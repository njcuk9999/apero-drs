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
__PACKAGE__ = 'startup'
__CONFIG_FILE__ = 'config.txt'
# -----------------------------------------------------------------------------



# =============================================================================
# Define functions
# =============================================================================
def read_config_file(config_file=None):
    # TODO: store user config in /home/$USER/.spirou_config
    # TODO: This will avoid having to rewrite config for every update
    # TODO: Read default parameters and then add "user parameters" to them

    if config_file is None:
        # get config file path
        config_file = pkg_resources.resource_filename(__PACKAGE__,
                                                      __CONFIG_FILE__)
    # make sure config file exists
    if not os.path.exists(config_file):
        raise IOError("Config file doesn't exists at {0}".format(config_file))
    # get keys and values from config file
    keys, values = gettxt(config_file)
    # convert key value pairs into dictionary
    # TODO: use default parameters to check format/range etc for config
    # TODO: return error if user defined config file is wrong
    params = dict(zip(keys, values))
    # return dictionary
    return params


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


def config_error(key):
    # get config file path
    config_file = pkg_resources.resource_filename(__PACKAGE__, __CONFIG_FILE__)
    # construct new error message
    emsg = 'key "{0}" must be defined in config file (located at {1})'
    # return error message
    return emsg.format(key, config_file)


def check_config(params, keys):
    # make sure we have a list
    if type(keys) == str:
        keys = [keys]
    elif hasattr(keys, '__len__'):
        pass
    else:
        raise ValueError("Key(s) must be string or list of strings")
    # loop around each key and check if it exists
    for key in keys:
        if key not in params:
            # if there is an error return error message
            return config_error(key)
    # if everything fine return None
    return None


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
