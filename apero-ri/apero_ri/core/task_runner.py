#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Background task queue runner.

Manages a global in-memory queue of AperoAsyncTask instances and a daemon
worker thread that processes them one at a time.  Thread-safe via a single
lock protecting _queue, _current, _instances and _errors.
"""

import contextlib
import json
import sys
import threading
import time
import traceback
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.task_runner"
# =============================================================================
# Module-level state
# =============================================================================
# task_id -> AperoAsyncTask instance
_instances: Dict[str, Any] = {}

# ── Named queues ──────────────────────────────────────────────────────────
# Each queue name has its own worker thread so queues run truly in parallel.
# Built-in queue names:
#   'apero_checks'       – APERO_CHECK_TASK tasks (quick, profile-bound)
#   'global'             – GLOBAL-type async tasks (backups, syncs, …)
#   'instrument_{NAME}'  – per-instrument INSTRUMENT-type tasks; the NAME is
#                          the uppercase instrument string, e.g. 'SPIROU'.
#
# Each queue is a list of (instrument, task_id) tuples (FIFO).
_queues:         Dict[str, List[Tuple[str, str]]] = {}
_currents:       Dict[str, Optional[Tuple[str, str]]] = {}
_worker_threads: Dict[str, Optional[threading.Thread]] = {}

# Legacy aliases kept so existing code that reads _queue / _current directly
# still works.  They always point at the 'global' queue / current.
def _global_queue() -> List[Tuple[str, str]]:
    return _queues.setdefault("global", [])

# task_id -> full traceback string on failure
_errors: Dict[str, str] = {}

_lock = threading.Lock()
_scheduler_thread: Optional[threading.Thread] = None

# ─────────────────────────────────────────────────────────────────────────
# Back-compat shims – code that references _queue / _current / _worker_thread
# directly will continue to work against the 'global' queue.
# ─────────────────────────────────────────────────────────────────────────
def _get_queue(name: str) -> List[Tuple[str, str]]:
    """Return (creating if needed) the named queue list."""
    return _queues.setdefault(name, [])

def _get_current(name: str) -> Optional[Tuple[str, str]]:
    return _currents.get(name)

def _set_current(name: str, val: Optional[Tuple[str, str]]) -> None:
    _currents[name] = val

def _all_queued() -> List[Tuple[str, str]]:
    """Return a flat list of every pending entry across all queues."""
    out: List[Tuple[str, str]] = []
    for q in _queues.values():
        out.extend(q)
    return out

def _all_currents() -> List[Tuple[str, str]]:
    """Return a list of all currently-executing entries (one per worker)."""
    return [c for c in _currents.values() if c is not None]
_scheduler_local_data_dir = str(Path.home() / ".ari")
_scheduler_poll_seconds = 30.0
_async_tasks_rel_dir = Path("admin") / "async_tasks"
_history_relpath = _async_tasks_rel_dir / "async_history.txt"
_task_logs_rel_dir = _async_tasks_rel_dir / "task_logs"
_task_info_rel_dir = _async_tasks_rel_dir / "task_info"
_task_errors_rel_dir = _async_tasks_rel_dir / "task_errors"
_aprofile_preset_cache: Dict[str, dict] = {}
_task_log_paths: Dict[str, str] = {}
_task_instruments: Dict[str, str] = {}
_stop_events: Dict[str, threading.Event] = {}
_shutdown_event = threading.Event()


class _TaskLogTeeStream:
    """Tee stream that forwards output and writes timestamped log lines."""

    def __init__(self, path: Path, sink: Any, stream_tag: str):
        self._path = path
        self._sink = sink
        self._stream_tag = stream_tag
        self._buffer = ""

    def write(self, data: Any) -> int:
        text = str(data or "")
        if not text:
            return 0
        try:
            self._sink.write(text)
        except Exception:
            pass
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.rstrip("\r")
            if line.strip():
                _append_task_log_line(
                    self._path,
                    f"[{self._stream_tag}] {line}",
                )
        return len(text)

    def flush(self) -> None:
        if self._buffer.strip():
            _append_task_log_line(
                self._path, f"[{self._stream_tag}] {self._buffer.rstrip()}"
            )
        self._buffer = ""
        try:
            self._sink.flush()
        except Exception:
            pass


# =============================================================================
# Define functions
# =============================================================================
def _is_global_scope(instrument: str) -> bool:
    """Return True if this scope key represents global async tasks."""
    return str(instrument).strip() == "__GLOBAL__"


def _task_keys_for_scope(task_module: Any, instrument: str) -> List[str]:
    """Return task keys allowed in this scope from tasks.TYPE."""
    want_type = "GLOBAL" if _is_global_scope(instrument) else "INSTRUMENT"
    keys: List[str] = []
    for task_key in task_module.TASK_LIST.keys():
        ttype = (
            str(task_module.TYPE.get(task_key, "INSTRUMENT")).strip().upper()
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
    sensitive_tokens = ["password", "passwd", "secret", "token", "api_key"]

    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        for key, item in value.items():
            key_str = str(key)
            key_lower = key_str.lower()
            if any(token in key_lower for token in sensitive_tokens):
                out[key_str] = "***REDACTED***"
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
        / "resources"
        / "aprofile_instruments"
    )
    path = resources_dir / profile_file
    if not path.is_file():
        _aprofile_preset_cache[profile_file] = {}
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
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
    return Path(_scheduler_local_data_dir) / "admin" / "async_history.txt"


def _safe_scope_name(value: str) -> str:
    """Return a filesystem-safe identifier for instrument scope names."""
    text = str(value or "").strip()
    if not text:
        return "unknown"
    cleaned = "".join(c if c.isalnum() or c in "-_." else "_" for c in text)
    return cleaned or "unknown"


def _profile_history_file_path(profile_id: str) -> Path:
    """Return the per-profile APERO-check history file path.

    Stored separately from the global async history so profile history
    is persistent across global clears and carries log_path.
    """
    safe = _safe_scope_name(str(profile_id or ""))
    return (
        Path(_scheduler_local_data_dir)
        / _async_tasks_rel_dir
        / f"apero_checks_{safe}.jsonl"
    )


def append_profile_check_history(
    profile_id: str,
    task_id: str,
    task_name: str,
    status: str,
    details: str = "",
    log_path: str = "",
    duration_seconds: Optional[float] = None,
    obsdir: str = "",
    check_key: str = "",
    task_mode: str = "",
) -> None:
    """Append one entry to the per-profile APERO-check history file."""
    try:
        path = _profile_history_file_path(profile_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": str(task_id or ""),
            "task_name": str(task_name or task_id or ""),
            "status": str(status or ""),
            "details": str(details or ""),
            "log_path": str(log_path or ""),
            "obsdir": str(obsdir or ""),
            "check_key": str(check_key or ""),
            "task_mode": str(task_mode or ""),
        }
        if duration_seconds is not None:
            payload["duration_seconds"] = round(float(duration_seconds), 3)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def get_profile_check_history(profile_id: str,
                               limit: int = 200) -> List[Dict[str, Any]]:
    """Return newest per-profile APERO-check history entries (newest first)."""
    try:
        path = _profile_history_file_path(profile_id)
        if not path.exists() or limit <= 0:
            return []
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        out: List[Dict[str, Any]] = []
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                out.append({
                    "timestamp": str(row.get("timestamp", "")),
                    "task_id": str(row.get("task_id", "")),
                    "task_name": str(row.get("task_name", "") or row.get("task_id", "")),
                    "status": str(row.get("status", "")),
                    "details": str(row.get("details", "")),
                    "log_path": str(row.get("log_path", "")),
                    "obsdir": str(row.get("obsdir", "")),
                    "check_key": str(row.get("check_key", "")),
                    "task_mode": str(row.get("task_mode", "")),
                    "duration_seconds": row.get("duration_seconds"),
                })
            except Exception:
                continue
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []


def clear_profile_check_history(profile_id: str) -> Dict[str, Any]:
    """Clear the per-profile APERO-check history file."""
    try:
        path = _profile_history_file_path(profile_id)
        if path.exists():
            path.write_text("", encoding="utf-8")
            return {"cleared": True, "path": str(path)}
        return {"cleared": False, "reason": "file not found"}
    except Exception as exc:
        return {"cleared": False, "reason": str(exc)}


def _task_log_file_path(instrument: str, task_id: str) -> Path:
    """Return per-task current log file path."""
    base = Path(_scheduler_local_data_dir) / _task_logs_rel_dir
    scope = _safe_scope_name(instrument or "GLOBAL")
    name = _safe_scope_name(task_id)
    return base / f"{scope}__{name}.log"


def _task_info_file_path(instrument: str, task_id: str) -> Path:
    """Return per-task info markdown path."""
    base = Path(_scheduler_local_data_dir) / _task_info_rel_dir
    scope = _safe_scope_name(instrument or "GLOBAL")
    name = _safe_scope_name(task_id)
    return base / f"{scope}__{name}.md"


def _task_error_file_path(instrument: str, task_id: str) -> Path:
    """Return per-task error text path."""
    base = Path(_scheduler_local_data_dir) / _task_errors_rel_dir
    scope = _safe_scope_name(instrument or "GLOBAL")
    name = _safe_scope_name(task_id)
    return base / f"{scope}__{name}.txt"


def _append_task_log_line(path: Path, message: str) -> None:
    """Append one timestamped line to task log file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f'{stamp} | {str(message or "")}\n')
    except Exception:
        pass


