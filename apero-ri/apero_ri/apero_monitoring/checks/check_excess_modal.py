#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reduced APERO check: excess modal noise in telluric stars (EXCESS_MODAL)."""

from typing import Tuple

import numpy as np

import apero_ri.apero_monitoring.core.red_common as red_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links

# Optional scipy import for the spline low-pass filter.
try:
    from scipy.interpolate import InterpolatedUnivariateSpline as _IUS
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'EXCESS_MODAL'
CHECK_HUMAN_NAME = 'Excess Modal Noise'
CHECK_TYPE = 'red'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'MANUAL_START',
                      'APERO_START', 'APERO_END']

CHECK.description = """
Tests for excess modal noise in telluric-standard stars.

For each tcorr file belonging to a vetted telluric star, it computes the
pixel-to-pixel RMS (photon noise proxy) and the RMS with a 20-pixel stride
(photon + modal noise proxy) on a sample H-band order.  The test passes when
the modal component (quadratic subtraction of the two) does not exceed a
mode-specific threshold.

This test is True by default when no vetted telluric stars were observed.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=EXCESS_MODAL.

If still FALSE please email <CONTACT:C1>.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.EA, starred=True)
clist1.add(contacts.NJC)
clist1.add(contacts.LM)
CHECK.contact_list['C1'] = clist1

# Hard-coded vetted hot stars (same list as in the original excess_modal.py).
_VETTED_STARS = frozenset([
    'HR8709', 'HR3117', 'HR3131', 'HR5107', 'HR4467', 'HR7590', 'HR5671',
    'HR6743', 'HR875', 'HR806', 'HR9098', 'HR1903', 'HR3314', 'HR4023',
    'HR7830',
])

_SAMPLE_ORDER = 58      # middle H-band order (1-indexed FITS row)
_THRESHOLD_HA = 0.015
_THRESHOLD_HE = 0.010
_DEFAULT_PATTERN = '*e2ds*tcorr_A.fits'


# =============================================================================
# Internal helpers
# =============================================================================
def _estimate_sigma(spectrum: np.ndarray) -> float:
    """Robust std via 16th/84th percentile, ignoring NaNs."""
    finite = spectrum[np.isfinite(spectrum)]
    if len(finite) < 3:
        return np.nan
    p16 = float(np.nanpercentile(finite, 16))
    p84 = float(np.nanpercentile(finite, 84))
    return (p84 - p16) / 2.0


def _lowpass_filter(vector: np.ndarray, width: int = 101) -> np.ndarray:
    """NaN-aware spline low-pass filter (matches original excess_modal.py)."""
    if not _HAS_SCIPY:
        # Fallback: uniform box convolution.
        from numpy.lib.stride_tricks import sliding_window_view
        out = np.full_like(vector, np.nan)
        half = width // 2
        for i in range(len(vector)):
            lo = max(0, i - half)
            hi = min(len(vector), i + half + 1)
            chunk = vector[lo:hi]
            finite = chunk[np.isfinite(chunk)]
            if len(finite):
                out[i] = np.mean(finite)
        return out
    valid = np.isfinite(vector)
    if valid.sum() < width:
        return np.full_like(vector, np.nanmedian(vector))
    x = np.arange(len(vector))
    spl = _IUS(x[valid], vector[valid], k=1, ext=3)
    return spl(x)


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Flag vetted telluric stars with excess modal noise."""
    _ = dbparams
    if not red_common.is_check_enabled(aparams, 'excess_modal', default=True):
        return True, 'Skipped excess_modal: disabled.'
    # Resolve config.
    obj_key = str(red_common.get_check_value(
        aparams, 'excess_modal', ['obj_key'], 'DRSOBJN'))
    mode_key = str(red_common.get_check_value(
        aparams, 'excess_modal', ['mode_key'], 'DRSMODE'))
    sample_order = int(red_common.get_check_value(
        aparams, 'excess_modal', ['sample_order'], _SAMPLE_ORDER))
    thresh_ha = float(red_common.get_check_value(
        aparams, 'excess_modal', ['threshold_ha'], _THRESHOLD_HA))
    thresh_he = float(red_common.get_check_value(
        aparams, 'excess_modal', ['threshold_he'], _THRESHOLD_HE))
    pattern = str(red_common.get_check_value(
        aparams, 'excess_modal', ['file_pattern'], _DEFAULT_PATTERN))
    vetted = red_common.get_check_value(
        aparams, 'excess_modal', ['vetted_stars'], None)
    vetted_set = frozenset(vetted) if isinstance(vetted, list) else _VETTED_STARS
    # Pick per-mode threshold from instrument name.
    inst_upper = str(instrument or '').upper()
    if 'HE' in inst_upper:
        default_threshold = thresh_he
    else:
        default_threshold = thresh_ha
    obs_path, files = red_common.list_red_files(aparams, obs_dir, pattern)
    if not obs_path.exists():
        return False, (f'Reduced directory for {obs_dir} does not exist '
                       f'({obs_path}).')
    if not files:
        return True, (f'No tcorr files ({pattern}) found in {obs_path}; '
                      'nothing to check.')
    passed_lines = []
    failed_lines = []
    checked = 0
    for filename in files:
        try:
            from astropy.io import fits
            header = fits.getheader(str(filename), ext=0)
            obj_name = str(header.get(obj_key, '') or '').strip().upper()
            if obj_name not in vetted_set:
                continue
            mode = str(header.get(mode_key, '') or '').upper()
            if 'HE' in mode:
                threshold = thresh_he
            elif 'HA' in mode:
                threshold = thresh_ha
            else:
                threshold = default_threshold
            data = fits.getdata(str(filename), ext=1)
            if data is None:
                continue
            arr = np.asarray(data)
            # Select the sample order row (FITS rows are 1-indexed).
            row_idx = sample_order - 1
            if row_idx < 0 or row_idx >= arr.shape[0]:
                continue
            sp = arr[row_idx].astype(float)
            # Use central 2048 pixels to avoid edge artefacts.
            centre = len(sp) // 2
            half = 1024
            lo, hi = max(0, centre - half), min(len(sp), centre + half)
            sp = sp[lo:hi]
            # Normalise by low-pass trend.
            trend = _lowpass_filter(sp)
            with np.errstate(divide='ignore', invalid='ignore'):
                sp_norm = np.where(trend != 0, sp / trend, np.nan)
            # Pixel-to-pixel RMS.
            diff1 = sp_norm[1:] - sp_norm[:-1]
            rms1 = float(np.nanstd(diff1)) / np.sqrt(2)
            # 20-pixel stride RMS.
            stride = 20
            diff20 = sp_norm[stride:] - sp_norm[:-stride]
            rms20 = float(np.nanstd(diff20)) / np.sqrt(2)
            # Excess modal noise (quadratic subtraction).
            sq_diff = rms20 ** 2 - rms1 ** 2
            rms_lf = float(np.sqrt(max(sq_diff, 0.0)))
            checked += 1
            if rms_lf > threshold:
                failed_lines.append(
                    f'\t{filename.name} [{obj_name}]: '
                    f'excess_modal={rms_lf:.5f} > {threshold:.5f}'
                )
            else:
                passed_lines.append(
                    f'\t{filename.name} [{obj_name}]: '
                    f'excess_modal={rms_lf:.5f} ok'
                )
        except Exception as exc:
            failed_lines.append(
                f'\t{filename.name}: could not compute modal noise ({exc})'
            )
    if checked == 0 and not failed_lines:
        return True, 'No vetted telluric stars observed in this obsdir.'
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
