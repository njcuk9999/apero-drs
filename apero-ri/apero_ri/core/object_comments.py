#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Per-profile shared object comment storage.

Comments are stored per apero profile, shared across all users:

    ~/.ari/shared/{profile_id}/object_comments.yaml

Structure
---------
::

    {OBJNAME}:
      - id: <uuid>
        username: <str>
        comment: <str>
        created_at: <iso8601>
        updated_at: <iso8601>
"""
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ================================================================
# Module name
# ================================================================
__NAME__ = 'apero_ri.core.object_comments'

# ================================================================
# Paths
# ================================================================
_ARI_DIR: Optional[Path] = None


def _ari_dir() -> Path:
    if _ARI_DIR is not None:
        return _ARI_DIR
    return Path.home() / '.ari'


def set_ari_dir(path: Optional[str]) -> None:
    """Allow overriding the base ARI directory."""
    global _ARI_DIR
    if path:
        _ARI_DIR = Path(path).expanduser()
    else:
        _ARI_DIR = None


def _shared_dir(profile_id: str) -> Path:
    d = _ari_dir() / 'shared' / profile_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _comments_path(profile_id: str) -> Path:
    return _shared_dir(profile_id) / 'object_comments.yaml'


# ================================================================
# YAML helpers
# ================================================================
def _load_yaml(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data if data is not None else default
    except Exception:
        return default


def _save_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(
            data, f, default_flow_style=False,
            allow_unicode=True,
        )


def _new_id() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ================================================================
# Public API
# ================================================================
def load_comments(profile_id: str) -> Dict[str, List[dict]]:
    """Load all object comments for a profile."""
    path = _comments_path(profile_id)
    data = _load_yaml(path, {})
    if not isinstance(data, dict):
        return {}
    return data


def save_comments(
    profile_id: str, data: Dict[str, List[dict]]
) -> None:
    """Save all object comments for a profile."""
    _save_yaml(_comments_path(profile_id), data)


def list_comments(
    profile_id: str, objname: str
) -> List[dict]:
    """Return comments for a specific object, newest first."""
    all_comments = load_comments(profile_id)
    items = all_comments.get(objname, [])
    if not isinstance(items, list):
        items = []
    items.sort(
        key=lambda c: c.get('created_at', ''),
        reverse=True,
    )
    return items


def add_comment(
    profile_id: str, objname: str,
    username: str, comment: str
) -> dict:
    """Add a comment and return the new comment dict."""
    all_comments = load_comments(profile_id)
    items = all_comments.setdefault(objname, [])
    entry = dict()
    entry['id'] = _new_id()
    entry['username'] = username
    entry['comment'] = comment
    entry['created_at'] = _now_iso()
    entry['updated_at'] = entry['created_at']
    items.append(entry)
    save_comments(profile_id, all_comments)
    return entry


def edit_comment(
    profile_id: str, objname: str,
    comment_id: str, new_text: str
) -> Optional[dict]:
    """Edit a comment's text. Returns updated comment or None."""
    all_comments = load_comments(profile_id)
    items = all_comments.get(objname, [])
    for item in items:
        if item.get('id') == comment_id:
            item['comment'] = new_text
            item['updated_at'] = _now_iso()
            save_comments(profile_id, all_comments)
            return item
    return None


def delete_comment(
    profile_id: str, objname: str, comment_id: str
) -> bool:
    """Delete a comment by ID. Returns True if found."""
    all_comments = load_comments(profile_id)
    items = all_comments.get(objname, [])
    original_len = len(items)
    items = [
        c for c in items if c.get('id') != comment_id
    ]
    if len(items) == original_len:
        return False
    all_comments[objname] = items
    save_comments(profile_id, all_comments)
    return True


def get_comment_by_id(
    profile_id: str, objname: str, comment_id: str
) -> Optional[dict]:
    """Look up a single comment by its ID."""
    all_comments = load_comments(profile_id)
    items = all_comments.get(objname, [])
    for item in items:
        if item.get('id') == comment_id:
            return item
    return None