def _prepare_task_log(instrument: str, task_id: str, task_name: str) -> Path:
    """Create/overwrite the per-task current log and return its path."""
    path = _task_log_file_path(instrument, task_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    except Exception:
        pass
    _append_task_log_line(path, f"Task queued: {task_name} [{task_id}]")
    with _lock:
        _task_log_paths[task_id] = str(path)
        _task_instruments[task_id] = instrument
    return path


def _make_task_logger(log_path: Path):
    """Build a callable logger injected into task run params."""

    def _log_fn(message: Any) -> None:
        _append_task_log_line(log_path, str(message or ""))

    return _log_fn


def _tail_lines(path: Path, lines: int) -> str:
    """Return at most the last ``lines`` from a UTF-8 text file."""
    try:
        raw_lines = path.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
    except Exception:
        return ""
    if lines <= 0 or len(raw_lines) <= lines:
        return "\n".join(raw_lines)
    return "\n".join(raw_lines[-lines:])


def _log_path_for_task(task_id: str, instrument: str = "") -> str:
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
    scope = instrument or _task_instruments.get(task_id, "")
    return str(_task_log_file_path(scope, task_id))


def _resolve_existing_task_log_file(task_id: str) -> Optional[Path]:
    """Return most recent on-disk task log path for task id, if present."""
    try:
        safe_task = _safe_scope_name(task_id)
        candidates: List[Path] = []
        base_new = Path(_scheduler_local_data_dir) / _task_logs_rel_dir
        candidates.extend(list(base_new.glob(f"*__{safe_task}.log")))
        # Legacy location (before admin/async_tasks/task_logs migration)
        base_old = Path(_scheduler_local_data_dir) / "admin" / "async_task_logs"
        candidates.extend(list(base_old.glob(f"*__{safe_task}.log")))
        if not candidates:
            return None
        candidates.sort(
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        return candidates[0]
    except Exception:
        return None


def _resolve_existing_task_data_file(
    task_id: str, rel_dir: Path, suffix: str
) -> Optional[Path]:
    """Return newest persisted per-task data file by task id."""
    try:
        base = Path(_scheduler_local_data_dir) / rel_dir
        safe_task = _safe_scope_name(task_id)
        candidates = list(base.glob(f"*__{safe_task}{suffix}"))
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
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _write_text_file(path: Path, content: str) -> None:
    """Write UTF-8 text file safely; ignore write failures."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(content or ""), encoding="utf-8")
    except Exception:
        pass


def _persist_task_info_error(
    instrument: str, task_id: str, info: str, error: str
) -> None:
    """Persist task info/error payloads in dedicated files."""
    _write_text_file(_task_info_file_path(instrument, task_id), info or "")
    _write_text_file(_task_error_file_path(instrument, task_id), error or "")


def get_persisted_task_info_error(task_id: str) -> Dict[str, str]:
    """Return persisted task info/error from dedicated files."""
    scope = _task_instruments.get(task_id, "")
    info_path = _task_info_file_path(scope, task_id)
    err_path = _task_error_file_path(scope, task_id)

    info = _read_text_file(info_path)
    error = _read_text_file(err_path)

    if not info:
        found = _resolve_existing_task_data_file(
            task_id, _task_info_rel_dir, ".md"
        )
        if found is not None:
            info = _read_text_file(found)
    if not error:
        found = _resolve_existing_task_data_file(
            task_id, _task_errors_rel_dir, ".txt"
        )
        if found is not None:
            error = _read_text_file(found)

    return {"info": info, "error": error}


def _append_history_entry(
    instrument: str,
    task_id: str,
    task_name: str,
    status: str,
    details: str = "",
    duration_seconds: Optional[float] = None,
) -> None:
    """Append one history entry to async history file as JSON line."""
    try:
        path = _history_file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "instrument": str(instrument or ""),
            "task_id": str(task_id or ""),
            "task_name": str(task_name or task_id or ""),
            "status": str(status or ""),
            "details": str(details or ""),
        }
        if duration_seconds is not None:
            payload["duration_seconds"] = round(float(duration_seconds), 3)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
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
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        out: List[Dict[str, Any]] = []
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                out.append(
                    {
                        "timestamp": str(row.get("timestamp", "")),
                        "instrument": str(row.get("instrument", "")),
                        "task_id": str(row.get("task_id", "")),
                        "task_name": str(
                            row.get("task_name", "") or row.get("task_id", "")
                        ),
                        "status": str(row.get("status", "")),
                        "details": str(row.get("details", "")),
                        "duration_seconds": row.get("duration_seconds"),
                    }
                )
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
                    path.read_text(
                        encoding="utf-8", errors="replace"
                    ).splitlines()
                )
            except Exception:
                removed = 0
        elif legacy.exists():
            try:
                removed = len(
                    legacy.read_text(
                        encoding="utf-8", errors="replace"
                    ).splitlines()
                )
            except Exception:
                removed = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        try:
            if legacy.exists():
                legacy.unlink()
        except Exception:
            pass
        return {"success": True, "removed": removed}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# =============================================================================
# Sync-source override
# =============================================================================
def _run_sync_source_override(
    instance: Any,
    run_params: Dict[str, Any],
    sync_source: str,
    instrument: str,
    log_path: Path,
) -> None:
    """Copy pre-built task output files from *sync_source* into LOCAL_DATA_DIR.

    When a task's TASK_CONFIG contains ``sync_source`` (a directory path,
    typically an SSHFS mount or an rsync'd mirror produced by
    ``apero_sync.run()`` on the remote host), the server skips ``run_job``
    entirely and instead copies the result JSON files from that path into
    the local tasks directory.

    The source layout is expected to mirror the standard output layout::

        <sync_source>/tasks/<INSTRUMENT>/<profile>/…

    Files are copied to::

        <LOCAL_DATA_DIR>/tasks/<INSTRUMENT>/<profile>/…
    """
    import shutil

    tlog = _make_task_logger(log_path)

    source = Path(sync_source).expanduser().resolve()
    if not source.is_dir():
        raise FileNotFoundError(
            f"sync_source directory does not exist: {source}"
        )

    local_data_dir = (
        Path(run_params.get("LOCAL_DATA_DIR") or str(Path.home() / ".ari"))
        .expanduser()
        .resolve()
    )

    synced: List[str] = []
    skipped = 0
    errors: List[str] = []

    # Walk the source tasks directory tree and copy all files
    source_tasks = source / "tasks"
    if not source_tasks.is_dir():
        # If the source is already the tasks/<instrument> level, handle that
        source_tasks = source

    tlog(f"sync_source: scanning {source_tasks}")

    for src_file in source_tasks.rglob("*"):
        if src_file.is_dir():
            continue
        try:
            rel = src_file.relative_to(source_tasks)
        except ValueError:
            skipped += 1
            continue

        dst_file = local_data_dir / "tasks" / rel
        try:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(dst_file))
            synced.append(str(dst_file))
        except Exception as exc:
            errors.append(f"{rel}: {exc}")

    tlog(
        f"sync_source: copied {len(synced)} files, "
        f"skipped {skipped}, errors {len(errors)}."
    )

    instance.output_files = synced
    instance.info = (
        f"## Sync Source Override\n\n"
        f"- Source: `{source}`\n"
        f"- Files copied: {len(synced)}\n"
        f"- Errors: {len(errors)}\n"
    )
    if errors:
        instance.info += "\n### Errors\n"
        for err in errors[:20]:
            instance.info += f"- {err}\n"

    instance.last_run = datetime.now(timezone.utc).isoformat()
    instance.progress = 1.0


def _resolve_sync_profile_source_dir(
    sync_source: str,
    instrument: str,
    profile_name: str,
) -> Path:
    """Resolve a precomputed source path for one APERO profile."""
    source = Path(sync_source).expanduser().resolve()
    if not source.is_dir():
        raise FileNotFoundError(
            f"sync_source directory does not exist: {source}"
        )

    candidates = [
        source / "tasks" / instrument / profile_name,
        source / instrument / profile_name,
        source / profile_name,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate

    has_root_tree = (
        (source / "tasks").exists()
        or (source / instrument).exists()
    )
    if not has_root_tree:
        return source

    raise FileNotFoundError(
        "Could not resolve sync_source for profile "
        f"{profile_name}: {source}"
    )


def _copy_sync_profile_override(
    run_params: Dict[str, Any],
    sync_source: str,
    instrument: str,
    profile_name: str,
    log_path: Path,
) -> List[str]:
    """Copy precomputed output files for one APERO profile."""
    import shutil

    tlog = _make_task_logger(log_path)
    source_dir = _resolve_sync_profile_source_dir(
        sync_source,
        instrument,
        profile_name,
    )
    local_data_dir = (
        Path(run_params.get("LOCAL_DATA_DIR") or str(Path.home() / ".ari"))
        .expanduser()
        .resolve()
    )
    dest_root = local_data_dir / "tasks" / instrument / profile_name
    synced = []
    stop_event = run_params.get("STOP_EVENT")

    tlog(
        "sync_source: profile "
        f"{profile_name} from {source_dir} to {dest_root}"
    )

    source_files = []
    for src_file in source_dir.rglob("*"):
        if src_file.is_dir() or src_file.is_symlink():
            continue
        source_files.append(src_file)

    total = len(source_files)
    tlog(
        "sync_source: profile "
        f"{profile_name} discovered {total} file(s)"
    )

    for idx, src_file in enumerate(source_files, start=1):
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("Task cancelled while syncing pre-computed data")

        rel = src_file.relative_to(source_dir)
        dst_file = dest_root / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        # Always overwrite: a previously-synced destination can have the
        # same size and mtime as the source even when the content has
        # been regenerated (e.g. ftable JSON with the same row count
        # but updated KW_OUTPUT values). Trusting size+mtime as a skip
        # heuristic would leave stale rows on the local server forever
        # once the first sync has run. fetch_precomputed must mean
        # "the remote is authoritative — copy unconditionally".
        shutil.copy2(str(src_file), str(dst_file))
        synced.append(str(dst_file))

        if idx % 250 == 0 or idx == total:
            tlog(
                "sync_source: profile "
                f"{profile_name} progress {idx}/{total} "
                f"(copied={len(synced)})"
            )

    tlog(
        "sync_source: profile "
        f"{profile_name} finished (copied={len(synced)})"
    )
    return synced


def _split_sync_profile_modes(
    run_params: Dict[str, Any],
    task_cfg: Dict[str, Any],
) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Split APERO profiles into sync and server-run groups."""
    raw = task_cfg.get("sync_profiles", {})
    if not isinstance(raw, dict):
        return [], list(run_params.get("APERO_PROFILE_NAMES") or [])

    sync_profiles = []
    run_server_profiles = []
    for profile_name in run_params.get("APERO_PROFILE_NAMES") or []:
        entry = raw.get(profile_name, {})
        if not isinstance(entry, dict):
            run_server_profiles.append(profile_name)
            continue
        mode = str(entry.get("mode", "run_server") or "run_server")
        mode = mode.strip().lower()
        sync_source = str(entry.get("sync_source", "") or "").strip()
        if mode == "fetch_precomputed" and sync_source:
            sync_profiles.append((profile_name, sync_source))
        else:
            run_server_profiles.append(profile_name)
    return sync_profiles, run_server_profiles


def _append_sync_profile_info(
    instance: Any,
    sync_profiles: List[Tuple[str, str]],
    synced_files: List[str],
) -> None:
    """Append a short sync summary to the task info markdown."""
    if not sync_profiles:
        return

    lines = [
        "## Pre-computed Profiles",
        "",
        f"- Profiles synced: {len(sync_profiles)}",
        f"- Files copied: {len(synced_files)}",
    ]
    for profile_name, sync_source in sync_profiles:
        lines.append(
            f"- {profile_name}: `{sync_source}`"
        )
    block = "\n".join(lines)
    info = str(getattr(instance, "info", "") or "").strip()
    if info:
        instance.info = info + "\n\n" + block
    else:
        instance.info = block


# =============================================================================
# Worker
# =============================================================================
def _execute_task(_inst: str, task_id: str) -> None:
    """Execute one task identified by instrument and task_id.

    Called by both the general worker and the APERO-checks worker after
    they pop an entry from their respective queues.
    """
    instance = _instances.get(task_id)
    if instance is None:
        return  # should not happen; caller clears current in finally

    instance.status = "in_progress"
    start_time = time.perf_counter()
    run_params = dict(getattr(instance, "_run_params", {}) or {})
    task_name = str(getattr(instance, "name", task_id) or task_id)
    log_path = _prepare_task_log(_inst, task_id, task_name)
    run_params["TASK_LOG_PATH"] = str(log_path)
    run_params["TASK_LOGGER"] = _make_task_logger(log_path)
    run_params["STOP_EVENT"] = _stop_events.get(task_id, threading.Event())
    instance._run_params = run_params
    instance._task_log_path = str(log_path)
    _append_task_log_line(log_path, "Task execution started.")
    try:
        # Treat task output files as this-run artifacts.
        instance.output_files = []

        # ── sync_source override ────────────────────────────────────
        # When a task has sync_source configured, copy pre-built
        # results from that path instead of running the task.
        task_cfg = run_params.get("TASK_CONFIG", {})
        sync_source = str(task_cfg.get("sync_source", "") or "").strip()
        sync_profiles, run_server_profiles = _split_sync_profile_modes(
            run_params,
            task_cfg,
        )
        local_task_enabled = False
        try:
            from apero_ri import tasks as task_module

            task_key = str(getattr(instance, "_task_key", "") or "").strip()
            local_task_enabled = bool(
                task_module.LOCAL_TASK.get(task_key, False)
            )
        except Exception:
            local_task_enabled = False

        if sync_profiles and local_task_enabled:
            synced_files = []
            for profile_name, profile_source in sync_profiles:
                synced_files.extend(
                    _copy_sync_profile_override(
                        run_params,
                        profile_source,
                        _inst,
                        profile_name,
                        log_path,
                    )
                )

            if run_server_profiles:
                subset_params = dict(run_params)
                profile_map = dict(
                    run_params.get("APERO_PROFILES", {}) or {}
                )
                subset_params["APERO_PROFILE_NAMES"] = list(
                    run_server_profiles
                )
                subset_params["APERO_PROFILES"] = dict(
                    (profile_name, profile_map[profile_name])
                    for profile_name in run_server_profiles
                    if profile_name in profile_map
                )
                stdout_tee = _TaskLogTeeStream(
                    log_path, sink=sys.stdout, stream_tag="stdout"
                )
                stderr_tee = _TaskLogTeeStream(
                    log_path, sink=sys.stderr, stream_tag="stderr"
                )
                with contextlib.redirect_stdout(
                    stdout_tee
                ), contextlib.redirect_stderr(stderr_tee):
                    instance.run_job(subset_params)
                stdout_tee.flush()
                stderr_tee.flush()

            current_files = list(
                getattr(instance, "output_files", []) or []
            )
            current_files.extend(synced_files)
            instance.output_files = _dedupe_strings(current_files)
            _append_sync_profile_info(
                instance,
                sync_profiles,
                synced_files,
            )
        elif sync_source and local_task_enabled:
            _run_sync_source_override(
                instance,
                run_params,
                sync_source,
                _inst,
                log_path,
            )
        elif sync_source and not local_task_enabled:
            _append_task_log_line(
                log_path,
                "sync_source ignored: task does not support "
                "LOCAL_TASK override.",
            )
            stdout_tee = _TaskLogTeeStream(
                log_path, sink=sys.stdout, stream_tag="stdout"
            )
            stderr_tee = _TaskLogTeeStream(
                log_path, sink=sys.stderr, stream_tag="stderr"
            )
            with contextlib.redirect_stdout(
                stdout_tee
            ), contextlib.redirect_stderr(stderr_tee):
                instance.run_job(run_params)
            stdout_tee.flush()
            stderr_tee.flush()
        else:
            stdout_tee = _TaskLogTeeStream(
                log_path, sink=sys.stdout, stream_tag="stdout"
            )
            stderr_tee = _TaskLogTeeStream(
                log_path, sink=sys.stderr, stream_tag="stderr"
            )
            with contextlib.redirect_stdout(
                stdout_tee
            ), contextlib.redirect_stderr(stderr_tee):
                instance.run_job(run_params)
            stdout_tee.flush()
            stderr_tee.flush()

        stop_ev = _stop_events.get(task_id)
        if stop_ev is not None and stop_ev.is_set():
            instance.status = "cancelled"
            _append_task_log_line(
                log_path, "Task cancelled by user request."
            )
        else:
            instance.status = "completed"
            _append_task_log_line(
                log_path, "Task execution completed successfully."
            )
    except Exception:
        instance.status = "failed"
        _append_task_log_line(
            log_path, "Task execution failed. Traceback follows:"
        )
        for line in traceback.format_exc().splitlines():
            if line.strip():
                _append_task_log_line(log_path, line)
        with _lock:
            _errors[task_id] = traceback.format_exc()
    finally:
        duration_seconds = max(0.0, time.perf_counter() - start_time)
        _append_task_log_line(
            log_path,
            f"Task finished with status={instance.status} in "
            f"{duration_seconds:.2f}s.",
        )
        instance.run_count = getattr(instance, "run_count", 0) + 1
        instance.last_run = datetime.now(timezone.utc).isoformat()
        task_status = getattr(instance, "status", "")
        task_error = (
            ""
            if task_status != "failed"
            else _errors.get(task_id, "")
        )
        _append_history_entry(
            _inst,
            task_id,
            getattr(instance, "name", task_id),
            task_status,
            task_error,
            duration_seconds=duration_seconds,
        )
        # Write per-profile history for manual APERO check tasks.
        if str(task_id or "").startswith("manual_apero_check__"):
            try:
                task_cfg = dict(
                    getattr(instance, "_run_params", {}).get("TASK_CONFIG", {}) or {}
                )
                filters = task_cfg.get("filters", {}) or {}
                profile_id = str(
                    filters.get("APERO_PROFILE_INCLUDE", "") or ""
                ).strip()
                if profile_id:
                    # Decode obsdir/check from task_id slug
                    # Format: manual_apero_check__{profile}__{obsdir}__{mode}__{check}__uuid
                    parts = task_id.split("__")
                    # parts[0]='manual_apero_check', parts[1]=profile_slug,
                    # parts[2]=obsdir_slug, parts[3]=mode, parts[4]=check, parts[5]=uuid
                    obs_dir = ""
                    check_key = ""
                    task_mode = ""
                    if len(parts) >= 4:
                        obs_dir = parts[2].replace("_", "-")
                    if len(parts) >= 5:
                        task_mode = parts[3]
                    if len(parts) >= 6:
                        check_key_raw = parts[4]
                        check_key = "" if check_key_raw.lower() == "all" else check_key_raw.upper()
                    append_profile_check_history(
                        profile_id=profile_id,
                        task_id=task_id,
                        task_name=getattr(instance, "name", task_id),
                        status=task_status,
                        details=task_error[:2000] if task_error else "",
                        log_path=str(log_path),
                        duration_seconds=duration_seconds,
                        obsdir=obs_dir,
                        check_key=check_key,
                        task_mode=task_mode,
                    )
            except Exception:
                pass
        _persist_runtime_state(_inst, task_id, instance)
        # NOTE: the caller (worker loop) clears _current / _apero_check_current.


def _make_worker(queue_name: str):
    """Return a daemon-worker function that processes the named queue."""
    def _worker() -> None:
        while not _shutdown_event.is_set():
            entry: Optional[Tuple[str, str]] = None
            with _lock:
                q = _queues.get(queue_name, [])
                if q:
                    entry = q.pop(0)
                    _currents[queue_name] = entry
            if entry is None:
                _shutdown_event.wait(0.5)
                continue
            try:
                _execute_task(*entry)
            finally:
                with _lock:
                    _currents[queue_name] = None
    _worker.__name__ = "ari-worker-%s" % queue_name
    return _worker


# Keep named functions for clarity in thread listings.
_run_worker = _make_worker("global")
_run_apero_check_worker = _make_worker("apero_checks")


def _persist_runtime_state(
    instrument: str, task_id: str, instance: Any
) -> None:
    """Write runtime fields back to async_tasks.yaml after each run."""
    try:
        from apero_ri.core.auth import load_async_tasks, save_async_tasks

        with _lock:
            error = _errors.get(task_id, "")
        all_tasks = load_async_tasks()
        for tc in all_tasks.get(instrument, []):
            if tc.get("id") == task_id:
                tc["last_run"] = getattr(instance, "last_run", "Never")
                tc["run_count"] = getattr(instance, "run_count", 0)
                tc["output_files"] = _dedupe_strings(
                    getattr(instance, "output_files", [])
                )
                tc["last_run_params"] = _sanitize_run_params(
                    getattr(instance, "_run_params", {})
                )
                tc["last_status"] = getattr(instance, "status", "failed")
                tc.pop("info", None)
                tc.pop("error", None)
                break
        _persist_task_info_error(
            instrument,
            task_id,
            getattr(instance, "info", ""),
            error,
        )
        save_async_tasks(all_tasks)
    except Exception:
        pass  # Never let persistence failures crash the worker


_QUEUE_THREAD_NAMES = {
    "apero_checks": "ari-apero-check-worker",
    "global":       "ari-task-worker",
}


def _ensure_queue_worker(queue_name: str) -> None:
    """Ensure a live worker thread exists for *queue_name*.

    Worker threads are created on demand so new instrument queues appear
    automatically the first time a task is routed to them.
    """
    t = _worker_threads.get(queue_name)
    if t is None or not t.is_alive():
        thread_name = _QUEUE_THREAD_NAMES.get(
            queue_name,
            "ari-worker-%s" % queue_name,
        )
        _queues.setdefault(queue_name, [])
        _currents.setdefault(queue_name, None)
        new_t = threading.Thread(
            target=_make_worker(queue_name),
            daemon=True,
            name=thread_name,
        )
        _worker_threads[queue_name] = new_t
        new_t.start()


# Back-compat shims
def _ensure_worker() -> None:
    _ensure_queue_worker("global")

def _ensure_apero_check_worker() -> None:
    _ensure_queue_worker("apero_checks")


def _parse_last_run(value: Any) -> Optional[datetime]:
    """Parse a stored last-run timestamp."""
    if not value or value == "Never":
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


def hydrate_runtime_state(
    instance: Any, task_cfg: Optional[dict] = None
) -> Any:
    """Copy persisted runtime fields onto a new task instance."""
    cfg = task_cfg or {}
    instance.last_run = cfg.get(
        "last_run", getattr(instance, "last_run", "Never")
    )
    instance.run_count = _coerce_run_count(
        cfg.get("run_count", getattr(instance, "run_count", 0))
    )
    instance.info = cfg.get("info", getattr(instance, "info", ""))
    instance.output_files = _dedupe_strings(
        cfg.get("output_files", getattr(instance, "output_files", [])) or []
    )
    return instance


def _task_is_busy(task_id: str) -> bool:
    """Return True if a task is already queued or running (any queue)."""
    with _lock:
        if any(c[1] == task_id for c in _all_currents()):
            return True
        return any(t == task_id for _, t in _all_queued())


def _task_is_due(task_cfg: dict, now: datetime) -> bool:
    """Return True if a task should be enqueued by the scheduler."""
    if not task_cfg.get("active", True):
        return False

    cooldown_until = _parse_last_run(task_cfg.get("cooldown_until"))
    if cooldown_until is not None and now < cooldown_until:
        return False

    task_id = str(task_cfg.get("id", "") or "").strip()
    if not task_id or _task_is_busy(task_id):
        return False

    try:
        frequency_hours = float(task_cfg.get("frequency", 0) or 0)
    except (TypeError, ValueError):
        return False
    if frequency_hours <= 0:
        return False

    last_run = _parse_last_run(task_cfg.get("last_run"))
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
        if sval in ["true", "1", "yes", "on"]:
            return True
        if sval in ["false", "0", "no", "off", ""]:
            return False
    return bool(value)


def can_enqueue_now(
    task_cfg: dict, now: Optional[datetime] = None
) -> Tuple[bool, str]:
    """Return whether a task may be manually enqueued right now."""
    now_utc = now or datetime.now(timezone.utc)

    if not task_cfg.get("active", True):
        return False, "Task is inactive."

    task_id = str(task_cfg.get("id", "") or "").strip()
    if not task_id:
        return False, "Task id is missing."

    if _task_is_busy(task_id):
        return False, "Task is already queued or running."

    cooldown_until = _parse_last_run(task_cfg.get("cooldown_until"))
    if cooldown_until is not None and now_utc < cooldown_until:
        return False, f"Task is in cooldown until {cooldown_until.isoformat()}."

    return True, ""


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
                Path(local_data_dir)
                / "admin"
                / "async_tasks"
                / "scheduler.lock"
            )
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_handle = lock_path.open("a+")
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return

        import uuid as uuid_module

        from apero_ri import tasks as task_module
        from apero_ri.core.auth import (
            load_apero_profiles,
            load_async_tasks,
            save_async_tasks,
        )

        import_errors = getattr(task_module, "IMPORT_ERRORS", {}) or {}

        all_tasks = load_async_tasks()
        all_profiles = load_apero_profiles(enabled_only=True)
        now = datetime.now(timezone.utc)
        changed = False

        if "__GLOBAL__" not in all_tasks:
            all_tasks["__GLOBAL__"] = []
            changed = True

        for instrument, task_list in all_tasks.items():
            if not isinstance(task_list, list):
                continue

            stored_tasks = task_list
            by_key = {}
            for task_cfg in stored_tasks:
                if not isinstance(task_cfg, dict):
                    continue
                key = str(task_cfg.get("task_key", "")).strip()
                if key and key not in by_key:
                    by_key[key] = task_cfg

            merged = []
            task_keys = _task_keys_for_scope(task_module, instrument)
            for idx, task_key in enumerate(task_keys, start=1):
                task_cfg = dict(by_key.get(task_key, {}))
                task_id = str(task_cfg.get("id", "")).strip()
                if not task_id:
                    task_id = str(
                        uuid_module.uuid5(
                            uuid_module.NAMESPACE_URL,
                            f"ari-async-task:{instrument}:{task_key}",
                        )
                    )
                    changed = True

                default_freq = _normalize_task_frequency(
                    task_module.FREQ.get(task_key, 24.0), 24.0
                )
                default_enabled = _normalize_task_enabled(
                    task_module.ENABLED.get(task_key, False), False
                )

                merged_cfg = {
                    "id": task_id,
                    "task_key": task_key,
                    "frequency": _normalize_task_frequency(
                        task_cfg.get("frequency", default_freq), default_freq
                    ),
                    "active": _normalize_task_enabled(
                        task_cfg.get("active", default_enabled), default_enabled
                    ),
                    "order": idx,
                }

                # Preserve multiprocessing settings so scheduler merges do not
                # silently reset task parallelism back to defaults.
                supports_mp = bool(
                    task_module.MULTI_PROCESS.get(task_key, False)
                )
                keep_mp = supports_mp or any(
                    key in task_cfg
                    for key in ["ncores", "mp_backend", "mp_start_method"]
                )
                if keep_mp:
                    try:
                        ncores = int(task_cfg.get("ncores", 1) or 1)
                    except (TypeError, ValueError):
                        ncores = 1
                    merged_cfg["ncores"] = max(1, ncores)

                    backend = (
                        str(task_cfg.get("mp_backend", "threads") or "threads")
                        .strip()
                        .lower()
                    )
                    if backend not in ["threads", "processes"]:
                        backend = "threads"
                    merged_cfg["mp_backend"] = backend

                    start_method = (
                        str(
                            task_cfg.get("mp_start_method", "default")
                            or "default"
                        )
                        .strip()
                        .lower()
                    )
                    if start_method not in [
                        "default",
                        "spawn",
                        "fork",
                        "forkserver",
                    ]:
                        start_method = "default"
                    merged_cfg["mp_start_method"] = start_method

                if task_key == "ARI_LOCAL_DATA_BACKUP":
                    try:
                        daily_copies = int(task_cfg.get("daily_copies", 7) or 0)
                    except (TypeError, ValueError):
                        daily_copies = 7
                    try:
                        weekly_copies = int(
                            task_cfg.get("weekly_copies", 4) or 0
                        )
                    except (TypeError, ValueError):
                        weekly_copies = 4
                    merged_cfg["daily_copies"] = max(0, daily_copies)
                    merged_cfg["weekly_copies"] = max(0, weekly_copies)
                    from apero_ri.tasks.apero_backup import (
                        DEFAULT_BACKUP_MAX_SIZE_MB,
                    )
                    try:
                        backup_max_mb = float(
                            task_cfg.get(
                                "backup_max_size_mb",
                                DEFAULT_BACKUP_MAX_SIZE_MB,
                            )
                        )
                    except (TypeError, ValueError):
                        backup_max_mb = float(DEFAULT_BACKUP_MAX_SIZE_MB)
                    if backup_max_mb <= 0:
                        backup_max_mb = float(DEFAULT_BACKUP_MAX_SIZE_MB)
                    merged_cfg["backup_max_size_mb"] = backup_max_mb
                    # Pass through admin-customised exclude lists.
                    for _key in ("exclude_dirs", "exclude_paths"):
                        _val = task_cfg.get(_key)
                        if isinstance(_val, list):
                            cleaned = []
                            for _item in _val:
                                _s = str(_item or "").strip()
                                if _s and _s not in cleaned:
                                    cleaned.append(_s)
                            if cleaned:
                                merged_cfg[_key] = cleaned

                if task_key == "APERO_SYNC_ASSETS":
                    mode_val = str(
                        task_cfg.get("mode") or "remote"
                    ).strip().lower()
                    # backwards compatibility with legacy mode names
                    if mode_val in ("sync", "upload", "remote"):
                        mode_val = "remote"
                    elif mode_val == "local":
                        mode_val = "local"
                    else:
                        mode_val = "remote"
                    merged_cfg["mode"] = mode_val
                    merged_cfg["force_download"] = bool(
                        task_cfg.get("force_download", False)
                    )
                    _local_src = str(
                        task_cfg.get("local_source_path") or ""
                    ).strip()
                    if _local_src:
                        merged_cfg[
                            "local_source_path"
                        ] = _local_src

                if task_key in [
                    "LEGACY_ASTROM_GSHEET",
                    "LEGACY_REJECT_GSHEET",
                ]:
                    for _key in [
                        "DRY_RUN",
                        "google_secret_name",
                        "sheet_id",
                        "sheet_name",
                        "sheet_names",
                        "resolve_tolerance_arcsec",
                        "created_by",
                    ]:
                        if _key in task_cfg:
                            merged_cfg[_key] = task_cfg.get(_key)

                for field in [
                    "last_run",
                    "run_count",
                    "output_files",
                    "last_status",
                    "sync_source",
                    "sync_profiles",
                    "filters",
                ]:
                    if field in task_cfg:
                        merged_cfg[field] = task_cfg.get(field)

                import_error = str(import_errors.get(task_key, "")).strip()
                if import_error:
                    merged_cfg["last_status"] = "failed"

                merged.append(merged_cfg)

            if merged != stored_tasks:
                all_tasks[instrument] = merged
                changed = True

            ordered_tasks = sorted(
                merged, key=lambda task: task.get("order", 999)
            )
            for task_cfg in ordered_tasks:
                if not _task_is_due(task_cfg, now):
                    continue
                task_key = str(task_cfg.get("task_key", "") or "").strip()
                task_id = str(task_cfg.get("id", "") or "").strip()
                if str(import_errors.get(task_key, "")).strip():
                    continue
                task_cls = task_module.TASK_LIST.get(task_key)
                if not task_cls or not task_id:
                    continue
                try:
                    instance = hydrate_runtime_state(task_cls(), task_cfg)
                    instance.USE_SUBPROCESS = bool(
                        task_module.USE_SUBPROCESS.get(task_key, False)
                    )
                    instance._task_key = task_key
                except Exception:
                    task_cfg["last_status"] = "failed"
                    task_cfg["error"] = traceback.format_exc()
                    changed = True
                    continue
                run_params = build_run_params(
                    instrument, local_data_dir, all_profiles, task_cfg
                )
                # Route APERO check tasks to their dedicated queue so they
                # are never blocked by long-running general async tasks.
                check_queue = "apero_checks" if task_key == "APERO_CHECK_TASK" else "default"
                enqueue(instrument, task_id, instance, run_params,
                        queue=check_queue)

        if changed:
            save_async_tasks(all_tasks)
    except Exception:
        pass
    finally:
        if lock_handle is not None:
            lock_handle.close()


