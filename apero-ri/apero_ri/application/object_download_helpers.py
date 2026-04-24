"""
Object-page plot data download helpers.

Provides a single endpoint :func:`api_object_download` that streams
the raw numerical data behind each of the eight object-page plots as
CSV (and LBL data as zip / tar.gz). The helpers reuse the same data
loaders and extractors as the plot builders to guarantee no drift
between the on-screen plot and the downloaded CSV.

Supported ``kind`` values (see :func:`api_object_download`):

- ``snr``         — SNR vs time (date, mjd, snr_h, snr_y)
- ``berv``        — BERV / vtot vs time (date, mjd, vtot, vsys, berv)
- ``spec``        — Median S1D spectrum (wavelength, ext_flux, tcorr_flux)
- ``ccf_rv``      — CCF radial velocity vs time (date, mjd, rv, err)
- ``ccf_profile`` — Median CCF profile (rv, median, +/-1σ, +/-2σ, fit, residual)
- ``ts_snr``      — Per-night SNR (date, mjd, snr_h, snr_y)
- ``ts_airmass``  — Per-night airmass (date, mjd, airmass)
- ``lbl``         — LBL files (rdb, rdb2, fits) bundled as zip or tar.gz
"""

import csv
import io
import re
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from flask import Response, jsonify, request

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
)
from apero_ri.core.object_funcs import (
    load_object_ftable_rows,
    load_object_htable_rows,
    load_object_preset,
    load_object_table_row,
)
from apero_ri.core.permissions import resolve_user_permissions


# =============================================================================
# Define helper utilities
# =============================================================================
def _safe_filename(name: str) -> str:
    """
    Convert an arbitrary string into a safe download filename token.

    :param name: str, raw text

    :return: str, filtered to [A-Za-z0-9._-]
    """
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(name or "").strip())
    return cleaned.strip("._-") or "object"


