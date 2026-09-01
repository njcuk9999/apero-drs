#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO processing queue functionality

Provides the functionality for apero_processing to run in "queue mode",
where instead of processing a run list directly, the run list is grouped
(by what can be run together) and written to a queue directory on disk.

The queue directory contains four sub-directories:
    - pending: groups waiting to be run
    - running: groups currently being run
    - complete: groups that have finished running successfully
    - failed: groups that have finished running with errors

Each group is a sub-directory named:
    APERO-QUEUE-GROUP-{UNIXTIME}-{GROUPNAME}
and contains one yaml file per run item named:
    APERO-QUEUE-RUN-{PRIORITY}.yaml

These names are designed so that a simple alphabetical sort gives the
correct execution order (earliest group first, and within a group the
lowest priority run first). This is required by apero_queue which will
take the "next item" from the queue (and wait until a group is finished
before moving on to the next group).

Created on 2026-08-31

@author: cook
"""
import os
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc
from aperocore.core import drs_text
from apero.base import base as apero_base
from apero.utils import drs_utils

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_queue.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_misc.display_func
# get the parameter dictionary
ParamDict = param_functions.ParamDict
# define the queue sub-directory names (order here defines creation order)
QUEUE_PENDING_DIR = 'pending'
QUEUE_RUNNING_DIR = 'running'
QUEUE_COMPLETE_DIR = 'complete'
QUEUE_FAILED_DIR = 'failed'
QUEUE_SUB_DIRS = [QUEUE_PENDING_DIR, QUEUE_RUNNING_DIR, QUEUE_COMPLETE_DIR,
                  QUEUE_FAILED_DIR]
# define the queue output sub-directories (for batch mode)
QUEUE_OUTPUT_DIR = 'output'
QUEUE_LOGS_DIR = os.path.join(QUEUE_OUTPUT_DIR, 'logs')
QUEUE_ERRORS_DIR = os.path.join(QUEUE_OUTPUT_DIR, 'errors')
QUEUE_SCRIPTS_DIR = os.path.join(QUEUE_OUTPUT_DIR, 'scripts')
# define the queue lock file name (stops multiple apero_queues clashing)
QUEUE_LOCK_FILE = 'apero_queue.lock'
# define the batch template file name (created by apero_queue init)
QUEUE_BATCH_TEMPLATE = 'batch_template.yaml'
# define the queue group directory name format
#    {0} = unix time (zero padded so groups sort alphabetically by time)
#    {1} = group name (zero padded group number + recipe shortname)
QUEUE_GROUP_FORMAT = 'APERO-QUEUE-GROUP-{0}-{1}'
# define the unix time format (zero padded to 11 digits so alphabetical
#    sorting equals chronological sorting)
QUEUE_TIME_FORMAT = '{0:011.0f}'
# define the group name format
#    {0} = group number (zero padded so groups sort alphabetically in the
#          order they were created)
#    {1} = recipe shortname
QUEUE_GROUP_NAME_FORMAT = '{0:04d}-{1}'
# define the queue run item yaml file name format
#    {0} = run priority (zero padded so runs sort alphabetically by
#          priority within a group)
QUEUE_RUN_FORMAT = 'APERO-QUEUE-RUN-{0:08d}.yaml'
# define the queue states
QUEUE_STATE_PENDING = 'pending'
QUEUE_STATE_RUNNING = 'running'
QUEUE_STATE_COMPLETE = 'complete'
QUEUE_STATE_FAILED = 'failed'
# define the log signature that flags a recipe as NOT successful (this is
#    printed by apero recipes at the end of a failed run)
QUEUE_FAIL_SIGNATURE = 'has NOT been successfully completed'
# define the number of status entries to show per page in status mode
QUEUE_STATUS_PAGE_SIZE = 10
# define the valid mp modes for run mode
QUEUE_MP_MODES = ['process', 'pool', 'linear']
# define default batch template values (used as defaults in init mode)
QUEUE_BATCH_DEFAULTS = dict()
QUEUE_BATCH_DEFAULTS['time'] = '48:00:00'
QUEUE_BATCH_DEFAULTS['nodes'] = 1
QUEUE_BATCH_DEFAULTS['cpus_per_task'] = 24
QUEUE_BATCH_DEFAULTS['mem'] = '0'
QUEUE_BATCH_DEFAULTS['account'] = ''
QUEUE_BATCH_DEFAULTS['job_name'] = 'apero_queue'
QUEUE_BATCH_DEFAULTS['mail_user'] = ''
QUEUE_BATCH_DEFAULTS['mail_type'] = 'BEGIN,END,FAIL'
QUEUE_BATCH_DEFAULTS['activation'] = []


# =============================================================================
# Define classes
# =============================================================================
class QueueLockError(Exception):
    """
    Exception raised when the queue lock cannot be acquired
    """
    pass


class QueueLock:
    """
    Simple file based lock for the queue directory

    Stops multiple apero_queue instances claiming the same pending tasks
    at the same time. Used as a context manager:

        with QueueLock(params):
            # claim tasks here

    The lock file contains the PID of the process holding the lock - if
    the lock file exists but the process is dead the lock is considered
    stale and is taken over.
    """
    def __init__(self, params: ParamDict, timeout: float = 60.0,
                 wait: float = 1.0):
        """
        Construct the queue lock

        :param params: ParamDict, the parameter dictionary of constants
        :param timeout: float, the maximum time (in seconds) to wait for
                        the lock before raising QueueLockError
        :param wait: float, the time (in seconds) to wait between lock
                     acquisition attempts
        """
        self.params = params
        self.timeout = timeout
        self.wait = wait
        # construct the lock file path
        self.lockfile = os.path.join(get_queue_path(params),
                                     QUEUE_LOCK_FILE)
        # whether we currently hold the lock
        self.locked = False

    def acquire(self):
        """
        Acquire the queue lock (waits up to self.timeout seconds)

        :raises QueueLockError: if the lock cannot be acquired
        """
        # record the start time (for the timeout)
        start_time = time.time()
        # loop until we acquire the lock or time out
        while True:
            # try to create the lock file exclusively
            try:
                # O_EXCL guarantees this fails if the file exists
                flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                fd = os.open(self.lockfile, flags)
                # write our pid to the lock file
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                # we now hold the lock
                self.locked = True
                return
            except FileExistsError:
                # lock file exists - check for a stale lock
                if self._stale():
                    # remove the stale lock and try again
                    self._remove_lockfile()
                    continue
            # deal with timing out
            if time.time() - start_time > self.timeout:
                emsg = ('Queue: Could not acquire queue lock "{0}" - is '
                        'another apero_queue running? If not remove the '
                        'lock file manually.')
                raise QueueLockError(emsg.format(self.lockfile))
            # wait before trying again
            time.sleep(self.wait)

    def release(self):
        """
        Release the queue lock (if we hold it)
        """
        if self.locked:
            self._remove_lockfile()
            self.locked = False

    def _stale(self) -> bool:
        """
        Check whether the current lock file is stale (owning process dead)

        :return: bool, True if the lock file is stale
        """
        # read the pid from the lock file
        try:
            with open(self.lockfile, 'r') as lfile:
                pid = int(lfile.read().strip())
        except (OSError, ValueError):
            # unreadable lock file - treat as stale
            return True
        # check whether the process is still alive (signal 0 = no signal)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            # process is dead - lock is stale
            return True
        except PermissionError:
            # process exists but is owned by someone else - not stale
            return False
        # process is alive - lock is not stale
        return False

    def _remove_lockfile(self):
        """
        Remove the lock file (ignoring errors if already removed)
        """
        try:
            os.remove(self.lockfile)
        except OSError:
            pass

    def __enter__(self) -> 'QueueLock':
        # acquire the lock on entering the context
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # always release the lock on exiting the context
        self.release()


# =============================================================================
# Define functions
# =============================================================================
def queue_mode_active(params: ParamDict) -> bool:
    """
    Work out whether queue mode is active

    Priority order (highest first):
        1. params['INPUTS']['QUEUE_MODE'] (from the command line, if set)
        2. params['QUEUE_MODE'] (from the run yaml file, if set)
        3. params['QUEUE.MODE'] (from config.py + instrument overrides)

    :param params: ParamDict, the parameter dictionary of constants

    :return: bool, True if queue mode is active
    """
    # start with the config value (default False, instrument overridable)
    queue_mode = drs_text.true_text(params['QUEUE.MODE'])
    # -------------------------------------------------------------------------
    # the run yaml file value (if present) overrides the config value
    if 'QUEUE_MODE' in params:
        # get the run file value
        value = params['QUEUE_MODE']
        # only use non-null values
        if not drs_text.null_text(value, ['', 'None']):
            queue_mode = drs_text.true_text(value)
    # -------------------------------------------------------------------------
    # the command line input (if set) overrides everything else
    if 'INPUTS' in params:
        if 'QUEUE_MODE' in params['INPUTS']:
            # get the command line value
            value = params['INPUTS']['QUEUE_MODE']
            # only use non-null values (default is None)
            if not drs_text.null_text(value, ['', 'None']):
                queue_mode = drs_text.true_text(value)
    # -------------------------------------------------------------------------
    # return whether queue mode is active
    return queue_mode


def get_queue_path(params: ParamDict) -> str:
    """
    Get the queue directory path

    Uses QUEUE.PATH - if a relative path is given the queue directory goes
    inside PATH.OTHER (i.e. PATH.OTHER/{QUEUE.PATH}), if an absolute path
    is given the absolute path is used directly (without the PATH.OTHER
    sub-directory)

    :param params: ParamDict, the parameter dictionary of constants

    :return: str, the absolute path to the queue directory
    """
    # get the queue path from parameters
    queue_path = str(params['QUEUE.PATH'])
    # if we have an absolute path use it directly
    if os.path.isabs(queue_path):
        return queue_path
    # otherwise the queue directory goes inside PATH.OTHER
    return str(os.path.join(params['PATH.OTHER'], queue_path))


def setup_queue_directories(params: ParamDict) -> Dict[str, str]:
    """
    Create the queue directory (and the pending/running/complete
    sub-directories) if they do not exist

    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary of strings, the absolute paths to the queue
             sub-directories (keys: 'pending', 'running', 'complete')
    """
    # get the queue path
    queue_path = get_queue_path(params)
    # make the queue directory if it doesn't exist
    if not os.path.exists(queue_path):
        os.makedirs(queue_path)
    # storage of sub-directory paths
    sub_dirs = dict()
    # loop around the queue sub-directories
    for sub_dir in QUEUE_SUB_DIRS:
        # construct the sub-directory path
        sub_path = os.path.join(queue_path, sub_dir)
        # make the sub-directory if it doesn't exist
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)
        # add to storage
        sub_dirs[sub_dir] = sub_path
    # return the sub-directory paths
    return sub_dirs


def add_run_list_to_queue(params: ParamDict, runlist: List[Any]):
    """
    Add a run list to the queue

    Groups the run list by what can be run together (using
    drs_processing.group_tasks2) and creates one group sub-directory per
    group inside the "pending" queue directory. Each group sub-directory
    contains one yaml file per run item (in that group).

    :param params: ParamDict, the parameter dictionary of constants
    :param runlist: list of Run instances, the run list to add to the queue

    :return: None, writes the queue group directories and run yaml files
    """
    # set function name
    func_name = display_func('add_run_list_to_queue', __NAME__)
    # deferred import: avoids a module level dependency between drs_queue
    #   and drs_processing (drs_processing may need to import drs_queue)
    from apero.tools.module.processing import drs_processing
    # deal with an empty run list (nothing to queue)
    if len(runlist) == 0:
        WLOG(params, 'warning', 'Queue: No runs to add to queue',
             sublevel=2)
        return
    # -------------------------------------------------------------------------
    # make sure queue directories exist (and get their paths)
    sub_dirs = setup_queue_directories(params)
    # get the pending directory (all new groups start as pending)
    pending_dir = sub_dirs[QUEUE_PENDING_DIR]
    # -------------------------------------------------------------------------
    # group the tasks by what can be run together
    grouplist, groupnames = drs_processing.group_tasks2(runlist)
    # get the unix time of queue creation (shared by all groups from this
    #   call so groups created together sort by group number)
    unixtime = QUEUE_TIME_FORMAT.format(time.time())
    # -------------------------------------------------------------------------
    # log progress: adding N groups to the queue
    msg = 'Queue: Adding {0} runs in {1} groups to queue: {2}'
    margs = [len(runlist), len(grouplist), pending_dir]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # loop around groups (in group number order)
    for groupkey in sorted(grouplist.keys()):
        # construct the group name from group number + recipe shortname
        groupname = QUEUE_GROUP_NAME_FORMAT.format(groupkey,
                                                   groupnames[groupkey])
        # construct the group directory name
        group_dirname = QUEUE_GROUP_FORMAT.format(unixtime, groupname)
        # construct the group directory path (groups start in pending)
        group_path = os.path.join(pending_dir, group_dirname)
        # make the group directory if it doesn't exist
        if not os.path.exists(group_path):
            os.makedirs(group_path)
        # ---------------------------------------------------------------------
        # loop around run items in this group
        for run_item in grouplist[groupkey]:
            # convert the run item into a queue dictionary
            queue_dict = _run_item_to_dict(run_item, group_dirname)
            # construct the run yaml file name (sorts by priority)
            run_filename = QUEUE_RUN_FORMAT.format(run_item.priority)
            # construct the run yaml file path
            run_path = os.path.join(group_path, run_filename)
            # write the run yaml file
            base.write_yaml(queue_dict, run_path, width=float('inf'))
        # ---------------------------------------------------------------------
        # log progress: added group with N runs
        msg = 'Queue: \t Added group "{0}" ({1} runs)'
        margs = [group_dirname, len(grouplist[groupkey])]
        WLOG(params, '', msg.format(*margs))


# =============================================================================
# Define queue management functions
# =============================================================================
def setup_output_directories(params: ParamDict) -> Dict[str, str]:
    """
    Create the queue output directories (for batch mode) if they do not
    exist ({QUEUE.PATH}/output/logs, {QUEUE.PATH}/output/errors and
    {QUEUE.PATH}/output/scripts)

    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary of strings, the absolute paths to the output
             sub-directories (keys: 'logs', 'errors', 'scripts')
    """
    # get the queue path
    queue_path = get_queue_path(params)
    # storage of output directory paths
    out_dirs = dict()
    out_dirs['logs'] = os.path.join(queue_path, QUEUE_LOGS_DIR)
    out_dirs['errors'] = os.path.join(queue_path, QUEUE_ERRORS_DIR)
    out_dirs['scripts'] = os.path.join(queue_path, QUEUE_SCRIPTS_DIR)
    # loop around output directories and create them if they don't exist
    for key in out_dirs:
        if not os.path.exists(out_dirs[key]):
            os.makedirs(out_dirs[key])
    # return the output directory paths
    return out_dirs


def list_queue_entries(params: ParamDict,
                       states: Optional[List[str]] = None
                       ) -> List[Dict[str, str]]:
    """
    List all queue entries (run yaml files) across the queue state
    directories

    Note: this only lists files (it does not read the yaml contents) so
    it stays fast even for very large queues (600K+ entries)

    :param params: ParamDict, the parameter dictionary of constants
    :param states: list of strings or None, only list entries in these
                   states (None means all states)

    :return: list of dictionaries with keys 'state', 'group', 'run' and
             'path', sorted by group name then run file name
    """
    # deal with no states given (use all states)
    if states is None:
        states = list(QUEUE_SUB_DIRS)
    # get the queue path
    queue_path = get_queue_path(params)
    # storage for entries
    entries = []
    # loop around requested states
    for state in states:
        # construct the state directory path
        state_path = os.path.join(queue_path, state)
        # skip states that do not exist yet
        if not os.path.isdir(state_path):
            continue
        # loop around group directories in this state
        for group in sorted(os.listdir(state_path)):
            # construct the group directory path
            group_path = os.path.join(state_path, group)
            # skip non-directories and non-queue-group directories
            if not os.path.isdir(group_path):
                continue
            if not group.startswith('APERO-QUEUE-GROUP-'):
                continue
            # loop around run yaml files in this group
            for run_file in sorted(os.listdir(group_path)):
                # skip non-run files
                if not run_file.startswith('APERO-QUEUE-RUN-'):
                    continue
                if not run_file.endswith('.yaml'):
                    continue
                # add the entry to storage
                entry = dict()
                entry['state'] = state
                entry['group'] = group
                entry['run'] = run_file
                entry['path'] = os.path.join(group_path, run_file)
                entries.append(entry)
    # sort entries by group name then run file name (execution order)
    entries.sort(key=lambda ent: (ent['group'], ent['run']))
    # return the entries
    return entries


NextGroupReturn = Tuple[Optional[str], List[str], List[str]]


def get_next_group(params: ParamDict) -> NextGroupReturn:
    """
    Get the next (i.e. earliest unfinished) group in the queue

    A group is unfinished if it has entries in the pending or running
    directories. The next group is the alphabetically first unfinished
    group (group directory names sort in chronological order).

    :param params: ParamDict, the parameter dictionary of constants

    :return: tuple, 1. the group directory name (or None if the queue is
             empty), 2. list of pending run file names in that group,
             3. list of running run file names in that group
    """
    # list the pending and running entries only
    states = [QUEUE_PENDING_DIR, QUEUE_RUNNING_DIR]
    entries = list_queue_entries(params, states=states)
    # deal with an empty queue
    if len(entries) == 0:
        return None, [], []
    # the next group is the first group in the sorted entries
    group = entries[0]['group']
    # collect the pending and running run files for this group
    pending_runs, running_runs = [], []
    for entry in entries:
        # skip entries not in this group
        if entry['group'] != group:
            continue
        # sort into pending and running
        if entry['state'] == QUEUE_PENDING_DIR:
            pending_runs.append(entry['run'])
        else:
            running_runs.append(entry['run'])
    # sort the run file names (priority order)
    pending_runs.sort()
    running_runs.sort()
    # return the group and its pending/running run files
    return group, pending_runs, running_runs


def move_run_file(queue_path: str, group: str, run_file: str,
                  from_state: str, to_state: str) -> bool:
    """
    Move a run yaml file from one queue state directory to another (and
    update the "state" entry inside the yaml file)

    Note: this function is deliberately params-free and uses simple text
    operations so it stays fast (it is mirrored by the fast "system"
    mode in apero_queue.py)

    :param queue_path: str, the absolute path to the queue directory
    :param group: str, the group directory name
    :param run_file: str, the run yaml file name
    :param from_state: str, the state directory to move from
    :param to_state: str, the state directory to move to

    :return: bool, True if the move was successful
    """
    # construct source and destination paths
    src_dir = os.path.join(queue_path, from_state, group)
    dst_dir = os.path.join(queue_path, to_state, group)
    src_path = os.path.join(src_dir, run_file)
    dst_path = os.path.join(dst_dir, run_file)
    # deal with the source file not existing
    if not os.path.exists(src_path):
        return False
    # make the destination group directory if it doesn't exist
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    # read the yaml file as plain text (fast, no yaml library needed)
    with open(src_path, 'r') as rfile:
        lines = rfile.readlines()
    # update the state line in the yaml text
    for it, line in enumerate(lines):
        if line.startswith('state:'):
            lines[it] = 'state: {0}\n'.format(to_state)
            break
    # write the updated yaml to the destination
    with open(dst_path, 'w') as wfile:
        wfile.writelines(lines)
    # remove the source file
    os.remove(src_path)
    # remove the source group directory if it is now empty
    try:
        if len(os.listdir(src_dir)) == 0:
            os.rmdir(src_dir)
    except OSError:
        pass
    # move was successful
    return True


def get_queue_cores(params: ParamDict) -> int:
    """
    Get the number of cores to use for the queue (same rules as
    drs_processing.process_run_list via drs_utils.get_cores)

    :param params: ParamDict, the parameter dictionary of constants

    :return: int, the number of cores to use
    """
    # use the same core logic as processing (note get_cores lives in
    #   drs_utils so drs_queue does not need drs_processing here)
    return drs_utils.get_cores(params)


def get_queue_mpmode(params: ParamDict) -> str:
    """
    Get the multiprocessing mode for the queue - from the --mpmode command
    line argument if set, otherwise from the TOOLS.REPROCESS.MP_TYPE
    constant (same default as drs_processing.process_run_list)

    :param params: ParamDict, the parameter dictionary of constants

    :return: str, the multiprocessing mode ('process', 'pool' or 'linear')
    """
    # default to the same constant used by process_run_list
    mpmode = str(params['TOOLS.REPROCESS.MP_TYPE']).lower()
    # command line input overrides the constant
    if 'INPUTS' in params:
        if 'MPMODE' in params['INPUTS']:
            value = params['INPUTS']['MPMODE']
            if not drs_text.null_text(value, ['', 'None']):
                mpmode = str(value).lower()
    # unknown modes fall back to linear (same as process_run_list)
    if mpmode not in QUEUE_MP_MODES:
        mpmode = 'linear'
    # return the multiprocessing mode
    return mpmode


# =============================================================================
# Define queue mode functions
# =============================================================================
def queue_run(params: ParamDict, cores: Optional[int] = None,
              mpmode: Optional[str] = None) -> Dict[str, Any]:
    """
    Run mode: run the next task(s) in the queue

    Takes the next N pending tasks (N = cores) from the earliest
    unfinished group, moves them to running, executes them and moves them
    to complete/failed based on the result. Never crosses a group
    boundary - if the earliest group has tasks running (but none pending)
    nothing is run (we must wait for the group to finish).

    :param params: ParamDict, the parameter dictionary of constants
    :param cores: int or None, override the number of cores (None uses
                  the --cores argument / CORES parameter via get_cores)
    :param mpmode: str or None, override the multiprocessing mode (None
                   uses the --mpmode argument / MP_TYPE constant)

    :return: dictionary, summary of what was done (keys: 'group',
             'n_run', 'n_complete', 'n_failed', 'message')
    """
    # storage for the summary (returned - used by the gui/flask)
    summary = dict(group=None, n_run=0, n_complete=0, n_failed=0,
                   message='')
    # make sure the queue directories exist
    setup_queue_directories(params)
    # get the queue path
    queue_path = get_queue_path(params)
    # get the number of cores and the multiprocessing mode (unless
    #   explicitly overridden e.g. by the gui)
    if cores is None:
        cores = get_queue_cores(params)
    if mpmode is None:
        mpmode = get_queue_mpmode(params)
    # -------------------------------------------------------------------------
    # claim tasks inside the queue lock (so parallel apero_queues do not
    #   claim the same tasks)
    with QueueLock(params):
        # get the next unfinished group
        group, pending_runs, running_runs = get_next_group(params)
        # deal with an empty queue
        if group is None:
            summary['message'] = 'Nothing to run (queue is empty)'
            WLOG(params, '', 'Queue: {0}'.format(summary['message']))
            return summary
        # store the group in the summary
        summary['group'] = group
        # deal with the group having no pending tasks (but still running)
        #   we must NOT start the next group until this group is finished
        if len(pending_runs) == 0:
            wmsg = ('Group "{0}" has {1} task(s) still running - '
                    'waiting for group to finish (not starting next '
                    'group)')
            summary['message'] = wmsg.format(group, len(running_runs))
            WLOG(params, 'warning',
                 'Queue: {0}'.format(summary['message']), sublevel=2)
            return summary
        # take the next N pending tasks (up to the end of the group)
        claimed_runs = pending_runs[:cores]
        # move the claimed tasks from pending to running
        for run_file in claimed_runs:
            move_run_file(queue_path, group, run_file,
                          QUEUE_PENDING_DIR, QUEUE_RUNNING_DIR)
    # -------------------------------------------------------------------------
    # log progress: running N tasks from group
    msg = 'Queue: Running {0} task(s) from group "{1}" [mpmode={2}]'
    WLOG(params, 'info', msg.format(len(claimed_runs), group, mpmode))
    # build the task list (read the claimed yaml files)
    tasks = []
    for run_file in claimed_runs:
        # construct the running yaml path
        run_path = os.path.join(queue_path, QUEUE_RUNNING_DIR, group,
                                run_file)
        # read the yaml file
        run_dict = base.load_yaml(run_path)
        # construct the task tuple (group, run file, runstring, shortname)
        task = dict()
        task['group'] = group
        task['run_file'] = run_file
        task['runstring'] = str(run_dict['runstring'])
        task['shortname'] = str(run_dict['shortname'])
        tasks.append(task)
    # -------------------------------------------------------------------------
    # execute the tasks (linear or multiprocess based on mpmode)
    results = _execute_tasks(params, tasks, cores, mpmode)
    # -------------------------------------------------------------------------
    # move tasks from running to complete/failed based on results
    for run_file in results:
        # work out the destination state
        if results[run_file]:
            to_state = QUEUE_COMPLETE_DIR
        else:
            to_state = QUEUE_FAILED_DIR
        # move the run file
        move_run_file(queue_path, group, run_file,
                      QUEUE_RUNNING_DIR, to_state)
        # log the result
        msg = 'Queue: \t {0}/{1} --> {2}'
        WLOG(params, '', msg.format(group, run_file, to_state))
    # -------------------------------------------------------------------------
    # summarize
    n_ok = sum(1 for run_file in results if results[run_file])
    n_bad = len(results) - n_ok
    msg = 'Finished {0} task(s): {1} complete, {2} failed'
    summary['n_run'] = len(results)
    summary['n_complete'] = n_ok
    summary['n_failed'] = n_bad
    summary['message'] = msg.format(len(results), n_ok, n_bad)
    WLOG(params, 'info', 'Queue: {0}'.format(summary['message']))
    # return the summary (used by the gui/flask)
    return summary


def queue_status(params: ParamDict):
    """
    Status mode: show an interactive terminal (cli) view of the queue

    Shows a summary of how many tasks are pending/running/complete/failed
    and then an interactive pager (--rows entries at a time, default 10)
    that can be scrolled through (large queues may have 600K+ entries so
    we never load everything into the terminal at once)

    Note: for a graphical view (with action buttons) use gui mode
    (apero_queue.py gui) - status mode is the fallback for terminals
    with no browser access

    :param params: ParamDict, the parameter dictionary of constants

    :return: None
    """
    # get the state filter from user inputs (default all states)
    states = _get_state_filter(params)
    # gather the queue entries (fast - only lists files)
    entries = list_queue_entries(params, states=states)
    # get the rows per page (default cli page size)
    rows = _get_status_rows(params, QUEUE_STATUS_PAGE_SIZE)
    # get the colour class
    colors = drs_misc.Colors()
    # define per-state colours
    state_colors = dict()
    state_colors[QUEUE_PENDING_DIR] = colors.warning
    state_colors[QUEUE_RUNNING_DIR] = colors.okblue
    state_colors[QUEUE_COMPLETE_DIR] = colors.okgreen
    state_colors[QUEUE_FAILED_DIR] = colors.fail
    # -------------------------------------------------------------------------
    # print the summary (counts per state)
    print(colors.header + 'APERO QUEUE STATUS' + colors.endc)
    print('Queue path: {0}'.format(get_queue_path(params)))
    for state in QUEUE_SUB_DIRS:
        # skip states filtered out
        if state not in states:
            continue
        # count entries in this state
        count = sum(1 for entry in entries if entry['state'] == state)
        # print the count (coloured by state)
        cargs = [state_colors[state], state.upper(), count, colors.endc]
        print('{0}\t{1}: {2}{3}'.format(*cargs))
    # deal with no entries at all
    if len(entries) == 0:
        print('Queue is empty (no entries to show)')
        return
    # -------------------------------------------------------------------------
    # non-interactive mode (not a tty): just print the first page
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    # start at the first entry
    position = 0
    # loop around pages (interactive pager)
    while True:
        # print the current page
        _print_status_page(entries, position, rows, state_colors, colors)
        # non-interactive: only show the first page
        if not interactive:
            break
        # ask the user what to do next
        prompt = ('[n]ext [p]rev [j]ump <N> [q]uit : ')
        try:
            user_input = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        # deal with quitting
        if user_input.startswith('q'):
            break
        # deal with going backwards
        elif user_input.startswith('p'):
            position = max(0, position - rows)
        # deal with jumping to a specific entry
        elif user_input.startswith('j'):
            # get the jump target (number after 'j')
            try:
                target = int(user_input[1:].strip())
                position = max(0, min(target, len(entries) - 1))
            except ValueError:
                print('Invalid jump target (use e.g. "j 1000")')
        # default (and 'n'): go forwards
        else:
            # do not go past the end of the list
            if position + rows < len(entries):
                position = position + rows


def reset_queue(params: ParamDict, states: List[str]) -> int:
    """
    Reset the queue (non-interactive core): remove all run yaml files
    (and group directories) from the given queue state directories

    Note: this function does NOT ask for confirmation - it is used by
    queue_reset (cli, which asks first) and by the gui/flask (which
    confirms in the browser)

    :param params: ParamDict, the parameter dictionary of constants
    :param states: list of strings, the queue states to reset

    :return: int, the number of entries removed
    """
    # get the queue path
    queue_path = get_queue_path(params)
    # count what we are about to remove
    entries = list_queue_entries(params, states=states)
    # deal with nothing to reset
    if len(entries) == 0:
        return 0
    # -------------------------------------------------------------------------
    # remove the group directories in the selected states
    with QueueLock(params):
        for state in states:
            # construct the state directory path
            state_path = os.path.join(queue_path, state)
            # skip states that do not exist
            if not os.path.isdir(state_path):
                continue
            # loop around group directories and remove them
            for group in os.listdir(state_path):
                # only remove queue group directories
                if not group.startswith('APERO-QUEUE-GROUP-'):
                    continue
                # remove the group directory (and all its yaml files)
                shutil.rmtree(os.path.join(state_path, group),
                              ignore_errors=True)
    # return the number of entries removed
    return len(entries)


def queue_reset(params: ParamDict):
    """
    Reset mode: remove all run yaml files (and group directories) from
    the queue state directories

    The --qstate argument can be used to only reset one state (pending,
    running, complete or failed) - the default is to reset all states.
    If there are entries in the running directory the user is warned and
    asked to confirm before anything is removed.

    :param params: ParamDict, the parameter dictionary of constants

    :return: None
    """
    # get the state filter from user inputs (default all states)
    states = _get_state_filter(params)
    # -------------------------------------------------------------------------
    # warn the user if there are running entries (things may be running!)
    running_entries = list_queue_entries(params,
                                         states=[QUEUE_RUNNING_DIR])
    if len(running_entries) > 0 and QUEUE_RUNNING_DIR in states:
        wmsg = ('Queue: There are {0} entries in the running directory - '
                'tasks may currently be running!')
        WLOG(params, 'warning', wmsg.format(len(running_entries)),
             sublevel=2)
    # -------------------------------------------------------------------------
    # count what we are about to remove
    entries = list_queue_entries(params, states=states)
    # deal with nothing to reset
    if len(entries) == 0:
        WLOG(params, '', 'Queue: Nothing to reset')
        return
    # ask the user to confirm the reset
    question = ('Queue: Remove {0} entries from state(s) {1}? [y/N]: ')
    user_input = _ask(question.format(len(entries), ', '.join(states)))
    if not user_input.lower().startswith('y'):
        WLOG(params, '', 'Queue: Reset cancelled')
        return
    # -------------------------------------------------------------------------
    # do the reset (non-interactive core)
    n_removed = reset_queue(params, states)
    # log that the reset is done
    msg = 'Queue: Reset complete ({0} entries removed from {1})'
    WLOG(params, 'info', msg.format(n_removed, ', '.join(states)))


def queue_init(params: ParamDict):
    """
    Init mode: interactively create the batch template file

    Asks the user for the sbatch settings (time, nodes, cpus, memory,
    account, email etc) and for any activation script lines needed to set
    up the environment inside a batch job (e.g. module loads, conda/venv
    activation, apero profile setup). The template is stored in
    {QUEUE.PATH}/batch_template.yaml and used by batch mode.

    :param params: ParamDict, the parameter dictionary of constants

    :return: None
    """
    # make sure the queue (and output) directories exist
    setup_queue_directories(params)
    setup_output_directories(params)
    # get the queue path and template path
    queue_path = get_queue_path(params)
    template_path = os.path.join(queue_path, QUEUE_BATCH_TEMPLATE)
    # start from the defaults (or the current template if it exists)
    if os.path.exists(template_path):
        template = base.load_yaml(template_path,
                                  default=dict(QUEUE_BATCH_DEFAULTS))
        WLOG(params, '', 'Queue: Updating existing batch template')
    else:
        template = dict(QUEUE_BATCH_DEFAULTS)
    # -------------------------------------------------------------------------
    # ask the user for the sbatch settings (enter keeps current value)
    print('APERO QUEUE BATCH TEMPLATE SETUP')
    print('Press ENTER to keep the [current] value\n')
    # define the questions to ask (key, question)
    questions = [
        ('time', 'sbatch --time (e.g. 48:00:00)'),
        ('nodes', 'sbatch --nodes'),
        ('cpus_per_task', 'sbatch --cpus-per-task'),
        ('mem', 'sbatch --mem (0 = all node memory)'),
        ('account', 'sbatch --account (e.g. rrg-xxxxxx)'),
        ('job_name', 'sbatch --job-name prefix'),
        ('mail_user', 'sbatch --mail-user (email address)'),
        ('mail_type', 'sbatch --mail-type'),
    ]
    # loop around the questions
    for key, question in questions:
        # ask the question showing the current value
        prompt = '{0} [{1}]: '.format(question, template[key])
        user_input = _ask(prompt)
        # keep the current value if the user just pressed enter
        if len(user_input.strip()) > 0:
            template[key] = user_input.strip()
    # -------------------------------------------------------------------------
    # ask the user for the activation script lines (multiple allowed)
    print('\nActivation script lines (run at the start of every batch '
          'job)')
    print('e.g.: module load StdEnv/2023 python/3.12')
    print('e.g.: source /path/to/env/bin/activate')
    print('e.g.: source apero_profile.sh my_profile')
    # show any current activation lines
    if len(template['activation']) > 0:
        print('Current activation lines:')
        for line in template['activation']:
            print('\t{0}'.format(line))
        # ask whether to keep or redefine them
        user_input = _ask('Keep current activation lines? [Y/n]: ')
        if user_input.lower().startswith('n'):
            template['activation'] = []
    # loop asking for activation lines until the user is done
    while True:
        prompt = 'Add activation script line (or ENTER to continue): '
        user_input = _ask(prompt)
        # blank input means the user is done
        if len(user_input.strip()) == 0:
            break
        # add the activation line to the template
        template['activation'].append(user_input.strip())
    # -------------------------------------------------------------------------
    # save the template to the queue directory
    base.write_yaml(template, template_path, width=float('inf'))
    # log that the template has been written
    msg = 'Queue: Batch template written to {0}'
    WLOG(params, 'info', msg.format(template_path))


def batch_queue(params: ParamDict, per_batch: int,
                n_batches: Optional[int] = None,
                submit: bool = False) -> Dict[str, Any]:
    """
    Batch the queue (non-interactive core): create (and optionally
    submit) sbatch scripts for the next unfinished group in the queue

    Tasks are only ever taken from the earliest unfinished group (never
    two groups at once). Each runstring in a batch script is followed by
    a call to "apero_queue.py system" which moves the task from running
    to complete/failed as soon as it finishes.

    Note: this function does NOT ask questions - it is used by
    queue_batch (cli, which asks first) and by the gui/flask (which
    supplies the values from a form)

    :param params: ParamDict, the parameter dictionary of constants
    :param per_batch: int, the number of tasks per batch script
    :param n_batches: int or None, the number of batch scripts to create
                      (None means as many as needed for all pending
                      tasks in the group)
    :param submit: bool, if True submit the scripts via sbatch

    :return: dictionary, summary of what was done (keys: 'group',
             'scripts', 'n_claimed', 'n_submitted', 'message')
    """
    # storage for the summary (returned - used by the gui/flask)
    summary = dict(group=None, scripts=[], n_claimed=0, n_submitted=0,
                   message='')
    # make sure the queue (and output) directories exist
    setup_queue_directories(params)
    out_dirs = setup_output_directories(params)
    # get the queue path
    queue_path = get_queue_path(params)
    # -------------------------------------------------------------------------
    # load the batch template (created by init mode)
    template_path = os.path.join(queue_path, QUEUE_BATCH_TEMPLATE)
    if not os.path.exists(template_path):
        summary['message'] = ('No batch template found - please run '
                              '"apero_queue.py init" first')
        return summary
    template = base.load_yaml(template_path,
                              default=dict(QUEUE_BATCH_DEFAULTS))
    # -------------------------------------------------------------------------
    # claim tasks inside the queue lock
    with QueueLock(params):
        # get the next unfinished group
        group, pending_runs, running_runs = get_next_group(params)
        # deal with an empty queue
        if group is None:
            summary['message'] = 'Nothing to batch (queue is empty)'
            return summary
        # store the group in the summary
        summary['group'] = group
        # deal with the group having no pending tasks (but still running)
        if len(pending_runs) == 0:
            wmsg = ('Group "{0}" has {1} task(s) still running - '
                    'waiting for group to finish (not starting next '
                    'group)')
            summary['message'] = wmsg.format(group, len(running_runs))
            return summary
        # ---------------------------------------------------------------------
        # work out the number of batches (never more than needed)
        per_batch = max(1, int(per_batch))
        max_batches = (len(pending_runs) + per_batch - 1) // per_batch
        if n_batches is None:
            n_batches = max_batches
        n_batches = max(1, min(int(n_batches), max_batches))
        # only claim the tasks we are actually going to batch
        n_claim = min(len(pending_runs), n_batches * per_batch)
        claimed_runs = pending_runs[:n_claim]
        # move the claimed tasks from pending to running
        for run_file in claimed_runs:
            move_run_file(queue_path, group, run_file,
                          QUEUE_PENDING_DIR, QUEUE_RUNNING_DIR)
    # store the number of claimed tasks
    summary['n_claimed'] = len(claimed_runs)
    # -------------------------------------------------------------------------
    # generate the batch scripts
    for b_it in range(n_batches):
        # slice the tasks for this batch
        batch_runs = claimed_runs[b_it * per_batch:(b_it + 1) * per_batch]
        # skip empty batches (shouldn't happen but be safe)
        if len(batch_runs) == 0:
            continue
        # generate the batch script for these tasks
        script_path = _write_batch_script(params, template, group,
                                          batch_runs, b_it, out_dirs)
        summary['scripts'].append(script_path)
        # log the script creation
        msg = 'Queue: \t Created batch script {0} ({1} tasks)'
        WLOG(params, '', msg.format(script_path, len(batch_runs)))
    # -------------------------------------------------------------------------
    # submit the batch scripts via sbatch (if requested)
    if submit:
        # check that sbatch is available
        if shutil.which('sbatch') is None:
            summary['message'] = ('"sbatch" not found on this machine - '
                                  'scripts written but not submitted')
            WLOG(params, 'warning',
                 'Queue: {0}'.format(summary['message']), sublevel=2)
            return summary
        # submit each script via sbatch
        for script_path in summary['scripts']:
            # submit the script
            cmd = ['sbatch', script_path]
            output = subprocess.run(cmd, capture_output=True, text=True)
            # log the submission result
            if output.returncode == 0:
                summary['n_submitted'] += 1
                msg = 'Queue: \t Submitted {0}: {1}'
                WLOG(params, '',
                     msg.format(os.path.basename(script_path),
                                output.stdout.strip()))
            else:
                wmsg = 'Queue: \t Failed to submit {0}: {1}'
                WLOG(params, 'warning',
                     wmsg.format(os.path.basename(script_path),
                                 output.stderr.strip()), sublevel=2)
    # -------------------------------------------------------------------------
    # construct the summary message
    msg = 'Created {0} batch script(s) ({1} tasks claimed, {2} submitted)'
    summary['message'] = msg.format(len(summary['scripts']),
                                    summary['n_claimed'],
                                    summary['n_submitted'])
    # return the summary (used by the gui/flask)
    return summary


def queue_batch(params: ParamDict):
    """
    Batch mode: create (and optionally submit) sbatch scripts for the
    next unfinished group in the queue (interactive cli wrapper around
    batch_queue)

    The user is asked how many tasks to put in each batch script
    (activation scripts are slow to load so we do not want one batch
    script per task), how many batch scripts to create and whether to
    submit them via sbatch.

    :param params: ParamDict, the parameter dictionary of constants

    :return: None
    """
    # get the queue path
    queue_path = get_queue_path(params)
    # -------------------------------------------------------------------------
    # check the batch template exists (created by init mode)
    template_path = os.path.join(queue_path, QUEUE_BATCH_TEMPLATE)
    if not os.path.exists(template_path):
        emsg = ('Queue: No batch template found - please run '
                '"apero_queue.py init" first (expected: {0})')
        WLOG(params, 'error', emsg.format(template_path))
        return
    template = base.load_yaml(template_path,
                              default=dict(QUEUE_BATCH_DEFAULTS))
    # -------------------------------------------------------------------------
    # peek at the next unfinished group (to show the user the counts)
    group, pending_runs, running_runs = get_next_group(params)
    # deal with an empty queue
    if group is None:
        WLOG(params, '', 'Queue: Nothing to batch (queue is empty)')
        return
    # deal with the group having no pending tasks (but still running)
    if len(pending_runs) == 0:
        wmsg = ('Queue: Group "{0}" has {1} task(s) still running - '
                'waiting for group to finish (not starting next group)')
        wargs = [group, len(running_runs)]
        WLOG(params, 'warning', wmsg.format(*wargs), sublevel=2)
        return
    # ---------------------------------------------------------------------
    # interactively work out how to split the tasks into batches
    n_tasks = len(pending_runs)
    msg = 'Queue: Group "{0}" has {1} pending task(s)'
    WLOG(params, 'info', msg.format(group, n_tasks))
    # ask how many tasks per batch script
    default_per_batch = int(template['cpus_per_task'])
    prompt = 'How many tasks per batch script? [{0}]: '
    per_batch = _ask_int(prompt.format(default_per_batch),
                         default_per_batch, minimum=1)
    # work out the maximum number of batch scripts needed
    max_batches = (n_tasks + per_batch - 1) // per_batch
    # ask how many batch scripts to create (may be less than needed
    #   e.g. user only wants to submit a few batches at a time)
    prompt = 'How many batch scripts to create? [{0}]: '
    n_batches = _ask_int(prompt.format(max_batches), max_batches,
                         minimum=1)
    # ask whether to submit the batch scripts via sbatch
    user_input = _ask('Submit batch script(s) via sbatch? [y/N]: ')
    submit = user_input.lower().startswith('y')
    # -------------------------------------------------------------------------
    # do the batching (non-interactive core - claims tasks under lock)
    summary = batch_queue(params, per_batch, n_batches, submit)
    # log the summary message
    WLOG(params, 'info', 'Queue: {0}'.format(summary['message']))
    # tell the user where the scripts are (if not submitted)
    if len(summary['scripts']) > 0 and summary['n_submitted'] == 0:
        msg = ('Queue: Scripts are in {0} (submit manually with '
               'sbatch)')
        WLOG(params, '',
             msg.format(os.path.dirname(summary['scripts'][0])))


def queue_system(params: ParamDict):
    """
    System mode (slow fallback): move a run yaml file from running to
    complete/failed

    This is the params-based fallback for the fast system mode in
    apero_queue.py (which avoids loading params entirely by using the
    --qpath argument baked into the batch scripts)

    :param params: ParamDict, the parameter dictionary of constants
                   (must have INPUTS.QID and INPUTS.QRESULT set)

    :return: None
    """
    # get the queue path
    queue_path = get_queue_path(params)
    # get the qid (group/run_file) and result from user inputs
    qid = str(params['INPUTS']['QID'])
    qresult = str(params['INPUTS']['QRESULT']).lower()
    # deal with a null qid
    if drs_text.null_text(qid, ['', 'None']):
        WLOG(params, 'error', 'Queue: system mode requires --qid')
        return
    # split the qid into group and run file
    group, run_file = qid.split('/', 1)
    # work out the destination state from the result
    if qresult in ['success', 'complete', 'true', '1']:
        to_state = QUEUE_COMPLETE_DIR
    else:
        to_state = QUEUE_FAILED_DIR
    # move the run file from running to the destination state
    moved = move_run_file(queue_path, group, run_file,
                          QUEUE_RUNNING_DIR, to_state)
    # log the result
    if moved:
        msg = 'Queue: {0} --> {1}'
        WLOG(params, '', msg.format(qid, to_state))
    else:
        wmsg = 'Queue: could not move {0} (not in running)'
        WLOG(params, 'warning', wmsg.format(qid), sublevel=2)


# =============================================================================
# Define worker functions
# =============================================================================
def _run_item_to_dict(run_item: Any, group_dirname: str) -> Dict[str, Any]:
    """
    Convert a Run instance into a plain dictionary for the queue yaml file

    :param run_item: Run instance, the run item to convert
    :param group_dirname: str, the name of the group directory this run
                          item belongs to

    :return: dictionary, the queue yaml dictionary
    """
    # construct the queue dictionary (order here is the order in the yaml)
    queue_dict = dict()
    queue_dict['recipe'] = str(run_item.recipename)
    queue_dict['shortname'] = str(run_item.shortname)
    queue_dict['obs_dir'] = str(run_item.obs_dir)
    queue_dict['args'] = _sanitize_value(run_item.kwargs)
    queue_dict['runstring'] = str(run_item.runstring)
    queue_dict['is_reference'] = bool(run_item.reference)
    queue_dict['group'] = str(group_dirname)
    queue_dict['state'] = QUEUE_STATE_PENDING
    queue_dict['priority'] = int(run_item.priority)
    # return the queue dictionary
    return queue_dict


def _sanitize_value(value: Any) -> Any:
    """
    Sanitize a value so it can be written to a yaml file

    Basic python types (str, int, float, bool, None) are kept as they are,
    dictionaries / lists / tuples are sanitized recursively and any other
    type is converted to its string representation

    :param value: Any, the value to sanitize

    :return: Any, the sanitized value (yaml safe)
    """
    # basic types are yaml safe as they are
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    # sanitize dictionaries recursively
    if isinstance(value, dict):
        return {str(key): _sanitize_value(value[key]) for key in value}
    # sanitize lists/tuples/sets recursively (always return a list)
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_value(item) for item in value]
    # any other type is converted to its string representation
    return str(value)


def _get_state_filter(params: ParamDict) -> List[str]:
    """
    Get the queue state filter from user inputs (--qstate argument)

    :param params: ParamDict, the parameter dictionary of constants

    :return: list of strings, the queue states to act on (defaults to
             all states if --qstate is not set or set to 'all')
    """
    # default to all states
    states = list(QUEUE_SUB_DIRS)
    # check for the qstate user input
    if 'INPUTS' in params:
        if 'QSTATE' in params['INPUTS']:
            value = params['INPUTS']['QSTATE']
            # only use non-null and non-'all' values
            if not drs_text.null_text(value, ['', 'None', 'All']):
                value = str(value).lower()
                # only accept valid states
                if value in QUEUE_SUB_DIRS:
                    states = [value]
    # return the state filter
    return states


def _get_status_rows(params: ParamDict, default: int) -> int:
    """
    Get the number of rows per page for status mode (from the --rows
    command line argument if set, otherwise the given default)

    :param params: ParamDict, the parameter dictionary of constants
    :param default: int, the default number of rows per page

    :return: int, the number of rows per page (always >= 1)
    """
    # start with the default
    rows = default
    # check for the rows user input
    if 'INPUTS' in params:
        if 'ROWS' in params['INPUTS']:
            value = params['INPUTS']['ROWS']
            # only use non-null values
            if not drs_text.null_text(value, ['', 'None']):
                try:
                    rows = int(value)
                except (TypeError, ValueError):
                    wmsg = ('Queue: Invalid --rows value "{0}" - using '
                            'default ({1})')
                    WLOG(params, 'warning', wmsg.format(value, default),
                         sublevel=1)
    # rows must be at least 1
    return max(rows, 1)


def _ask(question: str) -> str:
    """
    Ask the user a question and return their (string) answer

    :param question: str, the question to ask

    :return: str, the user's answer ('' if input is not possible)
    """
    # deal with input not being possible (e.g. non-interactive)
    try:
        return input(question)
    except (EOFError, KeyboardInterrupt):
        return ''


def _ask_int(question: str, default: int, minimum: int = 1) -> int:
    """
    Ask the user for an integer (with a default and a minimum value)

    :param question: str, the question to ask
    :param default: int, the value used if the user just presses enter
    :param minimum: int, the minimum allowed value

    :return: int, the user's answer (or the default)
    """
    # loop until we get a valid answer
    while True:
        # ask the question
        user_input = _ask(question).strip()
        # blank input means use the default
        if len(user_input) == 0:
            return max(default, minimum)
        # try to convert the answer to an integer
        try:
            value = int(user_input)
        except ValueError:
            print('Invalid integer - please try again')
            continue
        # enforce the minimum value
        if value < minimum:
            print('Value must be >= {0} - please try again'.format(minimum))
            continue
        # return the valid value
        return value


def _print_status_page(entries: List[Dict[str, str]], position: int,
                       page: int, state_colors: Dict[str, str],
                       colors: Any):
    """
    Print one page of the queue status pager

    :param entries: list of dictionaries, the queue entries (from
                    list_queue_entries)
    :param position: int, the index of the first entry to show
    :param page: int, the number of entries to show per page
    :param state_colors: dictionary, mapping state name to colour code
    :param colors: Colors instance, for header/end colour codes

    :return: None, prints to standard output
    """
    # work out the end of the page
    end = min(position + page, len(entries))
    # print the page header (shows where we are in the list)
    header = '\nN={0}-{1} of {2} entries'
    print(colors.header + header.format(position, end - 1, len(entries))
          + colors.endc)
    # keep track of the current group (to separate groups nicely)
    current_group = None
    # loop around the entries in this page
    for it in range(position, end):
        # get this entry
        entry = entries[it]
        # print a group separator when the group changes
        if entry['group'] != current_group:
            current_group = entry['group']
            print(colors.bold + '  ' + current_group + colors.endc)
        # get the colour for this state
        color = state_colors.get(entry['state'], '')
        # print the entry (index, state, run file name)
        eargs = [color, it, entry['state'].upper(), entry['run'],
                 colors.endc]
        print('{0}    [{1}] {2:<9} {3}{4}'.format(*eargs))


def _run_task(task: Dict[str, str]) -> Tuple[str, bool, str]:
    """
    Run a single queue task (executes the runstring in a shell)

    Success requires both a zero exit code and the absence of the apero
    "has NOT been successfully completed" log signature in the output

    :param task: dictionary, the task with keys 'group', 'run_file',
                 'runstring' and 'shortname'

    :return: tuple, 1. the run file name, 2. bool True if the task was
             successful, 3. str the tail of the task output (for
             reporting failures)
    """
    # run the runstring in a shell (capturing all output)
    process = subprocess.run(task['runstring'], shell=True,
                             capture_output=True, text=True)
    # combine standard output and error for the failure check
    output = str(process.stdout) + str(process.stderr)
    # keep only the tail of the output (for reporting)
    tail = '\n'.join(output.splitlines()[-10:])
    # success requires a zero return code
    success = process.returncode == 0
    # and the output must not contain the apero failure signature
    if QUEUE_FAIL_SIGNATURE in output:
        success = False
    # return the run file name, success flag and output tail
    return task['run_file'], success, tail


def _execute_tasks(params: ParamDict, tasks: List[Dict[str, str]],
                   cores: int, mpmode: str) -> Dict[str, bool]:
    """
    Execute a list of queue tasks (linear or in parallel based on mpmode)

    :param params: ParamDict, the parameter dictionary of constants
    :param tasks: list of dictionaries, the tasks to run (each with keys
                  'group', 'run_file', 'runstring' and 'shortname')
    :param cores: int, the number of cores to use (for pool/process)
    :param mpmode: str, the multiprocessing mode ('process', 'pool' or
                   'linear')

    :return: dictionary, mapping run file name to success (bool)
    """
    # storage of results (run file name -> success)
    results = dict()
    # -------------------------------------------------------------------------
    # linear mode: run tasks one after the other
    if mpmode == 'linear' or cores == 1 or len(tasks) == 1:
        # loop around tasks
        for t_it, task in enumerate(tasks):
            # log which task we are running
            msg = 'Queue: Running {0} [{1}/{2}]'
            margs = [task['shortname'], t_it + 1, len(tasks)]
            WLOG(params, '', msg.format(*margs))
            WLOG(params, '', '\t{0}'.format(task['runstring']), wrap=False)
            # run the task
            run_file, success, tail = _run_task(task)
            # store the result
            results[run_file] = success
            # report failures (with the output tail)
            if not success:
                wmsg = 'Queue: Task {0} FAILED:\n{1}'
                WLOG(params, 'warning', wmsg.format(run_file, tail),
                     sublevel=2)
        # return the results
        return results
    # -------------------------------------------------------------------------
    # pool mode: use a multiprocessing pool
    if mpmode == 'pool':
        # deferred import (only needed for parallel modes)
        from multiprocessing import get_context
        # use fork-based pool (same as drs_processing pool mode)
        with get_context('fork').Pool(cores) as pool:
            outputs = pool.map(_run_task, tasks)
    # -------------------------------------------------------------------------
    # process mode: use individual processes (chunked by cores)
    else:
        # deferred imports (only needed for parallel modes)
        from multiprocessing import Process, Manager
        # shared storage for the process results
        manager = Manager()
        shared = manager.list()

        # small wrapper to push results into the shared list
        def _process_target(_task, _shared):
            _shared.append(_run_task(_task))
        # run the tasks in chunks of size cores
        for c_it in range(0, len(tasks), cores):
            # storage of processes in this chunk
            procs = []
            # start a process for each task in this chunk
            for task in tasks[c_it:c_it + cores]:
                proc = Process(target=_process_target,
                               args=(task, shared))
                proc.start()
                procs.append(proc)
            # wait for all processes in this chunk to finish
            for proc in procs:
                proc.join()
        # convert the shared list to a normal list
        outputs = list(shared)
    # -------------------------------------------------------------------------
    # store (and report) the parallel results
    for run_file, success, tail in outputs:
        results[run_file] = success
        # report failures (with the output tail)
        if not success:
            wmsg = 'Queue: Task {0} FAILED:\n{1}'
            WLOG(params, 'warning', wmsg.format(run_file, tail),
                 sublevel=2)
    # return the results
    return results


def _write_batch_script(params: ParamDict, template: Dict[str, Any],
                        group: str, batch_runs: List[str], batch_it: int,
                        out_dirs: Dict[str, str]) -> str:
    """
    Write a single sbatch script for a set of queue tasks

    Each runstring is followed by a call to "apero_queue.py system" which
    moves the task from running to complete/failed as soon as the task
    finishes (this is how batch mode knows when tasks are done)

    :param params: ParamDict, the parameter dictionary of constants
    :param template: dictionary, the batch template (from init mode)
    :param group: str, the group directory name these tasks belong to
    :param batch_runs: list of strings, the run yaml file names to put in
                       this batch script
    :param batch_it: int, the index of this batch script (used in the
                     script/job name)
    :param out_dirs: dictionary, the output directory paths (from
                     setup_output_directories)

    :return: str, the absolute path to the written batch script
    """
    # get the queue path
    queue_path = get_queue_path(params)
    # construct the job name (template prefix + group + batch number)
    job_name = '{0}_{1}_B{2:04d}'.format(template['job_name'], group,
                                         batch_it)
    # construct the script file name and path
    script_name = '{0}-BATCH-{1:04d}.sbatch'.format(group, batch_it)
    script_path = os.path.join(out_dirs['scripts'], script_name)
    # -------------------------------------------------------------------------
    # build the sbatch header lines
    lines = ['#!/bin/bash']
    lines.append('#SBATCH --time={0}'.format(template['time']))
    lines.append('#SBATCH --nodes={0}'.format(template['nodes']))
    lines.append('#SBATCH --cpus-per-task={0}'
                 ''.format(template['cpus_per_task']))
    lines.append('#SBATCH --mem={0}'.format(template['mem']))
    # only add the account if one was given
    if len(str(template['account'])) > 0:
        lines.append('#SBATCH --account={0}'.format(template['account']))
    lines.append('#SBATCH --job-name={0}'.format(job_name))
    lines.append('#SBATCH --output={0}'
                 ''.format(os.path.join(out_dirs['logs'], '%j_%x.out')))
    lines.append('#SBATCH --error={0}'
                 ''.format(os.path.join(out_dirs['errors'], '%j_%x.err')))
    # only add the email settings if an email address was given
    if len(str(template['mail_user'])) > 0:
        lines.append('#SBATCH --mail-user={0}'
                     ''.format(template['mail_user']))
        lines.append('#SBATCH --mail-type={0}'
                     ''.format(template['mail_type']))
    lines.append('')
    # -------------------------------------------------------------------------
    # add the activation script lines (environment setup)
    lines.append('echo "RUNNING: activation scripts"')
    for act_line in template['activation']:
        lines.append('echo "{0}"'.format(act_line.replace('"', '\\"')))
        lines.append(act_line)
    lines.append('')
    # -------------------------------------------------------------------------
    # add the runstrings (each followed by an apero_queue system call to
    #   move the task from running to complete/failed when it finishes)
    for r_it, run_file in enumerate(batch_runs):
        # read the running yaml to get the runstring and shortname
        run_path = os.path.join(queue_path, QUEUE_RUNNING_DIR, group,
                                run_file)
        run_dict = base.load_yaml(run_path)
        # construct the queue id for this task (group/run_file)
        qid = '{0}/{1}'.format(group, run_file)
        # add the echo line (shows progress in the batch log)
        eargs = [run_dict['shortname'], r_it + 1, len(batch_runs)]
        lines.append('echo "Running: {0} [{1}/{2}]"'.format(*eargs))
        # add the runstring itself
        lines.append(str(run_dict['runstring']))
        # add the apero_queue system call (moves the task to
        #   complete/failed based on the exit code of the runstring)
        lines.append('if [ $? -eq 0 ]; then')
        lines.append('    apero_queue.py system --qpath={0} --qid={1} '
                     '--qresult=success'.format(queue_path, qid))
        lines.append('else')
        lines.append('    apero_queue.py system --qpath={0} --qid={1} '
                     '--qresult=failed'.format(queue_path, qid))
        lines.append('fi')
        lines.append('')
    # -------------------------------------------------------------------------
    # write the batch script to disk
    with open(script_path, 'w') as sfile:
        sfile.write('\n'.join(lines))
    # make the script executable
    os.chmod(script_path, 0o755)
    # return the script path
    return script_path


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

