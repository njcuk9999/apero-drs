#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deterministic diagnostics security and collector regression tests."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from apero import dev
from apero_ri.core import diagnostic_tokens as tokens


def test_grant_scope_storage_and_revocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Grants keep explicit scopes and never persist the bearer credential.

    :param tmp_path: Isolated storage root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    monkeypatch.setattr(tokens.secret_store, 'get_ari_dir', lambda: tmp_path)
    grant = tokens.issue('admin', [['SPIROU', 'mini']], 24, 'fir')
    assert tokens.validate(grant['token'])['profiles'] == [['SPIROU', 'mini']]
    path = tmp_path / 'secret' / 'diagnostic_tokens.json'
    assert grant['token'] not in path.read_text()
    assert path.stat().st_mode & 0o777 == 0o600
    assert 'token' not in tokens.list_grants()[0]
    assert tokens.revoke(grant['id'])
    assert tokens.validate(grant['token']) is None


def test_grant_expiry_and_lifetime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Expired grants and oversized lifetimes cannot authorize reports.

    :param tmp_path: Isolated storage root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    monkeypatch.setattr(tokens.secret_store, 'get_ari_dir', lambda: tmp_path)
    with pytest.raises(ValueError):
        tokens.issue('admin', [['SPIROU', 'mini']], 25)
    grant = tokens.issue('admin', [['SPIROU', 'mini']])
    path = tmp_path / 'secret' / 'diagnostic_tokens.json'
    stored = json.loads(path.read_text())
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    next(iter(stored.values()))['expires_at'] = past.isoformat()
    path.write_text(json.dumps(stored))
    assert tokens.validate(grant['token']) is None
    assert tokens.list_grants()[0]['state'] == 'expired'
    assert tokens.validate('ordinary-user-token') is None


def test_collector_redaction_and_containment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reports redact credentials and refuse symlinked object payloads.

    :param tmp_path: Isolated ARI root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from aperocore.core import diagnostics as common
    from apero_ri.core import diagnostics

    monkeypatch.setattr(diagnostics.auth, 'load_async_tasks', lambda: dict())
    root = tmp_path / 'tasks' / 'SPIROU' / 'mini' / 'objects'
    root.mkdir(parents=True)
    (root.parent / 'obs_table.json').write_text(json.dumps(dict(
        rows=[dict(OBJNAME='GL699')], GENERATED_AT='test-time')))
    external = tmp_path / 'private.json'
    external.write_text('{"rows": [{"private": "do-not-export"}]}')
    (root / 'ftable_all_GL699.json').symlink_to(external)
    profile = dict(database=dict(DATABASE_PASSWORD='super-private'),
                   paths=dict(PATH_OTHER=str(tmp_path / 'other')),
                   notes='failure super-private password=hidden')
    report = diagnostics.collect(profile, 'SPIROU', 'mini', tmp_path,
                                  'GL699', include_database=False)
    encoded = json.dumps(report)
    assert 'super-private' not in encoded
    assert 'do-not-export' not in encoded
    assert 'password=hidden' not in encoded
    assert report['sections']['cache']['object_tables']['all']['skipped']
    assert report['sections']['cache']['obs_table.json']['n_rows'] == 1
    assert common.redact('https://user:password@host') == (
        'https://[REDACTED]@host')
    with pytest.raises(ValueError):
        diagnostics.collect(profile, 'SPIROU', 'mini', tmp_path, '../secret')
    monkeypatch.setattr(diagnostics.apero_async, 'get_db_params',
                        lambda profile: dict(DATABASE_PASSWORD='saved-secret'))
    profile['notes'] = 'bare credential echo: saved-secret'
    report = diagnostics.collect(profile, 'SPIROU', 'mini', tmp_path,
                                  include_logs=True, include_database=False)
    assert 'saved-secret' not in json.dumps(report)


