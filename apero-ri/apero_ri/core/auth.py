#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Authentication and user management.

Manages user accounts stored in ~/.ari/admin/users.yaml,
password hashing via the cryptography package, and Flask session login.
"""
import os
import base64
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

# PBKDF2 parameters
HASH_ALGORITHM = hashes.SHA256()
HASH_ITERATIONS = 600_000
HASH_KEY_LENGTH = 32
SALT_LENGTH = 16

# Default admin account
DEFAULT_USER = 'neil'
DEFAULT_PASSWORD = '1234'
DEFAULT_GROUPS = ['admin']


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
    with open(USERS_FILE, 'r') as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_users(users: Dict[str, dict]) -> None:
    """Save users to users.yaml."""
    ensure_ari_directory()
    with open(USERS_FILE, 'w') as f:
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
    return {
        'username': username,
        'groups': user.get('groups', []),
    }


def get_user_info(username: str) -> Optional[dict]:
    """Get user info by username."""
    users = load_users()
    if username not in users:
        return None
    user = users[username]
    return {
        'username': username,
        'groups': user.get('groups', []),
    }


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
