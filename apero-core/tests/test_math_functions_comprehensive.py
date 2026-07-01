#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for apero math functions."""

import numpy as np
from aperocore.math import gauss, nan, fast


# =============================================================================
# Define functions - gauss function tests
# =============================================================================
def test_gauss_function_has_expected_functions() -> None:
    """gauss module should have expected functions."""
    assert hasattr(gauss, 'gauss_function')
    assert hasattr(gauss, 'gauss_function_nodc')


def test_gauss_function_at_center() -> None:
    """gauss_function at x=x0 should equal a + dc."""
    x0 = 2.0
    a = 3.5
    sigma = 1.2
    dc = 0.4
    result = gauss.gauss_function(x0, a=a, x0=x0, sigma=sigma, dc=dc)
    expected = a + dc
    assert np.isclose(result, expected)


def test_gauss_function_far_from_center() -> None:
    """gauss_function far from center should approach dc."""
    x = 100.0
    a = 1.0
    x0 = 0.0
    sigma = 1.0
    dc = 0.5
    result = gauss.gauss_function(x, a=a, x0=x0, sigma=sigma, dc=dc)
    # Far from center, should be very close to dc
    assert result < (dc + 0.01)


def test_gauss_function_returns_array_for_array_input() -> None:
    """gauss_function should return array for array input."""
    x = np.linspace(-3, 3, 10)
    result = gauss.gauss_function(x, a=1.0, x0=0.0, sigma=1.0, dc=0.0)
    assert isinstance(result, np.ndarray)
    assert result.shape == x.shape


def test_gauss_function_nodc_matches_with_dc_zero() -> None:
    """gauss_function_nodc should match gauss_function with dc=0."""
    x = np.linspace(-3, 3, 10)
    a = 2.0
    x0 = 0.5
    sigma = 1.1
    y1 = gauss.gauss_function_nodc(x, a=a, x0=x0, sigma=sigma)
    y2 = gauss.gauss_function(x, a=a, x0=x0, sigma=sigma, dc=0.0)
    assert np.allclose(y1, y2)


def test_gauss_function_is_symmetric() -> None:
    """gauss_function should be symmetric around center."""
    x0 = 1.5
    a = 5.0
    sigma = 0.7
    delta = 0.3

    left = gauss.gauss_function(
        x0 - delta, a=a, x0=x0, sigma=sigma, dc=0.0
    )
    right = gauss.gauss_function(
        x0 + delta, a=a, x0=x0, sigma=sigma, dc=0.0
    )
    assert np.isclose(left, right)


def test_gauss_function_peak_proportional_to_amplitude() -> None:
    """gauss_function peak should scale with amplitude."""
    x = np.array([0.0])
    a1 = 1.0
    a2 = 2.0
    x0 = 0.0
    sigma = 1.0
    dc = 0.0

    y1 = gauss.gauss_function(x, a=a1, x0=x0, sigma=sigma, dc=dc)
    y2 = gauss.gauss_function(x, a=a2, x0=x0, sigma=sigma, dc=dc)
    assert np.isclose(y2[0] / y1[0], 2.0)


# =============================================================================
# Define functions - nan handling tests
# =============================================================================
def test_killnan_replaces_nan() -> None:
    """killnan should replace NaN values."""
    array = np.array([1.0, np.nan, 3.0])
    result = nan.killnan(array, value=-99.0)
    assert not np.any(np.isnan(result))
    assert result[1] == -99.0


def test_killnan_replaces_inf() -> None:
    """killnan should replace infinity values."""
    array = np.array([1.0, np.inf, -np.inf, 3.0])
    result = nan.killnan(array, value=-99.0)
    assert np.isfinite(result).all()
    assert np.sum(result == -99.0) == 2


def test_killnan_preserves_finite() -> None:
    """killnan should preserve finite values."""
    array = np.array([1.0, 2.0, 3.0])
    result = nan.killnan(array, value=-99.0)
    assert np.allclose(result, array)


def test_killnan_default_value() -> None:
    """killnan with default value should use 0."""
    array = np.array([1.0, np.nan, 3.0])
    result = nan.killnan(array)
    # Default value is typically 0
    assert result[1] == 0.0


# =============================================================================
# Define functions - polyfit tests
# =============================================================================
def test_nanpolyfit_matches_polyfit() -> None:
    """nanpolyfit should match polyfit for finite points."""
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([1.0, 3.0, 5.0, 7.0, 9.0])  # Linear: y = 2x + 1

    coeffs = nan.nanpolyfit(x, y, deg=1)
    expected = np.polyfit(x, y, deg=1)
    assert np.allclose(coeffs, expected)


def test_nanpolyfit_ignores_nan() -> None:
    """nanpolyfit should ignore NaN points."""
    x = np.array([0.0, 1.0, 2.0, 3.0, np.nan, 4.0])
    y = np.array([1.0, 3.0, 5.0, 7.0, 9.0, 9.0])

    coeffs = nan.nanpolyfit(x, y, deg=1)
    mask = np.isfinite(x) & np.isfinite(y)
    expected = np.polyfit(x[mask], y[mask], deg=1)
    assert np.allclose(coeffs, expected)


def test_nanpolyfit_different_degrees() -> None:
    """nanpolyfit should work with different polynomial degrees."""
    x = np.linspace(0, 10, 11)
    y = 2 * x**2 - 3 * x + 1

    for deg in [1, 2, 3, 4]:
        coeffs = nan.nanpolyfit(x, y, deg=deg)
        assert len(coeffs) == deg + 1


# =============================================================================
# Define functions - chebyshev fit tests
# =============================================================================
def test_nanchebyfit_accepts_domain() -> None:
    """nanchebyfit should accept domain parameter."""
    x = np.linspace(-1, 1, 10)
    y = np.sin(x)
    domain = [-1, 1]

    result = nan.nanchebyfit(x, y, deg=3, domain=domain)
    assert isinstance(result, np.ndarray)


def test_nanchebyfit_ignores_nan() -> None:
    """nanchebyfit should ignore NaN values."""
    x = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
    y = np.array([1.0, np.nan, 0.0, 0.25, 1.0])
    domain = [-1.0, 1.0]

    result = nan.nanchebyfit(x, y, deg=2, domain=domain)
    assert isinstance(result, np.ndarray)


# =============================================================================
# Define functions - fast math functions
# =============================================================================
def test_fast_module_has_functions() -> None:
    """fast module should have fast math functions."""
    assert hasattr(fast, 'rot8')


def test_rot8_identity_rotation() -> None:
    """rot8 with rotnum=0 should return same array."""
    array = np.array([[1, 2], [3, 4]])
    result = fast.rot8(array, 0)
    assert np.array_equal(result, array)


def test_rot8_accepts_array() -> None:
    """rot8 should accept 2D array."""
    array = np.array([[1, 2, 3], [4, 5, 6]])
    for rotnum in range(8):
        result = fast.rot8(array, rotnum)
        assert isinstance(result, np.ndarray)


# =============================================================================
# Define functions - math module attribute tests
# =============================================================================
def test_gauss_module_is_importable() -> None:
    """gauss module should be importable."""
    from aperocore.math import gauss as g
    assert g is not None


def test_nan_module_is_importable() -> None:
    """nan module should be importable."""
    from aperocore.math import nan as n
    assert n is not None


def test_fast_module_is_importable() -> None:
    """fast module should be importable."""
    from aperocore.math import fast as f
    assert f is not None


# =============================================================================
# End of code
# =============================================================================

