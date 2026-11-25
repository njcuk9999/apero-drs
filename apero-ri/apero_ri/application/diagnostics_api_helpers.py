#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Admin grant management and read-only, explicitly scoped diagnostics API."""

import gzip
import json
from pathlib import Path
from typing import Any

from flask import Response, jsonify, render_template, request, session

from aperocore import drs_lang
from apero_ri.base import base
from apero_ri.core import audit_log, auth, diagnostic_tokens, diagnostics
from apero_ri.core import permissions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.application.diagnostics_api_helpers'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
PERMISSION = 'manage.admin.diagnostics'
PAGE_ID = 'home.admin_portal.diagnostics'

# =============================================================================
# Define functions
# =============================================================================
def _fail(code: str, status: int = 400) -> tuple[Any, int]:
    """Return a localized error without echoing credentials.

    :param code: Non-sensitive machine-readable error code.
    :param status: HTTP status.
    :return: JSON error and HTTP status.
    """
    message = drs_lang.textentry('ARI_DIAGNOSTICS_ERROR', args=[code])
    return jsonify(success=False, error=str(message), code=code), status


def _secure_transport() -> bool:
    """Accept HTTPS or an actual loopback connection with a loopback host.

    :return: Whether bearer credentials can be handled by this request.
    """
    import ipaddress

    if request.is_secure:
        return True
    try:
        local = ipaddress.ip_address(request.remote_addr or '').is_loopback
    except ValueError:
        local = False
    return local and request.host.split(':')[0] in ('localhost', '127.0.0.1')


def _perms(app: Any, user: dict) -> set:
    """Resolve current permissions for an administrator or grant issuer.

    :param app: ARI application.
    :param user: Current user record.
    :return: Current permission set.
    """
    return set(permissions.resolve_user_permissions(
        user.get('groups', []), app.ari_groups))


def _profiles(app: Any, user: dict) -> dict[tuple[str, str], dict]:
    """Resolve accessible profiles rather than trusting stored grant scopes.

    :param app: ARI application.
    :param user: Current administrator record.
    :return: Explicit instrument/profile pairs and their hydrated settings.
    """
    return {(row['instrument'], row['profile_id']): row['data']
            for row in auth.get_accessible_profiles(user, app.ari_groups)}


def admin_view(app: Any) -> Any:
    """Render the diagnostics admin page with its registered sidebar.

    :param app: ARI application.
    :return: Authorized page or permission error.
    """
    user = auth.get_effective_user(session)
    if not user or PERMISSION not in _perms(app, user):
        return _fail('forbidden', 403)
    definition = app.ari_pages[PAGE_ID]
    context = app._build_sidebar_context(PAGE_ID, _perms(app, user), user)
    context.update(page_id=PAGE_ID, page_label=definition['label'],
                   page_icon=definition['icon'], is_parent=False)
    return render_template('admin/diagnostics.html', **context)


def _report(app: Any, profiles: dict, user: dict, grant_id: str = '') -> Any:
    """Collect one selected profile, returning JSON or a compressed export.

    :param app: ARI application.
    :param profiles: Currently authorized instrument/profile mappings.
    :param user: Administrator or grant issuer.
    :param grant_id: Diagnostic grant ID for auditing; empty for a session.
    :return: Report response or validation error.
    """
    instrument = request.args.get('instrument', '')
    profile_id = request.args.get('profile_id', '')
    pair = (instrument, profile_id)
    if pair not in profiles:
        return _fail('profile_not_authorized', 403)
    if not all(diagnostics.IDENTIFIER.fullmatch(value.replace('-', '_'))
               for value in pair):
        return _fail('invalid_profile_identifier')
    options = dict(objname=request.args.get('objname', '').strip(),
                   pid=request.args.get('pid', '').strip(),
                   include_logs=request.args.get('logs') == '1',
                   include_database=request.args.get('database', '1') != '0')
    try:
        report = diagnostics.collect(
            profiles[pair], instrument, profile_id,
            Path(app._resolve_local_data_dir()), **options)
    except ValueError:
        return _fail('invalid_report_filter')
    audit_log.record(user['username'], 'diagnostics.report', profile_id,
                     dict(instrument=instrument, grant_id=grant_id,
                          filters=report['filters']))
    report['success'] = True
    if request.path.endswith('/export'):
        payload = gzip.compress(json.dumps(report, allow_nan=False).encode())
        response = Response(payload, mimetype='application/gzip')
        response.headers['Content-Disposition'] = (
            f'attachment; filename="diagnostics-{profile_id}.json.gz"')
    else:
        response = jsonify(report)
    response.headers['Cache-Control'] = 'no-store'
    return response


