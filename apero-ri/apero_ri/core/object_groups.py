#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Per-profile shared object group storage.

Object groups let users organise targets into named collections
that are visible to everyone with access to the profile.

    ~/.ari/shared/{profile_id}/object_groups.yaml

Structure
---------
::

    groups:
      - name: <str>
        created_by: <str>
        created_at: <iso8601>
        objects:
          - objname: <str>
            added_by: <str>
            added_at: <iso8601>
"""
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ================================================================
# Module name
# ================================================================
__NAME__ = 'apero_ri.core.object_groups'

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


def _groups_path(profile_id: str) -> Path:
    return _shared_dir(profile_id) / 'object_groups.yaml'


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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ================================================================
# Internal helpers
# ================================================================
def _load_groups_data(profile_id: str) -> dict:
    path = _groups_path(profile_id)
    data = _load_yaml(path, {'groups': []})
    if not isinstance(data, dict):
        data = {'groups': []}
    if not isinstance(data.get('groups'), list):
        data['groups'] = []
    return data


def _save_groups_data(profile_id: str, data: dict) -> None:
    _save_yaml(_groups_path(profile_id), data)


def _find_group(
    groups: List[dict], name: str
) -> Optional[dict]:
    """Find a group dict by name (case-sensitive)."""
    for g in groups:
        if g.get('name') == name:
            return g
    return None


# ================================================================
# Public API — group CRUD
# ================================================================
def list_groups(profile_id: str) -> List[dict]:
    """Return all groups for a profile."""
    data = _load_groups_data(profile_id)
    return data['groups']


def create_group(
    profile_id: str, name: str, username: str
) -> Optional[dict]:
    """Create a new named group. Returns it or None if exists."""
    data = _load_groups_data(profile_id)
    groups = data['groups']
    if _find_group(groups, name) is not None:
        return None
    entry = dict()
    entry['name'] = name
    entry['created_by'] = username
    entry['created_at'] = _now_iso()
    entry['objects'] = []
    groups.append(entry)
    _save_groups_data(profile_id, data)
    return entry


def delete_group(profile_id: str, name: str) -> bool:
    """Delete a group by name. Returns True if found."""
    data = _load_groups_data(profile_id)
    groups = data['groups']
    original_len = len(groups)
    data['groups'] = [
        g for g in groups if g.get('name') != name
    ]
    if len(data['groups']) == original_len:
        return False
    _save_groups_data(profile_id, data)
    return True


def rename_group(
    profile_id: str, old_name: str, new_name: str
) -> bool:
    """Rename a group. Returns True on success."""
    data = _load_groups_data(profile_id)
    groups = data['groups']
    if _find_group(groups, new_name) is not None:
        return False
    group = _find_group(groups, old_name)
    if group is None:
        return False
    group['name'] = new_name
    _save_groups_data(profile_id, data)
    return True


# ================================================================
# Public API — object membership
# ================================================================
def get_groups_for_object(
    profile_id: str, objname: str
) -> List[str]:
    """Return group names that contain *objname*."""
    groups = list_groups(profile_id)
    result = []
    for g in groups:
        objs = g.get('objects', [])
        names = [
            o.get('objname', '') for o in objs
            if isinstance(o, dict)
        ]
        if objname in names:
            result.append(g['name'])
    return result


def add_object_to_group(
    profile_id: str, group_name: str,
    objname: str, username: str
) -> Optional[str]:
    """Add an object to a group.

    Returns None on success, or an error string.
    """
    data = _load_groups_data(profile_id)
    group = _find_group(data['groups'], group_name)
    if group is None:
        return 'Group not found'
    objs = group.setdefault('objects', [])
    existing = [
        o.get('objname', '') for o in objs
        if isinstance(o, dict)
    ]
    if objname in existing:
        return 'Object already in group'
    entry = dict()
    entry['objname'] = objname
    entry['added_by'] = username
    entry['added_at'] = _now_iso()
    objs.append(entry)
    _save_groups_data(profile_id, data)
    return None


def add_objects_bulk(
    profile_id: str, group_name: str,
    objnames: List[str], username: str
) -> dict:
    """Add multiple objects to a group.

    Returns dict with keys 'added', 'already_exists',
    'not_found' (group missing → all become not_found).
    """
    data = _load_groups_data(profile_id)
    group = _find_group(data['groups'], group_name)
    result = dict()
    result['added'] = []
    result['already_exists'] = []
    if group is None:
        result['not_found'] = list(objnames)
        return result
    result['not_found'] = []
    objs = group.setdefault('objects', [])
    existing = set(
        o.get('objname', '') for o in objs
        if isinstance(o, dict)
    )
    for objname in objnames:
        objname = str(objname).strip()
        if not objname:
            continue
        if objname in existing:
            result['already_exists'].append(objname)
        else:
            entry = dict()
            entry['objname'] = objname
            entry['added_by'] = username
            entry['added_at'] = _now_iso()
            objs.append(entry)
            existing.add(objname)
            result['added'].append(objname)
    _save_groups_data(profile_id, data)
    return result


def remove_object_from_group(
    profile_id: str, group_name: str, objname: str
) -> bool:
    """Remove an object from a group. Returns True if found."""
    data = _load_groups_data(profile_id)
    group = _find_group(data['groups'], group_name)
    if group is None:
        return False
    objs = group.get('objects', [])
    original_len = len(objs)
    group['objects'] = [
        o for o in objs
        if not (isinstance(o, dict)
                and o.get('objname') == objname)
    ]
    if len(group['objects']) == original_len:
        return False
    _save_groups_data(profile_id, data)
    return True
