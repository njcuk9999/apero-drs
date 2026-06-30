#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI rejection-list API helpers."""

from __future__ import annotations

import contextlib
import io
import json
from datetime import datetime
from pathlib import Path
from typing import List
from typing import Optional

import pandas as pd
from flask import jsonify
from flask import request

from apero_ri.application.astrometrics_api_helpers import _has_monitor_perm
from apero_ri.core.auth import user_has_admin_privileges
from apero_ri.core.permissions import load_parameters
from apero_ri.core.permissions import resolve_user_permissions


# =============================================================================
# Define variables
# =============================================================================
HISTORY_DIRNAME = '.rejection_history'
HISTORY_FILENAME = 'rejection_list.jsonl'
HISTORY_LOCKNAME = 'rejection_list.lock'
DEFAULT_SYNC_USER = 'googlesheet'


# =============================================================================
# Define functions
# =============================================================================
def _rejection_mod():
    """Return the DRS rejection module."""
    from apero.core import drs_rejection

    return drs_rejection


def _local_data_dir(app) -> Path:
    """Return the configured local ARI data directory."""
    return Path(app._resolve_local_data_dir())


def _assets_dir(app) -> Path:
    """Return the local apero-assets directory."""
    return _local_data_dir(app) / 'apero-assets'


def _history_path(app) -> Path:
    """Return the shared rejection-history file path."""
    return _assets_dir(app) / HISTORY_DIRNAME / HISTORY_FILENAME


def _history_lock(app):
    """Return the cross-process lock for the history JSONL file."""
    mod = _rejection_mod()
    lockpath = _assets_dir(app) / HISTORY_DIRNAME / HISTORY_LOCKNAME
    return mod._FileLock(str(lockpath))


def _configured_tab_map() -> dict:
    """Return the configured logical-tab to asset-dir mapping."""
    params = load_parameters() or {}
    raw_map = params.get('instrument_map', {})
    out = dict()
    if isinstance(raw_map, dict):
        for key, value in raw_map.items():
            tab_key = str(key or '').strip().lower()
            if not tab_key:
                continue
            if isinstance(value, dict):
                raw_dirs = value.get('value', [])
            elif isinstance(value, list):
                raw_dirs = value
            else:
                raw_dirs = [value]
            dirs = []
            for item in raw_dirs:
                asset_dir = str(item or '').strip().lower()
                if asset_dir:
                    dirs.append(asset_dir)
            if dirs:
                out[tab_key] = dirs
    if out:
        return out
    instruments = params.get('instruments', {})
    if isinstance(instruments, dict):
        raw_instruments = instruments.get('value', [])
    elif isinstance(instruments, list):
        raw_instruments = instruments
    else:
        raw_instruments = []
    for item in raw_instruments:
        name = str(item or '').strip().lower()
        if name:
            out[name] = [name]
    return out


def _tab_label(tab_key: str) -> str:
    """Return the human-readable label for one tab key."""
    return str(tab_key or '').strip().replace('_', '-').upper()


def _expanded_tabs() -> List[dict]:
    """Return one tab entry per mapped asset directory."""
    tab_map = _configured_tab_map()
    tabs = []
    for perm_key in sorted(tab_map):
        targets = tab_map[perm_key]
        for target in targets:
            row = dict()
            row['key'] = target
            row['label'] = _tab_label(target)
            row['targets'] = [target]
            row['perm_key'] = perm_key
            tabs.append(row)
    return tabs


def get_rejection_tabs(perms=None) -> List[dict]:
    """Return visible rejection tabs for the current permission set."""
    tabs = []
    for row in _expanded_tabs():
        perm_label = _tab_label(row['perm_key'])
        if perms is not None and not _has_monitor_perm(perms, perm_label):
            continue
        tabs.append(dict(row))
    return tabs


def resolve_rejection_tab_key(instrument: str) -> str:
    """Resolve an instrument name to one rejection-list tab key."""
    target = str(instrument or '').strip().lower()
    if target == '':
        return ''
    for row in _expanded_tabs():
        key = str(row.get('key') or '').strip().lower()
        perm_key = str(row.get('perm_key') or '').strip().lower()
        if target in {key, perm_key}:
            return key
    return ''


def get_rejection_rows_for_tab_key(app, tab_key: str) -> List[dict]:
    """Return normalized rejection-list rows for one tab key."""
    tab = _resolve_tab(tab_key)
    if tab is None:
        return []
    _ensure_tab_metadata_backfill(app, tab)
    df = _load_tab_df(app, tab)
    rows = []
    for _, row in df.iterrows():
        rows.append(_row_to_dict(row))
    return rows


