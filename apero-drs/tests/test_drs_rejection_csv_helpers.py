#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for CSV read/write helpers in `apero.core.drs_rejection`."""

from pathlib import Path

import pandas as pd

from apero.core import drs_rejection


def _make_row(identifier: str, comment: str, used: int) -> dict:
    """Build a row dict matching rejection CSV schema."""
    return {
        'IDENTIFIER': identifier,
        'DATE_ADDED': '2026-06-30T00:00:00',
        'PP': 1,
        'TEL': 0,
        'RV': 1,
        'USED': used,
        'WHO': 'tester',
        'LAST_UPDATE': '2026-06-30T00:00:00',
        'COMMENT': comment,
    }


def test_read_csv_missing_file_returns_empty_schema(tmp_path) -> None:
    """Reading a missing reject CSV should return empty typed dataframe."""
    csv_path = tmp_path / 'missing.csv'
    df = drs_rejection._read_csv(str(csv_path))
    assert list(df.columns) == drs_rejection.CSV_COLUMNS
    assert len(df) == 0


def test_read_csv_coerces_ints_and_deduplicates_identifier(tmp_path) -> None:
    """Reader should coerce integer fields and keep last duplicate ID row."""
    csv_path = tmp_path / 'reject.csv'
    rows = [
        {
            'IDENTIFIER': 'OBJ1',
            'DATE_ADDED': 'd1',
            'PP': '1',
            'TEL': '0',
            'RV': '1',
            'USED': '0',
            'COMMENT': 'old',
        },
        {
            'IDENTIFIER': 'OBJ1',
            'DATE_ADDED': 'd2',
            'PP': '2',
            'TEL': '1',
            'RV': '0',
            'USED': '1',
            'COMMENT': 'new',
        },
    ]
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    df = drs_rejection._read_csv(str(csv_path))
    assert len(df) == 1
    assert int(df.iloc[0]['PP']) == 2
    assert int(df.iloc[0]['USED']) == 1
    assert str(df.iloc[0]['COMMENT']) == 'new'


def test_write_csv_enforces_schema_and_deduplicates(tmp_path) -> None:
    """Writer should keep only schema columns and last duplicate ID."""
    csv_path = tmp_path / 'x' / 'reject.csv'
    rows = [
        _make_row('OBJ2', 'first', 0),
        _make_row('OBJ2', 'second', 1),
        _make_row('OBJ3', 'other', 1),
    ]
    df = pd.DataFrame(rows)
    df['EXTRA'] = 'ignore'
    drs_rejection._write_csv(str(csv_path), df)
    out = pd.read_csv(csv_path, dtype=str)
    assert list(out.columns) == drs_rejection.CSV_COLUMNS
    # OBJ2 deduplicated to last row and OBJ3 kept.
    assert len(out) == 2
    obj2 = out[out['IDENTIFIER'] == 'OBJ2'].iloc[0]
    assert obj2['COMMENT'] == 'second'


