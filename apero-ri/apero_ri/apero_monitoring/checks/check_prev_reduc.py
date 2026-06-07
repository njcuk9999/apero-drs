#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reduced APERO check: every recent raw file has a pp file (PREV_REDUC)."""

from pathlib import Path
from typing import List, Optional, Set, Tuple

import numpy as np

import apero_ri.apero_monitoring.core.red_common as red_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'PREV_REDUC'
CHECK_HUMAN_NAME = 'Previous Reduction Check'
CHECK_TYPE = 'red'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'MANUAL_START',
                      'APERO_START', 'APERO_END']

CHECK.description = """
Checks whether there are any raw files without any reduced products.

Every raw file must have a corresponding preprocessed (pp) file for the
previous 7 days.  Every subsequent day (up to 7 days after the failure) will
also fail until the missing file is processed.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=PREV_REDUC.

If still FALSE you should get a list of files that are missing.

Please try re-running the manual trigger on this specific observation
directory.

If still FALSE after re-running the manual trigger please check the DPR TYPE
of the files that are missing (e.g. dfits {{filename}} | fitsort dpr.type).

Please locate the preprocessing log for these files (under the APERO
msg/processing/ directory, search for the file identifier in the relevant
apero_preprocess log files).

After re-running the manual trigger and locating the log files, please email
<CONTACT:C1> with the list of missing files and the relevant log content.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.NJC, starred=True)
clist1.add(contacts.EA)
clist1.add(contacts.LM)
CHECK.contact_list['C1'] = clist1

_DEFAULT_LOOKBACK_DAYS = 7
_DEFAULT_RAW_SUFFIX = '.fits'
_DEFAULT_PP_SUFFIX = '_pp.fits'


# =============================================================================
# Internal helpers
# =============================================================================
def _file_prefix(filename: Path, pp_suffix: str) -> str:
    """Return the stem identifier for cross-matching raw vs pp files."""
    name = filename.name
    # Strip the pp suffix when present, otherwise the full suffix.
    if name.endswith(pp_suffix):
        return name[: -len(pp_suffix)]
    return filename.stem


def _collect_prefixes(directory: Path,
                      suffix: str,
                      reject_set: Set[str],
                      lookback_days: Optional[int] = None) -> List[str]:
    """Walk ``directory`` and collect file prefixes matching ``suffix``.

    When ``lookback_days`` is given, only files with an mtime within that many
    days of the most-recently-modified file are included.
    """
    if not directory.exists():
        return []
    try:
        files = sorted(directory.rglob(f'*{suffix}'))
    except Exception:
        return []
    if not files:
        return []
    # Determine the cutoff mtime (most-recent minus lookback window).
    cutoff: Optional[float] = None
    if lookback_days is not None:
        try:
            mtimes = [f.stat().st_mtime for f in files]
            latest = max(mtimes)
            cutoff = latest - lookback_days * 86400.0
        except Exception:
            cutoff = None
    prefixes = []
    for fpath in files:
        try:
            if cutoff is not None and fpath.stat().st_mtime < cutoff:
                continue
        except Exception:
            continue
        prefix = _file_prefix(fpath, _DEFAULT_PP_SUFFIX).upper()
        if prefix in reject_set:
            continue
        prefixes.append(prefix)
    return prefixes


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Return False when any recent raw file has no corresponding pp file."""
    _ = dbparams
    if not red_common.is_check_enabled(aparams, 'prev_reduc', default=True):
        return True, 'Skipped prev_reduc: disabled.'
    lookback = int(red_common.get_check_value(
        aparams, 'prev_reduc', ['lookback_days'], _DEFAULT_LOOKBACK_DAYS))
    raw_suffix = str(red_common.get_check_value(
        aparams, 'prev_reduc', ['raw_suffix'], _DEFAULT_RAW_SUFFIX))
    pp_suffix = str(red_common.get_check_value(
        aparams, 'prev_reduc', ['pp_suffix'], _DEFAULT_PP_SUFFIX))
    # Load the ARI reject list to exclude already-rejected files.
    reject_set = red_common.get_reject_identifiers(aparams, instrument)
    # Collect raw and pp prefixes from the profile directories.
    raw_dir = red_common.get_raw_dir(aparams)
    pp_dir = red_common.get_pp_dir(aparams)
    if raw_dir is None:
        return False, 'PATH.RAW is not configured; cannot run prev_reduc check.'
    if pp_dir is None:
        return False, 'PATH.PP is not configured; cannot run prev_reduc check.'
    # Scan within the specific obsdir only (mirroring the original).
    raw_obs = raw_dir / str(obs_dir)
    pp_obs = pp_dir / str(obs_dir)
    raw_prefixes = _collect_prefixes(raw_obs, raw_suffix, reject_set,
                                     lookback_days=lookback)
    pp_prefixes_set = set(
        _collect_prefixes(pp_obs, pp_suffix, set(), lookback_days=None)
    )
    if not raw_prefixes:
        return True, f'No raw files found in {raw_obs} within {lookback} days.'
    # Compare prefix lists.
    missing = [p for p in raw_prefixes if p not in pp_prefixes_set]
    if not missing:
        passed_lines = [
            f'\tAll {len(raw_prefixes)} raw file(s) have pp equivalents.'
        ]
        return red_common.build_report(obs_dir, passed_lines, [])
    sample = missing[:8]
    extra = len(missing) - len(sample)
    failed_lines = [f'\tMissing pp for {len(missing)} raw file(s):']
    for name in sample:
        failed_lines.append(f'\t  {name}')
    if extra > 0:
        failed_lines.append(f'\t  ... and {extra} more')
    return red_common.build_report(obs_dir, [], failed_lines)


# =============================================================================
# Must put the function to run for this check
# =============================================================================
CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    _instrument = 'NIRPS_HA'
    _obs_dir = '2021-01-01'
    _aparams = red_common.load_example_aparams(_instrument)
    _dbparams = dict()
    _check_dict = {dep: True for dep in CHECK.dependencies}
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict=_check_dict)
    print(CHECK.report())


# =============================================================================
# End of code
# =============================================================================
