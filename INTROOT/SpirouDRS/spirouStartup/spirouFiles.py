#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-31 at 18:06

@author: cook
"""

from . import spirouRecipe

# =============================================================================
# Define Files
# =============================================================================
drs_input = spirouRecipe.DrsInput
drs_fits_input = spirouRecipe.DrsFitsFile

# =============================================================================
# Input Files
# =============================================================================
dark_dark = drs_fits_input('DARK_DARK', DPRTYPE='DARK_DARK')
flat_dark = drs_fits_input('FLAT_DARK', DPRTYPE='FLAT_DARK')
dark_flat = drs_fits_input('DARK_FLAT', DPRTYPE='DARK_FLAT')



# =============================================================================
# Output Files
# =============================================================================

# =============================================================================
# End of code
# =============================================================================
