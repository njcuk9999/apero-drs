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


def test_completed_job_retention_starts_at_completion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A slow collection still retains its report for 24 completed hours.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.core import diagnostic_jobs

    directory = diagnostic_jobs._directory(tmp_path, 'alice')
    job_id = 'c' * 32
    state = dict(id=job_id, instrument='SPIROU', profile_id='mini',
                 options=dict(), created=1.0, completed_at=100000.0,
                 status='completed')
    diagnostic_jobs._write(directory / (job_id + '.json'), state)
    monkeypatch.setattr(diagnostic_jobs.time, 'time', lambda: 100001.0)
    assert diagnostic_jobs.get(tmp_path, 'alice', job_id) is not None
    monkeypatch.setattr(diagnostic_jobs.time, 'time',
                        lambda: 100000.0 + diagnostic_jobs.LIFETIME)
    assert diagnostic_jobs.get(tmp_path, 'alice', job_id) is None


def test_saved_report_share_rotation_expiry_and_delete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sharing is private by default, scoped, revocable and time-limited.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.core import diagnostic_jobs

    monkeypatch.setattr(diagnostic_jobs.time, 'time', lambda: 100000.0)
    directory = diagnostic_jobs._directory(tmp_path, 'alice')
    job_id = 'd' * 32
    state = dict(id=job_id, instrument='SPIROU', profile_id='mini',
                 options=dict(), created=1.0, completed_at=100000.0,
                 status='completed')
    report = dict(success=True, profile_id='mini')
    diagnostic_jobs._write(directory / (job_id + '.json'), state)
    diagnostic_jobs._write(directory / (job_id + '.report'), report)
    assert diagnostic_jobs.share(tmp_path, 'bob', job_id) is None
    token = diagnostic_jobs.share(tmp_path, 'alice', job_id)
    # the owner's listing can show the active link again without rotating it
    assert diagnostic_jobs.share_token(tmp_path, 'alice', job_id) == token
    assert diagnostic_jobs.share_token(tmp_path, 'bob', job_id) is None
    listed = diagnostic_jobs.saved(tmp_path, 'alice', {('SPIROU', 'mini')})
    assert listed[0]['share_token'] == token
    assert listed[0]['expires_at'] == 100000.0 + diagnostic_jobs.LIFETIME
    assert diagnostic_jobs.shared(tmp_path, token)[2] == report
    assert diagnostic_jobs.shared(tmp_path, token + 'x') is None
    rotated = diagnostic_jobs.share(tmp_path, 'alice', job_id)
    assert diagnostic_jobs.shared(tmp_path, token) is None
    assert diagnostic_jobs.shared(tmp_path, rotated) is not None
    assert diagnostic_jobs.revoke_share(tmp_path, 'alice', job_id)
    assert diagnostic_jobs.shared(tmp_path, rotated) is None
    assert diagnostic_jobs.share_token(tmp_path, 'alice', job_id) is None
    token = diagnostic_jobs.share(tmp_path, 'alice', job_id)
    monkeypatch.setattr(diagnostic_jobs.time, 'time',
                        lambda: 100000.0 + diagnostic_jobs.LIFETIME)
    assert diagnostic_jobs.shared(tmp_path, token) is None
    monkeypatch.setattr(diagnostic_jobs.time, 'time', lambda: 100001.0)
    assert not diagnostic_jobs.delete(tmp_path, 'bob', job_id)
    assert diagnostic_jobs.delete(tmp_path, 'alice', job_id)
    assert diagnostic_jobs.shared(tmp_path, token) is None
    assert not (directory / (job_id + '.report')).exists()


