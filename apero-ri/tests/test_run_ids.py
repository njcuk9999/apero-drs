#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused coverage for the durable RUN ID catalog."""

import json
import csv
import sys
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml

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


def test_run_id_health_breakdown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Count blank PIs per instrument, excluding unauthorized catalogs."""
    from apero_ri.application import run_ids_api_helpers

    monkeypatch.setattr(auth, 'ARI_DIR', tmp_path)
    seeds = dict(R1='', R2='  ', R3='Named PI')
    run_ids.update_catalog(tmp_path, 'SPIROU', seeds)
    run_ids.update_catalog(tmp_path, 'NIRPS', dict(R1=''))
    app_stub = SimpleNamespace(_get_instrument_run_ids=lambda inst: [])
    perms = {'manage.run_id.SPIROU', 'manage.run_id.NIRPS'}
    report = run_ids_api_helpers.build_run_id_health(app_stub, perms)
    assert report['status'] == 'warning'
    assert report['total'] == 4
    assert report['missing_pi'] == 3
    counts = {row['instrument']: row['missing_pi']
              for row in report['instruments']}
    assert counts == dict(SPIROU=2, NIRPS=1)
    perms = {'manage.run_id.SPIROU'}
    report = run_ids_api_helpers.build_run_id_health(app_stub, perms)
    assert report['missing_pi'] == 2
    assert report['total'] == 3
    assert len(report['instruments']) == 1
    for run_id in ['R1', 'R2']:
        edit_kwargs = dict(run_id=run_id, pi='Filled PI')
        run_ids.update_catalog(tmp_path, 'SPIROU', **edit_kwargs)
    report = run_ids_api_helpers.build_run_id_health(app_stub, perms)
    assert report['status'] == 'ok'
    assert report['missing_pi'] == 0


def test_run_id_global_health(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Global health includes the RUN ID report and instrument details."""
    from apero_ri.application import admin_health_helpers

    monkeypatch.setattr(auth, 'ARI_DIR', tmp_path)
    run_ids.update_catalog(tmp_path, 'SPIROU', dict(R1=''))
    app_stub = SimpleNamespace(_get_instrument_run_ids=lambda inst: [],
                               ari_pages=permissions.load_pages())
    perms = {'manage.run_id.SPIROU'}
    health_args = [app_stub, dict(), perms]
    health = admin_health_helpers.build_admin_card_health_uncached(*health_args)
    page_id = 'home.admin_portal.run_ids'
    assert health[page_id]['status'] == 'warning'
    assert health[page_id]['missing_pi'] == 1
    rows = admin_health_helpers.build_admin_health_rows(app_stub, health)
    row = next(item for item in rows if item['page_id'] == page_id)
    assert row['url'] == '/admin_portal/run_ids'
    assert row['details'] == ['SPIROU: 1 of 1 RUN ID(s) missing a PI name.']
    assert 'missing a PI name' in row['rule_message']


def test_admin_yaml_mirror(tmp_path: Path) -> None:
    """Asset edits synchronize to YAML and YAML restores absent assets."""
    run_ids.update_catalog(tmp_path, 'SPIROU', dict(R1='Seed PI'))
    edit_kwargs = dict(run_id='R1', pi='Edited PI', comment='Persistent')
    records = run_ids.update_catalog(tmp_path, 'SPIROU', **edit_kwargs)
    mirror = tmp_path / 'admin/run_ids/spirou_run_ids.yaml'
    assert yaml.safe_load(mirror.read_text()) == records
    assets = tmp_path / 'apero-assets/run_ids/spirou.json'
    assets.unlink()
    assert run_ids.update_catalog(tmp_path, 'SPIROU') == records
    assert json.loads(assets.read_text()) == records
    mirror.write_text('broken: [', encoding='utf-8')
    assert run_ids.update_catalog(tmp_path, 'SPIROU') == records
    assert yaml.safe_load(mirror.read_text()) == records


def test_csv_duplicate_policies(tmp_path: Path) -> None:
    """Reject is atomic, keep uses first row, overwrite uses last row."""
    run_ids.update_catalog(tmp_path, 'SPIROU', dict(R1='Existing'))
    content = ('RUN ID,PI,COMMENT\r\n'
               'R1,Replacement,Note\r\n'
               'R2,First,First note\r\n'
               'R2,Last,Last note\r\n')
    assets = tmp_path / 'apero-assets/run_ids/spirou.json'
    mirror = tmp_path / 'admin/run_ids/spirou_run_ids.yaml'
    before_assets = assets.read_bytes()
    before_mirror = mirror.read_bytes()
    with pytest.raises(ValueError, match='Duplicate RUN IDs: R1, R2'):
        run_ids.import_csv(tmp_path, 'SPIROU', content, 'reject')
    assert assets.read_bytes() == before_assets
    assert mirror.read_bytes() == before_mirror
    report = run_ids.import_csv(tmp_path, 'SPIROU', content, 'skip')
    assert report == dict(added=1, updated=0, skipped=2,
                          duplicates=['R1', 'R2'])
    records = run_ids.update_catalog(tmp_path, 'SPIROU')
    assert records['R1']['pi'] == 'Existing'
    assert records['R2']['pi'] == 'First'
    report = run_ids.import_csv(tmp_path, 'SPIROU', content, 'overwrite')
    assert report['updated'] == 2
    records = run_ids.update_catalog(tmp_path, 'SPIROU')
    assert records['R1']['pi'] == 'Replacement'
    assert records['R2']['pi'] == 'Last'
    assert yaml.safe_load(mirror.read_text()) == records


