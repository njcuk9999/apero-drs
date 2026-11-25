#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only reduction-host diagnostics for ARI's linked queue tunnels."""

import os
import re
from pathlib import Path
from typing import Any

from aperocore.base import base
from aperocore.constants.param_functions import ParamDict
from aperocore.core import diagnostics as common
from apero.base import base as apero_base
from apero.core import drs_database
from apero.tools.module.processing import drs_queue
from apero.tools.module.processing import drs_queue_procs

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.processing.drs_queue_diagnostics'
__version__ = apero_base.__version__
__date__ = apero_base.__date__
__authors__ = apero_base.__authors__

# =============================================================================
# Define functions
# =============================================================================
def loopback_allowed(address: str) -> bool:
    """Restrict richer queue diagnostics to local or SSH-forwarded clients.

    :param address: Actual socket peer address, not a forwarded header.
    :return: Whether the request originated from loopback.
    """
    import ipaddress

    try:
        return ipaddress.ip_address(address).is_loopback
    except ValueError:
        return False


def _logs(params: ParamDict) -> dict[str, Any]:
    """Read recent LogDatabase timings without loading or creating tables.

    :param params: Queue host's active APERO parameters.
    :return: Recent recipe log records and their resource semantics.
    """
    manager = drs_database.LogDatabase(params, 'DIAGNOSTICS')
    if not re.fullmatch(r'[A-Za-z0-9_]+', str(manager.dbtable)):
        raise ValueError('invalid_log_table')
    columns = ('PID, RECIPE, SHORTNAME, GROUPNAME, LEVEL, SUBLEVEL, '
               'START_TIME, END_TIME, ENDED, PASSED_ALL_QC, ERRORMSGS, '
               'RAM_USAGE_START, RAM_USAGE_END, CPU_USAGE_START, CPU_USAGE_END')
    query = (f'SELECT {columns} FROM `{manager.dbtable}` '
             'WHERE USED=1 ORDER BY UNIXTIME DESC LIMIT 100')
    rows = common.database_rows(manager.dburl, query, dict())
    return dict(rows=rows, limit=100,
                resource_semantics='host_snapshots_not_process_peaks')


def _processes(other: Path, queue: Path) -> dict:
    """Inspect bounded registry artifacts and check generated monitor hooks.

    :param other: Configured PATH.OTHER.
    :param queue: Configured queue root.
    :return: Registry rows, script monitor evidence, and redacted log tails.
    """
    root = other / drs_queue_procs.PROC_DIR_NAME
    entries = common.inventory(root)
    records = []
    artifacts = []
    logs = []
    for entry in entries['entries']:
        path = Path(entry['path'])
        if path.suffix != '.json':
            continue
        record = common.read_json(path, root).get('data')
        if not isinstance(record, dict):
            continue
        records.append(dict(record, qids=record.get('qids', [])[-100:]))
        for artifact in record.get('artifact_paths', [])[:3]:
            selected = Path(artifact)
            if not selected.resolve().is_relative_to(queue.resolve()):
                continue
            if len(artifacts) >= 20:
                break
            payload = common.log_tail(selected, queue)
            content = payload.pop('text', '')
            payload['monitor_hook_present'] = 'drs_queue_stats.py' in content
            payload['content'] = content
            artifacts.append(payload)
        for name in record.get('log_paths', [])[:1]:
            selected = Path(name)
            approved = next((approved for approved in (queue, other)
                             if selected.resolve().is_relative_to(
                                 approved.resolve())), None)
            if approved is not None and len(logs) < 3:
                logs.append(common.log_tail(selected, approved))
    return dict(inventory=entries, records=records[:100],
                artifacts=artifacts, log_tails=logs)


def collect(params: ParamDict) -> dict[str, Any]:
    """Describe the queue host, its active profile, stores, and recipe logs.

    :param params: Current queue GUI's APERO profile parameters.
    :return: Bounded redacted JSON report. No queue actions are dispatched.
    """
    from apero.tools.module.processing import drs_queue_gui

    queue = Path(drs_queue.get_queue_path(params))
    other = Path(params['PATH.OTHER'])
    userenv = params['DRS.USERENV']
    uconfig = os.environ.get(userenv, '')
    configuration = dict(paths={key: str(value) for key, value in params.items()
                                if key.startswith('PATH.')},
                         database=base.DPARAMS)
    report = dict(success=True, schema_version=1, runtime=common.runtime(),
                  instrument=params['OBS.INSTRUMENT'],
                  profile_id=Path(uconfig).name, drs_uconfig=uconfig,
                  queue_path=str(queue), configuration=configuration,
                  sections=dict())
    checks = dict(queue=lambda: common.inventory(queue),
                  stats_files=lambda: common.inventory(
                      Path(drs_queue.get_stats_dir(str(queue)))),
                  processes=lambda: _processes(other, queue),
                  log_database=lambda: _logs(params),
                  settings=lambda: drs_queue.load_queue_settings(params),
                  runtime_info=drs_queue_gui.get_runtime_info)
    for name, check in checks.items():
        try:
            report['sections'][name] = check()
        except Exception as error:
            report['sections'][name] = dict(error=str(error))
    try:
        status = drs_queue_gui.get_status_data(params)
        entries = sorted(status['entries'], key=lambda row: (
            row['state'] not in ('failed', 'running'), row['qid']))
        truncated = len(entries) > 100
        report['sections']['status'] = dict(status, entries=entries[:100],
                                            entries_truncated=truncated)
    except Exception as error:
        report['sections']['status'] = dict(error=str(error))
    try:
        stats = dict(drs_queue_gui.get_stats_data(params))
        stats['tasks'] = {key: value[-100:]
                          for key, value in stats['tasks'].items()}
        report['sections']['stats'] = stats
    except Exception as error:
        report['sections']['stats'] = dict(error=str(error))
    report['limits'] = dict(rows=100, artifacts=20, log_tails=3,
                            file_bytes=common.FILE_LIMIT)
    return common.redact(report, common.secret_values(configuration))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================