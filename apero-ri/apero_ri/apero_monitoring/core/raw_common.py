#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared helpers for APERO raw checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import os

import numpy as np
import yaml
from astropy.io import fits

from apero_ri.application import profile_utils

# Store an in-process FITS-header cache for the active obsdir worker.
_ACTIVE_OBSDIR = ''
_HEADER_CACHE = dict()
_FILE_LIST_CACHE = dict()

# Number of failing files shown in check messages before truncation.
FAIL_FILE_SAMPLE_SIZE = 8


# =============================================================================
# Define functions
# =============================================================================
def activate_obsdir_header_cache(obsdir: str) -> None:
    """Activate a cache namespace for one obsdir worker.

    This function scopes cached FITS primary headers to one obsdir workflow.
    Re-activating with a different obsdir clears stale headers so cache entries
    cannot leak across nights.

    :param obsdir: Obsdir identifier currently processed by the worker.
    :return: None
    """
    global _ACTIVE_OBSDIR, _HEADER_CACHE, _FILE_LIST_CACHE
    name = str(obsdir or '').strip()
    if _ACTIVE_OBSDIR != name:
        _HEADER_CACHE = dict()
        _FILE_LIST_CACHE = dict()
    _ACTIVE_OBSDIR = name


def clear_obsdir_header_cache() -> None:
    """Clear and disable the active obsdir FITS-header cache.

    Workers call this after finishing one obsdir so memory remains bounded and
    cached headers cannot be reused by unrelated obsdirs.

    :return: None
    """
    global _ACTIVE_OBSDIR, _HEADER_CACHE, _FILE_LIST_CACHE
    _ACTIVE_OBSDIR = ''
    _HEADER_CACHE = dict()
    _FILE_LIST_CACHE = dict()


def get_raw_config(aparams: dict) -> dict:
    """Return the APERO-check config block for one profile.

    The check configuration is expected directly under `apero-checks` with one
    sub-section per check and one optional shared `common` section.

    :param aparams: Hydrated APERO profile mapping.
    :return: Top-level check configuration mapping.
    """
    cfg = aparams.get('apero-checks', {}) if isinstance(aparams, dict) else {}
    return dict(cfg) if isinstance(cfg, dict) else dict()


def get_common_value(aparams: dict,
                     keys: List[str],
                     default: Any = None) -> Any:
    """Return a nested shared check setting from apero-checks.common.

    :param aparams: Hydrated APERO profile mapping.
    :param keys: Ordered nested key path under `apero-checks.common`.
    :param default: Fallback value when the path is missing.
    :return: Resolved value or default.
    """
    cfg = get_raw_config(aparams)
    current = cfg.get('common', default)
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return default if current is None else current


def get_check_value(aparams: dict,
                    check_name: str,
                    keys: List[str],
                    default: Any = None) -> Any:
    """Return a nested setting from one explicit check section.

    :param aparams: Hydrated APERO profile mapping.
    :param check_name: Check section under `apero-checks`.
    :param keys: Ordered nested key path inside the check section.
    :param default: Fallback value when the path is missing.
    :return: Resolved value or default.
    """
    cfg = get_raw_config(aparams)
    current = cfg.get(str(check_name), default)
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return default if current is None else current


def to_bool(value: Any, default: bool = False) -> bool:
    """Convert flexible config values to bool."""
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ['1', 'true', 't', 'yes', 'on']:
        return True
    if text in ['0', 'false', 'f', 'no', 'off']:
        return False
    return bool(default)


def is_check_enabled(aparams: dict,
                     check_name: str,
                     default: bool = True) -> bool:
    """Return whether one top-level check section is enabled."""
    enabled = get_check_value(aparams,
                              check_name,
                              ['enabled'],
                              default)
    return to_bool(enabled, default=default)


def get_raw_value(aparams: dict,
                  keys: List[str],
                  default: Any = None) -> Any:
    """Return a nested raw APERO-check setting."""
    current = get_raw_config(aparams)
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return default if current is None else current


def get_raw_dir(aparams: dict) -> Optional[Path]:
    """Resolve the raw directory from a hydrated APERO profile."""
    for key in ('PATH.RAW', 'PATH_RAW', 'raw'):
        value = profile_utils.profile_get_path(aparams, key, '')
        if str(value or '').strip():
            return Path(str(value)).expanduser()
    return None


