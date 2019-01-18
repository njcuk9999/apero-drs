#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""

from .core import param_functions
from .core import constant_functions
from .default import pseudo_const

# =============================================================================
# Define variables
# =============================================================================
# define name of script
__NAME__ = 'constants.__init__.py'
# define all functions
__all__ = ['load', 'ParamDict', 'ConfigError', 'ConfigWarning', 'gen_all']
# get non-instrument constants (highest level)
TopConstants = param_functions.load_config()
# get non-instrument psuedo constants (highest level)
TopPseudoConstants = param_functions.load_pconfig()
# Get Colours Class
Colors = pseudo_const.Colors

# =============================================================================
# Define functions
# =============================================================================
# load a config file (based on instrument)
#    Errors returned via ConfigError (must be handled
load = param_functions.load_config

# load the pseudo constants (based on instrument)
pload = param_functions.load_pconfig

# param dict
ParamDict = param_functions.ParamDict

# config error
ConfigError = param_functions.ConfigError

# config warning
ConfigWarning = param_functions.ConfigWarning

# helper function
gen_all = param_functions.get_config_all


# =============================================================================
# End of code
# =============================================================================
