#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - shared target-information section descriptors.

This module defines the canonical, ordered list of sections that
appear under "Target Information" both:
  - in the data-portal object page  (``target_info`` tab), and
  - in the astrometrics page         (``resolve target`` tab).

Adding (or reordering) a section here updates BOTH pages
automatically.

Each section is one of:

  * a **data section** -- a key/value grid built by a row-builder
    callable that takes the loaded astrometric YAML entry and returns
    a list of row dicts ``{label, value, units, source, key,
    precision, editable, flaggable}``;

  * a **chart section** -- a placeholder card identified by
    ``chart_type`` (``'finder'``, ``'rotation'``, ``'sed'``,
    ``'hr_diagram'``) that the client renders using its own logic.

Layout order matches the user-requested grouping:
  1. Identity
  2. Astrometry & Coordinates
  3. Kinematics
  4. Photometry
  5. Stellar Parameters
  6. Telluric Windows
  7. Finder Chart
  8. Rotation Periods
  9. Spectral Energy Distribution
 10. HR Diagram
 11. Status (provenance: first/last edit, author, status flag)

Created on 2026-04-22

@author: cook
"""
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

from apero_ri.science import stellar_params as sp
from apero_ri.components.target_info_citations import CITATIONS


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.components.target_info_sections'

# Public chart types known to the client renderer.
CHART_FINDER = 'finder'
CHART_ROTATION = 'rotation'
CHART_SED = 'sed'
CHART_HR = 'hr_diagram'


# =============================================================================
# Row helpers
# =============================================================================
def _row(entry: Dict[str, Any], key: str, label: str,
         units: Optional[str] = None,
         precision: Optional[int] = None,
         editable: bool = True,
         flaggable: bool = True,
         fallback_keys: Optional[List[str]] = None,
         citation: Optional[str] = None) -> Dict[str, Any]:
    """Build a single row dict from a yaml entry.

    Reads ``entry[key]['value' / 'source' / 'units']`` (or scalar) using
    the helpers in :mod:`apero_ri.science.stellar_params`.

    :param entry: dict, the loaded astrometric YAML entry
    :param key: str, top-level YAML key to read
    :param label: str, human-readable label for the UI
    :param units: str or None, override units (else read from yaml)
    :param precision: int or None, suggested decimal places for the
                     client-side formatter
    :param editable: bool, can a moderator edit this value
    :param flaggable: bool, can any user flag this value as bad
    :param fallback_keys: list of alternative keys to try if ``key`` is
                         missing
    :return: row dict ``{key, label, value, units, source, precision,
             editable, flaggable}``
    """
    val = sp.get_value(entry, key,
                       tuple(fallback_keys) if fallback_keys else None)
    if units is None:
        units = sp.get_units(entry, key)
    src = sp.get_source(entry, key)
    return {
        'key': key,
        'label': label,
        'value': val,
        'units': units,
        'source': src,
        'precision': precision,
        'editable': editable,
        'flaggable': flaggable,
        'citation': citation,
        'citation_text': CITATIONS.get(citation) if citation else None,
    }


def _row_literal(label: str, value: Any,
                 units: Optional[str] = None,
                 precision: Optional[int] = None,
                 source: Optional[str] = None,
                 key: Optional[str] = None,
                 editable: bool = False,
                 flaggable: bool = False) -> Dict[str, Any]:
    """Build a row from a directly supplied value (no yaml lookup).

    Used for derived/computed fields where the value is calculated
    rather than read from the yaml.

    :param label: str, display label
    :param value: any, the value to show
    :param units: str or None, units string
    :param precision: int or None, decimal-place hint
    :param source: str or None, source citation
    :param key: str or None, identifier for editing/flagging
    :param editable: bool, can be edited
    :param flaggable: bool, can be flagged
    :return: row dict
    """
    return {
        'key': key,
        'label': label,
        'value': value,
        'units': units,
        'source': source,
        'precision': precision,
        'editable': editable,
        'flaggable': flaggable,
        'citation': None,
        'citation_text': None,
    }


# =============================================================================
# Per-section row builders
# =============================================================================
def _build_identity(entry: Dict[str, Any],
                    obj_row: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identity rows: names, aliases, classification, epoch.

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, optional row from the data-portal
                   object_table (header-derived names)
    :return: list of row dicts
    """
    rows: List[Dict[str, Any]] = []
    rows.append(_row(entry, 'APERO_NAME', 'APERO Name',
                     editable=False, flaggable=False))
    rows.append(_row(entry, 'ORIGINAL_NAME', 'Original Name'))
    rows.append(_row(entry, 'SIMBAD_NAME', 'SIMBAD Name'))
    rows.append(_row(entry, 'APERO_CLASS', 'APERO Class'))
    rows.append(_row(entry, 'EPOCH', 'Epoch (JD)', units='JD',
                     precision=2))
    aliases_val = entry.get('ALIASES')
    if isinstance(aliases_val, (list, tuple)):
        aliases_val = list(aliases_val)
    rows.append(_row_literal('Aliases', aliases_val, key='ALIASES',
                             editable=True, flaggable=True))
    rows.append(_row(entry, 'KEYWORDS', 'Keywords'))
    rows.append(_row(entry, 'NOTES', 'Notes'))
    if obj_row is not None:
        for src_key, label in (
            ('OBJNAME', 'OBJECT name(s) in headers'),
            ('PP_VERSION', 'OB Name(s) in headers'),
            ('PP_PI_NAME', 'PI name(s) in headers'),
            ('PP_PROG_ID', 'Project/Run name(s) in headers'),
        ):
            val = obj_row.get(src_key)
            if val is not None:
                rows.append(_row_literal(label, val,
                                         editable=False, flaggable=False))
    return rows


