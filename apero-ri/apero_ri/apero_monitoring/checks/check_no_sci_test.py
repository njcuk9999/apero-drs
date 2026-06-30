#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO check for science-file presence."""

from typing import Tuple

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'NO_SCI'
CHECK_HUMAN_NAME = 'Science Presence Check'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['SPIROU', 'NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR']

CHECK.description = """
Check whether any science observations are present for the observation
night.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=NO_SCI.

If still FALSE, verify whether science data should exist and then check
[ESO archives]({links.ESO_ARCHIVES}).

If there is a good reason for no science data, override the check.

If there is science data on ESO archives but not locally, contact
<CONTACT:C1>.

If there is no science data on ESO archives and no clear reason, contact
<CONTACT:C2>.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.TV, starred=True)
clist1.add(contacts.LM)
clist1.add(contacts.NJC)

clist2 = contacts.AperoCheckContactList()
clist2.add(contacts.CURRENT_OBSERVER, starred=True)
clist2.add(contacts.TELESCOPE_3P6)
clist2.add(contacts.TELESCOPE_DNOS)
clist2.add(contacts.NJC)
clist2.add(contacts.LM)
clist2.add(contacts.FB)
clist2.add(contacts.EA)
clist2.add(contacts.LMI)
clist2.add(contacts.RA)

CHECK.contact_list['C1'] = clist1
CHECK.contact_list['C2'] = clist2


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Check that at least one configured science DPR type is present.

    The function classifies each file DPR type into science or non-science
    groups and fails when no science-type files exist for the obsdir.

    :param instrument: APERO instrument name (unused by this check body).
    :param obs_dir: Obsdir identifier currently being validated.
    :param aparams: Hydrated APERO profile parameters.
    :param dbparams: Database parameters (unused by this check body).
    :return: Tuple of pass flag and formatted report text.
    """
    # Keep signature compatibility with the generic check interface.
    _ = instrument, dbparams
    # Allow global enable or disable of this check from profile config.
    if not raw_common.is_check_enabled(aparams, 'no_sci', default=True):
        return True, 'Skipped no_sci: disabled.'
    # Resolve all FITS files for the requested obsdir.
    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    # Fail immediately when the obsdir path is missing.
    if not obs_path.exists():
        return False, f'Observation directory {obs_dir} does not exist.'
    # Fail immediately when no FITS files are available for inspection.
    if len(files) == 0:
        return False, f'No FITS files found in {obs_path}'

    # Load DPR header key and configured science DPR types.
    dpr_key = raw_common.get_header_key(aparams, 'dpr_type')
    science_types = raw_common.get_check_value(aparams,
                                               'no_sci',
                                               ['dprtypes'],
                                               [])
    if isinstance(science_types, list):
        science_types = list(science_types)
    else:
        science_types = []
    # Skip the check when no science DPR configuration exists.
    if dpr_key == '' or len(science_types) == 0:
        return True, 'No science DPR types configured for this check.'

    # Count science and non-science DPR types separately.
    science_counts = dict()
    other_counts = dict()
    for filename in files:
        header = raw_common.read_primary_header(filename)
        dpr_type = str(header.get(dpr_key, '') or '').strip()
        if dpr_type in science_types:
            science_counts[dpr_type] = int(science_counts.get(dpr_type, 0)) + 1
        else:
            other_counts[dpr_type] = int(other_counts.get(dpr_type, 0)) + 1

    # Build pass and fail report lines from the computed counts.
    passed_lines = []
    failed_lines = []
    if len(science_counts) == 0:
        failed_lines.append(f'\tNo science files found for obsdir {obs_dir}')
        for dpr_type, count in sorted(other_counts.items()):
            failed_lines.append(f'\tOther {dpr_type}: {count}')
    else:
        for dpr_type, count in sorted(science_counts.items()):
            passed_lines.append(f'\tScience {dpr_type}: {count}')
        for dpr_type, count in sorted(other_counts.items()):
            passed_lines.append(f'\tOther {dpr_type}: {count}')
    # Return the standard report payload for this check.
    return raw_common.build_report(obs_dir, passed_lines, failed_lines)


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
    _aparams = raw_common.load_example_aparams(_instrument)
    _dbparams = dict()
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict={})
    print(CHECK.report())


# =============================================================================
# End of code
# =============================================================================