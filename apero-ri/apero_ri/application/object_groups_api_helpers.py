#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: API handlers for shared object groups.

Permissions
-----------
- Any authenticated user with profile access can list groups and
  add objects to groups.
- Only users with ``monitor.{INSTRUMENT}`` (or higher) can delete
  or rename groups, or remove objects from groups.
- The Object Groups page filters out objects the user cannot see
  (via science-group run_id intersection).
"""
import io
from pathlib import Path

from apero_ri.application.user_favourites_api_helpers import (
    _load_object_table,
    _name_match_row,
    _resolve_objname,
)
from apero_ri.core import object_groups as og
from apero_ri.core.auth import (
    get_accessible_profiles,
    get_effective_user,
)
from apero_ri.core.permissions import (
    get_inherited_groups,
)
from flask import jsonify, request, session

# ================================================================
# Module name
# ================================================================
__NAME__ = 'apero_ri.application.object_groups_api_helpers'


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


def _resolve_query(app, profile, query):
    """Resolve *query* to (objname, nickname, error, candidates).

    Returns a 4-tuple:
    - objname:    canonical APERO name (or None on failure)
    - nickname:   the user-typed query when it differs from objname
    - error:      error string (or None on success)
    - candidates: list of partial-match names (or [])
    """
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari')
    )
    instrument = profile['instrument']
    profile_id = profile['profile_id']

    rows = _load_object_table(
        base_dir, instrument, profile_id
    )
    if rows is None:
        # No object table — accept query as literal
        return query, '', None, []

    resolved = _resolve_objname(rows, query)
    if resolved is not None:
        nickname = '' if resolved.upper() == query.strip().upper() else query.strip()
        return resolved, nickname, None, []

    # Direct exact OBJNAME match (belt-and-suspenders)
    exact = [
        r for r in rows
        if (str(r.get('OBJNAME', '')).strip().upper()
            == query.upper())
    ]
    if exact:
        return str(exact[0]['OBJNAME']).strip(), '', None, []

    partial = [
        str(r['OBJNAME']).strip()
        for r in rows
        if _name_match_row(r, query)
    ]
    if not partial:
        msg = (
            "Object '{}' not found in profile "
            "'{}'.".format(query, profile_id)
        )
        return None, '', msg, []

    if len(partial) > 1:
        msg = (
            "Query '{}' matches multiple objects."
            .format(query)
        )
        return None, '', msg, partial[:20]

    nickname = (
        '' if partial[0].upper() == query.strip().upper()
        else query.strip()
    )
    return partial[0], nickname, None, []


# ================================================================
# API endpoints — group CRUD
# ================================================================
def api_object_groups_list(app):
    """GET  list all groups for a profile."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    if not profile_id:
        return jsonify(
            success=False, error='profile_id required'
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    can_mod = _can_moderate(user_info, app, instrument)

    groups = og.list_groups(profile_id)
    items = []
    for g in groups:
        entry = dict(g)
        entry['object_count'] = len(g.get('objects', []))
        entry['can_edit'] = can_mod
        entry['can_delete'] = can_mod
        items.append(entry)

    return jsonify(
        success=True, groups=items, can_moderate=can_mod
    )


def api_object_groups_for_object(app):
    """GET  groups containing a specific object."""
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

    group_names = og.get_groups_for_object(
        profile_id, objname
    )
    all_groups = og.list_groups(profile_id)
    all_group_names = [
        g.get('name', '') for g in all_groups
    ]

    instrument = profile['instrument']
    can_mod = _can_moderate(user_info, app, instrument)

    return jsonify(
        success=True,
        member_groups=group_names,
        all_groups=all_group_names,
        can_moderate=can_mod,
    )


def api_object_groups_create(app):
    """POST  create a new group."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    name = str(body.get('name', '')).strip()
    if not profile_id or not name:
        return jsonify(
            success=False,
            error='profile_id and name required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    username = user_info.get('username', '')
    group = og.create_group(profile_id, name, username)
    if group is None:
        return jsonify(
            success=False,
            error='Group already exists',
        ), 409

    instrument = profile['instrument']
    can_mod = _can_moderate(user_info, app, instrument)
    group['object_count'] = 0
    group['can_edit'] = can_mod
    group['can_delete'] = can_mod
    return jsonify(success=True, group=group)


def api_object_groups_delete(app):
    """POST  delete a group (monitor only)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    name = str(body.get('name', '')).strip()
    if not profile_id or not name:
        return jsonify(
            success=False,
            error='profile_id and name required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    if not _can_moderate(user_info, app, instrument):
        return jsonify(
            success=False,
            error='Insufficient permissions',
        ), 403

    if not og.delete_group(profile_id, name):
        return jsonify(
            success=False, error='Group not found'
        ), 404

    return jsonify(success=True)


def api_object_groups_rename(app):
    """POST  rename a group (monitor only)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    old_name = str(body.get('old_name', '')).strip()
    new_name = str(body.get('new_name', '')).strip()
    if not profile_id or not old_name or not new_name:
        return jsonify(
            success=False,
            error='profile_id, old_name and '
                  'new_name required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    if not _can_moderate(user_info, app, instrument):
        return jsonify(
            success=False,
            error='Insufficient permissions',
        ), 403

    if not og.rename_group(profile_id, old_name, new_name):
        return jsonify(
            success=False,
            error='Rename failed (not found or name taken)',
        ), 400

    return jsonify(success=True)


# ================================================================
# API endpoints — object membership
# ================================================================
def api_object_groups_add_object(app):
    """POST  add an object to a group (resolves aliases)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    group_name = str(body.get('group', '')).strip()
    query = str(body.get('objname', '')).strip()
    if not profile_id or not group_name or not query:
        return jsonify(
            success=False,
            error='profile_id, group and objname required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    objname, nickname, error, candidates = _resolve_query(
        app, profile, query
    )
    if error:
        code = 404 if not candidates else 400
        return jsonify(
            success=False, error=error,
            candidates=candidates,
        ), code

    username = user_info.get('username', '')
    err = og.add_object_to_group(
        profile_id, group_name, objname, username
    )
    if err:
        return jsonify(success=False, error=err), 400

    return jsonify(
        success=True,
        resolved_objname=objname,
        nickname=nickname,
    )


def api_object_groups_add_objects_bulk(app):
    """POST  (multipart) bulk-add objects from text/csv.

    Each line is resolved through alias lookup. Lines that
    cannot be resolved are reported as ``not_found``.
    """
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = str(
        request.form.get('profile_id', '')
    ).strip()
    group_name = str(
        request.form.get('group', '')
    ).strip()
    if not profile_id or not group_name:
        return jsonify(
            success=False,
            error='profile_id and group required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    uploaded = request.files.get('file')
    if not uploaded:
        return jsonify(
            success=False, error='No file uploaded'
        ), 400

    raw = uploaded.read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')

    queries = []
    for line in io.StringIO(text):
        name = line.strip().split(',')[0].strip()
        if name:
            queries.append(name)

    username = user_info.get('username', '')
    added = 0
    skipped = 0
    not_found = []

    for query in queries:
        objname, nickname, error, _cand = _resolve_query(
            app, profile, query
        )
        if error or objname is None:
            not_found.append(query)
            continue
        err = og.add_object_to_group(
            profile_id, group_name, objname, username
        )
        if err:
            skipped += 1
        else:
            added += 1

    return jsonify(
        success=True,
        added=added,
        skipped=skipped,
        not_found=not_found,
    )


def api_object_groups_add_objects_json(app):
    """POST  bulk-add objects from a JSON list of names.

    Expected JSON body::

        {
            "profile_id": "<str>",
            "group": "<str>",
            "objnames": ["OBJ1", "OBJ2", ...]
        }

    Objects that cannot be resolved are reported in
    ``not_found``.  Objects already in the group are
    silently counted as ``skipped``.
    """
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(
            success=False, error='Unauthorized'
        ), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(
        body.get('profile_id', '')
    ).strip()
    group_name = str(
        body.get('group', '')
    ).strip()
    objnames = body.get('objnames', [])

    if not profile_id or not group_name:
        return jsonify(
            success=False,
            error='profile_id and group required',
        ), 400
    if not isinstance(objnames, list) or not objnames:
        return jsonify(
            success=False,
            error='objnames must be a non-empty list',
        ), 400
    # Cap at 5000 to prevent abuse
    if len(objnames) > 5000:
        return jsonify(
            success=False,
            error='Too many objects (max 5000)',
        ), 400

    profile = _resolve_profile(
        app, user_info, profile_id
    )
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    username = user_info.get('username', '')
    added = 0
    skipped = 0
    not_found = []

    for raw_name in objnames:
        name = str(raw_name).strip()
        if not name:
            continue
        # Resolve through alias lookup
        objname, _nick, error, _cand = (
            _resolve_query(app, profile, name)
        )
        if error or objname is None:
            not_found.append(name)
            continue
        err = og.add_object_to_group(
            profile_id, group_name,
            objname, username,
        )
        if err:
            skipped += 1
        else:
            added += 1

    return jsonify(
        success=True,
        added=added,
        skipped=skipped,
        not_found=not_found,
    )


def api_object_groups_remove_object(app):
    """POST  remove an object from a group (monitor only)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    group_name = str(body.get('group', '')).strip()
    objname = str(body.get('objname', '')).strip()
    if not profile_id or not group_name or not objname:
        return jsonify(
            success=False,
            error='profile_id, group and objname required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    if not _can_moderate(user_info, app, instrument):
        return jsonify(
            success=False,
            error='Insufficient permissions',
        ), 403

    if not og.remove_object_from_group(
        profile_id, group_name, objname
    ):
        return jsonify(
            success=False,
            error='Object not in group',
        ), 404

    return jsonify(success=True)


def api_object_groups_objects(app):
    """GET  list objects in a group, filtered by user access."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    group_name = request.args.get('group', '').strip()
    if not profile_id or not group_name:
        return jsonify(
            success=False,
            error='profile_id and group required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    accessible_rids = app._get_user_accessible_run_ids(
        user_info, instrument
    )

    groups = og.list_groups(profile_id)
    group = None
    for g in groups:
        if g.get('name') == group_name:
            group = g
            break
    if group is None:
        return jsonify(
            success=False, error='Group not found'
        ), 404

    # Filter objects by user's science-group run_ids
    obj_list = _filter_group_objects(
        app, profile_id, group, accessible_rids
    )

    can_mod = _can_moderate(user_info, app, instrument)
    return jsonify(
        success=True, objects=obj_list,
        can_moderate=can_mod,
    )


def _filter_group_objects(
    app, profile_id, group, accessible_rids
):
    """Return list of objects the user can see.

    If accessible_rids is empty the user can see nothing.
    Objects are matched against the object_table.json to
    determine their run_ids.
    """
    import json as _json
    from pathlib import Path

    base_dir = Path.home() / '.ari'
    # Need object_table to map objname -> run_ids
    objs_raw = group.get('objects', [])
    if not objs_raw:
        return []

    # Try to load the object table for run_id lookup
    run_id_map = _load_run_id_map(app, profile_id)

    result = []
    for obj_entry in objs_raw:
        if not isinstance(obj_entry, dict):
            continue
        objname = obj_entry.get('objname', '')
        if not objname:
            continue
        # Check if user can see this object
        obj_rids = run_id_map.get(objname, set())
        if obj_rids and not (obj_rids & accessible_rids):
            continue
        result.append(dict(
            objname=objname,
            added_by=obj_entry.get('added_by', ''),
            added_at=obj_entry.get('added_at', ''),
        ))
    return result


def _load_run_id_map(app, profile_id):
    """Build objname -> set(run_id) mapping from cache."""
    import json as _json
    from pathlib import Path

    if not hasattr(app, '_obj_group_rid_cache'):
        app._obj_group_rid_cache = {}

    if profile_id in app._obj_group_rid_cache:
        return app._obj_group_rid_cache[profile_id]

    base = Path.home() / '.ari'
    accessible = get_accessible_profiles(None, app.ari_groups)
    # find instrument for this profile
    instrument = None
    for prof in get_accessible_profiles(
        {'groups': ['super_admin']}, app.ari_groups
    ):
        if prof['profile_id'] == profile_id:
            instrument = prof['instrument']
            break

    if not instrument:
        app._obj_group_rid_cache[profile_id] = {}
        return {}

    tasks_dir = base / 'tasks' / instrument
    json_path = tasks_dir / profile_id / 'object_table.json'
    if not json_path.exists():
        legacy = tasks_dir / (
            'object_table_{}.json'.format(profile_id)
        )
        if legacy.exists():
            json_path = legacy

    if not json_path.exists():
        app._obj_group_rid_cache[profile_id] = {}
        return {}

    try:
        with open(json_path, encoding='utf-8') as f:
            data = _json.load(f)
    except Exception:
        app._obj_group_rid_cache[profile_id] = {}
        return {}

    rid_map = {}
    for row in data.get('rows', []):
        objname = str(row.get('OBJNAME', '')).strip()
        if not objname:
            continue
        raw = str(row.get('RUN_ID', '') or '')
        rids = {
            r.strip() for r in raw.split(',') if r.strip()
        }
        if objname in rid_map:
            rid_map[objname] |= rids
        else:
            rid_map[objname] = rids

    app._obj_group_rid_cache[profile_id] = rid_map
    return rid_map
