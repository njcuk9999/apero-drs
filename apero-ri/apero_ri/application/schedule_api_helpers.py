#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI monitor schedule API helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set

from flask import jsonify, request

from apero_ri.core import permissions as perms
from apero_ri.core import schedule
from apero_ri.core import user_data as ud
from apero_ri.core.auth import get_public_permissions, load_users
from apero_ri.core.permissions import resolve_user_permissions


__NAME__ = 'apero_ri.application.schedule_api_helpers'


# =============================================================================
# Define permission helpers
# =============================================================================
def _data_dir(app) -> Path:
    return Path(app.args.data_dir or str(Path.home() / '.ari'))


def _monitor_like_perm(perm: str) -> bool:
    if not isinstance(perm, str):
        return False
    if perm in ('view.monitor_portal', 'view.monitor', 'monitor'):
        return True
    if perm.startswith('monitor.'):
        return True
    if perm.startswith('view.monitor_portal.'):
        return True
    if perm.startswith('view.monitor.'):
        return True
    return False


def _user_and_perms(app):
    user_info = app._get_api_user()
    if user_info:
        user_perms = resolve_user_permissions(
            user_info.get('groups', []), app.ari_groups
        )
    else:
        user_perms = get_public_permissions()
    return user_info, set(user_perms or set())


def _all_instruments() -> Set[str]:
    params = perms.load_parameters()
    raw = params.get('instruments', {}).get('value', [])
    return set(str(item).strip().upper() for item in raw if item)


def _monitor_instruments(app, user_info: Optional[dict],
                         user_perms: Set[str]) -> List[str]:
    valid = _all_instruments()
    out: Set[str] = set()

    for perm in user_perms:
        if not isinstance(perm, str):
            continue
        if perm.startswith('monitor.'):
            suffix = perm.split('.', 1)[1].strip().upper()
            if suffix in valid:
                out.add(suffix)
        if perm.startswith('view.monitor_portal.'):
            suffix = perm.rsplit('.', 1)[-1].strip().upper()
            if suffix in valid:
                out.add(suffix)

    if ('monitor' in user_perms
            or 'view.monitor_portal' in user_perms
            or 'manage.astrometrics' in user_perms):
        groups = []
        if user_info:
            groups = user_info.get('groups', [])
        out |= set(perms.get_user_instruments(groups, app.ari_groups))

    return sorted(list(out))


def _can_view_monitor_schedule(app, user_info: Optional[dict],
                               user_perms: Set[str],
                               instrument: str) -> bool:
    if not user_info:
        return False
    if any(_monitor_like_perm(p) for p in user_perms):
        allowed = set(_monitor_instruments(app, user_info, user_perms))
        return instrument in allowed
    return False


def _can_manage_schedule(user_perms: Set[str], instrument: str) -> bool:
    inst = str(instrument or '').strip().upper()
    if ('manage.astrometrics' in user_perms
            or 'manage.group.super_admin' in user_perms
            or 'manage.group.admin' in user_perms
            or 'manage.instrument.super_admin' in user_perms
            or 'manage.instrument.admin' in user_perms):
        return True
    for perm in user_perms:
        if not isinstance(perm, str):
            continue
        if perm.startswith('manage.group.super_admin'):
            return True
        if perm.startswith('manage.group.admin.'):
            if perm.endswith('.' + inst):
                return True
        if perm.startswith('manage.group.moderator'):
            if perm == 'manage.group.moderator':
                return True
            if perm.endswith('.' + inst):
                return True
        if perm.startswith('manage.instrument.super_admin.'):
            if perm.endswith('.' + inst):
                return True
        if perm.startswith('manage.instrument.admin.'):
            if perm.endswith('.' + inst):
                return True
        if perm.startswith('manage.instrument.moderator'):
            if perm == 'manage.instrument.moderator':
                return True
            if perm.endswith('.' + inst):
                return True
    return False


def _display_name(users: Dict[str, dict], username: str) -> str:
    row = users.get(username, dict())
    first_names = str(row.get('first_names', '') or '').strip()
    last_name = str(row.get('last_name', '') or '').strip()
    full = (first_names + ' ' + last_name).strip()
    return full or username


def _user_list_payload() -> List[Dict]:
    users = load_users()
    out = []
    for username, udata in users.items():
        if not isinstance(udata, dict):
            continue
        out.append({
            'username': username,
            'who': _display_name(users, username),
        })
    out.sort(key=lambda item: item['username'].lower())
    return out


