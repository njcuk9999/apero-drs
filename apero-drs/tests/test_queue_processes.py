"""Tests for the APERO queue process registry (Processes tab)."""
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import pytest

from apero.tools.module.processing import drs_queue
from apero.tools.module.processing import drs_queue_procs as procs
from apero.tools.module.processing import drs_queue_stats as stats
from apero.tools.module.processing import drs_queue_gui as gui
from apero.tools.module.setup import drs_reset
from apero import dev


@pytest.mark.parametrize('blocked', [False, True])
@pytest.mark.parametrize('selected', [
    'later', 'earlier', 'missing', '../outside.yaml',
])
def test_selected_pending_task_runs_once(
    tmp_path: Path, monkeypatch: Any, selected: str, blocked: bool,
) -> None:
    """Run only the selected pending task through the registered runner.

    :param tmp_path: Temporary profile.
    :param monkeypatch: Runtime overrides.
    :param selected: Requested pending queue ID.
    :param blocked: Whether a protected failure must prevent execution.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    params['PATH.OTHER'] = str(tmp_path / 'other')
    queue_path = tmp_path / 'queue'
    monkeypatch.setattr(drs_queue, 'get_queue_path',
                        lambda params: str(queue_path))
    monkeypatch.setattr(drs_queue, 'WLOG', lambda *args, **kwargs: None)
    drs_queue.setup_queue_directories(params)
    run = drs_queue.QUEUE_RUN_FORMAT.format(0)
    pending = ['APERO-QUEUE-GROUP-{0}/{1}'.format(group, run)
               for group in ['earlier', 'later']]
    if selected in ['earlier', 'later', 'missing']:
        selected = 'APERO-QUEUE-GROUP-{0}/{1}'.format(selected, run)
    for qid in pending:
        destination = queue_path / 'pending' / qid
        destination.parent.mkdir(parents=True, exist_ok=True)
        drs_queue.base.write_yaml(
            dict(state='pending', runstring='recipe'), str(destination))
    if blocked:
        failed = queue_path / 'failed' / 'APERO-QUEUE-GROUP-blocked'
        failed.mkdir(parents=True)
        drs_queue.base.write_yaml(
            dict(state='failed', is_reference=True, runstring='recipe'),
            str(failed / run))
    executed = []

    def execute(params: Any, tasks: list, cores: int,
                mpmode: str, **kwargs: Any) -> dict:
        """Record the claimed work without launching real recipes."""
        assert cores == 1 and mpmode == 'linear'
        executed.extend(task['group'] + '/' + task['run_file']
                        for task in tasks)
        return {task['run_file']: True for task in tasks}

    monkeypatch.setattr(drs_queue, '_execute_tasks', execute)
    result = drs_queue.queue_run(
        params, cores=1, mpmode='linear', ntasks=1, qid=selected)
    expected = [selected] if selected in pending and not blocked else []
    assert executed == expected
    assert result['n_run'] == len(executed)
    for qid in pending:
        state = 'complete' if qid in executed else 'pending'
        assert (queue_path / state / qid).exists()
    if executed:
        again = drs_queue.queue_run(
            params, cores=1, mpmode='linear', ntasks=1, qid=selected)
        assert again['n_run'] == 0
        assert executed == [selected]


def test_gui_selected_run_forces_single_process(monkeypatch: Any) -> None:
    """Selected-row requests enforce single-process settings on the server.

    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    state = gui.GuiState()
    calls = []

    def run(params: Any, **kwargs: Any) -> dict:
        """Capture the runner inputs without executing any queue tasks."""
        calls.append(kwargs)
        return dict(message='finished')

    monkeypatch.setattr(drs_queue, 'queue_run', run)
    result = gui.action_run(params, state, cores=8, ntasks='all',
                            mpmode='process', qid='group/task.yaml')
    assert result['started']
    assert state.worker is not None
    state.worker.join(timeout=5)
    assert len(calls) == 1
    assert calls[0]['cores'] == 1
    assert calls[0]['ntasks'] == '1'
    assert calls[0]['mpmode'] == 'linear'
    assert calls[0]['qid'] == 'group/task.yaml'
    assert calls[0]['owner'] == 'gui'