def test_completed_job_is_shared_automatically(tmp_path: Path) -> None:
    """A finished collection already has its link when it is listed.

    :param tmp_path: Isolated ARI data root.
    :return: None.
    """
    import threading
    from apero_ri.core import diagnostic_jobs

    shared_events = []
    finished = threading.Event()

    def collect(progress: object) -> dict:
        """Return a synthetic report immediately.

        :param progress: Stage callback.
        :return: Synthetic report.
        """
        return dict(filters=dict(), profile_id='mini')

    def on_share() -> None:
        """Record that the automatic link was created.

        :return: None.
        """
        shared_events.append(True)
        finished.set()

    options = dict(objname='', pid='', include_logs=False,
                   include_database=False)
    start_args = [tmp_path, 'alice', 'SPIROU', 'mini', options, collect,
                  lambda report: None]
    state, _ = diagnostic_jobs.start(*start_args, on_share=on_share)
    assert finished.wait(5)
    allowed = {('SPIROU', 'mini')}
    # wait for the worker to publish completion after creating the link
    for _ in range(100):
        job = diagnostic_jobs.get(tmp_path, 'alice', state['id'])
        if job and job['status'] == 'completed':
            break
        threading.Event().wait(0.05)
    listed = diagnostic_jobs.saved(tmp_path, 'alice', allowed)
    assert shared_events == [True]
    token = listed[0]['share_token']
    assert diagnostic_jobs.shared(tmp_path, token)[2]['profile_id'] == 'mini'


def test_scheduled_cleanup_removes_only_expired_jobs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scheduled cleanup removes old reports, not live or fresh jobs.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    import fcntl
    from apero_ri import tasks
    from apero_ri.core import diagnostic_jobs

    monkeypatch.setattr(diagnostic_jobs.time, 'time', lambda: 200000.0)
    directory = diagnostic_jobs._directory(tmp_path, 'alice')
    expired, fresh = 'a' * 32, 'b' * 32
    for job_id, completed_at in ((expired, 100000.0), (fresh, 199999.0)):
        state = dict(id=job_id, created=completed_at,
                     completed_at=completed_at, status='completed')
        diagnostic_jobs._write(directory / (job_id + '.json'), state)
        diagnostic_jobs._write(directory / (job_id + '.report'), dict(ok=True))
        diagnostic_jobs._write(directory / (job_id + '.share'), dict(ok=True))
    active = 'c' * 32
    state = dict(id=active, created=1.0, status='running')
    diagnostic_jobs._write(directory / (active + '.json'), state)
    with (directory / (active + '.lock')).open('w') as active_lock:
        fcntl.flock(active_lock, fcntl.LOCK_EX)
        task = tasks.TASK_LIST['DIAGNOSTICS_CLEANUP']()
        task.run_job(dict(LOCAL_DATA_DIR=str(tmp_path)))
        assert (directory / (active + '.json')).exists()
    assert tasks.TYPE['DIAGNOSTICS_CLEANUP'] == 'GLOBAL'
    assert tasks.ENABLED['DIAGNOSTICS_CLEANUP']
    assert not (directory / (expired + '.report')).exists()
    assert not (directory / (expired + '.share')).exists()
    assert (directory / (fresh + '.report')).exists()


