#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – SNR, BERV and median-spectrum plot builders.

Part of the object-page plot suite; see also:
    plot_obj_ccf.py        – CCF plots
    plot_obj_lbl.py        – LBL RV plots
    plot_obj_timeseries.py – per-night time-series plots
    plot_obj_ind.py        – individual file-browser plots

Public API
----------
build_snr_plot_json          – SNR vs time (json_item)
build_berv_plot_json         – BERV coverage (json_item)
build_snr_plot_components    – SNR vs time (script/div)
build_berv_plot_components   – BERV coverage (script/div)
build_spec_plot_json         – Median spectrum (json_item)
build_spec_plot_components   – Median spectrum (script/div)

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

import re
import warnings
from datetime import datetime, timezone
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
__NAME__ = "apero_ri.plots.plot_obj_spectrum"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

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
        dt = mjd_to_datetime(row.get("EXT_MJDMID"))
        if dt is None:
            continue
        qc_ok = int(row.get("EXT_QCC_ALL") or 1) == 1
        # ---------------------------------------------------------------------
        raw_h = row.get("EXT_H")
        if raw_h is not None:
            try:
                h_pts.append((dt, float(raw_h), qc_ok))
            except (TypeError, ValueError):
                pass
        raw_y = row.get("EXT_Y")
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
        dt = mjd_to_datetime(row.get("EXT_MJDMID"))
        if dt is None:
            continue
        raw_berv = row.get("EXT_BERV")
        if raw_berv is None:
            continue
        try:
            berv_kms = float(raw_berv)
        except (TypeError, ValueError):
            continue
        # ---------------------------------------------------------------------
        vtot = (vsys_kms - berv_kms) if vsys_kms is not None else -berv_kms
        ext_qc_ok = int(row.get("EXT_QCC_ALL") or 1) == 1
        tcorr_qc_raw = row.get("TCORR_QCC_ALL")
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
            v = row.get("EXT_MJDMID")
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
        jd_start = Time(mjd_min, format="mjd").jd - 14
        jd_end = Time(mjd_max, format="mjd").jd + 60
        times_jd = np.arange(jd_start, jd_end, 1.0)
        # ---------------------------------------------------------------------
        # object parameters
        ra = float(obj_props.get("RA [Deg]") or 0.0)
        dec = float(obj_props.get("Dec [Deg]") or 0.0)
        pmra = float(obj_props.get("PMRA [mas/yr]") or 0.0)
        pmdec = float(obj_props.get("PMDE [mas/yr]") or 0.0)
        px = float(obj_props.get("Plx [mas]") or 0.0)
        rv = float(obj_props.get("RV [km/s]") or 0.0)
        # ---------------------------------------------------------------------
        # observatory parameters
        lat = float(obs_props.get("lat", 0.0))
        lon = float(obs_props.get("lon", 0.0))
        alt = float(obs_props.get("alt", 0.0))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = barycorrpy.get_BC_vel(
                JDUTC=times_jd,
                ra=ra,
                dec=dec,
                epoch=2451545.0,  # J2000.0 in JD
                pmra=pmra,
                pmdec=pmdec,
                px=px,
                rv=rv,
                lat=lat,
                longi=lon,
                alt=alt,
                leap_update=False,
            )
        bervs_kms = result[0] / 1000.0  # convert m/s → km/s
        vsys_kms = (vsys_ms / 1000.0) if vsys_ms is not None else 0.0
        vtot_kms = vsys_kms - bervs_kms
        # ---------------------------------------------------------------------
        # convert JD times to UTC datetimes for Bokeh
        x_dates = []
        for jd in times_jd:
            try:
                dt = Time(jd, format="jd").to_datetime(timezone=timezone.utc)
                x_dates.append(dt)
            except Exception:
                pass
        return x_dates, list(vtot_kms)

    except Exception:
        return [], []


