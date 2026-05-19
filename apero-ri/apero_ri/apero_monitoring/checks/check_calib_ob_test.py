#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO check for required calibration OB names."""

from typing import Tuple

import numpy as np

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'COB_TEST'
CHECK_HUMAN_NAME = 'Calibration OB Name Check'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR']

CHECK.description = """
This check verifies that required calibration OB names appear in the
configured MJD spans. It scans all raw-file headers, enables each rule
only inside its configured MJD range, and then checks that matching OB
names occur at least once while the rule is active.
"""

# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Check that required calibration OB names appear in configured MJD spans.

    The function checks all raw-file headers, enables each rule only inside its
    configured MJD range, and then verifies that matching OB names occur at
    least once while the rule is active.

    :param instrument: APERO instrument name (unused by this check body).
    :param obs_dir: Obsdir identifier currently being validated.
    :param aparams: Hydrated APERO profile parameters.
    :param dbparams: Database parameters (unused by this check body).
    :return: Tuple of pass flag and formatted report text.
    """
    # Keep signature compatibility with the generic check interface.
    _ = instrument, dbparams
    # Allow global enable or disable of this check from profile config.
    if not raw_common.is_check_enabled(aparams,
                                       'calib_ob_test',
                                       default=True):
        return True, 'Skipped calib_ob_test: disabled.'
    # Resolve all FITS files for the requested obsdir.
    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    # Fail immediately when the obsdir path is missing.
    if not obs_path.exists():
        return False, f'Observation directory {obs_dir} does not exist.'
    # Fail immediately when no FITS files are available for inspection.
    if len(files) == 0:
        return False, f'No FITS files found in {obs_path}'

    # Load required header keys and configured calibration OB-name rules.
    obs_name_key = raw_common.get_header_key(aparams, 'obs_name')
    mjd_key = raw_common.get_header_key(aparams, 'mjd_obs')
    required = raw_common.get_check_value(aparams,
                                          'calib_ob_test',
                                          ['required_obnames'],
                                          dict())
    # Skip the check when OB-name rules are not configured.
    if obs_name_key == '' or mjd_key == '' or not isinstance(required, dict):
        return True, 'No calibration OB-name rules configured.'

    # Initialise per-rule counters and in-range activation flags.
    counts = dict()
    in_range = dict()
    for name in required:
        counts[str(name)] = 0
        in_range[str(name)] = False

    # Scan file headers and update active-rule counters.
    for filename in files:
        header = raw_common.read_primary_header(filename)
        obs_name = str(header.get(obs_name_key, '') or '')
        try:
            mjd_obs = float(header.get(mjd_key))
        except Exception:
            mjd_obs = np.nan
        if np.isnan(mjd_obs):
            continue

        # Evaluate each rule against this file's MJD and OB name.
        for name, rule in required.items():
            low = float(rule.get('mjd_start', -np.inf))
            high = float(rule.get('mjd_end', np.inf))
            if mjd_obs < low or mjd_obs > high:
                continue
            in_range[str(name)] = True
            if str(name) in obs_name:
                counts[str(name)] += 1

    # Build pass and fail messages for each configured rule.
    passed_lines = []
    failed_lines = []
    for name in required:
        if not in_range[str(name)]:
            passed_lines.append(
                f'\t{name} skipped '
                '(obsdir outside configured MJD range)'
            )
        elif counts[str(name)] > 0:
            passed_lines.append(
                f'\t{name} found ({counts[str(name)]} file(s))'
            )
        else:
            failed_lines.append(f'\t{name} not found in {obs_dir}')
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