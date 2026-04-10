#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Per-user and per-instrument data storage.

Manages YAML-backed links, markdown notes, calendar events and todo items
stored under ~/.ari/users/{username}/ (per-user) and
~/.ari/admin/instruments/ (per-instrument admin data).

Layout
------
~/.ari/users/{username}/
    links.yaml          {sections: [], types: {},
                        links: {section: {name: {url, type, description}}}}
    notes/
        {id}.md         YAML front-matter delimited markdown files
    calendar.yaml       {events: [{id, title, date, time,
                        color, category, recurrence, status}]}
    todo.yaml           {items: [{id, title, done, created, priority}]}

~/.ari/admin/instruments/
    {instrument}_calendar.yaml   {events: [...]}
    {instrument}_links.yaml      {sections: [], types: {}, links: {...}}
"""

import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.user_data"
# Optional markdown support – gracefully degrade if not installed
try:
    import markdown as _md_lib

    _MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]
    _HAS_MARKDOWN = True
except ImportError:
    _HAS_MARKDOWN = False

# =============================================================================
# Paths
# =============================================================================
ARI_DIR = Path.home() / ".ari"
USERS_DIR = ARI_DIR / "users"
INSTRUMENTS_DIR = ARI_DIR / "admin" / "instruments"


# =============================================================================
# Define functions
# =============================================================================
def set_ari_dir(path: Optional[str]) -> None:
    """Configure storage root (e.g. --data-dir) for user/admin data files."""
    global ARI_DIR, USERS_DIR, INSTRUMENTS_DIR
    base = Path(path).expanduser() if path else (Path.home() / ".ari")
    ARI_DIR = base
    USERS_DIR = ARI_DIR / "users"
    INSTRUMENTS_DIR = ARI_DIR / "admin" / "instruments"


def get_user_dir(username: str) -> Path:
    """Return (and create if necessary) the per-user data directory."""
    d = USERS_DIR / username
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_notes_dir(username: str) -> Path:
    """Return (and create) the per-user notes directory."""
    d = get_user_dir(username) / "notes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instruments_dir() -> Path:
    INSTRUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    return INSTRUMENTS_DIR


# =============================================================================
# YAML helpers
# =============================================================================
def _load_yaml(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if data is not None else default
    except Exception:
        return default


def _save_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def _new_id() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# Links
# =============================================================================
_LINKS_DEFAULT: Dict = {"sections": [], "types": {}, "links": {}}


def load_links(username: str) -> Dict:
    path = get_user_dir(username) / "links.yaml"
    data = _load_yaml(path, dict(_LINKS_DEFAULT))
    data.setdefault("sections", [])
    data.setdefault("types", {})
    data.setdefault("links", {})
    return data


def save_links(username: str, data: Dict) -> None:
    _save_yaml(get_user_dir(username) / "links.yaml", data)


def add_link(
    username: str,
    section: str,
    name: str,
    url: str,
    link_type: str = "",
    description: str = "",
) -> Dict:
    """Add a link and return the updated data."""
    data = load_links(username)
    if section not in data["sections"]:
        data["sections"].append(section)
    data["links"].setdefault(section, {})
    data["links"][section][name] = {
        "url": url,
        "type": link_type,
        "description": description,
    }
    save_links(username, data)
    return data


def update_link(
    username: str,
    section: str,
    name: str,
    new_name: str,
    url: str,
    link_type: str = "",
    description: str = "",
) -> Dict:
    data = load_links(username)
    section_links = data["links"].get(section, {})
    if name in section_links:
        del section_links[name]
    section_links[new_name] = {
        "url": url,
        "type": link_type,
        "description": description,
    }
    data["links"][section] = section_links
    save_links(username, data)
    return data


def remove_link(username: str, section: str, name: str) -> Dict:
    data = load_links(username)
    section_links = data["links"].get(section, {})
    section_links.pop(name, None)
    # Clean up empty section
    if not section_links:
        data["links"].pop(section, None)
        if section in data["sections"]:
            data["sections"].remove(section)
    else:
        data["links"][section] = section_links
    save_links(username, data)
    return data


def add_link_section(username: str, section: str) -> Dict:
    data = load_links(username)
    if section not in data["sections"]:
        data["sections"].append(section)
    save_links(username, data)
    return data


def remove_link_section(username: str, section: str) -> Dict:
    data = load_links(username)
    if section in data["sections"]:
        data["sections"].remove(section)
    data["links"].pop(section, None)
    save_links(username, data)
    return data


# =============================================================================
# Instrument links
# =============================================================================
def load_instrument_links(instrument: str) -> Dict:
    path = _instruments_dir() / f"{instrument}_links.yaml"
    data = _load_yaml(path, dict(_LINKS_DEFAULT))
    data.setdefault("sections", [])
    data.setdefault("types", {})
    data.setdefault("links", {})
    return data


def save_instrument_links(instrument: str, data: Dict) -> None:
    _save_yaml(_instruments_dir() / f"{instrument}_links.yaml", data)


def add_instrument_link(
    instrument: str,
    section: str,
    name: str,
    url: str,
    link_type: str = "",
    description: str = "",
) -> Dict:
    data = load_instrument_links(instrument)
    if section not in data["sections"]:
        data["sections"].append(section)
    data["links"].setdefault(section, {})
    data["links"][section][name] = {
        "url": url,
        "type": link_type,
        "description": description,
    }
    save_instrument_links(instrument, data)
    return data


def update_instrument_link(
    instrument: str,
    section: str,
    name: str,
    new_name: str,
    url: str,
    link_type: str = "",
    description: str = "",
) -> Dict:
    data = load_instrument_links(instrument)
    sec = data["links"].get(section, {})
    sec.pop(name, None)
    sec[new_name] = {"url": url, "type": link_type, "description": description}
    data["links"][section] = sec
    save_instrument_links(instrument, data)
    return data


def remove_instrument_link(instrument: str, section: str, name: str) -> Dict:
    data = load_instrument_links(instrument)
    sec = data["links"].get(section, {})
    sec.pop(name, None)
    if not sec:
        data["links"].pop(section, None)
        if section in data["sections"]:
            data["sections"].remove(section)
    else:
        data["links"][section] = sec
    save_instrument_links(instrument, data)
    return data


def add_instrument_link_section(instrument: str, section: str) -> Dict:
    data = load_instrument_links(instrument)
    if section not in data["sections"]:
        data["sections"].append(section)
    save_instrument_links(instrument, data)
    return data


def remove_instrument_link_section(instrument: str, section: str) -> Dict:
    data = load_instrument_links(instrument)
    if section in data["sections"]:
        data["sections"].remove(section)
    data["links"].pop(section, None)
    save_instrument_links(instrument, data)
    return data


def get_merged_links(username: str, instrument: str) -> Dict:
    """
    Return user links with instrument links appended as read-only section.
    """
    user_data = load_links(username)
    instr_data = load_instrument_links(instrument)
    # Deep-copy so we don't mutate stored data
    result = {
        "sections": list(user_data["sections"]),
        "types": dict(user_data["types"]),
        "links": {s: dict(v) for s, v in user_data["links"].items()},
        "instrument_sections": [],
    }
    for section in instr_data.get("sections", []):
        tag = f"[{instrument}] {section}"
        result["instrument_sections"].append(tag)
        result["links"][tag] = dict(instr_data["links"].get(section, {}))
    return result


# =============================================================================
# Pins
# =============================================================================
_PINS_DEFAULT: Dict = {"pins": []}


def _pins_path(username: str) -> Path:
    return get_user_dir(username) / "pins.yaml"


def load_pins(username: str) -> Dict:
    data = _load_yaml(_pins_path(username), dict(_PINS_DEFAULT))
    if isinstance(data, list):
        data = {"pins": data}
    if not isinstance(data, dict):
        data = dict(_PINS_DEFAULT)
    pins = data.get("pins", [])
    if not isinstance(pins, list):
        pins = []
    data["pins"] = pins
    return data


def save_pins(username: str, data: Dict) -> None:
    payload = data if isinstance(data, dict) else dict(_PINS_DEFAULT)
    pins = payload.get("pins", [])
    if not isinstance(pins, list):
        pins = []
    payload = {"pins": pins}
    _save_yaml(_pins_path(username), payload)


def list_pins(username: str) -> List[Dict]:
    return load_pins(username).get("pins", [])


def reorder_pins(username: str, ordered_ids: List[str]) -> List[Dict]:
    data = load_pins(username)
    pins = data.get("pins", [])
    id_map = {}
    for pin in pins:
        if isinstance(pin, dict):
            pin_id = str(pin.get("page_id", "")).strip()
            if pin_id:
                id_map[pin_id] = pin

    reordered = [id_map[i] for i in ordered_ids if i in id_map]
    seen = set(ordered_ids)
    for pin in pins:
        if not isinstance(pin, dict):
            continue
        pin_id = str(pin.get("page_id", "")).strip()
        if pin_id and pin_id not in seen:
            reordered.append(pin)

    data["pins"] = reordered
    save_pins(username, data)
    return reordered


# =============================================================================
# Object page section preferences
# =============================================================================
_OBJECT_SECTION_DEFAULT: Dict = {"pinned": []}


def _object_section_path(username: str) -> Path:
    return get_user_dir(username) / "object_section.yaml"


def load_object_section(username: str) -> Dict:
    data = _load_yaml(
        _object_section_path(username), dict(_OBJECT_SECTION_DEFAULT)
    )
    if not isinstance(data, dict):
        data = dict(_OBJECT_SECTION_DEFAULT)
    pinned = data.get("pinned", [])
    if not isinstance(pinned, list):
        pinned = []
    data["pinned"] = [str(x).strip() for x in pinned if str(x).strip()]
    return data


def save_object_section(username: str, data: Dict) -> None:
    payload = data if isinstance(data, dict) else dict(_OBJECT_SECTION_DEFAULT)
    pinned = payload.get("pinned", [])
    if not isinstance(pinned, list):
        pinned = []
    payload = {"pinned": [str(x).strip() for x in pinned if str(x).strip()]}
    _save_yaml(_object_section_path(username), payload)


def list_object_section_pins(username: str) -> List[str]:
    return load_object_section(username).get("pinned", [])


def reorder_object_section_pins(
    username: str, ordered_ids: List[str]
) -> List[str]:
    data = load_object_section(username)
    pins = data.get("pinned", [])
    pin_set = set(pins)

    reordered = []
    seen = set()
    for item in ordered_ids:
        sid = str(item).strip()
        if not sid or sid in seen or sid not in pin_set:
            continue
        reordered.append(sid)
        seen.add(sid)

    for sid in pins:
        if sid not in seen:
            reordered.append(sid)

    data["pinned"] = reordered
    save_object_section(username, data)
    return reordered


# =============================================================================
# Favourite objects per profile
# =============================================================================
_FAVOURITE_OBJECTS_DEFAULT: Dict = {"profiles": {}}


def _favourite_objects_path(username: str) -> Path:
    return get_user_dir(username) / "favourite_objects.yaml"


def _normalize_favourite_objects_data(data: Any) -> Dict:
    if not isinstance(data, dict):
        data = {}

    profiles_raw = data.get("profiles", {})
    if not isinstance(profiles_raw, dict):
        profiles_raw = {}

    profiles: Dict[str, Dict[str, Any]] = {}
    for profile_id, payload in profiles_raw.items():
        pid = str(profile_id).strip()
        if not pid:
            continue
        if not isinstance(payload, dict):
            payload = {}

        favourites_raw = payload.get("favourites", [])
        if not isinstance(favourites_raw, list):
            favourites_raw = []
        favourites: List[str] = []
        seen = set()
        for item in favourites_raw:
            objname = str(item).strip()
            if not objname or objname in seen:
                continue
            seen.add(objname)
            favourites.append(objname)

        last_object = str(payload.get("last_object", "")).strip()
        if not last_object:
            last_object = ""

        profiles[pid] = {
            "favourites": favourites,
            "last_object": last_object,
        }

    return {"profiles": profiles}


def load_favourite_objects(username: str) -> Dict:
    data = _load_yaml(
        _favourite_objects_path(username), dict(_FAVOURITE_OBJECTS_DEFAULT)
    )
    return _normalize_favourite_objects_data(data)


def save_favourite_objects(username: str, data: Dict) -> None:
    payload = _normalize_favourite_objects_data(data)
    _save_yaml(_favourite_objects_path(username), payload)


def get_profile_favourite_objects(username: str, profile_id: str) -> Dict:
    data = load_favourite_objects(username)
    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
    pid = str(profile_id).strip()
    payload = profiles.get(pid, {}) if pid else {}
    if not isinstance(payload, dict):
        payload = {}
    favourites = payload.get("favourites", [])
    if not isinstance(favourites, list):
        favourites = []
    last_object = str(payload.get("last_object", "")).strip()
    return {
        "profile_id": pid,
        "favourites": [str(x).strip() for x in favourites if str(x).strip()],
        "last_object": last_object,
    }


def save_profile_favourite_objects(
    username: str,
    profile_id: str,
    favourites: List[str],
    last_object: Optional[str] = None,
) -> Dict:
    pid = str(profile_id).strip()
    if not pid:
        return {"profile_id": "", "favourites": [], "last_object": ""}

    data = load_favourite_objects(username)
    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}

    clean_favourites: List[str] = []
    seen = set()
    for item in favourites if isinstance(favourites, list) else []:
        objname = str(item).strip()
        if not objname or objname in seen:
            continue
        seen.add(objname)
        clean_favourites.append(objname)

    existing = profiles.get(pid, {})
    if not isinstance(existing, dict):
        existing = {}
    existing_last_object = str(existing.get("last_object", "")).strip()
    if last_object is None:
        clean_last_object = existing_last_object
    else:
        clean_last_object = str(last_object).strip()

    profiles[pid] = {
        "favourites": clean_favourites,
        "last_object": clean_last_object,
    }
    data["profiles"] = profiles
    save_favourite_objects(username, data)
    return get_profile_favourite_objects(username, pid)


# =============================================================================
# Notes
# =============================================================================
_FM_SEP = "---"


def _parse_note_file(path: Path) -> Optional[Dict]:
    """Parse a YAML-frontmatter markdown file into a note dict."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip() != _FM_SEP:
        # No front-matter – use just content
        return {
            "id": path.stem,
            "title": path.stem,
            "color": "#ffd966",
            "created": "",
            "section": "",
            "content": text,
        }
    # Find closing separator
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.rstrip() == _FM_SEP:
            end = i
            break
    if end is None:
        return None
    try:
        fm = yaml.safe_load("".join(lines[1:end]))
    except Exception:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    content = "".join(lines[end + 1:])
    fm["content"] = content
    fm.setdefault("id", path.stem)
    return fm


