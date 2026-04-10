#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Setup package initialisation.

Exposes first-run helpers so callers can do::

    from apero_ri.setup import is_setup_complete
    from apero_ri.setup import can_start_main_app
"""

# =============================================================================
# Imports
# =============================================================================
from apero_ri.setup.bootstrap import (
    can_start_main_app,
    ensure_directory_layout,
    is_legacy_local_install,
    is_setup_complete,
    resolve_local_data_dir,
    save_bootstrap_config,
    save_setup_state,
)

# =============================================================================
# Define variables
# =============================================================================
__all__ = [
    "can_start_main_app",
    "ensure_directory_layout",
    "is_legacy_local_install",
    "is_setup_complete",
    "resolve_local_data_dir",
    "save_bootstrap_config",
    "save_setup_state",
]

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
