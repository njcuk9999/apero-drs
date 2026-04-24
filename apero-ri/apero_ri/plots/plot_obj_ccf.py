#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – CCF plot builders (cross-correlation function).

Part of the object-page plot suite; see also:
    plot_obj_spectrum.py   – SNR, BERV and median-spectrum plots
    plot_obj_lbl.py        – LBL RV plots
    plot_obj_timeseries.py – per-night time-series plots
    plot_obj_ind.py        – individual file-browser plots

Public API
----------
build_ccf_plot_json           – 4-panel CCF plot (json_item)
build_ccf_plot_components     – 4-panel CCF plot (script/div)
build_ccf_rv_plot_json        – CCF RV vs time (json_item)
build_ccf_rv_plot_components  – CCF RV vs time (script/div)
build_ccf_profile_plot_json   – Median CCF profile (json_item)
build_ccf_profile_plot_components – Median CCF profile (script/div)

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

import threading
import time
import warnings
from collections import OrderedDict
from datetime import datetime, timezone
from os import path as op
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from apero_ri.base import base
from apero_ri.plots.plot_general import (
    make_time_figure,
    mjd_to_datetime,
    plot_to_components,
    resolve_file_path as _resolve_file_path,
    sci_header_label,
)
from apero_ri.plots.bokeh_theme import fg_glyph_color
from astropy.time import Time
from bokeh.models import (
    ColumnDataSource,
    CrosshairTool,
    HoverTool,
    Range1d,
    Span,
)

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.plots.plot_obj_ccf"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

_CCF_CACHE_MAX_ENTRIES = 512
_CCF_RV_MAX_POINTS = 2500
_CCF_FILE_CACHE: OrderedDict[str, Tuple[float, np.ndarray, np.ndarray]] = (
    OrderedDict()
)
_CCF_FILE_CACHE_LOCK = threading.Lock()

# Stash the most recent failed _load_ccf_data summary so callers
# (which only see a None return on failure) can surface diagnostic
# counters in the user-facing error message. Updated on every
# failed call; not request-scoped — best-effort diagnostics only.
_LAST_CCF_FAILURE_SUMMARY: Optional[Dict[str, Any]] = None


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
            t = hdul["RV_TABLE"]
            rv_vec = np.array(t.data["RV"], dtype=float)
            ccf_row = np.array(t.data["CCF_STACK"], dtype=float)
    except Exception:
        return None

    with _CCF_FILE_CACHE_LOCK:
        _CCF_FILE_CACHE[path] = (mtime, rv_vec, ccf_row)
        _CCF_FILE_CACHE.move_to_end(path)
        while len(_CCF_FILE_CACHE) > _CCF_CACHE_MAX_ENTRIES:
            _CCF_FILE_CACHE.popitem(last=False)
    return rv_vec, ccf_row


