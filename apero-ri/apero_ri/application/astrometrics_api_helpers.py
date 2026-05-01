"""Astrometrics API helpers."""
import json as _json
import os
import re
from pathlib import Path

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
)
from apero_ri.core.permissions import resolve_user_permissions
from flask import jsonify, request


def api_astrometrics_find_object(app):
    """Find objects across accessible profiles by name, coordinates, or date."""
    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))

    # Authentication
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    # Get search parameters
    search_type = request.args.get("search_type", "").strip().lower()
    if not search_type:
        return jsonify(success=False, error="Missing search_type"), 400

    # Get accessible profiles
    accessible = get_accessible_profiles(user_info, app.ari_groups)
    if not accessible:
        return jsonify(success=True, results={}, profiles={})

    # Collect results and profile metadata for rendering profile cards.
    results = {}
    profiles = {}

    # Helper function to normalize names for matching
    def _norm_variants(value: str):
        text = str(value or "").strip().lower()
        if not text:
            return set()
        variants = {
            re.sub(r"[^a-z0-9]+", "", text),
            re.sub(r"[^a-z0-9]+", "", text.replace("+", "p").replace("-", "m")),
        }
        return {v for v in variants if v}

    # Helper function to get row RA/Dec in degrees
    def _row_ra_dec_deg(row):
        ra_keys = ("RA [Deg]", "RA", "OBJRA", "OBJ_RA")
        dec_keys = ("Dec [Deg]", "DEC", "Dec", "OBJDEC", "OBJ_DEC")
        ra_val = None
        dec_val = None
        for key in ra_keys:
            if key in row:
                try:
                    ra_val = float(row.get(key))
                    break
                except Exception:
                    continue
        for key in dec_keys:
            if key in row:
                try:
                    dec_val = float(row.get(key))
                    break
                except Exception:
                    continue
        if ra_val is None or dec_val is None:
            return None
        return ra_val, dec_val

    # Helper to parse coordinates
    def _parse_coord(value, is_ra=True):
        """Parse coordinate in deg or HH:MM:SS format."""
        value = str(value).strip()
        if ":" in value:
            # HH:MM:SS or DD:MM:SS format
            parts = value.split(":")
            if len(parts) != 3:
                return None
            try:
                h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
                deg = h + m / 60 + s / 3600
                if is_ra:
                    return deg * 15  # RA is in hours, convert to degrees
                return deg
            except Exception:
                return None
        else:
            # Decimal degrees
            try:
                return float(value)
            except Exception:
                return None

    # Process each profile's object table
    for profile in accessible:
        profile_id = profile["profile_id"]
        instrument = profile["instrument"]
        pdata = profile.get("data", {}) or {}
        profiles[profile_id] = {
            "profile_id": profile_id,
            "instrument": instrument,
            "apero_version": str(pdata.get("apero_version", "") or ""),
            "reduction_server": str(
                pdata.get("reduction_server", "") or ""
            ),
        }

        # Get accessible run IDs for this profile
        accessible_run_ids = app._get_user_accessible_run_ids(
            user_info, instrument
        )
        if not accessible_run_ids:
            continue

        # Load object table
        tasks_dir = base_dir / "tasks" / instrument
        json_path = tasks_dir / profile_id / "object_table.json"

        if not json_path.exists():
            legacy_path = tasks_dir / f"object_table_{profile_id}.json"
            if legacy_path.exists():
                json_path = legacy_path

        if not json_path.exists():
            continue

        try:
            with open(json_path, encoding="utf-8") as f:
                data = _json.load(f)
        except Exception:
            continue

        all_rows = data.get("rows", [])

        # Filter rows by accessible run IDs
        filtered = []
        for row in all_rows:
            raw = str(row.get("RUN_ID", "") or "")
            row_rids = {r.strip() for r in raw.split(",") if r.strip()}
            if row_rids & accessible_run_ids:
                row["Run ID"] = raw
                filtered.append(row)

        # Apply search filter
        matching_rows = []

        if search_type == "name":
            query = request.args.get("query", "").strip()
            if not query or len(query) < 1:
                continue

            qvars = _norm_variants(query)
            for row in filtered:
                names = [str(row.get("OBJNAME", "") or "")]
                aliases = str(row.get("ALIASES", "") or "")
                if aliases:
                    names.extend(
                        part.strip()
                        for part in aliases.split("|")
                        if part.strip()
                    )

                for name in names:
                    nvars = _norm_variants(name)
                    if any(qv in nv for qv in qvars for nv in nvars):
                        matching_rows.append(row)
                        break

        elif search_type == "coords":
            ra_str = request.args.get("ra", "").strip()
            dec_str = request.args.get("dec", "").strip()
            sep_str = request.args.get("separation", "").strip()
            coord_format = request.args.get(
                "coord_format", "deg"
            ).strip().lower()
            sep_unit = request.args.get(
                "separation_unit", "arcsec"
            ).strip().lower()

            if not ra_str or not dec_str or not sep_str:
                continue

            # Parse input coordinates
            ra = _parse_coord(ra_str, is_ra=True)
            dec = _parse_coord(dec_str, is_ra=False)
            if ra is None or dec is None:
                return (
                    jsonify(
                        success=False,
                        error="Invalid coordinate format",
                    ),
                    400,
                )

            try:
                sep = float(sep_str)
            except Exception:
                return jsonify(success=False, error="Invalid separation"), 400

            # Convert separation to degrees
            if sep_unit == "arcmin":
                sep_deg = sep / 60
            elif sep_unit == "deg":
                sep_deg = sep
            else:  # arcsec (default)
                sep_deg = sep / 3600

            # Find objects within separation
            for row in filtered:
                row_coords = _row_ra_dec_deg(row)
                if row_coords is None:
                    continue
                row_ra, row_dec = row_coords

                # Angular distance (simple approximation)
                dra = (row_ra - ra) * 3600  # in arcsec
                ddec = (row_dec - dec) * 3600  # in arcsec
                dist_arcsec = (dra**2 + ddec**2) ** 0.5
                dist_deg = dist_arcsec / 3600

                if dist_deg <= sep_deg:
                    matching_rows.append(row)

        elif search_type == "date":
            first_obs = request.args.get("first_observed", "").strip()
            last_obs = request.args.get("last_observed", "").strip()

            if not first_obs and not last_obs:
                continue

            date_keys = ("OBS_DATE", "DATE_OBS", "DATE-OBS")

            for row in filtered:
                row_date = None
                for key in date_keys:
                    if key in row:
                        row_date = str(row.get(key, "")).strip()
                        break

                if not row_date:
                    continue

                # Basic date comparison (YYYY-MM-DD format)
                if first_obs and row_date < first_obs:
                    continue
                if last_obs and row_date > last_obs:
                    continue

                matching_rows.append(row)

        elif search_type == "advanced":
            prop = request.args.get("property", "").strip()
            val = request.args.get("value", "").strip()

            if not prop or not val:
                continue

            for row in filtered:
                if prop not in row:
                    continue
                row_val = str(row.get(prop, "")).strip()
                # Simple string matching
                if val.lower() in row_val.lower():
                    matching_rows.append(row)

        # Format results
        if matching_rows:
            objects = []
            seen_names = set()
            for row in matching_rows:
                obj_name = str(row.get("OBJNAME", "") or "").strip()
                if not obj_name:
                    continue

                name_key = obj_name.lower()
                if name_key in seen_names:
                    continue
                seen_names.add(name_key)

                obj_record = {
                    "name": obj_name,
                    "aliases": [],
                    "ra": None,
                    "dec": None,
                }

                # Get aliases
                aliases = row.get("ALIASES", "")
                if aliases:
                    obj_record["aliases"] = [
                        a.strip() for a in aliases.split("|") if a.strip()
                    ]

                # Get coordinates
                coords = _row_ra_dec_deg(row)
                if coords:
                    obj_record["ra"], obj_record["dec"] = coords

                objects.append(obj_record)

            if objects:
                results[profile_id] = objects

    return jsonify(success=True, results=results, profiles=profiles)


# =============================================================================
# Astrometric-database resolve helpers
# =============================================================================
# These endpoints serve the "Resolve Target" tab on the astrometrics page
# and the shared target-info component used by the data-portal object
# page.  They read directly from the apero astrometric YAML database
# under ``<data_dir>/apero-assets/astrometrics``.


def _astrom_dir(app) -> Path:
    """Return the on-disk path to the astrometric YAML database.

    :param app: the ARI application object
    :return: pathlib.Path to ``<data_dir>/apero-assets/astrometrics``
    """
    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    return base_dir / "apero-assets" / "astrometrics"


def _entry_status_from_path(
        dra,
        astrom_root: str,
        yaml_path: str,
        entry,
        apero_name: str,
):
    """Infer entry status from path, then yaml STATUS, then lookup.

    :param dra: imported ``drs_astrometrics`` module
    :param astrom_root: str, root astrometrics directory
    :param yaml_path: str, full path to the yaml file
    :param entry: dict, parsed yaml entry
    :param apero_name: str, canonical APERO name for fallback lookup
    :return: lower-case status string
    """
    parent = Path(yaml_path).parent.name.lower()
    if parent in dra.STATUS_SUBDIRS:
        return parent
    raw_status = None
    if isinstance(entry, dict):
        raw_status = entry.get('STATUS')
    if raw_status:
        status = str(raw_status).strip().lower()
        if status in dra.STATUS_SUBDIRS:
            return status
    try:
        found = dra.find_yaml_in_status_dirs(astrom_root, apero_name)
        if found is not None and found[1] in dra.STATUS_SUBDIRS:
            return found[1]
    except Exception:  # noqa: BLE001
        pass
    # Legacy flat-layout files are treated as verified.
    return dra.STATUS_VERIFIED


