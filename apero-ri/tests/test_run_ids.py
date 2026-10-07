#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused coverage for the durable RUN ID catalog."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from apero import dev
from apero_ri.core import run_ids
from apero_ri.core import auth
from apero_ri.core import permissions


@pytest.fixture()
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Yield a CLI-isolated ARI app without background services.

    :param tmp_path: Temporary storage root.
    :param monkeypatch: Fixture restoring startup overrides.
    :return: Isolated ARI application.
    """
    from apero_ri.application.application import ARIApp
    from apero_ri.core import task_runner
    from apero_ri.core import user_data

    original_root = auth.ARI_DIR
    original_user_root = user_data.ARI_DIR
    monkeypatch.setattr(sys, 'argv', ['ari-test', '--data-dir', str(tmp_path)])
    monkeypatch.setenv('ARI_DIR', str(tmp_path))
    monkeypatch.setattr(task_runner, 'start_background_services',
                        lambda *values: None)
    monkeypatch.setattr(ARIApp, '_start_admin_health_refresher',
                        lambda self: None)
    monkeypatch.setattr(auth, 'ensure_default_user', lambda: None)
    monkeypatch.setattr(auth, '_ari_dir_ensured', False)
    instance = ARIApp()
    instance.config.update(TESTING=True, SECRET_KEY='run-id-tests',
                           RATELIMIT_ENABLED=False)
    try:
        yield instance
    finally:
        auth.set_ari_dir(str(original_root))
        user_data.set_ari_dir(str(original_user_root))


def test_catalog_preserves_edits_and_retains_ids(tmp_path: Path) -> None:
    """Rescans preserve manual edits and previously discovered IDs."""
    assert dev is not None
    run_ids.update_catalog(tmp_path, 'SPIROU', dict(R1='Original PI'))
    edit_kwargs = dict(run_id='R1', pi='Edited PI', comment='Keep forever')
    run_ids.update_catalog(tmp_path, 'SPIROU', **edit_kwargs)
    records = run_ids.update_catalog(tmp_path, 'SPIROU', dict(R2='New PI'))
    assert records['R1'] == dict(pi='Edited PI', comment='Keep forever')
    assert records['R2']['pi'] == 'New PI'
    run_ids.update_catalog(tmp_path, 'SPIROU', run_id='R1')
    records = run_ids.update_catalog(tmp_path, 'SPIROU', dict(R1='Old PI'))
    assert records['R1']['pi'] == ''
    assert (tmp_path / 'apero-assets/run_ids/spirou.json').exists()


def test_duplicate_and_instrument_isolation(tmp_path: Path) -> None:
    """IDs are unique within an instrument, not across instruments."""
    create_kwargs = dict(run_id='R1', create=True)
    run_ids.update_catalog(tmp_path, 'SPIROU', **create_kwargs)
    with pytest.raises(ValueError, match='already exists'):
        run_ids.update_catalog(tmp_path, 'SPIROU', **create_kwargs)
    run_ids.update_catalog(tmp_path, 'NIRPS_HA', **create_kwargs)
    with pytest.raises(ValueError, match='Invalid instrument'):
        run_ids.update_catalog(tmp_path, '..')


def test_labels() -> None:
    """Optional metadata follows the requested label format."""
    assert run_ids.record_label('R1', dict()) == 'R1'
    assert run_ids.record_label('R1', dict(pi='PI')) == 'R1 (PI)'
    metadata = dict(pi='PI', comment='Note')
    assert run_ids.record_label('R1', metadata) == 'R1 (PI) [Note]'
    assert run_ids.record_label('R1', dict(comment='Note')) == 'R1'


def test_admin_catalog_workflow(
    client: Any, admin_user: tuple, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Admin creates and edits a durable ID used by science groups."""
    with client.session_transaction() as session:
        session['user'] = admin_user[0]
    monkeypatch.setattr(client.application,
                        '_refresh_admin_health_after_change',
                        lambda *values: None)
    url = '/api/admin/run-ids/save'
    payload = dict(instrument='SPIROU', run_id='TEST-RUN-1', create=True,
                   pi='Test PI', comment='Test comment')
    response = client.post(url, json=payload)
    assert response.status_code == 200
    assert client.post(url, json=payload).status_code == 400
    payload.update(create=False, pi='Edited PI')
    assert client.post(url, json=payload).status_code == 200
    response = client.get('/api/admin/run-ids/list?instrument=SPIROU')
    rows = response.get_json()['rows']
    assert any(row['pi'] == 'Edited PI' for row in rows)
    response = client.get('/api/admin/sci-groups/list?instrument=SPIROU')
    data = response.get_json()
    label = data['run_id_labels']['TEST-RUN-1']
    assert label == 'TEST-RUN-1 (Edited PI) [Test comment]'
    groups = auth.load_science_groups('SPIROU')
    assert 'TEST-RUN-1' in groups['All']['run_ids']
    response = client.get('/admin_portal/run_ids')
    assert response.status_code == 200
    assert b'ARI_RUN_IDS' in response.data
    assert b'Manage RUN IDs' in response.data
    assert b'admin_run_ids.css' in response.data


