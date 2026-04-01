#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bootstrap helpers for first-run APERO RI setup."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.setup.bootstrap'
BOOTSTRAP_FILE = Path.home() / '.apero_ri_bootstrap.yaml'
LEGACY_LOCAL_USER = 'njcuk9999'


# =============================================================================
# Define functions
# =============================================================================
def _default_data_dir() -> Path:
    return Path.home() / '.ari'


def load_bootstrap_config() -> Dict[str, Any]:
    if not BOOTSTRAP_FILE.exists():
        return {}
    try:
        with open(BOOTSTRAP_FILE, 'r', encoding='utf-8') as fobj:
            data = yaml.safe_load(fobj) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_bootstrap_config(local_data_dir: str) -> None:
    BOOTSTRAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'local_data_dir': str(Path(local_data_dir).expanduser()),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    with open(BOOTSTRAP_FILE, 'w', encoding='utf-8') as fobj:
        yaml.safe_dump(payload, fobj, default_flow_style=False,
                       allow_unicode=True)


def resolve_local_data_dir(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env_path = os.environ.get('ARI_DIR', '').strip()
    if env_path:
        return Path(env_path).expanduser()
    cfg = load_bootstrap_config()
    cfg_path = str(cfg.get('local_data_dir', '')).strip()
    if cfg_path:
        return Path(cfg_path).expanduser()
    return _default_data_dir()


def get_setup_state_path(local_data_dir: Path) -> Path:
    return Path(local_data_dir).expanduser() / 'admin' / 'setup_state.yaml'


def load_setup_state(local_data_dir: Path) -> Dict[str, Any]:
    path = get_setup_state_path(local_data_dir)
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as fobj:
            data = yaml.safe_load(fobj) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_setup_state(local_data_dir: Path,
                     admin_username: str,
                     email_configured: bool = True) -> None:
    path = get_setup_state_path(local_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'completed': True,
        'admin_username': admin_username,
        'email_configured': bool(email_configured),
        'completed_at': datetime.now(timezone.utc).isoformat(),
    }
    with open(path, 'w', encoding='utf-8') as fobj:
        yaml.safe_dump(payload, fobj, default_flow_style=False,
                       allow_unicode=True)


def is_setup_complete(local_data_dir: Path) -> bool:
    state = load_setup_state(local_data_dir)
    return bool(state.get('completed', False))


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as fobj:
            data = yaml.safe_load(fobj) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def get_users_file(local_data_dir: Path) -> Path:
    admin_dir = Path(local_data_dir).expanduser() / 'admin'
    new_path = admin_dir / 'general' / 'users.yaml'
    legacy_path = admin_dir / 'users.yaml'
    return new_path if new_path.exists() or not legacy_path.exists() else legacy_path


def get_email_file(local_data_dir: Path) -> Path:
    admin_dir = Path(local_data_dir).expanduser() / 'admin'
    new_path = admin_dir / 'email' / 'email.yaml'
    legacy_path = admin_dir / 'email.yaml'
    return new_path if new_path.exists() or not legacy_path.exists() else legacy_path


def has_admin_user(local_data_dir: Path,
                   preferred_username: Optional[str] = None) -> bool:
    users = _load_yaml_file(get_users_file(local_data_dir))
    if preferred_username and preferred_username in users:
        groups = users.get(preferred_username, {}).get('groups', [])
        return 'admin' in groups
    for user_data in users.values():
        if (isinstance(user_data, dict)
                and 'admin' in user_data.get('groups', [])):
            return True
    return False


def is_legacy_local_install(local_data_dir: Path) -> bool:
    users = _load_yaml_file(get_users_file(local_data_dir))
    email_cfg = _load_yaml_file(get_email_file(local_data_dir))
    if LEGACY_LOCAL_USER not in users:
        return False
    legacy_user = users.get(LEGACY_LOCAL_USER, {})
    if 'admin' not in legacy_user.get('groups', []):
        return False
    if not str(legacy_user.get('primary_email', '')).strip():
        return False
    return bool(email_cfg.get('enabled', False))


def can_start_main_app(local_data_dir: Path) -> bool:
    return (is_setup_complete(local_data_dir)
            or is_legacy_local_install(local_data_dir))


def ensure_directory_layout(local_data_dir: Path) -> None:
    base = Path(local_data_dir).expanduser()
    paths = [
        base,
        base / 'admin',
        base / 'admin' / 'instruments',
        base / 'backups',
        base / 'secret',
        base / 'tasks',
        base / 'users',
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)

    probe = base / '.write_test.tmp'
    with open(probe, 'w', encoding='utf-8') as fobj:
        fobj.write('ok')
    probe.unlink()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
