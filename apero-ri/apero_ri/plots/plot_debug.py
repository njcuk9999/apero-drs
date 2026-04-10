#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Debug plot generation for the data portal object page.

Generates Bokeh-based interactive debug plots from htable header data.

Five debug plot types:
- Maximum saturation level (EXT_EXTSMAX vs time)
- Effective readout noise (EXT_EFFRON vs time)
- APERO version & processing date (EXT_VERSION / EXT_PDATE vs time)
- Calibration time deltas (EXT_CDT* − EXT_MJDMID vs time), one panel per key
- Telluric correction map (from SC1D FITS files, generated on demand)

Created on 2026-03-25

@author: cook
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from apero_ri.base import base
from apero_ri.plots.plot_general import (
    make_time_figure,
    mjd_to_datetime,
    plot_to_components,
)

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.plots.plot_debug"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

PLOT_BACKGROUND_COLOR: str = base.PLOT_BACKGROUND_COLOR

# Debug plot definitions: key → (title, description)
DEBUG_PLOT_DEFS: Dict[str, Dict[str, str]] = {
    "extsmax": {
        "title": "Maximum Saturation Level",
        "description": (
            "Maximum saturation level measured at time of extraction."
        ),
    },
    "effron": {
        "title": "Effective Readout Noise",
        "description": ("Measured effective readout noise before extraction."),
    },
    "version": {
        "title": "APERO Processing Debug",
        "description": (
            "Plotting the version and processed date from the header from "
            "APERO. Note that offline reductions should lead to a straight "
            "line, while online reductions should be roughly a one-to-one "
            "with the Date axis."
        ),
    },
    "cdt": {
        "title": "Calibration Times",
        "description": (
            "Computed time between observation and calibration used. Some "
            "calibrations are reference calibrations (in purple) and thus "
            "diverge from the reference night, others should always be from "
            "the same night (orange) unless no calibration was taken that "
            "night in which case the closest calibration in time should have "
            "been used."
        ),
    },
    "tcorr_map": {
        "title": "Telluric Map",
        "description": (
            "Telluric map of e2dsff_tcorr_A files. Files are low-passed and "
            "corrected for the stars motion. The QC is displayed to the right "
            "of the image — in purple are the files that passed, in orange "
            "the files that failed."
        ),
    },
}


# =============================================================================
# Public API
# =============================================================================
def generate_debug_plots(
    htable_rows: List[Dict[str, Any]],
    objname: str,
    preset: Optional[Dict[str, Any]] = None,
    ftable_tcorr_rows: Optional[List[Dict[str, Any]]] = None,
    paths: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate all debug plots and return Bokeh script/div payloads.

    :param htable_rows: list of htable row dicts (one per observation)
    :param objname: str, object name for plot titles
    :param preset: dict, instrument profile preset (for CDT key colours)
    :param ftable_tcorr_rows: list of ftable tcorr row dicts (for tcorr map)
    :param paths: dict mapping PATH_* keys to directory strings (for tcorr map)

    :return: dict with 'success', 'plots' (dict of plot_key → plot_info)
    :rtype: dict
    """
    if not htable_rows:
        return dict(success=False, plots={}, error="No htable data available.")
    plots: Dict[str, Any] = {}
    for key in ("extsmax", "effron", "version", "cdt"):
        try:
            layout = _build_debug_layout(key, htable_rows, objname, preset)
        except Exception as e:
            plots[key] = _plot_entry(
                key, layout=None, error=f"Error generating plot: {e}"
            )
            continue
        plots[key] = _plot_entry(key, layout=layout)
    # tcorr_map is generated on demand (via generate button in the UI)
    # but we still provide an empty placeholder so JS knows the key exists
    plots["tcorr_map"] = _plot_entry("tcorr_map", layout=None, error="")
    return dict(success=True, plots=plots, error="")


def generate_single_debug_plot(
    plot_key: str,
    htable_rows: List[Dict[str, Any]],
    objname: str,
    preset: Optional[Dict[str, Any]] = None,
    ftable_tcorr_rows: Optional[List[Dict[str, Any]]] = None,
    paths: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate a single debug plot for the maximize view.

    Returns a dict compatible with the plot_payload format:
    ``{has_plot, script, div, message}``.
    """
    if not htable_rows:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No htable data available.",
        }
    try:
        if plot_key == "tcorr_map":
            if not ftable_tcorr_rows or not paths or not preset:
                return {
                    "has_plot": False,
                    "script": "",
                    "div": "",
                    "message": "Telluric map data unavailable.",
                }
            image = _build_tcorr_map(
                htable_rows, ftable_tcorr_rows, paths, preset, objname
            )
            if not image:
                return {
                    "has_plot": False,
                    "script": "",
                    "div": "",
                    "message": "Plot generation returned no image.",
                }
            defn = DEBUG_PLOT_DEFS.get(plot_key, {})
            title = defn.get("title", plot_key)
            div_html = (
                f'<div style="text-align:center;">'
                f'<img src="data:image/png;base64,{image}" '
                f'style="max-width:100%;height:auto;" '
                f'alt="{title}">'
                f"</div>"
            )
            return {
                "has_plot": True,
                "script": "",
                "div": div_html,
                "message": "",
            }
        else:
            layout = _build_debug_layout(plot_key, htable_rows, objname, preset)
    except Exception as e:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": f"Error generating plot: {e}",
        }
    if layout is None:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "Plot generation returned no data.",
        }
    script, div = plot_to_components(layout)
    return {"has_plot": True, "script": script, "div": div, "message": ""}


# =============================================================================
# Private helpers
# =============================================================================
def _plot_entry(
    key: str,
    layout: Optional[Any] = None,
    error: str = "",
) -> dict:
    """Build a standard plot info dict with Bokeh script/div."""
    defn = DEBUG_PLOT_DEFS.get(key, {})
    if layout is None:
        return {
            "key": key,
            "title": defn.get("title", key),
            "description": defn.get("description", ""),
            "has_plot": False,
            "script": "",
            "div": "",
            "error": error,
        }
    script, div = plot_to_components(layout)
    return {
        "key": key,
        "title": defn.get("title", key),
        "description": defn.get("description", ""),
        "has_plot": True,
        "script": script,
        "div": div,
        "error": error,
    }


