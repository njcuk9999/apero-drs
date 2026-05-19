#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO quality check for configured DPR groups."""

from typing import Tuple

import numpy as np
from astropy.io import fits

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'QUAL_TEST'
CHECK_HUMAN_NAME = 'Raw Quality Check'
CHECK_TYPE = 'raw'
# INSTRUMENTS = ['SPIROU', 'NIRPS_HE', 'NIRPS_HA']
INSTRUMENTS = []

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR']


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Run quality constraints on raw files belonging to configured DPR types.

    The function scans all FITS files in one obsdir, keeps only files whose
    DPR type appears in configured groups, and validates percentile and
    saturation metrics against per-type limits.

    :param instrument: APERO instrument name (unused by this check body).
    :param obs_dir: Obsdir identifier currently being validated.
    :param aparams: Hydrated APERO profile parameters.
    :param dbparams: Database parameters (unused by this check body).
    :return: Tuple of pass flag and formatted report text.
    """
    # Keep signature compatibility with the generic check interface.
    _ = instrument, dbparams
    # Allow global enable or disable of this check from profile config.
    if not raw_common.is_check_enabled(aparams, 'qual_test', default=True):
        return True, 'Skipped qual_test: disabled.'
    # Resolve all FITS files for the requested obsdir.
    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    # Fail immediately when the obsdir path is missing.
    if not obs_path.exists():
        return False, f'Observation directory {obs_dir} does not exist.'
    # Fail immediately when no FITS files are available for inspection.
    if len(files) == 0:
        return False, f'No FITS files found in {obs_path}'

    # Load header-key and quality-rule configuration blocks.
    dpr_key = raw_common.get_header_key(aparams, 'dpr_type')
    groups = raw_common.get_check_value(aparams,
                                        'qual_test',
                                        ['dpr_groups'],
                                        dict())
    constraints = raw_common.get_check_value(aparams,
                                             'qual_test',
                                             ['constraints'],
                                             dict())
    # Skip the check when quality configuration is not available.
    if dpr_key == '' or not isinstance(groups, dict):
        return True, 'No raw quality configuration is defined.'

    # Build the list of DPR types that should be quality controlled.
    valid_types = set()
    for values in groups.values():
        if isinstance(values, list):
            valid_types |= set(values)

    # Collect pass or fail messages at the file level.
    passed_lines = []
    failed_lines = []
    checked = 0
    # Process each FITS file and evaluate configured quality limits.
    for filename in files:
        # Read the primary header through the shared cache-aware helper.
        header = raw_common.read_primary_header(filename)
        # Skip files that do not belong to monitored DPR groups.
        dpr_type = str(header.get(dpr_key, '') or '').strip()
        if dpr_type not in valid_types:
            continue
        checked += 1
        # Load constraint values for this DPR type.
        rule = constraints.get(dpr_type, {})
        if not isinstance(rule, dict):
            failed_lines.append(
                f'\t{filename.name}: no quality rule for {dpr_type}'
            )
            continue

        # Open extension data arrays used by the quality metrics.
        try:
            image = fits.getdata(filename, ext=1)
            nread = fits.getdata(filename, ext=3)
        except Exception:
            failed_lines.append(
                f'\t{filename.name}: file has fewer than 4 HDUs'
            )
            continue
        if image is None or nread is None:
            failed_lines.append(
                f'\t{filename.name}: missing image or nread data'
            )
            continue
        image_arr = np.asarray(image)
        nread_arr = np.asarray(nread)
        # Compute summary metrics used by the quality rules.
        p99 = float(np.nanpercentile(image_arr, 99))
        fsat = float(np.mean(nread_arr != np.nanmax(nread_arr)))
        p99_min = float(rule.get('p99_min', -np.inf))
        p99_max = float(rule.get('p99_max', np.inf))
        fsat_max = float(rule.get('sat_frac_max', np.inf))

        # Collect all constraint violations for this file.
        file_failures = []
        if p99 < p99_min:
            file_failures.append(
                f'p99 too low ({p99:.4f} < {p99_min:.4f})'
            )
        if p99 > p99_max:
            file_failures.append(
                f'p99 too high ({p99:.4f} > {p99_max:.4f})'
            )
        if fsat > fsat_max:
            file_failures.append(
                f'saturation too high ({fsat:.5f} > {fsat_max:.5f})'
            )

        # Record either the failure list or a pass message for this file.
        if file_failures:
            message = '; '.join(file_failures)
            failed_lines.append(
                f'\t{filename.name} [{dpr_type}]: {message}'
            )
        else:
            passed_lines.append(f'\t{filename.name} [{dpr_type}] passed')

    # Report when no file matched configured DPR groups.
    if checked == 0:
        passed_lines.append('\tNo configured quality-controlled files found')
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