def _check_view_perm(app):
    """Check that the caller has ``view.data_portal`` permission.

    :param app: the ARI application object
    :return: tuple ``(user_info, error_response)``; the error_response
             is ``None`` when the caller is authorised, otherwise it is
             a Flask response tuple ready to be returned by the caller.
    """
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if "view.data_portal" not in perms:
        return user_info, (
            jsonify(success=False, error="Unauthorized"), 401
        )
    return user_info, None


def _build_payload(entry):
    """Build the shared target-info payload for an astrometric entry.

    Imported lazily to keep the top-level import graph small.

    :param entry: dict, the loaded astrometric YAML entry, or None
    :return: dict ``{sections: [...]}``
    """
    from apero_ri.components.target_info_sections import (
        build_target_info_payload,
    )
    if not entry:
        return {"sections": []}
    return build_target_info_payload(entry)


def api_astrometrics_resolve_by_name(app):
    """Resolve a single target by APERO/SIMBAD name or alias.

    Query string parameters:
        name (required) - the search string

    :param app: the ARI application object
    :return: Flask JSON response with keys ``success``, ``apero_name``,
             ``payload`` (the shared target-info payload), and
             ``raw`` (the full YAML entry as a dict).  When no match is
             found, ``success`` is True and ``apero_name`` is None.
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
    if err is not None:
        return err

    name = (request.args.get("name") or "").strip()
    if not name:
        return jsonify(success=False, error="Missing 'name'"), 400

    try:
        entry = dra.find_by_name(str(_astrom_dir(app)), name)
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    if not entry:
        return jsonify(success=True, apero_name=None,
                       payload={"sections": []}, raw=None,
                       status=None)

    # status: prefer the entry's own STATUS, else infer from the
    # on-disk sub-dir via find_yaml_in_status_dirs (legacy entries).
    status = None
    raw_status = entry.get("STATUS")
    if raw_status:
        status = str(raw_status).strip().lower() or None
    if status is None:
        try:
            found = dra.find_yaml_in_status_dirs(
                str(_astrom_dir(app)),
                entry.get("APERO_NAME") or name,
            )
            if found is not None:
                status = found[1]
        except Exception:  # noqa: BLE001
            status = None

    return jsonify(
        success=True,
        apero_name=entry.get("APERO_NAME"),
        payload=_build_payload(entry),
        entry=entry,
        raw=entry,
        status=status,
    )


def api_astrometrics_resolve_by_coords(app):
    """Resolve targets by sky coordinates within a search radius.

    Query string parameters:
        ra      (required, deg)      - right ascension in degrees
        dec     (required, deg)      - declination in degrees
        radius  (optional, arcsec)   - search radius (default 60)
        max     (optional, int)      - maximum results (default 50)

    :param app: the ARI application object
    :return: Flask JSON response with ``success`` and ``matches``,
             where ``matches`` is a list of
             ``{apero_name, separation_arcsec, payload}`` dicts ordered
             by ascending separation.
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
    if err is not None:
        return err

    try:
        ra_deg = float(request.args.get("ra", "").strip())
        dec_deg = float(request.args.get("dec", "").strip())
    except ValueError:
        return jsonify(success=False,
                       error="Invalid 'ra' / 'dec'"), 400

    radius_arcsec = request.args.get("radius", "60").strip() or "60"
    max_results = request.args.get("max", "50").strip() or "50"
    try:
        radius = float(radius_arcsec)
        n_max = max(1, int(max_results))
    except ValueError:
        return jsonify(success=False,
                       error="Invalid 'radius' / 'max'"), 400

    try:
        hits = dra.find_by_coords(
            str(_astrom_dir(app)),
            ra_deg=ra_deg, dec_deg=dec_deg,
            radius_arcsec=radius, max_results=n_max,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    matches = []
    for entry, sep_arcsec in hits:
        matches.append({
            "apero_name": entry.get("APERO_NAME"),
            "separation_arcsec": sep_arcsec,
            "payload": _build_payload(entry),
            "entry": entry,
        })

    return jsonify(success=True, matches=matches,
                   ra=ra_deg, dec=dec_deg, radius_arcsec=radius)


def api_astrometrics_resolve_by_filter(app):
    """Resolve targets by an arbitrary column-value filter.

    Query string parameters:
        column   (required) - the YAML key to filter on
        value    (required) - the value to match
        match    (optional) - one of ``exact``, ``substring``,
                              ``glob``, ``regex``, ``ge``, ``le``,
                              ``gt``, ``lt`` or ``auto`` (default).
        max      (optional, int) - maximum results (default 200)

    :param app: the ARI application object
    :return: Flask JSON response with ``success`` and ``matches``
             (list of ``{apero_name, payload}`` dicts).
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
    if err is not None:
        return err

    column = (request.args.get("column") or "").strip()
    value = request.args.get("value")
    match_mode = (request.args.get("match") or "auto").strip()
    if not column or value is None:
        return jsonify(success=False,
                       error="Missing 'column' / 'value'"), 400

    try:
        n_max = max(1, int(request.args.get("max", "200")))
    except ValueError:
        return jsonify(success=False, error="Invalid 'max'"), 400

    try:
        hits = dra.find_by_filter(
            str(_astrom_dir(app)),
            column=column, value=value,
            match=match_mode, max_results=n_max,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    matches = []
    for entry in hits:
        matches.append({
            "apero_name": entry.get("APERO_NAME"),
            "payload": _build_payload(entry),
            "entry": entry,
        })

    return jsonify(success=True, matches=matches,
                   column=column, value=value, match=match_mode)


def api_astrometrics_columns(app):
    """List the union of YAML keys across all astrometric entries.

    Used to populate the column dropdown of the advanced (filter)
    resolve form on the astrometrics page.

    :param app: the ARI application object
    :return: Flask JSON response with ``success`` and ``columns``
             (sorted list of strings).
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
    if err is not None:
        return err

    try:
        cols = dra.list_columns(str(_astrom_dir(app)))
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    return jsonify(success=True, columns=cols)


def api_astrometrics_list_all(app):
    """Return a summary row per astrometric entry across all statuses.

    Used by the "Astrometric database" tab on the astrometrics page.
    Each row contains the columns the table renders (and nothing more)
    so the response stays small even with thousands of entries.

    :param app: the ARI application object
    :return: Flask JSON response with ``success`` and ``rows`` (list of
             dicts with keys APERO_NAME, APERO_CLASS, RA, DEC, TEFF,
             SPT, STATUS, KEYWORDS, NOTES).
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
    if err is not None:
        return err

    astrom_root = str(_astrom_dir(app))
    # Disk-cache hit: keyed by the same mtime signature drs_astrometrics
    # uses internally; avoids the ~1.5s yaml rescan on cold start /
    # after any astrometric edit when the cached projection still
    # matches what's on disk.
    try:
        sig = dra._dir_mtime_signature(astrom_root)
    except Exception:  # noqa: BLE001
        sig = None
    cache_path = os.path.join(astrom_root, '.list_all_cache.json')
    if sig is not None:
        try:
            with open(cache_path, 'r', encoding='utf-8') as fp:
                cached = _json.load(fp)
            if (isinstance(cached, dict)
                    and cached.get('sig') == sig
                    and cached.get('version') == 2
                    and isinstance(cached.get('rows'), list)):
                rows = cached['rows']
                return jsonify(success=True, rows=rows,
                               count=len(rows))
        except (OSError, ValueError):
            pass

    rows = []
    for fpath in dra.iter_yaml_files(astrom_root):
        try:
            entry = dra.AstrometricDatabase._read_yaml(fpath)
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(entry, dict):
            continue
        apero_name = entry.get('APERO_NAME')
        if not apero_name:
            apero_name = Path(fpath).stem
        ra_block = entry.get("RA") or {}
        dec_block = entry.get("DEC") or {}
        teff_block = entry.get("TEFF") or {}
        spt_block = entry.get("SPT") or {}
        status = _entry_status_from_path(
            dra, astrom_root, fpath, entry, str(apero_name))
        rows.append({
            "APERO_NAME": apero_name,
            "APERO_CLASS": entry.get("APERO_CLASS") or "",
            "RA": (ra_block.get("value")
                   if isinstance(ra_block, dict) else ra_block),
            "DEC": (dec_block.get("value")
                    if isinstance(dec_block, dict) else dec_block),
            "TEFF": (teff_block.get("value")
                     if isinstance(teff_block, dict) else teff_block),
            "SPT": (spt_block.get("value")
                    if isinstance(spt_block, dict) else spt_block),
            "STATUS": status,
            "KEYWORDS": entry.get("KEYWORDS") or "",
            "NOTES": entry.get("NOTES") or "",
        })

    rows.sort(key=lambda r: str(r.get("APERO_NAME") or "").lower())
    # Best-effort write of the disk cache so the next cold start
    # (or first call after process restart) can skip the yaml scan.
    if sig is not None:
        try:
            tmp_path = cache_path + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as fp:
                _json.dump({'version': 2, 'sig': sig, 'rows': rows},
                           fp)
            os.replace(tmp_path, cache_path)
        except OSError:
            pass
    return jsonify(success=True, rows=rows, count=len(rows))


def api_astrometrics_list_rejected(app):
    """Return all entries currently in the ``rejected/`` sub-folder.

    Used by the "Rejected object names" tab on the astrometrics page.
    The response intentionally exposes only the user-visible fields
    needed to populate the per-entry cards.

    :param app: the ARI application object
    :return: Flask JSON response with ``success`` and ``rows``
             (list of dicts: APERO_NAME, ORIGINAL_NAME, ALIASES,
             NOTES, FIRST_AUTHOR, FIRST_UPDATED, LAST_AUTHOR,
             LAST_EDIT).
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
    if err is not None:
        return err

    astrom_root = _astrom_dir(app)
    rej_dir = astrom_root / dra.STATUS_REJECTED
    rows = []
    if rej_dir.is_dir():
        try:
            for name in sorted(os.listdir(str(rej_dir))):
                if not name.endswith('.yaml'):
                    continue
                fpath = rej_dir / name
                try:
                    entry = dra.AstrometricDatabase._read_yaml(
                        str(fpath)) or {}
                except Exception:  # noqa: BLE001
                    continue
                aliases = entry.get('ALIASES') or []
                if isinstance(aliases, str):
                    aliases = [aliases]
                rows.append({
                    'APERO_NAME': entry.get('APERO_NAME') or
                                  name[:-5],
                    'ORIGINAL_NAME': (
                        entry.get('ORIGINAL_NAME') or ''),
                    'ALIASES': list(aliases),
                    'NOTES': entry.get('NOTES') or '',
                    'FIRST_AUTHOR': (
                        entry.get('FIRST_AUTHOR') or ''),
                    'FIRST_UPDATED': (
                        entry.get('FIRST_UPDATED') or ''),
                    'LAST_AUTHOR': (
                        entry.get('LAST_AUTHOR') or ''),
                    'LAST_EDIT': entry.get('LAST_EDIT') or '',
                })
        except Exception as exc:  # noqa: BLE001
            return jsonify(success=False, error=str(exc)), 500
    rows.sort(key=lambda r: str(r.get('APERO_NAME') or '').lower())
    return jsonify(success=True, rows=rows, count=len(rows))


def api_astrometrics_add_rejected(app):
    """Manually add a new entry to the ``rejected/`` list.

    JSON body:
        apero_name (required, str)  - canonical name to reject
        aliases    (optional, list) - alternate names to reject too
        notes      (optional, str)  - free-form note shown on card

    Permission: ``manage.astrometrics`` OR any monitor permission
    (``monitor`` / ``monitor.<INST>`` / ``view.monitor.<INST>``).

    Refuses to overwrite an existing rejected/<NAME>.yaml so monitors
    can't silently clobber an earlier rejection note. Removing or
    editing an existing rejected entry is exposed via dedicated
    manage.astrometrics-only endpoints.

    :param app: the ARI application object
    :return: Flask JSON response with the created entry on success
    """
    from apero.core import drs_astrometrics as dra
    import datetime as _dt
    import yaml as _yaml

    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error="Login required"), 401
    perms = resolve_user_permissions(
        user_info["groups"], app.ari_groups
    )
    if not _has_monitor_perm(perms, ''):
        return jsonify(
            success=False,
            error=("Forbidden (need monitor or "
                   "manage.astrometrics)"),
        ), 403

    body = request.get_json(silent=True) or {}
    apero_name = (body.get('apero_name') or '').strip()
    if not apero_name:
        return jsonify(success=False,
                       error="Missing 'apero_name'"), 400
    raw_aliases = body.get('aliases') or []
    if isinstance(raw_aliases, str):
        raw_aliases = [raw_aliases]
    aliases = []
    for a in raw_aliases:
        s = str(a or '').strip()
        if s:
            aliases.append(s)
    notes = (body.get('notes') or '').strip()

    astrom_root = _astrom_dir(app)
    rej_dir = astrom_root / dra.STATUS_REJECTED
    rej_dir.mkdir(parents=True, exist_ok=True)
    fname = dra._safe_filename(apero_name)
    target = rej_dir / fname
    if target.is_file():
        return jsonify(
            success=False,
            error=("Rejection entry already exists for '{0}'"
                   ).format(apero_name),
        ), 409

    # also refuse if a verified/pending entry exists with that name
    try:
        existing = dra.find_by_name(str(astrom_root), apero_name)
    except Exception:  # noqa: BLE001
        existing = None
    if existing is not None:
        cur_status = (existing.get('STATUS') or '').lower()
        if cur_status and cur_status != dra.STATUS_REJECTED:
            return jsonify(
                success=False,
                error=("'{0}' already exists with status '{1}'; "
                       "use the standard set-status endpoint "
                       "to reject it").format(
                           apero_name, cur_status),
            ), 409

    author = user_info.get("username") or "unknown"
    today = _dt.datetime.utcnow().isoformat(timespec='seconds')
    entry = {
        'APERO_NAME': apero_name,
        'ORIGINAL_NAME': apero_name,
        'APERO_CLASS': 'REJECTED',
        'ALIASES': aliases,
        'NOTES': notes,
        'STATUS': dra.STATUS_REJECTED,
        'FIRST_UPDATED': today,
        'FIRST_AUTHOR': author,
        'LAST_EDIT': today,
        'LAST_AUTHOR': author,
    }
    try:
        with target.open('w', encoding='utf-8') as out:
            _yaml.safe_dump(entry, out, sort_keys=False,
                            default_flow_style=False,
                            allow_unicode=True)
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    # Invalidate caches so the new entry is immediately resolvable
    try:
        dra._invalidate_dir_caches(str(astrom_root))
    except Exception:  # noqa: BLE001
        pass

    return jsonify(
        success=True,
        apero_name=apero_name,
        path=str(target),
        entry=entry,
    )


