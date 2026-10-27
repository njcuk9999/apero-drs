#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused coverage for server-to-server sync (engine, adapters, protocol)."""

import contextlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List

import pytest
import yaml

from apero import dev
from apero_ri.core import auth
from apero_ri.core import issues
from apero_ri.core import user_data
from apero_ri.core.server_sync import adapters
from apero_ri.core.server_sync import crypto
from apero_ri.core.server_sync import engine
from apero_ri.core.server_sync import local_setup
from apero_ri.core.server_sync import store

# categories exercised end-to-end (others write outside tmp dirs)
CATS = ('users', 'user_data', 'science_groups', 'issues', 'apero_profiles',
        'astrometrics', 'db_definitions')


class Server:
    """One simulated ARI server living in its own data directory."""

    def __init__(self, root: Path, root_user: str) -> None:
        """Create the directory layout and setup state.

        :param root: Data directory.
        :param root_user: Setup (root) admin username.
        :return: None.
        """
        self.root = root
        (root / 'admin').mkdir(parents=True)
        state = dict(completed=True, admin_username=root_user)
        (root / 'admin' / 'setup_state.yaml').write_text(yaml.dump(state))

    @contextlib.contextmanager
    def active(self) -> Iterator[None]:
        """Point every storage module at this server's directory.

        :return: Context manager.
        """
        saved = auth.ARI_DIR
        saved_user = user_data.ARI_DIR
        auth.set_ari_dir(str(self.root))
        auth._ari_dir_ensured = False
        auth._profiles_cache.clear()
        user_data.set_ari_dir(str(self.root))
        # every other store follows ARI_DIR (as set from --data-dir)
        old_env = os.environ.get('ARI_DIR')
        os.environ['ARI_DIR'] = str(self.root)
        try:
            yield
        finally:
            auth.set_ari_dir(str(saved))
            auth._ari_dir_ensured = False
            auth._profiles_cache.clear()
            user_data.set_ari_dir(str(saved_user))
            if old_env is None:
                os.environ.pop('ARI_DIR', None)
            else:
                os.environ['ARI_DIR'] = old_env


class FakeClient:
    """PeerClient stand-in that serves requests from another Server."""

    def __init__(self, remote: Server, scope: str = 'readwrite') -> None:
        """Remember the remote server and token scope.

        :param remote: Server answering the requests.
        :param scope: Token scope granted by the remote server.
        :return: None.
        """
        self.remote = remote
        self.scope = scope

    def _call(self, action: str, payload: Any) -> Any:
        payload = json.loads(json.dumps(payload, default=str))
        with self.remote.active():
            out = engine.handle_peer(action, payload, self.scope, 'test')
        return json.loads(json.dumps(out, default=str))

    def hello(self, server_name: str) -> Dict[str, Any]:
        info = self._call('hello', dict())
        info['clock_skew'] = 0.0
        return info

    def manifest(self, categories: List[str]) -> Dict[str, Any]:
        return self._call('manifest', dict(categories=list(categories)))

    def fetch(self, category: str, keys: List[str]) -> Dict[str, Any]:
        return self._call('fetch', dict(category=category, keys=keys))

    def apply(self, category: str, upserts: Dict[str, Any],
              deletes: Dict[str, Any]) -> Dict[str, str]:
        payload = dict(category=category, upserts=upserts, deletes=deletes)
        return self._call('apply', payload)


