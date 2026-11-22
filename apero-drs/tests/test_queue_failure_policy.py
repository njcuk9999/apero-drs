#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for processing failure policy in the queue."""
from types import SimpleNamespace
from typing import Any
import os
import subprocess

import pytest

from apero import dev
from apero.tools.module.processing import drs_processing
from apero.tools.module.processing import drs_queue as queue


@pytest.mark.parametrize('reference,stop,blocked', [
    (False, False, False), (False, True, True), (True, False, True)])
def test_failed_task_blocks_claims(
    tmp_path: Any, monkeypatch: Any, reference: bool, stop: bool,
    blocked: bool,
) -> None:
    """Protected failures block claims until retried.

    :param tmp_path: Temporary queue directory.
    :param monkeypatch: Runtime override fixture.
    :param reference: Whether the failed task is a reference recipe.
    :param stop: Persisted stop-at-exception flag.
    :param blocked: Expected queue blocking decision.
    :return: None.
    """
    assert dev is not None
    monkeypatch.setattr(queue, 'get_queue_path', lambda params: str(tmp_path))
    group = 'APERO-QUEUE-GROUP-00000000001-0001-DARK'
    next_group = 'APERO-QUEUE-GROUP-00000000001-0002-EXT'
    run = 'APERO-QUEUE-RUN-00000001.yaml'
    failed = tmp_path / 'failed' / group
    pending = tmp_path / 'pending' / next_group
    failed.mkdir(parents=True)
    pending.mkdir(parents=True)
    metadata = dict(state='failed', is_reference=reference,
                    STOP_AT_EXCEPTION=stop, runstring='recipe')
    queue.base.write_yaml(metadata, str(failed / run))
    queue.base.write_yaml(dict(state='pending'), str(pending / run))
    params = queue.ParamDict()
    selected, pending_runs, _ = queue.get_next_group(params)
    assert selected == (group if blocked else next_group)
    assert pending_runs == ([] if blocked else [run])
    queue.move_run_file(str(tmp_path), group, run, 'failed', 'pending')
    assert queue._blocking_failure(params) is None
    assert queue.get_next_group(params)[1] == [run]


def test_generate_persists_stop_flag(tmp_path: Any, monkeypatch: Any) -> None:
    """Generation preserves the run-file failure policy.

    :param tmp_path: Temporary queue directory.
    :param monkeypatch: Runtime override fixture.
    :return: None.
    """
    monkeypatch.setattr(queue, 'get_queue_path', lambda params: str(tmp_path))
    monkeypatch.setattr(queue, 'WLOG', lambda *values, **options: None)
    monkeypatch.setattr(queue, '_add_db_push_group',
                        lambda *values, **options: None)
    run = SimpleNamespace(priority=1)
    monkeypatch.setattr(drs_processing, 'group_tasks2',
                        lambda runs: ({1: [run]}, {1: 'PP'}))
    monkeypatch.setattr(queue, '_run_item_to_dict',
                        lambda *values: dict(is_reference=False))
    params = queue.ParamDict()
    params['STOP_AT_EXCEPTION'] = True
    queue.add_run_list_to_queue(params, [run])
    entries = queue.list_queue_entries(params, states=['pending'])
    entry = next(item for item in entries if item['group'].endswith('-PP'))
    stored = queue.base.load_yaml(entry['path'])
    assert stored['STOP_AT_EXCEPTION'] is True


def test_linear_failure_releases_unstarted_tasks(
    monkeypatch: Any,
) -> None:
    """A protected linear failure stops and releases unstarted tasks.

    :param monkeypatch: Runtime override fixture.
    :return: None.
    """
    tasks = [dict(group='group', run_file=name, run_path=name,
                  shortname='DARK', runstring='recipe',
                  STOP_AT_EXCEPTION='True') for name in ['first', 'second']]
    executed, released = [], []
    monkeypatch.setattr(queue.os.path, 'exists', lambda path: True)
    monkeypatch.setattr(queue, 'WLOG', lambda *values, **options: None)
    monkeypatch.setattr(queue, '_run_task', lambda task: (
        executed.append(task['run_file']) or task['run_file'], False, ''))
    monkeypatch.setattr(queue, 'release_running',
                        lambda params, qids: released.extend(qids))
    result = queue._execute_tasks(queue.ParamDict(), tasks, 2, 'linear')
    assert result == dict(first=False)
    assert executed == ['first']
    assert released == ['group/second']


