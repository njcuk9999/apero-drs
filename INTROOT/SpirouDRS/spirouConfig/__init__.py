#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialization code for Spirou configuration module

Created on 2017-10-31 at 12:12

@author: cook

"""
from . import spirouConfig
from . import spirouKeywords
from . import spirouConst
from . import spirouConfigFile

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouConfig.__init__()'
# Define alias for constants
Constants = spirouConst
# Get version and author
__version__ = Constants.VERSION()
__author__ = Constants.AUTHORS()
__date__ = Constants.LATEST_EDIT()
__release__ = Constants.RELEASE()
# define imports using asterisk
__all__ = ['ConfigError',
           'CheckCparams',
           'CheckConfig',
           'ExtractDictParams',
           'GetKeywordArguments',
           'GetKwValues',
           'GetAbsFolderPath',
           'GetDefaultConfigFile'
           'LoadConfigFromFile',
           'ParamDict',
           'ReadConfigFile']


# =============================================================================
# Function aliases
# =============================================================================
# Custom config exception
ConfigError = spirouConfig.ConfigError
"""
Custom Config Error for passing to the log

if key is not None defined self.message reads "key [key] must be
defined in config file (located at [config_file]

if config_file is None then deafult config file is used in its place

:param message: string, the message to print in the error (if key=None)
:param key: string or None, the key that caused this error or None
:param config_file: string or None, the source of the key it came from
:param level: string, level (for logging) must be key in TRIG key above
              default = all, error, warning, info or graph
"""

CheckCparams = spirouConfig.check_params
"""
Check the parameter dictionary has certain required values, p must contain
at the very least keys 'DRS_ROOT' and 'TDATA'

:param p: dictionary, parameter dictionary
           (must have at least keys 'DRS_ROOT' and 'TDATA')

:return p: dictionary, the updated parameter dictionary
"""

CheckConfig = spirouConfig.check_config
"""
Check whether we have certain keys in dictionary
raises a Config Error if keys are not in params

:param params: parameter dictionary
:param keys: string or list of strings containing the keys to look for

:return None:
"""

ExtractDictParams = spirouConfig.extract_dict_params
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

# get the keywords from keywords file
GetKeywordArguments = spirouKeywords.get_keywords
"""
Get keywords defined in USE_KEYS from spirouKeywords.py 
(must be named exactly as in USE_KEYS list)

:param pp: parameter dictionary or None, if not None then keywords are added
           to the specified ParamDict else a new ParamDict is created

:return pp: if pp is None returns a new dictionary of keywords
            else adds USE_KEYS as keys with value = eval(key)
"""

# get the keyword values from a header/dictionary
GetKwValues = spirouKeywords.get_keyword_values_from_header
"""
Gets a keyword or keywords from a header or dictionary

:param p: parameter dictionary, the constants parameter dictionary
:param hdict: dictionary, raw dictionary or FITS rec header file containing
              all the keys in "keys" (spirouConfig.ConfigError raised if
              any key does not exist)
:param keys: list of strings or list of lists, the keys to find in "hdict"
             OR a list of keyword lists ([key, value, comment])
:param filename: string or None, if defined when an error is caught the
                 filename is logged, this filename should be where the
                 fits rec header is from (or where the dictionary was
                 compiled from) - if not from a file this should be left
                 as None
                 
:return values: list, the values in the header for the keys
                (size = len(keys))
"""

GetAbsFolderPath = spirouConfigFile.get_relative_folder
"""
Get the absolute path of folder defined at relative path
folder from package

:param package: string, the python package name
:param folder: string, the relative path of the configuration folder

:return data: string, the absolute path and filename of the default config
              file
"""

GetDefaultConfigFile = spirouConfigFile.get_default_config_file
"""
Get the absolute path for the  default config file defined in
configfile at relative path configfolder from package

:param package: string, the python package name
:param configfolder: string, the relative path of the configuration folder
:param configfile: string, the name of the configuration file

:return config_file: string, the absolute path and filename of the
                     default config file
"""

# Load a config file from given filename
LoadConfigFromFile = spirouConfig.load_config_from_file
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

ParamDict = spirouConfig.ParamDict
"""
Custom dictionary to retain source of a parameter (added via setSource,
retreived via getSource). String keys are case insensitive.

calls dict.__init__   i.e. the same as running dict(*arg, *kw)

:param arg: arguments passed to dict
:param kw: keyword arguments passed to dict

"""

ReadConfigFile = spirouConfig.read_config_file
"""
Read config file wrapper (push into ParamDict)

:param config_file: string or None, the config_file name, if none uses
                    PACKAGE/CONFIGFOLDER and CONFIG_FILE to get config
                    file name
:return params: parameter dictionary with key value pairs fron config file
"""


# =============================================================================
# End of code
# =============================================================================
