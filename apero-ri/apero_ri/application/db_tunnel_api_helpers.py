"""DB tunnel API helper functions for ARIApp."""

import re

from apero_ri.core.auth import validate_database_connection
from apero_ri.tasks import apero_async
from flask import jsonify, request


def api_db_ssh_tunnel_test(app):
    """Test one DB SSH tunnel definition with supplied credentials."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    persist_test_details = bool(body.get('persist_test_details', False))
    name = str(body.get("name", "") or "").strip()
    ssh_config_host = str(body.get("ssh_config_host", "") or "").strip()
    remote_host = str(body.get("remote_host", "") or "").strip()
    remote_port = str(body.get("remote_port", "") or "").strip() or "3306"
    local_port = str(body.get("local_port", "") or "").strip()
    req_username = str(
        body.get('DB_USERNAME_TEST', body.get('DATABASE_USERNAME', '')) or ''
    ).strip()
    req_password = str(
        body.get('DB_PASSWORD_TEST', body.get('DATABASE_PASSWORD', '')) or ''
    )
    req_db_name = str(
        body.get('DB_NAME_TEST', body.get('DATABASE_NAME', '')) or ''
    ).strip()
    username = req_username
    password = req_password
    db_name = req_db_name

    has_direct_tunnel_fields = bool(
        ssh_config_host or remote_host or local_port
    )

    tunnels = None
    tdef = None
    saved_test_details = False
    pending_user = ''
    pending_pass = ''
    pending_db_name = ''

    if name:
        tunnels = app._load_db_tunnel_definitions()
        tdef = tunnels.get(name, {})
        if not isinstance(tdef, dict) or not tdef:
            return jsonify(success=False, error="Tunnel not found"), 404

    if name and not has_direct_tunnel_fields:
        ssh_config_host = (
            ssh_config_host
            or str(tdef.get("ssh_config_host", "") or "").strip()
        )
        remote_host = (
            remote_host or str(tdef.get("remote_host", "") or "").strip()
        )
        remote_port = (
            remote_port or str(tdef.get("remote_port", "") or "").strip()
        )
        local_port = local_port or str(tdef.get("local_port", "") or "").strip()
        username = (
            username
            or str(
                tdef.get(
                    'DB_USERNAME_TEST', tdef.get('DATABASE_USERNAME', '')
                )
                or ''
            ).strip()
        )
        password = password or str(
            tdef.get('DB_PASSWORD_TEST', tdef.get('DATABASE_PASSWORD', ''))
            or ''
        )
        db_name = db_name or str(
            tdef.get('DB_NAME_TEST', tdef.get('DATABASE_NAME', '')) or ''
        ).strip()

    if name and persist_test_details and isinstance(tdef, dict):
        old_user = str(
            tdef.get('DB_USERNAME_TEST', tdef.get('DATABASE_USERNAME', ''))
            or ''
        ).strip()
        old_pass = str(
            tdef.get('DB_PASSWORD_TEST', tdef.get('DATABASE_PASSWORD', ''))
            or ''
        )
        old_db_name = str(
            tdef.get('DB_NAME_TEST', tdef.get('DATABASE_NAME', '')) or ''
        ).strip()
        if req_username and not old_user:
            pending_user = req_username
        if req_password and not old_pass:
            pending_pass = req_password
        if req_db_name and not old_db_name:
            pending_db_name = req_db_name

    remote_port = remote_port or "3306"

    if not ssh_config_host:
        return (
            jsonify(
                success=False, error="DATABASE_SSH_CONFIG_HOST is required"
            ),
            400,
        )
    if not remote_host:
        return jsonify(success=False, error="DATABASE_HOST is required"), 400
    if not local_port:
        return (
            jsonify(success=False, error="DATABASE_SSH_LOCAL_PORT is required"),
            400,
        )
    if not str(remote_port).isdigit() or not str(local_port).isdigit():
        return (
            jsonify(
                success=False,
                error=(
                    "DATABASE_SSH_LOCAL_PORT and "
                    "DATABASE_SSH_REMOTE_PORT must be numeric"
                ),
            ),
            400,
        )
    if not username or not db_name:
        return (
            jsonify(
                success=False,
                error="DB_USERNAME_TEST and DB_NAME_TEST are required",
            ),
            400,
        )

    runtime = app._build_db_tunnel_runtime_params(
        name or "__adhoc__",
        {
            "ssh_config_host": ssh_config_host,
            "remote_host": remote_host,
            "remote_port": remote_port,
            "local_port": local_port,
        },
        mode="mysql+pymysql",
    )
    try:
        status = apero_async.get_db_tunnel_status(runtime)
    except Exception as exc:
        return jsonify(success=True, valid=False, error=str(exc)), 200

    if not (status.get("active") or status.get("local_port_open")):
        return jsonify(
            success=True,
            valid=False,
            error=(
                "No active DB SSH tunnel for this definition. "
                "Use Ensure Active or Interactive Auth first."
            ),
            status=status,
        )

    result = validate_database_connection(
        "mysql+pymysql",
        "127.0.0.1",
        username,
        password,
        db_name,
        port=str(status.get("local_port", "") or ""),
        use_ssh_tunnel=False,
        ssh_config_host="",
        ssh_local_port="",
        ssh_remote_port="",
        local_data_dir=str(app._resolve_local_data_dir()),
    )
    if result.get('valid') and name and isinstance(tdef, dict):
        updated = False
        if pending_user:
            tdef['DB_USERNAME_TEST'] = pending_user
            updated = True
        if pending_pass:
            tdef['DB_PASSWORD_TEST'] = pending_pass
            updated = True
        if pending_db_name:
            tdef['DB_NAME_TEST'] = pending_db_name
            updated = True
        if updated:
            tunnels[name] = tdef
            app._save_db_tunnel_definitions(tunnels)
            app._refresh_admin_health_after_change(user_info, perms)
            saved_test_details = True
    return jsonify(
        success=True,
        status=status,
        saved_test_details=saved_test_details,
        **result,
    )


def api_db_ssh_tunnel_close(app):
    """Close one selected named DB tunnel or all saved DB tunnels."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    close_all = bool(body.get("close_all", False))
    rows = app._list_db_tunnel_rows()

    if close_all:
        seen_controls = set()
        closed = 0
        failed = []
        for row in rows:
            if not row.get("valid_config"):
                continue
            try:
                status = (
                    row.get("status", {})
                    if isinstance(row.get("status"), dict)
                    else {}
                )
                control_path = str(status.get("control_path", "") or "")
                if not control_path or control_path in seen_controls:
                    continue
                seen_controls.add(control_path)
                tdef = (
                    row.get("definition", {})
                    if isinstance(row.get("definition"), dict)
                    else {}
                )
                db_params = app._build_db_tunnel_runtime_params(
                    str(row.get("name", "") or ""), tdef
                )
                result = apero_async.close_db_tunnel(db_params)
                if result.get("ok"):
                    closed += 1
                else:
                    failed.append(result.get("error", "Unknown close error"))
            except Exception as exc:
                failed.append(str(exc))

        if failed:
            return jsonify(
                success=False, error="; ".join(failed), closed=closed
            )
        return jsonify(
            success=True, message="Closed all DB SSH tunnels.", closed=closed
        )

    tunnel_name = str(body.get("tunnel_name", "") or "").strip()
    if not tunnel_name:
        return jsonify(success=False, error="tunnel_name is required"), 400

    tunnels = app._load_db_tunnel_definitions()
    tunnel_def = tunnels.get(tunnel_name, {})
    if not isinstance(tunnel_def, dict) or not tunnel_def:
        return jsonify(success=False, error="Tunnel not found"), 404

    db_params = app._build_db_tunnel_runtime_params(tunnel_name, tunnel_def)
    result = apero_async.close_db_tunnel(db_params)
    status_code = 200 if result.get("ok") else 500
    return jsonify(success=bool(result.get("ok")), **result), status_code