def _build_astrometry(entry: Dict[str, Any],
                      obj_row: Optional[Dict[str, Any]]
                      ) -> List[Dict[str, Any]]:
    """Astrometry & coordinates rows.

    Includes both the catalog (epoch-of-observation) coordinates and
    the J2000-propagated coords with sexagesimal formatting.

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, unused (kept for signature parity)
    :return: list of row dicts
    """
    _ = obj_row
    rows: List[Dict[str, Any]] = []
    rows.append(_row(entry, 'RA', 'RA (catalog)', units='deg',
                     precision=7))
    rows.append(_row(entry, 'DEC', 'Dec (catalog)', units='deg',
                     precision=7))
    rows.append(_row(entry, 'RA_J2000_DEG', 'RA (J2000)', units='deg',
                     precision=7, editable=False))
    rows.append(_row(entry, 'DEC_J2000_DEG', 'Dec (J2000)', units='deg',
                     precision=7, editable=False))
    rows.append(_row(entry, 'RA_HMS', 'RA (J2000) HMS',
                     editable=False))
    rows.append(_row(entry, 'DEC_DMS', 'Dec (J2000) DMS',
                     editable=False))
    rows.append(_row(entry, 'GALACTIC_LON', 'Galactic longitude l',
                     units='deg', precision=4, editable=False))
    rows.append(_row(entry, 'GALACTIC_LAT', 'Galactic latitude b',
                     units='deg', precision=4, editable=False))
    rows.append(_row(entry, 'ECLIPTIC_LON', 'Ecliptic longitude \u03bb',
                     units='deg', precision=4, editable=False))
    rows.append(_row(entry, 'ECLIPTIC_LAT', 'Ecliptic latitude \u03b2',
                     units='deg', precision=4, editable=False))
    plx = sp.get_value(entry, 'PLX')
    plx_units = sp.get_units(entry, 'PLX', default='mas')
    plx_src = sp.get_source(entry, 'PLX')
    dist_pc = sp.distance_pc(plx)
    plx_label = 'Parallax'
    if dist_pc is not None:
        plx_value_str = '{0:.4f} ({1:.2f} pc)'.format(float(plx), dist_pc)
        rows.append({
            'key': 'PLX',
            'label': plx_label,
            'value': plx_value_str,
            'units': plx_units,
            'source': plx_src,
            'precision': None,
            'editable': True,
            'flaggable': True,
        })
    else:
        rows.append(_row(entry, 'PLX', plx_label, units='mas',
                         precision=4))
    rows.append(_row(entry, 'PMRA', 'PMRA (\u03bc\u03b1*)',
                     units='mas/yr', precision=3))
    rows.append(_row(entry, 'PMDE', 'PMDE (\u03bc\u03b4)',
                     units='mas/yr', precision=3))
    return rows


