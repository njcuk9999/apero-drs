"""User pins API helper functions for ARIApp."""

from datetime import datetime, timezone
from typing import Any

from apero_ri.core import user_data as ud
from flask import jsonify, request


def api_user_pins_toggle(app: Any) -> Any:
    """Toggle a page pin and return the JSON API response.

    :param app: Application facade for authentication and user-pin storage.
    :return: JSON response, optionally paired with an HTTP error status.
    """
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    page_id = str(data.get("page_id", "")).strip()
    label = str(data.get("label", "")).strip()
    url = str(data.get("url", "")).strip()
    icon = str(data.get("icon", "")).strip() or "fa-solid fa-thumbtack"
    if not page_id or not label or not url or not url.startswith("/"):
        return (
            jsonify(
                success=False,
                error="page_id, label, and relative url are required.",
            ),
            400,
        )
    if page_id in ("home.login", "home.logout"):
        return jsonify(success=False, error="This page cannot be pinned."), 400

    username = user_info["username"]
    pins = app._load_user_pins(username)
    existing = {pin["page_id"]: pin for pin in pins}
    now_iso = datetime.now(timezone.utc).isoformat()

    if page_id in existing:
        pins = [pin for pin in pins if pin["page_id"] != page_id]
        pinned = False
    else:
        pins.append(
            {
                "page_id": page_id,
                "label": label,
                "url": url,
                "icon": icon,
                "pinned_at": now_iso,
            }
        )
        pinned = True

    app._save_user_pins(username, pins)
    return jsonify(success=True, pinned=pinned, pins=pins)


def api_user_pins_remove(app: Any) -> Any:
    """Remove a page pin and return the JSON API response.

    :param app: Application facade for authentication and user-pin storage.
    :return: JSON response, optionally paired with an HTTP error status.
    """
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    page_id = str(data.get("page_id", "")).strip()
    if not page_id:
        return jsonify(success=False, error="page_id is required."), 400

    username = user_info["username"]
    pins = app._load_user_pins(username)
    pins = [pin for pin in pins if pin["page_id"] != page_id]

    app._save_user_pins(username, pins)
    return jsonify(success=True, pins=pins)


def api_user_pins_reorder(app: Any) -> Any:
    """Persist a user-specified pin order and return the JSON response.

    :param app: Application facade for authentication and user-pin storage.
    :return: JSON response, optionally paired with an HTTP error status.
    """
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json() or {}
    ordered_ids = body.get("ids", [])
    if not isinstance(ordered_ids, list):
        return jsonify(success=False, error="ids must be a list"), 400
    ordered_ids = [
        str(item).strip() for item in ordered_ids if str(item).strip()
    ]

    username = user_info["username"]
    app._load_user_pins(username)
    pins = ud.reorder_pins(username, ordered_ids)
    pins = app._normalize_pinned_pages(pins)
    app._save_user_pins(username, pins)
    return jsonify(success=True, pins=pins)
