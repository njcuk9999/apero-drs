#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for small, stable helpers in apero-core."""

import numpy as np

from aperocore.base import drs_base
from aperocore.math import gauss
from aperocore.math import nan


# =============================================================================
# Define functions
# =============================================================================
def test_generate_hash_is_deterministic_for_same_input() -> None:
    """`generate_hash` should return the same hash for same text and size."""
    value1 = drs_base.generate_hash('apero', size=10)
    value2 = drs_base.generate_hash('apero', size=10)
    assert value1 == value2


def test_generate_hash_changes_with_size() -> None:
    """Changing digest size should change output length and value."""
    short_hash = drs_base.generate_hash('apero', size=4)
    long_hash = drs_base.generate_hash('apero', size=12)
    # blake2 hex output length is 2 * digest_size.
    assert len(short_hash) == 8
    assert len(long_hash) == 24
    assert short_hash != long_hash


def test_escape_map_replaces_escape_sequences() -> None:
    """`_escape_map` should map escaped newlines and tabs to real chars."""
    raw = r'line1\nline2\tvalue'
    mapped = drs_base._escape_map(raw)
    assert mapped == 'line1\nline2\tvalue'


def test_escape_map_keeps_non_string_values() -> None:
    """`_escape_map` should return non-string values unchanged."""
    obj = {'a': 1}
    assert drs_base._escape_map(obj) is obj


def test_base_null_text_with_standard_and_custom_nulls() -> None:
    """`base_null_text` should handle `None`, blanks, and custom null values."""
    assert drs_base.base_null_text(None)
    assert drs_base.base_null_text(' n/a ', nulls=['N/A'])
    assert not drs_base.base_null_text('value', nulls=['N/A'])


def test_killnan_replaces_non_finite_values() -> None:
    """`killnan` should replace NaN and infinities with the chosen value."""
    values = np.array([1.0, np.nan, np.inf, -np.inf, 2.0])
    out = nan.killnan(values, value=-99.0)
    assert np.allclose(out, np.array([1.0, -99.0, -99.0, -99.0, 2.0]))


def test_nanpolyfit_matches_polyfit_on_masked_points() -> None:
    """`nanpolyfit` should match `np.polyfit` applied to finite points only."""
    xvalues = np.array([0.0, 1.0, 2.0, 3.0, np.nan, 4.0])
    yvalues = np.array([1.0, 3.0, 5.0, np.nan, 9.0, 9.0])
    coeffs = nan.nanpolyfit(xvalues, yvalues, deg=1)
    mask = np.isfinite(xvalues) & np.isfinite(yvalues)
    expected = np.polyfit(xvalues[mask], yvalues[mask], deg=1)
    assert np.allclose(coeffs, expected)


def test_nanchebyfit_matches_numpy_chebfit_on_masked_points() -> None:
    """`nanchebyfit` should match chebfit when finite values are selected."""
    xvalues = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
    yvalues = np.array([1.0, np.nan, 0.0, 0.25, 1.0])
    domain = [-1.0, 1.0]
    coeffs = nan.nanchebyfit(xvalues, yvalues, deg=2, domain=domain)
    xcheb = 2 * (xvalues - domain[0]) / (domain[1] - domain[0]) - 1
    mask = np.isfinite(xvalues) & np.isfinite(yvalues)
    expected = np.polynomial.chebyshev.chebfit(xcheb[mask], yvalues[mask], 2)
    assert np.allclose(coeffs, expected)


def test_gauss_function_matches_closed_form_at_center() -> None:
    """At x=x0 the gaussian value should be `a + dc`."""
    yvalue = gauss.gauss_function(2.0, a=3.5, x0=2.0, sigma=1.2, dc=0.4)
    assert np.isclose(yvalue, 3.9)


def test_gauss_function_nodc_equals_gauss_with_zero_dc() -> None:
    """No-DC variant should match full gaussian when dc=0."""
    xvalues = np.linspace(-3.0, 3.0, 11)
    y1 = gauss.gauss_function_nodc(xvalues, a=2.0, x0=0.5, sigma=1.1)
    y2 = gauss.gauss_function(xvalues, a=2.0, x0=0.5, sigma=1.1, dc=0.0)
    assert np.allclose(y1, y2)


def test_gauss_function_is_symmetric_around_center_when_dc_zero() -> None:
    """Gaussian should be symmetric for offsets around the mean."""
    acoeff = 5.0
    center = 1.5
    sigma = 0.7
    delta = 0.3
    left = gauss.gauss_function(center - delta, acoeff, center, sigma, 0.0)
    right = gauss.gauss_function(center + delta, acoeff, center, sigma, 0.0)
    assert np.isclose(left, right)