@pytest.mark.parametrize('output,code,expected', [
    ('done', 0, 0),
    ('W: Recipe x has NOT been successfully completed', 0, 1),
    ('crash', 3, 3),
])
def test_script_task_status_uses_fail_signature(
    tmp_path: Any, output: str, code: int, expected: int,
) -> None:
    """Batch/chain scripts fail tasks whose wrapped recipe failed.

    :param tmp_path: Temporary log directory.
    :param output: Task console output.
    :param code: Task exit code.
    :param expected: Expected task status.
    :return: None.
    """
    log_path = tmp_path / 'logs' / 'task.log'
    command = 'echo {0}; exit {1}'.format(queue.shlex.quote(output), code)
    lines = queue._shell_logged_command(
        'bash -c {0}'.format(queue.shlex.quote(command)), str(log_path))
    lines.append('exit $task_status')
    result = subprocess.run(['bash', '-c', '\n'.join(lines)],
                            capture_output=True)
    assert result.returncode == expected
    assert output in log_path.read_text()


def test_ari_task_runs_after_regular_processing(monkeypatch: Any) -> None:
    """The ARI task runs after the complete regular run list."""
    runs = [
        SimpleNamespace(shortname='EXT', priority=1, runstring='extract'),
        SimpleNamespace(shortname='ARITASK', priority=2,
                        runstring='apero_ri_tasks'),
    ]
    executed = []

    def run_parallel(params: Any, shortname: str, runlist: list,
                     **kwargs: Any) -> dict:
        executed.extend(run.shortname for run in runlist)
        return {run.priority: dict(ERROR=[], TIMING=0.0) for run in runlist}

    monkeypatch.setattr(drs_processing.drs_utils, 'get_cores', lambda p: 2)
    monkeypatch.setattr(drs_processing, '_multi_process_process', run_parallel)
    monkeypatch.setattr(drs_processing, 'WLOG', lambda *args, **kwargs: None)
    monkeypatch.setattr(drs_processing.drs_lock, 'reset_lock_dir',
                        lambda params: None)
    params = drs_processing.ParamDict()
    params['STOP_AT_EXCEPTION'] = False
    params['TEST_RUN'] = False
    params['TOOLS.REPROCESS.MP_TYPE'] = 'process'

    outlist, has_errors, _duration = drs_processing.process_run_list(
        params, 'PROCESSING', runs)

    assert executed == ['EXT', 'ARITASK']
    assert list(outlist) == [1, 2]
    assert not has_errors
    groups, names = drs_processing.group_tasks2(runs)
    assert list(names.values()) == ['EXT', 'ARITASK']
    ari_group = next(key for key, name in names.items()
                     if name == 'ARITASK')
    assert [run.shortname for run in groups[ari_group]] == ['ARITASK']


def test_chain_chunk_stops_after_reference_failure(
    tmp_path: Any, monkeypatch: Any,
) -> None:
    """Generated chunks stop and release unstarted work on ref failures.

    :param tmp_path: Temporary scripts and command output.
    :param monkeypatch: Runtime override fixture.
    :return: None.
    """
    trace = tmp_path / 'trace'
    stub = tmp_path / 'apero_queue.py'
    stub.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$TRACE"\n')
    stub.chmod(0o755)
    monkeypatch.setenv('TRACE', str(trace))
    monkeypatch.setenv('PATH', str(tmp_path) + os.pathsep + os.environ['PATH'])
    monkeypatch.setattr(queue, '_monitored_command',
                        lambda command, *values: command)
    group = 'APERO-QUEUE-GROUP-00000000001-0001-DARK'
    tasks = []
    marker = tmp_path / 'must-not-run'
    for index, command in enumerate(['false', 'touch ' + str(marker)]):
        run = queue.QUEUE_RUN_FORMAT.format(index)
        tasks.append(dict(qpath=str(tmp_path), qid=group + '/' + run,
                          shortname='DARK', command=command,
                          is_reference=True))
    script = tmp_path / 'chunk.sh'
    queue._write_chain_chunk_script(str(script), tasks, False)
    result = subprocess.run(['bash', str(script)], capture_output=True)
    assert result.returncode == 1
    assert not marker.exists()
    assert '--qresult=failed' in trace.read_text()
    assert '--qresult=pending' in trace.read_text()