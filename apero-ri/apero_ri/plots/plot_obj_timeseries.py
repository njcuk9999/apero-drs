#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Per-night time-series plot builders.

Part of the object-page plot suite; see also:
    plot_obj_spectrum.py – SNR, BERV and median-spectrum plots
    plot_obj_ccf.py      – CCF plots
    plot_obj_lbl.py      – LBL RV plots
    plot_obj_ind.py      – individual file-browser plots

Public API
----------
build_ts_snr_plot_json        – per-night SNR time series (json_item)
build_ts_snr_plot_components  – per-night SNR time series (script/div)
build_ts_airmass_plot_json    – per-night airmass (json_item)
build_ts_airmass_plot_components – per-night airmass (script/div)

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

from datetime import datetime, timezone
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
__NAME__ = "apero_ri.plots.plot_obj_timeseries"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

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
        ident = str(row.get("IDENTIFIER", "") or "").strip()
        obs = str(row.get("OBS_DIR", "") or "").strip()
        if ident and obs:
            id_to_obs[ident] = obs
    # -------------------------------------------------------------------------
    obs_buckets: Dict[str, Dict[str, List[float]]] = {}
    for row in htable_rows:
        ident = str(row.get("IDENTIFIER", "") or "").strip()
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
            means[key] = float(np.nanmean(vals)) if vals else float("nan")
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
    from bokeh.models import DatetimeTicker, DatetimeTickFormatter, FactorRange
    from bokeh.plotting import figure as bk_figure

    if not obs_data:
        return None
    obs_dirs = [d[0] for d in obs_data]
    snr_h = [d[1].get("EXT_H", float("nan")) for d in obs_data]
    snr_y = [d[1].get("EXT_Y", float("nan")) for d in obs_data]

    def _obs_dir_to_dt(obs_dir: str) -> Optional[datetime]:
        text = str(obs_dir or "").strip()
        m = re.match(r"^(\d{4})[-_]?([01]\d)[-_]?([0-3]\d)$", text)
        if not m:
            return None
        try:
            return datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
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
            x_axis_type="datetime",
            title="SNR per Night",
            x_axis_label="Date (UTC)",
            y_axis_label="SNR",
            tools="pan,wheel_zoom,box_zoom,reset,save",
            active_scroll="wheel_zoom",
            height=height,
            sizing_mode="stretch_width",
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[
                ("Obs Dir", "@obs"),
                ("Date", "@x{%F}"),
                ("SNR", "@y{0.0}"),
            ],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
        fig.add_tools(hover)
        src_h = ColumnDataSource({"x": x_ms, "y": snr_h, "obs": obs_dirs})
        src_y = ColumnDataSource({"x": x_ms, "y": snr_y, "obs": obs_dirs})

        first_dt = min(dt for dt in dts if dt is not None)
        last_dt = max(dt for dt in dts if dt is not None)
        span_days = max((last_dt - first_dt).days, 0)

        fig.xaxis.ticker = DatetimeTicker(desired_num_ticks=10)
        if span_days >= 365 * 2:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years="%Y",
                months="%Y",
                days="%Y",
            )
        elif span_days >= 90:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years="%Y",
                months="%Y-%m",
                days="%Y-%m",
            )
        else:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years="%Y",
                months="%Y-%m",
                days="%Y-%m-%d",
            )
        fig.xaxis.major_label_orientation = 0.785
    else:
        fig = bk_figure(
            x_range=FactorRange(*obs_dirs),
            title="SNR per Night",
            x_axis_label="Obs Dir",
            y_axis_label="SNR",
            tools="pan,wheel_zoom,box_zoom,reset,save",
            active_scroll="wheel_zoom",
            height=height,
            sizing_mode="stretch_width",
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[("Obs Dir", "@x"), ("SNR", "@y{0.0}")],
            mode="mouse",
        )
        fig.add_tools(hover)
        src_h = ColumnDataSource({"x": obs_dirs, "y": snr_h})
        src_y = ColumnDataSource({"x": obs_dirs, "y": snr_y})
        fig.xaxis.major_label_orientation = "vertical"

    fig.scatter(
        "x",
        "y",
        source=src_h,
        size=8,
        color="#e6820a",
        marker="circle",
        alpha=0.85,
        legend_label=label_h,
    )
    fig.scatter(
        "x",
        "y",
        source=src_y,
        size=8,
        color="#7e22ce",
        marker="circle",
        alpha=0.85,
        legend_label=label_y,
    )
    # -------------------------------------------------------------------------
    fig.xgrid.grid_line_color = None
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"
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
    from bokeh.models import (
        DatetimeTicker,
        DatetimeTickFormatter,
        FactorRange,
        Range1d,
    )
    from bokeh.plotting import figure as bk_figure

    obs_dirs: List[str] = []
    airmass: List[float] = []

    def _obs_dir_to_dt(obs_dir: str) -> Optional[datetime]:
        text = str(obs_dir or "").strip()
        m = re.match(r"^(\d{4})[-_]?([01]\d)[-_]?([0-3]\d)$", text)
        if not m:
            return None
        try:
            return datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                tzinfo=timezone.utc,
            )
        except ValueError:
            return None

    for obs_dir, means in obs_data:
        am = means.get("EXT_AIRMASS", float("nan"))
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
            x_axis_type="datetime",
            y_range=Range1d(0.0, 2.0),
            title="Airmass per Night",
            x_axis_label="Date (UTC)",
            y_axis_label="Airmass",
            tools="pan,wheel_zoom,box_zoom,reset,save",
            active_scroll="wheel_zoom",
            height=height,
            sizing_mode="stretch_width",
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[
                ("Obs Dir", "@obs"),
                ("Date", "@x{%F}"),
                ("Airmass", "@y{0.000}"),
            ],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
        fig.add_tools(hover)
        src = ColumnDataSource({"x": x_ms, "y": airmass, "obs": obs_dirs})
        first_dt = min(dt for dt in dts if dt is not None)
        last_dt = max(dt for dt in dts if dt is not None)
        span_days = max((last_dt - first_dt).days, 0)

        fig.xaxis.ticker = DatetimeTicker(desired_num_ticks=10)
        if span_days >= 365 * 2:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years="%Y",
                months="%Y",
                days="%Y",
            )
        elif span_days >= 90:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years="%Y",
                months="%Y-%m",
                days="%Y-%m",
            )
        else:
            fig.xaxis.formatter = DatetimeTickFormatter(
                years="%Y",
                months="%Y-%m",
                days="%Y-%m-%d",
            )
        fig.xaxis.major_label_orientation = 0.785
    else:
        fig = bk_figure(
            x_range=FactorRange(*obs_dirs),
            y_range=Range1d(0.0, 2.0),
            title="Airmass per Night",
            x_axis_label="Obs Dir",
            y_axis_label="Airmass",
            tools="pan,wheel_zoom,box_zoom,reset,save",
            active_scroll="wheel_zoom",
            height=height,
            sizing_mode="stretch_width",
            background_fill_color=base.PLOT_BACKGROUND_COLOR,
        )
        hover = HoverTool(
            tooltips=[("Obs Dir", "@x"), ("Airmass", "@y{0.000}")],
            mode="mouse",
        )
        fig.add_tools(hover)
        src = ColumnDataSource({"x": obs_dirs, "y": airmass})
        fig.xaxis.major_label_orientation = "vertical"

    fig.scatter(
        "x",
        "y",
        source=src,
        size=8,
        color="steelblue",
        marker="circle",
        alpha=0.85,
        legend_label="Mean airmass",
    )
    # -------------------------------------------------------------------------
    fig.xgrid.grid_line_color = None
    fig.grid.grid_line_color = "lightgray"
    fig.grid.grid_line_dash = "dashed"
    fig.legend.location = "top_right"
    return fig


