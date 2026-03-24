"""APERO RI: SSHFS mount management backend.

Configuration is stored in {ARI_DIR}/admin/sshfs.yaml.
SSH keys are stored in {ARI_DIR}/secret/ssh_keys/{key_name}.key.
Mount status is checked via subprocess commands.
"""

from __future__ import annotations

import os
import subprocess
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import re

import yaml


def _normalize_connection_mode(value: str) -> str:
    mode = str(value or 'direct').strip().lower()
    return mode if mode in {'direct', 'ssh_config_host'} else 'direct'


def _resolve_connection_target(mount_config: Dict[str, Any]) -> Dict[str, str]:
    """Resolve connection target details for direct or ssh-config modes."""
    mode = _normalize_connection_mode(mount_config.get('connection_mode', 'direct'))
    remote_path = str(mount_config.get('remote_path') or '').strip()

    if mode == 'ssh_config_host':
        ssh_config_host = str(mount_config.get('ssh_config_host') or '').strip()
        return {
            'mode': mode,
            'ssh_target': ssh_config_host,
            'sshfs_target': f'{ssh_config_host}:{remote_path}' if ssh_config_host and remote_path else '',
            'display_target': ssh_config_host,
        }

    remote_user = str(mount_config.get('remote_user') or '').strip() or 'root'
    remote_host = str(mount_config.get('remote_host') or '').strip()
    ssh_target = f'{remote_user}@{remote_host}' if remote_host else ''
    return {
        'mode': mode,
        'ssh_target': ssh_target,
        'sshfs_target': f'{ssh_target}:{remote_path}' if ssh_target and remote_path else '',
        'display_target': ssh_target,
    }


def _get_sshfs_config_path() -> Path:
    """Get path to SSHFS configuration file."""
    ari_dir = os.environ.get('ARI_DIR', os.path.expanduser('~/.ari'))
    return Path(ari_dir) / 'admin' / 'sshfs.yaml'


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
                        'mtime': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
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


