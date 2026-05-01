#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO astrometric "database" (yaml-backed, no SQL)

A drop-in replacement for ``drs_database.AstrometricDatabase`` that emulates
an astrometric database from a directory of per-object yaml files living
under ``params['DRS_DATA_ASSETS']/astrometrics``.

Design goals:
    1. As fast as possible (in-memory cache, lazy load, mtime invalidation).
    2. No SQL / no DatabaseManager dependency.
    3. Multiprocessing-safe (picklable instances, file locking on writes).
    4. No imports from anywhere in ``apero`` (apero-drs); only ``aperocore``
       so this module can be used freely throughout apero-drs without
       circular imports.

Created on 2026-04-21

@author: cook

import rules:
    only from
    - aperocore.*
    - python stdlib + yaml + numpy
"""
import os
import json
import re
import string
import tempfile
import time
import warnings
import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import yaml

# Prefer the libyaml-backed C loader when available — ~7× faster than
# the pure-Python SafeLoader on a 1k+ yaml directory scan, which
# dominates ARI's astrometric-database list endpoint.
try:
    _YAML_SAFE_LOADER = yaml.CSafeLoader  # type: ignore[attr-defined]
except AttributeError:  # pragma: no cover - libyaml not built
    _YAML_SAFE_LOADER = yaml.SafeLoader

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc
from aperocore.core import drs_text

# fcntl is POSIX-only; on Windows we silently fall back to lock-file polling
try:
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - Windows fallback
    _fcntl = None

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.drs_astrometrics.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get astropy time from aperocore base
Time = base.Time
# get ParamDict
ParamDict = param_functions.ParamDict
# get exceptions / warnings
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# get Logging function
WLOG = drs_log.wlog
# define bad characters for objects (alpha numeric + "_") - replicated from
#   apero/instruments/default/instrument.py so this module has no apero-drs
#   dependency
BAD_OBJ_CHARS = [' '] + list(string.punctuation.replace('_', ''))
# define null text values (anything matching is treated as a null entry)
NULL_TEXT = ['', 'None', 'Null', 'NULL', 'null', 'nan', 'NaN', 'inf']
# reserved object names that are never resolved against the catalogue
RESERVED_OBJ_NAMES = ['CALIB', 'SKY', 'TEST']
# subdirectory under DRS_DATA_ASSETS that holds the per-object yaml files
ASTROM_SUBDIR = 'astrometrics'
# yaml file extension we recognise
YAML_EXT = '.yaml'
# name of the lock-file directory (sub of ASTROM_SUBDIR)
LOCK_SUBDIR = '.locks'
# keys in the yaml that are searched (in order) when resolving a name
NAME_KEYS = ['APERO_NAME', 'ORIGINAL_NAME', 'SIMBAD_NAME']
# key in the yaml that holds aliases
ALIAS_KEY = 'ALIASES'
# the key whose value is the canonical APERO name returned to callers
APERO_NAME_KEY = 'APERO_NAME'
# ----------------------------------------------------------------------------
# Provenance / status metadata keys (added on every entry; back-filled for
# legacy entries the first time they are touched). All five live at the
# top level of the yaml as plain scalars.
# ----------------------------------------------------------------------------
META_FIRST_UPDATED = 'FIRST_UPDATED'   # ISO date the entry was created
META_FIRST_AUTHOR = 'FIRST_AUTHOR'     # user that first created the entry
META_LAST_EDIT = 'LAST_EDIT'           # ISO date of the most recent edit
META_LAST_AUTHOR = 'LAST_AUTHOR'       # user that made the most recent edit
META_STATUS = 'STATUS'                 # one of STATUS_VALUES
META_KEYS = (META_FIRST_UPDATED, META_FIRST_AUTHOR,
             META_LAST_EDIT, META_LAST_AUTHOR, META_STATUS)
# allowed values for META_STATUS
# - 'verified' : monitor-verified, ready for production use
# - 'pending'  : auto-resolved or hand-edited, awaits human verification
# - 'rejected' : explicitly excluded from the astrometric database
# - 'checked'  : legacy synonym of 'verified' (back-compat only)
# - 'error'    : entry has known problems
STATUS_VALUES = ('verified', 'pending', 'rejected',
                 'checked', 'error')
# canonical status names (used as on-disk subdirectory names too)
STATUS_VERIFIED = 'verified'
STATUS_PENDING = 'pending'
STATUS_REJECTED = 'rejected'
# subset that maps 1:1 to a sub-directory under ASTROM_SUBDIR
STATUS_SUBDIRS = (STATUS_VERIFIED, STATUS_PENDING, STATUS_REJECTED)
# legacy status -> canonical status (for back-compat status reads)
STATUS_ALIASES: Dict[str, str] = {'checked': STATUS_VERIFIED}
# default status assigned to a freshly-added or back-filled entry
DEFAULT_STATUS = STATUS_PENDING
# default author used when no author is supplied (e.g. backfill, migration)
DEFAULT_AUTHOR = 'njcuk9999'

# ----------------------------------------------------------------------------
# Required-field schema (used by validation + auto-issue creation).
# An entry is "complete" iff all of REQUIRED_FIELDS_STAR are present
# (non-null) OR PMRA/PMDE may be absent when ``NO_PM`` is True.
# ----------------------------------------------------------------------------
# top-level boolean key: when True, missing PMRA/PMDE is allowed
NO_PM_KEY = 'NO_PM'
# fields a stellar astrometric entry must define before being saved
REQUIRED_FIELDS_STAR = ('APERO_NAME', 'RA', 'DEC',
                        'PMRA', 'PMDE', 'PLX', 'TEFF')
# subset whose absence may be excused by NO_PM=True
REQUIRED_FIELDS_PM = ('PMRA', 'PMDE')
# -----------------------------------------------------------------------------
# Mapping of legacy SQL column names -> extractor callables that pull the
# equivalent value out of a yaml entry dict. This lets old callers do e.g.
# ``get_entries('OBJNAME, ALIASES')`` or ``get_entries('TEFF', ...)`` and
# still get sensible results from the new yaml schema.
# -----------------------------------------------------------------------------
def _nested_value(entry: Dict[str, Any], key: str) -> Any:
    """Return ``entry[key]['value']`` if nested, else ``entry[key]``."""
    val = entry.get(key)
    if isinstance(val, dict):
        return val.get('value')
    return val


def _nested_source(entry: Dict[str, Any], key: str) -> Any:
    """Return ``entry[key]['source']`` if nested, else ``None``."""
    val = entry.get(key)
    if isinstance(val, dict):
        return val.get('source')
    return None


# legacy_col -> callable(entry_dict) -> value
LEGACY_COL_MAP: Dict[str, Any] = dict()
LEGACY_COL_MAP['OBJNAME'] = lambda e: e.get(APERO_NAME_KEY)
LEGACY_COL_MAP['ORIGINAL_NAME'] = lambda e: e.get('ORIGINAL_NAME')
LEGACY_COL_MAP['ALIASES'] = lambda e: e.get('ALIASES')
LEGACY_COL_MAP['RA_DEG'] = lambda e: _nested_value(e, 'RA')
LEGACY_COL_MAP['RA_SOURCE'] = lambda e: _nested_source(e, 'RA')
LEGACY_COL_MAP['DEC_DEG'] = lambda e: _nested_value(e, 'DEC')
LEGACY_COL_MAP['DEC_SOURCE'] = lambda e: _nested_source(e, 'DEC')
LEGACY_COL_MAP['EPOCH'] = lambda e: e.get('EPOCH')
LEGACY_COL_MAP['PMRA'] = lambda e: _nested_value(e, 'PMRA')
LEGACY_COL_MAP['PMRA_SOURCE'] = lambda e: _nested_source(e, 'PMRA')
LEGACY_COL_MAP['PMDE'] = lambda e: _nested_value(e, 'PMDE')
LEGACY_COL_MAP['PMDE_SOURCE'] = lambda e: _nested_source(e, 'PMDE')
LEGACY_COL_MAP['PLX'] = lambda e: _nested_value(e, 'PLX')
LEGACY_COL_MAP['PLX_SOURCE'] = lambda e: _nested_source(e, 'PLX')
LEGACY_COL_MAP['RV'] = lambda e: _nested_value(e, 'RV')
LEGACY_COL_MAP['RV_SOURCE'] = lambda e: _nested_source(e, 'RV')
LEGACY_COL_MAP['TEFF'] = lambda e: _nested_value(e, 'TEFF')
LEGACY_COL_MAP['TEFF_SOURCE'] = lambda e: _nested_source(e, 'TEFF')
LEGACY_COL_MAP['SP_TYPE'] = lambda e: _nested_value(e, 'SPT')
LEGACY_COL_MAP['SP_TYPE_SOURCE'] = lambda e: _nested_source(e, 'SPT')
# legacy callers use SP_SOURCE (no _TYPE_) for the spectral-type source
LEGACY_COL_MAP['SP_SOURCE'] = lambda e: _nested_source(e, 'SPT')
LEGACY_COL_MAP['NOTES'] = lambda e: e.get('NOTES')
LEGACY_COL_MAP['USED'] = lambda e: 1
# DATE_ADDED has no native yaml field; expose as None for parity
LEGACY_COL_MAP['DATE_ADDED'] = lambda e: None
# legacy KEYWORDS column has no yaml equivalent (NO_PM filter is dropped)
LEGACY_COL_MAP['KEYWORDS'] = lambda e: None


def legacy_view(entry: Optional[Dict[str, Any]]
                ) -> Optional[Dict[str, Any]]:
    """
    Flatten a yaml entry dict into a dict of ``{legacy_sql_column: value}``
    using :data:`LEGACY_COL_MAP`. Useful for callers that were written
    against the old SQL schema.

    :param entry: dict (yaml entry) or None
    :return: dict mapping every key in ``LEGACY_COL_MAP`` to its value, or
             None if ``entry`` is None.
    """
    # propagate None so callers can do ``if legacy is None: ...``
    if entry is None:
        return None
    # apply every extractor in the legacy column map
    out: Dict[str, Any] = dict()
    for col, getter in LEGACY_COL_MAP.items():
        out[col] = getter(entry)
    return out
# -----------------------------------------------------------------------------
# Module-level caches: shared by all AstrometricDatabase instances within a
# process, keyed by the absolute path of the astrometrics directory. On a
# fork-based multiprocessing pool these are inherited copy-on-write; on
# spawn-based pools each worker rebuilds them lazily.
# -----------------------------------------------------------------------------
# {astro_path -> {cleaned_name -> APERO_NAME}}
_NAME_INDEX: Dict[str, Dict[str, str]] = dict()
# {astro_path -> {APERO_NAME -> entry_dict}}
_ENTRY_CACHE: Dict[str, Dict[str, Dict[str, Any]]] = dict()
# {astro_path -> {filename -> mtime}} (used for invalidation)
_MTIME_CACHE: Dict[str, Dict[str, float]] = dict()
# {astro_path -> directory mtime when last scanned} (cheap freshness check)
_DIR_MTIME: Dict[str, float] = dict()
# {(astro_path, raw_input_name) -> (apero_name, found_flag)} resolution cache
_RESOLVE_CACHE: Dict[Tuple[str, str], Tuple[str, int]] = dict()


# =============================================================================
# Define worker functions
# =============================================================================
def clean_object(rawobjname: Union[str, None]) -> str:
    """
    Clean a raw object name to a canonical comparable form.

    Replicated from ``apero/instruments/default/instrument.py:clean_object``
    so this module has no apero-drs dependency. Behaviour is intentionally
    identical:
        - ``None`` / null-like  -> ``'Null'``
        - strip whitespace
        - replace ``+`` -> ``p`` and ``-`` -> ``m``
        - replace any character in :data:`BAD_OBJ_CHARS` with ``_``
        - upper-case
        - collapse repeated underscores and strip leading/trailing ``_``

    :param rawobjname: str or None, the raw object name to clean

    :return: str, the cleaned object name (or ``'Null'``)
    """
    # null / None handling - mirror drs_text.null_text behaviour
    if rawobjname is None:
        return 'Null'
    # cast to string defensively (yaml may give us ints, etc.)
    rawobjname = str(rawobjname)
    # null text comparison
    if drs_text.null_text(rawobjname, NULL_TEXT):
        return 'Null'
    # strip whitespace from outside
    objectname = rawobjname.strip()
    # replace sign characters
    objectname = objectname.replace('+', 'p')
    objectname = objectname.replace('-', 'm')
    # replace bad characters with underscores
    for bad_char in BAD_OBJ_CHARS:
        objectname = objectname.replace(bad_char, '_')
    # force upper case
    objectname = objectname.upper()
    # collapse multiple underscores
    while '__' in objectname:
        objectname = objectname.replace('__', '_')
    # strip leading / trailing underscores
    objectname = objectname.strip('_')
    # return cleaned name
    return objectname


def name_search_variants(rawobjname: Union[str, None]) -> List[str]:
    """Return ordered candidate variants of a name for fuzzy lookup.

    Used by :func:`find_by_name` (and the index builder) so that a
    raw user-typed name resolves to the same entry regardless of
    whitespace, sign characters or underscore conventions.

    Variants explore the cross-product of:
        - whitespace -> ``'_'`` or removed
        - ``+``      -> ``'P'`` or removed
        - ``-``      -> ``'M'`` or removed
        - underscores collapsed-or-removed (each variant emitted
          twice: once with single ``_`` separators, once with no
          ``_`` at all)

    All variants are upper-cased and have any other punctuation
    replaced by ``_`` (then collapsed). The canonical
    :func:`clean_object` result is always first in the list.

    :param rawobjname: str or None, the raw user-supplied name
    :return: list[str], deduplicated ordered list of variants
             (empty list if the name is null/empty)
    """
    if rawobjname is None:
        return []
    raw = str(rawobjname).strip()
    if not raw or drs_text.null_text(raw, NULL_TEXT):
        return []
    # replace any punctuation EXCEPT whitespace, +, -, _ with '_'
    keep = {' ', '\t', '+', '-', '_'}
    norm_chars = []
    for ch in raw:
        if ch in BAD_OBJ_CHARS and ch not in keep:
            norm_chars.append('_')
        else:
            norm_chars.append(ch)
    norm = ''.join(norm_chars)
    # build cross-product
    seen: List[str] = []
    canonical = clean_object(rawobjname)
    if canonical and canonical != 'Null':
        seen.append(canonical)
    for ws in ('_', ''):
        for plus in ('P', ''):
            for minus in ('M', ''):
                v = norm
                # whitespace -> ws
                v = v.replace(' ', ws).replace('\t', ws)
                v = v.replace('+', plus).replace('-', minus)
                v = v.upper()
                while '__' in v:
                    v = v.replace('__', '_')
                v = v.strip('_')
                if v and v not in seen:
                    seen.append(v)
                # also try the same variant with all '_' removed
                v_no = v.replace('_', '')
                if v_no and v_no not in seen:
                    seen.append(v_no)
    return seen


def _is_null(value: Any) -> bool:
    """
    Return True if ``value`` should be treated as missing/null.

    :param value: anything from a yaml file
    :return: bool
    """
    # explicit None
    if value is None:
        return True
    # delegate to drs_text for strings
    if isinstance(value, str):
        return drs_text.null_text(value, NULL_TEXT)
    # everything else (numbers, lists, dicts) is non-null
    return False


def _safe_filename(apero_name: str) -> str:
    """
    Convert an APERO_NAME into a safe yaml filename (no path separators).

    :param apero_name: str, the canonical APERO name
    :return: str, the filename (without directory) e.g. ``"GL699.yaml"``
    """
    # the cleaned APERO name is already filesystem-safe by construction
    safe = clean_object(apero_name)
    # protect against an empty / null name
    if safe in ('', 'Null'):
        emsg = ('Cannot build filename from null/empty APERO name '
                '({0!r})').format(apero_name)
        raise AperoCodedException(None, message=emsg)
    # append the extension
    return safe + YAML_EXT


# =============================================================================
# SIMBAD / Gaia / VizieR resolution helpers (used by resolve_target)
# -----------------------------------------------------------------------------
# Ported (and lightly re-styled) from
# ``apero-utils/general/apero_astrometrics2/resolve_against_simbad.py`` so
# that this module remains the single source of truth for astrometric
# catalogue resolution. All network calls go through plain urllib (no
# astroquery dependency); astropy is imported lazily inside the
# coordinate-propagation helper so the rest of the module remains usable
# even if astropy is not installed.
# =============================================================================
# TAP endpoints
# Default TAP endpoints (used when no per-call URL is supplied; the
# AstrometricDatabase class overrides these from params - see
# `SIMBAD_TAPURL`, `GAIA_URL`, `VIZIER_TAPURL` constants in
# apero/instruments/default/constants.py).
SIMBAD_TAP = 'https://simbad.cds.unistra.fr/simbad/sim-tap/sync'
GAIA_TAP = 'https://gea.esac.esa.int/tap-server/tap/sync'
VIZIER_TAP = 'https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync'


def _to_sync_url(url: Optional[str], default: str) -> str:
    '''
    Normalise a TAP base URL into its synchronous query endpoint.

    Accepts either ``.../tap`` (or ``.../sim-tap``) or already
    ``.../tap/sync``; ``None`` falls back to ``default``.

    :param url: str or None, the user-supplied TAP URL
    :param default: str, the fallback synchronous endpoint
    :return: str, a URL ending in ``/sync``
    '''
    # null / empty -> default
    if url is None or str(url).strip() in ('', 'None', 'NULL'):
        return default
    s = str(url).rstrip('/')
    # already a sync endpoint
    if s.endswith('/sync'):
        return s
    return s + '/sync'
# physical / geometric constants
OBLIQUITY_DEG = 23.4392911
EARTH_ORBITAL_SPEED_KMS = 29.79
TELLURIC_THRESHOLD_KMS = 5.0
# month length / name tables for telluric-window labels
NON_LEAP_MONTH_LENGTHS = [31, 28, 31, 30, 31, 30,
                          31, 31, 30, 31, 30, 31]
NON_LEAP_MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# ICRS -> galactic rotation matrix (J2000)
EQUATORIAL_TO_GALACTIC_MATRIX = [
    [-0.0548755604, -0.8734370902, -0.4838350155],
    [0.4941094279, -0.44482963, 0.7469822445],
    [-0.867666149, -0.1980763734, 0.4559837762],
]
# default user-agent for TAP HTTP requests
_TAP_USER_AGENT = 'apero-astrometrics/1.0'


# -----------------------------------------------------------------------------
# Small value-normalisation helpers
# -----------------------------------------------------------------------------
def _nv(value: Any) -> Any:
    """
    Return ``None`` for empty / null-like values, else the stripped string.

    :param value: any value (typically a TAP cell)
    :return: stripped string or ``None``
    """
    # explicit None short-circuit
    if value is None:
        return None
    # strip whitespace and detect null sentinels
    s = str(value).strip()
    if s == '' or s.lower() in {'none', 'null', 'nan'}:
        return None
    return s


def _pf(value: Any) -> Optional[float]:
    """
    Parse-float helper. Returns ``None`` for null / non-numeric values.

    :param value: any value
    :return: float or ``None``
    """
    # use _nv to normalise null-like inputs
    s = _nv(value)
    if s is None:
        return None
    # try-cast to float
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


# -----------------------------------------------------------------------------
# Low-level TAP helpers (synchronous, plain urllib)
# -----------------------------------------------------------------------------
def _tap_get(endpoint: str, adql: str, fmt: str = 'json',
             timeout: int = 30, request_key: str = 'request',
             lang_key: str = 'lang', format_key: str = 'format',
             query_key: str = 'query') -> Optional[bytes]:
    """
    Issue a synchronous TAP query and return the raw response bytes.

    :param endpoint: str, TAP endpoint URL
    :param adql: str, the ADQL query
    :param fmt: str, result format (``'json'`` or ``'csv'``)
    :param timeout: int, request timeout in seconds
    :param request_key: str, query-string key for the ``doQuery`` action
    :param lang_key: str, query-string key for the ADQL language tag
    :param format_key: str, query-string key for the response format
    :param query_key: str, query-string key for the ADQL itself

    :return: raw bytes from the TAP service, or ``None`` on failure
    """
    # lazy import of urllib pieces (stdlib, but keep grouped here)
    from urllib.parse import quote_plus
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    # assemble the GET parameter string
    params_str = (
        '{0}=doQuery&{1}=adql&{2}={3}&{4}={5}'
    ).format(request_key, lang_key, format_key, fmt,
             query_key, quote_plus(adql))
    url = '{0}?{1}'.format(endpoint, params_str)
    # build and dispatch the HTTP request
    req = Request(url, headers={'User-Agent': _TAP_USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (HTTPError, URLError, OSError):
        # network errors are non-fatal: return None and let caller decide
        return None


def _simbad_json(adql: str, timeout: int = 30,
                 url: Optional[str] = None) -> Optional[dict]:
    """
    Run an ADQL query against the SIMBAD TAP and return parsed JSON.

    :param adql: str, the ADQL query
    :param timeout: int, request timeout in seconds
    :param url: optional TAP base or sync URL; defaults to
                :data:`SIMBAD_TAP`.
    :return: parsed JSON dict, or ``None`` on failure
    """
    import json
    # resolve endpoint
    endpoint = _to_sync_url(url, SIMBAD_TAP)
    # fetch raw bytes
    raw = _tap_get(endpoint, adql, fmt='json', timeout=timeout)
    if raw is None:
        return None
    # parse JSON
    try:
        return json.loads(raw)
    except Exception:
        return None


def _vizier_json(adql: str, timeout: int = 30,
                 url: Optional[str] = None) -> Optional[dict]:
    """
    Run an ADQL query against the VizieR TAP and return parsed JSON.

    VizieR TAP requires uppercase parameter keys.

    :param adql: str, the ADQL query
    :param timeout: int, request timeout in seconds
    :param url: optional TAP base or sync URL; defaults to
                :data:`VIZIER_TAP`.
    :return: parsed JSON dict, or ``None`` on failure
    """
    import json
    # resolve endpoint
    endpoint = _to_sync_url(url, VIZIER_TAP)
    # fetch raw bytes (with uppercase param keys for VizieR)
    raw = _tap_get(endpoint, adql, fmt='json', timeout=timeout,
                   request_key='REQUEST', lang_key='LANG',
                   format_key='FORMAT', query_key='QUERY')
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def _gaia_csv(adql: str, timeout: int = 30,
              url: Optional[str] = None
              ) -> Optional[List[Dict[str, str]]]:
    """
    Run an ADQL query against the Gaia TAP (CSV) and return list of dicts.

    :param adql: str, the ADQL query
    :param timeout: int, request timeout in seconds
    :param url: optional TAP base or sync URL; defaults to
                :data:`GAIA_TAP`.
    :return: list of dict rows, or ``None`` on failure
    """
    import csv
    import io
    # resolve endpoint
    endpoint = _to_sync_url(url, GAIA_TAP)
    # fetch raw bytes
    raw = _tap_get(endpoint, adql, fmt='csv', timeout=timeout)
    if raw is None:
        return None
    # decode and parse as CSV
    try:
        text = raw.decode('utf-8', errors='replace')
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Geometry helpers
# -----------------------------------------------------------------------------
def _sep_arcsec(ra1: float, dec1: float,
                ra2: float, dec2: float) -> float:
    """
    Angular separation between two ICRS positions, in arcseconds.

    :param ra1: float, RA of point 1 (deg)
    :param dec1: float, Dec of point 1 (deg)
    :param ra2: float, RA of point 2 (deg)
    :param dec2: float, Dec of point 2 (deg)
    :return: float, separation in arcseconds
    """
    # convert all four inputs to radians
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    # spherical-law-of-cosines
    cos_sep = (math.sin(d1) * math.sin(d2)
               + math.cos(d1) * math.cos(d2) * math.cos(r1 - r2))
    cos_sep = max(-1.0, min(1.0, cos_sep))
    return math.degrees(math.acos(cos_sep)) * 3600.0


def _propagate(ra_deg: float, dec_deg: float,
               pmra: Optional[float], pmdec: Optional[float],
               dt_yr: float) -> Tuple[float, float]:
    """
    Apply a simple proper-motion-only displacement to ICRS coordinates.

    :param ra_deg: float, RA at the reference epoch (deg)
    :param dec_deg: float, Dec at the reference epoch (deg)
    :param pmra: float or None, RA proper motion (mas/yr, with cos(dec))
    :param pmdec: float or None, Dec proper motion (mas/yr)
    :param dt_yr: float, time interval in Julian years
    :return: tuple, (RA, Dec) in degrees at the new epoch
    """
    # if proper motions are missing, return inputs unchanged
    if pmra is None or pmdec is None:
        return ra_deg, dec_deg
    # cos(dec) factor for the RA displacement
    cos_dec = math.cos(math.radians(dec_deg))
    if abs(cos_dec) < 1e-8:
        return ra_deg, dec_deg
    # apply the displacement (mas -> deg)
    new_ra = (ra_deg + (pmra * dt_yr) / (3.6e6 * cos_dec)) % 360.0
    new_dec = max(-90.0, min(90.0, dec_deg + (pmdec * dt_yr) / 3.6e6))
    return new_ra, new_dec


def _jd_to_jyear(epoch_jd: Optional[float]) -> Optional[float]:
    """
    Convert a Julian Date to a Julian year (using astropy if available).

    :param epoch_jd: float or None, Julian Date
    :return: float or None, Julian year
    """
    if epoch_jd is None:
        return None
    try:
        # lazy import - astropy may not be installed in minimal envs
        from astropy.time import Time as _AT
        return float(_AT(epoch_jd, format='jd').jyear)
    except Exception:
        return None


def _propagate_to_epoch(ra_deg: Optional[float],
                        dec_deg: Optional[float],
                        pmra: Optional[float],
                        pmdec: Optional[float],
                        source_epoch_jyear: Optional[float],
                        target_epoch_jyear: float,
                        plx_mas: Optional[float] = None,
                        rv_kms: Optional[float] = None,
                        ) -> Tuple[Optional[float], Optional[float]]:
    """
    Propagate ICRS coordinates between epochs (astropy with safe fallback).

    :param ra_deg: float or None, source RA (deg)
    :param dec_deg: float or None, source Dec (deg)
    :param pmra: float or None, RA pm (mas/yr, with cos(dec))
    :param pmdec: float or None, Dec pm (mas/yr)
    :param source_epoch_jyear: float or None, source epoch (Julian year)
    :param target_epoch_jyear: float, target epoch (Julian year)
    :param plx_mas: float or None, parallax (mas)
    :param rv_kms: float or None, radial velocity (km/s)
    :return: (RA, Dec) at the target epoch, or inputs if propagation fails
    """
    # propagation only meaningful with both coordinates
    if ra_deg is None or dec_deg is None:
        return ra_deg, dec_deg
    # need PMs and a source epoch to propagate
    if pmra is None or pmdec is None or source_epoch_jyear is None:
        return ra_deg, dec_deg
    # try the full astropy space-motion path
    try:
        from astropy import units as _u
        from astropy.coordinates import SkyCoord as _SC
        from astropy.time import Time as _AT
        # build kwargs for SkyCoord
        kwargs: Dict[str, Any] = dict()
        kwargs['pm_ra_cosdec'] = pmra * _u.mas / _u.yr
        kwargs['pm_dec'] = pmdec * _u.mas / _u.yr
        kwargs['obstime'] = _AT(source_epoch_jyear, format='jyear')
        # add distance if parallax is sane
        if plx_mas is not None and plx_mas > 0:
            kwargs['distance'] = (1000.0 / plx_mas) * _u.pc
        # add radial velocity if available
        if rv_kms is not None:
            kwargs['radial_velocity'] = rv_kms * _u.km / _u.s
        # construct the SkyCoord
        coord = _SC(ra=ra_deg * _u.deg, dec=dec_deg * _u.deg,
                    frame='icrs', **kwargs)
        # propagate to the target epoch
        moved = coord.apply_space_motion(
            new_obstime=_AT(target_epoch_jyear, format='jyear'))
        return float(moved.ra.deg), float(moved.dec.deg)
    except Exception:
        # fallback to simple PM-only propagation
        dt_yr = target_epoch_jyear - source_epoch_jyear
        return _propagate(ra_deg, dec_deg, pmra, pmdec, dt_yr)


def _set_if_none(d: dict, key: str, value: Any) -> None:
    """Set ``d[key] = value`` only if the existing slot is ``None``."""
    if d.get(key) is None and value is not None:
        d[key] = value


def _format_ra_hms(ra_deg: Optional[float]) -> Optional[str]:
    """Format an RA in degrees as ``HH:MM:SS.SSS``."""
    if ra_deg is None:
        return None
    # convert to total seconds-of-time
    total_seconds = (ra_deg % 360.0) * 240.0
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds - 3600 * hours - 60 * minutes
    # carry handling near the second boundary
    if seconds >= 59.995:
        seconds = 0.0
        minutes += 1
    if minutes >= 60:
        minutes = 0
        hours = (hours + 1) % 24
    return '{0:02d}:{1:02d}:{2:06.3f}'.format(hours, minutes, seconds)


def _format_dec_dms(dec_deg: Optional[float]) -> Optional[str]:
    """Format a Dec in degrees as ``+DD:MM:SS.SS``."""
    if dec_deg is None:
        return None
    sign = '+' if dec_deg >= 0 else '-'
    total_arcsec = abs(dec_deg) * 3600.0
    degrees = int(total_arcsec // 3600)
    minutes = int((total_arcsec % 3600) // 60)
    seconds = total_arcsec - 3600 * degrees - 60 * minutes
    # carry handling
    if seconds >= 59.995:
        seconds = 0.0
        minutes += 1
    if minutes >= 60:
        minutes = 0
        degrees += 1
    return '{0}{1:02d}:{2:02d}:{3:05.2f}'.format(sign, degrees,
                                                 minutes, seconds)


def _galactic_from_radec(ra_deg: Optional[float],
                         dec_deg: Optional[float]
                         ) -> Tuple[Optional[float], Optional[float]]:
    """Convert ICRS (RA, Dec) to Galactic (l, b), both in degrees."""
    if ra_deg is None or dec_deg is None:
        return None, None
    ra_r = math.radians(ra_deg)
    dec_r = math.radians(dec_deg)
    # equatorial unit vector
    eq_vec = [math.cos(dec_r) * math.cos(ra_r),
              math.cos(dec_r) * math.sin(ra_r),
              math.sin(dec_r)]
    # rotate via the equatorial -> galactic matrix
    gal_vec = [sum(EQUATORIAL_TO_GALACTIC_MATRIX[i][j] * eq_vec[j]
                   for j in range(3)) for i in range(3)]
    gal_lon = math.degrees(math.atan2(gal_vec[1], gal_vec[0])) % 360.0
    gal_lat = math.degrees(
        math.asin(max(-1.0, min(1.0, gal_vec[2]))))
    return gal_lon, gal_lat


def _ecliptic_from_radec(ra_deg: Optional[float],
                         dec_deg: Optional[float]
                         ) -> Tuple[Optional[float], Optional[float]]:
    """Convert ICRS (RA, Dec) to ecliptic (lon, lat), both in degrees."""
    if ra_deg is None or dec_deg is None:
        return None, None
    ra_r = math.radians(ra_deg)
    dec_r = math.radians(dec_deg)
    eps_r = math.radians(OBLIQUITY_DEG)
    # rotation about the x-axis
    sin_beta = (math.sin(dec_r) * math.cos(eps_r)
                - math.cos(dec_r) * math.sin(eps_r) * math.sin(ra_r))
    beta_r = math.asin(max(-1.0, min(1.0, sin_beta)))
    y = (math.sin(ra_r) * math.cos(eps_r)
         + math.tan(dec_r) * math.sin(eps_r))
    x = math.cos(ra_r)
    lambda_r = math.atan2(y, x)
    return math.degrees(lambda_r) % 360.0, math.degrees(beta_r)


def _doy_label(day_index: int) -> str:
    """Return a ``'MMM DD'`` label for a 0-based day-of-year index."""
    day_number = day_index + 1
    remaining = day_number
    for month_name, month_length in zip(NON_LEAP_MONTH_NAMES,
                                        NON_LEAP_MONTH_LENGTHS):
        if remaining <= month_length:
            return '{0} {1:02d}'.format(month_name, remaining)
        remaining -= month_length
    return 'Dec 31'


def _telluric_windows(ra_deg: Optional[float], dec_deg: Optional[float],
                      rv_kms: Optional[float]) -> Optional[str]:
    """
    Return a human-readable summary of the days of the year in which the
    object's RV (after barycentric correction) is within
    :data:`TELLURIC_THRESHOLD_KMS` of zero.
    """
    ecl_lon_deg, ecl_lat_deg = _ecliptic_from_radec(ra_deg, dec_deg)
    if ecl_lon_deg is None or ecl_lat_deg is None or rv_kms is None:
        return None
    # build a per-day boolean array of "flagged" days
    flagged = []
    for day_index in range(365):
        sun_lon_deg = ((day_index + 1) - 80.0) * 360.0 / 365.0
        vbary = (EARTH_ORBITAL_SPEED_KMS
                 * math.cos(math.radians(ecl_lat_deg))
                 * math.sin(math.radians(sun_lon_deg - ecl_lon_deg)))
        flagged.append(abs(rv_kms + vbary) < TELLURIC_THRESHOLD_KMS)
    # collapse runs into (start, end) tuples
    ranges: List[Tuple[int, int]] = []
    start = None
    for day_index, is_flagged in enumerate(flagged):
        if is_flagged and start is None:
            start = day_index
        elif not is_flagged and start is not None:
            ranges.append((start, day_index - 1))
            start = None
    if start is not None:
        ranges.append((start, 364))
    # merge a wrap-around window across year boundary
    if len(ranges) > 1 and flagged[0] and flagged[-1]:
        first_start, first_end = ranges[0]
        last_start, _ = ranges[-1]
        ranges = [(last_start, first_end)] + ranges[1:-1]
    # nothing flagged
    if not ranges:
        return 'always > 5 km/s'
    # human-readable output
    parts = []
    for r0, r1 in ranges:
        if r0 == r1:
            parts.append(_doy_label(r0))
        else:
            parts.append('{0} to {1}'.format(_doy_label(r0),
                                             _doy_label(r1)))
    return '; '.join(parts)


def _absolute_mag(apparent_mag: Optional[float],
                  parallax_mas: Optional[float]) -> Optional[float]:
    """Return absolute magnitude from apparent mag + parallax (mas)."""
    if apparent_mag is None or parallax_mas is None or parallax_mas <= 0:
        return None
    distance_pc = 1000.0 / parallax_mas
    return apparent_mag - 5.0 * math.log10(distance_pc) + 5.0


def _teff_from_gaia_colors(gbp: Optional[float], grp: Optional[float],
                           jmag: Optional[float], hmag: Optional[float]
                           ) -> Tuple[Optional[float], Optional[float]]:
    """
    Mann+2015 Teff from Gaia BP-RP and 2MASS J-H (M-dwarf calibration).

    :return: ``(TEFF_GAIA_JH, TEFF_GAIA)`` (either may be ``None``)
    """
    # need both Gaia magnitudes
    if gbp is None or grp is None:
        return None, None
    col = gbp - grp
    # calibration validity window
    if col < 1.5 or col > 4.5:
        return None, None
    # variant including J-H if available
    teff_gaia_jh = None
    if jmag is not None and hmag is not None:
        jh = jmag - hmag
        a, b, c = 3.172, -2.475, 1.082
        d, e = -0.2231, 0.01738
        f, g = 0.08776, 0.04355
        teff_gaia_jh = round(3500.0 * (a + b * col + c * col**2
                                       + d * col**3 + e * col**4
                                       + f * jh + g * jh**2), 1)
    # BP-RP only variant
    a2, b2, c2 = 3.245, -2.4309, 1.043
    d2, e2 = -0.2127, 0.01649
    teff_gaia = round(3500.0 * (a2 + b2 * col + c2 * col**2
                                + d2 * col**3 + e2 * col**4), 1)
    return teff_gaia_jh, teff_gaia


def _derive_fields(yaml_data: Dict[str, Any]) -> None:
    """
    Populate derived fields on ``yaml_data`` in-place. Only fills entries
    whose current value is ``None``.

    Mirrors :func:`derive_fields` in
    ``apero-utils/general/apero_astrometrics2/resolve_against_simbad.py``.
    """
    # extract raw scalars
    ra = _pf(yaml_data.get('RA', dict()).get('value'))
    dec = _pf(yaml_data.get('DEC', dict()).get('value'))
    plx = _pf(yaml_data.get('PLX', dict()).get('value'))
    pmra = _pf(yaml_data.get('PMRA', dict()).get('value'))
    pmde = _pf(yaml_data.get('PMDE', dict()).get('value'))
    rv = _pf(yaml_data.get('RV', dict()).get('value'))
    # photometry
    gmag = _pf(yaml_data.get('G_MAG', dict()).get('value'))
    gbp = _pf(yaml_data.get('GBP_MAG', dict()).get('value'))
    grp = _pf(yaml_data.get('GRP_MAG', dict()).get('value'))
    jmag = _pf(yaml_data.get('J_MAG', dict()).get('value'))
    hmag = _pf(yaml_data.get('H_MAG', dict()).get('value'))
    kmag = _pf(yaml_data.get('KS_MAG', dict()).get('value'))
    w1 = _pf(yaml_data.get('W1_MAG', dict()).get('value'))
    w2 = _pf(yaml_data.get('W2_MAG', dict()).get('value'))
    # propagate stored RA/DEC back to J2000 if EPOCH is non-J2000 + Gaia
    epoch_jd = _pf(yaml_data.get('EPOCH'))
    epoch_jyear = _jd_to_jyear(epoch_jd)
    ra_coord = ra
    dec_coord = dec
    ra_source = _nv(yaml_data.get('RA', dict()).get('source'))
    is_gaia_epoch_coord = (ra_source is not None
                           and 'GAIA' in ra_source.upper())
    cond_propagate = (ra is not None and dec is not None
                      and pmra is not None and pmde is not None
                      and is_gaia_epoch_coord
                      and epoch_jyear is not None
                      and epoch_jd is not None
                      and abs(epoch_jd - 2451545.0) > 1.0)
    if cond_propagate:
        ra_coord, dec_coord = _propagate_to_epoch(
            ra_deg=ra, dec_deg=dec, pmra=pmra, pmdec=pmde,
            source_epoch_jyear=epoch_jyear,
            target_epoch_jyear=2000.0,
            plx_mas=plx, rv_kms=rv)
    # J2000 coordinate fields
    if yaml_data.get('RA_J2000_DEG') is None:
        yaml_data['RA_J2000_DEG'] = ra_coord
    if yaml_data.get('DEC_J2000_DEG') is None:
        yaml_data['DEC_J2000_DEG'] = dec_coord
    # sexagesimal forms
    if yaml_data.get('RA_HMS') is None:
        yaml_data['RA_HMS'] = _format_ra_hms(ra_coord)
    if yaml_data.get('DEC_DMS') is None:
        yaml_data['DEC_DMS'] = _format_dec_dms(dec_coord)
    # galactic coordinates
    gal_l, gal_b = _galactic_from_radec(ra_coord, dec_coord)
    if yaml_data.get('GALACTIC_LON') is None:
        yaml_data['GALACTIC_LON'] = gal_l
    if yaml_data.get('GALACTIC_LAT') is None:
        yaml_data['GALACTIC_LAT'] = gal_b
    # ecliptic coordinates
    ecl_l, ecl_b = _ecliptic_from_radec(ra_coord, dec_coord)
    if yaml_data.get('ECLIPTIC_LON') is None:
        yaml_data['ECLIPTIC_LON'] = ecl_l
    if yaml_data.get('ECLIPTIC_LAT') is None:
        yaml_data['ECLIPTIC_LAT'] = ecl_b
    # telluric RV-amplitude limits and windows
    if rv is not None and ecl_b is not None:
        vbary_amp = (EARTH_ORBITAL_SPEED_KMS
                     * math.cos(math.radians(ecl_b)))
        if yaml_data.get('TELLURIC_VSYS_PLUS_VBARY_MIN') is None:
            yaml_data['TELLURIC_VSYS_PLUS_VBARY_MIN'] = rv - vbary_amp
        if yaml_data.get('TELLURIC_VSYS_PLUS_VBARY_MAX') is None:
            yaml_data['TELLURIC_VSYS_PLUS_VBARY_MAX'] = rv + vbary_amp
        if yaml_data.get('TELLURIC_LIMIT_WINDOWS') is None:
            yaml_data['TELLURIC_LIMIT_WINDOWS'] = _telluric_windows(
                ra_coord, dec_coord, rv)
    # tangential / 3D space velocities
    if (plx is not None and plx > 0
            and pmra is not None and pmde is not None):
        mu_tot = math.sqrt(pmra**2 + pmde**2)
        d_pc = 1000.0 / plx
        v_sky = 4.74047 * d_pc * mu_tot / 1000.0
        if yaml_data.get('V_SKY') is None:
            yaml_data['V_SKY'] = v_sky
        if rv is not None and yaml_data.get('V3D') is None:
            yaml_data['V3D'] = math.sqrt(v_sky**2 + rv**2)
    # UVW Galactic velocities (Johnson & Soderblom convention)
    have_all = all(v is not None for v in
                   (ra_coord, dec_coord, plx, pmra, pmde, rv))
    if have_all and plx > 0:
        ra_r = math.radians(ra_coord)
        dec_r = math.radians(dec_coord)
        d_pc = 1000.0 / plx
        k = 4.74047
        cos_ra = math.cos(ra_r)
        sin_ra = math.sin(ra_r)
        cos_dec = math.cos(dec_r)
        sin_dec = math.sin(dec_r)
        a_matrix = [
            [-sin_ra, -cos_ra * sin_dec, cos_ra * cos_dec],
            [cos_ra, -sin_ra * sin_dec, sin_ra * cos_dec],
            [0.0, cos_dec, sin_dec],
        ]
        velocity_components = [
            k * d_pc * pmra / 1000.0,
            k * d_pc * pmde / 1000.0,
            rv,
        ]
        v_eq = [sum(a_matrix[i][j] * velocity_components[j]
                    for j in range(3)) for i in range(3)]
        u_v = sum(EQUATORIAL_TO_GALACTIC_MATRIX[0][j] * v_eq[j]
                  for j in range(3))
        v_v = sum(EQUATORIAL_TO_GALACTIC_MATRIX[1][j] * v_eq[j]
                  for j in range(3))
        w_v = sum(EQUATORIAL_TO_GALACTIC_MATRIX[2][j] * v_eq[j]
                  for j in range(3))
        if yaml_data.get('U') is None:
            yaml_data['U'] = u_v
        if yaml_data.get('V') is None:
            yaml_data['V'] = v_v
        if yaml_data.get('W') is None:
            yaml_data['W'] = w_v
    # absolute magnitudes
    if yaml_data.get('AMAG_G') is None:
        yaml_data['AMAG_G'] = _absolute_mag(gmag, plx)
    if yaml_data.get('AMAG_KS') is None:
        yaml_data['AMAG_KS'] = _absolute_mag(kmag, plx)
    # Gaia-color Teff relations
    teff_gaia_jh, teff_gaia = _teff_from_gaia_colors(gbp, grp, jmag, hmag)
    if yaml_data.get('TEFF_GAIA_JH') is None:
        yaml_data['TEFF_GAIA_JH'] = teff_gaia_jh
    if yaml_data.get('TEFF_GAIA') is None:
        yaml_data['TEFF_GAIA'] = teff_gaia
    # photometric [Fe/H] (Duque-Arribas) for M-dwarf candidates
    m_ks = _absolute_mag(kmag, plx)
    m_g = _absolute_mag(gmag, plx)
    spt = _nv(yaml_data.get('SPT', dict()).get('value'))
    is_m_candidate = ((m_g is not None and 7.5 <= m_g <= 16.5)
                      or (spt is not None and spt.upper().startswith('M')))
    if (is_m_candidate and all(v is not None
                               for v in (m_ks, gbp, grp, w1, w2))):
        x = w1 - w2
        denom = 0.618 + 0.960 * x
        if abs(denom) > 1e-9:
            feh_num = ((gbp - grp) - 0.596 - 2.336 * x
                       - 0.498 * (x ** 2) - 0.254 * m_ks)
            yaml_data['FE_H'] = feh_num / denom
    # Gaia-derived Fe/H fallback
    if yaml_data.get('FE_H') is None:
        feh_gaia = _pf(yaml_data.get('GAIA_MH_GSPPHOT'))
        if feh_gaia is not None:
            yaml_data['FE_H'] = feh_gaia
    # Mann+2015 + Delfosse+2000 radius/mass for M-dwarf candidates
    if m_ks is not None and is_m_candidate:
        if yaml_data.get('R_STAR_MKS') is None:
            r_star = (1.9515 - 0.3520 * m_ks
                      + 0.01680 * (m_ks ** 2))
            if r_star > 0:
                yaml_data['R_STAR_MKS'] = r_star
        if (yaml_data.get('R_STAR_MKS_FEH') is None
                and yaml_data.get('FE_H') is not None):
            feh = _pf(yaml_data.get('FE_H'))
            if feh is not None:
                r_star_feh = (1.9305 - 0.3466 * m_ks
                              + 0.01647 * (m_ks ** 2)
                              + 0.04458 * feh)
                if r_star_feh > 0:
                    yaml_data['R_STAR_MKS_FEH'] = r_star_feh
        if yaml_data.get('MASS_STAR_MANN15') is None:
            m_star = (0.5858 + 0.3872 * m_ks
                      - 0.1217 * (m_ks ** 2)
                      + 0.0106 * (m_ks ** 3)
                      - 2.7262e-4 * (m_ks ** 4))
            if m_star > 0:
                yaml_data['MASS_STAR_MANN15'] = m_star
        if (yaml_data.get('MASS_STAR_DELFOSSE00') is None
                and 4.5 <= m_ks <= 9.5):
            log_m_del = 1e-3 * (1.8 + 6.12 * m_ks
                                + 13.205 * m_ks**2
                                - 6.2315 * m_ks**3
                                + 0.37529 * m_ks**4)
            yaml_data['MASS_STAR_DELFOSSE00'] = 10.0 ** log_m_del
    # for non-M candidates fall back to Gaia FLAME outputs
    if not is_m_candidate:
        feh_gaia = _pf(yaml_data.get('GAIA_MH_GSPPHOT'))
        yaml_data['FE_H'] = feh_gaia
        for key in ('R_STAR_MKS', 'R_STAR_MKS_FEH',
                    'MASS_STAR_MANN15', 'MASS_STAR_DELFOSSE00'):
            if yaml_data.get(key) is not None:
                yaml_data[key] = None
    # logg derivation
    mass_for_logg = _pf(yaml_data.get('MASS_STAR_MANN15'))
    radius_for_logg = _pf(yaml_data.get('R_STAR_MKS'))
    if not is_m_candidate:
        if mass_for_logg is None:
            mass_for_logg = _pf(yaml_data.get('GAIA_MASS_FLAME'))
        if radius_for_logg is None:
            radius_for_logg = _pf(yaml_data.get('GAIA_RADIUS_FLAME'))
    else:
        if radius_for_logg is None:
            radius_for_logg = _pf(yaml_data.get('R_STAR_MKS_FEH'))
    cond_logg = (yaml_data.get('LOG_G') is None
                 and mass_for_logg is not None
                 and radius_for_logg is not None
                 and mass_for_logg > 0 and radius_for_logg > 0)
    if cond_logg:
        yaml_data['LOG_G'] = (4.438 + math.log10(mass_for_logg)
                              - 2.0 * math.log10(radius_for_logg))
    # luminosity derivation
    teff_for_l = _pf(yaml_data.get('TEFF_GAIA_JH'))
    if teff_for_l is None:
        teff_for_l = _pf(yaml_data.get('TEFF_GAIA'))
    if teff_for_l is None:
        teff_for_l = _pf(yaml_data.get('TEFF', dict()).get('value'))
    if is_m_candidate:
        radius_for_l = _pf(yaml_data.get('R_STAR_MKS'))
        if radius_for_l is None:
            radius_for_l = radius_for_logg
        if (radius_for_l is not None and teff_for_l is not None
                and teff_for_l > 0):
            yaml_data['L_STAR'] = ((radius_for_l ** 2)
                                   * (teff_for_l / 5778.0) ** 4)
    else:
        lum_gaia = _pf(yaml_data.get('GAIA_LUM_FLAME'))
        if lum_gaia is not None:
            yaml_data['L_STAR'] = lum_gaia
    # FLAME re-derivation for non-M targets
    if not is_m_candidate:
        mass_gaia = _pf(yaml_data.get('GAIA_MASS_FLAME'))
        radius_gaia = _pf(yaml_data.get('GAIA_RADIUS_FLAME'))
        lum_gaia = _pf(yaml_data.get('GAIA_LUM_FLAME'))
        if (mass_gaia is not None and radius_gaia is not None
                and mass_gaia > 0 and radius_gaia > 0):
            yaml_data['LOG_G'] = (4.438 + math.log10(mass_gaia)
                                  - 2.0 * math.log10(radius_gaia))
        if lum_gaia is not None:
            yaml_data['L_STAR'] = lum_gaia


# -----------------------------------------------------------------------------
# Schema scaffolding
# -----------------------------------------------------------------------------
def _full_resolve_schema(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure every expected top-level key exists on ``d`` (None if absent).
    Mirrors ``_full_schema`` in resolve_against_simbad.py.
    """
    # top-level scalars
    for top in ('APERO_NAME', 'ORIGINAL_NAME', 'SIMBAD_NAME',
                'APERO_CLASS', 'EPOCH'):
        d.setdefault(top, None)
    # value+source+units blocks
    blocks_with_units = [
        ('RA', 'deg'), ('DEC', 'deg'),
        ('PMRA', 'mas/yr'), ('PMDE', 'mas/yr'),
        ('PLX', 'mas'), ('RV', 'km/s'),
        ('TEFF', 'K'),
    ]
    for block, units in blocks_with_units:
        sub = d.setdefault(block, dict())
        sub.setdefault('value', None)
        sub.setdefault('source', None)
        sub.setdefault('units', units)
    # value+source blocks
    for block in ('SPT',):
        sub = d.setdefault(block, dict())
        sub.setdefault('value', None)
        sub.setdefault('source', None)
    # vsini block (extra err key)
    vsini = d.setdefault('VSINI', dict())
    for k in ('value', 'err', 'source'):
        vsini.setdefault(k, None)
    vsini.setdefault('units', 'km/s')
    # photometry blocks
    for block in ('G_MAG', 'GBP_MAG', 'GRP_MAG',
                  'J_MAG', 'H_MAG', 'KS_MAG',
                  'W1_MAG', 'W2_MAG', 'W3_MAG', 'W4_MAG'):
        sub = d.setdefault(block, dict())
        sub.setdefault('value', None)
        sub.setdefault('source', None)
    # plain top-level lists/strings
    for k in ('KEYWORDS', 'ALIASES'):
        d.setdefault(k, None)
    d.setdefault('NOTES', None)
    # Gaia-derived extras
    for k in ('GAIA_SOURCE_ID',
              'GAIA_TEFF_GSPPHOT', 'GAIA_LOGG_GSPPHOT',
              'GAIA_MH_GSPPHOT',
              'GAIA_RADIUS_FLAME', 'GAIA_LUM_FLAME', 'GAIA_MASS_FLAME'):
        d.setdefault(k, None)
    # derived fields filled by _derive_fields
    derived_keys = (
        'RA_HMS', 'DEC_DMS', 'RA_J2000_DEG', 'DEC_J2000_DEG',
        'GALACTIC_LON', 'GALACTIC_LAT',
        'ECLIPTIC_LON', 'ECLIPTIC_LAT',
        'TELLURIC_VSYS_PLUS_VBARY_MIN',
        'TELLURIC_VSYS_PLUS_VBARY_MAX', 'TELLURIC_LIMIT_WINDOWS',
        'V_SKY', 'V3D', 'U', 'V', 'W',
        'AMAG_G', 'AMAG_KS',
        'TEFF_GAIA_JH', 'TEFF_GAIA',
        'FE_H', 'R_STAR_MKS', 'R_STAR_MKS_FEH', 'MASS_STAR_MANN15',
        'MASS_STAR_DELFOSSE00', 'LOG_G', 'L_STAR',
    )
    for k in derived_keys:
        d.setdefault(k, None)
    return d


