"""Vault data store for the ARI admin portal.

Vault entries are persisted in
``~/.ari/admin/general/vault.yaml``.

Each entry carries a visibility *level* that restricts who can
see it:

* ``super_admin`` – only super-admins.
* ``admin`` – admins and super-admins.
* ``moderator`` – moderators, admins, and super-admins.

Access is enforced through resolved permissions:

* ``manage.instrument.super_admin``
  → grants access to the ``super_admin`` level.
* ``manage.apero_profile``
  → grants access to the ``admin`` level.
* ``manage.admin.vault``
  → grants access to the ``moderator`` level (base).
"""
import uuid as _uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ARI_DIR = Path.home() / ".ari"
_ADMIN_GENERAL_DIR = _ARI_DIR / "admin" / "general"
_VAULT_FILE = _ADMIN_GENERAL_DIR / "vault.yaml"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Ordered from MOST to LEAST privileged.
VAULT_LEVELS: List[str] = [
    "super_admin",
    "admin",
    "moderator",
]

VAULT_LEVEL_LABELS: Dict[str, str] = {
    "super_admin": "Super Admin Only",
    "admin": "Admin & Above",
    "moderator": "Moderator & Above",
}

VAULT_LEVEL_ICONS: Dict[str, str] = {
    "super_admin": "fa-crown",
    "admin": "fa-shield-halved",
    "moderator": "fa-user-shield",
}

# Resolved permission required to access each level.
VAULT_LEVEL_PERM: Dict[str, str] = {
    "super_admin": "manage.instrument.super_admin",
    "admin": "manage.apero_profile",
    "moderator": "manage.admin.vault",
}


# ---------------------------------------------------------------------------
# Raw I/O
# ---------------------------------------------------------------------------
def _load_raw() -> dict:
    if not _VAULT_FILE.exists():
        return {"entries": []}
    try:
        with open(_VAULT_FILE, "r", encoding="utf-8") as fio:
            data = yaml.safe_load(fio) or {}
        if not isinstance(data.get("entries"), list):
            data["entries"] = []
        return data
    except Exception:
        return {"entries": []}


def _save_raw(data: dict) -> None:
    _ADMIN_GENERAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(_VAULT_FILE, "w", encoding="utf-8") as fio:
        yaml.dump(
            data,
            fio,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def load_entries() -> List[dict]:
    """Return all entries including the ``information`` field."""
    return list(_load_raw().get("entries", []))


def get_entry(entry_id: str) -> Optional[dict]:
    """Return a single entry by *id*, or ``None``."""
    for entry in load_entries():
        if entry.get("id") == entry_id:
            return entry
    return None


def save_entry(
    title: str,
    information: str,
    level: str,
    created_by: str,
    entry_id: Optional[str] = None,
) -> dict:
    """Create or update a vault entry.

    :param title: Human-readable title shown on the card.
    :param information: Sensitive body (never shown on the card).
    :param level: Vault visibility level (see :data:`VAULT_LEVELS`).
    :param created_by: Username of the creating user.
    :param entry_id: When given, update the matching entry.
    :returns: The saved entry dict.
    """
    now = datetime.now(timezone.utc).isoformat()
    data = _load_raw()
    entries: List[dict] = data.get("entries", [])

    if entry_id:
        for idx, existing in enumerate(entries):
            if existing.get("id") == entry_id:
                existing["title"] = title
                existing["information"] = information
                existing["level"] = level
                existing["modified_at"] = now
                entries[idx] = existing
                data["entries"] = entries
                _save_raw(data)
                return dict(existing)

    new_entry: dict = {
        "id": str(_uuid.uuid4()),
        "title": title,
        "information": information,
        "level": level,
        "created_by": created_by,
        "created_at": now,
        "modified_at": now,
    }
    entries.append(new_entry)
    data["entries"] = entries
    _save_raw(data)
    return dict(new_entry)


def delete_entry(entry_id: str) -> bool:
    """Delete an entry by *id*.

    :returns: ``True`` if the entry was found and deleted.
    """
    data = _load_raw()
    entries: List[dict] = data.get("entries", [])
    kept = [e for e in entries if e.get("id") != entry_id]
    if len(kept) == len(entries):
        return False
    data["entries"] = kept
    _save_raw(data)
    return True


# ---------------------------------------------------------------------------
# Level helpers
# ---------------------------------------------------------------------------
def accessible_levels(resolved_perms: set) -> List[str]:
    """Return levels the user may view, most privileged first."""
    return [
        lvl for lvl in VAULT_LEVELS
        if VAULT_LEVEL_PERM[lvl] in resolved_perms
    ]


def manageable_levels(resolved_perms: set) -> List[str]:
    """Return levels the user may create / edit / delete in."""
    return accessible_levels(resolved_perms)


def filter_by_level(
    entries: List[dict],
    levels: List[str],
) -> List[dict]:
    """Return only entries whose level is in *levels*."""
    level_set = set(levels)
    return [
        e for e in entries
        if e.get("level", "moderator") in level_set
    ]


def strip_information(entry: dict) -> dict:
    """Return a copy of *entry* without the ``information`` field."""
    result = dict(entry)
    result.pop("information", None)
    return result
