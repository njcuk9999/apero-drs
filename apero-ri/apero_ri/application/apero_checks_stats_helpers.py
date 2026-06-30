#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI – APERO-checks stats API and view helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import jsonify, render_template
from flask import session, redirect, url_for, flash

from apero_ri.application.monitor_view_helpers import (
    _has_any_monitor_perm,
    _can_manage_apero_profiles,
    _checks_root_for_profile,
)
from apero_ri.core import apero_checks as checks_core
from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
)
from apero_ri.core.auth import get_effective_user
from apero_ri.core.permissions import resolve_user_permissions


STATS_CACHE_SCHEMA = 1
STATS_CACHE_SUBDIR = Path('cache') / 'apero_checks_stats'


# =============================================================================
# Define helper functions
# =============================================================================

def _parse_file_date(raw: str) -> datetime | None:
    """Parse a 'YYYY-MM-DD HH:MM:SS' string into a UTC datetime."""
    value = str(raw or '').strip()
    if not value:
        return None
    # Try with time component first, then date-only.
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _midpoint_date(first_raw: str, last_raw: str) -> datetime | None:
    """Return the midpoint datetime between first and last file dates."""
    first = _parse_file_date(first_raw)
    last = _parse_file_date(last_raw)
    if first is None and last is None:
        return None
    if first is None:
        return last
    if last is None:
        return first
    delta = last - first
    return first + timedelta(seconds=delta.total_seconds() / 2.0)


def _bin_key(dt: datetime, bin_by: str) -> str:
    """Return a string bin key for a datetime."""
    mode = str(bin_by or 'month').strip().lower()
    if mode == 'week':
        # ISO week: YYYY-Www
        iso = dt.isocalendar()
        return f'{iso[0]:04d}-W{iso[1]:02d}'
    if mode == 'year':
        return str(dt.year)
    # Default: month
    return dt.strftime('%Y-%m')


def _stats_cache_path(
    local_data_dir: Path,
    profile_id: str,
    bin_by: str,
) -> Path:
    """Return the JSON cache path for one profile/bin combination."""
    safe_profile = str(profile_id or '').strip().replace('/', '_')
    safe_bin = str(bin_by or 'month').strip().lower()
    filename = f'{safe_profile}_{safe_bin}.json'
    return Path(local_data_dir) / STATS_CACHE_SUBDIR / filename


def _build_stats_signature(
    checks_root: Path,
    files: list[Path],
    ignored_checks: list[str],
) -> dict:
    """Build a source signature for cache invalidation."""
    digest = hashlib.sha1()
    digest.update(str(checks_root).encode('utf-8'))

    for check_key in sorted({str(v).strip() for v in ignored_checks}):
        if not check_key:
            continue
        digest.update(f'ign:{check_key}'.encode('utf-8'))

    for path in sorted(files, key=lambda p: str(p)):
        try:
            stat = path.stat()
        except OSError:
            continue
        path_key = str(path)
        digest.update(path_key.encode('utf-8'))
        digest.update(str(int(stat.st_mtime_ns)).encode('utf-8'))
        digest.update(str(int(stat.st_size)).encode('utf-8'))

    signature = dict()
    signature['schema'] = STATS_CACHE_SCHEMA
    signature['hash'] = digest.hexdigest()
    signature['file_count'] = len(files)
    return signature


def _load_stats_cache(cache_path: Path, signature: dict) -> dict | None:
    """Load cache payload if it matches the current source signature."""
    if not cache_path.exists() or not cache_path.is_file():
        return None

    try:
        with open(cache_path, 'r', encoding='utf-8') as handle:
            data = json.load(handle) or dict()
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    cached_sig = data.get('signature', {})
    payload = data.get('payload', {})
    if not isinstance(cached_sig, dict) or not isinstance(payload, dict):
        return None

    if cached_sig != signature:
        return None

    return payload


def _save_stats_cache(cache_path: Path, signature: dict, payload: dict) -> None:
    """Persist stats cache atomically."""
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache_path.with_suffix(cache_path.suffix + '.tmp')
        data = dict(signature=signature, payload=payload)
        with open(tmp, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False)
        tmp.replace(cache_path)
    except Exception:
        # Cache failures should never break API responses.
        return


