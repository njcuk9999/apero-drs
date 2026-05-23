#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI - GLOBAL async task: sync legacy astrometrics Google Sheet.

This task keeps the v0.7 legacy astrometrics Google Sheet and the local
ARI astrometric YAML store synchronized in both directions.

Direction 1: ARI -> Sheet
- Any ARI astrometric entry missing from the legacy sheet is appended to the
  sheet pending-list tab.

Direction 2: Sheet -> ARI
- Any legacy sheet entry missing from ARI is resolved via drs_astrometrics
  online resolver and written under pending/ in ARI.
- A monitor issue is raised with kind='astrometric' and type='legacy' so a
  moderator can confirm the imported target.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

import pandas as pd

from apero_ri.tasks import apero_async


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.legacy_astrom_gsheet'
ARI_DIR = Path.home() / '.ari'

PARAM_LIST = ['LOCAL_DATA_DIR', 'INSTRUMENT', 'TASK_CONFIG']
APERO_PROFILE_PARAM_LIST: List[str] = []
DEFAULT_FREQUENCY = 24.0
DEFAULT_ENABLED = False
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS: List[str] = []

DEFAULT_ASTROM_SHEET_ID = '1dOogfEwC7wAagjVFdouB1Y1JdF9Eva4uDW6CTZ8x2FM'
DEFAULT_ASTROM_SHEET_NAME = 'pending_list'
DEFAULT_ASTROM_MAIN_SHEET_NAMES = ['main', 'main_list']
DEFAULT_ASTROM_PENDING_SHEET_NAMES = ['pending_list', 'pending']

DEFAULT_GOOGLE_SECRET_NAME = 'legacy_gsheet_oauth.json'
DEFAULT_GSP_CLIENT_ID = (
    '241559402076-vbo2eu8sl64ehur7'
    'n1qhqb0q9pfb5hei.apps.googleusercontent.com'
)
DEFAULT_GSP_PROJECT_ID = 'apero-data-manag-1602517149890'
DEFAULT_GSP_CLIENT_SECRET = 'OE4_WF0Btk29Gmb8SrbTJ3UF'
DEFAULT_GSP_REFRESH_TOKEN = (
    '1//0dBWyhNqcGHgdCgYIARAAGA0SNwF-L9IrhXoPCjWJtD4f0EDxA'
    'gFX75Q-f5TOfO1VQNFgSFQ_89IW7trN3B4I0UYvvbVfrGRXZZg'
)

_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/spreadsheets',
]

_ASTROM_LEGACY_COLUMNS = [
    'OBJNAME',
    'ORIGINAL_NAME',
    'ALIASES',
    'RA_DEG',
    'RA_SOURCE',
    'DEC_DEG',
    'DEC_SOURCE',
    'EPOCH',
    'PMRA',
    'PMRA_SOURCE',
    'PMDE',
    'PMDE_SOURCE',
    'PLX',
    'PLX_SOURCE',
    'RV',
    'RV_SOURCE',
    'TEFF',
    'TEFF_SOURCE',
    'SP_TYPE',
    'SP_SOURCE',
    'NOTES',
    'USED',
]


# =============================================================================
# Define helpers
# =============================================================================
def _normalize_name(value: Any) -> str:
    text = str(value or '').strip().upper()
    if not text:
        return ''
    return ''.join(ch for ch in text if ch.isalnum())


def _split_aliases(value: Any) -> List[str]:
    if isinstance(value, (list, tuple)):
        raw_values = list(value)
    else:
        raw_values = str(value or '').split('|')
    out: List[str] = []
    seen: Set[str] = set()
    for raw in raw_values:
        alias = str(raw or '').strip()
        if not alias:
            continue
        low = alias.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(alias)
    return out


def _dedupe_names(values: Sequence[Any]) -> List[str]:
    out: List[str] = []
    seen: Set[str] = set()
    for value in values:
        text = str(value or '').strip()
        if not text:
            continue
        low = text.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(text)
    return out