# -----------------------------------------------------------------------------
# Merge helpers
# -----------------------------------------------------------------------------
def _merge_scalar(yaml_data: dict, yaml_block: str,
                  simbad: dict, simbad_key: str, source: str) -> None:
    """Merge a value+source scalar from simbad into yaml_data[yaml_block]."""
    block = yaml_data[yaml_block]
    if block.get('value') is None:
        val = _pf(simbad.get(simbad_key))
        if val is not None:
            block['value'] = val
            block['source'] = source


def _merge_mag(yaml_data: dict, yaml_block: str,
               simbad: dict, simbad_key: str, source: str) -> None:
    """Merge a value+source magnitude from simbad into yaml_data[block]."""
    block = yaml_data.get(yaml_block)
    if not isinstance(block, dict):
        yaml_data[yaml_block] = dict(value=None, source=None)
        block = yaml_data[yaml_block]
    if block.get('value') is None:
        val = _pf(simbad.get(simbad_key))
        if val is not None:
            block['value'] = val
            block['source'] = source


def _update_yaml_from_simbad(yaml_data: Dict[str, Any],
                             simbad: Dict[str, Any]
                             ) -> Dict[str, Any]:
    """
    Merge a :func:`_resolve_from_name` result into ``yaml_data``, filling
    only ``None`` values, then call :func:`_derive_fields`.

    :param yaml_data: dict, the destination yaml entry (modified in-place)
    :param simbad: dict, the result from :func:`_resolve_from_name`
    :return: ``yaml_data`` (same instance)
    """
    # ensure full schema
    _full_resolve_schema(yaml_data)
    # SIMBAD canonical name
    if yaml_data.get('SIMBAD_NAME') is None:
        yaml_data['SIMBAD_NAME'] = simbad.get('simbad_main_id')
    # ALIASES: every SIMBAD identifier minus the names already
    # captured as APERO_NAME / ORIGINAL_NAME / SIMBAD_NAME so the
    # alias list is informative rather than redundant.
    if yaml_data.get('ALIASES') in (None, '', [], ()):
        raw_aliases = simbad.get('aliases') or []
        if isinstance(raw_aliases, (list, tuple)):
            already = set()
            for k in ('APERO_NAME', 'ORIGINAL_NAME', 'SIMBAD_NAME'):
                v = yaml_data.get(k)
                if isinstance(v, str) and v.strip():
                    already.add(v.strip().casefold())
            cleaned: List[str] = []
            seen: set = set()
            for alias in raw_aliases:
                if not isinstance(alias, str):
                    continue
                aval = alias.strip()
                if not aval:
                    continue
                akey = aval.casefold()
                if akey in already or akey in seen:
                    continue
                seen.add(akey)
                cleaned.append(aval)
            if cleaned:
                yaml_data['ALIASES'] = cleaned
    # astrometry scalars
    _merge_scalar(yaml_data, 'RA', simbad, 'ra_deg', 'SIMBAD')
    _merge_scalar(yaml_data, 'DEC', simbad, 'dec_deg', 'SIMBAD')
    _merge_scalar(yaml_data, 'PLX', simbad, 'parallax_mas', 'SIMBAD')
    _merge_scalar(yaml_data, 'PMRA', simbad, 'pmra_masyr', 'SIMBAD')
    _merge_scalar(yaml_data, 'PMDE', simbad, 'pmdec_masyr', 'SIMBAD')
    _merge_scalar(yaml_data, 'RV', simbad, 'rv_kms', 'SIMBAD')
    # Teff: prefer Gaia GSP-Phot, else SIMBAD median teff measurements
    if yaml_data['TEFF']['value'] is None:
        gaia_teff = _pf(simbad.get('gaia_teff_gspphot'))
        simbad_teff = _pf(simbad.get('teff_simbad'))
        if gaia_teff is not None:
            yaml_data['TEFF']['value'] = gaia_teff
            yaml_data['TEFF']['source'] = 'Gaia DR3 GSP-Phot'
        elif simbad_teff is not None:
            yaml_data['TEFF']['value'] = simbad_teff
            yaml_data['TEFF']['source'] = 'SIMBAD mes_teff'
    # spectral type
    if (yaml_data['SPT']['value'] is None
            and _nv(simbad.get('sp_type')) is not None):
        yaml_data['SPT']['value'] = simbad['sp_type']
        yaml_data['SPT']['source'] = 'SIMBAD'
    # photometry
    _merge_mag(yaml_data, 'G_MAG', simbad, 'G_mag', 'SIMBAD/Gaia')
    _merge_mag(yaml_data, 'J_MAG', simbad, 'J_mag', 'SIMBAD/2MASS')
    _merge_mag(yaml_data, 'H_MAG', simbad, 'H_mag', 'SIMBAD/2MASS')
    _merge_mag(yaml_data, 'KS_MAG', simbad, 'K_mag', 'SIMBAD/2MASS')
    _merge_mag(yaml_data, 'GBP_MAG', simbad, 'GBP_mag', 'Gaia VizieR')
    _merge_mag(yaml_data, 'GRP_MAG', simbad, 'GRP_mag', 'Gaia VizieR')
    _merge_mag(yaml_data, 'W1_MAG', simbad, 'W1_mag', 'AllWISE')
    _merge_mag(yaml_data, 'W2_MAG', simbad, 'W2_mag', 'AllWISE')
    _merge_mag(yaml_data, 'W3_MAG', simbad, 'W3_mag', 'AllWISE')
    _merge_mag(yaml_data, 'W4_MAG', simbad, 'W4_mag', 'AllWISE')
    # Gaia extra scalar fields
    extra_keys = [
        ('GAIA_TEFF_GSPPHOT', 'gaia_teff_gspphot'),
        ('GAIA_LOGG_GSPPHOT', 'gaia_logg_gspphot'),
        ('GAIA_MH_GSPPHOT', 'gaia_mh_gspphot'),
        ('GAIA_RADIUS_FLAME', 'gaia_radius_flame'),
        ('GAIA_LUM_FLAME', 'gaia_lum_flame'),
        ('GAIA_MASS_FLAME', 'gaia_mass_flame'),
    ]
    for yaml_key, src_key in extra_keys:
        if (yaml_data.get(yaml_key) is None
                and _nv(simbad.get(src_key)) is not None):
            v = _pf(simbad[src_key])
            yaml_data[yaml_key] = v if v is not None else simbad[src_key]
    # Gaia source id - keep as string to avoid scientific notation
    if (yaml_data.get('GAIA_SOURCE_ID') is None
            and _nv(simbad.get('gaia_source_id')) is not None):
        yaml_data['GAIA_SOURCE_ID'] = str(simbad.get('gaia_source_id'))
    # finally compute all derived fields
    _derive_fields(yaml_data)
    return yaml_data