def _resolve_tab(raw_tab: str) -> Optional[dict]:
    """Resolve one logical tab from the configured map."""
    requested = str(raw_tab or '').strip().lower()
    if not requested:
        return None
    for row in _expanded_tabs():
        if row['key'] == requested:
            return dict(row)
    return None


def _csv_paths(app, tab: dict) -> List[Path]:
    """Return every reject.csv path for a logical tab."""
    mod = _rejection_mod()
    paths = []
    for target in tab['targets']:
        path = _assets_dir(app) / target / mod.REJECT_SUBDIR / mod.REJECT_CSV
        paths.append(path)
    return paths


def _read_df(csv_path: Path) -> pd.DataFrame:
    """Read one reject CSV into a normalized DataFrame."""
    mod = _rejection_mod()
    return mod._read_csv(str(csv_path))


def _write_df(csv_path: Path, df: pd.DataFrame) -> None:
    """Persist one reject DataFrame to disk."""
    mod = _rejection_mod()
    mod._write_csv(str(csv_path), df)


def _file_lock(csv_path: Path):
    """Return the cross-process lock for one reject CSV."""
    mod = _rejection_mod()
    lockdir = csv_path.parent / mod.LOCK_SUBDIR
    lockpath = lockdir / 'reject.lock'
    return mod._FileLock(str(lockpath))


def _lock_all(paths: List[Path]):
    """Acquire locks for all mapped CSV paths in stable order."""
    stack = contextlib.ExitStack()
    for path in sorted(paths, key=lambda item: str(item)):
        stack.enter_context(_file_lock(path))
    return stack


def _empty_df() -> pd.DataFrame:
    """Return an empty rejection table."""
    mod = _rejection_mod()
    return pd.DataFrame(columns=mod.CSV_COLUMNS)


def _utcnow_iso() -> str:
    """Return the current UTC timestamp in seconds precision."""
    return datetime.utcnow().isoformat(timespec='seconds')


def _normalize_metadata_frame(df: pd.DataFrame,
                              fallback_user: str,
                              fallback_time: str) -> tuple[pd.DataFrame, bool]:
    """Backfill WHO/LAST_UPDATE columns for old rejection rows."""
    if len(df) == 0:
        return df, False
    frame = df.copy()
    changed = False
    if 'WHO' not in frame.columns:
        frame['WHO'] = ''
        changed = True
    if 'LAST_UPDATE' not in frame.columns:
        frame['LAST_UPDATE'] = ''
        changed = True

    who_values = [str(value or '').strip() for value in frame['WHO'].tolist()]
    time_values = [
        str(value or '').strip()
        for value in frame['LAST_UPDATE'].tolist()
    ]
    for row_it in range(len(frame)):
        if who_values[row_it] == '':
            who_values[row_it] = str(fallback_user or DEFAULT_SYNC_USER)
            changed = True
        if time_values[row_it] == '':
            time_values[row_it] = str(fallback_time or _utcnow_iso())
            changed = True
    frame['WHO'] = who_values
    frame['LAST_UPDATE'] = time_values
    return frame, changed


def _ensure_tab_metadata_backfill(app, tab: dict) -> None:
    """Ensure legacy rows have WHO/LAST_UPDATE across all mapped files."""
    paths = _csv_paths(app, tab)
    now_iso = _utcnow_iso()
    with _lock_all(paths):
        for path in paths:
            df = _read_df(path)
            updated_df, changed = _normalize_metadata_frame(
                df,
                DEFAULT_SYNC_USER,
                now_iso,
            )
            if changed:
                _write_df(path, updated_df)


def _parse_binary_filter(raw_value: str) -> Optional[int]:
    """Parse one optional binary list-filter value from the request."""
    value = str(raw_value or '').strip()
    if value not in ['0', '1']:
        return None
    return int(value)


def _check_user(app):
    """Return the current API user and resolved permissions."""
    user_info = app._get_api_user()
    if not user_info:
        return None, set(), (
            jsonify(success=False, error='Login required'), 401
        )
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    return user_info, perms, None


def _check_tab_perm(app, raw_tab: str):
    """Validate login, tab existence, and monitor permission."""
    user_info, perms, err = _check_user(app)
    if err is not None:
        return None, set(), None, err
    tab = _resolve_tab(raw_tab)
    if tab is None:
        return user_info, perms, None, (
            jsonify(success=False, error='Invalid instrument tab'),
            400,
        )
    perm_label = _tab_label(tab['perm_key'])
    if not _has_monitor_perm(perms, perm_label):
        return user_info, perms, tab, (
            jsonify(success=False, error='Forbidden'), 403
        )
    return user_info, perms, tab, None


