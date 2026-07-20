#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Authentication and user management.

Manages user accounts stored in ~/.ari/admin/general/users.yaml,
password hashing via the cryptography package, and Flask session login.
"""

import base64
import binascii
import os
import socket
import threading
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml
from apero_ri.core.log import get_logger
from apero_ri.core import user_data as ud
from apero_ri.core.permissions import (
    load_groups,
    load_pages,
    resolve_user_permissions,
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

log = get_logger(__name__)

# =============================================================================
# Define variables
# =============================================================================
ARI_DIR = Path.home() / ".ari"
ADMIN_DIR = ARI_DIR / "admin"
ADMIN_GENERAL_DIR = ADMIN_DIR / "general"
USERS_FILE = ADMIN_GENERAL_DIR / "users.yaml"
SCI_GROUPS_DIR = ADMIN_DIR / "science_groups"
ADMIN_HEALTH_DIR = ADMIN_DIR / "health"
ADMIN_HEALTH_CONFIG_FILE = ADMIN_HEALTH_DIR / "health_status.yaml"

# PBKDF2 parameters
HASH_ALGORITHM = hashes.SHA256()
HASH_ITERATIONS = 600_000
HASH_KEY_LENGTH = 32
SALT_LENGTH = 16

# ---------------------------------------------------------------------------
# In-process mtime-gated cache for apero_profiles.yaml.
# The file is large (~138 KB) and yaml.safe_load takes ~250 ms.
# We re-read only when the file's mtime changes, so admin UI saves take
# effect immediately while normal page loads never touch the disk.
# ---------------------------------------------------------------------------
_profiles_cache: dict = {}  # key -> {'mtime': float, 'data': ...}
_profiles_lock = threading.Lock()
# One-time guard: ensure_ari_directory() does 5 mkdir calls on /mnt/h which
# are slow on WSL/NTFS even when the dirs already exist.  After the first
# successful call per process lifetime we skip it on every subsequent request.
_ari_dir_ensured: bool = False

# Default admin account — username is fixed; password is generated on first run.
DEFAULT_USER = "admin"
DEFAULT_GROUPS = ["super_admin"]


def user_is_super_admin(groups: Optional[List[str]]) -> bool:
    """Return True if group list includes super_admin."""
    return "super_admin" in set(groups or [])


def user_has_admin_privileges(groups: Optional[List[str]]) -> bool:
    """Return True if group list includes admin-level privileges."""
    gset = set(groups or [])
    return ("admin" in gset) or ("super_admin" in gset)


def set_ari_dir(path: Optional[str]) -> None:
    """Configure storage root for auth-managed files."""
    global ARI_DIR, ADMIN_DIR, ADMIN_GENERAL_DIR, USERS_FILE, SCI_GROUPS_DIR
    global APERO_PROFILES_FILE, DB_ACCESS_FILE, DB_TUNNELS_FILE
    global ASYNC_TASKS_FILE
    global ADMIN_HEALTH_DIR, ADMIN_HEALTH_CONFIG_FILE
    base = Path(path).expanduser() if path else (Path.home() / ".ari")
    ARI_DIR = base
    ADMIN_DIR = ARI_DIR / "admin"
    ADMIN_GENERAL_DIR = ADMIN_DIR / "general"
    USERS_FILE = ADMIN_GENERAL_DIR / "users.yaml"
    SCI_GROUPS_DIR = ADMIN_DIR / "science_groups"
    APERO_PROFILES_FILE = ADMIN_GENERAL_DIR / "apero_profiles.yaml"
    DB_ACCESS_FILE = ADMIN_GENERAL_DIR / "db_access.yaml"
    DB_TUNNELS_FILE = ADMIN_GENERAL_DIR / "db_tunnels.yaml"
    ASYNC_TASKS_FILE = ADMIN_DIR / "async_tasks" / "async_tasks.yaml"
    ADMIN_HEALTH_DIR = ADMIN_DIR / "health"
    ADMIN_HEALTH_CONFIG_FILE = ADMIN_HEALTH_DIR / "health_status.yaml"


# =============================================================================
# Password hashing
# =============================================================================
def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 via the cryptography package.

    Returns a string: base64(salt):base64(derived_key)
    """
    if salt is None:
        salt = os.urandom(SALT_LENGTH)
    kdf = PBKDF2HMAC(
        algorithm=HASH_ALGORITHM,
        length=HASH_KEY_LENGTH,
        salt=salt,
        iterations=HASH_ITERATIONS,
    )
    key = kdf.derive(password.encode("utf-8"))
    salt_b64 = base64.b64encode(salt).decode("ascii")
    key_b64 = base64.b64encode(key).decode("ascii")
    return f"{salt_b64}:{key_b64}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt_b64, key_b64 = stored_hash.split(":")
        salt = base64.b64decode(salt_b64)
        stored_key = base64.b64decode(key_b64)
    except (ValueError, binascii.Error):
        return False

    kdf = PBKDF2HMAC(
        algorithm=HASH_ALGORITHM,
        length=HASH_KEY_LENGTH,
        salt=salt,
        iterations=HASH_ITERATIONS,
    )
    try:
        kdf.verify(password.encode("utf-8"), stored_key)
        return True
    except Exception:  # cryptography raises InvalidKey (not public API) on mismatch
        return False


