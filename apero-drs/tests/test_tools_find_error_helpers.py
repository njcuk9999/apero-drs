#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for filesystem/text helper functions in `find_error`."""

from apero.tools.module.error import find_error


# =============================================================================
# Define functions
# =============================================================================
def test_find_all_py_files_finds_python_and_skips_symlink(tmp_path) -> None:
    """Finder should include .py files but ignore symlinked files."""
    subdir = tmp_path / 'subdir'
    subdir.mkdir()

    f1 = tmp_path / 'a.py'
    f2 = subdir / 'b.py'
    f3 = tmp_path / 'not_python.txt'
    f1.write_text('print("a")\n', encoding='utf-8')
    f2.write_text('print("b")\n', encoding='utf-8')
    f3.write_text('x\n', encoding='utf-8')

    link = tmp_path / 'link.py'
    link.symlink_to(f1)

    files = find_error.find_all_py_files(str(tmp_path))
    values = set(list(files))

    assert str(f1) in values
    assert str(f2) in values
    assert str(link) not in values


def test_open_all_py_files_reads_lines_and_relative_names(
    tmp_path, monkeypatch
) -> None:
    """Open helper should flatten lines and return relative file labels."""
    f1 = tmp_path / 'alpha.py'
    f2 = tmp_path / 'sub' / 'beta.py'
    f2.parent.mkdir()
    f1.write_text('line1\nline2\n', encoding='utf-8')
    f2.write_text('line3\n', encoding='utf-8')

    def _fake_relative_folder(package, rel):
        _ = package, rel
        return str(tmp_path)

    monkeypatch.setattr(
        'apero.tools.module.error.find_error.drs_misc.get_relative_folder',
        _fake_relative_folder,
    )

    entries, line_nums, files = find_error.open_all_py_files(
        [str(f1), str(f2)]
    )

    assert entries[0].strip() == 'line1'
    assert entries[2].strip() == 'line3'
    assert line_nums == [0, 1, 0]
    assert files[0] == 'alpha.py'
    assert files[2].endswith('sub/beta.py')


def test_search_for_database_entry_returns_all_matches() -> None:
    """Search helper should collect line numbers and file names for matches."""
    entries = ['abc 10', 'no match', 'abc 20']
    line_nums = [4, 8, 15]
    files = ['f1.py', 'f2.py', 'f3.py']

    found, nums, fnames = find_error.search_for_database_entry(
        'abc', entries, line_nums, files
    )

    assert found is True
    assert nums == [4, 15]
    assert fnames == ['f1.py', 'f3.py']


