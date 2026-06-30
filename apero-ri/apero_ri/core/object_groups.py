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
    tmp_path = path.with_name(
        '{0}.{1}.tmp'.format(path.name, uuid.uuid4().hex)
    )
    with open(tmp_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    tmp_path.replace(path)


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


def get_group(
    profile_id: str,
    name: str,
) -> Optional[dict]:
    """Return one group for a profile or None when missing."""
    data = _load_groups_data(profile_id)
    return _find_group(data['groups'], name)


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


def get_summary_columns(
    profile_id: str,
    group_name: str,
) -> List[str]:
    """Return persisted summary-table column IDs for a group."""
    group = get_group(profile_id, group_name)
    if not isinstance(group, dict):
        return []
    columns = group.get('summary_columns', [])
    if not isinstance(columns, list):
        return []
    result = []
    seen = set()
    for column in columns:
        text = str(column).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def set_summary_columns(
    profile_id: str,
    group_name: str,
    columns: List[str],
) -> bool:
    """Persist summary-table column IDs for a group."""
    data = _load_groups_data(profile_id)
    group = _find_group(data['groups'], group_name)
    if group is None:
        return False

    clean = []
    seen = set()
    for column in columns:
        text = str(column).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        clean.append(text)

    group['summary_columns'] = clean
    _save_groups_data(profile_id, data)
    return True


def get_summary_aliases(
    profile_id: str,
    group_name: str,
) -> Dict[str, str]:
    """Return persisted summary-table aliases keyed by property ID."""
    group = get_group(profile_id, group_name)
    if not isinstance(group, dict):
        return dict()
    aliases = group.get('summary_aliases', dict())
    if not isinstance(aliases, dict):
        return dict()
    clean = dict()
    for key, value in aliases.items():
        pkey = str(key).strip()
        pval = str(value).strip()
        if pkey and pval:
            clean[pkey] = pval
    return clean


def set_summary_aliases(
    profile_id: str,
    group_name: str,
    aliases: Dict[str, str],
) -> bool:
    """Persist summary-table aliases keyed by property ID."""
    data = _load_groups_data(profile_id)
    group = _find_group(data['groups'], group_name)
    if group is None:
        return False

    clean = dict()
    if isinstance(aliases, dict):
        for key, value in aliases.items():
            pkey = str(key).strip()
            pval = str(value).strip()
            if pkey and pval:
                clean[pkey] = pval

    group['summary_aliases'] = clean
    _save_groups_data(profile_id, data)
    return True


def get_summary_custom_columns(
    profile_id: str,
    group_name: str,
) -> List[dict]:
    """Return persisted custom summary columns for a group."""
    group = get_group(profile_id, group_name)
    if not isinstance(group, dict):
        return []
    rows = group.get('summary_custom_columns', [])
    if not isinstance(rows, list):
        return []
    clean = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get('name', '')).strip()
        expr = str(row.get('expression', '')).strip()
        vars_map = row.get('variables', dict())
        if not name or not expr:
            continue
        if not isinstance(vars_map, dict):
            continue
        vars_clean = dict()
        for key, value in vars_map.items():
            vkey = str(key).strip().lower()
            vval = str(value).strip()
            if len(vkey) == 1 and vkey.isalpha() and vval:
                vars_clean[vkey] = vval
        if not vars_clean:
            continue
        entry = dict()
        entry['name'] = name
        entry['expression'] = expr
        entry['variables'] = vars_clean
        clean.append(entry)
    return clean


def set_summary_custom_columns(
    profile_id: str,
    group_name: str,
    custom_columns: List[dict],
) -> bool:
    """Persist custom summary columns for a group."""
    data = _load_groups_data(profile_id)
    group = _find_group(data['groups'], group_name)
    if group is None:
        return False

    clean = []
    seen = set()
    if isinstance(custom_columns, list):
        for row in custom_columns:
            if not isinstance(row, dict):
                continue
            name = str(row.get('name', '')).strip()
            expr = str(row.get('expression', '')).strip()
            vars_map = row.get('variables', dict())
            if not name or not expr:
                continue
            name_key = name.lower()
            if name_key in seen:
                continue
            if not isinstance(vars_map, dict):
                continue
            vars_clean = dict()
            for key, value in vars_map.items():
                vkey = str(key).strip().lower()
                vval = str(value).strip()
                if len(vkey) == 1 and vkey.isalpha() and vval:
                    vars_clean[vkey] = vval
            if not vars_clean:
                continue
            entry = dict()
            entry['name'] = name
            entry['expression'] = expr
            entry['variables'] = vars_clean
            clean.append(entry)
            seen.add(name_key)

    group['summary_custom_columns'] = clean
    _save_groups_data(profile_id, data)
    return True
