#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Admin audit log.

Records who changed what and when for sensitive admin mutations
(permissions, user groups, APERO profiles, backup config, etc).

Storage: append-only JSON-lines file at ~/.ari/admin/audit/audit.log
Each line is one JSON object: {ts, actor, action, target, detail}

This is intentionally simple (no DB) — audit trails are write-heavy,
read-rarely, and must survive partial writes / crashes gracefully.
JSONL append is atomic at the OS level for small writes and trivially
greppable/parseable.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from apero_ri.core.log import get_logger

log = get_logger(__name__)

ARI_DIR = Path.home() / ".ari"
AUDIT_DIR = ARI_DIR / "admin" / "audit"
AUDIT_FILE = AUDIT_DIR / "audit.log"

_write_lock = threading.Lock()

# Cap how many lines we'll ever read back into memory at once.
MAX_READ_LINES = 5000


def set_ari_dir(path: Optional[str]) -> None:
    """Configure storage root (e.g. --data-dir)."""
    global ARI_DIR, AUDIT_DIR, AUDIT_FILE
    base = Path(path).expanduser() if path else (Path.home() / ".ari")
    ARI_DIR = base
    AUDIT_DIR = ARI_DIR / "admin" / "audit"
    AUDIT_FILE = AUDIT_DIR / "audit.log"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record(
    actor: str,
    action: str,
    target: str = "",
    detail: Optional[Dict[str, Any]] = None,
) -> None:
    """Append one audit entry.

    :param actor: username (or 'system') performing the action
    :param action: short verb-based identifier, e.g. 'user.group.update',
                   'apero_profile.create', 'backup_config.update'
    :param target: the object acted upon, e.g. a username or profile id
    :param detail: optional JSON-serialisable dict with extra context
                   (e.g. {'before': [...], 'after': [...]})
    """
    entry = {
        "ts": _now_iso(),
        "actor": actor or "system",
        "action": action,
        "target": target,
        "detail": detail or {},
    }
    line = json.dumps(entry, default=str, ensure_ascii=False)
    try:
        with _write_lock:
            AUDIT_DIR.mkdir(parents=True, exist_ok=True)
            with open(AUDIT_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except OSError as exc:
        log.warning("Failed to write audit entry (%s %s %s): %s",
                    actor, action, target, exc)


def query(
    limit: int = 200,
    actor: Optional[str] = None,
    action_prefix: Optional[str] = None,
    target: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return the most recent audit entries (newest first), optionally filtered.

    Reads at most MAX_READ_LINES from the tail of the file to bound memory use.
    """
    if not AUDIT_FILE.exists():
        return []

    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-MAX_READ_LINES:]
    except OSError as exc:
        log.warning("Failed to read audit log: %s", exc)
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
        if actor and entry.get("actor") != actor:
            continue
        if action_prefix and not str(entry.get("action", "")).startswith(action_prefix):
            continue
        if target and entry.get("target") != target:
            continue
        entries.append(entry)
        if len(entries) >= limit:
            break
    return entries
