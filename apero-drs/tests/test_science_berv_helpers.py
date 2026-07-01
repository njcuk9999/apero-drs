#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for helper logic in `apero.science.extract.berv`."""

import numpy as np

from apero.science.extract import berv


# =============================================================================
# Define functions
# =============================================================================
def _base_props() -> berv.ParamDict:
    """Create a minimal BERV property dictionary for branch tests."""
    props = berv.ParamDict()
    props['BERV'] = np.nan
    props['BERV_MAX'] = np.nan
    props['BJD'] = np.nan
    props['BERV_EST'] = np.nan
    props['BJD_EST'] = np.nan
    props['BERV_MAX_EST'] = np.nan
    props['BERVSOURCE'] = 'None'
    return props


def test_assign_use_berv_prefers_barycorrpy_when_present() -> None:
    """If full barycorrpy values exist, `USE_*` should come from them."""
    props = _base_props()
    props['BERV'] = 1.25
    props['BJD'] = 2450000.5
    props['BERV_MAX'] = 3.0
    props['BERVSOURCE'] = 'barycorrpy'

    out = berv.assign_use_berv(props, use=True)

    assert out['USE_BERV'] == 1.25
    assert out['USE_BJD'] == 2450000.5
    assert out['USE_BERV_MAX'] == 3.0
    assert out['USED_ESTIMATE'] is False


def test_assign_use_berv_falls_back_to_estimate_when_needed() -> None:
    """When barycorrpy values are missing, estimate values should be selected."""
    props = _base_props()
    props['BERV_EST'] = -2.5
    props['BJD_EST'] = 2451111.1
    props['BERV_MAX_EST'] = 4.5

    out = berv.assign_use_berv(props, use=True)

    assert out['USE_BERV'] == -2.5
    assert out['USE_BJD'] == 2451111.1
    assert out['USE_BERV_MAX'] == 4.5
    assert out['USED_ESTIMATE'] is True


def test_assign_use_berv_returns_none_when_use_is_false() -> None:
    """When disabled, selected BERV values should be set to None."""
    props = _base_props()
    props['BERV'] = 1.0
    props['BJD'] = 2450001.0
    props['BERV_MAX'] = 2.0

    out = berv.assign_use_berv(props, use=False)

    assert out['USE_BERV'] is None
    assert out['USE_BJD'] is None
    assert out['USE_BERV_MAX'] is None
    assert out['USED_ESTIMATE'] is True

