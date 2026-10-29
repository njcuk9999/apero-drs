"""Tests for the APERO queue process registry (Processes tab)."""
import os
import socket
import subprocess
import sys
import threading

from apero.tools.module.processing import drs_queue
from apero.tools.module.processing import drs_queue_procs as procs


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