# =============================================================================
# User management
# =============================================================================
def ensure_ari_directory() -> None:
    """Create the ~/.ari/admin directory if it doesn't exist.

    On WSL/NTFS mounts every mkdir syscall is slow even with exist_ok=True.
    We use a module-level flag so the work only happens once per process.
    """
    global _ari_dir_ensured
    if _ari_dir_ensured:
        return
    ADMIN_DIR.mkdir(parents=True, exist_ok=True)
    ADMIN_GENERAL_DIR.mkdir(parents=True, exist_ok=True)
    SCI_GROUPS_DIR.mkdir(parents=True, exist_ok=True)
    ASYNC_TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADMIN_HEALTH_DIR.mkdir(parents=True, exist_ok=True)
    _ari_dir_ensured = True


def load_users() -> Dict[str, dict]:
    """Load users from users.yaml."""
    ensure_ari_directory()
    legacy_file = ADMIN_DIR / "users.yaml"
    if not USERS_FILE.exists() and legacy_file.exists():
        try:
            USERS_FILE.write_bytes(legacy_file.read_bytes())
        except OSError as exc:
            log.warning("Could not migrate legacy users file: %s", exc)
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_users(users: Dict[str, dict]) -> None:
    """Save users to users.yaml."""
    ensure_ari_directory()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(users, f, default_flow_style=False)


def create_user(username: str, password: str, groups: List[str]) -> None:
    """Create a new user or update an existing one."""
    users = load_users()
    users[username] = {
        "password": hash_password(password),
        "groups": groups,
    }
    save_users(users)


def ensure_default_user() -> None:
    """Ensure at least one admin user exists.

    If no admin account is found a new 'admin' account is created with a
    randomly generated password.  The credentials are printed to stdout once
    so the operator can log in and change them immediately.
    """
    import secrets as _secrets
    import string as _string

    users = load_users()
    for user_data in users.values():
        if isinstance(user_data, dict) and user_has_admin_privileges(
            user_data.get("groups", [])
        ):
            return

    # No admin found — generate a secure random password and create the account.
    alphabet = _string.ascii_letters + _string.digits + "!@#$%^&*"
    password = "".join(_secrets.choice(alphabet) for _ in range(20))
    create_user(DEFAULT_USER, password, DEFAULT_GROUPS)

    border = "=" * 60
    print(border, flush=True)
    print("  APERO RI — first-run admin account created", flush=True)
    print(f"  Username : {DEFAULT_USER}", flush=True)
    print(f"  Password : {password}", flush=True)
    print("  Change this password immediately after first login.", flush=True)
    print(border, flush=True)


def find_username_by_email(email: str) -> Optional[str]:
    """Return the username whose emails list contains *email* (case-insensitive).

    Returns None if no match found.
    """
    needle = email.lower().strip()
    if not needle:
        return None
    users = load_users()
    for uname, udata in users.items():
        stored = udata.get('emails') or []
        if isinstance(stored, str):
            stored = [stored]
        for addr in stored:
            if str(addr).lower().strip() == needle:
                return uname
    return None


def authenticate(username: str, password: str) -> Optional[dict]:
    """Authenticate a user.

    *username* may be either a username or any registered email address.
    Returns user dict on success, None on failure.
    """
    users = load_users()
    # Allow login with an email address
    if username not in users:
        matched = find_username_by_email(username)
        if matched is None:
            return None
        username = matched
    user = users[username]
    if not verify_password(password, user.get("password", "")):
        return None
    # Record previous last_login before updating
    prev_login = user.get("last_login")
    # Update last_login timestamp
    user["last_login"] = datetime.now(timezone.utc).isoformat()
    save_users(users)
    return {
        "username": username,
        "groups": user.get("groups", []),
        "last_login": prev_login,
    }


def get_user_info(username: str) -> Optional[dict]:
    """Get user info by username."""
    users = load_users()
    if username not in users:
        return None
    user = users[username]
    return {
        "username": username,
        "first_names": user.get("first_names", ""),
        "groups": user.get("groups", []),
        "instruments": user.get("instruments", []),
        "last_login": user.get("last_login"),
    }


def search_users(query: str) -> List[dict]:
    """Search users by username substring (case-insensitive, min 3 chars)."""
    if len(query) < 3:
        return []
    users = load_users()
    query_lower = query.lower()
    results = []
    for username, data in users.items():
        if query_lower in username.lower():
            results.append(
                {
                    "username": username,
                    "groups": data.get("groups", []),
                    "instruments": data.get("instruments", []),
                    "first_names": data.get("first_names", ""),
                    "last_name": data.get("last_name", ""),
                }
            )
    return results


def list_all_users() -> List[dict]:
    """Return all users as a list of dicts."""
    users = load_users()
    return [
        {
            "username": username,
            "groups": data.get("groups", []),
            "instruments": data.get("instruments", []),
            "first_names": data.get("first_names", ""),
            "last_name": data.get("last_name", ""),
        }
        for username, data in users.items()
    ]


def update_user_groups(username: str, groups: List[str]) -> bool:
    """Update a user's groups list. Returns True on success."""
    users = load_users()
    if username not in users:
        return False
    users[username]["groups"] = groups
    save_users(users)
    return True


def update_user_instruments(username: str, instruments: List[str]) -> bool:
    """Update a user's instruments list. Returns True on success."""
    users = load_users()
    if username not in users:
        return False
    users[username]["instruments"] = instruments
    save_users(users)
    return True


def delete_user(username: str) -> bool:
    """Delete a user. Returns True on success."""
    users = load_users()
    if username not in users:
        return False
    del users[username]
    save_users(users)
    return True