def _compute_obsdir_stats(files, ignored_checks, bin_by):
    """Compute per-obs-dir summary stats and histogram bins.

    Returns a dict with:
      - counts: {passed, failed, overridden, monitored, total}
      - histogram: list of {bin, passed, failed, overridden, monitored}
        sorted by bin key
    """
    # Overall counters
    n_passed = 0
    n_failed = 0
    n_overridden = 0
    n_monitored = 0

    # Histogram accumulator: bin_key -> {passed, failed, ...}
    bins: dict = {}

    ignored_set = set(ignored_checks or [])

    for path in files:
        try:
            data = checks_core.load_check_file(path)
        except Exception:
            continue

        failures = data.get('failures', {})
        passes = data.get('passes', {})

        # Determine obsdir-level status
        has_active_failure = False
        has_override = False
        has_monitor = False

        for key, failure in failures.items():
            if key in ignored_set:
                continue
            is_ov = bool((failure or {}).get('override'))
            is_mo = bool((failure or {}).get('monitor'))
            has_override = has_override or is_ov
            has_monitor = has_monitor or is_mo
            if not is_ov and not is_mo:
                has_active_failure = True

        # Also check passes for override/monitor markers
        for key, passed_item in passes.items():
            if key in ignored_set:
                continue
            has_override = has_override or bool(
                (passed_item or {}).get('override')
            )
            has_monitor = has_monitor or bool(
                (passed_item or {}).get('monitor')
            )

        if has_active_failure:
            n_failed += 1
        else:
            n_passed += 1
        if has_override:
            n_overridden += 1
        if has_monitor:
            n_monitored += 1

        # Determine date for histogram from midpoint
        first_raw = str(data.get('first file') or '').strip()
        last_raw = str(data.get('last file') or '').strip()
        mid = _midpoint_date(first_raw, last_raw)
        if mid is None:
            continue

        bk = _bin_key(mid, bin_by)
        if bk not in bins:
            bins[bk] = dict(
                bin=bk,
                passed=0,
                failed=0,
                overridden=0,
                monitored=0,
            )
        if has_active_failure:
            bins[bk]['failed'] += 1
        else:
            bins[bk]['passed'] += 1
        if has_override:
            bins[bk]['overridden'] += 1
        if has_monitor:
            bins[bk]['monitored'] += 1

    histogram = sorted(bins.values(), key=lambda row: row['bin'])

    counts = dict(
        passed=n_passed,
        failed=n_failed,
        overridden=n_overridden,
        monitored=n_monitored,
        total=n_passed + n_failed,
    )
    return dict(counts=counts, histogram=histogram)


def _compute_checks_stats(files, ignored_checks, bin_by):
    """Compute per-check-key summary stats and histogram bins.

    Returns a dict with:
      - checks: dict of check_key ->
          {name, passed, failed, overridden, monitored}
      - histogram_by_check: dict of check_key ->
          list of {bin, passed, failed, overridden, monitored}
      - check_keys: sorted list of all seen check keys
    """
    # Per-check counters: check_key -> {name, passed, failed, ...}
    check_counts: dict = {}

    # Per-check histogram: check_key -> bin_key -> {passed, failed, ...}
    check_bins: dict = {}

    ignored_set = set(ignored_checks or [])

    for path in files:
        try:
            data = checks_core.load_check_file(path)
        except Exception:
            continue

        failures = data.get('failures', {})
        passes = data.get('passes', {})

        # Determine date for histogram from midpoint
        first_raw = str(data.get('first file') or '').strip()
        last_raw = str(data.get('last file') or '').strip()
        mid = _midpoint_date(first_raw, last_raw)

        # Process failures
        for key, failure in failures.items():
            if key in ignored_set:
                continue
            name = str((failure or {}).get('name') or key).strip()
            is_ov = bool((failure or {}).get('override'))
            is_mo = bool((failure or {}).get('monitor'))
            is_active = not is_ov and not is_mo

            if key not in check_counts:
                check_counts[key] = dict(
                    name=name,
                    passed=0,
                    failed=0,
                    overridden=0,
                    monitored=0,
                )
            else:
                # Keep most recent non-empty name
                if name and name != key:
                    check_counts[key]['name'] = name

            if is_active:
                check_counts[key]['failed'] += 1
            if is_ov:
                check_counts[key]['overridden'] += 1
            if is_mo:
                check_counts[key]['monitored'] += 1

            if mid is None:
                continue
            bk = _bin_key(mid, bin_by)
            if key not in check_bins:
                check_bins[key] = {}
            if bk not in check_bins[key]:
                check_bins[key][bk] = dict(
                    bin=bk,
                    passed=0,
                    failed=0,
                    overridden=0,
                    monitored=0,
                )
            if is_active:
                check_bins[key][bk]['failed'] += 1
            if is_ov:
                check_bins[key][bk]['overridden'] += 1
            if is_mo:
                check_bins[key][bk]['monitored'] += 1

        # Process passes
        for key, passed_item in passes.items():
            if key in ignored_set:
                continue
            name = str((passed_item or {}).get('name') or key).strip()

            if key not in check_counts:
                check_counts[key] = dict(
                    name=name,
                    passed=0,
                    failed=0,
                    overridden=0,
                    monitored=0,
                )
            else:
                if name and name != key:
                    check_counts[key]['name'] = name

            check_counts[key]['passed'] += 1

            if mid is None:
                continue
            bk = _bin_key(mid, bin_by)
            if key not in check_bins:
                check_bins[key] = {}
            if bk not in check_bins[key]:
                check_bins[key][bk] = dict(
                    bin=bk,
                    passed=0,
                    failed=0,
                    overridden=0,
                    monitored=0,
                )
            check_bins[key][bk]['passed'] += 1

    # Compile sorted histograms per check
    histogram_by_check = {}
    for key, bin_map in check_bins.items():
        histogram_by_check[key] = sorted(
            bin_map.values(), key=lambda row: row['bin']
        )

    check_keys = sorted(check_counts.keys())

    return dict(
        checks=check_counts,
        histogram_by_check=histogram_by_check,
        check_keys=check_keys,
    )


