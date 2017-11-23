#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-21 at 11:52

@author: cook



Version 0.0.0
"""

from SpirouDRS import spirouConfig
from . import spirouRV

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouRV.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__all__ = ['DeltaVrms2D', 'ReNormCosmic2D', 'CalcRVdrift2D']

# =============================================================================
# Function aliases
# =============================================================================
# Compute the photon noise uncertainty for all order
DeltaVrms2D = spirouRV.delta_v_rms_2d

# Correction of the cosmics and renormalisation by comparison with
#    reference spectrum
ReNormCosmic2D = spirouRV.renormalise_cosmic2d

# Compute radial velocity drift between reference spectrum and current spectrum
CalcRVdrift2D = spirouRV.calculate_rv_drifts_2d


# =============================================================================
# End of code
# =============================================================================