def api_astrometrics_update_rejected(app):
    """Edit an existing entry in the ``rejected/`` list.

    JSON body:
        old_apero_name (required, str) - current canonical name
        apero_name     (required, str) - new canonical name
        aliases        (optional, list)
        notes          (optional, str)

    Required permission: ``manage.astrometrics``.

    :param app: the ARI application object
    :return: Flask JSON response with updated entry on success
    """
    from apero.core import drs_astrometrics as dra
    import datetime as _dt
    import yaml as _yaml

    user_info, err = _check_perm(app, "manage.astrometrics")
    if err is not None:
        return err

    body = request.get_json(silent=True) or {}
    old_name = (body.get('old_apero_name') or '').strip()
    apero_name = (body.get('apero_name') or '').strip()
    if not old_name or not apero_name:
        return jsonify(
            success=False,
            error=("Missing 'old_apero_name' / 'apero_name'"),
        ), 400

    raw_aliases = body.get('aliases') or []
    if isinstance(raw_aliases, str):
        raw_aliases = [raw_aliases]
    aliases = []
    for alias in raw_aliases:
        text = str(alias or '').strip()
        if text:
            aliases.append(text)
    notes = (body.get('notes') or '').strip()

    astrom_root = _astrom_dir(app)
    rej_dir = astrom_root / dra.STATUS_REJECTED
    src = rej_dir / dra._safe_filename(old_name)
    dst = rej_dir / dra._safe_filename(apero_name)
    if not src.is_file():
        return jsonify(
            success=False,
            error=("No rejected entry for '{0}'"
                   ).format(old_name),
        ), 404
    if src != dst and dst.is_file():
        return jsonify(
            success=False,
            error=("A rejected entry for '{0}' already exists"
                   ).format(apero_name),
        ), 409

    try:
        existing = dra.AstrometricDatabase._read_yaml(str(src)) or {}
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 400

    author = user_info.get('username') or 'unknown'
    now = _dt.datetime.utcnow().isoformat(timespec='seconds')
    entry = dict(existing)
    entry['APERO_NAME'] = apero_name
    entry['ORIGINAL_NAME'] = (
        str(entry.get('ORIGINAL_NAME') or '').strip() or apero_name
    )
    entry['APERO_CLASS'] = 'REJECTED'
    entry['ALIASES'] = aliases
    entry['NOTES'] = notes
    entry['STATUS'] = dra.STATUS_REJECTED
    if not entry.get('FIRST_UPDATED'):
        entry['FIRST_UPDATED'] = now
    if not entry.get('FIRST_AUTHOR'):
        entry['FIRST_AUTHOR'] = author
    entry['LAST_EDIT'] = now
    entry['LAST_AUTHOR'] = author

    try:
        tmp = dst.with_suffix(dst.suffix + '.tmp')
        with tmp.open('w', encoding='utf-8') as out:
            _yaml.safe_dump(entry, out, sort_keys=False,
                            default_flow_style=False,
                            allow_unicode=True)
        os.replace(str(tmp), str(dst))
        if src != dst and src.is_file():
            src.unlink()
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    try:
        dra._invalidate_dir_caches(str(astrom_root))
    except Exception:  # noqa: BLE001
        pass

    return jsonify(
        success=True,
        apero_name=apero_name,
        path=str(dst),
        entry=entry,
    )


