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
