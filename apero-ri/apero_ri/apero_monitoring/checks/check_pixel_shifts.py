#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reduced APERO check: detector pixel shifts in pp files (PIXEL_SHIFTS)."""

from typing import Tuple

import apero_ri.apero_monitoring.core.red_common as red_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'PIXEL_SHIFTS'
CHECK_HUMAN_NAME = 'Detector Pixel Shifts'
CHECK_TYPE = 'red'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'MANUAL_START',
                      'APERO_START', 'APERO_END']

CHECK.description = """
Checks for detector pixel shifts in the preprocessed (pp) files.

Specifically checks the DETOFFDX and DETOFFDY header keys for any non-zero
values.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=PIXEL_SHIFTS.

If still FALSE please email <CONTACT:C1>.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.EA, starred=True)
clist1.add(contacts.NJC)
clist1.add(contacts.LM)
CHECK.contact_list['C1'] = clist1

# Default header keys and file pattern (overridable from profile config).
_DEFAULT_DX_KEY = 'DETOFFDX'
_DEFAULT_DY_KEY = 'DETOFFDY'
_DEFAULT_PATTERN = '*pp.fits'


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Flag any preprocessed file with a non-zero detector pixel offset."""
    _ = instrument, dbparams
    if not red_common.is_check_enabled(aparams, 'pixel_shifts', default=True):
        return True, 'Skipped pixel_shifts: disabled.'
    # Resolve configuration with sensible defaults.
    dx_key = str(red_common.get_check_value(
        aparams, 'pixel_shifts', ['dx_key'], _DEFAULT_DX_KEY))
    dy_key = str(red_common.get_check_value(
        aparams, 'pixel_shifts', ['dy_key'], _DEFAULT_DY_KEY))
    pattern = str(red_common.get_check_value(
        aparams, 'pixel_shifts', ['file_pattern'], _DEFAULT_PATTERN))
    # Resolve the preprocessed files for this obsdir.
    obs_path, files = red_common.list_pp_files(aparams, obs_dir, pattern)
    if not obs_path.exists():
        return False, (f'Preprocessed directory for {obs_dir} does not exist '
                       f'({obs_path}).')
    if not files:
        return True, (f'No preprocessed files ({pattern}) found in '
                      f'{obs_path}; nothing to check.')
    # Examine each file for a non-zero detector offset.
    passed_lines = []
    failed_lines = []
    for filename in files:
        header = red_common.read_primary_header(filename)
        try:
            dx = float(header.get(dx_key, 0) or 0)
            dy = float(header.get(dy_key, 0) or 0)
        except (TypeError, ValueError):
            failed_lines.append(
                f'\t{filename.name}: could not read {dx_key}/{dy_key}'
            )
            continue
        if dx != 0 or dy != 0:
            failed_lines.append(
                f'\t{filename.name}: pixel shift dx={dx:.4f} dy={dy:.4f}'
            )
        else:
            passed_lines.append(f'\t{filename.name}: no shift')
    return red_common.build_report(obs_dir, passed_lines, failed_lines)


# =============================================================================
# Must put the function to run for this check
# =============================================================================
CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    _instrument = 'NIRPS_HA'
    _obs_dir = '2021-01-01'
    _aparams = red_common.load_example_aparams(_instrument)
    _dbparams = dict()
    _check_dict = {dep: True for dep in CHECK.dependencies}
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict=_check_dict)
    print(CHECK.report())


# =============================================================================
# End of code
# =============================================================================