def _note_to_file_text(note: Dict) -> str:
    """Serialise a note dict to YAML-frontmatter markdown text."""
    front = {
        "id": note.get("id", ""),
        "title": note.get("title", ""),
        "color": note.get("color", "#ffd966"),
        "created": note.get("created", ""),
        "section": note.get("section", ""),
    }
    content = note.get("content", "")
    return f"{_FM_SEP}\n{
        yaml.dump(
            front,
            default_flow_style=False,
            allow_unicode=True)}{_FM_SEP}\n{content}"


def load_notes(username: str) -> List[Dict]:
    """Return list of all notes for a user (sorted by created desc)."""
    notes_dir = get_notes_dir(username)
    notes = []
    for p in notes_dir.glob("*.md"):
        n = _parse_note_file(p)
        if n is not None:
            notes.append(n)
    return sorted(notes, key=lambda x: x.get("created", ""), reverse=True)


def get_note(username: str, note_id: str) -> Optional[Dict]:
    path = get_notes_dir(username) / f"{note_id}.md"
    if not path.exists():
        return None
    return _parse_note_file(path)


def save_note(username: str, note: Dict) -> Dict:
    """Create or update a note file.  Assigns id/created if missing."""
    if not note.get("id"):
        note["id"] = _new_id()
    if not note.get("created"):
        note["created"] = _now_iso()
    notes_dir = get_notes_dir(username)
    path = notes_dir / f"{note['id']}.md"
    path.write_text(_note_to_file_text(note), encoding="utf-8")
    return note


