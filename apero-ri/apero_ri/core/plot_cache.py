#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Optional plot cache for APERO RI.

Stores pre-computed plot payloads (Bokeh JSON, base64 images) on disk so
that repeated page loads return instantly when the underlying database has
not changed.

The cache is **entirely optional**: when disabled (or absent) every API
endpoint falls through to generating plots on the fly as before.

Cache layout::

    <cache_root>/
        cache_config.yaml
        <INSTRUMENT>/
            <profile_id>/
                _meta.json
                object_plots/<objname>.json
                debug_plots/<objname>.json
                finder_charts/<objname>.json
                lbl_plots/<objname>__<lbl_file>.json
                qc_graphs/payload.json
"""

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from apero_ri.base import base
from apero_ri.core import secret_store

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
__NAME__ = "apero_ri.core.plot_cache"

_DEFAULT_CACHE_DIR_NAME = "cache"
_CONFIG_FILENAME = "cache_config.yaml"
_META_FILENAME = "_meta.json"
_TIMING_RESET_FILENAME = "_timing_reset.json"

# cache_config.yaml is read on every API call.  Cache it in-process with a
# short TTL so the admin UI can still update it within ~10 seconds.
_CFG_TTL: float = 10.0
_cfg_cache: Dict[str, Dict[str, Any]] = {}
_cfg_lock = threading.Lock()

# Section keys (used in _meta.json, admin page, and API integration)
CACHE_SECTIONS = [
    "object_plots",
    "debug_plots",
    "finder_charts",
    "lbl_plots",
    "qc_graphs",
]


# =========================================================================
# Configuration helpers
# =========================================================================
def _config_path(data_dir: Optional[Path] = None) -> Path:
    """Return the cache configuration path for a data directory."""
    base = Path(data_dir) if data_dir else secret_store.get_ari_dir()
    return base / _DEFAULT_CACHE_DIR_NAME / _CONFIG_FILENAME


def load_cache_config(data_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load cache configuration.  Returns defaults when file is absent.

    The result is cached in-process for _CFG_TTL seconds so repeated
    calls within the same request (or across rapid sequential requests)
    do not hit the file system more than once every few seconds.
    """
    key = str(data_dir) if data_dir else "__default__"
    now = time.monotonic()
    with _cfg_lock:
        entry = _cfg_cache.get(key)
        if entry is not None and now < entry["expires"]:
            return entry["cfg"]
    # Cache miss — read from disk outside the lock.
    path = _config_path(data_dir)
    defaults: Dict[str, Any] = {
        # On by default: first object views are slow (FITS reads), so
        # every later view should come from cache.
        "enabled": True,
        "cache_dir": "",  # empty → use default (<data_dir>/cache)
    }
    if path.exists():
        try:
            with open(path, "r") as f:
                cfg = yaml.safe_load(f) or {}
            defaults.update({k: v for k, v in cfg.items() if k in defaults})
        except Exception:
            pass
    with _cfg_lock:
        _cfg_cache[key] = {"expires": now + _CFG_TTL, "cfg": defaults}
    return defaults


def save_cache_config(
    cfg: Dict[str, Any], data_dir: Optional[Path] = None
) -> None:
    """Persist cache configuration to disk."""
    path = _config_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(dict(cfg), f, default_flow_style=False)
    # Invalidate the in-process config cache so the new value is seen
    # immediately by subsequent calls within this process.
    key = str(data_dir) if data_dir else "__default__"
    with _cfg_lock:
        _cfg_cache.pop(key, None)


def resolve_cache_root(
    data_dir: Optional[Path] = None, cfg: Optional[Dict[str, Any]] = None
) -> Path:
    """Return the effective cache root directory."""
    if cfg is None:
        cfg = load_cache_config(data_dir)
    custom = str(cfg.get("cache_dir", "") or "").strip()
    if custom:
        return Path(custom).expanduser().resolve()
    base = Path(data_dir) if data_dir else secret_store.get_ari_dir()
    return base / _DEFAULT_CACHE_DIR_NAME


def is_cache_enabled(
    data_dir: Optional[Path] = None, cfg: Optional[Dict[str, Any]] = None
) -> bool:
    """Return whether plot caching is enabled in the resolved config."""
    if cfg is None:
        cfg = load_cache_config(data_dir)
    return bool(cfg.get("enabled", False))


# =========================================================================
# Per-profile metadata (db fingerprint)
# =========================================================================
def _profile_dir(cache_root: Path, instrument: str, profile_id: str) -> Path:
    """Return the cache directory for one instrument profile."""
    return cache_root / instrument / profile_id


