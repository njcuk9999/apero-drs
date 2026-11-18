#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reduced APERO check: low SNR in science spectra (LOW_SNR)."""

from typing import Tuple

import apero_ri.apero_monitoring.core.red_common as red_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'LOW_SNR'
CHECK_HUMAN_NAME = 'Low SNR in Science Spectra'
CHECK_TYPE = 'red'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'MANUAL_START',
                      'APERO_START', 'APERO_END']

CHECK.description = """
Checks whether any science files have SNR < 10 in extracted order 15 and 60
(header keys EXTSN015 and EXTSN060).
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with --test=LOW_SNR.

If still FALSE check ARI for previous observations of this object.

First check the APERO object flags spreadsheet. If the object is in this list
with CHECK=LOW_SNR then you can override the value with the APERO check
override code with --test=LOW_SNR.

If the previous observations are always below or around 10, you should bring
this up at the next meeting but override the value and note the object name.

If the weather was terrible or another issue was mentioned in the log that
could explain the low SNR you should bring this up at the next meeting but
override the value, state the object name and the weather-related reason.
Please then reject this file so it is not used in future reductions.

If the previous observations are usually well above 10 and the weather was
not terrible, please report to <CONTACT:C1> stating that the SNR was flagged
as being well below average (give the object name and the SNR usually found
and the SNR for this observation). Please then reject this file.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.CURRENT_OBSERVER, starred=True)
clist1.add(contacts.TELESCOPE_3P6)
clist1.add(contacts.TELESCOPE_DNOS)
clist1.add(contacts.NJC)
clist1.add(contacts.LM)
clist1.add(contacts.FB)
clist1.add(contacts.EA)
clist1.add(contacts.LMI)
clist1.add(contacts.RA)
CHECK.contact_list['C1'] = clist1

# Default configuration: science DPR types, SNR header keys and limits.
_DEFAULT_SCI_TYPES = [
    'OBJ_DARK', 'OBJ_FP', 'OBJ_SKY', 'TELLU_SKY', 'FLUXSTD_SKY',
]
_DEFAULT_SNR_KEYS = ['EXTSN015', 'EXTSN060']
_DEFAULT_SNR_LIMIT = 10.0
_DEFAULT_PATTERN = '*pp_e2dsff_A.fits'


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Flag any science spectrum whose SNR is below the configured minimum."""
    _ = instrument, dbparams
    if not red_common.is_check_enabled(aparams, 'low_snr', default=True):
        return True, 'Skipped low_snr: disabled.'
    # Resolve configuration.
    dpr_key = str(red_common.get_check_value(
        aparams, 'low_snr', ['dpr_key'],
        red_common.get_header_key(aparams, 'dpr_type') or 'DPRTYPE'))
    obj_key = str(red_common.get_check_value(
        aparams, 'low_snr', ['obj_key'], 'DRSOBJN'))
    sci_types = red_common.get_check_value(
        aparams, 'low_snr', ['sci_dprtypes'], _DEFAULT_SCI_TYPES)
    if not isinstance(sci_types, list):
        sci_types = list(_DEFAULT_SCI_TYPES)
    snr_keys = red_common.get_check_value(
        aparams, 'low_snr', ['snr_keys'], _DEFAULT_SNR_KEYS)
    if not isinstance(snr_keys, list):
        snr_keys = list(_DEFAULT_SNR_KEYS)
    snr_limit = float(red_common.get_check_value(
        aparams, 'low_snr', ['snr_limit'], _DEFAULT_SNR_LIMIT))
    pattern = str(red_common.get_check_value(
        aparams, 'low_snr', ['file_pattern'], _DEFAULT_PATTERN))
    # Locate reduced files.
    obs_path, files = red_common.list_red_files(aparams, obs_dir, pattern)
    if not obs_path.exists():
        return False, (f'Reduced directory for {obs_dir} does not exist '
                       f'({obs_path}).')
    if not files:
        return True, (f'No e2dsff science files ({pattern}) found in '
                      f'{obs_path}; nothing to check.')
    passed_lines = []
    failed_lines = []
    for filename in files:
        header = red_common.read_primary_header(filename)
        dpr_type = str(header.get(dpr_key, '') or '').strip()
        if dpr_type not in sci_types:
            continue
        obj_name = str(header.get(obj_key, '') or '').strip() or 'unknown'
        for snr_key in snr_keys:
            raw = header.get(snr_key)
            if raw is None:
                continue
            try:
                snr = float(raw)
            except (TypeError, ValueError):
                continue
            if snr < snr_limit:
                failed_lines.append(
                    f'\t{filename.name} [{obj_name}]: '
                    f'{snr_key}={snr:.1f} < {snr_limit:.1f}'
                )
                break
        else:
            passed_lines.append(
                f'\t{filename.name} [{obj_name}]: SNR ok'
            )
    if not passed_lines and not failed_lines:
        return True, 'No configured science-type files found in obsdir.'
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
