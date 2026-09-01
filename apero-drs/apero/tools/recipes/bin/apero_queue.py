#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO queue management tool

Manage the APERO processing queue (created by apero_processing in queue
mode). The main argument is "mode":

    - run: run the next task(s) in the queue (up to --cores tasks, never
           crossing a group boundary)
    - batch: create (and optionally submit) sbatch scripts for the next
             unfinished group in the queue
    - status: interactive terminal (cli) view of the queue (pending/
              running/complete/failed) - for use without a browser
    - gui: browser dashboard with the queue status (coloured by state,
           filterable, sortable) and action buttons (run, batch, reset,
           template settings)
    - reset: remove entries from the queue (optionally filtered by
             --qstate)
    - init: interactively create the batch template (sbatch settings and
            activation scripts) - required before using batch mode
    - system: internal fast mode used by batch scripts to move a task
              from running to complete/failed (uses --qpath, --qid and
              --qresult and avoids loading the full APERO runtime)

Created on 2026-08-31

@author: cook
"""
import argparse
import os
import sys
from typing import Any, Dict, Optional

import apero as apero_pkg

# Note: heavy APERO imports are deferred to runtime so that the "system"
#   mode (run after every runstring in batch scripts) stays super quick

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_queue.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
# define the queue state directory names for the fast "system" path
#    (duplicated from drs_queue deliberately - importing drs_queue loads
#     the full apero runtime which is far too slow for system mode)
QUEUE_RUNNING_DIR = 'running'
QUEUE_COMPLETE_DIR = 'complete'
QUEUE_FAILED_DIR = 'failed'
# define the valid queue modes
QUEUE_MODES = ['run', 'batch', 'status', 'gui', 'reset', 'init', 'system']


# =============================================================================
# Define fast path functions (system mode)
# =============================================================================
def _quick_parse_args() -> Dict[str, Optional[str]]:
    """
    Parse fast-path options before loading the full APERO runtime

    :return: dictionary with the quick option values
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('mode', nargs='?', default=None)
    parser.add_argument('--qpath', type=str, default=None)
    parser.add_argument('--qid', type=str, default=None)
    parser.add_argument('--qresult', type=str, default=None)
    args, _ = parser.parse_known_args()
    return dict(vars(args))


def _system_move(qpath: str, qid: str, qresult: str) -> bool:
    """
    Fast system mode: move a run yaml file from running to
    complete/failed using only the standard library (mirror of
    drs_queue.move_run_file)

    :param qpath: str, the absolute path to the queue directory
    :param qid: str, the queue id of the task ("{group}/{run_file}")
    :param qresult: str, the result of the task ('success' or 'failed')

    :return: bool, True if the move was successful
    """
    # split the qid into group and run file
    if '/' not in qid:
        return False
    group, run_file = qid.split('/', 1)
    # work out the destination state from the result
    if qresult.lower() in ['success', 'complete', 'true', '1']:
        to_state = QUEUE_COMPLETE_DIR
    else:
        to_state = QUEUE_FAILED_DIR
    # construct source and destination paths
    src_dir = os.path.join(qpath, QUEUE_RUNNING_DIR, group)
    dst_dir = os.path.join(qpath, to_state, group)
    src_path = os.path.join(src_dir, run_file)
    dst_path = os.path.join(dst_dir, run_file)
    # deal with the source file not existing
    if not os.path.exists(src_path):
        return False
    # make the destination group directory if it doesn't exist
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


def _system_main(quick_args: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Fast-path main for system mode (no APERO runtime loaded)

    :param quick_args: dictionary, the quick option values

    :return: dictionary containing the local variables
    """
    # get the fast-path arguments
    qpath = quick_args['qpath']
    qid = quick_args['qid']
    qresult = quick_args['qresult']
    # deal with missing arguments
    if qid is None or qresult is None:
        print('QUEUE ERROR: system mode requires --qid and --qresult')
        sys.exit(1)
    # move the run file
    moved = _system_move(qpath, qid, qresult)
    # report the result (kept minimal for speed)
    if moved:
        print('QUEUE: {0} --> {1}'.format(qid, qresult))
    else:
        print('QUEUE WARNING: could not move {0}'.format(qid))
    # return the local variables
    return locals()


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
def main(mode=None, **kwargs):
    """
    Main function for apero_queue.py

    :param mode: str, the queue mode (run/batch/status/reset/init/system)
    :param kwargs: additional keyword arguments

    :type mode: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # -------------------------------------------------------------------------
    # fast path for system mode (called after every runstring in batch
    #   scripts so must be super quick - avoids loading the full APERO
    #   runtime when --qpath is given)
    if mode is None:
        quick_args = _quick_parse_args()
        cond1 = quick_args['mode'] == 'system'
        cond2 = quick_args['qpath'] is not None
        if cond1 and cond2:
            return _system_main(quick_args)
    # -------------------------------------------------------------------------
    # normal (slow) path - load the full APERO runtime
    from apero.utils import drs_startup
    # assign function calls (must add positional)
    fkwargs = dict(mode=mode, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success,
                                outputs='None')


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # deferred imports (only needed on the slow path)
    from aperocore.core import drs_log
    from apero.tools.module.processing import drs_queue
    # get the logging function
    wlog = drs_log.wlog
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get the queue mode from inputs
    qmode = str(params['INPUTS']['MODE']).lower()
    # ----------------------------------------------------------------------
    # deal with an invalid mode
    if qmode not in QUEUE_MODES:
        emsg = 'Queue: Invalid mode "{0}" (must be one of: {1})'
        eargs = [qmode, ', '.join(QUEUE_MODES)]
        wlog(params, 'error', emsg.format(*eargs))
        return locals()
    # ----------------------------------------------------------------------
    # run mode: run the next task(s) in the queue
    if qmode == 'run':
        drs_queue.queue_run(params)
    # batch mode: create (and optionally submit) sbatch scripts
    elif qmode == 'batch':
        drs_queue.queue_batch(params)
    # status mode: interactive terminal (cli) view of the queue
    elif qmode == 'status':
        drs_queue.queue_status(params)
    # gui mode: browser dashboard with status view and action buttons
    elif qmode == 'gui':
        # deferred import (the gui module is only needed in gui mode)
        from apero.tools.module.processing import drs_queue_gui
        drs_queue_gui.queue_gui(params)
    # reset mode: remove entries from the queue
    elif qmode == 'reset':
        drs_queue.queue_reset(params)
    # init mode: interactively create the batch template
    elif qmode == 'init':
        drs_queue.queue_init(params)
    # system mode (slow fallback): move a task from running to
    #   complete/failed (the fast path in main() handles the usual case)
    elif qmode == 'system':
        drs_queue.queue_system(params)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

