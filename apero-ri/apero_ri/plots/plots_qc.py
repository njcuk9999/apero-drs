#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Quality-control graph components for data portal pages.

Provides builders for per-metric scatter plots (full time series and
6-month zoom) used on the QC graphs page, plus a single-plot maximize
helper.

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

import json
import math
import os
import re
import statistics
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from apero_ri.base import base
from astropy.time import Time
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource,
    CrosshairTool,
    DatetimeTickFormatter,
    HoverTool,
)
from bokeh.plotting import figure

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.plots.plots_qc"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define private helper functions
# =============================================================================
def _recover_rows_payload(text: str) -> Optional[Dict[str, Any]]:
    """
    Best-effort recovery for a partially-corrupt qc_stats JSON blob.

    Attempts to split the content of the top-level ``"rows"`` array
    into individual ``{ ... }`` objects by brace-depth, parse each
    in isolation, and drop the ones that fail. The surrounding
    payload (``generated_at``, ``metadata``, ...) is reconstructed
    with the recovered rows list.

    :param text: str, raw JSON file content (already preprocessed with
                 the cheap regex fix-ups)

    :return: dict payload on success, or None if recovery fails
    """
    try:
        start = text.index('"rows"')
        bracket = text.index('[', start)
    except ValueError:
        return None
    # walk the array and collect top-level objects
    depth = 0
    in_str = False
    esc = False
    chunks: List[str] = []
    buf: List[str] = []
    end_idx = -1
    for i in range(bracket + 1, len(text)):
        ch = text[i]
        if esc:
            buf.append(ch)
            esc = False
            continue
        if ch == '\\' and in_str:
            buf.append(ch)
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            buf.append(ch)
            continue
        if in_str:
            buf.append(ch)
            continue
        if ch == '{':
            depth += 1
            buf.append(ch)
            continue
        if ch == '}':
            depth -= 1
            buf.append(ch)
            if depth == 0:
                chunks.append(''.join(buf).strip())
                buf = []
            continue
        if ch == ']' and depth == 0:
            end_idx = i
            break
        if depth > 0:
            buf.append(ch)
    if end_idx < 0:
        return None
    rows: List[Dict[str, Any]] = []
    for chunk in chunks:
        chunk = chunk.strip().rstrip(',').strip()
        if not chunk:
            continue
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    # try to recover the metadata prefix (before "rows")
    head = text[:start].rstrip().rstrip(',')
    if not head.endswith('{'):
        # give up on metadata; return a minimal payload
        return {"rows": rows}
    try:
        prefix = json.loads(head + '"rows": [] }')
    except json.JSONDecodeError:
        return {"rows": rows}
    prefix['rows'] = rows
    prefix['row_count'] = len(rows)
    return prefix


def _load_rows(path: Path) -> Tuple[List[Dict[str, Any]], str]:
    """
    Load rows from a qc_stats JSON file.

    :param path: Path, absolute path to the JSON file

    :return: tuple, 1. rows: list of row dicts (may be empty on error)
                    2. error: str, error message or empty string
    :rtype: tuple[list, str]
    """
    # -------------------------------------------------------------------------
    # check file exists
    if not path.exists():
        return [], f"Missing file: {path.name}"
    # -------------------------------------------------------------------------
    # load and parse JSON
    try:
        with open(path, "r", encoding="utf-8") as fio:
            payload = json.load(fio)
    except json.JSONDecodeError as exc:
        # Self-heal known historical corruption patterns in
        # qc_stats_*.json produced by overlapping non-atomic writes
        # from earlier versions, e.g.:
        #   * `"KW_FOO:: 1.234,`  (missing closing quote)
        #   * `"KW_FOO":: 1.234,` (extra colon after closing quote)
        #   * `""KW_FOO": 1.234,` (duplicated opening quote)
        # First try simple regex fixes; if that still fails, fall back
        # to a row-level recovery that drops every ``{ ... }`` block
        # under ``rows`` that individually fails to parse. On success,
        # rewrite the file atomically so the cost is paid once.
        try:
            with open(path, "r", encoding="utf-8") as fio:
                raw = fio.read()
            patched = re.sub(
                r'"([A-Za-z_][A-Za-z0-9_]*)"?:: ',
                r'"\1": ',
                raw,
            )
            patched = re.sub(
                r'""([A-Za-z_][A-Za-z0-9_]*)":',
                r'"\1":',
                patched,
            )
            payload = None
            try:
                payload = json.loads(patched)
            except json.JSONDecodeError:
                payload = _recover_rows_payload(patched)
            if payload is None:
                return [], f"Failed to read {path.name}: {exc}"
            tmp = path.with_name(path.name + ".tmp")
            with open(tmp, "w", encoding="utf-8") as fio:
                json.dump(payload, fio, ensure_ascii=False, indent=2)
            os.replace(tmp, path)
        except Exception as exc2:  # noqa: BLE001
            return [], f"Failed to read {path.name}: {exc2}"
        except Exception as exc2:  # noqa: BLE001
            return [], f"Failed to read {path.name}: {exc2}"
    except Exception as exc:  # noqa: BLE001
        return [], f"Failed to read {path.name}: {exc}"
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return [], f"Invalid rows format in {path.name}"
    return rows, ""