@pytest.fixture()
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Two servers, A configured with B as a mirror peer.

    :param tmp_path: Temporary root.
    :param monkeypatch: Fixture used to route the client to server B.
    :return: Tuple (server A, server B, peer id, client holder).
    """
    assert dev is not None
    server_a = Server(tmp_path / 'a', 'roota')
    server_b = Server(tmp_path / 'b', 'rootb')
    holder = dict(client=FakeClient(server_b))
    monkeypatch.setattr(engine, 'make_client',
                        lambda peer: holder['client'])
    with server_a.active():
        _, _, token = crypto.new_token()
        cats = {name: name in CATS for name in adapters.ADAPTERS}
        peer = dict(label='B', url='http://b.example', mode='mirror',
                    categories=cats, approved=False, auto_sync=False)
        peer = store.add_peer(peer, token)
    yield server_a, server_b, peer['peer_id'], holder


def _users(server: Server) -> Dict[str, dict]:
    with server.active():
        return auth.load_users()


def _add_user(server: Server, name: str, email: str, **extra: Any) -> None:
    with server.active():
        users = auth.load_users()
        users[name] = dict(password='x:y', groups=['general.SPIROU'],
                           emails=[email], **extra)
        auth.save_users(users)


def _run(server: Server, peer_id: str, dry_run: bool = False) -> dict:
    with server.active():
        return engine.run_peer(peer_id, dry_run=dry_run, kind='records')


def _bump(server: Server) -> None:
    """Ensure the next write gets a strictly later mtime."""
    path = server.root / 'admin' / 'general' / 'users.yaml'
    if path.exists():
        stat = path.stat()
        os.utime(path, (stat.st_atime - 10, stat.st_mtime - 10))


def test_crypto_round_trip_and_tamper() -> None:
    """Signed requests verify; tampering and wrong keys are rejected."""
    key_id, secret, token = crypto.new_token()
    assert crypto.parse_token(token) == (key_id, secret)
    blob = crypto.encrypt_payload(secret, dict(a=1))
    assert crypto.decrypt_payload(secret, blob) == dict(a=1)
    _, other, _ = crypto.new_token()
    with pytest.raises(ValueError):
        crypto.decrypt_payload(other, blob)
    sig = crypto.sign_request(secret, 'POST', '/p', '1', 'n', blob)
    assert crypto.verify_request(secret, 'POST', '/p', '1', 'n', blob, sig)
    assert not crypto.verify_request(secret, 'POST', '/p', '1', 'n',
                                     blob + b'x', sig)
    with pytest.raises(ValueError):
        crypto.parse_token('nope')


def test_stop_prevents_next_push(pair: Any,
                               monkeypatch: pytest.MonkeyPatch) -> None:
    """Stopping after reading data prevents the next remote mutation."""
    server_a, server_b, peer_id, _ = pair
    _add_user(server_a, 'alice', 'alice@x')
    original = engine.load_records

    def load(category: str, keys: Any) -> dict:
        records = original(category, keys)
        store.request_stop(peer_id, 'tester')
        return records

    monkeypatch.setattr(engine, 'load_records', load)
    summary = _run(server_a, peer_id)
    assert summary.get('cancelled') is True
    assert summary['ok'] is False
    assert 'alice' not in _users(server_b)
    with server_a.active():
        assert store.run_status(peer_id)['status'] == 'cancelled'
        assert store.get_peer(peer_id)['auto_sync'] is False
        assert 'last_sync_at' not in store.get_peer(peer_id)
        with pytest.raises(store.SyncCancelled):
            store.check_cancelled(peer_id)


def test_stop_clears_legacy_stale_marker(pair: Any) -> None:
    """A stale running marker can be stopped when no worker holds the lock."""
    server_a, _, peer_id, _ = pair
    with server_a.active():
        path = store.peer_dir(peer_id) / 'run.json'
        store.write_json(path, dict(status='running'))
        result = store.request_stop(peer_id, 'tester')
        assert result['status'] == 'cancelled'
        assert store.run_status(peer_id)['status'] == 'cancelled'


def test_exited_process_marker_is_interrupted(pair: Any) -> None:
    """PID reuse cannot leave a previous process's run marked active."""
    server_a, _, peer_id, _ = pair
    with server_a.active():
        state = store.running_status()
        state['process_started'] -= 1
        store.write_json(store.peer_dir(peer_id) / 'run.json', state)
        assert store.run_status(peer_id)['status'] == 'interrupted'


