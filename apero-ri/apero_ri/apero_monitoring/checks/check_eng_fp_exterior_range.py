#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: FP exterior range."""

from typing import Tuple

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck

CHECK_NAME = 'ENG_FP_EXTERIOR_RANGE'
CHECK_HUMAN_NAME = 'ENG: FP Exterior Range'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'fp_exterior_range'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']


def _description(cfg: dict) -> str:
    logic = (
        'np.nanmin(' + str(cfg.get('key1', '')) + ') > '
        + str(cfg.get('val1', '')) + ' and '
        + 'np.nanmax(' + str(cfg.get('key1', '')) + ') < '
        + str(cfg.get('val2', ''))
    )
    return 'Performs the following test\n\n```python\n' + logic + '\n```'


def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
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
    low = float(cfg.get('val1', -np.inf))
    high = float(cfg.get('val2', np.inf))
    if key1 == '':
        return False, f'{TEST_KEY} missing key1.'
    _, files = raw_common.list_obsdir_files(aparams, obs_dir)
    if len(files) == 0:
        return False, f'No FITS files found in {obs_dir}.'
    defs = dict()
    defs[key1] = dict(key=key1, dtype='float')
    table, masks = raw_common.load_header_table(files, defs)
    x = np.array(table[key1][masks[key1]], dtype=float)
    if len(x) == 0:
        return True, f'Skipped {TEST_KEY}: no valid rows.'
    xmin = float(np.nanmin(x))
    xmax = float(np.nanmax(x))
    ok = xmin > low and xmax < high
    if ok:
        return True, f'{TEST_KEY} okay ({xmin:.3f}-{xmax:.3f}).'
    return False, f'{TEST_KEY} failed ({xmin:.3f}-{xmax:.3f}).'


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
