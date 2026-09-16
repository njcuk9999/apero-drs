#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for order extraction science functions."""

import numpy as np
import pytest

from aperocore.science.extract import extract_core


# =============================================================================
# Define functions
# =============================================================================
def test_extraction_recovers_flat_flux() -> None:
    """Extracting a flat order (image is the order profile scaled by a
    constant true flux, plus tiny noise) should recover that true flux
    level with very few cosmic rays found."""
    rng = np.random.default_rng(0)
    dim1, dim2 = 20, 30
    true_flux = 100.0
    orderp = np.zeros((dim1, dim2))
    # profile window matching r1=2, r2=2 around pos=10 (rows 8..12)
    orderp[8:13, :] = 0.2
    simage = true_flux * orderp + rng.normal(0, 0.01, (dim1, dim2))
    # constant chebyshev coefficients centered at row 10
    pos = np.array([10.0])
    spe, spelong, cpt, coslong = extract_core.extraction(
        simage, orderp, pos, r1=2.0, r2=2.0, cosmic_sigcut=5.0)
    assert spe.shape == (dim2,)
    assert spelong.shape[1] == dim2
    assert coslong.shape == spelong.shape
    assert cpt == 0
    assert np.allclose(spe, true_flux, atol=0.5)


def test_calculate_snr_higher_flux_gives_higher_snr() -> None:
    """A brighter order should have a higher SNR than a fainter one for
    the same noise."""
    e2ds_faint = np.full(100, 50.0)
    e2ds_bright = np.full(100, 500.0)
    snr_faint, flux_faint = extract_core.calculate_snr(
        e2ds_faint, blaze_width=10, r1=2, r2=2, eff_ron=5.0)
    snr_bright, flux_bright = extract_core.calculate_snr(
        e2ds_bright, blaze_width=10, r1=2, r2=2, eff_ron=5.0)
    assert flux_bright > flux_faint
    assert snr_bright > snr_faint


def test_cosmic_correction_reduces_outlier_influence() -> None:
    """Cosmic correction should adjust the extracted value away from a
    single very large outlier pixel."""
    sx = np.array([10.0, 10.0, 1.0e5, 10.0, 10.0])
    fx = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    weights = np.ones_like(sx)
    spe = np.array([1.0])
    spe_out, cpt = extract_core.cosmic_correction(
        sx, spe, fx, ic=0, weights=weights, cpt=0, cosmic_sigcut=5.0,
        cosmic_threshold=10)
    assert cpt >= 1
    assert spe_out[0] < 1.0e4


def test_valid_orders_skips_requested_orders() -> None:
    """valid_orders should include start..end but exclude skip_orders."""
    orders = extract_core.valid_orders(0, 5, skip_orders=[2, 4])
    assert orders == [0, 1, 3, 5]


def test_valid_orders_raises_on_bad_range() -> None:
    """start_order greater than end_order should raise ValueError."""
    with pytest.raises(ValueError):
        extract_core.valid_orders(5, 2)


def test_get_range_returns_value_for_fiber() -> None:
    """get_range should return the float value for the requested fiber."""
    rangedict = {'AB': 10, 'A': '5.5'}
    assert extract_core.get_range(rangedict, 'AB') == 10.0
    assert extract_core.get_range(rangedict, 'A') == 5.5


def test_get_range_raises_for_missing_fiber() -> None:
    """get_range should raise ValueError if fiber is not in rangedict."""
    with pytest.raises(ValueError):
        extract_core.get_range({'AB': 10}, 'C')


def test_measure_p2p_scat_returns_expected_keys() -> None:
    """measure_p2p_scat should return MP2P and BP2P (per-band) entries."""
    rng = np.random.default_rng(0)
    wavemap = np.array([np.linspace(1000.0, 1010.0, 50),
                       np.linspace(1010.0, 1020.0, 50),
                       np.linspace(1020.0, 1030.0, 50)])
    e2ds = 1000.0 + rng.normal(0, 5.0, (3, 50))
    bands = {'band1': (995.0, 1015.0), 'band2': (1015.0, 1035.0)}
    sprops = extract_core.measure_p2p_scat(wavemap, e2ds, blaze_width=10,
                                           bands=bands)
    assert 'MP2P' in sprops
    assert sprops['MP2P'].shape == (3,)
    assert set(sprops['BP2P'].keys()) == {'band1', 'band2'}
