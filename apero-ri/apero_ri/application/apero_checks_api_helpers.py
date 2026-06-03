#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI APERO-check API helpers."""

from __future__ import annotations

import traceback
import uuid
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import jsonify, request

from apero_ri.application.issues_api_helpers import _data_dir
from apero_ri.application.monitor_view_helpers import _has_any_monitor_perm
from apero_ri.application.monitor_view_helpers import (
    _get_apero_check_page_payload,
    _normalize_apero_checks_args,
)
from apero_ri.apero_monitoring.checks import CHECKS as MONITOR_CHECKS
from apero_ri.core import apero_checks as checks_core
from apero_ri.core.auth import (
    get_accessible_profiles,
    load_apero_profiles,
    get_public_permissions,
)
from apero_ri.core.issues import create_issue
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.core import task_runner


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
    # Fall back to recursive search (mirrors list_yaml_files behaviour)
    root_resolved = Path(root).expanduser().resolve()
    for suffix in ('.yaml', '.yml'):
        matches = sorted(root_resolved.rglob(f'{obsdir}{suffix}'), key=str)
        if matches:
            return matches[0]
    raise FileNotFoundError('APERO check file not found')


def _resolve_accessible_profile(app, profile_id: str) -> dict:
    """Return one accessible APERO profile by profile id."""
    profile = None
    user_info = app._get_api_user()
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            profile = item
            break
    if profile is None:
        raise FileNotFoundError('Profile not found or access denied')
    return profile


def _queue_apero_check_run(
    app,
    profile_id: str,
    obsdir: str,
    check_names=None,
    history_user: str = '',
    history_source: str = '',
):
    """Queue one APERO check task for a specific night/check selection."""
    profile = _resolve_accessible_profile(app, profile_id)
    instrument = str(profile.get('instrument') or '').strip()
    if not instrument:
        raise RuntimeError('Profile instrument is missing')

    all_profiles = load_apero_profiles()
    cleaned_checks = []
    if isinstance(check_names, list):
        for check_name in check_names:
            value = str(check_name or '').strip()
            if value:
                cleaned_checks.append(value)

    mode = 'check' if cleaned_checks else 'night'
    first_check = cleaned_checks[0] if cleaned_checks else 'all'
    task_id = (
        'manual_apero_check__'
        + _slug_task_token(profile_id)
        + '__'
        + _slug_task_token(obsdir)
        + '__'
        + _slug_task_token(mode)
        + '__'
        + _slug_task_token(first_check)
        + '__'
        + str(uuid.uuid4())
    )
    task_cfg = dict()
    task_cfg['id'] = task_id
    task_cfg['task_key'] = 'APERO_CHECK_TASK'
    task_cfg['active'] = True
    task_cfg['force_run'] = True
    task_cfg['obs_dirs'] = [str(obsdir).strip()]
    task_cfg['create'] = True

    filters = dict()
    filters['APERO_PROFILE_INCLUDE'] = str(profile_id).strip()
    task_cfg['filters'] = filters

    if cleaned_checks:
        task_cfg['checks'] = cleaned_checks
    if str(history_user or '').strip():
        task_cfg['history_user'] = str(history_user).strip()
    if str(history_source or '').strip():
        task_cfg['history_source'] = str(history_source).strip()

    allowed, reason = task_runner.can_enqueue_now(task_cfg)
    if not allowed:
        raise RuntimeError(str(reason or 'Task cannot be enqueued'))

    from apero_ri import tasks as task_module

    task_cls = task_module.TASK_LIST.get('APERO_CHECK_TASK')
    if task_cls is None:
        raise RuntimeError('APERO_CHECK_TASK is not available')

    run_params = task_runner.build_run_params(
        instrument,
        str(app._resolve_local_data_dir()),
        all_profiles,
        task_cfg,
    )
    try:
        instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
        instance.USE_SUBPROCESS = bool(
            task_module.USE_SUBPROCESS.get('APERO_CHECK_TASK', False)
        )
        instance._task_key = 'APERO_CHECK_TASK'
    except Exception as exc:
        raise RuntimeError(
            'Task initialization failed: ' + str(exc)
        ) from exc

    task_runner.enqueue(
        instrument,
        task_id,
        instance,
        run_params,
        prepend=True,
    )
    return dict(task_id=task_id, instrument=instrument)


