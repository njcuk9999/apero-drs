#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for drs_misc.py Colors and helper functions."""

import pickle
from aperocore.core import drs_misc


# =============================================================================
# Define functions - Colors class tests
# =============================================================================
def test_colors_initializes_with_default_theme() -> None:
    """Colors should initialize with DARK theme by default."""
    colors = drs_misc.Colors()
    assert colors.theme == 'DARK'


def test_colors_initializes_with_custom_theme() -> None:
    """Colors should initialize with specified theme."""
    colors = drs_misc.Colors(theme='LIGHT')
    assert colors.theme == 'LIGHT'


def test_colors_initializes_all_color_codes() -> None:
    """Colors should initialize all color attributes."""
    colors = drs_misc.Colors()
    # Check basic colors exist
    assert hasattr(colors, 'BLACK1')
    assert hasattr(colors, 'RED1')
    assert hasattr(colors, 'GREEN1')
    assert hasattr(colors, 'YELLOW1')
    assert hasattr(colors, 'BLUE1')
    assert hasattr(colors, 'MAGENTA1')
    assert hasattr(colors, 'CYAN1')
    assert hasattr(colors, 'WHITE1')
    # Check that they're all strings (ANSI codes)
    assert isinstance(colors.BLACK1, str)
    assert isinstance(colors.RED1, str)
    assert len(colors.RED1) > 0


def test_colors_has_themed_attributes() -> None:
    """Colors should have themed attributes (header, ok, warning, etc)."""
    colors = drs_misc.Colors()
    assert hasattr(colors, 'header')
    assert hasattr(colors, 'okblue')
    assert hasattr(colors, 'okgreen')
    assert hasattr(colors, 'ok')
    assert hasattr(colors, 'warning')
    assert hasattr(colors, 'fail')
    assert hasattr(colors, 'debug')
    assert hasattr(colors, 'endc')


def test_colors_dark_theme_sets_appropriate_colors() -> None:
    """Colors DARK theme should map to DARK color scheme."""
    colors = drs_misc.Colors(theme='DARK')
    assert colors.header == colors.MAGENTA1
    assert colors.okblue == colors.BLUE1
    assert colors.okgreen == colors.GREEN1
    assert colors.warning == colors.YELLOW1
    assert colors.fail == colors.RED1


def test_colors_light_theme_sets_appropriate_colors() -> None:
    """Colors LIGHT theme should map to LIGHT color scheme."""
    colors = drs_misc.Colors(theme='LIGHT')
    assert colors.header == colors.MAGENTA2
    assert colors.okblue == colors.MAGENTA2
    assert colors.okgreen == colors.BLACK2
    assert colors.warning == colors.BLUE2
    assert colors.fail == colors.RED2


def test_colors_update_theme_changes_scheme() -> None:
    """update_theme should change color scheme."""
    colors = drs_misc.Colors(theme='DARK')
    assert colors.header == colors.MAGENTA1
    colors.update_theme('LIGHT')
    assert colors.header == colors.MAGENTA2
    assert colors.theme == 'LIGHT'


def test_colors_print_with_valid_color() -> None:
    """print should return colored string for valid colors."""
    colors = drs_misc.Colors()
    result = colors.print('test message', 'red')
    assert 'test message' in result
    assert colors.RED1 in result
    assert colors.endc in result


def test_colors_print_with_color_shorthand() -> None:
    """print should accept color shorthands like 'r', 'b', 'g'."""
    colors = drs_misc.Colors()
    result_r = colors.print('test', 'r')
    result_red = colors.print('test', 'red')
    assert result_r == result_red


def test_colors_print_with_all_valid_colors() -> None:
    """print should work with all valid color codes."""
    colors = drs_misc.Colors()
    valid_colors = ['b', 'blue', 'r', 'red', 'g', 'green',
                    'y', 'yellow', 'm', 'magenta', 'k', 'black', 'grey']
    for color in valid_colors:
        result = colors.print('msg', color)
        assert 'msg' in result
        assert colors.endc in result


