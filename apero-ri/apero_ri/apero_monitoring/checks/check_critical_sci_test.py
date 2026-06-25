#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO check: critical science checks (CRITICAL_SCI_TEST)."""

from typing import Tuple

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links
from apero_ri.apero_monitoring.checks.check_critical_test import _run_critical


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'CRITICAL_SCI_TEST'
CHECK_HUMAN_NAME = 'Critical Science Check'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

# check_status.csv column type value matched by this check.
_DESC_TYPE = 'sci'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR']

CHECK.description = """
Checks science-critical status flags for this observation night using the
critical-check CSV file (PATH.CRITICAL_CHECK / critical csv file).  Each flag
listed in the description CSV that has type "sci" must be True for this check
to pass.

If PATH.CRITICAL_CHECK is not configured, the check passes automatically.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=CRITICAL_SCI_TEST.

Review the critical check CSV for the failing night and identify which
science flag is False.  Contact the appropriate support team.

If still FALSE after investigation, please contact <CONTACT:C1>.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.NJC, starred=True)
clist1.add(contacts.LM)
clist1.add(contacts.EA)
CHECK.contact_list['C1'] = clist1


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Return whether all 'sci'-type critical flags pass for this obsdir."""
    _ = instrument, dbparams

    critical_dir = raw_common.get_critical_check_dir(aparams)
    if critical_dir is None:
        return True, 'PATH.CRITICAL_CHECK not configured; critical sci check skipped.'

    csv_name = str(raw_common.get_check_value(
        aparams, 'critical_check', ['critical csv file'], 'check_status.csv'))
    desc_name = str(raw_common.get_check_value(
        aparams, 'critical_check', ['critical desc file'],
        'critical_checks_description.csv'))

    if not csv_name.strip() or not desc_name.strip():
        return True, 'Critical csv/desc file not configured; check skipped.'

    csv_file = str(critical_dir / csv_name)
    desc_file = str(critical_dir / desc_name)

    return _run_critical(obs_dir, csv_file, desc_file, _DESC_TYPE)


# =============================================================================
# Must put the function to run for this check
# =============================================================================
CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    _aparams = raw_common.load_example_aparams('NIRPS_HA')
    _obs_dir = '2025-09-01'
    _dbparams = dict()
    _check_dict = {dep: True for dep in CHECK.dependencies}
    CHECK('NIRPS_HA', _obs_dir, _aparams, _dbparams, check_dict=_check_dict)
    print(CHECK.report())
