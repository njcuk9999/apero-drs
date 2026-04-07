#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Bokeh plot payloads for the data portal object page.

Provides two time-series plots:

- **SNR vs time**: EXT_H (orange circles) and EXT_Y (purple circles);
  QC failures (EXT_QCC_ALL != 1) rendered as X markers.
- **BERV coverage**: Vtot = Vsys − BERV [km/s] vs time, with:
    * green circles     = passed all QC (EXT + TCORR)
    * blue X markers    = failed QC at EXT stage
    * red X markers     = failed QC at TCORR stage
    * gray dotted line  = theoretical annual BERV curve (barycorrpy)
    * horizontal dashed = Vsys [km/s] when available

Also provides spectrum, CCF, and LBL plot builders.  Each plot family
can be exported as either a ``json_item`` dict (for dynamic AJAX-loaded
pages) or as ``(script, div)`` HTML strings (for server-rendered
standalone maximize pages).

Created on 2024-01-01

@author: cook
"""
from __future__ import annotations

import re
import threading
import time
import warnings
from collections import OrderedDict
from datetime import datetime, timezone
from os import path as op
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from astropy.time import Time
from bokeh.models import (ColumnDataSource, CrosshairTool, HoverTool,
                          Range1d, Span)

from apero_ri.base import base
from apero_ri.plots.plot_general import make_time_figure
from apero_ri.plots.plot_general import mjd_to_datetime
from apero_ri.plots.plot_general import plot_to_components
from apero_ri.plots.plot_general import sci_header_label

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.plots.plot_objects'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# BLOCK_KIND → PATH_KEY mapping (mirrors apero_ri.base.base)
_BLOCK_KIND_TO_PATH: Dict[str, str] = {
    'raw':   'PATH_RAW',
    'tmp':   'PATH_PP',
    'calib': 'PATH_CALIB',
    'red':   'PATH_RED',
    'tellu': 'PATH_TELLU',
    'out':   'PATH_OUT',
    'lbl':   'PATH_LBL',
}

# CCF performance knobs (kept conservative for UI responsiveness)
_CCF_CACHE_MAX_ENTRIES = 512
_CCF_RV_MAX_POINTS = 2500
_CCF_FILE_CACHE: OrderedDict[str, Tuple[float, np.ndarray, np.ndarray]] = OrderedDict()
_CCF_FILE_CACHE_LOCK = threading.Lock()


def _decimate_ccf_grid(
    rv_vec: np.ndarray,
    all_ccf: np.ndarray,
    max_points: int = _CCF_RV_MAX_POINTS,
) -> Tuple[np.ndarray, np.ndarray, int, int]:
    """
    Downsample the CCF RV grid when it is very dense to reduce percentile,
    JSON serialization, and browser rendering costs.

    :param rv_vec: RV axis array [km/s]
    :param all_ccf: 2D CCF stack [n_obs, n_rv]
    :param max_points: maximum RV samples to keep

    :return: tuple (rv_used, ccf_used, original_points, used_points)
    :rtype: tuple
    """
    try:
        npts = int(len(rv_vec))
    except Exception:
        return rv_vec, all_ccf, 0, 0
    if npts <= 0 or npts <= int(max_points):
        return rv_vec, all_ccf, npts, npts
    idx = np.linspace(0, npts - 1, int(max_points), dtype=int)
    return rv_vec[idx], all_ccf[:, idx], npts, int(len(idx))


def _read_ccf_row_cached(path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Read RV/CCF arrays from a CCF FITS file with a small in-process LRU cache.
    Cache entries are invalidated automatically when file mtime changes.

    :param path: absolute file path to CCF FITS file

    :return: tuple (rv_vec, ccf_row) or None on any read error
    :rtype: tuple | None
    """
    from astropy.io import fits as _fits

    try:
        mtime = float(op.getmtime(path))
    except Exception:
        return None

    with _CCF_FILE_CACHE_LOCK:
        cached = _CCF_FILE_CACHE.get(path)
        if cached is not None and float(cached[0]) == mtime:
            _CCF_FILE_CACHE.move_to_end(path)
            return cached[1], cached[2]

    try:
        with _fits.open(str(path), memmap=False) as hdul:
            t = hdul['RV_TABLE']
            rv_vec = np.array(t.data['RV'], dtype=float)
            ccf_row = np.array(t.data['CCF_STACK'], dtype=float)
    except Exception:
        return None

    with _CCF_FILE_CACHE_LOCK:
        _CCF_FILE_CACHE[path] = (mtime, rv_vec, ccf_row)
        _CCF_FILE_CACHE.move_to_end(path)
        while len(_CCF_FILE_CACHE) > _CCF_CACHE_MAX_ENTRIES:
            _CCF_FILE_CACHE.popitem(last=False)
    return rv_vec, ccf_row


# =============================================================================
# Define private SNR / BERV series extractors
# =============================================================================
def _extract_snr_points(
    htable_rows: List[Dict[str, Any]],
) -> Tuple[list, list]:
    """
    Extract (dt, snr, qc_ok) tuples for H-band and Y-band, sorted by
    time.

    :param htable_rows: list of htable row dicts

    :return: tuple of two lists: (h_pts, y_pts)
    :rtype: tuple[list, list]
    """
    h_pts: list = []
    y_pts: list = []
    for row in htable_rows:
        if not isinstance(row, dict):
            continue
        dt = mjd_to_datetime(row.get('EXT_MJDMID'))
        if dt is None:
            continue
        qc_ok = int(row.get('EXT_QCC_ALL') or 1) == 1
        # ---------------------------------------------------------------------
        raw_h = row.get('EXT_H')
        if raw_h is not None:
            try:
                h_pts.append((dt, float(raw_h), qc_ok))
            except (TypeError, ValueError):
                pass
        raw_y = row.get('EXT_Y')
        if raw_y is not None:
            try:
                y_pts.append((dt, float(raw_y), qc_ok))
            except (TypeError, ValueError):
                pass
    # -------------------------------------------------------------------------
    h_pts.sort(key=lambda p: p[0])
    y_pts.sort(key=lambda p: p[0])
    return h_pts, y_pts


def _extract_berv_points(
    htable_rows: List[Dict[str, Any]],
    vsys_ms: Optional[float],
) -> Tuple[list, list, list]:
    """
    Extract BERV observation points, split by QC category.

    Returns three lists of (dt, vtot_km/s) tuples:

    - *passed*     – passed EXT *and* TCORR QC (green circles)
    - *ext_fail*   – failed EXT QC (blue X)
    - *tcorr_fail* – passed EXT, failed TCORR (red X)

    :param htable_rows: list of htable row dicts
    :param vsys_ms: float or None, systemic velocity in m/s

    :return: tuple (passed, ext_fail, tcorr_fail)
    :rtype: tuple[list, list, list]
    """
    vsys_kms = (vsys_ms / 1000.0) if vsys_ms is not None else None

    passed: list = []
    ext_fail: list = []
    tcorr_fail: list = []

    for row in htable_rows:
        if not isinstance(row, dict):
            continue
        dt = mjd_to_datetime(row.get('EXT_MJDMID'))
        if dt is None:
            continue
        raw_berv = row.get('EXT_BERV')
        if raw_berv is None:
            continue
        try:
            berv_kms = float(raw_berv)
        except (TypeError, ValueError):
            continue
        # ---------------------------------------------------------------------
        vtot = (
            (vsys_kms - berv_kms) if vsys_kms is not None
            else -berv_kms
        )
        ext_qc_ok = int(row.get('EXT_QCC_ALL') or 1) == 1
        tcorr_qc_raw = row.get('TCORR_QCC_ALL')
        tcorr_qc_ok = (
            bool(int(tcorr_qc_raw) == 1)
            if tcorr_qc_raw is not None
            else ext_qc_ok
        )
        if not ext_qc_ok:
            ext_fail.append((dt, vtot))
        elif not tcorr_qc_ok:
            tcorr_fail.append((dt, vtot))
        else:
            passed.append((dt, vtot))
    # -------------------------------------------------------------------------
    for lst in (passed, ext_fail, tcorr_fail):
        lst.sort(key=lambda p: p[0])
    return passed, ext_fail, tcorr_fail


# =============================================================================
# Define private BERV annual curve computation
# =============================================================================
def _compute_berv_curve(
    htable_rows: List[Dict[str, Any]],
    obj_props: Dict[str, Any],
    obs_props: Dict[str, Any],
    vsys_ms: Optional[float],
) -> Tuple[list, list]:
    """
    Compute the theoretical annual BERV curve using barycorrpy.

    Returns ``(x_datetimes, y_vtot_kms)`` or empty lists on any error.

    *obj_props* keys (from object_table.json row):
        ``RA [Deg]``, ``Dec [Deg]``, ``PMRA [mas/yr]``,
        ``PMDE [mas/yr]``, ``Plx [mas]``, ``RV [km/s]``
        (all optional; default to 0).

    *obs_props* keys (from instrument YAML ``observatory`` section):
        ``lat``, ``lon``, ``alt``.

    :param htable_rows: list of htable row dicts
    :param obj_props: dict, object properties from object_table.json
    :param obs_props: dict, observatory lat/lon/alt
    :param vsys_ms: float or None, systemic velocity in m/s

    :return: tuple (x_dates, y_vtot_kms)
    :rtype: tuple[list, list]
    """
    try:
        import barycorrpy
    except ImportError:
        return [], []

    try:
        # gather MJD min/max from htable rows
        mjd_vals = []
        for row in htable_rows:
            if not isinstance(row, dict):
                continue
            v = row.get('EXT_MJDMID')
            if v is not None:
                try:
                    mjd_vals.append(float(v))
                except (TypeError, ValueError):
                    pass
        if not mjd_vals:
            return [], []
        # ---------------------------------------------------------------------
        # daily JD times, 14 days before first obs and 60 days after last
        mjd_min = min(mjd_vals)
        mjd_max = max(mjd_vals)
        jd_start = Time(mjd_min, format='mjd').jd - 14
        jd_end = Time(mjd_max, format='mjd').jd + 60
        times_jd = np.arange(jd_start, jd_end, 1.0)
        # ---------------------------------------------------------------------
        # object parameters
        ra = float(obj_props.get('RA [Deg]') or 0.0)
        dec = float(obj_props.get('Dec [Deg]') or 0.0)
        pmra = float(obj_props.get('PMRA [mas/yr]') or 0.0)
        pmdec = float(obj_props.get('PMDE [mas/yr]') or 0.0)
        px = float(obj_props.get('Plx [mas]') or 0.0)
        rv = float(obj_props.get('RV [km/s]') or 0.0)
        # ---------------------------------------------------------------------
        # observatory parameters
        lat = float(obs_props.get('lat', 0.0))
        lon = float(obs_props.get('lon', 0.0))
        alt = float(obs_props.get('alt', 0.0))

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = barycorrpy.get_BC_vel(
                JDUTC=times_jd,
                ra=ra, dec=dec,
                epoch=2451545.0,   # J2000.0 in JD
                pmra=pmra, pmdec=pmdec,
                px=px, rv=rv,
                lat=lat, longi=lon, alt=alt,
                leap_update=False,
            )
        bervs_kms = result[0] / 1000.0   # convert m/s → km/s
        vsys_kms = (vsys_ms / 1000.0) if vsys_ms is not None else 0.0
        vtot_kms = vsys_kms - bervs_kms
        # ---------------------------------------------------------------------
        # convert JD times to UTC datetimes for Bokeh
        x_dates = []
        for jd in times_jd:
            try:
                dt = Time(jd, format='jd').to_datetime(
                    timezone=timezone.utc
                )
                x_dates.append(dt)
            except Exception:
                pass
        return x_dates, list(vtot_kms)

    except Exception:
        return [], []


