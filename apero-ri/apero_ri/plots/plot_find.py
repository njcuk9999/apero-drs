#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Finder chart plot generation (compatibility shim).

The implementation has moved to ``apero_ri.core.object_finder``.
This module re-exports ``generate_finder_charts`` so that any
existing imports from ``apero_ri.plots.plot_find`` keep working.
"""
# re-export the public API from the new location
from apero_ri.core.object_finder import (  # noqa: F401
    generate_finder_charts,
)

