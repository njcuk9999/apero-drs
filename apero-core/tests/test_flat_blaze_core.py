#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for flat and blaze calibration science functions."""

import numpy as np

from aperocore import math as mp
from aperocore.science.calib import flat_blaze_core


# =============================================================================
# Define functions
# =============================================================================
def _synthetic_order(npix: int = 200, amp: float = 1000.0,
                     period: float = 80.0, center: float = 100.0
                     ) -> np.ndarray:
    """Build a noiseless sinc-shaped order profile for testing."""
    xpix = np.arange(npix, dtype=float)
    return mp.sinc(xpix, amp, period, center, 0.0)


def test_calculate_blaze_flat_sinc_recovers_flat_profile() -> None:
    """Fitting a noiseless sinc order should give a flat close to unity."""
    e2ds = _synthetic_order() + 1.0
    e2ds_out, flat, blaze, rms = flat_blaze_core.calculate_blaze_flat_sinc(
        e2ds, peak_cut=0.3, badpercentile=95.0, med_size=5)
    assert e2ds_out.shape == e2ds.shape
    assert flat.shape == e2ds.shape
    assert blaze.shape == e2ds.shape
    # away from the cut edges, flat should be close to 1
    finite = np.isfinite(flat)
    assert finite.sum() > 30
    assert np.nanmax(np.abs(flat[finite] - 1.0)) < 0.05
    assert rms < 0.05


def test_flux_edge_trace_low_edge_flux_for_smooth_order() -> None:
    """A well-behaved order with a smooth peak in the middle should have
    low edge flux and no failed orders."""
    norders = 3
    profile = _synthetic_order(npix=100, center=50.0) + 1.0
    e2dsll = np.tile(profile, (norders * 4, 1))
    e2ds = np.zeros((norders, 10))
    med, flux_edge, max_edge_flux, failed_orders = \
        flat_blaze_core.flux_edge_trace(e2ds, e2dsll, mid_size=5,
                                        ignore_orders=[], flux_edge_limit=0.5)
    assert med.shape == (norders, 4)
    assert flux_edge.shape == (norders,)
    assert max_edge_flux == np.nanmax(flux_edge)
    assert failed_orders == []


def test_flux_edge_trace_ignores_requested_orders() -> None:
    """Orders in ignore_orders should be set to NaN and excluded from the
    failed orders list even if their raw edge flux would be high."""
    norders = 2
    e2dsll = np.zeros((norders * 4, 1))
    # give the profile a big edge (index 0 and last) contribution
    e2dsll[:, 0] = 1.0
    e2ds = np.zeros((norders, 10))
    med, flux_edge, max_edge_flux, failed_orders = \
        flat_blaze_core.flux_edge_trace(e2ds, e2dsll, mid_size=1,
                                        ignore_orders=[0],
                                        flux_edge_limit=0.1)
    assert np.isnan(flux_edge[0])
    assert 0 not in failed_orders


def test_compute_flat_response_uses_grouped_fibers() -> None:
    """Grouped traces should yield A, B, AB, and C responses."""
    ncols = 60
    order_map = np.zeros((8, ncols), dtype=int)
    order_map[1, :] = 1
    order_map[2, :] = 2
    order_map[3, :] = 3
    order_map[4, :] = 4
    order_map[6, :] = 5
    order_map[7, :] = 6
    xmap = np.tile(np.arange(ncols, dtype=float), (8, 1))
    profile = np.zeros((8, ncols), dtype=float)
    profile[1, :] = 10.0
    profile[2, :] = 20.0
    profile[3, :] = 11.0
    profile[4, :] = 21.0
    profile[6, :] = 7.0
    profile[7, :] = 8.0
    profiles_noshape = dict(AB=profile, C=profile)
    order_ranges = dict(AB=(1, 4), C=(5, 6))
    spectral_groups = [
        ('A', [[1], [3]]),
        ('B', [[2], [4]]),
        ('AB', [[1, 2], [3, 4]]),
        ('C', [[5], [6]])]

    frout = flat_blaze_core.compute_flat_response(
        order_map, xmap, profiles_noshape, order_ranges, ron=1.0,
        oversampling=2, max_half_cell=4.0, fwhm_pix=2.0,
        spectral_groups=spectral_groups)
    flat_response, flat_response_err = frout

    assert list(flat_response.keys()) == ['A', 'B', 'AB', 'C']
    assert flat_response['A'].shape == (2, ncols)
    assert flat_response['B'].shape == (2, ncols)
    assert flat_response['AB'].shape == (2, ncols)
    assert flat_response['C'].shape == (2, ncols)
    assert flat_response_err['AB'].shape == (2, ncols)

    med_a = np.nanmedian(flat_response['A'], axis=1)
    med_b = np.nanmedian(flat_response['B'], axis=1)
    med_ab = np.nanmedian(flat_response['AB'], axis=1)
    med_c = np.nanmedian(flat_response['C'], axis=1)

    assert np.allclose(med_a, [10.0, 11.0], atol=1e-5)
    assert np.allclose(med_b, [20.0, 21.0], atol=1e-5)
    assert np.allclose(med_ab, med_a + med_b, atol=1e-5)
    assert np.allclose(med_c, [7.0, 8.0], atol=1e-5)

