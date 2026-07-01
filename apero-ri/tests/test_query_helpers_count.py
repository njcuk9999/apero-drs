#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Additional tests for safe COUNT-query construction in query helpers."""

import pytest

from apero_ri.application import query_helpers


TABLE_ACCESS = {
    'FINDEX': {
        'columns': ['KW_RUN_ID', 'NAME', 'OBS_DIR'],
        'table_name': 'findex_table',
    },
    'OTHER': {
        'columns': ['ID', 'FINDEX_ID'],
        'table_name': 'other_table',
    },
}


def test_build_safe_count_query_basic() -> None:
    """Count query should include run-id filtering and return bound params."""
    query_spec = {'tables': [{'label': 'FINDEX'}], 'filters': []}
    sql, params = query_helpers.build_safe_count_query(
        TABLE_ACCESS, query_spec, run_ids=['r2', 'r1']
    )
    assert 'SELECT COUNT(*) AS cnt' in sql
    assert 'KW_RUN_ID' in sql
    assert params['_run_ids'] == ['r1', 'r2']


def test_build_safe_count_query_no_run_ids_returns_zero_query() -> None:
    """No run IDs should collapse to a constant-zero count query."""
    query_spec = {'tables': [{'label': 'FINDEX'}], 'filters': []}
    sql, params = query_helpers.build_safe_count_query(
        TABLE_ACCESS, query_spec, run_ids=[]
    )
    assert sql == 'SELECT 0 AS cnt'
    assert params == {}


def test_build_safe_count_query_supports_join_and_filter() -> None:
    """Join and scalar filters should be represented safely in SQL/params."""
    query_spec = {
        'tables': [{'label': 'FINDEX'}, {'label': 'OTHER'}],
        'joins': [
            {
                'left_label': 'FINDEX',
                'left_col': 'KW_RUN_ID',
                'right_label': 'OTHER',
                'right_col': 'ID',
                'type': 'LEFT',
            }
        ],
        'filters': [
            {
                'table_label': 'FINDEX',
                'column': 'NAME',
                'op': '=',
                'value': 'abc',
            }
        ],
    }
    sql, params = query_helpers.build_safe_count_query(
        TABLE_ACCESS, query_spec, run_ids=['r1']
    )
    assert 'LEFT JOIN' in sql
    assert 'WHERE' in sql
    assert params['p0'] == 'abc'


def test_build_safe_count_query_rejects_invalid_identifier() -> None:
    """Unknown table labels should raise ValueError before SQL generation."""
    query_spec = {'tables': [{'label': 'MISSING'}], 'filters': []}
    with pytest.raises(ValueError):
        query_helpers.build_safe_count_query(
            TABLE_ACCESS, query_spec, run_ids=['r1']
        )


def test_build_safe_count_query_rejects_invalid_operator() -> None:
    """Filter operators outside allowlist should raise ValueError."""
    query_spec = {
        'tables': [{'label': 'FINDEX'}],
        'filters': [
            {
                'table_label': 'FINDEX',
                'column': 'NAME',
                'op': 'DROP',
                'value': 'x',
            }
        ],
    }
    with pytest.raises(ValueError):
        query_helpers.build_safe_count_query(
            TABLE_ACCESS, query_spec, run_ids=['r1']
        )

