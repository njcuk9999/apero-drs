#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Base module.

Exposes package-level metadata and shared constants used throughout
the apero_ri package.

Created on 2024-01-01

@author: cook
"""

import warnings
from importlib.metadata import version
from pathlib import Path

import yaml

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = "apero_ri"
__version__ = version(__PACKAGE__)
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = "None"

# load the yaml file
__YAML__ = yaml.load(  # noqa: S506
    open(__PATH__.joinpath("info.yaml")),  # noqa: WPS515
    Loader=yaml.FullLoader,
)

# retrieve metadata from info.yaml
__authors__ = __YAML__["DRS.AUTHORS"]
__release__ = __YAML__["DRS.RELEASE"]

# retrieve date from _version module if available
try:
    from apero_ri._version import __date__
except ImportError:
    __date__ = ""

# =============================================================================
# Define yaml file names
# =============================================================================
INSTALL_YAML = "install.yaml"
DATABASE_YAML = "database.yaml"

# switch for no db in args
NO_DB = False

# =============================================================================
# Define shared constants
# =============================================================================
# Maps BLOCK_KIND SQL values to profile PATH_* configuration keys.
# Shared by apero_object_query and basket_funcs to keep the mapping
# canonical.
BLOCK_KIND: dict = {
    "raw": "PATH_RAW",
    "tmp": "PATH_PP",
    "calib": "PATH_CALIB",
    "red": "PATH_RED",
    "tellu": "PATH_TELLU",
    "out": "PATH_OUT",
    "lbl": "PATH_LBL",
}

# Shared plot background color (light yellow)
PLOT_BACKGROUND_COLOR: str = "#fff9dc"

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
