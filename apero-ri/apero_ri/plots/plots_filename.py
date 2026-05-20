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

import base64
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

# Maximum display side-length (pixels) for 2D FITS frame images.
# Larger images are stride-downsampled before embedding.
_FRAME_MAX_PX: int = 1024

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
        # extracted 2D spectra
        "EXT_E2DS",
        "EXT_E2DS_FF",
        "EXT_E2DS_LL",
        # extracted 1D spectra
        "EXT_S1D_W",
        "EXT_S1D_V",
        # telluric-corrected 2D spectra
        "TELLU_OBJ",
        "TELLU_RECON",
        "TELLU_SCLEAN",
        # telluric-corrected 1D spectra
        "SC1D_W_FILE",
        "SC1D_V_FILE",
        "RC1D_W_FILE",
        "RC1D_V_FILE",
        # telluric templates
        "TELLU_TEMP",
        "TELLU_TEMP_S1DV",
        "TELLU_TEMP_S1DW",
        # LBL
        "LBL_RDB",
        "LBL_RDB2",
        "LBL_DRIFT",
        "LBL_RDB_DRIFT",
        "LBL_RDB2_DRIFT",
        "LBL_RDB_FITS",
        "LBL_FITS",
    ]
)

# KW_OUTPUT prefixes whose files are shown via the 2D frame viewer.
# Any type whose name *starts with* one of these strings is plotable.
FRAME_OUTPUT_PREFIXES: Tuple[str, ...] = ("RAW_", "DRS_PP")


