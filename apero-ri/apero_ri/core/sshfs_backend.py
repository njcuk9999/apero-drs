#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: SSHFS mount management backend.

Configuration is stored in {ARI_DIR}/admin/sshfs/sshfs.yaml.
SSH keys are stored in {ARI_DIR}/secret/ssh_keys/{key_name}.key.
Mount status is checked via subprocess commands.
"""

# =============================================================================
# Imports
# =============================================================================
from __future__ import annotations

import json
import logging
import multiprocessing
import os
import re
import shlex
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.sshfs_backend'
DEFAULT_STATUS_SUBPROCESS_TIMEOUT_S = 4.0
SSH_CONNECT_MIN_INTERVAL_S = 20.0
_ssh_attempt_lock = threading.Lock()
_ssh_attempt_times: Dict[str, float] = {}

# =============================================================================
# Define functions
# =============================================================================

# -------------------------------------------------------------------------
# Define private helpers
# -------------------------------------------------------------------------

def _get_mount_logs_dir() -> Path:
    """Get directory for per-mount log files."""
    ari_dir = Path(os.environ.get('ARI_DIR', os.path.expanduser('~/.ari')))
    log_dir = ari_dir / 'admin' / 'sshfs' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    legacy_dir = ari_dir / 'admin' / 'sshfs_logs'
    if legacy_dir.exists() and legacy_dir.is_dir():
        for child in legacy_dir.iterdir():
            dest = log_dir / child.name
            if dest.exists():
                continue
            try:
                child.replace(dest)
            except OSError:
                continue
        try:
            legacy_dir.rmdir()
        except OSError:
            pass

    return log_dir


def save_mount_log(mount_name: str, log_lines: List[str],
                   source: str = 'mount') -> None:
    """Persist the last log for a mount to disk."""
    safe_name = re.sub(r'[^\w\-.]', '_', mount_name)
    log_path = _get_mount_logs_dir() / f'{safe_name}.json'
    entry = {
        'timestamp': datetime.now(tz=timezone.utc).isoformat(),
        'source': source,
        'lines': log_lines,
    }
    log_path.write_text(json.dumps(entry, indent=2), encoding='utf-8')


def get_mount_log(mount_name: str) -> Dict[str, Any]:
    """Read the last saved log for a mount."""
    safe_name = re.sub(r'[^\w\-.]', '_', mount_name)
    log_path = _get_mount_logs_dir() / f'{safe_name}.json'
    if not log_path.exists():
        return {'ok': True, 'log': [], 'timestamp': None, 'source': None}
    try:
        entry = json.loads(log_path.read_text(encoding='utf-8'))
        return {
            'ok': True,
            'log': entry.get('lines', []),
            'timestamp': entry.get('timestamp'),
            'source': entry.get('source'),
        }
    except Exception as exc:
        return {'ok': False, 'error': f'Failed to read log: {exc}'}


def _normalize_connection_mode(value: str) -> str:
    mode = str(value or 'direct').strip().lower()
    return mode if mode in {'direct', 'ssh_config_host'} else 'direct'


def _normalize_bool(value: Any) -> bool:
    """Normalize bool-like values from JSON/YAML payloads."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


def _resolve_connection_target(mount_config: Dict[str, Any]) -> Dict[str, str]:
    """Resolve connection target details for direct or ssh-config modes."""
    mode = _normalize_connection_mode(
        mount_config.get('connection_mode', 'direct'))
    remote_path = str(mount_config.get('remote_path') or '').strip()

    if mode == 'ssh_config_host':
        ssh_config_host = str(
            mount_config.get('ssh_config_host') or '').strip()
        return {
            'mode': mode,
            'ssh_target': ssh_config_host,
            'sshfs_target': (
                f'{ssh_config_host}:{remote_path}'
                if ssh_config_host and remote_path else ''),
            'display_target': ssh_config_host,
        }

    remote_user = str(mount_config.get('remote_user') or '').strip() or 'root'
    remote_host = str(mount_config.get('remote_host') or '').strip()
    ssh_target = f'{remote_user}@{remote_host}' if remote_host else ''
    return {
        'mode': mode,
        'ssh_target': ssh_target,
        'sshfs_target': (
            f'{ssh_target}:{remote_path}'
            if ssh_target and remote_path else ''),
        'display_target': ssh_target,
    }


