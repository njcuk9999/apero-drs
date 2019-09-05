#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from . import general

__all__ = ['calculate_telluric_absorption', 'get_blacklist', 'get_whitelist',
           'load_conv_tapas', 'load_templates', 'mk_tellu_quality_control',
           'normalise_by_pblaze']

# =============================================================================
# Define functions
# =============================================================================
calculate_telluric_absorption = general.calculate_telluric_absorption

get_blacklist = general.get_blacklist

get_trans_files = general.get_transmission_files

get_whitelist = general.get_whitelist

load_conv_tapas = general.load_conv_tapas

load_tapas_convolved = general.load_tapas_convolved

load_templates = general.load_templates

mk_tellu_quality_control = general.mk_tellu_quality_control

mk_tellu_write_trans_file = general.mk_tellu_write_trans_file

normalise_by_pblaze = general.normalise_by_pblaze

# =============================================================================
# End of code
# =============================================================================
