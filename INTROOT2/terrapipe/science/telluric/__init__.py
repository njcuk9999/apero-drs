#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from terrapipe.science.telluric import general

__all__ = ['calculate_telluric_absorption', 'get_blacklist', 'get_whitelist',
           'load_conv_tapas', 'load_templates', 'mk_tellu_quality_control',
           'normalise_by_pblaze']

# =============================================================================
# Define functions
# =============================================================================
calc_recon_and_correct = general.calc_recon_and_correct

calculate_telluric_absorption = general.calculate_telluric_absorption

fit_tellu_write_corrected = general.fit_tellu_write_corrected

fit_tellu_write_corrected_s1d = general.fit_tellu_write_corrected_s1d

fit_tellu_write_recon = general.fit_tellu_write_recon

fit_tellu_quality_control = general.fit_tellu_quality_control

gen_abso_pca_calc = general.gen_abso_pca_calc

get_blacklist = general.get_blacklist

get_non_tellu_objs = general.get_non_tellu_objs

get_trans_files = general.get_transmission_files

get_whitelist = general.get_whitelist

load_conv_tapas = general.load_conv_tapas

load_tapas_convolved = general.load_tapas_convolved

load_templates = general.load_templates

make_1d_template_cube = general.make_1d_template_cube

make_template_cubes = general.make_template_cubes

mk_tellu_quality_control = general.mk_tellu_quality_control

mk_tellu_write_trans_file = general.mk_tellu_write_trans_file

mk_1d_template_write = general.mk_1d_template_write

mk_template_write = general.mk_template_write

normalise_by_pblaze = general.normalise_by_pblaze

shift_all_to_frame = general.shift_all_to_frame

# =============================================================================
# End of code
# =============================================================================