def delete_note(username: str, note_id: str) -> bool:
    path = get_notes_dir(username) / f"{note_id}.md"
    if path.exists():
        path.unlink()
        return True
    return False


def render_note_html(content: str) -> str:
    """Render markdown content to HTML."""
    if _HAS_MARKDOWN:
        return _md_lib.markdown(content, extensions=_MD_EXTENSIONS)
    # Minimal fallback: wrap paragraphs
    paragraphs = re.split(r"\n{2,}", content.strip())
    return "".join(f'<p>{p.replace(chr(10), "<br>")}</p>' for p in paragraphs)


# =============================================================================
# User preferences (timezone, etc.)
# =============================================================================
_PREFS_DEFAULT: Dict = {"timezone": "UTC"}


def _prefs_path(username: str) -> Path:
    return get_user_dir(username) / "prefs.yaml"


def load_user_prefs(username: str) -> Dict:
    data = _load_yaml(_prefs_path(username), dict(_PREFS_DEFAULT))
    if not isinstance(data, dict):
        data = dict(_PREFS_DEFAULT)
    data.setdefault("timezone", "UTC")
    return data


def save_user_prefs(username: str, data: Dict) -> None:
    current = load_user_prefs(username)
    current.update(data)
    _save_yaml(_prefs_path(username), current)