def _is_plotable(kw_output: str) -> bool:
    """Return True if *kw_output* has a plot defined in this module.

    Exact output types are in :data:`PLOTABLE_OUTPUT_TYPES`.
    Output types whose names start with a prefix in
    :data:`FRAME_OUTPUT_PREFIXES` are also plotable (DS9-style frame
    viewer).

    :param kw_output: str, upper-cased KW_OUTPUT value
    :return: bool
    :rtype: bool
    """
    if kw_output in PLOTABLE_OUTPUT_TYPES:
        return True
    return any(kw_output.startswith(p) for p in FRAME_OUTPUT_PREFIXES)


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
# Define raw 1D extracted spectrum plot builder
# (EXT_S1D_W, EXT_S1D_V, SC1D_W_FILE, SC1D_V_FILE,
#  RC1D_W_FILE, RC1D_V_FILE)
# =============================================================================
def _build_s1d_raw_plot(
    filepath: Path,
    title: str,
) -> Dict[str, Any]:
    """
    Build a simple Bokeh wavelength vs flux line plot for raw APERO
    1D extracted spectrum files.

    Tries to read ``wavelength`` and ``flux`` columns from the first
    binary FITS table extension.

    :param filepath: Path, absolute path to the FITS file
    :param title: str, figure title

    :return: standard result dict
    :rtype: dict
    """
    wave: Optional[np.ndarray] = None
    flux: Optional[np.ndarray] = None
    try:
        from astropy.io import fits as _fits
        from astropy.table import Table as _Table

        with _fits.open(str(filepath)) as hdul:
            for hdu in hdul:
                if not hasattr(hdu, "columns"):
                    continue
                cols = [c.name.lower() for c in hdu.columns]
                if "wavelength" in cols and "flux" in cols:
                    tbl = _Table(hdu.data)
                    wave = np.array(tbl["wavelength"], dtype=float)
                    flux = np.array(tbl["flux"], dtype=float)
                    break
    except Exception as exc:
        return _no_plot(f"Could not load S1D data: {exc}")
    if wave is None or flux is None:
        return _no_plot(
            "No binary table with 'wavelength'/'flux' columns found."
        )
    finite_mask = np.isfinite(wave) & np.isfinite(flux)
    wave = wave[finite_mask]
    flux = flux[finite_mask]
    if len(wave) == 0:
        return _no_plot("No finite data points in spectrum.")
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
        legend_label="Flux",
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
# JS callback code for the interactive 2D frame viewer
# =============================================================================
# _FRAME_JS_UPDATE  – main update (interval → stretch → flip → rotate → emit)
# _FRAME_JS_RESET_PREFIX – reset widgets to defaults then run update
#
# Variable names injected via CustomJS args:
#   b64_data, orig_rows, orig_cols, data_min, data_max, zs_lo, zs_hi
#   source, fig_xr, fig_yr
#   sel_interval, sel_stretch, sel_rotate, sel_cmap, sel_flip
#   txt_pct, txt_pct_lo, txt_pct_hi, txt_vmin, txt_vmax, txt_stretch_a
#   mapper, _cmap_palettes
#   default_int, default_str, default_rot, default_pct, default_pct_lo,
#   default_pct_hi, default_vmin, default_vmax, default_sa, default_cmap,
#   default_flip
# =============================================================================
_FRAME_JS_UPDATE: str = """
// 0. Update colormap palette.
mapper.palette = _cmap_palettes[sel_cmap.value] || _cmap_palettes['gray'];

// 1. Decode & cache raw Float32 data (avoid re-decode on every event).
var _ck = 'af_' + source.id;
if (!window[_ck]) {
    var _b = atob(b64_data);
    var _buf = new ArrayBuffer(_b.length);
    var _u8  = new Uint8Array(_buf);
    for (var _i = 0; _i < _b.length; _i++) { _u8[_i] = _b.charCodeAt(_i); }
    window[_ck] = new Float32Array(_buf);
}
var raw = window[_ck];

// 2. Interval widget visibility.
var iMode = sel_interval.value;
txt_pct.visible    = (iMode === 'percentile');
txt_pct_lo.visible = (iMode === 'asymmetric');
txt_pct_hi.visible = (iMode === 'asymmetric');
txt_vmin.visible   = (iMode === 'manual');
txt_vmax.visible   = (iMode === 'manual');

// 3. Stretch param visibility + label.
var sMode = sel_stretch.value;
var sHasP = (sMode === 'log' || sMode === 'asinh' ||
             sMode === 'sinh' || sMode === 'power');
txt_stretch_a.visible = sHasP;
if      (sMode === 'log')                     txt_stretch_a.title = 'a  (default: 1000)';
else if (sMode === 'asinh' || sMode === 'sinh') txt_stretch_a.title = 'a  (default: 0.1)';
else if (sMode === 'power')                   txt_stretch_a.title = 'index  (default: 1.5)';

// 4. Sample-based percentile helper.
function _pct(arr, p) {
    var step = Math.max(1, Math.floor(arr.length / 50000));
    var s = [];
    for (var ii = 0; ii < arr.length; ii += step) {
        if (isFinite(arr[ii])) s.push(arr[ii]);
    }
    if (!s.length) return 0;
    s.sort(function(a, b) { return a - b; });
    var ix = (p / 100) * (s.length - 1);
    var lo = Math.floor(ix), hi = Math.ceil(ix);
    return (lo === hi) ? s[lo] : s[lo] + (s[hi] - s[lo]) * (ix - lo);
}

// 5. Compute vmin / vmax from selected interval.
var vmin, vmax;
if (iMode === 'minmax') {
    var mn = Infinity, mx = -Infinity;
    for (var ii = 0; ii < raw.length; ii++) {
        var v = raw[ii];
        if (isFinite(v)) { if (v < mn) mn = v; if (v > mx) mx = v; }
    }
    vmin = mn; vmax = mx;
} else if (iMode === 'zscale') {
    vmin = zs_lo; vmax = zs_hi;
} else if (iMode === 'percentile') {
    var pv = parseFloat(txt_pct.value);
    if (!isFinite(pv) || pv <= 0 || pv > 100) pv = 99;
    vmin = _pct(raw, (100 - pv) / 2);
    vmax = _pct(raw, (100 + pv) / 2);
} else if (iMode === 'asymmetric') {
    var plo = parseFloat(txt_pct_lo.value); if (!isFinite(plo)) plo = 1;
    var phi = parseFloat(txt_pct_hi.value); if (!isFinite(phi)) phi = 99;
    vmin = _pct(raw, plo); vmax = _pct(raw, phi);
} else if (iMode === 'manual') {
    vmin = parseFloat(txt_vmin.value); vmax = parseFloat(txt_vmax.value);
    if (!isFinite(vmin)) vmin = data_min;
    if (!isFinite(vmax)) vmax = data_max;
} else {
    vmin = data_min; vmax = data_max;
}
if (!isFinite(vmin) || !isFinite(vmax) || vmin >= vmax) {
    vmin = data_min; vmax = (data_max > data_min) ? data_max : data_min + 1;
}

// 6. Normalize raw to [0, 1].
var nd  = new Float32Array(raw.length);
var rng = vmax - vmin;
for (var ni = 0; ni < raw.length; ni++) {
    var nv = (raw[ni] - vmin) / rng;
    nd[ni] = (!isFinite(nv)) ? 0 : (nv < 0 ? 0 : (nv > 1 ? 1 : nv));
}

// 7. Apply stretch.
var sa = parseFloat(txt_stretch_a.value);
if (sMode === 'sqrt') {
    for (var si = 0; si < nd.length; si++) nd[si] = Math.sqrt(nd[si]);
} else if (sMode === 'squared') {
    for (var si = 0; si < nd.length; si++) { var sv = nd[si]; nd[si] = sv * sv; }
} else if (sMode === 'log') {
    var lA = (isFinite(sa) && sa > 0) ? sa : 1000;
    var lD = Math.log(lA + 1);
    for (var si = 0; si < nd.length; si++) nd[si] = Math.log(lA * nd[si] + 1) / lD;
} else if (sMode === 'asinh') {
    var aA = (isFinite(sa) && sa > 0) ? sa : 0.1;
    var aD = Math.log(1 / aA + Math.sqrt(1 / (aA * aA) + 1));
    for (var si = 0; si < nd.length; si++) {
        var sv = nd[si];
        nd[si] = Math.log(sv / aA + Math.sqrt(sv * sv / (aA * aA) + 1)) / aD;
    }
} else if (sMode === 'sinh') {
    var shA = (isFinite(sa) && sa > 0) ? sa : 0.1;
    var shD = Math.sinh(1 / shA);
    for (var si = 0; si < nd.length; si++) nd[si] = Math.sinh(nd[si] / shA) / shD;
} else if (sMode === 'power') {
    var pI = (isFinite(sa) && sa > 0) ? sa : 1.5;
    for (var si = 0; si < nd.length; si++) nd[si] = Math.pow(nd[si], pI);
}
// Post-stretch clip.
for (var ci = 0; ci < nd.length; ci++) {
    var cv = nd[ci];
    nd[ci] = (!isFinite(cv)) ? 0 : (cv < 0 ? 0 : (cv > 1 ? 1 : cv));
}

// 8. Apply Flip X / Flip Y.
var imgR = orig_rows, imgC = orig_cols, imgD = nd;
var fMode = sel_flip.value;
if (fMode === 'x' || fMode === 'both') {
    var fx = new Float32Array(imgR * imgC);
    for (var r = 0; r < imgR; r++) {
        for (var c = 0; c < imgC; c++) {
            fx[r * imgC + c] = imgD[r * imgC + (imgC - 1 - c)];
        }
    }
    imgD = fx;
}
if (fMode === 'y' || fMode === 'both') {
    var fy = new Float32Array(imgR * imgC);
    for (var r = 0; r < imgR; r++) {
        for (var c = 0; c < imgC; c++) {
            fy[r * imgC + c] = imgD[(imgR - 1 - r) * imgC + c];
        }
    }
    imgD = fy;
}

// Apply rotation (CCW in 90° steps).
// 90° CCW: out[i][j] = in[j][imgC-1-i], new shape (imgC × imgR)
var turns = ((parseInt(sel_rotate.value) || 0) / 90 + 4) % 4;
for (var t = 0; t < turns; t++) {
    var rR = imgC, rC = imgR;
    var rot = new Float32Array(rR * rC);
    for (var ri = 0; ri < rR; ri++) {
        for (var rj = 0; rj < rC; rj++) {
            rot[ri * rC + rj] = imgD[rj * imgC + (imgC - 1 - ri)];
        }
    }
    imgD = rot; imgR = rR; imgC = rC;
}

// 9. Attach Bokeh NDArray-compatible metadata so the image glyph
//    _set_data() assertion (img.dimension == 2) passes.  Bokeh
//    Float32NDArray extends Float32Array and sets these three
//    properties in its constructor; we replicate that here so we
//    can pass imgD directly without an extra copy.
imgD['shape']     = [imgR, imgC];
imgD['dimension'] = 2;
imgD['dtype']     = 'float32';

// 10. Push to Bokeh source and update axis ranges.
source.data = { image: [imgD], x: [0], y: [0], dw: [imgC], dh: [imgR] };
source.change.emit();
fig_xr.start = 0; fig_xr.end = imgC;
fig_yr.start = 0; fig_yr.end = imgR;
"""

