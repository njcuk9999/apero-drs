#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Bokeh plot builders keyed by APERO KW_OUTPUT type for the
file-browser filename-click feature.

One function per output-type family.  Each function receives the
absolute path to a FITS (or RDB) file and returns a standard result
dict::

    {'has_plot': True,  'plot': <json_item dict>,  'title': str,
     'message': ''}
    {'has_plot': False, 'message': str}

The public interface is :func:`build_filename_plot_json` which
dispatches to the appropriate builder, and
:data:`PLOTABLE_OUTPUT_TYPES` which lists the output types that have
a plot defined here (filenames whose ``KW_OUTPUT`` is *not* in this
set should not be made clickable in the frontend).

Created on 2025-01-01

@author: cook
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from apero_ri.base import base
from apero_ri.plots.plot_general import mjd_to_datetime, plot_to_components

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.plots.plots_filename"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Maximum data points sent to the browser for large 2D arrays
_MAX_PTS: int = 30_000

# Background colour shared with the rest of the UI
_BG_COLOUR: str = base.PLOT_BACKGROUND_COLOR

# ---------------------------------------------------------------------------
# Output types that have a plot defined in this module.
# The file-browser JS uses this list to decide which filenames are
# clickable.
# ---------------------------------------------------------------------------
PLOTABLE_OUTPUT_TYPES: frozenset = frozenset(
    [
        "DRS_POST_E",
        "DRS_POST_T",
        "DRS_POST_S",
        "DRS_POST_P",
        "DRS_POST_V",
        "TELLU_TEMP",
        "TELLU_TEMP_S1DV",
        "TELLU_TEMP_S1DW",
        "LBL_RDB",
        "LBL_RDB2",
        "LBL_DRIFT",
        "LBL_RDB_DRIFT",
        "LBL_RDB2_DRIFT",
        "LBL_RDB_FITS",
        "LBL_FITS",
    ]
)


# =============================================================================
# Define shared helpers
# =============================================================================
def _no_plot(msg: str) -> Dict[str, Any]:
    """Return a standard 'no plot' result dict.

    :param msg: str, human-readable reason

    :return: dict with has_plot=False and message
    :rtype: dict
    """
    return {"has_plot": False, "message": msg}


