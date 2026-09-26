#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for background fitting science functions."""

import numpy as np

from aperocore.science.calib import background_core


# =============================================================================
# Define functions
# =============================================================================
def test_binned_lower_envelope_returns_full_resolution_surface() -> None:
    """A binned fit should evaluate its surface on the original grid."""
    ny, nx = 40, 44
    ygrid = np.linspace(-1.0, 1.0, ny)[:, None]
    xgrid = np.linspace(-1.0, 1.0, nx)[None, :]
    expected = 10.0 + 2.0 * xgrid - 3.0 * ygrid
    image = expected + 0.01 * np.sin(20.0 * xgrid)
    error = np.ones_like(image)
    result = background_core.fit_lower_envelope_2d(
        image, error, xorder=1, yorder=1, f_pos=1.0,
        anneal=(1.0,), niter=5, nbin=(4, 4), bin_size=4)
    assert result['fit'].shape == image.shape
    assert result['nsig'].shape == image.shape
    assert result['ok'].shape == image.shape
    assert np.allclose(result['fit'], expected, atol=0.02)


def test_create_background_map_never_flags_bright_order() -> None:
    """A row of pixels far brighter than its local neighbourhood should
    never be flagged as background."""
    rng = np.random.default_rng(1)
    ny, nx = 40, 32
    profile = 5.0 + rng.normal(0, 0.5, ny)
    profile[15:20] = 100.0
    image = np.tile(profile[:, None], (1, nx))
    badpixmask = np.zeros_like(image, dtype=bool)
    bmask = background_core.create_background_map(
        image, badpixmask, width=8, percent=50.0, csize=3, nbad=3)
    assert bmask.shape == image.shape
    assert np.all(bmask[15:20] == 0)


def test_correct_local_background_matches_constant_input() -> None:
    """A constant image should produce an (almost) constant scattered
    light estimate equal to that constant, away from the edges (the
    kernel convolution uses zero-padding at the image boundary)."""
    image = np.full((256, 256), 42.0)
    scattered = background_core.correct_local_background(
        image, wx_ker=4, wy_ker=4, sig_ker=2)
    assert scattered.shape == image.shape
    assert np.isclose(scattered[128, 128], 42.0)


def test_iterative_box_background_shapes_and_finite() -> None:
    """The full-size background and the binned-down background should
    have the expected shapes and be finite where the image is finite."""
    image = np.full((16, 32), 10.0)
    bfull, bbinned = background_core.iterative_box_background(
        image, width=8, niter=2)
    assert bfull.shape == image.shape
    assert bbinned.shape[0] == image.shape[0]
    assert np.all(np.isfinite(bfull))


def _reference_create_background_map(image, badpixmask, width, percent,
                                     csize, nbad):
    """Reference implementation of create_background_map matching the
    pre-vectorisation behaviour."""
    import warnings
    from scipy.signal import convolve2d
    from aperocore import math as mp
    image0 = np.array(image)
    image0[np.array(badpixmask, dtype=bool)] = np.nan
    backest = np.zeros_like(image0)
    width2 = width // 4
    for x_it in range(0, image0.shape[1], width2):
        ribbon = mp.nanmedian(image0[:, x_it:x_it + width2], axis=1)
        for y_it in range(image0.shape[0]):
            ys = max(0, y_it - width // 2)
            ye = min(image0.shape[0] - 1, y_it + width // 2)
            backest[y_it, x_it:x_it + width2] = mp.nanpercentile(
                ribbon[ys:ye], percent)
    with warnings.catch_warnings(record=True) as _:
        backmask = np.array(image0 < backest, dtype=float)
    nribbon = convolve2d(backmask, np.ones([1, csize]), mode='same')
    backmask[nribbon == 1] = 0
    backmask[nribbon >= nbad] = 1
    return backmask


def test_create_background_map_matches_reference() -> None:
    """The vectorised create_background_map must produce identical
    output to the original per-row loop implementation, including on
    frames sprinkled with NaN pixels."""
    rng = np.random.default_rng(0)
    image = rng.normal(0.0, 50.0, (256, 256)).astype(float)
    image[100:105, :] += 500.0
    # sprinkle NaN pixels to exercise the nan-handling branch
    image[::17, ::19] = np.nan
    badpix = np.zeros_like(image, dtype=bool)
    badpix[10, 10] = True
    new = background_core.create_background_map(
        image, badpix, width=100, percent=5, csize=7, nbad=3)
    ref = _reference_create_background_map(
        image, badpix, width=100, percent=5, csize=7, nbad=3)
    assert np.array_equal(new, ref)