def test_collector_reports_actual_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Progress follows completed stages, including optional checks.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.core import diagnostics

    monkeypatch.setattr(diagnostics.auth, 'load_async_tasks', lambda: dict())
    monkeypatch.setattr(diagnostics, '_queues', lambda *args: dict())
    monkeypatch.setattr(diagnostics, '_database', lambda *args: dict())
    monkeypatch.setattr(diagnostics.apero_async, 'get_db_params',
                        lambda profile: dict())
    events = []
    profile = dict(paths=dict())
    diagnostics.collect(profile, 'SPIROU', 'mini', tmp_path,
                        include_logs=True, progress=lambda *event: (
                            events.append(event)))
    assert events[0] == ('runtime', 0, 10)
    assert [event[0] for event in events] == [
        'runtime', 'queues', 'paths', 'cache', 'manifests', 'tasks',
        'database', 'log_tails', 'product_paths', 'finalize', 'complete']
    assert [event[1] for event in events] == list(range(11))
    assert all(event[2] == 10 for event in events)
    events.clear()
    diagnostics.collect(profile, 'SPIROU', 'mini', tmp_path,
                        include_database=False, progress=lambda *event: (
                            events.append(event)))
    assert events[-1] == ('complete', 8, 8)
    assert 'database' not in [event[0] for event in events]
    assert 'log_tails' not in [event[0] for event in events]


def test_manifest_progress_reports_task_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Manifest checking identifies each task without changing the count.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.core import diagnostics

    monkeypatch.setattr(diagnostics.auth, 'load_async_tasks', lambda: dict())
    monkeypatch.setattr(diagnostics, '_queues', lambda *args: dict())
    monkeypatch.setattr(diagnostics.apero_sync, 'local_task_keys',
                        lambda: ['APERO_OBJECT_QUERY'])
    events = []
    profile = dict(paths=dict(PATH_OTHER=str(tmp_path)))
    diagnostics.collect(profile, 'SPIROU', 'mini', tmp_path,
                        include_database=False, progress=lambda *event: (
                            events.append(event)))
    assert ('manifests:APERO_OBJECT_QUERY', 4, 8) in events


def test_background_job_reconnect_and_isolation(tmp_path: Path) -> None:
    """A disconnected browser can recover one private in-progress job.

    :param tmp_path: Isolated ARI data root.
    :return: None.
    """
    import threading
    from apero_ri.core import diagnostic_jobs

    running = threading.Event()
    release = threading.Event()

    def collect(progress: object) -> dict:
        """Pause at a visible stage until the test releases the worker.

        :param progress: Stage callback.
        :return: Synthetic report.
        """
        progress('manifests', 4, 10)
        running.set()
        assert release.wait(5)
        return dict(filters=dict(), profile_id='mini')

    options = dict(objname='GL699', pid='', include_logs=True,
                   include_database=True)
    start_args = [tmp_path, 'alice', 'SPIROU', 'mini', options, collect,
                  lambda report: None]
    state, reused = diagnostic_jobs.start(*start_args)
    try:
        assert not reused and running.wait(5)
        allowed = {('SPIROU', 'mini')}
        resumed = diagnostic_jobs.latest(tmp_path, 'alice', allowed)
        assert resumed['id'] == state['id']
        assert resumed['stage'] == 'manifests'
        assert resumed['completed'] == 4
        assert resumed['stage_elapsed_s'] >= 0
        assert diagnostic_jobs.get(tmp_path, 'bob', state['id']) is None
        assert diagnostic_jobs.latest(tmp_path, 'alice', set()) is None
        duplicate, reused = diagnostic_jobs.start(*start_args)
        assert reused and duplicate['id'] == state['id']
        with pytest.raises(ValueError):
            different = dict(options, objname='other')
            diagnostic_jobs.start(tmp_path, 'alice', 'SPIROU', 'mini',
                                  different, collect, lambda report: None)
    finally:
        release.set()


def test_background_job_detects_server_interruption(tmp_path: Path) -> None:
    """An abandoned worker lock is reported as interrupted, not running.

    :param tmp_path: Isolated ARI data root.
    :return: None.
    """
    import time
    from apero_ri.core import diagnostic_jobs

    directory = diagnostic_jobs._directory(tmp_path, 'alice')
    job_id = 'a' * 32
    state = dict(id=job_id, instrument='SPIROU', profile_id='mini',
                 options=dict(), created=time.time(),
                 status='running', stage='paths', completed=2, total=8)
    diagnostic_jobs._write(directory / (job_id + '.json'), state)
    restored = diagnostic_jobs.get(tmp_path, 'alice', job_id)
    assert restored['status'] == 'interrupted'
    assert diagnostic_jobs.result(tmp_path, 'alice', job_id) is None