def get_user_timezone(username: str) -> str:
    return load_user_prefs(username).get("timezone", "UTC")


# =============================================================================
# Calendar
# =============================================================================
_CAL_DEFAULT: Dict = {"events": []}
_RECUR_VALUES = {"none", "daily", "weekly", "monthly", "yearly"}
_STATUS_VALUES = {"confirmed", "tentative"}


def _cal_path(username: str) -> Path:
    return get_user_dir(username) / "calendar.yaml"


def load_calendar(username: str) -> Dict:
    data = _load_yaml(_cal_path(username), dict(_CAL_DEFAULT))
    data.setdefault("events", [])
    return data


def save_calendar(username: str, data: Dict) -> None:
    _save_yaml(_cal_path(username), data)


def list_events(username: str) -> List[Dict]:
    return load_calendar(username).get("events", [])


def save_event(username: str, event: Dict) -> Dict:
    """Create or update a calendar event."""
    if not event.get("id"):
        event["id"] = _new_id()
    event.setdefault("recurrence", "none")
    event.setdefault("status", "confirmed")
    event.setdefault("color", "#4a90d9")
    event.setdefault("category", "personal")
    data = load_calendar(username)
    events = data["events"]
    for i, ev in enumerate(events):
        if ev.get("id") == event["id"]:
            events[i] = event
            break
    else:
        events.append(event)
    save_calendar(username, data)
    return event