def _queue_apero_check_profile_run(
    app,
    profile_id: str,
    history_user: str = '',
    history_source: str = '',
):
    """Queue one full-profile APERO check rerun."""
    profile = _resolve_accessible_profile(app, profile_id)
    instrument = str(profile.get('instrument') or '').strip()
    if not instrument:
        raise RuntimeError('Profile instrument is missing')

    all_profiles = load_apero_profiles()
    task_id = (
        'manual_apero_check__'
        + _slug_task_token(profile_id)
        + '__'
        + _slug_task_token('all_nights')
        + '__'
        + _slug_task_token('full_profile')
        + '__'
        + _slug_task_token('all')
        + '__'
        + str(uuid.uuid4())
    )
    task_cfg = dict()
    task_cfg['id'] = task_id
    task_cfg['task_key'] = 'APERO_CHECK_TASK'
    task_cfg['active'] = True
    task_cfg['force_run'] = True
    task_cfg['create'] = True

    filters = dict()
    filters['APERO_PROFILE_INCLUDE'] = str(profile_id).strip()
    task_cfg['filters'] = filters

    if str(history_user or '').strip():
        task_cfg['history_user'] = str(history_user).strip()
    if str(history_source or '').strip():
        task_cfg['history_source'] = str(history_source).strip()

    allowed, reason = task_runner.can_enqueue_now(task_cfg)
    if not allowed:
        raise RuntimeError(str(reason or 'Task cannot be enqueued'))

    from apero_ri import tasks as task_module

    task_cls = task_module.TASK_LIST.get('APERO_CHECK_TASK')
    if task_cls is None:
        raise RuntimeError('APERO_CHECK_TASK is not available')

    run_params = task_runner.build_run_params(
        instrument,
        str(app._resolve_local_data_dir()),
        all_profiles,
        task_cfg,
    )
    try:
        instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
        instance.USE_SUBPROCESS = bool(
            task_module.USE_SUBPROCESS.get('APERO_CHECK_TASK', False)
        )
        instance._task_key = 'APERO_CHECK_TASK'
    except Exception as exc:
        raise RuntimeError(
            'Task initialization failed: ' + str(exc)
        ) from exc

    task_runner.enqueue(
        instrument,
        task_id,
        instance,
        run_params,
        prepend=True,
    )
    return dict(task_id=task_id, instrument=instrument)


def _slug_task_token(value: str, max_len: int = 64) -> str:
    """Normalise one task-id token to a compact safe slug."""
    text = str(value or '').strip().lower()
    text = re.sub(r'[^a-z0-9_-]+', '-', text)
    text = text.replace('__', '_').strip('-_')
    if not text:
        text = 'na'
    return text[:max(8, int(max_len))]


def _manual_task_meta_from_task_cfg(task_cfg: dict) -> dict:
    """Infer manual APERO-check task details from TASK_CONFIG."""
    cfg = dict(task_cfg or {})
    checks = cfg.get('checks')
    obs_dirs = cfg.get('obs_dirs')
    filters = cfg.get('filters')
    if not isinstance(filters, dict):
        filters = {}

    obsdir = ''
    if isinstance(obs_dirs, list) and obs_dirs:
        obsdir = str(obs_dirs[0] or '')
    check_key = ''
    if isinstance(checks, list) and checks:
        check_key = str(checks[0] or '')
    profile_id = ''
    include = filters.get('APERO_PROFILE_INCLUDE')
    if isinstance(include, list) and include:
        profile_id = str(include[0] or '')
    elif isinstance(include, str):
        profile_id = str(include or '').strip()

    mode = 'single_check' if check_key else 'full_obsdir'
    label = 'Individual test re-run' if check_key else 'Full obsdir re-run'
    return {
        'mode': mode,
        'label': label,
        'obsdir': obsdir,
        'check_key': check_key,
        'profile_id': profile_id,
    }


