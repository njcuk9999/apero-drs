"""Astrometrics edit history: append-only audit log + restore.

History is stored as JSON-Lines under
``<astrometrics_root>/.history/<safe_filename>.jsonl``.

Each line has the schema:

    {
      "id": "<filename>::<line_index>",   # convenience for diff/restore
      "timestamp": "YYYY-MM-DDTHH:MM:SS",
      "user": "<username>",
      "action": "create" | "edit" | "restore" | "rename" | "delete",
      "apero_name": "<APERO_NAME after the change>",
      "previous_apero_name": "<APERO_NAME before the change>",
      "fields": ["LIST", "OF", "CHANGED", "FIELDS"],
      "before": { ...full prior entry... } | null,
      "after":  { ...full new entry...   } | null
    }

Notes:
- Append-only by design — earlier edits are never modified, so audit
  is always recoverable.
- The visible "history" tab can compress / dedupe by field on the
  client side if desired; we keep the full log on disk.
"""
import datetime as _dt
import json
import os
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from flask import jsonify, request

from apero_ri.core.permissions import resolve_user_permissions


HISTORY_DIRNAME = ".history"


def _history_dir(astrom_root: Path) -> Path:
    """Return the on-disk path of the history sub-directory."""
    return Path(astrom_root) / HISTORY_DIRNAME


def _safe_history_filename(name: str) -> str:
    """Return a filesystem-safe filename for a given APERO name.

    Mirrors :func:`drs_astrometrics._safe_filename` but always uses a
    ``.jsonl`` extension. Defined locally so we don't drag the DRS in.
    """
    name = str(name or "").strip()
    if not name:
        return "_unknown.jsonl"
    safe = []
    for ch in name:
        if ch.isalnum() or ch in ("-", "_", "."):
            safe.append(ch)
        else:
            safe.append("_")
    return "".join(safe) + ".jsonl"


def _has_history_perm(perms: Iterable[str]) -> bool:
    """Return True if the caller may view/restore astrometrics history."""
    return "manage.astrometrics.history" in set(perms or [])


def _utcnow_iso() -> str:
    """Return the current UTC time as ISO-8601 (seconds precision)."""
    return _dt.datetime.utcnow().isoformat(timespec="seconds")


def _diff_field_keys(before, after) -> List[str]:
    """Return a sorted list of top-level keys that differ.

    :param before: dict or None
    :param after: dict or None
    """
    keys = set()
    if isinstance(before, dict):
        keys.update(before.keys())
    if isinstance(after, dict):
        keys.update(after.keys())
    out = []
    for k in sorted(keys):
        b = (before or {}).get(k) if isinstance(before, dict) else None
        a = (after or {}).get(k) if isinstance(after, dict) else None
        if b != a:
            out.append(k)
    return out


def append_history(
        astrom_root: Path,
        apero_name: str,
        user: str,
        action: str,
        before: Optional[dict],
        after: Optional[dict],
        previous_apero_name: Optional[str] = None,
) -> Optional[str]:
    """Append a single history record. Returns the entry id or None.

    Best-effort: any I/O error is swallowed so it never breaks a save.
    """
    try:
        astrom_root = Path(astrom_root)
        hdir = _history_dir(astrom_root)
        hdir.mkdir(parents=True, exist_ok=True)
        fname = _safe_history_filename(apero_name)
        fpath = hdir / fname
        # If the apero_name was renamed, also append a record under the
        # OLD filename so name-keyed lookups stay coherent.
        files_to_write = [fpath]
        if (previous_apero_name
                and previous_apero_name != apero_name):
            old_fpath = hdir / _safe_history_filename(
                previous_apero_name)
            if old_fpath != fpath:
                files_to_write.append(old_fpath)

        record = {
            "timestamp": _utcnow_iso(),
            "user": str(user or "unknown"),
            "action": str(action or "edit"),
            "apero_name": str(apero_name or ""),
            "previous_apero_name": (
                str(previous_apero_name)
                if previous_apero_name else ""
            ),
            "fields": _diff_field_keys(before, after),
            "before": before if isinstance(before, dict) else None,
            "after": after if isinstance(after, dict) else None,
        }

        first_id = None
        for fp in files_to_write:
            with fp.open("a", encoding="utf-8") as out:
                out.write(json.dumps(record, sort_keys=False))
                out.write("\n")
            try:
                line_count = sum(1 for _ in fp.open(
                    "r", encoding="utf-8"))
            except OSError:
                line_count = 0
            entry_id = "{0}::{1}".format(
                fp.name, max(line_count - 1, 0))
            if first_id is None:
                first_id = entry_id
        return first_id
    except Exception:  # noqa: BLE001
        return None


def _iter_history_files(astrom_root: Path) -> Iterable[Path]:
    """Yield every *.jsonl history file in the history dir."""
    hdir = _history_dir(astrom_root)
    if not hdir.is_dir():
        return
    for entry in os.listdir(hdir):
        if entry.endswith(".jsonl"):
            yield hdir / entry


