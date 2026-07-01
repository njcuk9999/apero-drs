#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for general path/file helpers in `apero.io.drs_path`."""

import hashlib
import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

_DRS_CFG = Path(tempfile.mkdtemp(prefix='apero_drs_test_cfg_'))
(_DRS_CFG / 'database.yaml').write_text('{}', encoding='utf-8')
(_DRS_CFG / 'install.yaml').write_text('{}', encoding='utf-8')
os.environ.setdefault('DRS_UCONFIG', str(_DRS_CFG))

from apero.io import drs_path


def test_get_uncommon_path_returns_only_suffix_path() -> None:
    """`get_uncommon_path` should return portion unique to first path."""
    path1 = '/tmp/root/a/b'
    path2 = '/tmp/root'
    uncommon = drs_path.get_uncommon_path(path1, path2)
    assert 'a' in uncommon and 'b' in uncommon


def test_group_files_by_time_groups_close_times() -> None:
    """Times within threshold should get same group identifier."""
    # Times are in days here; threshold is converted from hours to days.
    times = np.array([0.0, 0.01, 0.5])
    groups = drs_path.group_files_by_time(times, 1.0, time_unit='hours')
    assert groups[0] == groups[1]
    assert groups[2] != groups[0]


def test_group_files_by_time_invalid_unit_raises() -> None:
    """Unsupported time-unit strings should raise an exception."""
    times = np.array([0.0, 1.0])
    with pytest.raises(Exception):
        drs_path.group_files_by_time(times, 1.0, time_unit='minutes')


def test_get_most_recent_matches_max_ctime(tmp_path) -> None:
    """Most-recent helper should match max creation-time in file list."""
    f1 = tmp_path / 'a.txt'
    f2 = tmp_path / 'b.txt'
    f1.write_text('one', encoding='utf-8')
    f2.write_text('two', encoding='utf-8')
    filelist = [str(f1), str(f2)]
    expected = max(os.path.getctime(v) for v in filelist)
    assert drs_path.get_most_recent(filelist) == expected


def test_makedirs_and_nofiles_and_listfiles(tmp_path) -> None:
    """Directory helpers should create paths and classify empty/non-empty."""
    target = tmp_path / 'x' / 'y'
    drs_path.makedirs(str(target))
    assert target.is_dir()
    assert drs_path.nofiles(str(target))
    test_file = target / 'file.txt'
    test_file.write_text('data', encoding='utf-8')
    assert not drs_path.nofiles(str(target))
    files = drs_path.listfiles(str(target))
    assert str(test_file) in files


def test_get_dirs_relative_and_absolute(tmp_path) -> None:
    """`get_dirs` should return absolute and relative paths as requested."""
    (tmp_path / 'a').mkdir()
    (tmp_path / 'a' / 'b').mkdir()
    abs_dirs = drs_path.get_dirs(str(tmp_path), relative=False)
    rel_dirs = drs_path.get_dirs(str(tmp_path), relative=True)
    assert str(tmp_path) in abs_dirs
    assert 'a' in rel_dirs


def test_get_all_non_empty_subdirs_returns_expected_relative_paths(
    tmp_path,
) -> None:
    """Only subdirectories containing files should be returned."""
    d1 = tmp_path / 'with_file'
    d2 = tmp_path / 'empty'
    d1.mkdir()
    d2.mkdir()
    (d1 / 'x.txt').write_text('x', encoding='utf-8')
    out = drs_path.get_all_non_empty_subdirs(str(tmp_path), relative=True)
    assert any('with_file' in item for item in out)
    assert not any('empty' == item for item in out)


def test_calculate_checksum_matches_python_hashlib(tmp_path) -> None:
    """Checksum helper should match hashlib md5 digest."""
    fpath = tmp_path / 'hash.txt'
    payload = b'checksum content\n'
    fpath.write_bytes(payload)
    expected = hashlib.md5(payload).hexdigest()
    assert drs_path.calculate_checksum(str(fpath)) == expected


def test_make_and_extract_tarfile_round_trip(tmp_path) -> None:
    """Tar helpers should archive and restore directory contents."""
    src = tmp_path / 'src'
    src.mkdir()
    (src / 'a.txt').write_text('A', encoding='utf-8')
    tarname = tmp_path / 'bundle.tar.gz'
    outdir = tmp_path / 'out'
    outdir.mkdir()
    drs_path.make_tarfile(str(tarname), str(src))
    drs_path.extract_tarfile(str(tarname), str(outdir))
    extracted = outdir / src.name / 'a.txt'
    assert extracted.is_file()
    assert extracted.read_text(encoding='utf-8') == 'A'


