#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generic gui process registry

Records the long running processes started by (or around) a browser gui so
the gui can list them, show their logs and stop them. A process is either:

    - a local process (pid + host + log files), e.g. a command run by the
      gui in the background
    - one or more submitted Slurm jobs (job ids + sbatch log files)

Processes may also record the work-item ids ("qids") they are handling so
an application can link a process to its own task logs.

Every process is one small json file in the registry directory (written
atomically). Only the standard library is used so recording a process
never slows down the caller.

The "kind" of a process is a free (lower case) string chosen by the
application (e.g. 'run', 'batch', 'reset').

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
import signal
import socket
import subprocess
import time
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.procs.py'
# default registry directory name (inside the application state directory,
#    next to the gui job logs)
PROC_DIR_NAME = 'gui_processes'
# default directory name (next to the registry) holding gui job logs - log
#    files inside it are owned by the gui and may be deleted on removal
JOB_DIR_NAME = 'gui_jobs'
# valid process ids (also used to refuse paths from the browser)
PROC_ID_RE = re.compile(r'^[a-z]+-\d{8}-\d{6}-[0-9a-f]{6}$')
# job ids printed by sbatch ("Submitted batch job 123", "--parsable" or the
#   chain submit scripts "Submitted <group>: 123")
SBATCH_ID_RE = re.compile(r'(?:Submitted batch job |: |^)(\d+)(?:;\S*)?\s*$')
# the most work-item ids kept per process (long runs keep cycling)
MAX_QIDS = 5000
# keep newly accepted Slurm jobs visible while squeue catches up
SLURM_START_GRACE = 90
# seconds a squeue answer is reused (many browsers poll the registry)
SQUEUE_CACHE_SECONDS = 5.0
_SQUEUE_CACHE: Dict[str, Any] = dict(time=0.0, key=None, value=None)
_USER_JOBS_CACHE: Dict[str, Any] = dict(time=0.0, value=set())
_SLURM_DETAILS_CACHE: Dict[str, Any] = dict(time=0.0, value=None)


# =============================================================================
# Define registry functions
# =============================================================================
def get_proc_dir(state_path: str, dir_name: str = PROC_DIR_NAME) -> str:
    """
    Get (and create) the process registry directory

    :param state_path: str, the application state directory the registry
                       lives in
    :param dir_name: str, the registry directory name

    :return: str, the registry directory
    """
    proc_dir = os.path.join(str(state_path), dir_name)
    os.makedirs(proc_dir, exist_ok=True)
    return proc_dir


def _proc_path(proc_dir: str, proc_id: str) -> Optional[str]:
    """Return the record path for a valid process id (None if invalid)."""
    if not PROC_ID_RE.match(str(proc_id)):
        return None
    return os.path.join(proc_dir, '{0}.json'.format(proc_id))


