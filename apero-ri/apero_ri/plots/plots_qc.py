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
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from astropy.time import Time
from bokeh.embed import components
from bokeh.models import (ColumnDataSource, CrosshairTool,
                          DatetimeTickFormatter, HoverTool)
from bokeh.plotting import figure

from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.plots.plots_qc'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define private helper functions
# =============================================================================
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
        return [], f'Missing file: {path.name}'
    # -------------------------------------------------------------------------
    # load and parse JSON
    try:
        with open(path, 'r', encoding='utf-8') as fio:
            payload = json.load(fio)
    except Exception as exc:
        return [], f'Failed to read {path.name}: {exc}'
    rows = payload.get('rows', [])
    if not isinstance(rows, list):
        return [], f'Invalid rows format in {path.name}'
    return rows, ''


def _label_from_headers(profile_data: Dict[str, Any],
                        section: str, key: str,
                        fallback: str) -> str:
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
        calib = profile_data.get('calib-headers', {})
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
    label = str(meta.get('label', '') or '').strip()
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
        return Time(mjd, format='mjd').to_datetime(timezone=timezone.utc)
    except Exception:
        return None


def _series(rows: List[Dict[str, Any]],
            y_key: str) -> Tuple[List[Any], List[float]]:
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
        dt = _to_datetime(row.get('KW_MID_OBS_TIME'))
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


def _empty_metric(display_name: str, label: str,
                  message: str) -> Dict[str, Any]:
    """
    Return a payload dict representing a metric with no plot data.

    :param display_name: str, human-readable metric name
    :param label: str, y-axis label
    :param message: str, the reason the plot is absent

    :return: dict, metric payload with has_plot=False
    :rtype: dict
    """
    return {
        'display_name': display_name,
        'label': label,
        'full_script': '',
        'zoom_script': '',
        'full_div': '',
        'zoom_div': '',
        'has_plot': False,
        'message': message,
    }


def _build_metric_plot(rows: List[Dict[str, Any]],
                       metric_key: str,
                       display_name: str,
                       label: str) -> Dict[str, Any]:
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
            display_name, label,
            f'No valid data for {display_name}.',
        )
    # -------------------------------------------------------------------------
    # build full time-series figure
    src = ColumnDataSource(data={'x': xvals, 'y': yvals})
    tools = 'pan,wheel_zoom,box_zoom,reset,save'
    hover = HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('Value', '@y{0.000000}'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    )
    p_full = figure(
        x_axis_type='datetime',
        tools=tools,
        active_scroll='wheel_zoom',
        height=320,
        sizing_mode='stretch_width',
        title=f'{display_name}: full time series',
        background_fill_color='#f5f0d0',
    )
    p_full.add_tools(hover)
    p_full.add_tools(CrosshairTool(dimensions='both'))
    p_full.scatter('x', 'y', source=src, size=6, alpha=0.75)
    p_full.xaxis.axis_label = 'Date (UTC)'
    p_full.yaxis.axis_label = label
    p_full.xaxis.formatter = DatetimeTickFormatter(
        days='%Y-%m-%d', months='%Y-%m', years='%Y',
    )
    # -------------------------------------------------------------------------
    # build 6-month zoom figure
    end_dt = xvals[-1]
    start_dt = end_dt - timedelta(days=183)
    recent_mask = [i for i, dt in enumerate(xvals) if dt >= start_dt]
    if not recent_mask:
        recent_mask = [len(xvals) - 1]
    src_zoom = ColumnDataSource(data={
        'x': [xvals[i] for i in recent_mask],
        'y': [yvals[i] for i in recent_mask],
    })
    p_zoom = figure(
        x_axis_type='datetime',
        tools=tools,
        active_scroll='wheel_zoom',
        height=320,
        sizing_mode='stretch_width',
        title=f'{display_name}: last 6 months',
        background_fill_color='#f0f4ff',
    )
    p_zoom.add_tools(HoverTool(
        tooltips=[
            ('Date (UTC)', '@x{%F %T}'),
            ('Value', '@y{0.000000}'),
        ],
        formatters={'@x': 'datetime'},
        mode='mouse',
    ))
    p_zoom.add_tools(CrosshairTool(dimensions='both'))
    p_zoom.scatter('x', 'y', source=src_zoom, size=6, alpha=0.85,
                   color='#d95f02')
    p_zoom.xaxis.axis_label = 'Date (UTC)'
    p_zoom.yaxis.axis_label = label
    p_zoom.xaxis.formatter = DatetimeTickFormatter(
        days='%Y-%m-%d', months='%Y-%m', years='%Y',
    )
    # -------------------------------------------------------------------------
    # serialise both views
    full_script, full_div = components(p_full)
    zoom_script, zoom_div = components(p_zoom)
    return {
        'display_name': display_name,
        'label': label,
        'full_script': full_script,
        'zoom_script': zoom_script,
        'full_div': full_div,
        'zoom_div': zoom_div,
        'has_plot': True,
        'message': '',
    }


