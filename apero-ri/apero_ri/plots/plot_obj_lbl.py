#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – LBL (line-by-line) radial-velocity plot builders.

Part of the object-page plot suite; see also:
    plot_obj_spectrum.py   – SNR, BERV and median-spectrum plots
    plot_obj_ccf.py        – CCF plots
    plot_obj_timeseries.py – per-night time-series plots
    plot_obj_ind.py        – individual file-browser plots

Public API
----------
build_lbl_plots_json     – all LBL flavor plots (json_item dict)
build_lbl_plot_components – single LBL flavor (script/div)

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from apero_ri.base import base
from apero_ri.plots.plot_general import (
    make_time_figure,
    mjd_to_datetime,
    plot_to_components,
    sci_header_label,
)
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
__NAME__ = "apero_ri.plots.plot_obj_lbl"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

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
    m = re.match(r"^lbl_(.+)\.rdb$", fname, re.IGNORECASE)
    return m.group(1) if m else fname


def _norm_obj_token(value: str) -> str:
    """
    Normalize an object/flavor token for robust equality checks.

    :param value: str, input token

    :return: str, lowercase alphanumeric-only token
    :rtype: str
    """
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _is_self_lbl_flavor(flavor_id: str, objname: str) -> bool:
    """
    Return True when *flavor_id* represents the self-self flavor for
    *objname* (i.e. ``{objname}_{objname}``, normalization-aware).

    :param flavor_id: str, parsed LBL flavor ID
    :param objname: str, object name from request/context

    :return: bool, True for self-self flavor
    :rtype: bool
    """
    ftoken = _norm_obj_token(flavor_id)
    otoken = _norm_obj_token(objname)
    if not ftoken or not otoken:
        return False
    return ftoken == (otoken + otoken)


def _sort_lbl_rdb_rows(
    rows: List[Dict[str, Any]], objname: str = ""
) -> List[Dict[str, Any]]:
    """
    Sort LBL RDB rows with self-self flavor first, then by filename.

    :param rows: list of LBL RDB ftable rows
    :param objname: str, target object name

    :return: sorted row list
    :rtype: list
    """

    def _key(row: Dict[str, Any]) -> Tuple[int, str]:
        fname = str(row.get("FILENAME", "") or "").strip()
        flavor_id = _lbl_rdb_flavor_id(fname)
        return (
            0 if _is_self_lbl_flavor(flavor_id, objname) else 1,
            fname.lower(),
        )

    return sorted(list(rows), key=_key)