def _check_history_perm(app):
    """Validate access to the global rejection history."""
    user_info, perms, err = _check_user(app)
    if err is not None:
        return None, set(), err
    allowed = 'manage.rejection_list.history' in set(perms or set())
    if not allowed:
        return user_info, perms, (
            jsonify(success=False, error='Forbidden'), 403
        )
    return user_info, perms, None


def _check_history_admin(app):
    """Validate admin-level access to history management actions."""
    user_info, perms, err = _check_history_perm(app)
    if err is not None:
        return None, set(), err
    groups = []
    if isinstance(user_info, dict):
        groups = list(user_info.get('groups', []))
    if not user_has_admin_privileges(groups):
        return user_info, perms, (
            jsonify(success=False, error='Forbidden (admin only)'),
            403,
        )
    return user_info, perms, None


def _parse_int_flag(value, default: int = 1) -> int:
    """Normalize one reject integer flag."""
    if value is None:
        return int(default)
    text = str(value).strip()
    if text == '':
        return int(default)
    lowered = text.lower()
    if lowered in {'true', 't', 'yes', 'y'}:
        return 1
    if lowered in {'false', 'f', 'no', 'n'}:
        return 0
    try:
        return int(float(text))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            'Invalid integer flag value: {0}'.format(text)
        ) from exc


def _row_payload(raw_row: dict,
                 date_added: Optional[str] = None,
                 who: Optional[str] = None,
                 last_update: Optional[str] = None) -> dict:
    """Normalize one request or CSV row into the reject schema."""
    mod = _rejection_mod()
    identifier = str(
        raw_row.get(mod.ID_COLUMN, raw_row.get('identifier', ''))
    ).strip()
    if not identifier:
        raise ValueError('IDENTIFIER is required')
    if _is_invalid_identifier(identifier):
        raise ValueError('IDENTIFIER is invalid: {0}'.format(identifier))
    payload = dict()
    payload[mod.ID_COLUMN] = identifier
    payload['DATE_ADDED'] = str(
        raw_row.get('DATE_ADDED', date_added or _utcnow_iso())
        or date_added or _utcnow_iso()
    ).strip()
    payload['WHO'] = str(
        raw_row.get('WHO', raw_row.get('who', who or ''))
        or who or ''
    ).strip()
    payload['LAST_UPDATE'] = str(
        raw_row.get('LAST_UPDATE',
                    raw_row.get('last_update', last_update or ''))
        or last_update or ''
    ).strip()
    if payload['WHO'] == '':
        payload['WHO'] = str(who or DEFAULT_SYNC_USER).strip()
    if payload['LAST_UPDATE'] == '':
        payload['LAST_UPDATE'] = str(last_update or _utcnow_iso()).strip()
    payload['PP'] = _parse_int_flag(
        raw_row.get('PP', raw_row.get('pp', 1)), 1
    )
    payload['TEL'] = _parse_int_flag(
        raw_row.get('TEL', raw_row.get('tel', 1)), 1
    )
    payload['RV'] = _parse_int_flag(
        raw_row.get('RV', raw_row.get('rv', 1)), 1
    )
    payload['USED'] = _parse_int_flag(
        raw_row.get('USED', raw_row.get('used', 1)), 1
    )
    payload['COMMENT'] = str(
        raw_row.get('COMMENT', raw_row.get('comment', '')) or ''
    ).strip()
    return payload


def _row_to_dict(row) -> dict:
    """Convert a DataFrame row to plain JSON-safe values."""
    mod = _rejection_mod()
    record = dict()
    for column in mod.CSV_COLUMNS:
        value = row.get(column, '')
        if pd.isna(value):
            value = ''
        if column in mod.INT_COLUMNS:
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = 0
        else:
            value = str(value)
        record[column] = value
    return record


def _is_invalid_identifier(identifier: str) -> bool:
    """Return True for known bad/sentinel identifier values."""
    value = str(identifier or '').strip()
    if value == '':
        return True
    low = value.lower()
    if low in {'#error!', 'error', '#n/a', 'nan', 'none', 'null'}:
        return True
    return False


def _sort_df(df: pd.DataFrame) -> pd.DataFrame:
    """Sort one rejection table for display."""
    if len(df) == 0:
        return df
    columns = [
        column for column in ['USED', 'DATE_ADDED', 'IDENTIFIER']
        if column in df.columns
    ]
    ascending = [False, False, True][:len(columns)]
    if not columns:
        return df.reset_index(drop=True)
    try:
        return df.sort_values(columns, ascending=ascending)
    except Exception:
        return df.reset_index(drop=True)