def _make_spec_figure(title: str, height: int = 420) -> Any:
    """
    Return a Bokeh figure suitable for spectrum (wavelength vs flux)
    plots.

    :param title: str, figure title
    :param height: int, figure height in pixels

    :return: Bokeh Figure
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
        sizing_mode="stretch_width",
        background_fill_color=_BG_COLOUR,
    )
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    return fig


def _downsample(
    x: np.ndarray,
    y: np.ndarray,
    max_pts: int = _MAX_PTS,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Uniformly thin two arrays to at most *max_pts* points.

    :param x: numpy.ndarray, x values
    :param y: numpy.ndarray, y values
    :param max_pts: int, maximum number of points to keep

    :return: tuple (x_ds, y_ds) downsampled arrays
    :rtype: tuple[numpy.ndarray, numpy.ndarray]
    """
    n = len(x)
    if n <= max_pts:
        return x, y
    stride = max(1, n // max_pts)
    return x[::stride], y[::stride]


def _detect_fiber(hdul: Any, candidates: Tuple[str, ...]) -> Optional[str]:
    """
    Probe an open FITS HDUList for a spectrum fiber suffix.

    Tries common extensions ``Flux<fiber>`` in the order given by
    *candidates* and returns the first match, or ``None``.

    :param hdul: astropy.io.fits HDUList (already open)
    :param candidates: tuple of fiber strings to test

    :return: str fiber suffix or None
    :rtype: str | None
    """
    ext_names = [hdu.name.upper() for hdu in hdul]
    for fiber in candidates:
        if f"FLUX{fiber.upper()}" in ext_names:
            return fiber
    return None


# =============================================================================
# Define 2D spectrum (DRS_POST_E / DRS_POST_T) plot builder
# =============================================================================
def _build_2d_spectrum_plot(
    filepath: Path,
    kw_fiber: str,
    title: str,
) -> Dict[str, Any]:
    """
    Build a Bokeh plot for a 2D extracted spectrum FITS file
    (DRS_POST_E or DRS_POST_T).

    Reads ``Wave{fiber}``, ``Flux{fiber}``, ``Blaze{fiber}`` from the
    file and plots the blaze-normalised flux vs wavelength (raveled,
    downsampled).

    :param filepath: Path, absolute path to the FITS file
    :param kw_fiber: str, fiber suffix used in extension names
    :param title: str, plot title
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    try:
        from astropy.io import fits as _fits

        with _fits.open(str(filepath)) as hdul:
            fiber = _detect_fiber(hdul, (kw_fiber, "AB", "A", "B", "C", ""))
            if fiber is None:
                return _no_plot("Cannot detect fiber in FITS extensions.")
            wave = np.array(hdul[f"Wave{fiber}"].data, dtype=float).ravel()
            flux = np.array(hdul[f"Flux{fiber}"].data, dtype=float).ravel()
            blaze = np.array(hdul[f"Blaze{fiber}"].data, dtype=float).ravel()
    except Exception as exc:
        return _no_plot(f"Could not load FITS data: {exc}")
    # -------------------------------------------------------------------------
    # normalize by blaze (avoid dividing by zero / small values)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        blaze_safe = np.where(np.abs(blaze) > 1e-6, blaze, np.nan)
        norm_flux = flux / blaze_safe
    # -------------------------------------------------------------------------
    finite_mask = np.isfinite(wave) & np.isfinite(norm_flux)
    wave = wave[finite_mask]
    norm_flux = norm_flux[finite_mask]
    if len(wave) == 0:
        return _no_plot("No finite data points in spectrum.")
    wave, norm_flux = _downsample(wave, norm_flux)
    # -------------------------------------------------------------------------
    fig = _make_spec_figure(title)
    from bokeh.models import HoverTool

    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Wavelength", "@x{0.000} nm"),
                ("Flux", "@y{0.000}"),
            ],
            mode="mouse",
        )
    )
    fig.line(
        list(wave),
        list(norm_flux),
        line_color="black",
        line_width=0.8,
        alpha=0.85,
        legend_label="Normalised flux",
    )
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
    return {"has_plot": True, "fig": fig, "title": title, "message": ""}


# =============================================================================
# Define 1D S1D spectrum (DRS_POST_S) plot builder
# =============================================================================
def _build_s1d_spectrum_plot(
    filepath: Path,
    kw_fiber: str,
) -> Dict[str, Any]:
    """
    Build a Bokeh plot for a 1D S1D spectrum FITS file (DRS_POST_S).

    Reads ``Wave``, ``Flux{fiber}``, ``Flux{fiber}TelluCorrected``
    from the ``UniformVelocity`` binary table extension.

    :param filepath: Path, absolute path to the FITS file
    :param kw_fiber: str, fiber suffix
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    title = "APERO 1D Spectrum"
    try:
        from astropy.table import Table as _Table

        tbl = _Table.read(str(filepath), hdu="UniformVelocity")
        wave = np.array(tbl["Wave"], dtype=float)
        # try fiber-specific column, fall back to first numeric column
        flux_col = f"Flux{kw_fiber}"
        tcorr_col = f"Flux{kw_fiber}TelluCorrected"
        if flux_col not in tbl.colnames:
            # try without fiber
            for cname in tbl.colnames:
                if cname.startswith("Flux") and "Tellu" not in cname:
                    flux_col = cname
                    break
        if tcorr_col not in tbl.colnames:
            tcorr_col = None
        flux = np.array(tbl[flux_col], dtype=float)
        tcorr = np.array(tbl[tcorr_col], dtype=float) if tcorr_col else None
    except Exception as exc:
        return _no_plot(f"Could not load S1D data: {exc}")
    # -------------------------------------------------------------------------
    fig = _make_spec_figure(title)
    from bokeh.models import HoverTool

    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Wavelength", "@x{0.000} nm"),
                ("Flux", "@y{0.000}"),
            ],
            mode="mouse",
        )
    )
    wave_ds, flux_ds = _downsample(wave, flux)
    fig.line(
        list(wave_ds),
        list(flux_ds),
        line_color="black",
        line_width=0.8,
        alpha=0.85,
        legend_label="Extracted 1D",
    )
    if tcorr is not None:
        _, tcorr_ds = _downsample(wave, tcorr)
        fig.line(
            list(wave_ds),
            list(tcorr_ds),
            line_color="red",
            line_width=0.8,
            alpha=0.75,
            legend_label="Telluric corrected 1D",
        )
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
    return {"has_plot": True, "fig": fig, "title": title, "message": ""}


