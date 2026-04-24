#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Shared Bokeh helpers for data portal plot modules.

Provides common utilities for building Bokeh figures that can be
embedded either via json_item (dynamic, AJAX-loaded pages) or via
components() (server-rendered standalone pages).

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

from datetime import timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from apero_ri.base import base
from astropy.time import Time
from bokeh.embed import components, json_item
from bokeh.models import CrosshairTool, DatetimeTickFormatter
from bokeh.plotting import figure

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.plots.plot_general"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# BLOCK_KIND → PATH_KEY mapping shared by all plot-object sub-modules.
# Used by _resolve_file_path below.  Mirrors apero_ri.base.base.BLOCK_KIND.
_BLOCK_KIND_TO_PATH: Dict[str, str] = {
    "raw": "PATH_RAW",
    "tmp": "PATH_PP",
    "calib": "PATH_CALIB",
    "red": "PATH_RED",
    "tellu": "PATH_TELLU",
    "out": "PATH_OUT",
    "lbl": "PATH_LBL",
}


# =============================================================================
# Define shared file-path helper
# =============================================================================
def resolve_file_path(
    row: Dict[str, Any], paths: Dict[str, str]
) -> Optional[Path]:
    """
    Resolve a FITS file path from an ftable row.

    Guards against path-traversal: the resolved path *must* remain
    inside the base directory for the block-kind or ``None`` is
    returned.

    Used by both ``plot_obj_spectrum`` (S1D / SC1D files) and
    ``plot_obj_ccf`` (CCF FITS files).  Defined here to avoid a
    cross-dependency between those two modules.

    :param row: dict, ftable row with keys BLOCK_KIND, OBS_DIR,
        FILENAME
    :param paths: dict mapping PATH_* keys to directory strings (e.g.
        PATH_RED, PATH_LBL)

    :return: Path to the file if it exists, None otherwise
    :rtype: pathlib.Path | None
    """
    block_kind = str(row.get("BLOCK_KIND", "") or "").strip()
    path_key = _BLOCK_KIND_TO_PATH.get(block_kind)
    if not path_key:
        return None
    base_str = str(paths.get(path_key, "") or "").strip()
    if not base_str:
        return None
    base_p = Path(base_str).resolve()
    obs_dir = str(row.get("OBS_DIR", "") or "").strip()
    filename = str(row.get("FILENAME", "") or "").strip()
    if not filename:
        return None
    try:
        obs_part = Path(obs_dir.strip("/")) if obs_dir else Path("")
        candidate = (base_p / obs_part / filename).resolve()
        candidate.relative_to(base_p)  # raises ValueError on traversal
        return candidate if candidate.is_file() else None
    except (ValueError, OSError):
        return None


# =============================================================================
# Define functions
# =============================================================================
def mjd_to_datetime(value: Any) -> Any:
    """
    Convert an MJD value to a timezone-aware UTC datetime.

    :param value: int, float or string MJD value

    :return: datetime (UTC) or None if conversion fails
    :rtype: datetime.datetime | None
    """
    # -------------------------------------------------------------------------
    # try to convert to float
    try:
        mjd = float(value)
    except (TypeError, ValueError):
        return None
    # -------------------------------------------------------------------------
    # convert MJD to UTC datetime
    try:
        return Time(mjd, format="mjd").to_datetime(timezone=timezone.utc)
    except Exception:
        return None


def sci_header_label(
    preset: Dict[str, Any], section: str, key: str, fallback: str
) -> str:
    """
    Resolve a display label from the sci-headers section of an
    instrument profile YAML.

    :param preset: dict, the instrument profile preset dictionary
    :param section: str, the sci-headers sub-section name
    :param key: str, the keyword key within the sub-section
    :param fallback: str, the value to return when the key is absent

    :return: str, resolved label or fallback
    :rtype: str
    """
    # -------------------------------------------------------------------------
    # validate preset structure
    if not isinstance(preset, dict):
        return fallback
    headers = preset.get("sci-headers", preset.get("headers", {}))
    if not isinstance(headers, dict):
        return fallback
    # -------------------------------------------------------------------------
    # resolve section → key → label
    sec = headers.get(section, {})
    if not isinstance(sec, dict):
        return fallback
    item = sec.get(key, {})
    if not isinstance(item, dict):
        return fallback
    label = str(item.get("label", "") or "").strip()
    return label or fallback


def make_time_figure(title: str = "", height: int = 350) -> Any:
    """
    Return a Bokeh figure with a datetime x-axis and standard tools.

    :param title: str, optional figure title
    :param height: int, optional figure pixel height (default 350)

    :return: Bokeh Figure object
    :rtype: bokeh.plotting.figure
    """
    # -------------------------------------------------------------------------
    # build tools string and create figure
    tools = "pan,wheel_zoom,box_zoom,reset,save"
    fig = figure(
        x_axis_type="datetime",
        tools=tools,
        active_scroll="wheel_zoom",
        height=height,
        sizing_mode="stretch_width",
        title=title,
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    # -------------------------------------------------------------------------
    # add crosshair and datetime formatter
    fig.add_tools(CrosshairTool(dimensions="both"))
    fig.xaxis.formatter = DatetimeTickFormatter(
        days="%Y-%m-%d",
        months="%Y-%m",
        years="%Y",
    )
    return fig


def plot_to_json_item(fig: Any, target_id: str) -> Dict[str, Any]:
    """
    Serialise a Bokeh figure to a JSON-embeddable dict for client-side
    rendering via Bokeh.embed.embed_item().

    :param fig: Bokeh figure or layout object
    :param target_id: str, the HTML element id to embed into

    :return: dict, the JSON-serialisable item payload
    :rtype: dict
    """
    try:
        from apero_ri.plots.bokeh_theme import (
            apply_theme_to_layout, get_request_theme,
        )
        apply_theme_to_layout(fig, get_request_theme())
    except Exception:  # noqa: BLE001
        pass
    return json_item(fig, target_id)


def plot_to_components(fig: Any) -> Tuple[str, str]:
    """
    Return (script, div) HTML strings for server-side embedding via
    Jinja2 templates.

    :param fig: Bokeh figure or layout object

    :return: tuple, 1. script: str, the Bokeh JS <script> block,
                    2. div:    str, the target <div> block
    :rtype: tuple[str, str]
    """
    try:
        from apero_ri.plots.bokeh_theme import (
            apply_theme_to_layout, get_request_theme,
        )
        apply_theme_to_layout(fig, get_request_theme())
    except Exception:  # noqa: BLE001
        pass
    return components(fig)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
