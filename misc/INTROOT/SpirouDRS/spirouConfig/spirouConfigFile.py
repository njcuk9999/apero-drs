#!/usr/bin/env python
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
import string
import pkg_resources
import warnings

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
VALID_CHARS = list(string.ascii_letters) + list(string.digits)
VALID_CHARS += list(string.punctuation) + list(string.whitespace)


# =============================================================================
# Define Custom classes
# =============================================================================
class ConfigException(Exception):
    """Raised when config file is incorrect"""
    pass


# =============================================================================
# Define functions
# =============================================================================
def read_config_file(package=None, configfolder=None, configfile=None,
                     config_file=None, return_raw=True, return_filename=False):
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

    :param return_filename: bool, if True only returns the filename (string)

    if return_filename:
        :return config_file: string, filename
    elif return_raw:
        :return keys: list of strings, the keys for each value
        :return values: list of objects matched to each key
    else:
        :return dictionary: dictionary, the key value pairs in a dictionary
    """
    if config_file is None:
        # get config file path
        config_file = get_default_config_file(package, configfolder,
                                              configfile)
    if return_filename:
        return config_file
    # get keys and values from config file
    keys, values = gettxt(config_file)
    # return keys and values if return_raw
    if return_raw:
        return keys, values
    else:
        return dict(zip(keys, values))


def get_user_config(p, package, configfolder, configfile):
    """
    Deal with the user defining a config file.

    User config file overwrites default file and can be defined in two places:

    - DRS_UCONFIG in the default (primary) config.py file
    - DRS_UCONFIG in the environmental variables

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:

    :param package: string, the DRS package (to get the absolute path)

    :param configfolder: string, the relative path of the config file relative
                         to the package path

    :param configfile: string, the name of the config file to look for

    :return p: parameter dictionary, ParamDict containing constants
        Updated with all keys from user config file (if set and found)
    :return warn_msgs: list, a list of warning messages to pipe to the logger
    """
    func_name = __NAME__ + '.get_user_config()'
    # set configfolder, defined location and warning messages
    defined_in = None
    warn_msgs = []

    if not p['USER_CONFIG']:
        return p, warn_msgs

    # set default config file (re-retrieve from package name etc)
    ckwargs = dict(package=package, configfolder=configfolder,
                   configfile=configfile, config_file=None,
                   return_filename=True)
    d_config_file = read_config_file(**ckwargs)

    # get DRS_CONFIG from environmental variables
    if 'DRS_UCONFIG' in os.environ:
        # set path
        rawpath = os.environ['DRS_UCONFIG']
        # check for relative paths in config folder
        rawpath = check_for_rel_paths(rawpath)
        # check that path exists
        if os.path.exists(rawpath):
            configfolder = str(rawpath)
            defined_in = 'environmental variables'
            p['DRS_UCONFIG'] = str(rawpath)
            if type(p) is not dict:
                p.set_source('DRS_UCONFIG', 'ENVIRONMENTAL VARIABLES')
            # reset warn messages (not needed)
        # deal with DRS_UCONFIG being set but not being found
        else:
            warn_msgs.append('Directory DRS_UCONFIG={0} does not '
                             'exist'.format(rawpath))
            warn_msgs.append('    but USER_CONFIG=1 and the user config '
                             'folder is set')
            warn_msgs.append('    in {0}'.format('the ENVIRONMENTAL VARIABLES'))
            warn_msgs.append('    User config file will not be used.')
    # get DRS_UCONFIG from default config file
    #    This needs to be done again in case the path supplied in the
    #    environmental variable "DRS_UCONFIG" did not exist
    if 'DRS_UCONFIG' in p:
        # set path
        rawpath = str(p['DRS_UCONFIG'])
        # check for relative paths in config folder
        rawpath = check_for_rel_paths(rawpath)
        # check that path exists
        if os.path.exists(rawpath):
            configfolder = str(rawpath)
            defined_in = d_config_file
            p['DRS_UCONFIG'] = str(rawpath)
            if type(p) is not dict:
                p.set_source('DRS_UCONFIG', func_name)
            warn_msgs = []
        # deal with DRS_UCONFIG being set but not being found
        else:
            warn_msgs.append('Directory DRS_UCONFIG={0} does not '
                             'exist'.format(rawpath))
            warn_msgs.append('    but USER_CONFIG=1 and the user config '
                             'folder is set')
            warn_msgs.append('    in {0}'.format(d_config_file))
            warn_msgs.append('    User config file will not be used.')
            warn_msgs.append('    Using primary config.py only')

    # if we don't have a user
    if configfolder is None:
        warn_msgs.append('USER_CONFIG=1 but no configuration directory set')
        warn_msgs.append('    Please set in primary config file or as an '
                         'environmental variable (DRS_UCONFIG)')
        warn_msgs.append('    User config file will not be used.')
        warn_msgs.append('    Using primary config.py only')
        return p, warn_msgs

    # construct new path
    configfile = os.path.join(configfolder, configfile)
    # check config file exists here
    if os.path.exists(configfile):
        # get the values in this config file
        keys, values = read_config_file(config_file=configfile)
        # loop around keys and add them to dictionary
        for key, value in zip(keys, values):
            if key not in ['USER_CONFIG', 'DRS_UCONFIG']:
                p[key] = value
                if type(p) is not dict:
                    p.set_source(key, configfile)
    else:
        warn_msgs.append('User config file {0} does not '
                         'exist'.format(configfile))
        warn_msgs.append('    but USER_CONFIG=1 and the user config '
                         'folder is set')
        warn_msgs.append('    in {0}'.format(defined_in))
        warn_msgs.append('    Either add user config file to {0}'
                         ''.format(configfile))
        warn_msgs.append('    Or remove DRS_UCONFIG from {0}'
                         ''.format(defined_in))
        warn_msgs.append('    User config file will not be used.')
        warn_msgs.append('    Using primary config.py only')

    # return parameters
    return p, warn_msgs


def check_for_rel_paths(path):
    """
    Checks for ~ and $HOME paths and

    :param path: string, the path to check

    :return: string, the path with the full path (using HOME environmental key)
    """
    # get home directory
    home = os.environ.get('HOME')
    if home is None:
        return path
    # check for ~ at start (i.e. home dir)
    if path.startswith('~/'):
        path = os.path.join(home, path[2:])
    # check for $HOME at start
    if path.startswith('$HOME/'):
        path = os.path.join(home, path[6:])
    # finally return path
    return path


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
    # first try to reformat text file to avoid weird characters
    #   (like mac smart quotes)
    validate_text_file(filename)
    # read raw config file as strings
    raw = get_raw_txt(filename, comments='#', delimiter='=')
    # check that we have lines in config file
    if len(raw) == 0:
        return [], []
    elif len(raw.shape) == 1:
        single = True
    else:
        single = False
    # check that we have opened config file correctly
    try:
        # check how many rows we have
        lraw = raw.shape[0]
    except TypeError:
        return [], []
    # loop around each variable (key and value pairs)
    if single:
        key = raw[0].strip().strip("'").strip('"')
        value = raw[1].strip().strip("'").strip('"')
        keys = [key]
        values = [evaluate_value(value)]
    else:
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


def get_raw_txt(filename, comments, delimiter):
    with warnings.catch_warnings(record=True) as _:
        # noinspection PyBroadException
        try:
            raw = np.genfromtxt(filename, comments=comments,
                                delimiter=delimiter, dtype=str).astype(str)
        except Exception:
            raw = read_lines(filename, comments=comments, delimiter=delimiter)
    # return the raw lines
    return raw


def validate_text_file(filename, comments='#'):
    """
    Validation on any text file, makes sure all non commented lines have
    valid characters (i.e. are either letters, digits, punctuation or
    whitespaces as defined by string.ascii_letters, string.digits,
    string.punctuation and string.whitespace.

    A ConfigException is raised if invalid character(s) found

    :param filename: string, name and location of the text file to open
    :param comments: char (string), the character that defines a comment line
    :return None:
    """
    func_name = __NAME__ + '.validate_text_file()'
    # open text file
    f = open(filename, 'r')
    # get lines
    lines = f.readlines()
    # close text file
    f.close()
    # loop around each line in text file
    for l, line in enumerate(lines):
        # ignore blank lines
        if len(line.strip()) == 0:
            continue
        # ignore comment lines (don't care about characters in comments)
        if line.strip()[0] == comments:
            continue
        # loop through each character in line and check if it is a valid
        # character
        emsg = ' Invalid character(s) found in file={0}'.format(filename)
        invalid = False
        for char in line:
            if char not in VALID_CHARS:
                invalid = True
                emsg += '\n\t\tLine {1} character={0}'.format(char, l + 1)
        emsg += '\n\n\tfunction = {0}'.format(func_name)
        # only raise an error if invalid is True (if we found bad characters)
        if invalid:
            raise ConfigException(emsg)


def read_lines(filename, comments='#', delimiter=' '):
    """

    :param filename:
    :param comments:
    :param delimiter:
    :return:
    """

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
        elif line[0] == comments:
            continue
        else:
            # append to raw
            try:
                key, value = line.split(delimiter)
            except ValueError as _:
                emsg = ('\n\t\t Wrong format for line {0} in file {1}'
                        '\n\t\t Lines must be "key" = "value"'
                        '\n\t\t Where "key" and "value" are a valid python '
                        'strings and contains no equal signs')
                raise ConfigException(emsg.format(l + 1, filename, line))

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
    # noinspection PyBroadException
    try:
        newvalue = eval(value)
        if type(newvalue) not in [int, float, bool, complex, list, dict]:
            return value
        else:
            return newvalue
    except Exception:
        return str(value)


def get_tags(package, relfolder, filename):
    # get the directory
    directory = get_relative_folder(package, relfolder)
    # get the abs path
    abspath = os.path.join(directory, filename)
    # get keys and values from filename
    keys, values = gettxt(abspath)
    # strip all whitespace from variables
    nkeys, nvalues = [], []
    for it in range(len(keys)):
        key, value = str(keys[it]), str(values[it])
        nkeys.append(key.strip())
        nvalues.append(value.strip())
    # make into dictionary
    tags = dict(zip(nkeys, nvalues))
    # return tags
    return tags

# =============================================================================
# End of code
# =============================================================================