_FRAME_JS_RESET_PREFIX: str = """
sel_interval.value  = default_int;
sel_stretch.value   = default_str;
sel_rotate.value    = default_rot;
txt_pct.value       = default_pct;
txt_pct_lo.value    = default_pct_lo;
txt_pct_hi.value    = default_pct_hi;
txt_vmin.value      = default_vmin;
txt_vmax.value      = default_vmax;
txt_stretch_a.value = default_sa;
sel_flip.value      = default_flip;
sel_cmap.value      = default_cmap;
"""


# =============================================================================
# Define 2D FITS frame (RAW_* / DRS_PP*) plot builder
# =============================================================================
def _build_frame_plot(
    filepath: Path,
    match_aspect: bool = True,
    pref_extnames: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build an interactive DS9-style 2D FITS frame viewer.

    Reads the first 2D (or first slice of ≥3D) image HDU, downsamples
    it to at most :data:`_FRAME_MAX_PX` pixels on each axis, and
    produces a Bokeh figure with interactive controls for:

    * **Interval** – MinMax, ZScale, Percentile, Asymmetric Percentile,
      Manual
    * **Stretch** – Linear, Sqrt, Log, Squared, Asinh, Sinh, Power
      (with editable *a* / *index* parameter where applicable)
    * **Flip X / Flip Y** – per-axis mirror
    * **Rotate** – 0, 90, 180, 270, 360° (counter-clockwise)
    * **Reset** – restores defaults (MinMax + Linear, no transforms)

    All normalization and transforms run in the browser via Bokeh
    CustomJS so the page needs no server round-trip when the user
    changes a control.

    :param filepath: Path, absolute path to the FITS file
    :param match_aspect: bool, if True preserve pixel aspect ratio
        (square pixels).  Set False for e2ds-style images where the
        y-axis (orders) should be stretched to fill the display.
    :param pref_extnames: optional list of HDU extension names to try
        before falling back to the first 2D image HDU.
    :return: standard result dict
    :rtype: dict
    """
    # ------------------------------------------------------------------
    # 1. Load first 2D image extension.
    # ------------------------------------------------------------------
    try:
        from astropy.io import fits as _fits

        with _fits.open(str(filepath)) as hdul:
            data: Optional[np.ndarray] = None
            orig_shape = (0, 0)
            # Try preferred extension names first.
            if pref_extnames:
                for _ext in pref_extnames:
                    try:
                        _hdata = hdul[_ext].data
                        if _hdata is not None:
                            d = np.asarray(_hdata, dtype=float)
                            if d.ndim == 2:
                                data = d
                                orig_shape = d.shape
                                break
                    except KeyError:
                        continue
            # Fall back to first 2D HDU.
            if data is None:
                for hdu in hdul:
                    if hdu.data is None:
                        continue
                    d = np.asarray(hdu.data, dtype=float)
                    if d.ndim == 2:
                        data = d
                        orig_shape = d.shape
                        break
                    elif d.ndim == 3:
                        data = d[0].astype(float)
                        orig_shape = data.shape
                        break
                    elif d.ndim > 3:
                        flat3 = d.reshape(-1, d.shape[-2], d.shape[-1])
                        data = flat3[0].astype(float)
                        orig_shape = data.shape
                        break
    except Exception as exc:
        return _no_plot(f"Could not load FITS data: {exc}")

    if data is None:
        return _no_plot("No 2D image data found in FITS file.")

    orig_h, orig_w = orig_shape

    # ------------------------------------------------------------------
    # 2. Use full resolution (no downsampling).
    # ------------------------------------------------------------------
    stride = 1
    disp = data.copy()
    disp_h, disp_w = disp.shape

    # ------------------------------------------------------------------
    # 3. Compute display statistics.
    # ------------------------------------------------------------------
    finite = disp[np.isfinite(disp)]
    if len(finite) == 0:
        return _no_plot("No finite data in image.")

    data_min = float(np.nanmin(finite))
    data_max = float(np.nanmax(finite))

    try:
        from astropy.visualization import ZScaleInterval as _ZSI

        _zs = _ZSI()
        zs_lo = float(_zs.get_limits(disp)[0])
        zs_hi = float(_zs.get_limits(disp)[1])
    except Exception:
        zs_lo, zs_hi = data_min, data_max

    # ------------------------------------------------------------------
    # 4. Encode display data as base64 Float32LE (row-major).
    # ------------------------------------------------------------------
    disp_clean = np.where(
        np.isfinite(disp), disp, data_min
    ).astype(np.float32)
    b64_data = base64.b64encode(disp_clean.tobytes()).decode("ascii")

    # ------------------------------------------------------------------
    # 5. Compute initial display image: ZScale + Sqrt, float64.
    #    float64 is required so Bokeh serialises it as a proper 2D
    #    NDArray (img.dimension == 2) without needing a DocumentReady
    #    JS workaround.
    # ------------------------------------------------------------------
    _zs_lo = zs_lo if zs_hi > zs_lo else data_min
    _zs_hi = zs_hi if zs_hi > zs_lo else data_max
    _zs_scale = _zs_hi - _zs_lo if _zs_hi > _zs_lo else 1.0
    _norm64 = np.clip(
        (disp_clean.astype(np.float64) - _zs_lo) / _zs_scale,
        0.0, 1.0,
    )
    norm_init = np.sqrt(_norm64)

    # ------------------------------------------------------------------
    # 6. Build Bokeh layout.
    # ------------------------------------------------------------------
    from bokeh.layouts import column as bk_column
    from bokeh.layouts import row as bk_row
    from bokeh.models import (
        Button,
        ColumnDataSource,
        CustomJS,
        LinearColorMapper,
        Select,
        TextInput,
    )
    from bokeh.palettes import (
        gray as bk_gray,
        viridis as bk_viridis,
        inferno as bk_inferno,
        plasma as bk_plasma,
        magma as bk_magma,
        turbo as bk_turbo,
    )
    from bokeh.plotting import figure as bk_figure

    # Bokeh serialises a float64 2D numpy array as a proper NDArray
    # with dimension=2, so the image glyph renders correctly without
    # any DocumentReady workaround.
    src = ColumnDataSource(
        data={
            "image": [norm_init],
            "x": [0.0],
            "y": [0.0],
            "dw": [float(disp_w)],
            "dh": [float(disp_h)],
        }
    )

    palette = bk_inferno(256)
    mapper = LinearColorMapper(palette=palette, low=0.0, high=1.0)

    _ds_note = (
        f"  \u2192 {disp_w}\u00d7{disp_h} displayed"
        if stride > 1
        else ""
    )
    fig = bk_figure(
        title=(
            f"{filepath.name}  "
            f"[{orig_w}\u00d7{orig_h} px]{_ds_note}"
        ),
        x_range=(0.0, float(disp_w)),
        y_range=(0.0, float(disp_h)),
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        match_aspect=match_aspect,
        height=500,
        sizing_mode="stretch_width",
        background_fill_color=_BG_COLOUR,
    )
    fig.image(
        image="image",
        x="x",
        y="y",
        dw="dw",
        dh="dh",
        color_mapper=mapper,
        source=src,
    )
    fig.axis.visible = False
    fig.grid.visible = False

    # --- Interval controls ---
    sel_interval = Select(
        title="Interval",
        value="zscale",
        options=[
            ("minmax", "MinMax"),
            ("zscale", "ZScale"),
            ("percentile", "Percentile"),
            ("asymmetric", "Asymmetric Percentile"),
            ("manual", "Manual"),
        ],
        width=210,
    )
    txt_pct = TextInput(
        title="Percentile %", value="99", width=120, visible=False
    )
    txt_pct_lo = TextInput(
        title="Lower %", value="1", width=100, visible=False
    )
    txt_pct_hi = TextInput(
        title="Upper %", value="99", width=100, visible=False
    )
    txt_vmin = TextInput(
        title="vmin",
        value=f"{data_min:.6g}",
        width=140,
        visible=False,
    )
    txt_vmax = TextInput(
        title="vmax",
        value=f"{data_max:.6g}",
        width=140,
        visible=False,
    )

    # --- Stretch controls ---
    sel_stretch = Select(
        title="Stretch",
        value="sqrt",
        options=[
            ("linear", "Linear"),
            ("sqrt", "Sqrt"),
            ("log", "Log"),
            ("squared", "Squared"),
            ("asinh", "Asinh"),
            ("sinh", "Sinh"),
            ("power", "Power"),
        ],
        width=160,
    )
    txt_stretch_a = TextInput(
        title="a / index", value="1000", width=140, visible=False
    )

    # --- Transform controls ---
    sel_flip = Select(
        title="Flip",
        value="none",
        options=[
            ("none", "No flip"),
            ("x",    "Flip X"),
            ("y",    "Flip Y"),
            ("both", "Flip Both"),
        ],
        width=130,
    )
    sel_rotate = Select(
        title="Rotate",
        value="0",
        options=[
            ("0", "0°"),
            ("90", "90°"),
            ("180", "180°"),
            ("270", "270°"),
            ("360", "360°"),
        ],
        width=100,
    )
    btn_reset = Button(
        label="Reset All", button_type="warning", width=100
    )

    # --- Colormap controls ---
    _cmap_palettes = {
        "gray":    list(bk_gray(256)),
        "inferno": list(bk_inferno(256)),
        "viridis": list(bk_viridis(256)),
        "plasma":  list(bk_plasma(256)),
        "magma":   list(bk_magma(256)),
        "turbo":   list(bk_turbo(256)),
    }
    sel_cmap = Select(
        title="Colormap",
        value="inferno",
        options=[
            ("gray",    "Gray"),
            ("inferno", "Inferno"),
            ("viridis", "Viridis"),
            ("plasma",  "Plasma"),
            ("magma",   "Magma"),
            ("turbo",   "Rainbow"),
        ],
        width=150,
    )
    _cb_args = dict(
        source=src,
        fig_xr=fig.x_range,
        fig_yr=fig.y_range,
        sel_interval=sel_interval,
        sel_stretch=sel_stretch,
        sel_rotate=sel_rotate,
        txt_pct=txt_pct,
        txt_pct_lo=txt_pct_lo,
        txt_pct_hi=txt_pct_hi,
        txt_vmin=txt_vmin,
        txt_vmax=txt_vmax,
        txt_stretch_a=txt_stretch_a,
        sel_flip=sel_flip,
        mapper=mapper,
        sel_cmap=sel_cmap,
        _cmap_palettes=_cmap_palettes,
        b64_data=b64_data,
        orig_rows=disp_h,
        orig_cols=disp_w,
        data_min=float(data_min),
        data_max=float(data_max),
        zs_lo=float(zs_lo),
        zs_hi=float(zs_hi),
        default_int="zscale",
        default_str="sqrt",
        default_rot="0",
        default_pct="99",
        default_pct_lo="1",
        default_pct_hi="99",
        default_vmin=f"{data_min:.6g}",
        default_vmax=f"{data_max:.6g}",
        default_sa="1000",
        default_cmap="inferno",
        default_flip="none",
    )

    _cb_update = CustomJS(args=_cb_args, code=_FRAME_JS_UPDATE)
    _cb_reset = CustomJS(
        args=_cb_args,
        code=_FRAME_JS_RESET_PREFIX + _FRAME_JS_UPDATE,
    )

    sel_interval.js_on_change("value", _cb_update)
    sel_stretch.js_on_change("value", _cb_update)
    sel_rotate.js_on_change("value", _cb_update)
    sel_cmap.js_on_change("value", _cb_update)
    txt_pct.js_on_change("value", _cb_update)
    txt_pct_lo.js_on_change("value", _cb_update)
    txt_pct_hi.js_on_change("value", _cb_update)
    txt_vmin.js_on_change("value", _cb_update)
    txt_vmax.js_on_change("value", _cb_update)
    txt_stretch_a.js_on_change("value", _cb_update)
    sel_flip.js_on_change("value", _cb_update)
    btn_reset.js_on_click(_cb_reset)

    layout = bk_column(
        bk_row(
            sel_interval,
            txt_pct, txt_pct_lo, txt_pct_hi,
            txt_vmin, txt_vmax,
            sel_stretch, txt_stretch_a,
            sel_cmap,
            sel_flip, sel_rotate, btn_reset,
        ),
        fig,
        sizing_mode="stretch_width",
    )
    title = f"Frame: {filepath.name}  [{orig_w}\u00d7{orig_h}]"
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

    if not _is_plotable(kw_output):
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
        elif kw_output in ("EXT_E2DS", "EXT_E2DS_FF", "EXT_E2DS_LL"):
            result = _build_frame_plot(
                filepath, match_aspect=False
            )
        elif kw_output in ("TELLU_OBJ", "TELLU_RECON"):
            result = _build_frame_plot(
                filepath, match_aspect=False
            )
        elif kw_output == "TELLU_SCLEAN":
            result = _build_frame_plot(
                filepath,
                match_aspect=False,
                pref_extnames=["SKY_A", "SKY_AB", "SKY_B"],
            )
        elif kw_output in (
            "EXT_S1D_W",
            "EXT_S1D_V",
        ):
            result = _build_s1d_raw_plot(
                filepath,
                "APERO Extracted 1D Spectrum",
            )
        elif kw_output in (
            "SC1D_W_FILE",
            "SC1D_V_FILE",
        ):
            result = _build_s1d_raw_plot(
                filepath,
                "APERO Telluric-Corrected 1D Spectrum",
            )
        elif kw_output in (
            "RC1D_W_FILE",
            "RC1D_V_FILE",
        ):
            result = _build_s1d_raw_plot(
                filepath,
                "APERO Reconstructed Telluric 1D",
            )
        elif any(
            kw_output.startswith(p) for p in FRAME_OUTPUT_PREFIXES
        ):
            result = _build_frame_plot(filepath, match_aspect=True)
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
