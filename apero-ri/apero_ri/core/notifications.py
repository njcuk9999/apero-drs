#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ARI notification + messaging persistence.

SQLite-backed notification, message and per-user preference store.
The DB lives at ``~/.ari/admin/notifications/notifications.db``.

Schema (kept intentionally minimal):

* ``notifications`` — bell-icon entries shown in the header.
* ``messages``      — user-to-user messages (the inbox).
* ``message_flags`` — message-id -> issue-id link for "flag as
                      issue" workflow.
* ``notification_prefs`` — per-user, per-channel toggles.

This module exposes thread-safe helper functions; it never imports
Flask so it can be used from background tasks too.
"""

import os
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ARI_DIR = Path.home() / ".ari"
NOTIF_DIR = ARI_DIR / "admin" / "notifications"
NOTIF_DB = NOTIF_DIR / "notifications.db"

# Channels users can opt out of. Keep in sync with the prefs UI.
CHANNELS = (
    "message",          # new direct message
    "calendar",         # new/updated calendar event
    "issue",            # new monitor-portal issue (monitors only)
    "admin_health",     # admin health check (admins only)
    "fav_object",       # favourite object updated
    "system",           # ARI system notice (cannot be disabled)
)
DISABLEABLE = tuple(c for c in CHANNELS if c != "system")

_db_lock = threading.Lock()
_initialised = False


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------
def _connect() -> sqlite3.Connection:
    NOTIF_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(NOTIF_DB), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_schema() -> None:
    global _initialised
    if _initialised:
        return
    with _db_lock:
        if _initialised:
            return
        conn = _connect()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id          TEXT PRIMARY KEY,
                    username    TEXT NOT NULL,
                    channel     TEXT NOT NULL,
                    title       TEXT NOT NULL,
                    body        TEXT,
                    url         TEXT,
                    payload     TEXT,
                    created_at  REAL NOT NULL,
                    read_at     REAL,
                    dismissed   INTEGER DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_notif_user_active
                    ON notifications(username, dismissed, created_at DESC);

                CREATE TABLE IF NOT EXISTS messages (
                    id          TEXT PRIMARY KEY,
                    sender      TEXT NOT NULL,
                    recipient   TEXT NOT NULL,
                    subject     TEXT,
                    body        TEXT NOT NULL,
                    created_at  REAL NOT NULL,
                    read_at     REAL,
                    deleted_by_recipient INTEGER DEFAULT 0,
                    deleted_by_sender    INTEGER DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_msg_recipient
                    ON messages(recipient, deleted_by_recipient,
                                created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_msg_sender
                    ON messages(sender, deleted_by_sender,
                                created_at DESC);

                CREATE TABLE IF NOT EXISTS message_flags (
                    message_id  TEXT PRIMARY KEY,
                    flagger     TEXT NOT NULL,
                    issue_id    TEXT,
                    flagged_at  REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notification_prefs (
                    username    TEXT NOT NULL,
                    channel     TEXT NOT NULL,
                    enabled     INTEGER DEFAULT 1,
                    browser_popups INTEGER DEFAULT 0,
                    PRIMARY KEY (username, channel)
                );
            """)
            conn.commit()
        finally:
            conn.close()
        _initialised = True


