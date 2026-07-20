"""APERO profile API helper functions for ARIApp."""

import os
import re
from pathlib import Path

from apero_ri.core import audit_log
from apero_ri.core.auth import load_apero_profiles, save_apero_profiles
from apero_ri.core.permissions import load_parameters
from apero_ri.tasks import apero_async
from flask import jsonify, request, url_for


def _to_bool(value):
    """Coerce request values to bool."""
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in ['1', 'true', 'yes', 'on', 'y']


def _profile_disabled(cfg: dict) -> bool:
    """Return True if a profile is disabled."""
    raw = cfg.get('disabled', cfg.get('DISABLED', False))
    return _to_bool(raw)


def _optional_path_is_enabled(cfg: dict, key: str) -> bool:
    """Return True when one optional path is configured and enabled."""
    value = str(profile_utils.profile_get_path(cfg, key, '') or '').strip()
    return bool(value)


def resolve_db_payload_for_test(app, data: dict) -> dict:
    """Resolve request DB payload into concrete test connection params."""
    mode = str(data.get("DATABASE_MODE", "") or "").strip()
    source = app._normalize_db_source(data.get("DATABASE_SOURCE", ""))
    local_name = str(data.get("DATABASE_LOCAL_NAME", "") or "").strip()
    username = str(data.get("DATABASE_USERNAME", "") or "").strip()
    password = data.get("DATABASE_PASSWORD", "")
    db_name = str(data.get("DATABASE_NAME", "") or "").strip()
    tunnel_name = str(data.get("DATABASE_TUNNEL_NAME", "") or "").strip()

    if not all([username, db_name]):
        return {
            "ok": False,
            "error": "DATABASE_USERNAME and DATABASE_NAME are required.",
        }

    if source == "local":
        if not local_name:
            return {
                "ok": False,
                "error": "DATABASE_LOCAL_NAME is required for local source.",
            }
        local_defs = app._load_local_db_definitions()
        local_def = local_defs.get(local_name, {})
        if not isinstance(local_def, dict) or not local_def:
            return {
                "ok": False,
                "error": f"Unknown local database definition: {local_name}",
            }
        mode = str(
            local_def.get("DATABASE_MODE", "") or "mysql+pymysql"
        ).strip()
        host = str(local_def.get("DATABASE_HOST", "") or "").strip()
        port = str(local_def.get("DATABASE_PORT", "") or "3306").strip()
        if not host:
            return {
                "ok": False,
                "error": "Selected local database definition"
                "has no DATABASE_HOST.",

            }
        return {
            "ok": True,
            "mode": mode,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "db_name": db_name,
            "use_ssh_tunnel": False,
            "ssh_config_host": "",
            "ssh_local_port": "",
            "ssh_remote_port": "",
            "database_source": "local",
            "database_local_name": local_name,
            "database_tunnel_name": "",
        }

    if not tunnel_name:
        return {
            "ok": False,
            "error": "DATABASE_TUNNEL_NAME is required when source"
            "is DB SSH tunnel.",

        }

    tunnels = app._load_db_tunnel_definitions()
    tunnel_def = tunnels.get(tunnel_name, {})
    if not isinstance(tunnel_def, dict) or not tunnel_def:
        return {
            "ok": False,
            "error": f"Unknown DB tunnel definition: {tunnel_name}",
        }

    runtime = app._build_db_tunnel_runtime_params(
        tunnel_name, tunnel_def, mode="mysql+pymysql"
    )
    try:
        status = apero_async.get_db_tunnel_status(runtime)
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "requires_tunnel_admin": True,
            "tunnel_admin_url": url_for("home_admin_portal_database_setup"),
        }

    if not status.get("active"):
        return {
            "ok": False,
            "error": (
                f'No active DB SSH tunnel for "{tunnel_name}". '
                "Open Database Setup and start/authenticate it first."
            ),
            "requires_tunnel_admin": True,
            "tunnel_admin_url": url_for("home_admin_portal_database_setup"),
        }

    return {
        "ok": True,
        "mode": "mysql+pymysql",
        "host": "127.0.0.1",
        "port": str(status.get("local_port", "") or ""),
        "username": username,
        "password": password,
        "db_name": db_name,
        "use_ssh_tunnel": False,
        "ssh_config_host": "",
        "ssh_local_port": "",
        "ssh_remote_port": "",
        "database_source": "db_ssh_tunnel",
        "database_local_name": "",
        "database_tunnel_name": tunnel_name,
    }


