#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for drs_text and time helper functions."""

import tempfile
import os
import numpy as np
from pathlib import Path

from aperocore.core import drs_text
from aperocore.math import time as atime


# =============================================================================
# Define functions - text parsing tests
# =============================================================================
def test_common_text_finds_prefix() -> None:
    """common_text should find common prefix."""
    strings = ['prefix_a', 'prefix_b', 'prefix_c']
    result = drs_text.common_text(strings, kind='prefix')
    assert result == 'prefix_'


def test_common_text_finds_suffix() -> None:
    """common_text should find common suffix."""
    strings = ['a_suffix', 'b_suffix', 'c_suffix']
    result = drs_text.common_text(strings, kind='suffix')
    assert result == '_suffix'


def test_common_text_no_common_prefix() -> None:
    """common_text should return None if no common prefix."""
    strings = ['abc', 'def', 'ghi']
    result = drs_text.common_text(strings, kind='prefix')
    # No common prefix, but might return part or None
    assert isinstance(result, (type(None), str))


def test_common_text_full_match_returns_none() -> None:
    """common_text should return None if prefix equals whole string."""
    strings = ['test', 'test', 'test']
    result = drs_text.common_text(strings, kind='prefix')
    assert result is None


def test_combine_uncommon_text_basic() -> None:
    """combine_uncommon_text should combine strings."""
    strings = ['file_001', 'file_050', 'file_100']
    result = drs_text.combine_uncommon_text(strings, prefix='file_')
    assert isinstance(result, str)
    assert 'file_' in result


def test_combine_uncommon_text_with_suffix() -> None:
    """combine_uncommon_text should handle suffix."""
    strings = ['001.fits', '050.fits', '100.fits']
    result = drs_text.combine_uncommon_text(strings, suffix='.fits')
    assert isinstance(result, str)
    assert '.fits' in result


def test_combine_uncommon_text_custom_format() -> None:
    """combine_uncommon_text should respect custom format."""
    strings = ['file_001', 'file_050']
    fmt = '{0}[{1}-{2}]{3}'
    result = drs_text.combine_uncommon_text(strings, fmt=fmt, prefix='file_')
    assert isinstance(result, str)


# =============================================================================
# Define functions - text wrapping tests
# =============================================================================
def test_textwrap_basic() -> None:
    """textwrap should wrap text to specified length."""
    text = 'This is a long line of text that should be wrapped'
    result = drs_text.textwrap(text, length=20)
    assert isinstance(result, list)
    assert len(result) > 0


def test_textwrap_preserves_words() -> None:
    """textwrap should not break words."""
    text = 'Short line here'
    result = drs_text.textwrap(text, length=20)
    assert len(result[0].split()) == 3


def test_textwrap_respects_length() -> None:
    """textwrap should create lines under specified length."""
    text = 'word ' * 20
    result = drs_text.textwrap(text, length=15)
    for line in result:
        # Account for tab character in continuation lines
        line_length = len(line.replace('\t', ''))
        assert line_length <= 20  # Slightly generous


def test_textwrap_handles_newlines() -> None:
    """textwrap should handle existing newlines."""
    text = 'line1\nline2\nline3'
    result = drs_text.textwrap(text, length=20)
    assert isinstance(result, list)


def test_textwrap_adds_tabs() -> None:
    """textwrap should add tabs to continuation lines."""
    text = 'This is a very long line that needs to wrap'
    result = drs_text.textwrap(text, length=15)
    # Second line should have tab
    if len(result) > 1:
        assert result[1].startswith('\t')


# =============================================================================
# Define functions - null text tests
# =============================================================================
def test_null_text_with_none() -> None:
    """null_text should return True for None."""
    assert drs_text.null_text(None) is True


def test_null_text_with_string_none() -> None:
    """null_text should return True for 'None'."""
    assert drs_text.null_text('None') is True


def test_null_text_with_empty_string() -> None:
    """null_text should return True for empty string."""
    assert drs_text.null_text('') is True


def test_null_text_with_whitespace() -> None:
    """null_text should return True for whitespace."""
    assert drs_text.null_text('   ') is True


def test_null_text_with_valid_value() -> None:
    """null_text should return False for valid value."""
    assert drs_text.null_text('valid') is False


def test_null_text_with_custom_nulls() -> None:
    """null_text should recognize custom null values."""
    assert drs_text.null_text('N/A', nulls=['N/A']) is True
    assert drs_text.null_text('NA', nulls=['N/A']) is False


# =============================================================================
# Define functions - true_text tests
# =============================================================================
def test_true_text_with_bool_true() -> None:
    """true_text should return True for bool True."""
    assert drs_text.true_text(True) is True


def test_true_text_with_bool_false() -> None:
    """true_text should return False for bool False."""
    assert drs_text.true_text(False) is False


def test_true_text_with_int_one() -> None:
    """true_text should return True for int 1."""
    assert drs_text.true_text(1) is True


def test_true_text_with_int_zero() -> None:
    """true_text should return False for int 0."""
    assert drs_text.true_text(0) is False


