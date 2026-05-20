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


# ---------------------------------------------------------------------------
# Export / Import with passphrase encryption
# ---------------------------------------------------------------------------
_PBKDF2_ITERS = 480_000


def _derive_fernet_key(
    passphrase: str, salt: bytes
) -> bytes:
    """Derive a Fernet-compatible key via PBKDF2-HMAC-SHA256.

    :returns: 44-byte URL-safe base-64 encoded key suitable for
        ``cryptography.fernet.Fernet``.
    """
    import base64 as _b64
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import (
        PBKDF2HMAC,
    )

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_PBKDF2_ITERS,
    )
    return _b64.urlsafe_b64encode(
        kdf.derive(passphrase.encode("utf-8"))
    )


def export_vault_yaml(
    entries: List[dict],
    passphrase: str,
) -> bytes:
    """Encrypt vault entry information and return YAML bytes.

    Each entry's ``information`` field is encrypted with Fernet
    using a key derived from *passphrase* and a random 16-byte
    salt embedded in the file header.

    :param entries: Plain-text vault entries (from
        :func:`load_entries`).
    :param passphrase: User-supplied passphrase.
    :returns: UTF-8 encoded YAML suitable for writing to a file.
    """
    import base64 as _b64
    import os as _os
    from cryptography.fernet import Fernet

    salt = _os.urandom(16)
    fernet_key = _derive_fernet_key(passphrase, salt)
    fnet = Fernet(fernet_key)

    export_entries = []
    for entry in entries:
        info = entry.get("information", "") or ""
        enc_token = fnet.encrypt(
            info.encode("utf-8")
        ).decode("ascii")
        export_entries.append({
            "id": entry.get("id", ""),
            "title": entry.get("title", ""),
            "level": entry.get("level", "moderator"),
            "created_by": entry.get("created_by", ""),
            "created_at": entry.get("created_at", ""),
            "modified_at": entry.get("modified_at", ""),
            "information_enc": enc_token,
        })

    payload = {
        "vault_export": {
            "version": 1,
            "exported_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "salt": _b64.b64encode(salt).decode("ascii"),
            "entries": export_entries,
        }
    }
    return yaml.dump(
        payload,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).encode("utf-8")


def import_vault_yaml(
    yaml_bytes: bytes,
    passphrase: str,
) -> List[dict]:
    """Decrypt an export YAML file and return plaintext entries.

    :param yaml_bytes: Raw bytes of the export YAML file.
    :param passphrase: Passphrase used during export.
    :returns: List of entry dicts with plaintext
        ``information`` fields.
    :raises ValueError: On wrong passphrase or malformed file.
    """
    import base64 as _b64
    from cryptography.fernet import Fernet, InvalidToken

    raw = (
        yaml.safe_load(
            yaml_bytes.decode("utf-8", errors="replace")
        )
        or {}
    )
    export = raw.get("vault_export")
    if not isinstance(export, dict):
        raise ValueError("Not a valid vault export file.")
    version = export.get("version", 0)
    if version != 1:
        raise ValueError(
            f"Unsupported export version: {version}"
        )
    salt_b64 = export.get("salt", "")
    if not salt_b64:
        raise ValueError("Missing salt in export file.")
    try:
        salt = _b64.b64decode(salt_b64)
    except Exception:
        raise ValueError("Corrupt salt in export file.")

    fernet_key = _derive_fernet_key(passphrase, salt)
    fnet = Fernet(fernet_key)

    results: List[dict] = []
    for raw_entry in export.get("entries", []):
        enc = str(raw_entry.get("information_enc", ""))
        try:
            info = fnet.decrypt(
                enc.encode("ascii")
            ).decode("utf-8")
        except InvalidToken:
            raise ValueError(
                "Wrong passphrase or corrupted file."
            )
        results.append({
            "id": raw_entry.get("id", ""),
            "title": raw_entry.get("title", ""),
            "level": raw_entry.get("level", "moderator"),
            "created_by": raw_entry.get("created_by", ""),
            "created_at": raw_entry.get(
                "created_at", ""
            ),
            "modified_at": raw_entry.get(
                "modified_at", ""
            ),
            "information": info,
        })
    return results
