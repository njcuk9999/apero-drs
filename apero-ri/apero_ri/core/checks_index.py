#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Per-profile APERO checks index.

Maintains a local-disk JSON index of check states for every obsdir in a
profile's checks root.  The index lets the policy build skip reading
unchanged YAML files (incremental scan) and provides O(1) check-results
queries.

Index location:   ``~/.ari/cache/checks_index_{profile_id}.json``
Lock file:        ``~/.ari/cache/checks_index_{profile_id}.lock``

Concurrency model
-----------------
Multiple Flask workers and the background task runner may write to the
same YAML files simultaneously.  The index uses:

* ``fcntl.flock(LOCK_EX)`` for cross-process mutual exclusion during writes
  (same approach already used by ``core/task_runner.py``).
* A module-level ``threading.Lock`` for in-process protection.

Reads are lock-free (the JSON is written atomically via temp-file + rename,
so readers always see a consistent snapshot).
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import fcntl as _fcntl
    _HAS_FCNTL = True
except ImportError:
    _HAS_FCNTL = False   # Windows fallback (not used in production)

__NAME__ = 'apero_ri.core.checks_index'

# ── Schema version — bump when the stored format changes ─────────────────────
_SCHEMA = '20260604a'

# Maximum age of an index file we will still use without a full rebuild.
_INDEX_MAX_AGE_S = 7 * 24 * 3600   # 7 days

# In-process lock guards the load → mutate → save cycle.
_INDEX_LOCK = threading.Lock()


# =============================================================================
# Path helpers
# =============================================================================
def _ari_dir() -> Path:
    env = os.environ.get('ARI_DIR')
    return Path(env).expanduser() if env else Path.home() / '.ari'


def _index_path(profile_id: str) -> Path:
    safe = str(profile_id or 'default').replace('/', '_').replace('\\', '_')
    return _ari_dir() / 'cache' / ('checks_index_%s.json' % safe)


def _lock_path(profile_id: str) -> Path:
    return _index_path(profile_id).with_suffix('.lock')


