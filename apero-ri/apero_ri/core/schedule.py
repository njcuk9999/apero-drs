#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI monitor schedule storage and statistics helpers."""
from __future__ import annotations

import sqlite3
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional


__NAME__ = 'apero_ri.core.schedule'

_LOCK = threading.Lock()


# =============================================================================
# Define helpers
# =============================================================================
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _norm_text(value: Optional[str]) -> str:
    return str(value or '').strip()


def _norm_instrument(instrument: str) -> str:
    return _norm_text(instrument).upper()


def _parse_date(value: str) -> Optional[date]:
    text = _norm_text(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except Exception:
        return None


def _days_overlap(
    start_day: date,
    end_day: date,
    since_day: date,
    until_day: date,
) -> int:
    lo = max(start_day, since_day)
    hi = min(end_day, until_day)
    if lo > hi:
        return 0
    return (hi - lo).days + 1


def _db_path(data_dir: Path) -> Path:
    path = Path(data_dir) / 'shared' / 'schedule.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect(data_dir: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(_db_path(data_dir)), timeout=30)
    con.row_factory = sqlite3.Row
    _init_schema(con)
    return con


def _init_schema(con: sqlite3.Connection) -> None:
    con.execute(
        'CREATE TABLE IF NOT EXISTS schedule_tasks ('
        ' id INTEGER PRIMARY KEY AUTOINCREMENT,'
        ' instrument TEXT NOT NULL,'
        ' name TEXT NOT NULL,'
        ' description TEXT NOT NULL DEFAULT \'\','
        ' active INTEGER NOT NULL DEFAULT 1,'
        ' created_at TEXT NOT NULL,'
        ' updated_at TEXT NOT NULL,'
        ' UNIQUE(instrument, name)'
        ')'
    )
    con.execute(
        'CREATE TABLE IF NOT EXISTS schedule_entries ('
        ' id INTEGER PRIMARY KEY AUTOINCREMENT,'
        ' instrument TEXT NOT NULL,'
        ' task TEXT NOT NULL,'
        ' username TEXT NOT NULL,'
        ' who TEXT NOT NULL,'
        ' date_start TEXT NOT NULL,'
        ' date_end TEXT NOT NULL,'
        ' hours REAL NOT NULL DEFAULT 0.0,'
        ' comment TEXT NOT NULL DEFAULT \'\','
        ' created_by TEXT NOT NULL,'
        ' created_at TEXT NOT NULL,'
        ' updated_at TEXT NOT NULL'
        ')'
    )
    con.execute(
        'CREATE TABLE IF NOT EXISTS schedule_stats_visibility ('
        ' instrument TEXT NOT NULL,'
        ' username TEXT NOT NULL,'
        ' visible INTEGER NOT NULL DEFAULT 1,'
        ' updated_by TEXT NOT NULL DEFAULT \'system\','
        ' updated_at TEXT NOT NULL,'
        ' PRIMARY KEY(instrument, username)'
        ')'
    )
    con.execute(
        'CREATE TABLE IF NOT EXISTS '
        'schedule_instrument_settings ('
        ' instrument TEXT NOT NULL,'
        ' key TEXT NOT NULL,'
        ' value TEXT NOT NULL DEFAULT \'\','
        ' updated_by TEXT NOT NULL DEFAULT \'system\','
        ' updated_at TEXT NOT NULL,'
        ' PRIMARY KEY(instrument, key)'
        ')'
    )
    con.commit()


# =============================================================================
# Define instrument-setting helpers
# =============================================================================
def get_instrument_setting(
    data_dir: Path,
    instrument: str,
    key: str,
    default: str = '',
) -> str:
    inst = _norm_instrument(instrument)
    key_str = _norm_text(key)
    with _connect(data_dir) as con:
        row = con.execute(
            'SELECT value FROM '
            'schedule_instrument_settings '
            'WHERE instrument = ? AND key = ?',
            [inst, key_str],
        ).fetchone()
    if row is None:
        return default
    return str(row['value'])


def set_instrument_setting(
    data_dir: Path,
    instrument: str,
    key: str,
    value: str,
    updated_by: str = 'system',
) -> None:
    inst = _norm_instrument(instrument)
    key_str = _norm_text(key)
    val_str = _norm_text(value)
    if not inst or not key_str:
        raise ValueError(
            'instrument and key are required'
        )
    now = _utc_now()
    updater = _norm_text(updated_by) or 'system'
    with _LOCK:
        with _connect(data_dir) as con:
            con.execute(
                'INSERT INTO '
                'schedule_instrument_settings '
                '(instrument, key, value,'
                ' updated_by, updated_at) '
                'VALUES (?, ?, ?, ?, ?) '
                'ON CONFLICT(instrument, key) '
                'DO UPDATE SET '
                ' value = excluded.value,'
                ' updated_by = excluded.updated_by,'
                ' updated_at = excluded.updated_at',
                [inst, key_str, val_str, updater, now],
            )
            con.commit()


# =============================================================================
# Define task helpers
# =============================================================================
def list_tasks(
    data_dir: Path,
    instrument: str,
    include_inactive: bool = False,
) -> List[Dict]:
    inst = _norm_instrument(instrument)
    query = (
        'SELECT id, instrument, name, description, active '
        'FROM schedule_tasks WHERE instrument = ?'
    )
    args = [inst]
    if not include_inactive:
        query += ' AND active = 1'
    query += ' ORDER BY LOWER(name) ASC'
    with _connect(data_dir) as con:
        rows = con.execute(query, args).fetchall()
    return [dict(row) for row in rows]


def upsert_task(
    data_dir: Path,
    instrument: str,
    name: str,
    description: str = '',
    active: bool = True,
) -> Dict:
    inst = _norm_instrument(instrument)
    task_name = _norm_text(name)
    if not inst or not task_name:
        raise ValueError('instrument and task name are required')
    now = _utc_now()
    with _LOCK:
        with _connect(data_dir) as con:
            con.execute(
                'INSERT INTO schedule_tasks ('
                ' instrument, name, description, active, created_at, updated_at'
                ') VALUES (?, ?, ?, ?, ?, ?) '
                'ON CONFLICT(instrument, name) DO UPDATE SET '
                ' description = excluded.description,'
                ' active = excluded.active,'
                ' updated_at = excluded.updated_at',
                [inst, task_name, _norm_text(description),
                 1 if active else 0, now, now],
            )
            row = con.execute(
                'SELECT id, instrument, name, description, active '
                'FROM schedule_tasks WHERE instrument = ? AND name = ?',
                [inst, task_name],
            ).fetchone()
            con.commit()
    return dict(row) if row else dict()


def rename_task(
    data_dir: Path,
    instrument: str,
    old_name: str,
    new_name: str,
    description: str = '',
) -> Dict:
    inst = _norm_instrument(instrument)
    old_task = _norm_text(old_name)
    new_task = _norm_text(new_name)
    if not old_task or not new_task:
        raise ValueError('old and new task names are required')
    now = _utc_now()
    with _LOCK:
        with _connect(data_dir) as con:
            row = con.execute(
                'SELECT id FROM schedule_tasks '
                'WHERE instrument = ? AND name = ?',
                [inst, old_task],
            ).fetchone()
            if not row:
                raise ValueError('task not found')
            con.execute(
                'UPDATE schedule_tasks SET '
                ' name = ?, description = ?, updated_at = ? '
                'WHERE instrument = ? AND name = ?',
                [new_task, _norm_text(description), now, inst, old_task],
            )
            con.execute(
                'UPDATE schedule_entries SET task = ?, updated_at = ? '
                'WHERE instrument = ? AND task = ?',
                [new_task, now, inst, old_task],
            )
            out = con.execute(
                'SELECT id, instrument, name, description, active '
                'FROM schedule_tasks WHERE instrument = ? AND name = ?',
                [inst, new_task],
            ).fetchone()
            con.commit()
    return dict(out) if out else dict()


def set_task_active(
    data_dir: Path,
    instrument: str,
    name: str,
    active: bool,
) -> None:
    inst = _norm_instrument(instrument)
    task_name = _norm_text(name)
    with _LOCK:
        with _connect(data_dir) as con:
            con.execute(
                'UPDATE schedule_tasks SET active = ?, updated_at = ? '
                'WHERE instrument = ? AND name = ?',
                [1 if active else 0, _utc_now(), inst, task_name],
            )
            con.commit()


# =============================================================================
# Define entry helpers
# =============================================================================
def add_entry(
    data_dir: Path,
    instrument: str,
    task: str,
    username: str,
    who: str,
    date_start: str,
    date_end: str,
    hours: float,
    comment: str,
    created_by: str,
) -> Dict:
    inst = _norm_instrument(instrument)
    task_name = _norm_text(task)
    uname = _norm_text(username)
    who_name = _norm_text(who)
    day_start = _parse_date(date_start)
    day_end = _parse_date(date_end)
    if not task_name:
        raise ValueError('task name is required')
    if day_start is None or day_end is None:
        raise ValueError(
            'date_start and date_end must be valid ISO dates'
        )
    if day_start > day_end:
        raise ValueError('date_start must be <= date_end')
    try:
        hour_val = float(hours or 0.0)
    except Exception:
        hour_val = 0.0
    now = _utc_now()
    cutoff = (
        datetime.now(timezone.utc) - timedelta(seconds=10)
    ).isoformat(timespec='seconds')
    creator = _norm_text(created_by) or 'anonymous'
    note = _norm_text(comment)

    with _LOCK:
        with _connect(data_dir) as con:
            existing = con.execute(
                'SELECT * FROM schedule_entries WHERE '
                ' instrument = ? AND task = ? AND username = ? '
                ' AND who = ? AND date_start = ? AND date_end = ? '
                ' AND hours = ? AND comment = ? AND created_by = ? '
                ' AND created_at >= ? '
                'ORDER BY id DESC LIMIT 1',
                [inst, task_name, uname, who_name,
                 day_start.isoformat(), day_end.isoformat(),
                 hour_val, note, creator, cutoff],
            ).fetchone()
            if existing is not None:
                return dict(existing)

            con.execute(
                'INSERT INTO schedule_entries ('
                ' instrument, task, username, who, date_start, date_end,'
                ' hours, comment, created_by, created_at, updated_at'
                ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                [inst, task_name, uname, who_name,
                 day_start.isoformat(), day_end.isoformat(),
                 hour_val, note, creator, now, now],
            )
            row = con.execute(
                'SELECT * FROM schedule_entries WHERE id = last_insert_rowid()'
            ).fetchone()
            con.commit()
    return dict(row) if row else dict()


def list_entries(
    data_dir: Path,
    instrument: str,
    filters: Optional[Dict[str, str]] = None,
) -> List[Dict]:
    inst = _norm_instrument(instrument)
    query = (
        'SELECT id, instrument, task, username, who, date_start, date_end, '
        'hours, comment, created_by, created_at, updated_at '
        'FROM schedule_entries WHERE instrument = ?'
    )
    args: List = [inst]
    fmap = filters or dict()
    for col in ('task', 'username', 'who', 'date_start',
                'date_end', 'comment'):
        value = _norm_text(fmap.get(col, ''))
        if value:
            query += ' AND LOWER(' + col + ') LIKE ?'
            args.append('%' + value.lower() + '%')
    hour_filter = _norm_text(fmap.get('hours', ''))
    if hour_filter:
        query += ' AND CAST(hours AS TEXT) LIKE ?'
        args.append('%' + hour_filter + '%')
    query += ' ORDER BY date_start DESC, id DESC'
    with _connect(data_dir) as con:
        rows = con.execute(query, args).fetchall()
    return [dict(row) for row in rows]


def list_entries_overlap(
    data_dir: Path,
    instrument: str,
    start_day: date,
    end_day: date,
) -> List[Dict]:
    inst = _norm_instrument(instrument)
    with _connect(data_dir) as con:
        rows = con.execute(
            'SELECT * FROM schedule_entries '
            'WHERE instrument = ? AND date_end >= ? AND date_start <= ? '
            'ORDER BY date_start ASC, id ASC',
            [inst, start_day.isoformat(), end_day.isoformat()],
        ).fetchall()
    return [dict(row) for row in rows]


def get_entry(
    data_dir: Path,
    instrument: str,
    entry_id: int,
) -> Optional[Dict]:
    inst = _norm_instrument(instrument)
    with _connect(data_dir) as con:
        row = con.execute(
            'SELECT * FROM schedule_entries '
            'WHERE instrument = ? AND id = ?',
            [inst, int(entry_id)],
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def update_entry(
    data_dir: Path,
    instrument: str,
    entry_id: int,
    task: str,
    username: str,
    who: str,
    date_start: str,
    date_end: str,
    hours: float,
    comment: str,
) -> Optional[Dict]:
    inst = _norm_instrument(instrument)
    task_name = _norm_text(task)
    uname = _norm_text(username)
    who_name = _norm_text(who)
    day_start = _parse_date(date_start)
    day_end = _parse_date(date_end)
    if not task_name:
        raise ValueError('task name is required')
    if day_start is None or day_end is None:
        raise ValueError(
            'date_start and date_end must be valid ISO dates'
        )
    if day_start > day_end:
        raise ValueError('date_start must be <= date_end')
    try:
        hour_val = float(hours or 0.0)
    except Exception:
        hour_val = 0.0

    with _LOCK:
        with _connect(data_dir) as con:
            con.execute(
                'UPDATE schedule_entries SET '
                ' task = ?, username = ?, who = ?, '
                ' date_start = ?, date_end = ?, hours = ?, '
                ' comment = ?, updated_at = ? '
                'WHERE instrument = ? AND id = ?',
                [task_name, uname, who_name,
                 day_start.isoformat(), day_end.isoformat(),
                 hour_val, _norm_text(comment), _utc_now(),
                 inst, int(entry_id)],
            )
            row = con.execute(
                'SELECT * FROM schedule_entries '
                'WHERE instrument = ? AND id = ?',
                [inst, int(entry_id)],
            ).fetchone()
            con.commit()
    if row is None:
        return None
    return dict(row)


def delete_entry(
    data_dir: Path,
    instrument: str,
    entry_id: int,
) -> bool:
    inst = _norm_instrument(instrument)
    with _LOCK:
        with _connect(data_dir) as con:
            cur = con.execute(
                'DELETE FROM schedule_entries '
                'WHERE instrument = ? AND id = ?',
                [inst, int(entry_id)],
            )
            con.commit()
    return int(cur.rowcount or 0) > 0


# =============================================================================
# Define stats helpers
# =============================================================================
def get_stats_visibility_map(
    data_dir: Path,
    instrument: str,
) -> Dict[str, bool]:
    inst = _norm_instrument(instrument)
    with _connect(data_dir) as con:
        rows = con.execute(
            'SELECT username, visible FROM schedule_stats_visibility '
            'WHERE instrument = ?',
            [inst],
        ).fetchall()
    out: Dict[str, bool] = dict()
    for row in rows:
        out[str(row['username'])] = bool(int(row['visible']))
    return out


def set_stats_user_visibility(
    data_dir: Path,
    instrument: str,
    username: str,
    visible: bool,
    updated_by: str,
) -> None:
    inst = _norm_instrument(instrument)
    uname = _norm_text(username)
    if not uname:
        raise ValueError('username is required')
    now = _utc_now()
    with _LOCK:
        with _connect(data_dir) as con:
            con.execute(
                'INSERT INTO schedule_stats_visibility ('
                ' instrument, username, visible, updated_by, updated_at'
                ') VALUES (?, ?, ?, ?, ?) '
                'ON CONFLICT(instrument, username) DO UPDATE SET '
                ' visible = excluded.visible,'
                ' updated_by = excluded.updated_by,'
                ' updated_at = excluded.updated_at',
                [inst, uname, 1 if visible else 0,
                 _norm_text(updated_by) or 'system', now],
            )
            con.commit()


def compute_stats(
    data_dir: Path,
    instrument: str,
    since: str,
    until: str,
    task: str = '',
) -> Dict:
    since_day = _parse_date(since)
    until_day = _parse_date(until)
    if since_day is None or until_day is None:
        raise ValueError('since and until must be valid ISO dates')
    if since_day > until_day:
        raise ValueError('since must be <= until')
    today = date.today()
    inst = _norm_instrument(instrument)
    task_name = _norm_text(task)

    query = (
        'SELECT username, who, task, date_start, date_end, hours '
        'FROM schedule_entries '
        'WHERE instrument = ? AND date_end >= ? AND date_start <= ?'
    )
    args: List = [inst, since_day.isoformat(), until_day.isoformat()]
    if task_name and task_name.lower() != 'all':
        query += ' AND task = ?'
        args.append(task_name)
    query += ' ORDER BY username ASC, date_start ASC'

    with _connect(data_dir) as con:
        rows = con.execute(query, args).fetchall()

    by_user: Dict[str, Dict] = dict()
    for row in rows:
        username = _norm_text(row['username'])
        who_name = _norm_text(row['who'])
        start_day = _parse_date(row['date_start'])
        end_day = _parse_date(row['date_end'])
        if start_day is None or end_day is None:
            continue
        overlap = _days_overlap(start_day, end_day, since_day, until_day)
        if overlap <= 0:
            continue
        try:
            hour_val = float(row['hours'] or 0.0)
        except Exception:
            hour_val = 0.0

        item = by_user.get(username)
        if item is None:
            item = {
                'username': username,
                'who': who_name,
                'days_completed': 0,
                'days_proposed': 0,
                'total_days': 0,
                'hours_estimated': 0.0,
            }
            by_user[username] = item

        if end_day < today:
            item['days_completed'] += overlap
        else:
            item['days_proposed'] += overlap
        item['total_days'] = (
            int(item['days_completed']) + int(item['days_proposed'])
        )
        item['hours_estimated'] += hour_val

    rows_out = list(by_user.values())
    rows_out.sort(key=lambda item: item['username'].lower())

    ratios = []
    for item in rows_out:
        if item['days_completed'] > 0:
            ratios.append(item['hours_estimated'] / item['days_completed'])
    mean_hours_day = (sum(ratios) / len(ratios)) if ratios else 0.0

    summary = {
        'avg_hours_per_day_completed': mean_hours_day,
        'avg_hours_per_week_completed': mean_hours_day * 7.0,
    }
    return {
        'rows': rows_out,
        'summary': summary,
    }


# =============================================================================
# Define calendar helpers
# =============================================================================
def week_window(anchor: str, offset_weeks: int = 0) -> Dict[str, str]:
    anchor_day = _parse_date(anchor) or date.today()
    start = anchor_day - timedelta(days=anchor_day.weekday())
    start = start + timedelta(days=7 * int(offset_weeks or 0))
    end = start + timedelta(days=6)
    return {
        'week_start': start.isoformat(),
        'week_end': end.isoformat(),
    }


def month_window(anchor: str, offset_months: int = 0) -> Dict[str, str]:
    anchor_day = _parse_date(anchor) or date.today()
    first = anchor_day.replace(day=1)
    month_index = (first.year * 12 + first.month - 1) + int(offset_months)
    year = month_index // 12
    month = (month_index % 12) + 1
    month_start = date(year, month, 1)
    if month == 12:
        next_start = date(year + 1, 1, 1)
    else:
        next_start = date(year, month + 1, 1)
    month_end = next_start - timedelta(days=1)
    return {
        'month_start': month_start.isoformat(),
        'month_end': month_end.isoformat(),
    }


def week_calendar_rows(
    data_dir: Path,
    instrument: str,
    week_start: str,
) -> Dict:
    start_day = _parse_date(week_start)
    if start_day is None:
        start_day = date.today() - timedelta(days=date.today().weekday())
    end_day = start_day + timedelta(days=6)

    rows = list_entries_overlap(data_dir, instrument, start_day, end_day)
    by_day: Dict[str, List[Dict]] = dict()
    for idx in range(7):
        day = start_day + timedelta(days=idx)
        by_day[day.isoformat()] = []

    for row in rows:
        row_start = _parse_date(row.get('date_start', ''))
        row_end = _parse_date(row.get('date_end', ''))
        if row_start is None or row_end is None:
            continue
        for idx in range(7):
            day = start_day + timedelta(days=idx)
            if row_start <= day <= row_end:
                by_day[day.isoformat()].append(dict(row))

    return {
        'week_start': start_day.isoformat(),
        'week_end': end_day.isoformat(),
        'days': by_day,
    }


def month_calendar_rows(
    data_dir: Path,
    instrument: str,
    month_start: str,
) -> Dict:
    bounds = month_window(month_start, 0)
    month_day = _parse_date(bounds['month_start'])
    if month_day is None:
        month_day = date.today().replace(day=1)
    month_end = _parse_date(bounds['month_end'])
    if month_end is None:
        month_end = month_day

    grid_start = month_day - timedelta(days=month_day.weekday())
    grid_end = month_end + timedelta(days=(6 - month_end.weekday()))

    rows = list_entries_overlap(data_dir, instrument, grid_start, grid_end)
    by_day: Dict[str, List[Dict]] = dict()
    day_cursor = grid_start
    while day_cursor <= grid_end:
        by_day[day_cursor.isoformat()] = []
        day_cursor += timedelta(days=1)

    for row in rows:
        row_start = _parse_date(row.get('date_start', ''))
        row_end = _parse_date(row.get('date_end', ''))
        if row_start is None or row_end is None:
            continue
        day_cursor = max(row_start, grid_start)
        while day_cursor <= min(row_end, grid_end):
            key = day_cursor.isoformat()
            if key in by_day:
                by_day[key].append(dict(row))
            day_cursor += timedelta(days=1)

    weeks: List[List[Dict]] = []
    week_days: List[Dict] = []
    day_cursor = grid_start
    while day_cursor <= grid_end:
        key = day_cursor.isoformat()
        week_days.append({
            'date': key,
            'in_month': (month_day <= day_cursor <= month_end),
            'entries': by_day.get(key, []),
        })
        if len(week_days) == 7:
            weeks.append(week_days)
            week_days = []
        day_cursor += timedelta(days=1)

    return {
        'month_start': month_day.isoformat(),
        'month_end': month_end.isoformat(),
        'grid_start': grid_start.isoformat(),
        'grid_end': grid_end.isoformat(),
        'weeks': weeks,
    }


_DAY_ABBR = [
    'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
]


def weeks_calendar_rows(
    data_dir: Path,
    instrument: str,
    week_start: str,
    weeks: int = 13,
    week_start_day: int = 0,
) -> Dict:
    """Return calendar data for *weeks* consecutive weeks.

    week_start_day: 0 = Monday … 6 = Sunday (ISO weekday).
    """
    wsd = int(week_start_day) % 7
    start_day = _parse_date(week_start)
    if start_day is None:
        today = date.today()
        shift = (today.weekday() - wsd) % 7
        start_day = today - timedelta(days=shift)
    else:
        shift = (start_day.weekday() - wsd) % 7
        start_day = start_day - timedelta(days=shift)

    try:
        week_count = int(weeks)
    except Exception:
        week_count = 13
    week_count = max(1, min(52, week_count))
    end_day = start_day + timedelta(days=week_count * 7 - 1)

    month_anchor = start_day + timedelta(days=7)
    target_start = month_anchor.replace(day=1)
    month_index = (
        target_start.year * 12 + target_start.month - 1 + 2
    )
    year = month_index // 12
    month = (month_index % 12) + 1
    if month == 12:
        target_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        target_end = (
            date(year, month + 1, 1) - timedelta(days=1)
        )

    rows = list_entries_overlap(
        data_dir, instrument, start_day, end_day
    )
    # Pre-parse entry dates once
    parsed_rows = []
    for row in rows:
        rs = _parse_date(row.get('date_start', ''))
        re = _parse_date(row.get('date_end', ''))
        if rs is not None and re is not None:
            parsed_rows.append((rs, re, row))

    weeks_out: List[Dict] = []
    for index in range(week_count):
        wk_start = start_day + timedelta(days=index * 7)
        wk_end = wk_start + timedelta(days=6)

        week_rows = [
            dict(r) for rs, re, r in parsed_rows
            if not (re < wk_start or rs > wk_end)
        ]

        # Build per-day entry list
        days_list: List[Dict] = []
        for d_idx in range(7):
            day = wk_start + timedelta(days=d_idx)
            day_entries = [
                dict(r) for rs, re, r in parsed_rows
                if rs <= day <= re
            ]
            days_list.append({
                'date': day.isoformat(),
                'entries': day_entries,
            })

        overlap = (
            (wk_start < target_start)
            or (wk_end > target_end)
        )
        weeks_out.append({
            'week_start': wk_start.isoformat(),
            'week_end': wk_end.isoformat(),
            'overlap_months': overlap,
            'entries': week_rows,
            'days': days_list,
        })

    day_headers = [
        _DAY_ABBR[(wsd + i) % 7] for i in range(7)
    ]
    return {
        'week_start': start_day.isoformat(),
        'week_end': end_day.isoformat(),
        'weeks': weeks_out,
        'target_start': target_start.isoformat(),
        'target_end': target_end.isoformat(),
        'day_headers': day_headers,
        'week_start_day': wsd,
    }