def test_job_completion_wins_lock_release_race(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Re-read state when a worker finishes between status and lock checks.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    import time
    from apero_ri.core import diagnostic_jobs

    directory = diagnostic_jobs._directory(tmp_path, 'alice')
    job_id = 'b' * 32
    path = directory / (job_id + '.json')
    state = dict(id=job_id, instrument='SPIROU', profile_id='mini',
                 options=dict(), created=time.time(), status='running',
                 stage='finalize', completed=7, total=8)
    diagnostic_jobs._write(path, state)

    def finished(directory: Path, identifier: str) -> bool:
        """Publish completion just before the lock check returns.

        :param directory: Actor's job directory.
        :param identifier: Job identifier.
        :return: False because the worker has released its lock.
        """
        state['status'] = 'completed'
        diagnostic_jobs._write(directory / (identifier + '.json'), state)
        return False

    monkeypatch.setattr(diagnostic_jobs, '_is_running', finished)
    assert diagnostic_jobs.get(tmp_path, 'alice', job_id)['status'] == (
        'completed')


def test_diagnostic_api_scope_and_permission_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Grants authorize only selected profiles and current issuer access.

    :param tmp_path: Isolated root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from flask import Flask
    from apero_ri.application import diagnostics_api_helpers as api

    app = Flask(__name__)
    app.ari_groups = dict()
    monkeypatch.setattr(tokens.secret_store, 'get_ari_dir', lambda: tmp_path)
    monkeypatch.setattr(api.auth, 'load_users',
                        lambda: dict(admin=dict(groups=['admin'])))
    monkeypatch.setattr(api, '_perms', lambda app, user: {api.PERMISSION})
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(), ('SPIROU', 'private'): dict()})
    monkeypatch.setattr(api.audit_log, 'record', lambda *args, **kwargs: None)
    app.add_url_rule('/api/diagnostics/<action>',
                     view_func=lambda action: api.api(app, action))
    grant = tokens.issue('admin', [['SPIROU', 'mini']])
    headers = dict(Authorization='Bearer ' + grant['token'])
    client = app.test_client()
    assert client.get('/api/diagnostics/profiles').status_code == 401
    response = client.get('/api/diagnostics/profiles', headers=headers)
    assert response.json['profiles'] == [dict(instrument='SPIROU',
                                             profile_id='mini')]
    response = client.get('/api/diagnostics/report?instrument=SPIROU'
                           '&profile_id=private', headers=headers)
    assert response.status_code == 403
    response = client.get('/api/diagnostics/run', headers=headers)
    assert response.status_code == 404
    response = client.get('/api/diagnostics/profiles', headers=headers,
                          base_url='http://external.example',
                          environ_overrides=dict(REMOTE_ADDR='192.0.2.10'))
    assert response.status_code == 200
    assert response.json['profiles'] == [dict(instrument='SPIROU',
                                             profile_id='mini')]
    response = client.get('/api/diagnostics/report?instrument=SPIROU'
                          '&profile_id=private', headers=headers,
                          base_url='http://external.example',
                          environ_overrides=dict(REMOTE_ADDR='192.0.2.10'))
    assert response.status_code == 403
    monkeypatch.setattr(api, '_perms', lambda app, user: set())
    assert client.get('/api/diagnostics/profiles',
                      headers=headers).status_code == 403


def test_debug_cli_downloads_without_persisting_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The local chat workflow saves only private diagnostic JSON reports.

    :param tmp_path: Local download root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.recipes import apero_ri_debug as cli

    def request(host: str, key: str, action: str = 'profiles',
                params: dict | None = None) -> dict:
        """Return deterministic scoped server responses.

        :param host: Requested server.
        :param key: Diagnostic credential.
        :param action: Requested read operation.
        :param params: Report filters.
        :return: Constructed response.
        """
        assert key == 'private-test-key'
        if action == 'profiles':
            return dict(profiles=[dict(instrument='SPIROU', profile_id='mini')])
        return dict(success=True, profile_id=params['profile_id'])

    monkeypatch.setenv('APERO_RI_DEBUG_KEY', 'private-test-key')
    monkeypatch.setattr(cli.diagnostics, 'request_report', request)
    argv = ['--host=https://ari.example', '--object=GL699',
            '--output=' + str(tmp_path)]
    assert cli.main(argv) == 0
    path = tmp_path / 'SPIROU-mini.json'
    assert json.loads(path.read_text())['profile_id'] == 'mini'
    assert path.stat().st_mode & 0o777 == 0o600
    assert 'private-test-key' not in path.read_text()
    assert cli.main(argv + ['--profile=forbidden']) == 1


