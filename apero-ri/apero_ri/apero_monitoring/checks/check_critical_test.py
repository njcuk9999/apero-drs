#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO check: critical instrument checks (CRITICAL_TEST)."""

import os
from pathlib import Path
from typing import Tuple

import pandas as pd
from astropy.time import Time

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'CRITICAL_TEST'
CHECK_HUMAN_NAME = 'Critical Instrument Check'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

# Obsdir dates before this are automatically passed (no critical-check data).
_FIRST_TEST_DATE = Time('2025-08-25T00:00:00', format='fits')

# check_status.csv column type value matched by this check.
_DESC_TYPE = 'raw'

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR']

CHECK.description = """
Checks instrument-critical status flags for this observation night using the
critical-check CSV file (PATH.CRITICAL_CHECK / critical csv file).  Each flag
listed in the description CSV that has type "raw" must be True for this check
to pass.

If PATH.CRITICAL_CHECK is not configured, the check passes automatically.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=CRITICAL_TEST.

Review the critical check CSV for the failing night and identify which
instrument flag is False.  Contact the appropriate support team.

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
    """Return whether all 'raw'-type critical flags pass for this obsdir."""
    _ = instrument, dbparams

    # Optional: if PATH.CRITICAL_CHECK is not set, pass automatically.
    critical_dir = raw_common.get_critical_check_dir(aparams)
    if critical_dir is None:
        return True, 'PATH.CRITICAL_CHECK not configured; critical check skipped.'

    # Get filenames from apero-checks yaml config (with defaults).
    csv_name = str(raw_common.get_check_value(
        aparams, 'critical_check', ['critical csv file'], 'check_status.csv'))
    desc_name = str(raw_common.get_check_value(
        aparams, 'critical_check', ['critical desc file'],
        'critical_checks_description.csv'))

    # Blank values (spirou profiles) mean skip.
    if not csv_name.strip() or not desc_name.strip():
        return True, 'Critical csv/desc file not configured; check skipped.'

    csv_file = str(critical_dir / csv_name)
    desc_file = str(critical_dir / desc_name)

    return _run_critical(obs_dir, csv_file, desc_file, _DESC_TYPE)


# =============================================================================
# Shared logic (mirrors critical_test.py from apero-utils)
# =============================================================================
def _run_critical(obs_dir: str, csv_file: str, desc_file: str,
                  desc_type: str) -> Tuple[bool, str]:
    """Run the critical-check logic for one obs_dir and desc type."""
    mr_obsdir = Time(obs_dir + 'T00:00:00', format='fits')
    if mr_obsdir < _FIRST_TEST_DATE:
        return True, (f'CRITICAL TEST: {obs_dir} is before first test date '
                      f'{_FIRST_TEST_DATE.fits}; automatically passing.')

    # Allow home-dir fallback for paths only accessible on the NIRPS system.
    if not os.path.exists(csv_file):
        csv_file = os.path.expanduser('~') + csv_file
        desc_file = os.path.expanduser('~') + desc_file

    try:
        df = pd.read_csv(csv_file, index_col=0)
    except Exception as exc:
        return False, f'CRITICAL TEST: Could not read csv {csv_file}: {exc}'

    try:
        df_desc = pd.read_csv(desc_file)
    except Exception as exc:
        return False, f'CRITICAL TEST: Could not read desc {desc_file}: {exc}'

    if obs_dir not in df.index:
        return False, (f'CRITICAL TEST: No entry for {obs_dir} in {csv_file}.')

    row = df.loc[obs_dir]
    passed = True
    msgs = []
    for _, desc in df_desc.iterrows():
        check_name = desc['name']
        check_desc = desc['description']
        if 'type' in desc and desc['type'] != desc_type:
            continue
        if check_name not in row:
            msgs.append(f'CRITICAL TEST: {check_name} missing from csv.')
            passed = False
        elif not row[check_name]:
            msgs.append(f'CRITICAL TEST: {check_name} FAILED — {check_desc}')
            passed = False
        else:
            msgs.append(f'CRITICAL TEST: {check_name} passed — {check_desc}')

    return passed, '\n'.join(msgs)


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
