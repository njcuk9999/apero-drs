"""Science groups API helper functions for ARIApp."""

import re
from io import StringIO

import yaml
from apero_ri.core.auth import (
    get_users_for_instrument,
    load_science_groups,
    load_users,
    save_science_groups,
)
from apero_ri.core.permissions import load_parameters
from flask import Response, jsonify, request


def api_sci_groups_list(app):
    """List science group names for an instrument."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    instrument = request.args.get("instrument", "").strip()
    if not instrument:
        return jsonify(success=False, error="No instrument"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    params = load_parameters()
    valid = params.get("instruments", {}).get("value", [])
    if instrument not in valid:
        return jsonify(success=False, error="Invalid instrument"), 400

    run_ids = app._get_instrument_run_ids(instrument)
    run_id_pi_names = app._get_instrument_run_id_pi_names(instrument)
    groups = load_science_groups(instrument)
    groups, run_ids = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=run_ids,
        persist=True,
    )
    group_names = sorted(
        groups.keys(),
        key=lambda n: (
            0 if app._is_all_science_group(n) else 1,
            str(n).lower(),
        ),
    )
    available_users = get_users_for_instrument(instrument)

    assigned_users = set()
    assigned_run_ids = set()
    groups_without_users = []
    groups_without_run_ids = []
    for gname, group_entry in groups.items():
        if not isinstance(group_entry, dict):
            continue
        is_all_group = app._is_all_science_group(gname)

        group_users = []
        for username in group_entry.get("users", []):
            uname = str(username).strip()
            if uname:
                group_users.append(uname)
                assigned_users.add(uname)

        group_run_ids = []
        for run_id in group_entry.get("run_ids", []):
            rid = str(run_id).strip()
            if rid:
                group_run_ids.append(rid)
                if not is_all_group:
                    assigned_run_ids.add(rid)

        if not group_users and not is_all_group:
            groups_without_users.append(str(gname))
        if not group_run_ids and not is_all_group:
            groups_without_run_ids.append(str(gname))

    available_set = {str(u).strip() for u in available_users if str(u).strip()}
    available_run_id_set = {
        str(rid).strip() for rid in run_ids if str(rid).strip()
    }
    missing_users = sorted(available_set - assigned_users)
    missing_run_ids = sorted(available_run_id_set - assigned_run_ids)

    health_issues = []
    health_details = []
    if missing_users:
        health_issues.append(
            f"{len(missing_users)} user(s) not assigned to any science group"
        )
        health_details.extend([f"user: {u}" for u in missing_users])

    if groups_without_users:
        health_issues.append(
            f"{len(groups_without_users)} science group(s) without users"
        )
        health_details.extend(
            [
                f"group-without-users: {name}"
                for name in sorted(groups_without_users)
            ]
        )

    if groups_without_run_ids:
        health_issues.append(
            f"{len(groups_without_run_ids)} science group(s) without run IDs"
        )
        health_details.extend(
            [
                f"group-without-run-ids: {name}"
                for name in sorted(groups_without_run_ids)
            ]
        )

    if missing_run_ids:
        health_issues.append(
            f"{len(missing_run_ids)} run ID(s) not assigned "
            "to any science group"
        )
        health_details.extend([f"run_id: {rid}" for rid in missing_run_ids])

    if health_issues:
        health_status = "warning"
        health_message = "; ".join(health_issues) + "."
    else:
        health_status = "ok"
        health_message = (
            f"All {len(available_users)} users and {len(run_ids)} run ID(s) "
            f"are assigned to at least one science group."
        )

    run_id_labels = dict()
    for run_id in run_ids:
        label = str(run_id)
        pi_name = str(run_id_pi_names.get(run_id, "") or "").strip()
        if pi_name:
            low_pi = pi_name.lower()
            if low_pi not in {"none", "null", "unknown"}:
                label = f"{run_id} ({pi_name})"
        run_id_labels[run_id] = label

    return jsonify(
        success=True,
        groups=group_names,
        run_ids=run_ids,
        run_id_labels=run_id_labels,
        available_users=available_users,
        health_status=health_status,
        health_message=health_message,
        total_users=len(available_users),
        missing_users=len(missing_users),
        missing_user_list=missing_users,
        missing_run_ids=len(missing_run_ids),
        missing_run_id_list=missing_run_ids,
        groups_without_users=sorted(groups_without_users),
        groups_without_run_ids=sorted(groups_without_run_ids),
        health_details=health_details,
    )


def api_sci_groups_save(app):
    """Save run_ids and users for a science group."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    name = data.get("name", "").strip()
    run_ids = data.get("run_ids", [])
    users = data.get("users", [])

    if not instrument or not name:
        return jsonify(success=False, error="Missing fields"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    groups = load_science_groups(instrument)
    groups, all_run_ids = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=app._get_instrument_run_ids(instrument),
        persist=True,
    )
    canonical_name = "All" if app._is_all_science_group(name) else name

    run_ids_clean = sorted(
        {str(rid).strip() for rid in (run_ids or []) if str(rid).strip()}
    )
    users_clean = sorted(
        {str(user).strip() for user in (users or []) if str(user).strip()}
    )
    if app._is_all_science_group(canonical_name):
        run_ids_clean = all_run_ids

    groups[canonical_name] = {
        "run_ids": run_ids_clean,
        "users": users_clean,
    }
    save_science_groups(instrument, groups)
    groups, _ = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=all_run_ids,
        persist=True,
    )
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True, group=groups.get(canonical_name, {}))


