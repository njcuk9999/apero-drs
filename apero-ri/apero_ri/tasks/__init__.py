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
__NAME__ = "apero_ri.tasks"

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
        def __init__(self, status: str = "pending"):
            super().__init__(
                f"{task_key} (Import Error)",
                f"Task unavailable: failed to import {module_name}",
                status,
            )

        def run_job(self, params: Dict[str, Any]) -> None:
            """Raise RuntimeError to signal the import failure."""
            message = IMPORT_ERRORS.get(task_key, "Unknown task import error.")
            self.info = (
                "## Task Import Error\n\n"
                f"**Task key**: `{task_key}`  \n"
                f"**Module**: `{module_name}`\n\n"
                f"```\n{message}\n```\n"
            )
            raise RuntimeError(message)

    return _FailedImportTask


def _register_task(
    task_key: str,
    module_name: str,
    class_name: str,
    task_type_fallback: str = "INSTRUMENT",
) -> Dict[str, Any]:
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
        module = import_module(f"apero_ri.tasks.{module_name}")
        task_cls = getattr(module, class_name)

        outdict = dict()
        outdict["task_cls"] = task_cls
        outdict["param_list"] = list(getattr(module, "PARAM_LIST", []))
        outdict["ap_list"] = list(
            getattr(module, "APERO_PROFILE_PARAM_LIST", [])
        )
        outdict["frequency"] = float(getattr(module, "DEFAULT_FREQUENCY", 24.0))
        outdict["enabled"] = bool(getattr(module, "DEFAULT_ENABLED", False))
        outdict["task_type"] = str(
            getattr(module, "TASK_TYPE", task_type_fallback)
        )
        outdict["use_subprocess"] = bool(
            getattr(module, "USE_SUBPROCESS", False)
        )
        outdict["multi_process"] = bool(getattr(module, "MULTI_PROCESS", False))
        outdict["filters"] = list(getattr(module, "FILTERS", []) or [])

        outdict["local_task"] = bool(
            getattr(module, "LOCAL_TASK", False) or False
        )

        return outdict

    except Exception:
        IMPORT_ERRORS[task_key] = traceback.format_exc()

        outdict = dict()
        outdict["task_cls"] = _failed_task_class(task_key, module_name)
        outdict["param_list"] = ["LOCAL_DATA_DIR", "INSTRUMENT", "TASK_CONFIG"]
        outdict["ap_list"] = []
        outdict["frequency"] = 24.0
        outdict["enabled"] = False
        outdict["task_type"] = task_type_fallback
        outdict["use_subprocess"] = False
        outdict["multi_process"] = False
        outdict["filters"] = []
        outdict["local_task"] = False
        return outdict


# =============================================================================
# Define task registry
# =============================================================================
TASK_LIST = dict()
P_LIST = dict()
AP_LIST = dict()
FREQ = dict()
ENABLED = dict()
TYPE = dict()
USE_SUBPROCESS = dict()
MULTI_PROCESS = dict()
LOCAL_TASK = dict()
FILTERS = dict()

# APERO_SYNC_ASSETS
_entry = _register_task(
    "APERO_SYNC_ASSETS",
    "apero_assets_sync",
    "AperoAssetsSyncTask",
    "GLOBAL",
)
TASK_LIST["APERO_SYNC_ASSETS"] = _entry["task_cls"]
P_LIST["APERO_SYNC_ASSETS"] = _entry["param_list"]
AP_LIST["APERO_SYNC_ASSETS"] = _entry["ap_list"]
FREQ["APERO_SYNC_ASSETS"] = _entry["frequency"]
ENABLED["APERO_SYNC_ASSETS"] = _entry["enabled"]
TYPE["APERO_SYNC_ASSETS"] = _entry["task_type"]
USE_SUBPROCESS["APERO_SYNC_ASSETS"] = _entry["use_subprocess"]
MULTI_PROCESS["APERO_SYNC_ASSETS"] = _entry["multi_process"]
LOCAL_TASK["APERO_SYNC_ASSETS"] = _entry["local_task"]
FILTERS["APERO_SYNC_ASSETS"] = _entry["filters"]