def get_critical_check_dir(aparams: dict) -> Optional[Path]:
    """Resolve the critical-check directory (PATH.CRITICAL_CHECK).

    Optional: returns None when not configured, which causes critical checks
    to pass automatically.
    """
    for key in ('PATH.CRITICAL_CHECK', 'PATH_CRITICAL_CHECK', 'critical_check'):
        value = profile_utils.profile_get_path(aparams, key, '')
        if str(value or '').strip():
            return Path(str(value)).expanduser()
    return None


def get_header_key(aparams: dict, logical_name: str) -> str:
    """Resolve one raw-header key name from apero-checks.common.

    :param aparams: Hydrated APERO profile mapping.
    :param logical_name: Logical header key name requested by checks.
    :return: Concrete FITS keyword or empty string.
    """
    keys = get_common_value(aparams, ['header_keys'], dict())
    if not isinstance(keys, dict):
        return ''
    return str(keys.get(logical_name, '') or '').strip()


def list_obsdir_files(aparams: dict, obs_dir: str) -> Tuple[Path, List[Path]]:
    """Return the obsdir path and every FITS file under it."""
    global _FILE_LIST_CACHE
    obs_name = str(obs_dir or '').strip()
    if _ACTIVE_OBSDIR != '' and obs_name == _ACTIVE_OBSDIR:
        cache_obs = _FILE_LIST_CACHE.get('obs_dir')
        cache_path = _FILE_LIST_CACHE.get('obs_path')
        cache_files = _FILE_LIST_CACHE.get('files')
        if (cache_obs == obs_name and isinstance(cache_path, Path)
                and isinstance(cache_files, list)):
            return cache_path, list(cache_files)

    raw_dir = get_raw_dir(aparams)
    if raw_dir is None:
        obs_path = Path(obs_name)
        files = []
    else:
        obs_path = raw_dir / obs_name
        files = sorted(obs_path.glob('*.fits'))

    if _ACTIVE_OBSDIR != '' and obs_name == _ACTIVE_OBSDIR:
        _FILE_LIST_CACHE = dict(obs_dir=obs_name,
                                obs_path=obs_path,
                                files=list(files))
    return obs_path, files


def read_primary_header(filename: Path):
    """Read one primary FITS header with optional obsdir-local caching.

    When an obsdir cache is active, this function stores one detached header
    copy per filename and returns a fresh copy for each caller. Returning a
    copy keeps callers isolated from each other even when cached data is used.

    :param filename: FITS filename whose primary header is required.
    :return: Detached astropy header object.
    """
    global _HEADER_CACHE
    cache_key = str(Path(filename).resolve())
    if _ACTIVE_OBSDIR != '' and cache_key in _HEADER_CACHE:
        return _HEADER_CACHE[cache_key].copy()
    header = fits.getheader(filename, ext=0).copy()
    if _ACTIVE_OBSDIR != '':
        _HEADER_CACHE[cache_key] = header.copy()
    return header


def empty_value(dtype: str) -> Any:
    """Return an empty placeholder for one configured dtype."""
    if dtype in ['float', 'time.mjd']:
        return np.nan
    if dtype == 'bool':
        return False
    return ''


def convert_value(raw_value: Any, dtype: str) -> Any:
    """Convert one raw header value to the configured dtype."""
    if raw_value is None:
        return empty_value(dtype)
    if dtype in ['float', 'time.mjd']:
        return float(raw_value)
    if dtype == 'bool':
        text = str(raw_value).strip().lower()
        return text in ['1', 'true', 't', 'yes', 'on']
    return str(raw_value)


def load_header_table(files: List[Path],
                      header_defs: Dict[str, dict]) -> Tuple[dict, dict]:
    """Build aligned vectors of selected header values for many files.

    The function reads each file primary header through the shared raw helper,
    therefore it automatically benefits from the active obsdir cache when one
    is enabled by the task runner.

    :param files: Ordered list of FITS files to scan.
    :param header_defs: Mapping of output field name to key and dtype config.
    :return: Tuple containing aligned value and presence-mask mappings.
    """
    # Start aligned table and mask containers with a filename column.
    table: Dict[str, Any] = dict(filename=[])
    masks: Dict[str, Any] = dict(filename=[])
    # Add one output vector per configured header definition.
    for name in header_defs:
        table[name] = []
        masks[name] = []

    # Populate all vectors by scanning files in input order.
    for filename in files:
        # Always store file names and mark that column as present.
        table['filename'].append(str(filename))
        masks['filename'].append(True)
        # Read headers through the cache-aware helper.
        header = read_primary_header(filename)
        # Extract and convert each configured header value.
        for name, conf in header_defs.items():
            key = str(conf.get('key', '') or '').strip()
            dtype = str(conf.get('dtype', 'str') or 'str').strip()
            raw_value = header.get(key) if key else None
            present = raw_value is not None
            try:
                value = convert_value(raw_value, dtype)
            except Exception:
                value = empty_value(dtype)
                present = False
            table[name].append(value)
            masks[name].append(present)

    # Convert python lists to numpy arrays for vectorized downstream checks.
    for key in table:
        table[key] = np.array(table[key])
        masks[key] = np.array(masks[key]).astype(bool)
    return table, masks


