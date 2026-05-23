#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI - GLOBAL async task: sync legacy reject Google Sheet.

This task keeps the v0.7 legacy reject Google Sheet tabs and ARI reject
CSV files synchronized in both directions for SPIROU, NIRPS_HE, NIRPS_HA.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

from apero_ri.tasks import apero_async


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.legacy_reject_gsheet'
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

DEFAULT_REJECT_SHEET_ID = '1gvMp1nHmEcKCUpxsTxkx-5m115mLuQIGHhxJCyVoZCM'
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

_INSTRUMENT_TAB_MAP = {
    'spirou': 'SPIROU',
    'nirps_he': 'NIRPS_HE',
    'nirps_ha': 'NIRPS_HA',
}


# =============================================================================
# Define helpers
# =============================================================================
def _normalize_identifier(value: Any) -> str:
    text = str(value or '').strip()
    if text.endswith('.fits'):
        text = text[:-5]
    return text


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in ['1', 'true', 'yes', 'y', 'on']


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


def _open_worksheet(payload: Dict[str, Any],
                    sheet_id: str,
                    sheet_name: str):
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
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet(sheet_name)


def _sheet_to_dataframe(worksheet) -> pd.DataFrame:
    rows = worksheet.get_all_records(default_blank='')
    if not rows:
        return pd.DataFrame(
            columns=['IDENTIFIER', 'DATE_ADDED', 'PP', 'TEL',
                     'RV', 'USED', 'COMMENT']
        )
    return pd.DataFrame(rows)


def _write_dataframe_to_sheet(worksheet, dataframe: pd.DataFrame) -> None:
    from gspread_dataframe import set_with_dataframe

    worksheet.clear()
    set_with_dataframe(worksheet,
                       dataframe.fillna(''),
                       include_index=False,
                       include_column_header=True,
                       resize=True)


def _normalize_reject_df(dataframe: pd.DataFrame,
                         mod) -> pd.DataFrame:
    if dataframe is None or len(dataframe.columns) == 0:
        frame = pd.DataFrame(columns=mod.CSV_COLUMNS)
    else:
        frame = dataframe.copy()
        for col in mod.CSV_COLUMNS:
            if col not in frame.columns:
                frame[col] = ''
        frame = frame[mod.CSV_COLUMNS]

    frame[mod.ID_COLUMN] = [
        _normalize_identifier(value)
        for value in frame[mod.ID_COLUMN].tolist()
    ]
    frame = frame[frame[mod.ID_COLUMN].astype(str).str.strip() != '']
    for int_col in mod.INT_COLUMNS:
        if int_col in frame.columns:
            frame[int_col] = pd.to_numeric(frame[int_col],
                                           errors='coerce').fillna(0)
            frame[int_col] = frame[int_col].astype(int)
    if 'DATE_ADDED' in frame.columns:
        frame['DATE_ADDED'] = [str(value or '').strip()
                               for value in frame['DATE_ADDED'].tolist()]
    frame['COMMENT'] = [str(value or '').strip()
                        for value in frame.get('COMMENT', '').tolist()]
    frame = frame.drop_duplicates(subset=[mod.ID_COLUMN], keep='first')
    return frame.reset_index(drop=True)


