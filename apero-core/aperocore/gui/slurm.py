#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slurm batch templates and scripts for browser guis

A batch template holds the sbatch resources (time, nodes, cpus, memory,
account, job name, mail settings) and the activation lines (module loads,
conda activate, ...) a batch script needs. Templates are saved as yaml
files (one per name) in a template directory chosen by the application.

Only the standard library and PyYAML are used.

Created on 2026-11-26

@author: cook
"""
import os
import shlex
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple

import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.slurm.py'
# directory name (inside the application state directory) of templates
TEMPLATE_DIR_NAME = 'batch_templates'
# the default template name
DEFAULT_TEMPLATE = 'default'
# the simple (single value) template fields shown in the gui, in order
TEMPLATE_FIELDS = ['time', 'nodes', 'cpus_per_task', 'mem', 'partition',
                   'account', 'job_name', 'mail_user', 'mail_type']
# the built-in template values (applications may pass their own defaults)
BATCH_DEFAULTS: Dict[str, Any] = dict(time='24:00:00', nodes=1,
                                      cpus_per_task=8, mem='32G',
                                      partition='', account='',
                                      job_name='gui_job', mail_user='',
                                      mail_type='END,FAIL', activation=[])


# =============================================================================
# Define template functions
# =============================================================================
def sanitize_template_name(name: Optional[str]) -> str:
    """
    Normalise a template (or job) name for use as a file name

    Blank/None falls back to the default template name. Only alphanumeric
    characters, dashes and underscores are kept (anything else, e.g. path
    separators, becomes an underscore).

    :param name: str or None, the requested name

    :return: str, the sanitised name
    """
    if name is None or str(name).strip() in ['', 'None']:
        return DEFAULT_TEMPLATE
    safe = ''.join(char if (char.isalnum() or char in '-_') else '_'
                   for char in str(name).strip())
    return safe or DEFAULT_TEMPLATE


def template_path(template_dir: str, name: Optional[str]) -> str:
    """
    Get the yaml file of a named template

    :param template_dir: str, the template directory
    :param name: str or None, the template name

    :return: str, the absolute template path
    """
    return os.path.join(template_dir,
                        sanitize_template_name(name) + '.yaml')


def list_templates(template_dir: str) -> List[str]:
    """
    List the saved template names (the default name is always listed)

    :param template_dir: str, the template directory

    :return: list of str, the sorted template names
    """
    names = {DEFAULT_TEMPLATE}
    if os.path.isdir(template_dir):
        for filename in os.listdir(template_dir):
            if filename.endswith('.yaml') and not filename.startswith('.'):
                names.add(filename[:-len('.yaml')])
    return sorted(names)


def load_template(template_dir: str, name: Optional[str] = None,
                  defaults: Optional[Dict[str, Any]] = None
                  ) -> Dict[str, Any]:
    """
    Load a named template (missing values filled from the defaults)

    :param template_dir: str, the template directory
    :param name: str or None, the template name
    :param defaults: dict or None, the default values (BATCH_DEFAULTS)

    :return: dict, the template values
    """
    template = dict(defaults or BATCH_DEFAULTS)
    path = template_path(template_dir, name)
    if os.path.exists(path):
        try:
            with open(path, 'r') as tfile:
                stored = yaml.safe_load(tfile) or dict()
        except (OSError, yaml.YAMLError):
            stored = dict()
        if isinstance(stored, dict):
            template.update(stored)
    if not isinstance(template.get('activation'), list):
        template['activation'] = []
    return template


def save_template(template_dir: str, template: Dict[str, Any],
                  name: Optional[str] = None) -> str:
    """
    Save a template under a name

    :param template_dir: str, the template directory (created)
    :param template: dict, the template values
    :param name: str or None, the template name

    :return: str, the path the template was saved to
    """
    os.makedirs(template_dir, exist_ok=True)
    path = template_path(template_dir, name)
    with open(path, 'w') as tfile:
        yaml.safe_dump(template, tfile, default_flow_style=False,
                       sort_keys=False, width=float('inf'))
    return path


def update_template(template_dir: str, name: Optional[str],
                    form: Dict[str, Any],
                    defaults: Optional[Dict[str, Any]] = None
                    ) -> Tuple[Dict[str, Any], str]:
    """
    Update a saved template from a gui form and save it

    :param template_dir: str, the template directory
    :param name: str or None, the template name
    :param form: dict, the form values (only template keys are used;
                 activation may be a list or a newline separated string)
    :param defaults: dict or None, the default values

    :return: tuple, (the saved template, the path it was saved to)
    """
    template = load_template(template_dir, name, defaults)
    for key in TEMPLATE_FIELDS:
        if key in form:
            template[key] = str(form[key]).strip()
    if 'activation' in form:
        activation = form['activation']
        if isinstance(activation, str):
            activation = activation.splitlines()
        template['activation'] = [str(line).rstrip()
                                  for line in activation
                                  if str(line).strip() != '']
    path = save_template(template_dir, template, name)
    return template, path


# =============================================================================
# Define script functions
# =============================================================================
def build_script(template: Dict[str, Any], job_name: str,
                 commands: List[str], log_path: str,
                 rc_path: Optional[str] = None,
                 err_path: Optional[str] = None) -> str:
    """
    Build the text of an sbatch script

    :param template: dict, the batch template (header + activation)
    :param job_name: str, the Slurm job name
    :param commands: list of str, the shell lines to run (after the
                     activation lines)
    :param log_path: str, the job output file (stdout, and stderr unless
                     err_path is given)
    :param rc_path: str or None, file the exit code of the last command is
                    written to (lets a waiting gui see the result after the
                    job left squeue)
    :param err_path: str or None, separate stderr file

    :return: str, the script text
    """
    template = dict(BATCH_DEFAULTS, **template)
    lines = ['#!/bin/bash']
    lines.append('#SBATCH --time={0}'.format(template['time']))
    lines.append('#SBATCH --nodes={0}'.format(template['nodes']))
    lines.append('#SBATCH --cpus-per-task={0}'
                 ''.format(template['cpus_per_task']))
    lines.append('#SBATCH --mem={0}'.format(template['mem']))
    # optional header lines (only when set)
    if str(template.get('partition') or '').strip():
        lines.append('#SBATCH --partition={0}'.format(template['partition']))
    if str(template.get('account') or '').strip():
        lines.append('#SBATCH --account={0}'.format(template['account']))
    lines.append('#SBATCH --job-name={0}'.format(job_name))
    lines.append('#SBATCH --output={0}'.format(log_path))
    if err_path is not None:
        lines.append('#SBATCH --error={0}'.format(err_path))
    if str(template.get('mail_user') or '').strip():
        lines.append('#SBATCH --mail-user={0}'
                     ''.format(template['mail_user']))
        lines.append('#SBATCH --mail-type={0}'
                     ''.format(template['mail_type']))
    lines.append('')
    # the activation lines (echoed so the log shows what ran)
    lines.append('echo "RUNNING: activation lines"')
    for act_line in template.get('activation') or []:
        lines.append('echo {0}'.format(shlex.quote(str(act_line))))
        lines.append(str(act_line))
    lines.append('')
    lines.append('export PYTHONUNBUFFERED=1')
    lines.extend(commands)
    lines.append('status=$?')
    # the job vanishes from squeue when done - this keeps its exit code
    if rc_path is not None:
        lines.append('echo "$status" > {0}'.format(shlex.quote(rc_path)))
    lines.append('exit $status')
    return '\n'.join(lines) + '\n'


def write_script(path: str, text: str) -> None:
    """
    Write an (executable) script file

    :param path: str, the script path (directory created)
    :param text: str, the script text

    :return: None
    """
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as sfile:
        sfile.write(text)
    os.chmod(path, 0o755)


def sbatch_available() -> bool:
    """
    Whether sbatch can be used on this machine

    :return: bool, True if sbatch is on the PATH
    """
    return shutil.which('sbatch') is not None


def submit(script_path: str) -> Tuple[bool, str, str]:
    """
    Submit an sbatch script

    :param script_path: str, the script path

    :return: tuple, (success, job id, sbatch output / error text)
    """
    if not sbatch_available():
        return False, '', '"sbatch" not found on this machine'
    try:
        output = subprocess.run(['sbatch', '--parsable', script_path],
                                capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        return False, '', str(error)
    text = (output.stderr or output.stdout).strip()
    if output.returncode != 0:
        return False, '', text
    job_id = output.stdout.strip().split(';')[0]
    return True, job_id, text


# =============================================================================
# End of code
# =============================================================================