def api_sci_groups_create(app):
    """Create a new science group."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    name = data.get("name", "").strip()
    if not instrument or not name:
        return jsonify(success=False, error="Missing fields"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    if not re.match(r"^[\w\-]+$", name):
        return (
            jsonify(
                success=False, error="Name must be alphanumeric (with _ or -)"
            ),
            400,
        )

    groups = load_science_groups(instrument)
    groups, _ = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=app._get_instrument_run_ids(instrument),
        persist=True,
    )
    canonical_name = "All" if app._is_all_science_group(name) else name
    if canonical_name in groups:
        return jsonify(success=False, error="Group already exists"), 409

    groups[canonical_name] = {"run_ids": [], "users": []}
    save_science_groups(instrument, groups)
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def api_sci_groups_delete(app):
    """Delete a science group."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    name = data.get("name", "").strip()
    if not instrument or not name:
        return jsonify(success=False, error="Missing fields"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    groups = load_science_groups(instrument)
    groups, _ = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=app._get_instrument_run_ids(instrument),
        persist=True,
    )
    canonical_name = "All" if app._is_all_science_group(name) else name
    if app._is_all_science_group(canonical_name):
        return (
            jsonify(success=False, error="The All group cannot be deleted"),
            400,
        )
    if canonical_name not in groups:
        return jsonify(success=False, error="Group not found"), 404

    del groups[canonical_name]
    save_science_groups(instrument, groups)
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def _normalize_group_payload(payload):
    """Normalize uploaded science-group YAML payload."""
    if not isinstance(payload, dict):
        raise ValueError("YAML root must be a mapping of group names")

    normalized = {}
    for raw_name, raw_entry in payload.items():
        name = str(raw_name or "").strip()
        if not name:
            continue
        if not isinstance(raw_entry, dict):
            raise ValueError(f"Group '{name}' entry must be a mapping")

        raw_run_ids = raw_entry.get("runids", raw_entry.get("run_ids", []))
        raw_users = raw_entry.get("users", [])

        if not isinstance(raw_run_ids, list):
            raise ValueError(f"Group '{name}' runids must be a list")
        if not isinstance(raw_users, list):
            raise ValueError(f"Group '{name}' users must be a list")

        normalized[name] = {
            "run_ids": sorted(
                {str(rid).strip() for rid in raw_run_ids if str(rid).strip()}
            ),
            "users": sorted(
                {str(user).strip() for user in raw_users if str(user).strip()}
            ),
        }

    return normalized


