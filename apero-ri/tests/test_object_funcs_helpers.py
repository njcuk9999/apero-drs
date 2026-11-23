#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for helper and builder functions in ``apero_ri.core.object_funcs``."""

import json
from pathlib import Path

from apero_ri.core import object_funcs


# =============================================================================
# Define functions
# =============================================================================
def _write_rows_file(path: Path, rows) -> None:
    """Write a small `{"rows": ...}` JSON payload used by object helpers."""
    path.write_text(
        json.dumps({'rows': rows}),
        encoding='utf-8',
    )


def test_small_numeric_and_collection_helpers_cover_edge_cases() -> None:
    """Small object helper functions should handle mixed-value inputs."""
    rows = [
        {'MID': '2026-01-03'},
        {'MID': '2026-01-01'},
        {'MID': '2026-01-02'},
    ]

    assert object_funcs._is_dict_row({'a': 1})
    assert not object_funcs._is_dict_row(['a'])
    assert object_funcs._first_present({'a': '', 'b': 2}, ['a', 'b']) == 2
    assert object_funcs._safe_float('3.5') == 3.5
    assert object_funcs._safe_float('nan') is None
    assert object_funcs._safe_float('bad') is None
    assert object_funcs._percentile([1.0, 3.0, 5.0], 25) == 2.0
    assert object_funcs._nanmedian([1, 'bad', 3]) == 2.0
    assert object_funcs._mean([1, None, '3']) == 2.0
    assert object_funcs._sum([1, None, '3']) == 4.0
    assert object_funcs._format_number(1.2345, ndp=2) == '1.23'
    assert object_funcs._join_unique(['A', 'a', '', 'B']) == 'A, B'
    assert object_funcs._unique_list(['A', 'a', '', 'None', 'B']) == [
        'A',
        'B',
    ]
    assert object_funcs._min_time(rows, 'MID') == '2026-01-01'
    assert object_funcs._max_time(rows, 'MID') == '2026-01-03'
    assert object_funcs._fmt_count(2, 5) == '2 (5)'
    assert object_funcs._qc_counts([
        {'PASSED_ALL_QC': 1},
        {'PASSED_ALL_QC': 0},
        {},
    ]) == {'total': 3, 'passed': 2, 'failed': 1}


def test_load_json_rows_filters_non_dict_rows_and_uses_cache(
    tmp_path: Path,
) -> None:
    """JSON row loading should filter entries and reuse cached values."""
    path = tmp_path / 'rows.json'
    object_funcs._json_rows_cache.clear()

    _write_rows_file(path, [{'name': 'alpha'}, 5, {'name': 'beta'}])
    first_rows = object_funcs._load_json_rows(path)

    _write_rows_file(path, [{'name': 'gamma'}])
    second_rows = object_funcs._load_json_rows(path)

    assert first_rows == [{'name': 'alpha'}, {'name': 'beta'}]
    assert second_rows == first_rows

    object_funcs._json_rows_cache.clear()


def test_resolve_lbl_path_allows_local_files_and_blocks_traversal(
    tmp_path: Path,
) -> None:
    """LBL path resolution should stay inside the configured base folder."""
    base_dir = tmp_path / 'lbl'
    obs_dir = base_dir / '2026-01-01'
    obs_dir.mkdir(parents=True)
    target = obs_dir / 'lbl_obj_obj.rdb'
    target.write_text('content', encoding='utf-8')

    resolved = object_funcs._resolve_lbl_path(
        str(base_dir),
        '2026-01-01',
        'lbl_obj_obj.rdb',
    )

    assert resolved == target.resolve()
    assert object_funcs._resolve_lbl_path(
        str(base_dir),
        '../escape',
        'lbl_obj_obj.rdb',
    ) is None
    assert object_funcs._resolve_lbl_path('', '2026-01-01', 'file.rdb') is None


