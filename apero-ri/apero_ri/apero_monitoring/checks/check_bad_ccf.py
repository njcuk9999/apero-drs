#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reduced APERO check: outlier CCF files in science targets (BAD_CCF)."""

import math
from typing import List, Optional, Tuple

import numpy as np

import apero_ri.apero_monitoring.core.red_common as red_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'BAD_CCF'
CHECK_HUMAN_NAME = 'Outlier CCF Files'
CHECK_TYPE = 'red'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'MANUAL_START',
                      'APERO_START', 'APERO_END']

CHECK.description = """
Detects outlier CCF (Cross-Correlation Function) files in science targets.

For each science object observed in this obsdir, the check queries the APERO
FileIndex database for CCF_RV files, reads the RV_OBJ and CCFMFWHM header
values, and flags files that are more than a configurable number of sigma
away from the nightly median using a robust (MAD-based) distance metric.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with --test=BAD_CCF.

If still FALSE, inspect the flagged CCF files in the reduced directory and
compare the RV and FWHM against previous nights for the same target.

If the outlier is caused by bad weather or instrument issues please reject
the affected file and override the check.

Please contact <CONTACT:C1> if you are unsure how to proceed.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.NJC, starred=True)
clist1.add(contacts.EA)
clist1.add(contacts.LM)
CHECK.contact_list['C1'] = clist1

_DEFAULT_SCI_TYPES = ['OBJ_DARK', 'OBJ_FP', 'OBJ_SKY']
_DEFAULT_CCF_OUTPUT = 'CCF_RV'
_DEFAULT_SCI_FIBER = 'A'
_DEFAULT_BAD_NSIG = 10.0
_DEFAULT_RV_KEY = 'RV_OBJ'
_DEFAULT_FWHM_KEY = 'CCFMFWHM'


# =============================================================================
# Internal helpers
# =============================================================================
def _mad_sigma(values: np.ndarray) -> float:
    """Robust std estimate via Median Absolute Deviation."""
    finite = values[np.isfinite(values)]
    if len(finite) < 2:
        return np.nan
    med = float(np.median(finite))
    return float(np.median(np.abs(finite - med))) * 1.4826


def _query_science_objects(dbparams: dict,
                           findex: str,
                           obs_dir: str,
                           sci_types: List[str]) -> List[str]:
    """Return distinct science object names observed in ``obs_dir``."""
    from apero_ri.tasks import apero_async
    type_clauses = ' OR '.join(
        f"fdb.KW_DPRTYPE={repr(t)}" for t in sci_types
    )
    query = f"""
        SELECT DISTINCT fdb.KW_OBJNAME AS OBJ
        FROM {findex} AS fdb
        WHERE fdb.BLOCK_KIND='raw'
          AND fdb.OBS_DIR={repr(obs_dir)}
          AND ({type_clauses})
          AND fdb.KW_OBJNAME IS NOT NULL
          AND fdb.KW_OBJNAME != ''
    """
    try:
        rows = apero_async.database_query(dbparams, query)
        return [str(r.get('OBJ', '') or '').strip()
                for r in rows if r.get('OBJ')]
    except Exception:
        return []


def _query_ccf_files(dbparams: dict,
                     findex: str,
                     obj_name: str,
                     ccf_output: str,
                     sci_fiber: str) -> List[str]:
    """Return absolute paths of CCF_RV files for one science object."""
    from apero_ri.tasks import apero_async
    query = f"""
        SELECT fdb.ABSPATH AS PATH
        FROM {findex} AS fdb
        WHERE fdb.BLOCK_KIND='red'
          AND fdb.KW_OUTPUT={repr(ccf_output)}
          AND fdb.KW_OBJNAME={repr(obj_name)}
          AND fdb.KW_FIBER={repr(sci_fiber)}
    """
    try:
        rows = apero_async.database_query(dbparams, query)
        return [str(r.get('PATH', '') or '').strip()
                for r in rows if r.get('PATH')]
    except Exception:
        return []


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Flag science targets with outlier CCF radial velocities or FWHM."""
    _ = instrument
    if not red_common.is_check_enabled(aparams, 'bad_ccf', default=True):
        return True, 'Skipped bad_ccf: disabled.'
    if not dbparams:
        return True, 'No database parameters available; skipping bad_ccf.'
    # Resolve configuration.
    from apero_ri.application import profile_utils
    sci_types = red_common.get_check_value(
        aparams, 'bad_ccf', ['sci_dprtypes'], _DEFAULT_SCI_TYPES)
    if not isinstance(sci_types, list):
        sci_types = list(_DEFAULT_SCI_TYPES)
    ccf_output = str(red_common.get_check_value(
        aparams, 'bad_ccf', ['ccf_output'], _DEFAULT_CCF_OUTPUT))
    sci_fiber = str(red_common.get_check_value(
        aparams, 'bad_ccf', ['sci_fiber'], _DEFAULT_SCI_FIBER))
    bad_nsig = float(red_common.get_check_value(
        aparams, 'bad_ccf', ['bad_nsig'], _DEFAULT_BAD_NSIG))
    rv_key = str(red_common.get_check_value(
        aparams, 'bad_ccf', ['rv_key'], _DEFAULT_RV_KEY))
    fwhm_key = str(red_common.get_check_value(
        aparams, 'bad_ccf', ['fwhm_key'], _DEFAULT_FWHM_KEY))
    # Resolve the FileIndex table name.
    findex_name = str(profile_utils.profile_get_db(
        aparams, 'FINDEX_TABLENAME', ''))
    if not findex_name:
        return True, 'No FINDEX_TABLENAME configured; skipping bad_ccf.'
    findex = profile_utils.q_ident(findex_name)
    # Query science objects observed in this obsdir.
    obj_names = _query_science_objects(
        dbparams, findex, obs_dir, sci_types)
    if not obj_names:
        return True, f'No science objects found in FINDEX for obsdir {obs_dir}.'
    passed_lines = []
    failed_lines = []
    for obj_name in obj_names:
        ccf_paths = _query_ccf_files(
            dbparams, findex, obj_name, ccf_output, sci_fiber)
        if not ccf_paths:
            passed_lines.append(f'\t{obj_name}: no CCF files found; skipping.')
            continue
        # Read RV and FWHM from each CCF file.
        rvs: List[Optional[float]] = []
        fwhms: List[Optional[float]] = []
        for path in ccf_paths:
            try:
                from astropy.io import fits
                header = fits.getheader(path, ext=0)
                rv = float(header.get(rv_key, np.nan))
                fw = float(header.get(fwhm_key, np.nan))
            except Exception:
                rv = np.nan
                fw = np.nan
            rvs.append(rv)
            fwhms.append(fw)
        rv_arr = np.array(rvs, dtype=float)
        fw_arr = np.array(fwhms, dtype=float)
        if np.sum(np.isfinite(rv_arr)) < 2:
            passed_lines.append(
                f'\t{obj_name}: fewer than 2 valid CCF files; skip outlier test.'
            )
            continue
        # Compute median + robust sigma for each metric.
        med_rv = float(np.nanmedian(rv_arr))
        sig_rv = _mad_sigma(rv_arr)
        med_fw = float(np.nanmedian(fw_arr))
        sig_fw = _mad_sigma(fw_arr)
        # Flag files whose distance in sigma-space exceeds the threshold.
        obj_failed = False
        for i, path in enumerate(ccf_paths):
            d_rv = (abs(rvs[i] - med_rv) / sig_rv
                    if sig_rv and math.isfinite(sig_rv) and sig_rv > 0
                    else 0.0)
            d_fw = (abs(fwhms[i] - med_fw) / sig_fw
                    if sig_fw and math.isfinite(sig_fw) and sig_fw > 0
                    else 0.0)
            nsig = math.sqrt(d_rv ** 2 + d_fw ** 2)
            if nsig > bad_nsig:
                from pathlib import Path
                fname = Path(path).name
                failed_lines.append(
                    f'\t{obj_name}: {fname} '
                    f'outlier nsig={nsig:.1f} '
                    f'(rv={rvs[i]:.3f} fwhm={fwhms[i]:.3f})'
                )
                obj_failed = True
        if not obj_failed:
            passed_lines.append(
                f'\t{obj_name}: {len(ccf_paths)} CCF file(s) ok'
            )
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
