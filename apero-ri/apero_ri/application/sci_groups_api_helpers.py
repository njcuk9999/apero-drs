"""Science groups API helper functions for ARIApp."""

import re

from apero_ri.core.auth import (
    get_users_for_instrument,
    load_science_groups,
    save_science_groups,
)
from apero_ri.core.permissions import load_parameters
from flask import jsonify, request


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

    return jsonify(
        success=True,
        groups=group_names,
        run_ids=run_ids,
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
