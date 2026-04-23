#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Issues subsystem (YAML-backed).

Stores user-flagged issues and target-add requests in a single
file at ``<data_dir>/shared/issues.yaml``.  Each issue is a dict
with the keys::

    id            : int (1-based, monotonically increasing)
    created_at    : ISO-8601 UTC timestamp
    created_by    : username (or 'anonymous')
    assigned_to   : str | null  (username assigned to handle the
                    issue; null = unassigned)
    kind          : 'astrometric' | 'flag' | 'target_request'
                    | 'ari' | 'other' (broad category)
    type          : str | null  (sub-category, e.g.
                    'variable flag', 'new object')
    title         : str | null  (one-line summary; if absent it is
                    synthesised on read from apero_name/field/value)
    origin_url    : str | null  (URL the user was on when filing;
                    used by the 'Go' action button on the issues
                    list)
    apero_name    : str | null
    field         : str | null  (yaml key being flagged)
    value         : Any | null  (current value)
    instrument    : str | null
    profile_id    : str | null
    visibility    : 'public' | 'monitor' | 'admin'
    status        : 'open' | 'resolved' | 'invalid'
    reason        : str  (free-form description)
    notes         : list[{author, text, created_at}]

The store is thread-safe via a simple file-level lock.

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


__NAME__ = 'apero_ri.core.issues'

# in-process lock to avoid concurrent writes
_LOCK = threading.Lock()


def _store_path(data_dir: Path) -> Path:
    """Return the on-disk path of the issues store.

    :param data_dir: Path, the ARI data directory
    :return: Path to the issues yaml file (parent created on demand)
    """
    p = Path(data_dir) / 'shared' / 'issues.yaml'
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load(data_dir: Path) -> List[Dict[str, Any]]:
    """Load all issues from disk; returns ``[]`` if the file is absent.

    :param data_dir: Path, the ARI data directory
    :return: list of issue dicts
    """
    import yaml as _yaml
    p = _store_path(data_dir)
    if not p.exists():
        return []
    try:
        with p.open('r', encoding='utf-8') as fh:
            data = _yaml.safe_load(fh) or []
        if isinstance(data, list):
            return data
    except Exception:  # noqa: BLE001
        pass
    return []


def _save(data_dir: Path,
          issues: List[Dict[str, Any]]) -> None:
    """Persist *issues* to the YAML store atomically.

    :param data_dir: Path, the ARI data directory
    :param issues: list of issue dicts to write
    """
    import yaml as _yaml
    p = _store_path(data_dir)
    tmp = p.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8') as fh:
        _yaml.safe_dump(
            issues, fh, sort_keys=False, allow_unicode=True)
    tmp.replace(p)


def _ensure_title(it: Dict[str, Any]) -> None:
    """Backfill ``title`` (and ``type`` defaults) on a legacy issue.

    Older issues stored before the title/type columns existed use a
    synthesised title built from ``apero_name``/``field``/``value``
    so the new UI can still render them sensibly.
    """
    if not it.get('title'):
        apero = it.get('apero_name')
        field = it.get('field')
        value = it.get('value')
        bits = []
        if apero:
            bits.append(f'Object: {apero}')
        if field:
            bits.append(f'Field: {field}')
        if value not in (None, ''):
            bits.append(f'value: {value}')
        if bits:
            it['title'] = ' '.join(bits)
        else:
            it['title'] = (it.get('reason') or '').strip()[:80]
    if 'type' not in it:
        # legacy 'flag' on an astrometric field -> variable flag
        if (it.get('kind') == 'flag' and it.get('field')
                and it.get('apero_name')):
            it['type'] = 'variable flag'
        elif it.get('kind') == 'target_request':
            it['type'] = 'new object'
        else:
            it['type'] = ''
    if 'origin_url' not in it:
        it['origin_url'] = ''
    if 'assigned_to' not in it:
        it['assigned_to'] = None