def test_shared_report_api_checks_owner_and_permissions(
    app: object, client: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Anonymous report access requires a valid link and current scope.

    :param app: Isolated ARI application fixture.
    :param client: Flask test client.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.application import diagnostics_api_helpers as api

    user = dict(username='share-owner', groups=['super_admin'])
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    monkeypatch.setattr(api.auth, 'get_user_info', lambda actor: user)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    monkeypatch.setattr(api.audit_log, 'record', lambda *args, **kwargs: None)
    root = Path(app._resolve_local_data_dir())
    directory = api.diagnostic_jobs._directory(root, user['username'])
    job_id = 'e' * 32
    import time

    state = dict(id=job_id, instrument='SPIROU', profile_id='mini',
                 options=dict(), created=time.time(), status='completed')
    api.diagnostic_jobs._write(directory / (job_id + '.json'), state)
    api.diagnostic_jobs._write(directory / (job_id + '.report'),
                               dict(success=True, profile_id='mini'))
    listing = client.get('/api/admin/diagnostics/saved')
    assert [row['id'] for row in listing.json['jobs']] == [job_id]
    shell = client.get('/diagnostics/shared')
    assert shell.status_code == 200
    assert b'id="shared-report"' not in shell.data
    assert b'id="shared-copy"' in shell.data
    assert shell.headers['Referrer-Policy'] == 'no-referrer'
    assert shell.headers['Cache-Control'] == 'no-store'
    assert "default-src 'self'" in shell.headers['Content-Security-Policy']
    assert client.get('/api/diagnostics/shared-report').status_code == 404
    issued = client.post('/api/admin/diagnostics/share', json=dict(id=job_id))
    assert issued.status_code == 200
    token = issued.json['token']
    headers = dict(Authorization='Bearer ' + token)
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: None)
    response = client.get('/api/diagnostics/shared-report', headers=headers)
    assert response.status_code == 200
    assert response.json['report']['profile_id'] == 'mini'
    assert response.headers['Cache-Control'] == 'no-store'
    # wget/curl download mode returns the bare report as an attachment
    download = client.get('/api/diagnostics/shared-report?download=1',
                          headers=headers)
    assert download.status_code == 200
    assert download.json == dict(success=True, profile_id='mini')
    assert ('filename="apero-diagnostics-SPIROU-mini.json"'
            in download.headers['Content-Disposition'])
    assert download.headers['Cache-Control'] == 'no-store'
    assert client.get('/api/diagnostics/shared-report?download=1'
                      ).status_code == 404
    monkeypatch.setattr(api, '_profiles', lambda app, user: dict())
    assert client.get('/api/diagnostics/shared-report',
                      headers=headers).status_code == 404
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    assert client.get('/api/admin/diagnostics/saved').json['jobs'] == []
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    assert client.post('/api/admin/diagnostics/revoke-share',
                       json=dict(id=job_id)).status_code == 200
    assert client.get('/api/diagnostics/shared-report',
                      headers=headers).status_code == 404
    assert client.post('/api/admin/diagnostics/delete',
                       json=dict(id=job_id)).status_code == 200


