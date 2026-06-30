#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Top-level exports for APERO monitoring checks."""

from importlib import import_module

from apero_ri.apero_monitoring.checks import CHECKS


def _module(module_name: str):
    """Import one APERO-monitoring module by full dotted name."""
    return import_module(module_name)


# Keep top-level aliases used by task modules.
core = _module('apero_ri.apero_monitoring.core.core')
raw_common = _module('apero_ri.apero_monitoring.core.raw_common')