def _manual_task_meta_from_id(task_id: str) -> dict:
    """Infer manual APERO-check metadata from encoded task id."""
    text = str(task_id or '')
    parts = text.split('__')
    out = {
        'mode': 'unknown',
        'label': 'Unknown manual run',
        'obsdir': '',
        'check_key': '',
        'profile_id': '',
    }
    if len(parts) < 6:
        return out
    if not parts[0].startswith('manual_apero_check'):
        return out
    out['profile_id'] = str(parts[1] or '')
    out['obsdir'] = str(parts[2] or '')
    mode = str(parts[3] or '')
    check_key = str(parts[4] or '')
    if mode == 'check':
        out['mode'] = 'single_check'
        out['label'] = 'Individual test re-run'
        out['check_key'] = '' if check_key == 'all' else check_key
    elif mode == 'night':
        out['mode'] = 'full_obsdir'
        out['label'] = 'Full obsdir re-run'
    return out


def _task_matches_profile(
    task_status: dict,
    profile_id: str,
    task_id: str = '',
) -> bool:
    """Return True when task status belongs to one APERO profile."""
    run_params = task_status.get('run_params')
    if not isinstance(run_params, dict):
        return False
    task_cfg = run_params.get('TASK_CONFIG')
    if not isinstance(task_cfg, dict):
        task_cfg = {}

    task_key = str(task_cfg.get('task_key') or '').strip().upper()
    if task_key and task_key != 'APERO_CHECK_TASK':
        return False
    if not task_key:
        task_id_text = str(task_id or '').strip().lower()
        if not task_id_text.startswith('manual_apero_check'):
            return False

    filters = task_cfg.get('filters')
    if not isinstance(filters, dict):
        filters = {}
    include = filters.get('APERO_PROFILE_INCLUDE')
    target = str(profile_id or '').strip().lower()
    if isinstance(include, list) and include:
        include_values = [
            str(item or '').strip().lower() for item in include
        ]
        return target in include_values
    if isinstance(include, str) and include.strip():
        include_values = [
            item.strip().lower() for item in include.split(',')
            if item.strip()
        ]
        return target in include_values

    profile_names = run_params.get('APERO_PROFILE_NAMES')
    if isinstance(profile_names, list) and profile_names:
        profile_values = [
            str(item or '').strip().lower()
            for item in profile_names
        ]
        return target in profile_values
    return False