def _metric_definitions(section: str) -> List[Tuple[str, str, str, str]]:
    """
    Return the metric definitions for a named QC section.

    Each entry is a 4-tuple:
        (metric_key, display_name, header_section, source_filename)

    :param section: str, the QC section name (e.g. 'shape', 'wave')

    :return: list of 4-tuples describing each metric
    :rtype: list[tuple[str, str, str, str]]
    """
    sname = str(section or '').strip().lower()
    # -------------------------------------------------------------------------
    # shape metrics
    if sname == 'shape':
        return [
            ('KW_SHAPE_DX', 'SHAPE DX', 'SHAPEL',
             'qc_stats_SHAPEL.json'),
            ('KW_SHAPE_DY', 'SHAPE DY', 'SHAPEL',
             'qc_stats_SHAPEL.json'),
            ('KW_SHAPE_A', 'SHAPE A', 'SHAPEL',
             'qc_stats_SHAPEL.json'),
            ('KW_SHAPE_B', 'SHAPE B', 'SHAPEL',
             'qc_stats_SHAPEL.json'),
            ('KW_SHAPE_C', 'SHAPE C', 'SHAPEL',
             'qc_stats_SHAPEL.json'),
            ('KW_SHAPE_D', 'SHAPE D', 'SHAPEL',
             'qc_stats_SHAPEL.json'),
        ]
    # -------------------------------------------------------------------------
    # wave metrics
    if sname == 'wave':
        return [
            ('KW_WFP_DRIFT', 'WFP DRIFT', 'WAVE_NIGHT',
             'qc_stats_WAVE_NIGHT.json'),
            ('KW_CAVITY_WIDTH', 'CAVITY WIDTH', 'WAVE_NIGHT',
             'qc_stats_WAVE_NIGHT.json'),
        ]
    return []