def test_linked_queue_scope_and_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only explicitly linked queues with matching host profiles are exported.

    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.core import diagnostics

    queues = dict(allowed=dict(enabled=True, instrument='SPIROU',
                               profile_id='mini', local_port='8090'),
                  private=dict(enabled=True, instrument='SPIROU',
                               profile_id='private', local_port='8091'))
    monkeypatch.setattr(diagnostics.apero_queues, 'load_queues', lambda: queues)
    calls = []

    def snapshot(port: str) -> dict:
        """Return a deterministic queue-host identity.

        :param port: Requested configured local port.
        :return: Queue identity and redacted payload.
        """
        calls.append(port)
        return dict(instrument='SPIROU', profile_id='mini')

    monkeypatch.setattr(diagnostics.diagnostic_api, 'queue_snapshot', snapshot)
    report = diagnostics._queues('SPIROU', 'mini')
    assert list(report) == ['allowed']
    assert calls == ['8090']
    assert report['allowed']['identity_match']
    queues['allowed']['profile_id'] = 'alias'
    report = diagnostics._queues('SPIROU', 'alias')
    assert not report['allowed']['identity_match']
    assert 'report' not in report['allowed']


def test_queue_loopback_boundary() -> None:
    """Queue diagnostics cannot be fetched directly by remote clients.

    :return: None.
    """
    dev.get_base_params('SPIROU')
    from apero.tools.module.processing import drs_queue_diagnostics as queue

    assert queue.loopback_allowed('127.0.0.1')
    assert queue.loopback_allowed('::1')
    assert not queue.loopback_allowed('206.12.93.77')


def test_admin_page_and_export(
    app: object, client: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real ARI routes render the admin page and return a private export.

    :param app: Isolated ARI application fixture.
    :param client: Flask test client fixture.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    import gzip
    from apero_ri.application import diagnostics_api_helpers as api

    user = dict(username='diagnostic-test', groups=['super_admin'])
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    monkeypatch.setattr(api.diagnostics, 'collect', lambda *args, **kwargs: {
        'filters': dict(), 'profile_id': 'mini'})
    page = client.get('/admin_portal/diagnostics')
    assert page.status_code == 200
    assert b'admin_diagnostics.js' in page.data
    assert b'/docs/ari_guide/admin_portal/diagnostics' in page.data
    assert b'#report-options' in page.data
    assert b'Leave it blank' in page.data
    overview = client.get('/api/admin/diagnostics/overview')
    assert overview.json['profiles'][0]['profile_id'] == 'mini'
    issued = client.post('/api/admin/diagnostics/issue', json=dict(
        profiles=[['SPIROU', 'mini']], hours=24),
        base_url='http://external.example',
        environ_overrides=dict(REMOTE_ADDR='192.0.2.10'))
    assert issued.status_code == 200
    assert issued.headers['Cache-Control'] == 'no-store'
    exported = client.get('/api/admin/diagnostics/export?instrument=SPIROU'
                           '&profile_id=mini')
    assert exported.status_code == 200
    assert json.loads(gzip.decompress(exported.data))['success']
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: None)
    assert client.get('/admin_portal/diagnostics').status_code == 403


def test_diagnostics_guide_anchors() -> None:
    """The published guide renders the anchors linked from the admin page.

    :return: None.
    """
    from apero_ri.core import docs

    raw, html, version, meta = docs.get_doc_content(
        'ari_guide/admin_portal/diagnostics', '0.8.XXX')
    assert raw and version == '0.8.XXX'
    assert meta['card_label'] == 'Diagnostics'
    for anchor in ('profiles', 'access-grants', 'report-options'):
        assert f'id="{anchor}"' in html


