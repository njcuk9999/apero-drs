#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Astrometric scanner.

Walks the on-disk astrometric YAMLs and the per-profile object
tables and creates issues for any inconsistency:

* ``astrometric-verify``       - YAMLs with ``STATUS=='pending'``
                                 (a moderator must verify them).
* ``astrometric-missing``      - OBJNAMEs that appear in an
                                 ``object_table.json`` but have no
                                 matching YAML (in any of
                                 ``verified/`` / ``pending/`` / flat
                                 layouts; ``rejected/`` is excluded).
* ``astrometrics-missing-required``
                              - YAMLs (verified or pending) that
                                lack one or more
                                :data:`REQUIRED_FIELDS_STAR`.

The scanner is idempotent: it uses :func:`create_issue`'s
``dedupe_key`` so re-running it does not create duplicates while
the underlying issue is still open.

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from apero_ri.core import issues as _issues


__NAME__ = 'apero_ri.core.astrometric_scanner'


# label values used for the auto-created issues (matched by the
# UI label-filter dropdown built in C5)
LABEL_VERIFY = 'astrometric-verify'
LABEL_MISSING = 'astrometric-missing'
LABEL_MISSING_REQ = 'astrometrics-missing-required'


def _safe_listdir(path: Path) -> List[str]:
    """``os.listdir`` that returns ``[]`` for missing dirs."""
    try:
        return os.listdir(path)
    except OSError:
        return []


def _load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    """Load a yaml mapping or return ``None`` on failure."""
    import yaml as _yaml
    try:
        with path.open('r', encoding='utf-8') as fh:
            data = _yaml.safe_load(fh)
        if isinstance(data, dict):
            return data
    except Exception as exc:  # noqa: BLE001
        warnings.warn(f'astrom scanner skipped {path}: {exc}')
    return None


def _iter_status_yamls(astrom_root: Path
                       ) -> List[Tuple[Path, str, Dict[str, Any]]]:
    """Yield ``(path, status, entry)`` for every astrometric yaml.

    Walks ``verified/``, ``pending/`` and the flat legacy layout (any
    yaml at the root is treated as ``verified`` for back-compat).
    The ``rejected/`` sub-dir is *not* walked - rejected entries are
    intentionally excluded from validation/missing checks.
    """
    out: List[Tuple[Path, str, Dict[str, Any]]] = []
    # status sub-dirs (excluding rejected/)
    for status in ('verified', 'pending'):
        sub = astrom_root / status
        for fname in _safe_listdir(sub):
            if not fname.endswith('.yaml'):
                continue
            fpath = sub / fname
            if not fpath.is_file():
                continue
            entry = _load_yaml(fpath)
            if entry is not None:
                out.append((fpath, status, entry))
    # flat legacy layout (root-level *.yaml)
    for fname in _safe_listdir(astrom_root):
        if not fname.endswith('.yaml'):
            continue
        fpath = astrom_root / fname
        if not fpath.is_file():
            continue
        entry = _load_yaml(fpath)
        if entry is not None:
            out.append((fpath, 'verified', entry))
    return out


def _collect_object_table_objnames(tasks_dir: Path
                                   ) -> Dict[str, set]:
    """Return ``{instrument: {OBJNAME, ...}}`` from object tables.

    Walks ``<tasks_dir>/<instrument>/<profile>/object_table.json``
    (new layout) and ``<tasks_dir>/<instrument>/object_table_<p>.json``
    (legacy layout).
    """
    result: Dict[str, set] = {}
    if not tasks_dir.is_dir():
        return result
    for inst_dir in tasks_dir.iterdir():
        if not inst_dir.is_dir():
            continue
        instrument = inst_dir.name
        names: set = result.setdefault(instrument, set())
        # new layout
        for prof_dir in inst_dir.iterdir():
            if not prof_dir.is_dir():
                continue
            jf = prof_dir / 'object_table.json'
            if jf.is_file():
                _add_objnames_from_json(jf, names)
        # legacy layout
        for jf in inst_dir.glob('object_table_*.json'):
            _add_objnames_from_json(jf, names)
    return result


def _add_objnames_from_json(jf: Path, names: set) -> None:
    """Append every ``OBJNAME`` from an object_table.json into a set."""
    try:
        with jf.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception:
        return
    for row in data.get('rows') or []:
        n = str(row.get('OBJNAME') or '').strip()
        if n:
            names.add(n)


