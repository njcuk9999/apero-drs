"""User favourite objects API helper functions for ARIApp."""

import json as _json
import re
from pathlib import Path
from typing import Dict, List, Optional

from apero_ri.core import user_data as ud
from flask import jsonify, request


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_object_table(base_dir: Path, instrument: str, profile_id: str):
    """Load object_table.json rows for alias resolution, or None."""
    tasks_dir = base_dir / "tasks" / instrument
    json_path = tasks_dir / profile_id / "object_table.json"
    if not json_path.exists():
        legacy = tasks_dir / f"object_table_{profile_id}.json"
        if legacy.exists():
            json_path = legacy
    if not json_path.exists():
        return None
    try:
        with open(json_path, encoding="utf-8") as fh:
            data = _json.load(fh)
        return data.get("rows", [])
    except Exception:
        return None


def _norm_variants(value: str):
    text = str(value or "").strip().lower()
    if not text:
        return set()
    variants = {
        re.sub(r"[^a-z0-9]+", "", text),
        re.sub(
            r"[^a-z0-9]+", "",
            text.replace("+", "p").replace("-", "m")
        ),
    }
    return {v for v in variants if v}


def _name_match_row(row: Dict, query: str) -> bool:
    qvars = _norm_variants(query)
    if not qvars:
        return True
    names = [str(row.get("OBJNAME", "") or "")]
    aliases = str(row.get("ALIASES", "") or "")
    if aliases:
        names.extend(
            part.strip() for part in aliases.split("|") if part.strip()
        )
    for name in names:
        nvars = _norm_variants(name)
        if any(qv in nv for qv in qvars for nv in nvars):
            return True
    return False


def _resolve_objname(
    rows: Optional[List[Dict]], query: str
) -> Optional[str]:
    """Resolve a user query to a canonical OBJNAME from the object table.

    Returns the canonical OBJNAME if exactly one match is found.
    Returns None if 0 or >1 matches (ambiguous).
    Also returns the exact match first (case-insensitive exact OBJNAME).
    """
    if rows is None:
        return None
    q = query.strip()
    if not q:
        return None
    # Exact match first
    for row in rows:
        if str(row.get("OBJNAME", "")).strip().upper() == q.upper():
            return str(row["OBJNAME"]).strip()
    # Alias match
    matches = [row for row in rows if _name_match_row(row, q)]
    if len(matches) == 1:
        return str(matches[0]["OBJNAME"]).strip()
    return None


def _find_object_in_sections(
    sections: List[Dict], objname: str
) -> Optional[str]:
    """Return section name containing objname, or None."""
    for sec in sections:
        for item in sec.get("items", []):
            if str(item.get("objname", "")).strip() == objname:
                return str(sec.get("name", "")).strip()
    return None


def _get_profile_info(app, profile_id: str, user_info: Dict):
    """Return (profile dict, instrument) or (None, None) if not found."""
    from apero_ri.core.auth import get_accessible_profiles
    accessible = get_accessible_profiles(user_info, app.ari_groups)
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            return prof, prof.get("instrument", "")
    return None, None


# ---------------------------------------------------------------------------
# Existing: reorder (now delegates to sections/save internally)
# ---------------------------------------------------------------------------

