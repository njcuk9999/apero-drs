"""Admin user management API helper functions for ARIApp."""

from apero_ri.core.auth import (
    get_effective_user,
    get_user_info,
    list_all_users,
    search_users,
    update_user_groups,
    update_user_instruments,
    user_has_admin_privileges,
    user_is_super_admin,
)
from apero_ri.core.permissions import (
    get_inherited_groups,
    get_user_instruments,
    load_parameters,
    resolve_user_permissions,
)
from flask import jsonify, request, session


def api_user_search(app):
    """Search users by username substring."""
    user_info, perms = app._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    perms = perms or set()

    query = request.args.get("q", "").strip()
    if query:
        results = search_users(query)
    else:
        results = list_all_users()

    all_groups = list(app.ari_groups.keys())
    editor_is_admin = user_has_admin_privileges(user_info.get("groups", []))
    editor_is_super_admin = user_is_super_admin(user_info.get("groups", []))
    can_add = {g for g in all_groups if f"manage.group.{g}" in perms}
    if editor_is_super_admin:
        can_add |= set(all_groups)
    elif editor_is_admin:
        can_add |= {g for g in all_groups if g not in ("admin", "super_admin")}

    inherited_map = {}
    for g in all_groups:
        inherited_map[g] = sorted(get_inherited_groups(g, app.ari_groups))

    params = load_parameters()
    all_instruments = params.get("instruments", {}).get("value", [])
    editor_instruments = get_user_instruments(
        user_info.get('groups', []), app.ari_groups
    )
    can_manage_instrument_groups = set()
    for g in all_groups:
        if f'manage.instrument.{g}' in perms:
            can_manage_instrument_groups.add(g)
        else:
            parts = g.rsplit('.', 1)
            if len(parts) == 2:
                instrument = parts[1]
                if f'manage.instrument.{instrument}' in perms:
                    can_manage_instrument_groups.add(g)
    can_add_instrument = (
        ("add.instrument" in perms)
        or bool(can_manage_instrument_groups)
        or editor_is_admin
    )

    # Build group categories: Global + per-instrument sections.
    # Groups with a dot suffix matching a known instrument are
    # filed under that instrument; everything else is "Global".
    instrument_set = set(all_instruments)
    group_categories = dict()
    group_categories['Global'] = []
    for inst in all_instruments:
        group_categories[inst] = []
    for g in all_groups:
        parts = g.rsplit('.', 1)
        has_inst = (
            len(parts) == 2 and parts[1] in instrument_set
        )
        if has_inst:
            group_categories[parts[1]].append(g)
        else:
            group_categories['Global'].append(g)

    return jsonify(
        success=True,
        users=results,
        all_groups=all_groups,
        can_add_groups=sorted(can_add),
        inherited_map=inherited_map,
        all_instruments=all_instruments,
        group_categories=group_categories,
        editor_instruments=editor_instruments,
        can_add_instrument=can_add_instrument,
        can_add_instrument_groups=sorted(
            can_manage_instrument_groups
        ),
        editor_username=user_info["username"],
        editor_is_admin=editor_is_admin,
        editor_is_super_admin=editor_is_super_admin,
    )