def _build_kinematics(entry: Dict[str, Any],
                      obj_row: Optional[Dict[str, Any]]
                      ) -> List[Dict[str, Any]]:
    """Kinematics rows: RV and Galactic UVW + total/sky velocities.

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, unused
    :return: list of row dicts
    """
    _ = obj_row
    rows: List[Dict[str, Any]] = []
    rows.append(_row(entry, 'RV', 'Radial velocity', units='km/s',
                     precision=2))
    rows.append(_row(entry, 'V_SKY', 'v_sky', units='km/s',
                     precision=2, editable=False))
    rows.append(_row(entry, 'V3D', 'v_3D', units='km/s',
                     precision=2, editable=False))
    rows.append(_row(entry, 'U', 'U (galactic)', units='km/s',
                     precision=2, editable=False, citation='js87_uvw'))
    rows.append(_row(entry, 'V', 'V (galactic)', units='km/s',
                     precision=2, editable=False, citation='js87_uvw'))
    rows.append(_row(entry, 'W', 'W (galactic)', units='km/s',
                     precision=2, editable=False, citation='js87_uvw'))
    return rows


def _build_photometry(entry: Dict[str, Any],
                      obj_row: Optional[Dict[str, Any]]
                      ) -> List[Dict[str, Any]]:
    """Photometric magnitudes and absolute mags.

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, unused
    :return: list of row dicts
    """
    _ = obj_row
    rows: List[Dict[str, Any]] = []
    bands = [
        ('G_MAG', 'G', 'mag'),
        ('GBP_MAG', 'G_BP', 'mag'),
        ('GRP_MAG', 'G_RP', 'mag'),
        ('J_MAG', 'J', 'mag'),
        ('H_MAG', 'H', 'mag'),
        ('KS_MAG', 'Ks', 'mag'),
        ('W1_MAG', 'W1', 'mag'),
        ('W2_MAG', 'W2', 'mag'),
        ('W3_MAG', 'W3', 'mag'),
        ('W4_MAG', 'W4', 'mag'),
    ]
    for key, label, units in bands:
        if key in entry:
            rows.append(_row(entry, key, label, units=units,
                             precision=4))
    rows.append(_row(entry, 'AMAG_G', 'M_G (absolute)', units='mag',
                     precision=3, editable=False))
    rows.append(_row(entry, 'AMAG_KS', 'M_Ks (absolute)', units='mag',
                     precision=3, editable=False))
    return rows


