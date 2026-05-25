#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Helpers for building Data Portal object-page statistics.

Provides low-level numeric helpers, JSON/YAML loaders, and the main
``build_object_page_stats`` builder used by the data-portal object
pages.  Also exposes lightweight public helpers for the object-plots
API endpoint.

Created on 2024-01-01

@author: cook
"""

from __future__ import annotations

import json
import math
import re
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import yaml
from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.object_funcs"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define private numeric / collection helpers
# =============================================================================
def _is_dict_row(row: Any) -> bool:
    """
    Return True when *row* is a dict.

    :param row: Any, the value to test

    :return: bool, True if row is a dict
    :rtype: bool
    """
    return isinstance(row, dict)


def _first_present(row: Dict[str, Any], keys: Sequence[str]) -> Any:
    """
    Return the first non-None, non-empty value found in *row* for any
    of *keys*.

    :param row: dict, mapping of column names to values
    :param keys: sequence of str, candidate keys in priority order

    :return: the first matching value, or None
    :rtype: Any
    """
    for key in keys:
        if key in row and row.get(key) not in (None, ""):
            return row.get(key)
    return None


def _safe_float(value: Any) -> Optional[float]:
    """
    Attempt to convert *value* to float, returning None on failure or
    when the result is NaN.

    :param value: Any, value to convert

    :return: float or None
    :rtype: float | None
    """
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(fval):
        return None
    return fval


def _percentile(sorted_values: Sequence[float], pct: float) -> Optional[float]:
    """
    Compute a percentile from a pre-sorted sequence of floats using
    linear interpolation.

    :param sorted_values: sequence of float, ascending-sorted values
    :param pct: float, percentile in range [0, 100]

    :return: float percentile value, or None when sequence is empty
    :rtype: float | None
    """
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    kpos = (len(sorted_values) - 1) * (pct / 100.0)
    kfloor = int(kpos)
    kceil = min(kfloor + 1, len(sorted_values) - 1)
    if kfloor == kceil:
        return float(sorted_values[kfloor])
    frac = kpos - kfloor
    return float(
        sorted_values[kfloor] * (1.0 - frac) + sorted_values[kceil] * frac
    )


def _nanmedian(values: Iterable[Any]) -> Optional[float]:
    """
    Compute the median of *values*, skipping NaN and non-numeric
    entries.

    :param values: iterable of Any, raw values

    :return: float median, or None when no valid values exist
    :rtype: float | None
    """
    vals = sorted(v for v in (_safe_float(x) for x in values) if v is not None)
    return _percentile(vals, 50)


def _mean(values: Iterable[Any]) -> Optional[float]:
    """
    Compute the arithmetic mean of *values*, skipping non-numeric
    entries.

    :param values: iterable of Any, raw values

    :return: float mean, or None when no valid values exist
    :rtype: float | None
    """
    vals = [v for v in (_safe_float(x) for x in values) if v is not None]
    if not vals:
        return None
    return float(sum(vals) / len(vals))


def _sum(values: Iterable[Any]) -> Optional[float]:
    """
    Compute the sum of *values*, skipping non-numeric entries.

    :param values: iterable of Any, raw values

    :return: float sum, or None when no valid values exist
    :rtype: float | None
    """
    vals = [v for v in (_safe_float(x) for x in values) if v is not None]
    if not vals:
        return None
    return float(sum(vals))


def _format_number(value: Optional[float], ndp: int = 3) -> Optional[str]:
    """
    Format a float to a fixed number of decimal places.

    :param value: float or None, value to format
    :param ndp: int, number of decimal places (default 3)

    :return: str formatted value, or None when value is None
    :rtype: str | None
    """
    if value is None:
        return None
    return f"{value:.{ndp}f}"


def _join_unique(values: Iterable[Any]) -> Optional[str]:
    """
    Join unique non-empty string representations of *values* with
    ', '.

    :param values: iterable of Any, raw values

    :return: comma-separated unique values, or None when none found
    :rtype: str | None
    """
    seen: set = set()
    ordered: List[str] = []
    for value in values:
        sval = str(value).strip() if value is not None else ""
        if not sval:
            continue
        skey = sval.lower()
        if skey in seen:
            continue
        seen.add(skey)
        ordered.append(sval)
    return ", ".join(ordered) if ordered else None


def _unique_list(values: Iterable[Any]) -> List[str]:
    """Return ordered unique non-empty string values as a list.

    Sibling of :func:`_join_unique` used when the renderer needs the
    raw list (so it can render chips with a filter for >5 entries).
    """
    seen: set = set()
    ordered: List[str] = []
    for value in values:
        sval = str(value).strip() if value is not None else ""
        if not sval or sval.lower() in ("none", "null"):
            continue
        skey = sval.lower()
        if skey in seen:
            continue
        seen.add(skey)
        ordered.append(sval)
    return ordered


def _min_time(rows: Iterable[Dict[str, Any]], key: str) -> Optional[str]:
    """
    Return the lexicographically smallest time string for *key* across
    *rows*.

    :param rows: iterable of row dicts
    :param key: str, column name carrying the time strings

    :return: str minimum time value, or None
    :rtype: str | None
    """
    vals = [str(r.get(key)) for r in rows if r.get(key)]
    return min(vals) if vals else None


def _max_time(rows: Iterable[Dict[str, Any]], key: str) -> Optional[str]:
    """
    Return the lexicographically largest time string for *key* across
    *rows*.

    :param rows: iterable of row dicts
    :param key: str, column name carrying the time strings

    :return: str maximum time value, or None
    :rtype: str | None
    """
    vals = [str(r.get(key)) for r in rows if r.get(key)]
    return max(vals) if vals else None


def _fmt_count(n_accessible: int, n_total: int) -> str:
    """
    Format an accessible/total count pair as 'accessible (total)'.

    :param n_accessible: int, number of accessible items
    :param n_total: int, total number of items

    :return: str formatted count string
    :rtype: str
    """
    return f"{n_accessible} ({n_total})"


def _qc_counts(rows: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count total, passed, and failed QC rows.

    :param rows: iterable of row dicts with 'PASSED_ALL_QC' int column

    :return: dict with keys 'total', 'passed', 'failed'
    :rtype: dict
    """
    rows_list = list(rows)
    total = len(rows_list)
    passed = sum(1 for r in rows_list if int(r.get("PASSED_ALL_QC") or 0) == 1)
    return {
        "total": total,
        "passed": passed,
        "failed": max(0, total - passed),
    }


# =============================================================================
# Define private file / profile loaders
# =============================================================================
def _load_json_rows(path: Path) -> List[Dict[str, Any]]:
    """
    Load a list of row dicts from a JSON file.

    :param path: Path, absolute file path

    :return: list of row dicts (empty list on any error or absence)
    :rtype: list
    """
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as rfile:
            payload = json.load(rfile) or {}
        rows = payload.get("rows") or []
    except Exception:
        return []
    return [row for row in rows if _is_dict_row(row)]


def _load_instrument_profile(
    instrument_profile_file: str,
) -> Dict[str, Any]:
    """
    Load an instrument profile YAML from the resources directory.

    :param instrument_profile_file: str, file name (not full path)

    :return: dict, parsed YAML content (empty dict on error)
    :rtype: dict
    """
    if not instrument_profile_file:
        return {}
    resources_dir = (
        Path(__file__).resolve().parents[1]
        / "resources"
        / "aprofile_instruments"
    )
    path = resources_dir / instrument_profile_file
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as rfile:
            data = yaml.safe_load(rfile) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


# =============================================================================
# Define private instrument-profile helpers
# =============================================================================
def _header_label(
    profile_data: Dict[str, Any], section: str, key: str, default: str
) -> str:
    """
    Resolve a display label from an instrument profile's sci-headers
    section.

    :param profile_data: dict, instrument profile data dict
    :param section: str, header sub-section name
    :param key: str, keyword key within section
    :param default: str, fallback label

    :return: str resolved label or default
    :rtype: str
    """
    headers: Dict[str, Any] = {}
    if isinstance(profile_data, dict):
        headers = profile_data.get(
            "sci-headers", profile_data.get("headers", {})
        )
    if not isinstance(headers, dict):
        return default
    sec = (
        headers.get(section, {})
        if isinstance(headers.get(section, {}), dict)
        else {}
    )
    item = sec.get(key, {}) if isinstance(sec.get(key, {}), dict) else {}
    label = str(item.get("label", "") or "").strip()
    return label or default


def _header_key(
    profile_data: Dict[str, Any], section: str, key: str, default: str
) -> str:
    """
    Return the FITS header keyword (not label) from an instrument
    profile's sci-headers section.

    :param profile_data: dict, instrument profile data dict
    :param section: str, header sub-section name
    :param key: str, keyword key within section
    :param default: str, fallback keyword

    :return: str resolved keyword or default
    :rtype: str
    """
    headers: Dict[str, Any] = {}
    if isinstance(profile_data, dict):
        headers = profile_data.get(
            "sci-headers", profile_data.get("headers", {})
        )
    if not isinstance(headers, dict):
        return default
    sec = (
        headers.get(section, {})
        if isinstance(headers.get(section, {}), dict)
        else {}
    )
    item = sec.get(key, {}) if isinstance(sec.get(key, {}), dict) else {}
    hkey = str(item.get("key", "") or "").strip()
    return hkey or default