def test_csv_validation_and_quoted_values(tmp_path: Path) -> None:
    """Quoted multiline values round trip; malformed imports change nothing."""
    content = ('\ufeffRUN_ID,PI,COMMENT\r\n'
               'R1,"Name, PI","Line one\nLine ""two"""\r\n')
    report = run_ids.import_csv(tmp_path, 'SPIROU', content, 'reject')
    assert report['added'] == 1
    records = run_ids.update_catalog(tmp_path, 'SPIROU')
    assert records['R1'] == dict(pi='Name, PI',
                                comment='Line one\nLine "two"')
    invalid = ['RUN ID,PI\nR2,PI\n',
               'RUN ID,PI,COMMENT\nR2,PI,Note,Extra\n',
               'RUN ID,PI,COMMENT\nR2,PI\n',
               'RUN ID,PI,COMMENT\n,PI,Note\n',
               'RUN ID,PI,COMMENT\nR2,"Unclosed\n',
               'RUN ID,PI,COMMENT\n']
    for text in invalid:
        with pytest.raises(ValueError):
            run_ids.import_csv(tmp_path, 'SPIROU', text, 'reject')
        assert run_ids.update_catalog(tmp_path, 'SPIROU') == records


def test_csv_endpoints(
    client: Any, admin_user: tuple, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Import/export enforce authorization and preserve selected CSV order."""
    import_url = '/api/admin/run-ids/import'
    export_url = '/api/admin/run-ids/export'
    payload = dict(instrument='SPIROU', duplicate_policy='reject',
                   csv='RUN ID,PI,COMMENT\nR1,,Missing\nR2,PI,"A, B"\n')
    assert client.post(import_url, json=payload).status_code == 401
    assert client.post(export_url, json=payload).status_code == 401
    with client.session_transaction() as session:
        session['user'] = admin_user[0]
    monkeypatch.setattr(client.application,
                        '_refresh_admin_health_after_change',
                        lambda *values: None)
    response = client.post(import_url, json=payload)
    assert response.status_code == 200
    assert response.get_json()['summary']['added'] == 2
    assert response.get_json()['health']['missing_pi'] == 1
    with monkeypatch.context() as rejection_patch:
        def unexpected_discovery(instrument: str) -> list:
            """Reject discovery during failed imports.

            :param instrument: Requested instrument.
            :return: Never returns.
            """
            raise AssertionError('Rejected import must not run discovery')

        rejection_patch.setattr(client.application,
                                '_get_instrument_run_ids',
                                unexpected_discovery)
        assert client.post(import_url, json=payload).status_code == 400
    payload['duplicate_policy'] = 'skip'
    response = client.post(import_url, json=payload)
    assert response.get_json()['summary']['skipped'] == 2
    selection = dict(instrument='SPIROU', run_ids=['R2', 'R1'])
    response = client.post(export_url, json=selection)
    assert response.status_code == 200
    assert 'attachment' in response.headers['Content-Disposition']
    content = response.data.decode('utf-8-sig')
    rows = list(csv.reader(StringIO(content)))
    assert rows == [['RUN ID', 'PI', 'COMMENT'],
                    ['R2', 'PI', 'A, B'], ['R1', '', 'Missing']]
    selection['run_ids'] = ['R1']
    response = client.post(export_url, json=selection)
    rows = list(csv.reader(StringIO(response.data.decode('utf-8-sig'))))
    assert rows == [['RUN ID', 'PI', 'COMMENT'], ['R1', '', 'Missing']]
    selection['run_ids'] = ['UNKNOWN']
    assert client.post(export_url, json=selection).status_code == 400
    user = dict(username='moderator', groups=['moderator.SPIROU'])
    monkeypatch.setattr(auth, 'get_effective_user', lambda session: user)
    payload['instrument'] = selection['instrument'] = 'NIRPS'
    assert client.post(import_url, json=payload).status_code == 403
    assert client.post(export_url, json=selection).status_code == 403