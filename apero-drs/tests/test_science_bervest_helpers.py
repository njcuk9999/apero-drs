#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for pure helper functions in ``apero.science.extract.bervest``."""

import datetime
from typing import Any

import numpy as np
import pytest

from apero.science.extract import bervest


# =============================================================================
# Define functions
# =============================================================================
def test_idl_mod_handles_scalar_and_array_negative_values() -> None:
    """`idl_mod` should mimic IDL modulo behavior for negatives."""
    scalar = bervest.idl_mod(-6, 5)
    array_input: Any = np.array([-1, 6, -11])
    array = bervest.idl_mod(array_input, 5)

    assert scalar == -1
    assert np.array_equal(array, np.array([-1, 1, -1]))


def test_daycnv_matches_documented_example_for_julian_date() -> None:
    """`daycnv` should reproduce the documented 2440000 conversion."""
    year, month, day, hour = bervest.daycnv(2440000.0, mode='idl')

    assert year == 1968
    assert month == 5
    assert day == 23
    assert np.isclose(hour, 12.0)


def test_daycnv_supports_dtlist_and_datetime_modes_for_iterables() -> None:
    """`daycnv` should return list/datetime outputs for supported modes."""
    dtlist = bervest.daycnv([2440000.0, 2440001.0], mode='dtlist')
    dtime = bervest.daycnv(2440000.0, mode='dt')

    assert len(dtlist) == 2
    assert len(dtlist[0]) == 7
    assert isinstance(dtime, datetime.datetime)
    assert dtime.year == 1968
    assert dtime.month == 5


def test_daycnv_invalid_mode_raises_value_error() -> None:
    """Unknown modes should raise a ``ValueError`` with guidance."""
    with pytest.raises(ValueError):
        bervest.daycnv(2440000.0, mode='bad_mode')

