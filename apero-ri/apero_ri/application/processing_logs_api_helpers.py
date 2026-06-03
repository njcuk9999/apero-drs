#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Processing logs API helper functions.

Exposes three JSON endpoints used by the monitor portal:

  api_processing_logs(app)
      Returns processing-run rows for a profile.

  api_processing_logs_pid(app)
      Returns recipe-level rows for one PID within a profile.

  api_processing_log_file(app)
      Returns the raw text of one APERO log file.
"""
from __future__ import annotations

import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import quote

from flask import jsonify, request, session, send_file

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_effective_user,
    get_public_permissions,
)
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.tasks import apero_async
from apero_ri.application import profile_utils


__NAME__ = (
    "apero_ri.application.processing_logs_api_helpers"
)

# Regex: only allow safe identifiers for table names
_SAFE_ID_RE = re.compile(r'^[A-Za-z0-9_]+$')
_PROC_LOG_CACHE_TTL = timedelta(hours=1)
_PROC_LOG_CACHE: Dict[Tuple[str, str, str], Dict[str, Any]] = dict()
_PROC_LOG_CACHE_LOCK = threading.Lock()


def _is_truthy(value: Any) -> bool:
    """Return True for common truthy JSON/form values."""
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in {'1', 'true', 'yes', 'y', 'on'}


def _cache_stamp(dt_value: datetime) -> str:
    """Format cache update timestamp for UI display."""
    return dt_value.strftime('%Y-%m-%d %H:%M:%S')


def _cache_get(
    cache_key: Tuple[str, str, str]
) -> Tuple[Dict[str, Any] | None, str | None]:
    """Return a cached payload if it is still within TTL."""
    now = datetime.now()
    with _PROC_LOG_CACHE_LOCK:
        entry = _PROC_LOG_CACHE.get(cache_key)
        if entry is None:
            return None, None
        updated_at = entry.get('updated_at')
        payload = entry.get('payload')
        if not isinstance(updated_at, datetime):
            _PROC_LOG_CACHE.pop(cache_key, None)
            return None, None
        if now - updated_at > _PROC_LOG_CACHE_TTL:
            _PROC_LOG_CACHE.pop(cache_key, None)
            return None, None
        if not isinstance(payload, dict):
            _PROC_LOG_CACHE.pop(cache_key, None)
            return None, None
        return dict(payload), _cache_stamp(updated_at)


def _cache_set(cache_key: Tuple[str, str, str], payload: Dict[str, Any]) -> str:
    """Store payload and return the display timestamp."""
    updated_at = datetime.now()
    with _PROC_LOG_CACHE_LOCK:
        _PROC_LOG_CACHE[cache_key] = dict(
            updated_at=updated_at,
            payload=dict(payload),
        )
    return _cache_stamp(updated_at)


def _safe_table(name: str) -> str:
    """Return a backtick-quoted table name or raise."""
    if not _SAFE_ID_RE.match(name):
        raise ValueError(f"Unsafe table name: {name!r}")
    return f"`{name}`"


def _get_log_table(profile_data: dict) -> str:
    """Return the log table name for a profile."""
    val = profile_utils.profile_get_db(
        profile_data, "LOG_TABLENAME", ""
    )
    return str(val).strip() if val else ""


def _get_log_dir(profile_data: dict) -> str:
    """Return the log directory root for a profile."""
    for key in ("PATH_LOG", "DRS_DATA_MSG", "LOG_PATH"):
        val = profile_utils.profile_get_path(
            profile_data, key, ""
        )
        if val:
            return str(val).strip()
    return ""


def _find_profile(
    app: Any, user_info: Any, profile_id: str
) -> Dict[str, Any] | None:
    """Return accessible profile dict or None."""
    accessible = get_accessible_profiles(
        user_info, app.ari_groups
    )
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            return prof
    return None


def _unique_count(rows: list, key: str) -> int:
    """Count unique non-null values for a column key."""
    seen = set()
    for row in rows:
        v = row.get(key)
        if v is not None:
            seen.add(str(v))
    return len(seen)


def _rows_to_serializable(rows: list) -> List[dict]:
    """Convert any non-serialisable values to strings."""
    out = []
    for row in rows:
        clean = {}
        for k, v in row.items():
            if v is None:
                clean[k] = None
            elif hasattr(v, "isoformat"):
                clean[k] = v.isoformat()
            else:
                try:
                    import json as _j
                    _j.dumps(v)
                    clean[k] = v
                except (TypeError, ValueError):
                    clean[k] = str(v)
        out.append(clean)
    return out


def _safe_like_pid(pid: str) -> str:
    """Return a LIKE-safe fragment of a user-supplied PID."""
    return pid.replace("\\", "").replace("%", "").replace("_", r"\_")


def _pid_group_summary(
    db_params: Any, tbl: str, safe_pid: str
) -> Dict[str, Any]:
    """Compute group-level summary stats for one PID.

    :return: dict with start_time, end_time, total_seconds, total_time,
             n_passed, n_failed, processing_log (relative to /msg/).
    """
    from apero_ri.core import fail_report as fr

    summary: Dict[str, Any] = dict(
        start_time=None, end_time=None, total_seconds=None,
        total_time="n/a", n_passed=0, n_failed=0, processing_log=None,
    )
    agg_query = f"""
        SELECT
            MIN(START_TIME) AS start_time,
            MAX(END_TIME)   AS end_time,
            SUM(CASE WHEN ENDED = 1 THEN 1 ELSE 0 END) AS n_passed,
            SUM(CASE WHEN ENDED = 1 THEN 0 ELSE 1 END) AS n_failed,
            TIMESTAMPDIFF(SECOND, MIN(START_TIME), MAX(END_TIME))
                            AS total_seconds
        FROM {tbl}
        WHERE GROUPNAME LIKE '%{safe_pid}%'
    """
    try:
        agg_rows = apero_async.database_query(db_params, agg_query)
    except Exception:
        agg_rows = []
    if agg_rows:
        row = _rows_to_serializable(agg_rows)[0]
        summary["start_time"] = row.get("start_time")
        summary["end_time"] = row.get("end_time")
        summary["n_passed"] = int(row.get("n_passed") or 0)
        summary["n_failed"] = int(row.get("n_failed") or 0)
        total_seconds = row.get("total_seconds")
        if total_seconds is not None:
            try:
                summary["total_seconds"] = int(total_seconds)
                summary["total_time"] = fr.format_duration(
                    float(total_seconds))
            except (TypeError, ValueError):
                pass

    # The apero_processing recipe's own log file — try matching on PID column
    # first (exact), then fall back to GROUPNAME LIKE (fuzzy).  Use the full
    # LOGFILE path rather than stripping a '/msg/' prefix that may not exist.
    for _log_query in [
        f"""
            SELECT LOGFILE AS log_file
            FROM {tbl}
            WHERE PID = '{safe_pid}'
              AND RECIPE LIKE '%processing%'
            LIMIT 1
        """,
        f"""
            SELECT LOGFILE AS log_file
            FROM {tbl}
            WHERE GROUPNAME LIKE '%{safe_pid}%'
              AND RECIPE LIKE '%processing%'
            LIMIT 1
        """,
    ]:
        try:
            log_rows = apero_async.database_query(db_params, _log_query)
            if log_rows:
                val = str(log_rows[0].get("log_file", "") or "").strip()
                if val:
                    summary["processing_log"] = val
                    break
        except Exception:
            pass
    return summary


# =============================================================================
# API: processing log table for a profile
# =============================================================================
def api_processing_logs(app: Any):
    """Return JSON rows for the processing log table."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
    else:
        perms = get_public_permissions()

    from apero_ri.application.monitor_view_helpers import (
        _has_any_monitor_perm,
    )
    if not _has_any_monitor_perm(perms):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    profile_id = str(data.get("profile_id", "") or "").strip()
    force_refresh = _is_truthy(data.get('force_refresh', False))
    if not profile_id:
        return jsonify({"error": "profile_id required"}), 400

    cache_key = ('profile', profile_id, '')
    if not force_refresh:
        cached_payload, cached_stamp = _cache_get(cache_key)
        if cached_payload is not None and cached_stamp is not None:
            cached_payload['last_updated'] = cached_stamp
            cached_payload['from_cache'] = True
            return jsonify(cached_payload), 200

    prof = _find_profile(app, user_info, profile_id)
    if not prof:
        return (
            jsonify({"error": "Profile not found or access denied"}),
            404,
        )

    profile_data = prof["data"]
    log_table = _get_log_table(profile_data)
    if not log_table:
        payload = dict(
            rows=[],
            columns=[],
            dropdown_columns=[],
        )
        stamp = _cache_set(cache_key, payload)
        payload['last_updated'] = stamp
        payload['from_cache'] = False
        return jsonify(payload), 200

    try:
        tbl = _safe_table(log_table)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    db_params = apero_async.get_db_params(profile_data)
    query = f"""
        SELECT
            main.RECIPE        AS `Recipe name`,
            main.START_TIME    AS `Start time`,
            main.END_TIME      AS `End time`,
            CASE
                WHEN main.START_TIME IS NULL THEN NULL
                WHEN main.END_TIME IS NULL THEN NULL
                WHEN main.END_TIME < main.START_TIME THEN NULL
                ELSE TIMESTAMPDIFF(
                    SECOND,
                    main.START_TIME,
                    main.END_TIME
                )
            END                AS `Time taken`,
            totals.FAILED      AS `Failed`,
            totals.GROUP_COUNT AS `Total run`,
            main.PID           AS `PID`,
            SUBSTRING_INDEX(main.LOGFILE, '/msg/', -1)
                             AS `Log file`
        FROM {tbl} AS main
        INNER JOIN (
            SELECT
                REPLACE(
                  REPLACE(GROUPNAME, 'APEROG-', ''),
                  '_apero_processing_group', ''
                ) AS JOIN_PID,
                SUM(NOT ENDED) AS FAILED,
                COUNT(*)       AS GROUP_COUNT
            FROM {tbl}
            GROUP BY GROUPNAME
        ) AS totals
          ON totals.JOIN_PID = main.PID
        WHERE main.RECIPE LIKE '%processing%'
        ORDER BY main.START_TIME DESC
    """
    try:
        rows = apero_async.database_query(db_params, query)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    if not rows:
        payload = dict(
            rows=[],
            columns=[],
            dropdown_columns=[],
        )
        stamp = _cache_set(cache_key, payload)
        payload['last_updated'] = stamp
        payload['from_cache'] = False
        return jsonify(payload), 200

    rows = _rows_to_serializable(rows)
    columns = list(rows[0].keys()) if rows else []

    # Determine which columns should use dropdown filters
    # (fewer than 5 unique non-null values).
    dropdown_cols = []
    for col in columns:
        if col in ("PID", "Recipe name", "Log file"):
            continue
        if _unique_count(rows, col) < 5:
            dropdown_cols.append(col)

    payload = dict(
        rows=rows,
        columns=columns,
        dropdown_columns=dropdown_cols,
    )
    stamp = _cache_set(cache_key, payload)
    payload['last_updated'] = stamp
    payload['from_cache'] = False
    return jsonify(payload), 200


