#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download basket: per-user file collection and compilation helpers.

Each user has a basket stored in ~/.ari/users/{username}/basket.json.
Compiled downloads are stored in ~/.ari/download/{username}/{job_id}/.
Downloads are automatically expired after 24 hours.

Security:
- add_to_basket always checks that entry.kw_run_id is in accessible_run_ids.
- _compile_job re-checks run_id access before including any file.
- Path traversal is prevented on job_id inputs.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import tarfile
import threading
import uuid
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from apero_ri.base.base import BLOCK_KIND
from apero_ri.core import secret_store as ss


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.basket_funcs'
ARI_DIR = Path.home() / '.ari'
USERS_DIR = ARI_DIR / 'users'
DOWNLOADS_DIR = ARI_DIR / 'download'

_DOWNLOAD_EXPIRY_HOURS = 24
_DOWNLOAD_STORAGE_LIMIT_BYTES = 5 * 1024 ** 3


# =============================================================================
# Path helpers
# =============================================================================

_share_tokens_lock = threading.Lock()


# =============================================================================
# Define functions
# =============================================================================
def set_ari_dir(path: Path) -> None:
    """Re-point module-level path globals (mirrors auth.set_ari_dir)."""
    global ARI_DIR, USERS_DIR, DOWNLOADS_DIR
    ARI_DIR = Path(path)
    USERS_DIR = ARI_DIR / 'users'
    DOWNLOADS_DIR = ARI_DIR / 'download'


def _share_tokens_path() -> Path:
    env_ari_dir = (
        Path(os.environ.get('ARI_DIR', str(ARI_DIR)))
        .expanduser().resolve()
    )
    return ss.resolve_secret_file(
        'share_tokens.json',
        legacy_paths=[env_ari_dir / 'share_tokens.json',
                      ARI_DIR / 'share_tokens.json'],
    )


def _load_share_tokens() -> Dict[str, Any]:
    path = _share_tokens_path()
    if not path.exists():
        return {}
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_share_tokens(tokens: Dict[str, Any]) -> None:
    path = _share_tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(tokens, fh, indent=2)
    ss.protect_path(path, 0o600)


