"""Query DB API helper functions for ARIApp."""

import time as _time
from pathlib import Path

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
    load_db_access,
)
from apero_ri.core.permissions import resolve_user_permissions
from flask import jsonify, request


def api_query_db_run(app):
    """Execute a structured, user-driven SELECT query safely."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    if not profile_id:
        return jsonify(success=False, error="Missing profile_id"), 400

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]
    cfg = (
        profile.get("data", {}) if isinstance(profile.get("data"), dict) else {}
    )

    run_ids = app._get_user_accessible_run_ids(user_info, instrument)

    table_access = app._get_user_table_access(user_info, profile)
    if not table_access:
        return (
            jsonify(
                success=False,
                error="No database tables are accessible with your current "
                "permissions for this profile.",
            ),
            403,
        )

    try:
        sql, params, col_labels = app._build_safe_select_query(
            table_access=table_access,
            query_spec=body,
            run_ids=run_ids,
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400

    nrids = len(run_ids)
    sql_preview = sql.replace(
        ":_run_ids",
        f'(/* {nrids} run ID{"s" if nrids != 1 else ""} */)',
    )
    params_preview = {k: v for k, v in params.items() if k != "_run_ids"}
    for key, val in params_preview.items():
        sql_preview = sql_preview.replace(f":{key}", repr(str(val)))

    try:
        rows = app._execute_db_query(cfg, sql, params)
    except Exception as exc:
        return (
            jsonify(
                success=False,
                error=f"Query failed: {exc}",
                sql_preview=sql_preview,
            ),
            500,
        )

    clean_rows = []
    for row in rows:
        clean_rows.append({k.split("__", 1)[-1]: v for k, v in row.items()})

    display_columns = [c.split("__", 1)[-1] for c in col_labels]
    table_for_col = {
        c.split("__", 1)[-1]: c.split("__", 1)[0] for c in col_labels
    }

    return jsonify(
        success=True,
        rows=clean_rows,
        columns=display_columns,
        table_for_col=table_for_col,
        total_rows=len(rows),
        sql_preview=sql_preview,
    )


def api_query_db_schema(app):
    """Return allowed tables and columns for a profile+user combination."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = request.args.get("profile_id", "").strip()
    if not profile_id:
        return jsonify(success=False, error="Missing profile_id"), 400

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    table_access = app._get_user_table_access(user_info, profile)

    tables_out = []
    for label, info in table_access.items():
        tables_out.append(
            {
                "label": label,
                "table_name": info["table_name"],
                "columns": info["columns"],
                "has_run_id_filter": label == "FINDEX",
            }
        )
    tables_out.sort(key=lambda t: t["label"])

    return jsonify(success=True, tables=tables_out)


def get_user_table_access(app, user_info, profile):
    """Return tables the user may query for this profile."""
    if user_info is None:
        return {}

    instrument = str(profile.get("instrument", "")).strip()
    profile_id = str(profile.get("profile_id", "")).strip()
    cfg = (
        profile.get("data", {}) if isinstance(profile.get("data"), dict) else {}
    )
    user_groups = set(user_info.get("groups", []) or [])

    db_access = load_db_access()
    entry = (
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
    if not isinstance(entry, dict):
        entry = {}

    table_key_map = app._db_access_table_keys()
    result = {}

    for label, key in table_key_map.items():
        table_name = str(app._profile_get_db(cfg, key, "")).strip()
        if not table_name:
            continue

        allowed_groups = entry.get("groups", {}).get(label, [])
        if not isinstance(allowed_groups, list):
            allowed_groups = []
        if not user_groups & set(allowed_groups):
            continue

        allowed_cols = entry.get("columns", {}).get(label, [])
        if not isinstance(allowed_cols, list):
            allowed_cols = []
        allowed_cols = [str(c).strip() for c in allowed_cols if str(c).strip()]

        if not allowed_cols:
            continue

        result[label] = {
            "table_name": table_name,
            "columns": allowed_cols,
        }

    return result


def api_file_browser(app):
    """Return filtered ftable_all rows for an object in one profile."""
    t_start = _time.time()

    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    preset = request.args.get("preset", "default").strip() or "default"

    if not profile_id or not objname:
        return (
            jsonify(success=False, error="Missing profile_id or objname"),
            400,
        )

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]
    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)

    from apero_ri.core import basket_funcs as bk

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    all_rows, _, generated_at = bk.load_ftable_rows(
        base_dir, instrument, profile_id, objname, "all"
    )
    total_m = len(all_rows)

    # Backfill missing KW_RUN_ID/KW_PI_NAME on LBL rows from non-LBL rows
    # in the same set; without this, instruments where LBL files lack
    # those header keys (e.g. NIRPS) would have all LBL rows stripped by
    # filter_accessible_rows below, so the file browser would return zero
    # LBL files even though the data exists on disk.
    all_rows = bk.backfill_lbl_run_ids(all_rows)

    accessible_rows = bk.filter_accessible_rows(
        all_rows,
        accessible_run_ids,
    )

    filtered = bk.apply_preset_filter(accessible_rows, preset)

    query_time = _time.time() - t_start
    return jsonify(
        success=True,
        rows=filtered,
        total=total_m,
        accessible=len(accessible_rows),
        preset=preset,
        generated_at=generated_at,
        query_time=round(query_time, 3),
    )
