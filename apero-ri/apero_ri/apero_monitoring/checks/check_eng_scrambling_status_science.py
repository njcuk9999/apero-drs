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
    _ = instrument, dbparams
    cfg = raw_common.get_check_value(aparams,
                                     'eng_test',
                                     ['tests', TEST_KEY],
                                     dict())
    if not isinstance(cfg, dict) or len(cfg) == 0:
        return True, f'Skipped {TEST_KEY}: not configured.'
    CHECK.description = _description(cfg)
    if not _to_bool(cfg.get('enabled', True)):
        return True, f'Skipped {TEST_KEY}: disabled.'
    key1 = str(cfg.get('key1', '')).strip()
    target = _to_bool(cfg.get('val1', True))
    dprtypes = cfg.get('dprtypes', [])
    dprkey = raw_common.get_header_key(aparams, 'dpr_type')
    if key1 == '':
        return False, f'{TEST_KEY} missing key1.'
    if not isinstance(dprtypes, list) or len(dprtypes) == 0:
        return True, f'Skipped {TEST_KEY}: no dprtypes configured.'
    if dprkey.strip() == '':
        return False, f'{TEST_KEY} requires dpr_type header key.'
    _, files = raw_common.list_obsdir_files(aparams, obs_dir)
    if len(files) == 0:
        return False, f'No FITS files found in {obs_dir}.'
    defs = dict()
    defs[key1] = dict(key=key1, dtype='bool')
    defs[dprkey] = dict(key=dprkey, dtype='str')
    table, masks = raw_common.load_header_table(files, defs)
    use = masks[key1] & masks[dprkey]
    use &= np.isin(table[dprkey], dprtypes)
    x = np.array(table[key1][use])
    if len(x) == 0:
        return True, f'Skipped {TEST_KEY}: no filtered rows.'
    ok = bool(np.all(x == target))
    if ok:
        return True, f'{TEST_KEY} okay on filtered rows.'
    return False, f'{TEST_KEY} failed on filtered rows.'


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
