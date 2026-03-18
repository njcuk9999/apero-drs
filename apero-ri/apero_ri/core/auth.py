#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Authentication and user management.

Manages user accounts stored in ~/.ari/admin/users.yaml,
password hashing via the cryptography package, and Flask session login.
"""
import os
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

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
    with open(ASYNC_TASKS_FILE, 'r') as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_async_tasks(tasks: dict) -> None:
    """Save async task configurations to async_tasks.yaml."""
    ensure_ari_directory()
    with open(ASYNC_TASKS_FILE, 'w') as f:
        yaml.dump(tasks, f, default_flow_style=False)


# =============================================================================
# APERO profile management
# =============================================================================
def load_apero_profiles() -> dict:
    """Load APERO profiles from apero_profiles.yaml."""
    ensure_ari_directory()
    if not APERO_PROFILES_FILE.exists():
        APERO_PROFILES_FILE.write_text('')
    with open(APERO_PROFILES_FILE, 'r') as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_apero_profiles(profiles: dict) -> None:
    """Save APERO profiles to apero_profiles.yaml."""
    ensure_ari_directory()
    with open(APERO_PROFILES_FILE, 'w') as f:
        yaml.dump(profiles, f, default_flow_style=False)


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
                                 password: str, db_name: str) -> dict:
    """Try to connect to a database using the given credentials.

    Returns dict with 'valid' bool and 'error' string.
    """
    if mode != 'mysql+pymysql':
        return {'valid': False, 'error': f'Unsupported mode: {mode}'}

    try:
        import pymysql
    except ImportError:
        return {'valid': False, 'error': 'pymysql is not installed'}

    # Parse host:port
    db_host = host
    db_port = 3306
    if ':' in host:
        parts = host.rsplit(':', 1)
        db_host = parts[0]
        try:
            db_port = int(parts[1])
        except ValueError:
            return {'valid': False, 'error': f'Invalid port: {parts[1]}'}

    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=username,
            password=password,
            database=db_name,
            connect_timeout=10,
        )
        conn.close()
        return {'valid': True, 'error': ''}
    except pymysql.err.OperationalError as e:
        return {'valid': False, 'error': str(e)}
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

    profiles_data = load_apero_profiles()
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
            accessible.append({
                'instrument': instrument,
                'profile_id': profile_id,
                'data': dict(profile_data),
            })

    accessible.sort(key=lambda x: (x['instrument'],
                                   x['data'].get('DISPLAY_ORDER', 999)))
    return accessible
