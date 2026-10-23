#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: endpoints for the admin Server Sync page and the peer protocol.

Admin endpoints (``/api/admin/server-sync/<action>``) require a logged-in
super admin. Peer endpoints (``/api/server-sync/peer/<action>``) are
called by other ARI servers and are authenticated by an issued sync
token (HMAC signature + nonce + timestamp); they never use the session.

Created on 2026-10-22

@author: cook
"""
import threading
import time
from typing import Any, Dict, Optional, Tuple

from flask import Response, jsonify, request, session

from apero_ri.ari_api import server_sync as peer_api
from apero_ri.core import auth
from apero_ri.core import permissions
from apero_ri.core.server_sync import adapters
from apero_ri.core.server_sync import crypto
from apero_ri.core.server_sync import engine
from apero_ri.core.server_sync import local_setup
from apero_ri.core.server_sync import store

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.application.server_sync_api_helpers'
# permission required for every admin endpoint
PERMISSION = 'manage.admin.server_sync'
# async task keys driving automatic sync
TASK_KEYS = ('SERVER_SYNC', 'SERVER_SYNC_TASK_DATA')
# maximum body size accepted by the peer apply endpoint (bytes)
PEER_MAX_BODY = 512 * 1024 * 1024


# =============================================================================
# Define admin permission helper
# =============================================================================
def _require(app: Any) -> Tuple[Optional[dict], Any]:
    """
    Require a super admin with the server-sync permission.

    :param app: ARIApp
    :return: tuple (user_info, None) or (None, error response)
    """
    user_info = auth.get_effective_user(session)
    if not user_info:
        return None, (jsonify(success=False, error='Login required'), 401)
    groups = user_info.get('groups', [])
    perms = permissions.resolve_user_permissions(groups, app.ari_groups)
    if PERMISSION not in perms or not auth.user_is_super_admin(groups):
        return None, (jsonify(success=False, error='Forbidden'), 403)
    return user_info, None


def _body() -> Dict[str, Any]:
    """Return the JSON request body as a dict."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else dict()


def _fail(message: str, status: int = 400) -> Tuple[Any, int]:
    """Return a JSON error response."""
    return jsonify(success=False, error=str(message)), status


# =============================================================================
# Define admin views
# =============================================================================
def _task_status() -> Dict[str, Any]:
    """
    Return the async task rows for the sync tasks.

    :return: dict task_key -> {active, frequency, last_run, last_status}
    :rtype: dict
    """
    out = dict()
    for row in auth.load_async_tasks().get('__GLOBAL__') or []:
        key = row.get('task_key')
        if key in TASK_KEYS:
            info = dict()
            for name in ('active', 'frequency', 'last_run', 'last_status',
                         'run_count'):
                info[name] = row.get(name)
            out[key] = info
    return out