# -----------------------------------------------------------------------------
# WISE designation helpers
# -----------------------------------------------------------------------------
def _escape_simbad(name: str) -> str:
    """Escape a string for use inside a single-quoted ADQL literal."""
    return name.replace("'", "''")


def _extract_wisea_designation(identifier: Any) -> Optional[str]:
    """Return the bare AllWISE designation or None for non-WISEA inputs."""
    sval = _nv(identifier)
    if sval is None:
        return None
    if sval.startswith('WISEA '):
        return sval.replace('WISEA ', '', 1).strip()
    return None


def _fetch_wise_by_designation(designation: str,
                               vizier_url: Optional[str] = None
                               ) -> Optional[Tuple[Any, ...]]:
    """Fetch one AllWISE row by its designation via VizieR."""
    safe = designation.replace("'", "''")
    # build query - intentionally uses double quotes inside the string
    adql = (
        'SELECT TOP 1 "AllWISE", W1mag, e_W1mag, W2mag, e_W2mag, '
        'W3mag, e_W3mag, W4mag, e_W4mag, RAJ2000, DEJ2000 '
        'FROM "II/328/allwise" '
        'WHERE "AllWISE" = \'{0}\''
    ).format(safe)
    payload = _vizier_json(adql, url=vizier_url)
    if payload is None:
        return None
    rows = payload.get('data', [])
    if not rows:
        return None
    row = rows[0]
    if len(row) < 11:
        return None
    return tuple(row)