def api_astrometrics_delete_rejected(app):
    """Delete an existing entry from the ``rejected/`` list.

    JSON body:
        apero_name (required, str) - canonical name to delete

    Required permission: ``manage.astrometrics``.

    :param app: the ARI application object
    :return: Flask JSON response on success
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_perm(app, "manage.astrometrics")
    if err is not None:
        return err

    body = request.get_json(silent=True) or {}
    apero_name = (body.get('apero_name') or '').strip()
    if not apero_name:
        return jsonify(success=False,
                       error="Missing 'apero_name'"), 400

    astrom_root = _astrom_dir(app)
    rej_dir = astrom_root / dra.STATUS_REJECTED
    target = rej_dir / dra._safe_filename(apero_name)
    if not target.is_file():
        return jsonify(
            success=False,
            error=("No rejected entry for '{0}'"
                   ).format(apero_name),
        ), 404

    try:
        target.unlink()
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    try:
        dra._invalidate_dir_caches(str(astrom_root))
    except Exception:  # noqa: BLE001
        pass

    return jsonify(success=True, apero_name=apero_name)


# Numeric astrometric fields that the manual-add form may set; each
# one is stored under the standard ``{value, source, units}`` schema
# (units are filled in from this map only if the caller does not
# supply an explicit per-field ``source``).
_MANUAL_FIELD_UNITS = {
    'RA': 'deg',
    'DEC': 'deg',
    'PMRA': 'mas/yr',
    'PMDE': 'mas/yr',
    'PLX': 'mas',
    'RV': 'km/s',
    'TEFF': 'K',
}
_MANUAL_EXTRA_NUMERIC_UNITS = {
    'RA_J2000_DEG': 'deg',
    'DEC_J2000_DEG': 'deg',
    'GALACTIC_LON': 'deg',
    'GALACTIC_LAT': 'deg',
    'ECLIPTIC_LON': 'deg',
    'ECLIPTIC_LAT': 'deg',
    'V_SKY': 'km/s',
    'V3D': 'km/s',
    'U': 'km/s',
    'V': 'km/s',
    'W': 'km/s',
    'G_MAG': 'mag',
    'GBP_MAG': 'mag',
    'GRP_MAG': 'mag',
    'J_MAG': 'mag',
    'H_MAG': 'mag',
    'KS_MAG': 'mag',
    'W1_MAG': 'mag',
    'W2_MAG': 'mag',
    'W3_MAG': 'mag',
    'W4_MAG': 'mag',
    'FE_H': 'dex',
    'GAIA_MH_GSPPHOT': 'dex',
    'R_STAR_MKS': 'Rsun',
    'R_STAR_MKS_FEH': 'Rsun',
    'GAIA_RADIUS_FLAME': 'Rsun',
    'MASS_STAR_MANN15': 'Msun',
    'MASS_STAR_DELFOSSE00': 'Msun',
    'GAIA_MASS_FLAME': 'Msun',
    'LOG_G': 'cgs',
    'GAIA_LOGG_GSPPHOT': 'cgs',
    'L_STAR': 'Lsun',
    'GAIA_LUM_FLAME': 'Lsun',
    'VSINI': 'km/s',
    'TEFF_GAIA_JH': 'K',
    'TEFF_GAIA': 'K',
    'GAIA_TEFF_GSPPHOT': 'K',
    'TELLURIC_VSYS_PLUS_VBARY_MIN': 'km/s',
    'TELLURIC_VSYS_PLUS_VBARY_MAX': 'km/s',
}
_MANUAL_RESERVED_KEYS = {
    'APERO_NAME', 'ORIGINAL_NAME', 'SIMBAD_NAME', 'APERO_CLASS',
    'RA', 'DEC', 'PMRA', 'PMDE', 'PLX', 'RV', 'TEFF', 'EPOCH',
    'SPT', 'GAIA_SOURCE_ID', 'NO_PM', 'ALIASES', 'KEYWORDS',
    'NOTES', 'STATUS',
    'FIRST_UPDATED', 'FIRST_AUTHOR', 'LAST_EDIT', 'LAST_AUTHOR',
}
_MANUAL_DERIVED_KEYS = (
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
# Plain top-level scalar fields the manual-add form may set
_MANUAL_SCALAR_FIELDS = ('EPOCH', 'SPT', 'GAIA_SOURCE_ID')


# ---------------------------------------------------------------------
# Concurrent-edit lock — minimal "always-grant" stub.
# The frontend (astrometrics_lock.js) calls /lock/{acquire,heartbeat,
# release} and the save endpoints call _astro_check_lock_for_save to
# verify the caller still owns the lock. A persistent multi-process
# lock store is not yet implemented, so for now we accept every call
# and never block a save. This keeps the contract stable so a real
# implementation can drop in later without touching call sites.
# ---------------------------------------------------------------------
def _astro_check_lock_for_save(app, apero_name, user_info, perms):
    """Return ``(True, None)`` — always allow saves (no-op stub)."""
    return True, None


def api_astrometrics_lock_acquire(app):
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error="Login required"), 401
    return jsonify(
        success=True,
        owner=user_info.get("username") or "unknown",
        held=False,
    )


def api_astrometrics_lock_heartbeat(app):
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error="Login required"), 401
    return jsonify(success=True)


def api_astrometrics_lock_release(app):
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error="Login required"), 401
    return jsonify(success=True)


def _coerce_optional_float(raw):
    """Return ``float(raw)`` or ``None`` (empty / 'null' -> None).

    Raises ``ValueError`` with a friendly message on bad numeric input
    so the calling endpoint can surface it as a 400 response.
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    if s == '' or s.lower() in ('null', 'none', 'nan'):
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        raise ValueError(
            "expected a number or blank, got {0!r}".format(raw))


def _apply_manual_extra_fields(entry, extra_fields):
    """Apply optional extra_fields values onto a manual target entry.

    :param entry: dict, mutable yaml entry being built
    :param extra_fields: mapping of yaml_key -> raw form value
    :raises ValueError: on invalid key names or invalid numeric values
    """
    if extra_fields is None:
        return
    if not isinstance(extra_fields, dict):
        raise ValueError("'extra_fields' must be an object")

    for raw_key, raw_val in extra_fields.items():
        yaml_key = str(raw_key or '').strip().upper()
        if not yaml_key:
            continue
        if not re.match(r'^[A-Z0-9_]+$', yaml_key):
            raise ValueError(
                "Invalid extra field key {0!r}".format(raw_key)
            )
        if yaml_key in _MANUAL_RESERVED_KEYS:
            continue

        sval = '' if raw_val is None else str(raw_val).strip()
        if sval == '':
            continue

        if yaml_key in _MANUAL_EXTRA_NUMERIC_UNITS:
            try:
                fval = _coerce_optional_float(sval)
            except ValueError as exc:
                raise ValueError(
                    "Field {0!r}: {1}".format(yaml_key, exc)
                )
            if fval is None:
                continue
            entry[yaml_key] = {
                'value': fval,
                'source': 'manual',
                'units': _MANUAL_EXTRA_NUMERIC_UNITS.get(yaml_key),
            }
            continue

        entry[yaml_key] = sval


def _normalize_manual_entry_for_recompute(entry, dra):
    """Normalize block/scalar types before running DRS derivations.

    :param entry: dict, mutable entry
    :param dra: imported drs_astrometrics module
    """
    dra._full_resolve_schema(entry)

    # SPT must be a value/source block for _derive_fields.
    spt = entry.get('SPT')
    if isinstance(spt, str):
        entry['SPT'] = dict(value=spt, source='manual')
    elif spt is None:
        entry['SPT'] = dict(value=None, source=None)

    # Convert plain scalar photometry inputs to value/source blocks.
    for key in ('G_MAG', 'GBP_MAG', 'GRP_MAG',
                'J_MAG', 'H_MAG', 'KS_MAG',
                'W1_MAG', 'W2_MAG', 'W3_MAG', 'W4_MAG'):
        val = entry.get(key)
        if isinstance(val, dict):
            continue
        if val is None:
            entry[key] = dict(value=None, source=None)
        else:
            entry[key] = dict(value=val, source='manual')


def _recompute_manual_fields(entry, dra):
    """Force-refresh derived fields in a manual entry.

    :param entry: dict, mutable yaml entry
    :param dra: imported drs_astrometrics module
    """
    _normalize_manual_entry_for_recompute(entry, dra)
    for key in _MANUAL_DERIVED_KEYS:
        entry[key] = None
    dra._derive_fields(entry)


