#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: vacuum gauge upper limit."""

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck, SimpleCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links

# =============================================================================
# Define variables
# =============================================================================
# Internal unique key used in YAML and monitor records.
CHECK_NAME = 'ENG_VAC_GAUGE_UPPER'
# Human readable title shown in UI views.
CHECK_HUMAN_NAME = 'ENG: Vacuum Gauge Upper'
# APERO check family (raw/red) used for routing and display.
CHECK_TYPE = 'raw'
# Instruments where this engineering check is valid.
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
# Config test key under apero-checks.eng_test.tests.
TEST_KEY = 'vacuum_gauge_upper'

# Build the runnable check object from metadata above.
CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
# Require upstream checks before evaluating this test.
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']

CHECK.description = """
This engineering sub-test checks that vacuum gauge pressure stays below
limit.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=ENG_TEST.

If still FALSE, report the failing ENG_TEST details and contact
<CONTACT:C1>.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.EA, starred=True)
clist1.add(contacts.LM)
clist1.add(contacts.NJC)
CHECK.contact_list['C1'] = clist1

# Attach declarative SimpleCheck helper for runtime/docs/admin.
SIMPLE_CHECK = SimpleCheck(CHECK, TEST_KEY)
# Define one input variable and its YAML/header mapping.
SIMPLE_CHECK.data['x'] = dict(
    key='metric_key',
    dtype='float',
    normalize='float',
)
# Define one input variable and its YAML/header mapping.
SIMPLE_CHECK.data['limit'] = dict(
    kind='config',
    key='limit',
    cast='float',
    default=1.0e-4,
)
# Define one derived variable used by the logic function.
SIMPLE_CHECK.calc['metric'] = lambda x, **_: float(np.nanmax(x))
# Core boolean logic: True means pass, False means fail.
SIMPLE_CHECK.func = lambda metric, limit, **_: metric < limit
# Pass message template displayed when logic passes.
SIMPLE_CHECK.pmsg = '{test_key} okay ({metric:.2E} < {limit:.2E}).'
# Fail reason template displayed when logic fails.
SIMPLE_CHECK.fmsg = '{metric:.2E} >= {limit:.2E}'
# Human-readable logic string for docs and admin displays.
SIMPLE_CHECK.desc = 'np.nanmax({x}) < {limit}'


# Register SimpleCheck runner as the check execution function.
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