# =============================================================================
# Define private SNR / BERV figure builders
# =============================================================================
def _make_snr_figure(h_pts: list, y_pts: list,
                     label_h: str, label_y: str) -> Any:
    """
    Build a Bokeh figure for the SNR vs time plot.

    :param h_pts: list of (dt, snr, qc_ok) tuples for H-band
    :param y_pts: list of (dt, snr, qc_ok) tuples for Y-band
    :param label_h: str, legend label for H-band
    :param label_y: str, legend label for Y-band

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    fig = make_time_figure(
        title='Signal to Noise Ratio vs Time', height=400
    )
    hover = HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('SNR',        '@y{0.00}'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    )
    fig.add_tools(hover)
    # -------------------------------------------------------------------------
    def _add_series(pts: list, color: str,
                    legend_label: str) -> None:
        pass_x = [p[0] for p in pts if p[2]]
        pass_y = [p[1] for p in pts if p[2]]
        fail_x = [p[0] for p in pts if not p[2]]
        fail_y = [p[1] for p in pts if not p[2]]
        if pass_x:
            src = ColumnDataSource({'x': pass_x, 'y': pass_y})
            fig.scatter('x', 'y', source=src, color=color, size=6,
                        alpha=0.78, marker='circle',
                        legend_label=legend_label)
        if fail_x:
            src = ColumnDataSource({'x': fail_x, 'y': fail_y})
            fig.scatter('x', 'y', source=src, color=color, size=9,
                        alpha=0.9, line_width=2, marker='cross',
                        legend_label=f'{legend_label} (QC fail)')
    # -------------------------------------------------------------------------
    _add_series(h_pts, '#e6820a', label_h)   # orange for H-band
    _add_series(y_pts, '#7e22ce', label_y)   # purple for Y-band

    fig.xaxis.axis_label = 'Date (UTC)'
    fig.yaxis.axis_label = 'SNR'
    if fig.legend:
        fig.legend.location = 'top_left'
        fig.legend.click_policy = 'hide'
    return fig


def _make_berv_figure(
    passed: list,
    ext_fail: list,
    tcorr_fail: list,
    curve_x: list,
    curve_y: list,
    vsys_ms: Optional[float],
    y_label: str,
) -> Any:
    """
    Build a Bokeh figure for the BERV coverage plot.

    :param passed: list of (dt, vtot) tuples that passed all QC
    :param ext_fail: list of (dt, vtot) tuples that failed EXT QC
    :param tcorr_fail: list of (dt, vtot) tuples that failed TCORR QC
    :param curve_x: list of datetimes for the BERV curve
    :param curve_y: list of vtot values [km/s] for the BERV curve
    :param vsys_ms: float or None, systemic velocity in m/s
    :param y_label: str, y-axis label

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    fig = make_time_figure(title='BERV Coverage', height=400)
    hover_pts = HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('Vtot',       '@y{0.000} km/s'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    )
    fig.add_tools(hover_pts)
    # -------------------------------------------------------------------------
    # BERV curve (background line)
    if curve_x and curve_y:
        src_curve = ColumnDataSource({'x': curve_x, 'y': curve_y})
        fig.line('x', 'y', source=src_curve, line_color='gray',
                 line_dash='dotted', line_width=2, alpha=0.7,
                 legend_label='BERV curve')
    # -------------------------------------------------------------------------
    # Vsys horizontal line  — solid blue
    if vsys_ms is not None:
        vsys_kms = vsys_ms / 1000.0
        vsys_span = Span(
            location=vsys_kms, dimension='width',
            line_color='blue', line_dash='solid',
            line_width=1.5, level='overlay',
        )
        fig.add_layout(vsys_span)
        src_dummy = ColumnDataSource({'x': [], 'y': []})
        fig.line('x', 'y', source=src_dummy, line_color='blue',
                 line_width=1.5,
                 legend_label=f'v_sys = {vsys_kms:.3f} km/s')
    # -------------------------------------------------------------------------
    # observation points (rendered on top)
    if passed:
        src = ColumnDataSource({
            'x': [p[0] for p in passed],
            'y': [p[1] for p in passed],
        })
        fig.scatter('x', 'y', source=src, name='berv_pts',
                    color='green', size=6, alpha=0.6,
                    marker='circle', legend_label='Passed all QC')
    if ext_fail:
        src = ColumnDataSource({
            'x': [p[0] for p in ext_fail],
            'y': [p[1] for p in ext_fail],
        })
        fig.scatter('x', 'y', source=src, name='berv_pts',
                    color='blue', size=9, alpha=0.9, line_width=2,
                    marker='cross', legend_label='Failed QC (EXT)')
    if tcorr_fail:
        src = ColumnDataSource({
            'x': [p[0] for p in tcorr_fail],
            'y': [p[1] for p in tcorr_fail],
        })
        fig.scatter('x', 'y', source=src, name='berv_pts',
                    color='red', size=9, alpha=0.9, line_width=2,
                    marker='cross', legend_label='Failed QC (TCORR)')
    # -------------------------------------------------------------------------
    fig.xaxis.axis_label = 'Date (UTC)'
    fig.yaxis.axis_label = y_label
    if fig.legend:
        fig.legend.location = 'top_left'
        fig.legend.click_policy = 'hide'
    return fig


# =============================================================================
# Define public SNR / BERV builders
# =============================================================================
def build_snr_plot_json(
    htable_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
    target_id: str = 'op-snr-plot-div',
) -> Dict[str, Any]:
    """
    Build SNR plot payload as a ``json_item`` dict for client-side
    embedding.

    :param htable_rows: list of htable row dicts
    :param preset: dict, instrument profile preset
    :param target_id: str, DOM element ID for Bokeh embedding

    :return: dict with has_plot, item/message
    :rtype: dict
    """
    label_h = sci_header_label(preset, 'ext', 'EXT_H', 'H-band SNR')
    label_y = sci_header_label(preset, 'ext', 'EXT_Y', 'Y-band SNR')
    h_pts, y_pts = _extract_snr_points(htable_rows)
    if not h_pts and not y_pts:
        return {
            'has_plot': False,
            'message': 'No SNR data found in htable.',
        }
    fig = _make_snr_figure(h_pts, y_pts, label_h, label_y)
    script, div = plot_to_components(fig)
    return {
        'has_plot': True,
        'script': script,
        'div': div,
        'message': '',
    }


def build_berv_plot_json(
    htable_rows: List[Dict[str, Any]],
    vsys_ms: Optional[float],
    preset: Dict[str, Any],
    obj_props: Optional[Dict[str, Any]] = None,
    target_id: str = 'op-berv-plot-div',
) -> Dict[str, Any]:
    """
    Build BERV coverage plot payload as a ``json_item`` dict for
    client-side embedding.

    :param htable_rows: list of htable row dicts
    :param vsys_ms: float or None, systemic velocity in m/s
    :param preset: dict, instrument profile preset
    :param obj_props: dict or None, object properties from object table
    :param target_id: str, DOM element ID for Bokeh embedding

    :return: dict with has_plot, item/message
    :rtype: dict
    """
    passed, ext_fail, tcorr_fail = _extract_berv_points(
        htable_rows, vsys_ms
    )
    if not passed and not ext_fail and not tcorr_fail:
        return {
            'has_plot': False,
            'message': 'No BERV data found in htable.',
        }
    obs_props = (preset or {}).get('observatory', {})
    curve_x, curve_y = _compute_berv_curve(
        htable_rows, obj_props or {}, obs_props, vsys_ms
    )
    y_label = (
        'Vtot = Vsys \u2212 BERV [km/s]'
        if vsys_ms is not None
        else '\u2212BERV [km/s]'
    )
    fig = _make_berv_figure(
        passed, ext_fail, tcorr_fail,
        curve_x, curve_y, vsys_ms, y_label,
    )
    script, div = plot_to_components(fig)
    return {
        'has_plot': True,
        'script': script,
        'div': div,
        'message': '',
    }


def build_snr_plot_components(
    htable_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build SNR plot payload as ``(script, div)`` for server-side
    embedding.

    :param htable_rows: list of htable row dicts
    :param preset: dict, instrument profile preset

    :return: dict with has_plot, script, div, message
    :rtype: dict
    """
    label_h = sci_header_label(preset, 'ext', 'EXT_H', 'H-band SNR')
    label_y = sci_header_label(preset, 'ext', 'EXT_Y', 'Y-band SNR')
    h_pts, y_pts = _extract_snr_points(htable_rows)
    if not h_pts and not y_pts:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': 'No SNR data found in htable.',
        }
    fig = _make_snr_figure(h_pts, y_pts, label_h, label_y)
    script, div = plot_to_components(fig)
    return {
        'has_plot': True, 'script': script, 'div': div, 'message': ''
    }


def build_berv_plot_components(
    htable_rows: List[Dict[str, Any]],
    vsys_ms: Optional[float],
    preset: Dict[str, Any],
    obj_props: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build BERV coverage plot payload as ``(script, div)`` for
    server-side embedding.

    :param htable_rows: list of htable row dicts
    :param vsys_ms: float or None, systemic velocity in m/s
    :param preset: dict, instrument profile preset
    :param obj_props: dict or None, object properties from object table

    :return: dict with has_plot, script, div, message
    :rtype: dict
    """
    passed, ext_fail, tcorr_fail = _extract_berv_points(
        htable_rows, vsys_ms
    )
    if not passed and not ext_fail and not tcorr_fail:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': 'No BERV data found in htable.',
        }
    obs_props = (preset or {}).get('observatory', {})
    curve_x, curve_y = _compute_berv_curve(
        htable_rows, obj_props or {}, obs_props, vsys_ms
    )
    y_label = (
        'Vtot = Vsys \u2212 BERV [km/s]'
        if vsys_ms is not None
        else '\u2212BERV [km/s]'
    )
    fig = _make_berv_figure(
        passed, ext_fail, tcorr_fail,
        curve_x, curve_y, vsys_ms, y_label,
    )
    script, div = plot_to_components(fig)
    return {
        'has_plot': True, 'script': script, 'div': div, 'message': ''
    }


# =============================================================================
# Define private file path helpers
# =============================================================================
def _resolve_file_path(row: Dict[str, Any],
                       paths: Dict[str, str]) -> Optional[Path]:
    """
    Resolve a FITS file path from an ftable row, guarding against
    path-traversal attacks.

    :param row: dict, ftable row with BLOCK_KIND, OBS_DIR, FILENAME
    :param paths: dict mapping PATH_* keys to directory strings

    :return: Path if the resolved file exists, None otherwise
    :rtype: Path | None
    """
    block_kind = str(row.get('BLOCK_KIND', '') or '').strip()
    path_key = _BLOCK_KIND_TO_PATH.get(block_kind)
    if not path_key:
        return None
    base_str = str(paths.get(path_key, '') or '').strip()
    if not base_str:
        return None
    base_p = Path(base_str).resolve()
    obs_dir = str(row.get('OBS_DIR', '') or '').strip()
    filename = str(row.get('FILENAME', '') or '').strip()
    if not filename:
        return None
    try:
        obs_part = (
            Path(obs_dir.strip('/')) if obs_dir else Path('')
        )
        candidate = (base_p / obs_part / filename).resolve()
        # raises ValueError on path traversal
        candidate.relative_to(base_p)
        return candidate if candidate.is_file() else None
    except (ValueError, OSError):
        return None


def _gauss_fn(x: Any, amp: float, pos: float,
              sig: float, dc: float) -> Any:
    """
    Evaluate a 1D Gaussian function with a DC offset.

    :param x: array-like, evaluation points
    :param amp: float, amplitude (negative for absorption lines)
    :param pos: float, centre position
    :param sig: float, standard deviation (width)
    :param dc: float, DC offset

    :return: array-like, evaluated Gaussian values
    :rtype: numpy.ndarray
    """
    return amp * np.exp(-0.5 * ((x - pos) / sig) ** 2) + dc