def api_user_favourite_objects_reorder(app):
    """Save explicit user-defined order for favourite objects."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    ordered = body.get("objnames", [])
    if not profile_id:
        return jsonify(success=False, error="profile_id is required"), 400
    if not isinstance(ordered, list):
        return jsonify(success=False, error="objnames must be a list"), 400

    clean_ordered = []
    seen: set = set()
    for item in ordered:
        objname = str(item).strip()
        if not objname or objname in seen:
            continue
        seen.add(objname)
        clean_ordered.append(objname)

    username = user_info["username"]
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    # Reorder items across sections by flattening default section only
    if sections:
        default_sec = next(
            (s for s in sections if s.get("name") == "default"), None
        )
        if default_sec:
            existing_names = {
                str(it.get("objname", "")).strip()
                for it in default_sec.get("items", [])
                if str(it.get("objname", "")).strip()
            }
            existing_items_map: Dict[str, Dict] = {
                str(it.get("objname", "")).strip(): it
                for it in default_sec.get("items", [])
                if str(it.get("objname", "")).strip()
            }
            reordered = [
                existing_items_map[n]
                for n in clean_ordered
                if n in existing_names
            ]
            for it in default_sec.get("items", []):
                n = str(it.get("objname", "")).strip()
                if n and n not in {
                    str(r.get("objname", "")).strip() for r in reordered
                }:
                    reordered.append(it)
            default_sec["items"] = reordered

    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=None
    )
    return jsonify(success=True, sections=updated.get("sections", []))


# ---------------------------------------------------------------------------
# New: save full sections structure
# ---------------------------------------------------------------------------

def api_user_favourite_objects_sections_save(app):
    """Save the full sections structure (for drag-reorder and collapse)."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    sections_raw = body.get("sections", [])
    if not profile_id:
        return jsonify(success=False, error="profile_id is required"), 400
    if not isinstance(sections_raw, list):
        return (
            jsonify(success=False, error="sections must be a list"), 400
        )

    # Normalize without removing existing nickname/note
    username = user_info["username"]
    existing = ud.get_profile_fav_sections(username, profile_id)
    existing_sections = existing.get("sections", [])
    existing_items_map: Dict[str, Dict] = {}
    for sec in existing_sections:
        for it in sec.get("items", []):
            n = str(it.get("objname", "")).strip()
            if n:
                existing_items_map[n] = it

    clean_sections: List[Dict] = []
    seen_names: set = set()
    for sec in sections_raw:
        if not isinstance(sec, dict):
            continue
        name = str(sec.get("name", "")).strip()
        if not name or name in seen_names:
            continue
        seen_names.add(name)
        collapsed = bool(sec.get("collapsed", False))
        raw_items = sec.get("items", [])
        if not isinstance(raw_items, list):
            raw_items = []
        items: List[Dict] = []
        seen_obj: set = set()
        for raw_it in raw_items:
            objname = (
                str(raw_it.get("objname", "")).strip()
                if isinstance(raw_it, dict)
                else str(raw_it).strip()
            )
            if not objname or objname in seen_obj:
                continue
            seen_obj.add(objname)
            existing_it = existing_items_map.get(objname, {})
            items.append({
                "objname": objname,
                "nickname": str(
                    existing_it.get("nickname", "")
                ).strip(),
                "note": str(existing_it.get("note", "")).strip(),
            })
        clean_sections.append(
            {"name": name, "collapsed": collapsed, "items": items}
        )

    if not any(s["name"] == "default" for s in clean_sections):
        clean_sections.insert(0, {
            "name": "default", "collapsed": False, "items": []
        })

    updated = ud.save_profile_fav_sections(
        username, profile_id, clean_sections, last_object=None
    )
    return jsonify(success=True, **updated)


# ---------------------------------------------------------------------------
# New: rename a section
# ---------------------------------------------------------------------------

