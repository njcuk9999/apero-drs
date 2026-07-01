#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extended tests for additional helpers in `apero.io.drs_path`."""

from pathlib import Path

import numpy as np
import pytest

from apero.io import drs_path


def test_copyfile_copies_existing_source(tmp_path) -> None:
    """`copyfile` should copy an existing source file to destination."""
    src = tmp_path / 'src.txt'
    dst = tmp_path / 'dst.txt'
    src.write_text('abc', encoding='utf-8')
    drs_path.copyfile(str(src), str(dst), log=False)
    assert dst.read_text(encoding='utf-8') == 'abc'


def test_copyfile_missing_source_raises(tmp_path) -> None:
    """`copyfile` should raise when source file does not exist."""
    src = tmp_path / 'nope.txt'
    dst = tmp_path / 'dst.txt'
    with pytest.raises(Exception):
        drs_path.copyfile(str(src), str(dst), log=False)


def test_copy_element_for_file_and_directory(tmp_path) -> None:
    """`copy_element` should work for file paths and directory trees."""
    src_file = tmp_path / 'a.txt'
    dst_file = tmp_path / 'b.txt'
    src_file.write_text('one', encoding='utf-8')
    drs_path.copy_element(str(src_file), str(dst_file))
    assert dst_file.read_text(encoding='utf-8') == 'one'

    src_dir = tmp_path / 'srcdir'
    dst_dir = tmp_path / 'dstdir'
    src_dir.mkdir()
    (src_dir / 'x.txt').write_text('x', encoding='utf-8')
    drs_path.copy_element(str(src_dir), str(dst_dir))
    assert (dst_dir / 'x.txt').is_file()


def test_numpy_load_reads_standard_npy_file(tmp_path) -> None:
    """`numpy_load` should read arrays saved via `np.save`."""
    arr = np.array([1, 2, 3])
    fname = tmp_path / 'arr.npy'
    np.save(fname, arr)
    out = drs_path.numpy_load(str(fname))
    assert np.array_equal(out, arr)


def test_numpy_load_invalid_file_raises_value_error(tmp_path) -> None:
    """`numpy_load` should raise ValueError for non-numpy payload files."""
    bad = tmp_path / 'bad.npy'
    bad.write_text('not a numpy file', encoding='utf-8')
    with pytest.raises(ValueError):
        drs_path.numpy_load(str(bad))


def test_listdirs_returns_only_non_empty_directories(tmp_path) -> None:
    """`listdirs` should include non-empty dirs and recurse children."""
    non_empty = tmp_path / 'a'
    empty = tmp_path / 'b'
    child = non_empty / 'child'
    non_empty.mkdir()
    empty.mkdir()
    child.mkdir()
    (non_empty / 'f.txt').write_text('x', encoding='utf-8')
    (child / 'g.txt').write_text('y', encoding='utf-8')
    out = drs_path.listdirs(str(tmp_path))
    assert str(non_empty) in out
    assert str(child) in out
    assert str(empty) not in out


def test_recursive_path_glob_filters_by_prefix_and_suffix(tmp_path) -> None:
    """Recursive glob should honor both prefix and suffix filters."""
    sub = tmp_path / 'sub'
    sub.mkdir()
    (tmp_path / 'keep_a.txt').write_text('1', encoding='utf-8')
    (tmp_path / 'drop_a.log').write_text('2', encoding='utf-8')
    (sub / 'keep_b.txt').write_text('3', encoding='utf-8')
    out = drs_path.recursive_path_glob(
        params={},
        path=tmp_path,
        prefix='keep',
        suffix='.txt',
        job_msg='',
    )
    basenames = sorted([p.name for p in out])
    assert basenames == ['keep_a.txt', 'keep_b.txt']


def test_remove_broken_symlinks_removes_dead_link(
    tmp_path,
    monkeypatch,
) -> None:
    """Broken symlink helper should unlink dead symlinks recursively."""
    monkeypatch.setattr(drs_path, 'WLOG', lambda *a, **k: None)
    target = tmp_path / 'missing.txt'
    link = tmp_path / 'dead.lnk'
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip('symlink not supported in this environment')
    assert link.is_symlink()
    drs_path.remove_broken_symlinks({}, str(tmp_path))
    assert not link.exists()


def test_make_tarfile_with_excludes_skips_expected_files(tmp_path) -> None:
    """Tar creation should exclude paths matching configured prefix/suffix."""
    src = tmp_path / 'src'
    src.mkdir()
    keep = src / 'keep.txt'
    drop_suf = src / 'drop.tmp'
    keep.write_text('ok', encoding='utf-8')
    drop_suf.write_text('bad', encoding='utf-8')
    tarname = tmp_path / 'x.tar.gz'
    drs_path.make_tarfile(str(tarname), str(src),
                          exclude_suffixes=['.tmp'])
    out = tmp_path / 'out'
    out.mkdir()
    drs_path.extract_tarfile(str(tarname), str(out))
    assert (out / 'src' / 'keep.txt').is_file()
    assert not (out / 'src' / 'drop.tmp').exists()


