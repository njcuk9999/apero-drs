#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for dark calibration science functions."""

import numpy as np

from aperocore.science.calib import dark_core


# =============================================================================
# Define functions
# =============================================================================
def test_measure_dark_reports_median_and_dead_fraction() -> None:
    """A constant image with some NaNs should report the correct median
    and dead pixel fraction."""
    image = np.full((10, 10), 2.0)
    image[0, :5] = np.nan
    histo, med, dadead, qmin, qmax = dark_core.measure_dark(
        image, dark_qmin=5, dark_qmax=95, histo_bins=10, histo_low=0.0,
        histo_high=4.0)
    assert med == 2.0
    assert qmin == 2.0
    assert qmax == 2.0
    # 5 NaN pixels out of 100
    assert dadead == 5.0
    hist_values, bin_edges = histo
    assert len(bin_edges) == len(hist_values) + 1


def test_measure_dark_badpix_counts_hot_pixels() -> None:
    """Pixels above the cut limit should be counted as bad."""
    image = np.zeros((10, 10))
    image[0, 0] = 100.0
    image[0, 1] = 100.0
    nanmask = np.zeros((10, 10), dtype=bool)
    baddark, dadeadall = dark_core.measure_dark_badpix(
        image, nanmask, darkcutlimit=50.0)
    assert baddark == 2.0
    assert dadeadall == 2.0


def test_measure_dark_badpix_counts_nan_pixels_as_bad() -> None:
    """NaN pixels (even below the cut limit) should count towards
    dadeadall but not towards baddark."""
    image = np.zeros((10, 10))
    nanmask = np.zeros((10, 10), dtype=bool)
    nanmask[0, 0] = True
    baddark, dadeadall = dark_core.measure_dark_badpix(
        image, nanmask, darkcutlimit=50.0)
    assert baddark == 0.0
    assert dadeadall == 1.0


def test_correct_dark_subtracts_scaled_dark() -> None:
    """The dark image scaled by nfiles should be subtracted from image."""
    image = np.full((5, 5), 10.0)
    darkimage = np.full((5, 5), 2.0)
    corrected = dark_core.correct_dark(image, darkimage, nfiles=3)
    assert np.allclose(corrected, 4.0)