def test_mirror_users_root_excluded_and_deletions(pair: Any) -> None:
    """Mirror exchanges users both ways, never roots, and propagates deletes."""
    server_a, server_b, peer_id, _ = pair
    _add_user(server_a, 'roota', 'ra@x')
    _add_user(server_a, 'alice', 'alice@x')
    _add_user(server_b, 'rootb', 'rb@x')
    _add_user(server_b, 'bob', 'bob@x')
    summary = _run(server_a, peer_id)
    assert summary['ok'], summary['errors']
    assert set(_users(server_a)) == {'roota', 'alice', 'bob'}
    assert set(_users(server_b)) == {'rootb', 'alice', 'bob'}
    # edit on B, delete on A
    _bump(server_b)
    with server_b.active():
        users = auth.load_users()
        users['alice']['groups'] = ['admin']
        auth.save_users(users)
    with server_a.active():
        users = auth.load_users()
        users.pop('bob')
        auth.save_users(users)
    summary = _run(server_a, peer_id)
    assert summary['ok'], summary['errors']
    assert _users(server_a)['alice']['groups'] == ['admin']
    assert 'bob' not in _users(server_b)
    assert 'rootb' in _users(server_b)
    # a further run has nothing left to do
    summary = _run(server_a, peer_id, dry_run=True)
    counts = summary['categories']['users']
    assert counts['pull'] == counts['push'] == counts['conflicts'] == 0


def test_volatile_fields_and_per_user_files(pair: Any) -> None:
    """last_login stays local; user notes and links are copied verbatim."""
    server_a, server_b, peer_id, _ = pair
    _add_user(server_a, 'alice', 'alice@x', last_login='today')
    with server_a.active():
        user_data.save_links('alice', dict(sections=['s'], types=dict(),
                                           links=dict()))
        note = user_data.USERS_DIR / 'alice' / 'notes' / 'n1.md'
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text('---\nid: n1\n---\nhello\n')
    assert _run(server_a, peer_id)['ok']
    assert 'last_login' not in _users(server_b)['alice']
    note_b = server_b.root / 'users' / 'alice' / 'notes' / 'n1.md'
    assert note_b.read_text().endswith('hello\n')
    assert (server_b.root / 'users' / 'alice' / 'links.yaml').exists()


def test_duplicate_and_divergent_conflicts(pair: Any) -> None:
    """Identity clashes and first-sync divergence wait for a decision."""
    server_a, server_b, peer_id, _ = pair
    _add_user(server_a, 'alice', 'same@x')
    _add_user(server_b, 'alice2', 'same@x')
    _add_user(server_a, 'carol', 'carol@x', institutions=['A'])
    _add_user(server_b, 'carol', 'carol@x', institutions=['B'])
    summary = _run(server_a, peer_id)
    assert summary['conflicts'] >= 2
    assert 'alice2' not in _users(server_a)
    assert _users(server_a)['carol']['institutions'] == ['A']
    with server_a.active():
        state = store.load_state(peer_id)
        state['resolutions']['users'] = {
            adapters.make_key('alice2'): 'allow',
            adapters.make_key('alice'): 'allow',
            adapters.make_key('carol'): 'remote'}
        store.save_state(peer_id, state)
    summary = _run(server_a, peer_id)
    assert summary['ok'], summary['errors']
    assert 'alice2' in _users(server_a)
    assert _users(server_a)['carol']['institutions'] == ['B']
    with server_a.active():
        # one-shot decisions are consumed
        assert not store.load_state(peer_id)['resolutions']['users']


def test_copy_mode_keeps_local_changes(pair: Any) -> None:
    """Copy mode never pushes; remote changes win."""
    server_a, server_b, peer_id, _ = pair
    with server_a.active():
        store.update_peer(peer_id, mode='copy')
    _add_user(server_a, 'local_only', 'l@x')
    _add_user(server_b, 'bob', 'bob@x')
    assert _run(server_a, peer_id)['ok']
    assert 'bob' in _users(server_a)
    assert 'local_only' not in _users(server_b)


