#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - GLOBAL async task: sync the APERO assets directory.

The task manages ``{LOCAL_DATA_DIR}/apero-assets/`` which mirrors the
remote APERO data-assets bundle used by the ARI UI for the
``data_get`` / ``data_set`` operations.

Two modes are supported:

``mode='remote'`` (default)
    Drives the apero developer recipe ``apero_data_checksum.py`` as a
    subprocess to keep the local ``{LOCAL_DATA_DIR}/apero-assets/``
    directory in sync with the configured remote checksum/tar server:
      * ``update-local --indir <assets_dir>``: download anything that is
        missing or out-of-date.
      * ``update-remote --indir <assets_dir>``: rebuild the tar /
        checksums and push back to the remote when local files are
        newer.

``mode='local'``
    Bidirectional newest-wins copy between a user-supplied local
    directory (``TASK_CONFIG['local_source_path']``) and
    ``{LOCAL_DATA_DIR}/apero-assets/``. Each file present on either
    side is compared by mtime and copied to the side with the older
    (or missing) copy.

Legacy mode names (``sync``, ``upload``) are accepted and treated as
``remote`` for backwards compatibility with existing
``async_tasks.yaml`` files.

Task config keys (all optional, set in ``async_tasks.yaml``):
  ``mode``                ``'remote'`` (default) or ``'local'``.
  ``local_source_path``   absolute path used by ``mode='local'``.
  ``force_download``      bool: kept for backwards compatibility (not
                          used by ``mode='remote'`` subprocess).

Created on 2026-04-22

@author: cook
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tarfile as _tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
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


def _get_apero_checksums_path() -> Optional[Path]:
    """
    Return the path to ``apero/data/checksums.yaml`` inside the installed
    apero package, or None if the package is not importable.
    """
    try:
        import apero as _apero_pkg
        p = Path(_apero_pkg.__file__).parent / 'data' / CHECKSUM_FILE
        return p if p.exists() else None
    except ImportError:
        return None


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


def _probe_servers(
        servers: List[str],
        tar_filename: str,
        tlog) -> List[str]:
    """
    Test each server by sending a HEAD request for ``tar_filename``.

    Uses HEAD rather than a partial GET so that the Content-Length of the
    tar file (which can be hundreds of MB) does not trigger the size guard
    inside ``_fetch_url_bytes``.

    :param servers: list of base URL strings to test
    :param tar_filename: basename of the tar file to probe for
    :param tlog: log callable
    :return: list of base URL strings that responded successfully
    """
    reachable: List[str] = []
    for server in servers:
        base = server.rstrip('/')
        url = f'{base}/{tar_filename}'
        req = Request(url, method='HEAD',
                      headers={'User-Agent': _HTTP_AGENT})
        try:
            with urlopen(req, timeout=10) as resp:
                if resp.status < 400:
                    reachable.append(server)
                    tlog(f'  {server}: accessible'
                         f' (HTTP {resp.status})')
                else:
                    tlog(f'  {server}: unreachable'
                         f' (HTTP {resp.status})')
        except (URLError, OSError) as exc:
            tlog(f'  {server}: unreachable ({exc})')
    return reachable


def _check_assets(assets_dir: Path,
                  pkg_checksums: Dict[str, Any]) -> List[str]:
    """
    Compare local files against ``pkg_checksums['data']``.

    :param assets_dir: the local apero-assets directory
    :param pkg_checksums: parsed checksums YAML from the apero package
    :return: list of relative paths that are missing or stale
    """
    data = pkg_checksums.get('data') or {}
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


# ---------------------------------------------------------------------------
# Remote (apero_data_checksum.py) and local (bidirectional copy) helpers
# ---------------------------------------------------------------------------
_LEGACY_REMOTE_MODES = ('remote', 'sync', 'upload')
_LEGACY_LOCAL_MODES = ('local',)


