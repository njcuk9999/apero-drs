#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from apero.core.constants import constant_functions
from apero.core.constants import param_functions

# =============================================================================
# Define variables
# =============================================================================
# define name of script
__NAME__ = 'constants.__init__.py'
# define all functions
__all__ = ['load', 'pload', 'ParamDict', 'ArgumentError', 'ConfigError',
           'ConfigWarning', 'gen_all', 'getmodnames', 'import_module',
           'get_filenames', 'get_relative_folder', 'break_point']

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

get_relative_folder = param_functions.get_relative_folder

# import modules
import_module = constant_functions.import_module

get_constants_from_file = constant_functions.get_constants_from_file

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

# update param dicts
uparamdicts = param_functions.update_paramdicts

update_file = constant_functions.update_file

# generate a drs breakpoint
break_point = param_functions.break_point

catch_sigint = param_functions.catch_sigint


# =============================================================================
# End of code
# =============================================================================
