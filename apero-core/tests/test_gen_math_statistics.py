#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Statistics-focused unit tests for `aperocore.math.gen_math`."""

import numpy as np

from aperocore.math import gen_math


def test_cal_med_abs_dev_zero_for_constant_array() -> None:
    """Median absolute deviation should be zero for constant vectors."""
    data = np.array([5.0, 5.0, 5.0, 5.0])
    assert gen_math.cal_med_abs_dev(data) == 0.0


def test_cal_med_abs_dev_matches_manual_value() -> None:
    """Median absolute deviation should match manual median(|x - median(x)|)."""
    data = np.array([1.0, 2.0, 3.0, 10.0])
    manual = np.median(np.abs(data - np.median(data)))
    assert np.isclose(gen_math.cal_med_abs_dev(data), manual)


def test_inv_normal_fraction_scales_linearly_with_sigma() -> None:
    """The implementation returns a constant factor multiplied by sigma."""
    one_sigma = gen_math.inv_normal_fraction(1.0)
    two_sigma = gen_math.inv_normal_fraction(2.0)
    assert np.isfinite(one_sigma)
    assert np.isclose(two_sigma, 2.0 * one_sigma)


def test_estimate_sigma_is_zero_for_constant_data() -> None:
    """Robust sigma estimate should be zero when all points are identical."""
    data = np.full(100, 7.2)
    assert np.isclose(gen_math.estimate_sigma(data), 0.0)


def test_estimate_sigma_scales_with_data_amplitude() -> None:
    """Sigma estimate should scale linearly with multiplicative data scaling."""
    base = np.linspace(-3.0, 3.0, 1000)
    est1 = gen_math.estimate_sigma(base)
    est2 = gen_math.estimate_sigma(4.0 * base)
    assert np.isclose(est2, 4.0 * est1, rtol=1e-2)


def test_robust_polyfit_recovers_clean_linear_relation() -> None:
    """Robust polyfit should recover coefficients on noise-free linear data."""
    xvalues = np.linspace(-5.0, 5.0, 200)
    yvalues = 2.5 * xvalues - 1.0
    fit, keep = gen_math.robust_polyfit(xvalues, yvalues, degree=1,
                                        nsigcut=5.0)
    assert np.isclose(fit[0], 2.5, atol=1e-6)
    assert np.isclose(fit[1], -1.0, atol=1e-6)
    assert keep.shape == xvalues.shape


def test_robust_polyfit_raises_for_insufficient_points() -> None:
    """Robust polyfit should raise if there are too few points to fit."""
    xvalues = np.array([0.0, 1.0])
    yvalues = np.array([0.0, 1.0])
    try:
        gen_math.robust_polyfit(xvalues, yvalues, degree=2, nsigcut=4.0)
    except Exception as exc:  # noqa: BLE001
        assert 'Not enough' in str(exc)
    else:
        raise AssertionError('Expected an exception for insufficient points')