def _now() -> float:
    return time.time()


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
def emit_notification(
    username: str,
    channel: str,
    title: str,
    body: str = "",
    url: str = "",
    payload: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Insert a notification for one user. Honours per-user prefs.

    Returns the new notification id, or None if the user has
    disabled this channel. ``system`` channel cannot be silenced.
    """
    _init_schema()
    username = (username or "").strip()
    channel = (channel or "system").strip().lower()
    if not username or not title:
        return None
    if channel != "system" and not is_channel_enabled(username, channel):
        return None
    nid = str(uuid.uuid4())
    import json as _json
    payload_str = _json.dumps(payload or {}, default=str)
    conn = _connect()
    try:
        with conn:
            conn.execute(
                "INSERT INTO notifications "
                "(id, username, channel, title, body, url, payload, "
                " created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (nid, username, channel, str(title)[:300],
                 str(body)[:4000], str(url)[:500], payload_str, _now()),
            )
    finally:
        conn.close()
    return nid


def emit_notification_bulk(
    usernames: Iterable[str],
    channel: str,
    title: str,
    body: str = "",
    url: str = "",
    payload: Optional[Dict[str, Any]] = None,
) -> int:
    """Emit the same notification to many users. Returns count sent."""
    sent = 0
    for u in usernames:
        if emit_notification(u, channel, title, body, url, payload):
            sent += 1
    return sent


def list_notifications(
    username: str,
    only_unread: bool = False,
    include_dismissed: bool = False,
    channel: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    _init_schema()
    sql = "SELECT * FROM notifications WHERE username = ?"
    args: List[Any] = [username]
    if not include_dismissed:
        sql += " AND dismissed = 0"
    if only_unread:
        sql += " AND read_at IS NULL"
    if channel:
        sql += " AND channel = ?"
        args.append(channel)
    sql += " ORDER BY created_at DESC LIMIT ?"
    args.append(int(max(1, min(limit, 500))))
    conn = _connect()
    try:
        rows = conn.execute(sql, args).fetchall()
    finally:
        conn.close()
    return [_row_to_dict(r) for r in rows]


def count_unread(username: str) -> int:
    _init_schema()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM notifications "
            "WHERE username = ? AND dismissed = 0 AND read_at IS NULL",
            (username,),
        ).fetchone()
    finally:
        conn.close()
    return int(row["c"]) if row else 0


def mark_read(username: str, ids: Iterable[str]) -> int:
    _init_schema()
    ids = [i for i in (ids or []) if i]
    if not ids:
        return 0
    conn = _connect()
    try:
        with conn:
            placeholders = ",".join("?" * len(ids))
            cur = conn.execute(
                "UPDATE notifications SET read_at = ? "
                "WHERE username = ? AND id IN (" + placeholders + ") "
                "AND read_at IS NULL",
                [_now(), username, *ids],
            )
            return cur.rowcount
    finally:
        conn.close()


def mark_all_read(username: str) -> int:
    _init_schema()
    conn = _connect()
    try:
        with conn:
            cur = conn.execute(
                "UPDATE notifications SET read_at = ? "
                "WHERE username = ? AND read_at IS NULL",
                (_now(), username),
            )
            return cur.rowcount
    finally:
        conn.close()


def dismiss(username: str, ids: Iterable[str]) -> int:
    _init_schema()
    ids = [i for i in (ids or []) if i]
    if not ids:
        return 0
    conn = _connect()
    try:
        with conn:
            placeholders = ",".join("?" * len(ids))
            cur = conn.execute(
                "UPDATE notifications SET dismissed = 1 "
                "WHERE username = ? AND id IN (" + placeholders + ")",
                [username, *ids],
            )
            return cur.rowcount
    finally:
        conn.close()


def dismiss_all(
    username: str, channel: Optional[str] = None
) -> int:
    _init_schema()
    conn = _connect()
    try:
        with conn:
            if channel:
                cur = conn.execute(
                    "UPDATE notifications SET dismissed = 1 "
                    "WHERE username = ? AND channel = ? "
                    "AND dismissed = 0",
                    (username, channel),
                )
            else:
                cur = conn.execute(
                    "UPDATE notifications SET dismissed = 1 "
                    "WHERE username = ? AND dismissed = 0",
                    (username,),
                )
            return cur.rowcount
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------
def get_prefs(username: str) -> Dict[str, Dict[str, bool]]:
    """Return prefs as {channel: {enabled, browser_popups}} for all
    DISABLEABLE channels (defaults applied for missing rows)."""
    _init_schema()
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT channel, enabled, browser_popups "
            "FROM notification_prefs WHERE username = ?",
            (username,),
        ).fetchall()
    finally:
        conn.close()
    have = {r["channel"]: r for r in rows}
    out: Dict[str, Dict[str, bool]] = {}
    for ch in DISABLEABLE:
        r = have.get(ch)
        out[ch] = {
            "enabled": bool(r["enabled"]) if r is not None else True,
            "browser_popups": bool(r["browser_popups"])
                if r is not None else False,
        }
    return out


def set_pref(
    username: str,
    channel: str,
    enabled: Optional[bool] = None,
    browser_popups: Optional[bool] = None,
) -> None:
    _init_schema()
    if channel not in DISABLEABLE:
        return
    conn = _connect()
    try:
        with conn:
            existing = conn.execute(
                "SELECT enabled, browser_popups "
                "FROM notification_prefs "
                "WHERE username = ? AND channel = ?",
                (username, channel),
            ).fetchone()
            cur_enabled = bool(existing["enabled"]) \
                if existing is not None else True
            cur_pop = bool(existing["browser_popups"]) \
                if existing is not None else False
            new_enabled = cur_enabled if enabled is None else bool(
                enabled)
            new_pop = cur_pop if browser_popups is None else bool(
                browser_popups)
            conn.execute(
                "INSERT INTO notification_prefs "
                "(username, channel, enabled, browser_popups) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT(username, channel) DO UPDATE SET "
                "  enabled = excluded.enabled, "
                "  browser_popups = excluded.browser_popups",
                (username, channel, int(new_enabled), int(new_pop)),
            )
    finally:
        conn.close()


def is_channel_enabled(username: str, channel: str) -> bool:
    if channel == "system":
        return True
    if channel not in DISABLEABLE:
        return True
    prefs = get_prefs(username)
    return bool(prefs.get(channel, {}).get("enabled", True))


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------
def send_message(
    sender: str,
    recipient: str,
    body: str,
    subject: str = "",
) -> Optional[str]:
    _init_schema()
    sender = (sender or "").strip()
    recipient = (recipient or "").strip()
    if not sender or not recipient or not body:
        return None
    mid = str(uuid.uuid4())
    conn = _connect()
    try:
        with conn:
            conn.execute(
                "INSERT INTO messages "
                "(id, sender, recipient, subject, body, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (mid, sender, recipient,
                 str(subject)[:200], str(body)[:8000], _now()),
            )
    finally:
        conn.close()
    # Fire a notification to the recipient (honours their prefs).
    short = (body[:120] + "…") if len(body) > 120 else body
    emit_notification(
        username=recipient,
        channel="message",
        title=("New message from " + sender),
        body=(subject + "\n" + short).strip(),
        url="/user_portal/messages",
        payload={"message_id": mid, "sender": sender},
    )
    return mid


def list_messages(
    username: str,
    box: str = "inbox",  # "inbox" | "sent"
    only_unread: bool = False,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    _init_schema()
    conn = _connect()
    try:
        if box == "sent":
            rows = conn.execute(
                "SELECT * FROM messages "
                "WHERE sender = ? AND deleted_by_sender = 0 "
                "ORDER BY created_at DESC LIMIT ?",
                (username, int(max(1, min(limit, 500)))),
            ).fetchall()
        else:
            sql = ("SELECT * FROM messages "
                   "WHERE recipient = ? AND deleted_by_recipient = 0")
            args: List[Any] = [username]
            if only_unread:
                sql += " AND read_at IS NULL"
            sql += " ORDER BY created_at DESC LIMIT ?"
            args.append(int(max(1, min(limit, 500))))
            rows = conn.execute(sql, args).fetchall()
    finally:
        conn.close()
    return [_row_to_dict(r) for r in rows]


def get_message(username: str, mid: str) -> Optional[Dict[str, Any]]:
    _init_schema()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM messages WHERE id = ? "
            "AND (sender = ? OR recipient = ?)",
            (mid, username, username),
        ).fetchone()
    finally:
        conn.close()
    return _row_to_dict(row) if row else None


def mark_message_read(username: str, mid: str) -> bool:
    _init_schema()
    conn = _connect()
    try:
        with conn:
            cur = conn.execute(
                "UPDATE messages SET read_at = ? "
                "WHERE id = ? AND recipient = ? AND read_at IS NULL",
                (_now(), mid, username),
            )
            changed = cur.rowcount > 0
            # Also clear (mark read + dismiss) any 'message'
            # channel notifications that point at this specific
            # message, so the bell badge / dropdown stops showing
            # it as soon as the user opens the message. Payload is
            # stored as a JSON string; match on the literal
            # ``"message_id": "<mid>"`` substring (mid is a UUID,
            # so the substring is unique to this message).
            try:
                like_pat = '%"message_id": "' + str(mid) + '"%'
                conn.execute(
                    "UPDATE notifications SET "
                    "  read_at = COALESCE(read_at, ?), "
                    "  dismissed = 1 "
                    "WHERE username = ? "
                    "  AND channel = 'message' "
                    "  AND payload LIKE ?",
                    (_now(), username, like_pat),
                )
            except Exception:
                # never let notification cleanup break the
                # message-read operation itself
                pass
            return changed
    finally:
        conn.close()


def mark_message_unread(username: str, mid: str) -> bool:
    _init_schema()
    conn = _connect()
    try:
        with conn:
            cur = conn.execute(
                "UPDATE messages SET read_at = NULL "
                "WHERE id = ? AND recipient = ? "
                "AND deleted_by_recipient = 0 "
                "AND read_at IS NOT NULL",
                (mid, username),
            )
            changed = cur.rowcount > 0
            if not changed:
                return False
            try:
                like_pat = '%"message_id": "' + str(mid) + '"%'
                conn.execute(
                    "UPDATE notifications SET "
                    "  read_at = NULL, "
                    "  dismissed = 0 "
                    "WHERE username = ? "
                    "  AND channel = 'message' "
                    "  AND payload LIKE ?",
                    (username, like_pat),
                )
            except Exception:
                pass
            return True
    finally:
        conn.close()


def delete_message(username: str, mid: str) -> bool:
    _init_schema()
    conn = _connect()
    try:
        with conn:
            cur = conn.execute(
                "UPDATE messages SET "
                "  deleted_by_recipient = "
                "    CASE WHEN recipient = ? THEN 1 "
                "         ELSE deleted_by_recipient END, "
                "  deleted_by_sender = "
                "    CASE WHEN sender = ? THEN 1 "
                "         ELSE deleted_by_sender END "
                "WHERE id = ? AND (recipient = ? OR sender = ?)",
                (username, username, mid, username, username),
            )
            return cur.rowcount > 0
    finally:
        conn.close()


def mark_all_messages_read(username: str) -> int:
    _init_schema()
    conn = _connect()
    try:
        with conn:
            cur = conn.execute(
                'UPDATE messages SET read_at = ? '
                'WHERE recipient = ? AND deleted_by_recipient = 0 '
                'AND read_at IS NULL',
                (_now(), username),
            )
            try:
                conn.execute(
                    'UPDATE notifications SET '
                    '  read_at = COALESCE(read_at, ?), '
                    '  dismissed = 1 '
                    'WHERE username = ? '
                    '  AND channel = ? '
                    '  AND dismissed = 0',
                    (_now(), username, 'message'),
                )
            except Exception:
                pass
            return int(cur.rowcount)
    finally:
        conn.close()


def delete_all_messages(
    username: str,
    box: str = 'inbox',
) -> int:
    _init_schema()
    target = str(box or 'inbox').strip().lower()
    if target not in ('inbox', 'sent', 'all'):
        return 0
    conn = _connect()
    deleted = 0
    try:
        with conn:
            if target in ('inbox', 'all'):
                cur_in = conn.execute(
                    'UPDATE messages SET deleted_by_recipient = 1 '
                    'WHERE recipient = ? AND deleted_by_recipient = 0',
                    (username,),
                )
                deleted += int(cur_in.rowcount)
                try:
                    conn.execute(
                        'UPDATE notifications SET dismissed = 1 '
                        'WHERE username = ? '
                        '  AND channel = ? '
                        '  AND dismissed = 0',
                        (username, 'message'),
                    )
                except Exception:
                    pass
            if target in ('sent', 'all'):
                cur_out = conn.execute(
                    'UPDATE messages SET deleted_by_sender = 1 '
                    'WHERE sender = ? AND deleted_by_sender = 0',
                    (username,),
                )
                deleted += int(cur_out.rowcount)
    finally:
        conn.close()
    return deleted


def count_unread_messages(username: str) -> int:
    _init_schema()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM messages "
            "WHERE recipient = ? AND deleted_by_recipient = 0 "
            "AND read_at IS NULL",
            (username,),
        ).fetchone()
    finally:
        conn.close()
    return int(row["c"]) if row else 0


def flag_message(
    username: str, mid: str, issue_id: Optional[str] = None
) -> bool:
    _init_schema()
    msg = get_message(username, mid)
    if not msg:
        return False
    conn = _connect()
    try:
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO message_flags "
                "(message_id, flagger, issue_id, flagged_at) "
                "VALUES (?, ?, ?, ?)",
                (mid, username, issue_id, _now()),
            )
    finally:
        conn.close()
    return True


def get_message_flag(mid: str) -> Optional[Dict[str, Any]]:
    _init_schema()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM message_flags WHERE message_id = ?",
            (mid,),
        ).fetchone()
    finally:
        conn.close()
    return _row_to_dict(row) if row else None
