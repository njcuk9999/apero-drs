#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Developer functions that avoid some conditions of the loading the full
APERO package

Created on 2026-09-02 13:35


@author: cook
"""

from apero.dev import core


# Get APERO parameters without loading the full APERO package / installing APERO
get_base_params = core.get_base_params