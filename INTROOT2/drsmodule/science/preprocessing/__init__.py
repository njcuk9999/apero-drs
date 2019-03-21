#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:35
@author: ncook
Version 0.0.1
"""
from . import identification
from . import detector

__all__ = []

# =============================================================================
# Define functions
# =============================================================================
drs_infile_id = identification.drs_infile_id

drs_outfile_id = identification.drs_outfile_id

get_hot_pixels = detector.get_hot_pixels

correct_top_bottom = detector.ref_top_bottom

median_filter_dark_amps = detector.median_filter_dark_amp

median_one_over_f_noise = detector.median_one_over_f_noise

test_for_corrupt_files = detector.test_for_corrupt_files

# =============================================================================
# End of code
# =============================================================================