def get_effective_user(session: dict) -> Optional[dict]:
    """Get the effective user, considering login-as functionality.

    The session may have:
      - 'user': the actually logged-in username
      - 'login_as': the username being impersonated

    Returns user info for the effective (impersonated or real) user.
    """
    real_user = session.get("user")
    if real_user is None:
        return None

    login_as_user = session.get("login_as")
    if login_as_user:
        # Verify the real user has permission to login as this user's group
        real_info = get_user_info(real_user)
        target_info = get_user_info(login_as_user)
        if real_info and target_info:
            groups = load_groups()
            real_perms = resolve_user_permissions(real_info["groups"], groups)
            # Check if real user can login_as any of target's groups
            for target_group in target_info["groups"]:
                if f"login_as.{target_group}" in real_perms:
                    return target_info
        # If impersonation not allowed, fall back to real user
        session.pop("login_as", None)

    return get_user_info(real_user)


def get_public_permissions() -> Set[str]:
    """Get permissions for unauthenticated (public) users."""
    groups = load_groups()
    return resolve_user_permissions(["public"], groups)


# =============================================================================
# APERO profile management
# =============================================================================
APERO_PROFILES_FILE = ADMIN_GENERAL_DIR / "apero_profiles.yaml"
DB_ACCESS_FILE = ADMIN_GENERAL_DIR / "db_access.yaml"
DB_TUNNELS_FILE = ADMIN_GENERAL_DIR / "db_tunnels.yaml"


# =============================================================================
# Async tasks configuration
# =============================================================================
ASYNC_TASKS_FILE = ADMIN_DIR / "async_tasks" / "async_tasks.yaml"

# =============================================================================
# Admin health status configuration
# =============================================================================
_ALLOWED_HEALTH_REFRESH = {"manual", "5m", "15m", "1h"}


