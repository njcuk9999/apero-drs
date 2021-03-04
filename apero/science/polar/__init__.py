#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from apero.science.polar import gen_pol
from apero.science.polar import lsd

__all__ = ['validate_polar_files']

# =============================================================================
# Define functions
# =============================================================================
calculate_polarimetry = gen_pol.calculate_polarimetry

calculate_stokes_i = gen_pol.calculate_stokes_i

calculate_continuum = gen_pol.calculate_continuum

generate_statistics = gen_pol.generate_statistics

lsd_analysis_wrapper = lsd.lsd_analysis_wrapper

validate_polar_files = gen_pol.validate_polar_files

quality_control = gen_pol.quality_control

write_files = gen_pol.write_files

# =============================================================================
# End of code
# =============================================================================