# regex matching Gaia DR2/EDR3/DR3 source-id names
_GAIA_NAME_RE = re.compile(
    r'^\s*Gaia\s+(DR2|EDR3|DR3)\s+(\d+)\s*$', re.IGNORECASE)


def _parse_gaia_name(name: str
                     ) -> Optional[Tuple[str, str]]:
    """Return ``(release, source_id)`` if ``name`` parses as a Gaia
    designation, else ``None``."""
    if not name:
        return None
    m = _GAIA_NAME_RE.match(name)
    if not m:
        return None
    rel = m.group(1).lower()
    return rel, m.group(2)


def _resolve_from_gaia_name(name: str,
                            vizier_url: Optional[str] = None
                            ) -> Optional[Dict[str, Any]]:
    """SIMBAD-fail fallback: resolve a ``Gaia DRx <id>`` name directly
    via VizieR.

    Returns a dict with the same shape as :func:`_resolve_from_name`
    (subset of keys; many will be ``None``). Used when SIMBAD knows
    nothing about ``name`` but the user supplied a Gaia source id.

    :param name: str, candidate name (e.g. ``"Gaia DR3 1234567890"``)
    :param vizier_url: optional override for the VizieR TAP endpoint
    :return: normalised result dict, or ``None`` if not a Gaia name or
             not found.
    """
    parsed = _parse_gaia_name(name)
    if parsed is None:
        return None
    release, source_id = parsed
    table_map = {'dr3': '"I/355/gaiadr3"',
                 'edr3': '"I/350/gaiaedr3"',
                 'dr2': '"I/345/gaia2"'}
    table = table_map.get(release, '"I/355/gaiadr3"')
    if release == 'dr2':
        adql = (
            'SELECT TOP 1 RA_ICRS, DE_ICRS, Plx, pmRA, pmDE, RV, '
            'BPmag, RPmag, e_BPmag, e_RPmag '
            'FROM {0} WHERE Source = {1}'
        ).format(table, source_id)
    else:
        adql = (
            'SELECT TOP 1 RA_ICRS, DE_ICRS, Plx, pmRA, pmDE, RVDR2, '
            'BPmag, RPmag, e_BPmag, e_RPmag '
            'FROM {0} WHERE Source = {1}'
        ).format(table, source_id)
    payload = _vizier_json(adql, url=vizier_url)
    if payload is None:
        return None
    rows = payload.get('data', [])
    if not rows:
        return None
    row = rows[0]
    if len(row) < 5:
        return None
    # build a minimal result dict matching _resolve_from_name's schema
    result: Dict[str, Any] = {
        'simbad_main_id': 'Gaia {0} {1}'.format(release.upper(),
                                                source_id),
        'ra_deg': _nv(row[0]),
        'dec_deg': _nv(row[1]),
        'parallax_mas': _nv(row[2]) if len(row) > 2 else None,
        'pmra_masyr': _nv(row[3]) if len(row) > 3 else None,
        'pmdec_masyr': _nv(row[4]) if len(row) > 4 else None,
        'rv_kms': _nv(row[5]) if len(row) > 5 else None,
        'sp_type': None,
        'otype_txt': None,
        'G_mag': None, 'J_mag': None, 'H_mag': None, 'K_mag': None,
        'GBP_mag': _nv(row[6]) if len(row) > 6 else None,
        'GRP_mag': _nv(row[7]) if len(row) > 7 else None,
        'GBP_err': _nv(row[8]) if len(row) > 8 else None,
        'GRP_err': _nv(row[9]) if len(row) > 9 else None,
        'W1_mag': None, 'W1_err': None,
        'W2_mag': None, 'W2_err': None,
        'W3_mag': None, 'W3_err': None,
        'W4_mag': None, 'W4_err': None,
        'gaia_source_id': source_id,
        'gaia_teff_gspphot': None, 'gaia_logg_gspphot': None,
        'gaia_mh_gspphot': None,
        'gaia_radius_flame': None, 'gaia_lum_flame': None,
        'gaia_mass_flame': None,
        'teff_simbad': None,
        'aliases': [],
    }
    return result


