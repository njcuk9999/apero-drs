#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for additional apero utility functions."""

import tempfile
import os
import numpy as np
from pathlib import Path

from aperocore.base import drs_base


# =============================================================================
# Define functions - hash generation tests
# =============================================================================
def test_generate_hash_produces_string() -> None:
    """generate_hash should produce a string hash."""
    result = drs_base.generate_hash('test', size=8)
    assert isinstance(result, str)


def test_generate_hash_deterministic() -> None:
    """generate_hash should produce same hash for same input."""
    hash1 = drs_base.generate_hash('test', size=8)
    hash2 = drs_base.generate_hash('test', size=8)
    assert hash1 == hash2


def test_generate_hash_different_sizes() -> None:
    """generate_hash should produce different length hashes."""
    hash4 = drs_base.generate_hash('test', size=4)
    hash12 = drs_base.generate_hash('test', size=12)
    assert len(hash4) != len(hash12)


def test_generate_hash_size_4_is_8_chars() -> None:
    """generate_hash with size=4 should produce 8 character string."""
    result = drs_base.generate_hash('test', size=4)
    assert len(result) == 8  # blake2 hex is 2 * size


def test_generate_hash_changes_with_input() -> None:
    """generate_hash should produce different hashes for different input."""
    hash1 = drs_base.generate_hash('input1', size=8)
    hash2 = drs_base.generate_hash('input2', size=8)
    assert hash1 != hash2


def test_generate_hash_is_hexadecimal() -> None:
    """generate_hash should produce hexadecimal string."""
    result = drs_base.generate_hash('test', size=8)
    # All characters should be hex digits
    assert all(c in '0123456789abcdef' for c in result.lower())


# =============================================================================
# Define functions - escape sequence tests
# =============================================================================
def test_escape_map_converts_newline() -> None:
    """_escape_map should convert \\n to actual newline."""
    raw = r'line1\nline2'
    result = drs_base._escape_map(raw)
    assert '\n' in result
    assert result.count('\n') == 1


def test_escape_map_converts_tab() -> None:
    """_escape_map should convert \\t to actual tab."""
    raw = r'col1\tcol2'
    result = drs_base._escape_map(raw)
    assert '\t' in result


def test_escape_map_converts_multiple_escapes() -> None:
    """_escape_map should convert multiple escape sequences."""
    raw = r'line1\nline2\tvalue'
    result = drs_base._escape_map(raw)
    assert '\n' in result
    assert '\t' in result


def test_escape_map_preserves_non_escape_strings() -> None:
    """_escape_map should leave non-escape strings unchanged."""
    raw = 'normal string'
    result = drs_base._escape_map(raw)
    assert result == raw


def test_escape_map_returns_non_strings_unchanged() -> None:
    """_escape_map should return non-strings unchanged."""
    obj = {'key': 'value'}
    result = drs_base._escape_map(obj)
    assert result is obj


def test_escape_map_with_list() -> None:
    """_escape_map should return list unchanged."""
    lst = [1, 2, 3]
    result = drs_base._escape_map(lst)
    assert result is lst


# =============================================================================
# Define functions - null text tests
# =============================================================================
def test_base_null_text_with_none() -> None:
    """base_null_text should return True for None."""
    assert drs_base.base_null_text(None) is True


def test_base_null_text_with_empty_string() -> None:
    """base_null_text should return True for empty string."""
    assert drs_base.base_null_text('') is True


def test_base_null_text_with_whitespace() -> None:
    """base_null_text should return True for whitespace."""
    assert drs_base.base_null_text('   ') is True


def test_base_null_text_with_valid_value() -> None:
    """base_null_text should return False for valid value."""
    assert drs_base.base_null_text('value') is False


def test_base_null_text_with_custom_nulls() -> None:
    """base_null_text should recognize custom null values."""
    assert drs_base.base_null_text('N/A', nulls=['N/A']) is True
    assert drs_base.base_null_text('NONE', nulls=['N/A']) is False


def test_base_null_text_with_multiple_custom_nulls() -> None:
    """base_null_text should handle multiple custom null values."""
    nulls = ['N/A', 'NA', 'none', '-99']
    assert drs_base.base_null_text('N/A', nulls=nulls) is True
    assert drs_base.base_null_text('NA', nulls=nulls) is True
    assert drs_base.base_null_text('none', nulls=nulls) is True
    assert drs_base.base_null_text('-99', nulls=nulls) is True
    assert drs_base.base_null_text('value', nulls=nulls) is False


# =============================================================================
# Define functions - type checking tests
# =============================================================================
def test_type_checking_constants_exist() -> None:
    """Type checking constants should exist."""
    assert hasattr(drs_base, 'SIMPLE_TYPES')
    assert hasattr(drs_base, 'SIMPLE_STYPES')
    assert hasattr(drs_base, 'NUMBER_TYPES')


