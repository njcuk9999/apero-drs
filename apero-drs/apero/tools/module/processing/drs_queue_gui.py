#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO processing queue GUI functionality

Provides a browser based dashboard for the APERO processing queue
(apero_queue.py gui). The dashboard shows the queue status (coloured by
state, filterable, sortable, paginated) and has action buttons to run
the next task(s), create/submit batch scripts, reset the queue and edit
the batch template settings.

The module is split into three layers so it can be reused elsewhere
(e.g. pushed through flask in apero_ri in the future):

    1. content functions: return plain (JSON-able) dictionaries or html
       strings (get_status_data, get_template_data, set_template_data,
       render_dashboard)
    2. action functions: perform queue actions and return plain
       dictionaries (action_run, action_batch, action_reset)
    3. server layer: a thin stdlib http.server wrapper that maps routes
       to the content/action functions (queue_gui) - flask can replace
       this layer without touching layers 1 and 2

Created on 2026-08-31

@author: cook
"""
import html as html_mod
import importlib.util
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from aperocore import drs_lang
from apero.base import base as apero_base
from apero.tools.module.processing import drs_queue
from apero.tools.module.processing import drs_queue_procs
from apero.tools.module.processing import drs_queue_stats

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_queue_gui.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry
# get the parameter dictionary
ParamDict = param_functions.ParamDict
# define the default host for the gui server (localhost only for safety)
GUI_DEFAULT_HOST = '127.0.0.1'
# apero_processing options the gui never exposes (queue mode is forced)
GUI_GENERATE_HIDDEN = ['queue_mode']
# the parts apero_reset.py can reset on their own (--only_{part})
GUI_RESET_PARTS = ['assets', 'tmp', 'red', 'calib', 'tellu', 'log', 'plot',
                   'run', 'lbl', 'out', 'other', 'queue']
# directory (inside PATH.OTHER) for generate/reset command output - kept
#    outside the queue and log directories as a reset removes those
GUI_JOB_DIR = 'queue_gui_jobs'
# number of trailing lines of command output sent to the gui
GUI_JOB_TAIL = 400
# regular expression for ANSI colour codes (stripped from activity log text)
ANSI_ESCAPE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
# define the default port for the gui server
GUI_DEFAULT_PORT = 8090
# define the number of ports to try if the default port is taken
GUI_PORT_ATTEMPTS = 50
# define the default number of rows per page in the status table
GUI_DEFAULT_ROWS = 100
# define the maximum number of entries for which we read the yaml files
#    to add detail columns (priority/recipe/runstring) to the table
#    (above this limit reading every yaml would be too slow - 600K+)
GUI_DETAIL_LIMIT = 10000
# define the maximum number of activity log messages kept in memory
GUI_MAX_MESSAGES = 200
# seconds between checks for stale running entries
GUI_STALE_INTERVAL = 30
# define the maximum number of task log bytes sent in one response (the
#    first request for a large log only gets the tail)
GUI_LOG_MAX_BYTES = 5 * 1024 * 1024
# define the fields of the batch template shown in the settings panel
GUI_TEMPLATE_FIELDS = ['time', 'nodes', 'cpus_per_task', 'mem',
                       'account', 'job_name', 'mail_user', 'mail_type']
# define the directory that stores the queue gui static templates
GUI_DIR = os.path.join(os.path.dirname(__file__), 'gui')
# define the dashboard html template path
GUI_TEMPLATE_PATH = os.path.join(GUI_DIR, 'queue_template.html')
# define the Info tab markdown (also included in the ARI apero_queue docs)
GUI_INFO_PATH = os.path.join(GUI_DIR, 'queue_info.md')
# queue id -> detail columns (priority/recipe/runstring) read from yaml
_DETAIL_CACHE: Dict[str, Dict[str, Any]] = dict()
_DETAIL_LOCK = threading.Lock()
# incremental reader + last aggregation of the task statistics
_STATS_READER = drs_queue_stats.StatsReader()
_STATS_CACHE: Dict[str, Any] = dict()
_STATS_LOCK = threading.Lock()
# number of time bins for the performance graphs
GUI_STATS_BINS = 400


def _load_gui_html_template() -> str:
    """
    Load the queue dashboard html template from disk

    :return: str, the html template text
    """
    try:
        with open(GUI_TEMPLATE_PATH, 'r', encoding='utf-8') as hfile:
            return hfile.read()
    except OSError:
        # provide a minimal fallback page if the template is missing
        lines = ['<!DOCTYPE html>', '<html><body>',
                 '<h1>APERO Queue</h1>',
                 '<p>Missing GUI template file:</p>',
                 '<pre>{0}</pre>'.format(GUI_TEMPLATE_PATH),
                 '</body></html>']
        return '\n'.join(lines)


def _markdown_inline(text: str) -> str:
    """
    Convert inline markdown (`code` and **bold**) of escaped text to html

    :param text: str, one line of markdown text

    :return: str, the html for the line
    """
    # escape first so markdown content cannot inject html
    text = html_mod.escape(text, quote=False)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return text


def render_info_html(path: str = GUI_INFO_PATH) -> str:
    """
    Render the Info tab markdown (headings, bullet lists, paragraphs,
    inline code and bold only) to html

    :param path: str, the markdown file to render

    :return: str, the html for the Info tab
    """
    try:
        with open(path, 'r', encoding='utf-8') as mfile:
            lines = mfile.read().splitlines()
    except OSError:
        return '<p>Missing info file: {0}</p>'.format(
            html_mod.escape(path))
    # collect html blocks; a block is a paragraph or a list item
    out: List[str] = []
    block: List[str] = []
    kind = None
    in_list = False

    def _flush():
        if not block:
            return
        text = _markdown_inline(' '.join(block))
        if kind == 'li':
            out.append('<li>{0}</li>'.format(text))
        else:
            out.append('<p>{0}</p>'.format(text))
        block.clear()

    for line in lines:
        stripped = line.strip()
        heading = re.match(r'^(#{1,4})\s+(.*)$', stripped)
        is_item = stripped.startswith('- ')
        # blank lines, headings and new items end the current block
        if not stripped or heading or is_item:
            _flush()
        # leaving a list (anything except an item or its continuation)
        if in_list and (heading or (stripped and not is_item
                                    and not line.startswith(' '))):
            out.append('</ul>')
            in_list = False
        if heading:
            level = len(heading.group(1)) + 1
            out.append('<h{0}>{1}</h{0}>'.format(
                level, _markdown_inline(heading.group(2))))
        elif is_item:
            if not in_list:
                out.append('<ul>')
                in_list = True
            kind = 'li'
            block.append(stripped[2:])
        elif stripped:
            if not block:
                kind = 'li' if in_list else 'p'
            block.append(stripped)
    _flush()
    if in_list:
        out.append('</ul>')
    return '\n'.join(out)


# =============================================================================
# Define classes
# =============================================================================
class GuiState:
    """
    Shared state for the queue gui server

    Holds the busy flag (only one action runs at a time), the activity
    log messages and the worker thread for the current action
    """
    def __init__(self):
        # whether an action is currently running
        self.busy = False
        # the activity log messages (most recent last)
        self.messages: List[str] = []
        # the worker thread for the current action
        self.worker: Optional[threading.Thread] = None
        # set by "stop all running" so an active queue run starts nothing new
        self.cancel = threading.Event()
        # the current/last generate or reset command (see _start_job)
        self.job: Optional[Dict[str, Any]] = None
        # bumped whenever a command may have changed queue/run files so
        #   the browser knows to reload everything
        self.data_version = 0
        # lock protecting the state
        self._lock = threading.Lock()

    def add_message(self, message: str):
        """
        Add a timestamped message to the activity log

        :param message: str, the message to add
        """
        with self._lock:
            # timestamp the message
            stamp = time.strftime('%H:%M:%S')
            self.messages.append('[{0}] {1}'.format(stamp, message))
            # keep the log bounded
            if len(self.messages) > GUI_MAX_MESSAGES:
                self.messages = self.messages[-GUI_MAX_MESSAGES:]

    def start_action(self, name: str, target, args: tuple) -> bool:
        """
        Start an action in a background worker thread (if not busy)

        :param name: str, the name of the action (for the log)
        :param target: callable, the function to run
        :param args: tuple, the arguments to pass to the function

        :return: bool, True if the action was started (False if busy)
        """
        with self._lock:
            # refuse to start if an action is already running
            if self.busy:
                return False
            # mark as busy
            self.busy = True
            self.cancel.clear()

        # define the worker wrapper (clears busy when done)
        def _worker():
            try:
                target(*args)
            except Exception as gui_error:
                emsg = '{0} FAILED: {1}'
                self.add_message(emsg.format(name, gui_error))
            finally:
                with self._lock:
                    self.busy = False
        # start the worker thread
        self.worker = threading.Thread(target=_worker, daemon=True)
        self.worker.start()
        return True


# =============================================================================
# Define content functions (reusable by flask / apero_ri)
# =============================================================================
def get_status_data(params: ParamDict,
                    states: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get the queue status as a plain (JSON-able) dictionary

    Detail columns (priority/recipe/runstring) are only added when the
    number of entries is below GUI_DETAIL_LIMIT (reading every yaml file
    would be too slow for very large queues)

    :param params: ParamDict, the parameter dictionary of constants
    :param states: list of strings or None, only include entries in
                   these states (None means all states)

    :return: dictionary with keys 'queue_path', 'generated', 'counts'
             (state -> count) and 'entries' (list of row dictionaries)
    """
    # gather the queue entries (fast - only lists files)
    entries = drs_queue.list_queue_entries(params, states=states)
    # work out whether we can afford to read the yaml files for details
    details = len(entries) <= GUI_DETAIL_LIMIT
    # -------------------------------------------------------------------------
    # build the table data (list of row dictionaries)
    data = []
    with _DETAIL_LOCK:
        cache = dict(_DETAIL_CACHE)
    for it, entry in enumerate(entries):
        # basic (listing only) information - always present
        row = dict()
        row['idx'] = it
        row['state'] = entry['state']
        row['group'] = entry['group']
        row['run'] = entry['run']
        row['qid'] = '{0}/{1}'.format(entry['group'], entry['run'])
        # detail information (yaml read once per qid - these fields do not
        #   change when a run file moves between states)
        if details:
            if row['qid'] not in cache:
                try:
                    run_dict = base.load_yaml(entry['path'])
                    cache[row['qid']] = dict(
                        priority=run_dict.get('priority', ''),
                        recipe=run_dict.get('recipe', ''),
                        runstring=run_dict.get('runstring', ''))
                except Exception as _:
                    # unreadable (or just moved) yaml - retry next refresh
                    cache[row['qid']] = None
            if cache[row['qid']] is not None:
                row.update(cache[row['qid']])
        # add the row to the table data
        data.append(row)
    # keep the cache bounded to the current queue (failed reads are retried)
    if details:
        current = {row['qid'] for row in data}
        with _DETAIL_LOCK:
            if states is None:
                _DETAIL_CACHE.clear()
            _DETAIL_CACHE.update({qid: value for qid, value in cache.items()
                                  if qid in current and value is not None})
    # -------------------------------------------------------------------------
    # build the counts per state
    counts = dict()
    for state in drs_queue.QUEUE_SUB_DIRS:
        counts[state] = sum(1 for ent in entries
                            if ent['state'] == state)
    # -------------------------------------------------------------------------
    # construct and return the status dictionary
    status = dict()
    status['queue_path'] = drs_queue.get_queue_path(params)
    status['generated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    status['counts'] = counts
    status['entries'] = data
    status['details'] = details
    return status


def _split_qid(qid: str) -> Optional[List[str]]:
    """
    Split and validate a queue id "{group}/{run_file}"

    :param qid: str, the queue id from the client

    :return: list [group, run_file] or None if the qid is not valid (we
             only accept plain queue names so no path can escape the
             queue directory)
    """
    parts = str(qid).split('/')
    if len(parts) != 2:
        return None
    group, run_file = parts
    if not group.startswith('APERO-QUEUE-GROUP-'):
        return None
    if not run_file.startswith('APERO-QUEUE-RUN-'):
        return None
    if not run_file.endswith('.yaml'):
        return None
    for part in parts:
        if '..' in part or '\\' in part or '\x00' in part:
            return None
    return [group, run_file]


def _pid_alive(pid: Any) -> bool:
    """
    Check whether a process id is still alive

    :param pid: Any, the pid (from the run yaml file)

    :return: bool, True if the process exists
    """
    try:
        os.kill(int(pid), 0)
    except (TypeError, ValueError, ProcessLookupError):
        return False
    except PermissionError:
        return True
    return True


def get_task_log(params: ParamDict, qid: str,
                 offset: int = -1) -> Dict[str, Any]:
    """
    Get (part of) the log of one queue task as a plain dictionary

    The log is read from byte "offset" onward. offset < 0 means a first
    read (only the last GUI_LOG_MAX_BYTES are sent for large logs). While
    a task is running only complete lines are sent so the client never
    receives half a line (or half an ANSI colour code).

    :param params: ParamDict, the parameter dictionary of constants
    :param qid: str, the queue id "{group}/{run_file}"
    :param offset: int, the byte offset to read from (-1 = first read)

    :return: dictionary with keys 'qid', 'state', 'pid', 'pid_host',
             'local', 'alive', 'exists', 'path', 'size', 'start',
             'offset', 'text', 'truncated', 'reset' and 'error'
    """
    out = dict(qid=qid, state=None, pid=None, pid_host=None, local=True,
               alive=False, exists=False, path='', size=0, start=0,
               offset=0, text='', truncated=False, reset=False,
               error=None)
    parts = _split_qid(qid)
    if parts is None:
        out['error'] = 'invalid queue id'
        return out
    group, run_file = parts
    queue_path = drs_queue.get_queue_path(params)
    # -------------------------------------------------------------------------
    # find the current state of the task (and its pid if running)
    for qstate in drs_queue.QUEUE_SUB_DIRS:
        run_path = os.path.join(queue_path, qstate, group, run_file)
        if os.path.exists(run_path):
            out['state'] = qstate
            break
    if out['state'] == drs_queue.QUEUE_RUNNING_DIR:
        try:
            run_dict = base.load_yaml(run_path, default=dict())
            out['pid'] = run_dict.get('pid')
            out['pid_host'] = run_dict.get('pid_host')
        except Exception as _:
            out['pid'] = None
        # a pid from another machine cannot be checked from here
        out['local'] = out['pid_host'] in [None, socket.gethostname()]
        if out['pid'] is not None and out['local']:
            out['alive'] = _pid_alive(out['pid'])
    # -------------------------------------------------------------------------
    # read the requested part of the log
    log_path = drs_queue.get_task_log_path(queue_path, group, run_file)
    growing = out['state'] == drs_queue.QUEUE_RUNNING_DIR
    return _read_log(out, log_path, offset, growing)


def _read_log(out: Dict[str, Any], log_path: str, offset: int,
              growing: bool) -> Dict[str, Any]:
    """
    Read (part of) a log file into a get_task_log style dictionary

    :param out: dict, the response dictionary to fill
    :param log_path: str, the log file path
    :param offset: int, the byte offset to read from (-1 = first read)
    :param growing: bool, True while the log is still being written (only
                    complete lines are sent)

    :return: dict, the filled response dictionary
    """
    out['path'] = log_path
    if not os.path.exists(log_path):
        return out
    out['exists'] = True
    size = os.path.getsize(log_path)
    out['size'] = size
    # the log was rewritten (e.g. task re-run) - start again
    if offset > size:
        out['reset'] = True
        offset = -1
    if offset < 0:
        start = max(0, size - GUI_LOG_MAX_BYTES)
        out['truncated'] = start > 0
    else:
        start = offset
    end = min(size, start + GUI_LOG_MAX_BYTES)
    with open(log_path, 'rb') as logfile:
        logfile.seek(start)
        data = logfile.read(end - start)
    # a truncated first read starts at the next full line
    if out['truncated']:
        cut = data.find(b'\n')
        if cut >= 0:
            data = data[cut + 1:]
            start = start + cut + 1
    # while running only send complete lines (rest comes next poll)
    if growing:
        cut = data.rfind(b'\n')
        data = data[:cut + 1] if cut >= 0 else b''
    out['start'] = start
    out['offset'] = start + len(data)
    out['text'] = data.decode('utf-8', errors='replace')
    return out


# =============================================================================
# Define statistics functions (reusable by flask / apero_ri)
# =============================================================================
def _bin_samples(samples: List[Dict[str, Any]], t0: float,
                 width: float, nbins: int) -> Dict[str, Any]:
    """
    Bin resource samples onto a common time grid

    Each task contributes its mean value per bin, so the per-type series
    are totals over the tasks running in that bin (they can be summed
    across types).

    :param samples: list of dict, the samples (drs_queue_stats)
    :param t0: float, the unix time of the first bin
    :param width: float, the bin width in seconds
    :param nbins: int, the number of bins

    :return: dict(types=type -> metric -> list, hosts=host -> metric -> list)
    """
    metrics = ['rss_mb', 'cpu', 'read_mb_s', 'write_mb_s']
    # (bin, qid) -> [shortname, count, sums...]
    per_task = dict()
    # (bin, host) -> [count, load sum, load n, mem sum, mem n]
    per_host = dict()
    for sample in samples:
        b_it = int((sample['t'] - t0) // width)
        if not 0 <= b_it < nbins:
            continue
        key = (b_it, sample['qid'])
        if key not in per_task:
            per_task[key] = [sample['shortname'], 0] + [0.0] * len(metrics)
        acc = per_task[key]
        acc[1] += 1
        for m_it, metric in enumerate(metrics):
            acc[2 + m_it] += sample.get(metric) or 0.0
        hkey = (b_it, sample.get('host', ''))
        hacc = per_host.setdefault(hkey, [0.0, 0, 0.0, 0])
        if sample.get('load1') is not None:
            hacc[0] += sample['load1']
            hacc[1] += 1
        if sample.get('mem_avail_mb') is not None:
            hacc[2] += sample['mem_avail_mb']
            hacc[3] += 1
    types = dict()
    for (b_it, _), acc in per_task.items():
        series = types.setdefault(acc[0], dict(
            ntasks=[0] * nbins, **{m: [0.0] * nbins for m in metrics}))
        series['ntasks'][b_it] += 1
        for m_it, metric in enumerate(metrics):
            series[metric][b_it] += acc[2 + m_it] / acc[1]
    for series in types.values():
        for metric in metrics:
            series[metric] = [round(value, 2) for value in series[metric]]
    hosts = dict()
    for (b_it, host), hacc in per_host.items():
        series = hosts.setdefault(host, dict(load1=[None] * nbins,
                                             mem_avail_mb=[None] * nbins))
        if hacc[1] > 0:
            series['load1'][b_it] = round(hacc[0] / hacc[1], 2)
        if hacc[3] > 0:
            series['mem_avail_mb'][b_it] = round(hacc[2] / hacc[3])
    return dict(types=types, hosts=hosts)


def get_stats_data(params: ParamDict) -> Dict[str, Any]:
    """
    Get the queue task statistics (timing per task + binned RAM/CPU/IO
    series) as a plain (JSON-able) dictionary

    :param params: ParamDict, the parameter dictionary of constants

    :return: dict(tasks=column dict, perf=binned series, ...)
    """
    stats_dir = drs_queue.get_stats_dir(drs_queue.get_queue_path(params))
    _STATS_READER.update(stats_dir)
    with _STATS_READER.lock:
        tasks = list(_STATS_READER.tasks)
        samples = list(_STATS_READER.samples)
    key = (stats_dir, len(tasks), len(samples))
    with _STATS_LOCK:
        if _STATS_CACHE.get('key') == key:
            return _STATS_CACHE['value']
    columns = ['qid', 'shortname', 'recipe', 'mode', 'host', 'start', 'end',
               'duration', 'success', 'peak_rss_mb', 'cpu_s', 'read_mb',
               'write_mb']
    out = dict(stats_dir=stats_dir, n_tasks=len(tasks),
               n_samples=len(samples),
               interval=drs_queue_stats.SAMPLE_INTERVAL,
               tasks={col: [task.get(col) for task in tasks]
                      for col in columns},
               perf=None)
    times = [task['start'] for task in tasks] + [task['end']
                                                  for task in tasks]
    times += [sample['t'] for sample in samples]
    if len(samples) > 0:
        t0, t1 = min(times), max(times)
        width = max(drs_queue_stats.SAMPLE_INTERVAL,
                    (t1 - t0) / GUI_STATS_BINS)
        nbins = int((t1 - t0) // width) + 1
        perf = _bin_samples(samples, t0, width, nbins)
        perf.update(t0=t0, width=width, nbins=nbins)
        out['perf'] = perf
    with _STATS_LOCK:
        _STATS_CACHE.update(key=key, value=out)
    return out


# =============================================================================
# Define process functions (reusable by flask / apero_ri)
# =============================================================================
def get_process_data(params: ParamDict) -> Dict[str, Any]:
    """
    Get the registered processes (generate/reset/run/batch/chain) with
    their live status as a plain (JSON-able) dictionary

    :param params: ParamDict, the parameter dictionary of constants

    :return: dict(processes=list of dicts, slurm=bool)
    """
    records = drs_queue_procs.load_all(drs_queue.get_proc_dir(params))
    jobs = [job for rec in records if not rec.get('finished')
            for job in rec.get('slurm_jobs') or []]
    slurm = drs_queue_procs.slurm_states(jobs)
    queue_path = drs_queue.get_queue_path(params)
    rows = []
    for record in records:
        row = dict(record)
        row['status'] = drs_queue_procs.proc_status(record, slurm)
        row['logs'] = [os.path.basename(path)
                       for path in drs_queue_procs.log_files(record)]
        qids = record.get('qids') or []
        # only the tasks still running are interesting (open their logs)
        running_dir = os.path.join(queue_path, drs_queue.QUEUE_RUNNING_DIR)
        row['running_qids'] = []
        for qid in qids:
            if _split_qid(qid) is None:
                continue
            if os.path.exists(os.path.join(running_dir, qid)):
                row['running_qids'].append(qid)
        row['n_qids'] = len(qids)
        del row['qids']
        rows.append(row)
    return dict(processes=rows, slurm=slurm is not None,
                host=socket.gethostname())


def get_process_log(params: ParamDict, proc_id: str, index: int = 0,
                    offset: int = -1) -> Dict[str, Any]:
    """
    Get (part of) one log file of a registered process (same format as
    get_task_log so the log viewer can follow it)

    :param params: ParamDict, the parameter dictionary of constants
    :param proc_id: str, the process id
    :param index: int, which of the process log files to read
    :param offset: int, the byte offset to read from (-1 = first read)

    :return: dict, see get_task_log
    """
    out = dict(qid=proc_id, state=None, pid=None, pid_host=None,
               local=True, alive=False, exists=False, path='', size=0,
               start=0, offset=0, text='', truncated=False, reset=False,
               error=None)
    record = drs_queue_procs.load(drs_queue.get_proc_dir(params), proc_id)
    if record is None:
        out['error'] = 'unknown process'
        return out
    jobs = record.get('slurm_jobs') or []
    status = drs_queue_procs.proc_status(
        record, drs_queue_procs.slurm_states(jobs))
    growing = status in ['running', 'pending', 'unknown']
    # map onto the log viewer states (running keeps it polling)
    out['state'] = 'running' if growing else (
        'complete' if status in ['complete', 'finished'] else 'failed')
    out['pid'] = record.get('pid')
    out['pid_host'] = record.get('host')
    out['local'] = record.get('host') == socket.gethostname()
    out['alive'] = status == 'running'
    paths = drs_queue_procs.log_files(record)
    if not 0 <= index < len(paths):
        out['path'] = '(no log file yet)'
        return out
    return _read_log(out, paths[index], offset, growing)


def action_process(params: ParamDict, state: GuiState, op: str,
                   ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Stop processes or tidy the process list

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (cancel event/log)
    :param op: str, 'stop' (ids), 'remove' (ids), 'clear_finished' or
               'clear_all' (records only - nothing is stopped)
    :param ids: list of str or None, the process ids

    :return: dict(success, message)
    """
    proc_dir = drs_queue.get_proc_dir(params)
    ids = [str(proc_id) for proc_id in (ids or [])]
    if op == 'stop':
        messages, success = [], True
        for proc_id in ids:
            record = drs_queue_procs.load(proc_dir, proc_id)
            if record is None:
                messages.append('unknown process {0}'.format(proc_id))
                success = False
                continue
            result = drs_queue.stop_process(params, record,
                                            cancel=state.cancel)
            success = success and result['success']
            messages.append(result['message'])
            state.add_message(result['message'])
        state.data_version += 1
        return dict(success=success, message='\n'.join(messages))
    if op in ['remove', 'clear_finished', 'clear_all']:
        if op == 'remove':
            targets = ids
        else:
            data = get_process_data(params)['processes']
            active = ['running', 'pending', 'unknown']
            targets = [row['id'] for row in data
                       if op == 'clear_all' or row['status'] not in active]
        removed = drs_queue_procs.remove(proc_dir, targets)
        message = 'Removed {0} process record(s)'.format(removed)
        state.add_message(message)
        return dict(success=True, message=message)
    return dict(success=False, message='unknown process action: ' + str(op))


def list_template_names(params: ParamDict) -> List[str]:
    """
    List the names of all saved batch templates

    :param params: ParamDict, the parameter dictionary of constants

    :return: list of strings, the available template names
    """
    return drs_queue.list_templates(params)


def get_template_data(params: ParamDict,
                     name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a named batch template as a plain (JSON-able) dictionary

    :param params: ParamDict, the parameter dictionary of constants
    :param name: str or None, the template name (default template used
                if None/blank)

    :return: dictionary, the batch template values (defaults if no
             template file exists yet)
    """
    template = drs_queue.load_template(params, name)
    return dict(template)


def set_template_data(params: ParamDict, form: Dict[str, Any],
                     name: Optional[str] = None) -> Dict[str, Any]:
    """
    Save a named batch template from a plain dictionary (e.g. a
    gui/flask form)

    :param params: ParamDict, the parameter dictionary of constants
    :param form: dictionary, the template values to save (only known
                 template keys are used)
    :param name: str or None, the template name (default template used
                if None/blank)

    :return: dictionary with keys 'template' (the saved values) and
             'path' (the absolute path it was saved to)
    """
    # make sure the queue directories exist
    drs_queue.setup_queue_directories(params)
    drs_queue.setup_output_directories(params)
    # start from the current named template (or defaults)
    template = get_template_data(params, name)
    # update the simple fields from the form
    for key in GUI_TEMPLATE_FIELDS:
        if key in form:
            template[key] = str(form[key])
    # update the activation lines from the form
    if 'activation' in form:
        activation = form['activation']
        # accept both a list of lines and a newline separated string
        if isinstance(activation, str):
            activation = activation.splitlines()
        template['activation'] = [str(line).strip()
                                  for line in activation
                                  if str(line).strip() != '']
    # save the named template
    template_path = drs_queue.save_template(params, template, name)
    # return the saved template and where it was saved
    return dict(template=template, path=template_path)


def render_dashboard(params: ParamDict,
                     rows: int = GUI_DEFAULT_ROWS) -> str:
    """
    Render the queue dashboard html page

    :param params: ParamDict, the parameter dictionary of constants
    :param rows: int, the number of rows per page in the status table

    :return: str, the dashboard html
    """
    # fill the html template (tokens instead of format - css/js braces)
    #   re-read so a page reload picks up template edits
    html = _load_gui_html_template()
    html = html.replace('XX_QPATH_XX',
                        drs_queue.get_queue_path(params))
    html = html.replace('XX_ROWS_XX', str(rows))
    html = html.replace('XX_TPLFIELDS_XX',
                        json.dumps(GUI_TEMPLATE_FIELDS))
    html = html.replace('XX_MPMODE_XX',
                        json.dumps(drs_queue.get_queue_mpmode(params)))
    html = html.replace('XX_INFO_XX', render_info_html())
    # return the rendered html
    return html


# =============================================================================
# Define action functions (reusable by flask / apero_ri)
# =============================================================================
def action_run(params: ParamDict, state: GuiState,
               cores: Optional[Any] = None,
               mpmode: Optional[str] = None,
               ntasks: Optional[Any] = None) -> Dict[str, Any]:
    """
    Start a queue run action in the background (run the next task(s) in
    the queue - see drs_queue.queue_run)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param cores: int/str or None, the number of tasks to run at once
    :param mpmode: str or None, the multiprocessing mode
    :param ntasks: int/str or None, total number of tasks to run in this
                   action (or "all")

    :return: dictionary with keys 'started' (bool) and 'message' (str)
    """
    # sanitize the cores value
    try:
        cores = max(1, int(cores))
    except (TypeError, ValueError):
        cores = 1
    # sanitize the mpmode value (default from TOOLS.REPROCESS.MP_TYPE)
    if mpmode not in drs_queue.QUEUE_MP_MODES:
        mpmode = drs_queue.get_queue_mpmode(params)
    # sanitize ntasks text from the form
    if ntasks is None:
        ntasks = ''
    ntasks = str(ntasks).strip()
    if len(ntasks) == 0:
        ntasks = None

    # define the run action (executed in the worker thread)
    def _do_run():
        state.add_message('Run started (cores={0}, mpmode={1}, '
                          'ntasks={2})'.format(cores, mpmode, ntasks))
        summary = drs_queue.queue_run(params, cores=cores,
                                      mpmode=mpmode,
                                      ntasks=ntasks,
                                      progress=state.add_message,
                                      cancel=state.cancel, owner='gui')
        state.add_message('Run: {0}'.format(summary['message']))
    # start the action in the background (if not busy)
    started = state.start_action('Run', _do_run, tuple())
    # construct the response
    if started:
        return dict(started=True, message='run started')
    return dict(started=False, message='busy - action already running')


def action_batch(params: ParamDict, state: GuiState,
                 per_batch: Optional[Any] = None,
                 n_batches: Optional[Any] = None,
                 submit: bool = False,
                 dry_run: bool = False,
                 template_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a queue batch action in the background (create and optionally
    submit sbatch scripts - see drs_queue.batch_queue)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param per_batch: int/str or None, the number of tasks per batch
                      script (None uses the template cpus_per_task)
    :param n_batches: int/str or None, the number of batch scripts
                      (None means as many as needed)
    :param submit: bool, if True submit the scripts via sbatch
    :param dry_run: bool, if True print commands instead of executing
    :param template_name: str or None, the named batch template to use
                          (default template used if None/blank)

    :return: dictionary with keys 'started' (bool) and 'message' (str)
    """
    # work out the template name up front (used for the cpus fallback
    #   below and passed through to batch_queue)
    template_name = drs_queue.sanitize_template_name(template_name)
    # sanitize the per_batch value (fall back to template cpus)
    try:
        per_batch = max(1, int(per_batch))
    except (TypeError, ValueError):
        template = get_template_data(params, template_name)
        try:
            per_batch = max(1, int(template['cpus_per_task']))
        except (TypeError, ValueError):
            per_batch = 1
    # sanitize the n_batches value (None means as many as needed)
    try:
        n_batches = max(1, int(n_batches))
    except (TypeError, ValueError):
        n_batches = None
    # sanitize the submit value
    submit = bool(submit)
    # sanitize the dry-run value
    dry_run = bool(dry_run)

    # define the batch action (executed in the worker thread)
    def _do_batch():
        state.add_message('Batch started (template={0}, per_batch={1}, '
                          'n_batches={2}, submit={3}, dry_run={4})'
                          ''.format(template_name, per_batch,
                                    n_batches, submit, dry_run))
        summary = drs_queue.batch_queue(params, per_batch, n_batches,
                                        submit, template_name,
                                        dry_run=dry_run)
        state.add_message('Batch: {0}'.format(summary['message']))
        scripts = summary.get('scripts', [])
        if len(scripts) > 0:
            out_dir = os.path.dirname(str(scripts[0]))
            state.add_message('Batch scripts path:\n{0}'.format(out_dir))
    # start the action in the background (if not busy)
    started = state.start_action('Batch', _do_batch, tuple())
    # construct the response
    if started:
        return dict(started=True, message='batch started')
    return dict(started=False, message='busy - action already running')


def action_chain(params: ParamDict, state: GuiState,
                 per_batch: Optional[Any] = None,
                 submit: bool = False,
                 dry_run: bool = False,
                 template_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a queue chain action in the background

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param per_batch: int/str or None, queue runs per array task
    :param submit: bool, if True submit generated chain script
    :param dry_run: bool, if True print commands instead of executing
    :param template_name: str or None, named batch template to use

    :return: dictionary with keys 'started' (bool) and 'message' (str)
    """
    template_name = drs_queue.sanitize_template_name(template_name)
    try:
        per_batch = max(1, int(per_batch))
    except (TypeError, ValueError):
        per_batch = None
    submit = bool(submit)
    dry_run = bool(dry_run)

    def _do_chain():
        state.add_message('Chain started (template={0}, per_batch={1}, '
                          'submit={2}, dry_run={3})'.format(
                              template_name, per_batch, submit, dry_run))
        summary = drs_queue.chain_queue(params, template_name,
                                        submit=submit,
                                        per_batch=per_batch,
                                        dry_run=dry_run)
        state.add_message('Chain: {0}'.format(summary['message']))
        chain_dir = summary.get('chain_dir')
        if chain_dir is not None:
            state.add_message('Chain output path:\n{0}'.format(chain_dir))
        submit_script = summary.get('submit_script')
        if submit_script is not None:
            state.add_message('Chain submit script:\n{0}'
                              ''.format(submit_script))

    started = state.start_action('Chain', _do_chain, tuple())
    if started:
        return dict(started=True, message='chain started')
    return dict(started=False, message='busy - action already running')


def action_reset(params: ParamDict, state: GuiState,
                 qstate: str = 'all',
                 dry_run: bool = False) -> Dict[str, Any]:
    """
    Reset the queue (synchronous - reset is fast). Confirmation must be
    done by the caller (e.g. a browser confirm dialog)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param qstate: str, the queue state to reset ('all' or one of
                   pending/running/complete/failed)
    :param dry_run: bool, if True only report what would be removed

    :return: dictionary with keys 'removed' (int) and 'message' (str)
    """
    # refuse to reset while an action is running
    if state.busy:
        return dict(removed=0,
                    message='busy - action already running')
    # work out the states to reset
    if qstate in drs_queue.QUEUE_SUB_DIRS:
        states = [qstate]
    else:
        states = list(drs_queue.QUEUE_SUB_DIRS)
    # do the reset (non-interactive core)
    n_removed = drs_queue.reset_queue(params, states, dry_run=dry_run)
    # log the reset in the activity log
    if dry_run:
        message = 'Reset dry-run: would remove {0} entries from {1}'
    else:
        message = 'Reset: removed {0} entries from {1}'
    message = message.format(n_removed, ', '.join(states))
    state.add_message(message)
    # construct the response
    return dict(removed=n_removed, message=message)


def action_queue(params: ParamDict, state: GuiState,
                 qaction: Optional[str] = None,
                 qid: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a queue action (move/retry/stop/clear) synchronously

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param qaction: str or None, queue action name
    :param qid: str or None, optional queue id (group/run file)

    :return: dictionary, action result summary
    """
    # normalize inputs
    qaction = str(qaction or '').strip().lower()
    qid = str(qid or '').strip()
    if len(qid) == 0:
        qid = None
    # do not mix with a running background action except stop requests
    stop_actions = ['stop_all_running', 'stop_to_pending',
                    'stop_to_complete', 'stop_to_failed',
                    'fail_stale_running']
    if state.busy and qaction not in stop_actions:
        return dict(success=False, moved=0, stopped=0, failed=0,
                    message='busy - action already running')
    # stop the active queue run first so it cannot claim new tasks
    if qaction == 'stop_all_running':
        state.cancel.set()
    # run action core
    result = drs_queue.queue_action_core(params, qaction, qid)
    # log it for the activity panel
    state.add_message(result['message'])
    # return action result
    return result


# =============================================================================
# Define generate / reset functions (reusable by flask / apero_ri)
# =============================================================================
def _script_path(module: str) -> str:
    """
    Get the file path of an apero tool recipe (without importing it)

    :param module: str, the recipe module name e.g. 'apero_processing'

    :return: str, the absolute path to the recipe script
    """
    spec = importlib.util.find_spec('apero.tools.recipes.bin.' + module)
    return str(spec.origin)


def list_runfiles(params: ParamDict) -> List[str]:
    """
    List the yaml run files in the run directory (PATH.RUN)

    :param params: ParamDict, the parameter dictionary of constants

    :return: list of strings, the run file names (sorted)
    """
    run_dir = str(params['PATH.RUN'])
    if not os.path.isdir(run_dir):
        return []
    return sorted(name for name in os.listdir(run_dir)
                  if name.endswith('.yaml') and not name.startswith('.'))


def _parse_runfile_text(lines: List[str],
                        values: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split a run yaml file into its commented sections for display

    Sections are the "# ----- / # Title / # -----" blocks of the run file
    templates; the comment lines just above a key describe that key and
    the comments of nested keys (e.g. RUN_RECIPES) are kept per entry

    :param lines: list of strings, the raw run file lines
    :param values: dict, the loaded yaml values

    :return: list of sections, each dict(name, items) where every item is
             dict(key, value, comment, children)
    """
    separator = re.compile(r'^#\s*[-=]{5,}\s*$')
    top_key = re.compile(r'^([A-Za-z_]\w*)\s*:')
    sub_key = re.compile(r'^\s+([A-Za-z_]\w*)\s*:[^#]*(?:#\s*(.*))?$')
    sections = []
    current = dict(name='General', items=[], description='')
    header, pending = [], []
    in_header = False
    item = None
    sub_group = ''
    for line in lines:
        text = line.strip()
        if separator.match(text):
            if in_header:
                if len(current['items']) > 0:
                    sections.append(current)
                name = header[0] if len(header) > 0 else 'General'
                current = dict(name=name, items=[],
                               description=' '.join(header[1:]))
            in_header = not in_header
            header, pending, item = [], [], None
            continue
        if in_header and (text.startswith('#') or text == ''):
            if text.lstrip('#').strip():
                header.append(text.lstrip('#').strip())
            continue
        in_header = False
        # indented lines belong to the last top level key (e.g. RUN_RECIPES)
        if line[:1] in [' ', '\t'] and item is not None:
            if text.startswith('#'):
                sub_group = text.lstrip('#').strip()
                continue
            match = sub_key.match(line)
            if match and isinstance(item['value'], dict):
                key = match.group(1)
                item['children'].append(dict(
                    key=key, value=item['value'].get(key),
                    comment=(match.group(2) or '').strip(),
                    group=sub_group))
            continue
        if text.startswith('#'):
            pending.append(text.lstrip('#').strip())
            continue
        if text == '':
            pending = []
            continue
        match = top_key.match(line)
        if match:
            key = match.group(1)
            item = dict(key=key, value=values.get(key),
                        comment=' '.join(pending), children=[])
            current['items'].append(item)
            pending, sub_group = [], ''
    if len(current['items']) > 0:
        sections.append(current)
    return sections


def get_runfile_data(params: ParamDict, name: str) -> Dict[str, Any]:
    """
    Load one run file (for display in the generate panel)

    :param params: ParamDict, the parameter dictionary of constants
    :param name: str, the run file name (must be in list_runfiles)

    :return: dict(name, path, sections, raw) or dict(error)
    """
    # only names listed in the run directory are accepted (no paths)
    if name not in list_runfiles(params):
        return dict(error='unknown run file: {0}'.format(name))
    path = os.path.join(str(params['PATH.RUN']), name)
    with open(path, 'r') as rfile:
        raw = rfile.read()
    try:
        values = base.load_yaml(path) or dict()
    except Exception as yaml_error:
        return dict(name=name, path=path, raw=raw, sections=[],
                    error='could not parse yaml: {0}'.format(yaml_error))
    sections = _parse_runfile_text(raw.splitlines(), values)
    return dict(name=name, path=path, raw=raw, sections=sections)


def get_processing_options(params: ParamDict) -> List[Dict[str, Any]]:
    """
    Get the apero_processing optional arguments (from its recipe
    definition) that the generate panel exposes

    :param params: ParamDict, the parameter dictionary of constants

    :return: list of dict(name, dtype, default, options, help)
    """
    _ = params
    # deferred imports (only needed by the generate panel)
    from aperocore.constants import load_functions
    from apero.instruments import select
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    recipes = pconst.RECIPEMOD().rd.recipes
    recipe = [rec for rec in recipes if rec.name == 'apero_processing.py'][0]
    options = []
    for name, kwarg in recipe.kwargs.items():
        if name in GUI_GENERATE_HIDDEN:
            continue
        dtype = kwarg.dtype
        dtype = dtype.__name__ if isinstance(dtype, type) else str(dtype)
        # 'options' on plain arguments only holds the metavar name
        choices = None
        if dtype == 'options' and kwarg.options is not None:
            choices = [str(opt) for opt in kwarg.options]
        options.append(dict(name=name, dtype=dtype,
                            default=str(kwarg.default),
                            options=choices,
                            help=str(kwarg.helpstr)))
    return options


def build_generate_command(params: ParamDict, runfile: str,
                           options: Dict[str, Any]) -> List[str]:
    """
    Build the apero_processing command (always in queue mode)

    :param params: ParamDict, the parameter dictionary of constants
    :param runfile: str, the run file name (must be in list_runfiles)
    :param options: dict, option name -> value from the gui form

    :raises ValueError: for an unknown run file, option or option value

    :return: list of strings, the command (no shell)
    """
    if runfile not in list_runfiles(params):
        raise ValueError('unknown run file: {0}'.format(runfile))
    allowed = {opt['name']: opt for opt in get_processing_options(params)}
    cmd = [sys.executable, _script_path('apero_processing'), runfile,
           '--queue_mode']
    for key, value in (options or dict()).items():
        if key not in allowed:
            raise ValueError('unknown apero_processing option: ' + key)
        opt = allowed[key]
        if opt['dtype'] == 'switch':
            if str(value).lower() in ['true', '1', 'yes', 'on']:
                cmd.append('--' + key)
            continue
        value = str(value).strip()
        if value == '':
            continue
        if opt['options'] is not None and value not in opt['options']:
            raise ValueError('invalid value for --{0}: {1}'.format(key,
                                                                  value))
        cmd.append('--{0}={1}'.format(key, value))
    return cmd


def build_reset_command(part: Optional[str]) -> List[str]:
    """
    Build the (non-interactive) apero_reset command

    :param part: str or None, one of GUI_RESET_PARTS or 'all'/None

    :raises ValueError: for an unknown part

    :return: list of strings, the command (no shell)
    """
    cmd = [sys.executable, _script_path('apero_reset'), '--nowarn']
    if part in [None, '', 'all']:
        return cmd
    if part not in GUI_RESET_PARTS:
        raise ValueError('unknown reset part: {0}'.format(part))
    return cmd + ['--only_{0}'.format(part)]


def _display_command(cmd: List[str]) -> str:
    """
    Shell-style string of a command, with the python interpreter and
    script path replaced by the recipe name

    :param cmd: list of strings, the command

    :return: str, the display command
    """
    return shlex.join([os.path.basename(cmd[1])] + cmd[2:])


def _start_job(params: ParamDict, state: GuiState, kind: str,
               cmd: List[str], stdin_text: Optional[str] = None,
               on_done=None) -> Dict[str, Any]:
    """
    Run a command (generate/reset) as the gui background action, with its
    output written to a log file the browser can follow

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state
    :param kind: str, the job name (e.g. 'Generate')
    :param cmd: list of strings, the command (no shell)
    :param stdin_text: str or None, text sent to the command's stdin
    :param on_done: callable or None, called with the return code

    :return: dict(started, message)
    """
    log_dir = os.path.join(str(params['PATH.OTHER']), GUI_JOB_DIR)
    os.makedirs(log_dir, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    log_path = os.path.join(log_dir, '{0}-{1}.log'.format(kind.lower(),
                                                          stamp))
    display = _display_command(cmd)

    def _run():
        state.job = dict(kind=kind, cmd=display, path=log_path,
                         running=True, returncode=None,
                         started=time.strftime('%H:%M:%S'))
        state.add_message('{0} started: {1}'.format(kind, display))
        env = dict(os.environ)
        env['PYTHONUNBUFFERED'] = '1'
        # the command runs from home, so make the apero packages this gui
        #   imported findable whatever the (possibly relative) PYTHONPATH
        pkg_roots = []
        for pkg in ['apero', 'aperocore']:
            spec = importlib.util.find_spec(pkg)
            if spec is not None and spec.origin is not None:
                pkg_roots.append(os.path.dirname(
                    os.path.dirname(os.path.abspath(spec.origin))))
        if env.get('PYTHONPATH'):
            pkg_roots.append(env['PYTHONPATH'])
        env['PYTHONPATH'] = os.pathsep.join(pkg_roots)
        stdin = subprocess.PIPE if stdin_text else subprocess.DEVNULL
        returncode = -1
        proc_id = None
        try:
            with open(log_path, 'w') as logfile:
                # run from home: apero_reset refuses to run inside a
                #   directory it would reset; own session so a stop also
                #   reaches the children (e.g. multiprocessing workers)
                process = subprocess.Popen(cmd, stdout=logfile,
                                           stderr=subprocess.STDOUT,
                                           stdin=stdin, env=env,
                                           cwd=os.path.expanduser('~'),
                                           start_new_session=True)
                rkwargs = dict(cmd=display, pid=process.pid, owner='gui',
                               log_paths=[log_path])
                proc_id = drs_queue_procs.register(
                    drs_queue.get_proc_dir(params), kind.lower(), display,
                    **rkwargs)
                if stdin_text:
                    process.stdin.write(stdin_text.encode())
                    process.stdin.close()
                returncode = process.wait()
        finally:
            state.job['running'] = False
            state.job['returncode'] = returncode
        drs_queue_procs.finish(drs_queue.get_proc_dir(params), proc_id,
                               returncode)
        if returncode == 0:
            state.add_message('{0} finished'.format(kind))
        else:
            tail = '\n'.join(_job_tail(log_path, 10))
            state.add_message('{0} FAILED (exit code {1}):\n{2}'.format(
                kind, returncode, tail))
        if on_done is not None:
            on_done(returncode)
        # anything that changed on disk must be reloaded by the browser
        state.data_version += 1

    started = state.start_action(kind, _run, tuple())
    if started:
        return dict(started=True, message='{0} started'.format(kind))
    return dict(started=False, message='busy - action already running')


def _job_tail(path: str, nlines: int, keep_ansi: bool = False) -> List[str]:
    """
    Get the last lines of a job log

    :param path: str, the job log path
    :param nlines: int, the number of lines to return
    :param keep_ansi: bool, if True keep ANSI colour codes (for the browser
                      to colour), otherwise strip them

    :return: list of strings, the lines
    """
    if not os.path.exists(path):
        return []
    with open(path, 'rb') as logfile:
        logfile.seek(max(0, os.path.getsize(path) - 256 * 1024))
        text = logfile.read().decode('utf-8', errors='replace')
    if not keep_ansi:
        text = ANSI_ESCAPE.sub('', text)
    text = text.replace('\r', '\n')
    return text.splitlines()[-nlines:]


def get_job_data(state: GuiState) -> Dict[str, Any]:
    """
    Get the current/last generate or reset job (with its output tail)

    :param state: GuiState, the shared gui state

    :return: dict, the job (empty if no job has run yet)
    """
    if state.job is None:
        return dict()
    job = dict(state.job)
    job['lines'] = _job_tail(job['path'], GUI_JOB_TAIL, keep_ansi=True)
    return job


def action_generate(params: ParamDict, state: GuiState,
                    runfile: Optional[str] = None,
                    options: Optional[Dict[str, Any]] = None,
                    mode: str = 'static') -> Dict[str, Any]:
    """
    Start apero_processing in queue mode (fills the pending queue)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state
    :param runfile: str, the run file name
    :param options: dict, apero_processing option name -> value
    :param mode: str, 'static' (run file) - 'dynamic' is not available yet

    :return: dict(started, message)
    """
    if mode != 'static':
        return dict(started=False, message='dynamic mode: coming soon')
    try:
        cmd = build_generate_command(params, str(runfile or ''), options)
    except ValueError as value_error:
        return dict(started=False, message=str(value_error))

    def _report(returncode: int):
        pending = drs_queue.list_queue_entries(
            params, states=[drs_queue.QUEUE_PENDING_DIR])
        state.add_message('Queue now has {0} pending task(s)'.format(
            len(pending)))

    return _start_job(params, state, 'Generate', cmd, on_done=_report)


def action_reset_data(params: ParamDict, state: GuiState,
                      part: Optional[str] = None) -> Dict[str, Any]:
    """
    Start apero_reset.py (no confirmation prompts - the browser confirms)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state
    :param part: str or None, 'all' (default) or one of GUI_RESET_PARTS

    :return: dict(started, message)
    """
    try:
        cmd = build_reset_command(part)
    except ValueError as value_error:
        return dict(started=False, message=str(value_error))
    # answers "create missing directory?" questions apero_reset may ask
    return _start_job(params, state, 'Reset', cmd, stdin_text='Y\n' * 100,
                      on_done=lambda _: drs_queue.setup_queue_directories(
                          params))


# =============================================================================
# Define server functions
# =============================================================================
def _stale_watcher(params: ParamDict, state: GuiState):
    """
    Background loop: fail running entries nothing is running any more
    (see drs_queue.find_stale_running)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (activity log)

    :return: None (runs until the gui exits)
    """
    while True:
        try:
            result = drs_queue.fail_stale_running(params)
            if result['moved'] > 0:
                lines = ['{0}: {1}'.format(item['qid'], item['reason'])
                         for item in result['stale']]
                state.add_message('{0}\n{1}'.format(result['message'],
                                                    '\n'.join(lines)))
                state.data_version += 1
        except Exception as stale_error:
            state.add_message('Stale running check failed: {0}'.format(
                stale_error))
        time.sleep(GUI_STALE_INTERVAL)


def _make_handler(params: ParamDict, state: GuiState, rows: int):
    """
    Create the http request handler class for the queue gui server

    The handler routes requests to the content/action functions (which
    are the flask-reusable layer)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param rows: int, the number of rows per page in the status table

    :return: the request handler class
    """
    class QueueGuiHandler(BaseHTTPRequestHandler):
        """Request handler for the queue gui server"""

        def _send(self, content: str, ctype: str = 'application/json',
                  code: int = 200):
            """Send a response with the given content and type"""
            body = content.encode('utf-8')
            # the browser may abandon a request (reload, closed tab)
            try:
                self.send_response(code)
                self.send_header('Content-Type',
                                 '{0}; charset=utf-8'.format(ctype))
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def _read_json(self) -> Dict[str, Any]:
            """Read the request body as a json dictionary"""
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length == 0:
                    return dict()
                return json.loads(self.rfile.read(length))
            except (ValueError, TypeError):
                return dict()

        def log_message(self, fmt, *args):
            """Silence the default request logging"""
            _ = fmt, args

        # pylint: disable=invalid-name
        def do_GET(self):
            """Handle GET requests (dashboard + read-only api)"""
            self._safe(self._get)

        # pylint: disable=invalid-name
        def do_POST(self):
            """Handle POST requests (actions)"""
            self._safe(self._post)

        def _safe(self, handler):
            """Run a handler, returning a json error instead of dropping
            the connection if it raises"""
            try:
                handler()
            except Exception as gui_error:
                emsg = '{0}: {1}'.format(type(gui_error).__name__,
                                         gui_error)
                wargs = [self.path, emsg]
                # warning: Queue GUI request {0} failed: {1}
                WLOG(params, 'warning', textentry('10-513-00003', args=wargs),
                     sublevel=2)
                self._send(json.dumps(dict(error=emsg)), code=500)

        def _get(self):
            """Route GET requests"""
            parsed = urlparse(self.path)
            route = parsed.path
            # the dashboard page
            if route in ['/', '/index.html']:
                self._send(render_dashboard(params, rows),
                           ctype='text/html')
            # the queue status (entries + counts)
            elif route == '/api/status':
                query = parse_qs(parsed.query)
                qstate = query.get('qstate', ['all'])[0]
                if qstate in drs_queue.QUEUE_SUB_DIRS:
                    states = [qstate]
                else:
                    states = None
                data = get_status_data(params, states=states)
                self._send(json.dumps(data))
            # the (incremental) log of one queue task
            elif route == '/api/log':
                query = parse_qs(parsed.query)
                qid = query.get('qid', [''])[0]
                try:
                    offset = int(query.get('offset', ['-1'])[0])
                except (TypeError, ValueError):
                    offset = -1
                data = get_task_log(params, qid, offset)
                self._send(json.dumps(data))
            # the registered processes (generate/reset/run/batch/chain)
            # task timing + binned performance statistics
            elif route == '/api/stats':
                self._send(json.dumps(get_stats_data(params)))
            elif route == '/api/processes':
                self._send(json.dumps(get_process_data(params),
                                      default=str))
            # the (incremental) log of one registered process
            elif route == '/api/process_log':
                query = parse_qs(parsed.query)
                proc_id = query.get('id', [''])[0]
                try:
                    index = int(query.get('file', ['0'])[0])
                    offset = int(query.get('offset', ['-1'])[0])
                except (TypeError, ValueError):
                    index, offset = 0, -1
                data = get_process_log(params, proc_id, index, offset)
                self._send(json.dumps(data))
            # the gui state (busy flag + activity log)
            elif route == '/api/state':
                job = state.job or dict()
                data = dict(busy=state.busy, messages=state.messages,
                            data_version=state.data_version,
                            job_running=bool(job.get('running')),
                            job_kind=job.get('kind'))
                self._send(json.dumps(data))
            # the current/last generate or reset command output
            elif route == '/api/job':
                self._send(json.dumps(get_job_data(state)))
            # the run files that generate can use
            elif route == '/api/runfiles':
                self._send(json.dumps(dict(names=list_runfiles(params))))
            # one run file (sections + raw text)
            elif route == '/api/runfile':
                query = parse_qs(parsed.query)
                name = query.get('name', [''])[0]
                self._send(json.dumps(get_runfile_data(params, name),
                                      default=str))
            # the apero_processing options shown by generate
            elif route == '/api/processing_options':
                data = dict(options=get_processing_options(params),
                            reset_parts=GUI_RESET_PARTS)
                self._send(json.dumps(data))
            # the list of saved batch template names
            elif route == '/api/templates':
                data = dict(names=list_template_names(params))
                self._send(json.dumps(data))
            # the batch template values (optional ?name= query param)
            elif route == '/api/template':
                query = parse_qs(parsed.query)
                name = query.get('name', [None])[0]
                self._send(json.dumps(get_template_data(params, name)))
            # unknown route
            else:
                self._send(json.dumps(dict(error='not found')),
                           code=404)

        def _post(self):
            """Route POST requests"""
            parsed = urlparse(self.path)
            route = parsed.path
            form = self._read_json()
            # run the next task(s)
            if route == '/api/run':
                response = action_run(params, state,
                                      cores=form.get('cores'),
                                      mpmode=form.get('mpmode'),
                                      ntasks=form.get('ntasks'))
                self._send(json.dumps(response))
            # create (and optionally submit) batch scripts
            elif route == '/api/batch':
                response = action_batch(
                    params, state, per_batch=form.get('per_batch'),
                    n_batches=form.get('n_batches'),
                    submit=form.get('submit', False),
                    dry_run=form.get('dry_run', False),
                    template_name=form.get('template'))
                self._send(json.dumps(response))
            # create (and optionally submit) dependency-chained arrays
            elif route == '/api/chain':
                response = action_chain(
                    params, state, per_batch=form.get('per_batch'),
                    submit=form.get('submit', False),
                    dry_run=form.get('dry_run', False),
                    template_name=form.get('template'))
                self._send(json.dumps(response))
            # reset the queue
            elif route == '/api/reset':
                response = action_reset(params, state,
                                        qstate=form.get('qstate',
                                                        'all'),
                                        dry_run=form.get('dry_run',
                                                         False))
                self._send(json.dumps(response))
            # run queue action(s) from the status page
            elif route == '/api/action':
                response = action_queue(params, state,
                                        qaction=form.get('qaction'),
                                        qid=form.get('qid'))
                self._send(json.dumps(response))
            # stop processes / tidy the process list
            elif route == '/api/process':
                ids = form.get('ids') or []
                if not isinstance(ids, list):
                    ids = []
                response = action_process(params, state,
                                          str(form.get('op', '')), ids)
                self._send(json.dumps(response))
            # save the batch template (name defaults to "default")
            elif route == '/api/template':
                name = form.get('name')
                result = set_template_data(params, form, name)
                msg = 'Batch template "{0}" saved to {1}'
                msg = msg.format(drs_queue.sanitize_template_name(name),
                                 result['path'])
                state.add_message(msg)
                response = dict(template=result['template'],
                                path=result['path'], message=msg)
                self._send(json.dumps(response))
            # fill the queue with apero_processing (queue mode)
            elif route == '/api/generate':
                response = action_generate(
                    params, state, runfile=form.get('runfile'),
                    options=form.get('options'),
                    mode=form.get('mode', 'static'))
                self._send(json.dumps(response))
            # reset apero data with apero_reset.py
            elif route == '/api/reset_data':
                response = action_reset_data(params, state,
                                             part=form.get('part'))
                self._send(json.dumps(response))
            # shut down the gui server
            elif route == '/api/shutdown':
                self._send(json.dumps(dict(message='shutting down')))
                # shutdown must run in another thread (shutdown blocks
                #   until the current request is finished)
                threading.Thread(target=self.server.shutdown,
                                 daemon=True).start()
            # unknown route
            else:
                self._send(json.dumps(dict(error='not found')),
                           code=404)

    # return the handler class
    return QueueGuiHandler


def queue_gui(params: ParamDict):
    """
    Gui mode: start the queue dashboard web server and open it in a
    browser

    The dashboard shows the queue status (coloured by state, filterable,
    sortable, paginated) and has action buttons to run the next task(s),
    create/submit batch scripts, reset the queue and edit the batch
    template settings. Stop the server with Ctrl+C or the Shutdown
    button in the dashboard.

    The --host and --port arguments control where the server listens
    (default 127.0.0.1:8090 - localhost only for safety) and --rows sets
    the status table page size.

    :param params: ParamDict, the parameter dictionary of constants

    :return: None
    """
    # make sure the queue directories exist
    drs_queue.setup_queue_directories(params)
    # -------------------------------------------------------------------------
    # get the host from user inputs (default localhost)
    host = GUI_DEFAULT_HOST
    if 'HOST' in params['INPUTS']:
        value = params['INPUTS']['HOST']
        if not drs_text.null_text(value, ['', 'None']):
            host = str(value)
    # get the port from user inputs (default 8090)
    port = GUI_DEFAULT_PORT
    if 'PORT' in params['INPUTS']:
        value = params['INPUTS']['PORT']
        try:
            port = int(value)
        except (TypeError, ValueError):
            port = GUI_DEFAULT_PORT
    # get the rows per page from user inputs (default 100)
    rows = GUI_DEFAULT_ROWS
    if 'ROWS' in params['INPUTS']:
        value = params['INPUTS']['ROWS']
        try:
            rows = max(1, int(value))
        except (TypeError, ValueError):
            rows = GUI_DEFAULT_ROWS
    # -------------------------------------------------------------------------
    # create the shared gui state
    state = GuiState()
    state.add_message('Queue GUI started')
    # periodically fail running entries nothing is running any more
    threading.Thread(target=_stale_watcher, args=(params, state),
                     daemon=True).start()
    # create the request handler class
    handler = _make_handler(params, state, rows)
    # -------------------------------------------------------------------------
    # start the server (try the next ports if the default is taken)
    server = None
    for p_it in range(GUI_PORT_ATTEMPTS):
        try:
            server = ThreadingHTTPServer((host, port + p_it), handler)
            port = port + p_it
            break
        except OSError:
            continue
    # deal with no free port found
    if server is None:
        eargs = [port, port + GUI_PORT_ATTEMPTS]
        # error: Queue: Could not find a free port (tried {0}-{1})
        WLOG(params, 'error', textentry('09-513-00003', args=eargs))
        return
    # -------------------------------------------------------------------------
    # log where the dashboard is
    url = 'http://{0}:{1}/'.format(host, port)
    margs = [url]
    # log: Queue: Dashboard running at {0} (Ctrl+C to stop)
    WLOG(params, 'info', textentry('40-513-00028', args=margs))
    # try to open the dashboard in a browser (ignore failures - e.g. on
    #   a headless machine the user can open the url manually)
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception as _:
        pass
    # -------------------------------------------------------------------------
    # serve until shutdown (Ctrl+C or the dashboard shutdown button)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        # optional interactive stop when Ctrl+C is used from terminal
        if state.busy:
            prompt = ('Queue: Action is running. Stop running tasks and '
                      'move them back to pending? [y/N]: ')
            try:
                user_input = input(prompt).strip().lower()
            except (EOFError, KeyboardInterrupt):
                user_input = ''
            if user_input.startswith('y'):
                state.cancel.set()
                result = drs_queue.queue_action_core(params,
                                                     'stop_all_running')
                if result['success']:
                    WLOG(params, 'info', result['message'])
                else:
                    WLOG(params, 'warning', result['message'],
                         sublevel=2)
            else:
                # log: Queue: Leaving running tasks active
                WLOG(params, '', textentry('40-513-00023'))
    finally:
        server.server_close()
    # if action still running, keep process alive until worker completes
    if state.busy and state.worker is not None:
        # log: Queue: Waiting for active action to finish
        WLOG(params, '', textentry('40-513-00022'))
        state.worker.join()
    # log that the server has stopped
    # log: Queue: Dashboard stopped
    WLOG(params, '', textentry('40-513-00021'))


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================