def api_astrometrics_add_manual(app):
    """Manually add a new astrometric entry under ``pending/``.

    JSON body:
        apero_name   (required, str)  - canonical APERO name
        apero_class  (optional, str)  - defaults to ``STAR``
        aliases      (optional, list) - alternate names
        notes        (optional, str)  - free-form note
        no_pm        (optional, bool) - mark entry as having no PM
        ra, dec      (optional, num)  - in degrees
        pmra, pmde   (optional, num)  - in mas/yr
        plx          (optional, num)  - in mas
        rv           (optional, num)  - in km/s
        teff         (optional, num)  - in K
        epoch        (optional, num)  - JD epoch
        spt          (optional, str)  - spectral type
        gaia_source_id (optional, str)
        original_name  (optional, str) - defaults to ``apero_name``
        simbad_name    (optional, str)
        extra_fields   (optional, object) - additional resolve-target
                fields as ``{YAML_KEY: value}``
        allow_update   (optional, bool) - update existing entry when
                True (default False)
        original_apero_name (optional, str) - lookup key for edits

    Permission: ``manage.astrometrics`` OR any monitor permission
    (``monitor`` / ``monitor.<INST>`` / ``view.monitor.<INST>``).

    Refuses to overwrite an existing entry; the caller must use the
    standard upload/edit endpoints to modify an entry that already
    exists (under any status sub-directory).

    :param app: the ARI application object
    :return: Flask JSON response with the created entry on success
    """
    from apero.core import drs_astrometrics as dra
    import datetime as _dt
    import yaml as _yaml

    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error="Login required"), 401
    perms = resolve_user_permissions(
        user_info["groups"], app.ari_groups
    )
    if not _has_monitor_perm(perms, ''):
        return jsonify(
            success=False,
            error=("Forbidden (need monitor or "
                   "manage.astrometrics)"),
        ), 403

    body = request.get_json(silent=True) or {}
    apero_name = (body.get('apero_name') or '').strip()
    if not apero_name:
        return jsonify(success=False,
                       error="Missing 'apero_name'"), 400
    allow_update = bool(body.get('allow_update'))
    raw_original = body.get('original_apero_name')
    original_supplied = bool(
        raw_original is not None
        and str(raw_original).strip()
    )
    original_name_for_edit = (
        str(raw_original).strip() if original_supplied
        else apero_name
    )
    # Treat the request as an update whenever the client has told us
    # which existing entry it is editing. The caller has clearly
    # opened the form via Edit, so the legacy "use the edit endpoints
    # to modify it" guard would just confuse them.
    if original_supplied:
        allow_update = True
    apero_class = (body.get('apero_class') or 'STAR').strip().upper()
    if apero_class == 'REJECTED':
        return jsonify(
            success=False,
            error=("Use /api/astrometrics/add-rejected to add a "
                   "rejected entry"),
        ), 400

    raw_aliases = body.get('aliases') or []
    if isinstance(raw_aliases, str):
        raw_aliases = [raw_aliases]
    aliases = []
    for a in raw_aliases:
        s = str(a or '').strip()
        if s:
            aliases.append(s)

    raw_keywords = body.get('keywords') or []
    if isinstance(raw_keywords, str):
        raw_keywords = [raw_keywords]
    keywords = []
    for kw in raw_keywords:
        s = str(kw or '').strip()
        if s:
            keywords.append(s)

    notes = (body.get('notes') or '').strip()
    no_pm = bool(body.get('no_pm'))

    # parse all optional numeric fields up-front so we can return a
    # single coherent error for bad numeric input
    parsed_nums = {}
    field_aliases = {
        'ra': 'RA', 'dec': 'DEC', 'pmra': 'PMRA', 'pmde': 'PMDE',
        'plx': 'PLX', 'rv': 'RV', 'teff': 'TEFF', 'epoch': 'EPOCH',
    }
    for body_key, yaml_key in field_aliases.items():
        if body_key not in body:
            continue
        try:
            parsed_nums[yaml_key] = _coerce_optional_float(
                body.get(body_key))
        except ValueError as exc:
            return jsonify(
                success=False,
                error="Field {0!r}: {1}".format(yaml_key, exc),
            ), 400

    # refuse if an entry already exists under any status sub-dir
    astrom_root = _astrom_dir(app)
    try:
        existing = dra.find_by_name(
            str(astrom_root), original_name_for_edit
        )
    except Exception:  # noqa: BLE001
        existing = None
    if existing is not None:
        cur_status = (existing.get('STATUS') or '').lower()
        if allow_update:
            pass
        else:
            return jsonify(
                success=False,
                error=("Cannot create a new target named '{0}': an "
                       "entry with status '{1}' already exists. To "
                       "modify it, open it via Resolve target and "
                       "click 'Edit'.").format(
                           apero_name, cur_status or 'unknown'),
            ), 409
    is_update = existing is not None and allow_update
    if is_update:
        _perms_now = resolve_user_permissions(
            user_info["groups"], app.ari_groups)
        ok, lock_err = _astro_check_lock_for_save(
            app, original_name_for_edit, user_info, _perms_now)
        if not ok:
            return lock_err

    pending_dir = astrom_root / dra.STATUS_PENDING
    pending_dir.mkdir(parents=True, exist_ok=True)
    fname = dra._safe_filename(apero_name)
    target = pending_dir / fname
    existing_path = None
    if is_update:
        try:
            found = dra.find_yaml_in_status_dirs(
                str(astrom_root), original_name_for_edit
            )
            if found is not None:
                existing_path = Path(found[0])
        except Exception:  # noqa: BLE001
            existing_path = None
        if target.is_file() and existing_path is not None:
            if target.resolve() != existing_path.resolve():
                return jsonify(
                    success=False,
                    error=("Cannot rename '{0}' to '{1}': "
                           "target already exists").format(
                               original_name_for_edit,
                               apero_name,
                           ),
                ), 409
    else:
        if target.is_file():
            return jsonify(
                success=False,
                error=("Entry already exists for '{0}' under pending/"
                       ).format(apero_name),
            ), 409

    author = user_info.get("username") or "unknown"
    today = _dt.datetime.utcnow().isoformat(timespec='seconds')

    first_updated = today
    first_author = author
    if is_update and isinstance(existing, dict):
        first_updated = str(existing.get('FIRST_UPDATED') or '').strip()
        first_author = str(existing.get('FIRST_AUTHOR') or '').strip()
        if not first_updated:
            first_updated = today
        if not first_author:
            first_author = author

    entry = {
        'APERO_NAME': apero_name,
        'ORIGINAL_NAME': (
            body.get('original_name') or apero_name).strip(),
        'APERO_CLASS': apero_class,
    }
    simbad_name = (body.get('simbad_name') or '').strip()
    if simbad_name:
        entry['SIMBAD_NAME'] = simbad_name

    # build the {value, source, units} mappings for numeric fields;
    # only emit a key if the user supplied something (even null)
    for yaml_key in ('RA', 'DEC', 'PMRA', 'PMDE', 'PLX',
                     'RV', 'TEFF'):
        if yaml_key not in parsed_nums:
            continue
        entry[yaml_key] = {
            'value': parsed_nums[yaml_key],
            'source': 'manual',
            'units': _MANUAL_FIELD_UNITS.get(yaml_key),
        }
    if 'EPOCH' in parsed_nums:
        entry['EPOCH'] = parsed_nums['EPOCH']

    for body_key in ('spt', 'gaia_source_id'):
        if body_key not in body:
            continue
        v = body.get(body_key)
        s = '' if v is None else str(v).strip()
        if s:
            yaml_key = ('SPT' if body_key == 'spt'
                        else 'GAIA_SOURCE_ID')
            entry[yaml_key] = s

    try:
        _apply_manual_extra_fields(entry, body.get('extra_fields'))
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400

    if no_pm:
        entry['NO_PM'] = True

    try:
        _recompute_manual_fields(entry, dra)
    except Exception as exc:  # noqa: BLE001
        return jsonify(
            success=False,
            error='Failed to recompute derived values: {0}'.format(exc),
        ), 400

    entry['ALIASES'] = aliases
    if keywords:
        entry['KEYWORDS'] = keywords
    else:
        entry['KEYWORDS'] = None
    entry['NOTES'] = notes or 'added manually via ARI'
    entry['STATUS'] = dra.STATUS_PENDING
    entry['FIRST_UPDATED'] = first_updated
    entry['FIRST_AUTHOR'] = first_author
    entry['LAST_EDIT'] = today
    entry['LAST_AUTHOR'] = author

    try:
        with target.open('w', encoding='utf-8') as out:
            _yaml.safe_dump(entry, out, sort_keys=False,
                            default_flow_style=False,
                            allow_unicode=True)
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    if is_update and existing_path is not None:
        try:
            if existing_path.resolve() != target.resolve():
                existing_path.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass

    try:
        dra._invalidate_dir_caches(str(astrom_root))
    except Exception:  # noqa: BLE001
        pass

    # Append an audit-log record for this save (best-effort).
    try:
        from apero_ri.application import astrometrics_history
        action = 'edit' if is_update else 'create'
        if str(body.get('source') or '').lower() == 'restore':
            action = 'restore'
        before_snap = (existing
                       if isinstance(existing, dict) else None)
        astrometrics_history.append_history(
            astrom_root=astrom_root,
            apero_name=apero_name,
            user=author,
            action=action,
            before=before_snap,
            after=entry,
            previous_apero_name=(
                original_name_for_edit
                if (is_update
                    and original_name_for_edit != apero_name)
                else None
            ),
        )
    except Exception:  # noqa: BLE001
        pass

    return jsonify(
        success=True,
        apero_name=apero_name,
        path=str(target),
        entry=entry,
        mode='updated' if is_update else 'created',
    )