# =============================================================================
# Define polarimetry spectrum (DRS_POST_P) plot builder
# =============================================================================
def _build_polar_plot(
    filepath: Path,
    kw_fiber: str,
) -> Dict[str, Any]:
    """
    Build a Bokeh plot for a polarimetry FITS file (DRS_POST_P).

    Reads ``Wave{fiber}``, ``Pol``, ``StokesI``, ``Null1``, ``Null2``
    from the file.

    :param filepath: Path, absolute path to the FITS file
    :param kw_fiber: str, fiber suffix
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    title = "APERO Polarimetry Spectrum"
    try:
        from astropy.io import fits as _fits

        with _fits.open(str(filepath)) as hdul:
            fiber = _detect_fiber(hdul, (kw_fiber, "AB", "A", "B", "C", ""))
            wave = np.array(hdul[f"Wave{fiber}"].data, dtype=float).ravel()
            pol = np.array(hdul["Pol"].data, dtype=float).ravel()
            stokesi = np.array(hdul["StokesI"].data, dtype=float).ravel()
            null1 = np.array(hdul["Null1"].data, dtype=float).ravel()
            null2 = np.array(hdul["Null2"].data, dtype=float).ravel()
    except Exception as exc:
        return _no_plot(f"Could not load polarimetry data: {exc}")
    # -------------------------------------------------------------------------
    fig = _make_spec_figure(title)
    datasets = [
        ("Pol", pol, "black"),
        ("StokesI", stokesi, "blue"),
        ("Null1", null1, "orange"),
        ("Null2", null2, "purple"),
    ]
    for label, y_arr, color in datasets:
        finite_mask = np.isfinite(wave) & np.isfinite(y_arr)
        if not np.any(finite_mask):
            continue
        w_ds, y_ds = _downsample(wave[finite_mask], y_arr[finite_mask])
        fig.line(
            list(w_ds),
            list(y_ds),
            line_color=color,
            line_width=0.8,
            alpha=0.75,
            legend_label=label,
        )
    if fig.legend:
        fig.legend.location = "top_right"
        fig.legend.click_policy = "hide"
    return {"has_plot": True, "fig": fig, "title": title, "message": ""}


# =============================================================================
# Define CCF spectrum (DRS_POST_V) plot builder
# =============================================================================
def _build_ccf_plot(
    filepath: Path,
) -> Dict[str, Any]:
    """
    Build a Bokeh plot for a CCF FITS file (DRS_POST_V).

    Reads the ``CCF`` binary table, computes the median CCF across
    all orders and overlays 1σ / 2σ percentile bands.

    :param filepath: Path, absolute path to the FITS file
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    title = "APERO CCF Spectrum"
    try:
        from astropy.table import Table as _Table

        ccf_tbl = _Table.read(str(filepath), hdu="CCF")
        rv_vec = np.array(ccf_tbl["RV"], dtype=float)
        # discover CCF order columns (CCF00, CCF01, ...)
        ccf_cols = sorted(
            [c for c in ccf_tbl.colnames if re.match(r"^CCF\d+$", c)]
        )
        if not ccf_cols:
            return _no_plot("No CCF order columns found in table.")
        all_ccf = np.zeros((len(ccf_cols), len(rv_vec)))
        for i, col in enumerate(ccf_cols):
            row_arr = np.array(ccf_tbl[col], dtype=float)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                med = np.nanmedian(row_arr)
                if med > 0:
                    row_arr = row_arr / med
            all_ccf[i] = row_arr
    except Exception as exc:
        return _no_plot(f"Could not load CCF data: {exc}")
    # -------------------------------------------------------------------------
    lower1 = 100.0 * (0.5 - 0.6827 / 2.0)
    upper1 = 100.0 * (0.5 + 0.6827 / 2.0)
    lower2 = 100.0 * (0.5 - 0.9545 / 2.0)
    upper2 = 100.0 * (0.5 + 0.9545 / 2.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y1_1sig = np.nanpercentile(all_ccf, lower1, axis=0)
        y2_1sig = np.nanpercentile(all_ccf, upper1, axis=0)
        y1_2sig = np.nanpercentile(all_ccf, lower2, axis=0)
        y2_2sig = np.nanpercentile(all_ccf, upper2, axis=0)
        med_ccf = np.nanmedian(all_ccf, axis=0)
    # -------------------------------------------------------------------------
    from bokeh.models import (
        Band,
        ColumnDataSource,
        HoverTool,
        Legend,
        LegendItem,
    )
    from bokeh.plotting import figure as bk_figure

    fig = bk_figure(
        title=title,
        x_axis_label="RV [km/s]",
        y_axis_label="Normalized CCF",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=400,
        sizing_mode="stretch_width",
        background_fill_color=_BG_COLOUR,
    )
    fig.add_tools(
        HoverTool(
            tooltips=[
                ("RV", "@x{0.000} km/s"),
                ("CCF", "@y{0.0000}"),
            ],
            mode="mouse",
        )
    )
    # Set y-axis range: 2σ band extent + 20 % padding so bands are clearly
    # visible
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        finite_ccf = med_ccf[np.isfinite(med_ccf)]
        finite_2sig_lo = y1_2sig[np.isfinite(y1_2sig)]
        finite_2sig_hi = y2_2sig[np.isfinite(y2_2sig)]
    if len(finite_ccf) > 0 and len(finite_2sig_lo) > 0:
        y_lo = float(np.nanmin(finite_2sig_lo))
        y_hi = float(np.nanmax(finite_2sig_hi))
        y_pad = max((y_hi - y_lo) * 0.20, 0.02)
        fig.y_range.start = y_lo - y_pad
        fig.y_range.end = y_hi + y_pad
    x = list(rv_vec)
    src_2 = ColumnDataSource(
        dict(
            x=x,
            upper=list(y2_2sig),
            lower=list(y1_2sig),
        )
    )
    src_1 = ColumnDataSource(
        dict(
            x=x,
            upper=list(y2_1sig),
            lower=list(y1_1sig),
        )
    )
    r_2sig = fig.add_layout(
        Band(
            base="x",
            upper="upper",
            lower="lower",
            source=src_2,
            fill_color="orange",
            fill_alpha=0.4,
            line_color=None,
            level="underlay",
        )
    )
    r_1sig = fig.add_layout(
        Band(
            base="x",
            upper="upper",
            lower="lower",
            source=src_1,
            fill_color="red",
            fill_alpha=0.4,
            line_color=None,
            level="underlay",
        )
    )
    r_med = fig.line(
        x, list(med_ccf), line_color="black", line_width=1.2, alpha=0.95
    )
    # Band glyphs don't appear in the auto-legend; build it explicitly
    # using dummy patch glyphs so click-to-hide works correctly.
    p_2sig = fig.patch(
        [],
        [],
        fill_color="orange",
        fill_alpha=0.4,
        line_color=None,
        visible=False,
    )
    p_1sig = fig.patch(
        [], [], fill_color="red", fill_alpha=0.4, line_color=None, visible=False
    )
    legend = Legend(
        items=[
            LegendItem(label="Median CCF", renderers=[r_med]),
            LegendItem(label="1\u03c3 band", renderers=[p_1sig]),
            LegendItem(label="2\u03c3 band", renderers=[p_2sig]),
        ],
        location="top_right",
        click_policy="hide",
    )
    fig.add_layout(legend)
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    return {"has_plot": True, "fig": fig, "title": title, "message": ""}


# =============================================================================
# Define TELLU_TEMP (2D template) plot builder
# =============================================================================
def _build_tellu_temp_2d_plot(
    filepath: Path,
) -> Dict[str, Any]:
    """
    Build a Bokeh plot for a 2D telluric template FITS file
    (TELLU_TEMP).

    Uses pixel index as the x-axis since no wavelength array is
    embedded in this HDU.

    :param filepath: Path, absolute path to the FITS file
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    title = "APERO 2D Telluric Template"
    try:
        from astropy.io import fits as _fits

        spectrum = np.array(
            _fits.getdata(str(filepath), extname="TELLU_TEMP"),
            dtype=float,
        ).ravel()
    except Exception as exc:
        return _no_plot(f"Could not load TELLU_TEMP data: {exc}")
    # -------------------------------------------------------------------------
    xpos = np.arange(len(spectrum), dtype=float)
    finite_mask = np.isfinite(spectrum)
    xpos = xpos[finite_mask]
    spectrum = spectrum[finite_mask]
    if len(xpos) == 0:
        return _no_plot("No finite data points in template.")
    xpos, spectrum = _downsample(xpos, spectrum)
    # -------------------------------------------------------------------------
    from bokeh.plotting import figure as bk_figure

    fig = bk_figure(
        title=title,
        x_axis_label="Pixel index",
        y_axis_label="Flux",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=380,
        sizing_mode="stretch_width",
        background_fill_color=_BG_COLOUR,
    )
    fig.line(
        list(xpos),
        list(spectrum),
        line_color="black",
        line_width=0.8,
        alpha=0.8,
        legend_label="Template flux",
    )
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    if fig.legend:
        fig.legend.location = "top_right"
    return {"has_plot": True, "fig": fig, "title": title, "message": ""}


# =============================================================================
# Define TELLU_TEMP_S1DV / TELLU_TEMP_S1DW plot builder
# =============================================================================
def _build_tellu_s1d_plot(
    filepath: Path,
    hdu_name: str,
    title: str,
) -> Dict[str, Any]:
    """
    Build a Bokeh plot for a 1D telluric template FITS table
    (TELLU_TEMP_S1DV or TELLU_TEMP_S1DW).

    :param filepath: Path, absolute path to the FITS file
    :param hdu_name: str, HDU extension name (e.g. 'TELLU_TEMP_S1DV')
    :param title: str, figure title
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    try:
        from astropy.table import Table as _Table

        tbl = _Table.read(str(filepath), hdu=hdu_name)
        wave = np.array(tbl["wavelength"], dtype=float)
        flux = np.array(tbl["flux"], dtype=float)
    except Exception as exc:
        return _no_plot(f"Could not load {hdu_name} data: {exc}")
    # -------------------------------------------------------------------------
    finite_mask = np.isfinite(wave) & np.isfinite(flux)
    wave = wave[finite_mask]
    flux = flux[finite_mask]
    if len(wave) == 0:
        return _no_plot("No finite data points in template.")
    wave, flux = _downsample(wave, flux)
    fig = _make_spec_figure(title)
    from bokeh.models import HoverTool

    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Wavelength", "@x{0.000} nm"),
                ("Flux", "@y{0.000}"),
            ],
            mode="mouse",
        )
    )
    fig.line(
        list(wave),
        list(flux),
        line_color="black",
        line_width=0.8,
        alpha=0.85,
        legend_label="Template flux",
    )
    if fig.legend:
        fig.legend.location = "top_right"
    return {"has_plot": True, "fig": fig, "title": title, "message": ""}