def api_sci_groups_export(app):
    """Export science groups for an instrument as YAML."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    instrument = request.args.get("instrument", "").strip()
    if not instrument:
        return jsonify(success=False, error="No instrument"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    params = load_parameters()
    valid = params.get("instruments", {}).get("value", [])
    if instrument not in valid:
        return jsonify(success=False, error="Invalid instrument"), 400

    groups = load_science_groups(instrument)
    groups, run_ids = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=app._get_instrument_run_ids(instrument),
        persist=True,
    )

    export_data = {}
    for name in sorted(groups.keys(), key=lambda x: str(x).lower()):
        entry = groups.get(name, {})
        export_data[str(name)] = {
            "runids": sorted(
                {
                    str(rid).strip()
                    for rid in entry.get("run_ids", [])
                    if str(rid).strip()
                }
            ),
            "users": sorted(
                {
                    str(user).strip()
                    for user in entry.get("users", [])
                    if str(user).strip()
                }
            ),
        }

    if "All" in export_data:
        export_data["All"]["runids"] = run_ids

    stream = StringIO()
    yaml.safe_dump(
        export_data,
        stream,
        sort_keys=False,
        default_flow_style=False,
    )
    content = stream.getvalue()
    filename = f"{instrument.lower()}_science_groups_export.yaml"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
    }
    return Response(content, mimetype="text/yaml", headers=headers)


def api_sci_groups_import(app):
    """Import science groups YAML with merge/replace behavior."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    instrument = str(request.form.get("instrument", "") or "").strip()
    mode = str(request.form.get("mode", "merge") or "merge").strip()
    mode = mode.lower()
    if mode not in {"merge", "replace"}:
        return jsonify(success=False, error="Mode must be merge or replace"), 400
    if not instrument:
        return jsonify(success=False, error="No instrument"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    params = load_parameters()
    valid = params.get("instruments", {}).get("value", [])
    if instrument not in valid:
        return jsonify(success=False, error="Invalid instrument"), 400

    up_file = request.files.get("file")
    if up_file is None:
        return jsonify(success=False, error="Missing YAML file"), 400

    try:
        raw_text = up_file.read().decode("utf-8")
    except Exception:
        return jsonify(success=False, error="Could not decode file"), 400

    try:
        raw_payload = yaml.safe_load(raw_text) if raw_text.strip() else {}
    except Exception as exc:
        return jsonify(success=False, error=f"Invalid YAML: {exc}"), 400

    try:
        imported = _normalize_group_payload(raw_payload)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400

    groups = load_science_groups(instrument)
    groups, all_run_ids = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=app._get_instrument_run_ids(instrument),
        persist=True,
    )

    changed = 0
    for raw_name, payload in imported.items():
        canonical_name = (
            "All" if app._is_all_science_group(raw_name) else raw_name
        )
        existing = groups.get(canonical_name, {"run_ids": [], "users": []})

        if mode == "merge":
            next_run_ids = sorted(
                set(existing.get("run_ids", [])) | set(payload["run_ids"])
            )
            next_users = sorted(
                set(existing.get("users", [])) | set(payload["users"])
            )
        else:
            next_run_ids = payload["run_ids"]
            next_users = payload["users"]

        if app._is_all_science_group(canonical_name):
            next_run_ids = all_run_ids

        groups[canonical_name] = {
            "run_ids": next_run_ids,
            "users": next_users,
        }
        changed += 1

    save_science_groups(instrument, groups)
    groups, _ = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=all_run_ids,
        persist=True,
    )
    app._refresh_admin_health_after_change(user_info, perms)

    return jsonify(
        success=True,
        mode=mode,
        imported_groups=sorted(imported.keys()),
        changed_groups=changed,
        total_groups=len(groups),
    )


def _check_sci_group_access(app, instrument, perms):
    """Return an error response tuple or None for valid access."""
    if not instrument:
        return jsonify(success=False, error='No instrument'), 400

    perm = f'manage.sci_group.{instrument}'
    if perm not in (perms or set()):
        return jsonify(success=False, error='Insufficient permissions'), 403

    params = load_parameters()
    valid = params.get('instruments', {}).get('value', [])
    if instrument not in valid:
        return jsonify(success=False, error='Invalid instrument'), 400
    return None


