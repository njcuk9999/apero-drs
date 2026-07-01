#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI - GLOBAL async task: sync known-errors Google Sheet.

This task keeps the ARI known-errors store (per-error YAML files under
``resources/monitor/known_errors``) synchronised in BOTH directions with a
Google Sheet.

Sync model
----------
- Records are keyed by their ``id`` (UUID).
- Rows present on only one side are copied to the other (union; no deletes).
- Rows present on both sides are reconciled by ``updated_at`` (the most
  recently edited record wins). Ties / unparseable timestamps prefer ARI.
- Sheet rows with a blank ``id`` are treated as new records (a UUID is
  generated and written back to the sheet).

It reuses the same Google OAuth secret (``legacy_gsheet_oauth.json``) as the
other legacy GSheet sync tasks.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from apero_ri.core import known_errors as ke
from apero_ri.core.secret_store import get_ari_dir
from apero_ri.tasks import apero_async


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.legacy_known_errors_gsheet'
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

# Sheet: https://docs.google.com/spreadsheets/d/
#   15Gu_aY6h9Esw1uTF8Y5JCHl6m7191AviJNTPkbeTiQE/edit?gid=0#gid=0
DEFAULT_KNOWN_ERRORS_SHEET_ID = '15Gu_aY6h9Esw1uTF8Y5JCHl6m7191AviJNTPkbeTiQE'
DEFAULT_GOOGLE_SECRET_NAME = 'legacy_gsheet_oauth.json'

# Columns mirrored to/from the sheet (slug is derived, so it is omitted).
KNOWN_ERROR_COLUMNS = [
    'id',
    'date_reported',
    'reported_by',
    'instrument_mode',
    'recipe',
    'action',
    'type',
    'error_code',
    'github_issue',
    'generic_error',
    'comments',
    'full_example_error',
    'updated_at',
]

_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/spreadsheets',
]


# =============================================================================
# Define helpers
# =============================================================================
def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in ['1', 'true', 'yes', 'y', 'on']


def _safe(value: Any) -> str:
    return str(value or '').strip()


def _now() -> str:
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def _parse_ts(value: Any) -> Optional[datetime]:
    text = _safe(value)
    if not text:
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(text, fmt)
        except Exception:
            continue
    return None


def _load_google_oauth_payload(task_cfg: Dict[str, Any]) -> Dict[str, Any]:
    secret_name = str(
        task_cfg.get('google_secret_name', DEFAULT_GOOGLE_SECRET_NAME)
        or DEFAULT_GOOGLE_SECRET_NAME
    ).strip()
    if not secret_name:
        secret_name = DEFAULT_GOOGLE_SECRET_NAME

    secret_path = get_ari_dir() / 'admin' / secret_name
    if secret_path.exists():
        try:
            with open(secret_path, 'r', encoding='utf-8') as infile:
                payload = json.load(infile)
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
    raise FileNotFoundError(
        'Missing Google OAuth secret file. Add credentials to '
        f'{secret_path}. Upload this file in Async Task admin editor.'
    )


def _open_worksheet(payload: Dict[str, Any],
                    sheet_id: str,
                    sheet_name: Optional[str]):
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
    if sheet_name:
        return spreadsheet.worksheet(sheet_name)
    # Default: first worksheet (gid=0).
    return spreadsheet.get_worksheet(0)


def _sheet_to_dataframe(worksheet) -> pd.DataFrame:
    all_values = worksheet.get_all_values()
    if not all_values:
        return pd.DataFrame(columns=KNOWN_ERROR_COLUMNS)
    header = all_values[0]
    data_rows = all_values[1:]
    # Drop trailing empty columns introduced by Google Sheets.
    while header and str(header[-1]).strip() == '':
        header = header[:-1]
        data_rows = [row[:len(header)] for row in data_rows]
    if not header:
        return pd.DataFrame(columns=KNOWN_ERROR_COLUMNS)
    # Pad or trim each data row to match header length.
    ncols = len(header)
    padded = [
        (row + [''] * ncols)[:ncols] for row in data_rows
    ]
    df = pd.DataFrame(padded, columns=header)
    # Drop rows that are entirely blank.
    df = df[df.apply(lambda r: any(str(v).strip() for v in r), axis=1)]
    return df.reset_index(drop=True)


