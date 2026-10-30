#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO queue task statistics (timing + resource monitoring)

Every queue task (run, batch or chain mode) is watched by a TaskMonitor:

    - one task record when the task ends (start, end, duration, result,
      peak RAM, CPU time, disk I/O)
    - one sample every SAMPLE_INTERVAL seconds while it runs (RAM, CPU,
      number of processes, disk I/O rate, host load and free memory)

The whole process group of the task is measured (the shell, the recipe
and any multiprocessing children) from /proc, so this works on Linux
login and compute nodes without extra packages. Each writing process uses
its own json-lines files (no locking between processes), all inside
{QUEUE.PATH}/output/stats.

This file only uses the standard library: batch/chain scripts run it
directly by path to wrap a task command:

    python drs_queue_stats.py --stats DIR --qid QID --shortname PP
        --recipe apero_preprocess.py --mode batch -- <command>

Created on 2026-10-28

@author: cook
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_queue_stats.py'
# seconds between resource samples of a running task
SAMPLE_INTERVAL = 10.0
# file name prefixes inside the stats directory
TASK_PREFIX = 'tasks-'
SAMPLE_PREFIX = 'samples-'
# clock ticks per second (cpu times in /proc/<pid>/stat)
try:
    CLOCK_TICKS = os.sysconf('SC_CLK_TCK')
except (AttributeError, ValueError, OSError):
    CLOCK_TICKS = 100
# serialises writes from monitor threads of the same process
_WRITE_LOCK = threading.Lock()


# =============================================================================
# Define /proc readers
# =============================================================================
def _group_pids(pgid: int) -> List[int]:
    """
    Get every pid in a process group (the task runs in its own session)

    :param pgid: int, the process group id

    :return: list of int, the pids (empty when /proc is not available)
    """
    pids = []
    try:
        names = os.listdir('/proc')
    except OSError:
        return pids
    for name in names:
        if not name.isdigit():
            continue
        try:
            with open('/proc/{0}/stat'.format(name), 'r') as sfile:
                stat = sfile.read()
        except OSError:
            continue
        # the command name (field 2) may contain spaces - split after it
        fields = stat[stat.rfind(')') + 2:].split()
        if len(fields) > 2 and int(fields[2]) == pgid:
            pids.append(int(name))
    return pids


def _proc_usage(pid: int) -> Optional[Dict[str, float]]:
    """
    Read the RAM, cpu time and disk I/O counters of one process

    :param pid: int, the process id

    :return: dict(rss_mb, cpu_s, read_mb, write_mb) or None if it is gone
    """
    try:
        with open('/proc/{0}/stat'.format(pid), 'r') as sfile:
            stat = sfile.read()
        fields = stat[stat.rfind(')') + 2:].split()
        cpu_s = (int(fields[11]) + int(fields[12])) / CLOCK_TICKS
        rss_mb = 0.0
        with open('/proc/{0}/status'.format(pid), 'r') as sfile:
            for line in sfile:
                if line.startswith('VmRSS:'):
                    rss_mb = int(line.split()[1]) / 1024.0
                    break
    except (OSError, ValueError, IndexError):
        return None
    read_mb, write_mb = 0.0, 0.0
    try:
        with open('/proc/{0}/io'.format(pid), 'r') as ifile:
            for line in ifile:
                key, _, value = line.partition(':')
                if key == 'read_bytes':
                    read_mb = int(value) / 1048576.0
                elif key == 'write_bytes':
                    write_mb = int(value) / 1048576.0
    except (OSError, ValueError):
        pass
    return dict(rss_mb=rss_mb, cpu_s=cpu_s, read_mb=read_mb,
                write_mb=write_mb)


def _host_usage() -> Dict[str, float]:
    """
    Read the host load average and available memory

    :return: dict(load1, mem_avail_mb)
    """
    out = dict(load1=None, mem_avail_mb=None)
    try:
        out['load1'] = round(os.getloadavg()[0], 2)
    except (AttributeError, OSError):
        pass
    try:
        with open('/proc/meminfo', 'r') as mfile:
            for line in mfile:
                if line.startswith('MemAvailable:'):
                    out['mem_avail_mb'] = round(int(line.split()[1]) / 1024)
                    break
    except (OSError, ValueError):
        pass
    return out


