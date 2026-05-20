#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Known errors API helpers."""

from __future__ import annotations

from flask import jsonify, request

from apero_ri.core.auth import get_public_permissions
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.core import known_errors as ke


def _is_monitor_perm(p) -> bool:
    if not isinstance(p, str):
        return False
    if p in ('view.monitor_portal', 'view.monitor', 'manage.astrometrics'):
        return True
    if p.startswith('monitor.'):
        return True
    if p.startswith('view.monitor_portal.'):
        return True
    if p.startswith('view.monitor.'):
        return True
    return False


def _require_monitor(app):
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info.get('groups', []), app.ari_groups
        )
    else:
        perms = get_public_permissions()

    has_monitor = any(_is_monitor_perm(p) for p in set(perms or ()))
    if not has_monitor:
        return None, None, jsonify(success=False, error='Monitor access required'), 403
    return user_info, perms, None, None


def api_known_errors_list(app):
    return jsonify(success=True, rows=ke.list_known_errors())


def api_known_errors_create(app):
    user_info, _, err, status = _require_monitor(app)
    if err is not None:
        return err, status

    body = request.get_json(silent=True) or {}
    generic_error = str(body.get('generic_error') or '').strip()
    if not generic_error:
        return jsonify(success=False, error='generic_error is required'), 400

    payload = {
        'date_reported': body.get('date_reported'),
        'reported_by': body.get('reported_by')
        or (user_info.get('username') if user_info else ''),
        'instrument_mode': body.get('instrument_mode'),
        'recipe': body.get('recipe'),
        'action': body.get('action'),
        'type': body.get('type'),
        'error_code': body.get('error_code'),
        'github_issue': body.get('github_issue'),
        'generic_error': body.get('generic_error'),
        'comments': body.get('comments'),
        'full_example_error': body.get('full_example_error'),
    }
    row = ke.create_known_error(payload)
    return jsonify(success=True, row=row)


def api_known_errors_update(app):
    _, _, err, status = _require_monitor(app)
    if err is not None:
        return err, status

    body = request.get_json(silent=True) or {}
    error_id = str(body.get('id') or '').strip()
    if not error_id:
        return jsonify(success=False, error='id is required'), 400

    payload = {
        'date_reported': body.get('date_reported'),
        'reported_by': body.get('reported_by'),
        'instrument_mode': body.get('instrument_mode'),
        'recipe': body.get('recipe'),
        'action': body.get('action'),
        'type': body.get('type'),
        'error_code': body.get('error_code'),
        'github_issue': body.get('github_issue'),
        'generic_error': body.get('generic_error'),
        'comments': body.get('comments'),
        'full_example_error': body.get('full_example_error'),
    }
    row = ke.update_known_error(error_id, payload)
    if row is None:
        return jsonify(success=False, error='Known error not found'), 404
    return jsonify(success=True, row=row)


def api_known_errors_delete(app):
    _, _, err, status = _require_monitor(app)
    if err is not None:
        return err, status

    body = request.get_json(silent=True) or {}
    error_id = str(body.get('id') or '').strip()
    if not error_id:
        return jsonify(success=False, error='id is required'), 400

    ok = ke.delete_known_error(error_id)
    if not ok:
        return jsonify(success=False, error='Known error not found'), 404
    return jsonify(success=True)
