"""Query DB API helper functions for ARIApp."""

import csv
import io
import time as _time
from pathlib import Path

import astropy.io.fits as fits
from apero_ri.base.base import BLOCK_KIND as block_kind_map
from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
    load_db_access,
)
from apero_ri.core.permissions import resolve_user_permissions
from flask import jsonify, request, send_file


def _render_sql_preview(sql: str, params: dict) -> str:
    """Return SQL with all bound parameters substituted inline (for display only)."""
    out = sql
    # Substitute all params, longest keys first to avoid partial matches
    for key in sorted(params.keys(), key=len, reverse=True):
        val = params[key]
        if isinstance(val, (list, tuple)):
            rendered = "(" + ", ".join(repr(str(v)) for v in val) + ")"
        else:
            rendered = repr(str(val))
        out = out.replace(f":{key}", rendered)
    return out


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

    sql_preview = _render_sql_preview(sql, params)

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


def api_query_db_count(app):
    """Execute a COUNT(*) version of the query without ORDER BY or LIMIT."""
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
                error="No database tables are accessible with your current permissions.",
            ),
            403,
        )

    try:
        sql, params = app._build_safe_count_query(
            table_access=table_access,
            query_spec=body,
            run_ids=run_ids,
        )
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400

    sql_preview = _render_sql_preview(sql, params)

    try:
        rows = app._execute_db_query(cfg, sql, params)
    except Exception as exc:
        return (
            jsonify(
                success=False,
                error=f"Count query failed: {exc}",
                sql_preview=sql_preview,
            ),
            500,
        )

    count = 0
    if rows:
        first = rows[0]
        for v in first.values():
            try:
                count = int(v)
                break
            except (TypeError, ValueError):
                pass

    limit = int(body.get("limit", 500))
    if limit != 0:
        limit = min(max(1, limit), 2000)

    return jsonify(
        success=True,
        count=count,
        limit=limit,
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

    # The LBL_RDB product row is written only to the separate
    # ftable_lbl_rdb_{objname}.json file, never to ftable_all, so merge
    # it in here too -- otherwise the "rdb"/"lbl" presets can never show
    # the .rdb file in the file browser even though it exists on disk.
    lbl_rdb_rows, _, _ = bk.load_ftable_rows(
        base_dir, instrument, profile_id, objname, "lbl_rdb"
    )
    if lbl_rdb_rows:
        existing_filenames = {r.get("FILENAME") for r in all_rows}
        for r in lbl_rdb_rows:
            if r.get("FILENAME") not in existing_filenames:
                all_rows.append(r)

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


def _resolve_file_header_request(app):
    """Resolve and validate a file-header request for the file browser."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()

    if 'view.data_portal' not in perms:
        return None, None, (jsonify(success=False, error='Unauthorized'), 401)

    profile_id = request.args.get('profile_id', '').strip()
    block_kind = request.args.get('block_kind', '').strip().lower()
    obs_dir = request.args.get('obs_dir', '').strip()
    filename = request.args.get('filename', '').strip()
    kw_run_id = request.args.get('kw_run_id', '').strip()

    if not profile_id or not block_kind or not filename:
        return (
            None,
            None,
            (
                jsonify(success=False, error='Missing required params'),
                400,
            ),
        )

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof['profile_id'] == profile_id:
            profile = prof
            break
    if profile is None:
        return (
            None,
            None,
            (jsonify(success=False, error='Profile not found'), 404),
        )

    instrument = profile['instrument']
    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)
    if kw_run_id and kw_run_id not in accessible_run_ids:
        return (
            None,
            None,
            (
                jsonify(success=False, error='Access denied for this run_id'),
                403,
            ),
        )

    path_key = block_kind_map.get(block_kind)
    if not path_key:
        err = f'Unknown block_kind: {block_kind}'
        return None, None, (jsonify(success=False, error=err), 400)

    profile_data = profile.get('data') or {}
    base_path_raw = str(
        app._profile_get_path(profile_data, path_key, '') or ''
    ).strip()
    if not base_path_raw:
        err = f'No path configured for {path_key}'
        return None, None, (jsonify(success=False, error=err), 400)

    try:
        base_path = Path(base_path_raw).resolve()
        obs_part = Path(obs_dir.strip('/')) if obs_dir else Path('')
        file_path = (base_path / obs_part / filename).resolve()
        file_path.relative_to(base_path)
    except (ValueError, OSError) as exc:
        err = f'Path error: {exc}'
        return None, None, (jsonify(success=False, error=err), 400)

    if not file_path.is_file():
        err = f'File not found: {filename}'
        return None, None, (jsonify(success=False, error=err), 404)

    context = dict(
        profile_id=profile_id,
        block_kind=block_kind,
        obs_dir=obs_dir,
        filename=filename,
    )
    return file_path, context, None


def _extract_fits_header_rows(file_path):
    """Extract FITS header cards as serializable rows."""
    header = fits.getheader(str(file_path), ext=0)
    rows = []
    for idx, card in enumerate(header.cards):
        key = str(card.keyword or '')
        val = '' if card.value is None else str(card.value)
        com = '' if card.comment is None else str(card.comment)
        rows.append(
            dict(
                index=idx,
                key=key,
                value=val,
                comment=com,
            )
        )
    return header, rows


def api_file_header(app):
    """Return FITS header rows for a file-browser row."""
    file_path, context, error_response = _resolve_file_header_request(app)
    if error_response is not None:
        return error_response

    try:
        header, rows = _extract_fits_header_rows(file_path)
    except Exception as exc:  # noqa: BLE001
        err = f'Failed to read FITS header: {exc}'
        return jsonify(success=False, error=err), 500

    return jsonify(
        success=True,
        rows=rows,
        card_count=len(rows),
        extension=0,
        summary=dict(
            simple=bool(header.get('SIMPLE', False)),
            bitpix=str(header.get('BITPIX', '')),
            naxis=str(header.get('NAXIS', '')),
        ),
        **context,
    )


def api_file_header_download(app):
    """Download a file header in CSV or FITS format."""
    file_path, context, error_response = _resolve_file_header_request(app)
    if error_response is not None:
        return error_response

    out_fmt = request.args.get('format', 'csv').strip().lower() or 'csv'
    if out_fmt not in {'csv', 'fits'}:
        return jsonify(success=False, error='Invalid format'), 400

    try:
        header, rows = _extract_fits_header_rows(file_path)
    except Exception as exc:  # noqa: BLE001
        err = f'Failed to read FITS header: {exc}'
        return jsonify(success=False, error=err), 500

    stem = Path(context['filename']).name
    safe_stem = stem.replace('.fits', '').replace('.fit', '')
    safe_stem = safe_stem or 'header'

    if out_fmt == 'csv':
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(['index', 'key', 'value', 'comment'])
        for row in rows:
            writer.writerow([
                row['index'],
                row['key'],
                row['value'],
                row['comment'],
            ])
        data = io.BytesIO(stream.getvalue().encode('utf-8'))
        stream.close()
        dl_name = f'{safe_stem}_header.csv'
        return send_file(
            data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=dl_name,
            max_age=0,
        )

    hdu = fits.PrimaryHDU(header=header)
    fits_bytes = io.BytesIO()
    hdu.writeto(fits_bytes, overwrite=True)
    fits_bytes.seek(0)
    dl_name = f'{safe_stem}_header.fits'
    return send_file(
        fits_bytes,
        mimetype='application/fits',
        as_attachment=True,
        download_name=dl_name,
        max_age=0,
    )