# =============================================================================
# Define API functions
# =============================================================================

def api_apero_checks_stats(app, profile_id):
    """Return obsdir and per-check stats for a profile as JSON.

    Query parameters:
      - bin_by: 'week', 'month' (default), or 'year'
    """
    from flask import request as flask_request
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()

    if not _has_any_monitor_perm(perms):
        return jsonify(success=False, error='Monitor access required'), 403

    # Resolve the profile
    profile = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            profile = item
            break
    if profile is None:
        return (
            jsonify(
                success=False,
                error='Profile not found or access denied',
            ),
            404,
        )

    bin_by = str(
        flask_request.args.get('bin_by', 'month') or 'month'
    ).strip().lower()
    if bin_by not in {'week', 'month', 'year'}:
        bin_by = 'month'

    # Load all YAML files for this profile
    checks_root = _checks_root_for_profile(app, profile['data'])
    local_data_dir = app._resolve_local_data_dir()
    ignored_checks = checks_core.load_ignored_checks(local_data_dir)
    files = checks_core.list_yaml_files(checks_root)

    signature = _build_stats_signature(
        checks_root,
        files,
        ignored_checks,
    )
    cache_path = _stats_cache_path(local_data_dir, profile_id, bin_by)
    cached_payload = _load_stats_cache(cache_path, signature)
    if cached_payload is not None:
        out = dict(cached_payload)
        out['cached'] = True
        return jsonify(**out)

    obsdir_stats = _compute_obsdir_stats(files, ignored_checks, bin_by)
    checks_stats = _compute_checks_stats(files, ignored_checks, bin_by)

    payload = dict(
        success=True,
        profile_id=profile_id,
        bin_by=bin_by,
        total_obsdirs=len(files),
        obsdir=obsdir_stats,
        checks=checks_stats,
    )
    _save_stats_cache(cache_path, signature, payload)

    out = dict(payload)
    out['cached'] = False
    return jsonify(**out)


# =============================================================================
# Define view function
# =============================================================================

def monitor_apero_checks_stats_view(app, profile_id):
    """Render the APERO-checks stats page for one profile.

    The page renders immediately as a skeleton; JS fetches the stats
    API asynchronously so the page load is never blocked by computation.
    """
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()

    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    prof = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            prof = item
            break
    if prof is None:
        flash('Profile not found or access denied.', 'warning')
        return redirect(url_for('monitor_apero_checks_view'))

    page_id = (
        f'home.monitor_portal.apero_checks.{profile_id}'
    )
    sidebar_page_id = 'home.monitor_portal.apero_checks'
    context = dict()
    context['page_id'] = page_id
    context['page_label'] = f'APERO Checks Stats – {profile_id}'
    context['page_icon'] = 'fa-solid fa-chart-bar'
    context['sidebar_root'] = 'home.monitor_portal'
    context['sidebar_label'] = 'Monitor Portal'
    context['sidebar_icon'] = 'fa-solid fa-chart-line'
    context['sidebar_url'] = '/monitor_portal'
    context['profile_id'] = profile_id
    context['profile_back_url'] = url_for(
        'monitor_apero_checks_profile_view',
        profile_id=profile_id,
    )
    context['stats_api_url'] = (
        f'/api/monitor/apero-checks/{profile_id}/stats'
    )
    context['can_manage_apero_profiles'] = (
        _can_manage_apero_profiles(perms)
    )

    try:
        context.update(
            app._build_sidebar_context(
                sidebar_page_id, perms, user_info
            )
        )
    except Exception:
        pass

    return render_template(
        'monitor_portal/apero_checks_stats.html',
        **context,
    )