# =============================================================================
# Define private SNR / BERV figure builders
# =============================================================================
def _make_snr_figure(
    h_pts: list, y_pts: list, label_h: str, label_y: str
) -> Any:
    """
    Build a Bokeh figure for the SNR vs time plot.

    :param h_pts: list of (dt, snr, qc_ok) tuples for H-band
    :param y_pts: list of (dt, snr, qc_ok) tuples for Y-band
    :param label_h: str, legend label for H-band
    :param label_y: str, legend label for Y-band

    :return: Bokeh figure object
    :rtype: bokeh.plotting.figure
    """
    fig = make_time_figure(title="Signal to Noise Ratio vs Time", height=400)
    hover = HoverTool(
        tooltips=[
            ("Date (UTC)", "@x{%F %T}"),
            ("SNR", "@y{0.00}"),
        ],
        formatters={"@x": "datetime"},
        mode="mouse",
    )
    fig.add_tools(hover)

    # -------------------------------------------------------------------------
    def _add_series(pts: list, color: str, legend_label: str) -> None:
        pass_x = [p[0] for p in pts if p[2]]
        pass_y = [p[1] for p in pts if p[2]]
        fail_x = [p[0] for p in pts if not p[2]]
        fail_y = [p[1] for p in pts if not p[2]]
        if pass_x:
            src = ColumnDataSource({"x": pass_x, "y": pass_y})
            fig.scatter(
                "x",
                "y",
                source=src,
                color=color,
                size=6,
                alpha=0.78,
                marker="circle",
                legend_label=legend_label,
            )
        if fail_x:
            src = ColumnDataSource({"x": fail_x, "y": fail_y})
            fig.scatter(
                "x",
                "y",
                source=src,
                color=color,
                size=9,
                alpha=0.9,
                line_width=2,
                marker="cross",
                legend_label=f"{legend_label} (QC fail)",
            )

    # -------------------------------------------------------------------------
    _add_series(h_pts, "#e6820a", label_h)  # orange for H-band
    _add_series(y_pts, "#7e22ce", label_y)  # purple for Y-band

    fig.xaxis.axis_label = "Date (UTC)"
    fig.yaxis.axis_label = "SNR"
    if fig.legend:
        fig.legend.location = "top_left"
        fig.legend.click_policy = "hide"
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
    fig = make_time_figure(title="BERV Coverage", height=400)
    hover_pts = HoverTool(
        tooltips=[
            ("Date (UTC)", "@x{%F %T}"),
            ("Vtot", "@y{0.000} km/s"),
        ],
        formatters={"@x": "datetime"},
        mode="mouse",
    )
    fig.add_tools(hover_pts)
    # -------------------------------------------------------------------------
    # BERV curve (background line)
    if curve_x and curve_y:
        src_curve = ColumnDataSource({"x": curve_x, "y": curve_y})
        fig.line(
            "x",
            "y",
            source=src_curve,
            line_color="gray",
            line_dash="dotted",
            line_width=2,
            alpha=0.7,
            legend_label="BERV curve",
        )
    # -------------------------------------------------------------------------
    # Vsys horizontal line  — solid blue
    if vsys_ms is not None:
        vsys_kms = vsys_ms / 1000.0
        vsys_span = Span(
            location=vsys_kms,
            dimension="width",
            line_color="blue",
            line_dash="solid",
            line_width=1.5,
            level="overlay",
        )
        fig.add_layout(vsys_span)
        src_dummy = ColumnDataSource({"x": [], "y": []})
        fig.line(
            "x",
            "y",
            source=src_dummy,
            line_color="blue",
            line_width=1.5,
            legend_label=f"v_sys = {vsys_kms:.3f} km/s",
        )
    # -------------------------------------------------------------------------
    # observation points (rendered on top)
    if passed:
        src = ColumnDataSource(
            {
                "x": [p[0] for p in passed],
                "y": [p[1] for p in passed],
            }
        )
        fig.scatter(
            "x",
            "y",
            source=src,
            name="berv_pts",
            color="green",
            size=6,
            alpha=0.6,
            marker="circle",
            legend_label="Passed all QC",
        )
    if ext_fail:
        src = ColumnDataSource(
            {
                "x": [p[0] for p in ext_fail],
                "y": [p[1] for p in ext_fail],
            }
        )
        fig.scatter(
            "x",
            "y",
            source=src,
            name="berv_pts",
            color="blue",
            size=9,
            alpha=0.9,
            line_width=2,
            marker="cross",
            legend_label="Failed QC (EXT)",
        )
    if tcorr_fail:
        src = ColumnDataSource(
            {
                "x": [p[0] for p in tcorr_fail],
                "y": [p[1] for p in tcorr_fail],
            }
        )
        fig.scatter(
            "x",
            "y",
            source=src,
            name="berv_pts",
            color="red",
            size=9,
            alpha=0.9,
            line_width=2,
            marker="cross",
            legend_label="Failed QC (TCORR)",
        )
    # -------------------------------------------------------------------------
    fig.xaxis.axis_label = "Date (UTC)"
    fig.yaxis.axis_label = y_label
    if fig.legend:
        fig.legend.location = "top_left"
        fig.legend.click_policy = "hide"
    return fig