def _run_scheduler() -> None:
    """Daemon scheduler that enqueues due tasks based on frequency."""
    while not _shutdown_event.is_set():
        _ensure_worker()
        _scheduler_poll(_scheduler_local_data_dir)
        _shutdown_event.wait(_scheduler_poll_seconds)


def start_background_services(local_data_dir: Optional[str] = None) -> None:
    """Start the queue worker and periodic scheduler threads."""
    global _scheduler_thread, _scheduler_local_data_dir
    if local_data_dir:
        _scheduler_local_data_dir = str(local_data_dir)

    _shutdown_event.clear()
    _ensure_worker()
    if _scheduler_thread is None or not _scheduler_thread.is_alive():
        _scheduler_thread = threading.Thread(
            target=_run_scheduler, daemon=True, name="ari-task-scheduler"
        )
        _scheduler_thread.start()


def shutdown_background_services(
    join_timeout: float = 2.0, debug: bool = False
) -> None:
    """Request background worker/scheduler shutdown and join briefly."""
    import sys as _sys

    global _scheduler_thread

    _debug = debug

    if _debug:
        with _lock:
            queued = sum(len(q) for q in _queues.values())
            currents = _all_currents()
        cur_str = ", ".join(c[1] for c in currents) or "none"
        print(
            f"[task_runner] Shutdown requested. "
            f"Queued tasks: {queued}. "
            f"Running tasks: {cur_str}.",
            file=_sys.stderr,
            flush=True,
        )

    _shutdown_event.set()
    with _lock:
        n_stop = len(_stop_events)
        for stop_event in _stop_events.values():
            stop_event.set()
    if _debug and n_stop:
        print(
            f"[task_runner] Sent stop signal to {n_stop} task stop-event(s).",
            file=_sys.stderr,
            flush=True,
        )

    threads_to_join = [_scheduler_thread] + list(_worker_threads.values())
    for thread in threads_to_join:
        if thread is None or not thread.is_alive():
            continue
        if _debug:
            print(
                f'[task_runner] Joining thread "{thread.name}"'
                f' (timeout={join_timeout}s)...',
                file=_sys.stderr,
                flush=True,
            )
        thread.join(timeout=max(0.0, float(join_timeout)))
        if _debug:
            still_alive = thread.is_alive()
            state = (
                "still running (timed out)" if still_alive else "exited cleanly"
            )
            print(
                f'[task_runner]   "{thread.name}" {state}.',
                file=_sys.stderr,
                flush=True,
            )

    with _lock:
        if not _all_currents():
            _instances.clear()
            for q in _queues.values():
                q.clear()
            _errors.clear()
            _stop_events.clear()
            _task_log_paths.clear()
            _task_instruments.clear()
            if _debug:
                print(
                    "[task_runner] In-memory state cleared.",
                    file=_sys.stderr,
                    flush=True,
                )
        else:
            if _debug:
                print(
                    "[task_runner] Tasks are still running; "
                    "in-memory state preserved.",
                    file=_sys.stderr,
                    flush=True,
                )

    _worker_threads.clear()
    _scheduler_thread = None


