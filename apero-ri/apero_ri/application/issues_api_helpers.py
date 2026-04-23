#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Issues API helpers (Flask handlers).

Endpoints:
    GET  /api/issues/list
    POST /api/issues/create
    POST /api/issues/update

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

from pathlib import Path

from flask import jsonify, request

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
)
from apero_ri.core.issues import (
    create_issue,
    list_issues,
    update_issue,
)
from apero_ri.core.permissions import resolve_user_permissions


__NAME__ = 'apero_ri.application.issues_api_helpers'


def _data_dir(app) -> Path:
    """Return the ARI data directory as a Path."""
    return Path(app.args.data_dir or str(Path.home() / '.ari'))


def _is_monitor_perm(p) -> bool:
    if not isinstance(p, str):
        return False
    if p in ('view.monitor_portal', 'view.monitor'):
        return True
    if p.startswith('monitor.'):
        return True
    if p.startswith('view.monitor_portal.'):
        return True
    if p.startswith('view.monitor.'):
        return True
    return False


def _user_visibility(perms) -> str:
    """Map a permission set to an issues visibility level.

    :param perms: set/list of permissions
    :return: 'admin', 'monitor', or 'public'
    """
    pset = set(perms or ())
    if 'manage.astrometrics' in pset:
        return 'admin'
    for p in pset:
        if _is_monitor_perm(p):
            return 'monitor'
    return 'public'


def api_issues_list(app):
    """List issues visible to the current caller."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()
    if 'view.data_portal' not in perms:
        return jsonify(success=False,
                       error='Unauthorized'), 401
    visibility = _user_visibility(perms)
    status = (request.args.get('status') or '').strip() or None
    instrument = (request.args.get('instrument') or '').strip(
    ) or None
    kind = (request.args.get('kind') or '').strip() or None
    issues = list_issues(
        _data_dir(app), visibility=visibility,
        status=status, instrument=instrument, kind=kind)
    return jsonify(success=True, issues=issues,
                   visibility=visibility)


def api_issues_create(app):
    """Create a new issue (flag / target_request / other).

    JSON body:
        kind        (required): 'flag' | 'target_request' | 'other'
        reason      (required): description
        apero_name  (optional)
        field       (optional)
        value       (optional)
        instrument  (optional)
        profile_id  (optional)
        visibility  (optional): 'public' (default) | 'monitor' | 'admin'
    """
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()
    if 'view.data_portal' not in perms:
        return jsonify(success=False,
                       error='Unauthorized'), 401
    body = request.get_json(silent=True) or {}
    kind = (body.get('kind') or '').strip()
    if kind not in ('flag', 'target_request', 'other'):
        return jsonify(success=False,
                       error="Invalid 'kind'"), 400
    reason = (body.get('reason') or '').strip()
    if not reason:
        return jsonify(success=False,
                       error="Missing 'reason'"), 400
    visibility = (body.get('visibility')
                  or 'public').strip()
    if visibility not in ('public', 'monitor', 'admin'):
        visibility = 'public'
    user_vis = _user_visibility(perms)
    rank = {'public': 0, 'monitor': 1, 'admin': 2}
    if rank[visibility] > rank[user_vis]:
        visibility = user_vis
    username = (user_info.get('username') if user_info
                else None) or 'anonymous'
    issue = create_issue(
        _data_dir(app),
        kind=kind, reason=reason, created_by=username,
        apero_name=body.get('apero_name'),
        field=body.get('field'),
        value=body.get('value'),
        instrument=body.get('instrument'),
        profile_id=body.get('profile_id'),
        visibility=visibility,
    )
    return jsonify(success=True, issue=issue)


def api_issues_update(app):
    """Update an issue's status or append a note (monitor+ only).

    JSON body:
        id      (required, int)
        status  (optional): 'open' | 'resolved' | 'invalid'
        note    (optional): free-form text to append
    """
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False,
                       error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups)
    pset = set(perms or ())
    has_monitor = ('manage.astrometrics' in pset
                   or any(_is_monitor_perm(p) for p in pset))
    if not has_monitor:
        return jsonify(success=False,
                       error='Monitor access required'), 403
    body = request.get_json(silent=True) or {}
    try:
        issue_id = int(body.get('id'))
    except (TypeError, ValueError):
        return jsonify(success=False,
                       error="Invalid 'id'"), 400
    status = body.get('status')
    note = body.get('note')
    if not status and not note:
        return jsonify(success=False,
                       error='Nothing to update'), 400
    issue = update_issue(
        _data_dir(app), issue_id,
        status=status, note=note,
        author=user_info.get('username'))
    if not issue:
        return jsonify(success=False,
                       error='Issue not found'), 404
    return jsonify(success=True, issue=issue)