def api_astrometrics_recompute_manual(app):
    """Preview recomputed derived fields for a manual-target payload.

    Accepts the same core numeric/scalar payload as add-manual and
    returns a transient recomputed entry without writing any yaml file.

    :param app: ARI application instance
    :return: Flask JSON response
    """
    from apero.core import drs_astrometrics as dra

    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401
    perms = resolve_user_permissions(
        user_info['groups'], app.ari_groups
    )
    if not _has_monitor_perm(perms, ''):
        return jsonify(
            success=False,
            error='Forbidden (need monitor or manage.astrometrics)',
        ), 403

    body = request.get_json(silent=True) or {}
    apero_name = (body.get('apero_name') or '').strip()
    if not apero_name:
        return jsonify(success=False,
                       error="Missing 'apero_name'"), 400

    entry = dict()
    entry['APERO_NAME'] = apero_name
    entry['ORIGINAL_NAME'] = (
        body.get('original_name') or apero_name
    ).strip()
    entry['APERO_CLASS'] = (
        body.get('apero_class') or 'STAR'
    ).strip().upper()

    simbad_name = (body.get('simbad_name') or '').strip()
    if simbad_name:
        entry['SIMBAD_NAME'] = simbad_name

    field_aliases = {
        'ra': 'RA', 'dec': 'DEC', 'pmra': 'PMRA', 'pmde': 'PMDE',
        'plx': 'PLX', 'rv': 'RV', 'teff': 'TEFF', 'epoch': 'EPOCH',
    }
    for body_key, yaml_key in field_aliases.items():
        if body_key not in body:
            continue
        try:
            num = _coerce_optional_float(body.get(body_key))
        except ValueError as exc:
            return jsonify(
                success=False,
                error='Field {0!r}: {1}'.format(yaml_key, exc),
            ), 400
        if yaml_key == 'EPOCH':
            entry['EPOCH'] = num
            continue
        entry[yaml_key] = {
            'value': num,
            'source': 'manual',
            'units': _MANUAL_FIELD_UNITS.get(yaml_key),
        }

    spt = (body.get('spt') or '').strip()
    if spt:
        entry['SPT'] = spt
    gaia_sid = (body.get('gaia_source_id') or '').strip()
    if gaia_sid:
        entry['GAIA_SOURCE_ID'] = gaia_sid

    raw_aliases = body.get('aliases') or []
    if isinstance(raw_aliases, str):
        raw_aliases = [raw_aliases]
    aliases = []
    for alias in raw_aliases:
        sval = str(alias or '').strip()
        if sval:
            aliases.append(sval)
    entry['ALIASES'] = aliases

    notes = (body.get('notes') or '').strip()
    if notes:
        entry['NOTES'] = notes
    if bool(body.get('no_pm')):
        entry['NO_PM'] = True

    try:
        _apply_manual_extra_fields(entry, body.get('extra_fields'))
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400

    try:
        _recompute_manual_fields(entry, dra)
    except Exception as exc:  # noqa: BLE001
        return jsonify(
            success=False,
            error='Failed to recompute derived values: {0}'.format(exc),
        ), 400

    return jsonify(success=True, entry=entry)


# =============================================================================
# Edit / upload endpoints (moderator+ / monitor+)
# =============================================================================
def _check_perm(app, perm):
    """Return ``(user_info, err)`` enforcing a single named permission.

    :param app: the ARI application object
    :param perm: str, the permission string the caller must hold
    :return: tuple ``(user_info, err)`` where ``err`` is None on
             success or a Flask response tuple to return otherwise.
    """
    user_info = app._get_api_user()
    if not user_info:
        return None, (
            jsonify(success=False, error="Login required"), 401
        )
    perms = resolve_user_permissions(
        user_info["groups"], app.ari_groups
    )
    if perm not in perms:
        return user_info, (
            jsonify(success=False,
                    error="Forbidden (need {0})".format(perm)),
            403,
        )
    return user_info, None


def _coerce_value(raw):
    """Best-effort coercion of a JSON-supplied value.

    - Empty string / None -> None
    - "true" / "false" (case-insensitive) -> bool
    - All-numeric strings -> float (or int when no decimal point)
    - Otherwise -> the original value unchanged
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float, bool, list, dict)):
        return raw
    s = str(raw).strip()
    if s == "" or s.lower() in ("none", "null"):
        return None
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        if "." in s or "e" in low:
            return float(s)
        return int(s)
    except ValueError:
        return s


def api_astrometrics_update_field(app):
    """POST one field update to an existing astrometric YAML entry.

    JSON body:
        apero_name (required) - canonical name of the entry
        key        (required) - top-level YAML key to update
        value      (required) - new value (any JSON-serialisable type)

    Required permission: ``manage.astrometrics`` (moderator+).
    A change to ``APERO_NAME`` triggers an atomic file rename via
    :func:`apero.core.drs_astrometrics.update_entry_field`.

    :param app: the ARI application object
    :return: Flask JSON response with the updated entry on success
    """
    from apero.core import drs_astrometrics as dra

    user_info, err = _check_perm(app, "manage.astrometrics")
    if err is not None:
        return err

    body = request.get_json(silent=True) or {}
    apero_name = (body.get("apero_name") or "").strip()
    key = (body.get("key") or "").strip()
    if not apero_name or not key:
        return jsonify(success=False,
                       error="Missing 'apero_name' / 'key'"), 400
    raw_value = body.get("value")
    new_value = _coerce_value(raw_value)
    author = user_info.get("username") or "unknown"

    _perms_now = resolve_user_permissions(
        user_info["groups"], app.ari_groups)
    ok, lock_err = _astro_check_lock_for_save(
        app, apero_name, user_info, _perms_now)
    if not ok:
        return lock_err

    try:
        entry = dra.update_entry_field(
            astrom_dir=str(_astrom_dir(app)),
            apero_name=apero_name,
            key=key, value=new_value,
            author=author,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 400

    new_apero = entry.get("APERO_NAME", apero_name)
    # Any edit to a regular target must go back to pending for review.
    current_status = str(entry.get('STATUS') or '').strip().lower()
    if current_status != dra.STATUS_REJECTED:
        try:
            _, _, entry = dra.set_status(
                astrom_root=str(_astrom_dir(app)),
                apero_name=new_apero,
                new_status=dra.STATUS_PENDING,
                author=author,
            )
        except Exception as exc:  # noqa: BLE001
            return jsonify(success=False, error=str(exc)), 400

    return jsonify(
        success=True,
        apero_name=new_apero,
        renamed=(new_apero != apero_name),
        payload=_build_payload(entry),
    )


def api_astrometrics_upload_yaml(app):
    """POST a brand-new astrometric YAML entry.

    JSON body either:
        entry      (required, dict) - the parsed YAML content, or
        yaml_text  (required, str)  - raw YAML text to be parsed

    Required permission: ``upload.astrometrics`` (monitor+).
    By default the call fails if a file already exists for the
    target ``APERO_NAME``; pass ``overwrite: true`` to replace it
    (only honoured when the caller also has ``manage.astrometrics``).

    :param app: the ARI application object
    :return: Flask JSON response with the stored entry on success
    """
    from apero.core import drs_astrometrics as dra

    user_info, err = _check_perm(app, "upload.astrometrics")
    if err is not None:
        return err

    body = request.get_json(silent=True) or {}
    entry = body.get("entry")
    if entry is None:
        text = body.get("yaml_text")
        if not text:
            return jsonify(success=False,
                           error="Missing 'entry' / 'yaml_text'"), 400
        try:
            import yaml as _yaml
            entry = _yaml.safe_load(text)
        except Exception as exc:  # noqa: BLE001
            return jsonify(success=False,
                           error="YAML parse error: {0}".format(exc)
                           ), 400
    if not isinstance(entry, dict):
        return jsonify(success=False,
                       error="entry must be a YAML mapping"), 400

    overwrite_req = bool(body.get("overwrite"))
    if overwrite_req:
        # only moderators can replace existing entries
        perms = resolve_user_permissions(
            user_info["groups"], app.ari_groups
        )
        if "manage.astrometrics" not in perms:
            return jsonify(
                success=False,
                error=("'overwrite' requires manage.astrometrics "
                       "permission"),
            ), 403

    author = user_info.get("username") or "unknown"
    try:
        fpath, stamped = dra.upload_entry(
            str(_astrom_dir(app)), entry,
            author=author, overwrite=overwrite_req,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 400

    return jsonify(
        success=True,
        apero_name=stamped.get("APERO_NAME"),
        path=str(fpath),
        payload=_build_payload(stamped),
    )


def _has_monitor_perm(perms, instrument):
    """Return True if ``perms`` grants verify rights for ``instrument``.

    Accepted: ``manage.astrometrics`` (admin override), bare
    ``monitor``, ``monitor.<INSTRUMENT>``,
    ``view.monitor_portal.<INSTRUMENT>``, or
    ``view.monitor.<INSTRUMENT>`` (case-insensitive instrument).

    When ``instrument`` is falsy the call is treated as a wildcard
    request: any of ``manage.astrometrics``, ``monitor``, or
    ``monitor.<X>`` (for any X) grants access.

    :param perms: iterable of permission strings the user holds
    :param instrument: str, the instrument name to verify against
                       (empty string = wildcard)
    :return: bool
    """
    pset = {str(p) for p in (perms or ())}
    if 'manage.astrometrics' in pset:
        return True
    inst = (str(instrument or '')).strip().lower()
    prefixes = ('monitor.', 'view.monitor_portal.',
                'view.monitor.')
    for p in pset:
        low = p.lower()
        if low == 'monitor':
            return True
        for prefix in prefixes:
            if low.startswith(prefix):
                tail = low[len(prefix):]
                if not inst:
                    return True
                if tail == inst or tail == 'all':
                    return True
    return False


def api_astrometrics_status(app):
    """Return the on-disk status of an astrometric entry by name.

    Query string parameters:
        name (required) - the APERO_NAME (or alias) to look up.

    Visible to anyone with ``view.data_portal``. Used by the data
    portal object page and the resolver UI to decide whether to show
    the verify banner.

    :param app: the ARI application object
    :return: Flask JSON ``{success, apero_name, status, found}``
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
    if err is not None:
        return err

    name = (request.args.get("name") or "").strip()
    if not name:
        return jsonify(success=False, error="Missing 'name'"), 400

    astrom_root = str(_astrom_dir(app))
    try:
        # Resolve aliases -> canonical APERO_NAME first
        entry = dra.find_by_name(astrom_root, name)
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    if not entry:
        return jsonify(success=True, apero_name=None,
                       status=None, found=False)
    apero_name = entry.get("APERO_NAME") or name
    # Prefer in-yaml STATUS; fall back to sub-dir lookup
    status = None
    raw_status = entry.get("STATUS")
    if raw_status:
        status = str(raw_status).strip().lower() or None
    if status is None:
        try:
            found = dra.find_yaml_in_status_dirs(
                astrom_root, apero_name)
            if found is not None:
                status = found[1]
        except Exception:  # noqa: BLE001
            status = None
    return jsonify(success=True, apero_name=apero_name,
                   status=status, found=True)


