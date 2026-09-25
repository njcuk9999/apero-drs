#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for APERO flat/blaze wrapper helpers."""

import numpy as np

from aperocore.constants import param_functions
from apero.science.calib import flat_blaze


ParamDict = param_functions.ParamDict


class _DummyRecipe:
    """Minimal recipe stub for wrapper tests that emit plots."""

    def plot(self, *args, **kwargs) -> None:
        """Accept plot calls without performing any plotting."""
        _ = args, kwargs


# =============================================================================
# Define functions
# =============================================================================
def test_compute_flat_response_uses_model_spectral_groups(
        spirou_params) -> None:
    """Wrapper should mirror grouped extracted fibers, not raw ranges."""
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
    model_props = ParamDict()
    model_props['SCIENCE_XMAP'] = xmap
    model_props['PROFILES_NOSHAPE'] = dict(AB=profile, C=profile)
    model_props['RON'] = 1.0
    model_props['SPECTRAL_GROUPS'] = [
        ('A', [[1], [3]]),
        ('B', [[2], [4]]),
        ('AB', [[1, 2], [3, 4]]),
        ('C', [[5], [6]])]
    order_ranges = dict(AB=(1, 4), C=(5, 6))

    frout = flat_blaze.compute_flat_response(
        spirou_params, _DummyRecipe(), model_props, order_map, order_ranges)
    flat_response, flat_response_err = frout

    assert list(flat_response.keys()) == ['A', 'B', 'AB', 'C']
    assert flat_response['AB'].shape == (2, ncols)
    assert flat_response['A'].shape == (2, ncols)
    assert flat_response['B'].shape == (2, ncols)
    assert flat_response['C'].shape == (2, ncols)
    assert flat_response_err['AB'].shape == (2, ncols)
    assert np.allclose(np.nanmedian(flat_response['AB'], axis=1),
                       [30.0, 32.0], atol=1e-5)

