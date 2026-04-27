#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Build legacy ``obj_props`` dicts from astrometric YAML
entries.

The data-portal finder/TESS code paths expect ``obj_props`` rows
loaded from the per-instrument ``object_table.json`` (column
labels like ``RA [Deg]``).  The astrometrics resolve page works
only with raw YAML entries (``RA: {value, source, units}``).

This helper bridges the two so the same backend code can be
called from either page.

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from astropy.time import Time

from apero_ri.science import stellar_params as sp


__NAME__ = 'apero_ri.core.yaml_obj_props'


def yaml_to_obj_props(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an astrometric YAML entry to an ``obj_props`` row.

    The keys returned mirror the columns produced by the
    apero_object_table task so finder/TESS code can consume the
    output unchanged.

    :param entry: dict, the loaded astrometric YAML entry
    :return: dict with keys ``OBJNAME``, ``RA [Deg]``, ``Dec [Deg]``,
             ``EPOCH [JD]``, ``Plx [mas]``, ``PMRA [mas/yr]``,
             ``PMDE [mas/yr]``, ``ALIASES``, plus the magnitude
             columns (``G_MAG``, ``J_MAG``, ``H_MAG``, ``KS_MAG``)
             used to seed the primary target on the finder chart.
    """
    if not isinstance(entry, dict):
        return {}

    # epoch is stored in JD already in the yaml (e.g. 2457388.5)
    epoch_jd = sp.get_value(entry, 'EPOCH')
    if epoch_jd is None:
        # fall back to Gaia EDR3
        epoch_jd = Time(2016.0, format='decimalyear').jd

    aliases_raw = entry.get('ALIASES') or []
    if isinstance(aliases_raw, list):
        aliases = '|'.join(str(a) for a in aliases_raw if a)
    else:
        aliases = str(aliases_raw)

    out: Dict[str, Any] = {
        'OBJNAME': entry.get('APERO_NAME') or entry.get(
            'ORIGINAL_NAME') or '',
        'RA [Deg]': _f(sp.get_value(entry, 'RA')),
        'Dec [Deg]': _f(sp.get_value(entry, 'DEC')),
        'EPOCH [JD]': _f(epoch_jd),
        'Plx [mas]': _f(sp.get_value(entry, 'PLX')) or 0.0,
        'PMRA [mas/yr]': _f(sp.get_value(entry, 'PMRA')) or 0.0,
        'PMDE [mas/yr]': _f(
            sp.get_value(entry, 'PMDE',
                         fallback_keys=('PMDEC',))) or 0.0,
        'ALIASES': aliases,
        # primary-target seed magnitudes (used to fix the
        # suptitle Jmag when 2MASS times out)
        'G_MAG': _f(sp.get_value(entry, 'G_MAG')),
        'J_MAG': _f(sp.get_value(entry, 'J_MAG')),
        'H_MAG': _f(sp.get_value(entry, 'H_MAG')),
        'KS_MAG': _f(sp.get_value(entry, 'KS_MAG')),
    }
    return out


def _f(value: Any) -> Optional[float]:
    """Coerce *value* to ``float`` (or ``None`` on failure)."""
    if value is None:
        return None
    try:
        f = float(value)
    except (ValueError, TypeError):
        return None
    return f


def aliases_from_yaml(entry: Dict[str, Any]) -> List[str]:
    """Return the ALIASES list from a YAML entry as a list of str.

    :param entry: dict, the loaded astrometric YAML entry
    :return: list of alias strings (may be empty)
    """
    if not isinstance(entry, dict):
        return []
    raw = entry.get('ALIASES') or []
    if isinstance(raw, list):
        return [str(a).strip() for a in raw if a]
    return [s.strip() for s in str(raw).split('|') if s.strip()]