def delete_event(username: str, event_id: str) -> bool:
    data = load_calendar(username)
    before = len(data["events"])
    data["events"] = [e for e in data["events"] if e.get("id") != event_id]
    if len(data["events"]) < before:
        save_calendar(username, data)
        return True
    return False


# Instrument calendar
def _instr_cal_path(instrument: str) -> Path:
    return _instruments_dir() / f"{instrument}_calendar.yaml"


def load_instrument_calendar(instrument: str) -> Dict:
    data = _load_yaml(_instr_cal_path(instrument), dict(_CAL_DEFAULT))
    data.setdefault("events", [])
    return data


def save_instrument_calendar(instrument: str, data: Dict) -> None:
    _save_yaml(_instr_cal_path(instrument), data)


def save_instrument_event(instrument: str, event: Dict) -> Dict:
    if not event.get("id"):
        event["id"] = _new_id()
    event.setdefault("recurrence", "none")
    event.setdefault("status", "confirmed")
    event.setdefault("color", "#7b5ea7")
    event.setdefault("category", "instrument")
    data = load_instrument_calendar(instrument)
    events = data["events"]
    for i, ev in enumerate(events):
        if ev.get("id") == event["id"]:
            events[i] = event
            break
    else:
        events.append(event)
    save_instrument_calendar(instrument, data)
    return event


