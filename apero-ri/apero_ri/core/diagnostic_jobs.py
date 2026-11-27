#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Private background diagnostic reports that survive browser refreshes."""

import fcntl
import hashlib
import hmac
import json
import os
import re
import secrets
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
SHARE_TOKEN = re.compile(r'^([0-9a-f]{64})\.([0-9a-f]{32})\.([\w-]{43})$')

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
    completed_at = state.get('completed_at', state.get('created', 0))
    expired = time.time() - completed_at >= LIFETIME
    if state.get('status') != 'running' and expired:
        return None
    if state.get('status') == 'running':
        state['stage_elapsed_s'] = max(
            0, int(time.time() - state.get('stage_started', state['created'])))
    state['share_active'] = (directory / (job_id + '.share')).is_file()
    return state


def latest(root: Path, actor: str, allowed: set) -> dict | None:
    """Find the newest unexpired job whose profile is still accessible.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator.
    :param allowed: Currently accessible instrument/profile tuples.
    :return: Latest authorized job metadata, or None.
    """
    directory = _directory(root, actor)
    def modified(path: Path) -> float:
        """Return a stable sort key if a job disappears during listing.

        :param path: Actor-owned job record.
        :return: Modification time, or zero when absent.
        """
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    paths = sorted(directory.glob('*.json'),
                   key=modified, reverse=True)
    for path in paths:
        if not JOB_ID.fullmatch(path.stem):
            continue
        state = get(root, actor, path.stem)
        if state and (state['instrument'], state['profile_id']) in allowed:
            return state
    return None


def saved(root: Path, actor: str, allowed: set) -> list[dict]:
    """List the owner's completed, unexpired and accessible reports.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator.
    :param allowed: Currently accessible instrument/profile tuples.
    :return: Up to 100 newest report metadata entries without report
             contents, each with ``expires_at`` and its active
             ``share_token`` (or None).
    """
    directory = _directory(root, actor)
    reports = []
    for path in directory.glob('*.json'):
        if not JOB_ID.fullmatch(path.stem):
            continue
        state = get(root, actor, path.stem)
        if not state or state.get('status') != 'completed':
            continue
        if (state['instrument'], state['profile_id']) not in allowed:
            continue
        if not (directory / (path.stem + '.report')).is_file():
            continue
        # owner-only listing: include the link so no extra request is needed
        state['share_token'] = share_token(root, actor, path.stem)
        state['expires_at'] = (state.get('completed_at', state['created'])
                               + LIFETIME)
        reports.append(state)
    reports.sort(key=lambda state: state.get('completed_at', state['created']),
                 reverse=True)
    return reports[:100]


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


def _issue_share(directory: Path, actor: str, job_id: str) -> str:
    """Write a fresh capability record, replacing any previous link.

    The token is kept next to the report in the owner's private ``0700``
    directory so saved-report listings can show the link again without
    rotating it; the digest is what public requests are checked against.

    :param directory: Owner's private job directory.
    :param actor: Authenticated report owner.
    :param job_id: Server-issued job identifier.
    :return: Bearer capability for the report.
    """
    # the owner hash ties the link to its directory without exposing a name
    actor_id = hashlib.sha256(actor.encode('utf-8')).hexdigest()
    token = actor_id + '.' + job_id + '.' + secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode('utf-8')).hexdigest()
    _write(directory / (job_id + '.share'),
           dict(actor=actor, digest=digest, token=token))
    return token


def share_token(root: Path, actor: str, job_id: str) -> str | None:
    """Return the owner's active share capability for one report.

    :param root: Active ARI data root.
    :param actor: Authenticated report owner.
    :param job_id: Server-issued job identifier.
    :return: Active bearer capability, or None when not shared.
    """
    if not JOB_ID.fullmatch(job_id):
        return None
    record = _read(_directory(root, actor) / (job_id + '.share'))
    if not record or record.get('actor') != actor:
        return None
    token = record.get('token')
    # only return a token that still validates against its stored digest
    if not isinstance(token, str) or not SHARE_TOKEN.fullmatch(token):
        return None
    digest = hashlib.sha256(token.encode('utf-8')).hexdigest()
    if not hmac.compare_digest(digest, str(record.get('digest', ''))):
        return None
    return token


def share(root: Path, actor: str, job_id: str) -> str | None:
    """Issue or rotate a public capability for one completed private report.

    :param root: Active ARI data root.
    :param actor: Authenticated report owner.
    :param job_id: Server-issued job identifier.
    :return: One-time bearer capability, or None when not shareable.
    """
    if not JOB_ID.fullmatch(job_id):
        return None
    directory = _directory(root, actor)
    descriptor = os.open(directory / '.jobs.lock', os.O_CREAT | os.O_RDWR,
                         0o600)
    with os.fdopen(descriptor, 'r+') as mutex:
        fcntl.flock(mutex, fcntl.LOCK_EX)
        if result(root, actor, job_id) is None:
            return None
        if _is_running(directory, job_id):
            return None
        return _issue_share(directory, actor, job_id)