def _build_sshfs_mount_command(mount: Dict[str, Any], key_path: Path,
                               local_mount: Path) -> List[str]:
    """Build sshfs command for one mount definition."""
    target_info = _resolve_connection_target(mount)
    remote_target = target_info['sshfs_target']
    if not remote_target:
        raise ValueError('Mount target is incomplete.')

    return [
        'sshfs',
        '-o', f'IdentityFile={key_path}',
        '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=accept-new',
        '-o', 'ServerAliveInterval=15,ServerAliveCountMax=3',
        remote_target,
        str(local_mount),
    ]


def _throttle_ssh_target(target: str,
                         action: str,
                         min_interval_s: float = SSH_CONNECT_MIN_INTERVAL_S
                         ) -> str:
    """Return an error string if a target is being contacted too often."""
    key = str(target or '').strip()
    if not key:
        return ''

    now = time.monotonic()
    with _ssh_attempt_lock:
        last = _ssh_attempt_times.get(key)
        if last is not None:
            delta = now - last
            if delta < min_interval_s:
                wait_s = max(0.0, min_interval_s - delta)
                return (
                    f'SSH connection to {key} throttled for safety during '
                    f'{action}. Wait about {wait_s:.0f}s and try again.'
                )
        _ssh_attempt_times[key] = now
    return ''


def _get_sshfs_config_path() -> Path:
    """Get path to SSHFS configuration file."""
    ari_dir = os.environ.get('ARI_DIR', os.path.expanduser('~/.ari'))
    admin_dir = Path(ari_dir) / 'admin'
    config_dir = admin_dir / 'sshfs'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'sshfs.yaml'
    legacy_file = admin_dir / 'sshfs.yaml'

    if not config_file.exists() and legacy_file.exists():
        try:
            config_file.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass

    return config_file


def _get_secret_dir() -> Path:
    """Get secret storage directory under ARI_DIR."""
    ari_dir = os.environ.get('ARI_DIR', os.path.expanduser('~/.ari'))
    secret_dir = Path(ari_dir) / 'secret'
    secret_dir.mkdir(parents=True, exist_ok=True)
    try:
        secret_dir.chmod(0o700)
    except OSError:
        pass
    return secret_dir


def _get_ssh_keys_dir() -> Path:
    """Get directory where SSH keys are stored."""
    ari_dir = Path(os.environ.get('ARI_DIR', os.path.expanduser('~/.ari')))
    ssh_dir = _get_secret_dir() / 'ssh_keys'
    ssh_dir.mkdir(parents=True, exist_ok=True)
    legacy_dir = ari_dir / 'admin' / 'ssh_keys'
    if legacy_dir.exists() and legacy_dir.is_dir():
        for child in legacy_dir.iterdir():
            dest = ssh_dir / child.name
            if dest.exists():
                continue
            child.replace(dest)
        try:
            legacy_dir.rmdir()
        except OSError:
            pass
    try:
        ssh_dir.chmod(0o700)
    except OSError:
        pass
    return ssh_dir


def _default_config() -> Dict[str, Any]:
    """Return default SSHFS configuration."""
    return {
        'mounts': [],  # List of mounted volumes
    }


# -------------------------------------------------------------------------
# Define public config I/O functions
# -------------------------------------------------------------------------
def load_sshfs_config() -> Dict[str, Any]:
    """Load SSHFS config from disk and merge with defaults."""
    cfg = _default_config()
    path = _get_sshfs_config_path()
    
    if not path.exists():
        return cfg

    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}
            cfg.update(data)
    except Exception:
        pass

    # Ensure mounts is a list
    if not isinstance(cfg.get('mounts'), list):
        cfg['mounts'] = []

    return cfg


