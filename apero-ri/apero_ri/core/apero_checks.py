#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI APERO-check YAML helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from apero_ri.application import profile_utils


CHECK_IGNORED_CHECKS = {'BAD_CCF'}
CHECK_IGNORED_TESTS = CHECK_IGNORED_CHECKS
CHECK_OVERRIDE_ALLOWED = set()
CONFIG_SUBDIR = 'monitor_apero_checks'
CONFIG_FILENAME = 'config.json'


def _now_iso() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _safe_load_yaml(path: Path) -> dict:
    """Load a YAML file into a dict."""
    if not path.exists() or not path.is_file():
        return dict()
    with open(path, encoding='utf-8') as handle:
        data = yaml.safe_load(handle) or dict()
    if isinstance(data, dict):
        return data
    return dict()


def _safe_write_yaml(path: Path, data: dict) -> None:
    """Write YAML atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
    tmp_path.replace(path)


def _config_dir(local_data_dir: Path) -> Path:
    """Return the APERO-checks config directory."""
    return Path(local_data_dir) / CONFIG_SUBDIR


def config_path(local_data_dir: Path) -> Path:
    """Return the config file path."""
    return _config_dir(local_data_dir) / CONFIG_FILENAME


def load_config(local_data_dir: Path) -> dict:
    """Load persisted checks configuration."""
    path = config_path(local_data_dir)
    if not path.exists() or not path.is_file():
        return dict()
    try:
        with open(path, encoding='utf-8') as handle:
            data = json.load(handle) or dict()
    except Exception:
        return dict()
    return data if isinstance(data, dict) else dict()


def save_config(local_data_dir: Path, data: dict) -> None:
    """Persist checks configuration."""
    cfg_dir = _config_dir(local_data_dir)
    cfg_dir.mkdir(parents=True, exist_ok=True)
    path = config_path(local_data_dir)
    tmp_path = path.with_suffix('.json.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
    tmp_path.replace(path)


def _normalize_ignored_checks(raw_checks: Any) -> List[str]:
    """Normalize ignored checks into a sorted list of unique keys."""
    if not isinstance(raw_checks, list):
        return sorted(CHECK_IGNORED_CHECKS)
    checks = {
        str(item).strip()
        for item in raw_checks
        if str(item).strip()
    }
    if not checks:
        checks = set(CHECK_IGNORED_CHECKS)
    return sorted(checks)


def _normalize_override_allowed(raw_checks: Any) -> List[str]:
    """Normalize override-allowed checks into a sorted unique list."""
    if not isinstance(raw_checks, list):
        return sorted(CHECK_OVERRIDE_ALLOWED)
    checks = {
        str(item).strip()
        for item in raw_checks
        if str(item).strip()
    }
    if not checks:
        checks = set(CHECK_OVERRIDE_ALLOWED)
    return sorted(checks)


def load_ignored_checks(local_data_dir: Path) -> List[str]:
    """Load the ignored-check list from config or fall back to defaults."""
    cfg = load_config(local_data_dir)
    return _normalize_ignored_checks(cfg.get('ignored_checks', []))


def load_override_allowed(local_data_dir: Path) -> List[str]:
    """Load override-allowed check keys from config."""
    cfg = load_config(local_data_dir)
    return _normalize_override_allowed(cfg.get('override_allowed', []))


def resolve_checks_root(
    local_data_dir: Path,
    profile_data: Optional[dict] = None,
    configured_root: Optional[str] = None,
) -> Path:
    """Resolve the YAML root directory for APERO checks."""
    candidates: List[str] = []
    if configured_root:
        candidates.append(str(configured_root))

    if isinstance(profile_data, dict):
        for key in (
            'PATH.CHECK',
            'PATH_CHECK',
            'PATHCHECK',
            'CHECK',
            'PATH.OTHER',
            'PATH_OTHER',
            'PATHOTHER',
            'OTHER',
        ):
            try:
                value = profile_utils.profile_get_path(profile_data, key, '')
            except Exception:
                value = ''
            if value:
                candidates.append(str(value))

    candidates.append(str(Path(local_data_dir) / 'apero_checks'))

    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if path.exists() or path.parent.exists():
            return path
    return Path(candidates[-1]).expanduser()


def list_yaml_files(root_dir: Path) -> List[Path]:
    """Return every YAML file under the checks root."""
    if not root_dir.exists() or not root_dir.is_dir():
        return []
    files = []
    for path in root_dir.rglob('*'):
        if not path.is_file():
            continue
        suffix = str(path.suffix or '').lower()
        if suffix in {'.yaml', '.yml'}:
            files.append(path)
    return sorted({path.resolve() for path in files}, key=str)


def load_check_file(path: Path) -> dict:
    """Load and normalise one check YAML file."""
    data = _safe_load_yaml(path)
    if not data:
        data = dict()
    data['__path__'] = str(path)
    data['obsdir'] = str(data.get('obsdir') or path.stem)
    data['instrument'] = str(data.get('instrument') or '').strip()
    data['profile'] = str(data.get('profile') or '').strip()
    data['history'] = _normalise_history(data.get('history'))
    data['failures'] = _normalise_failures(data.get('failures'))
    return data


def _normalise_history(raw_history: Any) -> dict:
    """Normalise history into a dict keyed by history entry ids."""
    if not isinstance(raw_history, dict):
        return dict()
    out = dict()
    for key, value in raw_history.items():
        if not isinstance(value, dict):
            continue
        out[str(key)] = dict(value)
    return out


def _normalise_failures(raw_failures: Any) -> dict:
    """Normalise the failures mapping."""
    if not isinstance(raw_failures, dict):
        return dict()
    out = dict()
    for key, value in raw_failures.items():
        if not isinstance(value, dict):
            continue
        row = dict(value)
        row['name'] = str(row.get('name') or key).strip()
        row['type'] = str(row.get('type') or 'all').strip().lower()
        row['message'] = str(row.get('message') or '').strip()
        row['override'] = _normalise_event(row.get('override'))
        row['monitor'] = _normalise_event(row.get('monitor'))
        out[str(key)] = row
    return out


def _normalise_event(value: Any) -> dict:
    """Normalise one override/monitor event mapping."""
    if not isinstance(value, dict):
        return dict()
    out = dict()
    out['date'] = str(value.get('date') or '').strip()
    out['user'] = str(value.get('user') or '').strip()
    out['source'] = str(value.get('source') or '').strip()
    out['comment'] = str(value.get('comment') or '').strip()
    return out


def failure_is_hidden(
    failure: dict,
    type_filter: str,
    show_overridden: bool,
    show_monitored: bool,
) -> bool:
    """Return True when a failure should be hidden by filters."""
    failure_type = str(failure.get('type') or '').strip().lower()
    if type_filter and type_filter != 'all' and failure_type != type_filter:
        return True
    if not show_overridden and failure.get('override'):
        return True
    if not show_monitored and failure.get('monitor'):
        return True
    return False


def build_obsdir_summary(
    data: dict,
    type_filter: str = 'all',
    show_overridden: bool = False,
    show_monitored: bool = False,
    ignored_checks: Optional[List[str]] = None,
) -> dict:
    """Build one obsdir card summary."""
    ignored_set = set(ignored_checks or CHECK_IGNORED_CHECKS)
    failures = data.get('failures', {})
    visible = []
    ignored = []
    for key, failure in failures.items():
        if key in ignored_set:
            ignored.append(key)
            continue
        if failure_is_hidden(
            failure, type_filter, show_overridden, show_monitored
        ):
            continue
        visible.append((key, failure))

    failed = len(visible)
    return dict(
        obsdir=str(data.get('obsdir') or ''),
        instrument=str(data.get('instrument') or ''),
        profile=str(data.get('profile') or ''),
        path=str(data.get('__path__') or ''),
        history=list(data.get('history', {}).values()),
        visible_failures=visible,
        visible_failure_count=failed,
        ignored_failures=ignored,
        status='ok' if failed == 0 else 'failed',
    )


def paginate_items(
    items: List[dict],
    page: int,
    per_page: int,
) -> Tuple[List[dict], int]:
    """Paginate a list of items."""
    if per_page <= 0:
        return list(items), 1
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages


def update_failure_event(
    path: Path,
    failure_key: str,
    event_key: str,
    username: str,
    comment: str,
) -> dict:
    """Update one failure override/monitor event and save the file."""
    data = _safe_load_yaml(path)
    failures = data.get('failures', {})
    failure = failures.get(failure_key)
    if not isinstance(failure, dict):
        raise KeyError(f'Unknown failure: {failure_key}')

    failure[event_key] = dict(
        date=_now_iso(),
        user=str(username or 'anonymous').strip() or 'anonymous',
        source='ARI',
        comment=str(comment or '').strip(),
    )
    failures[failure_key] = failure
    data['failures'] = failures
    _safe_write_yaml(path, data)
    return load_check_file(path)


def clear_failure_event(path: Path, failure_key: str, event_key: str) -> dict:
    """Clear one failure event and save the file."""
    data = _safe_load_yaml(path)
    failures = data.get('failures', {})
    failure = failures.get(failure_key)
    if not isinstance(failure, dict):
        raise KeyError(f'Unknown failure: {failure_key}')
    failure.pop(event_key, None)
    failures[failure_key] = failure
    data['failures'] = failures
    _safe_write_yaml(path, data)
    return load_check_file(path)
