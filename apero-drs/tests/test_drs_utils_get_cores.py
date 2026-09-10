#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `get_cores` helper in `apero.utils.drs_utils`."""

from apero.utils import drs_utils


def _base_params(spirou_params):
    """Copy default parameters and reset command-line inputs."""
    params = spirou_params.copy()
    params['INPUTS'] = dict()
    return params


def test_get_cores_uses_input_value(monkeypatch, spirou_params) -> None:
    """Valid INPUTS.CORES should override the configured core count."""
    monkeypatch.setattr(drs_utils, 'WLOG', lambda *a, **k: None)
    params = _base_params(spirou_params)
    params['INPUTS']['CORES'] = '2'
    out = drs_utils.get_cores(params)
    assert out == 2


def test_get_cores_zero_means_all_but_one(monkeypatch, spirou_params) -> None:
    """CORES=0 should map to cpu_count - 1 per helper logic."""
    monkeypatch.setattr(drs_utils, 'WLOG', lambda *a, **k: None)
    params = _base_params(spirou_params)
    params['CORES'] = 0
    out = drs_utils.get_cores(params)
    assert out == (drs_utils.os.cpu_count() - 1)


def test_get_cores_negative_offsets_from_cpu_count(monkeypatch, spirou_params) -> None:
    """Negative core counts should offset from total CPU count."""
    monkeypatch.setattr(drs_utils, 'WLOG', lambda *a, **k: None)
    params = _base_params(spirou_params)
    params['CORES'] = -1
    out = drs_utils.get_cores(params)
    assert out == (drs_utils.os.cpu_count() - 1)


def test_get_cores_invalid_string_falls_back_to_one(monkeypatch,
                                                    spirou_params) -> None:
    """Invalid core strings should trigger fallback to one core."""
    monkeypatch.setattr(drs_utils, 'WLOG', lambda *a, **k: None)
    params = _base_params(spirou_params)
    params['CORES'] = 1
    params['INPUTS']['CORES'] = 'bad'
    out = drs_utils.get_cores(params)
    assert out == 1