def profile_db_params(app, profile_cfg: dict) -> dict:
    """Build runtime DB params for one APERO profile."""
    username = str(
        app._profile_get_db(profile_cfg, "DATABASE_USERNAME", "")
    ).strip()
    source = app._normalize_db_source(
        app._profile_get_db(profile_cfg, "DATABASE_SOURCE", "")
    )
    local_name = app._resolve_local_db_name_from_profile_cfg(profile_cfg)
    tunnel_name = app._resolve_tunnel_name_from_profile_cfg(profile_cfg)

    if source == "local" and local_name:
        local_defs = app._load_local_db_definitions()
        local_def = local_defs.get(local_name, {})
        if isinstance(local_def, dict) and local_def:
            return {
                "DATABASE_MODE": str(
                    local_def.get("DATABASE_MODE", "") or "mysql+pymysql"
                ).strip(),
                "DATABASE_SOURCE": source,
                "DATABASE_LOCAL_NAME": local_name,
                "DATABASE_TUNNEL_NAME": "",
                "DATABASE_HOST": str(
                    local_def.get("DATABASE_HOST", "") or ""
                ).strip(),
                "DATABASE_PORT": str(
                    local_def.get("DATABASE_PORT", "") or "3306"
                ).strip(),
                "DATABASE_USERNAME": username,
                "DATABASE_PASSWORD": str(
                    app._profile_get_db(profile_cfg, "DATABASE_PASSWORD", "")
                    or ""
                ),
                "DATABASE_NAME": str(
                    app._profile_get_db(profile_cfg, "DATABASE_NAME", "")
                ).strip(),
                "DATABASE_USE_SSH_TUNNEL": False,
                "DATABASE_SSH_CONFIG_HOST": "",
                "DATABASE_SSH_LOCAL_PORT": "",
                "DATABASE_SSH_REMOTE_PORT": "",
                "LOCAL_DATA_DIR": str(app._resolve_local_data_dir()),
            }

    if source == "db_ssh_tunnel" and tunnel_name:
        tunnels = app._load_db_tunnel_definitions()
        tunnel_def = tunnels.get(tunnel_name, {})
        if isinstance(tunnel_def, dict) and tunnel_def:
            tparams = app._build_db_tunnel_runtime_params(
                tunnel_name, tunnel_def, mode="mysql+pymysql"
            )
            host = str(tparams.get("DATABASE_HOST", "") or "").strip()
            port = str(tparams.get("DATABASE_PORT", "") or "").strip()
            return {
                "DATABASE_MODE": str(
                    tparams.get("DATABASE_MODE", "mysql+pymysql")
                ).strip(),
                "DATABASE_SOURCE": source,
                "DATABASE_LOCAL_NAME": "",
                "DATABASE_TUNNEL_NAME": tunnel_name,
                "DATABASE_HOST": host,
                "DATABASE_PORT": port,
                "DATABASE_USERNAME": username,
                "DATABASE_PASSWORD": str(
                    app._profile_get_db(profile_cfg, "DATABASE_PASSWORD", "")
                    or ""
                ),
                "DATABASE_NAME": str(
                    app._profile_get_db(profile_cfg, "DATABASE_NAME", "")
                ).strip(),
                "DATABASE_USE_SSH_TUNNEL": True,
                "DATABASE_SSH_CONFIG_HOST": str(
                    tparams.get("DATABASE_SSH_CONFIG_HOST", "") or ""
                ).strip(),
                "DATABASE_SSH_LOCAL_PORT": str(
                    tparams.get("DATABASE_SSH_LOCAL_PORT", "") or ""
                ).strip(),
                "DATABASE_SSH_REMOTE_PORT": str(
                    tparams.get("DATABASE_SSH_REMOTE_PORT", "") or ""
                ).strip(),
                "LOCAL_DATA_DIR": str(app._resolve_local_data_dir()),
            }

    return {
        "DATABASE_MODE": "",
        "DATABASE_SOURCE": source,
        "DATABASE_LOCAL_NAME": local_name,
        "DATABASE_TUNNEL_NAME": tunnel_name,
        "DATABASE_HOST": "",
        "DATABASE_PORT": "",
        "DATABASE_USERNAME": username,
        "DATABASE_PASSWORD": str(
            app._profile_get_db(profile_cfg, "DATABASE_PASSWORD", "") or ""
        ),
        "DATABASE_NAME": str(
            app._profile_get_db(profile_cfg, "DATABASE_NAME", "")
        ).strip(),
        "DATABASE_USE_SSH_TUNNEL": False,
        "DATABASE_SSH_CONFIG_HOST": "",
        "DATABASE_SSH_LOCAL_PORT": "",
        "DATABASE_SSH_REMOTE_PORT": "",
        "LOCAL_DATA_DIR": str(app._resolve_local_data_dir()),
    }


