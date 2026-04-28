#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ARI notifications + messages + users HTTP API helpers.

These helpers are bound onto :class:`ARIApp` via ``ariapp_impls.py``.
Each function takes ``app`` as the first argument so it can re-use
the existing permission helpers (``_require_user`` etc).
"""

from typing import Any, Dict, List

from flask import jsonify, request

from apero_ri.core import auth, notifications as notif


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
def api_notifications_list(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    only_unread = request.args.get("unread", "0") in ("1", "true")
    include_dismissed = request.args.get(
        "include_dismissed", "0") in ("1", "true")
    channel = (request.args.get("channel") or "").strip() or None
    try:
        limit = int(request.args.get("limit", "100"))
    except (TypeError, ValueError):
        limit = 100
    items = notif.list_notifications(
        username,
        only_unread=only_unread,
        include_dismissed=include_dismissed,
        channel=channel,
        limit=limit,
    )
    return jsonify(
        success=True,
        items=items,
        unread=notif.count_unread(username),
        unread_messages=notif.count_unread_messages(username),
    )


def api_notifications_unread_count(app):
    """Lightweight endpoint hit by the bell poller."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    return jsonify(
        success=True,
        unread=notif.count_unread(username),
        unread_messages=notif.count_unread_messages(username),
    )


def api_notifications_mark_read(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    data = request.get_json(silent=True) or {}
    ids = data.get("ids")
    if ids is None or (isinstance(ids, list) and len(ids) == 0):
        n = notif.mark_all_read(username)
    else:
        if not isinstance(ids, list):
            return jsonify(success=False, error="ids must be a list"), 400
        n = notif.mark_read(username, [str(x) for x in ids])
    return jsonify(success=True, updated=n)


def api_notifications_dismiss(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    data = request.get_json(silent=True) or {}
    ids = data.get("ids")
    channel = (data.get("channel") or "").strip() or None
    if ids is None or (isinstance(ids, list) and len(ids) == 0):
        n = notif.dismiss_all(username, channel=channel)
    else:
        if not isinstance(ids, list):
            return jsonify(success=False, error="ids must be a list"), 400
        n = notif.dismiss(username, [str(x) for x in ids])
    return jsonify(success=True, dismissed=n)


def api_notification_prefs_get(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    return jsonify(
        success=True,
        prefs=notif.get_prefs(username),
        channels=list(notif.DISABLEABLE),
    )


def api_notification_prefs_save(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    data = request.get_json(silent=True) or {}
    prefs = data.get("prefs") or {}
    if not isinstance(prefs, dict):
        return jsonify(success=False, error="prefs must be object"), 400
    for ch, p in prefs.items():
        if not isinstance(p, dict):
            continue
        notif.set_pref(
            username, str(ch),
            enabled=p.get("enabled"),
            browser_popups=p.get("browser_popups"),
        )
    return jsonify(success=True, prefs=notif.get_prefs(username))


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------
def _user_exists(username: str) -> bool:
    try:
        users = auth.load_users() or {}
    except Exception:  # noqa: BLE001
        users = {}
    return username in users


def api_messages_list(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    box = (request.args.get("box") or "inbox").lower()
    only_unread = request.args.get("unread", "0") in ("1", "true")
    items = notif.list_messages(
        username, box=box, only_unread=only_unread)
    return jsonify(success=True, items=items, box=box,
                   unread=notif.count_unread_messages(username))


def api_messages_send(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    data = request.get_json(silent=True) or {}
    recipient = str(data.get("recipient") or "").strip()
    body = str(data.get("body") or "").strip()
    subject = str(data.get("subject") or "").strip()
    if not recipient or not body:
        return jsonify(
            success=False, error="recipient and body required"), 400
    if not _user_exists(recipient):
        return jsonify(success=False, error="Unknown recipient"), 404
    mid = notif.send_message(
        username, recipient, body, subject=subject)
    if not mid:
        return jsonify(success=False, error="Send failed"), 500
    return jsonify(success=True, id=mid)


def api_messages_get(app, mid: str):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    msg = notif.get_message(username, mid)
    if not msg:
        return jsonify(success=False, error="Not found"), 404
    if msg.get("recipient") == username:
        notif.mark_message_read(username, mid)
    flag = notif.get_message_flag(mid)
    return jsonify(success=True, message=msg, flag=flag)


def api_messages_delete(app, mid: str):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    ok = notif.delete_message(username, mid)
    if not ok:
        return jsonify(success=False, error="Not found"), 404
    return jsonify(success=True)


def api_messages_flag_as_issue(app, mid: str):
    """Flag a message into the monitor-portal issues queue."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info.get("username", "")
    msg = notif.get_message(username, mid)
    if not msg:
        return jsonify(success=False, error="Not found"), 404
    # Hand off to the existing issues helper if present.
    issue_id = None
    try:
        from apero_ri.application import issues_api_helpers as _iah
        creator = getattr(_iah, "create_issue_internal", None)
        if callable(creator):
            issue_id = creator(
                kind="flag",
                title=("Flagged message from "
                       + str(msg.get("sender", ""))),
                body=str(msg.get("body", "")),
                created_by=username,
                meta={
                    "source": "message",
                    "message_id": mid,
                    "sender": msg.get("sender"),
                    "recipient": msg.get("recipient"),
                    "subject": msg.get("subject"),
                },
            )
    except Exception:  # noqa: BLE001
        issue_id = None
    notif.flag_message(username, mid, issue_id=issue_id)
    return jsonify(success=True, issue_id=issue_id)


# ---------------------------------------------------------------------------
# Users (lightweight directory used by the user_portal/users page)
# ---------------------------------------------------------------------------
def api_users_directory(app):
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    me = user_info.get("username", "")
    try:
        users = auth.load_users() or {}
    except Exception:  # noqa: BLE001
        users = {}
    out: List[Dict[str, Any]] = []
    for uname, urec in sorted(users.items()):
        if not isinstance(urec, dict):
            continue
        out.append({
            "username": uname,
            "first_names": urec.get("first_names", ""),
            "last_name": urec.get("last_name", ""),
            "email": urec.get("email", ""),
            "groups": urec.get("groups", []),
            "is_self": (uname == me),
        })
    return jsonify(success=True, users=out, me=me)