def _as_float(value: Any) -> Optional[float]:
    text = str(value or '').strip()
    if text in ['', 'None', 'none', 'null', 'nan']:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in ['1', 'true', 'yes', 'y', 'on']


def _nested_value(entry: Dict[str, Any], key: str) -> Any:
    value = entry.get(key)
    if isinstance(value, dict):
        return value.get('value')
    return value


def _nested_source(entry: Dict[str, Any], key: str) -> str:
    value = entry.get(key)
    if isinstance(value, dict):
        return str(value.get('source') or '')
    return ''


def _legacy_oauth_default_payload() -> Dict[str, Any]:
    payload = dict()
    payload['client_id'] = DEFAULT_GSP_CLIENT_ID
    payload['project_id'] = DEFAULT_GSP_PROJECT_ID
    payload['client_secret'] = DEFAULT_GSP_CLIENT_SECRET
    payload['refresh_token'] = DEFAULT_GSP_REFRESH_TOKEN
    payload['token_uri'] = 'https://oauth2.googleapis.com/token'
    payload['scopes'] = list(_SCOPES)
    return payload


def _load_google_oauth_payload(task_cfg: Dict[str, Any]) -> Dict[str, Any]:
    from apero_ri.core import secret_store as ss

    cfg_payload = task_cfg.get('google_oauth')
    if isinstance(cfg_payload, dict):
        return dict(cfg_payload)

    secret_name = str(
        task_cfg.get('google_secret_name', DEFAULT_GOOGLE_SECRET_NAME)
        or DEFAULT_GOOGLE_SECRET_NAME
    ).strip()
    if not secret_name:
        secret_name = DEFAULT_GOOGLE_SECRET_NAME

    legacy_paths = [
        ss.get_ari_dir() / 'admin' / secret_name,
        ss.get_ari_dir() / secret_name,
    ]
    secret_path = ss.resolve_secret_file(secret_name,
                                         legacy_paths=legacy_paths,
                                         mode=0o600)

    if secret_path.exists():
        try:
            with open(secret_path, 'r', encoding='utf-8') as infile:
                payload = json.load(infile)
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass

    payload = _legacy_oauth_default_payload()
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    with open(secret_path, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, indent=2)
    try:
        secret_path.chmod(0o600)
    except OSError:
        pass
    return payload


def _open_spreadsheet(payload: Dict[str, Any],
                      sheet_id: str):
    import gspread
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    scopes = payload.get('scopes')
    if not isinstance(scopes, list) or len(scopes) == 0:
        scopes = list(_SCOPES)
    creds = Credentials(
        token=None,
        refresh_token=str(payload.get('refresh_token') or ''),
        token_uri=str(payload.get('token_uri')
                      or 'https://oauth2.googleapis.com/token'),
        client_id=str(payload.get('client_id') or ''),
        client_secret=str(payload.get('client_secret') or ''),
        scopes=scopes,
    )
    creds.refresh(Request())
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)


def _sheet_name_candidates(value: Any,
                           defaults: Sequence[str]) -> List[str]:
    if isinstance(value, (list, tuple)):
        raw = list(value)
    else:
        raw = [value]

    out: List[str] = []
    seen: Set[str] = set()

    for item in raw + list(defaults):
        text = str(item or '').strip()
        if not text:
            continue
        low = text.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(text)
    return out


def _open_first_matching_sheet(spreadsheet,
                               name_candidates: Sequence[str],
                               label: str):
    for sheet_name in name_candidates:
        try:
            return spreadsheet.worksheet(sheet_name), sheet_name
        except Exception:
            continue

    emsg = (
        'Could not find {0} worksheet in sheet. Tried: {1}'.format(
            label,
            ', '.join(name_candidates),
        )
    )
    raise RuntimeError(emsg)


def _sheet_to_dataframe(worksheet) -> pd.DataFrame:
    rows = worksheet.get_all_records(default_blank='')
    if not rows:
        return pd.DataFrame(columns=_ASTROM_LEGACY_COLUMNS)
    return pd.DataFrame(rows)


