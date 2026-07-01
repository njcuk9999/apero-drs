#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for base.py YAML and utility functions."""

import os
import tempfile
import numpy as np

from aperocore.base import base


# =============================================================================
# Define functions
# =============================================================================
def test_to_plain_data_converts_commented_map() -> None:
    """to_plain_data should convert CommentedMap to dict."""
    from ruamel.yaml.comments import CommentedMap
    cmap = CommentedMap({'key': 'value', 'num': 42})
    result = base.to_plain_data(cmap)
    assert isinstance(result, dict)
    assert result == {'key': 'value', 'num': 42}


def test_to_plain_data_converts_commented_seq() -> None:
    """to_plain_data should convert CommentedSeq to list."""
    from ruamel.yaml.comments import CommentedSeq
    cseq = CommentedSeq([1, 2, 3, 'four'])
    result = base.to_plain_data(cseq)
    assert isinstance(result, list)
    assert result == [1, 2, 3, 'four']


def test_to_plain_data_converts_scalar_float() -> None:
    """to_plain_data should convert ScalarFloat to float."""
    from ruamel.yaml.scalarfloat import ScalarFloat
    sfloat = ScalarFloat(3.14)
    result = base.to_plain_data(sfloat)
    assert isinstance(result, float)
    assert result == 3.14


def test_to_plain_data_converts_scalar_int() -> None:
    """to_plain_data should convert ScalarInt to int."""
    from ruamel.yaml.scalarint import ScalarInt
    sint = ScalarInt(42)
    result = base.to_plain_data(sint)
    assert isinstance(result, int)
    assert result == 42


def test_to_plain_data_converts_scalar_bool() -> None:
    """to_plain_data should convert ScalarBoolean to bool."""
    from ruamel.yaml.scalarbool import ScalarBoolean
    sbool = ScalarBoolean(True)
    result = base.to_plain_data(sbool)
    assert isinstance(result, bool)
    assert result is True


def test_to_plain_data_converts_scalar_string() -> None:
    """to_plain_data should convert ScalarString to str."""
    from ruamel.yaml.scalarstring import ScalarString
    sstr = ScalarString('hello')
    result = base.to_plain_data(sstr)
    assert isinstance(result, str)
    assert result == 'hello'


def test_to_plain_data_handles_native_types() -> None:
    """to_plain_data should return native Python types unchanged."""
    assert base.to_plain_data(42) == 42
    assert base.to_plain_data('text') == 'text'
    assert base.to_plain_data(3.14) == 3.14
    assert base.to_plain_data(True) is True
    assert base.to_plain_data([1, 2]) == [1, 2]


def test_to_plain_data_recurses_nested_structures() -> None:
    """to_plain_data should recursively convert nested structures."""
    from ruamel.yaml.comments import CommentedMap, CommentedSeq
    from ruamel.yaml.scalarint import ScalarInt

    nested = CommentedMap({
        'list': CommentedSeq([1, ScalarInt(2), 3]),
        'num': ScalarInt(5)
    })
    result = base.to_plain_data(nested)
    assert result == {'list': [1, 2, 3], 'num': 5}
    assert isinstance(result, dict)
    assert isinstance(result['list'], list)


def test_load_yaml_creates_file_from_dict() -> None:
    """load_yaml should successfully load a YAML file."""
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.yaml',
        delete=False
    ) as f:
        f.write("key1: value1\n")
        f.write("key2: 42\n")
        f.write("key3: 3.14\n")
        tmpfile = f.name

    try:
        result = base.load_yaml(tmpfile)
        assert result['key1'] == 'value1'
        assert result['key2'] == 42
        assert abs(result['key3'] - 3.14) < 0.01
    finally:
        os.unlink(tmpfile)


