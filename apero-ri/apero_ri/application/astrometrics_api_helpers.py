"""Astrometrics API helpers."""
import json as _json
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
                       payload={"sections": []}, raw=None)

    return jsonify(
        success=True,
        apero_name=entry.get("APERO_NAME"),
        payload=_build_payload(entry),
        raw=entry,
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

    :param app: ARI application instance
    :param name: str, target name (any alias)
    :return: dict yaml entry or None
    """
    from apero.core import drs_astrometrics as dra
    try:
        return dra.find_by_name(str(_astrom_dir(app)), name)
    except Exception:  # noqa: BLE001
        return None


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

    Query string parameters:
        name (required) - target name (any alias)

    :param app: ARI application instance
    :return: Flask JSON response with ``success``, ``apero_name``,
             ``entry`` (yaml-shaped), ``payload`` (target-info
             payload), ``error``.
    """
    from apero.core import drs_astrometrics as dra

    _, err = _check_view_perm(app)
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

    return jsonify(
        success=True,
        apero_name=entry.get('APERO_NAME')
        or entry.get('SIMBAD_NAME') or name,
        entry=entry,
        payload=_build_payload(entry),
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

    _, err = _check_view_perm(app)
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
    for row in (rows or [])[:25]:
        nm = row.get('main_id') or ''
        entry = _row_to_entry(row, nm)
        matches.append({
            'apero_name': entry.get('APERO_NAME'),
            'entry': entry,
            'payload': _build_payload(entry),
        })
    return jsonify(success=True, matches=matches)


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


