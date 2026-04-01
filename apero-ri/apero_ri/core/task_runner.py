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
import json
import yaml
import contextlib
import sys
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.task_runner'
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
_async_tasks_rel_dir = Path('admin') / 'async_tasks'
_history_relpath = _async_tasks_rel_dir / 'async_history.txt'
_task_logs_rel_dir = _async_tasks_rel_dir / 'task_logs'
_task_info_rel_dir = _async_tasks_rel_dir / 'task_info'
_task_errors_rel_dir = _async_tasks_rel_dir / 'task_errors'
_aprofile_preset_cache: Dict[str, dict] = {}
_task_log_paths: Dict[str, str] = {}
_task_instruments: Dict[str, str] = {}
_stop_events: Dict[str, threading.Event] = {}


class _TaskLogTeeStream:
    """Tee stream that forwards output and writes timestamped log lines."""

    def __init__(self, path: Path, sink: Any, stream_tag: str):
        self._path = path
        self._sink = sink
        self._stream_tag = stream_tag
        self._buffer = ''

    def write(self, data: Any) -> int:
        text = str(data or '')
        if not text:
            return 0
        try:
            self._sink.write(text)
        except Exception:
            pass
        self._buffer += text
        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            line = line.rstrip('\r')
            if line.strip():
                _append_task_log_line(
                    self._path,
                    f'[{self._stream_tag}] {line}',
                )
        return len(text)

    def flush(self) -> None:
        if self._buffer.strip():
            _append_task_log_line(
                self._path,
                f'[{self._stream_tag}] {self._buffer.rstrip()}')
        self._buffer = ''
        try:
            self._sink.flush()
        except Exception:
            pass


# =============================================================================
# Define functions
# =============================================================================
def _is_global_scope(instrument: str) -> bool:
    """Return True if this scope key represents global async tasks."""
    return str(instrument).strip() == '__GLOBAL__'


def _task_keys_for_scope(task_module: Any, instrument: str) -> List[str]:
    """Return task keys allowed in this scope from tasks.TYPE."""
    want_type = 'GLOBAL' if _is_global_scope(instrument) else 'INSTRUMENT'
    keys: List[str] = []
    for task_key in task_module.TASK_LIST.keys():
        ttype = (
            str(task_module.TYPE.get(task_key, 'INSTRUMENT'))
            .strip().upper()
        )
        if ttype == want_type:
            keys.append(task_key)
    return keys


def _dedupe_strings(values: Any) -> List[str]:
    """Return stable-order unique string values."""
    if not isinstance(values, list):
        return []
    out: List[str] = []
    seen = set()
    for item in values:
        sval = str(item).strip()
        if not sval or sval in seen:
            continue
        seen.add(sval)
        out.append(sval)
    return out


