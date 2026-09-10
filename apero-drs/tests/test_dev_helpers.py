#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for APERO developer configuration helpers."""

from pathlib import Path

from apero.dev import get_uconfig_path


# =============================================================================
# Define functions
# =============================================================================
def test_get_uconfig_path_creates_complete_test_configuration() -> None:
    """Developer setup should create all configuration files needed by tests."""
    uconfig = Path(get_uconfig_path('SPIROU'))
    expected = [
        'database.yaml',
        'install.yaml',
        'user_config.yaml',
        'user_constants.yaml',
        'user_keywords.yaml',
    ]

    assert uconfig.is_dir()
    assert all((uconfig / filename).is_file() for filename in expected)