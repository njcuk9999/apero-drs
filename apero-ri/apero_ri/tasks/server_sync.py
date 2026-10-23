#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - GLOBAL async tasks: synchronise this server with its peers.

``SERVER_SYNC`` runs every 15 minutes by default and syncs every record
category (users, groups, profiles, ...) with each peer that has been
reviewed in the Server Sync page (Run tab) and has automatic sync
switched on. ``SERVER_SYNC_TASK_DATA`` does the same for the large,
regenerable ``tasks/`` outputs on a slower schedule.

Peers that need review, new conflicts and failures are reported in the
task log and as notifications to super admins.

Created on 2026-10-22

@author: cook
"""
from typing import Any, Dict, List

from apero_ri.core.server_sync import engine
from apero_ri.core.server_sync import store
from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.server_sync'
PARAM_LIST = ['LOCAL_DATA_DIR', 'TASK_LOGGER']
APERO_PROFILE_PARAM_LIST = []
# 15 minutes
DEFAULT_FREQUENCY = 0.25
DEFAULT_ENABLED = False
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS = []


def _sync_all(kind: str, params: Dict[str, Any]) -> List[str]:
    """
    Sync every approved peer with automatic sync switched on.

    :param kind: str, 'records' or 'task_files'
    :param params: dict, task parameters (TASK_LOGGER, STOP_EVENT)

    :return: list of failure messages
    :rtype: list
    """
    logger = params.get('TASK_LOGGER')
    stop_event = params.get('STOP_EVENT')

    def log(msg: str) -> None:
        if callable(logger):
            logger(msg)

    failures = []
    for peer_id, peer in store.load_peers().items():
        if stop_event is not None and stop_event.is_set():
            break
        label = peer.get('label') or peer_id
        if not peer.get('approved') or not peer.get('auto_sync'):
            log(f'{label}: skipped (needs review / automatic sync off)')
            continue
        if kind == 'task_files' and not engine.categories_for(peer, kind):
            log(f'{label}: task outputs not enabled for this peer')
            continue
        log(f'{label}: syncing {kind} ({peer.get("mode")})')
        try:
            run_kwargs = dict(dry_run=False, kind=kind, actor='system',
                              auto=True, logger=log)
            summary = engine.run_peer(peer_id, **run_kwargs)
        except store.SyncBusy as exc:
            log(f'{label}: {exc}')
            continue
        counts = summary.get('categories', dict())
        moved = sum(c.get('pull', 0) + c.get('push', 0) + c.get('merge', 0)
                    for c in counts.values())
        log(f'{label}: {moved} change(s), {summary["conflicts"]} '
            f'conflict(s) skipped, {summary["seconds"]}s')
        for warning in summary.get('warnings', []):
            log(f'{label}: WARNING {warning}')
        if not summary['ok']:
            failures.append(f'{label}: ' + '; '.join(summary['errors'][:5]))
    return failures


class ServerSyncTask(apero_async.AperoAsyncTask):
    """Sync record data with every approved peer."""

    def __init__(self, status: str = 'pending') -> None:
        """
        Initialise the task.

        :param status: str, initial scheduler status

        :return: None
        """
        super().__init__('Server Sync',
                         'Synchronise users, groups, profiles and other '
                         'records with peer ARI servers', status)

    def run_job(self, params: Dict[str, Any]) -> None:
        """
        Run the sync for every approved peer.

        :param params: dict, task parameters

        :return: None; raises RuntimeError when any peer failed
        """
        failures = _sync_all('records', params)
        if failures:
            raise RuntimeError('\n'.join(failures))


class ServerSyncTaskDataTask(apero_async.AperoAsyncTask):
    """Sync derived tasks/ outputs with every approved peer."""

    def __init__(self, status: str = 'pending') -> None:
        """
        Initialise the task.

        :param status: str, initial scheduler status

        :return: None
        """
        super().__init__('Server Sync (task outputs)',
                         'Synchronise derived tasks/ outputs with peer ARI '
                         'servers', status)

    def run_job(self, params: Dict[str, Any]) -> None:
        """
        Run the task-output sync for every approved peer.

        :param params: dict, task parameters

        :return: None; raises RuntimeError when any peer failed
        """
        failures = _sync_all('task_files', params)
        if failures:
            raise RuntimeError('\n'.join(failures))


# =============================================================================
# End of code
# =============================================================================