def resolve_profile_db_test_target(
    app,
    mode: str,
    host: str,
    port: str,
    username: str,
    password: str,
    db_name: str,
    use_ssh_tunnel: bool,
    ssh_config_host: str,
    ssh_local_port: str,
    ssh_remote_port: str,
):
    """Resolve DB test target while keeping tunnel setup on admin page."""
    if not use_ssh_tunnel:
        return {
            "mode": mode,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "db_name": db_name,
            "use_ssh_tunnel": False,
            "ssh_config_host": "",
            "ssh_local_port": "",
            "ssh_remote_port": "",
            "tunnel_required": False,
        }

    db_params = {
        "DATABASE_MODE": mode,
        "DATABASE_HOST": host,
        "DATABASE_PORT": port,
        "DATABASE_USERNAME": username,
        "DATABASE_PASSWORD": password,
        "DATABASE_NAME": db_name,
        "DATABASE_USE_SSH_TUNNEL": True,
        "DATABASE_SSH_CONFIG_HOST": ssh_config_host,
        "DATABASE_SSH_LOCAL_PORT": ssh_local_port,
        "DATABASE_SSH_REMOTE_PORT": ssh_remote_port,
        "LOCAL_DATA_DIR": str(app._resolve_local_data_dir()),
    }
    status = apero_async.get_db_tunnel_status(db_params)
    if not status.get("active"):
        return {
            "tunnel_required": True,
            "error": (
                "No active DB SSH tunnel for this profile. "
                "Open Database Setup and start/authenticate tunnel first."
            ),
            "tunnel_admin_url": url_for("home_admin_portal_database_setup"),
        }

    return {
        "mode": mode,
        "host": "127.0.0.1",
        "port": str(status.get("local_port", "") or ""),
        "username": username,
        "password": password,
        "db_name": db_name,
        "use_ssh_tunnel": False,
        "ssh_config_host": "",
        "ssh_local_port": "",
        "ssh_remote_port": "",
        "tunnel_required": False,
    }


def fetch_table_columns(app, profile_cfg: dict, table_name: str):
    """Fetch ordered column names from a profile DB/table."""
    db_params = app._profile_db_params(profile_cfg)
    if (
        "DATABASE_USER" not in db_params
        and str(db_params.get("DATABASE_USERNAME", "")).strip()
    ):
        db_params["DATABASE_USER"] = str(
            db_params.get("DATABASE_USERNAME", "")
        ).strip()
    mode = str(db_params.get("DATABASE_MODE", "")).strip()
    host = str(db_params.get("DATABASE_HOST", "")).strip()
    username = str(db_params.get("DATABASE_USERNAME", "")).strip()
    db_name = str(db_params.get("DATABASE_NAME", "")).strip()

    if not all([mode, host, username, db_name, table_name]):
        raise ValueError("Missing DB connection or table configuration.")

    if "." in table_name:
        schema_name, table_only = table_name.split(".", 1)
    else:
        schema_name, table_only = db_name, table_name

    if not re.match(r"^[A-Za-z0-9_]+$", schema_name):
        raise ValueError(f"Invalid schema name: {schema_name}")
    if not re.match(r"^[A-Za-z0-9_]+$", table_only):
        raise ValueError(f"Invalid table name: {table_only}")

    # Probe table existence/read access.
    apero_async.database_query(
        db_params, f"SELECT 1 AS ok FROM {app._q_ident(table_name)} LIMIT 1"
    )

    rows = apero_async.database_query(
        db_params,
        (
            "SELECT COLUMN_NAME AS col "
            "FROM information_schema.COLUMNS "
            f"WHERE TABLE_SCHEMA = '{schema_name}' "
            f"AND TABLE_NAME = '{table_only}' "
            "ORDER BY ORDINAL_POSITION"
        ),
    )
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        col = str(row.get("col", "")).strip()
        if col:
            out.append(col)
    return out


