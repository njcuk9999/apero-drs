#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused tests for the unified Search page."""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from apero import dev

from apero_ri.application import astrometrics_api_helpers
from apero_ri.application import search_helpers
from apero_ri.core import auth, permissions
from tests.test_run_ids import app


def test_search_page(client: Any) -> None:
    """Search is registered and finder controls no longer live in Astro."""
    assert dev is not None
    response = client.get('/search')
    assert response.status_code == 200
    assert b'fo-tab-run-id' in response.data
    assert b'search-page-query' in response.data
    assert b'search-version' in response.data
    pages = permissions.load_pages()
    definition = pages['home.search']
    assert definition['quick-nav']
    assert definition['side-nav']['pinned']
    assert definition['parent'] == 'home'
    response = client.get('/astrometrics')
    assert response.status_code == 200
    assert b'fo-name-query' not in response.data
    assert b'please click here' in response.data
    assert b'astro-tab-resolve-target' in response.data


def test_search_permissions(
    client: Any, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Site search indexes permitted page text without exposing admin pages."""
    monkeypatch.setattr(auth, 'get_effective_user', lambda session: None)
    monkeypatch.setattr(search_helpers.docs, 'get_search_index',
                        lambda version: [dict(label='Test Doc',
                                             url='/docs/test',
                                             keywords='test phrase')])
    response = client.get('/api/search/index?scope=docs')
    items = response.get_json()['items']
    assert len(items) == 1
    assert items[0]['label'] == 'Test Doc'
    response = client.get('/api/search/index?scope=site')
    items = response.get_json()['items']
    urls = {item['url'] for item in items}
    assert '/search' in urls
    assert '/astrometrics' in urls
    assert '/admin_portal/run_ids' not in urls
    assert '/user_portal' not in urls
    assert not any('script src' in item['keywords'] for item in items)


def test_run_id_exact_and_authorized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RUN ID lookup matches whole IDs and denies shared-row leakage."""
    from flask import Flask

    flask_app = Flask(__name__)
    profile = dict(profile_id='test', instrument='SPIROU')
    monkeypatch.setattr(astrometrics_api_helpers, 'get_accessible_profiles',
                        lambda *values: [profile])
    user = dict(groups=['public'])
    stub = SimpleNamespace(args=SimpleNamespace(data_dir=str(tmp_path)),
                           ari_groups=permissions.load_groups(),
                           _get_api_user=lambda: user,
                           _get_user_accessible_run_ids=lambda *values: {'R1'})
    directory = tmp_path / 'tasks/SPIROU/test'
    directory.mkdir(parents=True)
    rows = [dict(OBJNAME='Visible', RUN_ID='R1, PRIVATE'),
            dict(OBJNAME='Prefix', RUN_ID='R10')]
    (directory / 'object_table.json').write_text(json.dumps(dict(rows=rows)))
    url = '/api/astrometrics/find-object?search_type=run_id&query='
    with flask_app.test_request_context(url + 'R1'):
        response = astrometrics_api_helpers.api_astrometrics_find_object(stub)
        data = response.get_json()
        assert [item['name'] for item in data['results']['test']] == ['Visible']
    with flask_app.test_request_context(url + 'PRIVATE'):
        response = astrometrics_api_helpers.api_astrometrics_find_object(stub)
        assert response.get_json()['results'] == dict()