def test_diagnostics_polling_does_not_exhaust_write_limit(
    app: object, client: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Frequent status reads must not block a later share action.

    :param app: Isolated ARI application fixture.
    :param client: Flask test client.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    import time
    from apero_ri.application import diagnostics_api_helpers as api

    user = dict(username='rate-test', groups=['super_admin'])
    monkeypatch.setattr(api.auth, 'get_effective_user', lambda session: user)
    monkeypatch.setattr(api, '_profiles', lambda app, user: {
        ('SPIROU', 'mini'): dict(paths=dict())})
    monkeypatch.setattr(api.audit_log, 'record', lambda *args, **kwargs: None)
    root = Path(app._resolve_local_data_dir())
    directory = api.diagnostic_jobs._directory(root, user['username'])
    job_id = 'f' * 32
    state = dict(id=job_id, instrument='SPIROU', profile_id='mini',
                 options=dict(), created=time.time(), status='completed')
    api.diagnostic_jobs._write(directory / (job_id + '.json'), state)
    api.diagnostic_jobs._write(directory / (job_id + '.report'), dict(ok=True))
    remote = dict(REMOTE_ADDR='192.0.2.101')
    for index in range(30):
        response = client.get('/api/admin/diagnostics/latest',
                              environ_overrides=remote)
        assert response.status_code == 200, index
    response = client.post('/api/admin/diagnostics/share',
                           json=dict(id=job_id), environ_overrides=remote)
    assert response.status_code == 200
    for index in range(19):
        response = client.post('/api/admin/diagnostics/share',
                               json=dict(id=job_id), environ_overrides=remote)
        assert response.status_code == 200, index
    response = client.post('/api/admin/diagnostics/share',
                           json=dict(id=job_id), environ_overrides=remote)
    assert response.status_code == 429


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
    # apero_ri_debug follows the same progress stream as the admin page
    app._resolve_local_data_dir = lambda: str(tmp_path)

    def collect(*args: object, progress: object = None,
                **kwargs: object) -> dict:
        """Emit one stage, then return a synthetic report.

        :param args: Collector arguments.
        :param progress: Stage callback.
        :param kwargs: Collector options.
        :return: Synthetic report.
        """
        progress('paths', 1, 2)
        return dict(filters=dict(), profile_id='mini')

    monkeypatch.setattr(api.diagnostics, 'collect', collect)
    response = client.get('/api/diagnostics/stream?instrument=SPIROU'
                          '&profile_id=mini', headers=headers)
    events = [json.loads(line) for line in response.data.splitlines()]
    assert events[0] == dict(type='progress', stage='paths', completed=1,
                             total=2)
    assert events[-1]['report']['profile_id'] == 'mini'
    response = client.get('/api/diagnostics/stream?instrument=SPIROU'
                          '&profile_id=private', headers=headers)
    assert response.status_code == 403
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
    capfd: pytest.CaptureFixture,
) -> None:
    """The local chat workflow saves only private diagnostic JSON reports.

    :param tmp_path: Local download root.
    :param monkeypatch: Runtime overrides.
    :param capfd: Captured CLI stdout/stderr.
    :return: None.
    """
    import logging
    from apero_ri.recipes import apero_ri_debug as cli

    # start from an unconfigured logger, as a fresh CLI process does;
    # earlier tests may have bound a handler to a stale stderr
    monkeypatch.setattr(logging.getLogger('apero_ri'), 'handlers', [])

    def request(host: str, key: str, action: str = 'profiles',
                params: dict | None = None, on_event: object = None) -> dict:
        """Return deterministic scoped server responses.

        :param host: Requested server.
        :param key: Diagnostic credential.
        :param action: Requested read operation.
        :param params: Report filters.
        :param on_event: Stream progress callback.
        :return: Constructed response.
        """
        assert key == 'private-test-key'
        if action == 'profiles':
            return dict(profiles=[dict(instrument='SPIROU', profile_id='mini')])
        # the CLI follows the progress stream rather than a blocking report
        assert action == 'stream'
        on_event(dict(type='progress', stage='manifests', completed=4,
                      total=10))
        for _ in range(cli.HEARTBEATS_PER_UPDATE):
            on_event(dict(type='heartbeat'))
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
    # progress goes to the log on stderr; stdout keeps the saved paths
    out, logged = capfd.readouterr()
    assert str(path) in out
    assert 'Key authorizes 1 profile(s): SPIROU/mini' in logged
    assert 'SPIROU / mini: 40% - stage manifests' in logged
    assert 'still collecting' in logged
    assert 'saved' in logged
    assert cli.main(argv + ['--profile=forbidden']) == 1
    assert 'profile_not_authorized' in capfd.readouterr().err


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
    # saved reports render as their own table with share/download endpoints
    assert b'id="diag-saved"' in page.data
    assert b'data-download-api="/api/diagnostics/shared-report?download=1"' in (
        page.data)
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


def test_object_plot_cache_and_relative_log_tails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Object reports summarise cached plot failures and read PATH_LOG tails.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    from apero_ri.core import diagnostics

    monkeypatch.setattr(diagnostics.auth, 'load_async_tasks', lambda: dict())
    monkeypatch.setattr(diagnostics, '_queues', lambda *args: dict())
    monkeypatch.setattr(diagnostics.apero_async, 'get_db_params',
                        lambda profile: dict())
    # one failed cached spectrum response and one unrelated object
    section = tmp_path / 'cache' / 'SPIROU' / 'mini' / 'object_plots'
    section.mkdir(parents=True)
    failed = dict(has_plot=False, message='Plot build failed: KeyError',
                  error='KW_MJDMID', traceback='Traceback\nKeyError')
    payload = dict(success=True, plot_group='spectrum', snr=failed,
                   spec=dict(has_plot=True, script='<s>', div='<d>'))
    entry = dict(cached_at='2026-11-26T00:00:00', payload=payload)
    (section / 'spectrum__GL699__rid_th_default.json').write_text(
        json.dumps(entry))
    (section / 'spectrum__GL905__rid_th_default.json').write_text('{}')
    # recipe LOGFILE values are stored relative to PATH_LOG
    logroot = tmp_path / 'log'
    (logroot / 'processing').mkdir(parents=True)
    (logroot / 'processing' / 'run.log').write_text('log-tail-text')
    rows = [dict(LOGFILE='processing/run.log')]
    monkeypatch.setattr(diagnostics, '_database',
                        lambda *args: dict(recipe_logs=rows))
    profile = dict(paths=dict(PATH_LOG=str(logroot)))
    report = diagnostics.collect(profile, 'SPIROU', 'mini', tmp_path,
                                 'GL699', include_logs=True)
    plots = report['sections']['cache']['object_plots']
    assert len(plots['entries']) == 1
    response = plots['entries'][0]['response']
    assert response['plot_group'] == 'spectrum'
    assert response['plots']['snr']['error'] == 'KW_MJDMID'
    assert response['plots']['spec']['script_chars'] == 3
    assert '<s>' not in json.dumps(report)
    assert report['sections']['log_tails'][0]['text'] == 'log-tail-text'