def _normalize_group_entry_payload(raw_entry):
    """Normalize one per-group payload entry."""
    if not isinstance(raw_entry, dict):
        raise ValueError('Group payload must be a mapping')

    raw_run_ids = raw_entry.get('runids', raw_entry.get('run_ids', []))
    raw_users = raw_entry.get('users', [])
    if not isinstance(raw_run_ids, list):
        raise ValueError('runids must be a list')
    if not isinstance(raw_users, list):
        raise ValueError('users must be a list')

    run_ids = sorted(
        {str(rid).strip() for rid in raw_run_ids if str(rid).strip()}
    )
    users = sorted(
        {str(user).strip() for user in raw_users if str(user).strip()}
    )
    return dict(run_ids=run_ids, users=users)


def _normalize_global_users_payload(raw_payload):
    """Normalize global users payload to user->set(groups)."""
    if not isinstance(raw_payload, dict):
        raise ValueError('YAML root must be a user mapping')

    normalized = dict()
    for raw_user, raw_entry in raw_payload.items():
        username = str(raw_user or '').strip()
        if not username:
            continue
        if not isinstance(raw_entry, dict):
            raise ValueError(f"User '{username}' entry must be a mapping")
        groups = raw_entry.get('groups', [])
        if not isinstance(groups, list):
            raise ValueError(f"User '{username}' groups must be a list")
        normalized[username] = {
            str(group).strip() for group in groups if str(group).strip()
        }
    return normalized


def _normalize_global_run_ids_payload(raw_payload):
    """Normalize global run-id payload to run_id->set(groups)."""
    if not isinstance(raw_payload, dict):
        raise ValueError('YAML root must be a run-id mapping')

    normalized = dict()
    for raw_run_id, raw_entry in raw_payload.items():
        run_id = str(raw_run_id or '').strip()
        if not run_id:
            continue
        if not isinstance(raw_entry, dict):
            raise ValueError(
                f"Run ID '{run_id}' entry must be a mapping"
            )
        groups = raw_entry.get('groups', [])
        if not isinstance(groups, list):
            raise ValueError(f"Run ID '{run_id}' groups must be a list")
        normalized[run_id] = {
            str(group).strip() for group in groups if str(group).strip()
        }
    return normalized


def _collect_assignment_state(app, instrument):
    """Collect groups and assignment maps for one instrument."""
    run_ids = app._get_instrument_run_ids(instrument)
    groups = load_science_groups(instrument)
    groups, run_ids = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=run_ids,
        persist=True,
    )

    run_to_groups = dict()
    user_to_groups = dict()
    assigned_run_ids = set()
    assigned_users = set()
    for gname, gentry in groups.items():
        if not isinstance(gentry, dict):
            continue
        if app._is_all_science_group(gname):
            continue
        cname = str(gname)
        for run_id in gentry.get('run_ids', []):
            rid = str(run_id).strip()
            if not rid:
                continue
            assigned_run_ids.add(rid)
            run_to_groups.setdefault(rid, set()).add(cname)
        for username in gentry.get('users', []):
            uname = str(username).strip()
            if not uname:
                continue
            assigned_users.add(uname)
            user_to_groups.setdefault(uname, set()).add(cname)

    return dict(
        groups=groups,
        run_ids=run_ids,
        run_to_groups=run_to_groups,
        user_to_groups=user_to_groups,
        assigned_run_ids=assigned_run_ids,
        assigned_users=assigned_users,
    )


