#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Plot registry for the data portal object page.

Defines :class:`PlotClass` (a lightweight metadata descriptor for a
single rendered plot) and provides two ordered registries:

- :data:`OBJ_PLOTS`   – all object-page Bokeh plots
- :data:`DEBUG_PLOTS` – all debug plot sections

Each :class:`PlotClass` instance declares:

``title``
    Human-readable plot title.
``description``
    Brief description shown in the UI.
``plot_key``
    API payload key (e.g. ``"spec"``, ``"snr"``).
``div_id``
    The HTML element id of the Bokeh target ``<div>``.
``yaxiszoom``
    Ordered list of zoom options to show in the y-axis zoom
    control.  Supported values are integers (sigma multiples) or
    the string ``"full"``.  **An empty list disables the control
    entirely.**
``full_screen``
    ``True`` if a full-screen / maximise button should be shown.
``load``
    ``"auto"`` – plot loads automatically when the tab is opened.
    ``"generate"`` – plot is generated only on explicit user action.
``section``
    Logical grouping key used by the API (``"spectrum"``,
    ``"ccf"``, ``"time_series"``, ``"debug"``).

Usage example::

    from apero_ri.plots.plot_manager import OBJ_PLOTS

    for key, plot in OBJ_PLOTS.items():
        if not plot.yaxiszoom:
            print(key, "has no y-axis zoom control")

Created on 2026-04-10