def admin_api(app: Any, action: str) -> Any:
    """Manage grants or collect reports using admin session authorization.

    :param app: ARI application.
    :param action: Fixed overview, issue, revoke, report, or export action.
    :return: Authorized response.
    """
    user = auth.get_effective_user(session)
    if not user or PERMISSION not in _perms(app, user):
        return _fail('forbidden', 403)
    profiles = _profiles(app, user)
    if action == 'overview' and request.method == 'GET':
        rows = [dict(instrument=pair[0], profile_id=pair[1])
                for pair in sorted(profiles)]
        response = jsonify(success=True, profiles=rows,
                            grants=diagnostic_tokens.list_grants(),
                            host=request.host_url.rstrip('/'))
        response.headers['Cache-Control'] = 'no-store'
        return response
    if action in ('report', 'export') and request.method == 'GET':
        return _report(app, profiles, user)
    body = request.get_json(silent=True)
    if request.method != 'POST' or not isinstance(body, dict):
        return _fail('invalid_request', 405)
    if action == 'issue':
        if not _secure_transport():
            return _fail('https_required', 403)
        selected = body.get('profiles')
        if not isinstance(selected, list):
            return _fail('invalid_profile_scope')
        for pair in selected:
            if (not isinstance(pair, list) or len(pair) != 2
                    or not all(isinstance(value, str) for value in pair)
                    or tuple(pair) not in profiles):
                return _fail('profile_not_authorized', 403)
        try:
            grant = diagnostic_tokens.issue(
                user['username'], selected, body.get('hours', 24),
                str(body.get('label', '')))
        except ValueError:
            return _fail('invalid_grant')
        audit_log.record(user['username'], 'diagnostics.issue', grant['id'],
                         dict(profiles=selected, expires=grant['expires_at']))
        response = jsonify(success=True, grant=grant)
        response.headers['Cache-Control'] = 'no-store'
        return response
    if action == 'revoke':
        grant_id = str(body.get('id', ''))
        found = diagnostic_tokens.revoke(grant_id)
        audit_log.record(user['username'], 'diagnostics.revoke', grant_id)
        return jsonify(success=found)
    return _fail('unknown_action', 404)


def api(app: Any, action: str) -> Any:
    """Serve only read-only diagnostic requests with short-lived grants.

    :param app: ARI application.
    :param action: Fixed profiles, report, or export action.
    :return: Scoped diagnostic response; never a proxy to management APIs.
    """
    if not _secure_transport():
        return _fail('https_required', 403)
    header = request.headers.get('Authorization', '')
    grant = diagnostic_tokens.validate(header[7:]) if header.startswith(
        'Bearer ') else None
    if grant is None:
        return _fail('invalid_or_expired_grant', 401)
    user = auth.load_users().get(grant['actor'])
    if not user or PERMISSION not in _perms(app, user):
        return _fail('issuer_no_longer_authorized', 403)
    user = dict(user, username=grant['actor'])
    current = _profiles(app, user)
    pairs = {tuple(pair) for pair in grant['profiles']}
    profiles = {pair: data for pair, data in current.items() if pair in pairs}
    if action == 'profiles':
        rows = [dict(instrument=pair[0], profile_id=pair[1])
                for pair in sorted(profiles)]
        audit_log.record(user['username'], 'diagnostics.profiles', grant['id'])
        response = jsonify(success=True, profiles=rows,
                            expires_at=grant['expires_at'], schema_version=1)
        response.headers['Cache-Control'] = 'no-store'
        return response
    if action in ('report', 'export'):
        return _report(app, profiles, user, grant['id'])
    return _fail('unknown_action', 404)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================