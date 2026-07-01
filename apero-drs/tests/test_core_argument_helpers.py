#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for helper functions in `apero.core.drs_argument`."""

from apero.core import drs_argument


# =============================================================================
# Define functions
# =============================================================================
def test_help_format_cleans_text_and_adds_options() -> None:
    """`_help_format` should normalize text and prepend option choices."""
    keys = ['--my-opt', '-m']
    helpstr = (
        '  this has\nnewline and\t tabs and enough words to wrap across '
        'multiple lines cleanly  '
    )

    out = drs_argument._help_format(keys, helpstr, options=['x', 'y'])

    assert out.startswith('--my-opt,-m')
    lines = out.split('\n')
    assert '{x,y}' in lines[1]
    assert '\t' not in ''.join(line.strip() for line in lines[1:])


def test_get_arg_prefers_positional_arguments() -> None:
    """`_get_arg` should return positional value when key exists in both."""
    pos = object()
    opt = object()

    out = drs_argument._get_arg(  # type: ignore[arg-type]
        {'same': pos}, {'same': opt}, 'same'
    )

    assert out is pos


def test_get_arg_returns_none_for_missing_keys() -> None:
    """`_get_arg` should return None when key is not found."""
    out = drs_argument._get_arg({}, {}, 'missing')
    assert out is None


def test_get_file_list_filters_by_extension_and_skips_index(tmp_path) -> None:
    """`_get_file_list` should apply extension filtering and skip index fits."""
    subdir = tmp_path / 'sub'
    subdir.mkdir()
    (tmp_path / 'alpha.py').write_text('print(1)\n', encoding='utf-8')
    (tmp_path / 'beta.txt').write_text('x\n', encoding='utf-8')
    (tmp_path / 'index.fits').write_text('x\n', encoding='utf-8')
    (subdir / 'gamma.py').write_text('print(2)\n', encoding='utf-8')

    flist, limit = drs_argument._get_file_list(
        50, str(tmp_path), ext='.py', recursive=True
    )

    joined = '\n'.join(flist.tolist())
    assert 'alpha.py' in joined
    assert 'gamma.py' in joined
    assert 'index.fits' not in joined
    assert not limit


def test_get_file_list_dir_only_returns_nested_directories(tmp_path) -> None:
    """`_get_file_list` with `dir_only` should list subdirectories."""
    subdir = tmp_path / 'night1'
    subdir.mkdir()
    (subdir / 'file.fits').write_text('x\n', encoding='utf-8')

    flist, limit = drs_argument._get_file_list(
        50, str(tmp_path), recursive=True, dir_only=True
    )

    joined = '\n'.join(flist.tolist())
    assert 'night1' in joined
    assert not limit

