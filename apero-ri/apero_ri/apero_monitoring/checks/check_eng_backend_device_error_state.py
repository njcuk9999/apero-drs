#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: backend device error state."""

from typing import Tuple

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck

CHECK_NAME = 'ENG_BACKEND_ERROR_STATE'
CHECK_HUMAN_NAME = 'ENG: Backend Device Error State'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'backend_device_error_state'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']


def _description(cfg: dict) -> str:
    logic = (
        'np.all(np.char.upper(np.char.strip(' + str(cfg.get('key1', ''))
        + ')) != np.char.upper(' + repr(str(cfg.get('val1', ''))) + '))'
    )
    return 'Performs the following test\n\n```python\n' + logic + '\n```'


def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Run backend-device error-state validation for one observation night.

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
    target = str(cfg.get('val1', 'NOK')).strip().upper()
    if key1 == '':
        return False, f'{TEST_KEY} missing key1.'
    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    if len(files) == 0:
        return False, f'No FITS files found in {obs_dir}.'
    defs = dict()
    defs[key1] = dict(key=key1, dtype='str')
    table, masks = raw_common.load_header_table(files, defs)
    values = np.char.upper(
        np.char.strip(np.array(table[key1]).astype(str))
    )
    use = masks[key1]
    x = values[use]
    if len(x) == 0:
        return True, f'Skipped {TEST_KEY}: no valid rows.'
    ok = bool(np.all(x != target))
    if ok:
        return True, f'{TEST_KEY} okay (none == {target!r}).'
    fail_use = use & (values == target)
    fail_files = raw_common.files_from_mask(table, fail_use)
    reason = f'found value == {target!r}'
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