def _write_dataframe_to_sheet(worksheet, dataframe: pd.DataFrame) -> None:
    from gspread_dataframe import set_with_dataframe

    worksheet.clear()
    set_with_dataframe(worksheet,
                       dataframe.fillna(''),
                       include_index=False,
                       include_column_header=True,
                       resize=True)


def _normalize_astrom_sheet_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or len(dataframe.columns) == 0:
        return pd.DataFrame(columns=_ASTROM_LEGACY_COLUMNS)
    frame = dataframe.copy()
    for col in _ASTROM_LEGACY_COLUMNS:
        if col not in frame.columns:
            frame[col] = ''
    return frame[_ASTROM_LEGACY_COLUMNS]


def _entry_to_legacy_row(entry: Dict[str, Any]) -> Dict[str, Any]:
    aliases = entry.get('ALIASES')
    if isinstance(aliases, (list, tuple)):
        aliases_txt = '|'.join(_dedupe_names(aliases))
    else:
        aliases_txt = '|'.join(_split_aliases(aliases))

    row = dict()
    row['OBJNAME'] = str(entry.get('APERO_NAME') or '').strip()
    row['ORIGINAL_NAME'] = str(entry.get('ORIGINAL_NAME')
                               or row['OBJNAME']).strip()
    row['ALIASES'] = aliases_txt
    row['RA_DEG'] = _nested_value(entry, 'RA')
    row['RA_SOURCE'] = _nested_source(entry, 'RA')
    row['DEC_DEG'] = _nested_value(entry, 'DEC')
    row['DEC_SOURCE'] = _nested_source(entry, 'DEC')
    row['EPOCH'] = entry.get('EPOCH', '')
    row['PMRA'] = _nested_value(entry, 'PMRA')
    row['PMRA_SOURCE'] = _nested_source(entry, 'PMRA')
    row['PMDE'] = _nested_value(entry, 'PMDE')
    row['PMDE_SOURCE'] = _nested_source(entry, 'PMDE')
    row['PLX'] = _nested_value(entry, 'PLX')
    row['PLX_SOURCE'] = _nested_source(entry, 'PLX')
    row['RV'] = _nested_value(entry, 'RV')
    row['RV_SOURCE'] = _nested_source(entry, 'RV')
    row['TEFF'] = _nested_value(entry, 'TEFF')
    row['TEFF_SOURCE'] = _nested_source(entry, 'TEFF')
    row['SP_TYPE'] = str(entry.get('SPT') or '').strip()
    row['SP_SOURCE'] = str(entry.get('SPT_SOURCE') or '').strip()
    row['NOTES'] = str(entry.get('NOTES') or '').strip()
    row['USED'] = 1
    return row


def _resolve_online_entry(name: str) -> Optional[Dict[str, Any]]:
    from apero_ri.application.astrometrics_api_helpers import (
        _resolve_online_using_drs,
    )

    return _resolve_online_using_drs(name)