# =============================================================================
# Define endpoint helpers
# =============================================================================
def api_schedule_meta(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    instruments = _monitor_instruments(app, user_info, user_perms)
    if not instruments:
        return jsonify(success=False,
                       error='Monitor access required'), 403

    req_inst = str(request.args.get('instrument', '')).strip().upper()
    instrument = req_inst if req_inst in instruments else instruments[0]
    tasks = schedule.list_tasks(_data_dir(app), instrument)
    vis_map = schedule.get_stats_visibility_map(
        _data_dir(app), instrument
    )
    can_manage = _can_manage_schedule(user_perms, instrument)
    wsd_str = schedule.get_instrument_setting(
        _data_dir(app), instrument, 'week_start_day', '0'
    )
    try:
        week_start_day = int(wsd_str)
    except Exception:
        week_start_day = 0

    return jsonify(
        success=True,
        instruments=instruments,
        instrument=instrument,
        current_username=str(user_info.get('username', '')),
        tasks=tasks,
        users=_user_list_payload(),
        stats_visibility=vis_map,
        can_manage=can_manage,
        week_start_day=week_start_day,
    )


def api_schedule_entries_list(app):
    user_info, user_perms = _user_and_perms(app)
    instrument = str(request.args.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    filters = dict()
    for key in ('task', 'username', 'who', 'date_start',
                'date_end', 'hours', 'comment'):
        filters[key] = request.args.get(key, '')

    rows = schedule.list_entries(_data_dir(app), instrument, filters=filters)
    return jsonify(success=True, rows=rows)


def _save_user_calendar_event(entry: Dict) -> None:
    username = str(entry.get('username', '') or '').strip()
    if not username:
        return
    title = '[' + str(entry.get('instrument', '')) + '] '
    title += str(entry.get('task', '') or 'Schedule task')
    event = {
        'id': 'schedule-' + str(entry.get('instrument', ''))
              + '-' + str(entry.get('id', '')),
        'title': title,
        'date': str(entry.get('date_start', '') or ''),
        'time': '',
        'color': '#2f7d32',
        'category': 'personal',
        'recurrence': 'none',
        'status': 'confirmed',
        'timezone': 'UTC',
    }
    ud.save_event(username, event)


def api_schedule_entries_add(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    username = str(body.get('username', '')).strip()
    # Managers may create unassigned (no username) entries
    if not username:
        if not _can_manage_schedule(user_perms, instrument):
            return jsonify(
                success=False,
                error='Username is required'
            ), 400
    users = load_users()
    who = str(body.get('who', '')).strip()
    if username and not who:
        who = _display_name(users, username)

    try:
        row = schedule.add_entry(
            _data_dir(app),
            instrument=instrument,
            task=str(body.get('task', '')),
            username=username,
            who=who,
            date_start=str(body.get('date_start', '')),
            date_end=str(body.get('date_end', '')),
            hours=float(body.get('hours', 0.0) or 0.0),
            comment=str(body.get('comment', '')),
            created_by=str(user_info.get('username', 'anonymous')),
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    if bool(body.get('link_user_calendar', False)):
        _save_user_calendar_event(row)

    return jsonify(success=True, row=row)


def api_schedule_entries_edit(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    users = load_users()
    username = str(body.get('username', '')).strip()
    who = str(body.get('who', '')).strip() or _display_name(users, username)
    try:
        entry_id = int(body.get('entry_id'))
    except Exception:
        return jsonify(success=False, error='Invalid entry_id'), 400

    try:
        row = schedule.update_entry(
            _data_dir(app),
            instrument=instrument,
            entry_id=entry_id,
            task=str(body.get('task', '')),
            username=username,
            who=who,
            date_start=str(body.get('date_start', '')),
            date_end=str(body.get('date_end', '')),
            hours=float(body.get('hours', 0.0) or 0.0),
            comment=str(body.get('comment', '')),
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    if row is None:
        return jsonify(success=False, error='Entry not found'), 404

    _save_user_calendar_event(row)
    return jsonify(success=True, row=row)


def api_schedule_entries_delete(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    try:
        entry_id = int(body.get('entry_id'))
    except Exception:
        return jsonify(success=False, error='Invalid entry_id'), 400

    try:
        deleted = schedule.delete_entry(
            _data_dir(app),
            instrument=instrument,
            entry_id=entry_id,
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    if not deleted:
        return jsonify(success=False, error='Entry not found'), 404
    return jsonify(success=True)


def api_schedule_link_user_calendar(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    try:
        entry_id = int(body.get('entry_id'))
    except Exception:
        return jsonify(success=False, error='Invalid entry_id'), 400

    row = schedule.get_entry(_data_dir(app), instrument, entry_id)
    if row is None:
        return jsonify(success=False, error='Entry not found'), 404

    _save_user_calendar_event(row)
    return jsonify(success=True)


def api_schedule_tasks_upsert(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_manage_schedule(user_perms, instrument):
        return jsonify(success=False,
                       error='Manage permission required'), 403

    try:
        row = schedule.upsert_task(
            _data_dir(app),
            instrument=instrument,
            name=str(body.get('name', '')),
            description=str(body.get('description', '')),
            active=bool(body.get('active', True)),
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    return jsonify(success=True, row=row)


def api_schedule_tasks_rename(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_manage_schedule(user_perms, instrument):
        return jsonify(success=False,
                       error='Manage permission required'), 403

    try:
        row = schedule.rename_task(
            _data_dir(app),
            instrument=instrument,
            old_name=str(body.get('old_name', '')),
            new_name=str(body.get('new_name', '')),
            description=str(body.get('description', '')),
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    return jsonify(success=True, row=row)


def api_schedule_tasks_set_active(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_manage_schedule(user_perms, instrument):
        return jsonify(success=False,
                       error='Manage permission required'), 403

    try:
        schedule.set_task_active(
            _data_dir(app),
            instrument=instrument,
            name=str(body.get('name', '')),
            active=bool(body.get('active', False)),
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    return jsonify(success=True)


def api_schedule_calendar_week(app):
    user_info, user_perms = _user_and_perms(app)
    instrument = str(request.args.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    week_start = str(request.args.get('week_start', '')).strip()
    if not week_start:
        week_start = schedule.week_window('', 0)['week_start']

    payload = schedule.week_calendar_rows(
        _data_dir(app),
        instrument=instrument,
        week_start=week_start,
    )
    return jsonify(success=True, payload=payload)


def api_schedule_calendar_month(app):
    user_info, user_perms = _user_and_perms(app)
    instrument = str(request.args.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    month_start = str(request.args.get('month_start', '')).strip()
    if not month_start:
        month_start = schedule.month_window('', 0)['month_start']

    payload = schedule.month_calendar_rows(
        _data_dir(app),
        instrument=instrument,
        month_start=month_start,
    )
    return jsonify(success=True, payload=payload)


def api_schedule_calendar_weeks(app):
    user_info, user_perms = _user_and_perms(app)
    instrument = str(request.args.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    week_start = str(request.args.get('week_start', '')).strip()
    try:
        weeks = int(request.args.get('weeks', 13))
    except Exception:
        weeks = 13

    wsd_str = schedule.get_instrument_setting(
        _data_dir(app), instrument, 'week_start_day', '0'
    )
    try:
        week_start_day = int(wsd_str)
    except Exception:
        week_start_day = 0

    payload = schedule.weeks_calendar_rows(
        _data_dir(app),
        instrument=instrument,
        week_start=week_start,
        weeks=weeks,
        week_start_day=week_start_day,
    )
    return jsonify(success=True, payload=payload)


def api_schedule_stats(app):
    user_info, user_perms = _user_and_perms(app)
    instrument = str(request.args.get('instrument', '')).strip().upper()
    if not _can_view_monitor_schedule(app, user_info, user_perms, instrument):
        return jsonify(success=False,
                       error='Monitor access required'), 403

    since = str(request.args.get('since', '')).strip()
    until = str(request.args.get('until', '')).strip()
    task = str(request.args.get('task', '')).strip()
    try:
        payload = schedule.compute_stats(
            _data_dir(app),
            instrument=instrument,
            since=since,
            until=until,
            task=task,
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    vis_map = schedule.get_stats_visibility_map(_data_dir(app), instrument)
    rows = []
    for row in payload.get('rows', []):
        username = str(row.get('username', ''))
        if vis_map.get(username, True):
            rows.append(row)

    return jsonify(
        success=True,
        rows=rows,
        summary=payload.get('summary', dict()),
        stats_visibility=vis_map,
    )


def api_schedule_stats_visibility_set(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(body.get('instrument', '')).strip().upper()
    if not _can_manage_schedule(user_perms, instrument):
        return jsonify(success=False,
                       error='Manage permission required'), 403

    username = str(body.get('username', '')).strip()
    visible = bool(body.get('visible', True))
    try:
        schedule.set_stats_user_visibility(
            _data_dir(app),
            instrument=instrument,
            username=username,
            visible=visible,
            updated_by=str(user_info.get('username', 'system')),
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    vis_map = schedule.get_stats_visibility_map(
        _data_dir(app), instrument
    )
    return jsonify(success=True, stats_visibility=vis_map)


def api_schedule_instrument_setting_set(app):
    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(
            success=False, error='Login required'
        ), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(
        body.get('instrument', '')
    ).strip().upper()
    if not _can_manage_schedule(user_perms, instrument):
        return jsonify(
            success=False,
            error='Manage permission required'
        ), 403

    key = str(body.get('key', '')).strip()
    value = str(body.get('value', '')).strip()
    if not key:
        return jsonify(
            success=False, error='key is required'
        ), 400

    try:
        schedule.set_instrument_setting(
            _data_dir(app),
            instrument=instrument,
            key=key,
            value=value,
            updated_by=str(
                user_info.get('username', 'system')
            ),
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

    return jsonify(success=True)


def api_schedule_entries_bulk_add(app):
    """Create repeating unassigned entries in one call.

    Requires manage permission.  Generates one entry per repeat
    period (week / 2 weeks / month) for each selected task,
    starting at *date_start*.  ``username`` and ``who`` are left
    blank (unassigned).
    """
    from datetime import date, timedelta

    user_info, user_perms = _user_and_perms(app)
    if not user_info:
        return jsonify(
            success=False, error='Login required'
        ), 401

    body = request.get_json(silent=True) or dict()
    instrument = str(
        body.get('instrument', '')
    ).strip().upper()
    if not _can_manage_schedule(user_perms, instrument):
        return jsonify(
            success=False,
            error='Manage permission required'
        ), 403

    tasks_list = body.get('tasks', [])
    date_start_str = str(
        body.get('date_start', '')
    ).strip()
    interval = str(
        body.get('repeat_interval', 'week')
    ).strip().lower()
    try:
        repeats = max(1, min(104, int(
            body.get('repeats', 1) or 1
        )))
    except Exception:
        repeats = 1
    creator = str(
        user_info.get('username', 'anonymous')
    )

    # Parse start date
    from apero_ri.core.schedule import _parse_date as _pd
    start_day = _pd(date_start_str)
    if start_day is None:
        return jsonify(
            success=False, error='Invalid date_start'
        ), 400

    def _add_months(d: date, n: int) -> date:
        month = d.month - 1 + n
        year = d.year + month // 12
        month = month % 12 + 1
        import calendar
        last = calendar.monthrange(year, month)[1]
        return d.replace(
            year=year, month=month,
            day=min(d.day, last)
        )

    # Build list of (date_start, date_end) pairs
    periods = []
    for i in range(repeats):
        if interval == 'week':
            ps = start_day + timedelta(days=i * 7)
            pe = ps + timedelta(days=6)
        elif interval == '2weeks':
            ps = start_day + timedelta(days=i * 14)
            pe = ps + timedelta(days=13)
        else:  # month
            ps = _add_months(start_day, i)
            pe = _add_months(start_day, i + 1) - timedelta(
                days=1
            )
        periods.append(
            (ps.isoformat(), pe.isoformat())
        )

    results = []
    errors = []
    for task_name in tasks_list:
        task_name = str(task_name or '').strip()
        if not task_name:
            continue
        for ds, de in periods:
            try:
                row = schedule.add_entry(
                    _data_dir(app),
                    instrument=instrument,
                    task=task_name,
                    username='',
                    who='',
                    date_start=ds,
                    date_end=de,
                    hours=0.0,
                    comment='',
                    created_by=creator,
                )
                results.append(row)
            except ValueError as exc:
                errors.append(
                    {'task': task_name,
                     'period': ds,
                     'error': str(exc)}
                )
            except Exception as exc:
                errors.append(
                    {'task': task_name,
                     'period': ds,
                     'error': str(exc)}
                )

    return jsonify(
        success=True, rows=results, errors=errors
    )
