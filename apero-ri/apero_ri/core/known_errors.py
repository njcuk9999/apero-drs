#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Known APERO errors store backed by per-error YAML files.

Source of truth:
    apero-ri/apero_ri/resources/monitor/known_errors/*.yaml
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import uuid

import yaml


__NAME__ = 'apero_ri.core.known_errors'


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def known_errors_dir() -> Path:
    dpath = (
        _repo_root()
        / 'apero-ri'
        / 'apero_ri'
        / 'resources'
        / 'monitor'
        / 'known_errors'
    )
    dpath.mkdir(parents=True, exist_ok=True)
    return dpath


def _slugify(text: str) -> str:
    raw = str(text or '').strip().lower()
    raw = re.sub(r'[^a-z0-9]+', '-', raw)
    raw = re.sub(r'-+', '-', raw)
    return raw.strip('-') or 'known-error'


def _safe(value: Any) -> str:
    return str(value or '').strip()


def _parse_date(value: str) -> str:
    text = _safe(value)
    if not text:
        return ''
    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            continue
    return text[:10]


def _normalize_row(payload: Dict[str, Any]) -> Dict[str, Any]:
    generic_error = _safe(payload.get('generic_error'))
    title = generic_error.splitlines()[0][:100] if generic_error else 'Known error'
    slug = _slugify(title)
    row_id = _safe(payload.get('id')) or str(uuid.uuid4())

    return {
        'id': row_id,
        'slug': slug,
        'date_reported': _parse_date(payload.get('date_reported', '')),
        'reported_by': _safe(payload.get('reported_by')),
        'instrument_mode': _safe(payload.get('instrument_mode')),
        'recipe': _safe(payload.get('recipe')),
        'action': _safe(payload.get('action')),
        'type': _safe(payload.get('type')),
        'error_code': _safe(payload.get('error_code')),
        'github_issue': _safe(payload.get('github_issue')),
        'generic_error': generic_error,
        'comments': _safe(payload.get('comments')),
        'full_example_error': _safe(payload.get('full_example_error')),
        'updated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
    }


def _yaml_path(error_id: str) -> Path:
    return known_errors_dir() / f'{error_id}.yaml'


def _load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return _normalize_row(data)


def list_known_errors() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in sorted(known_errors_dir().glob('*.yaml')):
        data = _load_yaml(path)
        if data is None:
            continue
        rows.append(data)

    rows.sort(
        key=lambda item: (
            item.get('date_reported', ''),
            item.get('instrument_mode', ''),
            item.get('recipe', ''),
        ),
        reverse=True,
    )
    return rows


def _write_row(row: Dict[str, Any]) -> Dict[str, Any]:
    norm = _normalize_row(row)
    path = _yaml_path(norm['id'])
    text = yaml.safe_dump(norm, sort_keys=False, allow_unicode=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(text, encoding='utf-8')
    tmp.replace(path)
    return norm


def create_known_error(payload: Dict[str, Any]) -> Dict[str, Any]:
    row = _normalize_row(payload)
    row['id'] = str(uuid.uuid4())
    out = _write_row(row)
    return out


def update_known_error(error_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    path = _yaml_path(error_id)
    if not path.exists():
        return None
    existing = _load_yaml(path)
    if existing is None:
        return None
    merged = dict(existing)
    merged.update(payload or {})
    merged['id'] = error_id
    out = _write_row(merged)
    return out


def delete_known_error(error_id: str) -> bool:
    path = _yaml_path(error_id)
    if not path.exists():
        return False
    path.unlink()
    return True
