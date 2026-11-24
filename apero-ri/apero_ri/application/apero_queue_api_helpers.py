#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - APERO queue setup (admin) and dashboard proxy (monitor).

Admins define how ARI reaches each ``apero_queue.py gui`` dashboard (SSH
local forward + linked APERO profile) on the "APERO Queue Setup" page.
Monitors see one tab per queue whose linked profile they can access; each
tab embeds the queue dashboard through ``proxy_view``, which forwards the
dashboard requests to the tunnel after checking access. Actions listed in
a definition's ``blocked_actions`` are refused for non-admin users.

Created on 2026-10-28

@author: cook
"""
from __future__ import annotations

import html as html_mod
import re
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple

import yaml
from flask import Response, jsonify, request, session

from aperocore.drs_lang import textentry
from apero_ri.application import monitor_view_helpers as mvh
from apero_ri.core import apero_queues
from apero_ri.core import auth
from apero_ri.core import permissions
from apero_ri.core import sshfs_interactive
from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.application.apero_queue_api_helpers'
# permission required for the setup page (and unrestricted dashboard use)
PERMISSION = 'manage.admin.apero_queue_setup'
# dashboard paths that may be proxied (page + json api only)
PROXY_PATH = re.compile(r'^(|index\.html|api/[a-z_]+)$')
# proxied request timeout (seconds) - dashboard actions start in background
PROXY_TIMEOUT = 60
# quick probe timeout (seconds) for the setup page health column
PROBE_TIMEOUT = 2
# worker restart request timeout (seconds)
RESTART_TIMEOUT = 10
# never route localhost requests through http(s)_proxy environment settings
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler(dict()))
# one reconnect at a time per queue across startup and monitor requests
_RECONNECT_LOCKS: Dict[str, threading.Lock] = dict()


# =============================================================================
# Define permission helpers
# =============================================================================
def _user_perms(app: Any) -> Tuple[Optional[dict], set]:
    """Return the effective user and their permissions."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return None, set()
    perms = permissions.resolve_user_permissions(user_info['groups'],
                                                 app.ari_groups)
    return user_info, set(perms)


def _require_admin(app: Any) -> Tuple[Optional[dict], Any]:
    """Require the APERO queue setup permission."""
    user_info, perms = _user_perms(app)
    if not user_info:
        return None, (jsonify(success=False, error='Login required'), 401)
    if PERMISSION not in perms:
        return None, (jsonify(success=False, error='Forbidden'), 403)
    return user_info, None