# =============================================================================
# Define classes
# =============================================================================
class TaskMonitor:
    """
    Measure one queue task (its whole process group) while it runs and
    write a task record when it ends. Never raises - statistics must not
    break the queue.
    """
    def __init__(self, stats_dir: Optional[str], qid: str, shortname: str,
                 recipe: str = '', mode: str = 'run',
                 interval: Optional[float] = None) -> None:
        """
        :param stats_dir: str or None, the stats directory (None disables)
        :param qid: str, the queue id "{group}/{run_file}"
        :param shortname: str, the recipe short name (e.g. PP, DARK)
        :param recipe: str, the recipe name
        :param mode: str, 'run', 'batch' or 'chain'
        :param interval: float or None, seconds between samples (None uses
                         SAMPLE_INTERVAL)
        """
        self.stats_dir = stats_dir
        self.info = dict(qid=qid, group=str(qid).split('/')[0],
                         shortname=shortname, recipe=recipe, mode=mode,
                         host=socket.gethostname())
        self.interval = SAMPLE_INTERVAL if interval is None else interval
        self.pid = None
        self.start = None
        self.peak_rss = 0.0
        self.cpu_s = 0.0
        self.io = dict(read_mb=0.0, write_mb=0.0)
        # cumulative counters of processes that already exited
        self._done = dict(cpu_s=0.0, read_mb=0.0, write_mb=0.0)
        self._last = dict()
        self._stop = threading.Event()
        self._thread = None
        self._nsamples = 0

    def begin(self, pid: int) -> None:
        """
        Start watching the process group led by pid

        :param pid: int, the task process id (a session/group leader)
        """
        self.pid = pid
        self.start = time.time()
        if self.stats_dir is None:
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _measure(self) -> Dict[str, float]:
        """Sum the usage of every process still in the task group."""
        current = dict()
        for pid in _group_pids(self.pid):
            usage = _proc_usage(pid)
            if usage is not None:
                current[pid] = usage
        # counters of processes that exited since the last sample
        for pid, usage in self._last.items():
            if pid not in current:
                for key in self._done:
                    self._done[key] += usage[key]
        self._last = current
        total = dict(rss_mb=0.0, nproc=len(current))
        for key in self._done:
            total[key] = self._done[key] + sum(u[key]
                                               for u in current.values())
        total['rss_mb'] = sum(u['rss_mb'] for u in current.values())
        return total

    def _loop(self) -> None:
        """Sample until the task ends."""
        prev, prev_time = None, None
        while True:
            try:
                now = time.time()
                usage = self._measure()
                self.peak_rss = max(self.peak_rss, usage['rss_mb'])
                self.cpu_s = max(self.cpu_s, usage['cpu_s'])
                self.io['read_mb'] = max(self.io['read_mb'],
                                         usage['read_mb'])
                self.io['write_mb'] = max(self.io['write_mb'],
                                          usage['write_mb'])
                if prev is not None and usage['nproc'] > 0:
                    self._write(SAMPLE_PREFIX,
                                self._sample(now, usage, prev, prev_time))
                    self._nsamples += 1
                prev, prev_time = usage, now
            except Exception as _:
                pass
            if self._stop.wait(self.interval if prev_time else 1.0):
                return

    def _sample(self, now: float, usage: Dict[str, float],
                prev: Dict[str, float], prev_time: float) -> Dict[str, Any]:
        """Build one resource sample (rates since the previous sample)."""
        dtime = max(now - prev_time, 1e-3)

        def _rate(key: str) -> float:
            """Calculate a non-negative per-second counter rate."""
            return round(max(0.0, usage[key] - prev[key]) / dtime, 3)

        sample = dict(t=round(now, 1), qid=self.info['qid'],
                      shortname=self.info['shortname'],
                      host=self.info['host'],
                      rss_mb=round(usage['rss_mb'], 1), nproc=usage['nproc'],
                      # percent of one core (200 = two busy cores)
                      cpu=round(100 * _rate('cpu_s'), 1),
                      read_mb_s=_rate('read_mb'),
                      write_mb_s=_rate('write_mb'))
        sample.update(_host_usage())
        return sample

    def finish(self, returncode: int,
               success: Optional[bool] = None) -> None:
        """
        Stop watching and write the task record

        :param returncode: int, the task exit code
        :param success: bool or None, the task result (None = exit code 0)
        """
        end = time.time()
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        if self.stats_dir is None or self.start is None:
            return
        if success is None:
            success = returncode == 0
        record = dict(self.info)
        record.update(start=round(self.start, 1), end=round(end, 1),
                      duration=round(end - self.start, 2),
                      returncode=returncode, success=bool(success),
                      peak_rss_mb=round(self.peak_rss, 1),
                      cpu_s=round(self.cpu_s, 1),
                      read_mb=round(self.io['read_mb'], 1),
                      write_mb=round(self.io['write_mb'], 1),
                      nsamples=self._nsamples)
        self._write(TASK_PREFIX, record)

    def _write(self, prefix: str, record: Dict[str, Any]) -> None:
        """Append one json line to this process' stats file."""
        name = '{0}{1}-{2}.jsonl'.format(prefix, self.info['host'],
                                         os.getpid())
        try:
            with _WRITE_LOCK:
                os.makedirs(self.stats_dir, exist_ok=True)
                with open(os.path.join(self.stats_dir, name), 'a') as sfile:
                    sfile.write(json.dumps(record) + '\n')
        except OSError:
            pass


