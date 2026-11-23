#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compatibility shim for legacy misspelled module name.

This module re-exports the real implementation from
``legacy_reject_gsheet`` so existing imports continue to work.
"""

from apero_ri.tasks.legacy_reject_gsheet import *  # noqa: F401,F403
