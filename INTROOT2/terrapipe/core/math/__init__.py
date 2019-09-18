#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 15:53

@author: cook
"""
from . import general
from . import gauss
from . import nan
from . import fast

# =============================================================================
# Define functions
# =============================================================================

calculate_polyvals = general.calculate_polyvals

fit_gauss_with_slope = gauss.fit_gauss_with_slope

fit2dpoly = general.fit2dpoly

fitgaussian = gauss.fitgaussian

fwhm = general.fwhm

gauss_fit_nn = gauss.gauss_fit_nn

gaussian_function_nn =  gauss.gaussian_function_nn

gauss_function = gauss.gauss_function

gauss_fit_s = gauss.gauss_fit_s

get_dll_from_coefficients = general.get_dll_from_coefficients

get_ll_from_coefficients = general.get_ll_from_coefficients

get_ll_from_coefficients_cheb = general.get_ll_from_coefficients_cheb

iuv_spline = general.iuv_spline

killnan = nan.killnan

measure_box_min_max = general.measure_box_min_max

medfilt_1d = fast.medfilt_1d

nanargmax = fast.nanargmax

nanargmin = fast.nanargmin

nanmax = fast.nanmax

nanmin = fast.nanmin

nanmean = fast.nanmean

nanmedian = fast.nanmedian

nanpad = nan.nanpad

nanpolyfit = nan.nanpolyfit

nanstd = fast.nanstd

nansum = fast.nansum

median = fast.median

linear_minimization = general.linear_minimization

relativistic_waveshift = general.relativistic_waveshift

# =============================================================================
# End of code
# =============================================================================
