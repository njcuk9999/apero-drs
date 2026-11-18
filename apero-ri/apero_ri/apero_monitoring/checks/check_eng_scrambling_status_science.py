#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: scrambling status on science dprtypes."""

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck, SimpleCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links

# Internal unique key used in YAML and monitor records.
CHECK_NAME = 'ENG_SCRAMBLING_STATE'
# Human readable title shown in UI views.
CHECK_HUMAN_NAME = 'ENG: Scrambling Status Science'
# APERO check family (raw/red) used for routing and display.
CHECK_TYPE = 'raw'
# Instruments where this engineering check is valid.
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
# Config test key under apero-checks.eng_test.tests.
TEST_KEY = 'scrambling_status_science'

# Build the runnable check object from metadata above.
CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
# Require upstream checks before evaluating this test.
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']

CHECK.description = """
This engineering sub-test checks AO scrambling status remains enabled.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=ENG_TEST.

If still FALSE, report the failing ENG_TEST details and contact
<CONTACT:C1>.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.LM, starred=True)
clist1.add(contacts.GLC)
clist1.add(contacts.NJC)
clist1.add(contacts.EA)
CHECK.contact_list['C1'] = clist1

# Attach declarative SimpleCheck helper for runtime/docs/admin.
SIMPLE_CHECK = SimpleCheck(CHECK, TEST_KEY)
# Define one input variable and its YAML/header mapping.
SIMPLE_CHECK.data['x'] = dict(
    key='status_key',
    dtype='bool',
    normalize='bool',
)
# Define one input variable and its YAML/header mapping.
SIMPLE_CHECK.data['status_value'] = dict(
    kind='config',
    key='status_value',
    cast='bool',
    default=True,
)
# Restrict evaluation rows using configured filter values.
SIMPLE_CHECK.filters['dpr_type'] = dict(
    logical_key='dpr_type',
    key='dprtypes',
    dtype='str',
    default=['OBJECT,FP', 'OBJECT,SKY', 'TELLURIC,SKY'],
)
# Core boolean logic: True means pass, False means fail.
SIMPLE_CHECK.func = lambda x, status_value, **_: x == status_value
# Pass message template displayed when logic passes.
SIMPLE_CHECK.pmsg = '{test_key} okay on filtered rows.'
# Fail reason template displayed when logic fails.
SIMPLE_CHECK.fmsg = 'filtered rows contain values != {status_value}'
# Human-readable logic string for docs and admin displays.
SIMPLE_CHECK.desc = (
    'np.all({x} == {status_value}) on dprtypes {dpr_type}'
)


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