def test_object_loaders_and_builder_summarize_accessible_rows(
    tmp_path: Path,
) -> None:
    """Public object helpers should load rows and build a consistent summary."""
    base_dir = tmp_path / 'ari'
    objects_dir = base_dir / 'tasks' / 'SPIROU' / 'profile1' / 'objects'
    objects_dir.mkdir(parents=True)

    obj_row = {
        'OBJNAME': 'GL699',
        'RA [Deg]': 269.452,
        'Dec [Deg]': 4.693,
        'DPRTYPE': 'OBJ_FP',
    }
    raw_rows = [
        {
            'KW_RUN_ID': 'RUN1',
            'PASSED_ALL_QC': 1,
            'MID_OBS_TIME': '2026-01-01T01:00:00',
            'IDENTIFIER': 'ID1',
        },
        {
            'KW_RUN_ID': 'RUN2',
            'PASSED_ALL_QC': 0,
            'MID_OBS_TIME': '2026-01-02T01:00:00',
            'IDENTIFIER': 'ID2',
        },
    ]
    ext_rows = [
        {
            'KW_RUN_ID': 'RUN1',
            'PASSED_ALL_QC': 1,
            'MID_OBS_TIME': '2026-01-01T02:00:00',
            'LAST_MODIFIED': '2026-01-03T00:00:00',
            'OBS_DIR': '2026-01-01',
            'IDENTIFIER': 'ID1',
            'KW_DPRTYPE': 'OBJ_FP',
        },
        {
            'KW_RUN_ID': 'RUN2',
            'PASSED_ALL_QC': 0,
            'MID_OBS_TIME': '2026-01-02T02:00:00',
            'LAST_MODIFIED': '2026-01-04T00:00:00',
            'OBS_DIR': '2026-01-01',
            'IDENTIFIER': 'ID2',
            'KW_DPRTYPE': 'OBJ_FP',
        },
    ]
    ccf_rows = [
        {
            'KW_RUN_ID': 'RUN1',
            'PASSED_ALL_QC': 1,
            'MID_OBS_TIME': '2026-01-01T02:30:00',
            'LAST_MODIFIED': '2026-01-03T01:00:00',
            'IDENTIFIER': 'ID1',
        }
    ]
    htable_rows = [
        {
            'IDENTIFIER': 'ID1',
            'OBJNAME': 'GL699',
            'PP_OBJECT': 'GL699',
            'EXT_OBJECT': 'GL699',
            'PP_OBNAME': 'Barnard',
            'PP_PI_NAME': 'Cook',
            'PP_PROG_ID': 'RUN1',
            'PP_VERSION': '1.0',
            'EXT_VERSION': '2.0',
            'TCORR_VERSION': '3.0',
            'CCF_VERSION': '4.0',
            'CCF_MASK': 'M2',
            'CCF_DV': 1.234,
            'CCF_FWHM': 7.89,
            'EXT_Y': 100.0,
            'EXT_H': 80.0,
            'EXT_SEEING': 0.9,
            'EXT_AIRMASS': 1.1,
            'EXT_EXPTIME': 600.0,
        },
        {
            'IDENTIFIER': 'ID2',
            'OBJNAME': 'GL699',
            'PP_OBJECT': 'GL699',
            'EXT_OBJECT': 'GL699',
            'PP_OBNAME': 'Hidden',
            'PP_PI_NAME': 'Other',
            'PP_PROG_ID': 'RUN2',
            'EXT_Y': 10.0,
            'EXT_H': 8.0,
        },
    ]

    _write_rows_file(objects_dir.parent / 'object_table.json', [obj_row])
    _write_rows_file(objects_dir / 'htable_GL699.json', htable_rows)
    _write_rows_file(objects_dir / 'ftable_raw_GL699.json', raw_rows)
    _write_rows_file(objects_dir / 'ftable_ext_GL699.json', ext_rows)
    _write_rows_file(objects_dir / 'ftable_ccf_GL699.json', ccf_rows)

    object_funcs._json_rows_cache.clear()

    assert object_funcs.load_object_table_row(objects_dir, 'GL699') == obj_row
    assert (
        object_funcs.load_object_htable_rows(objects_dir, 'GL699')
        == htable_rows
    )
    assert object_funcs.load_object_ftable_rows(
        objects_dir,
        'GL699',
        'ext',
    ) == ext_rows
    assert object_funcs.load_object_preset('') == {}

    payload = object_funcs.build_object_page_stats(
        base_dir=base_dir,
        instrument='SPIROU',
        profile_id='profile1',
        obj_row=obj_row,
        objname='GL699',
        accessible_run_ids={'RUN1'},
    )

    assert payload['target_info']['object_name'] == 'GL699'
    assert payload['spectrum']['raw_total'] == '1 (2)'
    assert payload['spectrum']['raw_rejected'] == '0 (1)'
    assert payload['spectrum']['median_snr_y'] == '100.00'
    assert payload['spectrum']['ob_names_in_headers'] == ['Barnard']
    assert payload['ccf']['mask_used'] == 'M2'
    assert payload['ccf']['systemic_velocity'] == '1.234'
    assert payload['time_series'][0]['num_ext'] == '1 (2)'
    assert payload['time_series'][0]['snr_order_15'] == '100.00'
    assert payload['labels']['target_info']['pi_names_in_headers'] == (
        'PI name(s) in header'
    )

    object_funcs._json_rows_cache.clear()

