#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - GLOBAL async task: keep prebuilt documentation snapshots fresh.

Fingerprints the documentation sources of every version and rebuilds
(rendered pages, sidebars, search index) only when something changed,
writing the result to ``{LOCAL_DATA_DIR}/docs_cache`` so documentation
requests are always served from a prebuilt snapshot.

Created on 2026-11-26

@author: cook
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from typing import Any, Dict, List

from apero_ri.core import docs
from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.docs_snapshot'

# Module-level task metadata consumed by the registry
PARAM_LIST = ['LOCAL_DATA_DIR', 'TASK_LOGGER']
APERO_PROFILE_PARAM_LIST: List[str] = []
# Fingerprint check is cheap; a rebuild only happens when sources changed
DEFAULT_FREQUENCY = 0.25
DEFAULT_ENABLED = True
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS: List[str] = []


# =============================================================================
# Define classes
# =============================================================================
class DocsSnapshotTask(apero_async.AperoAsyncTask):
    """Rebuild stale documentation snapshots in the background."""

    def __init__(self, status: str = 'pending') -> None:
        """Initialize the task with its display metadata.

        :param status: str, initial async task status

        :return: None
        """
        name = 'Documentation Snapshot'
        description = ('Prebuild rendered documentation pages, sidebars '
                       'and the search index when sources change')
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:
        """Refresh every documentation version's snapshot if stale.

        :param params: dict, LOCAL_DATA_DIR and optional TASK_LOGGER

        :return: None
        """
        docs.set_snapshot_dir(Path(params['LOCAL_DATA_DIR']).expanduser())
        statuses = docs.refresh_snapshots(logger=params.get('TASK_LOGGER'))
        lines = ['## Documentation Snapshot', '']
        for version, status in statuses.items():
            lines.append('- **{0}**: {1}'.format(version, status))
        self.info = '\n'.join(lines) + '\n'


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
