#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO check for required calibration DPR types."""

from typing import Tuple

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'CALIB_TEST'
CHECK_HUMAN_NAME = 'Calibration Presence Check'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['SPIROU', 'NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR']


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Check that required calibration DPR types are present in one obsdir.

    The function counts file occurrences for each configured calibration DPR
    type and reports missing categories as failures.

    :param instrument: APERO instrument name (unused by this check body).
    :param obs_dir: Obsdir identifier currently being validated.
    :param aparams: Hydrated APERO profile parameters.
    :param dbparams: Database parameters (unused by this check body).
    :return: Tuple of pass flag and formatted report text.
    """
    # Keep signature compatibility with the generic check interface.
    _ = instrument, dbparams
    # Allow global enable or disable of this check from profile config.
    if not raw_common.is_check_enabled(aparams, 'calib_test', default=True):
        return True, 'Skipped calib_test: disabled.'
    # Resolve all FITS files for the requested obsdir.
    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    # Fail immediately when the obsdir path is missing.
    if not obs_path.exists():
        return False, f'Observation directory {obs_dir} does not exist.'
    # Fail immediately when no FITS files are available for inspection.
    if len(files) == 0:
        return False, f'No FITS files found in {obs_path}'

    # Load DPR header key and required calibration DPR types.
    dpr_key = raw_common.get_header_key(aparams, 'dpr_type')
    required = raw_common.get_check_value(aparams,
                                          'calib_test',
                                          ['required_dprtypes'],
                                          [])
    required = list(required) if isinstance(required, list) else []
    # Skip the check when no calibration DPR configuration exists.
    if dpr_key == '' or len(required) == 0:
        return True, 'No calibration DPR types configured for this check.'

    # Count observed DPR type values across files.
    counts = dict()
    for filename in files:
        header = raw_common.read_primary_header(filename)
        dpr_type = str(header.get(dpr_key, '') or '').strip()
        if dpr_type == '':
            continue
        counts[dpr_type] = int(counts.get(dpr_type, 0)) + 1

    # Build pass or fail lines for each required DPR type.
    passed_lines = []
    failed_lines = []
    for dpr_type in required:
        count = int(counts.get(str(dpr_type), 0))
        if count > 0:
            passed_lines.append(
                f'\t{dpr_type} present ({count} file(s))'
            )
        else:
            failed_lines.append(
                f'\tNo {dpr_type} files found in {obs_dir}'
            )
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