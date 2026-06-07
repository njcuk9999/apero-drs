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
from apero_ri.core.permissions import load_parameters


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


def _configured_instrument_map() -> Dict[str, List[str]]:
    """Return the configured instrument map from parameters.yaml."""
    params = load_parameters() or dict()
    raw_map = params.get('instrument_map', {})
    out: Dict[str, List[str]] = dict()
    if isinstance(raw_map, dict):
        for key, value in raw_map.items():
            map_key = str(key or '').strip().lower()
            if not map_key:
                continue
            if isinstance(value, dict):
                raw_values = value.get('value', [])
            elif isinstance(value, list):
                raw_values = value
            else:
                raw_values = [value]
            aliases = []
            for item in raw_values:
                alias = str(item or '').strip().lower()
                if alias and alias not in aliases:
                    aliases.append(alias)
            if aliases:
                out[map_key] = aliases
    return out


def _profile_instrument_names(profile_data: Optional[dict]) -> List[str]:
    """Return canonical instrument names and aliases for a profile."""
    if not isinstance(profile_data, dict):
        return []

    raw_names = []
    for key in ('INSTRUMENT', 'instrument'):
        raw_names.append(profile_utils.profile_get_general(profile_data,
                                                          key, ''))

    preset_data = profile_data.get('APERO_INSTRUMENT_PROFILE_DATA', {})
    if isinstance(preset_data, dict):
        for key in ('INSTRUMENT', 'instrument'):
            raw_names.append(profile_utils.profile_get_general(preset_data,
                                                              key, ''))

    mapped = []
    inst_map = _configured_instrument_map()
    for raw_name in raw_names:
        name = str(raw_name or '').strip().lower()
        if not name or name in mapped:
            continue
        mapped.append(name)
        for map_key, aliases in inst_map.items():
            if name == map_key or name in aliases:
                if map_key not in mapped:
                    mapped.append(map_key)
                for alias in aliases:
                    if alias not in mapped:
                        mapped.append(alias)
    return mapped


def _extend_root_candidates(base_root: str,
                            profile_data: Optional[dict]) -> List[str]:
    """Return base-root candidates expanded by mapped instrument aliases."""
    if not base_root:
        return []

    root = Path(base_root).expanduser()
    candidates = []
    for instrument in _profile_instrument_names(profile_data):
        lower_path = str(root / instrument)
        upper_path = str(root / instrument.upper())
        if lower_path not in candidates:
            candidates.append(lower_path)
        if upper_path not in candidates:
            candidates.append(upper_path)
    root_str = str(root)
    if root_str not in candidates:
        candidates.append(root_str)
    return candidates


def resolve_checks_root(
    local_data_dir: Path,
    profile_data: Optional[dict] = None,
    configured_root: Optional[str] = None,
) -> Path:
    """Resolve the YAML root directory for APERO checks."""
    candidates: List[str] = []
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

    # The profile-specific PATH.CHECK should be the primary source of truth.
    # Fall back to the persisted config root only when the profile does not
    # define a usable checks directory.
    if configured_root:
        candidates.extend(
            _extend_root_candidates(str(configured_root), profile_data)
        )

    candidates.extend(
        _extend_root_candidates(
            str(Path(local_data_dir) / 'apero_checks'), profile_data
        )
    )

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
    data['passes'] = _normalise_passes(data.get('passes'))
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


def _normalise_passes(raw_passes: Any) -> dict:
    """Normalise the passes mapping."""
    if not isinstance(raw_passes, dict):
        return dict()
    out = dict()
    for key, value in raw_passes.items():
        if not isinstance(value, dict):
            continue
        row = dict(value)
        row['name'] = str(row.get('name') or key).strip()
        row['type'] = str(row.get('type') or 'all').strip().lower()
        row['message'] = str(row.get('message') or '').strip()
        out[str(key)] = row
    return out


