#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: enclosure setpoint offset."""

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck, SimpleCheck

# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'ENG_ENC_SETPOINT_OFFSET'
CHECK_HUMAN_NAME = 'ENG: Enclosure Setpoint Offset'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'enclosure_setpoint_offset'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']
SIMPLE_CHECK = SimpleCheck(CHECK, TEST_KEY)
SIMPLE_CHECK.data['x'] = dict(
    key=['sensor_key', 'key1'],
    dtype='float',
    normalize='float',
)
SIMPLE_CHECK.data['y'] = dict(
    key=['setpoint_key', 'key2'],
    dtype='float',
    normalize='float',
)
SIMPLE_CHECK.data['limit'] = dict(
    kind='config',
    key=['limit', 'val1'],
    cast='float',
    default=0.1,
)
SIMPLE_CHECK.calc['metric'] = (
    lambda x, y, **_: float(np.abs(np.nanmean(x - y)))
)
SIMPLE_CHECK.func = lambda metric, limit, **_: metric < limit
SIMPLE_CHECK.pmsg = '{test_key} okay ({metric:.2E} < {limit:.2E}).'
SIMPLE_CHECK.fmsg = '{metric:.2E} >= {limit:.2E}'
SIMPLE_CHECK.desc = 'np.abs(np.nanmean({x} - {y})) < {limit}'


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