# =============================================================================
# Define private spectrum plot helpers
# =============================================================================
def _find_median_ext_row(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Return the ftable_ext row whose EXT_H value is closest to the
    median EXT_H across all htable rows.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts

    :return: tuple (best_row, best_identifier) or (None, None)
    :rtype: tuple
    """
    id_to_snr: Dict[str, float] = {}
    for row in htable_rows:
        ident = str(row.get('IDENTIFIER', '') or '').strip()
        raw_h = row.get('EXT_H')
        if ident and raw_h is not None:
            try:
                id_to_snr[ident] = float(raw_h)
            except (TypeError, ValueError):
                pass
    if not id_to_snr:
        return None, None
    med_snr = float(np.nanmedian(list(id_to_snr.values())))
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for row in ftable_ext_rows:
        ident = str(row.get('IDENTIFIER', '') or '').strip()
        if ident in id_to_snr:
            scored.append((abs(id_to_snr[ident] - med_snr), row))
    if not scored:
        return None, None
    scored.sort(key=lambda x: x[0])
    best_row = scored[0][1]
    best_ident = str(best_row.get('IDENTIFIER', '') or '').strip()
    return best_row, best_ident


def _find_ftable_row_by_identifier(
    ftable_rows: List[Dict[str, Any]],
    identifier: str,
) -> Optional[Dict[str, Any]]:
    """
    Return the first ftable row whose IDENTIFIER matches *identifier*.

    :param ftable_rows: list of ftable row dicts
    :param identifier: str, IDENTIFIER value to match

    :return: matching row dict or None
    :rtype: dict | None
    """
    for row in ftable_rows:
        if (str(row.get('IDENTIFIER', '') or '').strip()
                == identifier):
            return row
    return None


def _derive_s1d_path(ext_row: Dict[str, Any],
                     paths: Dict[str, str]) -> Optional[Path]:
    """
    Derive the extracted S1D path by replacing ``_e2dsff_`` with
    ``_s1d_v_`` in the filename.

    :param ext_row: dict, ftable ext row with FILENAME
    :param paths: dict mapping PATH_* keys to directory strings

    :return: resolved Path or None
    :rtype: Path | None
    """
    filename = str(ext_row.get('FILENAME', '') or '').strip()
    s1d_filename = filename.replace('_e2dsff_', '_s1d_v_')
    if s1d_filename == filename:
        return None
    return _resolve_file_path(
        dict(ext_row, FILENAME=s1d_filename), paths
    )


def _derive_sc1d_path(tcorr_row: Dict[str, Any],
                      paths: Dict[str, str]) -> Optional[Path]:
    """
    Derive the telluric-corrected S1D path by replacing
    ``_e2dsff_tcorr_`` with ``_s1d_v_tcorr_`` in the filename.

    :param tcorr_row: dict, ftable tcorr row with FILENAME
    :param paths: dict mapping PATH_* keys to directory strings

    :return: resolved Path or None
    :rtype: Path | None
    """
    filename = str(tcorr_row.get('FILENAME', '') or '').strip()
    sc1d_filename = filename.replace(
        '_e2dsff_tcorr_', '_s1d_v_tcorr_'
    )
    if sc1d_filename == filename:
        return None
    return _resolve_file_path(
        dict(tcorr_row, FILENAME=sc1d_filename), paths
    )


def _load_s1d_data(
    path: Path,
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Load (wavelength, flux) arrays from an S1D FITS BinTable
    (HDU index 1).

    :param path: Path, absolute path to the S1D FITS file

    :return: tuple (wavelength, flux) arrays, or (None, None) on error
    :rtype: tuple[numpy.ndarray | None, numpy.ndarray | None]
    """
    try:
        from astropy.io import fits as _fits
        with _fits.open(str(path)) as hdul:
            dat = hdul[1].data
            wave = np.array(dat['wavelength'], dtype=float)
            flux = np.array(dat['flux'], dtype=float)
        return wave, flux
    except Exception:
        return None, None


def _make_spec_band_figure(
    wave: np.ndarray,
    ext_flux: Optional[np.ndarray],
    tcorr_flux: Optional[np.ndarray],
    xlim: List[float],
    title: str,
    height: int = 280,
    sizing_mode: str = 'stretch_width',
) -> Any:
    """
    Build a single Bokeh figure for one wavelength band of the
    spectrum.

    :param wave: numpy.ndarray, wavelength array [nm]
    :param ext_flux: numpy.ndarray or None, extracted flux array
    :param tcorr_flux: numpy.ndarray or None, telluric-corrected flux
    :param xlim: list of two floats, [wave_min, wave_max] in nm
    :param title: str, figure title
    :param height: int, figure height in pixels
    :param sizing_mode: str, Bokeh sizing_mode (default 'stretch_width')

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    from bokeh.plotting import figure as bk_figure

    fig = bk_figure(
        title=title,
        x_axis_label='Wavelength [nm]',
        y_axis_label='Flux',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        active_scroll='wheel_zoom',
        height=height,
        sizing_mode=sizing_mode,
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    mask = (wave >= xlim[0]) & (wave <= xlim[1])
    w_m = wave[mask]
    # -------------------------------------------------------------------------
    if ext_flux is not None:
        ef_m = np.where(
            np.isfinite(ext_flux[mask]), ext_flux[mask], np.nan
        )
        fig.line(w_m, ef_m, line_color='black', line_width=0.8,
                 alpha=0.9, legend_label='Extracted')
    if tcorr_flux is not None:
        tf_m = np.where(
            np.isfinite(tcorr_flux[mask]), tcorr_flux[mask], np.nan
        )
        fig.line(w_m, tf_m, line_color='red', line_width=0.8,
                 alpha=0.9, legend_label='Telluric corrected')
        valid_tc = tf_m[np.isfinite(tf_m)]
        if len(valid_tc) > 0:
            fig.y_range.start = 0.0
            fig.y_range.end = float(
                1.5 * np.nanpercentile(valid_tc, 99)
            )
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _build_spec_layout(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    ftable_tcorr_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    maximize: bool = False,
) -> Tuple[Optional[Any], str]:
    """
    Core spectrum builder that returns ``(layout, message)``.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param ftable_tcorr_rows: list of ftable tcorr row dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param preset: dict, instrument profile preset

    :return: tuple (Bokeh layout or None, error message string)
    :rtype: tuple
    """
    from bokeh.layouts import column as bk_column, gridplot

    ext_row, best_ident = _find_median_ext_row(
        htable_rows, ftable_ext_rows
    )
    if ext_row is None:
        return None, 'No matching EXT spectrum found.'

    s1d_path = _derive_s1d_path(ext_row, paths)
    if s1d_path is None:
        return None, 'Extracted S1D file not found on disk.'

    wave, ext_flux = _load_s1d_data(s1d_path)
    if wave is None:
        return None, 'Could not load extracted S1D data.'
    # -------------------------------------------------------------------------
    # load telluric-corrected S1D (optional)
    tcorr_flux: Optional[np.ndarray] = None
    if best_ident:
        tcorr_row = _find_ftable_row_by_identifier(
            ftable_tcorr_rows, best_ident
        )
        if tcorr_row is not None:
            sc1d_path = _derive_sc1d_path(tcorr_row, paths)
            if sc1d_path is not None:
                _, tcorr_flux = _load_s1d_data(sc1d_path)
    # -------------------------------------------------------------------------
    # wavelength limits from preset
    spec_wave = (preset or {}).get('plot', {}).get('SpecWave', {})
    limit0: List[float] = spec_wave.get('limit0', [965, 2500])
    limit1: List[float] = spec_wave.get('limit1', [1082, 1085])
    limit2: List[float] = spec_wave.get('limit2', [1600, 1604])
    limit3: List[float] = spec_wave.get('limit3', [2164, 2169])
    # -------------------------------------------------------------------------
    # build title with median SNR
    snr_h_label = sci_header_label(
        preset, 'ext', 'EXT_H', 'H-band SNR'
    )
    med_snr_h: Optional[float] = None
    for row in htable_rows:
        if (str(row.get('IDENTIFIER', '') or '').strip()
                == best_ident):
            try:
                med_snr_h = float(row.get('EXT_H') or 0)
            except (TypeError, ValueError):
                pass
            break
    title_full = (
        f'Median spectrum [{snr_h_label}={med_snr_h:.1f}]'
        if med_snr_h is not None
        else 'Median spectrum'
    )
    # -------------------------------------------------------------------------
    # build figures for normal/object-page layout vs maximize layout
    if maximize:
        # In maximize mode each row is a separate Bokeh root so CSS
        # flex can give each ~50 % of the available viewport height.
        fig_full = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit0, title_full,
            height=200, sizing_mode='stretch_both',
        )
        fig_z1 = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit1,
            f'Zoom in {limit1[0]}\u2013{limit1[1]} nm',
            height=200, sizing_mode='stretch_both',
        )
        fig_z2 = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit2,
            f'Zoom in {limit2[0]}\u2013{limit2[1]} nm',
            height=200, sizing_mode='stretch_both',
        )
        fig_z3 = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit3,
            f'Zoom in {limit3[0]}\u2013{limit3[1]} nm',
            height=200, sizing_mode='stretch_both',
        )
        zoom_grid = gridplot(
            [[fig_z1, fig_z2, fig_z3]],
            sizing_mode='stretch_both',
        )
        # Return two separate roots; build_spec_plot_components will
        # call components([fig_full, zoom_grid]) to get one shared
        # script and two independent divs for the template.
        return [fig_full, zoom_grid], ''
    else:
        fig_full = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit0, title_full, height=280
        )
        fig_z1 = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit1,
            f'Zoom in {limit1[0]}\u2013{limit1[1]} nm', height=220,
        )
        fig_z2 = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit2,
            f'Zoom in {limit2[0]}\u2013{limit2[1]} nm', height=220,
        )
        fig_z3 = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit3,
            f'Zoom in {limit3[0]}\u2013{limit3[1]} nm', height=220,
        )
        layout = bk_column([
            fig_full,
            gridplot(
                [[fig_z1, fig_z2, fig_z3]],
                sizing_mode='stretch_width',
            ),
        ], sizing_mode='stretch_width')
    return layout, ''


# =============================================================================
# Define public spectrum plot builders
# =============================================================================
def build_spec_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    ftable_tcorr_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    target_id: str = 'op-spec-plot-div',
) -> Dict[str, Any]:
    """
    Build spectrum plot as a ``json_item`` dict for client-side
    embedding.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param ftable_tcorr_rows: list of ftable tcorr row dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param preset: dict, instrument profile preset
    :param target_id: str, DOM element ID for Bokeh embedding

    :return: dict with has_plot, item/message
    :rtype: dict
    """
    layout, msg = _build_spec_layout(
        htable_rows, ftable_ext_rows, ftable_tcorr_rows, paths, preset
    )
    if layout is None:
        return {'has_plot': False, 'message': msg}
    script, div = plot_to_components(layout)
    return {
        'has_plot': True,
        'script': script,
        'div': div,
        'message': '',
    }


def build_spec_plot_components(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    ftable_tcorr_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    maximize: bool = False,
) -> Dict[str, Any]:
    """
    Build spectrum plot as ``(script, div)`` for server-side embedding.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param ftable_tcorr_rows: list of ftable tcorr row dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param preset: dict, instrument profile preset

    :return: dict with has_plot, script, div, message
    :rtype: dict
    """
    layout, msg = _build_spec_layout(
        htable_rows, ftable_ext_rows, ftable_tcorr_rows, paths, preset,
        maximize=maximize,
    )
    if layout is None:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': msg,
        }
    if isinstance(layout, list):
        # maximize mode: two separate roots → one script, two divs
        from bokeh.embed import components as _bk_components
        script, div_list = _bk_components(layout)
        return {
            'has_plot': True,
            'script': script,
            'div': div_list[0],
            'div2': div_list[1],
            'two_rows': True,
            'message': '',
        }
    script, div = plot_to_components(layout)
    return {
        'has_plot': True, 'script': script, 'div': div, 'message': ''
    }


# =============================================================================
# Define private CCF helpers
# =============================================================================
def _load_ccf_data(
    ftable_ccf_rows: List[Dict[str, Any]],
    htable_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    ccf_mjd_start: Optional[float] = None,
    ccf_mjd_end: Optional[float] = None,
    max_files: int = 100,
) -> Optional[Tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]
]]:
    """
    Load and stack CCF data from all CCF FITS files.

    :param ftable_ccf_rows: list of ftable ccf row dicts
    :param htable_rows: list of htable row dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param ccf_mjd_start: float or None, lower MJD bound (inclusive)
    :param ccf_mjd_end: float or None, upper MJD bound (inclusive)
    :param max_files: int, maximum number of CCF files to load

    :return: tuple (rv_vec, all_ccf, datetimes, dv_ms, sdv_ms) sorted
             by time, or None if no data could be loaded
    :rtype: tuple | None
    """
    def _row_mid_obs_mjd(row: Dict[str, Any]) -> Optional[float]:
        raw = row.get('MID_OBS_TIME')
        if raw is None:
            return None
        sval = str(raw).strip()
        if not sval:
            return None
        try:
            return float(Time(sval, format='isot', scale='utc').mjd)
        except Exception:
            try:
                return float(sval)
            except Exception:
                return None

    def _equally_spaced_indices(nvals: int, nout: int) -> List[int]:
        if nvals <= 0 or nout <= 0:
            return []
        if nout >= nvals:
            return list(range(nvals))
        if nout == 1:
            return [0]
        idx = [int(round(i * (nvals - 1) / (nout - 1))) for i in range(nout)]
        uniq: List[int] = []
        seen = set()
        for i in idx:
            ii = min(max(i, 0), nvals - 1)
            if ii not in seen:
                seen.add(ii)
                uniq.append(ii)
        if len(uniq) < nout:
            for i in range(nvals):
                if i in seen:
                    continue
                uniq.append(i)
                if len(uniq) >= nout:
                    break
        return sorted(uniq[:nout])

    total_rows = len(ftable_ccf_rows)
    timed_rows: List[Tuple[float, Dict[str, Any]]] = []
    for row in ftable_ccf_rows:
        mjd = _row_mid_obs_mjd(row)
        if mjd is None:
            continue
        timed_rows.append((mjd, row))
    timed_rows.sort(key=lambda x: x[0])

    all_mjd_vals = [x[0] for x in timed_rows]
    available_mjd_min = min(all_mjd_vals) if all_mjd_vals else None
    available_mjd_max = max(all_mjd_vals) if all_mjd_vals else None

    in_range_rows: List[Tuple[float, Dict[str, Any]]] = []
    for mjd, row in timed_rows:
        if ccf_mjd_start is not None and mjd < ccf_mjd_start:
            continue
        if ccf_mjd_end is not None and mjd > ccf_mjd_end:
            continue
        in_range_rows.append((mjd, row))

    in_range_total = len(in_range_rows)
    if in_range_total > max_files:
        sel_idx = _equally_spaced_indices(in_range_total, max_files)
        selected_rows = [in_range_rows[i] for i in sel_idx]
        sampling_mode = 'equally_spaced'
    else:
        selected_rows = in_range_rows
        sampling_mode = 'all'

    summary: Dict[str, Any] = {
        'max_files': int(max_files),
        'total_rows': int(total_rows),
        'rows_with_mid_obs_time': int(len(timed_rows)),
        'in_range_total': int(in_range_total),
        'selected_total': int(len(selected_rows)),
        'loaded_total': 0,
        'sampling_mode': sampling_mode,
        'ccf_mjd_start': ccf_mjd_start,
        'ccf_mjd_end': ccf_mjd_end,
        'available_mjd_min': available_mjd_min,
        'available_mjd_max': available_mjd_max,
        'selected_mjd_min': (selected_rows[0][0] if selected_rows else None),
        'selected_mjd_max': (selected_rows[-1][0] if selected_rows else None),
    }

    ht_by_id: Dict[str, Dict[str, Any]] = {}
    for row in htable_rows:
        ident = str(row.get('IDENTIFIER', '') or '').strip()
        if ident:
            ht_by_id[ident] = row

    rv_vec: Optional[np.ndarray] = None
    all_ccf_rows: List[np.ndarray] = []
    datetimes_list: List[Any] = []
    dv_ms_list: List[float] = []
    sdv_ms_list: List[float] = []

    for mjd_val, row in selected_rows:
        path = _resolve_file_path(row, paths)
        if path is None:
            continue
        ident = str(row.get('IDENTIFIER', '') or '').strip()
        ht_row = ht_by_id.get(ident, {})
        raw_dv = ht_row.get('CCF_DV')
        raw_sdv = ht_row.get('CCF_SDV')
        if raw_dv is None or raw_sdv is None:
            continue
        try:
            dv_ms_val = float(raw_dv) * 1000.0   # km/s → m/s
            sdv_ms_val = float(raw_sdv)           # already m/s
            dt = mjd_to_datetime(float(mjd_val))
            if dt is None:
                continue
            read_out = _read_ccf_row_cached(str(path))
            if read_out is None:
                continue
            rv_file, ccf_row = read_out
            if rv_vec is None:
                rv_vec = rv_file
            med = float(np.nanmedian(ccf_row))
            if med != 0.0:
                ccf_row = ccf_row / med
            all_ccf_rows.append(ccf_row)
            datetimes_list.append(dt)
            dv_ms_list.append(dv_ms_val)
            sdv_ms_list.append(sdv_ms_val)
        except Exception:
            continue

    summary['loaded_total'] = int(len(all_ccf_rows))

    if rv_vec is None or len(all_ccf_rows) == 0:
        return None

    all_ccf = np.array(all_ccf_rows)
    datetimes = np.array(datetimes_list)
    dv_ms_arr = np.array(dv_ms_list)
    sdv_ms_arr = np.array(sdv_ms_list)
    sort_idx = np.argsort([dt.timestamp() for dt in datetimes])
    return (
        rv_vec,
        all_ccf[sort_idx],
        datetimes[sort_idx],
        dv_ms_arr[sort_idx],
        sdv_ms_arr[sort_idx],
        summary,
    )


def _fit_ccf_gaussian(
    rv_vec: np.ndarray,
    med_ccf: np.ndarray,
) -> Tuple[bool, np.ndarray, List[float]]:
    """
    Fit a Gaussian to the median CCF.

    :param rv_vec: numpy.ndarray, RV axis values [km/s]
    :param med_ccf: numpy.ndarray, median CCF values (normalised)

    :return: tuple (has_fit, fit_array, xlim)
    :rtype: tuple[bool, numpy.ndarray, list[float]]
    """
    try:
        from scipy.optimize import curve_fit
    except ImportError:
        return (
            False,
            np.full(len(rv_vec), np.nan),
            [float(rv_vec.min()), float(rv_vec.max())],
        )

    amp0 = 1.0 - float(med_ccf[np.argmin(med_ccf)])
    pos0 = float(rv_vec[np.argmin(med_ccf)])
    guess = [-amp0, pos0, 4.0, 1.0]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            coeffs, _ = curve_fit(
                _gauss_fn, rv_vec, med_ccf,
                p0=guess, maxfev=5000,
            )
        fit = _gauss_fn(rv_vec, *coeffs)
        xlim: List[float] = [
            coeffs[1] - abs(coeffs[2]) * 20,
            coeffs[1] + abs(coeffs[2]) * 20,
        ]
        return True, fit, xlim
    except Exception:
        return (
            False,
            np.full(len(rv_vec), np.nan),
            [float(rv_vec.min()), float(rv_vec.max())],
        )


def _make_ccf_rv_figure(
    datetimes: np.ndarray,
    dv_ms: np.ndarray,
    sdv_ms: np.ndarray,
    height: int = 250,
) -> Any:
    """
    Build the CCF RV vs time panel with error bars (Whisker) and
    outlier markers.

    :param datetimes: numpy.ndarray, UTC datetime objects
    :param dv_ms: numpy.ndarray, CCF RV values [m/s]
    :param sdv_ms: numpy.ndarray, CCF RV uncertainties [m/s]
    :param height: int, figure height in pixels

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    from bokeh.models import Whisker

    fig = make_time_figure('CCF Radial Velocity vs Time', height=height)
    fig.add_tools(HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('RV', '@y{0.000} m/s'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    ))
    pp = np.nanpercentile(dv_ms, [10, 90])
    diff = float(pp[1] - pp[0])
    if diff < 1e-6:
        diff = max(abs(float(np.nanmean(dv_ms))) * 0.01, 1.0)
    central = float(np.nanmean(pp))
    ylim_lo = central - 1.5 * diff
    ylim_hi = central + 1.5 * diff

    dts_ms = np.array([dt.timestamp() * 1000.0 for dt in datetimes])
    good = (dv_ms >= ylim_lo) & (dv_ms <= ylim_hi)
    # -------------------------------------------------------------------------
    if np.any(good):
        src = ColumnDataSource(dict(
            x=dts_ms[good], y=dv_ms[good],
            upper=dv_ms[good] + sdv_ms[good],
            lower=dv_ms[good] - sdv_ms[good],
        ))
        fig.circle('x', 'y', source=src, size=6, color='green',
                   alpha=0.7, legend_label='Good')
        fig.add_layout(Whisker(
            source=src, base='x', upper='upper', lower='lower',
            line_color='green', line_alpha=0.5,
        ))
    # -------------------------------------------------------------------------
    l_arrow = 0.04 * diff
    for clip_mask, yt, marker in [
        (dv_ms < ylim_lo, ylim_lo + l_arrow, 'triangle'),
        (dv_ms > ylim_hi, ylim_hi - l_arrow, 'inverted_triangle'),
    ]:
        if np.any(clip_mask):
            src_out = ColumnDataSource(dict(
                x=dts_ms[clip_mask],
                y=np.full(int(np.sum(clip_mask)), yt),
            ))
            fig.scatter('x', 'y', source=src_out, marker=marker,
                        size=8, color='red', alpha=0.8,
                        legend_label='Outlier')
    # -------------------------------------------------------------------------
    fig.y_range.start = ylim_lo
    fig.y_range.end = ylim_hi
    fig.yaxis.axis_label = 'RV [m/s]'
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _make_ccf_profile_figure(
    rv_vec: np.ndarray,
    med_ccf: np.ndarray,
    y1_1sig: np.ndarray,
    y2_1sig: np.ndarray,
    y1_2sig: np.ndarray,
    y2_2sig: np.ndarray,
    fit: np.ndarray,
    xlim: List[float],
    has_fit: bool,
    height: int = 280,
) -> Any:
    """
    Build the median CCF profile with 1σ/2σ band overlays and a
    Gaussian fit panel.

    :param rv_vec: numpy.ndarray, RV axis [km/s]
    :param med_ccf: numpy.ndarray, median normalised CCF
    :param y1_1sig: numpy.ndarray, lower 1σ percentile across epochs
    :param y2_1sig: numpy.ndarray, upper 1σ percentile
    :param y1_2sig: numpy.ndarray, lower 2σ percentile
    :param y2_2sig: numpy.ndarray, upper 2σ percentile
    :param fit: numpy.ndarray, Gaussian fit values
    :param xlim: list of two floats, RV display window [km/s]
    :param has_fit: bool, whether the Gaussian fit succeeded
    :param height: int, figure height in pixels

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    from bokeh.models import Band
    from bokeh.plotting import figure as bk_figure

    limmask = (rv_vec >= xlim[0]) & (rv_vec <= xlim[1])
    rv_m = rv_vec[limmask]

    fig = bk_figure(
        title='Median CCF Profile',
        x_axis_label='RV [km/s]',
        y_axis_label='Normalized CCF',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        active_scroll='wheel_zoom',
        height=height,
        sizing_mode='stretch_width',
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.add_tools(HoverTool(
        tooltips=[('RV', '$x{0.000} km/s'), ('CCF', '$y{0.000000}')],
        mode='mouse',
    ))
    fig.add_tools(CrosshairTool(dimensions='both'))
    # -------------------------------------------------------------------------
    src_2 = ColumnDataSource(dict(
        x=rv_m,
        upper=y2_2sig[limmask],
        lower=y1_2sig[limmask],
    ))
    fig.add_layout(Band(
        base='x', upper='upper', lower='lower', source=src_2,
        fill_color='orange', fill_alpha=0.4, line_color=None,
    ))
    src_1 = ColumnDataSource(dict(
        x=rv_m,
        upper=y2_1sig[limmask],
        lower=y1_1sig[limmask],
    ))
    fig.add_layout(Band(
        base='x', upper='upper', lower='lower', source=src_1,
        fill_color='red', fill_alpha=0.4, line_color=None,
    ))
    # legend proxy quads for bands (on hidden extra ranges so auto-range unaffected)
    fig.extra_x_ranges['_proxy'] = Range1d(start=0, end=1)
    fig.extra_y_ranges['_proxy'] = Range1d(start=0, end=1)
    fig.quad(left=[5], right=[6], top=[6], bottom=[5],
            fill_color='orange', fill_alpha=0.4, line_color=None,
            legend_label='2σ band',
            x_range_name='_proxy', y_range_name='_proxy')
    fig.quad(left=[5], right=[6], top=[6], bottom=[5],
            fill_color='red', fill_alpha=0.4, line_color=None,
            legend_label='1σ band',
            x_range_name='_proxy', y_range_name='_proxy')
    fig.line(rv_m, med_ccf[limmask], line_color='black',
             line_width=1.5, legend_label='Median CCF')
    if has_fit:
        fig.line(rv_m, fit[limmask], line_color='dodgerblue',
                 line_width=2.0, line_dash='dashed',
                 legend_label='Gaussian fit')
    # initial zoom to 2σ envelope with 10% padding
    y_lo = float(np.nanmin(y1_2sig[limmask]))
    y_hi = float(np.nanmax(y2_2sig[limmask]))
    y_pad = 0.1 * (y_hi - y_lo) if y_hi > y_lo else 0.01
    fig.y_range = Range1d(start=y_lo - y_pad, end=y_hi + y_pad)
    x_pad = 0.02 * (float(rv_m[-1]) - float(rv_m[0])) if len(rv_m) > 1 else 1.0
    fig.x_range = Range1d(start=float(rv_m[0]) - x_pad,
                          end=float(rv_m[-1]) + x_pad)
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _make_ccf_residuals_figure(
    rv_vec: np.ndarray,
    med_ccf: np.ndarray,
    fit: np.ndarray,
    y1_1sig: np.ndarray,
    y2_1sig: np.ndarray,
    y1_2sig: np.ndarray,
    y2_2sig: np.ndarray,
    xlim: List[float],
    has_fit: bool,
    height: int = 230,
) -> Any:
    """
    Build the CCF residuals (CCF minus Gaussian fit) panel.

    :param rv_vec: numpy.ndarray, RV axis [km/s]
    :param med_ccf: numpy.ndarray, median normalised CCF
    :param fit: numpy.ndarray, Gaussian fit values
    :param y1_1sig: numpy.ndarray, lower 1σ percentile across epochs
    :param y2_1sig: numpy.ndarray, upper 1σ percentile
    :param y1_2sig: numpy.ndarray, lower 2σ percentile
    :param y2_2sig: numpy.ndarray, upper 2σ percentile
    :param xlim: list of two floats, RV display window [km/s]
    :param has_fit: bool, whether the Gaussian fit succeeded
    :param height: int, figure height in pixels

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    from bokeh.models import Band
    from bokeh.plotting import figure as bk_figure

    limmask = (rv_vec >= xlim[0]) & (rv_vec <= xlim[1])
    rv_m = rv_vec[limmask]

    fig = bk_figure(
        title='CCF Residuals (CCF \u2212 fit)',
        x_axis_label='RV [km/s]',
        y_axis_label='Residuals',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        active_scroll='wheel_zoom',
        height=height,
        sizing_mode='stretch_width',
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.add_tools(HoverTool(
        tooltips=[('RV', '$x{0.000} km/s'), ('Residual', '$y{0.000000}')],
        mode='mouse',
    ))
    fig.add_tools(CrosshairTool(dimensions='both'))
    # -------------------------------------------------------------------------
    if has_fit:
        f_m = fit[limmask]
        src_2 = ColumnDataSource(dict(
            x=rv_m,
            upper=y2_2sig[limmask] - f_m,
            lower=y1_2sig[limmask] - f_m,
        ))
        src_1 = ColumnDataSource(dict(
            x=rv_m,
            upper=y2_1sig[limmask] - f_m,
            lower=y1_1sig[limmask] - f_m,
        ))
        fig.add_layout(Band(
            base='x', upper='upper', lower='lower', source=src_2,
            fill_color='orange', fill_alpha=0.4,
        ))
        fig.add_layout(Band(
            base='x', upper='upper', lower='lower', source=src_1,
            fill_color='red', fill_alpha=0.4,
        ))
        # legend proxy quads for bands (on hidden extra ranges)
        fig.extra_x_ranges['_proxy'] = Range1d(start=0, end=1)
        fig.extra_y_ranges['_proxy'] = Range1d(start=0, end=1)
        fig.quad(left=[5], right=[6], top=[6], bottom=[5],
                fill_color='orange', fill_alpha=0.4, line_color=None,
                legend_label='2σ band',
                x_range_name='_proxy', y_range_name='_proxy')
        fig.quad(left=[5], right=[6], top=[6], bottom=[5],
                fill_color='red', fill_alpha=0.4, line_color=None,
                legend_label='1σ band',
                x_range_name='_proxy', y_range_name='_proxy')
        fig.line(rv_m, med_ccf[limmask] - f_m, line_color='black',
                 line_width=1.2, legend_label='Median residual')
        # initial zoom to 2σ residual envelope with 10% padding
        res_lo = float(np.nanmin(y1_2sig[limmask] - f_m))
        res_hi = float(np.nanmax(y2_2sig[limmask] - f_m))
        res_pad = 0.1 * (res_hi - res_lo) if res_hi > res_lo else 0.01
        fig.y_range = Range1d(start=res_lo - res_pad, end=res_hi + res_pad)
        x_pad = 0.02 * (float(rv_m[-1]) - float(rv_m[0])) if len(rv_m) > 1 else 1.0
        fig.x_range = Range1d(start=float(rv_m[0]) - x_pad,
                              end=float(rv_m[-1]) + x_pad)
        fig.legend.location = 'top_right'
    else:
        fig.text(
            x=[0.5], y=[0.5],
            text=['No Gaussian fit available'],
            text_font_size='12pt', text_color='gray',
            text_align='center',
            x_units='screen', y_units='screen',
        )
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _make_ccf_spread_figure(
    rv_vec: np.ndarray,
    med_ccf: np.ndarray,
    y1_1sig: np.ndarray,
    y2_1sig: np.ndarray,
    y1_2sig: np.ndarray,
    y2_2sig: np.ndarray,
    xlim: List[float],
    has_fit: bool,
    height: int = 230,
) -> Any:
    """
    Build the CCF spread (percentile bands relative to the median)
    panel.

    :param rv_vec: numpy.ndarray, RV axis [km/s]
    :param med_ccf: numpy.ndarray, median normalised CCF
    :param y1_1sig: numpy.ndarray, lower 1σ percentile across epochs
    :param y2_1sig: numpy.ndarray, upper 1σ percentile
    :param y1_2sig: numpy.ndarray, lower 2σ percentile
    :param y2_2sig: numpy.ndarray, upper 2σ percentile
    :param xlim: list of two floats, RV display window [km/s]
    :param has_fit: bool, whether the Gaussian fit succeeded (unused)
    :param height: int, figure height in pixels

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    from bokeh.models import Band
    from bokeh.plotting import figure as bk_figure

    limmask = (rv_vec >= xlim[0]) & (rv_vec <= xlim[1])
    rv_m = rv_vec[limmask]
    med_m = med_ccf[limmask]

    fig = bk_figure(
        title='CCF Spread (relative to median)',
        x_axis_label='RV [km/s]',
        y_axis_label='Spread',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        active_scroll='wheel_zoom',
        height=height,
        sizing_mode='stretch_width',
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.add_tools(HoverTool(
        tooltips=[('RV', '$x{0.000} km/s'), ('Spread', '$y{0.000000}')],
        mode='mouse',
    ))
    fig.add_tools(CrosshairTool(dimensions='both'))
    # -------------------------------------------------------------------------
    spread_2sig_upper = y2_2sig[limmask] - med_m
    spread_2sig_lower = y1_2sig[limmask] - med_m
    src_2 = ColumnDataSource(dict(
        x=rv_m,
        upper=spread_2sig_upper,
        lower=spread_2sig_lower,
    ))
    src_1 = ColumnDataSource(dict(
        x=rv_m,
        upper=y2_1sig[limmask] - med_m,
        lower=y1_1sig[limmask] - med_m,
    ))
    fig.add_layout(Band(
        base='x', upper='upper', lower='lower', source=src_2,
        fill_color='orange', fill_alpha=0.4, line_color=None,
    ))
    fig.add_layout(Band(
        base='x', upper='upper', lower='lower', source=src_1,
        fill_color='red', fill_alpha=0.4, line_color=None,
    ))
    # legend proxy quads for bands (on hidden extra ranges)
    fig.extra_x_ranges['_proxy'] = Range1d(start=0, end=1)
    fig.extra_y_ranges['_proxy'] = Range1d(start=0, end=1)
    fig.quad(left=[5], right=[6], top=[6], bottom=[5],
            fill_color='orange', fill_alpha=0.4, line_color=None,
            legend_label='2σ band',
            x_range_name='_proxy', y_range_name='_proxy')
    fig.quad(left=[5], right=[6], top=[6], bottom=[5],
            fill_color='red', fill_alpha=0.4, line_color=None,
            legend_label='1σ band',
            x_range_name='_proxy', y_range_name='_proxy')
    fig.line(rv_m, np.zeros(len(rv_m)), line_color='black',
             line_width=1.2, legend_label='Median (zero)')
    # initial zoom to 2 sigma range
    y_max_2sig = float(np.nanmax(np.abs(np.concatenate(
        [spread_2sig_upper, spread_2sig_lower]))))
    if y_max_2sig > 0:
        fig.y_range.start = -1.1 * y_max_2sig
        fig.y_range.end = 1.1 * y_max_2sig
    x_pad = 0.02 * (float(rv_m[-1]) - float(rv_m[0])) if len(rv_m) > 1 else 1.0
    fig.x_range = Range1d(start=float(rv_m[0]) - x_pad,
                          end=float(rv_m[-1]) + x_pad)
    fig.legend.location = 'top_right'
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _build_ccf_layout(
    htable_rows: List[Dict[str, Any]],
    ftable_ccf_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    ccf_mjd_start: Optional[float] = None,
    ccf_mjd_end: Optional[float] = None,
    ccf_nobs: int = 100,
) -> Tuple[Optional[Any], str, Dict[str, Any]]:
    """
    Core CCF builder that returns ``(layout, message)``.

    :param htable_rows: list of htable row dicts
    :param ftable_ccf_rows: list of ftable ccf row dicts
    :param paths: dict mapping PATH_* keys to directory strings

    :return: tuple (Bokeh layout or None, error message string)
    :rtype: tuple
    """
    from bokeh.layouts import column as bk_column

    t_load0 = time.perf_counter()
    result = _load_ccf_data(
        ftable_ccf_rows,
        htable_rows,
        paths,
        ccf_mjd_start=ccf_mjd_start,
        ccf_mjd_end=ccf_mjd_end,
        max_files=int(max(1, ccf_nobs)),
    )
    load_ms = (time.perf_counter() - t_load0) * 1000.0
    if result is None:
        return None, 'No CCF data could be loaded.', {
            'max_files': int(max(1, ccf_nobs)),
            'sampling_mode': 'all',
            'selected_total': 0,
            'loaded_total': 0,
            'in_range_total': 0,
            'ccf_mjd_start': ccf_mjd_start,
            'ccf_mjd_end': ccf_mjd_end,
            'timings_ms': {
                'load_data': round(load_ms, 2),
                'stats_fit': 0.0,
                'build_figures': 0.0,
                'total': round(load_ms, 2),
            },
        }

    rv_vec, all_ccf, datetimes, dv_ms, sdv_ms, summary = result
    rv_used, ccf_used, rv_points_orig, rv_points_used = _decimate_ccf_grid(
        rv_vec, all_ccf, max_points=_CCF_RV_MAX_POINTS
    )
    summary['rv_points_original'] = int(rv_points_orig)
    summary['rv_points_used'] = int(rv_points_used)
    summary['rv_decimated'] = bool(rv_points_used < rv_points_orig)
    # -------------------------------------------------------------------------
    # percentile bands for profile, residuals, and spread panels
    t_stats0 = time.perf_counter()
    lower1 = 100.0 * (0.5 - 0.6827 / 2.0)
    upper1 = 100.0 * (0.5 + 0.6827 / 2.0)
    lower2 = 100.0 * (0.5 - 0.9545 / 2.0)
    upper2 = 100.0 * (0.5 + 0.9545 / 2.0)
    y1_1sig = np.nanpercentile(ccf_used, lower1, axis=0)
    y2_1sig = np.nanpercentile(ccf_used, upper1, axis=0)
    y1_2sig = np.nanpercentile(ccf_used, lower2, axis=0)
    y2_2sig = np.nanpercentile(ccf_used, upper2, axis=0)
    med_ccf = np.nanmedian(ccf_used, axis=0)
    has_fit, fit, xlim = _fit_ccf_gaussian(rv_used, med_ccf)
    stats_ms = (time.perf_counter() - t_stats0) * 1000.0
    # -------------------------------------------------------------------------
    t_fig0 = time.perf_counter()
    fig_rv = _make_ccf_rv_figure(datetimes, dv_ms, sdv_ms)
    fig_prof = _make_ccf_profile_figure(
        rv_used, med_ccf,
        y1_1sig, y2_1sig, y1_2sig, y2_2sig,
        fit, xlim, has_fit,
    )
    fig_res = _make_ccf_residuals_figure(
        rv_used, med_ccf, fit,
        y1_1sig, y2_1sig, y1_2sig, y2_2sig,
        xlim, has_fit,
    )
    fig_spread = _make_ccf_spread_figure(
        rv_used, med_ccf,
        y1_1sig, y2_1sig, y1_2sig, y2_2sig,
        xlim, has_fit,
    )
    fig_ms = (time.perf_counter() - t_fig0) * 1000.0

    if str(summary.get('sampling_mode', '')) == 'equally_spaced':
        smjd = summary.get('selected_mjd_min', None)
        emjd = summary.get('selected_mjd_max', None)
        try:
            sdate = Time(float(smjd), format='mjd').to_datetime(
                timezone=timezone.utc).strftime('%Y-%m-%d')
            edate = Time(float(emjd), format='mjd').to_datetime(
                timezone=timezone.utc).strftime('%Y-%m-%d')
        except Exception:
            sdate = '--'
            edate = '--'
        nobs = int(summary.get('selected_total', 0) or 0)
        suffix = f' [{sdate} to {edate}, Nobs={nobs}]'
        fig_rv.title.text = str(fig_rv.title.text) + suffix
        fig_prof.title.text = str(fig_prof.title.text) + suffix
        fig_res.title.text = str(fig_res.title.text) + suffix
        fig_spread.title.text = str(fig_spread.title.text) + suffix

    layout = bk_column([fig_rv, fig_prof, fig_res, fig_spread],
                       sizing_mode='stretch_width')
    total_ms = load_ms + stats_ms + fig_ms
    summary['timings_ms'] = {
        'load_data': round(load_ms, 2),
        'stats_fit': round(stats_ms, 2),
        'build_figures': round(fig_ms, 2),
        'total': round(total_ms, 2),
    }
    return layout, '', summary


# =============================================================================
# Define public CCF plot builders
# =============================================================================
def build_ccf_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ccf_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    ccf_mjd_start: Optional[float] = None,
    ccf_mjd_end: Optional[float] = None,
    ccf_nobs: int = 100,
    target_id: str = 'op-ccf-plot-div',
) -> Dict[str, Any]:
    """
    Build CCF plot (4 panels) as a ``json_item`` dict for client-side
    embedding.

    :param htable_rows: list of htable row dicts
    :param ftable_ccf_rows: list of ftable ccf row dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param preset: dict, instrument profile preset (unused – reserved)
    :param target_id: str, DOM element ID for Bokeh embedding

    :return: dict with has_plot, item/message
    :rtype: dict
    """
    layout, msg, summary = _build_ccf_layout(
        htable_rows,
        ftable_ccf_rows,
        paths,
        ccf_mjd_start=ccf_mjd_start,
        ccf_mjd_end=ccf_mjd_end,
        ccf_nobs=ccf_nobs,
    )
    if layout is None:
        return {'has_plot': False, 'message': msg, 'sample_info': summary}
    script, div = plot_to_components(layout)
    return {
        'has_plot': True,
        'script': script,
        'div': div,
        'message': '',
        'sample_info': summary,
    }


def build_ccf_plot_components(
    htable_rows: List[Dict[str, Any]],
    ftable_ccf_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    ccf_mjd_start: Optional[float] = None,
    ccf_mjd_end: Optional[float] = None,
    ccf_nobs: int = 100,
) -> Dict[str, Any]:
    """
    Build CCF plot as ``(script, div)`` for server-side embedding.

    :param htable_rows: list of htable row dicts
    :param ftable_ccf_rows: list of ftable ccf row dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param preset: dict, instrument profile preset (unused – reserved)

    :return: dict with has_plot, script, div, message
    :rtype: dict
    """
    layout, msg, summary = _build_ccf_layout(
        htable_rows,
        ftable_ccf_rows,
        paths,
        ccf_mjd_start=ccf_mjd_start,
        ccf_mjd_end=ccf_mjd_end,
        ccf_nobs=ccf_nobs,
    )
    if layout is None:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': msg,
            'sample_info': summary,
        }
    script, div = plot_to_components(layout)
    return {
        'has_plot': True,
        'script': script,
        'div': div,
        'message': '',
        'sample_info': summary,
    }


# =============================================================================
# Define private LBL helpers
# =============================================================================
def _lbl_rdb_flavor_id(filename: str) -> str:
    """
    Extract a flavor ID string from an LBL RDB filename.

    For example, ``lbl_GL699_GL699.rdb`` → ``GL699_GL699``.

    :param filename: str, RDB file name (may include directory)

    :return: str, flavor ID or the raw filename on no match
    :rtype: str
    """
    fname = Path(filename).name
    m = re.match(r'^lbl_(.+)\.rdb$', fname, re.IGNORECASE)
    return m.group(1) if m else fname


def _load_lbl_table(
    lbl_row: Dict[str, Any],
    path_lbl: str,
) -> Tuple[Optional[str], Optional[Any]]:
    """
    Load an LBL RDB Table from disk.

    :param lbl_row: dict, ftable lbl_rdb row with OBS_DIR and FILENAME
    :param path_lbl: str, base LBL directory path

    :return: tuple (flavor_id, Table) or (None, None) on failure
    :rtype: tuple[str | None, astropy.table.Table | None]
    """
    if not path_lbl:
        return None, None
    obs_dir = str(lbl_row.get('OBS_DIR', '') or '').strip()
    filename = str(lbl_row.get('FILENAME', '') or '').strip()
    if not filename:
        return None, None
    base = Path(path_lbl).resolve()
    try:
        obs_part = (
            Path(obs_dir.strip('/')) if obs_dir else Path('')
        )
        candidate = (base / obs_part / filename).resolve()
        candidate.relative_to(base)
        if not candidate.is_file():
            return None, None
    except (ValueError, OSError):
        return None, None
    try:
        from astropy.table import Table as _ATable
        tbl = _ATable.read(str(candidate), format='ascii.rdb')
    except Exception:
        return None, None
    return _lbl_rdb_flavor_id(filename), tbl


def _lbl_wave_colour(wave_nm: float,
                     wave_min: float, wave_max: float) -> str:
    """
    Map a wavelength value to a blue→red hex colour string using a
    simple coolwarm approximation.

    :param wave_nm: float, wavelength in nm
    :param wave_min: float, minimum wavelength in nm (→ blue)
    :param wave_max: float, maximum wavelength in nm (→ red)

    :return: str, hex colour string e.g. '#ff8000'
    :rtype: str
    """
    span = wave_max - wave_min
    t = (
        0.0 if span <= 0
        else max(0.0, min(1.0, (wave_nm - wave_min) / span))
    )
    if t < 0.5:
        r = int(round(2.0 * t * 255))
        g = int(round(2.0 * t * 255))
        b = 255
    else:
        r = 255
        g = int(round(2.0 * (1.0 - t) * 255))
        b = int(round(2.0 * (1.0 - t) * 255))
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def _make_lbl_rv_figure(
    datetimes: np.ndarray,
    vrad: np.ndarray,
    svrad: np.ndarray,
    reset_mask: np.ndarray,
    ylim: List[float],
    flavor_id: str,
    height: int = 280,
) -> Any:
    """
    Build the LBL RV vs time panel with error bars, reset-RV coloring,
    and outlier markers.

    :param datetimes: numpy.ndarray, UTC datetime objects
    :param vrad: numpy.ndarray, radial velocity array [m/s]
    :param svrad: numpy.ndarray, RV uncertainty array [m/s]
    :param reset_mask: numpy.ndarray bool, True where RESET_RV is set
    :param ylim: list of two floats, display y-axis limits
    :param flavor_id: str, RDB flavor identifier for the title
    :param height: int, figure height in pixels

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    from bokeh.models import Whisker

    fig = make_time_figure(
        f'LBL Radial Velocity \u2014 {flavor_id}', height=height
    )
    fig.add_tools(HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('RV', '@y{0.000} m/s'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    ))
    dts_ms = np.array([dt.timestamp() * 1000.0 for dt in datetimes])
    good = ~reset_mask
    # -------------------------------------------------------------------------
    if np.any(good):
        src = ColumnDataSource(dict(
            x=dts_ms[good], y=vrad[good],
            upper=vrad[good] + svrad[good],
            lower=vrad[good] - svrad[good],
        ))
        fig.circle('x', 'y', source=src, size=5, color='green',
                   alpha=0.7, legend_label='Good')
        fig.add_layout(Whisker(
            source=src, base='x', upper='upper', lower='lower',
            line_color='green', line_alpha=0.5,
        ))
    if np.any(reset_mask):
        src_rst = ColumnDataSource(dict(
            x=dts_ms[reset_mask], y=vrad[reset_mask],
            upper=vrad[reset_mask] + svrad[reset_mask],
            lower=vrad[reset_mask] - svrad[reset_mask],
        ))
        fig.circle('x', 'y', source=src_rst, size=5,
                   color='mediumpurple', alpha=0.7,
                   legend_label='Reset RV')
        fig.add_layout(Whisker(
            source=src_rst, base='x', upper='upper', lower='lower',
            line_color='mediumpurple', line_alpha=0.5,
        ))
    # -------------------------------------------------------------------------
    diff = float(ylim[1] - ylim[0])
    l_arrow = 0.04 * diff
    for clip_mask, yt, marker in [
        (vrad < ylim[0], ylim[0] + l_arrow, 'triangle'),
        (vrad > ylim[1], ylim[1] - l_arrow, 'inverted_triangle'),
    ]:
        if np.any(clip_mask):
            src_out = ColumnDataSource(dict(
                x=dts_ms[clip_mask],
                y=np.full(int(np.sum(clip_mask)), yt),
            ))
            fig.scatter('x', 'y', source=src_out, marker=marker,
                        size=8, color='red', alpha=0.8,
                        legend_label='Outlier')
    # -------------------------------------------------------------------------
    fig.y_range.start = ylim[0]
    fig.y_range.end = ylim[1]
    fig.yaxis.axis_label = 'Velocity [m/s]'
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _make_lbl_snr_figure(
    datetimes: np.ndarray,
    snr_h: np.ndarray,
    reset_mask: np.ndarray,
    bad_idxs: List[int],
    snr_label: str,
    height: int = 230,
) -> Any:
    """
    Build the LBL SNR_H vs time panel.

    :param datetimes: numpy.ndarray, UTC datetime objects
    :param snr_h: numpy.ndarray, SNR H-band values
    :param reset_mask: numpy.ndarray bool, True where RESET_RV is set
    :param bad_idxs: list of int, indices of outlier points
    :param snr_label: str, y-axis label
    :param height: int, figure height in pixels

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    fig = make_time_figure(f'{snr_label} vs Time', height=height)
    fig.add_tools(HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('SNR', '@y{0.00}'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    ))
    dts_ms = np.array([dt.timestamp() * 1000.0 for dt in datetimes])
    bad_set = set(bad_idxs)
    bad_mask = np.array(
        [i in bad_set for i in range(len(datetimes))], dtype=bool
    )
    good_no_bad = (~reset_mask) & (~bad_mask)
    # -------------------------------------------------------------------------
    if np.any(good_no_bad):
        fig.circle(dts_ms[good_no_bad], snr_h[good_no_bad],
                   size=5, color='green', alpha=0.7,
                   legend_label='Good')
    if np.any(reset_mask):
        fig.circle(dts_ms[reset_mask], snr_h[reset_mask],
                   size=5, color='mediumpurple', alpha=0.7,
                   legend_label='Reset RV')
    if np.any(bad_mask):
        fig.circle(dts_ms[bad_mask], snr_h[bad_mask],
                   size=5, color='red', alpha=0.8,
                   legend_label='Outlier')
    # -------------------------------------------------------------------------
    fig.yaxis.axis_label = snr_label
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _make_lbl_wave_figure(
    datetimes: np.ndarray,
    vrad: np.ndarray,
    svrad: np.ndarray,
    wave_vrad_dict: Dict[str, np.ndarray],
    wave_svrad_dict: Dict[str, np.ndarray],
    wavemap: List[float],
    flavor_id: str = '',
    height: int = 280,
) -> Any:
    """
    Build the LBL wavelength-binned RV vs time panel, coloured by
    wavelength.

    :param datetimes: numpy.ndarray, UTC datetime objects
    :param vrad: numpy.ndarray, overall RV array [m/s]
    :param svrad: numpy.ndarray, overall RV uncertainty array [m/s]
    :param wave_vrad_dict: dict mapping column names to wave RV arrays
    :param wave_svrad_dict: dict mapping column names to wave σRV arrays
    :param wavemap: list of float, wavelength [nm] per column
    :param height: int, figure height in pixels

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    from bokeh.models import DatetimeTickFormatter
    from bokeh.plotting import figure as bk_figure

    from bokeh.models import Whisker

    fig = bk_figure(
        title=f'LBL Wave RV vs Time \u2014 {flavor_id}' if flavor_id else 'LBL Wave RV vs Time',
        x_axis_type='datetime',
        x_axis_label='Date',
        y_axis_label='RV [m/s]',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        active_scroll='wheel_zoom',
        height=height,
        sizing_mode='stretch_width',
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.add_tools(HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('RV', '@y{0.000} m/s'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    ))
    fig.add_tools(CrosshairTool(dimensions='both'))
    fig.xaxis.formatter = DatetimeTickFormatter(
        days='%Y-%m-%d', months='%Y-%m', years='%Y',
    )

    wave_min = min(wavemap) if wavemap else 900.0
    wave_max = max(wavemap) if wavemap else 2500.0
    med_svrad = (
        float(np.nanmedian(svrad)) if len(svrad) > 0 else 1.0
    )
    dts_ms = np.array([dt.timestamp() * 1000.0 for dt in datetimes])
    # -------------------------------------------------------------------------
    for col_key, wave_nm in zip(wave_vrad_dict.keys(), wavemap):
        vrad_key = wave_vrad_dict[col_key]
        svrad_col = col_key.replace('vrad_', 'svrad_')
        svrad_key = wave_svrad_dict.get(
            svrad_col, np.full(len(vrad_key), np.nan)
        )
        med_svrad_key = (
            float(np.nanmedian(svrad_key))
            if len(svrad_key) > 0 else 0.0
        )
        if med_svrad_key > 10.0 * med_svrad:
            continue
        if med_svrad > 0 and med_svrad_key < med_svrad * 0.01:
            continue
        color = _lbl_wave_colour(wave_nm, wave_min, wave_max)
        label = f'{int(wave_nm)} nm'
        src_w = ColumnDataSource(dict(
            x=dts_ms, y=vrad_key,
            upper=vrad_key + svrad_key,
            lower=vrad_key - svrad_key,
        ))
        fig.scatter('x', 'y', source=src_w, size=4, color=color,
                    alpha=0.6, marker='circle', legend_label=label)
        fig.add_layout(Whisker(
            source=src_w, base='x', upper='upper', lower='lower',
            line_color=color, line_alpha=0.3,
        ))
    # overall vrad as black points
    src_ov = ColumnDataSource(dict(
        x=dts_ms, y=vrad,
        upper=vrad + svrad,
        lower=vrad - svrad,
    ))
    fig.scatter('x', 'y', source=src_ov, size=5, color='black',
                alpha=0.8, marker='circle', legend_label='Overall vrad')
    fig.add_layout(Whisker(
        source=src_ov, base='x', upper='upper', lower='lower',
        line_color='black', line_alpha=0.4,
    ))
    # -------------------------------------------------------------------------
    # initial zoom around overall vrad (outlier rejection)
    pp = np.nanpercentile(vrad, [5, 95])
    diff = float(pp[1] - pp[0])
    if diff < 1.0:
        diff = max(abs(float(np.nanmean(vrad))) * 0.01, 10.0)
    central = float(np.nanmean(pp))
    fig.y_range.start = central - 2.0 * diff
    fig.y_range.end = central + 2.0 * diff
    # -------------------------------------------------------------------------
    # Move legend below the figure
    legend = fig.legend[0]
    legend.click_policy = 'hide'
    legend.orientation = 'horizontal'
    legend.label_text_font_size = '9pt'
    legend.spacing = 2
    legend.padding = 4
    fig.add_layout(legend, 'below')
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    return fig


def _build_lbl_layout(
    tbl: Any,
    flavor_id: str,
    preset: Dict[str, Any],
) -> Optional[Any]:
    """
    Build a 3-panel LBL column layout from an astropy RDB Table.

    :param tbl: astropy.table.Table, loaded LBL RDB table
    :param flavor_id: str, flavor identifier string
    :param preset: dict, instrument profile preset

    :return: Bokeh column layout or None on empty / invalid data
    :rtype: bokeh.layouts.column | None
    """
    from bokeh.layouts import column as bk_column

    rjd = np.array([float(v) for v in tbl['rjd']])
    vrad = np.array([float(v) for v in tbl['vrad']])
    svrad = np.array([float(v) for v in tbl['svrad']])
    reset_mask = np.array([bool(int(v)) for v in tbl['RESET_RV']])

    snr_h_label = sci_header_label(preset, 'lbl', 'EXT_H', 'EXTSN035')
    snr_key = 'EXTSN035'
    try:
        snr_h = np.array([float(v) for v in tbl[snr_key]])
    except (KeyError, Exception):
        snr_h = np.zeros(len(rjd))
    # -------------------------------------------------------------------------
    # convert MJD to UTC datetimes
    datetimes = np.array([mjd_to_datetime(rjd_i) for rjd_i in rjd])
    valid = np.array([dt is not None for dt in datetimes])
    if not np.any(valid):
        return None

    dts_valid = datetimes[valid]
    sort_idx = np.argsort([dt.timestamp() for dt in dts_valid])
    dts_s = dts_valid[sort_idx]
    vrad_s = vrad[valid][sort_idx]
    svrad_s = svrad[valid][sort_idx]
    reset_s = reset_mask[valid][sort_idx]
    snr_s = snr_h[valid][sort_idx]
    # -------------------------------------------------------------------------
    # compute ylim
    pp = np.nanpercentile(vrad_s, [10, 90])
    diff = float(pp[1] - pp[0])
    central = float(np.nanmean(pp))
    if diff < 1.0:
        diff = max(abs(central) * 0.01, 10.0)
    ylim: List[float] = [
        central - 1.5 * diff, central + 1.5 * diff
    ]
    bad_idxs = [
        int(i) for i in np.where(
            (vrad_s < ylim[0]) | (vrad_s > ylim[1])
        )[0]
    ]
    # -------------------------------------------------------------------------
    # wave-binned columns
    wave_vrad_cols = sorted([
        c for c in tbl.colnames
        if c.startswith('vrad_') and 'nm' in c
    ])
    wave_svrad_cols = sorted([
        c for c in tbl.colnames
        if c.startswith('svrad_') and 'nm' in c
    ])
    wave_vrad_dict: Dict[str, np.ndarray] = {}
    wave_svrad_dict: Dict[str, np.ndarray] = {}
    wavemap: List[float] = []
    for col in wave_vrad_cols:
        m = re.match(r'vrad_(\d+)nm', col)
        if m:
            wavemap.append(float(m.group(1)))
            wave_vrad_dict[col] = np.array(
                [float(v) for v in tbl[col]], dtype=float
            )[valid][sort_idx]
    for col in wave_svrad_cols:
        wave_svrad_dict[col] = np.array(
            [float(v) for v in tbl[col]], dtype=float
        )[valid][sort_idx]
    # -------------------------------------------------------------------------
    fig_rv = _make_lbl_rv_figure(
        dts_s, vrad_s, svrad_s, reset_s, ylim, flavor_id
    )
    fig_snr = _make_lbl_snr_figure(
        dts_s, snr_s, reset_s, bad_idxs, snr_h_label
    )
    fig_wave = _make_lbl_wave_figure(
        dts_s, vrad_s, svrad_s, wave_vrad_dict, wave_svrad_dict,
        wavemap, flavor_id=flavor_id, height=420,
    )
    return bk_column([fig_rv, fig_snr, fig_wave],
                     sizing_mode='stretch_width')


# =============================================================================
# Define public LBL plot builders
# =============================================================================
def build_lbl_plots_json(
    ftable_lbl_rdb_rows: List[Dict[str, Any]],
    path_lbl: str,
    preset: Dict[str, Any],
    target_id_prefix: str = 'op-lbl-vel-plot',
) -> Dict[str, Dict[str, Any]]:
    """
    Build LBL plots for each RDB file as ``json_item`` dicts.

    :param ftable_lbl_rdb_rows: list of ftable lbl_rdb row dicts
    :param path_lbl: str, base LBL directory path
    :param preset: dict, instrument profile preset
    :param target_id_prefix: str, DOM ID prefix for Bokeh embedding

    :return: dict keyed by rdb_filename with per-file plot payloads
    :rtype: dict
    """
    results: Dict[str, Dict[str, Any]] = {}
    for row in ftable_lbl_rdb_rows:
        filename = str(row.get('FILENAME', '') or '').strip()
        if not filename:
            continue
        flavor_id, tbl = _load_lbl_table(row, path_lbl)
        if tbl is None:
            results[filename] = {
                'has_plot': False,
                'message': f'Could not load {filename}',
            }
            continue
        target_id = f'{target_id_prefix}-{flavor_id}'
        try:
            layout = _build_lbl_layout(tbl, flavor_id, preset)
            if layout is None:
                results[filename] = {
                    'has_plot': False,
                    'message': 'No valid date rows in RDB file.',
                }
                continue
            script, div = plot_to_components(layout)
            results[filename] = {
                'has_plot': True,
                'script': script,
                'div': div,
                'message': '',
            }
        except Exception as exc:
            results[filename] = {
                'has_plot': False,
                'message': f'Plot error: {exc}',
            }
    return results


def build_lbl_plot_components(
    ftable_lbl_rdb_rows: List[Dict[str, Any]],
    path_lbl: str,
    preset: Dict[str, Any],
    lbl_filename: str,
) -> Dict[str, Any]:
    """
    Build a single LBL plot as ``(script, div)`` for server-side
    embedding.

    :param ftable_lbl_rdb_rows: list of ftable lbl_rdb row dicts
    :param path_lbl: str, base LBL directory path
    :param preset: dict, instrument profile preset
    :param lbl_filename: str, RDB filename to render

    :return: dict with has_plot, script, div, message
    :rtype: dict
    """
    for row in ftable_lbl_rdb_rows:
        filename = str(row.get('FILENAME', '') or '').strip()
        if filename != lbl_filename:
            continue
        flavor_id, tbl = _load_lbl_table(row, path_lbl)
        if tbl is None:
            return {
                'has_plot': False, 'script': '', 'div': '',
                'message': f'Could not load {lbl_filename}',
            }
        layout = _build_lbl_layout(tbl, flavor_id, preset)
        if layout is None:
            return {
                'has_plot': False, 'script': '', 'div': '',
                'message': 'No valid date rows in RDB file.',
            }
        script, div = plot_to_components(layout)
        return {
            'has_plot': True, 'script': script, 'div': div,
            'message': '',
        }
    return {
        'has_plot': False, 'script': '', 'div': '',
        'message': (
            f'RDB file {lbl_filename} not found in ftable rows.'
        ),
    }


# =============================================================================
# Define private per-night aggregation helper
# =============================================================================
def _aggregate_by_obs_dir(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    keys: List[str],
) -> List[Tuple[str, Dict[str, float]]]:
    """
    Aggregate htable column means by obs_dir, using the
    IDENTIFIER → OBS_DIR mapping from ftable_ext_rows.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param keys: list of str, htable column names to average

    :return: list of (obs_dir, {key: mean}) sorted by obs_dir
    :rtype: list[tuple[str, dict]]
    """
    id_to_obs: Dict[str, str] = {}
    for row in ftable_ext_rows:
        ident = str(row.get('IDENTIFIER', '') or '').strip()
        obs = str(row.get('OBS_DIR', '') or '').strip()
        if ident and obs:
            id_to_obs[ident] = obs
    # -------------------------------------------------------------------------
    obs_buckets: Dict[str, Dict[str, List[float]]] = {}
    for row in htable_rows:
        ident = str(row.get('IDENTIFIER', '') or '').strip()
        obs = id_to_obs.get(ident)
        if not obs:
            continue
        if obs not in obs_buckets:
            obs_buckets[obs] = {k: [] for k in keys}
        for key in keys:
            val = row.get(key)
            if val is not None:
                try:
                    obs_buckets[obs][key].append(float(val))
                except (TypeError, ValueError):
                    pass
    # -------------------------------------------------------------------------
    result: List[Tuple[str, Dict[str, float]]] = []
    for obs in sorted(obs_buckets.keys()):
        means: Dict[str, float] = {}
        for key in keys:
            vals = obs_buckets[obs][key]
            means[key] = (
                float(np.nanmean(vals)) if vals else float('nan')
            )
        result.append((obs, means))
    return result


def _make_ts_snr_figure(
    obs_data: List[Tuple[str, Dict[str, float]]],
    label_h: str,
    label_y: str,
    height: int = 300,
) -> Optional[Any]:
    """
    Build a per-night SNR scatter figure with obs_dir on the x-axis.

    :param obs_data: list of (obs_dir, {EXT_H: float, EXT_Y: float})
    :param label_h: str, H-band SNR legend label
    :param label_y: str, Y-band SNR legend label
    :param height: int, figure height in pixels

    :return: Bokeh figure or None if obs_data is empty
    :rtype: bokeh.plotting.figure | None
    """
    from bokeh.models import DatetimeTickFormatter, DatetimeTicker, FactorRange
    from bokeh.plotting import figure as bk_figure

    if not obs_data:
        return None
    obs_dirs = [d[0] for d in obs_data]
    snr_h = [d[1].get('EXT_H', float('nan')) for d in obs_data]
    snr_y = [d[1].get('EXT_Y', float('nan')) for d in obs_data]

    def _obs_dir_to_dt(obs_dir: str) -> Optional[datetime]:
        text = str(obs_dir or '').strip()
        m = re.match(r'^(\d{4})[-_]?([01]\d)[-_]?([0-3]\d)$', text)
        if not m:
            return None
        try:
            return datetime(
                int(m.group(1)), int(m.group(2)), int(m.group(3)),
                tzinfo=timezone.utc,
            )
        except ValueError:
            return None

    dts = [_obs_dir_to_dt(obs) for obs in obs_dirs]
    has_all_dates = all(dt is not None for dt in dts)
    use_time_axis = has_all_dates and len(obs_dirs) >= 2
    # -------------------------------------------------------------------------
    if use_time_axis:
        x_ms = [int(dt.timestamp() * 1000.0) for dt in dts if dt is not None]
        fig = bk_figure(
            x_axis_type='datetime',
            title='SNR per Night',
            x_axis_label='Date (UTC)',
            y_axis_label='SNR',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            active_scroll='wheel_zoom',
            height=height,
            sizing_mode='stretch_width',
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[('Obs Dir', '@obs'), ('Date', '@x{%F}'),
                      ('SNR', '@y{0.0}')],
            formatters={'@x': 'datetime'},
            mode='mouse',
        )
        fig.add_tools(hover)
        src_h = ColumnDataSource({'x': x_ms, 'y': snr_h, 'obs': obs_dirs})
        src_y = ColumnDataSource({'x': x_ms, 'y': snr_y, 'obs': obs_dirs})

        first_dt = min(dt for dt in dts if dt is not None)
        last_dt = max(dt for dt in dts if dt is not None)
        span_days = max((last_dt - first_dt).days, 0)

        fig.xaxis.ticker = DatetimeTicker(desired_num_ticks=10)
        if span_days >= 365 * 2:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years='%Y', months='%Y', days='%Y',
            )
        elif span_days >= 90:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years='%Y', months='%Y-%m', days='%Y-%m',
            )
        else:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years='%Y', months='%Y-%m', days='%Y-%m-%d',
            )
        fig.xaxis.major_label_orientation = 0.785
    else:
        fig = bk_figure(
            x_range=FactorRange(*obs_dirs),
            title='SNR per Night',
            x_axis_label='Obs Dir',
            y_axis_label='SNR',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            active_scroll='wheel_zoom',
            height=height,
            sizing_mode='stretch_width',
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[('Obs Dir', '@x'), ('SNR', '@y{0.0}')],
            mode='mouse',
        )
        fig.add_tools(hover)
        src_h = ColumnDataSource({'x': obs_dirs, 'y': snr_h})
        src_y = ColumnDataSource({'x': obs_dirs, 'y': snr_y})
        fig.xaxis.major_label_orientation = 'vertical'

    fig.scatter('x', 'y', source=src_h, size=8, color='#e6820a',
                marker='circle', alpha=0.85, legend_label=label_h)
    fig.scatter('x', 'y', source=src_y, size=8, color='#7e22ce',
                marker='circle', alpha=0.85, legend_label=label_y)
    # -------------------------------------------------------------------------
    fig.xgrid.grid_line_color = None
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    return fig


