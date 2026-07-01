#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared helpers for APERO reduced (red) checks.

These helpers mirror :mod:`apero_ri.apero_monitoring.core.raw_common` but
resolve the reduced-data directories (PATH.RED / PATH.PP), the manual-trigger
log file (PATH.TRIGGER_LOG) and provide reduced-file globbing.  The generic
report / config / header helpers are re-exported from ``raw_common`` so a red
check only needs to import this one module.
"""

from __future__ import annotations

import csv as _csv
from pathlib import Path
from typing import List, Optional, Tuple

from apero_ri.application import profile_utils
from apero_ri.apero_monitoring.core import raw_common

# Column order of the manual-trigger CSV log (written without a header row).
MANUAL_LOG_COLUMNS = ['TIMESTAMP', 'PROFILE', 'STATUS', 'OBSDIRS', 'COMMENT']

# Re-export the generic helpers so red checks import a single module.
get_raw_config = raw_common.get_raw_config
get_common_value = raw_common.get_common_value
get_check_value = raw_common.get_check_value
to_bool = raw_common.to_bool
is_check_enabled = raw_common.is_check_enabled
get_header_key = raw_common.get_header_key
read_primary_header = raw_common.read_primary_header
build_report = raw_common.build_report
format_failed_file_message = raw_common.format_failed_file_message
get_raw_dir = raw_common.get_raw_dir
load_example_aparams = raw_common.load_example_aparams


# =============================================================================
# Path resolution
# =============================================================================
def _resolve_path(aparams: dict, keys: Tuple[str, ...]) -> Optional[Path]:
    """Return the first non-empty profile path among ``keys``."""
    for key in keys:
        value = profile_utils.profile_get_path(aparams, key, '')
        if str(value or '').strip():
            return Path(str(value)).expanduser()
    return None


def get_red_dir(aparams: dict) -> Optional[Path]:
    """Resolve the reduced (DRS_DATA_RED) directory from a profile."""
    return _resolve_path(aparams, ('PATH.RED', 'PATH_RED', 'red'))


def get_pp_dir(aparams: dict) -> Optional[Path]:
    """Resolve the preprocessed (DRS_DATA_WORKING) directory from a profile."""
    return _resolve_path(aparams, ('PATH.PP', 'PATH_PP', 'pp', 'tmp'))


def get_trigger_log(aparams: dict) -> Optional[Path]:
    """Resolve the manual-trigger log file (PATH.TRIGGER_LOG)."""
    return _resolve_path(
        aparams, ('PATH.TRIGGER_LOG', 'PATH_TRIGGER_LOG', 'trigger_log')
    )


# =============================================================================
# Reduced-file listing
# =============================================================================
def _list_obsdir_pattern(base_dir: Optional[Path],
                         obs_dir: str,
                         pattern: str) -> Tuple[Path, List[Path]]:
    """Return obsdir path under ``base_dir`` and files matching ``pattern``."""
    obs_name = str(obs_dir or '').strip()
    if base_dir is None:
        return Path(obs_name), []
    obs_path = base_dir / obs_name
    if not obs_path.exists():
        return obs_path, []
    return obs_path, sorted(obs_path.glob(pattern))


def list_red_files(aparams: dict,
                   obs_dir: str,
                   pattern: str = '*.fits') -> Tuple[Path, List[Path]]:
    """Return the reduced obsdir path and every file matching ``pattern``."""
    return _list_obsdir_pattern(get_red_dir(aparams), obs_dir, pattern)


def list_pp_files(aparams: dict,
                  obs_dir: str,
                  pattern: str = '*.fits') -> Tuple[Path, List[Path]]:
    """Return the preprocessed obsdir path and files matching ``pattern``."""
    return _list_obsdir_pattern(get_pp_dir(aparams), obs_dir, pattern)


def list_raw_files(aparams: dict,
                   obs_dir: str,
                   pattern: str = '*.fits') -> Tuple[Path, List[Path]]:
    """Return the raw obsdir path and files matching ``pattern``."""
    return _list_obsdir_pattern(get_raw_dir(aparams), obs_dir, pattern)


# =============================================================================
# Manual-trigger log
# =============================================================================
def check_manual_trigger_status(aparams: dict,
                                obs_dir: str,
                                status: str) -> Tuple[bool, str]:
    """Return whether one obsdir reached a manual-trigger ``status``.

    The manual trigger writes a per-profile CSV log (no header row) with the
    columns in :data:`MANUAL_LOG_COLUMNS`.  Each row records one status event
    for a pipe-separated list of obsdirs.  This returns ``True`` when ``obs_dir``
    appears in any row whose STATUS matches ``status`` (rows whose OBSDIRS list
    contains a ``*`` wildcard are skipped, matching the original behaviour).

    The log file is located at ``PATH.TRIGGER_LOG``.

    :param aparams: Hydrated APERO profile mapping.
    :param obs_dir: Obsdir identifier currently validated.
    :param status: Manual-trigger status token to look for (e.g. APERO_END).
    :return: Tuple of pass flag and message.
    """
    logname = get_trigger_log(aparams)
    if logname is None:
        # PATH.TRIGGER_LOG is optional: profiles that don't configure it
        # simply skip this check rather than failing it.
        return True, ('PATH.TRIGGER_LOG is not configured for this profile; '
                      'manual-trigger check skipped.')
    if not logname.exists():
        return False, f'Manual-trigger log {logname} does not exist.'
    obs_name = str(obs_dir or '').strip()
    status_token = str(status or '').strip()
    try:
        with open(logname, 'r', encoding='utf-8', newline='') as handle:
            reader = _csv.reader(handle)
            for raw_row in reader:
                if not raw_row:
                    continue
                row = dict(zip(MANUAL_LOG_COLUMNS, raw_row))
                if str(row.get('STATUS', '') or '').strip() != status_token:
                    continue
                obs_dirs = str(row.get('OBSDIRS', '') or '').split('|')
                obs_dirs = [item.strip() for item in obs_dirs]
                if '*' in obs_dirs:
                    continue
                if obs_name in obs_dirs:
                    return True, (f'Found {status_token} for obsdir '
                                  f'{obs_name} in {logname.name}.')
    except Exception as exc:
        return False, f'Could not read manual-trigger log {logname}: {exc}'
    return False, (f'{status_token} not found for obsdir {obs_name} in '
                   f'{logname.name}.')


# =============================================================================
# Rejection list (ARI / APERO sourced)
# =============================================================================
def _ari_data_dir() -> Path:
    """Return the ARI local data directory (defaults to ``~/.ari``)."""
    return Path.home() / '.ari'


def get_reject_identifiers(aparams: dict, instrument: str) -> set:
    """Return the set of rejected file identifiers for one instrument.

    ARI keeps the reject list as an APERO asset (synced from the historic
    Google Sheet) at
    ``<data_dir>/apero-assets/<instrument>/reject/reject.csv``.  This reads it
    through APERO's ``drs_rejection`` CSV reader so checks never need direct
    Google-Sheet access.  Any failure (APERO not importable, asset missing,
    offline) returns an empty set, so the calling check still runs and simply
    does not skip any rejected file.

    :param aparams: Hydrated APERO profile mapping (unused; reserved).
    :param instrument: APERO instrument name, e.g. ``'NIRPS_HE'``.
    :return: Set of uppercase reject identifiers (odometer / filename stems).
    """
    _ = aparams
    target = str(instrument or '').strip().lower()
    if not target:
        return set()
    try:
        from apero.core import drs_rejection
    except Exception:
        return set()
    csv_path = (
        _ari_data_dir()
        / 'apero-assets'
        / target
        / drs_rejection.REJECT_SUBDIR
        / drs_rejection.REJECT_CSV
    )
    if not csv_path.exists():
        return set()
    try:
        frame = drs_rejection._read_csv(str(csv_path))
        identifiers = set()
        for value in frame[drs_rejection.ID_COLUMN]:
            text = str(value or '').strip().upper()
            if text:
                identifiers.add(text)
        return identifiers
    except Exception:
        return set()
