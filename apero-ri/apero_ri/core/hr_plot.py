#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - HR diagram plot generation.

Plots the target on a Teff vs absolute G-magnitude diagram with
the Pecaut & Mamajek (2013) main-sequence reference table as a
backdrop.  When parallax is missing the absolute magnitude is
omitted and the target is shown only by its Teff.

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

import base64
import io
import math
from typing import Any, Dict, Optional

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from apero_ri.science import stellar_params as sp


__NAME__ = 'apero_ri.core.hr_plot'

# Compact subset of Pecaut & Mamajek (2013) updated table
# (V5 columns: SpT, Teff [K], Mg [Gaia G abs mag])
# Source: Eric Mamajek's online table (cdsweb), Aug 2022 rev.
# Used only as a visual backdrop for the user's target.
_PM_TABLE = [
    # SpT,  Teff(K), M_G
    ('O5V', 41500, -5.20),
    ('B0V', 31400, -3.10),
    ('B5V', 15700, -1.05),
    ('A0V',  9700,  0.55),
    ('A5V',  8080,  1.95),
    ('F0V',  7220,  2.65),
    ('F5V',  6510,  3.40),
    ('G0V',  5980,  4.30),
    ('G5V',  5660,  4.85),
    ('K0V',  5280,  5.50),
    ('K5V',  4410,  6.95),
    ('M0V',  3870,  8.50),
    ('M2V',  3550,  9.55),
    ('M4V',  3210, 11.10),
    ('M5V',  3030, 12.30),
    ('M6V',  2850, 13.55),
    ('M7V',  2650, 14.40),
    ('M8V',  2500, 15.40),
    ('L0V',  2270, 17.20),
]


def generate_hr_plot(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an HR diagram for *entry* as a base64 PNG.

    :param entry: dict, the loaded astrometric YAML entry
    :return: ``{success, image, title, error}``
    """
    if not isinstance(entry, dict):
        return dict(success=False, image='', title='',
                    error='No entry data')
    objname = entry.get('APERO_NAME') or entry.get(
        'ORIGINAL_NAME') or 'target'
    teff = _f(sp.get_value(entry, 'TEFF'))
    plx = _f(sp.get_value(entry, 'PLX'))
    g = _f(sp.get_value(entry, 'G_MAG'))
    if teff is None or not np.isfinite(teff):
        return dict(
            success=False, image='', title='',
            error='Missing Teff for this target.',
        )

    mg_target = None
    if (g is not None and plx is not None
            and np.isfinite(g) and np.isfinite(plx)
            and plx > 0):
        # M = m + 5*log10(plx_arcsec) + 5
        # plx in mas -> arcsec /1000
        mg_target = g + 5.0 * math.log10(plx / 1000.0) + 5.0

    fig, ax = plt.subplots(figsize=(7.5, 6.0), dpi=110)
    pm_t = np.array([row[1] for row in _PM_TABLE])
    pm_m = np.array([row[2] for row in _PM_TABLE])
    pm_lab = [row[0] for row in _PM_TABLE]
    ax.plot(pm_t, pm_m, '-', color='#888', lw=1.2,
            label='Pecaut & Mamajek MS')
    ax.scatter(pm_t, pm_m, s=14, color='#888', zorder=2)
    # spectral-type labels (annotate every other point)
    for i, lab in enumerate(pm_lab):
        if i % 2 == 0:
            ax.annotate(lab, (pm_t[i], pm_m[i]),
                        textcoords='offset points',
                        xytext=(4, 2), fontsize=7,
                        color='#666')

    title_extra = ''
    if mg_target is not None:
        ax.scatter([teff], [mg_target], s=200, marker='*',
                   color='#e63946', edgecolor='black',
                   linewidth=0.8, zorder=4,
                   label=f'{objname} (Teff={teff:.0f} K, '
                         f'M_G={mg_target:.2f})')
        title_extra = (
            f' (Teff={teff:.0f}K, M_G={mg_target:.2f})')
    else:
        ax.axvline(teff, color='#e63946', lw=1.5,
                   ls='--', alpha=0.7,
                   label=f'{objname} (Teff={teff:.0f} K)')
        title_extra = f' (Teff={teff:.0f}K)'

    ax.set_xscale('log')
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_xlabel('Teff [K]')
    ax.set_ylabel(r'Absolute Gaia G magnitude $M_G$')
    ax.set_title(f'HR Diagram: {objname}{title_extra}')
    ax.grid(True, which='both', ls=':', alpha=0.4)
    ax.legend(fontsize=8, loc='upper left')
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return dict(
        success=True,
        image=base64.b64encode(buf.getvalue()).decode('ascii'),
        title=f'HR: {objname}',
        error='',
    )


def _f(value: Any) -> Optional[float]:
    """Coerce *value* to ``float`` (or ``None``)."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
