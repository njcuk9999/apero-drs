#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Target-info Bokeh plot builders.

Replaces the static matplotlib SED / HR plots with fully
interactive Bokeh figures that share the same registration system
as the other object-page plots (see ``plot_manager.OBJ_PLOTS``).

Public API
----------
build_sed_plot_json(entry)
    Spectral Energy Distribution: photometry from the astrometric
    YAML entry (Gaia BP/G/RP, 2MASS J/H/Ks, AllWISE W1/W2/W3) as
    coloured points connected by a dashed grey line. A blackbody
    curve (Teff from the entry, scaled to the photometry) is
    overlaid as a solid black line. Crosshair, hover, grid,
    log-log axes.

build_hr_plot_json(entry, neighborhood=None)
    HR diagram (Teff vs absolute Gaia G mag) with the 20-pc
    Gaia neighborhood as a faint scatter backdrop and the target
    plotted as a large red star. Crosshair, hover, grid,
    inverted axes.

build_finder_plot_json / build_rotation_plot_json: not yet
implemented in this module (still served by their own image
endpoints).

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from apero_ri.base import base
from apero_ri.plots.plot_general import (
    plot_to_components,
)
from apero_ri.science import stellar_params as sp
from bokeh.models import (
    ColumnDataSource,
    CrosshairTool,
    FixedTicker,
    HoverTool,
    Label,
)
from bokeh.plotting import figure


__NAME__ = "apero_ri.plots.plot_obj_targetinfo"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__


# ---------------------------------------------------------------
# Filter zero-points (Vega, Jy) and effective wavelengths (um)
# ---------------------------------------------------------------
SED_FILTERS: List[Tuple[str, str, float, float, str]] = [
    # (key,        label,    lambda_um, F0_Jy,  colour)
    ('GBP_MAG',  'Gaia BP', 0.5050,  3552.0, '#5fa8d3'),
    ('G_MAG',    'Gaia G',  0.6230,  3228.7, '#3a86ff'),
    ('GRP_MAG',  'Gaia RP', 0.7730,  2554.9, '#bd2c2c'),
    ('J_MAG',    '2MASS J', 1.235,   1594.0, '#7d4f1d'),
    ('H_MAG',    '2MASS H', 1.662,   1024.0, '#a06030'),
    ('KS_MAG',   '2MASS K', 2.159,    666.7, '#bf6f3a'),
    ('W1_MAG',   'WISE W1', 3.353,    309.5, '#7c3aed'),
    ('W2_MAG',   'WISE W2', 4.603,    171.8, '#9d4edd'),
    ('W3_MAG',   'WISE W3', 11.561,    31.7, '#c77dff'),
]