def _extract_column(
    htable_rows: List[Dict[str, Any]], key: str, dtype=float
) -> np.ndarray:
    """Extract a column from htable_rows as a numpy array."""
    vals = []
    for row in htable_rows:
        val = row.get(key)
        if val is not None:
            try:
                vals.append(dtype(val))
            except (ValueError, TypeError):
                vals.append(np.nan if dtype == float else None)
        else:
            vals.append(np.nan if dtype == float else None)
    return np.array(vals)


def _extract_mjd_datetimes(
    htable_rows: List[Dict[str, Any]],
) -> tuple:
    """
    Extract MJD values and convert to UTC datetimes for Bokeh.

    :return: (mjd_arr, datetimes) or (None, None)
    """
    mjd_vals = []
    dts = []
    for row in htable_rows:
        val = row.get("EXT_MJDMID")
        if val is None:
            continue
        try:
            mjd = float(val)
        except (ValueError, TypeError):
            continue
        dt = mjd_to_datetime(mjd)
        if dt is None:
            continue
        mjd_vals.append(mjd)
        dts.append(dt)
    if not mjd_vals:
        return None, None
    return np.array(mjd_vals), dts


# =============================================================================
# Layout dispatcher
# =============================================================================
def _build_debug_layout(
    plot_key: str,
    htable_rows: List[Dict[str, Any]],
    objname: str,
    preset: Optional[Dict[str, Any]] = None,
) -> Optional[Any]:
    """Dispatch to the correct Bokeh layout builder."""
    builders = {
        "extsmax": _build_extsmax_layout,
        "effron": _build_effron_layout,
        "version": _build_version_layout,
        "cdt": _build_cdt_layout,
    }
    builder = builders.get(plot_key)
    if builder is None:
        return None
    if plot_key == "cdt":
        return builder(htable_rows, objname, preset)
    return builder(htable_rows, objname)


# =============================================================================
# Individual Bokeh layout builders
# =============================================================================
def _build_extsmax_layout(
    htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[Any]:
    """Maximum saturation level vs time (Bokeh scatter)."""
    return _build_simple_mjd_layout(
        htable_rows,
        column="EXT_EXTSMAX",
        ylabel="Maximum Saturation Level",
        title=f"Maximum Saturation Level [{objname}]",
        color="#1f77b4",
    )


def _build_effron_layout(
    htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[Any]:
    """Effective readout noise vs time (Bokeh scatter)."""
    return _build_simple_mjd_layout(
        htable_rows,
        column="EXT_EFFRON",
        ylabel="Effective Readout Noise",
        title=f"Effective Readout Noise [{objname}]",
        color="#2ca02c",
    )


def _build_simple_mjd_layout(
    htable_rows: List[Dict[str, Any]],
    column: str,
    ylabel: str,
    title: str,
    color: str = "#1f77b4",
) -> Optional[Any]:
    """Build a single Bokeh time-series scatter for one column."""
    from bokeh.layouts import column as bk_column
    from bokeh.models import ColumnDataSource, HoverTool

    mjd_arr, dts = _extract_mjd_datetimes(htable_rows)
    if dts is None or not dts:
        return None
    values = _extract_column(htable_rows, column)
    if len(values) == 0 or np.all(np.isnan(values)):
        return None
    # Align: only rows where MJDMID was parseable
    mjd_list = []
    val_list = []
    dt_list = []
    idx = 0
    for row in htable_rows:
        val = row.get("EXT_MJDMID")
        if val is None:
            continue
        try:
            float(val)
        except (ValueError, TypeError):
            continue
        vv = None
        try:
            raw = row.get(column)
            if raw is not None:
                vv = float(raw)
        except (ValueError, TypeError):
            pass
        if idx < len(dts):
            val_list.append(vv if vv is not None else float("nan"))
            dt_list.append(dts[idx])
        idx += 1
    if not dt_list:
        return None
    dts_ms = [dt.timestamp() * 1000.0 for dt in dt_list]
    src = ColumnDataSource({"x": dts_ms, "y": val_list})
    fig = make_time_figure(title=title, height=300)
    fig.yaxis.axis_label = ylabel
    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Date (UTC)", "@x{%F %T}"),
                (ylabel, "@y{0.000}"),
            ],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
    )
    fig.scatter("x", "y", source=src, size=6, color=color, alpha=0.7)
    return bk_column([fig], sizing_mode="stretch_width")


