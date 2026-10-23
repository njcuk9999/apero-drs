#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Background peer manifests with disk-backed status for Flask workers."""

import hashlib
import threading
import time
import uuid
from pathlib import Path

from apero_ri.core.server_sync import adapters
from apero_ri.core.server_sync import store

JOB_TTL = 3600.0


def start(categories: list[str], owner: str) -> dict:
    """Start or reuse a scan for categories authorized by the token owner.

    :param categories: Requested adapter names.
    :param owner: Issued token identifier.
    :return: Job status without manifest data.
    """
    names = sorted(set(categories))
    if not names or any(name not in adapters.ADAPTERS for name in names):
        raise ValueError('Choose known manifest categories')
    digest = hashlib.sha256(owner.encode()).hexdigest()
    directory = store.sync_dir() / 'manifest_jobs' / digest
    directory.mkdir(parents=True, exist_ok=True)
    with store.journal_lock():
        now = time.time()
        for path in directory.glob('*.json'):
            state = store.read_json(path, dict())
            if now - state.get('started', 0) > JOB_TTL:
                path.unlink(missing_ok=True)
            elif state.get('categories') == names:
                if state.get('status') == 'running':
                    return _public(state)
        job_id = uuid.uuid4().hex
        path = directory / f'{job_id}.json'
        state = dict(job_id=job_id, categories=names, started=now,
                     status='running', category='', completed=0)
        store.write_json(path, state, mode=0o600)
    worker = threading.Thread(target=_scan, args=(path, state), daemon=True)
    worker.start()
    return _public(state)


def _public(state: dict) -> dict:
    """Return status excluding the potentially large manifests.

    :param state: Saved job state.
    :return: Public progress fields.
    """
    return {key: value for key, value in state.items() if key != 'result'}


def _scan(path: Path, state: dict) -> None:
    """Scan categories outside the HTTP request worker.

    :param path: Captured job file path.
    :param state: Initial job metadata.
    :return: None.
    """
    from apero_ri.core.server_sync import engine

    state = dict(state)
    result = dict()
    try:
        for category in state['categories']:
            state['category'] = category
            store.write_json(path, state, mode=0o600)
            result[category] = engine.scan(category)
            state['completed'] += 1
        state.update(status='done', result=result)
    except Exception as exc:
        state.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    store.write_json(path, state, mode=0o600)


def read(job_id: str, owner: str, category: str = '') -> dict:
    """Read progress or one completed category, scoped to its token.

    :param job_id: Server-issued scan identifier.
    :param owner: Issued token identifier.
    :param category: Category to retrieve, or empty for status only.
    :return: Progress or category manifest.
    """
    if len(job_id) != 32 or any(c not in '0123456789abcdef' for c in job_id):
        raise ValueError('Invalid manifest job')
    digest = hashlib.sha256(owner.encode()).hexdigest()
    path = store.sync_dir() / 'manifest_jobs' / digest / f'{job_id}.json'
    state = store.read_json(path, dict())
    if not state or time.time() - state['started'] > JOB_TTL:
        raise ValueError('Manifest job expired or unknown; analyse again')
    if category:
        if state['status'] != 'done' or category not in state['categories']:
            raise ValueError('Manifest category is not ready')
        return state['result'][category]
    return _public(state)