def _gauss_fn(x: Any, amp: float, pos: float, sig: float, dc: float) -> Any:
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
) -> Optional[
    Tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        Dict[str, Any],
    ]
]:
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
        raw = row.get("MID_OBS_TIME")
        if raw is None:
            return None
        sval = str(raw).strip()
        if not sval:
            return None
        try:
            return float(Time(sval, format="isot", scale="utc").mjd)
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
        sampling_mode = "equally_spaced"
    else:
        selected_rows = in_range_rows
        sampling_mode = "all"

    summary: Dict[str, Any] = {
        "max_files": int(max_files),
        "total_rows": int(total_rows),
        "rows_with_mid_obs_time": int(len(timed_rows)),
        "in_range_total": int(in_range_total),
        "selected_total": int(len(selected_rows)),
        "loaded_total": 0,
        "sampling_mode": sampling_mode,
        "ccf_mjd_start": ccf_mjd_start,
        "ccf_mjd_end": ccf_mjd_end,
        "available_mjd_min": available_mjd_min,
        "available_mjd_max": available_mjd_max,
        "selected_mjd_min": (selected_rows[0][0] if selected_rows else None),
        "selected_mjd_max": (selected_rows[-1][0] if selected_rows else None),
    }

    ht_by_id: Dict[str, Dict[str, Any]] = {}
    for row in htable_rows:
        ident = str(row.get("IDENTIFIER", "") or "").strip()
        if ident:
            ht_by_id[ident] = row

    rv_vec: Optional[np.ndarray] = None
    all_ccf_rows: List[np.ndarray] = []
    datetimes_list: List[Any] = []
    dv_ms_list: List[float] = []
    sdv_ms_list: List[float] = []

    # Per-failure-mode counters surfaced in summary so the front-end
    # can diagnose "No CCF profile data could be loaded" without
    # needing server-side log access.
    fail_counts = {
        "no_path": 0,
        "no_htable_dv": 0,
        "no_datetime": 0,
        "fits_read_failed": 0,
        "exception": 0,
    }
    last_failure_path: Optional[str] = None
    last_failure_reason: Optional[str] = None

    for mjd_val, row in selected_rows:
        path = _resolve_file_path(row, paths)
        if path is None:
            fail_counts["no_path"] += 1
            last_failure_reason = (
                "no file path could be resolved for row")
            continue
        ident = str(row.get("IDENTIFIER", "") or "").strip()
        ht_row = ht_by_id.get(ident, {})
        raw_dv = ht_row.get("CCF_DV")
        raw_sdv = ht_row.get("CCF_SDV")
        if raw_dv is None or raw_sdv is None:
            fail_counts["no_htable_dv"] += 1
            last_failure_path = str(path)
            last_failure_reason = (
                "missing CCF_DV / CCF_SDV in htable")
            continue
        try:
            dv_ms_val = float(raw_dv) * 1000.0  # km/s → m/s
            sdv_ms_val = float(raw_sdv)  # already m/s
            dt = mjd_to_datetime(float(mjd_val))
            if dt is None:
                fail_counts["no_datetime"] += 1
                last_failure_path = str(path)
                last_failure_reason = "mjd_to_datetime returned None"
                continue
            read_out = _read_ccf_row_cached(str(path))
            if read_out is None:
                fail_counts["fits_read_failed"] += 1
                last_failure_path = str(path)
                last_failure_reason = (
                    "_read_ccf_row_cached returned None")
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
        except Exception as _ccf_exc:  # noqa: BLE001
            fail_counts["exception"] += 1
            last_failure_path = str(path)
            last_failure_reason = (
                "exception while loading: "
                + type(_ccf_exc).__name__ + ': '
                + str(_ccf_exc)[:160])
            continue

    summary["loaded_total"] = int(len(all_ccf_rows))
    summary["fail_counts"] = fail_counts
    summary["last_failure_path"] = last_failure_path
    summary["last_failure_reason"] = last_failure_reason

    if rv_vec is None or len(all_ccf_rows) == 0:
        # Stash the summary so the caller (which only gets None back)
        # can still surface the diagnostic counters in its error
        # response. Indexed by id() of the input list to avoid
        # cross-talk between concurrent requests for different
        # objects (good-enough; not 100% race-proof).
        global _LAST_CCF_FAILURE_SUMMARY
        _LAST_CCF_FAILURE_SUMMARY = summary
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
    finite_rv = np.isfinite(rv_vec)
    if np.any(finite_rv):
        default_xlim = [
            float(np.nanmin(rv_vec[finite_rv])),
            float(np.nanmax(rv_vec[finite_rv])),
        ]
    else:
        default_xlim = [-1.0, 1.0]

    try:
        from scipy.optimize import curve_fit
    except ImportError:
        return False, np.full(len(rv_vec), np.nan), default_xlim

    finite = np.isfinite(rv_vec) & np.isfinite(med_ccf)
    if np.count_nonzero(finite) < 7:
        return False, np.full(len(rv_vec), np.nan), default_xlim

    x_fit = np.array(rv_vec[finite], dtype=float)
    y_fit = np.array(med_ccf[finite], dtype=float)
    order = np.argsort(x_fit)
    x_fit = x_fit[order]
    y_fit = y_fit[order]

    idx_min = int(np.argmin(y_fit))
    pos0 = float(x_fit[idx_min])
    dc0 = float(np.nanpercentile(y_fit, 90.0))
    depth0 = max(dc0 - float(y_fit[idx_min]), 1e-4)
    amp0 = -depth0

    x_span = float(x_fit[-1] - x_fit[0])
    sig0 = max(x_span / 25.0, 0.5)
    half_win = max(8.0 * sig0, 5.0)
    win = (x_fit >= pos0 - half_win) & (x_fit <= pos0 + half_win)
    if np.count_nonzero(win) >= 7:
        x_use = x_fit[win]
        y_use = y_fit[win]
    else:
        x_use = x_fit
        y_use = y_fit

    x_lo = float(x_use[0])
    x_hi = float(x_use[-1])
    y_lo = float(np.nanmin(y_use))
    y_hi = float(np.nanmax(y_use))
    y_span = max(y_hi - y_lo, 1e-4)
    amp_bound = max(5.0 * depth0, y_span)
    sig_low = max((x_hi - x_lo) / 1000.0, 1e-3)
    sig_high = max((x_hi - x_lo), sig_low * 10.0)
    bounds = (
        [-amp_bound, x_lo, sig_low, y_lo - 0.25 * y_span],
        [-1e-9, x_hi, sig_high, y_hi + 0.25 * y_span],
    )
    guess = [amp0, pos0, sig0, dc0]

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            coeffs, _ = curve_fit(
                _gauss_fn,
                x_use,
                y_use,
                p0=guess,
                bounds=bounds,
                maxfev=20000,
            )
        fit = _gauss_fn(rv_vec, *coeffs)
        sig = max(abs(float(coeffs[2])), sig_low)
        c0 = float(coeffs[1])
        xlim = [
            max(default_xlim[0], c0 - 20.0 * sig),
            min(default_xlim[1], c0 + 20.0 * sig),
        ]
        if xlim[1] <= xlim[0]:
            xlim = default_xlim
        return True, fit, xlim
    except Exception:
        return False, np.full(len(rv_vec), np.nan), default_xlim


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

    fig = make_time_figure("CCF Radial Velocity vs Time", height=height)
    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Date (UTC)", "@x{%F %T}"),
                ("RV", "@y{0.000} m/s"),
            ],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
    )
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
        src = ColumnDataSource(
            dict(
                x=dts_ms[good],
                y=dv_ms[good],
                upper=dv_ms[good] + sdv_ms[good],
                lower=dv_ms[good] - sdv_ms[good],
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src,
            marker='circle',
            size=6,
            color="green",
            alpha=0.7,
            legend_label="Good",
        )
        whisk = Whisker(
            source=src,
            base="x",
            upper="upper",
            lower="lower",
            line_color="green",
            line_alpha=0.7,
        )
        whisk.upper_head.line_color = "green"
        whisk.lower_head.line_color = "green"
        whisk.upper_head.line_alpha = 0.7
        whisk.lower_head.line_alpha = 0.7
        fig.add_layout(whisk)
    # -------------------------------------------------------------------------
    l_arrow = 0.04 * diff
    for clip_mask, yt, marker in [
        (dv_ms < ylim_lo, ylim_lo + l_arrow, "triangle"),
        (dv_ms > ylim_hi, ylim_hi - l_arrow, "inverted_triangle"),
    ]:
        if np.any(clip_mask):
            src_out = ColumnDataSource(
                dict(
                    x=dts_ms[clip_mask],
                    y=np.full(int(np.sum(clip_mask)), yt),
                )
            )
            fig.scatter(
                "x",
                "y",
                source=src_out,
                marker=marker,
                size=8,
                color="red",
                alpha=0.8,
                legend_label="Outlier",
            )
    # -------------------------------------------------------------------------
    fig.y_range.start = ylim_lo
    fig.y_range.end = ylim_hi
    fig.yaxis.axis_label = "RV [m/s]"
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
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
    if np.count_nonzero(limmask) < 3:
        limmask = np.isfinite(rv_vec)
    rv_m = rv_vec[limmask]

    fig = bk_figure(
        title="Median CCF Profile",
        x_axis_label="RV [km/s]",
        y_axis_label="Normalized CCF",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=height,
        sizing_mode="stretch_width",
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.add_tools(
        HoverTool(
            tooltips=[("RV", "$x{0.000} km/s"), ("CCF", "$y{0.000000}")],
            mode="mouse",
        )
    )
    fig.add_tools(CrosshairTool(dimensions="both"))
    # -------------------------------------------------------------------------
    src_2 = ColumnDataSource(
        dict(
            x=rv_m,
            upper=y2_2sig[limmask],
            lower=y1_2sig[limmask],
        )
    )
    fig.add_layout(
        Band(
            base="x",
            upper="upper",
            lower="lower",
            source=src_2,
            fill_color="orange",
            fill_alpha=0.4,
            line_color=None,
        )
    )
    src_1 = ColumnDataSource(
        dict(
            x=rv_m,
            upper=y2_1sig[limmask],
            lower=y1_1sig[limmask],
        )
    )
    fig.add_layout(
        Band(
            base="x",
            upper="upper",
            lower="lower",
            source=src_1,
            fill_color="red",
            fill_alpha=0.4,
            line_color=None,
        )
    )
    # legend proxy quads for bands (on hidden extra ranges so auto-range
    # unaffected)
    fig.extra_x_ranges["_proxy"] = Range1d(start=0, end=1)
    fig.extra_y_ranges["_proxy"] = Range1d(start=0, end=1)
    fig.quad(
        left=[5],
        right=[6],
        top=[6],
        bottom=[5],
        fill_color="orange",
        fill_alpha=0.4,
        line_color=None,
        legend_label="2σ band",
        x_range_name="_proxy",
        y_range_name="_proxy",
    )
    fig.quad(
        left=[5],
        right=[6],
        top=[6],
        bottom=[5],
        fill_color="red",
        fill_alpha=0.4,
        line_color=None,
        legend_label="1σ band",
        x_range_name="_proxy",
        y_range_name="_proxy",
    )
    fig.line(
        rv_m,
        med_ccf[limmask],
        line_color=fg_glyph_color(),
        line_width=1.5,
        legend_label="Median CCF",
    )
    if has_fit:
        fig.line(
            rv_m,
            fit[limmask],
            line_color="dodgerblue",
            line_width=2.0,
            line_dash="dashed",
            legend_label="Gaussian fit",
        )
    # initial zoom to 2σ envelope with 10% padding
    y_lo = float(np.nanmin(y1_2sig[limmask]))
    y_hi = float(np.nanmax(y2_2sig[limmask]))
    y_pad = 0.1 * (y_hi - y_lo) if y_hi > y_lo else 0.01
    fig.y_range = Range1d(start=y_lo - y_pad, end=y_hi + y_pad)
    x_pad = 0.02 * (float(rv_m[-1]) - float(rv_m[0])) if len(rv_m) > 1 else 1.0
    fig.x_range = Range1d(
        start=float(rv_m[0]) - x_pad, end=float(rv_m[-1]) + x_pad
    )
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
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
        title="CCF Residuals (CCF \u2212 fit)",
        x_axis_label="RV [km/s]",
        y_axis_label="Residuals",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=height,
        sizing_mode="stretch_width",
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.add_tools(
        HoverTool(
            tooltips=[("RV", "$x{0.000} km/s"), ("Residual", "$y{0.000000}")],
            mode="mouse",
        )
    )
    fig.add_tools(CrosshairTool(dimensions="both"))
    # -------------------------------------------------------------------------
    if has_fit:
        f_m = fit[limmask]
        residual_label = 'Median residual'
    else:
        f_m = med_ccf[limmask]
        residual_label = 'Residual vs median CCF'
        from bokeh.models import Label as _BkLabel

        fig.add_layout(
            _BkLabel(
                x=20,
                y=20,
                x_units='screen',
                y_units='screen',
                text='Gaussian fit unavailable: showing residuals vs median',
                text_font_size='10pt',
                text_color='gray',
            )
        )

    src_2 = ColumnDataSource(
        dict(
            x=rv_m,
            upper=y2_2sig[limmask] - f_m,
            lower=y1_2sig[limmask] - f_m,
        )
    )
    src_1 = ColumnDataSource(
        dict(
            x=rv_m,
            upper=y2_1sig[limmask] - f_m,
            lower=y1_1sig[limmask] - f_m,
        )
    )
    fig.add_layout(
        Band(
            base='x',
            upper='upper',
            lower='lower',
            source=src_2,
            fill_color='orange',
            fill_alpha=0.4,
        )
    )
    fig.add_layout(
        Band(
            base='x',
            upper='upper',
            lower='lower',
            source=src_1,
            fill_color='red',
            fill_alpha=0.4,
        )
    )
    # legend proxy quads for bands (on hidden extra ranges)
    fig.extra_x_ranges['_proxy'] = Range1d(start=0, end=1)
    fig.extra_y_ranges['_proxy'] = Range1d(start=0, end=1)
    fig.quad(
        left=[5],
        right=[6],
        top=[6],
        bottom=[5],
        fill_color='orange',
        fill_alpha=0.4,
        line_color=None,
        legend_label='2σ band',
        x_range_name='_proxy',
        y_range_name='_proxy',
    )
    fig.quad(
        left=[5],
        right=[6],
        top=[6],
        bottom=[5],
        fill_color='red',
        fill_alpha=0.4,
        line_color=None,
        legend_label='1σ band',
        x_range_name='_proxy',
        y_range_name='_proxy',
    )
    fig.line(
        rv_m,
        med_ccf[limmask] - f_m,
        line_color=fg_glyph_color(),
        line_width=1.2,
        legend_label=residual_label,
    )
    # initial zoom to 2σ residual envelope with 10% padding
    with np.errstate(all='ignore'):
        res_lo_a = np.nanmin(y1_2sig[limmask] - f_m)
        res_hi_a = np.nanmax(y2_2sig[limmask] - f_m)
    if (
        not np.isfinite(res_lo_a)
        or not np.isfinite(res_hi_a)
        or res_hi_a <= res_lo_a
    ):
        res_lo, res_hi = -1.0, 1.0
    else:
        res_lo, res_hi = float(res_lo_a), float(res_hi_a)
    res_pad = 0.1 * (res_hi - res_lo) if res_hi > res_lo else 0.01
    fig.y_range = Range1d(start=res_lo - res_pad, end=res_hi + res_pad)
    if len(rv_m) > 1 and np.isfinite(rv_m[0]) and np.isfinite(rv_m[-1]):
        x_pad = 0.02 * (float(rv_m[-1]) - float(rv_m[0]))
        fig.x_range = Range1d(
            start=float(rv_m[0]) - x_pad,
            end=float(rv_m[-1]) + x_pad,
        )
    else:
        fig.x_range = Range1d(start=float(xlim[0]), end=float(xlim[1]))
    fig.legend.location = 'top_right'
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
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
        title="CCF Spread (relative to median)",
        x_axis_label="RV [km/s]",
        y_axis_label="Spread",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=height,
        sizing_mode="stretch_width",
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.add_tools(
        HoverTool(
            tooltips=[("RV", "$x{0.000} km/s"), ("Spread", "$y{0.000000}")],
            mode="mouse",
        )
    )
    fig.add_tools(CrosshairTool(dimensions="both"))
    # -------------------------------------------------------------------------
    spread_2sig_upper = y2_2sig[limmask] - med_m
    spread_2sig_lower = y1_2sig[limmask] - med_m
    src_2 = ColumnDataSource(
        dict(
            x=rv_m,
            upper=spread_2sig_upper,
            lower=spread_2sig_lower,
        )
    )
    src_1 = ColumnDataSource(
        dict(
            x=rv_m,
            upper=y2_1sig[limmask] - med_m,
            lower=y1_1sig[limmask] - med_m,
        )
    )
    fig.add_layout(
        Band(
            base="x",
            upper="upper",
            lower="lower",
            source=src_2,
            fill_color="orange",
            fill_alpha=0.4,
            line_color=None,
        )
    )
    fig.add_layout(
        Band(
            base="x",
            upper="upper",
            lower="lower",
            source=src_1,
            fill_color="red",
            fill_alpha=0.4,
            line_color=None,
        )
    )
    # legend proxy quads for bands (on hidden extra ranges)
    fig.extra_x_ranges["_proxy"] = Range1d(start=0, end=1)
    fig.extra_y_ranges["_proxy"] = Range1d(start=0, end=1)
    fig.quad(
        left=[5],
        right=[6],
        top=[6],
        bottom=[5],
        fill_color="orange",
        fill_alpha=0.4,
        line_color=None,
        legend_label="2σ band",
        x_range_name="_proxy",
        y_range_name="_proxy",
    )
    fig.quad(
        left=[5],
        right=[6],
        top=[6],
        bottom=[5],
        fill_color="red",
        fill_alpha=0.4,
        line_color=None,
        legend_label="1σ band",
        x_range_name="_proxy",
        y_range_name="_proxy",
    )
    fig.line(
        rv_m,
        np.zeros(len(rv_m)),
        line_color=fg_glyph_color(),
        line_width=1.2,
        legend_label="Median (zero)",
    )
    # initial zoom to 2 sigma range
    y_max_2sig = float(
        np.nanmax(
            np.abs(np.concatenate([spread_2sig_upper, spread_2sig_lower]))
        )
    )
    if y_max_2sig > 0:
        fig.y_range.start = -1.1 * y_max_2sig
        fig.y_range.end = 1.1 * y_max_2sig
    x_pad = 0.02 * (float(rv_m[-1]) - float(rv_m[0])) if len(rv_m) > 1 else 1.0
    fig.x_range = Range1d(
        start=float(rv_m[0]) - x_pad, end=float(rv_m[-1]) + x_pad
    )
    fig.legend.location = "top_right"
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
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
        return (
            None,
            "No CCF data could be loaded.",
            {
                "max_files": int(max(1, ccf_nobs)),
                "sampling_mode": "all",
                "selected_total": 0,
                "loaded_total": 0,
                "in_range_total": 0,
                "ccf_mjd_start": ccf_mjd_start,
                "ccf_mjd_end": ccf_mjd_end,
                "timings_ms": {
                    "load_data": round(load_ms, 2),
                    "stats_fit": 0.0,
                    "build_figures": 0.0,
                    "total": round(load_ms, 2),
                },
            },
        )

    rv_vec, all_ccf, datetimes, dv_ms, sdv_ms, summary = result
    rv_used, ccf_used, rv_points_orig, rv_points_used = _decimate_ccf_grid(
        rv_vec, all_ccf, max_points=_CCF_RV_MAX_POINTS
    )
    summary["rv_points_original"] = int(rv_points_orig)
    summary["rv_points_used"] = int(rv_points_used)
    summary["rv_decimated"] = bool(rv_points_used < rv_points_orig)
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
        rv_used,
        med_ccf,
        y1_1sig,
        y2_1sig,
        y1_2sig,
        y2_2sig,
        fit,
        xlim,
        has_fit,
    )
    fig_res = _make_ccf_residuals_figure(
        rv_used,
        med_ccf,
        fit,
        y1_1sig,
        y2_1sig,
        y1_2sig,
        y2_2sig,
        xlim,
        has_fit,
    )
    fig_spread = _make_ccf_spread_figure(
        rv_used,
        med_ccf,
        y1_1sig,
        y2_1sig,
        y1_2sig,
        y2_2sig,
        xlim,
        has_fit,
    )
    fig_ms = (time.perf_counter() - t_fig0) * 1000.0

    smjd = summary.get("selected_mjd_min", None)
    emjd = summary.get("selected_mjd_max", None)
    try:
        sdate = (
            Time(float(smjd), format="mjd")
            .to_datetime(timezone=timezone.utc)
            .strftime("%Y-%m-%d")
        )
        edate = (
            Time(float(emjd), format="mjd")
            .to_datetime(timezone=timezone.utc)
            .strftime("%Y-%m-%d")
        )
    except Exception:
        sdate = "--"
        edate = "--"
    nobs = int(summary.get("selected_total", 0) or 0)
    suffix = f" [{sdate} to {edate} (Nobs={nobs})]"
    fig_rv.title.text = str(fig_rv.title.text) + suffix
    fig_prof.title.text = str(fig_prof.title.text) + suffix
    fig_res.title.text = str(fig_res.title.text) + suffix
    fig_spread.title.text = str(fig_spread.title.text) + suffix

    layout = bk_column(
        [fig_rv, fig_prof, fig_res, fig_spread], sizing_mode="stretch_width"
    )
    total_ms = load_ms + stats_ms + fig_ms
    summary["timings_ms"] = {
        "load_data": round(load_ms, 2),
        "stats_fit": round(stats_ms, 2),
        "build_figures": round(fig_ms, 2),
        "total": round(total_ms, 2),
    }
    return layout, "", summary


def _load_ccf_rv_from_htable(
    htable_rows: List[Dict[str, Any]],
) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]]:
    """
    Load CCF RV time-series directly from htable rows (no CCF FITS reads).

    :param htable_rows: list of htable row dicts

    :return: tuple (datetimes, dv_ms, sdv_ms, summary) or None
    :rtype: tuple | None
    """
    datetimes_list: List[Any] = []
    dv_ms_list: List[float] = []
    sdv_ms_list: List[float] = []
    total_rows = len(htable_rows)
    candidate_rows = 0

    for row in htable_rows:
        if not isinstance(row, dict):
            continue
        raw_dv = row.get("CCF_DV")
        raw_sdv = row.get("CCF_SDV")
        if raw_dv is None or raw_sdv is None:
            continue
        candidate_rows += 1
        try:
            dv_ms_val = float(raw_dv) * 1000.0
            sdv_ms_val = float(raw_sdv)
        except Exception:
            continue

        dt = None
        raw_mjd = row.get("CCF_MJDMID")
        if raw_mjd is not None:
            try:
                dt = mjd_to_datetime(float(raw_mjd))
            except Exception:
                dt = None
        if dt is None:
            raw_mid = row.get("MID_OBS_TIME")
            if raw_mid is not None:
                sval = str(raw_mid).strip()
                if sval:
                    try:
                        dt = Time(sval, format="isot", scale="utc").to_datetime(
                            timezone=timezone.utc
                        )
                    except Exception:
                        dt = None
        if dt is None:
            continue

        datetimes_list.append(dt)
        dv_ms_list.append(dv_ms_val)
        sdv_ms_list.append(sdv_ms_val)

    loaded_total = len(datetimes_list)
    summary: Dict[str, Any] = {
        "total_rows": int(total_rows),
        "candidate_rows": int(candidate_rows),
        "loaded_total": int(loaded_total),
    }
    if loaded_total == 0:
        return None

    datetimes = np.array(datetimes_list)
    dv_ms = np.array(dv_ms_list)
    sdv_ms = np.array(sdv_ms_list)
    sort_idx = np.argsort([dt.timestamp() for dt in datetimes])
    return datetimes[sort_idx], dv_ms[sort_idx], sdv_ms[sort_idx], summary