# =============================================================================
# Define public SNR / BERV builders
# =============================================================================
def build_snr_plot_json(
    htable_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
    target_id: str = "op-snr-plot-div",
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
    label_h = sci_header_label(preset, "ext", "EXT_H", "H-band SNR")
    label_y = sci_header_label(preset, "ext", "EXT_Y", "Y-band SNR")
    h_pts, y_pts = _extract_snr_points(htable_rows)
    if not h_pts and not y_pts:
        return {
            "has_plot": False,
            "message": "No SNR data found in htable.",
        }
    fig = _make_snr_figure(h_pts, y_pts, label_h, label_y)
    script, div = plot_to_components(fig)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
    }


def build_berv_plot_json(
    htable_rows: List[Dict[str, Any]],
    vsys_ms: Optional[float],
    preset: Dict[str, Any],
    obj_props: Optional[Dict[str, Any]] = None,
    target_id: str = "op-berv-plot-div",
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
    passed, ext_fail, tcorr_fail = _extract_berv_points(htable_rows, vsys_ms)
    if not passed and not ext_fail and not tcorr_fail:
        return {
            "has_plot": False,
            "message": "No BERV data found in htable.",
        }
    obs_props = (preset or {}).get("observatory", {})
    curve_x, curve_y = _compute_berv_curve(
        htable_rows, obj_props or {}, obs_props, vsys_ms
    )
    y_label = (
        "Vtot = Vsys \u2212 BERV [km/s]"
        if vsys_ms is not None
        else "\u2212BERV [km/s]"
    )
    fig = _make_berv_figure(
        passed,
        ext_fail,
        tcorr_fail,
        curve_x,
        curve_y,
        vsys_ms,
        y_label,
    )
    script, div = plot_to_components(fig)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
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
    label_h = sci_header_label(preset, "ext", "EXT_H", "H-band SNR")
    label_y = sci_header_label(preset, "ext", "EXT_Y", "Y-band SNR")
    h_pts, y_pts = _extract_snr_points(htable_rows)
    if not h_pts and not y_pts:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No SNR data found in htable.",
        }
    fig = _make_snr_figure(h_pts, y_pts, label_h, label_y)
    script, div = plot_to_components(fig)
    return {"has_plot": True, "script": script, "div": div, "message": ""}


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
    passed, ext_fail, tcorr_fail = _extract_berv_points(htable_rows, vsys_ms)
    if not passed and not ext_fail and not tcorr_fail:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No BERV data found in htable.",
        }
    obs_props = (preset or {}).get("observatory", {})
    curve_x, curve_y = _compute_berv_curve(
        htable_rows, obj_props or {}, obs_props, vsys_ms
    )
    y_label = (
        "Vtot = Vsys \u2212 BERV [km/s]"
        if vsys_ms is not None
        else "\u2212BERV [km/s]"
    )
    fig = _make_berv_figure(
        passed,
        ext_fail,
        tcorr_fail,
        curve_x,
        curve_y,
        vsys_ms,
        y_label,
    )
    script, div = plot_to_components(fig)
    return {"has_plot": True, "script": script, "div": div, "message": ""}


# =============================================================================
# Define private file path helpers
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
        ident = str(row.get("IDENTIFIER", "") or "").strip()
        raw_h = row.get("EXT_H")
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
        ident = str(row.get("IDENTIFIER", "") or "").strip()
        if ident in id_to_snr:
            scored.append((abs(id_to_snr[ident] - med_snr), row))
    if not scored:
        return None, None
    scored.sort(key=lambda x: x[0])
    best_row = scored[0][1]
    best_ident = str(best_row.get("IDENTIFIER", "") or "").strip()
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
        if str(row.get("IDENTIFIER", "") or "").strip() == identifier:
            return row
    return None