def api_user_favourite_objects_sections_rename(app):
    """Rename a section."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    old_name = str(body.get("old_name", "")).strip()
    new_name = str(body.get("new_name", "")).strip()
    if not profile_id or not old_name or not new_name:
        return (
            jsonify(
                success=False,
                error="profile_id, old_name and new_name are required",
            ),
            400,
        )

    username = user_info["username"]
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    # Check name uniqueness
    existing_names = {s.get("name") for s in sections}
    if old_name not in existing_names:
        return (
            jsonify(success=False, error=f"Section '{old_name}' not found"),
            404,
        )
    if new_name != old_name and new_name in existing_names:
        return (
            jsonify(
                success=False,
                error=f"Section '{new_name}' already exists",
            ),
            400,
        )

    for sec in sections:
        if sec.get("name") == old_name:
            sec["name"] = new_name
            break

    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=None
    )
    return jsonify(success=True, **updated)


# ---------------------------------------------------------------------------
# New: delete a section
# ---------------------------------------------------------------------------

def api_user_favourite_objects_sections_delete(app):
    """Delete a section, moving its items to 'default' (or another)."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    section_name = str(body.get("section_name", "")).strip()
    move_to = str(body.get("move_to", "default")).strip() or "default"
    if not profile_id or not section_name:
        return (
            jsonify(
                success=False,
                error="profile_id and section_name are required",
            ),
            400,
        )
    if section_name == "default":
        return (
            jsonify(
                success=False,
                error="Cannot delete the 'default' section",
            ),
            400,
        )

    username = user_info["username"]
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    target_sec = next(
        (s for s in sections if s.get("name") == section_name), None
    )
    if target_sec is None:
        return (
            jsonify(
                success=False,
                error=f"Section '{section_name}' not found",
            ),
            404,
        )

    orphaned = target_sec.get("items", [])
    dest_sec = next(
        (s for s in sections if s.get("name") == move_to), None
    )
    if dest_sec is None:
        dest_sec = next(
            (s for s in sections if s.get("name") == "default"), None
        )
    if dest_sec is None and sections:
        dest_sec = sections[0]

    if dest_sec is not None and orphaned:
        existing_names_in_dest = {
            str(it.get("objname", "")).strip()
            for it in dest_sec.get("items", [])
        }
        for it in orphaned:
            n = str(it.get("objname", "")).strip()
            if n and n not in existing_names_in_dest:
                dest_sec["items"].append(it)
                existing_names_in_dest.add(n)

    new_sections = [s for s in sections if s.get("name") != section_name]
    if not any(s.get("name") == "default" for s in new_sections):
        new_sections.insert(
            0, {"name": "default", "collapsed": False, "items": []}
        )

    updated = ud.save_profile_fav_sections(
        username, profile_id, new_sections, last_object=None
    )
    return jsonify(success=True, **updated)


# ---------------------------------------------------------------------------
# New: save per-object nickname/note
# ---------------------------------------------------------------------------

def api_user_favourite_objects_meta_save(app):
    """Save nickname and note for a specific favourite object."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    objname = str(body.get("objname", "")).strip()
    nickname = str(body.get("nickname", "")).strip()
    note = str(body.get("note", "")).strip()
    if not profile_id or not objname:
        return (
            jsonify(
                success=False,
                error="profile_id and objname are required",
            ),
            400,
        )

    username = user_info["username"]
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    found = False
    for sec in sections:
        for item in sec.get("items", []):
            if str(item.get("objname", "")).strip() == objname:
                item["nickname"] = nickname
                item["note"] = note
                found = True
                break
        if found:
            break

    if not found:
        return (
            jsonify(
                success=False,
                error=f"Object '{objname}' not found in favourites",
            ),
            404,
        )

    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=None
    )
    return jsonify(success=True, **updated)


# ---------------------------------------------------------------------------
# New: add one object (with alias resolution)
# ---------------------------------------------------------------------------

def api_user_favourite_objects_add(app):
    """Add an object by name (resolves aliases) to a section."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    query = str(body.get("query", "")).strip()
    section_name = str(
        body.get("section_name", "default") or "default"
    ).strip()
    nickname = str(body.get("nickname", "")).strip()
    note = str(body.get("note", "")).strip()

    if not profile_id or not query:
        return (
            jsonify(
                success=False,
                error="profile_id and query are required",
            ),
            400,
        )

    username = user_info["username"]
    base_dir = Path(
        app.args.data_dir or str(Path.home() / ".ari")
    )
    prof, instrument = _get_profile_info(app, profile_id, user_info)
    if not prof:
        return jsonify(success=False, error="Profile not found"), 404

    rows = _load_object_table(base_dir, instrument, profile_id)
    if rows is not None:
        resolved = _resolve_objname(rows, query)
        if resolved is None:
            # Try exact match among all rows
            exact = [
                r for r in rows
                if str(r.get("OBJNAME", "")).strip().upper() == query.upper()
            ]
            if exact:
                resolved = str(exact[0]["OBJNAME"]).strip()
            else:
                # Return partial matches so the client can display options
                partial = [
                    str(r["OBJNAME"]).strip()
                    for r in rows
                    if _name_match_row(r, query)
                ]
                if not partial:
                    return jsonify(
                        success=False,
                        error=(
                            f"Object '{query}' not found in profile "
                            f"'{profile_id}'."
                        ),
                        candidates=[],
                    ), 404
                if len(partial) > 1:
                    return jsonify(
                        success=False,
                        error=f"Query '{query}' matches multiple objects.",
                        candidates=partial[:20],
                    ), 400
                resolved = partial[0]
        objname = resolved
    else:
        # No object table: treat query as literal APERO name
        objname = query

    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    # Check if already in any section
    existing_sec = _find_object_in_sections(sections, objname)
    if existing_sec is not None:
        return jsonify(
            success=False,
            error=(
                f"'{objname}' is already in section '{existing_sec}'."
            ),
            already_exists=True,
            section_name=existing_sec,
        ), 400

    # Find or create target section
    target = next(
        (s for s in sections if s.get("name") == section_name), None
    )
    if target is None:
        if section_name == "default":
            target = {
                "name": "default", "collapsed": False, "items": []
            }
            sections.insert(0, target)
        else:
            target = {
                "name": section_name, "collapsed": False, "items": []
            }
            sections.append(target)

    target["items"].append(
        {"objname": objname, "nickname": nickname, "note": note}
    )

    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=None
    )
    return jsonify(
        success=True, resolved_objname=objname, **updated
    )


