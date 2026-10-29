#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Coverage for APERO queue definitions, access and dashboard proxy."""

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator

import pytest

from apero import dev
from apero_ri.application import apero_queue_api_helpers as aq
from apero_ri.core import apero_queues
from apero_ri.core import auth


class _FakeQueueGui(BaseHTTPRequestHandler):
    """Minimal stand-in for the apero_queue.py gui server."""

    posted = []

    def log_message(self, fmt: str, *args: Any) -> None:
        _ = fmt, args

    def _send(self, body: bytes, ctype: str) -> None:
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ('/', '/index.html'):
            page = b'<html><head></head><body>queue</body></html>'
            self._send(page, 'text/html; charset=utf-8')
        else:
            self._send(json.dumps(dict(path=self.path)).encode(),
                       'application/json')

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get('Content-Length', 0))
        _FakeQueueGui.posted.append((self.path, self.rfile.read(length)))
        self._send(b'{"started": true}', 'application/json')


@pytest.fixture()
def fake_gui() -> Iterator[int]:
    """Run the fake queue gui on a free localhost port."""
    server = ThreadingHTTPServer(('127.0.0.1', 0), _FakeQueueGui)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    _FakeQueueGui.posted = []
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()


@pytest.fixture()
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Yield an isolated ARI app without background services."""
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
    instance.config.update(TESTING=True, SECRET_KEY='apero-queue-tests',
                           RATELIMIT_ENABLED=False)
    try:
        yield instance
    finally:
        auth.set_ari_dir(str(original_root))
        user_data.set_ari_dir(str(original_user_root))


def _as_user(monkeypatch: pytest.MonkeyPatch, perms: set,
             profiles: set) -> None:
    """Pretend the request comes from a user with perms/profile access."""
    user = dict(username='tester', groups=['monitor.SPIROU'])
    monkeypatch.setattr(aq, '_user_perms', lambda app: (user, set(perms)))
    monkeypatch.setattr(aq, '_accessible_profile_keys',
                        lambda app, user_info, user_perms: set(profiles))


def _save_queue(port: int, **overrides: Any) -> None:
    """Save one queue definition pointing at a local port."""
    raw = dict(ssh_config_host='narval1', local_port=str(port),
               instrument='SPIROU', profile_id='spirou_main')
    raw.update(overrides)
    apero_queues.save_queues(dict(q1=apero_queues.normalize_queue(raw)))


def test_normalize_and_validate() -> None:
    """Defaults are filled in and invalid definitions are rejected."""
    assert dev is not None
    qdef = apero_queues.normalize_queue(dict(blocked_actions=['bad', 'run']))
    assert qdef['remote_host'] == 'localhost'
    assert qdef['remote_port'] == apero_queues.DEFAULT_REMOTE_PORT
    assert qdef['blocked_actions'] == ['run']
    default = apero_queues.normalize_queue(dict())
    assert default['blocked_actions'] == ['reset_data', 'shutdown']
    good = apero_queues.normalize_queue(dict(
        ssh_config_host='h', local_port='18090', instrument='spirou',
        profile_id='p'))
    assert good['instrument'] == 'SPIROU'
    assert apero_queues.validate_queue('ok_name', good, dict()) == ''
    assert 'name' in apero_queues.validate_queue('bad name', good, dict())
    clash = apero_queues.validate_queue('b', good, dict(a=good))
    assert 'already used' in clash
    params = apero_queues.tunnel_params(good, '/tmp/ari')
    assert params['TUNNEL_STATE_SUBDIR'] == 'queue_tunnels'


def test_monitor_access_follows_profile(app: Any,
                                        monkeypatch: pytest.MonkeyPatch
                                        ) -> None:
    """Monitors only see queues linked to profiles they can access."""
    _save_queue(18090)
    _as_user(monkeypatch, {'monitor.SPIROU'}, {('SPIROU', 'spirou_main')})
    user, perms = aq._user_perms(app)
    assert list(aq.accessible_queues(app, user, perms)) == ['q1']
    _as_user(monkeypatch, {'monitor.SPIROU'}, {('SPIROU', 'other')})
    user, perms = aq._user_perms(app)
    assert aq.accessible_queues(app, user, perms) == dict()
    _as_user(monkeypatch, {aq.PERMISSION}, set())
    user, perms = aq._user_perms(app)
    assert list(aq.accessible_queues(app, user, perms)) == ['q1']


def test_proxy_forwards_and_blocks(app: Any, fake_gui: int,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """The proxy forwards dashboard calls and refuses blocked actions."""
    _save_queue(fake_gui)
    _as_user(monkeypatch, {'monitor.SPIROU'}, {('SPIROU', 'spirou_main')})
    client = app.test_client()
    base = '/monitor_portal/apero_queue/q1/proxy/'
    page = client.get(base)
    assert page.status_code == 200
    assert b'#btn-shutdown' in page.data
    assert client.get(base + 'api/status?qstate=all').get_json() == dict(
        path='/api/status?qstate=all')
    assert client.post(base + 'api/run', json=dict(cores=2)).status_code == 200
    assert _FakeQueueGui.posted[-1][0] == '/api/run'
    assert client.post(base + 'api/reset_data', json=dict()).status_code == 403
    assert client.post(base + 'api/run', data='x').status_code == 415
    assert client.get(base + '../etc/passwd').status_code == 404
    assert client.get('/monitor_portal/apero_queue/nope/proxy/'
                      ).status_code == 404
    _as_user(monkeypatch, {aq.PERMISSION}, set())
    assert client.post(base + 'api/reset_data', json=dict()).status_code == 200
    assert b'#btn-shutdown' not in client.get(base).data


def test_admin_api_requires_permission(app: Any,
                                       monkeypatch: pytest.MonkeyPatch
                                       ) -> None:
    """Only users with the setup permission can manage definitions."""
    client = app.test_client()
    _as_user(monkeypatch, {'monitor.SPIROU'}, set())
    assert client.get('/api/admin/apero-queue/list').status_code == 403
    _as_user(monkeypatch, {aq.PERMISSION}, set())
    body = dict(name='q2', ssh_config_host='h', local_port='18091',
                instrument='SPIROU', profile_id='p')
    saved = client.post('/api/admin/apero-queue/save', json=body)
    assert saved.get_json()['success']
    assert 'q2' in apero_queues.load_queues()
    bad = client.post('/api/admin/apero-queue/save', json=dict(name='x y'))
    assert bad.status_code == 400
