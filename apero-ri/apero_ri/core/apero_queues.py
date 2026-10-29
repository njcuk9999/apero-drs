#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - APERO queue dashboard definitions.

An APERO queue definition describes how ARI reaches one running
``apero_queue.py gui`` dashboard: an SSH local forward (same mechanism as
the DB SSH tunnels) plus the APERO profile the queue belongs to (used to
decide which monitors can see it).

Created on 2026-10-28

@author: cook
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

import yaml

from apero_ri.core import auth

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.apero_queues'
# file (inside the admin general directory) storing the definitions
QUEUES_FILENAME = 'apero_queues.yaml'
# tunnel state sub-directory (kept apart from db_tunnels so the single DB
#   tunnel policy never closes a queue tunnel)
TUNNEL_STATE_SUBDIR = 'queue_tunnels'
# valid definition names
NAME_PATTERN = re.compile(r'^[A-Za-z0-9_\-]+$')
# valid ssh modes (see database setup)
SSH_MODES = ('apero', 'simple')
# queue gui POST routes (api/<action>) that can be restricted for monitors
#   value = (label, css selectors hidden in the embedded dashboard)
QUEUE_ACTIONS: Dict[str, tuple] = dict(
    generate=('Generate (apero_processing)', '#btn-generate'),
    run=('Run tasks', '#btn-run'),
    batch=('Batch (sbatch)', '#btn-batch'),
    chain=('Chain (Slurm arrays)', '#btn-chain'),
    action=('Queue actions (retry/stop/clear)',
            '#action-table .action-cell-run button, .row-actions'),
    reset=('Reset queue state(s)', '#act-row-reset'),
    template=('Save batch templates', '#btn-save-template'),
    process=('Stop processes / edit the process list',
             '.proc-actions, .proc-stop'),
    reset_data=('Reset all data (apero_reset)', '#act-row-reset-data'),
    shutdown=('Shutdown queue GUI', '#btn-shutdown'),
)
# actions monitors cannot use unless an admin allows them
DEFAULT_BLOCKED_ACTIONS = ['reset_data', 'shutdown']
# the default queue gui port (drs_queue_gui.GUI_DEFAULT_PORT)
DEFAULT_REMOTE_PORT = '8090'


# =============================================================================
# Define functions
# =============================================================================
def _queues_file() -> Path:
    """Return the definitions file path selected by ``auth.set_ari_dir``.

    :return: Path to the queue definitions YAML file.
    """
    return auth.ADMIN_GENERAL_DIR / QUEUES_FILENAME


def load_queues() -> Dict[str, dict]:
    """
    Load all APERO queue definitions.

    :return: dict, definition name -> definition dict
    """
    auth.ensure_ari_directory()
    path = _queues_file()
    if not path.exists():
        return dict()
    with open(path, 'r', encoding='utf-8') as qfile:
        data = yaml.safe_load(qfile)
    queues = data.get('queues', dict()) if isinstance(data, dict) else None
    if not isinstance(queues, dict):
        return dict()
    return {str(name): normalize_queue(qdef)
            for name, qdef in queues.items() if isinstance(qdef, dict)}


def save_queues(queues: Dict[str, dict]) -> None:
    """
    Save all APERO queue definitions.

    :param queues: dict, definition name -> definition dict

    :return: None
    """
    auth.ensure_ari_directory()
    with open(_queues_file(), 'w', encoding='utf-8') as qfile:
        yaml.safe_dump(dict(queues=queues), qfile, default_flow_style=False,
                       sort_keys=True)


def normalize_queue(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a definition with every field present and cleaned.

    :param raw: dict, the raw definition (from yaml or a request body)

    :return: dict, the normalized definition
    """
    def _str(key: str, default: str = '') -> str:
        """Read and trim one string field from the raw definition.

        :param key: Definition field to read.
        :param default: Value used when the field is empty or missing.
        :return: Trimmed field value or its default.
        """
        return str(raw.get(key, default) or default).strip()

    blocked = raw.get('blocked_actions', DEFAULT_BLOCKED_ACTIONS)
    if not isinstance(blocked, list):
        blocked = list(DEFAULT_BLOCKED_ACTIONS)
    blocked = sorted({str(item) for item in blocked
                      if str(item) in QUEUE_ACTIONS})
    ssh_mode = _str('ssh_mode', 'apero')
    return dict(
        label=_str('label'),
        ssh_config_host=_str('ssh_config_host'),
        remote_host=_str('remote_host', 'localhost'),
        remote_port=_str('remote_port', DEFAULT_REMOTE_PORT),
        local_port=_str('local_port'),
        ssh_mode=ssh_mode if ssh_mode in SSH_MODES else 'apero',
        instrument=_str('instrument').upper(),
        profile_id=_str('profile_id'),
        enabled=bool(raw.get('enabled', True)),
        blocked_actions=blocked,
        notes=_str('notes'),
    )


def validate_queue(name: str, qdef: Dict[str, Any],
                   queues: Dict[str, dict]) -> str:
    """
    Validate one definition before saving.

    :param name: str, the definition name
    :param qdef: dict, the normalized definition
    :param queues: dict, the existing definitions (for port clashes)

    :return: str, an error message ('' when valid)
    """
    if not NAME_PATTERN.match(name or ''):
        return 'name must be alphanumeric, dash, or underscore'
    for key in ('ssh_config_host', 'remote_host', 'local_port',
                'instrument', 'profile_id'):
        if not qdef.get(key):
            return '{0} is required'.format(key)
    for key in ('local_port', 'remote_port'):
        value = qdef.get(key, '')
        if not value.isdigit() or not 0 < int(value) < 65536:
            return '{0} must be a port number'.format(key)
    if '/' in qdef['remote_host'] or ':' in qdef['remote_host']:
        return 'remote_host must be a host name only'
    for other, odef in queues.items():
        if other != name and odef.get('local_port') == qdef['local_port']:
            return 'local_port {0} is already used by "{1}"'.format(
                qdef['local_port'], other)
    return ''


def tunnel_params(qdef: Dict[str, Any], local_data_dir: str) -> dict:
    """
    Build apero_async tunnel parameters for one definition.

    :param qdef: dict, the normalized definition
    :param local_data_dir: str, the ARI data directory (tunnel state)

    :return: dict, parameters for apero_async tunnel functions
    """
    return {
        'DATABASE_HOST': qdef['remote_host'],
        'DATABASE_PORT': qdef['local_port'],
        'DATABASE_SSH_CONFIG_HOST': qdef['ssh_config_host'],
        'DATABASE_SSH_LOCAL_PORT': qdef['local_port'],
        'DATABASE_SSH_REMOTE_PORT': qdef['remote_port'],
        'DATABASE_SSH_SIMPLE_MODE': qdef['ssh_mode'] == 'simple',
        'DATABASE_SSH_ALLOW_MULTIPLE': True,
        'TUNNEL_STATE_SUBDIR': TUNNEL_STATE_SUBDIR,
        'LOCAL_DATA_DIR': str(local_data_dir),
    }


def hidden_selectors(blocked: List[str]) -> List[str]:
    """
    Return the dashboard css selectors to hide for blocked actions.

    :param blocked: list of str, the blocked action names

    :return: list of str, css selectors
    """
    return [QUEUE_ACTIONS[action][1] for action in blocked
            if action in QUEUE_ACTIONS]


# =============================================================================
# End of code
# =============================================================================
