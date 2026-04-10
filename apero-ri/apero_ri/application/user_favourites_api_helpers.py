"""User favourite objects API helper functions for ARIApp."""

from apero_ri.core import user_data as ud
from flask import jsonify, request


def api_user_favourite_objects_reorder(app):
    """Save explicit user-defined order for favourite objects."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    ordered = body.get("objnames", [])
    if not profile_id:
        return jsonify(success=False, error="profile_id is required"), 400
    if not isinstance(ordered, list):
        return jsonify(success=False, error="objnames must be a list"), 400

    clean_ordered = []
    seen = set()
    for item in ordered:
        objname = str(item).strip()
        if not objname or objname in seen:
            continue
        seen.add(objname)
        clean_ordered.append(objname)

    username = user_info["username"]
    payload = ud.get_profile_favourite_objects(username, profile_id)
    favourites = payload.get("favourites", [])
    if not isinstance(favourites, list):
        favourites = []
    existing = [str(name).strip() for name in favourites if str(name).strip()]
    existing_set = set(existing)

    reordered = [name for name in clean_ordered if name in existing_set]
    for name in existing:
        if name not in reordered:
            reordered.append(name)

    updated = ud.save_profile_favourite_objects(
        username,
        profile_id,
        reordered,
        last_object=None,
    )
    return jsonify(success=True, favourite_objects=updated)
