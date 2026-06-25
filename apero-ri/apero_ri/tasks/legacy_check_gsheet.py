#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI - GLOBAL async task: sync legacy check Google Sheet to ARI.

One-way sync: Sheet -> ARI.

OVERRIDES tab (shared across instruments):
  Columns: obsdir, date, test_type, test_name, test_value, who, comment
  Any row where test_value == 'TRUE' and test_name is a known check key
  sets the 'override' event on the matching failure YAML entry.
  Rows are filtered to the current instrument via the test_type column
  (e.g. 'RAW-NIRPS-HE' contains 'NIRPS-HE').

Monitoring tab (one per instrument, e.g. 'Comments-NIRPS-HE'):
  Columns: obsdir, date, Name, Comments - NIRPS-HE
  Any row with a non-empty comment sets the 'monitor' event on ALL
  currently failing, non-overridden checks for that obsdir.

Per-instrument sheet URLs are stored in the aprofile_instruments
YAML under the 'legacy_checks_gsheet' key.  URLs can also be
overridden globally via TASK_CONFIG.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlparse

import yaml

from apero_ri.core.secret_store import get_ari_dir
from apero_ri.tasks import apero_async

# =============================================================================
# Module constants
# =============================================================================
__NAME__ = 'apero_ri.tasks.legacy_check_gsheet'
ARI_DIR = Path.home() / '.ari'

PARAM_LIST = ['LOCAL_DATA_DIR', 'INSTRUMENT', 'TASK_CONFIG']
APERO_PROFILE_PARAM_LIST: List[str] = []
DEFAULT_FREQUENCY = 12.0
DEFAULT_ENABLED = False
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS: List[str] = []

DEFAULT_GOOGLE_SECRET_NAME = 'legacy_gsheet_oauth.json'

_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/spreadsheets',
]

_TASK_SOURCE = 'LEGACY_CHECK_GSHEET'
_TASK_USER = 'legacy_gsheet'

# Translation table: sheet test_name -> ARI check key.
# Keys are matched case-insensitively (after .upper()).
# Extend this dict whenever the sheet uses a different name than ARI.
_TEST_NAME_TRANSLATION: Dict[str, str] = {
    'CRIT_SCI': 'CRITICAL_SCI_TEST',
}


