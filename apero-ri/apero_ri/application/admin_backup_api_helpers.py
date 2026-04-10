"""Admin backup API helper functions for ARIApp."""

import json
import os
from pathlib import Path

from apero_ri.core import backup_backend as bb
from apero_ri.core import secret_store as ss
from flask import jsonify, request, session, url_for
from werkzeug.utils import secure_filename


def api_admin_backups_oauth_callback(app):
    """Handle Google OAuth callback for backup configuration."""
    user_info, perms = app._require_admin_backup_perm()
    if not user_info:
        return "Unauthorized", 401
    if "manage.admin.backup" not in (perms or set()):
        return "Insufficient permissions", 403

    cfg = bb.load_backup_config()
    client_secret_path = Path(
        str(cfg.get("gdrive_oauth_client_secret_file", "")).strip()
    ).expanduser()
    if not client_secret_path.exists():
        return "Google OAuth client secret file not found.", 400

    if request.args.get("error"):
        err = str(request.args.get("error", "")).strip()
        return (
            "<html><body><h3>Google OAuth failed</h3>"
            f"<p>{err}</p><script>setTimeout(function(){{window.close();}}, "
            "1500);</script>"
            "</body></html>"
        )

    expected_state = str(session.get("ab_google_oauth_state", "") or "").strip()
    expected_code_verifier = str(
        session.get("ab_google_oauth_code_verifier", "") or ""
    ).strip()
    got_state = str(request.args.get("state", "") or "").strip()
    if not expected_state or expected_state != got_state:
        return "Google OAuth state mismatch. Please retry connect.", 400
    if not expected_code_verifier:
        return (
            "Google OAuth verifier missing in session. Please retry connect.",
            400,
        )

    try:
        from google_auth_oauthlib.flow import Flow
    except Exception:
        return "google-auth-oauthlib is not installed.", 500

    redirect_uri = url_for("api_admin_backups_oauth_callback", _external=True)
    flow = Flow.from_client_secrets_file(
        str(client_secret_path),
        scopes=bb.GDRIVE_OAUTH_SCOPES,
        state=expected_state,
        redirect_uri=redirect_uri,
        code_verifier=expected_code_verifier,
    )

    host_name = str(request.host or "").split(":", 1)[0].strip().lower()
    is_local_host = host_name in {"localhost", "127.0.0.1", "::1"}
    allow_insecure = str(
        os.environ.get("ARI_ALLOW_INSECURE_OAUTH", "")
    ).strip().lower() in {"1", "true", "yes", "on"}
    using_https = bool(request.is_secure)

    if (not using_https) and (not is_local_host) and (not allow_insecure):
        return (
            "<html><body><h3>Google OAuth requires HTTPS</h3>"
            "<p>This callback was reached over HTTP. Use an HTTPS URL "
            "for APERO RI, "
            "or (for trusted private testing only) set "
            "ARI_ALLOW_INSECURE_OAUTH=1 "
            "before starting the server.</p>"
            "<script>setTimeout(function(){window.close();}, 3000);</script>"
            "</body></html>"
        ), 400

    old_insecure = os.environ.get("OAUTHLIB_INSECURE_TRANSPORT")
    try:
        if (not using_https) and (is_local_host or allow_insecure):
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        flow.fetch_token(authorization_response=request.url)
    except Exception as exc:
        msg = str(exc) or "OAuth token exchange failed."
        return (
            "<html><body><h3>Google OAuth failed</h3>"
            f"<p>{msg}</p><script>setTimeout(function(){{window.close();}}, "
            "2500);</script>"
            "</body></html>"
        ), 400
    finally:
        if old_insecure is None:
            os.environ.pop("OAUTHLIB_INSECURE_TRANSPORT", None)
        else:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = old_insecure

    token_path = bb.save_gdrive_oauth_token(
        cfg, json.loads(flow.credentials.to_json())
    )
    cfg["gdrive_oauth_token_file"] = str(token_path)
    bb.save_backup_config(cfg)
    app._refresh_admin_health_after_change(user_info, perms)
    session.pop("ab_google_oauth_state", None)
    session.pop("ab_google_oauth_code_verifier", None)

    return (
        "<html><body><h3>Google account connected</h3>"
        "<p>You can close this window.</p>"
        "<script>setTimeout(function(){window.close();}, 1200);</script>"
        "</body></html>"
    )


def api_admin_backups_upload_json(app):
    """Upload and validate JSON secret files for backup configuration."""
    user_info, perms = app._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.admin.backup" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    target_field = str(request.form.get("target_field", "")).strip()
    allowed_targets = {
        "gdrive_oauth_client_secret_file",
        "s3_credentials_file",
    }
    if target_field not in allowed_targets:
        return jsonify(success=False, error="Invalid target field."), 400

    if "file" not in request.files:
        return jsonify(success=False, error="No file provided."), 400

    uploaded = request.files["file"]
    if not uploaded or not uploaded.filename:
        return jsonify(success=False, error="Empty filename."), 400

    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".json"):
        return (
            jsonify(success=False, error="Only .json files are accepted."),
            400,
        )

    payload = uploaded.read()
    if not payload:
        return jsonify(success=False, error="Uploaded file is empty."), 400
    if len(payload) > 5 * 1024 * 1024:
        return (
            jsonify(success=False, error="JSON file is too large (max 5 MB)."),
            400,
        )

    try:
        json.loads(payload.decode("utf-8"))
    except Exception:
        return (
            jsonify(
                success=False, error="Uploaded file is not valid UTF-8 JSON."
            ),
            400,
        )

    upload_targets = {
        "gdrive_oauth_client_secret_file": "gdrive_oauth_client_secret.json",
        "s3_credentials_file": "s3_credentials.json",
    }
    final_path = ss.get_secret_path(upload_targets[target_field])

    with open(final_path, "wb") as handle:
        handle.write(payload)

    ss.protect_path(final_path, 0o600)

    return jsonify(
        success=True, stored_file=final_path.name, stored_path=str(final_path)
    )


def api_admin_backups_save(app):
    """Save admin backup configuration settings."""
    user_info, perms = app._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.admin.backup" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json() or {}
    allowed = {
        "enabled",
        "provider",
        "gdrive_oauth_client_secret_file",
        "gdrive_oauth_token_file",
        "gdrive_folder_id",
        "s3_bucket",
        "s3_prefix",
        "s3_region",
        "s3_endpoint_url",
        "s3_access_key_id",
        "s3_secret_access_key",
        "s3_credentials_file",
        "rsync_ssh_target",
        "rsync_remote_dir",
        "rsync_ssh_key",
        "rsync_port",
        "rsync_extra_opts",
        "local_mirror_dir",
        "backup_methods",
        "active_method_id",
    }

    existing = bb.load_backup_config()
    cfg = dict(existing)
    for key in allowed:
        if key in body:
            cfg[key] = body.get(key)

    if "enabled" in body:
        enabled_val = body.get("enabled")
        if isinstance(enabled_val, bool):
            cfg["enabled"] = enabled_val
        else:
            cfg["enabled"] = str(enabled_val).strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }

    if "s3_secret_access_key" not in body and existing.get(
        "s3_secret_access_key_enc"
    ):
        cfg["s3_secret_access_key_enc"] = existing.get(
            "s3_secret_access_key_enc", ""
        )

    bb.save_backup_config(cfg)
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)
