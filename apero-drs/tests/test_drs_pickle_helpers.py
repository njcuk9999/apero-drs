#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for pickle helper functions in `apero.io.drs_pickle`."""

import os
import tempfile
from pathlib import Path

_DRS_CFG = Path(tempfile.mkdtemp(prefix='apero_drs_test_cfg_'))
(_DRS_CFG / 'database.yaml').write_text('{}', encoding='utf-8')
(_DRS_CFG / 'install.yaml').write_text('{}', encoding='utf-8')
os.environ.setdefault('DRS_UCONFIG', str(_DRS_CFG))

from apero.io import drs_pickle


def test_make_and_get_pickle_single_object(tmp_path) -> None:
    """Single pickle write/read should round-trip the stored object."""
    params = {'PATH.OTHER': str(tmp_path)}
    payload = {'value': 42, 'name': 'demo'}
    drs_pickle.make_pickle(params, payload, prefix='p1', suffix=1, log=False)
    out = drs_pickle.get_pickle(params, prefix='p1', suffix=1)
    assert out == payload


def test_get_pickle_without_suffix_returns_sorted_dict(tmp_path) -> None:
    """Reading prefix without suffix should return key-sorted dictionary."""
    params = {'PATH.OTHER': str(tmp_path)}
    drs_pickle.make_pickle(params, 'three', prefix='p2', suffix=3, log=False)
    drs_pickle.make_pickle(params, 'one', prefix='p2', suffix=1, log=False)
    out = drs_pickle.get_pickle(params, prefix='p2', suffix=None)
    assert list(out.keys()) == [1, 3]
    assert out[1] == 'one'
    assert out[3] == 'three'


def test_get_pickle_remove_true_cleans_directory(tmp_path, monkeypatch) -> None:
    """`remove=True` should delete pickle files and their directory."""
    monkeypatch.setattr(drs_pickle, 'WLOG', lambda *a, **k: None)
    params = {'PATH.OTHER': str(tmp_path)}
    drs_pickle.make_pickle(params, [1, 2, 3], prefix='p3', suffix=7, log=False)
    _ = drs_pickle.get_pickle(params, prefix='p3', suffix=7, remove=True)
    pdir = tmp_path / 'pickles' / 'p3'
    assert not pdir.exists()