# =============================================================================
# Public helpers
# =============================================================================
def build_run_params(
    instrument: str,
    local_data_dir: str,
    all_profiles: dict,
    task_cfg: Optional[dict] = None,
) -> dict:
    """Build the ``params`` dict expected by ``AperoAsyncTask.run_job``.

    Maps ``DATABASE_USERNAME`` → ``DATABASE_USER`` for each profile so that
    ``apero_async.database_query`` can find the correct key.
    """
    profiles = all_profiles.get(instrument, {})
    mapped: Dict[str, dict] = {}
    db_keys = [
        "DATABASE_MODE",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_USER",
        "DATABASE_USERNAME",
        "DATABASE_PASSWORD",
        "DATABASE_NAME",
        "DATABASE_USE_SSH_TUNNEL",
        "DATABASE_SSH_CONFIG_HOST",
        "DATABASE_SSH_LOCAL_PORT",
        "DATABASE_SSH_REMOTE_PORT",
        "ASTROM_TABLENAME",
        "CALIB_TABLENAME",
        "FINDEX_TABLENAME",
        "LOG_TABLENAME",
        "TELLU_TABLENAME",
        "REJECT_TABLENAME",
    ]
    path_keys = [
        "PATH_RAW",
        "PATH_PP",
        "PATH_RED",
        "PATH_CALIB",
        "PATH_OUT",
        "PATH_TELLU",
        "PATH_LOG",
        "PATH_LBL",
        "PATH_CHECK",
        "PATH_OTHER",
        "PATH_TRIGGER",
    ]
    for pname, pcfg in profiles.items():
        p = deepcopy(pcfg) if isinstance(pcfg, dict) else {}
        disabled = p.get('disabled', p.get('DISABLED', False))
        if isinstance(disabled, str):
            disabled = disabled.strip().lower() in [
                '1',
                'true',
                'yes',
                'on',
                'y',
            ]
        if bool(disabled):
            continue

        # Merge preset YAML referenced by APERO_INSTRUMENT_PROFILE so task
        # payloads include all instrument defaults without requiring code edits
        # for each new profile key.
        preset_name = str(p.get("APERO_INSTRUMENT_PROFILE", "") or "").strip()
        preset_data = _load_aprofile_preset(preset_name)
        if isinstance(preset_data, dict) and preset_data:
            _merge_missing(p, preset_data)
            # Keep a full copy for debugging/future task use.
            p["APERO_INSTRUMENT_PROFILE_DATA"] = deepcopy(preset_data)

        # Compatibility aliases between legacy/current key names.
        if "sci-headers" not in p and isinstance(p.get("headers"), dict):
            p["sci-headers"] = deepcopy(p.get("headers", {}))
        # Presets may use singular "plot" while tasks expect "plots".
        if "plots" not in p and isinstance(p.get("plot"), dict):
            p["plots"] = deepcopy(p.get("plot", {}))
        if "plot" not in p and isinstance(p.get("plots"), dict):
            p["plot"] = deepcopy(p.get("plots", {}))

        database = p.get("database", {})
        if not isinstance(database, dict):
            database = {}
        for key in db_keys:
            if key not in database and p.get(key):
                database[key] = p.get(key)
        if "DATABASE_USER" not in database and database.get(
            "DATABASE_USERNAME"
        ):
            database["DATABASE_USER"] = database.get("DATABASE_USERNAME")
        if "DATABASE_USERNAME" not in database and database.get(
            "DATABASE_USER"
        ):
            database["DATABASE_USERNAME"] = database.get("DATABASE_USER")
        p["database"] = database

        paths = p.get("paths", {})
        if not isinstance(paths, dict):
            paths = {}
        for key in path_keys:
            if key not in paths and p.get(key):
                paths[key] = p.get(key)
        p["paths"] = paths

        # Keep flat keys available in run-time payload for legacy code paths.
        for key in db_keys:
            if key not in p and database.get(key):
                p[key] = database.get(key)
        for key in path_keys:
            if key not in p and paths.get(key):
                p[key] = paths.get(key)

        if "DATABASE_USERNAME" in p and "DATABASE_USER" not in p:
            p["DATABASE_USER"] = p["DATABASE_USERNAME"]
        # Preserve legacy flat keys while also providing nested general.
        general = p.get("general", {})
        if not isinstance(general, dict):
            general = {}
        # Normalize preset lowercase keys to task uppercase keys.
        if "SCIENCE_FIBER" not in general and "science_fiber" in general:
            general["SCIENCE_FIBER"] = general.get("science_fiber")
        if "SCIENCE_TYPES" not in general and "science_types" in general:
            general["SCIENCE_TYPES"] = general.get("science_types")
        if "INSTRUMENT" not in general and "instrument" in general:
            general["INSTRUMENT"] = general.get("instrument")
        if "SCIENCE_FIBER" not in general and p.get("SCIENCE_FIBER"):
            general["SCIENCE_FIBER"] = p.get("SCIENCE_FIBER")
        if "SCIENCE_TYPES" not in general and p.get("SCIENCE_TYPES"):
            general["SCIENCE_TYPES"] = p.get("SCIENCE_TYPES")
        general["INSTRUMENT"] = instrument
        p["general"] = general
        # Ensure task code receives the instrument in each APERO profile
        # payload.
        p["INSTRUMENT"] = instrument
        mapped[pname] = p
    from pathlib import Path as _Path

    global _scheduler_local_data_dir
    safe_dir = local_data_dir or str(_Path.home() / ".ari")
    _scheduler_local_data_dir = safe_dir
    return {
        "LOCAL_DATA_DIR": safe_dir,
        "INSTRUMENT": instrument,
        "APERO_PROFILE_NAMES": list(mapped.keys()),
        "APERO_PROFILES": mapped,
        "TASK_CONFIG": dict(task_cfg or {}),
    }


