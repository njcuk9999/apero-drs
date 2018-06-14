#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou THORCA module

Created on 2017-10-30 at 17:09

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouTHORCA
from . import spirouWAVE

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouTHORCA.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['CalcInstrumentDrift', 'CalcLittrowSolution',
           'DetectBadLines', 'ExtrapolateLittrowSolution',
           'FirstGuessSolution', 'Fit1DSolution', 'FPWaveSolution',
           'GetE2DSll', 'GetLampParams', 'JoinOrders', 'SecondGuessSolution']


# =============================================================================
# Function aliases
# =============================================================================
CalcInstrumentDrift = spirouWAVE.calculate_instrument_drift

CalcLittrowSolution = spirouTHORCA.calculate_littrow_sol

DetectBadLines = spirouTHORCA.detect_bad_lines

ExtrapolateLittrowSolution = spirouTHORCA.extrapolate_littrow_sol

FirstGuessSolution = spirouTHORCA.first_guess_at_wave_solution

Fit1DSolution = spirouTHORCA.fit_1d_solution

FPWaveSolution = spirouWAVE.fp_wavelength_sol

GetE2DSll = spirouTHORCA.get_e2ds_ll

GetLampParams = spirouTHORCA.get_lamp_parameters

JoinOrders = spirouTHORCA.join_orders

SecondGuessSolution = spirouTHORCA.second_guess_at_wave_solution


# =============================================================================
# End of code
# =============================================================================