def propagate_dependency_states(
    loaded: dict,
    checks_registry: dict,
    ignored_set: Optional[set] = None,
) -> dict:
    """Propagate monitored/overridden state from failing dependencies.

    If check B depends on check A, and check A is in ``failures`` with an
    ``override`` or ``monitor`` event, then check B also inherits that status
    (provided B is not already overridden/monitored).  The failure message is
    replaced with a human-readable explanation.

    Runs up to 5 passes to handle transitive dependency chains
    (e.g. C → B → A where A is monitored propagates to both B and C).

    :param loaded: normalised dict from :func:`load_check_file`.
    :param checks_registry: mapping of check_key → AperoCheck object
                            (e.g. ``MONITOR_CHECKS`` from
                            ``apero_ri.apero_monitoring.checks``).
    :param ignored_set: check keys to skip.
    :return: the same ``loaded`` dict with failures mutated in-place.
    """
    if not isinstance(checks_registry, dict):
        return loaded
    failures = loaded.get('failures')
    if not isinstance(failures, dict):
        return loaded
    skip = set(ignored_set or [])

    for _pass in range(5):
        changed = False
        for check_key, check_row in list(failures.items()):
            if not isinstance(check_row, dict):
                continue
            if check_key in skip:
                continue
            # Skip if already has any override or monitor status.
            if check_row.get('override') or check_row.get('monitor'):
                continue
            check_obj = checks_registry.get(check_key)
            if check_obj is None:
                continue
            deps = list(getattr(check_obj, 'dependencies', []) or [])
            for dep_key in deps:
                dep_row = failures.get(dep_key)
                if not isinstance(dep_row, dict):
                    continue
                dep_override = dep_row.get('override') or {}
                dep_monitor = dep_row.get('monitor') or {}
                if not dep_override and not dep_monitor:
                    continue
                # Dependency is monitored/overridden — inherit its status.
                if dep_override:
                    status_label = 'overridden'
                    inherited_event = dict(dep_override)
                    original_comment = str(dep_override.get('comment') or '')
                else:
                    status_label = 'monitored'
                    inherited_event = dict(dep_monitor)
                    original_comment = str(dep_monitor.get('comment') or '')

                inherited_comment = (
                    'Inherited from dependency %s.' % dep_key
                    + (' Original: ' + original_comment if original_comment else '')
                ).strip()
                inherited_event['comment'] = inherited_comment
                inherited_event['inherited_from'] = dep_key

                new_message = (
                    'Check failed due to failed dependency: %(dep)s '
                    'but this check is %(status)s. '
                    'This check is now %(status)s.'
                ) % {'dep': dep_key, 'status': status_label}

                failures[check_key] = dict(check_row)
                if dep_override:
                    failures[check_key]['override'] = inherited_event
                else:
                    failures[check_key]['monitor'] = inherited_event
                failures[check_key]['message'] = new_message
                changed = True
                break  # only first matching dependency matters per check

        if not changed:
            break  # no more propagation needed

    return loaded


def _normalise_event(value: Any) -> dict:
    """Normalise one override/monitor event mapping."""
    if not isinstance(value, dict):
        return dict()
    date = str(value.get('date') or '').strip()
    user = str(value.get('user') or '').strip()
    source = str(value.get('source') or '').strip()
    comment = str(value.get('comment') or '').strip()
    if not any((date, user, source, comment)):
        return dict()
    out = dict()
    out['date'] = date
    out['user'] = user
    out['source'] = source
    out['comment'] = comment
    return out


def _iso_from_mtime(path_value: str) -> str:
    """Return an ISO UTC timestamp from file mtime, when available."""
    value = str(path_value or '').strip()
    if value == '':
        return ''
    try:
        stat = Path(value).stat()
        stamp = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return stamp.isoformat(timespec='seconds')
    except Exception:
        return ''


def _format_last_run_utc(raw_value: str) -> str:
    """Format a raw datetime-like value as UTC display text."""
    text = str(raw_value or '').strip()
    if text == '':
        return ''
    try:
        value = text.replace('Z', '+00:00')
        dtime = datetime.fromisoformat(value)
        if dtime.tzinfo is None:
            dtime = dtime.replace(tzinfo=timezone.utc)
        else:
            dtime = dtime.astimezone(timezone.utc)
        out = dtime.strftime('%Y-%m-%d %H:%M:%S')
        return out + ' (UTC)'
    except Exception:
        pass
    try:
        dtime = datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
        out = dtime.strftime('%Y-%m-%d %H:%M:%S')
        return out + ' (UTC)'
    except Exception:
        return text


def _latest_history_date(raw_history: Any) -> str:
    """Return the newest non-empty history date string."""
    if not isinstance(raw_history, dict):
        return ''
    dates = []
    for value in raw_history.values():
        if not isinstance(value, dict):
            continue
        date = str(value.get('date') or '').strip()
        if date:
            dates.append(date)
    if not dates:
        return ''
    return sorted(dates)[-1]