def test_colors_print_with_invalid_color() -> None:
    """print should handle invalid colors gracefully."""
    colors = drs_misc.Colors()
    result = colors.print('test', 'invalid')
    assert 'test' in result
    assert colors.endc in result


def test_colors_str_representation() -> None:
    """__str__ should return proper Colors representation."""
    colors = drs_misc.Colors(theme='DARK')
    str_repr = str(colors)
    assert 'Colors' in str_repr
    assert 'DARK' in str_repr


def test_colors_pickle_and_unpickle() -> None:
    """Colors should be pickleable and unpickleable."""
    colors = drs_misc.Colors(theme='LIGHT')
    # Pickle and unpickle
    pickled = pickle.dumps(colors)
    unpickled = pickle.loads(pickled)
    # Verify theme and attributes are preserved
    assert unpickled.theme == 'LIGHT'
    assert unpickled.header == colors.MAGENTA2


# =============================================================================
# Define functions - display_func tests
# =============================================================================
def test_display_func_with_name_only() -> None:
    """display_func with only name should format correctly."""
    result = drs_misc.display_func(name='my_function')
    assert result == 'my_function()'


def test_display_func_with_name_and_program() -> None:
    """display_func with name and program should format correctly."""
    result = drs_misc.display_func(name='method', program='module')
    assert result == 'module.method()'


def test_display_func_with_all_params() -> None:
    """display_func with all params should format correctly."""
    result = drs_misc.display_func(
        name='method',
        program='module',
        class_name='MyClass'
    )
    assert result == 'module.MyClass.method()'


def test_display_func_with_none_name() -> None:
    """display_func should use 'Unknown' when name is None."""
    result = drs_misc.display_func(name=None)
    assert result == 'Unknown()'


def test_display_func_invalid_name_type_raises_error() -> None:
    """display_func should raise ValueError for non-string name."""
    try:
        drs_misc.display_func(name=123)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert 'not string' in str(e).lower()


def test_display_func_with_program_only() -> None:
    """display_func with program only should work."""
    result = drs_misc.display_func(name='func', program='prog')
    assert result == 'prog.func()'


def test_display_func_with_class_only() -> None:
    """display_func with class name only should work."""
    result = drs_misc.display_func(name='method', class_name='Class')
    assert result == 'Class.method()'


def test_display_func_empty_program_ignored() -> None:
    """display_func should ignore None program and class."""
    result = drs_misc.display_func(
        name='func',
        program=None,
        class_name=None
    )
    assert result == 'func()'


# =============================================================================
# Define functions - utility function tests
# =============================================================================
def test_get_system_stats_returns_dict() -> None:
    """get_system_stats should return a dictionary."""
    stats = drs_misc.get_system_stats()
    assert isinstance(stats, dict)


def test_get_system_stats_contains_expected_keys() -> None:
    """get_system_stats should contain expected stat keys."""
    stats = drs_misc.get_system_stats()
    expected_keys = [
        'ram_used', 'raw_total', 'swap_used', 'swap_total',
        'cpu_percent', 'cpu_total'
    ]
    for key in expected_keys:
        assert key in stats


def test_get_system_stats_values_are_numeric() -> None:
    """get_system_stats values should be numeric."""
    stats = drs_misc.get_system_stats()
    for key, value in stats.items():
        assert isinstance(value, (int, float)), \
            f"{key} value should be numeric, got {type(value)}"


def test_get_system_stats_ram_used_positive_or_error() -> None:
    """get_system_stats ram_used should be positive or -1 on error."""
    stats = drs_misc.get_system_stats()
    assert stats['ram_used'] > 0 or stats['ram_used'] == -1


def test_get_system_stats_cpu_count_positive_or_error() -> None:
    """get_system_stats cpu_total should be positive or -1 on error."""
    stats = drs_misc.get_system_stats()
    assert stats['cpu_total'] > 0 or stats['cpu_total'] == -1


# =============================================================================
# End of code
# =============================================================================

