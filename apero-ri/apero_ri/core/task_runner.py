#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Background task queue runner.

Manages a global in-memory queue of AperoAsyncTask instances and a daemon
worker thread that processes them one at a time.  Thread-safe via a single
lock protecting _queue, _current, _instances and _errors.
"""
import threading
import traceback
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# Module-level state
# =============================================================================
# task_id -> AperoAsyncTask instance
_instances: Dict[str, Any] = {}
# pending queue: list of (instrument, task_id)
_queue: List[Tuple[str, str]] = []
# currently executing entry, or None
_current: Optional[Tuple[str, str]] = None
# task_id -> full traceback string on failure
_errors: Dict[str, str] = {}

_lock = threading.Lock()
_worker_thread: Optional[threading.Thread] = None
_scheduler_thread: Optional[threading.Thread] = None
_scheduler_local_data_dir = str(Path.home() / '.ari')
_scheduler_poll_seconds = 30.0


# =============================================================================
# Worker
# =============================================================================
def _run_worker() -> None:
    """Daemon worker: pop tasks from the queue and execute them."""
    global _current
    while True:
        entry: Optional[Tuple[str, str]] = None
        with _lock:
            if _queue:
                entry = _queue.pop(0)
                _current = entry

        if entry is None:
            time.sleep(0.5)
            continue

        _inst, task_id = entry
        instance = _instances.get(task_id)
        if instance is None:
            with _lock:
                _current = None
            continue

        instance.status = 'in_progress'
        try:
            run_params = getattr(instance, '_run_params', {})
            instance.run_job(run_params)
            instance.status = 'completed'
        except Exception:
            instance.status = 'failed'
            with _lock:
                _errors[task_id] = traceback.format_exc()
        finally:
            instance.run_count = getattr(instance, 'run_count', 0) + 1
            instance.last_run = datetime.now(timezone.utc).isoformat()
            _persist_runtime_state(_inst, task_id, instance)
            with _lock:
                _current = None


def _persist_runtime_state(instrument: str, task_id: str,
                            instance: Any) -> None:
    """Write runtime fields back to async_tasks.yaml after each run."""
    try:
        from apero_ri.core.auth import load_async_tasks, save_async_tasks
        with _lock:
            error = _errors.get(task_id, '')
        all_tasks = load_async_tasks()
        for tc in all_tasks.get(instrument, []):
            if tc.get('id') == task_id:
                tc['last_run'] = getattr(instance, 'last_run', 'Never')
                tc['run_count'] = getattr(instance, 'run_count', 0)
                tc['info'] = getattr(instance, 'info', '')
                tc['output_files'] = list(getattr(instance, 'output_files', []))
                tc['error'] = error
                tc['last_status'] = getattr(instance, 'status', 'failed')
                break
        save_async_tasks(all_tasks)
    except Exception:
        pass  # Never let persistence failures crash the worker


def _ensure_worker() -> None:
    """Start the worker thread if it is not already running."""
    global _worker_thread
    if _worker_thread is None or not _worker_thread.is_alive():
        _worker_thread = threading.Thread(
            target=_run_worker, daemon=True, name='ari-task-worker'
        )
        _worker_thread.start()


def _parse_last_run(value: Any) -> Optional[datetime]:
    """Parse a stored last-run timestamp."""
    if not value or value == 'Never':
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _coerce_run_count(value: Any) -> int:
    """Normalize a stored run-count value."""
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def hydrate_runtime_state(instance: Any, task_cfg: Optional[dict] = None) -> Any:
    """Copy persisted runtime fields onto a new task instance."""
    cfg = task_cfg or {}
    instance.last_run = cfg.get('last_run', getattr(instance, 'last_run', 'Never'))
    instance.run_count = _coerce_run_count(
        cfg.get('run_count', getattr(instance, 'run_count', 0))
    )
    instance.info = cfg.get('info', getattr(instance, 'info', ''))
    instance.output_files = list(
        cfg.get('output_files', getattr(instance, 'output_files', [])) or []
    )
    return instance


def _task_is_busy(task_id: str) -> bool:
    """Return True if a task is already queued or running."""
    with _lock:
        if _current is not None and _current[1] == task_id:
            return True
        return any(queued_id == task_id for _, queued_id in _queue)


def _task_is_due(task_cfg: dict, now: datetime) -> bool:
    """Return True if a task should be enqueued by the scheduler."""
    if not task_cfg.get('active', True):
        return False

    task_id = str(task_cfg.get('id', '') or '').strip()
    if not task_id or _task_is_busy(task_id):
        return False

    try:
        frequency_hours = float(task_cfg.get('frequency', 0) or 0)
    except (TypeError, ValueError):
        return False
    if frequency_hours <= 0:
        return False

    last_run = _parse_last_run(task_cfg.get('last_run'))
    if last_run is None:
        return True

    elapsed_seconds = (now - last_run).total_seconds()
    return elapsed_seconds >= frequency_hours * 3600.0


def _scheduler_poll(local_data_dir: str) -> None:
    """Queue any active tasks whose frequency window has elapsed."""
    try:
        import fcntl
    except ImportError:
        fcntl = None

    lock_handle = None
    try:
        if fcntl is not None:
            lock_path = Path(local_data_dir) / 'admin' / 'async_tasks.scheduler.lock'
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_handle = lock_path.open('a+')
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return

        from apero_ri import tasks as task_module
        from apero_ri.core.auth import load_apero_profiles, load_async_tasks

        all_tasks = load_async_tasks()
        all_profiles = load_apero_profiles()
        now = datetime.now(timezone.utc)

        for instrument, task_list in all_tasks.items():
            ordered_tasks = sorted(task_list, key=lambda task: task.get('order', 999))
            for task_cfg in ordered_tasks:
                if not _task_is_due(task_cfg, now):
                    continue
                task_key = str(task_cfg.get('task_key', '') or '').strip()
                task_id = str(task_cfg.get('id', '') or '').strip()
                task_cls = task_module.TASK_LIST.get(task_key)
                if not task_cls or not task_id:
                    continue
                instance = hydrate_runtime_state(task_cls(), task_cfg)
                run_params = build_run_params(
                    instrument, local_data_dir, all_profiles, task_cfg
                )
                enqueue(instrument, task_id, instance, run_params)
    except Exception:
        pass
    finally:
        if lock_handle is not None:
            lock_handle.close()


def _run_scheduler() -> None:
    """Daemon scheduler that enqueues due tasks based on frequency."""
    while True:
        _ensure_worker()
        _scheduler_poll(_scheduler_local_data_dir)
        time.sleep(_scheduler_poll_seconds)


def start_background_services(local_data_dir: Optional[str] = None) -> None:
    """Start the queue worker and periodic scheduler threads."""
    global _scheduler_thread, _scheduler_local_data_dir
    if local_data_dir:
        _scheduler_local_data_dir = str(local_data_dir)

    _ensure_worker()
    if _scheduler_thread is None or not _scheduler_thread.is_alive():
        _scheduler_thread = threading.Thread(
            target=_run_scheduler, daemon=True, name='ari-task-scheduler'
        )
        _scheduler_thread.start()


# =============================================================================
# Public helpers
# =============================================================================
def build_run_params(instrument: str, local_data_dir: str,
                     all_profiles: dict,
                     task_cfg: Optional[dict] = None) -> dict:
    """Build the ``params`` dict expected by ``AperoAsyncTask.run_job``.

    Maps ``DATABASE_USERNAME`` → ``DATABASE_USER`` for each profile so that
    ``apero_async.database_query`` can find the correct key.
    """
    profiles = all_profiles.get(instrument, {})
    mapped: Dict[str, dict] = {}
    for pname, pcfg in profiles.items():
        p = dict(pcfg)
        if 'DATABASE_USERNAME' in p and 'DATABASE_USER' not in p:
            p['DATABASE_USER'] = p['DATABASE_USERNAME']
        mapped[pname] = p
    from pathlib import Path as _Path
    safe_dir = local_data_dir or str(_Path.home() / '.ari')
    return {
        'LOCAL_DATA_DIR': safe_dir,
        'INSTRUMENT': instrument,
        'APERO_PROFILE_NAMES': list(mapped.keys()),
        'APERO_PROFILES': mapped,
        'TASK_CONFIG': dict(task_cfg or {}),
    }


def enqueue(instrument: str, task_id: str, instance: Any,
            run_params: dict, prepend: bool = False) -> None:
    """Add a task instance to the execution queue.

    If the task_id is already queued it is moved to the new position.
    """
    _ensure_worker()
    instance._run_params = run_params
    instance.status = 'queued'
    with _lock:
        _instances[task_id] = instance
        _errors.pop(task_id, None)
        # Remove any existing entry for this task_id
        updated = [(i, t) for i, t in _queue if t != task_id]
        entry = (instrument, task_id)
        if prepend:
            updated.insert(0, entry)
        else:
            updated.append(entry)
        _queue[:] = updated


def stop_and_clear() -> None:
    """Clear the pending queue; does not interrupt the running task."""
    with _lock:
        for _i, tid in _queue:
            inst = _instances.get(tid)
            if inst is not None:
                inst.status = 'cancelled'
        _queue.clear()


def clear_instance(task_id: str) -> None:
    """Remove a task instance and its error record from memory."""
    with _lock:
        _instances.pop(task_id, None)
        _errors.pop(task_id, None)
        # Remove from queue if present
        _queue[:] = [(i, t) for i, t in _queue if t != task_id]


def get_status() -> dict:
    """Return current queue and running-task information."""
    with _lock:
        return {
            'current': _current,
            'queue': list(_queue),
            'queue_length': len(_queue),
        }


def get_task_status(task_id: str) -> dict:
    """Return a status dict for a single task by id."""
    with _lock:
        instance = _instances.get(task_id)
        if instance is None:
            return {'found': False}
        is_current = _current is not None and _current[1] == task_id
        is_queued = any(t == task_id for _, t in _queue)
        error = _errors.get(task_id, '')

    return {
        'found': True,
        'status': instance.status,
        'progress': instance.progress,
        'info': instance.info,
        'last_run': getattr(instance, 'last_run', 'Never'),
        'output_files': getattr(instance, 'output_files', []),
        'run_count': getattr(instance, 'run_count', 0),
        'is_current': is_current,
        'is_queued': is_queued,
        'error': error,
    }
