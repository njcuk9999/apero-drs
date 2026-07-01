#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `uniform_time_list` in `apero.utils.drs_utils`."""

import numpy as np

from apero.utils import drs_utils


def test_uniform_time_list_returns_all_true_when_shorter_than_target() -> None:
    """If times already <= requested count, mask should be all True."""
    times = np.array([1.0, 2.0, 3.0])
    mask = drs_utils.uniform_time_list(times, number=5)
    assert mask.dtype == bool
    assert mask.tolist() == [True, True, True]


def test_uniform_time_list_returns_requested_number_of_points() -> None:
    """Mask should contain exactly `number` True values when trimming."""
    times = np.array([0.0, 0.1, 0.2, 1.0, 2.0, 3.0, 4.0])
    mask = drs_utils.uniform_time_list(times, number=4)
    assert int(np.sum(mask)) == 4


def test_uniform_time_list_with_unsorted_input_preserves_mask_shape() -> None:
    """Function should handle unsorted inputs and return aligned mask."""
    times = np.array([5.0, 1.0, 3.0, 2.0, 4.0])
    mask = drs_utils.uniform_time_list(times, number=3)
    assert mask.shape == times.shape
    assert mask.dtype == bool