def _derive_s1d_path(
    ext_row: Dict[str, Any], paths: Dict[str, str]
) -> Optional[Path]:
    """
    Derive the extracted S1D path by replacing ``_e2dsff_`` with
    ``_s1d_v_`` in the filename.

    :param ext_row: dict, ftable ext row with FILENAME
    :param paths: dict mapping PATH_* keys to directory strings

    :return: resolved Path or None
    :rtype: Path | None
    """
    filename = str(ext_row.get("FILENAME", "") or "").strip()
    s1d_filename = filename.replace("_e2dsff_", "_s1d_v_")
    if s1d_filename == filename:
        return None
    return _resolve_file_path(dict(ext_row, FILENAME=s1d_filename), paths)


def _derive_sc1d_path(
    tcorr_row: Dict[str, Any], paths: Dict[str, str]
) -> Optional[Path]:
    """
    Derive the telluric-corrected S1D path by replacing
    ``_e2dsff_tcorr_`` with ``_s1d_v_tcorr_`` in the filename.

    :param tcorr_row: dict, ftable tcorr row with FILENAME
    :param paths: dict mapping PATH_* keys to directory strings

    :return: resolved Path or None
    :rtype: Path | None
    """
    filename = str(tcorr_row.get("FILENAME", "") or "").strip()
    sc1d_filename = filename.replace("_e2dsff_tcorr_", "_s1d_v_tcorr_")
    if sc1d_filename == filename:
        return None
    return _resolve_file_path(dict(tcorr_row, FILENAME=sc1d_filename), paths)


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
            wave = np.array(dat["wavelength"], dtype=float)
            flux = np.array(dat["flux"], dtype=float)
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
    sizing_mode: str = "stretch_width",
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
        x_axis_label="Wavelength [nm]",
        y_axis_label="Flux",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=height,
        sizing_mode=sizing_mode,
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    mask = (wave >= xlim[0]) & (wave <= xlim[1])
    w_m = wave[mask]
    # Theme-aware foreground colour for the "Extracted" line (was
    # hardcoded "black", invisible on the dark theme).
    from apero_ri.plots.bokeh_theme import fg_glyph_color
    fg = fg_glyph_color()
    # -------------------------------------------------------------------------
    if ext_flux is not None:
        ef_m = np.where(np.isfinite(ext_flux[mask]), ext_flux[mask], np.nan)
        fig.line(
            w_m,
            ef_m,
            line_color=fg,
            line_width=0.8,
            alpha=0.9,
            legend_label="Extracted",
        )
    if tcorr_flux is not None:
        tf_m = np.where(np.isfinite(tcorr_flux[mask]), tcorr_flux[mask], np.nan)
        fig.line(
            w_m,
            tf_m,
            line_color="red",
            line_width=0.8,
            alpha=0.9,
            legend_label="Telluric corrected",
        )
        valid_tc = tf_m[np.isfinite(tf_m)]
        if len(valid_tc) > 0:
            fig.y_range.start = 0.0
            fig.y_range.end = float(1.5 * np.nanpercentile(valid_tc, 99))
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
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
    from bokeh.layouts import column as bk_column
    from bokeh.layouts import gridplot

    ext_row, best_ident = _find_median_ext_row(htable_rows, ftable_ext_rows)
    if ext_row is None:
        return None, "No matching EXT spectrum found."

    s1d_path = _derive_s1d_path(ext_row, paths)
    if s1d_path is None:
        return None, "Extracted S1D file not found on disk."

    wave, ext_flux = _load_s1d_data(s1d_path)
    if wave is None:
        return None, "Could not load extracted S1D data."
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
    spec_wave = (preset or {}).get("plot", {}).get("SpecWave", {})
    limit0: List[float] = spec_wave.get("limit0", [965, 2500])
    limit1: List[float] = spec_wave.get("limit1", [1082, 1085])
    limit2: List[float] = spec_wave.get("limit2", [1600, 1604])
    limit3: List[float] = spec_wave.get("limit3", [2164, 2169])
    # -------------------------------------------------------------------------
    # build title with median SNR
    snr_h_label = sci_header_label(preset, "ext", "EXT_H", "H-band SNR")
    med_snr_h: Optional[float] = None
    for row in htable_rows:
        if str(row.get("IDENTIFIER", "") or "").strip() == best_ident:
            try:
                med_snr_h = float(row.get("EXT_H") or 0)
            except (TypeError, ValueError):
                pass
            break
    title_full = (
        f"Median spectrum [{snr_h_label}={med_snr_h:.1f}]"
        if med_snr_h is not None
        else "Median spectrum"
    )
    # -------------------------------------------------------------------------
    # build figures for normal/object-page layout vs maximize layout
    if maximize:
        # In maximize mode each row is a separate Bokeh root so CSS
        # flex can give each ~50 % of the available viewport height.
        fig_full = _make_spec_band_figure(
            wave,
            ext_flux,
            tcorr_flux,
            limit0,
            title_full,
            height=200,
            sizing_mode="stretch_both",
        )
        fig_z1 = _make_spec_band_figure(
            wave,
            ext_flux,
            tcorr_flux,
            limit1,
            f"Zoom in {limit1[0]}\u2013{limit1[1]} nm",
            height=200,
            sizing_mode="stretch_both",
        )
        fig_z2 = _make_spec_band_figure(
            wave,
            ext_flux,
            tcorr_flux,
            limit2,
            f"Zoom in {limit2[0]}\u2013{limit2[1]} nm",
            height=200,
            sizing_mode="stretch_both",
        )
        fig_z3 = _make_spec_band_figure(
            wave,
            ext_flux,
            tcorr_flux,
            limit3,
            f"Zoom in {limit3[0]}\u2013{limit3[1]} nm",
            height=200,
            sizing_mode="stretch_both",
        )
        zoom_grid = gridplot(
            [[fig_z1, fig_z2, fig_z3]],
            sizing_mode="stretch_both",
        )
        # Return two separate roots; build_spec_plot_components will
        # call components([fig_full, zoom_grid]) to get one shared
        # script and two independent divs for the template.
        return [fig_full, zoom_grid], ""
    else:
        fig_full = _make_spec_band_figure(
            wave, ext_flux, tcorr_flux, limit0, title_full, height=280
        )
        fig_z1 = _make_spec_band_figure(
            wave,
            ext_flux,
            tcorr_flux,
            limit1,
            f"Zoom in {limit1[0]}\u2013{limit1[1]} nm",
            height=220,
        )
        fig_z2 = _make_spec_band_figure(
            wave,
            ext_flux,
            tcorr_flux,
            limit2,
            f"Zoom in {limit2[0]}\u2013{limit2[1]} nm",
            height=220,
        )
        fig_z3 = _make_spec_band_figure(
            wave,
            ext_flux,
            tcorr_flux,
            limit3,
            f"Zoom in {limit3[0]}\u2013{limit3[1]} nm",
            height=220,
        )
        layout = bk_column(
            [
                fig_full,
                gridplot(
                    [[fig_z1, fig_z2, fig_z3]],
                    sizing_mode="stretch_width",
                ),
            ],
            sizing_mode="stretch_width",
        )
    return layout, ""


# =============================================================================
# Define public spectrum plot builders
# =============================================================================
def build_spec_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    ftable_tcorr_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    target_id: str = "op-spec-plot-div",
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
        return {"has_plot": False, "message": msg}
    script, div = plot_to_components(layout)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
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
        htable_rows,
        ftable_ext_rows,
        ftable_tcorr_rows,
        paths,
        preset,
        maximize=maximize,
    )
    if layout is None:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": msg,
        }
    if isinstance(layout, list):
        # maximize mode: two separate roots → one script, two divs
        from bokeh.embed import components as _bk_components

        script, div_list = _bk_components(layout)
        return {
            "has_plot": True,
            "script": script,
            "div": div_list[0],
            "div2": div_list[1],
            "two_rows": True,
            "message": "",
        }
    script, div = plot_to_components(layout)
    return {"has_plot": True, "script": script, "div": div, "message": ""}



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
