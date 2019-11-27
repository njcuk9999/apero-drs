#!/usr/bin/env python
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
__all__ = ['Constants',
           'ConfigError',
           'CheckCparams',
           'CheckConfig',
           'ExtractDictParams',
           'GetKeywordArguments',
           'GetKeywordValues',
           'GetAbsFolderPath',
           'GetDefaultConfigFile',
           'LoadConfigFromFile',
           'ParamDict',
           'ReadConfigFile']

# =============================================================================
# Function aliases
# =============================================================================
# Custom config exception
ConfigError = spirouConfig.ConfigError

CheckCparams = spirouConfig.check_params

CheckConfig = spirouConfig.check_config

ExtractDictParams = spirouConfig.extract_dict_params

GetTxt = spirouConfigFile.get_raw_txt

GetConfigParams = spirouConfig.get_config_params

GetKeywordArguments = spirouKeywords.get_keywords

GetKeywordValues = spirouKeywords.get_keyword_values_from_header

GetAbsFolderPath = spirouConfigFile.get_relative_folder

GetDefaultConfigFile = spirouConfigFile.get_default_config_file

LoadConfigFromFile = spirouConfig.load_config_from_file

ParamDict = spirouConfig.ParamDict

ReadConfigFile = spirouConfig.read_config_file


# =============================================================================
# End of code
# =============================================================================
