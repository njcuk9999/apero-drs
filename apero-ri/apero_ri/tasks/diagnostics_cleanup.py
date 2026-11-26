#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scheduled cleanup of expired private diagnostic reports."""

from pathlib import Path
from typing import Any, Dict, List

from aperocore import drs_lang
from apero_ri.core import diagnostic_jobs
from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.diagnostics_cleanup'
PARAM_LIST = ['LOCAL_DATA_DIR']
APERO_PROFILE_PARAM_LIST: List[str] = []
DEFAULT_FREQUENCY = 1.0
DEFAULT_ENABLED = True
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS: List[str] = []

# =============================================================================
# Define classes
# =============================================================================
class DiagnosticsCleanupTask(apero_async.AperoAsyncTask):
    """Remove expired saved diagnostic reports on the global task schedule."""

    def __init__(self, status: str = 'pending') -> None:
        """Initialize the scheduled cleanup task.

        :param status: Initial task status.
        :return: None.
        """
        name = str(drs_lang.textentry('ARI_DIAGNOSTICS_CLEANUP_NAME'))
        description = str(drs_lang.textentry('ARI_DIAGNOSTICS_CLEANUP_DESC'))
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:
        """Remove expired reports from the active ARI data directory.

        :param params: Task parameters including LOCAL_DATA_DIR.
        :return: None.
        """
        count = diagnostic_jobs.cleanup_expired(Path(params['LOCAL_DATA_DIR']))
        self.info = str(drs_lang.textentry('ARI_DIAGNOSTICS_CLEANUP_COUNT',
                                          args=[count]))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================