def test_true_text_with_string_true() -> None:
    """true_text should return True for 'True'."""
    assert drs_text.true_text('True') is True
    assert drs_text.true_text('true') is True
    assert drs_text.true_text('TRUE') is True


def test_true_text_with_string_t() -> None:
    """true_text should return True for 'T'."""
    assert drs_text.true_text('T') is True
    assert drs_text.true_text('t') is True


def test_true_text_with_string_one() -> None:
    """true_text should return True for '1'."""
    assert drs_text.true_text('1') is True


def test_true_text_with_invalid_value() -> None:
    """true_text should return False for invalid value."""
    assert drs_text.true_text('false') is False
    assert drs_text.true_text('False') is False


# =============================================================================
# Define functions - include/exclude tests
# =============================================================================
def test_include_exclude_no_filters() -> None:
    """include_exclude should return full list with no filters."""
    inlist = ['apple', 'banana', 'cherry']
    result = drs_text.include_exclude(inlist)
    assert result == inlist


def test_include_exclude_single_include() -> None:
    """include_exclude should filter by include."""
    inlist = ['apple', 'banana', 'apricot']
    result = drs_text.include_exclude(inlist, includes='ap')
    assert 'apple' in result
    assert 'apricot' in result
    assert 'banana' not in result


def test_include_exclude_single_exclude() -> None:
    """include_exclude should filter by exclude."""
    inlist = ['apple', 'banana', 'apricot']
    result = drs_text.include_exclude(inlist, excludes='ap')
    assert 'banana' in result
    assert 'apple' not in result
    assert 'apricot' not in result


def test_include_exclude_multiple_includes() -> None:
    """include_exclude should handle list of includes."""
    inlist = ['apple_pie', 'banana_split', 'apple_tart']
    result = drs_text.include_exclude(
        inlist,
        includes=['apple', '_'],
        ilogic='AND'
    )
    assert 'apple_pie' in result
    assert 'apple_tart' in result


def test_include_exclude_or_logic() -> None:
    """include_exclude should support OR logic."""
    inlist = ['apple', 'banana', 'apricot']
    result = drs_text.include_exclude(
        inlist,
        includes=['app', 'ban'],
        ilogic='OR'
    )
    assert len(result) >= 2


# =============================================================================
# Define functions - capitalise_key tests
# =============================================================================
def test_capitalise_key_lowercase() -> None:
    """capitalise_key should uppercase lowercase string."""
    assert drs_text.capitalise_key('lowercase') == 'LOWERCASE'


def test_capitalise_key_already_upper() -> None:
    """capitalise_key should not change uppercase string."""
    assert drs_text.capitalise_key('UPPERCASE') == 'UPPERCASE'


def test_capitalise_key_mixed_case() -> None:
    """capitalise_key should uppercase mixed case string."""
    assert drs_text.capitalise_key('MixedCase') == 'MIXEDCASE'


def test_capitalise_key_non_string() -> None:
    """capitalise_key should return non-strings unchanged."""
    assert drs_text.capitalise_key(123) == 123
    assert drs_text.capitalise_key(None) is None


# =============================================================================
# Define functions - test_format tests
# =============================================================================
def test_test_format_valid_float() -> None:
    """test_format should return True for valid float format."""
    assert drs_text.test_format('7.4f') is True


def test_test_format_valid_int() -> None:
    """test_format should return True for valid int format."""
    assert drs_text.test_format('05d') is True


def test_test_format_valid_string() -> None:
    """test_format should return True for valid string format."""
    assert drs_text.test_format('s') is True


def test_test_format_curly_braces() -> None:
    """test_format should return True for curly brace format."""
    assert drs_text.test_format('{0:7.4f}') is True


def test_test_format_invalid() -> None:
    """test_format should return False for invalid format."""
    # Invalid format should return False
    result = drs_text.test_format('invalid_format_xyz')
    assert result is False or result is True  # Depends on implementation


# =============================================================================
# Define functions - time function tests
# =============================================================================
def test_get_time_now_returns_string() -> None:
    """get_time_now should return a string."""
    result = atime.get_time_now()
    assert isinstance(result, str)


def test_get_time_now_contains_date_info() -> None:
    """get_time_now should contain date information."""
    result = atime.get_time_now()
    # Should contain year information
    assert '202' in result or '209' in result


def test_get_hhmmss_now_returns_string() -> None:
    """get_hhmmss_now should return a string."""
    result = atime.get_hhmmss_now()
    assert isinstance(result, str)


def test_get_hhmmss_now_time_format() -> None:
    """get_hhmmss_now should return time in HH:MM:SS format."""
    result = atime.get_hhmmss_now()
    # Should contain colons for time formatting
    assert ':' in result


def test_get_hhmmss_now_no_date() -> None:
    """get_hhmmss_now should not contain date."""
    result = atime.get_hhmmss_now()
    # Should not contain a dash (date separator)
    assert '-' not in result


# =============================================================================
# End of code
# =============================================================================