def _peer_view(peer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a peer config safe for the browser (plus run status).

    :param peer: dict, stored peer config

    :return: dict
    :rtype: dict
    """
    view = dict(peer)
    view['categories'] = dict(adapters.default_categories(),
                              **(peer.get('categories') or dict()))
    view['run'] = store.read_json(store.peer_dir(peer['peer_id'])
                                  / 'run.json', dict())
    view['has_token'] = bool(store.get_peer_token(peer['peer_id']))
    return view


def overview(app: Any, user: dict) -> Any:
    """GET: everything the page needs on load."""
    out = dict(success=True)
    out['identity'] = store.get_identity()
    out['root_username'] = store.root_username()
    out['categories'] = adapters.describe()
    out['peers'] = [_peer_view(p) for p in store.load_peers().values()]
    out['issued'] = store.list_issued()
    out['tasks'] = _task_status()
    out['pending_setup'] = len(local_setup.pending_items())
    out['this_url'] = request.host_url.rstrip('/') + request.script_root
    return jsonify(out)


def set_identity(app: Any, user: dict) -> Any:
    """POST {server_name}: rename this server."""
    identity = store.set_server_name(_body().get('server_name', ''))
    return jsonify(success=True, identity=identity)


def issue_token(app: Any, user: dict) -> Any:
    """POST {label, scope}: create a token for another server."""
    body = _body()
    try:
        token = store.issue_token(body.get('label', ''),
                                  body.get('scope', 'readwrite'),
                                  user['username'])
    except ValueError as exc:
        return _fail(exc)
    return jsonify(success=True, token=token, issued=store.list_issued())


def revoke_token(app: Any, user: dict) -> Any:
    """POST {key_id}: revoke an issued token."""
    removed = store.revoke_issued(str(_body().get('key_id', '')))
    return jsonify(success=removed, issued=store.list_issued())


def _clean_categories(raw: Any) -> Dict[str, bool]:
    """Keep only known category toggles."""
    raw = raw if isinstance(raw, dict) else dict()
    return {k: bool(v) for k, v in raw.items() if k in adapters.ADAPTERS}


def add_peer(app: Any, user: dict) -> Any:
    """POST {label, url, token, mode}: test then save a peer."""
    body = _body()
    mode = body.get('mode', 'mirror')
    if mode not in store.MODES:
        return _fail(f'mode must be one of {store.MODES}')
    try:
        url = peer_api.normalise_url(body.get('url', ''))
        crypto.parse_token(body.get('token', ''))
    except ValueError as exc:
        return _fail(exc)
    peer = dict(label=str(body.get('label') or url)[:120], url=url,
                mode=mode, categories=adapters.default_categories(),
                approved=False, auto_sync=False, created_by=user['username'])
    peer = store.add_peer(peer, body['token'].strip())
    try:
        info = engine.handshake(peer)
    except Exception as exc:
        store.delete_peer(peer['peer_id'])
        return _fail(f'Connection test failed: {exc}')
    if info['blocking']:
        store.delete_peer(peer['peer_id'])
        return _fail(' '.join(info['blocking']))
    peer = store.get_peer(peer['peer_id'])
    return jsonify(success=True, peer=_peer_view(peer), hello=info)


def update_peer(app: Any, user: dict) -> Any:
    """POST {peer_id, ...}: edit label/url/token/mode/categories/auto."""
    body = _body()
    peer = store.get_peer(str(body.get('peer_id', '')))
    if peer is None:
        return _fail('Unknown peer', 404)
    changes = dict()
    if 'label' in body:
        changes['label'] = str(body['label'] or '')[:120]
    try:
        if body.get('url'):
            changes['url'] = peer_api.normalise_url(body['url'])
        if body.get('token'):
            key_id, _ = crypto.parse_token(body['token'])
            store.set_peer_token(peer['peer_id'], body['token'].strip())
            changes['key_id'] = key_id
    except ValueError as exc:
        return _fail(exc)
    if body.get('mode') in store.MODES and body['mode'] != peer['mode']:
        changes['mode'] = body['mode']
        # a different mode needs a fresh reviewed run
        changes['approved'] = False
        changes['auto_sync'] = False
    if 'categories' in body:
        old = dict(adapters.default_categories(),
                   **(peer.get('categories') or dict()))
        new = dict(old, **_clean_categories(body['categories']))
        changes['categories'] = new
        if any(new[k] and not old.get(k) for k in new):
            # newly enabled data must be reviewed before auto sync
            changes['approved'] = False
            changes['auto_sync'] = False
    if 'auto_sync' in body:
        wanted = bool(body['auto_sync'])
        approved = changes.get('approved', peer.get('approved'))
        if wanted and not approved:
            return _fail('Run a reviewed sync from the Run tab first.')
        changes['auto_sync'] = wanted
    peer = store.update_peer(peer['peer_id'], **changes)
    return jsonify(success=True, peer=_peer_view(peer))


def delete_peer(app: Any, user: dict) -> Any:
    """POST {peer_id}: forget a peer and its sync state."""
    removed = store.delete_peer(str(_body().get('peer_id', '')))
    return jsonify(success=removed)


def test_peer(app: Any, user: dict) -> Any:
    """POST {peer_id}: re-run the handshake."""
    peer = store.get_peer(str(_body().get('peer_id', '')))
    if peer is None:
        return _fail('Unknown peer', 404)
    try:
        info = engine.handshake(peer)
    except Exception as exc:
        return _fail(f'Connection test failed: {exc}')
    return jsonify(success=True, hello=info,
                   peer=_peer_view(store.get_peer(peer['peer_id'])))


def _run_thread(peer_id: str, dry_run: bool, kind: str, actor: str) -> None:
    """
    Run a sync in a background thread, recording status in run.json.

    :return: None
    """
    path = store.peer_dir(peer_id) / 'run.json'
    try:
        summary = engine.run_peer(peer_id, dry_run=dry_run, kind=kind,
                                  actor=actor)
    except store.SyncBusy as exc:
        summary = dict(ok=False, errors=[str(exc)], conflicts=0)
    except Exception as exc:
        summary = dict(ok=False, errors=[f'{type(exc).__name__}: {exc}'],
                       conflicts=0)
    status = dict(status='done', dry_run=dry_run, kind=kind,
                  finished_at=store.now_iso(), summary=summary)
    store.write_json(path, status)
    # a successful reviewed (non-dry) manual run unlocks automatic sync
    if summary.get('ok') and not dry_run:
        store.update_peer(peer_id, approved=True, approved_by=actor,
                          approved_at=store.now_iso())


def run(app: Any, user: dict) -> Any:
    """POST {peer_id, dry_run, kind}: start an analysis or a sync."""
    body = _body()
    peer = store.get_peer(str(body.get('peer_id', '')))
    if peer is None:
        return _fail('Unknown peer', 404)
    kind = body.get('kind', 'all')
    if kind not in engine.RUN_KINDS:
        return _fail(f'kind must be one of {engine.RUN_KINDS}')
    dry_run = bool(body.get('dry_run', True))
    path = store.peer_dir(peer['peer_id']) / 'run.json'
    current = store.read_json(path, dict())
    # a 'running' marker older than 6h is from a crashed worker
    started = float(current.get('started_ts') or 0)
    if current.get('status') == 'running' and time.time() - started < 21600:
        return _fail('A run is already in progress for this peer', 409)
    status = dict(status='running', dry_run=dry_run, kind=kind,
                  started_at=store.now_iso(), started_ts=time.time(),
                  actor=user['username'])
    store.write_json(path, status)
    thread_args = (peer['peer_id'], dry_run, kind, user['username'])
    thread = threading.Thread(target=_run_thread, args=thread_args,
                              daemon=True, name='ari-server-sync')
    thread.start()
    return jsonify(success=True, run=status)


def plan(app: Any, user: dict) -> Any:
    """GET ?peer_id: last plan, resolutions and run status."""
    peer = store.get_peer(str(request.args.get('peer_id', '')))
    if peer is None:
        return _fail('Unknown peer', 404)
    state = store.load_state(peer['peer_id'])
    out = dict(success=True, peer=_peer_view(peer))
    out['plan'] = state.get('last_plan') or dict()
    out['plan_at'] = state.get('last_plan_at')
    out['plan_dry_run'] = state.get('last_plan_dry_run')
    out['resolutions'] = state.get('resolutions') or dict()
    return jsonify(out)


def resolve(app: Any, user: dict) -> Any:
    """POST {peer_id, category, keys, resolution}: resolve conflicts."""
    body = _body()
    peer = store.get_peer(str(body.get('peer_id', '')))
    if peer is None:
        return _fail('Unknown peer', 404)
    category = body.get('category')
    if category not in adapters.ADAPTERS:
        return _fail('Unknown category')
    resolution = body.get('resolution')
    if resolution not in engine.RESOLUTIONS + ('clear',):
        return _fail(f'resolution must be one of {engine.RESOLUTIONS} or '
                     'clear')
    keys = [str(k) for k in body.get('keys') or []]
    state = store.load_state(peer['peer_id'])
    cat = state['resolutions'].setdefault(category, dict())
    for key in keys:
        if resolution == 'clear':
            cat.pop(key, None)
        else:
            cat[key] = resolution
    store.save_state(peer['peer_id'], state)
    return jsonify(success=True, resolutions=state['resolutions'])


def history(app: Any, user: dict) -> Any:
    """GET ?peer_id&limit: recent sync history."""
    peer_id = request.args.get('peer_id') or None
    try:
        limit = int(request.args.get('limit', 100))
    except ValueError:
        limit = 100
    rows = store.read_history(peer_id=peer_id, limit=limit)
    return jsonify(success=True, history=rows)


def task_update(app: Any, user: dict) -> Any:
    """POST {task_key, active, frequency}: edit the sync async task."""
    body = _body()
    task_key = body.get('task_key')
    if task_key not in TASK_KEYS:
        return _fail('Unknown task')
    tasks = auth.load_async_tasks()
    rows = [r for r in tasks.get('__GLOBAL__') or []
            if r.get('task_key') == task_key]
    if not rows:
        return _fail('Task not in the catalogue yet: open the Async Tasks '
                     'page once so it is registered.', 404)
    if 'active' in body:
        rows[0]['active'] = bool(body['active'])
    if 'frequency' in body:
        try:
            freq = float(body['frequency'])
        except (TypeError, ValueError):
            return _fail('frequency must be a number of hours')
        if freq < 0.05:
            return _fail('frequency must be at least 0.05 h (3 minutes)')
        rows[0]['frequency'] = freq
    auth.save_async_tasks(tasks)
    return jsonify(success=True, tasks=_task_status())


def setup_list(app: Any, user: dict) -> Any:
    """GET: records needing local setup and local ssh hosts."""
    out = dict(success=True)
    out['items'] = local_setup.pending_items()
    out['ssh_hosts'] = local_setup.ssh_hosts()
    out['ssh_config'] = str(local_setup.ssh_config_path())
    return jsonify(out)


def setup_update(app: Any, user: dict) -> Any:
    """POST {kind, name, values, done}: set local values on a record."""
    body = _body()
    try:
        values = body.get('values') if isinstance(body.get('values'),
                                                  dict) else dict()
        local_setup.update_item(str(body.get('kind', '')),
                                str(body.get('name', '')), values,
                                bool(body.get('done', True)))
    except ValueError as exc:
        return _fail(exc)
    return jsonify(success=True, items=local_setup.pending_items())


def ssh_preview(app: Any, user: dict) -> Any:
    """POST {fields}: preview a Host block."""
    try:
        block = local_setup.build_host_block(_body().get('fields') or dict())
    except ValueError as exc:
        return _fail(exc)
    return jsonify(success=True, block=block)


def ssh_append(app: Any, user: dict) -> Any:
    """POST {fields, confirm}: append a Host block to ~/.ssh/config."""
    body = _body()
    if not body.get('confirm'):
        return _fail('Confirmation required')
    try:
        result = local_setup.append_host_block(body.get('fields') or dict())
    except (ValueError, OSError) as exc:
        return _fail(exc)
    return jsonify(success=True, ssh_hosts=local_setup.ssh_hosts(), **result)


# admin action -> (handler, HTTP method)
ADMIN_ACTIONS = dict(
    overview=(overview, 'GET'),
    identity=(set_identity, 'POST'),
    issue_token=(issue_token, 'POST'),
    revoke_token=(revoke_token, 'POST'),
    add_peer=(add_peer, 'POST'),
    update_peer=(update_peer, 'POST'),
    delete_peer=(delete_peer, 'POST'),
    test_peer=(test_peer, 'POST'),
    run=(run, 'POST'),
    plan=(plan, 'GET'),
    resolve=(resolve, 'POST'),
    history=(history, 'GET'),
    task_update=(task_update, 'POST'),
    setup_list=(setup_list, 'GET'),
    setup_update=(setup_update, 'POST'),
    ssh_preview=(ssh_preview, 'POST'),
    ssh_append=(ssh_append, 'POST'),
)


def admin_api(app: Any, action: str) -> Any:
    """
    Dispatch an admin server-sync request.

    :param app: ARIApp
    :param action: str, action name from the URL

    :return: Flask response
    """
    user, err = _require(app)
    if err:
        return err
    entry = ADMIN_ACTIONS.get(action)
    if entry is None:
        return _fail('Unknown action', 404)
    handler, method = entry
    if request.method != method:
        return _fail('Method not allowed', 405)
    return handler(app, user)


# =============================================================================
# Define peer endpoint
# =============================================================================
def peer_api_view(app: Any, action: str) -> Any:
    """
    Serve a signed request from another ARI server.

    :param app: ARIApp
    :param action: str, hello / manifest / fetch / apply

    :return: Flask response (encrypted on success)
    """
    if action not in ('hello', 'manifest', 'fetch', 'apply'):
        return _fail('Unknown action', 404)
    request.max_content_length = PEER_MAX_BODY
    key_id = request.headers.get(crypto.HDR_KEY_ID, '')
    timestamp = request.headers.get(crypto.HDR_TIMESTAMP, '')
    nonce = request.headers.get(crypto.HDR_NONCE, '')
    signature = request.headers.get(crypto.HDR_SIGNATURE, '')
    caller = request.headers.get(crypto.HDR_SERVER_ID, '')[:64]
    issued = store.get_issued(key_id)
    # same message for every auth failure (no token enumeration)
    denied = _fail('Authentication failed', 401)
    if not issued or not nonce or len(nonce) > 64:
        return denied
    try:
        age = abs(time.time() - float(timestamp))
    except ValueError:
        return denied
    if age > engine.CLOCK_BLOCK:
        return _fail('Request expired: check both server clocks', 401)
    body = request.get_data(cache=False)
    secret = issued['secret']
    # accept the path with or without the application script root
    paths = {request.script_root + request.path, request.path}
    valid = any(crypto.verify_request(secret, 'POST', p, timestamp, nonce,
                                      body, signature) for p in paths)
    if not valid or not store.check_nonce(key_id, nonce):
        return denied
    try:
        envelope = crypto.decrypt_payload(secret, body)
    except ValueError:
        return denied
    if not isinstance(envelope, dict) or envelope.get('nonce') != nonce:
        return denied
    store.touch_issued(key_id, caller)
    reply = dict(nonce=nonce)
    try:
        handle_args = [action, envelope.get('payload'), issued['scope'],
                       caller]
        reply['payload'] = engine.handle_peer(*handle_args)
    except (PermissionError, ValueError) as exc:
        reply['error'] = str(exc)
    except Exception as exc:
        reply['error'] = f'{type(exc).__name__}: {exc}'
    blob = crypto.encrypt_payload(secret, reply)
    return Response(blob, mimetype='application/octet-stream')


# =============================================================================
# End of code
# =============================================================================
