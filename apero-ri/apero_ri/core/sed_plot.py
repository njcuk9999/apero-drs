#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - SED (Spectral Energy Distribution) plot generation.

Builds a simple SED plot from the photometry stored in the
astrometric YAML entry: Gaia BP/G/RP, 2MASS J/H/Ks and AllWISE
W1/W2/W3 magnitudes converted to AB-flux density (Jy) at the
filter effective wavelengths.

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

import base64
import io
from typing import Any, Dict, Optional

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from apero_ri.science import stellar_params as sp


__NAME__ = 'apero_ri.core.sed_plot'

# Filter effective wavelengths in micron (Vega zero-points
# for traditional photometry; we work entirely in apparent
# magnitudes here).
#   References for wavelengths and Vega zero fluxes:
#   - Gaia DR3: Riello+ 2021 (passband description)
#   - 2MASS: Cohen+ 2003 (J=1594, H=1024, Ks=666.7 Jy)
#   - AllWISE: Wright+ 2010 (W1=309.5, W2=171.8, W3=31.7 Jy)
#   Numbers chosen to give SED in Jansky from Vega magnitudes.
FILTERS = [
    # (key,           label, lambda_um, F0_Jy,  colour)
    ('GBP_MAG',  'Gaia BP', 0.5050,  3552.0, '#5fa8d3'),
    ('G_MAG',    'Gaia G',  0.6230,  3228.7, '#3a86ff'),
    ('GRP_MAG',  'Gaia RP', 0.7730,  2554.9, '#bd2c2c'),
    ('J_MAG',    '2MASS J', 1.235,   1594.0, '#7d4f1d'),
    ('H_MAG',    '2MASS H', 1.662,   1024.0, '#a06030'),
    ('KS_MAG',   '2MASS K', 2.159,   666.7,  '#bf6f3a'),
    ('W1_MAG',   'WISE W1', 3.353,   309.5,  '#7c3aed'),
    ('W2_MAG',   'WISE W2', 4.603,   171.8,  '#9d4edd'),
    ('W3_MAG',   'WISE W3', 11.561,  31.7,   '#c77dff'),
]


def generate_sed_plot(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an SED plot for *entry* and return as a base64 PNG.

    :param entry: dict, the loaded astrometric YAML entry
    :return: ``{success: bool, image: str (base64), bands: list,
                title: str, error: str}``
    """
    if not isinstance(entry, dict):
        return dict(success=False, image='', bands=[],
                    title='', error='No entry data')
    objname = entry.get('APERO_NAME') or entry.get(
        'ORIGINAL_NAME') or 'target'

    pts = []  # list of (lambda_um, flux_jy, label, colour, mag)
    for key, label, lam, f0, col in FILTERS:
        mag = sp.get_value(entry, key)
        if mag is None:
            continue
        try:
            mag = float(mag)
        except (ValueError, TypeError):
            continue
        if not np.isfinite(mag):
            continue
        flux = f0 * 10.0 ** (-0.4 * mag)
        pts.append((lam, flux, label, col, mag))

    if len(pts) < 2:
        return dict(
            success=False, image='', bands=[], title='',
            error=('Not enough photometry to build SED '
                   f'(need >=2 bands, have {len(pts)}).'),
        )

    fig, ax = plt.subplots(figsize=(7.5, 5.0), dpi=110)
    lams = np.array([p[0] for p in pts])
    fluxes = np.array([p[1] for p in pts])
    nu_fnu = (3e14 / lams) * fluxes  # nu*F_nu in Jy*Hz
    ax.plot(lams, nu_fnu, color='#888', lw=1.0, alpha=0.6,
            zorder=1)
    for lam, flux, label, col, mag in pts:
        nf = (3e14 / lam) * flux
        ax.scatter(lam, nf, s=80, color=col,
                   edgecolor='black', linewidth=0.6,
                   zorder=2, label=f'{label} ({mag:.2f})')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'Wavelength [$\mu$m]')
    ax.set_ylabel(r'$\nu F_\nu$ [Jy$\cdot$Hz]')
    ax.set_title(f'SED: {objname}')
    ax.grid(True, which='both', ls=':', alpha=0.4)
    ax.legend(fontsize=8, loc='best', frameon=True,
              ncol=2)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return dict(
        success=True,
        image=base64.b64encode(buf.getvalue()).decode('ascii'),
        bands=[p[2] for p in pts],
        title=f'SED: {objname}',
        error='',
    )
