#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – backwards-compatibility shim for plot_objects.

All plot-builder functions have moved to the modules listed below.
Import from those modules directly; this file re-exports everything so
that existing call-sites continue to work without modification.

    plot_obj_spectrum   – SNR / BERV / spectrum builders
    plot_obj_ccf        – CCF profile / RV builders
    plot_obj_lbl        – LBL RV time-series builders
    plot_obj_timeseries – observation-level time-series builders

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

# =============================================================================
# Re-export spectrum builders
# =============================================================================
from apero_ri.plots.plot_obj_spectrum import (
    build_berv_plot_components,
    build_berv_plot_json,
    build_snr_plot_components,
    build_snr_plot_json,
    build_spec_plot_components,
    build_spec_plot_json,
)

# =============================================================================
# Re-export CCF builders
# =============================================================================
from apero_ri.plots.plot_obj_ccf import (
    build_ccf_plot_components,
    build_ccf_plot_json,
    build_ccf_profile_plot_components,
    build_ccf_profile_plot_json,
    build_ccf_rv_plot_components,
    build_ccf_rv_plot_json,
)

# =============================================================================
# Re-export LBL builders
# =============================================================================
from apero_ri.plots.plot_obj_lbl import (
    build_lbl_plot_components,
    build_lbl_plots_json,
)

# =============================================================================
# Re-export time-series builders
# =============================================================================
from apero_ri.plots.plot_obj_timeseries import (
    build_ts_airmass_plot_components,
    build_ts_airmass_plot_json,
    build_ts_snr_plot_components,
    build_ts_snr_plot_json,
)

# =============================================================================
# End of code
# =============================================================================
