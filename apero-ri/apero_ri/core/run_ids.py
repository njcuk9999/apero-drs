#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persistent, instrument-scoped RUN ID metadata in APERO assets."""

import fcntl
import csv
import json
import os
import tempfile
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from typing import Iterator, Optional

import yaml


def _write_catalog(path: Path, records: dict, use_yaml: bool = False) -> None:
    """Atomically write catalog data.

    :param path: Target file path.
    :param records: RUN ID to metadata mapping.
    :param use_yaml: Write YAML rather than JSON.
    :return: None.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            if use_yaml:
                yaml.safe_dump(records, handle, sort_keys=True,
                               allow_unicode=True)
            else:
                json.dump(records, handle, indent=2, ensure_ascii=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def _catalog_transaction(root: Path, instrument: str) -> Iterator[dict]:
    """Lock, load, and synchronize asset and admin catalog files.

    :param root: ARI data directory.
    :param instrument: Validated instrument name.
    :return: Context manager yielding the editable catalog mapping.
    :raises ValueError: Invalid instrument name.
    """
    if not instrument or Path(instrument).name != instrument:
        raise ValueError('Invalid instrument')
    if instrument in {'.', '..'}:
        raise ValueError('Invalid instrument')
    directory = Path(root) / 'apero-assets' / 'run_ids'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{instrument.lower()}.json'
    admin_path = (Path(root) / 'admin' / 'run_ids'
                  / f'{instrument.lower()}_run_ids.yaml')
    with path.with_suffix('.lock').open('a', encoding='utf-8') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            with path.open(encoding='utf-8') as handle:
                records = json.load(handle)
        elif admin_path.exists():
            with admin_path.open(encoding='utf-8') as handle:
                records = yaml.safe_load(handle) or dict()
        else:
            records = dict()
        original = json.dumps(records, sort_keys=True)
        yield records
        if admin_path.exists():
            try:
                with admin_path.open(encoding='utf-8') as handle:
                    mirrored = yaml.safe_load(handle)
            except yaml.YAMLError:
                mirrored = None
        else:
            mirrored = None
        if not path.exists() or json.dumps(records, sort_keys=True) != original:
            _write_catalog(path, records)
        if mirrored != records:
            _write_catalog(admin_path, records, use_yaml=True)


def update_catalog(
    root: Path, instrument: str, seeds: Optional[dict] = None,
    run_id: Optional[str] = None, pi: str = '', comment: str = '',
    create: bool = False,
) -> dict:
    """Load/merge/edit a catalog under an exclusive filesystem lock.

    :param root: ARI data directory containing apero-assets.
    :param instrument: Validated instrument name.
    :param seeds: Discovered RUN ID to PI mapping; only new IDs are seeded.
    :param run_id: ID to create or edit, or None for a read/seed operation.
    :param pi: PI saved for the edited record, including an empty value.
    :param comment: Comment saved for the edited record.
    :param create: Reject existing IDs when True; require them otherwise.
    :return: RUN ID to metadata mapping.
    :raises ValueError: Invalid instrument/ID or duplicate/missing record.
    """
    with _catalog_transaction(root, instrument) as records:
        for seed_id, seed_pi in (seeds or dict()).items():
            seed_id = str(seed_id).strip()
            if seed_id and seed_id not in records:
                records[seed_id] = dict(pi=str(seed_pi or ''), comment='')
        if run_id is not None:
            run_id = run_id.strip()
            if not run_id or ',' in run_id or ';' in run_id:
                raise ValueError('Enter one non-empty RUN ID')
            if create and run_id in records:
                raise ValueError('RUN ID already exists')
            if not create and run_id not in records:
                raise ValueError('RUN ID does not exist')
            records[run_id] = dict(pi=pi.strip(), comment=comment.strip())
        return records


def import_csv(
    root: Path, instrument: str, content: str, duplicate_policy: str,
) -> dict:
    """Validate and merge a CSV into both catalog copies.

    :param root: ARI data directory.
    :param instrument: Validated instrument name.
    :param content: CSV text with RUN ID, PI, and COMMENT columns.
    :param duplicate_policy: reject, skip (first wins), or overwrite (last).
    :return: Added/updated/skipped counts and duplicate RUN IDs.
    :raises ValueError: Invalid CSV or rejected duplicate records.
    """
    if duplicate_policy not in {'reject', 'skip', 'overwrite'}:
        raise ValueError('Invalid duplicate policy')
    reader = csv.DictReader(StringIO(content.lstrip('\ufeff')), strict=True)
    try:
        headers = reader.fieldnames or []
        normalized = [name.strip().upper().replace('_', ' ')
                      for name in headers]
        if len(headers) != 3 or set(normalized) != {'RUN ID', 'PI', 'COMMENT'}:
            raise ValueError('CSV must have RUN ID, PI, COMMENT columns')
        column_map = dict(zip(normalized, headers))
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                message = f'Invalid column count on line {reader.line_num}'
                raise ValueError(message)
            values = {name: row[key].strip()
                      for name, key in column_map.items()}
            run_id = values['RUN ID']
            if not run_id or ',' in run_id or ';' in run_id:
                raise ValueError(f'Invalid RUN ID on line {reader.line_num}')
            rows.append((run_id, dict(pi=values['PI'],
                                     comment=values['COMMENT'])))
    except csv.Error as exc:
        raise ValueError(f'Invalid CSV: {exc}') from exc
    if not rows:
        raise ValueError('CSV contains no RUN IDs')
    with _catalog_transaction(root, instrument) as records:
        seen = set(records)
        duplicates = set()
        incoming = dict()
        skipped = 0
        for run_id, record in rows:
            if run_id in seen:
                duplicates.add(run_id)
                if duplicate_policy == 'skip':
                    skipped += 1
                    continue
            seen.add(run_id)
            incoming[run_id] = record
        if duplicates and duplicate_policy == 'reject':
            duplicate_text = ', '.join(sorted(duplicates))
            raise ValueError(f'Duplicate RUN IDs: {duplicate_text}')
        added = len(set(incoming) - set(records))
        updated = len(incoming) - added
        records.update(incoming)
        return dict(added=added, updated=updated, skipped=skipped,
                    duplicates=sorted(duplicates))


def record_label(run_id: str, record: dict) -> str:
    """Format one RUN ID with its optional PI and comment.

    :param run_id: RUN ID text.
    :param record: Metadata containing pi and comment.
    :return: Display label for science-group membership lists.
    """
    pi = record.get('pi', '')
    comment = record.get('comment', '')
    label = f'{run_id} ({pi})' if pi else run_id
    if pi and comment:
        label += f' [{comment}]'
    return label