def save_sshfs_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Save SSHFS config to disk."""
    path = _get_sshfs_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, 'w') as f:
            yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
        return {'ok': True, 'message': 'Configuration saved.'}
    except Exception as e:
        return {'ok': False, 'error': f'Failed to save config: {str(e)}'}


# -------------------------------------------------------------------------
# Define SSH key management functions
# -------------------------------------------------------------------------
def list_ssh_keys() -> Dict[str, Any]:
    """List available SSH keys stored in the system."""
    try:
        ssh_dir = _get_ssh_keys_dir()
        keys = []
        
        if ssh_dir.exists():
            for key_file in sorted(ssh_dir.glob('*.key')):
                key_name = key_file.stem
                try:
                    stat = key_file.stat()
                    keys.append({
                        'name': key_name,
                        'path': str(key_file),
                        'size': stat.st_size,
                        'mtime': datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc).isoformat(),
                    })
                except Exception:
                    pass
        
        return {'ok': True, 'keys': keys}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'keys': []}


def add_ssh_key(key_name: str, key_content: str) -> Dict[str, Any]:
    """Add or update an SSH key."""
    if not key_name or not key_content.strip():
        return {'ok': False, 'error': 'Key name and content are required.'}

    # Validate key name (alphanumeric, underscore, hyphen only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', key_name):
        return {'ok': False, 'error': 'Key name must contain only alphanumeric characters, hyphens, and underscores.'}

    try:
        ssh_dir = _get_ssh_keys_dir()
        key_path = ssh_dir / f'{key_name}.key'
        
        # Write key with restricted permissions
        key_path.write_text(key_content.strip() + '\n')
        key_path.chmod(0o600)
        
        return {'ok': True, 'message': f'SSH key "{key_name}" added successfully.'}
    except Exception as e:
        return {'ok': False, 'error': f'Failed to add SSH key: {str(e)}'}


def delete_ssh_key(key_name: str) -> Dict[str, Any]:
    """Delete an SSH key."""
    try:
        ssh_dir = _get_ssh_keys_dir()
        key_path = ssh_dir / f'{key_name}.key'
        
        if not key_path.exists():
            return {'ok': False, 'error': f'SSH key "{key_name}" not found.'}
        
        key_path.unlink()
        return {'ok': True, 'message': f'SSH key "{key_name}" deleted successfully.'}
    except Exception as e:
        return {'ok': False, 'error': f'Failed to delete SSH key: {str(e)}'}


# -------------------------------------------------------------------------
# Define mount management functions
# -------------------------------------------------------------------------
def add_mount(mount_config: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new SSHFS mount configuration."""
    connection_mode = _normalize_connection_mode(
        mount_config.get('connection_mode', 'direct')
    )
    mount_config['connection_mode'] = connection_mode
    # UI policy: mounting is command-only (never executed inside the UI).
    mount_config['manual_mode'] = True

    required = ['name', 'remote_path', 'local_mount', 'ssh_key']
    for field in required:
        if not mount_config.get(field):
            return {'ok': False, 'error': f'Missing required field: {field}'}

    if connection_mode == 'ssh_config_host':
        if not mount_config.get('ssh_config_host'):
            return {'ok': False,
                    'error': 'Missing required field: ssh_config_host'}
        mount_config['remote_user'] = ''
        mount_config['remote_host'] = ''
    else:
        if not mount_config.get('remote_host'):
            return {'ok': False,
                    'error': 'Missing required field: remote_host'}
        mount_config['ssh_config_host'] = ''

    try:
        cfg = load_sshfs_config()
        
        # Check if mount name already exists
        existing = [m for m in cfg.get('mounts', [])
                    if m.get('name') == mount_config['name']]
        if existing:
            return {'ok': False, 'error': f'Mount "{mount_config["name"]}" already exists.'}
        
        # Normalize remote path (ensure leading slash)
        if not mount_config['remote_path'].startswith('/'):
            mount_config['remote_path'] = '/' + mount_config['remote_path']
        
        # Add metadata
        mount_config['created_at'] = datetime.now(tz=timezone.utc).isoformat()
        mount_config['status'] = 'unmounted'
        
        cfg['mounts'].append(mount_config)
        result = save_sshfs_config(cfg)
        
        if result['ok']:
            return {'ok': True, 'message': f'Mount "{mount_config["name"]}" added successfully.'}
        return result
    except Exception as e:
        return {'ok': False, 'error': f'Failed to add mount: {str(e)}'}