# =============================================================================
# Low-level YAML helpers (avoid importing private apero_checks symbols)
# =============================================================================
def _now_iso() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _read_yaml(path: Path) -> dict:
    """Load a YAML file into a plain dict."""
    if not path.is_file():
        return {}
    with open(path, encoding='utf-8') as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def _write_yaml(path: Path, data: dict) -> None:
    """Atomically write a dict as YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as fh:
        yaml.safe_dump(
            data, fh, sort_keys=False, allow_unicode=True
        )
    tmp.replace(path)


# =============================================================================
# Utility helpers
# =============================================================================
def _as_bool(value: Any) -> bool:
    """Coerce value to bool."""
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in ('1', 'true', 'yes', 'y', 'on')


def _parse_gsheet_url(url: str) -> Tuple[str, int]:
    """Parse a Google Sheets URL into (sheet_id, gid).

    Handles both ?gid= query param and #gid= fragment.
    """
    url = str(url or '').strip()
    parsed = urlparse(url)
    # Extract sheet_id from path: /spreadsheets/d/{sheet_id}/...
    sheet_id = ''
    parts = parsed.path.split('/')
    for i, part in enumerate(parts):
        if part == 'd' and i + 1 < len(parts):
            sheet_id = parts[i + 1]
            break
    # Extract gid from query string
    qs = parse_qs(parsed.query)
    gid_vals = qs.get('gid', [])
    gid = 0
    if gid_vals:
        try:
            gid = int(gid_vals[0])
        except (ValueError, TypeError):
            gid = 0
    # Fallback: fragment (#gid=...)
    if gid == 0 and parsed.fragment:
        frag_parts = parsed.fragment.split('=')
        if len(frag_parts) == 2 and frag_parts[0] == 'gid':
            try:
                gid = int(frag_parts[1])
            except (ValueError, TypeError):
                gid = 0
    return sheet_id, gid


def _normalize_instrument_key(value: str) -> str:
    """Normalize an instrument name for config map lookups."""
    text = str(value or '').strip().upper()
    return text.replace('-', '_')


def _resolve_task_url(
    task_cfg: Dict[str, Any],
    instrument: str,
    single_key: str,
    map_key: str,
) -> str:
    """Resolve per-instrument URL from task config.

    Preference order:
    1) map-based value for this instrument
    2) legacy global scalar value
    """
    normalized = _normalize_instrument_key(instrument)
    url_map = task_cfg.get(map_key)
    if isinstance(url_map, dict):
        value = str(url_map.get(normalized) or '').strip()
        if value:
            return value
    return str(task_cfg.get(single_key) or '').strip()


# =============================================================================
# Google OAuth / gspread helpers (mirrored from legacy_astrom_gsheet)
# =============================================================================
def _load_google_oauth_payload(
    task_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """Load OAuth2 payload from LOCAL_DATA_DIR/admin only."""

    secret_name = str(
        task_cfg.get('google_secret_name', DEFAULT_GOOGLE_SECRET_NAME)
        or DEFAULT_GOOGLE_SECRET_NAME
    ).strip() or DEFAULT_GOOGLE_SECRET_NAME

    secret_path = get_ari_dir() / 'admin' / secret_name

    if secret_path.exists():
        try:
            with open(secret_path, 'r', encoding='utf-8') as fh:
                payload = json.load(fh)
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
    raise FileNotFoundError(
        'Missing Google OAuth secret file. Add credentials to '
        f'{secret_path}. Upload this file in Async Task admin editor.'
    )


def _open_spreadsheet(payload: Dict[str, Any], sheet_id: str):
    """Open a gspread spreadsheet using service-account or OAuth2 credentials."""
    import gspread

    scopes = payload.get('scopes')
    if not isinstance(scopes, list) or not scopes:
        scopes = list(_SCOPES)

    if payload.get('type') == 'service_account':
        from google.oauth2.service_account import Credentials as SACredentials
        creds = SACredentials.from_service_account_info(payload, scopes=scopes)
    else:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        creds = Credentials(
            token=None,
            refresh_token=str(payload.get('refresh_token') or ''),
            token_uri=str(
                payload.get('token_uri')
                or 'https://oauth2.googleapis.com/token'
            ),
            client_id=str(payload.get('client_id') or ''),
            client_secret=str(payload.get('client_secret') or ''),
            scopes=scopes,
        )
        creds.refresh(Request())

    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)


def _open_worksheet_by_gid(spreadsheet, gid: int, label: str):
    """Return the worksheet whose numeric GID matches *gid*."""
    for ws in spreadsheet.worksheets():
        if ws.id == gid:
            return ws
    raise RuntimeError(
        f'Worksheet with gid={gid} ({label}) not found in spreadsheet.'
    )


# =============================================================================
# Sync helpers
# =============================================================================
def _build_obsdir_index(
    checks_root: Path,
) -> Dict[str, Path]:
    """Return dict mapping obsdir -> yaml_path for all check YAMLs."""
    from apero_ri.core.apero_checks import list_yaml_files

    index: Dict[str, Path] = {}
    for yaml_path in list_yaml_files(checks_root):
        # Use file stem as obsdir; matches how load_check_file works.
        obsdir = yaml_path.stem
        index[obsdir] = yaml_path
    return index


def _sync_overrides(
    spreadsheet,
    override_gid: int,
    yaml_by_obsdir: Dict[str, Path],
    monitor_checks: dict,
    instrument_dash: str,
    dry_run: bool,
    tlog,
) -> Tuple[int, int, int]:
    """Apply override events from the OVERRIDES sheet tab.

    Filters rows to the current instrument using the test_type column
    (e.g. 'RAW-NIRPS-HE' contains instrument_dash 'NIRPS-HE').

    Returns (applied, skipped, errors).
    """
    ws = _open_worksheet_by_gid(spreadsheet, override_gid, 'OVERRIDES')
    rows = ws.get_all_records(default_blank='')
    tlog(f'[OVERRIDES] Sheet rows: {len(rows)}')

    # Group valid rows by obsdir to batch YAML reads/writes.
    by_obsdir: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    row_skipped = 0

    for row in rows:
        obsdir = str(row.get('obsdir') or '').strip()
        test_name = str(row.get('test_name') or '').strip().upper()
        test_value = str(row.get('test_value') or '').strip().upper()
        test_type = str(row.get('test_type') or '').strip().upper()
        who = (
            str(row.get('who') or _TASK_USER).strip() or _TASK_USER
        )
        comment = str(row.get('comment') or '').strip()

        if not obsdir or not test_name or test_value != 'TRUE':
            row_skipped += 1
            continue
        # Translate legacy sheet name -> ARI check key if needed.
        test_name = _TEST_NAME_TRANSLATION.get(test_name, test_name)
        # Filter to this instrument only.
        if instrument_dash not in test_type:
            continue
        if test_name not in monitor_checks:
            tlog(
                f'[OVERRIDES] Unknown check {test_name!r} – skipping.'
            )
            row_skipped += 1
            continue
        by_obsdir[obsdir].append((test_name, who, comment))

    applied = 0
    skipped = row_skipped
    errors = 0

    for obsdir, events in by_obsdir.items():
        yaml_path = yaml_by_obsdir.get(obsdir)
        if yaml_path is None:
            tlog(f'[OVERRIDES] No YAML for obsdir={obsdir!r}.')
            skipped += len(events)
            continue

        data = _read_yaml(yaml_path)
        failures = data.get('failures') or {}
        if not isinstance(failures, dict):
            skipped += len(events)
            continue

        changed = False
        for test_name, who, comment in events:
            failure = failures.get(test_name)
            if not isinstance(failure, dict):
                tlog(
                    f'[OVERRIDES] {test_name!r} not in failures '
                    f'for {obsdir!r}.'
                )
                skipped += 1
                continue
            if failure.get('override'):
                # Already overridden – do not overwrite.
                skipped += 1
                continue
            prefix = '(dry-run) ' if dry_run else ''
            tlog(
                f'[OVERRIDES] {prefix}override: '
                f'{obsdir!r}/{test_name!r}'
            )
            if not dry_run:
                failure['override'] = {
                    'date': _now_iso(),
                    'user': who,
                    'source': _TASK_SOURCE,
                    'comment': comment,
                }
                failures[test_name] = failure
                changed = True
            applied += 1

        if changed:
            data['failures'] = failures
            try:
                _write_yaml(yaml_path, data)
            except Exception as exc:
                tlog(f'[OVERRIDES] Write error for {obsdir!r}: {exc}')
                errors += 1

    return applied, skipped, errors


def _sync_monitoring(
    spreadsheet,
    monitoring_gid: int,
    yaml_by_obsdir: Dict[str, Path],
    instrument_dash: str,
    dry_run: bool,
    tlog,
) -> Tuple[int, int, int]:
    """Apply monitor events from the instrument monitoring sheet tab.

    For each row with a non-empty comment, sets the 'monitor' event on
    all currently failing non-overridden checks for that obsdir.

    Returns (applied, skipped, errors).
    """
    ws = _open_worksheet_by_gid(
        spreadsheet, monitoring_gid, 'monitoring'
    )
    rows = ws.get_all_records(default_blank='')
    tlog(f'[MONITORING] Sheet rows: {len(rows)}')

    if not rows:
        tlog('[MONITORING] Sheet is empty.')
        return 0, 0, 0

    # Detect the comments column name dynamically.
    # Expected: 'Comments - NIRPS-HE' or 'Comments - NIRPS-HA'.
    all_columns = list(rows[0].keys())
    target_norm = (
        f'comments - {instrument_dash.lower()}'
    )
    comments_col: Optional[str] = None
    for col in all_columns:
        if col.strip().lower() == target_norm:
            comments_col = col
            break
    if comments_col is None:
        # Fallback: any column that starts with 'comments'.
        for col in all_columns:
            if col.strip().lower().startswith('comments'):
                comments_col = col
                break
    if comments_col is None:
        tlog(
            f'[MONITORING] Comments column not found '
            f'(expected {target_norm!r}). '
            f'Available: {all_columns}'
        )
        return 0, 0, 0

    tlog(f'[MONITORING] Using column: {comments_col!r}')

    applied = 0
    skipped = 0
    errors = 0

    for row in rows:
        obsdir = str(row.get('obsdir') or '').strip()
        comment = str(row.get(comments_col) or '').strip()
        who = (
            str(row.get('Name') or _TASK_USER).strip() or _TASK_USER
        )

        if not obsdir or not comment:
            continue

        yaml_path = yaml_by_obsdir.get(obsdir)
        if yaml_path is None:
            skipped += 1
            continue

        data = _read_yaml(yaml_path)
        failures = data.get('failures') or {}
        if not isinstance(failures, dict):
            skipped += 1
            continue

        changed = False
        for check_key, failure in list(failures.items()):
            if not isinstance(failure, dict):
                continue
            # Skip if already overridden.
            if failure.get('override'):
                continue
            # Skip if monitor event already set.
            if failure.get('monitor'):
                skipped += 1
                continue
            prefix = '(dry-run) ' if dry_run else ''
            tlog(
                f'[MONITORING] {prefix}monitor: '
                f'{obsdir!r}/{check_key!r}'
            )
            if not dry_run:
                failure['monitor'] = {
                    'date': _now_iso(),
                    'user': who,
                    'source': _TASK_SOURCE,
                    'comment': comment,
                }
                failures[check_key] = failure
                changed = True
            applied += 1

        if changed:
            data['failures'] = failures
            try:
                _write_yaml(yaml_path, data)
            except Exception as exc:
                tlog(
                    f'[MONITORING] Write error for {obsdir!r}: '
                    f'{exc}'
                )
                errors += 1

    return applied, skipped, errors


# =============================================================================
# Task class
# =============================================================================
class LegacyCheckGSheetTask(apero_async.AperoAsyncTask):
    """One-way sync from legacy NIRPS check Google Sheets to ARI YAMLs."""

    def __init__(self, status: str = 'pending') -> None:
        name = 'Legacy Check GSheet Sync'
        description = (
            'One-way sync from the NIRPS check Google Sheets '
            '(OVERRIDES tab + per-instrument monitoring tabs) '
            'to the local ARI check YAML files. Processes overrides '
            'first, then monitoring comments. Per-instrument sheet '
            'URLs are read from the aprofile_instruments preset YAML.'
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:  # noqa: C901
        from apero_ri.apero_monitoring import CHECKS as MONITOR_CHECKS
        from apero_ri.core.auth import load_apero_profiles
        from apero_ri.core.apero_checks import resolve_checks_root
        from apero_ri.core.permissions import load_parameters

        task_cfg = dict(params.get('TASK_CONFIG') or {})
        dry_run = _as_bool(
            task_cfg.get('DRY_RUN', task_cfg.get('dry_run'))
        )
        local_data_dir = Path(
            params.get('LOCAL_DATA_DIR', str(ARI_DIR))
        ).expanduser().resolve()

        task_logger = params.get('TASK_LOGGER')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        tlog(f'{_TASK_SOURCE} start.')
        tlog(f'Mode: {"DRY_RUN" if dry_run else "APPLY"}')
        tlog(f'Local data dir: {local_data_dir}')

        # Load configured checks root (global default).
        params_cfg = load_parameters()
        checks_cfg = dict(
            params_cfg.get('apero_check', {}) or {}
        )
        configured_root = str(
            checks_cfg.get('checks_root', '') or ''
        ).strip()

        payload = _load_google_oauth_payload(task_cfg)
        self.progress = 0.0

        # ---- iterate over all hydrated profiles -------------------------
        all_profiles = load_apero_profiles(
            hydrate=True,
            enabled_only=True,
        )
        total_applied = 0
        total_skipped = 0
        total_errors = 0

        # De-duplicate (instrument, checks_root) pairs already processed.
        processed: Set[Tuple[str, str]] = set()

        instr_count = 0
        for instrument, instr_profiles in all_profiles.items():
            if not isinstance(instr_profiles, dict):
                continue
            for profile_id, profile_data in instr_profiles.items():
                if not isinstance(profile_data, dict):
                    continue

                # Resolve checks root for this profile.
                checks_root = Path(
                    resolve_checks_root(
                        local_data_dir,
                        profile_data,
                        configured_root,
                    )
                )

                pair_key = (
                    str(instrument).upper(),
                    str(checks_root),
                )
                if pair_key in processed:
                    continue

                # Get per-instrument gsheet config from preset.
                preset_data = (
                    profile_data.get('APERO_INSTRUMENT_PROFILE_DATA')
                    or {}
                )
                if not isinstance(preset_data, dict):
                    preset_data = {}
                gsheet_cfg = preset_data.get('legacy_checks_gsheet')
                if not isinstance(gsheet_cfg, dict):
                    gsheet_cfg = {}

                # URLs: preset first, then task_cfg fallback.
                monitoring_url = (
                    str(
                        gsheet_cfg.get('monitoring_sheet_url') or ''
                    ).strip()
                    or _resolve_task_url(
                        task_cfg,
                        str(instrument),
                        'monitoring_sheet_url',
                        'monitoring_sheet_urls',
                    )
                )
                override_url = (
                    str(
                        gsheet_cfg.get('override_sheet_url') or ''
                    ).strip()
                    or _resolve_task_url(
                        task_cfg,
                        str(instrument),
                        'override_sheet_url',
                        'override_sheet_urls',
                    )
                )

                if not monitoring_url or not override_url:
                    tlog(
                        f'[{instrument}] No sheet URLs configured – '
                        'skipping.'
                    )
                    processed.add(pair_key)
                    continue

                tlog(
                    f'[{instrument}] profile={profile_id!r} '
                    f'checks_root={checks_root}'
                )

                # Parse sheet IDs and GIDs.
                over_sheet_id, over_gid = _parse_gsheet_url(
                    override_url
                )
                mon_sheet_id, mon_gid = _parse_gsheet_url(
                    monitoring_url
                )

                if not over_sheet_id or not mon_sheet_id:
                    tlog(
                        f'[{instrument}] Could not parse sheet URLs.'
                    )
                    processed.add(pair_key)
                    continue

                tlog(
                    f'[{instrument}] Override sheet_id={over_sheet_id}'
                    f' gid={over_gid}'
                )
                tlog(
                    f'[{instrument}] Monitoring sheet_id='
                    f'{mon_sheet_id} gid={mon_gid}'
                )

                # instrument_dash: 'NIRPS_HE' -> 'NIRPS-HE'
                instrument_dash = (
                    str(instrument).upper().replace('_', '-')
                )

                # Build obsdir -> yaml_path index once.
                yaml_by_obsdir = _build_obsdir_index(checks_root)
                tlog(
                    f'[{instrument}] YAML index: '
                    f'{len(yaml_by_obsdir)} entries'
                )

                # Open the override spreadsheet.
                try:
                    over_spreadsheet = _open_spreadsheet(
                        payload, over_sheet_id
                    )
                except Exception as exc:
                    tlog(
                        f'[{instrument}] Cannot open override '
                        f'spreadsheet: {exc}'
                    )
                    processed.add(pair_key)
                    total_errors += 1
                    continue

                # Open the monitoring spreadsheet (may be same file).
                if mon_sheet_id == over_sheet_id:
                    mon_spreadsheet = over_spreadsheet
                else:
                    try:
                        mon_spreadsheet = _open_spreadsheet(
                            payload, mon_sheet_id
                        )
                    except Exception as exc:
                        tlog(
                            f'[{instrument}] Cannot open monitoring '
                            f'spreadsheet: {exc}'
                        )
                        processed.add(pair_key)
                        total_errors += 1
                        continue

                # 1) Sync OVERRIDES first.
                try:
                    ov_a, ov_s, ov_e = _sync_overrides(
                        spreadsheet=over_spreadsheet,
                        override_gid=over_gid,
                        yaml_by_obsdir=yaml_by_obsdir,
                        monitor_checks=MONITOR_CHECKS,
                        instrument_dash=instrument_dash,
                        dry_run=dry_run,
                        tlog=tlog,
                    )
                    tlog(
                        f'[{instrument}] OVERRIDES: '
                        f'applied={ov_a} skipped={ov_s} errors={ov_e}'
                    )
                    total_applied += ov_a
                    total_skipped += ov_s
                    total_errors += ov_e
                except Exception as exc:
                    tlog(
                        f'[{instrument}] OVERRIDES sync failed: {exc}'
                    )
                    total_errors += 1

                # 2) Sync MONITORING second.
                # Reload the index so monitoring sees new overrides.
                yaml_by_obsdir = _build_obsdir_index(checks_root)
                try:
                    mo_a, mo_s, mo_e = _sync_monitoring(
                        spreadsheet=mon_spreadsheet,
                        monitoring_gid=mon_gid,
                        yaml_by_obsdir=yaml_by_obsdir,
                        instrument_dash=instrument_dash,
                        dry_run=dry_run,
                        tlog=tlog,
                    )
                    tlog(
                        f'[{instrument}] MONITORING: '
                        f'applied={mo_a} skipped={mo_s} errors={mo_e}'
                    )
                    total_applied += mo_a
                    total_skipped += mo_s
                    total_errors += mo_e
                except Exception as exc:
                    tlog(
                        f'[{instrument}] MONITORING sync failed: {exc}'
                    )
                    total_errors += 1

                processed.add(pair_key)
                instr_count += 1
                self.progress = min(
                    0.99,
                    instr_count / max(1, len(all_profiles)),
                )

        tlog(
            f'{_TASK_SOURCE} complete. '
            f'total_applied={total_applied} '
            f'total_skipped={total_skipped} '
            f'total_errors={total_errors}'
        )
        self.progress = 1.0


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