def _close_verify_issues(app, apero_name, instrument, author):
    """Close any open ``astrometric-verify`` issues for this entry.

    Best-effort: silently ignores any failure (the verify itself is
    the user-visible operation; closing the linked issue is a side
    effect that should not block the response).

    :param app: ARI application instance
    :param apero_name: str, canonical APERO_NAME just verified
    :param instrument: str or None, instrument scope of the issue
    :param author: str, the verifying user (recorded as the closer)
    :return: int, number of issues closed
    """
    try:
        from apero_ri.core import issues as issues_core
    except Exception:  # noqa: BLE001
        return 0
    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    closed = 0
    try:
        rows = issues_core.list_issues(
            data_dir=str(base_dir),
            visibility='admin',
            status='open',
            label='astrometric-verify',
            instrument=(instrument or None),
        )
    except Exception:  # noqa: BLE001
        return 0
    for row in rows or ():
        try:
            row_name = (
                (row.get('apero_name')
                 or (row.get('context') or {}).get('apero_name')
                 or '')
            )
        except Exception:  # noqa: BLE001
            row_name = ''
        if str(row_name).strip().lower() != str(
                apero_name).strip().lower():
            continue
        try:
            issues_core.update_issue(
                data_dir=str(base_dir),
                issue_id=row.get('id'),
                status='resolved',
                note='Verified by {0}'.format(author),
                author=author,
            )
            closed += 1
        except Exception:  # noqa: BLE001
            continue
    return closed