def _make_ts_airmass_figure(
    obs_data: List[Tuple[str, Dict[str, float]]],
    height: int = 260,
) -> Optional[Any]:
    """
    Build a per-night airmass scatter figure with obs_dir on the
    x-axis.  Only observations with airmass in [0, 2] are shown.

    :param obs_data: list of (obs_dir, {EXT_AIRMASS: float})
    :param height: int, figure height in pixels

    :return: Bokeh figure or None if no valid airmass data
    :rtype: bokeh.plotting.figure | None
    """
    from bokeh.models import (DatetimeTickFormatter, DatetimeTicker,
                              FactorRange, Range1d)
    from bokeh.plotting import figure as bk_figure

    obs_dirs: List[str] = []
    airmass: List[float] = []

    def _obs_dir_to_dt(obs_dir: str) -> Optional[datetime]:
        text = str(obs_dir or '').strip()
        m = re.match(r'^(\d{4})[-_]?([01]\d)[-_]?([0-3]\d)$', text)
        if not m:
            return None
        try:
            return datetime(
                int(m.group(1)), int(m.group(2)), int(m.group(3)),
                tzinfo=timezone.utc,
            )
        except ValueError:
            return None

    for obs_dir, means in obs_data:
        am = means.get('EXT_AIRMASS', float('nan'))
        if 0.0 <= am <= 2.0:
            obs_dirs.append(obs_dir)
            airmass.append(am)
    if not obs_dirs:
        return None

    dts = [_obs_dir_to_dt(obs) for obs in obs_dirs]
    has_all_dates = all(dt is not None for dt in dts)
    use_time_axis = has_all_dates and len(obs_dirs) >= 2
    # -------------------------------------------------------------------------
    if use_time_axis:
        x_ms = [int(dt.timestamp() * 1000.0) for dt in dts if dt is not None]
        fig = bk_figure(
            x_axis_type='datetime',
            y_range=Range1d(0.0, 2.0),
            title='Airmass per Night',
            x_axis_label='Date (UTC)',
            y_axis_label='Airmass',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            active_scroll='wheel_zoom',
            height=height,
            sizing_mode='stretch_width',
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[('Obs Dir', '@obs'), ('Date', '@x{%F}'),
                      ('Airmass', '@y{0.000}')],
            formatters={'@x': 'datetime'},
            mode='mouse',
        )
        fig.add_tools(hover)
        src = ColumnDataSource({'x': x_ms, 'y': airmass, 'obs': obs_dirs})
        first_dt = min(dt for dt in dts if dt is not None)
        last_dt = max(dt for dt in dts if dt is not None)
        span_days = max((last_dt - first_dt).days, 0)

        fig.xaxis.ticker = DatetimeTicker(desired_num_ticks=10)
        if span_days >= 365 * 2:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years='%Y', months='%Y', days='%Y',
            )
        elif span_days >= 90:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years='%Y', months='%Y-%m', days='%Y-%m',
            )
        else:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years='%Y', months='%Y-%m', days='%Y-%m-%d',
            )
        fig.xaxis.major_label_orientation = 0.785
    else:
        fig = bk_figure(
            x_range=FactorRange(*obs_dirs),
            y_range=Range1d(0.0, 2.0),
            title='Airmass per Night',
            x_axis_label='Obs Dir',
            y_axis_label='Airmass',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            active_scroll='wheel_zoom',
            height=height,
            sizing_mode='stretch_width',
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[('Obs Dir', '@x'), ('Airmass', '@y{0.000}')],
            mode='mouse',
        )
        fig.add_tools(hover)
        src = ColumnDataSource({'x': obs_dirs, 'y': airmass})
        fig.xaxis.major_label_orientation = 'vertical'

    fig.scatter('x', 'y', source=src, size=8, color='steelblue',
                marker='circle', alpha=0.85, legend_label='Mean airmass')
    # -------------------------------------------------------------------------
    fig.xgrid.grid_line_color = None
    fig.grid.grid_line_color = 'lightgray'
    fig.grid.grid_line_dash = 'dashed'
    fig.legend.location = 'top_right'
    return fig


