#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: API handlers for per-object comments.

Permissions
-----------
- Any authenticated user with access to the profile can list and
  add comments.
- A comment can be edited or deleted by the author or by a user
  who has the ``monitor.{INSTRUMENT}`` group (resolved via
  inherited groups).
"""
from apero_ri.core import object_comments as oc
from apero_ri.core.auth import (
    get_accessible_profiles,
    get_effective_user,
)
from apero_ri.core.permissions import (
    get_inherited_groups,
    resolve_user_permissions,
)
from flask import jsonify, request, session

# ================================================================
# Module name
# ================================================================
__NAME__ = 'apero_ri.core.object_comments_api_helpers'


# ================================================================
# Helpers
# ================================================================
def _can_moderate(user_info, app, instrument):
    """Check if user has monitor.{instrument} privileges."""
    user_groups = set(user_info.get('groups', []))
    all_groups = set(user_groups)
    for g in list(user_groups):
        all_groups |= get_inherited_groups(g, app.ari_groups)
    target = 'monitor.{}'.format(instrument)
    return target in all_groups


def _resolve_profile(app, user_info, profile_id):
    """Find an accessible profile or return None."""
    accessible = get_accessible_profiles(
        user_info, app.ari_groups
    )
    for prof in accessible:
        if prof['profile_id'] == profile_id:
            return prof
    return None


# ================================================================
# API endpoints
# ================================================================
def api_object_comments_list(app):
    """GET  list comments for (profile, object)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    objname = request.args.get('objname', '').strip()
    if not profile_id or not objname:
        return jsonify(
            success=False,
            error='profile_id and objname required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    can_mod = _can_moderate(user_info, app, instrument)
    username = user_info.get('username', '')

    comments = oc.list_comments(profile_id, objname)
    items = []
    for c in comments:
        entry = dict(c)
        is_owner = c.get('username') == username
        entry['can_edit'] = is_owner or can_mod
        entry['can_delete'] = is_owner or can_mod
        items.append(entry)

    return jsonify(success=True, comments=items)


def api_object_comments_add(app):
    """POST  add a comment."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    objname = str(body.get('objname', '')).strip()
    comment = str(body.get('comment', '')).strip()
    if not profile_id or not objname or not comment:
        return jsonify(
            success=False,
            error='profile_id, objname and comment required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    username = user_info.get('username', '')
    entry = oc.add_comment(
        profile_id, objname, username, comment
    )
    entry['can_edit'] = True
    entry['can_delete'] = True
    return jsonify(success=True, comment=entry)


def api_object_comments_edit(app):
    """POST  edit a comment."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    objname = str(body.get('objname', '')).strip()
    comment_id = str(body.get('comment_id', '')).strip()
    comment = str(body.get('comment', '')).strip()
    if not all([profile_id, objname, comment_id, comment]):
        return jsonify(
            success=False,
            error='profile_id, objname, comment_id '
                  'and comment required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    existing = oc.get_comment_by_id(
        profile_id, objname, comment_id
    )
    if not existing:
        return jsonify(
            success=False, error='Comment not found'
        ), 404

    username = user_info.get('username', '')
    instrument = profile['instrument']
    is_owner = existing.get('username') == username
    can_mod = _can_moderate(user_info, app, instrument)
    if not is_owner and not can_mod:
        return jsonify(
            success=False,
            error='Not allowed to edit this comment',
        ), 403

    updated = oc.edit_comment(
        profile_id, objname, comment_id, comment
    )
    if not updated:
        return jsonify(
            success=False, error='Edit failed'
        ), 500

    updated['can_edit'] = True
    updated['can_delete'] = True
    return jsonify(success=True, comment=updated)


def api_object_comments_delete(app):
    """POST  delete a comment."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    objname = str(body.get('objname', '')).strip()
    comment_id = str(body.get('comment_id', '')).strip()
    if not all([profile_id, objname, comment_id]):
        return jsonify(
            success=False,
            error='profile_id, objname and comment_id required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    existing = oc.get_comment_by_id(
        profile_id, objname, comment_id
    )
    if not existing:
        return jsonify(
            success=False, error='Comment not found'
        ), 404

    username = user_info.get('username', '')
    instrument = profile['instrument']
    is_owner = existing.get('username') == username
    can_mod = _can_moderate(user_info, app, instrument)
    if not is_owner and not can_mod:
        return jsonify(
            success=False,
            error='Not allowed to delete this comment',
        ), 403

    if not oc.delete_comment(
        profile_id, objname, comment_id
    ):
        return jsonify(
            success=False, error='Delete failed'
        ), 500

    return jsonify(success=True)
