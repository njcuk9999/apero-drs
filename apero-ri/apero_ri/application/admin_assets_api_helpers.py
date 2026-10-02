"""Admin Asset Management API helper functions for ARIApp."""

import os

from flask import abort, jsonify, request, send_from_directory, url_for

from apero_ri.core import asset_management as am
from apero_ri.core.permissions import resolve_user_permissions

# default cap (MB) on an asset upload request body (tars can be large)
_DEFAULT_MAX_UPLOAD_MB = 4096


def _require_asset_admin(app):
    """
    Resolve the session/Bearer-token user and check asset permission.

    :return: (user_info, None) on success or (None, error_response)
    """
    user_info = app._get_api_user()
    if not user_info:
        return None, (jsonify(success=False, error="Unauthorized"), 401)
    perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    if am.ASSET_PERMISSION not in perms:
        return None, (jsonify(success=False, error="Forbidden"), 403)
    return user_info, None


def _setup_required_response():
    """Return the response telling clients the admin must set a path."""
    setup_url = url_for(
        am.ASSET_PAGE_ID.replace(".", "_"), _external=True
    )
    msg = (
        "Asset hosting is not set up on this ARI server. An admin must "
        f"set the assets directory at: {setup_url}"
    )
    return jsonify(success=False, error=msg, setup_required=True,
                   setup_url=setup_url), 409


def _public_base_url():
    """Return the public download base url (for AURLS.URLS)."""
    return request.url_root.rstrip("/") + am.PUBLIC_URL_PREFIX


def api_admin_assets_status(app):
    """Return the configured assets path and the hosted file index."""
    _, err = _require_asset_admin(app)
    if err:
        return err
    cfg = am.load_config()
    assets_dir = am.get_assets_dir()
    files = [] if assets_dir is None else am.list_files(assets_dir)
    return jsonify(success=True, configured=assets_dir is not None,
                   assets_path=cfg["assets_path"],
                   public_download=cfg["public_download"],
                   public_url=_public_base_url(), files=files)


def api_admin_assets_config(app):
    """Set the directory on this server that hosts the assets."""
    _, err = _require_asset_admin(app)
    if err:
        return err
    body = request.get_json(silent=True) or {}
    public_download = bool(body.get("public_download", True))
    try:
        assets_dir = am.set_assets_path(body.get("assets_path", ""),
                                        public_download=public_download)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    return jsonify(success=True, assets_path=str(assets_dir),
                   public_download=public_download)


def _send_asset(assets_dir, filename):
    """Send a hosted asset file as an attachment (404 if invalid)."""
    try:
        name = am.validate_filename(filename)
    except ValueError:
        abort(404)
    return send_from_directory(assets_dir, name, as_attachment=True)


def public_assets_download(app, filename):
    """Public (no login) download of a hosted asset file."""
    assets_dir = am.get_assets_dir()
    if assets_dir is None or not am.load_config()["public_download"]:
        abort(404)
    return _send_asset(assets_dir, filename)


def api_assets_download(app, filename):
    """Download a hosted asset file with any valid session/API token."""
    if not app._get_api_user():
        return jsonify(success=False, error="Unauthorized"), 401
    assets_dir = am.get_assets_dir()
    if assets_dir is None:
        return _setup_required_response()
    return _send_asset(assets_dir, filename)


def api_admin_assets_delete(app):
    """Delete a hosted asset file from disk."""
    _, err = _require_asset_admin(app)
    if err:
        return err
    assets_dir = am.get_assets_dir()
    if assets_dir is None:
        return _setup_required_response()
    body = request.get_json(silent=True) or {}
    try:
        deleted = am.delete_file(assets_dir, body.get("filename", ""))
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    if not deleted:
        return jsonify(success=False, error="File not found"), 404
    return jsonify(success=True)


def api_admin_assets_upload(app):
    """
    Receive an asset file as a raw request body (used by apero_assets.py).

    Query args: ``filename`` (required), ``overwrite`` (``1``/``0``).
    Optional header ``X-Content-MD5`` is verified against the upload.
    """
    _, err = _require_asset_admin(app)
    if err:
        return err
    assets_dir = am.get_assets_dir()
    if assets_dir is None:
        return _setup_required_response()
    try:
        max_mb = int(os.environ.get("ARI_ASSETS_MAX_UPLOAD_MB",
                                    _DEFAULT_MAX_UPLOAD_MB))
    except ValueError:
        max_mb = _DEFAULT_MAX_UPLOAD_MB
    # override the global MAX_CONTENT_LENGTH for this request only
    request.max_content_length = max_mb * 1024 * 1024
    filename = request.args.get("filename", "")
    overwrite = request.args.get("overwrite", "0") in ("1", "true", "yes")
    expected_md5 = request.headers.get("X-Content-MD5")
    try:
        sv_args = [assets_dir, filename, request.stream]
        sv_kwargs = dict(expected_md5=expected_md5, overwrite=overwrite)
        stored = am.save_stream(*sv_args, **sv_kwargs)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    return jsonify(success=True, **stored)
