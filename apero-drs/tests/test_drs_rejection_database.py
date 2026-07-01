#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `RejectDatabase` behavior in `apero.core.drs_rejection`."""

import numpy as np

from apero.core import drs_rejection


def _params(tmp_path):
    """Build a minimal params dict accepted by RejectDatabase."""
    return {'PATH.ASSETS': str(tmp_path), 'INSTRUMENT': 'TEST'}


def test_load_db_initializes_empty_cache(tmp_path) -> None:
    """Loading a missing reject CSV should initialize empty cached frame."""
    db = drs_rejection.RejectDatabase(_params(tmp_path), shortname='T')
    db.load_db()
    df = drs_rejection._DF_CACHE.get(db.path)
    assert df is not None
    assert len(df) == 0


def test_add_entries_and_get_entries_variants(tmp_path) -> None:
    """Database API should support scalar, array, tuple, and frame returns."""
    db = drs_rejection.RejectDatabase(_params(tmp_path), shortname='T')
    db.add_entries(identifier='OBJ1', pp_flag=1, tel_flag=0,
                   rv_flag=1, used=1, comment='c1')
    db.add_entries(identifier='OBJ2', pp_flag=0, tel_flag=0,
                   rv_flag=1, used=1, comment='c2')

    scalar = db.get_entries('IDENTIFIER', nentries=1)
    assert isinstance(scalar, str)

    arr = db.get_entries('IDENTIFIER')
    assert isinstance(arr, np.ndarray)
    assert set(arr.tolist()) == {'OBJ1', 'OBJ2'}

    row = db.get_entries('IDENTIFIER,COMMENT', nentries=1)
    assert isinstance(row, tuple)
    assert len(row) == 2

    frame = db.get_entries('IDENTIFIER,COMMENT')
    assert 'IDENTIFIER' in frame.columns
    assert 'COMMENT' in frame.columns


def test_add_entries_replaces_existing_identifier(tmp_path) -> None:
    """Adding same identifier twice should keep only latest row content."""
    db = drs_rejection.RejectDatabase(_params(tmp_path), shortname='T')
    db.add_entries(identifier='OBJX', used=1, comment='old')
    db.add_entries(identifier='OBJX', used=1, comment='new')
    out = db.get_entries('IDENTIFIER,COMMENT')
    assert len(out) == 1
    assert str(out.iloc[0]['COMMENT']) == 'new'


def test_get_entries_filters_used_flag(tmp_path) -> None:
    """Inactive rows (USED=0) should be filtered out by get_entries."""
    db = drs_rejection.RejectDatabase(_params(tmp_path), shortname='T')
    db.add_entries(identifier='OBJ1', used=0, comment='off')
    db.add_entries(identifier='OBJ2', used=1, comment='on')
    arr = db.get_entries('IDENTIFIER')
    assert arr.tolist() == ['OBJ2']


def test_remove_entries_removes_matching_rows(tmp_path) -> None:
    """Remove API should delete rows matching the pandas eval condition."""
    db = drs_rejection.RejectDatabase(_params(tmp_path), shortname='T')
    db.add_entries(identifier='OBJ1', used=1, comment='c1')
    db.add_entries(identifier='OBJ2', used=1, comment='c2')
    db.remove_entries('IDENTIFIER == "OBJ1"')
    out = db.get_entries('IDENTIFIER')
    assert out.tolist() == ['OBJ2']


def test_add_entries_empty_identifier_raises(tmp_path) -> None:
    """Adding with blank identifier should raise a coded exception."""
    db = drs_rejection.RejectDatabase(_params(tmp_path), shortname='T')
    with np.testing.assert_raises(Exception):
        db.add_entries(identifier='   ')

