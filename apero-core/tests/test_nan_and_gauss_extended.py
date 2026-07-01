#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extended unit tests for NaN and Gaussian helpers in aperocore."""

import numpy as np

from aperocore.math import gauss
from aperocore.math import nan


def test_nanpad_fills_center_nan_from_neighbor_median() -> None:
    """`nanpad` should replace center NaN with local finite-neighbor median."""
    image = np.array([[np.nan, 2.0, 3.0],
                      [4.0, np.nan, 6.0],
                      [7.0, 8.0, 9.0]])
    out = nan.nanpad(image)
    assert np.isfinite(out).all()
    assert np.isclose(out[0, 0], 0.0)
    assert np.isclose(out[1, 1], 5.0)


def test_centered_super_gauss_peak_is_amplitude() -> None:
    """Centered super-gaussian should evaluate to `amp` at x=0."""
    value = gauss.centered_super_gauss(np.array([0.0]), fwhm=2.0,
                                       amp=3.5, expo=2.0)
    assert np.isclose(value[0], 3.5)


def test_super_gauss_center_is_amp_plus_zero_point() -> None:
    """Super-gaussian with center offset should give amp+zp at center."""
    value = gauss.super_gauss(np.array([1.5]), center=1.5, amp=2.0,
                              fwhm=3.0, expo=2.0, zp=0.7)
    assert np.isclose(value[0], 2.7)


def test_gauss_floor_is_symmetric_around_zero() -> None:
    """`gauss_floor` should be symmetric for +x and -x."""
    left = gauss.gauss_floor(np.array([-1.2]), a=2.0, sigma=0.8)[0]
    right = gauss.gauss_floor(np.array([1.2]), a=2.0, sigma=0.8)[0]
    assert np.isclose(left, right)