def _queue_status_payload(app, profile_id: str) -> dict:
    """Build queue-status payload for one APERO profile."""
    status = task_runner.get_status()
    running = []
    queued = []

    current_info = status.get('current_info')
    if isinstance(current_info, dict):
        task_id = str(current_info.get('task_id') or '')
        detail = task_runner.get_task_status(task_id)
        if detail.get('found') and _task_matches_profile(
            detail,
            profile_id,
            task_id=task_id,
        ):
            task_cfg = dict(detail.get('run_params', {}).get('TASK_CONFIG', {})
                            or {})
            task_meta = _manual_task_meta_from_task_cfg(task_cfg)
            running.append({
                'task_id': task_id,
                'task_name': str(current_info.get('task_name') or task_id),
                'status': str(detail.get('status') or ''),
                'progress': detail.get('progress', 0),
                'subprogress': detail.get('subprogress', 0),
                'info': str(detail.get('info') or ''),
                'run_count': detail.get('run_count', 0),
                'log_path': str(detail.get('log_path') or ''),
                'manual': task_id.startswith('manual_apero_check__'),
                'task_mode': task_meta.get('mode'),
                'task_label': task_meta.get('label'),
                'obsdir': task_meta.get('obsdir'),
                'check_key': task_meta.get('check_key'),
            })

    for index, queue_item in enumerate(status.get('queue_info') or [], 1):
        if not isinstance(queue_item, dict):
            continue
        task_id = str(queue_item.get('task_id') or '')
        detail = task_runner.get_task_status(task_id)
        if not detail.get('found'):
            continue
        if not _task_matches_profile(
            detail,
            profile_id,
            task_id=task_id,
        ):
            continue
        task_cfg = dict(detail.get('run_params', {}).get('TASK_CONFIG', {})
                        or {})
        task_meta = _manual_task_meta_from_task_cfg(task_cfg)
        queued.append({
            'position': index,
            'task_id': task_id,
            'task_name': str(queue_item.get('task_name') or task_id),
            'status': str(detail.get('status') or ''),
            'progress': detail.get('progress', 0),
            'subprogress': detail.get('subprogress', 0),
            'info': str(detail.get('info') or ''),
            'run_count': detail.get('run_count', 0),
            'log_path': str(detail.get('log_path') or ''),
            'manual': task_id.startswith('manual_apero_check__'),
            'task_mode': task_meta.get('mode'),
            'task_label': task_meta.get('label'),
            'obsdir': task_meta.get('obsdir'),
            'check_key': task_meta.get('check_key'),
        })

    history = []
    for row in status.get('recent_history') or []:
        if not isinstance(row, dict):
            continue
        task_id = str(row.get('task_id') or '')
        if not task_id.startswith('manual_apero_check__'):
            continue
        meta = _manual_task_meta_from_id(task_id)
        expected = _slug_task_token(profile_id)
        if str(meta.get('profile_id') or '') != expected:
            continue
        history.append({
            'timestamp': str(row.get('timestamp') or ''),
            'task_id': task_id,
            'task_name': str(row.get('task_name') or task_id),
            'status': str(row.get('status') or ''),
            'details': str(row.get('details') or ''),
            'duration_seconds': row.get('duration_seconds'),
            'task_mode': meta.get('mode'),
            'task_label': meta.get('label'),
            'obsdir': meta.get('obsdir'),
            'check_key': meta.get('check_key'),
        })

    return {
        'profile_id': profile_id,
        'running': running,
        'queued': queued,
        'history': history,
    }


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
    valid_checks = {
        str(key or '').strip()
        for key in MONITOR_CHECKS
        if str(key or '').strip() != ''
    }

    local_data_dir = app._resolve_local_data_dir()
    cfg = checks_core.load_config(local_data_dir)
    if root_path:
        cfg['checks_root'] = root_path
    cfg['ignored_checks'] = [
        key for key in checks_core._normalize_ignored_checks(
            ignored_checks
        )
        if key in valid_checks
    ]
    cfg['override_allowed'] = [
        key for key in checks_core._normalize_override_allowed(
            override_allowed
        )
        if key in valid_checks
    ]
    checks_core.save_config(local_data_dir, cfg)
    # Invalidate the in-memory and disk policy caches so the next page
    # load reflects the newly saved ignored/override state immediately.
    from apero_ri.application import page_view_helpers as pvh
    pvh.invalidate_policy_cache(local_data_dir)
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


def api_apero_checks_profile_page(app, profile_id):
    """Return one or two pages of APERO-check cards as JSON."""
    user_info, perms = _api_user(app)
    can_monitor = _has_any_monitor_perm(perms)
    can_manage = 'manage.apero_profile' in set(perms or set())
    if not can_monitor and not can_manage:
        return jsonify(success=False, error='Monitor access required'), 403

    profile = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            profile = item
            break
    if profile is None:
        return jsonify(
            success=False,
            error='Profile not found or access denied',
        ), 404

    page_args = _normalize_apero_checks_args(request.args)
    try:
        pages_to_load = max(1, min(int(request.args.get('pages', '2')), 2))
    except (TypeError, ValueError):
        pages_to_load = 2

    payload = _get_apero_check_page_payload(
        app,
        profile['data'],
        profile_id,
        profile['instrument'],
        page_args['page_num'],
        page_args['per_page'],
        page_args['type_filter'],
        page_args['result_filter'],
        page_args['obsdir_filter'],
        page_args['obsdir_sort'],
        page_args['show_overridden'],
        page_args['show_monitored'],
        page_args['show_passed'],
        pages_to_load=pages_to_load,
    )

    pages = dict()
    for key, value in payload['pages'].items():
        pages[str(key)] = value

    return jsonify(
        success=True,
        profile_id=profile_id,
        page=payload['page'],
        per_page=payload['per_page'],
        total_cards=payload['total_cards'],
        total_pages=payload['total_pages'],
        checks_root=payload['checks_root'],
        pages=pages,
    )