def create_share_token(username: str, job_id: str) -> str:
    """Create or return the existing share token for a job."""
    safe_id = _safe_job_id(job_id)
    if safe_id is None:
        raise ValueError('Invalid job id')
    meta = _load_job_meta(username, safe_id)
    if meta is None:
        raise ValueError('Job not found')
    if meta.get('status') != 'done':
        raise ValueError('Job is not yet complete')
    with _share_tokens_lock:
        tokens = _load_share_tokens()
        existing = str(meta.get('share_token', '') or '')
        if existing and existing in tokens:
            return existing
        token = str(uuid.uuid4())
        tokens[token] = {
            'username': username,
            'job_id': safe_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        meta['share_token'] = token
        _save_share_tokens(tokens)
        _save_job_meta(username, safe_id, meta)
    return token


def get_share_job(token: str) -> Optional[Dict[str, Any]]:
    """
    Return {'username', 'job_id', 'meta'} for a valid non-expired share token.
    """
    if not token or not re.match(r'^[0-9a-f-]{36}$', str(token)):
        return None
    tokens = _load_share_tokens()
    entry = tokens.get(str(token))
    if not entry:
        return None
    username = str(entry.get('username', '') or '')
    job_id = str(entry.get('job_id', '') or '')
    if not username or not job_id:
        return None
    meta = _load_job_meta(username, job_id)
    if meta is None:
        return None
    # Check whether the job itself has expired
    created_str = meta.get('created_at', '')
    if created_str:
        try:
            created_at = datetime.fromisoformat(str(created_str))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            cutoff = (datetime.now(timezone.utc)
                      - timedelta(hours=_DOWNLOAD_EXPIRY_HOURS))
            if created_at < cutoff:
                return None
        except Exception:
            pass
    return {'username': username, 'job_id': job_id, 'meta': meta}


# =============================================================================
# Basket I/O
# =============================================================================

def _basket_path(username: str) -> Path:
    return USERS_DIR / username / 'basket.json'


def load_basket(username: str) -> List[Dict[str, Any]]:
    """Return the user's basket entries (never raises)."""
    path = _basket_path(username)
    if not path.exists():
        return []
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        entries = data.get('entries', [])
        return [e for e in entries if isinstance(e, dict)]
    except Exception:
        return []


def save_basket(username: str, entries: List[Dict[str, Any]]) -> None:
    """Persist the user's basket entries."""
    path = _basket_path(username)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump({'version': 1, 'entries': entries}, fh, indent=2)


def add_to_basket(username: str,
                  new_entries: List[Dict[str, Any]],
                  accessible_run_ids: Set[str]) -> int:
    """
    Add entries to the basket after access-checking each row.

    Deduplication key: (profile_id, obs_dir, filename).
    Entries whose kw_run_id is not in accessible_run_ids are silently
    dropped — this is the primary security gate.

    Returns the count of newly-added entries.
    """
    existing = load_basket(username)
    existing_keys = {
        (
            str(e.get('profile_id', '') or ''),
            str(e.get('obs_dir', '') or ''),
            str(e.get('filename', '') or ''),
        )
        for e in existing
    }
    added = 0
    for entry in new_entries:
        run_id = str(entry.get('kw_run_id', '') or '').strip()
        if run_id not in accessible_run_ids:
            continue
        key = (
            str(entry.get('profile_id', '') or ''),
            str(entry.get('obs_dir', '') or ''),
            str(entry.get('filename', '') or ''),
        )
        if key in existing_keys:
            continue
        entry_copy = {k: v for k, v in entry.items()}
        entry_copy['id'] = entry_copy.get('id') or str(uuid.uuid4())
        entry_copy['added_at'] = datetime.now(timezone.utc).isoformat()
        existing.append(entry_copy)
        existing_keys.add(key)
        added += 1
    save_basket(username, existing)
    return added


def remove_from_basket(username: str, entry_ids: List[str]) -> int:
    """Remove basket entries by their id. Returns count removed."""
    id_set = set(entry_ids)
    entries = load_basket(username)
    before = len(entries)
    entries = [e for e in entries if e.get('id') not in id_set]
    save_basket(username, entries)
    return before - len(entries)


def clear_basket(username: str, profile_id: Optional[str] = None) -> int:
    """Clear all entries, or only entries for a specific profile_id."""
    entries = load_basket(username)
    before = len(entries)
    if profile_id:
        entries = [e for e in entries if e.get('profile_id') != profile_id]
    else:
        entries = []
    save_basket(username, entries)
    return before - len(entries)


# =============================================================================
# File path resolution
# =============================================================================

def _resolve_path(entry: Dict[str, Any],
                  profile_cfg: Dict[str, Any]) -> Optional[Path]:
    """
    Resolve the absolute path for a basket entry.

    Follows the same pattern as apero_object_query.object_query_headers:
        path_key = BLOCK_KIND[block_kind]
        base     = aparams['paths'][path_key]
        abspath  = Path(base) / obs_dir / filename
    """
    block_kind = str(entry.get('block_kind', '') or '')
    obs_dir = str(entry.get('obs_dir', '') or '')
    filename = str(entry.get('filename', '') or '')
    if not filename:
        return None
    # Basic traversal guard – obs_dir / filename come from user's basket JSON
    if '..' in obs_dir or '..' in filename:
        return None
    path_key = BLOCK_KIND.get(block_kind)
    if path_key is None:
        return None
    paths_cfg = profile_cfg.get('paths', {})
    if not isinstance(paths_cfg, dict):
        paths_cfg = {}
    base = str(
        paths_cfg.get(path_key)
        or profile_cfg.get(path_key)
        or ''
    ).strip()
    if not base:
        return None
    return Path(base) / obs_dir / filename


# =============================================================================
# Basket summary
# =============================================================================

def basket_summary(username: str,
                   profile_cfgs: Dict[str, Dict[str, Any]],
                   accessible_run_ids: Set[str],
                   profile_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Return a summary dict for the user's basket:
      {total_files, accessible_files, total_size_bytes, missing_files}

    profile_cfgs: {profile_id: profile_data_dict}
    accessible_run_ids: the logged-in user's allowed run_ids (security gate)
    """
    entries = load_basket(username)
    if profile_id:
        entries = [
            e for e in entries
            if str(e.get('profile_id', '') or '') == str(profile_id)
        ]
    total = len(entries)
    accessible = 0
    total_size = 0
    missing = 0
    for entry in entries:
        run_id = str(entry.get('kw_run_id', '') or '').strip()
        if run_id not in accessible_run_ids:
            continue
        accessible += 1
        cfg = profile_cfgs.get(str(entry.get('profile_id', '') or ''), {})
        path = _resolve_path(entry, cfg)
        if path and path.is_file():
            total_size += path.stat().st_size
        else:
            missing += 1
    return {
        'total_files': total,
        'accessible_files': accessible,
        'total_size_bytes': total_size,
        'missing_files': missing,
    }


# =============================================================================
# Download job management
# =============================================================================

def _jobs_dir(username: str) -> Path:
    new_dir = DOWNLOADS_DIR / username
    legacy_dir = USERS_DIR / username / 'downloads'

    # One-way migration to keep existing jobs visible after path move.
    if legacy_dir.exists():
        new_dir.mkdir(parents=True, exist_ok=True)
        for child in legacy_dir.iterdir():
            dest = new_dir / child.name
            if dest.exists():
                continue
            try:
                shutil.move(str(child), str(dest))
            except Exception:
                continue
        try:
            legacy_dir.rmdir()
        except Exception:
            pass

    new_dir.mkdir(parents=True, exist_ok=True)
    return new_dir


def _job_meta_path(username: str, job_id: str) -> Path:
    return _jobs_dir(username) / job_id / 'meta.json'


def _load_job_meta(username: str, job_id: str) -> Optional[Dict[str, Any]]:
    path = _job_meta_path(username, job_id)
    if not path.exists():
        return None
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return None


def _save_job_meta(username: str, job_id: str,
                   meta: Dict[str, Any]) -> None:
    path = _job_meta_path(username, job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=2)


def _safe_job_id(job_id: str) -> Optional[str]:
    """Return the sanitised job_id, or None if it looks malicious."""
    safe = Path(job_id).name
    if safe != job_id or '/' in job_id or '..' in job_id or not safe:
        return None
    return safe


def create_download_job(username: str,
                        entries: List[Dict[str, Any]],
                        profile_cfgs: Dict[str, Dict[str, Any]],
                        accessible_run_ids: Set[str],
                        fmt: str = 'zip',
                        chunk_size_gb: Optional[float] = None,
                        email_on_done: bool = False,
                        user_email: str = '',
                        profile_id: str = '') -> str:
    """
    Start a background download compilation job. Returns job_id.

    fmt: 'zip' or 'tar.gz'
    chunk_size_gb: if set, split output into ~chunk_size_gb GB chunks.
    profile_id: used to generate a descriptive archive filename.
    """
    fmt = fmt if fmt in ('zip', 'tar.gz', 'native') else 'zip'
    job_id = str(uuid.uuid4())
    meta: Dict[str, Any] = {
        'job_id': job_id,
        'status': 'pending',
        'fmt': fmt,
        'profile_id': profile_id,
        'chunk_size_gb': chunk_size_gb,
        'email_on_done': email_on_done,
        'user_email': user_email,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'completed_at': None,
        'error': None,
        'chunks': [],
        'total_size_bytes': 0,
        'entry_count': 0,
        'accessible_count': 0,
        'no_files': False,
    }
    _save_job_meta(username, job_id, meta)

    t = threading.Thread(
        target=_compile_job,
        args=(username, job_id, entries, profile_cfgs,
              accessible_run_ids, fmt, chunk_size_gb,
              email_on_done, user_email, profile_id),
        daemon=True,
    )
    t.start()
    return job_id


def get_job_status(username: str, job_id: str) -> Optional[Dict[str, Any]]:
    """Return job metadata dict, or None if not found / invalid id."""
    safe_id = _safe_job_id(job_id)
    if safe_id is None:
        return None
    return _load_job_meta(username, safe_id)


def get_job_chunk_path(username: str, job_id: str,
                       chunk_idx: int) -> Optional[Path]:
    """
    Return Path to a compiled chunk file if the job is done and it exists.
    """
    safe_id = _safe_job_id(job_id)
    if safe_id is None:
        return None
    meta = _load_job_meta(username, safe_id)
    if not meta or meta.get('status') != 'done':
        return None
    chunks = meta.get('chunks', [])
    if chunk_idx < 0 or chunk_idx >= len(chunks):
        return None
    p = Path(chunks[chunk_idx].get('path', ''))
    if not p.is_file():
        return None
    return p


def list_recent_jobs(username: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Return recent download jobs for the user, newest first."""
    jobs_dir = _jobs_dir(username)
    if not jobs_dir.exists():
        return []
    metas = []
    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        meta = _load_job_meta(username, job_dir.name)
        if meta:
            metas.append(meta)
    metas.sort(
        key=lambda m: m.get('created_at', ''),
        reverse=True,
    )
    return metas[:limit]


def get_downloads_storage_limit_bytes() -> int:
    """Return max allowed compiled-download storage per user."""
    return _DOWNLOAD_STORAGE_LIMIT_BYTES


def get_downloads_usage(username: str) -> Dict[str, int]:
    """Return compiled-download disk usage for a user."""
    jobs_dir = _jobs_dir(username)
    if not jobs_dir.exists():
        return {'total_bytes': 0, 'job_count': 0, 'file_count': 0}

    total_bytes = 0
    file_count = 0
    job_count = 0
    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        meta = _load_job_meta(username, job_dir.name)
        if meta is None:
            continue
        job_count += 1
        chunks = meta.get('chunks', [])
        for chunk in chunks:
            p = Path(str(chunk.get('path', '') or ''))
            if p.is_file():
                try:
                    total_bytes += p.stat().st_size
                    file_count += 1
                except Exception:
                    pass
    return {
        'total_bytes': int(total_bytes),
        'job_count': int(job_count),
        'file_count': int(file_count),
    }


def remove_download_job(username: str, job_id: str) -> Dict[str, Any]:
    """Remove one compiled download job directory for a user."""
    safe_id = _safe_job_id(job_id)
    if safe_id is None:
        return {'success': False, 'error': 'Invalid job id'}

    meta = _load_job_meta(username, safe_id)
    if meta is None:
        return {'success': False, 'error': 'Job not found'}

    status = str(meta.get('status', '') or '').lower()
    if status in ('pending', 'running'):
        return {'success': False, 'error': 'Cannot remove a running job'}

    job_dir = _jobs_dir(username) / safe_id
    try:
        shutil.rmtree(str(job_dir), ignore_errors=False)
    except FileNotFoundError:
        pass
    except Exception as exc:
        return {'success': False, 'error': str(exc)}
    return {'success': True, 'removed': 1}


def clear_download_jobs(username: str) -> Dict[str, int]:
    """Remove all completed/failed job directories for a user."""
    jobs_dir = _jobs_dir(username)
    if not jobs_dir.exists():
        return {'removed': 0, 'skipped': 0}

    removed = 0
    skipped = 0
    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        meta = _load_job_meta(username, job_dir.name)
        if meta is None:
            continue
        status = str(meta.get('status', '') or '').lower()
        if status in ('pending', 'running'):
            skipped += 1
            continue
        try:
            shutil.rmtree(str(job_dir), ignore_errors=False)
            removed += 1
        except Exception:
            skipped += 1
    return {'removed': removed, 'skipped': skipped}


def _compile_job(username: str,
                 job_id: str,
                 entries: List[Dict[str, Any]],
                 profile_cfgs: Dict[str, Dict[str, Any]],
                 accessible_run_ids: Set[str],
                 fmt: str,
                 chunk_size_gb: Optional[float],
                 email_on_done: bool,
                 user_email: str,
                 profile_id: str = '') -> None:
    """Background thread: build zip/tar.gz archive(s) of accessible files."""
    meta = _load_job_meta(username, job_id) or {}
    meta['status'] = 'running'
    _save_job_meta(username, job_id, meta)

    job_dir = _jobs_dir(username) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Security: re-verify run_id access for every entry
        accessible = [
            e for e in entries
            if str(e.get('kw_run_id', '') or '').strip() in accessible_run_ids
        ]
        meta['entry_count'] = len(entries)
        meta['accessible_count'] = len(accessible)

        # Resolve absolute paths and filter to files that exist
        file_pairs: List[tuple] = []  # (src_path, arc_name)
        for e in accessible:
            cfg = profile_cfgs.get(str(e.get('profile_id', '') or ''), {})
            path = _resolve_path(e, cfg)
            if path and path.is_file():
                arc_name = '/'.join(filter(None, [
                    str(e.get('profile_id', '') or ''),
                    str(e.get('objname', '') or ''),
                    str(e.get('obs_dir', '') or ''),
                    str(e.get('filename', '') or ''),
                ]))
                file_pairs.append((path, arc_name))

        total_size = sum(p.stat().st_size for p, _ in file_pairs)
        meta['total_size_bytes'] = total_size

        # If no accessible files were found on disk, mark done with no_files
        if not file_pairs:
            meta['chunks'] = []
            meta['status'] = 'done'
            meta['no_files'] = True
            meta['completed_at'] = datetime.now(timezone.utc).isoformat()
            _save_job_meta(username, job_id, meta)
            return

        # Build descriptive base filename:
        # download_{profile}_{YYYY}_{MM}_{DD}_{HH}_{MM}_{SS.cc}
        ts = datetime.now(timezone.utc)
        ts_str = (ts.strftime('%Y_%m_%d_%H_%M_')
                  + f'{ts.second:02d}.{ts.microsecond // 10000:02d}')
        safe_profile = re.sub(r'[^\w.-]', '_', str(profile_id or 'all'))
        base_name = f'download_{safe_profile}_{ts_str}'

        # Native format: copy file as-is (only valid for exactly one file)
        if fmt == 'native' and len(file_pairs) == 1:
            src, _arc = file_pairs[0]
            out_name = src.name
            out_path = job_dir / out_name
            shutil.copy2(str(src), str(out_path))
            chunk_metas = [{
                'index': 0,
                'path': str(out_path),
                'filename': out_name,
                'size_bytes': (
                    out_path.stat().st_size if out_path.exists() else 0
                ),
                'file_count': 1,
            }]
        else:
            # Archive format (zip / tar.gz); fall back to zip for native+multi
            actual_fmt = fmt if fmt in ('zip', 'tar.gz') else 'zip'

            # Split into chunks if requested
            if chunk_size_gb and file_pairs:
                chunk_bytes = int(chunk_size_gb * 1024 ** 3)
                chunks_files: List[List] = []
                cur_chunk: List = []
                cur_size = 0
                for p, arc in file_pairs:
                    sz = p.stat().st_size
                    if cur_chunk and cur_size + sz > chunk_bytes:
                        chunks_files.append(cur_chunk)
                        cur_chunk = [(p, arc)]
                        cur_size = sz
                    else:
                        cur_chunk.append((p, arc))
                        cur_size += sz
                if cur_chunk:
                    chunks_files.append(cur_chunk)
            else:
                chunks_files = [file_pairs]

            # Build archive(s)
            chunk_metas = []
            multi = len(chunks_files) > 1
            for c_idx, chunk in enumerate(chunks_files):
                if actual_fmt == 'tar.gz':
                    out_name = (f'{base_name}_part{c_idx + 1}.tar.gz' if multi
                                else f'{base_name}.tar.gz')
                    out_path = job_dir / out_name
                    with tarfile.open(str(out_path), 'w:gz') as tf:
                        for src, arc in chunk:
                            tf.add(str(src), arcname=arc)
                else:
                    out_name = (f'{base_name}_part{c_idx + 1}.zip' if multi
                                else f'{base_name}.zip')
                    out_path = job_dir / out_name
                    with zipfile.ZipFile(str(out_path), 'w',
                                         zipfile.ZIP_DEFLATED,
                                         allowZip64=True) as zf:
                        for src, arc in chunk:
                            zf.write(str(src), arcname=arc)
                chunk_metas.append({
                    'index': c_idx,
                    'path': str(out_path),
                    'filename': out_name,
                    'size_bytes': (
                        out_path.stat().st_size if out_path.exists() else 0
                    ),
                    'file_count': len(chunk),
                })

        meta['chunks'] = chunk_metas
        meta['status'] = 'done'
        meta['completed_at'] = datetime.now(timezone.utc).isoformat()
        _save_job_meta(username, job_id, meta)

        if email_on_done and user_email:
            _send_download_ready_email(user_email, job_id, chunk_metas)

    except Exception as exc:
        meta['status'] = 'error'
        meta['error'] = str(exc)
        meta['completed_at'] = datetime.now(timezone.utc).isoformat()
        _save_job_meta(username, job_id, meta)


def _send_download_ready_email(to_email: str,
                                job_id: str,
                                chunk_metas: List[Dict[str, Any]]) -> None:
    """Send a download-ready notification email (best-effort)."""
    try:
        from apero_ri.core import email_backend as eb
        n_files = sum(c.get('file_count', 0) for c in chunk_metas)
        total_bytes = sum(c.get('size_bytes', 0) for c in chunk_metas)
        size_mb = total_bytes / 1024 ** 2
        n_chunks = len(chunk_metas)
        body = (
            'Your APERO RI download basket compilation is complete.\n\n'
            f'Job ID: {job_id}\n'
            f'Total files archived: {n_files}\n'
            f'Total archive size: {size_mb:.1f} MB\n'
            f'Number of download parts: {n_chunks}\n\n'
            'Please log in to APERO RI and open your Download Basket '
            'to retrieve your files.\n\n'
            f'Download links expire after {_DOWNLOAD_EXPIRY_HOURS} hours.\n'
        )
        eb.send_email(to_email, 'APERO RI: Download basket ready', body)
    except Exception:
        pass


# =============================================================================
# File browser helpers
# =============================================================================

def load_ftable_rows(base_dir: Path,
                     instrument: str,
                     profile_id: str,
                     objname: str,
                     fkind: str = 'all') -> tuple:
    """
    Load rows from ftable_{fkind}_{objname}.json.
    Returns (rows, metadata, generated_at).
    """
    objects_dir = base_dir / 'tasks' / instrument / profile_id / 'objects'
    json_path = objects_dir / f'ftable_{fkind}_{objname}.json'
    if not json_path.exists():
        return [], {}, None
    try:
        with open(json_path, encoding='utf-8') as fh:
            data = json.load(fh)
        rows = data.get('rows', [])
        metadata = data.get('metadata', {})
        generated_at = (data.get('generated_at')
                        or (metadata.get('GENERATED_AT')
                            if isinstance(metadata, dict) else None))
        return rows, metadata, generated_at
    except Exception:
        return [], {}, None


def filter_accessible_rows(rows: List[Dict[str, Any]],
                           accessible_run_ids: Set[str]
                           ) -> List[Dict[str, Any]]:
    """Return only rows whose KW_RUN_ID is in accessible_run_ids."""
    return [
        r for r in rows
        if str(r.get('KW_RUN_ID', '') or '').strip() in accessible_run_ids
    ]


def apply_preset_filter(rows: List[Dict[str, Any]],
                        preset: str) -> List[Dict[str, Any]]:
    """
    Filter rows by a named preset.

    preset values:
      'ext2d'   – DRS_POST_E  block=out  QC=1
      'tcorr2d' – DRS_POST_T  block=out  QC=1
      'tcorr1d' – DRS_POST_E  block=out  QC=1  (same as ext2d per user spec)
      'polar'   – DRS_POST_P  block=out  QC=1
      'ccfrv'   – DRS_POST_V  block=out  QC=1
      'rdb'     – LBL_RDB%    block=lbl  (no QC filter)
            'none'    – no preset filter (return all accessible rows)
      'default' – block=out  QC=1
    """
    def _qc(r: Dict) -> bool:
        v = r.get('PASSED_ALL_QC')
        try:
            return int(v) == 1
        except (TypeError, ValueError):
            return bool(v)

    if preset == 'none':
        return rows

    if preset == 'ext2d':
        return [r for r in rows
                if r.get('BLOCK_KIND') == 'out'
                and r.get('KW_OUTPUT') == 'DRS_POST_E'
                and _qc(r)]
    elif preset == 'tcorr2d':
        return [r for r in rows
                if r.get('BLOCK_KIND') == 'out'
                and r.get('KW_OUTPUT') == 'DRS_POST_T'
                and _qc(r)]
    elif preset == 'tcorr1d':
        return [r for r in rows
                if r.get('BLOCK_KIND') == 'out'
                and r.get('KW_OUTPUT') == 'DRS_POST_E'
                and _qc(r)]
    elif preset == 'polar':
        return [r for r in rows
                if r.get('BLOCK_KIND') == 'out'
                and r.get('KW_OUTPUT') == 'DRS_POST_P'
                and _qc(r)]
    elif preset == 'ccfrv':
        return [r for r in rows
                if r.get('BLOCK_KIND') == 'out'
                and r.get('KW_OUTPUT') == 'DRS_POST_V'
                and _qc(r)]
    elif preset == 'rdb':
        return [r for r in rows
                if r.get('BLOCK_KIND') == 'lbl'
                and 'LBL_RDB' in str(r.get('KW_OUTPUT', '') or '')]
    else:  # 'default' or anything else
        return [r for r in rows
                if r.get('BLOCK_KIND') == 'out'
                and _qc(r)]


def group_rows(rows: List[Dict[str, Any]],
               group_by: str) -> List[Dict[str, Any]]:
    """
    Collapse rows into groups keyed by group_by column.
    Each group dict has:
      group_value, file_count, rows (list of grouped row dicts,
        with group_by column as first key)
    """
    if not group_by:
        return rows
    from collections import OrderedDict
    groups: Dict[str, List] = OrderedDict()
    for r in rows:
        key = str(r.get(group_by, '') or '')
        groups.setdefault(key, []).append(r)
    result = []
    for key, grp_rows in groups.items():
        result.append({
            'group_value': key,
            'group_by_col': group_by,
            'file_count': len(grp_rows),
            'rows': grp_rows,
        })
    return result


# =============================================================================
# Cleanup expired downloads
# =============================================================================

def cleanup_expired_downloads(username: str) -> int:
    """
    Delete job directories older than _DOWNLOAD_EXPIRY_HOURS. Returns count.
    """
    jobs_dir = _jobs_dir(username)
    if not jobs_dir.exists():
        return 0
    cutoff = (datetime.now(timezone.utc)
              - timedelta(hours=_DOWNLOAD_EXPIRY_HOURS))
    removed = 0
    removed_job_ids: List[str] = []
    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        meta = _load_job_meta(username, job_dir.name)
        if meta is None:
            continue
        created_str = meta.get('created_at', '')
        if not created_str:
            continue
        try:
            created_at = datetime.fromisoformat(str(created_str))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if created_at < cutoff:
                shutil.rmtree(str(job_dir), ignore_errors=True)
                removed_job_ids.append(job_dir.name)
                removed += 1
        except Exception:
            pass
    # Prune stale share tokens for removed jobs
    if removed_job_ids:
        with _share_tokens_lock:
            tokens = _load_share_tokens()
            cleaned = {
                tok: entry for tok, entry in tokens.items()
                if not (entry.get('username') == username
                        and entry.get('job_id') in removed_job_ids)
            }
            if len(cleaned) != len(tokens):
                _save_share_tokens(cleaned)
    return removed


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