def api_astrometrics_verify(app):
    """Flip a pending astrometric entry to ``verified``.

    JSON body:
        apero_name (required) - canonical name of the entry
        instrument (required) - instrument scope; the caller must
                                hold ``monitor.<INSTRUMENT>`` (or
                                ``manage.astrometrics`` as override)

    Effects:
        - moves the YAML from ``pending/`` (or flat legacy layout)
          to ``verified/`` via ``drs_astrometrics.set_status``
        - refreshes ``LAST_EDIT`` / ``LAST_AUTHOR`` provenance
        - closes any open ``astrometric-verify`` issue for that
          ``apero_name`` + ``instrument``

    :param app: the ARI application object
    :return: Flask JSON response with the verified entry on success
    """
    from apero.core import drs_astrometrics as dra

    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error="Login required"), 401
    perms = resolve_user_permissions(
        user_info["groups"], app.ari_groups
    )
    body = request.get_json(silent=True) or {}
    apero_name = (body.get("apero_name") or "").strip()
    instrument = (body.get("instrument") or "").strip()
    if not apero_name:
        return jsonify(success=False,
                       error="Missing 'apero_name'"), 400
    if not _has_monitor_perm(perms, instrument):
        return jsonify(
            success=False,
            error=("Forbidden (need monitor.{0} or "
                   "manage.astrometrics)").format(
                       instrument or '<INSTRUMENT>'),
        ), 403
    author = user_info.get("username") or "unknown"
    astrom_root = str(_astrom_dir(app))
    try:
        new_path, old_status, entry = dra.set_status(
            astrom_root=astrom_root,
            apero_name=apero_name,
            new_status=dra.STATUS_VERIFIED,
            author=author,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 400
    closed = _close_verify_issues(
        app, entry.get("APERO_NAME") or apero_name,
        instrument, author,
    )
    return jsonify(
        success=True,
        apero_name=entry.get("APERO_NAME") or apero_name,
        status=dra.STATUS_VERIFIED,
        old_status=old_status,
        path=str(new_path),
        issues_closed=closed,
        payload=_build_payload(entry),
    )


# =============================================================
# SED + HR diagram (yaml-only, shared between both pages)
# =============================================================

def _shared_cache_dir(app, kind: str) -> Path:
    """Return the shared cache dir for a yaml-based artefact.

    The directory layout ``<cache_root>/_shared/<kind>/`` is keyed
    only by canonical APERO_NAME so the data-portal object page
    and the resolve target page hit the same cache entries.

    :param app: ARI application instance
    :param kind: artefact kind (``sed`` or ``hr``)
    :return: pathlib.Path (created on demand)
    """
    from apero_ri.core.plot_cache import (
        load_cache_config, resolve_cache_root,
    )
    base_dir = Path(
        app.args.data_dir or str(Path.home() / ".ari"))
    cfg = load_cache_config(base_dir)
    root = resolve_cache_root(base_dir, cfg)
    out = root / '_shared' / kind
    out.mkdir(parents=True, exist_ok=True)
    return out


def _safe_name(name: str) -> str:
    """Return a filename-safe variant of *name* for use as a key.

    :param name: str, the input name
    :return: str, slug suitable for a filename
    """
    return re.sub(r'[^A-Za-z0-9._+-]+', '_',
                  str(name)).strip('_') or 'unknown'


def _resolve_yaml_entry(app, name: str):
    """Resolve a name to its astrometric YAML entry.

    Tries the on-disk APERO astrometric store first; if no match is
    found, falls back to the per-user transient store populated by
    ``api_astrometrics_resolve_online_*`` so that SED / HR / finder
    plots still work for a freshly-resolved-online target that has
    not yet been persisted.

    :param app: ARI application instance
    :param name: str, target name (any alias)
    :return: dict yaml entry or None
    """
    from apero.core import drs_astrometrics as dra
    from apero_ri.core import transient_astrometrics as tastro
    try:
        entry = dra.find_by_name(str(_astrom_dir(app)), name)
    except Exception:  # noqa: BLE001
        entry = None
    if entry:
        return entry
    try:
        user_info = app._get_api_user()
    except Exception:  # noqa: BLE001
        user_info = None
    username = (user_info or {}).get('username') if user_info else None
    return tastro.get(username, name)


def api_astrometrics_sed(app):
    """Generate (or return cached) SED plot for a target.

    Query string parameters:
        name (required) - target name (any alias).
        _ts  (optional) - if present, force a regeneration.

    :param app: ARI application instance
    :return: Flask JSON response with ``success``, ``image``,
             ``apero_name``, ``error``.
    """
    _, err = _check_view_perm(app)
    if err is not None:
        return err
    name = (request.args.get('name') or '').strip()
    if not name:
        return jsonify(success=False,
                       error="Missing 'name'"), 400
    entry = _resolve_yaml_entry(app, name)
    if not entry:
        return jsonify(success=False,
                       error=f'No entry for {name!r}'), 404
    apero_name = entry.get('APERO_NAME') or name
    safe = _safe_name(apero_name)
    cdir = _shared_cache_dir(app, 'sed')
    cpath = cdir / f'{safe}.json'
    force = bool((request.args.get('_ts') or '').strip())
    if not force and cpath.exists():
        try:
            with cpath.open('r', encoding='utf-8') as fh:
                cached = _json.load(fh)
            cached['apero_name'] = apero_name
            return jsonify(**cached)
        except Exception:  # noqa: BLE001
            pass
    from apero_ri.plots.plot_obj_targetinfo import (
        build_sed_plot_json,
    )
    payload = build_sed_plot_json(entry)
    # Adapt builder payload {has_plot, script, div, message}
    # into the API contract {success, has_plot, script, div,
    # error, apero_name}.
    if payload.get('has_plot'):
        result = {
            'success': True,
            'has_plot': True,
            'script': payload.get('script', ''),
            'div': payload.get('div', ''),
            'message': payload.get('message', ''),
        }
    else:
        result = {
            'success': True,
            'has_plot': False,
            'message': payload.get('message', ''),
            'error': payload.get('message', ''),
        }
    result['apero_name'] = apero_name
    if result.get('success'):
        try:
            with cpath.open('w', encoding='utf-8') as fh:
                _json.dump(result, fh)
        except Exception:  # noqa: BLE001
            pass
    return jsonify(**result)


def api_astrometrics_hr(app):
    """Generate (or return cached) HR diagram for a target.

    Query string parameters:
        name (required) - target name (any alias).
        _ts  (optional) - if present, force a regeneration.

    :param app: ARI application instance
    :return: Flask JSON response with ``success``, ``image``,
             ``apero_name``, ``error``.
    """
    _, err = _check_view_perm(app)
    if err is not None:
        return err
    name = (request.args.get('name') or '').strip()
    if not name:
        return jsonify(success=False,
                       error="Missing 'name'"), 400
    entry = _resolve_yaml_entry(app, name)
    if not entry:
        return jsonify(success=False,
                       error=f'No entry for {name!r}'), 404
    apero_name = entry.get('APERO_NAME') or name
    safe = _safe_name(apero_name)
    cdir = _shared_cache_dir(app, 'hr')
    cpath = cdir / f'{safe}.json'
    force = bool((request.args.get('_ts') or '').strip())
    if not force and cpath.exists():
        try:
            with cpath.open('r', encoding='utf-8') as fh:
                cached = _json.load(fh)
            cached['apero_name'] = apero_name
            return jsonify(**cached)
        except Exception:  # noqa: BLE001
            pass
    from apero_ri.plots.plot_obj_targetinfo import (
        build_hr_plot_json,
        load_or_query_20pc_neighborhood,
    )
    # Use the same shared 20-pc Gaia backdrop cache the
    # object-page uses, so both pages render identical HR.
    try:
        base_dir = Path(
            app.args.data_dir or str(Path.home() / '.ari'))
        nb_cache = (base_dir / 'cache' / '_shared'
                    / 'gaia_20pc' / 'neighborhood.json')
        neighborhood = load_or_query_20pc_neighborhood(
            cache_path=str(nb_cache))
    except Exception:  # noqa: BLE001
        neighborhood = []
    payload = build_hr_plot_json(entry, neighborhood=neighborhood)
    if payload.get('has_plot'):
        result = {
            'success': True,
            'has_plot': True,
            'script': payload.get('script', ''),
            'div': payload.get('div', ''),
            'message': payload.get('message', ''),
        }
    else:
        result = {
            'success': True,
            'has_plot': False,
            'message': payload.get('message', ''),
            'error': payload.get('message', ''),
        }
    result['apero_name'] = apero_name
    if result.get('success'):
        try:
            with cpath.open('w', encoding='utf-8') as fh:
                _json.dump(result, fh)
        except Exception:  # noqa: BLE001
            pass
    return jsonify(**result)


# =============================================================
# Resolve online (SIMBAD / Vizier) - delegates to drs_astrometrics
# =============================================================

def api_astrometrics_resolve_online_by_name(app):
    """Query SIMBAD/Gaia/Vizier for a name and return parameters.

    Returns a yaml-shaped entry dict (NOT yet stored) so the
    front-end can offer to upload it as a new astrometric entry.

    The resolved entry is also placed in a per-user, time-limited
    in-memory store via
    :mod:`apero_ri.core.transient_astrometrics`, so that subsequent
    calls to ``/api/astrometrics/sed``, ``/hr-diagram`` etc. for
    the same name can render plots without the entry ever touching
    the on-disk APERO astrometric database.

    Query string parameters:
        name (required) - target name (any alias)

    :param app: ARI application instance
    :return: Flask JSON response with ``success``, ``apero_name``,
             ``entry`` (yaml-shaped), ``payload`` (target-info
             payload), ``error``.
    """
    from apero.core import drs_astrometrics as dra
    from apero_ri.core import transient_astrometrics as tastro

    user_info, err = _check_view_perm(app)
    if err is not None:
        return err
    name = (request.args.get('name') or '').strip()
    if not name:
        return jsonify(success=False,
                       error="Missing 'name'"), 400

    try:
        entry = _resolve_online_using_drs(name)
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500

    if not entry:
        return jsonify(success=True, apero_name=None,
                       entry=None, payload={"sections": []})

    # Stash in the per-user transient store so SED / HR / finder
    # endpoints can locate the entry by name on follow-up requests.
    username = (user_info or {}).get('username') if user_info else None
    tastro.put(username, name, entry)

    return jsonify(
        success=True,
        apero_name=entry.get('APERO_NAME')
        or entry.get('SIMBAD_NAME') or name,
        entry=entry,
        payload=_build_payload(entry),
        transient=True,
    )


def _resolve_online_using_drs(name):
    """Use ``drs_astrometrics`` low-level helpers to build a yaml entry.

    Calls ``_resolve_from_name`` (SIMBAD + Gaia + VizieR), then folds
    the result into a fully-shaped yaml dict via
    ``_update_yaml_from_simbad``.

    :param name: str, the target identifier
    :return: dict yaml entry or None
    """
    from apero.core import drs_astrometrics as dra

    simbad = dra._resolve_from_name(
        name,
        simbad_url=dra.SIMBAD_TAP,
        gaia_url=dra.GAIA_TAP,
        vizier_url=dra.VIZIER_TAP,
    )
    if simbad is None:
        return None
    entry = {
        'APERO_NAME': dra.clean_object(name),
        'ORIGINAL_NAME': name,
        'APERO_CLASS': 'STAR',
        'EPOCH': 2451545.0,
    }
    dra._full_resolve_schema(entry)
    dra._update_yaml_from_simbad(entry, simbad)
    return entry


def api_astrometrics_resolve_online_by_coords(app):
    """SIMBAD cone-search by sky coordinates.

    Query string parameters:
        ra      (required, deg)
        dec     (required, deg)
        radius  (optional, arcsec, default 60)

    :param app: ARI application instance
    :return: Flask JSON response with ``success``, ``matches``
             (list of candidate yaml-shaped entries), ``error``.
    """
    from apero.core import drs_astrometrics as dra
    from apero_ri.core import transient_astrometrics as tastro

    user_info, err = _check_view_perm(app)
    if err is not None:
        return err
    try:
        ra = float((request.args.get('ra') or '').strip())
        dec = float((request.args.get('dec') or '').strip())
    except ValueError:
        return jsonify(success=False,
                       error="Invalid 'ra' / 'dec'"), 400
    radius_arcsec = float(
        (request.args.get('radius') or '60').strip() or 60.0)
    # SIMBAD ADQL cone search via the basic_data table
    adql = (
        "SELECT TOP 25 main_id, ra, dec, "
        "pmra, pmdec, plx_value, rvz_radvel, sp_type, "
        "DISTANCE(POINT('ICRS', ra, dec), "
        f"POINT('ICRS', {ra}, {dec})) AS sep "
        "FROM basic "
        "WHERE 1=CONTAINS(POINT('ICRS', ra, dec), "
        f"CIRCLE('ICRS', {ra}, {dec}, "
        f"{radius_arcsec / 3600.0})) "
        "ORDER BY sep ASC")
    try:
        raw = dra._simbad_json(adql)
    except Exception as exc:  # noqa: BLE001
        return jsonify(success=False, error=str(exc)), 500
    rows = _tap_rows_from_json(raw)
    matches = []
    username = (user_info or {}).get('username') if user_info else None
    for row in (rows or [])[:25]:
        nm = row.get('main_id') or ''
        entry = _row_to_entry(row, nm)
        # transient-store every match so the user can render plots
        # for whichever they pick from the picker.
        try:
            tastro.put(username, nm, entry)
        except Exception:  # noqa: BLE001
            pass
        matches.append({
            'apero_name': entry.get('APERO_NAME'),
            'entry': entry,
            'payload': _build_payload(entry),
        })
    return jsonify(success=True, matches=matches, transient=True)


def _tap_rows_from_json(raw):
    """Convert a TAP JSON response (column/data form) to row dicts.

    :param raw: the parsed JSON from ``_simbad_json`` / ``_vizier_json``
    :return: list of dict rows (possibly empty)
    """
    if not isinstance(raw, dict):
        return []
    cols = raw.get('metadata') or raw.get('columns') or []
    names = []
    for c in cols:
        if isinstance(c, dict):
            names.append(c.get('name') or c.get('id'))
        else:
            names.append(str(c))
    data = raw.get('data') or []
    out = []
    for row in data:
        if not isinstance(row, list):
            continue
        out.append({names[i] if i < len(names) else f'col{i}':
                    row[i] for i in range(len(row))})
    return out


def _row_to_entry(row, name):
    """Convert a SIMBAD row dict to a yaml-shaped entry."""
    from apero.core import drs_astrometrics as dra

    out = {
        'APERO_NAME': str(name).upper().replace(' ', ''),
        'ORIGINAL_NAME': name,
        'SIMBAD_NAME': row.get('main_id'),
        'APERO_CLASS': 'STAR',
    }
    for src_k, dst_k, units in [
        ('ra', 'RA', 'deg'),
        ('dec', 'DEC', 'deg'),
        ('pmra', 'PMRA', 'mas/yr'),
        ('pmdec', 'PMDE', 'mas/yr'),
        ('plx_value', 'PLX', 'mas'),
        ('rvz_radvel', 'RV', 'km/s'),
    ]:
        v = dra._pf(row.get(src_k))
        if v is not None:
            out[dst_k] = {'value': v, 'source': 'SIMBAD',
                          'units': units}
    spt = row.get('sp_type')
    if spt:
        out['SPT'] = {'value': spt, 'source': 'SIMBAD'}
    out['EPOCH'] = 2457388.5
    out['ALIASES'] = [name]
    return out


