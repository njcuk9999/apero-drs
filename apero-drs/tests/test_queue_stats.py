"""Tests for the APERO queue task statistics (Stats tab)."""
import sys
import json
import os
from pathlib import Path
from typing import Any

from apero.tools.module.processing import drs_queue_gui
from apero.tools.module.processing import drs_queue_stats as stats

# a child that allocates ~50 MB and burns cpu for ~1.5 s
CHILD = ('import time; data = bytearray(50 * 1024 * 1024); '
         'end = time.time() + 1.5\n'
         'while time.time() < end: sum(range(1000))')


def test_reader_rewrite_and_delete(tmp_path: Path) -> None:
    """Rebuild cached records after atomic replacement and deletion.

    :param tmp_path: Temporary stats directory.
    :return: None.
    """
    path = tmp_path / 'tasks-test.jsonl'
    path.write_text(json.dumps(dict(qid='G/R1')) + '\n')
    reader = stats.StatsReader()
    reader.update(str(tmp_path))
    replacement = tmp_path / 'replacement'
    replacement.write_text(json.dumps(dict(qid='G/R2')) + '\n')
    replacement.replace(path)
    reader.update(str(tmp_path))
    assert [task['qid'] for task in reader.tasks] == ['G/R2']
    previous = path.stat()
    path.write_text(json.dumps(dict(qid='G/R3')) + '\n')
    os.utime(path, ns=(previous.st_atime_ns, previous.st_mtime_ns + 1000000))
    reader.update(str(tmp_path))
    assert [task['qid'] for task in reader.tasks] == ['G/R3']
    path.write_text('')
    reader.update(str(tmp_path))
    assert reader.tasks == []
    path.unlink()
    reader.update(str(tmp_path))
    assert reader.tasks == []


def test_remove_exact_qids_from_shared_stores(tmp_path: Path) -> None:
    """Filtering preserves other tasks, malformed lines, and reader state.

    :param tmp_path: Temporary stats directory.
    :return: None.
    """
    for prefix in [stats.TASK_PREFIX, stats.SAMPLE_PREFIX]:
        path = tmp_path / (prefix + 'shared.jsonl')
        rows = [dict(qid='G/R1'), dict(qid='G/R10')]
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    reader = stats.StatsReader()
    reader.update(str(tmp_path))
    stats.remove_qids(str(tmp_path), ['G/R1'])
    reader.update(str(tmp_path))
    assert [row['qid'] for row in reader.tasks] == ['G/R10']
    assert [row['qid'] for row in reader.samples] == ['G/R10']
    malformed = tmp_path / 'tasks-broken.jsonl'
    malformed.write_bytes(b'not json\n{"qid":')
    stats.remove_qids(str(tmp_path), ['G/R10'])
    reader.update(str(tmp_path))
    assert reader.tasks == reader.samples == []
    assert malformed.read_bytes() == b'not json\n{"qid":'
    assert not (tmp_path / 'tasks-shared.jsonl').exists()


def test_gui_cache_notices_same_count_rewrite(tmp_path: Path,
                                             monkeypatch: Any) -> None:
    """Replacing one task with one other task invalidates aggregation.

    :param tmp_path: Temporary stats root.
    :param monkeypatch: Runtime overrides.
    :return: None.
    """
    monkeypatch.setattr(drs_queue_gui.drs_queue, 'get_queue_path',
                        lambda params: str(tmp_path))
    directory = tmp_path / 'output' / 'stats'
    directory.mkdir(parents=True)
    path = directory / 'tasks-cache.jsonl'
    row = dict(qid='G/R1', start=1, end=2)
    path.write_text(json.dumps(row) + '\n')
    assert drs_queue_gui.get_stats_data(None)['tasks']['qid'] == ['G/R1']
    row['qid'] = 'G/R2'
    replacement = directory / 'replacement'
    replacement.write_text(json.dumps(row) + '\n')
    replacement.replace(path)
    assert drs_queue_gui.get_stats_data(None)['tasks']['qid'] == ['G/R2']


def test_monitor_wrapper_records_task_and_samples(tmp_path):
    argv = ['--stats', str(tmp_path), '--qid', 'G/R1', '--shortname', 'PP',
            '--recipe', 'apero_preprocess.py', '--mode', 'batch', '--',
            sys.executable, '-c', CHILD]
    original = stats.SAMPLE_INTERVAL
    stats.SAMPLE_INTERVAL = 0.3
    try:
        assert stats.main(argv) == 0
    finally:
        stats.SAMPLE_INTERVAL = original
    reader = stats.StatsReader()
    reader.update(str(tmp_path))
    assert len(reader.tasks) == 1
    task = reader.tasks[0]
    assert task['shortname'] == 'PP' and task['success']
    assert task['duration'] > 1.0
    assert task['peak_rss_mb'] > 40
    assert task['cpu_s'] > 0.5
    assert len(reader.samples) >= 1
    # a second update only reads new lines
    reader.update(str(tmp_path))
    assert len(reader.tasks) == 1


def test_failed_command_exit_code(tmp_path):
    argv = ['--stats', str(tmp_path), '--qid', 'G/R2', '--',
            sys.executable, '-c', 'raise SystemExit(3)']
    assert stats.main(argv) == 3
    reader = stats.StatsReader()
    reader.update(str(tmp_path))
    assert reader.tasks[0]['returncode'] == 3
    assert not reader.tasks[0]['success']


def test_bin_samples_sums_tasks_per_type():
    samples = [dict(t=100, qid='a', shortname='PP', rss_mb=100, cpu=100),
               dict(t=105, qid='a', shortname='PP', rss_mb=300, cpu=100),
               dict(t=101, qid='b', shortname='PP', rss_mb=50, cpu=50,
                    host='h', load1=2.0, mem_avail_mb=1000),
               dict(t=102, qid='c', shortname='DARK', rss_mb=10, cpu=200),
               dict(t=150, qid='c', shortname='DARK', rss_mb=20, cpu=0)]
    out = drs_queue_gui._bin_samples(samples, 100, 10, 6)
    # task a averages to 200 MB, plus task b 50 MB in the first bin
    assert out['types']['PP']['rss_mb'][0] == 250
    assert out['types']['PP']['ntasks'][0] == 2
    assert out['types']['DARK']['cpu'][0] == 200
    assert out['types']['DARK']['rss_mb'][5] == 20
    assert out['hosts']['h']['load1'][0] == 2.0
