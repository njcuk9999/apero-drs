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
from . import spirouConst as Constants

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

# Load a config file from given filename
LoadConfigFromFile = spirouConfig.load_config_from_file

# Custom dictionary class - parameter dictionary
ParamDict = spirouConfig.ParamDict

# Reads the config file and loads all variables into dictionary
ReadConfigFile = spirouConfig.read_config_file