def api_user_update_groups(app):
    """Update a target user's groups."""
    user_info, perms = app._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    perms = perms or set()

    data = request.get_json()
    if not data or "username" not in data or "groups" not in data:
        return jsonify(success=False, error="Missing data"), 400

    target = data["username"]
    new_groups = data["groups"]

    target_info = get_user_info(target)
    if not target_info:
        return jsonify(success=False, error="User not found"), 404

    editor_is_admin = user_has_admin_privileges(user_info.get("groups", []))
    editor_is_super_admin = user_is_super_admin(user_info.get("groups", []))
    target_groups = set(target_info.get("groups", []))

    if ("super_admin" in target_groups) and not editor_is_super_admin:
        return (
            jsonify(
                success=False,
                error="Only super-admin can modify super-admin accounts",
            ),
            403,
        )
    if ("admin" in target_groups) and not editor_is_super_admin:
        return (
            jsonify(
                success=False,
                error="Only super-admin can modify admin accounts",
            ),
            403,
        )

    if (
        ("admin" in set(new_groups)) or ("super_admin" in set(new_groups))
    ) and not editor_is_super_admin:
        return (
            jsonify(
                success=False,
                error="Only super-admin can assign admin-level groups",
            ),
            403,
        )

    old_groups = target_groups
    changed = (set(new_groups) - old_groups) | (old_groups - set(new_groups))
    for g in changed:
        if f"manage.group.{g}" not in perms and not editor_is_admin:
            return (
                jsonify(
                    success=False, error=f"No permission to manage group: {g}"
                ),
                403,
            )

    if not update_user_groups(target, new_groups):
        return jsonify(success=False, error="Update failed"), 500
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def api_user_update_instruments(app):
    """Update a target user's instruments."""
    user_info, perms = app._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    perms = perms or set()

    data = request.get_json()
    if not data or "username" not in data or "instruments" not in data:
        return jsonify(success=False, error="Missing data"), 400

    target = data["username"]
    new_instruments = data["instruments"]

    target_info = get_user_info(target)
    if not target_info:
        return jsonify(success=False, error="User not found"), 404

    editor_is_admin = user_has_admin_privileges(user_info.get("groups", []))
    editor_is_super_admin = user_is_super_admin(user_info.get("groups", []))
    target_groups = set(target_info.get("groups", []))

    if ("super_admin" in target_groups) and not editor_is_super_admin:
        return (
            jsonify(
                success=False,
                error="Only super-admin can modify super-admin accounts",
            ),
            403,
        )
    if ("admin" in target_groups) and not editor_is_super_admin:
        return (
            jsonify(
                success=False,
                error="Only super-admin can modify admin accounts",
            ),
            403,
        )

    if target != user_info["username"] and not editor_is_admin:
        can_manage_any = "add.instrument" in perms
        missing = []
        for g in target_groups:
            has_perm = f'manage.instrument.{g}' in perms
            if not has_perm:
                parts = g.rsplit('.', 1)
                if len(parts) == 2:
                    has_perm = (
                        f'manage.instrument.{parts[1]}'
                        in perms
                    )
            if not has_perm:
                missing.append(g)
        if not can_manage_any and missing:
            return (
                jsonify(
                    success=False,
                    error=(
                        "No permission to manage instruments for user groups: "
                        + ", ".join(sorted(missing))
                    ),
                ),
                403,
            )

    if not isinstance(new_instruments, list):
        return jsonify(success=False, error="instruments must be a list"), 400

    params = load_parameters()
    valid = set(params.get("instruments", {}).get("value", []))
    for inst in new_instruments:
        if inst not in valid:
            return (
                jsonify(success=False, error=f"Invalid instrument: {inst}"),
                400,
            )

    if not update_user_instruments(target, new_instruments):
        return jsonify(success=False, error="Update failed"), 500
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def api_login_as_search(app):
    """Search users that the editor can impersonate."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    real_user = session.get("user")
    real_info = get_user_info(real_user)
    if not real_info:
        return jsonify(success=False, error="Unauthorized"), 401

    perms = resolve_user_permissions(real_info["groups"], app.ari_groups)

    query = request.args.get("q", "").strip()
    if query:
        results = search_users(query)
    else:
        results = list_all_users()

    filtered = []
    for user in results:
        if user["username"] == real_user:
            continue
        can_impersonate = any(
            f"login_as.{group}" in perms for group in user["groups"]
        )
        if can_impersonate:
            filtered.append(user)

    return jsonify(
        success=True,
        users=filtered,
        current_login_as=session.get("login_as"),
        real_user=real_user,
    )


def api_login_as_set(app):
    """Set the login-as user in the session."""
    real_user = session.get("user")
    if not real_user:
        return jsonify(success=False, error="Not logged in"), 401

    real_info = get_user_info(real_user)
    if not real_info:
        return jsonify(success=False, error="Unauthorized"), 401

    perms = resolve_user_permissions(real_info["groups"], app.ari_groups)

    data = request.get_json()
    if not data or "username" not in data:
        return jsonify(success=False, error="Missing data"), 400

    target = data["username"]
    if target == real_user:
        return jsonify(success=False, error="Cannot login as yourself"), 400

    target_info = get_user_info(target)
    if not target_info:
        return jsonify(success=False, error="User not found"), 404

    can_do = any(f"login_as.{g}" in perms for g in target_info["groups"])
    if not can_do:
        return (
            jsonify(success=False, error="No permission to login as this user"),
            403,
        )

    session["login_as"] = target
    return jsonify(success=True, username=target)
