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
    assert b'fo-property-dialog' in response.data
    assert b'ARI_SEARCH_EXAMPLES' in response.data
    assert b'112. matches' in response.data
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


def test_run_id_prefix_and_authorized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prefixes match authorized IDs, without shared-row leakage."""
    from flask import Flask

    flask_app = Flask(__name__)
    profile = dict(profile_id='test', instrument='SPIROU')
    monkeypatch.setattr(astrometrics_api_helpers, 'get_accessible_profiles',
                        lambda *values: [profile])
    user = dict(groups=['public'])
    stub = SimpleNamespace(args=SimpleNamespace(data_dir=str(tmp_path)),
                           ari_groups=permissions.load_groups(),
                           _get_api_user=lambda: user,
                           _get_user_accessible_run_ids=lambda *values:
                           {'R1', '112.A', '112.B'})
    directory = tmp_path / 'tasks/SPIROU/test'
    directory.mkdir(parents=True)
    rows = [dict(OBJNAME='Visible', RUN_ID='R1, PRIVATE'),
            dict(OBJNAME='Prefix', RUN_ID='R10'),
            dict(OBJNAME='First run', RUN_ID='112.A'),
            dict(OBJNAME='Second run', RUN_ID='112.B'),
            dict(OBJNAME='Private run', RUN_ID='R1, 112.PRIVATE')]
    (directory / 'object_table.json').write_text(json.dumps(dict(rows=rows)))
    url = '/api/astrometrics/find-object?search_type=run_id&query='
    with flask_app.test_request_context(url + 'R1'):
        response = astrometrics_api_helpers.api_astrometrics_find_object(stub)
        data = response.get_json()
        names = [item['name'] for item in data['results']['test']]
        assert names == ['Visible', 'Private run']
    with flask_app.test_request_context(url + '112.'):
        response = astrometrics_api_helpers.api_astrometrics_find_object(stub)
        data = response.get_json()
        names = [item['name'] for item in data['results']['test']]
        assert names == ['First run', 'Second run']
    with flask_app.test_request_context(url + 'PRIVATE'):
        response = astrometrics_api_helpers.api_astrometrics_find_object(stub)
        assert response.get_json()['results'] == dict()


def test_property_instruments(tmp_path: Path) -> None:
    """Property instrument filters are specific to their source."""
    profiles = []
    for instrument in ['SPIROU', 'NIRPS']:
        profiles.append(dict(profile_id='test', instrument=instrument))
        directory = tmp_path / 'tasks' / instrument / 'test'
        objects = directory / 'objects'
        objects.mkdir(parents=True)
        rows = [dict(OBJNAME='Star', RUN_ID='R1', TARGET_KEY='value')]
        payload = json.dumps(dict(rows=rows))
        (directory / 'object_table.json').write_text(payload)
        source = 'htable' if instrument == 'SPIROU' else 'ftable_ext'
        rows = [dict(KW_RUN_ID='R1', SHARED_KEY='value')]
        payload = json.dumps(dict(rows=rows))
        (objects / f'{source}_Star.json').write_text(payload)
    stub = SimpleNamespace(_get_user_accessible_run_ids=lambda *values: {'R1'})
    catalog_args = [stub, tmp_path, profiles, None]
    catalog = astrometrics_api_helpers._advanced_property_catalog(*catalog_args)
    assert catalog['instruments'] == ['NIRPS', 'SPIROU']
    shared = next(row for row in catalog['properties']
                  if row['property'] == 'SHARED_KEY')
    assert shared['source_instruments'] == dict(header=['SPIROU'],
                                              spectrum_info=['NIRPS'])
    examples = search_helpers.search_examples()
    assert {row['instrument'] for row in examples} == {
        'SPIROU', 'NIRPS_HA', 'NIRPS_HE',
    }
    keys = {'name', 'coords', 'date', 'run_id', 'header',
            'target_info', 'spectrum_info'}
    assert all(keys <= set(row) for row in examples)


@pytest.mark.parametrize('query, expected', [
    ('search_type=name&query=alias', [('name', 'Full Alias')]),
    ('search_type=run_id&query=112.', [('run id', '112.A')]),
    ('search_type=coords&ra=30&dec=10&separation=1', [('coords', '30.0, 10.0')]),
    ('search_type=date&first_observed=2026-01-01', [('date', '2026-10-07')]),
    ('search_type=advanced&source=target_info&property=TEFF&value=320',
     [('TEFF', '3200')]),
    ('search_type=advanced&source=header&property=EXPTIME&value=60',
     [('EXPTIME', '600')]),
    ('search_type=advanced&source=spectrum_info&property=SNR&value=50',
     [('SNR', '150')]),
])
def test_actual_match_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    query: str, expected: list,
) -> None:
    """Return the data value that matched for each search mode.

    :param tmp_path: Isolated table directory.
    :param monkeypatch: Fixture replacing profile access.
    :param query: Search request arguments.
    :param expected: Matched property/value pairs.
    :return: None.
    """
    from flask import Flask

    profile = dict(instrument='SPIROU', profile_id='test')
    monkeypatch.setattr(astrometrics_api_helpers, 'get_accessible_profiles',
                        lambda *values: [profile])
    stub = SimpleNamespace(args=SimpleNamespace(data_dir=str(tmp_path)),
                           ari_groups=permissions.load_groups(),
                           _get_api_user=lambda: dict(groups=['public']),
                           _get_user_accessible_run_ids=lambda *values:
                           {'112.A'})
    directory = tmp_path / 'tasks/SPIROU/test'
    objects = directory / 'objects'
    objects.mkdir(parents=True)
    row = dict(OBJNAME='Canonical', ALIASES='Full Alias', RUN_ID='112.A',
               RA=30, DEC=10, OBS_DATE='2026-10-07', TEFF=3200)
    payload = json.dumps(dict(rows=[row]))
    (directory / 'object_table.json').write_text(payload)
    spectrum = dict(KW_RUN_ID='112.A', IDENTIFIER='exposure', SNR=150)
    (objects / 'ftable_ext_Canonical.json').write_text(
        json.dumps(dict(rows=[spectrum])))
    header = dict(IDENTIFIER='exposure', EXPTIME=600)
    (objects / 'htable_Canonical.json').write_text(
        json.dumps(dict(rows=[header])))
    flask_app = Flask(__name__)
    with flask_app.test_request_context('/?' + query):
        response = astrometrics_api_helpers.api_astrometrics_find_object(stub)
    result = response.get_json()['results']['test'][0]
    assert result['name'] == 'Canonical'
    assert result['matches'] == [dict(property=key, value=value)
                                 for key, value in expected]