def _label_from_headers(
    profile_data: Dict[str, Any], section: str, key: str, fallback: str
) -> str:
    """
    Resolve a display label from the calib-headers section of a
    profile data dict.

    :param profile_data: dict, the profile data sub-dictionary
    :param section: str, the calib-headers sub-section name
    :param key: str, the keyword key within the sub-section
    :param fallback: str, the value to return when key is absent

    :return: str, resolved label or fallback
    :rtype: str
    """
    # -------------------------------------------------------------------------
    # validate structure
    calib: Dict[str, Any] = {}
    if isinstance(profile_data, dict):
        calib = profile_data.get("calib-headers", {})
    if not isinstance(calib, dict):
        return fallback
    # -------------------------------------------------------------------------
    # walk section → key → label
    sec = calib.get(section, {})
    if not isinstance(sec, dict):
        return fallback
    meta = sec.get(key, {})
    if not isinstance(meta, dict):
        return fallback
    label = str(meta.get("label", "") or "").strip()
    return label or fallback


def _to_datetime(value: Any) -> Any:
    """
    Convert an MJD-like value to a timezone-aware UTC datetime.

    :param value: int, float or string MJD value

    :return: datetime (UTC) or None on failure
    :rtype: datetime.datetime | None
    """
    try:
        mjd = float(value)
    except (TypeError, ValueError):
        return None
    try:
        return Time(mjd, format="mjd").to_datetime(timezone=timezone.utc)
    except Exception:
        return None