def test_simple_types_contains_basic_types() -> None:
    """SIMPLE_TYPES should contain basic Python types."""
    assert int in drs_base.SIMPLE_TYPES
    assert float in drs_base.SIMPLE_TYPES
    assert str in drs_base.SIMPLE_TYPES
    assert bool in drs_base.SIMPLE_TYPES
    assert list in drs_base.SIMPLE_TYPES
    assert dict in drs_base.SIMPLE_TYPES


def test_simple_stypes_matches_types() -> None:
    """SIMPLE_STYPES should have matching string representations."""
    assert 'int' in drs_base.SIMPLE_STYPES
    assert 'float' in drs_base.SIMPLE_STYPES
    assert 'str' in drs_base.SIMPLE_STYPES
    assert 'bool' in drs_base.SIMPLE_STYPES
    assert 'list' in drs_base.SIMPLE_STYPES
    assert 'dict' in drs_base.SIMPLE_STYPES


def test_number_types_contains_numeric() -> None:
    """NUMBER_TYPES should contain numeric types."""
    assert int in drs_base.NUMBER_TYPES
    assert float in drs_base.NUMBER_TYPES


# =============================================================================
# Define functions - string type tests
# =============================================================================
def test_strtype_mapping_exists() -> None:
    """STRTYPE should map types to strings."""
    assert hasattr(drs_base, 'STRTYPE')
    assert isinstance(drs_base.STRTYPE, dict)


def test_strtype_contains_basic_types() -> None:
    """STRTYPE should map basic types."""
    assert int in drs_base.STRTYPE
    assert float in drs_base.STRTYPE
    assert str in drs_base.STRTYPE
    assert list in drs_base.STRTYPE
    assert dict in drs_base.STRTYPE


def test_typestr_is_inverted_strtype() -> None:
    """TYPESTR should be inverse of STRTYPE."""
    assert hasattr(drs_base, 'TYPESTR')
    # Sample check: string 'int' should map to int
    assert drs_base.TYPESTR.get('int') == int


# =============================================================================
# Define functions - color constants tests
# =============================================================================
def test_colors_dictionary_exists() -> None:
    """COLOURS dictionary should exist."""
    assert hasattr(drs_base, 'COLOURS')
    assert isinstance(drs_base.COLOURS, dict)


def test_colors_contains_ansi_codes() -> None:
    """COLOURS should contain ANSI color codes."""
    assert 'RED1' in drs_base.COLOURS
    assert 'GREEN1' in drs_base.COLOURS
    assert 'BLUE1' in drs_base.COLOURS
    assert 'ENDC' in drs_base.COLOURS


def test_colors_values_are_strings() -> None:
    """All COLOURS values should be strings (ANSI codes)."""
    for key, value in drs_base.COLOURS.items():
        assert isinstance(value, str)


def test_colors_have_escape_prefix() -> None:
    """ANSI codes should start with escape character."""
    for key, value in drs_base.COLOURS.items():
        # ANSI codes typically start with \033
        assert value.startswith('\033') or key in ['ENDC']


# =============================================================================
# Define functions - configuration constants tests
# =============================================================================
def test_configuration_constants_exist() -> None:
    """Configuration constants should exist."""
    assert hasattr(drs_base, 'DEFAULT_LANG')
    assert hasattr(drs_base, 'LANGUAGES')
    assert hasattr(drs_base, 'AUTHORS')


def test_authors_dictionary_exists() -> None:
    """AUTHORS dictionary should exist and have entries."""
    assert hasattr(drs_base, 'AUTHORS')
    assert isinstance(drs_base.AUTHORS, dict)
    assert len(drs_base.AUTHORS) > 0


def test_yaml_files_constants_defined() -> None:
    """YAML file name constants should be defined."""
    assert hasattr(drs_base, 'INSTALL_YAML')
    assert hasattr(drs_base, 'DATABASE_YAML')
    assert isinstance(drs_base.INSTALL_YAML, str)
    assert isinstance(drs_base.DATABASE_YAML, str)


# =============================================================================
# Define functions - package info tests
# =============================================================================
def test_package_name_defined() -> None:
    """Package name should be defined."""
    assert hasattr(drs_base, '__PACKAGE__')
    assert drs_base.__PACKAGE__ == 'aperocore'


def test_version_string_exists() -> None:
    """Version string should exist."""
    assert hasattr(drs_base, '__version__')
    assert isinstance(drs_base.__version__, str)


def test_authors_defined() -> None:
    """Authors should be defined."""
    assert hasattr(drs_base, '__authors__')


# =============================================================================
# End of code
# =============================================================================