def _csv_response(rows: List[List[Any]], filename: str) -> Response:
    """
    Build a CSV download Flask response from a list of rows.

    :param rows: list of list, first row is header
    :param filename: str, suggested download filename

    :return: flask.Response
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    for row in rows:
        writer.writerow(row)
    body = buf.getvalue().encode("utf-8")
    resp = Response(body, mimetype="text/csv; charset=utf-8")
    resp.headers["Content-Disposition"] = (
        'attachment; filename="' + _safe_filename(filename) + '"'
    )
    resp.headers["Content-Length"] = str(len(body))
    return resp


def _fmt(val: Any) -> Any:
    """
    Format a numeric value for CSV (NaN → empty), pass through others.

    :param val: any

    :return: str or original value
    """
    try:
        f = float(val)
        if not np.isfinite(f):
            return ""
        return f
    except (TypeError, ValueError):
        return val if val is not None else ""


def _human_dt(dt: Optional[datetime]) -> str:
    """
    Render a datetime as ``YYYY-MM-DDTHH:MM:SS`` UTC, or empty.

    :param dt: datetime or None

    :return: str
    """
    if dt is None:
        return ""
    try:
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:  # noqa: BLE001
        return ""


# =============================================================================
# Define common request parsing
# =============================================================================
def _parse_common(app):
    """
    Parse common query parameters and authorize the request.

    :param app: ARIApp instance

    :return: tuple
        (err_response, profile, user_info, perms,
         objname, kind, fmt, vsys_ms,
         ccf_mjd_start, ccf_mjd_end, ccf_nobs)
        ``err_response`` is None on success, or a Flask response/tuple
        to short-circuit with on failure.
    """
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if "view.data_portal" not in perms:
        return (
            (jsonify(success=False, error="Unauthorized"), 401),
            None, None, None, "", "", "csv", None, None, None, 100,
        )

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    kind = request.args.get("kind", "").strip().lower()
    fmt = (request.args.get("format", "csv") or "csv").strip().lower()
    if not profile_id or not objname or not kind:
        return (
            (jsonify(success=False, error=(
                "Missing profile_id, objname or kind"
            )), 400),
            None, None, None, "", "", fmt, None, None, None, 100,
        )

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = next(
        (p for p in accessible if p["profile_id"] == profile_id), None
    )
    if not profile:
        return (
            (jsonify(success=False, error="Profile not found"), 404),
            None, None, None, "", "", fmt, None, None, None, 100,
        )

    def _maybe_float(name):
        sval = request.args.get(name, "").strip()
        if not sval:
            return None
        try:
            return float(sval)
        except ValueError:
            return None

    vsys_ms = _maybe_float("vsys_ms")
    ccf_mjd_start = _maybe_float("ccf_mjd_start")
    ccf_mjd_end = _maybe_float("ccf_mjd_end")
    ccf_nobs = 100
    nobs_str = request.args.get("ccf_nobs", "").strip()
    if nobs_str:
        try:
            ccf_nobs = max(1, min(1000, int(float(nobs_str))))
        except ValueError:
            ccf_nobs = 100
    if (
        ccf_mjd_start is not None
        and ccf_mjd_end is not None
        and ccf_mjd_start > ccf_mjd_end
    ):
        ccf_mjd_start, ccf_mjd_end = ccf_mjd_end, ccf_mjd_start

    return (
        None, profile, user_info, perms,
        objname, kind, fmt, vsys_ms,
        ccf_mjd_start, ccf_mjd_end, ccf_nobs,
    )


def _load_rows(app, profile, objname, kind):
    """
    Load and access-filter htable + the relevant ftable rows.

    :param app: ARIApp instance
    :param profile: profile dict from get_accessible_profiles
    :param objname: str, object name
    :param kind: str, download kind (selects which ftables to load)

    :return: tuple
        (htable_rows, ftable_ext_rows, ftable_tcorr_rows,
         ftable_ccf_rows, ftable_lbl_rows, paths, preset, profile_data)
    """
    instrument = profile["instrument"]
    profile_id = profile["profile_id"]
    profile_data = profile.get("data") or {}
    instrument_profile_file = str(
        profile_data.get("APERO_INSTRUMENT_PROFILE", "")
        or profile_data.get("apero_instrument_profile", "")
        or ""
    ).strip()

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    objects_dir = (
        base_dir / "tasks" / instrument / profile_id / "objects"
    )
    accessible_run_ids = app._get_user_accessible_run_ids(
        app._get_api_user(), instrument
    )

    htable_rows = load_object_htable_rows(objects_dir, objname)
    preset = load_object_preset(instrument_profile_file)

    need_ext = kind in {"snr", "berv", "spec", "ts_snr", "ts_airmass"}
    need_tcorr = kind in {"berv", "spec"}
    need_ccf = kind in {"ccf_rv", "ccf_profile"}
    need_lbl = kind == "lbl"

    ftable_ext_rows = (
        load_object_ftable_rows(objects_dir, objname, "ext")
        if need_ext else []
    )
    ftable_tcorr_rows = (
        load_object_ftable_rows(objects_dir, objname, "tcorr")
        if need_tcorr else []
    )
    ftable_ccf_rows = (
        load_object_ftable_rows(objects_dir, objname, "ccf")
        if need_ccf else []
    )
    ftable_lbl_rows = (
        load_object_ftable_rows(objects_dir, objname, "lbl_rdb")
        if need_lbl else []
    )

    htable_rows, ftables = app._filter_plot_rows(
        htable_rows,
        {
            "ext": ftable_ext_rows,
            "tcorr": ftable_tcorr_rows,
            "ccf": ftable_ccf_rows,
            "lbl_rdb": ftable_lbl_rows,
        },
        accessible_run_ids,
    )
    ftable_ext_rows = ftables["ext"]
    ftable_tcorr_rows = ftables["tcorr"]
    ftable_ccf_rows = ftables["ccf"]
    ftable_lbl_rows = ftables["lbl_rdb"]

    path_red = str(
        app._profile_get_path(profile_data, "PATH_RED", "") or ""
    )
    path_lbl = str(
        app._profile_get_path(profile_data, "PATH_LBL", "") or ""
    )
    paths = {"PATH_RED": path_red, "PATH_LBL": path_lbl}
    return (
        htable_rows, ftable_ext_rows, ftable_tcorr_rows,
        ftable_ccf_rows, ftable_lbl_rows, paths, preset, profile_data,
    )


# =============================================================================
# Define per-kind CSV builders
# =============================================================================
def _build_snr_csv(htable_rows: List[Dict[str, Any]], objname: str) -> Response:
    """
    Build CSV for SNR plot: date, mjd, snr_h, snr_y.

    :param htable_rows: list of htable dicts
    :param objname: str

    :return: flask.Response
    """
    from apero_ri.plots.plot_general import mjd_to_datetime

    rows: List[List[Any]] = [
        ["date_utc", "mjd", "snr_h", "snr_y"]
    ]
    pts: List[Tuple[float, datetime, Any, Any]] = []
    for row in htable_rows:
        if not isinstance(row, dict):
            continue
        mjd = row.get("EXT_MJDMID")
        try:
            mjd_f = float(mjd)
        except (TypeError, ValueError):
            continue
        dt = mjd_to_datetime(mjd_f)
        if dt is None:
            continue
        pts.append((mjd_f, dt, row.get("EXT_H"), row.get("EXT_Y")))
    pts.sort(key=lambda t: t[0])
    for mjd_f, dt, h_val, y_val in pts:
        rows.append([_human_dt(dt), mjd_f, _fmt(h_val), _fmt(y_val)])
    fname = _safe_filename(objname) + "_snr.csv"
    return _csv_response(rows, fname)


def _build_berv_csv(
    htable_rows: List[Dict[str, Any]],
    vsys_ms: Optional[float],
    objname: str,
) -> Response:
    """
    Build CSV for BERV plot: date, mjd, vtot, vsys, berv (all km/s).

    :param htable_rows: list of htable dicts
    :param vsys_ms: float or None, systemic velocity in m/s
    :param objname: str

    :return: flask.Response
    """
    from apero_ri.plots.plot_general import mjd_to_datetime

    vsys_kms = (
        (vsys_ms / 1000.0) if vsys_ms is not None else float("nan")
    )
    rows: List[List[Any]] = [[
        "date_utc", "mjd",
        "vtot_km_s", "vsys_km_s", "berv_km_s",
    ]]
    pts: List[Tuple[float, datetime, float]] = []
    for row in htable_rows:
        if not isinstance(row, dict):
            continue
        mjd = row.get("EXT_MJDMID")
        berv_raw = row.get("EXT_BERV")
        try:
            mjd_f = float(mjd)
            berv_kms = float(berv_raw)
        except (TypeError, ValueError):
            continue
        dt = mjd_to_datetime(mjd_f)
        if dt is None:
            continue
        pts.append((mjd_f, dt, berv_kms))
    pts.sort(key=lambda t: t[0])
    for mjd_f, dt, berv_kms in pts:
        if vsys_ms is not None:
            vtot = vsys_kms - berv_kms
        else:
            vtot = -berv_kms
        rows.append([
            _human_dt(dt), mjd_f,
            _fmt(vtot), _fmt(vsys_kms), _fmt(berv_kms),
        ])
    fname = _safe_filename(objname) + "_berv.csv"
    return _csv_response(rows, fname)


def _build_spec_csv(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    ftable_tcorr_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    objname: str,
) -> Response:
    """
    Build CSV for Median Spectrum plot: wavelength, ext_flux,
    tcorr_flux. The "median spectrum" is, like in the plot, the single
    S1D file whose EXT_H is closest to the median EXT_H across all
    htable rows.

    :param htable_rows: list of htable dicts
    :param ftable_ext_rows: list of ftable ext dicts
    :param ftable_tcorr_rows: list of ftable tcorr dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param objname: str

    :return: flask.Response
    """
    from apero_ri.plots.plot_obj_spectrum import (
        _derive_s1d_path,
        _derive_sc1d_path,
        _find_ftable_row_by_identifier,
        _find_median_ext_row,
        _load_s1d_data,
    )

    ext_row, best_ident = _find_median_ext_row(
        htable_rows, ftable_ext_rows
    )
    if ext_row is None:
        return jsonify(
            success=False,
            error="No matching EXT spectrum found.",
        ), 404
    s1d_path = _derive_s1d_path(ext_row, paths)
    if s1d_path is None:
        return jsonify(
            success=False,
            error="Extracted S1D file not found on disk.",
        ), 404
    wave, ext_flux = _load_s1d_data(s1d_path)
    if wave is None:
        return jsonify(
            success=False,
            error="Could not load extracted S1D data.",
        ), 500

    tcorr_flux: Optional[np.ndarray] = None
    if best_ident:
        tcorr_row = _find_ftable_row_by_identifier(
            ftable_tcorr_rows, best_ident
        )
        if tcorr_row is not None:
            sc1d_path = _derive_sc1d_path(tcorr_row, paths)
            if sc1d_path is not None:
                _, tcorr_flux = _load_s1d_data(sc1d_path)

    rows: List[List[Any]] = [["wavelength_nm", "ext_flux", "tcorr_flux"]]
    n = int(len(wave))
    has_tcorr = (
        tcorr_flux is not None and len(tcorr_flux) == n
    )
    for i in range(n):
        rows.append([
            _fmt(wave[i]),
            _fmt(ext_flux[i]),
            _fmt(tcorr_flux[i]) if has_tcorr else "",
        ])
    fname = _safe_filename(objname) + "_median_spectrum.csv"
    return _csv_response(rows, fname)


def _build_ccf_rv_csv(
    htable_rows: List[Dict[str, Any]],
    objname: str,
) -> Response:
    """
    Build CSV for CCF RV plot: date, mjd, rv (m/s), err (m/s).

    Mirrors the conversion done in
    :func:`apero_ri.plots.plot_obj_ccf._make_ccf_rv_figure`:
    ``CCF_DV`` is in km/s and converted to m/s; ``CCF_SDV`` is already
    in m/s.

    :param htable_rows: list of htable dicts
    :param objname: str

    :return: flask.Response
    """
    from apero_ri.plots.plot_general import mjd_to_datetime

    rows: List[List[Any]] = [[
        "date_utc", "mjd", "rv_m_s", "err_rv_m_s",
    ]]
    pts: List[Tuple[float, datetime, float, float]] = []
    for row in htable_rows:
        if not isinstance(row, dict):
            continue
        mjd = row.get("EXT_MJDMID")
        raw_dv = row.get("CCF_DV")
        raw_sdv = row.get("CCF_SDV")
        try:
            mjd_f = float(mjd)
            dv_ms = float(raw_dv) * 1000.0
            sdv_ms = float(raw_sdv)
        except (TypeError, ValueError):
            continue
        dt = mjd_to_datetime(mjd_f)
        if dt is None:
            continue
        pts.append((mjd_f, dt, dv_ms, sdv_ms))
    pts.sort(key=lambda t: t[0])
    for mjd_f, dt, dv_ms, sdv_ms in pts:
        rows.append([
            _human_dt(dt), mjd_f, _fmt(dv_ms), _fmt(sdv_ms),
        ])
    fname = _safe_filename(objname) + "_ccf_rv.csv"
    return _csv_response(rows, fname)


def _build_ccf_profile_csv(
    htable_rows: List[Dict[str, Any]],
    ftable_ccf_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    ccf_mjd_start: Optional[float],
    ccf_mjd_end: Optional[float],
    ccf_nobs: int,
    objname: str,
) -> Response:
    """
    Build CSV for the median CCF profile: rv (km/s), median_ccf,
    -1σ, +1σ, -2σ, +2σ, gaussian fit, residual.

    :param htable_rows: list of htable dicts
    :param ftable_ccf_rows: list of ftable ccf dicts
    :param paths: dict mapping PATH_* keys to directory strings
    :param ccf_mjd_start: float or None
    :param ccf_mjd_end: float or None
    :param ccf_nobs: int, max files to load
    :param objname: str

    :return: flask.Response
    """
    from apero_ri.plots.plot_obj_ccf import (
        _fit_ccf_gaussian,
        _load_ccf_data,
    )

    out = _load_ccf_data(
        ftable_ccf_rows,
        htable_rows,
        paths,
        ccf_mjd_start=ccf_mjd_start,
        ccf_mjd_end=ccf_mjd_end,
        max_files=int(ccf_nobs or 100),
    )
    if out is None:
        return jsonify(
            success=False,
            error="No CCF profile data could be loaded.",
        ), 404
    rv_vec, all_ccf, _datetimes, _dv_ms, _sdv_ms, _summary = out

    ccf_used = np.asarray(all_ccf, dtype=float)
    if ccf_used.size == 0 or rv_vec is None:
        return jsonify(
            success=False,
            error="CCF data array is empty.",
        ), 404
    # 1σ ≈ 68.27%, 2σ ≈ 95.45%
    lower1, upper1 = 15.865, 84.135
    lower2, upper2 = 2.275, 97.725
    y1_1sig = np.nanpercentile(ccf_used, lower1, axis=0)
    y2_1sig = np.nanpercentile(ccf_used, upper1, axis=0)
    y1_2sig = np.nanpercentile(ccf_used, lower2, axis=0)
    y2_2sig = np.nanpercentile(ccf_used, upper2, axis=0)
    med_ccf = np.nanmedian(ccf_used, axis=0)

    has_fit, fit_arr, _xlim = _fit_ccf_gaussian(
        np.asarray(rv_vec, dtype=float), med_ccf
    )
    fit_vec: np.ndarray
    if has_fit and fit_arr is not None and len(fit_arr) == len(med_ccf):
        fit_vec = np.asarray(fit_arr, dtype=float)
    else:
        fit_vec = np.full_like(med_ccf, np.nan)
    residual = med_ccf - fit_vec

    rows: List[List[Any]] = [[
        "rv_km_s", "median_ccf",
        "minus_1sigma", "plus_1sigma",
        "minus_2sigma", "plus_2sigma",
        "gaussian_fit", "residual",
    ]]
    n = len(rv_vec)
    for i in range(n):
        rows.append([
            _fmt(rv_vec[i]),
            _fmt(med_ccf[i]),
            _fmt(y1_1sig[i]),
            _fmt(y2_1sig[i]),
            _fmt(y1_2sig[i]),
            _fmt(y2_2sig[i]),
            _fmt(fit_vec[i]),
            _fmt(residual[i]),
        ])
    fname = _safe_filename(objname) + "_ccf_profile.csv"
    return _csv_response(rows, fname)


def _build_ts_csv(
    htable_rows: List[Dict[str, Any]],
    ftable_ext_rows: List[Dict[str, Any]],
    keys: List[str],
    objname: str,
    suffix: str,
    header_extras: List[str],
) -> Response:
    """
    Build a per-night time-series CSV: obs_dir, mjd_mean, then one
    column per *key* (averaged across that obs_dir).

    Uses the same IDENTIFIER → OBS_DIR mapping as
    :func:`apero_ri.plots.plot_obj_timeseries._aggregate_by_obs_dir`,
    extended with a per-night mean MJD so the user gets the date
    column they asked for.

    :param htable_rows: list of htable dicts
    :param ftable_ext_rows: list of ftable ext dicts
    :param keys: list of htable column names to average
    :param objname: str
    :param suffix: str, filename suffix (e.g. "snr", "airmass")
    :param header_extras: list of str header labels for each key

    :return: flask.Response
    """
    from apero_ri.plots.plot_general import mjd_to_datetime

    id_to_obs: Dict[str, str] = {}
    for row in ftable_ext_rows:
        ident = str(row.get("IDENTIFIER", "") or "").strip()
        obs = str(row.get("OBS_DIR", "") or "").strip()
        if ident and obs:
            id_to_obs[ident] = obs

    obs_keys: Dict[str, Dict[str, List[float]]] = {}
    obs_mjds: Dict[str, List[float]] = {}
    for row in htable_rows:
        ident = str(row.get("IDENTIFIER", "") or "").strip()
        obs = id_to_obs.get(ident)
        if not obs:
            continue
        bucket = obs_keys.setdefault(obs, {k: [] for k in keys})
        for k in keys:
            v = row.get(k)
            if v is not None:
                try:
                    bucket[k].append(float(v))
                except (TypeError, ValueError):
                    pass
        try:
            mjd_v = float(row.get("EXT_MJDMID"))
            obs_mjds.setdefault(obs, []).append(mjd_v)
        except (TypeError, ValueError):
            pass

    rows: List[List[Any]] = [
        ["obs_dir", "date_utc", "mjd_mean"] + list(header_extras)
    ]
    for obs in sorted(obs_keys.keys()):
        mjds = obs_mjds.get(obs, [])
        mjd_mean = float(np.nanmean(mjds)) if mjds else float("nan")
        dt = (
            mjd_to_datetime(mjd_mean)
            if np.isfinite(mjd_mean) else None
        )
        means = []
        for k in keys:
            vals = obs_keys[obs][k]
            means.append(
                _fmt(float(np.nanmean(vals))) if vals else ""
            )
        rows.append([
            obs, _human_dt(dt), _fmt(mjd_mean), *means,
        ])
    fname = _safe_filename(objname) + "_" + suffix + ".csv"
    return _csv_response(rows, fname)


# =============================================================================
# Define LBL bundle builder
# =============================================================================
def _collect_lbl_files(
    ftable_lbl_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
) -> List[Tuple[str, Path]]:
    """
    Resolve LBL rdb / rdb2 / fits files on disk.

    :param ftable_lbl_rows: list of ftable lbl_rdb dicts
    :param paths: dict mapping PATH_* keys

    :return: list of (arcname, abs_path) for files that exist
    """
    base = Path(paths.get("PATH_LBL", "") or "")
    out: List[Tuple[str, Path]] = []
    seen: set = set()
    if not str(base):
        return out
    for row in ftable_lbl_rows:
        obs_dir = str(row.get("OBS_DIR", "") or "").strip()
        filename = str(row.get("FILENAME", "") or "").strip()
        if not filename:
            continue
        obs_part = obs_dir.strip("/") if obs_dir else ""
        cand = (base / obs_part / filename).resolve() if obs_part \
            else (base / filename).resolve()
        if not cand.exists() or not cand.is_file():
            continue
        arcname = (
            obs_part + "/" + cand.name if obs_part else cand.name
        )
        if arcname in seen:
            continue
        seen.add(arcname)
        out.append((arcname, cand))
    return out


def _build_lbl_bundle(
    ftable_lbl_rows: List[Dict[str, Any]],
    paths: Dict[str, str],
    fmt: str,
    objname: str,
) -> Response:
    """
    Bundle all LBL rdb/rdb2/fits files for an object into zip or tar.gz.

    :param ftable_lbl_rows: list of ftable lbl_rdb dicts
    :param paths: dict mapping PATH_* keys
    :param fmt: str, "zip" or "tar" (anything else → zip)
    :param objname: str

    :return: flask.Response
    """
    files = _collect_lbl_files(ftable_lbl_rows, paths)
    if not files:
        return jsonify(
            success=False,
            error="No LBL files found on disk for this object.",
        ), 404

    safe_obj = _safe_filename(objname)
    buf = io.BytesIO()
    if fmt == "tar":
        with tarfile.open(fileobj=buf, mode="w:gz") as tf:
            for arcname, abs_path in files:
                tf.add(str(abs_path), arcname=safe_obj + "/" + arcname)
        body = buf.getvalue()
        resp = Response(body, mimetype="application/gzip")
        download_name = safe_obj + "_lbl.tar.gz"
    else:
        with zipfile.ZipFile(
            buf, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            for arcname, abs_path in files:
                zf.write(str(abs_path), arcname=safe_obj + "/" + arcname)
        body = buf.getvalue()
        resp = Response(body, mimetype="application/zip")
        download_name = safe_obj + "_lbl.zip"
    resp.headers["Content-Disposition"] = (
        'attachment; filename="' + download_name + '"'
    )
    resp.headers["Content-Length"] = str(len(body))
    return resp


# =============================================================================
# Define public entry point
# =============================================================================
def api_object_download(app):
    """
    Download the raw data behind an object-page plot.

    Query parameters:

    - ``profile_id`` (required)
    - ``objname``    (required)
    - ``kind``       (required) one of:
      ``snr``, ``berv``, ``spec``, ``ccf_rv``, ``ccf_profile``,
      ``ts_snr``, ``ts_airmass``, ``lbl``
    - ``format``     optional, only used for ``kind=lbl`` ("zip" or
      "tar"); defaults to "zip"
    - ``vsys_ms``    optional, used by ``kind=berv``
    - ``ccf_mjd_start`` / ``ccf_mjd_end`` / ``ccf_nobs``
      optional, used by ``kind=ccf_profile``

    :param app: ARIApp instance

    :return: flask.Response (CSV / zip / tar.gz) or JSON error
    """
    parsed = _parse_common(app)
    (
        err, profile, _user_info, _perms,
        objname, kind, fmt, vsys_ms,
        ccf_mjd_start, ccf_mjd_end, ccf_nobs,
    ) = parsed
    if err is not None:
        return err

    valid = {
        "snr", "berv", "spec", "ccf_rv", "ccf_profile",
        "ts_snr", "ts_airmass", "lbl",
    }
    if kind not in valid:
        return jsonify(
            success=False,
            error="Invalid kind. Use one of: " + ", ".join(sorted(valid)),
        ), 400

    (
        htable_rows, ftable_ext_rows, ftable_tcorr_rows,
        ftable_ccf_rows, ftable_lbl_rows,
        paths, _preset, _profile_data,
    ) = _load_rows(app, profile, objname, kind)

    try:
        if kind == "snr":
            return _build_snr_csv(htable_rows, objname)
        if kind == "berv":
            return _build_berv_csv(htable_rows, vsys_ms, objname)
        if kind == "spec":
            return _build_spec_csv(
                htable_rows, ftable_ext_rows, ftable_tcorr_rows,
                paths, objname,
            )
        if kind == "ccf_rv":
            return _build_ccf_rv_csv(htable_rows, objname)
        if kind == "ccf_profile":
            return _build_ccf_profile_csv(
                htable_rows, ftable_ccf_rows, paths,
                ccf_mjd_start, ccf_mjd_end, ccf_nobs, objname,
            )
        if kind == "ts_snr":
            return _build_ts_csv(
                htable_rows, ftable_ext_rows,
                ["EXT_H", "EXT_Y"], objname, "ts_snr",
                ["snr_h", "snr_y"],
            )
        if kind == "ts_airmass":
            return _build_ts_csv(
                htable_rows, ftable_ext_rows,
                ["EXT_AIRMASS"], objname, "ts_airmass",
                ["airmass"],
            )
        if kind == "lbl":
            return _build_lbl_bundle(
                ftable_lbl_rows, paths, fmt, objname,
            )
    except Exception as exc:  # noqa: BLE001
        try:
            app.logger.exception(
                "OBJECT_DOWNLOAD failed object=%s kind=%s err=%s",
                objname, kind, exc,
            )
        except Exception:  # noqa: BLE001
            pass
        return jsonify(
            success=False, error="Download failed: " + str(exc),
        ), 500
    # Should not reach here.
    return jsonify(success=False, error="Unhandled kind"), 400


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