def _combine_frames(frames: List[pd.DataFrame]) -> pd.DataFrame:
    """Merge mapped reject tables into one logical unique list."""
    mod = _rejection_mod()
    if not frames:
        return _empty_df()
    merged = pd.concat(frames, ignore_index=True)
    if len(merged) == 0:
        return _empty_df()
    merged = _sort_df(merged)
    if mod.ID_COLUMN in merged.columns:
        merged = merged.drop_duplicates(
            subset=[mod.ID_COLUMN], keep='first'
        )
    return merged.reset_index(drop=True)


def _load_tab_df(app, tab: dict) -> pd.DataFrame:
    """Load and merge all reject rows for one logical tab."""
    frames = []
    for path in _csv_paths(app, tab):
        frames.append(_read_df(path))
    out = _combine_frames(frames)
    if len(out) > 0 and 'IDENTIFIER' in out.columns:
        valid = ~out['IDENTIFIER'].astype(str).map(_is_invalid_identifier)
        out = out[valid].reset_index(drop=True)
    return out


def _find_existing(df: pd.DataFrame, identifier: str) -> Optional[dict]:
    """Return the matching logical row for one identifier."""
    if len(df) == 0:
        return None
    mask = df['IDENTIFIER'].astype(str) == str(identifier)
    if len(df[mask]) == 0:
        return None
    return _row_to_dict(df[mask].iloc[0])


def _replace_all(paths: List[Path],
                 old_identifier: Optional[str],
                 payload: dict) -> None:
    """Write one logical row to every mapped reject CSV."""
    new_row = pd.DataFrame([payload])
    for path in paths:
        df = _read_df(path)
        if old_identifier:
            old_mask = df['IDENTIFIER'].astype(str) == str(old_identifier)
            df = df[~old_mask].reset_index(drop=True)
        new_mask = df['IDENTIFIER'].astype(str) == payload['IDENTIFIER']
        df = df[~new_mask].reset_index(drop=True)
        df = pd.concat([df, new_row], ignore_index=True)
        _write_df(path, df)


def _delete_all(paths: List[Path], identifier: str) -> None:
    """Delete one identifier from every mapped reject CSV."""
    for path in paths:
        df = _read_df(path)
        mask = df['IDENTIFIER'].astype(str) == str(identifier)
        df = df[~mask].reset_index(drop=True)
        _write_df(path, df)


def _diff_fields(before, after) -> List[str]:
    """Return the changed top-level fields between two rows."""
    keys = set()
    if isinstance(before, dict):
        keys.update(before.keys())
    if isinstance(after, dict):
        keys.update(after.keys())
    out = []
    for key in sorted(keys):
        before_value = None if before is None else before.get(key)
        after_value = None if after is None else after.get(key)
        if before_value != after_value:
            out.append(key)
    return out


def append_history(app,
                   instrument: str,
                   user: str,
                   action: str,
                   before: Optional[dict],
                   after: Optional[dict]) -> Optional[str]:
    """Append one shared history record for the logical tab."""
    try:
        history_path = _history_path(app)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        identifier = ''
        if isinstance(after, dict):
            identifier = str(after.get('IDENTIFIER') or '').strip()
        if not identifier and isinstance(before, dict):
            identifier = str(before.get('IDENTIFIER') or '').strip()
        previous = ''
        if isinstance(before, dict):
            previous = str(before.get('IDENTIFIER') or '').strip()
        record = dict(
            timestamp=_utcnow_iso(),
            user=str(user or 'unknown'),
            instrument=str(instrument or ''),
            action=str(action or 'edit'),
            identifier=identifier,
            previous_identifier=previous,
            fields=_diff_fields(before, after),
            resolved=False,
            resolved_at='',
            resolved_by='',
            before=before if isinstance(before, dict) else None,
            after=after if isinstance(after, dict) else None,
        )
        with _history_lock(app):
            with history_path.open('a', encoding='utf-8') as out:
                out.write(json.dumps(record, sort_keys=False))
                out.write('\n')
            with history_path.open('r', encoding='utf-8') as inp:
                line_count = sum(1 for _ in inp)
        return '{0}::{1}'.format(
            history_path.name, max(line_count - 1, 0)
        )
    except Exception:
        return None