def _load_meta(profile_dir: Path) -> Dict[str, Any]:
    """Load profile cache metadata, or return an empty mapping on failure."""
    meta_path = profile_dir / _META_FILENAME
    if not meta_path.exists():
        return {}
    try:
        with open(meta_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_meta(profile_dir: Path, meta: Dict[str, Any]) -> None:
    """Persist cache metadata for one profile."""
    profile_dir.mkdir(parents=True, exist_ok=True)
    meta_path = profile_dir / _META_FILENAME
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)


def get_timing_reset_ts(profile_dir: Path) -> Optional[float]:
    """Return last timing-reset Unix timestamp, or None if never reset."""
    path = profile_dir / _TIMING_RESET_FILENAME
    if not path.exists():
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        ts = float(data.get("reset_at_ts", 0) or 0)
        return ts if ts > 0 else None
    except Exception:
        return None


def write_timing_reset(profile_dir: Path) -> None:
    """Record the current time as the timing-reset point for a profile."""
    profile_dir.mkdir(parents=True, exist_ok=True)
    path = profile_dir / _TIMING_RESET_FILENAME
    with open(path, "w") as f:
        json.dump(
            {
                "reset_at": datetime.now(timezone.utc).isoformat(),
                "reset_at_ts": time.time(),
            },
            f,
        )


def _db_fingerprint_matches(
    meta: Dict[str, Any], db_updates: Dict[str, str]
) -> bool:
    """Return True when the stored fingerprint matches *db_updates*."""
    stored = meta.get("db_updates", {})
    if not stored:
        return False
    return all(
        str(stored.get(k, "")).strip() == str(db_updates.get(k, "")).strip()
        for k in db_updates
    )


# =========================================================================
# Read / write individual cache entries
# =========================================================================
def _section_dir(
    cache_root: Path, instrument: str, profile_id: str, section: str
) -> Path:
    """Return the directory for one profile's cache section."""
    return _profile_dir(cache_root, instrument, profile_id) / section


def _safe_filename(name: str) -> str:
    """Sanitise an object name for use as a filename component."""
    safe = name.replace("/", "_").replace("\\", "_").replace("..", "_")
    if len(safe) > 200:
        safe = safe[:160] + "_" + hashlib.md5(name.encode()).hexdigest()[:12]
    return safe


def get_cached(
    cache_root: Path, instrument: str, profile_id: str, section: str, key: str
) -> Optional[Dict[str, Any]]:
    """Return a cached payload dict, or *None* if not present."""
    safe = _safe_filename(key)
    path = (
        _section_dir(cache_root, instrument, profile_id, section)
        / f"{safe}.json"
    )
    if not path.exists():
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def put_cached(
    cache_root: Path,
    instrument: str,
    profile_id: str,
    section: str,
    key: str,
    payload: Dict[str, Any],
    generation_time: float = 0.0,
) -> None:
    """Write a payload dict into the cache."""
    d = _section_dir(cache_root, instrument, profile_id, section)
    d.mkdir(parents=True, exist_ok=True)
    safe = _safe_filename(key)
    entry = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "generation_time_s": round(generation_time, 3),
        "payload": payload,
    }
    path = d / f"{safe}.json"
    with open(path, "w") as f:
        json.dump(entry, f)


# =========================================================================
# Invalidation
# =========================================================================
def invalidate_profile(
    cache_root: Path,
    instrument: str,
    profile_id: str,
    sections: Optional[List[str]] = None,
) -> int:
    """Delete cached entries for a profile.  Returns count of files removed."""
    pdir = _profile_dir(cache_root, instrument, profile_id)
    if not pdir.exists():
        return 0
    targets = sections or CACHE_SECTIONS
    removed = 0
    for sec in targets:
        sdir = pdir / sec
        if not sdir.is_dir():
            continue
        for f in sdir.iterdir():
            if f.is_file():
                f.unlink()
                removed += 1
    return removed


def invalidate_all(cache_root: Path) -> int:
    """Purge cache contents except configuration and return removed count."""
    if not cache_root.exists():
        return 0
    removed = 0
    for root, dirs, files in os.walk(str(cache_root), topdown=False):
        for fname in files:
            fp = Path(root) / fname
            if fp.name == _CONFIG_FILENAME:
                continue
            fp.unlink()
            removed += 1
        rp = Path(root)
        if rp != cache_root:
            try:
                rp.rmdir()
            except OSError:
                pass
    return removed