def api_apero_checks_policy_sections(app):
    """Return heavy APERO checks policy sections asynchronously."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    local_data_dir = app._resolve_local_data_dir()
    checks_cfg = checks_core.load_config(local_data_dir)
    ignored_checks = checks_core.load_ignored_checks(local_data_dir)
    override_allowed = checks_core.load_override_allowed(local_data_dir)

    from apero_ri.application import page_view_helpers as pvh

    payload = pvh._build_apero_policy_payload(
        local_data_dir,
        checks_cfg,
        ignored_checks,
        override_allowed,
    )
    checks_catalog = payload.get('checks_catalog', [])
    checks_health = pvh._build_checks_policy_health(
        checks_catalog,
        ignored_checks,
    )

    return jsonify(
        success=True,
        checks_catalog=checks_catalog,
        profile_summaries=payload.get('profile_summaries', []),
        policy_last_updated=payload.get('policy_last_updated', ''),
        checks_health=checks_health,
    )


def api_apero_checks_view_yaml(app):
    """Return one APERO check YAML file content in read-only mode."""
    user_info, perms = _api_user(app)
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id') or '').strip()
    obsdir = str(body.get('obsdir') or '').strip()
    check_path = str(body.get('check_path') or '').strip()
    if not profile_id or not obsdir:
        return jsonify(
            success=False,
            error='Missing profile_id or obsdir',
        ), 400

    try:
        path = _resolve_checks_path(
            app,
            profile_id,
            obsdir,
            check_path,
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 404

    max_bytes = 2_000_000
    try:
        raw = path.read_bytes()
        was_truncated = len(raw) > max_bytes
        if was_truncated:
            raw = raw[:max_bytes]
        text = raw.decode('utf-8', errors='replace')
        if was_truncated:
            text += ('\n\n# --- output truncated by ARI ' +
                     f'({max_bytes} bytes limit) ---')
    except Exception:
        return jsonify(
            success=False,
            error='Could not read YAML file',
            traceback=traceback.format_exc(),
        ), 500

    try:
        stat = path.stat()
        last_run_raw = datetime.fromtimestamp(
            stat.st_mtime,
            tz=timezone.utc,
        ).isoformat(timespec='seconds')
    except Exception:
        last_run_raw = ''

    last_run = checks_core.format_last_run_display(last_run_raw)

    return jsonify(
        success=True,
        path=str(path),
        obsdir=obsdir,
        last_run=last_run,
        content=text,
        truncated=was_truncated,
    )


def api_apero_checks_rerun_night(app):
    """Queue an async APERO-check run for one profile night."""
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
    if not profile_id or not obsdir:
        return jsonify(success=False, error='Missing profile_id or obsdir'), 400

    try:
        queued = _queue_apero_check_run(
            app,
            profile_id,
            obsdir,
            check_names=[],
            history_user=str(user_info.get('username') or '').strip(),
            history_source='ARI:apero_checks',
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400

    return jsonify(
        success=True,
        task_id=str(queued.get('task_id') or ''),
        instrument=str(queued.get('instrument') or ''),
    )


def api_apero_checks_rerun_single_check(app):
    """Queue an async APERO-check run for one check on one night."""
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
    check_key = str(body.get('check_key') or '').strip()
    if not profile_id or not obsdir or not check_key:
        return jsonify(
            success=False,
            error='Missing profile_id, obsdir or check_key',
        ), 400

    try:
        queued = _queue_apero_check_run(
            app,
            profile_id,
            obsdir,
            check_names=[check_key],
            history_user=str(user_info.get('username') or '').strip(),
            history_source='ARI:apero_checks',
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400

    return jsonify(
        success=True,
        task_id=str(queued.get('task_id') or ''),
        instrument=str(queued.get('instrument') or ''),
    )


def api_apero_checks_clean_reset_profile(app):
    """Delete all profile YAMLs and queue one full rerun."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id') or '').strip()
    if profile_id == '':
        return jsonify(success=False, error='Missing profile_id'), 400

    try:
        profile = _resolve_accessible_profile(app, profile_id)
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 404

    local_data_dir = app._resolve_local_data_dir()
    cfg = checks_core.load_config(local_data_dir)
    root = checks_core.resolve_checks_root(
        local_data_dir,
        profile_data=profile.get('data'),
        configured_root=cfg.get('checks_root', ''),
    )

    deleted = 0
    failures = []
    for path in checks_core.list_yaml_files(root):
        try:
            path.unlink(missing_ok=False)
            deleted += 1
        except Exception as exc:
            failures.append(f'{path.name}: {exc}')

    if failures:
        return jsonify(
            success=False,
            error='Failed to remove one or more YAML files',
            deleted=deleted,
            failed=len(failures),
            details=failures[:10],
        ), 500

    try:
        queued = _queue_apero_check_profile_run(
            app,
            profile_id,
            history_user=str(user_info.get('username') or '').strip(),
            history_source='ARI:apero_checks_clean_reset',
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc), deleted=deleted), 400

    return jsonify(
        success=True,
        deleted=deleted,
        task_id=str(queued.get('task_id') or ''),
        instrument=str(queued.get('instrument') or ''),
    )


