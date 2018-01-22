#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-31 at 12:12

@author: cook



Version 0.0.0
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
           'LoadConfigFromFile',
           'ParamDict',
           'ReadConfigFile']


# =============================================================================
# Function aliases
# =============================================================================
# Custom config exception
ConfigError = spirouConfig.ConfigError

# Check the parameter dictionary has certain required values
CheckCparams = spirouConfig.check_params

# Check whether we have certain keys in dictionary
CheckConfig = spirouConfig.check_config

# Extract dictionary parameters from string (with specific suffix)
ExtractDictParams = spirouConfig.extract_dict_params

# get the keywords from keywords file
GetKeywordArguments = spirouKeywords.get_keywords

# get the keyword values from a header/dictionary
GetKwValues = spirouKeywords.get_keyword_values_from_header

GetAbsFolderPath = spirouConfigFile.get_relative_folder

GetAbsConfigPath = spirouConfigFile.get_relative_folder

# Load a config file from given filename
LoadConfigFromFile = spirouConfig.load_config_from_file

# Custom dictionary class - parameter dictionary
ParamDict = spirouConfig.ParamDict

# Reads the config file and loads all variables into dictionary
ReadConfigFile = spirouConfig.read_config_file

# =============================================================================
# End of code
# =============================================================================