def _resolve_queue_name(queue: str, task_key: str, instrument: str) -> str:
    """Return the queue name to use for a given task.

    Routing rules (first match wins):
    1. Explicit ``queue`` override (e.g. ``"apero_checks"``) is respected.
    2. ``APERO_CHECK_TASK`` → ``"apero_checks"``.
    3. Tasks whose type is ``"GLOBAL"`` → ``"global"``.
    4. Tasks whose type is ``"INSTRUMENT"`` → ``"instrument_{INSTRUMENT}"``.
    5. Anything else → ``"global"`` as a safe default.
    """
    if queue and queue not in ("default", "auto"):
        return queue
    if task_key == "APERO_CHECK_TASK":
        return "apero_checks"
    # Look up the task type from the registry.
    try:
        from apero_ri import tasks as _task_module
        ttype = str(_task_module.TYPE.get(task_key, "") or "").upper().strip()
    except Exception:
        ttype = ""
    if ttype == "INSTRUMENT":
        inst = str(instrument or "unknown").strip().upper()
        return "instrument_%s" % inst
    # GLOBAL tasks (and anything unrecognised) go on the global queue.
    return "global"


def enqueue(
    instrument: str,
    task_id: str,
    instance: Any,
    run_params: dict,
    prepend: bool = False,
    queue: str = "auto",
) -> None:
    """Add a task instance to the appropriate execution queue.

    Each queue has its own worker thread, so tasks on different queues run
    truly in parallel:

    * ``"apero_checks"``        — quick APERO check runs (per-profile)
    * ``"global"``              — long-running GLOBAL tasks (backups, syncs…)
    * ``"instrument_{NAME}"``   — per-instrument INSTRUMENT tasks (one thread
                                  per instrument so SPIROU never blocks NIRPS)

    Pass ``queue="auto"`` (the default) to have the queue chosen automatically
    from the task key and type, or pass an explicit name to override.

    If the task_id is already queued on any queue it is moved to the new
    position in the target queue.
    """
    task_key = str(getattr(instance, "_task_key", "") or "").strip()
    queue_name = _resolve_queue_name(queue, task_key, instrument)
    _ensure_queue_worker(queue_name)

    instance._run_params = run_params
    instance.status = "queued"
    with _lock:
        _instances[task_id] = instance
        _task_instruments[task_id] = instrument
        _stop_events[task_id] = threading.Event()
        _errors.pop(task_id, None)
        # Remove this task_id from whichever queue currently holds it.
        for q in _queues.values():
            updated = [(i, t) for i, t in q if t != task_id]
            q[:] = updated
        # Append / prepend to the target queue.
        target = _queues.setdefault(queue_name, [])
        entry = (instrument, task_id)
        if prepend:
            target.insert(0, entry)
        else:
            target.append(entry)