def delete_mount(mount_name: str) -> Dict[str, Any]:
    """Delete an SSHFS mount configuration."""
    try:
        cfg = load_sshfs_config()
        mount = next(
            (m for m in cfg.get('mounts', [])
             if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.'}
        
        # Unmount first if currently mounted
        if mount.get('status') == 'mounted':
            unmount_result = unmount_sshfs(mount_name)
            if not unmount_result['ok']:
                return {'ok': False, 'error': f'Cannot delete mounted volume. Unmount first: {unmount_result["error"]}'}
        
        cfg['mounts'] = [m for m in cfg['mounts']
                         if m.get('name') != mount_name]
        result = save_sshfs_config(cfg)
        
        if result['ok']:
            return {'ok': True, 'message': f'Mount "{mount_name}" deleted successfully.'}
        return result
    except Exception as e:
        return {'ok': False, 'error': f'Failed to delete mount: {str(e)}'}


def update_mount(original_name: str,
                 mount_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing SSHFS mount configuration."""
    original_name = str(original_name or '').strip()
    if not original_name:
        return {'ok': False, 'error': 'Original mount name is required.'}

    connection_mode = _normalize_connection_mode(
        mount_config.get('connection_mode', 'direct')
    )
    mount_config['connection_mode'] = connection_mode
    # UI policy: mounting is command-only (never executed inside the UI).
    mount_config['manual_mode'] = True

    required = ['name', 'remote_path', 'local_mount', 'ssh_key']
    for field in required:
        if not mount_config.get(field):
            return {'ok': False, 'error': f'Missing required field: {field}'}

    if connection_mode == 'ssh_config_host':
        if not mount_config.get('ssh_config_host'):
            return {'ok': False,
                    'error': 'Missing required field: ssh_config_host'}
        mount_config['remote_user'] = ''
        mount_config['remote_host'] = ''
    else:
        if not mount_config.get('remote_host'):
            return {'ok': False,
                    'error': 'Missing required field: remote_host'}
        mount_config['ssh_config_host'] = ''

    if not str(mount_config['remote_path']).startswith('/'):
        mount_config['remote_path'] = '/' + str(mount_config['remote_path'])

    try:
        cfg = load_sshfs_config()
        mounts = cfg.get('mounts', [])
        index = next((i for i, m in enumerate(mounts)
                      if m.get('name') == original_name), None)
        if index is None:
            return {'ok': False, 'error': f'Mount "{original_name}" not found.'}

        existing = mounts[index]
        if existing.get('status') == 'mounted':
            return {'ok': False,
                    'error': 'Unmount this mount before editing it.'}

        new_name = str(mount_config.get('name') or '').strip()
        for i, mount in enumerate(mounts):
            if i != index and mount.get('name') == new_name:
                return {'ok': False, 'error': f'Mount "{new_name}" already exists.'}

        updated = dict(existing)
        updated.update(mount_config)
        updated['status'] = 'unmounted'
        updated['mounted_at'] = None
        mounts[index] = updated

        result = save_sshfs_config(cfg)
        if result['ok']:
            return {'ok': True, 'message': f'Mount "{new_name}" updated successfully.'}
        return result
    except Exception as e:
        return {'ok': False, 'error': f'Failed to update mount: {str(e)}'}


def _prepare_mount_dir(local_mount: Path, log: List[str]) -> None:
    """Ensure *local_mount* exists as a directory, cleaning up stale FUSE
    mount points when necessary."""
    try:
        local_mount.mkdir(parents=True, exist_ok=True)
        log.append(f'Mount directory ready: {local_mount}')
    except OSError:
        # Likely a stale FUSE mount (I/O error on stat).  Try to
        # force-unmount and then re-create.
        log.append(f'Mount directory exists but inaccessible (stale FUSE?) — '
                   f'attempting fusermount -uz {local_mount}')
        fuse = subprocess.run(
            ['fusermount', '-uz', str(local_mount)],
            capture_output=True, text=True, timeout=10,
        )
        log.append(f'fusermount exit={fuse.returncode}  '
                   f'stderr={fuse.stderr.strip() or "(none)"}')
        # If fusermount failed, try lazy umount as fallback
        if fuse.returncode != 0:
            log.append(f'Trying umount -l {local_mount}')
            um = subprocess.run(
                ['umount', '-l', str(local_mount)],
                capture_output=True, text=True, timeout=10,
            )
            log.append(f'umount -l exit={um.returncode}  '
                       f'stderr={um.stderr.strip() or "(none)"}')
        local_mount.mkdir(parents=True, exist_ok=True)
        log.append(f'Mount directory ready after cleanup: {local_mount}')


def mount_sshfs(mount_name: str) -> Dict[str, Any]:
    """Return a command to mount an SSHFS volume manually.

    UI policy intentionally avoids executing SSHFS mount commands directly in
    the web process.
    """
    log: List[str] = []
    try:
        cfg = load_sshfs_config()
        mount = next(
            (m for m in cfg.get('mounts', [])
             if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.',
                    'log': log}
        
        if mount.get('status') == 'mounted':
            # Verify the mount is actually live before returning early
            local_mount_path = mount.get('local_mount', '')
            mq = subprocess.run(
                ['mountpoint', '-q', local_mount_path],
                capture_output=True, timeout=5,
            )
            if mq.returncode == 0:
                return {'ok': True,
                        'message': f'Mount "{mount_name}" is already mounted.',
                        'log': log}
            # Config says mounted but it's not — fix the stale status
            log.append(f'Config says mounted but mountpoint check failed — '
                       f'resetting status')
            mount['status'] = 'unmounted'
            mount['mounted_at'] = None
            save_sshfs_config(cfg)
        
        # Get SSH key path
        ssh_key = mount.get('ssh_key')
        ssh_keys_dir = _get_ssh_keys_dir()
        key_path = ssh_keys_dir / f'{ssh_key}.key'
        
        if not key_path.exists():
            return {'ok': False, 'error': f'SSH key "{ssh_key}" not found.',
                    'log': log}
        
        # Create local mount directory (handle stale mounts)
        local_mount = Path(mount.get('local_mount', ''))
        _prepare_mount_dir(local_mount, log)

        manual_cmd = _build_sshfs_mount_command(mount, key_path, local_mount)
        cmd_text = shlex.join(manual_cmd)
        log.append('Command-only mode enabled; mount command was not executed.')
        log.append(f'Run manually: {cmd_text}')
        save_mount_log(mount_name, log, source='mount')
        return {
            'ok': True,
            'manual_mode': True,
            'message': (
                f'Run this command in your terminal to mount "{mount_name}".'
            ),
            'command': cmd_text,
            'log': log,
        }
    except subprocess.TimeoutExpired:
        log.append('Operation timed out')
        save_mount_log(mount_name, log, source='mount')
        return {'ok': False, 'error': 'Mount operation timed out.',
                'log': log}
    except Exception as e:
        log.append(f'Exception: {e}')
        save_mount_log(mount_name, log, source='mount')
        return {'ok': False, 'error': f'Failed to mount: {str(e)}',
                'log': log}


def unmount_sshfs(mount_name: str) -> Dict[str, Any]:
    """Unmount an SSHFS volume."""
    try:
        cfg = load_sshfs_config()
        mount = next(
            (m for m in cfg.get('mounts', [])
             if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.'}
        
        if mount.get('status') != 'mounted':
            return {'ok': True, 'message': f'Mount "{mount_name}" is not mounted.'}
        
        local_mount = mount.get('local_mount')
        
        # Try umount
        result = subprocess.run(
            ['umount', local_mount],
            capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            # Try force unmount
            result = subprocess.run(
                ['umount', '-l', local_mount],
                capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                error = result.stderr or result.stdout or 'Unknown error'
                return {'ok': False, 'error': f'Failed to unmount: {error}'}
        
        # Update config
        mount['status'] = 'unmounted'
        mount['mounted_at'] = None
        save_sshfs_config(cfg)
        
        return {'ok': True, 'message': f'Mount "{mount_name}" unmounted successfully.'}
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'Unmount operation timed out.'}
    except Exception as e:
        return {'ok': False, 'error': f'Failed to unmount: {str(e)}'}


def lazy_unmount_sshfs(mount_name: str) -> Dict[str, Any]:
    """Attempt to repair a stuck SSHFS mount via lazy detach commands."""
    try:
        cfg = load_sshfs_config()
        mount = next(
            (m for m in cfg.get('mounts', [])
             if m.get('name') == mount_name), None)

        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.'}

        local_mount = str(mount.get('local_mount', '') or '').strip()
        if not local_mount:
            return {'ok': False, 'error': 'Mount has no local mount path.'}

        attempts = [
            ['fusermount', '-uz', local_mount],
            ['umount', '-l', local_mount],
        ]
        errors: List[str] = []
        for cmd in attempts:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except FileNotFoundError:
                errors.append(f'{cmd[0]} not available')
                continue
            except subprocess.TimeoutExpired:
                errors.append(f'{" ".join(cmd)} timed out')
                continue

            if result.returncode == 0:
                mount['status'] = 'unmounted'
                mount['mounted_at'] = None
                save_sshfs_config(cfg)
                return {
                    'ok': True,
                    'message': f'Mount "{mount_name}" lazy-unmounted successfully.',
                    'command': ' '.join(cmd),
                }

            err = (result.stderr or result.stdout or 'Unknown error').strip()
            errors.append(f'{" ".join(cmd)}: {err}')

        try:
            status_check = subprocess.run(
                ['mountpoint', '-q', local_mount],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if status_check.returncode != 0:
                mount['status'] = 'unmounted'
                mount['mounted_at'] = None
                save_sshfs_config(cfg)
                return {
                    'ok': True,
                    'message': (
                        f'Mount "{mount_name}" appears detached now; '
                        f'local state was reset.'
                    ),
                    'command': 'status-reset',
                }
        except Exception:
            pass

        return {
            'ok': False,
            'error': 'Failed to lazy-unmount: ' + '; '.join(errors),
        }
    except Exception as e:
        return {'ok': False, 'error': f'Failed to lazy-unmount: {str(e)}'}


# -------------------------------------------------------------------------
# Define status and health functions
# -------------------------------------------------------------------------
def _check_mount_status_worker(mount: Dict[str, Any],
                               out_conn) -> None:
    """Worker for mount status checks, isolated in a child process."""
    try:
        local_mount = str(mount.get('local_mount', '') or '').strip()
        if not local_mount:
            out_conn.send({
                'ok': False,
                'error': 'Mount has no local_mount configured.',
                'status': 'unknown',
            })
            return

        result = subprocess.run(
            ['mountpoint', '-q', local_mount],
            capture_output=True,
            timeout=3,
        )
        is_mounted = result.returncode == 0

        status_data = {
            'ok': True,
            'mounted': is_mounted,
            'local_mount': local_mount,
            'mounted_at': mount.get('mounted_at'),
            'check_mode': 'mountpoint+ls-timeout',
        }

        # If it is mounted, probe local directory responsiveness without SSH.
        # This catches stale mounts while avoiding long hangs via timeout.
        if is_mounted:
            try:
                ls_result = subprocess.run(
                    ['ls', '-1', local_mount],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if ls_result.returncode == 0:
                    status_data['responsive'] = True
                    sample = ''
                    for line in (ls_result.stdout or '').splitlines():
                        line = line.strip()
                        if line:
                            sample = line
                            break
                    if sample:
                        status_data['sample_entry'] = sample
                else:
                    status_data['responsive'] = False
                    status_data['auth_stale'] = True
                    err = (ls_result.stderr or ls_result.stdout or '').strip()
                    status_data['warning'] = (
                        'Mountpoint exists but directory listing failed'
                        + (f': {err}' if err else '.')
                    )
            except subprocess.TimeoutExpired:
                status_data['responsive'] = False
                status_data['auth_stale'] = True
                status_data['warning'] = (
                    'Mountpoint exists but directory listing timed out; '
                    'mount is likely stale/unresponsive.'
                )
        out_conn.send(status_data)
    except subprocess.TimeoutExpired:
        out_conn.send({
            'ok': False,
            'error': 'Status check timed out (mountpoint).',
            'status': 'unknown',
        })
    except Exception as exc:
        out_conn.send({
            'ok': False,
            'error': f'Failed to check status: {exc}',
            'status': 'unknown',
        })
    finally:
        try:
            out_conn.close()
        except Exception:
            pass


def check_mount_status(mount_name: str) -> Dict[str, Any]:
    """Check the status of an SSHFS mount."""
    try:
        cfg = load_sshfs_config()
        mount = next(
            (m for m in cfg.get('mounts', [])
             if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.', 'status': 'unknown'}
        
        timeout_s = max(1.0, float(DEFAULT_STATUS_SUBPROCESS_TIMEOUT_S))
        ctx = multiprocessing.get_context('spawn')
        parent_conn, child_conn = ctx.Pipe(duplex=False)
        proc = ctx.Process(
            target=_check_mount_status_worker,
            args=(mount, child_conn),
            daemon=True,
        )
        proc.start()
        try:
            child_conn.close()
        except Exception:
            pass
        proc.join(timeout=timeout_s)

        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=1.0)
            if proc.is_alive():
                proc.kill()
                proc.join(timeout=1.0)
            try:
                parent_conn.close()
            except Exception:
                pass
            return {
                'ok': False,
                'error': (
                    f'Status check timed out after {timeout_s:.1f}s '
                    f'(subprocess terminated).'
                ),
                'status': 'unknown',
            }

        try:
            if not parent_conn.poll(0.05):
                raise RuntimeError('no result')
            status_data = parent_conn.recv()
        except Exception:
            try:
                parent_conn.close()
            except Exception:
                pass
            return {
                'ok': False,
                'error': 'Status check subprocess exited without result.',
                'status': 'unknown',
            }
        finally:
            try:
                parent_conn.close()
            except Exception:
                pass

        if not isinstance(status_data, dict):
            return {
                'ok': False,
                'error': 'Invalid status payload from status subprocess.',
                'status': 'unknown',
            }
        return status_data
    except Exception as e:
        return {'ok': False, 'error': f'Failed to check status: {str(e)}', 'status': 'unknown'}


def get_mounts_status() -> Dict[str, Any]:
    """Get status for all configured mounts."""
    try:
        cfg = load_sshfs_config()
        mounts = []
        
        for mount in cfg.get('mounts', []):
            status = check_mount_status(mount.get('name', ''))
            target_info = _resolve_connection_target(mount)
            key_name = str(mount.get('ssh_key') or '').strip()
            key_path = _get_ssh_keys_dir() / f'{key_name}.key'
            mount_cmd = ''
            if key_name and key_path.exists():
                try:
                    cmd = _build_sshfs_mount_command(
                        mount,
                        key_path,
                        Path(str(mount.get('local_mount') or '')),
                    )
                    mount_cmd = shlex.join(cmd)
                except Exception:
                    mount_cmd = ''
            mounts.append({
                'name': mount.get('name'),
                'connection_mode': _normalize_connection_mode(
                    mount.get('connection_mode', 'direct')),
                'manual_mode': True,
                'ssh_config_host': mount.get('ssh_config_host', ''),
                'remote_host': mount.get('remote_host'),
                'remote_path': mount.get('remote_path'),
                'local_mount': mount.get('local_mount'),
                'ssh_key': mount.get('ssh_key'),
                'remote_user': mount.get('remote_user', 'root'),
                'display_target': target_info.get('display_target', ''),
                'mount_command': mount_cmd,
                'status': status,
            })
        
        return {'ok': True, 'mounts': mounts}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'mounts': []}


def test_ssh_connection(
    connection_mode: str,
    remote_host: str,
    remote_user: str,
    ssh_config_host: str,
    remote_path: str,
    ssh_key_name: str,
) -> Dict[str, Any]:
    """Validate SSH auth and optional remote-path accessibility."""
    connection_mode = _normalize_connection_mode(connection_mode)
    remote_host = str(remote_host or '').strip()
    remote_user = str(remote_user or '').strip() or 'root'
    ssh_config_host = str(ssh_config_host or '').strip()
    remote_path = str(remote_path or '').strip()
    ssh_key_name = str(ssh_key_name or '').strip()

    if not ssh_key_name:
        return {
            'ok': False,
            'error': 'SSH key is required for connection test.',
        }

    if connection_mode == 'ssh_config_host' and not ssh_config_host:
        return {'ok': False,
                'error': 'SSH config host is required for connection test.'}

    if connection_mode == 'direct' and not remote_host:
        return {'ok': False,
                'error': 'Remote host is required for connection test.'}

    key_path = _get_ssh_keys_dir() / f'{ssh_key_name}.key'
    if not key_path.exists():
        return {'ok': False, 'error': f'SSH key "{ssh_key_name}" not found.'}

    if connection_mode == 'ssh_config_host':
        target = ssh_config_host
    else:
        target = f'{remote_user}@{remote_host}'

    throttle_error = _throttle_ssh_target(target, action='test connection')
    if throttle_error:
        return {'ok': False, 'error': throttle_error}

    base_ssh_cmd = [
        'ssh',
        '-i', str(key_path),
        '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=accept-new',
        '-o', 'ConnectTimeout=8',
        target,
    ]

    # Use a single SSH session for the whole validation to avoid connection
    # bursts on hosts that enforce strict per-user limits.
    if remote_path:
        remote_cmd = (
            'echo SSH_OK && '
            f'test -d {shlex.quote(remote_path)} && '
            'echo PATH_OK && '
            f'ls -1 {shlex.quote(remote_path)} 2>/dev/null | head -1'
        )
    else:
        remote_cmd = 'echo SSH_OK'

    login = subprocess.run(
        base_ssh_cmd + ['sh', '-lc', remote_cmd],
        capture_output=True,
        text=True,
        timeout=12,
    )
    if login.returncode != 0:
        err = (login.stderr or login.stdout or 'Unknown SSH error').strip()
        return {'ok': False, 'error': f'SSH connection failed: {err}'}

    lines = [line.strip() for line in (login.stdout or '').splitlines()
             if line.strip()]
    has_ssh_ok = 'SSH_OK' in lines
    has_path_ok = 'PATH_OK' in lines

    if not remote_path:
        if has_ssh_ok:
            return {'ok': True, 'message': 'SSH authentication succeeded.'}
        # Some ssh_config targets use wrappers/forced commands that can suppress
        # marker output even when auth succeeds. A zero return code is enough
        # to confirm login in this case.
        return {
            'ok': True,
            'message': (
                'SSH authentication succeeded '
                '(login marker output was not returned by remote shell).'
            ),
        }

    if not has_path_ok:
        # Fallback probe: on some hosts marker echoes may be filtered, so test
        # the directory directly in a second call.
        path_probe = subprocess.run(
            base_ssh_cmd + ['test', '-d', remote_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if path_probe.returncode != 0:
            return {
                'ok': False,
                'error': (
                    f'SSH login worked, but remote path "{remote_path}" '
                    f'is not accessible as a directory.'
                ),
            }
    first_item = ''
    try:
        marker_index = lines.index('PATH_OK')
        if marker_index + 1 < len(lines):
            first_item = lines[marker_index + 1]
    except ValueError:
        first_item = ''
    return {
        'ok': True,
        'message': (
            f'SSH authentication succeeded and remote path "{remote_path}" is accessible.'
        ),
        'sample_entry': first_item,
    }


def health_check() -> Dict[str, Any]:
    """
    Check health of all SSHFS mounts.

    :return: dict with status, message
    :rtype: dict
    """
    try:
        cfg = load_sshfs_config()
        mounts = cfg.get('mounts', [])
        
        if not mounts:
            return {'status': 'ok', 'message': 'No SSHFS mounts configured.'}
        
        status_data = get_mounts_status()
        if not status_data['ok']:
            return {'status': 'error', 'message': f'Failed to check mount status: {status_data["error"]}'}
        
        all_mounts = status_data.get('mounts', [])
        mounted_count = sum(
            1 for m in all_mounts if m['status'].get('mounted'))
        failed_count = sum(
            1 for m in all_mounts if m['status'].get('ok') == False)
        
        if failed_count > 0:
            return {
                'status': 'error',
                'message': f'{failed_count} of {len(all_mounts)} SSHFS mounts have connection issues.',
            }
        
        if mounted_count == len(all_mounts):
            return {'status': 'ok', 'message': f'All {len(all_mounts)} SSHFS mounts are mounted.'}
        
        unmounted = len(all_mounts) - mounted_count
        return {
            'status': 'warning',
            'message': f'{unmounted} of {len(all_mounts)} SSHFS mounts are not currently mounted.',
        }
    except Exception as e:
        return {'status': 'error',
                'message': f'SSHFS health check failed: {str(e)}'}

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