# ARI_LOCAL_DATA_BACKUP
_entry = _register_task(
    "ARI_LOCAL_DATA_BACKUP",
    "apero_backup",
    "AperoLocalDataBackupTask",
    "GLOBAL",
)
TASK_LIST["ARI_LOCAL_DATA_BACKUP"] = _entry["task_cls"]
P_LIST["ARI_LOCAL_DATA_BACKUP"] = _entry["param_list"]
AP_LIST["ARI_LOCAL_DATA_BACKUP"] = _entry["ap_list"]
FREQ["ARI_LOCAL_DATA_BACKUP"] = _entry["frequency"]
ENABLED["ARI_LOCAL_DATA_BACKUP"] = _entry["enabled"]
TYPE["ARI_LOCAL_DATA_BACKUP"] = _entry["task_type"]
USE_SUBPROCESS["ARI_LOCAL_DATA_BACKUP"] = _entry["use_subprocess"]
MULTI_PROCESS["ARI_LOCAL_DATA_BACKUP"] = _entry["multi_process"]
LOCAL_TASK["ARI_LOCAL_DATA_BACKUP"] = _entry["local_task"]
FILTERS["ARI_LOCAL_DATA_BACKUP"] = _entry["filters"]

# APERO_OBJECT_TABLE
_entry = _register_task(
    "APERO_OBJECT_TABLE",
    "apero_object_table",
    "AperoObjectTableTask",
    "INSTRUMENT",
)
TASK_LIST["APERO_OBJECT_TABLE"] = _entry["task_cls"]
P_LIST["APERO_OBJECT_TABLE"] = _entry["param_list"]
AP_LIST["APERO_OBJECT_TABLE"] = _entry["ap_list"]
FREQ["APERO_OBJECT_TABLE"] = _entry["frequency"]
ENABLED["APERO_OBJECT_TABLE"] = _entry["enabled"]
TYPE["APERO_OBJECT_TABLE"] = _entry["task_type"]
USE_SUBPROCESS["APERO_OBJECT_TABLE"] = _entry["use_subprocess"]
MULTI_PROCESS["APERO_OBJECT_TABLE"] = _entry["multi_process"]
LOCAL_TASK["APERO_OBJECT_TABLE"] = _entry["local_task"]
FILTERS["APERO_OBJECT_TABLE"] = _entry["filters"]

# APERO_OBS_TABLE
_entry = _register_task(
    "APERO_OBS_TABLE",
    "apero_observation_table",
    "AperoObservationTableTask",
    "INSTRUMENT",
)
TASK_LIST["APERO_OBS_TABLE"] = _entry["task_cls"]
P_LIST["APERO_OBS_TABLE"] = _entry["param_list"]
AP_LIST["APERO_OBS_TABLE"] = _entry["ap_list"]
FREQ["APERO_OBS_TABLE"] = _entry["frequency"]
ENABLED["APERO_OBS_TABLE"] = _entry["enabled"]
TYPE["APERO_OBS_TABLE"] = _entry["task_type"]
USE_SUBPROCESS["APERO_OBS_TABLE"] = _entry["use_subprocess"]
MULTI_PROCESS["APERO_OBS_TABLE"] = _entry["multi_process"]
LOCAL_TASK["APERO_OBS_TABLE"] = _entry["local_task"]
FILTERS["APERO_OBS_TABLE"] = _entry["filters"]

# APERO_OBJECT_QUERY
_entry = _register_task(
    "APERO_OBJECT_QUERY",
    "apero_object_query",
    "AperoObjectQueryTask",
    "INSTRUMENT",
)
TASK_LIST["APERO_OBJECT_QUERY"] = _entry["task_cls"]
P_LIST["APERO_OBJECT_QUERY"] = _entry["param_list"]
AP_LIST["APERO_OBJECT_QUERY"] = _entry["ap_list"]
FREQ["APERO_OBJECT_QUERY"] = _entry["frequency"]
ENABLED["APERO_OBJECT_QUERY"] = _entry["enabled"]
TYPE["APERO_OBJECT_QUERY"] = _entry["task_type"]
USE_SUBPROCESS["APERO_OBJECT_QUERY"] = _entry["use_subprocess"]
MULTI_PROCESS["APERO_OBJECT_QUERY"] = _entry["multi_process"]
LOCAL_TASK["APERO_OBJECT_QUERY"] = _entry["local_task"]
FILTERS["APERO_OBJECT_QUERY"] = _entry["filters"]