# =========================================================================
# Statistics / inventory for admin page
# =========================================================================
def _dir_stats(directory: Path) -> Tuple[int, int]:
    """Return (file_count, total_bytes) for a directory tree."""
    count = 0
    total = 0
    if not directory.exists():
        return count, total
    for root, _dirs, files in os.walk(str(directory)):
        for fname in files:
            fp = Path(root) / fname
            if fp.name == _CONFIG_FILENAME:
                continue
            try:
                total += fp.stat().st_size
                count += 1
            except OSError:
                pass
    return count, total


def _format_size(nbytes: int) -> str:
    """Format a byte count using a binary unit and one decimal place."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024  # type: ignore[assignment]
    return f"{nbytes:.1f} TB"


def cache_inventory(data_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Build a full inventory for the admin cache page.

    Returns::

        {
            'enabled': bool,
            'cache_dir': str,
            'total_files': int,
            'total_size': str,
            'total_size_bytes': int,
            'profiles': [
                {
                    'instrument': str,
                    'profile_id': str,
                    'sections': {
                        'object_plots': {'files': int, 'size': str,
                                         'size_bytes': int},
                        ...
                    },
                    'total_files': int,
                    'total_size': str,
                    'total_size_bytes': int,
                    'db_updates': dict,
                    'last_cached': str,
                },
                ...
            ],
        }
    """
    cfg = load_cache_config(data_dir)
    cache_root = resolve_cache_root(data_dir, cfg)
    enabled = is_cache_enabled(data_dir, cfg)

    result: Dict[str, Any] = {
        "enabled": enabled,
        "cache_dir": str(cache_root),
        "total_files": 0,
        "total_size": "0 B",
        "total_size_bytes": 0,
        "profiles": [],
    }

    if not cache_root.exists():
        return result

    grand_files = 0
    grand_bytes = 0

    for inst_dir in sorted(cache_root.iterdir()):
        if not inst_dir.is_dir():
            continue
        instrument = inst_dir.name
        for prof_dir in sorted(inst_dir.iterdir()):
            if not prof_dir.is_dir():
                continue
            profile_id = prof_dir.name
            meta = _load_meta(prof_dir)
            sections_info: Dict[str, Dict[str, Any]] = {}
            prof_files = 0
            prof_bytes = 0
            for sec in CACHE_SECTIONS:
                sdir = prof_dir / sec
                fc, fb = _dir_stats(sdir)
                sections_info[sec] = {
                    "files": fc,
                    "size": _format_size(fb),
                    "size_bytes": fb,
                }
                prof_files += fc
                prof_bytes += fb

            result["profiles"].append(
                {
                    "instrument": instrument,
                    "profile_id": profile_id,
                    "sections": sections_info,
                    "total_files": prof_files,
                    "total_size": _format_size(prof_bytes),
                    "total_size_bytes": prof_bytes,
                    "db_updates": meta.get("db_updates", {}),
                    "last_cached": meta.get("last_cached", ""),
                }
            )
            grand_files += prof_files
            grand_bytes += prof_bytes

    result["total_files"] = grand_files
    result["total_size"] = _format_size(grand_bytes)
    result["total_size_bytes"] = grand_bytes
    return result


