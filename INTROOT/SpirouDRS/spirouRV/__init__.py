#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou radial velocity module module

Created on 2017-11-21 at 11:52

@author: cook

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
__all__ = ['CalcRVdrift2D', 'Coravelation', 'CreateDriftFile',
           'DeltaVrms2D', 'DriftPerOrder', 'DriftAllOrders',
           'FitCCF', 'GetDrift', 'GetCCFMask', 'GetFiberC_E2DSName',
           'PearsonRtest', 'RemoveWidePeaks', 'RemoveZeroPeaks',
           'ReNormCosmic2D', 'SigmaClip']

# =============================================================================
# Function aliases
# =============================================================================
CalcRVdrift2D = spirouRV.calculate_rv_drifts_2d

Coravelation = spirouRV.coravelation

CreateDriftFile = spirouRV.create_drift_file

DeltaVrms2D = spirouRV.delta_v_rms_2d

DriftPerOrder = spirouRV.drift_per_order

DriftAllOrders = spirouRV.drift_all_orders

FitCCF = spirouRV.fit_ccf

GetDrift = spirouRV.get_drift

GetCCFMask = spirouRV.get_ccf_mask

GetFiberC_E2DSName = spirouRV.get_fiberc_e2ds_name

PearsonRtest = spirouRV.pearson_rtest

RemoveWidePeaks = spirouRV.remove_wide_peaks

RemoveZeroPeaks = spirouRV.remove_zero_peaks

ReNormCosmic2D = spirouRV.renormalise_cosmic2d

SigmaClip = spirouRV.sigma_clip

# =============================================================================
# End of code
# =============================================================================