def add_mount(mount_config: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new SSHFS mount configuration."""
    connection_mode = _normalize_connection_mode(
        mount_config.get('connection_mode', 'direct')
    )
    mount_config['connection_mode'] = connection_mode

    required = ['name', 'remote_path', 'local_mount', 'ssh_key']
    for field in required:
        if not mount_config.get(field):
            return {'ok': False, 'error': f'Missing required field: {field}'}

    if connection_mode == 'ssh_config_host':
        if not mount_config.get('ssh_config_host'):
            return {'ok': False, 'error': 'Missing required field: ssh_config_host'}
        mount_config['remote_user'] = ''
        mount_config['remote_host'] = ''
    else:
        if not mount_config.get('remote_host'):
            return {'ok': False, 'error': 'Missing required field: remote_host'}
        mount_config['ssh_config_host'] = ''

    try:
        cfg = load_sshfs_config()
        
        # Check if mount name already exists
        existing = [m for m in cfg.get('mounts', []) if m.get('name') == mount_config['name']]
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
        mount = next((m for m in cfg.get('mounts', []) if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.'}
        
        # Unmount first if currently mounted
        if mount.get('status') == 'mounted':
            unmount_result = unmount_sshfs(mount_name)
            if not unmount_result['ok']:
                return {'ok': False, 'error': f'Cannot delete mounted volume. Unmount first: {unmount_result["error"]}'}
        
        cfg['mounts'] = [m for m in cfg['mounts'] if m.get('name') != mount_name]
        result = save_sshfs_config(cfg)
        
        if result['ok']:
            return {'ok': True, 'message': f'Mount "{mount_name}" deleted successfully.'}
        return result
    except Exception as e:
        return {'ok': False, 'error': f'Failed to delete mount: {str(e)}'}


def update_mount(original_name: str, mount_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing SSHFS mount configuration."""
    original_name = str(original_name or '').strip()
    if not original_name:
        return {'ok': False, 'error': 'Original mount name is required.'}

    connection_mode = _normalize_connection_mode(
        mount_config.get('connection_mode', 'direct')
    )
    mount_config['connection_mode'] = connection_mode

    required = ['name', 'remote_path', 'local_mount', 'ssh_key']
    for field in required:
        if not mount_config.get(field):
            return {'ok': False, 'error': f'Missing required field: {field}'}

    if connection_mode == 'ssh_config_host':
        if not mount_config.get('ssh_config_host'):
            return {'ok': False, 'error': 'Missing required field: ssh_config_host'}
        mount_config['remote_user'] = ''
        mount_config['remote_host'] = ''
    else:
        if not mount_config.get('remote_host'):
            return {'ok': False, 'error': 'Missing required field: remote_host'}
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
            return {'ok': False, 'error': 'Unmount this mount before editing it.'}

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


def mount_sshfs(mount_name: str) -> Dict[str, Any]:
    """Mount an SSHFS volume."""
    try:
        cfg = load_sshfs_config()
        mount = next((m for m in cfg.get('mounts', []) if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.'}
        
        if mount.get('status') == 'mounted':
            return {'ok': True, 'message': f'Mount "{mount_name}" is already mounted.'}
        
        # Get SSH key path
        ssh_key = mount.get('ssh_key')
        ssh_keys_dir = _get_ssh_keys_dir()
        key_path = ssh_keys_dir / f'{ssh_key}.key'
        
        if not key_path.exists():
            return {'ok': False, 'error': f'SSH key "{ssh_key}" not found.'}
        
        # Create local mount directory
        local_mount = Path(mount.get('local_mount', ''))
        local_mount.mkdir(parents=True, exist_ok=True)

        target_info = _resolve_connection_target(mount)
        remote_target = target_info['sshfs_target']
        if not remote_target:
            return {'ok': False, 'error': 'Mount target is incomplete.'}

        # Build sshfs command
        cmd = [
            'sshfs',
            '-o', f'IdentityFile={key_path}',
            '-o', 'BatchMode=yes',
            '-o', 'StrictHostKeyChecking=accept-new',
            '-o', 'reconnect,ServerAliveInterval=15,ServerAliveCountMax=3',
            remote_target,
            str(local_mount),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            error = result.stderr or result.stdout or 'Unknown error'
            return {'ok': False, 'error': f'Failed to mount: {error}'}
        
        # Update config
        mount['status'] = 'mounted'
        mount['mounted_at'] = datetime.now(tz=timezone.utc).isoformat()
        save_sshfs_config(cfg)
        
        return {'ok': True, 'message': f'Mount "{mount_name}" mounted successfully.'}
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'Mount operation timed out.'}
    except Exception as e:
        return {'ok': False, 'error': f'Failed to mount: {str(e)}'}


def unmount_sshfs(mount_name: str) -> Dict[str, Any]:
    """Unmount an SSHFS volume."""
    try:
        cfg = load_sshfs_config()
        mount = next((m for m in cfg.get('mounts', []) if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.'}
        
        if mount.get('status') != 'mounted':
            return {'ok': True, 'message': f'Mount "{mount_name}" is not mounted.'}
        
        local_mount = mount.get('local_mount')
        
        # Try umount
        result = subprocess.run(['umount', local_mount], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            # Try force unmount
            result = subprocess.run(['umount', '-l', local_mount], capture_output=True, text=True, timeout=10)
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


def check_mount_status(mount_name: str) -> Dict[str, Any]:
    """Check the status of an SSHFS mount."""
    try:
        cfg = load_sshfs_config()
        mount = next((m for m in cfg.get('mounts', []) if m.get('name') == mount_name), None)
        
        if not mount:
            return {'ok': False, 'error': f'Mount "{mount_name}" not found.', 'status': 'unknown'}
        
        local_mount = mount.get('local_mount')
        
        # Check if mount point is actually mounted
        result = subprocess.run(
            ['mountpoint', '-q', local_mount],
            capture_output=True,
            timeout=5
        )
        
        is_mounted = result.returncode == 0
        
        # Try to list directory contents
        file_count = 0
        last_error = None
        
        try:
            local_path = Path(local_mount)
            if local_path.exists() and is_mounted:
                file_count = len(list(local_path.iterdir()))
        except Exception as e:
            last_error = str(e)
        
        status_data = {
            'ok': True,
            'mounted': is_mounted,
            'local_mount': local_mount,
            'file_count': file_count if is_mounted else 0,
            'mounted_at': mount.get('mounted_at'),
        }
        
        if last_error:
            status_data['warning'] = last_error
        
        return status_data
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'Status check timed out.', 'status': 'unknown'}
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
            mounts.append({
                'name': mount.get('name'),
                'connection_mode': _normalize_connection_mode(mount.get('connection_mode', 'direct')),
                'ssh_config_host': mount.get('ssh_config_host', ''),
                'remote_host': mount.get('remote_host'),
                'remote_path': mount.get('remote_path'),
                'local_mount': mount.get('local_mount'),
                'ssh_key': mount.get('ssh_key'),
                'remote_user': mount.get('remote_user', 'root'),
                'display_target': target_info.get('display_target', ''),
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
        return {'ok': False, 'error': 'SSH config host is required for connection test.'}

    if connection_mode == 'direct' and not remote_host:
        return {'ok': False, 'error': 'Remote host is required for connection test.'}

    key_path = _get_ssh_keys_dir() / f'{ssh_key_name}.key'
    if not key_path.exists():
        return {'ok': False, 'error': f'SSH key "{ssh_key_name}" not found.'}

    if connection_mode == 'ssh_config_host':
        target = ssh_config_host
    else:
        target = f'{remote_user}@{remote_host}'

    base_ssh_cmd = [
        'ssh',
        '-i', str(key_path),
        '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=accept-new',
        '-o', 'ConnectTimeout=8',
        target,
    ]

    # Step 1: Validate login/auth only.
    login = subprocess.run(
        base_ssh_cmd + ['echo', 'SSH_OK'],
        capture_output=True,
        text=True,
        timeout=12,
    )
    if login.returncode != 0:
        err = (login.stderr or login.stdout or 'Unknown SSH error').strip()
        return {'ok': False, 'error': f'SSH connection failed: {err}'}

    # Step 2: Optionally validate remote path exists and is readable.
    if not remote_path:
        return {'ok': True, 'message': 'SSH authentication succeeded.'}

    path_check = subprocess.run(
        base_ssh_cmd + ['test', '-d', remote_path],
        capture_output=True,
        text=True,
        timeout=12,
    )
    if path_check.returncode != 0:
        return {
            'ok': False,
            'error': f'SSH login worked, but remote path "{remote_path}" is not accessible as a directory.',
        }

    sample_cmd = f'ls -1 {shlex.quote(remote_path)} 2>/dev/null | head -1'
    sample = subprocess.run(
        base_ssh_cmd + ['sh', '-lc', sample_cmd],
        capture_output=True,
        text=True,
        timeout=12,
    )
    first_item = (sample.stdout or '').strip()
    return {
        'ok': True,
        'message': (
            f'SSH authentication succeeded and remote path "{remote_path}" is accessible.'
        ),
        'sample_entry': first_item,
    }


def health_check() -> Dict[str, Any]:
    """Check health of all SSHFS mounts."""
    try:
        cfg = load_sshfs_config()
        mounts = cfg.get('mounts', [])
        
        if not mounts:
            return {'status': 'ok', 'message': 'No SSHFS mounts configured.'}
        
        status_data = get_mounts_status()
        if not status_data['ok']:
            return {'status': 'error', 'message': f'Failed to check mount status: {status_data["error"]}'}
        
        all_mounts = status_data.get('mounts', [])
        mounted_count = sum(1 for m in all_mounts if m['status'].get('mounted'))
        failed_count = sum(1 for m in all_mounts if m['status'].get('ok') == False)
        
        if failed_count > 0:
            return {
                'status': 'error',
                'message': f'{failed_count} of {len(all_mounts)} SSHFS mounts have connection issues.',
            }
        
        if mounted_count == len(all_mounts):
            return {'status': 'ok', 'message': f'All {len(all_mounts)} SSHFS mounts are mounted and accessible.'}
        
        unmounted = len(all_mounts) - mounted_count
        return {
            'status': 'warning',
            'message': f'{unmounted} of {len(all_mounts)} SSHFS mounts are not currently mounted.',
        }
    except Exception as e:
        return {'status': 'error', 'message': f'SSHFS health check failed: {str(e)}'}