def test_admin_stream_reports_progress_and_enforces_scope(
    app: object, client: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stream real stage updates only for authorized profile reports.

    :param app: Isolated ARI application fixture.
    :param client: Flask test client.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.application import diagnostics_api_helpers as api

    user = dict(username='diagnostic-test', groups=['super_admin'])
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    monkeypatch.setattr(api.audit_log, 'record', lambda *args, **kwargs: None)

    def collect(*args: object, **kwargs: object) -> dict:
        """Produce staged test output for the streaming endpoint.

        :param args: Collector positional arguments.
        :param kwargs: Collector options and callback.
        :return: Synthetic redacted report.
        """
        callback = kwargs['progress']
        callback('runtime', 0, 1)
        callback('complete', 1, 1)
        return dict(filters=dict(), profile_id='mini')

    monkeypatch.setattr(api.diagnostics, 'collect', collect)
    path = '/api/admin/diagnostics/stream?instrument=SPIROU&profile_id='
    response = client.get(path + 'mini')
    assert response.status_code == 200
    assert response.mimetype == 'application/x-ndjson'
    assert response.headers['Cache-Control'] == 'no-store'
    events = [json.loads(line) for line in response.data.splitlines()]
    assert [event['type'] for event in events] == [
        'progress', 'progress', 'report']
    assert events[-1]['report']['success']
    assert client.get(path + 'private').status_code == 403
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: None)
    assert client.get(path + 'mini').status_code == 403