def _build_stellar_params(entry: Dict[str, Any],
                          obj_row: Optional[Dict[str, Any]]
                          ) -> List[Dict[str, Any]]:
    """Stellar parameters: Teff, [Fe/H], radius, mass, log g, L.

    Uses both the apero-derived fields (M-dwarf calibrations) and the
    Gaia DR3 GSP-Phot / FLAME astrophysical parameters when available.

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, unused
    :return: list of row dicts
    """
    _ = obj_row
    rows: List[Dict[str, Any]] = []
    rows.append(_row(entry, 'TEFF', 'Teff (catalog / SIMBAD)',
                     units='K', precision=0))
    rows.append(_row(entry, 'TEFF_GAIA_JH',
                     'Teff (G_BP-G_RP + J-H) [Mann+15]',
                     units='K', precision=0, editable=False,
                     citation='mann15_teff_bprp_jh'))
    rows.append(_row(entry, 'TEFF_GAIA',
                     'Teff (G_BP-G_RP) [Mann+15]',
                     units='K', precision=0, editable=False,
                     citation='mann15_teff_bprp'))
    rows.append(_row(entry, 'GAIA_TEFF_GSPPHOT',
                     'Teff (Gaia DR3 GSP-Phot)',
                     units='K', precision=0, editable=False,
                     citation='gaia_dr3_gspphot'))
    rows.append(_row(entry, 'SPT', 'Spectral type'))
    rows.append(_row(entry, 'FE_H', '[Fe/H]', units='dex',
                     precision=3, editable=False,
                     citation='duque23_feh'))
    rows.append(_row(entry, 'GAIA_MH_GSPPHOT',
                     '[M/H] (Gaia DR3 GSP-Phot)', units='dex',
                     precision=3, editable=False,
                     citation='gaia_dr3_gspphot'))
    rows.append(_row(entry, 'R_STAR_MKS',
                     'R\u2605 (M_Ks) [Mann+15]', units='R\u2299',
                     precision=3, editable=False,
                     citation='mann15_radius_mks'))
    rows.append(_row(entry, 'R_STAR_MKS_FEH',
                     'R\u2605 (M_Ks + [Fe/H]) [Mann+15]',
                     units='R\u2299', precision=3, editable=False,
                     citation='mann15_radius_mks_feh'))
    rows.append(_row(entry, 'GAIA_RADIUS_FLAME',
                     'R\u2605 (Gaia DR3 FLAME)', units='R\u2299',
                     precision=3, editable=False,
                     citation='gaia_dr3_flame'))
    rows.append(_row(entry, 'MASS_STAR_MANN15',
                     'M\u2605 (M_Ks) [Mann+15]', units='M\u2299',
                     precision=3, editable=False,
                     citation='mann15_mass_mks'))
    rows.append(_row(entry, 'MASS_STAR_DELFOSSE00',
                     'M\u2605 (M_K) [Delfosse+00]', units='M\u2299',
                     precision=3, editable=False,
                     citation='delfosse00_mass_mk'))
    rows.append(_row(entry, 'GAIA_MASS_FLAME',
                     'M\u2605 (Gaia DR3 FLAME)', units='M\u2299',
                     precision=3, editable=False,
                     citation='gaia_dr3_flame'))
    rows.append(_row(entry, 'LOG_G', 'log g', units='cgs',
                     precision=3, editable=False,
                     citation='logg_from_mr'))
    rows.append(_row(entry, 'GAIA_LOGG_GSPPHOT',
                     'log g (Gaia DR3 GSP-Phot)', units='cgs',
                     precision=3, editable=False,
                     citation='gaia_dr3_gspphot'))
    rows.append(_row(entry, 'L_STAR', 'L\u2605', units='L\u2299',
                     precision=4, editable=False,
                     citation='lum_from_rt'))
    rows.append(_row(entry, 'GAIA_LUM_FLAME',
                     'L\u2605 (Gaia DR3 FLAME)', units='L\u2299',
                     precision=4, editable=False,
                     citation='gaia_dr3_flame'))
    rows.append(_row(entry, 'VSINI', 'v sin(i)', units='km/s',
                     precision=2))
    return rows


def _build_telluric(entry: Dict[str, Any],
                    obj_row: Optional[Dict[str, Any]]
                    ) -> List[Dict[str, Any]]:
    """Telluric-overlap window summaries.

    These are derived in apero from the orbital barycentric correction
    sampled over a non-leap year.

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, unused
    :return: list of row dicts
    """
    _ = obj_row
    rows: List[Dict[str, Any]] = []
    rows.append(_row(entry, 'TELLURIC_VSYS_PLUS_VBARY_MIN',
                     'min |v_sys + v_bary,orb|',
                     units='km/s', precision=2, editable=False))
    rows.append(_row(entry, 'TELLURIC_VSYS_PLUS_VBARY_MAX',
                     'max |v_sys + v_bary,orb|',
                     units='km/s', precision=2, editable=False))
    rows.append(_row(entry, 'TELLURIC_LIMIT_WINDOWS',
                     'Telluric-overlap windows',
                     editable=False))
    return rows