# APERO_QC_STATS
_entry = _register_task(
    "APERO_QC_STATS", "apero_qc_stats", "AperoQCStats", "INSTRUMENT"
)
TASK_LIST["APERO_QC_STATS"] = _entry["task_cls"]
P_LIST["APERO_QC_STATS"] = _entry["param_list"]
AP_LIST["APERO_QC_STATS"] = _entry["ap_list"]
FREQ["APERO_QC_STATS"] = _entry["frequency"]
ENABLED["APERO_QC_STATS"] = _entry["enabled"]
TYPE["APERO_QC_STATS"] = _entry["task_type"]
USE_SUBPROCESS["APERO_QC_STATS"] = _entry["use_subprocess"]
MULTI_PROCESS["APERO_QC_STATS"] = _entry["multi_process"]
LOCAL_TASK["APERO_QC_STATS"] = _entry["local_task"]
FILTERS["APERO_QC_STATS"] = _entry["filters"]

# APERO_CHECK_TASK
_entry = _register_task(
    "APERO_CHECK_TASK",
    "apero_check_task",
    "AperoCheckTask",
    "INSTRUMENT",
)
TASK_LIST["APERO_CHECK_TASK"] = _entry["task_cls"]
P_LIST["APERO_CHECK_TASK"] = _entry["param_list"]
AP_LIST["APERO_CHECK_TASK"] = _entry["ap_list"]
FREQ["APERO_CHECK_TASK"] = _entry["frequency"]
ENABLED["APERO_CHECK_TASK"] = _entry["enabled"]
TYPE["APERO_CHECK_TASK"] = _entry["task_type"]
USE_SUBPROCESS["APERO_CHECK_TASK"] = _entry["use_subprocess"]
MULTI_PROCESS["APERO_CHECK_TASK"] = _entry["multi_process"]
LOCAL_TASK["APERO_CHECK_TASK"] = _entry["local_task"]
FILTERS["APERO_CHECK_TASK"] = _entry["filters"]

# GENERATE_CHECK_DOCS
_entry = _register_task(
    "GENERATE_CHECK_DOCS",
    "apero_check_doc_tasks",
    "GenerateCheckDocsTask",
    "GLOBAL",
)
TASK_LIST["GENERATE_CHECK_DOCS"] = _entry["task_cls"]
P_LIST["GENERATE_CHECK_DOCS"] = _entry["param_list"]
AP_LIST["GENERATE_CHECK_DOCS"] = _entry["ap_list"]
FREQ["GENERATE_CHECK_DOCS"] = _entry["frequency"]
ENABLED["GENERATE_CHECK_DOCS"] = _entry["enabled"]
TYPE["GENERATE_CHECK_DOCS"] = _entry["task_type"]
USE_SUBPROCESS["GENERATE_CHECK_DOCS"] = _entry["use_subprocess"]
MULTI_PROCESS["GENERATE_CHECK_DOCS"] = _entry["multi_process"]
LOCAL_TASK["GENERATE_CHECK_DOCS"] = _entry["local_task"]
FILTERS["GENERATE_CHECK_DOCS"] = _entry["filters"]

# FAV_OBJECT_WATCHER
_entry = _register_task(
    "FAV_OBJECT_WATCHER",
    "fav_object_watcher",
    "FavObjectWatcherTask",
    "GLOBAL",
)
TASK_LIST["FAV_OBJECT_WATCHER"] = _entry["task_cls"]
P_LIST["FAV_OBJECT_WATCHER"] = _entry["param_list"]
AP_LIST["FAV_OBJECT_WATCHER"] = _entry["ap_list"]
FREQ["FAV_OBJECT_WATCHER"] = _entry["frequency"]
ENABLED["FAV_OBJECT_WATCHER"] = _entry["enabled"]
TYPE["FAV_OBJECT_WATCHER"] = _entry["task_type"]
USE_SUBPROCESS["FAV_OBJECT_WATCHER"] = _entry["use_subprocess"]
MULTI_PROCESS["FAV_OBJECT_WATCHER"] = _entry["multi_process"]
LOCAL_TASK["FAV_OBJECT_WATCHER"] = _entry["local_task"]
FILTERS["FAV_OBJECT_WATCHER"] = _entry["filters"]

