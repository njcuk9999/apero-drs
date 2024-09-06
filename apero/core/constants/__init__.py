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
from apero.core.constants import load_functions

# =============================================================================
# Define variables
# =============================================================================
# define name of script
__NAME__ = 'constants.__init__.py'
# define all functions
__all__ = ['load', 'pload', 'ParamDict', 'gen_all', 'getmodnames',
           'import_module']

# =============================================================================
# Define functions
# =============================================================================
# load a config file (based on instrument)
#    Errors returned via ConfigError (must be handled
load = load_functions.load_config

# load the pseudo constants (based on instrument)
pload = load_functions.load_pconfig

# load the psuedo constants typing
PseudoConstants = load_functions.select.Instrument

# pchcek
PCheck = param_functions.PCheck

# get module names
getmodnames = param_functions.get_module_names

# import modules
import_module = constant_functions.import_module

get_constants_from_file = constant_functions.get_constants_from_file

# param dict
ParamDict = param_functions.ParamDict

# helper function
gen_all = param_functions.get_config_all

# update param dicts
uparamdicts = param_functions.update_paramdicts

update_file = constant_functions.update_file

# catching Ctrl+C and other code interruptions
catch_sigint = param_functions.catch_sigint


# =============================================================================
# End of code
# =============================================================================
