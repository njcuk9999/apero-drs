#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persistent, instrument-scoped RUN ID metadata in APERO assets."""

import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Optional


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
    if not instrument or Path(instrument).name != instrument:
        raise ValueError('Invalid instrument')
    if instrument in {'.', '..'}:
        raise ValueError('Invalid instrument')
    directory = Path(root) / 'apero-assets' / 'run_ids'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{instrument.lower()}.json'
    lock_path = path.with_suffix('.lock')
    with lock_path.open('a', encoding='utf-8') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            with path.open(encoding='utf-8') as handle:
                records = json.load(handle)
        else:
            records = dict()
        changed = False
        for seed_id, seed_pi in (seeds or dict()).items():
            seed_id = str(seed_id).strip()
            if seed_id and seed_id not in records:
                records[seed_id] = dict(pi=str(seed_pi or ''), comment='')
                changed = True
        if run_id is not None:
            run_id = run_id.strip()
            if not run_id or ',' in run_id or ';' in run_id:
                raise ValueError('Enter one non-empty RUN ID')
            if create and run_id in records:
                raise ValueError('RUN ID already exists')
            if not create and run_id not in records:
                raise ValueError('RUN ID does not exist')
            records[run_id] = dict(pi=pi.strip(), comment=comment.strip())
            changed = True
        if changed:
            descriptor, temporary = tempfile.mkstemp(dir=directory)
            try:
                with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
                    json.dump(records, handle, indent=2, ensure_ascii=True)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        return records


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