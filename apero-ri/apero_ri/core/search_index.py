#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Durable, profile-scoped Search keys, filtered by current RUN ID access."""

import fcntl
import hashlib
import json
import logging
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

MAX_AGE = 24 * 60 * 60
SOURCES = dict(target_info='Target information',
               spectrum_info='Spectrum information', header='Header')
FTABLE_KINDS = ('raw', 'pp', 'ext', 'tcorr', 'ccf', 'lbl', 'lbl_rdb')
_LOCK = threading.Lock()
_CACHE = dict()
_REFRESHING = set()
_RETRY_AFTER = dict()
_LOGGER = logging.getLogger(__name__)


def index_path(base_dir: Path, profile: dict) -> Path:
    """Return the cache path for a data root and plain profile descriptor.

    :param base_dir: Local ARI data directory.
    :param profile: Descriptor with instrument and profile_id.
    :return: Collision-resistant profile index path.
    """
    identity = [str(profile['instrument']), str(profile['profile_id'])]
    digest = hashlib.sha256(json.dumps(identity).encode()).hexdigest()
    return Path(base_dir) / 'admin' / 'search_index' / f'{digest}.json'


def _rows(path: Path) -> list:
    """Load a table, treating absent files as empty.

    :param path: JSON table path.
    :return: Dictionary rows; malformed present files raise ValueError.
    """
    try:
        with path.open(encoding='utf-8') as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        return []
    rows = payload.get('rows', []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError(f'Invalid Search table: {path}')
    return [row for row in rows if isinstance(row, dict)]


def _run_ids(row: dict, key: str) -> set:
    """Extract run IDs from row's comma-separated key.

    :param row: Table row.
    :param key: Run ID field.
    :return: Nonempty run ID strings.
    """
    return {part.strip() for part in str(row.get(key) or '').split(',')
            if part.strip()}


def scan_profile(base_dir: Path, profile: dict) -> dict:
    """Scan every object into a run-to-source-to-key mapping.

    :param base_dir: Local ARI data root.
    :param profile: Plain instrument/profile_id descriptor.
    :return: JSON-serializable index with generation time and run keys.
    """
    tasks_dir = Path(base_dir) / 'tasks' / str(profile['instrument'])
    profile_dir = tasks_dir / str(profile['profile_id'])
    table = profile_dir / 'object_table.json'
    if not table.exists():
        table = tasks_dir / f"object_table_{profile['profile_id']}.json"
    runs = dict()

    def add(source: str, row: dict, run_ids: set) -> None:
        """Add row keys for source to each authorized-by-data run.

        :param source: Key source.
        :param row: Data row.
        :param run_ids: Associated runs.
        :return: None.
        """
        for run_id in run_ids:
            sources = runs.setdefault(run_id, dict())
            sources.setdefault(source, set()).update(map(str, row))

    objects = dict()
    for row in _rows(table):
        run_ids = _run_ids(row, 'RUN_ID')
        add('target_info', row, run_ids)
        name = str(row.get('OBJNAME') or '').strip()
        if name:
            objects.setdefault(name, set()).update(run_ids)
    for name, object_runs in objects.items():
        directory = profile_dir / 'objects'
        identifiers = dict()
        for kind in ('all',) + FTABLE_KINDS:
            for row in _rows(directory / f'ftable_{kind}_{name}.json'):
                run_ids = _run_ids(row, 'KW_RUN_ID') & object_runs
                if kind != 'all':
                    add('spectrum_info', row, run_ids)
                identifier = str(row.get('IDENTIFIER') or '').strip()
                if identifier:
                    identifiers.setdefault(identifier, set()).update(run_ids)
        for row in _rows(directory / f'htable_{name}.json'):
            run_ids = _run_ids(row, 'KW_RUN_ID')
            run_ids.update(_run_ids(row, 'RUN_ID'))
            if not run_ids:
                identifier = str(row.get('IDENTIFIER') or '').strip()
                run_ids = identifiers.get(identifier, set())
            add('header', row, run_ids & object_runs)
    serialized = dict()
    for run_id, sources in runs.items():
        serialized[run_id] = dict()
        for source, keys in sources.items():
            serialized[run_id][source] = sorted(keys)
    return dict(version=1, generated_at=time.time(), runs=serialized)


def read_index(base_dir: Path, profile: dict) -> Any:
    """Read an index, using an mtime-aware process cache.

    :param base_dir: Local ARI data root.
    :param profile: Plain profile descriptor.
    :return: Index dictionary, or None when missing or invalid.
    """
    path = index_path(base_dir, profile)
    try:
        stat = path.stat()
        signature = (stat.st_mtime_ns, stat.st_size, stat.st_ino)
        with _LOCK:
            cached = _CACHE.get(path)
            if cached and cached[0] == signature:
                return cached[1]
        with path.open(encoding='utf-8') as handle:
            index = json.load(handle)
        if index.get('version') != 1 or not isinstance(index['runs'], dict):
            return None
        float(index['generated_at'])
        with _LOCK:
            _CACHE[path] = (signature, index)
        return index
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def refresh_profile(base_dir: Path, profile: dict) -> bool:
    """Atomically replace one index, with a cross-process refresh lock.

    :param base_dir: Local ARI data root.
    :param profile: Plain profile descriptor.
    :return: True if refreshed, False if another worker owns the lock.
    """
    path = index_path(base_dir, profile)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.with_suffix('.lock').open('a') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        index = scan_profile(base_dir, profile)
        descriptor, temporary = tempfile.mkstemp(dir=path.parent)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
                json.dump(index, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        with _LOCK:
            _CACHE.pop(path, None)
    return True


def request_refresh(base_dir: Path, profile: dict) -> None:
    """Start at most one background refresh per profile in this process.

    :param base_dir: Local ARI data root.
    :param profile: Plain descriptor, with no application/user objects.
    :return: None.
    """
    path = index_path(base_dir, profile)
    with _LOCK:
        if path in _REFRESHING:
            return
        if time.monotonic() < _RETRY_AFTER.get(path, 0):
            return
        _REFRESHING.add(path)

    def worker() -> None:
        """Refresh the captured profile, retaining old data on failure."""
        try:
            index = read_index(base_dir, profile)
            if index and time.time() - index['generated_at'] < MAX_AGE:
                return
            refresh_profile(base_dir, profile)
        except Exception:
            _LOGGER.exception('Search index refresh failed')
            with _LOCK:
                _RETRY_AFTER[path] = time.monotonic() + 60
        finally:
            with _LOCK:
                _REFRESHING.discard(path)

    try:
        threading.Thread(target=worker, daemon=True).start()
    except Exception:
        with _LOCK:
            _REFRESHING.discard(path)
        raise


def catalog(base_dir: Path, profiles: list, run_access: dict,
            background: bool = False) -> dict:
    """Merge cached keys only for currently accessible profiles and runs.

    :param base_dir: Local ARI root.
    :param profiles: Current authorized plain profile descriptors.
    :param run_access: Instrument to current authorized run ID set.
    :param background: Schedule cold builds instead of blocking.
    :return: Sources, properties, instruments, and aggregate index status.
    """
    availability = dict()
    instruments = set()
    status = 'ready'
    for profile in profiles:
        instrument = str(profile.get('instrument') or '').strip()
        profile_id = str(profile.get('profile_id') or '').strip()
        allowed = run_access.get(instrument, set())
        if not instrument or not profile_id or not allowed:
            continue
        descriptor = dict(instrument=instrument, profile_id=profile_id)
        index = read_index(base_dir, descriptor)
        if index is None and not background:
            refresh_profile(base_dir, descriptor)
            index = read_index(base_dir, descriptor)
        if index is None:
            status = 'loading'
            request_refresh(base_dir, descriptor)
            continue
        if time.time() - index['generated_at'] >= MAX_AGE:
            if status != 'loading':
                status = 'stale'
            request_refresh(base_dir, descriptor)
        for run_id in allowed:
            sources = index['runs'].get(run_id, dict())
            if sources:
                instruments.add(instrument)
            for source in SOURCES:
                for key in sources.get(source, []):
                    availability.setdefault(key, dict())
                    source_map = availability[key]
                    source_map.setdefault(source, set()).add(instrument)
    properties = []
    for key, source_map in sorted(availability.items()):
        sources = [source for source in SOURCES if source in source_map]
        source_instruments = dict()
        for source in sources:
            source_instruments[source] = sorted(source_map[source])
        combined = set().union(*source_map.values())
        properties.append(dict(property=key, sources=sources,
                               instruments=sorted(combined),
                               source_instruments=source_instruments))
    sources = [dict(key=key, label=label) for key, label in SOURCES.items()]
    return dict(sources=sources, properties=properties,
                instruments=sorted(instruments), status=status)