def _build_version_layout(
    htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[Any]:
    """APERO version (top) and processing date (bottom) vs time."""
    from bokeh.layouts import column as bk_column
    from bokeh.models import ColumnDataSource, HoverTool

    mjd_arr, dts = _extract_mjd_datetimes(htable_rows)
    if dts is None or not dts:
        return None

    dts_ms = [dt.timestamp() * 1000.0 for dt in dts]

    # --- version numbers (convert 'X.Y.ZZZ' → X*10000+Y*1000+Z) ---
    ver_nums = []
    for row in htable_rows:
        if row.get("EXT_MJDMID") is None:
            continue
        raw = str(row.get("EXT_VERSION", "") or "")
        try:
            parts = raw.split(".")
            if len(parts) >= 3:
                ver_nums.append(
                    int(parts[0]) * 10000
                    + int(parts[1]) * 1000
                    + int(parts[2])
                )
            else:
                ver_nums.append(float("nan"))
        except (ValueError, TypeError):
            ver_nums.append(float("nan"))
    if len(ver_nums) != len(dts_ms):
        return None

    # --- processing dates (convert ISO string → ms since epoch) ---
    pdate_ms = []
    for row in htable_rows:
        if row.get("EXT_MJDMID") is None:
            continue
        raw = str(row.get("EXT_PDATE", "") or "")
        try:
            from astropy.time import Time as _AstroTime

            mjd_p = _AstroTime(raw, format="iso").mjd
            dt_p = mjd_to_datetime(mjd_p)
            pdate_ms.append(
                dt_p.timestamp() * 1000.0 if dt_p is not None else float("nan")
            )
        except Exception:
            pdate_ms.append(float("nan"))
    if len(pdate_ms) != len(dts_ms):
        return None

    src_v = ColumnDataSource({"x": dts_ms, "y": ver_nums})
    src_p = ColumnDataSource({"x": dts_ms, "y": pdate_ms})

    fig_top = make_time_figure(
        title=f"APERO Version [{objname}]", height=250
    )
    fig_top.yaxis.axis_label = "Version Number"
    fig_top.add_tools(
        HoverTool(
            tooltips=[("Date (UTC)", "@x{%F %T}"), ("Version", "@y{0}")],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
    )
    fig_top.scatter("x", "y", source=src_v, size=5, color="#7e22ce", alpha=0.7)

    fig_bot = make_time_figure(
        title=f"APERO Processing Date [{objname}]", height=250
    )
    fig_bot.xaxis.axis_label = "Observation Date (UTC)"
    fig_bot.yaxis.axis_label = "Processing Date (UTC)"
    fig_bot.xaxis.formatter.__class__  # already set in make_time_figure
    fig_bot.yaxis.formatter = fig_top.xaxis.formatter.__class__()
    fig_bot.add_tools(
        HoverTool(
            tooltips=[
                ("Obs Date (UTC)", "@x{%F %T}"),
                ("Proc Date (UTC)", "@y{%F %T}"),
            ],
            formatters={"@x": "datetime", "@y": "datetime"},
            mode="mouse",
        )
    )
    fig_bot.scatter("x", "y", source=src_p, size=5, color="#e6820a", alpha=0.7)

    return bk_column([fig_top, fig_bot], sizing_mode="stretch_width")


def _build_cdt_layout(
    htable_rows: List[Dict[str, Any]],
    objname: str,
    preset: Optional[Dict[str, Any]] = None,
) -> Optional[Any]:
    """
    Calibration time deltas: one Bokeh figure per CDT key.

    Key order and reference flag come from
    ``preset['sci-headers']['ext']`` entries whose header keys start
    with ``EXT_CDT`` or equal ``EXT_WAVETIME``.  A key is coloured
    purple when its YAML entry contains ``ref: true``; otherwise orange.
    """
    from bokeh.layouts import column as bk_column
    from bokeh.models import ColumnDataSource, HoverTool

    mjd_arr, dts = _extract_mjd_datetimes(htable_rows)
    if dts is None or not dts:
        return None

    dts_ms = [dt.timestamp() * 1000.0 for dt in dts]

    # Build aligned MJD array for delta computation
    mjd_aligned = []
    valid_rows = []
    for row in htable_rows:
        v = row.get("EXT_MJDMID")
        if v is None:
            continue
        try:
            mjd_aligned.append(float(v))
            valid_rows.append(row)
        except (ValueError, TypeError):
            pass

    if not valid_rows:
        return None

    # Get CDT key list from preset sci-headers if available
    cdt_keys = _get_cdt_keys_from_preset(preset)

    figures = []
    for hdr_key, label, is_ref in cdt_keys:
        vals = []
        for i, row in enumerate(valid_rows):
            raw = row.get(hdr_key)
            try:
                val = float(raw) if raw is not None else float("nan")
            except (ValueError, TypeError):
                val = float("nan")
            delta = val - mjd_aligned[i] if np.isfinite(val) else float("nan")
            vals.append(delta)

        all_nan = all(not np.isfinite(v) for v in vals)
        if all_nan:
            continue

        color = "#7e22ce" if is_ref else "#e6820a"  # purple : orange
        fig = make_time_figure(
            title=f"{label} [{objname}]",
            height=200,
        )
        fig.yaxis.axis_label = "\u0394t [days]"
        fig.add_tools(
            HoverTool(
                tooltips=[
                    ("Date (UTC)", "@x{%F %T}"),
                    ("\u0394t [days]", "@y{0.000}"),
                ],
                formatters={"@x": "datetime"},
                mode="mouse",
            )
        )
        src = ColumnDataSource({"x": dts_ms, "y": vals})
        fig.scatter("x", "y", source=src, size=5, color=color, alpha=0.7)
        figures.append(fig)

    if not figures:
        return None
    return bk_column(figures, sizing_mode="stretch_width")


def _get_cdt_keys_from_preset(
    preset: Optional[Dict[str, Any]],
) -> List[tuple]:
    """
    Return list of (hdr_key, label, is_ref) tuples for CDT-style keys.

    Reads from ``preset['sci-headers']['ext']``.  Falls back to a
    built-in list if the preset is unavailable.
    """
    fallback = [
        ("EXT_CDTDARK", "DARK file", True),
        ("EXT_CDTBAD", "BADPIX file", False),
        ("EXT_CDTBACK", "BACKGROUND file", False),
        ("EXT_CDTORDP", "ORDER_PROFILE file", False),
        ("EXT_CDTLOCO", "LOCO file", False),
        ("EXT_CDTSHAPL", "Local shape file", False),
        ("EXT_CDTSHAPX", "Shape X file", True),
        ("EXT_CDTSHAPY", "Shape Y file", True),
        ("EXT_CDTFLAT", "FLAT file", False),
        ("EXT_CDTBLAZE", "BLAZE file", False),
        ("EXT_CDTWAVE", "Wave file", False),
        ("EXT_WAVETIME", "Wave sol", False),
    ]
    if not preset:
        return fallback
    ext = (preset.get("sci-headers") or preset.get("headers", {})).get(
        "ext", {}
    )
    if not isinstance(ext, dict) or not ext:
        return fallback
    result = []
    for hdr_key, entry in ext.items():
        if not isinstance(entry, dict):
            continue
        if not (
            hdr_key.startswith("EXT_CDT") or hdr_key == "EXT_WAVETIME"
        ):
            continue
        label = str(entry.get("label", hdr_key)).strip() or hdr_key
        is_ref = bool(entry.get("ref", False))
        result.append((hdr_key, label, is_ref))
    return result if result else fallback


# =============================================================================
# Telluric map (matplotlib, generated on demand)
# =============================================================================
def _fig_to_base64(fig) -> str:
    """Render a matplotlib figure to base64-encoded PNG and close it."""
    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=120,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def _build_tcorr_map(
    htable_rows: List[Dict[str, Any]],
    ftable_tcorr_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    objname: str,
) -> Optional[str]:
    """Telluric correction map (intensity + residuals, 2×2 grid).

    Requires SC1D FITS files accessible via paths and ftable_tcorr_rows.
    Returns a base64-encoded PNG string.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import gridspec
    from matplotlib.colors import ListedColormap

    # Get wavelength range from preset
    wave_range = preset.get("TcorrMapWave", [1716, 1726])
    if isinstance(wave_range, dict):
        wave_range = wave_range.get("value", [1716, 1726])
    wave_min, wave_max = float(wave_range[0]), float(wave_range[1])
    wave_diff = wave_max - wave_min
    # Derive SC1D file paths from ftable_tcorr_rows
    sc1d_paths = []
    for row in ftable_tcorr_rows:
        sc1d_path = _derive_sc1d_path(row, paths)
        if sc1d_path is not None:
            sc1d_paths.append(sc1d_path)
    if not sc1d_paths:
        return None
    # Load reference file
    try:
        ref_wave, ref_flux = _load_s1d_data(sc1d_paths[0])
    except Exception:
        return None
    if ref_wave is None:
        return None
    # Apply wavelength mask
    wave_mask = (ref_wave > wave_min - 0.5 * wave_diff) & (
        ref_wave < wave_max + 0.5 * wave_diff
    )
    ref_wave = ref_wave[wave_mask]
    if len(ref_wave) == 0:
        return None
    # Build intensity maps
    n_files = len(sc1d_paths)
    n_pix = int(np.sum(wave_mask))
    map2d = np.zeros((n_files, n_pix))
    bervs = np.zeros(n_files)
    qcc_pass = np.zeros((n_files, 1))
    rvoffset = np.zeros((n_files, 1))
    for it, sc1d_path in enumerate(sc1d_paths):
        if sc1d_path is None or not sc1d_path.exists():
            continue
        wave_i, flux_i, hdr_i = _load_s1d_data_with_header(sc1d_path)
        if wave_i is None:
            continue
        flux_masked = flux_i[wave_mask].astype(float)
        # Low-pass filter the spectrum
        lp = _lowpass_filter(flux_masked, 501)
        if lp is not None:
            map2d[it] = flux_masked / lp
        else:
            map2d[it] = flux_masked
        bervs[it] = float(hdr_i.get("BERV", 0.0))
        qc_all = str(hdr_i.get("QCC_ALL", "0"))
        qcc_pass[it] = 1 if qc_all.upper() in ("T", "TRUE", "1") else 0
        rv = float(hdr_i.get("MKT_ARV", 0.0))
        rvoffset[it] = 0.0 if np.isnan(rv) else rv
    # Compute median spectrum
    med = np.nanmedian(map2d, axis=0)
    valid = np.isfinite(med)
    if not np.any(valid):
        return None
    from scipy.interpolate import InterpolatedUnivariateSpline

    med_spl = InterpolatedUnivariateSpline(ref_wave[valid], med[valid], k=3)
    # Subtract median (corrected for stellar motion)
    map2d_star = np.array(map2d)
    for it in range(n_files):
        dv = bervs[it] - (rvoffset[it] / 1000.0)
        dvshift = 1.0 + dv * 1000.0 / 299792458.0
        map2d_star[it] -= med_spl(ref_wave / dvshift)
    # Plot
    binary_cmap = ListedColormap(["orange", "purple"])
    gridspec_kw = {"width_ratios": [40, 1, 1, 1], "height_ratios": [1, 1]}
    fig = plt.figure(figsize=(12, 12))
    fig.set_facecolor("white")
    gs = gridspec.GridSpec(2, 4, **gridspec_kw)
    main_1 = fig.add_subplot(gs[0, 0])
    main_2 = fig.add_subplot(gs[1, 0])
    qcc_1 = fig.add_subplot(gs[0, 1])
    qcc_2 = fig.add_subplot(gs[1, 1])
    cb_1 = fig.add_subplot(gs[0, 3])
    cb_2 = fig.add_subplot(gs[1, 3])
    extent = [ref_wave.min(), ref_wave.max(), 0, n_files]
    # Original data range
    p10, p90 = np.nanpercentile(map2d, [10, 90])
    mid = 0.5 * (p10 + p90)
    width = 3 * (p90 - p10)
    range1 = [mid - 0.5 * width, mid + 0.5 * width]
    im0 = main_1.imshow(
        map2d,
        aspect="auto",
        vmin=range1[0],
        vmax=range1[1],
        interpolation="nearest",
        extent=extent,
        origin="lower",
    )
    main_1.set_ylabel("Observation number")
    main_1.set_title("Telluric corrected s1d")
    main_1.set(xlim=[wave_min, wave_max])
    fig.colorbar(
        im0, cax=cb_1, orientation="vertical", label="Normalized\nIntensity"
    )
    cb_1.set_aspect("auto")
    qcc_1.imshow(
        qcc_pass,
        aspect="auto",
        cmap=binary_cmap,
        interpolation="nearest",
        origin="lower",
        vmin=0,
        vmax=1,
    )
    for pos in ("top", "right", "left", "bottom"):
        qcc_1.spines[pos].set_visible(False)
    qcc_1.tick_params(
        left=False, bottom=False, labelleft=False, labelbottom=False
    )
    qcc_1.set_xticks([])
    qcc_1.set_xlabel("QC", labelpad=10, loc="center")
    qcc_1.xaxis.set_label_position("top")
    # Residuals range
    p10, p90 = np.nanpercentile(map2d_star, [10, 90])
    mid = 0.5 * (p10 + p90)
    width = 3 * (p90 - p10)
    range2 = [mid - 0.5 * width, mid + 0.5 * width]
    im1 = main_2.imshow(
        map2d_star,
        aspect="auto",
        vmin=range2[0],
        vmax=range2[1],
        interpolation="nearest",
        extent=extent,
        origin="lower",
    )
    main_2.set_xlabel("Wavelength")
    main_2.set_ylabel("Observation number")
    main_2.set_title("Residuals to star median")
    main_2.set(xlim=[wave_min, wave_max])
    fig.colorbar(
        im1, cax=cb_2, orientation="vertical", label="Normalized\nResidual"
    )
    cb_2.set_aspect("auto")
    qcc_2.imshow(
        qcc_pass,
        aspect="auto",
        cmap=binary_cmap,
        interpolation="nearest",
        origin="lower",
        vmin=0,
        vmax=1,
    )
    qcc_2.axis("off")
    fig.subplots_adjust(
        hspace=0.15, wspace=0.01, left=0.1, right=0.9, bottom=0.05, top=0.9
    )
    fig.suptitle(f"Telluric Map [{objname}]")
    return _fig_to_base64(fig)


# =============================================================================
# SC1D helpers (for tcorr_map)
# =============================================================================
def _derive_sc1d_path(
    tcorr_row: Dict[str, Any], paths: Dict[str, str]
) -> Optional[Path]:
    """Derive SC1D path from a tcorr ftable row."""
    filename = str(tcorr_row.get("FILENAME", "") or "").strip()
    sc1d_filename = filename.replace("_e2dsff_tcorr_", "_s1d_v_tcorr_")
    if sc1d_filename == filename:
        return None
    block_kind = str(tcorr_row.get("BLOCK_KIND", "red") or "red").strip()
    path_key_map = {
        "raw": "PATH_RAW",
        "tmp": "PATH_PP",
        "calib": "PATH_CALIB",
        "red": "PATH_RED",
        "tellu": "PATH_TELLU",
        "out": "PATH_OUT",
        "lbl": "PATH_LBL",
    }
    path_key = path_key_map.get(block_kind, "PATH_RED")
    base_dir = paths.get(path_key)
    if not base_dir:
        return None
    obs_dir = str(tcorr_row.get("OBS_DIR", "") or "").strip()
    candidate = Path(base_dir) / obs_dir / sc1d_filename
    return candidate if candidate.exists() else None


def _load_s1d_data(path) -> tuple:
    """Load (wavelength, flux) from an S1D FITS BinTable (HDU index 1)."""
    try:
        from astropy.io import fits as _fits

        with _fits.open(str(path)) as hdul:
            dat = hdul[1].data
            wave = np.array(dat["wavelength"], dtype=float)
            flux = np.array(dat["flux"], dtype=float)
        return wave, flux
    except Exception:
        return None, None


def _load_s1d_data_with_header(path) -> tuple:
    """Load (wavelength, flux, header) from an S1D FITS file."""
    try:
        from astropy.io import fits as _fits

        with _fits.open(str(path)) as hdul:
            hdr = dict(hdul[0].header)
            dat = hdul[1].data
            wave = np.array(dat["wavelength"], dtype=float)
            flux = np.array(dat["flux"], dtype=float)
        return wave, flux, hdr
    except Exception:
        return None, None, {}


def _lowpass_filter(data: np.ndarray, width: int) -> Optional[np.ndarray]:
    """Simple low-pass filter using uniform convolution."""
    if len(data) < width:
        return None
    kernel = np.ones(width) / width
    # Pad to handle edges
    padded = np.pad(data, width // 2, mode="edge")
    filtered = np.convolve(padded, kernel, mode="same")
    return filtered[width // 2: width // 2 + len(data)]


from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.plots.plot_debug"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

PLOT_BACKGROUND_COLOR: str = base.PLOT_BACKGROUND_COLOR

# Debug plot definitions: key → (title, description)
DEBUG_PLOT_DEFS: Dict[str, Dict[str, str]] = {
    "extsmax": {
        "title": "Maximum Saturation Level",
        "description": (
            "Maximum saturation level measured at time of extraction."
        ),
    },
    "effron": {
        "title": "Effective Readout Noise",
        "description": ("Measured effective readout noise before extraction."),
    },
    "version": {
        "title": "APERO Processing Debug",
        "description": (
            "Plotting the version and processed date from the header from "
            "APERO. Note that offline reductions should lead to a straight "
            "line, while online reductions should be roughly a one-to-one "
            "with the Date axis."
        ),
    },
    "cdt": {
        "title": "Calibration Times",
        "description": (
            "Computed time between observation and calibration used. Some "
            "calibrations are reference calibrations (in purple) and thus "
            "diverge from the reference night, others should always be from "
            "the same night (orange) unless no calibration was taken that "
            "night in which case the closest calibration in time should have "
            "been used."
        ),
    },
    "tcorr_map": {
        "title": "Telluric Map",
        "description": (
            "Telluric map of e2dsff_tcorr_A files. Files are low-passed and "
            "corrected for the stars motion. The QC is displayed to the right "
            "of the image — in purple are the files that passed, in orange "
            "the files that failed."
        ),
    },
}


# =============================================================================
# Public API
# =============================================================================
def generate_debug_plots(
    htable_rows: List[Dict[str, Any]],
    objname: str,
    preset: Optional[Dict[str, Any]] = None,
    ftable_tcorr_rows: Optional[List[Dict[str, Any]]] = None,
    paths: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate all debug plots and return them as base64-encoded PNGs.

    :param htable_rows: list of htable row dicts (one per observation)
    :param objname: str, object name for plot titles
    :param preset: dict, instrument profile preset (for TcorrMapWave)
    :param ftable_tcorr_rows: list of ftable tcorr row dicts (for tcorr map)
    :param paths: dict mapping PATH_* keys to directory strings (for tcorr map)

    :return: dict with 'success', 'plots' (dict of plot_key → plot_info)
    :rtype: dict
    """
    if not htable_rows:
        return dict(success=False, plots={}, error="No htable data available.")
    plots: Dict[str, Any] = {}
    for key in ("extsmax", "effron", "version", "cdt"):
        try:
            image = _build_debug_plot(key, htable_rows, objname)
        except Exception as e:
            image = None
            plots[key] = _plot_entry(
                key, image=None, error=f"Error generating plot: {e}"
            )
            continue
        plots[key] = _plot_entry(key, image=image)
    # tcorr map (requires SC1D files — optional)
    if ftable_tcorr_rows and paths and preset:
        try:
            image = _build_tcorr_map(
                htable_rows, ftable_tcorr_rows, paths, preset, objname
            )
        except Exception:
            image = None
        plots["tcorr_map"] = _plot_entry("tcorr_map", image=image)
    return dict(success=True, plots=plots, error="")


def generate_single_debug_plot(
    plot_key: str,
    htable_rows: List[Dict[str, Any]],
    objname: str,
    preset: Optional[Dict[str, Any]] = None,
    ftable_tcorr_rows: Optional[List[Dict[str, Any]]] = None,
    paths: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate a single debug plot for the maximize view.

    Returns a dict compatible with the plot_payload format:
    ``{has_plot, script, div, message}``.
    """
    if not htable_rows:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No htable data available.",
        }
    try:
        if plot_key == "tcorr_map":
            if not ftable_tcorr_rows or not paths or not preset:
                return {
                    "has_plot": False,
                    "script": "",
                    "div": "",
                    "message": "Telluric map data unavailable.",
                }
            image = _build_tcorr_map(
                htable_rows, ftable_tcorr_rows, paths, preset, objname
            )
        else:
            image = _build_debug_plot(plot_key, htable_rows, objname)
    except Exception as e:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": f"Error generating plot: {e}",
        }
    if not image:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "Plot generation returned no image.",
        }
    defn = DEBUG_PLOT_DEFS.get(plot_key, {})
    title = defn.get("title", plot_key)
    div_html = (
        f'<div style="text-align:center;">'
        f'<img src="data:image/png;base64,{image}" '
        f'style="max-width:100%;height:auto;" '
        f'alt="{title}">'
        f"</div>"
    )
    return {"has_plot": True, "script": "", "div": div_html, "message": ""}


# =============================================================================
# Private helpers
# =============================================================================
def _plot_entry(key: str, image: Optional[str] = None, error: str = "") -> dict:
    """Build a standard plot info dict."""
    defn = DEBUG_PLOT_DEFS.get(key, {})
    return {
        "key": key,
        "title": defn.get("title", key),
        "description": defn.get("description", ""),
        "has_plot": image is not None,
        "image": image or "",
        "error": error,
    }


def _fig_to_base64(fig) -> str:
    """Render a matplotlib figure to base64-encoded PNG and close it."""
    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=120,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def _extract_mjd_datetimes(htable_rows: List[Dict[str, Any]]):
    """Extract MJD values and convert to matplotlib date numbers."""
    from astropy.time import Time as AstroTime

    mjd_vals = []
    for row in htable_rows:
        val = row.get("EXT_MJDMID")
        if val is not None:
            try:
                mjd_vals.append(float(val))
            except (ValueError, TypeError):
                pass
    if not mjd_vals:
        return None, None
    mjd_arr = np.array(mjd_vals)
    t = AstroTime(mjd_arr, format="mjd")
    return mjd_arr, t.plot_date


def _extract_column(
    htable_rows: List[Dict[str, Any]], key: str, dtype=float
) -> np.ndarray:
    """Extract a column from htable_rows as a numpy array."""
    vals = []
    for row in htable_rows:
        val = row.get(key)
        if val is not None:
            try:
                vals.append(dtype(val))
            except (ValueError, TypeError):
                vals.append(np.nan if dtype == float else val)
        else:
            vals.append(np.nan if dtype == float else None)
    return np.array(vals)


# =============================================================================
# Individual plot builders
# =============================================================================
def _build_debug_plot(
    plot_key: str, htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[str]:
    """Dispatch to the correct plot builder."""
    builders = {
        "extsmax": _build_extsmax_plot,
        "effron": _build_effron_plot,
        "version": _build_version_plot,
        "cdt": _build_cdt_plot,
    }
    builder = builders.get(plot_key)
    if builder is None:
        return None
    return builder(htable_rows, objname)


def _build_extsmax_plot(
    htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[str]:
    """Maximum saturation level vs time."""
    return _build_simple_mjd_plot(
        htable_rows,
        objname,
        column="EXT_EXTSMAX",
        ylabel="Maximum Saturation Level",
        title=f"Maximum Saturation Level [{objname}]",
    )


def _build_effron_plot(
    htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[str]:
    """Effective readout noise vs time."""
    return _build_simple_mjd_plot(
        htable_rows,
        objname,
        column="EXT_EFFRON",
        ylabel="Effective Readout Noise",
        title=f"Effective Readout Noise [{objname}]",
    )


def _build_simple_mjd_plot(
    htable_rows: List[Dict[str, Any]],
    objname: str,
    column: str,
    ylabel: str,
    title: str,
) -> Optional[str]:
    """Build a simple MJD time-series plot for a single column."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mjd_arr, plot_dates = _extract_mjd_datetimes(htable_rows)
    if plot_dates is None:
        return None
    values = _extract_column(htable_rows, column)
    if len(values) == 0 or np.all(np.isnan(values)):
        return None
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.set_facecolor("white")
    ax.set_facecolor(PLOT_BACKGROUND_COLOR)
    ax.grid(which="both", color="lightgray", ls="--")
    ax.plot_date(plot_dates, values, fmt=".", alpha=0.5)
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    fig.suptitle(title)
    fig.subplots_adjust(hspace=0, left=0.1, right=0.99, bottom=0.15, top=0.9)
    return _fig_to_base64(fig)


def _build_version_plot(
    htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[str]:
    """APERO version and processing date vs observation time."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from astropy.time import Time as AstroTime

    mjd_arr, plot_dates = _extract_mjd_datetimes(htable_rows)
    if plot_dates is None:
        return None
    # Extract version numbers (convert to numeric for plotting)
    versions_raw = _extract_column(htable_rows, "EXT_VERSION", dtype=str)
    version_nums = []
    for v in versions_raw:
        try:
            # Convert version like '0.8.106' to numeric 0.8106
            parts = str(v).split(".")
            if len(parts) >= 3:
                version_nums.append(
                    int(parts[0]) * 10000 + int(parts[1]) * 1000 + int(parts[2])
                )
            else:
                version_nums.append(np.nan)
        except (ValueError, TypeError):
            version_nums.append(np.nan)
    version_arr = np.array(version_nums, dtype=float)
    # Extract processing date (convert to MJD)
    pdate_raw = _extract_column(htable_rows, "EXT_PDATE", dtype=str)
    pdate_mjd = []
    for pd in pdate_raw:
        try:
            t = AstroTime(str(pd), format="iso")
            pdate_mjd.append(t.mjd)
        except Exception:
            pdate_mjd.append(np.nan)
    pdate_arr = np.array(pdate_mjd)
    fig, frames = plt.subplots(nrows=2, ncols=1, figsize=(12, 5), sharex=True)
    fig.set_facecolor("white")
    for frame in frames:
        frame.set_facecolor(PLOT_BACKGROUND_COLOR)
        frame.grid(which="both", color="lightgray", ls="--")
    # Plot version
    frames[0].plot_date(
        plot_dates, version_arr, fmt=".", alpha=0.5, label="Version"
    )
    frames[0].legend(loc=0)
    frames[0].set_ylabel("Version Number")
    # Plot processing date
    frames[1].plot_date(
        plot_dates, pdate_arr, fmt=".", alpha=0.5, label="Processing Date"
    )
    frames[1].set_xlabel("Date")
    frames[1].set_ylabel("MJD")
    frames[1].legend(loc=0)
    fig.suptitle(f"APERO Processing Debug [{objname}]")
    fig.subplots_adjust(hspace=0.05, left=0.1, right=0.99, bottom=0.12, top=0.9)
    return _fig_to_base64(fig)


def _build_cdt_plot(
    htable_rows: List[Dict[str, Any]], objname: str
) -> Optional[str]:
    """Calibration time deltas (CDT − MJD) for 12 calibration keys."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mjd_arr, plot_dates = _extract_mjd_datetimes(htable_rows)
    if plot_dates is None:
        return None
    # CDT keys and whether they are reference calibrations (purple)
    # or same-night calibrations (orange)
    cdt_keys = {
        "CDTDARK": True,
        "CDTBAD": False,
        "CDTBACK": False,
        "CDTORDP": False,
        "CDTLOCO": False,
        "CDTSHAPL": False,
        "CDTSHAPX": True,
        "CDTSHAPY": True,
        "CDTFLAT": False,
        "CDTBLAZE": False,
        "CDTWAVE": False,
        "WAVETIME": False,
    }
    fig, frames = plt.subplots(
        nrows=len(cdt_keys), ncols=1, figsize=(12, 24), sharex=True
    )
    fig.set_facecolor("white")
    for it, (key, is_ref) in enumerate(cdt_keys.items()):
        hdr_key = f"EXT_{key}"
        variable = _extract_column(htable_rows, hdr_key)
        color = "purple" if is_ref else "orange"
        frame = frames[it]
        frame.set_facecolor(PLOT_BACKGROUND_COLOR)
        frame.grid(which="both", color="lightgray", ls="--")
        frame.plot_date(
            plot_dates,
            variable - mjd_arr,
            color=color,
            fmt=".",
            alpha=0.5,
            label=key,
        )
        frame.set_ylabel(r"$\Delta$t [d]")
        frame.legend(loc=0)
    frames[-1].set_xlabel("Date")
    fig.suptitle(f"APERO Calibration Times [{objname}]")
    fig.subplots_adjust(hspace=0, left=0.1, right=0.99, bottom=0.03, top=0.97)
    return _fig_to_base64(fig)


def _build_tcorr_map(
    htable_rows: List[Dict[str, Any]],
    ftable_tcorr_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    preset: Dict[str, Any],
    objname: str,
) -> Optional[str]:
    """Telluric correction map (intensity + residuals, 2×2 grid).

    Requires SC1D FITS files accessible via paths and ftable_tcorr_rows.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import gridspec
    from matplotlib.colors import ListedColormap

    # Get wavelength range from preset
    wave_range = preset.get("TcorrMapWave", [1716, 1726])
    if isinstance(wave_range, dict):
        wave_range = wave_range.get("value", [1716, 1726])
    wave_min, wave_max = float(wave_range[0]), float(wave_range[1])
    wave_diff = wave_max - wave_min
    # Derive SC1D file paths from ftable_tcorr_rows
    sc1d_paths = []
    for row in ftable_tcorr_rows:
        sc1d_path = _derive_sc1d_path(row, paths)
        if sc1d_path is not None:
            sc1d_paths.append(sc1d_path)
    if not sc1d_paths:
        return None
    # Load reference file
    try:
        ref_wave, ref_flux = _load_s1d_data(sc1d_paths[0])
    except Exception:
        return None
    if ref_wave is None:
        return None
    # Apply wavelength mask
    wave_mask = (ref_wave > wave_min - 0.5 * wave_diff) & (
        ref_wave < wave_max + 0.5 * wave_diff
    )
    ref_wave = ref_wave[wave_mask]
    if len(ref_wave) == 0:
        return None
    # Build intensity maps
    n_files = len(sc1d_paths)
    n_pix = int(np.sum(wave_mask))
    map2d = np.zeros((n_files, n_pix))
    bervs = np.zeros(n_files)
    qcc_pass = np.zeros((n_files, 1))
    rvoffset = np.zeros((n_files, 1))
    for it, sc1d_path in enumerate(sc1d_paths):
        if sc1d_path is None or not sc1d_path.exists():
            continue
        wave_i, flux_i, hdr_i = _load_s1d_data_with_header(sc1d_path)
        if wave_i is None:
            continue
        flux_masked = flux_i[wave_mask].astype(float)
        # Low-pass filter the spectrum
        lp = _lowpass_filter(flux_masked, 501)
        if lp is not None:
            map2d[it] = flux_masked / lp
        else:
            map2d[it] = flux_masked
        bervs[it] = float(hdr_i.get("BERV", 0.0))
        qc_all = str(hdr_i.get("QCC_ALL", "0"))
        qcc_pass[it] = 1 if qc_all.upper() in ("T", "TRUE", "1") else 0
        rv = float(hdr_i.get("MKT_ARV", 0.0))
        rvoffset[it] = 0.0 if np.isnan(rv) else rv
    # Compute median spectrum
    med = np.nanmedian(map2d, axis=0)
    valid = np.isfinite(med)
    if not np.any(valid):
        return None
    from scipy.interpolate import InterpolatedUnivariateSpline

    med_spl = InterpolatedUnivariateSpline(ref_wave[valid], med[valid], k=3)
    # Subtract median (corrected for stellar motion)
    map2d_star = np.array(map2d)
    for it in range(n_files):
        dv = bervs[it] - (rvoffset[it] / 1000.0)
        dvshift = 1.0 + dv * 1000.0 / 299792458.0
        map2d_star[it] -= med_spl(ref_wave / dvshift)
    # Plot
    binary_cmap = ListedColormap(["orange", "purple"])
    gridspec_kw = {"width_ratios": [40, 1, 1, 1], "height_ratios": [1, 1]}
    fig = plt.figure(figsize=(12, 12))
    fig.set_facecolor("white")
    gs = gridspec.GridSpec(2, 4, **gridspec_kw)
    main_1 = fig.add_subplot(gs[0, 0])
    main_2 = fig.add_subplot(gs[1, 0])
    qcc_1 = fig.add_subplot(gs[0, 1])
    qcc_2 = fig.add_subplot(gs[1, 1])
    cb_1 = fig.add_subplot(gs[0, 3])
    cb_2 = fig.add_subplot(gs[1, 3])
    extent = [ref_wave.min(), ref_wave.max(), 0, n_files]
    # Original data range
    p10, p90 = np.nanpercentile(map2d, [10, 90])
    mid = 0.5 * (p10 + p90)
    width = 3 * (p90 - p10)
    range1 = [mid - 0.5 * width, mid + 0.5 * width]
    im0 = main_1.imshow(
        map2d,
        aspect="auto",
        vmin=range1[0],
        vmax=range1[1],
        interpolation="nearest",
        extent=extent,
        origin="lower",
    )
    main_1.set_ylabel("Observation number")
    main_1.set_title("Telluric corrected s1d")
    main_1.set(xlim=[wave_min, wave_max])
    fig.colorbar(
        im0, cax=cb_1, orientation="vertical", label="Normalized\nIntensity"
    )
    cb_1.set_aspect("auto")
    qcc_1.imshow(
        qcc_pass,
        aspect="auto",
        cmap=binary_cmap,
        interpolation="nearest",
        origin="lower",
        vmin=0,
        vmax=1,
    )
    for pos in ("top", "right", "left", "bottom"):
        qcc_1.spines[pos].set_visible(False)
    qcc_1.tick_params(
        left=False, bottom=False, labelleft=False, labelbottom=False
    )
    qcc_1.set_xticks([])
    qcc_1.set_xlabel("QC", labelpad=10, loc="center")
    qcc_1.xaxis.set_label_position("top")
    # Residuals range
    p10, p90 = np.nanpercentile(map2d_star, [10, 90])
    mid = 0.5 * (p10 + p90)
    width = 3 * (p90 - p10)
    range2 = [mid - 0.5 * width, mid + 0.5 * width]
    im1 = main_2.imshow(
        map2d_star,
        aspect="auto",
        vmin=range2[0],
        vmax=range2[1],
        interpolation="nearest",
        extent=extent,
        origin="lower",
    )
    main_2.set_xlabel("Wavelength")
    main_2.set_ylabel("Observation number")
    main_2.set_title("Residuals to star median")
    main_2.set(xlim=[wave_min, wave_max])
    fig.colorbar(
        im1, cax=cb_2, orientation="vertical", label="Normalized\nResidual"
    )
    cb_2.set_aspect("auto")
    qcc_2.imshow(
        qcc_pass,
        aspect="auto",
        cmap=binary_cmap,
        interpolation="nearest",
        origin="lower",
        vmin=0,
        vmax=1,
    )
    qcc_2.axis("off")
    fig.subplots_adjust(
        hspace=0.15, wspace=0.01, left=0.1, right=0.9, bottom=0.05, top=0.9
    )
    fig.suptitle(f"Telluric Map [{objname}]")
    return _fig_to_base64(fig)


# =============================================================================
# SC1D helpers (for tcorr_map)
# =============================================================================
def _derive_sc1d_path(
    tcorr_row: Dict[str, Any], paths: Dict[str, str]
) -> Optional[Path]:
    """Derive SC1D path from a tcorr ftable row."""
    filename = str(tcorr_row.get("FILENAME", "") or "").strip()
    sc1d_filename = filename.replace("_e2dsff_tcorr_", "_s1d_v_tcorr_")
    if sc1d_filename == filename:
        return None
    block_kind = str(tcorr_row.get("BLOCK_KIND", "red") or "red").strip()
    path_key_map = {
        "raw": "PATH_RAW",
        "tmp": "PATH_PP",
        "calib": "PATH_CALIB",
        "red": "PATH_RED",
        "tellu": "PATH_TELLU",
        "out": "PATH_OUT",
        "lbl": "PATH_LBL",
    }
    path_key = path_key_map.get(block_kind, "PATH_RED")
    base_dir = paths.get(path_key)
    if not base_dir:
        return None
    obs_dir = str(tcorr_row.get("OBS_DIR", "") or "").strip()
    candidate = Path(base_dir) / obs_dir / sc1d_filename
    return candidate if candidate.exists() else None


def _load_s1d_data(path) -> tuple:
    """Load (wavelength, flux) from an S1D FITS BinTable (HDU index 1)."""
    try:
        from astropy.io import fits as _fits

        with _fits.open(str(path)) as hdul:
            dat = hdul[1].data
            wave = np.array(dat["wavelength"], dtype=float)
            flux = np.array(dat["flux"], dtype=float)
        return wave, flux
    except Exception:
        return None, None


def _load_s1d_data_with_header(path) -> tuple:
    """Load (wavelength, flux, header) from an S1D FITS file."""
    try:
        from astropy.io import fits as _fits

        with _fits.open(str(path)) as hdul:
            hdr = dict(hdul[0].header)
            dat = hdul[1].data
            wave = np.array(dat["wavelength"], dtype=float)
            flux = np.array(dat["flux"], dtype=float)
        return wave, flux, hdr
    except Exception:
        return None, None, {}


def _lowpass_filter(data: np.ndarray, width: int) -> Optional[np.ndarray]:
    """Simple low-pass filter using uniform convolution."""
    if len(data) < width:
        return None
    kernel = np.ones(width) / width
    # Pad to handle edges
    padded = np.pad(data, width // 2, mode="edge")
    filtered = np.convolve(padded, kernel, mode="same")
    return filtered[width // 2: width // 2 + len(data)]