def test_admin_background_job_survives_refresh(
    app: object, client: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A fresh page can recover the same job and its finished report.

    :param app: Isolated ARI application fixture.
    :param client: Flask test client.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    import threading
    from apero_ri.application import diagnostics_api_helpers as api

    user = dict(username='diagnostics-resume', groups=['super_admin'])
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    monkeypatch.setattr(api.audit_log, 'record', lambda *args, **kwargs: None)
    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()
    original_write = api.diagnostic_jobs._write

    def write(path: Path, payload: dict) -> None:
        """Signal after the terminal job record is published.

        :param path: Job record path.
        :param payload: Job metadata or report.
        :return: None.
        """
        original_write(path, payload)
        if payload.get('status') == 'completed':
            finished.set()

    monkeypatch.setattr(api.diagnostic_jobs, '_write', write)

    def collect(*args: object, **kwargs: object) -> dict:
        """Hold the collection open across a new status request.

        :param args: Collector positional arguments.
        :param kwargs: Collector options and callback.
        :return: Synthetic report.
        """
        kwargs['progress']('manifests', 4, 10)
        started.set()
        assert release.wait(5)
        return dict(filters=dict(), profile_id='mini')

    monkeypatch.setattr(api.diagnostics, 'collect', collect)
    body = dict(instrument='SPIROU', profile_id='mini', objname='GL699',
                include_logs=True, include_database=True)
    response = client.post('/api/admin/diagnostics/start', json=body)
    job_id = response.json['job']['id']
    try:
        assert response.status_code == 200 and started.wait(5)
        response = client.get('/api/admin/diagnostics/latest')
        assert response.json['job']['id'] == job_id
        assert response.json['job']['stage'] == 'manifests'
        response = client.post('/api/admin/diagnostics/start', json=body)
        assert response.json['reused'] and response.json['job']['id'] == job_id
        monkeypatch.setattr(api, '_profiles', lambda app, user: dict())
        response = client.get('/api/admin/diagnostics/job?id=' + job_id)
        assert response.status_code == 404
    finally:
        release.set()
        assert finished.wait(5)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    response = client.get('/api/admin/diagnostics/job?id=' + job_id)
    assert response.json['job']['status'] == 'completed'
    assert response.json['job']['completed'] == response.json['job']['total']
    assert response.json['report']['profile_id'] == 'mini'
    directory = api.diagnostic_jobs._directory(
        Path(app._resolve_local_data_dir()), user['username'])
    assert (directory / (job_id + '.report')).stat().st_mode & 0o777 == 0o600


def test_admin_stream_sends_progress_before_collection_finishes(
    app: object, client: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The HTTP response emits progress while the collector is still busy.

    :param app: Isolated ARI application fixture.
    :param client: Flask test client.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    import threading
    from apero_ri.application import diagnostics_api_helpers as api

    user = dict(username='diagnostic-test', groups=['super_admin'])
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    monkeypatch.setattr(api.audit_log, 'record', lambda *args, **kwargs: None)
    release = threading.Event()

    def collect(*args: object, **kwargs: object) -> dict:
        """Wait after sending progress to prove it is streamed immediately.

        :param args: Collector positional arguments.
        :param kwargs: Collector options and callback.
        :return: Synthetic redacted report.
        """
        kwargs['progress']('queues', 1, 2)
        if not release.wait(5):
            raise RuntimeError('test_timeout')
        return dict(filters=dict(), profile_id='mini')

    monkeypatch.setattr(api.diagnostics, 'collect', collect)
    path = '/api/admin/diagnostics/stream?instrument=SPIROU&profile_id=mini'
    response = client.get(path, buffered=False)
    try:
        iterator = iter(response.response)
        event = json.loads(next(iterator))
        assert event['stage'] == 'queues'
        assert event['completed'] == 1 and event['total'] == 2
        release.set()
        assert json.loads(next(iterator))['type'] == 'report'
    finally:
        release.set()
        response.close()


def test_admin_stream_handles_collection_failure(
    app: object, client: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collection failures end the stream without returning a report.

    :param app: Isolated ARI application fixture.
    :param client: Flask test client.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.application import diagnostics_api_helpers as api

    user = dict(username='diagnostic-test', groups=['super_admin'])
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})

    def collect(*args: object, **kwargs: object) -> dict:
        """Fail after reporting the current stage.

        :param args: Collector positional arguments.
        :param kwargs: Collector options and callback.
        :return: This function always raises.
        """
        kwargs['progress']('queues', 1, 8)
        raise RuntimeError('private-test-error')

    monkeypatch.setattr(api.diagnostics, 'collect', collect)
    path = '/api/admin/diagnostics/stream?instrument=SPIROU&profile_id=mini'
    response = client.get(path)
    events = [json.loads(line) for line in response.data.splitlines()]
    assert [event['type'] for event in events] == ['progress', 'error']
    assert b'private-test-error' not in response.data


def test_product_fits_metadata_and_finite_json(tmp_path: Path) -> None:
    """FITS diagnostics contain headers, not image arrays or outside files.

    :param tmp_path: Isolated configured product root.
    :return: None.
    """
    import numpy as np
    from astropy.io import fits
    from aperocore.core import diagnostics as common
    from apero_ri.core import diagnostics

    path = tmp_path / 'product.fits'
    fits.PrimaryHDU(np.zeros((4, 4))).writeto(path)
    rows = [dict(BLOCK_KIND='out', FILENAME=str(path), KW_OUTPUT='DRS_POST_T')]
    profile = dict(paths=dict(PATH_OUT=str(tmp_path)))
    report = diagnostics._products(profile, rows)
    assert report['files'][0]['exists']
    assert report['fits_samples'][0]['hdus'][0]['header']['NAXIS1'] == 4
    assert 'data' not in report['fits_samples'][0]['hdus'][0]
    assert common.redact(float('nan')) is None
    assert common.redact(dict(PASS='hidden'))['PASS'] == '[REDACTED]'


def test_transport_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow HTTP while rejecting credentials embedded in URLs.

    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.ari_api import diagnostics

    requests = []

    def get(url: str, headers: dict, params: dict) -> dict:
        """Record the validated diagnostic transport request.

        :param url: Diagnostic endpoint URL.
        :param headers: Authorization headers.
        :param params: Request filters.
        :return: Synthetic response.
        """
        requests.append((url, headers, params))
        return dict(success=True)

    monkeypatch.setattr(diagnostics, '_get', get)
    response = diagnostics.request_report('http://206.12.93.77:5000', 'key')
    assert response['success']
    endpoint = 'http://206.12.93.77:5000/api/diagnostics/profiles'
    assert requests[0][0] == endpoint
    assert requests[0][1] == dict(Authorization='Bearer key')
    for host in ('https://user:password@ari.example',
                 'https://ari.example?token=hidden'):
        with pytest.raises(ValueError):
            diagnostics.request_report(host, 'private-test-key')