def api_apero_profiles_list_tables(app):
    """List available tables in the selected APERO profile database."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    resolved = app._resolve_db_payload_for_test(data)
    if not resolved.get("ok") and resolved.get("requires_tunnel_admin"):
        return jsonify(
            success=True,
            valid=False,
            tables=[],
            requires_tunnel_admin=True,
            error=resolved.get("error", "DB tunnel required."),
            tunnel_admin_url=resolved.get("tunnel_admin_url", ""),
        )
    if not resolved.get("ok"):
        return (
            jsonify(
                success=False,
                error=resolved.get("error", "Invalid database payload"),
            ),
            400,
        )

    db_params = {
        "DATABASE_MODE": resolved["mode"],
        "DATABASE_HOST": resolved["host"],
        "DATABASE_PORT": resolved["port"],
        "DATABASE_USER": resolved["username"],
        "DATABASE_PASSWORD": resolved["password"],
        "DATABASE_NAME": resolved["db_name"],
        "DATABASE_USE_SSH_TUNNEL": resolved["use_ssh_tunnel"],
        "DATABASE_SSH_CONFIG_HOST": resolved["ssh_config_host"],
        "DATABASE_SSH_LOCAL_PORT": resolved["ssh_local_port"],
        "DATABASE_SSH_REMOTE_PORT": resolved["ssh_remote_port"],
        "LOCAL_DATA_DIR": str(app._resolve_local_data_dir()),
    }

    sql_db_name = str(resolved["db_name"]).replace("'", "''")
    query = (
        "SELECT table_name "
        "FROM information_schema.tables "
        f"WHERE table_schema = '{sql_db_name}' "
        "ORDER BY table_name"
    )

    try:
        rows = apero_async.database_query(db_params, query)
        tables = sorted(
            {
                str(row.get("table_name")).strip()
                for row in (rows or [])
                if isinstance(row, dict)
                and str(row.get("table_name") or "").strip()
            }
        )
        return jsonify(success=True, valid=True, tables=tables)
    except Exception as exc:
        return jsonify(success=True, valid=False, error=str(exc), tables=[])


def api_apero_profiles_list(app):
    """List APERO profiles for an instrument."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    instrument = request.args.get("instrument", "").strip()
    if not instrument:
        return jsonify(success=False, error="No instrument"), 400

    params = load_parameters()
    valid = params.get("instruments", {}).get("value", [])
    if instrument not in valid:
        return jsonify(success=False, error="Invalid instrument"), 400

    all_profiles = load_apero_profiles(hydrate=False)
    inst_profiles = all_profiles.get(instrument, {})

    db_keys = [
        "DATABASE_USERNAME",
        "DATABASE_PASSWORD",
        "DATABASE_NAME",
        "DATABASE_SOURCE",
        "DATABASE_LOCAL_NAME",
        "DATABASE_TUNNEL_NAME",
        "ASTROM_TABLENAME",
        "CALIB_TABLENAME",
        "FINDEX_TABLENAME",
        "LOG_TABLENAME",
        "TELLU_TABLENAME",
        "REJECT_TABLENAME",
    ]
    path_keys = [
        "PATH_RAW",
        "PATH_PP",
        "PATH_RED",
        "PATH_CALIB",
        "PATH_OUT",
        "PATH_TELLU",
        "PATH_LOG",
        "PATH_LBL",
            "PATH_CHECK",
            "PATH_OTHER",
            "PATH_TRIGGER_LOG",
            "PATH_CRITICAL_CHECK",
    ]

    profiles = []
    profile_errors = []
    for name, cfg in inst_profiles.items():
        disabled = _profile_disabled(cfg)
        entry = {
            "name": name,
            "DISPLAY_ORDER": cfg.get("DISPLAY_ORDER", 999),
            "groups": cfg.get("groups", []),
            "apero_version": cfg.get("apero_version", ""),
            "reduction_server": cfg.get("reduction_server", ""),
            "disabled": disabled,
        }

        for key in db_keys:
            entry[key] = app._profile_get_db(cfg, key, "")
        entry["DATABASE_SOURCE"] = app._normalize_db_source(
            entry.get("DATABASE_SOURCE", "")
        )
        entry["SCIENCE_FIBER"] = app._profile_get_general(
            cfg, "SCIENCE_FIBER", ""
        )
        entry["SCIENCE_TYPES"] = app._profile_get_general(
            cfg, "SCIENCE_TYPES", []
        )
        entry["APERO_INSTRUMENT_PROFILE"] = cfg.get(
            "APERO_INSTRUMENT_PROFILE", ""
        )

        all_paths_ok = True
        for key in path_keys:
            val = app._profile_get_path(cfg, key, "")
            entry[key] = val
            if disabled:
                entry[key + "_exists"] = True
                continue
            if key in ("PATH_TRIGGER_LOG", "PATH_CRITICAL_CHECK"):
                # Optional paths: only check existence when set, never affect
                # all_paths_ok.  TRIGGER_LOG is a file; CRITICAL_CHECK is a dir.
                if not val:
                    entry[key + "_exists"] = False
                    continue
                entry[key + "_exists"] = Path(val).is_file() if key == "PATH_TRIGGER_LOG" else Path(val).is_dir()
                continue
            if val:
                entry[key + "_exists"] = Path(val).is_dir()
                if not entry[key + "_exists"]:
                    all_paths_ok = False
            else:
                entry[key + "_exists"] = False
                all_paths_ok = False
        entry["all_paths_ok"] = all_paths_ok

        if disabled:
            db_ok = True
            db_error = ''
        else:
            db_check = app._validate_profile_database(cfg)
            db_ok = bool(db_check.get("valid", False))
            db_error = str(db_check.get("error", "")).strip()
        entry["db_ok"] = db_ok
        entry["db_error"] = db_error

        reasons = []
        if disabled:
            reasons.append('disabled')
        if not db_ok:
            reasons.append(f'db: {db_error or "connection failed"}')
        if not all_paths_ok:
        if not all_paths_ok:
            reasons.append("paths: missing or invalid directory")
        if not _optional_path_is_enabled(cfg, 'PATH_TRIGGER_LOG'):
            reasons = [r for r in reasons if 'PATH_TRIGGER_LOG' not in r]
        if not _optional_path_is_enabled(cfg, 'PATH_CRITICAL_CHECK'):
            reasons = [r for r in reasons if 'PATH_CRITICAL_CHECK' not in r]
        entry["status_reasons"] = reasons
        if reasons and not disabled:
            profile_errors.append(
                f"Instrument {instrument} profile {name}: {'; '.join(reasons)}"
            )

        profiles.append(entry)

    profiles.sort(key=lambda p: p["DISPLAY_ORDER"])

    if not profiles:
        status = {
            "level": "warning",
            "headline": "No APERO profiles configured for this instrument.",
            "details": [],
        }
    elif profile_errors:
        status = {
            "level": "error",
            "headline": f"{len(profile_errors)} profile(s) need attention.",
            "details": profile_errors,
        }
    else:
        status = {
            "level": "ok",
            "headline": "Everything ready for this instrument.",
            "details": [],
        }

    return jsonify(success=True, profiles=profiles, status=status)