def _write_dataframe_to_sheet(worksheet, dataframe: pd.DataFrame) -> None:
    worksheet.clear()
    header = dataframe.columns.tolist()
    rows = dataframe.fillna('').astype(str).values.tolist()
    values = [header] + rows
    if values:
        worksheet.update('A1', values)


def _row_from_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a known-error record reduced to the synced columns."""
    out: Dict[str, Any] = dict()
    for col in KNOWN_ERROR_COLUMNS:
        out[col] = _safe(record.get(col))
    return out


def _sheet_rows(dataframe: pd.DataFrame) -> Tuple[
        Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Split sheet rows into an id->row map plus blank-id (new) rows."""
    by_id: Dict[str, Dict[str, Any]] = dict()
    new_rows: List[Dict[str, Any]] = []
    if dataframe is None or len(dataframe.columns) == 0:
        return by_id, new_rows
    frame = dataframe.copy()
    for col in KNOWN_ERROR_COLUMNS:
        if col not in frame.columns:
            frame[col] = ''
    for record in frame.to_dict(orient='records'):
        # Must have a generic_error to be a meaningful row.
        if not _safe(record.get('generic_error')):
            continue
        row = _row_from_record(record)
        ident = _safe(row.get('id'))
        if ident:
            by_id[ident] = row
        else:
            new_rows.append(row)
    return by_id, new_rows


def _merge(local_map: Dict[str, Dict[str, Any]],
           sheet_map: Dict[str, Dict[str, Any]],
           sheet_new: List[Dict[str, Any]]) -> Tuple[
               Dict[str, Dict[str, Any]],
               List[str],
               List[str],
               List[str]]:
    """Reconcile local + sheet records by id and updated_at.

    :return: (merged_map, to_ari_ids, to_sheet_ids, conflict_ids)
    """
    merged: Dict[str, Dict[str, Any]] = dict()
    to_ari: List[str] = []
    to_sheet: List[str] = []
    conflicts: List[str] = []

    all_ids = set(local_map.keys()) | set(sheet_map.keys())
    for ident in all_ids:
        lrow = local_map.get(ident)
        srow = sheet_map.get(ident)
        if lrow and not srow:
            merged[ident] = lrow
            to_sheet.append(ident)
        elif srow and not lrow:
            merged[ident] = srow
            to_ari.append(ident)
        else:
            # Present on both sides: newest updated_at wins (tie -> local).
            lts = _parse_ts(lrow.get('updated_at'))
            sts = _parse_ts(srow.get('updated_at'))
            if sts is not None and (lts is None or sts > lts):
                merged[ident] = srow
                to_ari.append(ident)
            else:
                merged[ident] = lrow
                if lts is not None and sts is not None and lts > sts:
                    to_sheet.append(ident)
            if lrow != srow:
                conflicts.append(ident)

    # Brand-new sheet rows (blank id) become new ARI records.
    for row in sheet_new:
        new_row = dict(row)
        new_row['id'] = str(uuid.uuid4())
        if not _safe(new_row.get('updated_at')):
            new_row['updated_at'] = _now()
        merged[new_row['id']] = new_row
        to_ari.append(new_row['id'])

    return merged, to_ari, to_sheet, conflicts