def _build_ccf_rv_layout(
    htable_rows: List[Dict[str, Any]],
) -> Tuple[Optional[Any], str, Dict[str, Any]]:
    """Build the fast CCF RV-vs-time layout from htable only."""
    t0 = time.perf_counter()
    out = _load_ccf_rv_from_htable(htable_rows)
    load_ms = (time.perf_counter() - t0) * 1000.0
    if out is None:
        return (
            None,
            "No CCF RV points available.",
            {
                "total_rows": int(len(htable_rows)),
                "candidate_rows": 0,
                "loaded_total": 0,
                "timings_ms": {
                    "load_data": round(load_ms, 2),
                    "build_figures": 0.0,
                    "total": round(load_ms, 2),
                },
            },
        )

    datetimes, dv_ms, sdv_ms, summary = out
    t1 = time.perf_counter()
    fig_rv = _make_ccf_rv_figure(datetimes, dv_ms, sdv_ms)
    from bokeh.layouts import column as bk_column

    layout = bk_column([fig_rv], sizing_mode="stretch_width")
    fig_ms = (time.perf_counter() - t1) * 1000.0
    total_ms = load_ms + fig_ms
    summary["timings_ms"] = {
        "load_data": round(load_ms, 2),
        "build_figures": round(fig_ms, 2),
        "total": round(total_ms, 2),
    }
    return layout, "", summary


