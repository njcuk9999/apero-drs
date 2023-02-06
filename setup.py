#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO setup.py for use with pip

pip install -U -e .

Created on 2023-02-06

@author: cook, Vandal
"""
import os
from pathlib import Path

from setuptools import setup

# =============================================================================
# Define variables
# =============================================================================
# define the instruments here
INSTRUMENTS = ["spirou", "nirps_ha", "nirps_he"]
# Get the package directory from this file name
PACKAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


# =============================================================================
# Define functions
# =============================================================================
def get_relative_path(path: str) -> Path:
    """
    Create a absolute path from a given relative path (relative to this
    dir)

    :param path: str, the relative path to this path

    :return: The absolute path from this directory
    """
    return PACKAGE_DIR.joinpath(path)


# =============================================================================
# Start of code
# =============================================================================
# get the absolute path for the bin directory
binpath = get_relative_path("apero/recipes")
# get the absolute path for the tools directory
tools_path = get_relative_path("apero/tools/recipes")
# storage for all paths where there could be scripts
paths = []
# loop around paths and get all sub-directories for bin directory
for path in binpath.iterdir():
    if path.is_dir() and path.name in INSTRUMENTS:
        paths.append(path)
# loop around paths and get all sub-directories for tools directory
for path in tools_path.iterdir():
    if path.is_dir():
        paths.append(path)
# Find all __init__.py files in paths
scripts = []
for path in paths:
    for f in path.iterdir():
        if f.is_file() and os.access(f, os.X_OK) and f.name != "__init__.py":
            scripts.append(os.path.relpath(str(f)))
# run the python setup using the list of scripts
setup(scripts=scripts)