def load_admin_health_config() -> dict:
    """Load admin health-status settings from health_status.yaml."""
    ensure_ari_directory()
    legacy_file = ADMIN_DIR / "health_status.yaml"
    if not ADMIN_HEALTH_CONFIG_FILE.exists() and legacy_file.exists():
        try:
            ADMIN_HEALTH_CONFIG_FILE.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass
    if not ADMIN_HEALTH_CONFIG_FILE.exists():
        default = {"refresh_frequency": "manual"}
        with open(ADMIN_HEALTH_CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(default, f, default_flow_style=False)
        return default

    with open(ADMIN_HEALTH_CONFIG_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        data = {}

    freq = str(data.get("refresh_frequency", "manual")).strip().lower()
    if freq not in _ALLOWED_HEALTH_REFRESH:
        freq = "manual"
    return {"refresh_frequency": freq}


def save_admin_health_config(config: dict) -> None:
    """Save admin health-status settings to health_status.yaml."""
    ensure_ari_directory()
    freq = str(config.get("refresh_frequency", "manual")).strip().lower()
    if freq not in _ALLOWED_HEALTH_REFRESH:
        freq = "manual"
    payload = {
        "refresh_frequency": freq,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(ADMIN_HEALTH_CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(payload, f, default_flow_style=False)


def load_async_tasks() -> dict:
    """Load async task configurations from async_tasks.yaml.

    Returns dict: {instrument: [task_cfg_dict, ...]}
    """
    ensure_ari_directory()
    ASYNC_TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    legacy_file = ADMIN_DIR / "async_tasks.yaml"
    if not ASYNC_TASKS_FILE.exists() and legacy_file.exists():
        try:
            ASYNC_TASKS_FILE.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass
    if not ASYNC_TASKS_FILE.exists():
        ASYNC_TASKS_FILE.write_text("")
    try:
        with open(ASYNC_TASKS_FILE, "r") as f:
            data = yaml.safe_load(f)
    except Exception:
        # File may be corrupted (e.g. null bytes from truncated write).
        # Try stripping null bytes before giving up.
        try:
            raw = ASYNC_TASKS_FILE.read_bytes()
            cleaned = raw.replace(b"\x00", b"")
            data = yaml.safe_load(cleaned)
        except Exception:
            data = None
    if not data:
        return {}
    if not isinstance(data, dict):
        return {}

    # Canonicalize global scope key so old variants do not split state
    # across multiple buckets (GLOBAL/global/__global__/__GLOBAL__).
    out = {}
    global_rows = []
    for raw_key, raw_tasks in data.items():
        key = str(raw_key or '').strip()
        norm = key.lower().replace('_', '')
        is_global = norm == 'global'
        if is_global:
            if isinstance(raw_tasks, list):
                global_rows.extend(raw_tasks)
            continue
        out[key] = raw_tasks
    if len(global_rows) > 0:
        existing = out.get('__GLOBAL__', [])
        if not isinstance(existing, list):
            existing = []
        out['__GLOBAL__'] = existing + global_rows
    return out


def save_async_tasks(tasks: dict) -> None:
    """Save async task configurations to async_tasks.yaml."""
    ensure_ari_directory()
    ASYNC_TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ASYNC_TASKS_FILE, "w") as f:
        yaml.dump(tasks, f, default_flow_style=False)


# =============================================================================
# APERO profile management
# =============================================================================
def _profile_is_disabled(profile_data: dict) -> bool:
    """Return True when a profile config is marked disabled."""
    if not isinstance(profile_data, dict):
        return False
    raw = profile_data.get('disabled', profile_data.get('DISABLED', False))
    if isinstance(raw, bool):
        return raw
    text = str(raw or '').strip().lower()
    return text in {'1', 'true', 'yes', 'on', 'y'}


def _profile_is_temporary(profile_data: dict) -> bool:
    """Return True when a profile config is marked temporary."""
    if not isinstance(profile_data, dict):
        return False
    raw = profile_data.get('temporary', profile_data.get('TEMPORARY', False))
    if isinstance(raw, bool):
        return raw
    text = str(raw or '').strip().lower()
    return text in {'1', 'true', 'yes', 'on', 'y'}


def _filter_enabled_profiles(profiles: Any) -> dict:
    """Return a copy of profiles with disabled and temporary removed."""
    if not isinstance(profiles, dict):
        return {}

    out: Dict[str, dict] = {}
    for instrument, instr_profiles in profiles.items():
        if not isinstance(instr_profiles, dict):
            continue
        enabled: Dict[str, dict] = {}
        for profile_id, profile_data in instr_profiles.items():
            if _profile_is_disabled(profile_data):
                continue
            if _profile_is_temporary(profile_data):
                continue
            enabled[profile_id] = profile_data
        out[instrument] = enabled
    return out


def _filter_temporary_profiles(profiles: Any) -> dict:
    """Return a copy of profiles with temporary profiles removed."""
    if not isinstance(profiles, dict):
        return {}

    out: Dict[str, dict] = {}
    for instrument, instr_profiles in profiles.items():
        if not isinstance(instr_profiles, dict):
            continue
        visible: Dict[str, dict] = {}
        for profile_id, profile_data in instr_profiles.items():
            if _profile_is_temporary(profile_data):
                continue
            visible[profile_id] = profile_data
        out[instrument] = visible
    return out


def load_apero_profiles(
    hydrate: bool = True,
    enabled_only: bool = False,
    include_temporary: bool = False,
) -> dict:
    """Load APERO profiles from apero_profiles.yaml.

    Args:
        hydrate: When True, merge APERO_INSTRUMENT_PROFILE defaults into each
            profile payload for runtime use. When False, return raw file
            content (useful before mutating/saving profiles).
        enabled_only: When True, skip profiles marked as disabled.
        include_temporary: When True, keep temporary draft profiles in the
            returned structure. Temporary profiles are hidden by default.

    The loaded profiles are cached in-process for _PROFILES_TTL seconds so
    that repeated calls within the same server process (e.g. multiple
    simultaneous API requests) do not all hit the YAML file on disk.
    """
    cache_key = 'hydrated' if hydrate else 'raw'
    if enabled_only:
        cache_key += '_enabled'

    ensure_ari_directory()
    legacy_file = ADMIN_DIR / "apero_profiles.yaml"
    if not APERO_PROFILES_FILE.exists() and legacy_file.exists():
        try:
            APERO_PROFILES_FILE.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass
    if not APERO_PROFILES_FILE.exists():
        APERO_PROFILES_FILE.write_text("")

    # Check file mtime without the lock (cheap stat call).
    try:
        current_mtime = APERO_PROFILES_FILE.stat().st_mtime
    except OSError:
        current_mtime = None

    with _profiles_lock:
        entry = _profiles_cache.get(cache_key)
        if (entry is not None
                and current_mtime is not None
                and entry.get("mtime") == current_mtime):
            return entry["data"]

    # Cache miss or file changed — parse YAML outside the lock.
    with open(APERO_PROFILES_FILE, "r") as f:
        data = yaml.safe_load(f)
    profiles = data if data else {}
    if not hydrate:
        result = profiles
    elif not isinstance(profiles, dict):
        result = {}
    else:
        hydrated: Dict[str, dict] = {}
        for instrument, instr_profiles in profiles.items():
            if not isinstance(instr_profiles, dict):
                continue
            hprofiles: Dict[str, dict] = {}
            for profile_id, profile_data in instr_profiles.items():
                if not isinstance(profile_data, dict):
                    continue
                hprofiles[profile_id] = _hydrate_profile_data(
                    profile_data, instrument
                )
            hydrated[instrument] = hprofiles
        result = hydrated

    if enabled_only:
        result = _filter_enabled_profiles(result)
    elif not include_temporary:
        result = _filter_temporary_profiles(result)
    with _profiles_lock:
        _profiles_cache[cache_key] = {
            "mtime": current_mtime,
            "data": result,
        }
    return result


def save_apero_profiles(profiles: dict) -> None:
    """Save APERO profiles to apero_profiles.yaml."""
    ensure_ari_directory()
    with open(APERO_PROFILES_FILE, "w") as f:
        yaml.dump(profiles, f, default_flow_style=False)
    # Invalidate in-process cache so the next read returns the new data.
    with _profiles_lock:
        _profiles_cache.clear()


def rename_instrument(old_name: str, new_name: str) -> Dict[str, Any]:
    """Rename an instrument across all ARI data stores.

    Updates (in order):

    1. ``apero_profiles.yaml`` — moves the top-level instrument key and
       updates ``general.INSTRUMENT`` / ``general.instrument`` inside
       every sub-profile.
    2. Instrument data files under ``~/.ari/admin/instruments/`` — renames
       ``{old}_calendar.yaml`` and ``{old}_links.yaml`` (if they exist).
    3. Science-groups file under ``~/.ari/admin/science_groups/`` — renames
       ``{old_lower}_science_groups.yaml`` (if it exists).
    4. Per-instrument permission groups — renames every group named
       ``{level}.{old}`` to ``{level}.{new}`` and updates user memberships.
    5. User records — replaces ``old_name`` with ``new_name`` in every
       user's ``instruments`` list.
    6. Task output directory — renames ``~/.ari/tasks/{OLD}/`` if present.
    7. Cache directory — renames ``~/.ari/cache/{OLD}/`` if present.
    8. ``parameters.yaml`` — replaces ``old_name`` with ``new_name`` in
       the ``instruments.value`` list.

    :raises ValueError: if ``old_name`` is not found or ``new_name``
        already exists.
    :returns: summary dict describing what was changed.
    """
    import os

    old = str(old_name or "").strip()
    new = str(new_name or "").strip()
    if not old or not new:
        raise ValueError("Both old_name and new_name are required.")
    if old == new:
        raise ValueError("old_name and new_name are the same.")

    summary: Dict[str, Any] = {
        "profiles_updated": False,
        "files_renamed": [],
        "groups_renamed": [],
        "users_updated": 0,
        "tasks_dir_renamed": False,
        "cache_dir_renamed": False,
    }

    # ------------------------------------------------------------------
    # 1. apero_profiles.yaml
    # ------------------------------------------------------------------
    all_profiles = load_apero_profiles(hydrate=False)
    if not isinstance(all_profiles, dict) or old not in all_profiles:
        raise ValueError(
            f"Instrument '{old}' not found in apero_profiles."
        )
    if new in all_profiles:
        raise ValueError(
            f"Instrument '{new}' already exists in apero_profiles."
        )

    # Move the key and update embedded instrument name in sub-profiles.
    profile_block = all_profiles.pop(old)
    if isinstance(profile_block, dict):
        for pname, pdata in profile_block.items():
            if not isinstance(pdata, dict):
                continue
            # Drop hydrated key if accidentally persisted.
            pdata.pop("APERO_INSTRUMENT_PROFILE_DATA", None)
            gen = pdata.get("general")
            if isinstance(gen, dict):
                if gen.get("INSTRUMENT") == old:
                    gen["INSTRUMENT"] = new
                if gen.get("instrument") == old:
                    gen["instrument"] = new
    all_profiles[new] = profile_block
    save_apero_profiles(all_profiles)
    summary["profiles_updated"] = True

    # ------------------------------------------------------------------
    # 2. Instrument data files (calendar, links)
    # ------------------------------------------------------------------
    instr_dir = ud.INSTRUMENTS_DIR
    instr_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("_calendar.yaml", "_links.yaml"):
        old_file = instr_dir / f"{old}{suffix}"
        new_file = instr_dir / f"{new}{suffix}"
        if old_file.exists():
            os.rename(str(old_file), str(new_file))
            summary["files_renamed"].append(str(new_file))

    # ------------------------------------------------------------------
    # 3. Science-groups file
    # ------------------------------------------------------------------
    sci_dir = SCI_GROUPS_DIR
    old_sg = sci_dir / f"{old.lower()}_science_groups.yaml"
    new_sg = sci_dir / f"{new.lower()}_science_groups.yaml"
    if old_sg.exists() and not new_sg.exists():
        os.rename(str(old_sg), str(new_sg))
        summary["files_renamed"].append(str(new_sg))

    # ------------------------------------------------------------------
    # 4. Permission groups
    # ------------------------------------------------------------------
    from apero_ri.core import permissions as _perm_mod  # local import

    all_groups = _perm_mod.load_groups()
    group_levels = [
        "general", "monitor", "developer", "moderator"
    ]
    old_group_names = {
        f"{lvl}.{old}" for lvl in group_levels
    }
    renamed_groups: Dict[str, str] = {}
    for old_gname in list(all_groups.keys()):
        if old_gname in old_group_names:
            new_gname = old_gname.replace(
                f".{old}", f".{new}", 1
            )
            all_groups[new_gname] = all_groups.pop(old_gname)
            renamed_groups[old_gname] = new_gname
    if renamed_groups:
        _perm_mod.save_groups(all_groups)
        summary["groups_renamed"] = list(renamed_groups.values())

    # Update group memberships in every user record.
    if renamed_groups:
        all_users_raw = load_users()
        changed_users = 0
        for uname, udata in all_users_raw.items():
            if not isinstance(udata, dict):
                continue
            user_groups = list(udata.get("groups") or [])
            new_groups = [
                renamed_groups.get(g, g) for g in user_groups
            ]
            if new_groups != user_groups:
                all_users_raw[uname]["groups"] = new_groups
                changed_users += 1
        if changed_users:
            save_users(all_users_raw)

    # ------------------------------------------------------------------
    # 5. User instrument lists
    # ------------------------------------------------------------------
    all_users_raw = load_users()
    users_updated = 0
    for uname, udata in all_users_raw.items():
        if not isinstance(udata, dict):
            continue
        user_instr = list(udata.get("instruments") or [])
        if old in user_instr:
            all_users_raw[uname]["instruments"] = [
                new if i == old else i for i in user_instr
            ]
            users_updated += 1
    if users_updated:
        save_users(all_users_raw)
    summary["users_updated"] = users_updated

    # ------------------------------------------------------------------
    # 6. Task output directory
    # ------------------------------------------------------------------
    tasks_old = ARI_DIR / "tasks" / old
    tasks_new = ARI_DIR / "tasks" / new
    if tasks_old.exists() and not tasks_new.exists():
        os.rename(str(tasks_old), str(tasks_new))
        summary["tasks_dir_renamed"] = True

    # ------------------------------------------------------------------
    # 7. Cache directory
    # ------------------------------------------------------------------
    cache_old = ARI_DIR / "cache" / old
    cache_new = ARI_DIR / "cache" / new
    if cache_old.exists() and not cache_new.exists():
        os.rename(str(cache_old), str(cache_new))
        summary["cache_dir_renamed"] = True

    # ------------------------------------------------------------------
    # 8. parameters.yaml instruments list
    # ------------------------------------------------------------------
    from apero_ri.core import permissions as _perm_mod  # local import

    _params = _perm_mod.load_parameters()
    _instr_block = _params.get("instruments")
    if isinstance(_instr_block, dict):
        _instr_list = _instr_block.get("value")
        if isinstance(_instr_list, list) and old in _instr_list:
            _instr_block["value"] = [
                new if i == old else i for i in _instr_list
            ]
            _perm_mod.save_parameters(_params)
            summary["parameters_yaml_updated"] = True

    return summary


def _apero_instrument_profile_path(filename: str) -> Path:
    """Return path under resources/aprofile_instruments for a profile file."""
    pkg_dir = Path(__file__).resolve().parents[1]
    safe_name = Path(str(filename or "")).name
    return pkg_dir / "resources" / "aprofile_instruments" / safe_name


def _load_apero_instrument_profile(filename: str) -> Dict:
    """Load one instrument profile YAML from resources/aprofile_instruments."""
    path = _apero_instrument_profile_path(filename)
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _merge_missing_profile(dst: Dict, src: Dict) -> Dict:
    """Recursively merge missing keys from src into dst."""
    if not isinstance(dst, dict) or not isinstance(src, dict):
        return dst
    for key, src_val in src.items():
        if key not in dst:
            dst[key] = deepcopy(src_val)
            continue
        dst_val = dst.get(key)
        if isinstance(dst_val, dict) and isinstance(src_val, dict):
            _merge_missing_profile(dst_val, src_val)
    return dst


def _hydrate_profile_data(profile_data: dict, instrument: str) -> dict:
    """Hydrate runtime profile data from APERO_INSTRUMENT_PROFILE reference.

    This keeps resource instrument YAML as the source of truth for sections
    like sci-headers/plots/general extras (e.g. has_polarimetry,
    db-query-preset-file) while preserving user-managed values such as
    DB/path settings and science selections.
    """
    out = deepcopy(profile_data) if isinstance(profile_data, dict) else {}
    ref_name = str(
        out.get("APERO_INSTRUMENT_PROFILE", "")
        or out.get("apero_instrument_profile", "")
        or ""
    ).strip()
    if not ref_name:
        return out

    preset = _load_apero_instrument_profile(ref_name)
    if not preset:
        return out

    # Keep all preset keys available (forward compatible with new fields).
    _merge_missing_profile(out, preset)
    out["APERO_INSTRUMENT_PROFILE_DATA"] = deepcopy(preset)

    # sci-headers: always from instrument resource profile
    if isinstance(preset.get("sci-headers"), dict):
        out["sci-headers"] = deepcopy(preset.get("sci-headers", {}))
    elif isinstance(preset.get("headers"), dict):
        # Backward compatibility for legacy preset files.
        out["sci-headers"] = deepcopy(preset.get("headers", {}))

    # calib-headers: always from instrument resource profile when available.
    if isinstance(preset.get("calib-headers"), dict):
        out["calib-headers"] = deepcopy(preset.get("calib-headers", {}))

    # plots: accept either "plots" or "plot" in resource file
    if isinstance(preset.get("plots"), dict):
        out["plots"] = deepcopy(preset.get("plots", {}))
    elif isinstance(preset.get("plot"), dict):
        out["plots"] = deepcopy(preset.get("plot", {}))
    if isinstance(out.get("plots"), dict):
        out["plot"] = deepcopy(out.get("plots", {}))

    # general: start from resource defaults, then force canonical science keys
    # from saved profile to preserve admin/user selections.
    preset_general = preset.get("general", {})
    saved_general = (
        out.get("general", {}) if isinstance(out.get("general"), dict) else {}
    )
    if isinstance(preset_general, dict):
        merged_general = deepcopy(preset_general)

        sci_fiber = (
            saved_general.get("SCIENCE_FIBER")
            or saved_general.get("science_fiber")
            or ""
        )
        sci_types = (
            saved_general.get("SCIENCE_TYPES")
            or saved_general.get("science_types")
            or []
        )
        if isinstance(sci_types, str):
            sci_types = [v.strip() for v in sci_types.split(",") if v.strip()]
        elif not isinstance(sci_types, list):
            sci_types = []

        merged_general["INSTRUMENT"] = instrument
        if sci_fiber:
            merged_general["SCIENCE_FIBER"] = sci_fiber
        if sci_types:
            merged_general["SCIENCE_TYPES"] = sci_types
        out["general"] = merged_general

    return out


def load_db_access() -> dict:
    """Load DB access configuration from db_access.yaml."""
    ensure_ari_directory()
    legacy_file = ADMIN_DIR / "db_access.yaml"
    if not DB_ACCESS_FILE.exists() and legacy_file.exists():
        try:
            DB_ACCESS_FILE.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass
    if not DB_ACCESS_FILE.exists():
        DB_ACCESS_FILE.write_text("")
    with open(DB_ACCESS_FILE, "r") as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_db_access(data: dict) -> None:
    """Save DB access configuration to db_access.yaml."""
    ensure_ari_directory()
    with open(DB_ACCESS_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def load_db_tunnels() -> dict:
    """Load DB tunnel/local definitions from db_tunnels.yaml."""
    ensure_ari_directory()
    legacy_file = ADMIN_DIR / "db_tunnels.yaml"
    if not DB_TUNNELS_FILE.exists() and legacy_file.exists():
        try:
            DB_TUNNELS_FILE.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass
    if not DB_TUNNELS_FILE.exists():
        DB_TUNNELS_FILE.write_text("")
    with open(DB_TUNNELS_FILE, "r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        data = {}
    tunnels = data.get("tunnels", {})
    if not isinstance(tunnels, dict):
        tunnels = {}
    local_databases = data.get("local_databases", {})
    if not isinstance(local_databases, dict):
        local_databases = {}
    return {
        "tunnels": tunnels,
        "local_databases": local_databases,
    }


def save_db_tunnels(data: dict) -> None:
    """Save DB tunnel/local definitions to db_tunnels.yaml."""
    ensure_ari_directory()
    payload = data if isinstance(data, dict) else {}
    tunnels = payload.get("tunnels", {})
    if not isinstance(tunnels, dict):
        tunnels = {}
    local_databases = payload.get("local_databases", {})
    if not isinstance(local_databases, dict):
        local_databases = {}
    with open(DB_TUNNELS_FILE, "w") as f:
        yaml.dump(
            {
                "tunnels": tunnels,
                "local_databases": local_databases,
            },
            f,
            default_flow_style=False,
        )


def validate_path_exists(path_str: str, kind: str = "dir") -> dict:
    """Check whether a path exists on disk as a directory or file.

    Returns dict with 'valid' and 'exists'.
    """
    p = Path(path_str)
    if kind == "file":
        # Match the directory browser's classification (anything that isn't
        # a directory is listed as a file), so symlinks / special files that
        # show up there also validate as "exists" here.
        exists = p.exists() and not p.is_dir()
    else:
        exists = p.is_dir()
    return {"valid": exists, "exists": exists}


def validate_database_connection(
    mode: str,
    host: str,
    username: str,
    password: str,
    db_name: str,
    port: str = "",
    use_ssh_tunnel: Any = False,
    ssh_config_host: str = "",
    ssh_local_port: str = "",
    ssh_remote_port: str = "",
    local_data_dir: Optional[str] = None,
) -> dict:
    """Try to connect to a database using the given credentials.

    Returns dict with 'valid' bool and 'error' string.
    """
    sql_error = None
    try:
        from apero_ri.tasks import apero_async

        db_params = {
            "DATABASE_MODE": mode,
            "DATABASE_HOST": host,
            "DATABASE_PORT": port,
            "DATABASE_USER": username,
            "DATABASE_PASSWORD": password,
            "DATABASE_NAME": db_name,
            "DATABASE_USE_SSH_TUNNEL": use_ssh_tunnel,
            "DATABASE_SSH_CONFIG_HOST": ssh_config_host,
            "DATABASE_SSH_LOCAL_PORT": ssh_local_port,
            "DATABASE_SSH_REMOTE_PORT": ssh_remote_port,
            "DATABASE_SSH_ALLOW_MULTIPLE": bool(use_ssh_tunnel),
        }
        if local_data_dir:
            db_params["LOCAL_DATA_DIR"] = str(local_data_dir)
        apero_async.database_query(db_params, "SELECT 1 AS ok")
        return {"valid": True, "error": ""}
    except Exception as e:
        sql_error = str(e)

    # Some DB servers accept a tunnel/auth handshake but drop later stages.
    # Run staged direct probes so the UI can show exactly where it fails.
    try:
        import pymysql

        tunnel_mode = str(mode or "").strip().lower()
        host_text = str(host or "").strip()
        user_text = str(username or "").strip()
        password_text = str(password or "")
        db_name_text = str(db_name or "").strip()
        port_value = 3306
        if port:
            try:
                port_value = int(str(port).strip())
            except Exception:
                port_value = 3306

        if tunnel_mode.startswith('mysql'):
            stage_bits = []
            try:
                with socket.create_connection(
                    (host_text, port_value), timeout=5
                ):
                    stage_bits.append('tcp=ok')
            except Exception as tcp_exc:
                stage_bits.append('tcp=fail')
                return {
                    'valid': False,
                    'error': (
                        f'{sql_error} | Direct TCP probe failed: {tcp_exc} '
                        f'| Stages: {", ".join(stage_bits)}'
                    ),
                }

            try:
                with pymysql.connect(
                    host=host_text,
                    user=user_text,
                    password=password_text,
                    database=None,
                    port=port_value,
                    connect_timeout=10,
                    read_timeout=10,
                    write_timeout=10,
                    autocommit=True,
                    charset='utf8mb4',
                ) as conn:
                    conn.ping(reconnect=False)
                stage_bits.append('auth=ok')
            except Exception as auth_exc:
                stage_bits.append('auth=fail')
                return {
                    'valid': False,
                    'error': (
                        f'{sql_error} | Direct MySQL connect/auth failed: '
                        f'{auth_exc} | Stages: {", ".join(stage_bits)}'
                    ),
                }

            try:
                with pymysql.connect(
                    host=host_text,
                    user=user_text,
                    password=password_text,
                    database=db_name_text,
                    port=port_value,
                    connect_timeout=10,
                    read_timeout=10,
                    write_timeout=10,
                    autocommit=True,
                    charset='utf8mb4',
                ) as conn:
                    conn.ping(reconnect=False)
                stage_bits.append('db_select=ok')
            except Exception as db_exc:
                stage_bits.append('db_select=fail')
                return {
                    'valid': False,
                    'error': (
                        f'{sql_error} | Direct MySQL auth succeeded, but '
                        f'database selection failed: {db_exc} '
                        f'| Stages: {", ".join(stage_bits)}'
                    ),
                }

            try:
                with pymysql.connect(
                    host=host_text,
                    user=user_text,
                    password=password_text,
                    database=db_name_text,
                    port=port_value,
                    connect_timeout=10,
                    read_timeout=10,
                    write_timeout=10,
                    autocommit=True,
                    charset='utf8mb4',
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute('SELECT 1 AS ok')
                        cursor.fetchone()
                stage_bits.append('query=ok')
                return {
                    'valid': True,
                    'error': '',
                    'warning': (
                        'SQLAlchemy query failed, but a direct PyMySQL '
                        'query succeeded. '
                        f'Stages: {", ".join(stage_bits)}'
                    ),
                }
            except Exception as direct_query_exc:
                stage_bits.append('query=fail')
                return {
                    'valid': False,
                    'error': (
                        f'{sql_error} | Direct MySQL auth succeeded, but '
                        'query failed after DB selection. '
                        f'Direct query error: {direct_query_exc} '
                        f'| Stages: {", ".join(stage_bits)}'
                    ),
                }
    except Exception as direct_exc:
        return {
            'valid': False,
            'error': (
                f'{sql_error} | Direct MySQL connect/auth failed: '
                f'{direct_exc}'
            ),
        }

    return {'valid': False, 'error': sql_error or 'Database test failed.'}


# =============================================================================
# Science group management
# =============================================================================
def _sci_groups_file(instrument: str) -> Path:
    """Return the path to the science groups YAML for an instrument."""
    safe = instrument.lower().replace(" ", "_")
    new_path = SCI_GROUPS_DIR / f"{safe}_science_groups.yaml"
    legacy_path = ADMIN_DIR / f"{safe}_science_groups.yaml"
    if not new_path.exists() and legacy_path.exists():
        try:
            SCI_GROUPS_DIR.mkdir(parents=True, exist_ok=True)
            new_path.write_bytes(legacy_path.read_bytes())
        except Exception:
            pass
    return new_path


def load_science_groups(instrument: str) -> Dict[str, dict]:
    """Load science groups for an instrument. Creates file if missing."""
    path = _sci_groups_file(instrument)
    ensure_ari_directory()
    if not path.exists():
        path.write_text("")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    groups = data if isinstance(data, dict) else {}

    # Keep a reserved canonical All group present for every instrument.
    changed = False
    all_entry = groups.get("All")
    if not isinstance(all_entry, dict):
        groups["All"] = {"run_ids": [], "users": []}
        changed = True
    else:
        if not isinstance(all_entry.get("run_ids", []), list):
            all_entry["run_ids"] = []
            changed = True
        if not isinstance(all_entry.get("users", []), list):
            all_entry["users"] = []
            changed = True
        groups["All"] = all_entry

    if changed:
        try:
            save_science_groups(instrument, groups)
        except Exception:
            pass

    return groups


def save_science_groups(instrument: str, groups: Dict[str, dict]) -> None:
    """Save science groups for an instrument."""
    ensure_ari_directory()
    path = _sci_groups_file(instrument)
    with open(path, "w") as f:
        yaml.dump(groups, f, default_flow_style=False)


def get_users_for_instrument(instrument: str) -> List[str]:
    """Get all usernames whose groups grant access to *instrument*."""
    from apero_ri.core.permissions import (
        get_inherited_groups,
        load_groups,
    )
    groups = load_groups()
    users = load_users()
    result = []
    for username, data in users.items():
        user_groups = set(data.get('groups', []))
        all_groups = set(user_groups)
        for g in list(user_groups):
            all_groups |= get_inherited_groups(g, groups)
        has_instr = any(
            g.rsplit('.', 1)[-1] == instrument
            for g in all_groups
            if '.' in g
        )
        if has_instr:
            result.append(username)
    return sorted(result)


def get_accessible_profiles(
    user_info: Optional[dict], ari_groups: Dict[str, dict]
) -> List[dict]:
    """Get APERO profiles accessible to a user.

    Access rules:
    1. User's instruments must include the profile's instrument.
       If the user has no instruments assigned, all instruments match.
    2. If a profile has groups assigned, the user must belong to (or
       inherit) at least one of those groups.
    3. Profiles with an empty groups list are visible to anyone who
       has ``view.data_portal`` permission.
    """
    from apero_ri.core.permissions import get_inherited_groups
    from apero_ri.core.permissions import get_user_instruments

    profiles_data = load_apero_profiles(hydrate=False, enabled_only=True)
    if not profiles_data:
        return []

    if user_info:
        user_instruments = set(get_user_instruments(
            user_info.get('groups', []), ari_groups
        ))
        user_groups = set(user_info.get("groups", []))
        all_user_groups = set(user_groups)
        for grp in list(user_groups):
            all_user_groups |= get_inherited_groups(grp, ari_groups)
    else:
        user_instruments = set()
        all_user_groups = {"public"}

    accessible = []
    for instrument, instr_profiles in profiles_data.items():
        if not isinstance(instr_profiles, dict):
            continue
        # If user has explicit instruments, filter to those
        if user_instruments and instrument not in user_instruments:
            continue
        for profile_id, profile_data in instr_profiles.items():
            if not isinstance(profile_data, dict):
                continue
            profile_groups = set(profile_data.get("groups", []))
            if profile_groups and not all_user_groups & profile_groups:
                continue
            hydrated_data = _hydrate_profile_data(profile_data, instrument)
            accessible.append(
                {
                    "instrument": instrument,
                    "profile_id": profile_id,
                    "data": hydrated_data,
                }
            )

    accessible.sort(
        key=lambda x: (x["instrument"], x["data"].get("DISPLAY_ORDER", 999))
    )
    return accessible
