#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for helper functions in `apero.science.velocity.gen_vel`."""

import numpy as np

from apero.science.velocity import gen_vel


# =============================================================================
# Define functions
# =============================================================================
def test_fwhm_fp_airy_returns_finite_for_valid_coeffs() -> None:
    """`fwhm_fp_airy` should return a finite width for valid parameters."""
    popt = np.array([1.0, 0.0, 4.0, 2.0, 0.0])

    width = gen_vel.fwhm_fp_airy(popt)

    assert np.isfinite(width)
    assert width > 0


def test_fwhm_fp_airy_returns_nan_for_invalid_branch() -> None:
    """`fwhm_fp_airy` should return NaN when acos argument is out of range."""
    popt = np.array([1.0, 0.0, 4.0, 0.1, 0.0])

    width = gen_vel.fwhm_fp_airy(popt)

    assert np.isnan(width)


def test_bisector_cut_is_centered_for_symmetric_profile() -> None:
    """`bisector_cut` should be near zero for symmetric CCF-like data."""
    xx = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    yy = np.array([0.0, 0.8, 1.0, 0.8, 0.0])

    value = gen_vel.bisector_cut(xx, yy, cut=0.7)

    assert abs(value) < 1e-12


def test_get_coeff_dict_handles_1d_and_2d_arrays() -> None:
    """`get_coeff_dict` should map names to scalar and per-order values."""
    names = ['A', 'B']
    one_d = np.array([1.0, 2.0])
    two_d = np.array([[1.0, 2.0], [3.0, 4.0]])

    out_1d = gen_vel.get_coeff_dict(one_d, names)
    out_2d = gen_vel.get_coeff_dict(two_d, names)

    assert out_1d['A'] == 1.0
    assert out_1d['B'] == 2.0
    assert np.array_equal(out_2d['A'], np.array([1.0, 3.0]))
    assert np.array_equal(out_2d['B'], np.array([2.0, 4.0]))

