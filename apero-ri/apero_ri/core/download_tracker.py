#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download tracker: per-user download usage tracking and rate limiting.

Tracks two categories independently:
  - **api**: downloads via the programmatic API (ari_api client)
  - **basket**: downloads via the web-based download basket

Storage:  ~/.ari/admin/general/download_tracker.yaml
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# =============================================================================
# Module-level state
# =============================================================================
ARI_DIR = Path.home() / '.ari'
_lock = threading.Lock()

_DEFAULTS: Dict[str, Any] = {
    'settings': {
        'api_rate_limit_seconds': 2,
        'basket_rate_limit_seconds': 0,
        'basket_max_archive_gb': 5.0,
    },
    'api_usage': {},
    'basket_usage': {},
}


def set_ari_dir(path: Path) -> None:
    global ARI_DIR
    ARI_DIR = Path(path)


# =============================================================================
# Low-level I/O
# =============================================================================
def _tracker_path() -> Path:
    admin_dir = ARI_DIR / 'admin'
    general_dir = admin_dir / 'general'
    general_dir.mkdir(parents=True, exist_ok=True)
    tracker_file = general_dir / 'download_tracker.yaml'
    legacy_file = admin_dir / 'download_tracker.yaml'
    if not tracker_file.exists() and legacy_file.exists():
        try:
            tracker_file.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass
    return tracker_file


def _load() -> Dict[str, Any]:
    path = _tracker_path()
    if not path.exists():
        return _deep_copy_defaults()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return _deep_copy_defaults()
        for key, default_val in _DEFAULTS.items():
            data.setdefault(key, type(default_val)())
        if isinstance(data.get('settings'), dict):
            for k, v in _DEFAULTS['settings'].items():
                data['settings'].setdefault(k, v)
        return data
    except Exception:
        return _deep_copy_defaults()


def _save(data: Dict[str, Any]) -> None:
    path = _tracker_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def _deep_copy_defaults() -> Dict[str, Any]:
    import copy
    return copy.deepcopy(_DEFAULTS)


# =============================================================================
# Settings
# =============================================================================
def load_settings() -> Dict[str, Any]:
    with _lock:
        return dict(_load().get('settings', _DEFAULTS['settings']))


def save_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        data = _load()
        settings = data.get('settings', {})
        if 'api_rate_limit_seconds' in updates:
            val = updates['api_rate_limit_seconds']
            settings['api_rate_limit_seconds'] = max(0, float(val))
        if 'basket_rate_limit_seconds' in updates:
            val = updates['basket_rate_limit_seconds']
            settings['basket_rate_limit_seconds'] = max(0, float(val))
        if 'basket_max_archive_gb' in updates:
            val = updates['basket_max_archive_gb']
            settings['basket_max_archive_gb'] = max(0.1, float(val))
        data['settings'] = settings
        _save(data)
        return dict(settings)


# =============================================================================
# Usage recording
# =============================================================================
def record_download(username: str, category: str,
                    file_bytes: int, file_count: int = 1) -> None:
    """Record a download for a user under ``category`` ('api' or 'basket')."""
    key = f'{category}_usage'
    with _lock:
        data = _load()
        usage = data.setdefault(key, {})
        entry = usage.get(username)
        if not isinstance(entry, dict):
            entry = {'total_bytes': 0, 'total_files': 0,
                     'last_download_at': ''}
        entry['total_bytes'] = entry.get('total_bytes', 0) + max(0, file_bytes)
        entry['total_files'] = entry.get('total_files', 0) + max(0, file_count)
        entry['last_download_at'] = datetime.now(timezone.utc).isoformat()
        usage[username] = entry
        data[key] = usage
        _save(data)


def get_user_usage(username: str,
                   category: str) -> Dict[str, Any]:
    """Return usage dict for one user and category."""
    key = f'{category}_usage'
    with _lock:
        data = _load()
    entry = data.get(key, {}).get(username)
    if not isinstance(entry, dict):
        return {'total_bytes': 0, 'total_files': 0, 'last_download_at': ''}
    return dict(entry)


def list_all_usage(category: str) -> List[Dict[str, Any]]:
    """Return a list of {username, total_bytes, total_files, last_download_at}
    for every user with recorded usage in *category*."""
    key = f'{category}_usage'
    with _lock:
        data = _load()
    usage = data.get(key, {})
    result = []
    for uname, entry in sorted(usage.items()):
        if not isinstance(entry, dict):
            continue
        result.append({
            'username': uname,
            'total_bytes': entry.get('total_bytes', 0),
            'total_files': entry.get('total_files', 0),
            'last_download_at': entry.get('last_download_at', ''),
        })
    return result


def reset_user_usage(username: str, category: str) -> None:
    """Reset a single user's usage counters for *category*."""
    key = f'{category}_usage'
    with _lock:
        data = _load()
        usage = data.get(key, {})
        if username in usage:
            del usage[username]
            data[key] = usage
            _save(data)


# =============================================================================
# Rate limiting
# =============================================================================
def check_rate_limit(username: str, category: str) -> Optional[float]:
    """Check if user is rate-limited.

    Returns ``None`` if the user may proceed, or the number of seconds
    they must wait before the next download.
    """
    settings = load_settings()
    limit_key = f'{category}_rate_limit_seconds'
    limit_secs = settings.get(limit_key, 0)
    if limit_secs <= 0:
        return None

    entry = get_user_usage(username, category)
    last_str = entry.get('last_download_at', '')
    if not last_str:
        return None

    try:
        last_dt = datetime.fromisoformat(last_str)
        now = datetime.now(timezone.utc)
        elapsed = (now - last_dt).total_seconds()
        if elapsed < limit_secs:
            return round(limit_secs - elapsed, 2)
    except (ValueError, TypeError):
        pass
    return None


# =============================================================================
# Helpers
# =============================================================================
def format_bytes(n: int) -> str:
    """Human-readable byte size."""
    if n < 0:
        n = 0
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}' if unit != 'B' else f'{n} B'
        n /= 1024
    return f'{n:.1f} PB'
