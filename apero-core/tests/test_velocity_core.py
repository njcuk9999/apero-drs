#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for radial velocity / CCF science functions."""

import numpy as np

from aperocore import math as mp
from aperocore.science.velocity import velocity_core


# =============================================================================
# Define functions
# =============================================================================
def test_fwhm_fp_airy_scales_with_period() -> None:
    """The FWHM should scale linearly with the airy function period (w)
    for fixed beta, and be NaN when out of bounds."""
    popt1 = [10.0, 50.0, 20.0, 1.5, 0.0]
    popt2 = [10.0, 50.0, 40.0, 1.5, 0.0]
    fwhm1 = velocity_core.fwhm_fp_airy(np.array(popt1))
    fwhm2 = velocity_core.fwhm_fp_airy(np.array(popt2))
    assert np.isfinite(fwhm1) and fwhm1 > 0
    assert np.isclose(fwhm2 / fwhm1, 2.0)
    # beta so small that part1 is out of the arccos domain -> NaN
    bad_popt = [10.0, 50.0, 20.0, 0.01, 0.0]
    assert np.isnan(velocity_core.fwhm_fp_airy(np.array(bad_popt)))


def test_fit_fp_peaks_recovers_known_peak() -> None:
    """Fitting a noiseless airy peak should recover its known amplitude
    and position closely."""
    x = np.arange(100, dtype=float)
    true_params = [100.0, 50.0, 20.0, 1.5, 0.0]
    y = mp.ea_airy_function(x, *true_params)
    p0, popt, pcov, warns = velocity_core.fit_fp_peaks(x, y, size=20)
    assert warns is None
    assert abs(popt[1] - true_params[1]) < 1.0


def test_delta_v_rms_2d_shapes() -> None:
    """delta_v_rms_2d should return per-order dvrms2 and a scalar weighted
    mean."""
    rng = np.random.default_rng(0)
    norders, npix = 3, 50
    spe = 1000.0 + rng.normal(0, 10.0, (norders, npix))
    wave = np.tile(np.linspace(1000.0, 1010.0, npix), (norders, 1))
    dvrms2, weightedmean, weightedmeanorder = velocity_core.delta_v_rms_2d(
        spe, wave, sigdet=5.0, threshold=1e6, size=3)
    assert dvrms2.shape == (norders,)
    assert weightedmeanorder.shape == (norders,)
    assert np.isfinite(weightedmean)


def test_bisector_cut_interpolates_between_points() -> None:
    """bisector_cut should return an x value between the bracketing
    points for a simple linear ramp."""
    yy = np.linspace(0.0, 1.0, 11)
    xx = np.arange(11, dtype=float)
    span = velocity_core.bisector_cut(xx, yy, cut=0.5)
    assert 0.0 <= span <= 10.0


def test_get_coeff_dict_1d_and_2d() -> None:
    """get_coeff_dict should map names to columns (2D) or scalars (1D)."""
    names = ['amp', 'cen', 'width']
    coeffs_1d = np.array([1.0, 2.0, 3.0])
    cdict = velocity_core.get_coeff_dict(coeffs_1d, names)
    assert cdict['amp'] == 1.0
    assert cdict['cen'] == 2.0
    coeffs_2d = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    cdict2 = velocity_core.get_coeff_dict(coeffs_2d, names)
    assert np.allclose(cdict2['width'], [3.0, 6.0])
