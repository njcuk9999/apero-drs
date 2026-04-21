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