def _body() -> Dict[str, Any]:
    """Return the JSON request body as a dict."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else dict()


def _fail(message: str, status: int = 400) -> Tuple[Any, int]:
    """Return a JSON error response."""
    return jsonify(success=False, error=str(message)), status


def _accessible_profile_keys(app: Any, user_info: dict,
                             perms: set) -> set:
    """Return the (instrument, profile_id) pairs a monitor can access."""
    cards, _, _ = mvh._accessible_profile_cards(app, user_info, perms)
    return {(card['instrument'], card['profile_id']) for card in cards}


def accessible_queues(app: Any, user_info: Optional[dict],
                      perms: set) -> Dict[str, dict]:
    """
    Return the queue definitions the user may open.

    Admins with the setup permission see every enabled queue; monitors
    see enabled queues linked to an APERO profile they can access.

    :param app: ARIApp
    :param user_info: dict or None, the effective user
    :param perms: set, the user's permissions

    :return: dict, definition name -> definition
    """
    if not user_info:
        return dict()
    queues = {name: qdef for name, qdef in apero_queues.load_queues().items()
              if qdef['enabled']}
    if PERMISSION in perms:
        return queues
    if not mvh._has_any_monitor_perm(perms):
        return dict()
    allowed = _accessible_profile_keys(app, user_info, perms)
    return {name: qdef for name, qdef in queues.items()
            if (qdef['instrument'], qdef['profile_id']) in allowed}


# =============================================================================
# Define status helpers
# =============================================================================
def _tunnel_params(app: Any, qdef: dict) -> dict:
    """Return apero_async tunnel parameters for one definition."""
    return apero_queues.tunnel_params(qdef, app._resolve_local_data_dir())


def _probe_gui_detail(local_port: str) -> Tuple[bool, str]:
    """Probe the queue dashboard and retain the useful failure reason.

    :param local_port: Local SSH-forward port.
    :return: Whether ``/api/state`` returned 200 plus an error detail.
    """
    url = 'http://127.0.0.1:{0}/api/state'.format(local_port)
    try:
        with _OPENER.open(url, timeout=PROBE_TIMEOUT) as resp:
            if resp.status == 200:
                return True, ''
            message = textentry(
                'APERO_QUEUE_GUI_HTTP_ERROR', args=[resp.status]
            )
            return False, str(message)
    except urllib.error.HTTPError as exc:
        message = textentry('APERO_QUEUE_GUI_HTTP_ERROR', args=[exc.code])
        return False, str(message)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        message = textentry('APERO_QUEUE_GUI_PROBE_ERROR', args=[str(exc)])
        return False, str(message)


def _probe_gui(local_port: str) -> bool:
    """Return True when the queue dashboard answers on the local port."""
    return _probe_gui_detail(local_port)[0]


def queue_status(app: Any, qdef: dict) -> Dict[str, Any]:
    """
    Return tunnel and dashboard health for one definition.

    :param app: ARIApp
    :param qdef: dict, the normalized definition

    :return: dict, status flags (see apero_async.get_db_tunnel_status)
    """
    try:
        status = apero_async.get_db_tunnel_status(_tunnel_params(app, qdef))
    except Exception as exc:
        return dict(active=False, gui_alive=False, error=str(exc))
    if status.get('local_port_open'):
        gui_alive, gui_error = _probe_gui_detail(qdef['local_port'])
    else:
        gui_alive = False
        gui_error = ''
    status['gui_alive'] = gui_alive
    status['gui_error'] = gui_error
    return status


def restore_tunnels(app: Any) -> None:
    """Attempt to restore enabled queue tunnels once at server startup.

    :param app: ARIApp supplying the data directory and logger.
    :return: None.
    """
    try:
        queues = apero_queues.load_queues()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        message = textentry('APERO_QUEUE_STARTUP_LOAD_FAILED', args=[str(exc)])
        app.logger.warning(str(message))
        return

    for name, qdef in queues.items():
        if not qdef['enabled']:
            continue
        lock = _RECONNECT_LOCKS.setdefault(name, threading.Lock())
        if not lock.acquire(blocking=False):
            continue
        try:
            params = _tunnel_params(app, qdef)
            status = apero_async.get_db_tunnel_status(params)
            if not status['local_port_open']:
                apero_async._ensure_ssh_tunnel(params)
        except (OSError, RuntimeError, ValueError) as exc:
            message = textentry('APERO_QUEUE_STARTUP_TUNNEL_FAILED',
                                args=[name, str(exc)])
            app.logger.warning(str(message))
        finally:
            lock.release()


def _profile_options() -> List[Dict[str, str]]:
    """Return every configured APERO profile for the link dropdown."""
    profiles = auth.load_apero_profiles(hydrate=False)
    options = []
    for instrument in sorted(profiles or dict()):
        inst_profiles = profiles.get(instrument)
        if not isinstance(inst_profiles, dict):
            continue
        for profile_id in sorted(inst_profiles):
            options.append(dict(instrument=str(instrument),
                                profile_id=str(profile_id)))
    return options


# =============================================================================
# Define admin views
# =============================================================================
def list_queues(app: Any, user: dict) -> Any:
    """List every definition with live status."""
    _ = user
    rows = []
    for name, qdef in sorted(apero_queues.load_queues().items()):
        rows.append(dict(name=name, definition=qdef,
                         status=queue_status(app, qdef)))
    actions = [dict(key=key, label=value[0])
               for key, value in apero_queues.QUEUE_ACTIONS.items()]
    return jsonify(success=True, queues=rows, actions=actions,
                   default_blocked=apero_queues.DEFAULT_BLOCKED_ACTIONS,
                   profiles=_profile_options(),
                   ssh_hosts=app._list_ssh_config_hosts())


def save_queue(app: Any, user: dict) -> Any:
    """Create or update one definition."""
    _ = user
    body = _body()
    queues = apero_queues.load_queues()
    qdef = apero_queues.normalize_queue(body)
    previous_name = str(body.get('previous_name', '') or '').strip()
    profile_named = bool(body.get('profile_name'))
    if profile_named:
        name = apero_queues.profile_queue_name(
            qdef['instrument'], qdef['profile_id'])
        qdef['label'] = qdef['profile_id']
    else:
        name = str(body.get('name', '') or '').strip()
    if previous_name and previous_name not in queues:
        return _fail('Queue being edited no longer exists', 404)
    if name in queues and name != previous_name:
        return _fail('A queue with this APERO profile name already exists')
    checked_queues = dict(queues)
    checked_queues.pop(previous_name, None)
    error = apero_queues.validate_queue(name, qdef, checked_queues)
    if error:
        return _fail(error)
    if previous_name and previous_name != name:
        old_qdef = queues.pop(previous_name)
        apero_async.close_db_tunnel(_tunnel_params(app, old_qdef))
    queues[name] = qdef
    apero_queues.save_queues(queues)
    return jsonify(success=True, name=name)


def _named_queue(body: Dict[str, Any]) -> Tuple[str, Optional[dict]]:
    """Return the requested definition name and definition."""
    name = str(body.get('name', '') or '').strip()
    return name, apero_queues.load_queues().get(name)


def delete_queue(app: Any, user: dict) -> Any:
    """Delete one definition (closing its tunnel first)."""
    _ = user
    name, qdef = _named_queue(_body())
    if qdef is None:
        return _fail('Queue not found', 404)
    apero_async.close_db_tunnel(_tunnel_params(app, qdef))
    queues = apero_queues.load_queues()
    queues.pop(name, None)
    apero_queues.save_queues(queues)
    return jsonify(success=True)


def ensure_tunnel(app: Any, user: dict) -> Any:
    """Start (non-interactively) or verify one queue tunnel."""
    _ = user
    _, qdef = _named_queue(_body())
    if qdef is None:
        return _fail('Queue not found', 404)
    try:
        apero_async._ensure_ssh_tunnel(_tunnel_params(app, qdef))
    except Exception as exc:
        return _fail('Failed to start queue tunnel: {0}'.format(exc), 500)
    status = queue_status(app, qdef)
    if status.get('gui_alive'):
        message = 'Tunnel active and the queue dashboard is answering.'
    else:
        message = ('Tunnel active but the queue dashboard is not answering '
                   '- is "apero_queue.py gui --port {0}" running on the '
                   'remote host?'.format(qdef['remote_port']))
    return jsonify(success=True, message=message, status=status)


def close_tunnel(app: Any, user: dict) -> Any:
    """Close one queue tunnel."""
    _ = user
    _, qdef = _named_queue(_body())
    if qdef is None:
        return _fail('Queue not found', 404)
    result = apero_async.close_db_tunnel(_tunnel_params(app, qdef))
    if not result.get('ok'):
        return _fail(result.get('error', 'Failed to close tunnel'), 500)
    return jsonify(success=True, message='Queue tunnel closed.')


def retry_dashboard(app: Any, user: dict) -> Any:
    """Ask the queue supervisor to replace an unresponsive GUI worker.

    The public queue server remains reachable on the remote loopback port
    when its worker dies. Its ``/api/shutdown`` endpoint restarts only that
    worker, leaving the SSH tunnel and active queue task process unchanged.

    :param app: ARI application.
    :param user: Authenticated admin user.
    :return: Flask JSON response.
    """
    _ = user
    _, qdef = _named_queue(_body())
    if qdef is None:
        return _fail('Queue not found', 404)
    status = queue_status(app, qdef)
    if not status.get('local_port_open'):
        return _fail(str(textentry('APERO_QUEUE_TUNNEL_REQUIRED')))
    if status.get('gui_alive'):
        message = str(textentry('APERO_QUEUE_GUI_ALREADY_ALIVE'))
        return jsonify(
            success=True,
            message=message,
            status=status,
        )

    url = 'http://127.0.0.1:{0}/api/shutdown'.format(qdef['local_port'])
    payload = b'{"restart":true}'
    proxied = urllib.request.Request(
        url,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with _OPENER.open(proxied, timeout=RESTART_TIMEOUT) as resp:
            body = resp.read()
            response_status = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read()
        response_status = exc.code
    except (urllib.error.URLError, OSError, ValueError) as exc:
        message = textentry(
            'APERO_QUEUE_GUI_SUPERVISOR_ERROR', args=[str(exc)]
        )
        return _fail(str(message), 502)
    if not 200 <= response_status < 300:
        detail = body.decode('utf-8', errors='replace').strip()
        message = textentry(
            'APERO_QUEUE_GUI_RESTART_REJECTED',
            args=[response_status, detail or 'no response body'],
        )
        return _fail(str(message), 502)
    return jsonify(
        success=True,
        message=str(textentry('APERO_QUEUE_GUI_RESTART_REQUESTED')),
    )


def auth_start(app: Any, user: dict) -> Any:
    """Start an interactive (PTY) SSH tunnel for password/2FA prompts."""
    _ = user
    _, qdef = _named_queue(_body())
    if qdef is None:
        return _fail('Queue not found', 404)
    result = sshfs_interactive.start_interactive_ssh_tunnel(
        ssh_config_host=qdef['ssh_config_host'],
        local_port=int(qdef['local_port']),
        remote_host=qdef['remote_host'],
        remote_port=int(qdef['remote_port']),
        local_data_dir=str(app._resolve_local_data_dir()),
        simple_ssh=qdef['ssh_mode'] == 'simple',
        state_subdir=apero_queues.TUNNEL_STATE_SUBDIR,
    )
    return jsonify(**result)


def _token() -> str:
    """Return the interactive session token from the request body."""
    return str(_body().get('token', '') or '').strip()


def auth_poll(app: Any, user: dict) -> Any:
    """Poll output from an interactive tunnel session."""
    _ = app, user
    return jsonify(**sshfs_interactive.poll_session(_token()))


def auth_send(app: Any, user: dict) -> Any:
    """Send input to an interactive tunnel session."""
    _ = app, user
    body = _body()
    token = str(body.get('token', '') or '').strip()
    return jsonify(**sshfs_interactive.send_input(
        token, str(body.get('data', ''))))


def auth_close(app: Any, user: dict) -> Any:
    """Close an interactive tunnel session."""
    _ = app, user
    return jsonify(**sshfs_interactive.close_session(_token()))


ADMIN_ACTIONS = dict(
    list=(list_queues, 'GET'),
    save=(save_queue, 'POST'),
    delete=(delete_queue, 'POST'),
    ensure=(ensure_tunnel, 'POST'),
    close=(close_tunnel, 'POST'),
    retry_dashboard=(retry_dashboard, 'POST'),
    auth_start=(auth_start, 'POST'),
    auth_poll=(auth_poll, 'POST'),
    auth_send=(auth_send, 'POST'),
    auth_close=(auth_close, 'POST'),
)


def admin_api(app: Any, action: str) -> Any:
    """
    Dispatch an admin APERO queue setup request.

    :param app: ARIApp
    :param action: str, action name from the URL

    :return: Flask response
    """
    user, err = _require_admin(app)
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
# Define monitor page context and proxy
# =============================================================================
def build_monitor_context(app: Any, user_info: Optional[dict],
                          perms: set) -> Dict[str, Any]:
    """
    Build the monitor APERO queue page context (one tab per queue).

    :param app: ARIApp
    :param user_info: dict or None, the effective user
    :param perms: set, the user's permissions

    :return: dict, template context
    """
    tabs = []
    queues = accessible_queues(app, user_info, set(perms or set()))
    for name, qdef in sorted(queues.items()):
        tabs.append(dict(
            name=name,
            label=qdef['profile_id'] or name,
            instrument=qdef['instrument'],
            profile_id=qdef['profile_id'],
            proxy_url='/monitor_portal/apero_queue/{0}/proxy/'.format(name),
        ))
    return dict(apero_queue_tabs=tabs,
                apero_queue_can_setup=PERMISSION in set(perms or set()))


def _monitor_state(app: Any, qdef: dict) -> Dict[str, Any]:
    """Return the minimal health flags monitors are allowed to see."""
    status = queue_status(app, qdef)
    return dict(alive=bool(status.get('gui_alive')),
                tunnel=bool(status.get('local_port_open')))


def monitor_status(app: Any) -> Any:
    """
    Report whether each queue the user can open is reachable.

    :param app: ARIApp

    :return: Flask response, dict(success, queues=name -> flags)
    """
    user_info, perms = _user_perms(app)
    if not user_info:
        return _fail('Login required', 401)
    queues = accessible_queues(app, user_info, perms)
    if not queues:
        return jsonify(success=True, queues=dict())
    # each probe can take PROBE_TIMEOUT seconds, so check queues in parallel
    workers = min(8, len(queues))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {name: pool.submit(_monitor_state, app, qdef)
                   for name, qdef in queues.items()}
        states = {name: future.result() for name, future in futures.items()}
    return jsonify(success=True, queues=states)


def monitor_reconnect(app: Any, name: str) -> Any:
    """
    Start/verify one queue tunnel for any user who can open the queue.

    Only non-interactive SSH is attempted; tunnels needing password or
    Duo prompts still need an admin (Interactive Auth on the setup page).

    :param app: ARIApp
    :param name: str, the queue definition name

    :return: Flask response, dict(success, alive, message)
    """
    user_info, perms = _user_perms(app)
    if not user_info:
        return _fail('Login required', 401)
    # json-only posts cannot be forged by cross-site html forms
    if not request.is_json:
        return _fail('JSON body required', 415)
    qdef = accessible_queues(app, user_info, perms).get(name)
    if qdef is None:
        return _fail('Not found', 404)
    lock = _RECONNECT_LOCKS.setdefault(name, threading.Lock())
    if not lock.acquire(blocking=False):
        return _fail('A reconnect is already in progress', 409)
    try:
        if _monitor_state(app, qdef)['alive']:
            return jsonify(success=True, alive=True,
                           message='Queue dashboard is already reachable.')
        try:
            apero_async._ensure_ssh_tunnel(_tunnel_params(app, qdef))
        except Exception as exc:
            msg = ('Could not start the tunnel ({0}). If it needs a '
                   'password or Duo prompt, ask an admin to use '
                   'Interactive Auth on the APERO Queue Setup page.')
            return _fail(msg.format(exc), 502)
        alive = _monitor_state(app, qdef)['alive']
        if alive:
            message = 'Tunnel active and the queue dashboard is answering.'
        else:
            message = ('Tunnel active but the queue dashboard is not '
                       'answering - apero_queue.py gui may not be running.')
        return jsonify(success=True, alive=alive, message=message)
    finally:
        lock.release()


def _offline_page(qdef: dict, error: str) -> Response:
    """Return a small themed page shown when the dashboard is unreachable."""
    message = (
        '<!DOCTYPE html><html><body style="font-family:sans-serif;'
        'background:#0d1117;color:#c9d1d9;padding:24px">'
        '<h2>APERO queue dashboard unreachable</h2>'
        '<p>ARI could not reach the queue dashboard for profile '
        '<code>{0} / {1}</code>.</p><p>Either the SSH tunnel is down or '
        '<code>apero_queue.py gui --port {2}</code> is not running on the '
        'remote host. An admin can (re)start the tunnel on the APERO Queue '
        'Setup page.</p><p style="color:#8b949e">{3}</p></body></html>'
    )
    escape = html_mod.escape
    html = message.format(escape(qdef['instrument']),
                          escape(qdef['profile_id']),
                          escape(qdef['remote_port']), escape(error))
    return Response(html, status=502, content_type='text/html')


def _hide_blocked(body: bytes, blocked: List[str]) -> bytes:
    """Inject css hiding blocked controls into the dashboard page."""
    selectors = apero_queues.hidden_selectors(blocked)
    if not selectors:
        return body
    style = '<style>{0} {{ display: none !important; }}</style></head>'
    style = style.format(', '.join(selectors))
    return body.replace(b'</head>', style.encode('utf-8'), 1)


def proxy_view(app: Any, name: str, subpath: str = '') -> Any:
    """
    Forward one queue dashboard request through the queue's SSH tunnel.

    :param app: ARIApp
    :param name: str, the queue definition name
    :param subpath: str, the dashboard path ('' / 'index.html' / 'api/...')

    :return: Flask response
    """
    user_info, perms = _user_perms(app)
    if not user_info:
        return _fail('Login required', 401)
    qdef = accessible_queues(app, user_info, perms).get(name)
    if qdef is None or not PROXY_PATH.match(subpath or ''):
        return _fail('Not found', 404)
    is_admin = PERMISSION in perms
    blocked = [] if is_admin else (list(qdef['blocked_actions'])
                                   + list(apero_queues.ADMIN_ONLY_ACTIONS))
    data = None
    headers = dict()
    if request.method == 'POST':
        # json-only posts cannot be forged by cross-site html forms
        if not request.is_json:
            return _fail('JSON body required', 415)
        action = subpath[len('api/'):] if subpath.startswith('api/') else ''
        if action in blocked:
            msg = 'The "{0}" action is disabled for monitors on this queue.'
            return jsonify(error=msg.format(action),
                           message=msg.format(action)), 403
        data = request.get_data()
        headers['Content-Type'] = 'application/json'
    url = 'http://127.0.0.1:{0}/{1}'.format(qdef['local_port'], subpath)
    query = request.query_string.decode('utf-8', errors='replace')
    if query:
        url += '?' + query
    proxied = urllib.request.Request(url, data=data, headers=headers,
                                     method=request.method)
    try:
        with _OPENER.open(proxied, timeout=PROXY_TIMEOUT) as resp:
            body, status = resp.read(), resp.status
            ctype = resp.headers.get('Content-Type', 'application/json')
    except urllib.error.HTTPError as exc:
        body, status = exc.read(), exc.code
        ctype = exc.headers.get('Content-Type', 'application/json')
    except (urllib.error.URLError, OSError) as exc:
        if subpath in ('', 'index.html'):
            return _offline_page(qdef, str(exc))
        emsg = 'Queue dashboard unreachable: {0}'.format(exc)
        return jsonify(error=emsg), 502
    if ctype.startswith('text/html'):
        body = _hide_blocked(body, blocked)
    response = Response(body, status=status, content_type=ctype)
    response.headers['Cache-Control'] = 'no-store'
    return response


# =============================================================================
# End of code
# =============================================================================
