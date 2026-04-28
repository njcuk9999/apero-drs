#!/usr/bin/env python3
"""Backfill ``FIRST_UPDATED`` / ``FIRST_AUTHOR`` from legacy NOTES.

Many astrometric yaml entries carry a provenance line of the form::

    Added on 2023-03-31 14:18:24.231 by nirps-client@maestria using
    drs_astrometrics.py

(written historically by ``apero/tools/module/database/
drs_astrometrics.py::AstroObj.stamp_note``).  The recent
``_stamp_metadata`` back-fill rewrote ``FIRST_UPDATED`` /
``FIRST_AUTHOR`` to the migration timestamp / user, losing the
original provenance.

This one-off script walks every ``*.yaml`` under the configured
astrometrics root (including ``verified/`` / ``pending/`` /
``rejected/`` sub-dirs) and, for every entry whose NOTES contains
the ``Added on ... by ... using ...`` pattern:

  * sets ``FIRST_UPDATED`` to the timestamp captured between
    ``Added on`` and ``by`` (overwrites whatever was there);
  * sets ``FIRST_AUTHOR`` to the user captured between ``by`` and
    ``using``;
  * rewrites NOTES to ``"added by drs_astrometrics.py"``, optionally
    appending any non-provenance text that surrounded the matched
    pattern.

Entries whose NOTES do not match the pattern are left untouched.

Run with ``--dry-run`` first to preview the changes.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover - import guard
    raise SystemExit(
        "PyYAML is required to run this migration script: {0}"
        .format(exc)
    )


# Pattern matches the historical stamp_note() output.  We keep the
# author / script tokens permissive (``\S+``) but the script name
# itself is anchored at "drs_astrometrics.py" or any non-space token
# so we don't accidentally swallow trailing free-form notes.
_NOTE_RE = re.compile(
    r"Added on\s+(?P<ts>\S+(?:\s+\S+)?)\s+by\s+"
    r"(?P<author>\S+)\s+using\s+(?P<script>\S+)"
)
NEW_NOTE = "added by drs_astrometrics.py"


def _is_null(value: Any) -> bool:
    """Mirror ``drs_astrometrics._is_null`` without importing apero."""
    if value is None:
        return True
    if isinstance(value, str):
        s = value.strip().lower()
        return s in ("", "null", "none", "nan")
    return False


def _iter_yaml_files(root: Path):
    """Yield every astrometric ``*.yaml`` under ``root``.

    Includes flat-layout entries directly under ``root`` and any
    entries inside the ``verified/`` / ``pending/`` / ``rejected/``
    sub-directories.  Hidden / lock files are skipped.
    """
    for sub in (".",) + ("verified", "pending", "rejected"):
        d = root if sub == "." else root / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.yaml")):
            if p.name.startswith("."):
                continue
            yield p


def _parse_note(notes: str) -> Optional[Tuple[str, str, str]]:
    """Return ``(timestamp, author, leftover_notes)`` or None.

    ``leftover_notes`` is whatever text in the original notes is
    *not* part of the matched ``Added on ... by ... using ...``
    fragment, with its surrounding whitespace collapsed.
    """
    if not isinstance(notes, str) or not notes.strip():
        return None
    m = _NOTE_RE.search(notes)
    if not m:
        return None
    ts = m.group("ts").strip()
    author = m.group("author").strip()
    # strip the matched fragment out of the original notes
    leftover = (notes[:m.start()] + notes[m.end():]).strip()
    # collapse runs of whitespace that the removal may have left
    leftover = re.sub(r"\s+", " ", leftover)
    return ts, author, leftover


def _migrate_entry(entry: Dict[str, Any]) -> bool:
    """Mutate ``entry`` in place; return True iff anything changed.

    Always overwrites ``FIRST_UPDATED`` / ``FIRST_AUTHOR`` when the
    NOTES line matches the legacy pattern - the whole point of the
    script is to recover the original provenance even when the
    fields were already populated by the recent back-fill.
    """
    if not isinstance(entry, dict):
        return False
    parsed = _parse_note(entry.get("NOTES", ""))
    if parsed is None:
        return False
    ts, author, leftover = parsed
    entry["FIRST_UPDATED"] = ts
    entry["FIRST_AUTHOR"] = author
    if leftover:
        entry["NOTES"] = NEW_NOTE + " " + leftover
    else:
        entry["NOTES"] = NEW_NOTE
    return True


def _atomic_write(path: Path, entry: Dict[str, Any]) -> None:
    """Write ``entry`` to ``path`` atomically (tmp + rename)."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as out:
        yaml.safe_dump(
            entry,
            out,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )
    os.replace(tmp, path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Back-fill FIRST_UPDATED / FIRST_AUTHOR from legacy "
            "NOTES provenance lines."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.home() / ".ari" / "apero-assets" / "astrometrics",
        help=(
            "Root of the astrometric yaml store "
            "(default: ~/.ari/apero-assets/astrometrics)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change but do not write any files.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print one line per inspected file (matched or not).",
    )
    args = parser.parse_args(argv)

    root = args.root.expanduser()
    if not root.is_dir():
        print("astrometric root does not exist: {0}".format(root),
              file=sys.stderr)
        return 2

    n_total = 0
    n_changed = 0
    n_skipped_no_match = 0
    n_errors = 0
    for fpath in _iter_yaml_files(root):
        n_total += 1
        try:
            with fpath.open("r", encoding="utf-8") as fh:
                entry = yaml.safe_load(fh)
        except Exception as exc:  # noqa: BLE001
            n_errors += 1
            print("[ERROR] {0}: cannot read ({1})".format(fpath, exc),
                  file=sys.stderr)
            continue
        if not isinstance(entry, dict):
            n_skipped_no_match += 1
            if args.verbose:
                print("[SKIP ] {0}: not a yaml mapping".format(fpath))
            continue
        before = (entry.get("NOTES"),
                  entry.get("FIRST_UPDATED"),
                  entry.get("FIRST_AUTHOR"))
        changed = _migrate_entry(entry)
        if not changed:
            n_skipped_no_match += 1
            if args.verbose:
                print("[SKIP ] {0}: notes do not match pattern"
                      .format(fpath))
            continue
        n_changed += 1
        after = (entry.get("NOTES"),
                 entry.get("FIRST_UPDATED"),
                 entry.get("FIRST_AUTHOR"))
        print(
            "[{tag}] {p}\n"
            "    NOTES         : {nb!r} -> {na!r}\n"
            "    FIRST_UPDATED : {ub!r} -> {ua!r}\n"
            "    FIRST_AUTHOR  : {ab!r} -> {aa!r}".format(
                tag=("DRY  " if args.dry_run else "WRITE"),
                p=fpath,
                nb=before[0], na=after[0],
                ub=before[1], ua=after[1],
                ab=before[2], aa=after[2],
            )
        )
        if args.dry_run:
            continue
        try:
            _atomic_write(fpath, entry)
        except Exception as exc:  # noqa: BLE001
            n_errors += 1
            print("[ERROR] {0}: write failed ({1})".format(fpath, exc),
                  file=sys.stderr)

    print("---")
    print("scanned  : {0}".format(n_total))
    print("changed  : {0}{1}".format(
        n_changed, " (dry-run)" if args.dry_run else ""))
    print("skipped  : {0}".format(n_skipped_no_match))
    print("errors   : {0}".format(n_errors))
    return 0 if n_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
