"""Tests for the APERO queue task statistics (Stats tab)."""
import sys

from apero.tools.module.processing import drs_queue_gui
from apero.tools.module.processing import drs_queue_stats as stats

# a child that allocates ~50 MB and burns cpu for ~1.5 s
CHILD = ('import time; data = bytearray(50 * 1024 * 1024); '
         'end = time.time() + 1.5\n'
         'while time.time() < end: sum(range(1000))')


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