def api_apero_checks_delete_obsdir(app):
    """Delete one APERO-check YAML file for an obsdir (admin only)."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id') or '').strip()
    obsdir = str(body.get('obsdir') or '').strip()
    check_path = str(body.get('check_path') or '').strip()
    if not profile_id or not obsdir:
        return jsonify(success=False, error='Missing profile_id or obsdir'), 400

    try:
        path = _resolve_checks_path(
            app,
            profile_id,
            obsdir,
            check_path,
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 404

    try:
        path.unlink(missing_ok=False)
    except Exception:
        return jsonify(
            success=False,
            error='Failed to remove YAML file',
            traceback=traceback.format_exc(),
        ), 500

    return jsonify(success=True, deleted_path=str(path))


def api_apero_checks_delete_test_from_yamls(app):
    """Delete one test key from failures/passes across profile YAML files."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    body = request.get_json(silent=True) or {}
    check_key = str(body.get('check_key') or '').strip().upper()
    profile_scope = str(body.get('profile_scope') or 'all').strip()
    if check_key == '':
        return jsonify(success=False, error='Missing check_key'), 400

    profiles = list(get_accessible_profiles(user_info, app.ari_groups) or [])
    if profile_scope != 'all':
        profiles = [
            item for item in profiles
            if str(item.get('profile_id') or '') == profile_scope
        ]
        if len(profiles) == 0:
            return jsonify(
                success=False,
                error='Profile not found or access denied',
            ), 404

    local_data_dir = app._resolve_local_data_dir()
    cfg = checks_core.load_config(local_data_dir)

    all_files = []
    seen_files = set()
    selected_profiles = []
    for profile in profiles:
        profile_id = str(profile.get('profile_id') or '').strip()
        if profile_id != '':
            selected_profiles.append(profile_id)
        root = checks_core.resolve_checks_root(
            local_data_dir,
            profile_data=profile.get('data'),
            configured_root=cfg.get('checks_root', ''),
        )
        for path in checks_core.list_yaml_files(root):
            path_key = str(path.resolve())
            if path_key in seen_files:
                continue
            seen_files.add(path_key)
            all_files.append(path)

    scanned = 0
    updated = 0
    removed_failures = 0
    removed_passes = 0
    for path in all_files:
        scanned += 1
        outcome = checks_core.delete_test_key(path, check_key)
        removed_failures += int(outcome.get('removed_failures') or 0)
        removed_passes += int(outcome.get('removed_passes') or 0)
        if bool(outcome.get('changed')):
            updated += 1

    return jsonify(
        success=True,
        check_key=check_key,
        profile_scope=profile_scope,
        selected_profiles=sorted(selected_profiles),
        yaml_files_scanned=scanned,
        yaml_files_updated=updated,
        removed_failures=removed_failures,
        removed_passes=removed_passes,
    )


def api_apero_checks_queue_status(app, profile_id):
    """Return APERO-check queue and history for one profile."""
    user_info, perms = _api_user(app)
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    profile = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            profile = item
            break
    if profile is None:
        return jsonify(
            success=False,
            error='Profile not found or access denied',
        ), 404

    payload = _queue_status_payload(app, profile_id)
    return jsonify(success=True, **payload)


