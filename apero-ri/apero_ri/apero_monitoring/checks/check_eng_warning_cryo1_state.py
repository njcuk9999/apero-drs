#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: warning cryo1 state."""

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck, SimpleCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links

# Internal unique key used in YAML and monitor records.
CHECK_NAME = 'ENG_WARN_CRYO1'
# Human readable title shown in UI views.
CHECK_HUMAN_NAME = 'ENG: Warning Cryo1 State'
# APERO check family (raw/red) used for routing and display.
CHECK_TYPE = 'raw'
# Instruments where this engineering check is valid.
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
# Config test key under apero-checks.eng_test.tests.
TEST_KEY = 'warning_cryo1_state'

# Build the runnable check object from metadata above.
CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
# Require upstream checks before evaluating this test.
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']

CHECK.description = """
This engineering sub-test checks cryocooler 1 warning flag activity.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=ENG_TEST.

If still FALSE, report the failing ENG_TEST details and contact
<CONTACT:C1>.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.LM, starred=True)
clist1.add(contacts.PV)
clist1.add(contacts.NJC)
clist1.add(contacts.EA)
CHECK.contact_list['C1'] = clist1

# Attach declarative SimpleCheck helper for runtime/docs/admin.
SIMPLE_CHECK = SimpleCheck(CHECK, TEST_KEY)
# Define one input variable and its YAML/header mapping.
SIMPLE_CHECK.data['x'] = dict(
    key='status_key',
    dtype='str',
    normalize='strip',
)
# Define one input variable and its YAML/header mapping.
SIMPLE_CHECK.data['target'] = dict(
    kind='config',
    key='target',
    cast='str',
    default='',
)
# Core boolean logic: True means pass, False means fail.
SIMPLE_CHECK.func = lambda x, target, **_: x == target
# Pass message template displayed when logic passes.
SIMPLE_CHECK.pmsg = "{test_key} okay (all == {target!r})."
# Fail reason template displayed when logic fails.
SIMPLE_CHECK.fmsg = "found values != {target!r}"
# Human-readable logic string for docs and admin displays.
SIMPLE_CHECK.desc = "np.all(np.char.strip({x}) == {target!r})"


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
