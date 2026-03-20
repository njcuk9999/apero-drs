#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Task registry with resilient imports.

A task module import failure should never crash Flask. Failed imports are
captured in IMPORT_ERRORS and the task key is backed by a placeholder task
class that reports the import problem in the task error panel.
"""

import traceback
from importlib import import_module
from typing import Any, Dict, Optional

from apero_ri.tasks import apero_async


IMPORT_ERRORS: Dict[str, str] = {}


def _failed_task_class(task_key: str, module_name: str):
    """Build a placeholder task class when module import fails."""

    class _FailedImportTask(apero_async.AperoAsyncTask):
        def __init__(self, status='pending'):
            super().__init__(
                f'{task_key} (Import Error)',
                f'Task unavailable: failed to import {module_name}',
                status,
            )

        def run_job(self, params: Dict[str, Any]):
            message = IMPORT_ERRORS.get(task_key, 'Unknown task import error.')
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
    """Import one task module safely and return normalized task metadata."""
    try:
        module = import_module(f'apero_ri.tasks.{module_name}')
        task_cls = getattr(module, class_name)
        return {
            'task_cls': task_cls,
            'param_list': list(getattr(module, 'PARAM_LIST', [])),
            'ap_list': list(getattr(module, 'APERO_PROFILE_PARAM_LIST', [])),
            'frequency': float(getattr(module, 'DEFAULT_FREQUENCY', 24.0)),
            'enabled': bool(getattr(module, 'DEFAULT_ENABLED', False)),
            'task_type': str(getattr(module, 'TASK_TYPE', task_type_fallback)),
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
# TASK LIST
# =============================================================================
TASK_LIST: Dict[str, Any] = {}
P_LIST: Dict[str, Any] = {}
AP_LIST: Dict[str, Any] = {}
FREQ: Dict[str, Any] = {}
ENABLED: Dict[str, Any] = {}
TYPE: Dict[str, Any] = {}

_TASK_DEFS = [
    ('ARI_LOCAL_DATA_BACKUP', 'apero_backup', 'AperoLocalDataBackupTask', 'GLOBAL'),
    ('APERO_OBJECT_TABLE', 'apero_object_table', 'AperoObjectTableTask', 'INSTRUMENT'),
    ('APERO_OBS_TABLE', 'apero_observation_table', 'AperoObservationTableTask', 'INSTRUMENT'),
    ('APERO_OBJECT_QUERY', 'apero_object_query', 'AperoObjectQueryTask', 'INSTRUMENT'),
]

for _task_key, _module_name, _class_name, _fallback_type in _TASK_DEFS:
    _entry = _register_task(_task_key, _module_name, _class_name, _fallback_type)
    TASK_LIST[_task_key] = _entry['task_cls']
    P_LIST[_task_key] = _entry['param_list']
    AP_LIST[_task_key] = _entry['ap_list']
    FREQ[_task_key] = _entry['frequency']
    ENABLED[_task_key] = _entry['enabled']
    TYPE[_task_key] = _entry['task_type']
