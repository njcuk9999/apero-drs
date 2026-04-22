#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – GLOBAL async task: sync the APERO assets directory.

The task manages ``{LOCAL_DATA_DIR}/apero-assets/`` which mirrors the
remote APERO data-assets bundle (calibration files, static tables, etc.)
used by the ARI UI for "get" (download) and "set" (upload) operations.

Workflow (default ``mode='sync'``):
  1. Download the remote ``checksums.yaml`` from the first reachable server.
  2. Compare every listed file against the local copy (MD-5 hash).
  3. If anything is missing or stale, download the versioned tar file and
     extract it into ``apero-assets/``.
  4. Write a local ``checksums.yaml`` so the next run can skip the download
     when nothing has changed.

Workflow (``mode='upload'``):
  1. Index all files under ``TASK_CONFIG['local_indir']`` and build a fresh
     ``checksums.yaml`` + versioned tar file.
  2. Upload both via rsync to the configured SSH host.

Task config keys (all optional, set in ``async_tasks.yaml``):
  ``asset_servers``   list of base URL strings (trailing slash optional).
                      Each is tried in turn until one is reachable.
  ``checksum_file``   filename of the remote checksum YAML
                      (default ``'checksums.yaml'``).
  ``force_download``  bool: re-extract even if checksums match.
  ``mode``            ``'sync'`` (default) or ``'upload'``.
  ``local_indir``     source directory for upload mode.
  ``ssh_user``        SSH username for rsync upload.
  ``ssh_host``        SSH hostname for rsync upload.
  ``ssh_options``     extra SSH options string (e.g. ``'-p 22'``).
  ``ssh_assets_path`` remote path to deploy assets to.

Created on 2026-04-22