def api_database_setup_local_db_save(app):
    """Create/update one reusable local database definition."""
    user_info, perms = app._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "") or "").strip()
    mode = str(body.get("DATABASE_MODE", "") or "").strip() or "mysql+pymysql"
    host = str(body.get("DATABASE_HOST", "") or "").strip()
    port = str(body.get("DATABASE_PORT", "") or "").strip() or "3306"
    username = str(body.get("DATABASE_USERNAME", "") or "").strip()
    password = str(body.get("DATABASE_PASSWORD", "") or "")
    db_name = str(body.get("DATABASE_NAME", "") or "").strip()
    notes = str(body.get("notes", "") or "").strip()

    if not name:
        return jsonify(success=False, error="name is required"), 400
    if not re.match(r"^[A-Za-z0-9_\-]+$", name):
        return (
            jsonify(
                success=False,
                error="name must be alphanumeric, dash, or underscore",
            ),
            400,
        )
    if mode not in ("mysql+pymysql",):
        return jsonify(success=False, error="Unsupported DATABASE_MODE"), 400
    if not host:
        return jsonify(success=False, error="DATABASE_HOST is required"), 400
    if not port.isdigit():
        return (
            jsonify(success=False, error="DATABASE_PORT must be numeric"),
            400,
        )

    defs = app._load_local_db_definitions()
    defs[name] = {
        "DATABASE_MODE": mode,
        "DATABASE_HOST": host,
        "DATABASE_PORT": port,
        "DATABASE_USERNAME": username,
        "DATABASE_PASSWORD": password,
        "DATABASE_NAME": db_name,
        "notes": notes,
    }
    app._save_local_db_definitions(defs)
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)
