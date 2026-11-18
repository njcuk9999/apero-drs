#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: APERO assets hosting (Asset Management admin page).

The admin chooses a directory on the ARI server that hosts the APERO
assets tar files.  ``apero_assets.py update-remote`` (in ``ari`` upload
mode) pushes new tar files to this directory through the ARI API using
an admin API token.

Hosted files can be downloaded publicly from ``/apero-assets/<filename>``
(unless the admin disables it) or by any API-token user from
``/api/assets/download/<filename>``.

The configuration is stored in ``{ARI_DIR}/admin/asset_management.yaml``::

    assets_path: /absolute/path/to/hosted/assets
    public_download: true

Created on 2026-10-01

@author: cook
"""

import hashlib
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import IO, Any, Dict, List, Optional

from werkzeug.utils import secure_filename

from apero_ri.core import user_data as ud

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.asset_management"
# permission required for the page and every asset API endpoint
ASSET_PERMISSION = "manage.admin.asset_management"
# page id (and endpoint) admins use to configure the hosting path
ASSET_PAGE_ID = "home.admin_portal.asset_management"
# only these file types may be uploaded / listed / deleted
ALLOWED_SUFFIXES = (".tar.gz", ".tgz", ".tar", ".yaml")
# chunk size used when streaming uploads to disk
_CHUNK_SIZE = 1 << 20
# url prefix of the public (no login) download route
PUBLIC_URL_PREFIX = "/apero-assets/"


# =============================================================================
# Config I/O
# =============================================================================
def _config_path() -> Path:
    """Return the path of the asset management config yaml."""
    # ud.ARI_DIR may be re-pointed at runtime so resolve it on every call
    return ud.ARI_DIR / "admin" / "asset_management.yaml"


def load_config() -> Dict[str, Any]:
    """
    Load the asset management config.

    :return: dict with keys ``assets_path`` (empty string when unset) and
             ``public_download`` (bool, default True)
    """
    data = ud._load_yaml(_config_path(), {})
    if not isinstance(data, dict):
        data = {}
    data["assets_path"] = str(data.get("assets_path") or "").strip()
    data["public_download"] = bool(data.get("public_download", True))
    return data


def set_assets_path(path: str, public_download: bool = True) -> Path:
    """
    Validate, create and persist the assets hosting directory.

    :param path: str, absolute directory path on the ARI server
    :param public_download: bool, allow downloads without logging in

    :raises ValueError: if the path is not absolute or not writable

    :return: Path, the resolved assets directory
    """
    raw = str(path or "").strip()
    if not raw:
        raise ValueError("An assets directory path is required.")
    assets_dir = Path(raw).expanduser()
    if not assets_dir.is_absolute():
        raise ValueError("The assets directory must be an absolute path.")
    try:
        assets_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError(f"Cannot create directory: {exc}") from exc
    if not os.access(assets_dir, os.W_OK):
        raise ValueError(f"Directory is not writable: {assets_dir}")
    cfg = load_config()
    cfg["assets_path"] = str(assets_dir)
    cfg["public_download"] = bool(public_download)
    ud._save_yaml(_config_path(), cfg)
    return assets_dir


def get_assets_dir() -> Optional[Path]:
    """
    Return the configured assets directory, or None if not set up.

    :return: Path or None
    """
    raw = load_config().get("assets_path", "")
    if not raw:
        return None
    assets_dir = Path(raw)
    if not assets_dir.is_dir():
        return None
    return assets_dir


# =============================================================================
# File helpers
# =============================================================================
def validate_filename(filename: str) -> str:
    """
    Check a client-supplied filename is a safe, allowed asset filename.

    :param filename: str, the requested basename

    :raises ValueError: if the name is unsafe or has a disallowed suffix

    :return: str, the validated filename
    """
    name = str(filename or "").strip()
    # secure_filename strips separators/dot-dot; any change means unsafe
    if not name or secure_filename(name) != name:
        raise ValueError(f"Invalid filename: {filename!r}")
    if not name.endswith(ALLOWED_SUFFIXES):
        allowed = ", ".join(ALLOWED_SUFFIXES)
        raise ValueError(f"Filename must end with one of: {allowed}")
    return name


def list_files(assets_dir: Path) -> List[Dict[str, Any]]:
    """
    List the hosted asset files (newest first).

    :param assets_dir: Path, the configured assets directory

    :return: list of dicts with name, size_bytes, modified (iso), age_s
    """
    now = time.time()
    rows = []
    for entry in assets_dir.iterdir():
        if not entry.is_file() or not entry.name.endswith(ALLOWED_SUFFIXES):
            continue
        stat = entry.stat()
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        rows.append(dict(name=entry.name, size_bytes=stat.st_size,
                         modified=modified.isoformat(),
                         age_s=max(0.0, now - stat.st_mtime)))
    rows.sort(key=lambda row: row["age_s"])
    return rows


def delete_file(assets_dir: Path, filename: str) -> bool:
    """
    Delete one hosted asset file from disk.

    :param assets_dir: Path, the configured assets directory
    :param filename: str, basename of the file to delete

    :raises ValueError: if the filename is invalid

    :return: bool, True if the file existed and was removed
    """
    target = assets_dir / validate_filename(filename)
    if not target.is_file():
        return False
    target.unlink()
    return True


def save_stream(assets_dir: Path, filename: str, stream: IO[bytes],
                expected_md5: Optional[str] = None,
                overwrite: bool = False) -> Dict[str, Any]:
    """
    Stream an uploaded file into the assets directory atomically.

    :param assets_dir: Path, the configured assets directory
    :param filename: str, basename to store the file as
    :param stream: binary file-like object (the request body)
    :param expected_md5: str or None, if given the upload must match it
    :param overwrite: bool, if False an existing file is an error

    :raises ValueError: on invalid name, existing file or md5 mismatch

    :return: dict with name, size_bytes and md5 of the stored file
    """
    name = validate_filename(filename)
    target = assets_dir / name
    if target.exists() and not overwrite:
        raise ValueError(f"File already exists: {name}")
    md5 = hashlib.md5()
    size = 0
    # write to a hidden temp file so partial uploads are never listed
    fd, tmp_name = tempfile.mkstemp(dir=assets_dir, prefix=".upload_")
    try:
        with os.fdopen(fd, "wb") as fh:
            for chunk in iter(lambda: stream.read(_CHUNK_SIZE), b""):
                fh.write(chunk)
                md5.update(chunk)
                size += len(chunk)
        digest = md5.hexdigest()
        if expected_md5 and expected_md5.strip().lower() != digest:
            raise ValueError("Checksum mismatch: upload was corrupted.")
        if size == 0:
            raise ValueError("Uploaded file is empty.")
        os.chmod(tmp_name, 0o644)
        os.replace(tmp_name, target)
    except BaseException:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise
    return dict(name=name, size_bytes=size, md5=digest)
