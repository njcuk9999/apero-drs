#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: local setup after a server sync.

Records that reference host-specific resources (APERO profile paths,
SSHFS mount points, DB tunnel SSH aliases / forward ports, local DB
hosts) arrive from another server flagged ``sync_needs_local_setup``.
This module lists them, lets an admin fill in the local values, and
helps add ``Host`` entries to this server's ``~/.ssh/config``.

Created on 2026-10-22

@author: cook
"""
import re
import shutil
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from apero_ri.core import auth
from apero_ri.core import sshfs_backend
from apero_ri.core.server_sync import adapters

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.server_sync.local_setup'
NEEDS = adapters.NEEDS_SETUP
# fields an admin may set per kind (validated by _FIELD_RULES)
EDITABLE = dict(
    tunnel=('ssh_config_host', 'local_port', 'ssh_mode'),
    local_db=('DATABASE_HOST', 'DATABASE_PORT'),
    sshfs=('connection_mode', 'ssh_config_host', 'local_mount'),
    profile=(),
)
# strict patterns: values end up in ssh commands / ssh config
_ALIAS = r'[A-Za-z0-9][A-Za-z0-9._\-]{0,62}'
_FIELD_RULES = dict(
    ssh_config_host=re.compile(rf'^{_ALIAS}$'),
    local_port=re.compile(r'^[0-9]{1,5}$'),
    ssh_mode=re.compile(r'^(apero|simple)$'),
    DATABASE_HOST=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._\-]{0,252}$'),
    DATABASE_PORT=re.compile(r'^[0-9]{1,5}$'),
    connection_mode=re.compile(r'^(direct|ssh_config_host)$'),
    local_mount=re.compile(r'^/[A-Za-z0-9._/\-]{1,250}$'),
)
# ssh config Host block field patterns (no whitespace => no injection)
_HOST_RULES = dict(
    alias=re.compile(rf'^{_ALIAS}$'),
    hostname=re.compile(r'^[A-Za-z0-9][A-Za-z0-9.\-:]{0,252}$'),
    user=re.compile(r'^[A-Za-z0-9._][A-Za-z0-9._\-]{0,63}$'),
    port=re.compile(r'^[0-9]{1,5}$'),
    identity_file=re.compile(r'^~?/[A-Za-z0-9._/\-]{1,250}$'),
    proxy_jump=re.compile(r'^[A-Za-z0-9._@:,\-]{1,250}$'),
)


# =============================================================================
# Define pending-item functions
# =============================================================================
def pending_items() -> List[Dict[str, Any]]:
    """
    List records that still need host-specific setup on this server.

    :return: list of dicts (kind, name, label, current values, editable)
    :rtype: list
    """
    rows = []
    kwargs = dict(hydrate=False, include_temporary=True)
    for inst, profiles in auth.load_apero_profiles(**kwargs).items():
        for pid, cfg in (profiles or {}).items():
            if isinstance(cfg, dict) and cfg.get(NEEDS):
                rows.append(_row('profile', f'{inst}/{pid}', dict(),
                                 'Set data paths on the APERO Profiles page, '
                                 'then enable the profile.'))
    data = auth.load_db_tunnels() or dict()
    for name, info in (data.get('tunnels') or {}).items():
        if info.get(NEEDS):
            rows.append(_row('tunnel', name, info,
                             'Pick an SSH alias that exists on this server '
                             'and a free local forward port.'))
    for name, info in (data.get('local_databases') or {}).items():
        if info.get(NEEDS):
            rows.append(_row('local_db', name, info,
                             'Database host/port as seen from this server.'))
    for mount in sshfs_backend.load_sshfs_config().get('mounts', []):
        if mount.get(NEEDS):
            rows.append(_row('sshfs', str(mount.get('name')), mount,
                             'Choose a local mount point and connection '
                             'method for this server.'))
    return rows


def _row(kind: str, name: str, record: Dict[str, Any],
         hint: str) -> Dict[str, Any]:
    """
    Build one pending-item row for the UI.

    :return: dict row
    :rtype: dict
    """
    row = dict()
    row['kind'] = kind
    row['name'] = name
    row['hint'] = hint
    row['editable'] = list(EDITABLE[kind])
    row['values'] = {k: record.get(k) for k in EDITABLE[kind]}
    return row


def update_item(kind: str, name: str, values: Dict[str, Any],
                done: bool = True) -> None:
    """
    Set local values on a synced record and clear its setup flag.

    :param kind: str, 'tunnel', 'local_db', 'sshfs' or 'profile'
    :param name: str, record name (inst/profile for profiles)
    :param values: dict, field -> value (only EDITABLE fields)
    :param done: bool, clear the needs-setup flag

    :return: None
    :raises ValueError: on unknown kind/record or invalid values
    """
    if kind not in EDITABLE:
        raise ValueError(f'Unknown kind {kind!r}')
    clean = dict()
    for field in EDITABLE[kind]:
        if field not in values:
            continue
        value = str(values[field] or '').strip()
        if value and not _FIELD_RULES[field].match(value):
            raise ValueError(f'Invalid value for {field}')
        clean[field] = value
    record, save = _locate(kind, name)
    record.update(clean)
    if done:
        record.pop(NEEDS, None)
    save()


def _locate(
    kind: str, name: str
) -> Tuple[Dict[str, Any], Callable[[], None]]:
    """
    Find a record by kind/name and return it with a save callback.

    :return: tuple (record dict, save callable)
    :raises ValueError: if the record does not exist
    """
    if kind == 'profile':
        kwargs = dict(hydrate=False, include_temporary=True)
        profiles = auth.load_apero_profiles(**kwargs)
        inst, _, pid = name.partition('/')
        record = (profiles.get(inst) or dict()).get(pid)
        if not isinstance(record, dict):
            raise ValueError(f'Unknown profile {name!r}')
        return record, lambda: auth.save_apero_profiles(profiles)
    if kind in ('tunnel', 'local_db'):
        data = auth.load_db_tunnels() or dict()
        section = 'tunnels' if kind == 'tunnel' else 'local_databases'
        record = (data.get(section) or dict()).get(name)
        if not isinstance(record, dict):
            raise ValueError(f'Unknown {kind} {name!r}')
        return record, lambda: auth.save_db_tunnels(data)
    cfg = sshfs_backend.load_sshfs_config()
    for mount in cfg.get('mounts', []):
        if mount.get('name') == name:
            return mount, lambda: sshfs_backend.save_sshfs_config(cfg)
    raise ValueError(f'Unknown mount {name!r}')


# =============================================================================
# Define ssh config helpers
# =============================================================================
def ssh_config_path() -> Path:
    """
    Return this server's ~/.ssh/config path.

    :return: Path
    :rtype: Path
    """
    return Path.home() / '.ssh' / 'config'


def ssh_hosts() -> List[str]:
    """
    List non-wildcard Host aliases from ~/.ssh/config.

    :return: sorted list of aliases
    :rtype: list
    """
    path = ssh_config_path()
    if not path.is_file():
        return []
    hosts = set()
    for raw in path.read_text(encoding='utf-8', errors='replace').splitlines():
        line = raw.strip()
        if not line.lower().startswith('host '):
            continue
        for token in line.split()[1:]:
            if not any(ch in token for ch in '*?!'):
                hosts.add(token)
    return sorted(hosts)


def build_host_block(fields: Dict[str, Any]) -> str:
    """
    Build a validated ssh config Host block.

    :param fields: dict with alias, hostname and optional user, port,
                   identity_file, proxy_jump

    :return: str, the Host block text
    :rtype: str
    :raises ValueError: if a field is missing or invalid
    """
    names = dict(hostname='HostName', user='User', port='Port',
                 identity_file='IdentityFile', proxy_jump='ProxyJump')
    clean = dict()
    for field, rule in _HOST_RULES.items():
        value = str(fields.get(field) or '').strip()
        if not value:
            continue
        if not rule.match(value):
            raise ValueError(f'Invalid {field}')
        clean[field] = value
    if 'alias' not in clean or 'hostname' not in clean:
        raise ValueError('alias and hostname are required')
    lines = [f'Host {clean["alias"]}']
    for field, directive in names.items():
        if field in clean:
            lines.append(f'    {directive} {clean[field]}')
    return '\n'.join(lines) + '\n'


def append_host_block(fields: Dict[str, Any]) -> Dict[str, str]:
    """
    Append a Host block to ~/.ssh/config after backing it up.

    :param fields: dict, see build_host_block

    :return: dict with 'block' and 'backup' (path or '')
    :rtype: dict
    :raises ValueError: if the alias already exists or fields are invalid
    """
    block = build_host_block(fields)
    alias = str(fields.get('alias')).strip()
    if alias in ssh_hosts():
        raise ValueError(f'Host {alias!r} already exists in ~/.ssh/config')
    path = ssh_config_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    backup = ''
    if path.exists():
        backup_path = path.with_name(f'config.ari-backup-{int(time.time())}')
        shutil.copy2(path, backup_path)
        backup = str(backup_path)
        existing = path.read_text(encoding='utf-8', errors='replace')
    else:
        existing = ''
    sep = '' if not existing or existing.endswith('\n\n') else '\n'
    if existing and not existing.endswith('\n'):
        sep = '\n\n'
    with open(path, 'a', encoding='utf-8') as fio:
        fio.write(f'{sep}# added by APERO RI server sync\n{block}')
    path.chmod(0o600)
    return dict(block=block, backup=backup)


# =============================================================================
# End of code
# =============================================================================
