#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for bad pixel detection science functions."""

import numpy as np
import pytest

from aperocore.science.calib import badpix_core


# =============================================================================
# Define functions
# =============================================================================
def test_normalise_median_flat_constant_image() -> None:
    """A constant image should normalise to (approximately) unity."""
    image = np.full((20, 20), 500.0)
    image_med, image_norm = badpix_core.normalise_median_flat(
        image, wmed=5, percentile=90.0)
    assert image_med.shape == image.shape
    assert image_norm.shape == image.shape
    assert np.allclose(image_med, 1.0)
    assert np.allclose(image_norm, 1.0)


def test_normalise_median_flat_old_method_matches_new() -> None:
    """The 'old' sorting-based method should agree with 'new' for a
    constant image."""
    image = np.full((10, 10), 200.0)
    med_new, norm_new = badpix_core.normalise_median_flat(
        image, wmed=3, percentile=90.0, method='new')
    med_old, norm_old = badpix_core.normalise_median_flat(
        image, wmed=3, percentile=90.0, method='old')
    assert np.allclose(med_new, med_old)
    assert np.allclose(norm_new, norm_old)


def test_locate_bad_pixels_flags_hot_and_deviant_pixels() -> None:
    """Hot dark pixels and deviant flat pixels should be flagged bad."""
    shape = (10, 10)
    fmed = np.full(shape, 1.0)
    fimage = np.full(shape, 1.0)
    dimage = np.zeros(shape)
    # make one flat pixel deviate strongly from the median
    fimage[3, 3] = 5.0
    # make one dark pixel very hot
    dimage[7, 7] = 1000.0
    badpix_map, stats = badpix_core.locate_bad_pixels(
        fimage, fmed, dimage, wmed=3, cut_ratio=0.1, illum_cut=0.1,
        max_hotpix=100.0)
    assert badpix_map.shape == shape
    assert badpix_map[3, 3]
    assert badpix_map[7, 7]
    assert not badpix_map[0, 0]
    assert len(stats) == 5


def test_locate_bad_pixels_shape_mismatch_raises() -> None:
    """A flat/dark shape mismatch should raise a ValueError."""
    fimage = np.zeros((5, 5))
    fmed = np.zeros((5, 5))
    dimage = np.zeros((4, 4))
    with pytest.raises(ValueError):
        badpix_core.locate_bad_pixels(fimage, fmed, dimage, wmed=3,
                                      cut_ratio=0.1, illum_cut=0.1,
                                      max_hotpix=100.0)


def test_full_flat_badpix_mask_identity_rotation() -> None:
    """With no rotation, pixels far from unity should be flagged bad."""
    mdata = np.ones((6, 6))
    mdata[2, 2] = 5.0
    mask = badpix_core.full_flat_badpix_mask(mdata, rotnum=0, threshold=0.5)
    assert mask.shape == mdata.shape
    assert mask[2, 2]
    assert not mask[0, 0]