# =============================================================================
# API: PID detail rows
# =============================================================================
def api_processing_logs_pid(app: Any):
    """Return JSON rows for one PID's recipe detail."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
    else:
        perms = get_public_permissions()

    from apero_ri.application.monitor_view_helpers import (
        _has_any_monitor_perm,
    )
    if not _has_any_monitor_perm(perms):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    profile_id = str(data.get("profile_id", "") or "").strip()
    pid = str(data.get("pid", "") or "").strip()
    force_refresh = _is_truthy(data.get('force_refresh', False))
    if not profile_id or not pid:
        return (
            jsonify({"error": "profile_id and pid required"}),
            400,
        )

    cache_key = ('pid', profile_id, pid)
    if not force_refresh:
        cached_payload, cached_stamp = _cache_get(cache_key)
        if cached_payload is not None and cached_stamp is not None:
            cached_payload['last_updated'] = cached_stamp
            cached_payload['from_cache'] = True
            return jsonify(cached_payload), 200

    prof = _find_profile(app, user_info, profile_id)
    if not prof:
        return (
            jsonify({"error": "Profile not found or access denied"}),
            404,
        )

    profile_data = prof["data"]
    log_table = _get_log_table(profile_data)
    if not log_table:
        payload = dict(
            rows=[],
            columns=[],
            dropdown_columns=[],
            group_name=pid,
        )
        stamp = _cache_set(cache_key, payload)
        payload['last_updated'] = stamp
        payload['from_cache'] = False
        return jsonify(payload), 200

    try:
        tbl = _safe_table(log_table)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    db_params = apero_async.get_db_params(profile_data)
    # PID is user-supplied; use a parameterised-style escape by
    # injecting only the hex-safe portion into the LIKE pattern.
    safe_pid = _safe_like_pid(pid)
    query = f"""
        SELECT
            RECIPE   AS `Recipe name`,
            SHORTNAME AS `Short name`,
            RUNSTRING AS `Recipe call`,
            CASE
                WHEN START_TIME IS NULL THEN NULL
                WHEN END_TIME IS NULL THEN NULL
                WHEN END_TIME < START_TIME THEN NULL
                ELSE TIMESTAMPDIFF(
                    SECOND,
                    START_TIME,
                    END_TIME
                )
            END     AS `Time taken`,
            ENDED    AS `Finished`,
            SUBSTRING_INDEX(LOGFILE, '/msg/', -1) AS `Log file`
        FROM {tbl}
        WHERE GROUPNAME LIKE '%{safe_pid}%'
        ORDER BY RECIPE
    """
    try:
        rows = apero_async.database_query(db_params, query)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    if not rows:
        payload = dict(
            rows=[],
            columns=[],
            dropdown_columns=[],
            group_name=pid,
        )
        stamp = _cache_set(cache_key, payload)
        payload['last_updated'] = stamp
        payload['from_cache'] = False
        return jsonify(payload), 200

    rows = _rows_to_serializable(rows)
    columns = list(rows[0].keys()) if rows else []

    dropdown_cols = []
    for col in columns:
        if col in ("Recipe name", "Short name",
                   "Recipe call", "Log file"):
            continue
        if _unique_count(rows, col) < 5:
            dropdown_cols.append(col)

    # Get page title = GROUPNAME for this PID
    title_query = f"""
        SELECT GROUPNAME
        FROM {tbl}
        WHERE GROUPNAME LIKE '%{safe_pid}%'
        LIMIT 1
    """
    title = pid
    try:
        title_rows = apero_async.database_query(
            db_params, title_query
        )
        if title_rows:
            title = str(
                title_rows[0].get("GROUPNAME", pid) or pid
            )
    except Exception:
        pass

    summary = _pid_group_summary(db_params, tbl, safe_pid)

    payload = dict(
        rows=rows,
        columns=columns,
        dropdown_columns=dropdown_cols,
        group_name=title,
        summary=summary,
    )
    stamp = _cache_set(cache_key, payload)
    payload['last_updated'] = stamp
    payload['from_cache'] = False
    return jsonify(payload), 200


# =============================================================================
# API: log file content
# =============================================================================
def api_processing_log_file(app: Any):
    """Return the text content of one APERO log file."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
    else:
        perms = get_public_permissions()

    from apero_ri.application.monitor_view_helpers import (
        _has_any_monitor_perm,
    )
    if not _has_any_monitor_perm(perms):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    profile_id = str(data.get("profile_id", "") or "").strip()
    clean_logfile = str(
        data.get("clean_logfile", "") or ""
    ).strip()

    if not profile_id or not clean_logfile:
        return (
            jsonify(
                {"error": "profile_id and clean_logfile required"}
            ),
            400,
        )

    # Security: reject path traversal attempts
    if ".." in clean_logfile or clean_logfile.startswith("/"):
        return jsonify({"error": "Invalid log file path"}), 400

    prof = _find_profile(app, user_info, profile_id)
    if not prof:
        return (
            jsonify({"error": "Profile not found or access denied"}),
            404,
        )

    profile_data = prof["data"]
    log_dir = _get_log_dir(profile_data)
    if not log_dir:
        return (
            jsonify({"exists": False, "content": ""}),
            200,
        )

    # Build the full path safely.
    # clean_logfile is already relative to the msg/ directory
    # (the SQL strips everything up to and including /msg/).
    # PATH_LOG points to the msg/ dir itself, so we join directly.
    base = Path(log_dir).resolve()
    full = (base / clean_logfile).resolve()

    # Ensure the resolved path is still under the log root
    try:
        full.relative_to(base)
    except ValueError:
        return jsonify({"error": "Invalid log file path"}), 400

    if not full.is_file():
        return jsonify({
            "exists": False,
            "content": "",
            "log_path": str(full),
            "looked_at": str(full),
        }), 200

    try:
        content = full.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "exists": True,
        "content": content,
        "log_path": str(full),
    }), 200


