#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from . import general

__all__ = ['get_blacklist', 'get_whitelist']

# =============================================================================
# Define functions
# =============================================================================
calculate_telluric_absorption = general.calculate_telluric_absorption

get_blacklist = general.get_blacklist

get_whitelist = general.get_whitelist

load_conv_tapas = general.load_conv_tapas

load_templates = general.load_templates

normalise_by_pblaze = general.normalise_by_pblaze

# =============================================================================
# End of code
# =============================================================================
