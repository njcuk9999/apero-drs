#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI: User upload management helpers.

Upload directories are configured by the admin and stored in
{ARI_DIR}/admin/uploads_config.yaml.

Each directory entry has:
    id          : unique UUID string
    name        : human-readable label
    path        : absolute directory path on disk
    type        : "per_user"  – uploads stored in {path}/{username}/
                  "global"    – uploads stored directly in {path}/
    quota_gb    : float, per-user quota (per_user) or total cap (global)
    allowed_groups : list of group names allowed to upload

Share tokens are stored per-file in
{ARI_DIR}/admin/uploads_shares.yaml with the structure:
    {token: {dir_id, username, filename, created}}
"""

import os
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from apero_ri.core import user_data as ud

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.upload_data"

_CONFIG_DEFAULT: Dict = {"directories": []}
_SHARES_DEFAULT: Dict = {}

# =============================================================================
# Path helpers
# =============================================================================


def _admin_uploads_config_path() -> Path:
    return ud.ARI_DIR / "admin" / "uploads_config.yaml"


def _shares_path() -> Path:
    return ud.ARI_DIR / "admin" / "uploads_shares.yaml"


# =============================================================================
# Config I/O
# =============================================================================


def load_uploads_config() -> Dict:
    """Load the uploads config (list of directory entries)."""
    data = ud._load_yaml(
        _admin_uploads_config_path(), dict(_CONFIG_DEFAULT)
    )
    if not isinstance(data, dict):
        data = dict(_CONFIG_DEFAULT)
    if not isinstance(data.get("directories"), list):
        data["directories"] = []
    return data


def save_uploads_config(data: Dict) -> None:
    """Persist the uploads config."""
    ud._save_yaml(_admin_uploads_config_path(), data)


def get_all_directories() -> List[Dict]:
    """Return the list of configured upload directory entries."""
    return load_uploads_config().get("directories", [])


def get_directory_by_id(dir_id: str) -> Optional[Dict]:
    """Return a single directory entry by id, or None."""
    for entry in get_all_directories():
        if entry.get("id") == dir_id:
            return entry
    return None


def add_directory(
    name: str,
    path: str,
    dir_type: str,
    quota_gb: float,
    allowed_groups: List[str],
) -> Dict:
    """Create a new directory entry and return it."""
    entry = {
        "id": str(uuid.uuid4()),
        "name": str(name).strip(),
        "path": str(path).strip(),
        "type": dir_type if dir_type in ("per_user", "global") else "per_user",
        "quota_gb": float(quota_gb) if quota_gb else 1.0,
        "allowed_groups": list(allowed_groups),
    }
    cfg = load_uploads_config()
    cfg["directories"].append(entry)
    save_uploads_config(cfg)
    return entry


def edit_directory(
    dir_id: str,
    name: str,
    path: str,
    dir_type: str,
    quota_gb: float,
    allowed_groups: List[str],
) -> Optional[Dict]:
    """Update an existing directory entry. Returns the updated entry or None."""
    cfg = load_uploads_config()
    for entry in cfg["directories"]:
        if entry.get("id") == dir_id:
            entry["name"] = str(name).strip()
            entry["path"] = str(path).strip()
            entry["type"] = (
                dir_type
                if dir_type in ("per_user", "global") else "per_user"
            )
            entry["quota_gb"] = float(quota_gb) if quota_gb else 1.0
            entry["allowed_groups"] = list(allowed_groups)
            save_uploads_config(cfg)
            return entry
    return None


def delete_directory(dir_id: str) -> bool:
    """Remove a directory entry by id. Returns True if found and removed."""
    cfg = load_uploads_config()
    before = len(cfg["directories"])
    cfg["directories"] = [
        d for d in cfg["directories"] if d.get("id") != dir_id
    ]
    if len(cfg["directories"]) < before:
        save_uploads_config(cfg)
        return True
    return False


# =============================================================================
# File path helpers (with traversal prevention)
# =============================================================================


def _user_upload_dir(dir_cfg: Dict, username: str) -> Path:
    """
    Resolve the upload directory for a specific user.
    For per_user type adds a username subdirectory.
    """
    base = Path(dir_cfg["path"]).expanduser().resolve()
    if dir_cfg.get("type") == "per_user":
        # Sanitise username to avoid directory traversal
        safe_user = "".join(
            c for c in username if c.isalnum() or c in ("-", "_", ".")
        )
        return base / safe_user
    return base


def _resolve_safe(upload_dir: Path, filename: str) -> Optional[Path]:
    """
    Return the resolved absolute path for a file inside upload_dir.
    Returns None if the path escapes the upload directory.
    """
    candidate = (upload_dir / filename).resolve()
    try:
        candidate.relative_to(upload_dir.resolve())
    except ValueError:
        return None
    return candidate


# =============================================================================
# File listing and size helpers
# =============================================================================

_GiB = 1024 ** 3


def list_user_files(
    dir_cfg: Dict, username: str
) -> List[Dict]:
    """
    Return a list of file metadata dicts for a user's upload directory.
    Each dict: {filename, size_bytes, modified_iso}
    """
    upload_dir = _user_upload_dir(dir_cfg, username)
    if not upload_dir.is_dir():
        return []
    files = []
    for item in sorted(upload_dir.iterdir()):
        if item.is_file():
            stat = item.stat()
            files.append({
                "filename": item.name,
                "size_bytes": stat.st_size,
                "modified_iso": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(),
            })
    return files


def get_user_quota_used_bytes(dir_cfg: Dict, username: str) -> int:
    """Return total bytes used by a user in a per_user directory."""
    upload_dir = _user_upload_dir(dir_cfg, username)
    if not upload_dir.is_dir():
        return 0
    total = 0
    for item in upload_dir.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return total


def get_dir_quota_used_bytes(dir_cfg: Dict) -> int:
    """Return total bytes used in a global directory."""
    base = Path(dir_cfg["path"]).expanduser().resolve()
    if not base.is_dir():
        return 0
    total = 0
    for item in base.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return total


def quota_used_bytes(dir_cfg: Dict, username: str) -> int:
    """Convenience: returns bytes used by the user (or dir for global)."""
    if dir_cfg.get("type") == "per_user":
        return get_user_quota_used_bytes(dir_cfg, username)
    return get_dir_quota_used_bytes(dir_cfg)


# =============================================================================
# Upload / delete
# =============================================================================


def store_file(
    dir_cfg: Dict, username: str, filename: str, file_obj: Any
) -> Tuple[bool, str]:
    """
    Write `file_obj` (a file-like object) to the upload directory.
    Returns (success, error_message).  Quota is checked before writing.
    """
    upload_dir = _user_upload_dir(dir_cfg, username)
    target = _resolve_safe(upload_dir, filename)
    if target is None:
        return False, "Invalid filename (path traversal detected)"

    # Read content first to check size
    content = file_obj.read()
    file_size = len(content)

    quota_bytes = int(dir_cfg.get("quota_gb", 1.0) * _GiB)
    used = quota_used_bytes(dir_cfg, username)
    if used + file_size > quota_bytes:
        return False, "Quota exceeded"

    upload_dir.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as f:
        f.write(content)
    return True, ""


def delete_file(
    dir_cfg: Dict, username: str, filename: str
) -> Tuple[bool, str]:
    """
    Delete a file from the user's upload directory.
    Returns (success, error_message).
    """
    upload_dir = _user_upload_dir(dir_cfg, username)
    target = _resolve_safe(upload_dir, filename)
    if target is None:
        return False, "Invalid filename"
    if not target.is_file():
        return False, "File not found"
    try:
        target.unlink()
    except OSError as exc:
        return False, str(exc)
    return True, ""


# =============================================================================
# Share tokens
# =============================================================================


def _load_shares() -> Dict:
    data = ud._load_yaml(_shares_path(), dict(_SHARES_DEFAULT))
    return data if isinstance(data, dict) else {}


def _save_shares(shares: Dict) -> None:
    ud._save_yaml(_shares_path(), shares)


def create_share_token(
    dir_id: str, username: str, filename: str
) -> str:
    """
    Create (or return existing) a share token for a file.
    Returns the token string.
    """
    shares = _load_shares()
    # Return existing token if already shared
    for token, info in shares.items():
        if (
            info.get("dir_id") == dir_id
            and info.get("username") == username
            and info.get("filename") == filename
        ):
            return token
    token = secrets.token_urlsafe(32)
    shares[token] = {
        "dir_id": dir_id,
        "username": username,
        "filename": filename,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    _save_shares(shares)
    return token


def resolve_share_token(
    token: str,
) -> Optional[Tuple[Dict, str, str]]:
    """
    Resolve a share token.
    Returns (dir_cfg, username, filename) or None if invalid.
    """
    shares = _load_shares()
    info = shares.get(token)
    if not info:
        return None
    dir_cfg = get_directory_by_id(info.get("dir_id", ""))
    if not dir_cfg:
        return None
    return dir_cfg, info.get("username", ""), info.get("filename", "")


def delete_share_token(
    dir_id: str, username: str, filename: str
) -> None:
    """Remove any share token for a file."""
    shares = _load_shares()
    to_remove = [
        t for t, info in shares.items()
        if (
            info.get("dir_id") == dir_id
            and info.get("username") == username
            and info.get("filename") == filename
        )
    ]
    for t in to_remove:
        del shares[t]
    if to_remove:
        _save_shares(shares)


# =============================================================================
# Quota info helpers
# =============================================================================


def get_quota_info_for_user(
    dir_cfg: Dict, username: str
) -> Dict:
    """
    Return quota summary for a user in a directory.
    {used_bytes, quota_bytes, used_gb, quota_gb, pct}
    """
    quota_bytes = int(dir_cfg.get("quota_gb", 1.0) * _GiB)
    used = quota_used_bytes(dir_cfg, username)
    pct = round(used / quota_bytes * 100, 1) if quota_bytes else 0.0
    return {
        "used_bytes": used,
        "quota_bytes": quota_bytes,
        "used_gb": round(used / _GiB, 3),
        "quota_gb": dir_cfg.get("quota_gb", 1.0),
        "pct": pct,
    }


def get_all_users_quota(dir_cfg: Dict) -> List[Dict]:
    """
    For per_user directories: return quota info for each sub-directory.
    For global: return a single entry for the whole directory.
    """
    results = []
    if dir_cfg.get("type") == "per_user":
        base = Path(dir_cfg["path"]).expanduser().resolve()
        if base.is_dir():
            for subdir in sorted(base.iterdir()):
                if subdir.is_dir():
                    username = subdir.name
                    info = get_quota_info_for_user(dir_cfg, username)
                    info["username"] = username
                    results.append(info)
    else:
        used = get_dir_quota_used_bytes(dir_cfg)
        quota_bytes = int(dir_cfg.get("quota_gb", 1.0) * _GiB)
        results.append({
            "username": "(global)",
            "used_bytes": used,
            "quota_bytes": quota_bytes,
            "used_gb": round(used / _GiB, 3),
            "quota_gb": dir_cfg.get("quota_gb", 1.0),
            "pct": round(
                used / quota_bytes * 100, 1
            ) if quota_bytes else 0.0,
        })
    return results
