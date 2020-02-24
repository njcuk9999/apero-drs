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
from apero.science.preprocessing import general

__all__ = []

# =============================================================================
# Define functions
# =============================================================================
drs_infile_id = identification.drs_infile_id

drs_outfile_id = identification.drs_outfile_id

get_hot_pixels = detector.get_hot_pixels

fix_header = identification.fix_header

correct_top_bottom = detector.ref_top_bottom

median_filter_dark_amps = detector.median_filter_dark_amp

median_one_over_f_noise = detector.median_one_over_f_noise

nirps_correction = detector.nirps_correction

test_for_corrupt_files = detector.test_for_corrupt_files

quality_control = general.quality_control

# =============================================================================
# End of code
# =============================================================================