def _history_records(app) -> List[dict]:
    """Return all shared rejection-history records."""
    records = []
    history_path = _history_path(app)
    if not history_path.is_file():
        return records
    try:
        with history_path.open('r', encoding='utf-8') as inp:
            for line_number, raw_line in enumerate(inp):
                text = raw_line.strip()
                if not text:
                    continue
                try:
                    record = json.loads(text)
                except ValueError:
                    continue
                if not isinstance(record, dict):
                    continue
                record['resolved'] = bool(record.get('resolved', False))
                record['resolved_at'] = str(
                    record.get('resolved_at') or ''
                )
                record['resolved_by'] = str(
                    record.get('resolved_by') or ''
                )
                record['id'] = '{0}::{1}'.format(
                    history_path.name, line_number
                )
                records.append(record)
    except OSError:
        return []
    return records


def _write_history_records(app, records: List[dict]) -> None:
    """Write the full rejection-history record list back to disk."""
    history_path = _history_path(app)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open('w', encoding='utf-8') as out:
        for record in records:
            cleaned = dict(record)
            cleaned.pop('id', None)
            out.write(json.dumps(cleaned, sort_keys=False))
            out.write('\n')


def _resolve_history_record(app,
                            entry_id: str,
                            username: str) -> Optional[dict]:
    """Mark one rejection-history record as resolved."""
    resolved = None
    with _history_lock(app):
        records = _history_records(app)
        changed = False
        for record in records:
            if record.get('id') != entry_id:
                continue
            if not record.get('resolved', False):
                record['resolved'] = True
                record['resolved_at'] = _utcnow_iso()
                record['resolved_by'] = str(username or 'unknown')
                changed = True
            resolved = dict(record)
            break
        if resolved is None:
            return None
        if changed:
            _write_history_records(app, records)
    return resolved


def _history_record(app, entry_id: str) -> Optional[dict]:
    """Return one shared rejection-history record by id."""
    if '::' not in str(entry_id or ''):
        return None
    fname, _, raw_idx = str(entry_id).partition('::')
    if fname != HISTORY_FILENAME:
        return None
    try:
        index = int(raw_idx)
    except (TypeError, ValueError):
        return None
    for record in _history_records(app):
        if record.get('id') == '{0}::{1}'.format(fname, index):
            return record
    return None


def _history_identifier(row: Optional[dict]) -> str:
    """Return the identifier value from one history row snapshot."""
    if not isinstance(row, dict):
        return ''
    value = str(row.get('IDENTIFIER') or '').strip()
    return value


def _decode_upload(uploaded) -> str:
    """Decode one uploaded CSV file to text."""
    raw = uploaded.read()
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('latin-1')


def api_rejection_list_list(app):
    """List one logical rejection tab with pagination and filtering."""
    _, _, tab, err = _check_tab_perm(
        app, request.args.get('instrument', '')
    )
    if err is not None:
        return err
    _ensure_tab_metadata_backfill(app, tab)
    try:
        per_page = int(request.args.get('per_page', 50) or 50)
    except (TypeError, ValueError):
        per_page = 50
    if per_page not in (50, 100, 500):
        per_page = 50
    try:
        page = max(1, int(request.args.get('page', 1) or 1))
    except (TypeError, ValueError):
        page = 1
    sort_mode = str(
        request.args.get('sort', 'identifier_desc')
        or 'identifier_desc'
    ).strip().lower()
    query = str(request.args.get('q', '') or '').strip().lower()
    df = _load_tab_df(app, tab)
    mod = _rejection_mod()
    if query and 'IDENTIFIER' in df.columns:
        mask = df['IDENTIFIER'].astype(str).str.lower().str.contains(
            query, na=False, regex=False
        )
        df = df[mask].reset_index(drop=True)

    text_filters = dict(
        identifier='IDENTIFIER',
        who='WHO',
        last_update='LAST_UPDATE',
        comment='COMMENT',
    )
    for req_key, colname in text_filters.items():
        value = str(request.args.get(req_key, '') or '').strip().lower()
        if value == '' or colname not in df.columns:
            continue
        series = df[colname].astype(str).str.lower()
        mask = series.str.contains(value, na=False, regex=False)
        df = df[mask].reset_index(drop=True)

    for column in mod.INT_COLUMNS:
        filter_value = _parse_binary_filter(
            request.args.get(column.lower(), '')
        )
        if filter_value is None or column not in df.columns:
            continue
        series = pd.to_numeric(df[column], errors='coerce').fillna(0)
        df = df[series.astype(int) == filter_value].reset_index(drop=True)

    allowed_sorts = dict(
        identifier='IDENTIFIER',
        pp='PP',
        tel='TEL',
        rv='RV',
        used='USED',
        who='WHO',
        last_update='LAST_UPDATE',
        comment='COMMENT',
    )
    if '_' in sort_mode:
        sort_key, sort_dir = sort_mode.rsplit('_', 1)
    else:
        sort_key, sort_dir = 'identifier', 'asc'
    if sort_key not in allowed_sorts:
        sort_key = 'identifier'
    if sort_dir not in ['asc', 'desc']:
        sort_dir = 'asc'
    sort_mode = f'{sort_key}_{sort_dir}'
    sort_col = allowed_sorts.get(sort_key, 'IDENTIFIER')

    if sort_col in df.columns:
        asc = sort_dir == 'asc'
        if sort_col in mod.INT_COLUMNS:
            series = pd.to_numeric(df[sort_col], errors='coerce').fillna(0)
        else:
            series = df[sort_col].astype(str).str.lower()
        df = df.assign(_sort_key=series)
        df = df.sort_values(
            by='_sort_key',
            ascending=asc,
            kind='stable'
        ).drop(columns=['_sort_key']).reset_index(drop=True)
    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    rows = []
    for _, row in df.iloc[start:end].iterrows():
        rows.append(_row_to_dict(row))
    return jsonify(
        success=True,
        instrument=tab['key'],
        instrument_label=tab['label'],
        rows=rows,
        total=total,
        page=page,
        per_page=per_page,
        sort=sort_mode,
        pages=(total + per_page - 1) // per_page if per_page else 1,
        int_columns=list(mod.INT_COLUMNS),
    )