def _write(proc_dir: str, record: Dict[str, Any]) -> None:
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
             qids: Optional[List[str]] = None,
             artifact_paths: Optional[List[str]] = None) -> Optional[str]:
    """
    Record a new process (never raises - registry problems must not stop
    the actual work)

    :param proc_dir: str, the registry directory
    :param kind: str, the (application defined) kind of process
    :param label: str, short human readable description
    :param cmd: str, the command line (display only)
    :param pid: int or None, the local process id (None for slurm jobs)
    :param owner: str, 'gui' (started by the dashboard) or 'cli'
    :param log_paths: list of str or None, log files
    :param log_globs: list of str or None, glob patterns for log files
                      that only exist later (sbatch .out/.err files)
    :param slurm_jobs: list of str or None, Slurm job ids
    :param qids: list of str or None, work-item ids handled by this
                 process
    :param artifact_paths: Explicitly owned generated scripts/index files.

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
                  artifact_paths=list(artifact_paths or []),
                  slurm_jobs=[str(job) for job in (slurm_jobs or [])],
                  slurm_submitted_at=(time.time() if slurm_jobs else None),
                  qids=list(qids or [])[-MAX_QIDS:])
    try:
        _write(proc_dir, record)
    except OSError:
        return None
    return proc_id


def update(proc_dir: str, proc_id: Optional[str], **fields: Any) -> None:
    """
    Update fields of a process record (never raises)

    :param proc_dir: str, the registry directory
    :param proc_id: str or None, the process id (None does nothing)
    :param fields: the fields to set

    :return: None. Persists the updated process record when it exists.
    """
    if proc_id is None:
        return
    record = load(proc_dir, proc_id)
    if record is None:
        return
    record.update(fields)
    if fields.get('slurm_jobs'):
        record['slurm_submitted_at'] = time.time()
    if 'qids' in fields:
        record['qids'] = list(record['qids'])[-MAX_QIDS:]
    try:
        _write(proc_dir, record)
    except OSError:
        return


def finish(proc_dir: str, proc_id: Optional[str], returncode: int,
           stopped: bool = False) -> None:
    """
    Mark a process as finished (never raises)

    :param proc_dir: str, the registry directory
    :param proc_id: str or None, the process id
    :param returncode: int, the exit code (0 = success)
    :param stopped: bool, True if the process was stopped by a user

    :return: None. Marks the process record as finished when found.
    """
    fields = dict(finished=time.strftime('%Y-%m-%d %H:%M:%S'),
                  returncode=int(returncode))
    if stopped:
        fields['stopped'] = True
    update(proc_dir, proc_id, **fields)


def owned_file(path: str, roots: List[str]) -> bool:
    """Check that a regular file resolves inside a trusted artifact root.

    :param path: Candidate file path.
    :param roots: Trusted artifact directories, never record-supplied paths.
    :return: Whether deletion is bounded to an owned directory.
    """
    if os.path.islink(path) or not os.path.isfile(path):
        return False
    absolute = os.path.abspath(path)
    resolved = os.path.realpath(path)
    for root in roots:
        boundary = os.path.abspath(root) + os.sep
        if absolute.startswith(boundary) and resolved.startswith(boundary):
            return True
    return False


def remove(proc_dir: str, proc_ids: List[str],
           artifact_roots: Optional[List[str]] = None,
           protected_qids: Optional[List[str]] = None,
           job_dir_name: str = JOB_DIR_NAME) -> int:
    """
    Remove inactive records and their unshared, owned log files.

    :param proc_dir: str, the registry directory
    :param proc_ids: list of str, the process ids
    :param artifact_roots: Additional trusted log directories, or None.
    :param protected_qids: Retained work-item ids, None preserves scripts.
    :param job_dir_name: str, the gui job log directory name (next to the
                         registry) - always a trusted log directory

    :return: int, the number of records removed
    """
    roots = [os.path.join(os.path.dirname(proc_dir), job_dir_name)]
    roots.extend(artifact_roots or [])
    records = load_all(proc_dir)
    jobs = [job for record in records
            for job in record.get('slurm_jobs') or []]
    slurm = slurm_states(jobs) if jobs else None
    targets = set(proc_ids)
    selected = []
    for record in records:
        if record['id'] not in targets:
            continue
        if proc_status(record, slurm) in ['running', 'pending', 'unknown']:
            continue
        selected.append(record)
    removed = 0
    deleted = []
    for record in selected:
        path = _proc_path(proc_dir, record['id'])
        if path is None:
            continue
        try:
            os.remove(path)
        except OSError:
            continue
        deleted.append(record)
        removed += 1
    retained = load_all(proc_dir)
    protected = {os.path.realpath(path) for record in retained
                 for path in log_files(record)
                 + list(record.get('artifact_paths') or [])}
    held = set(protected_qids or [])
    held.update(qid for record in retained for qid in record.get('qids') or [])
    for record in deleted:
        paths = log_files(record)
        known_items = protected_qids is not None
        shared_tasks = held.intersection(record.get('qids') or [])
        if known_items and not shared_tasks:
            paths += list(record.get('artifact_paths') or [])
        for path in paths:
            if os.path.realpath(path) in protected:
                continue
            if owned_file(path, roots):
                try:
                    os.remove(path)
                except OSError:
                    continue
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


def slurm_job_details() -> Dict[str, Any]:
    """Return useful live Slurm details for the current user's jobs.

    :return: Mapping with availability, user, jobs, and optional error.
    """
    if shutil.which('squeue') is None:
        return dict(available=False, user=getpass.getuser(), jobs=[],
                    error='squeue is not available')
    now = time.time()
    if now - _SLURM_DETAILS_CACHE['time'] < SQUEUE_CACHE_SECONDS:
        cached = _SLURM_DETAILS_CACHE.get('value')
        if isinstance(cached, dict):
            return cached
    fields = [
        ('job_id', '%i'),
        ('name', '%j'),
        ('state', '%T'),
        ('partition', '%P'),
        ('reason', '%r'),
        ('elapsed', '%M'),
        ('time_limit', '%l'),
        ('time_left', '%L'),
        ('nodes', '%D'),
        ('cpus', '%C'),
        ('memory', '%m'),
        ('submit_time', '%V'),
        ('start_time', '%S'),
        ('node_list', '%R'),
        ('dependency', '%E'),
    ]
    command = [
        'squeue',
        '-h',
        '-u',
        getpass.getuser(),
        '-o',
        '|'.join(field[1] for field in fields),
    ]
    try:
        output = subprocess.run(command, capture_output=True, text=True,
                                timeout=15)
    except (OSError, subprocess.SubprocessError) as error:
        result = dict(available=False, user=getpass.getuser(), jobs=[],
                      error=str(error))
        return result
    if output.returncode != 0:
        result = dict(
            available=False,
            user=getpass.getuser(),
            jobs=[],
            error=(output.stderr or 'squeue failed').strip(),
        )
        return result
    jobs = []
    keys = [field[0] for field in fields]
    for line in output.stdout.splitlines():
        values = line.strip().split('|', len(keys) - 1)
        if len(values) != len(keys):
            continue
        job = dict(zip(keys, values))
        job['base_job_id'] = job['job_id'].split('_')[0]
        jobs.append(job)
    jobs.sort(key=lambda item: item['job_id'])
    result = dict(available=True, user=getpass.getuser(), jobs=jobs,
                  error='')
    _SLURM_DETAILS_CACHE.update(time=now, value=result)
    return result


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
    if record.get('submitting'):
        return 'running'
    jobs = record.get('slurm_jobs') or []
    if len(jobs) > 0:
        if slurm is None:
            return 'unknown'
        states = [slurm[job] for job in jobs if job in slurm]
        if len(states) == 0:
            submitted_at = record.get('slurm_submitted_at')
            try:
                recent = (submitted_at is not None and
                          time.time() - float(submitted_at) <
                          SLURM_START_GRACE)
            except (TypeError, ValueError):
                recent = False
            if recent:
                return 'pending'
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
# Define stop functions
# =============================================================================
def kill_pid(pid: int) -> bool:
    """
    Try to terminate one pid cleanly then force kill if needed

    Gui jobs are started in their own session, so when the pid leads a
    process group the whole group is signalled (the command and any
    children it started, e.g. multiprocessing workers)

    :param pid: int, process id

    :return: bool, True if process is gone after kill attempts
    """
    # process already gone counts as success
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    # signal the whole process group if the pid leads one
    try:
        group = os.getpgid(pid) == pid
    except ProcessLookupError:
        return True

    def _signal(sig: int) -> Optional[bool]:
        """
        Signal the process (or its group)

        :param sig: int, the signal to send

        :return: True if already gone, False if not permitted, None if sent
        """
        try:
            if group:
                os.killpg(pid, sig)
            else:
                os.kill(pid, sig)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        return None

    def _wait_gone(n_checks: int) -> Optional[bool]:
        """
        Poll (every 0.1 s) whether the process has exited

        :param n_checks: int, the number of polls

        :return: True if gone, False if not permitted, None if still alive
        """
        for _ in range(n_checks):
            time.sleep(0.1)
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return True
            except PermissionError:
                return False
        return None

    # send TERM first and allow a short grace period, then escalate to KILL
    for sig, n_checks in [(signal.SIGTERM, 20), (signal.SIGKILL, 20)]:
        result = _signal(sig)
        if result is not None:
            return result
        result = _wait_gone(n_checks)
        if result is not None:
            return result
    return False


def stop_process(proc_dir: str, record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stop one registered process: scancel for Slurm jobs, TERM then KILL
    (whole process group) for local processes. The record is marked as
    finished (stopped) on success.

    Applications with extra clean up (e.g. releasing work items a process
    held) should do that around this call.

    :param proc_dir: str, the registry directory
    :param record: dict, the process record (see register)

    :return: dict(success=bool, message=str)
    """
    jobs = record.get('slurm_jobs') or []
    status = proc_status(record, slurm_states(jobs))
    label = '{0} ({1})'.format(record.get('label', ''), record['id'])
    # only active processes can be stopped
    if status not in ['running', 'pending', 'unknown']:
        return dict(success=False,
                    message='{0} is not running ({1})'.format(label, status))
    # -------------------------------------------------------------------------
    # slurm jobs: cancel them
    if len(jobs) > 0:
        if shutil.which('scancel') is None:
            return dict(success=False,
                        message='"scancel" not found on this machine')
        output = subprocess.run(['scancel'] + jobs, capture_output=True,
                                text=True)
        if output.returncode != 0:
            msg = 'scancel failed for {0}: {1}'
            return dict(success=False,
                        message=msg.format(label, output.stderr.strip()))
        finish(proc_dir, record['id'], -15, stopped=True)
        msg = 'Cancelled Slurm job(s) {0} of {1}'
        return dict(success=True, message=msg.format(', '.join(jobs), label))
    # -------------------------------------------------------------------------
    # local processes (only from the machine they run on)
    pid = record.get('pid')
    if pid is None or record.get('host') != socket.gethostname():
        msg = '{0} runs on {1} - it cannot be stopped from here'
        return dict(success=False,
                    message=msg.format(label, record.get('host')))
    # never kill the gui itself
    if int(pid) == os.getpid():
        return dict(success=False, message='refusing to stop this GUI')
    if not kill_pid(int(pid)):
        return dict(success=False,
                    message='could not stop {0} (pid {1})'.format(label, pid))
    finish(proc_dir, record['id'], -15, stopped=True)
    return dict(success=True, message='Stopped {0}'.format(label))


# =============================================================================
# End of code
# =============================================================================