# =============================================================================
# Define public builder functions
# =============================================================================
def build_qc_plot_payload(base_dir: Path,
                          profile: Dict[str, Any]) -> Dict[str, Any]:
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
    profile_id = str(profile.get('profile_id', '') or '').strip()
    instrument = str(profile.get('instrument', '') or '').strip()
    profile_data: Dict[str, Any] = {}
    if isinstance(profile.get('data'), dict):
        profile_data = profile['data']
    # -------------------------------------------------------------------------
    # load qc_stats JSON rows
    tasks_dir = Path(base_dir) / 'tasks' / instrument / profile_id
    shape_rows, shape_err = _load_rows(tasks_dir / 'qc_stats_SHAPEL.json')
    wave_rows, wave_err = _load_rows(
        tasks_dir / 'qc_stats_WAVE_NIGHT.json'
    )
    # -------------------------------------------------------------------------
    # build shape plots
    shape_defs = [(m[0], m[1]) for m in _metric_definitions('shape')]
    shape_plots: List[Dict[str, Any]] = []
    if shape_err:
        for metric_key, display_name in shape_defs:
            shape_plots.append(
                _empty_metric(display_name, display_name, shape_err)
            )
    else:
        for metric_key, display_name in shape_defs:
            label = _label_from_headers(
                profile_data, 'SHAPEL', metric_key, display_name
            )
            item = _build_metric_plot(
                shape_rows, metric_key, display_name, label
            )
            item['metric_key'] = metric_key
            shape_plots.append(item)
    # -------------------------------------------------------------------------
    # build wave plots
    wave_defs = [(m[0], m[1]) for m in _metric_definitions('wave')]
    wave_plots: List[Dict[str, Any]] = []
    if wave_err:
        for metric_key, display_name in wave_defs:
            wave_plots.append(
                _empty_metric(display_name, display_name, wave_err)
            )
    else:
        for metric_key, display_name in wave_defs:
            label = _label_from_headers(
                profile_data, 'WAVE_NIGHT', metric_key, display_name
            )
            item = _build_metric_plot(
                wave_rows, metric_key, display_name, label
            )
            item['metric_key'] = metric_key
            wave_plots.append(item)
    # -------------------------------------------------------------------------
    # return assembled payload
    return {
        'shape_plots': shape_plots,
        'wave_plots': wave_plots,
        'shape_file': str(tasks_dir / 'qc_stats_SHAPEL.json'),
        'wave_file': str(tasks_dir / 'qc_stats_WAVE_NIGHT.json'),
    }


def build_qc_single_plot_payload(base_dir: Path,
                                 profile: Dict[str, Any],
                                 section: str,
                                 metric_key: str,
                                 view_key: str) -> Dict[str, Any]:
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
    profile_id = str(profile.get('profile_id', '') or '').strip()
    instrument = str(profile.get('instrument', '') or '').strip()
    profile_data: Dict[str, Any] = {}
    if isinstance(profile.get('data'), dict):
        profile_data = profile['data']
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
            'has_plot': False,
            'message': f'Unknown QC metric: {metric_key}',
            'display_name': metric_key,
            'label': metric_key,
            'section': section,
            'view_name': view_key,
            'plot_div': '',
            'plot_script': '',
        }
    # -------------------------------------------------------------------------
    # load data rows
    _, display_name, header_section, filename = metric
    tasks_dir = Path(base_dir) / 'tasks' / instrument / profile_id
    rows, err = _load_rows(tasks_dir / filename)
    label = _label_from_headers(
        profile_data, header_section, metric_key, display_name
    )
    if err:
        return {
            'has_plot': False,
            'message': err,
            'display_name': display_name,
            'label': label,
            'section': section,
            'view_name': view_key,
            'plot_div': '',
            'plot_script': '',
        }
    # -------------------------------------------------------------------------
    # build full metric payload
    metric_payload = _build_metric_plot(
        rows, metric_key, display_name, label
    )
    if not metric_payload.get('has_plot'):
        return {
            'has_plot': False,
            'message': metric_payload.get(
                'message', f'No valid data for {display_name}.'
            ),
            'display_name': display_name,
            'label': label,
            'section': section,
            'view_name': view_key,
            'plot_div': '',
            'plot_script': '',
        }
    # -------------------------------------------------------------------------
    # select view variant
    vkey = str(view_key or '').strip().lower()
    if vkey not in {'full', 'zoom'}:
        vkey = 'full'
    if vkey == 'zoom':
        plot_div = metric_payload.get('zoom_div', '')
        plot_script = metric_payload.get('zoom_script', '')
        view_name = 'Last 6 months'
    else:
        plot_div = metric_payload.get('full_div', '')
        plot_script = metric_payload.get('full_script', '')
        view_name = 'Full time series'
    # -------------------------------------------------------------------------
    # return final payload
    return {
        'has_plot': True,
        'message': '',
        'display_name': display_name,
        'label': label,
        'section': section,
        'view_name': view_name,
        'plot_div': plot_div,
        'plot_script': plot_script,
    }


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    # --------------------------------------------------------------------------
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================