def api_rejection_list_add(app):
    """Add one logical rejection row across the mapped CSV files."""
    body = request.get_json(silent=True) or {}
    user_info, _, tab, err = _check_tab_perm(
        app, body.get('instrument', '')
    )
    if err is not None:
        return err
    _ensure_tab_metadata_backfill(app, tab)
    now_iso = _utcnow_iso()
    username = user_info.get('username', 'unknown')
    payload = _row_payload(body,
                           who=username,
                           last_update=now_iso)
    replace_existing = bool(body.get('replace_existing'))
    paths = _csv_paths(app, tab)
    with _lock_all(paths):
        existing = _find_existing(_load_tab_df(app, tab), payload['IDENTIFIER'])
        if existing is not None and not replace_existing:
            return jsonify(
                success=False,
                requires_confirmation=True,
                error='Identifier already exists',
                existing=existing,
                incoming=payload,
            ), 409
        _replace_all(paths, payload['IDENTIFIER'], payload)
    action = 'replace' if existing is not None else 'create'
    append_history(
        app,
        tab['key'],
        username,
        action,
        existing,
        payload,
    )
    return jsonify(success=True, instrument=tab['key'], row=payload)


def api_rejection_list_update(app):
    """Update one logical rejection row across the mapped CSV files."""
    body = request.get_json(silent=True) or {}
    user_info, _, tab, err = _check_tab_perm(
        app, body.get('instrument', '')
    )
    if err is not None:
        return err
    _ensure_tab_metadata_backfill(app, tab)
    old_identifier = str(body.get('old_identifier') or '').strip()
    if not old_identifier:
        return jsonify(
            success=False,
            error='old_identifier is required'
        ), 400
    paths = _csv_paths(app, tab)
    with _lock_all(paths):
        current = _load_tab_df(app, tab)
        before = _find_existing(current, old_identifier)
        if before is None:
            return jsonify(success=False, error='Identifier not found'), 404
        payload = _row_payload(
            body,
            before.get('DATE_ADDED'),
            who=user_info.get('username', 'unknown'),
            last_update=_utcnow_iso(),
        )
        other = _find_existing(current, payload['IDENTIFIER'])
        has_other = (
            other is not None
            and payload['IDENTIFIER'] != old_identifier
        )
        if has_other:
            return jsonify(
                success=False,
                error='Identifier already exists',
                existing=other,
            ), 409
        _replace_all(paths, old_identifier, payload)
    append_history(
        app,
        tab['key'],
        user_info.get('username', 'unknown'),
        'edit',
        before,
        payload,
    )
    return jsonify(success=True, instrument=tab['key'], row=payload)


