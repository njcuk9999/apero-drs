#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spirou configuration module (file loading specifics)

Created on 2018-01-10 at 11:38

@author: cook

Import rules: No imports from SpirouDRS
"""
from __future__ import division
import numpy as np
import os
import pkg_resources
import sys

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
# Define Custom classes
# =============================================================================
class ConfigException(Exception):
    """Raised when config file is incorrect"""
    pass


# =============================================================================
# Define functions
# =============================================================================
def read_config_file(package, configfolder, configfile, config_file=None,
                     return_raw=True):
    """
    Read a configruation file called "configfile" at relative path
    "configfolder" (relative to "package" path)

            i.e. if package is X  is located at /home/bin/packageX
            and the config file is located at /home/bin/packageX/config/Y.txt

            then package = "packageX"
                 configfolder = "./config/"
                 configfile = "Y.txt"

    Note the config file should be in the following format:

                # BEGINNING OF CONFIG FILE

                # Comment
                key1 = value1
                key2 = value2

                # Comment
                key3 = value3

                # END OF CONFIG FILE

    (i.e. comments start with #, blank lines are ignored and the resulting
     key value pairs would be as follows:

        keys = ['key1', 'key2', 'key3']
        values = ['value1', 'value2', 'value3']

        or if return_raw = False

        {'key1':'value1', 'key2':'value2', 'key3':'value3'}

    :param package: string, python package name
                    i.e. import packageX
                      --> package = "packageX"

    :param configfolder: string, the relative path of the configuration file
                         (relative to the package)

    :param configfile: string, the configuration filename (filename only)

    :param config_file: string or None, if not None then overrides the path
                        created from package/configfolder/configfile and uses
                        "config_file" as the path to read the config file

    :param return_raw: bool, if True returns key and value pairs, if False
                       returns a dictionary of key value pairs
    :return:
    """
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

    If file cannot be read will generate an IOError

    :param filename: string, the filename (+ absolute path) of file to open

    :return keys: list of strings, upper case strings for each variable
    :return values: list of strings, value of each key
    """
    # read raw config file as strings
    try:
        raw = np.genfromtxt(filename, comments="#", delimiter='=',
                            dtype=str).astype(str)
    except Exception:
        raw = read_lines(filename, comments='#', delimiter='=')

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


def read_lines(filename, comments='#', delimiter=' '):

    func_name = __NAME__ + '.read_lines()'
    # manually open file (slow)
    try:
        # open the file
        f = open(filename, 'r')
        # read the lines
        lines = f.readlines()
        # close the opened file
        f.close()
    except Exception as e:
        emsg = ('\n\t\t {0}: File "{1}" cannot be read by {2}. '
                '\n\t\t Error was: {3}')
        raise ConfigException(emsg.format(type(e), filename, func_name, e))
    # valid lines
    raw = []
    # loop around lines
    for l, line in enumerate(lines):
        # remove line endings and blanks at start and end
        line = line.replace('\n', '').strip()
        # do not include blank lines
        if len(line) == 0:
            continue
        # do not include commented lines
        elif line[0] == '#':
            continue
        else:
            # append to raw
            try:
                key, value = line.split(delimiter)
            except ValueError as e:
                emsg = ('\n\t\t Wrong format for line {0} in file {1}'
                        '\n\t\t Lines must be "key" = "value"'
                        '\n\t\t Where "key" and "value" are a valid python '
                        'strings and contains no equal signs')
                raise ConfigException(emsg.format(l+1, filename, line))

            raw.append([key, value])
    # check that raw has entries
    if len(raw) == 0:
        raise ConfigException("No valid lines found in {0}".format(filename))
    # return raw
    return np.array(raw)


def get_relative_folder(package, folder):
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
        raise ConfigException(emsg.format(package, func_name))
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
        raise ConfigException(emsg.format(*eargs))
    # return the absolute data_folder path
    return data_folder


def get_default_config_file(package, configfolder, configfile):
    """
    Get the absolute path for the  default config file defined in
    configfile at relative path configfolder from package

    :param package: string, the python package name
    :param configfolder: string, the relative path of the configuration folder
    :param configfile: string, the name of the configuration file

    :return config_file: string, the absolute path and filename of the
                         default config file
    """
    func_name = __NAME__ + '.get_default_config_file()'
    # get the config folder
    config_folder = get_relative_folder(package, configfolder)
    # Get the config file path
    config_file = os.path.join(config_folder, configfile)
    # test that config file exists
    if not os.path.exists(config_file):
        emsg = 'Config file "{0}" not found at "{1}" (function={2})'
        raise ConfigException(emsg.format(configfile, config_folder, func_name))
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
# End of code
# =============================================================================
