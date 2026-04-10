"""User DB access API helper functions for ARIApp."""

from datetime import datetime, timezone

from apero_ri.core.auth import (
    get_accessible_profiles,
    load_db_access,
    save_db_access,
)
from flask import jsonify, request


def api_user_db_access_save(app):
    """Persist group/column access for one profile into db_access.yaml."""
    user_info, perms = app._require_user_db_access_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = str(data.get("instrument", "")).strip()
    profile_id = str(data.get("profile_id", "")).strip()
    groups_map = data.get("groups", {})
    columns_map = data.get("columns", {})

    if not instrument or not profile_id:
        return jsonify(success=False, error="Missing profile selection"), 400
    if not isinstance(groups_map, dict) or not isinstance(columns_map, dict):
        return (
            jsonify(success=False, error="Invalid groups/columns payload"),
            400,
        )

    profile = app._find_accessible_profile(user_info, profile_id, instrument)
    if not profile:
        return (
            jsonify(success=False, error="Profile not found or access denied"),
            404,
        )

    editable_groups = set(app._editable_groups_for_editor(user_info, perms))

    cfg = (
        profile.get("data", {}) if isinstance(profile.get("data"), dict) else {}
    )
    valid_tables = {
        label
        for label, key in app._db_access_table_keys().items()
        if str(app._profile_get_db(cfg, key, "")).strip()
    }

    db_access = load_db_access()
    existing_entry = (
        (
            (
                db_access.get(instrument, {})
                if isinstance(db_access.get(instrument, {}), dict)
                else {}
            ).get(profile_id, {})
        )
        if instrument and profile_id
        else {}
    )
    existing_groups_map = (
        existing_entry.get("groups", {})
        if isinstance(existing_entry, dict)
        else {}
    )

    cleaned_groups = {}
    for table, raw_groups in groups_map.items():
        if table not in valid_tables:
            continue
        if not isinstance(raw_groups, list):
            return (
                jsonify(success=False, error=f"groups[{table}] must be a list"),
                400,
            )

        existing_for_table = existing_groups_map.get(table, [])
        if not isinstance(existing_for_table, list):
            existing_for_table = []
        existing_for_table = [
            str(g).strip() for g in existing_for_table if str(g).strip()
        ]

        preserved_noneditable = [
            g for g in existing_for_table if g not in editable_groups
        ]
        vals = list(preserved_noneditable)
        for g in raw_groups:
            gname = str(g).strip()
            if not gname:
                continue
            if gname not in app.ari_groups:
                continue
            if gname not in editable_groups and gname not in existing_for_table:
                return (
                    jsonify(
                        success=False,
                        error=f"No permission to assign group: {gname}",
                    ),
                    403,
                )
            if gname not in vals:
                vals.append(gname)
        cleaned_groups[table] = vals

    cleaned_cols = {}
    table_columns = {}
    for label, key in app._db_access_table_keys().items():
        if label not in valid_tables:
            continue
        table_name = str(app._profile_get_db(cfg, key, "")).strip()
        try:
            table_columns[label] = app._fetch_table_columns(cfg, table_name)
        except Exception as exc:
            return (
                jsonify(
                    success=False,
                    error=f"Unable to validate columns for {label}: {exc}",
                ),
                400,
            )

    for table, raw_cols in columns_map.items():
        if table not in valid_tables:
            continue
        if not isinstance(raw_cols, list):
            return (
                jsonify(
                    success=False, error=f"columns[{table}] must be a list"
                ),
                400,
            )
        allowed_cols = set(table_columns.get(table, []))
        cols = []
        for col in raw_cols:
            cname = str(col).strip()
            if cname and cname not in allowed_cols:
                return (
                    jsonify(
                        success=False,
                        error=f"Invalid column for {table}: {cname}",
                    ),
                    400,
                )
            if cname and cname not in cols:
                cols.append(cname)
        cleaned_cols[table] = cols

    for table in valid_tables:
        cleaned_groups.setdefault(table, [])
        cleaned_cols.setdefault(table, [])

    inst_access = db_access.get(instrument)
    if instrument not in db_access or not isinstance(inst_access, dict):
        db_access[instrument] = {}
    db_access[instrument][profile_id] = {
        "groups": cleaned_groups,
        "columns": cleaned_cols,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_db_access(db_access)

    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def build_user_db_access_health_report(app, user_info):
    """Build detailed health report for User DB Access rules."""
    if user_info is None:
        from apero_ri.core.auth import (
            _hydrate_profile_data,
            load_apero_profiles,
        )

        all_profiles_data = load_apero_profiles(hydrate=False)
        profiles = []
        for instrument, instr_profiles in (all_profiles_data or {}).items():
            if not isinstance(instr_profiles, dict):
                continue
            for profile_id, profile_data in instr_profiles.items():
                if not isinstance(profile_data, dict):
                    continue
                hydrated = _hydrate_profile_data(profile_data, instrument)
                profiles.append(
                    {
                        "instrument": instrument,
                        "profile_id": profile_id,
                        "data": hydrated,
                    }
                )
    else:
        profiles = get_accessible_profiles(user_info, app.ari_groups)
    db_access = load_db_access()
    table_key_map = app._db_access_table_keys()

    checked = 0
    warnings = 0
    profile_rows = []

    for prof in profiles:
        instrument = str(prof.get("instrument", "")).strip()
        profile_id = str(prof.get("profile_id", "")).strip()
        cfg = prof.get("data", {}) if isinstance(prof.get("data"), dict) else {}

        if not instrument or not profile_id:
            continue

        table_names = [
            label
            for label, key in table_key_map.items()
            if str(app._profile_get_db(cfg, key, "")).strip()
        ]
        if not table_names:
            profile_rows.append(
                {
                    "instrument": instrument,
                    "profile_id": profile_id,
                    "has_tables": False,
                    "status": "info",
                    "message": "No configured APERO DB"
                    "table names for this profile.",

                    "missing_groups": [],
                    "missing_columns": [],
                }
            )
            continue

        checked += 1
        prof_entry = (
            (
                (
                    db_access.get(instrument, {})
                    if isinstance(db_access.get(instrument, {}), dict)
                    else {}
                ).get(profile_id, {})
            )
            if instrument and profile_id
            else {}
        )
        groups_map = (
            prof_entry.get("groups", {}) if isinstance(prof_entry, dict) else {}
        )
        columns_map = (
            prof_entry.get("columns", {})
            if isinstance(prof_entry, dict)
            else {}
        )

        missing_groups = []
        missing_columns = []
        for table in table_names:
            glist = groups_map.get(table, [])
            if not isinstance(glist, list) or not glist:
                missing_groups.append(table)
            clist = columns_map.get(table, [])
            if not isinstance(clist, list) or not clist:
                missing_columns.append(table)

        is_warning = bool(missing_groups or missing_columns)
        if is_warning:
            warnings += 1
            parts = []
            if missing_groups:
                parts.append(f'missing groups: {", ".join(missing_groups)}')
            if missing_columns:
                parts.append(f'missing columns: {", ".join(missing_columns)}')
            message = "; ".join(parts)
            status = "warning"
        else:
            status = "ok"
            message = f"All {len(table_names)} table rule(s) are configured."

        profile_rows.append(
            {
                "instrument": instrument,
                "profile_id": profile_id,
                "has_tables": True,
                "status": status,
                "message": message,
                "missing_groups": missing_groups,
                "missing_columns": missing_columns,
            }
        )

    if checked == 0:
        status = "warning"
        message = (
            "No APERO profiles with configured table names "
            "were found for DB-access checks."
        )
    elif warnings:
        status = "warning"
        message = (
            f"{warnings} of {checked} profile(s) "
            "have incomplete DB table access rules."
        )
    else:
        status = "ok"
        message = (
            f"All {checked} profile(s) have complete DB table access rules."
        )

    profile_rows.sort(
        key=lambda row: (row.get("instrument", ""), row.get("profile_id", ""))
    )
    return {
        "status": status,
        "message": message,
        "checked_profiles": checked,
        "warning_profiles": warnings,
        "profiles": profile_rows,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def api_user_db_access_details(app):
    """Get group toggles and DB columns for one selected profile."""
    user_info, perms = app._require_user_db_access_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = request.args.get("profile_id", "").strip()
    instrument = request.args.get("instrument", "").strip()
    if not profile_id or not instrument:
        return jsonify(success=False, error="Missing profile selection"), 400

    profile = app._find_accessible_profile(user_info, profile_id, instrument)
    if not profile:
        return (
            jsonify(success=False, error="Profile not found or access denied"),
            404,
        )

    editable_groups = app._editable_groups_for_editor(user_info, perms)
    all_groups = list(app.ari_groups.keys())
    cfg = (
        profile.get("data", {}) if isinstance(profile.get("data"), dict) else {}
    )

    db_access = load_db_access()
    saved_entry = (
        (
            (
                db_access.get(instrument, {})
                if isinstance(db_access.get(instrument, {}), dict)
                else {}
            ).get(profile_id, {})
        )
        if instrument and profile_id
        else {}
    )
    saved_groups = (
        saved_entry.get("groups", {}) if isinstance(saved_entry, dict) else {}
    )
    saved_columns = (
        saved_entry.get("columns", {}) if isinstance(saved_entry, dict) else {}
    )

    sections = []
    for label, key in app._db_access_table_keys().items():
        table_name = str(app._profile_get_db(cfg, key, "")).strip()
        if not table_name:
            continue

        selected_groups = saved_groups.get(label, [])
        if not isinstance(selected_groups, list):
            selected_groups = []
        selected_groups = [
            str(g).strip() for g in selected_groups if str(g).strip()
        ]

        groups_ui = []
        for group_name in all_groups:
            groups_ui.append(
                {
                    "name": group_name,
                    "selected": group_name in selected_groups,
                    "editable": group_name in editable_groups,
                }
            )

        columns_error = ""
        columns_all = []
        try:
            columns_all = app._fetch_table_columns(cfg, table_name)
        except Exception as exc:
            columns_error = str(exc)

        selected_cols = saved_columns.get(label, [])
        if not isinstance(selected_cols, list):
            selected_cols = []
        selected_cols = [
            str(c).strip() for c in selected_cols if str(c).strip()
        ]

        if not selected_cols and columns_all:
            selected_cols = list(columns_all)

        columns_ui = []
        selected_set = set(selected_cols)
        for col in columns_all:
            columns_ui.append(
                {
                    "name": col,
                    "selected": col in selected_set,
                }
            )

        sections.append(
            {
                "table": label,
                "table_name": table_name,
                "groups": groups_ui,
                "columns": columns_ui,
                "columns_error": columns_error,
            }
        )

    return jsonify(
        success=True,
        instrument=instrument,
        profile_id=profile_id,
        sections=sections,
        editable_groups=editable_groups,
    )
