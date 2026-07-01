#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for helper functions in `apero.io.drs_table`."""

import numpy as np
import pytest
from astropy.table import Table

from apero.io import drs_table


def test_make_table_constructs_expected_columns() -> None:
    """`make_table` should build a table with provided columns and values."""
    cols = ['A', 'B']
    vals = [[1, 2], [3, 4]]
    table = drs_table.make_table(cols, vals)
    assert table.colnames == cols
    assert table['A'].tolist() == [1, 2]


def test_make_table_raises_for_length_mismatch() -> None:
    """`make_table` should fail when columns and value lists mismatch."""
    with pytest.raises(Exception):
        drs_table.make_table(['A', 'B'], [[1, 2]])


def test_vstack_cols_empty_and_single_cases() -> None:
    """Stack helper should return None for empty and identity for single."""
    assert drs_table.vstack_cols([]) is None
    one = Table({'X': [1], 'Y': [2]})
    assert drs_table.vstack_cols([one]) is one


def test_vstack_cols_merges_tables_and_rows() -> None:
    """Stack helper should combine both Table and Row inputs."""
    t1 = Table({'X': [1, 2], 'Y': [3, 4]})
    row = t1[0]
    out = drs_table.vstack_cols([t1, row])
    assert len(out) == 3
    assert out['X'].tolist() == [1, 2, 1]


def test_force_dtype_col_current_string_bug_raises_type_error() -> None:
    """Current implementation raises TypeError due STRINGS check logic."""
    with pytest.raises(TypeError):
        drs_table.force_dtype_col(['a', 'b'], dtype=str)


def test_prep_merge_keeps_required_columns_and_types() -> None:
    """`prep_merge` should coerce dtypes to match template table dtypes."""
    parent = Table({'A': np.array([1, 2], dtype=int),
                    'B': np.array([0.5, 1.5], dtype=float)})
    template = Table({'A': np.array([0], dtype=float),
                      'B': np.array([0], dtype=float)})
    out = drs_table.prep_merge({}, 'f.fits', parent, template)
    assert out['A'].dtype == template['A'].dtype
    assert out['B'].dtype == template['B'].dtype


def test_prep_merge_raises_when_column_missing() -> None:
    """`prep_merge` should raise if source table lacks template column."""
    parent = Table({'A': [1, 2]})
    template = Table({'A': [1], 'B': [2]})
    with pytest.raises(Exception):
        drs_table.prep_merge({}, 'f.fits', parent, template)


def test_list_of_formats_contains_read_and_write_flags() -> None:
    """Formats table should include bool convenience columns."""
    ftable = drs_table.list_of_formats()
    assert 'read?' in ftable.colnames
    assert 'write?' in ftable.colnames


def test_string_formats_applies_mask() -> None:
    """String formatter should include only rows where mask is True."""
    ftable = Table({'Format': ['f1', 'f2', 'f3']})
    mask = np.array([True, False, True])
    out = drs_table.string_formats(ftable=ftable, mask=mask)
    assert 'f1' in out and 'f3' in out
    assert 'f2' not in out