def api_apero_checks_queue_cancel_task(app, profile_id):
    """Cancel one queued/running APERO-check task for this profile."""
    user_info, perms = _api_user(app)
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    body = request.get_json(silent=True) or {}
    task_id = str(body.get('task_id') or '').strip()
    if not task_id:
        return jsonify(success=False, error='Missing task_id'), 400

    detail = task_runner.get_task_status(task_id)
    if not detail.get('found'):
        return jsonify(success=False, error='Task not found'), 404
    if not _task_matches_profile(detail, profile_id, task_id=task_id):
        return jsonify(success=False, error='Task does not match profile'), 403

    result = task_runner.cancel_task(task_id)
    if not result.get('success'):
        return jsonify(
            success=False,
            error=str(result.get('error') or ''),
        ), 400
    return jsonify(success=True, result=result)


def api_apero_checks_queue_kill_profile(app, profile_id):
    """Cancel all queued/running APERO-check tasks for one profile."""
    user_info, perms = _api_user(app)
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    payload = _queue_status_payload(app, profile_id)
    to_cancel = []
    for row in payload.get('running', []):
        task_id = str(row.get('task_id') or '')
        if task_id:
            to_cancel.append(task_id)
    for row in payload.get('queued', []):
        task_id = str(row.get('task_id') or '')
        if task_id:
            to_cancel.append(task_id)

    results = []
    for task_id in to_cancel:
        results.append(task_runner.cancel_task(task_id))

    return jsonify(
        success=True,
        profile_id=profile_id,
        cancelled=len(results),
        results=results,
    )


def api_apero_checks_queue_clear_history(app, profile_id):
    """Clear recent async history (global operation)."""
    user_info, perms = _api_user(app)
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    result = task_runner.clear_recent_history()
    return jsonify(
        success=True,
        profile_id=profile_id,
        scope='global',
        result=result,
    )


def api_apero_checks_check_results(app):
    """Return all (profile_id, obsdir) rows where a check has a given state.

    Used by the check-info page to show which nights failed/monitored/mixed
    for a specific check key, in an overlay table.

    Query parameters:
        check_key  (required) – e.g. "ASTROM"
        state      (required) – one of: failed, monitored, mixed, overridden, passed
    """
    user_info, perms = _api_user(app)
    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    check_key = str(request.args.get('check_key', '') or '').strip()
    state_filter = str(request.args.get('state', '') or '').strip().lower()
    if not check_key or not state_filter:
        return jsonify(success=False, error='check_key and state required'), 400

    from apero_ri.application import page_view_helpers as pvh
    from flask import url_for as _flask_url_for

    local_data_dir = app._resolve_local_data_dir()
    checks_cfg = checks_core.load_config(local_data_dir)
    ignored_checks = set(checks_core.load_ignored_checks(local_data_dir))

    profile_rows = pvh._collect_policy_roots(local_data_dir, checks_cfg)

    rows = []
    for row in profile_rows:
        profile_id = str(row.get('profile_id') or '')
        checks_root = row.get('checks_root')
        if not checks_root:
            continue
        for yaml_path in sorted(Path(checks_root).glob('*.yaml')):
            obsdir = yaml_path.stem  # filename without .yaml
            try:
                loaded = checks_core.load_check_file(yaml_path)
            except Exception:
                continue
            # Look in failures and passes for this check_key.
            for bucket in ('failures', 'passes'):
                bucket_data = loaded.get(bucket, {})
                if not isinstance(bucket_data, dict):
                    continue
                check_row = bucket_data.get(check_key)
                if check_row is None:
                    continue
                row_state = pvh._row_state(bucket, check_row or {})
                if row_state == state_filter:
                    try:
                        obsdir_url = _flask_url_for(
                            'monitor_apero_checks_obsdir_view',
                            profile_id=profile_id,
                            obsdir=obsdir,
                        )
                    except Exception:
                        obsdir_url = ''
                    rows.append(dict(
                        profile_id=profile_id,
                        obsdir=obsdir,
                        state=row_state,
                        obsdir_url=obsdir_url,
                    ))
                    break  # only one state per obsdir/check

    rows.sort(key=lambda r: (r['profile_id'], r['obsdir']))
    return jsonify(success=True, check_key=check_key, state=state_filter,
                   rows=rows)
