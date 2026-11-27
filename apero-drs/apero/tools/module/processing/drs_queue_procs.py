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

The registry itself is the generic gui process registry shared with other
guis (aperocore.gui.procs); this module only adds the APERO queue names
(registry and gui job directories inside PATH.OTHER) and keeps the
functions available under their queue module name.

Created on 2026-10-28

@author: cook
"""
from typing import List, Optional

from aperocore.gui import procs as gui_procs

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_queue_procs.py'
# registry directory name (inside PATH.OTHER, next to the gui job logs)
PROC_DIR_NAME = 'queue_processes'
# gui job log directory name (inside PATH.OTHER) - its files are owned by
#    the queue gui and are removed with their process records
JOB_DIR_NAME = 'queue_gui_jobs'
# valid process kinds
PROC_KINDS = ['generate', 'reset', 'run', 'batch', 'chain']
# the shared registry settings (see aperocore.gui.procs)
PROC_ID_RE = gui_procs.PROC_ID_RE
SBATCH_ID_RE = gui_procs.SBATCH_ID_RE
MAX_QIDS = gui_procs.MAX_QIDS
SLURM_START_GRACE = gui_procs.SLURM_START_GRACE
SQUEUE_CACHE_SECONDS = gui_procs.SQUEUE_CACHE_SECONDS
# the shared registry / status functions (see aperocore.gui.procs)
load = gui_procs.load
load_all = gui_procs.load_all
register = gui_procs.register
update = gui_procs.update
finish = gui_procs.finish
owned_file = gui_procs.owned_file
parse_sbatch_ids = gui_procs.parse_sbatch_ids
slurm_states = gui_procs.slurm_states
user_slurm_jobs = gui_procs.user_slurm_jobs
slurm_job_details = gui_procs.slurm_job_details
pid_alive = gui_procs.pid_alive
proc_status = gui_procs.proc_status
log_files = gui_procs.log_files


# =============================================================================
# Define functions
# =============================================================================
def get_proc_dir(other_path: str) -> str:
    """
    Get (and create) the queue process registry directory

    :param other_path: str, the PATH.OTHER directory

    :return: str, the registry directory
    """
    return gui_procs.get_proc_dir(other_path, PROC_DIR_NAME)


def remove(proc_dir: str, proc_ids: List[str],
           artifact_roots: Optional[List[str]] = None,
           protected_qids: Optional[List[str]] = None) -> int:
    """
    Remove inactive records and their unshared, owned log files (the
    queue gui job directory is always a trusted log directory)

    :param proc_dir: str, the registry directory
    :param proc_ids: list of str, the process ids
    :param artifact_roots: Additional trusted log directories, or None.
    :param protected_qids: Retained queue IDs, None preserves scripts.

    :return: int, the number of records removed
    """
    rkwargs = dict(artifact_roots=artifact_roots,
                   protected_qids=protected_qids, job_dir_name=JOB_DIR_NAME)
    return gui_procs.remove(proc_dir, proc_ids, **rkwargs)


# =============================================================================
# End of code
# =============================================================================
