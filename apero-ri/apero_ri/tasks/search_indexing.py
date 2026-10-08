#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Daily GLOBAL task refreshing local Search property indexes."""

from pathlib import Path
from typing import Any

from apero_ri.core import auth, search_index
from apero_ri.tasks import apero_async

PARAM_LIST = ['LOCAL_DATA_DIR', 'TASK_LOGGER']
APERO_PROFILE_PARAM_LIST = []
DEFAULT_FREQUENCY = 24.0
DEFAULT_ENABLED = True
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS = []


class SearchIndexingTask(apero_async.AperoAsyncTask):
    """Refresh per-profile indexes without hydrating APERO configuration."""

    def __init__(self, status: str = 'pending') -> None:
        """Initialize a task with the supplied scheduler status.

        :param status: Initial async task status.
        :return: None.
        """
        super().__init__('Search Indexing',
                         'Refresh local Search property keys', status)

    def run_job(self, params: dict[str, Any]) -> None:
        """Scan every configured profile and log progress or failures.

        :param params: LOCAL_DATA_DIR, TASK_LOGGER, optional STOP_EVENT.
        :return: None; raises RuntimeError if any profile refresh failed.
        """
        base_dir = Path(params['LOCAL_DATA_DIR']).expanduser()
        logger = params.get('TASK_LOGGER')
        stop_event = params.get('STOP_EVENT')
        profiles = auth.load_apero_profiles(hydrate=False)
        failures = []
        for instrument, entries in profiles.items():
            if not isinstance(entries, dict):
                continue
            for profile_id in entries:
                if stop_event is not None and stop_event.is_set():
                    return
                profile = dict(instrument=instrument, profile_id=profile_id)
                try:
                    refreshed = search_index.refresh_profile(base_dir, profile)
                    state = 'refreshed' if refreshed else 'already refreshing'
                    message = f'{instrument}/{profile_id}: {state}'
                except Exception as exc:
                    message = f'{instrument}/{profile_id}: failed: {exc}'
                    failures.append(message)
                if callable(logger):
                    logger(message)
        if failures:
            raise RuntimeError('\n'.join(failures))