def delete_instrument_event(instrument: str, event_id: str) -> bool:
    data = load_instrument_calendar(instrument)
    before = len(data["events"])
    data["events"] = [e for e in data["events"] if e.get("id") != event_id]
    if len(data["events"]) < before:
        save_instrument_calendar(instrument, data)
        return True
    return False


def get_merged_calendar(username: str, instrument: str) -> List[Dict]:
    """Merge personal and instrument events; instrument events tagged."""
    personal = list_events(username)
    instr = load_instrument_calendar(instrument).get("events", [])
    tagged = []
    for ev in instr:
        ev = dict(ev)
        ev["_source"] = instrument
        ev["category"] = "instrument"
        tagged.append(ev)
    return personal + tagged


# =============================================================================
# Todo
# =============================================================================
_TODO_DEFAULT: Dict = {
    "items": [],
    "projects": ["Unknown"],
    "tags": ["Unknown"],
}

_TODO_STATUS_VALUES = {"todo", "in-progress", "blocked", "done"}
_TODO_SIZE_VALUES = {"xs", "sm", "md", "lg", "xl"}


def _todo_path(username: str) -> Path:
    return get_user_dir(username) / "todo.yaml"


def _normalize_todo_labels(values: Any) -> List[str]:
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        values = []
    clean = []
    seen = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        clean.append(text)
    if not clean:
        clean = ["Unknown"]
    return clean


def _normalize_todo_priority(value: Any) -> int:
    text = str(value).strip().lower()
    if text in {"high", "urgent"}:
        return 2
    if text in {"normal", "medium"}:
        return 0
    if text in {"low"}:
        return -1
    try:
        return int(text)
    except Exception:
        return 0


def _normalize_todo_item(item: Dict) -> Dict:
    item_id = str(item.get("id", "")).strip() or _new_id()
    title = str(item.get("title", "")).strip() or "Untitled"

    status = str(item.get("status", "")).strip().lower()
    if status not in _TODO_STATUS_VALUES:
        status = "done" if bool(item.get("done", False)) else "todo"

    created = str(item.get("created", "")).strip() or _now_iso()
    date_added = str(item.get("date_added", "")).strip()
    if not date_added:
        date_added = created[:10] if len(created) >= 10 else _now_iso()[:10]

    size = str(item.get("size", "md")).strip().lower()
    if size not in _TODO_SIZE_VALUES:
        size = "md"

    return {
        "id": item_id,
        "title": title,
        "status": status,
        "size": size,
        "priority": _normalize_todo_priority(item.get("priority", 0)),
        "date_added": date_added,
        "created": created,
        "projects": _normalize_todo_labels(item.get("projects", [])),
        "tags": _normalize_todo_labels(item.get("tags", [])),
        "comments": str(item.get("comments", "") or ""),
        "link_url": str(item.get("link_url", "") or "").strip(),
        # Keep a legacy flag for compatibility with older UI logic.
        "done": status == "done",
    }


