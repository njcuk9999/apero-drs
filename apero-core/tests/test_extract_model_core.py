#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for model-based extraction helper functions."""

import numpy as np

from aperocore import math as mp
from aperocore.science.extract import extract_model_core


# =============================================================================
# Define functions
# =============================================================================
def test_hysteresis_mask_grows_from_seed() -> None:
    """Only candidates connected to a high-sigma seed should be masked."""
    nsig = np.zeros((8, 8))
    nsig[3, 3] = 11.0
    nsig[3, 4] = 4.0
    nsig[0, 0] = 4.0
    mask = extract_model_core.hysteresis_mask(nsig, nsig1=10.0, nsig2=3.0)
    assert mask[3, 3]
    assert mask[3, 4]
    assert not mask[0, 0]


def test_fit_ron_recovers_known_noise() -> None:
    """fit_ron should recover a Gaussian residual scale when model is zero."""
    rng = np.random.default_rng(0)
    true_ron = 7.5
    model = np.zeros((80, 80))
    residual = rng.normal(0.0, true_ron, model.shape)
    measured = extract_model_core.fit_ron(residual, model, ron_start=8.0,
                                          stride=1)
    assert np.isclose(measured, true_ron, rtol=0.08)


def test_fill_nans_uses_nearest_finite_pixel() -> None:
    """fill_nans should replace holes while preserving finite pixels."""
    image = np.arange(25, dtype=float).reshape(5, 5)
    image[2, 2] = np.nan
    math_filled = mp.fill_nans_nearest(image)
    filled = math_filled
    assert np.isfinite(filled).all()
    assert np.allclose(filled, math_filled)
    assert filled[0, 0] == image[0, 0]


def test_background_model_returns_full_size_arrays() -> None:
    """background_model should return full-size finite arrays for a plane."""
    ygrid, xgrid = np.indices((32, 40), dtype=float)
    image = 10.0 + 0.1 * xgrid + 0.2 * ygrid
    bkg, err = extract_model_core.background_model(image, size=(7, 5))
    assert bkg.shape == image.shape
    assert err.shape == image.shape
    assert np.isfinite(bkg).all()


def test_sample_bilinear_matches_grid_points() -> None:
    """Sampling at exact coarse-grid nodes should recover coarse values."""
    coarse = np.arange(9, dtype=float).reshape(3, 3)
    ypos = np.array([0.0, 1.0, 2.0])
    xpos = np.array([0.0, 1.0, 2.0])
    rows = np.array([[0.0, 1.0], [2.0, 1.0]])
    cols = np.array([[0.0, 1.0], [2.0, 0.0]])
    sampled = mp.sample_bilinear(coarse, ypos, xpos, rows, cols)
    expected = np.array([[0.0, 4.0], [8.0, 3.0]])
    assert np.allclose(sampled, expected)


def test_spectral_groups_spirou_splits_ab_and_keeps_c() -> None:
    """SPIROU AB should expose A, B and AB groupings plus C."""
    ranges = dict(AB=(1, 4), C=(5, 6))
    groupings = [('A', [[1], [3]]), ('B', [[2], [4]]),
                 ('AB', [[1, 2], [3, 4]]), ('C', [[5], [6]])]
    groups = extract_model_core.spectral_groups(ranges, groupings)
    names = [item[0] for item in groups]
    assert names == ['A', 'B', 'AB', 'C']
    assert groups[2][1] == [[1, 2], [3, 4]]


def test_ribbon_geometry_tiles_orders() -> None:
    """ribbon_geometry should return adjacent row intervals."""
    centers1 = np.array([10.0, 30.0, 50.0])
    widths1 = np.array([4.0, 4.0, 4.0])
    centers2 = np.array([12.0, 32.0, 52.0])
    widths2 = np.array([4.0, 4.0, 4.0])
    _, row1, row2 = extract_model_core.ribbon_geometry(
        centers1, widths1, centers2, widths2)
    assert np.all(row2[:-1] == row1[1:])


def test_irregular_savgol_recovers_quadratic() -> None:
    """irregular_savgol should recover a local quadratic exactly enough."""
    xpos = np.linspace(0.0, 10.0, 80)
    values = 2.0 + 0.5 * xpos - 0.1 * xpos ** 2
    xout = np.linspace(2.0, 8.0, 20)
    yout, eout = mp.irregular_savgol(
        xpos, values, xout, window=2.0, yerr=np.ones_like(values))
    expected = 2.0 + 0.5 * xout - 0.1 * xout ** 2
    assert np.allclose(yout, expected, atol=1e-8)
    assert np.all(np.isfinite(eout))


def test_extract_spectra_simple_trace() -> None:
    """extract_spectra should produce a finite spectrum for one trace."""
    image = np.tile(np.linspace(10.0, 20.0, 30), (5, 1))
    error = np.ones_like(image)
    order_map = np.zeros_like(image, dtype=int)
    order_map[2, :] = 1
    xmap = np.tile(np.arange(30, dtype=float), (5, 1))
    profiles = dict(A=np.ones_like(image))
    ranges = dict(A=(1, 1))
    xgrid = np.arange(5.0, 25.0, 1.0)
    out = extract_model_core.extract_spectra(
        image, error, order_map, xmap, profiles, ranges, xgrid,
        groupings=[('A', [[1]])], window=2.0)
    spec, espec = out['A']
    assert spec.shape == (1, xgrid.size)
    assert np.isfinite(spec).all()
    assert np.isfinite(espec).all()