def _build_status(entry: Dict[str, Any],
                  obj_row: Optional[Dict[str, Any]]
                  ) -> List[Dict[str, Any]]:
    """Provenance / status rows: who created the entry & when, etc.

    These five keys are populated by ``apero.core.drs_astrometrics``
    on every write (including back-fill of legacy entries).

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, unused
    :return: list of row dicts
    """
    _ = obj_row
    rows: List[Dict[str, Any]] = []
    rows.append(_row(entry, 'STATUS', 'Status',
                     editable=True, flaggable=False))
    rows.append(_row(entry, 'FIRST_UPDATED', 'First updated',
                     editable=False, flaggable=False))
    first_author_row = _row(entry, 'FIRST_AUTHOR', 'First author',
                            editable=False, flaggable=False)
    first_author = str(entry.get('FIRST_AUTHOR') or '').strip()
    if first_author:
        first_author_row['value_url'] = (
            '/user_portal/users/' + quote(first_author, safe='')
        )
    rows.append(first_author_row)
    rows.append(_row(entry, 'LAST_EDIT', 'Last edit',
                     editable=False, flaggable=False))
    last_author_row = _row(entry, 'LAST_AUTHOR', 'Last author',
                           editable=False, flaggable=False)
    last_author = str(entry.get('LAST_AUTHOR') or '').strip()
    if last_author:
        last_author_row['value_url'] = (
            '/user_portal/users/' + quote(last_author, safe='')
        )
    rows.append(last_author_row)
    verifier = str(entry.get('VERIFIER') or '').strip()
    verifier_row = _row_literal(
        'Verifier',
        verifier or 'None',
        key='VERIFIER',
        editable=False,
        flaggable=False,
    )
    if verifier and verifier.lower() not in ('none', 'null'):
        verifier_row['value_url'] = (
            '/user_portal/users/' + quote(verifier, safe='')
        )
    rows.append(verifier_row)
    return rows


# =============================================================================
# Section descriptors
# =============================================================================
# A section is a dict with these keys:
#   id          : str        - stable identifier (used by API + CSS)
#   title       : str        - heading text
#   icon        : str        - Font Awesome class
#   kind        : str        - 'data' or 'chart'
#   description : str | None - optional intro paragraph (rendered above
#                              the section body)
#   build       : callable   - row builder (data sections only); takes
#                              (entry, obj_row) and returns list of rows
#   chart_type  : str | None - one of CHART_* constants (chart sections)
#   chart_id    : str | None - stable HTML id for the chart container
#                              (chart sections)
#
# The list order is the rendering order on both pages.
TARGET_INFO_SECTIONS: List[Dict[str, Any]] = [
    {
        'id': 'identity',
        'title': 'Identity',
        'icon': 'fa-solid fa-id-card',
        'kind': 'data',
        'description': None,
        'build': _build_identity,
    },
    {
        'id': 'astrometry',
        'title': 'Astrometry & Coordinates',
        'icon': 'fa-solid fa-location-crosshairs',
        'kind': 'data',
        'description': None,
        'build': _build_astrometry,
    },
    {
        'id': 'kinematics',
        'title': 'Kinematics',
        'icon': 'fa-solid fa-arrows-up-down-left-right',
        'kind': 'data',
        'description': None,
        'build': _build_kinematics,
    },
    {
        'id': 'photometry',
        'title': 'Photometry',
        'icon': 'fa-solid fa-palette',
        'kind': 'data',
        'description': None,
        'build': _build_photometry,
    },
    {
        'id': 'stellar_params',
        'title': 'Stellar Parameters',
        'icon': 'fa-solid fa-temperature-half',
        'kind': 'data',
        'description': (
            'Catalog values, photometric calibrations (Mann et al. 2015 '
            'and Duque-Arribas et al. 2023 for M-dwarfs) and Gaia DR3 '
            'astrophysical parameters (GSP-Phot / FLAME).'
        ),
        'build': _build_stellar_params,
    },
    {
        'id': 'telluric',
        'title': 'Telluric Windows',
        'icon': 'fa-solid fa-cloud',
        'kind': 'data',
        'description': (
            'Annual range of |v_sys + v_bary,orb| projected on the line '
            'of sight; small values mark windows where stellar lines '
            'overlap telluric features.'
        ),
        'build': _build_telluric,
    },
    {
        'id': 'status',
        'title': 'Status',
        'icon': 'fa-solid fa-circle-info',
        'kind': 'data',
        'description': (
            'Provenance metadata for this catalogue entry: when it was '
            'first created, when it was last edited, by whom, and the '
            'current vetting status (checked / pending / error).'
        ),
        'build': _build_status,
    },
    {
        'id': 'sed',
        'title': 'Spectral Energy Distribution',
        'icon': 'fa-solid fa-chart-area',
        'kind': 'chart',
        'chart_type': CHART_SED,
        'chart_id': 'op-sed-plot',
        'description': None,
    },
    {
        'id': 'hr_diagram',
        'title': 'HR Diagram',
        'icon': 'fa-solid fa-star-half-stroke',
        'kind': 'chart',
        'chart_type': CHART_HR,
        'chart_id': 'op-hr-diagram',
        'description': None,
    },
    {
        'id': 'finder_chart',
        'title': 'Finder Chart',
        'icon': 'fa-solid fa-crosshairs',
        'kind': 'chart',
        'chart_type': CHART_FINDER,
        'chart_id': 'op-finder-chart',
        'description': None,
    },
    {
        'id': 'rotation',
        'title': 'TESS Rotation Periods',
        'icon': 'fa-solid fa-arrows-rotate',
        'kind': 'chart',
        'chart_type': CHART_ROTATION,
        'chart_id': 'op-tess-rotation',
        'description': None,
    },
]