def test_profiles_keep_paths_and_need_setup(pair: Any) -> None:
    """Profile paths stay local; new profiles arrive disabled and flagged."""
    server_a, server_b, peer_id, _ = pair
    with server_b.active():
        cfg = dict(apero_version='0.8', paths=dict(PATH_RAW='/b/raw'),
                   database=dict(DATABASE_NAME='db'))
        auth.save_apero_profiles(dict(SPIROU=dict(p1=cfg)))
    assert _run(server_a, peer_id)['ok']
    with server_a.active():
        prof = auth.load_apero_profiles(hydrate=False)['SPIROU']['p1']
        assert prof['paths'] == dict()
        assert prof['disabled'] is True
        assert prof['database']['DATABASE_NAME'] == 'db'
        kinds = [i['kind'] for i in local_setup.pending_items()]
        assert 'profile' in kinds
        prof['paths'] = dict(PATH_RAW='/a/raw')
        auth.save_apero_profiles(dict(SPIROU=dict(p1=prof)))
    summary = _run(server_a, peer_id, dry_run=True)
    assert summary['categories']['apero_profiles']['push'] == 0
    with server_b.active():
        prof_b = auth.load_apero_profiles(hydrate=False)['SPIROU']['p1']
        assert prof_b['paths'] == dict(PATH_RAW='/b/raw')


def test_issues_keep_local_ids(pair: Any) -> None:
    """Issues match on sync uid; numeric ids are assigned locally."""
    server_a, server_b, peer_id, _ = pair
    with server_a.active():
        issues.create_issue(server_a.root, 'other', 'from a', 'alice')
    with server_b.active():
        issues.create_issue(server_b.root, 'other', 'from b', 'bob')
    assert _run(server_a, peer_id)['ok']
    with server_a.active():
        rows = issues._load(server_a.root)
    assert sorted(r['id'] for r in rows) == [1, 2]
    assert {r['reason'] for r in rows} == {'from a', 'from b'}


def test_astrometric_history_merges(pair: Any) -> None:
    """Diverged astrometric history files become the union of both."""
    server_a, server_b, peer_id, _ = pair
    for server, stamp in ((server_a, '1'), (server_b, '2')):
        hist = server.root / 'apero-assets' / 'astrometrics' / '.history'
        hist.mkdir(parents=True)
        line = json.dumps(dict(timestamp=stamp, action='edit'))
        (hist / 'GL699.jsonl').write_text(line + '\n')
    assert _run(server_a, peer_id)['ok']
    for server in (server_a, server_b):
        path = (server.root / 'apero-assets' / 'astrometrics' / '.history'
                / 'GL699.jsonl')
        assert len(path.read_text().splitlines()) == 2


def test_db_tunnel_local_fields(pair: Any) -> None:
    """Tunnel aliases/ports stay local and new tunnels need setup."""
    server_a, server_b, peer_id, _ = pair
    with server_b.active():
        tun = dict(ssh_config_host='b-alias', remote_host='db', local_port='1',
                   remote_port='3306', ssh_mode='apero')
        auth.save_db_tunnels(dict(tunnels=dict(t1=tun), local_databases={}))
    assert _run(server_a, peer_id)['ok']
    with server_a.active():
        tun_a = auth.load_db_tunnels()['tunnels']['t1']
        assert tun_a[adapters.NEEDS_SETUP] is True
        local_setup.update_item('tunnel', 't1',
                                dict(ssh_config_host='a-alias',
                                     local_port='3307'))
        tun_a = auth.load_db_tunnels()['tunnels']['t1']
        assert adapters.NEEDS_SETUP not in tun_a
    summary = _run(server_a, peer_id, dry_run=True)
    assert summary['categories']['db_definitions']['push'] == 0
    with server_b.active():
        assert auth.load_db_tunnels()['tunnels']['t1']['local_port'] == '1'
    with pytest.raises(ValueError):
        local_setup.update_item('tunnel', 't1',
                                dict(ssh_config_host='x\nProxyCommand'))


