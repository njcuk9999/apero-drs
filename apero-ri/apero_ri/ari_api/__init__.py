#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARI API client library.

Provides programmatic access to APERO Reduction Interface (ARI) data from
Python scripts and notebooks.  Only requires ``requests`` (no Flask or
apero-drs).

Quick start::

    from apero_ri import ari_api

    # First-time setup (stores token locally in ~/.ari/)
    ari_api.configure(server='https://ari.example.com', token='<your-token>')

    # List available profiles
    profiles = ari_api.list_profiles()

    # Work with a profile
    profile = ari_api.AperoProfile('spirou_xxs_08_cook_home')
    obj_table = profile.get_object_table()  # pandas DataFrame by default
    obs_table = profile.get_observation_table()

    # Get a single object
    obj = profile.get_object('GL699')
    info = obj.target_info()               # pandas DataFrame
    obj.get_data('/tmp/GL699_data')        # download files
"""

from apero_ri.ari_api.client import (
    AperoObject,
    AperoProfile,
    configure,
    list_profiles,
    list_profiles_detailed,
)

__all__ = [
    "configure",
    "list_profiles",
    "list_profiles_detailed",
    "AperoProfile",
    "AperoObject",
]