def load_todo(username: str) -> Dict:
    data = _load_yaml(_todo_path(username), dict(_TODO_DEFAULT))
    data.setdefault("items", [])
    data.setdefault("projects", ["Unknown"])
    data.setdefault("tags", ["Unknown"])

    norm_items = []
    projects = set(_normalize_todo_labels(data.get("projects", [])))
    tags = set(_normalize_todo_labels(data.get("tags", [])))
    for item in data.get("items", []):
        if not isinstance(item, dict):
            continue
        normalized = _normalize_todo_item(item)
        norm_items.append(normalized)
        projects.update(normalized.get("projects", []))
        tags.update(normalized.get("tags", []))

    data["items"] = norm_items
    data["projects"] = sorted(projects)
    data["tags"] = sorted(tags)
    return data


def save_todo(username: str, data: Dict) -> None:
    _save_yaml(_todo_path(username), data)


def list_todo_items(username: str) -> List[Dict]:
    return load_todo(username).get("items", [])


def get_todo_metadata(username: str) -> Dict:
    data = load_todo(username)
    return {
        "projects": _normalize_todo_labels(data.get("projects", [])),
        "tags": _normalize_todo_labels(data.get("tags", [])),
    }


def manage_todo_metadata(username: str, kind: str, op: str, value: str) -> Dict:
    data = load_todo(username)
    key = "projects" if kind == "projects" else "tags"
    current = set(_normalize_todo_labels(data.get(key, [])))
    text = str(value).strip()
    if not text:
        return get_todo_metadata(username)

    if op == "add":
        current.add(text)
    elif op == "remove" and text != "Unknown":
        current.discard(text)

    if not current:
        current.add("Unknown")

    data[key] = sorted(current)
    save_todo(username, data)
    return get_todo_metadata(username)


def save_todo_item(username: str, item: Dict) -> Dict:
    """Create or update a todo item."""
    normalized = _normalize_todo_item(item)

    data = load_todo(username)
    items = data["items"]
    for i, it in enumerate(items):
        if it.get("id") == normalized["id"]:
            # Preserve immutable creation metadata unless explicitly provided.
            normalized["created"] = it.get("created", normalized["created"])
            normalized["date_added"] = it.get(
                "date_added", normalized["date_added"]
            )
            items[i] = normalized
            break
    else:
        items.append(normalized)

    data["projects"] = sorted(
        set(_normalize_todo_labels(data.get("projects", [])))
        | set(normalized.get("projects", []))
    )
    data["tags"] = sorted(
        set(_normalize_todo_labels(data.get("tags", [])))
        | set(normalized.get("tags", []))
    )
    save_todo(username, data)
    return normalized


def toggle_todo(username: str, item_id: str) -> Optional[Dict]:
    data = load_todo(username)
    for item in data["items"]:
        if item.get("id") == item_id:
            done = item.get("status", "todo") == "done"
            item["status"] = "todo" if done else "done"
            item["done"] = item["status"] == "done"
            save_todo(username, data)
            return item
    return None


def delete_todo_item(username: str, item_id: str) -> bool:
    data = load_todo(username)
    before = len(data["items"])
    data["items"] = [it for it in data["items"] if it.get("id") != item_id]
    if len(data["items"]) < before:
        save_todo(username, data)
        return True
    return False


def reorder_todo_items(username: str, ordered_ids: List[str]) -> List[Dict]:
    """Reorder items to match ordered_ids list and return new item list."""
    data = load_todo(username)
    id_map = {it.get("id"): it for it in data["items"]}
    reordered = [id_map[i] for i in ordered_ids if i in id_map]
    # Append any items not in the list (safety)
    seen = set(ordered_ids)
    for it in data["items"]:
        if it.get("id") not in seen:
            reordered.append(it)
    data["items"] = reordered
    save_todo(username, data)
    return reordered


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
