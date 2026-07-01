#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for spline wrappers and unit-handling helpers in gen_math."""

import numpy as np
import pytest

from aperocore.math import gen_math


def test_iuv_spline_returns_nanspline_when_k_too_large() -> None:
    """`iuv_spline` should return `NanSpline` when len(x) < k+1."""
    xvalues = np.array([0.0, 1.0, 2.0])
    yvalues = np.array([1.0, 2.0, 3.0])
    spline = gen_math.iuv_spline(xvalues, yvalues, k=3)
    assert isinstance(spline, gen_math.NanSpline)


def test_nanspline_call_returns_nan_vector_with_input_length() -> None:
    """`NanSpline` call should return all-NaN output with matching length."""
    spline = gen_math.NanSpline('forced failure')
    xvalues = np.linspace(0.0, 1.0, 5)
    out = spline(xvalues)
    assert out.shape == xvalues.shape
    assert np.isnan(out).all()


def test_relativistic_waveshift_zero_velocity_returns_one() -> None:
    """Relativistic correction should be exactly one at dv=0."""
    corr = gen_math.relativistic_waveshift(0.0, units='m/s')
    assert np.isclose(corr, 1.0)


def test_relativistic_waveshift_invalid_units_raises() -> None:
    """Unsupported unit strings should raise `ValueError`."""
    with pytest.raises(ValueError):
        gen_math.relativistic_waveshift(1.0, units='cm/s')


def test_covariance_vs_distance_returns_expected_shapes() -> None:
    """Covariance helper should return arrays aligned to distance bins."""
    xvalues = np.array([0.0, 1.0, 2.0, 3.0])
    yvalues = np.array([1.0, 2.0, 3.0, 4.0])
    distances = np.array([1.0, 2.0])
    dx_out, cov_out, npairs = gen_math.covariance_vs_distance(
        xvalues, yvalues, distances
    )
    assert dx_out.shape == distances.shape
    assert cov_out.shape == distances.shape
    assert npairs.shape == distances.shape