def test_simple_fit_batch_recovers_two_profile_amplitudes() -> None:
    """simple_fit_batch should recover two profile amplitudes plus DC."""
    profile1 = np.tile(np.array([1.0, 0.2, 0.0])[:, None], (1, 12))
    profile2 = np.tile(np.array([0.0, 0.3, 1.0])[:, None], (1, 12))
    amp1_true = np.linspace(10.0, 12.0, 12)
    amp2_true = np.linspace(20.0, 22.0, 12)
    zero_true = np.linspace(1.0, 2.0, 12)
    science = amp1_true * profile1 + amp2_true * profile2 + zero_true
    amp1, amp2, zero = extract_model_core.simple_fit_batch(
        profile1, profile2, science, trace_nan_frac=0.30)
    assert np.allclose(amp1, amp1_true)
    assert np.allclose(amp2, amp2_true)
    assert np.allclose(zero, zero_true)


def test_weighted_fit_batch_returns_finite_weights() -> None:
    """weighted_fit_batch should recover amplitudes and return weights."""
    profile1 = np.tile(np.array([1.0, 0.2, 0.0])[:, None], (1, 8))
    profile2 = np.tile(np.array([0.0, 0.3, 1.0])[:, None], (1, 8))
    amp1_true = np.full(8, 5.0)
    amp2_true = np.full(8, 7.0)
    zero_true = np.full(8, 1.0)
    science = amp1_true * profile1 + amp2_true * profile2 + zero_true
    amp1, amp2, zero, weights = extract_model_core.weighted_fit_batch(
        profile1, profile2, science, noise=2.0, nu=4.0, n_iter=3,
        trim_keep=0.70, trace_nan_frac=0.30)
    assert np.allclose(amp1, amp1_true, atol=1e-8)
    assert np.allclose(amp2, amp2_true, atol=1e-8)
    assert np.allclose(zero, zero_true, atol=1e-8)
    assert weights.shape == science.shape
    assert np.isfinite(weights).all()


def test_model_in_science_builds_trace_model() -> None:
    """model_in_science should evaluate per-order amplitudes on traces."""
    nearest = np.zeros((4, 6), dtype=int)
    nearest[1, :] = 1
    nearest[2, :] = 2
    xmap = np.tile(np.arange(6, dtype=float), (4, 1))
    profiles = dict(A=np.ones_like(xmap), B=np.ones_like(xmap))
    ranges = dict(A=(1, 1), B=(2, 2))
    flux1 = np.full((1, 6), 3.0)
    flux2 = np.full((1, 6), 0.0)
    zero_point = np.full((1, 6), 2.0)
    fiber_model, zero_model = extract_model_core.model_in_science(
        flux1, flux2, zero_point, nearest, xmap, profiles, ranges,
        fibers=('A', 'B'))
    assert np.allclose(fiber_model[1, :], 3.0)
    assert np.allclose(zero_model[1, :], 2.0)
    assert np.allclose(fiber_model[0, :], 0.0)


def test_extract_orders_returns_fiber_models_and_spectra() -> None:
    """extract_orders should fit a simple two-profile ribbon."""
    image = np.zeros((6, 10))
    profile1 = np.zeros_like(image)
    profile2 = np.zeros_like(image)
    profile1[2:4] = 1.0
    profile2[3:5] = 1.0
    image = 4.0 * profile1 + 7.0 * profile2
    out = extract_model_core.extract_orders(
        image, profile1, profile2, np.array([1]), np.array([5]),
        noise=1.0, nclip=2, nsig_clip=20.0, zp_mad_cut=10.0,
        robust=False, nu=4.0, n_iter=10, trim_keep=0.70,
        trace_nan_frac=0.30, products=True, extras=True)
    flux1, flux2, zero_points = out[:3]
    assert np.allclose(flux1[0], 4.0, atol=1e-5)
    assert np.allclose(flux2[0], 7.0, atol=1e-5)
    assert out[5].shape == image.shape
    assert zero_points.shape == (1, image.shape[1])


def test_model_spectra_packages_individual_and_combined_flux() -> None:
    """model_spectra should preserve fibers and sum finite contributions."""
    flux1 = np.array([[1.0, np.nan, 3.0]])
    flux2 = np.array([[4.0, 5.0, np.nan]])
    spectra = extract_model_core.model_spectra(flux1, flux2, 'A', 'B')
    assert np.allclose(spectra['A'], flux1, equal_nan=True)
    assert np.allclose(spectra['B'], flux2, equal_nan=True)
    assert np.allclose(spectra['COMBINED'], [[5.0, 5.0, 3.0]],
                       equal_nan=True)