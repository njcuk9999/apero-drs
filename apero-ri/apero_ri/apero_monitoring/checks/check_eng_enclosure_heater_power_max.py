#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: enclosure heater power max."""

from typing import Tuple

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck

CHECK_NAME = 'ENG_ENC_HEATER_MAX'
CHECK_HUMAN_NAME = 'ENG: Enclosure Heater Power Max'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'enclosure_heater_power_max'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']


def _description(cfg: dict) -> str:
    logic = (
        'np.nanmax(' + str(cfg.get('key1', '')) + ') < '
        + str(cfg.get('val1', ''))
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
    limit = float(cfg.get('val1', np.nan))
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
    metric = float(np.nanmax(x))
    if metric < limit:
        return True, f'{TEST_KEY} okay ({metric:.1f} < {limit:.1f}).'
    return False, f'{TEST_KEY} failed ({metric:.1f} >= {limit:.1f}).'


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
