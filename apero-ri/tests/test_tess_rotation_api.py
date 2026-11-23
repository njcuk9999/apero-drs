#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Offline regressions for TESS rotation cache and execution dispatch."""

from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from flask import Flask
import pytest

from apero_ri.application import data_portal_api_helpers as helpers
from apero_ri.core import plot_cache
from apero_ri.core import run_tessilator


@pytest.mark.parametrize('cached', [False, True])
def test_tess_rotation_cache_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, cached: bool,
) -> None:
    """Use cache hits directly and run the helper on cache misses.

    :param monkeypatch: Fixture replacing authorization and science boundaries.
    :param tmp_path: Isolated cache root for the request.
    :param cached: Whether a cached result is available.
    :return: None.
    """
    flask_app = Flask(__name__)
    app = SimpleNamespace(args=SimpleNamespace(data_dir=str(tmp_path)),
                          ari_groups=dict(), _get_api_user=lambda: None)
    monkeypatch.setattr(helpers, 'get_public_permissions',
                        lambda: {'view.data_portal'})
    monkeypatch.setattr(helpers, 'get_accessible_profiles', mock.Mock())
    context = dict(instrument='NIRPS_HE', objname='TEST_OBJECT',
                   obj_props=dict(ALIASES='ALIAS_A | ALIAS_B'))
    resolver = mock.Mock(return_value=(True, context))
    monkeypatch.setattr(helpers, '_resolve_target_context', resolver)
    monkeypatch.setattr(plot_cache, 'load_cache_config', mock.Mock())
    cache_root = tmp_path / 'cache'
    root_resolver = mock.Mock(return_value=cache_root)
    monkeypatch.setattr(plot_cache, 'resolve_cache_root', root_resolver)
    result = dict(success=True, sectors=[1])
    cached_result = result if cached else None
    cache_reader = mock.Mock(return_value=cached_result)
    monkeypatch.setattr(run_tessilator, 'get_tess_cached', cache_reader)
    runner = mock.Mock(return_value=result)
    monkeypatch.setattr(run_tessilator, 'run_tessilator', runner)
    with flask_app.test_request_context('/api/tess-rotation'):
        response = helpers.api_tess_rotation(app)
    assert response.get_json() == result
    cache_reader.assert_called_once_with(cache_root, 'NIRPS_HE', 'TEST_OBJECT')
    if cached:
        runner.assert_not_called()
    else:
        run_kwargs = dict(objname='TEST_OBJECT', cache_root=cache_root,
                          instrument='NIRPS_HE', aliases=['ALIAS_A', 'ALIAS_B'])
        runner.assert_called_once_with(**run_kwargs)