# =============================================================================
# Define public per-night time series plot builders
# =============================================================================
def build_ts_snr_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
    target_id: str = 'op-ts-snr-plot-div',
) -> Dict[str, Any]:
    """
    Build the per-night SNR plot as a ``json_item`` dict.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param preset: dict, instrument profile preset
    :param target_id: str, DOM element ID for Bokeh embedding

    :return: dict with has_plot, item/message
    :rtype: dict
    """
    label_h = sci_header_label(preset, 'ext', 'EXT_H', 'H-band SNR')
    label_y = sci_header_label(preset, 'ext', 'EXT_Y', 'Y-band SNR')
    obs_data = _aggregate_by_obs_dir(
        htable_rows, ftable_ext_rows, ['EXT_H', 'EXT_Y']
    )
    if not obs_data:
        return {'has_plot': False, 'message': 'No per-night SNR data.'}
    fig = _make_ts_snr_figure(obs_data, label_h, label_y)
    if fig is None:
        return {'has_plot': False, 'message': 'No per-night SNR data.'}
    script, div = plot_to_components(fig)
    return {
        'has_plot': True,
        'script': script,
        'div': div,
        'message': '',
    }


def build_ts_snr_plot_components(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the per-night SNR plot as ``(script, div)`` components for
    server-rendered standalone pages.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param preset: dict, instrument profile preset

    :return: dict with has_plot, script, div, message
    :rtype: dict
    """
    label_h = sci_header_label(preset, 'ext', 'EXT_H', 'H-band SNR')
    label_y = sci_header_label(preset, 'ext', 'EXT_Y', 'Y-band SNR')
    obs_data = _aggregate_by_obs_dir(
        htable_rows, ftable_ext_rows, ['EXT_H', 'EXT_Y']
    )
    if not obs_data:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': 'No per-night SNR data.',
        }
    fig = _make_ts_snr_figure(obs_data, label_h, label_y)
    if fig is None:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': 'No per-night SNR data.',
        }
    script, div = plot_to_components(fig)
    return {
        'has_plot': True, 'script': script, 'div': div, 'message': '',
    }


def build_ts_airmass_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
    target_id: str = 'op-ts-airmass-plot-div',
) -> Dict[str, Any]:
    """
    Build the per-night airmass plot as a ``json_item`` dict.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param preset: dict, instrument profile preset
    :param target_id: str, DOM element ID for Bokeh embedding

    :return: dict with has_plot, item/message
    :rtype: dict
    """
    obs_data = _aggregate_by_obs_dir(
        htable_rows, ftable_ext_rows, ['EXT_AIRMASS']
    )
    if not obs_data:
        return {
            'has_plot': False,
            'message': 'No per-night airmass data.',
        }
    fig = _make_ts_airmass_figure(obs_data)
    if fig is None:
        return {
            'has_plot': False,
            'message': 'No airmass values in range 0\u20132.',
        }
    script, div = plot_to_components(fig)
    return {
        'has_plot': True,
        'script': script,
        'div': div,
        'message': '',
    }


def build_ts_airmass_plot_components(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the per-night airmass plot as ``(script, div)`` components
    for server-rendered standalone pages.

    :param htable_rows: list of htable row dicts
    :param ftable_ext_rows: list of ftable ext row dicts
    :param preset: dict, instrument profile preset

    :return: dict with has_plot, script, div, message
    :rtype: dict
    """
    obs_data = _aggregate_by_obs_dir(
        htable_rows, ftable_ext_rows, ['EXT_AIRMASS']
    )
    if not obs_data:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': 'No per-night airmass data.',
        }
    fig = _make_ts_airmass_figure(obs_data)
    if fig is None:
        return {
            'has_plot': False, 'script': '', 'div': '',
            'message': 'No airmass values in range 0\u20132.',
        }
    script, div = plot_to_components(fig)
    return {
        'has_plot': True, 'script': script, 'div': div, 'message': '',
    }


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    # -------------------------------------------------------------------------
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
