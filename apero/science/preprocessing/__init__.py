#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:35
@author: ncook
Version 0.0.1
"""
from apero.science.preprocessing import detector
from apero.science.preprocessing import gen_pp
from apero.science.preprocessing import identification

__all__ = []

# =============================================================================
# Define functions
# =============================================================================
correct_capacitive_coupling = detector.correct_capacitive_coupling

correct_sci_capacitive_coupling = detector.correct_sci_capacitive_coupling

correct_cosmics = detector.correct_cosmics

correct_top_bottom = detector.ref_top_bottom

correct_left_right = detector.correct_left_right

create_led_flat = detector.create_led_flat

drs_infile_id = identification.drs_infile_id

drs_outfile_id = identification.drs_outfile_id

errslope_correct = detector.errslope_correct

get_hot_pixels = detector.get_hot_pixels

get_obj_reject_list = gen_pp.get_obj_reject_list

get_file_reject_list = gen_pp.get_file_reject_list

intercept_correct = detector.intercept_correct

load_led_flat = detector.load_led_flat

median_filter_dark_amps = detector.median_filter_dark_amp

median_one_over_f_noise = detector.median_one_over_f_noise

nirps_correction = detector.nirps_correction

nirps_order_mask = detector.nirps_order_mask

quality_control1 = gen_pp.quality_control1

quality_control2 = gen_pp.quality_control2

reject_infile = gen_pp.reject_infile

resolve_target = gen_pp.resolve_target

test_for_corrupt_files = detector.test_for_corrupt_files

# =============================================================================
# End of code
# =============================================================================