@author: cook
"""

import hashlib
import os
import shutil
import tarfile as _tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.apero_assets_sync'
# Default home .ari directory
ARI_DIR = Path.home() / '.ari'
# Name of the apero-assets sub-directory within LOCAL_DATA_DIR
ASSETS_SUBDIR = 'apero-assets'
# Default name of the checksum YAML on both local disk and remote server
CHECKSUM_FILE = 'checksums.yaml'
# HTTP request timeout (seconds) for checksum + tar downloads
HTTP_TIMEOUT = 60
# Max size of tar download that we will attempt (bytes).  1.5 GB default.
MAX_TAR_BYTES = 1_500_000_000
# rsync command template (mirrors drs_assets.RSYNC_CMD)
RSYNC_CMD = 'rsync -avuz -e "{SSH}" {INPATH} {USER}@{HOST}:{OUTPATH}'
# User-agent string sent with HTTP requests
_HTTP_AGENT = 'apero-ri-assets-sync/1.0'
# Module-level task metadata consumed by the registry
PARAM_LIST = ['LOCAL_DATA_DIR', 'INSTRUMENT', 'TASK_CONFIG']
APERO_PROFILE_PARAM_LIST: List[str] = []
DEFAULT_FREQUENCY = 24.0        # run once per day by default
DEFAULT_ENABLED = True
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS: List[str] = []


# =============================================================================
# Define helpers
# =============================================================================
def _md5(path: Path) -> str:
    """Return the hex MD5 digest of the file at ``path``."""
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    """Load a YAML file and return its contents, or None on failure."""
    if not _HAS_YAML:
        return None
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return _yaml.safe_load(fh) or {}
    except Exception:
        return None


def _save_yaml(data: Dict[str, Any], path: Path) -> None:
    """Write ``data`` to ``path`` as YAML (atomic via tmp file)."""
    if not _HAS_YAML:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix='.yaml.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            _yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=False)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _fetch_url_bytes(url: str, timeout: int = HTTP_TIMEOUT,
                     max_bytes: int = MAX_TAR_BYTES) -> Optional[bytes]:
    """
    Download ``url`` and return its raw bytes, or None on failure.

    Respects ``max_bytes`` to guard against accidentally downloading huge
    files.
    """
    req = Request(url, headers={'User-Agent': _HTTP_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            # honour content-length as a pre-flight guard
            cl = resp.headers.get('Content-Length')
            if cl and int(cl) > max_bytes:
                return None
            data = resp.read(max_bytes + 1)
            if len(data) > max_bytes:
                return None
            return data
    except (URLError, OSError):
        return None


def _fetch_remote_checksum(
        servers: List[str],
        checksum_file: str) -> Optional[Dict[str, Any]]:
    """
    Try each URL in ``servers`` and return the parsed checksum YAML dict.

    :param servers: list of base URL strings (tried in order)
    :param checksum_file: filename of the checksum YAML on the server
    :return: parsed dict or None if no server was reachable
    """
    if not _HAS_YAML:
        return None
    for server in servers:
        base = server.rstrip('/')
        url = f'{base}/{checksum_file}'
        data = _fetch_url_bytes(url, timeout=30, max_bytes=10_000_000)
        if data is None:
            continue
        try:
            result = _yaml.safe_load(data.decode('utf-8', errors='replace'))
            if isinstance(result, dict):
                return result
        except Exception:
            continue
    return None


def _probe_servers(
        servers: List[str],
        checksum_file: str,
        tlog) -> List[str]:
    """
    Test each server with a small request for the checksum file header.

    :param servers: list of base URL strings to test
    :param checksum_file: filename used to build the probe URL
    :param tlog: log callable
    :return: list of base URL strings that responded successfully
    """
    reachable: List[str] = []
    for server in servers:
        base = server.rstrip('/')
        url = f'{base}/{checksum_file}'
        data = _fetch_url_bytes(url, timeout=10, max_bytes=512)
        if data is not None:
            reachable.append(server)
            tlog(f'  {server}: accessible')
        else:
            tlog(f'  {server}: unreachable')
    return reachable


def _check_assets(assets_dir: Path,
                  remote_checksums: Dict[str, Any]) -> List[str]:
    """
    Compare local files against ``remote_checksums['data']``.

    :param assets_dir: the local apero-assets directory
    :param remote_checksums: parsed checksum YAML from the server
    :return: list of relative paths that are missing or stale
    """
    data = remote_checksums.get('data') or {}
    stale: List[str] = []
    for rel_path, expected_hash in data.items():
        local_path = assets_dir / rel_path
        if not local_path.exists():
            stale.append(rel_path)
            continue
        actual_hash = _md5(local_path)
        if actual_hash != expected_hash:
            stale.append(rel_path)
    return stale


def _download_and_extract(
        servers: List[str],
        tar_filename: str,
        assets_dir: Path,
        tlog) -> bool:
    """
    Download ``tar_filename`` from the first reachable server and extract
    into ``assets_dir``.

    :param servers: list of base URL strings
    :param tar_filename: basename of the tar file to download
    :param assets_dir: destination directory for extraction
    :param tlog: log callable
    :return: True on success, False if no server could supply the file
    """
    assets_dir.mkdir(parents=True, exist_ok=True)
    # check if the file is already cached locally (avoid re-download)
    local_tar = assets_dir / tar_filename
    if not local_tar.exists():
        tlog(f'Downloading assets tar file: {tar_filename}')
        downloaded = False
        for server in servers:
            base = server.rstrip('/')
            url = f'{base}/{tar_filename}'
            tlog(f'Trying: {url}')
            raw = _fetch_url_bytes(url, timeout=HTTP_TIMEOUT,
                                   max_bytes=MAX_TAR_BYTES)
            if raw is None:
                tlog(f'  Failed (unreachable or too large).')
                continue
            # write to a temp file and atomically rename
            fd, tmp_tar = tempfile.mkstemp(dir=assets_dir,
                                            suffix='.tar.gz.tmp')
            try:
                with os.fdopen(fd, 'wb') as fh:
                    fh.write(raw)
                os.replace(tmp_tar, local_tar)
                downloaded = True
                tlog(f'  Download OK ({len(raw):,} bytes).')
                break
            except Exception as exc:
                if os.path.exists(tmp_tar):
                    os.unlink(tmp_tar)
                tlog(f'  Write failed: {exc}')
                continue
        if not downloaded:
            tlog('ERROR: could not download assets tar file from any server.')
            return False
    else:
        tlog(f'Using cached tar file: {local_tar.name}')
    # extract the tar file
    tlog(f'Extracting {local_tar.name} into {assets_dir}')
    try:
        with _tarfile.open(local_tar, 'r:gz') as tf:
            # safety: reject any member with absolute path or '..'
            safe_members = []
            for member in tf.getmembers():
                member_path = Path(member.name)
                if member_path.is_absolute():
                    continue
                if '..' in member_path.parts:
                    continue
                safe_members.append(member)
            tf.extractall(path=assets_dir, members=safe_members)
    except Exception as exc:
        tlog(f'ERROR extracting tar file: {exc}')
        return False
    tlog('Extraction complete.')
    return True


def _build_local_checksums(assets_dir: Path,
                            servers: List[str]) -> Dict[str, Any]:
    """
    Index all files under ``assets_dir`` and compute their MD5 hashes.

    :param assets_dir: directory to index
    :param servers: list of server base URLs to embed in the YAML
    :return: checksums dict ready for YAML serialisation
    """
    data: Dict[str, str] = {}
    for root, _dirs, files in os.walk(assets_dir):
        for filename in sorted(files):
            if filename.endswith('_assets.tar.gz'):
                continue
            if filename == CHECKSUM_FILE:
                continue
            abs_path = Path(root) / filename
            rel_path = abs_path.relative_to(assets_dir).as_posix()
            data[rel_path] = _md5(abs_path)
    now = datetime.now(timezone.utc)
    setup: Dict[str, Any] = {}
    setup['tarfile'] = ''
    setup['version'] = ''
    setup['unixtime'] = now.timestamp()
    setup['humantime'] = now.isoformat()
    setup['servers'] = servers
    return {'setup': setup, 'data': data}


def _upload_via_rsync(tar_path: Path, ssh_user: str, ssh_host: str,
                       ssh_options: str, ssh_assets_path: str,
                       tlog) -> bool:
    """
    Upload ``tar_path`` to the remote server via rsync.

    :return: True if the rsync command exited 0, False otherwise.
    """
    cmd = RSYNC_CMD.format(
        SSH=ssh_options or 'ssh',
        INPATH=str(tar_path),
        USER=ssh_user,
        HOST=ssh_host,
        OUTPATH=ssh_assets_path,
    )
    tlog(f'rsync: {cmd}')
    rc = os.system(cmd)
    if rc != 0:
        tlog(f'rsync exited with code {rc}.')
        return False
    return True


# =============================================================================
# Define classes
# =============================================================================
class AperoAssetsSyncTask(apero_async.AperoAsyncTask):
    """
    Sync the APERO assets bundle to/from ``{LOCAL_DATA_DIR}/apero-assets/``.

    In default (``mode='sync'``) mode:
      - Downloads the remote ``checksums.yaml``.
      - Compares checksums of local files.
      - Extracts the versioned tar only when something has changed.

    In ``mode='upload'`` mode:
      - Builds a fresh checksum YAML and tar from ``TASK_CONFIG['local_indir']``.
      - Uploads via rsync to the configured SSH host.
    """

    def __init__(self, status: str = 'pending') -> None:
        name = 'APERO Assets Sync Task'
        description = (
            'Sync the APERO data-assets bundle with '
            '{LOCAL_DATA_DIR}/apero-assets/ using checksums to avoid '
            'unnecessary large downloads.'
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:
        """
        Execute the assets sync.

        Required keys in ``params``:
          - ``LOCAL_DATA_DIR``: str, root directory (e.g. ``~/.ari``).
          - ``TASK_CONFIG``: dict of per-task overrides (see module doc).

        Optional ``TASK_CONFIG`` keys:
          - ``asset_servers``: list of str, base URLs for the remote assets.
          - ``checksum_file``: str, filename of the checksum YAML.
          - ``force_download``: bool, re-extract even if up-to-date.
          - ``mode``: ``'sync'`` (default) or ``'upload'``.
          - ``local_indir``: str, source directory for upload mode.
          - ``ssh_user``, ``ssh_host``, ``ssh_options``, ``ssh_assets_path``.

        :param params: dict, task parameter dictionary
        :return: None
        """
        local_data_dir = Path(
            params.get('LOCAL_DATA_DIR', str(ARI_DIR))
        ).expanduser().resolve()

        task_cfg = dict(params.get('TASK_CONFIG') or {})
        task_logger = params.get('TASK_LOGGER')
        stop_event = params.get('STOP_EVENT')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        tlog('APERO_SYNC_ASSETS start.')

        # assets directory inside LOCAL_DATA_DIR
        assets_dir = local_data_dir / ASSETS_SUBDIR
        assets_dir.mkdir(parents=True, exist_ok=True)
        tlog(f'Assets directory: {assets_dir}')

        # read task config
        mode = str(task_cfg.get('mode') or 'sync').strip().lower()
        raw_servers = task_cfg.get('asset_servers') or []
        if isinstance(raw_servers, str):
            raw_servers = [raw_servers]
        servers: List[str] = [str(s).strip() for s in raw_servers if s]
        checksum_file = str(
            task_cfg.get('checksum_file') or CHECKSUM_FILE
        ).strip()
        force_download = bool(task_cfg.get('force_download', False))

        # ---- reset info -----------------------------------------------------
        generated_at = datetime.now(timezone.utc).isoformat()
        self.info = (
            f'## APERO Assets Sync\n\n'
            f'**Mode**: `{mode}`  \n'
            f'**Assets dir**: `{assets_dir}`  \n'
            f'**Generated at**: {generated_at}  \n'
        )

        # =====================================================================
        # UPLOAD mode: push local assets to remote server
        # =====================================================================
        if mode == 'upload':
            self._run_upload(
                task_cfg=task_cfg,
                assets_dir=assets_dir,
                servers=servers,
                checksum_file=checksum_file,
                tlog=tlog,
                stop_event=stop_event,
            )
            self.progress = 1.0
            tlog('APERO_SYNC_ASSETS completed (upload).')
            return

        # =====================================================================
        # SYNC mode: check and download if changed
        # =====================================================================
        if not servers:
            msg = (
                'No asset_servers configured in TASK_CONFIG. '
                'Set TASK_CONFIG.asset_servers to a list of base URLs.'
            )
            tlog(f'WARNING: {msg}')
            self.info += f'\n**WARNING**: {msg}\n'
            self.progress = 1.0
            return

        self.info += (
            f'**Servers**: {", ".join(servers[:3])}'
            f'{"…" if len(servers) > 3 else ""}  \n'
        )

        if stop_event is not None and stop_event.is_set():
            tlog('Cancellation requested. Exiting.')
            return

        # ---- probe server accessibility ------------------------------------
        tlog('Probing server accessibility...')
        reachable = _probe_servers(servers, checksum_file, tlog)
        if reachable:
            self.info += (
                '**Accessible**: '
                + ', '.join(f'`{s}`' for s in reachable) + '  \n'
            )
        else:
            self.info += (
                '**WARNING**: none of the configured servers are '
                'currently reachable.  \n'
            )

        if stop_event is not None and stop_event.is_set():
            tlog('Cancellation requested after probe. Exiting.')
            return

        # ---- fetch remote checksum -----------------------------------------
        tlog(f'Fetching remote checksum: {checksum_file}')
        remote_chk = _fetch_remote_checksum(servers, checksum_file)

        if remote_chk is None:
            msg = (
                'Could not fetch remote checksum YAML from any configured '
                'server. Assets are not updated.'
            )
            tlog(f'WARNING: {msg}')
            self.info += f'\n**WARNING**: {msg}\n'
            self.progress = 1.0
            return

        # remote version info for reporting
        setup_info = remote_chk.get('setup') or {}
        remote_version = str(setup_info.get('version') or 'unknown')
        remote_ts = str(setup_info.get('humantime') or 'unknown')
        tar_filename = str(setup_info.get('tarfile') or '').strip()
        self.info += (
            f'**Remote version**: `{remote_version}`  \n'
            f'**Remote timestamp**: {remote_ts}  \n'
        )
        tlog(
            f'Remote checksum: version={remote_version}, '
            f'ts={remote_ts}, tar={tar_filename}.'
        )

        self.progress = 0.2

        if stop_event is not None and stop_event.is_set():
            tlog('Cancellation requested after checksum fetch. Exiting.')
            return

        # ---- compare checksums ----------------------------------------------
        if force_download:
            stale: List[str] = list(
                (remote_chk.get('data') or {}).keys()
            )
            tlog(f'force_download=True: marking all {len(stale)} files stale.')
        else:
            stale = _check_assets(assets_dir, remote_chk)
            tlog(
                f'Checksum comparison: {len(stale)} file(s) missing/stale '
                f'out of {len(remote_chk.get("data") or {})}.'
            )

        self.progress = 0.3

        if not stale:
            tlog('Assets are up-to-date. Nothing to download.')
            self.info += '\n### Status\nAssets are **up-to-date**. No download needed.\n'
            # persist the remote checksum YAML locally for offline checks
            _save_yaml(remote_chk, assets_dir / checksum_file)
            self.output_files = [str(assets_dir / checksum_file)]
            self.progress = 1.0
            tlog('APERO_SYNC_ASSETS completed (no download needed).')
            return

        self.info += (
            f'\n### Changed files\n'
            f'{len(stale)} file(s) are missing or have changed.\n'
        )
        if stale[:5]:
            for rel in stale[:5]:
                self.info += f'- `{rel}`\n'
            if len(stale) > 5:
                self.info += f'- …and {len(stale) - 5} more\n'

        if stop_event is not None and stop_event.is_set():
            tlog('Cancellation requested before download. Exiting.')
            return

        # ---- download and extract tar file ----------------------------------
        if not tar_filename:
            msg = (
                'Remote checksum YAML has no tarfile entry. '
                'Cannot download assets tar.'
            )
            tlog(f'ERROR: {msg}')
            self.info += f'\n**ERROR**: {msg}\n'
            self.progress = 1.0
            return

        self.progress = 0.4
        ok = _download_and_extract(
            servers=servers,
            tar_filename=tar_filename,
            assets_dir=assets_dir,
            tlog=tlog,
        )

        self.progress = 0.9

        if ok:
            # save the remote checksum YAML locally so the next run
            # can compare without a network round-trip
            _save_yaml(remote_chk, assets_dir / checksum_file)
            n_files = len(remote_chk.get('data') or {})
            self.info += (
                f'\n### Download\n'
                f'Extracted `{tar_filename}` '
                f'({n_files} file(s) indexed).\n'
            )
            self.output_files = [str(assets_dir / checksum_file)]
            tlog(
                f'APERO_SYNC_ASSETS completed: '
                f'extracted {tar_filename} ({n_files} files).'
            )
        else:
            self.info += f'\n**ERROR**: download/extraction failed.\n'
            tlog('APERO_SYNC_ASSETS failed: download/extraction error.')
            raise RuntimeError(
                'APERO assets sync failed: could not download or extract '
                f'{tar_filename!r} from {servers}.'
            )

        self.progress = 1.0

    # -------------------------------------------------------------------------
    # Upload helper
    # -------------------------------------------------------------------------
    def _run_upload(self,
                    task_cfg: Dict[str, Any],
                    assets_dir: Path,
                    servers: List[str],
                    checksum_file: str,
                    tlog,
                    stop_event) -> None:
        """
        Build a checksums YAML + tar file from ``local_indir`` and upload
        via rsync to the configured SSH host.

        :param task_cfg: task configuration dict
        :param assets_dir: the local apero-assets directory
        :param servers: list of server base URLs (embedded in checksums YAML)
        :param checksum_file: name for the checksum YAML file
        :param tlog: log callable
        :param stop_event: threading.Event for cooperative cancellation
        :return: None
        """
        local_indir_raw = str(task_cfg.get('local_indir') or '').strip()
        if not local_indir_raw:
            msg = ('upload mode requires TASK_CONFIG.local_indir to be set '
                   'to the local assets source directory.')
            tlog(f'ERROR: {msg}')
            self.info += f'\n**ERROR**: {msg}\n'
            raise ValueError(msg)

        local_indir = Path(local_indir_raw).expanduser().resolve()
        if not local_indir.exists():
            msg = f'local_indir does not exist: {local_indir}'
            tlog(f'ERROR: {msg}')
            self.info += f'\n**ERROR**: {msg}\n'
            raise FileNotFoundError(msg)

        # Sanity-check: expect a marker file so a misconfigured indir cannot
        # accidentally upload the wrong directory
        if not (local_indir / 'apero-assets.txt').exists():
            msg = (
                f'local_indir={local_indir} is missing the required '
                f'"apero-assets.txt" marker file.'
            )
            tlog(f'ERROR: {msg}')
            self.info += f'\n**ERROR**: {msg}\n'
            raise FileNotFoundError(msg)

        tlog(f'Indexing upload source: {local_indir}')
        self.progress = 0.1

        # build checksums
        chk_data = _build_local_checksums(local_indir, servers)

        # derive tar filename from current unix time
        unix_now = str(time.time()).replace('.', '_')
        tar_name = f'{unix_now}_assets.tar.gz'
        chk_data['setup']['tarfile'] = tar_name

        # write checksum YAML into the source directory
        chk_path = local_indir / checksum_file
        _save_yaml(chk_data, chk_path)
        tlog(f'Saved checksum YAML: {chk_path} ({len(chk_data["data"])} files)')

        self.progress = 0.3

        if stop_event is not None and stop_event.is_set():
            tlog('Cancellation requested before tar creation. Exiting.')
            return

        # build the tar file (exclude existing tar files to avoid nesting)
        tar_path = local_indir / tar_name
        tlog(f'Building tar file: {tar_path}')
        try:
            with _tarfile.open(tar_path, 'w:gz') as tf:
                for root, _dirs, files in os.walk(local_indir):
                    for filename in sorted(files):
                        if filename.endswith('_assets.tar.gz'):
                            continue
                        abs_path = Path(root) / filename
                        arcname = abs_path.relative_to(local_indir).as_posix()
                        tf.add(abs_path, arcname=arcname)
        except Exception as exc:
            msg = f'Failed to create tar file: {exc}'
            tlog(f'ERROR: {msg}')
            self.info += f'\n**ERROR**: {msg}\n'
            raise

        tlog(
            f'Tar file created: {tar_path.name} '
            f'({tar_path.stat().st_size:,} bytes)'
        )
        self.progress = 0.7

        if stop_event is not None and stop_event.is_set():
            tlog('Cancellation requested before rsync upload. Exiting.')
            return

        # rsync upload
        ssh_user = str(task_cfg.get('ssh_user') or '').strip()
        ssh_host = str(task_cfg.get('ssh_host') or '').strip()
        ssh_options = str(task_cfg.get('ssh_options') or 'ssh').strip()
        ssh_assets_path = str(task_cfg.get('ssh_assets_path') or '').strip()

        if not ssh_user or not ssh_host or not ssh_assets_path:
            msg = (
                'upload mode requires TASK_CONFIG: '
                'ssh_user, ssh_host, and ssh_assets_path.'
            )
            tlog(f'ERROR: {msg}')
            self.info += f'\n**ERROR**: {msg}\n'
            raise ValueError(msg)

        tlog(f'Uploading {tar_path.name} → {ssh_user}@{ssh_host}:{ssh_assets_path}')
        ok = _upload_via_rsync(
            tar_path=tar_path,
            ssh_user=ssh_user,
            ssh_host=ssh_host,
            ssh_options=ssh_options,
            ssh_assets_path=ssh_assets_path,
            tlog=tlog,
        )
        self.progress = 0.95

        n_files = len(chk_data.get('data') or {})
        if ok:
            self.info += (
                f'\n### Upload\n'
                f'Uploaded `{tar_name}` ({n_files} files) to '
                f'`{ssh_user}@{ssh_host}:{ssh_assets_path}`.\n'
            )
            self.output_files = [str(tar_path), str(chk_path)]
            tlog(f'Upload succeeded: {tar_name}.')
        else:
            msg = f'rsync upload failed for {tar_name}.'
            self.info += f'\n**ERROR**: {msg}\n'
            raise RuntimeError(msg)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
