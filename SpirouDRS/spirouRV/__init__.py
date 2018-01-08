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
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['DeltaVrms2D', 'ReNormCosmic2D', 'CalcRVdrift2D']

# =============================================================================
# Function aliases
# =============================================================================
# Compute radial velocity drift between reference spectrum and current spectrum
CalcRVdrift2D = spirouRV.calculate_rv_drifts_2d

# calculate and fit CCF
Coravelation = spirouRV.coravelation

# create drift file for drift-peak
CreateDriftFile = spirouRV.create_drift_file

# Compute the photon noise uncertainty for all order
DeltaVrms2D = spirouRV.delta_v_rms_2d


DriftPerOrder = spirouRV.drift_per_order

DriftAllOrders = spirouRV.drift_all_orders

# fit the CCF
FitCCF = spirouRV.fit_ccf

GetDrift = spirouRV.get_drift

GetCCFMask = spirouRV.get_ccf_mask

PearsonRtest = spirouRV.pearson_rtest

RemoveWidePeaks = spirouRV.remove_wide_peaks

RemoveZeroPeaks = spirouRV.remove_zero_peaks

# Correction of the cosmics and renormalisation by comparison with
#    reference spectrum
ReNormCosmic2D = spirouRV.renormalise_cosmic2d


SigmaClip = spirouRV.sigma_clip



# =============================================================================
# End of code
# =============================================================================
