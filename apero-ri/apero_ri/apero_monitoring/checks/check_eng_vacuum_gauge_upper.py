#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: vacuum gauge upper limit."""

from typing import Tuple

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck

# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'ENG_VAC_GAUGE_UPPER'
CHECK_HUMAN_NAME = 'ENG: Vacuum Gauge Upper'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'vacuum_gauge_upper'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']


def _description(cfg: dict) -> str:
    """Build a concrete logic description from this test config."""
    logic = (
        'np.nanmax(' + str(cfg.get('key1', '')) + ') < '
        + str(cfg.get('val1', ''))
    )
    out = 'Performs the following test\n\n'
    out += '```python\n'
    out += logic + '\n'
    out += '```'
    return out


def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Run vacuum-gauge upper-limit validation for one obsdir.

    :param instrument: Active instrument key for the current profile.
    :param obs_dir: Observation-directory/night identifier.
    :param aparams: APERO runtime parameters and test configuration.
    :param dbparams: Runtime/database context passed by monitor task.
    :returns: Tuple ``(is_ok, message)`` for pass/skip/failure reporting.
    """
    _ = instrument, dbparams
    cfg = raw_common.get_check_value(aparams,
                                     'eng_test',
                                     ['tests', TEST_KEY],
                                     dict())
    if not isinstance(cfg, dict) or len(cfg) == 0:
        return True, f'Skipped {TEST_KEY}: not configured.'

    CHECK.description = _description(cfg)
    if not bool(cfg.get('enabled', True)):
        return True, f'Skipped {TEST_KEY}: disabled.'

    key1 = str(cfg.get('key1', '')).strip()
    limit = float(cfg.get('val1', np.nan))
    if key1 == '':
        return False, f'{TEST_KEY} missing key1.'

    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    if len(files) == 0:
        return False, f'No FITS files found in {obs_dir}.'

    header_defs = dict()
    header_defs[key1] = dict(key=key1, dtype='float')
    table, masks = raw_common.load_header_table(files, header_defs)

    use = masks[key1]
    x = np.array(table[key1][use], dtype=float)
    if len(x) == 0:
        return True, f'Skipped {TEST_KEY}: no valid rows.'

    metric = float(np.nanmax(x))
    if metric < limit:
        return True, f'{TEST_KEY} okay ({metric:.2E} < {limit:.2E}).'
    use_files = raw_common.files_from_mask(table, use)
    reason = f'{metric:.2E} >= {limit:.2E}'
    message = raw_common.format_failed_file_message(
        TEST_KEY,
        reason,
        obs_path,
        use_files,
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
