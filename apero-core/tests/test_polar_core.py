#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for polarimetry science functions."""

import numpy as np

from aperocore.science.polar import polar_core


# =============================================================================
# Define functions
# =============================================================================
def _make_data(nexp: int, npix: int = 10, seed: int = 0):
    """Build synthetic A/B exposure flux and error dicts."""
    rng = np.random.default_rng(seed)
    data, errdata = dict(), dict()
    for exp in range(1, nexp + 1):
        a = 1000.0 + rng.normal(0, 1.0, npix)
        b = 900.0 + rng.normal(0, 1.0, npix)
        data['A_{0}'.format(exp)] = a
        data['B_{0}'.format(exp)] = b
        errdata['A_{0}'.format(exp)] = np.sqrt(a)
        errdata['B_{0}'.format(exp)] = np.sqrt(b)
    return data, errdata


def test_polarimetry_diff_method_shapes_4exp() -> None:
    """The difference method should return arrays matching the exposure
    shape for 4 exposures."""
    data, errdata = _make_data(4)
    pol, polerr, null1, null2 = polar_core.polarimetry_diff_method(
        data, errdata, nexp=4)
    assert pol.shape == (10,)
    assert polerr.shape == (10,)
    assert null1.shape == (10,)
    assert null2.shape == (10,)


def test_polarimetry_diff_method_shapes_2exp() -> None:
    """The difference method should also work for 2 exposures."""
    data, errdata = _make_data(2)
    pol, polerr, null1, null2 = polar_core.polarimetry_diff_method(
        data, errdata, nexp=2)
    assert pol.shape == (10,)
    assert np.all(np.isfinite(pol))


def test_polarimetry_ratio_method_shapes_4exp() -> None:
    """The ratio method should return arrays matching the exposure shape
    for 4 exposures."""
    data, errdata = _make_data(4)
    pol, polerr, null1, null2 = polar_core.polarimetry_ratio_method(
        data, errdata, nexp=4)
    assert pol.shape == (10,)
    assert polerr.shape == (10,)


def test_calculate_stokes_i_sums_fluxes() -> None:
    """Stokes I should be close to the sum of A+B flux over all
    exposures."""
    data, errdata = _make_data(2, seed=1)
    stokesi, stokesierr = polar_core.calculate_stokes_i(data, errdata,
                                                        nexp=2)
    expected = (data['A_1'] + data['B_1']) + (data['A_2'] + data['B_2'])
    assert np.allclose(stokesi, expected)
    assert np.all(stokesierr > 0)


def test_remove_continuum_polarization_subtracts_constant_continuum() -> None:
    """A constant continuum polarization should be removed, leaving the
    polarization signal alone."""
    norders, npix = 2, 20
    wavemap = np.tile(np.linspace(1000.0, 1010.0, npix), (norders, 1))
    stokesi = np.full((norders, npix), 100.0)
    wldata = np.linspace(990.0, 1020.0, 301)
    cont_pol = np.full(301, 0.01)
    pol = np.full((norders, npix), 0.05)
    new_pol, order_cont_pol = polar_core.remove_continuum_polarization(
        wldata, pol.copy(), stokesi, wavemap, cont_pol, reddest_thres=2000.0)
    assert np.allclose(new_pol, 0.04, atol=1e-6)
    assert order_cont_pol.shape == (norders, npix)


def test_normalize_stokes_i_divides_by_continuum() -> None:
    """Stokes I should be divided by a constant continuum flux."""
    norders, npix = 2, 20
    wavemap = np.tile(np.linspace(1000.0, 1010.0, npix), (norders, 1))
    stokesi = np.full((norders, npix), 200.0)
    stokesierr = np.full((norders, npix), 2.0)
    pol = np.full((norders, npix), 0.01)
    wldata = np.linspace(990.0, 1020.0, 301)
    cont_flux = np.full(301, 100.0)
    new_stokesi, new_stokesierr, order_cont_flux = \
        polar_core.normalize_stokes_i(wldata, pol, stokesi, stokesierr,
                                      wavemap, cont_flux,
                                      reddest_thres=2000.0)
    assert np.allclose(new_stokesi, 2.0)
    assert np.allclose(new_stokesierr, 0.02)


def test_clean_polarimetry_data_removes_nans() -> None:
    """clean_polarimetry_data should drop NaN entries and sort by
    wavelength."""
    norders, npix = 2, 5
    wavemap = np.array([[5.0, 4.0, 3.0, 2.0, 1.0],
                        [10.0, 9.0, 8.0, 7.0, 6.0]])
    stokesi = np.ones((norders, npix))
    stokesierr = np.ones((norders, npix)) * 0.1
    pol = np.ones((norders, npix)) * 0.02
    polerr = np.ones((norders, npix)) * 0.01
    null1 = np.ones((norders, npix)) * 0.001
    null2 = np.ones((norders, npix)) * 0.001
    cont_pol = np.ones((norders, npix)) * 0.02
    cont_flux = np.ones((norders, npix)) * 100.0
    # introduce a NaN
    stokesi[0, 0] = np.nan
    outs = polar_core.clean_polarimetry_data(
        wavemap, stokesi, stokesierr, pol, polerr, null1, null2, cont_pol,
        cont_flux)
    clean_wavemap = outs[0]
    # one bad pixel removed out of 10, and sorted ascending
    assert clean_wavemap.size == 9
    assert np.all(np.diff(clean_wavemap) >= 0)
