#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic unit tests for easy-to-verify helpers in `aperocore.math.gen_math`."""

import numpy as np

from aperocore.math import gen_math


def test_fwhm_value_for_sigma_one() -> None:
    """`fwhm(1)` should match the standard Gaussian conversion constant."""
    assert np.isclose(gen_math.fwhm(1.0), 2.3548200450309493)


def test_normal_fraction_zero_sigma_is_zero() -> None:
    """`normal_fraction(0)` should produce exactly zero."""
    assert np.isclose(gen_math.normal_fraction(0.0), 0.0)


def test_largest_divisor_below_returns_expected_divisor() -> None:
    """`largest_divisor_below` should return the largest divisor <= bound."""
    assert gen_math.largest_divisor_below(4088, 9) == 8


def test_calculate_polyvals_matches_numpy_polyval() -> None:
    """`calculate_polyvals` should evaluate each coefficient row correctly."""
    coeffs = np.array([[1.0, 2.0], [0.0, 1.0]])
    yfits = gen_math.calculate_polyvals(coeffs, dim=4)
    xfit = np.arange(0, 4, 1)
    expected0 = np.polyval(coeffs[0][::-1], xfit)
    expected1 = np.polyval(coeffs[1][::-1], xfit)
    assert np.allclose(yfits[0], expected0)
    assert np.allclose(yfits[1], expected1)


def test_ea_airy_function_is_positive_and_bounded() -> None:
    """Airy helper should return values above zero point and below peak."""
    xvalues = np.linspace(-1.0, 1.0, 21)
    yvalues = gen_math.ea_airy_function(xvalues, 2.0, 0.0, 1.0, 2.0, 1.5)
    assert np.all(yvalues >= 1.5)
    assert np.all(yvalues <= 3.5)


def test_measure_box_min_max_constant_signal() -> None:
    """For constant vectors min and max profiles should stay constant."""
    signal = np.full(10, 3.0)
    minv, maxv = gen_math.measure_box_min_max(signal, size=2)
    assert np.allclose(minv, 3.0)
    assert np.allclose(maxv, 3.0)


def test_get_magic_grid_is_strictly_increasing() -> None:
    """`get_magic_grid` should create a monotonic increasing wavelength grid."""
    grid = gen_math.get_magic_grid(1000.0, 1001.0, dv_grid=500.0)
    assert grid.size > 0
    assert np.all(np.diff(grid) > 0)


def test_sigfig_handles_scalar_list_and_array() -> None:
    """`sigfig` should preserve container type and significant-figure logic."""
    assert isinstance(gen_math.sigfig(1.23456, 3), float)
    assert gen_math.sigfig(1.23456, 3) == 1.23
    assert isinstance(gen_math.sigfig([1.23456], 3), list)
    arr = gen_math.sigfig(np.array([1.23456]), 3)
    assert isinstance(arr, np.ndarray)
    assert np.isclose(arr[0], 1.23)


def test_rot8_invert_recovers_original_image() -> None:
    """Applying `rot8` then inverse rotation should recover the input array."""
    image = np.arange(16).reshape(4, 4)
    rotated = gen_math.rot8(image, 1, invert=False)
    back = gen_math.rot8(rotated, 1, invert=True)
    assert np.array_equal(image, back)


def test_percentile_bin_expected_shape() -> None:
    """`percentile_bin` output shape should match requested bin grid."""
    image = np.arange(100).reshape(10, 10).astype(float)
    out = gen_math.percentile_bin(image, bx=5, by=2, percentile=50)
    assert out.shape == (2, 5)


def test_get_circular_mask_returns_boolean_square() -> None:
    """`get_circular_mask` should return a square boolean array."""
    mask = gen_math.get_circular_mask(9)
    assert mask.shape == (9, 9)
    assert mask.dtype == bool


def test_fit_and_val_cheby_round_trip() -> None:
    """Chebyshev fit and evaluate should reproduce simple input relation."""
    xvalues = np.linspace(0.0, 10.0, 50)
    yvalues = 2.0 + 0.5 * xvalues
    coeffs = gen_math.fit_cheby(xvalues, yvalues, deg=1, domain=[0.0, 10.0])
    yfit = gen_math.val_cheby(coeffs, xvalues, domain=[0.0, 10.0])
    assert np.allclose(yvalues, yfit, atol=1e-8)


def test_relativistic_waveshift_zero_velocity_is_one() -> None:
    """For zero velocity the multiplicative wavelength correction is one."""
    corr = gen_math.relativistic_waveshift(0.0, units='km/s')
    assert np.isclose(corr, 1.0)

