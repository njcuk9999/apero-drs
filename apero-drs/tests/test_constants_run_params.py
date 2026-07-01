#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for small helpers in ``apero.constants.run_params``."""

from apero.constants import run_params


# =============================================================================
# Define functions
# =============================================================================
def test_run_param_add_updates_registry_and_position(monkeypatch) -> None:
    """`RunParam.add` should set position and store item in RUN_KEYS."""
    monkeypatch.setattr(run_params, 'RUN_KEYS', {})
    monkeypatch.setattr(run_params, 'POS', 0)

    item = run_params.RunParam(
        name='TEST_KEY',
        value=5,
        dtype=int,
        section='Section',
    )
    item.add()

    assert item.position == 1
    assert run_params.RUN_KEYS['TEST_KEY'] is item
    assert run_params.POS == 1


def test_run_param_create_comment_with_section_header() -> None:
    """`create_comment` should include section header and wrapped comment."""
    item = run_params.RunParam(
        name='KEY',
        section='Science options',
        comment='This is a deliberately long comment for wrapping checks.',
    )

    result = item.create_comment(current_section_title='Core options')

    assert result is not None
    assert 'Science options' in result
    assert '-' * run_params.MAX_WIDTH in result
    assert 'deliberately long comment' in result


def test_run_param_create_comment_returns_none_without_content() -> None:
    """No section change and no comment should return ``None``."""
    item = run_params.RunParam(name='KEY', section='Core options', comment=None)

    assert item.create_comment(current_section_title='Core options') is None


def test_run_param_copy_is_independent_of_original() -> None:
    """`copy` should deep-copy mutable values and preserve metadata."""
    item = run_params.RunParam(
        name='KEY',
        value={'a': [1, 2]},
        dtype=dict,
        dtypei=int,
        comment='comment',
        section='section',
        after='OTHER',
        disabled=True,
        position=10,
    )

    copied = item.copy()
    copied.value['a'].append(3)

    assert copied is not item
    assert copied.name == item.name
    assert copied.position == 10
    assert item.value == {'a': [1, 2]}
    assert copied.value == {'a': [1, 2, 3]}

