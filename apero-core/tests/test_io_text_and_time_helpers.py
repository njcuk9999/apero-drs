#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for IO, text, and time helpers in ``apero-core``."""

from pathlib import Path
from typing import Any

import numpy as np
from astropy.table import Table

from aperocore.core import drs_text
from aperocore.io import drs_io
from aperocore.math import time as time_mod


# =============================================================================
# Define functions
# =============================================================================
def test_no_mask_table_clears_mask_flags_from_masked_columns() -> None:
    """`no_mask_table` should keep values while clearing masked flags."""
    table = Table(masked=True)
    table['flux'] = np.ma.array([1.0, 2.0], mask=[False, True])

    result = drs_io.no_mask_table(table)

    assert np.allclose(result['flux'].data, np.array([1.0, 2.0]))
    assert np.array_equal(result['flux'].mask, np.array([False, False]))


def test_no_mask_table_returns_non_table_inputs_unchanged() -> None:
    """`no_mask_table` should be a no-op for non-table values."""
    payload: Any = {'not': 'a table'}
    assert drs_io.no_mask_table(payload) is payload


def test_get_time_now_returns_iso_from_time_provider(monkeypatch) -> None:
    """`get_time_now` should return the ISO string from `Time.now()`."""

    class _FakeNow:
        """Simple container matching the astropy time object interface."""

        iso = '2026-06-30 12:34:56.789'

    class _FakeTime:
        """Replacement `Time` class with a deterministic `now` method."""

        @staticmethod
        def now() -> _FakeNow:
            """Return a deterministic object for the test."""
            return _FakeNow()

    monkeypatch.setattr(time_mod, 'Time', _FakeTime)

    assert time_mod.get_time_now() == '2026-06-30 12:34:56.789'


def test_get_hhmmss_now_uses_last_time_component(monkeypatch) -> None:
    """`get_hhmmss_now` should keep only the HH:MM:SS.SSS fragment."""
    monkeypatch.setattr(
        time_mod,
        'get_time_now',
        lambda: '2026-06-30 12:34:56.789',
    )

    assert time_mod.get_hhmmss_now() == '12:34:56.789'


def test_load_text_file_and_read_lines_skip_comments(tmp_path: Path) -> None:
    """Both loaders should skip comments and blank lines consistently."""
    filename = tmp_path / 'config.txt'
    filename.write_text(
        '# comment\n\nALPHA=1\nBETA=two\n',
        encoding='utf-8',
    )
    expected = np.array([['ALPHA', '1'], ['BETA', 'two']])

    assert np.array_equal(drs_text.load_text_file(filename), expected)
    assert np.array_equal(drs_text.read_lines(filename), expected)


def test_load_text_file_falls_back_to_read_lines(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """`load_text_file` should fall back when `genfromtxt` fails."""
    filename = tmp_path / 'fallback.txt'
    filename.write_text('KEY=value\n', encoding='utf-8')

    def _raise_genfromtxt(*args, **kwargs):
        """Raise an error to force the slow-path parser."""
        raise ValueError('forced failure')

    monkeypatch.setattr(drs_text.np, 'genfromtxt', _raise_genfromtxt)

    result = drs_text.load_text_file(filename)

    assert np.array_equal(result, np.array([['KEY', 'value']]))


def test_common_text_finds_prefixes_and_suffixes() -> None:
    """`common_text` should detect shared prefixes and suffixes."""
    prefix = drs_text.common_text(['pre_one', 'pre_two'], kind='prefix')
    suffix = drs_text.common_text(['one_end', 'two_end'], kind='suffix')

    assert prefix == 'pre_'
    assert suffix == '_end'


def test_combine_uncommon_text_preserves_prefix_and_suffix() -> None:
    """`combine_uncommon_text` should collapse varying middle segments."""
    result = drs_text.combine_uncommon_text(
        ['file_001.fits', 'file_003.fits', 'file_002.fits'],
        prefix='file_',
        suffix='.fits',
        fmt='{0}{1}-{2}{3}',
    )

    assert result == 'file_001-003.fits'


def test_textwrap_tabs_follow_up_lines_after_wrapping() -> None:
    """Wrapped lines after the first should be indented with a tab."""
    lines = drs_text.textwrap('alpha beta gamma delta', length=10)

    assert lines[0] == 'alpha'
    assert lines[1].startswith('\t')
    assert lines[1].strip() == 'beta gamma'
    assert lines[2].startswith('\t')
    assert lines[2].strip() == 'delta'


def test_null_text_and_true_text_handle_common_text_inputs() -> None:
    """Boolean-ish and null-ish text should be interpreted correctly."""
    assert drs_text.null_text(None)
    assert drs_text.null_text('n/a', nulls=['N/A'])
    assert drs_text.true_text('true')
    assert not drs_text.true_text('false')


def test_include_exclude_filters_entries_with_mixed_logic() -> None:
    """`include_exclude` should apply include and exclude filters."""
    inlist = ['SCI_A', 'SCI_BAD', 'CAL_A', 'SCI_GOOD']
    result = drs_text.include_exclude(
        inlist,
        includes='SCI',
        excludes='BAD',
    )

    assert result == ['SCI_A', 'SCI_GOOD']


def test_capitalise_key_and_clean_strings_normalize_text() -> None:
    """Case and whitespace cleanup helpers should normalize text values."""
    cleaned = drs_text.clean_strings(['  alpha ', 'Beta  '])

    assert drs_text.capitalise_key('mixed') == 'MIXED'
    assert cleaned == ['ALPHA', 'BETA']


def test_test_format_accepts_valid_and_rejects_invalid_formats() -> None:
    """`test_format` should distinguish valid and invalid format strings."""
    assert drs_text.test_format('7.2f')
    assert drs_text.test_format('{0}')
    assert not drs_text.test_format('bad.format')


def test_cull_leading_trailing_removes_requested_characters() -> None:
    """`cull_leading_trailing` should strip repeated edge characters."""
    text = '"\'value\'"'
    result = drs_text.cull_leading_trailing(text, ['"', "'"])

    assert result == 'value'


def test_string_type_detects_supported_scalar_and_container_forms() -> None:
    """`string_type` should infer the expected target Python type."""
    assert drs_text.string_type('None') is type(None)
    assert drs_text.string_type('TRUE') is bool
    assert drs_text.string_type('[1, 2]') is list
    assert drs_text.string_type('{"a": 1}') is dict
    assert drs_text.string_type('-3') is int
    assert drs_text.string_type('+4.5') is float
    assert drs_text.string_type('alpha/beta') is str


def test_clean_ascii_text_and_fits_table_column_remove_non_ascii() -> None:
    """ASCII cleanup helpers should strip non-ASCII chars in text fields."""
    text = 'Café\nTab\tDone'
    cleaned_text = drs_text.clean_ascii_text(text)
    table = Table({'name': ['Café', 'naïve']})

    drs_text.clean_fits_table_column(table, 'name')

    assert cleaned_text == 'Caf Tab Done'
    assert list(table['name']) == ['Caf', 'nave']


def test_pattern_is_too_generic_handles_extensions_and_specific_names() -> None:
    """Generic wildcard-only patterns should be detected reliably."""
    assert drs_text.pattern_is_too_generic('*.fits', extension='.fits')
    assert drs_text.pattern_is_too_generic('???.txt', extension='.txt')
    assert not drs_text.pattern_is_too_generic('science_*.fits')