# =============================================================================
# Define task class
# =============================================================================
class LegacyKnownErrorsGSheetTask(apero_async.AperoAsyncTask):
    """Bi-directional sync between ARI known-errors YAMLs and a Google Sheet."""

    def __init__(self, status: str = 'pending') -> None:
        name = 'Legacy Known Errors GSheet Sync'
        description = (
            'Sync the monitor known-errors list with a Google Sheet in both '
            'directions (union; newest updated_at wins on conflict).'
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:
        task_cfg = dict(params.get('TASK_CONFIG') or {})
        dry_run = _as_bool(task_cfg.get('DRY_RUN', task_cfg.get('dry_run')))
        task_logger = params.get('TASK_LOGGER')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        payload = _load_google_oauth_payload(task_cfg)
        sheet_id = str(
            task_cfg.get('sheet_id') or DEFAULT_KNOWN_ERRORS_SHEET_ID
        )
        sheet_name = task_cfg.get('sheet_name') or None

        self.progress = 0.0
        self.subprogress = 0.0
        tlog('LEGACY_KNOWN_ERRORS_GSHEET start.')
        tlog('Mode: {0}'.format('DRY_RUN' if dry_run else 'APPLY'))
        tlog('Known-errors sheet id: {0}'.format(sheet_id))

        # ── Load both sides ────────────────────────────────────────────
        worksheet = _open_worksheet(payload, sheet_id, sheet_name)
        sheet_df = _sheet_to_dataframe(worksheet)
        sheet_map, sheet_new = _sheet_rows(sheet_df)

        local_records = ke.list_known_errors_raw()
        local_map = {
            _safe(rec.get('id')): _row_from_record(rec)
            for rec in local_records
            if _safe(rec.get('id'))
        }
        self.progress = 0.3
        tlog(
            'Loaded local={0}, sheet={1} (+{2} new sheet rows).'.format(
                len(local_map), len(sheet_map), len(sheet_new)
            )
        )

        # ── Merge ──────────────────────────────────────────────────────
        merged, to_ari, to_sheet, conflicts = _merge(
            local_map, sheet_map, sheet_new
        )
        self.progress = 0.6
        tlog(
            'Merge: sheet->ARI={0}, ARI->sheet={1}, conflicts={2}, '
            'total={3}'.format(
                len(to_ari), len(to_sheet), len(conflicts), len(merged)
            )
        )

        # ── Write back ─────────────────────────────────────────────────
        if dry_run:
            tlog('Dry-run; not writing ARI YAMLs or the sheet.')
            for ident in to_ari:
                tlog('- sheet->ARI: {0}'.format(ident))
            for ident in to_sheet:
                tlog('- ARI->sheet: {0}'.format(ident))
        else:
            # Write every winning record to ARI (preserves updated_at).
            n_written = 0
            for ident, row in merged.items():
                try:
                    ke.write_known_error_raw(row)
                    n_written += 1
                except Exception as exc:
                    tlog('! failed to write {0}: {1}'.format(ident, exc))
            self.progress = 0.85
            tlog('Wrote {0} ARI known-error file(s).'.format(n_written))

            # Refresh the sheet from the merged set (stable column order).
            ordered = sorted(
                merged.values(),
                key=lambda r: (
                    _safe(r.get('date_reported')),
                    _safe(r.get('instrument_mode')),
                    _safe(r.get('recipe')),
                ),
                reverse=True,
            )
            out_df = pd.DataFrame(ordered, columns=KNOWN_ERROR_COLUMNS)
            _write_dataframe_to_sheet(worksheet, out_df)
            tlog('Refreshed Google Sheet with {0} row(s).'.format(len(out_df)))

        # ── Summary ────────────────────────────────────────────────────
        info_lines = [
            '# Legacy Known Errors Sheet Sync',
            '',
            '- Mode: {0}'.format('DRY_RUN' if dry_run else 'APPLY'),
            '- Local records: {0}'.format(len(local_map)),
            '- Sheet records: {0}'.format(len(sheet_map)),
            '- New sheet rows (blank id): {0}'.format(len(sheet_new)),
            '- Added sheet -> ARI: {0}'.format(len(to_ari)),
            '- Pushed ARI -> sheet: {0}'.format(len(to_sheet)),
            '- Conflicts reconciled (newest wins): {0}'.format(len(conflicts)),
            '- Total after merge: {0}'.format(len(merged)),
        ]
        self.info = '\n'.join(info_lines) + '\n'
        self.output_files = [str(ke.known_errors_dir())]
        self.progress = 1.0
        self.subprogress = 1.0
        tlog('LEGACY_KNOWN_ERRORS_GSHEET completed.')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('LegacyKnownErrorsGSheetTask module - import only.')

# =============================================================================
# End of code
# =============================================================================