def _read_history_file(
        fpath: Path,
) -> List[Tuple[int, dict]]:
    """Return [(line_index, record), ...] for a single file."""
    out = []
    try:
        with fpath.open("r", encoding="utf-8") as fp:
            for idx, raw in enumerate(fp):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                rec.setdefault("apero_name", "")
                rec.setdefault("user", "")
                rec.setdefault("timestamp", "")
                rec.setdefault("fields", [])
                rec["__file"] = fpath.name
                rec["__line"] = idx
                rec["id"] = "{0}::{1}".format(fpath.name, idx)
                out.append((idx, rec))
    except OSError:
        pass
    return out


def _build_summary(rec: dict) -> dict:
    """Strip heavy before/after blobs from a record for list views."""
    return {
        "id": rec.get("id"),
        "timestamp": rec.get("timestamp"),
        "user": rec.get("user"),
        "action": rec.get("action"),
        "apero_name": rec.get("apero_name"),
        "previous_apero_name": rec.get("previous_apero_name") or "",
        "fields": list(rec.get("fields") or []),
    }


# --------------------------------------------------------------------
# Flask endpoints
# --------------------------------------------------------------------
def _astrom_root(app) -> Path:
    base_dir = Path(
        app.args.data_dir or str(Path.home() / ".ari"))
    return base_dir / "apero-assets" / "astrometrics"


def _check_history_perm(app):
    """Authorise the caller. Returns ``(user_info, perms, error)``."""
    user_info = app._get_api_user()
    if not user_info:
        return None, set(), (
            jsonify(success=False, error="Login required"), 401)
    perms = resolve_user_permissions(
        user_info["groups"], app.ari_groups)
    if not _has_history_perm(perms):
        return user_info, perms, (
            jsonify(
                success=False,
                error=("Forbidden (need "
                       "manage.astrometrics.history)"),
            ),
            403,
        )
    return user_info, perms, None


def api_astrometrics_history_list(app):
    """List history entries (newest first) with optional filtering.

    Query parameters:
        ``q``        - case-insensitive substring filter on apero_name
        ``page``     - 1-based page number (default 1)
        ``per_page`` - one of 50, 100, 500 (default 50)
    """
    _, _, err = _check_history_perm(app)
    if err is not None:
        return err

    try:
        per_page = int(request.args.get("per_page", 50) or 50)
    except (TypeError, ValueError):
        per_page = 50
    if per_page not in (50, 100, 500):
        per_page = 50
    try:
        page = max(1, int(request.args.get("page", 1) or 1))
    except (TypeError, ValueError):
        page = 1
    q = (request.args.get("q") or "").strip().lower()

    astrom_root = _astrom_root(app)

    # Gather all records from all files; de-dupe by id to avoid the
    # rename-cross-write picking the same record twice.
    seen = set()
    all_recs = []
    for fpath in _iter_history_files(astrom_root):
        for _, rec in _read_history_file(fpath):
            rid = rec.get("id")
            if rid in seen:
                continue
            seen.add(rid)
            if q:
                name = str(rec.get("apero_name") or "").lower()
                prev = str(
                    rec.get("previous_apero_name") or "").lower()
                if q not in name and q not in prev:
                    continue
            all_recs.append(rec)

    # newest first
    all_recs.sort(key=lambda r: str(r.get("timestamp") or ""),
                  reverse=True)

    total = len(all_recs)
    start = (page - 1) * per_page
    end = start + per_page
    page_recs = all_recs[start:end]
    summaries = [_build_summary(r) for r in page_recs]

    return jsonify(
        success=True,
        rows=summaries,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if per_page else 1,
    )


def _parse_history_id(entry_id: str) -> Tuple[Optional[str],
                                              Optional[int]]:
    """Split ``"<filename>::<line_index>"`` into its parts."""
    if not entry_id or "::" not in entry_id:
        return None, None
    fname, _, idx = entry_id.partition("::")
    try:
        return fname, int(idx)
    except (TypeError, ValueError):
        return fname, None


def _load_history_record(astrom_root: Path,
                         entry_id: str) -> Optional[dict]:
    """Re-read a single history record by id."""
    fname, idx = _parse_history_id(entry_id)
    if fname is None or idx is None:
        return None
    if "/" in fname or "\\" in fname or fname.startswith("."):
        return None
    fpath = _history_dir(astrom_root) / fname
    if not fpath.is_file():
        return None
    for line_idx, rec in _read_history_file(fpath):
        if line_idx == idx:
            return rec
    return None


def api_astrometrics_history_get(app):
    """Return the full record (with before/after) for a single id.

    Body / query params: ``id``.
    """
    _, _, err = _check_history_perm(app)
    if err is not None:
        return err
    entry_id = (request.args.get("id")
                or (request.get_json(silent=True) or {}).get("id")
                or "").strip()
    if not entry_id:
        return jsonify(success=False, error="Missing 'id'"), 400
    rec = _load_history_record(_astrom_root(app), entry_id)
    if rec is None:
        return jsonify(success=False, error="Not found"), 404
    return jsonify(success=True, entry=rec)