def _merge_reject_frames(local_df: pd.DataFrame,
                         sheet_df: pd.DataFrame,
                         mod,
                         progress_cb=None) -> Tuple[
                             pd.DataFrame,
                             int,
                             int,
                             List[str],
                             List[str],
                         ]:
    local_map = {
        _normalize_identifier(row[mod.ID_COLUMN]): dict(row)
        for row in local_df.to_dict(orient='records')
        if _normalize_identifier(row.get(mod.ID_COLUMN))
    }
    sheet_map = {
        _normalize_identifier(row[mod.ID_COLUMN]): dict(row)
        for row in sheet_df.to_dict(orient='records')
        if _normalize_identifier(row.get(mod.ID_COLUMN))
    }

    ids_local = set(local_map.keys())
    ids_sheet = set(sheet_map.keys())
    from_sheet = sorted(ids_sheet - ids_local)
    from_local = sorted(ids_local - ids_sheet)

    merged_ids = sorted(ids_local | ids_sheet)
    merged_rows = []
    now = datetime.utcnow().isoformat(timespec='seconds')
    total = len(merged_ids)
    for row_it, ident in enumerate(merged_ids, start=1):
        base = sheet_map.get(ident) or local_map.get(ident) or {}
        row = dict(base)
        row[mod.ID_COLUMN] = ident
        if not str(row.get('DATE_ADDED') or '').strip():
            row['DATE_ADDED'] = now
        for int_col in mod.INT_COLUMNS:
            try:
                row[int_col] = int(float(row.get(int_col, 0) or 0))
            except (TypeError, ValueError):
                row[int_col] = 0
        row['COMMENT'] = str(row.get('COMMENT') or '').strip()
        merged_rows.append(row)
        if callable(progress_cb):
            try:
                progress_cb(row_it, total)
            except Exception:
                pass

    merged_df = pd.DataFrame(merged_rows)
    for col in mod.CSV_COLUMNS:
        if col not in merged_df.columns:
            merged_df[col] = ''
    merged_df = merged_df[mod.CSV_COLUMNS]
    return (
        merged_df.reset_index(drop=True),
        len(from_sheet),
        len(from_local),
        from_sheet,
        from_local,
    )


def _sheet_name_map(task_cfg: Dict[str, Any]) -> Dict[str, str]:
    user_map = task_cfg.get('sheet_names')
    out = dict(_INSTRUMENT_TAB_MAP)
    if isinstance(user_map, dict):
        for key, value in user_map.items():
            norm_key = str(key or '').strip().lower()
            norm_val = str(value or '').strip()
            if norm_key in out and norm_val:
                out[norm_key] = norm_val
    return out


