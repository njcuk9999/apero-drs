#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 15:53

@author: cook
"""

from apero.core.math import fast
from apero.core.math import gauss
from apero.core.math import gen_math
from apero.core.math import nan

# =============================================================================
# Define functions
# =============================================================================
calculate_polyvals = gen_math.calculate_polyvals

centered_super_gauss = gauss.centered_super_gauss

ea_airy_function = gen_math.ea_airy_function

estimate_sigma = gen_math.estimate_sigma

fit_gauss_with_slope = gauss.fit_gauss_with_slope

fit2dpoly = gen_math.fit2dpoly

fit_cheby = gen_math.fit_cheby

fitgaussian = gauss.fitgaussian

fuzzy_curve_fit = gen_math.fuzzy_curve_fit

fwhm = gen_math.fwhm

gauss_fit_nn = gauss.gauss_fit_nn

gaussian_function_nn = gauss.gaussian_function_nn

gauss_function = gauss.gauss_function

gauss_function_nodc = gauss.gauss_function_nodc

gauss_beta_function = gauss.gauss_beta_function

gauss_fit_s = gauss.gauss_fit_s

get_magic_grid = gen_math.get_magic_grid

get_circular_mask = gen_math.get_circular_mask

get_dll_from_coefficients = gen_math.get_dll_from_coefficients

get_ll_from_coefficients = gen_math.get_ll_from_coefficients

get_ll_from_coefficients_cheb = gen_math.get_ll_from_coefficients_cheb

iuv_spline = gen_math.iuv_spline

killnan = nan.killnan

largest_divisor_below = gen_math.largest_divisor_below

lowpassfilter = gen_math.lowpassfilter

measure_box_min_max = gen_math.measure_box_min_max

median_absolute_deviation = gen_math.median_absolute_deviation

medbin = gen_math.medbin

medfilt_1d = fast.medfilt_1d

median = fast.median

nanargmax = fast.nanargmax

nanargmin = fast.nanargmin

nanmax = fast.nanmax

nanmin = fast.nanmin

nanmean = fast.nanmean

nanmedian = fast.nanmedian

nanpad = nan.nanpad

nanchebyfit = nan.nanchebyfit

nanpolyfit = nan.nanpolyfit

nanstd = fast.nanstd

nansum = fast.nansum

nanpercentile = fast.nanpercentile

normal_fraction = gen_math.normal_fraction

odd_ratio_mean = fast.odd_ratio_mean

percentile_bin = gen_math.percentile_bin

linear_minimization = gen_math.linear_minimization

relativistic_waveshift = gen_math.relativistic_waveshift

robust_nanstd = gen_math.robust_nanstd

robust_chebyfit = gen_math.robust_chebyfit

robust_polyfit = gen_math.robust_polyfit

rot8 = gen_math.rot8

sinc = gen_math.sinc

sigfig = gen_math.sigfig

square_medbin = gen_math.square_medbin

super_gauss_fast = fast.super_gauss_fast

val_cheby = gen_math.val_cheby

xpand_mask = gen_math.xpand_mask

# =============================================================================
# End of code
# =============================================================================