# =============================================================================
# Define reader
# =============================================================================
class StatsReader:
    """
    Incremental reader of the stats directory (only new bytes are parsed
    on each call, so the dashboard can poll it cheaply)
    """
    def __init__(self) -> None:
        """Initialize incremental offsets and task/sample result buffers."""
        self.offsets: Dict[str, int] = dict()
        self.tasks: List[Dict[str, Any]] = []
        self.samples: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def update(self, stats_dir: str) -> None:
        """
        Parse anything new in the stats directory

        :param stats_dir: str, the stats directory
        """
        with self.lock:
            if not os.path.isdir(stats_dir):
                self.offsets, self.tasks, self.samples = dict(), [], []
                return
            for name in sorted(os.listdir(stats_dir)):
                if not name.endswith('.jsonl'):
                    continue
                if name.startswith(TASK_PREFIX):
                    target = self.tasks
                elif name.startswith(SAMPLE_PREFIX):
                    target = self.samples
                else:
                    continue
                path = os.path.join(stats_dir, name)
                offset = self.offsets.get(path, 0)
                try:
                    size = os.path.getsize(path)
                except OSError:
                    continue
                # a removed/rewritten stats directory - start again
                if size < offset:
                    self.offsets, self.tasks, self.samples = dict(), [], []
                    return self.update(stats_dir)
                if size == offset:
                    continue
                with open(path, 'rb') as sfile:
                    sfile.seek(offset)
                    data = sfile.read(size - offset)
                # only complete lines (a writer may be mid-line)
                cut = data.rfind(b'\n')
                if cut < 0:
                    continue
                for line in data[:cut + 1].splitlines():
                    try:
                        target.append(json.loads(line))
                    except ValueError:
                        continue
                self.offsets[path] = offset + cut + 1


# =============================================================================
# Define command line wrapper (batch/chain scripts)
# =============================================================================
def main(argv: Optional[List[str]] = None) -> int:
    """
    Run a command in its own session while monitoring it

    :param argv: list of str or None, the command line arguments

    :return: int, the command exit code
    """
    parser = argparse.ArgumentParser(description='APERO queue task monitor')
    parser.add_argument('--stats', required=True)
    parser.add_argument('--qid', required=True)
    parser.add_argument('--shortname', default='')
    parser.add_argument('--recipe', default='')
    parser.add_argument('--mode', default='batch')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = list(args.command)
    if command[:1] == ['--']:
        command = command[1:]
    if len(command) == 0:
        parser.error('no command given')
    monitor = TaskMonitor(args.stats, args.qid, args.shortname,
                          recipe=args.recipe, mode=args.mode)
    process = subprocess.Popen(command, start_new_session=True)
    monitor.begin(process.pid)
    try:
        returncode = process.wait()
    except KeyboardInterrupt:
        process.terminate()
        returncode = process.wait()
    monitor.finish(returncode)
    return returncode


if __name__ == '__main__':
    sys.exit(main())

# =============================================================================
# End of code
# =============================================================================