# =============================================================================
# Define task class
# =============================================================================
class LegacyRejectGSheetTask(apero_async.AperoAsyncTask):
    """Bi-directional sync between ARI reject CSVs and legacy sheet tabs."""

    def __init__(self, status: str = 'pending') -> None:
        name = 'Legacy Reject GSheet Sync'
        description = (
            'Sync legacy v0.7 reject Google Sheet tabs with ARI reject '
            'CSV lists for SPIROU, NIRPS_HE, and NIRPS_HA.'
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:
        task_cfg = dict(params.get('TASK_CONFIG') or {})
        dry_run = _as_bool(task_cfg.get('DRY_RUN', task_cfg.get('dry_run')))
        local_data_dir = Path(
            params.get('LOCAL_DATA_DIR', str(ARI_DIR))
        ).expanduser().resolve()
        assets_dir = local_data_dir / 'apero-assets'

        task_logger = params.get('TASK_LOGGER')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        from apero.core import drs_rejection as mod

        payload = _load_google_oauth_payload(task_cfg)
        sheet_id = str(task_cfg.get('sheet_id') or DEFAULT_REJECT_SHEET_ID)
        name_map = _sheet_name_map(task_cfg)

        tlog('LEGACY_REJECT_GSHEET start.')
        tlog('Mode: {0}'.format('DRY_RUN' if dry_run else 'APPLY'))
        tlog('Assets dir: {0}'.format(assets_dir))
        tlog('Reject sheet id: {0}'.format(sheet_id))

        total_from_sheet = 0
        total_from_local = 0
        tab_summaries = []
        marker_3306464 = False
        dry_sheet_to_ari: List[str] = []
        dry_ari_to_sheet: List[str] = []
        n_tabs = len(_INSTRUMENT_TAB_MAP)
        self.progress = 0.0
        self.subprogress = 0.0

        for tab_it, asset_key in enumerate(['spirou', 'nirps_he', 'nirps_ha'],
                                           start=1):
            sheet_name = name_map[asset_key]
            self.progress = (tab_it - 1) / n_tabs
            self.subprogress = 0.0
            tlog('Tab {0}: loading sheet and local data.'.format(sheet_name))
            worksheet = _open_worksheet(payload, sheet_id, sheet_name)
            sheet_df = _normalize_reject_df(_sheet_to_dataframe(worksheet), mod)

            csv_path = (
                assets_dir / asset_key / mod.REJECT_SUBDIR / mod.REJECT_CSV
            )
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            local_df = _normalize_reject_df(mod._read_csv(str(csv_path)), mod)

            tlog(
                'Tab {0}: rows local={1}, sheet={2}.'.format(
                    sheet_name,
                    len(local_df),
                    len(sheet_df),
                )
            )

            progress_mark = [0]

            def merge_progress(done: int, total: int) -> None:
                if total <= 0:
                    self.subprogress = 1.0
                    return
                self.subprogress = done / total
                step = max(1, total // 20)
                should_log = (
                    done == 1
                    or done == total
                    or done - progress_mark[0] >= step
                )
                if should_log:
                    progress_mark[0] = done
                    tlog(
                        'Tab {0}: scanned rows {1}/{2}'.format(
                            sheet_name,
                            done,
                            total,
                        )
                    )

            (
                merged_df,
                n_from_sheet,
                n_from_local,
                from_sheet,
                from_local,
            ) = _merge_reject_frames(local_df,
                                     sheet_df,
                                     mod,
                                     progress_cb=merge_progress)
            self.subprogress = 1.0
            if dry_run:
                tlog(
                    'Tab {0}: dry-run; skip writing local CSV and sheet.'
                    .format(sheet_name)
                )
                for ident in from_sheet:
                    dry_sheet_to_ari.append(
                        '{0}: {1}'.format(sheet_name, ident)
                    )
                for ident in from_local:
                    dry_ari_to_sheet.append(
                        '{0}: {1}'.format(sheet_name, ident)
                    )
            else:
                mod._write_csv(str(csv_path), merged_df)
                _write_dataframe_to_sheet(worksheet, merged_df)
                tlog(
                    'Tab {0}: wrote local CSV and refreshed sheet.'
                    .format(sheet_name)
                )

            total_from_sheet += n_from_sheet
            total_from_local += n_from_local
            tab_summaries.append(
                '{0}: sheet->ARI={1}, ARI->sheet={2}'.format(
                    sheet_name,
                    n_from_sheet,
                    n_from_local,
                )
            )
            if '3306464' in set(merged_df[mod.ID_COLUMN].astype(str)):
                marker_3306464 = True

            tlog(
                'Tab {0}: sheet->ARI={1}, ARI->sheet={2}, total={3}'.format(
                    sheet_name,
                    n_from_sheet,
                    n_from_local,
                    len(merged_df),
                )
            )
            self.progress = tab_it / n_tabs

        if dry_run:
            tlog('Dry-run planned changes:')
            tlog('added from google sheet to ari:')
            if len(dry_sheet_to_ari) == 0:
                tlog('- <none>')
            else:
                for item in dry_sheet_to_ari:
                    tlog('- {0}'.format(item))

            tlog('added from ari to googlesheet:')
            if len(dry_ari_to_sheet) == 0:
                tlog('- <none>')
            else:
                for item in dry_ari_to_sheet:
                    tlog('- {0}'.format(item))

        info_lines = [
            '# Legacy Reject Sheet Sync',
            '',
            '- Mode: {0}'.format('DRY_RUN' if dry_run else 'APPLY'),
            '- Added sheet -> ARI: {0}'.format(total_from_sheet),
            '- Added ARI -> sheet: {0}'.format(total_from_local),
            '- 3306464 present after sync: {0}'.format(
                'yes' if marker_3306464 else 'no'
            ),
            '',
            '## Per Tab',
        ]
        info_lines.extend(['- {0}'.format(item) for item in tab_summaries])

        if dry_run:
            info_lines.extend(['', '## Dry Run Planned Changes'])
            info_lines.append('')
            info_lines.append('added from google sheet to ari:')
            if len(dry_sheet_to_ari) == 0:
                info_lines.append('- <none>')
            else:
                info_lines.extend(
                    ['- {0}'.format(item) for item in dry_sheet_to_ari]
                )

            info_lines.append('')
            info_lines.append('added from ari to googlesheet:')
            if len(dry_ari_to_sheet) == 0:
                info_lines.append('- <none>')
            else:
                info_lines.extend(
                    ['- {0}'.format(item) for item in dry_ari_to_sheet]
                )

        self.info = '\n'.join(info_lines) + '\n'
        self.output_files = [str(assets_dir)]
        self.progress = 1.0
        self.subprogress = 1.0
        tlog('LEGACY_REJECT_GSHEET completed.')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('LegacyRejectGSheetTask module - import only.')

# =============================================================================
# End of code
# =============================================================================