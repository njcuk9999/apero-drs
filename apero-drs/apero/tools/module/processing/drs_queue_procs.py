#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO queue process registry

Records the long running processes started around the queue so the queue
dashboard can list them, show their logs and stop them:

    - generate: apero_processing (queue mode) started by the gui
    - reset: apero_reset started by the gui
    - run: apero_queue.py run (cli or gui) - the queue tasks it is
           currently running are kept in "qids"
    - batch / chain: submitted Slurm jobs (job ids + sbatch log files)

Every process is one small json file in the registry directory (written
atomically). Only the standard library is used so recording a process
never slows down the caller.

Created on 2026-10-28

@author: cook
"""
import getpass
import glob
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import time
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_queue_procs.py'
# registry directory name (inside PATH.OTHER, next to the gui job logs)
PROC_DIR_NAME = 'queue_processes'
# valid process kinds
PROC_KINDS = ['generate', 'reset', 'run', 'batch', 'chain']
# valid process ids (also used to refuse paths from the browser)
PROC_ID_RE = re.compile(r'^[a-z]+-\d{8}-\d{6}-[0-9a-f]{6}$')
# job ids printed by sbatch ("Submitted batch job 123", "--parsable" or the
#   chain submit script "Submitted <group>: 123")
SBATCH_ID_RE = re.compile(r'(?:Submitted batch job |: |^)(\d+)(?:;\S*)?\s*$')
# the most queue ids kept per process (runs with ntasks=all keep cycling)
MAX_QIDS = 5000
# seconds a squeue answer is reused (many browsers poll the registry)
SQUEUE_CACHE_SECONDS = 5.0
_SQUEUE_CACHE: Dict[str, Any] = dict(time=0.0, key=None, value=None)
_USER_JOBS_CACHE: Dict[str, Any] = dict(time=0.0, value=set())


# =============================================================================
# Define registry functions
# =============================================================================
def get_proc_dir(other_path: str) -> str:
    """
    Get (and create) the process registry directory

    :param other_path: str, the PATH.OTHER directory

    :return: str, the registry directory
    """
    proc_dir = os.path.join(str(other_path), PROC_DIR_NAME)
    os.makedirs(proc_dir, exist_ok=True)
    return proc_dir


def _proc_path(proc_dir: str, proc_id: str) -> Optional[str]:
    """Return the record path for a valid process id (None if invalid)."""
    if not PROC_ID_RE.match(str(proc_id)):
        return None
    return os.path.join(proc_dir, '{0}.json'.format(proc_id))


def _write(proc_dir: str, record: Dict[str, Any]):
    """Write one record atomically."""
    os.makedirs(proc_dir, exist_ok=True)
    path = _proc_path(proc_dir, record['id'])
    tmp_path = '{0}.tmp{1}'.format(path, os.getpid())
    with open(tmp_path, 'w') as pfile:
        json.dump(record, pfile, indent=1)
    os.replace(tmp_path, path)


def load(proc_dir: str, proc_id: str) -> Optional[Dict[str, Any]]:
    """
    Load one process record

    :param proc_dir: str, the registry directory
    :param proc_id: str, the process id

    :return: dict or None (unknown/invalid id)
    """
    path = _proc_path(proc_dir, proc_id)
    if path is None or not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as pfile:
            return json.load(pfile)
    except (OSError, ValueError):
        return None


def load_all(proc_dir: str) -> List[Dict[str, Any]]:
    """
    Load every process record (newest first)

    :param proc_dir: str, the registry directory

    :return: list of dicts
    """
    if not os.path.isdir(proc_dir):
        return []
    records = []
    for name in os.listdir(proc_dir):
        if not name.endswith('.json'):
            continue
        record = load(proc_dir, name[:-len('.json')])
        if record is not None:
            records.append(record)
    records.sort(key=lambda rec: rec.get('started', ''), reverse=True)
    return records


def register(proc_dir: str, kind: str, label: str, cmd: str = '',
             pid: Optional[int] = None, owner: str = 'cli',
             log_paths: Optional[List[str]] = None,
             log_globs: Optional[List[str]] = None,
             slurm_jobs: Optional[List[str]] = None,
             qids: Optional[List[str]] = None) -> Optional[str]:
    """
    Record a new process (never raises - registry problems must not stop
    the actual work)

    :param proc_dir: str, the registry directory
    :param kind: str, one of PROC_KINDS
    :param label: str, short human readable description
    :param cmd: str, the command line (display only)
    :param pid: int or None, the local process id (None for slurm jobs)
    :param owner: str, 'gui' (started by the dashboard) or 'cli'
    :param log_paths: list of str or None, log files
    :param log_globs: list of str or None, glob patterns for log files
                      that only exist later (sbatch .out/.err files)
    :param slurm_jobs: list of str or None, Slurm job ids
    :param qids: list of str or None, queue ids handled by this process

    :return: str or None, the process id (None if recording failed)
    """
    stamp = time.strftime('%Y%m%d-%H%M%S')
    proc_id = '{0}-{1}-{2}'.format(kind, stamp, secrets.token_hex(3))
    record = dict(id=proc_id, kind=kind, label=str(label), cmd=str(cmd),
                  pid=pid, host=socket.gethostname(), owner=owner,
                  started=time.strftime('%Y-%m-%d %H:%M:%S'),
                  finished=None, returncode=None, stopped=False,
                  log_paths=list(log_paths or []),
                  log_globs=list(log_globs or []),
                  slurm_jobs=[str(job) for job in (slurm_jobs or [])],
                  qids=list(qids or [])[-MAX_QIDS:])
    try:
        _write(proc_dir, record)
    except OSError:
        return None
    return proc_id


def update(proc_dir: str, proc_id: Optional[str], **fields: Any):
    """
    Update fields of a process record (never raises)

    :param proc_dir: str, the registry directory
    :param proc_id: str or None, the process id (None does nothing)
    :param fields: the fields to set

    :return: None
    """
    if proc_id is None:
        return
    record = load(proc_dir, proc_id)
    if record is None:
        return
    record.update(fields)
    if 'qids' in fields:
        record['qids'] = list(record['qids'])[-MAX_QIDS:]
    try:
        _write(proc_dir, record)
    except OSError:
        return


def finish(proc_dir: str, proc_id: Optional[str], returncode: int,
           stopped: bool = False):
    """
    Mark a process as finished (never raises)

    :param proc_dir: str, the registry directory
    :param proc_id: str or None, the process id
    :param returncode: int, the exit code (0 = success)
    :param stopped: bool, True if the process was stopped by a user

    :return: None
    """
    fields = dict(finished=time.strftime('%Y-%m-%d %H:%M:%S'),
                  returncode=int(returncode))
    if stopped:
        fields['stopped'] = True
    update(proc_dir, proc_id, **fields)


def remove(proc_dir: str, proc_ids: List[str]) -> int:
    """
    Remove process records (does not stop anything)

    :param proc_dir: str, the registry directory
    :param proc_ids: list of str, the process ids

    :return: int, the number of records removed
    """
    removed = 0
    for proc_id in proc_ids:
        path = _proc_path(proc_dir, proc_id)
        if path is not None and os.path.exists(path):
            os.remove(path)
            removed += 1
    return removed


# =============================================================================
# Define status functions
# =============================================================================
def parse_sbatch_ids(text: str) -> List[str]:
    """
    Get the Slurm job ids printed by sbatch (or the chain submit script)

    :param text: str, the sbatch standard output

    :return: list of str, the job ids
    """
    ids = []
    for line in str(text).splitlines():
        match = SBATCH_ID_RE.search(line.strip())
        if match:
            ids.append(match.group(1))
    return ids


def slurm_states(job_ids: List[str]) -> Optional[Dict[str, str]]:
    """
    Get the squeue state of Slurm jobs (jobs missing from squeue finished)

    :param job_ids: list of str, the job ids (array jobs use the base id)

    :return: dict job id -> state (e.g. RUNNING, PENDING) or None when
             squeue is not available
    """
    if shutil.which('squeue') is None:
        return None
    if len(job_ids) == 0:
        return dict()
    key = ','.join(sorted(set(job_ids)))
    now = time.time()
    fresh = now - _SQUEUE_CACHE['time'] < SQUEUE_CACHE_SECONDS
    if _SQUEUE_CACHE['key'] == key and fresh:
        return dict(_SQUEUE_CACHE['value'])
    cmd = ['squeue', '-h', '-o', '%i %T', '-j', key]
    try:
        output = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    states = dict()
    for line in output.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        # array jobs are listed as 123_4 or 123_[5-9]
        base_id = parts[0].split('_')[0]
        # any running element makes the whole job running
        if states.get(base_id) != 'RUNNING':
            states[base_id] = parts[1]
    _SQUEUE_CACHE.update(time=now, key=key, value=dict(states))
    return states


def user_slurm_jobs() -> Optional[set]:
    """
    Get the base ids of every Slurm job of the current user

    :return: set of str, or None when squeue is not available
    """
    if shutil.which('squeue') is None:
        return None
    now = time.time()
    if now - _USER_JOBS_CACHE['time'] < SQUEUE_CACHE_SECONDS:
        return set(_USER_JOBS_CACHE['value'])
    cmd = ['squeue', '-h', '-u', getpass.getuser(), '-o', '%i']
    try:
        output = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if output.returncode != 0:
        return None
    jobs = {line.split('_')[0] for line in output.stdout.split()}
    _USER_JOBS_CACHE.update(time=now, value=set(jobs))
    return jobs


def pid_alive(pid: Any) -> bool:
    """
    Check whether a local process id is still alive

    :param pid: Any, the process id

    :return: bool, True if the process exists
    """
    try:
        os.kill(int(pid), 0)
    except (TypeError, ValueError, ProcessLookupError):
        return False
    except PermissionError:
        return True
    return True


def proc_status(record: Dict[str, Any],
                slurm: Optional[Dict[str, str]]) -> str:
    """
    Work out the current status of one process record

    :param record: dict, the process record
    :param slurm: dict or None, the slurm_states result

    :return: str, one of running, pending, complete, failed, stopped,
             finished (slurm jobs gone from squeue), lost (process died
             without finishing) or unknown (cannot be checked from here)
    """
    if record.get('finished'):
        if record.get('stopped'):
            return 'stopped'
        return 'complete' if record.get('returncode') == 0 else 'failed'
    jobs = record.get('slurm_jobs') or []
    if len(jobs) > 0:
        if slurm is None:
            return 'unknown'
        states = [slurm[job] for job in jobs if job in slurm]
        if len(states) == 0:
            return 'finished'
        if any(state != 'PENDING' for state in states):
            return 'running'
        return 'pending'
    if record.get('pid') is None:
        return 'unknown'
    if record.get('host') != socket.gethostname():
        return 'unknown'
    return 'running' if pid_alive(record['pid']) else 'lost'


def log_files(record: Dict[str, Any]) -> List[str]:
    """
    Get the existing log files of a process (fixed paths + globs)

    :param record: dict, the process record

    :return: list of str, the log file paths
    """
    paths = [path for path in record.get('log_paths', [])
             if os.path.exists(path)]
    for pattern in record.get('log_globs', []):
        paths += sorted(glob.glob(pattern))
    return paths


# =============================================================================
# End of code
# =============================================================================