def test_transport_stream_parses_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stream events split across chunks still arrive in order.

    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    import io
    from apero_ri.ari_api import diagnostics

    class FakeResponse:
        """Minimal streamed ``requests`` response."""

        def __init__(self, status: int, body: bytes) -> None:
            """Store a status code and body.

            :param status: HTTP status code.
            :param body: Raw response body.
            :return: None.
            """
            self.status_code = status
            self.body = body
            self.raw = io.BytesIO(body)
            self.raw.read = (lambda size, decode_content=True,
                             stream=self.raw: io.BytesIO.read(stream, size))

        def __enter__(self) -> 'FakeResponse':
            """Enter the response context.

            :return: This response.
            """
            return self

        def __exit__(self, *args: object) -> None:
            """Leave the response context.

            :param args: Exception details.
            :return: None.
            """

        def iter_content(self, size: int) -> object:
            """Yield the body in small chunks to split lines.

            :param size: Ignored chunk size.
            :return: Chunk iterator.
            """
            return (self.body[i:i + 7] for i in range(0, len(self.body), 7))

    responses = []

    class FakeSession:
        """``requests.Session`` returning the queued response."""

        trust_env = True

        def __enter__(self) -> 'FakeSession':
            """Enter the session context.

            :return: This session.
            """
            return self

        def __exit__(self, *args: object) -> None:
            """Leave the session context.

            :param args: Exception details.
            :return: None.
            """

        def get(self, *args: object, **kwargs: object) -> FakeResponse:
            """Return the next queued response.

            :param args: Request arguments.
            :param kwargs: Request options.
            :return: Fake response.
            """
            return responses.pop(0)

    monkeypatch.setattr(diagnostics.requests, 'Session', FakeSession)
    body = (b'{"type": "progress", "stage": "paths", "completed": 1, '
            b'"total": 2}\n{"type": "heartbeat"}\n'
            b'{"type": "report", "report": {"profile_id": "mini"}}\n')
    responses.append(FakeResponse(200, body))
    seen = []
    report = diagnostics.request_report('https://ari.example', 'key',
                                        'stream', dict(), seen.append)
    assert report == dict(profile_id='mini')
    assert [event['type'] for event in seen] == ['progress', 'heartbeat']
    responses.append(FakeResponse(
        200, b'{"type": "error", "code": "collection_failed"}\n'))
    with pytest.raises(ValueError, match='collection_failed'):
        diagnostics.request_report('https://ari.example', 'key', 'stream')
    responses.append(FakeResponse(200, b'{"type": "heartbeat"}\n'))
    with pytest.raises(ValueError, match='diagnostic_stream_incomplete'):
        diagnostics.request_report('https://ari.example', 'key', 'stream')
    # HTTP failures name the server's error code, not just the status
    responses.append(FakeResponse(
        401, b'{"success": false, "code": "invalid_or_expired_grant"}'))
    with pytest.raises(ValueError,
                       match='diagnostic_http_401: invalid_or_expired_grant'):
        diagnostics.request_report('https://ari.example', 'key', 'stream')


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