def files_from_mask(table: dict, mask: Any) -> List[Path]:
    """Return file paths whose boolean mask entry is True.

    :param table: Output table returned by ``load_header_table``.
    :param mask: Boolean-like mask aligned with table rows.
    :return: List of matching file paths.
    """
    # Get the aligned filename column used by every raw check table.
    raw_names = np.array(table.get('filename', []), dtype=str)
    # Convert the incoming mask to a strict boolean numpy array.
    use = np.array(mask).astype(bool)
    # Protect against malformed masks to keep checks robust.
    if len(raw_names) == 0 or len(raw_names) != len(use):
        return []
    # Build Path objects to make basename/parent handling consistent.
    out = []
    for name in raw_names[use]:
        out.append(Path(str(name)))
    return out


def format_failed_file_message(test_key: str,
                               reason: str,
                               obs_path: Path,
                               fail_files: List[Path],
                               sample_size: int = FAIL_FILE_SAMPLE_SIZE
                               ) -> str:
    """Create a verbose failure message with representative filenames.

    The output is designed for monitor users so they can quickly identify
    where failures came from and inspect specific files.

    :param test_key: Logical check key used in APERO-check config.
    :param reason: Human-readable failure reason.
    :param obs_path: Observation directory path used by the check.
    :param fail_files: Files that failed or contributed to the failure.
    :param sample_size: Maximum number of files to list.
    :return: Multiline failure message string.
    """
    # Normalize and de-duplicate file paths while preserving order.
    unique = []
    seen = set()
    for item in fail_files:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        unique.append(Path(text))

    # Resolve the shared folder shown to users.
    common_path = str(obs_path)
    if len(unique) > 0:
        try:
            parts = [str(path.parent) for path in unique]
            common_path = os.path.commonpath(parts)
        except Exception:
            common_path = str(unique[0].parent)

    # Start message with a concise summary.
    lines = []
    lines.append(f'{test_key} failed ({reason})')
    lines.append('')
    lines.append(f'Path: {common_path}')
    lines.append('')

    # Add a representative sample of failing files.
    if len(unique) == 0:
        lines.append('File 1: (no matching file rows found)')
        return '\n'.join(lines)

    count = min(max(int(sample_size), 1), len(unique))
    for idx in range(count):
        lines.append(f'File {idx + 1}: {unique[idx].name}')

    # Show truncation when there are more failures than the sample size.
    if len(unique) > count:
        lines.append('...')
        lines.append(f'File N: {unique[-1].name}')

    return '\n'.join(lines)


def build_report(obs_dir: str,
                 passed_lines: List[str],
                 failed_lines: List[str]) -> Tuple[bool, str]:
    """Build a standard APERO-check report block."""
    passed = list(passed_lines or [])
    failed = list(failed_lines or [])
    passed_text = '\n'.join(passed) if passed else '\tNone'
    failed_text = '\n'.join(failed) if failed else '\tNone'
    outmsg = '\n'
    outmsg += '\n' + '*' * 50
    outmsg += f'\nQC for obsdir {obs_dir}'
    outmsg += '\nPassed QC:'
    outmsg += '\n' + passed_text
    outmsg += '\nFailed QC:'
    outmsg += '\n' + failed_text
    outmsg += '\n' + '*' * 50
    outmsg += '\n'
    return len(failed) == 0, outmsg


def load_example_aparams(instrument: str = 'NIRPS_HA') -> dict:
    """Load a lightweight example instrument profile for __main__ tests."""
    mapping = dict(
        NIRPS_HA='nirps_ha_v7.yaml',
        NIRPS_HE='nirps_he_v7.yaml',
    )
    filename = mapping.get(str(instrument).upper(), 'nirps_ha_v7.yaml')
    profile_file = (
        Path(__file__).resolve().parents[2]
        / 'resources'
        / 'aprofile_instruments'
        / filename
    )
    with open(profile_file, 'r', encoding='utf-8') as handle:
        data = yaml.safe_load(handle) or dict()
    if not isinstance(data, dict):
        data = dict()
    data['paths'] = dict(raw='.')
    return data