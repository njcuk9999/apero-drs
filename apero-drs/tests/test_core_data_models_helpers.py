#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for helper behavior in ``apero.core.drs_data_models``."""

import astropy.units as uu
import pytest

from apero.core import drs_data_models


# =============================================================================
# Define functions
# =============================================================================
def test_apero_table_model_create_table_sets_units_and_description() -> None:
    """`create_table` should build columns with model metadata."""
    model = drs_data_models.AperoTableModel('EXT')
    model.add_column('flux', units=1 * uu.electron,
                     description='Flux values')
    model.add_column('wave', units=1 * uu.nm, description='Wavelength')

    table = model.create_table(flux=[1.0, 2.0], wave=[1000.0, 1001.0])

    assert table.colnames == ['flux', 'wave']
    assert table['flux'].unit == uu.electron
    assert table['wave'].unit == uu.nm
    assert table['flux'].description == 'Flux values'


def test_apero_table_model_create_table_requires_all_columns() -> None:
    """Missing required column should raise an exception."""
    model = drs_data_models.AperoTableModel('EXT')
    model.add_column('flux')
    model.add_column('wave')

    with pytest.raises(Exception):
        model.create_table(flux=[1.0, 2.0])


def test_data_model_getstate_setstate_round_trip() -> None:
    """State helpers should serialize and restore model attributes."""
    model = drs_data_models.AperoImageModel('SCI', shape=[2048, 2048])

    state = model.__getstate__()

    restored = drs_data_models.AperoImageModel('TMP')
    restored.__setstate__(state)

    assert restored.name == 'SCI'
    assert restored.datatype == 'image'
    assert restored.shape == [2048, 2048]