def test_catalog_api_permissions(
    client: Any, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each API request enforces login and instrument-specific access."""
    monkeypatch.setattr(auth, 'get_effective_user', lambda session: None)
    url = '/api/admin/run-ids/list?instrument=SPIROU'
    assert client.get(url).status_code == 401
    user = dict(username='moderator', groups=['moderator.SPIROU'])
    monkeypatch.setattr(auth, 'get_effective_user', lambda session: user)
    assert client.get(url).status_code == 200
    url = '/api/admin/run-ids/list?instrument=NIRPS'
    assert client.get(url).status_code == 403
    payload = dict(instrument='NIRPS', run_id='R1', create=True)
    response = client.post('/api/admin/run-ids/save', json=payload)
    assert response.status_code == 403
    payload = dict(instrument='SPIROU', run_id=['R1'], create=True)
    response = client.post('/api/admin/run-ids/save', json=payload)
    assert response.status_code == 400


def test_profile_scan_seeds_catalog(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Profile discovery seeds metadata without overwriting admin edits."""
    from apero_ri.application import ariapp_impls

    monkeypatch.setattr(auth, 'ARI_DIR', tmp_path)
    profiles = dict(SPIROU=dict(test_profile=dict()))
    monkeypatch.setattr(auth, 'load_apero_profiles', lambda **kw: profiles)
    monkeypatch.setattr(auth, 'load_science_groups', lambda inst: dict())
    directory = tmp_path / 'tasks/SPIROU/test_profile'
    directory.mkdir(parents=True)
    rows = [dict(RUN_ID='R1, R2', PI_NAMES='PI One; PI Two')]
    path = directory / 'object_table.json'
    path.write_text(json.dumps(dict(rows=rows)), encoding='utf-8')
    assert ariapp_impls.ariapp_get_instrument_run_ids('SPIROU') == ['R1', 'R2']
    records = run_ids.update_catalog(tmp_path, 'SPIROU')
    assert records['R1']['pi'] == 'PI One'
    assert records['R2']['pi'] == 'PI Two'
    run_ids.update_catalog(tmp_path, 'SPIROU', run_id='R1', pi='Manual')
    profiles.clear()
    assert ariapp_impls.ariapp_get_instrument_run_ids('SPIROU') == ['R1', 'R2']
    records = run_ids.update_catalog(tmp_path, 'SPIROU')
    assert records['R1']['pi'] == 'Manual'


def test_page_registration() -> None:
    """Page registration and inherited grants agree with the new route."""
    pages = permissions.load_pages()
    page_id = 'home.admin_portal.run_ids'
    assert pages[page_id]['view-permission'] == 'manage.run_id'
    template = permissions.page_id_to_template(page_id, pages)
    assert template == 'admin/run_ids.html'
    groups = permissions.load_groups()
    perms = permissions.resolve_user_permissions(['admin'], groups)
    assert 'manage.run_id.SPIROU' in perms
    assert 'manage.run_id.NIRPS' in perms