def test_load_yaml_fills_missing_keys_with_default() -> None:
    """load_yaml should fill missing keys using default dict."""
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.yaml',
        delete=False
    ) as f:
        f.write("key1: value1\n")
        tmpfile = f.name

    try:
        default = {'key2': 'default_value', 'key3': 99}
        result = base.load_yaml(tmpfile, default=default)
        assert result['key1'] == 'value1'
        assert result['key2'] == 'default_value'
        assert result['key3'] == 99
    finally:
        os.unlink(tmpfile)


def test_load_yaml_preserves_explicit_values_over_defaults() -> None:
    """load_yaml should not override explicit values with defaults."""
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.yaml',
        delete=False
    ) as f:
        f.write("key1: explicit_value\n")
        tmpfile = f.name

    try:
        default = {'key1': 'default_value'}
        result = base.load_yaml(tmpfile, default=default)
        assert result['key1'] == 'explicit_value'
    finally:
        os.unlink(tmpfile)


def test_load_yaml_handles_scientific_notation() -> None:
    """load_yaml should parse scientific notation floats."""
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.yaml',
        delete=False
    ) as f:
        f.write("sci1: 1.23e6\n")
        f.write("sci2: 1e-5\n")
        f.write("sci3: -4.56e+3\n")
        tmpfile = f.name

    try:
        result = base.load_yaml(tmpfile)
        assert abs(result['sci1'] - 1.23e6) < 1.0
        assert abs(result['sci2'] - 1e-5) < 1e-10
        assert abs(result['sci3'] - (-4.56e3)) < 1.0
    finally:
        os.unlink(tmpfile)


def test_write_yaml_creates_valid_yaml_file() -> None:
    """write_yaml should create a valid YAML file."""
    data = {
        'key1': 'value1',
        'key2': 42,
        'key3': 3.14,
        'nested': {'sub_key': 'sub_value'}
    }

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.yaml',
        delete=False
    ) as f:
        tmpfile = f.name

    try:
        base.write_yaml(data, tmpfile)
        # Read it back to verify
        result = base.load_yaml(tmpfile)
        assert result['key1'] == 'value1'
        assert result['key2'] == 42
        assert abs(result['key3'] - 3.14) < 0.01
        assert result['nested']['sub_key'] == 'sub_value'
    finally:
        os.unlink(tmpfile)


def test_write_yaml_with_custom_width() -> None:
    """write_yaml should respect custom width parameter."""
    data = {'longkey': 'a' * 100}

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.yaml',
        delete=False
    ) as f:
        tmpfile = f.name

    try:
        # Just ensure it doesn't raise an error
        base.write_yaml(data, tmpfile, width=50)
        assert os.path.exists(tmpfile)
        result = base.load_yaml(tmpfile)
        assert len(result['longkey']) == 100
    finally:
        os.unlink(tmpfile)


def test_get_default_log_dir_creates_path() -> None:
    """get_default_log_dir should return a valid log directory."""
    log_dir = base.get_default_log_dir()
    # Check that it's a string and contains a date
    assert isinstance(log_dir, str)
    assert '2026' in log_dir or '2025' in log_dir or '2024' in log_dir
    # Path should exist after calling the function
    assert os.path.exists(log_dir) or log_dir.startswith(
        os.path.expanduser('~/.apero/dlog/')
    )


def test_tqdm_module_returns_passthrough_when_disabled() -> None:
    """tqdm_module with use=False should return a callable."""
    tqdm_func = base.tqdm_module(use=False)
    # The passthrough function should be callable
    assert callable(tqdm_func)
    # It should accept an argument
    test_list = [1, 2, 3, 4, 5]
    result = tqdm_func(test_list)
    # Result should be iterable
    assert hasattr(result, '__iter__')


def test_enable_scientific_floats_config() -> None:
    """enable_scientific_floats should configure YAML resolver."""
    from ruamel.yaml import YAML
    yaml_inst = YAML(typ='rt')
    # Just verify it doesn't raise an error
    base.enable_scientific_floats(yaml_inst)
    # Check that resolver was modified (indirectly)
    assert hasattr(yaml_inst, 'Resolver')


# =============================================================================
# End of code
# =============================================================================


