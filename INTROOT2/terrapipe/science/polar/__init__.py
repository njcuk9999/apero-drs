#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from terrapipe.science.polar import general
from terrapipe.science.polar import lsd

__all__ = ['validate_polar_files']

# =============================================================================
# Define functions
# =============================================================================
calculate_polarimetry = general.calculate_polarimetry

calculate_stokes_i = general.calculate_stokes_i

calculate_continuum = general.calculate_continuum

lsd_analysis_wrapper = lsd.lsd_analysis_wrapper

validate_polar_files = general.validate_polar_files

quality_control = general.quality_control

# =============================================================================
# End of code
# =============================================================================