def _add_sheet_object_to_ari(
    astrom_root: Path,
    sheet_row: Dict[str, Any],
    task_logger,
    tolerance_arcsec: float,
    created_by: str,
    dry_run: bool,
) -> Dict[str, Any]:
    from apero.core import drs_astrometrics as dra
    from apero_ri.core import issues as issues_core

    objname = str(sheet_row.get('OBJNAME') or '').strip()
    original_name = str(sheet_row.get('ORIGINAL_NAME') or '').strip()
    aliases = _split_aliases(sheet_row.get('ALIASES'))
    query_candidates = _dedupe_names([original_name, objname] + aliases)

    resolved_entry = None
    resolved_name = ''
    for candidate in query_candidates:
        try:
            resolved_entry = _resolve_online_entry(candidate)
        except Exception:
            resolved_entry = None
        if isinstance(resolved_entry, dict) and len(resolved_entry) > 0:
            resolved_name = candidate
            break

    if not isinstance(resolved_entry, dict) or len(resolved_entry) == 0:
        return dict(status='unresolved', name=objname)

    sheet_ra = _as_float(sheet_row.get('RA_DEG'))
    sheet_dec = _as_float(sheet_row.get('DEC_DEG'))
    resolved_ra = _as_float(_nested_value(resolved_entry, 'RA'))
    resolved_dec = _as_float(_nested_value(resolved_entry, 'DEC'))
    if None not in (sheet_ra, sheet_dec, resolved_ra, resolved_dec):
        sep_arcsec = dra._sep_arcsec(sheet_ra,
                                     sheet_dec,
                                     resolved_ra,
                                     resolved_dec)
        if sep_arcsec > tolerance_arcsec:
            return dict(status='coord_mismatch',
                        name=objname,
                        separation_arcsec=sep_arcsec)

    target_name = dra.clean_object(objname or resolved_entry.get('APERO_NAME'))
    if not target_name:
        target_name = dra.clean_object(resolved_name)
    if not target_name:
        return dict(status='invalid_name', name=objname)

    if dra.find_by_name(str(astrom_root), target_name) is not None:
        return dict(status='already_present', name=target_name)

    merged_aliases = _dedupe_names(
        aliases
        + _split_aliases(resolved_entry.get('ALIASES'))
        + [resolved_entry.get('APERO_NAME'),
           resolved_entry.get('ORIGINAL_NAME'),
           resolved_entry.get('SIMBAD_NAME')]
    )

    now = datetime.utcnow().isoformat(timespec='seconds')
    resolved_entry['APERO_NAME'] = target_name
    resolved_entry['ORIGINAL_NAME'] = original_name or resolved_name
    resolved_entry['ALIASES'] = merged_aliases
    resolved_entry['STATUS'] = dra.STATUS_PENDING
    resolved_entry['VERIFIER'] = 'None'
    resolved_entry['FIRST_UPDATED'] = now
    resolved_entry['FIRST_AUTHOR'] = created_by
    resolved_entry['LAST_EDIT'] = now
    resolved_entry['LAST_AUTHOR'] = created_by

    notes = str(resolved_entry.get('NOTES') or '').strip()
    legacy_note = (
        'Imported from legacy astrometric Google Sheet by '
        'LEGACY_ASTROM_GSHEET task.'
    )
    if notes:
        resolved_entry['NOTES'] = f'{notes} {legacy_note}'
    else:
        resolved_entry['NOTES'] = legacy_note

    if not dry_run:
        pending_dir = astrom_root / dra.STATUS_PENDING
        pending_dir.mkdir(parents=True, exist_ok=True)
        target_file = pending_dir / dra._safe_filename(target_name)
        with open(target_file, 'w', encoding='utf-8') as outfile:
            import yaml as _yaml

            _yaml.safe_dump(resolved_entry,
                            outfile,
                            sort_keys=False,
                            default_flow_style=False,
                            allow_unicode=True)

        try:
            dra._invalidate_dir_caches(str(astrom_root))
        except Exception:
            pass

    issue_reason = (
        'Imported from legacy astrometric Google Sheet. Confirm object '
        'identity and astrometric fields on the resolver page.'
    )
    if dry_run:
        return dict(status='would_add_to_ari', name=target_name)

    try:
        issues_core.create_issue(
            data_dir=str(astrom_root.parent.parent),
            kind='astrometric',
            reason=issue_reason,
            created_by=created_by,
            apero_name=target_name,
            field='STATUS',
            value='pending',
            instrument='*',
            profile_id=None,
            visibility='monitor',
            title='Legacy astrometric import: {0}'.format(target_name),
            type_='legacy',
            origin_url='legacy_gsheet_sync',
            label='astrometric-legacy',
            action='Open resolver page and confirm target',
            dedupe_key='legacy-import:{0}'.format(target_name),
        )
    except Exception as exc:
        if callable(task_logger):
            task_logger('Issue creation failed for {0}: {1}'.format(
                target_name, exc))

    return dict(status='added_to_ari', name=target_name)