def api_apero_profiles_test_tables(app):
    """Test table names and fetch available fibers / DPRTYPE options."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    table_keys = [
        "ASTROM_TABLENAME",
        "CALIB_TABLENAME",
        "FINDEX_TABLENAME",
        "LOG_TABLENAME",
        "TELLU_TABLENAME",
        "REJECT_TABLENAME",
    ]

    resolved = app._resolve_db_payload_for_test(data)
    if not resolved.get("ok") and resolved.get("requires_tunnel_admin"):
        return jsonify(
            success=True,
            valid=False,
            requires_tunnel_admin=True,
            error=resolved.get("error", "DB tunnel required."),
            tunnel_admin_url=resolved.get("tunnel_admin_url", ""),
        )
    if not resolved.get("ok"):
        return (
            jsonify(
                success=False,
                error=resolved.get("error", "Invalid database payload"),
            ),
            400,
        )

    tables = {}
    for key in table_keys:
        val = str(data.get(key, "")).strip()
        if not val:
            return jsonify(success=False, error=f"{key} is required"), 400
        if not re.match(r"^[A-Za-z0-9_\.]+$", val):
            return (
                jsonify(success=False, error=f"Invalid table name: {key}"),
                400,
            )
        tables[key] = val

    def qtable(name):
        return ".".join(f"`{part}`" for part in name.split("."))

    db_params = {
        "DATABASE_MODE": resolved["mode"],
        "DATABASE_HOST": resolved["host"],
        "DATABASE_PORT": resolved["port"],
        "DATABASE_USER": resolved["username"],
        "DATABASE_PASSWORD": resolved["password"],
        "DATABASE_NAME": resolved["db_name"],
        "DATABASE_USE_SSH_TUNNEL": resolved["use_ssh_tunnel"],
        "DATABASE_SSH_CONFIG_HOST": resolved["ssh_config_host"],
        "DATABASE_SSH_LOCAL_PORT": resolved["ssh_local_port"],
        "DATABASE_SSH_REMOTE_PORT": resolved["ssh_remote_port"],
        "LOCAL_DATA_DIR": str(app._resolve_local_data_dir()),
    }

    try:
        for key in table_keys:
            query = f"SELECT 1 AS ok FROM {qtable(tables[key])} LIMIT 1"
            apero_async.database_query(db_params, query)

        findex = qtable(tables["FINDEX_TABLENAME"])
        fiber_rows = apero_async.database_query(
            db_params,
            f"""
            SELECT KW_FIBER AS value
            FROM {findex}
            WHERE KW_FIBER IS NOT NULL
                AND KW_FIBER <> ''
            GROUP BY KW_FIBER
            """,
        )
        dpr_rows = apero_async.database_query(
            db_params,
            f"""
            SELECT KW_DPRTYPE AS value
            FROM {findex}
            WHERE KW_DPRTYPE IS NOT NULL
                AND KW_DPRTYPE <> ''
            GROUP BY KW_DPRTYPE
            """,
        )

        fibers = sorted(
            {
                str(r.get("value")).strip()
                for r in fiber_rows
                if str(r.get("value", "")).strip()
            }
        )
        dprtypes = sorted(
            {
                str(r.get("value")).strip()
                for r in dpr_rows
                if str(r.get("value", "")).strip()
            }
        )

        return jsonify(
            success=True, valid=True, fibers=fibers, dprtypes=dprtypes
        )
    except Exception as exc:
        return jsonify(
            success=True, valid=False, error=str(exc), fibers=[], dprtypes=[]
        )


def build_apero_profiles_overview_status(app) -> dict:
    """Build all-instruments APERO profile readiness and issue details."""
    profiles_by_instrument = load_apero_profiles()
    path_keys = [
        "PATH_RAW",
        "PATH_PP",
        "PATH_RED",
        "PATH_CALIB",
        "PATH_OUT",
        "PATH_TELLU",
        "PATH_LOG",
        "PATH_LBL",
            "PATH_CHECK",
            "PATH_OTHER",
    ]
    # PATH_TRIGGER_LOG is intentionally excluded here: it is an optional path
    # (only the reduced manual-trigger checks need it) so an empty value must
    # not flag an otherwise-healthy profile as needing attention.

    issues = []
    total_profiles = 0
    per_instrument = {}

    for instrument, inst_profiles in profiles_by_instrument.items():
        if not isinstance(inst_profiles, dict):
            continue

        inst_issues = []
        inst_total = 0
        for name, cfg in inst_profiles.items():
            if not isinstance(cfg, dict):
                continue
            total_profiles += 1
            inst_total += 1

            if _profile_disabled(cfg):
                continue

            reason_parts = []

            db = app._validate_profile_database(cfg)
            if not db.get("valid", False):
                db_error = str(
                    db.get("error", "") or "connection failed"
                ).strip()
                reason_parts.append(f"Database error: {db_error}")

            invalid_paths = []
            for key in path_keys:
                path_val = str(app._profile_get_path(cfg, key, "")).strip()
                if not path_val or not Path(path_val).is_dir():
                    invalid_paths.append(key)
            if invalid_paths:
                reason_parts.append(
                    "Invalid paths: " + ", ".join(invalid_paths)
                )

            if not str(cfg.get("APERO_INSTRUMENT_PROFILE", "")).strip():
                reason_parts.append("No instrument profile selected")

            if reason_parts:
                line = (
                    f"Instrument {instrument} profile {name}: "
                    f'{" | ".join(reason_parts)}'
                )
                issues.append(line)
                inst_issues.append(line)

        per_instrument[instrument] = {
            "total_profiles": inst_total,
            "issues": inst_issues,
        }

    if issues:
        status = {
            "level": "error",
            "headline": "Some APERO profiles need attention.",
            "details": issues,
        }
    else:
        status = {
            "level": "ok",
            "headline": "All profiles across instruments ready.",
            "details": [],
        }

    return {
        "status": status,
        "issues": issues,
        "total_profiles": total_profiles,
        "per_instrument": per_instrument,
    }


def api_apero_profiles_save(app, package_dir: Path):
    """Create or update an APERO profile."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    name = data.get("name", "").strip()

    if not instrument or not name:
        return jsonify(success=False, error="Missing fields"), 400

    if not re.match(r"^[\w\-]+$", name):
        return (
            jsonify(
                success=False, error="Name must be alphanumeric (with _ or -)"
            ),
            400,
        )

    _META_KEYS = ["apero_version", "reduction_server"]
    _DB_REQUIRED_KEYS = [
        "DATABASE_USERNAME",
        "DATABASE_NAME",
        "ASTROM_TABLENAME",
        "CALIB_TABLENAME",
        "FINDEX_TABLENAME",
        "LOG_TABLENAME",
        "TELLU_TABLENAME",
        "REJECT_TABLENAME",
    ]
    _DB_OPTIONAL_KEYS = [
        "DATABASE_PASSWORD",
        "DATABASE_SOURCE",
        "DATABASE_LOCAL_NAME",
        "DATABASE_TUNNEL_NAME",
    ]
    _apero_instrument_profile = str(
        data.get("APERO_INSTRUMENT_PROFILE", "") or ""
    ).strip()
    _PATH_KEYS = [
        "PATH_RAW",
        "PATH_PP",
        "PATH_RED",
        "PATH_CALIB",
        "PATH_OUT",
        "PATH_TELLU",
        "PATH_LOG",
        "PATH_LBL",
        "PATH_CHECK",
        "PATH_OTHER",
    ]
    # Optional path keys: not required, but validated as absolute when set.
    _PATH_OPTIONAL_KEYS = [
        "PATH_TRIGGER_LOG",
        "PATH_CRITICAL_CHECK",
    ]

    values = {}
    for k in _META_KEYS:
        val = data.get(k, "").strip()
        if not val:
            return jsonify(success=False, error=f"{k} is required"), 400
        values[k] = val

    db_values = {}
    for k in _DB_REQUIRED_KEYS:
        val = data.get(k, "").strip()
        if not val:
            return jsonify(success=False, error=f"{k} is required"), 400
        db_values[k] = val
    db_values["DATABASE_PASSWORD"] = data.get("DATABASE_PASSWORD", "")
    for k in _DB_OPTIONAL_KEYS:
        if k == "DATABASE_PASSWORD":
            continue
        db_values[k] = str(data.get(k, "") or "").strip()

    database_source = app._normalize_db_source(data.get("DATABASE_SOURCE", ""))
    local_name = str(data.get("DATABASE_LOCAL_NAME", "") or "").strip()
    tunnel_name = str(data.get("DATABASE_TUNNEL_NAME", "") or "").strip()

    db_values["DATABASE_SOURCE"] = database_source
    db_values["DATABASE_LOCAL_NAME"] = local_name
    db_values["DATABASE_TUNNEL_NAME"] = tunnel_name

    if database_source == "local":
        if not local_name:
            return (
                jsonify(
                    success=False,
                    error=(
                        "DATABASE_LOCAL_NAME is required "
                        "when DATABASE_SOURCE is local"
                    ),
                ),
                400,
            )
        local_defs = app._load_local_db_definitions()
        local_def = local_defs.get(local_name, {})
        if not isinstance(local_def, dict) or not local_def:
            return (
                jsonify(
                    success=False,
                    error=f"Unknown local database definition: {local_name}",
                ),
                400,
            )
        db_values.pop("DATABASE_MODE", None)
        db_values.pop("DATABASE_HOST", None)
        db_values.pop("DATABASE_PORT", None)
        db_values["DATABASE_TUNNEL_NAME"] = ""
    else:
        if not tunnel_name:
            return (
                jsonify(
                    success=False,
                    error=(
                        "DATABASE_TUNNEL_NAME is required when "
                        "DATABASE_SOURCE is db_ssh_tunnel"
                    ),
                ),
                400,
            )
        tunnels = app._load_db_tunnel_definitions()
        tunnel_def = tunnels.get(tunnel_name, {})
        if not isinstance(tunnel_def, dict) or not tunnel_def:
            return (
                jsonify(
                    success=False,
                    error=f"Unknown DB tunnel definition: {tunnel_name}",
                ),
                400,
            )
        db_values.pop("DATABASE_MODE", None)
        db_values.pop("DATABASE_HOST", None)
        db_values.pop("DATABASE_PORT", None)
        db_values["DATABASE_LOCAL_NAME"] = ""

    science_fiber = str(data.get("SCIENCE_FIBER", "")).strip()
    if not science_fiber:
        return jsonify(success=False, error="SCIENCE_FIBER is required"), 400

    path_values = {}
    for k in _PATH_KEYS:
        val = data.get(k, "").strip()
        if not val:
            return jsonify(success=False, error=f"{k} is required"), 400
        if not os.path.isabs(val):
            return (
                jsonify(success=False, error=f"{k} must be an absolute path"),
                400,
            )
        path_values[k] = val
    # Optional paths: only validated (as absolute) when a value is provided.
    for k in _PATH_OPTIONAL_KEYS:
        val = data.get(k, "").strip()
        if not val:
            path_values[k] = ""
            continue
        if not os.path.isabs(val):
            return (
                jsonify(success=False, error=f"{k} must be an absolute path"),
                400,
            )
        path_values[k] = val

    science_types_raw = data.get("SCIENCE_TYPES", [])
    if isinstance(science_types_raw, str):
        science_types = [
            t.strip() for t in science_types_raw.split(",") if t.strip()
        ]
    else:
        science_types = [
            str(t).strip() for t in science_types_raw if str(t).strip()
        ]
    if not science_types:
        return jsonify(success=False, error="SCIENCE_TYPES is required"), 400

    all_profiles = load_apero_profiles(hydrate=False)
    inst_profiles = all_profiles.setdefault(instrument, {})

    if name in inst_profiles:
        order = inst_profiles[name].get("DISPLAY_ORDER", 999)
    else:
        max_order = max(
            (p.get("DISPLAY_ORDER", 0) for p in inst_profiles.values()),
            default=0,
        )
        order = max_order + 1

    if name in inst_profiles:
        existing_groups = inst_profiles[name].get("groups", [])
        existing_disabled = _profile_disabled(inst_profiles[name])
    else:
        existing_groups = []
        existing_disabled = False
    new_groups = data.get("groups", existing_groups)
    if not isinstance(new_groups, list):
        return jsonify(success=False, error="groups must be a list"), 400
    new_groups = [str(g).strip() for g in new_groups if str(g).strip()]
    if not new_groups:
        return (
            jsonify(success=False, error="At least one group is required"),
            400,
        )

    profile_data = {"DISPLAY_ORDER": order, "groups": new_groups}
    profile_data['disabled'] = _to_bool(
        data.get('disabled', existing_disabled)
    )
    profile_data.update(values)
    profile_data["database"] = dict(db_values)
    profile_data["paths"] = dict(path_values)
    profile_data["general"] = {
        "INSTRUMENT": instrument,
        "SCIENCE_FIBER": science_fiber,
        "SCIENCE_TYPES": science_types,
    }
    if _apero_instrument_profile:
        profile_data["APERO_INSTRUMENT_PROFILE"] = _apero_instrument_profile
        preset_path = (
            package_dir
            / "resources"
            / "aprofile_instruments"
            / _apero_instrument_profile
        )
        if not preset_path.is_file():
            return (
                jsonify(
                    success=False,
                    error=(
                        "Instrument profile file not found: "
                        f"{_apero_instrument_profile}"
                    ),
                ),
                400,
            )
    inst_profiles[name] = profile_data
    all_profiles[instrument] = inst_profiles
    save_apero_profiles(all_profiles)
    audit_log.record(
        actor=user_info.get("username", ""),
        action="apero_profile.save",
        target=f"{instrument}/{name}",
    )
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def api_apero_profiles_toggle_disabled(app):
    """Toggle a profile's disabled flag."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    data = request.get_json() or {}
    instrument = str(data.get('instrument', '')).strip()
    name = str(data.get('name', '')).strip()
    if not instrument or not name:
        return jsonify(success=False, error='Missing fields'), 400

    all_profiles = load_apero_profiles(hydrate=False)
    inst_profiles = all_profiles.get(instrument, {})
    if name not in inst_profiles or not isinstance(inst_profiles[name], dict):
        return jsonify(success=False, error='Profile not found'), 404

    current = _profile_disabled(inst_profiles[name])
    if 'disabled' in data:
        new_value = _to_bool(data.get('disabled'))
    else:
        new_value = not current

    inst_profiles[name]['disabled'] = new_value
    all_profiles[instrument] = inst_profiles
    save_apero_profiles(all_profiles)
    audit_log.record(
        actor=user_info.get("username", ""),
        action="apero_profile.toggle_disabled",
        target=f"{instrument}/{name}",
        detail={"disabled": new_value},
    )
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True, disabled=new_value)
