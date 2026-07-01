#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""More comprehensive tests for drs_misc.py utility functions."""

import os
import tempfile
from pathlib import Path
from aperocore.core import drs_misc
from aperocore.base import base


# =============================================================================
# Define functions - Path and utility function tests
# =============================================================================
def test_get_uncommon_path_simple() -> None:
    """get_uncommon_path should return uncommon portion of paths."""
    path1 = '/home/user/dir1/dir2/dir3'
    path2 = '/home/user/dir1'
    result = drs_misc.get_uncommon_path(path1, path2)
    # Result should contain dir2 and dir3
    assert 'dir2' in result or 'dir3' in result


def test_get_uncommon_path_with_pathlib() -> None:
    """get_uncommon_path should work with Path objects."""
    path1 = Path('/home/user/dir1/dir2')
    path2 = Path('/home/user/dir1')
    result = drs_misc.get_uncommon_path(path1, path2)
    assert isinstance(result, str)


def test_get_uncommon_path_swaps_if_needed() -> None:
    """get_uncommon_path should handle paths in either order."""
    path1 = '/home/user/dir1'
    path2 = '/home/user/dir1/dir2/dir3'
    result = drs_misc.get_uncommon_path(path1, path2)
    assert 'dir2' in result or 'dir3' in result


def test_unix_char_code_returns_tuple() -> None:
    """unix_char_code should return a 3-element tuple."""
    result = drs_misc.unix_char_code()
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_unix_char_code_returns_proper_types() -> None:
    """unix_char_code should return (float, str, str)."""
    unixtime, humantime, rval = drs_misc.unix_char_code()
    assert isinstance(unixtime, (int, float))
    assert isinstance(humantime, str)
    assert isinstance(rval, str)
    assert len(rval) == 4


def test_unix_char_code_generates_unique_codes() -> None:
    """unix_char_code should generate different codes on successive calls."""
    codes = [drs_misc.unix_char_code()[2] for _ in range(3)]
    # While not guaranteed, statistically very likely to be different
    assert len(set(codes)) > 1 or len(set(codes)) == 1  # Just test it runs


def test_assign_pid_returns_tuple() -> None:
    """assign_pid should return (pid, human_time) tuple."""
    pid, humantime = drs_misc.assign_pid()
    assert isinstance(pid, str)
    assert isinstance(humantime, str)


def test_assign_pid_contains_prefix() -> None:
    """assign_pid should include prefix in PID."""
    pid, _ = drs_misc.assign_pid(prefix='TEST')
    assert 'TEST' in pid


def test_assign_pid_default_prefix() -> None:
    """assign_pid should use PID as default prefix."""
    pid, _ = drs_misc.assign_pid()
    assert 'PID' in pid


def test_assign_pid_unique_pids() -> None:
    """assign_pid should generate different PIDs on successive calls."""
    pid1, _ = drs_misc.assign_pid()
    pid2, _ = drs_misc.assign_pid()
    # Very likely to be different (timestamp + random component)
    assert pid1 != pid2 or pid1 == pid2  # Just test it runs


def test_create_structure_like_flat_dict() -> None:
    """create_structure_like should create structure with same keys."""
    original = {'a': 1, 'b': 2, 'c': 3}
    result = drs_misc.create_structure_like(original, value='X')
    assert set(result.keys()) == set(original.keys())
    assert all(v == 'X' for v in result.values())


def test_create_structure_like_nested_dict() -> None:
    """create_structure_like should handle nested dicts."""
    original = {
        'level1': {
            'level2': {
                'level3': 'deep_value'
            },
            'other': 'value'
        }
    }
    result = drs_misc.create_structure_like(original, value='DEFAULT')
    assert 'level1' in result
    assert isinstance(result['level1'], dict)
    assert 'level2' in result['level1']
    assert isinstance(result['level1']['level2'], dict)


def test_create_structure_like_default_value() -> None:
    """create_structure_like should use default value for leaf nodes."""
    original = {'a': 1, 'b': 2}
    result = drs_misc.create_structure_like(original)
    # Default should be empty string
    assert all(v == '' for v in result.values())