# =============================================================================
# File locking
# =============================================================================
class _FileLock:
    """Context manager: acquires an exclusive cross-process file lock."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._fh = None

    def __enter__(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._path, 'w')
        if _HAS_FCNTL:
            _fcntl.flock(self._fh, _fcntl.LOCK_EX)
        return self

    def __exit__(self, *_):
        if self._fh:
            if _HAS_FCNTL:
                _fcntl.flock(self._fh, _fcntl.LOCK_UN)
            self._fh.close()
            self._fh = None


# =============================================================================
# Index I/O
# =============================================================================
def _load_raw(profile_id: str) -> Optional[Dict[str, Any]]:
    """Load the index JSON without validation (returns None on any error)."""
    path = _index_path(profile_id)
    if not path.is_file():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return None
        if data.get('schema') != _SCHEMA:
            return None
        return data
    except Exception:
        return None


def load_index(profile_id: str) -> Dict[str, Any]:
    """Load the index for one profile.

    :return: dict with ``entries`` mapping obsdir → obsdir_record, or an
             empty index when no valid file exists.
    """
    data = _load_raw(profile_id)
    if data is None:
        return _empty_index(profile_id)
    age = time.time() - float(data.get('built_at') or 0.0)
    if age > _INDEX_MAX_AGE_S:
        return _empty_index(profile_id)
    if not isinstance(data.get('entries'), dict):
        data['entries'] = {}
    return data


def _empty_index(profile_id: str) -> Dict[str, Any]:
    return {
        'schema': _SCHEMA,
        'profile_id': profile_id,
        'built_at': 0.0,
        'entries': {},
    }


def _save_index(profile_id: str, data: Dict[str, Any]) -> None:
    """Atomically persist the index JSON (must be called under the lock)."""
    path = _index_path(profile_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    data['schema'] = _SCHEMA
    data['built_at'] = time.time()
    tmp = path.with_suffix('.tmp')
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, separators=(',', ':'))
    tmp.replace(path)


# =============================================================================
# Obsdir record helpers
# =============================================================================
def _make_obsdir_record(
    mtime_ns: int,
    card_color: str,
    check_states: Dict[str, str],
) -> Dict[str, Any]:
    """Return a compact per-obsdir index record."""
    return {
        'm': mtime_ns,           # st_mtime_ns for invalidation
        'c': card_color,         # e.g. 'failed', 'ok', 'overridden', 'monitored'
        's': check_states,       # {check_key: state}
    }


def _obsdir_mtime_ns(yaml_path: Path) -> int:
    try:
        return int(yaml_path.stat().st_mtime_ns)
    except Exception:
        return 0


def _record_from_loaded(
    mtime_ns: int,
    loaded: Dict[str, Any],
    ignored_set: Set[str],
) -> Dict[str, Any]:
    """Build an obsdir index record from a normalised ``load_check_file`` dict.

    ``loaded`` is the dict returned by ``apero_checks.load_check_file`` AFTER
    ``propagate_dependency_states`` has been applied.
    """
    from apero_ri.application.page_view_helpers import (
        _policy_obsdir_counts,
        _row_state,
    )

    summary = _policy_obsdir_counts(loaded, ignored_set)
    card_color = str(summary.get('card_color') or 'ok')

    check_states: Dict[str, str] = {}
    for bucket in ('failures', 'passes'):
        bucket_data = loaded.get(bucket) or {}
        if not isinstance(bucket_data, dict):
            continue
        for ck, row in bucket_data.items():
            if not isinstance(row, dict) or ck in ignored_set:
                continue
            check_states[ck] = _row_state(bucket, row)

    return _make_obsdir_record(mtime_ns, card_color, check_states)


# =============================================================================
# Public API
# =============================================================================
def update_obsdir(
    profile_id: str,
    obsdir: str,
    yaml_path: Path,
    loaded: Dict[str, Any],
    ignored_set: Optional[Set[str]] = None,
) -> None:
    """Update or insert one obsdir entry in the index.

    Called after any YAML mutation (override, monitor, check run).  Acquires
    the cross-process file lock and the in-process lock for the duration of
    the read-modify-write cycle.

    :param profile_id: Profile identifier (index file key).
    :param obsdir: Obsdir name (YAML stem).
    :param yaml_path: Path to the YAML file on disk.
    :param loaded: Normalised dict from ``load_check_file`` (after propagation).
    :param ignored_set: Check keys to exclude from the index entry.
    """
    mtime_ns = _obsdir_mtime_ns(yaml_path)
    record = _record_from_loaded(mtime_ns, loaded, set(ignored_set or []))
    with _INDEX_LOCK, _FileLock(_lock_path(profile_id)):
        data = _load_raw(profile_id) or _empty_index(profile_id)
        if not isinstance(data.get('entries'), dict):
            data['entries'] = {}
        data['entries'][obsdir] = record
        _save_index(profile_id, data)


def delete_obsdir(profile_id: str, obsdir: str) -> None:
    """Remove one obsdir entry from the index (after YAML deletion).

    :param profile_id: Profile identifier.
    :param obsdir: Obsdir name to remove.
    """
    with _INDEX_LOCK, _FileLock(_lock_path(profile_id)):
        data = _load_raw(profile_id)
        if data is None:
            return
        entries = data.get('entries')
        if isinstance(entries, dict) and obsdir in entries:
            del entries[obsdir]
            _save_index(profile_id, data)


def delete_all_obsdirs(profile_id: str) -> None:
    """Wipe all entries for one profile (e.g. after a clean reset).

    :param profile_id: Profile identifier.
    """
    with _INDEX_LOCK, _FileLock(_lock_path(profile_id)):
        data = _empty_index(profile_id)
        _save_index(profile_id, data)


def invalidate_index(profile_id: str) -> None:
    """Delete the index file entirely, forcing a full rebuild on next scan."""
    path = _index_path(profile_id)
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


def get_check_results(
    profile_id: str,
    check_key: str,
    state_filter: str,
) -> List[Dict[str, str]]:
    """Return all obsdir names for one check+state without any file I/O.

    :return: list of ``{'obsdir': str}`` dicts sorted alphabetically,
             or an empty list when the index does not exist yet.
    """
    data = _load_raw(profile_id)
    if data is None:
        return []
    entries = data.get('entries') or {}
    out = []
    for obsdir, record in entries.items():
        states = record.get('s') or {}
        if states.get(check_key) == state_filter:
            out.append({'obsdir': obsdir})
    out.sort(key=lambda r: r['obsdir'])
    return out


def incremental_update(
    profile_id: str,
    checks_root: Path,
    loaded_cache: Dict[str, Dict[str, Any]],
    ignored_set: Set[str],
    checks_registry: Dict[str, Any],
) -> Tuple[Dict[str, Any], int, int]:
    """Incrementally update the index for one profile root.

    Compares stored mtime values against the filesystem.  Only YAML files
    that are new or modified are loaded; unchanged files reuse the cached
    record.  Returns the rebuilt index data plus counters.

    :param profile_id: Profile identifier.
    :param checks_root: Path to the profile's checks directory.
    :param loaded_cache: Mutable dict — caller MAY pre-populate it or pass
                         ``{}``; this function fills it with newly loaded
                         dicts keyed by Path.
    :param ignored_set: Check keys to exclude.
    :param checks_registry: ``MONITOR_CHECKS`` for dependency propagation.
    :return: ``(updated_index_data, n_from_disk, n_from_cache)``
    """
    from apero_ri.core import apero_checks as _ac

    with _INDEX_LOCK, _FileLock(_lock_path(profile_id)):
        data = _load_raw(profile_id) or _empty_index(profile_id)
        if not isinstance(data.get('entries'), dict):
            data['entries'] = {}
        old_entries: Dict[str, Any] = dict(data['entries'])
        new_entries: Dict[str, Any] = {}

        yaml_files = sorted(checks_root.glob('*.yaml'))
        n_disk = 0
        n_cache = 0

        for yaml_path in yaml_files:
            obsdir = yaml_path.stem
            mtime_ns = _obsdir_mtime_ns(yaml_path)
            cached = old_entries.get(obsdir)

            if cached and cached.get('m') == mtime_ns:
                # File unchanged — reuse cached record.
                new_entries[obsdir] = cached
                n_cache += 1
                continue

            # File is new or modified — read from disk.
            n_disk += 1
            try:
                loaded = _ac.load_check_file(yaml_path)
                _ac.propagate_dependency_states(
                    loaded, checks_registry, ignored_set
                )
                loaded_cache[yaml_path] = loaded
            except Exception:
                continue
            new_entries[obsdir] = _record_from_loaded(
                mtime_ns, loaded, ignored_set
            )

        data['entries'] = new_entries
        _save_index(profile_id, data)

    return data, n_disk, n_cache
