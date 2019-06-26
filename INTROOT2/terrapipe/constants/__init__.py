#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""

from . import constant_functions, param_functions

# =============================================================================
# Define variables
# =============================================================================
# define name of script
__NAME__ = 'constants.__init__.py'
# define all functions
__all__ = ['load', 'ParamDict', 'ArgumentError', 'ConfigError',
           'ConfigWarning', 'gen_all']
# get non-instrument constants (highest level)
TopConstants = param_functions.load_config()
# get non-instrument psuedo constants (highest level)
TopPseudoConstants = param_functions.load_pconfig()

# =============================================================================
# Define functions
# =============================================================================
# load a config file (based on instrument)
#    Errors returned via ConfigError (must be handled
load = param_functions.load_config

# load the pseudo constants (based on instrument)
pload = param_functions.load_pconfig

# get module names
getmodnames = param_functions.get_module_names

# import modules
import_module = constant_functions.import_module

# get file names
get_filenames = param_functions.get_file_names

# param dict
ParamDict = param_functions.ParamDict

# argument error
ArgumentError = param_functions.ArgumentError

# config error
ConfigError = param_functions.ConfigError

# config warning
ConfigWarning = param_functions.ConfigWarning

# helper function
gen_all = param_functions.get_config_all


# =============================================================================
# End of code
# =============================================================================