# =============================================================================
# Define private LBL helpers
# =============================================================================
def _parse_lbl_rdb_flavor(filename: str) -> tuple[str, str]:
    """
    Extract (science, comparison) pair from an LBL RDB filename of the
    form ``lbl_{science}_{comparison}.rdb``.

    :param filename: str, LBL RDB file name (may include directory)

    :return: tuple (science, comparison) or ('', '') on no match
    :rtype: tuple[str, str]
    """
    fname = Path(filename).name
    m = re.match(r"^lbl_(.+)\.rdb$", fname, re.IGNORECASE)
    if not m:
        return "", ""
    inner = m.group(1)
    return inner, inner


def _resolve_lbl_path(
    path_lbl: str, obs_dir: str, filename: str
) -> Optional[Path]:
    """
    Resolve an LBL file path with basic path-traversal prevention.

    :param path_lbl: str, base LBL directory
    :param obs_dir: str, observation sub-directory (relative)
    :param filename: str, file name within obs_dir

    :return: Path if the resolved file exists, None otherwise
    :rtype: Path | None
    """
    if not path_lbl or not filename:
        return None
    base = Path(path_lbl).resolve()
    try:
        obs_part = Path(obs_dir.strip("/")) if obs_dir else Path("")
        candidate = (base / obs_part / filename).resolve()
        # raises ValueError on path traversal attempt
        candidate.relative_to(base)
        return candidate if candidate.is_file() else None
    except (ValueError, OSError):
        return None


def _compute_lbl_flavor_stats(
    rdb_path: Path,
    fits_path: Optional[Path],
    lbl_version_hdrkey: str,
) -> Dict[str, Any]:
    """
    Read an LBL_RDB ``.rdb`` file and its optional FITS companion and
    return summary statistics.

    Stats mirror those produced by ``ari_core.lbl_stats_table()``.

    :param rdb_path: Path, path to the ``.rdb`` table file
    :param fits_path: Path or None, optional companion FITS file
    :param lbl_version_hdrkey: str, FITS header key for LBL version

    :return: dict of statistical summaries (empty on read failure)
    :rtype: dict
    """
    try:
        from astropy.io import fits as _fits
        from astropy.table import Table
    except ImportError:
        return {}

    stats: Dict[str, Any] = {}
    # -------------------------------------------------------------------------
    # read the RDB table
    try:
        rdb_table = Table.read(str(rdb_path), format="ascii.rdb")
    except Exception:
        return {}

    def _col(name: str) -> list:
        if name in rdb_table.colnames:
            return list(rdb_table[name])
        return []

    vrad_raw = _col("vrad")
    svrad_raw = _col("svrad")
    rjd_raw = _col("rjd")
    reset_raw = _col("RESET_RV")

    vrad = [v for v in (_safe_float(x) for x in vrad_raw) if v is not None]
    svrad = [v for v in (_safe_float(x) for x in svrad_raw) if v is not None]
    rjd = [v for v in (_safe_float(x) for x in rjd_raw) if v is not None]
    reset_flags = [
        bool(int(x) if x not in (None, "", "None") else 0) for x in reset_raw
    ]

    n_measurements = len(vrad)
    stats["measurement_count"] = n_measurements
    if not vrad:
        return stats
    # -------------------------------------------------------------------------
    # RV uncertainty percentiles (svrad: 25, 50, 75)
    svrad_sorted = sorted(v for v in svrad if v is not None)
    p25_s = _percentile(svrad_sorted, 25)
    p50_s = _percentile(svrad_sorted, 50)
    p75_s = _percentile(svrad_sorted, 75)
    if p25_s is not None and p50_s is not None and p75_s is not None:
        stats["rv_uncertainty_percentiles"] = (
            f"{p25_s:.2f}, {p50_s:.2f}, {p75_s:.2f} m/s"
        )
    # -------------------------------------------------------------------------
    # RV absolute deviation percentiles (|vrad - median|: 25, 50, 75)
    vrad_sorted = sorted(vrad)
    median_v = _percentile(vrad_sorted, 50) or 0.0
    abs_dev = sorted(abs(v - median_v) for v in vrad)
    p25_d = _percentile(abs_dev, 25)
    p50_d = _percentile(abs_dev, 50)
    p75_d = _percentile(abs_dev, 75)
    if p25_d is not None and p50_d is not None and p75_d is not None:
        stats["rv_abs_dev_percentiles"] = (
            f"{p25_d:.2f}, {p50_d:.2f}, {p75_d:.2f} m/s"
        )
    # -------------------------------------------------------------------------
    # systemic velocity
    stats["systemic_velocity"] = f"{median_v:.2f} m/s"
    stats["systemic_velocity_ms"] = median_v
    # -------------------------------------------------------------------------
    # ylim (valid velocity domain): based on p10/p90 ±150%
    p10 = _percentile(vrad_sorted, 10)
    p90 = _percentile(vrad_sorted, 90)
    if p10 is not None and p90 is not None:
        diff = p90 - p10
        central = (p10 + p90) / 2.0
        ylim_lo = central - 1.5 * diff
        ylim_hi = central + 1.5 * diff
        stats["valid_velocity_domain"] = f"{ylim_lo:.2f} to {ylim_hi:.2f} m/s"
        stats["spurious_low_points"] = sum(1 for v in vrad if v < ylim_lo)
        stats["spurious_high_points"] = sum(1 for v in vrad if v > ylim_hi)
    else:
        stats["spurious_low_points"] = 0
        stats["spurious_high_points"] = 0
    # -------------------------------------------------------------------------
    # number of nights (unique floor(rjd))
    unique_nights = {int(math.floor(j)) for j in rjd}
    stats["n_nights"] = len(unique_nights)
    # -------------------------------------------------------------------------
    # RESET_RV count
    stats["n_reset_rv_points"] = sum(1 for f in reset_flags if f)
    # -------------------------------------------------------------------------
    # LBL version from companion FITS header
    if fits_path is not None:
        try:
            hdr = _fits.getheader(str(fits_path))
            hdrkey = lbl_version_hdrkey or "LBL_VERS"
            stats["lbl_version"] = (
                str(hdr.get(hdrkey, "") or "").strip() or None
            )
        except Exception:
            stats["lbl_version"] = None
    else:
        stats["lbl_version"] = None

    return stats