# =============================================================================
# API: generate fail report (PDF) + token download
# =============================================================================
def _read_log_text(log_dir: str, clean_logfile: str) -> str:
    """Safely read one log file's text given the msg/ root + relative path.

    Returns an empty string when the path is missing/unsafe/unreadable.
    """
    clean_logfile = str(clean_logfile or "").strip()
    if not log_dir or not clean_logfile:
        return ""
    if ".." in clean_logfile or clean_logfile.startswith("/"):
        return ""
    base = Path(log_dir).resolve()
    full = (base / clean_logfile).resolve()
    try:
        full.relative_to(base)
    except ValueError:
        return ""
    if not full.is_file():
        return ""
    try:
        return full.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def api_processing_logs_fail_report(app: Any):
    """Generate a PDF fail report for one PID and return share/download URLs."""
    from apero_ri.core import fail_report as fr

    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
    else:
        perms = get_public_permissions()

    from apero_ri.application.monitor_view_helpers import (
        _has_any_monitor_perm,
    )
    if not _has_any_monitor_perm(perms):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    profile_id = str(data.get("profile_id", "") or "").strip()
    pid = str(data.get("pid", "") or "").strip()
    if not profile_id or not pid:
        return jsonify({"error": "profile_id and pid required"}), 400

    prof = _find_profile(app, user_info, profile_id)
    if not prof:
        return (
            jsonify({"error": "Profile not found or access denied"}),
            404,
        )

    profile_data = prof["data"]
    log_table = _get_log_table(profile_data)
    if not log_table:
        return jsonify({"error": "No log table for this profile"}), 400
    try:
        tbl = _safe_table(log_table)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    db_params = apero_async.get_db_params(profile_data)
    safe_pid = _safe_like_pid(pid)
    log_dir = _get_log_dir(profile_data)

    # Group-level summary (reused from the page).
    summary = _pid_group_summary(db_params, tbl, safe_pid)

    # Failed (not finished) recipes only.
    fail_query = f"""
        SELECT
            RECIPE    AS recipe_name,
            SHORTNAME AS short_name,
            RUNSTRING AS recipe_call,
            CASE
                WHEN START_TIME IS NULL THEN NULL
                WHEN END_TIME IS NULL THEN NULL
                WHEN END_TIME < START_TIME THEN NULL
                ELSE TIMESTAMPDIFF(SECOND, START_TIME, END_TIME)
            END       AS time_taken_seconds,
            SUBSTRING_INDEX(LOGFILE, '/msg/', -1) AS log_file
        FROM {tbl}
        WHERE GROUPNAME LIKE '%{safe_pid}%'
          AND (ENDED = 0 OR ENDED IS NULL)
        ORDER BY RECIPE
    """
    try:
        fail_rows = _rows_to_serializable(
            apero_async.database_query(db_params, fail_query)
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    # Build the page URL (with domain) for clickable links.
    page_url = request.url_root.rstrip("/") + (
        "/monitor_portal/proc_logs/%s/%s" % (
            quote(profile_id, safe=""), quote(pid, safe=""))
    )

    # Read each failed recipe's log, extract error blocks, assemble sections.
    failed_recipes: List[Dict[str, Any]] = []
    group_items: List[Dict[str, Any]] = []
    for row in fail_rows:
        clean_logfile = str(row.get("log_file", "") or "")
        log_name = clean_logfile.split("/")[-1] if clean_logfile else ""
        log_text = _read_log_text(log_dir, clean_logfile)
        error_blocks = fr.extract_error_blocks(log_text)
        # Flat list of lines for the PDF per-recipe section.
        error_lines = [ln for blk in error_blocks for ln in blk]
        secs = row.get("time_taken_seconds")
        log_url = (
            page_url + "?log=" + quote(clean_logfile, safe="")
            if clean_logfile else ""
        )
        failed_recipes.append(dict(
            log_name=log_name or "(unknown log)",
            recipe_name=str(row.get("recipe_name", "") or ""),
            short_name=str(row.get("short_name", "") or ""),
            recipe_call=str(row.get("recipe_call", "") or ""),
            time_taken=fr.format_duration(
                float(secs)) if secs is not None else "n/a",
            log_url=log_url,
            error_lines=error_lines,
            error_blocks=error_blocks,
        ))
        group_items.append(dict(
            label=log_name or str(row.get("recipe_name", "") or ""),
            error_blocks=error_blocks,
        ))

    error_groups = fr.group_error_blocks(group_items)

    # Enrich each error group with the recipe details (call, log url, time)
    # for every recipe that contributed to that group.
    recipe_by_label: Dict[str, Dict[str, Any]] = {
        r["log_name"]: r for r in failed_recipes
    }
    for grp in error_groups:
        grp["recipe_details"] = [
            dict(
                recipe_name=recipe_by_label[lbl]["recipe_name"],
                recipe_call=recipe_by_label[lbl]["recipe_call"],
                log_name=recipe_by_label[lbl]["log_name"],
                log_url=recipe_by_label[lbl]["log_url"],
                time_taken=recipe_by_label[lbl]["time_taken"],
            )
            for lbl in grp.get("recipes", [])
            if lbl in recipe_by_label
        ]

    report_data = dict(
        profile_id=profile_id,
        pid=pid,
        start_time=summary.get("start_time"),
        end_time=summary.get("end_time"),
        total_time=summary.get("total_time"),
        n_failed=summary.get("n_failed", len(failed_recipes)),
        n_passed=summary.get("n_passed", 0),
        processing_log=summary.get("processing_log"),
        page_url=page_url,
        error_groups=error_groups,
        failed_recipes=failed_recipes,
    )

    try:
        from apero_ri.core import fail_report_pdf as frpdf
    except ImportError as exc:
        return jsonify({
            "error": (
                "PDF generation requires the 'reportlab' package, which is "
                "not installed in the server environment (%s). Install it "
                "with: pip install reportlab" % exc
            )
        }), 500
    try:
        pdf_bytes = frpdf.build_fail_report_pdf(report_data)
    except Exception as exc:
        return jsonify({"error": "PDF generation failed: %s" % exc}), 500

    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", pid) or "report"
    filename = "fail_report_%s.pdf" % safe_name
    token = fr.store_report_pdf(pdf_bytes, dict(
        profile_id=profile_id, pid=pid, filename=filename,
    ))
    fr.update_report_cache(profile_id, pid, token, filename)

    # Use scheme-relative URLs (//host/path) so the browser inherits the
    # current page's scheme (HTTP or HTTPS) and avoids mixed-content blocks.
    base = request.url_root.rstrip("/")
    # Strip the scheme part ("http:" or "https:") leaving "//host[:port]".
    base_rel = re.sub(r"^https?:", "", base)
    share_url = base_rel + "/monitor_portal/proc_logs_report/" + token
    download_url = share_url + "?download=1"

    return jsonify({
        "success": True,
        "share_url": share_url,
        "download_url": download_url,
        "filename": filename,
        "expires_hours": fr.REPORT_EXPIRY_HOURS,
        "summary": dict(
            start_time=summary.get("start_time"),
            end_time=summary.get("end_time"),
            total_time=summary.get("total_time"),
            n_failed=summary.get("n_failed", len(failed_recipes)),
            n_passed=summary.get("n_passed", 0),
            processing_log=summary.get("processing_log"),
        ),
        "error_groups": error_groups,
        "failed_count": len(failed_recipes),
    }), 200


def api_processing_logs_report_download(app: Any, token: str):
    """Serve a generated fail-report PDF by its public share token.

    Public by design (unguessable UUID token, 24h expiry) so reports can be
    shared with collaborators without an ARI account.
    """
    from apero_ri.core import fail_report as fr

    resolved = fr.resolve_report_token(str(token or ""))
    if not resolved:
        return jsonify({"error": "Report not found or expired"}), 404

    as_attachment = _is_truthy(request.args.get("download", ""))
    return send_file(
        resolved["pdf_path"],
        mimetype="application/pdf",
        as_attachment=as_attachment,
        download_name=resolved["filename"],
    )


def api_processing_logs_fail_report_info(app: Any):
    """Return cached fail-report status for a profile+pid (no generation)."""
    from apero_ri.core import fail_report as fr

    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
    else:
        perms = get_public_permissions()

    from apero_ri.application.monitor_view_helpers import _has_any_monitor_perm
    if not _has_any_monitor_perm(perms):
        return jsonify({"error": "Forbidden"}), 403

    profile_id = str(request.args.get("profile_id", "") or "").strip()
    pid = str(request.args.get("pid", "") or "").strip()
    if not profile_id or not pid:
        return jsonify({"error": "profile_id and pid required"}), 400

    status = fr.get_report_cache_status(profile_id, pid)
    if not status:
        return jsonify({"cached": False}), 200

    base_rel = re.sub(r"^https?:", "", request.url_root.rstrip("/"))
    token = status.get("token", "")
    share_url = (base_rel + "/monitor_portal/proc_logs_report/" + token
                 ) if token else ""
    download_url = share_url + "?download=1" if share_url else ""

    return jsonify({
        "cached": True,
        "token_valid": bool(status.get("token_valid")),
        "generated_at": status.get("generated_at", ""),
        "age_hours": status.get("age_hours", -1),
        "filename": status.get("filename", "fail_report.pdf"),
        "share_url": share_url,
        "download_url": download_url,
    }), 200