@author: cook
"""

from __future__ import annotations

from typing import Dict, List

from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.plots.plot_manager"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# PlotClass
# =============================================================================
class PlotClass:
    """Metadata descriptor for a single rendered plot.

    All attributes are set after instantiation; there are no
    constructor arguments.

    Attribute reference
    -------------------
    title : str
        Human-readable plot title displayed in the page UI.

    description : str
        One-paragraph explanation shown in tooltips / info panels.

    plot_key : str
        Short identifier string that links this descriptor to the data
        flowing through the system.  The same key is used in **three**
        places that must stay in sync:

        1. **API payload** – the ``result[plot_key]`` entry returned by
           ``api_object_plots`` / ``api_debug_plots`` in
           ``apero_ri/application/data_portal_api_helpers.py``.
        2. **Timing dict** – the ``server_timings_ms[plot_key]`` entry
           stored in the cache and read by ``build_admin_cache_context``
           in ``apero_ri/application/admin_cache_helpers.py``.
        3. **Plot registry** – the key in :data:`OBJ_PLOTS` /
           :data:`DEBUG_PLOTS` (this file).

    div_id : str
        The ``id`` attribute of the target ``<div>`` element in the
        object page HTML template.  Defined in:

            ``apero_ri/templates/data_portal/object_page.html``

        The JS in ``apero_ri/static/js/object_page.js`` uses this id to
        find the container when calling ``Bokeh.embed.embed_item`` and
        when wiring y-axis zoom controls (``ensureYAxisControl``).

    yaxiszoom : list
        Controls the y-axis zoom widget rendered above the plot.

        * **Non-empty list** – the widget is shown; each entry becomes
          one ``<option>`` in the zoom ``<select>`` drop-down.
          Integers are treated as sigma multiples (e.g. ``3`` →
          "3 sig"); the string ``"full"`` means "show all data".
        * **Empty list** – the widget is *suppressed* for this plot.
          Suppression is implemented in ``ensureYAxisControl`` in
          ``apero_ri/static/js/object_page.js`` by checking the
          ``data-op-nozoom="1"`` attribute on the parent wrapper
          ``<div>`` (set in
          ``apero_ri/templates/data_portal/object_page.html``).

    yflip : bool
        If ``True`` the y-axis is flipped (smallest value at the top,
        largest at the bottom).  Currently used by the HR diagram so
        that brighter (smaller absolute magnitude) stars sit at the
        top.  Builders consult this flag via
        ``OBJ_PLOTS[<key>].yflip`` and apply
        ``fig.y_range.flipped = True`` immediately after constructing
        the Bokeh figure.

    full_screen : bool
        ``True`` if a maximise / full-screen button should be rendered
        for this plot.  The button links to the route defined as
        ``ri_object_plot_max`` in
        ``apero_ri/application/routes.py``, passing ``plot_key`` as
        ``plot_key=``.

    load : str
        ``"auto"``     – the plot is requested automatically when the
                         parent tab is first opened.
        ``"generate"`` – the plot is *not* fetched at page load; the
                         user must click a "Generate" button.  Used for
                         expensive on-demand plots (e.g. telluric map).

    section : str
        Logical API group passed to the ``plot_group`` query-parameter
        of ``/api/data-portal/object-plots``.  Allowed values come from
        ``valid_groups`` in ``api_object_plots`` in
        ``apero_ri/application/data_portal_api_helpers.py``:
        ``"spectrum"``, ``"ccf"``, ``"time_series"`` (object plots) or
        ``"debug"`` (debug plots, handled by a separate endpoint).
    """

    def __init__(self) -> None:
        self.title: str = ""
        self.description: str = ""
        self.plot_key: str = ""
        self.div_id: str = ""
        # Non-empty list = show y-axis zoom with those options.
        # Empty list     = no zoom control for this plot.
        # Suppression is enforced via data-op-nozoom="1" on the wrapper
        # <div> in object_page.html + ensureYAxisControl in object_page.js.
        self.yaxiszoom: List = [3, 5, 10, "full"]
        # Flip the y-axis (smaller value at top).  Builders should
        # apply fig.y_range.flipped = True early when this is set.
        self.yflip: bool = False
        self.full_screen: bool = False
        # "auto"     – loaded automatically on tab open
        # "generate" – user must click a generate button
        self.load: str = "auto"
        self.section: str = ""

    def __repr__(self) -> str:
        return (
            f"PlotClass(key={self.plot_key!r},"
            f" title={self.title!r},"
            f" yaxiszoom={self.yaxiszoom!r})"
        )


# =============================================================================
# Object-page plot registry
# =============================================================================
# SNR plot ----------------------------------------------------------------
_snr = PlotClass()
_snr.title = "Signal-to-Noise Ratio"
_snr.description = (
    "SNR in H and Y bands vs time."
    " QC failures are shown as cross markers."
)
_snr.plot_key = "snr"
_snr.div_id = "op-snr-plot-div"
_snr.yaxiszoom = [3, 5, 10, "full"]
_snr.full_screen = True
_snr.load = "auto"
_snr.section = "spectrum"

# BERV plot ---------------------------------------------------------------
_berv = PlotClass()
_berv.title = "BERV Coverage"
_berv.description = (
    "Barycentric Earth Radial Velocity vs time."
    " Green = passed QC, blue/red = failed QC stages."
)
_berv.plot_key = "berv"
_berv.div_id = "op-berv-plot-div"
_berv.yaxiszoom = []
_berv.full_screen = True
_berv.load = "auto"
_berv.section = "spectrum"

# Median spectrum plot ----------------------------------------------------
_spec = PlotClass()
_spec.title = "Median Spectrum"
_spec.description = (
    "Median S1D spectrum built from all observations."
    " Shows the blaze-normalised spectral flux."
)
_spec.plot_key = "spec"
_spec.div_id = "op-spec-plot-div"
# Median spectrum has a very wide flux range across orders;
# sigma-clipping the y-axis is misleading so the control is hidden.
_spec.yaxiszoom = []
_spec.full_screen = True
_spec.load = "auto"
_spec.section = "spectrum"

# CCF RV plot -------------------------------------------------------------
_ccf_rv = PlotClass()
_ccf_rv.title = "CCF Radial Velocity"
_ccf_rv.description = (
    "CCF-derived radial velocity vs time."
    " Systemic velocity subtracted when available."
)
_ccf_rv.plot_key = "ccf_rv"
_ccf_rv.div_id = "op-ccf-rv-plot-div"
_ccf_rv.yaxiszoom = [3, 5, 10, "full"]
_ccf_rv.full_screen = True
_ccf_rv.load = "auto"
_ccf_rv.section = "ccf"

# Median CCF profile plot -------------------------------------------------
_ccf_profile = PlotClass()
_ccf_profile.title = "Median CCF Profile"
_ccf_profile.description = (
    "Median CCF profile stacked from all observations."
    " Percentile envelope shown; Gaussian fit overlaid."
)
_ccf_profile.plot_key = "ccf_profile"
_ccf_profile.div_id = "op-ccf-profile-plot-div"
# CCF profile is a narrow Gaussian; sigma-clipping is unhelpful here.
_ccf_profile.yaxiszoom = []
_ccf_profile.full_screen = True
_ccf_profile.load = "auto"
_ccf_profile.section = "ccf"

# Time-series SNR plot ----------------------------------------------------
_ts_snr = PlotClass()
_ts_snr.title = "Time Series SNR"
_ts_snr.description = (
    "Per-order SNR time series showing the highest signal orders."
)
_ts_snr.plot_key = "ts_snr"
_ts_snr.div_id = "op-ts-snr-plot-div"
_ts_snr.yaxiszoom = [3, 5, 10, "full"]
_ts_snr.full_screen = True
_ts_snr.load = "auto"
_ts_snr.section = "time_series"

# Time-series airmass plot ------------------------------------------------
_ts_airmass = PlotClass()
_ts_airmass.title = "Time Series Airmass"
_ts_airmass.description = (
    "Airmass vs observation number, colour-coded by date."
)
_ts_airmass.plot_key = "ts_airmass"
_ts_airmass.div_id = "op-ts-airmass-plot-div"
_ts_airmass.yaxiszoom = [3, 5, 10, "full"]
_ts_airmass.full_screen = True
_ts_airmass.load = "auto"
_ts_airmass.section = "time_series"

# LBL velocity plot -------------------------------------------------------
_lbl = PlotClass()
_lbl.title = "LBL Velocity"
_lbl.description = (
    "LBL radial-velocity time series per science+template flavor."
    " Whiskers show per-epoch uncertainties."
)
_lbl.plot_key = "lbl"
# LBL plot divs are created dynamically by renderLbl() in JS using the
# pattern 'op-lbl-vel-plot-<sidToken>'.  div_id is intentionally left
# empty here; the JS identifies LBL divs by that prefix.
_lbl.div_id = ""
_lbl.yaxiszoom = [5, 10, 20, "full"]
_lbl.full_screen = True
_lbl.load = "auto"
_lbl.section = "lbl"

# SED plot ----------------------------------------------------------------
_sed = PlotClass()
_sed.title = "Spectral Energy Distribution"
_sed.description = (
    "SED built from Gaia BP/G/RP, 2MASS J/H/Ks and AllWISE "
    "W1/W2/W3 photometry stored in the astrometric YAML entry."
    " A blackbody curve at the catalogued Teff is overlaid for"
    " context."
)
_sed.plot_key = "sed"
_sed.div_id = "op-sed-plot-div"
# log-log axes - sigma-clipped y-zoom would be misleading.
_sed.yaxiszoom = []
_sed.full_screen = True
_sed.load = "auto"
_sed.section = "target_info"

# HR diagram plot ---------------------------------------------------------
_hr = PlotClass()
_hr.title = "HR Diagram"
_hr.description = (
    "Hertzsprung-Russell diagram (Teff vs absolute Gaia G mag)"
    " with the local 20-pc Gaia neighborhood as a faint backdrop"
    " and the Pecaut & Mamajek MS reference."
)
_hr.plot_key = "hr"
_hr.div_id = "op-hr-plot-div"
_hr.yaxiszoom = []
_hr.yflip = True
_hr.full_screen = True
_hr.load = "auto"
_hr.section = "target_info"

# Public object-plot registry (insertion-ordered)
OBJ_PLOTS: Dict[str, PlotClass] = {
    "sed": _sed,
    "hr": _hr,
    "snr": _snr,
    "berv": _berv,
    "spec": _spec,
    "ccf_rv": _ccf_rv,
    "ccf_profile": _ccf_profile,
    "ts_snr": _ts_snr,
    "ts_airmass": _ts_airmass,
    "lbl": _lbl,
}


# =============================================================================
# Debug-plot registry
# =============================================================================
_dbg_extsmax = PlotClass()
_dbg_extsmax.title = "Maximum Saturation Level"
_dbg_extsmax.description = (
    "Maximum saturation level measured at time of extraction."
)
_dbg_extsmax.plot_key = "extsmax"
_dbg_extsmax.div_id = "op-debug-extsmax-div"
_dbg_extsmax.yaxiszoom = [3, 5, 10, "full"]
_dbg_extsmax.full_screen = True
_dbg_extsmax.load = "auto"
_dbg_extsmax.section = "debug"

_dbg_effron = PlotClass()
_dbg_effron.title = "Effective Readout Noise"
_dbg_effron.description = (
    "Measured effective readout noise before extraction."
)
_dbg_effron.plot_key = "effron"
_dbg_effron.div_id = "op-debug-effron-div"
_dbg_effron.yaxiszoom = [3, 5, 10, "full"]
_dbg_effron.full_screen = True
_dbg_effron.load = "auto"
_dbg_effron.section = "debug"

_dbg_version = PlotClass()
_dbg_version.title = "APERO Processing Debug"
_dbg_version.description = (
    "APERO version and processing date from the file header."
    " Offline reductions show a flat line;"
    " online reductions should be one-to-one with the Date axis."
)
_dbg_version.plot_key = "version"
_dbg_version.div_id = "op-debug-version-div"
_dbg_version.yaxiszoom = [3, 5, 10, "full"]
_dbg_version.full_screen = True
_dbg_version.load = "auto"
_dbg_version.section = "debug"

_dbg_cdt = PlotClass()
_dbg_cdt.title = "Calibration Time Deltas"
_dbg_cdt.description = (
    "Time between each observation and the calibration used."
    " Reference calibrations (purple) diverge by design;"
    " same-night calibrations (orange) should be near zero."
)
_dbg_cdt.plot_key = "cdt"
_dbg_cdt.div_id = "op-debug-cdt-div"
_dbg_cdt.yaxiszoom = [3, 5, 10, "full"]
_dbg_cdt.full_screen = True
_dbg_cdt.load = "auto"
_dbg_cdt.section = "debug"

_dbg_tcorr_map = PlotClass()
_dbg_tcorr_map.title = "Telluric Map"
_dbg_tcorr_map.description = (
    "Telluric map of e2dsff_tcorr_A files, low-passed and"
    " corrected for the star's barycentric motion."
    " QC pass/fail shown to the right."
)
_dbg_tcorr_map.plot_key = "tcorr_map"
_dbg_tcorr_map.div_id = "op-debug-tcorr-map-div"
_dbg_tcorr_map.yaxiszoom = []
_dbg_tcorr_map.full_screen = True
_dbg_tcorr_map.load = "generate"
_dbg_tcorr_map.section = "debug"

# Public debug-plot registry (insertion-ordered)
DEBUG_PLOTS: Dict[str, PlotClass] = {
    "extsmax": _dbg_extsmax,
    "effron": _dbg_effron,
    "version": _dbg_version,
    "cdt": _dbg_cdt,
    "tcorr_map": _dbg_tcorr_map,
}


# =============================================================================
# Convenience helpers
# =============================================================================
def no_yzoom_div_ids() -> List[str]:
    """Return the ``div_id`` values for all plots that have no y-axis zoom.

    :return: list of element id strings for plots without y-axis zoom
    :rtype: list[str]
    """
    result: List[str] = []
    for registry in (OBJ_PLOTS, DEBUG_PLOTS):
        for plot in registry.values():
            if not plot.yaxiszoom and plot.div_id:
                result.append(plot.div_id)
    return result


# =============================================================================
# End of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")
