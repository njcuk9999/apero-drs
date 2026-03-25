#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Task registry with resilient imports.

A task module import failure should never crash Flask.  Failed imports
are captured in IMPORT_ERRORS and the task key is backed by a
placeholder class that reports the import problem in the error panel.
"""

# =============================================================================
# Imports
# =============================================================================
import traceback
from importlib import import_module
from typing import Any, Dict

from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks'

# errors recorded for any task whose module could not be imported
IMPORT_ERRORS: Dict[str, str] = {}

# =============================================================================
# Define functions
# =============================================================================
def _failed_task_class(task_key: str, module_name: str) -> type:
    """
    Build a placeholder task class for a module that failed to import.

    :param task_key: str, registry key for the task
    :param module_name: str, module that failed to load

    :return: type, a sub-class of AperoAsyncTask that raises on run
    :rtype: type
    """

    class _FailedImportTask(apero_async.AperoAsyncTask):
        def __init__(self, status: str = 'pending'):
            super().__init__(
                f'{task_key} (Import Error)',
                f'Task unavailable: failed to import {module_name}',
                status,
            )

        def run_job(self, params: Dict[str, Any]) -> None:
            """Raise RuntimeError to signal the import failure."""
            message = IMPORT_ERRORS.get(
                task_key, 'Unknown task import error.'
            )
            self.info = (
                '## Task Import Error\n\n'
                f'**Task key**: `{task_key}`  \n'
                f'**Module**: `{module_name}`\n\n'
                f'```\n{message}\n```\n'
            )
            raise RuntimeError(message)

    return _FailedImportTask


def _register_task(task_key: str,
                   module_name: str,
                   class_name: str,
                   task_type_fallback: str = 'INSTRUMENT') -> Dict[str, Any]:
    """
    Import one task module safely and return normalised task metadata.

    :param task_key: str, registry key used in TASK_LIST / P_LIST etc.
    :param module_name: str, module name inside apero_ri.tasks
    :param class_name: str, task class to load from that module
    :param task_type_fallback: str, TASK_TYPE to use on import error

    :return: dict containing task_cls, param_list, ap_list, frequency,
             enabled, and task_type
    :rtype: dict
    """
    try:
        module = import_module(f'apero_ri.tasks.{module_name}')
        task_cls = getattr(module, class_name)
        return {
            'task_cls': task_cls,
            'param_list': list(getattr(module, 'PARAM_LIST', [])),
            'ap_list': list(
                getattr(module, 'APERO_PROFILE_PARAM_LIST', [])
            ),
            'frequency': float(
                getattr(module, 'DEFAULT_FREQUENCY', 24.0)
            ),
            'enabled': bool(getattr(module, 'DEFAULT_ENABLED', False)),
            'task_type': str(
                getattr(module, 'TASK_TYPE', task_type_fallback)
            ),
        }
    except Exception:
        IMPORT_ERRORS[task_key] = traceback.format_exc()
        return {
            'task_cls': _failed_task_class(task_key, module_name),
            'param_list': ['LOCAL_DATA_DIR', 'INSTRUMENT', 'TASK_CONFIG'],
            'ap_list': [],
            'frequency': 24.0,
            'enabled': False,
            'task_type': task_type_fallback,
        }


# =============================================================================
# Define task registry
# =============================================================================
TASK_LIST: Dict[str, Any] = {}
P_LIST: Dict[str, Any] = {}
AP_LIST: Dict[str, Any] = {}
FREQ: Dict[str, Any] = {}
ENABLED: Dict[str, Any] = {}
TYPE: Dict[str, Any] = {}

# (task_key, module_name, class_name, task_type)
_TASK_DEFS = [
    ('ARI_LOCAL_DATA_BACKUP',
     'apero_backup', 'AperoLocalDataBackupTask', 'GLOBAL'),
    ('APERO_OBJECT_TABLE',
     'apero_object_table', 'AperoObjectTableTask', 'INSTRUMENT'),
    ('APERO_OBS_TABLE',
     'apero_observation_table', 'AperoObservationTableTask', 'INSTRUMENT'),
    ('APERO_OBJECT_QUERY',
     'apero_object_query', 'AperoObjectQueryTask', 'INSTRUMENT'),
    ('APERO_QC_STATIS',
     'apero_qc_stats', 'AperoQCStats', 'INSTRUMENT'),
]

for _task_key, _module_name, _class_name, _fallback_type in _TASK_DEFS:
    _entry = _register_task(
        _task_key, _module_name, _class_name, _fallback_type
    )
    TASK_LIST[_task_key] = _entry['task_cls']
    P_LIST[_task_key] = _entry['param_list']
    AP_LIST[_task_key] = _entry['ap_list']
    FREQ[_task_key] = _entry['frequency']
    ENABLED[_task_key] = _entry['enabled']
    TYPE[_task_key] = _entry['task_type']

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