def _sanitize_run_params(value: Any) -> Any:
    """Return a JSON-safe copy of run params with secrets redacted."""
    sensitive_tokens = ['password', 'passwd', 'secret', 'token', 'api_key']

    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        for key, item in value.items():
            key_str = str(key)
            key_lower = key_str.lower()
            if any(token in key_lower for token in sensitive_tokens):
                out[key_str] = '***REDACTED***'
            else:
                out[key_str] = _sanitize_run_params(item)
        return out
    if isinstance(value, list):
        return [_sanitize_run_params(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_run_params(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _load_aprofile_preset(profile_file: str) -> dict:
    """
    Load one APERO instrument profile YAML from resources/aprofile_instruments.
    """
    if not profile_file:
        return {}
    if profile_file in _aprofile_preset_cache:
        return dict(_aprofile_preset_cache[profile_file])
    resources_dir = (
        Path(__file__).resolve().parents[1]
        / 'resources' / 'aprofile_instruments'
    )
    path = resources_dir / profile_file
    if not path.is_file():
        _aprofile_preset_cache[profile_file] = {}
        return {}
    try:
        with path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    _aprofile_preset_cache[profile_file] = data
    return dict(data)


def _merge_missing(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge missing keys from src into dst.

    Existing dst values always win. If both values are dicts, merge recursively.
    """
    if not isinstance(dst, dict) or not isinstance(src, dict):
        return dst
    for key, src_val in src.items():
        if key not in dst:
            dst[key] = deepcopy(src_val)
            continue
        dst_val = dst.get(key)
        # Treat explicit null/blank placeholders as missing.
        if dst_val is None:
            dst[key] = deepcopy(src_val)
            continue
        if isinstance(dst_val, str) and not dst_val.strip():
            dst[key] = deepcopy(src_val)
            continue
        if isinstance(dst_val, dict) and isinstance(src_val, dict):
            _merge_missing(dst_val, src_val)
    return dst


def _history_file_path() -> Path:
    """Return the history file path under local data dir."""
    return Path(_scheduler_local_data_dir) / _history_relpath


def _legacy_history_file_path() -> Path:
    """Return legacy history file path for backward compatibility."""
    return Path(_scheduler_local_data_dir) / 'admin' / 'async_history.txt'


def _safe_scope_name(value: str) -> str:
    """Return a filesystem-safe identifier for instrument scope names."""
    text = str(value or '').strip()
    if not text:
        return 'unknown'
    cleaned = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in text)
    return cleaned or 'unknown'


def _task_log_file_path(instrument: str, task_id: str) -> Path:
    """Return per-task current log file path."""
    base = Path(_scheduler_local_data_dir) / _task_logs_rel_dir
    scope = _safe_scope_name(instrument or 'GLOBAL')
    name = _safe_scope_name(task_id)
    return base / f'{scope}__{name}.log'


def _task_info_file_path(instrument: str, task_id: str) -> Path:
    """Return per-task info markdown path."""
    base = Path(_scheduler_local_data_dir) / _task_info_rel_dir
    scope = _safe_scope_name(instrument or 'GLOBAL')
    name = _safe_scope_name(task_id)
    return base / f'{scope}__{name}.md'


def _task_error_file_path(instrument: str, task_id: str) -> Path:
    """Return per-task error text path."""
    base = Path(_scheduler_local_data_dir) / _task_errors_rel_dir
    scope = _safe_scope_name(instrument or 'GLOBAL')
    name = _safe_scope_name(task_id)
    return base / f'{scope}__{name}.txt'


def _append_task_log_line(path: Path, message: str) -> None:
    """Append one timestamped line to task log file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        with path.open('a', encoding='utf-8') as handle:
            handle.write(f'{stamp} | {str(message or "")}\n')
    except Exception:
        pass


def _prepare_task_log(instrument: str, task_id: str,
                      task_name: str) -> Path:
    """Create/overwrite the per-task current log and return its path."""
    path = _task_log_file_path(instrument, task_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('', encoding='utf-8')
    except Exception:
        pass
    _append_task_log_line(path, f'Task queued: {task_name} [{task_id}]')
    with _lock:
        _task_log_paths[task_id] = str(path)
        _task_instruments[task_id] = instrument
    return path


def _make_task_logger(log_path: Path):
    """Build a callable logger injected into task run params."""

    def _log_fn(message: Any) -> None:
        _append_task_log_line(log_path, str(message or ''))

    return _log_fn


def _tail_lines(path: Path, lines: int) -> str:
    """Return at most the last ``lines`` from a UTF-8 text file."""
    try:
        raw_lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception:
        return ''
    if lines <= 0 or len(raw_lines) <= lines:
        return '\n'.join(raw_lines)
    return '\n'.join(raw_lines[-lines:])


def _log_path_for_task(task_id: str, instrument: str = '') -> str:
    """Return current log path for a task id without reading file content."""
    path = _task_log_paths.get(task_id)
    if path:
        return path
    # If in-memory cache was lost (e.g. process restart), recover the most
    # recent log file for this task id from disk.
    resolved = _resolve_existing_task_log_file(task_id)
    if resolved is not None:
        _task_log_paths[task_id] = str(resolved)
        return str(resolved)
    scope = instrument or _task_instruments.get(task_id, '')
    return str(_task_log_file_path(scope, task_id))


def _resolve_existing_task_log_file(task_id: str) -> Optional[Path]:
    """Return most recent on-disk task log path for task id, if present."""
    try:
        safe_task = _safe_scope_name(task_id)
        candidates: List[Path] = []
        base_new = Path(_scheduler_local_data_dir) / _task_logs_rel_dir
        candidates.extend(list(base_new.glob(f'*__{safe_task}.log')))
        # Legacy location (before admin/async_tasks/task_logs migration)
        base_old = Path(_scheduler_local_data_dir) / 'admin' / 'async_task_logs'
        candidates.extend(list(base_old.glob(f'*__{safe_task}.log')))
        if not candidates:
            return None
        candidates.sort(
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        return candidates[0]
    except Exception:
        return None


def _resolve_existing_task_data_file(task_id: str,
                                     rel_dir: Path,
                                     suffix: str) -> Optional[Path]:
    """Return newest persisted per-task data file by task id."""
    try:
        base = Path(_scheduler_local_data_dir) / rel_dir
        safe_task = _safe_scope_name(task_id)
        candidates = list(base.glob(f'*__{safe_task}{suffix}'))
        if not candidates:
            return None
        candidates.sort(
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        return candidates[0]
    except Exception:
        return None


def _read_text_file(path: Path) -> str:
    """Read UTF-8 text file safely; return empty string on error."""
    try:
        if not path.is_file():
            return ''
        return path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''


def _write_text_file(path: Path, content: str) -> None:
    """Write UTF-8 text file safely; ignore write failures."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(content or ''), encoding='utf-8')
    except Exception:
        pass


def _persist_task_info_error(instrument: str, task_id: str,
                             info: str, error: str) -> None:
    """Persist task info/error payloads in dedicated files."""
    _write_text_file(_task_info_file_path(instrument, task_id), info or '')
    _write_text_file(_task_error_file_path(instrument, task_id), error or '')


def get_persisted_task_info_error(task_id: str) -> Dict[str, str]:
    """Return persisted task info/error from dedicated files."""
    scope = _task_instruments.get(task_id, '')
    info_path = _task_info_file_path(scope, task_id)
    err_path = _task_error_file_path(scope, task_id)

    info = _read_text_file(info_path)
    error = _read_text_file(err_path)

    if not info:
        found = _resolve_existing_task_data_file(
            task_id, _task_info_rel_dir, '.md')
        if found is not None:
            info = _read_text_file(found)
    if not error:
        found = _resolve_existing_task_data_file(
            task_id, _task_errors_rel_dir, '.txt')
        if found is not None:
            error = _read_text_file(found)

    return {'info': info, 'error': error}


def _append_history_entry(instrument: str, task_id: str,
                          task_name: str, status: str,
                          details: str = '',
                          duration_seconds: Optional[float] = None) -> None:
    """Append one history entry to async history file as JSON line."""
    try:
        path = _history_file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'instrument': str(instrument or ''),
            'task_id': str(task_id or ''),
            'task_name': str(task_name or task_id or ''),
            'status': str(status or ''),
            'details': str(details or ''),
        }
        if duration_seconds is not None:
            payload['duration_seconds'] = round(float(duration_seconds), 3)
        with path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + '\n')
    except Exception:
        pass


def get_recent_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Return newest async history entries from async_history.txt."""
    try:
        path = _history_file_path()
        if not path.exists():
            legacy = _legacy_history_file_path()
            if legacy.exists():
                path = legacy
        if not path.exists() or limit <= 0:
            return []
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        out: List[Dict[str, Any]] = []
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                out.append({
                    'timestamp': str(row.get('timestamp', '')),
                    'instrument': str(row.get('instrument', '')),
                    'task_id': str(row.get('task_id', '')),
                    'task_name': str(
                        row.get('task_name', '') or row.get('task_id', '')
                    ),
                    'status': str(row.get('status', '')),
                    'details': str(row.get('details', '')),
                    'duration_seconds': row.get('duration_seconds'),
                })
            except Exception:
                continue
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []


def clear_recent_history() -> Dict[str, Any]:
    """Clear async history entries from async_history.txt."""
    try:
        path = _history_file_path()
        legacy = _legacy_history_file_path()
        removed = 0
        if path.exists():
            try:
                removed = len(
                    path.read_text(encoding='utf-8', errors='replace')
                    .splitlines()
                )
            except Exception:
                removed = 0
        elif legacy.exists():
            try:
                removed = len(
                    legacy.read_text(encoding='utf-8', errors='replace')
                    .splitlines()
                )
            except Exception:
                removed = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('', encoding='utf-8')
        try:
            if legacy.exists():
                legacy.unlink()
        except Exception:
            pass
        return {'success': True, 'removed': removed}
    except Exception as exc:
        return {'success': False, 'error': str(exc)}


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
        start_time = time.perf_counter()
        run_params = dict(getattr(instance, '_run_params', {}) or {})
        task_name = str(getattr(instance, 'name', task_id) or task_id)
        log_path = _prepare_task_log(_inst, task_id, task_name)
        run_params['TASK_LOG_PATH'] = str(log_path)
        run_params['TASK_LOGGER'] = _make_task_logger(log_path)
        run_params['STOP_EVENT'] = _stop_events.get(task_id, threading.Event())
        instance._run_params = run_params
        instance._task_log_path = str(log_path)
        _append_task_log_line(log_path, 'Task execution started.')
        try:
            # Treat task output files as this-run artifacts.
            instance.output_files = []
            stdout_tee = _TaskLogTeeStream(log_path, sink=sys.stdout, stream_tag='stdout')
            stderr_tee = _TaskLogTeeStream(log_path, sink=sys.stderr, stream_tag='stderr')
            with contextlib.redirect_stdout(stdout_tee), contextlib.redirect_stderr(stderr_tee):
                instance.run_job(run_params)
            stdout_tee.flush()
            stderr_tee.flush()
            stop_ev = _stop_events.get(task_id)
            if stop_ev is not None and stop_ev.is_set():
                instance.status = 'cancelled'
                _append_task_log_line(log_path, 'Task cancelled by user request.')
            else:
                instance.status = 'completed'
                _append_task_log_line(log_path, 'Task execution completed successfully.')
        except Exception:
            instance.status = 'failed'
            _append_task_log_line(log_path, 'Task execution failed. Traceback follows:')
            for line in traceback.format_exc().splitlines():
                if line.strip():
                    _append_task_log_line(log_path, line)
            with _lock:
                _errors[task_id] = traceback.format_exc()
        finally:
            duration_seconds = max(0.0, time.perf_counter() - start_time)
            _append_task_log_line(
                log_path,
                f'Task finished with status={instance.status} in '
                f'{duration_seconds:.2f}s.',
            )
            instance.run_count = getattr(instance, 'run_count', 0) + 1
            instance.last_run = datetime.now(timezone.utc).isoformat()
            _append_history_entry(
                _inst,
                task_id,
                getattr(instance, 'name', task_id),
                getattr(instance, 'status', ''),
                ('' if getattr(instance, 'status', '') != 'failed'
                 else _errors.get(task_id, '')),
                duration_seconds=duration_seconds,
            )
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
                tc['output_files'] = _dedupe_strings(
                    getattr(instance, 'output_files', [])
                )
                tc['last_run_params'] = _sanitize_run_params(
                    getattr(instance, '_run_params', {})
                )
                tc['last_status'] = getattr(instance, 'status', 'failed')
                tc.pop('info', None)
                tc.pop('error', None)
                break
        _persist_task_info_error(
            instrument,
            task_id,
            getattr(instance, 'info', ''),
            error,
        )
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


def hydrate_runtime_state(instance: Any,
                          task_cfg: Optional[dict] = None) -> Any:
    """Copy persisted runtime fields onto a new task instance."""
    cfg = task_cfg or {}
    instance.last_run = cfg.get(
        'last_run', getattr(instance, 'last_run', 'Never'))
    instance.run_count = _coerce_run_count(
        cfg.get('run_count', getattr(instance, 'run_count', 0))
    )
    instance.info = cfg.get('info', getattr(instance, 'info', ''))
    instance.output_files = _dedupe_strings(
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

    cooldown_until = _parse_last_run(task_cfg.get('cooldown_until'))
    if cooldown_until is not None and now < cooldown_until:
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


def _normalize_task_frequency(value, default: float = 24.0) -> float:
    """Normalize a task frequency value in hours."""
    try:
        freq = float(value)
        if freq > 0:
            return freq
    except (TypeError, ValueError):
        pass
    return float(default)


def _normalize_task_enabled(value, default: bool = False) -> bool:
    """Normalize a task enabled flag."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        sval = value.strip().lower()
        if sval in ['true', '1', 'yes', 'on']:
            return True
        if sval in ['false', '0', 'no', 'off', '']:
            return False
    return bool(value)


def can_enqueue_now(task_cfg: dict,
                    now: Optional[datetime] = None) -> Tuple[bool, str]:
    """Return whether a task may be manually enqueued right now."""
    now_utc = now or datetime.now(timezone.utc)

    if not task_cfg.get('active', True):
        return False, 'Task is inactive.'

    task_id = str(task_cfg.get('id', '') or '').strip()
    if not task_id:
        return False, 'Task id is missing.'

    if _task_is_busy(task_id):
        return False, 'Task is already queued or running.'

    cooldown_until = _parse_last_run(task_cfg.get('cooldown_until'))
    if cooldown_until is not None and now_utc < cooldown_until:
        return False, f'Task is in cooldown until {cooldown_until.isoformat()}.'

    return True, ''


def _scheduler_poll(local_data_dir: str) -> None:
    """Queue any active tasks whose frequency window has elapsed."""
    try:
        import fcntl
    except ImportError:
        fcntl = None

    lock_handle = None
    try:
        if fcntl is not None:
            lock_path = (
                Path(local_data_dir) / 'admin' / 'async_tasks'
                / 'scheduler.lock'
            )
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_handle = lock_path.open('a+')
            try:
                fcntl.flock(
                    lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB
                )
            except OSError:
                return

        from apero_ri import tasks as task_module
        from apero_ri.core.auth import (
            load_apero_profiles, load_async_tasks, save_async_tasks)
        import uuid as uuid_module
        import_errors = getattr(task_module, 'IMPORT_ERRORS', {}) or {}

        all_tasks = load_async_tasks()
        all_profiles = load_apero_profiles()
        now = datetime.now(timezone.utc)
        changed = False

        if '__GLOBAL__' not in all_tasks:
            all_tasks['__GLOBAL__'] = []
            changed = True

        for instrument, task_list in all_tasks.items():
            if not isinstance(task_list, list):
                continue

            stored_tasks = task_list
            by_key = {}
            for task_cfg in stored_tasks:
                if not isinstance(task_cfg, dict):
                    continue
                key = str(task_cfg.get('task_key', '')).strip()
                if key and key not in by_key:
                    by_key[key] = task_cfg

            merged = []
            task_keys = _task_keys_for_scope(task_module, instrument)
            for idx, task_key in enumerate(task_keys, start=1):
                task_cfg = dict(by_key.get(task_key, {}))
                task_id = str(task_cfg.get('id', '')).strip()
                if not task_id:
                    task_id = str(uuid_module.uuid5(
                        uuid_module.NAMESPACE_URL,
                        f'ari-async-task:{instrument}:{task_key}'
                    ))
                    changed = True

                default_freq = _normalize_task_frequency(
                    task_module.FREQ.get(task_key, 24.0), 24.0
                )
                default_enabled = _normalize_task_enabled(
                    task_module.ENABLED.get(task_key, False), False
                )

                merged_cfg = {
                    'id': task_id,
                    'task_key': task_key,
                    'frequency': _normalize_task_frequency(
                        task_cfg.get('frequency', default_freq), default_freq
                    ),
                    'active': _normalize_task_enabled(
                        task_cfg.get('active', default_enabled),
                        default_enabled
                    ),
                    'order': idx,
                }

                # Preserve multiprocessing settings so scheduler merges do not
                # silently reset task parallelism back to defaults.
                supports_mp = bool(task_module.MULTI_PROCESS.get(task_key, False))
                keep_mp = supports_mp or any(
                    key in task_cfg
                    for key in ['ncores', 'mp_backend', 'mp_start_method']
                )
                if keep_mp:
                    try:
                        ncores = int(task_cfg.get('ncores', 1) or 1)
                    except (TypeError, ValueError):
                        ncores = 1
                    merged_cfg['ncores'] = max(1, ncores)

                    backend = str(
                        task_cfg.get('mp_backend', 'threads') or 'threads'
                    ).strip().lower()
                    if backend not in ['threads', 'processes']:
                        backend = 'threads'
                    merged_cfg['mp_backend'] = backend

                    start_method = str(
                        task_cfg.get('mp_start_method', 'default') or 'default'
                    ).strip().lower()
                    if start_method not in ['default', 'spawn', 'fork', 'forkserver']:
                        start_method = 'default'
                    merged_cfg['mp_start_method'] = start_method

                if task_key == 'ARI_LOCAL_DATA_BACKUP':
                    try:
                        daily_copies = int(
                            task_cfg.get('daily_copies', 7) or 0)
                    except (TypeError, ValueError):
                        daily_copies = 7
                    try:
                        weekly_copies = int(
                            task_cfg.get('weekly_copies', 4) or 0)
                    except (TypeError, ValueError):
                        weekly_copies = 4
                    merged_cfg['daily_copies'] = max(0, daily_copies)
                    merged_cfg['weekly_copies'] = max(0, weekly_copies)

                for field in ['last_run', 'run_count', 'output_files',
                              'last_status']:
                    if field in task_cfg:
                        merged_cfg[field] = task_cfg.get(field)

                import_error = str(import_errors.get(task_key, '')).strip()
                if import_error:
                    merged_cfg['last_status'] = 'failed'

                merged.append(merged_cfg)

            if merged != stored_tasks:
                all_tasks[instrument] = merged
                changed = True

            ordered_tasks = sorted(
                merged, key=lambda task: task.get('order', 999))
            for task_cfg in ordered_tasks:
                if not _task_is_due(task_cfg, now):
                    continue
                task_key = str(task_cfg.get('task_key', '') or '').strip()
                task_id = str(task_cfg.get('id', '') or '').strip()
                if str(import_errors.get(task_key, '')).strip():
                    continue
                task_cls = task_module.TASK_LIST.get(task_key)
                if not task_cls or not task_id:
                    continue
                try:
                    instance = hydrate_runtime_state(task_cls(), task_cfg)
                except Exception:
                    task_cfg['last_status'] = 'failed'
                    task_cfg['error'] = traceback.format_exc()
                    changed = True
                    continue
                run_params = build_run_params(
                    instrument, local_data_dir, all_profiles, task_cfg
                )
                enqueue(instrument, task_id, instance, run_params)

        if changed:
            save_async_tasks(all_tasks)
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
    db_keys = [
        'DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_PORT',
        'DATABASE_USER', 'DATABASE_USERNAME', 'DATABASE_PASSWORD',
        'DATABASE_NAME', 'DATABASE_USE_SSH_TUNNEL',
        'DATABASE_SSH_CONFIG_HOST', 'DATABASE_SSH_LOCAL_PORT',
        'DATABASE_SSH_REMOTE_PORT',
        'ASTROM_TABLENAME', 'CALIB_TABLENAME', 'FINDEX_TABLENAME',
        'LOG_TABLENAME', 'TELLU_TABLENAME', 'REJECT_TABLENAME',
    ]
    path_keys = [
        'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
        'PATH_OUT', 'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
    ]
    for pname, pcfg in profiles.items():
        p = deepcopy(pcfg) if isinstance(pcfg, dict) else {}

        # Merge preset YAML referenced by APERO_INSTRUMENT_PROFILE so task
        # payloads include all instrument defaults without requiring code edits
        # for each new profile key.
        preset_name = str(p.get('APERO_INSTRUMENT_PROFILE', '') or '').strip()
        preset_data = _load_aprofile_preset(preset_name)
        if isinstance(preset_data, dict) and preset_data:
            _merge_missing(p, preset_data)
            # Keep a full copy for debugging/future task use.
            p['APERO_INSTRUMENT_PROFILE_DATA'] = deepcopy(preset_data)

        # Compatibility aliases between legacy/current key names.
        if 'sci-headers' not in p and isinstance(p.get('headers'), dict):
            p['sci-headers'] = deepcopy(p.get('headers', {}))
        # Presets may use singular "plot" while tasks expect "plots".
        if 'plots' not in p and isinstance(p.get('plot'), dict):
            p['plots'] = deepcopy(p.get('plot', {}))
        if 'plot' not in p and isinstance(p.get('plots'), dict):
            p['plot'] = deepcopy(p.get('plots', {}))

        database = p.get('database', {})
        if not isinstance(database, dict):
            database = {}
        for key in db_keys:
            if key not in database and p.get(key):
                database[key] = p.get(key)
        if ('DATABASE_USER' not in database
                and database.get('DATABASE_USERNAME')):
            database['DATABASE_USER'] = database.get('DATABASE_USERNAME')
        if ('DATABASE_USERNAME' not in database
                and database.get('DATABASE_USER')):
            database['DATABASE_USERNAME'] = database.get('DATABASE_USER')
        p['database'] = database

        paths = p.get('paths', {})
        if not isinstance(paths, dict):
            paths = {}
        for key in path_keys:
            if key not in paths and p.get(key):
                paths[key] = p.get(key)
        p['paths'] = paths

        # Keep flat keys available in run-time payload for legacy code paths.
        for key in db_keys:
            if key not in p and database.get(key):
                p[key] = database.get(key)
        for key in path_keys:
            if key not in p and paths.get(key):
                p[key] = paths.get(key)

        if 'DATABASE_USERNAME' in p and 'DATABASE_USER' not in p:
            p['DATABASE_USER'] = p['DATABASE_USERNAME']
        # Preserve legacy flat keys while also providing nested general.
        general = p.get('general', {})
        if not isinstance(general, dict):
            general = {}
        # Normalize preset lowercase keys to task uppercase keys.
        if 'SCIENCE_FIBER' not in general and 'science_fiber' in general:
            general['SCIENCE_FIBER'] = general.get('science_fiber')
        if 'SCIENCE_TYPES' not in general and 'science_types' in general:
            general['SCIENCE_TYPES'] = general.get('science_types')
        if 'INSTRUMENT' not in general and 'instrument' in general:
            general['INSTRUMENT'] = general.get('instrument')
        if 'SCIENCE_FIBER' not in general and p.get('SCIENCE_FIBER'):
            general['SCIENCE_FIBER'] = p.get('SCIENCE_FIBER')
        if 'SCIENCE_TYPES' not in general and p.get('SCIENCE_TYPES'):
            general['SCIENCE_TYPES'] = p.get('SCIENCE_TYPES')
        general['INSTRUMENT'] = instrument
        p['general'] = general
        # Ensure task code receives the instrument in each APERO profile
        # payload.
        p['INSTRUMENT'] = instrument
        mapped[pname] = p
    from pathlib import Path as _Path
    global _scheduler_local_data_dir
    safe_dir = local_data_dir or str(_Path.home() / '.ari')
    _scheduler_local_data_dir = safe_dir
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
        _task_instruments[task_id] = instrument
        _stop_events[task_id] = threading.Event()
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


def stop_all_with_cooldown(instrument: Optional[str] = None) -> Dict[str, Any]:
    """Stop queued tasks and apply per-task cooldown windows.

    Cooldown is set to ``now + frequency`` for each selected task. Running tasks
    are not interrupted, but subsequent enqueue attempts are blocked until the
    cooldown expires.
    """
    from apero_ri.core.auth import load_async_tasks, save_async_tasks

    now = datetime.now(timezone.utc)
    all_tasks = load_async_tasks()

    instruments: List[str]
    if instrument:
        instruments = [instrument] if instrument in all_tasks else []
    else:
        instruments = list(all_tasks.keys())

    with _lock:
        if instrument:
            keep = []
            for queued_instrument, queued_task_id in _queue:
                if queued_instrument == instrument:
                    inst = _instances.get(queued_task_id)
                    if inst is not None:
                        inst.status = 'cancelled'
                        _append_history_entry(
                            queued_instrument,
                            queued_task_id,
                            getattr(inst, 'name', queued_task_id),
                            'cancelled',
                            'Cancelled from queue stop action.',
                        )
                else:
                    keep.append((queued_instrument, queued_task_id))
            _queue[:] = keep
        else:
            for _i, tid in _queue:
                inst = _instances.get(tid)
                if inst is not None:
                    inst.status = 'cancelled'
                    _append_history_entry(
                        _i,
                        tid,
                        getattr(inst, 'name', tid),
                        'cancelled',
                        'Cancelled from queue stop action.',
                    )
            _queue.clear()

    updated = 0
    for inst_key in instruments:
        task_list = all_tasks.get(inst_key, [])
        if not isinstance(task_list, list):
            continue
        for task_cfg in task_list:
            if not isinstance(task_cfg, dict):
                continue
            freq = _normalize_task_frequency(
                task_cfg.get('frequency', 24.0), 24.0)
            cooldown_until = now + timedelta(hours=freq)
            task_cfg['cooldown_until'] = cooldown_until.isoformat()
            task_cfg['last_run'] = now.isoformat()
            task_cfg['last_status'] = 'cancelled'
            updated += 1

    save_async_tasks(all_tasks)
    return {
        'instrument': instrument or 'ALL',
        'updated_tasks': updated,
        'cooldown_set_at': now.isoformat(),
    }


def cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a queued or running task.

    For queued tasks the entry is removed from the queue immediately and the
    instance is marked cancelled.  For a running task the STOP_EVENT is set so
    cooperative tasks can exit early; the worker will mark the task cancelled
    once run_job() returns.
    """
    was_running = False
    was_queued = False
    task_name = task_id
    _inst = ''

    with _lock:
        inst = _instances.get(task_id)
        if inst is not None:
            task_name = str(getattr(inst, 'name', task_id) or task_id)
        # Is it currently running?
        if _current and _current[1] == task_id:
            was_running = True
            _inst = _current[0]
            stop_ev = _stop_events.get(task_id)
            if stop_ev is not None:
                stop_ev.set()
            if inst is not None:
                inst.status = 'cancelling'
        else:
            # Remove from queue
            new_queue = [(i, t) for i, t in _queue if t != task_id]
            if len(new_queue) < len(_queue):
                was_queued = True
                for i, t in _queue:
                    if t == task_id:
                        _inst = i
                        break
                _queue[:] = new_queue
                if inst is not None:
                    inst.status = 'cancelled'

    if not was_running and not was_queued:
        return {'success': False, 'error': 'Task not found in queue or currently running.'}

    # Log and history outside the lock
    log_path_str = _task_log_paths.get(task_id, '')
    if log_path_str:
        _append_task_log_line(
            Path(log_path_str),
            'Cancellation requested by user.' + (' (task is running; waiting for cooperative exit)' if was_running else ''),
        )

    if was_queued:
        _append_history_entry(
            _inst, task_id, task_name, 'cancelled',
            'Cancelled by user from queue.',
        )

    return {
        'success': True,
        'task_id': task_id,
        'was_running': was_running,
        'was_queued': was_queued,
    }


def clear_instance(task_id: str) -> None:
    """Remove a task instance and its error record from memory."""
    with _lock:
        _instances.pop(task_id, None)
        _errors.pop(task_id, None)
        _task_log_paths.pop(task_id, None)
        _task_instruments.pop(task_id, None)
        _stop_events.pop(task_id, None)
        # Remove from queue if present
        _queue[:] = [(i, t) for i, t in _queue if t != task_id]


def get_task_log(task_id: str, lines: int = 400) -> Dict[str, Any]:
    """Return current log content and metadata for one task id."""
    path_str = _log_path_for_task(task_id)
    path = Path(path_str)

    exists = path.is_file()
    content = _tail_lines(path, max(1, int(lines))) if exists else ''
    mtime = None
    if exists:
        try:
            mtime = datetime.fromtimestamp(
                path.stat().st_mtime,
                tz=timezone.utc,
            ).isoformat()
        except Exception:
            mtime = None
    return {
        'task_id': task_id,
        'path': str(path),
        'exists': exists,
        'content': content,
        'updated_at': mtime,
    }


def get_status() -> dict:
    """Return current queue and running-task information."""
    with _lock:
        current_info = None
        if _current is not None:
            curr_instrument, curr_task_id = _current
            curr_inst = _instances.get(curr_task_id)
            current_info = {
                'instrument': curr_instrument,
                'task_id': curr_task_id,
                'task_name': (
                    getattr(curr_inst, 'name', curr_task_id)
                    if curr_inst else curr_task_id
                ),
                'log_path': _log_path_for_task(curr_task_id, curr_instrument),
            }

        queue_info = []
        for q_instrument, q_task_id in _queue:
            q_inst = _instances.get(q_task_id)
            queue_info.append({
                'instrument': q_instrument,
                'task_id': q_task_id,
                'task_name': (
                    getattr(q_inst, 'name', q_task_id)
                    if q_inst else q_task_id
                ),
                'log_path': _log_path_for_task(q_task_id, q_instrument),
            })

        return {
            'current': _current,
            'current_info': current_info,
            'queue': list(_queue),
            'queue_info': queue_info,
            'queue_length': len(_queue),
            'recent_history': get_recent_history(limit=50),
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
        'subprogress': getattr(instance, 'subprogress', 0.0),
        'use_subprocess': bool(getattr(instance, 'USE_SUBPROCESS', False)),
        'info': instance.info,
        'last_run': getattr(instance, 'last_run', 'Never'),
        'output_files': getattr(instance, 'output_files', []),
        'run_params': _sanitize_run_params(
            getattr(instance, '_run_params', {})),
        'run_count': getattr(instance, 'run_count', 0),
        'is_current': is_current,
        'is_queued': is_queued,
        'error': error,
        'log_path': _log_path_for_task(task_id),
    }


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
