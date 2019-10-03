#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from . import general

__all__ = ['compute_ccf_fp', 'compute_ccf_science', 'locate_reference_file',
           'measure_fp_peaks', 'remove_telluric_domain', 'remove_wide_peaks',
           'write_ccf']

# =============================================================================
# Define functions
# =============================================================================
compute_ccf_fp = general.compute_ccf_fp

compute_ccf_science = general.compute_ccf_science

locate_reference_file = general.locate_reference_file

measure_fp_peaks = general.measure_fp_peaks

remove_telluric_domain = general.remove_telluric_domain

remove_wide_peaks = general.remove_wide_peaks

write_ccf = general.write_ccf


# =============================================================================
# End of code
# =============================================================================
