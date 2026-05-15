#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI APERO-check API helpers."""

from __future__ import annotations

from pathlib import Path

from flask import jsonify, request

from apero_ri.application.issues_api_helpers import _data_dir
from apero_ri.application.monitor_view_helpers import _has_any_monitor_perm
from apero_ri.core import apero_checks as checks_core
from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
)
from apero_ri.core.issues import create_issue
from apero_ri.core.permissions import resolve_user_permissions


def _api_user(app):
    """Return the current API user and permissions."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    return user_info, perms


def _resolve_checks_path(
    app,
    profile_id: str,
    obsdir: str,
    check_path: str = '',
) -> Path:
    """Resolve the obsdir YAML path for one profile."""
    profile = None
    user_info = app._get_api_user()
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            profile = item
            break
    if profile is None:
        raise FileNotFoundError('Profile not found or access denied')
    cfg = checks_core.load_config(app._resolve_local_data_dir())
    root = checks_core.resolve_checks_root(
        app._resolve_local_data_dir(),
        profile_data=profile['data'],
        configured_root=cfg.get('checks_root', ''),
    )

    raw_check_path = str(check_path or '').strip()
    if raw_check_path:
        try:
            resolved = Path(raw_check_path).expanduser().resolve()
            root_resolved = Path(root).expanduser().resolve()
            suffix = str(resolved.suffix or '').lower()
            inside_root = resolved.is_relative_to(root_resolved)
            if (
                inside_root
                and resolved.is_file()
                and suffix in {'.yaml', '.yml'}
            ):
                return resolved
        except Exception:
            pass

    path = root / f'{obsdir}.yaml'
    if path.exists():
        return path
    alt = root / f'{obsdir}.yml'
    if alt.exists():
        return alt
    raise FileNotFoundError('APERO check file not found')


def api_apero_checks_update_failure(app):
    """Update one failure override or monitor event."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id') or '').strip()
    obsdir = str(body.get('obsdir') or '').strip()
    check_path = str(body.get('check_path') or '').strip()
    failure_key = str(body.get('failure_key') or '').strip()
    action = str(body.get('action') or '').strip().lower()
    comment = str(body.get('comment') or '').strip()
    if not profile_id or not obsdir or not failure_key:
        return jsonify(success=False, error='Missing identifiers'), 400
    if action not in {
        'override',
        'monitor',
        'clear',
        'clear_override',
        'clear_monitor',
    }:
        return jsonify(success=False, error='Invalid action'), 400

    cfg = checks_core.load_config(app._resolve_local_data_dir())
    override_allowed = set(
        checks_core._normalize_override_allowed(
            cfg.get('override_allowed', [])
        )
    )
    if action == 'override' and failure_key not in override_allowed:
        return jsonify(
            success=False,
            error='Override not allowed for this check',
        ), 403

    try:
        path = _resolve_checks_path(
            app,
            profile_id,
            obsdir,
            check_path,
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 404

    username = str(user_info.get('username') or 'anonymous')
    try:
        if action == 'clear':
            checks_core.clear_failure_event(path, failure_key, 'override')
            loaded = checks_core.clear_failure_event(
                path, failure_key, 'monitor'
            )
        elif action == 'clear_override':
            loaded = checks_core.clear_failure_event(
                path, failure_key, 'override'
            )
        elif action == 'clear_monitor':
            loaded = checks_core.clear_failure_event(
                path, failure_key, 'monitor'
            )
        else:
            loaded = checks_core.update_failure_event(
                path,
                failure_key,
                action,
                username,
                comment,
            )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    return jsonify(success=True, check=loaded)


def api_apero_checks_create_issue(app):
    """Create an APERO-check issue from selected failures."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id') or '').strip()
    obsdir = str(body.get('obsdir') or '').strip()
    failures = body.get('failures') or []
    reason = str(body.get('reason') or '').strip()
    if not profile_id or not obsdir or not failures:
        return jsonify(success=False, error='Missing issue details'), 400
    if not reason:
        return jsonify(success=False, error='Missing reason'), 400
    if isinstance(failures, list):
        failure_names = [str(item).strip() for item in failures if item]
    else:
        failure_names = [str(failures).strip()]

    try:
        issue = create_issue(
            _data_dir(app),
            kind='ari',
            reason=reason,
            created_by=str(user_info.get('username') or 'anonymous'),
            profile_id=profile_id,
            visibility='monitor',
            title=f'APERO Checks: {obsdir}',
            type_='APERO Check',
            label='apero-check',
            action='Go to check',
            origin_url=body.get('origin_url'),
            value={'obsdir': obsdir, 'failures': failure_names},
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    return jsonify(success=True, issue=issue)


def api_apero_checks_config_save(app):
    """Persist the APERO-check YAML directory configuration."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    body = request.get_json(silent=True) or {}
    root_path = str(body.get('checks_root') or '').strip()
    ignored_checks = body.get('ignored_checks') or []
    override_allowed = body.get('override_allowed') or []

    local_data_dir = app._resolve_local_data_dir()
    cfg = checks_core.load_config(local_data_dir)
    if root_path:
        cfg['checks_root'] = root_path
    cfg['ignored_checks'] = checks_core._normalize_ignored_checks(
        ignored_checks
    )
    cfg['override_allowed'] = checks_core._normalize_override_allowed(
        override_allowed
    )
    checks_core.save_config(local_data_dir, cfg)
    return jsonify(
        success=True,
        checks_root=str(cfg.get('checks_root') or ''),
        ignored_checks=cfg['ignored_checks'],
        override_allowed=cfg['override_allowed'],
    )


def api_apero_checks_browse_dirs(app):
    """List subdirectories for the APERO checks root browser."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    raw_path = str(request.args.get('path', '') or '').strip()
    if not raw_path:
        current = app._resolve_local_data_dir()
    else:
        try:
            current = Path(raw_path).expanduser().resolve()
        except Exception:
            current = app._resolve_local_data_dir()

    if not current.exists():
        if current.parent.exists():
            current = current.parent
        else:
            current = Path.home()

    if current.exists() and not current.is_dir():
        current = current.parent

    dirs = []
    try:
        children = sorted(
            current.iterdir(), key=lambda item: item.name.lower()
        )
        for child in children:
            if child.is_dir():
                item = dict()
                item['name'] = child.name
                item['path'] = str(child)
                dirs.append(item)
    except Exception:
        dirs = []

    return jsonify(
        success=True,
        path=str(current),
        parent=str(current.parent),
        dirs=dirs[:500],
    )