def format_last_run_display(raw_value: str) -> str:
    """Public helper to format last-run strings for UI display."""
    return _format_last_run_utc(raw_value)


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
    show_passed: bool = False,
    ignored_checks: Optional[List[str]] = None,
) -> dict:
    """Build one obsdir card summary."""
    ignored_set = set(ignored_checks or CHECK_IGNORED_CHECKS)
    failures = data.get('failures', {})
    passes = data.get('passes', {})
    all_non_ignored = {
        key: value for key, value in failures.items()
        if key not in ignored_set
    }
    override_count = 0
    monitor_count = 0
    active_failure_count = 0
    for failure in all_non_ignored.values():
        has_override = bool((failure or {}).get('override'))
        has_monitor = bool((failure or {}).get('monitor'))
        if has_override:
            override_count += 1
        if has_monitor:
            monitor_count += 1
        if not has_override and not has_monitor:
            active_failure_count += 1

    if active_failure_count > 0:
        status = 'failed'
        result_state = 'failed'
        status_detail = 'failed'
        status_label = 'Failed'
        card_color = 'failed'
    else:
        status = 'ok'
        result_state = 'passed'
        if override_count > 0 and monitor_count > 0:
            status_detail = 'overrides_and_monitoring'
            status_label = 'Passed (with overrides and monitoring)'
            if override_count > monitor_count:
                card_color = 'overridden'
            elif monitor_count > override_count:
                card_color = 'monitored'
            else:
                card_color = 'overridden_monitored'
        elif override_count > 0:
            status_detail = 'overrides'
            status_label = 'Passed (with overrides)'
            card_color = 'overridden'
        elif monitor_count > 0:
            status_detail = 'monitoring'
            status_label = 'Passed (with monitoring)'
            card_color = 'monitored'
        else:
            status_detail = 'passed'
            status_label = 'Passed'
            card_color = 'ok'

    last_run_raw = _latest_history_date(data.get('history', {}))
    if last_run_raw == '':
        last_run_raw = _iso_from_mtime(str(data.get('__path__') or ''))
    last_run = _format_last_run_utc(last_run_raw)
    visible = []
    visible_passes = []
    ignored = []
    for key, failure in failures.items():
        if key in ignored_set:
            ignored.append(key)
            continue
        if failure_is_hidden(
            failure, type_filter, show_overridden, show_monitored
        ):
            continue
        failure_row = dict(failure)
        failure_row['last_run'] = str(last_run)
        visible.append((key, failure_row))

    # Always keep pass rows in the summary payload.
    #
    # The page defaults to hiding passed checks, but the client-side toggle
    # needs the pass data to already exist on the card summary when the user
    # switches that visibility on.
    for key, check in passes.items():
        if key in ignored_set:
            continue
        check_type = str(check.get('type') or '').strip().lower()
        if type_filter and type_filter != 'all' and check_type != type_filter:
            continue
        check_row = dict(check)
        check_row['last_run'] = str(last_run)
        visible_passes.append((key, check_row))

    failed = len(visible)
    return dict(
        obsdir=str(data.get('obsdir') or ''),
        instrument=str(data.get('instrument') or ''),
        profile=str(data.get('profile') or ''),
        path=str(data.get('__path__') or ''),
        last_run=str(last_run),
        history=list(data.get('history', {}).values()),
        visible_failures=visible,
        visible_passes=visible_passes,
        visible_failure_count=failed,
        active_failure_count=active_failure_count,
        visible_pass_count=len(visible_passes),
        ignored_failures=ignored,
        status=status,
        result_state=result_state,
        status_detail=status_detail,
        status_label=status_label,
        override_count=override_count,
        monitor_count=monitor_count,
        card_color=card_color,
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

    # Keep the last comment so UI can prefill if event is re-enabled.
    prev_event = failure.get(event_key)
    last_comment = ''
    if isinstance(prev_event, dict):
        last_comment = str(prev_event.get('comment') or '').strip()
    cache_key = f'{event_key}_last_comment'
    if last_comment:
        failure[cache_key] = last_comment

    failure.pop(event_key, None)
    failures[failure_key] = failure
    data['failures'] = failures
    _safe_write_yaml(path, data)
    return load_check_file(path)


def delete_test_key(path: Path, test_key: str) -> dict:
    """Delete one test key from failures and passes in one YAML file."""
    key = str(test_key or '').strip()
    if key == '':
        return dict(
            changed=False,
            removed_failures=0,
            removed_passes=0,
        )

    data = _safe_load_yaml(path)
    failures = data.get('failures', dict())
    passes = data.get('passes', dict())
    key_upper = key.upper()

    removed_failures = 0
    removed_passes = 0

    if isinstance(failures, dict):
        for current_key in list(failures.keys()):
            if str(current_key or '').strip().upper() != key_upper:
                continue
            failures.pop(current_key, None)
            removed_failures += 1

    if isinstance(passes, dict):
        for current_key in list(passes.keys()):
            if str(current_key or '').strip().upper() != key_upper:
                continue
            passes.pop(current_key, None)
            removed_passes += 1

    changed = (removed_failures + removed_passes) > 0
    if changed:
        data['failures'] = failures if isinstance(failures, dict) else dict()
        data['passes'] = passes if isinstance(passes, dict) else dict()
        _safe_write_yaml(path, data)

    return dict(
        changed=changed,
        removed_failures=removed_failures,
        removed_passes=removed_passes,
    )
