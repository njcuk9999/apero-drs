#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Private background diagnostic reports that survive browser refreshes."""

import fcntl
import hashlib
import json
import os
import re
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.diagnostic_jobs'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
LIFETIME = 24 * 3600
JOB_ID = re.compile(r'^[0-9a-f]{32}$')

# =============================================================================
# Define functions
# =============================================================================
def _directory(root: Path, actor: str) -> Path:
    """Return a private actor-specific diagnostic job directory.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator name.
    :return: Created private directory with no username in its path.
    """
    digest = hashlib.sha256(actor.encode('utf-8')).hexdigest()
    directory = root / 'secret' / 'diagnostic_jobs' / digest
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    return directory


def _write(path: Path, payload: dict) -> None:
    """Atomically replace a private job record.

    :param path: Server-owned job record path.
    :param payload: JSON-compatible status or redacted report.
    :return: None.
    """
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent,
                                         delete=False) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(payload, temporary, allow_nan=False)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _read(path: Path) -> dict | None:
    """Read an atomically published job record.

    :param path: Server-owned job record path.
    :return: Record or None if absent or invalid.
    """
    try:
        result = json.loads(path.read_text(encoding='utf-8'))
        return result if isinstance(result, dict) else None
    except (OSError, ValueError):
        return None


def _is_running(directory: Path, job_id: str) -> bool:
    """Check whether a worker still owns a job's process-safe lock.

    :param directory: Actor's private directory.
    :param job_id: Server-generated job identifier.
    :return: True while the worker holds its lock.
    """
    lock_path = directory / (job_id + '.lock')
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, 'r+') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(handle, fcntl.LOCK_UN)
    return False


def get(root: Path, actor: str, job_id: str) -> dict | None:
    """Read an actor's unexpired job and detect interrupted workers.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator.
    :param job_id: Server-issued identifier.
    :return: Job metadata, or None when missing or expired.
    """
    if not JOB_ID.fullmatch(job_id):
        return None
    directory = _directory(root, actor)
    state = _read(directory / (job_id + '.json'))
    if not state:
        return None
    if state.get('status') == 'running' and not _is_running(directory, job_id):
        state = _read(directory / (job_id + '.json')) or state
        if state.get('status') == 'running':
            state['status'] = 'interrupted'
    if (state.get('status') != 'running'
            and time.time() - state.get('created', 0) > LIFETIME):
        return None
    if state.get('status') == 'running':
        state['stage_elapsed_s'] = max(
            0, int(time.time() - state.get('stage_started', state['created'])))
    return state


def latest(root: Path, actor: str, allowed: set) -> dict | None:
    """Find the newest unexpired job whose profile is still accessible.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator.
    :param allowed: Currently accessible instrument/profile tuples.
    :return: Latest authorized job metadata, or None.
    """
    directory = _directory(root, actor)
    paths = sorted(directory.glob('*.json'),
                   key=lambda path: path.stat().st_mtime, reverse=True)
    for path in paths:
        if not JOB_ID.fullmatch(path.stem):
            continue
        state = get(root, actor, path.stem)
        if state and (state['instrument'], state['profile_id']) in allowed:
            return state
    return None


def result(root: Path, actor: str, job_id: str) -> dict | None:
    """Read a completed job's report from the private job store.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator.
    :param job_id: Server-issued identifier.
    :return: Completed report, or None.
    """
    state = get(root, actor, job_id)
    if not state or state['status'] != 'completed':
        return None
    return _read(_directory(root, actor) / (job_id + '.report'))


def start(root: Path, actor: str, instrument: str, profile_id: str,
          options: dict, collect: Callable[..., dict],
          on_complete: Callable[[dict], None]) -> tuple[dict, bool]:
    """Start or reconnect to one actor/profile background collection.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator.
    :param instrument: Authorized instrument.
    :param profile_id: Authorized profile ID.
    :param options: Validated non-secret report filters.
    :param collect: Closure running the authorized collection.
    :param on_complete: Audit callback for a completed report.
    :return: Job metadata and whether an existing job was reused.
    :raises ValueError: A different collection is already running.
    """
    directory = _directory(root, actor)
    mutex_path = directory / '.jobs.lock'
    descriptor = os.open(mutex_path, os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, 'r+') as mutex:
        fcntl.flock(mutex, fcntl.LOCK_EX)
        for path in directory.glob('*.json'):
            if not JOB_ID.fullmatch(path.stem):
                continue
            previous = get(root, actor, path.stem)
            if previous is None:
                for suffix in ('.json', '.report', '.lock'):
                    (directory / (path.stem + suffix)).unlink(missing_ok=True)
                continue
            if not previous or previous['status'] != 'running':
                continue
            if (previous['instrument'], previous['profile_id']) != (
                    instrument, profile_id):
                continue
            if previous['options'] != options:
                raise ValueError('diagnostic_job_already_running')
            return previous, True
        job_id = uuid.uuid4().hex
        lock_path = directory / (job_id + '.lock')
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        lock_handle = os.fdopen(lock_fd, 'r+')
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state_path = directory / (job_id + '.json')
        state = dict(id=job_id, instrument=instrument, profile_id=profile_id,
                     options=options, created=time.time(), status='running',
                     stage='runtime', completed=0, total=1,
                     stage_started=time.time())
        _write(state_path, state)

        def progress(stage: str, completed: int, total: int) -> None:
            """Persist one collector stage for all polling clients.

            :param stage: Current stage identifier.
            :param completed: Finished stages.
            :param total: Total stages.
            :return: None.
            """
            if state['stage'] != stage:
                state['stage_started'] = time.time()
            state.update(stage=stage, completed=completed, total=total)
            _write(state_path, state)

        def worker() -> None:
            """Collect once, publishing the final private report atomically.

            :return: None.
            """
            try:
                report = collect(progress=progress)
                on_complete(report)
                report['success'] = True
                _write(directory / (job_id + '.report'), report)
                state.update(status='completed', stage='complete',
                             completed=state['total'])
            except Exception:
                state.update(status='failed', error='collection_failed')
            finally:
                try:
                    _write(state_path, state)
                finally:
                    fcntl.flock(lock_handle, fcntl.LOCK_UN)
                    lock_handle.close()

        try:
            threading.Thread(target=worker, daemon=True,
                             name='ari-diagnostic-' + job_id[:8]).start()
        except Exception:
            lock_handle.close()
            raise
        return dict(state), False


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================