# =============================================================================
# Define LBL RDB (time-series) plot builder
# =============================================================================
def _build_lbl_rdb_plot(
    filepath: Path,
    kw_output: str,
) -> Dict[str, Any]:
    """
    Build a Bokeh RV vs time plot for an LBL RDB file.

    Handles ascii (.rdb) and FITS (.fits HDU='RDB') formats.
    Uses the ``rjd`` column (treated as MJD) for dates and ``vrad``
    / ``svrad`` for velocities.

    :param filepath: Path, absolute path to the file
    :param kw_output: str, output type identifier (used for title)
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    title = f"LBL RV Time Series ({filepath.name})"
    try:
        from astropy.table import Table as _Table

        if kw_output == "LBL_RDB_FITS":
            tbl = _Table.read(str(filepath), format="fits", hdu="RDB")
        else:
            tbl = _Table.read(
                str(filepath), format="ascii.rdb", fast_reader=False
            )
        rjd = np.array([float(v) for v in tbl["rjd"]], dtype=float)
        vrad = np.array([float(v) for v in tbl["vrad"]], dtype=float)
        svrad = np.array([float(v) for v in tbl["svrad"]], dtype=float)
        reset_mask = np.zeros(len(rjd), dtype=bool)
        if "RESET_RV" in tbl.colnames:
            reset_mask = np.array([bool(int(v)) for v in tbl["RESET_RV"]])
    except Exception as exc:
        return _no_plot(f"Could not load LBL RDB data: {exc}")
    # -------------------------------------------------------------------------
    datetimes = np.array([mjd_to_datetime(r) for r in rjd])
    valid = np.array([dt is not None for dt in datetimes])
    if not np.any(valid):
        return _no_plot("No valid date values in RDB file.")
    dts = datetimes[valid]
    vrad_v = vrad[valid]
    svrad_v = svrad[valid]
    reset_v = reset_mask[valid]
    sort_idx = np.argsort([dt.timestamp() for dt in dts])
    dts_s = dts[sort_idx]
    vrad_s = vrad_v[sort_idx]
    svrad_s = svrad_v[sort_idx]
    reset_s = reset_v[sort_idx]
    # -------------------------------------------------------------------------
    # y-axis limits (similar to existing LBL plot)
    pp = np.nanpercentile(vrad_s, [10, 90])
    diff = float(pp[1] - pp[0])
    central = float(np.nanmean(pp))
    if diff < 1.0:
        diff = max(abs(central) * 0.01, 10.0)
    ylim: List[float] = [
        central - 1.5 * diff,
        central + 1.5 * diff,
    ]
    # -------------------------------------------------------------------------
    from bokeh.models import (
        ColumnDataSource,
        HoverTool,
        Range1d,
        Whisker,
    )
    from bokeh.plotting import figure as bk_figure

    fig = bk_figure(
        x_axis_type="datetime",
        title=title,
        x_axis_label="Date (UTC)",
        y_axis_label="vrad [m/s]",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        y_range=Range1d(ylim[0], ylim[1]),
        height=380,
        sizing_mode="stretch_width",
        background_fill_color=_BG_COLOUR,
    )
    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Date (UTC)", "@x{%F %T}"),
                ("vrad", "@y{0.0} m/s"),
            ],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
    )
    # -------------------------------------------------------------------------
    # normal points (not reset)
    good = ~reset_s
    if np.any(good):
        src_g = ColumnDataSource(
            dict(
                x=list(dts_s[good]),
                y=list(vrad_s[good]),
                upper=list(vrad_s[good] + svrad_s[good]),
                lower=list(vrad_s[good] - svrad_s[good]),
            )
        )
        fig.add_layout(
            Whisker(
                source=src_g,
                base="x",
                upper="upper",
                lower="lower",
                dimension="height",
                line_color="black",
                line_alpha=0.5,
                level="underlay",
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src_g,
            color="black",
            marker="circle",
            size=5,
            alpha=0.7,
            legend_label="RV",
        )
    # -------------------------------------------------------------------------
    # reset-RV points (different colour)
    if np.any(reset_s):
        src_r = ColumnDataSource(
            dict(
                x=list(dts_s[reset_s]),
                y=list(vrad_s[reset_s]),
                upper=list(vrad_s[reset_s] + svrad_s[reset_s]),
                lower=list(vrad_s[reset_s] - svrad_s[reset_s]),
            )
        )
        fig.add_layout(
            Whisker(
                source=src_r,
                base="x",
                upper="upper",
                lower="lower",
                dimension="height",
                line_color="orange",
                line_alpha=0.5,
                level="underlay",
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src_r,
            color="orange",
            marker="circle",
            size=5,
            alpha=0.7,
            legend_label="RV (reset)",
        )
    # -------------------------------------------------------------------------
    from bokeh.models import DatetimeTickFormatter

    fig.xaxis.formatter = DatetimeTickFormatter(
        days="%Y-%m-%d",
        months="%Y-%m",
        years="%Y",
    )
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    if fig.legend:
        fig.legend.location = "top_right"
        fig.legend.click_policy = "hide"
    return {"has_plot": True, "fig": fig, "title": title, "message": ""}


# =============================================================================
# Define LBL FITS (trumpet) plot builder
# =============================================================================
def _lbl_trumpet_panel(
    wave: np.ndarray,
    y: np.ndarray,
    ey: np.ndarray,
    mask: np.ndarray,
    title: str,
    y_label: str,
    on_color: str = "#1f4e79",
    off_color: str = "#6fa8dc",
    height: int = 320,
) -> Any:
    """
    Build a single Bokeh 'trumpet' panel (wavelength vs velocity
    derivative) for an LBL FITS file, mirroring the matplotlib
    ``lbl_trumpet_plot`` helper in ``visu_info_plots.py``.

    :param wave: numpy.ndarray, wavelength array [nm]
    :param y: numpy.ndarray, velocity-derivative values
    :param ey: numpy.ndarray, uncertainties
    :param mask: numpy.ndarray[bool], True = good measurement
    :param title: str, figure title
    :param y_label: str, y-axis label
    :param on_color: str, colour for good points
    :param off_color: str, colour for bad points (sigma > threshold)
    :param height: int, figure pixel height

    :return: Bokeh Figure
    :rtype: bokeh.plotting.figure
    """
    from bokeh.models import ColumnDataSource, HoverTool, Whisker
    from bokeh.plotting import figure as bk_figure

    # clip to percentile range
    finite_y = y[np.isfinite(y)]
    if len(finite_y) == 0:
        low, high = -1.0, 1.0
    else:
        low, high = np.nanpercentile(finite_y, [5.0, 95.0])
    median_val = float(np.nanmedian(y))

    fig = bk_figure(
        title=title,
        x_axis_label="Wavelength [nm]",
        y_axis_label=y_label,
        y_range=(low, high),
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        height=height,
        sizing_mode="stretch_width",
        background_fill_color=_BG_COLOUR,
    )
    fig.add_tools(
        HoverTool(
            tooltips=[
                ("Wavelength", "@x{0.000} nm"),
                (y_label, "@y{0.000}"),
            ],
            mode="mouse",
        )
    )
    # -------------------------------------------------------------------------
    # bad points (semi-transparent)
    bad_mask = ~mask & np.isfinite(y)
    if np.any(bad_mask):
        src_b = ColumnDataSource(
            dict(
                x=list(wave[bad_mask]),
                y=list(y[bad_mask]),
                upper=list(y[bad_mask] + ey[bad_mask]),
                lower=list(y[bad_mask] - ey[bad_mask]),
            )
        )
        fig.add_layout(
            Whisker(
                source=src_b,
                base="x",
                upper="upper",
                lower="lower",
                dimension="height",
                line_color=off_color,
                line_alpha=0.1,
                level="underlay",
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src_b,
            color=off_color,
            marker="circle",
            size=4,
            alpha=0.08,
            legend_label="σ > 300 m/s",
        )
    # -------------------------------------------------------------------------
    # good points
    good_mask = mask & np.isfinite(y)
    if np.any(good_mask):
        src_g = ColumnDataSource(
            dict(
                x=list(wave[good_mask]),
                y=list(y[good_mask]),
                upper=list(y[good_mask] + ey[good_mask]),
                lower=list(y[good_mask] - ey[good_mask]),
            )
        )
        fig.add_layout(
            Whisker(
                source=src_g,
                base="x",
                upper="upper",
                lower="lower",
                dimension="height",
                line_color=on_color,
                line_alpha=0.4,
                level="underlay",
            )
        )
        fig.scatter(
            "x",
            "y",
            source=src_g,
            color=on_color,
            marker="circle",
            size=5,
            alpha=0.5,
            legend_label="σ < 300 m/s",
        )
    # -------------------------------------------------------------------------
    # median line
    from bokeh.models import Span

    fig.add_layout(
        Span(
            location=median_val,
            dimension="width",
            line_color="red",
            line_dash="dashed",
            line_width=1.5,
        )
    )
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    if fig.legend:
        fig.legend.location = "top_right"
        fig.legend.click_policy = "hide"
    return fig


def _build_lbl_fits_plot(
    filepath: Path,
) -> Dict[str, Any]:
    """
    Build a three-panel Bokeh trumpet plot for an LBL FITS file
    (LBL_FITS).

    Reads ``WAVE_START``, ``WAVE_END``, ``dv``, ``sdv``, ``d2v``,
    ``sd2v``, ``d3v``, ``sd3v`` from the file and builds one panel
    per velocity derivative.

    :param filepath: Path, absolute path to the FITS file
    :param target_id: str, Bokeh embed target id

    :return: standard result dict
    :rtype: dict
    """
    title = f"LBL Velocities ({filepath.name})"
    try:
        from astropy.table import Table as _Table

        fits_tbl = _Table.read(str(filepath))
        wavestart = np.array(fits_tbl["WAVE_START"], dtype=float)
        waveend = np.array(fits_tbl["WAVE_END"], dtype=float)
        wave = 0.5 * (wavestart + waveend)
        dv = np.array(fits_tbl["dv"], dtype=float) / 1000.0
        sdv = np.array(fits_tbl["sdv"], dtype=float) / 1000.0
        d2v = np.array(fits_tbl["d2v"], dtype=float)
        sd2v = np.array(fits_tbl["sd2v"], dtype=float)
        d3v = np.array(fits_tbl["d3v"], dtype=float)
        sd3v = np.array(fits_tbl["sd3v"], dtype=float)
    except Exception as exc:
        return _no_plot(f"Could not load LBL FITS data: {exc}")
    # -------------------------------------------------------------------------
    mask = sdv < (300.0 / 1000.0)  # sdv < 300 m/s threshold in km/s
    fig1 = _lbl_trumpet_panel(
        wave,
        dv,
        sdv,
        mask,
        title="dv vs Wavelength",
        y_label="dv [km/s]",
        on_color="#1f4e79",
        off_color="#6fa8dc",
    )
    fig2 = _lbl_trumpet_panel(
        wave,
        d2v,
        sd2v,
        mask,
        title="d2v vs Wavelength",
        y_label="d2v",
        on_color="#b45f06",
        off_color="#f6b26b",
    )
    fig3 = _lbl_trumpet_panel(
        wave,
        d3v,
        sd3v,
        mask,
        title="d3v vs Wavelength",
        y_label="d3v",
        on_color="#38761d",
        off_color="#93c47d",
    )
    from bokeh.layouts import column as bk_column

    layout = bk_column([fig1, fig2, fig3])
    return {"has_plot": True, "fig": layout, "title": title, "message": ""}


# =============================================================================
# Define public dispatch function
# =============================================================================
def build_filename_plot_json(
    filepath: Path,
    kw_output: str,
    kw_fiber: str = "AB",
) -> Dict[str, Any]:
    """
    Build a Bokeh plot for the given file, dispatching to the
    appropriate builder based on *kw_output*.

    Returns a dict with ``script`` and ``div`` HTML strings for
    direct injection (Bokeh components approach), avoiding the
    json_item / embed_item path that can produce stale model
    references in long-running server processes.

    :param filepath: Path, absolute path to the file on disk
    :param kw_output: str, APERO output type keyword (e.g. 'DRS_POST_E')
    :param kw_fiber: str, fiber suffix for FITS extension names

    :return: standard result dict (see module docstring)
    :rtype: dict
    """
    if not filepath.is_file():
        return _no_plot(f"File not found: {filepath}")

    kw_output = kw_output.strip().upper()

    if kw_output not in PLOTABLE_OUTPUT_TYPES:
        return _no_plot(f"No plot defined for output type: {kw_output}")

    try:
        if kw_output == "DRS_POST_E":
            result = _build_2d_spectrum_plot(
                filepath,
                kw_fiber,
                "APERO Extracted Spectrum",
            )
        elif kw_output == "DRS_POST_T":
            result = _build_2d_spectrum_plot(
                filepath,
                kw_fiber,
                "APERO Normalised Spectrum (telluric corrected)",
            )
        elif kw_output == "DRS_POST_S":
            result = _build_s1d_spectrum_plot(
                filepath,
                kw_fiber,
            )
        elif kw_output == "DRS_POST_P":
            result = _build_polar_plot(filepath, kw_fiber)
        elif kw_output == "DRS_POST_V":
            result = _build_ccf_plot(filepath)
        elif kw_output == "TELLU_TEMP":
            result = _build_tellu_temp_2d_plot(filepath)
        elif kw_output == "TELLU_TEMP_S1DV":
            result = _build_tellu_s1d_plot(
                filepath,
                "TELLU_TEMP_S1DV",
                "APERO 1D Telluric Template [v]",
            )
        elif kw_output == "TELLU_TEMP_S1DW":
            result = _build_tellu_s1d_plot(
                filepath,
                "TELLU_TEMP_S1DW",
                "APERO 1D Telluric Template [w]",
            )
        elif kw_output in (
            "LBL_RDB",
            "LBL_RDB2",
            "LBL_DRIFT",
            "LBL_RDB_DRIFT",
            "LBL_RDB2_DRIFT",
            "LBL_RDB_FITS",
        ):
            result = _build_lbl_rdb_plot(filepath, kw_output)
        elif kw_output == "LBL_FITS":
            result = _build_lbl_fits_plot(filepath)
        else:
            return _no_plot(f"No handler for output type: {kw_output}")
    except Exception as exc:
        return _no_plot(f"Plot build error: {exc}")

    if not result.get("has_plot"):
        return result

    script, div = plot_to_components(result["fig"])
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "title": result.get("title", ""),
        "message": "",
    }


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