def _match_lbl_snr_from_htable(
    rjd: np.ndarray,
    htable_rows: List[Dict[str, Any]],
    max_dt_days: float = 3.0e-2,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Map LBL ``rjd`` samples to htable SNR columns using nearest
    ``EXT_MJDMID`` match within a small tolerance.

    :param rjd: numpy.ndarray, LBL MJD times
    :param htable_rows: list of htable rows
    :param max_dt_days: float, max allowed |delta_mjd| for match

    :return: tuple (snr_h, snr_y) arrays aligned to ``rjd``
    :rtype: tuple[numpy.ndarray, numpy.ndarray]
    """
    snr_h = np.full(len(rjd), np.nan, dtype=float)
    snr_y = np.full(len(rjd), np.nan, dtype=float)
    if not len(rjd) or not htable_rows:
        return snr_h, snr_y

    mjd_vals: List[float] = []
    h_vals: List[float] = []
    y_vals: List[float] = []
    for row in htable_rows:
        if not isinstance(row, dict):
            continue
        try:
            mjd = float(row.get("EXT_MJDMID"))
        except (TypeError, ValueError):
            continue
        try:
            hval = float(row.get("EXT_H"))
        except (TypeError, ValueError):
            hval = np.nan
        try:
            yval = float(row.get("EXT_Y"))
        except (TypeError, ValueError):
            yval = np.nan
        mjd_vals.append(mjd)
        h_vals.append(hval)
        y_vals.append(yval)

    if not mjd_vals:
        return snr_h, snr_y

    mjd_arr = np.array(mjd_vals, dtype=float)
    h_arr = np.array(h_vals, dtype=float)
    y_arr = np.array(y_vals, dtype=float)
    for it, rjd_i in enumerate(rjd):
        r = float(rjd_i)
        # LBL tables can carry RJD-like values offset from MJD by 0.5 day.
        # Try direct and +/-0.5 shifted matches, then keep the best.
        d0 = np.abs(mjd_arr - r)
        d1 = np.abs(mjd_arr - (r - 0.5))
        d2 = np.abs(mjd_arr - (r + 0.5))
        if d0.size == 0:
            continue
        cands = [
            (float(np.min(d0)), int(np.argmin(d0))),
            (float(np.min(d1)), int(np.argmin(d1))),
            (float(np.min(d2)), int(np.argmin(d2))),
        ]
        cands.sort(key=lambda item: item[0])
        best_dt, j = cands[0]
        if best_dt <= float(max_dt_days):
            snr_h[it] = h_arr[j]
            snr_y[it] = y_arr[j]
    return snr_h, snr_y


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
    obs_dir = str(lbl_row.get("OBS_DIR", "") or "").strip()
    filename = str(lbl_row.get("FILENAME", "") or "").strip()
    if not filename:
        return None, None
    base = Path(path_lbl).resolve()
    try:
        obs_part = Path(obs_dir.strip("/")) if obs_dir else Path("")
        candidate = (base / obs_part / filename).resolve()
        candidate.relative_to(base)
        if not candidate.is_file():
            return None, None
    except (ValueError, OSError):
        return None, None
    try:
        from astropy.table import Table as _ATable

        tbl = _ATable.read(str(candidate), format="ascii.rdb")
    except Exception:
        return None, None
    return _lbl_rdb_flavor_id(filename), tbl


def _lbl_wave_colour(wave_nm: float, wave_min: float, wave_max: float) -> str:
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
    t = 0.0 if span <= 0 else max(0.0, min(1.0, (wave_nm - wave_min) / span))
    if t < 0.5:
        r = int(round(2.0 * t * 255))
        g = int(round(2.0 * t * 255))
        b = 255
    else:
        r = 255
        g = int(round(2.0 * (1.0 - t) * 255))
        b = int(round(2.0 * (1.0 - t) * 255))
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


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
    from bokeh.models import TeeHead, Whisker

    fig = make_time_figure(
        f"LBL Radial Velocity \u2014 {flavor_id}", height=height
    )
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
    dts_ms = np.array([dt.timestamp() * 1000.0 for dt in datetimes])
    good = ~reset_mask
    # -------------------------------------------------------------------------
    if np.any(good):
        src = ColumnDataSource(
            dict(
                x=dts_ms[good],
                y=vrad[good],
                upper=vrad[good] + svrad[good],
                lower=vrad[good] - svrad[good],
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src,
            marker='circle',
            size=5,
            color="green",
            alpha=0.7,
            legend_label="Good",
        )
        fig.add_layout(
            Whisker(
                source=src,
                base="x",
                upper="upper",
                lower="lower",
                line_color="green",
                line_alpha=0.7,
                upper_head=TeeHead(
                    line_color="green", line_alpha=0.7, size=6
                ),
                lower_head=TeeHead(
                    line_color="green", line_alpha=0.7, size=6
                ),
            )
        )
    if np.any(reset_mask):
        src_rst = ColumnDataSource(
            dict(
                x=dts_ms[reset_mask],
                y=vrad[reset_mask],
                upper=vrad[reset_mask] + svrad[reset_mask],
                lower=vrad[reset_mask] - svrad[reset_mask],
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src_rst,
            marker='circle',
            size=5,
            color="mediumpurple",
            alpha=0.7,
            legend_label="Reset RV",
        )
        fig.add_layout(
            Whisker(
                source=src_rst,
                base="x",
                upper="upper",
                lower="lower",
                line_color="mediumpurple",
                line_alpha=0.7,
                upper_head=TeeHead(
                    line_color="mediumpurple",
                    line_alpha=0.7,
                    size=6,
                ),
                lower_head=TeeHead(
                    line_color="mediumpurple",
                    line_alpha=0.7,
                    size=6,
                ),
            )
        )
    # -------------------------------------------------------------------------
    diff = float(ylim[1] - ylim[0])
    l_arrow = 0.04 * diff
    for clip_mask, yt, marker in [
        (vrad < ylim[0], ylim[0] + l_arrow, "triangle"),
        (vrad > ylim[1], ylim[1] - l_arrow, "inverted_triangle"),
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
    fig.y_range.start = ylim[0]
    fig.y_range.end = ylim[1]
    fig.yaxis.axis_label = "Velocity [m/s]"
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
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
    fig = make_time_figure(f"{snr_label} vs Time", height=height)
    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Date (UTC)", "@x{%F %T}"),
                ("SNR", "@y{0.00}"),
            ],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
    )
    dts_ms = np.array([dt.timestamp() * 1000.0 for dt in datetimes])
    bad_set = set(bad_idxs)
    bad_mask = np.array(
        [i in bad_set for i in range(len(datetimes))], dtype=bool
    )
    good_no_bad = (~reset_mask) & (~bad_mask)
    # -------------------------------------------------------------------------
    if np.any(good_no_bad):
        fig.scatter(
            dts_ms[good_no_bad],
            snr_h[good_no_bad],
            marker='circle',
            size=5,
            color="green",
            alpha=0.7,
            legend_label="Good",
        )
    if np.any(reset_mask):
        fig.scatter(
            dts_ms[reset_mask],
            snr_h[reset_mask],
            marker='circle',
            size=5,
            color="mediumpurple",
            alpha=0.7,
            legend_label="Reset RV",
        )
    if np.any(bad_mask):
        fig.scatter(
            dts_ms[bad_mask],
            snr_h[bad_mask],
            marker='circle',
            size=5,
            color="red",
            alpha=0.8,
            legend_label="Outlier",
        )
    # -------------------------------------------------------------------------
    fig.yaxis.axis_label = snr_label
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    return fig


def _make_lbl_wave_figure(
    datetimes: np.ndarray,
    vrad: np.ndarray,
    svrad: np.ndarray,
    wave_vrad_dict: Dict[str, np.ndarray],
    wave_svrad_dict: Dict[str, np.ndarray],
    wavemap: List[float],
    flavor_id: str = "",
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
    from bokeh.models import DatetimeTickFormatter, Whisker
    from bokeh.plotting import figure as bk_figure

    fig = bk_figure(
        title=(
            f"LBL Wave RV vs Time \u2014 {flavor_id}"
            if flavor_id
            else "LBL Wave RV vs Time"
        ),
        x_axis_type="datetime",
        x_axis_label="Date",
        y_axis_label="RV [m/s]",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=height,
        sizing_mode="stretch_width",
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
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
    fig.add_tools(CrosshairTool(dimensions="both"))
    fig.xaxis.formatter = DatetimeTickFormatter(
        days="%Y-%m-%d",
        months="%Y-%m",
        years="%Y",
    )

    wave_min = min(wavemap) if wavemap else 900.0
    wave_max = max(wavemap) if wavemap else 2500.0
    med_svrad = float(np.nanmedian(svrad)) if len(svrad) > 0 else 1.0
    dts_ms = np.array([dt.timestamp() * 1000.0 for dt in datetimes])
    # -------------------------------------------------------------------------
    for col_key, wave_nm in zip(wave_vrad_dict.keys(), wavemap):
        vrad_key = wave_vrad_dict[col_key]
        svrad_col = col_key.replace("vrad_", "svrad_")
        svrad_key = wave_svrad_dict.get(
            svrad_col, np.full(len(vrad_key), np.nan)
        )
        med_svrad_key = (
            float(np.nanmedian(svrad_key)) if len(svrad_key) > 0 else 0.0
        )
        if med_svrad_key > 10.0 * med_svrad:
            continue
        if med_svrad > 0 and med_svrad_key < med_svrad * 0.01:
            continue
        color = _lbl_wave_colour(wave_nm, wave_min, wave_max)
        label = f"{int(wave_nm)} nm"
        src_w = ColumnDataSource(
            dict(
                x=dts_ms,
                y=vrad_key,
                upper=vrad_key + svrad_key,
                lower=vrad_key - svrad_key,
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src_w,
            size=4,
            color=color,
            alpha=0.5,
            marker="circle",
            legend_label=label,
        )
        whisk = Whisker(
            source=src_w,
            base="x",
            upper="upper",
            lower="lower",
            line_color=color,
            line_alpha=0.5,
        )
        # Match whisker caps to wavelength colour (avoid default black caps).
        whisk.upper_head.line_color = color
        whisk.lower_head.line_color = color
        whisk.upper_head.line_alpha = 0.5
        whisk.lower_head.line_alpha = 0.5
        fig.add_layout(whisk)
    # overall vrad as foreground points (drawn last so it remains on top).
    # Use a theme-aware foreground colour so it stays visible on the
    # near-black dark theme background (was hardcoded "black").
    from apero_ri.plots.bokeh_theme import fg_glyph_color
    fg = fg_glyph_color()
    src_ov = ColumnDataSource(
        dict(
            x=dts_ms,
            y=vrad,
            upper=vrad + svrad,
            lower=vrad - svrad,
        )
    )
    fig.scatter(
        "x",
        "y",
        source=src_ov,
        size=5,
        color=fg,
        alpha=0.55,
        marker="circle",
        legend_label="Overall vrad",
        level="overlay",
    )
    whisk_ov = Whisker(
        source=src_ov,
        base="x",
        upper="upper",
        lower="lower",
        line_color=fg,
        line_alpha=0.55,
    )
    whisk_ov.upper_head.line_color = fg
    whisk_ov.lower_head.line_color = fg
    whisk_ov.upper_head.line_alpha = 0.55
    whisk_ov.lower_head.line_alpha = 0.55
    fig.add_layout(whisk_ov)
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
    legend.click_policy = "hide"
    legend.orientation = "horizontal"
    if hasattr(legend, "nrows"):
        legend.nrows = 2
    legend.label_text_font_size = "9pt"
    legend.spacing = 2
    legend.padding = 4
    fig.add_layout(legend, "below")
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    return fig


def _build_lbl_layout(
    tbl: Any,
    flavor_id: str,
    preset: Dict[str, Any],
    htable_rows: Optional[List[Dict[str, Any]]] = None,
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

    rjd = np.array([float(v) for v in tbl["rjd"]])
    vrad = np.array([float(v) for v in tbl["vrad"]])
    svrad = np.array([float(v) for v in tbl["svrad"]])
    reset_mask = np.array([bool(int(v)) for v in tbl["RESET_RV"]])

    snr_h_label = sci_header_label(preset, "lbl", "EXT_H", "EXT_H")
    snr_h, snr_y = _match_lbl_snr_from_htable(rjd, htable_rows or [])
    if not np.any(np.isfinite(snr_h)):
        try:
            snr_h = np.array([float(v) for v in tbl["EXT_H"]])
        except (KeyError, Exception):
            pass
    if not np.any(np.isfinite(snr_h)):
        try:
            snr_h = np.array([float(v) for v in tbl["EXTSN035"]])
        except (KeyError, Exception):
            snr_h = np.array(snr_y, copy=True)
    if not np.any(np.isfinite(snr_h)):
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
    ylim: List[float] = [central - 1.5 * diff, central + 1.5 * diff]
    bad_idxs = [
        int(i) for i in np.where((vrad_s < ylim[0]) | (vrad_s > ylim[1]))[0]
    ]
    # -------------------------------------------------------------------------
    # wave-binned columns
    wave_vrad_cols = [
        c for c in tbl.colnames if c.startswith("vrad_") and "nm" in c
    ]
    wave_svrad_cols = [
        c for c in tbl.colnames if c.startswith("svrad_") and "nm" in c
    ]

    def _wave_nm_from_col(colname: str) -> float:
        m = re.match(r".*_(\d+)nm", str(colname))
        if m:
            return float(m.group(1))
        return float("inf")

    wave_vrad_cols = sorted(wave_vrad_cols, key=_wave_nm_from_col)
    wave_svrad_cols = sorted(wave_svrad_cols, key=_wave_nm_from_col)
    wave_vrad_dict: Dict[str, np.ndarray] = {}
    wave_svrad_dict: Dict[str, np.ndarray] = {}
    wavemap: List[float] = []
    for col in wave_vrad_cols:
        m = re.match(r"vrad_(\d+)nm", col)
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
    fig_snr = _make_lbl_snr_figure(dts_s, snr_s, reset_s, bad_idxs, snr_h_label)
    fig_wave = _make_lbl_wave_figure(
        dts_s,
        vrad_s,
        svrad_s,
        wave_vrad_dict,
        wave_svrad_dict,
        wavemap,
        flavor_id=flavor_id,
        height=420,
    )
    return bk_column([fig_rv, fig_snr, fig_wave], sizing_mode="stretch_width")


# =============================================================================
# Define public LBL plot builders
# =============================================================================
def build_lbl_plots_json(
    ftable_lbl_rdb_rows: List[Dict[str, Any]],
    path_lbl: str,
    preset: Dict[str, Any],
    target_id_prefix: str = "op-lbl-vel-plot",
    htable_rows: Optional[List[Dict[str, Any]]] = None,
    objname: str = "",
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
    for row in _sort_lbl_rdb_rows(ftable_lbl_rdb_rows, objname=objname):
        filename = str(row.get("FILENAME", "") or "").strip()
        if not filename:
            continue
        flavor_id, tbl = _load_lbl_table(row, path_lbl)
        if tbl is None:
            results[filename] = {
                "has_plot": False,
                "message": f"Could not load {filename}",
            }
            continue
        target_id = f"{target_id_prefix}-{flavor_id}"
        try:
            layout = _build_lbl_layout(
                tbl, flavor_id, preset, htable_rows=htable_rows
            )
            if layout is None:
                results[filename] = {
                    "has_plot": False,
                    "message": "No valid date rows in RDB file.",
                }
                continue
            script, div = plot_to_components(layout)
            results[filename] = {
                "has_plot": True,
                "script": script,
                "div": div,
                "message": "",
            }
        except Exception as exc:
            results[filename] = {
                "has_plot": False,
                "message": f"Plot error: {exc}",
            }
    return results


def build_lbl_plot_components(
    ftable_lbl_rdb_rows: List[Dict[str, Any]],
    path_lbl: str,
    preset: Dict[str, Any],
    lbl_filename: str,
    htable_rows: Optional[List[Dict[str, Any]]] = None,
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
        filename = str(row.get("FILENAME", "") or "").strip()
        if filename != lbl_filename:
            continue
        flavor_id, tbl = _load_lbl_table(row, path_lbl)
        if tbl is None:
            return {
                "has_plot": False,
                "script": "",
                "div": "",
                "message": f"Could not load {lbl_filename}",
            }
        layout = _build_lbl_layout(
            tbl, flavor_id, preset, htable_rows=htable_rows
        )
        if layout is None:
            return {
                "has_plot": False,
                "script": "",
                "div": "",
                "message": "No valid date rows in RDB file.",
            }
        script, div = plot_to_components(layout)
        return {
            "has_plot": True,
            "script": script,
            "div": div,
            "message": "",
        }
    return {
        "has_plot": False,
        "script": "",
        "div": "",
        "message": (f"RDB file {lbl_filename} not found in ftable rows."),
    }



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