def api_rejection_list_delete(app):
    """Delete one logical rejection row from every mapped CSV file."""
    body = request.get_json(silent=True) or {}
    user_info, _, tab, err = _check_tab_perm(
        app, body.get('instrument', '')
    )
    if err is not None:
        return err
    _ensure_tab_metadata_backfill(app, tab)
    identifier = str(body.get('identifier') or '').strip()
    if not identifier:
        return jsonify(
            success=False,
            error='identifier is required'
        ), 400
    paths = _csv_paths(app, tab)
    with _lock_all(paths):
        before = _find_existing(_load_tab_df(app, tab), identifier)
        if before is None:
            return jsonify(success=False, error='Identifier not found'), 404
        _delete_all(paths, identifier)
    append_history(
        app,
        tab['key'],
        user_info.get('username', 'unknown'),
        'delete',
        before,
        None,
    )
    return jsonify(success=True, instrument=tab['key'], identifier=identifier)


def api_rejection_list_upload(app):
    """Upload many rejection rows with explicit conflict confirmation."""
    user_info, _, tab, err = _check_tab_perm(
        app, request.form.get('instrument', '')
    )
    if err is not None:
        return err
    _ensure_tab_metadata_backfill(app, tab)
    uploaded = request.files.get('file')
    if uploaded is None:
        return jsonify(success=False, error='No file uploaded'), 400
    try:
        incoming = pd.read_csv(
            io.StringIO(_decode_upload(uploaded)), dtype=str
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400
    if len(incoming) == 0:
        return jsonify(success=False, error='CSV is empty'), 400
    rows = []
    errors = []
    now_iso = _utcnow_iso()
    username = user_info.get('username', 'unknown')
    for index, (_, row) in enumerate(incoming.iterrows(), start=2):
        try:
            rows.append(_row_payload(dict(row),
                                     who=username,
                                     last_update=now_iso))
        except ValueError as exc:
            errors.append('row {0}: {1}'.format(index, exc))
    if errors:
        return jsonify(
            success=False,
            error='CSV validation failed',
            details=errors,
        ), 400
    replace_existing = str(
        request.form.get('replace_existing', '')
    ).strip().lower() in {'1', 'true', 'yes', 'y'}
    upload_df = pd.DataFrame(rows)
    if len(upload_df) > 0:
        upload_df = upload_df.drop_duplicates(
            subset=['IDENTIFIER'], keep='last'
        ).reset_index(drop=True)
    paths = _csv_paths(app, tab)
    with _lock_all(paths):
        current = _load_tab_df(app, tab)
        conflicts = []
        for _, row in upload_df.iterrows():
            payload = _row_to_dict(row)
            existing = _find_existing(current, payload['IDENTIFIER'])
            if existing is not None:
                conflict = dict()
                conflict['existing'] = existing
                conflict['incoming'] = payload
                conflicts.append(conflict)
        if conflicts and not replace_existing:
            return jsonify(
                success=False,
                requires_confirmation=True,
                error='Some identifiers already exist',
                conflicts=conflicts,
                conflict_count=len(conflicts),
                processed=len(upload_df),
            ), 409
        added = 0
        replaced = 0
        unchanged = 0
        history_rows = []
        for _, row in upload_df.iterrows():
            payload = _row_to_dict(row)
            before = _find_existing(current, payload['IDENTIFIER'])
            if before is None:
                added += 1
                history_rows.append(('create', None, payload))
            elif before == payload:
                unchanged += 1
                continue
            else:
                replaced += 1
                history_rows.append(('replace', before, payload))
            _replace_all(paths, payload['IDENTIFIER'], payload)
            current = _load_tab_df(app, tab)
    for action, before, after in history_rows:
        append_history(
            app,
            tab['key'],
            user_info.get('username', 'unknown'),
            action,
            before,
            after,
        )
    return jsonify(
        success=True,
        instrument=tab['key'],
        added=added,
        replaced=replaced,
        unchanged=unchanged,
        processed=len(upload_df),
    )


def api_rejection_history_list(app):
    """Return the shared logical rejection history."""
    _, _, err = _check_history_perm(app)
    if err is not None:
        return err
    try:
        per_page = int(request.args.get('per_page', 50) or 50)
    except (TypeError, ValueError):
        per_page = 50
    if per_page not in (50, 100, 500):
        per_page = 50
    try:
        page = max(1, int(request.args.get('page', 1) or 1))
    except (TypeError, ValueError):
        page = 1
    query = str(request.args.get('q', '') or '').strip().lower()
    records = []
    for record in _history_records(app):
        identifier = str(record.get('identifier') or '').lower()
        previous = str(record.get('previous_identifier') or '').lower()
        instrument = str(record.get('instrument') or '').lower()
        if query and query not in identifier \
                and query not in previous \
                and query not in instrument:
            continue
        records.append(record)
    records.sort(
        key=lambda item: str(item.get('timestamp') or ''),
        reverse=True,
    )
    total = len(records)
    start = (page - 1) * per_page
    end = start + per_page
    rows = []
    for record in records[start:end]:
        row = dict()
        row['id'] = record.get('id')
        row['timestamp'] = record.get('timestamp')
        row['user'] = record.get('user')
        row['instrument'] = record.get('instrument')
        row['action'] = record.get('action')
        row['identifier'] = record.get('identifier')
        row['previous_identifier'] = (
            record.get('previous_identifier') or ''
        )
        row['fields'] = list(record.get('fields') or [])
        row['resolved'] = bool(record.get('resolved', False))
        row['resolved_at'] = str(record.get('resolved_at') or '')
        row['resolved_by'] = str(record.get('resolved_by') or '')
        rows.append(row)
    return jsonify(
        success=True,
        rows=rows,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if per_page else 1,
    )


def api_rejection_history_get(app):
    """Return one shared rejection-history record by id."""
    _, _, err = _check_history_perm(app)
    if err is not None:
        return err
    entry_id = str(
        request.args.get('id')
        or (request.get_json(silent=True) or {}).get('id')
        or ''
    ).strip()
    if not entry_id:
        return jsonify(success=False, error='Missing id'), 400
    record = _history_record(app, entry_id)
    if record is None:
        return jsonify(success=False, error='Not found'), 404
    return jsonify(success=True, entry=record)


def api_rejection_history_restore(app):
    """Restore the row state represented by one history entry."""
    user_info, _, err = _check_history_perm(app)
    if err is not None:
        return err
    body = request.get_json(silent=True) or {}
    entry_id = str(body.get('id') or '').strip()
    if not entry_id:
        return jsonify(success=False, error='Missing id'), 400
    record = _history_record(app, entry_id)
    if record is None:
        return jsonify(success=False, error='Not found'), 404
    tab = _resolve_tab(str(record.get('instrument') or ''))
    if tab is None:
        return jsonify(success=False, error='Invalid history instrument'), 400
    before_row = record.get('before')
    after_row = record.get('after')
    has_before = isinstance(before_row, dict)
    has_after = isinstance(after_row, dict)
    if not has_before and not has_after:
        return jsonify(
            success=False,
            error='History entry has no row data'
        ), 400

    payload = None
    payload_identifier = ''
    after_identifier = _history_identifier(after_row)
    before_identifier = _history_identifier(before_row)
    replace_identifier = ''
    delete_identifier = ''

    if has_before:
        payload = _row_payload(before_row, before_row.get('DATE_ADDED'))
        payload_identifier = str(payload.get('IDENTIFIER') or '').strip()
        replace_identifier = after_identifier or payload_identifier
    elif has_after:
        delete_identifier = after_identifier

    paths = _csv_paths(app, tab)
    with _lock_all(paths):
        current = _load_tab_df(app, tab)
        if payload is not None:
            before = _find_existing(current, replace_identifier)
            if before is None and replace_identifier != payload_identifier:
                before = _find_existing(current, payload_identifier)
            _replace_all(paths, replace_identifier, payload)
            restored = payload
        else:
            before = _find_existing(current, delete_identifier)
            _delete_all(paths, delete_identifier)
            restored = None

    append_history(
        app,
        tab['key'],
        user_info.get('username', 'unknown'),
        'restore',
        before,
        restored,
    )
    return jsonify(success=True, instrument=tab['key'], row=restored)


def api_rejection_history_delete(app):
    """Delete one rejection history entry by id (admin-only)."""
    _, _, err = _check_history_admin(app)
    if err is not None:
        return err
    body = request.get_json(silent=True) or {}
    entry_id = str(body.get('id') or '').strip()
    if not entry_id:
        return jsonify(success=False, error='Missing id'), 400
    with _history_lock(app):
        records = _history_records(app)
        kept = []
        found = False
        for record in records:
            if record.get('id') == entry_id:
                found = True
                continue
            kept.append(record)
        if not found:
            return jsonify(success=False, error='Not found'), 404
        _write_history_records(app, kept)
    return jsonify(success=True, deleted_id=entry_id)


def api_rejection_history_clear(app):
    """Clear all rejection history entries (admin-only)."""
    _, _, err = _check_history_admin(app)
    if err is not None:
        return err
    with _history_lock(app):
        records = _history_records(app)
        removed = len(records)
        _write_history_records(app, [])
    return jsonify(success=True, cleared_entries=removed)


def api_rejection_history_resolve(app):
    """Backward-compatible alias for history restore."""
    return api_rejection_history_restore(app)