def test_read_only_token_blocks_mirror(pair: Any) -> None:
    """A read-only token cannot be used for a mirror."""
    server_a, _, peer_id, holder = pair
    holder['client'] = FakeClient(holder['client'].remote, scope='read')
    summary = _run(server_a, peer_id)
    assert not summary['ok']
    assert 'read+write' in ' '.join(summary['errors'])


def test_every_adapter_exports_and_round_trips(
        pair: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """All categories export on a fresh server and sync without errors."""
    from apero_ri.core import known_errors
    from apero_ri.core import notifications
    from apero_ri.core import vault_store

    server_a, server_b, peer_id, _ = pair
    # known errors live in the package, not the data dir: redirect them
    monkeypatch.setattr(known_errors, 'known_errors_dir',
                        lambda: _mk(Path(os.environ['ARI_DIR']) / 'ke'))
    with server_a.active():
        names = [n for n in adapters.ADAPTERS if n != 'email']
        store.update_peer(peer_id, categories={n: True for n in names})
        notifications.emit_notification('alice', 'system', 'hi')
        vault_store.save_entry('title', 'secret', 'admin', 'alice')
        assert notifications.notif_db().is_relative_to(server_a.root)
    summary = _run(server_a, peer_id)
    assert summary['ok'], summary['errors']
    summary = _run(server_a, peer_id, dry_run=True)
    for name, counts in summary['categories'].items():
        moved = counts['pull'] + counts['push'] + counts['conflicts']
        assert moved == 0, (name, counts)
    with server_b.active():
        assert len(vault_store.load_entries()) == 1
        assert (server_b.root / 'admin' / 'general' / 'vault.yaml').exists()


def test_rejection_list_and_checks_policy(pair: Any) -> None:
    """Rejection rows/history and the checks policy sync between servers."""
    from apero.core import drs_rejection
    from apero_ri.core import apero_checks
    import pandas as pd

    server_a, server_b, peer_id, _ = pair
    with server_a.active():
        cats = dict(rejection_list=True, checks_policy=True)
        store.update_peer(peer_id, categories=cats)
    rows = dict(a=['ID_A'], b=['ID_B'])
    for server, tag in ((server_a, 'a'), (server_b, 'b')):
        path = server.root / 'apero-assets' / 'spirou' / 'reject'
        path.mkdir(parents=True)
        frame = pd.DataFrame([dict(IDENTIFIER=i, PP=1, TEL=0, RV=0, USED=1,
                                   DATE_ADDED='2026-01-01', WHO=tag)
                              for i in rows[tag]],
                             columns=drs_rejection.CSV_COLUMNS)
        drs_rejection._write_csv(str(path / 'reject.csv'), frame)
        hist = server.root / 'apero-assets' / '.rejection_history'
        hist.mkdir(parents=True)
        line = json.dumps(dict(timestamp=tag, identifier=tag,
                               resolved=False))
        (hist / 'rejection_list.jsonl').write_text(line + '\n')
    with server_a.active():
        policy = dict(ignored_checks=['X'], checks_root='/a/checks',
                      excluded_obsdirs=dict(SPIROU=['2026-01-01']))
        apero_checks.save_config(server_a.root, policy)
    summary = _run(server_a, peer_id)
    assert summary['ok'], summary['errors']
    for server in (server_a, server_b):
        csv = server.root / 'apero-assets/spirou/reject/reject.csv'
        ids = set(drs_rejection._read_csv(str(csv))['IDENTIFIER'])
        assert ids == {'ID_A', 'ID_B'}
        hist = (server.root / 'apero-assets/.rejection_history'
                / 'rejection_list.jsonl')
        assert len(hist.read_text().splitlines()) == 2
    cfg_b = apero_checks.load_config(server_b.root)
    assert cfg_b['ignored_checks'] == ['X']
    assert cfg_b['excluded_obsdirs'] == dict(SPIROU=['2026-01-01'])
    assert 'checks_root' not in cfg_b
    summary = _run(server_a, peer_id, dry_run=True)
    for name in ('rejection_list', 'checks_policy'):
        counts = summary['categories'][name]
        assert counts['pull'] + counts['push'] + counts['merge'] == 0


def _mk(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_ssh_host_block_validation() -> None:
    """Host blocks reject injected directives."""
    block = local_setup.build_host_block(dict(alias='db', hostname='h.org',
                                              user='me', port='22'))
    assert block.startswith('Host db\n')
    with pytest.raises(ValueError):
        local_setup.build_host_block(dict(alias='db', hostname='h org'))


def test_peer_endpoint_authentication(tmp_path: Path,
                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Signed hello works once; replays and bad signatures are refused."""
    from apero_ri.application.application import ARIApp
    from apero_ri.core import task_runner

    original_root = auth.ARI_DIR
    original_user_root = user_data.ARI_DIR
    monkeypatch.setattr(sys, 'argv', ['ari-test', '--data-dir',
                                      str(tmp_path)])
    monkeypatch.setenv('ARI_DIR', str(tmp_path))
    monkeypatch.setattr(task_runner, 'start_background_services',
                        lambda *values: None)
    monkeypatch.setattr(ARIApp, '_start_admin_health_refresher',
                        lambda self: None)
    monkeypatch.setattr(auth, 'ensure_default_user', lambda: None)
    monkeypatch.setattr(auth, '_ari_dir_ensured', False)
    app = ARIApp()
    app.config.update(TESTING=True, SECRET_KEY='ss', RATELIMIT_ENABLED=False)
    try:
        token = store.issue_token('peer', 'read', 'tester')
        key_id, secret = crypto.parse_token(token)
        client = app.test_client()
        path = '/api/server-sync/peer/hello'
        body = crypto.encrypt_payload(secret, dict(nonce='n1', payload={}))
        headers = dict()
        headers[crypto.HDR_KEY_ID] = key_id
        headers[crypto.HDR_TIMESTAMP] = str(int(__import__('time').time()))
        headers[crypto.HDR_NONCE] = 'n1'
        sign_args = [secret, 'POST', path, headers[crypto.HDR_TIMESTAMP],
                     'n1', body]
        headers[crypto.HDR_SIGNATURE] = crypto.sign_request(*sign_args)
        resp = client.post(path, data=body, headers=headers)
        assert resp.status_code == 200
        reply = crypto.decrypt_payload(secret, resp.data)
        assert reply['payload']['scope'] == 'read'
        # replayed nonce
        assert client.post(path, data=body, headers=headers).status_code == 401
        # tampered signature
        headers[crypto.HDR_NONCE] = 'n2'
        assert client.post(path, data=body, headers=headers).status_code == 401
        # admin API refuses anonymous users
        resp = client.get('/api/admin/server-sync/overview')
        assert resp.status_code == 401
        # super admin sees the page and API; an admin does not
        auth.create_user('boss', 'pw', ['super_admin'])
        auth.create_user('helper', 'pw', ['admin'])
        with client.session_transaction() as sess:
            sess['user'] = 'helper'
        resp = client.get('/api/admin/server-sync/overview')
        assert resp.status_code == 403
        with client.session_transaction() as sess:
            sess['user'] = 'boss'
        resp = client.get('/admin_portal/server_sync')
        assert resp.status_code == 200
        assert b'ss-root' in resp.data
        data = client.get('/api/admin/server-sync/overview').get_json()
        assert data['success'] and len(data['categories']) > 10
        resp = client.post('/api/admin/server-sync/issue_token',
                           json=dict(label='x', scope='bad'))
        assert resp.status_code == 400
        _, _, peer_token = crypto.new_token()
        peer = store.add_peer(dict(label='test', auto_sync=True), peer_token)
        resp = client.post('/api/admin/server-sync/stop',
                   json=dict(peer_id=peer['peer_id']))
        assert resp.status_code == 200
        assert resp.get_json()['run']['status'] == 'cancelled'
        assert store.get_peer(peer['peer_id'])['auto_sync'] is False
    finally:
        auth.set_ari_dir(str(original_root))
        user_data.set_ari_dir(str(original_user_root))