def _series(
    rows: List[Dict[str, Any]], y_key: str
) -> Tuple[List[Any], List[float]]:
    """
    Extract and sort a (datetime, y-value) series for one metric key.

    :param rows: list of row dicts from a qc_stats JSON
    :param y_key: str, the column name for the y-axis values

    :return: tuple, 1. xvals: list of datetime objects (sorted)
                    2. yvals: list of float values (corresponding)
    :rtype: tuple[list, list]
    """
    # -------------------------------------------------------------------------
    # build (dt, y) pairs
    points: List[Tuple[Any, float]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        dt = _to_datetime(row.get("KW_MID_OBS_TIME"))
        if dt is None:
            continue
        raw_y = row.get(y_key)
        if raw_y is None:
            continue
        try:
            yval = float(raw_y)
        except (TypeError, ValueError):
            continue
        points.append((dt, yval))
    # -------------------------------------------------------------------------
    # sort and unpack
    points.sort(key=lambda item: item[0])
    xvals = [p[0] for p in points]
    yvals = [p[1] for p in points]
    return xvals, yvals


def _empty_metric(
    display_name: str, label: str, message: str
) -> Dict[str, Any]:
    """
    Return a payload dict representing a metric with no plot data.

    :param display_name: str, human-readable metric name
    :param label: str, y-axis label
    :param message: str, the reason the plot is absent

    :return: dict, metric payload with has_plot=False
    :rtype: dict
    """
    return {
        "display_name": display_name,
        "label": label,
        "full_script": "",
        "zoom_script": "",
        "full_div": "",
        "zoom_div": "",
        "has_plot": False,
        "message": message,
    }


def _build_metric_plot(
    rows: List[Dict[str, Any]], metric_key: str, display_name: str, label: str
) -> Dict[str, Any]:
    """
    Create full time-series and 6-month zoom scatter plots for one
    QC metric.

    :param rows: list of row dicts from a qc_stats JSON
    :param metric_key: str, column name carrying the metric values
    :param display_name: str, human-readable metric name for titles
    :param label: str, y-axis label

    :return: dict, metric payload; has_plot=True when data is available
    :rtype: dict
    """
    # -------------------------------------------------------------------------
    # extract time series
    xvals, yvals = _series(rows, metric_key)
    if not xvals:
        return _empty_metric(
            display_name,
            label,
            f"No valid data for {display_name}.",
        )
    # -------------------------------------------------------------------------
    # build full time-series figure
    f_low, f_high = _sigma_window(yvals, nsigma=5.0)
    full_in_x, full_in_y, full_low_x, full_high_x = _split_outliers(
        xvals, yvals, f_low, f_high
    )
    src = ColumnDataSource(data={"x": full_in_x, "y": full_in_y})
    tools = "pan,wheel_zoom,box_zoom,reset,save"
    hover = HoverTool(
        tooltips=[
            ("Date (UTC)", "@x{%F %T}"),
            ("Value", "@y{0.000000}"),
        ],
        formatters={"@x": "datetime"},
        mode="mouse",
    )
    p_full = figure(
        x_axis_type="datetime",
        tools=tools,
        active_scroll="wheel_zoom",
        height=320,
        sizing_mode="stretch_width",
        title=f"{display_name}: full time series",
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    p_full.add_tools(hover)
    p_full.add_tools(CrosshairTool(dimensions="both"))
    p_full.scatter("x", "y", source=src, size=6, alpha=0.75)
    _apply_plot_window_and_outlier_arrows(
        p_full,
        ymin=f_low,
        ymax=f_high,
        low_x=full_low_x,
        high_x=full_high_x,
    )
    p_full.xaxis.axis_label = "Date (UTC)"
    p_full.yaxis.axis_label = label
    p_full.xaxis.formatter = DatetimeTickFormatter(
        days="%Y-%m-%d",
        months="%Y-%m",
        years="%Y",
    )
    # -------------------------------------------------------------------------
    # build 6-month zoom figure
    end_dt = xvals[-1]
    start_dt = end_dt - timedelta(days=183)
    recent_mask = [i for i, dt in enumerate(xvals) if dt >= start_dt]
    if not recent_mask:
        recent_mask = [len(xvals) - 1]
    src_zoom = ColumnDataSource(
        data={
            "x": [xvals[i] for i in recent_mask],
            "y": [yvals[i] for i in recent_mask],
        }
    )
    zoom_xvals = [xvals[i] for i in recent_mask]
    zoom_yvals = [yvals[i] for i in recent_mask]
    z_low, z_high = _sigma_window(zoom_yvals, nsigma=5.0)
    zoom_in_x, zoom_in_y, zoom_low_x, zoom_high_x = _split_outliers(
        zoom_xvals, zoom_yvals, z_low, z_high
    )
    src_zoom = ColumnDataSource(data={"x": zoom_in_x, "y": zoom_in_y})
    p_zoom = figure(
        x_axis_type="datetime",
        tools=tools,
        active_scroll="wheel_zoom",
        height=320,
        sizing_mode="stretch_width",
        title=f"{display_name}: last 6 months",
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    p_zoom.add_tools(
        HoverTool(
            tooltips=[
                ("Date (UTC)", "@x{%F %T}"),
                ("Value", "@y{0.000000}"),
            ],
            formatters={"@x": "datetime"},
            mode="mouse",
        )
    )
    p_zoom.add_tools(CrosshairTool(dimensions="both"))
    p_zoom.scatter(
        "x", "y", source=src_zoom, size=6, alpha=0.85, color="#d95f02"
    )
    _apply_plot_window_and_outlier_arrows(
        p_zoom,
        ymin=z_low,
        ymax=z_high,
        low_x=zoom_low_x,
        high_x=zoom_high_x,
    )
    p_zoom.xaxis.axis_label = "Date (UTC)"
    p_zoom.yaxis.axis_label = label
    p_zoom.xaxis.formatter = DatetimeTickFormatter(
        days="%Y-%m-%d",
        months="%Y-%m",
        years="%Y",
    )
    # -------------------------------------------------------------------------
    # serialise both views
    full_script, full_div = components(p_full)
    zoom_script, zoom_div = components(p_zoom)
    return {
        "display_name": display_name,
        "label": label,
        "full_script": full_script,
        "zoom_script": zoom_script,
        "full_div": full_div,
        "zoom_div": zoom_div,
        "has_plot": True,
        "message": "",
    }


def _science_fiber(profile_data: Dict[str, Any]) -> str:
    """Return configured science fiber (upper case), or empty when unset."""
    if not isinstance(profile_data, dict):
        return ""
    general = profile_data.get("general", {})
    if not isinstance(general, dict):
        return ""
    return str(general.get("science_fiber", "") or "").strip().upper()


def _normalize_row_fiber(row: Dict[str, Any]) -> str:
    """Extract a row fiber label from any known key names."""
    for key in ("KW_FIBER", "FIBER", "SCIENCE_FIBER"):
        raw = row.get(key)
        if raw is None:
            continue
        sval = str(raw).strip().upper()
        if sval:
            return sval
    return ""


def _wave_fiber_values(rows: List[Dict[str, Any]]) -> List[str]:
    """Return sorted distinct fiber labels from wave rows."""
    fibers = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        fiber = _normalize_row_fiber(row)
        if fiber:
            fibers.add(fiber)
    return sorted(fibers)


def _dedupe_wave_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fallback de-duplication: keep first row per timestamp."""
    deduped: List[Dict[str, Any]] = []
    seen_times = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        tval = row.get("KW_MID_OBS_TIME")
        if tval in seen_times:
            continue
        seen_times.add(tval)
        deduped.append(row)
    return deduped


def _filter_wave_rows(
    rows: List[Dict[str, Any]],
    profile_data: Dict[str, Any],
    selected_fiber: str = "",
) -> Tuple[List[Dict[str, Any]], str, List[str]]:
    """Filter wave rows by selected/default fiber and return metadata."""
    if not rows:
        return rows, "", []

    available_fibers = _wave_fiber_values(rows)
    fibers_present = len(available_fibers) > 0
    requested = str(selected_fiber or "").strip().upper()
    if requested in {"ALL", "__ALL__", "*"}:
        requested = ""

    if requested and fibers_present:
        filtered = [
            r
            for r in rows
            if isinstance(r, dict) and _normalize_row_fiber(r) == requested
        ]
        return filtered, requested, available_fibers

    default_fiber = _science_fiber(profile_data)
    if not requested and default_fiber and fibers_present:
        filtered = [
            r
            for r in rows
            if isinstance(r, dict) and _normalize_row_fiber(r) == default_fiber
        ]
        if filtered:
            return filtered, default_fiber, available_fibers

    # Legacy rows may have no fiber metadata yet.
    return _dedupe_wave_rows(rows), "", available_fibers


def _sigma_window(
    values: List[float], nsigma: float = 5.0
) -> Tuple[float, float]:
    """Return a robust y-range around median ± nsigma*std with sane padding."""
    clean: List[float] = []
    for value in values:
        if value is None:
            continue
        try:
            fval = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(fval):
            continue
        clean.append(fval)
    if not clean:
        return -1.0, 1.0

    med = float(statistics.median(clean))
    sigma = float(statistics.pstdev(clean)) if len(clean) > 1 else 0.0
    if sigma <= 0:
        # Flat series: center around median with a small non-zero window.
        pad = max(abs(med) * 0.05, 1e-6)
        ymin = med - pad
        ymax = med + pad
    else:
        ymin = med - nsigma * sigma
        ymax = med + nsigma * sigma

    if not math.isfinite(ymin) or not math.isfinite(ymax) or ymin == ymax:
        pad = max(abs(med) * 0.05, 1e-6)
        ymin = med - pad
        ymax = med + pad
    return ymin, ymax


def _split_outliers(
    xvals: List[Any], yvals: List[float], ymin: float, ymax: float
) -> Tuple[List[Any], List[float], List[Any], List[Any]]:
    """Split points into in-range, low-outlier and high-outlier buckets."""
    in_x: List[Any] = []
    in_y: List[float] = []
    low_x: List[Any] = []
    high_x: List[Any] = []
    for xval, yval in zip(xvals, yvals):
        if yval < ymin:
            low_x.append(xval)
        elif yval > ymax:
            high_x.append(xval)
        else:
            in_x.append(xval)
            in_y.append(yval)
    return in_x, in_y, low_x, high_x


def _apply_plot_window_and_outlier_arrows(
    pobj: Any, ymin: float, ymax: float, low_x: List[Any], high_x: List[Any]
) -> None:
    """Apply y-range and draw arrow-like markers for clipped outliers."""
    span = ymax - ymin
    if not math.isfinite(span) or span <= 0:
        span = max(abs(ymax), 1.0)
    margin = max(0.02 * span, 1e-9)

    pobj.y_range.start = ymin
    pobj.y_range.end = ymax

    # Draw downward triangles near top edge for high outliers and upward
    # triangles near bottom edge for low outliers.
    if high_x:
        pobj.scatter(
            x=high_x,
            y=[ymax - margin] * len(high_x),
            marker="inverted_triangle",
            size=9,
            color="#c1121f",
            alpha=0.95,
        )
    if low_x:
        pobj.scatter(
            x=low_x,
            y=[ymin + margin] * len(low_x),
            marker="triangle",
            size=9,
            color="#003049",
            alpha=0.95,
        )


def _metric_definitions(section: str) -> List[Tuple[str, str, str, str]]:
    """
    Return the metric definitions for a named QC section.

    Each entry is a 4-tuple:
        (metric_key, display_name, header_section, source_filename)

    :param section: str, the QC section name (e.g. 'shape', 'wave')

    :return: list of 4-tuples describing each metric
    :rtype: list[tuple[str, str, str, str]]
    """
    sname = str(section or "").strip().lower()
    # -------------------------------------------------------------------------
    # shape metrics
    if sname == "shape":
        return [
            ("KW_SHAPE_DX", "SHAPE DX", "SHAPEL", "qc_stats_SHAPEL.json"),
            ("KW_SHAPE_DY", "SHAPE DY", "SHAPEL", "qc_stats_SHAPEL.json"),
            ("KW_SHAPE_A", "SHAPE A", "SHAPEL", "qc_stats_SHAPEL.json"),
            ("KW_SHAPE_B", "SHAPE B", "SHAPEL", "qc_stats_SHAPEL.json"),
            ("KW_SHAPE_C", "SHAPE C", "SHAPEL", "qc_stats_SHAPEL.json"),
            ("KW_SHAPE_D", "SHAPE D", "SHAPEL", "qc_stats_SHAPEL.json"),
        ]
    # -------------------------------------------------------------------------
    # wave metrics
    if sname == "wave":
        return [
            (
                "KW_WFP_DRIFT",
                "WFP DRIFT",
                "WAVE_NIGHT",
                "qc_stats_WAVE_NIGHT.json",
            ),
            (
                "KW_CAVITY_WIDTH",
                "CAVITY WIDTH",
                "WAVE_NIGHT",
                "qc_stats_WAVE_NIGHT.json",
            ),
        ]
    return []


# =============================================================================
# Define public builder functions
# =============================================================================
def build_qc_plot_payload(
    base_dir: Path, profile: Dict[str, Any], selected_fiber: str = ""
) -> Dict[str, Any]:
    """
    Build the full page payload for the quality-control graphs page.

    :param base_dir: Path, the ARI data directory root
    :param profile: dict, the accessible profile dict (profile_id,
                    instrument, data)

    :return: dict with keys 'shape_plots', 'wave_plots',
             'shape_file', 'wave_file'
    :rtype: dict
    """
    # -------------------------------------------------------------------------
    # resolve profile metadata
    profile_id = str(profile.get("profile_id", "") or "").strip()
    instrument = str(profile.get("instrument", "") or "").strip()
    profile_data: Dict[str, Any] = {}
    if isinstance(profile.get("data"), dict):
        profile_data = profile["data"]
    # -------------------------------------------------------------------------
    # load qc_stats JSON rows
    tasks_dir = Path(base_dir) / "tasks" / instrument / profile_id
    shape_rows, shape_err = _load_rows(tasks_dir / "qc_stats_SHAPEL.json")
    wave_rows, wave_err = _load_rows(tasks_dir / "qc_stats_WAVE_NIGHT.json")
    wave_fibers: List[str] = []
    active_wave_fiber = ""
    if not wave_err:
        wave_rows, active_wave_fiber, wave_fibers = _filter_wave_rows(
            wave_rows, profile_data, selected_fiber=selected_fiber
        )
    # -------------------------------------------------------------------------
    # build shape plots
    shape_defs = [(m[0], m[1]) for m in _metric_definitions("shape")]
    shape_plots: List[Dict[str, Any]] = []
    if shape_err:
        for metric_key, display_name in shape_defs:
            shape_plots.append(
                _empty_metric(display_name, display_name, shape_err)
            )
    else:
        for metric_key, display_name in shape_defs:
            label = _label_from_headers(
                profile_data, "SHAPEL", metric_key, display_name
            )
            item = _build_metric_plot(
                shape_rows, metric_key, display_name, label
            )
            item["metric_key"] = metric_key
            shape_plots.append(item)
    # -------------------------------------------------------------------------
    # build wave plots
    wave_defs = [(m[0], m[1]) for m in _metric_definitions("wave")]
    wave_plots: List[Dict[str, Any]] = []
    if wave_err:
        for metric_key, display_name in wave_defs:
            wave_plots.append(
                _empty_metric(display_name, display_name, wave_err)
            )
    else:
        for metric_key, display_name in wave_defs:
            label = _label_from_headers(
                profile_data, "WAVE_NIGHT", metric_key, display_name
            )
            item = _build_metric_plot(
                wave_rows, metric_key, display_name, label
            )
            item["metric_key"] = metric_key
            wave_plots.append(item)
    # -------------------------------------------------------------------------
    # return assembled payload
    return {
        "shape_plots": shape_plots,
        "wave_plots": wave_plots,
        "shape_file": str(tasks_dir / "qc_stats_SHAPEL.json"),
        "wave_file": str(tasks_dir / "qc_stats_WAVE_NIGHT.json"),
        "wave_fibers": wave_fibers,
        "selected_wave_fiber": active_wave_fiber,
    }


def build_qc_single_plot_payload(
    base_dir: Path,
    profile: Dict[str, Any],
    section: str,
    metric_key: str,
    view_key: str,
    selected_fiber: str = "",
) -> Dict[str, Any]:
    """
    Build the payload for a single QC plot variant used by the
    maximize view.

    :param base_dir: Path, the ARI data directory root
    :param profile: dict, the accessible profile dict
    :param section: str, the QC section name (e.g. 'shape', 'wave')
    :param metric_key: str, the column key for the metric
    :param view_key: str, 'full' or 'zoom'

    :return: dict with has_plot, plot_div, plot_script and metadata
    :rtype: dict
    """
    # -------------------------------------------------------------------------
    # resolve profile metadata
    profile_id = str(profile.get("profile_id", "") or "").strip()
    instrument = str(profile.get("instrument", "") or "").strip()
    profile_data: Dict[str, Any] = {}
    if isinstance(profile.get("data"), dict):
        profile_data = profile["data"]
    # -------------------------------------------------------------------------
    # look up metric definition
    defs = _metric_definitions(section)
    metric: Optional[Tuple[str, str, str, str]] = None
    for row in defs:
        if row[0] == metric_key:
            metric = row
            break
    if metric is None:
        return {
            "has_plot": False,
            "message": f"Unknown QC metric: {metric_key}",
            "display_name": metric_key,
            "label": metric_key,
            "section": section,
            "view_name": view_key,
            "plot_div": "",
            "plot_script": "",
        }
    # -------------------------------------------------------------------------
    # load data rows
    _, display_name, header_section, filename = metric
    tasks_dir = Path(base_dir) / "tasks" / instrument / profile_id
    rows, err = _load_rows(tasks_dir / filename)
    active_wave_fiber = ""
    if not err and str(section or "").strip().lower() == "wave":
        rows, active_wave_fiber, _ = _filter_wave_rows(
            rows, profile_data, selected_fiber=selected_fiber
        )
    label = _label_from_headers(
        profile_data, header_section, metric_key, display_name
    )
    if err:
        return {
            "has_plot": False,
            "message": err,
            "display_name": display_name,
            "label": label,
            "section": section,
            "view_name": view_key,
            "plot_div": "",
            "plot_script": "",
        }
    # -------------------------------------------------------------------------
    # build full metric payload
    metric_payload = _build_metric_plot(rows, metric_key, display_name, label)
    if not metric_payload.get("has_plot"):
        return {
            "has_plot": False,
            "message": metric_payload.get(
                "message", f"No valid data for {display_name}."
            ),
            "display_name": display_name,
            "label": label,
            "section": section,
            "view_name": view_key,
            "plot_div": "",
            "plot_script": "",
        }
    # -------------------------------------------------------------------------
    # select view variant
    vkey = str(view_key or "").strip().lower()
    if vkey not in {"full", "zoom"}:
        vkey = "full"
    if vkey == "zoom":
        plot_div = metric_payload.get("zoom_div", "")
        plot_script = metric_payload.get("zoom_script", "")
        view_name = "Last 6 months"
    else:
        plot_div = metric_payload.get("full_div", "")
        plot_script = metric_payload.get("full_script", "")
        view_name = "Full time series"
    # -------------------------------------------------------------------------
    # return final payload
    return {
        "has_plot": True,
        "message": "",
        "display_name": display_name,
        "label": label,
        "section": section,
        "view_name": view_name,
        "plot_div": plot_div,
        "plot_script": plot_script,
        "selected_wave_fiber": active_wave_fiber,
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