def stop_and_clear() -> None:
    """Clear all pending queues; does not interrupt any running task."""
    with _lock:
        for _i, tid in _all_queued():
            inst = _instances.get(tid)
            if inst is not None:
                inst.status = "cancelled"
        for q in _queues.values():
            q.clear()


def kill_all() -> Dict[str, Any]:
    """Immediately interrupt the running task and clear the queue.

    Sets the stop event on any running task so cooperative
    tasks exit early, marks every queued task cancelled, and
    clears the queue.  Cooldowns are set so the scheduler
    does not immediately re-enqueue anything.
    """
    killed_current = None

    with _lock:
        # 1. Interrupt all running tasks
        for cur in _all_currents():
            cur_inst, cur_tid = cur
            if killed_current is None:
                killed_current = cur_tid
            ev = _stop_events.get(cur_tid)
            if ev is not None:
                ev.set()
            inst = _instances.get(cur_tid)
            if inst is not None:
                inst.status = 'cancelling'

        # 2. Cancel every queued task
        cancelled = []
        for qi, qtid in _all_queued():
            inst = _instances.get(qtid)
            if inst is not None:
                inst.status = 'cancelled'
            cancelled.append(qtid)
        for q in _queues.values():
            q.clear()

    # 3. Apply cooldowns to prevent re-scheduling
    result = stop_all_with_cooldown()
    result['killed_current'] = killed_current
    result['cancelled_queued'] = len(cancelled)
    return result


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
        for q in _queues.values():
            if instrument:
                keep = []
                for queued_instrument, queued_task_id in q:
                    if queued_instrument == instrument:
                        inst = _instances.get(queued_task_id)
                        if inst is not None:
                            inst.status = "cancelled"
                            _append_history_entry(
                                queued_instrument,
                                queued_task_id,
                                getattr(inst, "name", queued_task_id),
                                "cancelled",
                                "Cancelled from queue stop action.",
                            )
                    else:
                        keep.append((queued_instrument, queued_task_id))
                q[:] = keep
            else:
                for _i, tid in q:
                    inst = _instances.get(tid)
                    if inst is not None:
                        inst.status = "cancelled"
                        _append_history_entry(
                            _i,
                            tid,
                            getattr(inst, "name", tid),
                            "cancelled",
                            "Cancelled from queue stop action.",
                        )
                q.clear()

    updated = 0
    for inst_key in instruments:
        task_list = all_tasks.get(inst_key, [])
        if not isinstance(task_list, list):
            continue
        for task_cfg in task_list:
            if not isinstance(task_cfg, dict):
                continue
            freq = _normalize_task_frequency(
                task_cfg.get("frequency", 24.0), 24.0
            )
            cooldown_until = now + timedelta(hours=freq)
            task_cfg["cooldown_until"] = cooldown_until.isoformat()
            task_cfg["last_run"] = now.isoformat()
            task_cfg["last_status"] = "cancelled"
            updated += 1

    save_async_tasks(all_tasks)
    return {
        "instrument": instrument or "ALL",
        "updated_tasks": updated,
        "cooldown_set_at": now.isoformat(),
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
    _inst = ""

    with _lock:
        inst = _instances.get(task_id)
        if inst is not None:
            task_name = str(getattr(inst, "name", task_id) or task_id)
        # Is it currently running in any worker?
        running_cur = next(
            (c for c in _all_currents() if c[1] == task_id), None
        )
        if running_cur is not None:
            was_running = True
            _inst = running_cur[0]
            stop_ev = _stop_events.get(task_id)
            if stop_ev is not None:
                stop_ev.set()
            if inst is not None:
                inst.status = "cancelling"
        else:
            # Remove from whichever queue holds this task_id.
            for target_queue in _queues.values():
                new_queue = [(i, t) for i, t in target_queue if t != task_id]
                if len(new_queue) < len(target_queue):
                    was_queued = True
                    for i, t in target_queue:
                        if t == task_id:
                            _inst = i
                            break
                    target_queue[:] = new_queue
                    if inst is not None:
                        inst.status = "cancelled"
                    break

    if not was_running and not was_queued:
        return {
            "success": False,
            "error": "Task not found in queue or currently running.",
        }

    # Log and history outside the lock
    log_path_str = _task_log_paths.get(task_id, "")
    if log_path_str:
        _append_task_log_line(
            Path(log_path_str),
            "Cancellation requested by user."
            + (
                " (task is running; waiting for cooperative exit)"
                if was_running
                else ""
            ),
        )

    if was_queued:
        _append_history_entry(
            _inst,
            task_id,
            task_name,
            "cancelled",
            "Cancelled by user from queue.",
        )

    return {
        "success": True,
        "task_id": task_id,
        "was_running": was_running,
        "was_queued": was_queued,
    }


def clear_instance(task_id: str) -> None:
    """Remove a task instance and its error record from memory."""
    with _lock:
        _instances.pop(task_id, None)
        _errors.pop(task_id, None)
        _task_log_paths.pop(task_id, None)
        _task_instruments.pop(task_id, None)
        _stop_events.pop(task_id, None)
        # Remove from whichever queue holds this task_id
        for q in _queues.values():
            q[:] = [(i, t) for i, t in q if t != task_id]


def get_task_log(task_id: str, lines: int = 400) -> Dict[str, Any]:
    """Return current log content and metadata for one task id."""
    path_str = _log_path_for_task(task_id)
    path = Path(path_str)

    exists = path.is_file()
    content = _tail_lines(path, max(1, int(lines))) if exists else ""
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
        "task_id": task_id,
        "path": str(path),
        "exists": exists,
        "content": content,
        "updated_at": mtime,
    }