# =========================================================================
# High-level helpers used by API endpoints
# =========================================================================
def check_and_serve(
    data_dir: Path,
    instrument: str,
    profile_id: str,
    section: str,
    key: str,
    aparams: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Try to serve *key* from cache; return None on miss or disabled.

    When *aparams* is provided, the stored db fingerprint is verified
    so that stale entries are not served.
    """
    cfg = load_cache_config(data_dir)
    if not cfg.get("enabled"):
        return None
    cache_root = resolve_cache_root(data_dir, cfg)
    pdir = _profile_dir(cache_root, instrument, profile_id)

    if aparams is not None:
        meta = _load_meta(pdir)
        stored = meta.get("db_updates", {})
        if not stored:
            return None
        current = aparams.get("database-update", {})
        if not isinstance(current, dict) or not current:
            return None
        if not _db_fingerprint_matches(meta, current):
            return None

    entry = get_cached(cache_root, instrument, profile_id, section, key)
    if entry is None:
        return None
    payload = entry.get("payload")
    if not isinstance(payload, dict):
        return payload
    # Include cache metadata so API callers can expose a reliable
    # "last updated" value without changing payload structure elsewhere.
    out = dict(payload)
    out["_cache_cached_at"] = entry.get("cached_at", "")
    out["_served_from_cache"] = True
    return out


# Plot groups the object page builds on first view; an object is "warm"
# once each has been cached under the current database fingerprint.
OBJECT_WARM_GROUPS = (
    "target_info",
    "spectrum",
    "ccf_rv",
    "ccf_profile",
    "time_series",
)


def _warm_marker(
    cache_root: Path, instrument: str, profile_id: str, objname: str,
    group: str,
) -> Path:
    """Return the marker file recording one cached object plot group.

    Markers live in the ``object_plots`` section so invalidating that
    section also makes the object cold again.
    """
    sdir = _section_dir(cache_root, instrument, profile_id, "object_plots")
    safe = _safe_filename(str(objname).lower())
    return sdir / f"_warm__{safe}__{group}.flag"


def mark_object_group_warm(
    cache_root: Path, instrument: str, profile_id: str, objname: str,
    group: str, signature: str,
) -> None:
    """Record that an object's plot group is cached for given inputs.

    :param cache_root: Path, resolved cache root
    :param instrument: str, instrument name
    :param profile_id: str, APERO profile id
    :param objname: str, object name
    :param group: str, object plot group (see ``OBJECT_WARM_GROUPS``)
    :param signature: str, ``object_plot_signature`` of the cached inputs

    :return: None
    """
    path = _warm_marker(cache_root, instrument, profile_id, objname, group)
    path.parent.mkdir(parents=True, exist_ok=True)
    # the marker only counts while the object inputs are unchanged
    path.write_text(signature)


def is_object_warm(
    data_dir: Path,
    instrument: str,
    profile_id: str,
    objname: str,
    signature: str,
) -> bool:
    """Return True when every first-view plot group of an object is cached.

    A group is warm only if its marker was written for the current
    ``object_plot_signature``, i.e. its cached plots will be served.

    :param data_dir: Path, ARI data directory
    :param instrument: str, instrument name
    :param profile_id: str, APERO profile id
    :param objname: str, object name
    :param signature: str, current ``object_plot_signature`` of the object

    :return: bool, True if the object page will load from cache
    """
    cfg = load_cache_config(data_dir)
    if not cfg.get("enabled"):
        return False
    cache_root = resolve_cache_root(data_dir, cfg)
    for group in OBJECT_WARM_GROUPS:
        marker = _warm_marker(cache_root, instrument, profile_id, objname,
                              group)
        try:
            if marker.read_text() != signature:
                return False
        except OSError:
            return False
    return True


def object_plot_signature(
    objects_dir: Path, objname: str, preset: Dict[str, Any],
) -> str:
    """Return a short hash of every input the object-page plots read.

    Covers the ARI version, the size and mtime of the object's JSON
    tables and ``object_table.json``, and the loaded instrument preset.
    A manifest restore keeps the publisher's mtime (``copy2``), so a
    republished table changes the signature and identical ones do not.
    FITS files read directly from ``PATH_RED`` are not covered.

    :param objects_dir: Path, profile ``objects`` task directory
    :param objname: str, object name
    :param preset: dict, loaded instrument preset used by plot builders

    :return: str, 12-character hex signature
    """
    hasher = hashlib.sha1(str(base.__version__).encode())
    # tables written by the object query (and the object table task)
    paths = [objects_dir / f"htable_{objname}.json"]
    paths += [objects_dir / f"ftable_{kind}_{objname}.json"
              for kind in ("ext", "tcorr", "ccf")]
    paths.append(objects_dir.parent / "object_table.json")
    for path in paths:
        try:
            info = path.stat()
            token = f"{path.name}:{info.st_size}:{info.st_mtime_ns}"
        except OSError:
            token = f"{path.name}:missing"
        hasher.update(token.encode())
    # hash the preset as loaded (it is cached in-process, not re-read)
    hasher.update(json.dumps(preset, sort_keys=True, default=str).encode())
    return hasher.hexdigest()[:12]


def value_signature(value: Any) -> str:
    """Return a short stable hash of a JSON-serialisable value.

    :param value: Any, value such as an astrometric entry dict or None

    :return: str, 12-character hex signature
    """
    blob = json.dumps(value, sort_keys=True, default=str).encode()
    return hashlib.sha1(blob).hexdigest()[:12]


def prune_cached(
    cache_root: Path, instrument: str, profile_id: str, section: str,
    prefix: str, keep_prefix: str,
) -> int:
    """Delete entries starting with *prefix* but not with *keep_prefix*.

    Used to drop an object's plot responses built from superseded inputs.

    :param cache_root: Path, resolved cache root
    :param instrument: str, instrument name
    :param profile_id: str, APERO profile id
    :param section: str, cache section such as ``object_plots``
    :param prefix: str, key prefix shared by all versions of the entry
    :param keep_prefix: str, key prefix of the current version

    :return: int, number of files removed
    """
    sdir = _section_dir(cache_root, instrument, profile_id, section)
    safe_prefix = _safe_filename(prefix)
    safe_keep = _safe_filename(keep_prefix)
    removed = 0
    try:
        names = [path.name for path in sdir.iterdir()]
    except OSError:
        return 0
    for name in names:
        if name.startswith(safe_prefix) and not name.startswith(safe_keep):
            try:
                (sdir / name).unlink()
                removed += 1
            except OSError:
                pass
    return removed


def generate_and_cache(
    data_dir: Path,
    instrument: str,
    profile_id: str,
    section: str,
    key: str,
    generator: callable,
    aparams: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call generator(), cache the result when enabled, and return it.

    *generator* is a zero-argument callable that returns a dict payload.
    """
    t0 = time.time()
    payload = generator()
    elapsed = time.time() - t0

    cfg = load_cache_config(data_dir)
    if cfg.get("enabled"):
        cache_root = resolve_cache_root(data_dir, cfg)
        put_cached(
            cache_root, instrument, profile_id, section, key, payload, elapsed
        )
        # Update profile meta with db fingerprint
        if aparams is not None:
            pdir = _profile_dir(cache_root, instrument, profile_id)
            meta = _load_meta(pdir)
            current = aparams.get("database-update", {})
            if isinstance(current, dict) and current:
                meta["db_updates"] = dict(current)
            meta["last_cached"] = datetime.now(timezone.utc).isoformat()
            _save_meta(pdir, meta)

    return payload


# =========================================================================
# Finder chart specialised cache (stores raw PNG files, not base64 in JSON)
# =========================================================================
def put_finder_cached(
    cache_root: Path,
    instrument: str,
    profile_id: str,
    key: str,
    payload: Dict[str, Any],
    generation_time: float = 0.0,
) -> None:
    """Cache a finder chart result as individual PNG files + small JSON.

    The *payload* dict must contain ``images`` (list of base64 strings),
    ``bands``, ``titles``, ``title``, ``error``, and ``success``.
    Each image is decoded from base64 and stored as a raw ``.png`` file,
    eliminating the ~33 % base64 overhead from the on-disk cache.
    """
    import base64 as _b64

    d = _section_dir(cache_root, instrument, profile_id, "finder_charts")
    d.mkdir(parents=True, exist_ok=True)
    safe = _safe_filename(key)

    images = payload.get("images", [])
    image_files: List[str] = []
    for idx, b64str in enumerate(images):
        fname = f"{safe}_{idx}.png"
        with open(d / fname, "wb") as fh:
            fh.write(_b64.b64decode(b64str))
        image_files.append(fname)

    meta_entry = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "generation_time_s": round(generation_time, 3),
        "payload": {
            "success": payload.get("success", True),
            "bands": payload.get("bands", []),
            "titles": payload.get("titles", []),
            "title": payload.get("title", ""),
            "error": payload.get("error", ""),
            "image_files": image_files,
        },
    }
    with open(d / f"{safe}.json", "w") as fh:
        json.dump(meta_entry, fh)


def get_finder_cached(
    cache_root: Path, instrument: str, profile_id: str, key: str
) -> Optional[Dict[str, Any]]:
    """Load a cached finder chart, returning the full API payload (with base64
    images) or *None* on miss.

    Raw PNG files are read and base64-encoded on the fly — this is fast
    (~1 ms per image) and keeps the on-disk cache compact.
    """
    import base64 as _b64

    safe = _safe_filename(key)
    d = _section_dir(cache_root, instrument, profile_id, "finder_charts")
    meta_path = d / f"{safe}.json"
    if not meta_path.exists():
        return None
    try:
        with open(meta_path, "r") as fh:
            entry = json.load(fh)
    except Exception:
        return None

    payload = entry.get("payload", {})
    image_files = payload.get("image_files", [])

    images: List[str] = []
    for fname in image_files:
        img_path = d / fname
        if not img_path.exists():
            return None  # incomplete cache — treat as miss
        with open(img_path, "rb") as fh:
            images.append(_b64.b64encode(fh.read()).decode("ascii"))

    return {
        "success": payload.get("success", True),
        "images": images,
        "bands": payload.get("bands", []),
        "titles": payload.get("titles", []),
        "title": payload.get("title", ""),
        "error": payload.get("error", ""),
    }
