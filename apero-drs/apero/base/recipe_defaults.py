#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lightweight recipe defaults.

This module is intentionally import-only and avoids any runtime imports so
recipes can access shared defaults without triggering heavy APERO setup.

Created on 2026-07-02

@author: cook
"""

# =============================================================================
# Define variables
# =============================================================================
DATABASE_NAMES = ['calib', 'tellu', 'findex', 'log', 'astrom', 'reject']
DATABASE_FULLNAMES = ['calibration', 'telluric', 'file index', 'recipe log',
                      'astrometric', 'rejection']

# =============================================================================
# End of code
# =============================================================================