# =============================================================================
# Define public page builder
# =============================================================================
def build_object_page_stats(
    *,
    base_dir: Path,
    instrument: str,
    profile_id: str,
    obj_row: Dict[str, Any],
    objname: str,
    accessible_run_ids: set,
    instrument_profile_file: str = "",
    path_lbl: str = "",
) -> Dict[str, Any]:
    """
    Build object-page sections and labels from object, ftable, and
    htable data sources.

    :param base_dir: Path, ARI data directory root
    :param instrument: str, instrument name (e.g. 'SPIROU')
    :param profile_id: str, profile identifier string
    :param obj_row: dict, object-table row for this object
    :param objname: str, canonical object name
    :param accessible_run_ids: set, run IDs accessible to the user
    :param instrument_profile_file: str, optional instrument YAML name
    :param path_lbl: str, optional base LBL directory path

    :return: dict with keys 'target_info', 'spectrum', 'lbl', 'ccf',
             'time_series', 'debug', 'labels'
    :rtype: dict
    """
    # -------------------------------------------------------------------------
    # resolve directories
    profile_dir = base_dir / "tasks" / instrument / profile_id
    objects_dir = profile_dir / "objects"
    preset = _load_instrument_profile(instrument_profile_file)
    # -------------------------------------------------------------------------
    # build display label mappings from instrument profile
    labels = {
        "target_info": {
            "ob_names_in_headers": _header_label(
                preset, "pp", "PP_OBNAME", "OB Name(s) in headers"
            ),
            "pi_names_in_headers": _header_label(
                preset, "pp", "PP_PI_NAME", "PI name(s) in header"
            ),
        },
        "spectrum": {
            "pp_version": _header_label(
                preset, "pp", "PP_VERSION", "Version [pp]"
            ),
            "ext_version": _header_label(
                preset, "ext", "EXT_VERSION", "Version [ext]"
            ),
        },
        "ccf": {
            "ccf_version": _header_label(
                preset, "ccf", "CCF_VERSION", "Version [ccf]"
            ),
        },
        "time_series": {
            "snr_order_15": _header_label(
                preset, "ext", "EXT_Y", "SNR[Order 15]"
            ),
            "snr_order_60": _header_label(
                preset, "ext", "EXT_H", "SNR[Order 60]"
            ),
        },
    }
    # -------------------------------------------------------------------------
    # load ftable rows for each file kind
    fkind_map = {
        "raw": "raw",
        "pp": "pp",
        "ext": "ext",
        "tcorr": "tcorr",
        "ccf": "ccf",
        "lbl": "lbl",
        "lbl_rdb": "lbl_rdb",
    }
    ftable_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for fkind, stem in fkind_map.items():
        fpath = (
            objects_dir
            / f'ftable_{stem}_{obj_row.get("OBJNAME", objname)}.json'
        )
        all_rows = _load_json_rows(fpath)
        accessible_rows = [
            row
            for row in all_rows
            if str(row.get("KW_RUN_ID", "") or "") in accessible_run_ids
        ]
        ftable_data[fkind] = {
            "all": all_rows,
            "accessible": accessible_rows,
        }
    # -------------------------------------------------------------------------
    # load htable rows
    htable_path = objects_dir / f'htable_{obj_row.get("OBJNAME", objname)}.json'
    htable_rows = _load_json_rows(htable_path)

    accessible_ids = {
        str(row.get("IDENTIFIER", "") or "").strip()
        for fkind in fkind_map
        for row in ftable_data[fkind]["accessible"]
        if str(row.get("IDENTIFIER", "") or "").strip()
    }
    if accessible_ids:
        htable_rows_acc = [
            row
            for row in htable_rows
            if str(row.get("IDENTIFIER", "") or "").strip() in accessible_ids
        ]
    else:
        htable_rows_acc = list(htable_rows)

    htable_by_id = {
        str(row.get("IDENTIFIER", "") or "").strip(): row
        for row in htable_rows_acc
        if str(row.get("IDENTIFIER", "") or "").strip()
    }
    # -------------------------------------------------------------------------
    # convenience row lists
    raw_rows = ftable_data["raw"]["accessible"]
    pp_rows = ftable_data["pp"]["accessible"]
    ext_rows = ftable_data["ext"]["accessible"]
    tcorr_rows = ftable_data["tcorr"]["accessible"]
    ccf_rows = ftable_data["ccf"]["accessible"]
    lbl_rows = ftable_data["lbl"]["accessible"]

    raw_rows_all = ftable_data["raw"]["all"]
    pp_rows_all = ftable_data["pp"]["all"]
    ext_rows_all = ftable_data["ext"]["all"]
    tcorr_rows_all = ftable_data["tcorr"]["all"]
    ccf_rows_all = ftable_data["ccf"]["all"]
    lbl_rows_all = ftable_data["lbl"]["all"]
    # -------------------------------------------------------------------------
    # target information section
    target_info = {
        "object_name": obj_row.get("OBJNAME"),
        "ra_deg": _first_present(obj_row, ["RA [Deg]", "RA_DEG"]),
        "ra_source": _first_present(obj_row, ["RA source", "RA_SOURCE"]),
        "dec_deg": _first_present(obj_row, ["Dec [Deg]", "DEC_DEG"]),
        "dec_source": _first_present(obj_row, ["Dec source", "DEC_SOURCE"]),
        "finder_chart": None,
        "teff_k": _first_present(obj_row, ["Teff [K]", "TEFF"]),
        "teff_source": _first_present(obj_row, ["Teff source", "TEFF_SOURCE"]),
        "spectral_type": _first_present(obj_row, ["SpT", "SPECTRAL_TYPE"]),
        "spectral_type_source": _first_present(
            obj_row, ["SpT source", "SPT_SOURCE"]
        ),
        "pmra": _first_present(obj_row, ["PMRA [mas/yr]", "PMRA"]),
        "pmdec": _first_present(
            obj_row, ["PMDE [mas/yr]", "PMDEC [mas/yr]", "PMDEC"]
        ),
        "parallax": _first_present(obj_row, ["Plx [mas]", "PLX"]),
        "radial_velocity": _first_present(obj_row, ["RV [km/s]", "RV"]),
        "radial_velocity_source": _first_present(
            obj_row, ["RV source", "RV_SOURCE"]
        ),
        "aliases": _first_present(obj_row, ["ALIASES", "ALIASES_STR"]),
    }
    # -------------------------------------------------------------------------
    # header-derived lists (shared between target & spectrum tabs); kept as
    # plain Python lists so the renderer can chip+filter when len > 5.
    _hdr_object_names = _unique_list([
        obj_row.get("OBJNAME"),
        *[r.get("OBJNAME") for r in htable_rows_acc],
        *[r.get("PP_OBJECT") for r in htable_rows_acc],
        *[r.get("EXT_OBJECT") for r in htable_rows_acc],
    ])
    _hdr_ob_names = _unique_list(
        r.get("PP_OBNAME") for r in htable_rows_acc
    )
    _hdr_pi_names = _unique_list(
        r.get("PP_PI_NAME") for r in htable_rows_acc
    )
    _hdr_run_ids = _unique_list(
        r.get("PP_PROG_ID") for r in htable_rows_acc
    )
    # -------------------------------------------------------------------------
    # QC counts per file kind
    raw_stats = _qc_counts(raw_rows)
    pp_stats = _qc_counts(pp_rows)
    ext_stats = _qc_counts(ext_rows)
    tcorr_stats = _qc_counts(tcorr_rows)
    ccf_stats = _qc_counts(ccf_rows)
    lbl_stats = _qc_counts(lbl_rows)

    raw_stats_all = _qc_counts(raw_rows_all)
    pp_stats_all = _qc_counts(pp_rows_all)
    ext_stats_all = _qc_counts(ext_rows_all)
    tcorr_stats_all = _qc_counts(tcorr_rows_all)
    ccf_stats_all = _qc_counts(ccf_rows_all)
    lbl_stats_all = _qc_counts(lbl_rows_all)
    # -------------------------------------------------------------------------
    # spectrum information section
    spectrum_info = {
        "dprtypes": _first_present(obj_row, ["DPRTYPE", "ALL_DPRTYPES"]),
        "raw_total": _fmt_count(raw_stats["total"], raw_stats_all["total"]),
        "raw_rejected": _fmt_count(
            raw_stats["failed"], raw_stats_all["failed"]
        ),
        "raw_first_mid": _min_time(raw_rows, "MID_OBS_TIME"),
        "raw_last_mid": _max_time(raw_rows, "MID_OBS_TIME"),
        "pp_total": _fmt_count(pp_stats["total"], pp_stats_all["total"]),
        "pp_passed": _fmt_count(pp_stats["passed"], pp_stats_all["passed"]),
        "pp_failed": _fmt_count(pp_stats["failed"], pp_stats_all["failed"]),
        "pp_first_mid": _min_time(pp_rows, "MID_OBS_TIME"),
        "pp_last_mid": _max_time(pp_rows, "MID_OBS_TIME"),
        "pp_last_processed": _max_time(pp_rows, "LAST_MODIFIED"),
        "pp_version": _join_unique(
            r.get("PP_VERSION") for r in htable_rows_acc
        ),
        "ext_total": _fmt_count(ext_stats["total"], ext_stats_all["total"]),
        "ext_passed": _fmt_count(ext_stats["passed"], ext_stats_all["passed"]),
        "ext_failed": _fmt_count(ext_stats["failed"], ext_stats_all["failed"]),
        "ext_first_mid": _min_time(ext_rows, "MID_OBS_TIME"),
        "ext_last_mid": _max_time(ext_rows, "MID_OBS_TIME"),
        "ext_last_processed": _max_time(ext_rows, "LAST_MODIFIED"),
        "ext_version": _join_unique(
            r.get("EXT_VERSION") for r in htable_rows_acc
        ),
        "tcorr_total": _fmt_count(
            tcorr_stats["total"], tcorr_stats_all["total"]
        ),
        "tcorr_passed": _fmt_count(
            tcorr_stats["passed"], tcorr_stats_all["passed"]
        ),
        "tcorr_failed": _fmt_count(
            tcorr_stats["failed"], tcorr_stats_all["failed"]
        ),
        "tcorr_first_mid": _min_time(tcorr_rows, "MID_OBS_TIME"),
        "tcorr_last_mid": _max_time(tcorr_rows, "MID_OBS_TIME"),
        "tcorr_last_processed": _max_time(tcorr_rows, "LAST_MODIFIED"),
        "tcorr_version": _join_unique(
            r.get("TCORR_VERSION") for r in htable_rows_acc
        ),
        "median_snr_y": _format_number(
            _nanmedian(r.get("EXT_Y") for r in htable_rows_acc),
            ndp=2,
        ),
        "median_snr_h": _format_number(
            _nanmedian(r.get("EXT_H") for r in htable_rows_acc),
            ndp=2,
        ),
        # header-derived names: lists -> chip+filter UI when len > 5
        "object_names_in_headers": _hdr_object_names,
        "ob_names_in_headers": _hdr_ob_names,
        "pi_names_in_headers": _hdr_pi_names,
        "project_run_names_in_headers": _hdr_run_ids,
    }
    # -------------------------------------------------------------------------
    # LBL: build per-flavor stats from individual LBL_RDB files
    lbl_rdb_rows_acc = ftable_data["lbl_rdb"]["accessible"]
    lbl_rdb_rows_all = ftable_data["lbl_rdb"]["all"]

    lbl_vers_hdrkey = _header_key(preset, "lbl", "LBL_VERSION", "LBL_VERS")

    # group accessible lbl_rdb rows by filename
    lbl_rdb_by_file: Dict[str, Dict[str, Any]] = {}
    for row in lbl_rdb_rows_acc:
        fname = str(row.get("FILENAME", "") or "").strip()
        if fname:
            lbl_rdb_by_file[fname] = row

    lbl_flavors: List[Dict[str, Any]] = []
    _obj_up = (objname or '').upper()

    def _lbl_flavor_sort_key(item):
        # Self-flavor ({obj}_{obj}) first, then alphabetical
        _fname, _ = item
        fid, _ = _parse_lbl_rdb_flavor(_fname)
        is_self = bool(
            _obj_up
            and fid.upper() == _obj_up + '_' + _obj_up
        )
        return (0 if is_self else 1, _fname.lower())

    for fname, row in sorted(
        lbl_rdb_by_file.items(),
        key=_lbl_flavor_sort_key,
    ):
        flavor_id, _ = _parse_lbl_rdb_flavor(fname)
        obs_dir = str(row.get("OBS_DIR", "") or "").strip()

        rdb_full = _resolve_lbl_path(path_lbl, obs_dir, fname)
        fits_fname = Path(fname).stem + ".fits"
        fits_full = _resolve_lbl_path(path_lbl, obs_dir, fits_fname)

        fstats = (
            _compute_lbl_flavor_stats(rdb_full, fits_full, lbl_vers_hdrkey)
            if rdb_full is not None
            else {}
        )
        lbl_flavors.append(
            {
                "flavor_id": flavor_id or fname,
                "rdb_filename": fname,
                "measurement_count": fstats.get("measurement_count"),
                "n_nights": fstats.get("n_nights"),
                "n_reset_rv_points": fstats.get("n_reset_rv_points"),
                "systemic_velocity": fstats.get("systemic_velocity"),
                "rv_uncertainty_percentiles": fstats.get(
                    "rv_uncertainty_percentiles"
                ),
                "rv_abs_dev_percentiles": fstats.get("rv_abs_dev_percentiles"),
                "spurious_low_points": fstats.get("spurious_low_points"),
                "spurious_high_points": fstats.get("spurious_high_points"),
                "valid_velocity_domain": fstats.get("valid_velocity_domain"),
                "lbl_version": fstats.get("lbl_version"),
                "systemic_velocity_ms": fstats.get("systemic_velocity_ms"),
            }
        )

    # summary fields (prefer flavor data when available)
    if lbl_flavors:
        summary_measurement_count = str(
            sum(f["measurement_count"] or 0 for f in lbl_flavors)
        )
        summary_lbl_version = _join_unique(
            f.get("lbl_version") for f in lbl_flavors
        )
        summary_n_nights = max(
            (f["n_nights"] or 0 for f in lbl_flavors), default=0
        )
    else:
        summary_measurement_count = _fmt_count(
            lbl_stats["total"], lbl_stats_all["total"]
        )
        summary_lbl_version = _join_unique(
            r.get("LBL_VERSION") for r in htable_rows_acc
        )
        summary_n_nights = len(
            {str(r.get("OBS_DIR")) for r in lbl_rows if r.get("OBS_DIR")}
        )

    lbl_info = {
        "measurement_count": summary_measurement_count,
        "n_nights": summary_n_nights,
        "lbl_version": summary_lbl_version,
        "rv_uncertainty_percentiles": (
            lbl_flavors[0].get("rv_uncertainty_percentiles")
            if lbl_flavors
            else None
        ),
        "rv_abs_dev_percentiles": (
            lbl_flavors[0].get("rv_abs_dev_percentiles")
            if lbl_flavors
            else None
        ),
        "spurious_low_points": (
            lbl_flavors[0].get("spurious_low_points") if lbl_flavors else None
        ),
        "spurious_high_points": (
            lbl_flavors[0].get("spurious_high_points") if lbl_flavors else None
        ),
        "n_reset_rv_points": (
            lbl_flavors[0].get("n_reset_rv_points") if lbl_flavors else None
        ),
        "systemic_velocity": (
            lbl_flavors[0].get("systemic_velocity") if lbl_flavors else None
        ),
        # raw float systemic velocity in m/s for downstream use
        "vsys_ms": (
            lbl_flavors[0].get("systemic_velocity_ms") if lbl_flavors else None
        ),
        "valid_velocity_domain": (
            lbl_flavors[0].get("valid_velocity_domain") if lbl_flavors else None
        ),
        "flavors": lbl_flavors,
        "total_rdb_files": _fmt_count(
            len(lbl_rdb_rows_acc), len(lbl_rdb_rows_all)
        ),
    }
    # -------------------------------------------------------------------------
    # CCF information section
    ccf_info = {
        "mask_used": _join_unique(r.get("CCF_MASK") for r in htable_rows_acc),
        "systemic_velocity": _format_number(
            _nanmedian(r.get("CCF_DV") for r in htable_rows_acc),
            ndp=3,
        ),
        "fwhm": _format_number(
            _nanmedian(r.get("CCF_FWHM") for r in htable_rows_acc),
            ndp=3,
        ),
        "total_files": _fmt_count(ccf_stats["total"], ccf_stats_all["total"]),
        "passed_qc": _fmt_count(ccf_stats["passed"], ccf_stats_all["passed"]),
        "failed_qc": _fmt_count(ccf_stats["failed"], ccf_stats_all["failed"]),
        "first_mid": _min_time(ccf_rows, "MID_OBS_TIME"),
        "last_mid": _max_time(ccf_rows, "MID_OBS_TIME"),
        "last_processed": _max_time(ccf_rows, "LAST_MODIFIED"),
        "ccf_version": _join_unique(
            r.get("CCF_VERSION") for r in htable_rows_acc
        ),
    }
    # -------------------------------------------------------------------------
    # time-series table: one row per observation night
    nights: Dict[str, Dict[str, Any]] = {}
    for row in ext_rows_all:
        obs_dir = str(row.get("OBS_DIR") or "")
        if not obs_dir:
            continue
        entry = nights.setdefault(
            obs_dir,
            {
                "obs_dir": obs_dir,
                "ext_rows_all": [],
                "ext_rows": [],
                "tcorr_rows_all": [],
                "tcorr_rows": [],
            },
        )
        entry["ext_rows_all"].append(row)
        if str(row.get("KW_RUN_ID", "") or "") in accessible_run_ids:
            entry["ext_rows"].append(row)

    for row in tcorr_rows_all:
        obs_dir = str(row.get("OBS_DIR") or "")
        if not obs_dir:
            continue
        entry = nights.setdefault(
            obs_dir,
            {
                "obs_dir": obs_dir,
                "ext_rows_all": [],
                "ext_rows": [],
                "tcorr_rows_all": [],
                "tcorr_rows": [],
            },
        )
        entry["tcorr_rows_all"].append(row)
        if str(row.get("KW_RUN_ID", "") or "") in accessible_run_ids:
            entry["tcorr_rows"].append(row)

    time_series = []
    for nkey in sorted(nights.keys()):
        nentry = nights[nkey]
        ext_n_all = nentry["ext_rows_all"]
        ext_n = nentry["ext_rows"]
        tc_n_all = nentry["tcorr_rows_all"]
        tc_n = nentry["tcorr_rows"]
        all_n = ext_n + tc_n

        ids = {
            str(r.get("IDENTIFIER", "") or "").strip()
            for r in all_n
            if str(r.get("IDENTIFIER", "") or "").strip()
        }
        n_hrows = [htable_by_id[i] for i in ids if i in htable_by_id]

        dprtypes = sorted(
            {str(r.get("KW_DPRTYPE")) for r in all_n if r.get("KW_DPRTYPE")}
        )
        time_series.append(
            {
                "obs_dir": nkey,
                "first_obs_mid": _min_time(all_n, "MID_OBS_TIME"),
                "last_obs_mid": _max_time(all_n, "MID_OBS_TIME"),
                "num_ext": _fmt_count(len(ext_n), len(ext_n_all)),
                "num_tcorr": _fmt_count(len(tc_n), len(tc_n_all)),
                "seeing": _format_number(
                    _mean(r.get("EXT_SEEING") for r in n_hrows), ndp=2
                ),
                "airmass": _format_number(
                    _mean(r.get("EXT_AIRMASS") for r in n_hrows), ndp=3
                ),
                "mean_exptime": _format_number(
                    _mean(r.get("EXT_EXPTIME") for r in n_hrows), ndp=3
                ),
                "total_exptime": _format_number(
                    _sum(r.get("EXT_EXPTIME") for r in n_hrows), ndp=3
                ),
                "snr_order_15": _format_number(
                    _mean(r.get("EXT_Y") for r in n_hrows), ndp=2
                ),
                "snr_order_60": _format_number(
                    _mean(r.get("EXT_H") for r in n_hrows), ndp=2
                ),
                "dprtypes": (", ".join(dprtypes) if dprtypes else None),
                "ext_files_label": (
                    f"{_fmt_count(len(ext_n), len(ext_n_all))} [download]"
                ),
                "tcorr_files_label": (
                    f"{_fmt_count(len(tc_n), len(tc_n_all))} [download]"
                ),
                "request_ext_files": "Extracted 2D files",
                "request_tcorr_files": "Telluric corrected 2D files",
            }
        )
    # -------------------------------------------------------------------------
    # assemble and return the full page payload
    return {
        "target_info": target_info,
        "spectrum": spectrum_info,
        "lbl": lbl_info,
        "ccf": ccf_info,
        "time_series": time_series,
        "debug": {
            "status": "coming_soon",
            "message": "Coming soon",
        },
        "labels": labels,
    }


