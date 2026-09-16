#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for telluric science functions."""

import numpy as np

from aperocore.science.telluric import telluric_core


# =============================================================================
# Define functions
# =============================================================================
def test_normalise_by_pblaze_flat_case() -> None:
    """A spectrum that is a constant multiple of the blaze should
    normalise to that same constant (both are percentile-normalised
    the same way, so the multiple cancels to 1 here since image =
    2 * blaze normalises to blaze_norm = blaze/pct and image/pct(image)
    = 2*blaze/(2*pct(blaze)) - same as blaze_norm)."""
    norders, npix = 3, 50
    xpix = np.arange(npix, dtype=float)
    blaze = 100.0 * np.exp(-((xpix - 25) ** 2) / (2 * 15.0 ** 2)) + 1.0
    blaze = np.tile(blaze, (norders, 1))
    image = blaze * 2.0
    image1, blaze_norm = telluric_core.normalise_by_pblaze(
        image, blaze, blaze_p=90.0, cut_blaze_norm=0.1)
    assert image1.shape == image.shape
    assert blaze_norm.shape == blaze.shape
    finite = np.isfinite(image1)
    assert finite.sum() > 0
    assert np.allclose(image1[finite], 1.0, atol=0.05)


def test_normalise_by_pblaze_cuts_low_blaze() -> None:
    """Pixels where the normalised blaze is below the cut should become
    NaN in both outputs."""
    image = np.full((1, 10), 10.0)
    blaze = np.full((1, 10), 1.0)
    blaze[0, :3] = 0.01
    image1, blaze_norm = telluric_core.normalise_by_pblaze(
        image, blaze, blaze_p=90.0, cut_blaze_norm=0.5)
    assert np.all(np.isnan(blaze_norm[0, :3]))
    assert np.all(np.isnan(image1[0, :3]))


def test_make_trans_model_recovers_known_amplitudes() -> None:
    """Fitting a noiseless linear model (bias + water + others) should
    recover the known amplitudes."""
    rng = np.random.default_rng(0)
    ntrans = 10
    expo_water = rng.uniform(0.5, 1.5, ntrans)
    expo_others = rng.uniform(0.5, 1.5, ntrans)
    true_bias, true_water_amp, true_others_amp = 0.1, 0.5, 0.3
    trans_slice = (true_bias + true_water_amp * expo_water
                  + true_others_amp * expo_others)
    transcube = np.zeros((1, 1, ntrans))
    transcube[0, 0, :] = trans_slice
    zero_res, water_res, others_res = telluric_core.make_trans_model(
        transcube, expo_water, expo_others, sigma_cut=5.0,
        min_trans_files=3)
    assert np.isclose(zero_res[0, 0], true_bias, atol=1e-6)
    assert np.isclose(water_res[0, 0], true_water_amp, atol=1e-6)
    assert np.isclose(others_res[0, 0], true_others_amp, atol=1e-6)


def test_make_trans_model_skips_insufficient_points() -> None:
    """A pixel with fewer finite points than min_trans_files should be
    left as NaN."""
    expo_water = np.array([1.0, 1.1])
    expo_others = np.array([1.0, 1.1])
    transcube = np.zeros((1, 1, 2))
    transcube[0, 0, :] = [1.0, 1.1]
    zero_res, water_res, others_res = telluric_core.make_trans_model(
        transcube, expo_water, expo_others, sigma_cut=5.0,
        min_trans_files=3)
    assert np.isnan(zero_res[0, 0])


def test_identify_sky_line_regions_finds_a_line() -> None:
    """A single strong emission line embedded in noise should be
    identified as a non-zero region."""
    rng = np.random.default_rng(0)
    npix = 200
    wave1d = np.linspace(1000.0, 1010.0, npix)
    sky_med = rng.normal(0, 1.0, npix)
    sky_med[95:105] += 50.0
    regions = telluric_core.identify_sky_line_regions(
        wave1d, sky_med, line_sigma=5.0, erode_size=1, dilate_size=2,
        wavestart=1000.0, waveend=1010.0, binvelo=2.0)
    assert regions.shape == wave1d.shape
    assert np.any(regions[95:105] != 0)
    assert np.all(regions[:20] == 0)
