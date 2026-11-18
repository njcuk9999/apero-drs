#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused Search index persistence and permission tests."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from apero import dev

from apero_ri.core import search_index


def _table(path: Path, rows: list) -> None:
    """Write rows to an isolated JSON table and return None."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(rows=rows)), encoding='utf-8')


def _profile(base_dir: Path) -> dict:
    """Seed a temporary profile and return its plain descriptor."""
    assert dev is not None
    profile = dict(instrument='SPIROU', profile_id='test')
    directory = base_dir / 'tasks/SPIROU/test'
    rows = [dict(OBJNAME='Star', RUN_ID='PUBLIC, PRIVATE')]
    _table(directory / 'object_table.json', rows)
    rows = [dict(KW_RUN_ID='PUBLIC', IDENTIFIER='visible', FLUX=1),
            dict(KW_RUN_ID='PRIVATE', IDENTIFIER='hidden', SECRET=1)]
    _table(directory / 'objects/ftable_ext_Star.json', rows)
    rows = [dict(IDENTIFIER='visible', PUBLIC_HEADER=1),
            dict(IDENTIFIER='hidden', PRIVATE_HEADER=1),
            dict(UNSCOPED_HEADER=1)]
    _table(directory / 'objects/htable_Star.json', rows)
    return profile


def test_cached_read_and_permissions(tmp_path: Path,
                                     monkeypatch: pytest.MonkeyPatch) -> None:
    """Warm catalogs never scan and filter current run/profile access."""
    profile = _profile(tmp_path)
    access = dict(SPIROU={'PUBLIC'})
    catalog = search_index.catalog(tmp_path, [profile], access)
    keys = {row['property'] for row in catalog['properties']}
    assert {'FLUX', 'PUBLIC_HEADER'} <= keys
    assert not {'SECRET', 'PRIVATE_HEADER', 'UNSCOPED_HEADER'} & keys

    def fail_scan(*values: object) -> dict:
        """Reject a repeated disk scan."""
        pytest.fail('Warm catalog scanned data tables')

    monkeypatch.setattr(search_index, 'scan_profile', fail_scan)
    search_index._CACHE.clear()
    assert search_index.catalog(tmp_path, [profile], access) == catalog
    private = search_index.catalog(tmp_path, [profile],
                                   dict(SPIROU={'PRIVATE'}))
    keys = {row['property'] for row in private['properties']}
    assert {'SECRET', 'PRIVATE_HEADER'} <= keys
    assert 'PUBLIC_HEADER' not in keys
    assert not search_index.catalog(tmp_path, [], access)['properties']


def test_all_objects(tmp_path: Path) -> None:
    """Keys beyond the former fifty-object limit are indexed."""
    profile = _profile(tmp_path)
    directory = tmp_path / 'tasks/SPIROU/test'
    rows = [dict(OBJNAME=f'Star{number}', RUN_ID='PUBLIC')
            for number in range(60)]
    _table(directory / 'object_table.json', rows)
    rows = [dict(KW_RUN_ID='PUBLIC', LAST_OBJECT_KEY=1)]
    _table(directory / 'objects/ftable_ext_Star59.json', rows)
    catalog = search_index.catalog(tmp_path, [profile],
                                   dict(SPIROU={'PUBLIC'}))
    assert 'LAST_OBJECT_KEY' in {row['property']
                                 for row in catalog['properties']}


def test_stale_refresh_and_failure(tmp_path: Path,
                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """Serve stale data while refreshing; failed scans preserve old JSON."""
    profile = _profile(tmp_path)
    search_index.refresh_profile(tmp_path, profile)
    path = search_index.index_path(tmp_path, profile)
    index = json.loads(path.read_text())
    index['generated_at'] = 0
    path.write_text(json.dumps(index))
    requested = []
    monkeypatch.setattr(search_index, 'request_refresh',
                        lambda *values: requested.append(values))
    catalog = search_index.catalog(tmp_path, [profile],
                                   dict(SPIROU={'PUBLIC'}))
    assert catalog['status'] == 'stale'
    assert catalog['properties']
    assert len(requested) == 1
    table = tmp_path / 'tasks/SPIROU/test/object_table.json'
    table.write_text('invalid json')
    with pytest.raises(ValueError):
        search_index.refresh_profile(tmp_path, profile)
    assert json.loads(path.read_text()) == index


def test_cold_background(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Cold nonblocking catalogs schedule a build with loading status."""
    profile = _profile(tmp_path)
    requested = []
    monkeypatch.setattr(search_index, 'request_refresh',
                        lambda *values: requested.append(values))
    catalog = search_index.catalog(tmp_path, [profile],
                                   dict(SPIROU={'PUBLIC'}), background=True)
    assert catalog['status'] == 'loading'
    assert catalog['properties'] == []
    assert catalog['instruments'] == []
    assert len(requested) == 1