def _build_ccf_profile_layout(
    htable_rows: List[Dict[str, Any]],
    ftable_ccf_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    ccf_mjd_start: Optional[float] = None,
    ccf_mjd_end: Optional[float] = None,
    ccf_nobs: int = 100,
) -> Tuple[Optional[Any], str, Dict[str, Any]]:
    """
    Build the heavy CCF profile/residual/spread layout (no RV panel).
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
        diag = _LAST_CCF_FAILURE_SUMMARY or {}
        fc = diag.get("fail_counts") or {}
        # Compose a user-actionable message
        bits = []
        if diag.get("total_rows", 0) == 0:
            bits.append("no CCF rows in ftable")
        elif diag.get("rows_with_mid_obs_time", 0) == 0:
            bits.append("no rows had a parseable MID_OBS_TIME")
        elif diag.get("in_range_total", 0) == 0:
            bits.append("no rows fall within the selected MJD range")
        elif fc.get("no_path", 0) > 0 and (
                fc.get("no_path", 0) == diag.get("selected_total", -1)):
            bits.append(
                "every CCF file path failed to resolve (check "
                "PATH_RED / PATH_OUT in the profile config)")
        elif fc.get("no_htable_dv", 0) > 0:
            bits.append(
                "all selected rows are missing CCF_DV/CCF_SDV in "
                "the htable")
        elif fc.get("fits_read_failed", 0) > 0:
            bits.append(
                str(fc.get("fits_read_failed"))
                + " CCF FITS file(s) failed to read")
        elif fc.get("exception", 0) > 0:
            bits.append(
                str(fc.get("exception")) + " row(s) raised an "
                "exception during load — last: "
                + str(diag.get("last_failure_reason") or "?"))
        msg = "No CCF profile data could be loaded."
        if bits:
            msg += " Reason: " + "; ".join(bits) + "."
        full_summary = {
            "max_files": int(max(1, ccf_nobs)),
            "sampling_mode": "all",
            "selected_total": 0,
            "loaded_total": 0,
            "in_range_total": 0,
            "ccf_mjd_start": ccf_mjd_start,
            "ccf_mjd_end": ccf_mjd_end,
            "timings_ms": {
                "load_data": round(load_ms, 2),
                "stats_fit": 0.0,
                "build_figures": 0.0,
                "total": round(load_ms, 2),
            },
        }
        # Attach the diagnostic counters for the front-end to inspect
        full_summary.update({
            "diagnostic": {
                "fail_counts": fc,
                "last_failure_path": diag.get("last_failure_path"),
                "last_failure_reason": diag.get("last_failure_reason"),
                "total_rows": diag.get("total_rows"),
                "rows_with_mid_obs_time": diag.get(
                    "rows_with_mid_obs_time"),
                "in_range_total": diag.get("in_range_total"),
                "selected_total": diag.get("selected_total"),
            },
        })
        return None, msg, full_summary

    rv_vec, all_ccf, _datetimes, _dv_ms, _sdv_ms, summary = result
    rv_used, ccf_used, rv_points_orig, rv_points_used = _decimate_ccf_grid(
        rv_vec, all_ccf, max_points=_CCF_RV_MAX_POINTS
    )
    summary["rv_points_original"] = int(rv_points_orig)
    summary["rv_points_used"] = int(rv_points_used)
    summary["rv_decimated"] = bool(rv_points_used < rv_points_orig)

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

    t_fig0 = time.perf_counter()
    fig_prof = _make_ccf_profile_figure(
        rv_used,
        med_ccf,
        y1_1sig,
        y2_1sig,
        y1_2sig,
        y2_2sig,
        fit,
        xlim,
        has_fit,
    )
    fig_res = _make_ccf_residuals_figure(
        rv_used,
        med_ccf,
        fit,
        y1_1sig,
        y2_1sig,
        y1_2sig,
        y2_2sig,
        xlim,
        has_fit,
    )
    fig_spread = _make_ccf_spread_figure(
        rv_used,
        med_ccf,
        y1_1sig,
        y2_1sig,
        y1_2sig,
        y2_2sig,
        xlim,
        has_fit,
    )
    fig_ms = (time.perf_counter() - t_fig0) * 1000.0

    smjd = summary.get("selected_mjd_min", None)
    emjd = summary.get("selected_mjd_max", None)
    try:
        sdate = (
            Time(float(smjd), format="mjd")
            .to_datetime(timezone=timezone.utc)
            .strftime("%Y-%m-%d")
        )
        edate = (
            Time(float(emjd), format="mjd")
            .to_datetime(timezone=timezone.utc)
            .strftime("%Y-%m-%d")
        )
    except Exception:
        sdate = "--"
        edate = "--"
    nobs = int(summary.get("selected_total", 0) or 0)
    suffix = f" [{sdate} to {edate} (Nobs={nobs})]"
    fig_prof.title.text = str(fig_prof.title.text) + suffix
    fig_res.title.text = str(fig_res.title.text) + suffix
    fig_spread.title.text = str(fig_spread.title.text) + suffix

    layout = bk_column(
        [fig_prof, fig_res, fig_spread], sizing_mode="stretch_width"
    )
    total_ms = load_ms + stats_ms + fig_ms
    summary["timings_ms"] = {
        "load_data": round(load_ms, 2),
        "stats_fit": round(stats_ms, 2),
        "build_figures": round(fig_ms, 2),
        "total": round(total_ms, 2),
    }
    return layout, "", summary


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
    target_id: str = "op-ccf-plot-div",
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
        return {"has_plot": False, "message": msg, "sample_info": summary}
    script, div = plot_to_components(layout)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
        "sample_info": summary,
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
            "has_plot": False,
            "script": "",
            "div": "",
            "message": msg,
            "sample_info": summary,
        }
    script, div = plot_to_components(layout)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
        "sample_info": summary,
    }


def build_ccf_rv_plot_json(
    htable_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
    target_id: str = "op-ccf-rv-plot-div",
) -> Dict[str, Any]:
    """Build fast CCF RV-vs-time plot JSON from htable only."""
    layout, msg, summary = _build_ccf_rv_layout(htable_rows)
    if layout is None:
        return {"has_plot": False, "message": msg, "sample_info": summary}
    script, div = plot_to_components(layout)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
        "sample_info": summary,
    }


def build_ccf_rv_plot_components(
    htable_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
) -> Dict[str, Any]:
    """Build fast CCF RV-vs-time plot as components from htable only."""
    layout, msg, summary = _build_ccf_rv_layout(htable_rows)
    if layout is None:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": msg,
            "sample_info": summary,
        }
    script, div = plot_to_components(layout)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
        "sample_info": summary,
    }


def build_ccf_profile_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ccf_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    ccf_mjd_start: Optional[float] = None,
    ccf_mjd_end: Optional[float] = None,
    ccf_nobs: int = 100,
    target_id: str = "op-ccf-profile-plot-div",
) -> Dict[str, Any]:
    """Build CCF median profile/residual/spread plot JSON."""
    layout, msg, summary = _build_ccf_profile_layout(
        htable_rows,
        ftable_ccf_rows,
        paths,
        ccf_mjd_start=ccf_mjd_start,
        ccf_mjd_end=ccf_mjd_end,
        ccf_nobs=ccf_nobs,
    )
    if layout is None:
        return {"has_plot": False, "message": msg, "sample_info": summary}
    script, div = plot_to_components(layout)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
        "sample_info": summary,
    }


def build_ccf_profile_plot_components(
    htable_rows: List[Dict[str, Any]],
    ftable_ccf_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    ccf_mjd_start: Optional[float] = None,
    ccf_mjd_end: Optional[float] = None,
    ccf_nobs: int = 100,
) -> Dict[str, Any]:
    """Build CCF median profile/residual/spread plot as components."""
    layout, msg, summary = _build_ccf_profile_layout(
        htable_rows,
        ftable_ccf_rows,
        paths,
        ccf_mjd_start=ccf_mjd_start,
        ccf_mjd_end=ccf_mjd_end,
        ccf_nobs=ccf_nobs,
    )
    if layout is None:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": msg,
            "sample_info": summary,
        }
    script, div = plot_to_components(layout)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
        "sample_info": summary,
    }



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