def list_issues(
        data_dir: Path,
        visibility: str = 'public',
        status: Optional[str] = None,
        instrument: Optional[str] = None,
        kind: Optional[str] = None,
        type_: Optional[str] = None,
        created_by: Optional[str] = None,
        assigned_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List issues filtered by visibility, status, instrument, kind.

    :param data_dir: Path, the ARI data directory
    :param visibility: caller's visibility level - returns issues at
                       this level or lower (public < monitor < admin)
    :param status: optional status filter ('open', 'resolved', ...)
    :param instrument: optional instrument filter (or '*' for global)
    :param kind: optional kind filter
    :param type_: optional type sub-filter (e.g. 'variable flag')
    :param created_by: optional filter on the submitter username
    :param assigned_to: optional filter on the assignee username;
                        the special value ``'__none__'`` matches
                        unassigned issues
    :return: list of matching issue dicts
    """
    rank = {'public': 0, 'monitor': 1, 'admin': 2}
    cutoff = rank.get(visibility, 0)
    out = []
    for it in _load(data_dir):
        v = it.get('visibility', 'public')
        if rank.get(v, 0) > cutoff:
            continue
        if status and it.get('status') != status:
            continue
        if kind and it.get('kind') != kind:
            continue
        _ensure_title(it)
        if type_ and (it.get('type') or '') != type_:
            continue
        if created_by and (it.get('created_by') or '') != created_by:
            continue
        if assigned_to:
            current_assignee = (it.get('assigned_to') or '').strip()
            if assigned_to == '__none__':
                if current_assignee:
                    continue
            elif current_assignee != assigned_to:
                continue
        if instrument:
            inst = it.get('instrument') or '*'
            if inst not in (instrument, '*'):
                continue
        out.append(it)
    return out


def create_issue(
        data_dir: Path,
        kind: str,
        reason: str,
        created_by: str = 'anonymous',
        apero_name: Optional[str] = None,
        field: Optional[str] = None,
        value: Any = None,
        instrument: Optional[str] = None,
        profile_id: Optional[str] = None,
        visibility: str = 'public',
        title: Optional[str] = None,
        type_: Optional[str] = None,
        origin_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Append a new issue to the store and return it.

    :param data_dir: Path, the ARI data directory
    :param kind: str, one of ``'flag'``, ``'target_request'``,
                 ``'other'``
    :param reason: str, free-form reason / description
    :param created_by: str, username (default ``'anonymous'``)
    :param apero_name: str or None, the canonical name involved
    :param field: str or None, the yaml key being flagged
    :param value: Any, the current value of the flagged field
    :param instrument: str or None, instrument scope
    :param profile_id: str or None, profile scope
    :param visibility: ``'public'``, ``'monitor'`` or ``'admin'``
    :return: the created issue dict (with ``id`` assigned)
    """
    with _LOCK:
        issues = _load(data_dir)
        next_id = (max((it.get('id') or 0)
                       for it in issues) + 1) if issues else 1
        issue = {
            'id': next_id,
            'created_at': datetime.now(
                timezone.utc).isoformat(timespec='seconds'),
            'created_by': str(created_by or 'anonymous'),
            'assigned_to': None,
            'kind': kind,
            'type': str(type_ or ''),
            'title': str(title or '').strip() or None,
            'origin_url': str(origin_url or '') or None,
            'apero_name': apero_name,
            'field': field,
            'value': value,
            'instrument': instrument,
            'profile_id': profile_id,
            'visibility': visibility,
            'status': 'open',
            'reason': str(reason or ''),
            'notes': [],
        }
        _ensure_title(issue)
        issues.append(issue)
        _save(data_dir, issues)
        return issue


def update_issue(
        data_dir: Path,
        issue_id: int,
        status: Optional[str] = None,
        note: Optional[str] = None,
        author: Optional[str] = None,
        assigned_to: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Update status or append a note on an existing issue.

    :param data_dir: Path, the ARI data directory
    :param issue_id: int, the id of the issue to update
    :param status: str or None, new status (e.g. ``'resolved'``)
    :param note: str or None, free-form note to append
    :param author: str or None, username for the note
    :param assigned_to: str or None; pass ``''`` to clear, a
                        username to assign, or ``None`` to leave
                        the current assignee untouched
    :return: updated issue dict or None if not found
    """
    with _LOCK:
        issues = _load(data_dir)
        target = None
        for it in issues:
            if it.get('id') == issue_id:
                target = it
                break
        if target is None:
            return None
        old_assignee = target.get('assigned_to')
        if status:
            target['status'] = status
        if assigned_to is not None:
            target['assigned_to'] = (str(assigned_to).strip()
                                     or None)
        if note:
            target.setdefault('notes', []).append({
                'author': str(author or 'anonymous'),
                'text': str(note),
                'created_at': datetime.now(
                    timezone.utc).isoformat(timespec='seconds'),
            })
        _save(data_dir, issues)
        new_assignee = target.get('assigned_to')
        # Sync the assignee's user-portal todo list.
        try:
            from apero_ri.core import user_data as _ud
            if old_assignee and old_assignee != new_assignee:
                _ud.remove_issue_todo(old_assignee, target['id'])
            if new_assignee:
                _ud.upsert_issue_todo(new_assignee, target)
        except Exception:
            pass
        return target
