#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Astrometric-database helpers for the ARI API client.

Wraps the ``/api/astrometrics/*`` REST endpoints so callers can
access the APERO astrometric database, run SIMBAD lookups, and
file manual-object requests without writing raw ``requests`` calls.

Quick start::

    from apero_ri import ari_api
    from apero_ri.ari_api import astrometrics as astro

    ari_api.configure(server='https://ari.example.com',
                      token='<your-token>')

    entry = astro.resolve_by_name('GL699')
    # entry is a dict with keys 'apero_name', 'payload', 'raw', 'status'

    rows = astro.list_all()
    # rows is a list of summary dicts (APERO_NAME, STATUS, RA, DEC …)

    online = astro.resolve_online_by_name('Proxima Centauri')
    # returns the SIMBAD-resolved entry (not yet stored on the server)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from apero_ri.ari_api.client import _get, _post, _rows_to_fmt

# ---------------------------------------------------------------------------
# Local-database resolve helpers
# ---------------------------------------------------------------------------


def resolve_by_name(name: str) -> Dict[str, Any]:
    """Resolve a target from the APERO astrometric database by name.

    Searches the on-disk YAML database for *name* (exact APERO name
    or any registered alias).

    :param name: target identifier string
    :return: dict with keys ``apero_name``, ``payload``, ``raw``,
             ``status``, and ``success``
    :raises RuntimeError: when the server returns an error
    """
    if not name or not name.strip():
        raise ValueError("'name' must not be empty")
    return _get(
        "/api/astrometrics/resolve-by-name",
        params=dict(name=name.strip()),
    )


def resolve_by_coords(
    ra: float,
    dec: float,
    *,
    radius_arcsec: float = 60.0,
    max_results: int = 50,
) -> Dict[str, Any]:
    """Resolve targets within *radius_arcsec* of (*ra*, *dec*).

    :param ra: right ascension in degrees (ICRS)
    :param dec: declination in degrees (ICRS)
    :param radius_arcsec: search radius in arcsec (default 60)
    :param max_results: maximum number of results (default 50)
    :return: dict with keys ``success``, ``matches``
             (list of ``{apero_name, separation_arcsec, payload}``),
             ``ra``, ``dec``, ``radius_arcsec``
    :raises RuntimeError: when the server returns an error
    """
    return _get(
        "/api/astrometrics/resolve-by-coords",
        params=dict(
            ra=ra,
            dec=dec,
            radius=radius_arcsec,
            max=max_results,
        ),
    )


def resolve_by_filter(
    column: str,
    value: str,
    *,
    match: str = "auto",
    max_results: int = 200,
) -> Dict[str, Any]:
    """Filter astrometric entries by a column value.

    :param column: YAML key to filter on
    :param value: value to match
    :param match: matching strategy – one of ``exact``, ``substring``,
        ``glob``, ``regex``, ``ge``, ``le``, ``gt``, ``lt``, or
        ``auto`` (default)
    :param max_results: maximum number of results (default 200)
    :return: dict with keys ``success``, ``matches``
             (list of ``{apero_name, payload}``), ``column``,
             ``value``, ``match``
    :raises RuntimeError: when the server returns an error
    """
    return _get(
        "/api/astrometrics/resolve-by-filter",
        params=dict(
            column=column,
            value=value,
            match=match,
            max=max_results,
        ),
    )


def list_columns() -> List[str]:
    """Return the sorted union of YAML keys across all entries.

    :return: list of column-name strings
    :raises RuntimeError: when the server returns an error
    """
    data = _get("/api/astrometrics/columns")
    return data.get("columns") or []


# ---------------------------------------------------------------------------
# Full-database listing
# ---------------------------------------------------------------------------


def list_all(fmt: str = "dict") -> Any:
    """Return a summary row for every astrometric entry.

    :param fmt: output format – ``'dict'`` (default), ``'pandas'``, or
                ``'astropy'``
    :return: list of summary dicts (or DataFrame / Table), each with
             keys ``APERO_NAME``, ``APERO_CLASS``, ``RA``, ``DEC``,
             ``TEFF``, ``SPT``, ``STATUS``, ``KEYWORDS``, ``NOTES``
    :raises RuntimeError: when the server returns an error
    """
    data = _get("/api/astrometrics/list-all")
    rows = data.get("rows") or []
    return _rows_to_fmt(rows, None, fmt)


# ---------------------------------------------------------------------------
# Online (SIMBAD / Gaia / VizieR) resolve helpers
# ---------------------------------------------------------------------------


def resolve_online_by_name(name: str) -> Dict[str, Any]:
    """Resolve a target via SIMBAD/Gaia/VizieR by name.

    The resolved entry is *not* stored in the APERO database; it is
    placed in a time-limited transient store on the server so that
    follow-up SED / HR-diagram requests can reference it.

    :param name: target identifier (any SIMBAD-resolvable alias)
    :return: dict with keys ``success``, ``apero_name``, ``entry``
             (yaml-shaped dict or None), ``payload``, ``transient``
    :raises RuntimeError: when the server returns an error or
                          SIMBAD is unreachable
    """
    if not name or not name.strip():
        raise ValueError("'name' must not be empty")
    return _get(
        "/api/astrometrics/resolve-online-by-name",
        params=dict(name=name.strip()),
    )


def resolve_online_by_coords(
    ra: float,
    dec: float,
    *,
    radius_arcsec: float = 60.0,
) -> Dict[str, Any]:
    """SIMBAD cone-search by sky coordinates.

    :param ra: right ascension in degrees (ICRS)
    :param dec: declination in degrees (ICRS)
    :param radius_arcsec: search radius in arcsec (default 60)
    :return: dict with keys ``success``, ``matches``
             (list of ``{apero_name, entry, payload}``),
             ``transient``
    :raises RuntimeError: when the server returns an error or
                          SIMBAD is unreachable
    """
    return _get(
        "/api/astrometrics/resolve-online-by-coords",
        params=dict(ra=ra, dec=dec, radius=radius_arcsec),
    )


# ---------------------------------------------------------------------------
# Issue-filing helper
# ---------------------------------------------------------------------------


def request_manual_object(
    name: str,
    *,
    notes: str = "",
    origin_url: str = "",
) -> Dict[str, Any]:
    """File a *request.manual object* issue for *name*.

    Submits an issue with ``kind='astrometric'`` and
    ``type='request.manual object'`` so that a monitor can add the
    target to the APERO astrometric database.

    :param name: target name to request
    :param notes: optional free-text notes for the issue
    :param origin_url: URL of the page from which the request
                       originates (for back-links in the issue)
    :return: dict with keys ``ok``, ``issue_id`` (or ``error``)
    :raises RuntimeError: when the server returns an error
    """
    if not name or not name.strip():
        raise ValueError("'name' must not be empty")
    body: Dict[str, Any] = dict(
        kind="astrometric",
        type="request.manual object",
        title=f"Manual object request: {name.strip()}",
        apero_name=name.strip(),
        visibility="internal",
    )
    if notes:
        body["reason"] = notes.strip()
    if origin_url:
        body["origin_url"] = origin_url.strip()
    return _post("/api/issues/create", body=body)