# =============================================================================
# Define task class
# =============================================================================
class LegacyAstromGSheetTask(apero_async.AperoAsyncTask):
    """Bi-directional sync between ARI astrometrics and legacy sheet."""

    def __init__(self, status: str = 'pending') -> None:
        name = 'Legacy Astrometric GSheet Sync'
        description = (
            'Sync legacy v0.7 astrometric Google Sheet main/pending tabs '
            'with ARI astrometric YAML entries in both directions.'
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:
        task_cfg = dict(params.get('TASK_CONFIG') or {})
        dry_run = _as_bool(task_cfg.get('DRY_RUN', task_cfg.get('dry_run')))
        local_data_dir = Path(
            params.get('LOCAL_DATA_DIR', str(ARI_DIR))
        ).expanduser().resolve()
        astrom_root = local_data_dir / 'apero-assets' / 'astrometrics'

        sheet_id = str(task_cfg.get('sheet_id') or DEFAULT_ASTROM_SHEET_ID)
        name_map = task_cfg.get('sheet_names')
        if not isinstance(name_map, dict):
            name_map = dict()
        pending_value = (
            name_map.get('pending')
            if isinstance(name_map, dict)
            else None
        )
        main_value = (
            name_map.get('main')
            if isinstance(name_map, dict)
            else None
        )
        pending_candidates = _sheet_name_candidates(
            pending_value or task_cfg.get('sheet_name'),
            DEFAULT_ASTROM_PENDING_SHEET_NAMES,
        )
        main_candidates = _sheet_name_candidates(
            main_value,
            DEFAULT_ASTROM_MAIN_SHEET_NAMES,
        )
        if len(pending_candidates) == 0:
            pending_candidates = [DEFAULT_ASTROM_SHEET_NAME]
        if len(main_candidates) == 0:
            main_candidates = ['main']
        tolerance_arcsec = float(task_cfg.get('resolve_tolerance_arcsec', 120))
        created_by = str(task_cfg.get('created_by') or __NAME__)

        task_logger = params.get('TASK_LOGGER')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        from apero.core import drs_astrometrics as dra

        payload = _load_google_oauth_payload(task_cfg)
        self.progress = 0.0
        self.subprogress = 0.0
        tlog('LEGACY_ASTROM_GSHEET start.')
        tlog('Mode: {0}'.format('DRY_RUN' if dry_run else 'APPLY'))
        tlog('Astrom root: {0}'.format(astrom_root))
        tlog('Astrom sheet id: {0}'.format(sheet_id))
        tlog('Main tab candidates: {0}'.format(', '.join(main_candidates)))
        tlog('Pending tab candidates: {0}'.format(
            ', '.join(pending_candidates)
        ))

        spreadsheet = _open_spreadsheet(payload, sheet_id)
        main_ws, main_sheet_name = _open_first_matching_sheet(
            spreadsheet,
            main_candidates,
            'main',
        )
        pending_ws, pending_sheet_name = _open_first_matching_sheet(
            spreadsheet,
            pending_candidates,
            'pending',
        )

        main_df = _normalize_astrom_sheet_df(_sheet_to_dataframe(main_ws))
        pending_df = _normalize_astrom_sheet_df(_sheet_to_dataframe(pending_ws))
        sheet_df = pd.concat([main_df, pending_df], ignore_index=True)

        ari_entries = dra.load_all_entries(str(astrom_root))
        tlog('Loaded ARI entries: {0}'.format(len(ari_entries)))
        tlog(
            'Loaded main/pending rows: {0}/{1} (total {2})'.format(
                len(main_df),
                len(pending_df),
                len(sheet_df),
            )
        )
        tlog(
            'Resolved tabs main/pending: {0}/{1}'.format(
                main_sheet_name,
                pending_sheet_name,
            )
        )

        def log_scan(label: str,
                     row_it: int,
                     total: int,
                     progress_mark: List[int],
                     base: float,
                     width: float) -> None:
            if total <= 0:
                self.subprogress = 1.0
                self.progress = base + width
                return
            self.subprogress = row_it / total
            self.progress = base + width * (row_it / total)
            step = max(1, total // 20)
            should_log = (
                row_it == 1
                or row_it == total
                or row_it - progress_mark[0] >= step
            )
            if should_log:
                progress_mark[0] = row_it
                tlog('{0}: scanned rows {1}/{2}'.format(label, row_it, total))

        scan_mark = [0]
        sheet_total = len(sheet_df)
        tlog('Phase 1/3: indexing sheet names.')
        existing_sheet_names: Set[str] = set()
        for row_it, (_, row) in enumerate(sheet_df.iterrows(), start=1):
            log_scan('Phase 1/3',
                     row_it,
                     sheet_total,
                     scan_mark,
                     0.0,
                     0.2)
            names = [row.get('OBJNAME', ''), row.get('ORIGINAL_NAME', '')]
            names.extend(_split_aliases(row.get('ALIASES', '')))
            for name in names:
                norm = _normalize_name(name)
                if norm:
                    existing_sheet_names.add(norm)
        self.progress = 0.2
        self.subprogress = 1.0

        added_to_sheet: List[str] = []
        skipped_rejected: List[str] = []
        scan_mark = [0]
        ari_total = len(ari_entries)
        tlog('Phase 2/3: scanning ARI entries against sheet.')
        for row_it, (apero_name, entry) in enumerate(ari_entries, start=1):
            log_scan('Phase 2/3',
                     row_it,
                     ari_total,
                     scan_mark,
                     0.2,
                     0.4)
            status = str(entry.get('STATUS') or '').strip().lower()
            if status == str(dra.STATUS_REJECTED).strip().lower():
                rejected_name = str(entry.get('APERO_NAME') or apero_name)
                skipped_rejected.append(rejected_name)
                continue
            names = [
                apero_name,
                entry.get('APERO_NAME'),
                entry.get('ORIGINAL_NAME'),
                entry.get('SIMBAD_NAME'),
            ]
            names.extend(_split_aliases(entry.get('ALIASES')))
            if any(_normalize_name(name) in existing_sheet_names
                   for name in names):
                continue
            row = _entry_to_legacy_row(entry)
            pending_df = pd.concat([pending_df, pd.DataFrame([row])],
                                   ignore_index=True)
            added_to_sheet.append(str(row.get('OBJNAME') or apero_name))
            for name in names:
                norm = _normalize_name(name)
                if norm:
                    existing_sheet_names.add(norm)
        self.progress = 0.6
        self.subprogress = 1.0
        if len(skipped_rejected) > 0:
            tlog(
                'Skipped rejected ARI entries (not added to sheet): {0}'
                .format(len(skipped_rejected))
            )

        added_to_ari: List[str] = []
        would_add_to_ari: List[str] = []
        unresolved: List[str] = []
        mismatched: List[str] = []
        scan_mark = [0]
        sheet_total = len(sheet_df)
        tlog('Phase 3/3: scanning sheet rows for missing ARI targets.')
        for row_it, (_, row) in enumerate(sheet_df.iterrows(), start=1):
            log_scan('Phase 3/3',
                     row_it,
                     sheet_total,
                     scan_mark,
                     0.6,
                     0.4)
            row_dict = dict(row)
            names = _dedupe_names([
                row_dict.get('OBJNAME'),
                row_dict.get('ORIGINAL_NAME'),
            ] + _split_aliases(row_dict.get('ALIASES')))

            if any(dra.find_by_name(str(astrom_root), name) is not None
                   for name in names):
                continue

            result = _add_sheet_object_to_ari(
                astrom_root=astrom_root,
                sheet_row=row_dict,
                task_logger=tlog,
                tolerance_arcsec=tolerance_arcsec,
                created_by=created_by,
                dry_run=dry_run,
            )
            status = result.get('status', '')
            name = str(result.get('name') or row_dict.get('OBJNAME') or '')
            if status == 'added_to_ari':
                added_to_ari.append(name)
            elif status == 'would_add_to_ari':
                would_add_to_ari.append(name)
            elif status == 'coord_mismatch':
                sep = result.get('separation_arcsec')
                if isinstance(sep, float):
                    mismatched.append('{0} ({1:.2f} arcsec)'.format(name, sep))
                else:
                    mismatched.append(name)
            elif status == 'already_present':
                continue
            else:
                unresolved.append(name)
        self.progress = 1.0
        self.subprogress = 1.0

        if len(added_to_sheet) > 0 and not dry_run:
            _write_dataframe_to_sheet(
                pending_ws,
                _normalize_astrom_sheet_df(pending_df),
            )
            tlog(
                'Pending sheet updated with {0} ARI rows.'.format(
                    len(added_to_sheet)
                )
            )
        elif len(added_to_sheet) > 0 and dry_run:
            tlog(
                'Dry-run: {0} ARI rows would be added to pending sheet.'
                .format(len(added_to_sheet))
            )

        if dry_run:
            tlog('Dry-run planned changes:')
            tlog('added from google sheet to ari:')
            if len(would_add_to_ari) == 0:
                tlog('- <none>')
            else:
                for name in would_add_to_ari:
                    tlog('- {0}'.format(name))

            tlog('added from ari to googlesheet:')
            if len(added_to_sheet) == 0:
                tlog('- <none>')
            else:
                for name in added_to_sheet:
                    tlog('- {0}'.format(name))

        lp_needs_sync = any(
            _normalize_name(item) == _normalize_name('LP_416M570')
            for item in (
                added_to_ari
                + would_add_to_ari
                + unresolved
                + mismatched
            )
        )

        info_lines = [
            '# Legacy Astrometric Sheet Sync',
            '',
            '- Mode: {0}'.format('DRY_RUN' if dry_run else 'APPLY'),
            '- Main tab: {0}'.format(main_sheet_name),
            '- Pending tab: {0}'.format(pending_sheet_name),
            '- Added ARI -> sheet: {0}'.format(len(added_to_sheet)),
            '- Skipped rejected ARI entries: {0}'.format(
                len(skipped_rejected)
            ),
            '- Added sheet -> ARI: {0}'.format(len(added_to_ari)),
            '- Would add sheet -> ARI (dry-run): {0}'.format(
                len(would_add_to_ari)
            ),
            '- Unresolved sheet entries: {0}'.format(len(unresolved)),
            '- Coordinate mismatches: {0}'.format(len(mismatched)),
            '- LP_416M570 detected as pending add: {0}'.format(
                'yes' if lp_needs_sync else 'no'
            ),
        ]
        if len(added_to_ari) > 0:
            preview = ', '.join(added_to_ari[:15])
            info_lines.extend(['', '## Added To ARI', preview])
        if len(would_add_to_ari) > 0:
            preview = ', '.join(would_add_to_ari[:15])
            info_lines.extend(['', '## Would Add To ARI (Dry Run)', preview])
        if dry_run:
            info_lines.extend(['', '## Dry Run Planned Changes'])
            info_lines.append('')
            info_lines.append('added from google sheet to ari:')
            if len(would_add_to_ari) == 0:
                info_lines.append('- <none>')
            else:
                info_lines.extend(
                    ['- {0}'.format(item) for item in would_add_to_ari]
                )

            info_lines.append('')
            info_lines.append('added from ari to googlesheet:')
            if len(added_to_sheet) == 0:
                info_lines.append('- <none>')
            else:
                info_lines.extend(
                    ['- {0}'.format(item) for item in added_to_sheet]
                )
        if len(unresolved) > 0:
            preview = ', '.join(unresolved[:15])
            info_lines.extend(['', '## Unresolved', preview])
        if len(mismatched) > 0:
            preview = ', '.join(mismatched[:15])
            info_lines.extend(['', '## Coordinate Mismatch', preview])

        self.info = '\n'.join(info_lines) + '\n'
        self.output_files = [str(astrom_root)]
        tlog(
            'LEGACY_ASTROM_GSHEET completed. '
            'sheet_add={0}, ari_add={1}, ari_would_add={2}, '
            'unresolved={3}, mismatch={4}'.format(
                len(added_to_sheet),
                len(added_to_ari),
                len(would_add_to_ari),
                len(unresolved),
                len(mismatched),
            )
        )


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('LegacyAstromGSheetTask module - import only.')

# =============================================================================
# End of code
# =============================================================================