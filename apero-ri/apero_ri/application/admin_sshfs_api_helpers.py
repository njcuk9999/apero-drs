"""Admin SSHFS API helper functions for ARIApp."""

from apero_ri.core import sshfs_backend as sb
from apero_ri.core.auth import get_effective_user
from apero_ri.core.permissions import resolve_user_permissions
from flask import jsonify, request, session


def api_admin_sshfs_interactive_close(app):
    """Close and clean up an interactive SSH/SSHFS session."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    from apero_ri.core.sshfs_interactive import close_session

    body = request.get_json(silent=True) or {}
    token = str(body.get("token", "")).strip()
    if not token:
        return jsonify(ok=False, error="token required"), 400

    result = close_session(token)

    mount_name = str(body.get("mount_name", "")).strip()
    if mount_name:
        from apero_ri.core.sshfs_interactive import finalise_interactive_mount

        terminal_log = str(body.get("terminal_log", "")).strip()
        if terminal_log:
            sb.save_mount_log(
                mount_name,
                terminal_log.splitlines(),
                source="interactive",
            )
        mount_status = sb.check_mount_status(mount_name)
        if mount_status.get("mounted"):
            finalise_interactive_mount(mount_name)
            app._refresh_admin_health_after_change(user_info, perms)
            result["mount_ok"] = True
        else:
            result["mount_ok"] = False

    return jsonify(**result)