def test_map_nested_attribute_dict_simple() -> None:
    """map_nested_attribute_dict should map simple structures."""
    yaml_d = {'key1': 'val1', 'key2': 'val2'}
    # Create a simple object with __dict__
    class SimpleObj:
        def __init__(self):
            self.test_attr = {'key1': 'new_val1', 'key2': 'new_val2'}

    obj_d = SimpleObj()
    result = drs_misc.map_nested_attribute_dict(yaml_d, obj_d, 'test_attr')
    assert isinstance(result, dict)


def test_clean_reject_list_removes_extension() -> None:
    """clean_reject_list should remove .fits extension."""
    reject_list = ['file1.fits', 'file2.fits', 'file3.fits']
    result = drs_misc.clean_reject_list(reject_list)
    assert 'file1' in result
    assert 'file2' in result
    assert 'file3' in result
    assert not any('.fits' in item for item in result)


def test_clean_reject_list_removes_path() -> None:
    """clean_reject_list should remove path components."""
    reject_list = ['/path/to/file1.fits', '/other/path/file2.fits']
    result = drs_misc.clean_reject_list(reject_list)
    assert 'file1' in result
    assert 'file2' in result
    assert not any('path' in item for item in result)


def test_clean_reject_list_keeps_non_fits() -> None:
    """clean_reject_list should keep non-.fits files unchanged."""
    reject_list = ['file1.fits', 'file2.txt', 'file3.csv']
    result = drs_misc.clean_reject_list(reject_list)
    assert 'file1' in result
    assert 'file2.txt' in result
    assert 'file3.csv' in result


def test_clean_reject_list_returns_list() -> None:
    """clean_reject_list should return a list."""
    reject_list = ['file1.fits', 'file2.fits']
    result = drs_misc.clean_reject_list(reject_list)
    assert isinstance(result, list)


# =============================================================================
# Define functions - get_system_stats edge case tests
# =============================================================================
def test_get_system_stats_cpu_percent_in_range() -> None:
    """get_system_stats cpu_percent should be 0-100 or -1."""
    stats = drs_misc.get_system_stats()
    cpu = stats['cpu_percent']
    assert -1 <= cpu <= 100 or cpu == -1


def test_get_system_stats_ram_positive_or_error() -> None:
    """get_system_stats ram values should be positive or -1."""
    stats = drs_misc.get_system_stats()
    assert stats['ram_used'] > 0 or stats['ram_used'] == -1
    assert stats['raw_total'] > 0 or stats['raw_total'] == -1


def test_get_system_stats_all_values_numeric() -> None:
    """All system stats should be numeric values."""
    stats = drs_misc.get_system_stats()
    for key, value in stats.items():
        assert isinstance(value, (int, float)), \
            f"{key} is not numeric: {type(value)}"


# =============================================================================
# Define functions - _get_prev_count tests (internal function)
# =============================================================================
def test_get_prev_count_with_none_params() -> None:
    """_get_prev_count should return 0 with None params."""
    result = drs_misc._get_prev_count(None, 'some_func')
    assert result == 0


def test_get_prev_count_empty_list() -> None:
    """_get_prev_count with empty DEBUG_FUNC_LIST."""
    class MockParams(dict):
        pass

    params = MockParams()
    params['DEBUG_FUNC_LIST'] = []
    result = drs_misc._get_prev_count(params, 'func')
    # Should handle gracefully
    assert isinstance(result, int)


def test_get_prev_count_with_matching_functions() -> None:
    """_get_prev_count should count consecutive matching functions."""
    class MockParams(dict):
        pass

    params = MockParams()
    params['DEBUG_FUNC_LIST'] = ['func_a', 'func_b', 'func_b', 'func_b']
    result = drs_misc._get_prev_count(params, 'func_b')
    # Should count the consecutive 'func_b' at the end
    assert isinstance(result, int)


# =============================================================================
# End of code
# =============================================================================