# =============================================================================
# Public API
# =============================================================================
def list_sections() -> List[Dict[str, Any]]:
    """Return the section descriptors as plain dicts (no callables).

    Useful for serialising the section list to the client when only
    the metadata (id / title / icon / kind) is needed.

    :return: list of metadata dicts
    """
    out: List[Dict[str, Any]] = []
    for sec in TARGET_INFO_SECTIONS:
        meta = {
            'id': sec['id'],
            'title': sec['title'],
            'icon': sec['icon'],
            'kind': sec['kind'],
            'description': sec.get('description'),
        }
        if sec['kind'] == 'chart':
            meta['chart_type'] = sec.get('chart_type')
            meta['chart_id'] = sec.get('chart_id')
        out.append(meta)
    return out


def _summary_property_token(row: Dict[str, Any]) -> str:
    """Return the stable property token for one target-info row."""
    key = str(row.get('key') or '').strip()
    if key:
        return key
    return str(row.get('label') or '').strip()


def _summary_property_id(
    section_id: str,
    row: Dict[str, Any],
) -> str:
    """Return the persisted property ID for one target-info row."""
    return '{0}::{1}'.format(
        section_id,
        _summary_property_token(row),
    )


def _skip_summary_property(row: Dict[str, Any]) -> bool:
    """Return True for rows that should not be selectable."""
    token = _summary_property_token(row).upper()
    label = str(row.get('label') or '').strip().upper()
    return token in {'OBJNAME', 'APERO_NAME'} or label == 'APERO NAME'


def build_target_info_property_catalog() -> List[Dict[str, Any]]:
    """Return selectable summary-table properties from target info."""
    obj_row = dict(
        OBJNAME='',
        PP_VERSION='',
        PP_PI_NAME='',
        PP_PROG_ID='',
    )
    catalog: List[Dict[str, Any]] = []
    seen = set()

    for section in TARGET_INFO_SECTIONS:
        if section.get('kind') != 'data':
            continue
        build = section.get('build')
        if build is None:
            continue
        try:
            rows = build(dict(), obj_row)
        except Exception:  # noqa: BLE001
            rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            prop_id = _summary_property_id(section['id'], row)
            if not _summary_property_token(row):
                continue
            if _skip_summary_property(row):
                continue
            if prop_id in seen:
                continue
            seen.add(prop_id)
            catalog.append(dict(
                id=prop_id,
                label=str(
                    row.get('label')
                    or _summary_property_token(row)
                ),
                token=_summary_property_token(row),
                section_id=section['id'],
                section_title=section['title'],
                section_description=(
                    section.get('description') or ''
                ),
                units=str(row.get('units') or ''),
            ))

    return catalog