def _normalise_mode(raw_mode: Any) -> str:
    """Map task-config mode string to canonical ``remote``/``local``."""
    val = str(raw_mode or 'remote').strip().lower()
    if val in _LEGACY_LOCAL_MODES:
        return 'local'
    if val in _LEGACY_REMOTE_MODES:
        return 'remote'
    return 'remote'


def _find_apero_data_checksum_script() -> Optional[Path]:
    """Locate the installed ``apero_data_checksum.py`` recipe."""
    try:
        import apero as _apero_pkg
    except ImportError:
        return None
    candidate = (Path(_apero_pkg.__file__).parent
                 / 'tools' / 'recipes' / 'dev'
                 / 'apero_data_checksum.py')
    return candidate if candidate.is_file() else None


def _run_subprocess(cmd: List[str], tlog,
                    extra_env: Optional[dict] = None) -> Tuple[int, str]:
    """Run ``cmd`` capturing combined output; stream lines to ``tlog``."""
    tlog('Running: ' + ' '.join(cmd))
    env = None
    if extra_env:
        env = dict(os.environ)
        env.update(extra_env)
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
    except OSError as exc:
        tlog('ERROR: failed to launch subprocess: {0}'.format(exc))
        return 127, str(exc)
    captured: List[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            tlog('  ' + line)
            captured.append(line)
    rc = proc.wait()
    return rc, '\n'.join(captured)


def _run_remote_sync(assets_dir: Path, tlog,
                     drs_uconfig: Optional[str] = None) -> List[str]:
    """Drive ``apero_data_checksum.py update-local`` then ``update-remote``.

    :return: list of human-readable status lines for the task ``info``
             panel.
    """
    summary: List[str] = []
    script = _find_apero_data_checksum_script()
    if script is None:
        msg = ('Could not locate apero_data_checksum.py inside the '
               'installed apero package.')
        tlog('ERROR: ' + msg)
        raise FileNotFoundError(msg)

    if not drs_uconfig:
        msg = (
            'DRS_UCONFIG is not set in the task configuration. '
            'Please edit the APERO_SYNC_ASSETS task and set the '
            'DRS_UCONFIG directory (the APERO user config directory '
            'produced by apero_profile.sh).'
        )
        tlog('ERROR: ' + msg)
        raise RuntimeError(msg)
    uconfig_path = Path(drs_uconfig).expanduser()
    if not uconfig_path.is_dir():
        msg = (
            f'DRS_UCONFIG path does not exist or is not a directory: '
            f'{drs_uconfig}'
        )
        tlog('ERROR: ' + msg)
        raise RuntimeError(msg)
    tlog(f'DRS_UCONFIG: {uconfig_path}')
    extra_env = {'DRS_UCONFIG': str(uconfig_path)}

    base_cmd = [sys.executable, str(script)]
    indir = str(assets_dir)
    cmd_map = dict()
    cmd_map['update-local'] = (
        base_cmd + ['update-local', '--indir', indir]
    )
    cmd_map['update-remote'] = (
        base_cmd + ['update-remote', '--indir', indir]
    )
    for sub in ('update-local', 'update-remote'):
        cmd = cmd_map[sub]
        rc, output = _run_subprocess(cmd, tlog, extra_env=extra_env)
        if rc != 0:
            msg = ('apero_data_checksum.py {0} failed (exit {1}).'
                   ).format(sub, rc)
            if output:
                lines = output.splitlines()
                tail = '\n'.join(lines[-8:])
                msg = msg + '\nOutput tail:\n' + tail
            tlog('ERROR: ' + msg)
            summary.append('FAILED: ' + sub + ' (exit ' + str(rc) + ')')
            raise RuntimeError(msg)
        summary.append('OK: ' + sub)
    return summary


def _iter_files(root: Path):
    """Yield ``(rel_posix_path, abs_path)`` for every file under root."""
    for parent, _dirs, files in os.walk(root):
        for fname in files:
            ap = Path(parent) / fname
            try:
                rel = ap.relative_to(root).as_posix()
            except ValueError:
                continue
            yield rel, ap


def _copy_newer(src: Path, dst: Path) -> None:
    """Atomically copy ``src`` to ``dst`` (creating parent dirs)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(dst.parent), prefix='.assets_tmp_'
    )
    os.close(fd)
    try:
        shutil.copy2(str(src), tmp)
        os.replace(tmp, str(dst))
    except Exception:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass
        raise


def _run_local_sync(source_dir: Path, assets_dir: Path,
                    tlog, stop_event,
                    progress_cb=None) -> Dict[str, int]:
    """Bidirectional newest-wins copy between two local trees.

    :param progress_cb: optional callable ``f(fraction)`` invoked with a
        float in ``[0.1, 0.95]`` as files are processed, so the UI
        progress bar can advance.
    """
    if not source_dir.is_dir():
        raise FileNotFoundError(
            'local_source_path does not exist or is not a directory: '
            + str(source_dir)
        )
    assets_dir.mkdir(parents=True, exist_ok=True)

    tlog(f'Scanning local source tree: {source_dir}')
    src_files = dict(_iter_files(source_dir))
    tlog(f'  source files found: {len(src_files)}')
    tlog(f'Scanning assets tree: {assets_dir}')
    dst_files = dict(_iter_files(assets_dir))
    tlog(f'  assets files found: {len(dst_files)}')

    all_rel = sorted(set(src_files) | set(dst_files))
    total = len(all_rel)
    tlog(
        f'Comparing {total} unique relative paths '
        f'({len(set(src_files) & set(dst_files))} in both, '
        f'{len(set(src_files) - set(dst_files))} source-only, '
        f'{len(set(dst_files) - set(src_files))} assets-only).'
    )

    stats = {
        'src_to_dst': 0,
        'dst_to_src': 0,
        'unchanged': 0,
        'total': total,
    }
    # Log every ~5% (and at least every 100 files) so progress is
    # visible even on small trees.
    log_every = max(1, min(500, total // 20 or 1))
    last_logged = 0
    bytes_copied = 0
    for idx, rel in enumerate(all_rel, start=1):
        if stop_event is not None and stop_event.is_set():
            tlog('Cancellation requested; stopping local sync.')
            break
        sp = src_files.get(rel)
        dp = dst_files.get(rel)
        action = None
        try:
            if sp is None and dp is not None:
                target = source_dir / rel
                _copy_newer(dp, target)
                stats['dst_to_src'] += 1
                action = 'dst->src (new)'
                try:
                    bytes_copied += dp.stat().st_size
                except OSError:
                    pass
            elif dp is None and sp is not None:
                target = assets_dir / rel
                _copy_newer(sp, target)
                stats['src_to_dst'] += 1
                action = 'src->dst (new)'
                try:
                    bytes_copied += sp.stat().st_size
                except OSError:
                    pass
            elif sp is not None and dp is not None:
                try:
                    s_mt = sp.stat().st_mtime
                    d_mt = dp.stat().st_mtime
                except OSError:
                    continue
                if abs(s_mt - d_mt) <= 1.0:
                    stats['unchanged'] += 1
                else:
                    if s_mt > d_mt:
                        _copy_newer(sp, assets_dir / rel)
                        stats['src_to_dst'] += 1
                        action = 'src->dst (newer)'
                        try:
                            bytes_copied += sp.stat().st_size
                        except OSError:
                            pass
                    else:
                        _copy_newer(dp, source_dir / rel)
                        stats['dst_to_src'] += 1
                        action = 'dst->src (newer)'
                        try:
                            bytes_copied += dp.stat().st_size
                        except OSError:
                            pass
        except Exception as exc:  # noqa: BLE001
            tlog(f'  WARN: failed on {rel}: {exc}')
            continue

        if action is not None:
            tlog(f'  [{idx}/{total}] {action}: {rel}')

        if idx - last_logged >= log_every or idx == total:
            pct = (idx / total * 100.0) if total else 100.0
            tlog(
                f'Progress: {idx}/{total} ({pct:.1f}%) - '
                f'src->dst={stats["src_to_dst"]}, '
                f'dst->src={stats["dst_to_src"]}, '
                f'unchanged={stats["unchanged"]}, '
                f'bytes copied={bytes_copied}'
            )
            last_logged = idx
            if progress_cb is not None and total:
                # map progress into [0.1, 0.95]
                try:
                    progress_cb(0.1 + 0.85 * (idx / total))
                except Exception:
                    pass

    stats['bytes_copied'] = bytes_copied
    return stats


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
        mode = _normalise_mode(task_cfg.get('mode'))
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
        # LOCAL mode: bidirectional newest-wins copy with a local source
        # =====================================================================
        if mode == 'local':
            local_src_raw = str(
                task_cfg.get('local_source_path') or ''
            ).strip()
            if not local_src_raw:
                msg = ("mode='local' requires TASK_CONFIG."
                       "local_source_path to be set")
                tlog('ERROR: ' + msg)
                self.info += '\n**ERROR**: ' + msg + '\n'
                self.progress = 1.0
                raise ValueError(msg)
            source_dir = Path(local_src_raw).expanduser().resolve()
            self.info += (
                f'**Local source**: `{source_dir}`  \n'
            )
            tlog(f'Local-sync source: {source_dir}')
            self.progress = 0.1

            def _progress_cb(frac: float) -> None:
                try:
                    f = float(frac)
                except (TypeError, ValueError):
                    return
                if f < 0.0:
                    f = 0.0
                elif f > 0.99:
                    f = 0.99
                self.progress = f

            try:
                stats = _run_local_sync(
                    source_dir, assets_dir, tlog, stop_event,
                    progress_cb=_progress_cb,
                )
            except Exception as exc:  # noqa: BLE001
                self.info += f'\n**ERROR**: {exc}\n'
                self.progress = 1.0
                raise
            self.progress = 1.0
            self.info += (
                '\n### Local sync\n'
                f'- total compared: {stats.get("total", 0)}\n'
                f'- source -> assets: {stats["src_to_dst"]}\n'
                f'- assets -> source: {stats["dst_to_src"]}\n'
                f'- unchanged: {stats["unchanged"]}\n'
                f'- bytes copied: {stats.get("bytes_copied", 0)}\n'
            )
            tlog(
                'APERO_SYNC_ASSETS completed (local): '
                f'total={stats.get("total", 0)}, '
                f'src->dst={stats["src_to_dst"]}, '
                f'dst->src={stats["dst_to_src"]}, '
                f'unchanged={stats["unchanged"]}, '
                f'bytes copied={stats.get("bytes_copied", 0)}.'
            )
            return

        # =====================================================================
        # REMOTE mode: drive apero_data_checksum.py update-local + update-remote
        # =====================================================================
        self.progress = 0.1
        drs_uconfig = str(task_cfg.get('drs_uconfig') or '').strip()
        self.info += f'**DRS_UCONFIG**: `{drs_uconfig or "(not set)"}`  \n'
        try:
            summary = _run_remote_sync(assets_dir, tlog,
                                       drs_uconfig=drs_uconfig or None)
        except Exception as exc:  # noqa: BLE001
            self.info += f'\n**ERROR**: {exc}\n'
            self.progress = 1.0
            raise
        self.progress = 1.0
        self.info += '\n### Remote sync\n'
        for line in summary:
            self.info += f'- {line}\n'
        if force_download:
            self.info += (
                '\n_Note: ``force_download`` is ignored in '
                'remote mode (handled by apero_data_checksum.py).'
                '_\n'
            )
        tlog('APERO_SYNC_ASSETS completed (remote).')
        return

    # -------------------------------------------------------------------------
    # Legacy upload helper (kept for reference; no longer wired to run_job)
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
