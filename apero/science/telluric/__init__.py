#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from apero.science.telluric import gen_tellu
from apero.science.telluric import mk_tellu
from apero.science.telluric import fit_tellu
from apero.science.telluric import template_tellu

__all__ = ['calculate_tellu_res_absorption', 'get_tellu_exclude_list',
           'get_tellu_include_list', 'load_conv_tapas', 'load_templates',
           'mk_tellu_quality_control', 'normalise_by_pblaze']

# =============================================================================
# Define functions
# =============================================================================
calc_recon_and_correct = fit_tellu.calc_recon_and_correct

calc_res_model = fit_tellu.calc_res_model

calculate_tellu_res_absorption = mk_tellu.calculate_tellu_res_absorption

correct_other_science = fit_tellu.correct_other_science

fit_tellu_write_corrected = fit_tellu.fit_tellu_write_corrected

fit_tellu_write_corrected_s1d = fit_tellu.fit_tellu_write_corrected_s1d

fit_tellu_write_recon = fit_tellu.fit_tellu_write_recon

fit_tellu_quality_control = fit_tellu.fit_tellu_quality_control

fit_tellu_summary = fit_tellu.fit_tellu_summary

gen_abso_pca_calc = fit_tellu.gen_abso_pca_calc

get_tellu_exclude_list = gen_tellu.get_tellu_exclude_list

get_non_tellu_objs = gen_tellu.get_non_tellu_objs

get_trans_files = gen_tellu.get_transmission_files

get_tellu_objs = gen_tellu.get_tellu_objs

get_trans_model = gen_tellu.get_trans_model

get_tellu_include_list = gen_tellu.get_tellu_include_list

get_blaze_props = gen_tellu.get_blaze_props

list_current_templates = template_tellu.list_current_templates

load_conv_tapas = gen_tellu.load_conv_tapas

load_templates = gen_tellu.load_templates

load_tellu_file = gen_tellu.load_tellu_file

make_1d_template_cube = template_tellu.make_1d_template_cube

make_trans_cube = mk_tellu.make_trans_cube

make_trans_model = mk_tellu.make_trans_model

make_template_cubes = template_tellu.make_template_cubes

mk_tellu_quality_control = mk_tellu.mk_tellu_quality_control

mk_tellu_write_trans_file = mk_tellu.mk_tellu_write_trans_file

mk_tellu_summary = mk_tellu.mk_tellu_summary

mk_1d_template_write = template_tellu.mk_1d_template_write

mk_template_qc = template_tellu.mk_template_qc

mk_model_qc = mk_tellu.mk_model_qc

mk_model_summary = mk_tellu.mk_model_summary

mk_write_model = mk_tellu.mk_write_model

mk_template_write = template_tellu.mk_template_write

mk_template_summary = template_tellu.mk_template_summary

tellu_preclean = gen_tellu.tellu_preclean

normalise_by_pblaze = gen_tellu.normalise_by_pblaze

shift_template = fit_tellu.shift_template

# =============================================================================
# End of code
# =============================================================================