def test_daily_task(tmp_path: Path,
                    monkeypatch: pytest.MonkeyPatch) -> None:
    """Registry enables daily GLOBAL indexing with plain raw profiles."""
    from apero_ri import tasks
    from apero_ri.tasks import search_indexing

    profile = _profile(tmp_path)
    calls = []

    def load_profiles(hydrate: bool = True) -> dict:
        """Record hydration choice and return raw test profiles."""
        calls.append(hydrate)
        return dict(SPIROU=dict(test=dict()))

    monkeypatch.setattr(search_indexing.auth, 'load_apero_profiles',
                        load_profiles)
    messages = []
    params = dict(LOCAL_DATA_DIR=str(tmp_path), TASK_LOGGER=messages.append)
    task = tasks.TASK_LIST['SEARCH_INDEXING']()
    task.run_job(params)
    assert calls == [False]
    assert messages == ['SPIROU/test: refreshed']
    assert search_index.read_index(tmp_path, profile)['runs']
    assert tasks.FREQ['SEARCH_INDEXING'] == 24.0
    assert tasks.ENABLED['SEARCH_INDEXING']
    assert tasks.TYPE['SEARCH_INDEXING'] == 'GLOBAL'
    assert 'SEARCH_INDEXING' not in tasks.IMPORT_ERRORS


def test_search_columns_bypass_assets(tmp_path: Path,
                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Finder columns bypass astrometrics assets and return loading state."""
    from flask import Flask
    from apero_ri.application import astrometrics_api_helpers as helpers

    profile = _profile(tmp_path)
    monkeypatch.setattr(helpers, 'get_public_permissions',
                        lambda: {'view.data_portal'})
    monkeypatch.setattr(helpers, 'get_accessible_profiles',
                        lambda *values: [profile])

    def fail_assets(*values: object) -> Path:
        """Reject all asset access from the finder endpoint."""
        pytest.fail('Finder accessed astrometrics assets')

    monkeypatch.setattr(helpers, '_astrom_dir', fail_assets)
    monkeypatch.setattr(search_index, 'request_refresh', lambda *values: None)
    stub = SimpleNamespace(args=SimpleNamespace(data_dir=str(tmp_path)),
                           ari_groups=dict(), _get_api_user=lambda: None,
                           _get_user_accessible_run_ids=lambda *values:
                           {'PUBLIC'})
    app = Flask(__name__)
    with app.test_request_context('/api/astrometrics/columns?purpose=search'):
        data = helpers.api_astrometrics_columns(stub).get_json()
        assert data['success']
        assert data['columns'] == []
        assert data['find_object_index_status'] == 'loading'
        assert data['find_object_properties'] == []
        assert data['find_object_instruments'] == []
    monkeypatch.setattr(helpers, 'get_public_permissions', lambda: set())
    with app.test_request_context('/api/astrometrics/columns?purpose=search'):
        response, code = helpers.api_astrometrics_columns(stub)
        assert code == 401


def test_background_deduplicates_and_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Concurrent cold reads share a worker and failed scans back off."""
    profile = _profile(tmp_path)
    workers = []

    class DeferredThread:
        """Capture background work deterministically without starting it."""

        def __init__(self, target: object, daemon: bool) -> None:
            """Capture target and verify daemon mode."""
            self.target = target
            assert daemon

        def start(self) -> None:
            """Record the pending worker."""
            workers.append(self.target)

    monkeypatch.setattr(search_index.threading, 'Thread', DeferredThread)
    search_index.request_refresh(tmp_path, profile)
    search_index.request_refresh(tmp_path, profile)
    assert len(workers) == 1
    workers.pop()()
    assert search_index.read_index(tmp_path, profile) is not None
    path = search_index.index_path(tmp_path, profile)
    path.unlink()
    table = tmp_path / 'tasks/SPIROU/test/object_table.json'
    table.write_text('invalid')
    search_index.request_refresh(tmp_path, profile)
    workers.pop()()
    search_index.request_refresh(tmp_path, profile)
    assert workers == []
    assert path not in search_index._REFRESHING


def test_header_all_linkage(tmp_path: Path) -> None:
    """Use ftable_all for header run attribution, not spectrum properties."""
    profile = _profile(tmp_path)
    directory = tmp_path / 'tasks/SPIROU/test/objects'
    rows = [dict(IDENTIFIER='all-only', KW_RUN_ID='PUBLIC', ALL_ONLY_KEY=1)]
    _table(directory / 'ftable_all_Star.json', rows)
    rows = [dict(IDENTIFIER='all-only', LINKED_HEADER=1)]
    _table(directory / 'htable_Star.json', rows)
    catalog = search_index.catalog(tmp_path, [profile],
                                   dict(SPIROU={'PUBLIC'}))
    keys = {row['property'] for row in catalog['properties']}
    assert 'LINKED_HEADER' in keys
    assert 'ALL_ONLY_KEY' not in keys


def test_astrometrics_columns_unchanged(tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """The normal columns route still loads astrometrics column assets."""
    from flask import Flask
    from apero.core import drs_astrometrics as dra
    from apero_ri.application import astrometrics_api_helpers as helpers

    calls = []
    monkeypatch.setattr(helpers, '_check_view_perm', lambda app: (None, None))
    monkeypatch.setattr(helpers, '_astrom_dir', lambda app: tmp_path)
    monkeypatch.setattr(helpers, 'get_accessible_profiles', lambda *args: [])

    def list_columns(directory: str) -> list:
        """Record the asset path and return representative columns."""
        calls.append(directory)
        return ['APERO_NAME', 'RA']

    monkeypatch.setattr(dra, 'list_columns', list_columns)
    stub = SimpleNamespace(args=SimpleNamespace(data_dir=str(tmp_path)),
                           ari_groups=dict(), _get_api_user=lambda: None)
    app = Flask(__name__)
    with app.test_request_context('/api/astrometrics/columns'):
        data = helpers.api_astrometrics_columns(stub).get_json()
    assert calls == [str(tmp_path)]
    assert data['columns'] == ['APERO_NAME', 'RA']
    assert data['find_object_index_status'] == 'ready'