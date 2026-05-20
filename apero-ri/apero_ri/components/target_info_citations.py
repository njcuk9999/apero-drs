#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - footnote / citation strings for the target-info table.

Used by the client renderer to attach a small superscript marker to a
parameter label and pop up a one-line provenance note.  The wording is
ours, but the references themselves are the canonical ones used by
Erik Artigau's "starometer" tool (github.com/eartigau/starometer):

  * Mann et al. 2015, ApJ 804, 64       -- M-dwarf empirical
                                            polynomials (Teff, R, M)
  * Delfosse et al. 2000, A&A 364, 217  -- M-dwarf K-band
                                            mass-luminosity
  * Duque-Arribas et al. 2023, ApJ 944, 88 -- photometric [Fe/H] for
                                              M-dwarfs
  * Johnson & Soderblom 1987, AJ 93, 864 -- galactic UVW convention
  * Pecaut & Mamajek 2013 / Mamajek 2018 -- AFGK empirical sequence
  * Gaia DR3 (Gaia Collaboration 2023)   -- GSP-Phot / FLAME
                                            astrophysical parameters

Created on 2026-04-22

@author: cook
"""
from typing import Dict


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.components.target_info_citations'

# Citation marker -> human-readable footnote string.  The marker keys
# match the trailing ``[<marker>]`` token added to row labels by the
# JS renderer when ``citation`` is set in the row dict.
CITATIONS: Dict[str, str] = {
    'mann15_teff_bprp_jh': (
        'Mann et al. 2015, ApJ 804, 64 - Table 2 row 11; Teff '
        'polynomial in (G_BP - G_RP) and (J - H); ~49 K scatter.'
    ),
    'mann15_teff_bprp': (
        'Mann et al. 2015, ApJ 804, 64 - Table 2 row 1; Teff '
        'polynomial in (G_BP - G_RP); ~52 K scatter.'
    ),
    'mann15_radius_mks': (
        'Mann et al. 2015, ApJ 804, 64 - Table 1 row 1; R_star '
        'polynomial in M_Ks; ~3% scatter.'
    ),
    'mann15_radius_mks_feh': (
        'Mann et al. 2015, ApJ 804, 64 - Table 1 row 2; R_star '
        'polynomial in M_Ks with a [Fe/H] term; ~3% scatter.'
    ),
    'mann15_mass_mks': (
        'Mann et al. 2015, ApJ 804, 64 - Table 1 mass-luminosity '
        'polynomial in M_Ks; ~2% scatter.'
    ),
    'delfosse00_mass_mk': (
        'Delfosse et al. 2000, A&A 364, 217; K-band '
        'mass-luminosity for M-dwarfs (valid for M_K in '
        '[4.5, 9.5]); ~10% scatter.'
    ),
    'duque23_feh': (
        'Duque-Arribas et al. 2023, ApJ 944, 88; photometric [Fe/H] '
        'from G_BP - G_RP, W1 - W2 and M_Ks; ~0.10 dex reliability.'
    ),
    'logg_from_mr': (
        'Reconstructed from the empirical mass and radius using '
        'log g = log g_sun + log10(M / Msun) - 2 log10(R / Rsun).'
    ),
    'lum_from_rt': (
        'Computed from R_star and Teff using L / Lsun = '
        '(R / Rsun)^2 (Teff / Tsun)^4 with Tsun = 5778 K.'
    ),
    'js87_uvw': (
        'Galactic U, V, W computed in the convention of '
        'Johnson & Soderblom 1987, AJ 93, 864 (U toward the galactic '
        'centre, V along galactic rotation, W toward the NGP); '
        'requires a measured radial velocity.'
    ),
    'gaia_dr3_gspphot': (
        'Gaia DR3 GSP-Phot astrophysical parameters '
        '(Gaia Collaboration 2023; Andrae et al. 2023, A&A 674, A27).'
    ),
    'gaia_dr3_flame': (
        'Gaia DR3 FLAME astrophysical parameters '
        '(Gaia Collaboration 2023; Creevey et al. 2023, A&A 674, A26).'
    ),
}


# =============================================================================
# End of code
# =============================================================================
