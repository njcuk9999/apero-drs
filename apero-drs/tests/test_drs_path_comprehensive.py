#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for DRS path construction with developer default parameters."""

import os

from apero.core import drs_file


# =============================================================================
# Define functions
# =============================================================================
def test_drspath_lists_raw_block_for_dev_parameters(spirou_params) -> None:
    """Developer parameters should construct the configured raw block."""
    drspath = drs_file.DrsPath(spirou_params, block_kind='raw', check=False)

    assert drspath.block_name == 'raw'
    assert drspath.block_name in drspath.block_names()
    assert str(drspath) == 'DrsPath[RAW][BLOCK]'


def test_strip_path_removes_configured_block_prefix(spirou_params) -> None:
    """Configured block prefixes should be removed from paths exactly once."""
    drspath = drs_file.DrsPath(spirou_params, block_kind='raw', check=False)
    filename = os.path.join(drspath.block_path, '2026-01-01', 'raw.fits')

    stripped, found = drs_file.DrsPath.strip_path(spirou_params, filename)

    assert found
    assert stripped == os.path.join('2026-01-01', 'raw.fits')


# =============================================================================
# End of code
# =============================================================================