# =============================================================================
# Define public helpers for the object-plots API endpoint
# =============================================================================
def load_object_htable_rows(
    objects_dir: Path, objname: str
) -> List[Dict[str, Any]]:
    """
    Load and return htable rows for *objname* from *objects_dir*.

    :param objects_dir: Path, directory containing htable JSON files
    :param objname: str, canonical object name

    :return: list of htable row dicts (empty on error or absence)
    :rtype: list
    """
    return _load_json_rows(objects_dir / f"htable_{objname}.json")


def load_object_preset(
    instrument_profile_file: str,
) -> Dict[str, Any]:
    """
    Load and return the instrument profile preset dict.

    :param instrument_profile_file: str, file name (not full path)

    :return: dict, parsed profile data (empty dict on error)
    :rtype: dict
    """
    return _load_instrument_profile(instrument_profile_file)


def load_object_table_row(objects_dir: Path, objname: str) -> Dict[str, Any]:
    """
    Return the object_table row for *objname*.

    Looks for ``object_table.json`` one level above *objects_dir* (i.e.
    in the instrument profile task directory).

    :param objects_dir: Path, directory containing object JSON files
    :param objname: str, canonical object name

    :return: dict, the matching object row (empty dict on failure)
    :rtype: dict
    """
    try:
        obj_table_path = objects_dir.parent / "object_table.json"
        rows = _load_json_rows(obj_table_path)
        for row in rows:
            if row.get("OBJNAME") == objname:
                return row
    except Exception:
        pass
    return {}


