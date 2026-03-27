#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARI API client — programmatic access to APERO Reduction Interface data.

This module provides:
- ``configure(server, token)`` — store connection settings
- ``list_profiles()`` — list accessible APERO profiles
- ``AperoProfile(name)`` — work with object/observation tables
- ``AperoObject`` — inspect and download data for a single target
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import requests
except ImportError:
    requests = None  # type: ignore[assignment]

# -------------------------------------------------------------------------
# Configuration persistence
# -------------------------------------------------------------------------
_CONFIG_DIR = Path.home() / '.ari'
_CONFIG_FILE = _CONFIG_DIR / 'api_config.json'

# In-memory overrides (set by configure())
_runtime_server: Optional[str] = None
_runtime_token: Optional[str] = None


def _ensure_requests():
    """Raise a helpful error when ``requests`` is not installed."""
    if requests is None:
        raise ImportError(
            "The 'requests' package is required for ari_api.  "
            "Install it with:  pip install apero_ri[api]"
        )


def _load_config() -> Dict[str, str]:
    """Load config from ``~/.ari/api_config.json``."""
    if _CONFIG_FILE.exists():
        try:
            with open(_CONFIG_FILE, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def _save_config(cfg: Dict[str, str]) -> None:
    """Persist config to ``~/.ari/api_config.json`` (chmod 0o600)."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, 'w', encoding='utf-8') as fh:
        json.dump(cfg, fh, indent=2)
    try:
        _CONFIG_FILE.chmod(0o600)
    except OSError:
        pass


def configure(server: str, token: str, *, save: bool = True) -> None:
    """Set the ARI server URL and API token.

    Parameters
    ----------
    server : str
        Base URL of the ARI instance (e.g. ``https://ari.example.com``).
    token : str
        API token obtained from the ARI user portal.
    save : bool
        If *True* (default), persist to ``~/.ari/api_config.json``.
    """
    global _runtime_server, _runtime_token
    _runtime_server = server.rstrip('/')
    _runtime_token = token
    if save:
        cfg = _load_config()
        cfg['server'] = _runtime_server
        cfg['token'] = _runtime_token
        _save_config(cfg)


def _get_server() -> str:
    """Return the configured server URL."""
    if _runtime_server:
        return _runtime_server
    cfg = _load_config()
    server = cfg.get('server', '').strip()
    if not server:
        raise RuntimeError(
            "ARI server not configured.  Call ari_api.configure(server=..., "
            "token=...) first."
        )
    return server.rstrip('/')


def _get_token() -> str:
    """Return the configured API token."""
    if _runtime_token:
        return _runtime_token
    cfg = _load_config()
    token = cfg.get('token', '').strip()
    if not token:
        raise RuntimeError(
            "ARI API token not configured.  Call ari_api.configure(server=..., "
            "token=...) first, or generate a token in the ARI user portal."
        )
    return token


# -------------------------------------------------------------------------
# Low-level HTTP helpers
# -------------------------------------------------------------------------
def _headers() -> Dict[str, str]:
    return {'Authorization': f'Bearer {_get_token()}'}


def _raise_api_error(resp) -> None:
    """Extract a server error message from the response JSON, or fall back."""
    try:
        data = resp.json()
        msg = data.get('error', '') if isinstance(data, dict) else ''
    except Exception:
        msg = ''
    if msg:
        raise RuntimeError(f'[HTTP {resp.status_code}] {msg}')
    resp.raise_for_status()


def _get(path: str, params: Optional[dict] = None) -> dict:
    """Perform an authenticated GET and return the JSON body."""
    _ensure_requests()
    url = f'{_get_server()}{path}'
    resp = requests.get(url, headers=_headers(), params=params, timeout=120)
    if not resp.ok:
        _raise_api_error(resp)
    data = resp.json()
    if isinstance(data, dict) and data.get('success') is False:
        raise RuntimeError(data.get('error', 'Unknown server error'))
    return data


def _post(path: str, body: Optional[dict] = None) -> dict:
    """Perform an authenticated POST and return the JSON body."""
    _ensure_requests()
    url = f'{_get_server()}{path}'
    resp = requests.post(url, headers=_headers(), json=body or {}, timeout=120)
    if not resp.ok:
        _raise_api_error(resp)
    data = resp.json()
    if isinstance(data, dict) and data.get('success') is False:
        raise RuntimeError(data.get('error', 'Unknown server error'))
    return data


def _download(path: str, dest: Path, params: Optional[dict] = None) -> Path:
    """Stream-download a file to *dest*."""
    _ensure_requests()
    url = f'{_get_server()}{path}'
    with requests.get(url, headers=_headers(), params=params,
                      stream=True, timeout=300) as resp:
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'wb') as fh:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                fh.write(chunk)
    return dest


# -------------------------------------------------------------------------
# Table formatting helpers
# -------------------------------------------------------------------------
def _rows_to_fmt(rows: List[dict], columns: Optional[List[str]],
                 fmt: str) -> Any:
    """Convert a list of row-dicts to the requested format.

    Parameters
    ----------
    rows : list of dict
        Row data as returned by the server.
    columns : list of str or None
        Column ordering hint.
    fmt : str
        ``'pandas'`` → ``pandas.DataFrame``,
        ``'astropy'`` → ``astropy.table.Table``,
        ``'dict'`` → raw list of dicts.
    """
    if fmt == 'dict':
        return rows
    if fmt == 'pandas':
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for fmt='pandas'.  "
                "Install it with:  pip install pandas"
            )
        if columns:
            return pd.DataFrame(rows, columns=columns)
        return pd.DataFrame(rows)
    if fmt == 'astropy':
        try:
            from astropy.table import Table
        except ImportError:
            raise ImportError(
                "astropy is required for fmt='astropy'.  "
                "Install it with:  pip install astropy"
            )
        if not rows:
            return Table()
        return Table(rows)
    raise ValueError(f"Unsupported format '{fmt}'. Use 'pandas', 'astropy', "
                     f"or 'dict'.")


# -------------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------------
def list_profiles() -> List[str]:
    """Return a list of accessible profile IDs.

    >>> profiles = ari_api.list_profiles()
    ['spirou_xxs_08_cook_home', ...]
    """
    data = _get('/api/data-portal/profiles')
    return [p['profile_id'] for p in data.get('profiles', [])]


def list_profiles_detailed() -> List[Dict[str, str]]:
    """Return detailed profile info (profile_id, instrument, label)."""
    data = _get('/api/data-portal/profiles')
    return data.get('profiles', [])


# -------------------------------------------------------------------------
# AperoProfile
# -------------------------------------------------------------------------
class AperoProfile:
    """Interface to a single APERO reduction profile.

    Parameters
    ----------
    profile_id : str
        The profile identifier (e.g. ``'spirou_xxs_08_cook_home'``).

    Examples
    --------
    >>> profile = ari_api.AperoProfile('spirou_xxs_08_cook_home')
    >>> obj_table = profile.get_object_table()
    >>> obs_table = profile.get_observation_table(fmt='astropy')
    """

    def __init__(self, profile_id: str):
        self.profile_id = profile_id

    def __repr__(self) -> str:
        return f"AperoProfile('{self.profile_id}')"

    # -----------------------------------------------------------------
    # Tables
    # -----------------------------------------------------------------
    def get_object_table(self, fmt: str = 'pandas') -> Any:
        """Fetch the object table for this profile.

        Parameters
        ----------
        fmt : str
            ``'pandas'`` (default) → ``DataFrame``,
            ``'astropy'`` → ``astropy.table.Table``,
            ``'dict'`` → list of dicts.
        """
        data = _get('/api/data-portal/object-table',
                     {'profile_id': self.profile_id})
        rows = data.get('rows', [])
        columns = data.get('columns', None)
        return _rows_to_fmt(rows, columns, fmt)

    def get_observation_table(self, fmt: str = 'pandas') -> Any:
        """Fetch the observation table for this profile.

        Parameters
        ----------
        fmt : str
            ``'pandas'`` (default) → ``DataFrame``,
            ``'astropy'`` → ``astropy.table.Table``,
            ``'dict'`` → list of dicts.
        """
        data = _get('/api/data-portal/obs-table',
                     {'profile_id': self.profile_id})
        rows = data.get('rows', [])
        columns = data.get('columns', None)
        return _rows_to_fmt(rows, columns, fmt)

    # -----------------------------------------------------------------
    # Objects
    # -----------------------------------------------------------------
    def list_objects(self) -> List[str]:
        """Return a list of object names available in this profile."""
        data = _get('/api/data-portal/object-table',
                     {'profile_id': self.profile_id})
        rows = data.get('rows', [])
        return [
            str(r.get('OBJNAME', ''))
            for r in rows if r.get('OBJNAME')
        ]

    def get_object(self, objname: str) -> 'AperoObject':
        """Get an :class:`AperoObject` handle for the given target.

        Parameters
        ----------
        objname : str
            Target name (e.g. ``'GL699'``).
        """
        return AperoObject(self.profile_id, objname)


# -------------------------------------------------------------------------
# AperoObject
# -------------------------------------------------------------------------
class AperoObject:
    """Interface to a single target within an APERO profile.

    Normally obtained via :meth:`AperoProfile.get_object`.

    Parameters
    ----------
    profile_id : str
        Profile identifier.
    objname : str
        Object / target name.

    Examples
    --------
    >>> obj = profile.get_object('GL699')
    >>> info = obj.target_info()            # pandas DataFrame
    >>> files = obj.list_files()            # list of dicts
    >>> obj.get_count()                     # number of downloadable files
    >>> obj.get_data('/tmp/GL699_data')     # download matching files
    """

    def __init__(self, profile_id: str, objname: str):
        self.profile_id = profile_id
        self.objname = objname

    def __repr__(self) -> str:
        return f"AperoObject('{self.profile_id}', '{self.objname}')"

    def target_info(self, fmt: str = 'pandas') -> Any:
        """Return the object-page summary statistics as a table.

        Parameters
        ----------
        fmt : str
            ``'pandas'`` (default), ``'astropy'``, or ``'dict'``.
        """
        data = _get('/api/data-portal/object-page', {
            'profile_id': self.profile_id,
            'objname': self.objname,
        })
        sections = data.get('sections', {})
        rows: List[dict] = []
        if isinstance(sections, dict):
            for section_name, section_data in sections.items():
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        rows.append({
                            'section': section_name,
                            'key': key,
                            'value': value,
                        })
                elif isinstance(section_data, list):
                    # time_series is a list of observation dicts
                    for i, item in enumerate(section_data):
                        if isinstance(item, dict):
                            for key, value in item.items():
                                rows.append({
                                    'section': section_name,
                                    'key': key,
                                    'value': value,
                                })
        return _rows_to_fmt(rows, ['section', 'key', 'value'], fmt)

    def list_files(self, preset: str = 'default') -> List[dict]:
        """Return the file-browser rows for this object.

        Parameters
        ----------
        preset : str
            File filter preset (default ``'default'``).

        Returns
        -------
        list of dict
            Each dict has keys from the file table (filename, DPRTYPE,
            night, etc.).
        """
        data = _get('/api/data-portal/file-browser', {
            'profile_id': self.profile_id,
            'objname': self.objname,
            'preset': preset,
        })
        return data.get('rows', [])

    def get_count(self, *, preset: str = 'default',
                  **filters: Any) -> int:
        """Return the number of files that would be downloaded.

        Accepts the same arguments as :meth:`get_data` (minus *localdir*
        and *overwrite*) so you can preview the file count before
        committing to a download.

        Parameters
        ----------
        preset : str
            File filter preset (default ``'default'``).
        **filters
            Column-name filters applied to the file list.
            For example ``KW_DPRTYPE='OBJ_FP'``.

        Returns
        -------
        int
            Number of matching files.
        """
        rows = self.list_files(preset=preset)
        if filters:
            rows = [
                r for r in rows
                if all(str(r.get(k, '')) == str(v) for k, v in filters.items())
            ]
        return len(rows)

    def get_data(self, localdir: str, *,
                 preset: str = 'default',
                 overwrite: bool = False,
                 **filters: Any) -> List[Path]:
        """Download files for this object to a local directory.

        Files are added to the user's basket, compiled into an archive,
        and downloaded.

        Parameters
        ----------
        localdir : str
            Local directory to save files into.
        preset : str
            File filter preset (default ``'default'``).
        overwrite : bool
            Re-download even if a local file with the same name exists.
        **filters
            Column-name filters applied to the file list before download.
            For example ``KW_DPRTYPE='OBJ_FP'`` keeps only rows whose
            ``KW_DPRTYPE`` column matches the given value.

        Returns
        -------
        list of Path
            Paths to downloaded files.
        """
        rows = self.list_files(preset=preset)

        # Apply column filters
        if filters:
            filtered = []
            for row in rows:
                match = True
                for key, val in filters.items():
                    if str(row.get(key, '')) != str(val):
                        match = False
                        break
                if match:
                    filtered.append(row)
            rows = filtered

        if not rows:
            return []

        out_dir = Path(localdir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Build basket entries from file rows.
        # The file browser returns UPPERCASE keys but add_to_basket
        # expects lowercase keys.
        _KEY_MAP = {
            'FILENAME': 'filename',
            'KW_RUN_ID': 'kw_run_id',
            'OBS_DIR': 'obs_dir',
            'BLOCK_KIND': 'block_kind',
            'KW_DPRTYPE': 'kw_dprtype',
            'NIGHT': 'night',
        }
        entries = []
        for row in rows:
            entry = {
                'profile_id': self.profile_id,
                'objname': self.objname,
            }
            for src, dst in _KEY_MAP.items():
                if src in row:
                    entry[dst] = row[src]
                elif dst in row:
                    entry[dst] = row[dst]
            entries.append(entry)

        # Clear basket, add entries, compile, poll, download
        _post('/api/data-portal/basket/clear',
              {'profile_id': self.profile_id})
        _post('/api/data-portal/basket/add', {'entries': entries})

        compile_resp = _post('/api/data-portal/basket/compile', {
            'fmt': 'zip',
            'profile_id': self.profile_id,
        })
        job_id = compile_resp.get('job_id')
        if not job_id:
            raise RuntimeError('Compilation failed — no job ID returned')

        # Poll until ready
        import time
        for _ in range(600):  # up to 10 minutes
            status = _get(f'/api/data-portal/basket/compile-status/{job_id}')
            job = status.get('job', {})
            state = job.get('status', '')
            if state == 'done':
                break
            if state in ('error', 'failed'):
                raise RuntimeError(
                    f'Compilation failed: {job.get("error", state)}'
                )
            time.sleep(1)
        else:
            raise TimeoutError('Download compilation timed out')

        # Download chunks
        import zipfile
        downloaded: List[Path] = []
        chunks = job.get('chunks', [])
        for chunk in chunks:
            idx = chunk.get('index', 0)
            archive_path = out_dir / f'_ari_download_{job_id}_{idx}.zip'
            _download(
                f'/api/data-portal/basket/download/{job_id}/{idx}',
                archive_path,
            )
            # Extract
            with zipfile.ZipFile(archive_path, 'r') as zf:
                for member in zf.namelist():
                    dest = out_dir / Path(member).name
                    if not overwrite and dest.exists():
                        downloaded.append(dest)
                        continue
                    with zf.open(member) as src, open(dest, 'wb') as dst:
                        dst.write(src.read())
                    downloaded.append(dest)
            # Clean up archive
            archive_path.unlink(missing_ok=True)

        return downloaded
