#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:35
@author: ncook
Version 0.0.1
"""
from apero.science.preprocessing import identification
from apero.science.preprocessing import detector
from apero.science.preprocessing import gen_pp

__all__ = []

# =============================================================================
# Define functions
# =============================================================================
drs_infile_id = identification.drs_infile_id

drs_outfile_id = identification.drs_outfile_id

get_hot_pixels = detector.get_hot_pixels

reject_infile = gen_pp.reject_infile

correct_cosmics = detector.correct_cosmics

correct_top_bottom = detector.ref_top_bottom

correct_left_right = detector.correct_left_right

nirps_order_mask = detector.nirps_order_mask

median_filter_dark_amps = detector.median_filter_dark_amp

median_one_over_f_noise = detector.median_one_over_f_noise

nirps_correction = detector.nirps_correction

test_for_corrupt_files = detector.test_for_corrupt_files

quality_control = gen_pp.quality_control

resolve_target = gen_pp.resolve_target

# =============================================================================
# End of code
# =============================================================================