# LEGACY_ASTROM_GSHEET
_entry = _register_task(
    'LEGACY_ASTROM_GSHEET',
    'legacy_astrom_gsheet',
    'LegacyAstromGSheetTask',
    'GLOBAL',
)
TASK_LIST['LEGACY_ASTROM_GSHEET'] = _entry['task_cls']
P_LIST['LEGACY_ASTROM_GSHEET'] = _entry['param_list']
AP_LIST['LEGACY_ASTROM_GSHEET'] = _entry['ap_list']
FREQ['LEGACY_ASTROM_GSHEET'] = _entry['frequency']
ENABLED['LEGACY_ASTROM_GSHEET'] = _entry['enabled']
TYPE['LEGACY_ASTROM_GSHEET'] = _entry['task_type']
USE_SUBPROCESS['LEGACY_ASTROM_GSHEET'] = _entry['use_subprocess']
MULTI_PROCESS['LEGACY_ASTROM_GSHEET'] = _entry['multi_process']
LOCAL_TASK['LEGACY_ASTROM_GSHEET'] = _entry['local_task']
FILTERS['LEGACY_ASTROM_GSHEET'] = _entry['filters']

# LEGACY_REJECT_GSHEET
_entry = _register_task(
    'LEGACY_REJECT_GSHEET',
    'lecacy_reject_gsheet',
    'LegacyRejectGSheetTask',
    'GLOBAL',
)
TASK_LIST['LEGACY_REJECT_GSHEET'] = _entry['task_cls']
P_LIST['LEGACY_REJECT_GSHEET'] = _entry['param_list']
AP_LIST['LEGACY_REJECT_GSHEET'] = _entry['ap_list']
FREQ['LEGACY_REJECT_GSHEET'] = _entry['frequency']
ENABLED['LEGACY_REJECT_GSHEET'] = _entry['enabled']
TYPE['LEGACY_REJECT_GSHEET'] = _entry['task_type']
USE_SUBPROCESS['LEGACY_REJECT_GSHEET'] = _entry['use_subprocess']
MULTI_PROCESS['LEGACY_REJECT_GSHEET'] = _entry['multi_process']
LOCAL_TASK['LEGACY_REJECT_GSHEET'] = _entry['local_task']
FILTERS['LEGACY_REJECT_GSHEET'] = _entry['filters']

# LEGACY_CHECK_GSHEET
_entry = _register_task(
    'LEGACY_CHECK_GSHEET',
    'legacy_check_gsheet',
    'LegacyCheckGSheetTask',
    'GLOBAL',
)
TASK_LIST['LEGACY_CHECK_GSHEET'] = _entry['task_cls']
P_LIST['LEGACY_CHECK_GSHEET'] = _entry['param_list']
AP_LIST['LEGACY_CHECK_GSHEET'] = _entry['ap_list']
FREQ['LEGACY_CHECK_GSHEET'] = _entry['frequency']
ENABLED['LEGACY_CHECK_GSHEET'] = _entry['enabled']
TYPE['LEGACY_CHECK_GSHEET'] = _entry['task_type']
USE_SUBPROCESS['LEGACY_CHECK_GSHEET'] = _entry['use_subprocess']
MULTI_PROCESS['LEGACY_CHECK_GSHEET'] = _entry['multi_process']
LOCAL_TASK['LEGACY_CHECK_GSHEET'] = _entry['local_task']
FILTERS['LEGACY_CHECK_GSHEET'] = _entry['filters']

# LEGACY_KNOWN_ERRORS_GSHEET
_entry = _register_task(
    'LEGACY_KNOWN_ERRORS_GSHEET',
    'legacy_known_errors_gsheet',
    'LegacyKnownErrorsGSheetTask',
    'GLOBAL',
)
TASK_LIST['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['task_cls']
P_LIST['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['param_list']
AP_LIST['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['ap_list']
FREQ['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['frequency']
ENABLED['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['enabled']
TYPE['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['task_type']
USE_SUBPROCESS['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['use_subprocess']
MULTI_PROCESS['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['multi_process']
LOCAL_TASK['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['local_task']
FILTERS['LEGACY_KNOWN_ERRORS_GSHEET'] = _entry['filters']

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