# ---------------------------------------------------------------------------
# New: bulk add from a text file
# ---------------------------------------------------------------------------

def api_user_favourite_objects_add_bulk(app):
    """Bulk add objects from an uploaded text file (one name per line)."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = str(
        request.form.get("profile_id", "") or ""
    ).strip()
    section_name = str(
        request.form.get("section_name", "default") or "default"
    ).strip()

    if not profile_id:
        return (
            jsonify(success=False, error="profile_id is required"), 400
        )

    upload = request.files.get("file")
    if upload is None:
        return jsonify(success=False, error="No file uploaded"), 400

    # Read & decode file safely (max 1 MB)
    raw = upload.read(1024 * 1024)
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        text = raw.decode("latin-1", errors="replace")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return (
            jsonify(success=False, error="Uploaded file is empty"), 400
        )

    username = user_info["username"]
    base_dir = Path(
        app.args.data_dir or str(Path.home() / ".ari")
    )
    prof, instrument = _get_profile_info(app, profile_id, user_info)
    if not prof:
        return jsonify(success=False, error="Profile not found"), 404

    rows = _load_object_table(base_dir, instrument, profile_id)
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    target = next(
        (s for s in sections if s.get("name") == section_name), None
    )
    if target is None:
        if section_name == "default":
            target = {
                "name": "default", "collapsed": False, "items": []
            }
            sections.insert(0, target)
        else:
            target = {
                "name": section_name, "collapsed": False, "items": []
            }
            sections.append(target)

    results: Dict[str, List[str]] = {
        "added": [],
        "not_found": [],
        "already_exists": [],
        "ambiguous": [],
    }

    for line in lines:
        query = line.strip()
        if not query or query.startswith("#"):
            continue

        if rows is not None:
            # Try exact OBJNAME first
            exact_matches = [
                r for r in rows
                if str(r.get("OBJNAME", "")).strip().upper()
                == query.upper()
            ]
            if exact_matches:
                objname = str(exact_matches[0]["OBJNAME"]).strip()
            else:
                partial = [
                    str(r["OBJNAME"]).strip()
                    for r in rows
                    if _name_match_row(r, query)
                ]
                if not partial:
                    results["not_found"].append(query)
                    continue
                if len(partial) > 1:
                    results["ambiguous"].append(query)
                    continue
                objname = partial[0]
        else:
            objname = query

        existing_sec = _find_object_in_sections(sections, objname)
        if existing_sec is not None:
            results["already_exists"].append(objname)
            continue

        target["items"].append(
            {"objname": objname, "nickname": "", "note": ""}
        )
        results["added"].append(objname)

    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=None
    )
    return jsonify(success=True, results=results, **updated)

