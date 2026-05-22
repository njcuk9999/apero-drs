#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: FP exterior range."""

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck, SimpleCheck

CHECK_NAME = 'ENG_FP_EXTERIOR_RANGE'
CHECK_HUMAN_NAME = 'ENG: FP Exterior Range'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'fp_exterior_range'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']
SIMPLE_CHECK = SimpleCheck(CHECK, TEST_KEY)
SIMPLE_CHECK.data['x'] = dict(
    key=['metric_key', 'key1'],
    dtype='float',
    normalize='float',
)
SIMPLE_CHECK.data['low'] = dict(
    kind='config',
    key=['lower_limit', 'val1'],
    cast='float',
    default=23.496,
)
SIMPLE_CHECK.data['high'] = dict(
    kind='config',
    key=['upper_limit', 'val2'],
    cast='float',
    default=24.504,
)
SIMPLE_CHECK.calc['xmin'] = lambda x, **_: float(np.nanmin(x))
SIMPLE_CHECK.calc['xmax'] = lambda x, **_: float(np.nanmax(x))
SIMPLE_CHECK.func = (
    lambda xmin, xmax, low, high, **_: (xmin > low) and (xmax < high)
)
SIMPLE_CHECK.pmsg = '{test_key} okay ({xmin:.3f}-{xmax:.3f}).'
SIMPLE_CHECK.fmsg = (
    'range {xmin:.3f}-{xmax:.3f} outside {low:.3f}-{high:.3f}'
)
SIMPLE_CHECK.desc = (
    'np.nanmin({x}) > {low} and np.nanmax({x}) < {high}'
)


CHECK.func = SIMPLE_CHECK.run


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