def revoke_share(root: Path, actor: str, job_id: str) -> bool:
    """Revoke a report owner's public link without deleting the report.

    :param root: Active ARI data root.
    :param actor: Authenticated report owner.
    :param job_id: Server-issued job identifier.
    :return: Whether an active share existed.
    """
    if not JOB_ID.fullmatch(job_id):
        return False
    directory = _directory(root, actor)
    descriptor = os.open(directory / '.jobs.lock', os.O_CREAT | os.O_RDWR,
                         0o600)
    with os.fdopen(descriptor, 'r+') as mutex:
        fcntl.flock(mutex, fcntl.LOCK_EX)
        path = directory / (job_id + '.share')
        existed = path.is_file()
        path.unlink(missing_ok=True)
        return existed


def shared(root: Path, token: str) -> tuple[str, dict, dict] | None:
    """Validate a public capability and read its unexpired saved report.

    :param root: Active ARI data root.
    :param token: Bearer capability, never included in the return value.
    :return: Owner, job metadata and report, or None for an invalid link.
    """
    match = SHARE_TOKEN.fullmatch(token)
    if match is None:
        return None
    actor_id, job_id, _secret = match.groups()
    directory = root / 'secret' / 'diagnostic_jobs' / actor_id
    record = _read(directory / (job_id + '.share'))
    if not record or not isinstance(record.get('actor'), str):
        return None
    actor = record['actor']
    expected_actor = hashlib.sha256(actor.encode('utf-8')).hexdigest()
    digest = hashlib.sha256(token.encode('utf-8')).hexdigest()
    if not hmac.compare_digest(actor_id, expected_actor):
        return None
    if not hmac.compare_digest(digest, str(record.get('digest', ''))):
        return None
    state = get(root, actor, job_id)
    report = result(root, actor, job_id)
    if not state or state['status'] != 'completed' or report is None:
        return None
    return actor, state, report


def delete(root: Path, actor: str, job_id: str) -> bool:
    """Delete one finished report and revoke its public link.

    :param root: Active ARI data root.
    :param actor: Authenticated report owner.
    :param job_id: Server-issued job identifier.
    :return: Whether the report was deleted.
    :raises ValueError: If a collection is still running.
    """
    if not JOB_ID.fullmatch(job_id):
        return False
    directory = _directory(root, actor)
    descriptor = os.open(directory / '.jobs.lock', os.O_CREAT | os.O_RDWR,
                         0o600)
    with os.fdopen(descriptor, 'r+') as mutex:
        fcntl.flock(mutex, fcntl.LOCK_EX)
        path = directory / (job_id + '.json')
        state = _read(path)
        if state is None:
            return False
        if _is_running(directory, job_id):
            raise ValueError('diagnostic_job_running')
        for suffix in ('.json', '.report', '.share', '.lock'):
            (directory / (job_id + suffix)).unlink(missing_ok=True)
        return True


def cleanup_expired(root: Path) -> int:
    """Remove expired job records and reports without touching active jobs.

    :param root: Active ARI data root.
    :return: Number of expired jobs removed.
    """
    jobs_root = root / 'secret' / 'diagnostic_jobs'
    if not jobs_root.is_dir() or jobs_root.is_symlink():
        return 0
    removed = 0
    for directory in jobs_root.iterdir():
        valid = re.fullmatch(r'[0-9a-f]{64}', directory.name)
        if not valid or not directory.is_dir() or directory.is_symlink():
            continue
        descriptor = os.open(directory / '.jobs.lock', os.O_CREAT | os.O_RDWR,
                             0o600)
        with os.fdopen(descriptor, 'r+') as mutex:
            fcntl.flock(mutex, fcntl.LOCK_EX)
            for path in directory.glob('*.json'):
                if not JOB_ID.fullmatch(path.stem) or path.is_symlink():
                    continue
                state = _read(path)
                if not state:
                    continue
                retained = state.get('completed_at', state.get('created', 0))
                if time.time() - retained < LIFETIME:
                    continue
                if _is_running(directory, path.stem):
                    continue
                for suffix in ('.json', '.report', '.share', '.lock'):
                    (directory / (path.stem + suffix)).unlink(missing_ok=True)
                removed += 1
    return removed


def start(root: Path, actor: str, instrument: str, profile_id: str,
          options: dict, collect: Callable[..., dict],
          on_complete: Callable[[dict], None],
          on_share: Callable[[], None] | None = None
          ) -> tuple[dict, bool]:
    """Start or reconnect to one actor/profile background collection.

    :param root: Active ARI data root.
    :param actor: Authenticated administrator.
    :param instrument: Authorized instrument.
    :param profile_id: Authorized profile ID.
    :param options: Validated non-secret report filters.
    :param collect: Closure running the authorized collection.
    :param on_complete: Audit callback for a completed report.
    :param on_share: Optional audit callback once the report's share link
                     has been created; None disables automatic sharing.
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
                for suffix in ('.json', '.report', '.share', '.lock'):
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
                # create the link before publishing completion so the
                # saved-report listing never shows a finished, unshared row
                if on_share is not None:
                    try:
                        _issue_share(directory, actor, job_id)
                        on_share()
                    except OSError:
                        # the owner can still create the link manually
                        pass
                state.update(status='completed', stage='complete',
                             completed=state['total'], completed_at=time.time())
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