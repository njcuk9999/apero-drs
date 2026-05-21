#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: scrambling status on science dprtypes."""

from typing import Tuple

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck

CHECK_NAME = 'ENG_SCRAMBLING_STATE'
CHECK_HUMAN_NAME = 'ENG: Scrambling Status Science'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'scrambling_status_science'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']


def _to_bool(value: object) -> bool:
    text = str(value).strip().lower()
    return text in ['1', 'true', 'yes', 'on', 't']


def _description(cfg: dict) -> str:
    logic = (
        'np.all(' + str(cfg.get('key1', '')) + ' == '
        + str(cfg.get('val1', '')) + ') on dprtypes '
        + str(cfg.get('dprtypes', []))
    )
    return 'Performs the following test\n\n```python\n' + logic + '\n```'


def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Run scrambling-state validation for science dprtypes in one obsdir.

    This check reads a boolean status header and verifies that all rows
    matching configured science DPRTYPE values have the configured target
    state. The return value follows the APERO monitor convention.

    :param instrument: Active instrument key (kept for API consistency).
    :param obs_dir: Observation-directory/night identifier to inspect.
    :param aparams: APERO runtime parameters and check configuration tree.
    :param dbparams: Database/runtime context (unused by this check).
    :returns: Tuple ``(is_ok, message)`` where ``is_ok`` is ``True`` for
              pass or intentional skip, and ``False`` for a hard failure.
    """
    # Keep API signature compatibility even when some inputs are unused.
    _ = instrument, dbparams
    # Read check-specific configuration from the eng_test section.
    cfg = raw_common.get_check_value(aparams,
                                     'eng_test',
                                     ['tests', TEST_KEY],
                                     dict())
    # Missing config means this check is not enabled for this profile.
    if not isinstance(cfg, dict) or len(cfg) == 0:
        return True, f'Skipped {TEST_KEY}: not configured.'
    # Expose the effective test logic string in UI documentation.
    CHECK.description = _description(cfg)
    # Respect explicit enabled/disabled switch in the YAML configuration.
    if not _to_bool(cfg.get('enabled', True)):
        return True, f'Skipped {TEST_KEY}: disabled.'
    # Pull configured header keys, boolean target and row filter dprtypes.
    key1 = str(cfg.get('key1', '')).strip()
    target = _to_bool(cfg.get('val1', True))
    dprtypes = cfg.get('dprtypes', [])
    dprkey = raw_common.get_header_key(aparams, 'dpr_type')
    # Without a status key we cannot evaluate this engineering test.
    if key1 == '':
        return False, f'{TEST_KEY} missing key1.'
    # No DPRTYPE filter means there is no science subset to validate.
    if not isinstance(dprtypes, list) or len(dprtypes) == 0:
        return True, f'Skipped {TEST_KEY}: no dprtypes configured.'
    # Abort if the profile does not define the DPRTYPE header mapping.
    if dprkey.strip() == '':
        return False, f'{TEST_KEY} requires dpr_type header key.'
    # Resolve obsdir path and the list of FITS files to inspect.
    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    # Empty night directories are reported as hard failures.
    if len(files) == 0:
        return False, f'No FITS files found in {obs_dir}.'
    # Define exactly which headers to load and how to cast each column.
    defs = dict()
    defs[key1] = dict(key=key1, dtype='bool')
    defs[dprkey] = dict(key=dprkey, dtype='str')
    # Read headers once and keep valid-row masks for each column.
    table, masks = raw_common.load_header_table(files, defs)
    # Start with rows where both required headers are present.
    use = masks[key1] & masks[dprkey]
    # Restrict to science dprtypes configured for this check.
    use &= np.isin(table[dprkey], dprtypes)
    # Convert full status column to booleans for robust comparisons.
    values = np.array(table[key1]).astype(bool)
    # Keep only rows participating in this science-state decision.
    x = values[use]
    # If no row matches the filter, skip to avoid false hard failures.
    if len(x) == 0:
        return True, f'Skipped {TEST_KEY}: no filtered rows.'
    # Pass only when every selected row matches the configured target.
    ok = bool(np.all(x == target))
    if ok:
        return True, f'{TEST_KEY} okay on filtered rows.'
    # Build a row mask of true failures for file-level diagnostics.
    fail_use = use & (values != target)
    # Map failed rows back to source FITS filenames for the report.
    fail_files = raw_common.files_from_mask(table, fail_use)
    # Build concise reason text for the formatted multiline message.
    reason = f'filtered rows contain values != {target}'
    # Create a message with path + representative failing files.
    message = raw_common.format_failed_file_message(
        TEST_KEY,
        reason,
        obs_path,
        fail_files,
    )
    return False, message


CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    _instrument = 'NIRPS_HA'
    _obs_dir = '2021-01-01'
    _aparams = raw_common.load_example_aparams(_instrument)
    _dbparams = dict()
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict={})
    print(CHECK.report())


# =============================================================================
# End of code
# =============================================================================