def load_object_ftable_rows(
    objects_dir: Path, objname: str, fkind: str
) -> List[Dict[str, Any]]:
    """
    Load and return ftable rows for *objname* and file-kind *fkind*.

    Looks for ``ftable_{fkind}_{objname}.json`` in *objects_dir*.

    :param objects_dir: Path, directory containing ftable JSON files
    :param objname: str, canonical object name
    :param fkind: str, file-kind identifier (e.g. 'ext', 'ccf')

    :return: list of ftable row dicts (empty on error or absence)
    :rtype: list
    """
    return _load_json_rows(objects_dir / f"ftable_{fkind}_{objname}.json")


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================


def _is_dict_row(row: Any) -> bool:
    return isinstance(row, dict)


def _first_present(row: Dict[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in row and row.get(key) not in (None, ""):
            return row.get(key)
    return None


def _safe_float(value: Any) -> Optional[float]:
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(fval):
        return None
    return fval


def _percentile(sorted_values: Sequence[float], pct: float) -> Optional[float]:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    kpos = (len(sorted_values) - 1) * (pct / 100.0)
    kfloor = int(kpos)
    kceil = min(kfloor + 1, len(sorted_values) - 1)
    if kfloor == kceil:
        return float(sorted_values[kfloor])
    frac = kpos - kfloor
    return float(
        sorted_values[kfloor] * (1.0 - frac) + sorted_values[kceil] * frac
    )


def _nanmedian(values: Iterable[Any]) -> Optional[float]:
    vals = sorted(v for v in (_safe_float(x) for x in values) if v is not None)
    return _percentile(vals, 50)


def _mean(values: Iterable[Any]) -> Optional[float]:
    vals = [v for v in (_safe_float(x) for x in values) if v is not None]
    if not vals:
        return None
    return float(sum(vals) / len(vals))


def _sum(values: Iterable[Any]) -> Optional[float]:
    vals = [v for v in (_safe_float(x) for x in values) if v is not None]
    if not vals:
        return None
    return float(sum(vals))


def _format_number(value: Optional[float], ndp: int = 3) -> Optional[str]:
    if value is None:
        return None
    return f"{value:.{ndp}f}"


def _join_unique(values: Iterable[Any]) -> Optional[str]:
    seen = set()
    ordered = []
    for value in values:
        sval = str(value).strip() if value is not None else ""
        if not sval:
            continue
        skey = sval.lower()
        if skey in seen:
            continue
        seen.add(skey)
        ordered.append(sval)
    return ", ".join(ordered) if ordered else None


def _min_time(rows: Iterable[Dict[str, Any]], key: str) -> Optional[str]:
    vals = [str(r.get(key)) for r in rows if r.get(key)]
    return min(vals) if vals else None


def _max_time(rows: Iterable[Dict[str, Any]], key: str) -> Optional[str]:
    vals = [str(r.get(key)) for r in rows if r.get(key)]
    return max(vals) if vals else None


def _fmt_count(n_accessible: int, n_total: int) -> str:
    return f"{n_accessible} ({n_total})"


def _qc_counts(rows: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    rows_list = list(rows)
    total = len(rows_list)
    passed = sum(1 for r in rows_list if int(r.get("PASSED_ALL_QC") or 0) == 1)
    return {
        "total": total,
        "passed": passed,
        "failed": max(0, total - passed),
    }


# ---------------------------------------------------------------------------
# In-process read cache: avoids re-reading the same large JSON data files
# on every plot API request.  Files are only refreshed after
# _JSON_ROWS_TTL seconds, which is safe because the task runner updates
# them at most once per hour.  On SSHFS this eliminates repeated
# round-trips for hot objects.
# ---------------------------------------------------------------------------
_JSON_ROWS_TTL: float = 300.0  # seconds before a cached entry is refreshed
_json_rows_cache: Dict[str, Any] = (
    {}
)  # path_str -> {'expires': float, 'rows': list}
_json_rows_lock = threading.Lock()


def _load_json_rows(path: Path) -> List[Dict[str, Any]]:
    key = str(path)
    now = time.monotonic()
    # Check the cache first (under lock to avoid torn reads).
    with _json_rows_lock:
        entry = _json_rows_cache.get(key)
        if entry is not None and now < entry["expires"]:
            return entry["rows"]
    # Cache miss or expired — read from disk outside the lock so other
    # threads are not blocked during a potentially slow SSHFS read.
    if not path.exists():
        rows: List[Dict[str, Any]] = []
    else:
        try:
            with path.open("r", encoding="utf-8") as rfile:
                payload = json.load(rfile) or {}
            raw = payload.get("rows") or []
            rows = [r for r in raw if _is_dict_row(r)]
        except Exception:
            rows = []
    with _json_rows_lock:
        _json_rows_cache[key] = {"expires": now + _JSON_ROWS_TTL, "rows": rows}
    return rows


# Instrument profile YAMLs live inside the installed package atnd never
# change at runtime, so a plain dict cache (populated on first access) is
# sufficient — no TTL needed.
_instrument_profile_cache: Dict[str, Dict[str, Any]] = {}


def _load_instrument_profile(instrument_profile_file: str) -> Dict[str, Any]:
    if not instrument_profile_file:
        return {}
    # Return the already-loaded dict without touching the file system.
    cached = _instrument_profile_cache.get(instrument_profile_file)
    if cached is not None:
        return cached
    resources_dir = (
        Path(__file__).resolve().parents[1]
        / "resources"
        / "aprofile_instruments"
    )
    path = resources_dir / instrument_profile_file
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as rfile:
            data = yaml.safe_load(rfile) or {}
        if not isinstance(data, dict):
            return {}
        _instrument_profile_cache[instrument_profile_file] = data
        return data
    except Exception:
        return {}


def _header_label(
    profile_data: Dict[str, Any], section: str, key: str, default: str
) -> str:
    headers = {}
    if isinstance(profile_data, dict):
        headers = profile_data.get(
            "sci-headers", profile_data.get("headers", {})
        )
    if not isinstance(headers, dict):
        return default
    sec = (
        headers.get(section, {})
        if isinstance(headers.get(section, {}), dict)
        else {}
    )
    item = sec.get(key, {}) if isinstance(sec.get(key, {}), dict) else {}
    label = str(item.get("label", "") or "").strip()
    return label or default


def _header_key(
    profile_data: Dict[str, Any], section: str, key: str, default: str
) -> str:
    """Return the FITS header keyword (not label) from profile data."""
    headers = {}
    if isinstance(profile_data, dict):
        headers = profile_data.get(
            "sci-headers", profile_data.get("headers", {})
        )
    if not isinstance(headers, dict):
        return default
    sec = (
        headers.get(section, {})
        if isinstance(headers.get(section, {}), dict)
        else {}
    )
    item = sec.get(key, {}) if isinstance(sec.get(key, {}), dict) else {}
    hkey = str(item.get("key", "") or "").strip()
    return hkey or default


def _parse_lbl_rdb_flavor(filename: str) -> tuple[str, str]:
    """Extract (science, comparison) from 'lbl_{science}_{comparison}.rdb'.

    Returns ('', '') if the pattern does not match.
    """
    # Match the base filename only (strip any directory component)
    fname = Path(filename).name
    m = re.match(r"^lbl_(.+)\.rdb$", fname, re.IGNORECASE)
    if not m:
        return "", ""
    inner = m.group(1)  # everything between 'lbl_' and '.rdb'
    return inner, inner  # science_comparison pair; split further if needed


def _resolve_lbl_path(
    path_lbl: str, obs_dir: str, filename: str
) -> Optional[Path]:
    """Resolve an LBL file path with basic path-traversal prevention."""
    if not path_lbl or not filename:
        return None
    base = Path(path_lbl).resolve()
    try:
        obs_part = Path(obs_dir.strip("/")) if obs_dir else Path("")
        candidate = (base / obs_part / filename).resolve()
        candidate.relative_to(base)  # raises ValueError on traversal
        return candidate if candidate.is_file() else None
    except (ValueError, OSError):
        return None


def _compute_lbl_flavor_stats(
    rdb_path: Path, fits_path: Optional[Path], lbl_version_hdrkey: str
) -> Dict[str, Any]:
    """Read an LBL_RDB .rdb file and optional FITS companion for stats.

    Stats mirror those produced by ari_core.lbl_stats_table().
    """
    try:
        from astropy.io import fits as _fits
        from astropy.table import Table
    except ImportError:
        return {}

    stats: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Read the RDB table
    # ------------------------------------------------------------------
    try:
        rdb_table = Table.read(str(rdb_path), format="ascii.rdb")
    except Exception:
        return {}

    # pull required columns (guard or missing columns gracefully)
    def _col(name: str) -> list:
        if name in rdb_table.colnames:
            return list(rdb_table[name])
        return []

    vrad_raw = _col("vrad")
    svrad_raw = _col("svrad")
    rjd_raw = _col("rjd")
    reset_raw = _col("RESET_RV")

    vrad = [v for v in (_safe_float(x) for x in vrad_raw) if v is not None]
    svrad = [v for v in (_safe_float(x) for x in svrad_raw) if v is not None]
    rjd = [v for v in (_safe_float(x) for x in rjd_raw) if v is not None]
    reset_flags = [
        bool(int(x) if x not in (None, "", "None") else 0) for x in reset_raw
    ]

    n_measurements = len(vrad)
    stats["measurement_count"] = n_measurements

    if not vrad:
        return stats

    # ------------------------------------------------------------------
    # RV uncertainty percentiles (svrad: 25, 50, 75)
    # ------------------------------------------------------------------
    svrad_sorted = sorted(v for v in svrad if v is not None)
    p25_s = _percentile(svrad_sorted, 25)
    p50_s = _percentile(svrad_sorted, 50)
    p75_s = _percentile(svrad_sorted, 75)
    if p25_s is not None and p50_s is not None and p75_s is not None:
        stats["rv_uncertainty_percentiles"] = (
            f"{p25_s:.2f}, {p50_s:.2f}, {p75_s:.2f} m/s"
        )

    # ------------------------------------------------------------------
    # RV absolute deviation percentiles (|vrad - median|: 25, 50, 75)
    # ------------------------------------------------------------------
    vrad_sorted = sorted(vrad)
    median_v = _percentile(vrad_sorted, 50) or 0.0
    abs_dev = sorted(abs(v - median_v) for v in vrad)
    p25_d = _percentile(abs_dev, 25)
    p50_d = _percentile(abs_dev, 50)
    p75_d = _percentile(abs_dev, 75)
    if p25_d is not None and p50_d is not None and p75_d is not None:
        stats["rv_abs_dev_percentiles"] = (
            f"{p25_d:.2f}, {p50_d:.2f}, {p75_d:.2f} m/s"
        )

    # ------------------------------------------------------------------
    # Systemic velocity
    # ------------------------------------------------------------------
    stats["systemic_velocity"] = f"{median_v:.2f} m/s"
    stats["systemic_velocity_ms"] = median_v  # raw float for BERV plot

    # ------------------------------------------------------------------
    # ylim (valid velocity domain): based on p10/p90 ±150%
    # ------------------------------------------------------------------
    p10 = _percentile(vrad_sorted, 10)
    p90 = _percentile(vrad_sorted, 90)
    if p10 is not None and p90 is not None:
        diff = p90 - p10
        central = (p10 + p90) / 2.0
        ylim_lo = central - 1.5 * diff
        ylim_hi = central + 1.5 * diff
        stats["valid_velocity_domain"] = f"{ylim_lo:.2f} to {ylim_hi:.2f} m/s"
        # outliers outside the ylim window
        stats["spurious_low_points"] = sum(1 for v in vrad if v < ylim_lo)
        stats["spurious_high_points"] = sum(1 for v in vrad if v > ylim_hi)
    else:
        stats["spurious_low_points"] = 0
        stats["spurious_high_points"] = 0

    # ------------------------------------------------------------------
    # Number of nights (unique floor(rjd))
    # ------------------------------------------------------------------
    unique_nights = {int(math.floor(j)) for j in rjd}
    stats["n_nights"] = len(unique_nights)

    # ------------------------------------------------------------------
    # RESET_RV count
    # ------------------------------------------------------------------
    stats["n_reset_rv_points"] = sum(1 for f in reset_flags if f)

    # ------------------------------------------------------------------
    # LBL version from companion FITS header
    # ------------------------------------------------------------------
    if fits_path is not None:
        try:
            hdr = _fits.getheader(str(fits_path))
            hdrkey = lbl_version_hdrkey or "LBL_VERS"
            stats["lbl_version"] = (
                str(hdr.get(hdrkey, "") or "").strip() or None
            )
        except Exception:
            stats["lbl_version"] = None
    else:
        stats["lbl_version"] = None

    return stats


def build_object_page_stats(
    *,
    base_dir: Path,
    instrument: str,
    profile_id: str,
    obj_row: Dict[str, Any],
    objname: str,
    accessible_run_ids: set,
    instrument_profile_file: str = "",
    path_lbl: str = "",
) -> Dict[str, Any]:
    """Build object-page sections and labels from object data sources."""
    profile_dir = base_dir / "tasks" / instrument / profile_id
    objects_dir = profile_dir / "objects"

    preset = _load_instrument_profile(instrument_profile_file)

    labels = {
        "target_info": {
            "ob_names_in_headers": _header_label(
                preset, "pp", "PP_OBNAME", "OB Name(s) in headers"
            ),
            "pi_names_in_headers": _header_label(
                preset, "pp", "PP_PI_NAME", "PI name(s) in header"
            ),
        },
        "spectrum": {
            "pp_version": _header_label(
                preset, "pp", "PP_VERSION", "Version [pp]"
            ),
            "ext_version": _header_label(
                preset, "ext", "EXT_VERSION", "Version [ext]"
            ),
        },
        "ccf": {
            "ccf_version": _header_label(
                preset, "ccf", "CCF_VERSION", "Version [ccf]"
            ),
        },
        "time_series": {
            "snr_order_15": _header_label(
                preset, "ext", "EXT_Y", "SNR[Order 15]"
            ),
            "snr_order_60": _header_label(
                preset, "ext", "EXT_H", "SNR[Order 60]"
            ),
        },
    }

    fkind_map = {
        "raw": "raw",
        "pp": "pp",
        "ext": "ext",
        "tcorr": "tcorr",
        "ccf": "ccf",
        "lbl": "lbl",
        "lbl_rdb": "lbl_rdb",
    }
    ftable_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for fkind, stem in fkind_map.items():
        fpath = (
            objects_dir
            / f'ftable_{stem}_{obj_row.get("OBJNAME", objname)}.json'
        )
        all_rows = _load_json_rows(fpath)
        accessible_rows = [
            row
            for row in all_rows
            if str(row.get("KW_RUN_ID", "") or "") in accessible_run_ids
        ]
        ftable_data[fkind] = {
            "all": all_rows,
            "accessible": accessible_rows,
        }

    htable_path = objects_dir / f'htable_{obj_row.get("OBJNAME", objname)}.json'
    htable_rows = _load_json_rows(htable_path)

    accessible_ids = {
        str(row.get("IDENTIFIER", "") or "").strip()
        for fkind in fkind_map
        for row in ftable_data[fkind]["accessible"]
        if str(row.get("IDENTIFIER", "") or "").strip()
    }
    if accessible_ids:
        htable_rows_acc = [
            row
            for row in htable_rows
            if str(row.get("IDENTIFIER", "") or "").strip() in accessible_ids
        ]
    else:
        htable_rows_acc = list(htable_rows)

    htable_by_id = {
        str(row.get("IDENTIFIER", "") or "").strip(): row
        for row in htable_rows_acc
        if str(row.get("IDENTIFIER", "") or "").strip()
    }

    raw_rows = ftable_data["raw"]["accessible"]
    pp_rows = ftable_data["pp"]["accessible"]
    ext_rows = ftable_data["ext"]["accessible"]
    tcorr_rows = ftable_data["tcorr"]["accessible"]
    ccf_rows = ftable_data["ccf"]["accessible"]
    lbl_rows = ftable_data["lbl"]["accessible"]

    raw_rows_all = ftable_data["raw"]["all"]
    pp_rows_all = ftable_data["pp"]["all"]
    ext_rows_all = ftable_data["ext"]["all"]
    tcorr_rows_all = ftable_data["tcorr"]["all"]
    ccf_rows_all = ftable_data["ccf"]["all"]
    lbl_rows_all = ftable_data["lbl"]["all"]

    target_info = {
        "object_name": obj_row.get("OBJNAME"),
        "ra_deg": _first_present(obj_row, ["RA [Deg]", "RA_DEG"]),
        "ra_source": _first_present(obj_row, ["RA source", "RA_SOURCE"]),
        "dec_deg": _first_present(obj_row, ["Dec [Deg]", "DEC_DEG"]),
        "dec_source": _first_present(obj_row, ["Dec source", "DEC_SOURCE"]),
        "finder_chart": None,
        "teff_k": _first_present(obj_row, ["Teff [K]", "TEFF"]),
        "teff_source": _first_present(obj_row, ["Teff source", "TEFF_SOURCE"]),
        "spectral_type": _first_present(obj_row, ["SpT", "SPECTRAL_TYPE"]),
        "spectral_type_source": _first_present(
            obj_row, ["SpT source", "SPT_SOURCE"]
        ),
        "pmra": _first_present(obj_row, ["PMRA [mas/yr]", "PMRA"]),
        "pmdec": _first_present(
            obj_row, ["PMDE [mas/yr]", "PMDEC [mas/yr]", "PMDEC"]
        ),
        "parallax": _first_present(obj_row, ["Plx [mas]", "PLX"]),
        "radial_velocity": _first_present(obj_row, ["RV [km/s]", "RV"]),
        "radial_velocity_source": _first_present(
            obj_row, ["RV source", "RV_SOURCE"]
        ),
        "aliases": _first_present(obj_row, ["ALIASES", "ALIASES_STR"]),
    }
    # header-derived lists, kept as lists for chip+filter rendering
    _hdr_object_names = _unique_list([
        obj_row.get("OBJNAME"),
        *[r.get("OBJNAME") for r in htable_rows_acc],
        *[r.get("PP_OBJECT") for r in htable_rows_acc],
        *[r.get("EXT_OBJECT") for r in htable_rows_acc],
    ])
    _hdr_ob_names = _unique_list(
        r.get("PP_OBNAME") for r in htable_rows_acc
    )
    _hdr_pi_names = _unique_list(
        r.get("PP_PI_NAME") for r in htable_rows_acc
    )
    _hdr_run_ids = _unique_list(
        r.get("PP_PROG_ID") for r in htable_rows_acc
    )

    raw_stats = _qc_counts(raw_rows)
    pp_stats = _qc_counts(pp_rows)
    ext_stats = _qc_counts(ext_rows)
    tcorr_stats = _qc_counts(tcorr_rows)
    ccf_stats = _qc_counts(ccf_rows)
    lbl_stats = _qc_counts(lbl_rows)

    raw_stats_all = _qc_counts(raw_rows_all)
    pp_stats_all = _qc_counts(pp_rows_all)
    ext_stats_all = _qc_counts(ext_rows_all)
    tcorr_stats_all = _qc_counts(tcorr_rows_all)
    ccf_stats_all = _qc_counts(ccf_rows_all)
    lbl_stats_all = _qc_counts(lbl_rows_all)

    spectrum_info = {
        "dprtypes": _first_present(obj_row, ["DPRTYPE", "ALL_DPRTYPES"]),
        "raw_total": _fmt_count(raw_stats["total"], raw_stats_all["total"]),
        "raw_rejected": _fmt_count(
            raw_stats["failed"], raw_stats_all["failed"]
        ),
        "raw_first_mid": _min_time(raw_rows, "MID_OBS_TIME"),
        "raw_last_mid": _max_time(raw_rows, "MID_OBS_TIME"),
        "pp_total": _fmt_count(pp_stats["total"], pp_stats_all["total"]),
        "pp_passed": _fmt_count(pp_stats["passed"], pp_stats_all["passed"]),
        "pp_failed": _fmt_count(pp_stats["failed"], pp_stats_all["failed"]),
        "pp_first_mid": _min_time(pp_rows, "MID_OBS_TIME"),
        "pp_last_mid": _max_time(pp_rows, "MID_OBS_TIME"),
        "pp_last_processed": _max_time(pp_rows, "LAST_MODIFIED"),
        "pp_version": _join_unique(
            r.get("PP_VERSION") for r in htable_rows_acc
        ),
        "ext_total": _fmt_count(ext_stats["total"], ext_stats_all["total"]),
        "ext_passed": _fmt_count(ext_stats["passed"], ext_stats_all["passed"]),
        "ext_failed": _fmt_count(ext_stats["failed"], ext_stats_all["failed"]),
        "ext_first_mid": _min_time(ext_rows, "MID_OBS_TIME"),
        "ext_last_mid": _max_time(ext_rows, "MID_OBS_TIME"),
        "ext_last_processed": _max_time(ext_rows, "LAST_MODIFIED"),
        "ext_version": _join_unique(
            r.get("EXT_VERSION") for r in htable_rows_acc
        ),
        "tcorr_total": _fmt_count(
            tcorr_stats["total"], tcorr_stats_all["total"]
        ),
        "tcorr_passed": _fmt_count(
            tcorr_stats["passed"], tcorr_stats_all["passed"]
        ),
        "tcorr_failed": _fmt_count(
            tcorr_stats["failed"], tcorr_stats_all["failed"]
        ),
        "tcorr_first_mid": _min_time(tcorr_rows, "MID_OBS_TIME"),
        "tcorr_last_mid": _max_time(tcorr_rows, "MID_OBS_TIME"),
        "tcorr_last_processed": _max_time(tcorr_rows, "LAST_MODIFIED"),
        "tcorr_version": _join_unique(
            r.get("TCORR_VERSION") for r in htable_rows_acc
        ),
        "median_snr_y": _format_number(
            _nanmedian(r.get("EXT_Y") for r in htable_rows_acc), ndp=2
        ),
        "median_snr_h": _format_number(
            _nanmedian(r.get("EXT_H") for r in htable_rows_acc), ndp=2
        ),
        # header-derived names: lists -> chip+filter UI when len > 5
        "object_names_in_headers": _hdr_object_names,
        "ob_names_in_headers": _hdr_ob_names,
        "pi_names_in_headers": _hdr_pi_names,
        "project_run_names_in_headers": _hdr_run_ids,
    }

    # ------------------------------------------------------------------
    # LBL: build per-flavor stats from individual LBL_RDB files
    # ------------------------------------------------------------------
    lbl_rdb_rows_acc = ftable_data["lbl_rdb"]["accessible"]
    lbl_rdb_rows_all = ftable_data["lbl_rdb"]["all"]

    # LBL_VERSION header keyword from instrument profile
    lbl_vers_hdrkey = _header_key(preset, "lbl", "LBL_VERSION", "LBL_VERS")

    # Group accessible lbl_rdb rows by filename (latest row per file wins)
    lbl_rdb_by_file: Dict[str, Dict[str, Any]] = {}
    for row in lbl_rdb_rows_acc:
        fname = str(row.get("FILENAME", "") or "").strip()
        if fname:
            lbl_rdb_by_file[fname] = row

    lbl_flavors: List[Dict[str, Any]] = []
    _obj_up = (objname or '').upper()

    def _lbl_flavor_sort_key(item):
        # Self-flavor ({obj}_{obj}) first, then alphabetical
        _fname, _ = item
        fid, _ = _parse_lbl_rdb_flavor(_fname)
        is_self = bool(
            _obj_up
            and fid.upper() == _obj_up + '_' + _obj_up
        )
        return (0 if is_self else 1, _fname.lower())

    for fname, row in sorted(
        lbl_rdb_by_file.items(),
        key=_lbl_flavor_sort_key,
    ):
        flavor_id, _ = _parse_lbl_rdb_flavor(fname)
        obs_dir = str(row.get("OBS_DIR", "") or "").strip()

        # Resolve the .rdb file path
        rdb_full = _resolve_lbl_path(path_lbl, obs_dir, fname)

        # Derive companion .fits path (same stem, .fits extension)
        fits_fname = Path(fname).stem + ".fits"
        fits_full = _resolve_lbl_path(path_lbl, obs_dir, fits_fname)

        fstats = (
            _compute_lbl_flavor_stats(rdb_full, fits_full, lbl_vers_hdrkey)
            if rdb_full is not None
            else {}
        )

        lbl_flavors.append(
            {
                "flavor_id": flavor_id or fname,
                "rdb_filename": fname,
                "measurement_count": fstats.get("measurement_count"),
                "n_nights": fstats.get("n_nights"),
                "n_reset_rv_points": fstats.get("n_reset_rv_points"),
                "systemic_velocity": fstats.get("systemic_velocity"),
                "systemic_velocity_ms": fstats.get("systemic_velocity_ms"),
                "rv_uncertainty_percentiles": fstats.get(
                    "rv_uncertainty_percentiles"
                ),
                "rv_abs_dev_percentiles": fstats.get("rv_abs_dev_percentiles"),
                "spurious_low_points": fstats.get("spurious_low_points"),
                "spurious_high_points": fstats.get("spurious_high_points"),
                "valid_velocity_domain": fstats.get("valid_velocity_domain"),
                "lbl_version": fstats.get("lbl_version"),
            }
        )

    # Summary: prefer flavor data when available
    if lbl_flavors:
        summary_measurement_count = str(
            sum(f["measurement_count"] or 0 for f in lbl_flavors)
        )
        summary_lbl_version = _join_unique(
            f.get("lbl_version") for f in lbl_flavors
        )
        summary_n_nights = max(
            (f["n_nights"] or 0 for f in lbl_flavors), default=0
        )
    else:
        summary_measurement_count = _fmt_count(
            lbl_stats["total"], lbl_stats_all["total"]
        )
        summary_lbl_version = _join_unique(
            r.get("LBL_VERSION") for r in htable_rows_acc
        )
        summary_n_nights = len(
            {str(r.get("OBS_DIR")) for r in lbl_rows if r.get("OBS_DIR")}
        )

    lbl_info = {
        # Summary (backwards-compatible flat fields; populated from first
        # flavor)
        "measurement_count": summary_measurement_count,
        "n_nights": summary_n_nights,
        "lbl_version": summary_lbl_version,
        "rv_uncertainty_percentiles": (
            lbl_flavors[0].get("rv_uncertainty_percentiles")
            if lbl_flavors
            else None
        ),
        "rv_abs_dev_percentiles": (
            lbl_flavors[0].get("rv_abs_dev_percentiles")
            if lbl_flavors
            else None
        ),
        "spurious_low_points": (
            lbl_flavors[0].get("spurious_low_points") if lbl_flavors else None
        ),
        "spurious_high_points": (
            lbl_flavors[0].get("spurious_high_points") if lbl_flavors else None
        ),
        "n_reset_rv_points": (
            lbl_flavors[0].get("n_reset_rv_points") if lbl_flavors else None
        ),
        "systemic_velocity": (
            lbl_flavors[0].get("systemic_velocity") if lbl_flavors else None
        ),
        # Raw float systemic velocity in m/s for downstream use (e.g. BERV plot)
        "vsys_ms": (
            lbl_flavors[0].get("systemic_velocity_ms") if lbl_flavors else None
        ),
        "valid_velocity_domain": (
            lbl_flavors[0].get("valid_velocity_domain") if lbl_flavors else None
        ),
        # Per-flavor sub-sections
        "flavors": lbl_flavors,
        "total_rdb_files": _fmt_count(
            len(lbl_rdb_rows_acc), len(lbl_rdb_rows_all)
        ),
    }

    ccf_info = {
        "mask_used": _join_unique(r.get("CCF_MASK") for r in htable_rows_acc),
        "systemic_velocity": _format_number(
            _nanmedian(r.get("CCF_DV") for r in htable_rows_acc), ndp=3
        ),
        "fwhm": _format_number(
            _nanmedian(r.get("CCF_FWHM") for r in htable_rows_acc), ndp=3
        ),
        "total_files": _fmt_count(ccf_stats["total"], ccf_stats_all["total"]),
        "passed_qc": _fmt_count(ccf_stats["passed"], ccf_stats_all["passed"]),
        "failed_qc": _fmt_count(ccf_stats["failed"], ccf_stats_all["failed"]),
        "first_mid": _min_time(ccf_rows, "MID_OBS_TIME"),
        "last_mid": _max_time(ccf_rows, "MID_OBS_TIME"),
        "last_processed": _max_time(ccf_rows, "LAST_MODIFIED"),
        "ccf_version": _join_unique(
            r.get("CCF_VERSION") for r in htable_rows_acc
        ),
    }

    nights: Dict[str, Dict[str, Any]] = {}
    for row in ext_rows_all:
        obs_dir = str(row.get("OBS_DIR") or "")
        if not obs_dir:
            continue
        entry = nights.setdefault(
            obs_dir,
            {
                "obs_dir": obs_dir,
                "ext_rows_all": [],
                "ext_rows": [],
                "tcorr_rows_all": [],
                "tcorr_rows": [],
            },
        )
        entry["ext_rows_all"].append(row)
        if str(row.get("KW_RUN_ID", "") or "") in accessible_run_ids:
            entry["ext_rows"].append(row)

    for row in tcorr_rows_all:
        obs_dir = str(row.get("OBS_DIR") or "")
        if not obs_dir:
            continue
        entry = nights.setdefault(
            obs_dir,
            {
                "obs_dir": obs_dir,
                "ext_rows_all": [],
                "ext_rows": [],
                "tcorr_rows_all": [],
                "tcorr_rows": [],
            },
        )
        entry["tcorr_rows_all"].append(row)
        if str(row.get("KW_RUN_ID", "") or "") in accessible_run_ids:
            entry["tcorr_rows"].append(row)

    time_series = []
    for nkey in sorted(nights.keys()):
        nentry = nights[nkey]
        ext_n_all = nentry["ext_rows_all"]
        ext_n = nentry["ext_rows"]
        tc_n_all = nentry["tcorr_rows_all"]
        tc_n = nentry["tcorr_rows"]
        all_n = ext_n + tc_n

        ids = {
            str(r.get("IDENTIFIER", "") or "").strip()
            for r in all_n
            if str(r.get("IDENTIFIER", "") or "").strip()
        }
        n_hrows = [htable_by_id[i] for i in ids if i in htable_by_id]

        dprtypes = sorted(
            {str(r.get("KW_DPRTYPE")) for r in all_n if r.get("KW_DPRTYPE")}
        )

        time_series.append(
            {
                "obs_dir": nkey,
                "first_obs_mid": _min_time(all_n, "MID_OBS_TIME"),
                "last_obs_mid": _max_time(all_n, "MID_OBS_TIME"),
                "num_ext": _fmt_count(len(ext_n), len(ext_n_all)),
                "num_tcorr": _fmt_count(len(tc_n), len(tc_n_all)),
                "seeing": _format_number(
                    _mean(r.get("EXT_SEEING") for r in n_hrows), ndp=2
                ),
                "airmass": _format_number(
                    _mean(r.get("EXT_AIRMASS") for r in n_hrows), ndp=3
                ),
                "mean_exptime": _format_number(
                    _mean(r.get("EXT_EXPTIME") for r in n_hrows), ndp=3
                ),
                "total_exptime": _format_number(
                    _sum(r.get("EXT_EXPTIME") for r in n_hrows), ndp=3
                ),
                "snr_order_15": _format_number(
                    _mean(r.get("EXT_Y") for r in n_hrows), ndp=2
                ),
                "snr_order_60": _format_number(
                    _mean(r.get("EXT_H") for r in n_hrows), ndp=2
                ),
                "dprtypes": ", ".join(dprtypes) if dprtypes else None,
                "ext_files_label": (
                    f"{_fmt_count(len(ext_n), len(ext_n_all))} [download]"
                ),
                "tcorr_files_label": (
                    f"{_fmt_count(len(tc_n), len(tc_n_all))} [download]"
                ),
                "request_ext_files": "Extracted 2D files",
                "request_tcorr_files": "Telluric corrected 2D files",
            }
        )

    return {
        "target_info": target_info,
        "spectrum": spectrum_info,
        "lbl": lbl_info,
        "ccf": ccf_info,
        "time_series": time_series,
        "debug": {
            "status": "coming_soon",
            "message": "Coming soon",
        },
        "labels": labels,
    }


# ---------------------------------------------------------------------------
# Public helpers for the object-plots API endpoint
# ---------------------------------------------------------------------------


def load_object_htable_rows(
    objects_dir: Path, objname: str
) -> List[Dict[str, Any]]:
    """Load and return htable rows for *objname* from *objects_dir*.

    Returns an empty list when the file is absent or unreadable.
    """
    return _load_json_rows(objects_dir / f"htable_{objname}.json")


def load_object_preset(instrument_profile_file: str) -> Dict[str, Any]:
    """Load and return the instrument profile preset dict.

    Returns an empty dict when the file is absent or unreadable.
    """
    return _load_instrument_profile(instrument_profile_file)


def load_object_table_row(objects_dir: Path, objname: str) -> Dict[str, Any]:
    """Return the object_table row for *objname*.

    Looks for ``object_table.json`` one level above *objects_dir* (i.e., in
    the instrument profile task directory).  Returns an empty dict when the
    file is absent, the row is not found, or any error occurs.
    """
    try:
        obj_table_path = objects_dir.parent / "object_table.json"
        rows = _load_json_rows(obj_table_path)
        for row in rows:
            if row.get("OBJNAME") == objname:
                return row
    except Exception:
        pass
    return {}


def load_object_ftable_rows(
    objects_dir: Path, objname: str, fkind: str
) -> List[Dict[str, Any]]:
    """Load and return ftable rows for *objname* and file-kind *fkind*.

    Looks for ``ftable_{fkind}_{objname}.json`` in *objects_dir*.
    Returns an empty list when the file is absent or unreadable.
    """
    return _load_json_rows(objects_dir / f"ftable_{fkind}_{objname}.json")
