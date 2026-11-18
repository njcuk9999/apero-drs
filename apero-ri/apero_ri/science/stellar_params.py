#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - stellar parameter accessors.

Provides a thin, typed read layer over the apero astrometric YAML
schema.  Most "derived" quantities (galactic coords, U/V/W, stellar
mass/radius, log g, photometric Teff and [Fe/H]) are already computed
by ``apero.core.drs_astrometrics._derive_fields`` and stored in the
yaml under their own keys, so this module mostly just looks them up.

Where a derived value is NOT present in the yaml (older entries,
partial entries) we compute it on the fly from the primary catalog
fields when possible.

Created on 2026-04-22

@author: cook
"""
import math
from typing import Any, Dict, Optional, Tuple

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.science.stellar_params'


# =============================================================================
# Define helpers
# =============================================================================
def _nested_value(entry: Dict[str, Any], key: str) -> Any:
    """Pull ``entry[key]`` returning either a scalar or the ``value``
    sub-key of a ``{value, source, units}`` block.

    :param entry: dict, the yaml-loaded astrometric entry
    :param key: str, top-level key to look up
    :return: the scalar value, or None if missing/null
    """
    if not isinstance(entry, dict):
        return None
    block = entry.get(key)
    if block is None:
        return None
    if isinstance(block, dict):
        return block.get('value')
    return block


def _nested_attr(entry: Dict[str, Any], key: str, attr: str) -> Any:
    """Pull a sub-attribute (``source`` or ``units``) of a value block.

    :param entry: dict, the yaml-loaded astrometric entry
    :param key: str, top-level key
    :param attr: str, sub-attribute name (e.g. ``'source'``, ``'units'``)
    :return: the attribute value, or None
    """
    if not isinstance(entry, dict):
        return None
    block = entry.get(key)
    if isinstance(block, dict):
        return block.get(attr)
    return None


def _to_float(value: Any) -> Optional[float]:
    """Convert ``value`` to float when possible, returning None otherwise.

    :param value: any value
    :return: float or None
    """
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(out):
        return None
    return out


# =============================================================================
# Single-value accessors
# =============================================================================
def get_value(entry: Dict[str, Any], key: str,
              fallback_keys: Optional[Tuple[str, ...]] = None) -> Any:
    """Return the ``value`` of ``key`` (or the first matching fallback).

    :param entry: dict, the yaml-loaded astrometric entry
    :param key: str, primary yaml key
    :param fallback_keys: tuple of str, additional keys to try in order
    :return: the resolved value or None
    """
    val = _nested_value(entry, key)
    if val is not None:
        return val
    if fallback_keys:
        for fk in fallback_keys:
            val = _nested_value(entry, fk)
            if val is not None:
                return val
    return None


def get_source(entry: Dict[str, Any], key: str) -> Optional[str]:
    """Return the ``source`` sub-key of ``key`` (or None).

    :param entry: dict, the yaml-loaded astrometric entry
    :param key: str, top-level yaml key
    :return: source string or None
    """
    src = _nested_attr(entry, key, 'source')
    return None if src is None else str(src)


def get_units(entry: Dict[str, Any], key: str,
              default: Optional[str] = None) -> Optional[str]:
    """Return the ``units`` sub-key of ``key`` (or ``default``).

    :param entry: dict, the yaml-loaded astrometric entry
    :param key: str, top-level yaml key
    :param default: str or None, value to return when units are absent
    :return: units string or default
    """
    u = _nested_attr(entry, key, 'units')
    if u is None:
        return default
    return str(u)


# =============================================================================
# Derived computations (used as fallbacks when the yaml lacks a field)
# =============================================================================
def absolute_mag(apparent: Optional[float],
                 parallax_mas: Optional[float]) -> Optional[float]:
    """Compute ``M = m - 5*log10(d_pc) + 5`` from parallax in mas.

    :param apparent: float, apparent magnitude
    :param parallax_mas: float, trigonometric parallax in mas
    :return: absolute magnitude, or None
    """
    m = _to_float(apparent)
    plx = _to_float(parallax_mas)
    if m is None or plx is None or plx <= 0:
        return None
    distance_pc = 1000.0 / plx
    return m - 5.0 * math.log10(distance_pc) + 5.0


def distance_pc(parallax_mas: Optional[float]) -> Optional[float]:
    """Convert parallax in mas to distance in parsecs.

    :param parallax_mas: float, trigonometric parallax in mas
    :return: distance in pc, or None for non-positive/NaN parallax
    """
    plx = _to_float(parallax_mas)
    if plx is None or plx <= 0:
        return None
    return 1000.0 / plx


def luminosity(radius_rsun: Optional[float],
               teff_k: Optional[float],
               teff_sun_k: float = 5778.0) -> Optional[float]:
    """Compute ``L/Lsun = (R/Rsun)^2 * (Teff/Tsun)^4``.

    :param radius_rsun: float, stellar radius in solar radii
    :param teff_k: float, effective temperature in K
    :param teff_sun_k: float, solar Teff (default 5778 K)
    :return: luminosity in solar luminosities, or None
    """
    r = _to_float(radius_rsun)
    t = _to_float(teff_k)
    if r is None or t is None or t <= 0:
        return None
    return (r ** 2) * ((t / teff_sun_k) ** 4)


# =============================================================================
# End of code
# =============================================================================