# Pecaut & Mamajek (2013) compact MS reference (used as fallback
# backdrop on the HR diagram if the 20-pc neighborhood is not
# available).
PM_TABLE = [
    # SpT,   Teff(K),  M_G
    ('O5V', 41500.0, -5.20),
    ('B0V', 31400.0, -3.10),
    ('B5V', 15700.0, -1.05),
    ('A0V',  9700.0,  0.55),
    ('A5V',  8080.0,  1.95),
    ('F0V',  7220.0,  2.65),
    ('F5V',  6510.0,  3.40),
    ('G0V',  5980.0,  4.30),
    ('G5V',  5660.0,  4.85),
    ('K0V',  5280.0,  5.50),
    ('K5V',  4410.0,  6.95),
    ('M0V',  3870.0,  8.50),
    ('M2V',  3550.0,  9.55),
    ('M4V',  3210.0, 11.10),
    ('M5V',  3030.0, 12.30),
    ('M6V',  2850.0, 13.55),
    ('M7V',  2650.0, 14.40),
    ('M8V',  2500.0, 15.40),
    ('L0V',  2270.0, 17.20),
]


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def _f(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        out = float(value)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(out):
        return None
    return out


def _planck_jy(lam_um: np.ndarray, teff_k: float) -> np.ndarray:
    """Return Planck B_nu (in arbitrary Jy-equivalent units) for an
    array of wavelengths in microns at temperature ``teff_k``.

    Constants are dropped (the curve is rescaled to fit the
    photometry) so the absolute normalisation does not matter.
    """
    h = 6.626e-34
    c = 2.998e8
    kB = 1.381e-23
    lam_m = lam_um * 1e-6
    nu = c / lam_m
    x = h * nu / (kB * teff_k)
    # B_nu ~ nu^3 / (exp(x) - 1); drop common prefactors
    with np.errstate(over='ignore', invalid='ignore'):
        bnu = (nu ** 3) / np.expm1(x)
    bnu = np.where(np.isfinite(bnu), bnu, 0.0)
    return bnu


def _fit_blackbody(
    lams_um: np.ndarray,
    fluxes_jy: np.ndarray,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Fit a blackbody to (lam_um, F_nu Jy) photometry.

    Mirrors starometer/index.html: for each candidate Teff in a
    20 K grid from 2200 to 12000 K, evaluate the Planck B_nu
    template at the photometric wavelengths, solve for the best
    multiplicative scale via weighted least squares (default
    sigma = 8% of flux), and keep the (Teff, scale) pair with
    minimum chi^2.

    :return: tuple ``(teff_k, scale, chi2_red)`` or
             ``(None, None, None)`` if the fit failed.
    """
    if lams_um.size < 3:
        return None, None, None
    fluxes = np.asarray(fluxes_jy, dtype=float)
    sigmas = np.maximum(0.08 * np.abs(fluxes), 1.0e-9)
    weights = 1.0 / (sigmas ** 2)
    best = None
    for teff_k in range(2200, 12001, 20):
        model = _planck_jy(lams_um, float(teff_k))
        if not np.all(np.isfinite(model)) or np.any(model <= 0):
            continue
        denom = float(np.sum(weights * model * model))
        if denom <= 0:
            continue
        scale = float(np.sum(weights * model * fluxes) / denom)
        if scale <= 0:
            continue
        resid = fluxes - scale * model
        chi2 = float(np.sum(weights * resid * resid))
        if best is None or chi2 < best[2]:
            best = (float(teff_k), scale, chi2)
    if best is None:
        return None, None, None
    dof = max(lams_um.size - 2, 1)
    return best[0], best[1], best[2] / dof


# ---------------------------------------------------------------
# SED plot
# ---------------------------------------------------------------
def _make_sed_figure(
    pts: List[Tuple[float, float, str, str, float]],
    teff: Optional[float],
    objname: str,
) -> Any:
    """Build a Bokeh SED figure. ``pts`` is a list of
    ``(lambda_um, flux_jy, label, colour, mag)`` tuples.

    Matches starometer: Fν (Jy) on log y-axis with explicit
    ticks at [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20];
    wavelength on log x-axis (μm).
    """
    lams = np.array([p[0] for p in pts])
    fluxes = np.array([p[1] for p in pts])
    labels = [p[2] for p in pts]
    colors = [p[3] for p in pts]
    mags = np.array([p[4] for p in pts])

    src = ColumnDataSource(data=dict(
        lam=lams, flux=fluxes, label=labels,
        color=colors, mag=mags,
    ))

    fig = figure(
        x_axis_type='log', y_axis_type='log',
        x_axis_label='Wavelength [μm]',
        y_axis_label='Fν  [Jy]',
        title='Spectral Energy Distribution',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        active_scroll='wheel_zoom',
        sizing_mode='stretch_width',
        height=420,
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    fig.grid.grid_line_color = '#aaaaaa'
    fig.grid.grid_line_alpha = 0.35
    fig.grid.minor_grid_line_color = '#cccccc'
    fig.grid.minor_grid_line_alpha = 0.20

    # Explicit y-axis ticks per starometer (Jy, semi-log)
    y_ticks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5,
               1.0, 2.0, 5.0, 10.0, 20.0]
    y_labels = {0.01: '0.01', 0.02: '0.02', 0.05: '0.05',
                0.1: '0.1', 0.2: '0.2', 0.5: '0.5',
                1.0: '1', 2.0: '2', 5.0: '5',
                10.0: '10', 20.0: '20'}
    fig.yaxis.ticker = FixedTicker(ticks=y_ticks)
    fig.yaxis.major_label_overrides = y_labels

    # Dashed connecting line through the photometry
    fig.line(lams, fluxes, line_color='#888888',
             line_width=1.5, line_dash='dashed', alpha=0.7,
             legend_label='Photometry')

    # Blackbody overlay: weighted chi^2 fit over a Teff grid
    # (starometer-style), independent of the YAML Teff value.
    # The catalogue Teff (if any) is shown as a secondary dotted
    # curve for comparison.
    fit_teff, fit_scale, _chi2 = _fit_blackbody(lams, fluxes)
    lam_grid = np.logspace(np.log10(0.3), np.log10(30.0), 400)
    if fit_teff is not None and fit_scale is not None:
        bb_fit = _planck_jy(lam_grid, fit_teff) * fit_scale
        fig.line(
            lam_grid, bb_fit,
            line_color='#222222', line_width=2.2, alpha=0.95,
            legend_label=(
                'Blackbody fit (Teff={0:.0f} K)'.format(fit_teff)
            ),
        )
    if teff is not None and teff > 0 and (
            fit_teff is None
            or abs(teff - fit_teff) > 50.0):
        bnu_cat = _planck_jy(lam_grid, teff)
        bnu_at_data = _planck_jy(lams, teff)
        ok = (bnu_at_data > 0) & np.isfinite(fluxes)
        scale_cat = (
            float(np.median(fluxes[ok] / bnu_at_data[ok]))
            if ok.any() else 1.0
        )
        fig.line(
            lam_grid, bnu_cat * scale_cat,
            line_color='#888888', line_width=1.5,
            line_dash='dotted', alpha=0.85,
            legend_label=(
                'Catalogue Teff={0:.0f} K'.format(teff)
            ),
        )

    # Photometry points (coloured + outlined)
    fig.scatter('lam', 'flux', source=src, size=11,
                fill_color='color', line_color='black',
                line_width=0.8, marker='circle',
                legend_label='Bands')

    # Crosshair + hover
    fig.add_tools(CrosshairTool(dimensions='both',
                                line_color='#555555',
                                line_alpha=0.5))
    fig.add_tools(HoverTool(tooltips=[
        ('Band', '@label'),
        ('λ [μm]', '@lam{0.000}'),
        ('mag', '@mag{0.00}'),
        ('Fν [Jy]', '@flux{0.0000}'),
    ], mode='mouse'))

    fig.legend.click_policy = 'hide'
    fig.legend.location = 'bottom_left'
    fig.legend.background_fill_alpha = 0.7
    fig.title.text = 'SED: {0}'.format(objname)
    return fig


def build_sed_plot_json(
    entry: Optional[Dict[str, Any]],
    target_id: str = 'op-sed-plot-div',
) -> Dict[str, Any]:
    """Build the SED Bokeh plot payload.

    :param entry: astrometric YAML entry dict (or None)
    :param target_id: DOM target id (kept for parity with other
                      builders; uses script/div embedding)
    :return: ``{has_plot: bool, script: str, div: str,
                message: str}``
    """
    if not isinstance(entry, dict):
        return {'has_plot': False,
                'message': 'No astrometric entry available.'}
    objname = (entry.get('APERO_NAME')
               or entry.get('ORIGINAL_NAME') or 'target')
    teff = _f(sp.get_value(entry, 'TEFF'))
    pts = []
    for key, label, lam, f0, col in SED_FILTERS:
        mag = _f(sp.get_value(entry, key))
        if mag is None:
            continue
        flux_jy = f0 * (10.0 ** (-0.4 * mag))
        pts.append((lam, flux_jy, label, col, mag))
    if len(pts) < 2:
        return {
            'has_plot': False,
            'message': ('Not enough photometry to build SED '
                        '(need >=2 bands, have {0}).').format(
                len(pts)),
        }
    fig = _make_sed_figure(pts, teff, str(objname))
    script, div = plot_to_components(fig)
    return {'has_plot': True, 'script': script, 'div': div,
            'message': ''}


# ---------------------------------------------------------------
# HR diagram plot
# ---------------------------------------------------------------
def _make_hr_figure(
    bp_rp_target: Optional[float],
    mg_target: Optional[float],
    objname: str,
    neighborhood: Optional[List[Dict[str, float]]] = None,
) -> Any:
    """Build a Bokeh HR figure matching starometer.

    x-axis: G_BP - G_RP (linear).
    y-axis: M_G (absolute Gaia G), flipped so brighter is up.
    Background: Gaia stars within 20 pc as a faint orange scatter
    (no quality cuts beyond non-null mags + Plx > 50 mas).
    Target: large orange star with white outline.
    """
    fig = figure(
        x_axis_label='G_BP − G_RP  [mag]',
        y_axis_label='Absolute Gaia G   M_G  [mag]',
        title='HR Diagram',
        x_range=(-0.2, 4.5),
        tools='pan,wheel_zoom,box_zoom,reset,save',
        active_scroll='wheel_zoom',
        sizing_mode='stretch_width',
        height=480,
        background_fill_color=base.PLOT_BACKGROUND_COLOR,
    )
    # Apply y-axis flip declared in plot_manager.OBJ_PLOTS['hr']
    # immediately, so brighter (smaller M_G) sits at the top.
    try:
        from apero_ri.plots.plot_manager import OBJ_PLOTS as _OPM
        if _OPM.get('hr') and _OPM['hr'].yflip:
            fig.y_range.flipped = True
    except Exception:  # noqa: BLE001
        fig.y_range.flipped = True
    fig.grid.grid_line_color = '#aaaaaa'
    fig.grid.grid_line_alpha = 0.35
    fig.grid.minor_grid_line_color = '#cccccc'
    fig.grid.minor_grid_line_alpha = 0.20

    if neighborhood:
        nb_x = np.array([d.get('bp_rp') for d in neighborhood],
                        dtype=float)
        nb_y = np.array([d.get('m_g') for d in neighborhood],
                        dtype=float)
        ok = np.isfinite(nb_x) & np.isfinite(nb_y)
        if ok.any():
            nb_src = ColumnDataSource(data=dict(
                bp_rp=nb_x[ok], m_g=nb_y[ok],
            ))
            fig.scatter('bp_rp', 'm_g', source=nb_src, size=5,
                        fill_color='#ffb068', line_color=None,
                        fill_alpha=0.70,
                        legend_label='Gaia stars within 20 pc')

    # Target star
    if bp_rp_target is not None and mg_target is not None:
        tgt_src = ColumnDataSource(data=dict(
            bp_rp=[bp_rp_target], m_g=[mg_target],
            name=[objname],
        ))
        fig.scatter('bp_rp', 'm_g', source=tgt_src,
                    marker='star', size=24,
                    fill_color='#ff3b1f', fill_alpha=1.0,
                    line_color='#ffffff', line_width=2.0,
                    legend_label=str(objname))

    fig.add_tools(CrosshairTool(dimensions='both',
                                line_color='#555555',
                                line_alpha=0.5))
    fig.add_tools(HoverTool(tooltips=[
        ('G_BP−G_RP', '@bp_rp{0.00}'),
        ('M_G', '@m_g{0.00}'),
    ], mode='mouse'))

    # Brighter (smaller M_G) at top - already applied above via
    # plot_manager.OBJ_PLOTS['hr'].yflip; reassert here for safety.
    fig.y_range.flipped = True

    fig.legend.click_policy = 'hide'
    fig.legend.location = 'top_right'
    fig.legend.background_fill_alpha = 0.7
    fig.title.text = 'HR Diagram: {0}'.format(objname)
    return fig


def build_hr_plot_json(
    entry: Optional[Dict[str, Any]],
    neighborhood: Optional[List[Dict[str, float]]] = None,
    target_id: str = 'op-hr-plot-div',
) -> Dict[str, Any]:
    """Build the HR-diagram Bokeh plot payload.

    :param entry: astrometric YAML entry dict (or None)
    :param neighborhood: optional 20-pc Gaia star list, each item
                         a dict with keys ``bp_rp`` (mag) and
                         ``m_g`` (abs G mag).
    :param target_id: DOM target id (kept for parity with other
                      builders; uses script/div embedding)
    :return: ``{has_plot, script, div, message}``
    """
    if not isinstance(entry, dict):
        return {'has_plot': False,
                'message': 'No astrometric entry available.'}
    objname = (entry.get('APERO_NAME')
               or entry.get('ORIGINAL_NAME') or 'target')
    plx = _f(sp.get_value(entry, 'PLX'))
    g = _f(sp.get_value(entry, 'G_MAG'))
    gbp = _f(sp.get_value(entry, 'GBP_MAG'))
    grp = _f(sp.get_value(entry, 'GRP_MAG'))

    mg_target = None
    if g is not None and plx is not None and plx > 0:
        # plx in mas → distance modulus form (starometer style)
        mg_target = g + 5.0 * math.log10(plx) - 10.0

    bp_rp_target = None
    if gbp is not None and grp is not None:
        bp_rp_target = gbp - grp

    if mg_target is None or bp_rp_target is None:
        return {'has_plot': False,
                'message': ('Need Gaia G, BP, RP and parallax '
                            'to place this target on the HR '
                            'diagram.')}

    fig = _make_hr_figure(bp_rp_target, mg_target, str(objname),
                          neighborhood=neighborhood)
    script, div = plot_to_components(fig)
    return {'has_plot': True, 'script': script, 'div': div,
            'message': ''}


# ---------------------------------------------------------------
# 20-pc Gaia neighborhood loader (with on-disk cache).
# Lives here (not in a separate module) so the plot builder is
# self-contained.  TTL is long because the neighborhood is
# essentially static.
# ---------------------------------------------------------------
NEIGHBOR_CACHE_TTL_DAYS = 90
NEIGHBOR_PARALLAX_LIMIT_MAS = 50.0  # 1/0.020 arcsec  -> 20 pc


def load_or_query_20pc_neighborhood(
    cache_path: Optional[str] = None,
    timeout: int = 60,
) -> List[Dict[str, float]]:
    """Return a list of dicts ``[{bp_rp, m_g}, ...]`` for Gaia
    stars within 20 pc, matching starometer's HR backdrop.

    Uses a JSON on-disk cache when ``cache_path`` is given;
    queries Vizier ("I/355/gaiadr3") if the cache is stale,
    missing, or in the legacy ``{teff, mg}`` schema.

    Returns an empty list (and never raises) on any failure.
    """
    import json
    import os
    import time as _time

    # --- read cache (only accept the v2 schema with bp_rp) ---
    if cache_path and os.path.exists(cache_path):
        try:
            mtime = os.path.getmtime(cache_path)
            age_days = (_time.time() - mtime) / 86400.0
            if age_days < NEIGHBOR_CACHE_TTL_DAYS:
                with open(cache_path, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    items = data.get('items') or []
                    if (isinstance(items, list) and items
                            and isinstance(items[0], dict)
                            and 'bp_rp' in items[0]
                            and 'm_g' in items[0]):
                        return [d for d in items
                                if isinstance(d, dict)]
        except Exception:
            pass

    # --- query Vizier (Gaia DR3 mirror, starometer-style) ---
    try:
        from apero.core import drs_astrometrics as dra
    except Exception:
        return []
    adql = (
        'SELECT TOP 800 BPmag, RPmag, Gmag, Plx '
        'FROM "I/355/gaiadr3" '
        'WHERE Plx > {0} '
        'AND BPmag IS NOT NULL '
        'AND RPmag IS NOT NULL '
        'AND Gmag IS NOT NULL'
    ).format(NEIGHBOR_PARALLAX_LIMIT_MAS)
    try:
        payload = dra._vizier_json(adql, timeout=timeout)
    except Exception:
        payload = None
    items: List[Dict[str, float]] = []
    if isinstance(payload, dict):
        rows = payload.get('data') or []
        # Column order matches SELECT: BPmag, RPmag, Gmag, Plx
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) < 4:
                continue
            try:
                bp = float(row[0])
                rp = float(row[1])
                gmag = float(row[2])
                plx = float(row[3])
            except (TypeError, ValueError):
                continue
            if (not math.isfinite(bp) or not math.isfinite(rp)
                    or not math.isfinite(gmag)
                    or not math.isfinite(plx) or plx <= 0):
                continue
            m_g = gmag + 5.0 * math.log10(plx) - 10.0
            items.append({'bp_rp': bp - rp, 'm_g': m_g})

    # --- write cache ---
    if cache_path and items:
        try:
            os.makedirs(os.path.dirname(cache_path),
                        exist_ok=True)
            tmp = cache_path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump({'items': items,
                           'count': len(items),
                           'schema': 'bp_rp_mg_v1'}, fh)
            os.replace(tmp, cache_path)
        except Exception:
            pass
    return items


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
