#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Authentication and user management.

Manages user accounts stored in ~/.ari/admin/users.yaml,
password hashing via the cryptography package, and Flask session login.
"""
import os
import base64
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from apero_ri.core.permissions import (resolve_user_permissions, load_groups,
                                       load_pages)

# =============================================================================
# Define variables
# =============================================================================
ARI_DIR = Path.home() / '.ari'
ADMIN_DIR = ARI_DIR / 'admin'
USERS_FILE = ADMIN_DIR / 'users.yaml'
SCI_GROUPS_DIR = ADMIN_DIR
ADMIN_HEALTH_CONFIG_FILE = ADMIN_DIR / 'health_status.yaml'

# PBKDF2 parameters
HASH_ALGORITHM = hashes.SHA256()
HASH_ITERATIONS = 600_000
HASH_KEY_LENGTH = 32
SALT_LENGTH = 16

# Default admin account
DEFAULT_USER = 'neil'
DEFAULT_PASSWORD = '1234'
DEFAULT_GROUPS = ['admin']


def set_ari_dir(path: Optional[str]) -> None:
    """Configure storage root for auth-managed files."""
    global ARI_DIR, ADMIN_DIR, USERS_FILE, SCI_GROUPS_DIR
    global APERO_PROFILES_FILE, DB_ACCESS_FILE, ASYNC_TASKS_FILE
    global ADMIN_HEALTH_CONFIG_FILE
    base = Path(path).expanduser() if path else (Path.home() / '.ari')
    ARI_DIR = base
    ADMIN_DIR = ARI_DIR / 'admin'
    USERS_FILE = ADMIN_DIR / 'users.yaml'
    SCI_GROUPS_DIR = ADMIN_DIR
    APERO_PROFILES_FILE = ADMIN_DIR / 'apero_profiles.yaml'
    DB_ACCESS_FILE = ADMIN_DIR / 'db_access.yaml'
    ASYNC_TASKS_FILE = ADMIN_DIR / 'async_tasks.yaml'
    ADMIN_HEALTH_CONFIG_FILE = ADMIN_DIR / 'health_status.yaml'


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
    key = kdf.derive(password.encode('utf-8'))
    salt_b64 = base64.b64encode(salt).decode('ascii')
    key_b64 = base64.b64encode(key).decode('ascii')
    return f'{salt_b64}:{key_b64}'


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt_b64, key_b64 = stored_hash.split(':')
        salt = base64.b64decode(salt_b64)
        stored_key = base64.b64decode(key_b64)
    except (ValueError, Exception):
        return False

    kdf = PBKDF2HMAC(
        algorithm=HASH_ALGORITHM,
        length=HASH_KEY_LENGTH,
        salt=salt,
        iterations=HASH_ITERATIONS,
    )
    try:
        kdf.verify(password.encode('utf-8'), stored_key)
        return True
    except Exception:
        return False


# =============================================================================
# User management
# =============================================================================
def ensure_ari_directory() -> None:
    """Create the ~/.ari/admin directory if it doesn't exist."""
    ADMIN_DIR.mkdir(parents=True, exist_ok=True)


def load_users() -> Dict[str, dict]:
    """Load users from users.yaml."""
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_users(users: Dict[str, dict]) -> None:
    """Save users to users.yaml."""
    ensure_ari_directory()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(users, f, default_flow_style=False)


def create_user(username: str, password: str,
                groups: List[str]) -> None:
    """Create a new user or update an existing one."""
    users = load_users()
    users[username] = {
        'password': hash_password(password),
        'groups': groups,
    }
    save_users(users)


def ensure_default_user() -> None:
    """Ensure the default admin user exists."""
    users = load_users()
    for user_data in users.values():
        if isinstance(user_data, dict) and 'admin' in user_data.get('groups', []):
            return
    if DEFAULT_USER not in users:
        create_user(DEFAULT_USER, DEFAULT_PASSWORD, DEFAULT_GROUPS)


def authenticate(username: str, password: str) -> Optional[dict]:
    """Authenticate a user. Returns user dict on success, None on failure."""
    users = load_users()
    if username not in users:
        return None
    user = users[username]
    if not verify_password(password, user.get('password', '')):
        return None
    # Record previous last_login before updating
    prev_login = user.get('last_login')
    # Update last_login timestamp
    user['last_login'] = datetime.now(timezone.utc).isoformat()
    save_users(users)
    return {
        'username': username,
        'groups': user.get('groups', []),
        'last_login': prev_login,
    }


