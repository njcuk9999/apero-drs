#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-01-10 at 11:38

@author: cook

Import rules: No imports from SpirouDRS
"""
from __future__ import division
import numpy as np
import os
import pkg_resources


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouConfigFile.py'
# Get version and author
__version__ = 'Unknown'
__author__ = 'Unknown'
__release__ = 'Unknown'
__date__ = 'Unknown'
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def read_config_file(package, configfolder, configfile, config_file=None,
                     return_raw=True):
    if config_file is None:
        # get config file path
        config_file = get_default_config_file(package, configfolder,
                                              configfile)
    # get keys and values from config file
    keys, values = gettxt(config_file)
    # return keys and values if return_raw
    if return_raw:
        return keys, values
    else:
        return dict(zip(keys, values))


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


def get_default_config_file(package, configfolder, config_file):
    """
    Get default config file defined in __CONFIG_FILE__ at relative path
    __CONFIGFOLDER__ from __PACKAGE__

    :return config_file: string, the path and filename of the default config
                         file
    """
    init = pkg_resources.resource_filename(package, '__init__.py')
    # Get the config_folder from relative path
    current = os.getcwd()
    os.chdir(os.path.dirname(init))
    config_folder = os.path.abspath(configfolder)
    os.chdir(current)
    # Get the config file path
    config_file = os.path.join(config_folder, config_file)
    # return the config file path
    return config_file


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
        if type(newvalue) not in [int, float, bool, complex, list, dict]:
            return value
        else:
            return newvalue
    except Exception:
        return str(value)


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