def flatten_target_info_properties(
    entry: Dict[str, Any],
    obj_row: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Return summary-property values keyed by property ID."""
    if not isinstance(entry, dict):
        entry = {}
    if obj_row is not None and not isinstance(obj_row, dict):
        obj_row = None

    values: Dict[str, Dict[str, Any]] = dict()
    for section in TARGET_INFO_SECTIONS:
        if section.get('kind') != 'data':
            continue
        build = section.get('build')
        if build is None:
            continue
        try:
            rows = build(entry, obj_row)
        except Exception:  # noqa: BLE001
            rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            if not _summary_property_token(row):
                continue
            if _skip_summary_property(row):
                continue
            prop_id = _summary_property_id(section['id'], row)
            values[prop_id] = dict(
                id=prop_id,
                label=str(
                    row.get('label')
                    or _summary_property_token(row)
                ),
                value=row.get('value'),
                units=str(row.get('units') or ''),
                section_id=section['id'],
                section_title=section['title'],
            )

    return values


def build_target_info_payload(
        entry: Dict[str, Any],
        obj_row: Optional[Dict[str, Any]] = None,
        include_charts: bool = True,
        chart_ids: Optional[List[str]] = None,
        only_ids: Optional[List[str]] = None,
        exclude_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build the JSON payload that the client renderer consumes.

    :param entry: dict, the loaded astrometric YAML entry
    :param obj_row: dict or None, optional row from the data-portal
                   ``object_table.json`` (used to add header-derived
                   names to the Identity section)
    :param include_charts: bool, when False omit chart placeholder
                          sections from the output
    :param chart_ids: list[str] or None, when given (and
                      ``include_charts`` is True) keep only chart
                      sections whose ``id`` is in this list.
    :param only_ids: list[str] or None, when given keep only sections
                     (data or chart) whose ``id`` is in this list.
                     Applied AFTER ``include_charts``/``chart_ids``.
                     Useful when rendering one section into a
                     dedicated host card (e.g. HR Diagram or Status
                     on the data-portal object page).
    :param exclude_ids: list[str] or None, when given drop sections
                        whose ``id`` is in this list. Useful for the
                        target-info card on data-portal where some
                        sections are rendered as their own page-level
                        cards instead.
    :return: dict ``{sections: [...]}`` where each section has either
             ``rows`` (data) or ``chart_type``/``chart_id`` (chart)
    """
    if not isinstance(entry, dict):
        entry = {}
    only_set = set(only_ids) if only_ids is not None else None
    exclude_set = set(exclude_ids) if exclude_ids else set()
    sections_out: List[Dict[str, Any]] = []
    for sec in TARGET_INFO_SECTIONS:
        sid = sec['id']
        if sid in exclude_set:
            continue
        if only_set is not None and sid not in only_set:
            continue
        if sec['kind'] == 'data':
            builder: Callable[..., List[Dict[str, Any]]] = sec['build']
            try:
                rows = builder(entry, obj_row)
            except Exception:  # noqa: BLE001
                rows = []
            sections_out.append({
                'id': sid,
                'title': sec['title'],
                'icon': sec['icon'],
                'kind': 'data',
                'description': sec.get('description'),
                'rows': rows,
            })
        elif sec['kind'] == 'chart':
            if not include_charts:
                continue
            if chart_ids is not None and sid not in chart_ids:
                continue
            sections_out.append({
                'id': sid,
                'title': sec['title'],
                'icon': sec['icon'],
                'kind': 'chart',
                'description': sec.get('description'),
                'chart_type': sec.get('chart_type'),
                'chart_id': sec.get('chart_id'),
            })
    return {'sections': sections_out}


# =============================================================================
# End of code
# =============================================================================