def test_process_gui_preserves_retained_tasks(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """Removing a process cleans its console, not retained queue data.

    :param tmp_path: Temporary profile.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    params['PATH.OTHER'] = str(tmp_path / 'other')
    queue_path = tmp_path / 'queue'
    monkeypatch.setattr(drs_queue, 'get_queue_path',
                        lambda params: str(queue_path))
    drs_queue.setup_queue_directories(params)
    group = 'APERO-QUEUE-GROUP-test'
    run = drs_queue.QUEUE_RUN_FORMAT.format(0)
    qid = group + '/' + run
    directory = queue_path / 'complete' / group
    directory.mkdir()
    (directory / run).write_text('state: complete\n')
    task_log = Path(drs_queue.get_task_log_path(str(queue_path), group, run))
    task_log.parent.mkdir(parents=True)
    task_log.write_text('task output')
    stats_dir = drs_queue.get_stats_dir(str(queue_path))
    stats.TaskMonitor(stats_dir, qid, 'PP')._write('tasks-', dict(qid=qid))
    console = tmp_path / 'other' / gui.GUI_JOB_DIR / 'run.log'
    console.parent.mkdir(parents=True)
    console.write_text('console')
    proc_dir = drs_queue.get_proc_dir(params)
    proc_id = procs.register(proc_dir, 'run', 'run', qids=[qid],
                             log_paths=[str(console)])
    assert proc_id is not None
    procs.finish(proc_dir, proc_id, 0)
    result = gui.action_process(params, gui.GuiState(), 'remove', [proc_id])
    assert result['success']
    assert not console.exists()
    assert task_log.exists()
    reader = stats.StatsReader()
    reader.update(stats_dir)
    assert [row['qid'] for row in reader.tasks] == [qid]
    (directory / run).unlink()
    orphan = procs.register(proc_dir, 'run', 'orphan', qids=[qid])
    procs.finish(proc_dir, orphan, 0)
    result = gui.action_process(params, gui.GuiState(), 'clear_finished')
    assert result['success']
    assert not task_log.exists()
    reader.update(stats_dir)
    assert reader.tasks == []


def test_full_reset_preserves_active_queue(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """Full queue reset refuses to hide live work.

    :param tmp_path: Temporary profile.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    params['PATH.OTHER'] = str(tmp_path / 'other')
    monkeypatch.setattr(drs_queue, 'get_queue_path',
                        lambda params: str(tmp_path / 'queue'))
    monkeypatch.setattr(drs_reset, 'WLOG', lambda *args, **kwargs: None)
    marker = tmp_path / 'queue' / 'output' / 'live.log'
    marker.parent.mkdir(parents=True)
    marker.write_text('live output')
    proc_dir = drs_queue.get_proc_dir(params)
    procs.register(proc_dir, 'run', 'live', pid=os.getpid())
    drs_reset.reset_queue(params, log=False)
    assert marker.read_text() == 'live output'


def test_full_idle_reset_preserves_templates(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """An idle full reset clears outputs and chains, not saved settings.

    :param tmp_path: Temporary profile.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    params['PATH.OTHER'] = str(tmp_path / 'other')
    queue_path = tmp_path / 'queue'
    monkeypatch.setattr(drs_queue, 'get_queue_path',
                        lambda params: str(queue_path))
    drs_queue.setup_queue_directories(params)
    template = queue_path / drs_queue.QUEUE_BATCH_TEMPLATE_DIR / 'mine.yaml'
    template.parent.mkdir(exist_ok=True)
    template.write_text('settings')
    legacy = queue_path / drs_queue.QUEUE_BATCH_TEMPLATE
    legacy.write_text('legacy settings')
    output = queue_path / 'output' / 'stats' / 'tasks-old.jsonl'
    output.parent.mkdir(parents=True)
    output.write_text('old stats')
    chain = Path(drs_queue.get_chain_root(params)) / 'APERO-CHAIN-old'
    chain.mkdir(parents=True)
    (chain / 'submit_chain.sh').write_text('old commands')
    drs_reset.reset_queue(params, log=False)
    assert template.read_text() == 'settings'
    assert legacy.read_text() == 'legacy settings'
    assert not output.exists() and not chain.exists()
    assert not (queue_path / drs_queue.QUEUE_LOCK_FILE).exists()
    assert all((queue_path / state).is_dir()
               for state in drs_queue.QUEUE_SUB_DIRS)


@pytest.mark.parametrize('operation', ['remove', 'clear_finished', 'clear_all'])
def test_gui_removal_preserves_shared_qids_and_live_records(
    tmp_path: Path, monkeypatch: Any, operation: str,
) -> None:
    """All process-list removal actions protect live work and shared tasks.

    :param tmp_path: Temporary profile.
    :param monkeypatch: Runtime overrides.
    :param operation: Process-list removal action.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    params['PATH.OTHER'] = str(tmp_path / 'other')
    queue_path = tmp_path / 'queue'
    monkeypatch.setattr(drs_queue, 'get_queue_path',
                        lambda params: str(queue_path))
    group = 'APERO-QUEUE-GROUP-test'
    run = drs_queue.QUEUE_RUN_FORMAT.format(0)
    qid = group + '/' + run
    log = Path(drs_queue.get_task_log_path(str(queue_path), group, run))
    log.parent.mkdir(parents=True)
    log.write_text('shared task log')
    proc_dir = drs_queue.get_proc_dir(params)
    removed = procs.register(proc_dir, 'run', 'finished', qids=[qid])
    active = procs.register(proc_dir, 'run', 'active', pid=os.getpid(),
                            qids=[qid])
    assert removed is not None and active is not None
    procs.finish(proc_dir, removed, 0)
    state = gui.GuiState()
    result = gui.action_process(params, state, operation, [removed, active])
    assert result['success'] == (operation == 'clear_finished')
    assert procs.load(proc_dir, removed) is None
    assert procs.load(proc_dir, active) is not None
    assert log.read_text() == 'shared task log'
    assert state.data_version == 1


def test_reset_scopes_task_artifacts(tmp_path: Path, monkeypatch: Any) -> None:
    """Reset removes only selected inaccessible tasks, never live work.

    :param tmp_path: Temporary queue profile.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    params['PATH.OTHER'] = str(tmp_path / 'other')
    queue_path = tmp_path / 'queue'
    monkeypatch.setattr(drs_queue, 'get_queue_path',
                        lambda params: str(queue_path))
    monkeypatch.setattr(drs_queue, 'WLOG', lambda *args, **kwargs: None)
    drs_queue.setup_queue_directories(params)
    group = 'APERO-QUEUE-GROUP-test'
    qids = []
    for index, state in enumerate(['complete', 'pending', 'running']):
        run = drs_queue.QUEUE_RUN_FORMAT.format(index)
        directory = queue_path / state / group
        directory.mkdir()
        (directory / run).write_text('state: ' + state + '\n')
        qid = group + '/' + run
        qids.append(qid)
        log = Path(drs_queue.get_task_log_path(str(queue_path), group, run))
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(state)
        monitor = stats.TaskMonitor(drs_queue.get_stats_dir(str(queue_path)),
                                    qid, 'PP')
        monitor._write(stats.TASK_PREFIX, dict(qid=qid))
    template = queue_path / 'batch_templates' / 'mine.yaml'
    template.parent.mkdir(exist_ok=True)
    template.write_text('settings')
    assert drs_queue.reset_queue(params, ['complete'], dry_run=True) == 1
    assert len(drs_queue.list_queue_entries(params)) == 3
    assert drs_queue.reset_queue(params, ['complete']) == 1
    assert drs_queue.reset_queue(params, ['pending', 'running']) == 1
    assert template.read_text() == 'settings'
    entries = drs_queue.list_queue_entries(params)
    assert [entry['state'] for entry in entries] == ['running']
    reader = stats.StatsReader()
    reader.update(drs_queue.get_stats_dir(str(queue_path)))
    assert [row['qid'] for row in reader.tasks] == [qids[2]]
    logs = list((queue_path / drs_queue.QUEUE_TASK_LOGS_DIR).rglob('*.log'))
    assert len(logs) == 1 and logs[0].read_text() == 'running'


def test_remove_owned_unshared_logs(tmp_path: Path) -> None:
    """Remove owned logs, preserving shared files and symlink escapes.

    :param tmp_path: Temporary registry and artifacts.
    :return: None.
    """
    proc_dir = procs.get_proc_dir(str(tmp_path))
    owned = tmp_path / 'queue_gui_jobs'
    owned.mkdir()
    unique = owned / 'unique.log'
    shared = owned / 'shared.log'
    outside = tmp_path / 'outside.log'
    for path in [unique, shared, outside]:
        path.write_text('keep or remove')
    escape = owned / 'escape.log'
    escape.symlink_to(outside)
    paths = [str(path) for path in [unique, shared, outside, escape]]
    first = procs.register(proc_dir, 'generate', 'first', log_paths=paths)
    second = procs.register(proc_dir, 'generate', 'second',
                            log_paths=[str(shared)])
    assert first is not None and second is not None
    procs.finish(proc_dir, first, 0)
    procs.finish(proc_dir, second, 0)
    assert procs.remove(proc_dir, [first]) == 1
    assert not unique.exists()
    assert shared.exists() and outside.exists() and escape.is_symlink()
    assert procs.remove(proc_dir, [second]) == 1
    assert not shared.exists()


def test_remove_preserves_live_and_unknown(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """Removal never hides local, remote, or unverifiable Slurm work.

    :param tmp_path: Temporary registry.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    proc_dir = procs.get_proc_dir(str(tmp_path))
    local = procs.register(proc_dir, 'run', 'local', pid=os.getpid())
    remote = procs.register(proc_dir, 'run', 'remote', pid=1)
    assert local is not None and remote is not None
    procs.update(proc_dir, remote, host='other-host')
    batch = procs.register(proc_dir, 'batch', 'batch', slurm_jobs=['123'])
    assert batch is not None
    monkeypatch.setattr(procs, 'slurm_states', lambda jobs: None)
    assert procs.remove(proc_dir, [local, remote, batch]) == 0
    assert len(procs.load_all(proc_dir)) == 3


def test_remove_slurm_globs_are_bounded(tmp_path: Path) -> None:
    """Globs delete owned unshared files, not unrelated paths or trees.

    :param tmp_path: Temporary artifacts and process records.
    :return: None.
    """
    proc_dir = procs.get_proc_dir(str(tmp_path))
    root = tmp_path / 'queue' / 'output' / 'logs'
    root.mkdir(parents=True)
    owned = root / '123_job.out'
    shared = root / '123_shared.out'
    outside = tmp_path / '123_outside.out'
    for path in [owned, shared, outside]:
        path.write_text('output')
    (root / '123_directory.out').mkdir()
    escaped = root / 'escaped'
    escaped.symlink_to(tmp_path, target_is_directory=True)
    patterns = [str(root / '123_*.out'), str(tmp_path / '123_*.out'),
                str(escaped / '123_*.out')]
    first = procs.register(proc_dir, 'batch', 'first', log_globs=patterns)
    second = procs.register(proc_dir, 'batch', 'second',
                            log_globs=[str(root / '*shared.out')])
    assert first is not None and second is not None
    procs.finish(proc_dir, first, 0)
    procs.finish(proc_dir, second, 0)
    assert procs.remove(proc_dir, [first], [str(root)]) == 1
    assert not owned.exists()
    assert shared.exists() and outside.exists()
    assert (root / '123_directory.out').is_dir()
    assert procs.remove(proc_dir, [second], [str(root)]) == 1
    assert not shared.exists()


def test_generated_scripts_preserved_until_inaccessible(tmp_path: Path) -> None:
    """Generated scripts remain while queue IDs or process references exist.

    :param tmp_path: Temporary artifact and registry directories.
    :return: None.
    """
    proc_dir = procs.get_proc_dir(str(tmp_path))
    root = tmp_path / 'queue' / 'output' / 'scripts'
    root.mkdir(parents=True)
    script = root / 'owned.sbatch'
    script.write_text('commands')
    first = procs.register(proc_dir, 'batch', 'first', qids=['G/R1'],
                            artifact_paths=[str(script)])
    assert first is not None
    procs.finish(proc_dir, first, 0)
    assert procs.remove(proc_dir, [first], [str(root)], ['G/R1']) == 1
    assert script.exists()
    second = procs.register(proc_dir, 'batch', 'second', qids=['G/R1'],
                             artifact_paths=[str(script)])
    assert second is not None
    procs.finish(proc_dir, second, 0)
    assert procs.remove(proc_dir, [second], [str(root)], []) == 1
    assert not script.exists()


def test_register_update_finish_and_remove(tmp_path):
    proc_dir = procs.get_proc_dir(str(tmp_path))
    proc_id = procs.register(proc_dir, 'run', 'apero_queue.py run',
                             pid=999999999, qids=['G/R1'])
    record = procs.load(proc_dir, proc_id)
    assert record['qids'] == ['G/R1']
    assert procs.proc_status(record, None) == 'lost'
    procs.update(proc_dir, proc_id, qids=['G/R2'])
    procs.finish(proc_dir, proc_id, 0, stopped=True)
    # a later finish (e.g. the process exiting) keeps the stopped flag
    procs.finish(proc_dir, proc_id, 0)
    record = procs.load(proc_dir, proc_id)
    assert record['qids'] == ['G/R2']
    assert procs.proc_status(record, None) == 'stopped'
    assert [rec['id'] for rec in procs.load_all(proc_dir)] == [proc_id]
    assert procs.load(proc_dir, '../etc/passwd') is None
    assert procs.remove(proc_dir, [proc_id, 'bad']) == 1
    assert procs.load_all(proc_dir) == []


def test_slurm_parsing_and_status(tmp_path):
    text = ('Submitting APERO chain: APERO-CHAIN-12\n'
            'Submitted batch job 101\n'
            'Submitted APERO-QUEUE-GROUP-1-0001-PP: 102;cluster\n'
            '103\nChain submission complete\n')
    assert procs.parse_sbatch_ids(text) == ['101', '102', '103']
    record = dict(slurm_jobs=['101', '102'])
    assert procs.proc_status(record, None) == 'unknown'
    assert procs.proc_status(record, dict()) == 'finished'
    assert procs.proc_status(record, {'101': 'PENDING'}) == 'pending'
    assert procs.proc_status(record, {'102': 'RUNNING'}) == 'running'
    (tmp_path / '101_job.out').write_text('x')
    record['log_globs'] = [str(tmp_path / '101_*.out')]
    assert procs.log_files(record) == [str(tmp_path / '101_job.out')]


def test_slurm_job_details(monkeypatch: Any) -> None:
    """Live scheduler details should be parsed for the Processes view."""
    procs._SLURM_DETAILS_CACHE.update(time=0.0, value=None)
    output = (
        '123_4|apero_pp|RUNNING|def|None|00:02:03|02:00:00|01:57:57|'
        '1|8|16G|2026-11-19T10:00:00|2026-11-19T10:01:00|node1|'
        'afterok:122\n'
    )

    class Result:
        """Stand-in for one successful squeue call."""

        returncode = 0
        stdout = output
        stderr = ''

    monkeypatch.setattr(procs.shutil, 'which', lambda name: '/usr/bin/squeue')
    monkeypatch.setattr(procs.subprocess, 'run',
                        lambda *args, **kwargs: Result())
    monkeypatch.setattr(procs.getpass, 'getuser', lambda: 'apero')
    result = procs.slurm_job_details()
    assert result['available']
    assert result['user'] == 'apero'
    assert result['jobs'][0]['job_id'] == '123_4'
    assert result['jobs'][0]['base_job_id'] == '123'
    assert result['jobs'][0]['state'] == 'RUNNING'
    assert result['jobs'][0]['node_list'] == 'node1'


def test_slurm_job_details_unavailable(monkeypatch: Any) -> None:
    """Non-Slurm hosts should return an explicit unavailable result."""
    procs._SLURM_DETAILS_CACHE.update(time=0.0, value=None)
    monkeypatch.setattr(procs.shutil, 'which', lambda name: None)
    result = procs.slurm_job_details()
    assert not result['available']
    assert result['jobs'] == []
    assert 'not available' in result['error']


def _running_entry(queue_path, run, lines, age):
    """Write one running queue yaml, aged by `age` seconds."""
    group = 'APERO-QUEUE-GROUP-00000000001-0001-PP'
    run_dir = queue_path / drs_queue.QUEUE_RUNNING_DIR / group
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / run
    path.write_text('state: running\nrunstring: x\n' + lines)
    stamp = os.path.getmtime(path) - age
    os.utime(path, (stamp, stamp))
    return '{0}/{1}'.format(group, run)


def test_fail_stale_running(tmp_path, monkeypatch):
    queue_path = tmp_path / 'queue'
    for state in drs_queue.QUEUE_SUB_DIRS:
        (queue_path / state).mkdir(parents=True)
    proc_dir = procs.get_proc_dir(str(tmp_path))
    monkeypatch.setattr(drs_queue, 'get_queue_path',
                        lambda params: str(queue_path))
    monkeypatch.setattr(drs_queue, 'get_proc_dir', lambda params: proc_dir)
    monkeypatch.setattr(procs, 'user_slurm_jobs', lambda: None)
    host = socket.gethostname()
    dead = _running_entry(queue_path, 'APERO-QUEUE-RUN-00000001.yaml',
                          'pid: 999999999\npid_host: {0}\n'.format(host), 0)
    alive = _running_entry(queue_path, 'APERO-QUEUE-RUN-00000002.yaml',
                           'pid: {0}\npid_host: {1}\n'.format(os.getpid(),
                                                              host), 0)
    remote = _running_entry(queue_path, 'APERO-QUEUE-RUN-00000003.yaml',
                            'pid: 1\npid_host: other-node\n', 0)
    fresh = _running_entry(queue_path, 'APERO-QUEUE-RUN-00000004.yaml',
                           '', 10)
    old = _running_entry(queue_path, 'APERO-QUEUE-RUN-00000005.yaml', '',
                         drs_queue.QUEUE_STALE_GRACE + 60)
    held = _running_entry(queue_path, 'APERO-QUEUE-RUN-00000006.yaml', '',
                          drs_queue.QUEUE_STALE_GRACE + 60)
    # a live registered process (this test) holds one old entry
    procs.register(proc_dir, 'run', 'run', pid=os.getpid(), qids=[held])
    stale = {item['qid'] for item in drs_queue.find_stale_running(None)}
    assert stale == {dead, old}
    _ = alive, remote, fresh
    result = drs_queue.fail_stale_running(None)
    assert result['moved'] == 2
    failed = queue_path / drs_queue.QUEUE_FAILED_DIR
    assert (failed / dead).exists() and (failed / old).exists()
    log = drs_queue.get_task_log_path(str(queue_path), *dead.split('/'))
    assert 'marked failed' in open(log).read()
    assert drs_queue.find_stale_running(None) == []


def test_stop_local_process(tmp_path, monkeypatch):
    proc_dir = procs.get_proc_dir(str(tmp_path))
    monkeypatch.setattr(drs_queue, 'get_proc_dir', lambda params: proc_dir)
    child = subprocess.Popen([sys.executable, '-c',
                              'import time; time.sleep(60)'],
                             start_new_session=True)
    # reap the child like the gui job thread does (a zombie looks alive)
    threading.Thread(target=child.wait, daemon=True).start()
    try:
        proc_id = procs.register(proc_dir, 'generate', 'apero_processing',
                                 pid=child.pid, owner='gui')
        record = procs.load(proc_dir, proc_id)
        assert procs.proc_status(record, None) == 'running'
        result = drs_queue.stop_process(None, record)
        assert result['success'], result['message']
        child.wait(timeout=10)
        record = procs.load(proc_dir, proc_id)
        assert procs.proc_status(record, None) == 'stopped'
        again = drs_queue.stop_process(None, record)
        assert not again['success']
    finally:
        if child.poll() is None:
            child.kill()