def scan(data_dir: Path,
         astrom_root: Path,
         tasks_dir: Optional[Path] = None,
         created_by: str = 'astrometric-scanner',
         visibility: str = 'monitor',
         ) -> Dict[str, int]:
    """Walk the astrometric archive and create issues for anomalies.

    :param data_dir: Path, the ARI data dir (``~/.ari``)
    :param astrom_root: Path, the parent of
                        ``verified/``/``pending/``/``rejected/``
                        (typically ``~/.ari/apero-assets/astrometrics``)
    :param tasks_dir: Path, the ARI tasks dir (default
                      ``data_dir/tasks``); used to build the
                      object-table OBJNAME cross-check
    :param created_by: str, username to attribute auto-issues to
    :param visibility: str, visibility tier (default ``'monitor'``
                       so general users do not see scan noise)

    :return: dict with counts of issues created per label
    """
    # late import to avoid hard dep on apero core in unit tests
    from apero.core.drs_astrometrics import (
        REQUIRED_FIELDS_STAR, validate_required_fields,
        APERO_NAME_KEY,
    )
    if tasks_dir is None:
        tasks_dir = Path(data_dir) / 'tasks'
    counts = {LABEL_VERIFY: 0, LABEL_MISSING: 0,
              LABEL_MISSING_REQ: 0}
    seen_ids: Dict[str, set] = {LABEL_VERIFY: set(),
                                LABEL_MISSING: set(),
                                LABEL_MISSING_REQ: set()}
    # -------- per-yaml checks (verify / missing-required) --------
    yaml_apero_names: set = set()
    for fpath, status, entry in _iter_status_yamls(astrom_root):
        apero_name = str(entry.get(APERO_NAME_KEY) or fpath.stem)
        yaml_apero_names.add(apero_name)
        # missing-required (apply to verified + pending)
        missing = validate_required_fields(entry,
                                           required=REQUIRED_FIELDS_STAR)
        if missing:
            reason = (
                'YAML "{0}" (status={1}) is missing required '
                'field(s): {2}.'
            ).format(apero_name, status, ', '.join(missing))
            action = (
                'Edit the YAML and supply the missing field(s). '
                'Set NO_PM=True if no proper motion is known. '
                'Use a SpT->Teff relation if Teff is unknown. '
                'PLX may be omitted as a last resort.'
            )
            it = _issues.create_issue(
                data_dir=data_dir, kind='astrometric',
                reason=reason, created_by=created_by,
                apero_name=apero_name,
                field=','.join(missing),
                value=None,
                instrument=None,
                visibility=visibility,
                title='Missing required field(s) on {0}'.format(
                    apero_name),
                type_='missing required',
                label=LABEL_MISSING_REQ, action=action,
                dedupe_key='req:{0}'.format(apero_name),
            )
            seen_ids[LABEL_MISSING_REQ].add(it.get('id'))
        # astrometric-verify: any pending entry
        if status == 'pending':
            reason = (
                'Astrometric entry "{0}" is pending verification.'
            ).format(apero_name)
            action = (
                'Open the resolver page (or the object page) and '
                'click "Verify" once you have checked every field.'
            )
            it = _issues.create_issue(
                data_dir=data_dir, kind='astrometric',
                reason=reason, created_by=created_by,
                apero_name=apero_name, field=None, value=None,
                instrument=None, visibility=visibility,
                title='Verify astrometric entry: {0}'.format(
                    apero_name),
                type_='verify', label=LABEL_VERIFY, action=action,
                dedupe_key='verify:{0}'.format(apero_name),
            )
            seen_ids[LABEL_VERIFY].add(it.get('id'))
    # -------- object-table cross-check (missing entirely) --------
    objnames_by_inst = _collect_object_table_objnames(tasks_dir)
    # quick lower-cased lookup of yaml apero names
    yaml_lower = {n.lower() for n in yaml_apero_names}
    for instrument, objnames in objnames_by_inst.items():
        for name in objnames:
            if name.lower() in yaml_lower:
                continue
            reason = (
                'OBJNAME "{0}" appears in {1} object_table but no '
                'matching astrometric YAML was found.'
            ).format(name, instrument)
            action = (
                'Run apero_astrometrics with this object name to '
                'create a YAML, or open the resolver page in ARI '
                'and resolve+save it.'
            )
            it = _issues.create_issue(
                data_dir=data_dir, kind='astrometric',
                reason=reason, created_by=created_by,
                apero_name=name, field=None, value=None,
                instrument=instrument, visibility=visibility,
                title='Missing astrometric YAML: {0}'.format(name),
                type_='missing', label=LABEL_MISSING, action=action,
                dedupe_key='missing:{0}:{1}'.format(instrument,
                                                   name),
            )
            seen_ids[LABEL_MISSING].add(it.get('id'))
    for k in counts:
        counts[k] = len(seen_ids[k])
    return counts
