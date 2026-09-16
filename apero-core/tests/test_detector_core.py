#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for preprocessing detector science functions."""

import numpy as np

from aperocore.science.preprocessing import detector_core


# =============================================================================
# Define functions
# =============================================================================
def test_ref_top_bottom_removes_constant_offset() -> None:
    """A constant top/bottom reference level should be subtracted evenly
    across the image (via the linear y-weighting)."""
    dim1, dim2 = 20, 16
    image = np.zeros((dim1, dim2))
    image[:4, :] = 5.0
    image[-4:, :] = 15.0
    corrected = detector_core.ref_top_bottom(image.copy(), tamp=2, ntop=4,
                                             nbottom=4)
    assert corrected.shape == image.shape
    # top rows should be reduced towards zero relative to the reference
    assert corrected[-1, 0] < image[-1, 0]


def test_correct_cosmics_flags_a_hot_pixel() -> None:
    """A single very hot pixel (large error slope) should be flagged as a
    bad pixel and set to NaN."""
    rng = np.random.default_rng(0)
    shape = (40, 40)
    image = 100.0 + rng.normal(0, 1.0, shape)
    intercept = rng.normal(0, 1.0, shape)
    errslope = np.full(shape, 1.0)
    # inject an extreme outlier in errslope well away from the edges
    errslope[20, 20] = 500.0
    inttime = np.ones(shape)
    outs = detector_core.correct_cosmics(
        image.copy(), intercept.copy(), errslope.copy(), inttime, tamp=2,
        ntop=4, nbottom=4, readout_noise=5.0, variance_cut1=3.0,
        variance_cut2=5.0, intercept_cut1=9.0, intercept_cut2=16.0,
        intboxsize=4)
    corrected_image, num_bad_intercept, num_bad_slope, num_bad_both = outs
    assert corrected_image.shape == shape
    assert np.isnan(corrected_image[20, 20])
    assert num_bad_slope >= 1
    assert num_bad_intercept >= 0
    assert num_bad_both >= 0
