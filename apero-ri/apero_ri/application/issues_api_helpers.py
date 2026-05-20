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
    load_users,
)
from apero_ri.core.issues import (
    create_issue,
    delete_issue,
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
    type_ = (request.args.get('type') or '').strip() or None
    created_by = (request.args.get('created_by') or '').strip(
    ) or None
    assigned_to = (request.args.get('assigned_to') or '').strip(
    ) or None
    label = (request.args.get('label') or '').strip() or None
    issues = list_issues(
        _data_dir(app), visibility=visibility,
        status=status, instrument=instrument, kind=kind,
        type_=type_, created_by=created_by,
        assigned_to=assigned_to, label=label)
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
    if kind not in ('astrometric', 'flag', 'target_request',
                    'ari', 'other'):
        return jsonify(success=False,
                       error="Invalid 'kind'"), 400
    reason = (body.get('reason') or '').strip()
    if not reason:
        # allow an empty reason if a title is given (e.g. simple
        # "new object" requests where the title is self-explanatory)
        title_str = (body.get('title') or '').strip()
        if title_str:
            reason = title_str
        else:
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
        title=body.get('title'),
        type_=body.get('type'),
        origin_url=body.get('origin_url'),
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
    assigned_to = body.get('assigned_to')
    if (status is None and not note
            and assigned_to is None):
        return jsonify(success=False,
                       error='Nothing to update'), 400
    issue = update_issue(
        _data_dir(app), issue_id,
        status=status, note=note,
        author=user_info.get('username'),
        assigned_to=assigned_to)
    if not issue:
        return jsonify(success=False,
                       error='Issue not found'), 404
    return jsonify(success=True, issue=issue)


def api_issues_users(app):
    """List users that an issue can be assigned to.

    Returns the set of users whose resolved permissions grant
    at least monitor-level visibility (i.e. anyone who can act on
    issues). Optional ``?instrument=`` arg further restricts to
    monitors of a specific instrument.
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
    instrument = (request.args.get('instrument') or '').strip()
    inst_upper = instrument.upper() if instrument else ''
    out = []
    for username, udata in load_users().items():
        if not isinstance(udata, dict):
            continue
        groups = udata.get('groups') or []
        try:
            uperms = resolve_user_permissions(
                groups, app.ari_groups)
        except Exception:
            continue
        upset = set(uperms or ())
        is_admin = 'manage.astrometrics' in upset
        is_monitor = any(_is_monitor_perm(p) for p in upset)
        if not (is_admin or is_monitor):
            continue
        if inst_upper:
            # require either a global monitor perm or one
            # scoped to this instrument
            ok = is_admin
            if not ok:
                for p in upset:
                    if not _is_monitor_perm(p):
                        continue
                    if '.' not in p:
                        ok = True
                        break
                    suffix = p.rsplit('.', 1)[-1].upper()
                    if suffix in ('MONITOR', 'MONITOR_PORTAL'):
                        ok = True
                        break
                    if suffix == inst_upper:
                        ok = True
                        break
            if not ok:
                continue
        out.append({
            'username': username,
            'level': 'admin' if is_admin else 'monitor',
        })
    out.sort(key=lambda u: u['username'].lower())
    return jsonify(success=True, users=out)


def _is_admin_or_super(perms) -> bool:
    """True if the caller can fully edit/delete issues."""
    pset = set(perms or ())
    if 'manage.astrometrics' in pset:
        return True
    for p in pset:
        if p == 'super_admin' or p.startswith('manage.group.super_admin'):
            return True
        if p == 'admin' or p.startswith('manage.group.admin'):
            return True
        if p.startswith('manage.instrument.') and (
                p.endswith('.super_admin') or p.endswith('.admin')):
            return True
    return False


def api_issues_delete(app):
    """Hard-delete an issue. Admin / super-admin only.

    JSON body: {"id": <int>}
    """
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups)
    if not _is_admin_or_super(perms):
        return jsonify(
            success=False,
            error='Admin / super-admin access required'), 403
    body = request.get_json(silent=True) or {}
    try:
        issue_id = int(body.get('id'))
    except (TypeError, ValueError):
        return jsonify(success=False, error="Invalid 'id'"), 400
    deleted = delete_issue(_data_dir(app), issue_id)
    if not deleted:
        return jsonify(success=False, error='Issue not found'), 404
    return jsonify(success=True, deleted=deleted)


def api_issues_edit(app):
    """Edit core fields of an issue. Admin / super-admin only.

    Unlike :func:`api_issues_update` (which monitors can use to set
    status / append notes), this endpoint can rewrite the title,
    body (reason), kind, type, label, action and visibility — used
    to clean up tests or correct mistaken filings.

    JSON body keys (all optional except ``id``):
        id, title, reason, kind, type, label, action, visibility
    """
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups)
    if not _is_admin_or_super(perms):
        return jsonify(
            success=False,
            error='Admin / super-admin access required'), 403
    body = request.get_json(silent=True) or {}
    try:
        issue_id = int(body.get('id'))
    except (TypeError, ValueError):
        return jsonify(success=False, error="Invalid 'id'"), 400
    # Direct file mutation: load, patch, save (mirrors update_issue
    # but for fields the monitor endpoint doesn't expose).
    from apero_ri.core import issues as _issues
    with _issues._LOCK:
        all_issues = _issues._load(_data_dir(app))
        target = None
        for it in all_issues:
            if it.get('id') == issue_id:
                target = it
                break
        if target is None:
            return jsonify(success=False, error='Not found'), 404
        for key in ('title', 'reason', 'kind', 'type',
                    'label', 'action', 'visibility'):
            if key in body and body[key] is not None:
                target[key] = str(body[key])
        # apero_name + field + value editable too (correct typos)
        for key in ('apero_name', 'field', 'value'):
            if key in body:
                target[key] = body[key]
        _issues._save(_data_dir(app), all_issues)
    return jsonify(success=True, issue=target)


def create_issue_internal(
    kind: str,
    title: str = '',
    body: str = '',
    created_by: str = 'system',
    meta=None,
):
    """Programmatic issue creation (used by the message flag flow).

    Returns the created issue's ``id`` as a string, or ``None`` on
    failure. Reads ``ARI_DIR`` from the environment because there is
    no ``app`` context here.
    """
    try:
        from pathlib import Path as _P
        data_dir = _P.home() / '.ari'
        meta = meta or {}
        issue_kind = str(kind or 'message')
        issue_type = str(meta.get('type') or 'reported message')
        issue = create_issue(
            data_dir,
            kind=issue_kind,
            reason=str(body or ''),
            created_by=str(created_by or 'system'),
            title=str(title or '')[:200] or None,
            type_=issue_type,
            origin_url=str(meta.get('origin_url') or '') or None,
            label='reported-message',
            visibility='monitor',
        )
        return str(issue.get('id')) if issue else None
    except Exception:  # noqa: BLE001
        return None
