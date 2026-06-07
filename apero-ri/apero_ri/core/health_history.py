#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Admin health history.

Records periodic snapshots of the admin-health summary so trends
(e.g. "email check has been failing for 3 days") can be surfaced.

Storage: append-only JSON-lines file at ~/.ari/admin/health/history.log
Each line is one JSON object: {ts, summary} where summary maps each
health-check key to its status ('ok' / 'warning' / 'error').

JSONL append matches the audit-log pattern: write-heavy, read-rarely,
must survive partial writes / crashes gracefully.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from apero_ri.core.log import get_logger

log = get_logger(__name__)

ARI_DIR = Path.home() / ".ari"
HEALTH_DIR = ARI_DIR / "admin" / "health"
HISTORY_FILE = HEALTH_DIR / "history.log"

_write_lock = threading.Lock()

# Cap how many lines we'll ever read back into memory at once.
MAX_READ_LINES = 5000


def set_ari_dir(path: Optional[str]) -> None:
    """Configure storage root (e.g. --data-dir)."""
    global ARI_DIR, HEALTH_DIR, HISTORY_FILE
    base = Path(path).expanduser() if path else (Path.home() / ".ari")
    ARI_DIR = base
    HEALTH_DIR = ARI_DIR / "admin" / "health"
    HISTORY_FILE = HEALTH_DIR / "history.log"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_snapshot(health: Dict[str, Any]) -> None:
    """Append one health snapshot, summarising each check to its status.

    :param health: the full health dict as produced by
                   build_admin_card_health_uncached (key -> {status, ...})
    """
    summary = {
        key: str(entry.get("status", "")) for key, entry in (health or {}).items()
        if isinstance(entry, dict)
    }
    if not summary:
        return
    entry = {"ts": _now_iso(), "summary": summary}
    line = json.dumps(entry, default=str, ensure_ascii=False)
    try:
        with _write_lock:
            HEALTH_DIR.mkdir(parents=True, exist_ok=True)
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except OSError as exc:
        log.warning("Failed to write health history snapshot: %s", exc)


def query(limit: int = 200, key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return the most recent snapshots (newest first), optionally filtered to one key.

    Reads at most MAX_READ_LINES from the tail of the file to bound memory use.
    When `key` is given, each returned entry is reduced to {ts, status} for
    that single check (entries lacking the key are skipped).
    """
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-MAX_READ_LINES:]
    except OSError as exc:
        log.warning("Failed to read health history: %s", exc)
        return []

    entries: List[Dict[str, Any]] = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        summary = entry.get("summary", {}) or {}
        if key:
            if key not in summary:
                continue
            entries.append({"ts": entry.get("ts", ""), "status": summary[key]})
        else:
            entries.append({"ts": entry.get("ts", ""), "summary": summary})
        if len(entries) >= limit:
            break
    return entries
