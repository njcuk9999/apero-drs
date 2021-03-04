#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from apero.science.velocity import gen_vel

__all__ = ['compute_ccf_fp', 'compute_ccf_science', 'locate_reference_file',
           'measure_fp_peaks', 'remove_telluric_domain', 'remove_wide_peaks',
           'write_ccf']

# =============================================================================
# Define functions
# =============================================================================
compute_ccf_fp = gen_vel.compute_ccf_fp

compute_ccf_science = gen_vel.compute_ccf_science

fit_fp_peaks = gen_vel.fit_fp_peaks

locate_reference_file = gen_vel.locate_reference_file

measure_fp_peaks = gen_vel.measure_fp_peaks

remove_telluric_domain = gen_vel.remove_telluric_domain

remove_wide_peaks = gen_vel.remove_wide_peaks

write_ccf = gen_vel.write_ccf


# =============================================================================
# End of code
# =============================================================================