def get_user_info(username: str) -> Optional[dict]:
    """Get user info by username."""
    users = load_users()
    if username not in users:
        return None
    user = users[username]
    return {
        'username': username,
        'first_names': user.get('first_names', ''),
        'groups': user.get('groups', []),
        'instruments': user.get('instruments', []),
        'last_login': user.get('last_login'),
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
            results.append({
                'username': username,
                'groups': data.get('groups', []),
                'instruments': data.get('instruments', []),
                'first_names': data.get('first_names', ''),
                'last_name': data.get('last_name', ''),
            })
    return results


def list_all_users() -> List[dict]:
    """Return all users as a list of dicts."""
    users = load_users()
    return [
        {
            'username': username,
            'groups': data.get('groups', []),
            'instruments': data.get('instruments', []),
            'first_names': data.get('first_names', ''),
            'last_name': data.get('last_name', ''),
        }
        for username, data in users.items()
    ]


def update_user_groups(username: str, groups: List[str]) -> bool:
    """Update a user's groups list. Returns True on success."""
    users = load_users()
    if username not in users:
        return False
    users[username]['groups'] = groups
    save_users(users)
    return True


def update_user_instruments(username: str,
                            instruments: List[str]) -> bool:
    """Update a user's instruments list. Returns True on success."""
    users = load_users()
    if username not in users:
        return False
    users[username]['instruments'] = instruments
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
    real_user = session.get('user')
    if real_user is None:
        return None

    login_as_user = session.get('login_as')
    if login_as_user:
        # Verify the real user has permission to login as this user's group
        real_info = get_user_info(real_user)
        target_info = get_user_info(login_as_user)
        if real_info and target_info:
            groups = load_groups()
            real_perms = resolve_user_permissions(
                real_info['groups'], groups
            )
            # Check if real user can login_as any of target's groups
            for target_group in target_info['groups']:
                if f'login_as.{target_group}' in real_perms:
                    return target_info
        # If impersonation not allowed, fall back to real user
        session.pop('login_as', None)

    return get_user_info(real_user)


def get_public_permissions() -> Set[str]:
    """Get permissions for unauthenticated (public) users."""
    groups = load_groups()
    return resolve_user_permissions(['public'], groups)


# =============================================================================
# APERO profile management
# =============================================================================
APERO_PROFILES_FILE = ADMIN_DIR / 'apero_profiles.yaml'
DB_ACCESS_FILE = ADMIN_DIR / 'db_access.yaml'


# =============================================================================
# Async tasks configuration
# =============================================================================
ASYNC_TASKS_FILE = ADMIN_DIR / 'async_tasks.yaml'

# =============================================================================
# Admin health status configuration
# =============================================================================
_ALLOWED_HEALTH_REFRESH = {'manual', '5m', '15m', '1h'}


def load_admin_health_config() -> dict:
    """Load admin health-status settings from health_status.yaml."""
    ensure_ari_directory()
    if not ADMIN_HEALTH_CONFIG_FILE.exists():
        default = {'refresh_frequency': 'manual'}
        with open(ADMIN_HEALTH_CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(default, f, default_flow_style=False)
        return default

    with open(ADMIN_HEALTH_CONFIG_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        data = {}

    freq = str(data.get('refresh_frequency', 'manual')).strip().lower()
    if freq not in _ALLOWED_HEALTH_REFRESH:
        freq = 'manual'
    return {'refresh_frequency': freq}


def save_admin_health_config(config: dict) -> None:
    """Save admin health-status settings to health_status.yaml."""
    ensure_ari_directory()
    freq = str(config.get('refresh_frequency', 'manual')).strip().lower()
    if freq not in _ALLOWED_HEALTH_REFRESH:
        freq = 'manual'
    payload = {
        'refresh_frequency': freq,
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    with open(ADMIN_HEALTH_CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(payload, f, default_flow_style=False)


def load_async_tasks() -> dict:
    """Load async task configurations from async_tasks.yaml.

    Returns dict: {instrument: [task_cfg_dict, ...]}
    """
    ensure_ari_directory()
    if not ASYNC_TASKS_FILE.exists():
        ASYNC_TASKS_FILE.write_text('')
    try:
        with open(ASYNC_TASKS_FILE, 'r') as f:
            data = yaml.safe_load(f)
    except Exception:
        # File may be corrupted (e.g. null bytes from truncated write).
        # Try stripping null bytes before giving up.
        try:
            raw = ASYNC_TASKS_FILE.read_bytes()
            cleaned = raw.replace(b'\x00', b'')
            data = yaml.safe_load(cleaned)
        except Exception:
            data = None
    return data if data else {}


def save_async_tasks(tasks: dict) -> None:
    """Save async task configurations to async_tasks.yaml."""
    ensure_ari_directory()
    with open(ASYNC_TASKS_FILE, 'w') as f:
        yaml.dump(tasks, f, default_flow_style=False)


# =============================================================================
# APERO profile management
# =============================================================================
def load_apero_profiles(hydrate: bool = True) -> dict:
    """Load APERO profiles from apero_profiles.yaml.

    Args:
        hydrate: When True, merge APERO_INSTRUMENT_PROFILE defaults into each
            profile payload for runtime use. When False, return raw file
            content (useful before mutating/saving profiles).
    """
    ensure_ari_directory()
    if not APERO_PROFILES_FILE.exists():
        APERO_PROFILES_FILE.write_text('')
    with open(APERO_PROFILES_FILE, 'r') as f:
        data = yaml.safe_load(f)
    profiles = data if data else {}
    if not hydrate:
        return profiles
    if not isinstance(profiles, dict):
        return {}

    hydrated: Dict[str, dict] = {}
    for instrument, instr_profiles in profiles.items():
        if not isinstance(instr_profiles, dict):
            continue
        hprofiles: Dict[str, dict] = {}
        for profile_id, profile_data in instr_profiles.items():
            if not isinstance(profile_data, dict):
                continue
            hprofiles[profile_id] = _hydrate_profile_data(profile_data, instrument)
        hydrated[instrument] = hprofiles
    return hydrated


def save_apero_profiles(profiles: dict) -> None:
    """Save APERO profiles to apero_profiles.yaml."""
    ensure_ari_directory()
    with open(APERO_PROFILES_FILE, 'w') as f:
        yaml.dump(profiles, f, default_flow_style=False)


def _apero_instrument_profile_path(filename: str) -> Path:
    """Return path under resources/aprofile_instruments for a profile file."""
    pkg_dir = Path(__file__).resolve().parents[1]
    safe_name = Path(str(filename or '')).name
    return pkg_dir / 'resources' / 'aprofile_instruments' / safe_name


def _load_apero_instrument_profile(filename: str) -> Dict:
    """Load one instrument profile YAML from resources/aprofile_instruments."""
    path = _apero_instrument_profile_path(filename)
    if not path.is_file():
        return {}
    try:
        with path.open('r', encoding='utf-8') as f:
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
        out.get('APERO_INSTRUMENT_PROFILE', '')
        or out.get('apero_instrument_profile', '')
        or ''
    ).strip()
    if not ref_name:
        return out

    preset = _load_apero_instrument_profile(ref_name)
    if not preset:
        return out

    # Keep all preset keys available (forward compatible with new fields).
    _merge_missing_profile(out, preset)
    out['APERO_INSTRUMENT_PROFILE_DATA'] = deepcopy(preset)

    # sci-headers: always from instrument resource profile
    if isinstance(preset.get('sci-headers'), dict):
        out['sci-headers'] = deepcopy(preset.get('sci-headers', {}))
    elif isinstance(preset.get('headers'), dict):
        # Backward compatibility for legacy preset files.
        out['sci-headers'] = deepcopy(preset.get('headers', {}))

    # calib-headers: always from instrument resource profile when available.
    if isinstance(preset.get('calib-headers'), dict):
        out['calib-headers'] = deepcopy(preset.get('calib-headers', {}))

    # plots: accept either "plots" or "plot" in resource file
    if isinstance(preset.get('plots'), dict):
        out['plots'] = deepcopy(preset.get('plots', {}))
    elif isinstance(preset.get('plot'), dict):
        out['plots'] = deepcopy(preset.get('plot', {}))
    if isinstance(out.get('plots'), dict):
        out['plot'] = deepcopy(out.get('plots', {}))

    # general: start from resource defaults, then force canonical science keys
    # from saved profile to preserve admin/user selections.
    preset_general = preset.get('general', {})
    saved_general = out.get('general', {}) if isinstance(out.get('general'), dict) else {}
    if isinstance(preset_general, dict):
        merged_general = deepcopy(preset_general)

        sci_fiber = (
            saved_general.get('SCIENCE_FIBER')
            or saved_general.get('science_fiber')
            or ''
        )
        sci_types = (
            saved_general.get('SCIENCE_TYPES')
            or saved_general.get('science_types')
            or []
        )
        if isinstance(sci_types, str):
            sci_types = [v.strip() for v in sci_types.split(',') if v.strip()]
        elif not isinstance(sci_types, list):
            sci_types = []

        merged_general['INSTRUMENT'] = instrument
        if sci_fiber:
            merged_general['SCIENCE_FIBER'] = sci_fiber
        if sci_types:
            merged_general['SCIENCE_TYPES'] = sci_types
        out['general'] = merged_general

    return out


def load_db_access() -> dict:
    """Load DB access configuration from db_access.yaml."""
    ensure_ari_directory()
    if not DB_ACCESS_FILE.exists():
        DB_ACCESS_FILE.write_text('')
    with open(DB_ACCESS_FILE, 'r') as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_db_access(data: dict) -> None:
    """Save DB access configuration to db_access.yaml."""
    ensure_ari_directory()
    with open(DB_ACCESS_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def validate_path_exists(path_str: str) -> dict:
    """Check whether a directory exists on disk.

    Returns dict with 'valid' and 'exists'.
    """
    p = Path(path_str)
    exists = p.is_dir()
    return {'valid': exists, 'exists': exists}


def validate_database_connection(mode: str, host: str, username: str,
                                 password: str, db_name: str,
                                 port: str = '',
                                 use_ssh_tunnel: Any = False,
                                 ssh_config_host: str = '',
                                 ssh_local_port: str = '',
                                 ssh_remote_port: str = '',
                                 local_data_dir: Optional[str] = None) -> dict:
    """Try to connect to a database using the given credentials.

    Returns dict with 'valid' bool and 'error' string.
    """
    try:
        from apero_ri.tasks import apero_async

        db_params = {
            'DATABASE_MODE': mode,
            'DATABASE_HOST': host,
            'DATABASE_PORT': port,
            'DATABASE_USER': username,
            'DATABASE_PASSWORD': password,
            'DATABASE_NAME': db_name,
            'DATABASE_USE_SSH_TUNNEL': use_ssh_tunnel,
            'DATABASE_SSH_CONFIG_HOST': ssh_config_host,
            'DATABASE_SSH_LOCAL_PORT': ssh_local_port,
            'DATABASE_SSH_REMOTE_PORT': ssh_remote_port,
        }
        if local_data_dir:
            db_params['LOCAL_DATA_DIR'] = str(local_data_dir)
        apero_async.database_query(db_params, 'SELECT 1 AS ok')
        return {'valid': True, 'error': ''}
    except Exception as e:
        return {'valid': False, 'error': str(e)}


# =============================================================================
# Science group management
# =============================================================================
def _sci_groups_file(instrument: str) -> Path:
    """Return the path to the science groups YAML for an instrument."""
    safe = instrument.lower().replace(' ', '_')
    return SCI_GROUPS_DIR / f'{safe}_science_groups.yaml'


def load_science_groups(instrument: str) -> Dict[str, dict]:
    """Load science groups for an instrument. Creates file if missing."""
    path = _sci_groups_file(instrument)
    ensure_ari_directory()
    if not path.exists():
        path.write_text('')
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_science_groups(instrument: str,
                        groups: Dict[str, dict]) -> None:
    """Save science groups for an instrument."""
    ensure_ari_directory()
    path = _sci_groups_file(instrument)
    with open(path, 'w') as f:
        yaml.dump(groups, f, default_flow_style=False)


def get_users_for_instrument(instrument: str) -> List[str]:
    """Get all usernames that have this instrument in their profile."""
    users = load_users()
    result = []
    for username, data in users.items():
        if instrument in data.get('instruments', []):
            result.append(username)
    return sorted(result)


def get_accessible_profiles(user_info: Optional[dict],
                            ari_groups: Dict[str, dict]) -> List[dict]:
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

    profiles_data = load_apero_profiles(hydrate=False)
    if not profiles_data:
        return []

    if user_info:
        user_instruments = set(user_info.get('instruments', []))
        user_groups = set(user_info.get('groups', []))
        all_user_groups = set(user_groups)
        for grp in list(user_groups):
            all_user_groups |= get_inherited_groups(grp, ari_groups)
    else:
        user_instruments = set()
        all_user_groups = {'public'}

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
            profile_groups = set(profile_data.get('groups', []))
            if profile_groups and not all_user_groups & profile_groups:
                continue
            hydrated_data = _hydrate_profile_data(profile_data, instrument)
            accessible.append({
                'instrument': instrument,
                'profile_id': profile_id,
                'data': hydrated_data,
            })

    accessible.sort(key=lambda x: (x['instrument'],
                                   x['data'].get('DISPLAY_ORDER', 999)))
    return accessible