# =============================================================================
# Define public per-night time series plot builders
# =============================================================================
def build_ts_snr_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
    target_id: str = "op-ts-snr-plot-div",
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
    label_h = sci_header_label(preset, "ext", "EXT_H", "H-band SNR")
    label_y = sci_header_label(preset, "ext", "EXT_Y", "Y-band SNR")
    obs_data = _aggregate_by_obs_dir(
        htable_rows, ftable_ext_rows, ["EXT_H", "EXT_Y"]
    )
    if not obs_data:
        return {"has_plot": False, "message": "No per-night SNR data."}
    fig = _make_ts_snr_figure(obs_data, label_h, label_y)
    if fig is None:
        return {"has_plot": False, "message": "No per-night SNR data."}
    script, div = plot_to_components(fig)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
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
    label_h = sci_header_label(preset, "ext", "EXT_H", "H-band SNR")
    label_y = sci_header_label(preset, "ext", "EXT_Y", "Y-band SNR")
    obs_data = _aggregate_by_obs_dir(
        htable_rows, ftable_ext_rows, ["EXT_H", "EXT_Y"]
    )
    if not obs_data:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No per-night SNR data.",
        }
    fig = _make_ts_snr_figure(obs_data, label_h, label_y)
    if fig is None:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No per-night SNR data.",
        }
    script, div = plot_to_components(fig)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
    }


def build_ts_airmass_plot_json(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    preset: Dict[str, Any],
    target_id: str = "op-ts-airmass-plot-div",
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
        htable_rows, ftable_ext_rows, ["EXT_AIRMASS"]
    )
    if not obs_data:
        return {
            "has_plot": False,
            "message": "No per-night airmass data.",
        }
    fig = _make_ts_airmass_figure(obs_data)
    if fig is None:
        return {
            "has_plot": False,
            "message": "No airmass values in range 0\u20132.",
        }
    script, div = plot_to_components(fig)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
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
        htable_rows, ftable_ext_rows, ["EXT_AIRMASS"]
    )
    if not obs_data:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No per-night airmass data.",
        }
    fig = _make_ts_airmass_figure(obs_data)
    if fig is None:
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": "No airmass values in range 0\u20132.",
        }
    script, div = plot_to_components(fig)
    return {
        "has_plot": True,
        "script": script,
        "div": div,
        "message": "",
    }

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
