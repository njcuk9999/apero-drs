#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Background (and interactive) command jobs for browser guis

A job is one command (no shell) run in the background by the gui with its
output (stdout + stderr) written to a log file the browser follows. Jobs
belong to a channel (normally one page/tab of the gui) and every channel
runs at most one job at a time.

Interactive jobs keep their stdin open so the browser console can answer
prompts (lines typed in the browser are written to the command's stdin).
Jobs can also be submitted to Slurm (sbatch) - the gui then waits for the
job to finish (the job output goes to the same log).

Every job is recorded in the process registry (aperocore.gui.procs) so it
also shows up (and can be stopped) on the processes page.

Created on 2026-11-26

@author: cook
"""
import os
import shlex
import subprocess
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from aperocore.gui import procs as gui_procs
from aperocore.gui import slurm as gui_slurm

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.jobs.py'
# environment variable holding the job log path (set for every job)
JOB_LOG_ENV = 'APEROCORE_GUI_JOB_LOG'
# number of trailing lines of job output sent to the browser
JOB_TAIL = 400
# seconds between squeue checks while waiting for a slurm job
SLURM_POLL = 10
# seconds a finished Slurm job may lack its exit code file (shared fs lag)
SLURM_GONE_GRACE = 60


# =============================================================================
# Define classes
# =============================================================================
class JobManager:
    """
    Run gui jobs (one per channel) and keep track of their state
    """

    def __init__(self, state: Any,
                 proc_dir_func: Callable[[], Optional[str]],
                 job_dir_func: Callable[[], Optional[str]]) -> None:
        """
        Initialise the job manager

        :param state: GuiState, the shared gui state (activity messages)
        :param proc_dir_func: callable returning the process registry
                              directory (None = no registry)
        :param job_dir_func: callable returning the job log directory
                             (None = no working directory, jobs refused)

        :return: None
        """
        self.state = state
        self.proc_dir_func = proc_dir_func
        self.job_dir_func = job_dir_func
        # channel -> job dictionary (the current or last job)
        self.jobs: Dict[str, Dict[str, Any]] = dict()
        # channel -> Popen of running local jobs (for stdin / stop)
        self.processes: Dict[str, subprocess.Popen] = dict()
        self.lock = threading.Lock()

    def running(self, channel: str) -> bool:
        """
        Whether a channel has a running job

        :param channel: str, the channel

        :return: bool, True if a job is running
        """
        job = self.jobs.get(channel)
        return job is not None and bool(job.get('running'))

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a short summary of every channel's current/last job

        :return: dict, channel -> dict(kind, label, running, returncode)
        """
        out = dict()
        for channel, job in list(self.jobs.items()):
            out[channel] = dict(kind=job.get('kind'), label=job.get('label'),
                                running=bool(job.get('running')),
                                returncode=job.get('returncode'),
                                interactive=bool(job.get('interactive')))
        return out

    def get(self, channel: str) -> Dict[str, Any]:
        """
        Get the current/last job of a channel with the tail of its output

        :param channel: str, the channel

        :return: dict, the job (empty if no job ran on this channel yet)
        """
        # deferred import (webapp imports this module)
        from aperocore.gui import webapp
        source = self.jobs.get(channel)
        if source is None:
            return dict()
        job = dict(source)
        job['lines'] = webapp.job_tail(job['path'], JOB_TAIL, keep_ansi=True)
        return job

    def start(self, channel: str, kind: str, cmd: List[str],
              label: Optional[str] = None, cwd: Optional[str] = None,
              env: Optional[Dict[str, str]] = None,
              interactive: bool = False,
              stdin_text: Optional[str] = None,
              slurm_template: Optional[Dict[str, Any]] = None,
              on_done: Optional[Callable[[int], None]] = None
              ) -> Dict[str, Any]:
        """
        Start a command as the background job of a channel

        :param channel: str, the owning channel (one job per channel)
        :param kind: str, the process kind (registry / log names)
        :param cmd: list of str, the command (no shell)
        :param label: str or None, display text (default: the command)
        :param cwd: str or None, working directory (default: home)
        :param env: dict or None, extra environment variables
        :param interactive: bool, keep stdin open for browser input
        :param stdin_text: str or None, text written to stdin at start
        :param slurm_template: dict or None, run through sbatch with this
                               batch template instead of locally
        :param on_done: callable or None, called with the return code

        :return: dict(started, message)
        """
        job_dir = self.job_dir_func()
        if job_dir is None:
            return dict(started=False, message='no working directory set')
        with self.lock:
            if self.running(channel):
                return dict(started=False,
                            message='busy - a job is already running here')
            # the log file the browser follows
            stamp = time.strftime('%Y%m%d-%H%M%S')
            log_path = os.path.join(job_dir, '{0}-{1}.log'.format(
                gui_slurm.sanitize_template_name(kind), stamp))
            display = label or shlex.join(cmd)
            job = dict(kind=kind, label=display, cmd=shlex.join(cmd),
                       path=log_path, running=True, returncode=None,
                       started=time.strftime('%H:%M:%S'), proc_id=None,
                       interactive=interactive and slurm_template is None,
                       channel=channel, slurm=slurm_template is not None)
            self.jobs[channel] = job
        # run the job in a worker thread
        jargs = (channel, job, cmd, cwd, env, stdin_text, slurm_template,
                 on_done)
        thread = threading.Thread(target=self._run, args=jargs, daemon=True)
        thread.start()
        return dict(started=True, message='{0} started'.format(kind))

    def _run(self, channel: str, job: Dict[str, Any], cmd: List[str],
             cwd: Optional[str], env: Optional[Dict[str, str]],
             stdin_text: Optional[str],
             slurm_template: Optional[Dict[str, Any]],
             on_done: Optional[Callable[[int], None]]) -> None:
        """
        Run one job (worker thread): execute, wait, record the result

        :param channel: str, the owning channel
        :param job: dict, the job dictionary (updated in place)
        :param cmd: list of str, the command
        :param cwd: str or None, the working directory
        :param env: dict or None, extra environment variables
        :param stdin_text: str or None, text written to stdin at start
        :param slurm_template: dict or None, batch template (slurm job)
        :param on_done: callable or None, called with the return code

        :return: None
        """
        proc_dir = self.proc_dir_func()
        self.state.add_message('{0} started: {1}'.format(job['kind'],
                                                         job['label']),
                               channel)
        # environment: unbuffered python so output appears immediately
        full_env = dict(os.environ)
        full_env['PYTHONUNBUFFERED'] = '1'
        # tell the command where its output goes (e.g. to record it)
        full_env[JOB_LOG_ENV] = job['path']
        full_env.update(env or dict())
        workdir = cwd or os.path.expanduser('~')
        returncode = -1
        try:
            if slurm_template is not None:
                sargs = [job, cmd, workdir, env or dict(), slurm_template,
                         proc_dir]
                returncode = self._run_slurm(*sargs)
            else:
                returncode = self._run_local(channel, job, cmd, workdir,
                                             full_env, stdin_text, proc_dir)
        except Exception as job_error:
            with open(job['path'], 'a') as logfile:
                logfile.write('\nGUI job error: {0}\n'.format(job_error))
        finally:
            with self.lock:
                job['running'] = False
                job['returncode'] = returncode
                self.processes.pop(channel, None)
        # record the result (a stop from the processes page already did)
        record = None
        if proc_dir is not None and job['proc_id'] is not None:
            record = gui_procs.load(proc_dir, job['proc_id'])
        if record is not None and not record.get('finished'):
            gui_procs.finish(proc_dir, job['proc_id'], returncode)
        if returncode == 0:
            self.state.add_message('{0} finished'.format(job['kind']),
                                   channel)
        else:
            self.state.add_message('{0} FAILED (exit code {1})'.format(
                job['kind'], returncode), channel)
        if on_done is not None:
            try:
                on_done(returncode)
            except Exception as done_error:
                self.state.add_message('{0} follow-up failed: {1}'.format(
                    job['kind'], done_error), channel)
        # anything that changed on disk must be reloaded by the browser
        self.state.bump()

    def _run_local(self, channel: str, job: Dict[str, Any], cmd: List[str],
                   workdir: str, env: Dict[str, str],
                   stdin_text: Optional[str],
                   proc_dir: Optional[str]) -> int:
        """
        Run a job on this machine and wait for it

        :param channel: str, the owning channel
        :param job: dict, the job dictionary (updated in place)
        :param cmd: list of str, the command
        :param workdir: str, the working directory
        :param env: dict, the full environment
        :param stdin_text: str or None, text written to stdin at start
        :param proc_dir: str or None, the process registry directory

        :return: int, the exit code
        """
        keep_stdin = job['interactive'] or stdin_text
        stdin = subprocess.PIPE if keep_stdin else subprocess.DEVNULL
        # own session so a stop also reaches the children
        popen_kwargs = dict(stderr=subprocess.STDOUT, stdin=stdin, env=env,
                            cwd=workdir, start_new_session=True)
        # append mode (O_APPEND): the echoed browser answers (send_input)
        #   and the command output both always go to the end of the log
        with open(job['path'], 'a') as logfile:
            process = subprocess.Popen(cmd, stdout=logfile, **popen_kwargs)
            with self.lock:
                self.processes[channel] = process
            if proc_dir is not None:
                rkwargs = dict(cmd=job['cmd'], pid=process.pid, owner='gui',
                               log_paths=[job['path']])
                job['proc_id'] = gui_procs.register(proc_dir, job['kind'],
                                                    job['label'], **rkwargs)
            # pre-written answers (non interactive jobs close stdin after)
            if stdin_text and process.stdin is not None:
                try:
                    process.stdin.write(stdin_text.encode())
                    process.stdin.flush()
                    if not job['interactive']:
                        process.stdin.close()
                except (BrokenPipeError, OSError):
                    pass
            return process.wait()

    def _run_slurm(self, job: Dict[str, Any], cmd: List[str], workdir: str,
                   env: Dict[str, str], template: Dict[str, Any],
                   proc_dir: Optional[str]) -> int:
        """
        Run a job through sbatch and wait for it to finish

        :param job: dict, the job dictionary (updated in place)
        :param cmd: list of str, the command
        :param workdir: str, the working directory of the job
        :param env: dict, extra environment variables for the job
        :param template: dict, the batch template
        :param proc_dir: str or None, the process registry directory

        :return: int, the exit code (-1 if the job died without one)
        """
        stem = os.path.splitext(job['path'])[0]
        script_path, rc_path = stem + '.sbatch', stem + '.rc'
        # the command line (environment variables exported first)
        lines = ['export {0}={1}'.format(key, shlex.quote(value))
                 for key, value in env.items()]
        lines.append('cd {0}'.format(shlex.quote(workdir)))
        lines.append(shlex.join(cmd))
        job_name = '{0}_{1}'.format(template.get('job_name', 'gui'),
                                    job['kind'])
        sargs = [template, job_name, lines, job['path']]
        text = gui_slurm.build_script(*sargs, rc_path=rc_path)
        gui_slurm.write_script(script_path, text)
        success, job_id, output = gui_slurm.submit(script_path)
        if not success:
            with open(job['path'], 'w') as logfile:
                logfile.write('sbatch failed: {0}\n'.format(output))
            return 1
        if proc_dir is not None:
            rkwargs = dict(cmd=job['cmd'], owner='gui',
                           log_paths=[job['path']], slurm_jobs=[job_id],
                           artifact_paths=[script_path, rc_path])
            label = '{0} [slurm {1}]'.format(job['label'], job_id)
            job['proc_id'] = gui_procs.register(proc_dir, job['kind'], label,
                                                **rkwargs)
        self.state.add_message('{0} submitted as Slurm job {1}'.format(
            job['kind'], job_id), job['channel'])
        return wait_slurm_job(proc_dir, job['proc_id'], job_id, rc_path)

    def send_input(self, channel: str, text: str) -> Dict[str, Any]:
        """
        Send one line of input to the running interactive job of a channel

        :param channel: str, the channel
        :param text: str, the text (a new line is added)

        :return: dict(success, message)
        """
        with self.lock:
            process = self.processes.get(channel)
            job = self.jobs.get(channel)
        if process is None or job is None or not job.get('interactive'):
            return dict(success=False,
                        message='no interactive job running here')
        if process.stdin is None or process.stdin.closed:
            return dict(success=False, message='job input is closed')
        try:
            process.stdin.write((text + '\n').encode())
            process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            return dict(success=False, message=str(error))
        # echo the answer into the log so the console shows it
        with open(job['path'], 'a') as logfile:
            logfile.write(text + '\n')
        return dict(success=True, message='sent')

    def stop(self, channel: str) -> Dict[str, Any]:
        """
        Stop the running job of a channel

        :param channel: str, the channel

        :return: dict(success, message)
        """
        job = self.jobs.get(channel)
        if job is None or not job.get('running'):
            return dict(success=False, message='no job running here')
        proc_dir = self.proc_dir_func()
        # registered jobs are stopped through the registry (also slurm)
        if proc_dir is not None and job.get('proc_id') is not None:
            record = gui_procs.load(proc_dir, job['proc_id'])
            if record is not None:
                return gui_procs.stop_process(proc_dir, record)
        process = self.processes.get(channel)
        if process is None:
            return dict(success=False, message='job cannot be stopped')
        killed = gui_procs.kill_pid(process.pid)
        return dict(success=killed,
                    message='stopped' if killed else 'could not stop job')

    def shutdown(self) -> None:
        """
        Close the stdin of interactive jobs (called when the gui stops -
        running jobs are left running)

        :return: None
        """
        with self.lock:
            processes = list(self.processes.values())
        for process in processes:
            try:
                if process.stdin is not None:
                    process.stdin.close()
            except OSError:
                pass


# =============================================================================
# Define functions
# =============================================================================
def wait_slurm_job(proc_dir: Optional[str], proc_id: Optional[str],
                   job_id: str, rc_path: str) -> int:
    """
    Wait for a submitted single-command Slurm job to finish

    :param proc_dir: str or None, the process registry directory
    :param proc_id: str or None, the registered process id
    :param job_id: str, the Slurm job id
    :param rc_path: str, the exit code file written by the job

    :return: int, the exit code (-1 if the job died without one, e.g.
             time limit, out of memory or scancel)
    """
    gone_since = None
    while True:
        # the job writes its exit code when done
        if os.path.exists(rc_path):
            with open(rc_path) as rc_file:
                text = rc_file.read().strip()
            return int(text) if text.lstrip('-').isdigit() else 1
        # stopped from the processes page (scancel)
        record = None
        if proc_dir is not None and proc_id is not None:
            record = gui_procs.load(proc_dir, proc_id)
        if record is not None and record.get('finished'):
            return int(record.get('returncode') or -15)
        # gone from squeue without an exit code (after a grace period)
        states = gui_procs.slurm_states([job_id])
        if states is not None and job_id not in states:
            gone_since = gone_since or time.time()
            if time.time() - gone_since > SLURM_GONE_GRACE:
                return -1
        time.sleep(SLURM_POLL)


# =============================================================================
# End of code
# =============================================================================
