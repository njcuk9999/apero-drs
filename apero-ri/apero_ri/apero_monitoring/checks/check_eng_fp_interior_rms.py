#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Engineering check: FP interior RMS."""

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck, SimpleCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links

CHECK_NAME = 'ENG_FP_INTERIOR_RMS'
CHECK_HUMAN_NAME = 'ENG: FP Interior RMS'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']
TEST_KEY = 'fp_interior_rms'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'CALIB_TEST']

CHECK.description = """
This engineering sub-test checks Fabry-Perot interior temperature
stability.
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

SIMPLE_CHECK = SimpleCheck(CHECK, TEST_KEY)
SIMPLE_CHECK.data['x'] = dict(
    key='metric_key',
    dtype='float',
    normalize='float',
)
SIMPLE_CHECK.data['limit'] = dict(
    kind='config',
    key='limit',
    cast='float',
    default=1.0e-2,
)
SIMPLE_CHECK.calc['metric'] = lambda x, **_: float(np.nanstd(x))
SIMPLE_CHECK.func = lambda metric, limit, **_: metric < limit
SIMPLE_CHECK.pmsg = '{test_key} okay ({metric:.2E} < {limit:.2E}).'
SIMPLE_CHECK.fmsg = '{metric:.2E} >= {limit:.2E}'
SIMPLE_CHECK.desc = 'np.nanstd({x}) < {limit}'


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