def api_sci_groups_io_export(app):
    """Export YAML for global users/run IDs or selected group."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    instrument = request.args.get('instrument', '').strip()
    err = _check_sci_group_access(app, instrument, perms)
    if err is not None:
        return err

    scope = request.args.get('scope', 'group').strip().lower()
    kind = request.args.get('kind', 'group').strip().lower()
    selection = request.args.get('selection', 'all').strip().lower()
    raw_group = request.args.get('group', '').strip()

    state = _collect_assignment_state(app, instrument)
    groups = state['groups']
    run_ids = state['run_ids']
    run_to_groups = state['run_to_groups']
    user_to_groups = state['user_to_groups']

    export_data = dict()
    if scope == 'group':
        if not raw_group:
            return jsonify(success=False, error='Missing group'), 400
        canonical_group = (
            'All' if app._is_all_science_group(raw_group) else raw_group
        )
        if canonical_group not in groups:
            return jsonify(success=False, error='Group not found'), 404
        entry = groups.get(canonical_group, {})
        export_data[canonical_group] = {
            'runids': sorted(
                {
                    str(rid).strip()
                    for rid in entry.get('run_ids', [])
                    if str(rid).strip()
                }
            ),
            'users': sorted(
                {
                    str(user).strip()
                    for user in entry.get('users', [])
                    if str(user).strip()
                }
            ),
        }
        filename = (
            f'{instrument.lower()}_{canonical_group}_science_group.yaml'
        )
    elif scope == 'global':
        if kind not in {'users', 'run_ids'}:
            return jsonify(success=False, error='Invalid global kind'), 400
        if selection not in {'all', 'unassigned'}:
            return jsonify(success=False, error='Invalid selection'), 400

        if kind == 'run_ids':
            run_id_pi_names = app._get_instrument_run_id_pi_names(instrument)
            selected_ids = sorted(run_ids)
            if selection == 'unassigned':
                selected_ids = sorted(
                    set(run_ids) - set(state['assigned_run_ids'])
                )
            for run_id in selected_ids:
                pi_name = str(run_id_pi_names.get(run_id, '') or '').strip()
                if pi_name.lower() in {'none', 'null', 'unknown'}:
                    pi_name = ''
                export_data[run_id] = {
                    'pi_names': [pi_name] if pi_name else [],
                    'groups': sorted(run_to_groups.get(run_id, set())),
                }
            filename = (
                f'{instrument.lower()}_run_ids_{selection}_science_groups.yaml'
            )
        else:
            all_users = get_users_for_instrument(instrument)
            selected_users = sorted(all_users)
            if selection == 'unassigned':
                selected_users = sorted(
                    set(all_users) - set(state['assigned_users'])
                )

            user_rows = load_users()
            for username in selected_users:
                row = user_rows.get(username, {})
                first_name = str(row.get('first_names', '')).strip()
                last_name = str(row.get('last_name', '')).strip()
                export_data[username] = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'groups': sorted(user_to_groups.get(username, set())),
                }
            filename = (
                f'{instrument.lower()}_users_{selection}_science_groups.yaml'
            )
    else:
        return jsonify(success=False, error='Invalid scope'), 400

    stream = StringIO()
    yaml.safe_dump(
        export_data,
        stream,
        sort_keys=False,
        default_flow_style=False,
    )
    headers = {
        'Content-Disposition': f'attachment; filename={filename}',
    }
    return Response(
        stream.getvalue(),
        mimetype='text/yaml',
        headers=headers,
    )


def api_sci_groups_io_import(app):
    """Import YAML for global users/run IDs or selected group."""
    user_info, perms = app._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    instrument = str(request.form.get('instrument', '') or '').strip()
    err = _check_sci_group_access(app, instrument, perms)
    if err is not None:
        return err

    scope = str(request.form.get('scope', 'group') or '').strip().lower()
    kind = str(request.form.get('kind', 'group') or '').strip().lower()
    mode = str(request.form.get('mode', 'merge') or '').strip().lower()
    raw_group = str(request.form.get('group', '') or '').strip()
    if mode not in {'merge', 'replace'}:
        return jsonify(success=False, error='Mode must be merge or replace'), 400

    up_file = request.files.get('file')
    if up_file is None:
        return jsonify(success=False, error='Missing YAML file'), 400
    try:
        raw_text = up_file.read().decode('utf-8')
    except Exception:
        return jsonify(success=False, error='Could not decode file'), 400
    try:
        raw_payload = yaml.safe_load(raw_text) if raw_text.strip() else {}
    except Exception as exc:
        return jsonify(success=False, error=f'Invalid YAML: {exc}'), 400

    state = _collect_assignment_state(app, instrument)
    groups = state['groups']
    all_run_ids = state['run_ids']
    changed = 0

    if scope == 'group':
        if not raw_group:
            return jsonify(success=False, error='Missing group'), 400
        canonical_group = (
            'All' if app._is_all_science_group(raw_group) else raw_group
        )
        if canonical_group not in groups:
            return jsonify(success=False, error='Group not found'), 404

        payload = raw_payload
        if isinstance(raw_payload, dict) and canonical_group in raw_payload:
            payload = raw_payload[canonical_group]
        try:
            normalized = _normalize_group_entry_payload(payload or {})
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400

        existing = groups.get(canonical_group, {'run_ids': [], 'users': []})
        if mode == 'merge':
            next_run_ids = sorted(
                set(existing.get('run_ids', [])) | set(normalized['run_ids'])
            )
            next_users = sorted(
                set(existing.get('users', [])) | set(normalized['users'])
            )
        else:
            next_run_ids = list(normalized['run_ids'])
            next_users = list(normalized['users'])

        if app._is_all_science_group(canonical_group):
            next_run_ids = all_run_ids

        groups[canonical_group] = {
            'run_ids': next_run_ids,
            'users': next_users,
        }
        changed = 1

    elif scope == 'global':
        if kind not in {'users', 'run_ids'}:
            return jsonify(success=False, error='Invalid global kind'), 400

        non_all_groups = {
            str(name)
            for name in groups
            if not app._is_all_science_group(name)
        }

        if kind == 'users':
            try:
                incoming = _normalize_global_users_payload(raw_payload or {})
            except ValueError as exc:
                return jsonify(success=False, error=str(exc)), 400

            for username, target_groups in incoming.items():
                if mode == 'replace':
                    for gname in list(non_all_groups):
                        entry = groups.get(gname, {'run_ids': [], 'users': []})
                        users = {
                            str(user).strip()
                            for user in entry.get('users', [])
                            if str(user).strip()
                        }
                        if username in users:
                            users.remove(username)
                            entry['users'] = sorted(users)
                            groups[gname] = entry
                for target_group in sorted(target_groups):
                    cname = (
                        'All' if app._is_all_science_group(target_group)
                        else target_group
                    )
                    if app._is_all_science_group(cname):
                        continue
                    if cname not in groups:
                        groups[cname] = {'run_ids': [], 'users': []}
                        non_all_groups.add(cname)
                    entry = groups[cname]
                    users = {
                        str(user).strip()
                        for user in entry.get('users', [])
                        if str(user).strip()
                    }
                    users.add(username)
                    entry['users'] = sorted(users)
                    groups[cname] = entry
                changed += 1

        else:
            try:
                incoming = _normalize_global_run_ids_payload(raw_payload or {})
            except ValueError as exc:
                return jsonify(success=False, error=str(exc)), 400

            for run_id, target_groups in incoming.items():
                if mode == 'replace':
                    for gname in list(non_all_groups):
                        entry = groups.get(gname, {'run_ids': [], 'users': []})
                        run_set = {
                            str(rid).strip()
                            for rid in entry.get('run_ids', [])
                            if str(rid).strip()
                        }
                        if run_id in run_set:
                            run_set.remove(run_id)
                            entry['run_ids'] = sorted(run_set)
                            groups[gname] = entry
                for target_group in sorted(target_groups):
                    cname = (
                        'All' if app._is_all_science_group(target_group)
                        else target_group
                    )
                    if app._is_all_science_group(cname):
                        continue
                    if cname not in groups:
                        groups[cname] = {'run_ids': [], 'users': []}
                        non_all_groups.add(cname)
                    entry = groups[cname]
                    run_set = {
                        str(rid).strip()
                        for rid in entry.get('run_ids', [])
                        if str(rid).strip()
                    }
                    run_set.add(run_id)
                    entry['run_ids'] = sorted(run_set)
                    groups[cname] = entry
                changed += 1
    else:
        return jsonify(success=False, error='Invalid scope'), 400

    save_science_groups(instrument, groups)
    groups, _ = app._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=all_run_ids,
        persist=True,
    )
    app._refresh_admin_health_after_change(user_info, perms)

    return jsonify(
        success=True,
        scope=scope,
        kind=kind,
        mode=mode,
        changed=changed,
        total_groups=len(groups),
    )