def _queue_entry_info(q_instrument: str, q_task_id: str) -> dict:
    """Build a dict describing one queued entry."""
    q_inst = _instances.get(q_task_id)
    return {
        "instrument": q_instrument,
        "task_id": q_task_id,
        "task_name": (
            getattr(q_inst, "name", q_task_id) if q_inst else q_task_id
        ),
        "log_path": _log_path_for_task(q_task_id, q_instrument),
    }


def get_status() -> dict:
    """Return current queue and running-task information for all queues."""
    with _lock:
        # Build a per-queue status dict.
        named_queues: Dict[str, dict] = {}
        for qname, q in _queues.items():
            cur = _currents.get(qname)
            cur_info = None
            if cur is not None:
                ci, ct = cur
                ci_inst = _instances.get(ct)
                cur_info = _queue_entry_info(ci, ct)
            named_queues[qname] = {
                "current": cur,
                "current_info": cur_info,
                "queue": list(q),
                "queue_info": [_queue_entry_info(qi, qt) for qi, qt in q],
                "queue_length": len(q),
            }

        # Back-compat: expose global queue fields at the top level so
        # existing API consumers that read "current_info" / "queue_info" etc.
        # continue to work.
        global_q = named_queues.get("global", {
            "current": None,
            "current_info": None,
            "queue": [],
            "queue_info": [],
            "queue_length": 0,
        })
        apero_q = named_queues.get("apero_checks", {
            "current": None,
            "current_info": None,
            "queue": [],
            "queue_info": [],
            "queue_length": 0,
        })

        return {
            # Back-compat: global queue at top level
            "current": global_q["current"],
            "current_info": global_q["current_info"],
            "queue": global_q["queue"],
            "queue_info": global_q["queue_info"],
            "queue_length": global_q["queue_length"],
            # Back-compat: apero_checks queue at top level
            "apero_check_current": apero_q["current"],
            "apero_check_current_info": apero_q["current_info"],
            "apero_check_queue": apero_q["queue"],
            "apero_check_queue_info": apero_q["queue_info"],
            "apero_check_queue_length": apero_q["queue_length"],
            # Full named-queue status (new — includes instrument queues)
            "named_queues": named_queues,
            # Combined history
            "recent_history": get_recent_history(limit=50),
        }


def get_task_status(task_id: str) -> dict:
    """Return a status dict for a single task by id."""
    with _lock:
        instance = _instances.get(task_id)
        if instance is None:
            return {"found": False}
        is_current = any(c[1] == task_id for c in _all_currents())
        is_queued = any(t == task_id for _, t in _all_queued())
        error = _errors.get(task_id, "")

    return {
        "found": True,
        "status": instance.status,
        "progress": instance.progress,
        "subprogress": getattr(instance, "subprogress", 0.0),
        "use_subprocess": bool(getattr(instance, "USE_SUBPROCESS", False)),
        "info": instance.info,
        "last_run": getattr(instance, "last_run", "Never"),
        "output_files": getattr(instance, "output_files", []),
        "run_params": _sanitize_run_params(
            getattr(instance, "_run_params", {})
        ),
        "run_count": getattr(instance, "run_count", 0),
        "is_current": is_current,
        "is_queued": is_queued,
        "error": error,
        "log_path": _log_path_for_task(task_id),
    }


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