# -----------------------------------------------------------------------------
# Top-level resolver
# -----------------------------------------------------------------------------
def _resolve_from_name(name: str,
                       simbad_url: Optional[str] = None,
                       gaia_url: Optional[str] = None,
                       vizier_url: Optional[str] = None
                       ) -> Optional[Dict[str, Any]]:
    """
    Query SIMBAD/Gaia/VizieR for ``name`` and return a normalised dict.

    All keys may be ``None``. Caller must merge the result into a yaml
    entry via :func:`_update_yaml_from_simbad`.

    :param name: str, the target name to resolve
    :param simbad_url: optional override for the SIMBAD TAP endpoint;
                       defaults to module-level :data:`SIMBAD_TAP`.
    :param gaia_url: optional override for the Gaia TAP endpoint.
    :param vizier_url: optional override for the VizieR TAP endpoint.
    :return: dict of normalised SIMBAD/Gaia/VizieR results, or ``None``
             if SIMBAD did not return anything for ``name``.
    """
    # escape the name for ADQL string literals
    safe = _escape_simbad(name)
    # ----- 1. core SIMBAD query -----
    adql = (
        'SELECT TOP 1 b.main_id, b.ra, b.dec, b.plx_value, b.pmra, '
        'b.pmdec, b.rvz_radvel, b.sp_type, b.otype_txt, '
        'f.G, f.J, f.H, f.K '
        'FROM ident i JOIN basic b ON i.oidref = b.oid '
        'LEFT JOIN allfluxes f ON b.oid = f.oidref '
        'WHERE i.id = \'{0}\''
    ).format(safe)
    payload = _simbad_json(adql, url=simbad_url)
    if payload is None:
        # SIMBAD unreachable: try Gaia by-name as a last resort
        return _resolve_from_gaia_name(name, vizier_url=vizier_url)
    rows = payload.get('data', [])
    if not rows:
        # SIMBAD returned no match: try Gaia by-name as a last resort
        return _resolve_from_gaia_name(name, vizier_url=vizier_url)
    row = rows[0]
    keys = ['simbad_main_id', 'ra_deg', 'dec_deg', 'parallax_mas',
            'pmra_masyr', 'pmdec_masyr', 'rv_kms',
            'sp_type', 'otype_txt',
            'G_mag', 'J_mag', 'H_mag', 'K_mag']
    result: Dict[str, Any] = {k: _nv(v) for k, v in zip(keys, row)}
    # null-fill all optional keys
    optional_keys = ('GBP_mag', 'GBP_err', 'GRP_mag', 'GRP_err',
                     'W1_mag', 'W1_err', 'W2_mag', 'W2_err',
                     'W3_mag', 'W3_err', 'W4_mag', 'W4_err',
                     'gaia_source_id',
                     'gaia_teff_gspphot', 'gaia_logg_gspphot',
                     'gaia_mh_gspphot',
                     'gaia_radius_flame', 'gaia_lum_flame',
                     'gaia_mass_flame', 'teff_simbad')
    for k in optional_keys:
        result.setdefault(k, None)
    # ----- 2. SIMBAD Teff median from mesFe_h -----
    adql_teff = (
        'SELECT TOP 10 m.teff FROM mesFe_h m '
        'JOIN ident i ON m.oidref = i.oidref '
        'WHERE i.id = \'{0}\' AND m.teff IS NOT NULL'
    ).format(safe)
    teff_p = _simbad_json(adql_teff, url=simbad_url)
    if teff_p:
        teffs = [_pf(r[0]) for r in teff_p.get('data', [])
                 if _pf(r[0]) is not None]
        if teffs:
            result['teff_simbad'] = sorted(teffs)[len(teffs) // 2]
    # ----- 2b. SIMBAD identifier list (used for ALIASES) -----
    # Pull every identifier SIMBAD knows for this object so the caller
    # can populate the ALIASES field on a freshly-resolved entry.
    adql_all_idents = (
        'SELECT i2.id FROM ident i '
        'JOIN ident i2 ON i.oidref = i2.oidref '
        'WHERE i.id = \'{0}\''
    ).format(safe)
    all_idents_p = _simbad_json(adql_all_idents, url=simbad_url)
    aliases_list: List[str] = []
    if all_idents_p:
        seen_aliases = set()
        for irow in all_idents_p.get('data', []):
            if not irow:
                continue
            aval = _nv(irow[0])
            if aval is None:
                continue
            akey = aval.strip().casefold()
            if not akey or akey in seen_aliases:
                continue
            seen_aliases.add(akey)
            aliases_list.append(aval.strip())
    result['aliases'] = aliases_list
    # ----- 3. Gaia identifier via SIMBAD cross-match -----
    adql_idents = (
        'SELECT i2.id FROM ident i '
        'JOIN ident i2 ON i.oidref = i2.oidref '
        'WHERE i.id = \'{0}\' AND ('
        "i2.id LIKE 'Gaia DR3 %' OR i2.id LIKE 'Gaia EDR3 %' "
        "OR i2.id LIKE 'Gaia DR2 %' OR i2.id LIKE 'WISEA %')"
    ).format(safe)
    idents_p = _simbad_json(adql_idents, url=simbad_url)
    gaia_release: Optional[str] = None
    gaia_source_id: Optional[str] = None
    wise_designation: Optional[str] = None
    if idents_p:
        prefixes = (('Gaia DR3 ', 'dr3'),
                    ('Gaia EDR3 ', 'edr3'),
                    ('Gaia DR2 ', 'dr2'))
        for irow in idents_p.get('data', []):
            ident_val = _nv(irow[0]) if irow else None
            if ident_val is None:
                continue
            for prefix, rel in prefixes:
                if ident_val.startswith(prefix):
                    candidate = ident_val[len(prefix):].strip()
                    if candidate.isdigit():
                        gaia_source_id = candidate
                        gaia_release = rel
                        break
            if wise_designation is None:
                wise_designation = _extract_wisea_designation(ident_val)
            if (gaia_source_id is not None
                    and wise_designation is not None):
                break
    result['gaia_source_id'] = gaia_source_id
    # ----- 4. Gaia BP/RP + PMs from VizieR -----
    ra_deg = _pf(result['ra_deg'])
    dec_deg = _pf(result['dec_deg'])
    simbad_ra_deg = ra_deg
    simbad_dec_deg = dec_deg
    simbad_pmra = _pf(result.get('pmra_masyr'))
    simbad_pmdec = _pf(result.get('pmdec_masyr'))
    simbad_plx = _pf(result.get('parallax_mas'))
    simbad_rv = _pf(result.get('rv_kms'))
    gaia_ref_epoch: Optional[float] = None
    if gaia_source_id is not None:
        if gaia_release == 'dr2':
            adql_gaia = (
                'SELECT TOP 1 phot_bp_mean_mag, phot_rp_mean_mag, '
                'phot_bp_mean_mag_error, phot_rp_mean_mag_error, '
                'ra, dec, pmra, pmdec '
                'FROM "I/345/gaia2" WHERE source_id = {0}'
            ).format(gaia_source_id)
        else:
            table_map = dict()
            table_map['dr3'] = '"I/355/gaiadr3"'
            table_map['edr3'] = '"I/350/gaiaedr3"'
            table = table_map.get(gaia_release or 'dr3',
                                  '"I/355/gaiadr3"')
            adql_gaia = (
                'SELECT TOP 1 BPmag, RPmag, e_BPmag, e_RPmag, '
                'RA_ICRS, DE_ICRS, pmRA, pmDE '
                'FROM {0} WHERE Source = {1}'
            ).format(table, gaia_source_id)
        gaia_p = _vizier_json(adql_gaia, url=vizier_url)
        if gaia_p:
            gdata = gaia_p.get('data', [])
            if gdata:
                gv = gdata[0]
                _set_if_none(result, 'GBP_mag',
                             _nv(gv[0]) if len(gv) > 0 else None)
                _set_if_none(result, 'GRP_mag',
                             _nv(gv[1]) if len(gv) > 1 else None)
                _set_if_none(result, 'GBP_err',
                             _nv(gv[2]) if len(gv) > 2 else None)
                _set_if_none(result, 'GRP_err',
                             _nv(gv[3]) if len(gv) > 3 else None)
                # prefer Gaia astrometry as the WISE-propagation anchor
                ra_gaia = _pf(gv[4]) if len(gv) > 4 else None
                dec_gaia = _pf(gv[5]) if len(gv) > 5 else None
                if ra_gaia is not None:
                    ra_deg = ra_gaia
                if dec_gaia is not None:
                    dec_deg = dec_gaia
                if gaia_release in {'dr3', 'edr3'}:
                    gaia_ref_epoch = 2016.0
                elif gaia_release == 'dr2':
                    gaia_ref_epoch = 2015.5
                _set_if_none(result, 'pmra_masyr',
                             _nv(gv[6]) if len(gv) > 6 else None)
                _set_if_none(result, 'pmdec_masyr',
                             _nv(gv[7]) if len(gv) > 7 else None)
    # positional fallback for BP/RP if source-id lookup missed
    gaia_query_ra = ra_deg
    gaia_query_dec = dec_deg
    if (gaia_ref_epoch is None and simbad_ra_deg is not None
            and simbad_dec_deg is not None):
        gaia_query_ra, gaia_query_dec = _propagate_to_epoch(
            ra_deg=simbad_ra_deg, dec_deg=simbad_dec_deg,
            pmra=simbad_pmra, pmdec=simbad_pmdec,
            source_epoch_jyear=2000.0,
            target_epoch_jyear=2016.0,
            plx_mas=simbad_plx, rv_kms=simbad_rv)
    cond_pos = ((result.get('GBP_mag') is None
                 or result.get('GRP_mag') is None)
                and gaia_query_ra is not None
                and gaia_query_dec is not None)
    if cond_pos:
        adql_pos = (
            'SELECT TOP 10 RA_ICRS, DE_ICRS, BPmag, RPmag, '
            'e_BPmag, e_RPmag '
            'FROM "I/355/gaiadr3" WHERE 1 = CONTAINS('
            "POINT('ICRS', RA_ICRS, DE_ICRS), "
            "CIRCLE('ICRS', {0}, {1}, 0.0005))"
        ).format(gaia_query_ra, gaia_query_dec)
        gaia_pos_p = _vizier_json(adql_pos, url=vizier_url)
        if gaia_pos_p:
            best_gaia: Optional[Tuple[float, list]] = None
            for gv in gaia_pos_p.get('data', []):
                if len(gv) < 4:
                    continue
                rra, rdec = _pf(gv[0]), _pf(gv[1])
                if rra is None or rdec is None:
                    continue
                dist = _sep_arcsec(gaia_query_ra, gaia_query_dec,
                                   rra, rdec)
                if best_gaia is None or dist < best_gaia[0]:
                    best_gaia = (dist, gv)
            if best_gaia:
                gv = best_gaia[1]
                ra_gaia = _pf(gv[0]) if len(gv) > 0 else None
                dec_gaia = _pf(gv[1]) if len(gv) > 1 else None
                if ra_gaia is not None:
                    ra_deg = ra_gaia
                if dec_gaia is not None:
                    dec_deg = dec_gaia
                gaia_ref_epoch = 2016.0
                _set_if_none(result, 'GBP_mag',
                             _nv(gv[2]) if len(gv) > 2 else None)
                _set_if_none(result, 'GRP_mag',
                             _nv(gv[3]) if len(gv) > 3 else None)
                _set_if_none(result, 'GBP_err',
                             _nv(gv[4]) if len(gv) > 4 else None)
                _set_if_none(result, 'GRP_err',
                             _nv(gv[5]) if len(gv) > 5 else None)
    # ----- 5. Gaia DR3 astrophysical parameters -----
    if gaia_source_id is not None:
        adql_astro = (
            'SELECT TOP 1 teff_gspphot, logg_gspphot, mh_gspphot, '
            'radius_flame, lum_flame, mass_flame '
            'FROM gaiadr3.astrophysical_parameters '
            'WHERE source_id = {0}'
        ).format(gaia_source_id)
        astro_rows = _gaia_csv(adql_astro, url=gaia_url)
        if astro_rows:
            ar = astro_rows[0]
            _set_if_none(result, 'gaia_teff_gspphot',
                         _nv(ar.get('teff_gspphot')))
            _set_if_none(result, 'gaia_logg_gspphot',
                         _nv(ar.get('logg_gspphot')))
            _set_if_none(result, 'gaia_mh_gspphot',
                         _nv(ar.get('mh_gspphot')))
            _set_if_none(result, 'gaia_radius_flame',
                         _nv(ar.get('radius_flame')))
            _set_if_none(result, 'gaia_lum_flame',
                         _nv(ar.get('lum_flame')))
            _set_if_none(result, 'gaia_mass_flame',
                         _nv(ar.get('mass_flame')))
    # ----- 6. AllWISE photometry -----
    pmra_v = _pf(result.get('pmra_masyr'))
    pmdec_v = _pf(result.get('pmdec_masyr'))
    if wise_designation is not None:
        wise_row = _fetch_wise_by_designation(wise_designation,
                                              vizier_url=vizier_url)
        if wise_row is not None:
            _set_if_none(result, 'W1_mag', _nv(wise_row[1]))
            _set_if_none(result, 'W1_err', _nv(wise_row[2]))
            _set_if_none(result, 'W2_mag', _nv(wise_row[3]))
            _set_if_none(result, 'W2_err', _nv(wise_row[4]))
            _set_if_none(result, 'W3_mag', _nv(wise_row[5]))
            _set_if_none(result, 'W3_err', _nv(wise_row[6]))
            _set_if_none(result, 'W4_mag', _nv(wise_row[7]))
            _set_if_none(result, 'W4_err', _nv(wise_row[8]))
    cond_wise_pos = ((result.get('W1_mag') is None
                      or result.get('W2_mag') is None)
                     and ra_deg is not None and dec_deg is not None)
    if cond_wise_pos:
        if (gaia_ref_epoch is not None and pmra_v is not None
                and pmdec_v is not None):
            # propagate Gaia coords to AllWISE epoch (~2010.5)
            dt_yr = 2010.5 - gaia_ref_epoch
            mu_tot = math.sqrt(pmra_v ** 2 + pmdec_v ** 2)
            radius = max(20.0, min(300.0,
                                   abs(dt_yr) * mu_tot / 1000.0 + 12.0))
            ra_wise, dec_wise = _propagate_to_epoch(
                ra_deg=ra_deg, dec_deg=dec_deg,
                pmra=pmra_v, pmdec=pmdec_v,
                source_epoch_jyear=gaia_ref_epoch,
                target_epoch_jyear=2010.5,
                plx_mas=simbad_plx, rv_kms=simbad_rv)
        elif (simbad_ra_deg is not None
              and simbad_dec_deg is not None):
            ra_wise, dec_wise = _propagate_to_epoch(
                ra_deg=simbad_ra_deg, dec_deg=simbad_dec_deg,
                pmra=simbad_pmra, pmdec=simbad_pmdec,
                source_epoch_jyear=2000.0,
                target_epoch_jyear=2010.5,
                plx_mas=simbad_plx, rv_kms=simbad_rv)
            if (simbad_pmra is not None
                    and simbad_pmdec is not None):
                mu_tot = math.sqrt(simbad_pmra ** 2
                                   + simbad_pmdec ** 2)
                radius = max(20.0, min(300.0,
                                       abs(2010.5 - 2000.0)
                                       * mu_tot / 1000.0 + 12.0))
            else:
                radius = 30.0
        else:
            radius = 30.0
            ra_wise, dec_wise = ra_deg, dec_deg
        adql_wise = (
            'SELECT TOP 10 RAJ2000, DEJ2000, W1mag, e_W1mag, '
            'W2mag, e_W2mag, W3mag, e_W3mag, W4mag, e_W4mag '
            'FROM "II/328/allwise" WHERE 1 = CONTAINS('
            "POINT('ICRS', RAJ2000, DEJ2000), "
            "CIRCLE('ICRS', {0}, {1}, {2}/3600.0))"
        ).format(ra_wise, dec_wise, radius)
        wise_p = _vizier_json(adql_wise, url=vizier_url)
        if wise_p:
            best_wise: Optional[Tuple[float, list]] = None
            for wv in wise_p.get('data', []):
                if len(wv) < 6:
                    continue
                wra, wdec = _pf(wv[0]), _pf(wv[1])
                if wra is None or wdec is None:
                    continue
                dist = _sep_arcsec(ra_wise, dec_wise, wra, wdec)
                if best_wise is None or dist < best_wise[0]:
                    best_wise = (dist, wv)
            if best_wise:
                wv = best_wise[1]
                _set_if_none(result, 'W1_mag',
                             _nv(wv[2]) if len(wv) > 2 else None)
                _set_if_none(result, 'W1_err',
                             _nv(wv[3]) if len(wv) > 3 else None)
                _set_if_none(result, 'W2_mag',
                             _nv(wv[4]) if len(wv) > 4 else None)
                _set_if_none(result, 'W2_err',
                             _nv(wv[5]) if len(wv) > 5 else None)
                _set_if_none(result, 'W3_mag',
                             _nv(wv[6]) if len(wv) > 6 else None)
                _set_if_none(result, 'W3_err',
                             _nv(wv[7]) if len(wv) > 7 else None)
                _set_if_none(result, 'W4_mag',
                             _nv(wv[8]) if len(wv) > 8 else None)
                _set_if_none(result, 'W4_err',
                             _nv(wv[9]) if len(wv) > 9 else None)
    return result


# =============================================================================
# File-locking helper
# =============================================================================
class _FileLock:
    """
    Cross-platform best-effort file lock.

    On POSIX uses ``fcntl.flock`` on a sidecar ``*.lock`` file. On platforms
    without ``fcntl`` falls back to spinning on ``O_EXCL`` creation of a
    sentinel file. Either way the lock is released on context exit.
    """
    # lock acquisition timeout (seconds)
    DEFAULT_TIMEOUT = 30.0
    # spin-wait sleep between attempts (seconds)
    SLEEP_INTERVAL = 0.05

    def __init__(self, lockpath: str,
                 timeout: float = DEFAULT_TIMEOUT) -> None:
        """
        :param lockpath: str, full path to the lock file (will be created)
        :param timeout: float, how long to wait before raising
        """
        # path of the lock-file used as the mutex
        self.lockpath = lockpath
        # acquisition timeout
        self.timeout = timeout
        # the open file handle (for fcntl path) or fd (for fallback)
        self._fh = None
        # whether we are using the fallback spin-wait path
        self._fallback = _fcntl is None

    def __enter__(self) -> '_FileLock':
        """Acquire the lock, blocking up to ``self.timeout`` seconds."""
        # ensure the parent directory of the lock file exists
        os.makedirs(os.path.dirname(self.lockpath), exist_ok=True)
        # start time for timeout accounting
        start = time.time()
        # POSIX path: open the lock file and flock() it
        if not self._fallback:
            # open the sidecar file (create if missing)
            self._fh = open(self.lockpath, 'a+')
            # spin until LOCK_EX succeeds or we time out
            while True:
                try:
                    _fcntl.flock(self._fh.fileno(),
                                 _fcntl.LOCK_EX | _fcntl.LOCK_NB)
                    return self
                except (BlockingIOError, OSError):
                    if (time.time() - start) > self.timeout:
                        self._fh.close()
                        emsg = 'Timeout acquiring lock {0}'.format(
                            self.lockpath)
                        raise AperoCodedException(None, message=emsg)
                    time.sleep(self.SLEEP_INTERVAL)
        # Fallback path: O_EXCL spin-wait
        while True:
            try:
                fd = os.open(self.lockpath,
                             os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                # write our pid for debugging then keep fd open
                os.write(fd, str(os.getpid()).encode('utf-8'))
                self._fh = fd
                return self
            except FileExistsError:
                if (time.time() - start) > self.timeout:
                    emsg = 'Timeout acquiring lock {0}'.format(self.lockpath)
                    raise AperoCodedException(None, message=emsg)
                time.sleep(self.SLEEP_INTERVAL)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Release the lock and clean up."""
        # POSIX path
        if not self._fallback and self._fh is not None:
            try:
                _fcntl.flock(self._fh.fileno(), _fcntl.LOCK_UN)
            finally:
                self._fh.close()
                self._fh = None
            return
        # Fallback path
        if self._fallback and self._fh is not None:
            try:
                os.close(self._fh)
            finally:
                self._fh = None
                # remove the sentinel file so others can acquire
                try:
                    os.remove(self.lockpath)
                except OSError:
                    pass


# =============================================================================
# Define the AstrometricDatabase class
# =============================================================================
class AstrometricDatabase:
    """
    Yaml-backed astrometric "database" with a call-surface compatible with
    the legacy ``drs_database.AstrometricDatabase`` (where it makes sense).

    Each object lives in its own yaml file under
    ``params['DRS_DATA_ASSETS']/astrometrics/<APERO_NAME>.yaml``; the file
    layout matches the example in
    ``vscode_share/astrometric_example.yaml``.

    The class is **picklable** (state is just simple python objects) so it
    can be passed through multiprocessing pools, and module-level caches
    survive across forks.
    """
    # class-level identifier used in error messages
    classname = 'AstrometricDatabase'

    def __init__(self, params: ParamDict,
                 shortname: Optional[str] = None) -> None:
        """
        Construct the astrometric database.

        :param params: ParamDict, the apero parameter dictionary - only
                       ``params['DRS_DATA_ASSETS']`` is used.
        :param shortname: str or None, the calling recipe shortname (kept
                          for parity with the old API; used only in log /
                          notes messages).
        """
        # set function name (display only)
        # _ = display_func('__init__', __NAME__, self.classname)
        # store the parameter dict
        self.params = params
        # store the recipe shortname for log messages
        self.shortname = shortname or 'None'
        # base assets path from params (may not exist on disk yet)
        assets_root = str(params['PATH.ASSETS'])
        # absolute path to the astrometrics directory
        self.path = os.path.abspath(os.path.join(assets_root, ASTROM_SUBDIR))
        # absolute path to the lock directory
        self.lockdir = os.path.join(self.path, LOCK_SUBDIR)
        # parity attributes with the legacy API (unused but read by callers)
        self.name = 'astrom'
        self.kind = 'astrom'
        # try to record the instrument name (best-effort)
        try:
            self.instrument = str(params['INSTRUMENT'])
        except Exception:
            self.instrument = 'None'
        # legacy attribute kept as None for callers that expected the old
        # SQL-backed manager to expose pconst / database handles
        self.pconst = None
        self.database = None
        # TAP endpoints (read from params; fall back to module defaults)
        self.simbad_url = self._read_param('SIMBAD_TAPURL', SIMBAD_TAP)
        self.gaia_url = self._read_param('GAIA_URL', GAIA_TAP)
        self.vizier_url = self._read_param('VIZIER_TAPURL', VIZIER_TAP)

    def _read_param(self, key: str, default: str) -> str:
        '''Best-effort param lookup that tolerates missing keys.'''
        try:
            value = self.params[key]
        except Exception:
            return default
        if value is None or str(value).strip() in ('', 'None', 'NULL'):
            return default
        return str(value)

    # -------------------------------------------------------------------------
    # Pickle support
    # -------------------------------------------------------------------------
    def __getstate__(self) -> dict:
        """Return picklable state (everything in __dict__ already is)."""
        return dict(self.__dict__)

    def __setstate__(self, state: dict) -> None:
        """Restore pickled state."""
        self.__dict__.update(state)

    # -------------------------------------------------------------------------
    # Compatibility no-op
    # -------------------------------------------------------------------------
    def load_db(self) -> None:
        """
        Compatibility shim for callers that used to do ``objdbm.load_db()``
        on the old SQL-backed class. Triggers a (cached) directory scan.
        """
        # ensure the index is populated (cheap if already loaded)
        self._ensure_loaded()

    def warm_cache(self, *args: Any, **kwargs: Any) -> None:
        """
        Compatibility shim for the legacy SQL class which used to pre-load
        the full table to avoid per-object SQL round-trips. The yaml-backed
        implementation already lazy-loads everything in :meth:`_ensure_loaded`
        so this call is now equivalent to :meth:`load_db`.
        """
        # accept and ignore any args (legacy was warm_cache(pconst))
        _ = args, kwargs
        self._ensure_loaded()

    # -------------------------------------------------------------------------
    # Index loading / cache management
    # -------------------------------------------------------------------------
    def _ensure_loaded(self, force: bool = False) -> None:
        """
        Make sure the in-memory index for ``self.path`` is up to date.

        Uses two cheap freshness checks before doing any I/O:
            1. directory mtime - if unchanged we trust the in-memory cache
            2. per-file mtime  - only re-read yaml files that changed

        :param force: bool, if True ignore caches and re-scan from disk
        """
        # if the directory does not exist yet, init empty caches and return
        if not os.path.isdir(self.path):
            _NAME_INDEX.setdefault(self.path, dict())
            _ENTRY_CACHE.setdefault(self.path, dict())
            _MTIME_CACHE.setdefault(self.path, dict())
            _DIR_MTIME[self.path] = -1.0
            return
        # current directory mtime
        try:
            dir_mtime = os.path.getmtime(self.path)
        except OSError:
            dir_mtime = -1.0
        # cheap path: if dir mtime unchanged and not forcing, we're done
        if (not force
                and self.path in _DIR_MTIME
                and _DIR_MTIME[self.path] == dir_mtime
                and self.path in _NAME_INDEX):
            return
        # ensure cache slots exist for this path
        name_index = _NAME_INDEX.setdefault(self.path, dict())
        entries = _ENTRY_CACHE.setdefault(self.path, dict())
        mtimes = _MTIME_CACHE.setdefault(self.path, dict())
        # set of yaml files currently on disk
        disk_files = set()
        # track if anything changed (so we can decide whether to invalidate)
        any_changes = False
        # iterate over directory entries (no recursion - flat layout)
        for fname in os.listdir(self.path):
            # only consider .yaml files (skip .locks, hidden, etc.)
            if not fname.endswith(YAML_EXT):
                continue
            # skip dotfiles (tmp files etc.)
            if fname.startswith('.'):
                continue
            # full path
            fpath = os.path.join(self.path, fname)
            # skip directories that happen to end in .yaml
            if not os.path.isfile(fpath):
                continue
            # remember we saw this file
            disk_files.add(fname)
            # fetch current mtime
            try:
                fmtime = os.path.getmtime(fpath)
            except OSError:
                continue
            # skip files that have not changed since last load
            if (not force
                    and fname in mtimes
                    and mtimes[fname] == fmtime):
                continue
            # (re)load this yaml file
            try:
                entry = self._read_yaml(fpath)
            except Exception as exc:
                # log a warning but do not crash - one bad file should not
                # break the whole catalogue
                wmsg = 'Skipping unreadable astrometric yaml: {0} ({1})'
                warnings.warn(wmsg.format(fpath, exc))
                continue
            # the canonical APERO name is required
            apero_name = entry.get(APERO_NAME_KEY)
            if _is_null(apero_name):
                wmsg = ('Astrometric yaml {0} has no APERO_NAME - '
                        'skipping').format(fpath)
                warnings.warn(wmsg)
                continue
            # store the entry keyed by the canonical name
            entries[str(apero_name)] = entry
            # remember mtime so we don't reload next time
            mtimes[fname] = fmtime
            # add every searchable key into the name index
            self._index_entry(name_index, str(apero_name), entry)
            any_changes = True
        # detect deletions on disk (files we cached but no longer exist)
        deleted = [f for f in mtimes if f not in disk_files]
        if deleted:
            # cheapest correct option: nuke caches for this path and rebuild
            _NAME_INDEX[self.path] = dict()
            _ENTRY_CACHE[self.path] = dict()
            _MTIME_CACHE[self.path] = dict()
            _DIR_MTIME[self.path] = -1.0
            self._invalidate_resolve_cache()
            self._ensure_loaded(force=True)
            return
        # remember the directory mtime for the cheap freshness check
        _DIR_MTIME[self.path] = dir_mtime
        # only invalidate the per-name resolution cache if we actually
        # picked up new/changed entries
        if any_changes:
            self._invalidate_resolve_cache()

    def _index_entry(self, name_index: Dict[str, str],
                     apero_name: str, entry: Dict[str, Any]) -> None:
        """
        Add an entry's searchable keys into ``name_index``.

        :param name_index: dict, the mutable cleaned-name -> APERO_NAME map
        :param apero_name: str, the canonical APERO name
        :param entry: dict, the loaded yaml entry
        """
        def _index(value: Any, primary: bool) -> None:
            for variant in name_search_variants(value):
                if primary:
                    name_index[variant] = apero_name
                else:
                    name_index.setdefault(variant, apero_name)

        # always index the cleaned APERO name itself (primary)
        _index(apero_name, True)
        # index the other primary name keys (do not overwrite primary)
        for key in NAME_KEYS:
            if key == APERO_NAME_KEY:
                continue
            value = entry.get(key)
            if _is_null(value):
                continue
            _index(value, False)
        # index every alias (if any)
        aliases = entry.get(ALIAS_KEY)
        if isinstance(aliases, str):
            # tolerate pipe-delimited strings (legacy db format)
            aliases = aliases.split('|')
        if isinstance(aliases, (list, tuple)):
            for alias in aliases:
                if _is_null(alias):
                    continue
                _index(alias, False)

    @staticmethod
    def _invalidate_resolve_cache() -> None:
        """Clear the per-process name resolution cache."""
        # simple wholesale clear is fine - it only stores name lookups
        _RESOLVE_CACHE.clear()

    @staticmethod
    def _read_yaml(fpath: str) -> Dict[str, Any]:
        """
        Read a yaml file and return its top-level dict.

        :param fpath: str, absolute path to the yaml file
        :return: dict, the parsed yaml content
        """
        # open with explicit utf-8 encoding (yaml files contain unicode)
        with open(fpath, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=_YAML_SAFE_LOADER)
        # ensure we return a dict even for empty files
        if data is None:
            return dict()
        if not isinstance(data, dict):
            emsg = 'Astrometric yaml {0} is not a mapping'.format(fpath)
            raise AperoCodedException(None, message=emsg)
        return data

    @staticmethod
    def _write_yaml(fpath: str, data: Dict[str, Any]) -> None:
        """
        Atomically write ``data`` to ``fpath`` as yaml.

        Uses a tmp-file + ``os.replace`` so a crash mid-write cannot leave
        a half-written yaml on disk.

        :param fpath: str, target file path
        :param data: dict, the data to dump
        """
        # write to a tmp file alongside the target so os.replace is atomic
        target_dir = os.path.dirname(fpath)
        os.makedirs(target_dir, exist_ok=True)
        # delete=False semantics via mkstemp - we control unlink ourselves
        fd, tmppath = tempfile.mkstemp(prefix='.astrom_', suffix=YAML_EXT,
                                       dir=target_dir)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, default_flow_style=False,
                               sort_keys=False, allow_unicode=True)
            # atomic rename onto the final filename
            os.replace(tmppath, fpath)
        except Exception:
            # clean up the tmp file if anything went wrong
            try:
                os.remove(tmppath)
            except OSError:
                pass
            raise

    # -------------------------------------------------------------------------
    # Public API: name resolution
    # -------------------------------------------------------------------------
    def find_objname(self, objname: Optional[Any] = None,
                     return_flag: bool = False
                     ) -> Tuple[str, Union[bool, int]]:
        """
        Resolve ``objname`` against the catalogue and return the canonical
        ``APERO_NAME`` used by the DRS.

        Lookup order (after cleaning ``objname``):
            1. matches a cleaned ``APERO_NAME``                -> flag = 1
            2. matches a cleaned ``ORIGINAL_NAME`` /
               ``SIMBAD_NAME`` / any alias                     -> flag = 2
            3. not found                                       -> flag = 0

        :param objname: str, the raw object name from a header
        :param return_flag: bool, if True returns the int flag, else a bool

        :return: ``(name, flag)`` or ``(name, found_bool)``
        """
        # _ = display_func('find_objname', __NAME__, self.classname)
        # guard against a missing input
        if objname is None:
            if return_flag:
                return '', 0
            return '', False
        # cast to string defensively
        raw = str(objname)
        # per-process cache key (path + raw input)
        cache_key = (self.path, raw)
        # fast path: hit in resolution cache
        if cache_key in _RESOLVE_CACHE:
            cobj, found = _RESOLVE_CACHE[cache_key]
            if return_flag:
                return cobj, found
            return cobj, found > 0
        # reserved object names (CALIB / SKY / TEST) bypass the catalogue
        if raw in RESERVED_OBJ_NAMES:
            _RESOLVE_CACHE[cache_key] = (raw, 1)
            if return_flag:
                return raw, 1
            return raw, True
        # clean the input name into the comparable form
        cleaned = clean_object(raw)
        # null inputs short-circuit (can't resolve)
        if cleaned == 'Null':
            _RESOLVE_CACHE[cache_key] = ('', 0)
            if return_flag:
                return '', 0
            return '', False
        # also short-circuit reserved names after cleaning
        if cleaned in RESERVED_OBJ_NAMES:
            _RESOLVE_CACHE[cache_key] = (cleaned, 1)
            if return_flag:
                return cleaned, 1
            return cleaned, True
        # ensure the name index is loaded (and fresh)
        self._ensure_loaded()
        # grab the index for this path (always present after _ensure_loaded)
        name_index = _NAME_INDEX.get(self.path, dict())
        entries = _ENTRY_CACHE.get(self.path, dict())
        # try to look up via the variant list (whitespace / sign / _
        # tolerant); the canonical clean_object value is the first
        # variant so behaviour for already-clean names is unchanged.
        apero_name: Optional[str] = None
        hit_variant: Optional[str] = None
        for variant in name_search_variants(raw):
            if variant in name_index:
                apero_name = name_index[variant]
                hit_variant = variant
                break
        if apero_name is not None:
            # decide if it was a primary or alias hit
            if hit_variant == clean_object(apero_name):
                flag = 1
            else:
                flag = 2
            # sanity check: entry exists too
            if apero_name not in entries:
                flag = 0
                apero_name = cleaned
        else:
            # not found - return the cleaned name for downstream consistency
            apero_name = cleaned
            flag = 0
        # cache the resolution for this raw input
        _RESOLVE_CACHE[cache_key] = (apero_name, flag)
        # return in the requested form
        if return_flag:
            return apero_name, flag
        return apero_name, flag > 0

    def find_objnames(self,
                      objnames: Union[List[str], np.ndarray, str],
                      allow_empty: bool = True,
                      listname: Optional[str] = None
                      ) -> Tuple[List[str], List[str]]:
        """
        Resolve a list of object names. Thin wrapper around
        :meth:`find_objname`.

        :param objnames: list/array/str, the raw names to resolve
        :param allow_empty: bool, if False raise when no names resolve
        :param listname: str, name of the input list (for error messages)

        :return: ``(found_apero_names, missing_raw_names)``
        """
        func_name = display_func('find_objnames', __NAME__, self.classname)
        # accept a single string for convenience
        if isinstance(objnames, str):
            objnames = [objnames]
        # accept anything iterable that is not already list/ndarray
        if not isinstance(objnames, (list, np.ndarray)):
            objnames = list(objnames)
        # storage for results
        found_names: List[str] = []
        missing_names: List[str] = []
        # iterate and resolve one-by-one (cache makes repeats free)
        for objname in objnames:
            apero_name, found = self.find_objname(objname)
            if found:
                found_names.append(apero_name)
            else:
                missing_names.append(str(objname))
        # raise if caller requires at least one resolution
        if len(found_names) == 0 and not allow_empty:
            label = listname if listname is not None else func_name
            emsg = ('No objects found in astrometric catalogue.'
                    '\n\tPlease add objects under {0}'
                    '\n\tListname={1}'
                    '\n\tObjnames: "{2}"')
            eargs = [self.path, label,
                     ', '.join(str(n) for n in objnames)]
            raise AperoCodedException(None, message=emsg.format(*eargs),
                                      targs=eargs)
        # return the two lists
        return found_names, missing_names

    # -------------------------------------------------------------------------
    # Public API: get / iterate entries
    # -------------------------------------------------------------------------
    def get_entries(self, columns: str = '*',
                    nentries: Optional[int] = None,
                    condition: Optional[Any] = None
                    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        Return a slice of the catalogue.

        :param columns: str, ``'*'`` returns the full entry dicts, otherwise
                        a comma-separated list of top-level keys to keep.
        :param nentries: int or None, limit the number of returned entries
                         (returns a single entry / None if ``nentries == 1``)
        :param condition: callable or None,
                          ``condition(entry_dict) -> bool`` predicate to
                          filter entries. (We accept a callable rather than
                          an SQL string because there is no SQL here.)
                          ``None`` means no filtering.

        :return: list of dicts, a single dict (``nentries == 1``) or
                 ``None`` if there are no matches.
        """
        # _ = display_func('get_entries', __NAME__, self.classname)
        # ensure caches are populated and fresh
        self._ensure_loaded()
        # grab the entry dict for this path
        entries = _ENTRY_CACHE.get(self.path, dict())
        # parse the columns request
        if columns == '*' or columns is None:
            wanted_cols: Optional[List[str]] = None
        else:
            wanted_cols = [c.strip() for c in str(columns).split(',')
                           if c.strip()]
        # accept old-style SQL strings only as a soft warning - we cannot
        # honour them, but we also should not silently ignore them
        if isinstance(condition, str):
            wmsg = ('AstrometricDatabase.get_entries received an SQL-style '
                    'condition string ({0!r}); ignoring. Pass a callable '
                    'instead.').format(condition)
            warnings.warn(wmsg)
            condition = None
        # build the filtered/projected output list
        out: List[Dict[str, Any]] = []
        for apero_name, entry in entries.items():
            # apply the predicate if given
            if condition is not None and not condition(entry):
                continue
            # project columns if requested (with legacy column aliasing)
            if wanted_cols is None:
                row = dict(entry)
            else:
                row = dict()
                for col in wanted_cols:
                    # try a legacy alias first, then a direct yaml key
                    if col in LEGACY_COL_MAP:
                        row[col] = LEGACY_COL_MAP[col](entry)
                    else:
                        row[col] = entry.get(col)
            # always keep the canonical name accessible
            row.setdefault(APERO_NAME_KEY, apero_name)
            out.append(row)
            # respect nentries limit early
            if nentries is not None and len(out) >= nentries:
                break
        # honour the legacy nentries == 1 convention
        if nentries == 1:
            return out[0] if out else None
        # return list (possibly empty)
        return out

    def get_entry(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Return the full yaml entry for any name (APERO_NAME, ORIGINAL_NAME,
        SIMBAD_NAME, or alias). The name is resolved via
        :meth:`find_objname` first.

        :param name: str, any name that can identify the object
        :return: dict or None if not found
        """
        # ensure caches are loaded
        self._ensure_loaded()
        # resolve the input to a canonical APERO_NAME first
        apero_name, found = self.find_objname(name)
        if not found:
            return None
        # direct lookup against the entry cache
        entries = _ENTRY_CACHE.get(self.path, dict())
        return entries.get(apero_name)

    def count(self, condition: Optional[Any] = None) -> int:
        """
        Count the catalogue entries (optionally filtered by ``condition``).

        :param condition: callable or None, see :meth:`get_entries`
        :return: int
        """
        # ensure caches are loaded
        self._ensure_loaded()
        entries = _ENTRY_CACHE.get(self.path, dict())
        # no condition - cheap len()
        if condition is None or isinstance(condition, str):
            return len(entries)
        # predicate path
        return sum(1 for e in entries.values() if condition(e))

    # -------------------------------------------------------------------------
    # Public API: write entries
    # -------------------------------------------------------------------------
    def add_entry(self, entry: Dict[str, Any],
                  overwrite: bool = True,
                  merge: bool = True,
                  skip_validation: bool = False,
                  allow_rejected: bool = False) -> str:
        """
        Add (or update) a single entry in the catalogue.

        The entry **must** contain an ``APERO_NAME`` key; the yaml file on
        disk is named after the cleaned form of that name. The write is
        protected by a per-file lock so concurrent processes can safely
        call this method.

        :param entry: dict, the new/updated entry. Must contain
                      ``APERO_NAME``.
        :param overwrite: bool, if False and the file already exists, raise.
        :param merge: bool, if True merge with the existing on-disk entry
                      (new keys replace old keys); if False replace the
                      entry wholesale.
        :param skip_validation: bool, if True bypass the
                               :data:`REQUIRED_FIELDS_STAR` check
                               (used by migration / back-fill scripts).
        :param allow_rejected: bool, if True allow writing even when the
                              same APERO_NAME appears in the
                              ``rejected/`` sub-directory (default: refuse
                              and raise).

        :return: str, the absolute path of the yaml file that was written
        """
        # validate input early
        if not isinstance(entry, dict):
            emsg = 'add_entry() expects a dict, got {0}'
            raise AperoCodedException(
                None, message=emsg.format(type(entry).__name__))
        # extract & validate the APERO_NAME
        apero_name = entry.get(APERO_NAME_KEY)
        if _is_null(apero_name):
            emsg = 'add_entry() entry missing required key "{0}"'
            raise AperoCodedException(
                None, message=emsg.format(APERO_NAME_KEY))
        # refuse to write objects that exist in the rejected/ sub-dir
        # (unless explicitly allowed by the caller)
        if not allow_rejected:
            astrom_root = os.path.dirname(os.path.abspath(self.path))
            existing = find_yaml_in_status_dirs(astrom_root,
                                                str(apero_name))
            if existing is not None and existing[1] == STATUS_REJECTED:
                emsg = ('Astrometric entry "{0}" is on the reject list '
                        '({1}); refusing to add. Pass '
                        'allow_rejected=True to override.')
                raise AperoCodedException(
                    None,
                    message=emsg.format(apero_name, existing[0]))
        # build the on-disk file path
        fname = _safe_filename(str(apero_name))
        fpath = os.path.join(self.path, fname)
        # build the lock-file path
        lockpath = os.path.join(self.lockdir, fname + '.lock')
        # ensure the catalogue directory exists
        os.makedirs(self.path, exist_ok=True)
        # acquire the per-file lock for the write window
        with _FileLock(lockpath):
            # decide what to write based on existence + flags
            if os.path.isfile(fpath):
                if not overwrite:
                    emsg = 'Astrometric entry already exists: {0}'
                    raise AperoCodedException(None,
                                              message=emsg.format(fpath))
                # merge with existing on-disk entry (entry overrides existing)
                if merge:
                    try:
                        existing = self._read_yaml(fpath)
                    except Exception:
                        existing = dict()
                    existing.update(entry)
                    final = existing
                else:
                    final = dict(entry)
            else:
                final = dict(entry)
            # add a NOTES timestamp if none present (mirrors legacy behaviour)
            if 'NOTES' not in final or _is_null(final.get('NOTES')):
                final['NOTES'] = ('Added on {0} by drs_astrometrics '
                                  '(shortname={1})').format(
                    Time.now().iso, self.shortname)
            # enforce required-fields contract before writing (unless
            # the caller is intentionally back-filling / migrating)
            if not skip_validation:
                missing = validate_required_fields(final)
                if missing:
                    emsg = ('Astrometric entry "{0}" is missing required '
                            'field(s): {1}. Set them on the entry, or '
                            'set NO_PM=True if no proper motion is '
                            'known, or pass skip_validation=True to '
                            'bypass.')
                    raise AperoCodedException(
                        None,
                        message=emsg.format(apero_name,
                                            ', '.join(missing)))
            # populate / refresh provenance metadata
            _stamp_metadata(final, author=DEFAULT_AUTHOR)
            # do the atomic write
            self._write_yaml(fpath, final)
        # invalidate any in-memory caches for this path so next read sees it
        _DIR_MTIME.pop(self.path, None)
        if self.path in _MTIME_CACHE:
            _MTIME_CACHE[self.path].pop(fname, None)
        self._invalidate_resolve_cache()
        # return the path that was written (useful for callers/logging)
        return fpath

    def add_entries(self, entries: List[Dict[str, Any]],
                    overwrite: bool = True,
                    merge: bool = True,
                    skip_validation: bool = False,
                    allow_rejected: bool = False) -> List[str]:
        """
        Add (or update) a list of entries in the catalogue.

        Each entry **must** contain an ``APERO_NAME`` key. Entries are
        written one-by-one via :meth:`add_entry` (so each acquires its own
        per-file lock independently).

        :param entries: list of dicts, the new/updated entries.
        :param overwrite: bool, see :meth:`add_entry`
        :param merge: bool, see :meth:`add_entry`
        :param skip_validation: bool, see :meth:`add_entry`
        :param allow_rejected: bool, see :meth:`add_entry`

        :return: list of str, the absolute paths of the yaml files written.
        """
        # validate input early
        if not isinstance(entries, (list, tuple)):
            emsg = 'add_entries() expects a list of dicts, got {0}'
            raise AperoCodedException(
                None, message=emsg.format(type(entries).__name__))
        # write each entry in turn and collect the resulting paths
        out_paths: List[str] = []
        for entry in entries:
            out_paths.append(self.add_entry(
                entry, overwrite=overwrite, merge=merge,
                skip_validation=skip_validation,
                allow_rejected=allow_rejected))
        return out_paths

    # -------------------------------------------------------------------------
    # Remote resolution + archive refresh
    # -------------------------------------------------------------------------
    def resolve_target(self, name: str,
                       aliases: Optional[List[str]] = None,
                       apero_name: Optional[str] = None,
                       original_name: Optional[str] = None,
                       apero_class: Optional[str] = None,
                       epoch_jd: float = 2451545.0,
                       ) -> Optional[Dict[str, Any]]:
        """
        Resolve a free-form target name into a fully-populated yaml entry
        dict by querying SIMBAD / Gaia / VizieR.

        The returned dict has the same schema as the on-disk yaml files
        (see :data:`LEGACY_COL_MAP` / ``vscode_share/astrometric_example``)
        and is suitable for passing straight to :meth:`add_entry`.

        :param name: str, the user-supplied target name (will be sent to
                     SIMBAD; aliases are tried as fallbacks if given).
        :param aliases: optional list of fall-back names to try if SIMBAD
                        does not recognise ``name``.
        :param apero_name: optional override for the entry's
                          ``APERO_NAME``. Defaults to
                          ``clean_object(name)``.
        :param original_name: optional override for ``ORIGINAL_NAME``
                              (defaults to ``name``).
        :param apero_class: optional value for ``APERO_CLASS``.
        :param epoch_jd: float, the EPOCH (Julian Date) to record on the
                         entry. Defaults to J2000 (JD 2451545.0) which is
                         the SIMBAD reference epoch.

        :return: dict (yaml entry) or ``None`` if no resolver succeeded.
        """
        # build the base entry shell
        entry: Dict[str, Any] = dict()
        entry['APERO_NAME'] = apero_name or clean_object(name)
        entry['ORIGINAL_NAME'] = original_name or name
        if apero_class is not None:
            entry['APERO_CLASS'] = apero_class
        entry['EPOCH'] = epoch_jd
        if aliases:
            # store aliases as a clean list
            entry['ALIASES'] = [str(a) for a in aliases if _nv(a)]
        # ensure full schema scaffolding (so merge helpers see all keys)
        _full_resolve_schema(entry)
        # try the primary name first
        simbad = _resolve_from_name(name,
                                    simbad_url=self.simbad_url,
                                    gaia_url=self.gaia_url,
                                    vizier_url=self.vizier_url)
        # alias fallbacks (cap at 5 like the upstream tool)
        if simbad is None and aliases:
            for alias in list(aliases)[:5]:
                a = _nv(alias)
                if a and a != name:
                    simbad = _resolve_from_name(
                        a,
                        simbad_url=self.simbad_url,
                        gaia_url=self.gaia_url,
                        vizier_url=self.vizier_url)
                    if simbad is not None:
                        break
        # nothing found - bail out
        if simbad is None:
            return None
        # merge SIMBAD / Gaia / WISE results into the entry
        _update_yaml_from_simbad(entry, simbad)
        return entry

    def update_archive(self, overwrite_existing: bool = False,
                       limit: Optional[int] = None,
                       delay_s: float = 0.3) -> Dict[str, int]:
        """
        Refresh the on-disk archive by re-resolving each entry against
        SIMBAD / Gaia / VizieR.

        For every yaml file under :attr:`path`:
            - if it is already fully resolved and ``overwrite_existing``
              is False, only derived fields are recomputed;
            - otherwise the entry is re-queried and merged in-place.

        :param overwrite_existing: bool, if True, re-query SIMBAD even
                                   for already-resolved entries.
        :param limit: int or None, process at most this many files.
        :param delay_s: float, sleep between queries (seconds) to be
                        polite to TAP servers.

        :return: dict with keys 'resolved', 'failed', 'skipped' (counts).
        """
        # ensure caches are loaded so we can iterate entries by name
        self._ensure_loaded()
        # flat list of (apero_name, entry) sorted by name for stability
        entries = _ENTRY_CACHE.get(self.path, dict())
        names = sorted(entries.keys())
        if limit is not None:
            names = names[:limit]
        # accumulators
        resolved = 0
        failed = 0
        skipped = 0
        # iterate
        for idx, apero_name in enumerate(names):
            entry = dict(entries[apero_name])
            # ensure the entry has the full schema
            _full_resolve_schema(entry)
            # decide whether to re-query
            already = (entry.get('SIMBAD_NAME') is not None
                       and not overwrite_existing)
            if already:
                # just refresh derived fields and write back
                _derive_fields(entry)
                self.add_entry(entry, overwrite=True, merge=False,
                               skip_validation=True)
                skipped += 1
                continue
            # pick the best name to send to SIMBAD
            search_name = None
            for key in ('SIMBAD_NAME', 'ORIGINAL_NAME', 'APERO_NAME'):
                v = _nv(entry.get(key))
                if v is not None:
                    search_name = v
                    break
            if search_name is None:
                skipped += 1
                continue
            # collect aliases for fallbacks
            aliases = entry.get('ALIASES') or []
            if isinstance(aliases, str):
                aliases = [aliases]
            # resolve via SIMBAD/Gaia
            simbad = _resolve_from_name(search_name,
                                        simbad_url=self.simbad_url,
                                        gaia_url=self.gaia_url,
                                        vizier_url=self.vizier_url)
            if simbad is None:
                for alias in list(aliases)[:5]:
                    a = _nv(alias)
                    if a and a != search_name:
                        simbad = _resolve_from_name(
                            a,
                            simbad_url=self.simbad_url,
                            gaia_url=self.gaia_url,
                            vizier_url=self.vizier_url)
                        if simbad is not None:
                            break
            # merge or fail
            if simbad is None:
                _derive_fields(entry)
                self.add_entry(entry, overwrite=True, merge=False,
                               skip_validation=True)
                failed += 1
            else:
                _update_yaml_from_simbad(entry, simbad)
                self.add_entry(entry, overwrite=True, merge=False,
                               skip_validation=True)
                resolved += 1
            # rate-limit between TAP queries
            if delay_s > 0 and idx + 1 < len(names):
                time.sleep(delay_s)
        # return counts
        out = dict()
        out['resolved'] = resolved
        out['failed'] = failed
        out['skipped'] = skipped
        return out


# =============================================================================
# Path-based helpers (no ParamDict required)
# =============================================================================
# These are intentionally decoupled from ``AstrometricDatabase`` and the
# apero ParamDict so that callers (e.g. apero-ri) can search the yaml
# directory directly with no apero runtime initialisation.
#
# The functions below take a directory path and return plain python data.
# Results are mtime-cached per-process for speed.

# per-process cache: astrom_dir -> (mtime_signature, list[(apero_name, entry)])
_DIR_CACHE: Dict[str, Tuple[float, List[Tuple[str, Dict[str, Any]]]]] = {}
# per-process cache: astrom_dir -> (mtime_signature, name_index)
_DIR_NAME_INDEX: Dict[str, Tuple[float, Dict[str, str]]] = {}


def _dir_mtime_signature(astrom_dir: str) -> float:
    """Return a signature that changes when any *.yaml in the dir changes.

    Computed as ``max(yaml mtime) + n_yaml * 1e-6``. We deliberately
    avoid using the directory's own mtime so that our cache files
    written into the same directory do not invalidate the signature.

    Includes yamls in the canonical status sub-directories
    (``verified``/``pending``/``rejected``) when ``astrom_dir`` is the
    top-level astrometrics root, so callers that pass the root see a
    signature that changes when any sub-dir changes.

    :param astrom_dir: str, directory containing ``*.yaml`` astrometric
                       entries
    :return: float, a signature value (not interpretable as a real time)
    """
    if not os.path.isdir(astrom_dir):
        return -1.0
    max_mtime = 0.0
    n_yaml = 0
    scan_dirs = [astrom_dir]
    for sub in STATUS_SUBDIRS:
        sub_path = os.path.join(astrom_dir, sub)
        if os.path.isdir(sub_path):
            scan_dirs.append(sub_path)
    for d in scan_dirs:
        try:
            with os.scandir(d) as it:
                for ent in it:
                    if not ent.name.endswith(YAML_EXT):
                        continue
                    try:
                        st = ent.stat()
                    except OSError:
                        continue
                    if st.st_mtime > max_mtime:
                        max_mtime = st.st_mtime
                    n_yaml += 1
        except OSError:
            continue
    return max_mtime + n_yaml * 1e-6


def iter_yaml_files(astrom_dir: str) -> List[str]:
    """List the absolute paths of every ``*.yaml`` file in ``astrom_dir``.

    Includes yamls in the canonical status sub-directories
    (``verified``/``pending``/``rejected``) when ``astrom_dir`` is the
    top-level astrometrics root, so this transparently spans the new
    on-disk layout. Sub-dir scanning is skipped when ``astrom_dir`` is
    *itself* one of the status sub-dirs (avoids infinite recursion-like
    layouts and keeps targeted scans fast).

    :param astrom_dir: str, directory to scan (non-recursive within
                       each tier)
    :return: list of absolute file paths, sorted alphabetically
    """
    if not os.path.isdir(astrom_dir):
        return []
    out: List[str] = []
    seen: set = set()
    base = os.path.basename(os.path.normpath(astrom_dir)).lower()
    # Only descend into status sub-dirs when the caller passed the
    # top-level root (i.e. not a status sub-dir itself). Sub-dir
    # entries take priority: if the same basename also exists at the
    # top level (legacy / partial-migration leftover) the top-level
    # copy is dropped so callers see exactly one entry per name.
    if base not in STATUS_SUBDIRS:
        for sub in STATUS_SUBDIRS:
            sub_path = os.path.join(astrom_dir, sub)
            if not os.path.isdir(sub_path):
                continue
            for fn in sorted(os.listdir(sub_path)):
                if not fn.endswith(YAML_EXT):
                    continue
                if fn in seen:
                    continue
                seen.add(fn)
                out.append(os.path.abspath(
                    os.path.join(sub_path, fn)))
    for fn in sorted(os.listdir(astrom_dir)):
        if not fn.endswith(YAML_EXT):
            continue
        if fn in seen:
            continue
        seen.add(fn)
        out.append(os.path.abspath(os.path.join(astrom_dir, fn)))
    return out


def astrom_status_dir(astrom_root: str, status: str) -> str:
    """Return ``<astrom_root>/<status>/`` for one of STATUS_SUBDIRS.

    The result is *always* returned (no existence check); callers are
    expected to ``os.makedirs(..., exist_ok=True)`` if they need it.

    :param astrom_root: str, the top-level astrometrics directory (the
                        parent of ``verified``/``pending``/``rejected``)
    :param status: str, one of STATUS_SUBDIRS (or a STATUS_ALIASES key)
    :return: absolute path of the status sub-directory
    """
    canonical = STATUS_ALIASES.get(status, status)
    if canonical not in STATUS_SUBDIRS:
        emsg = ('Unknown astrometric status {0!r}; '
                'expected one of {1}')
        raise ValueError(emsg.format(status, STATUS_SUBDIRS))
    return os.path.abspath(os.path.join(astrom_root, canonical))


def find_yaml_in_status_dirs(
        astrom_root: str, apero_name: str,
) -> Optional[Tuple[str, str]]:
    """Locate the on-disk yaml for ``apero_name`` across status sub-dirs.

    Searches verified, pending, then rejected. Falls back to the
    legacy flat layout (``<astrom_root>/<APERO_NAME>.yaml``) so old
    archives keep working.

    :param astrom_root: str, the top-level astrometrics directory
    :param apero_name: str, the APERO_NAME of the entry
    :return: ``(yaml_path, status)`` tuple if found, else None
    """
    fname = _safe_filename(str(apero_name))
    for status in STATUS_SUBDIRS:
        path = os.path.join(astrom_root, status, fname)
        if os.path.isfile(path):
            return os.path.abspath(path), status
    # legacy flat-layout fallback
    legacy = os.path.join(astrom_root, fname)
    if os.path.isfile(legacy):
        return os.path.abspath(legacy), STATUS_VERIFIED
    return None


def validate_required_fields(
        entry: Dict[str, Any],
        required: Tuple[str, ...] = REQUIRED_FIELDS_STAR,
) -> List[str]:
    """Return the list of REQUIRED fields missing/null on ``entry``.

    PMRA/PMDE are not flagged as missing when ``entry[NO_PM_KEY]`` is
    truthy (the explicit "no proper-motion known" escape hatch).

    :param entry: dict, the yaml entry to validate
    :param required: tuple of required field names; defaults to
                     :data:`REQUIRED_FIELDS_STAR`
    :return: list of missing field names (empty if entry is complete)
    """
    if not isinstance(entry, dict):
        return list(required)
    no_pm = bool(entry.get(NO_PM_KEY))
    missing: List[str] = []
    for key in required:
        if no_pm and key in REQUIRED_FIELDS_PM:
            continue
        if key in (APERO_NAME_KEY, 'EPOCH'):
            value = entry.get(key)
        else:
            value = _nested_value(entry, key)
        if _is_null(value):
            missing.append(key)
    return missing


def load_all_entries(
        astrom_dir: str,
        use_cache: bool = True,
) -> List[Tuple[str, Dict[str, Any]]]:
    """Load every astrometric yaml entry from ``astrom_dir``.

    :param astrom_dir: str, directory containing ``*.yaml`` entries
    :param use_cache: bool, when True (default) re-use a per-process
                     cached copy if no yaml file has changed
    :return: list of ``(apero_name, entry_dict)`` tuples
    """
    sig = _dir_mtime_signature(astrom_dir)
    if use_cache:
        cached = _DIR_CACHE.get(astrom_dir)
        if cached is not None and cached[0] == sig:
            return cached[1]
    out: List[Tuple[str, Dict[str, Any]]] = []
    for fpath in iter_yaml_files(astrom_dir):
        try:
            entry = AstrometricDatabase._read_yaml(fpath)
        except Exception:
            # skip malformed yaml files rather than failing the whole load
            continue
        apero_name = entry.get(APERO_NAME_KEY)
        if not apero_name:
            # fall back to the filename stem if the file lacks APERO_NAME
            apero_name = os.path.splitext(os.path.basename(fpath))[0]
        out.append((str(apero_name), entry))
    if use_cache:
        _DIR_CACHE[astrom_dir] = (sig, out)
    return out


def _build_name_index(
        astrom_dir: str,
) -> Dict[str, str]:
    """Build a cleaned-name -> APERO_NAME map for ``astrom_dir``.

    Includes APERO_NAME, ORIGINAL_NAME, SIMBAD_NAME and every alias.
    Uses two cache tiers:
      1. an in-process cache (``_DIR_NAME_INDEX``)
      2. a JSON file on disk at ``<astrom_dir>/.name_index.json``
         keyed by the directory's mtime signature; this lets the index
         survive process restarts and skip parsing 1000+ yaml files.

    :param astrom_dir: str, directory containing astrometric yaml files
    :return: dict mapping cleaned name strings to canonical APERO_NAME
    """
    sig = _dir_mtime_signature(astrom_dir)
    cached = _DIR_NAME_INDEX.get(astrom_dir)
    if cached is not None and cached[0] == sig:
        return cached[1]
    # try disk cache
    disk = _load_persisted_name_index(astrom_dir, sig)
    if disk is not None:
        _DIR_NAME_INDEX[astrom_dir] = (sig, disk)
        return disk
    index: Dict[str, str] = {}

    def _index(value: Any, apero_name: str) -> None:
        for variant in name_search_variants(value):
            index.setdefault(variant, apero_name)

    for apero_name, entry in load_all_entries(astrom_dir):
        _index(apero_name, apero_name)
        for key in NAME_KEYS:
            if key == APERO_NAME_KEY:
                continue
            value = entry.get(key)
            if _is_null(value):
                continue
            _index(value, apero_name)
        aliases = entry.get(ALIAS_KEY)
        if isinstance(aliases, str):
            aliases = aliases.split('|')
        if isinstance(aliases, (list, tuple)):
            for alias in aliases:
                if _is_null(alias):
                    continue
                _index(alias, apero_name)
    _DIR_NAME_INDEX[astrom_dir] = (sig, index)
    _persist_name_index(astrom_dir, sig, index)
    return index


_NAME_INDEX_FILE = '.name_index.json'
# Bump when the indexing strategy changes so old on-disk caches are
# invalidated automatically (current: variant-based fuzzy index).
_NAME_INDEX_VERSION = 2

# Optional override: when the environment variable
# ``APERO_ASTROMETRICS_INDEX_DIR`` is set, the persisted
# cleaned-name index is written there (one JSON per astrom_dir,
# named by sha1 of the directory path) rather than inside the
# astrometrics yaml directory itself. This keeps the yaml
# directory pristine for upload/distribution. APERO RI sets this
# at startup so the default ``apero-assets/astrometrics`` folder
# stays clean.
_NAME_INDEX_DIR_ENV = 'APERO_ASTROMETRICS_INDEX_DIR'


def _name_index_path(astrom_dir: str) -> str:
    override = os.environ.get(_NAME_INDEX_DIR_ENV)
    if override:
        try:
            os.makedirs(override, exist_ok=True)
        except OSError:
            return os.path.join(astrom_dir, _NAME_INDEX_FILE)
        import hashlib
        digest = hashlib.sha1(
            os.path.abspath(astrom_dir).encode('utf-8')).hexdigest()
        return os.path.join(override, 'name_index_{0}.json'.format(digest))
    return os.path.join(astrom_dir, _NAME_INDEX_FILE)


def _load_persisted_name_index(
        astrom_dir: str,
        signature: float,
) -> Optional[Dict[str, str]]:
    """Return on-disk cleaned-name -> APERO_NAME map if signature matches.

    :param astrom_dir: str, directory containing astrometric yaml files
    :param signature: float, the current dir-mtime signature
    :return: dict if cache is fresh, otherwise ``None``
    """
    fpath = _name_index_path(astrom_dir)
    try:
        with open(fpath, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get('version') != _NAME_INDEX_VERSION:
        return None
    if data.get('signature') != signature:
        return None
    idx = data.get('index')
    if not isinstance(idx, dict):
        return None
    return {str(k): str(v) for k, v in idx.items()}


def _persist_name_index(
        astrom_dir: str,
        signature: float,
        index: Dict[str, str],
) -> None:
    """Write the cleaned-name index to disk atomically.

    Failures are silent: the in-process cache still works.
    """
    fpath = _name_index_path(astrom_dir)
    tmp = fpath + '.tmp'
    payload = {'version': _NAME_INDEX_VERSION,
               'signature': signature, 'count': len(index),
               'index': index}
    try:
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh)
        os.replace(tmp, fpath)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass


def find_by_name(
        astrom_dir: str,
        name: str,
) -> Optional[Dict[str, Any]]:
    """Look up an astrometric entry by name or alias.

    :param astrom_dir: str, directory containing astrometric yaml files
    :param name: str, the (possibly raw) object name to resolve
    :return: the matching entry dict, or None if no match was found
    """
    if not name:
        return None
    index = _build_name_index(astrom_dir)
    apero_name: Optional[str] = None
    for variant in name_search_variants(name):
        apero_name = index.get(variant)
        if apero_name is not None:
            break
    if apero_name is None:
        return None
    # fast path: the on-disk file follows _safe_filename(apero_name)
    fname = _safe_filename(apero_name)
    candidates = [os.path.join(astrom_dir, fname)]
    base = os.path.basename(os.path.normpath(astrom_dir)).lower()
    if base not in STATUS_SUBDIRS:
        for sub in STATUS_SUBDIRS:
            candidates.append(os.path.join(astrom_dir, sub, fname))
    for fpath in candidates:
        if os.path.isfile(fpath):
            try:
                return AstrometricDatabase._read_yaml(fpath)
            except Exception:  # noqa: BLE001
                pass
    # fallback: scan all entries (handles legacy filenames)
    for an, entry in load_all_entries(astrom_dir):
        if an == apero_name:
            return entry
    return None


def find_by_coords(
        astrom_dir: str,
        ra_deg: float,
        dec_deg: float,
        radius_arcsec: float,
        ra_key: str = 'RA',
        dec_key: str = 'DEC',
        max_results: int = 50,
) -> List[Tuple[Dict[str, Any], float]]:
    """Find every entry within ``radius_arcsec`` of (``ra_deg``, ``dec_deg``).

    Uses the ``RA`` / ``DEC`` blocks from each yaml entry (which carry
    a ``value`` sub-key per the schema). Results are sorted by ascending
    angular separation.

    :param astrom_dir: str, directory containing astrometric yaml files
    :param ra_deg: float, target right ascension in degrees
    :param dec_deg: float, target declination in degrees
    :param radius_arcsec: float, maximum angular separation to include
    :param ra_key: str, top-level yaml key to read RA from (default RA)
    :param dec_key: str, top-level yaml key to read DEC from (default DEC)
    :param max_results: int, hard cap on number of returned matches
    :return: list of ``(entry, separation_arcsec)`` tuples, ascending
    """
    matches: List[Tuple[Dict[str, Any], float]] = []
    for _apero_name, entry in load_all_entries(astrom_dir):
        ra_val = _nested_value(entry, ra_key)
        dec_val = _nested_value(entry, dec_key)
        ra_f = _pf(ra_val)
        dec_f = _pf(dec_val)
        if ra_f is None or dec_f is None:
            continue
        sep = _sep_arcsec(ra_deg, dec_deg, ra_f, dec_f)
        if sep <= radius_arcsec:
            matches.append((entry, sep))
    matches.sort(key=lambda pair: pair[1])
    return matches[:max_results]


def list_columns(astrom_dir: str) -> List[str]:
    """Return the union of top-level keys present across all yaml entries.

    Useful for populating an "advanced search" dropdown in a UI.

    :param astrom_dir: str, directory containing astrometric yaml files
    :return: alphabetically sorted list of unique key names
    """
    keys: set = set()
    for _apero_name, entry in load_all_entries(astrom_dir):
        if isinstance(entry, dict):
            keys.update(entry.keys())
    return sorted(keys)


def find_by_filter(
        astrom_dir: str,
        column: str,
        value: Any,
        match: str = 'auto',
        max_results: int = 200,
) -> List[Dict[str, Any]]:
    """Return every entry whose ``column`` matches ``value``.

    For numeric columns the comparison is exact-equality on the floated
    ``value`` sub-key. For string columns ``match='substring'`` (the
    default for non-numeric values) does a case-insensitive substring
    match; ``match='exact'`` requires equality after ``clean_object``.

    :param astrom_dir: str, directory containing astrometric yaml files
    :param column: str, top-level yaml key to filter on
    :param value: search value (string or numeric)
    :param match: str, ``'auto'``, ``'exact'``, ``'substring'``, or
                 ``'numeric'``; ``'auto'`` picks numeric for floats/ints
                 and substring for strings
    :param max_results: int, hard cap on number of returned matches
    :return: list of matching entry dicts
    """
    if match == 'auto':
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            match = 'numeric'
        else:
            try:
                float(str(value))
                match = 'numeric'
            except (TypeError, ValueError):
                match = 'substring'
    needle = None
    if match == 'numeric':
        try:
            needle = float(value)
        except (TypeError, ValueError):
            return []
    elif match == 'exact':
        needle = clean_object(str(value))
    else:  # substring
        needle = str(value).strip().lower()
        if not needle:
            return []
    out: List[Dict[str, Any]] = []
    for _apero_name, entry in load_all_entries(astrom_dir):
        if column not in entry:
            continue
        candidate = _nested_value(entry, column)
        if candidate is None:
            # also try the raw key (e.g. APERO_NAME stored as plain string)
            candidate = entry.get(column)
        if _is_null(candidate):
            continue
        if match == 'numeric':
            cf = _pf(candidate)
            if cf is None:
                continue
            if abs(cf - needle) <= max(abs(needle), 1.0) * 1e-9:
                out.append(entry)
        elif match == 'exact':
            if clean_object(str(candidate)) == needle:
                out.append(entry)
        else:  # substring
            if isinstance(candidate, (list, tuple)):
                hay = ' '.join(str(v) for v in candidate).lower()
            else:
                hay = str(candidate).lower()
            if needle in hay:
                out.append(entry)
        if len(out) >= max_results:
            break
    return out


# =============================================================================
# Provenance metadata + path-based write helpers
# -----------------------------------------------------------------------------
# These helpers let callers (apero-ri) edit / upload yaml entries directly
# without instantiating ``AstrometricDatabase``. They also stamp the five
# provenance keys (FIRST_UPDATED, FIRST_AUTHOR, LAST_EDIT, LAST_AUTHOR,
# STATUS) consistently for both writes via ``add_entry`` and direct edits.
# =============================================================================
def _today_iso() -> str:
    """Return today's UTC date as an ISO string (YYYY-MM-DD)."""
    try:
        return Time.now().iso.split(' ')[0]
    except Exception:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def _stamp_metadata(entry: Dict[str, Any],
                    author: Optional[str] = None) -> None:
    """Populate / refresh provenance metadata on ``entry`` in-place.

    - ``FIRST_UPDATED`` / ``FIRST_AUTHOR`` are only set if missing.
    - ``LAST_EDIT`` / ``LAST_AUTHOR`` are always refreshed.
    - ``STATUS`` defaults to ``'pending'`` only if missing or invalid.

    :param entry: dict, the yaml entry (modified in place)
    :param author: str or None, the author to record (defaults to
                   :data:`DEFAULT_AUTHOR`)
    :return: None
    """
    if not isinstance(entry, dict):
        return
    who = (str(author).strip()
           if author and str(author).strip() else DEFAULT_AUTHOR)
    today = _today_iso()
    # FIRST_* only set if missing / null
    if _is_null(entry.get(META_FIRST_UPDATED)):
        entry[META_FIRST_UPDATED] = today
    if _is_null(entry.get(META_FIRST_AUTHOR)):
        entry[META_FIRST_AUTHOR] = who
    # LAST_* always refreshed
    entry[META_LAST_EDIT] = today
    entry[META_LAST_AUTHOR] = who
    # STATUS default
    cur = entry.get(META_STATUS)
    if _is_null(cur) or str(cur).strip().lower() not in STATUS_VALUES:
        entry[META_STATUS] = DEFAULT_STATUS


def _set_nested(entry: Dict[str, Any], key: str, value: Any) -> None:
    """Set ``key`` on ``entry`` honouring the {value, source, units} schema.

    If the existing value at ``key`` is a dict containing a ``value``
    sub-key, only the ``value`` sub-key is replaced (preserving source /
    units). Otherwise the top-level key is set wholesale.

    :param entry: dict, the yaml entry (modified in place)
    :param key: str, top-level key to set
    :param value: any, the new value
    """
    cur = entry.get(key)
    if isinstance(cur, dict) and 'value' in cur:
        cur['value'] = value
        return
    entry[key] = value


def _invalidate_dir_caches(astrom_dir: str) -> None:
    """Drop every per-process cache for ``astrom_dir`` after a write."""
    _DIR_CACHE.pop(astrom_dir, None)
    _DIR_NAME_INDEX.pop(astrom_dir, None)
    _DIR_MTIME.pop(astrom_dir, None)
    _MTIME_CACHE.pop(astrom_dir, None)
    _RESOLVE_CACHE.clear()


def update_entry_field(
        astrom_dir: str,
        apero_name: str,
        key: str,
        value: Any,
        author: Optional[str] = None,
) -> Dict[str, Any]:
    """Update a single field on the entry identified by ``apero_name``.

    Honours the ``{value, source, units}`` schema: if the existing field
    is such a mapping, only the ``value`` sub-key is replaced.

    A change to ``APERO_NAME`` triggers a rename of the underlying yaml
    file (atomic ``os.replace`` after writing the new file). The five
    provenance keys are refreshed automatically.

    The lookup supports both layouts:
    - status sub-directories (``verified``/``pending``/``rejected``)
    - legacy flat files directly under ``astrom_dir``.

    :param astrom_dir: str, directory containing astrometric yaml files
    :param apero_name: str, the canonical APERO name of the entry to edit
    :param key: str, top-level yaml key to update
    :param value: any, the new value
    :param author: str or None, user making the edit (recorded in
                   ``LAST_AUTHOR``)
    :return: dict, the updated entry
    """
    if not apero_name:
        emsg = 'update_entry_field: apero_name is required'
        raise AperoCodedException(None, message=emsg)
    if not key:
        emsg = 'update_entry_field: key is required'
        raise AperoCodedException(None, message=emsg)
    fname = _safe_filename(str(apero_name))
    fpath = os.path.join(astrom_dir, fname)
    if not os.path.isfile(fpath):
        found = find_yaml_in_status_dirs(astrom_dir, apero_name)
        if found is not None:
            fpath = found[0]
    if not os.path.isfile(fpath):
        emsg = 'update_entry_field: no entry for {0!r} ({1})'
        raise AperoCodedException(
            None, message=emsg.format(apero_name, fpath))
    entry = AstrometricDatabase._read_yaml(fpath)
    # detect APERO_NAME rename
    rename_to: Optional[str] = None
    if key == APERO_NAME_KEY:
        cleaned = clean_object(str(value)) if value is not None else ''
        if cleaned in ('', 'Null'):
            emsg = 'update_entry_field: invalid new APERO_NAME {0!r}'
            raise AperoCodedException(
                None, message=emsg.format(value))
        if cleaned != clean_object(apero_name):
            rename_to = cleaned
    # apply the edit
    _set_nested(entry, key, value)
    # also keep raw APERO_NAME consistent on rename
    if rename_to is not None:
        entry[APERO_NAME_KEY] = rename_to
    # refresh provenance
    _stamp_metadata(entry, author=author)
    # write to (possibly new) target then remove old file on rename
    if rename_to is not None:
        new_fpath = os.path.join(
            os.path.dirname(fpath), rename_to + YAML_EXT)
        if os.path.isfile(new_fpath):
            emsg = ('update_entry_field: cannot rename {0} -> {1} '
                    '(target already exists)')
            raise AperoCodedException(
                None, message=emsg.format(apero_name, rename_to))
        AstrometricDatabase._write_yaml(new_fpath, entry)
        try:
            os.remove(fpath)
        except OSError:
            pass
    else:
        AstrometricDatabase._write_yaml(fpath, entry)
    _invalidate_dir_caches(astrom_dir)
    return entry


def upload_entry(
        astrom_dir: str,
        entry: Dict[str, Any],
        author: Optional[str] = None,
        overwrite: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """Write a freshly-uploaded yaml entry to disk under ``astrom_dir``.

    The entry must contain a valid ``APERO_NAME``. By default the call
    fails if a file already exists for that name (use ``overwrite=True``
    to replace).

    :param astrom_dir: str, directory containing astrometric yaml files
    :param entry: dict, the parsed yaml content to write
    :param author: str or None, the uploading user (defaults to
                   :data:`DEFAULT_AUTHOR`)
    :param overwrite: bool, if True allow replacing an existing entry
    :return: tuple of (yaml file path, stamped entry dict)
    """
    if not isinstance(entry, dict):
        emsg = 'upload_entry: expected dict, got {0}'
        raise AperoCodedException(
            None, message=emsg.format(type(entry).__name__))
    apero_name = entry.get(APERO_NAME_KEY)
    if _is_null(apero_name):
        emsg = 'upload_entry: entry missing required key {0!r}'
        raise AperoCodedException(
            None, message=emsg.format(APERO_NAME_KEY))
    fname = _safe_filename(str(apero_name))
    fpath = os.path.join(astrom_dir, fname)
    if os.path.isfile(fpath) and not overwrite:
        emsg = 'upload_entry: entry already exists for {0!r} ({1})'
        raise AperoCodedException(
            None, message=emsg.format(apero_name, fpath))
    os.makedirs(astrom_dir, exist_ok=True)
    _stamp_metadata(entry, author=author)
    AstrometricDatabase._write_yaml(fpath, entry)
    _invalidate_dir_caches(astrom_dir)
    return fpath, entry


def set_status(
        astrom_root: str,
        apero_name: str,
        new_status: str,
        author: Optional[str] = None,
) -> Tuple[str, str, Dict[str, Any]]:
    """Move an entry between status sub-directories and refresh metadata.

    Locates the entry across ``verified``/``pending``/``rejected`` (with
    a flat-layout fallback), rewrites it with ``STATUS=new_status`` and
    refreshed ``LAST_EDIT``/``LAST_AUTHOR``, atomically writes it under
    ``<astrom_root>/<new_status>/`` and removes the old file when the
    on-disk path changes. Per-process caches for both directories are
    invalidated.

    :param astrom_root: str, top-level astrometrics directory (parent
                        of ``verified``/``pending``/``rejected``)
    :param apero_name: str, canonical APERO_NAME of the entry
    :param new_status: str, one of ``STATUS_SUBDIRS`` (or a key of
                       ``STATUS_ALIASES``); the target sub-dir/STATUS
    :param author: str or None, the user driving the change (recorded
                   on ``LAST_AUTHOR``)
    :return: tuple of ``(new_yaml_path, old_status, stamped_entry)``
    """
    if not apero_name:
        emsg = 'set_status: apero_name is required'
        raise AperoCodedException(None, message=emsg)
    canonical = STATUS_ALIASES.get(new_status, new_status)
    if canonical not in STATUS_SUBDIRS:
        emsg = ('set_status: unknown status {0!r}; '
                'expected one of {1}')
        raise AperoCodedException(
            None, message=emsg.format(new_status, STATUS_SUBDIRS))
    found = find_yaml_in_status_dirs(astrom_root, apero_name)
    if found is None:
        emsg = 'set_status: no yaml found for {0!r} under {1}'
        raise AperoCodedException(
            None, message=emsg.format(apero_name, astrom_root))
    old_path, old_status = found
    entry = AstrometricDatabase._read_yaml(old_path)
    # apply new STATUS *before* stamping so _stamp_metadata accepts it
    entry[META_STATUS] = canonical
    _stamp_metadata(entry, author=author)
    # ensure STATUS survives _stamp_metadata's default-only logic
    entry[META_STATUS] = canonical
    target_dir = astrom_status_dir(astrom_root, canonical)
    fname = _safe_filename(str(apero_name))
    new_path = os.path.abspath(os.path.join(target_dir, fname))
    os.makedirs(target_dir, exist_ok=True)
    AstrometricDatabase._write_yaml(new_path, entry)
    if os.path.abspath(old_path) != new_path:
        try:
            os.remove(old_path)
        except OSError:
            pass
        _invalidate_dir_caches(os.path.dirname(old_path))
    _invalidate_dir_caches(target_dir)
    _invalidate_dir_caches(astrom_root)
    return new_path, old_status, entry


def backfill_metadata(
        astrom_dir: str,
        author: Optional[str] = None,
        dry_run: bool = False,
) -> Dict[str, int]:
    """Populate the five provenance keys on every yaml in ``astrom_dir``.

    Existing values for any of the five keys are preserved; only missing
    or invalid keys are written. Useful as a one-shot migration after
    introducing the metadata schema.

    :param astrom_dir: str, directory containing astrometric yaml files
    :param author: str or None, author to record on entries that need
                   FIRST_AUTHOR / LAST_AUTHOR backfilled (defaults to
                   :data:`DEFAULT_AUTHOR`)
    :param dry_run: bool, if True, do not write files; just count
    :return: dict with counts ``{'scanned', 'updated', 'unchanged'}``
    """
    counts = {'scanned': 0, 'updated': 0, 'unchanged': 0}
    if not os.path.isdir(astrom_dir):
        return counts
    who = (str(author).strip()
           if author and str(author).strip() else DEFAULT_AUTHOR)
    today = _today_iso()
    for fpath in iter_yaml_files(astrom_dir):
        counts['scanned'] += 1
        try:
            entry = AstrometricDatabase._read_yaml(fpath)
        except Exception:
            continue
        changed = False
        # FIRST_*: only fill if missing
        if _is_null(entry.get(META_FIRST_UPDATED)):
            entry[META_FIRST_UPDATED] = today
            changed = True
        if _is_null(entry.get(META_FIRST_AUTHOR)):
            entry[META_FIRST_AUTHOR] = who
            changed = True
        # LAST_*: only fill if missing (don't overwrite real edits)
        if _is_null(entry.get(META_LAST_EDIT)):
            entry[META_LAST_EDIT] = today
            changed = True
        if _is_null(entry.get(META_LAST_AUTHOR)):
            entry[META_LAST_AUTHOR] = who
            changed = True
        # STATUS: default to pending if missing/invalid
        cur = entry.get(META_STATUS)
        if (_is_null(cur)
                or str(cur).strip().lower() not in STATUS_VALUES):
            entry[META_STATUS] = DEFAULT_STATUS
            changed = True
        if changed:
            counts['updated'] += 1
            if not dry_run:
                AstrometricDatabase._write_yaml(fpath, entry)
        else:
            counts['unchanged'] += 1
    if not dry_run and counts['updated']:
        _invalidate_dir_caches(astrom_dir)
    return counts


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Tiny self-test that exercises the public API against a temporary
    # astrometrics directory. Useful for sanity-checking edits to this
    # module without needing a full apero environment.
    # ----------------------------------------------------------------------
    import shutil

    # build an isolated workspace under the system tmpdir
    _tmp_root = tempfile.mkdtemp(prefix='drs_astrom_selftest_')
    try:
        # fake the bits of params that we use
        _params = ParamDict()
        _params['PATH.ASSETS'] = _tmp_root
        # construct the database (directory does not exist yet)
        _db = AstrometricDatabase(_params, shortname='SELFTEST')
        # add a single entry
        _db.add_entry({
            'APERO_NAME': 'GL699',
            'ORIGINAL_NAME': "Barnard's Star",
            'SIMBAD_NAME': 'GJ 699',
            'ALIASES': ['Barnard', 'BD+04 3561a', 'HIP 87937'],
            'RA': {'value': 269.452, 'source': 'Gaia DR3', 'units': 'deg'},
            'DEC': {'value': 4.668, 'source': 'Gaia DR3', 'units': 'deg'},
            'TEFF': {'value': 3134.0, 'source': 'Gaia DR3', 'units': 'K'},
        })
        # add a list of entries
        _db.add_entries([
            {'APERO_NAME': '10LAC',
             'ORIGINAL_NAME': '* 10 Lac',
             'SIMBAD_NAME': '*  10 Lac',
             'ALIASES': ['HD 214680', 'HR 8622'],
             'TEFF': {'value': 35200.0, 'source': '2018A&A',
                      'units': 'K'}},
        ])
        # resolve via APERO_NAME
        print('GL699            ->', _db.find_objname('GL699'))
        # resolve via SIMBAD_NAME
        print("GJ 699           ->", _db.find_objname('GJ 699'))
        # resolve via ORIGINAL_NAME (whitespace tolerated)
        print("Barnard's Star   ->", _db.find_objname("Barnard's Star"))
        # resolve via alias
        print('HD 214680        ->', _db.find_objname('HD 214680'))
        # unknown
        print('UNKNOWN_TARGET   ->', _db.find_objname('UNKNOWN_TARGET'))
        # find_objnames batch
        print('batch ->', _db.find_objnames(
            ['GL699', 'HR 8622', 'BOGUS'], allow_empty=True))
        # get_entries with legacy column aliasing
        print('count ->', _db.count())
        print('all   ->', [e['APERO_NAME'] for e in _db.get_entries()])
        print('proj  ->',
              _db.get_entries(columns='OBJNAME, ALIASES'))
        print('TEFF  ->', _db.get_entries(columns='OBJNAME, TEFF'))
        # get_entry by alias (must resolve)
        print('get_entry HR 8622 APERO_NAME ->',
              _db.get_entry('HR 8622').get('APERO_NAME'))
        # update existing entry (merge)
        _db.add_entry({'APERO_NAME': 'GL699',
                       'RV': {'value': -110.5, 'source': 'test'}})
        print('updated GL699 RV ->',
              _db.get_entry('GL699').get('RV'))
    finally:
        # clean up
        shutil.rmtree(_tmp_root, ignore_errors=True)

# =============================================================================
# End of code
# =============================================================================
